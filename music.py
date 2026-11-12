"""Synthesize a calm, cinematic music bed: warm pad chords + soft pulse. Usage: music.py SECONDS OUT.wav"""
import sys, numpy as np, wave
from scipy.signal import lfilter, butter

SR = 44100
dur = float(sys.argv[1]); out = sys.argv[2]
n = int(SR * dur); t = np.arange(n) / SR
bpm = 88; beat = 60 / bpm; bar = 4 * beat

def note(m): return 440 * 2 ** ((m - 69) / 12)
# Am - F - C - G, voiced low
chords = [[57, 60, 64, 69], [53, 57, 60, 65], [48, 55, 60, 64], [55, 59, 62, 67]]
bass = [45, 41, 48, 43]

pad = np.zeros(n); low = np.zeros(n)
rng = np.random.default_rng(3)
for i in range(int(dur / (2 * bar)) + 2):
    c = chords[i % 4]; s0 = i * 2 * bar
    a, b = int(s0 * SR), min(n, int((s0 + 2 * bar + 1.5) * SR))
    if a >= n: break
    tt = t[a:b] - s0
    env = np.minimum(1, tt / 1.2) * np.minimum(1, np.maximum(0, (2 * bar + 1.5 - tt) / 1.5))
    for m in c:
        for det in (-0.12, 0.0, 0.12):
            f = note(m) * 2 ** (det / 12)
            ph = rng.random() * 6.28
            pad[a:b] += env * (np.sin(2 * np.pi * f * tt + ph) + .3 * np.sin(4 * np.pi * f * tt + ph)) / 12
    fb = note(bass[i % 4])
    low[a:b] += env * np.sin(2 * np.pi * fb * tt) * .35

bb, ab = butter(2, 1800 / (SR / 2))
pad = lfilter(bb, ab, pad)
# slow swell
pad *= .8 + .2 * np.sin(2 * np.pi * t / 16)

# soft pulse: kick on 1 and 3, shaker on off-beats
perc = np.zeros(n)
kl = int(.35 * SR); kt = np.arange(kl) / SR
kick = np.sin(2 * np.pi * (48 + 70 * np.exp(-kt * 30)) * kt) * np.exp(-kt * 9)
sl = int(.06 * SR); st = np.arange(sl) / SR
hs, ha = butter(2, 6000 / (SR / 2), 'high')
shk = lfilter(hs, ha, rng.standard_normal(sl)) * np.exp(-st * 60)
k = 0
while k * beat < dur:
    p = int(k * beat * SR)
    if k % 2 == 0 and p + kl < n: perc[p:p + kl] += kick * .55
    q = int((k + .5) * beat * SR)
    if q + sl < n: perc[q:q + sl] += shk * .12
    k += 1
# percussion enters after the hook and drops for the final question
perc *= np.clip((t - 9) / 3, 0, 1) * np.clip((dur - 8 - t) / 2, 0, 1)

mix = pad * .55 + low + perc
mix *= np.clip(t / 2, 0, 1) * np.clip((dur - t) / 3, 0, 1)
mix /= np.abs(mix).max() + 1e-9
mix *= 0.9
stereo = np.stack([mix, np.roll(mix, int(.012 * SR))], 1)
with wave.open(out, 'wb') as w:
    w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR)
    w.writeframes((stereo * 32767).astype(np.int16).tobytes())
