"""Issue 9 (Tajná zpráva v knihovně): Klub Hvězdička's star code, the slips with pinking-shear edges, the village
library with its dachshund, babička's sewing, and Masopust: the girls' costumes (Alica an owl, Hanka a bear cub),
the bear, the kobyla, the kominík, the bába s nůší, the straw man, the musician, koblihy.

Costumed figures are the normal characters drawn with their clothes recoloured (`recolor`) and a costume drawn over
them, so faces, poses and balloon anchors stay the same as everywhere else.

The star code (hvězdičkové písmo): each letter is a shape (star, moon, heart, circle) with 1-6 dots under it, laid out
like the dots on a die. The kids know dice, so they can read it by counting. No háčky or čárky."""
import math, random
import lib
from lib import G, ell, bez, rrect, resample
from style3 import *
from style3 import C, _SC, Kid, arm_pts, draw_arm, draw_legs, head_outline, face, notch, hand
import palette as P
from scenes3 import BG, s_, sh_, sky, hills
from chars3 import Person, BABI, DEDA, TONDA, babicka, deda, tonda, star
from winter import betka, snowy_house, snow_field
from village import heart_pts, church, kostelnik
from pond import verka_old, VERKA
from attic import young
from letter import hand_text


# ------------------------------------------------------------------ helpers
class recolor:
    """temporarily swap palette entries, e.g. with recolor(ALICA_COAT=P.COSTUME_OWL): alica(...)"""
    def __init__(self, **kw): self.kw = kw

    def __enter__(self):
        self.old = {k: getattr(P, k) for k in self.kw}
        for k, v in self.kw.items(): setattr(P, k, v)

    def __exit__(self, *e):
        for k, v in self.old.items(): setattr(P, k, v)


def ring_fill(outer, inner, g, w=LINE, w_in=None):
    """a shape with a hole (a hood around a face, a headscarf, a mask): even-odd fill, both edges inked"""
    C.saveState()
    pth = C.beginPath()
    for poly_ in (outer, inner):
        pth.moveTo(*poly_[0])
        for q in poly_[1:]: pth.lineTo(*q)
        pth.close()
    C.setFillColor(G(g)); C.drawPath(pth, fill=1, stroke=0, fillMode=0)
    C.restoreState()
    stroke(outer, w, closed=True); stroke(inner, w if w_in is None else w_in, closed=True)


def zigzag(a, b, t=2.4, step=None, inward=1):
    """the points of a pinking-shear edge from a to b: teeth t deep, on the left of a->b when inward=1"""
    (x0, y0), (x1, y1) = a, b
    L = math.hypot(x1 - x0, y1 - y0) or 1
    step = step or t*1.25
    n = max(2, int(L/step))
    nx, ny = -(y1 - y0)/L*inward, (x1 - x0)/L*inward
    out = []
    for i in range(n + 1):
        f = i/n; d = t if i % 2 else 0
        out.append((x0 + (x1 - x0)*f + nx*d, y0 + (y1 - y0)*f + ny*d))
    return out


def zig_poly(corners, t=2.4, sides=None):
    """a closed outline through corners with pinking-shear teeth on the chosen sides (all by default)"""
    out = []
    n = len(corners)
    for i in range(n):
        a, b = corners[i], corners[(i + 1) % n]
        if sides is None or i in sides:
            out += zigzag(a, b, t)[:-1]
        else:
            out.append(a)
    return out


# ------------------------------------------------------------------ the star code
ROWS = ["ABCDEF", "GHIJKL", "MNOPRS", "TUVYZ"]
SHAPES = ["star", "moon", "heart", "circle"]
CODE = {ch: (SHAPES[r], i + 1) for r, row in enumerate(ROWS) for i, ch in enumerate(row)}
DICE = {1: [(0, 0)], 2: [(-1, 1), (1, -1)], 3: [(-1, 1), (0, 0), (1, -1)], 4: [(-1, 1), (1, 1), (-1, -1), (1, -1)],
        5: [(-1, 1), (1, 1), (0, 0), (-1, -1), (1, -1)], 6: [(-1, 1), (1, 1), (-1, 0), (1, 0), (-1, -1), (1, -1)]}


def star_pts(cx, cy, r, style="jana"):
    """jana: a star drawn in one stroke, lines crossing, a little window in the middle (how babička draws them);
    deda: the outline of a star, as děda draws it"""
    if style == "jana":
        return [(cx + math.cos(math.radians(90 + 144*i))*r, cy + math.sin(math.radians(90 + 144*i))*r) for i in range(6)]
    pts = []
    for i in range(10):
        rr = r if i % 2 == 0 else r*0.42
        a = math.radians(90 + 36*i)
        pts.append((cx + math.cos(a)*rr, cy + math.sin(a)*rr))
    return pts


def glyph(ch, x, y, h=12, style="jana", g=None):
    """one letter of the star code; (x, y) = the bottom middle of its cell, h = the cell height"""
    g = P.CIPHER_INK if g is None else g
    shp, n = CODE[ch]
    w = min(max(0.35, h*_SC[-1]*0.075), 1.8)
    cx, cy, rs = x, y + h*0.66, h*0.27
    if shp == "star":
        stroke(star_pts(cx, cy, rs*1.1, style), w, closed=style != "jana", g=g)
    elif shp == "moon":
        outer = ell(cx, cy, rs, rs, 24, 50, 310)
        inner = ell(cx + rs*0.55, cy, rs*0.8, rs*0.8, 20, 74, 286)[::-1]
        stroke(outer + inner, w, closed=True, g=g)
    elif shp == "heart":
        stroke(heart_pts(cx, cy - rs*0.08, rs*0.95), w, closed=True, g=g)
    else:
        stroke(ell(cx, cy, rs*0.85, rs*0.85, 24), w, closed=True, g=g)
    d = h*0.11
    for dx, dy in DICE[n]:
        dot(cx + dx*d, y + h*0.17 + dy*d, h*0.045, g)


def cipher_width(text, h=12):
    return sum(h*0.5 if c == " " else h*0.78 for c in text) - h*0.08


def cipher_text(text, x, y, h=12, style="jana", g=None):
    """a coded line, left end at x, bottom at y. Returns the x of each letter's middle (None for spaces)."""
    xs = []
    for c in text:
        if c == " ":
            xs.append(None); x += h*0.5; continue
        glyph(c, x + h*0.35, y, h, style, g)
        xs.append(x + h*0.35); x += h*0.78
    return xs


def cipher_decoded(text, x, y, h=14, upto=None, style="jana", size=None, g=None):
    """a coded line with the letters written under it, as Alica decodes it (the first `upto` letters only)"""
    xs = cipher_text(text, x, y, h, style, g)
    size = size or h*0.7
    k = 0
    for c, cx in zip(text, xs):
        if cx is None: continue
        k += 1
        if upto is not None and k > upto: break
        hand_text(cx - h*0.4, y - size*1.05, h*0.8, c, "SHB", size)


