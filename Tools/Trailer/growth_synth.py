import os, sys, math, wave, random
from array import array

SR = 44100
DUR = 48.0
N = int(SR * DUR)
BEAT = 0.5625
BAR = 4 * BEAT
TWO_PI = 2 * math.pi
PEAK_DB = -1.0


def _run(a, b, step=0.25):
    n = int((b - a) / step + 1e-9)
    return [round(a + i * step, 3) for i in range(n + 1)]


POPS = (_run(3.2, 11.5) + _run(12.2, 16.5) + _run(17.2, 25.5)
        + _run(26.2, 34.5) + _run(35.2, 42.5))
_POPS_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "growth", "pops.txt")
if os.path.exists(_POPS_FILE):
    with open(_POPS_FILE) as _f:
        POPS = [float(x) for x in _f.read().split() if x.strip()]

POP_LOW, POP_HIGH = 79, 97
PENT = (0, 2, 4, 7, 9)

random.seed(11)


def mtof(m):
    return 440.0 * 2 ** ((m - 69) / 12.0)


class Bus:
    def __init__(self):
        self.L = [0.0] * N
        self.R = [0.0] * N
        self.S = [0.0] * N

    def mix(self, sig, t, g=1.0, pan=0.0, send=0.0):
        s = int(round(t * SR))
        if s >= N or s < 0:
            return
        e = min(N, s + len(sig))
        seg = sig[:e - s]
        gl = g * math.cos((pan + 1) * math.pi / 4)
        gr = g * math.sin((pan + 1) * math.pi / 4)
        self.L[s:e] = [a + b * gl for a, b in zip(self.L[s:e], seg)]
        self.R[s:e] = [a + b * gr for a, b in zip(self.R[s:e], seg)]
        if send:
            gs = g * send
            self.S[s:e] = [a + b * gs for a, b in zip(self.S[s:e], seg)]


_cache = {}


def cached(key, fn):
    if key not in _cache:
        _cache[key] = fn()
    return _cache[key]


def fade_tail(out, k):
    k = min(k, len(out))
    n = len(out)
    for i in range(k):
        out[n - k + i] *= 1.0 - i / k
    return out


def marimba(m):
    def build():
        tau = 0.24 if m < 72 else (0.17 if m < 84 else 0.11)
        n = int(SR * tau * 4.5)
        w = TWO_PI * mtof(m) / SR
        att = int(0.002 * SR)
        out = [0.0] * n
        for i in range(n):
            t = i / SR
            e = math.exp(-t / tau)
            e2 = math.exp(-t / (tau * 0.12))
            v = math.sin(w * i) * e + 0.32 * math.sin(4 * w * i) * e2 + 0.08 * math.sin(9.9 * w * i) * e2
            if i < att:
                v *= i / att
            out[i] = v * 0.5
        return fade_tail(out, 300)
    return cached(('mar', m), build)


def pluck(m):
    def build():
        n = int(SR * 0.9)
        w = TWO_PI * mtof(m) / SR
        att = int(0.004 * SR)
        parts = ((1, 1.0, 0.30), (2, 0.5, 0.18), (3, 0.25, 0.10), (5, 0.08, 0.05))
        out = [0.0] * n
        for i in range(n):
            t = i / SR
            v = 0.0
            for h, a, tau in parts:
                v += a * math.sin(w * h * i) * math.exp(-t / tau)
            if i < att:
                v *= i / att
            out[i] = v * 0.4
        return fade_tail(out, 300)
    return cached(('plk', m), build)


def bell(m, scale=1.0):
    def build():
        n = int(SR * 2.2 * scale)
        w = TWO_PI * mtof(m) / SR
        att = int(0.002 * SR)
        parts = ((1.0, 1.0, 1.1), (2.0, 0.45, 0.7), (2.76, 0.3, 0.55), (5.4, 0.12, 0.3))
        out = [0.0] * n
        for i in range(n):
            t = i / SR
            v = 0.0
            for r, a, tau in parts:
                v += a * math.sin(w * r * i) * math.exp(-t / (tau * scale))
            if i < att:
                v *= i / att
            out[i] = v * 0.3
        return fade_tail(out, 400)
    return cached(('bel', m, scale), build)


def pad(notes, length, att=0.45, rel=0.9):
    def build():
        total = length + rel
        n = int(SR * total)
        env = [min(1.0, (i / SR) / att) * min(1.0, (total - i / SR) / rel) for i in range(n)]
        env = [0.5 - 0.5 * math.cos(math.pi * x) for x in env]
        out = [0.0] * n
        for m in notes:
            w = TWO_PI * mtof(m) / SR
            for i in range(n):
                x = w * i
                out[i] += env[i] * (math.sin(x) + 0.7 * math.sin(x * 1.0035) + 0.12 * math.sin(2 * x))
        return [v * 0.11 for v in out]
    return cached(('pad', tuple(notes), length, att, rel), build)


