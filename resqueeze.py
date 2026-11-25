"""Re-process already generated OmniVoice takes without regenerating: squeeze mid-phrase gaps, re-transcribe for timings, rewrite p<i>.mp3 and meta.json.
    <venv>/python resqueeze.py specs/<slug>.json short [--names names.json]"""
import sys, json, os, subprocess, hashlib, numpy as np, soundfile as sf, librosa
src = open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "tts_omnivoice.py")).read()
head = src.split("from omnivoice import OmniVoice")[0]; sq = src.split("def squeeze")[1].split("from omnivoice import OmniVoice")[0]
sys.argv = [sys.argv[0], sys.argv[1], sys.argv[2], "--ref", "x", "--ref-text", "x"] + sys.argv[3:]
al = src[src.index("def align("):src.index("for i, p in enumerate(paras):", src.index("def align("))]
exec(head); exec("def squeeze" + sq); exec(al)
from transformers import pipeline
ASR = pipeline("automatic-speech-recognition", model="openai/whisper-small", device="cpu", return_timestamps="word")
LANG = os.environ.get("TTS_LANG", "en"); meta = json.load(open(f"{out}/meta.json")); qc = json.load(open(f"{out}/qc.json")); extra = {"language": LANG} if LANG else {}
for i, p in enumerate(paras):
    au, sr = sf.read(f"{out}/raw{i}.wav"); au = au.astype("float32"); n0 = len(au) / sr; au = squeeze(au, sr); sf.write(f"{out}/raw{i}.wav", au, sr)
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", f"{out}/raw{i}.wav", "-b:a", "192k", f"{out}/raw{i}.mp3"], check=True)
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", f"{out}/raw{i}.mp3", "-af", f"atempo={TEMPO}", "-b:a", "192k", f"{out}/p{i}.mp3"], check=True)
    r = ASR({"raw": librosa.resample(au, orig_sr=sr, target_sr=16000), "sampling_rate": 16000}, generate_kwargs={"task": "transcribe", **extra}); sc, miss = score(p, r["text"])
    dur = float(subprocess.check_output(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", f"{out}/p{i}.mp3"]))
    meta[i] = {"hash": meta[i]["hash"], "dur": dur, "words": align(p, r["chunks"], len(au) / sr)}; qc[str(i)].update(match=round(sc, 3), missing=miss, heard=r["text"].strip())
    print(i, f"{n0:.1f}s -> {len(au) / sr:.1f}s match {sc:.2f} {miss}", flush=True)
json.dump(meta, open(f"{out}/meta.json", "w"), ensure_ascii=False); json.dump(qc, open(f"{out}/qc.json", "w"), ensure_ascii=False, indent=1); print("RESQ_DONE")
