"""Narrate a spec's vo with OmniVoice (local, free) into the engine's narration cache, with an automatic check of every paragraph.
    <venv with omnivoice, transformers, num2words, soundfile, librosa>/python tts_omnivoice.py specs/<slug>.json short --ref ref.wav --ref-text "..." [--names names.json] [--tries 3]
For each paragraph: generate (seeded), transcribe the result (whisper-small), compare it with the script (numbers spelled out, Devanagari names matched to their Latin form), retry with another seed while the match is poor, keep the best take.
Writes out/<slug>/<fmt>/vo/{raw<i>.mp3, p<i>.mp3, meta.json} in the same format as the ElevenLabs path (hash = md5(text + VOICE + tempo)), so `engine.py build` finds everything cached, plus qc.json (the check, per paragraph).
Draft quality: a cloned voice (not Ruhaan); the QC catches wrong or missing words, not tone. Listen before publishing."""
import argparse, difflib, hashlib, json, os, re, subprocess, sys, time
import numpy as np, soundfile as sf, torch, librosa
from num2words import num2words
ap = argparse.ArgumentParser(); ap.add_argument("spec"); ap.add_argument("fmt"); ap.add_argument("--ref"); ap.add_argument("--ref-text"); ap.add_argument("--names"); ap.add_argument("--tries", type=int, default=3); ap.add_argument("--only", default=""); ap.add_argument("--lang", default="en")
a = ap.parse_args(); torch.set_num_threads(4)
VOICE = "siw1N9V8LmYeEWKyWBxv"; TEMPO = {"long": 1.04, "short": 1.07}[a.fmt]
spec = json.load(open(a.spec)); paras = [s["vo"] for s in spec[a.fmt]]; out = f"out/{spec['slug']}/{a.fmt}/vo"; os.makedirs(out, exist_ok=True)
NAMES = json.load(open(a.names)) if a.names and a.lang == "en" else {}; DEV = {}
for lat, dev in NAMES.items():
    for dw, lw in zip(dev.split(), re.findall(r"[A-Za-z]+", lat)):
        if len(dev.split()) == len(re.findall(r"[A-Za-z]+", lat)): DEV[dw] = lw.lower()
