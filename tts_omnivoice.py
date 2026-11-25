"""Narrate a spec's vo with OmniVoice (local, free) into the engine's narration cache, with an automatic check of every paragraph.
    <venv with omnivoice, transformers, num2words, soundfile, librosa>/python tts_omnivoice.py specs/<slug>.json short --ref ref.wav --ref-text "..." [--names names.json] [--tries 3]
For each paragraph: generate (seeded), transcribe the result (whisper-small), compare it with the script (numbers spelled out, Devanagari names matched to their Latin form), retry with another seed while the match is poor, keep the best take.
Writes out/<slug>/<fmt>/vo/{raw<i>.mp3, p<i>.mp3, meta.json} in the same format as the ElevenLabs path (hash = md5(text + VOICE + tempo)), so `engine.py build` finds everything cached, plus qc.json (the check, per paragraph).
Draft quality: a cloned voice (not Ruhaan); the QC catches wrong or missing words, not tone. Listen before publishing."""
import argparse, difflib, hashlib, json, os, re, subprocess, sys, time
import numpy as np, soundfile as sf, torch, librosa
from num2words import num2words
ap = argparse.ArgumentParser(); ap.add_argument("spec"); ap.add_argument("fmt"); ap.add_argument("--ref"); ap.add_argument("--ref-text"); ap.add_argument("--names"); ap.add_argument("--tries", type=int, default=3); ap.add_argument("--only", default="")
a = ap.parse_args(); torch.set_num_threads(4)
VOICE = "siw1N9V8LmYeEWKyWBxv"; TEMPO = {"long": 1.04, "short": 1.07}[a.fmt]
spec = json.load(open(a.spec)); paras = [s["vo"] for s in spec[a.fmt]]; out = f"out/{spec['slug']}/{a.fmt}/vo"; os.makedirs(out, exist_ok=True)
NAMES = json.load(open(a.names)) if a.names else {}; DEV = {}
for lat, dev in NAMES.items():
    for dw, lw in zip(dev.split(), re.findall(r"[A-Za-z]+", lat)):
        if len(dev.split()) == len(re.findall(r"[A-Za-z]+", lat)): DEV[dw] = lw.lower()
def norm(s, asr=False):
    s = s.lower().replace("-", " ")
    if asr: s = re.sub(r"\d+(?:,\d{3})*(?:\.\d+)?", lambda m: " " + num2words(int(m.group(0).replace(",", ""))).replace("-", " ").replace(",", "").replace(" and", "") + " ", s)
    toks = []
    for t in re.findall(r"[\wऀ-ॿ']+", s):
        t = t.strip("'")
        if t: toks.append(DEV.get(t, t))
    return [t for t in toks if t != "and"]
def similar(x, y):
    if len(x) < 3 or len(y) < 3: return x == y
    return difflib.SequenceMatcher(None, x, y).ratio() >= .6
NUMW = set("zero one two three four five six seven eight nine ten eleven twelve thirteen fourteen fifteen sixteen seventeen eighteen nineteen twenty thirty forty fifty sixty seventy eighty ninety hundred thousand".split())
def score(script, heard):
    A, B = norm(script), norm(heard, True); m = difflib.SequenceMatcher(None, A, B, autojunk=False); good = 0
    badnum = [x for x in A if x in NUMW and A.count(x) > B.count(x)]                 # numbers must be heard exactly: a garbled number is a wrong number
    for tag, i1, i2, j1, j2 in m.get_opcodes():
        if tag == "equal": good += i2 - i1
        elif tag == "replace":
            for x, y in zip(A[i1:i2], B[j1:j2]): good += similar(x, y)
    return good / max(len(A), 1) - (.2 if badnum else 0), sorted(set(badnum)) + [x for x in A if x not in NUMW and not any(similar(x, y) for y in B)]
