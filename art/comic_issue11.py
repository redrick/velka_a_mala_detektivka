"""Velká a malá detektivka, issue 11: Kam mizí vajíčka? (outline: vault topics/comic-series/issue11-outline)"""
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
from tracks import dog_print, fox_print, liska
from village import candy_wrapper
from props_extra import binoculars
from pond import verka_old, mill, lantern, torch_beam
from winter import betka
from skola import mama, tata, vito, hobliny, kid_print, hay_wisp, morce
from velikonoce import *
import chars3

W, H = A4
M = 28; GUT = 9; TOP = H - 30
OUT = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                   "comics", "velka_a_mala_detektivka", "11_kam_mizi_vajicka.pdf")
os.makedirs(os.path.dirname(OUT), exist_ok=True)
cv = canvas.Canvas(OUT, pagesize=A4); lib.set_canvas(cv)
cv.setTitle("Velká a malá detektivka – Případ č. 11: Kam mizí vajíčka?")
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



# =================================================================== issue 11 helpers
HEAD.update({"mama": (107.6, 10.2), "tata": (122.6, 10.8)})
HID = []   # pages with a hidden kraslice, in order; the activity page's answer key is built from it
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
def ht(x, y, s): return hd("tata", x, y, s)
def ha(x, y, s): return hd("alica", x, y, s)
def hh(x, y, s): return hd("hanka", x, y, s)
def hb(x, y, s): return hd("babi", x, y, s)
def hdd(x, y, s): return hd("deda", x, y, s)
def htd(x, y, s): return hd("tonda", x, y, s)


def kr(x, y, rot=0):
    """one of the 10 hidden kraslice"""
    hidden_kraslice(x, y, 13, rot, HID_KINDS[len(HID) % len(HID_KINDS)])
    HID.append(PAGE[0])


def J(p, x, y, s, flip=False, pose="stand", **kw):
    """Joey, collar buried in his fur, head kept clear of balloons"""
    joey(x, y, s, flip=flip, pose=pose, collar=False, **kw)
    l, r, b, t = (23, 46, 15, 40) if pose == "sniff" else (18, 41, 36, 61)
    if flip: l, r = -r, -l
    keep_clear(p, x + l*s, y + b*s, x + r*s, y + t*s, "joey")


def K(p, x, y, s, **kw):
    """Kropenatka, kept clear of balloons"""
    kropenatka(x, y, s, **kw)
    keep_clear(p, x - 16*s, y, x + 16*s, y + 30*s, "kropenatka")


def inset(p, x, y, w, h, fn, label=None):
    """a round close-up inside a panel (a print seen through the lupa)"""
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


def kitchen(p, table=True, evening=False):
    """babička's kitchen at the chalupa; returns the floor/table line the figures stand on"""
    bg_fill(p, P.KITCHEN_WALL)
    for yy in range(int(p.Y(0.35)), int(p.y+p.h), 16): stroke([(p.x, yy), (p.x+p.w, yy)], BG*0.4, g=0.7)
    for xx in range(int(p.x), int(p.x+p.w), 16): stroke([(xx, p.Y(0.35)), (xx, p.y+p.h)], BG*0.4, g=0.7)
    shelf(p.X(0.02), p.X(0.02)+120, p.Y(0.72))
    for i, g in enumerate((P.JAM, 0.75, P.JAM, 0.55)): jar(p.X(0.02)+22+i*22, p.Y(0.72)+5, 14 + (i % 2)*4, g)
    wall_clock(p.X(0.93), p.Y(0.8), 13)
    shape([(p.x, p.y), (p.x+p.w, p.y), (p.x+p.w, p.Y(0.35)), (p.x, p.Y(0.35))], 0.7, BG)
    if evening:
        bg_fill(p, 0.0, 0.22)
        lx, ly = p.X(0.5), p.y + p.h
        fill([(lx, ly - 30), (lx - 160, p.Y(0.2)), (lx + 160, p.Y(0.2))], P.LANTERN_GLOW, 0.25)
        stroke([(lx, ly), (lx, ly - 22)], 1.0)
        shape(bez((lx - 18, ly - 34), (lx - 14, ly - 20), (lx + 14, ly - 20), (lx + 18, ly - 34)) + [(lx - 18, ly - 34)], 0.35, 1.0)
    return p.Y(0.03)


def table_front(p, y=0.3, x0=0.15, x1=0.85):
    """the kitchen table in front of the figures (drawn after them): its top edge at y; things go on it"""
    shape([(p.X(x0), p.y - 4), (p.X(x1), p.y - 4), (p.X(x1), p.Y(y)), (p.X(x0), p.Y(y))], P.CLOTH_CHECK, BG)
    for k in range(1, 8):
        xx = p.X(x0) + (p.X(x1) - p.X(x0))*k/8
        stroke([(xx, p.y), (xx, p.Y(y))], BG*0.5, g=1.0, alpha=0.5)
    return p.Y(y)


def bedroom_night(p):
    """the girls' room at the chalupa on a spring night; returns the floor line"""
    bg_fill(p, P.BEDROOM_WALL)
    for xx in range(int(p.x) + 12, int(p.x + p.w), 26): stroke([(xx, p.Y(0.3)), (xx, p.y + p.h)], 0.5, g=0.82)
    floor_y = p.y + 14
    shape([(p.x - 5, p.y - 5), (p.x + p.w + 5, p.y - 5), (p.x + p.w + 5, floor_y), (p.x - 5, floor_y)], P.FLOOR, BG)
    x0, x1, y0, y1 = p.X(0.06), p.X(0.26), p.Y(0.5), p.Y(0.88)
    shape([(x0 - 5, y0 - 5), (x1 + 5, y0 - 5), (x1 + 5, y1 + 5), (x0 - 5, y1 + 5)], P.DOOR_FRAME, BG)
    shape([(x0, y0), (x1, y0), (x1, y1), (x0, y1)], P.WINTER_NIGHT, BG)
    moon(x0 + (x1 - x0)*0.6, y0 + (y1 - y0)*0.65, 9)
    s_([((x0 + x1)/2, y0), ((x0 + x1)/2, y1)], BG*1.6, g=1.0)
    bg_fill(p, 0.0, 0.22)
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


def pytel(x, y, s=1.0):
    """táta's sack of wood shavings from his workshop"""
    with T(x, y, s):
        shape(bez((-14, 0), (-17, 14), (-15, 26), (-10, 30)) + [(10, 30)] + bez((10, 30), (15, 26), (17, 14), (14, 0)),
              P.PAPER_BAG, LINE*0.9)
        stroke(bez((-9, 27), (-3, 24), (3, 24), (9, 27)), LINE*0.6)
    hobliny(x, y + 30*s, 0.9*s, 4, 2)


def mud(p, y0, y1, seed=3):
    """a muddy strip across the bottom of a close-up"""
    bg_fill(p, P.SPRING_GRASS)
    r = random.Random(seed)
    pts = [(p.x - 5, p.Y(y0))] + [(p.x + p.w*i/12, p.Y(y1) + r.uniform(-6, 6)) for i in range(13)] + [(p.x + p.w + 5, p.Y(y0))]
    fill([(p.x - 5, p.y - 5)] + pts + [(p.x + p.w + 5, p.y - 5)], P.MUD)


def lantern_glow(x, y, r=60):
    fill(ell(x, y, r, r*0.8, 30), P.LANTERN_GLOW, 0.3)


def arrow_chalk(x, y, s=1.0, rot=0):
    """a chalk arrow on the ground or a fence (issue 12)"""
    with T(x, y, s, rot=rot):
        for w_, g in ((LINE*3.6, 0.0), (LINE*2.2, 1.0)):
            stroke([(-14, 0), (12, 0)], w_, g=g, taper=False)
            stroke([(4, 6), (13, 0), (4, -6)], w_, g=g, taper=False)


# =================================================================== 1 COVER
def cover():
    with Pn(M, 40, W-2*M, H-80) as p:
        gy = dvur(p, 0.4, 11, henhouse_x=0.2, henhouse_s=1.4, barn_x=0.74, barn_s=1.5, barn_kw=dict(door_open=True),
                  trees=((0.42, 1.1),), bushes=((0.05, 1.3), (0.97, 1.2)))
        run_fence(p.X(0.02), p.X(0.36), gy - 30, 60, p.X(0.3))
        for i, (fx, who) in enumerate(((0.06, 0), (0.12, 1), (0.21, 2))):
            slepice(p.X(fx), gy - 70 + (i % 2)*8, 1.6, who=who)
        egg_basket(p.X(0.62), p.Y(0.06), 2.2, 7)
        alica(p.X(0.47), p.Y(0.03), 2.0, mood="think", right="lens", lens=True, look=(1, -0.3))
        hanka(p.X(0.82), p.Y(0.03), 1.9, flip=True, mood="wow", right="front", look=(-1, -0.2),
              item=lambda x, y: torch(x, y, 190))
        J(p, p.X(0.14), p.Y(0.03), 1.6, mood="happy", pose="sniff")
        # a speckled tail peeking out from the bales in the barn door
        with T(p.X(0.69), gy + 8, 1.6):
            shape([(0, 0)] + bez((0, 0), (-5, 6), (-8, 13), (-5, 16)) + bez((-5, 16), (-3, 11), (0, 8), (4, 6)), P.KROPENATKA)
        dot(p.X(0.69) - 6, gy + 26, 1.2, P.KROPENATKA_DOT); dot(p.X(0.69) - 3, gy + 16, 1.2, P.KROPENATKA_DOT)
    box = [(M+34, H-236), (W-M-30, H-232), (W-M-34, H-48), (M+30, H-52)]
    fill([(x+3, y-3) for x, y in box], 0.0, 0.25); fill(box, 1.0)
    for a_, b_ in ((0, 1), (1, 2), (2, 3), (3, 0)): stroke([box[a_], box[b_]], 1.8)
    series_title(W/2, H-98, H-160, 40, 66)
    hand_text(M+40, H-190, W-2*M-80, "Alica, Hanka a Joey", "SHB", 20)
    hand_text(M+40, H-217, W-2*M-80, "Případ č. 11: Kam mizí vajíčka?", "SH", 15)
    magnifier(M+82, H-120, ang=-30, r=17)
    kraslice(W-M-96, H-140, 3.2, -15, "wax")
    page_end()