HI = "शून्य एक दो तीन चार पाँच छह सात आठ नौ दस ग्यारह बारह तेरह चौदह पंद्रह सोलह सत्रह अठारह उन्नीस बीस इक्कीस बाईस तेईस चौबीस पच्चीस छब्बीस सत्ताईस अट्ठाईस उनतीस तीस इकतीस बत्तीस तेंतीस चौंतीस पैंतीस छत्तीस सैंतीस अड़तीस उनतालीस चालीस इकतालीस बयालीस तैंतालीस चौवालीस पैंतालीस छियालीस सैंतालीस अड़तालीस उनचास पचास इक्यावन बावन तिरपन चौवन पचपन छप्पन सत्तावन अट्ठावन उनसठ साठ इकसठ बासठ तिरसठ चौंसठ पैंसठ छियासठ सड़सठ अड़सठ उनहत्तर सत्तर इकहत्तर बहत्तर तिहत्तर चौहत्तर पचहत्तर छिहत्तर सतत्तर अठहत्तर उनासी अस्सी इक्यासी बयासी तिरासी चौरासी पचासी छियासी सत्तासी अट्ठासी नवासी नब्बे इक्यानवे बानवे तिरानवे चौरानवे पचानवे छियानवे सत्तानवे अट्ठानवे निन्यानवे".split()
def hi_num(n):
    if n < 100: return HI[n]
    if n < 1000: return (HI[n // 100] + " सौ" + (" " + HI[n % 100] if n % 100 else ""))
    return str(n)
def norm(s, asr=False):
    s = s.lower().replace("-", " ").replace("\u0964", " ").replace("\u0965", " ")
    if asr: s = re.sub(r"\d+(?:,\d{3})*(?:\.\d+)?", lambda m: " " + (hi_num(int(m.group(0).replace(",", ""))) if a.lang == "hi" else num2words(int(m.group(0).replace(",", ""))).replace("-", " ").replace(",", "").replace(" and", "")) + " ", s)
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
    badnum = [x for x in A if x in NUMW and A.count(x) > B.count(x)] if a.lang == "en" else []                 # numbers must be heard exactly: a garbled number is a wrong number
    for tag, i1, i2, j1, j2 in m.get_opcodes():
        if tag == "equal": good += i2 - i1
        elif tag == "replace":
            for x, y in zip(A[i1:i2], B[j1:j2]): good += similar(x, y)
    return good / max(len(A), 1) - (.2 if badnum else 0), sorted(set(badnum)) + [x for x in A if x not in NUMW and not any(similar(x, y) for y in B)]
def squeeze(au, sr=24000, thr_db=-42.0, keep=.09, min_gap=.14):
    """Shorten silent gaps inside the clip (not the edges) to `keep` seconds: the model leaves 0.15-0.4 s hesitations mid-phrase, which sound like a drop-out. Punctuation pauses are put back later by the engine's breathe()."""
    fr = int(sr * .01); n = len(au) // fr; rms = np.array([np.sqrt(np.mean(au[i * fr:(i + 1) * fr] ** 2) + 1e-12) for i in range(n)]); db = 20 * np.log10(rms / (rms.max() + 1e-12) + 1e-12); sil = db < thr_db
    out = []; i = 0; lo = int(.25 / .01); hi = n - lo
    while i < n:
        if sil[i]:
            j = i
            while j < n and sil[j]: j += 1
            L = (j - i) * .01
            if i > lo and j < hi and L >= min_gap:
                k = int(keep / .01); a0 = au[i * fr:(i + k // 2) * fr]; b0 = au[(j - k + k // 2) * fr:j * fr]; out += [a0, b0]
            else: out.append(au[i * fr:j * fr])
            i = j
        else: out.append(au[i * fr:(i + 1) * fr]); i += 1
    out.append(au[n * fr:]); return np.concatenate(out).astype("float32")
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
        torch.manual_seed(1000 * i + k); t0 = time.time(); au = squeeze(M.generate(text=p, language=a.lang, ref_audio=a.ref, ref_text=a.ref_text, num_step=24)[0])
        w16 = librosa.resample(au.astype("float32"), orig_sr=24000, target_sr=16000); r = ASR({"raw": w16, "sampling_rate": 16000}, generate_kwargs={"task": "transcribe", "language": a.lang})
        sc, miss = score(p, r["text"]); print(f"[{i}] take {k + 1}: match {sc:.2f} missing {miss} ({time.time() - t0:.0f}s)", flush=True)
        if best is None or sc > best[0]: best = (sc, au, r, miss)
        if sc >= (.93 if a.lang == "en" else .8) and not miss: break
    sc, au, r, miss = best; sf.write(f"{out}/raw{i}.wav", au, 24000)
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", f"{out}/raw{i}.wav", "-b:a", "192k", f"{out}/raw{i}.mp3"], check=True)
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", f"{out}/raw{i}.mp3", "-af", f"atempo={TEMPO}", "-b:a", "192k", f"{out}/p{i}.mp3"], check=True)
    dur = float(subprocess.check_output(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", f"{out}/p{i}.mp3"]))
    meta[i] = {"hash": h, "dur": dur, "words": align(p, r["chunks"], len(au) / 24000)}; qc[str(i)] = {"match": round(sc, 3), "missing": miss, "heard": r["text"].strip(), "text": p}
    json.dump(meta, open(f"{out}/meta.json", "w"), ensure_ascii=False); json.dump(qc, open(f"{out}/qc.json", "w"), ensure_ascii=False, indent=1)
print("TTS_DONE", flush=True)
