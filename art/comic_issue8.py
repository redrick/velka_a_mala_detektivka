"""Velká a malá detektivka, issue 8: Stopy ve sněhu (outline: vault topics/comic-series/issue8-outline)"""
import os, sys
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
import math, random
import lib
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
import chars3

W, H = A4
M = 28; GUT = 9; TOP = H - 30
OUT = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                   "comics", "velka_a_mala_detektivka", "08_stopy_ve_snehu.pdf")
os.makedirs(os.path.dirname(OUT), exist_ok=True)
cv = canvas.Canvas(OUT, pagesize=A4); lib.set_canvas(cv)
cv.setTitle("Velká a malá detektivka – Případ č. 8: Stopy ve sněhu")
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


def _bubble_h(txt, w, size=14.5, font="SH"):
    return len(lines_of(txt, font, size, w - 30))*size*1.15 + 16


def say(p, txt, tx, ty, w=150, x=None, y=None, area=None, **kw):
    """speech balloon. Without x/y it places itself in reading order: on the row of the previous
    caption/balloon but to its right, or lower down; never over an earlier balloon or a speaker's
    face; as close above its speaker as that allows. area=(f0, f1) limits it horizontally."""
    h = _bubble_h(txt, w)
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
HID = []   # pages with a hidden carrot, in order; the notebook's answer key is built from it
N_HIDDEN = 10


def kc(x, y, rot=-30):
    """one of the 10 hidden carrots (see tracks.hidden_carrot)"""
    hidden_carrot(x, y, 13, rot)
    HID.append(PAGE[0])


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


# =================================================================== 1 COVER
def cover():
    with Pn(M, 40, W-2*M, H-80) as p:
        gy = p.Y(0.52)
        sm = garden8(p, gy, 81, k=2.0, noses=["stub", "none", "none", "none"], gap=0.9, dog=False,
                     fx=[(0.2, 1.45, "deda"), (0.52, 1.1, "betka")], base=p.Y(0.3))
        trail("srnka", [(p.X(0.9), gy - 10), (p.X(0.7), p.Y(0.36)), (p.X(0.44), p.Y(0.3)), (p.X(0.3), p.Y(0.26))], 1.6)
        trail("zajic", [(p.X(0.02), p.Y(0.45)), (p.X(0.3), p.Y(0.42)), (p.X(0.98), p.Y(0.47))], 1.3)
        trail("liska", [(p.X(0.98), p.Y(0.2)), (p.X(0.55), p.Y(0.18)), (p.X(0.05), p.Y(0.24))], 1.4)
        J(p, p.X(0.5), p.Y(0.05), 2.1, pose="sniff", mood="happy")
        A(p.X(0.12), p.Y(0.03), 2.0, mood="think", right="lens", lens=True, look=(1, -0.4))
        Hk(p.X(0.86), p.Y(0.03), 1.95, flip=True, mood="wow", right="point", look=(-1, -0.2),
           left="hug")
    box = [(M+34, H-236), (W-M-30, H-232), (W-M-34, H-48), (M+30, H-52)]
    fill([(x+3, y-3) for x, y in box], 0.0, 0.25); fill(box, 1.0)
    for a_, b_ in ((0, 1), (1, 2), (2, 3), (3, 0)): stroke([box[a_], box[b_]], 1.8)
    series_title(W/2, H-98, H-160, 40, 66)
    hand_text(M+40, H-190, W-2*M-80, "Alica, Hanka a Joey", "SHB", 20)
    hand_text(M+40, H-217, W-2*M-80, "Případ č. 8: Stopy ve sněhu", "SH", 15)
    magnifier(M+82, H-120, ang=-30, r=17)
    deer_print(W-M-100, H-118, 3.4, 10, ink=True)
    page_end()


# =================================================================== 2 WHO IS WHO
def page_cast():
    with Pn(M, 40, W-2*M, H-80) as p:
        hand_text(p.X(0.05), p.Y(0.95), p.w*0.9, "Kdo je kdo", "SHB", 28)
        cells = [
            ("Alica", "Lupa a zápisník.", lambda x, y: A(x, y, 0.9, hat=False, mood="happy", right="lens", lens=True)),
            ("Hanka", "Opička a baterka.", lambda x, y: Hk(x, y, 1.1, hat=False, mood="grin", right="hug")),
            ("Joey", "Nejlepší nos na světě.", lambda x, y: joey(x, y, 1.2, mood="happy")),
            ("Babička a děda", "Chalupa, kakao a lopata.", lambda x, y: (babicka(x - 22, y, 0.72, mood="happy"),
                                                                     deda(x + 22, y, 0.66, mood="happy"))),
            ("Bětka", "Staví nejlepší sněhuláky.", lambda x, y: betka(x, y, 1.0, mood="happy")),
            ("Tonda", "Ví všechno. Skoro.", lambda x, y: Td(x, y, 0.88, mood="grin")),
            ("Pan hajný", "Zná každou stopu v lese.", lambda x, y: hajny(x, y, 0.72, mood="happy")),
            ("Sněhuláci", "Mají nosy z pastináku.", lambda x, y: (snowman_b(x - 18, y, 0.95), snowman_b(x + 20, y, 0.75))),
            ("???", "Kdo chodí v noci?", lambda x, y: [deer_print(x - 30 + i*15, y + 10 + (i % 2)*8, 1.3, -80) for i in range(5)]),
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
                  "Joey našel babiččin prstýnek v pevnosti ze sněhu. A pan hajný slíbil, že naučí Klub Hvězdička číst stopy.",
                  "SH", 13, align="left", lead=17)
        ring(p.X(0.82), by + bh*0.55, 2.2)
        paw_print(p.X(0.9), by + 22, 1.6, 10, g=0.2)
    page_end()


# =================================================================== 3 the snowman family
def page_snowmen():
    R = rows([(270, [1]), (230, [0.5, 0.5]), (250, [1])])
    with Pn(*R[0]) as p:
        gy = p.Y(0.42)
        garden8(p, gy, 82, family=False, gap=0.9)
        parsnip_crate(p.X(0.62), p.Y(0.05), 1.1)
        betka(p.X(0.48), p.Y(0.03), 1.25, mood="grin", right="up", look=(-1, 0), item=lambda x, y: parsnip(x, y, 0.8, rot=160))
        A(p.X(0.12), p.Y(0.03), 1.15, mood="happy", right="front", look=(1, 0))
        Td(p.X(0.28), p.Y(0.03), 1.1, mood="grin", look=(1, 0))
        J(p, p.X(0.8), p.Y(0.03), 1.0, flip=True, mood="happy")
        kc(p.X(0.96), p.Y(0.5), rot=-60)
        cap(p, "Sobota. Klub Hvězdička staví sněhuláky na konci zahrady. Za plotem je louka a les.", w=290)
        say(p, "Děda Franta mi dal pastináky. Na nosy!", *hd_h("betka", p.X(0.48), p.Y(0.03), 1.25), w=150, area=(0.3, 0.75))
    with Pn(*R[1]) as p:
        gy = p.Y(0.5)
        winter_meadow(p, gy, 83)
        snowman_b(p.X(0.4), p.Y(0.06), 1.6, nose="parsnip", scarf=P.RIBBON)
        deda(p.X(0.75), p.Y(0.03), 1.0, flip=True, mood="grin", right="up", look=(-1, 0.3))
        say(p, "Můj bude největší!", *hd("deda", p.X(0.75), p.Y(0.03), 1.0), w=110, area=(0.45, 1.0))
    with Pn(*R[2]) as p:
        gy = p.Y(0.5)
        winter_meadow(p, gy, 84)
        snow_dog(p.X(0.55), p.Y(0.06), 1.5, flip=True)
        Hk(p.X(0.22), p.Y(0.03), 1.25, mood="grin", right="front", look=(1, -0.3))
        J(p, p.X(0.78), p.Y(0.03), 0.95, flip=True, mood="happy")
        say(p, "A já udělám sněhového Joeyho!", *hd_h("hanka", p.X(0.22), p.Y(0.03), 1.25), w=130, area=(0.0, 0.7))
    with Pn(*R[3]) as p:
        gy = p.Y(0.48)
        garden8(p, gy, 85, k=1.0, gap=0.92, dusk=True, flakes=36)
        cap(p, "Večer začalo sněžit. Ráno bude zahrada bílá a hladká.", w=230)
        Td(p.X(0.93), p.Y(0.03), 0.9, flip=True, mood="happy", right="wave", look=(-1, 0.3))
        say(p, "Dobrou noc, sněhuláci!", *hd_h("tonda", p.X(0.93), p.Y(0.03), 0.9), w=120, area=(0.55, 1.0))
    page_end()


