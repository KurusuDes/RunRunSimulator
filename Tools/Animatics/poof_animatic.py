import os, sys, math, random
import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont, ImageChops
from scipy import ndimage as ndi

ROOT = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(ROOT, '..', '..'))
SRC = os.path.join(REPO, 'Recordings', 'promo', 'life_track')
OUT = os.path.join(REPO, 'Recordings', 'animatic')
FONT = os.path.join(REPO, 'Assets', 'Feel', 'MMTools', 'Demos', 'MMTween', 'Fonts', 'Lato', 'TTF', 'Lato-Heavy.ttf')
MONO = os.path.join(REPO, 'Assets', 'Feel', 'NiceVibrations', 'Demo', 'Common', 'Fonts', 'RobotoMono-Bold.ttf')

W, H = 1920, 1080
FPS = 30
GROUND = 915
SCALE = 0.85
CX = W // 2
INK = (38, 92, 96)
CLOUD = (252, 248, 240)
CLOUD_SHADE = (222, 214, 232)
SHADOW_MUL = (0.47, 0.44, 0.52)


def cut(frame, box):
    im = Image.open(os.path.join(SRC, 'f_%04d.jpg' % frame)).convert('RGB').crop(box)
    a = np.asarray(im).astype(int)
    r, g, b = a[..., 0], a[..., 1], a[..., 2]
    lum = (r + g + b) / 3
    core = ((b - r > -12) & (lum >= 125)) | ((lum < 125) & (g > r + 2)) | ((lum > 226) & (abs(r - b) < 14))
    core = ndi.binary_opening(core, iterations=2)
    core = ndi.binary_closing(core, iterations=4)
    core = ndi.binary_fill_holes(core)
    lab, n = ndi.label(core)
    sizes = ndi.sum(core, lab, range(1, n + 1))
    core = ndi.binary_fill_holes(lab == np.argmax(sizes) + 1)
    m = Image.fromarray((core * 255).astype(np.uint8)).filter(ImageFilter.GaussianBlur(1.2))
    im.putalpha(m)
    im = im.crop(m.getbbox())
    return im.resize((int(im.width * SCALE), int(im.height * SCALE)), Image.LANCZOS)


def background():
    im = Image.open(os.path.join(SRC, 'f_0050.jpg')).convert('RGB')
    col = np.asarray(im.crop((20, 0, 120, H))).astype(float).mean(axis=1)
    col = ndi.gaussian_filter1d(col, 6, axis=0)
    shift = GROUND - 1010
    col = np.roll(col, shift, axis=0)
    col[:max(shift, 0)] = col[max(shift, 0)]
    bg = np.repeat(col[:, None, :], W, axis=1)
    x = np.linspace(-1, 1, W)[None, :, None]
    y = np.linspace(-1, 1, H)[:, None, None]
    bg *= 1 - 0.10 * (x ** 2 + 0.6 * y ** 2)
    return Image.fromarray(np.clip(bg, 0, 255).astype(np.uint8))


def ease_out_back(t, s=1.7):
    t -= 1
    return t * t * ((s + 1) * t + s) + 1


def smooth(t):
    t = min(max(t, 0.0), 1.0)
    return t * t * (3 - 2 * t)


def clamp01(t):
    return min(max(t, 0.0), 1.0)


def spring(t, amp, freq=2.6, damp=5.5):
    if t < 0:
        return 0.0
    return amp * math.exp(-damp * t) * math.cos(2 * math.pi * freq * t)


class Pose:
    def __init__(self, sx=1.0, sy=1.0, rot=0.0, lift=0.0, dx=0.0, tint=0.0, glow=0.0, alpha=1.0):
        self.sx, self.sy, self.rot, self.lift, self.dx = sx, sy, rot, lift, dx
        self.tint, self.glow, self.alpha = tint, glow, alpha


def glow_of(sprite, radius):
    a = sprite.split()[3]
    pad = radius * 3
    big = Image.new('L', (a.width + pad * 2, a.height + pad * 2), 0)
    big.paste(a, (pad, pad))
    big = big.filter(ImageFilter.MaxFilter(9)).filter(ImageFilter.GaussianBlur(radius))
    return big, pad