def slip(x, y, w, h, lines=(), gh=10, rot=0, old=False, zig=True, style="jana", s=1.0, seed=3):
    """a paper slip with a coded message, centred on (x, y). zig: pinking-shear edges (babička's sewing scissors);
    old: yellowed, torn, folded in four (the slip from 60 years ago)"""
    with T(x, y, s, rot=rot):
        c = [(-w/2, -h/2), (w/2, -h/2), (w/2, h/2), (-w/2, h/2)]
        if old:
            r = random.Random(seed); o = []
            for i in range(4):
                a, b = c[i], c[(i + 1) % 4]
                for k in range(8):
                    f = k/8
                    o.append((a[0] + (b[0] - a[0])*f + r.uniform(-0.9, 0.9), a[1] + (b[1] - a[1])*f + r.uniform(-0.9, 0.9)))
            fill([(px + 1.5, py - 1.5) for px, py in o], 0.0, 0.15)
            shape(o, P.OLD_SLIP, LINE*0.7)
            stroke([(-w/2 + 1, 0.5), (w/2 - 1, -0.5)], LINE*0.35, g=0.55)
            stroke([(0.4, -h/2 + 1), (-0.4, h/2 - 1)], LINE*0.35, g=0.55)
            fill(ell(w*0.3, -h*0.25, w*0.1, h*0.12, 16), P.OLD_SLIP*0.85 if lib.MODE == "bw" else P.OLD_SLIP, 0.35)
        else:
            o = zig_poly(c, 1.6) if zig else c
            fill([(px + 1.5, py - 1.5) for px, py in o], 0.0, 0.15)
            shape(o, P.SLIP, LINE*0.6)
        n = len(lines)
        for i, ln in enumerate(lines):
            yy = h/2 - (h - n*gh*1.25)/2 - (i + 1)*gh*1.25 + gh*0.15
            cipher_text(ln, -cipher_width(ln, gh)/2, yy, gh, style)


def cipher_key(x, y, w, h, style="deda", g=None, title=True):
    """the key from děda's club notebook: 4 rows (star, moon, heart, circle) x 6 letters; (x, y) = bottom left"""
    rows_ = len(ROWS)
    ch_ = h/(rows_ + (0.5 if title else 0))
    cw = w/6
    for r_, row in enumerate(ROWS):
        yy = y + h - (r_ + (1.5 if title else 1))*ch_
        for i, c in enumerate(row):
            cx = x + cw*(i + 0.5)
            glyph(c, cx, yy + ch_*0.36, ch_*0.6, style, g)
            hand_text(cx - cw/2, yy + ch_*0.04, cw, c, "SHB", ch_*0.3)


# ------------------------------------------------------------------ the hidden-object game: koblížky
def _koblih_body(rx, ry, sugar=True):
    o = ell(0, 0, rx, ry, 36)
    fill(o, P.KOBLIH)
    C.saveState(); C.clipPath(poly(o), stroke=0, fill=0)
    fill(bez((-rx*1.1, -ry*0.12), (-rx*0.4, -ry*0.38), (rx*0.4, -ry*0.38), (rx*1.1, -ry*0.12)) +
         bez((rx*1.1, ry*0.12), (rx*0.4, -ry*0.12), (-rx*0.4, -ry*0.12), (-rx*1.1, ry*0.12)), P.KOBLIH_BAND)
    if sugar:
        r = random.Random(int(rx*10))
        for _ in range(int(rx*1.4)):
            dot(r.uniform(-rx*0.8, rx*0.8), r.uniform(ry*0.15, ry*0.9), max(0.4, rx*0.05), 1.0)
    C.restoreState()
    return o


def koblih(x, y, s=1.0, rot=0, bitten=False):
    """a Masopust doughnut (kobliha): round, sugar on top, the pale band round its middle"""
    with T(x, y, s, rot=rot):
        o = _koblih_body(10, 7.5)
        stroke(o, LINE*0.8, closed=True)
        if bitten:
            shape(ell(8, 4, 4, 3.6, 18), P.KOBLIH_BAND, LINE*0.6)
            shape(ell(8.5, 3.5, 2, 1.6, 12), P.JAM, LINE*0.3)


def hidden_koblih(x, y, r=13, rot=0):
    """one of the 10 koblížky hidden in the issue: inside a white halo and a black line, so it reads on any ground"""
    with T(x, y, 1.0, rot=rot):
        o = ell(0, 0, r, r*0.74, 36)
        stroke(o, LINE*4.4, closed=True, g=0.0, taper=False)
        stroke(o, LINE*2.8, closed=True, g=1.0, taper=False)
        _koblih_body(r, r*0.74)
        stroke(o, LINE*0.5, closed=True, g=0.0, taper=False)


# ------------------------------------------------------------------ babička's sewing
def pinking_shears(x, y, s=1.0, rot=0, open_=18):
    """babička's sewing scissors that cut a zigzag edge; pivot at (x, y), blades towards +x"""
    with T(x, y, s, rot=rot):
        for sg in (-1, 1):
            with T(0, 0, 1.0, rot=sg*open_/2):
                blade = [(-3, sg*2.6), (0, -sg*0.2)] + zigzag((0, -sg*0.2), (30, sg*0.6), 1.3, inward=sg) + [(31, sg*1.2), (2, sg*3.4)]
                shape(blade, 0.82, LINE*0.7)
                handle = ell(-14, sg*6.5, 7.5, 4.5, 24)
                ring_fill(handle, ell(-14, sg*6.5, 4.6, 2.3, 18), P.SEWING, LINE*0.7, LINE*0.5)
                shape([(-7, sg*4.2), (-2, sg*2.2), (-2, sg*4.4), (-7, sg*7)], P.SEWING, LINE*0.6)
        dot(0, 0, 1.4, 0.3)


def sewing_machine(x, y, s=1.0):
    """an old black sewing machine on a wooden base, needle on the left; (x, y) = the middle of the base bottom"""
    with T(x, y, s):
        sh_(rrect(-36, 0, 72, 8, 2), P.SHELF)
        body = [(-30, 15), (-17, 15), (-17, 34), (18, 34), (18, 8), (31, 8), (31, 44)] + \
               bez((31, 44), (31, 49), (27, 50), (22, 50)) + [(-26, 50)] + bez((-26, 50), (-30, 50), (-31, 47), (-31, 44))
        form(body, P.SEWING, sdx=-1.5, sdy=1, sh=0.1)
        stroke(bez((-12, 44), (-4, 47), (6, 41), (14, 45)), LINE*0.6, g=P.SEWING_GOLD)
        stroke(bez((22, 30), (26, 26), (24, 20), (27, 14)), LINE*0.6, g=P.SEWING_GOLD)
        stroke([(-24, 15), (-24, 8.5)], LINE*0.6, g=0.6)
        shape([(-27, 8), (-21, 8), (-21, 9.5), (-27, 9.5)], 0.75, LINE*0.4)
        shape(ell(35, 36, 3, 7, 18), 0.6, LINE*0.6)
        shape(rrect(-2, 50, 6, 7, 1), P.FABRIC[0], LINE*0.5)
        stroke([(1, 57), (-25, 46), (-24, 16)], LINE*0.3, g=0.4, taper=False)


def fabric_scrap(x, y, w=16, h=10, g=None, rot=0, seed=1):
    """an offcut from the costumes: its cut sides have pinking-shear teeth"""
    g = P.FABRIC[seed % len(P.FABRIC)] if g is None else g
    r = random.Random(seed)
    c = [(-w/2 + r.uniform(-2, 2), -h/2), (w/2, -h/2 + r.uniform(-2, 2)), (w/2 + r.uniform(-2, 2), h/2), (-w/2, h/2 + r.uniform(-2, 2))]
    with T(x, y, 1.0, rot=rot):
        shape(zig_poly(c, 1.5), g, LINE*0.5)


