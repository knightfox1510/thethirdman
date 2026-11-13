"""Build an .srt from per-paragraph voice files using ElevenLabs speech-to-text word timings.
usage: make_srt.py vo_dir offsets.json out.srt"""
import json, os, sys, subprocess

KEY = os.environ["XI_KEY"]
vo, offs, out = sys.argv[1], json.load(open(sys.argv[2])), sys.argv[3]


def stt(path):
    r = subprocess.run(["curl", "-s", "--max-time", "120", "https://api.elevenlabs.io/v1/speech-to-text",
                        "-H", f"xi-api-key: {KEY}", "-F", "model_id=scribe_v1", "-F", "language_code=en",
                        "-F", "timestamps_granularity=word", "-F", f"file=@{path}"], capture_output=True, text=True)
    return [w for w in json.loads(r.stdout)["words"] if w.get("type") == "word"]


def ts(t):
    ms = int(round(t * 1000)); h, ms = divmod(ms, 3600000); m, ms = divmod(ms, 60000); s, ms = divmod(ms, 1000)
    return f"{h:02}:{m:02}:{s:02},{ms:03}"


cues = []
for i, off in enumerate(offs):
    words = stt(f"{vo}/p{i}.mp3")
    cur = []
    for w in words:
        cur.append(w)
        line = " ".join(x["text"] for x in cur)
        if len(line) >= 38 or w["text"][-1] in ".?!":
            cues.append((cur[0]["start"] + off, cur[-1]["end"] + off, line)); cur = []
    if cur:
        cues.append((cur[0]["start"] + off, cur[-1]["end"] + off, " ".join(x["text"] for x in cur)))
with open(out, "w") as f:
    for n, (a, b, txt) in enumerate(cues, 1):
        f.write(f"{n}\n{ts(a)} --> {ts(max(b, a + .8))}\n{txt}\n\n")
print(len(cues), "cues")