def draw_shadow(frame, width, lift, strength=1.0):
    k = 1.0 / (1.0 + lift / 260.0)
    w = width * 0.62 * k
    h = width * 0.11 * k
    m = Image.new('L', (W, H), 0)
    ImageDraw.Draw(m).ellipse((CX - w - 40, GROUND - h - 6, CX + w - 40, GROUND + h - 6), fill=int(255 * strength * (0.55 + 0.45 * k)))
    m = m.filter(ImageFilter.GaussianBlur(18))
    a = np.asarray(frame).astype(float)
    mm = np.asarray(m).astype(float)[..., None] / 255.0
    mul = np.array(SHADOW_MUL)[None, None, :]
    a = a * (1 - mm) + a * mul * mm
    return Image.fromarray(np.clip(a, 0, 255).astype(np.uint8))


def place(frame, sprite, pose, glow_cache=None):
    if pose.alpha <= 0.001:
        return frame
    sw, sh = sprite.size
    nw, nh = max(1, int(sw * pose.sx)), max(1, int(sh * pose.sy))
    sp = sprite.resize((nw, nh), Image.LANCZOS)
    if pose.tint > 0:
        rgb = sp.convert('RGB')
        white = Image.new('RGB', sp.size, (255, 253, 245))
        rgb = Image.blend(rgb, white, min(pose.tint, 1.0))
        rgb.putalpha(sp.split()[3])
        sp = rgb
    side = int(math.hypot(nw, nh) * 2) + 40
    canvas = Image.new('RGBA', (side, side), (0, 0, 0, 0))
    ox, oy = side // 2 - nw // 2, side // 2 - nh
    if pose.glow > 0:
        g, pad = glow_of(sp, 22)
        gl = Image.new('RGBA', g.size, (205, 255, 248, 0))
        gl.putalpha(g.point(lambda v: int(min(255, v * pose.glow * 1.6))))
        canvas.alpha_composite(gl, (ox - pad, oy - pad))
    canvas.alpha_composite(sp, (ox, oy))
    if pose.rot:
        canvas = canvas.rotate(pose.rot, resample=Image.BICUBIC, center=(side / 2, side / 2))
    if pose.alpha < 1:
        canvas.putalpha(canvas.split()[3].point(lambda v: int(v * pose.alpha)))
    px = int(CX + pose.dx - side / 2)
    py = int(GROUND - pose.lift - side / 2)
    frame = frame.convert('RGBA')
    frame.alpha_composite(canvas, (px, py)) if px >= 0 and py >= 0 else frame.paste(canvas, (px, py), canvas)
    return frame.convert('RGB')


def shards_from(sprite, n, seed):
    rng = random.Random(seed)
    a = np.asarray(sprite.split()[3]) > 40
    ys, xs = np.nonzero(a)
    seeds = [(xs[i], ys[i]) for i in rng.sample(range(len(xs)), n)]
    yy, xx = np.mgrid[0:sprite.height, 0:sprite.width]
    d = np.stack([(xx - sx) ** 2 + (yy - sy) ** 2 for sx, sy in seeds])
    lab = np.argmin(d, axis=0)
    out = []
    for i in range(n):
        m = (lab == i) & a
        if m.sum() < 400:
            continue
        m = ndi.binary_erosion(m, iterations=2)
        edge = m & ~ndi.binary_erosion(m, iterations=3)
        pix = np.asarray(sprite).copy()
        pix[..., 3] = (m * 255).astype(np.uint8)
        pix[edge, :3] = INK
        im = Image.fromarray(pix, 'RGBA')
        bb = im.getbbox()
        if not bb:
            continue
        piece = im.crop(bb)
        cx = (bb[0] + bb[2]) / 2 - sprite.width / 2
        cy = sprite.height - (bb[1] + bb[3]) / 2
        ang = math.atan2(cy - sprite.height * 0.45, cx)
        sp = rng.uniform(900, 1500)
        out.append(dict(img=piece, x=cx, y=cy, vx=math.cos(ang) * sp * rng.uniform(0.7, 1.1),
                        vy=abs(math.sin(ang)) * sp * 0.6 + rng.uniform(500, 1000), spin=rng.uniform(-720, 720)))
    return out


