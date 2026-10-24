"""Velká a malá detektivka, issue 12: Tajemné šipky (outline: vault topics/comic-series/issue12-outline)"""
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
from letter import Panel, caption, bubble, sfx, title, series_title, hand_text, lines_of, thought, shout
from tracks import dog_print
from props_extra import flour_patch
from pond import verka_old, rybar, stump, reeds, willow, water, torch_beam
from winter import betka
from joeyday import hajny, bone
from skola import mama, tata, vito, hobliny, morce, home, table, spoluzak
from velikonoce import *
from narozeniny import *
import chars3

W, H = A4
M = 28; GUT = 9; TOP = H - 30
OUT = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                   "comics", "velka_a_mala_detektivka", "12_tajemne_sipky.pdf")
os.makedirs(os.path.dirname(OUT), exist_ok=True)
cv = canvas.Canvas(OUT, pagesize=A4); lib.set_canvas(cv)
cv.setTitle("Velká a malá detektivka – Případ č. 12: Tajemné šipky")
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



# =================================================================== issue 12 helpers
HEAD.update({"mama": (107.6, 10.2), "tata": (122.6, 10.8), "betka": (70.2, 9.6), "franta": (118, 11.2),
             "hajny": (116, 11)})
HID = []   # pages with a hidden present, in order; the activity page's answer key is built from it
N_HIDDEN = 10


def keep_clear(p, x0, y0, x1, y1, what="picture"):
    p.heads.append(dict(txt=what, l=x0, r=x1, top=y1, b=y0))


def hx(who, x, y, s, top=2.0, up=2.1, wide=1.2):
    """hd() for a figure with something tall on its head (a bun, a straw hat): the tail stops above it"""
    tip = hd(who, x, y, s, up)
    if CUR:
        hy, hr = HEAD[who]
        b = CUR[-1].heads[-1]
        b["top"] = y + (hy + hr*top)*s; b["l"] = x - hr*wide*s; b["r"] = x + hr*wide*s
    return tip


def hm(x, y, s): return hx("mama", x, y, s, 1.85, 2.0, 1.2)        # máma's bun
def hv(x, y, s): return hx("verka", x, y, s, 2.2, 2.4, 2.0)        # Věrka's straw hat
def hf(x, y, s): return hx("franta", x, y, s, 1.9, 2.1, 1.6)       # Franta's bucket hat
def hj(x, y, s): return hx("hajny", x, y, s, 1.9, 2.1, 1.5)        # the hajný's felt hat
def ht(x, y, s): return hd("tata", x, y, s)
def ha(x, y, s): return hd("alica", x, y, s)
def hh(x, y, s): return hd("hanka", x, y, s)
def hb(x, y, s): return hd("babi", x, y, s)
def hdd(x, y, s): return hd("deda", x, y, s)
def htd(x, y, s): return hd("tonda", x, y, s)
def hbe(x, y, s): return hd("betka", x, y, s)


def dr(x, y, rot=0):
    """one of the 10 hidden presents"""
    hidden_darek(x, y, 13.5, rot, len(HID))
    HID.append(PAGE[0])


def J(p, x, y, s, flip=False, pose="stand", hat=False, **kw):
    """Joey, collar buried in his fur, head kept clear of balloons; hat: the party hat he hates"""
    joey(x, y, s, flip=flip, pose=pose, collar=False, **kw)
    if hat:
        party_hat(x + (-31 if flip else 31)*s, y + 57*s, s, 20 if flip else -20)
    l, r, b, t = (23, 46, 15, 40) if pose == "sniff" else (18, 41, 36, 61 + (18 if hat else 0))
    if flip: l, r = -r, -l
    keep_clear(p, x + l*s, y + b*s, x + r*s, y + t*s, "joey")


def KT(p, x, y, s, **kw):
    """malá Micka, kept clear of balloons"""
    kitten(x, y, s, **kw)
    keep_clear(p, x - 12*s, y, x + 12*s, y + 36*s, "kitten")


def inset(p, x, y, w, h, fn, label=None):
    """a round close-up inside a panel (seen through the lupa)"""
    shape(ell(x, y, w/2, h/2, 40), 1.0, LINE*1.2)
    C.saveState(); C.clipPath(poly(ell(x, y, w/2 - 1, h/2 - 1, 40)), stroke=0, fill=0)
    fn(x, y)
    C.restoreState()
    keep_clear(p, x - w/2, y - h/2, x + w/2, y + h/2, "inset")
    if label: hand_text(x - w/2, y - h/2 - 16, w, label, "SHB", 11)


def jar(x, y, h=14, g=P.JAM):
    sh_(rrect(x-5, y, 10, h, 2), P.JAR)
    clip_fill(rrect(x-5, y, 10, h, 2), [(x-6, y), (x+6, y), (x+6, y+h*0.7), (x-6, y+h*0.7)], g)
    stroke(rrect(x-5, y, 10, h, 2), BG, closed=True)
    sh_([(x-6, y+h), (x+6, y+h), (x+6, y+h+3), (x-6, y+h+3)], P.CLOTH_CHECK, BG*0.6)


def wall_clock(x, y, r=12):
    shape(ell(x, y, r, r, 30), 1.0, BG*1.3)
    for a in range(0, 360, 30):
        ra = math.radians(a); dot(x+math.cos(ra)*r*0.78, y+math.sin(ra)*r*0.78, 0.6, 0.2)
    stroke([(x, y), (x, y+r*0.6)], 1.0); stroke([(x, y), (x+r*0.45, y-r*0.1)], 1.0)


def kitchen(p, calendar=False, flour=False):
    """babička's kitchen at the chalupa; returns the floor line"""
    bg_fill(p, P.KITCHEN_WALL)
    for yy in range(int(p.Y(0.35)), int(p.y+p.h), 16): stroke([(p.x, yy), (p.x+p.w, yy)], BG*0.4, g=0.7)
    for xx in range(int(p.x), int(p.x+p.w), 16): stroke([(xx, p.Y(0.35)), (xx, p.y+p.h)], BG*0.4, g=0.7)
    shelf(p.X(0.02), p.X(0.02)+120, p.Y(0.72))
    for i, g in enumerate((P.JAM, 0.75, P.JAM, 0.55)): jar(p.X(0.02)+22+i*22, p.Y(0.72)+5, 14 + (i % 2)*4, g)
    wall_clock(p.X(0.93), p.Y(0.8), 13)
    if calendar: kalendar(p.X(0.74), p.Y(0.5), 46, 56)
    shape([(p.x, p.y), (p.x+p.w, p.y), (p.x+p.w, p.Y(0.35)), (p.x, p.Y(0.35))], 0.7, BG)
    if flour:
        for k, (fx, fy_) in enumerate(((0.3, 0.1), (0.55, 0.2), (0.7, 0.06))):
            flour_patch(p.X(fx), p.Y(fy_), 40 - k*8, 10)
    return p.Y(0.03)


def bedroom_home(p, night=False):
    """the girls' bedroom at home; returns the floor line"""
    bg_fill(p, P.BEDROOM_WALL)
    floor_y = p.y + 14
    shape([(p.x - 5, p.y - 5), (p.x + p.w + 5, p.y - 5), (p.x + p.w + 5, floor_y), (p.x - 5, floor_y)], P.FLOOR, BG)
    x0, x1, y0, y1 = p.X(0.06), p.X(0.26), p.Y(0.5), p.Y(0.88)
    shape([(x0 - 5, y0 - 5), (x1 + 5, y0 - 5), (x1 + 5, y1 + 5), (x0 - 5, y1 + 5)], P.DOOR_FRAME, BG)
    shape([(x0, y0), (x1, y0), (x1, y1), (x0, y1)], P.WINTER_NIGHT if night else P.SPRING_SKY, BG)
    if night: moon(x0 + (x1 - x0)*0.6, y0 + (y1 - y0)*0.65, 9)
    s_([((x0 + x1)/2, y0), ((x0 + x1)/2, y1)], BG*1.6, g=1.0)
    kids_drawing(p.X(0.4), p.Y(0.75), 36, 26, 4)
    if night: bg_fill(p, 0.0, 0.22)
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


def zzz(x, y, s=1.0):
    for i, (dx, dy, k) in enumerate(((0, 0, 1.0), (8, 9, 0.8), (14, 17, 0.6))):
        hand_text(x + dx*s - 10, y + dy*s, 20, "z", "SHB", 13*k*s)


def moon(x, y, r):
    shape(ell(x, y, r, r, 20), P.KRASLICE_YELLOW, LINE*0.6)
    fill(ell(x + r*0.55, y + r*0.2, r*0.85, r*0.85, 20), 0.97)


def home_table(p, y=0.3, x0=0.04, x1=0.6):
    """the kitchen table at home, in front of the figures: a cloth hanging to the floor. Returns its top"""
    shape([(p.X(x0), p.y - 4), (p.X(x1), p.y - 4), (p.X(x1), p.Y(y)), (p.X(x0), p.Y(y))], P.TABLECLOTH, BG)
    for k in range(1, 8):
        xx = p.X(x0) + (p.X(x1) - p.X(x0))*k/8
        stroke([(xx, p.y), (xx, p.Y(y))], BG*0.5, g=0.7, alpha=0.5)
    return p.Y(y)


def rain(p, n=60, seed=5):
    rd = random.Random(seed)
    bg_fill(p, 0.3, 0.25)
    for _ in range(n):
        x = p.x + rd.uniform(0, p.w); y = p.y + rd.uniform(0, p.h)
        stroke([(x, y), (x - 3, y - 10)], 0.6, g=0.25)


BED_LEN = 185


# =================================================================== 1 COVER
def cover():
    with Pn(M, 40, W-2*M, H-80) as p:
        gy = domov(p, 0.42, 11, house_x=0.28, house_s=1.5, garage_x=0.66, garage_kw=dict(door="closed"),
                   fence_=(0.0, 1.0), gate_x=0.83, paving=0.2, trees=((0.08, 1.2),), bushes=((0.5, 1.0),))
        for (fx, fy_, rot, kind) in ((0.06, 0.12, 0, "tata"), (0.28, 0.07, -8, "mama"), (0.6, 0.1, 20, "hanka"),
                                     (0.95, 0.2, 70, "tata")):
            sipka(p.X(fx), p.Y(fy_), 2.2, rot, kind)
        sipka(p.X(0.42), gy + 10, 1.6, 0, "tata")
        alica(p.X(0.42), p.Y(0.03), 2.0, mood="think", right="lens", lens=True, look=(1, -0.5))
        hanka(p.X(0.78), p.Y(0.03), 1.9, flip=True, mood="grin", right="hush", look=(-1, 0),
              item=lambda x, y: chalk_stick(x, y - 4, 1.4, 30, "hanka"))
        joey(p.X(0.14), p.Y(0.03), 1.6, mood="happy", collar=False)
        balonek(p.X(0.14) + 44*1.6, p.Y(0.03) + 46*1.6, P.BALLOON_RED, 1.4, 60, 8)
    box = [(M+34, H-236), (W-M-30, H-232), (W-M-34, H-48), (M+30, H-52)]
    fill([(x+3, y-3) for x, y in box], 0.0, 0.25); fill(box, 1.0)
    for a_, b_ in ((0, 1), (1, 2), (2, 3), (3, 0)): stroke([box[a_], box[b_]], 1.8)
    series_title(W/2, H-98, H-160, 40, 66)
    hand_text(M+40, H-190, W-2*M-80, "Alica, Hanka a Joey", "SHB", 20)
    hand_text(M+40, H-217, W-2*M-80, "Případ č. 12: Tajemné šipky", "SH", 15)
    magnifier(M+82, H-120, ang=-30, r=17)
    darek(W-M-96, H-150, 40, 30, P.PRESENT_RED, rot=-8)
    page_end()