# =================================================================== 4 morning: the noses are gone
def page_morning():
    R = rows([(260, [1]), (240, [0.5, 0.5]), (250, [1])])
    with Pn(*R[0]) as p:
        gy = p.Y(0.48)
        garden8(p, gy, 86, k=1.0, noses=["stub", "none", "none", "none"], house_x=None)
        trail("pes", [(p.X(0.02), p.Y(0.05)), (p.X(0.3), p.Y(0.1)), (p.X(0.5), p.Y(0.04)), (p.X(0.7), p.Y(0.08))], 1.0, wander=0.5)
        J(p, p.X(0.62), p.Y(0.03), 1.0, mood="happy")
        A(p.X(0.06), p.Y(0.03), 1.1, mood="surprised", right="up", look=(1, 0))
        kc(p.X(0.97), p.Y(0.07), rot=20)
        cap(p, "Ráno vyběhl Joey první.", w=160, where="tr")
        say(p, "Joey, počkej!", *hd_h("alica", p.X(0.06), p.Y(0.03), 1.1), w=100, area=(0.0, 0.4))
    with Pn(*R[1]) as p:
        snow_close(p, 0.55)
        snowman_b(p.X(0.3), p.Y(0.02), 2.3, nose="stub", scarf=P.RIBBON)
        snowman_b(p.X(0.78), p.Y(0.02), 1.8, nose="none", pompom=True)
        Hk(p.X(0.55), p.Y(0.03), 1.1, mood="surprised", look=(-1, 0.4))
        say(p, "Sněhuláci nemají nosy!", *hd_h("hanka", p.X(0.55), p.Y(0.03), 1.1), w=120, area=(0.3, 1.0))
    with Pn(*R[2]) as p:
        snow_close(p, 0.6)
        trail("pes", [(p.X(0.05), p.Y(0.05)), (p.X(0.4), p.Y(0.25)), (p.X(0.7), p.Y(0.1)), (p.X(0.95), p.Y(0.3))], 1.0, wander=0.7)
        J(p, p.X(0.6), p.Y(0.06), 1.05, pose="sniff", mood="happy")
        snow_spray(p.X(0.6) - 10, p.Y(0.1), 1.0)
        A(p.X(0.14), p.Y(0.03), 1.15, mood="worried", right="up", look=(1, 0))
        say(p, "Stůj! Šlapeš nám do stop!", *hd_h("alica", p.X(0.14), p.Y(0.03), 1.15), w=130, area=(0.0, 0.6))
    with Pn(*R[3]) as p:
        snow_close(p, 0.55)
        Hk(p.X(0.3), p.Y(0.03), 1.3, mood="wow", right="up", look=(1, 0.2), item=lambda x, y: nose_stub(x + 2, y + 2, 1.3))
        A(p.X(0.7), p.Y(0.03), 1.25, flip=True, mood="determined", right="front", look=(-1, 0),
          item=lambda x, y: notebook(x - 6, y - 4, 0.9))
        inset(p, p.X(0.9), p.Y(0.72), 64, 64, lambda x, y: nose_stub(x, y - 4, 3.2))
        say(p, "Tady je kousek nosu!", *hd_h("hanka", p.X(0.3), p.Y(0.03), 1.3), w=120, area=(0.0, 0.5))
        say(p, "Důkaz číslo jedna. Schovej ho.", *hd_h("alica", p.X(0.7), p.Y(0.03), 1.25), w=130, area=(0.4, 0.8))
    page_end()


# =================================================================== 5 the suspects; the forester arrives
def page_suspects():
    R = rows([(270, [1]), (220, [0.5, 0.5]), (260, [1])])
    with Pn(*R[0]) as p:
        gy = p.Y(0.5)
        garden8(p, gy, 87, k=0.85, noses="none", gap=0.86)
        trail("zajic", [(p.X(0.02), gy - 20), (p.X(0.5), gy - 24), (p.X(0.98), gy - 18)], 1.0)
        trail("liska", [(p.X(0.98), p.Y(0.3)), (p.X(0.6), p.Y(0.34)), (p.X(0.35), p.Y(0.33))], 1.0)
        mousehole(p.X(0.33), p.Y(0.33), 1.2)
        trail("srnka", [(p.X(0.86), gy - 12), (p.X(0.7), p.Y(0.25)), (p.X(0.5), p.Y(0.18))], 1.1, n=5)
        trail("pes", [(p.X(0.1), p.Y(0.04)), (p.X(0.4), p.Y(0.2)), (p.X(0.62), p.Y(0.12)), (p.X(0.84), p.Y(0.28)),
                      (p.X(0.6), p.Y(0.26))], 1.0, wander=0.8, seed=4)
        A(p.X(0.06), p.Y(0.03), 1.1, mood="think", right="lens", lens=True, look=(1, -0.5))
        kc(p.X(0.28), p.Y(0.07), rot=50)
        cap(p, "Kolem sněhuláků je spousta stop. Jenže Joey je skoro všechny pošlapal.", w=270, where="tr")
    with Pn(*R[1]) as p:
        snow_close(p, 0.5)
        Td(p.X(0.3), p.Y(0.03), 1.05, mood="determined", right="point", look=(1, -0.4))
        trail("zajic", [(p.X(0.6), p.Y(0.1)), (p.X(0.98), p.Y(0.3))], 1.6)
        say(p, "To byl zajíc! Zajíci mají rádi mrkev.", *hd_h("tonda", p.X(0.3), p.Y(0.03), 1.05), w=210)
    with Pn(*R[2]) as p:
        snow_close(p, 0.5)
        betka(p.X(0.2), p.Y(0.03), 1.1, mood="think", right="chin", look=(1, 0))
        Td(p.X(0.8), p.Y(0.03), 0.95, flip=True, mood="grin", right="hip", look=(-1, 0))
        say(p, "To ale nebyla mrkev. To byly pastináky.", *hd_h("betka", p.X(0.2), p.Y(0.03), 1.1), w=200, area=(0.0, 0.85))
        say(p, "Tak mají rádi i pastináky!", *hd_h("tonda", p.X(0.8), p.Y(0.03), 0.95), w=170, area=(0.35, 1.0))
    with Pn(*R[3]) as p:
        gy = p.Y(0.5)
        garden8(p, gy, 88, k=0.8, noses="none", gap=0.12, family=False)
        snowman_b(p.X(0.92), p.Y(0.1), 1.2, nose="none", scarf=P.RIBBON)
        hajny(p.X(0.14), p.Y(0.03), 1.05, mood="happy", right="wave", look=(1, 0))
        A(p.X(0.5), p.Y(0.03), 1.1, flip=True, mood="surprised", look=(-1, 0.2))
        Hk(p.X(0.64), p.Y(0.03), 1.05, flip=True, mood="happy", look=(-1, 0.2))
        J(p, p.X(0.78), p.Y(0.03), 0.95, flip=True, mood="happy")
        say(p, "Dobré ráno, detektivové! Slíbil jsem vám stopy.", *hj(p.X(0.14), p.Y(0.03), 1.05), w=200, area=(0.0, 0.5))
        say(p, "Pane hajný, kdo snědl sněhulákům nosy?", *hd_h("alica", p.X(0.5), p.Y(0.03), 1.1), w=200, area=(0.42, 1.0))
    page_end()


# =================================================================== 6 the meadow: dog and fox
def page_meadow():
    R = rows([(270, [1]), (230, [0.5, 0.5]), (250, [1])])
    with Pn(*R[0]) as p:
        gy = p.Y(0.5)
        winter_meadow(p, gy, 89)
        trail("pes", [(p.X(0.3), p.Y(0.06)), (p.X(0.45), p.Y(0.3)), (p.X(0.6), p.Y(0.15)), (p.X(0.72), p.Y(0.4)),
                      (p.X(0.86), p.Y(0.2)), (p.X(0.9), p.Y(0.36))], 1.0, wander=0.8, seed=6)
        J(p, p.X(0.84), p.Y(0.2), 1.0, mood="happy")
        hajny(p.X(0.1), p.Y(0.03), 1.0, mood="happy", right="point", look=(1, 0))
        A(p.X(0.24), p.Y(0.03), 1.0, mood="happy", look=(1, 0.2))
        Hk(p.X(0.34), p.Y(0.03), 0.95, mood="grin", look=(1, 0.2))
        cap(p, "Na louce smí Joey běhat bez vodítka. A to on miluje!", w=220, where="tr")
        say(p, "Kdo snědl nosy, vám neřeknu. Naučím vás stopy a přečtete si to sami.", *hj(p.X(0.1), p.Y(0.03), 1.0), w=230,
            area=(0.0, 0.62))
    with Pn(*R[1]) as p:
        snow_close(p, 0.4)
        trail("liska", [(p.X(0.05), p.Y(0.15)), (p.X(0.95), p.Y(0.45))], 1.6)
        hajny(p.X(0.85), p.Y(0.03), 0.85, flip=True, mood="happy", right="point", look=(-1, -0.4))
        say(p, "Pes běhá sem a tam. Liška chodí rovně, jako po provázku.", *hj(p.X(0.85), p.Y(0.03), 0.85), w=230,
            area=(0.0, 1.0))
    with Pn(*R[2]) as p:
        gy = p.Y(0.5)
        winter_meadow(p, gy, 90)
        liska(p.X(0.55), p.Y(0.18), 1.5, pose="pounce")
        mousehole(p.X(0.62), p.Y(0.1), 1.6)
        Hk(p.X(0.15), p.Y(0.03), 1.15, mood="wow", right="point", look=(1, 0))
        say(p, "Liška skáče do sněhu!", *hd_h("hanka", p.X(0.15), p.Y(0.03), 1.15), w=110, area=(0.0, 0.5))
    with Pn(*R[3]) as p:
        gy = p.Y(0.5)
        winter_meadow(p, gy, 91)
        pounce_hole(p.X(0.82), p.Y(0.3), 1.3)
        trail("liska", [(p.X(0.98), p.Y(0.4)), (p.X(0.82), p.Y(0.31))], 1.0)
        hajny(p.X(0.12), p.Y(0.03), 1.0, mood="happy", right="up", look=(1, 0))
        A(p.X(0.48), p.Y(0.03), 1.1, flip=True, mood="think", right="chin", look=(-1, 0),)
        say(p, "Slyší myš pod sněhem. A hop! Liška chytá myši, ne nosy.", *hj(p.X(0.12), p.Y(0.03), 1.0), w=180,
            area=(0.0, 0.62))
        say(p, "Ta liščí šňůra u plotu vedla k myší díře!", *hd_h("alica", p.X(0.48), p.Y(0.03), 1.1), w=150, area=(0.4, 1.0))
    page_end()