def draw_shards(frame, shards, t):
    if t < 0:
        return frame
    frame = frame.convert('RGBA')
    for s in shards:
        x = CX + s['x'] + s['vx'] * t
        y = GROUND - (s['y'] + s['vy'] * t - 0.5 * 3200 * t * t)
        if y > GROUND + 60:
            continue
        k = 0.62 * (1 - clamp01((t - 0.55) / 0.35))
        if k <= 0.02:
            continue
        im = s['img'].resize((max(1, int(s['img'].width * k)), max(1, int(s['img'].height * k))), Image.LANCZOS)
        im = im.rotate(s['spin'] * t, resample=Image.BICUBIC, expand=True)
        frame.alpha_composite(im, (int(x - im.width / 2), int(y - im.height / 2))) if x - im.width / 2 >= 0 and y - im.height / 2 >= 0 else None
    return frame.convert('RGB')


def make_puffs(seed, n, spread, height):
    rng = random.Random(seed)
    puffs = []
    for i in range(n):
        ang = math.pi * (i / (n - 1)) if n > 1 else math.pi / 2
        ang += rng.uniform(-0.18, 0.18)
        puffs.append(dict(ang=ang, dist=spread * rng.uniform(0.55, 1.0), r=rng.uniform(95, 150),
                          delay=rng.uniform(0, 0.06), life=rng.uniform(0.55, 0.75), cy=height * rng.uniform(0.25, 0.7)))
    for i in range(5):
        puffs.append(dict(ang=rng.uniform(0.3, math.pi - 0.3), dist=spread * 0.25, r=rng.uniform(130, 175),
                          delay=0.0, life=rng.uniform(0.6, 0.8), cy=height * rng.uniform(0.35, 0.6)))
    return puffs


def draw_cloud(frame, puffs, t):
    if t < 0:
        return frame
    mask = Image.new('L', (W, H), 0)
    shade = Image.new('L', (W, H), 0)
    dm, ds = ImageDraw.Draw(mask), ImageDraw.Draw(shade)
    any_ = False
    for p in puffs:
        u = (t - p['delay']) / p['life']
        if u < 0 or u > 1:
            continue
        grow = ease_out_back(clamp01(u / 0.28), 2.2)
        shrink = 1 - smooth((u - 0.55) / 0.45)
        r = p['r'] * grow * shrink
        if r < 2:
            continue
        d = p['dist'] * (0.25 + 0.75 * (1 - (1 - clamp01(u * 1.4)) ** 3))
        x = CX + math.cos(p['ang']) * d
        y = GROUND - p['cy'] - math.sin(p['ang']) * d * 0.55 - 60 * u
        dm.ellipse((x - r, y - r, x + r, y + r), fill=255)
        ds.ellipse((x - r * 0.9 + r * 0.22, y - r * 0.9 + r * 0.28, x + r * 0.9 + r * 0.22, y + r * 0.9 + r * 0.28), fill=255)
        any_ = True
    if not any_:
        return frame
    outline = mask.filter(ImageFilter.MaxFilter(11))
    body = np.asarray(mask).astype(float)[..., None] / 255
    ring = np.asarray(outline).astype(float)[..., None] / 255
    sh = np.asarray(shade.filter(ImageFilter.GaussianBlur(10))).astype(float)[..., None] / 255
    inner = np.asarray(mask.filter(ImageFilter.MinFilter(9)).filter(ImageFilter.GaussianBlur(6))).astype(float)[..., None] / 255
    a = np.asarray(frame).astype(float)
    a = a * (1 - ring) + np.array(INK)[None, None, :] * ring
    fill = np.array(CLOUD)[None, None, :] * (1 - 0.0)
    shading = 1 - inner * sh
    col = np.array(CLOUD)[None, None, :] * (1 - shading * 0.55) + np.array(CLOUD_SHADE)[None, None, :] * (shading * 0.55)
    col = col * (1 - body) + col * body
    a = a * (1 - body) + col * body
    return Image.fromarray(np.clip(a, 0, 255).astype(np.uint8))