def sewing_corner(x, y, s=1.0):
    """babička's sewing table: the machine, a pincushion, the pinking shears and offcuts on the floor; (x, y) = floor"""
    with T(x, y, s):
        sh_([(-46, 46), (46, 46), (46, 50), (-46, 50)], P.SHELF)
        for lx in (-42, 40): sh_([(lx, 0), (lx + 4, 0), (lx + 4, 46), (lx, 46)], P.SHELF)
        sewing_machine(-4, 50, 0.85)
        pinking_shears(30, 54, 0.6, rot=-12)
        shape(ell(-38, 55, 5, 3.6, 16), P.HEADSCARF, LINE*0.5)
        for i, (fx, fy, rr) in enumerate(((-30, 3, 10), (-12, 2, -20), (8, 4, 35), (24, 2, -5))):
            fabric_scrap(fx, fy, 12, 7, rot=rr, seed=i + 2)


# ------------------------------------------------------------------ the library
def bookshelf(x0, x1, y0, y1, nrows=4, seed=1):
    r = random.Random(seed)
    sh_([(x0, y0), (x1, y0), (x1, y1), (x0, y1)], P.SHELF)
    rh = (y1 - y0 - 6)/nrows
    for k in range(nrows):
        yb = y0 + 3 + k*rh
        fill([(x0 + 3, yb + 3), (x1 - 3, yb + 3), (x1 - 3, yb + rh), (x0 + 3, yb + rh)], 0.3)
        xx = x0 + 4
        while xx < x1 - 9:
            bw = r.uniform(4.5, 9); bh = rh*r.uniform(0.62, 0.9)
            if xx + bw > x1 - 4: break
            g = r.choice((0.38, 0.5, 0.62, 0.75, 0.86, 0.45, 0.7))
            if r.random() < 0.06 and xx + bh < x1 - 6:
                shape([(xx, yb + 3), (xx + bw*0.9, yb + 3), (xx + bh*0.55 + bw, yb + 3 + bh*0.8), (xx + bh*0.55, yb + 3 + bh*0.85)], g, BG*0.6)
                xx += bh*0.6 + bw; continue
            shape([(xx, yb + 3), (xx + bw, yb + 3), (xx + bw, yb + 3 + bh), (xx, yb + 3 + bh)], g, BG*0.6)
            if r.random() < 0.5: stroke([(xx + 1, yb + 3 + bh*0.75), (xx + bw - 1, yb + 3 + bh*0.75)], BG*0.4, g=1.0)
            xx += bw + r.uniform(0, 1.2)
        sh_([(x0, yb), (x1, yb), (x1, yb + 3.5), (x0, yb + 3.5)], P.SHELF)


def library(p, floor=0.12, seed=1, back=True, window=True):
    """the village library: shelves all round, a window; returns the floor line"""
    bg_ = [(p.x - 5, p.y - 5), (p.x + p.w + 5, p.y - 5), (p.x + p.w + 5, p.y + p.h + 5), (p.x - 5, p.y + p.h + 5)]
    fill(bg_, P.LIB_WALL)
    fy = p.Y(floor)
    if back:
        xs = [p.x - 4]
        while xs[-1] < p.x + p.w:
            xs.append(xs[-1] + 96)
        for i in range(len(xs) - 1):
            if window and i == 1:
                x0, x1 = xs[i] + 14, xs[i + 1] - 14
                shape([(x0 - 4, p.Y(0.45) - 4), (x1 + 4, p.Y(0.45) - 4), (x1 + 4, p.Y(0.92) + 4), (x0 - 4, p.Y(0.92) + 4)], P.DOOR_FRAME, BG)
                shape([(x0, p.Y(0.45)), (x1, p.Y(0.45)), (x1, p.Y(0.92)), (x0, p.Y(0.92))], P.SNOW_SKY, BG)
                fill([(x0, p.Y(0.45)), (x1, p.Y(0.45)), (x1, p.Y(0.55)), (x0, p.Y(0.58))], P.SNOW)
                s_([((x0 + x1)/2, p.Y(0.45)), ((x0 + x1)/2, p.Y(0.92))], BG*1.4, g=1.0)
                continue
            bookshelf(xs[i] + 2, xs[i + 1] - 2, fy, min(p.Y(0.98), fy + 230), 5, seed + i)
    shape([(p.x - 5, p.y - 5), (p.x + p.w + 5, p.y - 5), (p.x + p.w + 5, fy), (p.x - 5, fy)], P.FLOOR, BG)
    return fy


def library_desk(x, y, w=150, h=46, stamp=True):
    """the librarian's counter seen from the front; (x, y) = bottom left"""
    sh_([(x, y), (x + w, y), (x + w, y + h), (x, y + h)], P.SHELF)
    for k in range(1, 4): s_([(x + w*k/4, y + 4), (x + w*k/4, y + h - 4)], BG*0.5)
    sh_([(x - 4, y + h), (x + w + 4, y + h), (x + w + 4, y + h + 5), (x - 4, y + h + 5)], P.KRMELEC)
    t = y + h + 5
    for i, g in enumerate((0.5, 0.75, 0.62)):
        shape([(x + 10 + i, t + i*6), (x + 44 - i, t + i*6), (x + 44 - i, t + i*6 + 6), (x + 10 + i, t + i*6 + 6)], g, BG*0.6)
    if stamp:
        shape(rrect(x + w - 40, t, 14, 5, 1), 0.3, BG*0.6)
        shape(rrect(x + w - 36, t + 5, 6, 10, 2), P.SHELF, BG*0.6)
        shape(ell(x + w - 33, t + 16, 4, 3, 12), P.SHELF, BG*0.6)
    shape(rrect(x + w - 20, t, 16, 12, 1.5), 0.85, BG*0.6)
    for k in range(4): s_([(x + w - 18 + k*3.5, t + 12), (x + w - 18 + k*3.5, t + 15)], BG*0.4)


def library_card(x, y, w, h, entries, rot=0):
    """the borrowing card from the pocket inside the book's cover; entries: (name, date, faded)"""
    with T(x, y, 1.0, rot=rot):
        shape([(0, 0), (w, 0), (w, h), (0, h)], 0.97, LINE*0.8)
        hand_text(4, h - 15, w - 8, "VÝPŮJČKY", "SHB", 10)
        stroke([(4, h - 19), (w - 4, h - 19)], LINE*0.4)
        stroke([(w*0.45, 4), (w*0.45, h - 19)], LINE*0.4)
        rh = (h - 24)/max(6, len(entries))
        for i in range(max(6, len(entries))):
            yy = h - 19 - (i + 1)*rh
            stroke([(4, yy), (w - 4, yy)], LINE*0.25, g=0.6)
            if i < len(entries):
                name, date, faded = entries[i]
                g = 0.62 if faded else 0.05
                hand_text(6, yy + rh*0.22, w*0.4, name, "SH", rh*0.6, align="left", g=g)
                hand_text(w*0.45 + 4, yy + rh*0.26, w*0.53, date, "SH", rh*0.46, align="left", g=g)


