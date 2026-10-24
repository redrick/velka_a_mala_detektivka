"""Velká a malá detektivka, issue 9: Tajná zpráva v knihovně (outline: vault topics/comic-series/issue9-outline)"""
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
from props_extra import mug, stream, dog_bed, flour_patch, old_sock
from attic import (young, chest, attic, bedroom, bed_side, blanket_side, bunting, shelf_toys, kids_drawing,
                   owlet, owl_box, old_photo, map_half, ladder, sled, tin)
from pond import *
from village import *
from letter import Panel, caption, bubble, sfx, title, series_title, hand_text, lines_of, thought
from winter import *
from interior import stove
from advent import *
from joeyday import *
from tracks import *
from masopust import *
import chars3

W, H = A4
M = 28; GUT = 9; TOP = H - 30
OUT = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                   "comics", "velka_a_mala_detektivka", "09_tajna_zprava_v_knihovne.pdf")
os.makedirs(os.path.dirname(OUT), exist_ok=True)
cv = canvas.Canvas(OUT, pagesize=A4); lib.set_canvas(cv)
cv.setTitle("Velká a malá detektivka – Případ č. 9: Tajná zpráva v knihovně")
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


def rays(p, cx, cy, g=0.9, n=18):
    for i in range(n):
        a = i*math.tau/n
        fill([(cx, cy), (cx+math.cos(a)*500, cy+math.sin(a)*500), (cx+math.cos(a+0.14)*500, cy+math.sin(a+0.14)*500)], g)


def garden(p, gy, seed=1, house_x=None, house_s=1.0, tree_x=None, tree_s=1.2, hills_=True, clouds=True):
    sky(p, 0.95)
    if clouds: cloud(p.X(0.55), p.Y(0.85), 0.8)
    if hills_: hills(p, gy + p.h*0.06, 16, 0.87, seed)
    ground(p, gy)
    if house_x is not None: house(p.X(house_x), gy-4, house_s)
    if tree_x is not None: tree(p.X(tree_x), gy-6, tree_s, seed=seed+3)


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
    bg_fill(p, 0.92)
    for yy in range(int(p.Y(0.35)), int(p.y+p.h), 16): stroke([(p.x, yy), (p.x+p.w, yy)], BG*0.4, g=0.7)
    for xx in range(int(p.x), int(p.x+p.w), 16): stroke([(xx, p.Y(0.35)), (xx, p.y+p.h)], BG*0.4, g=0.7)
    shelf(p.X(0.02), p.X(0.02)+120, p.Y(0.72))
    for i, g in enumerate((P.JAM, 0.75, P.JAM, 0.55)): jar(p.X(0.02)+22+i*22, p.Y(0.72)+5, 14 + (i % 2)*4, g)
    wall_clock(p.X(0.93), p.Y(0.8), 13)
    shape([(p.x, p.y), (p.x+p.w, p.y), (p.x+p.w, p.Y(0.35)), (p.x, p.Y(0.35))], 0.7, BG)
    if table:
        for k_ in range(1, 6): stroke([(p.x+p.w*k_/6, p.y), (p.x+p.w*k_/6, p.Y(0.35))], BG*0.6)
        shape([(p.X(0.03), p.Y(0.35)), (p.X(0.97), p.Y(0.35)), (p.X(0.97), p.Y(0.38)), (p.X(0.03), p.Y(0.38))], 0.5, BG)
    if evening:
        bg_fill(p, 0.0, 0.22)
        lx, ly = p.X(0.5), p.y + p.h
        fill([(lx, ly - 30), (lx - 160, p.Y(0.2)), (lx + 160, p.Y(0.2))], P.LANTERN_GLOW, 0.25)
        stroke([(lx, ly), (lx, ly - 22)], 1.0)
        shape(bez((lx - 18, ly - 34), (lx - 14, ly - 20), (lx + 14, ly - 20), (lx + 18, ly - 34)) + [(lx - 18, ly - 34)], 0.35, 1.0)


def head_y(p, frac, hy, s):
    return p.Y(frac) - hy*s


def board_fence(x0, x1, y, h=90):
    xx = x0
    while xx < x1:
        form([(xx, y), (xx + 17, y), (xx + 17, y + h), (xx + 8.5, y + h + 7), (xx, y + h)], P.FENCE_RAIL, w=BG, sdx=2, sdy=0, sh=0.08)
        xx += 18
    for yy in (y + h*0.25, y + h*0.7):
        sh_([(x0 - 2, yy), (x1 + 2, yy), (x1 + 2, yy + 5), (x0 - 2, yy + 5)], P.POST)


def pond_view(p, bank=0.3, far=0.6, seed=1, mill_at=None, mill_s=0.55, sign_at=None, sign_s=1.1, lantern_=False,
              sky_g=None, clouds_=True, posts=False):
    fy = pond_bg(p, bank, far, seed, clouds_=clouds_, sky_g=sky_g)
    if mill_at is not None:
        mill(p.X(mill_at), fy + 4, mill_s, lantern_=lantern_)
    if posts:
        for i, px in enumerate((0.42, 0.48, 0.54, 0.6)):
            yy = p.Y(bank) + 8 + (p.Y(far) - p.Y(bank))*0.25
            sh_([(p.X(px) - 3, yy - 4), (p.X(px) + 3, yy - 4), (p.X(px) + 3, yy + 10 + (i % 2)*5), (p.X(px) - 3, yy + 10 + (i % 2)*5)], P.BARK)
    if sign_at is not None:
        dredge_sign(p.X(sign_at), p.Y(0.02), sign_s)
    return fy


def keep_clear(p, x0, y0, x1, y1, what="picture"):
    p.heads.append(dict(txt=what, l=x0, r=x1, top=y1, b=y0))


def hand_pt(kid_young, pose, x, y, s, flip=False):
    from style3 import Kid, arm_pts
    _, _, hh, _ = arm_pts(Kid(kid_young), 1, pose)
    return x + (-hh[0] if flip else hh[0])*s, y + hh[1]*s


def sickroom(p, evening=False, window=True):
    """Alica's room at the chalupa; returns the floor line"""
    bg_fill(p, P.BEDROOM_WALL)
    for xx in range(int(p.x) + 12, int(p.x + p.w), 26): stroke([(xx, p.Y(0.3)), (xx, p.y + p.h)], 0.5, g=0.82)
    floor_y = p.y + 14
    shape([(p.x - 5, p.y - 5), (p.x + p.w + 5, p.y - 5), (p.x + p.w + 5, floor_y), (p.x - 5, floor_y)], P.FLOOR, BG)
    if window:
        x0, x1, y0, y1 = p.X(0.04), p.X(0.2), p.Y(0.52), p.Y(0.86)
        shape([(x0 - 4, y0 - 4), (x1 + 4, y0 - 4), (x1 + 4, y1 + 4), (x0 - 4, y1 + 4)], P.DOOR_FRAME, BG)
        shape([(x0, y0), (x1, y0), (x1, y1), (x0, y1)], 0.45 if evening else P.NOV_SKY, BG)
        stroke(bez((x0, y0 + 10), (x0 + (x1 - x0)*0.3, y0 + 22), (x0 + (x1 - x0)*0.5, y0 + 30), (x1, y0 + 44)), 1.6, g=P.BARK)
        stroke([(x0 + (x1 - x0)*0.5, y0 + 30), (x0 + (x1 - x0)*0.55, y1 - 6)], 0.9, g=P.BARK)
        s_([((x0 + x1)/2, y0), ((x0 + x1)/2, y1)], BG*1.6, g=1.0); s_([(x0, (y0 + y1)/2), (x1, (y0 + y1)/2)], BG*1.6, g=1.0)
    if evening:
        bg_fill(p, 0.0, 0.2)
    return floor_y


def alica_in_bed(x0, x1, top, s=1.2, **kw):
    """bed along the wall, head end on the right, Alica sitting up under the blanket.
    returns her figure origin (for hd)"""
    bed_side(x0, x1, top)
    ax = x1 - 30; waist = top + 8; ay = waist - 45*s
    C.saveState()
    C.clipPath(poly([(x0 - 80, top - 10), (x1 + 80, top - 10), (x1 + 80, top + 500), (x0 - 80, top + 500)]), stroke=0, fill=0)
    alica(ax, ay, s, shadow=False, **kw)
    C.restoreState()
    blanket_side(x0, ax + 14, top, waist + 4)
    return ax, ay


def autumn(p, gy, seed=1, house_x=None, house_s=1.0, trees=(), hills_=True, leaves=True):
    """the chalupa in November"""
    sky(p, P.NOV_SKY)
    if hills_: hills(p, gy + p.h*0.06, 16, 0.87, seed)
    ground(p, gy)
    if house_x is not None: house(p.X(house_x), gy - 4, house_s)
    for i, (tx, ts) in enumerate(trees):
        tree(p.X(tx), gy - 6, ts, seed=seed + i, g=(P.LEAF_DARK, P.LEAF_LIGHT)[i % 2])
    if leaves: falling_leaves(p, 4, seed)


def village(p, gy, church_x=None, church_s=1.0, houses=(), seed=1, hour=3):
    sky(p, P.NOV_SKY)
    hills(p, gy + p.h*0.08, 18, 0.87, seed)
    for hx, hs in houses: house(p.X(hx), gy - 2, hs, smoke=False)
    if church_x is not None: church(p.X(church_x), gy - 2, church_s, hour=hour)
    ground(p, gy, P.GRASS)


def countryside(p, horizon=0.55, seed=1, brook=None, dusk=False):
    """fields sloping to the forest edge; brook=(y0, y1) panel fractions draws a brook across"""
    sky(p, 0.62 if dusk else P.NOV_SKY)
    hy = p.Y(horizon)
    far_trees(p, hy + 4, seed)
    fill([(p.x - 5, p.y - 5), (p.x + p.w + 5, p.y - 5), (p.x + p.w + 5, hy), (p.x - 5, hy)], P.FIELD)
    s_([(p.x - 5, hy), (p.x + p.w + 5, hy)], BG)
    r = random.Random(seed)
    for k_ in range(5):
        yy = p.y + (hy - p.y)*(0.2 + k_*0.18) + r.uniform(-4, 4)
        s_(bez((p.x - 5, yy), (p.X(0.3), yy + 6), (p.X(0.7), yy - 6), (p.x + p.w + 5, yy + 2)), BG*0.5, g=P.FIELD_DARK)
    if brook:
        stream(p, p.Y(brook[0]), p.Y(brook[1]))
    if dusk:
        bg_fill(p, 0.0, 0.18)


def radio_say(p, txt, wx, wy, w=150, **kw):
    """Alica's voice from the walkie-talkie: the tail points at the walkie-talkie"""
    say(p, txt, wx, wy + 8, w=w, **kw)


def memory_frame(p):
    """soft frame for a recent memory (Věrka tells)"""
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




# =================================================================== issue 5 helpers
HEAD.update({"betka": (70.2, 9.6), "franta": (118, 11.2)})


def hd_h(who, x, y, s, up=2.1):
    """hd() for a figure in a winter hat: the tail stops above the hat, and the hat is kept clear too"""
    tip = hd(who, x, y, s, up)
    if CUR:
        hy, hr = HEAD[who]
        CUR[-1].heads[-1]["top"] = y + (hy + hr*2.0)*s
    return tip


def A(x, y, s, hat=True, **kw):
    alica(x, y, s, **kw)
    if hat: winter_hat(x, y, s, "alica", P.ALICA_WINTER_HAT, kw.get("flip", False))


def Hk(x, y, s, hat=True, **kw):
    hanka(x, y, s, **kw)
    if hat: winter_hat(x, y, s, "hanka", P.HANKA_WINTER_HAT, kw.get("flip", False))


def Td(x, y, s, hat=True, **kw):
    tonda(x, y, s, **kw)
    if hat: winter_hat(x, y, s, "tonda", P.TONDA_WINTER_HAT, kw.get("flip", False))


def franta(x, y, s, **kw):
    kw.setdefault("hat", False); kw.setdefault("glasses", True); kw.setdefault("rod", False)
    rybar(x, y, s, **kw)


def winter_garden(p, gy, seed=1, house_x=None, house_s=1.0, trees=(), night=False, hills_=True, flakes=0):
    sky(p, P.WINTER_NIGHT if night else P.SNOW_SKY)
    if night:
        r = random.Random(seed)
        for _ in range(14):
            dot(p.x + r.random()*p.w, p.Y(0.6) + r.random()*p.h*0.38, 0.9, 1.0)
    if hills_: hills(p, gy + p.h*0.06, 16, P.SNOW_HILL, seed)
    snow_field(p, gy, seed)
    if house_x is not None: snowy_house(p.X(house_x), gy - 4, house_s, smoke=not night)
    for i, (tx, ts) in enumerate(trees):
        bare_tree(p.X(tx), gy - 6, ts, seed=seed + i)
    if flakes: snowfall(p, flakes, seed)
    if night: bg_fill(p, 0.0, 0.18)