# =================================================================== 2 WHO IS WHO
def page_cast():
    with Pn(M, 40, W-2*M, H-80) as p:
        hand_text(p.X(0.05), p.Y(0.95), p.w*0.9, "Kdo je kdo", "SHB", 28)
        cells = [
            ("Alica", "Má lupu a zápisník.", lambda x, y: alica(x, y, 0.9, mood="happy", right="lens", lens=True)),
            ("Hanka", "Má opičku a baterku.", lambda x, y: hanka(x, y, 1.1, mood="grin")),
            ("Joey", "Ví víc, než se zdá.", lambda x, y: joey(x, y, 1.2, mood="happy", collar=False)),
            ("Babička a děda", "Na chalupě.", lambda x, y: (babicka(x - 22, y, 0.62, mood="happy"), deda(x + 22, y, 0.58, mood="happy"))),
            ("Máma a táta", "Přijeli taky.", lambda x, y: (mama(x - 22, y, 0.62, mood="happy", outfit="home"), tata(x + 22, y, 0.6, mood="happy"))),
            ("Babiččiny slepičky", "Je jich osm.", lambda x, y: (slepice(x - 26, y, 1.3, who=0), slepice(x, y, 1.3, who=1),
                                                                  slepice(x + 26, y, 1.3, who=2))),
            ("Kropenatka", "Slepička s tečkami.", lambda x, y: kropenatka(x, y, 1.8)),
            ("Tonda", "Kamarád od vedle.", lambda x, y: tonda(x, y, 0.8, mood="grin")),
            ("Paní Věrka", "Ze mlýna. Z Klubu Hvězdička.", lambda x, y: verka_old(x, y, 0.62, mood="happy")),
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
                  "Ve škole jsme našly Míšu a Šišu. Schoval je pan Karel do tepla. A pak jsme jely na Velikonoce na chalupu.",
                  "SH", 13, align="left", lead=17)
        morce(p.X(0.78), by + bh*0.3, 1.8, who="misa"); morce(p.X(0.9), by + bh*0.3, 1.6, who="sisa", flip=True)
    page_end()


# =================================================================== 3 Thursday: arrival
def page_arrival():
    R = rows([(300, [1]), (220, [0.5, 0.5]), (230, [1])])
    with Pn(*R[0]) as p:
        gy = dvur(p, 0.38, 31, house_x=0.6, house_s=1.15, trees=((0.9, 0.9),), bushes=((0.32, 0.8),))
        fence(p.X(0.36), p.X(0.98), p.Y(0.2), 30)
        vito(p.X(0.17), p.Y(0.06), 0.85)
        babicka(p.X(0.55), p.Y(0.03), 1.0, flip=True, mood="happy", right="wave", look=(-1, 0))
        deda(p.X(0.7), p.Y(0.03), 0.95, flip=True, mood="grin", right="wave", look=(-1, 0))
        J(p, p.X(0.38), p.Y(0.03), 1.1, mood="happy")
        sfx(p.X(0.36), p.Y(0.42), "CINK CINK", 13, 6)
        kr(p.X(0.96), p.Y(0.06), 20)
        cap(p, "Zelený čtvrtek. Jedeme na Velikonoce na chalupu!", w=230, where="tl")
        say(p, "Vítejte, holčičky!", *hb(p.X(0.55), p.Y(0.03), 1.0), w=110, area=(0.4, 0.75))
    with Pn(*R[1]) as p:
        gy = dvur(p, 0.4, 32, clouds=False)
        tata(p.X(0.25), p.Y(0.03), 0.92, mood="grin", right="front", left="front", look=(1, 0),
             item=lambda x, y: pytel(x - 2, y - 44, 0.75))
        say(p, "Nesu slepičkám hobliny z dílny. Na podestýlku!", *ht(p.X(0.25), p.Y(0.03), 0.92), w=115, area=(0.4, 1.0))
    with Pn(*R[2]) as p:
        gy = dvur(p, 0.4, 33, clouds=False)
        babicka(p.X(0.22), p.Y(0.03), 1.0, mood="happy", right="front", look=(1, 0),
                item=lambda x, y: egg_basket(x + 4, y - 18, 0.7, 5))
        say(p, "V sobotu budeme barvit vajíčka. Sbírám je celý týden.", *hb(p.X(0.22), p.Y(0.03), 1.0), w=140, area=(0.4, 1.0))
    with Pn(*R[3]) as p:
        gy = dvur(p, 0.4, 34, house_x=0.82, house_s=0.7)
        hanka(p.X(0.12), p.Y(0.03), 1.15, mood="grin", right="up", look=(1, 0))
        alica(p.X(0.32), p.Y(0.03), 1.1, mood="happy", look=(1, 0))
        babicka(p.X(0.6), p.Y(0.03), 1.0, flip=True, mood="worried", look=(-1, 0),
                item=lambda x, y: egg_basket(x - 4, y - 18, 0.7, 4))
        say(p, "Já chci taky!", *hh(p.X(0.12), p.Y(0.03), 1.15), w=80, area=(0.0, 0.22))
        say(p, "Babi, proč máš v košíku tak málo vajíček?", *ha(p.X(0.32), p.Y(0.03), 1.1), w=165, area=(0.2, 0.7))
        say(p, "No právě…", *hb(p.X(0.6), p.Y(0.03), 1.0), w=80, area=(0.5, 1.0))
    page_end()


# =================================================================== 4 the henhouse: the case
def page_henhouse():
    R = rows([(320, [1]), (200, [0.5, 0.5]), (230, [1])])
    with Pn(*R[0]) as p:
        gy = dvur(p, 0.43, 41, henhouse_x=0.5, henhouse_s=1.7, trees=((0.08, 0.9),), bushes=((0.93, 0.9),))
        run_fence(p.X(0.24), p.X(0.8), p.Y(0.3), 50)
        hens = [(0.3, 0, 0.36), (0.38, 1, 0.33), (0.46, 2, 0.37), (0.55, 3, 0.32), (0.63, 4, 0.36), (0.71, 5, 0.33),
                (0.43, 6, 0.27)]
        for fx, who, fy_ in hens:
            slepice(p.X(fx), p.Y(fy_), 1.15, flip=fx > 0.5, pose="peck" if who % 3 == 0 else "stand", who=who)
        kropenatka(p.X(0.76), p.Y(0.3), 1.15, flip=True, puff=True)
        babicka(p.X(0.12), p.Y(0.03), 0.95, mood="happy", right="point", look=(1, 0))
        alica(p.X(0.85), p.Y(0.03), 1.05, flip=True, mood="happy", look=(-1, 0))
        hanka(p.X(0.95), p.Y(0.03), 1.1, flip=True, mood="wow", look=(-1, 0))
        cap(p, "Babička má osm slepiček. Kropenatka je ta s tečkami.", w=230, where="tl")
        say(p, "Každá snese skoro každý den jedno vajíčko.", *hb(p.X(0.12), p.Y(0.03), 0.95), w=150, area=(0.0, 0.42))
    with Pn(*R[1]) as p:
        fy, boxes = kurnik_inside(p, 0.08)
        for bx, by in boxes: egg(bx, by + 4, 1.2)
        slepice(p.X(0.2), fy, 1.5, who=1)
        cap(p, "Hnízda v kurníku. Hobliny od táty.", w=170, where="tl")
    with Pn(*R[2]) as p:
        gy = dvur(p, 0.42, 42, clouds=False)
        babicka(p.X(0.22), p.Y(0.03), 1.0, mood="worried", right="chin", look=(1, 0))
        say(p, "Ale tenhle týden jich je pořád míň. Jedno vždycky chybí.", *hb(p.X(0.22), p.Y(0.03), 1.0), w=150, area=(0.4, 1.0))
    with Pn(*R[3]) as p:
        gy = dvur(p, 0.42, 43, henhouse_x=0.85, henhouse_s=0.9)
        alica(p.X(0.14), p.Y(0.03), 1.15, mood="determined", right="lens", lens=True, look=(1, 0))
        hanka(p.X(0.36), p.Y(0.03), 1.15, mood="grin", right="up", look=(-1, 0))
        J(p, p.X(0.56), p.Y(0.03), 1.0, mood="happy")
        kr(p.X(0.97), p.Y(0.85), -15)
        say(p, "Babi, to je případ pro nás!", *ha(p.X(0.14), p.Y(0.03), 1.15), w=120, area=(0.0, 0.32))
        say(p, "Velká a malá detektivka!", *hh(p.X(0.36), p.Y(0.03), 1.15), w=120, area=(0.26, 0.6))
    page_end()


# =================================================================== 5 Friday: counting
def page_count():
    R = rows([(280, [1]), (230, [0.5, 0.5]), (240, [1])])
    with Pn(*R[0]) as p:
        fy, boxes = kurnik_inside(p, 0.08)
        for bx, by in boxes: egg(bx, by + 4, 1.2)
        alica(p.X(0.12), fy, 1.0, mood="think", right="front", look=(1, 0),
              item=lambda x, y: egg_basket(x + 6, y - 18, 0.6, 4))
        hanka(p.X(0.32), fy, 1.1, mood="happy", right="point", look=(1, 0.3))
        cap(p, "Pátek ráno. Holky sbírají vajíčka.", w=180, where="tr")
        say(p, "Jedno, dvě, tři… sedm!", *hh(p.X(0.32), fy, 1.1), w=110, area=(0.0, 0.5))
    with Pn(*R[1]) as p:
        bg_fill(p, 0.9)
        shape(rrect(p.X(0.05), p.Y(0.08), p.w*0.9, p.h*0.68, 4), 1.0, 1.0)
        for k in range(5): stroke([(p.X(0.07), p.Y(0.18 + k*0.12)), (p.X(0.93), p.Y(0.18 + k*0.12))], 0.4, g=0.7)
        egg_tally(p.X(0.1), p.Y(0.7), p.w*0.8, [("Čt", 7), ("Pá", 7)], 13)
        keep_clear(p, p.X(0.05), p.Y(0.08), p.X(0.95), p.Y(0.76), "tally")
        cap(p, "Alica si to kreslí do zápisníku.", w=170, where="tl")
    with Pn(*R[2]) as p:
        fy, boxes = kurnik_inside(p, 0.08, seed=4)
        hanka(p.X(0.2), fy, 1.2, mood="grin", right="up", look=(1, 0))
        say(p, "Já vím! Bere je zajíček. Na barvení!", *hh(p.X(0.2), fy, 1.2), w=130, area=(0.32, 1.0))
    with Pn(*R[3]) as p:
        gy = dvur(p, 0.43, 51, henhouse_x=0.55, henhouse_s=1.1)
        run_fence(p.X(0.3), p.X(0.8), p.Y(0.24), 46)
        for i, fx in enumerate((0.38, 0.5, 0.62)): slepice(p.X(fx), p.Y(0.27), 1.0, who=i + 2, pose="peck" if i == 1 else "stand")
        kropenatka(p.X(0.74), p.Y(0.27), 1.0, flip=True, puff=True)
        alica(p.X(0.14), p.Y(0.03), 1.1, mood="grin", look=(1, 0))
        say(p, "Hani, zajíček vajíčka nosí, nebere!", *ha(p.X(0.14), p.Y(0.03), 1.1), w=140, area=(0.0, 0.5))
        sfx(p.X(0.82), p.Y(0.8), "KVOK!", 14, 6)
    page_end()