def knihovnice(x, y, s=1.0, flip=False, left="down", right="down", mood="happy", look=(0, 0), item=None, shadow=True,
               legs="stand"):
    """paní knihovnice, the village librarian: dark bob, teal cardigan, a pencil behind her ear"""
    k = Person(**BABI)
    if shadow: cast_shadow(x, y, 16*s, 2.8*s)
    with T(x, y, s, flip):
        r = k.hr; cy = k.hy
        shape(bez((-r*1.05, cy + r*0.2), (-r*1.3, cy - r*0.6), (-r*1.1, cy - r*1.05), (-r*0.7, cy - r*1.05)) +
              [(r*0.7, cy - r*1.05)] + bez((r*0.7, cy - r*1.05), (r*1.1, cy - r*1.05), (r*1.3, cy - r*0.6), (r*1.05, cy + r*0.2)),
              P.LIB_HAIR)
        draw_legs(k, legs, P.STOCKINGS, boots=P.LIB_SKIRT, boot_top=k.ankle + 3)
        draw_arm(k, -1, left, P.LIB_TOP)
        skirt = [(-12.5, 58), (12.5, 58)] + bez((12.5, 58), (14, 45), (15.5, 32), (16, 22)) + \
                bez((16, 22), (6, 20.5), (-6, 20.5), (-16, 22)) + bez((-16, 22), (-15.5, 32), (-14, 45), (-12.5, 58))
        form(skirt, P.LIB_SKIRT, sdx=-2, sdy=1)
        top = bez((-5, k.sh_y + 2.5), (-9, k.sh_y + 2.2), (-k.sh_w - 1.2, k.sh_y + 0.5), (-k.sh_w - 1.8, k.sh_y - 4)) + \
              bez((-k.sh_w - 1.8, k.sh_y - 4), (-14, 72), (-14, 62), (-13.5, 55)) + [(13.5, 55)] + \
              bez((13.5, 55), (14, 62), (14, 72), (k.sh_w + 1.8, k.sh_y - 4)) + \
              bez((k.sh_w + 1.8, k.sh_y - 4), (k.sh_w + 1.2, k.sh_y + 0.5), (9, k.sh_y + 2.2), (5, k.sh_y + 2.5))
        form(top, P.LIB_TOP, sdx=-2.2, sdy=1.2)
        shape([(-4.5, k.sh_y + 2.4), (4.5, k.sh_y + 2.4), (0, k.sh_y - 7)], 0.95, LINE*0.7)
        stroke([(0, k.sh_y - 7), (0, 55)], LINE*0.6)
        for by in (78, 70, 62): shape(ell(-1.8, by, 0.9, 0.9, 10), 0.95, LINE*0.5)
        h, fa = draw_arm(k, 1, right, P.LIB_TOP)
        if item: item(*h)
        shape([(-2.8, k.hy - k.hr + 2), (2.8, k.hy - k.hr + 2), (3.1, k.sh_y + 0.5), (-3.1, k.sh_y + 0.5)], P.SKIN, 0)
        stroke([(-2.8, k.hy - k.hr + 2.5), (-3.1, k.sh_y + 0.8)], LINE*0.8)
        stroke([(2.8, k.hy - k.hr + 2.5), (3.1, k.sh_y + 0.8)], LINE*0.8)
        shape(head_outline(k), P.SKIN)
        face(0, cy, r, mood, look)
        bob = bez((-r*1.08, cy - r*0.35), (-r*1.2, cy + r*1.25), (r*1.2, cy + r*1.25), (r*1.08, cy - r*0.35)) + \
              bez((r*1.08, cy - r*0.35), (r*0.95, cy + r*0.15), (r*0.85, cy + r*0.5), (r*0.4, cy + r*0.55)) + \
              [(-r*0.6, cy + r*0.45)] + bez((-r*0.6, cy + r*0.45), (-r*0.85, cy + r*0.4), (-r*0.95, cy + r*0.15), (-r*1.08, cy - r*0.35))
        shape(bob, P.LIB_HAIR)
        stroke([(r*0.95, cy + r*0.95), (r*1.45, cy + r*0.25)], LINE*1.6, g=P.PENCIL if hasattr(P, "PENCIL") else 0.7)
        stroke([(r*0.95, cy + r*0.95), (r*1.45, cy + r*0.25)], LINE*0.4)


def jezevcik(x, y, s=1.0, flip=False, pose="stand", mood="happy"):
    """the library's dachshund, who greets everybody. Faces right, feet at y = 0. pose: stand, wag, up (jumps up to
    say hello), sniff"""
    with T(x, y, s, flip):
        rot = 22 if pose == "up" else 0
        if pose == "wag":
            for k in range(3):
                stroke(bez((-31 - k*2.5, 19 + k*3), (-33 - k*2.5, 21 + k*3), (-33 - k*2.5, 24 + k*3), (-32 - k*2.5, 26 + k*3)), LINE*0.5)
        with T(-17, 0, 1.0, rot=rot):
            with T(17, 0, 1.0):
                tail = bez((-21, 15), (-26, 17), (-29, 21), (-30, 26 if pose != "sniff" else 20))
                tube(tail, 2.6, 0.8, P.DACHSHUND, LINE*0.8, sh=0)
                legs = [(-17, 0), (-11.5, 0), (7, 0), (12, 0)] if pose != "up" else [(-17, 0), (-11.5, 0)]
                for i, (lx, ly) in enumerate(legs):
                    g = P.DACHSHUND_DARK if i in (1, 3) else P.DACHSHUND
                    tube([(lx, 10), (lx + 0.5, 1.5)], 3.6, 3.2, g, LINE*0.8, sh=0)
                    shape(ell(lx + 1.6, 1.0, 2.6, 1.2, 12), g, LINE*0.6)
                if pose == "up":
                    for lx, lyy in ((9, 6), (14, 5)):
                        tube([(lx, 10), (lx + 4, lyy)], 3.4, 3.0, P.DACHSHUND, LINE*0.8, sh=0)
                body = bez((-22, 14), (-22, 21), (-12, 20.5), (0, 20)) + bez((0, 20), (8, 20), (13, 19), (15, 15)) + \
                       bez((15, 15), (15, 9), (10, 6.5), (4, 7.5)) + bez((4, 7.5), (-6, 9), (-14, 8), (-19, 8.5)) + \
                       bez((-19, 8.5), (-22, 9), (-22.5, 11), (-22, 14))
                form(body, P.DACHSHUND, sdx=-1.4, sdy=1, sh=0.12)
                stroke(bez((8, 9), (6, 8), (2, 8.5), (-2, 9)), LINE*0.4, g=0.3)
                hy_ = 23 if pose != "sniff" else 15
                hx_ = 18 if pose != "sniff" else 20
                neck = [(10, 17), (16, 13), (hx_ + 2, hy_ - 4), (hx_ - 3, hy_ + 2)]
                shape(neck, P.DACHSHUND, 0)
                head = bez((hx_ - 5, hy_), (hx_ - 5, hy_ + 6), (hx_ + 4, hy_ + 6.5), (hx_ + 6, hy_ + 2)) + \
                       bez((hx_ + 6, hy_ + 2), (hx_ + 10, hy_ + 1), (hx_ + 13, hy_ - 1), (hx_ + 13, hy_ - 3)) + \
                       bez((hx_ + 13, hy_ - 3), (hx_ + 11, hy_ - 5), (hx_ + 4, hy_ - 5), (hx_ - 2, hy_ - 4)) + \
                       bez((hx_ - 2, hy_ - 4), (hx_ - 4, hy_ - 3), (hx_ - 5, hy_ - 2), (hx_ - 5, hy_))
                form(head, P.DACHSHUND, sdx=-1, sdy=0.8, sh=0.1)
                shape(ell(hx_ + 13, hy_ - 2.2, 1.6, 1.3, 12), 0.1, LINE*0.4)
                dot(hx_ + 3.5, hy_ + 1.6, 1.1, 0.0); dot(hx_ + 3.8, hy_ + 2, 0.35, 1.0)
                if mood == "happy":
                    stroke(bez((hx_ + 12, hy_ - 4), (hx_ + 10, hy_ - 5.5), (hx_ + 7, hy_ - 5.5), (hx_ + 5, hy_ - 4.2)), LINE*0.6)
                ear = bez((hx_ - 1, hy_ + 4.5), (hx_ - 6, hy_ + 3), (hx_ - 7, hy_ - 6), (hx_ - 3, hy_ - 9)) + \
                      bez((hx_ - 3, hy_ - 9), (hx_ - 1, hy_ - 7), (hx_ + 1, hy_ - 1), (hx_ + 1.5, hy_ + 3))
                shape(ear, P.DACHSHUND_DARK, LINE*0.8)
                shape([(hx_ - 4.5, hy_ - 4.8), (hx_ + 1.5, hy_ - 6), (hx_ + 1.8, hy_ - 4.3), (hx_ - 4, hy_ - 3)], P.ACCORDION, LINE*0.5)