def bedroom_night(p, window=True):
    """the girls' room at the chalupa at night, window onto the snowy garden; returns the floor line"""
    bg_fill(p, P.BEDROOM_WALL)
    for xx in range(int(p.x) + 12, int(p.x + p.w), 26): stroke([(xx, p.Y(0.3)), (xx, p.y + p.h)], 0.5, g=0.82)
    floor_y = p.y + 14
    shape([(p.x - 5, p.y - 5), (p.x + p.w + 5, p.y - 5), (p.x + p.w + 5, floor_y), (p.x - 5, floor_y)], P.FLOOR, BG)
    if window:
        x0, x1, y0, y1 = p.X(0.62), p.X(0.9), p.Y(0.42), p.Y(0.9)
        shape([(x0 - 5, y0 - 5), (x1 + 5, y0 - 5), (x1 + 5, y1 + 5), (x0 - 5, y1 + 5)], P.DOOR_FRAME, BG)
        shape([(x0, y0), (x1, y0), (x1, y1), (x0, y1)], P.WINTER_NIGHT, BG)
        fill([(x0, y0), (x1, y0), (x1, y0 + (y1 - y0)*0.3), (x0, y0 + (y1 - y0)*0.34)], P.SNOW)
        r = random.Random(7)
        for _ in range(16):
            dot(x0 + r.random()*(x1 - x0), y0 + (y1 - y0)*(0.35 + r.random()*0.6), 1.1, 1.0)
        s_([((x0 + x1)/2, y0), ((x0 + x1)/2, y1)], BG*1.6, g=1.0); s_([(x0, (y0 + y1)/2), (x1, (y0 + y1)/2)], BG*1.6, g=1.0)
        shape([(x0 - 8, y0 - 5), (x1 + 8, y0 - 5), (x1 + 8, y0 - 1), (x0 - 8, y0 - 1)], P.SILL, BG)
    bg_fill(p, 0.0, 0.22)
    return floor_y


def kid_in_bed(fn, hip, x0, x1, top, s=1.2, **kw):
    """bed along the wall, head end on the right, a child sitting up under the blanket (like alica_in_bed)"""
    bed_side(x0, x1, top)
    ax = x1 - 30; waist = top + 8; ay = waist - hip*s
    C.saveState()
    C.clipPath(poly([(x0 - 80, top - 10), (x1 + 80, top - 10), (x1 + 80, top + 500), (x0 - 80, top + 500)]), stroke=0, fill=0)
    fn(ax, ay, s, shadow=False, **kw)
    C.restoreState()
    blanket_side(x0, ax + 14, top, waist + 4)
    return ax, ay


def snow_tracks_to(x0, y0, x1, y1, n=6, s=1.0):
    pts = [(x0 + (x1 - x0)*i/(n - 1), y0 + (y1 - y0)*i/(n - 1)) for i in range(n)]
    star_trail(pts, s)


def hallway(p):
    planks(p, P.PLANKS, 26, 9, knots=False)
    floor_y = p.Y(0.1)
    shape([(p.x - 5, p.y - 5), (p.x + p.w + 5, p.y - 5), (p.x + p.w + 5, floor_y), (p.x - 5, floor_y)], P.FLOOR, BG)
    return floor_y



# =================================================================== issue 7 helpers (Joey, the forester)
HEAD.update({"hajny": (116, 11)})


def J(p, x, y, s, flip=False, pose="stand", **kw):
    """Joey, with his head kept clear of balloons"""
    joey(x, y, s, flip=flip, pose=pose, **kw)
    l, r, b, t = (23, 46, 15, 40) if pose == "sniff" else (18, 41, 36, 61)
    if flip: l, r = -r, -l
    keep_clear(p, x + l*s, y + b*s, x + r*s, y + t*s, "joey")


def hj(x, y, s, flip=False, up=2.0):
    """hd() for the forester: his felt hat sits high"""
    return hd("hajny", x, y, s, up=up)


# =================================================================== issue 8 helpers


# the snowman family at the bottom of the garden: (x fraction, size relative to the kids, whose)
FAMILY = [(0.22, 1.45, "deda"), (0.42, 1.1, "betka"), (0.58, 1.05, "alica"), (0.73, 1.0, "tonda")]


def garden8(p, gy, seed=1, k=1.0, family=True, noses="parsnip", gap=0.88, house_x=None, dusk=False, night=False,
            flakes=0, smooth=False, dog=True, fx=None, base=None):
    """the bottom of the chalupa garden: the fence with a gap onto the meadow, the forest beyond, the snowmen.
    noses: one value for all, or a list per snowman. Returns {who: (x, base y, scale)} for the snowmen."""
    winter_meadow(p, gy, seed, sky_g=P.WINTER_NIGHT if night else None)
    if house_x is not None: snowy_house(p.X(house_x), gy - 4, 0.9, smoke=not night)
    snow_fence(p.x - 5, p.x + p.w + 5, gy - 8, 34, gap_at=p.X(gap) if gap is not None else None)
    by = p.Y(0.12) if base is None else base
    if smooth:
        for i in range(5):
            yy = by - 6 + i*7
            stroke([(p.X(0.12), yy), (p.X(0.86), yy + 1)], 0.4, g=0.82)
    out = {}
    if family:
        for i, (f, ss, who) in enumerate(FAMILY if fx is None else [(a, b, c) for (a, b, c) in fx]):
            n = noses[i] if isinstance(noses, (list, tuple)) else noses
            snowman_b(p.X(f), by, ss*k, nose=n, scarf=P.RIBBON if who == "deda" else None,
                      pompom=who == "betka")
            out[who] = (p.X(f), by, ss*k)
        if dog: snow_dog(p.X(0.86), by, 0.9*k, flip=True)
    if flakes: snowfall(p, flakes, seed)
    if dusk: bg_fill(p, 0.0, 0.16)
    if night: bg_fill(p, 0.0, 0.22)
    return out


def nose_y(sm):
    """where a snowman's nose is, from garden8's (x, base, scale)"""
    x, y, s = sm
    return x + 6*s, y + 55*s


def snow_close(p, line=0.35):
    """a close-up of the snow: plain white ground with a pale horizon"""
    bg_fill(p, P.SNOW_SKY)
    fill([(p.x - 5, p.y - 5), (p.x + p.w + 5, p.y - 5), (p.x + p.w + 5, p.Y(1 - line)), (p.x - 5, p.Y(1 - line))], P.SNOW)


def watch_window(p, x0, y0, x1, y1, shape_=False):
    """the bedroom window at night, looking down the garden at the snowmen"""
    shape([(x0 - 6, y0 - 6), (x1 + 6, y0 - 6), (x1 + 6, y1 + 6), (x0 - 6, y1 + 6)], P.DOOR_FRAME, BG)
    shape([(x0, y0), (x1, y0), (x1, y1), (x0, y1)], P.WINTER_NIGHT, BG)
    fill([(x0, y0), (x1, y0), (x1, y0 + (y1 - y0)*0.42), (x0, y0 + (y1 - y0)*0.42)], P.SNOW)
    w = x1 - x0
    for f, s_k in ((0.25, 0.42), (0.45, 0.32), (0.62, 0.3), (0.78, 0.28)):
        snowman_b(x0 + w*f, y0 + (y1 - y0)*0.2, s_k*(w/150), nose="parsnip")
    if shape_:
        # something dark at the fence: no ears to see, no legs, just a shape
        fill(bez((x0 + w*0.88, y0 + (y1 - y0)*0.38), (x0 + w*0.86, y0 + (y1 - y0)*0.5), (x0 + w*0.98, y0 + (y1 - y0)*0.52),
                 (x0 + w*0.99, y0 + (y1 - y0)*0.38)), 0.15)
    r = random.Random(3)
    for _ in range(10):
        dot(x0 + r.random()*w, y0 + (y1 - y0)*(0.6 + r.random()*0.38), 0.9, 1.0)
    s_([((x0 + x1)/2, y0), ((x0 + x1)/2, y1)], BG*1.6, g=P.DOOR_FRAME); s_([(x0, (y0 + y1)/2), (x1, (y0 + y1)/2)], BG*1.6, g=P.DOOR_FRAME)
    shape([(x0 - 10, y0 - 6), (x1 + 10, y0 - 6), (x1 + 10, y0 - 1), (x0 - 10, y0 - 1)], P.SILL, BG)


def inset(p, x, y, w, h, fn, label=None):
    """a round close-up bubble inside a panel (a print or a bite seen through the lupa)"""
    shape(ell(x, y, w/2, h/2, 40), 1.0, LINE*1.2)
    fn(x, y)
    keep_clear(p, x - w/2, y - h/2, x + w/2, y + h/2, "inset")
    if label: hand_text(x - w/2, y - h/2 - 16, w, label, "SHB", 11)


# =================================================================== issue 9 helpers
HID = []   # pages with a hidden koblih, in order; the notebook's answer key is built from it
N_HIDDEN = 10
HEAD.update({"knihovnice": (101.2, 10.4)})


def kk(x, y, rot=0):
    """one of the 10 hidden koblížky (see masopust.hidden_koblih)"""
    hidden_koblih(x, y, 13, rot)
    HID.append(PAGE[0])


def hx(who, x, y, s, top=2.0, up=2.1, wide=1.2):
    """hd() for a figure with something tall or wide on its head (a hood, a mask, a top hat): the tail stops above it
    and all of it is kept clear"""
    tip = hd(who, x, y, s, up)
    if CUR:
        hy, hr = HEAD[who]
        b = CUR[-1].heads[-1]
        b["top"] = y + (hy + hr*top)*s; b["l"] = x - hr*wide*s; b["r"] = x + hr*wide*s
    return tip


def ho(x, y, s): return hx("alica", x, y, s, 2.35, 2.55, 1.3)          # Alica in the owl hood
def hb(x, y, s): return hx("hanka", x, y, s, 1.65, 1.95, 1.55)         # Hanka in the cub hood
def hm(x, y, s): return hx("deda", x, y, s, 1.75, 2.0, 1.7)            # the bear mask
def hbb(x, y, s): return hx("babi", x, y, s, 2.05, 2.25, 1.35)         # the bába's headscarf
def hk(x, y, s): return hx("verka", x, y, s, 2.6, 2.8, 1.5)            # the kominík's top hat
def hkn(x, y, s): return hx("knihovnice", x, y, s, 1.4, 1.5, 1.35)


def joey_smell(p, x, y, kind="lavender", n=4, seed=1):
    """what Joey smells, drawn like in issue 7: little lavender sprigs (babička), flour puffs (the mill), fish"""
    r = random.Random(seed)
    for i in range(n):
        px, py = x + r.uniform(-28, 28), y + r.uniform(-6, 18)
        if kind == "lavender":
            lavender_sprig(px, py, 1.5, r.uniform(-25, 25))
        else:
            for k_ in range(5):
                shape(ell(px + r.uniform(-4, 4), py + r.uniform(-3, 3), 2.2, 1.8, 10), 1.0, LINE*0.4)
    keep_clear(p, x - 34, y - 10, x + 34, y + 24, "smell")


def big_slip(p, x, y, lines, w=None, gh=20, rot=0, old=False, style="jana"):
    """a slip shown large in a panel, kept clear of balloons"""
    w = w or max(cipher_width(l, gh) for l in lines) + gh*1.4
    h = len(lines)*gh*1.25 + gh*0.9
    slip(x, y, w, h, lines, gh, rot, old=old, style=style)
    keep_clear(p, x - w/2 - 4, y - h/2 - 4, x + w/2 + 4, y + h/2 + 4, "slip")


def chalupa_room(p, evening=False, sewing=None):
    """the kitchen at the chalupa; sewing=x fraction puts babička's sewing table there"""
    kitchen(p, table=False, evening=evening)
    if sewing is not None:
        sewing_corner(p.X(sewing), p.y + 4, 1.0)


def hidden_star(x, y, r):
    """the star Věrka hides behind her back (her kominík hat's star), peeking out, with a little glint"""
    star(x, y, r, P.MASK, LINE*0.9)
    for a in (20, 70, 120):
        ra = math.radians(a)
        stroke([(x + math.cos(ra)*r*1.4, y + math.sin(ra)*r*1.4), (x + math.cos(ra)*r*2, y + math.sin(ra)*r*2)], LINE*0.7)


def table_top(p, y=0.32):
    """the kitchen table's edge across the back of a panel, for things lying on it"""
    shape([(p.X(0.03), p.Y(y)), (p.X(0.97), p.Y(y)), (p.X(0.97), p.Y(y + 0.04)), (p.X(0.03), p.Y(y + 0.04))], 0.5, BG)


def mill_winter(p, gy, seed=1, mill_x=0.6, mill_s=0.75):
    winter_garden(p, gy, seed, trees=((0.1, 0.8),))
    mill(p.X(mill_x), gy - 4, mill_s)


def morce(x, y, s=1.0, flip=False):
    """a guinea pig (morče) from the school's outdoor hutch: a round loaf, white with brown and black patches"""
    with T(x, y, s, flip):
        body = bez((-15, 4), (-17, 18), (2, 21), (10, 17)) + bez((10, 17), (17, 15), (19, 9), (17, 4)) + \
               bez((17, 4), (12, 0), (-10, 0), (-15, 4))
        fill(body, 0.97)
        C.saveState(); C.clipPath(poly(body), stroke=0, fill=0)
        fill(ell(-8, 12, 9, 9, 24), P.DACHSHUND)
        fill(ell(13, 13, 6, 7, 20), 0.2)
        C.restoreState()
        stroke(body, LINE, closed=True)
        shape(ell(9, 17.5, 2.6, 2, 12), 0.2, LINE*0.6)
        dot(13.5, 11.5, 1.2, 1.0) if False else dot(13.5, 11.5, 1.1, 0.0)
        dot(18.2, 7.5, 0.8, 0.3)
        for fx in (-9, 9): stroke([(fx, 1), (fx + 2, 0)], LINE*1.2)


