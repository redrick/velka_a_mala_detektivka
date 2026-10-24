"""Velká a malá detektivka, issue 13: Stopy u potoka (outline: vault topics/comic-series/issue13-outline)"""
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
from tracks import dog_print
from pond import verka_old, rybar, stump, reeds, willow, water, torch_beam, duck, badger, hole, treasure_tin, club_photo, badge
from winter import betka
from joeyday import hajny, sausage
from skola import mama, tata
from village import frog
from narozeniny import kolo, kitten, loupana_hul, suspect_card
from potok import *
from potok import _panel_fill
import chars3

W, H = A4
M = 28; GUT = 9; TOP = H - 30
OUT = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                   "comics", "velka_a_mala_detektivka", "13_stopy_u_potoka.pdf")
os.makedirs(os.path.dirname(OUT), exist_ok=True)
cv = canvas.Canvas(OUT, pagesize=A4); lib.set_canvas(cv)
cv.setTitle("Velká a malá detektivka – Případ č. 13: Stopy u potoka")
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



# =================================================================== issue 13 helpers
HEAD.update({"mama": (107.6, 10.2), "tata": (122.6, 10.8), "betka": (70.2, 9.6), "franta": (118, 11.2),
             "hajny": (116, 11)})
HID = []   # pages with a hidden frog, in order; the activity page's answer key is built from it
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


def hm(x, y, s): return hx("mama", x, y, s, 1.85, 2.0, 1.2)        # máma's bun
def hv(x, y, s): return hx("verka", x, y, s, 2.2, 2.4, 2.0)        # Věrka's straw hat
def hf(x, y, s): return hx("franta", x, y, s, 1.9, 2.1, 1.6)       # Franta's bucket hat
def hj(x, y, s): return hx("hajny", x, y, s, 1.9, 2.1, 1.5)        # the hajný's felt hat
def ht(x, y, s): return hd("tata", x, y, s)
def ha(x, y, s): return hd("alica", x, y, s)
def hh(x, y, s): return hd("hanka", x, y, s)
def hdd(x, y, s): return hd("deda", x, y, s)
def htd(x, y, s): return hd("tonda", x, y, s)
def hbe(x, y, s): return hd("betka", x, y, s)


def zb(x, y, rot=0):
    """one of the 10 hidden frogs"""
    hidden_zabka(x, y, 12.5, rot)
    HID.append(PAGE[0])


def J(p, x, y, s, flip=False, pose="stand", wet=False, **kw):
    """Joey, collar buried in his fur, head kept clear of balloons; wet: dripping after his swim"""
    joey(x, y, s, flip=flip, pose=pose, collar=False, **kw)
    if wet:
        rd = random.Random(int(x))
        for k in range(9):
            dx = rd.uniform(-22, 30)*s*(-1 if flip else 1); dy = rd.uniform(4, 30)*s
            fill(ell(x + dx, y + dy, 1.3*s, 2.0*s, 10), P.POND_WATER); stroke(ell(x + dx, y + dy, 1.3*s, 2.0*s, 10), 0.5, closed=True)
    l, r, b, t = (23, 46, 15, 40) if pose == "sniff" else (18, 41, 36, 61)
    if flip: l, r = -r, -l
    keep_clear(p, x + l*s, y + b*s, x + r*s, y + t*s, "joey")


def BB(p, x, y, s, **kw):
    """Hryzálek, kept clear of balloons"""
    bobr(x, y, s, **kw)
    flip = kw.get("flip", False)
    x0, x1 = (x - 30*s, x + 30*s)
    keep_clear(p, x0, y - 4*s, x1, y + 60*s, "bobr")


def inset(p, x, y, w, h, fn, label=None):
    """a round close-up inside a panel (seen through the lupa)"""
    shape(ell(x, y, w/2, h/2, 40), 1.0, LINE*1.2)
    C.saveState(); C.clipPath(poly(ell(x, y, w/2 - 1, h/2 - 1, 40)), stroke=0, fill=0)
    fn(x, y)
    C.restoreState()
    keep_clear(p, x - w/2, y - h/2, x + w/2, y + h/2, "inset")
    if label: hand_text(x - w/2, y - h/2 - 16, w, label, "SHB", 11)


def rider(fn, x, y, s, **kw):
    """somebody riding the pink bike, standing on the pedals; (x, y) = the ground under the bike"""
    kolo(x, y, s*1.15)
    fn(x - 5*s, y + 15*s, s, shadow=False, right="front", left="front", **kw)


def vozik(x, y, s=1.0):
    """děda's old handcart with the rolled-up canvas tent on it; (x, y) = the ground under its wheel, handle to the right"""
    with T(x, y, s):
        shape(rrect(-34, 14, 60, 18, 3), P.PLANKS, LINE)
        for k in (-20, -4, 12): stroke([(k, 15), (k, 31)], LINE*0.5, g=0.45)
        shape(rrect(-30, 32, 52, 16, 8), P.TENT_CANVAS, LINE)
        for k in (-18, 0, 14): stroke([(k, 32), (k + 2, 48)], LINE*1.2, g=P.GUY_ROPE)
        stroke([(26, 26), (58, 40)], LINE*2.6); stroke([(26, 26), (58, 40)], LINE*1.5, g=P.FIREWOOD)
        stroke(ell(-4, 12, 12, 12, 30), LINE*3.4, closed=True, g=0.25, taper=False)
        dot(-4, 12, 2.2, 0.5)
        star(-4, 40, 4, P.TAG_STAR)


def creek_bank(p, seed=1, level=0, creek_=(0.3, 0.44), gy_f=0.58, stones=None, rock_x=None, night=False, **kw):
    """the meadow with the creek running across behind the figures; returns the horizon y"""
    return louka(p, gy_f, seed, creek_=creek_, level=level, stones=stones, rock_x=rock_x, night=night, **kw)


def camp(p, gy_f=0.5, seed=1, tents=((0.12, "dome", 0.5), (0.48, "old", 0.42), (0.86, "small", 0.5)), fire=None,
         night=False, door="closed", **kw):
    """the camp on Hvězdná louka: the three tents on the meadow behind the figures; fire = (x, y, s, lit) fractions"""
    gy = louka(p, gy_f, seed, night=night, **kw)
    for fx, kind, s in tents:
        stan(p.X(fx), gy - 10, s, kind, door="glow" if night else door)
    if fire:
        fx, fy_, fs, lit = fire
        taborak(p.X(fx), p.Y(fy_), fs, lit)
    return gy


def tree_edge(p, x, y, s=1.0, seed=2):
    """a forest tree at the panel's edge"""
    tree(x, y, s, seed=seed, g=P.FOREST_DARK)


def wading(x, feet_y, wl, w=46, seed=6):
    """creek water over the legs of somebody standing in it up to wl"""
    r = random.Random(seed)
    top = [(x - w + i*(2*w)/16, wl + math.sin(i*1.3)*1.6) for i in range(17)]
    fill([(x - w, feet_y - 12)] + top + [(x + w, feet_y - 12)], P.CREEK)
    stroke(top[3:-3], LINE*0.9)
    for rx, ry in ((30, 5), (48, 8)):
        stroke(ell(x, wl, rx, ry, 30, 200, 340), BG*1.1, g=P.POND_RIPPLE)
    for k_ in range(7):
        a = math.radians(r.uniform(30, 150)); d = r.uniform(22, 44)
        dx, dy = x + math.cos(a)*d, wl + 3 + math.sin(a)*d*0.6
        rad = r.uniform(1.0, 1.9)
        fill(ell(dx, dy, rad, rad*1.3, 12), P.POND_WATER); stroke(ell(dx, dy, rad, rad*1.3, 12), 0.8, closed=True)


def pond_dam(p, dam_y=0.3, h=40, seed=1, stick=True, level_drop=False, night=False):
    """the little pond above Hryzálek's dam: water behind (upstream), the dam across, the creek below it in front.
    Returns (dam foot y, dam top y)"""
    gy = louka(p, 0.66, seed, forest=True, night=night)
    fill([(p.x - 5, p.Y(dam_y) + 8), (p.x + p.w + 5, p.Y(dam_y) + 8), (p.x + p.w + 5, p.Y(0.6)), (p.x - 5, p.Y(0.6))], P.CREEK)
    water([(p.x - 5, p.Y(dam_y) + 10), (p.x + p.w + 5, p.Y(dam_y) + 10), (p.x + p.w + 5, p.Y(0.58)), (p.x - 5, p.Y(0.58))], seed, 5)
    for fx in (0.05, 0.93): reeds(p.X(fx), p.Y(0.58) - 4, 0.8, seed + int(fx*10))
    top = hraz(p.X(0.06), p.X(0.94), p.Y(dam_y) - 6, h, seed, p.X(0.62) if stick else None)
    fill([(p.x - 5, p.y - 5), (p.x + p.w + 5, p.y - 5), (p.x + p.w + 5, p.Y(dam_y) - 6), (p.x - 5, p.Y(dam_y) - 6)],
         P.CREEK)
    for k in range(4):
        yy = p.Y(dam_y) - 14 - k*12
        stroke([(p.X(0.1 + k*0.05), yy), (p.X(0.3 + k*0.07), yy + 1)], BG, g=P.POND_RIPPLE)
        stroke([(p.X(0.6 - k*0.04), yy - 3), (p.X(0.85 - k*0.02), yy - 2)], BG, g=P.POND_RIPPLE)
    if night: night_tint(p, 0.4)
    return p.Y(dam_y) - 6, top


# =================================================================== 1 COVER
def cover():
    with Pn(M, 40, W-2*M, H-80) as p:
        gy = louka(p, 0.5, 11, creek_=(0.17, 0.36), level=1, stones=(0.3, 0.34, 0.38), night=True)
        shape(ell(p.X(0.86), p.Y(0.6), 22, 22, 30), P.KRASLICE_YELLOW, LINE*0.6)
        fill(ell(p.X(0.86) + 12, p.Y(0.6) + 4, 19, 19, 30), P.NIGHT_MEADOW)
        vrbka(p.X(0.5), p.Y(0.36), 1.4, seed=4)
        stan(p.X(0.86), p.Y(0.03), 1.5, "dome", door="glow")
        glow(p.X(0.86), p.Y(0.1), 120, 0.1)
        eyeshine(p.X(0.72), p.Y(0.28), 1.6)
        plesk(p.X(0.84), p.Y(0.24), 1.1)
        torch_beam(p.X(0.47), p.Y(0.15), p.X(0.62), p.Y(0.36), p.X(0.95), p.Y(0.2), 0.42)
        pahyl(p.X(0.2), p.Y(0.04), 2.6); tresky(p.X(0.2), p.Y(0.04), 90, 22, 4, 1.6)
        alica(p.X(0.08), p.Y(0.02), 2.0, mood="think", right="lens", lens=True, look=(1, -0.7))
        hanka(p.X(0.44), p.Y(0.02), 2.1, mood="wow", right="front", look=(1, 0.2), item=lambda x, y: torch(x, y, 15))
        joey(p.X(0.66), p.Y(0.03), 1.6, flip=True, mood="happy", collar=False)
    box = [(M+34, H-236), (W-M-30, H-232), (W-M-34, H-48), (M+30, H-52)]
    fill([(x+3, y-3) for x, y in box], 0.0, 0.25); fill(box, 1.0)
    for a_, b_ in ((0, 1), (1, 2), (2, 3), (3, 0)): stroke([box[a_], box[b_]], 1.8)
    series_title(W/2, H-98, H-160, 40, 66)
    hand_text(M+40, H-190, W-2*M-80, "Alica, Hanka a Joey", "SHB", 20)
    hand_text(M+40, H-217, W-2*M-80, "Případ č. 13: Stopy u potoka", "SH", 15)
    magnifier(M+82, H-120, ang=-30, r=17)
    bobr_print(W-M-92, H-140, 2.4, 20, ink=True)
    page_end()