# ------------------------------------------------------------------ the girls' costumes
def owl_hood(x, y, s=1.0, flip=False):
    """the top of Alica's owl costume: a hood with big owl eyes, a beak and ear tufts"""
    k = Kid(False); r = k.hr; cy = k.hy
    with T(x, y, s, flip):
        for sx in (-1, 1):
            shape([(sx*r*0.55, cy + r*1.45), (sx*r*1.25, cy + r*2.3), (sx*r*1.1, cy + r*1.2)], P.COSTUME_OWL_DARK, LINE*0.8)
        b0, b1, crown, w = cy + r*0.45, cy + r*0.8, cy + r*1.8, r*1.24
        top = bez((-w*0.98, b1), (-w*1.02, crown), (w*1.02, crown), (w*0.98, b1)) + [(w*0.98, b0), (-w*0.98, b0)]
        shape(top, P.COSTUME_OWL)
        for sx in (-1, 1):
            shape(ell(sx*r*0.46, cy + r*1.12, r*0.42, r*0.4, 24), P.COSTUME_OWL_LIGHT, LINE*0.7)
            shape(ell(sx*r*0.46, cy + r*1.12, r*0.24, r*0.24, 20), 1.0, LINE*0.6)
            dot(sx*r*0.43, cy + r*1.1, r*0.12, 0.0); dot(sx*r*0.4, cy + r*1.15, r*0.04, 1.0)
        shape([(-r*0.14, cy + r*1.0), (r*0.14, cy + r*1.0), (0, cy + r*0.68)], P.OWL_BEAK_COSTUME, LINE*0.6)
        shape([(-w, b0), (w, b0), (w, b0 + r*0.22), (-w, b0 + r*0.22)], P.COSTUME_OWL_DARK, LINE*0.7)


def alica_owl(x, y, s=1.0, flip=False, left="down", right="down", mood="happy", look=(0, 0), item=None, legs="stand",
              shadow=True, hood=True):
    """Alica as an owl: brown owl suit, cloth feather wings from her arms to her sides, an owl hood"""
    k = Kid(False)
    with T(x, y, s, flip):
        for side, pose in ((-1, left), (1, right)):
            S, E, H, fa = arm_pts(k, side, pose)
            hip = (side*12.5, 42.0)
            pts = [S, E, H]
            n = 4
            edge = []
            for i in range(n):
                a = (H[0] + (hip[0] - H[0])*i/n, H[1] + (hip[1] - H[1])*i/n)
                b = (H[0] + (hip[0] - H[0])*(i + 1)/n, H[1] + (hip[1] - H[1])*(i + 1)/n)
                mx, my = (a[0] + b[0])/2, (a[1] + b[1])/2
                L = math.hypot(b[0] - a[0], b[1] - a[1]) or 1
                nx, ny = -(b[1] - a[1])/L, (b[0] - a[0])/L
                if (mx + nx - 0)**2 + (my + ny - 60)**2 < (mx - 0)**2 + (my - 60)**2: nx, ny = -nx, -ny
                bump = min(4.0, L*0.5)
                edge += bez(a, (a[0] + nx*bump, a[1] + ny*bump), (b[0] + nx*bump, b[1] + ny*bump), b, 6)[1:]
            wing = pts + edge + [(side*9.5, 60)]
            area = abs(sum(wing[i][0]*wing[(i + 1) % len(wing)][1] - wing[(i + 1) % len(wing)][0]*wing[i][1] for i in range(len(wing))))/2
            if area < 25: continue
            shape(wing, P.COSTUME_OWL_WING, LINE*0.8)
            for i in range(1, n):
                q = edge[i*6 - 1]
                stroke([(S[0]*0.7 + E[0]*0.3, S[1]*0.7 + E[1]*0.3), (q[0]*0.85 + S[0]*0.15, q[1]*0.85 + S[1]*0.15)], LINE*0.4, g=P.COSTUME_OWL_DARK)
    with recolor(ALICA_COAT=P.COSTUME_OWL, ALICA_COLLAR=P.COSTUME_OWL_LIGHT, ALICA_COAT_FOLD=P.COSTUME_OWL_DARK,
                 TIGHTS=P.COSTUME_OWL_LIGHT, TIGHTS_STRIPE=P.COSTUME_OWL_LIGHT):
        alica(x, y, s, flip, left, right, mood, look, item=item, legs=legs, shadow=shadow, satchel=False)
    front = ("front", "hug", "chin", "hush", "lens", "hold")
    if left not in front and right not in front:
        with T(x, y, s, flip):
            for yy, xs in ((66, (-5, 0, 5)), (60, (-7.5, -2.5, 2.5, 7.5)), (54, (-5, 0, 5))):
                for xx in xs:
                    stroke(ell(xx, yy + 1.8, 2.4, 2.0, 8, 200, 340), LINE*0.5, g=P.COSTUME_OWL_DARK)
    if hood: owl_hood(x, y, s, flip)


def bear_ears_hood(x, y, s=1.0, flip=False, who="hanka", g=None, light=None):
    """a bear hood round the face, with two round ears (Hanka's cub costume)"""
    g = P.CUB if g is None else g; light = P.CUB_LIGHT if light is None else light
    k = Kid(True) if who == "hanka" else Kid(False)
    r = k.hr; cy = k.hy
    with T(x, y, s, flip):
        for sx in (-1, 1):
            shape(ell(sx*r*1.05, cy + r*1.1, r*0.46, r*0.46, 20), g, LINE*0.8)
            shape(ell(sx*r*1.05, cy + r*1.06, r*0.24, r*0.24, 16), light, LINE*0.5)
        ring_fill(ell(0, cy + r*0.12, r*1.42, r*1.38, 40), ell(0, cy - r*0.1, r*0.98, r*0.98, 36), g, LINE, LINE*0.8)


def hanka_bear(x, y, s=1.0, flip=False, left="down", right="down", mood="happy", look=(0, 0), item=None, legs="stand",
               shadow=True, monkey=True, torch=False):
    """Hanka as a little bear cub (babička sewed it): brown all over, a hood with round ears, still hugging opička"""
    with recolor(SWEATER=P.CUB, SWEATER_STRIPE=P.CUB, DUNGAREES=P.CUB, DUNGAREE_BUTTON=P.CUB, HANKA_BOOTS=P.CUB_DARK):
        hanka(x, y, s, flip, left, right, mood, look, item=item, legs=legs, shadow=shadow, monkey=monkey, torch=torch)
    bear_ears_hood(x, y, s, flip)