def bass(m):
    def build():
        n = int(SR * 1.2)
        w = TWO_PI * mtof(m) / SR
        att = int(0.01 * SR)
        out = [0.0] * n
        for i in range(n):
            t = i / SR
            e = math.exp(-t / 0.4)
            v = (math.sin(w * i) + 0.3 * math.sin(2 * w * i) * math.exp(-t / 0.15)) * e
            if i < att:
                v *= i / att
            out[i] = v * 0.7
        return fade_tail(out, 400)
    return cached(('bas', m), build)


def kick():
    def build():
        n = int(SR * 0.25)
        out = [0.0] * n
        ph = 0.0
        for i in range(n):
            t = i / SR
            f = 48 + 70 * math.exp(-t * 35)
            ph += TWO_PI * f / SR
            out[i] = math.sin(ph) * math.exp(-t / 0.07) * 0.8
        return fade_tail(out, 200)
    return cached(('kick',), build)


def shaker(var):
    def build():
        r = random.Random(100 + var)
        n = int(SR * 0.12)
        out = [0.0] * n
        prev = 0.0
        for i in range(n):
            t = i / SR
            x = r.uniform(-1, 1)
            hp = x - prev
            prev = x
            a = min(1.0, t / 0.004)
            out[i] = hp * a * math.exp(-t / 0.028) * 0.35
        return fade_tail(out, 200)
    return cached(('shk', var), build)


def wood():
    def build():
        n = int(SR * 0.1)
        out = [0.0] * n
        for i in range(n):
            t = i / SR
            out[i] = (math.sin(TWO_PI * 980 * t) + 0.5 * math.sin(TWO_PI * 1560 * t)) * math.exp(-t / 0.018) * 0.4
        return fade_tail(out, 200)
    return cached(('wood',), build)


def swell(length):
    def build():
        r = random.Random(5)
        n = int(SR * length)
        out = [0.0] * n
        y = 0.0
        for i in range(n):
            k = i / n
            a = 0.02 + 0.5 * k * k
            y += a * (r.uniform(-1, 1) - y)
            out[i] = y * k * k * 0.5
        return fade_tail(out, 400)
    return cached(('swl', length), build)


def xylo(m):
    def build():
        r = random.Random(m)
        n = int(SR * 0.28)
        w = TWO_PI * mtof(m) / SR
        out = [0.0] * n
        for i in range(n):
            t = i / SR
            v = math.sin(w * i) * math.exp(-t / 0.07) + 0.4 * math.sin(3.0 * w * i) * math.exp(-t / 0.03) \
                + 0.15 * math.sin(6.1 * w * i) * math.exp(-t / 0.015)
            if i < 60:
                v += r.uniform(-1, 1) * 0.25 * (1 - i / 60)
            out[i] = v * 0.55
        return fade_tail(out, 300)
    return cached(('xyl', m), build)


def comb_bw(x, d, fb):
    out = [0.0] * N
    zeros = [0.0] * d
    for s in range(0, N, d):
        xb = x[s:s + d]
        prev = out[s - d:s] if s >= d else zeros
        out[s:s + len(xb)] = [a + fb * b for a, b in zip(xb, prev)]
    return out


def allpass_bw(x, d, g):
    out = [0.0] * N
    zeros = [0.0] * d
    for s in range(0, N, d):
        xb = x[s:s + d]
        xp = x[s - d:s] if s >= d else zeros
        yp = out[s - d:s] if s >= d else zeros
        out[s:s + len(xb)] = [-g * a + b + g * c for a, b, c in zip(xb, xp, yp)]
    return out


def lowpass(x, a):
    y = 0.0
    out = [0.0] * len(x)
    for i, v in enumerate(x):
        y += a * (v - y)
        out[i] = y
    return out


def reverb(send, offset):
    delays = (1557, 1617, 1491, 1422, 1277, 1356)
    acc = [0.0] * N
    for d in delays:
        c = comb_bw(send, d + offset, 0.85)
        acc = [a + b for a, b in zip(acc, c)]
    acc = [v * 0.18 for v in acc]
    acc = allpass_bw(acc, 556 + offset, 0.5)
    acc = allpass_bw(acc, 441 + offset, 0.5)
    return lowpass(acc, 0.35)


CHORDS = {
    'C': dict(pad=[60, 64, 67], root=48, ct=[64, 67, 72, 67]),
    'Am': dict(pad=[57, 60, 64], root=45, ct=[64, 69, 72, 69]),
    'F': dict(pad=[57, 60, 65], root=41, ct=[65, 69, 72, 69]),
    'G': dict(pad=[59, 62, 67], root=43, ct=[62, 67, 71, 67]),
}
PROG = ['C', 'Am', 'F', 'G']