# =================================================================== 2 WHO IS WHO
def page_cast():
    with Pn(M, 40, W-2*M, H-80) as p:
        hand_text(p.X(0.05), p.Y(0.95), p.w*0.9, "Kdo je kdo", "SHB", 28)
        cells = [
            ("Alica", "Lupa a nové kolo.", lambda x, y: alica(x, y, 0.9, mood="happy", right="lens", lens=True)),
            ("Hanka", "Opička a baterka.", lambda x, y: hanka(x, y, 1.1, mood="grin", item=lambda a, b: torch(a, b, 10), right="front")),
            ("Joey", "Do vody nechce.", lambda x, y: joey(x, y, 1.2, mood="happy", collar=False)),
            ("Máma a táta", "Stan, oheň a buřty.", lambda x, y: (mama(x - 22, y, 0.62, mood="happy"), tata(x + 22, y, 0.6, mood="grin"))),
            ("Děda", "Kdysi tu stanoval s Klubem.", lambda x, y: deda(x, y, 0.62, mood="happy")),
            ("Tonda", "Bojí se vlkodlaků.", lambda x, y: tonda(x, y, 0.8, mood="grin")),
            ("Bětka", "Ráda kreslí.", lambda x, y: betka(x, y, 1.0, hat=False, mood="grin")),
            ("Pan Franta", "Rybář. Bětčin děda.", lambda x, y: rybar(x, y, 0.55, mood="happy", rod=False)),
            ("Pan hajný", "Zná každé zvíře v lese.", lambda x, y: hajny(x, y, 0.56, mood="happy")),
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
                  "Šipky vedly Alicu na oslavu jejích narozenin. Dostala koťátko Micku a nové růžové kolo!",
                  "SH", 13, align="left", lead=17)
        kolo(p.X(0.78), by + bh*0.14, 0.95)
        kitten(p.X(0.93), by + bh*0.12, 1.1, flip=True)
    page_end()


# =================================================================== 3 setting off
def page_go():
    R = rows([(290, [1]), (220, [0.5, 0.5]), (240, [1])])
    with Pn(*R[0]) as p:
        gy = louka(p, 0.5, 31, clouds=True)
        tree_edge(p, p.X(0.95), gy - 6, 1.1, 3)
        vozik(p.X(0.3), p.Y(0.04), 1.1)
        deda(p.X(0.42), p.Y(0.03), 0.95, flip=True, mood="grin", right="front", look=(-1, 0))
        kolo(p.X(0.7), p.Y(0.03), 1.1)
        alica(p.X(0.88), p.Y(0.03), 1.05, flip=True, mood="happy", look=(-1, 0))
        cap(p, "Konec května. Klub Hvězdička jede stanovat!", w=220, where="tl")
        say(p, "Znám jedno místo u potoka. Hvězdná louka.", *hdd(p.X(0.42), p.Y(0.03), 0.95), w=150, area=(0.2, 0.7))
    with Pn(*R[1]) as p:
        gy = louka(p, 0.5, 32, clouds=False)
        tonda(p.X(0.28), p.Y(0.03), 1.0, mood="grin", right="up", look=(1, 0))
        betka(p.X(0.7), p.Y(0.03), 1.25, flip=True, hat=False, mood="happy", right="front", look=(-1, 0),
              item=lambda x, y: skicak(x - 16, y - 6, 30, 24, 0, -8, 0))
        say(p, "Já nesu stan!", *htd(p.X(0.28), p.Y(0.03), 1.0), w=80, area=(0.0, 0.5))
        say(p, "A já skicák.", *hbe(p.X(0.7), p.Y(0.03), 1.25), w=80, area=(0.5, 1.0))
    with Pn(*R[2]) as p:
        gy = louka(p, 0.5, 33, clouds=False)
        tata(p.X(0.3), p.Y(0.03), 0.9, mood="happy", look=(1, -0.3))
        J(p, p.X(0.66), p.Y(0.03), 1.0, flip=True, pose="sniff")
        sausage(p.X(0.88), p.Y(0.1), 1.3, 10)
        say(p, "Joey! Buřty jsou na večer!", *ht(p.X(0.3), p.Y(0.03), 0.9), w=110, area=(0.0, 0.62))
    with Pn(*R[3]) as p:
        gy = louka(p, 0.55, 34, clouds=False)
        for fx in (0.05, 0.9): tree_edge(p, p.X(fx), gy - 8, 1.0, int(fx*10))
        walkers = [(0.14, lambda x, y: deda(x, y, 0.9, mood="happy", look=(1, 0), legs="walk")),
                   (0.27, lambda x, y: hanka(x, y, 1.0, mood="grin", look=(1, 0), legs="walk")),
                   (0.4, lambda x, y: mama(x, y, 0.88, mood="happy", look=(1, 0), legs="walk")),
                   (0.53, lambda x, y: tonda(x, y, 0.9, mood="grin", look=(1, 0), legs="walk")),
                   (0.65, lambda x, y: betka(x, y, 1.1, hat=False, mood="happy", look=(1, 0), legs="walk"))]
        for fx, fn in walkers: fn(p.X(fx), p.Y(0.04))
        zb(p.X(0.88), p.Y(0.42), 8)
        say(p, "Tady jsme kdysi stanovali s Klubem. Před padesáti lety!", *hdd(p.X(0.14), p.Y(0.04), 0.9), w=170,
            area=(0.0, 0.55))
        say(p, "Dědo, ty jsi tu byl jako kluk?", *hh(p.X(0.27), p.Y(0.04), 1.0), w=120, area=(0.3, 0.8))
    page_end()


# =================================================================== 4 Hvězdná louka: pitching the tents, the stones
def page_tents():
    R = rows([(300, [1]), (210, [0.5, 0.5]), (240, [1])])
    with Pn(*R[0]) as p:
        gy = louka(p, 0.55, 41, clouds=True)
        stan(p.X(0.72), p.Y(0.06), 0.95, "old", door="open")
        with T(p.X(0.36), p.Y(0.06), 1.0):
            shape(bez((-50, 0), (-40, 26), (30, 18), (52, 0)), P.TENT_GREEN, LINE)
            for k, (a, b, c_) in enumerate((((-30, 10), (-10, 110), (40, 90)), ((-60, 30), (0, 120), (60, 60)))):
                stroke(bez(a, b, (b[0] + 20, b[1]), c_), LINE*1.6, g=0.25)
        tata(p.X(0.36), p.Y(0.03), 0.95, mood="worried", right="up", left="up", look=(1, 0.4))
        deda(p.X(0.92), p.Y(0.03), 0.9, flip=True, mood="grin", right="hip", look=(-1, 0))
        cap(p, "Hvězdná louka. Stavíme stany.", w=170, where="tl")
        say(p, "Kde má ta tyčka začátek?!", *ht(p.X(0.36), p.Y(0.03), 0.95), w=110, area=(0.08, 0.56))
        say(p, "Můj stan stojí. Za minutu!", *hdd(p.X(0.92), p.Y(0.03), 0.9), w=110, area=(0.6, 1.0))
    with Pn(*R[1]) as p:
        gy = creek_bank(p, 42, 0, creek_=(0.1, 0.62), gy_f=0.78, stones=(0.28, 0.4, 0.52, 0.64), rock_x=0.84)
        cap(p, "Přes potok vedou kameny. Za ním je studánka.", w=180, where="tl")
    with Pn(*R[2]) as p:
        gy = creek_bank(p, 43, 0, creek_=(0.26, 0.5), gy_f=0.68, stones=(0.56, 0.62, 0.68))
        hanka(p.X(0.62), p.Y(0.28), 0.95, flip=True, mood="grin", right="wave", look=(-1, 0), shadow=False)
        J(p, p.X(0.3), p.Y(0.03), 1.05, mood="sad")
        say(p, "Pojď, Joey! Je to jen voda!", *hh(p.X(0.62), p.Y(0.28), 0.95), w=110, area=(0.4, 1.0))
    with Pn(*R[3]) as p:
        gy = creek_bank(p, 44, 0, creek_=(0.3, 0.46), gy_f=0.6, rock_x=0.84)
        betka(p.X(0.42), p.Y(0.03), 1.3, hat=False, mood="happy", right="front", look=(1, -0.2),
              item=lambda x, y: skicak(x - 20, y - 12, 40, 32, 0, -6, 1))
        alica(p.X(0.14), p.Y(0.03), 1.05, mood="think", look=(1, -0.2))
        zb(p.X(0.72), p.Y(0.4), -10)
        say(p, "Co kreslíš?", *ha(p.X(0.14), p.Y(0.03), 1.05), w=80, area=(0.0, 0.3))
        say(p, "Ten velký kámen v potoce. Každý den jeden obrázek!", *hbe(p.X(0.42), p.Y(0.03), 1.3), w=160, area=(0.2, 0.75))
    page_end()


# =================================================================== 5 evening: the saw, the knife, the fire
def page_evening():
    R = rows([(360, [1]), (390, [1])])
    with Pn(*R[0]) as p:
        gy = camp(p, 0.55, 51, tents=((0.86, "old", 0.45),), sky_g=P.SPRING_SKY)
        polena(p.X(0.4), p.Y(0.05), 1.3)
        tata(p.X(0.18), p.Y(0.03), 1.0, mood="happy", right="front", look=(1, -0.4),
             item=lambda x, y: pila(x, y, 1.0, -20))
        hanka(p.X(0.66), p.Y(0.03), 1.15, flip=True, mood="determined", right="front", left="front", look=(-1, -0.5),
              item=lambda x, y: loupana_hul(x - 4, y - 6, 0.7, 50, 46))
        kudrlinky(p.X(0.66), p.Y(0.04), 1.3)
        mama(p.X(0.88), p.Y(0.03), 0.95, flip=True, mood="worried", look=(-1, 0))
        zb(p.X(0.52), p.Y(0.42), 0)
        cap(p, "Večer. Táta řeže dřevo na oheň novou pilkou.", w=210, where="tl")
        say(p, "Jen suché spadlé větve!", *ht(p.X(0.18), p.Y(0.03), 1.0), w=110, area=(0.0, 0.42))
        say(p, "A já loupu klacík. Nožem!", *hh(p.X(0.66), p.Y(0.03), 1.15), w=110, area=(0.4, 0.78))
        say(p, "Opatrně, Hani.", *hm(p.X(0.88), p.Y(0.03), 0.95), w=90, area=(0.74, 1.0))
    with Pn(*R[1]) as p:
        gy = louka(p, 0.55, 52, sky_g=P.WINTER_NIGHT, clouds=False)
        night_stars(p, 0.62, 30, 5)
        night_tint(p, 0.3)
        taborak(p.X(0.5), p.Y(0.1), 1.6, burty=True)
        tonda(p.X(0.24), p.Y(0.03), 1.05, mood="wow", right="up", left="up", look=(1, 0))
        betka(p.X(0.76), p.Y(0.03), 1.3, flip=True, hat=False, mood="happy", look=(-1, 0))
        deda(p.X(0.92), p.Y(0.03), 0.9, flip=True, mood="happy", look=(-1, 0))
        alica(p.X(0.08), p.Y(0.03), 1.0, mood="worried", look=(1, 0))
        say(p, "…a v lese žije VLKODLAK!", *htd(p.X(0.24), p.Y(0.03), 1.05), w=120, area=(0.0, 0.5))
        say(p, "Vlkodlaci nejsou.", *hbe(p.X(0.76), p.Y(0.03), 1.3), w=90, area=(0.55, 0.85))
        say(p, "Dost strašení. Buřty jsou hotové!", *hdd(p.X(0.92), p.Y(0.03), 0.9), w=120, area=(0.6, 1.0))
    page_end()