def betka_kitten(x, y, s=1.0, flip=False, **kw):
    """Bětka as a kitten: cat ears on a band, drawn whiskers"""
    kw["hat"] = False
    betka(x, y, s, flip, **kw)
    k = Kid(True); r = k.hr; cy = k.hy
    with T(x, y, s, flip):
        stroke(bez((-r*1.0, cy + r*0.55), (-r*0.6, cy + r*1.15), (r*0.6, cy + r*1.15), (r*1.0, cy + r*0.55)), LINE*1.4, g=P.CAT_EARS)
        for sx in (-1, 1):
            shape([(sx*r*0.95, cy + r*0.75), (sx*r*0.95, cy + r*1.75), (sx*r*0.3, cy + r*1.05)], P.CAT_EARS, LINE*0.7)
            shape([(sx*r*0.84, cy + r*0.95), (sx*r*0.86, cy + r*1.45), (sx*r*0.5, cy + r*1.07)], 0.85, LINE*0.3)
            for dy in (-0.25, -0.42):
                stroke([(sx*r*0.4, cy - r*0.32), (sx*r*1.1, cy + r*dy)], LINE*0.4)
        shape([(-r*0.1, cy - r*0.15), (r*0.1, cy - r*0.15), (0, cy - r*0.28)], 0.2, LINE*0.3)


# ------------------------------------------------------------------ Masopust masks
def bear_head(x, y, r=10.6, rot=0):
    """the bear mask, centred on (x, y); r = the wearer's head radius"""
    with T(x, y, 1.0, rot=rot):
        for sx in (-1, 1):
            shape(ell(sx*r*1.05, r*1.2, r*0.5, r*0.5, 20), P.BEAR_FUR, LINE*0.8)
            shape(ell(sx*r*1.05, r*1.15, r*0.26, r*0.26, 16), P.BEAR_LIGHT, LINE*0.5)
        form(notch(ell(0, 0, r*1.62, r*1.45, 44), r*0.06, 3), P.BEAR_FUR, sdx=-1.4, sdy=1, sh=0.1)
        shape(ell(0, -r*0.5, r*0.78, r*0.58, 30), P.BEAR_LIGHT, LINE*0.8)
        shape(ell(0, -r*0.22, r*0.3, r*0.2, 16), P.BEAR_DARK, LINE*0.6)
        stroke([(0, -r*0.42), (0, -r*0.65)], LINE*0.6)
        stroke(bez((-r*0.35, -r*0.72), (-r*0.15, -r*0.85), (r*0.15, -r*0.85), (r*0.35, -r*0.72)), LINE*0.7)
        for sx in (-1, 1):
            dot(sx*r*0.55, r*0.35, r*0.13, 0.0); dot(sx*r*0.52, r*0.4, r*0.04, 1.0)
            stroke(bez((sx*r*0.8, r*0.62), (sx*r*0.65, r*0.72), (sx*r*0.45, r*0.72), (sx*r*0.32, r*0.62)), LINE*0.6)


def _fur_ticks(x0, x1, y0, y1, seed=3, g=None):
    r = random.Random(seed)
    for _ in range(int((x1 - x0)*(y1 - y0)/40)):
        px, py = r.uniform(x0, x1), r.uniform(y0, y1)
        stroke([(px, py), (px + r.uniform(-1, 1), py - 2.2)], LINE*0.45, g=P.BEAR_DARK if g is None else g)


def medved(x, y, s=1.0, flip=False, head=True, left="down", right="down", mood="happy", look=(0, 0), item=None,
           shadow=True, legs="stand"):
    """děda as the Masopust bear: brown fur all over and the bear mask (head=False: the mask is off, děda's face shows)"""
    with recolor(SHIRT=P.BEAR_FUR, SHIRT_CHECK=P.BEAR_FUR, VEST=P.BEAR_FUR, VEST_BUTTON=P.BEAR_FUR, WATCH_CHAIN=P.BEAR_FUR,
                 BELT=P.BEAR_FUR, TROUSERS=P.BEAR_FUR, DEDA_BOOTS=P.BEAR_DARK):
        deda(x, y, s, flip, left, right, mood, look, item, shadow, legs)
    k = Person(**DEDA)
    with T(x, y, s, flip):
        _fur_ticks(-13, 13, 60, 94, 3)
        _fur_ticks(-8, 8, 12, 50, 4)
        if head:
            bear_head(0, k.hy + k.hr*0.1, k.hr)


def kobyla(x, y, s=1.0, flip=False, left="down", right="front", mood="happy", look=(0, 0), mask=True, shadow=True):
    """Tonda as the Masopust kobyla: a white cloth horse round his waist, a horse head on the front with a star on its
    forehead, a ribbon skirt down to his white sneakers; a paper mask over his eyes"""
    k = Person(**TONDA); r = k.hr; cy = k.hy
    with T(x, y, s, flip):
        for i in range(5):
            stroke(bez((-30, 47), (-34 - i, 42), (-35 - i*1.2, 32), (-33 - i*1.5, 22 + i)), LINE*1.4, g=P.MANE)
    tonda(x, y, s, flip, left, right, mood, look, shadow=shadow)
    with T(x, y, s, flip):
        sk = [(-31, 50)] + bez((-31, 50), (-31, 30), (-31, 15), (-30, 8)) + \
             [(-24, 10), (-17, 7.5), (-10, 10), (-3, 7.5), (4, 10), (11, 7.5), (18, 10), (25, 7.5)] + \
             bez((30, 8), (31, 15), (31, 30), (31, 50))
        form(sk, P.KOBYLA_SKIRT, sdx=-1.6, sdy=0, sh=0.1)
        for i, xx in enumerate(range(-26, 30, 9)):
            stroke([(xx, 46), (xx + 1, 11)], LINE*1.4, g=P.STREAMERS[i % 4])
        form(ell(0, 50, 33, 8, 40), P.KOBYLA, sdx=-1.6, sdy=1, sh=0.1)
        neck = [(20, 52), (30, 48), (45, 78), (36, 84)]
        shape(neck, P.KOBYLA, LINE)
        for i in range(6):
            t = i/6
            mx, my = 20 + (36 - 20)*t, 52 + (84 - 52)*t
            shape(ell(mx - 2.5, my + 1, 3, 2.4, 12, rot=50), P.MANE, LINE*0.5)
        with T(44, 80, 1.0, rot=-35):
            for ex in (-4, -0.5):
                shape([(ex, 5), (ex + 2.2, 11), (ex + 3.6, 4.5)], P.KOBYLA, LINE*0.7)
            head = bez((-6, 4), (-6, 8), (2, 8), (6, 5)) + bez((6, 5), (14, 3), (18, 1), (18, -3)) + \
                   bez((18, -3), (17, -7), (8, -6), (2, -5)) + bez((2, -5), (-4, -4), (-6, -1), (-6, 4))
            form(head, P.KOBYLA, sdx=-1, sdy=0.8, sh=0.1)
            dot(15.5, -1.5, 0.9, 0.2)
            dot(2.5, 2.5, 1.2, 0.0)
            stroke([(4, -5.5), (5, 5)], LINE*0.6, g=P.HAT_BAND)
            star(-1.5, 5.2, 3.2, 1.0, LINE*0.6)
        Sx, Sy = k.sh_w, k.sh_y - 1.5
        _, _, H, _ = arm_pts(k, 1, right)
        stroke([(H[0], H[1]), (49, 76)], LINE*0.6, g=P.HAT_BAND)
        if mask:
            outer = bez((-r*1.05, cy + r*0.15), (-r*1.0, cy + r*0.55), (-r*0.2, cy + r*0.5), (0, cy + r*0.3)) + \
                    bez((0, cy + r*0.3), (r*0.2, cy + r*0.5), (r*1.0, cy + r*0.55), (r*1.05, cy + r*0.15)) + \
                    bez((r*1.05, cy + r*0.15), (r*0.9, cy - r*0.35), (r*0.2, cy - r*0.3), (0, cy - r*0.1)) + \
                    bez((0, cy - r*0.1), (-r*0.2, cy - r*0.3), (-r*0.9, cy - r*0.35), (-r*1.05, cy + r*0.15))
            C.saveState()
            pth = C.beginPath()
            for pl in (outer, ell(-r*0.4, cy + r*0.04, r*0.22, r*0.17, 16), ell(r*0.4, cy + r*0.04, r*0.22, r*0.17, 16)):
                pth.moveTo(*pl[0])
                for q in pl[1:]: pth.lineTo(*q)
                pth.close()
            C.setFillColor(G(P.DOMINO)); C.drawPath(pth, fill=1, stroke=0, fillMode=0)
            C.restoreState()
            stroke(outer, LINE*0.8, closed=True)


