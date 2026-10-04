import os, sys, wave
import numpy as np

SR = 44100
BPM = 120.0
BEAT = 60.0 / BPM
BAR = 4 * BEAT
DUR = 30.0
N = int(SR * DUR)
L = np.zeros(N)
R = np.zeros(N)
SAMPLES = sys.argv[1]
OUT = sys.argv[2]
rng = np.random.default_rng(7)

INTRO_END = 2.0
DNA_START, DNA_END = 8.0, 12.0
STROBE = 22.0
STOP = 23.5
FINAL = 24.0


def load(name):
    w = wave.open(os.path.join(SAMPLES, name), 'rb')
    ch, sw, fr, n = w.getnchannels(), w.getsampwidth(), w.getframerate(), w.getnframes()
    raw = w.readframes(n)
    w.close()
    dt = {1: np.int8, 2: np.int16, 4: np.int32}[sw]
    data = np.frombuffer(raw, dtype=dt).astype(np.float64).reshape(-1, ch).mean(axis=1)
    data /= float(2 ** (8 * sw - 1))
    if fr != SR:
        idx = np.minimum((np.arange(int(n * SR / fr)) * fr / SR).astype(int), n - 1)
        data = data[idx]
    return data


def pan_gains(gain, pan):
    return gain * np.cos((pan + 1) * np.pi / 4), gain * np.sin((pan + 1) * np.pi / 4)


def mix(sig, t, gain=1.0, pan=0.0):
    s = int(t * SR)
    if s >= N:
        return
    e = min(N, s + len(sig))
    gl, gr = pan_gains(gain, pan)
    L[s:e] += sig[:e - s] * gl
    R[s:e] += sig[:e - s] * gr


def midi(n):
    return 440.0 * 2 ** ((n - 69) / 12.0)


def tone(note, t, length, gain, kind='square', pan=0.0, attack=0.005, release=0.08, detune=0.0, bend=0.0):
    n = int(length * SR)
    tt = np.arange(n) / SR
    f = midi(note) * (1 + bend * np.exp(-tt * 30))
    ph = np.cumsum(f) / SR
    ph2 = ph * (1 + detune)
    if kind == 'square':
        v = np.where(ph % 1 < 0.5, 1.0, -1.0) * 0.5 + np.where(ph2 % 1 < 0.25, 1.0, -1.0) * 0.5
    elif kind == 'saw':
        v = ((2 * (ph % 1) - 1) + (2 * (ph2 % 1) - 1)) * 0.5
    elif kind == 'tri':
        v = 4 * np.abs(ph % 1 - 0.5) - 1
    else:
        v = np.sin(2 * np.pi * ph)
    env = np.minimum(1.0, tt / attack) if attack > 0 else np.ones(n)
    rem = length - tt
    env *= np.clip(rem / release, 0, 1)
    mix(v * env, t, gain, pan)


def riser(t, length, gain):
    n = int(length * SR)
    k = np.arange(n) / n
    noise = rng.uniform(-1, 1, n)
    out = np.zeros(n)
    lp = 0.0
    a = 0.02 + 0.5 * k * k
    for i in range(n):
        lp += a[i] * (noise[i] - lp)
        out[i] = lp
    mix(out * k * k, t, gain)


def sweep_down(t, length, gain):
    n = int(length * SR)
    tt = np.arange(n) / SR
    f = 900 * np.exp(-tt * 6) + 40
    ph = np.cumsum(f) / SR
    mix(np.sin(2 * np.pi * ph) * np.exp(-tt * 3), t, gain)


kick = load('Kick2.wav')
snare = load('Snare1.wav')
hat = load('Cymbal1.wav')
crash = load('Cymbal2.wav')
tom = load('Tom1.wav')

chords = [[60, 64, 67, 71], [57, 60, 64, 67], [53, 57, 60, 64], [55, 59, 62, 67]]
bass = [36, 33, 29, 31]

for b in range(int(INTRO_END / BEAT)):
    t = b * BEAT
    ch = chords[0] if b < 2 else chords[3]
    for k, note in enumerate(ch):
        tone(note + 12, t + k * BEAT / 4, BEAT / 4 * 0.9, 0.035 * (0.4 + b / 4), 'tri', pan=-0.4 + 0.25 * k)
riser(0.4, INTRO_END - 0.4, 0.35)
for note in [48, 60, 64, 67]:
    tone(note, 0.0, INTRO_END, 0.018, 'saw', attack=1.6, release=0.2, detune=0.004)

