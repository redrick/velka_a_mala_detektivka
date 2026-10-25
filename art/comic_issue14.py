"""Velká a malá detektivka, issue 14: Poklad na hradě (outline: vault topics/comic-series/issue14-outline)"""
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
from letter import Panel, caption, bubble, sfx, title, series_title, hand_text, lines_of, thought, shout
from pond import verka_old, rybar, treasure_tin, club_photo, badge, torch_beam
from winter import betka
from attic import ladder, young, owl, feather, pellet
from potok import louka, ve_spacaku, hrad_kresba, bobr, glow
from tocnik import *
from tocnik import _panel_fill, _rect
import chars3

W, H = A4
M = 28; GUT = 9; TOP = H - 30
OUT = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                   "comics", "velka_a_mala_detektivka", "14_poklad_na_hrade.pdf")
os.makedirs(os.path.dirname(OUT), exist_ok=True)
cv = canvas.Canvas(OUT, pagesize=A4); lib.set_canvas(cv)
cv.setTitle("Velká a malá detektivka – Případ č. 14: Poklad na hradě")
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



# =================================================================== issue 14 helpers
HEAD.update({"betka": (70.2, 9.6), "franta": (118, 11.2), "kastel": (109.4, 10.3)})
HID = []   # pages with a hidden key, in order; the activity page's answer key is built from it
N_HIDDEN = 10


def keep_clear(p, x0, y0, x1, y1, what="picture"):
    p.heads.append(dict(txt=what, l=x0, r=x1, top=y1, b=y0))


def hx(who, x, y, s, top=2.0, up=2.1, wide=1.2):
    """hd() for a figure with something tall on its head (a bun, a hat): the tail stops above it"""
    tip = hd(who, x, y, s, up)
    if CUR:
        hy, hr = HEAD[who]
        b = CUR[-1].heads[-1]
        b["top"] = y + (hy + hr*top)*s; b["l"] = x - hr*wide*s; b["r"] = x + hr*wide*s
    return tip


def hv(x, y, s): return hx("verka", x, y, s, 2.2, 2.4, 2.0)        # Věrka's straw hat
def hf(x, y, s): return hx("franta", x, y, s, 1.9, 2.1, 1.6)       # Franta's bucket hat
def hk(x, y, s): return hx("kastel", x, y, s, 1.4, 1.6, 1.3)       # the kastelánka's bob
def ha(x, y, s): return hd("alica", x, y, s)
def hh(x, y, s): return hd("hanka", x, y, s)
def hdd(x, y, s): return hd("deda", x, y, s)
def htd(x, y, s): return hd("tonda", x, y, s)
def hbe(x, y, s): return hd("betka", x, y, s)
def hyv(x, y, s): return hd("young", x, y, s)


def kl(x, y, rot=-20):
    """one of the 10 hidden keys"""
    hidden_klic(x, y, 13, rot)
    HID.append(PAGE[0])


def J(p, x, y, s, flip=False, pose="stand", **kw):
    """Joey, collar buried in his fur, head kept clear of balloons"""
    joey(x, y, s, flip=flip, pose=pose, collar=False, **kw)
    l, r, b, t = (23, 46, 15, 40) if pose == "sniff" else (18, 41, 36, 61)
    if flip: l, r = -r, -l
    keep_clear(p, x + l*s, y + b*s, x + r*s, y + t*s, "joey")


def inset(p, x, y, w, h, fn, label=None, g=1.0):
    """a round close-up inside a panel (seen through the lupa)"""
    shape(ell(x, y, w/2, h/2, 40), g, LINE*1.2)
    C.saveState(); C.clipPath(poly(ell(x, y, w/2 - 1, h/2 - 1, 40)), stroke=0, fill=0)
    fn(x, y)
    C.restoreState()
    keep_clear(p, x - w/2, y - h/2, x + w/2, y + h/2, "inset")
    if label: hand_text(x - w/2, y - h/2 - 16, w, label, "SHB", 11)


def stul(x, y, w=200, s=1.0):
    """the garden table at the chalupa"""
    shape(_rect(x - w/2, y + 40*s, x + w/2, y + 46*s), P.TABLE, LINE)
    for lx in (x - w/2 + 10, x + w/2 - 14):
        shape(_rect(lx, y, lx + 4*s, y + 40*s), P.TABLE, LINE*0.8)


def chalupa_garden(p, gy_f=0.5, seed=1):
    """the garden behind the chalupa in June"""
    gy = louka(p, gy_f, seed, forest=True, clouds=True)
    return gy


def spin_lines(x, y, s=1.0):
    """motion arcs round somebody spinning"""
    for k, (rx, ry, a0, a1) in enumerate(((36, 12, 200, 340), (40, 14, 20, 160), (30, 10, 190, 330))):
        stroke(ell(x, y + (30 + k*22)*s, rx*s, ry*s, 30, a0, a1), LINE*0.9, g=0.25)


def railing(p, y0, y1, g=None):
    """a wooden railing across the front of the panel (people stand behind it)"""
    g = g if g is not None else P.CASTLE_WOOD
    for k in range(int(p.w/60) + 2):
        px = p.x + 20 + k*60
        shape(_rect(px, p.y - 5, px + 7, y1 + 4), g, LINE*0.8)
    for yy in (y0, y1):
        shape(_rect(p.x - 5, yy - 4, p.x + p.w + 5, yy + 4), g, LINE*0.9)


def stairs(p, seed=3):
    """the stone stairs inside the tower: steps climbing to the right, a slit window"""
    _panel_fill(p, P.CASTLE_WALL_DARK)
    stone_wall(p.x - 5, p.y - 5, p.x + p.w + 5, p.y + p.h + 5, seed, g=P.CASTLE_WALL_DARK, rows=16)
    shape(_rect(p.X(0.78), p.Y(0.6), p.X(0.81), p.Y(0.85)), P.SUMMER_SKY, LINE)
    steps = []
    n = 14
    for i in range(n):
        x0 = p.x - 5 + i*p.w/n; y0 = p.y + i*p.h*0.04
        shape(_rect(x0, p.y - 5, x0 + p.w/n + 1, y0 + p.h*0.04), P.CASTLE_STONE, LINE*0.9)
        steps.append((x0 + p.w/n/2, y0 + p.h*0.04))
    return steps


def ghost(x, y, s=1.0):
    """a sheet ghost (Tonda's idea)"""
    with T(x, y, s):
        shape(bez((-18, 0), (-20, 40), (20, 40), (18, 0)) + [(12, 4), (6, 0), (0, 4), (-6, 0), (-12, 4)], 1.0, LINE)
        for sx in (-1, 1): fill(ell(sx*6, 26, 2.6, 3.6, 12), 0.0)
        fill(ell(0, 16, 3, 4, 12), 0.0)


def joey_kavka(x, y, s, flip=False):
    """Joey asleep with a jackdaw on the ground at his white chest, pulling out a tuft of fur"""
    joey_lezi(x, y, s, flip=flip)
    d = -1 if flip else 1
    kavka(x + d*58*s, y, 0.62*s, flip=not flip, pose="walk", item=lambda a, b: chlup(a + 2, b - 2, 0.45))


def kavka_dawn(p, x, y, s):
    """a jackdaw perched, kept clear of balloons"""
    kavka(x, y, s, pose="perch")
    keep_clear(p, x - 28*s, y - 2*s, x + 18*s, y + 30*s, "kavka")


# =================================================================== 1 COVER
def cover():
    with Pn(M, 40, W-2*M, H-80) as p:
        _panel_fill(p, P.DUSK_SKY)
        cloud(p.X(0.15), p.Y(0.62), 0.6)
        hills(p, p.Y(0.2), 30, P.FAR_FIELD, 3)
        gy = p.Y(0.14)
        palace_wall(p.x - 10, p.X(0.5), gy, p.h*0.36, 3, windows=(0.3, 0.7))
        hl = tower(p.X(0.72), gy, p.w*0.4, p.h*0.62, 9, roof=False,
                   marks={14: dict(eyes=True, glow=True, ribbon=True), 4: dict(bird=True)})
        battlement(p.X(0.52), p.X(0.92), gy + p.h*0.62, 14)
        kavka(p.X(0.6), gy + p.h*0.62 + 14, 1.4, pose="perch")
        kavky_sky(p.X(0.1), p.Y(0.66), p.X(0.5), p.Y(0.78), 5, 3, 0.9)
        cobbles(p, p.y, gy, 2)
        cx, cy, sz = hl[13]
        torch_beam(p.X(0.44) + 26, p.Y(0.02) + 92, cx - sz, cy - sz, cx + sz, cy + sz, 0.42)
        vetvicky(cx, gy + 2, 70, 4, 1.4)
        alica(p.X(0.16), p.Y(0.02), 2.0, mood="think", right="lens", lens=True, look=(1, 0.8))
        hanka(p.X(0.44), p.Y(0.02), 2.1, mood="wow", right="front", look=(1, 0.7), item=lambda x, y: torch(x, y, 40))
        joey(p.X(0.88), p.Y(0.02), 1.5, flip=True, mood="bark", collar=False)
    box = [(M+34, H-236), (W-M-30, H-232), (W-M-34, H-48), (M+30, H-52)]
    fill([(x+3, y-3) for x, y in box], 0.0, 0.25); fill(box, 1.0)
    for a_, b_ in ((0, 1), (1, 2), (2, 3), (3, 0)): stroke([box[a_], box[b_]], 1.8)
    series_title(W/2, H-98, H-160, 40, 66)
    hand_text(M+40, H-190, W-2*M-80, "Alica, Hanka a Joey", "SHB", 20)
    hand_text(M+40, H-217, W-2*M-80, "Případ č. 14: Poklad na hradě", "SH", 15)
    magnifier(M+82, H-120, ang=-30, r=17)
    velky_klic(W-M-86, H-110, 1.3, rot=-30)
    page_end()