# =================================================================== 6 a fox?
def page_fox():
    R = rows([(280, [1]), (220, [0.5, 0.5]), (250, [1])])
    with Pn(*R[0]) as p:
        gy = dvur(p, 0.43, 61, henhouse_x=0.8, henhouse_s=1.0, bushes=((0.06, 0.9),))
        run_fence(p.X(0.55), p.X(1.0), p.Y(0.2), 50)
        fill(ell(p.X(0.45), p.Y(0.1), 60, 12, 24), P.MUD)
        for k in range(4): dog_print(p.X(0.38) + k*16, p.Y(0.09) + (k % 2)*6, 1.0, 80)
        deda(p.X(0.2), p.Y(0.03), 0.95, mood="surprised", right="point", look=(1, -0.3))
        alica(p.X(0.62), p.Y(0.03), 1.05, flip=True, mood="think", right="lens", lens=True, look=(-1, -0.4))
        say(p, "Že by liška? Tady u plotu jsou stopy!", *hdd(p.X(0.2), p.Y(0.03), 0.95), w=150, area=(0.0, 0.45))
    with Pn(*R[1]) as p:
        mud(p, 0.6, 0.65)
        for k, (fx, fy_) in enumerate(((0.25, 0.2), (0.45, 0.42), (0.68, 0.22), (0.85, 0.45))):
            dog_print(p.X(fx), p.Y(fy_), 2.6, 70)
        cap(p, "Velké stopy v blátě.", w=140, where="tl")
    with Pn(*R[2]) as p:
        bg_fill(p, 0.92)
        inset(p, p.X(0.27), p.Y(0.46), 110, 110, lambda x, y: fox_print(x, y, 4.0), "liška: úzká")
        inset(p, p.X(0.73), p.Y(0.46), 110, 110, lambda x, y: dog_print(x, y, 4.0), "pes: kulatá")
        cap(p, "Jak učil pan hajný:", w=140, where="tl")
    with Pn(*R[3]) as p:
        gy = dvur(p, 0.43, 62)
        fill(ell(p.X(0.55), p.Y(0.06), 60, 10, 24), P.MUD)
        J(p, p.X(0.55), p.Y(0.03), 1.25, pose="sniff", mood="happy")
        for k in range(5): dot(p.X(0.65) + k*7, p.Y(0.12) + (k % 2)*6, 2.2, P.MUD_DARK)
        sfx(p.X(0.72), p.Y(0.55), "HRAB HRAB!", 15, 6)
        alica(p.X(0.14), p.Y(0.03), 1.1, mood="grin", right="point", look=(1, 0))
        deda(p.X(0.9), p.Y(0.03), 0.9, flip=True, mood="grin", look=(-1, 0))
        kr(p.X(0.36), p.Y(0.08), -30)
        say(p, "Kulatá stopa. To byl Joey! Tady kope.", *ha(p.X(0.14), p.Y(0.03), 1.1), w=140, area=(0.0, 0.42))
        say(p, "Joey, ty kopáči!", *hdd(p.X(0.9), p.Y(0.03), 0.9), w=100, area=(0.62, 1.0))
    page_end()


# =================================================================== 7 no shells
def page_shells():
    R = rows([(270, [1]), (230, [0.5, 0.5]), (250, [1])])
    with Pn(*R[0]) as p:
        gy = dvur(p, 0.42, 71, henhouse_x=0.75, henhouse_s=1.0)
        deda(p.X(0.18), p.Y(0.03), 0.95, mood="think", right="chin", look=(1, 0))
        alica(p.X(0.5), p.Y(0.03), 1.05, flip=True, mood="think", look=(-1, 0))
        say(p, "Když liška nebo kuna sní vajíčko, zůstanou po ní skořápky.", *hdd(p.X(0.18), p.Y(0.03), 0.95), w=170, area=(0.0, 0.6))
    with Pn(*R[1]) as p:
        gy = dvur(p, 0.42, 72, clouds=False, bushes=((0.68, 1.4),))
        hanka(p.X(0.3), p.Y(0.03), 1.2, mood="determined", right="front", look=(1, 0), item=lambda x, y: torch(x, y, 10))
        say(p, "Tady nic!", *hh(p.X(0.3), p.Y(0.03), 1.2), w=80, area=(0.0, 0.5))
    with Pn(*R[2]) as p:
        gy = dvur(p, 0.42, 73, clouds=False, henhouse_x=0.62, henhouse_s=1.1)
        alica(p.X(0.25), p.Y(0.03), 1.15, mood="think", right="lens", lens=True, look=(1, -0.3))
        say(p, "Tady taky ne.", *ha(p.X(0.25), p.Y(0.03), 1.15), w=90, area=(0.0, 0.5))
    with Pn(*R[3]) as p:
        gy = dvur(p, 0.4, 74, trees=((0.86, 1.2),))
        magpie(p.X(0.86), gy + 110, 1.2, flip=True)
        alica(p.X(0.14), p.Y(0.03), 1.1, mood="think", right="chin", look=(1, 0))
        deda(p.X(0.55), p.Y(0.03), 0.92, flip=True, mood="happy", right="point", look=(1, 0.5))
        say(p, "Žádné skořápky. Nikdo je nesnědl…", *ha(p.X(0.14), p.Y(0.03), 1.1), w=150, area=(0.0, 0.36))
        say(p, "Straky taky kradou vajíčka. A koukej, kdo tam sedí!", *hdd(p.X(0.55), p.Y(0.03), 0.92), w=180, area=(0.34, 0.8))
    page_end()


# =================================================================== 8 the magpie
def page_magpie():
    R = rows([(380, [1]), (360, [0.5, 0.5])])
    with Pn(*R[0]) as p:
        gy = dvur(p, 0.35, 81, house_x=0.15, house_s=0.9, trees=((0.85, 1.4),), bushes=((0.4, 1.0),))
        magpie(p.X(0.62), p.Y(0.72), 2.0, item=lambda x, y: foil_ball(x + 3, y, 1.2))
        for k in range(3): stroke([(p.X(0.52) - k*14, p.Y(0.7) + k*6), (p.X(0.47) - k*14, p.Y(0.69) + k*6)], LINE*0.6, g=0.4)
        sfx(p.X(0.7), p.Y(0.9), "ČAK ČAK!", 16, 6)
        alica(p.X(0.18), p.Y(0.03), 1.25, mood="wow", right="point", look=(1, 0.5))
        hanka(p.X(0.36), p.Y(0.03), 1.3, mood="wow", right="point", look=(1, 0.5))
        J(p, p.X(0.58), p.Y(0.03), 1.3, mood="bark")
        kr(p.X(0.96), p.Y(0.05), 15)
        say(p, "Straka! Něco nese v zobáku!", *ha(p.X(0.18), p.Y(0.03), 1.25), w=120, area=(0.0, 0.3))
        say(p, "Bílé a lesklé!", *hh(p.X(0.36), p.Y(0.03), 1.3), w=100, area=(0.22, 0.5))
    with Pn(*R[1]) as p:
        gy = dvur(p, 0.38, 82, clouds=False)
        alica(p.X(0.35), p.Y(0.03), 1.25, mood="determined", look=(1, 0), legs="walk")
        hanka(p.X(0.65), p.Y(0.03), 1.3, mood="determined", look=(1, 0), legs="walk")
        cap(p, "Honem za ní!", w=110, where="tl")
        say(p, "Straky mají rády lesklé věci!", *ha(p.X(0.35), p.Y(0.03), 1.25), w=120, area=(0.0, 0.6))
    with Pn(*R[2]) as p:
        sky(p, P.SPRING_SKY)
        with T(p.X(0.5), p.y - 120, 2.4):
            stroke(bez((0, 0), (-2, 40), (2, 80), (0, 120)), LINE*16, g=0.0); stroke(bez((0, 0), (-2, 40), (2, 80), (0, 120)), LINE*13, g=P.BARK)
            stroke(bez((0, 90), (14, 100), (26, 108), (40, 114)), LINE*7, g=0.0); stroke(bez((0, 90), (14, 100), (26, 108), (40, 114)), LINE*5, g=P.BARK)
        straci_hnizdo(p.X(0.55), p.Y(0.52), 2.0, items=False)
        magpie(p.X(0.25), p.Y(0.75), 1.6)
        cap(p, "Hnízdo vysoko na stromě.", w=160, where="tl")
    page_end()


# =================================================================== 9 the magpie's treasure
def page_treasure():
    R = rows([(270, [1]), (230, [0.5, 0.5]), (250, [1])])
    with Pn(*R[0]) as p:
        gy = dvur(p, 0.4, 91, trees=((0.85, 1.3),))
        deda(p.X(0.55), p.Y(0.03), 0.95, flip=True, mood="happy", right="up", look=(1, 0.8),
             item=lambda x, y: binoculars(x, y + 6, 0.8))
        alica(p.X(0.14), p.Y(0.03), 1.1, mood="surprised", look=(1, 0.3))
        say(p, "Dědo, co tam vidíš?", *ha(p.X(0.14), p.Y(0.03), 1.1), w=110, area=(0.0, 0.35))
        say(p, "Alobal… mašli… a lžičku!", *hdd(p.X(0.55), p.Y(0.03), 0.95), w=130, area=(0.3, 0.7))
    with Pn(*R[1]) as p:
        bg_fill(p, P.SPRING_SKY)
        # two round eyepieces side by side with a gap between them, like a pair of eyes
        r = min(p.w*0.215, p.h*0.4); gap = r*0.14
        eyes = [(p.X(0.5) + sx*(r + gap/2), p.Y(0.5)) for sx in (-1, 1)]
        for ex, ey in eyes:
            fill(ell(ex, ey, r + 1.5, r + 1.5, 48), 0.0, 0.1)
        C.saveState()
        pth = C.beginPath()
        for ex, ey in eyes:
            E = ell(ex, ey, r, r, 48); pth.moveTo(*E[0])
            for q in E[1:]: pth.lineTo(*q)
            pth.close()
        C.clipPath(pth, stroke=0, fill=0)
        straci_hnizdo(p.X(0.45), p.Y(0.2), 3.0)
        C.restoreState()
        for ex, ey in eyes: stroke(ell(ex, ey, r, r, 48), LINE*1.4, closed=True)
        keep_clear(p, p.X(0.2), p.Y(0.2), p.X(0.8), p.Y(0.82), "binoculars")
        cap(p, "Žádné vajíčko.", w=110, where="tl")
    with Pn(*R[2]) as p:
        gy = dvur(p, 0.42, 92, clouds=False)
        hanka(p.X(0.22), p.Y(0.03), 1.2, mood="surprised", right="front", look=(1, 0),
              item=lambda x, y: choc_egg(x + 4, y - 2, 0.9, open_=True))
        say(p, "To je můj alobal! Z čokoládového vajíčka!", *hh(p.X(0.22), p.Y(0.03), 1.2), w=130, area=(0.36, 1.0))
    with Pn(*R[3]) as p:
        gy = dvur(p, 0.42, 93, house_x=0.85, house_s=0.7)
        babicka(p.X(0.18), p.Y(0.03), 1.0, mood="wow", look=(1, 0.5))
        alica(p.X(0.6), p.Y(0.03), 1.1, flip=True, mood="think", right="chin", look=(-1, 0))
        say(p, "A lžička je ta, co nám straka vzala na podzim!", *hb(p.X(0.18), p.Y(0.03), 1.0), w=160, area=(0.0, 0.48))
        say(p, "Takže straka to nebyla. Vajíčka nejsou lesklá.", *ha(p.X(0.6), p.Y(0.03), 1.1), w=150, area=(0.42, 1.0))
    page_end()


