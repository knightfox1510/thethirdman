"""Synthesised sound effects (no samples, no licences): bat crack, ball bounce, whoosh, crowd swell, stamp.
    python3 sfx.py events.json total out.wav     # events = [[time_s, kind, gain], ...]"""
import json, sys, wave
import numpy as np

SR = 44100
RNG = np.random.default_rng(7)


def _band(x, lo, hi):
    f = np.fft.rfft(x); fr = np.fft.rfftfreq(len(x), 1 / SR)
    f[(fr < lo) | (fr > hi)] = 0
    return np.fft.irfft(f, len(x))


def _env(n, a, d):
    t = np.arange(n) / SR
    return np.minimum(1, t / max(a, 1e-4)) * np.exp(-np.maximum(0, t - a) / d)


def crack(n=int(SR * .35)):
    t = np.arange(n) / SR
    noise = _band(RNG.standard_normal(n), 1500, 7000) * _env(n, .0008, .018)
    knock = (np.sin(2 * np.pi * 1180 * t) + .6 * np.sin(2 * np.pi * 2460 * t)) * _env(n, .0005, .03)
    body = np.sin(2 * np.pi * 310 * t) * _env(n, .001, .06) * .5
    x = noise * 2.2 + knock + body
    return x / np.abs(x).max()


def bounce(n=int(SR * .2)):
    t = np.arange(n) / SR
    x = np.sin(2 * np.pi * (140 - 60 * t / .2) * t) * _env(n, .001, .035) + _band(RNG.standard_normal(n), 300, 2000) * _env(n, .0005, .01) * .6
    return x / np.abs(x).max() * .55


def whoosh(n=int(SR * .42)):
    t = np.arange(n) / SR; x = RNG.standard_normal(n)
    out = np.zeros(n); seg = 512
    for k in range(0, n, seg):        # sweeping band: low → high → low
        f = k / n; c = 600 + 3200 * np.sin(np.pi * f)
        out[k:k + seg] = _band(x[k:k + seg] if len(x[k:k + seg]) == seg else np.pad(x[k:k + seg], (0, seg - len(x[k:k + seg]))), c * .5, c * 1.6)[:len(x[k:k + seg])]
    env = np.sin(np.pi * np.clip(t / (n / SR), 0, 1)) ** 2
    out = out * env
    return out / np.abs(out).max() * .6


def crowd(n=int(SR * 3.2)):
    t = np.arange(n) / SR; x = RNG.standard_normal(n)
    roar = _band(x, 250, 2600) + .5 * _band(RNG.standard_normal(n), 2600, 5000)
    flutter = 1 + .25 * np.sin(2 * np.pi * 5.5 * t + 3 * np.sin(2 * np.pi * .7 * t))
    env = np.minimum(1, t / .45) * np.exp(-np.maximum(0, t - .9) / 1.1)
    y = roar * flutter * env
    return y / np.abs(y).max() * .7


def stamp(n=int(SR * .5)):
    t = np.arange(n) / SR
    thump = np.sin(2 * np.pi * (95 - 40 * t) * t) * _env(n, .002, .09)
    click = _band(RNG.standard_normal(n), 800, 6000) * _env(n, .0005, .012)
    x = thump + .8 * click
    return x / np.abs(x).max()


def tick(n=int(SR * .08)):
    t = np.arange(n) / SR
    x = np.sin(2 * np.pi * 1850 * t) * _env(n, .0005, .012) + .4 * np.sin(2 * np.pi * 3700 * t) * _env(n, .0005, .006)
    return x / np.abs(x).max()


KINDS = {"crack": crack, "bounce": bounce, "whoosh": whoosh, "crowd": crowd, "stamp": stamp, "tick": tick}
GAIN = {"crack": .55, "bounce": .25, "whoosh": .16, "crowd": .22, "stamp": .5, "tick": .12}


def render(events, total, out):
    buf = np.zeros(int(SR * (total + 4)))
    cache = {}
    for tm, kind, g in events:
        if kind not in cache: cache[kind] = KINDS[kind]()
        s = cache[kind] * GAIN[kind] * g; i = int(tm * SR)
        if i < 0 or i >= len(buf): continue
        e = min(len(buf), i + len(s)); buf[i:e] += s[:e - i]
    buf = np.clip(buf[:int(SR * total)], -1, 1)
    st = (np.repeat(buf[:, None], 2, 1) * 32767).astype(np.int16)
    with wave.open(out, "wb") as w:
        w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR); w.writeframes(st.tobytes())


if __name__ == "__main__":
    render(json.load(open(sys.argv[1])), float(sys.argv[2]), sys.argv[3])