from omnivoice import OmniVoice
from transformers import pipeline
M = OmniVoice.from_pretrained("k2-fsa/OmniVoice", device_map="cpu", dtype=torch.float32)
ASR = pipeline("automatic-speech-recognition", model="openai/whisper-small", device="cpu", return_timestamps="word")
meta = json.load(open(f"{out}/meta.json")) if os.path.exists(f"{out}/meta.json") else []; meta = meta + [None] * (len(paras) - len(meta)); qc = json.load(open(f"{out}/qc.json")) if os.path.exists(f"{out}/qc.json") else {}
only = {int(x) for x in a.only.split(",") if x != ""}
def align(script, chunks, dur):
    W = script.split(); S = [(c["text"].strip(), c["timestamp"][0], c["timestamp"][1] if c["timestamp"][1] is not None else c["timestamp"][0] + .3) for c in chunks if c["timestamp"][0] is not None]
    st = [None] * len(W); sn = [norm(w)[:1] or [""] for w in W]; sn = [x[0] for x in sn]; hn = []
    for t, s0, e0 in S:
        n = norm(t, True)
        for k in n: hn.append((k, s0, e0))
    m = difflib.SequenceMatcher(None, sn, [h[0] for h in hn], autojunk=False)
    for tag, i1, i2, j1, j2 in m.get_opcodes():
        if tag in ("equal", "replace"):
            for k, (i, j) in enumerate(zip(range(i1, i2), range(j1, j2))): st[i] = hn[j][1]
    first = S[0][1] if S else 0.0; last = S[-1][2] if S else dur
    idx = [i for i, v in enumerate(st) if v is not None]
    if not idx: st = [first + (last - first) * i / len(W) for i in range(len(W))]
    else:
        for i in range(len(W)):
            if st[i] is None:
                lo = max([k for k in idx if k < i], default=None); hi = min([k for k in idx if k > i], default=None)
                if lo is not None and hi is not None: st[i] = st[lo] + (st[hi] - st[lo]) * (i - lo) / (hi - lo)
                elif lo is not None: st[i] = st[lo] + (last - st[lo]) * (i - lo) / max(len(W) - lo, 1)
                else: st[i] = first + (st[hi] - first) * i / max(hi, 1)
    en = [min(st[i + 1] - .02, st[i] + 1.0) if i + 1 < len(W) else last for i in range(len(W))]
    return [{"w": W[i], "s": max(st[i], 0) / TEMPO, "e": max(en[i], st[i] + .05) / TEMPO} for i in range(len(W))]
for i, p in enumerate(paras):
    h = hashlib.md5((p + VOICE + str(TEMPO)).encode()).hexdigest()
    if meta[i] and meta[i].get("hash") == h and os.path.exists(f"{out}/p{i}.mp3") and (not only or i not in only): continue
    best = None
    for k in range(a.tries):
        torch.manual_seed(1000 * i + k); t0 = time.time(); au = M.generate(text=p, ref_audio=a.ref, ref_text=a.ref_text, num_step=24)[0]
        w16 = librosa.resample(au.astype("float32"), orig_sr=24000, target_sr=16000); r = ASR({"raw": w16, "sampling_rate": 16000}, generate_kwargs={"task": "transcribe", "language": "en"})
        sc, miss = score(p, r["text"]); print(f"[{i}] take {k + 1}: match {sc:.2f} missing {miss} ({time.time() - t0:.0f}s)", flush=True)
        if best is None or sc > best[0]: best = (sc, au, r, miss)
        if sc >= .93 and not miss: break
    sc, au, r, miss = best; sf.write(f"{out}/raw{i}.wav", au, 24000)
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", f"{out}/raw{i}.wav", "-b:a", "192k", f"{out}/raw{i}.mp3"], check=True)
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", f"{out}/raw{i}.mp3", "-af", f"atempo={TEMPO}", "-b:a", "192k", f"{out}/p{i}.mp3"], check=True)
    dur = float(subprocess.check_output(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", f"{out}/p{i}.mp3"]))
    meta[i] = {"hash": h, "dur": dur, "words": align(p, r["chunks"], len(au) / 24000)}; qc[str(i)] = {"match": round(sc, 3), "missing": miss, "heard": r["text"].strip(), "text": p}
    json.dump(meta, open(f"{out}/meta.json", "w"), ensure_ascii=False); json.dump(qc, open(f"{out}/qc.json", "w"), ensure_ascii=False, indent=1)
print("TTS_DONE", flush=True)