# =================================================================== 10 Tonda with a basket
def page_tonda():
    R = rows([(290, [1]), (220, [0.5, 0.5]), (240, [1])])
    with Pn(*R[0]) as p:
        gy = dvur(p, 0.42, 101, house_x=0.82, house_s=0.95, bushes=((0.2, 1.8),))
        fence(p.X(0.4), p.X(1.0), p.Y(0.12), 34)
        tonda(p.X(0.62), p.Y(0.03), 1.0, flip=True, mood="happy", right="front", look=(-1, 0),
              item=lambda x, y: egg_basket(x - 4, y - 18, 0.7, 9))
        alica(p.X(0.1), p.Y(0.03), 1.0, mood="whisper", look=(1, 0))
        hanka(p.X(0.26), p.Y(0.03), 1.05, mood="worried", look=(1, 0))
        forsythia(p.X(0.2), p.Y(0.0), 1.2, seed=7)
        say(p, "Pst! Tonda má košík plný vajíček!", *ha(p.X(0.1), p.Y(0.03), 1.0), w=130, area=(0.0, 0.38), whisper=True)
        say(p, "On je zloděj?", *hh(p.X(0.26), p.Y(0.03), 1.05), w=90, area=(0.2, 0.5), whisper=True)
    with Pn(*R[1]) as p:
        gy = dvur(p, 0.42, 102, clouds=False)
        alica(p.X(0.22), p.Y(0.03), 1.15, mood="determined", right="point", look=(1, 0))
        say(p, "Tondo! Kde jsi vzal ta vajíčka?", *ha(p.X(0.22), p.Y(0.03), 1.15), w=130, area=(0.36, 1.0))
    with Pn(*R[2]) as p:
        gy = dvur(p, 0.42, 103, clouds=False)
        tonda(p.X(0.22), p.Y(0.03), 1.05, mood="surprised", right="front", look=(1, 0),
              item=lambda x, y: egg_basket(x + 4, y - 18, 0.7, 9))
        say(p, "Od nás! Mamka je posílá paní Janě. Prý jí chybí.", *htd(p.X(0.22), p.Y(0.03), 1.05), w=140, area=(0.38, 1.0))
    with Pn(*R[3]) as p:
        gy = dvur(p, 0.42, 104, house_x=0.6, house_s=0.8)
        babicka(p.X(0.14), p.Y(0.03), 1.0, mood="grin", right="front", look=(1, 0),
                item=lambda x, y: egg_basket(x + 4, y - 18, 0.7, 9))
        tonda(p.X(0.82), p.Y(0.03), 1.0, flip=True, mood="grin", right="wave", look=(-1, 0))
        kr(p.X(0.45), p.Y(0.06), 25)
        say(p, "Děkuju, Tondo! Teď budeme mít na barvení dost.", *hb(p.X(0.14), p.Y(0.03), 1.0), w=160, area=(0.0, 0.5))
        say(p, "A v pondělí přijdu na koledu!", *htd(p.X(0.82), p.Y(0.03), 1.0), w=130, area=(0.55, 1.0))
    page_end()


# =================================================================== 11 grumpy Kropenatka
def page_kropenatka():
    R = rows([(280, [1]), (230, [0.5, 0.5]), (240, [1])])
    with Pn(*R[0]) as p:
        gy = dvur(p, 0.45, 111, henhouse_x=0.7, henhouse_s=1.2)
        run_fence(p.X(0.02), p.X(0.98), p.Y(0.32), 50)
        babicka(p.X(0.25), p.Y(0.03), 1.0, mood="surprised", right="front", left="front", look=(1, -0.4))
        K(p, p.X(0.48), p.Y(0.05), 1.7, flip=True, puff=True, straw=True)
        sfx(p.X(0.55), p.Y(0.55), "KVOK! KVOK!", 18, 6)
        alica(p.X(0.85), p.Y(0.03), 1.05, flip=True, mood="surprised", look=(-1, 0))
        say(p, "Kropenatko, co je s tebou?", *hb(p.X(0.25), p.Y(0.03), 1.0), w=120, area=(0.0, 0.4))
    with Pn(*R[1]) as p:
        bg_fill(p, P.SPRING_GRASS)
        kropenatka(p.X(0.5), p.Y(0.08), 4.0, puff=True, straw=True)
        keep_clear(p, p.X(0.15), p.Y(0.08), p.X(0.85), p.Y(0.85), "kropenatka")
        cap(p, "Načepýřená a mrzutá.", w=150, where="tl")
    with Pn(*R[2]) as p:
        gy = dvur(p, 0.43, 112, clouds=False)
        alica(p.X(0.22), p.Y(0.03), 1.15, mood="think", right="lens", lens=True, look=(1, 0))
        say(p, "Babi, ona má v peří stébla slámy!", *ha(p.X(0.22), p.Y(0.03), 1.15), w=130, area=(0.36, 1.0))
    with Pn(*R[3]) as p:
        gy = dvur(p, 0.43, 113, henhouse_x=0.9, henhouse_s=0.8)
        babicka(p.X(0.14), p.Y(0.03), 1.0, mood="happy", right="up", look=(1, 0))
        alica(p.X(0.62), p.Y(0.03), 1.1, flip=True, mood="think", right="chin", look=(-1, 0))
        say(p, "Slepice se hrabou všude, Alico. Pojď, uvaříme oběd.", *hb(p.X(0.14), p.Y(0.03), 1.0), w=170, area=(0.0, 0.5))
        say(p, "Ale v kurníku jsou hobliny…", *ha(p.X(0.62), p.Y(0.03), 1.1), w=120, area=(0.48, 1.0), whisper=True)
    page_end()


# =================================================================== 12 the list
def page_list():
    R = rows([(240, [1]), (310, [1]), (200, [1])])
    with Pn(*R[0]) as p:
        fy = kitchen(p, evening=True)
        deda(p.X(0.18), fy, 0.85, mood="think", right="chin", look=(1, 0))
        alica(p.X(0.72), fy, 1.0, flip=True, mood="determined", look=(-1, 0))
        say(p, "A co ježek? Ježci mají vajíčka rádi.", *hdd(p.X(0.18), fy, 0.85), w=140, area=(0.0, 0.45))
        say(p, "Ale pak by tu byly skořápky, dědo.", *ha(p.X(0.72), fy, 1.0), w=130, area=(0.5, 1.0))
    with Pn(*R[1]) as p:
        bg_fill(p, 0.9)
        notebook_big(p.X(0.06), p.Y(0.06), p.w*0.88, p.h*0.86, "PŘÍPAD Č. 11: KAM MIZÍ VAJÍČKA?",
                     ["1. Osm slepic, ale jen sedm vajíček.",
                      "2. Liška? Ne. Stopy u plotu jsou od Joeyho.",
                      "3. Straka? Ne. Má jen alobal a lžičku.",
                      "4. Tonda? Ne. Ten vajíčka nosí.",
                      "5. Ježek? Nikde nejsou skořápky.",
                      "6. Kropenatka je divná. Proč má v peří slámu?",
                      "7. Nikdo je nesnědl. Někdo je SCHOVÁVÁ!"])
        kr(p.X(0.9), p.Y(0.13), 20)
    with Pn(*R[2]) as p:
        fy = kitchen(p, evening=True)
        alica(p.X(0.18), fy, 1.0, mood="determined", right="up", look=(1, 0))
        J(p, p.X(0.82), fy, 0.95, flip=True, mood="happy")
        say(p, "Vajíčka jsou celá. Jsou někde schovaná!", *ha(p.X(0.18), fy, 1.0), w=160, area=(0.3, 0.75))
    page_end()


# =================================================================== 13 Saturday: dyeing
def page_dye():
    R = rows([(400, [1]), (340, [0.5, 0.5])])
    with Pn(*R[0]) as p:
        fy = kitchen(p)
        babicka(p.X(0.12), fy, 1.0, mood="happy", right="front", look=(1, -0.3))
        mama(p.X(0.33), fy, 1.0, outfit="home", mood="happy", right="front", look=(1, -0.3))
        hanka(p.X(0.52), fy, 1.15, mood="grin", right="front", look=(0, -0.3))
        alica(p.X(0.68), fy, 1.05, flip=True, mood="happy", right="front", look=(-0.5, -0.3))
        tata(p.X(0.87), fy, 0.95, flip=True, mood="think", right="front", look=(-1, -0.3))
        ty = table_front(p, 0.15, 0.04, 0.96)
        dye_pot(p.X(0.12), ty, 1.3)
        onion_skins(p.X(0.22), ty + 2, 1.0)
        candle(p.X(0.36), ty, 1.2)
        for k, kind in enumerate(("onion", "wax", "marker", "opicka", "star", "stripes")):
            kraslice(p.X(0.3 + k*0.07) + (12 if k > 1 else 0), ty + 9, 1.4, (k*13) % 30 - 15, kind)
        egg_basket(p.X(0.82), ty, 1.0, 6)
        for k, g in enumerate((P.CRAYON_RED, P.CRAYON_BLUE, P.KRASLICE_GREEN)): fixa(p.X(0.62) + k*14, ty + 3, 1.2, 20 + k*10, g)
        cap(p, "Bílá sobota. Barví se!", w=150, where="tl")
        say(p, "Já barvím v cibulových slupkách.", *hb(p.X(0.12), fy, 1.0), w=130, area=(0.0, 0.35))
        say(p, "Já kreslím voskem.", *hm(p.X(0.33), fy, 1.0), w=100, area=(0.22, 0.5))
        say(p, "A my fixama!", *hh(p.X(0.52), fy, 1.15), w=90, area=(0.42, 0.7))
        say(p, "Tohle měl být zajíc…", *ht(p.X(0.87), fy, 0.95), w=110, area=(0.7, 1.0))
    with Pn(*R[1]) as p:
        fy = kitchen(p, table=False)
        hanka(p.X(0.3), fy, 1.3, mood="grin", right="up", look=(1, 0.3),
              item=lambda x, y: kraslice(x, y + 8, 1.4, 0, "opicka"))
        say(p, "Na mojí je opička!", *hh(p.X(0.3), fy, 1.3), w=100, area=(0.4, 1.0))
    with Pn(*R[2]) as p:
        fy = kitchen(p, table=False)
        alica(p.X(0.3), fy, 1.2, mood="grin", right="up", look=(1, 0.3),
              item=lambda x, y: kraslice(x, y + 8, 1.4, 0, "star"))
        say(p, "A na mojí hvězdička. Jako Klub Hvězdička!", *ha(p.X(0.3), fy, 1.2), w=130, area=(0.42, 1.0))
    page_end()


