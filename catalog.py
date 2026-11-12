"""Write CATALOG.md: one row per video with title, theme, intro, durations, status and sources."""
import json, glob, os, subprocess
ROOT = os.path.dirname(os.path.abspath(__file__))
log = json.load(open(f"{ROOT}/intro_log.json")).get("assigned", {}) if os.path.exists(f"{ROOT}/intro_log.json") else {}
def dur(p):
    if not os.path.exists(p): return "–"
    s = float(subprocess.check_output(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", p]))
    return f"{int(s // 60)}:{int(s % 60):02d}"
rows = ["# The Third Man – video catalog", "", "| Slug | Long file | Theme | Intro | Long | Short | Sources |", "|---|---|---|---|---|---|---|"]
for p in sorted(glob.glob(f"{ROOT}/specs/*.json")):
    sp = json.load(open(p)); s = sp["slug"]; f = sp.get("files", {})
    d = f"{ROOT}/deliver/{s}"
    rows.append(f"| {s} | {f.get('long','')} | {sp.get('theme','whites')} | {sp.get('intro') or log.get(s,'–')} | {dur(f'{d}/{f.get('long')}.mp4')} | {dur(f'{d}/{f.get('short')}.mp4')} | {'<br>'.join(sp.get('sources', [])) or '–'} |")
open(f"{ROOT}/CATALOG.md", "w").write("\n".join(rows) + "\n")
print(f"{len(rows) - 4} videos catalogued")