# =================================================================== 7 the hare; how a twig is bitten
def page_hare():
    R = rows([(250, [1]), (210, [0.5, 0.5]), (290, [0.5, 0.5])])
    with Pn(*R[0]) as p:
        gy = p.Y(0.5)
        winter_meadow(p, gy, 92)
        for k_, (bx, bs) in enumerate(((0.62, 1.0), (0.78, 0.8), (0.92, 1.1))):
            bare_tree(p.X(bx), gy - 20, bs*0.6, seed=4 + k_)
        hare_form(p.X(0.7), p.Y(0.2), 30, 9)
        zajic(p.X(0.7), p.Y(0.18), 1.4)
        Hk(p.X(0.12), p.Y(0.03), 1.15, mood="whisper", right="point", look=(1, 0.2))
        hajny(p.X(0.3), p.Y(0.03), 1.0, mood="happy", right="hush", look=(1, 0))
        say(p, "Zajíček!", *hd_h("hanka", p.X(0.12), p.Y(0.03), 1.15), w=90, area=(0.0, 0.3), whisper=True)
        say(p, "Pst. Sedí v pelíšku.", *hj(p.X(0.3), p.Y(0.03), 1.0), w=110, area=(0.2, 0.6), whisper=True)
    with Pn(*R[1]) as p:
        gy = p.Y(0.55)
        winter_meadow(p, gy, 93)
        trail("zajic", [(p.X(0.05), p.Y(0.1)), (p.X(0.55), p.Y(0.25))], 1.2)
        zajic(p.X(0.8), p.Y(0.28), 1.5, pose="run")
        sfx(p.X(0.06), p.Y(0.8), "HOP HOP!", 15, -6)
    with Pn(*R[2]) as p:
        snow_close(p, 0.45)
        trail("zajic", [(p.X(0.1), p.Y(0.08)), (p.X(0.65), p.Y(0.15))], 2.2, n=2)
        A(p.X(0.82), p.Y(0.03), 1.15, flip=True, mood="wow", right="point", look=(-1, -0.5))
        say(p, "Velké tlapky vepředu, malé vzadu. Jako ypsilon!", *hd_h("alica", p.X(0.82), p.Y(0.03), 1.15), w=150,
            area=(0.0, 0.8))
    with Pn(*R[3]) as p:
        winter_meadow(p, p.Y(0.55), 94)
        hajny(p.X(0.2), p.Y(0.03), 0.95, mood="happy", right="front", look=(1, 0))
        inset(p, p.X(0.68), p.Y(0.3), 120, 90, lambda x, y: twig(x + 22, y, 2.0, "clean"), "zajíc")
        say(p, "Zajíc ukousne větvičku hladce a šikmo. Jako nůžkami.", *hj(p.X(0.2), p.Y(0.03), 0.95), w=220)
    with Pn(*R[4]) as p:
        winter_meadow(p, p.Y(0.55), 95)
        hajny(p.X(0.82), p.Y(0.03), 0.95, flip=True, mood="happy", right="front", look=(-1, 0))
        inset(p, p.X(0.34), p.Y(0.3), 120, 90, lambda x, y: twig(x + 22, y, 2.0, "frayed"), "srnka")
        say(p, "Srnka nemá nahoře přední zuby. Větvičku utrhne. Zůstane rozcuchaná.", *hj(p.X(0.82), p.Y(0.03), 0.95),
            w=230)
    page_end()


# =================================================================== 8 the boars at the oak
def page_boars():
    R = rows([(280, [1]), (220, [0.5, 0.5]), (250, [1])])
    with Pn(*R[0]) as p:
        gy = p.Y(0.42)
        winter_meadow(p, gy, 95)
        oak(p.X(0.55), gy - 4, 1.2, seed=5)
        rooted_ground(p.X(0.5), p.Y(0.2), 160, 26)
        trail("divocak", [(p.X(0.3), p.Y(0.25)), (p.X(0.05), p.Y(0.1))], 1.1, n=5)
        hajny(p.X(0.85), p.Y(0.03), 1.0, flip=True, mood="happy", right="point", look=(-1, -0.3))
        Td(p.X(0.7), p.Y(0.03), 0.95, flip=True, mood="surprised", look=(-1, -0.3))
        kc(p.X(0.9), p.Y(0.06), rot=-110)
        cap(p, "U starého dubu je sníh rozrytý až na hlínu.", w=200)
        say(p, "Tady hledali divočáci žaludy.", *hj(p.X(0.85), p.Y(0.03), 1.0), w=130, area=(0.45, 1.0))
    with Pn(*R[1]) as p:
        snow_close(p, 0.4)
        boar_print(p.X(0.5), p.Y(0.35), 5.0)
        cap(p, "Divočák má za kopýtkem dvě tečky. Říká se jim paspárky.", w=220)
    with Pn(*R[2]) as p:
        snow_close(p, 0.5)
        Td(p.X(0.35), p.Y(0.03), 1.1, mood="determined", right="up", look=(1, 0))
        say(p, "Divočák! Ten sní všechno! I nosy!", *hd_h("tonda", p.X(0.35), p.Y(0.03), 1.1), w=200)
    with Pn(*R[3]) as p:
        winter_forest(p, p.Y(0.42), 96, trees=((0.05, 0.6), (0.95, 0.55)))
        divocak(p.X(0.62), p.Y(0.28), 0.55, pose="root")
        divocak(p.X(0.76), p.Y(0.31), 0.45, flip=True)
        hajny(p.X(0.12), p.Y(0.03), 1.05, mood="whisper", right="hush", look=(1, 0.3))
        A(p.X(0.28), p.Y(0.03), 1.05, mood="wow", look=(1, 0.3))
        Hk(p.X(0.4), p.Y(0.03), 1.0, mood="wow", right="hug", look=(1, 0.3))
        say(p, "Divočáci jsou plaší. Necháme je být.", *hj(p.X(0.12), p.Y(0.03), 1.05), w=140, area=(0.0, 0.45), whisper=True)
        say(p, "Pojďme dál. Potichu.", *hd_h("alica", p.X(0.28), p.Y(0.03), 1.05), w=110, area=(0.2, 0.6), whisper=True)
    page_end()


# =================================================================== 9 the forest: deer prints, krmelec, squirrel
def page_forest():
    R = rows([(280, [1]), (220, [0.5, 0.5]), (250, [1])])
    with Pn(*R[0]) as p:
        gy = p.Y(0.4)
        winter_forest(p, gy, 97, trees=((0.08, 0.75), (0.95, 0.7)))
        krmelec(p.X(0.55), p.Y(0.2), 1.25)
        trail("srnka", [(p.X(0.2), p.Y(0.05)), (p.X(0.42), p.Y(0.16)), (p.X(0.5), p.Y(0.2))], 1.0)
        trail("srnka", [(p.X(0.62), p.Y(0.2)), (p.X(0.8), p.Y(0.1)), (p.X(0.98), p.Y(0.14))], 1.0, seed=3)
        hajny(p.X(0.22), p.Y(0.03), 1.05, mood="happy", right="point", look=(1, 0.2))
        Td(p.X(0.8), p.Y(0.03), 0.95, flip=True, mood="happy", look=(-1, 0.2))
        betka(p.X(0.9), p.Y(0.03), 1.0, flip=True, mood="happy", look=(-1, 0.2))
        say(p, "Tohle je krmelec. Nosím sem srnkám seno.", *hj(p.X(0.22), p.Y(0.03), 1.05), w=150, area=(0.0, 0.5))
    with Pn(*R[1]) as p:
        snow_close(p, 0.4)
        deer_print(p.X(0.5), p.Y(0.35), 5.0)
        cap(p, "Srnka: dvě úzké půlky. Jako srdíčko. A žádné tečky.", w=220)
    with Pn(*R[2]) as p:
        winter_forest(p, p.Y(0.3), 98, trees=(), far=False)
        spruce(p.X(0.7), p.Y(0.0), 1.1, seed=5)
        veverka(p.X(0.58), p.Y(0.62), 1.6)
        cone_scales(p.X(0.6), p.Y(0.06), 9)
        trail("veverka", [(p.X(0.05), p.Y(0.12)), (p.X(0.55), p.Y(0.06))], 1.1)
        Hk(p.X(0.18), p.Y(0.03), 1.1, mood="wow", right="point", look=(1, 0.6))
        say(p, "Veverka!", *hd_h("hanka", p.X(0.18), p.Y(0.03), 1.1), w=90, area=(0.0, 0.45))
    with Pn(*R[3]) as p:
        winter_forest(p, p.Y(0.42), 99, trees=((0.05, 0.6), (0.96, 0.62)))
        hajny(p.X(0.2), p.Y(0.03), 0.95, mood="happy", right="front", look=(1, 0),
              item=lambda x, y: shape(rrect(x - 4, y - 12, 26, 20, 2), 0.97, LINE*0.8))
        A(p.X(0.66), p.Y(0.03), 1.0, flip=True, mood="grin", right="front", look=(-1, 0))
        J(p, p.X(0.84), p.Y(0.03), 0.9, flip=True, mood="happy")
        say(p, "Letos napadlo moc sněhu. Zvířata mají hlad a chodí až ke vsi.", *hj(p.X(0.2), p.Y(0.03), 0.95), w=230,
            area=(0.0, 0.55))
        say(p, "Tady máte můj průvodce stopami.", *hj(p.X(0.2), p.Y(0.03), 0.95), w=150, area=(0.55, 1.0))
        say(p, "Děkujeme!", *hd_h("alica", p.X(0.66), p.Y(0.03), 1.0), w=90, area=(0.45, 0.9))
    page_end()


