import os, sys, math, random
from PIL import Image, ImageDraw, ImageFont, ImageFilter
import brawl_sim as b

REPO = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
OUT = os.path.join(REPO, 'Recordings', 'brawl')
FONTS = os.path.join(REPO, 'Assets', 'Feel')
F_TEXT = os.path.join(FONTS, 'MMTools', 'Demos', 'MMTween', 'Fonts', 'Lato', 'TTF', 'Lato-Heavy.ttf')
F_BLACK = os.path.join(FONTS, 'MMTools', 'Demos', 'MMTween', 'Fonts', 'Lato', 'TTF', 'Lato-Black.ttf')
F_DISPLAY = os.path.join(FONTS, 'NiceVibrations', 'Demo', 'Common', 'Fonts', 'BIG JOHN.otf')
F_MONO = os.path.join(FONTS, 'NiceVibrations', 'Demo', 'Common', 'Fonts', 'RobotoMono-Bold.ttf')

SS = 2
OW, OH = 1280, 720
W, H = OW * SS, OH * SS
PX = 60 * SS / 2
MX = (W - b.ARENA_W * PX) / 2
MY = 74 * SS
INK = (52, 30, 22)
CREAM = (244, 227, 206)
GOLD = (245, 185, 72)
CORAL = (194, 68, 40)
ALLY = (110, 160, 235)
FOE = (235, 110, 100)
TEAM = {0: ALLY, 1: FOE}
TEAM_NAME = {0: 'AZUL', 1: 'ROJO'}
FLOOR_A = (196, 214, 150)
FLOOR_B = (186, 206, 140)
ROCK = (178, 160, 140)
ROCK_TOP = (204, 188, 168)
GAS = (128, 84, 176)

_fonts = {}


def font(path, size):
    k = (path, size)
    if k not in _fonts:
        _fonts[k] = ImageFont.truetype(path, size)
    return _fonts[k]


def P(p):
    return (MX + p[0] * PX, MY + p[1] * PX)


def ease_out_back(t, s=1.70158):
    t -= 1
    return t * t * ((s + 1) * t + s) + 1


def text_c(d, xy, s, f, fill, stroke=0, sfill=INK, anchor='mm'):
    d.text(xy, s, font=f, fill=fill, stroke_width=stroke, stroke_fill=sfill, anchor=anchor)


def build_floor(world):
    im = Image.new('RGB', (W, H), (232, 214, 186))
    d = ImageDraw.Draw(im)
    for yy in range(0, H, 48):
        d.line((0, yy, W, yy), fill=(226, 206, 176), width=2)
    x0, y0 = P((0, 0))
    x1, y1 = P((b.ARENA_W, b.ARENA_H))
    d.rounded_rectangle((x0 - 14, y0 - 14, x1 + 14, y1 + 14), radius=34, fill=INK)
    d.rounded_rectangle((x0, y0, x1, y1), radius=24, fill=FLOOR_A)
    tile = PX * 2
    for i in range(int(b.ARENA_W / 2)):
        for j in range(int(b.ARENA_H / 2)):
            if (i + j) % 2 == 0:
                d.rectangle((x0 + i * tile, y0 + j * tile, x0 + (i + 1) * tile, y0 + (j + 1) * tile), fill=FLOOR_B)
    mask = Image.new('L', (W, H), 0)
    ImageDraw.Draw(mask).rounded_rectangle((x0, y0, x1, y1), radius=24, fill=255)
    base = Image.new('RGB', (W, H), (232, 214, 186))
    bd = ImageDraw.Draw(base)
    for yy in range(0, H, 48):
        bd.line((0, yy, W, yy), fill=(226, 206, 176), width=2)
    bd.rounded_rectangle((x0 - 14, y0 - 14, x1 + 14, y1 + 14), radius=34, fill=INK)
    base.paste(im, (0, 0), mask)
    d = ImageDraw.Draw(base)
    shadow = Image.new('L', (W, H), 0)
    sd = ImageDraw.Draw(shadow)
    for x, y, r in world.rocks:
        cx, cy = P((x, y))
        rr = r * PX
        sd.ellipse((cx - rr + 10, cy - rr + 22, cx + rr + 10, cy + rr + 22), fill=110)
    shadow = shadow.filter(ImageFilter.GaussianBlur(10))
    dark = Image.new('RGB', (W, H), (90, 100, 70))
    base = Image.composite(dark, base, shadow)
    d = ImageDraw.Draw(base)
    for x, y, r in world.rocks:
        cx, cy = P((x, y))
        rr = r * PX
        d.ellipse((cx - rr - 6, cy - rr - 6, cx + rr + 6, cy + rr + 6), fill=INK)
        d.ellipse((cx - rr, cy - rr, cx + rr, cy + rr), fill=ROCK)
        d.ellipse((cx - rr * 0.82, cy - rr * 0.9, cx + rr * 0.62, cy + rr * 0.45), fill=ROCK_TOP)
        d.ellipse((cx - rr * 0.5, cy - rr * 0.62, cx - rr * 0.1, cy - rr * 0.3), fill=(226, 214, 198))
    return base