# =================================================================== 6 night: PLESK!
def page_night():
    R = rows([(330, [1]), (190, [0.5, 0.5]), (230, [1])])
    with Pn(*R[0]) as p:
        gy = creek_bank(p, 61, 0, creek_=(0.22, 0.42), gy_f=0.6, stones=(0.66, 0.72, 0.78), night=True)
        stan(p.X(0.12), p.Y(0.04), 0.9, "dome", door="glow")
        torch_beam(p.X(0.4) + 24, p.Y(0.03) + 70, p.X(0.6), p.Y(0.45), p.X(0.95), p.Y(0.25), 0.4)
        hanka(p.X(0.4), p.Y(0.03), 1.15, mood="surprised", right="front", look=(1, 0.2), item=lambda x, y: torch(x, y, 10))
        plesk(p.X(0.78), p.Y(0.33), 1.2)
        sfx(p.X(0.7), p.Y(0.66), "PLESK!", 30, -6)
        cap(p, "V noci musí Hanka čůrat.", w=150, where="tl")
        say(p, "Kdo je tam?", *hh(p.X(0.4), p.Y(0.03), 1.15), w=80, area=(0.24, 0.6))
    with Pn(*R[1]) as p:
        _panel_fill(p, P.NIGHT_MEADOW)
        fill([(p.x, p.y), (p.x + p.w, p.y), (p.x + p.w, p.Y(0.7)), (p.x, p.Y(0.7))], P.CREEK_DEEP)
        night_tint(p, 0.4)
        torch_beam(p.x, p.Y(0.95), p.X(0.2), p.Y(0.0), p.X(1.0), p.Y(0.5), 0.35)
        eyeshine(p.X(0.55), p.Y(0.35), 2.0)
        keep_clear(p, p.X(0.3), p.Y(0.15), p.X(0.8), p.Y(0.55), "eyes")
        cap(p, "Dvě očička…", w=100, where="tl")
    with Pn(*R[2]) as p:
        gy = louka(p, 0.6, 62, night=True)
        stan(p.X(0.8), p.Y(0.06), 0.9, "dome", door="glow")
        hanka(p.X(0.35), p.Y(0.03), 1.15, mood="wow", look=(1, 0), legs="walk", item=lambda x, y: torch(x, y, -20),
              right="front")
        say(p, "Tati! V potoce je drak!", *hh(p.X(0.35), p.Y(0.03), 1.15), w=100, area=(0.0, 0.6))
    with Pn(*R[3]) as p:
        gy = louka(p, 0.62, 63, night=True)
        stan(p.X(0.2), p.Y(0.06), 1.1, "dome", door="glow")
        tata(p.X(0.46), p.Y(0.03), 0.95, mood="sleepy", look=(1, 0))
        hanka(p.X(0.8), p.Y(0.03), 1.15, flip=True, mood="worried", look=(-1, 0), item=lambda x, y: torch(x, y, 190),
              right="front")
        say(p, "To byla ryba. Spinkej.", *ht(p.X(0.46), p.Y(0.03), 0.95), w=100, area=(0.1, 0.6))
        say(p, "Ryba se svítícíma očima?", *hh(p.X(0.8), p.Y(0.03), 1.15), w=110, area=(0.55, 1.0))
    page_end()


# =================================================================== 7 morning: the felled willow
def page_morning():
    R = rows([(300, [1]), (210, [0.5, 0.5]), (240, [1])])
    with Pn(*R[0]) as p:
        gy = creek_bank(p, 71, 0, creek_=(0.36, 0.5), gy_f=0.62, stones=(0.8, 0.85, 0.9))
        vrbka(p.X(0.12), p.Y(0.42), 0.9, 5)
        pahyl(p.X(0.42), p.Y(0.28), 1.3); tresky(p.X(0.42), p.Y(0.28), 60, 16, 7)
        padla_vrbka(p.X(0.46), p.Y(0.3), 1.1, seed=3)
        alica(p.X(0.16), p.Y(0.03), 1.05, mood="wow", look=(1, 0.2))
        tonda(p.X(0.82), p.Y(0.03), 1.0, flip=True, mood="surprised", right="point", look=(-1, 0.2))
        cap(p, "Ráno.", w=70, where="tl")
        say(p, "Vrba spadla!", *ha(p.X(0.16), p.Y(0.03), 1.05), w=80, area=(0.0, 0.36))
        say(p, "Někdo ji v noci pokácel!", *htd(p.X(0.82), p.Y(0.03), 1.0), w=110, area=(0.6, 1.0))
    with Pn(*R[1]) as p:
        bg_fill(p, P.EARLY_SUMMER_GRASS)
        pahyl(p.X(0.5), p.Y(0.1), 3.6); tresky(p.X(0.5), p.Y(0.1), p.w*0.7, 26, 8, 2.2)
        keep_clear(p, p.X(0.3), p.Y(0.05), p.X(0.7), p.Y(0.72), "pahyl")
        cap(p, "Pahýl jako ořezaná tužka. A kolem třísky.", w=170, where="tl")
    with Pn(*R[2]) as p:
        gy = camp(p, 0.5, 72, tents=((0.7, "old", 0.6),))
        deda(p.X(0.22), p.Y(0.03), 0.9, mood="worried", right="up", left="up", look=(1, 0))
        say(p, "Kde je moje hůl? Večer stála u stanu!", *hdd(p.X(0.22), p.Y(0.03), 0.9), w=130, area=(0.38, 1.0))
    with Pn(*R[3]) as p:
        gy = camp(p, 0.5, 73)
        alica(p.X(0.18), p.Y(0.03), 1.15, mood="determined", right="lens", lens=True, look=(1, 0))
        hanka(p.X(0.46), p.Y(0.03), 1.15, mood="grin", right="up", look=(-1, 0))
        J(p, p.X(0.74), p.Y(0.03), 1.0, flip=True, mood="happy")
        zb(p.X(0.62), p.Y(0.06), 12)
        say(p, "Zakládám případ číslo třináct: Stopy u potoka!", *ha(p.X(0.18), p.Y(0.03), 1.15), w=160, area=(0.0, 0.45))
        say(p, "A já svítím baterkou!", *hh(p.X(0.46), p.Y(0.03), 1.15), w=110, area=(0.35, 0.75))
    page_end()