# =================================================================== 10 the forester's track guide
GUIDE = [
    ("srnka", "SRNKA", "Dvě úzké půlky. Srdíčko bez teček.", lambda x, y: srnka(x, y, 0.62, shadow=False)),
    ("divocak", "DIVOČÁK", "Dvě široké půlky a za nimi dvě tečky.", lambda x, y: divocak(x, y, 0.62, shadow=False)),
    ("zajic", "ZAJÍC", "Velké tlapky vepředu, malé vzadu. Jako Y.", lambda x, y: zajic(x, y, 1.5, shadow=False)),
    ("liska", "LIŠKA", "Úzký oválek. Jde rovně jako po provázku.", lambda x, y: liska(x, y, 0.9, shadow=False)),
    ("pes", "PES", "Kulatá tlapka s drápky. Běhá sem a tam.", lambda x, y: joey(x, y, 0.85, shadow=False)),
    ("kocka", "KOČKA", "Malá kulatá tlapka. Drápky schová.", lambda x, y: cat(x, y, 1.0, mood="open")),
    ("veverka", "VEVERKA", "Čtyři tlapky pohromadě. Od stromu ke stromu.", lambda x, y: veverka(x, y, 1.6)),
    ("ptacek", "PTÁČEK", "Tři prstíky dopředu, jeden dozadu.", lambda x, y: tit(x, y, 2.2)),
]