def kominik(x, y, s=1.0, flip=False, left="down", right="down", mood="happy", look=(0, 0), item=None, shadow=True,
            stick=True):
    """Věrka as the kominík: all in black, a top hat with a white star on it, soot on her cheeks; her grey plait shows"""
    with recolor(VERKA_COAT=P.KOMINIK, VERKA_SCARF=1.0 if lib.MODE == "bw" else P.SLIP, BRASS=P.KOMINIK):
        verka_old(x, y, s, flip, left, right, mood, look, item, shadow, hat=False, stick=stick)
    r = VERKA["hr"]; cy = VERKA["hy"]
    with T(x, y, s, flip):
        for sx in (-1, 1):
            fill(ell(sx*r*0.55, cy - r*0.4, r*0.2, r*0.13, 14), P.SOOT, 0.55)
        fill(ell(-r*0.1, cy - r*0.75, r*0.14, r*0.1, 12), P.SOOT, 0.5)
        crown = [(-r*0.82, cy + r*0.9), (r*0.82, cy + r*0.9), (r*0.9, cy + r*2.55), (-r*0.9, cy + r*2.55)]
        form(crown, P.TOP_HAT, sdx=-1, sdy=0, sh=0.08)
        shape([(-r*0.84, cy + r*0.9), (r*0.84, cy + r*0.9), (r*0.85, cy + r*1.2), (-r*0.85, cy + r*1.2)], 0.45, LINE*0.6)
        shape(ell(0, cy + r*0.88, r*1.45, r*0.26, 30), P.TOP_HAT, LINE*0.9)
        star(0, cy + r*1.85, r*0.46, 1.0, LINE*0.7)


def baba(x, y, s=1.0, flip=False, mask=True, left="down", right="down", mood="happy", look=(0, 0), item=None, shadow=True,
         nuse=True):
    """babička as the bába s nůší: a tall basket on her back, a red headscarf (her bun makes a bump under it), a shawl
    with a pinking-shear zigzag edge and a star brooch; mask=True: a painted bába mask with a long nose hides her face
    (and her glasses)"""
    k = Person(**BABI); r = k.hr; cy = k.hy
    with T(x, y, s, flip):
        if nuse:
            bk = [(-22, 50), (10, 50), (16, 120), (-28, 120)]
            shape(bk, P.NUSE, LINE)
            C.saveState(); C.clipPath(poly(bk), stroke=0, fill=0)
            for yy in range(53, 120, 5): stroke([(-30, yy), (18, yy)], LINE*0.4, g=0.35)
            for xx in range(-26, 16, 6): stroke([(xx, 50), (xx + (xx + 6)*0.12, 120)], LINE*0.4, g=0.45)
            C.restoreState()
            shape(ell(-6, 120, 22.5, 3.2, 30), P.NUSE, LINE*0.9)
    babicka(x, y, s, flip, left, right, mood, look, item, shadow)
    with T(x, y, s, flip):
        if mask:
            shape(ell(0, cy - r*0.06, r*0.92, r*0.98, 32), P.BABA_MASK, LINE*0.8)
            for sx in (-1, 1):
                fill(ell(sx*r*0.5, cy - r*0.42, r*0.2, r*0.16, 14), P.MASK_CHEEK, 0.8)
                shape(ell(sx*r*0.36, cy + r*0.06, r*0.14, r*0.1, 14), 0.1, LINE*0.4)
                stroke(bez((sx*r*0.58, cy + r*0.3), (sx*r*0.45, cy + r*0.42), (sx*r*0.25, cy + r*0.42), (sx*r*0.12, cy + r*0.3)), LINE*1.0)
            nose = bez((-r*0.08, cy + r*0.12), (r*0.05, cy - r*0.15), (r*0.45, cy - r*0.5), (r*0.68, cy - r*0.62)) + \
                   bez((r*0.68, cy - r*0.62), (r*0.5, cy - r*0.72), (r*0.12, cy - r*0.55), (-r*0.1, cy - r*0.35))
            shape(nose, P.BABA_MASK, LINE*0.7)
            stroke(bez((-r*0.38, cy - r*0.62), (-r*0.15, cy - r*0.82), (r*0.15, cy - r*0.82), (r*0.38, cy - r*0.62)), LINE*0.8)
            dot(-r*0.55, cy - r*0.62, r*0.05, 0.2)
        outer = bez((-r*0.7, cy - r*1.0), (-r*1.3, cy - r*0.6), (-r*1.3, cy + r*0.8), (-r*0.85, cy + r*1.35)) + \
                bez((-r*0.85, cy + r*1.35), (-r*0.6, cy + r*1.7), (-r*0.4, cy + r*2.0), (0, cy + r*2.0)) + \
                bez((0, cy + r*2.0), (r*0.4, cy + r*2.0), (r*0.6, cy + r*1.7), (r*0.85, cy + r*1.35)) + \
                bez((r*0.85, cy + r*1.35), (r*1.3, cy + r*0.8), (r*1.3, cy - r*0.6), (r*0.7, cy - r*1.0)) + \
                bez((r*0.7, cy - r*1.0), (r*0.4, cy - r*1.2), (-r*0.4, cy - r*1.2), (-r*0.7, cy - r*1.0))
        ring_fill(outer, ell(0, cy - r*0.06, r*0.9, r*0.96, 36), P.HEADSCARF, LINE, LINE*0.7)
        for dx, dy in ((-1.05, 0.4), (-0.62, 1.3), (0, 1.62), (0.62, 1.3), (1.05, 0.4), (-1.1, -0.4), (1.1, -0.4), (-0.3, 1.85), (0.3, 1.85)):
            dot(r*dx, cy + r*dy, r*0.07, P.HEADSCARF_DOT)
        stroke(bez((-r*0.35, cy + r*1.55), (-r*0.2, cy + r*1.75), (r*0.2, cy + r*1.75), (r*0.35, cy + r*1.55)), LINE*0.45, g=0.3)
        for sx in (-1, 1):
            shape([(0, cy - r*1.12), (sx*r*0.5, cy - r*1.7), (sx*r*0.15, cy - r*1.75)], P.HEADSCARF, LINE*0.7)
        shape(ell(0, cy - r*1.12, r*0.2, r*0.15, 12), P.HEADSCARF, LINE*0.6)
        sw = k.sh_w
        top_l, top_r = (-sw - 3, k.sh_y + 1.5), (sw + 3, k.sh_y + 1.5)
        side_l, side_r = (-sw - 4.5, k.sh_y - 13), (sw + 4.5, k.sh_y - 13)
        tip = (0, 52)
        shawl = [top_l, (-5, k.sh_y + 3), (5, k.sh_y + 3), top_r, side_r] + zigzag(side_r, tip, 2.4, inward=-1)[1:] + \
                zigzag(tip, side_l, 2.4, inward=-1)[1:]
        form(shawl, P.SHAWL, sdx=-1.6, sdy=1, sh=0.1)
        for t in (0.35, 0.65):
            stroke([(side_l[0]*(1 - t), side_l[1] + (tip[1] - side_l[1])*t + 3), (side_r[0]*(1 - t), side_r[1] + (tip[1] - side_r[1])*t + 3)],
                   LINE*0.35, g=0.3)
        if nuse:
            for sx in (-1, 1):
                stroke([(sx*6.5, k.sh_y + 2.5), (sx*8.5, k.sh_y - 16)], LINE*1.6, g=P.KRMELEC)
        star(0, k.sh_y - 7, 3.6, 1.0, LINE*0.7)
        stroke(ell(0, k.sh_y - 7, 1.1, 1.1, 10), LINE*0.3)