def kotec(x, y, s=1.0, open_=True):
    """the school's outdoor guinea-pig hutch: a wooden box on legs, a mesh front, a sloping roof; (x, y) = ground"""
    with T(x, y, s):
        for lx in (-38, 34): sh_([(lx, 0), (lx + 4, 0), (lx + 4, 12), (lx, 12)], P.KRMELEC)
        sh_([(-40, 12), (40, 12), (40, 46), (-40, 46)], P.SHELF)
        fill([(-34, 15), (6, 15), (6, 43), (-34, 43)], 0.25)
        C.saveState(); C.clipPath(poly([(-34, 15), (6, 15), (6, 43), (-34, 43)]), stroke=0, fill=0)
        for k in range(-34, 7, 4): stroke([(k, 15), (k, 43)], LINE*0.35, g=0.75)
        for k in range(15, 44, 4): stroke([(-34, k), (6, k)], LINE*0.35, g=0.75)
        C.restoreState()
        fill(bez((-32, 15), (-28, 22), (-18, 22), (-12, 15)), P.HAY)
        stroke([(-34, 15), (6, 15), (6, 43), (-34, 43), (-34, 15)], LINE*0.8)
        sh_([(10, 15), (36, 15), (36, 43), (10, 43)], P.SHELF)
        shape(ell(23, 29, 6, 6, 20), 0.15, LINE*0.6)
        if open_:
            shape([(36, 15), (54, 8), (54, 36), (36, 43)], 0.9, LINE*0.8)
            for k in range(1, 5): stroke([(36 + k*3.6, 15 - k*1.4), (36 + k*3.6, 43 - k*1.4)], LINE*0.3, g=0.5)
        sh_([(-46, 44), (46, 44), (40, 58), (-40, 58)], P.KRMELEC)
        stroke([(-44, 47), (44, 47)], LINE*0.4, g=0.3)


# =================================================================== 1 COVER
def cover():
    with Pn(M, 40, W-2*M, H-80) as p:
        gy = p.Y(0.5)
        masopust_street(p, gy, 91, houses=((0.08, 0.9), (0.4, 0.8), (0.9, 0.95)), church_x=0.62, garlands=0)
        streamers(p.x - 5, p.x + p.w + 5, p.Y(0.5), 14, 18, 4)
        medved(p.X(0.18), p.Y(0.42), 0.9, mood="happy")
        kominik(p.X(0.36), p.Y(0.42), 0.85, flip=True)
        baba(p.X(0.82), p.Y(0.42), 0.9, flip=True)
        slip(p.X(0.5), p.Y(0.33), 300, 100, ["HLEDEJ HVEZDU", "NA MASOPUSTU"], 30, rot=-4)
        J(p, p.X(0.62), p.Y(0.04), 1.9, mood="happy")
        alica_owl(p.X(0.17), p.Y(0.03), 1.9, mood="think", right="lens", look=(1, -0.3), item=lambda x, y: magnifier(x + 2, y + 8, ang=-20, r=6))
        hanka_bear(p.X(0.86), p.Y(0.03), 1.95, flip=True, mood="wow", right="point", look=(-1, -0.2), left="hug")
    box = [(M+34, H-236), (W-M-30, H-232), (W-M-34, H-48), (M+30, H-52)]
    fill([(x+3, y-3) for x, y in box], 0.0, 0.25); fill(box, 1.0)
    for a_, b_ in ((0, 1), (1, 2), (2, 3), (3, 0)): stroke([box[a_], box[b_]], 1.8)
    series_title(W/2, H-98, H-160, 40, 66)
    hand_text(M+40, H-190, W-2*M-80, "Alica, Hanka a Joey", "SHB", 20)
    hand_text(M+40, H-217, W-2*M-80, "Případ č. 9: Tajná zpráva v knihovně", "SH", 15)
    magnifier(M+82, H-120, ang=-30, r=17)
    glyph("E", W-M-100, H-140, 42)
    page_end()


# =================================================================== 2 WHO IS WHO
def page_cast():
    with Pn(M, 40, W-2*M, H-80) as p:
        hand_text(p.X(0.05), p.Y(0.95), p.w*0.9, "Kdo je kdo", "SHB", 28)
        cells = [
            ("Alica", "Lupa a zápisník.", lambda x, y: A(x, y, 0.9, hat=False, mood="happy", right="lens", lens=True)),
            ("Hanka", "Opička a baterka.", lambda x, y: Hk(x, y, 1.1, hat=False, mood="grin", right="hug")),
            ("Joey", "Nejlepší nos na světě.", lambda x, y: joey(x, y, 1.2, mood="happy")),
            ("Babička a děda", "Babička šije, děda vypráví.", lambda x, y: (babicka(x - 22, y, 0.72, mood="happy"),
                                                                       deda(x + 22, y, 0.66, mood="happy"))),
            ("Tonda a Bětka", "Kamarádi z Klubu.", lambda x, y: (Td(x - 20, y, 0.78, mood="grin"), betka(x + 22, y, 0.9, mood="happy"))),
            ("Franta a Věrka", "Dědovi kamarádi z dětství.", lambda x, y: (franta(x - 22, y, 0.6, mood="happy"),
                                                                      verka_old(x + 22, y, 0.66, mood="happy", stick=False))),
            ("Paní knihovnice", "A jezevčík. Vítá každého.", lambda x, y: (knihovnice(x - 14, y, 0.72, mood="happy"),
                                                                                jezevcik(x + 20, y, 0.9, pose="wag"))),
            ("Masopust", "Masky, průvod a koblihy.", lambda x, y: (bear_head(x - 20, y + 36, 9), koblih(x + 22, y + 14, 1.2))),
            ("???", "Kdo píše tajné zprávy?", lambda x, y: cipher_text("KDO", x - 30, y + 14, 26)),
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
                  "Sněhulákům snědla nosy srnka. A z knížky z knihovny pak vypadl podivný papírek. Samé hvězdičky a tečky!",
                  "SH", 13, align="left", lead=17)
        srnka(p.X(0.82), by + 16, 0.95, flip=True, shadow=False)
        slip(p.X(0.4), by + bh*0.3, 150, 50, ["HLEDEJ HVEZDU"], 12, rot=6)
    page_end()


# =================================================================== 3 evening: the slip
def page_slip():
    R = rows([(270, [1]), (230, [0.5, 0.5]), (250, [1])])
    with Pn(*R[0]) as p:
        chalupa_room(p, evening=True, sewing=0.84)
        babicka(p.X(0.72), p.y + 4, 1.0, mood="happy", right="front", look=(1, -0.3))
        A(p.X(0.14), p.Y(0.03), 1.15, hat=False, mood="surprised", right="front", look=(1, -0.2),
          item=lambda x, y: book(x + 12, y - 6, 0.8, rot=10))
        Hk(p.X(0.32), p.Y(0.03), 1.05, hat=False, mood="wow", look=(-1, 0))
        cap(p, "Jarní prázdniny na chalupě. Večer v kuchyni šije babička kostýmy na Masopust.", w=260, where="tr")
        say(p, "Ten papírek byl v knížce z knihovny!", *hd("alica", p.X(0.14), p.Y(0.03), 1.15), w=150, area=(0.0, 0.5))
    with Pn(*R[1]) as p:
        bg_fill(p, 0.88)
        big_slip(p, p.X(0.5), p.Y(0.45), ["HLEDEJ HVEZDU", "NA MASOPUSTU"], gh=17, rot=-3)
        cap(p, "Hvězdičky, měsíčky, srdíčka a tečky.", w=200, where="tl")
    with Pn(*R[2]) as p:
        bg_fill(p, P.LIB_WALL); bg_fill(p, 0.0, 0.15)
        Hk(p.X(0.3), p.Y(0.03), 1.4, hat=False, mood="grin", right="up", look=(1, 0.3),
           item=lambda x, y: slip(x + 10, y + 8, 40, 20, ["AHOJ"], 6, rot=12))
        say(p, "Papírek má zoubky!", *hd("hanka", p.X(0.3), p.Y(0.03), 1.4), w=110, area=(0.35, 1.0))
    with Pn(*R[3]) as p:
        chalupa_room(p, evening=True)
        J(p, p.X(0.45), p.Y(0.03), 1.15, pose="sniff", mood="happy")
        slip(p.X(0.45) + 66, p.Y(0.05), 60, 24, ["HLEDEJ"], 7, rot=8)
        joey_smell(p, p.X(0.45) + 66, p.Y(0.05) + 40, "lavender", 4, 3)
        A(p.X(0.12), p.Y(0.03), 1.1, hat=False, mood="happy", look=(1, 0))
        kk(p.X(0.95), p.Y(0.1), 15)
        cap(p, "Joey papírek očichal. Voní nějak povědomě.", w=200, where="tr")
        say(p, "Joey, to není k jídlu!", *hd("alica", p.X(0.12), p.Y(0.03), 1.1), w=120, area=(0.0, 0.35))
    page_end()


# =================================================================== 4 děda knows the code
def page_code():
    R = rows([(250, [1]), (220, [0.5, 0.5]), (280, [1])])
    with Pn(*R[0]) as p:
        chalupa_room(p, evening=True)
        deda(p.X(0.62), p.Y(0.03), 1.05, flip=True, mood="surprised", right="front", look=(-1, -0.3),
             item=lambda x, y: slip(x - 6, y + 4, 40, 18, ["HLEDEJ"], 5, rot=-8))
        A(p.X(0.15), p.Y(0.03), 1.1, hat=False, mood="wow", look=(1, 0.2))
        Hk(p.X(0.3), p.Y(0.03), 1.0, hat=False, mood="happy", look=(1, 0.2))
        say(p, "Dědo, co to je?", *hd("alica", p.X(0.15), p.Y(0.03), 1.1), w=100, area=(0.0, 0.42))
        say(p, "Hvězdičkové písmo! Tajné písmo Klubu Hvězdička!", *hd("deda", p.X(0.62), p.Y(0.03), 1.05), w=180, area=(0.42, 1.0))
    with Pn(*R[1]) as p:
        chalupa_room(p, evening=True)
        deda(p.X(0.25), p.Y(0.03), 0.85, mood="happy", right="chin", look=(1, 0.2))
        say(p, "Vymysleli jsme ho s Frantou a Věrkou. Před šedesáti lety.", *hd("deda", p.X(0.25), p.Y(0.03), 0.85), w=200)
    with Pn(*R[2]) as p:
        chalupa_room(p, evening=True)
        Hk(p.X(0.2), p.Y(0.03), 1.05, hat=False, mood="think", look=(1, 0.3))
        deda(p.X(0.75), p.Y(0.03), 0.8, flip=True, mood="grin", right="up", look=(-1, 0))
        say(p, "Umíš ho číst?", *hd("hanka", p.X(0.2), p.Y(0.03), 1.05), w=100, area=(0.0, 0.45))
        say(p, "Už ne. Ale klíč je na půdě!", *hd("deda", p.X(0.75), p.Y(0.03), 0.8), w=120, area=(0.4, 1.0))
    with Pn(*R[3]) as p:
        attic(p, floor_y=0.12, dark=0.35, seed=9)
        chest(p.X(0.62), p.Y(0.12), 1.1, open_=True)
        for k_, (sx_, sy_, rr) in enumerate(((0.7, 0.37, 12), (0.78, 0.32, -10), (0.56, 0.35, 20))):
            slip(p.X(sx_), p.Y(sy_), 34, 18, ["AHOJ"], 5, rot=rr, old=True, seed=k_)
        deda(p.X(0.88), p.Y(0.06), 1.0, flip=True, mood="grin", right="up", look=(-1, 0),
             item=lambda x, y: notebook(x - 6, y, 0.9))
        Hk(p.X(0.12), p.Y(0.06), 1.15, hat=False, mood="wow", right="up", look=(1, 0), torch=True)
        hx2, hy2 = hand_pt(True, "up", p.X(0.12), p.Y(0.06), 1.15)
        torch_beam(hx2 + 6, hy2 + 4, p.X(0.6), p.Y(0.2), p.X(0.75), p.Y(0.45), 0.35)
        A(p.X(0.3), p.Y(0.06), 1.15, hat=False, mood="surprised", look=(1, 0))
        kk(p.X(0.05), p.Y(0.85), -20)
        cap(p, "Na půdě, ve staré truhle.", w=170, where="tr")
        say(p, "Tady jsou naše staré zprávy. A tady klíč!", *hd("deda", p.X(0.88), p.Y(0.06), 1.0), w=150, area=(0.55, 1.0))
    page_end()