class Fx:
    def __init__(self):
        self.items = []
        self.banner = None
        self.shake = 0.0

    def add(self, **kw):
        self.items.append(kw)


def ingest(fx, world, ev, t):
    e = ev
    u = world.units
    k = e['ev']
    if k == 'hit':
        if e['tag'] in ('bleed', 'gas'):
            fx.add(type='tick', pos=e['pos'], t0=t, life=0.25, uid=e['dst'])
            return
        big = e['tag'] == 'super'
        fx.add(type='num', pos=e['pos'], t0=t, life=0.9, text=str(e['dmg']), color=GOLD if big else (255, 255, 255),
               size=40 if big else 32, jitter=random.uniform(-0.4, 0.4))
        fx.add(type='flash', uid=e['dst'], t0=t, life=0.08)
        fx.add(type='spark', pos=e['pos'], t0=t, life=0.22, team=u[e['src']].team if e['src'] >= 0 else 1)
        fx.shake = max(fx.shake, 4 if big else 2)
    elif k == 'heal':
        fx.add(type='num', pos=e['pos'], t0=t, life=0.9, text='+' + str(e['amt']), color=(140, 230, 120), size=30, jitter=0)
    elif k == 'ko':
        fx.add(type='ko', pos=e['pos'], t0=t, life=0.9, team=u[e['dst']].team)
        fx.shake = 10
        fx.add(type='feed', t0=t, life=3.0, src=e['src'], dst=e['dst'])
    elif k == 'swing':
        fx.add(type='swing', uid=e['src'], t0=t, life=0.16, dir=e['dir'], range=e['range'], arc=e['arc'])
    elif k == 'whip':
        fx.add(type='whip', a=e['a'], b=e['b'], t0=t, life=0.18, team=u[e['src']].team)
    elif k == 'super':
        fx.banner = dict(t0=t, life=1.3, text=e['name'].upper(), team=u[e['src']].team, who=u[e['src']].name)
        fx.add(type='ring', pos=e['pos'], t0=t, life=0.45, color=GOLD, r=3.0)
    elif k == 'gadget':
        fx.add(type='label', uid=e['src'], t0=t, life=0.9, text=e['name'])
        fx.add(type='ring', pos=e['pos'], t0=t, life=0.3, color=(255, 255, 255), r=1.6)
    elif k == 'boom':
        fx.add(type='ring', pos=e['pos'], t0=t, life=0.4, color=(255, 210, 230), r=e['radius'] + 0.6)
        fx.shake = max(fx.shake, 6)
    elif k == 'pop':
        fx.add(type='pop', pos=e['pos'], t0=t, life=0.15, kind=e['kind'])
    elif k == 'stand':
        fx.banner = dict(t0=t, life=1.6, text='¡ÚLTIMO EN PIE!', team=u[e['src']].team, who=u[e['src']].name)
    elif k == 'land':
        fx.add(type='ring', pos=e['pos'], t0=t, life=0.3, color=(255, 255, 255), r=1.4)