# =================================================================== 8 the suspect board (Bětka draws it)
def page_board():
    R = rows([(470, [1]), (270, [1])])
    with Pn(*R[0], bg=0.92) as p:
        shape(rrect(p.X(0.04), p.Y(0.04), p.w*0.92, p.h*0.82, 6), 1.0, LINE*1.4)
        for k in range(16): stroke([(p.X(0.06), p.Y(0.07 + k*0.05)), (p.X(0.94), p.Y(0.07 + k*0.05))], 0.4, g=0.8)
        hand_text(p.X(0.04), p.Y(0.9), p.w*0.92, "Kdo kácí stromy? (kreslí Bětka)", "SHB", 22)

        def monster(x, y):
            with T(x, y + 6, 1.5):
                shape(bez((-20, 0), (-26, 40), (26, 40), (20, 0)), 0.45, LINE)
                for sx in (-1, 1):
                    shape([(sx*8, 36), (sx*16, 52), (sx*18, 34)], 0.45, LINE)
                    dot(sx*7, 24, 3, 1.0); dot(sx*7, 24, 1.4, 0.0)
                stroke([(-8, 12), (-4, 9), (0, 12), (4, 9), (8, 12)], LINE)

        def dragon(x, y):
            with T(x, y + 10, 1.4):
                shape(bez((-26, 0), (-24, 20), (10, 26), (20, 14)) + [(30, 22), (26, 6), (20, 0)], P.WILLOW_DARK, LINE)
                for k in range(4): shape([(-16 + k*9, 17 + k), (-12 + k*9, 26 + k), (-8 + k*9, 18 + k)], P.FIRE_RED, LINE*0.6)
                dot(24, 16, 1.6, 0.0)
                shape([(30, 18), (42, 22), (36, 14), (44, 10), (30, 12)], P.FLAME, LINE*0.6)
        cards = [
            ("táta a pilka", lambda x, y: (tata(x - 10, y + 78 - (122.6 + 10.8)*0.9, 0.9, shadow=False, mood="surprised"),
                                          pila(x + 20, y + 30, 0.6, 30))),
            ("Hanka a nožík", lambda x, y: (hanka(x, y + 78 - (70.2 + 9.6)*1.5, 1.5, shadow=False, mood="grin"),
                                            kudrlinky(x + 22, y + 12, 0.8))),
            ("Joey", lambda x, y: joey(x - 4, y + 2, 1.4, collar=False, mood="happy", shadow=False)),
            ("vlkodlak? (Tonda)", monster),
            ("drak? (Hanka)", dragon),
            ("kdo ještě?", lambda x, y: hand_text(x - 30, y + 30, 60, "?", "SHB", 50, g=0.3)),
        ]
        cw, ch = p.w*0.27, p.h*0.3
        for i, (lbl, fn) in enumerate(cards):
            cx = p.X(0.09) + (i % 3)*(cw + p.w*0.03); cy = p.Y(0.5) - (i//3)*(ch + 12)
            suspect_card(cx, cy, cw, ch, fn, lbl, rot=((i*7) % 9) - 4)
        keep_clear(p, p.X(0.04), p.Y(0.04), p.X(0.96), p.Y(0.86), "board")
    with Pn(*R[1]) as p:
        gy = camp(p, 0.55, 81)
        tonda(p.X(0.14), p.Y(0.03), 1.05, mood="determined", right="point", look=(1, 0))
        betka(p.X(0.46), p.Y(0.03), 1.3, hat=False, mood="worried", look=(-1, 0))
        alica(p.X(0.8), p.Y(0.03), 1.1, flip=True, mood="determined", right="lens", lens=True, look=(-1, 0))
        say(p, "Byl to vlkodlak! Určitě!", *htd(p.X(0.14), p.Y(0.03), 1.05), w=110, area=(0.0, 0.36))
        say(p, "Vlkodlaci nejsou.", *hbe(p.X(0.46), p.Y(0.03), 1.3), w=90, area=(0.32, 0.6))
        say(p, "Nejdřív stopy. Kdo to byl, zjistí lupa!", *ha(p.X(0.8), p.Y(0.03), 1.1), w=140, area=(0.55, 1.0))
    page_end()


# =================================================================== 9 saw, knife, dog: the comparing
def page_compare():
    R = rows([(260, [1]), (230, [0.5, 0.5]), (250, [1])])
    with Pn(*R[0]) as p:
        gy = camp(p, 0.55, 91, tents=((0.86, "dome", 0.5),))
        polena(p.X(0.42), p.Y(0.05), 1.3)
        alica(p.X(0.18), p.Y(0.03), 1.05, mood="think", right="lens", lens=True, look=(1, -0.5))
        tata(p.X(0.68), p.Y(0.03), 0.95, flip=True, mood="happy", look=(-1, 0), item=lambda x, y: pila(x, y, 0.9, 200))
        inset(p, p.X(0.5), p.Y(0.66), 90, 76, lambda x, y: saw_closeup(x, y, 1.2))
        say(p, "Pilka řeže rovně. Ale pahýl je špičatý jako tužka!", *ha(p.X(0.18), p.Y(0.03), 1.05), w=140, area=(0.0, 0.44))
        say(p, "Vidíš? Já to nebyl.", *ht(p.X(0.68), p.Y(0.03), 0.95), w=90, area=(0.62, 1.0))
    with Pn(*R[1]) as p:
        bg_fill(p, P.EARLY_SUMMER_GRASS)
        kudrlinky(p.X(0.27), p.Y(0.42), 3.6, 4, 2)
        tresky(p.X(0.73), p.Y(0.42), 80, 9, 3, 3.6)
        hand_text(p.X(0.08), p.Y(0.25), p.w*0.4, "nožík", "SHB", 13)
        hand_text(p.X(0.52), p.Y(0.25), p.w*0.4, "u pahýlu", "SHB", 13)
        keep_clear(p, p.X(0.05), p.Y(0.2), p.X(0.95), p.Y(0.65), "pics")
        cap(p, "Hanka dělá dlouhé tenké kudrlinky. U pahýlu jsou krátké tlusté třísky.", w=210, where="tl")
    with Pn(*R[2]) as p:
        gy = camp(p, 0.55, 92, tents=())
        hanka(p.X(0.3), p.Y(0.03), 1.2, mood="sad", right="hug", look=(1, 0))
        alica(p.X(0.7), p.Y(0.03), 1.1, flip=True, mood="happy", right="hug", look=(-1, 0))
        say(p, "Já bych strom neuměla pokácet!", *hh(p.X(0.3), p.Y(0.03), 1.2), w=110, area=(0.0, 0.5))
        say(p, "Já vím, Hani. Promiň.", *ha(p.X(0.7), p.Y(0.03), 1.1), w=90, area=(0.5, 1.0))
    with Pn(*R[3]) as p:
        gy = camp(p, 0.55, 93)
        J(p, p.X(0.42), p.Y(0.03), 1.2, mood="happy")
        dog_bite(p.X(0.42) + 56, p.Y(0.03) + 48, 0.9, -10)
        alica(p.X(0.12), p.Y(0.03), 1.1, mood="think", right="point", look=(1, 0))
        inset(p, p.X(0.82), p.Y(0.42), 96, 80, lambda x, y: dog_bite(x, y, 1.6, 0))
        zb(p.X(0.62), p.Y(0.05), -8)
        say(p, "Joey, to jsi byl ty?", *ha(p.X(0.12), p.Y(0.03), 1.1), w=100, area=(0.0, 0.36))
        cap(p, "Joeyho zuby dělají jen malé dírky.", w=170, where="br")
    page_end()


# =================================================================== 10 bike ride; Franta: "to bude vydra"
def page_franta():
    R = rows([(290, [1]), (230, [1]), (230, [0.5, 0.5])])
    with Pn(*R[0]) as p:
        gy = creek_bank(p, 101, 0, creek_=(0.32, 0.46), gy_f=0.58)
        for fx in (0.04, 0.95): tree_edge(p, p.X(fx), gy - 8, 1.0, int(fx*10) + 2)
        rider(alica, p.X(0.42), p.Y(0.04), 1.0, mood="grin", look=(1, 0))
        tata(p.X(0.14), p.Y(0.03), 0.95, mood="happy", look=(1, 0), legs="walk")
        J(p, p.X(0.74), p.Y(0.03), 1.0, mood="happy")
        sfx(p.X(0.55), p.Y(0.82), "HOP!", 20, 6)
        cap(p, "Odpoledne jede Alica podél potoka na novém kole.", w=220, where="tl")
        say(p, "Vidlice pruží! Hop!", *ha(p.X(0.42) - 5, p.Y(0.04) + 15, 1.0), w=100, area=(0.3, 0.7))
    with Pn(*R[1]) as p:
        gy = creek_bank(p, 102, 0, creek_=(0.12, 0.44), gy_f=0.6)
        rybar(p.X(0.7), p.Y(0.2), 0.95, flip=True, mood="worried", look=(-1, 0), shadow=False)
        wading(p.X(0.7), p.Y(0.2), p.Y(0.2) + 24, 40)
        kolo(p.X(0.3), p.Y(0.03), 1.0)
        alica(p.X(0.14), p.Y(0.03), 1.05, mood="happy", look=(1, 0))
        say(p, "Dobrý den, pane Franto! Chytá to?", *ha(p.X(0.14), p.Y(0.03), 1.05), w=120, area=(0.0, 0.42))
        say(p, "Nic. Ryby mi asi žere vydra.", *hf(p.X(0.7), p.Y(0.2), 0.95), w=110, area=(0.44, 1.0))
    with Pn(*R[2]) as p:
        bg_fill(p, P.MUD)
        vydra_print(p.X(0.5), p.Y(0.45), 4.2, 0)
        keep_clear(p, p.X(0.3), p.Y(0.22), p.X(0.7), p.Y(0.7), "otisk")
        cap(p, "Pan Franta kreslí klackem do bláta.", w=170, where="tl")
        hand_text(p.X(0.1), p.Y(0.06), p.w*0.8, "vydra", "SHB", 14)
    with Pn(*R[3]) as p:
        gy = creek_bank(p, 103, 0, creek_=(0.3, 0.46), gy_f=0.62)
        rybar(p.X(0.72), p.Y(0.03), 0.95, flip=True, mood="happy", right="point", look=(-1, -0.3), rod=False)
        say(p, "Vydra má malou kulatou stopu. Pět prstů.", *hf(p.X(0.72), p.Y(0.03), 0.95), w=130, area=(0.0, 1.0))
    page_end()


# =================================================================== 11 the water rises
def page_rising():
    R = rows([(280, [1]), (220, [0.5, 0.5]), (250, [1])])
    with Pn(*R[0]) as p:
        gy = creek_bank(p, 111, 1, creek_=(0.36, 0.52), gy_f=0.66, rock_x=0.86)
        betka(p.X(0.5), p.Y(0.03), 1.25, hat=False, mood="surprised", right="front", left="front", look=(-1, 0))
        skicak(p.X(0.08), p.Y(0.12), 62, 50, 0, -4, 1)
        skicak(p.X(0.22), p.Y(0.12), 62, 50, 1, 3, 2)
        keep_clear(p, p.X(0.06), p.Y(0.1), p.X(0.38), p.Y(0.36), "kresby")
        alica(p.X(0.7), p.Y(0.03), 1.05, flip=True, mood="think", look=(-1, -0.4))
        say(p, "Můj kámen se zmenšil!", *hbe(p.X(0.5), p.Y(0.03), 1.25), w=100, area=(0.3, 0.62))
        say(p, "Ne. Voda je vyšší!", *ha(p.X(0.7), p.Y(0.03), 1.05), w=90, area=(0.62, 1.0))
    with Pn(*R[1]) as p:
        gy = creek_bank(p, 112, 1, creek_=(0.1, 0.6), gy_f=0.78, stones=(0.3, 0.42, 0.54, 0.66))
        cap(p, "Kameny přes potok jsou napůl pod vodou.", w=170, where="tl")
    with Pn(*R[2]) as p:
        gy = creek_bank(p, 113, 1, creek_=(0.08, 0.6), gy_f=0.76)
        tata(p.X(0.5), p.Y(0.1), 0.9, mood="grin", look=(1, 0), shadow=False)
        wading(p.X(0.5), p.Y(0.1), p.Y(0.1) + 22, 34)
        hanka(p.X(0.5) + 4, p.Y(0.1) + 94, 0.7, mood="grin", right="up", left="up", shadow=False)
        cap(p, "Táta přenáší holky.", w=110, where="tl")
    with Pn(*R[3]) as p:
        gy = creek_bank(p, 114, 1, creek_=(0.12, 0.46), gy_f=0.62)
        J(p, p.X(0.58), p.Y(0.12), 1.15, mood="happy")
        wading(p.X(0.62), p.Y(0.12), p.Y(0.12) + 16, 46)
        hanka(p.X(0.84), p.Y(0.3), 1.05, flip=True, mood="wow", look=(-1, 0), right="up")
        sfx(p.X(0.24), p.Y(0.72), "ŠPLOUCH!", 24, -4)
        zb(p.X(0.08), p.Y(0.06), 10)
        cap(p, "Joey do vody nechce. Ale kam jde Hanka, tam jde on!", w=200, where="tl")
        say(p, "Joey! Ty jsi statečný!", *hh(p.X(0.84), p.Y(0.3), 1.05), w=90, area=(0.66, 1.0))
    page_end()


# =================================================================== 12 the tracks in the mud
def page_tracks():
    R = rows([(300, [1]), (210, [0.5, 0.5]), (240, [1])])
    with Pn(*R[0]) as p:
        gy = creek_bank(p, 121, 1, creek_=(0.46, 0.6), gy_f=0.72)
        fill([(p.x - 5, p.Y(0.47)), (p.x + p.w + 5, p.Y(0.47)), (p.x + p.w + 5, p.Y(0.2)), (p.x - 5, p.Y(0.24))], P.MUD)
        drag_slide([(p.X(0.92), p.Y(0.16)), (p.X(0.78), p.Y(0.3)), (p.X(0.7), p.Y(0.47))], 26)
        bobr_trail([(p.X(0.3), p.Y(0.27)), (p.X(0.52), p.Y(0.42))], 1.0)
        alica(p.X(0.14), p.Y(0.03), 1.05, mood="wow", right="point", look=(1, -0.3))
        tonda(p.X(0.55), p.Y(0.03), 1.0, flip=True, mood="surprised", look=(-1, -0.3))
        say(p, "Stopy! A obrovské!", *ha(p.X(0.14), p.Y(0.03), 1.05), w=90, area=(0.0, 0.34))
        say(p, "Vlkodlak!!!", *htd(p.X(0.55), p.Y(0.03), 1.0), w=80, area=(0.36, 0.7))
    with Pn(*R[1]) as p:
        bg_fill(p, P.MUD)
        vydra_print(p.X(0.25), p.Y(0.42), 3.0, 0)
        bobr_print(p.X(0.68), p.Y(0.4), 3.6, 0)
        hand_text(p.X(0.05), p.Y(0.12), p.w*0.4, "vydra", "SHB", 13)
        hand_text(p.X(0.48), p.Y(0.12), p.w*0.4, "tahle", "SHB", 13)
        keep_clear(p, p.X(0.05), p.Y(0.1), p.X(0.95), p.Y(0.66), "stopy")
        cap(p, "Tahle je obrovská. A prsty má spojené.", w=180, where="tl")
    with Pn(*R[2]) as p:
        bg_fill(p, P.MUD)
        bobr_trail([(p.X(0.05), p.Y(0.2)), (p.X(0.95), p.Y(0.5))], 1.4)
        keep_clear(p, p.X(0.05), p.Y(0.1), p.X(0.95), p.Y(0.62), "stopy")
        cap(p, "Mezi stopami je šmouha. Jako by se tu něco táhlo.", w=190, where="tl")
    with Pn(*R[3]) as p:
        gy = creek_bank(p, 122, 1, creek_=(0.32, 0.48), gy_f=0.62)
        alica(p.X(0.16), p.Y(0.03), 1.15, mood="determined", right="lens", lens=True, look=(1, 0))
        betka(p.X(0.62), p.Y(0.03), 1.3, flip=True, hat=False, mood="think", look=(-1, 0))
        zb(p.X(0.4), p.Y(0.44), -14)
        say(p, "To není vydra! Vydra má malé tlapky.", *ha(p.X(0.16), p.Y(0.03), 1.15), w=140, area=(0.0, 0.44))
        say(p, "Je to něco velkého. A plave to.", *hbe(p.X(0.62), p.Y(0.03), 1.3), w=120, area=(0.44, 0.9))
    page_end()


# =================================================================== 13 the second night: the watch
def page_watch():
    R = rows([(330, [1]), (200, [0.5, 0.5]), (220, [1])])
    with Pn(*R[0]) as p:
        gy = louka(p, 0.62, 131, night=True)
        stan(p.X(0.5), p.Y(0.12), 1.6, "dome", door="glow")
        glow(p.X(0.5), p.Y(0.2), 150, 0.08)
        ve_spacaku(tonda, 47, p.X(0.14), p.Y(0.03), 1.0, mood="sleepy")
        zzz(p.X(0.14) + 14, p.Y(0.03) + 100)
        ve_spacaku(alica, 45, p.X(0.36), p.Y(0.03), 1.05, P.SLEEPING_BAG_2, mood="determined", look=(1, 0))
        ve_spacaku(hanka, 31, p.X(0.6), p.Y(0.03), 1.15, P.SLEEPING_BAG, mood="grin", right="front", look=(1, 0),
                   item=lambda x, y: torch(x, y, 15))
        ve_spacaku(betka, 31, p.X(0.84), p.Y(0.03), 1.25, P.SLEEPING_BAG_2, hat=False, mood="happy", look=(-1, 0))
        hd("tonda", p.X(0.14), p.Y(0.03) - 47*0.5, 1.0)
        cap(p, "Druhá noc. Hlídka u stanu.", w=150, where="tl")
        say(p, "Nikdo neusne!", *ha(p.X(0.36), p.Y(0.03) - 45*1.05*0.5, 1.05), w=80, area=(0.2, 0.55))
        say(p, "Já svítím!", *hh(p.X(0.6), p.Y(0.03) - 31*1.15*0.5, 1.15), w=70, area=(0.5, 0.75))
    with Pn(*R[1]) as p:
        _panel_fill(p, P.NIGHT_MEADOW)
        fill([(p.x, p.y), (p.x + p.w, p.y), (p.x + p.w, p.Y(0.6)), (p.x, p.Y(0.6))], P.CREEK_DEEP)
        night_tint(p, 0.4)
        torch_beam(p.x, p.Y(0.9), p.X(0.3), p.Y(0.0), p.X(1.0), p.Y(0.42), 0.35)
        plesk(p.X(0.6), p.Y(0.3), 1.6)
        sfx(p.X(0.12), p.Y(0.7), "PLESK!", 26, 6)
    with Pn(*R[2]) as p:
        _panel_fill(p, P.NIGHT_MEADOW)
        fill([(p.x, p.y), (p.x + p.w, p.y), (p.x + p.w, p.Y(0.6)), (p.x, p.Y(0.6))], P.CREEK_DEEP)
        night_tint(p, 0.4)
        torch_beam(p.x, p.Y(0.9), p.X(0.3), p.Y(0.0), p.X(1.0), p.Y(0.42), 0.35)
        for k in (1.0, 1.5): stroke(ell(p.X(0.6), p.Y(0.3), 26*k, 5*k, 24), BG, closed=True, g=P.POND_RIPPLE)
        cap(p, "A pak ticho. Jen kroužky na vodě.", w=150, where="tl")
    with Pn(*R[3]) as p:
        gy = louka(p, 0.62, 132, night=True)
        ve_spacaku(tonda, 47, p.X(0.2), p.Y(0.03), 1.05, mood="surprised", look=(1, 0))
        ve_spacaku(alica, 45, p.X(0.62), p.Y(0.03), 1.1, P.SLEEPING_BAG_2, mood="whisper", right="hush", look=(-1, 0))
        say(p, "Co? Kde? Vlkodlak?", *htd(p.X(0.2), p.Y(0.03) - 47*1.05*0.5, 1.05), w=100, area=(0.0, 0.45))
        say(p, "Psst! Už je pryč. Uplaval.", *ha(p.X(0.62), p.Y(0.03) - 45*1.1*0.5, 1.1), w=110, area=(0.45, 1.0),
            whisper=True)
    page_end()


# =================================================================== 14 the lupa: two big teeth
def page_teeth():
    R = rows([(290, [1]), (230, [0.5, 0.5]), (230, [1])])
    with Pn(*R[0]) as p:
        gy = creek_bank(p, 141, 2, creek_=(0.4, 0.54), gy_f=0.66)
        pahyl(p.X(0.55), p.Y(0.14), 1.6); tresky(p.X(0.55), p.Y(0.14), 70, 18, 11, 1.2)
        padla_vrbka(p.X(0.6), p.Y(0.16), 1.0, seed=5)
        alica(p.X(0.36), p.Y(0.03), 1.1, mood="think", right="lens", lens=True, look=(1, -0.6))
        hanka(p.X(0.12), p.Y(0.03), 1.1, mood="worried", look=(1, 0))
        cap(p, "Ráno leží další strom.", w=130, where="tr")
        say(p, "Zase!", *hh(p.X(0.12), p.Y(0.03), 1.1), w=60, area=(0.0, 0.24))
        say(p, "Podívám se lupou.", *ha(p.X(0.36), p.Y(0.03), 1.1), w=90, area=(0.18, 0.5))
    with Pn(*R[1]) as p:
        bg_fill(p, 0.9)
        inset(p, p.X(0.5), p.Y(0.4), p.w*0.7, p.h*0.68, lambda x, y: zuby_closeup(x, y, 1.4))
        magnifier(p.X(0.88), p.Y(0.15), ang=-40, r=10)
        cap(p, "Drážky. Vždycky dvě vedle sebe.", w=150, where="tl")
    with Pn(*R[2]) as p:
        gy = creek_bank(p, 142, 2, creek_=(0.36, 0.5), gy_f=0.66)
        alica(p.X(0.3), p.Y(0.03), 1.2, mood="wow", look=(1, 0))
        say(p, "Dva velké zuby vedle sebe! A ostré jako dláto!", *ha(p.X(0.3), p.Y(0.03), 1.2), w=130, area=(0.42, 1.0))
    with Pn(*R[3]) as p:
        gy = creek_bank(p, 143, 2, creek_=(0.36, 0.5), gy_f=0.64, rock_x=0.9)
        betka(p.X(0.6), p.Y(0.03), 1.3, flip=True, hat=False, mood="happy", right="front", look=(-1, 0))
        for k in range(3):
            skicak(p.X(0.06) + k*70, p.Y(0.14), 62, 50, k, (-4, 3, -2)[k], k + 1)
        keep_clear(p, p.X(0.05), p.Y(0.12), p.X(0.06) + 210, p.Y(0.14) + 56, "kresby")
        zb(p.X(0.78), p.Y(0.06), 6)
        say(p, "Třetí obrázek. Kámen skoro zmizel!", *hbe(p.X(0.6), p.Y(0.03), 1.3), w=120, area=(0.42, 1.0))
    page_end()


# =================================================================== 15 the guide (full page)
def page_guide():
    with Pn(M, 40, W-2*M, H-80, bg=0.97) as p:
        hand_text(p.X(0.04), p.Y(0.955), p.w*0.92, "Kdo to byl? Průvodce detektivky", "SHB", 26)
        hand_text(p.X(0.04), p.Y(0.915), p.w*0.92, "Porovnej, co našla Alica. Kdo kácí stromy u potoka?", "SH", 13)
        secs = [
            ("Jak je dřevo uříznuté?", [
                ("pilka", "rovně, placka", lambda x, y: saw_closeup(x, y, 0.8)),
                ("nožík", "dlouhé tenké kudrlinky", lambda x, y: kudrlinky(x, y - 4, 1.8, 4, 2)),
                ("noční návštěvník", "špička jako tužka, tlusté třísky", lambda x, y: (pahyl(x, y - 24, 1.3),
                                                                                       tresky(x, y - 24, 50, 10, 5, 0.9))),
            ], 0.62),
            ("Jaké jsou stopy?", [
                ("pes", "kulatá, čtyři prsty", lambda x, y: dog_print(x, y, 3.6, ink=True)),
                ("vydra", "malá, kulatá, pět prstů", lambda x, y: vydra_print(x, y, 3.2, ink=True)),
                ("noční návštěvník", "obrovská, prsty spojené blánou, šmouha od ocasu",
                 lambda x, y: (ocas_smouha([(x - 46, y - 18), (x + 46, y - 10)], 8), bobr_print(x, y + 4, 2.6, ink=True))),
            ], 0.335),
            ("Jak kouše?", [
                ("pes", "malé kulaté dírky", lambda x, y: dog_bite(x, y, 1.0, 0)),
                ("", "", None),
                ("noční návštěvník", "dva velké zuby vedle sebe: široké drážky", lambda x, y: zuby_closeup(x, y, 0.55)),
            ], 0.05),
        ]
        for head_, cells, fy_ in secs:
            hand_text(p.X(0.05), p.Y(fy_) + p.h*0.255, p.w*0.9, head_, "SHB", 16, align="left")
            cw = p.w*0.92/3
            for i, (name, tip, fig) in enumerate(cells):
                if fig is None: continue
                cx = p.X(0.04) + i*cw
                shape(rrect(cx + 4, p.Y(fy_), cw - 8, p.h*0.24, 8), 1.0, 1.1)
                C.saveState(); C.clipPath(poly(rrect(cx + 6, p.Y(fy_) + 2, cw - 12, p.h*0.24 - 4, 7)), stroke=0, fill=0)
                fig(cx + cw/2, p.Y(fy_) + p.h*0.15)
                C.restoreState()
                hand_text(cx + 8, p.Y(fy_) + 30, cw - 16, name, "SHB", 13)
                hand_text(cx + 8, p.Y(fy_) + 14, cw - 16, tip, "SH", 10, lead=11)
        hand_text(p.X(0.36), p.Y(0.2), p.w*0.28, "Kdo má velké ostré zuby, plovací blány a plochý ocas?",
                  "SHB", 12, lead=15)
        keep_clear(p, p.x, p.y, p.x + p.w, p.y + p.h, "guide")
    page_end()


# =================================================================== 16 STOP, DETEKTIVE!
def page_stop():
    with Pn(M, 40, W-2*M, H-80, bg=0.95) as p:
        title(p.X(0.5), p.Y(0.92), "STOP, DETEKTIVE!", 44)
        hand_text(p.X(0.05), p.Y(0.86), p.w*0.9, "Kdo kácí stromy u potoka? A proč stoupá voda?", "SHB", 17)
        cw, ch = p.w*0.3, p.h*0.19
        items = [
            ("pahýl jako tužka (strana 7)", lambda x, y: pahyl(x, y, 1.1)),
            ("tlusté třísky (strana 9)", lambda x, y: tresky(x, y + 14, 50, 9, 3, 1.2)),
            ("„PLESK!“ v noci (strany 6 a 13)", lambda x, y: plesk(x, y + 10, 0.9)),
            ("dědova hůl zmizela (strana 7)", lambda x, y: deda_hul(x - 20, y + 2, 0.5, -50)),
            ("Bětčiny obrázky kamene (strana 14)", lambda x, y: (skicak(x - 38, y, 24, 20, 0, 0, 1), skicak(x - 12, y, 24, 20, 1, 0, 2),
                                                                 skicak(x + 14, y, 24, 20, 2, 0, 3))),
            ("obrovská stopa s blánou (strana 12)", lambda x, y: bobr_print(x, y + 18, 1.6, ink=True)),
            ("šmouha mezi stopami (strana 12)", lambda x, y: bobr_trail([(x - 40, y + 6), (x + 40, y + 24)], 0.5)),
            ("dva velké zuby (strana 14)", lambda x, y: (C.saveState(), C.clipPath(poly(ell(x, y + 20, 26, 20, 30)), stroke=0, fill=0),
                                                         zuby_closeup(x, y + 20, 0.5), C.restoreState())),
            ("vydra to není (strana 12)", lambda x, y: vydra_print(x, y + 18, 1.8, ink=True)),
        ]
        for i, (txt, pic) in enumerate(items):
            cx = p.X(0.04) + (i % 3)*(cw + p.w*0.02); cy = p.Y(0.82) - (i//3 + 1)*(ch + 10)
            shape(rrect(cx, cy, cw, ch, 8), 1.0, 1.2)
            hand_text(cx + 6, cy + ch - 20, 30, str(i + 1), "SHB", 16, align="left")
            with T(cx + cw/2, cy + 50, 1.5):
                pic(0, 0)
            hand_text(cx + 8, cy + 22, cw - 16, txt, "SH", 10.5, lead=12)
        by = p.Y(0.82) - 3*(ch + 10)
        hand_text(p.X(0.05), by - 26, p.w*0.9, "Ukaž prstem! Kdo má velké zuby a plave? A kde je dědova hůl?", "SH", 14)
        with T(p.X(0.5), p.Y(0.03), 1.0, rot=180):
            hand_text(-p.w*0.45, 0, p.w*0.9, "Byl to mladý bobr! Kácí vrby zuby a staví si z větví hráz.", "SH", 12)
            hand_text(-p.w*0.45, -15, p.w*0.9, "Hráz zadržuje vodu, proto voda stoupá. A dědova hůl je v hrázi.", "SH", 12)
    page_end()


# =================================================================== 17 upstream on the bike
def page_upstream():
    R = rows([(300, [1]), (210, [0.5, 0.5]), (240, [1])])
    with Pn(*R[0]) as p:
        gy = creek_bank(p, 171, 2, creek_=(0.36, 0.5), gy_f=0.64)
        for fx in (0.03, 0.97): tree_edge(p, p.X(fx), gy - 6, 1.1, int(fx*10) + 5)
        bobr_trail([(p.X(0.08), p.Y(0.04)), (p.X(0.4), p.Y(0.2)), (p.X(0.62), p.Y(0.34))], 0.8)
        rider(alica, p.X(0.32), p.Y(0.06), 1.0, mood="determined", look=(1, 0))
        J(p, p.X(0.7), p.Y(0.06), 1.0, pose="sniff")
        cap(p, "Alica jede proti proudu. Joey čmuchá po stopě.", w=220, where="tl")
        say(p, "Čmuchej, Joey! Kam to vede?", *ha(p.X(0.32) - 5, p.Y(0.06) + 15, 1.0), w=120, area=(0.15, 0.6))
    with Pn(*R[1]) as p:
        gy = creek_bank(p, 172, 2, creek_=(0.36, 0.5), gy_f=0.64)
        deda(p.X(0.2), p.Y(0.03), 0.9, mood="happy", look=(1, 0), legs="walk")
        hanka(p.X(0.45), p.Y(0.03), 1.05, mood="worried", look=(1, 0), legs="walk")
        tonda(p.X(0.72), p.Y(0.03), 0.95, mood="grin", look=(1, 0), legs="walk")
        say(p, "Počkejte na mě!", *hh(p.X(0.45), p.Y(0.03), 1.05), w=90, area=(0.25, 0.75))
    with Pn(*R[2]) as p:
        gy = creek_bank(p, 173, 2, creek_=(0.36, 0.5), gy_f=0.64)
        betka(p.X(0.3), p.Y(0.03), 1.25, hat=False, mood="happy", look=(1, 0), legs="walk")
        mama(p.X(0.66), p.Y(0.03), 0.92, mood="happy", look=(1, 0), legs="walk")
        cap(p, "Všichni za ní.", w=100, where="tl")
    with Pn(*R[3]) as p:
        gy = louka(p, 0.68, 174)
        water([(p.x - 5, p.Y(0.2)), (p.x + p.w + 5, p.Y(0.2)), (p.x + p.w + 5, p.Y(0.62)), (p.x - 5, p.Y(0.6))], 8, 6)
        reeds(p.X(0.9), p.Y(0.58), 0.8, 3)
        kolo(p.X(0.3), p.Y(0.03), 1.0)
        alica(p.X(0.14), p.Y(0.03), 1.05, mood="wow", left="up", look=(1, 0.2))
        say(p, "Tady je z potoka najednou rybníček!", *ha(p.X(0.14), p.Y(0.03), 1.05), w=130, area=(0.0, 0.6))
    page_end()


# =================================================================== 18 the dam; děda's stick; the hajný
def page_dam():
    R = rows([(320, [1]), (200, [0.5, 0.5]), (230, [1])])
    with Pn(*R[0]) as p:
        foot, top = pond_dam(p, 0.36, 46, 181)
        alica(p.X(0.12), p.Y(0.02), 1.05, mood="wow", right="point", look=(1, 0.3), shadow=False)
        wading(p.X(0.12), p.Y(0.02), p.Y(0.02) + 10, 30)
        J(p, p.X(0.86), p.Y(0.04), 1.0, flip=True, mood="bark")
        sfx(p.X(0.62), p.Y(0.9), "HAF!", 18, 6)
        zb(p.X(0.34), top + 6, 0)
        say(p, "Hráz! Z větví a z bláta!", *ha(p.X(0.12), p.Y(0.02), 1.05), w=110, area=(0.0, 0.5))
    with Pn(*R[1]) as p:
        bg_fill(p, P.MUD)
        rd = random.Random(3)
        for i in range(18):
            a = math.radians(rd.uniform(-35, 35) + (180 if i % 2 else 0)); bx, by = p.X(rd.uniform(0, 1)), p.Y(rd.uniform(0, 1))
            stroke([(bx - math.cos(a)*40, by - math.sin(a)*40), (bx + math.cos(a)*40, by + math.sin(a)*40)], LINE*4.6)
            stroke([(bx - math.cos(a)*40, by - math.sin(a)*40), (bx + math.cos(a)*40, by + math.sin(a)*40)], LINE*3.0,
                   g=P.BARK if i % 3 else P.WOOD_PALE)
        deda_hul(p.X(0.1), p.Y(0.3), 1.5, -72, peeled=True)
        keep_clear(p, p.X(0.05), p.Y(0.2), p.X(0.95), p.Y(0.65), "hul")
        cap(p, "A v hrázi… dědova hůl! Bez kůry.", w=160, where="tl")
    with Pn(*R[2]) as p:
        gy = creek_bank(p, 182, 2, creek_=(0.36, 0.5), gy_f=0.66)
        deda(p.X(0.4), p.Y(0.03), 1.0, mood="wow", right="front", look=(1, 0),
             item=lambda x, y: deda_hul(x - 6, y - 50, 0.75, -10, peeled=True))
        say(p, "Moje hůl! Pořád má hvězdu z Klubu.", *hdd(p.X(0.4), p.Y(0.03), 1.0), w=120, area=(0.0, 1.0))
    with Pn(*R[3]) as p:
        gy = creek_bank(p, 183, 2, creek_=(0.36, 0.5), gy_f=0.64)
        for fx in (0.95,): tree_edge(p, p.X(fx), gy - 6, 1.2, 9)
        alica(p.X(0.14), p.Y(0.03), 1.1, mood="surprised", look=(1, 0))
        hajny(p.X(0.72), p.Y(0.03), 0.95, flip=True, mood="happy", right="wave", look=(-1, 0))
        say(p, "Pan hajný!", *ha(p.X(0.14), p.Y(0.03), 1.1), w=80, area=(0.0, 0.32))
        say(p, "Dobrý den, detektivové. Vidím, že jste našli hráz.", *hj(p.X(0.72), p.Y(0.03), 0.95), w=160, area=(0.36, 1.0))
    page_end()


# =================================================================== 19 the hajný explains
def page_explain():
    R = rows([(260, [1]), (220, [1/3, 1/3, 1/3]), (270, [1])])
    with Pn(*R[0]) as p:
        gy = creek_bank(p, 191, 2, creek_=(0.36, 0.5), gy_f=0.64)
        hajny(p.X(0.18), p.Y(0.03), 0.95, mood="happy", right="point", look=(1, 0))
        alica(p.X(0.5), p.Y(0.03), 1.05, flip=True, mood="wow", look=(-1, 0))
        hanka(p.X(0.72), p.Y(0.03), 1.1, flip=True, mood="wow", look=(-1, 0))
        say(p, "Tu hráz postavil bobr. Mladý bobr.", *hj(p.X(0.18), p.Y(0.03), 0.95), w=130, area=(0.0, 0.44))
        say(p, "Bobr?!", *ha(p.X(0.5), p.Y(0.03), 1.05), w=60, area=(0.4, 0.62))
        say(p, "Jako v pohádce?", *hh(p.X(0.72), p.Y(0.03), 1.1), w=80, area=(0.6, 1.0))
    pics = [("Bobří rodina bydlí dole u starého rybníka.", 0),
            ("Mladý bobr se letos vydal hledat vlastní potok.", 1),
            ("A tady si staví první hráz a nový domov.", 2)]
    for k, (txt, kind) in enumerate(pics):
        with Pn(*R[1 + k], bg=0.95) as p:
            fill([(p.x, p.y), (p.x + p.w, p.y), (p.x + p.w, p.Y(0.5)), (p.x, p.Y(0.5))], P.CREEK)
            if kind == 0:
                bobri_hrad(p.X(0.5), p.Y(0.24), p.w*0.7, p.h*0.4, 0.55)
                bobr(p.X(0.3), p.Y(0.42), 0.6, pose="swim"); bobr(p.X(0.75), p.Y(0.4), 0.5, pose="swim", flip=True)
            elif kind == 1:
                bobr(p.X(0.4), p.Y(0.38), 0.9, pose="swim")
                for j in range(3): stroke([(p.X(0.62 + j*0.1), p.Y(0.4)), (p.X(0.68 + j*0.1), p.Y(0.4))], LINE*1.4)
                shape([(p.X(0.94), p.Y(0.44)), (p.X(0.99), p.Y(0.4)), (p.X(0.94), p.Y(0.36))], 0.2, LINE)
            else:
                hraz(p.X(0.15), p.X(0.85), p.Y(0.3), 30, 7)
                bobr(p.X(0.55), p.Y(0.46), 0.7, pose="sit", branch=True)
            hand_text(p.X(0.04), p.Y(0.93) - 12, p.w*0.92, txt, "SH", 11, lead=13)
    with Pn(*R[4]) as p:
        gy = creek_bank(p, 192, 2, creek_=(0.36, 0.5), gy_f=0.64)
        rybar(p.X(0.14), p.Y(0.03), 0.95, mood="worried", look=(1, 0), rod=False)
        hajny(p.X(0.48), p.Y(0.03), 0.95, flip=True, mood="happy", look=(-1, 0))
        tonda(p.X(0.8), p.Y(0.03), 1.0, flip=True, mood="grin", look=(-1, 0))
        say(p, "A moje ryby?", *hf(p.X(0.14), p.Y(0.03), 0.95), w=80, area=(0.0, 0.32))
        say(p, "Bobr ryby nejí, Franto. Jen kůru, větvičky a listí.", *hj(p.X(0.48), p.Y(0.03), 0.95), w=150, area=(0.2, 0.7))
        say(p, "Takže žádný vlkodlak…", *htd(p.X(0.8), p.Y(0.03), 1.0), w=100, area=(0.66, 1.0))
    page_end()


# =================================================================== 20 the beaver fact page (full page)
def page_facts():
    with Pn(M, 40, W-2*M, H-80, bg=0.97) as p:
        hand_text(p.X(0.04), p.Y(0.955), p.w*0.92, "Bobr: co o něm víme", "SHB", 28)
        hand_text(p.X(0.04), p.Y(0.915), p.w*0.92, "Pan hajný vypráví. Bětka kreslí.", "SH", 13)
        facts = [
            ("Největší hlodavec v Evropě. Velký bobr váží 20 až 30 kilo. Jako Hanka!",
             lambda x, y: (bobr(x - 30, y, 0.9, pose="sit"), hanka(x + 34, y, 0.6, mood="grin", shadow=False))),
            ("Má oranžové zuby. Jsou tvrdé jako železo a pořád mu rostou. Okusováním si je obrušuje.",
             lambda x, y: bobr(x, y - 8, 1.3, pose="sit", branch=True)),
            ("Tenkou vrbu pokácí za jednu noc. Ohryže ji dokola, až zbude špička jako tužka.",
             lambda x, y: (pahyl(x - 24, y, 1.4), padla_vrbka(x - 16, y + 2, 0.45))),
            ("Ryby nejí! Jí kůru, větvičky, listí a vodní rostliny.",
             lambda x, y: (deda_hul(x - 40, y + 14, 0.6, -80, peeled=True), leknin(x + 30, y + 6, 1.2))),
            ("Plochý ocas je kormidlo. A když hrozí nebezpečí, plácne s ním o vodu: PLESK! Všichni se schovají.",
             lambda x, y: (fill([(x - 60, y - 10), (x + 60, y - 10), (x + 60, y + 6), (x - 60, y + 6)], P.CREEK),
                           bobr(x + 20, y + 6, 0.9, pose="slap"))),
            ("Pod vodou vydrží asi čtvrt hodiny. Uši a nos si zavře.",
             lambda x, y: (fill([(x - 60, y - 20), (x + 60, y - 20), (x + 60, y + 30), (x - 60, y + 30)], P.CREEK),
                           bobr(x, y + 30, 1.0, pose="swim"))),
            ("Vchod do bobřího domu je pod vodou. Liška se tam nedostane. Proto bobr staví hráze: aby měl vody dost.",
             lambda x, y: bobri_hrad(x, y - 6, 120, 60, 0.55)),
            ("Mladí bobři se ve dvou letech odstěhují od rodičů a hledají vlastní potok.",
             lambda x, y: (fill([(x - 60, y - 10), (x + 60, y - 10), (x + 60, y + 12), (x - 60, y + 12)], P.CREEK),
                           bobr(x - 18, y + 4, 0.7, pose="swim"), bobr(x + 34, y + 4, 0.5, pose="swim"))),
            ("Kdysi u nás bobři úplně zmizeli. Teď se vrátili a jsou chránění. Jejich hráze dělají domov žábám, vážkám i ptákům.",
             lambda x, y: (frog(x - 30, y, 1.6), frog(x + 30, y + 4, 1.2, flip=True))),
        ]
        cw, ch = p.w*0.92/3, p.h*0.27
        for i, (txt, pic) in enumerate(facts):
            cx = p.X(0.04) + (i % 3)*cw; cy = p.Y(0.88) - (i//3 + 1)*(ch + 6)
            shape(rrect(cx + 4, cy, cw - 8, ch, 8), 1.0, 1.1)
            C.saveState(); C.clipPath(poly(rrect(cx + 6, cy + 2, cw - 12, ch - 4, 7)), stroke=0, fill=0)
            pic(cx + cw/2, cy + ch*0.62)
            C.restoreState()
            hand_text(cx + 10, cy + ch*0.42, cw - 20, txt, "SH", 10.5, lead=12.5)
        keep_clear(p, p.x, p.y, p.x + p.w, p.y + p.h, "facts")
        hand_text(p.X(0.04), p.Y(0.025), p.w*0.92, "Kdo pozoruje bobry, chodí potichu, nesvítí jim do očí a nic jim neničí.",
                  "SHB", 12)
    page_end()


# =================================================================== 21 dusk: waiting by the dam
def page_dusk():
    R = rows([(330, [1]), (200, [0.5, 0.5]), (220, [1])])
    with Pn(*R[0]) as p:
        foot, top = pond_dam(p, 0.5, 40, 211, stick=False, night=True)
        bush_y = p.Y(0.03)
        hajny(p.X(0.14), bush_y, 0.9, mood="whisper", right="hush", look=(1, 0), shadow=False)
        alica(p.X(0.36), bush_y, 0.95, mood="whisper", look=(1, 0.3), shadow=False)
        hanka(p.X(0.52), bush_y, 1.0, mood="wow", look=(1, 0.3), shadow=False, item=lambda x, y: torch(x, y, 0), right="front")
        tonda(p.X(0.7), bush_y, 0.9, mood="worried", look=(1, 0.3), shadow=False)
        betka(p.X(0.88), bush_y, 1.1, hat=False, mood="happy", look=(-1, 0.3), shadow=False)
        rd = random.Random(21)
        for fx in (0.08, 0.27, 0.46, 0.64, 0.83, 1.0):
            with T(p.X(fx), p.y - 4, 1.0):
                bush = bez((-58, 0), (-64, 50), (-30, 66), (-10, 58)) + bez((-10, 58), (6, 72), (40, 64), (46, 48)) + \
                       bez((46, 48), (62, 40), (62, 10), (58, 0))
                shape(bush, P.FOREST_DARK, LINE)
                for k in range(8):
                    stroke(ell(rd.uniform(-40, 40), rd.uniform(14, 52), 6, 4, 12, 200, 340), LINE*0.6, g=0.2)
        night_tint(p, 0.2)
        cap(p, "Večer. Všichni se schovají u hráze.", w=170, where="tl")
        say(p, "Potichu… A nesvítit, dokud neřeknu.", *hj(p.X(0.2), bush_y + 10, 0.9), w=130, area=(0.0, 0.5), whisper=True)
    with Pn(*R[1]) as p:
        _panel_fill(p, P.NIGHT_MEADOW)
        water([(p.x - 5, p.y - 5), (p.x + p.w + 5, p.y - 5), (p.x + p.w + 5, p.Y(0.7)), (p.x - 5, p.Y(0.7))], 6, 4)
        night_tint(p, 0.45)
        for k in (1.0, 1.6, 2.3): stroke(ell(p.X(0.5), p.Y(0.4), 18*k, 4*k, 24), BG, closed=True, g=P.POND_RIPPLE)
        cap(p, "Na hladině se něco pohnulo…", w=150, where="tl")
    with Pn(*R[2]) as p:
        _panel_fill(p, P.NIGHT_MEADOW)
        fill([(p.x, p.y), (p.x + p.w, p.y), (p.x + p.w, p.Y(0.3)), (p.x, p.Y(0.3))], P.FOREST_DARK)
        night_tint(p, 0.35)
        hajny(p.X(0.25), p.Y(0.03), 1.0, mood="whisper", right="point", look=(1, 0), shadow=False)
        hanka(p.X(0.7), p.Y(0.03), 1.2, flip=True, mood="wow", look=(-1, 0), shadow=False, item=lambda x, y: torch(x, y, 170),
              right="front")
        say(p, "Teď, Hanko. Jen trošku.", *hj(p.X(0.25), p.Y(0.03), 1.0), w=100, area=(0.0, 0.55), whisper=True)
    with Pn(*R[3]) as p:
        gy = louka(p, 0.7, 212, night=True, forest=True)
        hanka(p.X(0.14), p.Y(0.03), 1.25, mood="wow", right="front", look=(1, 0.3), item=lambda x, y: torch(x, y, 15))
        torch_beam(p.X(0.14) + 30, p.Y(0.03) + 74, p.X(0.6), p.Y(0.62), p.X(1.0), p.Y(0.2), 0.42)
        hand_text(p.X(0.4), p.Y(0.35), p.w*0.55, "otoč stránku…", "SHB", 18, g=1.0)
    page_end()


# =================================================================== 22 Hryzálek (full page)
def page_beaver():
    with Pn(M, 40, W-2*M, H-80) as p:
        _panel_fill(p, P.NIGHT_MEADOW)
        far_trees_y = p.Y(0.78)
        from pond import far_trees
        far_trees(p, far_trees_y, 7, P.FOREST_DARK)
        water([(p.x - 5, p.y - 5), (p.x + p.w + 5, p.y - 5), (p.x + p.w + 5, far_trees_y), (p.x - 5, far_trees_y)], 9, 10)
        night_stars(p, 0.84, 30, 9)
        night_tint(p, 0.35)
        torch_beam(p.X(0.08), p.Y(0.06), p.X(0.2), p.Y(0.7), p.X(1.0), p.Y(0.3), 0.5)
        glow(p.X(0.58), p.Y(0.46), 160, 0.08)
        bobr(p.X(0.58), p.Y(0.42), 3.6, pose="swim", branch=True)
        reeds(p.X(0.94), p.Y(0.02), 1.6, 5)
        with T(p.X(0.1), p.Y(-0.02), 1.0):
            shape(bez((-90, 0), (-90, 80), (80, 90), (110, 0)), P.FOREST_DARK, LINE)
        hanka(p.X(0.12), p.Y(-0.06), 1.8, mood="wow", right="front", look=(1, 0.4), item=lambda x, y: torch(x, y, 20),
              shadow=False)
        sfx(p.X(0.42), p.Y(0.88), "ŠŠŠ…", 20, 0, fill_g=0.9)
        hand_text(p.X(0.5), p.Y(0.12), p.w*0.45, "Mladý bobr! S vrbovou větví v puse.", "SHB", 18, g=1.0, lead=22)
    page_end()


# =================================================================== 23 eating bark; PLESK; the name
def page_name():
    R = rows([(300, [1]), (200, [0.5, 0.5]), (250, [1])])
    with Pn(*R[0]) as p:
        foot, top = pond_dam(p, 0.36, 40, 231, stick=False, night=True)
        torch_beam(p.x, p.Y(0.1), p.X(0.4), p.Y(0.9), p.X(0.75), p.Y(0.3), 0.4)
        BB(p, p.X(0.56), top - 4, 1.6, pose="sit", branch=True)
        cap(p, "Bobr si sedne na hráz a okusuje kůru. Jako kukuřici!", w=230, where="tl")
        say(p, "On papá!", tx=p.X(0.1), ty=p.Y(0.05), w=70, area=(0.0, 0.3), whisper=True)
    with Pn(*R[1]) as p:
        gy = louka(p, 0.65, 232, night=True)
        J(p, p.X(0.45), p.Y(0.03), 1.4, mood="happy")
        for k in range(3): stroke([(p.X(0.18) - k*6, p.Y(0.4) + k*8), (p.X(0.25) - k*6, p.Y(0.46) + k*8)], LINE, g=1.0)
        cap(p, "Joey to nevydrží…", w=110, where="tl")
    with Pn(*R[2]) as p:
        _panel_fill(p, P.NIGHT_MEADOW)
        water([(p.x - 5, p.y - 5), (p.x + p.w + 5, p.y - 5), (p.x + p.w + 5, p.Y(0.6)), (p.x - 5, p.Y(0.6))], 4, 3)
        night_tint(p, 0.35)
        bobr(p.X(0.3), p.Y(0.3), 1.4, pose="slap")
        J(p, p.X(0.72), p.Y(0.05), 1.2, flip=True, mood="sad", wet=True)
        sfx(p.X(0.08), p.Y(0.8), "PLESK!", 24, -6)
    with Pn(*R[3]) as p:
        gy = louka(p, 0.66, 233, night=True)
        J(p, p.X(0.5), p.Y(0.03), 1.1, mood="sad", wet=True)
        alica(p.X(0.14), p.Y(0.03), 1.1, mood="grin", look=(1, 0))
        hanka(p.X(0.82), p.Y(0.03), 1.15, flip=True, mood="grin", right="up", look=(-1, 0), item=lambda x, y: torch(x, y, 80))
        say(p, "Chudák Joey! Bobr ho postříkal!", *ha(p.X(0.14), p.Y(0.03), 1.1), w=120, area=(0.0, 0.4))
        say(p, "Bude se jmenovat Hryzálek!", *hh(p.X(0.82), p.Y(0.03), 1.15), w=110, area=(0.6, 1.0))
        say(p, "Hryzálek. To se mi líbí.", *ha(p.X(0.14), p.Y(0.03), 1.1), w=100, area=(0.0, 0.42))
    page_end()


# =================================================================== 24 mesh, new stones, the tin
def page_mesh():
    R = rows([(290, [1]), (210, [0.5, 0.5]), (250, [1])])
    with Pn(*R[0]) as p:
        gy = camp(p, 0.55, 241, tents=((0.86, "dome", 0.5),))
        for fx in (0.32, 0.56):
            vrbka(p.X(fx), p.Y(0.12), 1.0, int(fx*10))
            pletivo(p.X(fx), p.Y(0.12), 26, 34)
        hajny(p.X(0.14), p.Y(0.03), 0.95, mood="happy", right="point", look=(1, 0))
        tata(p.X(0.72), p.Y(0.03), 0.95, flip=True, mood="happy", right="front", look=(-1, 0))
        say(p, "Pletivo ochrání naše vrby. Ty u hráze nechte jemu.", *hj(p.X(0.14), p.Y(0.03), 0.95), w=150, area=(0.0, 0.5))
        say(p, "Domluveno, Hryzálku.", *ht(p.X(0.72), p.Y(0.03), 0.95), w=100, area=(0.55, 1.0))
    with Pn(*R[1]) as p:
        gy = creek_bank(p, 242, 2, creek_=(0.4, 0.56), gy_f=0.7)
        tonda(p.X(0.3), p.Y(0.03), 1.0, mood="determined", right="front", left="front", look=(1, 0),
              item=lambda x, y: shape(ell(x + 6, y - 2, 14, 10, 20), P.STONE, LINE))
        say(p, "Já nesu největší!", *htd(p.X(0.3), p.Y(0.03), 1.0), w=90, area=(0.4, 1.0))
    with Pn(*R[2]) as p:
        gy = creek_bank(p, 243, 2, creek_=(0.12, 0.6), gy_f=0.78, stones=(0.3, 0.42, 0.54, 0.66))
        for i, fx in enumerate((0.36, 0.48, 0.6, 0.72)):
            stone_top(p.X(fx), p.Y(0.2 + i*0.1), 13, 4, 0)
        zb(p.X(0.88), p.Y(0.06), 0)
        cap(p, "Nové kameny. Vyšší. Ať má Hryzálek svoji vodu.", w=180, where="tl")
    with Pn(*R[3]) as p:
        gy = creek_bank(p, 244, 0, creek_=(0.1, 0.4), gy_f=0.62)
        bx0, bx1, by0, by1 = p.X(0.54), p.X(0.66), p.Y(0.02), p.Y(0.46)
        for k in range(10):
            t0, t1 = k/10, (k + 1)/10
            w0, w1 = 46*(1 - t0*0.55), 46*(1 - t1*0.55)
            yy0, yy1 = by0 + (by1 - by0)*t0, by0 + (by1 - by0)*t1
            cx0, cx1 = bx0 + (bx1 - bx0)*t0, bx0 + (bx1 - bx0)*t1
            shape([(cx0 - w0, yy0), (cx0 + w0, yy0), (cx1 + w1, yy1 - 2), (cx1 - w1, yy1 - 2)], 0.72, LINE*0.6)
        treasure_tin(p.X(0.76), p.Y(0.16), 0.6, dirty=True)
        keep_clear(p, p.X(0.5), p.Y(0.02), p.X(0.84), p.Y(0.46), "tin")
        betka(p.X(0.2), p.Y(0.03), 1.3, hat=False, mood="wow", right="point", look=(1, -0.2))
        cap(p, "Pod hrází teď teče méně vody. U staré lávky se něco leskne.", w=210, where="tr")
        say(p, "Tam něco je!", *hbe(p.X(0.2), p.Y(0.03), 1.3), w=80, area=(0.0, 0.4))
    page_end()


# =================================================================== 25 Věrka; the Klub tin; the castle drawing
def page_tin():
    R = rows([(280, [1]), (210, [0.5, 0.5]), (260, [1])])
    with Pn(*R[0]) as p:
        gy = camp(p, 0.55, 251, tents=((0.5, "old", 0.45),))
        verka_old(p.X(0.14), p.Y(0.03), 0.95, mood="grin", look=(1, 0),
                  item=None)
        deda(p.X(0.52), p.Y(0.03), 1.0, flip=True, mood="wow", right="front", look=(-1, 0),
             item=lambda x, y: treasure_tin(x - 6, y - 10, 0.45))
        alica(p.X(0.84), p.Y(0.03), 1.05, flip=True, mood="wow", look=(-1, 0))
        say(p, "Nesu buchty! Co to máte?", *hv(p.X(0.14), p.Y(0.03), 0.95), w=100, area=(0.0, 0.36))
        say(p, "Věrko… to je naše plechovka z Klubu!", *hdd(p.X(0.52), p.Y(0.03), 1.0), w=130, area=(0.3, 0.75))
    with Pn(*R[1]) as p:
        bg_fill(p, P.EARLY_SUMMER_GRASS)
        treasure_tin(p.X(0.5), p.Y(0.1), 1.6, open_=True)
        badge(p.X(0.2), p.Y(0.3), 12)
        keep_clear(p, p.X(0.05), p.Y(0.05), p.X(0.95), p.Y(0.7), "tin")
        cap(p, "Uvnitř: odznak s hvězdou…", w=150, where="tl")
    with Pn(*R[2]) as p:
        bg_fill(p, P.EARLY_SUMMER_GRASS)
        club_photo(p.X(0.18), p.Y(0.12), 150, 110, -3)
        keep_clear(p, p.X(0.15), p.Y(0.1), p.X(0.18) + 156, p.Y(0.12) + 114, "photo")
        cap(p, "…fotka Klubu na Hvězdné louce…", w=170, where="tl")
    with Pn(*R[3]) as p:
        gy = camp(p, 0.6, 252, tents=())
        hrad_kresba(p.X(0.4), p.Y(0.2), 110, 136, 4)
        keep_clear(p, p.X(0.38), p.Y(0.18), p.X(0.4) + 114, p.Y(0.2) + 140, "kresba")
        verka_old(p.X(0.14), p.Y(0.03), 0.95, mood="think", look=(1, 0.3))
        alica(p.X(0.86), p.Y(0.03), 1.1, flip=True, mood="wow", right="lens", lens=True, look=(-1, 0.3))
        cap(p, "…a kresba hradu.", w=100, where="tr")
        say(p, "Věž… hvězda… a čtrnáctka: XIV.", *hv(p.X(0.14), p.Y(0.03), 0.95), w=110, area=(0.0, 0.36))
        say(p, "„Další poklad je na…“ Kde?! Je to utržené!", *ha(p.X(0.86), p.Y(0.03), 1.1), w=130, area=(0.62, 1.0))
    page_end()


# =================================================================== 26 the last morning: the gift taken
def page_last():
    R = rows([(290, [1]), (210, [0.5, 0.5]), (250, [1])])
    with Pn(*R[0]) as p:
        gy = creek_bank(p, 261, 2, creek_=(0.36, 0.5), gy_f=0.64)
        drag_slide([(p.X(0.66), p.Y(0.18)), (p.X(0.72), p.Y(0.36))], 22, 5)
        tresky(p.X(0.62), p.Y(0.2), 60, 14, 21, 1.3)
        hanka(p.X(0.4), p.Y(0.03), 1.2, mood="wow", right="point", look=(1, 0.2))
        alica(p.X(0.14), p.Y(0.03), 1.05, mood="happy", look=(1, 0))
        cap(p, "Poslední ráno. Hanka nechala Hryzálkovi na břehu svůj oloupaný klacík.", w=230, where="tl")
        say(p, "Je pryč! Hryzálek si vzal můj dárek!", *hh(p.X(0.4), p.Y(0.03), 1.2), w=130, area=(0.28, 0.8))
    with Pn(*R[1]) as p:
        gy = camp(p, 0.55, 262, tents=((0.3, "dome", 0.7),))
        tata(p.X(0.72), p.Y(0.03), 0.95, flip=True, mood="happy", right="front", look=(-1, 0))
        cap(p, "Balíme stany.", w=100, where="tl")
    with Pn(*R[2]) as p:
        gy = camp(p, 0.55, 263, tents=())
        taborak(p.X(0.36), p.Y(0.1), 1.0, lit=True)
        J(p, p.X(0.66), p.Y(0.03), 1.1, flip=True, mood="sleepy")
        jx, jy = p.X(0.66), p.Y(0.03)
        for k in range(4):
            bx = jx - 16 + k*12
            stroke(bez((bx, jy + 44), (bx - 4, jy + 54), (bx + 4, jy + 62), (bx, jy + 72)), LINE*0.9, g=0.55)
        cap(p, "Joey se suší u ohně. Celý se kouří.", w=150, where="tl")
    with Pn(*R[3]) as p:
        gy = camp(p, 0.55, 264, tents=())
        alica(p.X(0.25), p.Y(0.03), 1.15, mood="happy", right="hug", look=(1, 0))
        hanka(p.X(0.62), p.Y(0.03), 1.15, flip=True, mood="grin", right="hug", look=(-1, 0))
        say(p, "Tohle byl náš nejmokřejší případ!", *ha(p.X(0.25), p.Y(0.03), 1.15), w=120, area=(0.0, 0.45))
        say(p, "Ahoj, Hryzálku!", *hh(p.X(0.62), p.Y(0.03), 1.15), w=90, area=(0.45, 0.85))
        cap(p, "Případ č. 13 vyřešen.", w=130, where="br")
    page_end()


# =================================================================== 27 activity (no pencil)
def dam_mini(x, y, w, h, variant):
    """one of the two "spot the difference" pictures of the dam; variant 1 has five things changed"""
    with Pn(x, y, w, h) as q:
        gy = louka(q, 0.75, 271, clouds=False)
        water([(q.x - 5, q.Y(0.4)), (q.x + q.w + 5, q.Y(0.4)), (q.x + q.w + 5, q.Y(0.72)), (q.x - 5, q.Y(0.72))], 3, 3)
        fill([(q.x - 5, q.y - 5), (q.x + q.w + 5, q.y - 5), (q.x + q.w + 5, q.Y(0.32)), (q.x - 5, q.Y(0.32))], P.CREEK)
        top = hraz(q.X(0.05), q.X(0.95), q.Y(0.3), 24, 9, q.X(0.62) if variant == 0 else None)
        bobr(q.X(0.4), top - 2, 0.6, pose="sit", branch=variant == 0)
        frog(q.X(0.86), q.Y(0.06), 0.7)
        if variant == 0: duck(q.X(0.2), q.Y(0.55), 0.6)
        if variant == 0: reeds(q.X(0.94), q.Y(0.7), 0.5, 2)
        else: reeds(q.X(0.06), q.Y(0.7), 0.5, 2)
        if variant == 1: cloud(q.X(0.3), q.Y(0.9), 0.4)


def page_quiz():
    with Pn(M, 40, W-2*M, H-80) as p:
        box = [(p.X(0.05), p.Y(0.905)), (p.X(0.95), p.Y(0.91)), (p.X(0.95), p.Y(0.905)+54), (p.X(0.05), p.Y(0.905)+52)]
        fill(box, 0.92)
        for a_, b_ in ((0, 1), (1, 2), (2, 3), (3, 0)): stroke([box[a_], box[b_]], 1.5)
        hand_text(p.X(0.05), p.Y(0.905)+18, p.w*0.9, "Detektivní zápisník", "SHB", 26)
        hand_text(p.X(0.05), p.Y(0.865), p.w*0.9, "Bez tužky. Stačí prst a dobré oči!", "SH", 13)
        hand_text(p.X(0.05), p.Y(0.82), p.w*0.9, "1. Kdo bydlí u potoka? Ukaž prstem, kdo patří kam.", "SHB", 14, align="left")
        animals = [lambda x, y: bobr(x, y, 0.55, pose="sit"), lambda x, y: frog(x, y + 4, 1.3),
                   lambda x, y: duck(x, y + 8, 0.9), lambda x, y: badger(x, y + 4, 0.7)]
        homes = [lambda x, y: reeds(x, y, 0.7, 3), lambda x, y: hraz(x - 34, x + 34, y + 2, 18, 4),
                 lambda x, y: hole(x, y + 12, 40, 14, tin_print=False), lambda x, y: leknin(x, y + 6, 1.3)]
        for i, fn in enumerate(animals):
            cx = p.X(0.12 + i*0.25); cy = p.Y(0.68)
            shape(rrect(cx - 50, cy - 6, 100, 66, 8), 1.0, 1.0)
            fn(cx, cy + 4)
        for i, fn in enumerate(homes):
            cx = p.X(0.12 + i*0.25); cy = p.Y(0.55)
            shape(rrect(cx - 50, cy - 6, 100, 56, 8), 0.95, 1.0)
            fn(cx, cy + 6)
        y2 = p.Y(0.5)
        hand_text(p.X(0.05), y2, p.w*0.9, "2. Najdi 5 rozdílů mezi obrázky hráze.", "SHB", 14, align="left")
        pw, ph = p.w*0.44, 190
        dam_mini(p.X(0.04), y2 - 20 - ph, pw, ph, 0)
        dam_mini(p.X(0.52), y2 - 20 - ph, pw, ph, 1)
        y4 = y2 - 20 - ph - 30
        hidden_zabka(p.X(0.09), y4 - 10, 12, 0)          # the legend: not one of the hidden ten
        hand_text(p.X(0.15), y4 - 4, p.w*0.8,
                  f"V sešitě je schovaných {N_HIDDEN} žabiček, jako je tahle (ta se nepočítá). Najdeš je všechny?",
                  "SHB", 14, align="left", lead=18)
        pages = ", ".join(map(str, HID[:-1])) + " a " + str(HID[-1]) if HID else ""
        with T(p.X(0.5), p.Y(0.015), 1.0, rot=180):
            hand_text(-p.w*0.45, 0, p.w*0.9, f"Žabičky jsou na stranách {pages}.", "SH", 10)
            hand_text(-p.w*0.45, -13, p.w*0.9, "Bobr – hráz, žabka – leknín, kachna – rákosí, jezevec – nora.", "SH", 10)
            hand_text(-p.w*0.45, -26, p.w*0.9, "Rozdíly: větev u bobra, dědova hůl, kachna, rákosí na druhé straně, mráček.",
                      "SH", 10)
    page_end()


# =================================================================== 28 back cover: next time
def back_cover():
    with Pn(M, 40, W-2*M, H-80, bg=0.95) as p:
        hand_text(p.X(0.1), p.Y(0.93), p.w*0.8, "Příště v sešitě č. 14:", "SHB", 20)
        title(p.X(0.5), p.Y(0.84), "POKLAD NA HRADĚ", 36)
        with Pn(p.X(0.08), p.Y(0.3), p.w*0.84, p.h*0.48, bg=0.9) as q:
            sky(q, P.SPRING_SKY)
            cloud(q.X(0.2), q.Y(0.85), 0.7)
            hills(q, q.Y(0.3), 60, P.FAR_FIELD, 4)
            with T(q.X(0.66), q.Y(0.48), 1.6):
                shape([(-24, 0), (24, 0), (24, 80), (-24, 80)], P.CASTLE_STONE, LINE*1.2)
                for k in range(5): shape([(-24 + k*10, 80), (-18 + k*10, 80), (-18 + k*10, 88), (-24 + k*10, 88)], P.CASTLE_STONE, LINE)
                shape(rrect(-5, 40, 10, 16, 5), 0.2, LINE)
                stroke([(0, 88), (0, 112)], LINE*1.2)
                shape([(0, 112), (18, 106), (0, 100)], P.TAG_STAR, LINE*0.8)
                star(7, 106, 3, 1.0)
                shape([(-50, 0), (60, 0), (60, 22), (-50, 22)], P.CASTLE_STONE, LINE)
            ground(q, q.Y(0.22), P.EARLY_SUMMER_GRASS)
            hrad_kresba(q.X(0.06), q.Y(0.3), 70, 86, -8)
            alica(q.X(0.3), q.Y(0.04), 1.0, mood="think", right="lens", lens=True, look=(1, 0.4))
            hanka(q.X(0.44), q.Y(0.04), 1.05, mood="wow", right="point", look=(1, 0.4))
            hand_text(q.X(0.86), q.Y(0.75), q.w*0.12, "?", "SHB", 34)
        hand_text(p.X(0.1), p.Y(0.24), p.w*0.8, "Kam vede kresba z plechovky? Velká a malá detektivka jede na hrad!", "SH", 16, lead=21)
        hand_text(p.X(0.1), p.Y(0.13), p.w*0.8, "Co je XIV?", "SHB", 16)
        hand_text(p.X(0.1), p.Y(0.015), p.w*0.8, "Velká a malá detektivka – sešit č. 13", "SH", 13, g=0.35)
    PAGE[0] += 1; cv.showPage()


def zzz(x, y, s=1.0):
    for i, (dx, dy, k) in enumerate(((0, 0, 1.0), (8, 9, 0.8), (14, 17, 0.6))):
        hand_text(x + dx*s - 10, y + dy*s, 20, "z", "SHB", 13*k*s, g=1.0)


cover(); page_cast(); page_go(); page_tents(); page_evening(); page_night(); page_morning(); page_board()
page_compare(); page_franta(); page_rising(); page_tracks(); page_watch(); page_teeth(); page_guide(); page_stop()
page_upstream(); page_dam(); page_explain(); page_facts(); page_dusk(); page_beaver(); page_name(); page_mesh()
page_tin(); page_last(); page_quiz(); back_cover()
cv.save()
print("ok", PAGE[0] - 1, "pages")
import letter
if letter.MISSING: PROBLEMS.append("no glyph in the font for: " + " ".join(sorted(letter.MISSING)))
if len(HID) != N_HIDDEN: PROBLEMS.append(f"{len(HID)} hidden frogs drawn, the notebook promises {N_HIDDEN}")
for pr in PROBLEMS: print("ORDER/LAYOUT:", pr)
if PROBLEMS: sys.exit(1)