# =================================================================== 5 decoding
def page_decode():
    R = rows([(240, [1]), (240, [0.5, 0.5]), (270, [1])])
    with Pn(*R[0]) as p:
        chalupa_room(p)
        table_top(p)
        notebook(p.X(0.55), p.Y(0.37), 1.4)
        slip(p.X(0.72), p.Y(0.42), 70, 26, ["HLEDEJ"], 9, rot=4)
        A(p.X(0.2), p.Y(0.03), 1.2, hat=False, mood="think", right="front", look=(1, -0.4))
        Hk(p.X(0.38), p.Y(0.03), 1.05, hat=False, mood="happy", look=(1, -0.3))
        cap(p, "Alica luští. Obrázek a tečky. Jako na kostce!", w=190, where="tr")
        say(p, "Měsíček a dvě tečky. To je H! Teď měsíček a šest teček…", *hd("alica", p.X(0.2), p.Y(0.03), 1.2), w=200, area=(0.0, 0.62))
    with Pn(*R[1]) as p:
        bg_fill(p, 0.95)
        cipher_decoded("HLEDEJ", p.X(0.1), p.Y(0.42), 30, upto=3, style="jana")
        cap(p, "H… L… E…", w=100, where="tl")
    with Pn(*R[2]) as p:
        chalupa_room(p)
        babicka(p.X(0.25), p.Y(0.03), 1.1, mood="happy", right="front", look=(1, 0), item=lambda x, y: mug(x, y - 4, 0.8))
        A(p.X(0.75), p.Y(0.03), 1.15, hat=False, flip=True, mood="surprised", look=(-1, 0))
        say(p, "Čtyři tečky? To je D, ne?", *hd("babi", p.X(0.25), p.Y(0.03), 1.1), w=120, area=(0.0, 0.55))
        say(p, "Jo, D! Díky, babi.", *hd("alica", p.X(0.75), p.Y(0.03), 1.15), w=100, area=(0.45, 1.0))
    with Pn(*R[3]) as p:
        bg_fill(p, 0.95)
        cipher_decoded("HLEDEJ HVEZDU", p.X(0.06), p.Y(0.68), 26)
        cipher_decoded("NA MASOPUSTU", p.X(0.06), p.Y(0.3), 26)
        A(p.X(0.8), p.Y(0.03), 0.85, hat=False, flip=True, mood="wow", right="up", look=(-1, 0))
        Hk(p.X(0.93), p.Y(0.03), 0.8, hat=False, flip=True, mood="think", look=(-1, 0))
        say(p, "„Hledej hvězdu na Masopustu!“", *hd("alica", p.X(0.8), p.Y(0.03), 0.85), w=170, area=(0.55, 1.0))
        say(p, "Co je Masopust?", *hd("hanka", p.X(0.93), p.Y(0.03), 0.8), w=110, area=(0.6, 1.0))
    page_end()


# =================================================================== 6 old or new?
def page_old():
    R = rows([(250, [1]), (220, [0.5, 0.5]), (280, [1])])
    with Pn(*R[0]) as p:
        chalupa_room(p)
        table_top(p)
        deda(p.X(0.12), p.Y(0.03), 1.0, mood="grin", right="up", look=(1, 0.3))
        say(p, "Masopust je v sobotu! Celá ves půjde v maskách.", *hd("deda", p.X(0.12), p.Y(0.03), 1.0), w=180, area=(0.0, 0.5))
        A(p.X(0.85), p.Y(0.03), 1.1, hat=False, flip=True, mood="think", right="lens", lens=True, look=(-1, -0.3))
        slip(p.X(0.42), p.Y(0.42), 60, 30, ["AHOJ", "KLUB"], 8, rot=-6, old=True, seed=4)
        slip(p.X(0.62), p.Y(0.42), 64, 30, ["HLEDEJ"], 9, rot=5)
        say(p, "Staré zprávy jsou žluté. Tahle je bílá. Nová!", *hd("alica", p.X(0.85), p.Y(0.03), 1.1), w=150, area=(0.45, 1.0))
    with Pn(*R[1]) as p:
        bg_fill(p, P.LIB_WALL)
        Hk(p.X(0.28), p.Y(0.03), 1.35, hat=False, mood="determined", right="point", look=(1, 0))
        slip(p.X(0.75), p.Y(0.3), 60, 28, ["HLEDEJ"], 8, rot=8)
        say(p, "A má zoubky. Ty staré ne.", *hd("hanka", p.X(0.28), p.Y(0.03), 1.35), w=130)
    with Pn(*R[2]) as p:
        bg_fill(p, P.LIB_WALL)
        A(p.X(0.22), p.Y(0.03), 1.1, hat=False, mood="determined", right="up", look=(1, 0))
        deda(p.X(0.78), p.Y(0.03), 0.92, flip=True, mood="surprised", look=(-1, 0))
        say(p, "Někdo umí vaše písmo i dnes!", *hd("alica", p.X(0.22), p.Y(0.03), 1.1), w=120, area=(0.0, 0.55))
        say(p, "Ale kdo?", *hd("deda", p.X(0.78), p.Y(0.03), 0.92), w=80, area=(0.5, 1.0))
    with Pn(*R[3]) as p:
        bg_fill(p, 0.9)
        notebook_big(p.X(0.06), p.Y(0.06), p.w*0.88, p.h*0.88, "PŘÍPAD Č. 9: TAJNÁ ZPRÁVA",
                     ["1. Písmo znají: děda, Franta, Věrka.",
                      "2. Tonda má klubový odznak. Viděl zápisník?",
                      "3. Papírek je bílý, nový. A má zoubky.",
                      "4. Zpráva: hledej hvězdu na Masopustu.",
                      "5. Kdo měl tu knížku? KNIHOVNA!"])
        kk(p.X(0.93), p.Y(0.12), -30)
    page_end()


# =================================================================== 7 the star code: full-page key
def page_key():
    with Pn(M, 40, W-2*M, H-80, bg=0.97) as p:
        hand_text(p.X(0.04), p.Y(0.955), p.w*0.92, "Hvězdičkové písmo Klubu Hvězdička", "SHB", 24)
        hand_text(p.X(0.04), p.Y(0.915), p.w*0.92, "Každé písmenko je obrázek a pod ním tečky. Tečky počítej jako na kostce!", "SH", 13)
        kx, ky, kw, kh = p.X(0.05), p.Y(0.42), p.w*0.9, p.h*0.47
        shape(rrect(kx - 6, ky - 6, kw + 12, kh + 12, 10), 1.0, 1.2)
        cipher_key(kx, ky, kw, kh, style="deda", title=False)
        for r_, nm in enumerate(("hvězdička", "měsíček", "srdíčko", "kolečko")):
            pass
        hand_text(p.X(0.05), p.Y(0.36), p.w*0.9, "Zkus to! Čti prstem, písmenko po písmenku:", "SHB", 16)
        words = ["JOEY", "SOVA", "MEDVED"]
        for i, wd in enumerate(words):
            yy = p.Y(0.27) - i*62
            hand_text(p.X(0.05), yy + 6, 20, str(i + 1), "SHB", 16, align="left")
            cipher_text(wd, p.X(0.14), yy - 6, 40, style="deda")
        hand_text(p.X(0.05), p.Y(0.03) + 18, p.w*0.9, "Pozor: babička kreslí hvězdičky jinak. Jedním tahem, s okýnkem uprostřed.", "SH", 11)
        with T(p.X(0.5), p.Y(0.015), 1.0, rot=180):
            hand_text(-p.w*0.45, 0, p.w*0.9, "1. JOEY  2. SOVA  3. MEDVĚD", "SH", 11)
    page_end()


# =================================================================== 8 the library
def page_library():
    R = rows([(280, [1]), (220, [0.5, 0.5]), (250, [1])])
    with Pn(*R[0]) as p:
        fy = library(p, 0.1, seed=3)
        knihovnice(p.X(0.72), fy + 12, 1.0, flip=True, mood="happy", right="wave", look=(-1, 0))
        library_desk(p.X(0.55), fy, 170)
        jezevcik(p.X(0.32), fy, 1.3, pose="up", mood="happy")
        J(p, p.X(0.14), fy, 1.0, mood="happy")
        A(p.X(0.04), fy, 1.0, hat=False, mood="grin", look=(1, 0))
        cap(p, "Ráno jdou detektivové do vesnické knihovny.", w=200, where="tl")
        say(p, "Dobrý den! Jezevčík vás musí přivítat. Vítá každého.", *hkn(p.X(0.72), fy + 12, 1.0), w=180, area=(0.48, 1.0))
    with Pn(*R[1]) as p:
        fy = library(p, 0.1, seed=4, window=False)
        J(p, p.X(0.12), fy, 1.15, pose="sniff", mood="happy")
        jezevcik(p.X(0.56), fy, 1.5, flip=True, pose="sniff")
        sfx(p.X(0.36), p.Y(0.62), "ČMUCH!", 16, -6)
    with Pn(*R[2]) as p:
        fy = library(p, 0.1, seed=5, window=False)
        Hk(p.X(0.3), fy, 1.3, hat=False, mood="grin", right="hug", look=(1, -0.3))
        jezevcik(p.X(0.72), fy, 1.2, flip=True, pose="wag")
        say(p, "On se usmívá!", *hd("hanka", p.X(0.3), fy, 1.3), w=100)
    with Pn(*R[3]) as p:
        fy = library(p, 0.1, seed=6)
        knihovnice(p.X(0.62), fy + 12, 1.0, flip=True, mood="happy", right="up", look=(-1, -0.3),
                   item=lambda x, y: book(x - 10, y - 2, 0.8, rot=-10))
        library_desk(p.X(0.42), fy, 200)
        A(p.X(0.14), fy, 1.1, hat=False, mood="think", right="front", look=(1, 0), item=lambda x, y: book(x + 12, y - 6, 0.8, rot=10))
        kk(p.X(0.95), p.Y(0.08), 20)
        say(p, "Kdo měl tuhle knížku před námi?", *hd("alica", p.X(0.14), fy, 1.1), w=130, area=(0.0, 0.42))
        say(p, "Podívám se do kartičky. Tuhle ti vybrala babička, viď?", *hkn(p.X(0.62), fy + 12, 1.0), w=230, area=(0.42, 1.0))
    page_end()


# =================================================================== 9 the borrowing card
def page_card():
    R = rows([(300, [1]), (210, [0.5, 0.5]), (240, [1])])
    with Pn(*R[0]) as p:
        bg_fill(p, 0.86)
        book(p.X(0.25), p.Y(0.2), 2.6, rot=-4)
        library_card(p.X(0.42), p.Y(0.07), 200, 250, [("Honza", "3. 2. 1966", True), ("Ja", "10. 2. 1966", True),
                                                       ("Pepa", "4. 5. 1979", True), ("Lenka", "1. 9. 1995", False),
                                                       ("Tonda", "12. 12.", False), ("Alica", "1. 2.", False)], rot=3)
        with T(p.X(0.42), p.Y(0.07), 1.0, rot=3):
            for k_ in range(5):
                fill(ell(54 + k_*7, 182 - 1, 6, 4.4, 14), 0.55, 0.35)
        keep_clear(p, p.X(0.4), p.Y(0.05), p.X(0.42) + 205, p.Y(0.07) + 260, "card")
        cap(p, "Kartička z knížky. Kdo si ji kdy půjčil.", w=200, where="tl")
    with Pn(*R[1]) as p:
        fy = library(p, 0.1, seed=7, window=False)
        A(p.X(0.3), fy, 1.2, hat=False, mood="wow", right="up", look=(1, 0))
        say(p, "Tonda! Ten ji měl v prosinci!", *hd("alica", p.X(0.3), fy, 1.2), w=130)
    with Pn(*R[2]) as p:
        fy = library(p, 0.1, seed=8, window=False)
        Hk(p.X(0.3), fy, 1.3, hat=False, mood="wow", look=(1, 0))
        say(p, "A Honza? To je náš děda!", *hd("hanka", p.X(0.3), fy, 1.3), w=120)
    with Pn(*R[3]) as p:
        fy = library(p, 0.1, seed=9)
        A(p.X(0.12), fy, 0.95, hat=False, mood="think", right="chin", look=(1, 0))
        knihovnice(p.X(0.82), fy, 0.95, flip=True, mood="happy", look=(-1, 0))
        jezevcik(p.X(0.62), fy, 1.0, flip=True, pose="wag")
        say(p, "Před šedesáti lety. A to druhé jméno je rozmazané. Ja… něco.", *hd("alica", p.X(0.12), fy, 0.95), w=230,
            area=(0.0, 0.55))
        say(p, "Tahle knížka je starší než moje maminka!", *hkn(p.X(0.82), fy, 0.95), w=170, area=(0.55, 1.0))
    page_end()


