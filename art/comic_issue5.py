"""Velká a malá detektivka, issue 5: Kdo staví sněhuláky? (outline: vault topics/comic-series/issue5-outline)"""
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
from props_extra import mug, stream
from attic import (young, chest, attic, bedroom, bed_side, blanket_side, bunting, shelf_toys, kids_drawing,
                   owlet, owl_box, old_photo, map_half, ladder, sled)
from pond import *
from village import *
from letter import Panel, caption, bubble, sfx, title, series_title, hand_text, lines_of, thought
from winter import *
from interior import stove
import chars3

W, H = A4
M = 28; GUT = 9; TOP = H - 30
OUT = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                   "comics", "velka_a_mala_detektivka", "05_kdo_stavi_snehulaky.pdf")
os.makedirs(os.path.dirname(OUT), exist_ok=True)
cv = canvas.Canvas(OUT, pagesize=A4); lib.set_canvas(cv)
cv.setTitle("Velká a malá detektivka – Případ č. 5: Kdo staví sněhuláky?")
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


def answer_snowmen(x, y, s=1.0):
    """the girls' answer: a waving snowman, three small ones holding hands, a star of twigs"""
    snowman_b(x, y, 1.15*s, right="wave", nose="carrot")
    for i in range(3):
        snowman_b(x + (52 + i*24)*s, y, 0.48*s, right="down", left="down", nose="carrot")
    for i in range(2):
        xx = x + (62 + i*24)*s
        stroke([(xx, y + 20*s), (xx + 4*s, y + 20*s)], LINE*1.2, g=P.BARK)
    star(x + 76*s, y + 62*s, 12*s, 1.0, w=LINE*1.6)


# =================================================================== 1 COVER
def cover():
    with Pn(M, 40, W-2*M, H-80) as p:
        gy = p.Y(0.4)
        winter_garden(p, gy, 4, house_x=0.8, house_s=1.15, trees=((0.08, 1.6),), flakes=36)
        snow_fence(p.X(0.55), p.X(1.02), gy - 10, 46, gap_at=p.X(0.72))
        pom(p.X(0.9), gy + 34, 6)                         # someone is peeking over the fence
        snowman_b(p.X(0.52), p.Y(0.06), 4.0, right="wave")
        snow_tracks_to(p.X(0.64), p.Y(0.05), p.X(0.72), gy - 12, 6, 2.0)
        A(p.X(0.2), p.Y(0.03), 3.1, mood="wow", right="lens", lens=True, look=(1, -0.6))
        Hk(p.X(0.84), p.Y(0.03), 2.6, flip=True, mood="surprised", right="point", look=(1, 0.3))
        joey(p.X(0.38), p.Y(0.03), 1.8, pose="sniff", mood="happy")
    box = [(M+34, H-236), (W-M-30, H-232), (W-M-34, H-48), (M+30, H-52)]
    fill([(x+3, y-3) for x, y in box], 0.0, 0.25); fill(box, 1.0)
    for a_, b_ in ((0, 1), (1, 2), (2, 3), (3, 0)): stroke([box[a_], box[b_]], 1.8)
    series_title(W/2, H-98, H-160, 40, 66)
    hand_text(M+40, H-190, W-2*M-80, "Alica a Hanka", "SHB", 20)
    hand_text(M+40, H-217, W-2*M-80, "Případ č. 5: Kdo staví sněhuláky?", "SH", 15)
    magnifier(M+82, H-120, ang=-30, r=17)
    star(W-M-100, H-118, 16, 1.0, w=1.6)
    page_end()


