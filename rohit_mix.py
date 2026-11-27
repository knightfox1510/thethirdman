"""Mix the Rohit reel: voice (out/rohit_vo/s*.mp3 at scene starts + 0.35 s), music bed, whoosh at cuts, crowd on the chant and close, stamp on the titles/final. Writes the SRT. python3 rohit_mix.py"""
import json, os, subprocess, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import rohit_vo as RV
D = "out/rohit_vo"; durs = json.load(open(f"{D}/durs.json")); OUT = "deliver/rohit_mumbai_cha_raja"; N = "Channel_Ep03_Mumbai_cha_Raja_Short_9x16_IG"
st = [sum(durs[:i]) for i in range(len(durs))]; tot = sum(durs); ev = []
for i, t in enumerate(st): ev.append((t + .02, "whoosh", 1.0))
ev += [(st[1] + .2, "crowd", 1.0), (st[1] + 3.5, "crowd", .8), (st[5] + .3, "stamp", 1.0), (st[6] + .3, "stamp", 1.0), (st[11] + .3, "crowd", 1.2), (st[11] + .5, "stamp", 1.0), (st[0] + .15, "crowd", .8)]
json.dump(ev, open(f"{D}/ev.json", "w")); subprocess.run(["python3", "sfx.py", f"{D}/ev.json", str(tot), f"{D}/sfx.wav"], check=True); subprocess.run(["python3", "music.py", str(tot), f"{D}/music.wav"], check=True)
ins = []; fl = []
for i in range(12): ins += ["-i", f"{D}/s{i}.mp3"]
ins += ["-i", f"{D}/sfx.wav", "-i", f"{D}/music.wav"]
for i in range(12): ms = int((st[i] + .35) * 1000); fl.append(f"[{i + 1}:a]adelay={ms}|{ms}[v{i}]")
fl.append("".join(f"[v{i}]" for i in range(12)) + "amix=inputs=12:normalize=0,asplit[vo][vk]")
fl.append("[13:a]volume=1.0[sx]"); fl.append("[14:a]volume=.5[mu0]"); fl.append("[mu0][vk]sidechaincompress=threshold=.04:ratio=8:attack=20:release=400[mu]")
fl.append("[vo][sx][mu]amix=inputs=3:normalize=0,alimiter=limit=.95[a]")
final = f"{OUT}/{N}_final.mp4"
subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", f"{OUT}/{N}.mp4"] + ins + ["-filter_complex", ";".join(fl), "-map", "0:v", "-map", "[a]", "-c:v", "copy", "-c:a", "aac", "-b:a", "192k", "-t", str(tot), final], check=True)
def ts(x): h = int(x // 3600); m = int(x % 3600 // 60); return f"{h:02d}:{m:02d}:{x % 60:06.3f}".replace(".", ",")
srt = []; n = 1
for i in range(12):
    al = json.load(open(f"{D}/s{i}.json")); ch = al["characters"]; a = al["character_start_times_seconds"]; b = al["character_end_times_seconds"]; words = []; cur = ""; s0 = 0
    for c, x, y in zip(ch, a, b):
        if c.isspace():
            if cur: words.append((cur, s0, e0)); cur = ""
            continue
        if not cur: s0 = x
        cur += c; e0 = y
    if cur: words.append((cur, s0, e0))
    for k in range(0, len(words), 6):
        g = words[k:k + 6]; srt.append(f"{n}\n{ts(st[i] + .35 + g[0][1])} --> {ts(st[i] + .35 + g[-1][2] + .15)}\n{' '.join(w for w, _, _ in g)}\n"); n += 1
open(f"{OUT}/{N}.srt", "w").write("\n".join(srt)); print("mixed", final)
