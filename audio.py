"""Place voice paragraphs at their scene offsets, mix the music bed under them with ducking."""
import json, subprocess, os
D = os.path.dirname(os.path.abspath(__file__))
durs = json.load(open(f"{D}/durs.json")); offs = json.load(open(f"{D}/vo_offsets.json"))
total = sum(durs)
subprocess.run(["python3", f"{D}/music.py", str(total), f"{D}/music.wav"], check=True)
ins, flt = [], []
for i, o in enumerate(offs):
    ins += ["-i", f"{D}/vo/p{i}.mp3"]
    ms = int(o * 1000)
    flt.append(f"[{i}:a]aresample=44100,aformat=channel_layouts=stereo,adelay={ms}|{ms}[v{i}]")
n = len(offs)
flt.append("".join(f"[v{i}]" for i in range(n)) + f"amix=inputs={n}:normalize=0,apad=whole_dur={total}[vo]")
flt.append("[vo]asplit=2[vo1][vosc]")
flt.append(f"[{n}:a]volume=0.13[mus]")
flt.append("[mus][vosc]sidechaincompress=threshold=0.03:ratio=6:attack=40:release=600[duck]")
flt.append(f"[vo1][duck]amix=inputs=2:normalize=0,atrim=0:{total},loudnorm=I=-14:TP=-1.5:LRA=11[out]")
subprocess.run(["ffmpeg", "-y", "-loglevel", "error", *ins, "-i", f"{D}/music.wav",
                "-filter_complex", ";".join(flt), "-map", "[out]", "-ar", "48000", "-c:a", "aac", "-b:a", "192k",
                f"{D}/mix.m4a"], check=True)
print("audio ok", total)