MEL_A = {
    'C': [(0, 76, 1), (1, 79, 1), (2, 76, 1), (3, 72, 1)],
    'Am': [(0, 72, 1), (1, 76, 1), (2, 81, 2)],
    'F': [(0, 77, 1), (1, 81, 1), (2, 77, 1), (3, 72, 1)],
    'G': [(0, 74, 1), (1, 79, 1), (2, 83, 1), (3, 79, 1)],
}
MEL_B = {
    'C': [(0, 79, .5), (.5, 76, .5), (1, 72, 1), (2, 76, .5), (2.5, 79, .5), (3, 84, 1)],
    'Am': [(0, 81, 1), (1, 79, .5), (1.5, 76, .5), (2, 72, 1), (3, 76, 1)],
    'F': [(0, 77, .5), (.5, 81, .5), (1, 84, 1), (2, 81, .5), (2.5, 77, .5), (3, 72, 1)],
    'G': [(0, 74, .5), (.5, 79, .5), (1, 83, 1), (2, 86, 1), (3, 83, .5), (3.5, 79, .5)],
}


def play_bar(b, t0, name, mel, mel_g, pad_g, bass_on=False, perc=0.0, counter=False, bright=False, bell_g=0.0):
    c = CHORDS[name]
    b.mix(pad(c['pad'], BAR), t0, pad_g, 0.0, 0.45)
    for beat, m, d in MEL_A[name] if mel == 'A' else MEL_B[name]:
        t = t0 + beat * BEAT
        b.mix(marimba(m), t, mel_g, 0.1, 0.3)
        if bright:
            b.mix(marimba(m + 12), t, mel_g * 0.35, 0.25, 0.4)
    if name == 'C' and bell_g:
        b.mix(bell(84, 0.8), t0, bell_g, 0.3, 0.6)
    if bass_on:
        r = c['root']
        b.mix(bass(r), t0, 0.8, 0.0)
        b.mix(bass(r + 7), t0 + 2 * BEAT, 0.6, 0.0)
        b.mix(bass(r + 12), t0 + 3.5 * BEAT, 0.35, 0.0)
    if perc:
        b.mix(kick(), t0, 0.6 * perc, 0.0)
        b.mix(kick(), t0 + 2 * BEAT, 0.5 * perc, 0.0)
        b.mix(wood(), t0 + BEAT, 0.35 * perc, -0.25, 0.15)
        b.mix(wood(), t0 + 3 * BEAT, 0.3 * perc, 0.25, 0.15)
        for k in range(8):
            b.mix(shaker(k % 3), t0 + k * BEAT / 2, (0.55 if k % 2 else 0.35) * perc, 0.2 if k % 2 else -0.2)
    if counter:
        for k, m in enumerate(c['ct']):
            b.mix(pluck(m), t0 + (k + 0.5) * BEAT, 0.5, -0.35, 0.3)
    if bright:
        for k, m in enumerate(c['ct']):
            b.mix(bell(m + 24, 0.45), t0 + k * BEAT + BEAT / 2, 0.3, 0.4 if k % 2 else -0.4, 0.5)