def slameny(x, y, s=1.0, flip=False):
    """the straw man from the Masopust parade: straw bundles tied with string, a straw cone for a head"""
    with T(x, y, s, flip):
        cast_shadow(0, 0, 18, 3)
        for lx in (-6, 6):
            tube([(lx, 58), (lx*1.1, 4)], 9, 8, P.STRAW, LINE*0.9, sh=0.1)
            for yy in (14, 30, 46): stroke([(lx - 4.5, yy), (lx + 4.5, yy - 1)], LINE*0.9, g=P.STRAW_DARK)
        for sx in (-1, 1):
            tube([(sx*14, 96), (sx*20, 74), (sx*21, 54)], 7.5, 6.5, P.STRAW, LINE*0.9, sh=0.1)
            for k_ in range(4):
                stroke([(sx*21 + k_ - 1.5, 54), (sx*21 + k_*1.4 - 2.5, 48)], LINE*0.6, g=P.STRAW_DARK)
        body = bez((-14, 100), (-22, 85), (-21, 66), (-16, 54)) + [(16, 54)] + bez((16, 54), (21, 66), (22, 85), (14, 100))
        form(body, P.STRAW, sdx=-2, sdy=1, sh=0.12)
        r = random.Random(4)
        for _ in range(26):
            px = r.uniform(-17, 17); py = r.uniform(58, 96)
            stroke([(px, py), (px + r.uniform(-1.5, 1.5), py - 6)], LINE*0.4, g=P.STRAW_DARK)
        for yy in (62, 82): stroke(bez((-19, yy), (-8, yy - 2), (8, yy - 2), (19, yy)), LINE*1.0, g=P.STRAW_DARK)
        cone = [(-14, 98), (14, 98), (2, 146), (-2, 146)]
        form(cone, P.STRAW, sdx=-1.5, sdy=0, sh=0.1)
        for k_ in range(-3, 4): stroke([(k_*3.5, 99), (k_*0.6, 140)], LINE*0.4, g=P.STRAW_DARK)
        stroke([(-9, 116), (9, 116)], LINE*1.0, g=P.STRAW_DARK)
        for sx in (-1, 1): shape(ell(sx*4, 108, 2.2, 1.1, 12), 0.15, LINE*0.4)
        for a in (-30, 0, 30):
            ra = math.radians(90 + a)
            stroke([(0, 145), (math.cos(ra)*6, 145 + math.sin(ra)*7)], LINE*0.7, g=P.STRAW_DARK)


def accordion(x, y, s=1.0):
    """a small red accordion, held across the chest; (x, y) = its middle"""
    with T(x, y, s):
        shape(rrect(-15, -8, 6, 16, 1.2), P.ACCORDION, LINE*0.7)
        shape(rrect(9, -8, 6, 16, 1.2), P.ACCORDION, LINE*0.7)
        pts = []
        for i in range(10):
            pts.append((-9 + i*2, 8 if i % 2 == 0 else 6.5))
        bel = pts + [(9, 8), (9, -8)] + [(-9 + i*2, -8 if i % 2 == 0 else -6.5) for i in range(9, -1, -1)]
        shape(bel, 0.85, LINE*0.6)
        for i in range(1, 9): stroke([(-9 + i*2, 7), (-9 + i*2, -7)], LINE*0.3, g=0.4)
        for yy in (-4, 0, 4): dot(12, yy, 0.9, 1.0)


def muzikant(x, y, s=1.0, flip=False, mood="happy", look=(0, 0)):
    """the village musician with an accordion (the sexton, in a ribboned hat)"""
    kostelnik(x, y, s, flip, "front", "front", mood, look, keys=False)
    with T(x, y, s, flip):
        accordion(0, 70, 1.0)
        for i, g in enumerate(P.STREAMERS):
            stroke(bez((6 + i*1.5, 121), (9 + i*2, 114), (8 + i*2.5, 108), (11 + i*2.5, 100)), LINE*1.2, g=g)


def young_bear(x, y, s=1.0, flip=False, head=True, **kw):
    """little Honza 60 years ago, in a homemade bear costume"""
    with recolor(YOUNG_SHIRT=P.BEAR_FUR, SHORTS=P.BEAR_FUR, KNEE_SOCKS=P.BEAR_FUR, KID_SHOES=P.BEAR_DARK):
        young(x, y, s, "deda", flip, **kw)
    if head:
        with T(x, y, s, flip):
            bear_head(0, TONDA["hy"] + TONDA["hr"]*0.1, TONDA["hr"])


# ------------------------------------------------------------------ the village at Masopust
def streamers(x0, x1, y, sag=18, n=14, seed=3):
    """a garland of paper streamers across the street"""
    r = random.Random(seed)
    pts = bez((x0, y), (x0 + (x1 - x0)*0.3, y - sag), (x0 + (x1 - x0)*0.7, y - sag), (x1, y), 40)
    stroke(pts, 0.6, g=0.3)
    for i in range(1, n):
        a = pts[int(i*len(pts)/n)]
        g = P.STREAMERS[i % 4]
        L = r.uniform(14, 24)
        stroke(bez(a, (a[0] + 2, a[1] - L*0.3), (a[0] - 2, a[1] - L*0.6), (a[0] + 1, a[1] - L)), LINE*1.6, g=g)


def masopust_street(p, gy, seed=1, houses=((0.12, 0.85), (0.45, 0.75), (0.82, 0.9)), church_x=None, garlands=1):
    """the village green on Masopust day: snowy houses, the church, streamers across"""
    sky(p, P.SNOW_SKY)
    hills(p, gy + p.h*0.08, 18, P.SNOW_HILL, seed)
    for hx, hs in houses: snowy_house(p.X(hx), gy - 2, hs, smoke=True)
    if church_x is not None: church(p.X(church_x), gy - 2, 0.9)
    snow_field(p, gy, seed)
    for k in range(garlands):
        streamers(p.x - 5, p.x + p.w + 5, p.Y(0.95 - k*0.1), 20, 16, seed + k)
