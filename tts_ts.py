"""ElevenLabs TTS with character timestamps -> per-paragraph mp3 + word timings.
usage: tts_ts.py script.json outdir   (script.json: list of paragraph strings)"""
import json, os, sys, base64, subprocess, urllib.request

KEY = os.environ["XI_KEY"]
VOICE = os.environ.get("XI_VOICE", "siw1N9V8LmYeEWKyWBxv")  # Ruhaan
TEMPO = float(os.environ.get("TEMPO", "1.06"))
SHOW = {"सचिन": "Sachin", "तेंदुलकर": "Tendulkar", "शोएब": "Shoaib", "अख़्तर": "Akhtar", "मुंबई": "Mumbai",
        "शारजाह": "Sharjah", "हार्दिक": "Hardik", "पंड्या": "Pandya", "अर्शदीप": "Arshdeep", "सिंह": "Singh",
        "बुमराह": "Bumrah", "धोनी": "Dhoni", "कोहली": "Kohli"}
NUM = {"one-twenty": "120", "one-fifty-eight": "158", "one-forty-six": "146", "one-thirty": "130"}

paras = json.load(open(sys.argv[1])); out = sys.argv[2]
os.makedirs(out, exist_ok=True)
meta = []
for i, p in enumerate(paras):
    body = {"text": p, "model_id": "eleven_multilingual_v2",
            "voice_settings": {"stability": 0.45, "similarity_boost": 0.8, "style": 0.3, "use_speaker_boost": True},
            "previous_text": paras[i - 1] if i else None, "next_text": paras[i + 1] if i + 1 < len(paras) else None}
    req = urllib.request.Request(f"https://api.elevenlabs.io/v1/text-to-speech/{VOICE}/with-timestamps?output_format=mp3_44100_192",
                                 data=json.dumps(body).encode(), headers={"xi-api-key": KEY, "Content-Type": "application/json"})
    d = json.load(urllib.request.urlopen(req, timeout=120))
    raw = f"{out}/raw{i}.mp3"
    open(raw, "wb").write(base64.b64decode(d["audio_base64"]))
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", raw, "-af", f"atempo={TEMPO}", "-b:a", "192k", f"{out}/p{i}.mp3"], check=True)
    al = d["alignment"]
    words, cur, st, en = [], "", None, None
    for ch, s, e in zip(al["characters"], al["character_start_times_seconds"], al["character_end_times_seconds"]):
        if ch.isspace():
            if cur: words.append([cur, st, en]); cur = ""
            continue
        if not cur: st = s
        cur += ch; en = e
    if cur: words.append([cur, st, en])
    disp = []
    for w, s, e in words:
        core = w.strip(".,?!")
        tail = w[len(w.rstrip(".,?!")):]
        core = SHOW.get(core, NUM.get(core.lower(), core))
        disp.append({"w": core + tail, "s": s / TEMPO, "e": e / TEMPO})
    dur = float(subprocess.check_output(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", f"{out}/p{i}.mp3"]))
    meta.append({"dur": dur, "words": disp})
    print(i, round(dur, 2), " ".join(x["w"] for x in disp), flush=True)
json.dump(meta, open(f"{out}/meta.json", "w"), ensure_ascii=False)