# =================================================================== 10 Tonda
def page_tonda():
    R = rows([(280, [1]), (220, [0.5, 0.5]), (250, [1])])
    with Pn(*R[0]) as p:
        gy = p.Y(0.5)
        winter_garden(p, gy, 92, house_x=0.15, trees=((0.9, 0.8),))
        kobyla(p.X(0.6), p.Y(0.04), 1.2, mood="grin", mask=False)
        A(p.X(0.14), p.Y(0.03), 1.05, mood="happy", look=(1, 0))
        Hk(p.X(0.27), p.Y(0.03), 0.98, mood="wow", look=(1, 0))
        cap(p, "Tonda zkouší kostým na Masopust.", w=200, where="tr")
        say(p, "Ijááá! Já budu kobyla!", *hd_h("tonda", p.X(0.6), p.Y(0.04), 1.2), w=120, area=(0.38, 0.85))
    with Pn(*R[1]) as p:
        winter_garden(p, p.Y(0.55), 93)
        A(p.X(0.28), p.Y(0.03), 1.15, mood="determined", right="front", look=(1, 0),
          item=lambda x, y: slip(x + 10, y + 4, 40, 18, ["HLEDEJ"], 5, rot=6))
        say(p, "Tondo, napsal jsi tohle?", *hd_h("alica", p.X(0.28), p.Y(0.03), 1.15), w=120)
    with Pn(*R[2]) as p:
        winter_garden(p, p.Y(0.55), 94)
        Td(p.X(0.4), p.Y(0.03), 1.0, mood="surprised", right="chin", look=(0, -0.3))
        say(p, "Hvězdičky? Já to vůbec neumím přečíst!", *hd_h("tonda", p.X(0.4), p.Y(0.03), 1.0), w=180)
    with Pn(*R[3]) as p:
        gy = p.Y(0.5)
        winter_garden(p, gy, 95, house_x=0.85)
        Td(p.X(0.15), p.Y(0.03), 1.1, mood="grin", right="up", look=(1, 0))
        A(p.X(0.55), p.Y(0.03), 1.1, flip=True, mood="think", right="chin", look=(-1, 0))
        Hk(p.X(0.68), p.Y(0.03), 1.0, flip=True, mood="happy", look=(-1, 0))
        say(p, "Naučíte mě to? Prosím!", *hd_h("tonda", p.X(0.15), p.Y(0.03), 1.1), w=110, area=(0.0, 0.42))
        say(p, "Tonda písmo nezná. Tak to nebyl on.", *hd_h("alica", p.X(0.55), p.Y(0.03), 1.1), w=140, area=(0.35, 0.8))
    page_end()


# =================================================================== 11 Franta
def page_franta():
    R = rows([(280, [1]), (220, [0.5, 0.5]), (250, [1])])
    with Pn(*R[0]) as p:
        gy = p.Y(0.5)
        winter_garden(p, gy, 96, house_x=0.85)
        franta(p.X(0.62), p.Y(0.03), 1.0, flip=True, mood="happy", right="front", look=(-1, -0.2))
        betka_kitten(p.X(0.8), p.Y(0.03), 1.05, flip=True, mood="grin", look=(-1, 0))
        A(p.X(0.12), p.Y(0.03), 1.05, mood="happy", right="front", look=(1, 0),
          item=lambda x, y: slip(x + 10, y + 4, 40, 18, ["HLEDEJ"], 5, rot=6))
        Hk(p.X(0.26), p.Y(0.03), 0.98, mood="happy", look=(1, 0))
        kk(p.X(0.04), p.Y(0.55), 10)
        say(p, "Hvězdičkové písmo? To jsem vymyslel já! S Honzou a s Věrkou.", *hd("franta", p.X(0.62), p.Y(0.03), 1.0), w=200,
            area=(0.3, 0.8))
    with Pn(*R[1]) as p:
        winter_garden(p, p.Y(0.55), 97)
        A(p.X(0.3), p.Y(0.03), 1.15, mood="determined", look=(1, 0))
        say(p, "Tak jste to psal vy?", *hd_h("alica", p.X(0.3), p.Y(0.03), 1.15), w=110)
    with Pn(*R[2]) as p:
        winter_garden(p, p.Y(0.55), 98)
        franta(p.X(0.3), p.Y(0.03), 0.95, mood="grin", right="front", look=(1, -0.3),
               item=lambda x, y: new_letter(x - 4, y - 10, 0.55, rot=-6))
        say(p, "Já? Já písmenka nerad. Já píšu obrázky.", *hd("franta", p.X(0.3), p.Y(0.03), 0.95), w=170)
    with Pn(*R[3]) as p:
        gy = p.Y(0.5)
        winter_garden(p, gy, 99, trees=((0.92, 0.7),))
        betka_kitten(p.X(0.15), p.Y(0.03), 1.15, mood="grin", right="up", look=(1, 0))
        franta(p.X(0.55), p.Y(0.03), 0.95, flip=True, mood="happy", look=(-1, 0))
        Hk(p.X(0.8), p.Y(0.03), 1.0, flip=True, mood="wow", look=(-1, 0))
        say(p, "Děda Franta bude na Masopustu medvědář. Vodí medvěda!", *hd("betka", p.X(0.15), p.Y(0.03), 1.15), w=180,
            area=(0.0, 0.5))
        say(p, "A medvěd bude zase váš děda. Jako každý rok.", *hd("franta", p.X(0.55), p.Y(0.03), 0.95), w=170, area=(0.45, 1.0))
    page_end()


# =================================================================== 12 Věrka
def page_verka():
    R = rows([(280, [1]), (220, [0.5, 0.5]), (250, [1])])
    with Pn(*R[0]) as p:
        gy = p.Y(0.5)
        mill_winter(p, gy, 100, 0.68, 0.8)
        verka_old(p.X(0.42), p.Y(0.03), 1.05, flip=True, mood="grin", right="back", look=(-1, 0), stick=False)
        hidden_star(p.X(0.42) + 22, p.Y(0.03) + 50, 11)
        A(p.X(0.1), p.Y(0.03), 1.05, mood="happy", look=(1, 0))
        Hk(p.X(0.22), p.Y(0.03), 0.98, mood="happy", look=(1, 0))
        J(p, p.X(0.9), p.Y(0.03), 0.95, flip=True, mood="happy")
        cap(p, "U mlýna.", w=90, where="tr")
        say(p, "Ale, detektivové! Copak vás vede?", *hd("verka", p.X(0.42), p.Y(0.03), 1.05), w=140, area=(0.25, 0.75))
    with Pn(*R[1]) as p:
        winter_garden(p, p.Y(0.55), 101)
        Hk(p.X(0.25), p.Y(0.03), 1.25, mood="whisper", right="point", look=(1, 0))
        verka_old(p.X(0.75), p.Y(0.03), 0.9, flip=True, mood="happy", right="back", look=(-1, 0), stick=False)
        hidden_star(p.X(0.75) + 19, p.Y(0.03) + 44, 10)
        say(p, "Má za zády hvězdu!", *hd_h("hanka", p.X(0.25), p.Y(0.03), 1.25), w=100, area=(0.0, 0.5), whisper=True)
    with Pn(*R[2]) as p:
        winter_garden(p, p.Y(0.55), 102)
        verka_old(p.X(0.3), p.Y(0.03), 0.85, mood="grin", right="back", left="hush", look=(1, 0), stick=False)
        say(p, "To je překvapení na sobotu. Neprozradím!", *hd("verka", p.X(0.3), p.Y(0.03), 0.85), w=190)
    with Pn(*R[3]) as p:
        winter_garden(p, p.Y(0.5), 103)
        verka_old(p.X(0.7), p.Y(0.03), 1.0, flip=True, mood="happy", look=(-1, -0.3), stick=False)
        J(p, p.X(0.5), p.Y(0.03), 1.05, pose="sniff", mood="happy")
        joey_smell(p, p.X(0.62), p.Y(0.45), "flour", 3, 4)
        A(p.X(0.12), p.Y(0.03), 1.05, mood="think", right="chin", look=(1, 0))
        cap(p, "Joey čichá: mouka. Věrka mele ve mlýně mouku.", w=210, where="tr")
        say(p, "Hvězda… Že by to byla Věrka?", *hd_h("alica", p.X(0.12), p.Y(0.03), 1.05), w=130, area=(0.0, 0.4), whisper=True)
    page_end()


# =================================================================== 13 the second slip
def page_boot():
    R = rows([(260, [1]), (230, [0.5, 0.5]), (260, [1])])
    with Pn(*R[0]) as p:
        fy = hallway(p)
        for k_ in range(3): boot(p.X(0.5) + k_*20, fy, 0.6)
        A(p.X(0.25), fy, 1.15, hat=False, mood="surprised", right="front", look=(1, -0.4),
          item=lambda x, y: boot(x + 2, y - 8, 0.55))
        slip(p.X(0.36), fy + 20, 36, 16, ["PRIJD"], 4.5, rot=-25)
        J(p, p.X(0.8), fy, 1.0, flip=True, mood="happy")
        kk(p.X(0.95), p.Y(0.14), 30)
        cap(p, "Ráno v předsíni.", w=130, where="tr")
        say(p, "V mé botě je další papírek!", *hd("alica", p.X(0.25), fy, 1.15), w=120, area=(0.0, 0.55))
    with Pn(*R[1]) as p:
        bg_fill(p, 0.88)
        big_slip(p, p.X(0.5), p.Y(0.45), ["PRIJD", "V MASCE"], gh=22, rot=4)
        cap(p, "Zase zoubky.", w=110, where="tl")
    with Pn(*R[2]) as p:
        bg_fill(p, P.LIB_WALL)
        A(p.X(0.25), p.Y(0.03), 1.15, hat=False, mood="wow", right="up", look=(1, 0))
        Hk(p.X(0.72), p.Y(0.03), 1.1, hat=False, flip=True, mood="grin", look=(-1, 0))
        say(p, "„Přijď v masce!“", *hd("alica", p.X(0.25), p.Y(0.03), 1.15), w=100, area=(0.0, 0.6))
        say(p, "Já chci masku!", *hd("hanka", p.X(0.72), p.Y(0.03), 1.1), w=90, area=(0.5, 1.0))
    with Pn(*R[3]) as p:
        fy = hallway(p)
        A(p.X(0.14), fy, 1.15, hat=False, mood="determined", right="up", look=(1, 0))
        Hk(p.X(0.55), fy, 1.1, hat=False, flip=True, mood="think", right="chin", look=(-1, 0))
        J(p, p.X(0.78), fy, 1.0, flip=True, mood="happy")
        say(p, "Bota stála tady, v předsíni. Ten papírek dal někdo z našeho domu!", *hd("alica", p.X(0.14), fy, 1.15), w=200,
            area=(0.0, 0.55))
        say(p, "Děda, babička, Joey… a my.", *hd("hanka", p.X(0.55), fy, 1.1), w=130, area=(0.4, 1.0))
    page_end()


# =================================================================== 14 the star test
def page_startest():
    R = rows([(250, [1]), (240, [0.5, 0.5]), (260, [1])])
    with Pn(*R[0]) as p:
        chalupa_room(p)
        A(p.X(0.14), p.Y(0.03), 1.15, hat=False, mood="determined", right="point", look=(1, 0))
        deda(p.X(0.7), p.Y(0.03), 1.0, flip=True, mood="grin", right="chin", look=(-1, 0))
        say(p, "Dědo! Byl jsi to ty?", *hd("alica", p.X(0.14), p.Y(0.03), 1.15), w=110, area=(0.0, 0.5))
        say(p, "Já? Kdepak! Tak mě vyzkoušej.", *hd("deda", p.X(0.7), p.Y(0.03), 1.0), w=140, area=(0.45, 1.0))
    with Pn(*R[1]) as p:
        bg_fill(p, 0.88)
        shape([(p.X(0.12), p.Y(0.12)), (p.X(0.88), p.Y(0.14)), (p.X(0.86), p.Y(0.86)), (p.X(0.1), p.Y(0.84))], 1.0, LINE)
        stroke(star_pts(p.X(0.48), p.Y(0.5), 50, "deda"), LINE*1.8, closed=True, g=P.CIPHER_INK)
        cap(p, "Děda nakreslil hvězdičku.", w=170, where="tl")
    with Pn(*R[2]) as p:
        bg_fill(p, 0.95)
        inset(p, p.X(0.27), p.Y(0.42), 120, 120, lambda x, y: stroke(star_pts(x, y, 42, "deda"), LINE*1.6, closed=True, g=P.CIPHER_INK),
              "děda")
        inset(p, p.X(0.73), p.Y(0.42), 120, 120, lambda x, y: stroke(star_pts(x, y, 42, "jana"), LINE*1.6, g=P.CIPHER_INK),
              "papírek")
    with Pn(*R[3]) as p:
        chalupa_room(p, sewing=0.88)
        A(p.X(0.12), p.Y(0.03), 1.15, hat=False, mood="think", right="chin", look=(1, 0))
        deda(p.X(0.45), p.Y(0.03), 1.0, flip=True, mood="happy", look=(-1, 0))
        babicka(p.X(0.72), p.y + 4, 0.95, flip=True, mood="happy", look=(1, 0))
        say(p, "Děda kreslí hvězdičku obrysem. Ta na papírku je jedním tahem!", *hd("alica", p.X(0.12), p.Y(0.03), 1.15), w=200,
            area=(0.0, 0.5))
        say(p, "Vidíš? A babička v klubu nikdy nebyla. Tak kdo?", *hd("deda", p.X(0.45), p.Y(0.03), 1.0), w=170, area=(0.3, 0.75))
    page_end()


