import json, math, os, sys
from PIL import Image, ImageDraw, ImageFont

OUT = sys.argv[1]
STUDIO = sys.argv[2]
FONT = sys.argv[3]
MONO = sys.argv[4]
os.makedirs(OUT, exist_ok=True)

W, H = 1920, 1080
FPS = 30
DUR = 30.0
BAR = 103
CREAM = (244, 227, 206)
CORAL = (194, 68, 40)
GOLD = (245, 185, 72)
INK = (52, 30, 22)

TITLES = [
    (0.25, 1.65, 'EVERY EGG HIDES SOMEONE NEW', 64),
    (2.0, 1.9, 'HATCH THEM', 124),
    (4.0, 1.9, 'RAISE THEM', 124),
    (6.0, 1.9, 'BREED THEM', 124),
    (8.0, 1.9, 'NO TWO ARE ALIKE', 104),
    (12.0, 2.4, 'SEND THEM TO FIGHT', 104),
    (15.5, 1.9, 'GRAB THE LOOT', 112),
    (18.5, 2.3, 'OUTSMART RIVALS', 108),
]
WIPES = [2.0, 8.0, 12.0, 24.0]
STROBE = [(22.0, 'HATCH'), (22.25, 'RAISE'), (22.5, 'BREED'), (22.75, 'FIGHT')]
QUESTION = (23.0, 1.0, 'WHICH ONE WILL YOU RAISE?')
SOON = 26.2
CARD_NAMES = ['Moldy Sprout', 'Snappy Glob', 'Murky Wisp']
CARD_TIMES = [8.35, 8.85, 9.35]
CARD_OUT = 10.0
LIFE = [(10.0, 'EGG'), (10.25, 'BLOBIM'), (10.5, 'ADULT')]
LIFE_OUT = 11.9

fonts = {}


def font(size, mono=False):
    key = (size, mono)
    if key not in fonts:
        fonts[key] = ImageFont.truetype(MONO if mono else FONT, size)
    return fonts[key]


def clamp(v, a=0.0, b=1.0):
    return max(a, min(b, v))


def out_cubic(p):
    return 1 - (1 - p) ** 3


def out_back(p, s=2.2):
    p -= 1
    return p * p * ((s + 1) * p + s) + 1


def in_cubic(p):
    return p ** 3


glyph_cache = {}