def draw_gas(layer, world):
    r = world.gas_r()
    if r >= b.GAS_R0 - 0.01:
        return
    m = Image.new('L', (W, H), 0)
    md = ImageDraw.Draw(m)
    x0, y0 = P((0, 0))
    x1, y1 = P((b.ARENA_W, b.ARENA_H))
    md.rounded_rectangle((x0, y0, x1, y1), radius=24, fill=118)
    cx, cy = P((b.ARENA_W / 2, b.ARENA_H / 2))
    rr = r * PX
    md.ellipse((cx - rr, cy - rr, cx + rr, cy + rr), fill=0)
    g = Image.new('RGBA', (W, H), GAS + (0,))
    g.putalpha(m)
    layer.alpha_composite(g)
    d = ImageDraw.Draw(layer)
    d.ellipse((cx - rr, cy - rr, cx + rr, cy + rr), outline=(196, 150, 240, 255), width=6)
    t = world.t
    for i in range(36):
        a = i / 36 * 6.283 + t * 0.3
        k = (math.sin(t * 2 + i * 1.7) + 1) / 2
        px, py = cx + math.cos(a) * (rr + 18 + k * 30), cy + math.sin(a) * (rr + 18 + k * 30)
        if x0 < px < x1 and y0 < py < y1:
            s = 6 + k * 8
            d.ellipse((px - s, py - s, px + s, py + s), fill=(196, 150, 240, 170))


def draw_telegraph(d, world, u):
    w = u.windup
    if not w:
        return
    k = 1 - w['left'] / w['total']
    c = TEAM[u.team]
    cx, cy = P(u.pos)
    if w['what'] == 'super':
        r = (1.0 + 0.6 * k) * PX
        d.ellipse((cx - r, cy - r, cx + r, cy + r), outline=GOLD + (230,), width=8)
        return
    a = b.ATTACKS[u.horn]
    dr = w['dir']
    ang = math.degrees(math.atan2(dr[1], dr[0]))
    if a['kind'] == 'cone':
        R = a['range'] * PX
        box = (cx - R, cy - R, cx + R, cy + R)
        d.pieslice(box, ang - a['arc'] / 2, ang + a['arc'] / 2, fill=c + (45,))
        Rk = R * k
        d.pieslice((cx - Rk, cy - Rk, cx + Rk, cy + Rk), ang - a['arc'] / 2, ang + a['arc'] / 2, fill=c + (110,))
        d.arc(box, ang - a['arc'] / 2, ang + a['arc'] / 2, fill=c + (230,), width=5)
    else:
        L = a['range'] * PX
        wdt = (a.get('width', 0.9) if a['kind'] != 'spray' else 1.2) * PX / 2
        if a['kind'] == 'dash':
            wdt = b.UNIT_R * PX
        if a['kind'] == 'proj':
            wdt = 0.45 * PX
        nx, ny = -dr[1], dr[0]

        def quad(l):
            return [(cx + nx * wdt, cy + ny * wdt), (cx + dr[0] * l + nx * wdt, cy + dr[1] * l + ny * wdt),
                    (cx + dr[0] * l - nx * wdt, cy + dr[1] * l - ny * wdt), (cx - nx * wdt, cy - ny * wdt)]
        d.polygon(quad(L), fill=c + (45,))
        d.polygon(quad(L * k), fill=c + (110,))
        d.line(quad(L) + [quad(L)[0]], fill=c + (230,), width=4)