# =================================================================== 14 what hens do (full page)
def dust_bath(x, y):
    """a hen sunk in a dusty hollow, puffs of dust flying up"""
    shape(ell(x, y + 1, 26, 5, 30), P.MUD, LINE*0.6)
    slepice(x - 2, y - 2, 1.0, pose="sit", who=0)
    rd = random.Random(14)
    for _ in range(9):
        px, py = x + rd.uniform(-26, 26), y + rd.uniform(6, 26)
        if abs(px - x) > 12 or py > y + 22:
            shape(ell(px, py, rd.uniform(2, 3.6), rd.uniform(1.8, 3), 14), 0.88, LINE*0.4)


def grit(x, y):
    """a pecking hen, little pebbles and grains in front of her beak"""
    slepice(x - 8, y, 1.0, pose="peck", who=1)
    rd = random.Random(15)
    for _ in range(6):
        shape(ell(x + 14 + rd.uniform(-5, 9), y + rd.uniform(0.5, 3), 1.6, 1.2, 10), 0.6, LINE*0.4)
    for _ in range(7):
        dot(x + 12 + rd.uniform(-4, 12), y + rd.uniform(0.5, 4), 0.9, P.STRAW_DARK)


def roost(x, y):
    """two hens asleep up on a perch, and the moon"""
    form([(x - 32, y + 10), (x + 32, y + 10), (x + 32, y + 14), (x - 32, y + 14)], P.BED, w=LINE*0.8, sh=0)
    for lx in (x - 26, x + 26): stroke([(lx, y + 10), (lx, y - 8)], LINE*1.4, g=P.BED)
    for k, hx in enumerate((x - 12, x + 12)):
        slepice(hx, y + 12, 0.8, pose="sit", who=k*2)
    moon(x + 30, y + 40, 6)


def moon(x, y, r):
    shape(ell(x, y, r, r, 20), P.KRASLICE_YELLOW, LINE*0.6)
    fill(ell(x + r*0.55, y + r*0.2, r*0.85, r*0.85, 20), 0.97)


def scratch(x, y):
    """a hen scratching the ground, a little worm wriggling out"""
    slepice(x - 6, y, 1.0, pose="stand", who=2)
    for k in range(3): stroke([(x - 18 + k*3, y + 0.5), (x - 24 + k*3, y - 1)], LINE*0.5)
    stroke(bez((x + 14, y + 0.5), (x + 17, y + 5), (x + 20, y - 1), (x + 24, y + 3)), LINE*1.8, g=0.0, taper=False)
    stroke(bez((x + 14, y + 0.5), (x + 17, y + 5), (x + 20, y - 1), (x + 24, y + 3)), LINE*1.1, g=P.HEN_COMB, taper=False)


def sunbath(x, y):
    """a hen sitting in the sun"""
    slepice(x - 6, y, 1.1, pose="sit", who=1)
    sx, sy = x + 24, y + 34
    for k in range(10):
        a = math.tau*k/10
        stroke([(sx + math.cos(a)*9, sy + math.sin(a)*9), (sx + math.cos(a)*13, sy + math.sin(a)*13)], LINE*0.6)
    shape(ell(sx, sy, 7, 7, 24), P.KRASLICE_YELLOW, LINE*0.6)


def dino_prints(x, y):
    """a hen's print beside a dinosaur's: the same three toes"""
    with T(x - 24, y + 4, 1.0):
        for a in (-38, 0, 38):
            ra = math.radians(90 + a)
            stroke([(0, 0), (math.cos(ra)*8, math.sin(ra)*8)], LINE*1.6, g=0.15)
        stroke([(0, 0), (0, -3)], LINE*1.4, g=0.15)
    with T(x + 10, y - 10, 1.0):
        shape(ell(0, 4, 7, 8, 20), P.MUD, LINE*0.7)
        for a in (-34, 0, 34):
            ra = math.radians(90 + a)
            toe = [(math.cos(ra)*r + math.cos(ra + math.pi/2)*w, math.sin(ra)*r + 4 + math.sin(ra + math.pi/2)*w)
                   for r, w in ((6, -3.2), (24, -1.8), (29, 0), (24, 1.8), (6, 3.2))]
            shape(toe, P.MUD, LINE*0.7)


