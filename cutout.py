"""Portrait cut-outs for the licensed player images: MODNet (Apache-2.0, Xenova/modnet ONNX) alpha matte -> transparent PNG, ready to composite on our own backgrounds.
    python3 cutout.py in.png [out.png]            one image
    python3 cutout.py --dir assets/licensed/in assets/licensed/cut     a whole folder
The model file is downloaded once from huggingface.co/Xenova/modnet (25 MB) into $MODNET (default: scratchpad/models/modnet.onnx)."""
import os, sys, glob
import numpy as np
from PIL import Image, ImageFilter
MODEL = os.environ.get("MODNET", "/tmp/claude-0/-home-user-thethirdman/0e6d8023-8d7b-5fe3-9abc-6751d93064e2/scratchpad/models/modnet.onnx")
_S = None


def session():
    global _S
    if _S is None:
        import onnxruntime as ort
        if not os.path.exists(MODEL):
            import urllib.request; os.makedirs(os.path.dirname(MODEL), exist_ok=True)
            urllib.request.urlretrieve("https://huggingface.co/Xenova/modnet/resolve/main/onnx/model.onnx", MODEL)
        _S = ort.InferenceSession(MODEL, providers=["CPUExecutionProvider"])
    return _S


def matte(img, ref=512):
    """Alpha matte (0..255) the size of img. The model sees the image at ~ref px on the short side (multiples of 32), then the matte is scaled back up."""
    w, h = img.size; s = ref / min(w, h); nw, nh = max(32, int(round(w * s / 32)) * 32), max(32, int(round(h * s / 32)) * 32)
    x = (np.asarray(img.convert("RGB").resize((nw, nh), Image.LANCZOS), np.float32) / 255 - .5) / .5
    out = session().run(None, {"input": x.transpose(2, 0, 1)[None]})[0][0, 0]
    return Image.fromarray((np.clip(out, 0, 1) * 255).astype(np.uint8)).resize((w, h), Image.LANCZOS)


def main_person(a, keep=0.30):
    """Keep only the biggest person in the matte (drops a neighbour who sits in the crop): connected blobs of alpha > 0.5, keep those >= keep * the biggest."""
    from scipy import ndimage as ndi
    arr = np.asarray(a, np.float32) / 255; lab, n = ndi.label(arr > .5)
    if n <= 1: return a
    areas = ndi.sum(np.ones_like(arr), lab, range(1, n + 1)); ok = [i + 1 for i, v in enumerate(areas) if v >= keep * areas.max()]
    mask = np.isin(lab, ok); grown = ndi.binary_dilation(mask, iterations=6)                  # the soft edge around the kept blobs stays, the rest goes
    return Image.fromarray((arr * grown * 255).astype(np.uint8))


def cutout(img, clean=True, only_main=True):
    a = matte(img)
    if only_main: a = main_person(a)
    if clean:                                           # tighten the edge a touch: removes the halo of the old background without eating hair
        arr = np.asarray(a, np.float32) / 255; arr = np.clip((arr - .08) / .84, 0, 1) ** 1.15; a = Image.fromarray((arr * 255).astype(np.uint8))
    out = img.convert("RGBA"); out.putalpha(a); return out


def main():
    if len(sys.argv) > 3 and sys.argv[1] == "--dir":
        os.makedirs(sys.argv[3], exist_ok=True)
        for f in sorted(glob.glob(sys.argv[2] + "/*")):
            if f.lower().endswith((".png", ".jpg", ".jpeg", ".webp")):
                o = os.path.join(sys.argv[3], os.path.splitext(os.path.basename(f))[0] + ".png"); cutout(Image.open(f)).save(o); print("cut", o)
    else:
        i = sys.argv[1]; o = sys.argv[2] if len(sys.argv) > 2 else os.path.splitext(i)[0] + "_cut.png"; cutout(Image.open(i)).save(o); print("cut", o)


if __name__ == "__main__":
    main()