def draw_unit(d, world, u, fx, t):
    if not u.alive:
        return
    x, y = P(u.pos)
    lift = 0
    if t < u.air_until:
        k = (t - u.air_t0) / (u.air_until - u.air_t0)
        lift = math.sin(k * math.pi) * 1.4 * PX
    R = b.UNIT_R * PX * 1.45
    d.ellipse((x - R * 1.05, y + R * 0.55, x + R * 1.05, y + R * 1.05), fill=(60, 70, 40, 90))
    d.ellipse((x - R * 1.3, y - R * 0.35 + R * 0.6, x + R * 1.3, y + R * 0.55 + R * 0.6), outline=TEAM[u.team] + (255,), width=7)
    y -= lift
    sq = 1.0
    for f in fx.items:
        if f['type'] == 'flash' and f['uid'] == u.uid:
            sq = 1.12
    rx, ry = R * sq, R / sq
    if u.dash:
        dx, dy = u.dash['dir']
        for i in range(1, 4):
            gx, gy = x - dx * i * R * 0.7, y - dy * i * R * 0.7
            d.ellipse((gx - rx, gy - ry, gx + rx, gy + ry), fill=u.fur + (70 - i * 18,))
    if t < getattr(u, 'stand_until', -1) or (t < u.shield_until and u.back == 'PuasDobles'):
        rr = R * 1.55
        d.ellipse((x - rr, y - rr, x + rr, y + rr), fill=(255, 235, 170, 70), outline=GOLD + (255,), width=5)
    d.ellipse((x - rx - 6, y - ry - 6, x + rx + 6, y + ry + 6), fill=INK + (255,))
    flash = any(f['type'] == 'flash' and f['uid'] == u.uid for f in fx.items)
    body = tuple(int(c + (255 - c) * 0.6) for c in u.fur) if flash else u.fur
    d.ellipse((x - rx, y - ry, x + rx, y + ry), fill=body + (255,))
    d.ellipse((x - rx * 0.7, y - ry * 0.85, x + rx * 0.2, y - ry * 0.1), fill=tuple(min(255, c + 30) for c in body) + (255,))
    fdx, fdy = u.facing
    hx, hy = x + fdx * R * 0.55, y - R * 0.95 + fdy * R * 0.25
    horn = [(hx - R * 0.28, hy + R * 0.12), (hx + fdx * R * 0.25, hy - R * 0.55), (hx + R * 0.28, hy + R * 0.12)]
    d.polygon(horn, fill=tuple(max(0, c - 70) for c in u.fur) + (255,), outline=INK + (255,))
    for s in (-1, 1):
        ex = x + fdx * R * 0.45 + (-fdy) * s * R * 0.32
        ey = y + fdy * R * 0.3 + fdx * s * R * 0.32 - R * 0.05
        er = R * 0.13
        d.ellipse((ex - er, ey - er * 1.3, ex + er, ey + er * 1.3), fill=INK + (255,))
    if u.charge >= 1.0:
        p = (math.sin(t * 8) + 1) / 2
        rr = R * (1.35 + 0.1 * p)
        d.ellipse((x - rr, y - rr, x + rr, y + rr), outline=GOLD + (int(150 + 100 * p),), width=6)
    bw, bh = 104, 16
    by = y - R - 46
    d.rounded_rectangle((x - bw / 2 - 4, by - 4, x + bw / 2 + 4, by + bh + 4), radius=8, fill=INK + (255,))
    k = u.hp / u.maxhp
    col = TEAM[u.team] if k > 0.35 else CORAL
    d.rounded_rectangle((x - bw / 2, by, x - bw / 2 + max(6, bw * k), by + bh), radius=6, fill=col + (255,))
    text_c(d, (x, by - 18), f'{int(u.hp)}', font(F_BLACK, 26), (255, 255, 255, 255), 4)
    for i in range(b.AMMO_MAX):
        fill = min(1.0, max(0.0, u.ammo - i))
        ax = x - 26 + i * 26
        ay = by + bh + 12
        d.rounded_rectangle((ax - 11, ay - 4, ax + 11, ay + 4), radius=3, fill=INK + (200,))
        if fill > 0:
            d.rounded_rectangle((ax - 10, ay - 3, ax - 10 + 20 * fill, ay + 3), radius=3, fill=(250, 170, 60, 255) if fill >= 1 else (200, 150, 90, 255))