def draw_flash(frame, t, cy, size=1.0):
    if t < 0 or t > 0.2:
        return frame
    u = t / 0.2
    a = np.asarray(frame).astype(float)
    yy, xx = np.mgrid[0:H, 0:W]
    d = np.hypot(xx - CX, (yy - (GROUND - cy)) * 1.15)
    rad = (260 + 520 * u) * size
    core = np.clip(1 - d / rad, 0, 1) ** 1.6 * (1 - u) ** 0.7
    ang = np.arctan2(yy - (GROUND - cy), xx - CX)
    rays = (np.cos(ang * 8 + u * 1.2) * 0.5 + 0.5) ** 14
    rays *= np.clip(1 - d / (rad * 1.9), 0, 1) * (1 - u)
    k = np.clip(core + rays * 0.85, 0, 1)[..., None]
    a = a * (1 - k) + np.array([255, 252, 236])[None, None, :] * k
    a += 28 * (1 - u) ** 3
    return Image.fromarray(np.clip(a, 0, 255).astype(np.uint8))


def sparkle(d, x, y, r, col):
    pts = []
    for i in range(8):
        ang = i * math.pi / 4
        rr = r if i % 2 == 0 else r * 0.28
        pts.append((x + math.cos(ang) * rr, y + math.sin(ang) * rr))
    d.polygon(pts, fill=col)