# =================================================================== 2 WHO IS WHO
def page_cast():
    with Pn(M, 40, W-2*M, H-80) as p:
        hand_text(p.X(0.05), p.Y(0.95), p.w*0.9, "Kdo je kdo", "SHB", 28)
        cells = [
            ("Alica", "Má lupu. Brzy jí bude osm!", lambda x, y: alica(x, y, 0.9, mood="happy", right="lens", lens=True)),
            ("Hanka", "Má opičku a tajemství.", lambda x, y: hanka(x, y, 1.1, mood="grin", right="hush")),
            ("Joey", "Ví víc, než se zdá.", lambda x, y: joey(x, y, 1.2, mood="happy", collar=False)),
            ("Máma a táta", "Co to pořád šeptají?", lambda x, y: (mama(x - 22, y, 0.62, mood="whisper", outfit="home"),
                                                             tata(x + 22, y, 0.6, mood="grin"))),
            ("Babička a děda", "Na chalupě.", lambda x, y: (babicka(x - 22, y, 0.62, mood="happy"), deda(x + 22, y, 0.58, mood="happy"))),
            ("Micka", "Kočka z chalupy.", lambda x, y: cat(x, y, 1.1, mood="happy")),
            ("Tonda", "Kamarád od vedle.", lambda x, y: tonda(x, y, 0.8, mood="grin")),
            ("Bětka", "Vnučka pana Franty.", lambda x, y: betka(x, y, 1.0, hat=False, mood="grin")),
            ("Paní Věrka a pan Franta", "Z Klubu Hvězdička.", lambda x, y: (verka_old(x - 24, y, 0.55, mood="happy"),
                                                                           rybar(x + 22, y, 0.55, mood="happy", rod=False))),
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
        hand_text(p.x + 20, by + bh - 52, p.w*0.6,
                  "Kropenatka schovávala vajíčka ve stodole. Chtěla být maminka. A za tři týdny měla osm kuřátek!",
                  "SH", 13, align="left", lead=17)
        kropenatka(p.X(0.8), by + bh*0.22, 1.6)
        for k in range(3): kure(p.X(0.7) + k*30, by + bh*0.12 + (k % 2)*6, 1.3, flip=k == 1)
    page_end()


# =================================================================== 3 Saturday at the chalupa: the first arrows
def page_first():
    R = rows([(290, [1]), (220, [0.5, 0.5]), (240, [1])])
    with Pn(*R[0]) as p:
        gy = dvur(p, 0.4, 31, house_x=0.62, house_s=1.1, henhouse_x=0.9, henhouse_s=0.8, trees=((0.08, 0.9),))
        kropenatka(p.X(0.42), p.Y(0.08), 1.2, flip=True)
        for k, (fx, fy_) in enumerate(((0.33, 0.05), (0.37, 0.1), (0.47, 0.04), (0.51, 0.09))):
            kure(p.X(fx), p.Y(fy_), 1.3, flip=k % 2 == 0, pose="peck" if k == 2 else "stand")
        hanka(p.X(0.18), p.Y(0.03), 1.1, mood="wow", right="hug", look=(1, -0.2))
        alica(p.X(0.72), p.Y(0.03), 1.05, flip=True, mood="happy", look=(-1, -0.2))
        dr(p.X(0.96), p.Y(0.05), 10)
        cap(p, "Sobota na chalupě. Kuřátka rostou jako z vody.", w=220, where="tl")
        say(p, "Ahoj, kuřátka!", *hh(p.X(0.18), p.Y(0.03), 1.1), w=90, area=(0.0, 0.32))
    with Pn(*R[1]) as p:
        bg_fill(p, P.KITCHEN_WALL)
        lunch_note(p.X(0.5) - 78, p.Y(0.12), 3.0, 4)
        keep_clear(p, p.X(0.1), p.Y(0.1), p.X(0.92), p.Y(0.66), "note")
        cap(p, "Máma dala Alice do svačiny psaníčko. Vždycky ho podepíše srdíčkem.", w=210, where="tl")
    with Pn(*R[2]) as p:
        gy = dvur(p, 0.42, 32, clouds=False)
        fill([(p.x, p.Y(0.0)), (p.x + p.w, p.Y(0.0)), (p.x + p.w, p.Y(0.2)), (p.x, p.Y(0.12))], P.PAVING)
        sipka(p.X(0.65), p.Y(0.08), 1.6, 5, "mama")
        alica(p.X(0.25), p.Y(0.03), 1.15, mood="surprised", right="point", look=(1, -0.5))
        say(p, "Šipka! Kdo ji nakreslil?", *ha(p.X(0.25), p.Y(0.03), 1.15), w=110, area=(0.36, 1.0))
    with Pn(*R[3]) as p:
        gy = dvur(p, 0.42, 33, barn_x=0.92, barn_s=0.7)
        for k, fx in enumerate((0.36, 0.52, 0.68)):
            sipka(p.X(fx), p.Y(0.08) + k*4, 1.3, 4, "mama")
        alica(p.X(0.12), p.Y(0.03), 1.05, mood="think", right="chin", look=(1, -0.3))
        hanka(p.X(0.84), p.Y(0.03), 1.1, flip=True, mood="grin", right="hush", look=(-1, 0))
        say(p, "Šipky vedou… a pak nic. Končí uprostřed trávy!", *ha(p.X(0.12), p.Y(0.03), 1.05), w=150, area=(0.0, 0.55))
        say(p, "Hihihi!", *hh(p.X(0.84), p.Y(0.03), 1.1), w=70, area=(0.66, 1.0))
    page_end()


# =================================================================== 4 děda's shed: mňau
def page_shed():
    R = rows([(300, [1]), (210, [0.5, 0.5]), (240, [1])])
    with Pn(*R[0]) as p:
        gy = dvur(p, 0.42, 41, trees=((0.9, 1.0),))
        kulna(p.X(0.55), gy - 4, 1.4)
        sfx(p.X(0.42), p.Y(0.84), "MŇAU!", 26, 6)
        alica(p.X(0.14), p.Y(0.03), 1.05, mood="surprised", look=(1, 0.2))
        deda(p.X(0.82), p.Y(0.03), 0.95, flip=True, mood="worried", right="up", look=(-1, 0))
        say(p, "Dědo, co je v kůlně?", *ha(p.X(0.14), p.Y(0.03), 1.05), w=110, area=(0.0, 0.32))
        say(p, "Mňau? To… to byla straka!", *hdd(p.X(0.82), p.Y(0.03), 0.95), w=120, area=(0.66, 1.0))
    with Pn(*R[1]) as p:
        bg_fill(p, P.SPRING_GRASS)
        with T(p.X(0.5), p.Y(0.06), 2.6):
            sh_([(-34, 0), (34, 0), (34, 60), (-34, 60)], P.DOOR)
            for yy in (12, 46): s_([(-34, yy), (34, yy)], BG*0.6)
        scratches(p.X(0.3), p.Y(0.1), 3.4)
        milk_saucer(p.X(0.7), p.Y(0.05), 2.2)
        cap(p, "U dveří kůlny: škrábance a miska s mlékem.", w=180, where="tl")
    with Pn(*R[2]) as p:
        gy = dvur(p, 0.42, 42, clouds=False)
        alica(p.X(0.25), p.Y(0.03), 1.15, mood="think", right="lens", lens=True, look=(1, -0.4))
        say(p, "Straka, která pije mléko?", *ha(p.X(0.25), p.Y(0.03), 1.15), w=110, area=(0.4, 1.0))
    with Pn(*R[3]) as p:
        gy = dvur(p, 0.42, 43, clouds=False)
        kulna(p.X(0.78), gy - 4, 1.0)
        cat(p.X(0.62), p.Y(0.04), 1.3, flip=True, mood="happy")
        keep_clear(p, p.X(0.62) - 16, p.Y(0.04), p.X(0.62) + 16, p.Y(0.04) + 60, "micka")
        deda(p.X(0.4), p.Y(0.03), 0.95, flip=True, mood="happy", right="point", look=(-1, 0))
        alica(p.X(0.1), p.Y(0.03), 1.05, mood="think", right="chin", look=(1, 0))
        dr(p.X(0.93), p.Y(0.06), -15)
        say(p, "I Micka chce do kůlny.", *ha(p.X(0.1), p.Y(0.03), 1.05), w=110, area=(0.0, 0.3))
        say(p, "Do kůlny teď nesmí nikdo! Ani Micka. Ani ty.", *hdd(p.X(0.4), p.Y(0.03), 0.95), w=160, area=(0.22, 0.68))
    page_end()


# =================================================================== 5 babička's kitchen: flour; the calendar; going home
def page_flour():
    R = rows([(290, [1]), (220, [0.5, 0.5]), (240, [1])])
    with Pn(*R[0]) as p:
        fy = kitchen(p, calendar=True, flour=True)
        babicka(p.X(0.42), fy, 1.05, mood="surprised", right="up", left="up", look=(-1, 0),
                item=lambda x, y: flour_patch(x, y, 12, 8))
        flour_patch(p.X(0.42), fy + 55, 22, 14)
        alica(p.X(0.12), fy, 1.0, mood="surprised", look=(1, 0))
        say(p, "Babi, ty jsi celá od mouky!", *ha(p.X(0.12), fy, 1.0), w=120, area=(0.0, 0.3))
        say(p, "Alicko, do kuchyně teď nesmíš! Šup ven!", *hb(p.X(0.42), fy, 1.05), w=150, area=(0.25, 0.7))
    with Pn(*R[1]) as p:
        bg_fill(p, P.KITCHEN_WALL)
        with T(p.X(0.5), p.Y(0.05), 2.6):
            sh_([(-34, 0), (34, 0), (34, 64), (-34, 64)], P.DOOR)
            shape(ell(24, 30, 2.4, 2.4, 10), 0.85, LINE*0.6)
        for k, (fx, fy_) in enumerate(((0.36, 0.5), (0.6, 0.34), (0.5, 0.66))):
            with T(p.X(fx), p.Y(fy_), 1.0, rot=k*20 - 10):
                fill(ell(0, 0, 9, 10, 18), 1.0, 0.9)
                for f, a in enumerate((-40, -14, 6, 26)):
                    ra = math.radians(90 + a)
                    with T(math.cos(ra)*12, math.sin(ra)*12, 1.0, rot=a):
                        fill(ell(0, 2, 2.4, 6, 12), 1.0, 0.9)
                with T(-11, -2, 1.0, rot=50): fill(ell(0, 0, 2.6, 6, 12), 1.0, 0.9)
        cap(p, "Na dveřích bílé otisky rukou.", w=160, where="tl")
    with Pn(*R[2]) as p:
        bg_fill(p, P.KITCHEN_WALL)
        kalendar(p.X(0.5) - 50, p.Y(0.06), 100, 116, (4, 3))
        keep_clear(p, p.X(0.5) - 52, p.Y(0.06), p.X(0.5) + 52, p.Y(0.06) + 124, "kalendar")
        cap(p, "Na kalendáři je jeden den zakroužkovaný.", w=170, where="tl")
    with Pn(*R[3]) as p:
        gy = dvur(p, 0.42, 51, house_x=0.15, house_s=0.8)
        vito(p.X(0.58), p.Y(0.06), 1.2)
        alica(p.X(0.88), p.Y(0.03), 1.05, flip=True, mood="determined", right="up", look=(-1, 0))
        hanka(p.X(0.32), p.Y(0.03), 1.1, mood="worried", look=(1, 0))
        cap(p, "V neděli jedeme domů.", w=130, where="tl")
        say(p, "Já nic nevím!", *hh(p.X(0.32), p.Y(0.03), 1.1), w=80, area=(0.18, 0.5))
        say(p, "Babička peče a děda něco schovává. Tady se něco děje!", *ha(p.X(0.88), p.Y(0.03), 1.05), w=150, area=(0.55, 1.0))
    page_end()


# =================================================================== 6 home: arrows in the village
def page_village():
    R = rows([(300, [1]), (210, [0.5, 0.5]), (240, [1])])
    with Pn(*R[0]) as p:
        gy = domov(p, 0.45, 61, house_x=0.3, house_s=1.2, garage_x=0.62, fence_=(0.0, 1.0), gate_x=0.82, paving=0.22,
                   trees=((0.92, 0.9),))
        sipka(p.X(0.2), gy + 6, 1.4, 0, "tata")
        oil_smudge(p.X(0.2) + 42, gy + 4, 1.0)
        sipka(p.X(0.55), p.Y(0.06), 1.4, 180, "hanka")
        sipka(p.X(0.84), p.Y(0.12), 1.5, 15, "mama")
        alica(p.X(0.1), p.Y(0.03), 1.05, mood="wow", right="point", look=(1, 0.3))
        hanka(p.X(0.42), p.Y(0.03), 1.1, mood="worried", look=(-1, 0))
        dr(p.X(0.72), p.Y(0.05), 15)
        cap(p, "Pondělí doma ve vsi. A šipky jsou i tady!", w=210, where="tl")
        say(p, "Na plotě! A na chodníku!", *ha(p.X(0.1), p.Y(0.03), 1.05), w=110, area=(0.0, 0.34))
    with Pn(*R[1]) as p:
        bg_fill(p, P.SPRING_GRASS)
        fence(p.x, p.x + p.w, p.Y(0.1), p.h*0.75, 22)
        sipka(p.X(0.5), p.Y(0.66), 2.6, 0, "tata")
        oil_smudge(p.X(0.82), p.Y(0.62), 1.8)
        alica(p.X(0.18), p.Y(0.0), 1.0, mood="think", right="up", look=(1, 0.6))
        cap(p, "Tahle je hodně vysoko.", w=140, where="tr")
    with Pn(*R[2]) as p:
        bg_fill(p, P.PAVING)
        for k in range(5): s_([(p.x + k*50 + 20, p.y), (p.x + k*50 + 10, p.y + p.h)], BG*0.5)
        sipka(p.X(0.55), p.Y(0.3), 3.0, 180, "hanka")
        cap(p, "A tahle je malinká. Těsně u země.", w=170, where="tl")
    with Pn(*R[3]) as p:
        gy = domov(p, 0.45, 62, fence_=(0.0, 1.0), clouds=False)
        alica(p.X(0.14), p.Y(0.03), 1.15, mood="determined", right="up", look=(1, 0))
        hanka(p.X(0.42), p.Y(0.03), 1.15, mood="grin", look=(-1, 0))
        J(p, p.X(0.7), p.Y(0.03), 1.0, flip=True, mood="happy")
        say(p, "Zakládám případ číslo dvanáct: Tajemné šipky!", *ha(p.X(0.14), p.Y(0.03), 1.15), w=150, area=(0.0, 0.4))
        say(p, "Já ti pomůžu! Teda… já nic nevím.", *hh(p.X(0.42), p.Y(0.03), 1.15), w=130, area=(0.3, 0.75))
    page_end()


# =================================================================== 7 Tonda's chalky hands
def page_tonda():
    R = rows([(290, [1]), (220, [0.5, 0.5]), (240, [1])])
    with Pn(*R[0]) as p:
        gy = domov(p, 0.45, 71, house_x=0.8, house_s=1.0, fence_=(0.0, 0.6), paving=0.24)
        tonda(p.X(0.55), p.Y(0.03), 1.0, mood="surprised", right="front", look=(-1, 0),
              item=lambda x, y: chalk_stick(x, y - 2, 1.0, 20, "tata"))
        alica(p.X(0.12), p.Y(0.03), 1.05, mood="determined", right="point", look=(1, 0))
        J(p, p.X(0.3), p.Y(0.03), 1.0, mood="bark")
        say(p, "Tondo! Ty máš ruce celé od křídy!", *ha(p.X(0.12), p.Y(0.03), 1.05), w=130, area=(0.0, 0.42))
        say(p, "Já… musím domů!", *htd(p.X(0.55), p.Y(0.03), 1.0), w=100, area=(0.4, 0.8))
    with Pn(*R[1]) as p:
        gy = domov(p, 0.42, 72, clouds=False, paving=0.2)
        tonda(p.X(0.6), p.Y(0.03), 1.1, mood="worried", look=(1, 0), legs="walk")
        sfx(p.X(0.12), p.Y(0.75), "FRRR!", 18, -6)
        for k in range(3): stroke([(p.X(0.44) - k*14, p.Y(0.3) + k*12), (p.X(0.32) - k*14, p.Y(0.3) + k*12)], LINE*0.7, g=0.4)
    with Pn(*R[2]) as p:
        gy = domov(p, 0.42, 73, clouds=False, paving=0.2)
        alica(p.X(0.3), p.Y(0.03), 1.1, mood="determined", look=(1, 0), legs="walk")
        J(p, p.X(0.68), p.Y(0.03), 1.0, mood="happy")
        cap(p, "Za ním!", w=80, where="tr")
    with Pn(*R[3]) as p:
        gy = domov(p, 0.45, 74, house_x=0.12, house_s=0.9, fence_=(0.25, 1.0), paving=0.22, trees=((0.9, 0.9),))
        hanka(p.X(0.3), p.Y(0.03), 1.1, mood="grin", look=(1, 0), legs="walk")
        alica(p.X(0.55), p.Y(0.03), 1.05, mood="determined", look=(1, 0), legs="walk")
        dr(p.X(0.08), p.Y(0.05), 8)
        say(p, "Počkejte na mě!", *hh(p.X(0.3), p.Y(0.03), 1.1), w=100, area=(0.0, 0.42))
        say(p, "Tonda běží k návsi!", *ha(p.X(0.55), p.Y(0.03), 1.05), w=110, area=(0.42, 0.85))
    page_end()


# =================================================================== 8 the hopscotch; the card in his pocket
def page_panak():
    R = rows([(300, [1]), (210, [0.5, 0.5]), (240, [1])])
    with Pn(*R[0]) as p:
        gy = domov(p, 0.48, 81, trees=((0.1, 1.0), (0.86, 1.1)), paving=0.36)
        panak(p.X(0.5), p.Y(0.04), 1.6, 0)
        tonda(p.X(0.76), p.Y(0.03), 1.0, flip=True, mood="grin", right="point", look=(-1, -0.4))
        alica(p.X(0.2), p.Y(0.03), 1.05, mood="think", look=(1, -0.4))
        say(p, "Proč kreslíš šipky?", *ha(p.X(0.2), p.Y(0.03), 1.05), w=100, area=(0.0, 0.36))
        say(p, "Jaké šipky? Já kreslím panáka! Na skákání!", *htd(p.X(0.76), p.Y(0.03), 1.0), w=140, area=(0.55, 1.0))
    with Pn(*R[1]) as p:
        bg_fill(p, P.PAVING)
        panak(p.X(0.5), p.Y(0.04), 2.0, 0)
        keep_clear(p, p.X(0.25), p.Y(0.05), p.X(0.75), p.Y(0.7), "panak")
        cap(p, "Opravdu panák. Od jedničky do osmičky.", w=130, where="tl")
    with Pn(*R[2]) as p:
        bg_fill(p, P.HOODIE)
        with T(p.X(0.5), p.Y(0.2), 3.0):
            shape([(-30, 0), (30, 0), (30, 36), (-30, 36)], P.JEANS, LINE)
            stroke(bez((-24, 34), (-20, 22), (20, 22), (24, 34)), LINE)
        pozvanka(p.X(0.5) - 30, p.Y(0.4), 2.0, 12, word=False)
        with T(p.X(0.5), p.Y(0.2), 3.0):
            shape([(-24, 0), (24, 0), (24, 26), (-24, 26)], P.JEANS, LINE)
        keep_clear(p, p.X(0.2), p.Y(0.15), p.X(0.8), p.Y(0.68), "kapsa")
        cap(p, "Z Tondovy kapsy kouká bílá kartička.", w=150, where="tl")
    with Pn(*R[3]) as p:
        gy = domov(p, 0.48, 82, clouds=False, paving=0.36, trees=((0.9, 0.9),))
        alica(p.X(0.14), p.Y(0.03), 1.1, mood="determined", right="point", look=(1, 0))
        tonda(p.X(0.5), p.Y(0.03), 1.0, flip=True, mood="worried", right="up", look=(-1, 0), legs="walk")
        hanka(p.X(0.8), p.Y(0.03), 1.1, flip=True, mood="whisper", right="hush", look=(-1, 0))
        say(p, "Co to máš v kapse?", *ha(p.X(0.14), p.Y(0.03), 1.1), w=100, area=(0.0, 0.34))
        say(p, "Nic! Ahoj!", *htd(p.X(0.5), p.Y(0.03), 1.0), w=80, area=(0.36, 0.66))
        say(p, "Psst, Tondo!", *hh(p.X(0.8), p.Y(0.03), 1.1), w=90, area=(0.66, 1.0), whisper=True)
    page_end()


# =================================================================== 9 táta's garage: the wide tracks
def page_garage():
    R = rows([(300, [1]), (210, [0.5, 0.5]), (240, [1])])
    with Pn(*R[0]) as p:
        gy = domov(p, 0.48, 91, house_x=0.2, house_s=1.1, garage_x=0.6, garage_kw=dict(door="ajar"))
        mud_puddle(p.X(0.55), p.Y(0.22), 140, 34)
        tyre_track([(p.X(0.36), p.Y(0.14)), (p.X(0.5), p.Y(0.22)), (p.X(0.6), gy - 4)], True)
        sekacka(p.X(0.86), p.Y(0.1), 1.2, flip=True)
        tata(p.X(0.78), p.Y(0.03), 0.95, flip=True, mood="surprised", right="front", left="front", look=(-1, 0))
        oil_smudge(p.X(0.78) - 18, p.Y(0.03) + 62, 1.0); oil_smudge(p.X(0.78) + 6, p.Y(0.03) + 60, 1.0)
        alica(p.X(0.12), p.Y(0.03), 1.05, mood="think", look=(1, 0))
        say(p, "Tati, co děláš v garáži?", *ha(p.X(0.12), p.Y(0.03), 1.05), w=110, area=(0.0, 0.34))
        say(p, "Já? Opravuju… sekačku!", *ht(p.X(0.78), p.Y(0.03), 0.95), w=120, area=(0.5, 1.0))
    with Pn(*R[1]) as p:
        bg_fill(p, P.MUD)
        tyre_track([(p.X(0.1), p.Y(0.48)), (p.X(0.9), p.Y(0.53))], True, s=2.6)
        tyre_track([(p.X(0.1), p.Y(0.22)), (p.X(0.9), p.Y(0.26))], False, s=2.0)
        cap(p, "Široká stopa se zoubky. A dole tenká stopa od Alicina kola.", w=200, where="tl")
        keep_clear(p, p.X(0.05), p.Y(0.15), p.X(0.95), p.Y(0.62), "stopy")
    with Pn(*R[2]) as p:
        gy = domov(p, 0.48, 92, clouds=False)
        sekacka(p.X(0.72), p.Y(0.08), 2.0, flip=True)
        alica(p.X(0.24), p.Y(0.03), 1.15, mood="think", right="point", look=(1, -0.3))
        say(p, "Ale sekačka stojí tady venku!", *ha(p.X(0.24), p.Y(0.03), 1.15), w=110, area=(0.36, 1.0))
    with Pn(*R[3]) as p:
        gy = domov(p, 0.48, 93, garage_x=0.82, garage_kw=dict(door="closed"), clouds=False)
        alica(p.X(0.14), p.Y(0.03), 1.1, mood="determined", right="chin", look=(1, 0))
        J(p, p.X(0.62), p.Y(0.03), 1.0, pose="sniff", mood="happy")
        dr(p.X(0.4), p.Y(0.06), -10)
        say(p, "Táta má ruce od oleje. A v garáži něco schovává.", *ha(p.X(0.14), p.Y(0.03), 1.1), w=160, area=(0.0, 0.56))
    page_end()


# =================================================================== 10 Hanka's secret
def page_hanka():
    R = rows([(300, [1]), (210, [0.5, 0.5]), (240, [1])])
    with Pn(*R[0]) as p:
        fy = bedroom_home(p)
        bed_side(p.X(0.45), p.X(0.45) + BED_LEN, fy + 40)
        hanka(p.X(0.62), fy, 1.15, mood="surprised", right="front", look=(-1, -0.4))
        hobliny(p.X(0.7), fy + 4, 1.3, 5, 3)
        alica(p.X(0.18), fy, 1.05, mood="think", right="point", look=(1, -0.2))
        say(p, "Hani, co strkáš pod postel?", *ha(p.X(0.18), fy, 1.05), w=120, area=(0.0, 0.36))
        say(p, "Neřeknu! Je to tajemství!", *hh(p.X(0.62), fy, 1.15), w=110, area=(0.45, 0.85))
    with Pn(*R[1]) as p:
        bg_fill(p, P.FLOOR)
        hobliny(p.X(0.5), p.Y(0.16), 4.6, 7, 4)
        cap(p, "Z Hančiny kapsy padají hobliny.", w=150, where="tl")
    with Pn(*R[2]) as p:
        fy = bedroom_home(p)
        alica(p.X(0.3), fy, 1.2, mood="think", right="lens", lens=True, look=(1, -0.4))
        say(p, "Dřevo… Hanka byla dneska v lesní školce.", *ha(p.X(0.3), fy, 1.2), w=130, area=(0.42, 1.0))
    with Pn(*R[3]) as p:
        fy = bedroom_home(p)
        alica(p.X(0.18), fy, 1.1, mood="sad", look=(1, 0))
        hanka(p.X(0.62), fy, 1.15, flip=True, mood="worried", right="hug", look=(-1, 0))
        dr(p.X(0.92), fy + 6, 20)
        say(p, "Hani, ty jsi na čí straně?", *ha(p.X(0.18), fy, 1.1), w=110, area=(0.0, 0.4))
        say(p, "Na tvojí! Jenom… nemůžu nic říct.", *hh(p.X(0.62), fy, 1.15), w=130, area=(0.42, 0.85))
    page_end()


# =================================================================== 11 night: Hanka nearly tells
def page_night():
    R = rows([(380, [1]), (360, [1])])
    with Pn(*R[0]) as p:
        fy = bedroom_home(p, night=True)
        ax, ay = kid_in_bed(hanka, 36, p.X(0.06), p.X(0.06) + BED_LEN*0.8, fy + 40, 1.3, mood="whisper", right="hug")
        bx, by_ = kid_in_bed(alica, 45, p.X(0.95) - BED_LEN, p.X(0.95), fy + 40, 1.3, mood="sleepy")
        hh(ax, ay, 1.3); ha(bx, by_, 1.3)
        cap(p, "Večer. Poprvé nejsou Velká a malá detektivka na stejné straně.", w=200, where="tl")
        say(p, "Opičko, víš co? V sobotu má Alica naroz…", *hh(ax, ay, 1.3), w=150, area=(0.0, 0.55), whisper=True)
        say(p, "Psst!", *hh(ax, ay, 1.3), w=60, area=(0.0, 0.35), whisper=True)
    with Pn(*R[1]) as p:
        fy = bedroom_home(p, night=True)
        ax, ay = kid_in_bed(hanka, 36, p.X(0.06), p.X(0.06) + BED_LEN*0.8, fy + 40, 1.3, mood="surprised", right="hug")
        bx, by_ = kid_in_bed(alica, 45, p.X(0.95) - BED_LEN, p.X(0.95), fy + 40, 1.3, mood="sleepy")
        say(p, "Hm? Co je v sobotu?", *ha(bx, by_, 1.3), w=110, area=(0.5, 1.0))
        say(p, "Nic! Spinkej!", *hh(ax, ay, 1.3), w=90, area=(0.0, 0.5))
    page_end()


# =================================================================== 12 máma on the phone; the torn list; odd questions
def page_phone():
    R = rows([(270, [1]), (220, [0.5, 0.5]), (260, [1])])
    with Pn(*R[0]) as p:
        fy = home(p, 0.08)
        mama(p.X(0.36), fy, 1.0, outfit="home", mood="whisper", right="chin", look=(-1, 0),
             item=lambda x, y: phone(x + 2, y + 6, 2.2, 70))
        ty = home_table(p, 0.24, 0.04, 0.56)
        seznam(p.X(0.12), ty - 2, 44, 52, -8)
        alica(p.X(0.82), fy, 1.05, flip=True, mood="think", look=(-1, 0))
        say(p, "…ano, ve tři. Balónky koupím…", *hm(p.X(0.36), fy, 1.0), w=130, area=(0.0, 0.6), whisper=True)
        say(p, "Mami? Kdo to byl?", *ha(p.X(0.82), fy, 1.05), w=100, area=(0.62, 1.0))
    with Pn(*R[1]) as p:
        bg_fill(p, P.TABLE)
        seznam(p.X(0.28), p.Y(0.08), 100, 120, -4)
        keep_clear(p, p.X(0.2), p.Y(0.08), p.X(0.8), p.Y(0.72), "seznam")
        cap(p, "Utržený papírek.", w=110, where="tl")
    with Pn(*R[2]) as p:
        fy = home(p, 0.08)
        mama(p.X(0.4), fy, 1.0, outfit="home", mood="grin", right="wave", look=(1, 0))
        say(p, "To byla jen… babička!", *hm(p.X(0.4), fy, 1.0), w=110, area=(0.52, 1.0))
    with Pn(*R[3]) as p:
        gy = domov(p, 0.42, 121, house_x=0.88, house_s=0.8, paving=0.2, trees=((0.62, 0.9),))
        verka_old(p.X(0.12), p.Y(0.03), 0.92, mood="grin", look=(1, 0))
        betka(p.X(0.33), p.Y(0.03), 1.2, hat=False, mood="worried", right="hip", left="hip", look=(1, 0))
        alica(p.X(0.55), p.Y(0.03), 1.05, flip=True, mood="surprised", look=(-1, 0))
        say(p, "Alicko, máš ráda kočičky?", *hv(p.X(0.12), p.Y(0.03), 0.92), w=120, area=(0.0, 0.36))
        say(p, "A jakou barvu? Růžovou?", *hbe(p.X(0.33), p.Y(0.03), 1.2), w=110, area=(0.2, 0.5))
        say(p, "Proč se všichni tak divně ptají?", *ha(p.X(0.55), p.Y(0.03), 1.05), w=130, area=(0.42, 0.85))
    page_end()


# =================================================================== 13 the suspect board
def page_board():
    R = rows([(470, [1]), (270, [1])])
    with Pn(*R[0], bg=0.92) as p:
        shape(rrect(p.X(0.04), p.Y(0.04), p.w*0.92, p.h*0.82, 6), P.BOX, LINE*1.4)
        hand_text(p.X(0.04), p.Y(0.9), p.w*0.92, "Všichni jsou podezřelí!", "SHB", 22)
        def mug(fn, who, s, **kw):
            hy, hr = HEAD[who]
            return lambda x, y: fn(x, y + 78 - (hy + hr)*s, s, shadow=False, **kw)
        cards = [
            ("Tonda", mug(tonda, "tonda", 1.25, mood="worried")),
            ("babička", mug(babicka, "babi", 1.15, mood="surprised")),
            ("děda", mug(deda, "deda", 1.05, mood="worried")),
            ("táta", mug(tata, "tata", 1.0, mood="surprised")),
            ("máma", mug(mama, "mama", 1.1, outfit="home", mood="whisper")),
            ("Hanka", mug(hanka, "hanka", 1.5, mood="grin")),
            ("paní Věrka", mug(verka_old, "verka", 1.0, mood="grin")),
            ("Bětka", mug(betka, "betka", 1.5, hat=False, mood="worried")),
            ("Joey", lambda x, y: joey(x - 4, y + 2, 1.4, collar=False, mood="happy", shadow=False)),
        ]
        cw, ch = p.w*0.27, p.h*0.24
        for i, (lbl, fn) in enumerate(cards):
            cx = p.X(0.09) + (i % 3)*(cw + p.w*0.03); cy = p.Y(0.6) - (i//3)*(ch + 10)
            suspect_card(cx, cy, cw, ch, fn, lbl, rot=((i*7) % 9) - 4)
            hand_text(cx + cw - 30, cy + ch - 34, 30, "?", "SHB", 22, g=0.15)
        keep_clear(p, p.X(0.04), p.Y(0.04), p.X(0.96), p.Y(0.86), "board")
    with Pn(*R[1]) as p:
        bg_fill(p, P.BEDROOM_WALL)
        floor_y = p.y + 14
        shape([(p.x - 5, p.y - 5), (p.x + p.w + 5, p.y - 5), (p.x + p.w + 5, floor_y), (p.x - 5, floor_y)], P.FLOOR, BG)
        alica(p.X(0.14), floor_y, 1.2, mood="worried", right="chin", look=(1, 0))
        hanka(p.X(0.82), floor_y, 1.2, flip=True, mood="grin", look=(-1, 0))
        say(p, "Chtějí nás vykrást?", *ha(p.X(0.14), floor_y, 1.2), w=100, area=(0.0, 0.36))
        say(p, "Hihi! Ne!", *hh(p.X(0.82), floor_y, 1.2), w=80, area=(0.66, 1.0))
        say(p, "Nebo… má Klub Hvězdička novou tajnou misi? Beze mě?", *ha(p.X(0.14), floor_y, 1.2), w=150, area=(0.0, 0.5))
    page_end()


# =================================================================== 14 rain; new arrows; the map
def page_map():
    R = rows([(220, [0.5, 0.5]), (520, [1])])
    with Pn(*R[0]) as p:
        gy = domov(p, 0.45, 141, fence_=(0.0, 1.0), clouds=False, paving=0.25)
        sipka(p.X(0.5), p.Y(0.12), 1.6, 0, "tata")
        rain(p, 80)
        cap(p, "Ve středu prší. Šipky se smyjí.", w=170, where="tl")
    with Pn(*R[1]) as p:
        gy = domov(p, 0.45, 142, fence_=(0.0, 1.0), clouds=False, paving=0.25)
        sipka(p.X(0.3), p.Y(0.12), 1.4, 0, "tata"); sipka(p.X(0.72), p.Y(0.08), 1.4, 10, "mama")
        dr(p.X(0.92), p.Y(0.06), -20)
        cap(p, "Ve čtvrtek ráno jsou tu nové!", w=150, where="tl")
    with Pn(*R[2], bg=0.92) as p:
        shape(rrect(p.X(0.06), p.Y(0.05), p.w*0.88, p.h*0.82, 4), 1.0, LINE*1.2)
        for k in range(14): stroke([(p.X(0.08), p.Y(0.09 + k*0.055)), (p.X(0.92), p.Y(0.09 + k*0.055))], 0.4, g=0.75)
        hand_text(p.X(0.1), p.Y(0.8), p.w*0.8, "Mapa šipek – kreslí Alica", "SHB", 18, align="left")
        # the map: our house in the middle, the garden behind it, the garage, Tonda's house, the square
        def blk(x, y, w, h, lbl, g=0.95):
            shape([(x, y), (x + w, y), (x + w, y + h), (x, y + h)], g, LINE*0.9)
            hand_text(x, y + h/2 - 5, w, lbl, "SH", 11)
        blk(p.X(0.36), p.Y(0.36), 90, 60, "náš dům")
        blk(p.X(0.12), p.Y(0.52), 80, 50, "garáž")
        blk(p.X(0.72), p.Y(0.6), 80, 50, "Tonda")
        blk(p.X(0.14), p.Y(0.14), 100, 50, "náves")
        gx0, gy0 = p.X(0.58), p.Y(0.2)
        shape([(gx0, gy0), (gx0 + 130, gy0), (gx0 + 130, gy0 + 70), (gx0, gy0 + 70)], P.SPRING_GRASS, LINE*0.9)
        hand_text(gx0, gy0 + 28, 130, "ZAHRADA", "SHB", 13)
        hand_text(gx0 + 100, gy0 + 46, 30, "?", "SHB", 26, g=P.CRAYON_RED)
        arrows = [((0.3, 0.42), -30, "tata"), ((0.62, 0.55), -70, "mama"), ((0.3, 0.27), 10, "hanka"),
                  ((0.52, 0.3), -15, "tata"), ((0.83, 0.48), -100, "hanka"), ((0.5, 0.52), -60, "mama")]
        for (fx, fy_), rot, kind in arrows:
            ax_, ay_ = p.X(fx), p.Y(fy_)
            sipka(ax_, ay_, 1.1, math.degrees(math.atan2(gy0 + 35 - ay_, gx0 + 65 - ax_)), kind)
        keep_clear(p, p.X(0.06), p.Y(0.05), p.X(0.94), p.Y(0.87), "mapa")
        cap(p, "Alica kreslí všechny šipky do mapy. Kam vedou?", w=230, where="tr")
    page_end()


# =================================================================== 15 the locked garden; hurt
def page_hurt():
    R = rows([(300, [1]), (210, [0.5, 0.5]), (240, [1])])
    with Pn(*R[0]) as p:
        gy = domov(p, 0.5, 151, fence_=(0.0, 1.0), gate_x=0.45, trees=((0.18, 1.0), (0.8, 1.1)))
        sfx(p.X(0.62), p.Y(0.88), "ŠUŠKY ŠUŠKY", 13, 4)
        verka_old(p.X(0.7), gy - 6, 0.95, flip=True, mood="whisper", look=(-1, 0), shadow=False)
        fence(p.X(0.58), p.X(0.84), gy - 14, 34)
        alica(p.X(0.25), p.Y(0.03), 1.1, mood="surprised", look=(1, 0.3))
        J(p, p.X(0.85), p.Y(0.03), 1.0, flip=True, mood="happy")
        balonek(p.X(0.85) - 44, p.Y(0.03) + 46, P.BALLOON_BLUE, 1.0, 40, 5)
        say(p, "Branka na zahradu je zamčená. A za plotem někdo šeptá!", *ha(p.X(0.25), p.Y(0.03), 1.1), w=170, area=(0.0, 0.56))
    with Pn(*R[1]) as p:
        gy = domov(p, 0.5, 152, fence_=(0.0, 1.0), clouds=False)
        alica(p.X(0.3), p.Y(0.03), 1.2, mood="worried", look=(1, 0.3))
        say(p, "…Klub… v sobotu… ať nic nepozná…", tx=p.X(0.9), ty=p.Y(0.7), w=120, area=(0.45, 1.0), whisper=True)
    with Pn(*R[2]) as p:
        gy = domov(p, 0.5, 153, fence_=(0.0, 1.0), clouds=False)
        alica(p.X(0.3), p.Y(0.03), 1.2, mood="sad", look=(-1, -0.3))
        say(p, "Mají schůzku Klubu Hvězdička. Beze mě.", *ha(p.X(0.3), p.Y(0.03), 1.2), w=120, area=(0.45, 1.0))
    with Pn(*R[3]) as p:
        fy = bedroom_home(p, night=True)
        bed_side(p.X(0.2), p.X(0.2) + BED_LEN, fy + 40)
        alica(p.X(0.36), fy, 1.15, mood="sad", look=(1, 0))
        hanka(p.X(0.5), fy, 1.15, flip=True, mood="worried", right="hug", left="hug", look=(-1, 0))
        say(p, "Neplač. Já ti něco… ne. Nemůžu. Ale bude to dobrý!", *hh(p.X(0.5), fy, 1.15), w=170, area=(0.45, 1.0))
    page_end()


# =================================================================== 16 the arrow guide (full page)
def page_arrows():
    with Pn(M, 40, W-2*M, H-80, bg=0.97) as p:
        hand_text(p.X(0.04), p.Y(0.955), p.w*0.92, "Kdo kreslí šipky?", "SHB", 28)
        hand_text(p.X(0.04), p.Y(0.915), p.w*0.92, "Alica si všimla, že šipky nejsou stejné. Kreslí je tři různí lidé!", "SH", 13)
        rows_ = [
            ("tata", "1. Dlouhá a rovná. Velká hlava.",
             "Vždycky hodně vysoko na plotě. Vedle jsou černé otisky prstů.", 0.66),
            ("mama", "2. Čárkovaná. Úhledná hlava.",
             "Na konci má malé srdíčko. Kdo se tak podepisuje?", 0.43),
            ("hanka", "3. Z teček, malá, nakřivo.",
             "Vždycky těsně u země. Kreslí ji někdo hodně malý.", 0.2),
        ]
        for kind, t1, t2, fy_ in rows_:
            shape(rrect(p.X(0.04), p.Y(fy_), p.w*0.92, p.h*0.2, 10), 1.0, 1.2)
            fill(rrect(p.X(0.06), p.Y(fy_) + 10, p.w*0.36, p.h*0.2 - 20, 6), P.PAVING)
            sipka(p.X(0.24), p.Y(fy_) + p.h*0.1, 3.2, 0, kind)
            hand_text(p.X(0.46), p.Y(fy_) + p.h*0.13, p.w*0.48, t1, "SHB", 15, align="left")
            hand_text(p.X(0.46), p.Y(fy_) + p.h*0.13 - 24, p.w*0.48, t2, "SH", 13, align="left", lead=16)
        if True:
            oil_smudge(p.X(0.36), p.Y(0.66) + p.h*0.06, 1.6)
        hand_text(p.X(0.05), p.Y(0.1), p.w*0.9, "Ukaž prstem: kdo je velký a má ruce od oleje? Kdo píše srdíčka? A kdo je tak malý?", "SHB", 14, lead=18)
        hand_text(p.X(0.05), p.Y(0.03), p.w*0.9, "Alica: „Ta malá… Ne. Hanka by mi to přece řekla!“", "SH", 13)
    page_end()


# =================================================================== 17 the birthday morning
def page_morning():
    R = rows([(290, [1]), (220, [0.5, 0.5]), (240, [1])])
    with Pn(*R[0]) as p:
        fy = home(p, 0.08)
        tata(p.X(0.12), fy, 0.95, mood="happy", right="front", look=(1, 0))
        mama(p.X(0.3), fy, 0.98, outfit="home", mood="happy", look=(1, 0))
        hanka(p.X(0.47), fy, 1.1, mood="grin", right="hush", look=(1, 0))
        alica(p.X(0.82), fy, 1.05, flip=True, mood="sleepy", look=(-1, 0))
        home_table(p, 0.24, 0.04, 0.58)
        cap(p, "Sobota ráno.", w=100, where="tr")
        say(p, "Dobré ráno.", *ht(p.X(0.12), fy, 0.95), w=80, area=(0.0, 0.24))
        say(p, "Snídaně je na stole.", *hm(p.X(0.3), fy, 0.98), w=100, area=(0.18, 0.46))
        say(p, "Dobré ráno…", *ha(p.X(0.82), fy, 1.05), w=90, area=(0.62, 1.0))
    with Pn(*R[1]) as p:
        fy = home(p, 0.08)
        alica(p.X(0.3), fy, 1.2, mood="sad", look=(1, -0.3))
        say(p, "Nikdo si nevzpomněl…", *ha(p.X(0.3), fy, 1.2), w=110, area=(0.42, 1.0))
    with Pn(*R[2]) as p:
        fy = bedroom_home(p)
        with T(p.X(0.62), fy, 1.6):
            sh_([(-28, 0), (28, 0), (28, 110), (-28, 110)], P.DOOR)
            shape(ell(20, 50, 2.4, 2.4, 10), 0.85, LINE*0.6)
        sipka(p.X(0.62), fy + 60, 1.8, 180, "hanka")
        paper_star(p.X(0.62), fy + 120, 18, None)
        cap(p, "Na dveřích pokojíčku: malá šipka a hvězda!", w=150, where="tl")
    with Pn(*R[3]) as p:
        fy = bedroom_home(p)
        alica(p.X(0.14), fy, 1.1, mood="wow", right="point", look=(1, 0))
        J(p, p.X(0.6), fy, 1.0, mood="happy")
        dr(p.X(0.9), fy + 6, 12)
        say(p, "Šipka vede z mého pokoje! Kam?", *ha(p.X(0.14), fy, 1.1), w=130, area=(0.0, 0.5))
    page_end()


# =================================================================== 18 Hanka knows the way
def page_hanka_leads():
    R = rows([(360, [1]), (380, [0.5, 0.5])])
    with Pn(*R[0]) as p:
        fy = bedroom_home(p)
        hanka(p.X(0.36), fy, 1.35, mood="grin", right="up", look=(1, 0), item=lambda x, y: torch(x, y, 80))
        alica(p.X(0.78), fy, 1.25, flip=True, mood="surprised", look=(-1, 0))
        say(p, "Pojď! Já vím kudy!", *hh(p.X(0.36), fy, 1.35), w=100, area=(0.1, 0.55))
        say(p, "Ty o tom víš?!", *ha(p.X(0.78), fy, 1.25), w=90, area=(0.6, 1.0))
        say(p, "Já jsem taky detektivka! Pojď!", *hh(p.X(0.36), fy, 1.35), w=130, area=(0.0, 0.6))
    with Pn(*R[1]) as p:
        fy = bedroom_home(p)
        alica(p.X(0.4), fy, 1.3, mood="determined", right="lens", lens=True, look=(1, 0))
        say(p, "Dobře. Půjdu po šipkách.", *ha(p.X(0.4), fy, 1.3), w=110, area=(0.0, 1.0))
    with Pn(*R[2], bg=0.93) as p:
        hand_text(p.X(0.08), p.Y(0.7), p.w*0.84, "Ale nejdřív…", "SHB", 20)
        hand_text(p.X(0.08), p.Y(0.55), p.w*0.84, "otoč stránku!", "SHB", 20)
        sipka(p.X(0.5), p.Y(0.3), 3.0, 0, "tata")
    page_end()


# =================================================================== 19 STOP, DETEKTIVE!
def page_stop():
    with Pn(M, 40, W-2*M, H-80, bg=0.95) as p:
        title(p.X(0.5), p.Y(0.92), "STOP, DETEKTIVE!", 44)
        hand_text(p.X(0.05), p.Y(0.86), p.w*0.9, "Co se v sobotu chystá? A kdo kreslil které šipky?", "SHB", 17)
        cw, ch = p.w*0.3, p.h*0.19
        items = [
            ("v kůlně mňouká a u dveří je mléko (strana 4)", lambda x, y: (milk_saucer(x - 12, y + 10, 1.3), scratches(x + 14, y + 12, 1.4))),
            ("babička je od mouky (strana 5)", lambda x, y: flour_patch(x, y + 24, 46, 14)),
            ("zakroužkovaný den v kalendáři (strana 5)", lambda x, y: kalendar(x - 20, y + 4, 40, 48)),
            ("Tondova kartička (strana 8)", lambda x, y: pozvanka(x - 26, y + 14, 1.5, 6, word=False)),
            ("široká stopa se zoubky (strana 9)", lambda x, y: tyre_track([(x - 40, y + 26), (x + 40, y + 30)], True)),
            ("hobliny v Hančině kapse (strana 10)", lambda x, y: hobliny(x, y + 16, 1.6, 5, 4)),
            ("„V sobotu má Alica naroz…“ (strana 11)", lambda x, y: hanka(x, y - 8, 0.48, mood="whisper", shadow=False)),
            ("„balónky, limo, 8 sv…“ (strana 12)", lambda x, y: balonky(x, y, 0.7, 4)),
            ("tři různé šipky (strana 16)", lambda x, y: (sipka(x - 22, y + 30, 0.5, 0, "tata"), sipka(x, y + 17, 0.5, 0, "mama"),
                                                         sipka(x + 22, y + 4, 0.5, 0, "hanka"))),
        ]
        for i, (txt, pic) in enumerate(items):
            cx = p.X(0.04) + (i % 3)*(cw + p.w*0.02); cy = p.Y(0.82) - (i//3 + 1)*(ch + 10)
            shape(rrect(cx, cy, cw, ch, 8), 1.0, 1.2)
            hand_text(cx + 6, cy + ch - 20, 30, str(i + 1), "SHB", 16, align="left")
            with T(cx + cw/2, cy + 52, 1.8):
                pic(0, 0)
            hand_text(cx + 8, cy + 24, cw - 16, txt, "SH", 10.5, lead=12)
        by = p.Y(0.82) - 3*(ch + 10)
        hand_text(p.X(0.05), by - 26, p.w*0.9, "Ukaž prstem! Co je v kůlně? A co v garáži?", "SH", 14)
        with T(p.X(0.5), p.Y(0.03), 1.0, rot=180):
            hand_text(-p.w*0.45, 0, p.w*0.9, "Alica má narozeniny a všichni chystají oslavu!", "SH", 12)
            hand_text(-p.w*0.45, -15, p.w*0.9, "Dlouhé šipky kreslí táta, ty se srdíčkem máma a ty malé z teček Hanka.", "SH", 12)
            hand_text(-p.w*0.45, -30, p.w*0.9, "V kůlně jsou koťátka a v garáži je nové kolo.", "SH", 12)
    page_end()


# =================================================================== 20 station 1: under the stairs
def page_stairs():
    R = rows([(320, [1]), (200, [0.5, 0.5]), (230, [1])])
    with Pn(*R[0]) as p:
        fy, ux = chodba(p, 0.08)
        hanka(p.X(0.18), fy, 1.2, mood="grin", right="front", look=(1, -0.3), item=lambda x, y: torch(x, y, -10))
        torch_beam(p.X(0.18) + 26, fy + 64, ux - 30, fy + 2, ux + 40, fy + 40, 0.45)
        sipka(ux, fy + 14, 1.2, 180, "hanka")
        alica(p.X(0.36), fy, 1.1, mood="think", look=(1, -0.3))
        say(p, "Pod schody je tma.", *ha(p.X(0.36), fy, 1.1), w=100, area=(0.2, 0.6))
        say(p, "Já tam posvítím!", *hh(p.X(0.18), fy, 1.2), w=90, area=(0.0, 0.3))
    with Pn(*R[1]) as p:
        bg_fill(p, P.BARN_DARK)
        torch_beam(p.x, p.Y(0.85), p.X(0.2), p.Y(0.0), p.X(1.0), p.Y(0.7), 0.45)
        paper_star(p.X(0.58), p.Y(0.45), 46, "TAM", 10)
        keep_clear(p, p.X(0.3), p.Y(0.15), p.X(0.86), p.Y(0.78), "star")
    with Pn(*R[2]) as p:
        fy, ux = chodba(p, 0.08)
        alica(p.X(0.65), fy, 1.2, flip=True, mood="happy", right="up", look=(-1, 0.2),
              item=lambda x, y: paper_star(x, y + 4, 14, "TAM", 0))
        say(p, "T… A… M. TAM!", *ha(p.X(0.65), fy, 1.2), w=100, area=(0.0, 0.5))
    with Pn(*R[3]) as p:
        fy, ux = chodba(p, 0.08)
        sipka(p.X(0.22), fy + 6, 1.5, 180, "hanka")
        sipka(p.X(0.12), p.Y(0.5), 1.5, 180, "mama")
        hanka(p.X(0.45), fy, 1.15, flip=True, mood="grin", right="point", look=(-1, 0))
        alica(p.X(0.65), fy, 1.1, flip=True, mood="determined", look=(-1, 0), legs="walk")
        say(p, "Ven ze dveří!", *hh(p.X(0.45), fy, 1.15), w=90, area=(0.3, 0.6))
    page_end()


# =================================================================== 21 station 2: the hopscotch; station 3: Joey
def page_stations():
    R = rows([(300, [1]), (210, [0.5, 0.5]), (240, [1])])
    with Pn(*R[0]) as p:
        gy = domov(p, 0.48, 211, paving=0.36, trees=((0.08, 1.0), (0.92, 1.0)))
        nx, ny = panak(p.X(0.45), p.Y(0.03), 1.7, 0)
        paper_star(nx + 40, ny - 16, 22, "SKOČ", 6)
        alica(p.X(0.7), p.Y(0.03), 1.05, flip=True, mood="grin", look=(-1, -0.3))
        hanka(p.X(0.18), p.Y(0.03), 1.1, mood="grin", right="point", look=(1, 0))
        say(p, "Tondův panák! A na hvězdě je napsáno…", *hh(p.X(0.18), p.Y(0.03), 1.1), w=140, area=(0.0, 0.42))
        say(p, "SKOČ!", *ha(p.X(0.7), p.Y(0.03), 1.05), w=70, area=(0.6, 1.0))
    with Pn(*R[1]) as p:
        bg_fill(p, P.PAVING)
        panak(p.X(0.3), p.Y(0.04), 1.9, 0)
        alica(p.X(0.3), p.Y(0.42), 0.85, mood="grin", right="up", left="up", legs="walk", shadow=False)
        sfx(p.X(0.58), p.Y(0.3), "HOP HOP!", 15, 4)
        say(p, "…sedm, osm!", *ha(p.X(0.3), p.Y(0.42), 0.85), w=80, area=(0.55, 1.0))
    with Pn(*R[2]) as p:
        bg_fill(p, P.PAVING)
        sipka(p.X(0.6), p.Y(0.5), 3.2, 0, "tata")
        oil_smudge(p.X(0.85), p.Y(0.4), 1.8)
        cap(p, "Za osmičkou je dlouhá šipka.", w=150, where="tl")
    with Pn(*R[3]) as p:
        gy = domov(p, 0.48, 212, fence_=(0.0, 1.0), clouds=False, paving=0.3)
        J(p, p.X(0.55), p.Y(0.03), 1.3, mood="happy")
        sipka(p.X(0.55) + 50, p.Y(0.06), 1.0, 0, "mama")
        alica(p.X(0.14), p.Y(0.03), 1.1, mood="grin", right="point", look=(1, 0))
        hanka(p.X(0.85), p.Y(0.03), 1.1, flip=True, mood="grin", look=(-1, 0))
        dr(p.X(0.36), p.Y(0.06), 18)
        say(p, "Joey, ty sedíš na šipce! Hodný pejsek, uhni!", *ha(p.X(0.14), p.Y(0.03), 1.1), w=160, area=(0.0, 0.5))
        say(p, "Vede k zahradě!", *hh(p.X(0.85), p.Y(0.03), 1.1), w=90, area=(0.68, 1.0))
    page_end()


# =================================================================== 22 the garden gate
def page_gate():
    R = rows([(360, [1]), (380, [1])])
    with Pn(*R[0]) as p:
        gy = domov(p, 0.5, 221, fence_=(0.0, 1.0), gate_x=0.62, trees=((0.12, 1.1), (0.88, 1.2)))
        for k, (fx, kind) in enumerate(((0.3, "tata"), (0.44, "mama"), (0.56, "hanka"))):
            sipka(p.X(fx), p.Y(0.08) + k*6, 1.5, 15, kind)
        balonek(p.X(0.62), gy + 36, P.BALLOON_YELLOW, 1.0, 50, 4); balonek(p.X(0.71), gy + 36, P.BALLOON_RED, 1.0, 46, 4)
        alica(p.X(0.14), p.Y(0.03), 1.1, mood="wow", look=(1, 0.2))
        hanka(p.X(0.82), p.Y(0.03), 1.15, flip=True, mood="grin", right="hush", look=(-1, 0))
        cap(p, "Všechny šipky vedou sem. K brance na naši zahradu.", w=230, where="tl")
        say(p, "Branka je odemčená…", *ha(p.X(0.14), p.Y(0.03), 1.1), w=110, area=(0.0, 0.36))
        say(p, "Tři… dva… jedna…", *hh(p.X(0.82), p.Y(0.03), 1.15), w=100, area=(0.64, 1.0), whisper=True)
    with Pn(*R[1]) as p:
        gy = domov(p, 0.42, 222, fence_=(0.0, 1.0), gate_x=0.56, gate_open=True, clouds=False)
        girlanda(p.X(0.45), p.X(0.9), gy + 70, 12, 8)
        balonky(p.X(0.62), gy + 30, 1.1, 5, 3)
        alica(p.X(0.3), p.Y(0.03), 1.5, mood="surprised", right="front", look=(1, 0.3))
        sfx(p.X(0.64), p.Y(0.42), "VRZ…", 22, -6)
        cap(p, "Alica otvírá branku…", w=150, where="tr")
    page_end()


# =================================================================== 23 PŘEKVAPENÍ! (full page)
def page_surprise():
    with Pn(M, 40, W-2*M, H-80) as p:
        gy = domov(p, 0.5, 231, trees=((0.06, 1.6), (0.94, 1.5)), clouds=True)
        girlanda(p.X(0.0), p.X(1.0), p.Y(0.86), 30, 16)
        transparent(p.X(0.22), p.X(0.78), p.Y(0.78), "VŠECHNO NEJLEPŠÍ, ALICO!", 18)
        top = party_table(p.X(0.25), p.X(0.75), gy - 60)
        balonky(p.X(0.14), gy - 20, 1.4, 5, 2); balonky(p.X(0.86), gy - 20, 1.4, 5, 5)
        back = [(0.2, lambda x, y: verka_old(x, y, 0.8, mood="grin", right="wave")),
                (0.31, lambda x, y: rybar(x, y, 0.8, mood="grin", rod=False, right="wave")),
                (0.69, lambda x, y: hajny(x, y, 0.8, mood="grin", right="wave")),
                (0.8, lambda x, y: deda(x, y, 0.8, mood="grin", right="wave")),
                (0.9, lambda x, y: babicka(x, y, 0.8, flip=True, mood="grin", right="wave"))]
        for fx, fn in back: fn(p.X(fx), gy - 70)
        mid = [(0.1, lambda x, y: tata(x, y, 1.0, mood="grin", right="up")),
               (0.22, lambda x, y: mama(x, y, 1.0, outfit="home", mood="grin", right="up")),
               (0.36, lambda x, y: tonda(x, y, 1.1, mood="grin", right="up", left="up")),
               (0.5, lambda x, y: betka(x, y, 1.3, hat=False, mood="grin", right="up", left="up")),
               (0.62, lambda x, y: spoluzak(x, y, 1.15, who="julca", mood="grin", right="up")),
               (0.74, lambda x, y: spoluzak(x, y, 1.15, who="stella", flip=True, mood="grin", right="wave")),
               (0.87, lambda x, y: spoluzak(x, y, 1.15, who="karel", flip=True, mood="grin", right="up"))]
        for fx, fn in mid: fn(p.X(fx), p.Y(0.2))
        dort(p.X(0.5), top, 1.8)
        J(p, p.X(0.36), p.Y(0.03), 1.4, mood="happy", hat=True)
        hanka(p.X(0.6), p.Y(0.03), 1.5, mood="grin", right="up", look=(-1, 0))
        alica(p.X(0.18), p.Y(0.03), 1.6, mood="wow", left="up", right="up", look=(1, 0.3))
        sfx(p.X(0.08), p.Y(0.66), "PŘEKVAPENÍ!", 46, -3)
    page_end()


# =================================================================== 24 who did what
def page_reveal():
    R = rows([(260, [1]), (230, [0.5, 0.5]), (250, [1])])
    with Pn(*R[0]) as p:
        gy = domov(p, 0.48, 241, clouds=False, trees=((0.92, 1.0),))
        girlanda(p.x, p.x + p.w, p.Y(0.95), 20, 10)
        alica(p.X(0.12), p.Y(0.03), 1.05, mood="wow", look=(1, 0))
        babicka(p.X(0.4), p.Y(0.03), 1.0, mood="grin", right="front", look=(-1, 0),
                item=lambda x, y: dort(x + 4, y - 10, 0.55, lit=False))
        tonda(p.X(0.7), p.Y(0.03), 1.0, flip=True, mood="grin", right="up", look=(-1, 0),
              item=lambda x, y: pozvanka(x - 14, y, 1.0, 0, word=False))
        say(p, "Takže ta mouka…", *ha(p.X(0.12), p.Y(0.03), 1.05), w=90, area=(0.0, 0.28))
        say(p, "…to jsem pekla dort!", *hb(p.X(0.4), p.Y(0.03), 1.0), w=110, area=(0.24, 0.56))
        say(p, "A já roznášel pozvánky!", *htd(p.X(0.7), p.Y(0.03), 1.0), w=110, area=(0.56, 1.0))
    with Pn(*R[1]) as p:
        gy = domov(p, 0.48, 242, clouds=False)
        mama(p.X(0.25), p.Y(0.03), 1.0, outfit="home", mood="grin", right="front", look=(1, 0),
             item=lambda x, y: seznam(x - 10, y - 20, 34, 40, -4))
        say(p, "A já kupovala balónky. A osm svíček!", *hm(p.X(0.25), p.Y(0.03), 1.0), w=120, area=(0.4, 1.0))
    with Pn(*R[2]) as p:
        gy = domov(p, 0.48, 243, clouds=False)
        transparent(p.X(0.08), p.X(0.92), p.Y(0.92), "VŠECHNO NEJLEPŠÍ", 13)
        keep_clear(p, p.X(0.08), p.Y(0.92) - 26, p.X(0.92), p.Y(0.92), "banner")
        betka(p.X(0.25), p.Y(0.03), 1.3, hat=False, mood="grin", right="up", look=(1, 0))
        say(p, "Já jsem malovala nápis!", *hbe(p.X(0.25), p.Y(0.03), 1.3), w=100, area=(0.42, 1.0))
    with Pn(*R[3]) as p:
        gy = domov(p, 0.48, 244, clouds=False, paving=0.2)
        sipka(p.X(0.5), p.Y(0.08), 1.2, 0, "hanka")
        alica(p.X(0.14), p.Y(0.03), 1.1, mood="surprised", look=(1, -0.2))
        hanka(p.X(0.4), p.Y(0.03), 1.15, flip=True, mood="grin", right="up", look=(-1, 0),
              item=lambda x, y: chalk_stick(x, y + 2, 1.2, 60, "hanka"))
        tata(p.X(0.66), p.Y(0.03), 0.95, flip=True, mood="grin", look=(-1, 0))
        mama(p.X(0.86), p.Y(0.03), 0.95, flip=True, outfit="home", mood="grin", look=(-1, 0))
        say(p, "Ty jsi kreslila ty malinký šipky?", *ha(p.X(0.14), p.Y(0.03), 1.1), w=130, area=(0.0, 0.36))
        say(p, "Jo! A táta ty dlouhý…", *hh(p.X(0.4), p.Y(0.03), 1.15), w=110, area=(0.3, 0.62))
        say(p, "…a já ty se srdíčkem.", *hm(p.X(0.86), p.Y(0.03), 0.95), w=110, area=(0.62, 1.0))
    page_end()


# =================================================================== 25 presents: Hanka's, děda's kitten
def page_kitten():
    R = rows([(240, [1]), (210, [0.5, 0.5]), (300, [1])])
    with Pn(*R[0]) as p:
        gy = domov(p, 0.48, 251, clouds=False)
        hanka(p.X(0.55), p.Y(0.03), 1.2, flip=True, mood="grin", right="front", look=(-1, 0),
              item=lambda x, y: cat_drawing(x - 30, y - 14, 44, 34, 4))
        loupana_hul(p.X(0.68), p.Y(0.03), 1.3, 12, 70)
        alica(p.X(0.15), p.Y(0.03), 1.05, mood="wow", look=(1, 0))
        say(p, "To je kočička. A tu hůl jsem sama oloupala! Nožem! Ve školce!", *hh(p.X(0.55), p.Y(0.03), 1.2), w=180,
            area=(0.3, 1.0))
    with Pn(*R[1]) as p:
        gy = domov(p, 0.48, 252, clouds=False)
        deda(p.X(0.25), p.Y(0.03), 1.0, mood="grin", right="front", look=(1, -0.3),
             item=lambda x, y: cat_basket(x + 4, y - 30, 0.75, kitten_in=True))
        say(p, "A tohle je ode mě. Opatrně!", *hdd(p.X(0.25), p.Y(0.03), 1.0), w=110, area=(0.45, 1.0))
    with Pn(*R[2]) as p:
        bg_fill(p, P.SPRING_GRASS)
        cat_basket(p.X(0.5), p.Y(0.06), 2.6, kitten_in=True, lid=False, mood="meow")
        keep_clear(p, p.X(0.2), p.Y(0.05), p.X(0.8), p.Y(0.8), "basket")
        sfx(p.X(0.06), p.Y(0.84), "MŇAU!", 24, -6)
    with Pn(*R[3]) as p:
        gy = domov(p, 0.48, 253, clouds=False)
        alica(p.X(0.14), p.Y(0.03), 1.1, mood="grin", right="hug", look=(1, -0.2),
              item=lambda x, y: kitten(x + 2, y - 10, 1.0, mood="happy"))
        deda(p.X(0.66), p.Y(0.03), 0.95, flip=True, mood="grin", look=(-1, 0))
        cat(p.X(0.84), p.Y(0.04), 1.1, flip=True, mood="happy")
        keep_clear(p, p.X(0.84) - 14, p.Y(0.04), p.X(0.84) + 14, p.Y(0.04) + 52, "micka")
        dr(p.X(0.4), p.Y(0.05), 20)
        say(p, "Kotě! Takže ta straka v kůlně…", *ha(p.X(0.14), p.Y(0.03), 1.1), w=130, area=(0.0, 0.4))
        say(p, "…byla koťátka! Micka jich měla pět. Tahle je pro tebe.", *hdd(p.X(0.66), p.Y(0.03), 0.95), w=170, area=(0.42, 1.0))
        say(p, "Bude se jmenovat Micka. Jako maminka! Malá Micka!", *ha(p.X(0.14), p.Y(0.03), 1.1), w=130, area=(0.0, 0.42))
    page_end()


# =================================================================== 26 the bike; games; the end
def page_bike():
    R = rows([(290, [1]), (210, [0.5, 0.5]), (250, [1])])
    with Pn(*R[0]) as p:
        gy = domov(p, 0.48, 261, garage_x=0.86, garage_kw=dict(door="open"), clouds=False)
        kolo(p.X(0.5), p.Y(0.03), 1.4, bow=True)
        tata(p.X(0.72), p.Y(0.03), 0.95, flip=True, mood="grin", right="front", look=(-1, 0))
        alica(p.X(0.14), p.Y(0.03), 1.05, mood="wow", left="up", right="up", look=(1, 0))
        say(p, "Kolo! Růžové! Takže ty široké stopy…", *ha(p.X(0.14), p.Y(0.03), 1.05), w=130, area=(0.0, 0.42))
        say(p, "…byly od něj. Má vpředu odpruženou vidlici. Pojedeme spolu do lesa!", *ht(p.X(0.72), p.Y(0.03), 0.95),
            w=170, area=(0.42, 1.0))
    with Pn(*R[1]) as p:
        gy = domov(p, 0.48, 262, clouds=False)
        for k, (fx, fn) in enumerate(((0.25, lambda x, y: tonda(x, y, 0.95, mood="grin", right="up", left="up")),
                                      (0.7, lambda x, y: alica(x, y, 0.95, mood="grin", right="up", left="up")))):
            fn(p.X(fx), p.Y(0.05) + (8 if k else 0))
            sack(p.X(fx), p.Y(0.05) + (8 if k else 0) - 4, 0.95, 52)
        sfx(p.X(0.42), p.Y(0.55), "HOP!", 16, 4)
        cap(p, "Skákání v pytli.", w=110, where="tl")
    with Pn(*R[2]) as p:
        gy = domov(p, 0.48, 263, clouds=False)
        J(p, p.X(0.4), p.Y(0.03), 1.3, mood="happy")
        party_hat(p.X(0.75), p.Y(0.08), 1.5, 120)
        sfx(p.X(0.5), p.Y(0.6), "TŘEP TŘEP!", 14, 4)
        cap(p, "Joey klobouček nechce.", w=130, where="tl")
    with Pn(*R[3]) as p:
        gy = domov(p, 0.48, 264, clouds=False)
        girlanda(p.x, p.x + p.w, p.Y(0.95), 20, 10)
        KT(p, p.X(0.5), p.Y(0.04), 1.2, flip=True)
        alica(p.X(0.25), p.Y(0.03), 1.15, mood="happy", right="hug", look=(1, 0))
        hanka(p.X(0.66), p.Y(0.03), 1.15, flip=True, mood="grin", right="hug", look=(-1, 0))
        say(p, "Vždyť to celé bylo pro tebe.", *hh(p.X(0.66), p.Y(0.03), 1.15), w=110, area=(0.5, 0.9))
        say(p, "Tohle byl můj nejlepší případ!", *ha(p.X(0.25), p.Y(0.03), 1.15), w=120, area=(0.0, 0.42))
        cap(p, "Případ č. 12 vyřešen.", w=130, where="br")
    page_end()


# =================================================================== 27 activity (no pencil)
def maze(x, y, cols, rows_, cell, seed=4):
    """an arrow maze: from START follow the arrow in each square to the next one. Only one way leads to the garden.
    (x, y) = bottom left. Returns the page centres of the start and the garden cells"""
    rd = random.Random(seed)
    path = [(0, 0)]
    seen = {(0, 0)}
    goal = (cols - 1, rows_ - 1)
    # a fixed winding path to the garden
    route = [(1, 0), (1, 0), (0, 1), (0, 1), (-1, 0), (0, 1), (1, 0), (1, 0), (1, 0), (0, -1), (1, 0), (0, 1)]
    c = (0, 0)
    for d in route:
        c = (c[0] + d[0], c[1] + d[1]); path.append(c)
    goal = path[-1]
    nxt = {path[i]: (path[i + 1][0] - path[i][0], path[i + 1][1] - path[i][1]) for i in range(len(path) - 1)}
    rot = {(1, 0): 0, (-1, 0): 180, (0, 1): 90, (0, -1): -90}
    for cx in range(cols):
        for cy in range(rows_):
            px, py = x + cx*cell, y + cy*cell
            shape([(px, py), (px + cell, py), (px + cell, py + cell), (px, py + cell)], 0.97 if (cx + cy) % 2 else 0.9, 0.6)
            if (cx, cy) == goal:
                with T(px + cell/2, py + cell*0.2, 0.35): dort(0, 0, 1.0, 8, True)
                continue
            if (cx, cy) in nxt:
                d = nxt[(cx, cy)]
            else:
                opts = [d for d in rot if 0 <= cx + d[0] < cols and 0 <= cy + d[1] < rows_ and (cx + d[0], cy + d[1]) not in nxt
                        and (cx + d[0], cy + d[1]) != goal]
                d = rd.choice(opts) if opts else (1, 0)
            sipka(px + cell/2, py + cell/2, cell/60, rot[d], "tata")
    return (x + cell/2, y + cell/2), (x + goal[0]*cell + cell/2, y + goal[1]*cell + cell/2)


def party_mini(q, x, y, w, h, variant):
    """one of the two "spot the difference" party pictures; variant 1 has five things changed"""
    with Pn(x, y, w, h) as qq:
        gy = domov(qq, 0.45, 271, clouds=False, trees=((0.85, 0.7),))
        girlanda(qq.x, qq.x + qq.w, qq.Y(0.92), 10, 8)
        top = party_table(qq.X(0.25), qq.X(0.75), qq.Y(0.18))
        dort(qq.X(0.5), top, 0.9, candles=8 if variant == 0 else 7)
        balonky(qq.X(0.12), qq.Y(0.3), 0.9, 4 if variant == 0 else 3, 2)
        J(qq, qq.X(0.82), qq.Y(0.03), 0.7, flip=True, mood="happy", hat=variant == 0)
        kitten(qq.X(0.2), qq.Y(0.03), 0.8, bow=variant == 0)
        if variant == 0: darek(qq.X(0.62), top, 16, 12, P.PRESENT_BLUE)
        if variant == 0: cloud(qq.X(0.4), qq.Y(0.8), 0.5)
        else: cloud(qq.X(0.6), qq.Y(0.8), 0.5)


def page_quiz():
    with Pn(M, 40, W-2*M, H-80) as p:
        box = [(p.X(0.05), p.Y(0.905)), (p.X(0.95), p.Y(0.91)), (p.X(0.95), p.Y(0.905)+54), (p.X(0.05), p.Y(0.905)+52)]
        fill(box, 0.92)
        for a_, b_ in ((0, 1), (1, 2), (2, 3), (3, 0)): stroke([box[a_], box[b_]], 1.5)
        hand_text(p.X(0.05), p.Y(0.905)+18, p.w*0.9, "Detektivní zápisník", "SHB", 26)
        hand_text(p.X(0.05), p.Y(0.865), p.w*0.9, "Zase bez tužky. Stačí prst a dobré oči!", "SH", 13)
        hand_text(p.X(0.05), p.Y(0.82), p.w*0.9, "1. Šipkové bludiště: začni u Alice a jdi vždycky tam, kam ukazuje šipka.",
                  "SHB", 14, align="left")
        cell = 52
        mx = p.X(0.5) - 3*cell; my = p.Y(0.5)
        (sx, sy), (gx, gy) = maze(mx, my, 6, 4, cell)
        alica(mx - 34, sy - cell/2, 0.5, mood="happy", shadow=False)
        hand_text(mx - 62, sy + cell*0.5, 56, "START", "SHB", 11)
        y2 = my - 34
        hand_text(p.X(0.05), y2, p.w*0.9, "2. Najdi 5 rozdílů mezi obrázky.", "SHB", 14, align="left")
        pw, ph = p.w*0.44, 200
        party_mini(p, p.X(0.04), y2 - 20 - ph, pw, ph, 0)
        party_mini(p, p.X(0.52), y2 - 20 - ph, pw, ph, 1)
        y4 = y2 - 20 - ph - 28
        hidden_darek(p.X(0.09), y4 - 8, 12, -10, 1)          # the legend: not one of the hidden ten
        hand_text(p.X(0.15), y4 - 4, p.w*0.8,
                  f"V sešitě je schovaných {N_HIDDEN} dárečků, jako je tenhle (ten se nepočítá). Najdeš je všechny?",
                  "SHB", 14, align="left", lead=18)
        pages = ", ".join(map(str, HID[:-1])) + " a " + str(HID[-1]) if HID else ""
        with T(p.X(0.5), p.Y(0.015), 1.0, rot=180):
            hand_text(-p.w*0.45, 0, p.w*0.9, f"Dárečky jsou na stranách {pages}.", "SH", 10)
            hand_text(-p.w*0.45, -13, p.w*0.9, "Rozdíly: svíčky, balónky, Joeyho klobouček, mašle na kotěti, dárek na stole (a mráček).", "SH", 10)
    page_end()


# =================================================================== 28 back cover: next time
def back_cover():
    with Pn(M, 40, W-2*M, H-80, bg=0.95) as p:
        hand_text(p.X(0.1), p.Y(0.93), p.w*0.8, "Příště v sešitě č. 13:", "SHB", 20)
        title(p.X(0.5), p.Y(0.84), "STOPY U POTOKA", 36)
        with Pn(p.X(0.08), p.Y(0.3), p.w*0.84, p.h*0.48, bg=0.9) as q:
            sky(q, P.SPRING_SKY)
            hills(q, q.Y(0.55), 20, P.FAR_FIELD, 3)
            ground(q, q.Y(0.5), P.SPRING_GRASS)
            for k, fx in enumerate((0.1, 0.3, 0.88)): tree(q.X(fx), q.Y(0.48), 1.1, seed=k + 4)
            wpts = [(q.x - 5, q.Y(0.12))] + [(q.x + q.w*i/10, q.Y(0.2) + 4*math.sin(i)) for i in range(11)] + \
                   [(q.x + q.w + 5, q.Y(0.3)), (q.x + q.w + 5, q.Y(0.1))] + \
                   [(q.x + q.w*(10 - i)/10, q.Y(0.06) + 3*math.sin(i*1.3)) for i in range(11)]
            water(wpts, 4, 6)
            stump(q.X(0.72), q.Y(0.3), 0.9)
            with T(q.X(0.72), q.Y(0.3) + 23, 0.9):
                shape([(-20, 0), (20, 0), (2, 16)], P.LOG_END, LINE)
            for k in range(6): fill(ell(q.X(0.66) + k*9, q.Y(0.28) - (k % 2)*3, 3, 1.6, 10), P.LOG_END)
            kolo(q.X(0.3), q.Y(0.25), 1.1)
            alica(q.X(0.48), q.Y(0.25), 1.1, mood="think", right="point", look=(1, -0.3))
            hand_text(q.X(0.84), q.Y(0.75), q.w*0.12, "?", "SHB", 34)
        hand_text(p.X(0.1), p.Y(0.24), p.w*0.8, "Jedeme stanovat k potoku! Alica na novém kole. Ale kdo tu v noci okusuje stromy?", "SH", 16, lead=21)
        hand_text(p.X(0.1), p.Y(0.13), p.w*0.8, "Kdo to byl?", "SHB", 16)
        hand_text(p.X(0.1), p.Y(0.015), p.w*0.8, "Velká a malá detektivka – sešit č. 12", "SH", 13, g=0.35)
    PAGE[0] += 1; cv.showPage()


cover(); page_cast(); page_first(); page_shed(); page_flour(); page_village(); page_tonda(); page_panak()
page_garage(); page_hanka(); page_night(); page_phone(); page_board(); page_map(); page_hurt(); page_arrows()
page_morning(); page_hanka_leads(); page_stop(); page_stairs(); page_stations(); page_gate(); page_surprise()
page_reveal(); page_kitten(); page_bike(); page_quiz(); back_cover()
cv.save()
print("ok", PAGE[0] - 1, "pages")
import letter
if letter.MISSING: PROBLEMS.append("no glyph in the font for: " + " ".join(sorted(letter.MISSING)))
if len(HID) != N_HIDDEN: PROBLEMS.append(f"{len(HID)} hidden presents drawn, the notebook promises {N_HIDDEN}")
for pr in PROBLEMS: print("ORDER/LAYOUT:", pr)
if PROBLEMS: sys.exit(1)