def draw_projs(d, world):
    for p in world.projs:
        x, y = P(p['pos'])
        k = p['kind']
        if k == 'tapon':
            r = 15
            d.ellipse((x - r - 4, y - r - 4, x + r + 4, y + r + 4), fill=INK + (255,))
            d.ellipse((x - r, y - r, x + r, y + r), fill=(250, 240, 220, 255))
            d.ellipse((x - r * 0.5, y - r * 0.6, x + r * 0.1, y - r * 0.1), fill=(255, 255, 255, 255))
        elif k == 'agua':
            vx, vy = b.v_norm(p['vel'])
            r = 11
            d.line((x - vx * 30, y - vy * 30, x, y), fill=(170, 225, 255, 160), width=12)
            d.ellipse((x - r, y - r, x + r, y + r), fill=(150, 215, 255, 255), outline=(60, 120, 170, 255), width=3)
        elif k == 'espina':
            vx, vy = b.v_norm(p['vel'])
            nx, ny = -vy, vx
            pts = [(x + vx * 22, y + vy * 22), (x - vx * 14 + nx * 8, y - vy * 14 + ny * 8), (x - vx * 14 - nx * 8, y - vy * 14 - ny * 8)]
            d.polygon(pts, fill=(120, 170, 100, 255), outline=INK + (255,))
        elif k == 'cometa':
            vx, vy = b.v_norm(p['vel'])
            for i in range(5):
                tx, ty = x - vx * i * 14, y - vy * i * 14
                tr = 16 - i * 3
                d.ellipse((tx - tr, ty - tr, tx + tr, ty + tr), fill=(255, 210, 110, 200 - i * 35))
            pts = []
            for i in range(10):
                a = i * math.pi / 5 + world.t * 6
                rr = 18 if i % 2 == 0 else 8
                pts.append((x + math.cos(a) * rr, y + math.sin(a) * rr))
            d.polygon(pts, fill=GOLD + (255,), outline=INK + (255,))
    for lb in world.lobs:
        k = (world.t - lb['t0']) / (lb['at'] - lb['t0'])
        k = min(max(k, 0), 1)
        tx, ty = P(lb['pos'])
        R = lb['radius'] * PX
        d.ellipse((tx - R, ty - R, tx + R, ty + R), fill=(255, 190, 220, int(40 + 70 * k)), outline=(255, 150, 200, 230), width=5)
        sx, sy = P(lb['start'])
        mx, my = sx + (tx - sx) * k, sy + (ty - sy) * k - math.sin(k * math.pi) * 3.2 * PX
        for j in range(3):
            ox = (j - 1) * 26
            d.ellipse((mx + ox - 18, my - 18, mx + ox + 18, my + 18), fill=(255, 225, 238, 255), outline=INK + (255,), width=4)
    for x, y, r, until in world.walls:
        cx, cy = P((x, y))
        rr = r * PX
        d.rounded_rectangle((cx - rr - 5, cy - rr - 5, cx + rr + 5, cy + rr + 5), radius=10, fill=INK + (255,))
        d.rounded_rectangle((cx - rr, cy - rr, cx + rr, cy + rr), radius=8, fill=(205, 170, 140, 255))
    for z in world.zones:
        cx, cy = P(z['pos'])
        R = z['radius'] * PX
        d.ellipse((cx - R, cy - R, cx + R, cy + R), fill=(255, 255, 255, 70), outline=(255, 255, 255, 220), width=6)
        for i in range(6):
            a = i * 1.047 + world.t * 0.8
            px, py = cx + math.cos(a) * R * 0.6, cy + math.sin(a) * R * 0.6
            d.rectangle((px - 4, py - 14, px + 4, py + 14), fill=(120, 210, 110, 220))
            d.rectangle((px - 14, py - 4, px + 14, py + 4), fill=(120, 210, 110, 220))


