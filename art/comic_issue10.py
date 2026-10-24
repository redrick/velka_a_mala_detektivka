"""Velká a malá detektivka, issue 10: Záhada ve škole (outline: vault topics/comic-series/issue10-outline)"""
import os, sys
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
import math, random
import lib
import zlib
import osobni
from lib import G, ell, bez, rrect
from style3 import *
from style3 import C
from chars3 import *
from scenes3 import *
from attic import bed_side, blanket_side, kids_drawing
from letter import Panel, caption, bubble, sfx, title, series_title, hand_text, lines_of, thought
from tracks import dog_print
from village import hen, heart_pts
from masopust import koblih
from props_extra import mug
from skola import *
import chars3

W, H = A4
M = 28; GUT = 9; TOP = H - 30
OUT = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                   "comics", "velka_a_mala_detektivka", "10_zahada_ve_skole.pdf")
os.makedirs(os.path.dirname(OUT), exist_ok=True)
cv = canvas.Canvas(OUT, pagesize=A4); lib.set_canvas(cv)
cv.setTitle("Velká a malá detektivka – Případ č. 10: Záhada ve škole")
PAGE = [1]
PROBLEMS = []


# =================================================================== reading-order guard
CUR = []


class Pn(Panel):
    """a panel that remembers its captions and balloons, and on exit checks that they read
    top to bottom, left to right, in the order they were placed, and that none overlap
    each other or a speaker's face"""
    def __init__(self, *a, **kw):
        super().__init__(*a, **kw); self.reads = []; self.heads = []; self.bodies = []; CUR.append(self)

    def __exit__(self, *e):
        CUR.remove(self)
        R = self.reads
        for i in range(1, len(R)):
            a, b = R[i-1], R[i]
            if b["top"] > a["top"] + 12:
                PROBLEMS.append(f"p{PAGE[0]}: '{b['txt'][:28]}' sits ABOVE earlier '{a['txt'][:28]}'")
            elif abs(b["top"] - a["top"]) <= 12 and b["l"] < a["l"]:
                PROBLEMS.append(f"p{PAGE[0]}: '{b['txt'][:28]}' is LEFT of earlier '{a['txt'][:28]}' on the same row")
        for i in range(len(R)):
            for j in range(i+1, len(R)):
                if _hit(R[i], R[j], -2):
                    PROBLEMS.append(f"p{PAGE[0]}: '{R[i]['txt'][:24]}' overlaps '{R[j]['txt'][:24]}'")
            for hb in self.heads:
                if _hit(R[i], hb, -1):
                    PROBLEMS.append(f"p{PAGE[0]}: '{R[i]['txt'][:24]}' covers {hb['txt']}'s face")
        for a in R:
            if a["l"] < self.x - 1 or a["r"] > self.x + self.w + 1 or a["top"] > self.y + self.h + 1 or a["b"] < self.y - 1:
                PROBLEMS.append(f"p{PAGE[0]}: '{a['txt'][:28]}' sticks out of its panel")
        super().__exit__(*e)


def _hit(a, b, m=4):
    return a["l"] < b["r"] + m and b["l"] < a["r"] + m and a["b"] < b["top"] + m and b["b"] < a["top"] + m


def _drawn_w(line, size):
    """how wide letter.hand_line really letters a line: it alternates the two hand fonts and stretches letters a bit"""
    from reportlab.pdfbase import pdfmetrics
    alt = osobni.on("font")
    return sum(max(pdfmetrics.stringWidth(ch, "SH", size), pdfmetrics.stringWidth(ch, "SH2" if alt else "SH", size))*1.035 + 0.2
               for ch in line)


BPAD = 16   # vertical room in a balloon around its text (osobni.balloon_outline fits táta's lopsided shape to its box)


def _geom(txt, ww, size=14.5, whisper=False, k=1.0):
    """lines wrapped at ww; the balloon outline scaled k times round them (centred on 0, 0); each line's baseline
    offset from the centre"""
    import letter as LT
    L = lines_of(txt, "SH", size, ww - 30)
    lead = size*1.15
    s_ = size*(LT.CAPS_K if LT._caps_on("SH") else 1)
    h = (len(L)*lead + BPAD)*k
    w = ww*k
    rx, ry = w/2*1.02, h/2*1.12
    E = LT.wobbly_ellipse(0, 0, rx, ry, zlib.crc32(txt.encode()), kind="whisper" if whisper else "speech")
    cap_h = s_*0.74
    base0 = ((len(L) - 1)*lead - cap_h)/2
    return L, lead, s_, h, rx, ry, E, [base0 - i*lead for i in range(len(L))], cap_h


def _inside(E, px, py):
    c = False; n = len(E)
    for i in range(n):
        (x0, y0), (x1, y1) = E[i], E[(i + 1) % n]
        if (y0 > py) != (y1 > py) and px < x0 + (py - y0)*(x1 - x0)/(y1 - y0):
            c = not c
    return c


def fit_k(txt, ww, size=14.5, whisper=False):
    """how much bigger than letter.bubble's the outline must be for every line, corners included, to sit inside it"""
    k = 1.0
    for _ in range(30):
        L, lead, s_, h, rx, ry, E, bases, cap_h = _geom(txt, ww, size, whisper, k)
        if all(_inside(E, sx*(_drawn_w(ln, s_)/2 + 4), yy)
               for ln, b in zip(L, bases) for sx in (-1, 1) for yy in (b + cap_h + 3, b - 4)):
            return k
        k += 0.03
    return k


def _bubble_h(txt, w, size=14.5, font="SH", k=1.0):
    return (len(lines_of(txt, font, size, w - 30))*size*1.15 + BPAD)*k


def bubble(x, y, w, txt, tx, ty, size=14.5, whisper=False, font="SH", ww=None, k=1.0):
    """letter.bubble with more room round the text and the text truly centred in it (issue 9 on).
    w = the outline's width; ww = the width the text wraps at (w/k)"""
    import letter as LT
    ww = ww or w/k
    L, lead, s_, h, rx, ry, E0, bases, cap_h = _geom(txt, ww, size, whisper, k)
    cx, cy = x + w/2, y - h/2
    E = [(cx + px, cy + py) for px, py in E0]
    ang = math.atan2(ty - cy, tx - cx)
    ex_r = 1/math.sqrt((math.cos(ang)/rx)**2 + (math.sin(ang)/ry)**2)
    if math.hypot(tx - cx, ty - cy) < ex_r + 14:
        tx, ty = cx + math.cos(ang)*(ex_r + 14), cy + math.sin(ang)*(ex_r + 14)
    n = len(E)
    ai = int(((ang % math.tau)/math.tau)*n)
    half = max(3, int(n*0.045))
    i0, i1 = (ai - half) % n, (ai + half) % n
    p0, p1 = E[i0], E[i1]
    mx, my = (p0[0] + p1[0])/2, (p0[1] + p1[1])/2
    nx, ny = -(ty - my), (tx - mx)
    c0 = (p0[0] + (tx - p0[0])*0.55 + nx*0.075, p0[1] + (ty - p0[1])*0.55 + ny*0.075)
    c1 = (p1[0] + (tx - p1[0])*0.55 + nx*0.075, p1[1] + (ty - p1[1])*0.55 + ny*0.075)
    seq = []; k = i1
    while k != i0:
        seq.append(E[k]); k = (k + 1) % n
    seq.append(E[i0])
    outline = seq + bez(p0, c0, c0, (tx, ty), 10)[1:] + bez((tx, ty), c1, c1, p1, 10)[1:]
    fill(outline, 1.0)
    if whisper:
        Pp = lib.resample(outline, 1.0, True)
        mine = osobni.whisper_dashes()
        rd = random.Random(zlib.crc32(txt.encode()))
        dash, gap = 5, 4; i = 0
        while i < len(Pp) - 1:
            if mine:
                dash = max(2, int(mine[0]*(1 + rd.uniform(-1, 1)*mine[1]))); gap = max(2, int(mine[2]))
            seg = Pp[i:i + dash]
            if len(seg) > 1: stroke(seg, 1.1)
            i += dash + gap
    else:
        stroke(outline, 1.25, closed=True)
    r = LT._rng(txt)
    from reportlab.pdfbase import pdfmetrics
    for ln, b in zip(L, bases):
        lw = _drawn_w(ln, s_)
        LT.hand_line(cx - lw/2, cy + b, ln, font, s_, r)
    return h


def say(p, txt, tx, ty, w=150, x=None, y=None, area=None, **kw):
    """speech balloon. Without x/y it places itself in reading order: on the row of the previous
    caption/balloon but to its right, or lower down; never over an earlier balloon or a speaker's
    face; as close above its speaker as that allows. area=(f0, f1) limits it horizontally.
    The width grows until the text fits inside the oval."""
    ww = w
    k = fit_k(txt, ww, whisper=kw.get("whisper", False))
    w = ww*k
    kw.update(ww=ww, k=k)
    if area and w*1.02 > p.X(area[1]) - p.X(area[0]) - 10:
        area = None
    h = _bubble_h(txt, ww, k=k)
    wb = w*1.02   # the balloon outline is a touch wider than w
    if x is None:
        pad = 5
        a0 = max(p.X(area[0]) if area else p.x, p.x + pad)
        a1 = min(p.X(area[1]) if area else p.x + p.w, p.x + p.w - pad)
        want = min(max(tx - wb/2, a0), a1 - wb)
        obst = p.reads + p.heads
        free = lambda l, top: all(not _hit(dict(l=l, r=l + wb, top=top, b=top - h*1.12), o) for o in obst)
        cands = []
        if p.reads:
            last = p.reads[-1]
            for l in sorted({max(last["r"] + 6, want), max(last["r"] + 6, a0)}):
                if l + wb <= a1 and free(l, last["top"]):
                    cands.append((l, last["top"])); break
            top = last["top"] - 14
        else:
            top = p.y + p.h - pad
        top0 = top
        xs_all = sorted(set([want, a0, a1 - wb] + [a0 + k*8 for k in range(int(max(0, a1 - wb - a0)/8) + 1)]),
                        key=lambda v: abs(v - want))
        top = top0
        while top - h*1.12 > p.y + pad:
            hit = next((l for l in xs_all if free(l, top)), None)
            if hit is not None:
                cands.append((hit, top))
            top -= 5
        if not cands:
            cands.append((want, top0))
        base = max(c[1] for c in cands)
        # near the speaker, as high as possible, and above the speaker's head if at all possible
        def body_cover(c):
            l_, t_ = c; b_ = t_ - h*1.12; tot = 0
            for bd in p.bodies:
                ox = max(0, min(l_ + wb, bd["r"]) - max(l_, bd["l"])); oy = max(0, min(t_, bd["top"]) - max(b_, bd["b"]))
                tot += ox*oy/((bd["r"] - bd["l"])*(bd["top"] - bd["b"]))
            return tot
        cost = lambda c: abs(c[0] + wb/2 - tx) + 0.9*(base - c[1]) + (300 if c[1] - h*1.12 < ty - 8 else 0) + 260*body_cover(c)
        l, top = min(cands, key=cost)
        x = l + w*0.01; y = top - h*0.06
    hb = next((b for b in p.heads if b.get("tip") == (tx, ty)), None)
    if hb and y + h*0.06 - h*1.12 < hb["top"]:
        # balloon beside the head, not above it: point at the side of the face, not through it
        left_side = x + w/2 < (hb["l"] + hb["r"])/2
        tx, ty = (hb["l"] - 3 if left_side else hb["r"] + 3), (hb["top"] + hb["b"])/2
    h = bubble(x, y, w, txt, tx, ty, **kw)
    p.reads.append(dict(txt=txt, l=x - w*0.01, r=x + w*1.01, top=y + h*0.06, b=y - h*1.06))


def cap(p, txt, w=None, size=12.5, where="tl"):
    w = w or min(p.w - 16, 230)
    caption(p, txt, w, size, where)
    h = len(lines_of(txt, "SHB", size, w - 16))*size*1.15 + 11
    x = p.x + 6 if where in ("tl", "bl") else p.x + p.w - w - 6
    y = p.y + p.h - h - 6 if where in ("tl", "tr") else p.y + 6
    p.reads.append(dict(txt=txt, l=x, r=x + w, top=y + h, b=y))


