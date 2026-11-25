"""Build the extension for Chrome and for Firefox from this one source.   python3 build.py   ->  dist/ttm-capture-chrome-<v>.zip and dist/ttm-capture-firefox-<v>.zip
Chrome: load the unzipped folder with 'Load unpacked' at chrome://extensions (Developer mode).  Firefox (128 or newer): about:debugging#/runtime/this-firefox > 'Load Temporary Add-on' > pick manifest.json from the unzipped folder
(temporary: it is removed when Firefox closes; a permanent install needs Mozilla signing, or Firefox Developer/Nightly with xpinstall.signatures.required=false).
Firefox differences: background runs as an event page (scripts) instead of a service worker, no 'power' permission (keep-awake is skipped), and a gecko add-on id."""
import json, os, shutil, zipfile
H = os.path.dirname(os.path.abspath(__file__)); M = json.load(open(f"{H}/manifest.json")); V = M["version"]; FILES = ["background.js", "batch.js", "direct.js", "hook.js", "panel.js"]
def build(kind):
    m = json.loads(json.dumps(M))
    if kind == "firefox":
        m["background"] = {"scripts": ["background.js"]}; m["permissions"] = [p for p in m["permissions"] if p != "power"]
        m["browser_specific_settings"] = {"gecko": {"id": "ttm-capture@thethirdman.local", "strict_min_version": "128.0"}}
    out = f"{H}/dist/ttm-capture-{kind}-{V}.zip"; os.makedirs(f"{H}/dist", exist_ok=True)
    with zipfile.ZipFile(out, "w", zipfile.ZIP_DEFLATED) as z:
        z.writestr("manifest.json", json.dumps(m, indent=2))
        for f in FILES: z.write(f"{H}/{f}", f)
        for f in sorted(os.listdir(f"{H}/icons")): z.write(f"{H}/icons/{f}", f"icons/{f}")
        z.write(f"{H}/README.md", "README.md")
    print(out)
for k in ("chrome", "firefox"): build(k)