def glyph(ch, size):
    key = (ch, size)
    if key in glyph_cache:
        return glyph_cache[key]
    f = font(size)
    pad = 20
    l, t, r, b = f.getbbox(ch, stroke_width=4)
    w, h = r - l + pad * 2 + 8, b - t + pad * 2 + 8
    im = Image.new('RGBA', (max(w, 1), max(h, 1)), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    ox, oy = pad - l, pad - t
    d.text((ox + 7, oy + 7), ch, font=f, fill=CORAL + (255,), stroke_width=4, stroke_fill=CORAL + (255,))
    d.text((ox, oy), ch, font=f, fill=CREAM + (255,), stroke_width=4, stroke_fill=INK + (255,))
    glyph_cache[key] = (im, ox, oy)
    return glyph_cache[key]


def kinetic(canvas, text, t, dur, size, x, baseline, center=False, bar=True):
    if t < 0 or t > dur:
        return
    f = font(size)
    total = f.getlength(text)
    if center:
        x = (W - total) / 2
    exit_p = clamp((t - (dur - 0.2)) / 0.2)
    exit_e = in_cubic(exit_p)
    for i, ch in enumerate(text):
        if ch == ' ':
            continue
        p = clamp((t - 0.035 * i) / 0.24)
        if p <= 0:
            continue
        e = out_back(p)
        sc = max(0.01, 0.4 + 0.6 * e)
        im, ox, oy = glyph(ch, size)
        iw, ih = im.size
        nw, nh = max(1, int(iw * sc)), max(1, int(ih * sc))
        g = im.resize((nw, nh), Image.BILINEAR)
        alpha = clamp(p * 3) * (1 - exit_e)
        if alpha < 1:
            a = g.getchannel('A').point(lambda v: int(v * alpha))
            g.putalpha(a)
        gx = x + f.getlength(text[:i])
        ytop = baseline - size * 0.8
        cx = gx - ox + iw / 2
        cy = ytop - oy + ih / 2 + (1 - e) * 46 - exit_e * 40
        canvas.alpha_composite(g, (int(cx - nw / 2), int(cy - nh / 2)))
    if bar:
        bp = out_cubic(clamp((t - 0.12) / 0.35))
        bw = (total + 24) * bp * (1 - exit_e)
        d = ImageDraw.Draw(canvas)
        by = baseline + size * 0.18 + 14
        bx = x if not center else (W - bw) / 2
        if bw > 1:
            d.rectangle([bx, by, bx + bw, by + 10], fill=GOLD + (255,))


def wipe(canvas, t, T):
    span = 0.34
    p = (t - (T - span / 2)) / span
    if p <= 0 or p >= 1:
        return
    d = ImageDraw.Draw(canvas)
    slant = 420
    for k, col in enumerate([GOLD, CORAL, CREAM]):
        q = clamp(p * 1.25 - k * 0.1)
        lead = -slant + (W + slant * 2) * out_cubic(clamp(q * 1.6))
        tail = -slant + (W + slant * 2) * in_cubic(clamp(q * 1.6 - 0.6))
        if lead <= tail:
            continue
        d.polygon([(tail, H), (lead, H), (lead + slant, 0), (tail + slant, 0)], fill=col + (255,))


def rounded(d, box, r, fill):
    d.rounded_rectangle(box, r, fill=fill)


def card(canvas, t, entry, slot):
    t_in = CARD_TIMES[slot]
    if t < t_in or t > CARD_OUT + 0.3:
        return
    pin = out_back(clamp((t - t_in) / 0.28), 1.6)
    pout = in_cubic(clamp((t - CARD_OUT - 0.04 * slot) / 0.26))
    cw, ch = 560, 168
    x = W - 70 - cw + (1 - pin) * (cw + 120) + pout * (cw + 120)
    y = BAR + 44 + slot * (ch + 22)
    if x >= W:
        return
    lay = Image.new('RGBA', (cw + 20, ch + 20), (0, 0, 0, 0))
    d = ImageDraw.Draw(lay)
    rounded(d, (10, 14, cw + 10, ch + 14), 22, INK + (110,))
    rounded(d, (0, 0, cw, ch), 22, CREAM + (246,))
    rounded(d, (0, 0, 16, ch), 8, CORAL + (255,))
    hexcol = entry['dna'].split('-')[-1]
    col = tuple(int(hexcol[i:i + 2], 16) for i in (0, 2, 4))
    d.ellipse((38, 30, 98, 90), fill=col + (255,), outline=INK + (255,), width=4)
    d.text((118, 22), entry['name'].upper(), font=font(40), fill=INK + (255,))
    sym = '♀' if entry['gender'] == 'Female' else '♂'
    d.text((cw - 58, 20), sym, font=font(40, True), fill=CORAL + (255,))
    genes = entry['dna'].split('-')
    shown = clamp((t - t_in - 0.18) / 0.5)
    n = int(len(genes) * shown + 0.999) if shown > 0 else 0
    gx = 38
    d.text((gx, 104), 'DNA', font=font(26, True), fill=CORAL + (255,))
    gx += 64
    for i in range(n):
        g = genes[i]
        tw = font(28, True).getlength(g)
        fresh = clamp((t - t_in - 0.18 - i * 0.5 / len(genes)) / 0.12)
        fill = GOLD if fresh < 1 else INK
        rounded(d, (gx - 6, 100, gx + tw + 6, 140), 8, (fill if fresh < 1 else (232, 210, 186)) + (255,))
        d.text((gx, 103), g, font=font(28, True), fill=INK + (255,))
        gx += tw + 18
    canvas.alpha_composite(lay, (int(x), int(y)))


def life_strip(canvas, t):
    if t < LIFE[0][0] or t > LIFE_OUT + 0.25:
        return
    d = ImageDraw.Draw(canvas)
    f = font(46)
    pout = in_cubic(clamp((t - LIFE_OUT) / 0.25))
    widths = [f.getlength(s) + 60 for _, s in LIFE]
    gap = 90
    total = sum(widths) + gap * (len(LIFE) - 1)
    x = (W - total) / 2
    y = H - BAR - 120 + pout * 200
    for i, (t0, s) in enumerate(LIFE):
        p = out_back(clamp((t - t0) / 0.22))
        if p > 0:
            w = widths[i]
            cx = x + w / 2
            hw, hh = w / 2 * p, 38 * p
            rounded(d, (cx - hw, y - hh, cx + hw, y + hh), int(36 * p) + 1, CREAM + (250,))
            if p > 0.6:
                d.text((cx, y), s, font=f, fill=INK + (255,), anchor='mm')
            if i < len(LIFE) - 1:
                ax = x + w + 18
                q = clamp((t - LIFE[i + 1][0]) / 0.2)
                if q > 0:
                    d.polygon([(ax, y - 16), (ax + 50 * q, y), (ax, y + 16)], fill=GOLD + (255,))
        x += widths[i] + gap


def strobe(canvas, t):
    for t0, word in STROBE:
        if t0 <= t < t0 + 0.25:
            d = ImageDraw.Draw(canvas)
            k = (t - t0) / 0.25
            size = int(230 + 40 * k)
            f = font(size)
            d.text((W / 2 + 10, H / 2 + 10), word, font=f, fill=CORAL + (255,), anchor='mm', stroke_width=6, stroke_fill=CORAL + (255,))
            d.text((W / 2, H / 2), word, font=f, fill=CREAM + (255,), anchor='mm', stroke_width=6, stroke_fill=INK + (255,))


def question(canvas, t):
    t0, dur, text = QUESTION
    if t < t0 or t >= t0 + dur:
        return
    d = ImageDraw.Draw(canvas)
    n = int(len(text) * clamp((t - t0) / 0.5))
    f = font(84)
    full = f.getlength(text)
    x = (W - full) / 2
    d.text((x, H / 2), text[:n], font=f, fill=CREAM + (255,), anchor='lm')
    if int(t * 8) % 2 == 0 or n < len(text):
        cx = x + f.getlength(text[:n]) + 10
        d.rectangle([cx, H / 2 - 40, cx + 18, H / 2 + 40], fill=GOLD + (255,))


def soon(canvas, t):
    if t < SOON:
        return
    p = out_cubic(clamp((t - SOON) / 0.6))
    d = ImageDraw.Draw(canvas)
    text = 'C O M I N G   S O O N'
    f = font(44)
    a = int(255 * p * clamp((DUR - 0.3 - t) / 0.5))
    d.text((W / 2, H - BAR - 150 + (1 - p) * 30), text, font=f, fill=CREAM + (a,), anchor='mm')


def vhs(canvas, t):
    if t > 1.7:
        return
    d = ImageDraw.Draw(canvas)
    if int(t * 4) % 2 == 0:
        d.polygon([(150, BAR + 46), (150, BAR + 86), (184, BAR + 66)], fill=CREAM + (230,))
        d.text((200, BAR + 40), 'PLAY', font=font(44, True), fill=CREAM + (230,))
    d.text((W - 150, BAR + 40), 'SP 0:00:%02d' % int(t * 10), font=font(44, True), fill=CREAM + (230,), anchor='ra')


studio = json.load(open(STUDIO, encoding='utf-8'))
cards = [next(e for e in studio if e['name'] == n and e['group'] == 'line') for n in CARD_NAMES]

frames = int(DUR * FPS)
only = [int(v) for v in sys.argv[5].split(',')] if len(sys.argv) > 5 else range(frames)
for fi in only:
    t = fi / FPS
    cv = Image.new('RGBA', (W, H), (0, 0, 0, 0))
    vhs(cv, t)
    for t0, dur, text, size in TITLES:
        kinetic(cv, text, t - t0, dur, size, 150, H - BAR - 120, center=(t0 < 1), bar=(t0 >= 1))
    for i, e in enumerate(cards):
        card(cv, t, e, i)
    life_strip(cv, t)
    strobe(cv, t)
    question(cv, t)
    soon(cv, t)
    for T in WIPES:
        wipe(cv, t, T)
    cv.save(os.path.join(OUT, 'g_%04d.png' % fi), compress_level=1)
print('GFX_DONE', frames)