HEAD = {"alica": (89.8, 9.8), "hanka": (70.2, 9.6), "deda": (114.8, 10.6), "babi": (101.2, 10.4),
        "tonda": (94, 9.9), "verka": (103, 10.2), "rybar": (118, 11.2), "young": (94, 9.9),
        "kostelnik": (111, 10.4)}


def hd(who, x, y, s, up=1.3):
    """a point just above a figure's head, for balloon tails; also marks the face as keep-clear"""
    hy, hr = HEAD[who]
    tip = (x, y + (hy + hr*up)*s)
    if CUR:
        CUR[-1].heads.append(dict(txt=who, l=x - hr*1.2*s, r=x + hr*1.2*s, top=y + (hy + hr*1.1)*s, b=y + (hy - hr*1.1)*s,
                                  tip=tip))
        CUR[-1].bodies.append(dict(l=x - hr*1.6*s, r=x + hr*1.6*s, top=y + (hy - hr*1.1)*s, b=y))
    return tip


# =================================================================== page helpers
def rows(spec):
    out = []; y = TOP
    for h, cols in spec:
        y -= h; x = M; tw = W - 2*M - GUT*(len(cols)-1)
        for f in cols:
            out.append((x, y, tw*f, h)); x += tw*f + GUT
        y -= GUT
    return out


def page_end():
    hand_text(W/2-20, 18, 40, f"– {PAGE[0]} –", "SH", 10, g=0.35)
    PAGE[0] += 1; cv.showPage()


def bg_fill(p, g, alpha=None):
    fill([(p.x, p.y), (p.x+p.w, p.y), (p.x+p.w, p.y+p.h), (p.x, p.y+p.h)], g, alpha)



# =================================================================== issue 10 helpers
HEAD.update({"mama": (107.6, 10.2), "tata": (122.6, 10.8), "lucie": (110.4, 10.3), "karel": (129.2, 10.6),
             "kid": (89.8, 9.8)})
HID = []   # pages with a hidden crayon, in order; the activity page's answer key is built from it
N_HIDDEN = 10
CRAYONS = (P.CRAYON_RED, P.CRAYON_BLUE, P.CRAYON_GREEN, P.CRAYON_ORANGE, P.CRAYON_BROWN)


def keep_clear(p, x0, y0, x1, y1, what="picture"):
    p.heads.append(dict(txt=what, l=x0, r=x1, top=y1, b=y0))


def hx(who, x, y, s, top=2.0, up=2.1, wide=1.2):
    """hd() for a figure with something tall on its head (a woolly hat, a bun): the tail stops above it"""
    tip = hd(who, x, y, s, up)
    if CUR:
        hy, hr = HEAD[who]
        b = CUR[-1].heads[-1]
        b["top"] = y + (hy + hr*top)*s; b["l"] = x - hr*wide*s; b["r"] = x + hr*wide*s
    return tip


def hm(x, y, s): return hx("mama", x, y, s, 1.85, 2.0, 1.2)        # máma's bun
def hk(x, y, s): return hx("karel", x, y, s, 2.15, 2.3, 1.2)       # pan Karel's woolly hat
def ht(x, y, s): return hd("tata", x, y, s)
def hl(x, y, s): return hd("lucie", x, y, s)
def hc(x, y, s): return hd("kid", x, y, s)
def ha(x, y, s): return hd("alica", x, y, s)
def hh(x, y, s): return hd("hanka", x, y, s)


def pk(x, y, rot=-25):
    """one of the 10 hidden crayons"""
    hidden_pastelka(x, y, 13, rot, CRAYONS[len(HID) % len(CRAYONS)])
    HID.append(PAGE[0])


def J(p, x, y, s, flip=False, pose="stand", **kw):
    """Joey, collar buried in his fur, head kept clear of balloons"""
    joey(x, y, s, flip=flip, pose=pose, collar=False, **kw)
    l, r, b, t = (23, 46, 15, 40) if pose == "sniff" else (18, 41, 36, 61)
    if flip: l, r = -r, -l
    keep_clear(p, x + l*s, y + b*s, x + r*s, y + t*s, "joey")


def inset(p, x, y, w, h, fn, label=None):
    """a round close-up inside a panel (a print seen through the lupa)"""
    shape(ell(x, y, w/2, h/2, 40), 1.0, LINE*1.2)
    C.saveState(); C.clipPath(poly(ell(x, y, w/2 - 1, h/2 - 1, 40)), stroke=0, fill=0)
    fn(x, y)
    C.restoreState()
    keep_clear(p, x - w/2, y - h/2, x + w/2, y + h/2, "inset")
    if label: hand_text(x - w/2, y - h/2 - 16, w, label, "SHB", 11)


def memory_frame(p):
    """soft dashed frame for something that happened before (pan Karel tells)"""
    bg_fill(p, 1.0, 0.25)
    b = 6
    ring = rrect(p.x + b, p.y + b, p.w - 2*b, p.h - 2*b, 22)
    C.saveState()
    pth = C.beginPath(); pth.rect(p.x - 2, p.y - 2, p.w + 4, p.h + 4)
    pth.moveTo(*ring[0])
    for q in ring[1:]: pth.lineTo(*q)
    pth.close()
    C.setFillColor(G(1.0)); C.drawPath(pth, fill=1, stroke=0, fillMode=0); C.restoreState()
    dash = lib.resample(ring, 1.0, True); i = 0
    while i < len(dash) - 1:
        stroke(dash[i:i+6], 0.9, g=0.35); i += 10


def meadow(p, seed, y0=0.5, y1=0.42, far=True):
    """a bit of the school meadow behind the figures (no buildings)"""
    return hillside(p, y0, y1, seed, far=far)


def bedroom_home(p):
    """the girls' bedroom at home, at night; returns the floor line"""
    bg_fill(p, P.BEDROOM_WALL)
    floor_y = p.y + 14
    shape([(p.x - 5, p.y - 5), (p.x + p.w + 5, p.y - 5), (p.x + p.w + 5, floor_y), (p.x - 5, floor_y)], P.FLOOR, BG)
    x0, x1, y0, y1 = p.X(0.06), p.X(0.26), p.Y(0.5), p.Y(0.88)
    shape([(x0 - 5, y0 - 5), (x1 + 5, y0 - 5), (x1 + 5, y1 + 5), (x0 - 5, y1 + 5)], P.DOOR_FRAME, BG)
    shape([(x0, y0), (x1, y0), (x1, y1), (x0, y1)], P.WINTER_NIGHT, BG)
    moon(x0 + (x1 - x0)*0.6, y0 + (y1 - y0)*0.65, 9)
    s_([((x0 + x1)/2, y0), ((x0 + x1)/2, y1)], BG*1.6, g=1.0)
    kids_drawing(p.X(0.4), p.Y(0.75), 36, 26, 4)
    bg_fill(p, 0.0, 0.2)
    return floor_y


def kid_in_bed(fn, hip, x0, x1, top, s=1.2, **kw):
    """bed along the wall, head end on the right, a child sitting up under the blanket"""
    bed_side(x0, x1, top)
    ax = x1 - 30; waist = top + 8; ay = waist - hip*s
    C.saveState()
    C.clipPath(poly([(x0 - 80, top - 10), (x1 + 80, top - 10), (x1 + 80, top + 500), (x0 - 80, top + 500)]), stroke=0, fill=0)
    fn(ax, ay, s, shadow=False, **kw)
    C.restoreState()
    blanket_side(x0, ax + 14, top, waist + 4)
    return ax, ay


def sataa(p, x0=0.04, x1=0.96, floor=0.1, seed=1):
    """the šatna (cloakroom) in the log building: plank walls, a row of hooks with jackets, boots on the floor"""
    planks(p, P.PLANKS, 26, seed, knots=False)
    fy = p.Y(floor)
    shape([(p.x - 5, p.y - 5), (p.x + p.w + 5, p.y - 5), (p.x + p.w + 5, fy), (p.x - 5, fy)], P.FLOOR, BG)
    sh_([(p.X(x0), p.Y(0.78)), (p.X(x1), p.Y(0.78)), (p.X(x1), p.Y(0.81)), (p.X(x0), p.Y(0.81))], P.SHELF)
    r = random.Random(seed)
    cols = (P.JULCA_JACKET, P.BEATKA_JACKET, P.STELLA_JACKET, P.KARELK_JACKET, P.ALICA_COAT)
    for i in range(int((x1 - x0)*p.w/42)):
        hx_ = p.X(x0) + 20 + i*42
        stroke([(hx_, p.Y(0.78)), (hx_, p.Y(0.75))], LINE*1.2)
        if r.random() < 0.6:
            shape(bez((hx_ - 10, p.Y(0.75)), (hx_ - 14, p.Y(0.6)), (hx_ - 12, p.Y(0.48)), (hx_ - 12, p.Y(0.44))) +
                  [(hx_ + 12, p.Y(0.44))] + bez((hx_ + 12, p.Y(0.44)), (hx_ + 12, p.Y(0.48)), (hx_ + 14, p.Y(0.6)), (hx_ + 10, p.Y(0.75))),
                  cols[i % len(cols)], LINE*0.8)
    for i in range(5):
        bx = p.X(0.1) + i*28
        shape([(bx, fy), (bx + 12, fy), (bx + 12, fy + 4), (bx + 4, fy + 6), (bx + 4, fy + 20), (bx, fy + 20)], P.KID_BOOTS, LINE*0.6)
    return fy


def thermometer(x, y, s=1.0, txt="mráz!"):
    with T(x, y, s):
        shape(rrect(-6, -2, 12, 46, 5), 1.0, LINE*0.7)
        stroke([(0, 4), (0, 14)], LINE*2.4, g=P.CRAYON_RED)
        shape(ell(0, 4, 3.2, 3.2, 12), P.CRAYON_RED, LINE*0.5)
        for k in range(8): stroke([(-3, 8 + k*4.5), (-1, 8 + k*4.5)], LINE*0.3)
        hand_text(-20, -16, 40, txt, "SHB", 10)


def beetle(x, y, s=1.0):
    with T(x, y, s):
        for sx in (-1, 1):
            for k in (-3, 0, 3): stroke([(k, 0), (k + sx*1, sx*5)], LINE*0.6)
        shape(ell(0, 0, 6, 3.6, 18), 0.15, LINE*0.6)
        shape(ell(6.5, 0, 2.2, 2, 12), 0.15, LINE*0.5)
        stroke([(0, -3.4), (0, 3.4)], LINE*0.4, g=0.6)


def worm(x, y, s=1.0):
    with T(x, y, s):
        pts = [(i*1.2, math.sin(i*0.5)*2.4) for i in range(18)]
        stroke(pts, LINE*3.4, g=0.0); stroke(pts, LINE*2.2, g=P.TONGUE)


def bowl(x, y, s=1.0):
    with T(x, y, s):
        shape(bez((-10, 6), (-8, -2), (8, -2), (10, 6)) + [(-10, 6)], 0.8, LINE*0.7)
        shape(ell(0, 6, 10, 2.2, 18), P.WATER, LINE*0.5)


def zzz(x, y, s=1.0):
    for i, (dx, dy, k) in enumerate(((0, 0, 1.0), (8, 9, 0.8), (14, 17, 0.6))):
        hand_text(x + dx*s - 10, y + dy*s, 20, "z", "SHB", 13*k*s)