def page_guide():
    with Pn(M, 40, W-2*M, H-80, bg=0.97) as p:
        hand_text(p.X(0.04), p.Y(0.955), p.w*0.92, "Průvodce stopami pana hajného", "SHB", 24)
        hand_text(p.X(0.04), p.Y(0.92), p.w*0.92, "Vystřihni si ho a nos ho s sebou do lesa!", "SH", 13)
        cw = p.w/2; ch = p.h*0.885/4
        for i, (key_, name, tip, fig) in enumerate(GUIDE):
            cx = p.x + (i % 2)*cw; cy = p.Y(0.905) - (i//2 + 1)*ch
            for k in range(0, int(cw - 16), 8):
                stroke([(cx + 8 + k, cy + 4), (cx + 12 + k, cy + 4)], 0.5, g=0.5)
            shape(rrect(cx + 6, cy + 8, cw - 12, ch - 12, 8), 1.0, 1.0)
            fig(cx + 52, cy + 52)
            fn = PRINTS[key_]
            px, py = cx + cw*0.72, cy + ch*0.62
            if fn: fn(px, py, 3.6, ink=True)
            else: bird_print(px, py - 8, 4.2, g=P.TRACK_INK)
            if key_ in ("liska", "pes", "zajic", "veverka", "srnka", "divocak"):
                trail(key_, [(cx + cw*0.5, cy + 22), (cx + cw - 16, cy + 30)], 0.65, ink=True,
                      wander=0.8 if key_ == "pes" else 0.0, seed=i)
            hand_text(cx + 14, cy + ch - 30, cw*0.5, name, "SHB", 16, align="left")
            hand_text(cx + 100, cy + 60, cw*0.36, tip, "SH", 11.5, align="left", lead=14)
    page_end()


# =================================================================== 11 at home: the suspect list
def page_list():
    R = rows([(220, [1]), (300, [1]), (210, [0.5, 0.5])])
    with Pn(*R[0]) as p:
        kitchen(p, table=False)
        A(p.X(0.15), p.Y(0.03), 1.15, hat=False, mood="think", right="chin", look=(1, 0))
        Hk(p.X(0.32), p.Y(0.03), 1.05, hat=False, mood="think", look=(1, 0))
        betka(p.X(0.62), p.Y(0.03), 1.1, hat=False, flip=True, mood="happy", look=(-1, 0))
        Td(p.X(0.8), p.Y(0.03), 1.05, hat=False, flip=True, mood="happy", look=(-1, 0))
        say(p, "Tak. Kdo snědl nosy? Zkusíme to přečíst.", *hd("alica", p.X(0.15), p.Y(0.03), 1.15), w=170, area=(0.0, 0.6))
    with Pn(*R[1]) as p:
        bg_fill(p, 0.9)
        notebook_big(p.X(0.06), p.Y(0.06), p.w*0.88, p.h*0.88, "PŘÍPAD Č. 8: NOSY",
                     ["1. kousek nosu (mám ho v kapse)",
                      "2. Joey: spal v předsíni. NE.", "3. liška: šla k myší díře. NE.",
                      "4. zajíc: ???", "5. divočák: ???",
                      "6. stopy s půlkami: Joey je pošlapal"])
        kc(p.X(0.93), p.Y(0.12), rot=-70)
    with Pn(*R[2]) as p:
        kitchen(p, table=False)
        A(p.X(0.3), p.Y(0.03), 1.15, hat=False, mood="determined", right="up", look=(1, 0))
        say(p, "Potřebujeme čistý sníh. Bez Joeyho!", *hd("alica", p.X(0.3), p.Y(0.03), 1.15), w=200)
    with Pn(*R[3]) as p:
        kitchen(p, table=False)
        deda(p.X(0.3), p.Y(0.03), 0.92, mood="grin", right="front", look=(1, 0))
        say(p, "Večer ho uhladím lopatou. Jako čistou stránku!", *hd("deda", p.X(0.3), p.Y(0.03), 0.92), w=210)
    page_end()


# =================================================================== 12 evening: the trap
def page_trap():
    R = rows([(270, [1]), (230, [0.5, 0.5]), (250, [1])])
    with Pn(*R[0]) as p:
        gy = p.Y(0.5)
        garden8(p, gy, 100, k=0.85, smooth=True, dusk=True)
        deda(p.X(0.5), p.Y(0.03), 1.0, mood="happy", right="front", look=(1, -0.3))
        shovel(p.X(0.5) + 26, p.Y(0.03) + 10, 0.85, rot=-70, snow=False)
        betka(p.X(0.88), p.Y(0.03), 1.05, flip=True, mood="grin", right="up", look=(-1, 0.4),
              item=lambda x, y: parsnip(x, y, 0.7, rot=150))
        cap(p, "Večer. Bětka dala sněhulákům nové nosy. Poslední tři pastináky.", w=230)
    with Pn(*R[1]) as p:
        fy = bedroom_night(p)
        Hk(p.X(0.28), fy, 1.3, hat=False, mood="grin", right="up", look=(1, 0), item=lambda x, y: torch(x, y, 30))
        say(p, "Já budu svítit!", *hd("hanka", p.X(0.28), fy, 1.3), w=100, area=(0.0, 0.6))
    with Pn(*R[2]) as p:
        fy = bedroom_night(p)
        A(p.X(0.25), fy, 1.15, hat=False, mood="whisper", right="hush", look=(1, 0))
        say(p, "Nesviť. Světlo zvířata vyleká.", *hd("alica", p.X(0.25), fy, 1.15), w=170, area=(0.0, 0.95), whisper=True)
    with Pn(*R[3]) as p:
        fy = hallway(p)
        shape([(p.X(0.04), fy), (p.X(0.18), fy), (p.X(0.18), p.Y(0.92)), (p.X(0.04), p.Y(0.92))], P.DOOR_FRAME, BG)
        dog_bed(p.X(0.3), fy, 1.4)
        joey(p.X(0.3), fy + 4, 0.95, mood="sleepy")
        keep_clear(p, p.X(0.3) + 16, fy + 38, p.X(0.3) + 40, fy + 64, "joey")
        babicka(p.X(0.55), fy, 1.1, mood="happy", right="front", look=(1, 0), item=lambda x, y: mug(x, y - 4, 0.8))
        deda(p.X(0.82), fy, 1.0, flip=True, mood="happy", look=(-1, -0.3))
        say(p, "Kakao pro hlídku!", *hd("babi", p.X(0.55), fy, 1.1), w=110, area=(0.35, 0.75))
        say(p, "A Joey spí v předsíni. Ať nám venku nešlape.", *hd("deda", p.X(0.82), fy, 1.0), w=150, area=(0.5, 1.0))
    page_end()


# =================================================================== 13 the night watch
def page_night():
    R = rows([(280, [1]), (220, [0.5, 0.5]), (250, [1])])
    with Pn(*R[0]) as p:
        bg_fill(p, P.BEDROOM_WALL)
        fy = p.y + 14
        shape([(p.x - 5, p.y - 5), (p.x + p.w + 5, p.y - 5), (p.x + p.w + 5, fy), (p.x - 5, fy)], P.FLOOR, BG)
        watch_window(p, p.X(0.45), p.Y(0.3), p.X(0.95), p.Y(0.9))
        bg_fill(p, 0.0, 0.2)
        A(p.X(0.12), fy, 1.25, hat=False, mood="whisper", right="front", look=(1, 0.3), item=lambda x, y: mug(x, y - 4, 0.75))
        Hk(p.X(0.3), fy, 1.15, hat=False, mood="happy", right="hug", look=(1, 0.3))
        kc(p.X(0.98), p.Y(0.12), rot=60)
        cap(p, "Hlídka u okna.", w=120)
        say(p, "Pst. Díváme se.", *hd("alica", p.X(0.12), fy, 1.25), w=100, area=(0.0, 0.4), whisper=True)
    with Pn(*R[1]) as p:
        bg_fill(p, P.BEDROOM_WALL); bg_fill(p, 0.0, 0.22)
        Hk(p.X(0.45), p.Y(0.03), 1.4, hat=False, mood="sleepy", right="hug", look=(1, 0))
        say(p, "Já vůbec nejsem ospalá…", *hd("hanka", p.X(0.45), p.Y(0.03), 1.4), w=120)
    with Pn(*R[2]) as p:
        fy = bedroom_night(p, window=False)
        kid_in_bed(hanka, 31, p.X(0.03), p.X(0.47), p.Y(0.3), 1.1, mood="sleepy", right="hug")
        kid_in_bed(alica, 45, p.X(0.53), p.X(0.97), p.Y(0.3), 1.0, mood="sleepy")
        sfx(p.X(0.08), p.Y(0.82), "CHRRR…", 15, -4)
        cap(p, "Nakonec usnuly obě.", w=150, where="tr")
    with Pn(*R[3]) as p:
        fy = hallway(p)
        x0, x1, y0, y1 = p.X(0.55), p.X(0.92), p.Y(0.35), p.Y(0.9)
        watch_window(p, x0, y0, x1, y1, shape_=True)
        bg_fill(p, 0.0, 0.25)
        dog_bed(p.X(0.25), fy, 1.4)
        J(p, p.X(0.22), fy + 4, 1.1, mood="open", flip=False)
        cap(p, "Jen Joey nespal. Něco tam venku bylo. Ale Joey neštěkl. Hodný pes.", w=230)
    page_end()


# =================================================================== 14 morning: one kind of print
def page_clean():
    R = rows([(260, [1]), (240, [0.5, 0.5]), (250, [1])])
    with Pn(*R[0]) as p:
        gy = p.Y(0.5)
        sm = garden8(p, gy, 101, k=0.85, smooth=True, noses=["stub", "none", "none", "parsnip"], gap=0.9)
        trail("srnka", [(p.X(0.9), gy - 10), (p.X(0.7), p.Y(0.2)), (p.X(0.42), p.Y(0.1)), (p.X(0.28), p.Y(0.1))], 1.0)
        A(p.X(0.06), p.Y(0.03), 1.05, mood="surprised", look=(1, 0))
        Hk(p.X(0.16), p.Y(0.03), 1.0, mood="surprised", right="point", look=(1, 0.3))
        kc(p.X(0.97), p.Y(0.06), rot=30)
        cap(p, "Ráno.", w=70, where="tr")
        say(p, "Zase nemají nosy!", *hd_h("hanka", p.X(0.16), p.Y(0.03), 1.0), w=110, area=(0.0, 0.5))
    with Pn(*R[1]) as p:
        snow_close(p, 0.35)
        for i in range(5):
            yy = p.Y(0.05) + i*14
            stroke([(p.x, yy), (p.x + p.w, yy + 1)], 0.4, g=0.82)
        trail("srnka", [(p.X(0.95), p.Y(0.55)), (p.X(0.5), p.Y(0.3)), (p.X(0.05), p.Y(0.15))], 1.5)
        trail("zajic", [(p.X(0.02), p.Y(0.6)), (p.X(0.98), p.Y(0.62))], 1.0)
        cap(p, "Na čistém sněhu vedou ke sněhulákům jen jedny stopy.", w=210, where="tl")
    with Pn(*R[2]) as p:
        snow_close(p, 0.2)
        magnifier(p.X(0.5), p.Y(0.45), ang=-30, r=58)
        deer_print(p.X(0.5), p.Y(0.47), 4.6)
    with Pn(*R[3]) as p:
        gy = p.Y(0.5)
        garden8(p, gy, 102, k=0.75, noses="none", family=False)
        A(p.X(0.15), p.Y(0.03), 1.1, mood="think", right="front", look=(1, -0.3), item=lambda x, y: notebook(x - 6, y - 4, 0.9))
        deda(p.X(0.5), p.Y(0.03), 1.0, flip=True, mood="happy", look=(-1, 0))
        betka(p.X(0.7), p.Y(0.03), 1.05, flip=True, mood="happy", look=(-1, 0))
        Td(p.X(0.86), p.Y(0.03), 1.05, flip=True, mood="happy", look=(-1, 0))
        say(p, "Stopu si nakreslím. Přesně.", *hd_h("alica", p.X(0.15), p.Y(0.03), 1.1), w=120, area=(0.0, 0.4))
        say(p, "Joey byl celou noc v předsíni. Dveře byly zavřené.", *hd("deda", p.X(0.5), p.Y(0.03), 1.0), w=170,
            area=(0.3, 1.0))
    page_end()


# =================================================================== 15 STOP, DETEKTIVE!
def page_stop():
    with Pn(M, 40, W-2*M, H-80, bg=0.95) as p:
        title(p.X(0.5), p.Y(0.92), "STOP, DETEKTIVE!", 44)
        hand_text(p.X(0.05), p.Y(0.86), p.w*0.9, "Máš všechny stopy. Kdo snědl sněhulákům nosy?", "SHB", 18)
        cw, ch = p.w*0.3, p.h*0.215
        items = [
            ("kousek nosu (strana 4)", lambda x, y: nose_stub(x, y + 26, 3.0)),
            ("větvičky pana hajného (strana 7)", lambda x, y: (twig(x + 6, y + 44, 1.2, "clean"), twig(x + 6, y + 18, 1.2, "frayed"))),
            ("dědův sněhulák a zajíc", lambda x, y: (snowman_b(x - 8, y + 2, 0.95, nose="stub", scarf=P.RIBBON),
                                            zajic(x + 30, y + 2, 0.75, flip=True))),
            ("stopa na čistém sněhu (strana 14)", lambda x, y: deer_print(x, y + 32, 3.6)),
            ("divočák: za kopýtkem dvě tečky", lambda x, y: boar_print(x, y + 34, 3.0)),
            ("Joey spal v předsíni", lambda x, y: (dog_bed(x, y + 6, 0.9), joey(x, y + 9, 0.6, mood="sleepy"))),
        ]
        for i, (txt, pic) in enumerate(items):
            cx = p.X(0.04) + (i % 3)*(cw + p.w*0.02); cy = p.Y(0.82) - (i//3 + 1)*(ch + 10)
            shape(rrect(cx, cy, cw, ch, 8), 1.0, 1.2)
            hand_text(cx + 6, cy + ch - 20, 30, str(i + 1), "SHB", 16, align="left")
            with T(cx + cw/2, cy + 36, 1.4):
                pic(0, 0)
            hand_text(cx + 8, cy + 20, cw - 16, txt, "SH", 10.5, lead=12)
        by = p.Y(0.82) - 2*(ch + 10) - 70
        shape(rrect(p.X(0.04), by, p.w*0.92, 60, 8), 1.0, 1.2)
        hand_text(p.X(0.06), by + 36, 30, "7", "SHB", 16, align="left")
        hand_text(p.X(0.12), by + 36, p.w*0.74, "Průvodce stopami na straně 10. Čí je ta stopa?", "SH", 14, align="left")
        deer_print(p.X(0.9), by + 30, 2.2, ink=True)
        hand_text(p.X(0.05), by - 32, p.w*0.9, "Kdo to byl? Jak to víš?", "SHB", 20)
        hand_text(p.X(0.05), by - 58, p.w*0.9, "A kdo to určitě nebyl?", "SHB", 20)
        hand_text(p.X(0.05), by - 84, p.w*0.9, "Nápověda: zajíc je malý. Kam by dosáhl?", "SH", 14)
        with T(p.X(0.5), p.Y(0.06), 1.0, rot=180):
            hand_text(-p.w*0.45, 0, p.w*0.9, "Srnka! Dvě úzké půlky bez teček. Nos je utržený a rozcuchaný,", "SH", 12)
            hand_text(-p.w*0.45, -15, p.w*0.9, "srnka nemá nahoře zuby. A zajíc by na dědova sněhuláka nedosáhl.", "SH", 12)
    page_end()


# =================================================================== 16 the reasoning
def page_reason():
    R = rows([(250, [1]), (230, [0.5, 0.5]), (270, [1])])
    with Pn(*R[0]) as p:
        kitchen(p, table=False)
        Td(p.X(0.15), p.Y(0.03), 1.15, hat=False, mood="determined", right="up", look=(1, 0))
        A(p.X(0.7), p.Y(0.03), 1.15, hat=False, flip=True, mood="think", right="front", look=(-1, -0.2),
          item=lambda x, y: shape(rrect(x - 22, y - 12, 26, 20, 2), 0.97, LINE*0.8))
        say(p, "Byl to divočák! Ten sní všechno!", *hd("tonda", p.X(0.15), p.Y(0.03), 1.15), w=140, area=(0.0, 0.5))
        say(p, "Divočák má za kopýtky dvě tečky. Tady žádné nejsou.", *hd("alica", p.X(0.7), p.Y(0.03), 1.15), w=170,
            area=(0.4, 1.0))
    with Pn(*R[1]) as p:
        kitchen(p, table=False)
        betka(p.X(0.4), p.Y(0.03), 1.4, hat=False, mood="think", right="chin", look=(1, 0))
        say(p, "Tak zajíc. Zajíci mají rádi zeleninu.", *hd("betka", p.X(0.4), p.Y(0.03), 1.4), w=140)
    with Pn(*R[2]) as p:
        kitchen(p, table=False)
        Hk(p.X(0.35), p.Y(0.03), 1.35, hat=False, mood="determined", right="up", look=(1, 0))
        say(p, "Zajíček je malý jako já. Na dědova sněhuláka nedosáhne!", *hd("hanka", p.X(0.35), p.Y(0.03), 1.35), w=160)
    with Pn(*R[3]) as p:
        kitchen(p, table=False)
        A(p.X(0.14), p.Y(0.03), 1.2, hat=False, mood="wow", right="up", look=(1, 0),
          item=lambda x, y: nose_stub(x + 2, y + 2, 1.3))
        Hk(p.X(0.88), p.Y(0.03), 1.1, hat=False, flip=True, mood="grin", right="up", look=(-1, 0))
        Td(p.X(0.7), p.Y(0.03), 1.05, hat=False, flip=True, mood="surprised", look=(-1, 0))
        say(p, "A nos je utržený. Rozcuchaný jako ta větvička. Dvě půlky, žádné tečky…", *hd("alica", p.X(0.14), p.Y(0.03), 1.2),
            w=200, area=(0.0, 0.62))
        say(p, "SRNKA!", *hd("hanka", p.X(0.88), p.Y(0.03), 1.1), w=90, area=(0.65, 1.0))
    page_end()


# =================================================================== 17 following the trail
def page_follow():
    R = rows([(270, [1]), (230, [0.5, 0.5]), (250, [1])])
    with Pn(*R[0]) as p:
        gy = p.Y(0.5)
        garden8(p, gy, 103, k=0.8, noses="none", gap=0.62, family=False)
        trail("srnka", [(p.X(0.05), p.Y(0.1)), (p.X(0.4), p.Y(0.25)), (p.X(0.62), gy - 10)], 1.0)
        J(p, p.X(0.45), p.Y(0.15), 1.0, pose="sniff", mood="happy")
        A(p.X(0.12), p.Y(0.03), 1.1, mood="determined", right="point", look=(1, 0.2))
        Hk(p.X(0.24), p.Y(0.03), 1.0, mood="happy", right="hug", look=(1, 0.2))
        betka(p.X(0.8), p.Y(0.03), 1.05, flip=True, mood="happy", look=(-1, 0.2))
        Td(p.X(0.92), p.Y(0.03), 1.0, flip=True, mood="happy", look=(-1, 0.2))
        kc(p.X(0.98), p.Y(0.45), rot=-20)
        cap(p, "Stopy vedou mezerou v plotě. Na louku a k lesu.", w=190, where="tr")
        say(p, "Joey, hledej!", *hd_h("alica", p.X(0.12), p.Y(0.03), 1.1), w=100, area=(0.0, 0.4))
    with Pn(*R[1]) as p:
        gy = p.Y(0.55)
        winter_meadow(p, gy, 104)
        trail("srnka", [(p.X(0.05), p.Y(0.05)), (p.X(0.6), p.Y(0.3)), (p.X(0.95), gy - 8)], 1.0)
        J(p, p.X(0.42), p.Y(0.12), 1.05, pose="sniff", mood="happy")
        sfx(p.X(0.5), p.Y(0.42), "ČMUCH ČMUCH!", 14, -5)
    with Pn(*R[2]) as p:
        winter_forest(p, p.Y(0.35), 105, trees=(), far=True)
        low_spruce(p.X(0.5), p.Y(0.06), 1.35)
        Hk(p.X(0.18), p.Y(0.03), 1.15, mood="determined", right="point", look=(1, 0), item=lambda x, y: torch(x, y, -10))
        say(p, "Já se tam vejdu!", *hd_h("hanka", p.X(0.18), p.Y(0.03), 1.15), w=100, area=(0.0, 0.45))
    with Pn(*R[3]) as p:
        bg_fill(p, 0.32)
        for k_ in range(9):
            x_ = p.x + k_*p.w/8
            fill([(x_ - 30, p.y + p.h + 5), (x_ + 30, p.y + p.h + 5), (x_, p.Y(0.6))], P.SPRUCE)
        fill([(p.x - 5, p.y - 5), (p.x + p.w + 5, p.y - 5), (p.x + p.w + 5, p.Y(0.35)), (p.x - 5, p.Y(0.35))], 0.7)
        deer_bed(p.X(0.58), p.Y(0.18), 120, 34)
        hx_ = p.X(0.2)
        Hk(hx_, p.Y(0.03), 1.25, hat=True, mood="wow", right="front", look=(1, -0.3), item=lambda x, y: torch(x, y, -20))
        hx2, hy2 = hand_pt(True, "front", hx_, p.Y(0.03), 1.25)
        torch_beam(hx2 + 9, hy2, p.X(0.8), p.Y(0.1), p.X(0.75), p.Y(0.3), 0.4)
        say(p, "Tady někdo spal! Je tu důlek a chlupy.", *hd_h("hanka", hx_, p.Y(0.03), 1.25), w=150, area=(0.0, 0.6))
        say(p, "Srnčí postýlka!", p.X(0.98), p.Y(0.5), w=100, area=(0.62, 1.0))
    page_end()


# =================================================================== 18 the deer
def page_deer():
    R = rows([(280, [1]), (230, [0.5, 0.5]), (240, [1])])
    with Pn(*R[0]) as p:
        gy = p.Y(0.35)
        winter_forest(p, gy, 106, trees=((0.62, 0.55), (0.98, 0.6)))
        srnka(p.X(0.78), p.Y(0.08), 0.95, flip=True, look=(-1, 0))
        J(p, p.X(0.5), p.Y(0.06), 0.95, mood="happy")
        A(p.X(0.08), p.Y(0.03), 1.05, mood="whisper", look=(1, 0.2))
        Hk(p.X(0.2), p.Y(0.03), 1.0, mood="whisper", right="hush", look=(1, 0.2))
        Td(p.X(0.32), p.Y(0.03), 1.0, mood="wow", look=(1, 0.2))
        cap(p, "A pak ji uviděli.", w=130, where="tr")
        say(p, "Pst. Srnka!", *hd_h("hanka", p.X(0.2), p.Y(0.03), 1.0), w=90, area=(0.0, 0.45), whisper=True)
    with Pn(*R[1]) as p:
        winter_forest(p, p.Y(0.3), 107, trees=(), far=True)
        srnka(p.X(0.68), p.Y(0.04), 1.4, pose="low", flip=True, look=(-1, -0.3))
        J(p, p.X(0.16), p.Y(0.04), 1.3, pose="sniff", mood="happy")
        cap(p, "Čmuch. Joey a srnka se očichali.", w=150, where="tl")
    with Pn(*R[2]) as p:
        winter_forest(p, p.Y(0.35), 108, trees=((0.95, 0.5),), far=True)
        A(p.X(0.2), p.Y(0.03), 1.0, mood="grin", right="up", look=(1, 0))
        say(p, "Víte, že srnka má vzadu bílé chlupy? Říká se tomu zrcátko. A když se lekne…",
            *hd_h("alica", p.X(0.2), p.Y(0.03), 1.0), w=235)
    with Pn(*R[3]) as p:
        gy = p.Y(0.42)
        winter_forest(p, gy, 109, trees=((0.05, 0.55),), far=True)
        srnka(p.X(0.82), p.Y(0.3), 0.85, pose="run", flip=False)
        A(p.X(0.3), p.Y(0.03), 1.1, mood="surprised", right="point", look=(1, 0.3))
        Hk(p.X(0.14), p.Y(0.03), 1.0, mood="sad", right="hug", look=(1, 0.3))
        J(p, p.X(0.5), p.Y(0.03), 0.95, mood="happy")
        say(p, "Utekla!", *hd_h("hanka", p.X(0.14), p.Y(0.03), 1.0), w=80, area=(0.0, 0.3))
        say(p, "…tak ho ukáže. Přesně takhle.", *hd_h("alica", p.X(0.3), p.Y(0.03), 1.1), w=130, area=(0.18, 0.66))
    page_end()


# =================================================================== 19 the forester: wild animals are shy
def page_shy():
    R = rows([(270, [1]), (230, [0.5, 0.5]), (250, [1])])
    with Pn(*R[0]) as p:
        winter_forest(p, p.Y(0.38), 110, trees=((0.05, 0.55), (0.97, 0.6)))
        A(p.X(0.12), p.Y(0.03), 1.1, mood="worried", look=(1, 0))
        Hk(p.X(0.24), p.Y(0.03), 1.0, mood="sad", right="hug", look=(1, 0))
        J(p, p.X(0.4), p.Y(0.03), 0.9, mood="happy")
        hajny(p.X(0.78), p.Y(0.03), 1.05, flip=True, mood="happy", look=(-1, 0))
        say(p, "Vyplašila jsem ji. Moc nahlas jsem povídala.", *hd_h("alica", p.X(0.12), p.Y(0.03), 1.1), w=150, area=(0.0, 0.45))
        say(p, "Kdepak. Divoká zvířata jsou plachá. Tak je to správně.", *hj(p.X(0.78), p.Y(0.03), 1.05), w=170,
            area=(0.45, 1.0))
    with Pn(*R[1]) as p:
        winter_forest(p, p.Y(0.35), 111, trees=(), far=True)
        hajny(p.X(0.3), p.Y(0.03), 0.92, mood="happy", right="front", look=(1, 0))
        say(p, "Hlavně, že jste ji nehonili. Ani Joey.", *hj(p.X(0.3), p.Y(0.03), 0.92), w=210)
    with Pn(*R[2]) as p:
        winter_forest(p, p.Y(0.35), 112, trees=(), far=True)
        hajny(p.X(0.3), p.Y(0.03), 0.92, mood="think", right="chin", look=(1, 0))
        say(p, "V zimě mají srnky hlad. A pastinák je pro ně dobrota.", *hj(p.X(0.3), p.Y(0.03), 0.92), w=230)
    with Pn(*R[3]) as p:
        winter_forest(p, p.Y(0.38), 113, trees=((0.97, 0.6),))
        Hk(p.X(0.15), p.Y(0.03), 1.15, mood="determined", right="up", look=(1, 0))
        betka(p.X(0.3), p.Y(0.03), 1.05, mood="happy", look=(1, 0))
        hajny(p.X(0.75), p.Y(0.03), 1.05, flip=True, mood="grin", look=(-1, 0))
        say(p, "Dáme jí zeleninu do krmelce! Ať nemusí jíst nosy.", *hd_h("hanka", p.X(0.15), p.Y(0.03), 1.15), w=170,
            area=(0.0, 0.55))
        say(p, "Výborný nápad, malá detektivko.", *hj(p.X(0.75), p.Y(0.03), 1.05), w=130, area=(0.5, 1.0))
    page_end()


# =================================================================== 20 the krmelec
def page_krmelec():
    R = rows([(270, [1]), (230, [0.5, 0.5]), (250, [1])])
    with Pn(*R[0]) as p:
        gy = p.Y(0.5)
        winter_meadow(p, gy, 114)
        sx_ = p.X(0.6)
        sled(sx_, p.Y(0.08), 1.0)
        for k_ in range(5): carrot(sx_ - 30 + k_*12, p.Y(0.08) + 20, 0.6, rot=-80 + k_*8)
        for k_ in range(3): apple(sx_ + 10 + k_*10, p.Y(0.08) + 24, 0.6)
        beet(sx_ - 20, p.Y(0.08) + 26, 0.6)
        stroke([(sx_ - 42, p.Y(0.08) + 14), (p.X(0.3) + 10, p.Y(0.08) + 60)], 0.9, g=0.3)
        Td(p.X(0.3), p.Y(0.03), 1.05, mood="grin", right="front", look=(-1, 0), legs="walk")
        betka(p.X(0.15), p.Y(0.03), 1.05, mood="happy", look=(1, 0), legs="walk")
        A(p.X(0.85), p.Y(0.03), 1.05, flip=True, mood="happy", look=(-1, 0))
        Hk(p.X(0.95), p.Y(0.03), 0.95, flip=True, mood="grin", right="hug", look=(-1, 0))
        kc(p.X(0.04), p.Y(0.06), rot=-40)
        cap(p, "Odpoledne vezl Klub Hvězdička na saních dobroty.", w=220)
    with Pn(*R[1]) as p:
        winter_forest(p, p.Y(0.35), 115, trees=(), far=True)
        krmelec(p.X(0.55), p.Y(0.06), 1.15, food=True)
        hajny(p.X(0.15), p.Y(0.03), 1.0, mood="happy", right="front", look=(1, 0), item=lambda x, y: carrot(x, y, 0.6, rot=-60))
        say(p, "Mrkev, jablka, řepa. Ty si pochutná!", *hj(p.X(0.15), p.Y(0.03), 1.0), w=140, area=(0.0, 0.6))
    with Pn(*R[2]) as p:
        winter_forest(p, p.Y(0.35), 116, trees=(), far=True)
        Hk(p.X(0.4), p.Y(0.03), 1.35, mood="grin", right="front", look=(1, 0), item=lambda x, y: carrot(x - 2, y - 2, 1.3, rot=-70))
        say(p, "A tahle je od opičky.", *hd_h("hanka", p.X(0.4), p.Y(0.03), 1.35), w=110)
    with Pn(*R[3]) as p:
        gy = p.Y(0.4)
        winter_forest(p, gy, 117, trees=((0.05, 0.55),))
        krmelec(p.X(0.72), p.Y(0.08), 1.1, food=True)
        A(p.X(0.2), p.Y(0.03), 1.1, mood="think", right="chin", look=(1, 0))
        betka(p.X(0.36), p.Y(0.03), 1.05, mood="grin", right="up", look=(-1, 0))
        say(p, "A když stejně přijde na naše nosy?", *hd_h("alica", p.X(0.2), p.Y(0.03), 1.1), w=140, area=(0.0, 0.42))
        say(p, "To mám vymyšlené!", *hd_h("betka", p.X(0.36), p.Y(0.03), 1.05), w=110, area=(0.25, 0.6))
    page_end()


# =================================================================== 21 pinecone noses; the deer at dusk
def page_cones():
    R = rows([(270, [1]), (230, [0.5, 0.5]), (250, [1])])
    with Pn(*R[0]) as p:
        gy = p.Y(0.5)
        sm = garden8(p, gy, 118, k=0.85, noses=["cone", "cone", "cone", "none"])
        x_, y_, s_k = sm["tonda"]
        betka(x_ + 34, p.Y(0.03), 1.1, flip=True, mood="grin", right="up", look=(-1, 0.4),
              item=lambda x, y: shape(ell(x, y, 2.6, 5, 14), P.PINECONE, LINE*0.5))
        kc(p.X(0.06), p.Y(0.06), rot=40)
        say(p, "Nosy ze šišek. Ty srnka nejí!", *hd_h("betka", x_ + 34, p.Y(0.03), 1.1), w=130, area=(0.45, 1.0))
    with Pn(*R[1]) as p:
        snow_close(p, 0.5)
        snow_dog(p.X(0.55), p.Y(0.06), 1.6, flip=True)
        with T(p.X(0.55) - 28*1.6, p.Y(0.06) + 15*1.6, 1.6, rot=-90):
            shape(ell(0, 0, 2.2, 4.4, 14), P.PINECONE, LINE*0.5)
        J(p, p.X(0.15), p.Y(0.03), 1.05, mood="happy")
        cap(p, "Sněhový Joey dostal taky šiškový nos.", w=200, where="tr")
    with Pn(*R[2]) as p:
        kitchen(p, table=False, evening=True)
        babicka(p.X(0.4), p.Y(0.03), 1.15, mood="happy", right="point", look=(1, 0.3))
        say(p, "Děti, pojďte k oknu. Ale potichu!", *hd("babi", p.X(0.4), p.Y(0.03), 1.15), w=140, whisper=True)
    with Pn(*R[3]) as p:
        gy = p.Y(0.55)
        winter_meadow(p, gy, 119, dusk=True)
        srnka(p.X(0.74), gy - 26, 0.5, flip=True)
        srnka(p.X(0.86), gy - 30, 0.44, flip=True, pose="low")
        snow_fence(p.x - 5, p.x + p.w + 5, p.Y(0.2), 34)
        for fn, fx_ in ((A, 0.1), (Hk, 0.22), (betka, 0.34), (Td, 0.46)):
            fn(p.X(fx_), p.Y(0.03), 0.95, mood="whisper", look=(1, 0.4))
        cap(p, "Na kraji louky stály dvě srnky. Všichni byli úplně potichu. I Alica.", w=250, where="tr")
    page_end()


# =================================================================== 22 case closed; a strange slip of paper
def page_end8():
    R = rows([(260, [1]), (230, [0.5, 0.5]), (260, [1])])
    with Pn(*R[0]) as p:
        kitchen(p, evening=True)
        for k_ in range(4): mug(p.X(0.2) + k_*60, p.Y(0.38) + 2, 0.8)
        A(p.X(0.1), p.Y(0.03), 1.1, hat=False, mood="grin", right="front", look=(1, 0), item=lambda x, y: notebook(x - 6, y - 4, 0.9))
        Td(p.X(0.85), p.Y(0.03), 1.05, hat=False, flip=True, mood="grin", right="up", look=(-1, 0))
        say(p, "Případ vyřešen!", *hd("alica", p.X(0.1), p.Y(0.03), 1.1), w=110, area=(0.0, 0.4))
        say(p, "Příště poznám každou stopu sám!", *hd("tonda", p.X(0.85), p.Y(0.03), 1.05), w=140, area=(0.5, 1.0))
    with Pn(*R[1]) as p:
        bg_fill(p, 0.9)
        dw, dh = p.w*0.8, p.h*0.7
        x0, y0 = p.X(0.1), p.Y(0.12)
        shape([(x0, y0), (x0 + dw, y0 + 3), (x0 + dw - 2, y0 + dh), (x0 + 2, y0 + dh - 2)], 1.0, LINE)
        crayon([(x0 + 10, y0 + 22), (x0 + dw - 10, y0 + 24)], P.SNOW_SHADE)
        srnka(x0 + dw*0.7, y0 + 24, 0.55, flip=True, shadow=False)
        joey(x0 + dw*0.25, y0 + 24, 0.7, shadow=False)
        opicka_sig(x0 + dw - 14, y0 + 12)
        hand_text(p.x, p.y + 4, p.w, "Hančin obrázek: srnka a Joey", "SH", 11)
    with Pn(*R[2]) as p:
        kitchen(p, table=False, evening=True)
        Hk(p.X(0.4), p.Y(0.03), 1.35, hat=False, mood="grin", right="hug", look=(1, 0))
        say(p, "Srnka a Joey jsou kamarádi.", *hd("hanka", p.X(0.4), p.Y(0.03), 1.35), w=120)
    with Pn(*R[3]) as p:
        kitchen(p, table=False, evening=True)
        A(p.X(0.18), p.Y(0.03), 1.2, hat=False, mood="surprised", right="front", look=(1, -0.2),
          item=lambda x, y: book(x + 14, y - 6, 0.8, rot=10))
        cipher_note(p.X(0.36), p.Y(0.32), 1.3, rot=-20)
        babicka(p.X(0.82), p.Y(0.03), 1.1, flip=True, mood="happy", look=(-1, 0))
        say(p, "V knížce z knihovny byl papírek. Samé hvězdičky a tečky!", *hd("alica", p.X(0.18), p.Y(0.03), 1.2), w=170,
            area=(0.0, 0.6))
        say(p, "To bude další případ.", *hd("babi", p.X(0.82), p.Y(0.03), 1.1), w=110, area=(0.62, 1.0))
    page_end()


# =================================================================== 23 activity
def page_quiz():
    with Pn(M, 40, W-2*M, H-80) as p:
        box = [(p.X(0.05), p.Y(0.905)), (p.X(0.95), p.Y(0.91)), (p.X(0.95), p.Y(0.905)+54), (p.X(0.05), p.Y(0.905)+52)]
        fill(box, 0.92)
        for a_, b_ in ((0, 1), (1, 2), (2, 3), (3, 0)): stroke([box[a_], box[b_]], 1.5)
        hand_text(p.X(0.05), p.Y(0.905)+18, p.w*0.9, "Detektivní zápisník", "SHB", 26)
        hand_text(p.X(0.05), p.Y(0.84), p.w*0.9, "Čí je to stopa? Spoj stopu se zvířetem.", "SHB", 15)
        prints_ = ["zajic", "srnka", "liska", "divocak", "veverka"]
        animals = [("divocak", lambda x, y: divocak(x - 6, y, 0.5, shadow=False)),
                   ("liska", lambda x, y: liska(x, y, 0.75, shadow=False)),
                   ("zajic", lambda x, y: zajic(x, y, 1.2, shadow=False)),
                   ("veverka", lambda x, y: veverka(x, y, 1.3)),
                   ("srnka", lambda x, y: srnka(x, y, 0.45, shadow=False))]
        rows_y = [p.Y(0.78) - i*58 for i in range(5)]
        for i, key_ in enumerate(prints_):
            hand_text(p.X(0.06), rows_y[i] - 4, 20, str(i + 1), "SHB", 15, align="left")
            PRINTS[key_](p.X(0.16), rows_y[i], 2.6, ink=True)
            dot(p.X(0.27), rows_y[i], 2.5, 0.2)
        for i, (key_, fig) in enumerate(animals):
            dot(p.X(0.62), rows_y[i], 2.5, 0.2)
            fig(p.X(0.78), rows_y[i] - 20)
            hand_text(p.X(0.9), rows_y[i] - 4, 20, "ABCDE"[i], "SHB", 15, align="left")
        y = rows_y[-1] - 50
        qs = ["1. Jak poznáš stopu divočáka?", "2. Proč liška skáče do sněhu?",
              "3. Jak ukousne větvičku zajíc? A jak srnka?", "4. Proč děda uhladil sníh?"]
        for q in qs:
            hand_text(p.X(0.06), y, p.w*0.9, q, "SH", 15, align="left")
            stroke([(p.X(0.06), y - 22), (p.X(0.94), y - 22)], 0.5, g=0.5)
            y -= 44
        y -= 10
        hidden_carrot(p.X(0.09), y - 6, 13)        # the legend: not one of the hidden ten
        hand_text(p.X(0.14), y - 4, p.w*0.82,
                  f"Srnka schovala v sešitě {N_HIDDEN} mrkviček, jako je tahle (ta se nepočítá). Najdeš je všechny?",
                  "SHB", 14, align="left", lead=18)
        ans = {k: "ABCDE"[[a for a, _ in animals].index(k)] for k in prints_}
        pages = ", ".join(map(str, HID[:-1])) + " a " + str(HID[-1]) if HID else ""
        with T(p.X(0.5), p.Y(0.015), 1.0, rot=180):
            hand_text(-p.w*0.45, 0, p.w*0.9, f"Mrkvičky jsou na stranách {pages}.", "SH", 10)
            hand_text(-p.w*0.45, -13, p.w*0.9, "Stopy: " + ", ".join(f"{i + 1}{ans[k]}" for i, k in enumerate(prints_)) + ".",
                      "SH", 10)
    page_end()


# =================================================================== 24 back cover: next time
def back_cover():
    with Pn(M, 40, W-2*M, H-80, bg=0.95) as p:
        hand_text(p.X(0.1), p.Y(0.93), p.w*0.8, "Příště v sešitě č. 9:", "SHB", 20)
        title(p.X(0.5), p.Y(0.84), "TAJNÁ ZPRÁVA V KNIHOVNĚ", 30)
        with Pn(p.X(0.08), p.Y(0.3), p.w*0.84, p.h*0.48, bg=0.9) as q:
            bg_fill(q, 0.88)
            for row in range(3):
                yy = q.Y(0.12) + row*q.h*0.3
                shape([(q.x, yy - 4), (q.x + q.w, yy - 4), (q.x + q.w, yy), (q.x, yy)], P.KRMELEC, BG)
                r = random.Random(row)
                xx = q.x + 6
                while xx < q.x + q.w - 20:
                    bw = r.uniform(10, 18); bh = r.uniform(q.h*0.18, q.h*0.25)
                    shape([(xx, yy), (xx + bw, yy), (xx + bw, yy + bh), (xx, yy + bh)], r.choice((0.45, 0.6, 0.75, 0.35)), BG*0.7)
                    xx += bw + 1
            cipher_note(q.X(0.5), q.Y(0.5), 2.2, rot=-6)
            masopust_mask(q.X(0.2), q.Y(0.75), 1.6, rot=8)
            masopust_mask(q.X(0.84), q.Y(0.2), 1.3, rot=-12)
        hand_text(p.X(0.1), p.Y(0.24), p.w*0.8, "V knížce z knihovny je schovaný papírek. Samé hvězdičky a tečky!", "SH", 16, lead=21)
        hand_text(p.X(0.1), p.Y(0.15), p.w*0.8, "A celá ves se chystá na Masopust.", "SHB", 16)
        hand_text(p.X(0.1), p.Y(0.015), p.w*0.8, "Velká a malá detektivka – sešit č. 8", "SH", 13, g=0.35)
    PAGE[0] += 1; cv.showPage()


cover(); page_cast(); page_snowmen(); page_morning(); page_suspects(); page_meadow(); page_hare(); page_boars()
page_forest(); page_guide(); page_list(); page_trap(); page_night(); page_clean(); page_stop(); page_reason()
page_follow(); page_deer(); page_shy(); page_krmelec(); page_cones(); page_end8(); page_quiz()
back_cover()
cv.save()
print("ok", PAGE[0] - 1, "pages")
import letter
if letter.MISSING: PROBLEMS.append("no glyph in the font for: " + " ".join(sorted(letter.MISSING)))
if len(HID) != N_HIDDEN: PROBLEMS.append(f"{len(HID)} hidden carrots drawn, the notebook promises {N_HIDDEN}")
for pr in PROBLEMS: print("ORDER/LAYOUT:", pr)
if PROBLEMS: sys.exit(1)