# =================================================================== 15 the costumes
def page_costumes():
    R = rows([(270, [1]), (240, [0.5, 0.5]), (240, [1])])
    with Pn(*R[0]) as p:
        chalupa_room(p, evening=True)
        sewing_corner(p.X(0.4), p.y + 4, 1.2)
        for i, (fx_, rr) in enumerate(((0.12, 20), (0.22, -30), (0.6, 50), (0.7, 0), (0.92, -40))):
            fabric_scrap(p.X(fx_), p.y + 10, 16, 9, rot=rr, seed=i + 5)
        babicka(p.X(0.18), p.Y(0.03), 1.1, mood="grin", right="up", look=(1, 0),
                item=lambda x, y: shape(ell(x + 6, y + 6, 10, 7, 20), P.COSTUME_OWL_WING, LINE*0.7))
        A(p.X(0.75), p.Y(0.03), 1.05, hat=False, flip=True, mood="wow", look=(-1, 0))
        kk(p.X(0.95), p.Y(0.45), 40)
        cap(p, "Večer babička šila kostýmy. Na zemi bylo plno ústřižků.", w=230, where="tr")
        say(p, "Tak. Sovička je hotová!", *hd("babi", p.X(0.18), p.Y(0.03), 1.1), w=110, area=(0.0, 0.5))
    with Pn(*R[1]) as p:
        chalupa_room(p, evening=True)
        alica_owl(p.X(0.45), p.Y(0.03), 1.35, mood="grin", left="wave", right="up", look=(0, 0))
        say(p, "Hú hú! Já jsem sova!", *ho(p.X(0.45), p.Y(0.03), 1.35), w=110)
    with Pn(*R[2]) as p:
        chalupa_room(p, evening=True)
        hanka_bear(p.X(0.45), p.Y(0.03), 1.5, mood="grin", look=(0, 0))
        say(p, "A já jsem medvídě!", *hb(p.X(0.45), p.Y(0.03), 1.5), w=110)
    with Pn(*R[3]) as p:
        chalupa_room(p, evening=True)
        deda(p.X(0.18), p.Y(0.03), 1.0, mood="grin", right="up", look=(1, 0))
        babicka(p.X(0.75), p.Y(0.03), 1.05, flip=True, mood="happy", look=(-1, 0))
        say(p, "A já budu zase velký medvěd!", *hd("deda", p.X(0.18), p.Y(0.03), 1.0), w=130, area=(0.0, 0.5))
        say(p, "A já musím ráno ještě něco zařídit.", *hd("babi", p.X(0.75), p.Y(0.03), 1.05), w=150, area=(0.45, 1.0))
    page_end()


# =================================================================== 16 Masopust morning
def page_morning9():
    R = rows([(270, [1]), (220, [0.5, 0.5]), (260, [1])])
    with Pn(*R[0]) as p:
        gy = p.Y(0.5)
        winter_garden(p, gy, 104, house_x=0.2, trees=((0.9, 0.8),))
        medved(p.X(0.6), p.Y(0.03), 1.0, head=False, mood="grin", right="front", look=(1, 0),
               item=lambda x, y: bear_head(x + 10, y + 2, 10))
        cap(p, "Sobota. Masopust!", w=150, where="tr")
        say(p, "Medvěd musí jít první. Uvidíme se v průvodu!", *hd("deda", p.X(0.6), p.Y(0.03), 1.0), w=170, area=(0.3, 0.95))
    with Pn(*R[1]) as p:
        winter_garden(p, p.Y(0.55), 105)
        hanka_bear(p.X(0.3), p.Y(0.03), 1.3, mood="think", look=(1, 0.2))
        J(p, p.X(0.7), p.Y(0.03), 1.0, flip=True, mood="happy")
        say(p, "A kde je babička?", *hb(p.X(0.3), p.Y(0.03), 1.3), w=100)
    with Pn(*R[2]) as p:
        winter_garden(p, p.Y(0.55), 106)
        alica_owl(p.X(0.3), p.Y(0.03), 1.05, mood="happy", right="up", look=(1, 0))
        say(p, "Musela něco zařídit. Pojďme!", *ho(p.X(0.3), p.Y(0.03), 1.05), w=160)
    with Pn(*R[3]) as p:
        gy = p.Y(0.5)
        masopust_street(p, gy, 107, church_x=0.5)
        betka_kitten(p.X(0.72), p.Y(0.03), 1.1, flip=True, mood="grin", right="wave", look=(-1, 0))
        alica_owl(p.X(0.12), p.Y(0.03), 1.05, mood="happy", look=(1, 0))
        hanka_bear(p.X(0.26), p.Y(0.03), 1.05, mood="grin", look=(1, 0))
        J(p, p.X(0.42), p.Y(0.03), 0.95, mood="happy")
        cap(p, "Na návsi se schází celá ves.", w=180, where="tr")
        say(p, "Ahoj, sovičko! Ahoj, medvídě!", *hd("betka", p.X(0.72), p.Y(0.03), 1.1), w=130, area=(0.48, 1.0))
    page_end()


# =================================================================== 17 the parade
def page_parade():
    with Pn(M, 40, W-2*M, H-80) as p:
        gy = p.Y(0.66)
        masopust_street(p, gy, 108, houses=((0.08, 0.85), (0.35, 0.75), (0.7, 0.85), (0.95, 0.8)), church_x=0.52, garlands=2)
        y1 = p.Y(0.27); k = 1.32
        muzikant(p.X(0.06), y1 + 14, k*0.95, mood="happy")
        franta(p.X(0.19), y1 + 8, k*0.92, mood="grin", right="front", look=(1, 0))
        medved(p.X(0.33), y1 + 4, k*0.95, left="up", right="up")
        stroke(bez((p.X(0.19) + 22, y1 + 82), (p.X(0.24), y1 + 60), (p.X(0.28), y1 + 66), (p.X(0.33) - 16, y1 + 78)), 1.0, g=0.3)
        kobyla(p.X(0.5), y1, k*0.95, mood="grin")
        kominik(p.X(0.68), y1 + 4, k*0.95, mood="happy", flip=True)
        baba(p.X(0.83), y1 + 2, k*0.95, flip=True, right="wave")
        slameny(p.X(0.96), y1 + 8, k*0.78, flip=True)
        alica_owl(p.X(0.08), p.Y(0.015), 1.25, mood="wow", right="point", look=(1, 0.3))
        hanka_bear(p.X(0.22), p.Y(0.015), 1.25, mood="grin", look=(1, 0.3))
        betka_kitten(p.X(0.33), p.Y(0.015), 1.25, mood="happy", look=(1, 0.3))
        J(p, p.X(0.44), p.Y(0.015), 1.1, mood="happy")
        kk(p.X(0.6), p.Y(0.1), 25)
        sfx(p.X(0.04), p.Y(0.9), "TRA-LA-LÁ!", 20, -4)
        cap(p, "Průvod! Vpředu muzikant, pak medvědář s medvědem, kobyla, kominík, bába s nůší a slaměný.", w=300, where="tr")
        cap(p, "Alica počítá: tři masky mají hvězdu. Najdeš je?", w=230, where="br")
    page_end()


