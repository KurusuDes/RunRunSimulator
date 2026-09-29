import math, wave, struct, random, sys, os

SR = 44100
BPM = 120.0
BEAT = 60.0 / BPM
DUR = 15.0
N = int(SR * DUR)
L = [0.0] * N
R = [0.0] * N
SAMPLES = sys.argv[1]
OUT = sys.argv[2]


def load(name):
    w = wave.open(os.path.join(SAMPLES, name), 'rb')
    ch, sw, fr, n = w.getnchannels(), w.getsampwidth(), w.getframerate(), w.getnframes()
    raw = w.readframes(n)
    w.close()
    fmt = {1: 'b', 2: 'h', 4: 'i'}[sw]
    data = struct.unpack('<%d%s' % (n * ch, fmt), raw)
    scale = float(2 ** (8 * sw - 1))
    mono = [sum(data[i * ch + c] for c in range(ch)) / ch / scale for i in range(n)]
    if fr != SR:
        ratio = fr / SR
        mono = [mono[min(int(i * ratio), n - 1)] for i in range(int(n / ratio))]
    return mono


def place(buf, t, gain=1.0, pan=0.0):
    start = int(t * SR)
    gl = gain * math.cos((pan + 1) * math.pi / 4)
    gr = gain * math.sin((pan + 1) * math.pi / 4)
    for i, s in enumerate(buf):
        j = start + i
        if j >= N:
            break
        L[j] += s * gl
        R[j] += s * gr


def midi(n):
    return 440.0 * 2 ** ((n - 69) / 12.0)


def tone(freq, t, length, gain, kind='square', pan=0.0, attack=0.005, release=0.08, detune=0.0):
    start = int(t * SR)
    n = int(length * SR)
    phase = 0.0
    phase2 = 0.0
    gl = gain * math.cos((pan + 1) * math.pi / 4)
    gr = gain * math.sin((pan + 1) * math.pi / 4)
    for i in range(n):
        j = start + i
        if j >= N:
            break
        tt = i / SR
        env = min(1.0, tt / attack) if attack > 0 else 1.0
        rem = length - tt
        if rem < release:
            env *= max(0.0, rem / release)
        phase += freq / SR
        phase2 += freq * (1 + detune) / SR
        if kind == 'square':
            v = (1.0 if (phase % 1.0) < 0.5 else -1.0) * 0.5 + (1.0 if (phase2 % 1.0) < 0.25 else -1.0) * 0.5
        elif kind == 'saw':
            v = 2.0 * (phase % 1.0) - 1.0 + 2.0 * (phase2 % 1.0) - 1.0
            v *= 0.5
        elif kind == 'tri':
            p = phase % 1.0
            v = 4.0 * abs(p - 0.5) - 1.0
        else:
            v = math.sin(2 * math.pi * phase)
        s = v * env
        L[j] += s * gl
        R[j] += s * gr


def noise_riser(t, length, gain):
    start = int(t * SR)
    n = int(length * SR)
    lp = 0.0
    for i in range(n):
        j = start + i
        if j >= N:
            break
        k = i / n
        a = 0.02 + 0.5 * k * k
        lp += a * (random.uniform(-1, 1) - lp)
        s = lp * gain * k * k
        L[j] += s
        R[j] += s


kick = load('Kick2.wav')
snare = load('Snare1.wav')
hat = load('Cymbal1.wav')
crash = load('Cymbal2.wav')
tom = load('Tom1.wav')

chords = [
    [60, 64, 67, 71],
    [57, 60, 64, 67],
    [53, 57, 60, 64],
    [55, 59, 62, 67],
]
bass = [36, 33, 29, 31]

HIT = 2.0
STOP = 12.5
FINAL = 13.0

for b in range(int(HIT / BEAT)):
    t = b * BEAT
    ch = chords[0] if b < 2 else chords[1]
    for k, note in enumerate(ch):
        tone(midi(note + 12), t + k * BEAT / 4, BEAT / 4 * 0.9, 0.035 * (0.4 + b / 4), 'tri', pan=-0.4 + 0.25 * k)
noise_riser(0.5, HIT - 0.5, 0.35)
for k, note in enumerate([60, 64, 67, 72]):
    tone(midi(note - 12), 0.0, HIT, 0.018, 'saw', attack=1.6, release=0.2, detune=0.004)

bar = 4 * BEAT
t = HIT
step = 0
while t < STOP - 1e-6:
    beat_in_bar = step % 4
    ci = int((t - HIT) / bar) % 4
    place(kick, t, 0.9)
    if beat_in_bar in (1, 3):
        place(snare, t, 0.55, 0.1)
    place(hat, t + BEAT / 2, 0.22, 0.3)
    place(hat, t, 0.12, -0.3)
    tone(midi(bass[ci]), t, BEAT * 0.45, 0.16, 'square', release=0.05)
    tone(midi(bass[ci] + 12), t + BEAT / 2, BEAT * 0.4, 0.09, 'square', release=0.05)
    arp = chords[ci]
    for k in range(4):
        n = arp[(step * 4 + k) % 4] + 12 + (12 if k == 3 else 0)
        tone(midi(n), t + k * BEAT / 4, BEAT / 4 * 0.8, 0.045, 'square', pan=0.5 if k % 2 else -0.5, release=0.03, detune=0.003)
    if beat_in_bar == 0:
        for note in arp:
            tone(midi(note), t, bar * 0.95, 0.012, 'saw', attack=0.05, release=0.3, detune=0.005)
    t += BEAT
    step += 1

place(crash, HIT, 0.6)
for tt in (6.0, 10.0):
    place(crash, tt, 0.35, 0.2)
for k in range(4):
    place(tom, STOP - BEAT + k * BEAT / 4, 0.35 + 0.1 * k, -0.5 + 0.33 * k)
noise_riser(STOP - 1.5, 1.5, 0.25)

place(kick, FINAL, 1.0)
place(crash, FINAL, 0.8)
for note in [48, 60, 64, 67, 72, 76]:
    tone(midi(note), FINAL, DUR - FINAL, 0.03, 'saw', attack=0.01, release=1.6, detune=0.004)
    tone(midi(note + 12), FINAL, 0.6, 0.025, 'square', release=0.5)

peak = max(max(abs(x) for x in L), max(abs(x) for x in R))
g = 0.89 / peak if peak > 0 else 1.0
fade = int(0.02 * SR)
w = wave.open(OUT, 'wb')
w.setnchannels(2)
w.setsampwidth(2)
w.setframerate(SR)
frames = bytearray()
for i in range(N):
    f = 1.0
    if i > N - fade:
        f = (N - i) / fade
    frames += struct.pack('<hh', int(max(-1, min(1, L[i] * g * f)) * 32767), int(max(-1, min(1, R[i] * g * f)) * 32767))
w.writeframes(bytes(frames))
w.close()
print('ok peak', peak)