def draw_fx(d, world, fx, t):
    keep = []
    for f in fx.items:
        k = (t - f['t0']) / f['life']
        if k > 1:
            continue
        keep.append(f)
        ty = f['type']
        if ty == 'num':
            x, y = P(f['pos'])
            x += f['jitter'] * PX
            y -= 70 + k * 60
            s = 0.6 + 0.6 * ease_out_back(min(1, k * 4)) - 0.2 * max(0, k - 0.6)
            a = int(255 * (1 - max(0, k - 0.65) / 0.35))
            text_c(d, (x, y), f['text'], font(F_DISPLAY, max(10, int(f['size'] * s * 1.3))), f['color'] + (a,), 5, INK + (a,))
        elif ty == 'spark':
            x, y = P(f['pos'])
            c = (255, 255, 255)
            for i in range(6):
                a = i * 1.047 + f['t0'] * 7
                r0, r1 = 20 + k * 30, 34 + k * 60
                d.line((x + math.cos(a) * r0, y + math.sin(a) * r0, x + math.cos(a) * r1, y + math.sin(a) * r1),
                       fill=c + (int(255 * (1 - k)),), width=6)
        elif ty == 'ko':
            x, y = P(f['pos'])
            R = (1 + 2.5 * k) * PX
            d.ellipse((x - R, y - R, x + R, y + R), outline=TEAM[f['team']] + (int(255 * (1 - k)),), width=10)
            s = ease_out_back(min(1, k * 3))
            text_c(d, (x, y - 40), 'KO', font(F_DISPLAY, max(10, int(70 * s))), CORAL + (int(255 * (1 - k * 0.6)),), 7)
        elif ty == 'swing':
            u = world.units[f['uid']]
            x, y = P(u.pos)
            R = f['range'] * PX
            ang = math.degrees(math.atan2(f['dir'][1], f['dir'][0]))
            sweep = f['arc'] * min(1, k * 2)
            d.arc((x - R, y - R, x + R, y + R), ang - f['arc'] / 2, ang - f['arc'] / 2 + sweep, fill=(255, 255, 255, int(255 * (1 - k))), width=14)
        elif ty == 'whip':
            a, bb = P(f['a']), P(f['b'])
            d.line((a, bb), fill=(255, 255, 255, int(255 * (1 - k))), width=int(16 * (1 - k)) + 2)
        elif ty == 'ring':
            x, y = P(f['pos'])
            R = f['r'] * PX * (0.4 + 0.6 * k)
            d.ellipse((x - R, y - R, x + R, y + R), outline=f['color'] + (int(255 * (1 - k)),), width=8)
        elif ty == 'pop':
            x, y = P(f['pos'])
            R = 10 + 20 * k
            d.ellipse((x - R, y - R, x + R, y + R), outline=(255, 255, 255, int(200 * (1 - k))), width=4)
        elif ty == 'label':
            u = world.units[f['uid']]
            x, y = P(u.pos)
            text_c(d, (x, y + 66), f['text'], font(F_BLACK, 28), (255, 255, 255, int(255 * (1 - k))), 5)
        elif ty == 'tick':
            pass
    fx.items = keep