# =================================================================== 1 COVER
def cover():
    with Pn(M, 40, W-2*M, H-80) as p:
        gy = school_garden(p, 0.6, 0.5, 31, school_x=0.5, school_s=0.95, budka_x=0.07, saplings=((0.2, 1.0), (0.82, 0.9)),
                           drops=False)
        kotec(p.X(0.52), p.Y(0.2), 2.2)
        hay_trail([(p.X(0.66), p.Y(0.2)), (p.X(0.75), p.Y(0.12)), (p.X(0.98), p.Y(0.05))], 9, 1.4, 4)
        snowdrops(p.X(0.04), p.Y(0.04), 4, 3, 1.4)
        spoluzak(p.X(0.08), p.Y(0.24), 1.15, "julca", mood="wow", look=(1, 0))
        spoluzak(p.X(0.17), p.Y(0.24), 1.1, "karel", mood="surprised", look=(1, 0))
        spoluzak(p.X(0.9), p.Y(0.24), 1.1, "stella", flip=True, mood="worried", look=(-1, 0))
        J(p, p.X(0.78), p.Y(0.03), 1.6, mood="happy", pose="sniff")
        alica(p.X(0.24), p.Y(0.03), 2.0, mood="think", right="lens", lens=True, look=(1, -0.3))
    box = [(M+34, H-236), (W-M-30, H-232), (W-M-34, H-48), (M+30, H-52)]
    fill([(x+3, y-3) for x, y in box], 0.0, 0.25); fill(box, 1.0)
    for a_, b_ in ((0, 1), (1, 2), (2, 3), (3, 0)): stroke([box[a_], box[b_]], 1.8)
    series_title(W/2, H-98, H-160, 40, 66)
    hand_text(M+40, H-190, W-2*M-80, "Alica, Hanka a Joey", "SHB", 20)
    hand_text(M+40, H-217, W-2*M-80, "Případ č. 10: Záhada ve škole", "SH", 15)
    magnifier(M+82, H-120, ang=-30, r=17)
    morce(W-M-112, H-150, 1.5, who="sisa", flip=True)
    page_end()


