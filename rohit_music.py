"""Hype bed for the Rohit reel: 126 bpm, four-on-the-floor kick, clap on 2 and 4, dhol/tasha pattern (Mumbai drums), driving bass, bright pad + arp, risers and impacts at scene cuts.
Usage: rohit_music.py durs.json OUT.wav"""
import sys, json, numpy as np, wave
from scipy.signal import lfilter, butter
SR = 44100; durs = json.load(open(sys.argv[1])); out = sys.argv[2]; dur = sum(durs); starts = [sum(durs[:i]) for i in range(len(durs))]
n = int(SR * dur); t = np.arange(n) / SR; bpm = 126; beat = 60 / bpm; rng = np.random.default_rng(7)
def note(m): return 440 * 2 ** ((m - 69) / 12)
def add(buf, s, at):
    i = int(at * SR)
    if 0 <= i < len(buf): e = min(len(buf), i + len(s)); buf[i:e] += s[:e - i]
kt = np.arange(int(.32 * SR)) / SR; kick = np.sin(2 * np.pi * (45 + 90 * np.exp(-kt * 35)) * kt) * np.exp(-kt * 8)
ct = np.arange(int(.22 * SR)) / SR; bc, ac = butter(2, [1200 / (SR / 2), 7000 / (SR / 2)], "band"); clap = lfilter(bc, ac, rng.standard_normal(len(ct))) * np.exp(-ct * 22)
ht = np.arange(int(.05 * SR)) / SR; bh, ah = butter(2, 8000 / (SR / 2), "high"); hat = lfilter(bh, ah, rng.standard_normal(len(ht))) * np.exp(-ht * 70)
dt = np.arange(int(.28 * SR)) / SR; dhol = np.sin(2 * np.pi * (70 + 60 * np.exp(-dt * 25)) * dt) * np.exp(-dt * 11)
tt_ = np.arange(int(.09 * SR)) / SR; bt, at_ = butter(2, 3000 / (SR / 2), "high"); tasha = lfilter(bt, at_, rng.standard_normal(len(tt_))) * np.exp(-tt_ * 45)
drums = np.zeros(n); dh = np.zeros(n); k = 0
while k * beat < dur:
    b = k * beat; add(drums, kick * .9, b)
    if k % 4 in (1, 3): add(drums, clap * .5, b)
    add(drums, hat * .22, b + beat / 2)
    for j, (off, g) in enumerate(((0, 1), (.25, .5), (.5, .8), (.75, .5))): add(dh, tasha * .28 * g, b + off * beat)    # tasha 16ths
    if k % 4 in (0, 2): add(dh, dhol * .8, b + .25 * beat); add(dh, dhol * .6, b + .75 * beat)                          # dhol syncopation
    k += 1
# bass + pad + arp: C - G - Am - F, bar by bar
bar = 4 * beat; chords = [[60, 64, 67], [55, 59, 62], [57, 60, 64], [53, 57, 60]]; roots = [36, 31, 33, 29]
pad = np.zeros(n); bass = np.zeros(n); arp = np.zeros(n)
for bi in range(int(dur / bar) + 2):
    s0 = bi * bar; a = int(s0 * SR); b = min(n, int((s0 + bar + .2) * SR))
    if a >= n: break
    tt = t[a:b] - s0; env = np.minimum(1, tt / .05) * np.minimum(1, np.maximum(0, (bar + .2 - tt) / .2)); c = chords[bi % 4]
    for m in c:
        for det in (-.1, .1): f = note(m + 12) * 2 ** (det / 12); pad[a:b] += env * (np.sin(2 * np.pi * f * tt) + .4 * np.sin(4 * np.pi * f * tt)) / 12
    for q in range(8):
        e0 = s0 + q * beat / 2; ai = int(e0 * SR); ln = int(.5 * beat * SR)
        if ai + ln >= n: break
        f = note(roots[bi % 4] + 12); bseg = np.sin(2 * np.pi * f * np.arange(ln) / SR) * np.exp(-np.arange(ln) / SR * 6); bass[ai:ai + ln] += bseg * (.5 if q % 2 == 0 else .3)
        f2 = note(c[q % 3] + 24); aseg = np.sign(np.sin(2 * np.pi * f2 * np.arange(ln) / SR)) * np.exp(-np.arange(ln) / SR * 9) * .06; arp[ai:ai + ln] += aseg
bl, al = butter(2, 2500 / (SR / 2)); pad = lfilter(bl, al, pad); arp = lfilter(bl, al, arp)
# sidechain pump from the kick
pump = np.ones(n); k = 0
while k * beat < dur:
    i = int(k * beat * SR); L = int(.22 * SR)
    if i + L < n: pump[i:i + L] = np.minimum(pump[i:i + L], 1 - .6 * np.exp(-np.arange(L) / SR * 14))
    k += 1
# risers into every cut + impact on the cut
fx = np.zeros(n)
for s in starts[1:]:
    L = int(1.1 * SR); i = int(s * SR) - L
    if i < 0: continue
    x = lfilter(*butter(2, [500 / (SR / 2), 9000 / (SR / 2)], "band"), rng.standard_normal(L)) * (np.linspace(0, 1, L) ** 2) * .35; fx[i:i + L] += x
    add(fx, kick * 1.2 + .5 * np.sin(2 * np.pi * 55 * np.arange(int(.6 * SR)) / SR)[:len(kick)] * np.exp(-np.arange(len(kick)) / SR * 5), s)
mix = (pad * .5 + arp + bass) * pump + drums * .85 + dh * .55 + fx
env = np.clip(t / .3, 0, 1) * np.clip((dur - t) / 2.5, 0, 1); mix *= env
mix /= np.abs(mix).max() + 1e-9; mix *= .9
st = np.stack([mix, np.roll(mix, int(.01 * SR))], 1)
with wave.open(out, "wb") as w: w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR); w.writeframes((st * 32767).astype(np.int16).tobytes())