def build_music():
    b = Bus()

    b.mix(pad([60, 64, 67], 3.2, att=1.6, rel=1.0), 0.0, 0.7, 0.0, 0.5)
    for t, m in ((0.3, 84), (1.1, 91), (1.9, 88), (2.6, 84)):
        b.mix(bell(m, 1.0), t, 0.9, 0.3 if m % 2 else -0.3, 0.7)

    for i, name in enumerate(PROG):
        play_bar(b, 3.0 + i * BAR, name, 'A', 0.75, 0.55, bell_g=0.5)

    rise = [60, 64, 67, 72, 64, 67, 72, 76, 67, 72, 76, 79, 72, 76, 79, 84]
    step = BEAT / 2
    for k, m in enumerate(rise):
        g = 0.35 + 0.55 * k / 15
        b.mix(marimba(m), 12.0 + k * step, g, -0.3 + 0.6 * k / 15, 0.35)
    b.mix(pad(CHORDS['F']['pad'], BAR, att=0.3), 12.0, 0.6, 0.0, 0.5)
    b.mix(pad(CHORDS['G']['pad'], BAR, att=0.3), 12.0 + BAR, 0.8, 0.0, 0.5)
    b.mix(bass(41), 12.0, 0.45)
    b.mix(bass(48 - 7), 12.0 + 2 * BEAT, 0.4)
    b.mix(bass(43), 12.0 + BAR, 0.65)
    b.mix(bass(50), 12.0 + BAR + 2 * BEAT, 0.55)
    for k in range(9):
        b.mix(shaker(k % 3), 14.25 + k * step, 0.2 + 0.35 * k / 8, 0.0)
    b.mix(swell(4.5), 12.0, 0.6, 0.0, 0.3)
    for k, m in enumerate((79, 83, 86, 91)):
        b.mix(marimba(m), 16.5 + k * 0.125, 0.8, 0.3, 0.4)
    b.mix(bell(84, 0.8), 17.0, 0.7, 0.0, 0.6)

    for i, name in enumerate(PROG):
        play_bar(b, 17.0 + i * BAR, name, 'B', 0.75, 0.55, bass_on=True, perc=0.6, bell_g=0.5)
    b.mix(bell(96, 0.8), 26.0, 0.7, 0.0, 0.6)

    for i, name in enumerate(PROG):
        play_bar(b, 26.0 + i * BAR, name, 'B', 0.75, 0.6, bass_on=True, perc=0.75, counter=True, bell_g=0.5)
    b.mix(bell(96, 0.8), 35.0, 0.9, 0.0, 0.6)

    for i, name in enumerate(PROG[:3]):
        play_bar(b, 35.0 + i * BAR, name, 'B', 0.85, 0.65, bass_on=True, perc=0.9, counter=True, bright=True, bell_g=0.6)

    t = 41.75
    b.mix(pad(CHORDS['G']['pad'], 1.25, att=0.15, rel=0.9), t, 0.8, 0.0, 0.5)
    b.mix(bass(43), t, 0.8)
    for k, m in enumerate((74, 79, 83, 86)):
        b.mix(marimba(m), t + k * 0.3, 0.85, -0.2 + 0.13 * k, 0.4)
        b.mix(bell(m + 12, 0.45), t + k * 0.3 + 0.15, 0.35, 0.3, 0.6)
    for k in range(4):
        b.mix(shaker(k % 3), t + k * 0.3, 0.5, 0.0)

    t = 43.0
    b.mix(pad([60, 64, 67, 72], 3.4, att=0.2, rel=1.3), t, 0.95, 0.0, 0.7)
    b.mix(bass(48), t, 0.9)
    b.mix(bass(36), t, 0.6)
    for k, m in enumerate((60, 72, 76, 79, 84)):
        b.mix(marimba(m), t + k * 0.09, 0.8, -0.3 + 0.15 * k, 0.5)
    b.mix(bell(84, 1.2), t, 0.9, 0.0, 0.8)
    for tt, m, p in ((43.9, 88, 0.3), (44.6, 91, -0.3), (45.4, 96, 0.0)):
        b.mix(bell(m, 1.0), tt, 0.55, p, 0.8)
    return b


def finish(b, wet):
    wl = reverb(b.S, 0)
    wr = reverb(b.S, 23)
    L = [a + wet * w for a, w in zip(b.L, wl)]
    R = [a + wet * w for a, w in zip(b.R, wr)]
    f0 = 45.3
    i0 = int(f0 * SR)
    for i in range(i0, N):
        x = (i - i0) / (N - i0)
        g = 0.5 + 0.5 * math.cos(math.pi * x)
        L[i] *= g
        R[i] *= g
    return L, R


def build_pops():
    b = Bus()
    runs = []
    cur = []
    for t in sorted(POPS):
        if cur and t - cur[-1] > 0.35:
            runs.append(cur)
            cur = []
        cur.append(t)
    if cur:
        runs.append(cur)
    for run in runs:
        n = len(run)
        for i, t in enumerate(run):
            p = i / (n - 1) if n > 1 else 0.0
            target = POP_LOW + (POP_HIGH - POP_LOW) * p
            best = min(
                (o * 12 + s for o in range(5, 9) for s in PENT),
                key=lambda m: abs(m - target)
            )
            b.mix(xylo(best), t, 0.9, -0.15 + 0.3 * ((i * 7) % 5) / 4)
    return b.L, b.R


def write_wav(path, L, R):
    peak = max(max(abs(v) for v in L), max(abs(v) for v in R), 1e-9)
    k = (10 ** (PEAK_DB / 20.0)) * 32767.0 / peak
    data = array('h', [0]) * (2 * N)
    data[0::2] = array('h', [int(round(v * k)) for v in L])
    data[1::2] = array('h', [int(round(v * k)) for v in R])
    if sys.byteorder == 'big':
        data.byteswap()
    w = wave.open(path, 'wb')
    w.setnchannels(2)
    w.setsampwidth(2)
    w.setframerate(SR)
    w.writeframes(data.tobytes())
    w.close()


def main():
    out_dir = sys.argv[1] if len(sys.argv) > 1 else os.path.join(os.path.dirname(os.path.abspath(__file__)), 'growth')
    os.makedirs(out_dir, exist_ok=True)
    L, R = build_pops()
    write_wav(os.path.join(out_dir, 'growth_pops.wav'), L, R)
    b = build_music()
    L, R = finish(b, 0.35)
    write_wav(os.path.join(out_dir, 'growth_music.wav'), L, R)
    print('ok', out_dir)


if __name__ == '__main__':
    main()