# =================================================================== 18 STOP, DETEKTIVE!
def page_stop():
    with Pn(M, 40, W-2*M, H-80, bg=0.95) as p:
        title(p.X(0.5), p.Y(0.92), "STOP, DETEKTIVE!", 44)
        hand_text(p.X(0.05), p.Y(0.86), p.w*0.9, "Kdo napsal tajné zprávy? Ukaž prstem na masku!", "SHB", 18)
        cw, ch = p.w*0.3, p.h*0.2
        items = [
            ("papírek má zoubky (strana 3)", lambda x, y: slip(x, y + 30, 60, 30, ["HLEDEJ"], 8)),
            ("Joey čichal papírek (strana 3)", lambda x, y: (joey(x - 14, y + 2, 0.55, pose="sniff", shadow=False),
                                                         [lavender_sprig(x + 8 + i*10, y + 30 + (i % 2)*6, 1.2, -10 + i*10) for i in range(3)])),
            ("kdo poznal D bez klíče? (strana 5)", lambda x, y: glyph("D", x, y + 8, 44, "jana")),
            ("kdo vybral knížku? (strana 8)", lambda x, y: book(x, y + 24, 1.2)),
            ("papírek v botě (strana 13)", lambda x, y: boot(x - 8, y + 6, 0.55)),
            ("hvězdička jedním tahem (strana 14)", lambda x, y: stroke(star_pts(x, y + 30, 22, "jana"), LINE*1.4, g=P.CIPHER_INK)),
        ]
        for i, (txt, pic) in enumerate(items):
            cx = p.X(0.04) + (i % 3)*(cw + p.w*0.02); cy = p.Y(0.82) - (i//3 + 1)*(ch + 10)
            shape(rrect(cx, cy, cw, ch, 8), 1.0, 1.2)
            hand_text(cx + 6, cy + ch - 20, 30, str(i + 1), "SHB", 16, align="left")
            with T(cx + cw/2, cy + 36, 1.4):
                pic(0, 0)
            hand_text(cx + 8, cy + 14, cw - 16, txt, "SH", 10.5, lead=12)
        by = p.Y(0.82) - 2*(ch + 10) - 150
        shape(rrect(p.X(0.04), by, p.w*0.92, 140, 8), 1.0, 1.2)
        for i, (fn, lbl) in enumerate(((lambda x, y: kobyla(x, y, 0.85, mood="grin"), "kobyla"),
                                       (lambda x, y: kominik(x, y, 0.85, flip=True), "kominík"),
                                       (lambda x, y: baba(x, y, 0.85, flip=True), "bába s nůší"))):
            fx = p.X(0.2 + i*0.3)
            fn(fx, by + 22)
            hand_text(fx - 50, by + 6, 100, lbl, "SHB", 12)
        hand_text(p.X(0.05), by - 30, p.w*0.9, "Nápověda: kdo šil kostýmy? A co voní levandulí?", "SH", 14)
        with T(p.X(0.5), p.Y(0.03), 1.0, rot=180):
            hand_text(-p.w*0.45, 0, p.w*0.9, "Bába s nůší je babička! Zoubky dělají babiččiny nůžky, levandule je její krém,", "SH", 12)
            hand_text(-p.w*0.45, -15, p.w*0.9, "písmeno D poznala bez klíče, knížku vybrala ona a hvězdičky kreslí jedním tahem.", "SH", 12)
    page_end()


# =================================================================== 19 kobyla and kominík
def page_masks():
    R = rows([(270, [1]), (230, [0.5, 0.5]), (250, [1])])
    with Pn(*R[0]) as p:
        gy = p.Y(0.55)
        masopust_street(p, gy, 109, garlands=1)
        kobyla(p.X(0.2), p.Y(0.03), 1.05, mood="grin", look=(1, 0))
        alica_owl(p.X(0.86), p.Y(0.03), 1.1, flip=True, mood="think", right="chin", look=(-1, 0))
        hanka_bear(p.X(0.7), p.Y(0.03), 1.05, flip=True, mood="grin", right="point", look=(-1, 0))
        say(p, "Ijááá! Hádejte, kdo jsem!", *hd("tonda", p.X(0.2), p.Y(0.03), 1.05), w=120, area=(0.0, 0.5))
        say(p, "Tonda! Má tenisky!", *hb(p.X(0.7), p.Y(0.03), 1.05), w=100, area=(0.45, 1.0))
    with Pn(*R[1]) as p:
        masopust_street(p, p.Y(0.6), 110, houses=((0.5, 0.8),))
        alica_owl(p.X(0.25), p.Y(0.03), 1.0, mood="think", right="chin", look=(1, 0))
        say(p, "Kobyla má hvězdu. Ale Tonda naše písmo neumí.", *ho(p.X(0.25), p.Y(0.03), 1.0), w=190)
    with Pn(*R[2]) as p:
        masopust_street(p, p.Y(0.6), 111, houses=((0.3, 0.8),))
        kominik(p.X(0.72), p.Y(0.03), 1.0, flip=True, mood="happy")
        J(p, p.X(0.35), p.Y(0.03), 1.1, pose="sniff", mood="happy")
        joey_smell(p, p.X(0.55), p.Y(0.45), "flour", 3, 7)
        cap(p, "Joey čichá ke kominíkovi: mouka.", w=170, where="tl")
    with Pn(*R[3]) as p:
        gy = p.Y(0.55)
        masopust_street(p, gy, 112, garlands=1)
        kominik(p.X(0.75), p.Y(0.03), 1.05, flip=True, mood="grin", right="up", look=(-1, 0))
        alica_owl(p.X(0.14), p.Y(0.03), 1.1, mood="happy", look=(1, 0))
        say(p, "Kominík je Věrka! A hvězda na klobouku byla to překvapení.", *ho(p.X(0.14), p.Y(0.03), 1.1), w=190, area=(0.0, 0.55))
        say(p, "Uhodla jsi! Ale zprávy jsem nepsala.", *hk(p.X(0.75), p.Y(0.03), 1.05), w=150, area=(0.5, 1.0))
    page_end()


# =================================================================== 20 the bába
def page_baba():
    R = rows([(280, [1]), (230, [0.5, 0.5]), (240, [1])])
    with Pn(*R[0]) as p:
        gy = p.Y(0.55)
        masopust_street(p, gy, 113, garlands=1)
        baba(p.X(0.66), p.Y(0.03), 1.1, flip=True, right="wave", look=(-1, 0))
        hanka_bear(p.X(0.25), p.Y(0.03), 1.2, mood="wow", right="point", look=(1, 0.4))
        kk(p.X(0.95), p.Y(0.08), -25)
        cap(p, "Bába s nůší tancuje mezi lidmi.", w=170, where="tr")
        say(p, "Ta bába má zoubky! Na šátku!", *hb(p.X(0.25), p.Y(0.03), 1.2), w=130, area=(0.0, 0.5))
    with Pn(*R[1]) as p:
        bg_fill(p, 0.95)
        def zz(x, y):
            pts = [(x - 40, y + 20), (x + 40, y + 20)] + zigzag((x + 40, y - 10), (x - 40, y - 10), 5, inward=1)
            shape([(x - 40, y + 20), (x + 40, y + 20), (x + 40, y - 10)] + zigzag((x + 40, y - 10), (x - 40, y - 10), 5)[1:], P.SHAWL, LINE)
        inset(p, p.X(0.27), p.Y(0.5), 120, 110, zz, "šátek")
        inset(p, p.X(0.73), p.Y(0.5), 120, 110, lambda x, y: slip(x, y, 80, 46, ["HLEDEJ"], 11), "papírek")
        cap(p, "Stejné zoubky!", w=120, where="tl")
    with Pn(*R[2]) as p:
        masopust_street(p, p.Y(0.6), 114, houses=((0.3, 0.8),))
        baba(p.X(0.7), p.Y(0.03), 1.0, flip=True, look=(-1, -0.3))
        J(p, p.X(0.32), p.Y(0.03), 1.1, mood="happy")
        joey_smell(p, p.X(0.5), p.Y(0.48), "lavender", 4, 9)
        cap(p, "Joey vrtí ocasem. Levandule!", w=160, where="tl")
    with Pn(*R[3]) as p:
        gy = p.Y(0.55)
        masopust_street(p, gy, 115, garlands=1)
        alica_owl(p.X(0.12), p.Y(0.03), 1.1, mood="wow", right="point", look=(1, 0))
        baba(p.X(0.72), p.Y(0.03), 1.05, flip=True, mask=False, mood="grin", right="up", look=(-1, 0),
             item=lambda x, y: (shape(ell(x + 4, y + 6, 8, 9, 24), P.BABA_MASK, LINE*0.7)))
        say(p, "Hvězda, zoubky, levandule. A pod šátkem drdol… Babičko!", *ho(p.X(0.12), p.Y(0.03), 1.1), w=200, area=(0.0, 0.55))
        say(p, "Našly jste mě, detektivky!", *hbb(p.X(0.72), p.Y(0.03), 1.05), w=130, area=(0.5, 1.0))
    page_end()


# =================================================================== 21 babička tells
def page_tells():
    R = rows([(260, [1]), (240, [0.5, 0.5]), (250, [1])])
    with Pn(*R[0]) as p:
        gy = p.Y(0.55)
        masopust_street(p, gy, 116, garlands=1)
        baba(p.X(0.45), p.Y(0.03), 0.95, mask=False, mood="happy", look=(1, 0), nuse=False)
        alica_owl(p.X(0.82), p.Y(0.03), 1.05, flip=True, mood="surprised", look=(-1, 0))
        hanka_bear(p.X(0.94), p.Y(0.03), 1.0, flip=True, mood="happy", look=(-1, 0))
        say(p, "Ty zprávy jsem psala já. Hvězdičkovým písmem.", *hbb(p.X(0.45), p.Y(0.03), 0.95), w=200, area=(0.1, 0.68))
        say(p, "Ale ty jsi v klubu nebyla!", *ho(p.X(0.82), p.Y(0.03), 1.05), w=110, area=(0.62, 1.0))
    with Pn(*R[1]) as p:
        masopust_street(p, p.Y(0.6), 117, houses=((0.5, 0.8),))
        baba(p.X(0.25), p.Y(0.03), 0.88, mask=False, mood="happy", look=(1, 0.3), nuse=False)
        say(p, "Nebyla. Ale jednou jsem takovou zprávu dostala. Před šedesáti lety.", *hbb(p.X(0.25), p.Y(0.03), 0.88), w=200)
    with Pn(*R[2]) as p:
        masopust_street(p, p.Y(0.6), 118, houses=((0.5, 0.8),))
        hanka_bear(p.X(0.4), p.Y(0.03), 1.45, mood="wow", look=(1, 0.3))
        say(p, "Vyprávěj!", *hb(p.X(0.4), p.Y(0.03), 1.45), w=90)
    with Pn(*R[3]) as p:
        fy = library(p, 0.1, seed=11)
        young(p.X(0.4), fy, 1.3, "jana", mood="surprised", right="front", look=(1, -0.3),
              item=lambda x, y: book(x + 12, y - 6, 0.8, rot=10))
        slip(p.X(0.58), p.Y(0.42), 60, 26, ["PRIJD"], 8, rot=-15, style="deda")
        memory_frame(p)
        cap(p, "Před šedesáti lety. Malá Jana si půjčila v knihovně knížku…", w=230, where="tl")
        say(p, "Papírek! Samé hvězdičky a tečky!", *hd("young", p.X(0.4), fy, 1.3), w=140, area=(0.45, 1.0))
    page_end()


# =================================================================== 22 the flashback
def page_flash():
    R = rows([(250, [0.5, 0.5]), (250, [1]), (250, [1])])
    with Pn(*R[0]) as p:
        bedroom_night(p, window=False)
        young(p.X(0.4), p.Y(0.03), 1.4, "jana", mood="think", right="front", look=(1, -0.3),
              item=lambda x, y: slip(x + 12, y + 4, 40, 20, ["BUDU"], 6, rot=8, style="deda"))
        fill([(p.X(0.78), p.Y(0.03) + 70), (p.X(0.62), p.Y(0.03)), (p.X(0.96), p.Y(0.03))], P.LANTERN_GLOW, 0.3)
        shape([(p.X(0.76), p.Y(0.03)), (p.X(0.8), p.Y(0.03)), (p.X(0.8), p.Y(0.03) + 60), (p.X(0.76), p.Y(0.03) + 60)], 0.4, LINE)
        shape(bez((p.X(0.72), p.Y(0.03) + 56), (p.X(0.74), p.Y(0.03) + 74), (p.X(0.82), p.Y(0.03) + 74), (p.X(0.84), p.Y(0.03) + 56)) +
              [(p.X(0.72), p.Y(0.03) + 56)], P.LANTERN_GLOW, LINE)
        memory_frame(p)
        cap(p, "Klíč neměla. Luštila sama, celý týden.", w=170, where="tl")
    with Pn(*R[1]) as p:
        bg_fill(p, 0.95)
        slip(p.X(0.5), p.Y(0.5), 180, 90, ["PRIJD NA", "MASOPUST", "BUDU MEDVED"], 18, style="deda")
        keep_clear(p, p.X(0.5) - 95, p.Y(0.5) - 50, p.X(0.5) + 95, p.Y(0.5) + 50)
        memory_frame(p)
        cap(p, "„Přijď na Masopust. Budu medvěd.“", w=180, where="tl")
    with Pn(*R[2]) as p:
        gy = p.Y(0.55)
        masopust_street(p, gy, 119, garlands=1)
        young_bear(p.X(0.4), p.Y(0.04), 1.25, left="up", right="up")
        young(p.X(0.6), p.Y(0.04), 1.25, "jana", flip=True, mood="grin", left="up", right="up", look=(-1, 0.2))
        sfx(p.X(0.05), p.Y(0.85), "TRA-LA-LÁ!", 18, -5)
        memory_frame(p)
        cap(p, "Na Masopustu tancoval medvěd jen s jednou holčičkou.", w=230, where="tr")
    with Pn(*R[3]) as p:
        gy = p.Y(0.55)
        masopust_street(p, gy, 120, garlands=1)
        young_bear(p.X(0.35), p.Y(0.04), 1.3, head=False, mood="grin", right="front", look=(1, 0),
                   item=lambda x, y: bear_head(x + 6, y + 2, 8))
        young(p.X(0.65), p.Y(0.04), 1.3, "jana", flip=True, mood="wow", look=(-1, 0))
        memory_frame(p)
        say(p, "Tys to rozluštila! Sama!", *hd("young", p.X(0.35), p.Y(0.04), 1.3), w=120, area=(0.0, 0.5))
        say(p, "Honzo!", *hd("young", p.X(0.65), p.Y(0.04), 1.3), w=80, area=(0.5, 1.0))
    page_end()


# =================================================================== 23 back in the present: the bear
def page_bear():
    R = rows([(270, [1]), (220, [0.5, 0.5]), (260, [1])])
    with Pn(*R[0]) as p:
        gy = p.Y(0.55)
        masopust_street(p, gy, 121, garlands=1)
        baba(p.X(0.25), p.Y(0.03), 1.1, mask=False, mood="happy", right="front", look=(1, 0), nuse=False,
             item=lambda x, y: slip(x + 14, y + 6, 46, 22, ["PRIJD"], 6, rot=8, old=True, style="deda"))
        alica_owl(p.X(0.7), p.Y(0.03), 1.05, flip=True, mood="wow", look=(-1, 0))
        say(p, "Ten papírek mám schovaný dodnes.", *hbb(p.X(0.25), p.Y(0.03), 1.1), w=150, area=(0.0, 0.5))
        say(p, "Babi, ty jsi byla první detektivka!", *ho(p.X(0.7), p.Y(0.03), 1.05), w=140, area=(0.5, 1.0))
    with Pn(*R[1]) as p:
        masopust_street(p, p.Y(0.6), 122, houses=((0.5, 0.8),))
        hanka_bear(p.X(0.4), p.Y(0.03), 1.4, mood="think", look=(1, 0.3))
        say(p, "A kde je ten medvěd?", *hb(p.X(0.4), p.Y(0.03), 1.4), w=110)
    with Pn(*R[2]) as p:
        masopust_street(p, p.Y(0.6), 123, houses=((0.5, 0.8),))
        medved(p.X(0.55), p.Y(0.03), 1.1, left="up", right="up")
        sfx(p.X(0.08), p.Y(0.8), "BRUMMM!", 20, -6)
    with Pn(*R[3]) as p:
        gy = p.Y(0.55)
        masopust_street(p, gy, 124, garlands=1)
        medved(p.X(0.38), p.Y(0.03), 1.05, head=False, mood="grin", right="front", look=(1, 0),
               item=lambda x, y: bear_head(x + 10, y + 2, 10))
        baba(p.X(0.62), p.Y(0.03), 1.0, flip=True, mask=False, mood="grin", look=(-1, 0), nuse=False)
        hanka_bear(p.X(0.12), p.Y(0.03), 1.1, mood="grin", look=(1, 0))
        say(p, "Velký medvěd a malé medvídě!", *hb(p.X(0.12), p.Y(0.03), 1.1), w=120, area=(0.0, 0.32))
        say(p, "Ahoj, Jano.", *hd("deda", p.X(0.38), p.Y(0.03), 1.05), w=80, area=(0.2, 0.55))
        say(p, "Ahoj, medvěde.", *hbb(p.X(0.62), p.Y(0.03), 1.0), w=90, area=(0.5, 0.9))
    page_end()


# =================================================================== 24 the dance
def page_dance():
    R = rows([(280, [1]), (220, [0.5, 0.5]), (250, [1])])
    with Pn(*R[0]) as p:
        gy = p.Y(0.55)
        masopust_street(p, gy, 125, garlands=2)
        muzikant(p.X(0.12), p.Y(0.03), 0.95, mood="happy")
        medved(p.X(0.45), p.Y(0.03), 1.05, left="up", right="up")
        baba(p.X(0.65), p.Y(0.03), 1.0, flip=True, mask=False, mood="grin", left="up", right="up", look=(-1, 0.2))
        sfx(p.X(0.8), p.Y(0.85), "TRA-LA-LÁ!", 18, 5)
        cap(p, "Medvěd tančí s bábou. Jako před šedesáti lety.", w=210, where="tl")
    with Pn(*R[1]) as p:
        masopust_street(p, p.Y(0.6), 126, houses=((0.5, 0.8),))
        hanka_bear(p.X(0.3), p.Y(0.03), 1.3, mood="grin", left="up", right="up", monkey=False)
        J(p, p.X(0.68), p.Y(0.03), 1.05, flip=True, mood="happy")
        say(p, "Já taky tancuju!", *hb(p.X(0.3), p.Y(0.03), 1.3), w=100)
    with Pn(*R[2]) as p:
        masopust_street(p, p.Y(0.6), 127, houses=((0.5, 0.8),))
        kobyla(p.X(0.32), p.Y(0.03), 0.85, mood="grin", mask=False)
        betka_kitten(p.X(0.72), p.Y(0.03), 1.1, flip=True, mood="grin", left="up", right="up")
        sfx(p.X(0.06), p.Y(0.88), "IJÁÁÁ!", 15, -6)
    with Pn(*R[3]) as p:
        gy = p.Y(0.55)
        masopust_street(p, gy, 128, garlands=2)
        for i, (fn, fx_) in enumerate(((lambda x, y: alica_owl(x, y, 1.0, mood="grin", left="up", right="up"), 0.08),
                                      (lambda x, y: kominik(x, y, 0.9, mood="grin", right="up", stick=False), 0.25),
                                      (lambda x, y: franta(x, y, 0.85, mood="grin", right="up"), 0.42),
                                      (lambda x, y: slameny(x, y, 0.75), 0.58),
                                      (lambda x, y: knihovnice(x, y, 0.9, mood="grin", right="up", left="up"), 0.74),
                                      (lambda x, y: jezevcik(x, y, 1.0, pose="up"), 0.9))):
            fn(p.X(fx_), p.Y(0.03))
        kk(p.X(0.96), p.Y(0.5), 15)
        cap(p, "Tančila celá ves.", w=140, where="tr")
    page_end()


# =================================================================== 25 koblihy
def page_koblihy():
    R = rows([(280, [1]), (220, [0.5, 0.5]), (250, [1])])
    with Pn(*R[0]) as p:
        gy = p.Y(0.55)
        masopust_street(p, gy, 129, garlands=1)
        tx0, tx1, ty = p.X(0.05), p.X(0.95), p.Y(0.2)
        Td(p.X(0.18), p.Y(0.06), 1.05, hat=False, mood="grin", right="up", look=(1, 0), item=lambda x, y: koblih(x, y + 4, 0.9, bitten=True))
        baba(p.X(0.78), p.Y(0.06), 1.05, flip=True, mask=False, mood="happy", look=(-1, 0), nuse=False)
        shape([(tx0, ty), (tx1, ty), (tx1, ty + 6), (tx0, ty + 6)], P.SHELF, BG)
        shape([(tx0 + 4, p.y + 4), (tx1 - 4, p.y + 4), (tx1 - 4, ty), (tx0 + 4, ty)], P.KOBYLA_SKIRT, BG)
        for k_ in range(9): koblih(tx0 + 40 + k_*52, ty + 12, 1.1)
        cap(p, "Po tanci byly koblihy. Pro celou ves.", w=190, where="tl")
        say(p, "Babičko, naučíš mě hvězdičkové písmo?", *hd("tonda", p.X(0.18), p.Y(0.06), 1.05), w=170, area=(0.0, 0.6))
        say(p, "Klíč má Alica. Ta tě to naučí.", *hbb(p.X(0.78), p.Y(0.06), 1.05), w=130, area=(0.55, 1.0))
    with Pn(*R[1]) as p:
        masopust_street(p, p.Y(0.6), 130, houses=((0.5, 0.8),))
        alica_owl(p.X(0.35), p.Y(0.03), 1.25, mood="happy", right="front", look=(1, 0), item=lambda x, y: koblih(x + 4, y, 0.8))
        say(p, "Babi, nechceš do našeho klubu?", *ho(p.X(0.35), p.Y(0.03), 1.25), w=140)
    with Pn(*R[2]) as p:
        masopust_street(p, p.Y(0.6), 131, houses=((0.5, 0.8),))
        baba(p.X(0.25), p.Y(0.03), 0.88, mask=False, mood="grin", look=(1, 0), nuse=False)
        say(p, "Kdepak. Klub má sedm členů. Já jsem první detektivka.", *hbb(p.X(0.25), p.Y(0.03), 0.88), w=200)
    with Pn(*R[3]) as p:
        gy = p.Y(0.55)
        masopust_street(p, gy, 132, garlands=1)
        medved(p.X(0.12), p.Y(0.03), 0.92, head=False, mood="grin", right="up", look=(1, 0))
        franta(p.X(0.27), p.Y(0.03), 0.85, mood="grin", right="up", look=(1, 0))
        kominik(p.X(0.41), p.Y(0.03), 0.88, mood="grin", right="up", stick=False)
        alica_owl(p.X(0.55), p.Y(0.03), 0.95, mood="grin", right="up")
        hanka_bear(p.X(0.66), p.Y(0.03), 0.95, mood="grin", right="up", monkey=False)
        kobyla(p.X(0.8), p.Y(0.03), 0.7, mood="grin", mask=False, right="up")
        betka_kitten(p.X(0.95), p.Y(0.03), 0.95, flip=True, mood="grin", right="up")
        say(p, "Klub Hvězdička má zase tajné písmo!", *hd("deda", p.X(0.12), p.Y(0.03), 0.92), w=170, area=(0.0, 0.6))
        sfx(p.X(0.62), p.Y(0.85), "HURÁ!", 22, 5)
    page_end()


# =================================================================== 26 evening: the answer; back to school
def page_end9():
    R = rows([(250, [1]), (240, [0.5, 0.5]), (260, [1])])
    with Pn(*R[0]) as p:
        chalupa_room(p, evening=True)
        shape([(p.X(0.03), p.Y(0.32)), (p.X(0.97), p.Y(0.32)), (p.X(0.97), p.Y(0.36)), (p.X(0.03), p.Y(0.36))], 0.5, BG)
        notebook(p.X(0.25), p.Y(0.37), 1.3)
        A(p.X(0.5), p.Y(0.03), 1.15, hat=False, mood="think", right="front", look=(-1, -0.4))
        Hk(p.X(0.7), p.Y(0.03), 1.05, hat=False, flip=True, mood="happy", look=(-1, -0.3))
        cap(p, "Večer napsala Alica babičce odpověď. Hvězdičkovým písmem.", w=230, where="tr")
    with Pn(*R[1]) as p:
        bg_fill(p, 0.88)
        big_slip(p, p.X(0.5), p.Y(0.5), ["DIKY", "BABI"], gh=24, rot=-3)
        cap(p, "Umíš to přečíst?", w=130, where="tl")
    with Pn(*R[2]) as p:
        chalupa_room(p, evening=True)
        babicka(p.X(0.4), p.Y(0.03), 1.15, mood="happy", right="front", look=(1, 0.2),
                item=lambda x, y: slip(x + 10, y + 6, 40, 20, ["DIKY"], 6, rot=6))
        say(p, "To je ta nejhezčí zpráva.", *hd("babi", p.X(0.4), p.Y(0.03), 1.15), w=120)
    with Pn(*R[3]) as p:
        chalupa_room(p, evening=True)
        deda(p.X(0.15), p.Y(0.03), 1.0, mood="happy", look=(1, 0))
        A(p.X(0.65), p.Y(0.03), 1.1, hat=False, flip=True, mood="grin", right="up", look=(-1, 0))
        Hk(p.X(0.82), p.Y(0.03), 1.05, hat=False, flip=True, mood="sleepy", right="hug", look=(-1, 0))
        say(p, "Zítra končí prázdniny. Jedete domů a v pondělí do školy.", *hd("deda", p.X(0.15), p.Y(0.03), 1.0), w=190,
            area=(0.0, 0.55))
        say(p, "Snad bude i ve škole nějaká záhada!", *hd("alica", p.X(0.65), p.Y(0.03), 1.1), w=150, area=(0.5, 1.0))
    page_end()


# =================================================================== 27 activity (no pencil)
def page_quiz():
    with Pn(M, 40, W-2*M, H-80) as p:
        box = [(p.X(0.05), p.Y(0.905)), (p.X(0.95), p.Y(0.91)), (p.X(0.95), p.Y(0.905)+54), (p.X(0.05), p.Y(0.905)+52)]
        fill(box, 0.92)
        for a_, b_ in ((0, 1), (1, 2), (2, 3), (3, 0)): stroke([box[a_], box[b_]], 1.5)
        hand_text(p.X(0.05), p.Y(0.905)+18, p.w*0.9, "Detektivní zápisník", "SHB", 26)
        hand_text(p.X(0.05), p.Y(0.865), p.w*0.9, "Dnes bez tužky. Stačí prst a dobré oči!", "SH", 13)
        hand_text(p.X(0.05), p.Y(0.82), p.w*0.9, "1. Přečti prstem tajné zprávy. Klíč je na straně 7.", "SHB", 15, align="left")
        msgs = ["KOBLIH", "BABI SIJE", "JOEY CICHA"]
        for i, m_ in enumerate(msgs):
            cipher_text(m_, p.X(0.08), p.Y(0.73) - i*48, 34, style="deda")
        y2 = p.Y(0.73) - 3*48 + 6
        hand_text(p.X(0.05), y2, p.w*0.9, "2. Kdo je pod maskou? Ukaž prstem, kdo k sobě patří.", "SHB", 15, align="left")
        masks = [lambda x, y: medved(x, y, 0.62, shadow=False), lambda x, y: kobyla(x, y, 0.62, shadow=False),
                 lambda x, y: kominik(x, y, 0.62, shadow=False, stick=False), lambda x, y: baba(x, y, 0.62, shadow=False)]
        faces = [lambda x, y: babicka(x, y, 0.68, shadow=False, mood="happy"), lambda x, y: deda(x, y, 0.62, shadow=False, mood="happy"),
                 lambda x, y: verka_old(x, y, 0.66, shadow=False, stick=False, mood="happy"), lambda x, y: tonda(x, y, 0.72, shadow=False, mood="grin")]
        for i in range(4):
            masks[i](p.X(0.14 + i*0.24), y2 - 100)
            hand_text(p.X(0.14 + i*0.24) - 30, y2 - 114, 60, "ABCD"[i], "SHB", 14)
            faces[i](p.X(0.14 + i*0.24), y2 - 206)
            hand_text(p.X(0.14 + i*0.24) - 30, y2 - 220, 60, str(i + 1), "SHB", 14)
        y3 = y2 - 246
        hand_text(p.X(0.05), y3, p.w*0.9, "3. Povídejte si:", "SHB", 15, align="left")
        qs = ["Proč měl papírek zoubky?", "Jak Joey poznal babičku?", "Proč to nemohl napsat děda?"]
        for i, q in enumerate(qs):
            hand_text(p.X(0.1), y3 - 22 - i*20, p.w*0.85, "– " + q, "SH", 14, align="left")
        y4 = y3 - 22 - 3*20 - 16
        hidden_koblih(p.X(0.09), y4 - 6, 13)        # the legend: not one of the hidden ten
        hand_text(p.X(0.14), y4 - 4, p.w*0.82,
                  f"Babička schovala v sešitě {N_HIDDEN} koblížků, jako je tenhle (ten se nepočítá). Najdeš je všechny?",
                  "SHB", 14, align="left", lead=18)
        pages = ", ".join(map(str, HID[:-1])) + " a " + str(HID[-1]) if HID else ""
        with T(p.X(0.5), p.Y(0.015), 1.0, rot=180):
            hand_text(-p.w*0.45, 0, p.w*0.9, f"Koblížky jsou na stranách {pages}.", "SH", 10)
            hand_text(-p.w*0.45, -13, p.w*0.9, "Zprávy: KOBLIH, BABI ŠIJE, JOEY ČICHÁ. Masky: A2, B4, C3, D1.", "SH", 10)
    page_end()


# =================================================================== 28 back cover: next time
def back_cover():
    with Pn(M, 40, W-2*M, H-80, bg=0.95) as p:
        hand_text(p.X(0.1), p.Y(0.93), p.w*0.8, "Příště v sešitě č. 10:", "SHB", 20)
        title(p.X(0.5), p.Y(0.84), "ZÁHADA VE ŠKOLE", 34)
        with Pn(p.X(0.08), p.Y(0.3), p.w*0.84, p.h*0.48, bg=0.9) as q:
            gy = q.Y(0.45)
            sky(q, P.NOV_SKY)
            sh_([(q.X(0.04), gy), (q.X(0.96), gy), (q.X(0.96), q.Y(0.86)), (q.X(0.04), q.Y(0.86))], 0.85)
            sh_([(q.X(0.0), q.Y(0.86)), (q.X(1.0), q.Y(0.86)), (q.X(0.96), q.Y(0.97)), (q.X(0.04), q.Y(0.97))], 0.45)
            for i in range(7):
                wx = q.X(0.08 + i*0.125)
                for wy in (q.Y(0.52), q.Y(0.7)):
                    shape([(wx, wy), (wx + 22, wy), (wx + 22, wy + 22), (wx, wy + 22)], 0.65, LINE*0.6)
            shape([(q.X(0.4), q.Y(0.9) - 2), (q.X(0.6), q.Y(0.9) - 2), (q.X(0.6), q.Y(0.9) + 14), (q.X(0.4), q.Y(0.9) + 14)], 1.0, LINE*0.6)
            hand_text(q.X(0.4), q.Y(0.9) + 1, q.w*0.2, "ŠKOLA", "SHB", 11)
            ground(q, gy, P.GRASS)
            kotec(q.X(0.32), q.Y(0.08), 2.1)
            morce(q.X(0.12), q.Y(0.05), 1.7)
            for k_ in range(8):
                stroke([(q.X(0.56) + k_*16, q.Y(0.08) + (k_ % 2)*5), (q.X(0.56) + k_*16 + 8, q.Y(0.08) + (k_ % 2)*5 + 3)], LINE*1.8, g=P.STRAW_DARK)
            hand_text(q.X(0.8), q.Y(0.2), q.w*0.18, "???", "SHB", 30)
        hand_text(p.X(0.1), p.Y(0.24), p.w*0.8, "Ze školního kotce zmizelo morče! Dvířka jsou otevřená a trávou vede stopa ze sena.", "SH", 16, lead=21)
        hand_text(p.X(0.1), p.Y(0.13), p.w*0.8, "A do školy přijdou máma s tátou.", "SHB", 16)
        hand_text(p.X(0.1), p.Y(0.015), p.w*0.8, "Velká a malá detektivka – sešit č. 9", "SH", 13, g=0.35)
    PAGE[0] += 1; cv.showPage()


cover(); page_cast(); page_slip(); page_code(); page_decode(); page_old(); page_key(); page_library(); page_card()
page_tonda(); page_franta(); page_verka(); page_boot(); page_startest(); page_costumes(); page_morning9(); page_parade()
page_stop(); page_masks(); page_baba(); page_tells(); page_flash(); page_bear(); page_dance(); page_koblihy(); page_end9()
page_quiz(); back_cover()
cv.save()
print("ok", PAGE[0] - 1, "pages")
import letter
if letter.MISSING: PROBLEMS.append("no glyph in the font for: " + " ".join(sorted(letter.MISSING)))
if len(HID) != N_HIDDEN: PROBLEMS.append(f"{len(HID)} hidden koblížky drawn, the notebook promises {N_HIDDEN}")
for pr in PROBLEMS: print("ORDER/LAYOUT:", pr)
if PROBLEMS: sys.exit(1)