def page_henfacts():
    with Pn(M, 40, W-2*M, H-80, bg=0.97) as p:
        hand_text(p.X(0.04), p.Y(0.955), p.w*0.92, "Co dělají slepice?", "SHB", 28)
        hand_text(p.X(0.04), p.Y(0.915), p.w*0.92, "Co nám řekla babička. Ukaž prstem na obrázek!", "SH", 13)
        items = [
            ("Koupe se v prachu. Tak si čistí peří.", dust_bath),
            ("Nemá zuby. Spolkne kamínky a ty jí v bříšku melou zrní.", grit),
            ("Spí na bidýlku. Prsty se jí samy chytí.", roost),
            ("Hrab, hrab, krok zpátky… Není tu žížala?", scratch),
            ("Ráda se vyhřívá na sluníčku.", sunbath),
            ("Je příbuzná dinosaurů! Stopy mají skoro stejné.", dino_prints),
        ]
        cw, ch = p.w*0.45, p.h*0.25
        for i, (txt, pic) in enumerate(items):
            cx = p.X(0.04) + (i % 2)*(cw + p.w*0.02); cy = p.Y(0.88) - (i//2 + 1)*(ch + 12)
            shape(rrect(cx, cy, cw, ch, 10), 1.0, 1.2)
            hand_text(cx + 8, cy + ch - 22, 30, str(i + 1), "SHB", 16, align="left")
            with T(cx + cw/2, cy + ch*0.36, 2.0):
                pic(0, 0)
            hand_text(cx + 10, cy + 26, cw - 20, txt, "SH", 13, lead=15)
        hand_text(p.X(0.05), p.Y(0.03), p.w*0.9, "Slepice si povídají. Umí přes dvacet různých zvuků!", "SHB", 14)
    page_end()


# =================================================================== 15 Saturday evening: Kropenatka is missing
def page_missing():
    R = rows([(270, [1]), (200, [0.5, 0.5]), (280, [1])])
    with Pn(*R[0]) as p:
        gy = dvur(p, 0.43, 151, henhouse_x=0.62, henhouse_s=1.6, clouds=False, evening=True)
        for k in range(6): slepice(p.X(0.47) + k*9, gy - 8, 0.55, who=k)
        babicka(p.X(0.25), p.Y(0.03), 1.0, mood="worried", right="point", look=(1, 0.3))
        hanka(p.X(0.85), p.Y(0.03), 1.15, flip=True, mood="worried", look=(-1, 0))
        cap(p, "Sobota večer. Slepičky jdou spát.", w=170, where="tl")
        say(p, "Pět, šest, sedm… Kde je Kropenatka?", *hb(p.X(0.25), p.Y(0.03), 1.0), w=140, area=(0.0, 0.48))
    with Pn(*R[1]) as p:
        bg_fill(p, P.WINTER_NIGHT)
        hanka(p.X(0.3), p.Y(0.03), 1.4, mood="worried", right="hug", look=(1, 0))
        say(p, "Kropenatka se ztratila!", *hh(p.X(0.3), p.Y(0.03), 1.4), w=110, area=(0.45, 1.0))
    with Pn(*R[2]) as p:
        bg_fill(p, P.WINTER_NIGHT)
        tata(p.X(0.25), p.Y(0.03), 1.0, mood="worried", right="front", look=(1, -0.3), item=lambda x, y: torch(x, y, -30))
        torch_beam(p.X(0.25) + 30, p.Y(0.58), p.X(0.7), p.Y(0.02), p.X(0.98), p.Y(0.3), 0.35)
        cap(p, "Všichni hledají s baterkami.", w=150, where="tl")
    with Pn(*R[3]) as p:
        gy = dvur(p, 0.49, 152, barn_x=0.85, barn_s=0.9, clouds=False)
        run_fence(p.X(0.0), p.X(0.42), p.Y(0.18), 56, p.X(0.32), 38)
        pirko(p.X(0.36), p.Y(0.13), 1.4, -60)
        hen_trail([(p.X(0.34), p.Y(0.1)), (p.X(0.5), p.Y(0.13)), (p.X(0.68), p.Y(0.2))], 6, 1.2)
        alica(p.X(0.18), p.Y(0.03), 1.0, mood="wow", right="lens", lens=True, look=(1, -0.3))
        deda(p.X(0.55), p.Y(0.03), 0.9, mood="happy", right="front", look=(-1, -0.2),
             item=lambda x, y: lantern(x, y - 8, 0.6, glow=True))
        J(p, p.X(0.72), p.Y(0.03), 1.0, mood="bark")
        sfx(p.X(0.78), p.Y(0.5), "HAF!", 16, 6)
        bg_fill(p, P.WINTER_NIGHT, 0.35)
        lantern_glow(p.X(0.55) + 8, p.Y(0.35), 90)
        kr(p.X(0.04), p.Y(0.06), -20)
        say(p, "Dírka pod pletivem! A pírko s tečkami!", *ha(p.X(0.18), p.Y(0.03), 1.0), w=140, area=(0.0, 0.42))
        say(p, "Tudy chodí slepice na zahradu. A Joey, stodola je zamčená.", *hdd(p.X(0.55), p.Y(0.03), 0.9), w=170,
            area=(0.35, 0.95))
    page_end()


# =================================================================== 16 night: Alica thinks
BED_LEN = 185   # a child's bed: a bit longer than Alica (s=1.3) is tall


def page_night():
    R = rows([(380, [1]), (360, [1])])
    with Pn(*R[0]) as p:
        fy = bedroom_night(p)
        ax, ay = kid_in_bed(alica, 45, p.X(0.06), p.X(0.06) + BED_LEN, fy + 40, 1.3, mood="think", look=(1, 0.5))
        thought(p.X(0.5), p.Y(0.95), p.w*0.47, p.h*0.62, ax + 14, ay + 115*1.3, seed=4)
        keep_clear(p, p.X(0.5), p.Y(0.33), p.X(0.97), p.Y(0.95), "thought")
        pirko(p.X(0.6), p.Y(0.62), 2.6, -20)
        hay_wisp(p.X(0.74), p.Y(0.84), 3.0, 10)
        hen_print(p.X(0.88), p.Y(0.72), 3.0, 10)
        kropenatka(p.X(0.68), p.Y(0.4), 2.4, puff=True)
        egg(p.X(0.86), p.Y(0.5), 3.0)
        hand_text(p.X(0.86) - 20, p.Y(0.5) - 12, 40, "?", "SHB", 26)
        cap(p, "Alica nemůže usnout.", w=150, where="tl")
    with Pn(*R[1]) as p:
        fy = bedroom_night(p)
        ax, ay = kid_in_bed(alica, 45, p.X(0.93) - BED_LEN, p.X(0.93), fy + 40, 1.3, mood="sleepy")
        sfx(p.X(0.66), p.Y(0.42), "CHRRR…", 18, -4)
        cap(p, "Pírko, sláma, dírka pod plotem… Kde spí Kropenatka? A kde jsou vajíčka?", w=260, where="tl")
        zzz(p.X(0.82), p.Y(0.72), 1.4)
    page_end()


# =================================================================== 17 Easter Sunday: the search
def page_sunday():
    R = rows([(290, [1]), (220, [0.5, 0.5]), (240, [1])])
    with Pn(*R[0]) as p:
        gy = dvur(p, 0.42, 171, house_x=0.2, house_s=1.0, henhouse_x=0.5, barn_x=0.85, barn_s=0.9, bushes=((0.66, 0.8),))
        babicka(p.X(0.08), p.Y(0.03), 0.9, mood="worried", right="wave", look=(1, 0))
        mama(p.X(0.3), p.Y(0.03), 0.95, outfit="home", mood="think", right="chin", look=(1, -0.3))
        tata(p.X(0.5), p.Y(0.03), 0.92, flip=True, mood="think", look=(-1, -0.3))
        deda(p.X(0.72), p.Y(0.03), 0.9, flip=True, mood="happy", right="point", look=(1, 0))
        cap(p, "Velikonoční neděle. Kropenatka nepřišla ani na snídani.", w=230, where="tr")
        say(p, "Puťa puťa puťa!", *hb(p.X(0.08), p.Y(0.03), 0.9), w=100, area=(0.0, 0.3))
    with Pn(*R[1]) as p:
        gy = dvur(p, 0.44, 172, barn_x=0.66, barn_s=1.0, barn_kw=dict(door_open=True), clouds=False)
        deda(p.X(0.2), p.Y(0.03), 0.95, mood="happy", right="up", look=(1, 0),
             item=lambda x, y: key(x + 2, y, 0.5, tag=False))
        say(p, "Odemknu stodolu. Ale tam je jen sláma.", *hdd(p.X(0.2), p.Y(0.03), 0.95), w=140, area=(0.0, 0.6))
    with Pn(*R[2]) as p:
        gy = dvur(p, 0.44, 173, clouds=False)
        hanka(p.X(0.25), p.Y(0.03), 1.25, mood="grin", right="front", look=(1, 0), item=lambda x, y: torch(x, y, 10))
        say(p, "Můžu si tam hrát na schovávanou? S opičkou?", *hh(p.X(0.25), p.Y(0.03), 1.25), w=118, area=(0.38, 1.0))
    with Pn(*R[3]) as p:
        gy = dvur(p, 0.49, 174, barn_x=0.62, barn_s=1.2, barn_kw=dict(door_open=True))
        deda(p.X(0.14), p.Y(0.03), 0.95, mood="grin", look=(1, 0))
        hanka(p.X(0.55), p.Y(0.03), 1.1, mood="happy", look=(1, 0), legs="walk")
        J(p, p.X(0.78), p.Y(0.03), 1.0, mood="happy", pose="sniff")
        kr(p.X(0.96), p.Y(0.06), 10)
        say(p, "Jasně, Hani. Ale nelez moc vysoko!", *hdd(p.X(0.14), p.Y(0.03), 0.95), w=140, area=(0.0, 0.45))
    page_end()


# =================================================================== 18 in the barn
def page_barn():
    R = rows([(320, [1]), (200, [0.5, 0.5]), (230, [1])])
    with Pn(*R[0]) as p:
        fy, gx, gyy = barn_inside(p, 0.08, 0.6, dark=0.25)
        hanka(p.X(0.18), fy, 1.2, monkey=False, mood="whisper", right="front", look=(1, 0),
              item=lambda x, y: torch(x, y, 10))
        monkey(p.X(0.36), fy + 4, 1.1)
        J(p, gx - 40, fy, 1.0, pose="sniff", mood="happy")
        say(p, "Opičko, schovej se tady. Raz, dva, tři…", *hh(p.X(0.18), fy, 1.2), w=140, area=(0.0, 0.45), whisper=True)
    with Pn(*R[1]) as p:
        fy, gx, gyy = barn_inside(p, 0.08, 0.5, light=False, dark=0.5)
        sfx(p.X(0.08), p.Y(0.72), "KVOK… KVOK…", 15, -4)
    with Pn(*R[2]) as p:
        fy, gx, gyy = barn_inside(p, 0.08, 0.85, light=False, dark=0.45)
        hanka(p.X(0.3), fy, 1.35, monkey=False, mood="surprised", look=(1, 0))
        say(p, "Kdo to tam kvoká?", *hh(p.X(0.3), fy, 1.35), w=100, area=(0.45, 1.0), whisper=True)
    with Pn(*R[3]) as p:
        fy, gx, gyy = barn_inside(p, 0.08, 0.75, light=False, dark=0.45)
        hanka(p.X(0.4), fy, 1.2, monkey=False, mood="determined", right="front", look=(1, -0.3), item=lambda x, y: torch(x, y, -15))
        sfx(p.X(0.12), p.Y(0.7), "CVAK!", 18, -6)
        J(p, p.X(0.62), fy, 1.0, mood="bark")
        sfx(p.X(0.86), p.Y(0.72), "HAF!", 14, 6)
    page_end()


# =================================================================== 19 STOP, DETEKTIVE!
def page_stop():
    with Pn(M, 40, W-2*M, H-80, bg=0.95) as p:
        title(p.X(0.5), p.Y(0.92), "STOP, DETEKTIVE!", 44)
        hand_text(p.X(0.05), p.Y(0.86), p.w*0.9, "Kde jsou vajíčka? A kde je Kropenatka?", "SHB", 18)
        cw, ch = p.w*0.3, p.h*0.2
        items = [
            ("každý den chybí jedno vajíčko (strana 5)", lambda x, y: (egg(x - 12, y + 26, 1.6), egg(x + 12, y + 26, 1.6))),
            ("nikde žádné skořápky (strana 7)", lambda x, y: egg_cracked(x, y + 20, 2.0, chick=False)),
            ("Kropenatka je načepýřená a kvoká (strana 11)", lambda x, y: kropenatka(x, y + 6, 1.3, puff=True)),
            ("sláma v peří, v kurníku jsou hobliny (strana 11)", lambda x, y: (hay_wisp(x - 14, y + 26, 2.6), hobliny(x + 16, y + 20, 1.6, 3, 2))),
            ("dírka pod pletivem, pírko a stopy (strana 15)", lambda x, y: (pirko(x - 12, y + 8, 1.4, -30), hen_print(x + 16, y + 20, 2.0))),
            ("ve stodole něco kvoká (strana 18)", lambda x, y: stodola(x, y + 4, 0.3)),
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
        for i, (fn, lbl) in enumerate(((lambda x, y: straci_hnizdo(x, y + 10, 1.2), "u straky na stromě"),
                                       (lambda x, y: egg_basket(x, y, 1.2, 9), "v Tondově košíku"),
                                       (lambda x, y: (balik(x - 40, y, 44, 26, 1), balik(x + 4, y, 44, 26, 2)), "mezi balíky slámy"))):
            fx = p.X(0.2 + i*0.3)
            fn(fx, by + 34)
            hand_text(fx - 60, by + 8, 120, lbl, "SHB", 12)
        hand_text(p.X(0.05), by - 30, p.w*0.9, "Ukaž prstem! Proč je Kropenatka tak mrzutá?", "SH", 14)
        with T(p.X(0.5), p.Y(0.03), 1.0, rot=180):
            hand_text(-p.w*0.45, 0, p.w*0.9, "Ve stodole mezi balíky! Kropenatka tam chodila dírkou pod pletivem a každý den tam snesla", "SH", 12)
            hand_text(-p.w*0.45, -15, p.w*0.9, "vajíčko. Proto měla v peří slámu. A je mrzutá, protože chce sedět na vajíčkách.", "SH", 12)
    page_end()


# =================================================================== 20 the torch
def page_torch():
    R = rows([(330, [1]), (200, [0.5, 0.5]), (220, [1])])
    with Pn(*R[0]) as p:
        fy, gx, gyy = barn_inside(p, 0.08, 0.72, light=False, dark=0.5)
        hanka(p.X(0.2), fy, 1.25, monkey=False, mood="wow", right="front", look=(1, -0.2), item=lambda x, y: torch(x, y, -12))
        torch_beam(p.X(0.2) + 26, fy + 64, gx - 4, fy + 4, gx + 12, fy + 50, 0.5)
        for ex in (-4, 5): shape(ell(gx + ex, fy + 22, 2.2, 2.2, 10), P.LANTERN_GLOW, LINE*0.5); dot(gx + ex, fy + 22, 0.9, 0.0)
        say(p, "Oči! Tam někdo je!", *hh(p.X(0.2), fy, 1.25), w=100, area=(0.0, 0.45))
    with Pn(*R[1]) as p:
        fy, gx, gyy = barn_inside(p, 0.08, 0.5, light=False, dark=0.4)
        hanka(gx - 36, fy, 1.0, monkey=False, mood="determined", look=(1, -0.3))
        say(p, "Já se tam vejdu!", *hh(gx - 36, fy, 1.0), w=100, area=(0.45, 1.0))
    with Pn(*R[2]) as p:
        bg_fill(p, P.BARN_DARK)
        torch_beam(p.x, p.Y(0.8), p.X(0.2), p.Y(0.0), p.X(1.0), p.Y(0.6), 0.45)
        nest(p.X(0.55), p.Y(0.18), 2.6)
        keep_clear(p, p.X(0.25), p.Y(0.15), p.X(0.85), p.Y(0.8), "nest")
        sfx(p.X(0.06), p.Y(0.85), "KVOK!", 16, -6)
    with Pn(*R[3]) as p:
        bg_fill(p, P.BARN_DARK)
        torch_beam(p.x, p.Y(0.9), p.X(0.4), p.Y(0.0), p.X(1.0), p.Y(0.7), 0.4)
        nest(p.X(0.62), p.Y(0.12), 2.3)
        hanka(p.X(0.18), p.Y(0.03), 1.3, monkey=False, mood="wow", right="point", look=(1, -0.2))
        say(p, "Kropenatko! Tady jsi!", *hh(p.X(0.18), p.Y(0.03), 1.3), w=110, area=(0.0, 0.4))
    page_end()


# =================================================================== 21 the nest
def page_nest():
    R = rows([(260, [1]), (220, [0.5, 0.5]), (270, [1])])
    with Pn(*R[0]) as p:
        gy = dvur(p, 0.47, 211, barn_x=0.55, barn_s=1.3, barn_kw=dict(door_open=True))
        hanka(p.X(0.52), p.Y(0.03), 1.1, mood="grin", right="up", look=(-1, 0))
        alica(p.X(0.12), p.Y(0.03), 1.05, mood="wow", look=(1, 0), legs="walk")
        babicka(p.X(0.28), p.Y(0.03), 0.95, mood="surprised", look=(1, 0), legs="walk")
        J(p, p.X(0.8), p.Y(0.03), 1.0, flip=True, mood="happy")
        say(p, "Pojďte sem! Kropenatka je tady! Sedí na vajíčkách!", *hh(p.X(0.52), p.Y(0.03), 1.1), w=170, area=(0.3, 0.95))
    with Pn(*R[1]) as p:
        fy, gx, gyy = barn_inside(p, 0.08, 0.35, dark=0.15)
        deda(p.X(0.6), fy, 0.95, flip=True, mood="determined", left="up", right="up", look=(-1, 0))
        sfx(p.X(0.08), p.Y(0.8), "HEJ RUP!", 16, -6)
    with Pn(*R[2]) as p:
        fy, gx, gyy = barn_inside(p, 0.08, 0.2, dark=0.1)
        nest(p.X(0.42), fy + 4, 1.4, hen_on=False)
        kropenatka(p.X(0.78), fy, 1.5, flip=True, puff=True)
        keep_clear(p, p.X(0.6), fy, p.X(0.95), fy + 50, "kropenatka")
        cap(p, "Pod Kropenatkou je…", w=130, where="tl")
    with Pn(*R[3]) as p:
        fy, gx, gyy = barn_inside(p, 0.08, 0.5, dark=0.1)
        nest(gx, fy + 4, 1.8, hen_on=False)
        babicka(p.X(0.14), fy, 1.0, mood="wow", right="point", look=(1, -0.3))
        alica(p.X(0.82), fy, 1.1, flip=True, mood="surprised", look=(-1, -0.3))
        kr(p.X(0.96), p.Y(0.86), -20)
        say(p, "Devět vajíček! Kropenatka je kvočna!", *hb(p.X(0.14), fy, 1.0), w=140, area=(0.0, 0.42))
        say(p, "Kvočna?", *ha(p.X(0.82), fy, 1.1), w=80, area=(0.66, 1.0))
        say(p, "Slepička, která chce mít kuřátka.", *hb(p.X(0.14), fy, 1.0), w=140, area=(0.0, 0.5))
    page_end()


# =================================================================== 22 the broody hen (full page)
def page_kvocna():
    with Pn(M, 40, W-2*M, H-80, bg=0.97) as p:
        hand_text(p.X(0.04), p.Y(0.955), p.w*0.92, "Kvočna", "SHB", 28)
        hand_text(p.X(0.04), p.Y(0.915), p.w*0.92, "Co vyprávěla babička. Ukaž prstem na obrázek!", "SH", 13)
        items = [
            ("Kvočna si najde tiché schované místo.", lambda x, y: (balik(x - 26, y - 10, 24, 16, 1), balik(x + 2, y - 10, 24, 16, 2),
                                                                     kropenatka(x - 4, y - 10, 0.7))),
            ("Každý den tam snese jedno vajíčko.", lambda x, y: nest(x, y - 6, 0.7, 5, hen_on=False)),
            ("Pak na nich sedí a hřeje je. Načepýří se a kvoká.", lambda x, y: nest(x, y - 8, 0.75)),
            ("Vajíčka obrací zobákem, aby byla teplá ze všech stran.", lambda x, y: (egg(x, y + 4, 1.6), turn_arrows(x, y + 4))),
            ("Asi za tři týdny se vyklubou kuřátka.", lambda x, y: (egg_cracked(x - 10, y + 2, 1.4), kure(x + 12, y - 6, 1.1))),
            ("Ale jen když je u slepic kohout!", lambda x, y: kohout(x, y - 12, 0.6)),
        ]
        cw, ch = p.w*0.45, p.h*0.25
        for i, (txt, pic) in enumerate(items):
            cx = p.X(0.04) + (i % 2)*(cw + p.w*0.02); cy = p.Y(0.88) - (i//2 + 1)*(ch + 12)
            shape(rrect(cx, cy, cw, ch, 10), 1.0, 1.2)
            hand_text(cx + 8, cy + ch - 22, 30, str(i + 1), "SHB", 16, align="left")
            with T(cx + cw/2, cy + ch*0.42, 2.2):
                pic(0, 0)
            hand_text(cx + 10, cy + 26, cw - 20, txt, "SH", 13, lead=15)
        hand_text(p.X(0.05), p.Y(0.03), p.w*0.9, "Kropenatka nebyla zloděj. Chtěla být maminka!", "SHB", 15)
    page_end()


def turn_arrows(x, y):
    for sgn in (1, -1):
        pts = [(x + math.cos(math.radians(a))*15, y + math.sin(math.radians(a))*13*sgn) for a in range(40, 141, 10)]
        stroke(pts, LINE*0.9)
        ex, ey = pts[-1]
        stroke([(ex + 1.5, ey + 3.5*sgn), (ex, ey), (ex + 4, ey - 0.5*sgn)], LINE*0.9)


# =================================================================== 23 no rooster
def page_rooster():
    R = rows([(270, [1]), (220, [0.5, 0.5]), (260, [1])])
    with Pn(*R[0]) as p:
        fy, gx, gyy = barn_inside(p, 0.08, 0.85, dark=0.1)
        hanka(p.X(0.12), fy, 1.15, mood="grin", right="hug", look=(1, 0))
        babicka(p.X(0.5), fy, 1.0, flip=True, mood="worried", right="chin", look=(-1, 0))
        nest(gx, fy + 4, 1.2)
        say(p, "Babi, budou kuřátka?", *hh(p.X(0.12), fy, 1.15), w=100, area=(0.0, 0.3))
        say(p, "Ach, Hani. My nemáme kohouta. Bez kohouta z vajíček kuřátka nebudou.", *hb(p.X(0.5), fy, 1.0), w=190,
            area=(0.25, 0.8))
    with Pn(*R[1]) as p:
        fy, gx, gyy = barn_inside(p, 0.08, 0.9, light=False, dark=0.2)
        hanka(p.X(0.4), fy, 1.4, mood="sad", right="hug", look=(0.3, -0.3))
        cap(p, "Hanka je smutná. Kropenatka taky.", w=170, where="tl")
    with Pn(*R[2]) as p:
        fy, gx, gyy = barn_inside(p, 0.08, 0.9, light=False, dark=0.15)
        alica(p.X(0.28), fy, 1.25, mood="wow", right="up", look=(1, 0))
        say(p, "Já vím! Paní Věrka má na mlýně kohouta!", *ha(p.X(0.28), fy, 1.2), w=118, area=(0.4, 1.0))
    with Pn(*R[3]) as p:
        gy = dvur(p, 0.43, 231, house_x=0.82, house_s=0.8)
        babicka(p.X(0.14), p.Y(0.03), 1.0, mood="grin", right="front", look=(1, 0))
        deda(p.X(0.36), p.Y(0.03), 0.95, mood="grin", look=(1, 0))
        alica(p.X(0.62), p.Y(0.03), 1.05, flip=True, mood="grin", look=(-1, 0))
        say(p, "Zítra je pondělí. Půjdete na koledu…", *hb(p.X(0.14), p.Y(0.03), 1.0), w=140, area=(0.0, 0.35))
        say(p, "…až k mlýnu!", *hdd(p.X(0.36), p.Y(0.03), 0.95), w=90, area=(0.3, 0.6))
    page_end()


# =================================================================== 24 Easter Monday: koleda to the mill
def page_koleda():
    R = rows([(330, [1]), (190, [0.5, 0.5]), (230, [1])])
    with Pn(*R[0]) as p:
        gy = dvur(p, 0.4, 241, house_x=0.15, house_s=0.8, trees=((0.9, 1.0),), bushes=((0.36, 0.9),))
        mill(p.X(0.72), gy - 4, 0.75)
        alica(p.X(0.14), p.Y(0.03), 1.05, mood="grin", right="front", look=(1, 0), legs="walk",
              item=lambda x, y: basket(x + 2, y - 14))
        hanka(p.X(0.3), p.Y(0.03), 1.1, mood="grin", look=(1, 0), legs="walk")
        tonda(p.X(0.48), p.Y(0.03), 1.0, mood="grin", right="up", look=(1, 0), legs="walk")
        betka(p.X(0.64), p.Y(0.03), 1.2, hat=False, mood="grin", look=(1, 0), legs="walk")
        cap(p, "Velikonoční pondělí. Děti chodí po vsi koledovat. Za básničku dostanou sladkosti.", w=260, where="tr")
        say(p, "Hody, hody, doprovody, dejte vejce malovaný!", *ha(p.X(0.14), p.Y(0.03), 1.05), w=150, area=(0.0, 0.42))
        say(p, "Nedáte-li malovaný, dejte aspoň bonbóny!", *htd(p.X(0.48), p.Y(0.03), 1.0), w=150, area=(0.3, 0.8))
    with Pn(*R[1]) as p:
        gy = dvur(p, 0.29, 242, clouds=False)
        fence(p.x, p.x + p.w, gy - 6, 30)
        kohout(p.X(0.5), gy + 26, 2.3, crow=True)
        sfx(p.X(0.06), p.Y(0.85), "KIKIRIKÍÍ!", 16, -5)
    with Pn(*R[2]) as p:
        gy = dvur(p, 0.42, 243, clouds=False)
        verka_old(p.X(0.25), p.Y(0.03), 0.85, mood="happy", right="front", look=(1, 0),
                  item=lambda x, y: candy_wrapper(x + 4, y, 1.2))
        say(p, "Koledníci! Tady máte bonbony. To je Pepík.", *hv(p.X(0.25), p.Y(0.03), 0.85), w=115, area=(0.38, 1.0))
    with Pn(*R[3]) as p:
        gy = dvur(p, 0.43, 244, clouds=False)
        mill(p.X(0.86), gy - 4, 0.5)
        alica(p.X(0.12), p.Y(0.03), 0.95, mood="determined", right="up", look=(1, 0))
        verka_old(p.X(0.58), p.Y(0.03), 0.92, flip=True, mood="grin", right="front", look=(-1, 0),
                  item=lambda x, y: egg_basket(x - 4, y - 18, 0.7, 9))
        say(p, "Potřebujeme vajíčka pro Kropenatku. Od slepic s kohoutem!", *ha(p.X(0.12), p.Y(0.03), 0.95),
            w=170, area=(0.0, 0.5))
        say(p, "To máte štěstí. Tady jsou ta nejlepší.", *hv(p.X(0.58), p.Y(0.03), 0.92), w=140, area=(0.45, 1.0))
    page_end()


# =================================================================== 25 the swap
def page_swap():
    R = rows([(280, [1]), (230, [0.5, 0.5]), (240, [1])])
    with Pn(*R[0]) as p:
        fy, gx, gyy = barn_inside(p, 0.08, 0.45, dark=0.1)
        nest(gx, fy + 4, 1.3, hen_on=False)
        babicka(p.X(0.14), fy, 0.95, mood="happy", right="front", look=(1, -0.3),
                item=lambda x, y: egg_basket(x + 4, y - 18, 0.7, 9))
        verka_old(p.X(0.78), fy, 0.92, flip=True, mood="happy", right="front", look=(-1, -0.3),
                  item=lambda x, y: egg(x - 2, y, 1.0))
        kropenatka(p.X(0.58), fy, 1.2, flip=True, puff=True)
        say(p, "Naše vajíčka si vezmu na kraslice.", *hb(p.X(0.14), fy, 0.95), w=130, area=(0.0, 0.4))
        say(p, "A tyhle od Pepíkových slepic dáme Kropence.", *hv(p.X(0.78), fy, 0.92), w=150, area=(0.5, 1.0))
    with Pn(*R[1]) as p:
        bg_fill(p, P.BARN_DARK)
        torch_beam(p.x, p.Y(0.9), p.X(0.2), p.Y(0.0), p.X(1.0), p.Y(0.7), 0.4)
        nest(p.X(0.5), p.Y(0.15), 2.3)
        keep_clear(p, p.X(0.2), p.Y(0.15), p.X(0.8), p.Y(0.75), "nest")
        cap(p, "Kropenatka si sedla a spokojeně zakvokala.", w=180, where="tl")
    with Pn(*R[2]) as p:
        fy = kitchen(p)
        hanka(p.X(0.25), fy, 1.2, mood="grin", right="up", look=(1, 0.3),
              item=lambda x, y: kraslice(x, y + 8, 1.3, 0, "opicka"))
        ty = table_front(p, 0.22, 0.5, 0.98)
        for k, kind in enumerate(("onion", "wax", "marker", "stripes", "star")):
            kraslice(p.X(0.56 + k*0.085), ty + 9, 1.2, (k*11) % 24 - 12, kind)
        say(p, "Devět kraslic od Kropenatky!", *hh(p.X(0.25), fy, 1.2), w=110, area=(0.4, 1.0))
    with Pn(*R[3]) as p:
        gy = dvur(p, 0.45, 251, barn_x=0.75, barn_s=1.0)
        J(p, p.X(0.45), p.Y(0.03), 1.3, mood="happy")
        alica(p.X(0.14), p.Y(0.03), 1.1, mood="grin", right="front", look=(1, -0.3))
        kr(p.X(0.95), p.Y(0.06), 30)
        say(p, "Joey, ty jsi to věděl od začátku! Pořád jsi táhl ke stodole.", *ha(p.X(0.14), p.Y(0.03), 1.1), w=170, area=(0.0, 0.62))
    page_end()


# =================================================================== 26 three weeks later
def page_chicks():
    R = rows([(390, [1]), (350, [0.5, 0.5])])
    with Pn(*R[0]) as p:
        gy = dvur(p, 0.4, 261, henhouse_x=0.85, henhouse_s=1.1, trees=((0.1, 1.0),), bushes=((0.62, 0.9),))
        kropenatka(p.X(0.5), p.Y(0.06), 1.8)
        r = random.Random(4)
        for k, (fx, fy_) in enumerate(((0.36, 0.04), (0.41, 0.09), (0.57, 0.05), (0.62, 0.1), (0.66, 0.03), (0.44, 0.02),
                                       (0.31, 0.1), (0.7, 0.07))):
            kure(p.X(fx), p.Y(fy_), 1.6, flip=k % 2 == 0, pose="peck" if k % 3 == 0 else "stand")
        hanka(p.X(0.14), p.Y(0.03), 1.2, mood="wow", right="hug", look=(1, -0.2))
        alica(p.X(0.88), p.Y(0.03), 1.1, flip=True, mood="grin", look=(-1, -0.2))
        sfx(p.X(0.4), p.Y(0.42), "PÍP PÍP PÍP!", 16, 4)
        cap(p, "O tři týdny později…", w=150, where="tl")
        say(p, "Kuřátka!", *hh(p.X(0.14), p.Y(0.03), 1.2), w=80, area=(0.0, 0.3))
        say(p, "Jedno, dvě, tři… osm kuřátek!", *ha(p.X(0.88), p.Y(0.03), 1.1), w=120, area=(0.65, 1.0))
    with Pn(*R[1]) as p:
        fy = kitchen(p, evening=True)
        mama(p.X(0.25), fy, 0.95, outfit="home", mood="whisper", right="hush", look=(1, 0))
        babicka(p.X(0.48), fy, 0.95, flip=True, mood="grin", right="front", look=(-1, 0),
                item=lambda x, y: (shape(rrect(x - 12, y - 8, 24, 16, 2), 1.0, LINE*0.6), arrow_chalk(x, y, 0.5)))
        say(p, "…a šipky dáme až ke…", *hm(p.X(0.25), fy, 0.95), w=110, area=(0.0, 0.5), whisper=True)
    with Pn(*R[2]) as p:
        fy = kitchen(p, evening=True)
        alica(p.X(0.25), fy, 1.15, mood="think", right="chin", look=(1, 0))
        cap(p, "Případ č. 11 vyřešen. Ale máma s babičkou si něco šeptají…", w=190, where="tr")
        say(p, "Co si to šeptáte?", *ha(p.X(0.25), fy, 1.15), w=100, area=(0.0, 0.5))
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
        prints = [lambda x, y: dog_print(x, y, 3.4), lambda x, y: hen_print(x, y, 3.0),
                  lambda x, y: kid_print(x, y, 1.5, 0), lambda x, y: fox_print(x, y, 3.4)]
        whos = [lambda x, y: liska(x - 4, y, 0.8, shadow=False), lambda x, y: hanka(x, y, 0.6, shadow=False, mood="happy"),
                lambda x, y: joey(x - 6, y, 1.0, shadow=False, collar=False), lambda x, y: kropenatka(x, y, 2.0)]
        y1 = p.Y(0.72)
        for i in range(4):
            prints[i](p.X(0.14 + i*0.24), y1)
            hand_text(p.X(0.14 + i*0.24) - 30, y1 - 34, 60, "ABCD"[i], "SHB", 14)
            whos[i](p.X(0.14 + i*0.24), y1 - 110)
            hand_text(p.X(0.14 + i*0.24) - 30, y1 - 128, 60, str(i + 1), "SHB", 14)
        y2 = y1 - 150
        hand_text(p.X(0.05), y2, p.w*0.9, "2. Které dvě kraslice jsou úplně stejné?", "SHB", 15, align="left")
        for i, kind in enumerate(("wax", "marker", "star", "marker", "onion", "stripes")):
            kraslice(p.X(0.14 + i*0.145), y2 - 46, 2.6, 0, kind)
            hand_text(p.X(0.14 + i*0.145) - 20, y2 - 92, 40, str(i + 1), "SHB", 13)
        y3 = y2 - 118
        hand_text(p.X(0.05), y3, p.w*0.9, "3. Povídejte si:", "SHB", 15, align="left")
        qs = ["Proč Kropenatka schovávala vajíčka?", "Proč nebyly nikde skořápky?",
              "Proč měla Kropenatka v peří slámu?", "Proč musela paní Věrka přinést vajíčka od Pepíka?"]
        for i, q in enumerate(qs):
            hand_text(p.X(0.1), y3 - 22 - i*20, p.w*0.85, "– " + q, "SH", 14, align="left")
        y4 = y3 - 22 - len(qs)*20 - 16
        hidden_kraslice(p.X(0.09), y4 - 2, 13, -10, "marker")          # the legend: not one of the hidden ten
        hand_text(p.X(0.15), y4 - 4, p.w*0.8,
                  f"Zajíček schoval {N_HIDDEN} kraslic, jako je tahle (ta se nepočítá). Najdeš je všechny?",
                  "SHB", 14, align="left", lead=18)
        pages = ", ".join(map(str, HID[:-1])) + " a " + str(HID[-1]) if HID else ""
        with T(p.X(0.5), p.Y(0.015), 1.0, rot=180):
            hand_text(-p.w*0.45, 0, p.w*0.9, f"Kraslice jsou na stranách {pages}.", "SH", 10)
            hand_text(-p.w*0.45, -13, p.w*0.9, "Stopy: A3 (Joey), B4 (Kropenatka), C2 (Hanka), D1 (liška). Stejné kraslice: 2 a 4.", "SH", 10)
    page_end()


# =================================================================== 28 back cover: next time
def back_cover():
    with Pn(M, 40, W-2*M, H-80, bg=0.95) as p:
        hand_text(p.X(0.1), p.Y(0.93), p.w*0.8, "Příště v sešitě č. 12:", "SHB", 20)
        title(p.X(0.5), p.Y(0.84), "TAJEMNÉ ŠIPKY", 36)
        with Pn(p.X(0.08), p.Y(0.3), p.w*0.84, p.h*0.48, bg=0.9) as q:
            gy = dvur(q, 0.35, 281, trees=((0.85, 1.1),), bushes=((0.08, 0.9),))
            fence(q.X(0.2), q.X(0.7), gy - 20, 34)
            for (fx, fy_, rot) in ((0.12, 0.12, 10), (0.32, 0.2, 5), (0.52, 0.16, -8), (0.7, 0.24, 20)):
                arrow_chalk(q.X(fx), q.Y(fy_), 1.5, rot)
            arrow_chalk(q.X(0.45), gy + 2, 1.0, 0)
            arrow_chalk(q.X(0.83), gy + 40, 1.0, 80)
            hand_text(q.X(0.86), q.Y(0.75), q.w*0.12, "?", "SHB", 34)
        hand_text(p.X(0.1), p.Y(0.24), p.w*0.8, "Alica bude mít narozeniny. Ale všichni se chovají nějak divně. A všude se objevují šipky!", "SH", 16, lead=21)
        hand_text(p.X(0.1), p.Y(0.13), p.w*0.8, "Kam vedou?", "SHB", 16)
        hand_text(p.X(0.1), p.Y(0.015), p.w*0.8, "Velká a malá detektivka – sešit č. 11", "SH", 13, g=0.35)
    PAGE[0] += 1; cv.showPage()


cover(); page_cast(); page_arrival(); page_henhouse(); page_count(); page_fox(); page_shells(); page_magpie()
page_treasure(); page_tonda(); page_kropenatka(); page_list(); page_dye(); page_henfacts(); page_missing(); page_night()
page_sunday(); page_barn(); page_stop(); page_torch(); page_nest(); page_kvocna(); page_rooster(); page_koleda()
page_swap(); page_chicks(); page_quiz(); back_cover()
cv.save()
print("ok", PAGE[0] - 1, "pages")
import letter
if letter.MISSING: PROBLEMS.append("no glyph in the font for: " + " ".join(sorted(letter.MISSING)))
if len(HID) != N_HIDDEN: PROBLEMS.append(f"{len(HID)} hidden kraslice drawn, the notebook promises {N_HIDDEN}")
for pr in PROBLEMS: print("ORDER/LAYOUT:", pr)
if PROBLEMS: sys.exit(1)