# =================================================================== 2 WHO IS WHO
def page_cast():
    with Pn(M, 40, W-2*M, H-80) as p:
        hand_text(p.X(0.05), p.Y(0.95), p.w*0.9, "Kdo je kdo", "SHB", 30)
        def mystery(x, y):
            shape(ell(x, y + 40, 20, 26, 30), 0.35)
            shape(ell(x, y + 76, 13, 13, 30), 0.35)
            pom(x, y + 94, 6)
            hand_text(x - 10, y + 32, 20, "?", "SHB", 24, g=1.0)
        cells = [
            ("Alica", "zase zdravá a hned do sněhu", lambda x, y: A(x, y, 0.9, mood="happy", right="lens", lens=True)),
            ("Hanka", "čte obrázky", lambda x, y: Hk(x, y, 1.1, mood="grin")),
            ("Joey", "má nejlepší nos", lambda x, y: joey(x, y, 1.2, mood="happy")),
            ("Babička", "vstává ze všech nejdřív", lambda x, y: babicka(x, y, 0.82, mood="happy")),
            ("Děda Honza", "založil Klub Hvězdička", lambda x, y: deda(x, y, 0.74, mood="happy")),
            ("Tonda", "má sáňky a legrácky", lambda x, y: Td(x, y, 0.88, mood="grin")),
            ("Franta", "kamarád z klubu, pěstuje zeleninu", lambda x, y: franta(x, y, 0.7, mood="happy")),
            ("Sněhulák", "kdo ho postavil?", lambda x, y: snowman_b(x, y, 1.0, right="wave")),
            ("???", "nikdo ho nezná", mystery),
        ]
        cw, ch = p.w/3, p.h*0.205
        for i, (name, line, fig) in enumerate(cells):
            cx = p.x + (i % 3)*cw; cy = p.Y(0.9) - (i//3 + 1)*ch
            shape(rrect(cx + 8, cy + 6, cw - 16, ch - 12, 10), 0.97, 1.2)
            fig(cx + cw/2, cy + 50)
            hand_text(cx + 10, cy + 32, cw - 20, name, "SHB", 15)
            hand_text(cx + 10, cy + 16, cw - 20, line, "SH", 11)
        by = p.y + 8; bh = p.Y(0.9) - 3*ch - by - 8
        shape(rrect(p.x + 8, by, p.w - 16, bh, 10), P.PHOTO_BG, 1.2)
        hand_text(p.x + 20, by + bh - 28, p.w*0.6, "Minule…", "SHB", 17, align="left")
        hand_text(p.x + 20, by + bh - 52, p.w*0.6,
                  "Hanka přečetla Frantův obrázkový dopis. Rybář z rybníka byl Franta! Hodiny na věži zase jdou a Klub Hvězdička je zase celý.",
                  "SH", 13, align="left", lead=17)
        church_clock(p.X(0.82), by + bh/2, 38, hour=12)
    page_end()


# =================================================================== 3 first snow
def page_first_snow():
    R = rows([(260, [1]), (240, [0.5, 0.5]), (250, [1])])
    with Pn(*R[0]) as p:
        fy = bedroom_night(p)
        A(p.X(0.55), fy, 1.35, hat=False, mood="wow", right="point", look=(1, 0.4))
        Hk(p.X(0.4), fy, 1.3, hat=False, mood="grin", right="up", look=(1, 0.4))
        cap(p, "Večer začalo sněžit.", w=170)
        say(p, "Sněží! Sněží!", *hd("hanka", p.X(0.4), fy, 1.3), w=110, area=(0.0, 0.6))
        say(p, "První sníh!", *hd("alica", p.X(0.55), fy, 1.35), w=100, area=(0.0, 0.62))
    with Pn(*R[1]) as p:
        kitchen(p, table=False, evening=True)
        babicka(p.X(0.3), p.Y(0.03), 1.15, mood="happy", right="front", look=(1, 0))
        Hk(p.X(0.75), p.Y(0.03), 1.1, hat=False, flip=True, mood="grin", look=(1, 0.3))
        say(p, "Ráno postavíme sněhuláka!", *hd("babi", p.X(0.3), p.Y(0.03), 1.15), w=140)
        say(p, "Velikánského!", *hd("hanka", p.X(0.75), p.Y(0.03), 1.1), w=110)
    with Pn(*R[2]) as p:
        bedroom_night(p, window=False)
        kid_in_bed(alica, 45, p.X(0.02), p.X(0.46), p.y + 48, 1.0, mood="sleepy")
        kid_in_bed(hanka, 31, p.X(0.54), p.X(0.96), p.y + 48, 1.1, mood="sleepy")
        joey(p.X(0.5), p.y + 14, 0.7, mood="sleepy")
        cap(p, "Všichni spí.", w=110)
        sfx(p.X(0.62), p.Y(0.7), "CHRRR…", 16, -4)
    with Pn(*R[3]) as p:
        winter_garden(p, p.Y(0.22), 3, house_x=0.2, house_s=1.1, trees=((0.86, 1.3),), night=True, flakes=50)
        snow_fence(p.X(0.4), p.X(1.02), p.Y(0.2), 40)
        cap(p, "A venku padá a padá sníh.", w=210)
    page_end()


# =================================================================== 4 the morning
def page_morning():
    R = rows([(300, [1]), (220, [0.5, 0.5]), (230, [1])])
    with Pn(*R[0]) as p:
        gy = p.Y(0.28)
        winter_garden(p, gy, 5, trees=((0.92, 1.2),))
        snow_fence(p.X(0.62), p.X(1.02), gy - 6, 44, gap_at=p.X(0.8))
        snowman_b(p.X(0.5), p.Y(0.08), 1.9, right="wave")
        snow_tracks_to(p.X(0.56), p.Y(0.06), p.X(0.8), gy - 8, 6, 1.1)
        A(p.X(0.12), p.Y(0.03), 1.25, mood="surprised", look=(1, 0))
        Hk(p.X(0.25), p.Y(0.03), 1.25, mood="wow", right="point", look=(1, 0))
        hidden_triangle(p.X(0.69), gy + 30)
        cap(p, "Ráno.", w=70)
        say(p, "Sněhulák! Kdo ho postavil?", *hd_h("hanka", p.X(0.25), p.Y(0.03), 1.25), w=150, area=(0.0, 0.55))
        say(p, "My ne. Babička taky ne…", *hd_h("alica", p.X(0.12), p.Y(0.03), 1.25), w=140, area=(0.0, 0.55))
    with Pn(*R[1]) as p:
        winter_garden(p, p.Y(0.3), 6, hills_=False)
        snowman_b(p.X(0.62), p.Y(0.05), 1.6, right="wave")
        Hk(p.X(0.3), p.Y(0.03), 1.4, mood="grin", right="up", look=(1, 0.3))
        say(p, "Je malý jako já!", *hd_h("hanka", p.X(0.3), p.Y(0.03), 1.4), w=120, area=(0.0, 0.6))
    with Pn(*R[2]) as p:
        winter_garden(p, p.Y(0.4), 7, hills_=False)
        snow_tracks_to(p.X(0.2), p.Y(0.12), p.X(0.9), p.Y(0.2), 7, 1.6)
        joey(p.X(0.4), p.Y(0.06), 1.15, pose="sniff", mood="happy")
        sfx(p.X(0.55), p.Y(0.7), "ČMUCH ČMUCH!", 16, -6)
    with Pn(*R[3]) as p:
        gy = p.Y(0.5)
        winter_garden(p, gy, 8, house_x=0.12, house_s=0.8)
        snow_fence(p.X(0.42), p.X(1.02), gy - 6, 40, gap_at=p.X(0.7))
        snow_tracks_to(p.X(0.4), p.Y(0.1), p.X(0.7), gy - 10, 7, 1.1)
        A(p.X(0.3), p.Y(0.03), 1.2, mood="determined", right="point", look=(1, 0.2))
        say(p, "Malé stopy. Vedou k díře v plotě!", *hd_h("alica", p.X(0.3), p.Y(0.03), 1.2), w=190, area=(0.0, 0.6))
    page_end()


# =================================================================== 5 under the magnifier
def page_lupa():
    R = rows([(320, [1]), (210, [0.5, 0.5]), (220, [1])])
    with Pn(*R[0]) as p:
        winter_garden(p, p.Y(0.25), 9, hills_=False)
        snowman_b(p.X(0.68), p.Y(0.5) - 56*5.0, 5.0, right="wave")
        A(p.X(0.2), p.Y(0.03), 1.6, mood="think", right="lens", lens=True, look=(1, 0.5))
        keep_clear(p, p.X(0.45), p.Y(0.35), p.X(0.92), p.Y(0.98), "snowman")
        say(p, "Oči jsou ořechy. Knoflíky jsou šišky.", *hd_h("alica", p.X(0.2), p.Y(0.03), 1.6), w=180, area=(0.0, 0.45))
        say(p, "A nos… to není mrkev! Je bílý!", *hd_h("alica", p.X(0.2), p.Y(0.03), 1.6), w=170, area=(0.0, 0.45))
    with Pn(*R[1]) as p:
        bg_fill(p, P.SNOW)
        star_print(p.X(0.5), p.Y(0.45), 7.0, 8)
        cap(p, "Stopa zblízka.", w=120)
    with Pn(*R[2]) as p:
        bg_fill(p, 0.9)
        notebook_big(p.X(0.07), p.Y(0.1), p.w*0.86, p.h*0.82, "PŘÍPAD Č. 5:",
                     ["1. malé stopy", "   s hvězdičkami", "2. bílý nos", "3. ořechy a šišky"])
    with Pn(*R[3]) as p:
        kitchen(p)
        babicka(p.X(0.7), p.Y(0.03), 1.15, flip=True, mood="happy", right="front", look=(1, 0))
        A(p.X(0.25), p.Y(0.03), 1.2, hat=False, mood="think", right="chin", look=(1, 0))
        hidden_triangle(p.X(0.08), p.Y(0.2))
        say(p, "Babičko, nechybí ti mrkev?", *hd("alica", p.X(0.25), p.Y(0.03), 1.2), w=150)
        say(p, "Nechybí. Mám je spočítané.", *hd("babi", p.X(0.7), p.Y(0.03), 1.15), w=150)
    page_end()


# =================================================================== 6 following the prints
def page_follow():
    R = rows([(250, [1]), (250, [0.5, 0.5]), (250, [1])])
    with Pn(*R[0]) as p:
        gy = p.Y(0.2)
        winter_garden(p, gy, 10, hills_=False)
        snow_fence(p.x - 5, p.x + p.w + 5, p.Y(0.06), 70, gap_at=p.X(0.25))
        Hk(p.X(0.25), p.Y(0.03), 1.2, mood="grin", legs="walk", look=(1, 0))
        A(p.X(0.66), p.Y(0.03), 1.25, flip=True, mood="surprised", look=(1, 0))
        say(p, "Tudy se vejdu jen já!", *hd_h("hanka", p.X(0.25), p.Y(0.03), 1.2), w=130, area=(0.0, 0.5))
        say(p, "Tak běž napřed. Já to oběhnu!", *hd_h("alica", p.X(0.66), p.Y(0.03), 1.25), w=150, area=(0.45, 1.0))
    with Pn(*R[1]) as p:
        winter_garden(p, p.Y(0.45), 11, hills_=False)
        fill([(p.x - 5, p.Y(0.12)), (p.x + p.w + 5, p.Y(0.12)), (p.x + p.w + 5, p.Y(0.32)), (p.x - 5, p.Y(0.32))], P.PRINT_SHADE)
        for xx in range(int(p.x), int(p.x + p.w), 9):
            for yy in (p.Y(0.15), p.Y(0.27)): stroke([(xx, yy - 3), (xx + 5, yy + 3)], 1.0, g=0.5)
        snow_tracks_to(p.X(0.05), p.Y(0.02), p.X(0.4), p.Y(0.1), 4, 1.0)
        A(p.X(0.72), p.Y(0.33), 1.0, flip=True, mood="worried", look=(1, -0.5))
        say(p, "Tady stopy končí. Jel tu traktor.", *hd_h("alica", p.X(0.72), p.Y(0.33), 1.0), w=150)
    with Pn(*R[2]) as p:
        winter_garden(p, p.Y(0.5), 12, hills_=False)
        snow_fence(p.x - 5, p.x + p.w + 5, p.Y(0.1), 60, gap_at=p.X(0.3))
        mitten(p.X(0.38), p.Y(0.06), 1.3, rot=20)          # Hanka loses her mitten (she doesn't notice)
        Hk(p.X(0.75), p.Y(0.03), 1.1, flip=True, mood="happy", legs="walk", look=(1, 0))
        say(p, "Alico, počkej na mě!", *hd_h("hanka", p.X(0.75), p.Y(0.03), 1.1), w=120, area=(0.4, 1.0))
    with Pn(*R[3]) as p:
        winter_garden(p, p.Y(0.35), 13, house_x=0.85, house_s=0.8)
        for i in range(5): big_print(p.X(0.08) + i*22, p.Y(0.08) + (i % 2)*8, 1.0, 90)
        sled(p.X(0.4), p.Y(0.05), 0.7)
        Td(p.X(0.22), p.Y(0.03), 1.15, mood="grin", right="hip", look=(1, 0))
        A(p.X(0.62), p.Y(0.03), 1.15, flip=True, mood="think", right="chin", look=(1, 0))
        say(p, "Já? Já stavím jenom obry! Tohle je prcek.", *hd_h("tonda", p.X(0.22), p.Y(0.03), 1.15), w=180, area=(0.0, 0.5))
        say(p, "Tonda dělá rád legrácky… Podezřelý číslo 1.", *hd_h("alica", p.X(0.62), p.Y(0.03), 1.15),
            w=170, whisper=True, area=(0.45, 0.8))
    page_end()


# =================================================================== 7 the night watch
def page_watch():
    R = rows([(260, [1]), (240, [0.5, 0.5]), (250, [1])])
    with Pn(*R[0]) as p:
        fy = bedroom_night(p)
        A(p.X(0.2), fy, 1.35, hat=False, mood="determined", right="front", look=(1, 0),
          item=lambda x, y: vysilacka(x + 2, y - 6, 1.0, rot=-20))
        Hk(p.X(0.42), fy, 1.25, hat=False, mood="determined", torch=True, right="lens", look=(1, 0))
        cap(p, "Noční hlídka.", w=120)
        say(p, "Dneska ho chytíme. Budu hlídat celou noc!", *hd("alica", p.X(0.2), fy, 1.35), w=170, area=(0.0, 0.6))
        say(p, "Já budu svítit!", *hd("hanka", p.X(0.42), fy, 1.25), w=110, area=(0.0, 0.6))
    with Pn(*R[1]) as p:
        fy = bedroom_night(p, window=False)
        wall_clock(p.X(0.82), p.Y(0.8), 16)
        A(p.X(0.4), fy, 1.3, hat=False, mood="sleepy", look=(1, 0))
        say(p, "Ještě… chvilku…", *hd("alica", p.X(0.4), fy, 1.3), w=110)
    with Pn(*R[2]) as p:
        fy = bedroom_night(p, window=False)
        kid_in_bed(alica, 45, p.X(0.02), p.X(0.5), p.y + 48, 0.95, mood="sleepy",
                   item=lambda x, y: vysilacka(x + 2, y - 6, 0.8, rot=-20))
        kid_in_bed(hanka, 31, p.X(0.54), p.X(0.98), p.y + 48, 1.0, mood="sleepy", torch=True, right="lens")
        joey(p.X(0.52), fy, 0.6, flip=True, mood="sleepy")
        sfx(p.X(0.4), p.Y(0.8), "CHRRR…", 16, -6)
    with Pn(*R[3]) as p:
        gy = p.Y(0.25)
        winter_garden(p, gy, 14, night=True, flakes=30, trees=((0.08, 1.2),))
        shape([(p.x - 5, p.y - 5), (p.X(0.15), p.y - 5), (p.X(0.15), p.y + p.h + 5), (p.x - 5, p.y + p.h + 5)], P.DOOR_FRAME, BG)
        shape([(p.X(0.85), p.y - 5), (p.x + p.w + 5, p.y - 5), (p.x + p.w + 5, p.y + p.h + 5), (p.X(0.85), p.y + p.h + 5)], P.DOOR_FRAME, BG)
        snowman_b(p.X(0.45), p.Y(0.06), 1.4, right="wave")
        betka(p.X(0.8), p.Y(0.04), 0.7, flip=True, mood="happy", legs="walk")   # only the reader sees her
        bg_fill(p, 0.0, 0.15)
        hidden_triangle(p.X(0.62), p.Y(0.07))
        cap(p, "Ale někdo nespí…", w=150)
    page_end()


# =================================================================== 8 the second morning
def page_second():
    R = rows([(300, [1]), (220, [0.5, 0.5]), (230, [1])])
    with Pn(*R[0]) as p:
        gy = p.Y(0.3)
        winter_garden(p, gy, 15, trees=((0.9, 1.2),))
        snowman_b(p.X(0.36), p.Y(0.07), 1.8, right="hold", item=lambda x, y: None)
        snowman_b(p.X(0.62), p.Y(0.07), 1.5, right="wave")
        snow_dog(p.X(0.47), p.Y(0.05), 1.4)
        Hk(p.X(0.1), p.Y(0.03), 1.2, mood="wow", right="point", look=(1, 0))
        hidden_triangle(p.X(0.79), p.Y(0.1))
        cap(p, "Druhé ráno.", w=100)
        say(p, "Další sněhulák! A má pejska!", *hd_h("hanka", p.X(0.1), p.Y(0.03), 1.2), w=150, area=(0.0, 0.5))
    with Pn(*R[1]) as p:
        winter_garden(p, p.Y(0.35), 16, hills_=False)
        snow_dog(p.X(0.65), p.Y(0.05), 2.0, flip=True)
        joey(p.X(0.22), p.Y(0.04), 1.15, mood="bark")
        sfx(p.X(0.4), p.Y(0.75), "HAF?", 20, -6)
    with Pn(*R[2]) as p:
        winter_garden(p, p.Y(0.35), 17, hills_=False)
        A(p.X(0.3), p.Y(0.03), 1.3, mood="sad", look=(1, 0))
        say(p, "My jsme zase všichni usnuli…", *hd_h("alica", p.X(0.3), p.Y(0.03), 1.3), w=140)
    with Pn(*R[3]) as p:
        bg_fill(p, P.SNOW_SKY)
        snow_fence(p.x - 5, p.x + p.w + 5, p.Y(0.0), 170, step=40)
        red_thread(p.X(0.52), p.Y(0.6), 2.2)
        A(p.X(0.2), head_y(p, 0.55, 89.8, 1.6), 1.6, mood="wow", right="lens", lens=True, look=(1, 0.3), shadow=False)
        say(p, "Červená vlna! Jako z bambule na čepici.", p.X(0.72), p.Y(0.62), w=170, area=(0.55, 1.0))
    page_end()


# =================================================================== 9 the suspect board
def page_board():
    R = rows([(240, [1]), (240, [0.5, 0.5]), (270, [1])])
    with Pn(*R[0]) as p:
        kitchen(p, table=False)
        babicka(p.X(0.7), p.Y(0.03), 1.15, flip=True, mood="whisper", right="hush", look=(1, 0),
                item=lambda x, y: mitten(x - 6, y - 4, 0.9, g=0.85))
        A(p.X(0.25), p.Y(0.03), 1.2, hat=False, mood="think", look=(1, 0))
        cap(p, "Babička přišla zvenku. Úplně brzo ráno.", w=230)
        say(p, "Babičko, proč máš mokré rukavice?", *hd("alica", p.X(0.25), p.Y(0.03), 1.2), w=170)
        say(p, "To je tajemství!", *hd("babi", p.X(0.7), p.Y(0.03), 1.15), w=110)
    with Pn(*R[1]) as p:
        kitchen(p, table=False)
        A(p.X(0.3), p.Y(0.03), 1.2, hat=False, mood="whisper", right="cheek", look=(1, 0))
        Hk(p.X(0.72), p.Y(0.03), 1.15, hat=False, flip=True, mood="surprised", look=(1, 0.3))
        say(p, "Babička vstává první. Podezřelá číslo 2!", *hd("alica", p.X(0.3), p.Y(0.03), 1.2), w=170, whisper=True)
    with Pn(*R[2]) as p:
        kitchen(p, table=False)
        Hk(p.X(0.3), p.Y(0.03), 1.2, hat=False, mood="worried", look=(1, 0))
        A(p.X(0.72), p.Y(0.03), 1.2, hat=False, flip=True, mood="determined", right="up", look=(1, 0))
        say(p, "Babička je hodná!", *hd("hanka", p.X(0.3), p.Y(0.03), 1.2), w=105, x=p.X(0.03), y=p.Y(0.97))
        say(p, "Detektiv podezírá každého.", *hd("alica", p.X(0.72), p.Y(0.03), 1.2), w=120, x=p.X(0.52), y=p.Y(0.97))
    with Pn(*R[3]) as p:
        bg_fill(p, 0.9)
        notebook_big(p.X(0.08), p.Y(0.08), p.w*0.84, p.h*0.84, "PODEZŘELÍ:",
                     ["1. Tonda: dělá legrácky,", "    má sáňky", "2. babička: vstává první,", "    mokré rukavice",
                      "3. ??? : červená bambule"])
    page_end()


# =================================================================== 10 cleared
def page_cleared():
    R = rows([(250, [1]), (250, [0.5, 0.5]), (250, [1])])
    with Pn(*R[0]) as p:
        kitchen(p, evening=True)
        for i in range(5): pernicek(p.X(0.42) + i*22, p.Y(0.4), 1.0, rot=(i - 2)*8)
        babicka(p.X(0.25), p.Y(0.03), 1.15, mood="grin", right="front", look=(1, 0),
                item=lambda x, y: (fill(ell(x, y, 5, 4, 14), 1.0), dot(x + 2, y + 2, 1, 0.8)))
        A(p.X(0.78), p.Y(0.03), 1.15, hat=False, flip=True, mood="wow", look=(1, 0))
        cap(p, "Druhý den, ještě za tmy.", w=200)
        say(p, "Peču perníčky na advent. Rukavice mám mokré od těsta!", *hd("babi", p.X(0.25), p.Y(0.03), 1.15), w=200)
        say(p, "Babička prověřena!", *hd("alica", p.X(0.78), p.Y(0.03), 1.15), w=120)
    with Pn(*R[1]) as p:
        winter_garden(p, p.Y(0.4), 18, hills_=False)
        for i in range(3): big_print(p.X(0.55) + i*26, p.Y(0.12) + (i % 2)*10, 1.4, 90)
        star_print(p.X(0.88), p.Y(0.14), 1.4, 90)
        Td(p.X(0.25), p.Y(0.03), 1.2, mood="grin", right="point", look=(1, -0.5))
        say(p, "Moje boty jsou obří!", *hd_h("tonda", p.X(0.25), p.Y(0.03), 1.2), w=120)
    with Pn(*R[2]) as p:
        winter_garden(p, p.Y(0.4), 19, hills_=False)
        runner_tracks(p.X(0.3), p.Y(0.12), p.X(1.05), p.Y(0.22))
        A(p.X(0.2), p.Y(0.03), 1.2, mood="think", right="chin", look=(1, -0.3))
        say(p, "Modrá čepice, žádná bambule. Sáňky dělají dlouhé čáry.", *hd_h("alica", p.X(0.2), p.Y(0.03), 1.2), w=180)
    with Pn(*R[3]) as p:
        winter_garden(p, p.Y(0.3), 20, house_x=0.85, house_s=0.8)
        sled(p.X(0.52), p.Y(0.05), 0.8)
        hidden_triangle(p.X(0.47), p.Y(0.11))
        A(p.X(0.2), p.Y(0.03), 1.2, mood="happy", look=(1, 0))
        Td(p.X(0.72), p.Y(0.03), 1.2, flip=True, mood="wow", right="up", look=(1, 0))
        say(p, "Tonda prověřen!", *hd_h("alica", p.X(0.2), p.Y(0.03), 1.2), w=110, x=p.X(0.03), y=p.Y(0.95))
        say(p, "Bílý nos? To bude pastinák! Ten pěstuje jenom Franta.", *hd_h("tonda", p.X(0.72), p.Y(0.03), 1.2), w=200,
            x=p.X(0.34), y=p.Y(0.95))
    page_end()


# =================================================================== 11 at Franta's
def hallway(p):
    planks(p, P.PLANKS, 26, 9, knots=False)
    floor_y = p.Y(0.1)
    shape([(p.x - 5, p.y - 5), (p.x + p.w + 5, p.y - 5), (p.x + p.w + 5, floor_y), (p.x - 5, floor_y)], P.FLOOR, BG)
    return floor_y


def page_franta():
    R = rows([(270, [1]), (240, [0.5, 0.5]), (240, [1])])
    with Pn(*R[0]) as p:
        gy = p.Y(0.2)
        winter_garden(p, gy, 21, house_x=0.62, house_s=1.6, trees=((0.12, 1.3),))
        franta(p.X(0.62), gy - 2, 1.05, mood="happy", right="wave", look=(-1, 0))
        A(p.X(0.25), p.Y(0.03), 1.1, mood="happy", look=(1, 0.3))
        Hk(p.X(0.37), p.Y(0.03), 1.05, mood="grin", look=(1, 0.3))
        cap(p, "U Franty.", w=90)
        say(p, "Holky! Pojďte dál, venku mrzne.", *hd("franta", p.X(0.62), gy - 2, 1.05), w=160, area=(0.45, 1.0))
    with Pn(*R[1]) as p:
        fy = hallway(p)
        parsnip_crate(p.X(0.55), fy, 1.6)
        A(p.X(0.18), fy, 1.2, hat=False, mood="wow", right="cheek", look=(1, -0.3))
        say(p, "Pastinák!", *hd("alica", p.X(0.18), fy, 1.2), w=90, whisper=True)
    with Pn(*R[2]) as p:
        fy = hallway(p)
        stove(p.X(0.55), p.X(0.85), fy, p.Y(0.6))
        small_boots(p.X(0.3), fy, 1.5)
        Hk(p.X(0.14), fy, 1.15, hat=False, mood="wow", right="point", look=(1, -0.5))
        say(p, "Malé botičky. S hvězdičkami!", *hd("hanka", p.X(0.14), fy, 1.15), w=130, whisper=True, area=(0.0, 0.55))
    with Pn(*R[3]) as p:
        fy = hallway(p)
        dx0, dx1 = p.X(0.7), p.X(0.86)
        shape([(dx0, fy), (dx1, fy), (dx1, p.Y(0.85)), (dx0, p.Y(0.85))], 0.25, BG)
        curtain = [(dx0, p.Y(0.85))] + bez((dx0, p.Y(0.85)), (dx0 + 10, p.Y(0.5)), (dx0 + 4, p.Y(0.3)), (dx0 + 14, fy)) + \
                  [(dx1, fy), (dx1, p.Y(0.85))]
        shape(curtain, P.CLOTH_CHECK, BG)
        pom(dx0 + 8, p.Y(0.45), 5)                       # a pompom peeks from behind the curtain
        franta(p.X(0.4), fy, 1.0, flip=True, mood="grin", right="front", look=(1, 0))
        A(p.X(0.12), fy, 1.05, hat=False, mood="think", look=(1, 0))
        say(p, "Sněhuláci? Ti chodí sami, holky.", *hd("franta", p.X(0.4), fy, 1.0), w=160, area=(0.2, 0.7))
    page_end()


# =================================================================== 12 the third morning
def page_third():
    R = rows([(320, [1]), (210, [0.5, 0.5]), (220, [1])])
    with Pn(*R[0]) as p:
        gy = p.Y(0.3)
        winter_garden(p, gy, 22, trees=((0.92, 1.2),))
        snowman_b(p.X(0.55), p.Y(0.07), 2.0, right="hold", item=lambda x, y: mitten(x + 3, y - 6, 0.9, rot=-30))
        Hk(p.X(0.18), p.Y(0.03), 1.3, mood="wow", right="point", legs="walk", look=(1, 0))
        A(p.X(0.32), p.Y(0.03), 1.25, mood="surprised", look=(1, 0))
        hidden_triangle(p.X(0.8), p.Y(0.12))
        cap(p, "Třetí ráno.", w=100)
        say(p, "Moje rukavička!", *hd_h("hanka", p.X(0.18), p.Y(0.03), 1.3), w=120, area=(0.0, 0.5))
    with Pn(*R[1]) as p:
        winter_garden(p, p.Y(0.35), 23, hills_=False)
        Hk(p.X(0.4), p.Y(0.03), 1.5, mood="happy", right="front", look=(1, 0),
           item=lambda x, y: mitten(x - 2, y - 6, 1.1))
        say(p, "Ztratila jsem ji u plotu!", *hd_h("hanka", p.X(0.4), p.Y(0.03), 1.5), w=130)
    with Pn(*R[2]) as p:
        winter_garden(p, p.Y(0.35), 24, hills_=False)
        A(p.X(0.3), p.Y(0.03), 1.3, mood="think", right="chin", look=(1, 0))
        Hk(p.X(0.72), p.Y(0.03), 1.2, flip=True, mood="happy", look=(1, 0))
        say(p, "Kdo ji našel, vrátil nám ji.", *hd_h("alica", p.X(0.3), p.Y(0.03), 1.3), w=135, x=p.X(0.03), y=p.Y(0.97))
        say(p, "Je hodný!", *hd_h("hanka", p.X(0.72), p.Y(0.03), 1.2), w=85, x=p.X(0.6), y=p.Y(0.97))
    with Pn(*R[3]) as p:
        gy = p.Y(0.3)
        winter_garden(p, gy, 25)
        snowman_b(p.X(0.2), p.Y(0.06), 1.4, right="wave")
        snowman_b(p.X(0.47), p.Y(0.06), 1.4, right="down")
        snow_dog(p.X(0.58), p.Y(0.04), 1.0)
        snowman_b(p.X(0.82), p.Y(0.06), 1.4, right="hold", item=lambda x, y: mitten(x + 3, y - 6, 0.9, rot=-30))
        cap(p, "Tři sněhuláci za tři noci.", w=210)
    page_end()


# =================================================================== 13 Alica reads the snowmen
def page_read():
    R = rows([(330, [1]), (200, [1]), (215, [0.5, 0.5])])
    with Pn(*R[0]) as p:
        bg_fill(p, P.SNOW_SKY)
        cells = [("AHOJ!", lambda x, y: snowman_b(x, y, 1.5, right="wave")),
                 ("MÁM RÁDA PEJSKY", lambda x, y: (snowman_b(x - 14, y, 1.3, right="down"), snow_dog(x + 10, y, 0.9))),
                 ("NAŠLA JSEM TO", lambda x, y: snowman_b(x, y, 1.5, right="hold", item=lambda a, b: mitten(a + 3, b - 6, 0.9, rot=-30)))]
        cw = p.w/3
        for i, (txt, fig) in enumerate(cells):
            cx = p.x + i*cw
            shape(rrect(cx + 10, p.Y(0.18), cw - 20, p.h*0.74, 10), 1.0, 1.2)
            fig(cx + cw/2, p.Y(0.24))
            hand_text(cx + 14, p.Y(0.07), cw - 28, txt, "SHB", 14)
            if i < 2:
                stroke([(cx + cw - 8, p.Y(0.55)), (cx + cw + 8, p.Y(0.55))], 2.0)
                stroke([(cx + cw + 8, p.Y(0.55)), (cx + cw + 2, p.Y(0.59))], 2.0)
                stroke([(cx + cw + 8, p.Y(0.55)), (cx + cw + 2, p.Y(0.51))], 2.0)
        cap(p, "Alica si sněhuláky nakreslila za sebou. Jako Frantův dopis.", w=300)
    with Pn(*R[1]) as p:
        kitchen(p, table=False)
        A(p.X(0.12), p.Y(0.03), 1.25, hat=False, mood="determined", right="up", look=(1, 0))
        say(p, "Sněhuláci jsou dopis! Někdo nám píše obrázky.", *hd("alica", p.X(0.12), p.Y(0.03), 1.25), w=180,
            x=p.X(0.2), y=p.Y(0.95))
        say(p, "Botičky s hvězdičkami, červená bambule, pastinák. Všechno vede k Frantovi!",
            *hd("alica", p.X(0.12), p.Y(0.03), 1.25), w=220, x=p.X(0.55), y=p.Y(0.95))
    with Pn(*R[2]) as p:
        kitchen(p, table=False)
        A(p.X(0.3), p.Y(0.03), 1.2, hat=False, mood="whisper", right="chin", look=(1, 0))
        say(p, "U Franty bydlí někdo malý. A stydí se zaklepat.", *hd("alica", p.X(0.3), p.Y(0.03), 1.2), w=170)
    with Pn(*R[3]) as p:
        kitchen(p, table=False)
        Hk(p.X(0.45), p.Y(0.03), 1.25, hat=False, mood="wow", right="up", look=(1, 0.3))
        hidden_triangle(p.X(0.88), p.Y(0.2))
        say(p, "Jako Franta, když byl malý!", *hd("hanka", p.X(0.45), p.Y(0.03), 1.25), w=140)
    page_end()


# =================================================================== 14 catch or answer?
def bell(x, y, s=1.0):
    with T(x, y, s):
        shape(bez((-6, 0), (-6, 10), (6, 10), (6, 0)) + [(-6, 0)], P.BRASS, LINE*0.8)
        dot(0, -1.5, 1.6, 0.3)
        stroke([(0, 10), (0, 16)], LINE*0.8)


def page_choice():
    R = rows([(250, [1]), (250, [0.5, 0.5]), (250, [1])])
    with Pn(*R[0]) as p:
        gy = p.Y(0.3)
        winter_garden(p, gy, 26, hills_=False)
        snow_fence(p.x - 5, p.x + p.w + 5, p.Y(0.08), 60)
        stroke([(p.X(0.35), p.Y(0.08) + 50), (p.X(0.8), p.Y(0.08) + 52)], 0.8, g=0.3)
        bell(p.X(0.58), p.Y(0.08) + 34, 1.2)
        A(p.X(0.2), p.Y(0.03), 1.3, mood="determined", right="up", look=(1, 0))
        say(p, "Dneska ho chytíme! Zvonek na plot a cink!", *hd_h("alica", p.X(0.2), p.Y(0.03), 1.3), w=180)
    with Pn(*R[1]) as p:
        winter_garden(p, p.Y(0.35), 27, hills_=False)
        Hk(p.X(0.4), p.Y(0.03), 1.4, mood="worried", look=(1, 0))
        say(p, "Když ho chytíš, bude se bát.", *hd_h("hanka", p.X(0.4), p.Y(0.03), 1.4), w=140)
    with Pn(*R[2]) as p:
        winter_garden(p, p.Y(0.35), 28, hills_=False)
        Hk(p.X(0.4), p.Y(0.03), 1.4, mood="determined", right="up", look=(1, 0.3))
        say(p, "Musíme mu odpovědět. Obrázkem!", *hd_h("hanka", p.X(0.4), p.Y(0.03), 1.4), w=150)
    with Pn(*R[3]) as p:
        winter_garden(p, p.Y(0.3), 29, house_x=0.88, house_s=0.8)
        A(p.X(0.2), p.Y(0.03), 1.2, mood="happy", right="front", look=(1, 0))
        babicka(p.X(0.55), p.Y(0.03), 1.1, flip=True, mood="grin", right="up", look=(1, 0),
                item=lambda x, y: shape([(x, y), (x + 14, y + 2), (x, y - 3)], P.CARROT, LINE*0.6))
        say(p, "…Máš pravdu, Hanko. Postavíme mu sněhuláky!", *hd_h("alica", p.X(0.2), p.Y(0.03), 1.2), w=190, area=(0.0, 0.5))
        say(p, "Pomůžu vám. Tentokrát s mrkví!", *hd("babi", p.X(0.55), p.Y(0.03), 1.1), w=150, area=(0.4, 0.85))
    page_end()


# =================================================================== 15 STOP, DETEKTIVE!
def page_stop():
    with Pn(M, 40, W-2*M, H-80, bg=0.95) as p:
        title(p.X(0.5), p.Y(0.92), "STOP, DETEKTIVE!", 44)
        hand_text(p.X(0.05), p.Y(0.86), p.w*0.9, "Už máš všechny stopy.", "SHB", 18)
        cw, ch = p.w*0.3, p.h*0.215
        items = [
            ("malé stopy s hvězdičkami", lambda x, y: (star_print(x - 12, y + 20, 2.0, 10), star_print(x + 14, y + 34, 2.0, -6))),
            ("bílý nos – pastinák", lambda x, y: parsnip(x, y + 50, 1.5, rot=-80)),
            ("červená vlna na plotě", lambda x, y: red_thread(x - 20, y + 30, 2.4)),
            ("malé botičky u Frantových kamen", lambda x, y: small_boots(x - 22, y + 4, 1.5)),
            ("bambule za závěsem", lambda x, y: (shape(rrect(x - 26, y, 52, 70, 4), P.CLOTH_CHECK, 1.0), pom(x + 12, y + 30, 8))),
            ("sněhulák vrátil rukavičku", lambda x, y: snowman_b(x, y, 0.85, right="hold", item=lambda a, b: mitten(a + 3, b - 6, 0.7, rot=-30))),
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
        hand_text(p.X(0.12), by + 36, p.w*0.74, "Strana 7: kdo šel v noci kolem okna?", "SH", 14, align="left")
        magnifier(p.X(0.9), by + 30, ang=-30, r=12)
        hand_text(p.X(0.05), by - 32, p.w*0.9, "Kdo staví sněhuláky?", "SHB", 20)
        hand_text(p.X(0.05), by - 58, p.w*0.9, "Proč nezaklepe? A jak mu odpovíš?", "SHB", 20)
        hand_text(p.X(0.05), by - 84, p.w*0.9, "Nápověda: prohlédni si znovu strany 7 a 11.", "SH", 14)
        with T(p.X(0.5), p.Y(0.06), 1.0, rot=180):
            hand_text(-p.w*0.45, 0, p.w*0.9, "Někdo malý, kdo bydlí u Franty. Stydí se, a tak píše obrázky ze sněhu.", "SH", 12)
            hand_text(-p.w*0.45, -15, p.w*0.9, "Odpovědět se dá taky sněhulákem. Otoč na další stranu!", "SH", 12)
    page_end()


# =================================================================== 16 the answer
def page_answer():
    R = rows([(330, [1]), (420, [1])])
    with Pn(*R[0]) as p:
        winter_garden(p, p.Y(0.3), 30, house_x=0.85, house_s=0.9)
        shape(ell(p.X(0.42), p.Y(0.12), 30, 26, 30), P.SNOW, LINE)
        A(p.X(0.3), p.Y(0.03), 1.3, mood="grin", right="front", look=(1, 0))
        Hk(p.X(0.58), p.Y(0.03), 1.2, flip=True, mood="grin", right="front", look=(1, 0))
        babicka(p.X(0.12), p.Y(0.03), 1.1, mood="happy", right="up", look=(1, 0))
        cap(p, "Odpověď se staví celé odpoledne.", w=230)
        say(p, "Kouli větší!", *hd("babi", p.X(0.12), p.Y(0.03), 1.1), w=100, area=(0.0, 0.4))
        say(p, "Ještě větší!", *hd_h("hanka", p.X(0.58), p.Y(0.03), 1.2), w=100, area=(0.4, 0.8))
    with Pn(*R[1]) as p:
        gy = p.Y(0.3)
        winter_garden(p, gy, 31, trees=((0.92, 1.2),))
        snow_fence(p.x - 5, p.X(0.5), gy - 6, 40)
        answer_snowmen(p.X(0.18), p.Y(0.06), 1.6)
        Hk(p.X(0.7), p.Y(0.03), 1.3, flip=True, mood="happy", right="wave", look=(1, 0))
        A(p.X(0.86), p.Y(0.03), 1.3, flip=True, mood="happy", look=(1, 0))
        hidden_triangle(p.X(0.58), p.Y(0.07))
        say(p, "Ahoj! Pojď si s námi hrát!", *hd_h("hanka", p.X(0.7), p.Y(0.03), 1.3), w=140, area=(0.5, 1.0))
        say(p, "Kdo umí číst obrázky, ten to pozná.", *hd_h("alica", p.X(0.86), p.Y(0.03), 1.3), w=150, area=(0.5, 1.0))
    page_end()


# =================================================================== 17 the answer to the answer
def page_reply():
    R = rows([(330, [1]), (420, [1])])
    with Pn(*R[0]) as p:
        gy = p.Y(0.3)
        winter_garden(p, gy, 32)
        answer_snowmen(p.X(0.08), p.Y(0.06), 1.2)
        snowman_b(p.X(0.62), p.Y(0.06), 0.75, pompom=True, right="wave")
        snow_tracks_to(p.X(0.98), p.Y(0.2), p.X(0.68), p.Y(0.06), 6, 1.0)
        A(p.X(0.86), p.Y(0.03), 1.2, flip=True, mood="wow", right="point", look=(1, 0))
        cap(p, "Ráno.", w=70)
        say(p, "Malý sněhulák s bambulí! A stopy vedou k nám, ne pryč!", *hd_h("alica", p.X(0.86), p.Y(0.03), 1.2), w=200,
            area=(0.4, 1.0))
    with Pn(*R[1]) as p:
        gy = p.Y(0.3)
        winter_garden(p, gy, 33, trees=((0.1, 1.3),))
        C.saveState()
        C.clipPath(poly([(p.X(0.55), p.Y(0.06) + 30), (p.x + p.w, p.Y(0.06) + 30), (p.x + p.w, p.y + p.h), (p.X(0.55), p.y + p.h)]),
                   stroke=0, fill=0)
        betka(p.X(0.72), p.Y(0.06) - 12, 1.6, flip=True, mood="whisper", look=(1, 0))
        C.restoreState()
        snow_fence(p.X(0.5), p.x + p.w + 5, p.Y(0.06), 70)
        Hk(p.X(0.3), p.Y(0.03), 1.4, mood="surprised", look=(1, 0.3))
        keep_clear(p, p.X(0.6), p.Y(0.06) + 70, p.X(0.84), p.Y(0.06) + 180, "betka")
        say(p, "Ahoj…", *hd_h("hanka", p.X(0.3), p.Y(0.03), 1.4), w=80, whisper=True, area=(0.0, 0.5))
    page_end()


# =================================================================== 18 meeting
def page_meet():
    R = rows([(260, [1]), (240, [0.5, 0.5]), (250, [1])])
    with Pn(*R[0]) as p:
        winter_garden(p, p.Y(0.3), 34, hills_=False)
        Hk(p.X(0.35), p.Y(0.03), 1.4, mood="happy", right="front", look=(1, 0), monkey=False,
           item=lambda x, y: chars3.monkey_dangle(x, y))
        betka(p.X(0.68), p.Y(0.03), 1.55, flip=True, mood="worried", look=(1, 0))
        say(p, "Chceš pohladit opičku?", *hd_h("hanka", p.X(0.35), p.Y(0.03), 1.4), w=130)
    with Pn(*R[1]) as p:
        winter_garden(p, p.Y(0.35), 35, hills_=False)
        betka(p.X(0.4), p.Y(0.03), 1.7, mood="whisper", right="hug", look=(1, 0))
        say(p, "Já jsem Bětka.", *hd_h("betka", p.X(0.4), p.Y(0.03), 1.7), w=110, whisper=True)
    with Pn(*R[2]) as p:
        winter_garden(p, p.Y(0.35), 36, hills_=False)
        A(p.X(0.3), p.Y(0.03), 1.3, mood="grin", right="wave", look=(1, 0))
        joey(p.X(0.7), p.Y(0.03), 0.95, flip=True, mood="happy")
        say(p, "Já jsem Alica. A tohle je Hanka a Joey!", *hd_h("alica", p.X(0.3), p.Y(0.03), 1.3), w=170)
    with Pn(*R[3]) as p:
        winter_garden(p, p.Y(0.3), 37, house_x=0.9, house_s=0.8)
        franta(p.X(0.2), p.Y(0.03), 1.0, mood="happy", right="front", look=(1, 0))
        betka(p.X(0.4), p.Y(0.03), 1.4, mood="happy", look=(-1, 0))
        A(p.X(0.65), p.Y(0.03), 1.2, flip=True, mood="happy", look=(1, 0))
        Hk(p.X(0.79), p.Y(0.03), 1.15, flip=True, mood="grin", look=(1, 0))
        hidden_triangle(p.X(0.92), p.Y(0.1))
        say(p, "To je moje vnučka. Je u mě na zimu. Stydí se, jako já, když jsem byl malý.", *hd("franta", p.X(0.2), p.Y(0.03), 1.0),
            w=240, x=p.X(0.03), y=p.Y(0.97))
    page_end()


# =================================================================== 19 why snowmen
def page_why():
    R = rows([(250, [1]), (250, [0.5, 0.5]), (250, [1])])
    with Pn(*R[0]) as p:
        hallway(p)
        x0, x1, y0, y1 = p.X(0.5), p.X(0.92), p.Y(0.3), p.Y(0.9)
        shape([(x0 - 5, y0 - 5), (x1 + 5, y0 - 5), (x1 + 5, y1 + 5), (x0 - 5, y1 + 5)], P.DOOR_FRAME, BG)
        with Pn(x0, y0, x1 - x0, y1 - y0, bg=P.SNOW_SKY) as w:
            snow_field(w, w.Y(0.4), 4)
            A(w.X(0.3), w.Y(0.05), 0.55, mood="happy", right="wave")
            Hk(w.X(0.5), w.Y(0.05), 0.55, mood="grin")
            joey(w.X(0.72), w.Y(0.05), 0.4, mood="happy")
        betka(p.X(0.25), p.Y(0.03), 1.5, hat=False, mood="sad", right="front", look=(1, 0.3))
        memory_frame(p)
        cap(p, "Bětka vypráví.", w=120)
        say(p, "Viděla jsem vás z okna. Chtěla jsem si s vámi hrát.", *hd("betka", p.X(0.25), p.Y(0.03), 1.5), w=190,
            whisper=True, area=(0.0, 0.5))
    with Pn(*R[1]) as p:
        winter_garden(p, p.Y(0.35), 38, night=True)
        franta(p.X(0.2), p.Y(0.05), 0.85, mood="happy", item=lambda x, y: lantern(x, y - 16, 0.8, glow=True))
        betka(p.X(0.62), p.Y(0.03), 1.2, mood="happy", right="front", look=(1, -0.3))
        shape(ell(p.X(0.82), p.Y(0.1), 16, 12, 24), P.SNOW, LINE)
        memory_frame(p)
        say(p, "Ráno, když všichni spí, se tolik nebojím.", *hd_h("betka", p.X(0.62), p.Y(0.03), 1.2), w=160, whisper=True)
    with Pn(*R[2]) as p:
        winter_garden(p, p.Y(0.45), 39, hills_=False)
        snow_fence(p.x - 5, p.x + p.w + 5, p.Y(0.1), 55)
        betka(p.X(0.4), p.Y(0.03), 1.3, mood="surprised", right="front", look=(1, -0.3),
              item=lambda x, y: mitten(x - 2, y - 6, 1.0))
        memory_frame(p)
        say(p, "Rukavičku jsem chtěla vrátit.", *hd_h("betka", p.X(0.4), p.Y(0.03), 1.3), w=140, whisper=True)
    with Pn(*R[3]) as p:
        kitchen(p, table=False)
        franta(p.X(0.22), p.Y(0.03), 0.95, mood="happy", right="front", look=(1, 0))
        Hk(p.X(0.72), p.Y(0.03), 1.2, hat=False, flip=True, mood="grin", right="up", look=(1, 0))
        say(p, "Naučil jsem ji obrázkové dopisy. Sněhuláci byli její dopisy.", *hd("franta", p.X(0.22), p.Y(0.03), 0.95), w=200)
        say(p, "A my jsme jí odpověděly!", *hd("hanka", p.X(0.72), p.Y(0.03), 1.2), w=130)
    page_end()


# =================================================================== 20 the big build
def page_build():
    R = rows([(360, [1]), (390, [1])])
    with Pn(*R[0]) as p:
        gy = p.Y(0.35)
        winter_garden(p, gy, 40, house_x=0.88, house_s=0.9)
        snowman_b(p.X(0.3), p.Y(0.06), 2.6, right="wave", nose="carrot")
        snowman_b(p.X(0.5), p.Y(0.06), 1.7, right="down", nose="parsnip", pompom=True)
        snowman_b(p.X(0.62), p.Y(0.06), 1.1, right="up", nose="carrot")
        Td(p.X(0.12), p.Y(0.03), 1.15, mood="grin", right="up", look=(1, 0))
        betka(p.X(0.76), p.Y(0.03), 1.3, flip=True, mood="grin", right="wave", look=(1, 0))
        cap(p, "Všichni spolu staví sněhulákovou rodinu.", w=260)
        say(p, "Táta sněhulák je obr! Jako já!", *hd_h("tonda", p.X(0.12), p.Y(0.03), 1.15), w=150, area=(0.0, 0.42))
    with Pn(*R[1]) as p:
        sky(p, P.SNOW_SKY)
        slope = [(p.x - 5, p.Y(0.75)), (p.x + p.w + 5, p.Y(0.15)), (p.x + p.w + 5, p.y - 5), (p.x - 5, p.y - 5)]
        shape(slope, P.SNOW, BG)
        with T(p.X(0.42), p.Y(0.48), 1.0, rot=-24):
            sled(0, 0, 1.2)
            seated(betka, "hanka", -14, 18*1.2, 1.25, P.BETKA_TROUSERS, P.BETKA_BOOTS, edge=2, mood="grin", right="up")
            seated(hanka, "hanka", 18, 18*1.2, 1.2, P.DUNGAREES, P.HANKA_BOOTS, edge=2, mood="grin", right="up")
        A(p.X(0.83), p.Y(0.2), 1.2, flip=True, mood="grin", right="up", look=(1, 0.3))
        joey(p.X(0.18), p.Y(0.68), 0.9, mood="happy")
        hidden_triangle(p.X(0.15), p.Y(0.25))
        sfx(p.X(0.12), p.Y(0.9), "JUPÍÍÍ!", 26, -8)
        cap(p, "Bětka se poprvé nahlas směje.", w=230, where="tr")
        say(p, "Ještě jednou!", p.X(0.42), p.Y(0.62), w=110, area=(0.25, 0.7))
    page_end()


# =================================================================== 21 evening cocoa
def page_cocoa():
    R = rows([(360, [1]), (390, [1])])
    with Pn(*R[0]) as p:
        kitchen(p, evening=True)
        for i, xx in enumerate((0.28, 0.42, 0.56, 0.7)): mug(p.X(xx), p.Y(0.38), 0.9)
        deda(p.X(0.12), p.Y(0.03), 1.05, mood="grin", right="up", look=(1, 0))
        franta(p.X(0.3), p.Y(0.03), 0.95, mood="happy", look=(1, 0))
        betka(p.X(0.5), p.Y(0.03), 1.3, hat=False, mood="grin", right="point", look=(-1, -0.5))
        A(p.X(0.68), p.Y(0.03), 1.2, hat=False, flip=True, mood="happy", look=(1, 0))
        Hk(p.X(0.8), p.Y(0.03), 1.15, hat=False, flip=True, mood="grin", look=(1, 0))
        babicka(p.X(0.93), p.Y(0.03), 1.05, flip=True, mood="happy", look=(1, 0))
        cap(p, "Večer u kakaa.", w=120)
        say(p, "Klub Hvězdička má nového člena. Zatím na zkoušku!", *hd("deda", p.X(0.12), p.Y(0.03), 1.05), w=190, area=(0.0, 0.5))
        say(p, "Já mám hvězdičky na botách!", *hd("betka", p.X(0.5), p.Y(0.03), 1.3), w=140, area=(0.4, 0.8))
    with Pn(*R[1]) as p:
        gy = p.Y(0.3)
        winter_garden(p, gy, 41, house_x=0.85, house_s=1.0, night=True)
        snowman_b(p.X(0.22), p.Y(0.06), 2.2, right="wave", nose="carrot")
        snowman_b(p.X(0.38), p.Y(0.06), 1.5, right="down", pompom=True)
        snowman_b(p.X(0.5), p.Y(0.06), 1.0, right="up", nose="carrot")
        snow_dog(p.X(0.62), p.Y(0.05), 1.2)
        star(p.X(0.4), p.Y(0.82), 18, 1.0, w=1.6)
        cap(p, "Dobrou noc, sněhuláci.", w=190)
    page_end()


# =================================================================== 22 activity
def page_quiz():
    with Pn(M, 40, W-2*M, H-80) as p:
        box = [(p.X(0.05), p.Y(0.905)), (p.X(0.95), p.Y(0.91)), (p.X(0.95), p.Y(0.905)+54), (p.X(0.05), p.Y(0.905)+52)]
        fill(box, 0.92)
        for a_, b_ in ((0, 1), (1, 2), (2, 3), (3, 0)): stroke([box[a_], box[b_]], 1.5)
        hand_text(p.X(0.05), p.Y(0.905)+18, p.w*0.9, "Detektivní zápisník", "SHB", 26)
        hand_text(p.X(0.05), p.Y(0.84), p.w*0.9, "Nakresli sněhulákový dopis! Co chceš kamarádovi říct?", "SHB", 15)
        bw, bh = p.w*0.27, p.h*0.2
        for i in range(3):
            bx = p.X(0.06) + i*(bw + p.w*0.04); by = p.Y(0.58)
            shape(rrect(bx, by, bw, bh, 8), 1.0, 1.2)
            hand_text(bx + 6, by + bh - 20, 30, str(i + 1), "SHB", 14, align="left")
            if i < 2:
                ax = bx + bw + 4; ay = by + bh/2
                stroke([(ax, ay), (ax + p.w*0.03, ay)], 1.6)
                stroke([(ax + p.w*0.03, ay), (ax + p.w*0.03 - 6, ay + 5)], 1.6)
                stroke([(ax + p.w*0.03, ay), (ax + p.w*0.03 - 6, ay - 5)], 1.6)
        y = p.Y(0.5)
        qs = ["1. Čím měli Bětčini sněhuláci nos?", "2. Co držel třetí sněhulák?",
              "3. Jak se jmenuje Frantova vnučka?", "4. Jak holky Bětce odpověděly?"]
        for q in qs:
            hand_text(p.X(0.06), y, p.w*0.9, q, "SH", 15, align="left")
            stroke([(p.X(0.06), y - 18), (p.X(0.94), y - 18)], 0.5, g=0.5)
            y -= 42
        hidden_triangle(p.X(0.08), y - 2, 9)
        hand_text(p.X(0.12), y - 10, p.w*0.84,
                  "Sněhuláci schovali v sešitě 10 trojúhelníčků s tečkou, jako je tenhle (ten se nepočítá). Najdeš je všechny? Obyčejné trojúhelníky se nepočítají!",
                  "SHB", 14, align="left", lead=18)
        with T(p.X(0.5), p.Y(0.015), 1.0, rot=180):
            hand_text(-p.w*0.45, 0, p.w*0.9, "Trojúhelníčky jsou na stranách 4, 5, 7, 8, 10, 12, 13, 16, 18 a 20.", "SH", 10)
    page_end()


# =================================================================== 23 next time
def page_next():
    with Pn(M, 40, W-2*M, H-80, bg=0.95) as p:
        hand_text(p.X(0.1), p.Y(0.93), p.w*0.8, "Příště v sešitě č. 6:", "SHB", 20)
        title(p.X(0.5), p.Y(0.84), "KAM MIZÍ PERNÍČKY?", 34)
        with Pn(p.X(0.08), p.Y(0.36), p.w*0.84, p.h*0.42, bg=0.9) as q:
            bg_fill(q, P.BEDROOM_WALL)
            x0, x1, y0, y1 = q.X(0.2), q.X(0.8), q.Y(0.3), q.Y(0.95)
            shape([(x0, y0), (x1, y0), (x1, y1), (x0, y1)], P.SNOW_SKY, BG)
            for xx in (0.35, 0.5, 0.65): bare_tree(q.X(xx), y0 + 6, 0.7, seed=int(xx*10))
            shape([(x0 - 14, y0 - 10), (x1 + 14, y0 - 10), (x1 + 14, y0 + 2), (x0 - 14, y0 + 2)], P.SILL, BG)
            for i in range(6): pernicek(q.X(0.27) + i*30, y0 + 10, 1.4, rot=(i - 3)*6, bitten=i in (1, 4))
            sykorka(q.X(0.75), y0 + 4, 2.0, flip=True)
            for i in range(5): dot(q.X(0.45) + i*12, y0 - 4 + (i % 2)*3, 1.4, 0.95)
            babicka(q.X(0.1), q.Y(0.02), 1.1, mood="surprised", look=(1, 0.3))
            say(q, "Kdo mi mlsá perníčky?", *hd("babi", q.X(0.1), q.Y(0.02), 1.1), w=130)
        hand_text(p.X(0.1), p.Y(0.3), p.w*0.8, "Advent. Babiččiny perníčky na okně jich ubývá. A na zamrzlém okně jsou malé ťukance…",
                  "SH", 16, lead=21)
        hand_text(p.X(0.3), p.Y(0.19), p.w*0.4, "Detektivní tým:", "SHB", 16)
        A(p.X(0.06), p.Y(0.03), 0.85, mood="happy", right="wave")
        Hk(p.X(0.15), p.Y(0.03), 0.85, mood="grin")
        betka(p.X(0.24), p.Y(0.03), 0.95, mood="happy")
        joey(p.X(0.34), p.Y(0.03), 0.65, mood="happy")
        Td(p.X(0.45), p.Y(0.03), 0.8, mood="grin")
        babicka(p.X(0.56), p.Y(0.03), 0.78, mood="happy")
        deda(p.X(0.67), p.Y(0.03), 0.74, mood="happy")
        franta(p.X(0.78), p.Y(0.03), 0.7, flip=True, mood="happy")
        snowman_b(p.X(0.9), p.Y(0.03), 0.7, right="wave")
    page_end()


# =================================================================== 24 back cover
def back_cover():
    with Pn(M, 40, W-2*M, H-80, bg=0.95) as p:
        sky(p, P.WINTER_NIGHT)
        r = random.Random(5)
        for _ in range(30): dot(p.x + r.random()*p.w, p.Y(0.45) + r.random()*p.h*0.5, 1.1, 1.0)
        snow_field(p, p.Y(0.42), 9)
        star(p.X(0.5), p.Y(0.85), 26, 1.0, w=1.8)
        snowman_b(p.X(0.3), p.Y(0.2), 2.6, right="wave", nose="carrot")
        snowman_b(p.X(0.5), p.Y(0.2), 1.8, right="down", pompom=True)
        snowman_b(p.X(0.64), p.Y(0.2), 1.2, right="up", nose="carrot")
        snow_dog(p.X(0.76), p.Y(0.19), 1.4)
        title(p.X(0.5), p.Y(0.12), "DOPISY ZE SNĚHU", 32)
        hand_text(p.X(0.1), p.Y(0.06), p.w*0.8, "Klub Hvězdička má o člena víc.", "SHB", 18)
        hand_text(p.X(0.1), p.Y(0.015), p.w*0.8, "Velká a malá detektivka · sešit č. 5", "SH", 13, g=0.35)
    PAGE[0] += 1; cv.showPage()


cover(); page_cast(); page_first_snow(); page_morning(); page_lupa(); page_follow(); page_watch(); page_second()
page_board(); page_cleared(); page_franta(); page_third(); page_read(); page_choice(); page_stop(); page_answer()
page_reply(); page_meet(); page_why(); page_build(); page_cocoa(); page_quiz(); page_next()
back_cover()
cv.save()
print("ok", PAGE[0] - 1, "pages")
for pr in PROBLEMS: print("ORDER/LAYOUT:", pr)
if PROBLEMS: sys.exit(1)
