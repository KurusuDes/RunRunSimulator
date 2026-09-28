import os
import sys
import math
import bpy
import numpy as np

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(__file__)), "parts"))
import part_common as pc

ARGS = pc.args()
WORK, OUT = ARGS[0], ARGS[1]
ONLY = set(ARGS[2].split(",")) if len(ARGS) > 2 and ARGS[2] else None
BASE = os.path.join(pc.ROOT, "Assets", "RunRunSimulator", "Resources", "Textures", "MoriMochi", "Patterns", "MonchiPattern_00.png")

pos = np.load(os.path.join(WORK, "pos.npy"))
nor = np.load(os.path.join(WORK, "nor.npy"))
RES = pos.shape[0]
valid = ~np.isnan(pos[..., 0])
P = pos[valid].astype(np.float64)
N = nor[valid].astype(np.float64)
LO, HI = P.min(0), P.max(0)
Q = (P - LO) / (HI - LO)
X, Y, Z = P[:, 0], P[:, 1], P[:, 2]
NZ = N[:, 2]


def smooth(a, b, x):
    t = np.clip((x - a) / (b - a), 0, 1)
    return t * t * (3 - 2 * t)


def lattice(seed):
    rng = np.random.default_rng(seed)
    return rng.random(64 ** 3).reshape(64, 64, 64)


def vnoise(p, freq, seed):
    g = lattice(seed)
    s = p * freq
    i = np.floor(s).astype(np.int64)
    f = s - i
    u = f * f * (3 - 2 * f)
    out = 0.0
    for dx in (0, 1):
        for dy in (0, 1):
            for dz in (0, 1):
                w = (u[:, 0] if dx else 1 - u[:, 0]) * (u[:, 1] if dy else 1 - u[:, 1]) * (u[:, 2] if dz else 1 - u[:, 2])
                out = out + w * g[(i[:, 0] + dx) % 64, (i[:, 1] + dy) % 64, (i[:, 2] + dz) % 64]
    return out


def fbm(p, freq, seed, octaves=4):
    total, amp, norm = 0.0, 1.0, 0.0
    for o in range(octaves):
        total = total + amp * vnoise(p, freq * 2 ** o, seed + o)
        norm += amp
        amp *= 0.5
    return total / norm


def centers(count, seed, where=None):
    rng = np.random.default_rng(seed)
    pool = np.arange(len(P)) if where is None else np.nonzero(where)[0]
    pick = [pool[rng.integers(len(pool))]]
    tries = 0
    min_d = 0.9 / math.sqrt(count)
    while len(pick) < count and tries < count * 60:
        tries += 1
        c = pool[rng.integers(len(pool))]
        if np.min(np.linalg.norm(P[pick] - P[c], axis=1)) > min_d:
            pick.append(c)
    return P[pick], N[pick]


def nearest(cs):
    d1 = np.full(len(P), np.inf)
    d2 = np.full(len(P), np.inf)
    idx = np.zeros(len(P), dtype=np.int64)
    for k, c in enumerate(cs):
        d = np.linalg.norm(P - c, axis=1)
        closer = d < d1
        d2 = np.where(closer, d1, np.minimum(d2, d))
        idx = np.where(closer, k, idx)
        d1 = np.where(closer, d, d1)
    return d1, d2, idx


def disc(d, r, soft=0.006):
    return 1 - smooth(r - soft, r + soft, d)


def spots(count, r_lo, r_hi, seed, where=None, warp=0.0):
    cs, _ = centers(count, seed, where)
    rng = np.random.default_rng(seed + 1)
    radii = rng.uniform(r_lo, r_hi, len(cs))
    q = P + (warp * (np.stack([vnoise(P, 9, seed + 7), vnoise(P, 9, seed + 8), vnoise(P, 9, seed + 9)], 1) - 0.5) if warp else 0)
    m = np.zeros(len(P))
    for c, r in zip(cs, radii):
        m = np.maximum(m, disc(np.linalg.norm(q - c, axis=1), r))
    return m


def tangent_polar(c, n):
    n = n / np.linalg.norm(n)
    t = np.cross(n, [0, 0, 1.0])
    if np.linalg.norm(t) < 1e-3:
        t = np.cross(n, [1.0, 0, 0])
    t /= np.linalg.norm(t)
    b = np.cross(n, t)
    v = P - c
    x, y = v @ t, v @ b
    return np.hypot(x, y), np.arctan2(y, x), np.abs(v @ n)


def shapes(count, r, seed, kind, where=None):
    cs, ns = centers(count, seed, where)
    rng = np.random.default_rng(seed + 3)
    m = np.zeros(len(P))
    for c, n in zip(cs, ns):
        rad, ang, depth = tangent_polar(c, n)
        ang = ang + rng.uniform(0, 2 * math.pi)
        if kind == "star":
            k = 0.5 + 0.5 * np.cos(5 * ang)
            edge = r * (0.5 + 0.5 * k ** 1.6)
        else:
            a = np.mod(ang, 2 * math.pi) - math.pi
            edge = r * (0.75 + 0.35 * np.abs(np.sin(a)) - 0.25 * np.cos(a)) * (1 - 0.35 * np.exp(-((np.abs(a) - math.pi) ** 2) / 0.08))
        m = np.maximum(m, (1 - smooth(edge - 0.005, edge + 0.005, rad)) * (depth < r * 1.5))
    return m


def dorsal(lo=0.1, hi=0.6):
    return smooth(lo, hi, NZ)


def belly():
    return smooth(-0.2, -0.6, NZ)