def draw_hud(d, world, score, rnd, fx, t):
    d.rounded_rectangle((W / 2 - 250, 14, W / 2 + 250, 120), radius=26, fill=INK + (235,))
    rem = max(0, b.ROUND_MAX - world.t)
    text_c(d, (W / 2, 50), f'RONDA {rnd}', font(F_DISPLAY, 34), CREAM + (255,))
    text_c(d, (W / 2, 92), f'{int(rem // 60)}:{int(rem % 60):02d}', font(F_MONO, 34), CREAM + (255,))
    for team, x in ((0, W / 2 - 170), (1, W / 2 + 170)):
        for i in range(2):
            sx = x + (i - 0.5) * 50
            filled = score[team] > i
            pts = []
            for j in range(10):
                a = -math.pi / 2 + j * math.pi / 5
                rr = 20 if j % 2 == 0 else 9
                pts.append((sx + math.cos(a) * rr, 68 + math.sin(a) * rr))
            d.polygon(pts, fill=(TEAM[team] if filled else (90, 70, 60)) + (255,), outline=CREAM + (255,))
    for side, team in ((0, 0), (1, 1)):
        units = [u for u in world.units if u.team == team]
        x0 = 14 if side == 0 else W - 14 - 330
        for i, u in enumerate(units):
            y0 = 190 + i * 300
            alpha = 255 if u.alive else 120
            d.rounded_rectangle((x0, y0, x0 + 330, y0 + 270), radius=22, fill=INK + (int(225 * alpha / 255),),
                                outline=TEAM[team] + (alpha,), width=5)
            d.ellipse((x0 + 18, y0 + 18, x0 + 70, y0 + 70), fill=u.fur + (alpha,), outline=CREAM + (alpha,), width=3)
            d.text((x0 + 84, y0 + 20), u.name, font=font(F_BLACK, 30), fill=CREAM + (alpha,))
            d.text((x0 + 84, y0 + 54), b.BODIES[u.body]['label'], font=font(F_TEXT, 20), fill=(200, 180, 160, alpha))
            lines = [('ATQ', b.ATTACKS[u.horn]['name']), ('SÚPER', b.SUPERS[u.back]['name']), ('TRUCO', b.GADGETS[u.wing]['name'])]
            for j, (tag, nm) in enumerate(lines):
                yy = y0 + 92 + j * 34
                col = GOLD if tag == 'SÚPER' else (TEAM[team] if tag == 'ATQ' else (200, 200, 200))
                d.text((x0 + 18, yy), tag, font=font(F_BLACK, 18), fill=col + (alpha,))
                d.text((x0 + 90, yy - 2), nm, font=font(F_TEXT, 21), fill=CREAM + (alpha,))
            bw = 294
            k = u.hp / u.maxhp
            d.rounded_rectangle((x0 + 18, y0 + 200, x0 + 18 + bw, y0 + 220), radius=8, fill=(30, 20, 15, alpha))
            if u.alive:
                d.rounded_rectangle((x0 + 18, y0 + 200, x0 + 18 + max(8, bw * k), y0 + 220), radius=8, fill=TEAM[team] + (255,))
            d.rounded_rectangle((x0 + 18, y0 + 232, x0 + 18 + bw, y0 + 248), radius=7, fill=(30, 20, 15, alpha))
            if u.alive and u.charge > 0:
                d.rounded_rectangle((x0 + 18, y0 + 232, x0 + 18 + max(8, bw * u.charge), y0 + 248), radius=7,
                                    fill=GOLD + (255 if u.charge >= 1 else 200,))
            if not u.alive:
                text_c(d, (x0 + 165, y0 + 135), 'KO', font(F_DISPLAY, 80), CORAL + (230,), 6)
    feeds = [f for f in fx.items if f['type'] == 'feed']
    if fx.banner:
        bn = fx.banner
        k = (t - bn['t0']) / bn['life']
        if k > 1:
            fx.banner = None
        else:
            s = ease_out_back(min(1, k * 5))
            a = int(255 * (1 - max(0, k - 0.75) / 0.25))
            y = H - 120
            d.rounded_rectangle((W / 2 - 460 * s, y - 62, W / 2 + 460 * s, y + 52), radius=26, fill=INK + (int(a * 0.9),),
                                outline=TEAM[bn['team']] + (a,), width=6)
            text_c(d, (W / 2, y - 26), bn['who'], font(F_BLACK, 28), TEAM[bn['team']] + (a,))
            text_c(d, (W / 2, y + 14), bn['text'], font(F_DISPLAY, max(10, int(44 * s))), GOLD + (a,), 5)


def kill_feed(world, fx, t):
    return [f for f in fx.items if f['type'] == 'feed']


def card(base, title, sub, team=None, sub2=None):
    im = base.copy().convert('RGBA')
    ov = Image.new('RGBA', (W, H), (40, 24, 18, 170))
    im.alpha_composite(ov)
    d = ImageDraw.Draw(im)
    c = TEAM[team] if team is not None else CREAM
    text_c(d, (W / 2, H / 2 - 40), title, font(F_DISPLAY, 120), c + (255,), 10)
    if sub:
        text_c(d, (W / 2, H / 2 + 70), sub, font(F_BLACK, 44), CREAM + (255,), 5)
    if sub2:
        text_c(d, (W / 2, H / 2 + 130), sub2, font(F_BLACK, 36), GOLD + (255,), 5)
    return im.convert('RGB').resize((OW, OH), Image.LANCZOS)