def draw_sparkles(frame, sparks, t):
    frame = frame.convert('RGBA')
    layer = Image.new('RGBA', (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)
    for s in sparks:
        u = (t - s['t0']) / s['life']
        if u < 0 or u > 1:
            continue
        r = s['r'] * math.sin(math.pi * u)
        x = CX + s['x'] + s['vx'] * u
        y = GROUND - s['y'] - s['vy'] * u
        sparkle(d, x, y, r + 3, INK + (255,))
        sparkle(d, x, y, r, s['col'] + (255,))
    frame.alpha_composite(layer)
    return frame.convert('RGB')


PHASES_HATCH = [(0, 12, 'reposo'), (12, 36, 'sacudida x3'), (36, 42, 'anticipa'), (42, 50, 'destello + nube'),
                (50, 66, 'sale con salto'), (66, 86, 'rebote'), (86, 98, 'saltito'), (98, 112, 'pausa')]
PHASES_EVO = [(0, 12, 'reposo'), (12, 46, 'brillo de rim'), (46, 52, 'anticipa'), (52, 60, 'destello + nube'),
              (60, 72, 'sale con salto'), (72, 96, 'rebote'), (96, 118, 'pausa')]


def timeline(frame, phases, f, total, title):
    d = ImageDraw.Draw(frame, 'RGBA')
    ft = ImageFont.truetype(FONT, 26)
    fm = ImageFont.truetype(MONO, 22)
    fh = ImageFont.truetype(FONT, 40)
    d.text((48, 36), title, font=fh, fill=(52, 30, 22, 255))
    cur = next((n for a, b, n in phases if a <= f < b), '')
    d.text((48, 88), cur, font=ImageFont.truetype(FONT, 30), fill=(194, 68, 40, 255))
    x0, x1, y0, y1 = 48, W - 48, H - 50, H - 26
    d.rectangle((x0, y0, x1, y1), fill=(52, 30, 22, 120))
    span = x1 - x0
    for i, (a, b, name) in enumerate(phases):
        xa, xb = x0 + span * a / total, x0 + span * b / total
        on = a <= f < b
        d.rectangle((xa + 1, y0 + 1, xb - 1, y1 - 1), fill=(245, 185, 72, 235) if on else (244, 227, 206, 150 if i % 2 else 110))
        tw = d.textlength(name, font=ft)
        if tw < xb - xa - 8:
            d.text(((xa + xb - tw) / 2, y0 - 34), name, font=ft, fill=(52, 30, 22, 255 if on else 150))
    px = x0 + span * (f + 0.5) / total
    d.rectangle((px - 2, y0 - 6, px + 2, y1 + 6), fill=(194, 68, 40, 255))
    lab = 'f %03d  ·  %.2f s' % (f, f / FPS)
    d.text((W - 48 - d.textlength(lab, font=fm), 44), lab, font=fm, fill=(52, 30, 22, 220))
    return frame


def hatch_pose(f):
    t = f / FPS
    p = Pose()
    p.sy = 1 + 0.012 * math.sin(t * 5)
    if 12 <= f < 36:
        k = (f - 12) // 8
        u = ((f - 12) % 8) / 8
        amp = [4.5, 8.0, 12.0][k]
        p.rot = amp * math.sin(u * 2 * math.pi)
        if k == 2:
            p.lift = 26 * math.sin(u * math.pi)
            p.sy = 1 + 0.06 * math.sin(u * math.pi)
            p.sx = 1 - 0.03 * math.sin(u * math.pi)
        p.dx = 3 * math.sin(f * 2.9)
    elif 36 <= f < 43:
        u = smooth((f - 36) / 6)
        p.sy, p.sx = 1 - 0.14 * u, 1 + 0.09 * u
        p.dx = 5 * math.sin(f * 4.1) * u
        p.tint = 0.35 * u
    if f >= 43:
        p.alpha = 0
    return p


def pop_pose(f, start, peak_lift, land_f):
    p = Pose()
    if f < start:
        p.alpha = 0
        return p
    if f < land_f:
        u = (f - start) / (land_f - start)
        p.lift = peak_lift * 4 * u * (1 - u)
        k = 1 - u
        p.sy = 0.8 + 0.5 * k if u < 0.5 else 1.0 + 0.14 * (1 - abs(u - 0.5) * 2)
        p.sx = 1 / math.sqrt(p.sy)
        grow = ease_out_back(clamp01((f - start) / 5), 2.0)
        p.sx *= 0.55 + 0.45 * grow
        p.sy *= 0.55 + 0.45 * grow
        p.tint = 0.6 * (1 - clamp01((f - start) / 6))
        return p
    s = spring((f - land_f) / FPS, 0.24)
    p.sy = 1 - s
    p.sx = 1 + s * 0.8
    return p


def evo_blob_pose(f):
    t = f / FPS
    p = Pose()
    p.sy = 1 + 0.015 * math.sin(t * 5)
    if 12 <= f < 46:
        u = (f - 12) / 34
        freq = 2 + 10 * u * u
        pulse = 0.5 + 0.5 * math.sin(2 * math.pi * freq * t)
        p.glow = (0.25 + 0.75 * u) * (0.55 + 0.45 * pulse)
        p.tint = 0.28 * u * u + 0.08 * pulse * u
        p.dx = 4 * u * u * math.sin(f * 3.3)
        p.sy *= 1 + 0.03 * u * math.sin(2 * math.pi * freq * t)
    elif 46 <= f < 53:
        u = smooth((f - 46) / 6)
        p.sy, p.sx = 1 - 0.16 * u, 1 + 0.1 * u
        p.glow, p.tint = 1.0, 0.35 + 0.5 * u
        p.dx = 6 * math.sin(f * 4.1)
    if f >= 53:
        p.alpha = 0
    return p


def render(name, total, phases, title, frames_fn):
    d = os.path.join(OUT, name)
    os.makedirs(d, exist_ok=True)
    for f in range(total):
        im = frames_fn(f)
        im = timeline(im, phases, f, total, title)
        im.save(os.path.join(d, 'f_%04d.jpg' % f), quality=93)
    return d


def main():
    os.makedirs(OUT, exist_ok=True)
    bg = background()
    egg = cut(50, (250, 440, 680, 1030))
    blob = cut(50, (800, 460, 1538, 1060))
    adult = cut(95, (590, 50, 1520, 1078))
    shards = shards_from(egg, 16, 7)
    puffs_h = make_puffs(3, 9, 300, egg.height * 0.55)
    zoom = 0.78
    blob_e = blob.resize((int(blob.width * zoom), int(blob.height * zoom)), Image.LANCZOS)
    adult = adult.resize((int(adult.width * zoom), int(adult.height * zoom)), Image.LANCZOS)
    puffs_e = make_puffs(11, 11, 340, adult.height * 0.5)
    rng = random.Random(5)
    sparks_h = [dict(t0=1.45 + rng.uniform(0, 0.25), life=rng.uniform(0.35, 0.6), r=rng.uniform(14, 26),
                     x=rng.uniform(-330, 330), y=rng.uniform(150, 520), vx=rng.uniform(-60, 60), vy=rng.uniform(40, 140),
                     col=rng.choice([(245, 185, 72), (255, 252, 236), (205, 255, 248)])) for _ in range(14)]
    sparks_e = [dict(t0=0.5 + rng.uniform(0, 1.0), life=rng.uniform(0.4, 0.7), r=rng.uniform(9, 18),
                     x=rng.uniform(-360, 360), y=rng.uniform(60, 420), vx=0, vy=rng.uniform(80, 200),
                     col=rng.choice([(255, 252, 236), (205, 255, 248)])) for _ in range(26)]
    sparks_e += [dict(t0=1.75 + rng.uniform(0, 0.3), life=rng.uniform(0.4, 0.7), r=rng.uniform(16, 30),
                      x=rng.uniform(-460, 460), y=rng.uniform(150, 800), vx=rng.uniform(-80, 80), vy=rng.uniform(40, 160),
                      col=rng.choice([(245, 185, 72), (255, 252, 236), (205, 255, 248)])) for _ in range(20)]

    def hatch(f):
        t = f / FPS
        p = hatch_pose(f)
        q = pop_pose(f, 50, 230, 64)
        if f >= 86:
            u = (f - 86) / 12
            if u < 1:
                q.lift = 70 * 4 * u * (1 - u)
                q.sy = 1 + 0.08 * math.sin(u * math.pi)
                q.sx = 1 / math.sqrt(q.sy)
            else:
                s = spring((f - 98) / FPS, 0.12)
                q.sy, q.sx = 1 - s, 1 + s * 0.8
        im = bg.copy()
        if p.alpha > 0:
            im = draw_shadow(im, egg.width * p.sx, p.lift)
            im = place(im, egg, p)
        if q.alpha > 0:
            im = draw_shadow(im, blob.width * q.sx, q.lift)
            im = place(im, blob, q)
        im = draw_cloud(im, puffs_h, t - 42 / FPS)
        im = draw_shards(im, shards, t - 42 / FPS)
        im = draw_flash(im, t - 42 / FPS, egg.height * 0.5)
        im = draw_sparkles(im, sparks_h, t)
        return im

    def evolve(f):
        t = f / FPS
        p = evo_blob_pose(f)
        q = pop_pose(f, 60, 60, 72)
        if f >= 60:
            q.glow = 1.0 - clamp01((f - 60) / 26)
        im = bg.copy()
        if p.alpha > 0:
            im = draw_shadow(im, blob_e.width * p.sx, p.lift)
            im = place(im, blob_e, p)
        if q.alpha > 0:
            im = draw_shadow(im, adult.width * q.sx, q.lift)
            im = place(im, adult, q)
        im = draw_sparkles(im, [s for s in sparks_e if s['t0'] < 1.6], t)
        im = draw_cloud(im, puffs_e, t - 52 / FPS)
        im = draw_flash(im, t - 52 / FPS, blob_e.height * 0.7, 1.25)
        im = draw_sparkles(im, [s for s in sparks_e if s['t0'] >= 1.6], t)
        return im

    which = sys.argv[1] if len(sys.argv) > 1 else 'both'
    if which in ('both', 'hatch'):
        render('hatch', 112, PHASES_HATCH, 'Eclosión · huevo → blobim', hatch)
    if which in ('both', 'evolve'):
        render('evolve', 118, PHASES_EVO, 'Evolución · blobim → adulto', evolve)


if __name__ == '__main__':
    main()