# =================================================================== 2 WHO IS WHO
def page_cast():
    with Pn(M, 40, W-2*M, H-80) as p:
        hand_text(p.X(0.05), p.Y(0.95), p.w*0.9, "Kdo je kdo", "SHB", 28)
        cells = [
            ("Alica", "Lupa a zápisník.", lambda x, y: alica(x, y, 0.9, mood="happy", right="lens", lens=True)),
            ("Hanka", "Opička a baterka.", lambda x, y: hanka(x, y, 1.1, mood="grin", item=lambda a, b: torch(a, b, 10), right="front")),
            ("Joey", "Jde všude s holkami.", lambda x, y: joey(x, y, 1.2, mood="happy", collar=False)),
            ("Děda", "Kdysi založil Klub Hvězdička.", lambda x, y: deda(x, y, 0.62, mood="happy")),
            ("Paní Věrka", "Z Klubu. Kreslila mapy.", lambda x, y: verka_old(x, y, 0.6, mood="happy")),
            ("Pan Franta", "Z Klubu. Bětčin děda.", lambda x, y: rybar(x, y, 0.55, mood="happy", rod=False)),
            ("Tonda", "Pořád má hlad.", lambda x, y: tonda(x, y, 0.8, mood="grin")),
            ("Bětka", "Ráda kreslí.", lambda x, y: betka(x, y, 1.0, hat=False, mood="grin")),
            ("Paní kastelánka", "Má klíče od celého hradu.", lambda x, y: kastelanka(x, y, 0.62, mood="happy")),
        ]
        cw, ch = p.w/3, p.h*0.19
        for i, (name, line, fig) in enumerate(cells):
            cx = p.x + (i % 3)*cw; cy = p.Y(0.9) - (i//3 + 1)*ch
            shape(rrect(cx + 8, cy + 6, cw - 16, ch - 12, 10), 0.97, 1.2)
            fig(cx + cw/2, cy + 46)
            hand_text(cx + 10, cy + 30, cw - 20, name, "SHB", 15 if len(name) < 16 else 12)
            hand_text(cx + 10, cy + 14, cw - 20, line, "SH", 11)
        by = p.y + 8; bh = p.Y(0.9) - 3*ch - by - 8
        shape(rrect(p.x + 8, by, p.w - 16, bh, 10), P.PHOTO_BG, 1.2)
        hand_text(p.x + 20, by + bh - 28, p.w*0.6, "Minule:", "SHB", 17, align="left")
        hand_text(p.x + 20, by + bh - 52, p.w*0.56,
                  "U potoka stavěl hráz mladý bobr Hryzálek. Pod hrází našel Klub starou plechovku. "
                  "V ní byla kresba hradu a záhadné XIV.",
                  "SH", 13, align="left", lead=17)
        hrad_kresba(p.X(0.66), by + bh*0.14, 70, 86, -6)
        bobr(p.X(0.9), by + bh*0.12, 0.7, pose="sit", flip=True)
    page_end()


# =================================================================== 3 the chalupa: the drawing is Točník
def page_chalupa():
    R = rows([(290, [1]), (220, [0.5, 0.5]), (240, [1])])
    with Pn(*R[0]) as p:
        gy = chalupa_garden(p, 0.5, 31)
        stul(p.X(0.5), p.Y(0.03), 230, 1.2)
        hrad_kresba(p.X(0.47), p.Y(0.03) + 56, 34, 42, 4)
        deda(p.X(0.2), p.Y(0.03), 0.95, mood="wow", right="point", look=(1, -0.2))
        verka_old(p.X(0.62), p.Y(0.03), 0.9, flip=True, mood="think", look=(-1, -0.4))
        alica(p.X(0.86), p.Y(0.03), 1.05, flip=True, mood="surprised", look=(-1, 0))
        cap(p, "Na chalupě. Klub Hvězdička zkoumá kresbu z plechovky.", w=230, where="tl")
        say(p, "Tuhle věž znám. To je hrad Točník!", *hdd(p.X(0.2), p.Y(0.03), 0.95), w=130, area=(0.0, 0.5))
        say(p, "Tam jsme už byly!", *ha(p.X(0.86), p.Y(0.03), 1.05), w=90, area=(0.66, 1.0))
    with Pn(*R[1]) as p:
        bg_fill(p, P.TABLECLOTH)
        hrad_kresba(p.X(0.25), p.Y(0.08), 120, 148, -3)
        keep_clear(p, p.X(0.22), p.Y(0.06), p.X(0.25) + 124, p.Y(0.08) + 152, "kresba")
        cap(p, "Věž, hvězda a XIV.", w=120, where="tl")
    with Pn(*R[2]) as p:
        gy = chalupa_garden(p, 0.52, 32)
        verka_old(p.X(0.3), p.Y(0.03), 0.95, mood="happy", right="front", look=(1, 0),
                  item=lambda x, y: hrad_kresba(x - 4, y - 20, 26, 32, 8))
        say(p, "Tu kresbu jsem kreslila já. Když jsme byli malí.", *hv(p.X(0.3), p.Y(0.03), 0.95), w=140, area=(0.0, 1.0))
    with Pn(*R[3]) as p:
        gy = chalupa_garden(p, 0.5, 33)
        verka_old(p.X(0.12), p.Y(0.03), 0.9, mood="worried", look=(1, 0))
        rybar(p.X(0.36), p.Y(0.03), 0.9, flip=True, mood="think", rod=False, look=(-1, 0))
        deda(p.X(0.62), p.Y(0.03), 0.85, flip=True, mood="grin", right="up", look=(-1, 0))
        hanka(p.X(0.9), p.Y(0.03), 1.0, flip=True, mood="grin", right="up", left="up", look=(-1, 0))
        kl(p.X(0.48), p.Y(0.06), -10)
        say(p, "Ale co je XIV… to už nevím.", *hv(p.X(0.12), p.Y(0.03), 0.9), w=100, area=(0.0, 0.28))
        say(p, "Já taky ne.", *hf(p.X(0.36), p.Y(0.03), 0.9), w=70, area=(0.22, 0.48))
        say(p, "Pojedeme na Točník. A budeme tam i spát!", *hdd(p.X(0.62), p.Y(0.03), 0.85), w=120, area=(0.44, 0.8))
        say(p, "Hurá!", *hh(p.X(0.9), p.Y(0.03), 1.0), w=60, area=(0.78, 1.0))
    page_end()


# =================================================================== 4 the walk up; the legend; Hanka spins
def page_walk():
    R = rows([(290, [1]), (220, [1]), (240, [1])])
    with Pn(*R[0]) as p:
        tocnik_view(p, 41, castle=(0.66, 0.52, 0.95), zebrak=(0.3, 0.34, 1.0))
        cap(p, "Sobota v červnu. Klub jde na hrad Točník.", w=200, where="tl")
    with Pn(*R[1]) as p:
        _panel_fill(p, P.SUMMER_SKY)
        wooded_hill(p, p.Y(0.7), 42, P.FOREST_DARK)
        zebrak_ruin(p.X(0.86), p.Y(0.52), 1.0)
        fill(_rect(p.x - 5, p.y - 5, p.x + p.w + 5, p.Y(0.2)), P.SPRING_GRASS)
        deda(p.X(0.1), p.Y(0.03), 0.78, mood="happy", right="point", look=(1, 0.3), legs="walk")
        say(p, "Tamhle dole je starý hrad Žebrák. Točník stojí nad ním.", *hdd(p.X(0.1), p.Y(0.03), 0.78), w=170,
            area=(0.0, 0.46))
        say(p, "Pověst říká: kdo chtěl na hrad, musel se třikrát otočit kolem hory.", *hdd(p.X(0.1), p.Y(0.03), 0.78),
            w=180, area=(0.42, 1.0))
    with Pn(*R[2]) as p:
        _panel_fill(p, P.SUMMER_SKY)
        wooded_hill(p, p.Y(0.75), 44, P.FOREST_DARK)
        fill(_rect(p.x - 5, p.y - 5, p.x + p.w + 5, p.Y(0.24)), P.SPRING_GRASS)
        hanka(p.X(0.16), p.Y(0.03), 1.15, mood="grin", right="up", left="up", look=(1, 0))
        spin_lines(p.X(0.16), p.Y(0.03), 1.1)
        tonda(p.X(0.42), p.Y(0.03), 1.0, mood="surprised", right="up", left="up", look=(-1, 0.2))
        spin_lines(p.X(0.42), p.Y(0.03), 1.1)
        J(p, p.X(0.62), p.Y(0.03), 1.0, mood="happy")
        alica(p.X(0.86), p.Y(0.03), 1.05, flip=True, mood="grin", look=(-1, 0))
        kl(p.X(0.74), p.Y(0.08), 15)
        say(p, "Raz, dva, tři!", *hh(p.X(0.16), p.Y(0.03), 1.15), w=80, area=(0.0, 0.32))
        say(p, "Točí se mi hlava!", *htd(p.X(0.42), p.Y(0.03), 1.0), w=90, area=(0.26, 0.6))
        say(p, "Proto se ten hrad jmenuje Točník!", *ha(p.X(0.86), p.Y(0.03), 1.05), w=120, area=(0.6, 1.0))
    page_end()


# =================================================================== 5 the gate, the kastelánka, the bears
def page_gate():
    R = rows([(300, [1]), (210, [0.5, 0.5]), (240, [1])])
    with Pn(*R[0]) as p:
        gy, gx = gate_bridge(p, 0.2, 51)
        kastelanka(gx - p.w*0.02, gy, 0.8, mood="happy", right="wave", look=(-1, 0), flip=True)
        deda(p.X(0.14), gy, 0.8, mood="happy", right="wave", look=(1, 0), legs="walk")
        betka(p.X(0.28), gy, 1.0, hat=False, mood="happy", look=(1, 0), legs="walk")
        tonda(p.X(0.4), gy, 0.85, mood="grin", look=(1, 0), legs="walk")
        say(p, "Dobrý den, paní kastelánko!", *hdd(p.X(0.14), gy, 0.8), w=110, area=(0.0, 0.42))
        say(p, "Vítejte na Točníku, Klube Hvězdičko!", *hk(gx - p.w*0.02, gy, 0.8), w=130, area=(0.45, 1.0))
    with Pn(*R[1]) as p:
        gy, hl = nadvori(p, 0.2, 52, tower_x=None, birds=False)
        kastelanka(p.X(0.74), p.Y(0.03), 0.9, flip=True, mood="grin", right="front", look=(-1, 0),
                   item=lambda x, y: velky_klic(x, y, 1.0, rot=-80))
        say(p, "Tady mám klíče od celého hradu.", *hk(p.X(0.74), p.Y(0.03), 0.9), w=130, area=(0.0, 0.66))
    with Pn(*R[2]) as p:
        gy = medvedi_prikop(p, 0.3, 53)
        brtnik(p.X(0.36), p.Y(0.08), 1.0)
        brtnik(p.X(0.72), p.Y(0.06), 0.9, pose="sit", flip=True)
        cap(p, "V hradním příkopu bydlí medvědi.", w=150, where="tl")
    with Pn(*R[3]) as p:
        medvedi_prikop(p, 0.55, 54, fence=False)
        brtnik(p.X(0.55), p.Y(0.57), 0.6, pose="stand")
        brtnik(p.X(0.8), p.Y(0.56), 0.5, pose="walk", flip=True)
        kastelanka(p.X(0.14), p.Y(0.03), 0.9, mood="happy", right="point", look=(1, 0.3))
        hanka(p.X(0.4), p.Y(0.03), 1.1, mood="wow", right="wave", look=(1, 0.4))
        tonda(p.X(0.66), p.Y(0.03), 0.95, mood="grin", look=(1, 0.3))
        alica(p.X(0.88), p.Y(0.03), 1.0, flip=True, mood="happy", look=(-1, 0.3))
        railing(p, p.Y(0.1), p.Y(0.2))
        say(p, "To je Martin a to je Agáta.", *hk(p.X(0.14), p.Y(0.03), 0.9), w=100, area=(0.0, 0.34))
        say(p, "Ahoj, medvídci!", *hh(p.X(0.4), p.Y(0.03), 1.1), w=80, area=(0.28, 0.56))
        say(p, "Ti jsou velcí!", *htd(p.X(0.66), p.Y(0.03), 0.95), w=80, area=(0.52, 0.8))
    page_end()


# =================================================================== 6 the courtyard; Václav IV; Roman numerals
def page_courtyard():
    R = rows([(280, [1]), (230, [1]), (240, [1])])
    with Pn(*R[0]) as p:
        gy, hl = nadvori(p, 0.22, 61, tower_x=0.84, tower_w=0.26)
        kavka(p.X(0.66), gy + p.h*0.28 + 12, 0.7, pose="perch")
        kastelanka(p.X(0.14), p.Y(0.03), 0.9, mood="happy", right="up", look=(1, 0.3))
        deda(p.X(0.34), p.Y(0.03), 0.88, flip=True, mood="happy", look=(-1, 0))
        alica(p.X(0.52), p.Y(0.03), 1.0, flip=True, mood="think", look=(-1, 0.2))
        cap(p, "Na nádvoří.", w=90, where="tr")
        say(p, "Tenhle hrad postavil král Václav IV. Před víc než šesti sty lety!", *hk(p.X(0.14), p.Y(0.03), 0.9),
            w=150, area=(0.0, 0.5))
        say(p, "IV? To je jako na kresbě z plechovky!", *ha(p.X(0.52), p.Y(0.03), 1.0), w=110, area=(0.36, 0.76))
    with Pn(*R[1]) as p:
        gy, hl = nadvori(p, 0.3, 62, tower_x=None, birds=False)
        shape(rrect(p.X(0.03), p.Y(0.12), p.w*0.36, p.h*0.62, 8), P.LETTER_PAPER, LINE)
        for i, (sym, num) in enumerate((("I", "1"), ("V", "5"), ("X", "10"), ("IV", "4"))):
            hand_text(p.X(0.04 + (i % 2)*0.17), p.Y(0.5 - (i//2)*0.24), p.w*0.16, f"{sym} = {num}", "SHB", 20)
        keep_clear(p, p.X(0.03), p.Y(0.12), p.X(0.39), p.Y(0.74), "papir")
        deda(p.X(0.5), p.Y(0.03), 0.9, mood="happy", right="point", look=(-1, 0))
        alica(p.X(0.82), p.Y(0.03), 1.05, flip=True, mood="wow", look=(-1, 0))
        cap(p, "Děda píše římské číslice.", w=150, where="tl")
        say(p, "Jednička před pětkou je čtyřka.", *hdd(p.X(0.5), p.Y(0.03), 0.9), w=110, area=(0.4, 0.7))
        say(p, "Takže XIV je čtrnáct!", *ha(p.X(0.82), p.Y(0.03), 1.05), w=90, area=(0.68, 1.0))
    with Pn(*R[2]) as p:
        gy, hl = nadvori(p, 0.24, 63, tower_x=0.82, tower_w=0.28)
        kavka(p.X(0.64), gy + p.h*0.28 + 12, 0.7, pose="perch", flip=True)
        tonda(p.X(0.12), p.Y(0.03), 0.95, mood="think", look=(1, 0))
        betka(p.X(0.34), p.Y(0.03), 1.2, hat=False, mood="think", look=(1, 0))
        alica(p.X(0.56), p.Y(0.03), 1.05, flip=True, mood="determined", right="lens", lens=True, look=(-1, 0))
        say(p, "Čtrnáct čeho?", *htd(p.X(0.12), p.Y(0.03), 0.95), w=80, area=(0.0, 0.24))
        say(p, "Schodů? Oken? Kroků?", *hbe(p.X(0.34), p.Y(0.03), 1.2), w=90, area=(0.2, 0.48))
        say(p, "To zjistíme!", *ha(p.X(0.56), p.Y(0.03), 1.05), w=70, area=(0.44, 0.68))
    page_end()


# =================================================================== 7 hunting 14; Bětka draws; the rohlík
def page_hunt():
    R = rows([(280, [1]), (220, [0.5, 0.5]), (250, [0.5, 0.5])])
    with Pn(*R[0]) as p:
        steps = stairs(p, 71)
        ax, ay = steps[13]
        alica(ax - 10, ay, 1.0, flip=True, mood="think", look=(-1, -0.3))
        hx_, hy_ = steps[3]
        hanka(hx_, hy_, 1.1, mood="grin", look=(1, 0.3), item=lambda x, y: torch(x, y, 30), right="front")
        kl(p.X(0.1), p.Y(0.62), 30)
        cap(p, "Alica počítá schody ve věži.", w=150, where="tl")
        say(p, "Dvanáct, třináct, čtrnáct… Nic tu není.", *ha(ax - 10, ay, 1.0), w=130, area=(0.36, 0.86))
    with Pn(*R[1]) as p:
        gy, hl = nadvori(p, 0.2, 72, tower_x=None, windows=(0.15, 0.4, 0.7, 0.9))
        tonda(p.X(0.78), p.Y(0.03), 1.0, flip=True, mood="think", right="point", look=(-1, 0.5))
        say(p, "Čtrnáct oken? Tady jsou jen čtyři.", *htd(p.X(0.78), p.Y(0.03), 1.0), w=110, area=(0.0, 1.0))
    with Pn(*R[2]) as p:
        gy, hl = nadvori(p, 0.24, 73, tower_x=0.7, tower_w=0.42, palace=False)
        betka(p.X(0.16), p.Y(0.03), 1.0, hat=False, mood="happy", right="front", left="front", look=(1, 0.4),
              item=lambda x, y: vez_kresba(x - 10, y - 30, 22, 28, 0))
        cap(p, "Bětka kreslí věž.", w=100, where="tr")
        say(p, "Ta věž má spoustu děr.", *hbe(p.X(0.16), p.Y(0.03), 1.0), w=80, area=(0.0, 0.46))
    with Pn(*R[3]) as p:
        gy, hl = nadvori(p, 0.3, 74, tower_x=None, birds=False)
        lavicka(p.X(0.36), p.Y(0.06), 1.4)
        rohlik(p.X(0.3), p.Y(0.06) + 28*1.4, 1.2)
        tonda(p.X(0.74), p.Y(0.03), 1.0, flip=True, mood="happy", look=(-1, 0), legs="walk")
        say(p, "Rohlík si nechám na potom.", *htd(p.X(0.74), p.Y(0.03), 1.0), w=100, area=(0.4, 1.0))
    with Pn(*R[4]) as p:
        gy, hl = nadvori(p, 0.3, 74, tower_x=None, birds=False)
        kavky_sky(p.X(0.7), p.Y(0.8), p.X(0.9), p.Y(0.92), 1, 7, 0.7)
        lavicka(p.X(0.36), p.Y(0.06), 1.4)
        drobky(p.X(0.3), p.Y(0.06) + 30*1.4, 26, 7)
        tonda(p.X(0.74), p.Y(0.03), 1.0, flip=True, mood="surprised", right="up", left="up", look=(-1, -0.3))
        say(p, "Můj rohlík! Je pryč!", *htd(p.X(0.74), p.Y(0.03), 1.0), w=90, area=(0.4, 1.0))
    page_end()


# =================================================================== 8 the bears? Joey?
def page_bears():
    R = rows([(240, [1]), (280, [1]), (230, [0.5, 0.5])])
    with Pn(*R[0]) as p:
        gy, hl = nadvori(p, 0.3, 81, tower_x=None, birds=False)
        tonda(p.X(0.18), p.Y(0.03), 1.0, mood="determined", right="point", look=(1, 0))
        hanka(p.X(0.5), p.Y(0.03), 1.15, mood="wow", look=(-1, 0))
        alica(p.X(0.8), p.Y(0.03), 1.05, flip=True, mood="think", look=(-1, 0))
        say(p, "To byli medvědi! Mají hlad!", *htd(p.X(0.18), p.Y(0.03), 1.0), w=110, area=(0.0, 0.4))
        say(p, "Medvědi mají rádi rohlíky!", *hh(p.X(0.5), p.Y(0.03), 1.15), w=100, area=(0.32, 0.66))
        say(p, "Pojďme se podívat.", *ha(p.X(0.8), p.Y(0.03), 1.05), w=90, area=(0.64, 1.0))
    with Pn(*R[1]) as p:
        medvedi_prikop(p, 0.55, 82, fence=False)
        brtnik(p.X(0.6), p.Y(0.57), 0.62, pose="stand")
        shape(ell(p.X(0.6) + 4, p.Y(0.57) + 72, 4.5, 4.5, 14), P.APPLE, LINE*0.6)
        brtnik(p.X(0.84), p.Y(0.56), 0.55, pose="sit", flip=True)
        kastelanka(p.X(0.14), p.Y(0.03), 0.9, mood="happy", right="up", look=(1, 0.4))
        alica(p.X(0.38), p.Y(0.03), 1.0, mood="think", look=(1, 0.3))
        railing(p, p.Y(0.1), p.Y(0.2))
        kl(p.X(0.93), p.Y(0.06), -30)
        say(p, "Medvědi z příkopu ven nemůžou. Dostávají jablka a mrkev.", *hk(p.X(0.14), p.Y(0.03), 0.9), w=140,
            area=(0.0, 0.42))
        say(p, "Takže medvědi to nebyli.", *ha(p.X(0.38), p.Y(0.03), 1.0), w=100, area=(0.3, 0.66))
    with Pn(*R[2]) as p:
        gy, hl = nadvori(p, 0.4, 83, tower_x=None, birds=False)
        joey_kavka(p.X(0.4), p.Y(0.06), 1.3)
        cap(p, "Joey spí na sluníčku.", w=120, where="tl")
    with Pn(*R[3]) as p:
        gy, hl = nadvori(p, 0.4, 84, tower_x=None, birds=False)
        tonda(p.X(0.24), p.Y(0.03), 1.0, mood="think", look=(1, 0))
        alica(p.X(0.72), p.Y(0.03), 1.05, flip=True, mood="happy", look=(-1, 0))
        say(p, "A co Joey? Ten sní všechno!", *htd(p.X(0.24), p.Y(0.03), 1.0), w=100, area=(0.0, 0.5))
        say(p, "Joey celou dobu spal.", *ha(p.X(0.72), p.Y(0.03), 1.05), w=90, area=(0.5, 1.0))
    page_end()


# =================================================================== 9 evening in the hall; the window; the legend
def sill_things(x0, x1, y):
    stuzka(x0 + 16, y + 4, 0.8, 8)
    sponka(x1 - 14, y + 5, 0.9, -10)


def page_evening():
    R = rows([(300, [1]), (210, [0.5, 0.5]), (240, [1])])
    with Pn(*R[0]) as p:
        fy, (sx0, sx1, sy) = hall(p, 0.16, 91, window=(0.62, 0.4, 0.16, 0.36), sill_items=sill_things)
        for i, fx in enumerate((0.14, 0.86)):
            shape(ell(p.X(fx), p.Y(0.07), 44, 9, 20), P.SLEEPING_BAG if i else P.SLEEPING_BAG_2, LINE)
        betka(p.X(0.42), p.Y(0.03), 1.2, hat=False, mood="happy", right="up", look=(1, 0.6))
        alica(p.X(0.84), p.Y(0.03), 1.05, flip=True, mood="happy", right="up", look=(-1, 0.6))
        cap(p, "Večer. Klub spí v hradní síni.", w=150, where="tl")
        say(p, "Stužku si dám na okno.", *hbe(p.X(0.42), p.Y(0.03), 1.2), w=90, area=(0.18, 0.5))
        say(p, "A já sponku s mašlí.", *ha(p.X(0.84), p.Y(0.03), 1.05), w=90, area=(0.7, 1.0))
    with Pn(*R[1]) as p:
        bg_fill(p, P.CASTLE_WALL_DARK)
        shape(_rect(p.X(0.25), p.Y(0.3), p.X(0.75), p.Y(1.02)), P.SUMMER_SKY, LINE)
        shape(_rect(p.x - 5, p.y - 5, p.x + p.w + 5, p.Y(0.3)), P.CASTLE_STONE, LINE)
        stuzka(p.X(0.3), p.Y(0.33), 1.8, 6)
        sponka(p.X(0.72), p.Y(0.34), 2.0, -8)
        keep_clear(p, p.X(0.1), p.Y(0.28), p.X(0.9), p.Y(0.45), "sill")
        cap(p, "Okno zůstane otevřené. Je teplo.", w=150, where="tl")
    with Pn(*R[2]) as p:
        fy, sill = hall(p, 0.2, 92, window=(0.85, 0.5, 0.14, 0.3), vault=False)
        lucerna(p.X(0.56), p.Y(0.04), 1.2)
        tonda(p.X(0.76), p.Y(0.03), 0.95, flip=True, mood="grin", right="up", left="up", look=(-1, 0))
        say(p, "Teď vám povím pověst o strašidle!", *htd(p.X(0.76), p.Y(0.03), 0.95), w=130, area=(0.0, 0.7))
    with Pn(*R[3]) as p:
        fy, sill = hall(p, 0.2, 93, window=(0.5, 0.5, 0.1, 0.28), vault=False)
        night_tint(p, 0.25)
        lucerna(p.X(0.5), p.Y(0.04), 1.2)
        ve_spacaku(tonda, 47, p.X(0.14), p.Y(0.03), 1.0, P.SLEEPING_BAG, mood="grin", look=(1, 0), right="up")
        ve_spacaku(deda, 59, p.X(0.36), p.Y(0.03), 0.85, P.SLEEPING_BAG_2, mood="happy", look=(1, 0))
        ve_spacaku(hanka, 31, p.X(0.66), p.Y(0.03), 1.15, P.SLEEPING_BAG, mood="grin", right="hug", look=(-1, 0))
        ve_spacaku(betka, 31, p.X(0.86), p.Y(0.03), 1.2, P.SLEEPING_BAG_2, hat=False, mood="happy", look=(-1, 0))
        kl(p.X(0.5), p.Y(0.3), 0)
        say(p, "Císař Rudolf se strašidla bál. Ale na úzké cestě se vozy nedaly otočit.",
            *htd(p.X(0.14), p.Y(0.03) - 47*0.5, 1.0), w=150, area=(0.0, 0.5))
        say(p, "Tak tu musel přespat. Jako my!", *hdd(p.X(0.36), p.Y(0.03) - 59*0.85*0.5, 0.85), w=100, area=(0.28, 0.62))
        say(p, "Já se nebojím.", *hh(p.X(0.66), p.Y(0.03) - 31*1.15*0.5, 1.15), w=80, area=(0.56, 0.84))
    page_end()


# =================================================================== 10 night: rustling in the wall
def page_night():
    R = rows([(300, [1]), (200, [0.5, 0.5]), (250, [1])])
    with Pn(*R[0]) as p:
        fy, (sx0, sx1, sy) = hall(p, 0.16, 101, night=True, window=(0.72, 0.42, 0.16, 0.34), sill_items=sill_things)
        lezi(tonda, p.X(0.3), p.Y(0.04), 0.8, P.SLEEPING_BAG, mood="sleepy")
        ve_spacaku(hanka, 31, p.X(0.5), p.Y(0.03), 1.15, P.SLEEPING_BAG, mood="surprised", right="front", look=(1, 0.3),
                   item=lambda x, y: torch(x, y, 30))
        sfx(p.X(0.82), p.Y(0.62), "ŠRAMOT…", 16, -4)
        sfx(p.X(0.84), p.Y(0.26), "ŠKRÁB", 16, 6)
        cap(p, "V noci.", w=70, where="tl")
        say(p, "Slyšíte to?", *hh(p.X(0.5), p.Y(0.03) - 31*1.15*0.5, 1.15), w=70, area=(0.3, 0.62), whisper=True)
    with Pn(*R[1]) as p:
        fy, sill = hall(p, 0.2, 102, night=True, window=(0.85, 0.5, 0.14, 0.3), vault=False)
        ve_spacaku(tonda, 47, p.X(0.4), p.Y(0.03), 1.05, P.SLEEPING_BAG, mood="surprised", right="up", left="up", look=(1, 0))
        say(p, "Strašidlo!!!", *htd(p.X(0.4), p.Y(0.03) - 47*1.05*0.5, 1.05), w=80, area=(0.0, 1.0))
    with Pn(*R[2]) as p:
        fy, sill = hall(p, 0.2, 103, night=True, window=(0.15, 0.5, 0.14, 0.3), vault=False)
        ve_spacaku(alica, 45, p.X(0.6), p.Y(0.03), 1.05, P.SLEEPING_BAG_2, mood="whisper", right="hush", look=(-1, 0))
        say(p, "Psst. To šramotí venku ve zdi.", *ha(p.X(0.6), p.Y(0.03) - 45*1.05*0.5, 1.05), w=110, area=(0.0, 1.0),
            whisper=True)
    with Pn(*R[3]) as p:
        fy, (sx0, sx1, sy) = hall(p, 0.16, 104, night=True, window=(0.66, 0.4, 0.2, 0.4), sill_items=sill_things)
        torch_beam(p.X(0.2) + 24, p.Y(0.03) + 60, sx0 + 4, sy - 20, sx1 - 4, sy + 60, 0.4)
        joey_lezi(p.X(0.4), p.Y(0.03), 0.95)
        ve_spacaku(hanka, 31, p.X(0.2), p.Y(0.03), 1.2, P.SLEEPING_BAG, mood="think", right="front", look=(1, 0.4),
                   item=lambda x, y: torch(x, y, 30))
        cap(p, "Hanka svítí na okno. Stužka i sponka tam pořád jsou.", w=180, where="tr")
        say(p, "Nikdo tu není.", *hh(p.X(0.2), p.Y(0.03) - 31*1.2*0.5, 1.2), w=80, area=(0.0, 0.42), whisper=True)
    page_end()


# =================================================================== 11 morning: the ribbon and the clip are gone
def page_morning():
    R = rows([(300, [1]), (210, [0.5, 0.5]), (240, [1])])
    with Pn(*R[0]) as p:
        fy, sill = hall(p, 0.16, 111, window=(0.5, 0.42, 0.16, 0.34))
        betka(p.X(0.24), p.Y(0.03), 1.25, hat=False, mood="surprised", right="point", look=(1, 0.5))
        alica(p.X(0.78), p.Y(0.03), 1.05, flip=True, mood="surprised", left="up", right="up", look=(-1, 0.5))
        cap(p, "Ráno.", w=60, where="tl")
        say(p, "Moje stužka je pryč!", *hbe(p.X(0.24), p.Y(0.03), 1.25), w=90, area=(0.0, 0.4))
        say(p, "A moje sponka taky!", *ha(p.X(0.78), p.Y(0.03), 1.05), w=90, area=(0.6, 1.0))
    with Pn(*R[1]) as p:
        bg_fill(p, P.CASTLE_WALL_DARK)
        shape(_rect(p.X(0.25), p.Y(0.3), p.X(0.75), p.Y(1.02)), P.SUMMER_SKY, LINE)
        shape(_rect(p.x - 5, p.y - 5, p.x + p.w + 5, p.Y(0.3)), P.CASTLE_STONE, LINE)
        cap(p, "Na okně nic není.", w=110, where="tl")
    with Pn(*R[2]) as p:
        fy, sill = hall(p, 0.2, 112, window=(0.15, 0.5, 0.14, 0.3), vault=False)
        tonda(p.X(0.5), p.Y(0.03), 1.05, mood="determined", right="up", look=(1, 0))
        say(p, "Strašidlo! Říkal jsem to!", *htd(p.X(0.5), p.Y(0.03), 1.05), w=100, area=(0.0, 1.0))
    with Pn(*R[3]) as p:
        fy, sill = hall(p, 0.16, 113, window=(0.86, 0.4, 0.12, 0.34))
        alica(p.X(0.18), p.Y(0.03), 1.15, mood="determined", right="lens", lens=True, look=(1, 0))
        hanka(p.X(0.46), p.Y(0.03), 1.15, mood="grin", right="up", look=(-1, 0), item=lambda x, y: torch(x, y, 80))
        J(p, p.X(0.7), p.Y(0.03), 1.0, flip=True, mood="happy")
        kl(p.X(0.6), p.Y(0.05), 10)
        say(p, "Zakládám případ číslo čtrnáct: Kdo krade na hradě?", *ha(p.X(0.18), p.Y(0.03), 1.15), w=150, area=(0.0, 0.45))
        say(p, "A taky najdeme poklad!", *hh(p.X(0.46), p.Y(0.03), 1.15), w=100, area=(0.36, 0.78))
    page_end()


# =================================================================== 12 the suspect board
def page_board():
    R = rows([(470, [1]), (270, [1])])
    with Pn(*R[0], bg=0.92) as p:
        shape(rrect(p.X(0.04), p.Y(0.04), p.w*0.92, p.h*0.82, 6), 1.0, LINE*1.4)
        for k in range(16): stroke([(p.X(0.06), p.Y(0.07 + k*0.05)), (p.X(0.94), p.Y(0.07 + k*0.05))], 0.4, g=0.8)
        hand_text(p.X(0.04), p.Y(0.9), p.w*0.92, "Kdo krade na hradě? (kreslí Bětka)", "SHB", 22)
        from narozeniny import suspect_card
        cards = [
            ("medvědi? (Tonda)", lambda x, y: brtnik(x - 6, y + 4, 0.75)),
            ("strašidlo? (Tonda)", lambda x, y: ghost(x, y + 8, 1.4)),
            ("Joey?", lambda x, y: joey(x - 4, y + 2, 1.4, collar=False, mood="happy", shadow=False)),
            ("kdo ještě?", lambda x, y: hand_text(x - 30, y + 30, 60, "?", "SHB", 50, g=0.3)),
            ("ztratilo se:", lambda x, y: (rohlik(x - 20, y + 50, 1.1), stuzka(x + 6, y + 30, 1.0), sponka(x - 6, y + 12, 1.3))),
        ]
        cw, ch = p.w*0.27, p.h*0.3
        for i, (lbl, fn) in enumerate(cards):
            cx = p.X(0.09) + (i % 3)*(cw + p.w*0.03); cy = p.Y(0.5) - (i//3)*(ch + 12)
            suspect_card(cx, cy, cw, ch, fn, lbl, rot=((i*7) % 9) - 4)
        keep_clear(p, p.X(0.04), p.Y(0.04), p.X(0.96), p.Y(0.86), "board")
    with Pn(*R[1]) as p:
        fy, sill = hall(p, 0.2, 121, window=(0.5, 0.5, 0.1, 0.3), vault=False)
        alica(p.X(0.14), p.Y(0.03), 1.1, mood="determined", right="lens", lens=True, look=(1, 0))
        tonda(p.X(0.5), p.Y(0.03), 1.05, mood="determined", right="point", look=(1, 0))
        betka(p.X(0.82), p.Y(0.03), 1.3, flip=True, hat=False, mood="worried", look=(-1, 0))
        say(p, "Medvědi jsou v příkopu. A Joey spal u Hanky.", *ha(p.X(0.14), p.Y(0.03), 1.1), w=140, area=(0.0, 0.4))
        say(p, "Tak zbývá strašidlo!", *htd(p.X(0.5), p.Y(0.03), 1.05), w=90, area=(0.36, 0.66))
        say(p, "Strašidla nejsou.", *hbe(p.X(0.82), p.Y(0.03), 1.3), w=90, area=(0.64, 1.0))
    page_end()


# =================================================================== 13 the windowsill: prints, a black feather; pigeon? the kastelánka?
def page_sill():
    R = rows([(280, [1]), (220, [0.5, 0.5]), (250, [1])])
    with Pn(*R[0]) as p:
        fy, (sx0, sx1, sy) = hall(p, 0.12, 131, window=(0.6, 0.3, 0.2, 0.44))
        alica(p.X(0.4), p.Y(0.03), 1.1, mood="think", right="lens", lens=True, look=(1, 0.5))
        bird_prints(sx0 + 20, sy - 6, 0.8, 4, 4)
        say(p, "V prachu na okně jsou stopičky!", *ha(p.X(0.4), p.Y(0.03), 1.1), w=110, area=(0.0, 0.44))
    with Pn(*R[1]) as p:
        bg_fill(p, P.CASTLE_STONE)
        inset(p, p.X(0.5), p.Y(0.42), p.w*0.74, p.h*0.66,
              lambda x, y: (bird_prints(x - 50, y - 18, 1.8, 4, 8), kavci_pero(x + 30, y - 6, 2.2, -60)), g=P.CASTLE_STONE)
        cap(p, "Tři prstíky dopředu, jeden dozadu. A pírko.", w=170, where="tl")
    with Pn(*R[2]) as p:
        fy, sill = hall(p, 0.2, 132, window=(0.15, 0.5, 0.14, 0.3), vault=False)
        tonda(p.X(0.5), p.Y(0.03), 1.05, mood="grin", right="point", look=(1, 0))
        say(p, "Ptačí stopy. To byl holub!", *htd(p.X(0.5), p.Y(0.03), 1.05), w=100, area=(0.0, 1.0))
    with Pn(*R[3]) as p:
        gy, hl = nadvori(p, 0.3, 133, tower_x=None, birds=False)
        hanka(p.X(0.14), p.Y(0.03), 1.15, mood="think", right="point", look=(1, 0))
        kastelanka(p.X(0.46), p.Y(0.03), 0.95, flip=True, mood="happy", look=(-1, 0))
        ladder(p.X(0.62), p.Y(0.03), p.Y(0.85), 30)
        alica(p.X(0.86), p.Y(0.03), 1.05, flip=True, mood="think", right="front", look=(-1, 0),
              item=lambda x, y: kavci_pero(x, y, 0.8, 20))
        say(p, "Paní kastelánka tu ráno byla. Se žebříkem!", *hh(p.X(0.14), p.Y(0.03), 1.15), w=120, area=(0.0, 0.38))
        say(p, "Ráno otvírám okenice, Hanko. Stužku jsem neviděla.", *hk(p.X(0.46), p.Y(0.03), 0.95), w=130,
            area=(0.26, 0.7))
        say(p, "A holubí pírko je šedé. Tohle je černé.", *ha(p.X(0.86), p.Y(0.03), 1.05), w=110, area=(0.66, 1.0))
    page_end()


# =================================================================== 14 the twigs under the tower; Joey's fur; putlog holes
def page_twigs():
    R = rows([(300, [1]), (210, [0.5, 0.5]), (240, [1])])
    with Pn(*R[0]) as p:
        gy, hl = nadvori(p, 0.2, 141, tower_x=0.7, tower_w=0.4, palace=False,
                         marks={14: dict(twigs=True)})
        cx, cy, sz = hl[13]
        vetvicky(cx, gy + 1, 60, 5, 1.2)
        J(p, cx + 30, p.Y(0.03), 1.0, flip=True, pose="sniff")
        alica(p.X(0.12), p.Y(0.03), 1.05, mood="think", look=(1, 0))
        hanka(p.X(0.3), p.Y(0.03), 1.1, mood="wow", right="point", look=(1, 0))
        cap(p, "Joey čmuchá u věže.", w=110, where="tl")
        say(p, "Joey něco našel!", *hh(p.X(0.3), p.Y(0.03), 1.1), w=80, area=(0.14, 0.5))
    with Pn(*R[1]) as p:
        bg_fill(p, P.SPRING_GRASS)
        vetvicky(p.X(0.5), p.Y(0.22), p.w*0.8, 6, 2.0)
        chlup(p.X(0.42), p.Y(0.34), 2.2)
        keep_clear(p, p.X(0.08), p.Y(0.15), p.X(0.92), p.Y(0.55), "vetvicky")
        cap(p, "Hromádka větviček. A v nich…", w=150, where="tl")
    with Pn(*R[2]) as p:
        gy, hl = nadvori(p, 0.3, 142, tower_x=None, birds=False)
        hanka(p.X(0.72), p.Y(0.03), 1.05, flip=True, mood="wow", right="front", look=(-1, 0), item=lambda x, y: chlup(x, y, 1.0))
        say(p, "Joeyho chlupy! Černé a bílé!", *hh(p.X(0.72), p.Y(0.03), 1.05), w=110, area=(0.0, 0.66))
    with Pn(*R[3]) as p:
        gy, hl = nadvori(p, 0.2, 143, tower_x=0.84, tower_w=0.3, palace=False)
        kl(p.X(0.6), p.Y(0.06), 30)
        kastelanka(p.X(0.14), p.Y(0.03), 0.9, mood="happy", right="up", look=(1, 0.5))
        alica(p.X(0.4), p.Y(0.03), 1.05, mood="think", look=(1, 0.4))
        betka(p.X(0.6), p.Y(0.03) - 2, 1.2, hat=False, mood="happy", right="front", look=(1, 0.3),
              item=lambda x, y: vez_kresba(x - 10, y - 32, 24, 30, 0))
        say(p, "Ty díry jsou po lešení. Stavitelé do nich kdysi strkali trámy.", *hk(p.X(0.14), p.Y(0.03), 0.9),
            w=150, area=(0.0, 0.42))
        say(p, "A kdo tam teď nosí větvičky?", *ha(p.X(0.4), p.Y(0.03), 1.05), w=100, area=(0.32, 0.62))
        say(p, "Nakreslím všechny díry.", *hbe(p.X(0.6), p.Y(0.03) - 2, 1.2), w=90, area=(0.5, 0.78))
    page_end()


# =================================================================== 15 the guide: who lives in the castle?
def page_guide():
    with Pn(M, 40, W-2*M, H-80, bg=0.97) as p:
        hand_text(p.X(0.04), p.Y(0.955), p.w*0.92, "Kdo bydlí na hradě? Průvodce detektivky", "SHB", 25)
        hand_text(p.X(0.04), p.Y(0.915), p.w*0.92, "Porovnej, co našla Alica. Kdo si odnáší věci z okna?", "SH", 13)
        cells = [
            ("medvěd", "Bydlí dole v příkopu. Ven nemůže. Stopa velká jako talíř.", lambda x, y: brtnik(x - 10, y - 40, 1.3)),
            ("holub", "Šedé pírko. Hnízdí na římse. Do díry nic nenosí.",
             lambda x, y: (holub(x - 20, y - 40, 2.6), holubi_pero(x + 44, y - 40, 2.0, -20))),
            ("netopýr", "Přes den visí hlavou dolů. V noci loví mušky. Hnízdo nestaví.",
             lambda x, y: (netopyr(x - 30, y + 30, 2.4), netopyr(x + 30, y - 20, 2.0, hang=False))),
            ("sova", "Měkké šedohnědé pírko. Pod hnízdem chlupaté vývržky.",
             lambda x, y: (owl(x - 20, y - 44, 1.25), pellet(x + 40, y - 36, 2.2))),
            ("strašidlo", "Nikdo ho nikdy neviděl. Stopy ani pírka nenechává.", lambda x, y: ghost(x, y - 40, 2.0)),
            ("tajemný soused", "Černé pírko. Tři prstíky dopředu, jeden dozadu. Pod dírou větvičky.",
             lambda x, y: (kavci_pero(x - 40, y - 40, 2.2, -20), bird_prints(x - 14, y - 30, 1.6, 3, 10),
                           vetvicky(x + 30, y - 44, 56, 3, 1.3))),
        ]
        cw, ch = p.w*0.92/3, p.h*0.36
        for i, (name, tip, fig) in enumerate(cells):
            cx = p.X(0.04) + (i % 3)*cw; cy = p.Y(0.86) - (i//3 + 1)*(ch + 10)
            shape(rrect(cx + 4, cy, cw - 8, ch, 8), 1.0, 1.1)
            C.saveState(); C.clipPath(poly(rrect(cx + 6, cy + 2, cw - 12, ch - 4, 7)), stroke=0, fill=0)
            fig(cx + cw/2, cy + ch*0.62)
            C.restoreState()
            hand_text(cx + 8, cy + ch*0.32, cw - 16, name, "SHB", 15)
            hand_text(cx + 10, cy + ch*0.22, cw - 20, tip, "SH", 11, lead=13)
        hand_text(p.X(0.08), p.Y(0.05), p.w*0.84, "Kdo má černé pírko, bydlí v díře ve zdi a nosí si domů měkké věci?",
                  "SHB", 14, lead=17)
        keep_clear(p, p.x, p.y, p.x + p.w, p.y + p.h, "guide")
    page_end()


# =================================================================== 16 dawn: Hanka's torch, two eyes and the ribbon
def page_dawn():
    R = rows([(280, [1]), (230, [0.5, 0.5]), (240, [1])])
    with Pn(*R[0]) as p:
        fy, (sx0, sx1, sy) = hall(p, 0.16, 161, window=(0.74, 0.42, 0.16, 0.34))
        _panel_fill(p, P.NIGHT_MEADOW, 0.22)
        lezi(alica, p.X(0.34), p.Y(0.04), 0.8, P.SLEEPING_BAG_2, mood="sleepy")
        ve_spacaku(hanka, 31, p.X(0.52), p.Y(0.03), 1.15, P.SLEEPING_BAG, mood="surprised", right="front", look=(1, 0.4),
                   item=lambda x, y: torch(x, y, 30))
        sfx(p.X(0.84), p.Y(0.64), "KJA!", 18, -6)
        sfx(p.X(0.85), p.Y(0.4), "KJA!", 16, 6)
        cap(p, "Brzy ráno. Hanka se vzbudí první.", w=170, where="tl")
        say(p, "Kdo to volá?", *hh(p.X(0.52), p.Y(0.03) - 31*1.15*0.5, 1.15), w=70, area=(0.36, 0.66), whisper=True)
    with Pn(*R[1]) as p:
        fy, (sx0, sx1, sy) = hall(p, 0.1, 162, window=(0.5, 0.36, 0.42, 0.56), vault=False)
        _panel_fill(p, P.NIGHT_MEADOW, 0.2)
        hanka(p.X(0.5), sy, 1.1, mood="wow", right="front", look=(1, 0.5), item=lambda x, y: torch(x, y, 30), shadow=False)
        cap(p, "Hanka se dívá z okna na věž.", w=150, where="tl")
    with Pn(*R[2]) as p:
        stone_wall(p.x - 5, p.y - 5, p.x + p.w + 5, p.y + p.h + 5, 162, rows=18)
        _panel_fill(p, P.NIGHT_MEADOW, 0.25)
        for hx_, hy_ in ((0.12, 0.42), (0.88, 0.42)):
            putlog(p.X(hx_), p.Y(hy_), 34)
        cx, cy = p.X(0.5), p.Y(0.42)
        torch_beam(p.x, p.y, cx - 36, cy - 40, cx + 36, cy + 30, 0.35)
        putlog(cx, cy, 44, eyes=True, ribbon=True, glow=True, twigs=True)
        keep_clear(p, cx - 30, cy - 70, cx + 30, cy + 26, "hole")
        cap(p, "V jedné díře svítí dvě světlá očička. A visí z ní… červená stužka!", w=170, where="tl")
    with Pn(*R[3]) as p:
        fy, sill = hall(p, 0.16, 163, window=(0.86, 0.42, 0.12, 0.34))
        _panel_fill(p, P.NIGHT_MEADOW, 0.18)
        hanka(p.X(0.24), p.Y(0.03), 1.2, mood="wow", right="point", look=(1, -0.3), item=None)
        ve_spacaku(alica, 45, p.X(0.6), p.Y(0.03), 1.1, P.SLEEPING_BAG_2, mood="sleepy", look=(-1, 0))
        kl(p.X(0.42), p.Y(0.05), -15)
        say(p, "Ali! Vstávej! Ve zdi je Bětčina stužka!", *hh(p.X(0.24), p.Y(0.03), 1.2), w=130, area=(0.0, 0.5))
        say(p, "Cože? Kde?", *ha(p.X(0.6), p.Y(0.03) - 45*1.1*0.5, 1.1), w=70, area=(0.46, 0.8))
    page_end()


# =================================================================== 17 STOP, DETEKTIVE!
def page_stop():
    with Pn(M, 40, W-2*M, H-80, bg=0.95) as p:
        title(p.X(0.5), p.Y(0.92), "STOP, DETEKTIVE!", 44)
        hand_text(p.X(0.05), p.Y(0.86), p.w*0.9, "Kdo krade na hradě? A co je XIV?", "SHB", 17)
        cw, ch = p.w*0.3, p.h*0.19
        items = [
            ("rohlík zmizel z lavičky (strana 7)", lambda x, y: (rohlik(x - 26, y + 14, 0.8), drobky(x + 16, y + 6, 20, 6))),
            ("stužka a sponka zmizely z okna (strana 11)", lambda x, y: (stuzka(x - 16, y + 12, 0.9), sponka(x + 22, y + 14, 1.1))),
            ("šramot venku ve zdi (strana 10)", lambda x, y: stone_wall(x - 34, y, x + 34, y + 34, 3, rows=10)),
            ("kdo to byl u Joeyho? (strana 8)", lambda x, y: joey_kavka(x - 20, y - 2, 0.75)),
            ("stopičky a černé pírko (strana 13)", lambda x, y: (bird_prints(x - 34, y + 8, 0.8, 3, 6), kavci_pero(x + 22, y + 2, 1.0, -30))),
            ("větvičky pod věží (strana 14)", lambda x, y: vetvicky(x, y + 6, 60, 2)),
            ("Joeyho chlupy (strana 14)", lambda x, y: chlup(x - 4, y + 10, 1.6)),
            ("„KJA! KJA!“ ráno (strana 16)", lambda x, y: hand_text(x - 40, y + 14, 80, "KJA!", "SHB", 20)),
            ("očička a stužka v díře (strana 16)", lambda x, y: putlog(x, y + 20, 26, eyes=True, ribbon=True)),
        ]
        for i, (txt, pic) in enumerate(items):
            cx = p.X(0.04) + (i % 3)*(cw + p.w*0.02); cy = p.Y(0.82) - (i//3 + 1)*(ch + 10)
            shape(rrect(cx, cy, cw, ch, 8), 1.0, 1.2)
            hand_text(cx + 6, cy + ch - 20, 30, str(i + 1), "SHB", 16, align="left")
            C.saveState(); C.clipPath(poly(rrect(cx + 2, cy + 2, cw - 4, ch - 4, 7)), stroke=0, fill=0)
            with T(cx + cw/2, cy + 50, 1.5):
                pic(0, 0)
            C.restoreState()
            hand_text(cx + 8, cy + 22, cw - 16, txt, "SH", 10.5, lead=12)
        by = p.Y(0.82) - 3*(ch + 10)
        hand_text(p.X(0.05), by - 26, p.w*0.9, "Ukaž prstem! Kdo to byl? A která díra je čtrnáctá?", "SH", 14)
        with T(p.X(0.5), p.Y(0.03), 1.0, rot=180):
            hand_text(-p.w*0.45, 0, p.w*0.9, "Kavka! Bydlí v díře ve zdi věže a nosí si domů měkké věci.", "SH", 12)
            hand_text(-p.w*0.45, -15, p.w*0.9, "A její díra je čtrnáctá: XIV!", "SH", 12)
    page_end()


# =================================================================== 18 counting the holes; the bird flies out
def page_count():
    R = rows([(280, [1]), (230, [0.5, 0.5]), (240, [1])])
    with Pn(*R[0]) as p:
        gy, hl = nadvori(p, 0.2, 181, tower_x=0.76, tower_w=0.36, palace=False, sky_g=P.DAWN_SKY,
                         marks={14: dict(ribbon=True, twigs=True)})
        alica(p.X(0.14), p.Y(0.03), 1.1, mood="determined", right="front", left="front", look=(1, 0.5),
              item=lambda x, y: vez_kresba(x - 12, y - 34, 26, 32, 0))
        hanka(p.X(0.36), p.Y(0.03), 1.15, mood="wow", right="point", look=(1, 0.5), item=None)
        cap(p, "Alica a Hanka běží na nádvoří.", w=160, where="tl")
        say(p, "Která díra to je?", *ha(p.X(0.14), p.Y(0.03), 1.1), w=80, area=(0.0, 0.3))
        say(p, "Tamta! Se stužkou!", *hh(p.X(0.36), p.Y(0.03), 1.15), w=90, area=(0.26, 0.56))
    with Pn(*R[1], bg=0.95) as p:
        vez_kresba(p.X(0.44), p.Y(0.05), p.w*0.52, p.h*0.86, 0, mark=14, numbers=True)
        keep_clear(p, p.X(0.43), p.Y(0.04), p.X(0.97), p.Y(0.92), "kresba")
        cap(p, "Alica počítá díry na Bětčině obrázku.", w=100, where="tl")
    with Pn(*R[2]) as p:
        gy, hl = nadvori(p, 0.3, 182, tower_x=None, birds=False, sky_g=P.DAWN_SKY)
        alica(p.X(0.74), p.Y(0.03), 1.0, flip=True, mood="wow", left="up", right="up", look=(-1, 0.3))
        say(p, "…třináct, čtrnáct! Čtrnáctá díra! XIV!", *ha(p.X(0.74), p.Y(0.03), 1.0), w=120, area=(0.0, 0.62))
    with Pn(*R[3]) as p:
        gy, hl = nadvori(p, 0.2, 183, tower_x=0.7, tower_w=0.4, palace=False, sky_g=P.DAWN_SKY, birds=False,
                         marks={14: dict(ribbon=True, twigs=True)})
        cx, cy, sz = hl[13]
        kavka(cx - 50, cy + 30, 1.3, pose="fly", flip=True)
        sfx(cx - 120, cy + 60, "KJA!", 22, 8)
        hanka(p.X(0.14), p.Y(0.03), 1.15, mood="wow", right="point", look=(1, 0.6))
        J(p, p.X(0.36), p.Y(0.03), 1.0, mood="bark")
        say(p, "Černý ptáček! Vyletěl z té díry!", *hh(p.X(0.14), p.Y(0.03), 1.15), w=110, area=(0.0, 0.4))
    page_end()


# =================================================================== 19 the kastelánka: a jackdaw
def page_kavka():
    R = rows([(270, [1]), (220, [1/3, 1/3, 1/3]), (260, [1])])
    with Pn(*R[0]) as p:
        gy, hl = nadvori(p, 0.24, 191, tower_x=0.86, tower_w=0.24, sky_g=P.DAWN_SKY, birds=False)
        kavka_dawn(p, p.X(0.7), gy + p.h*0.28 + 12, 1.0)
        kastelanka(p.X(0.16), p.Y(0.03), 0.92, mood="happy", right="up", look=(1, 0.6))
        hanka(p.X(0.4), p.Y(0.03), 1.1, flip=True, mood="think", look=(-1, 0.2))
        deda(p.X(0.6), p.Y(0.03), 0.9, flip=True, mood="surprised", look=(-1, 0.3))
        say(p, "To je kavka. Bydlí v díře ve zdi věže.", *hk(p.X(0.16), p.Y(0.03), 0.92), w=120, area=(0.0, 0.4))
        say(p, "A ona nám vzala stužku?", *hh(p.X(0.4), p.Y(0.03), 1.1), w=90, area=(0.3, 0.6))
    pics = [("Kavky si vystýlají hnízdo měkkými věcmi.", 0),
            ("Chlupy si vytrhají i zvířatům ze zad.", 1),
            ("A o jídlo se rády dělí.", 2)]
    for k, (txt, kind) in enumerate(pics):
        with Pn(*R[1 + k], bg=0.95) as p:
            fill(_rect(p.x, p.y, p.x + p.w, p.Y(0.3)), P.SPRING_GRASS)
            if kind == 0:
                kavka(p.X(0.4), p.Y(0.3), 1.6, pose="walk", item=lambda x, y: stuzka(x + 12, y - 6, 0.5, -30))
                hnizdo(p.X(0.8), p.Y(0.3), 0.6, items=False)
            elif kind == 1:
                joey_kavka(p.X(0.34), p.Y(0.28), 1.1)
            else:
                kavka(p.X(0.28), p.Y(0.3), 1.3, pose="perch", item=lambda x, y: rohlik(x + 8, y - 2, 0.35))
                kavka(p.X(0.72), p.Y(0.3), 1.3, pose="perch", flip=True)
            hand_text(p.X(0.04), p.Y(0.93) - 12, p.w*0.92, txt, "SH", 11, lead=13)
    with Pn(*R[4]) as p:
        gy, hl = nadvori(p, 0.3, 192, tower_x=None, birds=False)
        tonda(p.X(0.12), p.Y(0.03), 1.0, mood="surprised", look=(1, 0))
        kastelanka(p.X(0.36), p.Y(0.03), 0.92, flip=True, mood="grin", look=(-1, 0))
        alica(p.X(0.62), p.Y(0.03), 1.05, flip=True, mood="determined", right="up", look=(-1, 0))
        verka_old(p.X(0.86), p.Y(0.03), 0.9, flip=True, mood="wow", look=(-1, 0))
        say(p, "Takže můj rohlík snědly kavky?", *htd(p.X(0.12), p.Y(0.03), 1.0), w=100, area=(0.0, 0.3))
        say(p, "Ano. A ještě se o něj podělily.", *hk(p.X(0.36), p.Y(0.03), 0.92), w=110, area=(0.2, 0.52))
        say(p, "A jejich díra je čtrnáctá. XIV! Tam bude poklad!", *ha(p.X(0.62), p.Y(0.03), 1.05), w=130, area=(0.48, 0.8))
        say(p, "Že by…?", *hv(p.X(0.86), p.Y(0.03), 0.9), w=60, area=(0.78, 1.0))
    page_end()


# =================================================================== 20 the jackdaw fact page
def page_facts():
    with Pn(M, 40, W-2*M, H-80, bg=0.97) as p:
        hand_text(p.X(0.04), p.Y(0.955), p.w*0.92, "Kavka: co o ní víme", "SHB", 28)
        hand_text(p.X(0.04), p.Y(0.915), p.w*0.92, "Paní kastelánka vypráví. Bětka kreslí.", "SH", 13)
        facts = [
            ("Je velká jako holub. Ze všech našich černých ptáků je nejmenší.",
             lambda x, y: (kavka(x - 30, y - 20, 1.7), holub(x + 34, y - 20, 1.4, flip=True))),
            ("Je černá, jen zátylek má stříbrně šedý. A oči má světlé, skoro bílé.",
             lambda x, y: kavka(x - 30, y - 50, 3.6)),
            ("Volá „kja! kja!“. Proto se jí říká kavka.",
             lambda x, y: (kavka(x - 24, y - 20, 1.6, flip=False), hand_text(x + 6, y + 2, 60, "KJA!", "SHB", 18))),
            ("Hnízdí v dírách: ve stromech, ve skalách, v komínech a ve zdech hradů.",
             lambda x, y: (stone_wall(x - 60, y - 30, x + 60, y + 30, 5, rows=12), putlog(x, y, 24, bird=True))),
            ("Pod hnízdem leží větvičky, které se jí nevešly do díry.",
             lambda x, y: (stone_wall(x - 60, y - 6, x + 60, y + 34, 6, rows=12), putlog(x, y + 16, 20, twigs=True),
                           vetvicky(x, y - 24, 60, 4))),
            ("Hnízdo vystýlá chlupy, peřím, vlnou, mechem, hadříky i papírem.",
             lambda x, y: hnizdo(x, y - 24, 1.2)),
            ("Kavky jsou v páru celý život. Vejce snášejí v dubnu a květnu, v červnu mladé vylétnou.",
             lambda x, y: (kavka(x - 30, y - 20, 1.4), kavka(x + 30, y - 20, 1.4, flip=True),
                           kavka(x, y - 22, 0.9, young=True))),
            ("Jsou moc chytré a rády se dělí o jídlo, i s ostatními kavkami.",
             lambda x, y: (kavka(x - 28, y - 20, 1.4, item=lambda a, b: rohlik(a + 8, b - 2, 0.4)), kavka(x + 30, y - 20, 1.4, flip=True))),
            ("V roce 2001 byla kavka Ptákem roku. Všichni divocí ptáci u nás jsou chránění.",
             lambda x, y: (kavka(x, y - 20, 1.8), star(x - 40, y + 14, 8, P.TAG_STAR), star(x + 40, y + 14, 8, P.TAG_STAR))),
        ]
        cw, ch = p.w*0.92/3, p.h*0.27
        for i, (txt, pic) in enumerate(facts):
            cx = p.X(0.04) + (i % 3)*cw; cy = p.Y(0.88) - (i//3 + 1)*(ch + 6)
            shape(rrect(cx + 4, cy, cw - 8, ch, 8), 1.0, 1.1)
            C.saveState(); C.clipPath(poly(rrect(cx + 6, cy + 2, cw - 12, ch - 4, 7)), stroke=0, fill=0)
            pic(cx + cw/2, cy + ch*0.66)
            C.restoreState()
            hand_text(cx + 10, cy + ch*0.36, cw - 20, txt, "SH", 10.5, lead=12.5)
        keep_clear(p, p.x, p.y, p.x + p.w, p.y + p.h, "facts")
        hand_text(p.X(0.04), p.Y(0.025), p.w*0.92, "Hnízdo kavek nerušíme. Klub vzal jen svoje věci, když mladé už vylétly.",
                  "SHB", 12)
    page_end()


# =================================================================== 21 the ladder; Hanka climbs
def page_ladder():
    R = rows([(280, [1]), (220, [0.5, 0.5]), (250, [1])])
    with Pn(*R[0]) as p:
        gy, hl = nadvori(p, 0.2, 211, tower_x=0.78, tower_w=0.34, palace=False, marks={14: dict(ribbon=True, twigs=True)})
        kastelanka(p.X(0.18), p.Y(0.03), 0.92, mood="happy", right="front", look=(1, 0),
                   item=lambda x, y: ladder(x + 10, y - 60, y + 70, 24))
        alica(p.X(0.42), p.Y(0.03), 1.05, flip=True, mood="worried", look=(-1, 0))
        say(p, "Mladé kavky už vylétly. Můžeme se tam opatrně podívat.", *hk(p.X(0.18), p.Y(0.03), 0.92), w=140,
            area=(0.0, 0.36))
        say(p, "Ale ta díra je hrozně malá.", *ha(p.X(0.42), p.Y(0.03), 1.05), w=90, area=(0.3, 0.6))
    with Pn(*R[1]) as p:
        gy, hl = nadvori(p, 0.3, 212, tower_x=None, birds=False)
        deda(p.X(0.22), p.Y(0.03), 0.85, mood="think", look=(1, 0))
        rybar(p.X(0.74), p.Y(0.03), 0.85, flip=True, mood="happy", rod=False, look=(-1, 0))
        say(p, "Velká ruka tam neprojde.", *hdd(p.X(0.22), p.Y(0.03), 0.85), w=100, area=(0.0, 0.56))
        say(p, "Moje taky ne.", *hf(p.X(0.7), p.Y(0.03), 0.92), w=70, area=(0.5, 1.0))
    with Pn(*R[2]) as p:
        gy, hl = nadvori(p, 0.3, 213, tower_x=None, birds=False)
        hanka(p.X(0.5), p.Y(0.03), 1.25, mood="determined", right="up", look=(-1, 0))
        say(p, "Já mám nejmenší ruku!", *hh(p.X(0.5), p.Y(0.03), 1.25), w=90, area=(0.0, 1.0))
    with Pn(*R[3]) as p:
        gy, hl = nadvori(p, 0.06, 214, tower_x=0.66, tower_w=0.56, tower_h=p.h*1.2, palace=False, birds=False,
                         marks={14: dict(ribbon=True, twigs=True)})
        cx, cy, sz = hl[13]
        ladder(cx + 30, gy, cy - 4, 30)
        kastelanka(cx + 32, cy - 150, 0.8, mood="happy", look=(-1, 0.5), shadow=False, right="up", left="up")
        hanka(cx + 30, cy - 82, 0.95, flip=True, mood="determined", right="up", left="front", look=(-1, 0.5), shadow=False,
              item=lambda x, y: torch(x, y, 140))
        deda(p.X(0.14), gy, 0.82, mood="worried", right="front", look=(1, 0.5))
        J(p, p.X(0.32), gy, 0.9, mood="sad")
        kl(p.X(0.48), p.Y(0.05), 20)
        cap(p, "Hanka leze nahoru. Paní kastelánka ji jistí.", w=170, where="tl")
        say(p, "Opatrně, Hani!", *hdd(p.X(0.14), gy, 0.82), w=80, area=(0.0, 0.3))
    page_end()


# =================================================================== 22 Hanka at the hole (full page)
def page_hole():
    with Pn(M, 40, W-2*M, H-80) as p:
        _panel_fill(p, P.PUTLOG)
        glow(p.X(0.5), p.Y(0.42), 300, 0.1)
        torch_beam(p.X(0.16), p.Y(0.1), p.X(0.95), p.Y(0.75), p.X(0.95), p.Y(0.05), 0.25)
        stone_wall(p.x - 5, p.y - 5, p.X(0.12), p.y + p.h + 5, 22, g=P.CASTLE_WALL_DARK, rows=22)
        hnizdo(p.X(0.55), p.Y(0.2), 3.4)
        plechovka2(p.X(0.84), p.Y(0.42), 2.6)
        for k in range(8):
            a = k*math.tau/8
            stroke([(p.X(0.84) + math.cos(a)*70, p.Y(0.42) + 40 + math.sin(a)*70),
                    (p.X(0.84) + math.cos(a)*86, p.Y(0.42) + 40 + math.sin(a)*86)], LINE*1.2, g=P.TENT_GLOW)
        hanka(p.X(0.04), p.Y(-0.32), 4.2, mood="wow", right="front", look=(1, 0.1), item=lambda x, y: torch(x, y, 10),
              shadow=False)
        hand_text(p.X(0.3), p.Y(0.9), p.w*0.65, "Hnízdo z větviček. Stužka, sponka, Joeyho chlupy…", "SHB", 18, g=1.0, lead=22)
        hand_text(p.X(0.3), p.Y(0.82), p.w*0.65, "A vzadu se něco leskne!", "SHB", 18, g=1.0)
    page_end()


# =================================================================== 23 things back; the name
def page_back():
    R = rows([(280, [1]), (210, [0.5, 0.5]), (260, [1])])
    with Pn(*R[0]) as p:
        gy, hl = nadvori(p, 0.3, 231, tower_x=None, birds=False)
        betka(p.X(0.14), p.Y(0.03), 1.25, hat=False, mood="grin", right="up", look=(1, 0), item=lambda x, y: stuzka(x + 4, y + 2, 0.6, 60))
        alica(p.X(0.42), p.Y(0.03), 1.05, mood="grin", right="up", look=(1, 0), item=lambda x, y: sponka(x, y + 2, 0.9))
        tonda(p.X(0.7), p.Y(0.03), 1.0, mood="worried", look=(-1, 0))
        say(p, "Moje stužka!", *hbe(p.X(0.14), p.Y(0.03), 1.25), w=70, area=(0.0, 0.3))
        say(p, "Moje sponka!", *ha(p.X(0.42), p.Y(0.03), 1.05), w=70, area=(0.26, 0.56))
        say(p, "A můj rohlík mají kavky v bříšku!", *htd(p.X(0.7), p.Y(0.03), 1.0), w=110, area=(0.52, 1.0))
    with Pn(*R[1]) as p:
        gy, hl = nadvori(p, 0.3, 232, tower_x=None, birds=False)
        hanka(p.X(0.3), p.Y(0.03), 1.15, mood="grin", right="front", look=(1, 0),
              item=lambda x, y: plechovka2(x + 6, y - 14, 0.7))
        deda(p.X(0.72), p.Y(0.03), 0.92, flip=True, mood="wow", look=(-1, 0))
        say(p, "A tohle bylo úplně vzadu!", *hh(p.X(0.3), p.Y(0.03), 1.15), w=90, area=(0.0, 0.5))
    with Pn(*R[2]) as p:
        gy, hl = nadvori(p, 0.3, 233, tower_x=None, birds=False)
        deda(p.X(0.4), p.Y(0.03), 0.95, mood="wow", right="front", look=(1, 0),
             item=lambda x, y: plechovka2(x + 4, y - 14, 0.75))
        say(p, "Druhá plechovka Klubu Hvězdička!", *hdd(p.X(0.4), p.Y(0.03), 0.95), w=110, area=(0.0, 1.0))
    with Pn(*R[3]) as p:
        gy, hl = nadvori(p, 0.2, 234, tower_x=0.82, tower_w=0.3, tower_h=p.h*0.6, palace=False, birds=False)
        kavka_dawn(p, p.X(0.82) - p.w*0.06, gy + p.h*0.6 + 1, 1.0)
        kastelanka(p.X(0.14), p.Y(0.03), 0.92, mood="happy", look=(1, 0.3))
        hanka(p.X(0.38), p.Y(0.03), 1.15, mood="grin", right="wave", look=(1, 0.6))
        betka(p.X(0.58), p.Y(0.03), 1.2, hat=False, mood="grin", look=(1, 0.5))
        say(p, "Hnízdo necháme. Kavky se sem na jaře vrátí.", *hk(p.X(0.14), p.Y(0.03), 0.92), w=130, area=(0.0, 0.34))
        say(p, "Budeš se jmenovat Kája!", *hh(p.X(0.38), p.Y(0.03), 1.15), w=90, area=(0.28, 0.56))
        say(p, "Kavka Kája!", *hbe(p.X(0.58), p.Y(0.03), 1.2), w=70, area=(0.5, 0.72))
    page_end()


# =================================================================== 24 the tin: Věrka remembers; the star map and the key
def page_tin():
    R = rows([(260, [1]), (230, [1]), (250, [0.5, 0.5])])
    with Pn(*R[0]) as p:
        gy, hl = nadvori(p, 0.3, 241, tower_x=None, birds=False)
        verka_old(p.X(0.2), p.Y(0.03), 0.95, mood="wow", right="front", look=(1, 0),
                  item=lambda x, y: plechovka2(x + 4, y - 14, 0.7))
        deda(p.X(0.56), p.Y(0.03), 0.92, flip=True, mood="grin", look=(-1, 0))
        rybar(p.X(0.82), p.Y(0.03), 0.9, flip=True, mood="happy", rod=False, look=(-1, 0))
        say(p, "Teď si vzpomínám! Čtrnáctá díra!", *hv(p.X(0.2), p.Y(0.03), 0.95), w=110, area=(0.0, 0.42))
        say(p, "Pod ní tenkrát ležela hromada kamení. Vylezli jsme na ni.", *hdd(p.X(0.56), p.Y(0.03), 0.92), w=140,
            area=(0.38, 1.0))
    with Pn(*R[1], bg=0.9) as p:
        _panel_fill(p, P.SUMMER_SKY)
        stone_wall(p.X(0.4), p.y - 5, p.x + p.w + 5, p.y + p.h + 5, 242, rows=14)
        putlog(p.X(0.6), p.Y(0.62), 22)
        shape(bez((p.X(0.3), p.y - 5), (p.X(0.4), p.Y(0.3)), (p.X(0.6), p.Y(0.34)), (p.X(0.78), p.y - 5)), P.ROCK, LINE)
        for k in range(10):
            rd = random.Random(k)
            shape(ell(p.X(0.36 + rd.uniform(0, 0.36)), p.Y(rd.uniform(0.02, 0.24)), 10, 6, 14), P.ROCK_DARK, BG)
        young(p.X(0.55), p.Y(0.3), 0.9, "verka", mood="grin", right="up", look=(1, 0.5),
              item=lambda x, y: plechovka2(x, y - 4, 0.4, dirty=False))
        young(p.X(0.44), p.Y(0.24), 0.9, "deda", mood="happy", right="point", look=(1, 0.4))
        young(p.X(0.72), p.Y(0.2), 0.9, "franta", flip=True, mood="happy", look=(-1, 0.4))
        bg_fill(p, P.LETTER_PAPER, 0.25)
        cap(p, "Kdysi dávno…", w=90, where="tl")
        say(p, "Čtrnáctá díra. To nikdo neuhodne!", *hyv(p.X(0.55), p.Y(0.3), 0.9), w=120, area=(0.1, 0.5))
    with Pn(*R[2], bg=0.95) as p:
        hvezdna_mapa(p.X(0.08), p.Y(0.14), p.w*0.6, p.h*0.5, -4)
        klicek(p.X(0.78), p.Y(0.35), 1.3, 60)
        keep_clear(p, p.X(0.06), p.Y(0.1), p.X(0.95), p.Y(0.7), "mapa")
        cap(p, "Uvnitř je mapa hvězd a malý klíček.", w=160, where="tl")
    with Pn(*R[3], bg=0.95) as p:
        shape(_rect(p.X(0.1), p.Y(0.1), p.X(0.9), p.Y(0.6)), P.LETTER_PAPER, LINE)
        hand_text(p.X(0.14), p.Y(0.45), p.w*0.72, "Poslední poklad čeká tam, kde jsou hvězdy nejblíž.", "SH", 14, lead=18)
        star(p.X(0.82), p.Y(0.18), 7, P.TAG_STAR)
        keep_clear(p, p.X(0.1), p.Y(0.1), p.X(0.9), p.Y(0.6), "vzkaz")
        cap(p, "A vzkaz:", w=80, where="tl")
    page_end()


# =================================================================== 25 sunset on the wall
def page_sunset():
    R = rows([(330, [1]), (190, [0.5, 0.5]), (230, [1])])
    with Pn(*R[0]) as p:
        _panel_fill(p, P.DUSK_SKY)
        hills(p, p.Y(0.3), 30, P.FAR_FIELD, 5)
        wooded_hill(p, p.Y(0.3), 251, P.FOREST_DARK)
        kavky_sky(p.X(0.55), p.Y(0.7), p.X(0.95), p.Y(0.9), 5, 2, 0.9)
        wy = p.Y(0.12)
        who = [(0.1, lambda x, y: deda(x, y, 0.82, mood="happy", look=(1, 0.2))),
               (0.22, lambda x, y: verka_old(x, y, 0.8, mood="happy", look=(1, 0.2))),
               (0.33, lambda x, y: rybar(x, y, 0.78, mood="happy", rod=False, look=(1, 0.2))),
               (0.45, lambda x, y: tonda(x, y, 0.88, mood="grin", look=(1, 0.2))),
               (0.56, lambda x, y: betka(x, y, 1.05, hat=False, mood="happy", look=(1, 0.2))),
               (0.68, lambda x, y: alica(x, y, 1.0, mood="happy", look=(1, 0.3))),
               (0.8, lambda x, y: hanka(x, y, 1.05, mood="grin", right="wave", look=(1, 0.4)))]
        for fx, fn in who: fn(p.X(fx), wy)
        J(p, p.X(0.92), wy, 0.9, flip=True, mood="happy")
        fill(_rect(p.x - 5, p.y - 5, p.x + p.w + 5, wy + 30), P.CASTLE_WALL)
        stone_wall(p.x - 5, p.y - 5, p.x + p.w + 5, wy + 30, 252, rows=12)
        stroke([(p.x - 5, wy + 30), (p.x + p.w + 5, wy + 30)], LINE)
        kl(p.X(0.62), p.Y(0.06), 10)
        cap(p, "Večer. Celý Klub sedí na hradbě.", w=170, where="tl")
        say(p, "Rohlík, stužka, sponka i poklad. Všechno vyřešeno!", *ha(p.X(0.68), wy, 1.0), w=130, area=(0.3, 0.78))
        say(p, "Dobrou noc, Kájo!", *hh(p.X(0.8), wy, 1.05), w=80, area=(0.7, 1.0))
    with Pn(*R[1]) as p:
        gy = medvedi_prikop(p, 0.3, 253)
        _panel_fill(p, P.DUSK_SKY, 0.2)
        brtnik(p.X(0.4), p.Y(0.08), 0.9, pose="sit", mood="sleepy")
        brtnik(p.X(0.7), p.Y(0.06), 0.8, mood="sleepy", flip=True)
        cap(p, "Medvědi jdou spát.", w=110, where="tl")
    with Pn(*R[2]) as p:
        _panel_fill(p, P.DUSK_SKY)
        stone_wall(p.x - 5, p.y - 5, p.x + p.w + 5, p.y + p.h + 5, 254, rows=16)
        putlog(p.X(0.5), p.Y(0.5), 30, eyes=True)
        kavka(p.X(0.5) - 40, p.Y(0.5) + 18, 1.1, pose="perch")
        cap(p, "A kavky taky.", w=90, where="tl")
    with Pn(*R[3]) as p:
        gy, hl = nadvori(p, 0.3, 255, tower_x=None, birds=False, sky_g=P.DUSK_SKY)
        kastelanka(p.X(0.18), p.Y(0.03), 0.92, mood="happy", right="wave", look=(1, 0))
        tonda(p.X(0.5), p.Y(0.03), 1.0, flip=True, mood="grin", look=(-1, 0), right="front",
              item=lambda x, y: rohlik(x + 2, y - 2, 0.7))
        say(p, "Přijeďte zas, detektivové!", *hk(p.X(0.18), p.Y(0.03), 0.92), w=100, area=(0.0, 0.4))
        say(p, "Příště si rohlík schovám do kapsy!", *htd(p.X(0.5), p.Y(0.03), 1.0), w=120, area=(0.36, 0.8))
        cap(p, "Případ č. 14 vyřešen.", w=130, where="br")
    page_end()


# =================================================================== 26 Točník fact page
def page_tocnik():
    with Pn(M, 40, W-2*M, H-80, bg=0.97) as p:
        hand_text(p.X(0.04), p.Y(0.955), p.w*0.92, "Hrad Točník: co o něm víme", "SHB", 28)
        hand_text(p.X(0.04), p.Y(0.915), p.w*0.92, "Paní kastelánka vypráví.", "SH", 13)

        def cell_castle(x, y): castle_far(x, y - 40, 0.62)

        def cell_hall(x, y):
            palace_wall(x - 60, x + 60, y - 40, 50, 9, windows=(0.2, 0.45, 0.7), roof=True)

        facts = [
            ("Postavil ho král Václav IV. na konci čtrnáctého století. XIV. století!", cell_castle),
            ("Pod ním stojí starší hrad Žebrák. Když vyhořel, dal si král postavit nový hrad o kus výš.",
             lambda x, y: zebrak_ruin(x, y - 30, 1.4)),
            ("Znakem krále Václava byl ledňáček v zatočeném šátku.", lambda x, y: lednacek(x, y - 4, 1.2)),
            ("Hrad nikdy nikdo nedobyl. Husité ho obléhali tři dny a pak odtáhli.",
             lambda x, y: (stone_wall(x - 50, y - 36, x + 50, y + 10, 4, rows=12), battlement(x - 50, x + 50, y + 10, 10))),
            ("Dlouho neměl studnu. Pilo se dešťová voda z nádrže v příkopu.",
             lambda x, y: (shape(ell(x, y - 20, 50, 14, 30), P.POND_WATER, LINE), cloud(x, y + 14, 0.6))),
            ("Dnes v příkopu bydlí medvědi Martin a Agáta.",
             lambda x, y: (brtnik(x - 30, y - 34, 0.6), brtnik(x + 34, y - 34, 0.55, pose="sit", flip=True))),
            ("Velký sál paláce je druhý největší v Čechách. Větší je jen Vladislavský sál na Pražském hradě.", cell_hall),
            ("Střechu paláce stavěli tesaři dřevěným jeřábem jako ve středověku. Točili ho lidé, kteří chodili v kole.",
             lambda x, y: jerab(x, y - 36, 0.8)),
            ("Pověst: kdo chtěl na hrad, musel se třikrát otočit kolem hory. Proto Točník!",
             lambda x, y: (hanka(x, y - 40, 0.62, mood="grin", right="up", left="up", shadow=False), spin_lines(x, y - 40, 0.6))),
        ]
        cw, ch = p.w*0.92/3, p.h*0.27
        for i, (txt, pic) in enumerate(facts):
            cx = p.X(0.04) + (i % 3)*cw; cy = p.Y(0.88) - (i//3 + 1)*(ch + 6)
            shape(rrect(cx + 4, cy, cw - 8, ch, 8), 1.0, 1.1)
            C.saveState(); C.clipPath(poly(rrect(cx + 6, cy + 2, cw - 12, ch - 4, 7)), stroke=0, fill=0)
            pic(cx + cw/2, cy + ch*0.7)
            C.restoreState()
            hand_text(cx + 10, cy + ch*0.36, cw - 20, txt, "SH", 10.5, lead=12.5)
        keep_clear(p, p.x, p.y, p.x + p.w, p.y + p.h, "facts")
        hand_text(p.X(0.04), p.Y(0.025), p.w*0.92, "Na hradě je hodně schodů a vysoké zdi. Chodíme opatrně a držíme se dospělých.",
                  "SHB", 12)
    page_end()


# =================================================================== 27 activity (no pencil)
def page_quiz():
    with Pn(M, 40, W-2*M, H-80) as p:
        box = [(p.X(0.05), p.Y(0.905)), (p.X(0.95), p.Y(0.91)), (p.X(0.95), p.Y(0.905)+54), (p.X(0.05), p.Y(0.905)+52)]
        fill(box, 0.92)
        for a_, b_ in ((0, 1), (1, 2), (2, 3), (3, 0)): stroke([box[a_], box[b_]], 1.5)
        hand_text(p.X(0.05), p.Y(0.905)+18, p.w*0.9, "Detektivní zápisník", "SHB", 26)
        hand_text(p.X(0.05), p.Y(0.865), p.w*0.9, "Bez tužky. Stačí prst a dobré oči!", "SH", 13)
        hand_text(p.X(0.05), p.Y(0.82), p.w*0.9, "1. Římské číslice. Ukaž prstem, kolik hvězdiček patří ke které číslici.",
                  "SHB", 14, align="left")
        nums = ["I", "V", "X", "IV", "XIV"]
        counts = [5, 14, 1, 10, 4]
        for i, n in enumerate(nums):
            cx = p.X(0.12 + i*0.19); cy = p.Y(0.7)
            shape(rrect(cx - 40, cy - 6, 80, 50, 8), 1.0, 1.0)
            hand_text(cx - 40, cy + 12, 80, n, "SHB", 24)
        for i, c in enumerate(counts):
            cx = p.X(0.12 + i*0.19); cy = p.Y(0.58)
            shape(rrect(cx - 44, cy - 6, 88, 54, 8), 0.95, 1.0)
            for k in range(c):
                star(cx - 34 + (k % 5)*17, cy + 38 - (k//5)*15, 5, P.TAG_STAR)
        y2 = p.Y(0.5)
        hand_text(p.X(0.05), y2, p.w*0.9, "2. Najdi 5 rozdílů mezi obrázky věže.", "SHB", 14, align="left")
        pw, ph = p.w*0.44, 200
        with Pn(p.X(0.04), y2 - 20 - ph, pw, ph) as q:
            mini_tower(q, 0)
        with Pn(p.X(0.52), y2 - 20 - ph, pw, ph) as q:
            mini_tower(q, 1)
        y4 = y2 - 20 - ph - 30
        hidden_klic(p.X(0.09), y4 - 6, 13, -20)          # the legend: not one of the hidden ten
        hand_text(p.X(0.15), y4 - 4, p.w*0.8,
                  f"V sešitě je schovaných {N_HIDDEN} klíčů, jako je tenhle (ten se nepočítá). Najdeš je všechny?",
                  "SHB", 14, align="left", lead=18)
        pages = ", ".join(map(str, HID[:-1])) + " a " + str(HID[-1]) if HID else ""
        with T(p.X(0.5), p.Y(0.015), 1.0, rot=180):
            hand_text(-p.w*0.45, 0, p.w*0.9, f"Klíče jsou na stranách {pages}.", "SH", 10)
            hand_text(-p.w*0.45, -13, p.w*0.9, "I – 1 hvězdička, V – 5, X – 10, IV – 4, XIV – 14.", "SH", 10)
            hand_text(-p.w*0.45, -26, p.w*0.9, "Rozdíly: mráček, dveře, kavka na střeše, letící kavka, rohlík.", "SH", 10)
    page_end()


# =================================================================== 28 back cover: next time
def back_cover():
    with Pn(M, 40, W-2*M, H-80, bg=0.95) as p:
        hand_text(p.X(0.1), p.Y(0.93), p.w*0.8, "Příště v sešitě č. 15:", "SHB", 20)
        title(p.X(0.5), p.Y(0.84), "NOC PADAJÍCÍCH HVĚZD", 32)
        with Pn(p.X(0.08), p.Y(0.3), p.w*0.84, p.h*0.48, bg=0.9) as q:
            _panel_fill(q, P.NIGHT_MEADOW)
            night_stars(q, 0.35, 60, 15)
            for k in range(5):
                sx, sy = q.X(0.3 + k*0.12), q.Y(0.92 - k*0.05)
                stroke([(sx, sy), (sx - 40, sy - 30)], LINE*1.2, g=1.0)
                star(sx, sy, 3, 1.0)
            hills(q, q.Y(0.18), 40, P.FOREST_DARK, 6)
            hvezdna_mapa(q.X(0.66), q.Y(0.06), 120, 90, 6)
            alica(q.X(0.18), q.Y(0.04), 1.0, mood="wow", look=(1, 0.9))
            hanka(q.X(0.34), q.Y(0.04), 1.05, mood="wow", right="point", look=(1, 0.9))
            night_tint(q, 0.15)
        hand_text(p.X(0.1), p.Y(0.24), p.w*0.8, "Kde jsou hvězdy nejblíž? A co odemyká malý klíček?", "SH", 16, lead=21)
        hand_text(p.X(0.1), p.Y(0.13), p.w*0.8, "Klub Hvězdička se dívá na padající hvězdy.", "SHB", 16)
        hand_text(p.X(0.1), p.Y(0.015), p.w*0.8, "Velká a malá detektivka – sešit č. 14", "SH", 13, g=0.35)
    PAGE[0] += 1; cv.showPage()


cover(); page_cast(); page_chalupa(); page_walk(); page_gate(); page_courtyard(); page_hunt(); page_bears()
page_evening(); page_night(); page_morning(); page_board(); page_sill(); page_twigs(); page_guide(); page_dawn()
page_stop(); page_count(); page_kavka(); page_facts(); page_ladder(); page_hole(); page_back(); page_tin()
page_sunset(); page_tocnik(); page_quiz(); back_cover()
cv.save()
print("ok", PAGE[0] - 1, "pages")
import letter
if letter.MISSING: PROBLEMS.append("no glyph in the font for: " + " ".join(sorted(letter.MISSING)))
if len(HID) != N_HIDDEN: PROBLEMS.append(f"{len(HID)} hidden keys drawn, the notebook promises {N_HIDDEN}")
for pr in PROBLEMS: print("ORDER/LAYOUT:", pr)
if PROBLEMS: sys.exit(1)