def render_match(seeds, teams, crystals=60):
    os.makedirs(OUT, exist_ok=True)
    for f in os.listdir(OUT):
        if f.endswith('.jpg'):
            os.remove(os.path.join(OUT, f))
    n = [0]

    def save(im, times=1):
        for _ in range(times):
            im.save(os.path.join(OUT, 'f_%05d.jpg' % n[0]), quality=90)
            n[0] += 1

    score = [0, 0]
    for rnd, seed in enumerate(seeds, start=1):
        random.seed(seed)
        world = b.World(b.ROSTER, teams, seed, log=True)
        base = build_floor(world)
        fx = Fx()
        save(card(frame0_full(world, base, fx, score, rnd), f'RONDA {rnd}', 'AZUL  vs  ROJO'), 45)
        done = None
        ev_i = 0
        while done is None:
            world.step()
            new = world.events[ev_i:]
            ev_i = len(world.events)
            kos = 0
            if abs(world.t - b.GAS_START) < b.DT / 2:
                fx.banner = dict(t0=world.t, life=1.8, text='¡SE CIERRA EL GAS!', team=1, who='')
            for e in new:
                ingest(fx, world, e, world.t)
                kos += e['ev'] == 'ko'
            im = render_frame(world, base, fx, score, rnd)
            save(im, 1 + (5 if kos else 0))
            done = world.winner()
        score[done] += 1
        last = frame0_full(world, base, fx, score, rnd)
        alive = sum(1 for u in world.units if u.alive and u.team == done)
        save(card(last, f'¡GANA {TEAM_NAME[done]}!', f'{alive} en pie · {score[0]} - {score[1]}', done), 60)
        print(f'ronda {rnd} seed {seed}: gana {TEAM_NAME[done]} con {alive} vivos en {world.t:.0f} s')
        if max(score) == 2:
            win = 0 if score[0] == 2 else 1
            save(card(last, f'¡{TEAM_NAME[win]} SE LLEVA LA PARTIDA!', f'{score[0]} - {score[1]}', win, f'+{crystals} cristales'), 90)
            break
    return n[0]


def frame0_full(world, base, fx, score, rnd):
    im = base.copy().convert('RGBA')
    layer = Image.new('RGBA', (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)
    for u in world.units:
        draw_unit(d, world, u, fx, world.t)
    draw_hud(d, world, score, rnd, Fx(), world.t)
    im.alpha_composite(layer)
    return im


def render_frame(world, base, fx, score, rnd):
    t = world.t
    im = base.copy().convert('RGBA')
    gas = Image.new('RGBA', (W, H), (0, 0, 0, 0))
    draw_gas(gas, world)
    im.alpha_composite(gas)
    layer = Image.new('RGBA', (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)
    for u in world.units:
        if u.alive:
            draw_telegraph(d, world, u)
    im.alpha_composite(layer)
    layer = Image.new('RGBA', (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)
    for u in sorted(world.units, key=lambda u: u.pos[1]):
        draw_unit(d, world, u, fx, t)
    draw_projs(d, world)
    draw_fx(d, world, fx, t)
    im.alpha_composite(layer)
    hud = Image.new('RGBA', (W, H), (0, 0, 0, 0))
    hd = ImageDraw.Draw(hud)
    draw_hud(hd, world, score, rnd, fx, t)
    if fx.shake > 0.3:
        dx = int(random.uniform(-fx.shake, fx.shake) * SS)
        dy = int(random.uniform(-fx.shake, fx.shake) * SS)
        im = Image.Image.transform(im, im.size, Image.AFFINE, (1, 0, dx, 0, 1, dy), fillcolor=(232, 214, 186, 255))
        fx.shake *= 0.8
    im.alpha_composite(hud)
    return im.convert('RGB').resize((OW, OH), Image.LANCZOS)


if __name__ == '__main__':
    seeds = [int(x) for x in sys.argv[1].split(',')] if len(sys.argv) > 1 else [221, 213, 259]
    blue = [0, 2, 5]
    teams = [0 if i in blue else 1 for i in range(6)]
    total = render_match(seeds, teams)
    print('frames', total)