# =================================================================== 2 WHO IS WHO
def page_cast():
    with Pn(M, 40, W-2*M, H-80) as p:
        hand_text(p.X(0.05), p.Y(0.95), p.w*0.9, "Kdo je kdo", "SHB", 28)
        cells = [
            ("Alica", "Chodí do 2. třídy.", lambda x, y: alica(x, y, 0.9, mood="happy", right="lens", lens=True)),
            ("Hanka", "Chodí do školky. S opičkou.", lambda x, y: hanka(x, y, 1.1, mood="grin")),
            ("Joey", "Když běží, cinká.", lambda x, y: joey(x, y, 1.2, mood="happy", collar=False)),
            ("Máma a táta", "Táta umí se dřevem.", lambda x, y: (mama(x - 22, y, 0.62, mood="happy"), tata(x + 22, y, 0.6, mood="happy"))),
            ("Paní učitelka Lucie", "Učí v lesní škole.", lambda x, y: lucie(x, y, 0.68, mood="happy")),
            ("Pan Karel", "Školník. Opraví všechno.", lambda x, y: skolnik(x, y, 0.6, mood="happy")),
            ("Julca a Beatka", "Spolužačky.", lambda x, y: (spoluzak(x - 20, y, 0.82, "julca", mood="grin"),
                                                            spoluzak(x + 20, y, 0.82, "beatka", mood="happy"))),
            ("Stella a malý Karel", "Spolužáci.", lambda x, y: (spoluzak(x - 20, y, 0.82, "stella", mood="happy"),
                                                                 spoluzak(x + 20, y, 0.82, "karel", mood="grin"))),
            ("Míša a Šiša", "Školní morčata.", lambda x, y: (morce(x - 22, y + 4, 1.3, who="misa"),
                                                             morce(x + 24, y + 4, 1.3, who="sisa", flip=True))),
        ]
        cw, ch = p.w/3, p.h*0.19
        for i, (name, line, fig) in enumerate(cells):
            cx = p.x + (i % 3)*cw; cy = p.Y(0.9) - (i//3 + 1)*ch
            shape(rrect(cx + 8, cy + 6, cw - 16, ch - 12, 10), 0.97, 1.2)
            fig(cx + cw/2, cy + 46)
            hand_text(cx + 10, cy + 30, cw - 20, name, "SHB", 15)
            hand_text(cx + 10, cy + 14, cw - 20, line, "SH", 11)
        by = p.y + 8; bh = p.Y(0.9) - 3*ch - by - 8
        shape(rrect(p.x + 8, by, p.w - 16, bh, 10), P.PHOTO_BG, 1.2)
        hand_text(p.x + 20, by + bh - 28, p.w*0.6, "Minule:", "SHB", 17, align="left")
        hand_text(p.x + 20, by + bh - 52, p.w*0.6,
                  "Na Masopustu jsme odhalily babičku. Pak skončily prázdniny. Alica řekla: „Snad bude i ve škole nějaká záhada!“",
                  "SH", 13, align="left", lead=17)
        koblih(p.X(0.8), by + bh*0.45, 2.0)
        star(p.X(0.9), by + bh*0.7, 9, P.MASK)
    page_end()


# =================================================================== 3 Monday morning at home
def page_morning():
    R = rows([(260, [1]), (230, [0.5, 0.5]), (260, [1])])
    with Pn(*R[0]) as p:
        fy = home(p, 0.08)
        table(p, 0.3, 0.02, 0.4)
        mug(p.X(0.12), p.Y(0.335), 1.0)
        mama(p.X(0.22), fy, 1.0, outfit="home", hair="down", mood="sleepy", right="front", look=(1, 0),
             item=lambda x, y: mug(x + 2, y - 4, 0.8))
        hanka(p.X(0.42), fy, 1.15, mood="happy", look=(1, 0))
        alica(p.X(0.6), fy, 1.1, mood="happy", look=(1, 0))
        pk(p.X(0.5), p.Y(0.62), 30)
        cap(p, "Pondělí. První den po jarních prázdninách.", w=200, where="tr")
        say(p, "Hani, opička jde do školky taky?", *hd("mama", p.X(0.22), fy, 1.0), w=150, area=(0.0, 0.42))
        say(p, "Jasně!", *hh(p.X(0.42), fy, 1.15), w=70, area=(0.32, 0.6))
    with Pn(*R[1]) as p:
        gy = meadow(p, 41, 0.45, 0.4)
        vito(p.X(0.42), p.Y(0.06), 0.95, back_open=True)
        tata(p.X(0.82), p.Y(0.03), 0.95, flip=True, mood="grin", right="front", left="front", look=(-1, 0),
             item=lambda x, y: box_holes(x - 10, y - 14, 0.5))
        hobliny(p.X(0.8), p.Y(0.06), 0.6, 3)
    with Pn(*R[2]) as p:
        gy = meadow(p, 42, 0.45, 0.4)
        box_holes(p.X(0.5), p.Y(0.1), 1.0)
        stroke([(p.X(0.25), p.Y(0.45)), (p.X(0.33), p.Y(0.5))], LINE, g=0.3)
        alica(p.X(0.25), p.Y(0.03), 1.3, mood="surprised", right="point", look=(1, -0.2))
        say(p, "Tati, co je v té krabici s dírkami?", *ha(p.X(0.25), p.Y(0.03), 1.3), w=140)
    with Pn(*R[3]) as p:
        gy = meadow(p, 43, 0.5, 0.42)
        vito(p.X(0.42), p.Y(0.12), 0.9)
        tata(p.X(0.12), p.Y(0.03), 0.95, mood="happy", right="hush", look=(1, 0))
        alica(p.X(0.86), p.Y(0.03), 1.05, flip=True, mood="think", right="chin", look=(-1, 0))
        J(p, p.X(0.72), p.Y(0.03), 0.9, flip=True, mood="happy")
        say(p, "To je překvapení na zítra. Pro celou školu!", *ht(p.X(0.12), p.Y(0.03), 0.95), w=170, area=(0.0, 0.5))
        say(p, "A proč má dírky?", *ha(p.X(0.86), p.Y(0.03), 1.05), w=100, area=(0.6, 1.0))
    page_end()


# =================================================================== 4 the forest school
def page_school():
    R = rows([(380, [1]), (360, [1])])
    with Pn(*R[0]) as p:
        gy = school_garden(p, 0.52, 0.25, 51, school_x=0.33, school_s=0.85, budka_x=0.03, hutch_x=0.74, hutch_s=1.2,
                           pile_x=0.93, pile_s=0.8, saplings=((0.6, 1.0),), hutch_kw=dict(open_=True, shavings=True))
        hay_trail([(p.X(0.8), gy(0.8) - 8), (p.X(0.86), gy(0.86) - 6), (p.X(0.9), gy(0.9) - 4)], 5, 1.0, 5)
        vito(p.X(0.12), p.Y(0.06), 0.75)
        alica(p.X(0.36), p.Y(0.03), 1.1, mood="happy", right="wave", look=(1, 0))
        spoluzak(p.X(0.48), p.Y(0.03), 1.08, "julca", flip=True, mood="grin", right="wave", look=(-1, 0))
        spoluzak(p.X(0.56), p.Y(0.03), 1.06, "beatka", flip=True, mood="happy", look=(-1, 0))
        pk(p.X(0.97), p.Y(0.05), -40)
        cap(p, "Alica chodí do lesní školy. Na kopci stojí dvě jurty a mezi nimi malý srub.", w=250, where="tl")
        say(p, "Ahoj, Julco! Ahoj, Beatko!", *ha(p.X(0.36), p.Y(0.03), 1.1), w=120, area=(0.15, 0.45))
    with Pn(*R[1]) as p:
        gy = school_garden(p, 0.42, 0.36, 52, school_x=0.5, school_s=1.25, saplings=((0.06, 1.1), (0.94, 1.0)), far=True)
        for i, (fx, txt) in enumerate(((0.26, "JURTA"), (0.5, "SRUB"), (0.74, "JURTA"))):
            hand_text(p.X(fx) - 40, gy(fx) - 4, 80, txt, "SHB", 14)
        hand_text(p.X(0.3), gy(0.5) - 24, p.w*0.4, "(šatna a kumbál pana Karla)", "SH", 11)
        spoluzak(p.X(0.12), p.Y(0.03), 1.0, "stella", mood="happy", right="wave", look=(1, 0))
        spoluzak(p.X(0.88), p.Y(0.03), 1.0, "karel", flip=True, mood="grin", right="wave", look=(-1, 0))
        lucie(p.X(0.72), p.Y(0.03), 0.85, flip=True, mood="happy", look=(-1, 0))
        cap(p, "V jurtách se učí a v kamnech praská oheň. V srubu je šatna a kumbál pana školníka.", w=260, where="tl")
    page_end()


# =================================================================== 5 morning circle
def page_circle():
    R = rows([(280, [1]), (220, [0.5, 0.5]), (250, [1])])
    with Pn(*R[0]) as p:
        fy = yurt_inside(p, 0.08, 0.9)
        for i, (who, fx, fl) in enumerate((("stella", 0.08, False), ("karel", 0.2, False), ("julca", 0.66, True), ("beatka", 0.76, True))):
            spoluzak(p.X(fx), fy, 0.95, who, flip=fl, mood="happy", look=((-1 if fl else 1), 0))
        alica(p.X(0.32), fy, 0.98, mood="happy", look=(1, 0))
        lucie(p.X(0.48), fy, 0.95, mood="worried", look=(0, -0.2))
        cap(p, "Ranní kruh v jurtě.", w=140, where="tl")
        say(p, "Děti, musím vám něco říct. Míša a Šiša nejsou v kotci.", *hl(p.X(0.48), fy, 0.95), w=200, area=(0.25, 0.8))
    with Pn(*R[1]) as p:
        fy = yurt_inside(p, 0.08, None)
        spoluzak(p.X(0.25), fy, 1.05, "stella", mood="sad", right="hug", look=(1, -0.3))
        say(p, "Utekly? Nebo je někdo ukradl?", *hc(p.X(0.25), fy, 1.05), w=130, area=(0.35, 1.0))
    with Pn(*R[2]) as p:
        fy = yurt_inside(p, 0.08, None)
        spoluzak(p.X(0.25), fy, 1.05, "karel", mood="worried", look=(1, 0))
        say(p, "Chudinky. Venku mrzlo!", *hc(p.X(0.25), fy, 1.05), w=110, area=(0.35, 1.0))
    with Pn(*R[3]) as p:
        fy = yurt_inside(p, 0.08, 0.08)
        lucie(p.X(0.7), fy, 0.95, flip=True, mood="happy", right="point", look=(-1, 0))
        alica(p.X(0.25), fy, 1.1, mood="determined", right="up", lens=False, look=(1, 0),
              item=lambda x, y: magnifier(x + 2, y + 8, ang=-20, r=6))
        say(p, "Ale máme přece ve třídě detektivku. Alico?", *hl(p.X(0.7), fy, 0.95), w=170, area=(0.45, 1.0))
        say(p, "Jdeme na to!", *ha(p.X(0.25), fy, 1.1), w=90, area=(0.0, 0.45))
    page_end()


# =================================================================== 6 at the hutch
def page_hutch():
    R = rows([(290, [1]), (220, [0.5, 0.5]), (240, [1])])
    with Pn(*R[0]) as p:
        gy = meadow(p, 61, 0.6, 0.5)
        kotec(p.X(0.55), p.Y(0.18), 2.0, open_=True, shavings=True)
        hay_trail([(p.X(0.82), p.Y(0.15)), (p.X(0.9), p.Y(0.1)), (p.X(1.0), p.Y(0.06))], 5, 1.2, 6)
        alica(p.X(0.12), p.Y(0.03), 1.15, mood="think", right="lens", lens=True, look=(1, 0))
        spoluzak(p.X(0.25), p.Y(0.03), 1.05, "julca", mood="wow", look=(1, 0))
        pk(p.X(0.04), p.Y(0.6), 15)
        cap(p, "U kotce.", w=90, where="tr")
        say(p, "Dvířka jsou otevřená. A západka je ulomená!", *ha(p.X(0.12), p.Y(0.03), 1.15), w=170, area=(0.0, 0.45))
    with Pn(*R[1]) as p:
        bg_fill(p, P.SHELF)
        C.saveState(); C.clipPath(poly([(p.x, p.y), (p.x + p.w, p.y), (p.x + p.w, p.y + p.h), (p.x, p.y + p.h)]), stroke=0, fill=0)
        for k in range(int(p.x), int(p.x + p.w), 12): stroke([(k, p.y), (k, p.y + p.h)], LINE*0.5, g=0.75)
        for k in range(int(p.y), int(p.y + p.h), 12): stroke([(p.x, k), (p.x + p.w, k)], LINE*0.5, g=0.75)
        C.restoreState()
        shape(bez((p.x - 4, p.y), (p.X(0.1), p.Y(0.6)), (p.X(0.9), p.Y(0.62)), (p.x + p.w + 4, p.y)), P.HAY, LINE*0.8)
        rr = random.Random(5)
        for k in range(40):
            xx = p.X(rr.uniform(0.08, 0.92)); yy = p.Y(rr.uniform(0.05, 0.4))
            stroke([(xx, yy), (xx + rr.uniform(-12, 12), yy + rr.uniform(-3, 6))], LINE*0.7, g=P.STRAW_DARK)
        hobliny(p.X(0.5), p.Y(0.3), 3.2, 6, 3)
        cap(p, "V seně jsou hobliny. Kudrnaté dřevo z hoblíku!", w=200, where="tl")
    with Pn(*R[2]) as p:
        bg_fill(p, P.MUD)
        mud_strip(p.x, p.Y(0.4), p.x + p.w, p.Y(0.4), p.h*0.9, 3)
        holinka_print(p.X(0.35), p.Y(0.3), 2.2, -10)
        holinka_print(p.X(0.65), p.Y(0.6), 2.2, -10)
        kid_print(p.X(0.15), p.Y(0.7), 1.6, 20)
        cap(p, "Velké stopy od holínek.", w=170, where="tl")
    with Pn(*R[3]) as p:
        gy = meadow(p, 62, 0.55, 0.5)
        spoluzak(p.X(0.12), p.Y(0.03), 1.05, "beatka", mood="wow", right="point", look=(1, -0.2))
        alica(p.X(0.5), p.Y(0.03), 1.1, flip=True, mood="determined", look=(-1, 0))
        spoluzak(p.X(0.82), p.Y(0.03), 1.05, "stella", flip=True, mood="worried", look=(-1, 0))
        hay_trail([(p.X(0.2), p.Y(0.12)), (p.X(0.35), p.Y(0.08))], 3, 1.0, 7)
        say(p, "Koukejte! Ze dvířek vede stopa ze sena!", *hc(p.X(0.12), p.Y(0.03), 1.05), w=150, area=(0.0, 0.42))
        say(p, "Dolů ke klestí.", *ha(p.X(0.5), p.Y(0.03), 1.1), w=100, area=(0.35, 0.68))
        say(p, "A co když je tam vlk?", *hc(p.X(0.82), p.Y(0.03), 1.05), w=110, area=(0.65, 1.0))
    page_end()


# =================================================================== 7 the list and the box
def page_list():
    R = rows([(270, [1]), (230, [0.5, 0.5]), (250, [1])])
    with Pn(*R[0]) as p:
        bg_fill(p, 0.9)
        notebook_big(p.X(0.06), p.Y(0.06), p.w*0.88, p.h*0.86, "PŘÍPAD Č. 10: KDE JSOU MÍŠA A ŠIŠA?",
                     ["1. Dvířka otevřená, západka ulomená.",
                      "2. Ze dvířek vede dolů stopa ze sena.",
                      "3. Velké stopy od holínek.",
                      "4. V seně jsou hobliny. Kdo dělá se dřevem?",
                      "5. Vlci tu nejsou. Řekla to paní učitelka.",
                      "6. Kde jsou Míša a Šiša teď? Je jim zima?"])
    with Pn(*R[1]) as p:
        fy = sataa(p, seed=4)
        spoluzak(p.X(0.25), fy, 1.2, "julca", mood="wow", right="point", look=(1, -0.3))
        box_holes(p.X(0.72), fy, 0.95)
        hand_text(p.X(0.62), fy + 10, 60, "NESAHAT!", "SHB", 9)
        say(p, "V šatně je krabice s dírkami!", *hc(p.X(0.25), fy, 1.2), w=130)
    with Pn(*R[2]) as p:
        fy = sataa(p, seed=5)
        lucie(p.X(0.22), fy, 0.78, mood="happy", right="hush", look=(1, 0))
        say(p, "Tu tu ráno nechal Alicin táta. Na zítřek. Nesahat!", *hl(p.X(0.22), fy, 0.78), w=150, area=(0.3, 1.0))
    with Pn(*R[3]) as p:
        fy = sataa(p, seed=6)
        box_holes(p.X(0.5), fy, 1.1)
        spoluzak(p.X(0.12), fy, 1.0, "karel", mood="think", right="chin", look=(1, 0))
        alica(p.X(0.82), fy, 1.05, flip=True, mood="worried", look=(-1, 0))
        spoluzak(p.X(0.95), fy, 1.0, "beatka", flip=True, mood="surprised", look=(-1, 0))
        say(p, "Dírky jsou na dýchání. Co když jsou Míša a Šiša tady?", *hc(p.X(0.12), fy, 1.0), w=190, area=(0.0, 0.5))
        say(p, "Táta? To ne…", *ha(p.X(0.82), fy, 1.05), w=90, area=(0.6, 1.0), whisper=True)
    page_end()


# =================================================================== 8 following the hay trail
def page_trail():
    with Pn(M, 40, W-2*M, H-80) as p:
        gy = school_garden(p, 0.88, 0.56, 81, school_x=0.18, school_s=0.55, hutch_x=0.42, hutch_s=0.75, pile_x=None,
                           saplings=((0.62, 0.8), (0.32, 0.7)), hutch_kw=dict(open_=True))
        pts = [(p.X(0.47), gy(0.47) - 6), (p.X(0.55), p.Y(0.48)), (p.X(0.62), p.Y(0.38)), (p.X(0.72), p.Y(0.3)),
               (p.X(0.8), p.Y(0.22)), (p.X(0.84), p.Y(0.12))]
        hay_trail(pts, 16, 1.2, 9)
        klesti(p.X(0.84), p.Y(0.06), 1.8, nest=False)
        kids = [("alica", 0.62, 0.39), ("julca", 0.52, 0.47), ("karel", 0.43, 0.53), ("beatka", 0.35, 0.58),
                ("stella", 0.27, 0.62)]
        for who, fx, fy_ in kids[::-1]:
            if who == "alica":
                alica(p.X(fx), p.Y(fy_), 0.95, mood="determined", right="lens", lens=True, look=(1, -0.4), legs="walk")
            else:
                spoluzak(p.X(fx), p.Y(fy_), 0.92, who, mood="happy", look=(1, -0.2), legs="walk")
        lucie(p.X(0.15), p.Y(0.66), 0.85, mood="happy", look=(1, 0), legs="walk")
        pk(p.X(0.08), p.Y(0.35), 40)
        cap(p, "Celá třída jde po stopě ze sena. Pěkně za sebou, jako kachničky.", w=270, where="tl")
        cap(p, "Stopa vede z kopce dolů. Až k hromadě klestí.", w=230, where="bl")
    page_end()


# =================================================================== 9 the hedgehog
def page_hedgehog():
    R = rows([(300, [1]), (220, [0.5, 0.5]), (230, [1])])
    with Pn(*R[0]) as p:
        gy = meadow(p, 91, 0.7, 0.62)
        klesti(p.X(0.55), p.Y(0.08), 2.4, nest=True)
        alica(p.X(0.12), p.Y(0.03), 1.1, mood="surprised", look=(1, -0.3))
        spoluzak(p.X(0.92), p.Y(0.03), 1.05, "stella", flip=True, mood="worried", right="hug", look=(-1, 0))
        sfx(p.X(0.3), p.Y(0.82), "FUNÍ FUNÍ", 18, -5)
        say(p, "Pst! Něco tam funí!", *ha(p.X(0.12), p.Y(0.03), 1.1), w=100, area=(0.0, 0.32), whisper=True)
    with Pn(*R[1]) as p:
        gy = meadow(p, 92, 0.75, 0.7, far=False)
        jezek(p.X(0.42), p.Y(0.12), 3.2, hay=True)
        cap(p, "Ježek! A na bodlinách má seno.", w=180, where="tl")
    with Pn(*R[2]) as p:
        gy = meadow(p, 93, 0.6, 0.55)
        spoluzak(p.X(0.3), p.Y(0.03), 1.1, "julca", mood="wow", look=(0.5, -0.3))
        say(p, "Ježek je zloděj morčat!", *hc(p.X(0.3), p.Y(0.03), 1.1), w=110, area=(0.4, 1.0))
    with Pn(*R[3]) as p:
        gy = meadow(p, 94, 0.65, 0.6)
        klesti(p.X(0.72), p.Y(0.05), 1.3, nest=True)
        jezek(p.X(0.55), p.Y(0.05), 1.3, hay=True, flip=True)
        lucie(p.X(0.12), p.Y(0.03), 0.9, mood="happy", right="front", look=(1, 0))
        alica(p.X(0.36), p.Y(0.03), 1.05, mood="think", right="chin", look=(1, 0))
        say(p, "Kdepak. Ježek je malý. Morče by neodnesl.", *hl(p.X(0.12), p.Y(0.03), 0.9), w=150, area=(0.0, 0.36))
        say(p, "Ale seno si vzal. Proč?", *ha(p.X(0.36), p.Y(0.03), 1.05), w=110, area=(0.38, 0.75))
        pk(p.X(0.96), p.Y(0.5), 25)
    page_end()


# =================================================================== 10 the hedgehog guide (full page)
def page_guide():
    with Pn(M, 40, W-2*M, H-80, bg=0.97) as p:
        hand_text(p.X(0.04), p.Y(0.955), p.w*0.92, "Ježek na jaře", "SHB", 28)
        hand_text(p.X(0.04), p.Y(0.915), p.w*0.92, "Co Alice řekla paní učitelka. Ukaž prstem na obrázek!", "SH", 13)
        items = [
            ("Od listopadu do března spí. Zimní spánek.", lambda x, y: (jezek(x, y, 1.6, pose="curl"), zzz(x + 22, y + 26))),
            ("Na jaře se probudí. Má velký hlad!", lambda x, y: jezek(x - 8, y, 1.6)),
            ("Jí brouky, žížaly a slimáky. Morčata ne!", lambda x, y: (beetle(x - 16, y + 12, 1.6), worm(x + 4, y + 10, 1.3))),
            ("Pelíšek si staví z listí a ze sena.", lambda x, y: klesti(x, y, 0.4, nest=True)),
            ("Je malý. Morče je větší než on.", lambda x, y: (jezek(x - 20, y, 1.1), morce(x + 20, y, 1.4, who="misa"))),
            ("Nedávej mu mléko. Bolí ho z něj bříško. Jen vodu.", lambda x, y: bowl(x, y + 6, 1.8)),
        ]
        cw, ch = p.w*0.45, p.h*0.25
        for i, (txt, pic) in enumerate(items):
            cx = p.X(0.04) + (i % 2)*(cw + p.w*0.02); cy = p.Y(0.88) - (i//2 + 1)*(ch + 12)
            shape(rrect(cx, cy, cw, ch, 10), 1.0, 1.2)
            hand_text(cx + 8, cy + ch - 22, 30, str(i + 1), "SHB", 16, align="left")
            with T(cx + cw/2, cy + ch*0.36, 2.2):
                pic(0, 0)
            hand_text(cx + 10, cy + 26, cw - 20, txt, "SH", 13, lead=15)
        hand_text(p.X(0.05), p.Y(0.03), p.w*0.9, "Ježek seno nebral pro sebe k jídlu. Stavěl si postýlku!", "SHB", 14)
    page_end()


# =================================================================== 11 the scrap of paper
def page_note():
    R = rows([(260, [1]), (230, [0.5, 0.5]), (260, [1])])
    with Pn(*R[0]) as p:
        gy = meadow(p, 111, 0.7, 0.62)
        klesti(p.X(0.62), p.Y(0.08), 2.0, nest=True, note=True)
        alica(p.X(0.18), p.Y(0.03), 1.15, mood="wow", right="lens", lens=True, look=(1, -0.3))
        say(p, "V pelíšku je papírek!", *ha(p.X(0.18), p.Y(0.03), 1.15), w=110, area=(0.0, 0.4))
    with Pn(*R[1]) as p:
        bg_fill(p, 0.88)
        torn_note(p.X(0.5), p.Y(0.45), 170, 90, ["…ŠA JSOU", "…V TEPLE.", "K."], 15, rot=-3, wet=True)
        keep_clear(p, p.X(0.5) - 90, p.Y(0.45) - 50, p.X(0.5) + 90, p.Y(0.45) + 50, "note")
        cap(p, "Mokrý a roztrhaný.", w=140, where="tl")
    with Pn(*R[2]) as p:
        gy = meadow(p, 112, 0.6, 0.55)
        alica(p.X(0.25), p.Y(0.03), 1.05, mood="think", right="front", look=(0.5, -0.3),
              item=lambda x, y: torn_note(x + 10, y + 4, 34, 22, rot=8, seed=2))
        say(p, "„…ša jsou v teple. K.“", *ha(p.X(0.25), p.Y(0.03), 1.05), w=130, area=(0.35, 1.0))
    with Pn(*R[3]) as p:
        gy = meadow(p, 113, 0.6, 0.55)
        spoluzak(p.X(0.72), p.Y(0.03), 1.15, "karel", flip=True, mood="surprised", look=(-1, 0))
        spoluzak(p.X(0.12), p.Y(0.03), 1.0, "julca", mood="determined", right="point", look=(1, 0))
        spoluzak(p.X(0.26), p.Y(0.03), 1.0, "beatka", mood="surprised", right="point", look=(1, 0))
        say(p, "K. jako Karel!", *hc(p.X(0.12), p.Y(0.03), 1.0), w=100, area=(0.0, 0.3))
        say(p, "Karle, to jsi psal ty?", *hc(p.X(0.26), p.Y(0.03), 1.0), w=110, area=(0.22, 0.5))
        say(p, "Já?!", *hc(p.X(0.72), p.Y(0.03), 1.15), w=60, area=(0.55, 0.95))
    page_end()


# =================================================================== 12 malý Karel
def page_karel():
    R = rows([(260, [1]), (230, [0.5, 0.5]), (260, [1])])
    with Pn(*R[0]) as p:
        gy = meadow(p, 121, 0.6, 0.55)
        spoluzak(p.X(0.25), p.Y(0.03), 1.15, "stella", mood="determined", right="point", look=(1, 0))
        spoluzak(p.X(0.62), p.Y(0.03), 1.15, "karel", flip=True, mood="worried", right="front", look=(-1, 0),
                 item=lambda x, y: hay_wisp(x - 4, y, 1.2, 20))
        say(p, "A v kapse máš seno! Ukaž!", *hc(p.X(0.25), p.Y(0.03), 1.15), w=130, area=(0.0, 0.45))
    with Pn(*R[1]) as p:
        bg_fill(p, P.SPRING_SKY)
        hand_text(p.X(0.08), p.Y(0.8), p.w*0.84, "Bobek", "SHB", 18)
        with T(p.X(0.5), p.Y(0.2), 3.0):
            shape(ell(0, 10, 16, 11, 30), 0.85, LINE)
            shape(ell(15, 18, 8, 7, 20), 0.85, LINE)
            for ex in (12, 17): shape(ell(ex, 32, 2.6, 9, 14, rot=-10), 0.85, LINE*0.8)
            dot(18, 19, 1.1, 0.0); dot(23, 17, 0.9, 0.3)
            shape(ell(-16, 12, 3.5, 3.5, 12), 1.0, LINE*0.6)
        cap(p, "Karlův králík doma.", w=150, where="tl")
    with Pn(*R[2]) as p:
        gy = meadow(p, 122, 0.6, 0.55)
        spoluzak(p.X(0.22), p.Y(0.03), 1.0, "karel", mood="happy", right="up", look=(0.5, 0))
        say(p, "To seno je od mého králíka Bobka!", *hc(p.X(0.22), p.Y(0.03), 1.0), w=140, area=(0.35, 1.0))
    with Pn(*R[3]) as p:
        gy = meadow(p, 123, 0.6, 0.55)
        spoluzak(p.X(0.15), p.Y(0.03), 1.05, "karel", mood="grin", look=(1, 0))
        alica(p.X(0.55), p.Y(0.03), 1.1, flip=True, mood="think", right="chin", look=(-1, 0))
        lucie(p.X(0.85), p.Y(0.03), 0.9, flip=True, mood="happy", look=(-1, 0))
        say(p, "A v neděli jsem byl celý den u babičky. Daleko!", *hc(p.X(0.15), p.Y(0.03), 1.05), w=170, area=(0.0, 0.45))
        say(p, "To je pravda. Karel to nebyl.", *hl(p.X(0.85), p.Y(0.03), 0.9), w=130, area=(0.62, 1.0))
    page_end()


# =================================================================== 13 the boot prints go uphill
def page_prints():
    R = rows([(300, [1]), (210, [0.5, 0.5]), (240, [1])])
    with Pn(*R[0]) as p:
        gy = school_garden(p, 0.92, 0.55, 131, school_x=0.2, school_s=0.65, hutch_x=0.68, hutch_s=0.8, saplings=())
        for k in range(6):
            t = k/5
            xx = p.X(0.62 - t*0.36); yy = gy(0.62 - t*0.36) - 18 - (k % 2)*8
            fill(ell(xx, yy, 14, 7, 18), P.MUD, 0.7)
            holinka_print(xx, yy, 0.7, 75)
        hay_trail([(p.X(0.76), gy(0.76) - 10), (p.X(0.85), p.Y(0.2)), (p.X(0.95), p.Y(0.1))], 6, 0.9, 11)
        alica(p.X(0.55), p.Y(0.03), 1.0, flip=True, mood="determined", right="point", look=(-1, 0.3))
        pk(p.X(0.04), p.Y(0.1), 20)
        cap(p, "Seno vede dolů. Ale holínky jdou nahoru!", w=210, where="br")
    with Pn(*R[1]) as p:
        bg_fill(p, P.LOG)
        for k in range(12): stroke([(p.x, p.Y(k/12)), (p.x + p.w, p.Y(k/12))], LINE*0.6, g=0.3)
        srub(p.X(0.5), p.Y(0.0), 3.0, lock=True)
        keep_clear(p, p.X(0.4), p.Y(0.0), p.X(0.6), p.Y(0.55), "door")
        cap(p, "Až ke dveřím kumbálu. Zamčeno.", w=180, where="tl")
    with Pn(*R[2]) as p:
        gy = meadow(p, 132, 0.62, 0.58)
        lucie(p.X(0.2), p.Y(0.03), 0.75, mood="worried", right="chin", look=(1, 0),
              item=lambda x, y: shape(rrect(x - 3, y - 2, 6, 10, 1.5), P.PHONE, LINE*0.6))
        say(p, "Klíč má jen pan Karel. A telefon nebere.", *hl(p.X(0.2), p.Y(0.03), 0.75), w=150, area=(0.3, 1.0))
    with Pn(*R[3]) as p:
        gy = meadow(p, 133, 0.6, 0.55)
        alica(p.X(0.14), p.Y(0.03), 1.1, mood="think", right="chin", look=(1, 0))
        spoluzak(p.X(0.62), p.Y(0.03), 1.05, "julca", flip=True, mood="happy", look=(-1, 0))
        spoluzak(p.X(0.78), p.Y(0.03), 1.05, "stella", flip=True, mood="happy", look=(-1, 0))
        say(p, "Kdo chodí v takových velkých holínkách?", *ha(p.X(0.14), p.Y(0.03), 1.1), w=160, area=(0.0, 0.5))
        say(p, "Pan Karel je v pondělí v lese. Kácí dříví.", *hc(p.X(0.62), p.Y(0.03), 1.05), w=170, area=(0.45, 1.0))
    page_end()


# =================================================================== 14 pickup: táta and Joey
def page_pickup():
    R = rows([(280, [1]), (220, [0.5, 0.5]), (250, [1])])
    with Pn(*R[0]) as p:
        gy = school_garden(p, 0.75, 0.55, 141, school_x=0.62, school_s=0.65, saplings=((0.18, 0.8),))
        vito(p.X(0.14), p.Y(0.1), 0.8)
        tata(p.X(0.36), p.Y(0.03), 0.95, mood="happy", right="wave", look=(1, 0))
        J(p, p.X(0.55), p.Y(0.03), 1.1, mood="happy")
        for k in range(3): stroke([(p.X(0.5) - 10 - k*8, p.Y(0.15) + k*6), (p.X(0.5) - 24 - k*8, p.Y(0.15) + k*6)], LINE*0.6, g=0.4)
        sfx(p.X(0.62), p.Y(0.45), "CINK CINK", 14, 8)
        alica(p.X(0.88), p.Y(0.03), 1.05, flip=True, mood="happy", right="wave", look=(-1, 0))
        cap(p, "Odpoledne přijel táta. A s ním Joey.", w=190, where="tl")
    with Pn(*R[1]) as p:
        bg_fill(p, P.LOG)
        for k in range(12): stroke([(p.x, p.Y(k/12)), (p.x + p.w, p.Y(k/12))], LINE*0.6, g=0.3)
        srub(p.X(0.72), p.Y(0.0), 2.4, lock=True)
        J(p, p.X(0.25), p.Y(0.03), 1.4, pose="sniff", mood="happy")
        sfx(p.X(0.1), p.Y(0.8), "ČMUCH!", 16, -5)
    with Pn(*R[2]) as p:
        bg_fill(p, P.LOG)
        for k in range(12): stroke([(p.x, p.Y(k/12)), (p.x + p.w, p.Y(k/12))], LINE*0.6, g=0.3)
        J(p, p.X(0.6), p.Y(0.03), 1.5, flip=True, mood="bark")
        sfx(p.X(0.08), p.Y(0.45), "HAF!", 20, -6)
        cap(p, "Joey škrábe na dveře kumbálu.", w=150, where="tl")
    with Pn(*R[3]) as p:
        gy = school_garden(p, 0.78, 0.62, 142, school_x=0.3, school_s=0.6, pile_x=0.92, pile_s=0.6, saplings=())
        alica(p.X(0.55), p.Y(0.03), 1.1, flip=True, mood="happy", right="point", look=(1, 0))
        J(p, p.X(0.3), p.Y(0.03), 1.0, flip=True, mood="happy")
        say(p, "Joey, ne! Ježek je tamhle dole!", *ha(p.X(0.55), p.Y(0.03), 1.1), w=140, area=(0.35, 0.8))
    page_end()


# =================================================================== 15 is it táta?
def page_tata():
    R = rows([(260, [1]), (230, [0.5, 0.5]), (260, [1])])
    with Pn(*R[0]) as p:
        gy = meadow(p, 151, 0.55, 0.5)
        vito(p.X(0.55), p.Y(0.08), 1.0)
        tata(p.X(0.18), p.Y(0.03), 1.0, mood="happy", look=(1, 0))
        alica(p.X(0.88), p.Y(0.03), 1.1, flip=True, mood="think", right="chin", look=(-1, 0))
        say(p, "Tak co, detektivko? Našly jste je?", *ht(p.X(0.18), p.Y(0.03), 1.0), w=150, area=(0.0, 0.45))
        say(p, "Ještě ne.", *ha(p.X(0.88), p.Y(0.03), 1.1), w=80, area=(0.68, 1.0))
    with Pn(*R[1]) as p:
        bg_fill(p, P.TATA_CARGO)
        for k in range(3):
            shape(rrect(p.X(0.12 + k*0.28), p.Y(0.2), p.w*0.22, p.h*0.4, 3), P.TATA_CARGO, LINE)
            stroke([(p.X(0.12 + k*0.28), p.Y(0.52)), (p.X(0.34 + k*0.28), p.Y(0.52))], LINE*0.8)
        hobliny(p.X(0.5), p.Y(0.7), 2.4, 5, 8)
        cap(p, "Hobliny! Na tátových kalhotách.", w=170, where="tl")
    with Pn(*R[2]) as p:
        bg_fill(p, 0.92)
        inset(p, p.X(0.28), p.Y(0.5), 120, 120, lambda x, y: hobliny(x, y, 2.2, 4, 3), "v kotci")
        inset(p, p.X(0.72), p.Y(0.5), 120, 120, lambda x, y: hobliny(x, y, 2.2, 4, 8), "na tátovi")
    with Pn(*R[3]) as p:
        gy = meadow(p, 152, 0.55, 0.5)
        alica(p.X(0.14), p.Y(0.03), 1.1, mood="worried", look=(1, 0))
        tata(p.X(0.7), p.Y(0.03), 1.0, flip=True, mood="grin", right="hush", look=(-1, 0))
        say(p, "Tati… a co bylo v té krabici?", *ha(p.X(0.14), p.Y(0.03), 1.1), w=130, area=(0.0, 0.45))
        say(p, "Nic neprozradím. Zítra je brigáda!", *ht(p.X(0.7), p.Y(0.03), 1.0), w=150, area=(0.45, 1.0))
        pk(p.X(0.95), p.Y(0.6), 35)
    page_end()


# =================================================================== 16 evening at home
def page_evening():
    R = rows([(270, [1]), (220, [0.5, 0.5]), (260, [1])])
    with Pn(*R[0]) as p:
        fy = home(p, 0.08, evening=True)
        table(p, 0.3)
        alica(p.X(0.12), fy, 1.1, mood="determined", right="up", look=(1, 0))
        hanka(p.X(0.32), fy, 1.15, mood="wow", look=(-1, 0))
        mama(p.X(0.58), fy, 1.0, flip=True, outfit="home", mood="happy", look=(-1, 0))
        tata(p.X(0.82), fy, 0.95, flip=True, mood="happy", look=(-1, 0))
        cap(p, "Večer doma. Alica vypráví celý případ.", w=200, where="tr")
        say(p, "…a ježek měl na bodlinách seno!", *ha(p.X(0.12), fy, 1.1), w=140, area=(0.0, 0.4))
    with Pn(*R[1]) as p:
        fy = home(p, 0.08, evening=True)
        hanka(p.X(0.2), fy, 1.15, mood="determined", right="up", look=(1, 0.3))
        say(p, "Já chci taky do té školy! Já chci být u toho!", *hh(p.X(0.2), fy, 1.15), w=150, area=(0.3, 1.0))
    with Pn(*R[2]) as p:
        fy = home(p, 0.08, evening=True)
        mama(p.X(0.2), fy, 0.82, outfit="home", mood="happy", right="chin", look=(1, 0))
        say(p, "V noci na neděli mrzlo. Kdo by tam nechal morčata venku?", *hm(p.X(0.2), fy, 0.82), w=150, area=(0.3, 1.0))
    with Pn(*R[3]) as p:
        fy = home(p, 0.08, evening=True)
        tata(p.X(0.18), fy, 0.95, mood="grin", right="up", look=(1, 0))
        alica(p.X(0.62), fy, 1.1, flip=True, mood="think", look=(-1, 0))
        mama(p.X(0.85), fy, 1.0, flip=True, outfit="home", mood="grin", look=(-1, 0))
        say(p, "A já byl v neděli celý večer doma. Četl jsem vám pohádku!", *ht(p.X(0.18), fy, 0.95), w=180, area=(0.0, 0.5))
        say(p, "To je pravda. Táta to nebyl.", *hm(p.X(0.85), fy, 1.0), w=120, area=(0.65, 1.0))
    page_end()


# =================================================================== 17 the video call
def page_call():
    R = rows([(300, [1]), (210, [0.5, 0.5]), (240, [1])])
    with Pn(*R[0]) as p:
        fy = home(p, 0.08, evening=True)
        alica(p.X(0.3), fy, 1.15, mood="happy", right="front", look=(1, 0.3))
        hanka(p.X(0.5), fy, 1.15, mood="grin", look=(1, 0.3))
        video_call(p.X(0.72), p.Y(0.55), 92, 160, rot=-4)
        keep_clear(p, p.X(0.72) - 50, p.Y(0.55) - 82, p.X(0.72) + 50, p.Y(0.55) + 82, "phone")
        cap(p, "Videohovor s babičkou a dědou.", w=170, where="tl")
        say(p, "Babi, dědo, máme nový případ!", *ha(p.X(0.3), fy, 1.15), w=130, area=(0.0, 0.5))
    with Pn(*R[1]) as p:
        bg_fill(p, P.KITCHEN_WALL)
        deda(p.X(0.22), p.y - 30, 0.95, shadow=False, mood="happy", right="chin", look=(1, 0))
        say(p, "Ježci se teď budí. Hledají seno na pelíšek.", *hd("deda", p.X(0.22), p.y - 30, 0.95), w=140, area=(0.42, 1.0))
    with Pn(*R[2]) as p:
        bg_fill(p, P.KITCHEN_WALL)
        babicka(p.X(0.22), p.y - 20, 1.0, shadow=False, mood="think", right="chin", look=(1, 0))
        say(p, "A ten lístek? Kdo všechno se jmenuje na K.?", *hd("babi", p.X(0.22), p.y - 20, 1.0), w=140, area=(0.42, 1.0))
    with Pn(*R[3]) as p:
        fy = home(p, 0.08, evening=True)
        alica(p.X(0.25), fy, 1.15, mood="think", right="chin", look=(1, 0))
        hanka(p.X(0.7), fy, 1.15, flip=True, mood="grin", look=(-1, 0))
        say(p, "Karel. Ale ten to nebyl.", *ha(p.X(0.25), fy, 1.15), w=110, area=(0.0, 0.5))
        say(p, "Kozel! Kočka! Kukačka!", *hh(p.X(0.7), fy, 1.15), w=110, area=(0.5, 1.0))
    page_end()


# =================================================================== 18 night: Alica thinks
BED_LEN = 185   # a child's bed: a bit longer than Alica (s=1.3) is tall


def page_night():
    R = rows([(380, [1]), (360, [1])])
    with Pn(*R[0]) as p:
        fy = bedroom_home(p)
        ax, ay = kid_in_bed(alica, 45, p.X(0.06), p.X(0.06) + BED_LEN, fy + 40, 1.3, mood="think", look=(1, 0.5))
        thought(p.X(0.5), p.Y(0.95), p.w*0.47, p.h*0.62, ax + 14, ay + 115*1.3, seed=4)
        keep_clear(p, p.X(0.5), p.Y(0.33), p.X(0.97), p.Y(0.95), "thought")
        holinka_print(p.X(0.6), p.Y(0.78), 1.4, -15)
        hobliny(p.X(0.78), p.Y(0.8), 1.4, 4, 2)
        hand_text(p.X(0.86), p.Y(0.74), 40, "K.", "SHB", 26)
        box_holes(p.X(0.62), p.Y(0.5), 0.6)
        stroke([(p.X(0.55), p.Y(0.5)), (p.X(0.7), p.Y(0.65))], LINE*1.6, g=P.CRAYON_RED)
        stroke([(p.X(0.55), p.Y(0.65)), (p.X(0.7), p.Y(0.5))], LINE*1.6, g=P.CRAYON_RED)
        jezek(p.X(0.8), p.Y(0.5), 1.0)
        stroke([(p.X(0.74), p.Y(0.48)), (p.X(0.88), p.Y(0.62))], LINE*1.6, g=P.CRAYON_RED)
        stroke([(p.X(0.74), p.Y(0.62)), (p.X(0.88), p.Y(0.48))], LINE*1.6, g=P.CRAYON_RED)
        cap(p, "V noci nemůže Alica usnout.", w=170, where="tl")
    with Pn(*R[1]) as p:
        fy = bedroom_home(p)
        ax, ay = kid_in_bed(alica, 45, p.X(0.93) - BED_LEN, p.X(0.93), fy + 40, 1.3, mood="sleepy")
        sfx(p.X(0.6), p.Y(0.42), "CHRRR…", 18, -4)
        cap(p, "Holínky, hobliny, K. … Kdo se ještě jmenuje na K.? Zítra to zjistím.", w=250, where="tl")
        zzz(p.X(0.82), p.Y(0.72), 1.4)
    page_end()


# =================================================================== 19 Tuesday: the field day, the box
def page_brigada():
    R = rows([(300, [1]), (210, [0.5, 0.5]), (240, [1])])
    with Pn(*R[0]) as p:
        gy = school_garden(p, 0.82, 0.6, 191, school_x=0.62, school_s=0.65, saplings=((0.2, 0.7),))
        box_holes(p.X(0.4), p.Y(0.06), 1.1, open_=True)
        diely(p.X(0.4), p.Y(0.06) + 42, 0.6)
        tata(p.X(0.18), p.Y(0.03), 1.0, mood="grin", right="up", look=(1, 0))
        lucie(p.X(0.88), p.Y(0.03), 0.92, flip=True, mood="happy", look=(-1, 0))
        alica(p.X(0.66), p.Y(0.03), 1.05, flip=True, mood="wow", look=(-1, 0))
        cap(p, "Úterý. Brigáda! Rodiče přijeli pomáhat.", w=200, where="tr")
        say(p, "Tadá! Nový kotec. Udělal jsem ho v dílně.", *ht(p.X(0.18), p.Y(0.03), 1.0), w=170, area=(0.0, 0.48))
    with Pn(*R[1]) as p:
        bg_fill(p, 0.9)
        diely(p.X(0.5), p.Y(0.55), 1.3)
        box_holes(p.X(0.45), p.Y(0.08), 2.0, open_=True)
        fill(bez((p.X(0.28), p.Y(0.08) + 66), (p.X(0.32), p.Y(0.08) + 84), (p.X(0.5), p.Y(0.08) + 86), (p.X(0.56), p.Y(0.08) + 66)), P.HAY)
        cap(p, "Prkýnka, pletivo a seno.", w=160, where="tl")
    with Pn(*R[2]) as p:
        gy = meadow(p, 192, 0.6, 0.55)
        tata(p.X(0.2), p.Y(0.03), 0.72, mood="happy", right="chin", look=(1, 0))
        say(p, "Seno musí dýchat, jinak zplesniví. Proto dírky.", *ht(p.X(0.2), p.Y(0.03), 0.72), w=150, area=(0.3, 1.0))
    with Pn(*R[3]) as p:
        bg_fill(p, P.MUD)
        mud_strip(p.x, p.Y(0.5), p.x + p.w, p.Y(0.5), p.h*0.9, 5)
        trek_print(p.X(0.25), p.Y(0.45), 2.4, 10)
        holinka_print(p.X(0.65), p.Y(0.45), 2.4, -5)
        hand_text(p.X(0.12), p.Y(0.06), p.w*0.3, "táta", "SHB", 14)
        hand_text(p.X(0.52), p.Y(0.06), p.w*0.3, "u kotce", "SHB", 14)
        pk(p.X(0.9), p.Y(0.22), 10)
        cap(p, "Tátova bota je jiná. Žádné holínky.", w=200, where="tr")
    page_end()


# =================================================================== 20 pan Karel arrives
def page_skolnik():
    R = rows([(300, [1]), (220, [0.5, 0.5]), (230, [1])])
    with Pn(*R[0]) as p:
        gy = school_garden(p, 0.8, 0.6, 201, school_x=0.3, school_s=0.62, saplings=((0.85, 0.7),))
        skolnik(p.X(0.62), p.Y(0.03), 0.92, flip=True, hat=False, mood="happy", right="wave", look=(-1, 0))
        lucie(p.X(0.85), p.Y(0.03), 0.88, flip=True, mood="happy", look=(-1, 0))
        alica(p.X(0.14), p.Y(0.03), 1.05, mood="happy", look=(1, 0))
        cap(p, "Přišel pan Karel, školník. V holínkách.", w=190, where="tl")
        say(p, "Dobrý den, pane Karle!", *ha(p.X(0.14), p.Y(0.03), 1.05), w=110, area=(0.0, 0.4))
        say(p, "Dobrý den, děti! Brr, to je dneska zima na uši.", *hd("karel", p.X(0.62), p.Y(0.03), 0.92), w=170,
            area=(0.4, 1.0))
    with Pn(*R[1]) as p:
        bg_fill(p, P.SPRING_SKY)
        alica(p.X(0.45), p.Y(0.03), 1.6, mood="wow", look=(0.3, 0))
        sfx(p.X(0.08), p.Y(0.8), "KAREL… K.!", 18, -6)
    with Pn(*R[2]) as p:
        bg_fill(p, P.SPRING_SKY)
        inset(p, p.X(0.5), p.Y(0.45), 150, 120, lambda x, y: holinka_print(x, y, 2.4, 80), "holínka")
        cap(p, "Stejné holínky jako u kotce!", w=160, where="tl")
    with Pn(*R[3]) as p:
        gy = meadow(p, 202, 0.6, 0.55)
        alica(p.X(0.14), p.Y(0.03), 1.1, mood="determined", right="point", look=(1, 0))
        skolnik(p.X(0.85), p.Y(0.03), 0.7, flip=True, hat=False, mood="grin", right="chin", look=(-1, 0))
        say(p, "Pane Karle, kde máte čepici? Vy ji nosíte vždycky.", *ha(p.X(0.14), p.Y(0.03), 1.1), w=170, area=(0.0, 0.48))
        say(p, "Půjčil jsem ji někomu, komu byla větší zima.", *hd("karel", p.X(0.85), p.Y(0.03), 0.7), w=160, area=(0.45, 1.0))
    page_end()


# =================================================================== 21 Hanka and the paper bag
def page_uik():
    R = rows([(280, [1]), (210, [0.5, 0.5]), (260, [1])])
    with Pn(*R[0]) as p:
        gy = school_garden(p, 0.8, 0.6, 211, school_x=0.7, school_s=0.6, saplings=())
        vito(p.X(0.18), p.Y(0.1), 0.75)
        mama(p.X(0.42), p.Y(0.03), 1.0, mood="happy", right="wave", look=(1, 0))
        hanka(p.X(0.55), p.Y(0.03), 1.15, mood="grin", right="front", look=(1, 0),
              item=lambda x, y: paper_bag(x + 2, y - 6, 0.8))
        cap(p, "Po školce přivezla máma Hanku.", w=180, where="tr")
        say(p, "Já jsem tady! Kde je ten ježek?", *hh(p.X(0.55), p.Y(0.03), 1.15), w=130, area=(0.38, 0.85))
    with Pn(*R[1]) as p:
        bg_fill(p, P.LOG)
        for k in range(12): stroke([(p.x, p.Y(k/12)), (p.x + p.w, p.Y(k/12))], LINE*0.6, g=0.3)
        srub(p.X(0.75), p.Y(0.0), 2.4, lock=True)
        hanka(p.X(0.28), p.Y(0.03), 1.3, mood="happy", right="front", look=(1, -0.3),
              item=lambda x, y: paper_bag(x + 2, y - 6, 0.9))
        sfx(p.X(0.08), p.Y(0.82), "ŠUST ŠUST", 14, -5)
    with Pn(*R[2]) as p:
        bg_fill(p, P.LOG)
        for k in range(12): stroke([(p.x, p.Y(k/12)), (p.x + p.w, p.Y(k/12))], LINE*0.6, g=0.3)
        srub(p.X(0.5), p.Y(0.0), 2.4, lock=True)
        sfx(p.X(0.15), p.Y(0.75), "UÍÍÍK! UÍÍÍK!", 20, 6)
    with Pn(*R[3]) as p:
        gy = meadow(p, 212, 0.62, 0.58)
        hanka(p.X(0.14), p.Y(0.03), 1.2, mood="wow", right="point", look=(1, 0))
        alica(p.X(0.4), p.Y(0.03), 1.1, flip=True, mood="wow", look=(-1, 0))
        J(p, p.X(0.62), p.Y(0.03), 1.0, mood="bark")
        skolnik(p.X(0.88), p.Y(0.03), 0.86, flip=True, hat=False, mood="grin", right="hush", look=(-1, 0))
        say(p, "Za dveřmi něco píská! Uík!", *hh(p.X(0.14), p.Y(0.03), 1.2), w=120, area=(0.0, 0.38))
        say(p, "Morčata takhle volají, když šustí jídlo!", *ha(p.X(0.4), p.Y(0.03), 1.1), w=150, area=(0.25, 0.68))
    page_end()


# =================================================================== 22 STOP, DETEKTIVE!
def page_stop():
    with Pn(M, 40, W-2*M, H-80, bg=0.95) as p:
        title(p.X(0.5), p.Y(0.92), "STOP, DETEKTIVE!", 44)
        hand_text(p.X(0.05), p.Y(0.86), p.w*0.9, "Kde jsou Míša a Šiša? A kdo je tam schoval?", "SHB", 18)
        cw, ch = p.w*0.3, p.h*0.2
        items = [
            ("velké holínky u kotce (strana 6)", lambda x, y: holinka_print(x, y + 26, 1.1, 0)),
            ("hobliny v seně (strana 6)", lambda x, y: hobliny(x, y + 24, 1.4, 4, 3)),
            ("lístek: „… v teple. K.“ (strana 11)", lambda x, y: torn_note(x, y + 26, 54, 34, ["…V TEPLE.", "K."], 7, seed=4)),
            ("holínky jdou ke kumbálu (strana 13)", lambda x, y: srub(x, y + 2, 0.6)),
            ("Joey škrábe na dveře (strana 14)", lambda x, y: joey(x - 6, y + 4, 0.75, mood="bark", collar=False)),
            ("pan Karel bez čepice (strana 20)", lambda x, y: kulich(x - 4, y + 18, 1.2)),
        ]
        for i, (txt, pic) in enumerate(items):
            cx = p.X(0.04) + (i % 3)*(cw + p.w*0.02); cy = p.Y(0.82) - (i//3 + 1)*(ch + 10)
            shape(rrect(cx, cy, cw, ch, 8), 1.0, 1.2)
            hand_text(cx + 6, cy + ch - 20, 30, str(i + 1), "SHB", 16, align="left")
            with T(cx + cw/2, cy + 36, 1.4):
                pic(0, 0)
            hand_text(cx + 8, cy + 12, cw - 16, txt, "SH", 10.5, lead=12)
        by = p.Y(0.82) - 2*(ch + 10) - 150
        shape(rrect(p.X(0.04), by, p.w*0.92, 140, 8), 1.0, 1.2)
        for i, (fn, lbl) in enumerate(((lambda x, y: klesti(x, y, 0.6, nest=True), "v klestí u ježka"),
                                       (lambda x, y: box_holes(x, y, 0.95), "v krabici s dírkami"),
                                       (lambda x, y: srub(x, y, 0.85), "v kumbálu"))):
            fx = p.X(0.2 + i*0.3)
            fn(fx, by + 30)
            hand_text(fx - 60, by + 8, 120, lbl, "SHB", 12)
        hand_text(p.X(0.05), by - 30, p.w*0.9, "Ukaž prstem! A kdo se ještě jmenuje na K.?", "SH", 14)
        with T(p.X(0.5), p.Y(0.03), 1.0, rot=180):
            hand_text(-p.w*0.45, 0, p.w*0.9, "V kumbálu! Schoval je tam pan Karel, velký Karel. Jeho holínky vedou ke kumbálu,", "SH", 12)
            hand_text(-p.w*0.45, -15, p.w*0.9, "hobliny jsou z jeho ponku a lístek podepsal K. A čepici nemá, protože z ní udělal pelíšek.", "SH", 12)
    page_end()


# =================================================================== 23 the kumbál
def page_kumbal():
    R = rows([(260, [1]), (260, [1]), (230, [0.5, 0.5])])
    with Pn(*R[0]) as p:
        bg_fill(p, P.LOG)
        for k in range(12): stroke([(p.x, p.Y(k/12)), (p.x + p.w, p.Y(k/12))], LINE*0.6, g=0.3)
        srub(p.X(0.5), p.Y(0.0), 2.6, door_open=True, lock=False)
        skolnik(p.X(0.18), p.Y(0.03), 0.9, hat=False, mood="grin", right="front", look=(1, 0),
                item=lambda x, y: key(x + 4, y, 0.5, tag=False))
        hanka(p.X(0.82), p.Y(0.03), 1.15, flip=True, mood="wow", look=(-1, 0))
        say(p, "Tak pojďte. Ale potichu.", *hd("karel", p.X(0.18), p.Y(0.03), 0.9), w=120, area=(0.0, 0.32))
    with Pn(*R[1]) as p:
        fy = kumbal(p, 0.08)
        kulich(p.X(0.42), fy + 6, 2.2, nest=True)
        morce(p.X(0.36), fy + 12, 1.3, who="misa")
        morce(p.X(0.5), fy + 12, 1.2, who="sisa", flip=True)
        hanka(p.X(0.14), fy, 1.2, mood="wow", right="point", look=(1, -0.3))
        pk(p.X(0.92), p.Y(0.92), -30)
        say(p, "Míša a Šiša! V čepici!", *hh(p.X(0.14), fy, 1.2), w=110, area=(0.0, 0.38))
        sfx(p.X(0.55), p.Y(0.6), "UÍK!", 18, 8)
    with Pn(*R[2]) as p:
        fy = kumbal(p, 0.08, window=False, bench=False, seed=3)
        alica(p.X(0.22), fy, 1.0, mood="grin", right="up", look=(0.5, 0))
        say(p, "Našly jsme je! Jsou v teple!", *ha(p.X(0.22), fy, 1.0), w=130, area=(0.32, 1.0))
    with Pn(*R[3]) as p:
        fy = kumbal(p, 0.08, window=False, bench=False, seed=4)
        spoluzak(p.X(0.3), fy, 1.2, "stella", mood="grin", left="up", right="up")
        spoluzak(p.X(0.7), fy, 1.2, "karel", flip=True, mood="grin", right="up")
        sfx(p.X(0.3), p.Y(0.85), "HURÁ!", 20, -5)
    page_end()


# =================================================================== 24 pan Karel tells
def page_tells():
    R = rows([(240, [1]), (250, [0.5, 0.5]), (250, [1])])
    with Pn(*R[0]) as p:
        fy = kumbal(p, 0.08)
        skolnik(p.X(0.62), fy, 0.72, flip=True, hat=False, mood="happy", right="chin", look=(-1, 0))
        alica(p.X(0.4), fy, 0.95, mood="surprised", look=(1, 0))
        say(p, "V neděli večer jsem šel zkontrolovat kotec…", *hd("karel", p.X(0.62), fy, 0.72), w=170, area=(0.5, 1.0))
    with Pn(*R[1]) as p:
        gy = meadow(p, 241, 0.5, 0.45)
        bg_fill(p, 0.0, 0.18)
        kotec(p.X(0.55), p.Y(0.12), 1.4, open_=True)
        thermometer(p.X(0.12), p.Y(0.5), 1.2)
        memory_frame(p)
        cap(p, "Západka byla ulomená. A v noci mělo mrznout.", w=200, where="tl")
    with Pn(*R[2]) as p:
        fy = kumbal(p, 0.08, seed=5)
        bg_fill(p, 0.0, 0.18)
        skolnik(p.X(0.65), fy, 0.92, flip=True, hat=False, mood="happy", right="front", look=(-1, -0.4))
        kulich(p.X(0.32), fy + 6, 1.6, nest=True)
        morce(p.X(0.28), fy + 10, 0.9, who="misa"); morce(p.X(0.38), fy + 10, 0.85, who="sisa", flip=True)
        memory_frame(p)
        cap(p, "Tak jsem je odnesl do tepla. A dal jim svoji čepici.", w=200, where="tl")
    with Pn(*R[3]) as p:
        gy = meadow(p, 242, 0.5, 0.45)
        bg_fill(p, 0.0, 0.2)
        kotec(p.X(0.25), p.Y(0.12), 1.2, open_=True)
        torn_note(p.X(0.58), p.Y(0.6), 60, 30, ["MÍŠA A ŠIŠA JSOU", "U MĚ V TEPLE. K."], 6, rot=-25, torn=False)
        sfx(p.X(0.45), p.Y(0.85), "FŠŠŠ!", 18, -8)
        jezek(p.X(0.82), p.Y(0.08), 1.4, flip=True, hay=True)
        memory_frame(p)
        cap(p, "Na kotec dal lístek. Ale vítr ho sfoukl… a ježek si ho odnesl i se senem do pelíšku.", w=260, where="tl")
    page_end()


# =================================================================== 25 building the new hutch
def page_build():
    with Pn(M, 40, W-2*M, H-80) as p:
        gy = school_garden(p, 0.82, 0.7, 251, school_x=0.5, school_s=0.6, saplings=((0.1, 0.7), (0.9, 0.7)))
        diely(p.X(0.5), p.Y(0.6), 1.4)
        novy_kotec(p.X(0.5), p.Y(0.24), 2.4, misa=False, sisa=False, paint=False)
        tata(p.X(0.14), p.Y(0.2), 1.0, mood="grin", right="front", look=(1, 0),
             item=lambda x, y: (saw(x + 2, y - 2, 0.9)))
        skolnik(p.X(0.86), p.Y(0.2), 0.95, flip=True, hat=False, mood="happy", right="up", look=(-1, 0),
                item=lambda x, y: hammer(x, y))
        mama(p.X(0.3), p.Y(0.02), 1.0, mood="happy", right="front", look=(1, 0.3),
             item=lambda x, y: stroke([(x, y), (x + 8, y + 10)], LINE*1.6, g=P.NAME_PAINT))
        lucie(p.X(0.7), p.Y(0.02), 0.95, flip=True, mood="happy", right="front", look=(-1, 0.3))
        alica(p.X(0.43), p.Y(0.02), 1.05, mood="grin", right="up", look=(0.5, 0.3),
              item=lambda x, y: hay_wisp(x, y + 4, 1.2))
        hanka(p.X(0.55), p.Y(0.02), 1.1, flip=True, mood="grin", look=(-1, 0.3))
        spoluzak(p.X(0.06), p.Y(0.02), 0.95, "julca", mood="grin", right="up")
        spoluzak(p.X(0.95), p.Y(0.02), 0.95, "beatka", flip=True, mood="grin", right="up")
        J(p, p.X(0.2), p.Y(0.02), 1.0, mood="happy")
        sfx(p.X(0.06), p.Y(0.6), "ŤUK ŤUK!", 18, -6)
        sfx(p.X(0.78), p.Y(0.62), "VRZ VRZ!", 16, 6)
        pk(p.X(0.92), p.Y(0.42), -20)
        cap(p, "A pak se stavělo. Táta řeže, pan Karel tluče, máma s paní učitelkou malují a děti nosí seno.", w=280, where="tl")
        cap(p, "Joey dohlíží.", w=110, where="br")
    page_end()


# =================================================================== 26 moving in, the end
def page_end10():
    R = rows([(270, [1]), (230, [0.5, 0.5]), (250, [1])])
    with Pn(*R[0]) as p:
        gy = school_garden(p, 0.7, 0.55, 261, school_x=None, pile_x=0.88, pile_s=1.0, saplings=((0.08, 0.7),),
                           pile_kw=dict(nest=True))
        novy_kotec(p.X(0.42), p.Y(0.08), 1.7)
        fill(bez((p.X(0.66), p.Y(0.05)), (p.X(0.68), p.Y(0.16)), (p.X(0.8), p.Y(0.16)), (p.X(0.82), p.Y(0.05))), P.HAY)
        jezek(p.X(0.76), p.Y(0.05), 1.4, flip=True)
        cap(p, "Míša a Šiša mají nový kotec. Se západkou, se schůdky a s půdou na slámu. A ježek dostal vlastní hromádku sena.", w=260, where="tl")
    with Pn(*R[1]) as p:
        gy = meadow(p, 262, 0.6, 0.55)
        skolnik(p.X(0.22), p.Y(0.03), 0.75, hat=True, mood="grin", right="up", look=(0.5, 0))
        say(p, "A čepici mám zase já!", *hk(p.X(0.22), p.Y(0.03), 0.75), w=110, area=(0.35, 1.0))
    with Pn(*R[2]) as p:
        gy = meadow(p, 263, 0.6, 0.55)
        spoluzak(p.X(0.22), p.Y(0.03), 1.0, "karel", mood="grin", look=(0.5, 0))
        say(p, "Malý Karel a velký Karel. Oba v pohodě!", *hc(p.X(0.22), p.Y(0.03), 1.0), w=140, area=(0.32, 1.0))
    with Pn(*R[3]) as p:
        fy = home(p, 0.08, evening=True)
        table(p, 0.3)
        notebook(p.X(0.3), p.Y(0.34), 1.3)
        alica(p.X(0.5), fy, 1.15, mood="happy", right="front", look=(-1, -0.4))
        hanka(p.X(0.68), fy, 1.1, flip=True, mood="sleepy", right="hug")
        mama(p.X(0.88), fy, 1.0, flip=True, outfit="home", mood="happy", look=(-1, 0))
        cap(p, "Případ č. 10 vyřešen. Za dva týdny jsou Velikonoce. Jedeme na chalupu!", w=230, where="tl")
        say(p, "Tam taky něco najdeme!", *hh(p.X(0.68), fy, 1.1), w=110, area=(0.55, 1.0))
    page_end()


# =================================================================== 27 activity (no pencil)
def page_quiz():
    with Pn(M, 40, W-2*M, H-80) as p:
        box = [(p.X(0.05), p.Y(0.905)), (p.X(0.95), p.Y(0.91)), (p.X(0.95), p.Y(0.905)+54), (p.X(0.05), p.Y(0.905)+52)]
        fill(box, 0.92)
        for a_, b_ in ((0, 1), (1, 2), (2, 3), (3, 0)): stroke([box[a_], box[b_]], 1.5)
        hand_text(p.X(0.05), p.Y(0.905)+18, p.w*0.9, "Detektivní zápisník", "SHB", 26)
        hand_text(p.X(0.05), p.Y(0.865), p.w*0.9, "Zase bez tužky. Stačí prst a dobré oči!", "SH", 13)
        hand_text(p.X(0.05), p.Y(0.82), p.w*0.9, "1. Čí je stopa? Ukaž prstem, co k sobě patří.", "SHB", 15, align="left")
        prints = [lambda x, y: holinka_print(x, y, 1.2, 0), lambda x, y: trek_print(x, y, 1.2, 0),
                  lambda x, y: kid_print(x, y, 1.6, 0), lambda x, y: dog_print(x, y, 1.6)]
        whos = [lambda x, y: tata(x, y, 0.42, shadow=False, mood="happy"), lambda x, y: joey(x - 6, y, 0.8, shadow=False, collar=False),
                lambda x, y: skolnik(x, y, 0.4, shadow=False, mood="happy"), lambda x, y: alica(x, y, 0.55, shadow=False, mood="happy")]
        y1 = p.Y(0.7)
        for i in range(4):
            prints[i](p.X(0.14 + i*0.24), y1)
            hand_text(p.X(0.14 + i*0.24) - 30, y1 - 34, 60, "ABCD"[i], "SHB", 14)
            whos[i](p.X(0.14 + i*0.24), y1 - 120)
            hand_text(p.X(0.14 + i*0.24) - 30, y1 - 136, 60, str(i + 1), "SHB", 14)
        y2 = y1 - 160
        hand_text(p.X(0.05), y2, p.w*0.9, "2. Která je Míša a která Šiša? Šiša má na hlavě rozcuch.", "SHB", 15, align="left")
        morce(p.X(0.3), y2 - 70, 2.0, who="sisa"); morce(p.X(0.65), y2 - 70, 2.0, who="misa", flip=True)
        y3 = y2 - 100
        hand_text(p.X(0.05), y3, p.w*0.9, "3. Povídejte si:", "SHB", 15, align="left")
        qs = ["Proč pan Karel odnesl morčata do kumbálu?", "Proč měla tátova krabice dírky?",
              "Proč ježek bral seno?", "Proč morčata pískala, když Hanka šustila sáčkem?"]
        for i, q in enumerate(qs):
            hand_text(p.X(0.1), y3 - 22 - i*20, p.w*0.85, "– " + q, "SH", 14, align="left")
        y4 = y3 - 22 - len(qs)*20 - 16
        hidden_pastelka(p.X(0.09), y4 - 2, 13, -20)          # the legend: not one of the hidden ten
        hand_text(p.X(0.15), y4 - 4, p.w*0.8,
                  f"Ve škole se rozkutálelo {N_HIDDEN} pastelek, jako je tahle (ta se nepočítá). Najdeš je všechny?",
                  "SHB", 14, align="left", lead=18)
        pages = ", ".join(map(str, HID[:-1])) + " a " + str(HID[-1]) if HID else ""
        with T(p.X(0.5), p.Y(0.015), 1.0, rot=180):
            hand_text(-p.w*0.45, 0, p.w*0.9, f"Pastelky jsou na stranách {pages}.", "SH", 10)
            hand_text(-p.w*0.45, -13, p.w*0.9, "Stopy: A3 (pan Karel), B1 (táta), C4 (Alica), D2 (Joey). Vlevo je Šiša, vpravo Míša.", "SH", 10)
    page_end()


# =================================================================== 28 back cover: next time
def back_cover():
    with Pn(M, 40, W-2*M, H-80, bg=0.95) as p:
        hand_text(p.X(0.1), p.Y(0.93), p.w*0.8, "Příště v sešitě č. 11:", "SHB", 20)
        title(p.X(0.5), p.Y(0.84), "KAM MIZÍ VAJÍČKA?", 34)
        with Pn(p.X(0.08), p.Y(0.3), p.w*0.84, p.h*0.48, bg=0.9) as q:
            gy = q.Y(0.4)
            sky(q, P.SPRING_SKY)
            hills(q, gy + q.h*0.08, 16, 0.87, 5)
            house(q.X(0.75), gy - 4, 0.9)
            ground(q, gy, P.SPRING_GRASS)
            for i in range(3):
                shape(ell(q.X(0.38) + i*30, q.Y(0.14) + (i % 2)*8, 10, 13, 20), 0.97, LINE*0.8)
            hand_text(q.X(0.6), q.Y(0.22), q.w*0.18, "???", "SHB", 30)
            snowdrops(q.X(0.05), q.Y(0.05), 4, 2, 1.3)
        hand_text(p.X(0.1), p.Y(0.24), p.w*0.8, "Velikonoce na chalupě. Babička chce barvit vajíčka, ale vajíčka začnou mizet!", "SH", 16, lead=21)
        hand_text(p.X(0.1), p.Y(0.13), p.w*0.8, "Kam se ztrácejí?", "SHB", 16)
        hand_text(p.X(0.1), p.Y(0.015), p.w*0.8, "Velká a malá detektivka – sešit č. 10", "SH", 13, g=0.35)
    PAGE[0] += 1; cv.showPage()


cover(); page_cast(); page_morning(); page_school(); page_circle(); page_hutch(); page_list(); page_trail()
page_hedgehog(); page_guide(); page_note(); page_karel(); page_prints(); page_pickup(); page_tata(); page_evening()
page_call(); page_night(); page_brigada(); page_skolnik(); page_uik(); page_stop(); page_kumbal(); page_tells()
page_build(); page_end10(); page_quiz(); back_cover()
cv.save()
print("ok", PAGE[0] - 1, "pages")
import letter
if letter.MISSING: PROBLEMS.append("no glyph in the font for: " + " ".join(sorted(letter.MISSING)))
if len(HID) != N_HIDDEN: PROBLEMS.append(f"{len(HID)} hidden crayons drawn, the notebook promises {N_HIDDEN}")
for pr in PROBLEMS: print("ORDER/LAYOUT:", pr)
if PROBLEMS: sys.exit(1)