t = INTRO_END
step = 0
while t < STROBE - 1e-6:
    bib = step % 4
    ci = int((t - INTRO_END) / BAR) % 4
    dna = DNA_START <= t < DNA_END
    hard = t >= DNA_END
    if dna:
        if bib in (0, 2):
            mix(kick, t, 0.6)
        mix(hat, t + BEAT / 2, 0.14, 0.3)
        tone(bass[ci], t, BEAT * 0.9, 0.12, 'tri', release=0.1)
        arp = chords[ci]
        for k in range(4):
            n = arp[(step * 4 + k) % 4] + 24
            tone(n, t + k * BEAT / 4, BEAT / 4 * 0.7, 0.03, 'sine', pan=0.6 if k % 2 else -0.6, release=0.06)
    else:
        mix(kick, t, 0.95 if hard else 0.85)
        if bib in (1, 3):
            mix(snare, t, 0.6 if hard else 0.5, 0.1)
        mix(hat, t + BEAT / 2, 0.22, 0.3)
        mix(hat, t, 0.12, -0.3)
        if hard:
            mix(hat, t + BEAT / 4, 0.08, 0.5)
            mix(hat, t + 3 * BEAT / 4, 0.08, -0.5)
        tone(bass[ci], t, BEAT * 0.45, 0.16, 'square', release=0.05)
        tone(bass[ci] + 12, t + BEAT / 2, BEAT * 0.4, 0.09, 'square', release=0.05)
        arp = chords[ci]
        for k in range(4):
            n = arp[(step * 4 + k) % 4] + 12 + (12 if k == 3 else 0)
            tone(n, t + k * BEAT / 4, BEAT / 4 * 0.8, 0.045, 'square', pan=0.5 if k % 2 else -0.5, release=0.03, detune=0.003)
        if bib == 0:
            for note in arp:
                tone(note, t, BAR * 0.95, 0.012 if not hard else 0.016, 'saw', attack=0.05, release=0.3, detune=0.005)
        if hard and bib == 0 and int((t - DNA_END) / BAR) % 2 == 1:
            tone(arp[0] + 24, t, BEAT * 1.5, 0.03, 'square', release=0.3, bend=0.06)
    t += BEAT
    step += 1

mix(crash, INTRO_END, 0.6)
mix(crash, DNA_START, 0.3, -0.2)
sweep_down(DNA_START, 1.2, 0.08)
riser(DNA_END - 1.0, 1.0, 0.22)
mix(crash, DNA_END, 0.65)
for tt in (16.0, 18.0):
    mix(crash, tt, 0.35, 0.2)
for k in range(4):
    mix(tom, DNA_END - BEAT + k * BEAT / 4, 0.3 + 0.1 * k, -0.5 + 0.33 * k)
for k in range(4):
    mix(snare, 18.0 - BEAT + k * BEAT / 4, 0.25 + 0.1 * k, 0.1)

for k in range(12):
    tt = STROBE + k * (STOP - STROBE) / 12
    mix(tom if k % 3 else kick, tt, 0.35 + 0.04 * k, -0.6 + 0.1 * k)
    tone(72 + (k % 4) * 3, tt, 0.08, 0.025, 'square', release=0.03)
riser(STROBE, STOP - STROBE, 0.3)

mix(kick, FINAL, 1.0)
mix(crash, FINAL, 0.85)
sweep_down(FINAL, 1.5, 0.12)
for note in [48, 60, 64, 67, 72, 76]:
    tone(note, FINAL, DUR - FINAL, 0.03, 'saw', attack=0.01, release=3.5, detune=0.004)
    tone(note + 12, FINAL, 0.6, 0.025, 'square', release=0.5)
for k in range(16):
    tt = 26.0 + k * BEAT / 2
    tone([84, 88, 91, 95][k % 4], tt, 0.18, 0.018 * (1 - k / 18), 'tri', pan=-0.5 + (k % 4) / 3, release=0.12)

peak = max(np.abs(L).max(), np.abs(R).max())
g = 0.89 / peak
fade = int(1.2 * SR)
env = np.ones(N)
env[-fade:] = np.linspace(1, 0, fade)
st = np.stack([L, R], axis=1) * g * env[:, None]
pcm = (np.clip(st, -1, 1) * 32767).astype('<i2')
w = wave.open(OUT, 'wb')
w.setnchannels(2)
w.setsampwidth(2)
w.setframerate(SR)
w.writeframes(pcm.tobytes())
w.close()
print('ok peak', peak)