def stripes(freq, width, seed, axis=1, warp=0.08, sharp=0.08):
    w = warp * (fbm(P, 3, seed) - 0.5) * 2
    s = np.sin((P[:, axis] + w) * freq * 2 * math.pi)
    return smooth(1 - width - sharp, 1 - width + sharp, s)


def voronoi_edges(count, seed, width, where=None):
    cs, _ = centers(count, seed, where)
    d1, d2, _ = nearest(cs)
    return 1 - smooth(width * 0.5, width, d2 - d1)


def extremities():
    feet = smooth(0.2, 0.08, Z)
    tail = smooth(0.55, 0.85, Q[:, 1]) * smooth(0.55, 0.3, Q[:, 2])
    return np.maximum(feet, tail)


R = {}


def recipe(name, strength=0.55, light=0.0):
    def deco(fn):
        R[name] = (fn, strength, light)
        return fn
    return deco


@recipe("Lunares", 0.4)
def _():
    return spots(38, 0.045, 0.07, 11)


@recipe("Pecas", 0.36)
def _():
    return spots(260, 0.008, 0.014, 12, where=(NZ > -0.1))


@recipe("Dalmata", 0.38)
def _():
    return spots(70, 0.02, 0.05, 13, warp=0.05)


@recipe("Vaca", 0.46)
def _():
    return smooth(0.56, 0.6, fbm(P, 2.2, 14))


@recipe("Jirafa", 0.17)
def _():
    return 1 - voronoi_edges(55, 15, 0.035)


@recipe("Tigre", 0.19)
def _():
    return stripes(5.0, 0.35, 16) * (1 - belly())


@recipe("Cebra", 0.18)
def _():
    return stripes(9.0, 0.45, 17, warp=0.12)


@recipe("LomoOscuro", 0.36)
def _():
    return dorsal(0.05, 0.75) * smooth(0.25, 0.7, Q[:, 2])


@recipe("Bicolor", 0.26)
def _():
    line = 0.6 + 0.05 * (fbm(P, 4, 18) - 0.5)
    return smooth(line - 0.02, line + 0.02, Q[:, 2]) * (1 - belly())


@recipe("PuntasOscuras", 0.39)
def _():
    return extremities()


@recipe("Estrellas", 0.44)
def _():
    return shapes(22, 0.07, 19, "star")


@recipe("Corazones", 0.4)
def _():
    return shapes(18, 0.075, 20, "heart")


@recipe("Lava", 0.25, 0.4)
def _():
    edges = voronoi_edges(90, 21, 0.03)
    return 1 - 0.0 * edges, edges


@recipe("Rosetas", 0.28)
def _():
    cs, _ = centers(55, 22)
    rng = np.random.default_rng(23)
    q = P + 0.03 * (np.stack([vnoise(P, 14, 24), vnoise(P, 14, 25), vnoise(P, 14, 26)], 1) - 0.5)
    m = np.zeros(len(P))
    for c in cs:
        r = rng.uniform(0.035, 0.05)
        d = np.linalg.norm(q - c, axis=1)
        m = np.maximum(m, disc(d, r) - disc(d, r * 0.55))
    return m


@recipe("Salpicado", 0.44)
def _():
    big = spots(14, 0.04, 0.07, 27, warp=0.08)
    drops = spots(120, 0.006, 0.014, 28)
    return np.maximum(big, drops)


@recipe("RayasLomo", 0.32)
def _():
    band = np.abs(X)
    m = np.zeros(len(P))
    for off in (0.0, 0.12):
        m = np.maximum(m, 1 - smooth(0.02, 0.035, np.abs(band - off)))
    return m * dorsal(0.2, 0.6)


@recipe("ColaOscura", 0.39)
def _():
    return smooth(0.35, 0.95, Q[:, 1])


@recipe("Escamas", 0.12)
def _():
    return voronoi_edges(900, 29, 0.012) * (1 - belly())


@recipe("Nubes", 0.26, 0.33)
def _():
    n = fbm(P, 3.0, 30, 5)
    return smooth(0.55, 0.7, n), smooth(0.45, 0.3, n) * 0.6


@recipe("Mascara", 0.39)
def _():
    face = (Y < -0.45) & (Z > 0.45)
    eye = np.exp(-(((np.abs(X) - 0.28) / 0.13) ** 2 + ((Z - 0.8) / 0.12) ** 2))
    return smooth(0.35, 0.55, eye) * face


def load_base():
    img = bpy.data.images.load(BASE)
    a = np.empty(len(img.pixels), dtype=np.float32)
    img.pixels.foreach_get(a)
    return a.reshape(img.size[1], img.size[0], 4)[::-1].copy()


def save(arr, path):
    img = bpy.data.images.new(os.path.basename(path), arr.shape[1], arr.shape[0], alpha=True)
    img.pixels.foreach_set(arr[::-1].astype(np.float32).ravel())
    img.filepath_raw = path
    img.file_format = "PNG"
    img.save()
    bpy.data.images.remove(img)


base = load_base()
os.makedirs(OUT, exist_ok=True)
for k, (name, (fn, strength, light)) in enumerate(R.items()):
    if ONLY and name not in ONLY:
        continue
    res = fn()
    m, l = (res if isinstance(res, tuple) else (res, np.zeros(len(P))))
    out = base.copy()
    rgb = out[valid][:, :3]
    rgb = rgb * (1 - strength * m[:, None])
    rgb = rgb + (1 - rgb) * (light * l)[:, None]
    blk = out[valid]
    blk[:, :3] = rgb
    out[valid] = blk
    save(out, os.path.join(OUT, "Pattern_%02d_%s.png" % (k, name)))
    print("PATTERN_DONE", k, name, round(float(m.mean()), 3))
