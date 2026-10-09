"""Velká a malá detektivka, issue 6: Kam mizí perníčky? (outline: vault topics/comic-series/issue6-outline)"""
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
from props_extra import mug, stream, dog_bed, flour_patch
from attic import (young, chest, attic, bedroom, bed_side, blanket_side, bunting, shelf_toys, kids_drawing,
                   owlet, owl_box, old_photo, map_half, ladder, sled, tin)
from pond import *
from village import *
from letter import Panel, caption, bubble, sfx, title, series_title, hand_text, lines_of, thought
from winter import *
from interior import stove
from advent import *
import chars3

W, H = A4
M = 28; GUT = 9; TOP = H - 30
OUT = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                   "comics", "velka_a_mala_detektivka", "06_kam_mizi_pernicky.pdf")
os.makedirs(os.path.dirname(OUT), exist_ok=True)
cv = canvas.Canvas(OUT, pagesize=A4); lib.set_canvas(cv)
cv.setTitle("Velká a malá detektivka – Případ č. 6: Kam mizí perníčky?")
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


# =================================================================== issue 6 helpers
HID = []   # pages with a hidden gingerbread man, in order; the notebook's answer key is built from it
N_HIDDEN = 12


def gm(x, y):
    """one of the 12 hidden gingerbread men (see advent.hidden_gingerbread_man)"""
    hidden_gingerbread_man(x, y)
    HID.append(PAGE[0])


def flour_nose(x, y, s, flip=False):
    """a dab of flour on Joey's black nose (standing pose)"""
    nx = x + (-39.5 if flip else 39.5)*s
    shape(ell(nx, y + 44*s, 3.2*s, 2.4*s, 12), 1.0, LINE*0.4)
    for dx, dy in ((-4, 3), (3, 4), (-2, -3)): dot(nx + dx*s, y + 44*s + dy*s, 0.6*s, 1.0)


def kitchen_window(p, x0, x1, y0, y1, light="day", tray_=True, pecked=True, birds=0, prints=False, pecks=False):
    """the kitchen window from inside: frosty panes, the snowy garden, the sill outside with the cooling tray"""
    sky_g = {"day": P.SNOW_SKY, "dawn": 0.62, "night": P.WINTER_NIGHT}[light]
    shape([(x0 - 7, y0 - 7), (x1 + 7, y0 - 7), (x1 + 7, y1 + 7), (x0 - 7, y1 + 7)], P.DOOR_FRAME, BG)
    shape([(x0, y0), (x1, y0), (x1, y1), (x0, y1)], sky_g, BG)
    fill([(x0, y0), (x1, y0), (x1, y0 + (y1 - y0)*0.32), (x0, y0 + (y1 - y0)*0.36)], P.SNOW)
    for k, bx in enumerate((0.25, 0.7)): bare_tree(x0 + (x1 - x0)*bx, y0 + (y1 - y0)*0.3, 0.45, seed=k + 2)
    sill_y = y0 + 4
    fill([(x0, y0), (x1, y0), (x1, sill_y + 6), (x0, sill_y + 6)], P.SNOW)
    if tray_: tray(x0 + (x1 - x0)*0.12, sill_y, (x1 - x0)*0.55, 5, pecked)
    if prints:
        for i in range(5): bird_print(x0 + (x1 - x0)*(0.72 + i*0.045), sill_y + 3 + (i % 2)*2, 0.9, 10)
    if pecks: peck_marks(x0 + (x1 - x0)*0.3, y0 + (y1 - y0)*0.62, (x1 - x0)*0.35, 10)
    for i in range(birds):
        tit(x0 + (x1 - x0)*(0.3 + i*0.28), sill_y + 9, 1.5, flip=i % 2 == 1, kind=("great", "blue")[i % 2],
            pose="peck" if i == 0 else "perch")
    frost(x0, y0, x1, y1)
    s_([((x0 + x1)/2, y0), ((x0 + x1)/2, y1)], BG*2, g=P.DOOR_FRAME)
    s_([(x0, (y0 + y1)*0.5 + (y1 - y0)*0.12), (x1, (y0 + y1)*0.5 + (y1 - y0)*0.12)], BG*2, g=P.DOOR_FRAME)
    shape([(x0 - 12, y0 - 7), (x1 + 12, y0 - 7), (x1 + 12, y0 - 2), (x0 - 12, y0 - 2)], P.SILL, BG)


def hallway(p):
    planks(p, P.PLANKS, 26, 9, knots=False)
    floor_y = p.Y(0.1)
    shape([(p.x - 5, p.y - 5), (p.x + p.w + 5, p.y - 5), (p.x + p.w + 5, floor_y), (p.x - 5, floor_y)], P.FLOOR, BG)
    return floor_y


def pantry(p):
    """the pantry: shelves of jars, the tin on the middle shelf; returns the shelf line the tin stands on"""
    bg_fill(p, 0.82)
    for k, fy in enumerate((0.22, 0.52, 0.82)):
        y_ = p.Y(fy)
        shape([(p.x - 5, y_ - 4), (p.x + p.w + 5, y_ - 4), (p.x + p.w + 5, y_), (p.x - 5, y_)], P.SILL, BG)
        if k != 1:
            for i in range(6): jar(p.X(0.08) + i*p.w*0.15, y_, 14 + (i % 2)*5, (P.JAM, 0.75, 0.55)[i % 3])
    return p.Y(0.52)


def tin_closeup(p, stars, hearts, moons):
    bg_fill(p, 0.78)
    cookie_tin(p.X(0.06), p.Y(0.12), p.w*0.66, stars, hearts, moons, lid=False)


def newspaper(x, y, s=1.0):
    """děda's newspaper, held upside down"""
    from letter import hand_text as ht
    with T(x, y, s):
        shape([(-22, -14), (22, -14), (22, 14), (-22, 14)], 0.97, LINE*0.8)
        stroke([(0, -14), (0, 14)], 0.5, g=0.5)
        with T(0, 0, 1.0, rot=180):
            ht(-20, 6, 18, "NOVINY", "SH", 5)
            for k in range(4): stroke([(-19, 0 - k*3), (-3, 0 - k*3)], 0.5, g=0.55); stroke([(3, 8 - k*3.5), (19, 8 - k*3.5)], 0.5, g=0.55)


def tally(p, rows_):
    """Alica's count table in her notebook"""
    notebook_big(p.X(0.06), p.Y(0.08), p.w*0.88, p.h*0.84, "KOLIK HVĚZDIČEK?", rows_)


def mill_dawn(p, gy, spruce_x=0.62, spruce_s=1.0, stars=(), mill_x=0.2, lanterns=()):
    sky(p, 0.7)
    fill([(p.x - 5, p.Y(0.75)), (p.x + p.w + 5, p.Y(0.75)), (p.x + p.w + 5, p.y + p.h + 5), (p.x - 5, p.y + p.h + 5)], 0.8)
    hills(p, gy + p.h*0.06, 16, P.SNOW_HILL, 3)
    snow_field(p, gy, 6)
    if mill_x is not None: mill(p.X(mill_x), gy + 2, 0.75)
    star_spruce(p.X(spruce_x), gy - 4, spruce_s, stars)
    for lx, ly in lanterns: lantern(p.X(lx), p.Y(ly), 0.9, glow=True)


# the stars on the spruce: (fx, fy, pecked) — seven members, two of them eaten by the tits
SPRUCE_STARS = [(-0.6, 0.1, False), (0.55, 0.15, False), (-0.3, 0.38, False), (0.3, 0.42, True), (-0.45, 0.62, True),
                (0.2, 0.68, False), (0.0, 0.88, False)]
SPRUCE_FULL = [(fx, fy, False) for fx, fy, _ in SPRUCE_STARS] + [(0.45, 0.5, False), (-0.15, 0.55, False)]


# =================================================================== 1 COVER
def cover():
    with Pn(M, 40, W-2*M, H-80) as p:
        kitchen(p, table=True)
        kitchen_window(p, p.X(0.52), p.X(0.94), p.Y(0.42), p.Y(0.66), "day", tray_=True, birds=1, pecks=True)
        for i in range(6):
            (star_cookie, heart_cookie, moon_cookie)[i % 3](p.X(0.3) + i*24, p.Y(0.37), 1.4, rot=(i - 3)*7)
        A(p.X(0.2), p.Y(0.03), 3.0, hat=False, mood="wow", right="lens", lens=True, look=(1, 0.4))
        Hk(p.X(0.78), p.Y(0.03), 2.6, hat=False, flip=True, mood="grin", right="back", look=(-1, 0.2))
        hx_, hy_ = hand_pt(True, "back", p.X(0.78), p.Y(0.03), 2.6, flip=True)
        heart_cookie(hx_ + 8, hy_ - 4, 2.2, rot=20)                         # Hanka hides a heart behind her back
        joey(p.X(0.45), p.Y(0.03), 1.6, mood="happy")
    box = [(M+34, H-236), (W-M-30, H-232), (W-M-34, H-48), (M+30, H-52)]
    fill([(x+3, y-3) for x, y in box], 0.0, 0.25); fill(box, 1.0)
    for a_, b_ in ((0, 1), (1, 2), (2, 3), (3, 0)): stroke([box[a_], box[b_]], 1.8)
    series_title(W/2, H-98, H-160, 40, 66)
    hand_text(M+40, H-190, W-2*M-80, "Alica a Hanka", "SHB", 20)
    hand_text(M+40, H-217, W-2*M-80, "Případ č. 6: Kam mizí perníčky?", "SH", 15)
    magnifier(M+82, H-120, ang=-30, r=17)
    star_cookie(W-M-100, H-118, 1.8)
    page_end()


# =================================================================== 2 WHO IS WHO
def page_cast():
    with Pn(M, 40, W-2*M, H-80) as p:
        hand_text(p.X(0.05), p.Y(0.95), p.w*0.9, "Kdo je kdo", "SHB", 30)
        cells = [
            ("Alica", "počítá a pozoruje", lambda x, y: A(x, y, 0.9, hat=False, mood="happy", right="lens", lens=True)),
            ("Hanka", "miluje perníčky", lambda x, y: Hk(x, y, 1.1, hat=False, mood="grin")),
            ("Joey", "má nejlepší nos", lambda x, y: joey(x, y, 1.2, mood="happy")),
            ("Babička", "peče perníčky", lambda x, y: babicka(x, y, 0.82, mood="happy")),
            ("Děda Honza", "založil Klub Hvězdička", lambda x, y: deda(x, y, 0.74, mood="happy")),
            ("Bětka", "v klubu na zkoušku", lambda x, y: betka(x, y, 1.0, mood="happy")),
            ("Tonda", "sní všechno", lambda x, y: Td(x, y, 0.88, hat=False, mood="grin")),
            ("Franta", "kamarád z klubu", lambda x, y: franta(x, y, 0.7, mood="happy")),
            ("Věrka", "bydlí ve mlýně", lambda x, y: verka_old(x, y, 0.72, mood="happy")),
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
        hand_text(p.x + 20, by + bh - 28, p.w*0.5, "Minule…", "SHB", 17, align="left")
        hand_text(p.x + 20, by + bh - 52, p.w*0.5,
                  "Sněhuláci byli dopisy od Bětky, Frantovy vnučky. Teď je v Klubu Hvězdička, zatím na zkoušku. Tady je fotka celého klubu.",
                  "SH", 13, align="left", lead=17)
        club_photo7(p.X(0.57), by + 14, p.w*0.4, bh - 28, rot=2)
    page_end()


# =================================================================== 3 baking
def page_baking():
    R = rows([(270, [1]), (230, [0.5, 0.5]), (250, [1])])
    with Pn(*R[0]) as p:
        kitchen(p)
        for i in range(6):
            star_cookie(p.X(0.36) + i*20, p.Y(0.42), 1.0, rot=(i % 3 - 1)*8)
            heart_cookie(p.X(0.36) + i*20, p.Y(0.47), 1.0)
        babicka(p.X(0.2), p.Y(0.03), 1.15, mood="happy", right="front", look=(1, 0))
        A(p.X(0.62), p.Y(0.03), 1.15, hat=False, flip=True, mood="grin", right="front", look=(1, 0))
        Hk(p.X(0.8), p.Y(0.03), 1.1, hat=False, flip=True, mood="wow", right="up", look=(1, 0.3))
        cap(p, "Advent. Babička peče perníčky.", w=230)
        say(p, "Dvanáct hvězdiček, dvanáct srdíček a dvanáct měsíčků.", *hd("babi", p.X(0.2), p.Y(0.03), 1.15), w=200, area=(0.0, 0.55))
        say(p, "Srdíčka namočíme do čokolády!", *hd("hanka", p.X(0.8), p.Y(0.03), 1.1), w=150, area=(0.5, 1.0))
    with Pn(*R[1]) as p:
        bg_fill(p, 0.88)
        star_cookie(p.X(0.28), p.Y(0.5), 4.2, rot=-6)
        heart_cookie(p.X(0.72), p.Y(0.48), 4.2)
        piping_bag(p.X(0.46), p.Y(0.68), 2.0, rot=-40)
        hand_text(p.X(0.08), p.Y(0.1), p.w*0.4, "hvězdička: bílá poleva", "SH", 11)
        hand_text(p.X(0.52), p.Y(0.1), p.w*0.4, "srdíčko: čokoláda", "SH", 11)
    with Pn(*R[2]) as p:
        kitchen(p, table=False)
        deda(p.X(0.3), p.Y(0.03), 1.05, mood="grin", right="front", look=(1, 0), item=lambda x, y: moon_cookie(x, y, 1.0))
        babicka(p.X(0.75), p.Y(0.03), 1.1, flip=True, mood="surprised", right="hip", look=(1, 0))
        say(p, "Jen na zkoušku! A kolik je těch hvězdiček?", *hd("deda", p.X(0.3), p.Y(0.03), 1.05), w=170)
        say(p, "Dvanáct. A nesahat!", *hd("babi", p.X(0.75), p.Y(0.03), 1.1), w=110)
    with Pn(*R[3]) as p:
        kitchen(p, table=False, evening=True)
        kitchen_window(p, p.X(0.06), p.X(0.4), p.Y(0.4), p.Y(0.85), "night", pecked=False)
        babicka(p.X(0.58), p.Y(0.03), 1.1, mood="happy", right="front", look=(1, 0), item=lambda x, y: heart_cookie(x, y - 2, 1.0))
        Hk(p.X(0.8), p.Y(0.03), 1.1, hat=False, flip=True, mood="grin", right="front", look=(1, 0))
        cap(p, "Večer. Polámané perníčky chladnou za oknem, ostatní jsou v plechovce ve spíži.", w=300)
        say(p, "Jedno srdíčko na dobrou noc.", *hd("babi", p.X(0.58), p.Y(0.03), 1.1), w=140, area=(0.42, 1.0))
    page_end()


# =================================================================== 4 the first morning
def page_morning():
    R = rows([(300, [1]), (220, [0.5, 0.5]), (230, [1])])
    with Pn(*R[0]) as p:
        kitchen(p, table=False)
        kitchen_window(p, p.X(0.42), p.X(0.92), p.Y(0.38), p.Y(0.9), "day", pecked=True)
        crumbs(p.X(0.6), p.Y(0.38) + 14, 50, 4, 10, P.GINGER, seed=2)
        A(p.X(0.12), p.Y(0.03), 1.25, hat=False, mood="surprised", look=(1, 0.3))
        Hk(p.X(0.27), p.Y(0.03), 1.2, hat=False, mood="wow", right="point", look=(1, 0.4))
        gm(p.X(0.92) + 4, p.Y(0.38) - 2 + 13)          # on the end of the sill
        cap(p, "Ráno.", w=70)
        say(p, "Někdo okusoval perníčky za oknem!", *hd("hanka", p.X(0.27), p.Y(0.03), 1.2), w=160, area=(0.0, 0.42))
        say(p, "Kdo by lezl na okno?", *hd("alica", p.X(0.12), p.Y(0.03), 1.25), w=120, area=(0.0, 0.42))
    with Pn(*R[1]) as p:
        bg_fill(p, P.FROST)
        frost(p.x, p.y, p.x + p.w, p.y + p.h, seed=9)
        peck_marks(p.X(0.2), p.Y(0.7), p.w*0.6, 14, seed=4)
        fill([(p.x - 5, p.y - 5), (p.x + p.w + 5, p.y - 5), (p.x + p.w + 5, p.Y(0.35)), (p.x - 5, p.Y(0.35))], P.SNOW)
        for i in range(7): bird_print(p.X(0.15) + i*p.w*0.11, p.Y(0.15) + (i % 2)*8, 2.2, 10 - i*4)
        cap(p, "Zblízka: malinké stopičky a ťukance v jinovatce.", w=200)
    with Pn(*R[2]) as p:
        tin_closeup(p, 5, 11, 12)
        A(p.X(0.88), p.Y(0.03), 1.0, hat=False, flip=True, mood="wow", look=(1, -0.4))
        cap(p, "Plechovka ve spíži.", w=150)
        say(p, "Hvězdiček je jen pět!", *hd("alica", p.X(0.88), p.Y(0.03), 1.0), w=120, area=(0.5, 1.0))
    with Pn(*R[3]) as p:
        kitchen(p, table=False)
        deda(p.X(0.22), p.Y(0.03), 1.05, mood="happy", right="front", look=(1, 0), item=lambda x, y: mug(x, y - 4, 0.8))
        babicka(p.X(0.5), p.Y(0.03), 1.1, flip=True, mood="surprised", look=(1, 0))
        joey(p.X(0.75), p.Y(0.03), 1.0, pose="sniff", mood="happy")
        say(p, "To budou myši.", *hd("deda", p.X(0.22), p.Y(0.03), 1.05), w=110, area=(0.0, 0.4))
        sfx(p.X(0.72), p.Y(0.75), "ČMUCH ČMUCH!", 15, -6)
    page_end()


# =================================================================== 5 under the magnifier
def page_lupa():
    R = rows([(260, [0.5, 0.5]), (230, [1]), (260, [1])])
    with Pn(*R[0]) as p:
        kitchen(p, table=False)
        kitchen_window(p, p.X(0.1), p.X(0.9), p.Y(0.42), p.Y(0.95), "day", pecked=True)
        A(p.X(0.3), p.Y(0.03), 1.25, hat=False, mood="think", right="lens", lens=True, look=(1, 0.6))
        say(p, "Venku: malé okousané kousky.", *hd("alica", p.X(0.3), p.Y(0.03), 1.25), w=130, area=(0.45, 1.0))
    with Pn(*R[1]) as p:
        tin_closeup(p, 5, 11, 12)
        A(p.X(0.86), p.Y(0.03), 1.1, hat=False, flip=True, mood="think", right="lens", lens=True, look=(1, -0.3))
        gm(p.X(0.1), p.Y(0.06))
        say(p, "Tady: celé hvězdičky pryč. Ani drobek!", *hd("alica", p.X(0.86), p.Y(0.03), 1.1), w=130, area=(0.0, 1.0))
    with Pn(*R[2]) as p:
        kitchen(p, table=False)
        A(p.X(0.3), p.Y(0.03), 1.3, hat=False, mood="determined", right="up", look=(1, 0))
        Hk(p.X(0.7), p.Y(0.03), 1.2, hat=False, flip=True, mood="surprised", look=(1, 0.3))
        say(p, "To nejsou stejní zloději!", *hd("alica", p.X(0.3), p.Y(0.03), 1.3), w=140)
        say(p, "Dva zloději?", *hd("hanka", p.X(0.7), p.Y(0.03), 1.2), w=100)
    with Pn(*R[3]) as p:
        bg_fill(p, 0.9)
        notebook_big(p.X(0.07), p.Y(0.08), p.w*0.86, p.h*0.84, "PŘÍPAD Č. 6:",
                     ["1. za oknem: okousané kousky,", "   malinké stopičky", "2. ve spíži: chybí celé hvězdičky,",
                      "   bylo 12, zbylo 5, žádné drobky", "3. srdíčko: snědla Hanka (od babičky)"])
    page_end()


# =================================================================== 6 Joey?
def page_joey():
    R = rows([(260, [1]), (240, [0.5, 0.5]), (250, [1])])
    with Pn(*R[0]) as p:
        kitchen(p, table=False)
        flour_patch(p.X(0.18), p.Y(0.12), 60, 18)
        paw_trail(p.X(0.25), p.Y(0.14), p.X(0.78), p.Y(0.24), 7, 1.6)
        shape([(p.X(0.82), p.Y(0.02)), (p.X(0.98), p.Y(0.02)), (p.X(0.98), p.Y(0.85)), (p.X(0.82), p.Y(0.85))], P.DOOR_FRAME, BG)
        hand_text(p.X(0.82), p.Y(0.6), p.w*0.16, "SPÍŽ", "SHB", 12)
        A(p.X(0.12), p.Y(0.03), 1.2, hat=False, mood="wow", right="point", look=(1, -0.3))
        say(p, "Moučné tlapky! Vedou do spíže!", *hd("alica", p.X(0.12), p.Y(0.03), 1.2), w=160, area=(0.0, 0.6))
    with Pn(*R[1]) as p:
        kitchen(p, table=False)
        joey(p.X(0.55), p.Y(0.05), 1.5, mood="happy")
        flour_nose(p.X(0.55), p.Y(0.05), 1.5)
        A(p.X(0.16), p.Y(0.03), 1.1, hat=False, mood="determined", right="point", look=(1, 0))
        say(p, "Joey! Mám tě!", *hd("alica", p.X(0.16), p.Y(0.03), 1.1), w=100)
    with Pn(*R[2]) as p:
        y_ = pantry(p)
        tin(p.X(0.55), y_, 1.5)
        paw_trail(p.X(0.05), p.Y(0.06), p.X(0.42), p.Y(0.12), 5, 1.5)
        joey(p.X(0.4), p.Y(0.04), 1.0, mood="happy")
        say(p, "Stopy u plechovky končí…", p.X(0.15), p.Y(0.5), w=140)
    with Pn(*R[3]) as p:
        kitchen(p, table=False)
        Hk(p.X(0.18), p.Y(0.03), 1.15, hat=False, mood="determined", right="up", look=(1, 0))
        babicka(p.X(0.55), p.Y(0.03), 1.1, mood="happy", right="front", look=(1, 0))
        joey(p.X(0.8), p.Y(0.03), 1.0, flip=True, mood="happy")
        flour_nose(p.X(0.8), p.Y(0.03), 1.0, flip=True)
        gm(p.X(0.95), p.Y(0.1))
        say(p, "Joey neumí otevřít plechovku!", *hd("hanka", p.X(0.18), p.Y(0.03), 1.15), w=140, area=(0.0, 0.45))
        say(p, "Jen sedí a škemrá. Mouku má na čumáku od pečení.", *hd("babi", p.X(0.55), p.Y(0.03), 1.1), w=190, area=(0.35, 1.0))
    page_end()


# =================================================================== 7 the watch at the window
def page_watch():
    R = rows([(250, [1]), (250, [0.5, 0.5]), (250, [1])])
    with Pn(*R[0]) as p:
        kitchen(p, table=False, evening=True)
        kitchen_window(p, p.X(0.45), p.X(0.9), p.Y(0.4), p.Y(0.92), "dawn", pecked=False)
        curtain = [(p.X(0.36), p.Y(0.98))] + bez((p.X(0.36), p.Y(0.98)), (p.X(0.42), p.Y(0.6)), (p.X(0.38), p.Y(0.3)), (p.X(0.44), p.Y(0.02))) + \
                  [(p.X(0.3), p.Y(0.02)), (p.X(0.3), p.Y(0.98))]
        shape(curtain, P.CLOTH_CHECK, BG)
        A(p.X(0.12), p.Y(0.03), 1.25, hat=False, mood="whisper", right="hush", look=(1, 0.3))
        Hk(p.X(0.24), p.Y(0.03), 1.15, hat=False, mood="determined", look=(1, 0.3))
        cap(p, "Druhý den za svítání. Hlídka u okna.", w=250)
        say(p, "Pšt! Něco letí!", *hd("alica", p.X(0.12), p.Y(0.03), 1.25), w=100, whisper=True, area=(0.0, 0.3))
    with Pn(*R[1]) as p:
        bg_fill(p, 0.7)
        kitchen_window(p, p.X(0.06), p.X(0.94), p.Y(0.1), p.Y(0.92), "dawn", pecked=True, birds=2)
        sfx(p.X(0.55), p.Y(0.78), "ŤUK ŤUK", 16, -4)
    with Pn(*R[2]) as p:
        kitchen(p, table=False, evening=True)
        Hk(p.X(0.4), p.Y(0.03), 1.4, hat=False, mood="wow", right="point", look=(1, 0.3))
        say(p, "Sýkorky! Ptáčci mají hlad!", *hd("hanka", p.X(0.4), p.Y(0.03), 1.4), w=130)
    with Pn(*R[3]) as p:
        gy = p.Y(0.3)
        winter_garden(p, gy, 14, house_x=0.15, house_s=0.9, trees=((0.5, 1.1),), night=True)
        snow_fence(p.X(0.6), p.x + p.w + 5, gy - 6, 40, gap_at=None)
        tit(p.X(0.45), p.Y(0.7), 1.6, kind="great", pose="fly"); tit(p.X(0.55), p.Y(0.76), 1.4, flip=True, kind="blue", pose="fly")
        lantern(p.X(0.83), gy - 2, 0.55, glow=True)          # someone with a lantern at the gate; nobody says so
        gm(p.X(0.215), gy + 46)
        cap(p, "Sýkorky odletěly do zahrady.", w=210)
    page_end()


# =================================================================== 8 the bird feeder
def page_feeder():
    R = rows([(250, [1]), (240, [0.5, 0.5]), (260, [1])])
    with Pn(*R[0]) as p:
        kitchen(p, table=False)
        babicka(p.X(0.28), p.Y(0.03), 1.15, mood="worried", right="front", look=(1, 0),
                item=lambda x, y: shape([(x - 14, y), (x + 14, y), (x + 12, y + 4), (x - 12, y + 4)], P.TIN, LINE))
        A(p.X(0.72), p.Y(0.03), 1.15, hat=False, flip=True, mood="surprised", look=(1, 0))
        say(p, "Perník ptáčkům škodí. Je moc sladký a kořeněný.", *hd("babi", p.X(0.28), p.Y(0.03), 1.15), w=180)
    with Pn(*R[1]) as p:
        winter_garden(p, p.Y(0.35), 41, hills_=False)
        deda(p.X(0.35), p.Y(0.03), 1.05, mood="grin", right="up", look=(1, 0), item=lambda x, y: hammer(x, y))
        say(p, "Postavíme jim krmítko! Hned teď!", *hd("deda", p.X(0.35), p.Y(0.03), 1.05), w=150)
    with Pn(*R[2]) as p:
        winter_garden(p, p.Y(0.35), 42, hills_=False)
        bird_feeder(p.X(0.65), p.Y(0.04), 1.5)
        Hk(p.X(0.25), p.Y(0.03), 1.3, mood="grin", right="front", look=(1, 0), item=lambda x, y: seed_star(x, y - 4, 0.7))
        say(p, "Semínka a lůj!", *hd_h("hanka", p.X(0.25), p.Y(0.03), 1.3), w=110, area=(0.0, 0.5))
    with Pn(*R[3]) as p:
        gy = p.Y(0.35)
        winter_garden(p, gy, 43, house_x=0.88, house_s=0.85)
        bird_feeder(p.X(0.42), p.Y(0.05), 1.8, birds=2)
        A(p.X(0.12), p.Y(0.03), 1.25, mood="grin", right="up", look=(1, 0))
        Hk(p.X(0.24), p.Y(0.03), 1.15, mood="happy", look=(1, 0))
        joey(p.X(0.66), p.Y(0.03), 1.0, mood="happy")
        gm(p.X(0.42), p.Y(0.05) + 30)
        say(p, "Případ vyřešen!", *hd_h("alica", p.X(0.12), p.Y(0.03), 1.25), w=110, area=(0.0, 0.35))
    page_end()


# =================================================================== 9 the second morning: the turn
def page_turn():
    R = rows([(220, [0.5, 0.5]), (340, [1]), (190, [1])])
    with Pn(*R[0]) as p:
        kitchen(p, table=False)
        kitchen_window(p, p.X(0.1), p.X(0.9), p.Y(0.42), p.Y(0.95), "day", pecked=False)
        A(p.X(0.3), p.Y(0.03), 1.2, hat=False, mood="happy", look=(1, 0.5))
        cap(p, "Druhé ráno.", w=100)
        say(p, "Na okně nic. Sýkorky jsou u krmítka.", *hd("alica", p.X(0.3), p.Y(0.03), 1.2), w=130, area=(0.42, 1.0))
    with Pn(*R[1]) as p:
        winter_garden(p, p.Y(0.35), 44, hills_=False)
        bird_feeder(p.X(0.5), p.Y(0.04), 2.1, birds=2)
        gm(p.X(0.5), p.Y(0.04) + 40)
    with Pn(*R[2]) as p:
        tin_closeup(p, 3, 11, 12)
        A(p.X(0.88), p.Y(0.03), 1.25, hat=False, flip=True, mood="surprised", look=(1, -0.4))
        Hk(p.X(0.76), p.Y(0.03), 1.15, hat=False, flip=True, mood="wow", look=(1, -0.4))
        say(p, "Další dvě hvězdičky pryč!", *hd("alica", p.X(0.88), p.Y(0.03), 1.25), w=140, area=(0.45, 1.0))
    with Pn(*R[3]) as p:
        bg_fill(p, 0.3)
        title(p.X(0.5), p.Y(0.42), "PŘÍPAD NENÍ VYŘEŠEN!", 34)
    page_end()


# =================================================================== 10 the locked house
def page_locked():
    R = rows([(260, [1]), (240, [0.5, 0.5]), (250, [1])])
    with Pn(*R[0]) as p:
        gy = p.Y(0.25)
        winter_garden(p, gy, 45, house_x=0.5, house_s=1.6, trees=((0.1, 1.2), (0.9, 1.1)), night=True)
        cap(p, "V noci je všechno zavřené.", w=200)
    with Pn(*R[1]) as p:
        kitchen(p, table=False, evening=True)
        kitchen_window(p, p.X(0.5), p.X(0.92), p.Y(0.45), p.Y(0.9), "night", tray_=False)
        A(p.X(0.25), p.Y(0.03), 1.15, hat=False, mood="think", right="chin", look=(1, 0))
        say(p, "Okno zavřené. Dveře zamčené.", *hd("alica", p.X(0.25), p.Y(0.03), 1.15), w=120, area=(0.0, 0.48))
    with Pn(*R[2]) as p:
        fy = hallway(p)
        dog_bed(p.X(0.6), fy, 1.4)
        joey(p.X(0.6), fy + 4, 0.9, mood="sleepy")
        A(p.X(0.18), fy, 1.15, hat=False, mood="think", look=(1, -0.3))
        say(p, "A Joey spí v předsíni.", *hd("alica", p.X(0.18), fy, 1.15), w=120, area=(0.0, 0.6))
    with Pn(*R[3]) as p:
        y_ = pantry(p)
        tin(p.X(0.82), y_, 1.4)
        mousetrap(p.X(0.6), p.Y(0.05), 3.0)                   # the trap has no bait: nobody in the story says so
        A(p.X(0.25), p.Y(0.03), 1.3, hat=False, mood="determined", right="up", look=(1, 0))
        gm(p.X(0.08), p.Y(0.82) + 16)
        say(p, "Byl to někdo z domu!", *hd("alica", p.X(0.25), p.Y(0.03), 1.3), w=130, area=(0.0, 0.5))
    page_end()


# =================================================================== 11 Hanka?
def page_hanka():
    R = rows([(260, [1]), (240, [0.5, 0.5]), (250, [1])])
    with Pn(*R[0]) as p:
        fy = bedroom_night(p, window=False)
        bg_fill(p, 1.0, 0.2)
        bed_side(p.X(0.4), p.X(0.95), p.y + 48)
        pillow_crumbs(p.X(0.74), p.y + 52, 70)
        A(p.X(0.22), fy, 1.3, hat=False, mood="think", right="lens", lens=True, look=(1, -0.3))
        cap(p, "V dětském pokoji.", w=150)
        say(p, "Drobečky na Hančině polštáři…", *hd("alica", p.X(0.22), fy, 1.3), w=150, area=(0.0, 0.6))
    with Pn(*R[1]) as p:
        fy = bedroom_night(p, window=False); bg_fill(p, 1.0, 0.2)
        Hk(p.X(0.45), fy, 1.4, hat=False, mood="whisper", right="hush", look=(1, 0))
        say(p, "Pšt, opičko. To je tajemství.", *hd("hanka", p.X(0.45), fy, 1.4), w=130, whisper=True)
    with Pn(*R[2]) as p:
        fy = bedroom_night(p, window=False); bg_fill(p, 1.0, 0.2)
        A(p.X(0.45), fy, 1.35, hat=False, mood="worried", look=(1, 0))
        say(p, "Hanko… nebyla jsi to ty?", *hd("alica", p.X(0.45), fy, 1.35), w=130)
    with Pn(*R[3]) as p:
        fy = bedroom_night(p, window=False); bg_fill(p, 1.0, 0.2)
        Hk(p.X(0.25), fy, 1.3, hat=False, mood="sad", look=(1, 0))
        babicka(p.X(0.72), fy, 1.1, flip=True, mood="worried", right="front", look=(1, 0))
        say(p, "Já ne!", *hd("hanka", p.X(0.25), fy, 1.3), w=80, area=(0.0, 0.45))
        say(p, "Jedno srdíčko jsem jí dala já. Na dobrou noc.", *hd("babi", p.X(0.72), fy, 1.1), w=170, area=(0.4, 1.0))
    page_end()


# =================================================================== 12 Alica puts it right
def page_sorry():
    R = rows([(250, [0.5, 0.5]), (250, [1]), (250, [1])])
    with Pn(*R[0]) as p:
        bg_fill(p, 0.96)
        pillow_crumbs(p.X(0.1), p.Y(0.2), p.w*0.8)
        lx_, ly_ = p.X(0.6), p.Y(0.42)
        magnifier(lx_, ly_, ang=-30, r=30)
        C.saveState(); C.clipPath(poly(ell(lx_, ly_, 27, 27, 36)), stroke=0, fill=0)
        crumbs(lx_, ly_, 36, 26, 9, P.CHOCOLATE, seed=7, k=4.0)
        C.restoreState()
        say(p, "Drobky jsou tmavé. Čokoláda!", p.X(0.5), p.Y(0.4), w=140, x=p.X(0.05), y=p.Y(0.95))
    with Pn(*R[1]) as p:
        bg_fill(p, 0.88)
        heart_cookie(p.X(0.3), p.Y(0.5), 4.0)
        star_cookie(p.X(0.72), p.Y(0.5), 4.0)
        hand_text(p.X(0.05), p.Y(0.12), p.w*0.45, "srdíčko = tmavé", "SHB", 12)
        hand_text(p.X(0.5), p.Y(0.12), p.w*0.45, "hvězdička = bílá", "SHB", 12)
        cap(p, "Zmizely hvězdičky s bílou polevou.", w=150)
    with Pn(*R[2]) as p:
        fy = bedroom_night(p, window=False); bg_fill(p, 1.0, 0.2)
        A(p.X(0.44), fy, 1.3, hat=False, mood="sad", right="hug", look=(1, 0))
        Hk(p.X(0.54), fy, 1.25, hat=False, flip=True, mood="happy", right="hug", look=(1, 0))
        say(p, "Hanka to nebyla. Promiň, Hanko.", *hd("alica", p.X(0.44), fy, 1.3), w=140, area=(0.0, 0.5))
        say(p, "Nevadí.", *hd("hanka", p.X(0.54), fy, 1.25), w=80, area=(0.5, 1.0))
    with Pn(*R[3]) as p:
        fy = bedroom_night(p, window=False); bg_fill(p, 1.0, 0.2)
        Hk(p.X(0.25), fy, 1.3, hat=False, mood="grin", right="front", look=(1, 0))
        hanka_drawing(p.X(0.44), p.Y(0.35), 110, 80, rot=-4)
        A(p.X(0.82), fy, 1.25, hat=False, flip=True, mood="wow", look=(1, 0))
        gm(p.X(0.65), fy + 8)
        say(p, "Moje tajemství: obrázek pro Bětku!", *hd("hanka", p.X(0.25), fy, 1.3), w=150, area=(0.0, 0.42))
        say(p, "Detektiv se řídí stopami. Ne tím, co se mu zdá.", *hd("alica", p.X(0.82), fy, 1.25), w=170, area=(0.55, 1.0))
    page_end()


# =================================================================== 13 the suspect board
def page_board():
    R = rows([(240, [0.5, 0.5]), (510, [1])])
    with Pn(*R[0]) as p:
        winter_garden(p, p.Y(0.35), 46, hills_=False)
        Td(p.X(0.4), p.Y(0.03), 1.3, mood="grin", right="hip", look=(1, 0), item=lambda x, y: moon_cookie(x, y, 1.1))
        say(p, "Já bych jich snědl sto! Ale já mám rád měsíčky.", *hd_h("tonda", p.X(0.4), p.Y(0.03), 1.3), w=160)
    with Pn(*R[1]) as p:
        kitchen(p, table=False)
        deda(p.X(0.68), p.Y(0.03), 1.05, flip=True, mood="happy", right="front", look=(1, 0), item=lambda x, y: newspaper(x, y + 6, 1.0))
        A(p.X(0.22), p.Y(0.03), 1.1, hat=False, mood="think", right="chin", look=(1, 0))
        say(p, "Dědo, máš noviny vzhůru nohama.", *hd("alica", p.X(0.22), p.Y(0.03), 1.1), w=140)
    with Pn(*R[2]) as p:
        bg_fill(p, 0.9)
        notebook_big(p.X(0.08), p.Y(0.06), p.w*0.84, p.h*0.88, "PODEZŘELÍ:",
                     ["1. myši: NE. Berou jen hvězdičky,", "    a celé. Myš by nechala drobky.",
                      "2. Joey: NE. Neumí otevřít plechovku.", "3. Hanka: NE. Měla tmavé drobky.",
                      "4. Tonda: NE. V noci nebyl v domě", "    a měsíčky jsou všechny.",
                      "5. sýkorky: jen za oknem!", "", "6. ??? Kdo zbývá?"])
    page_end()


# =================================================================== 14 Hanka finds the clue
def page_boots():
    R = rows([(260, [1]), (240, [0.5, 0.5]), (250, [1])])
    with Pn(*R[0]) as p:
        fy = hallway(p)
        big_boots(p.X(0.6), fy, 2.2, needles=True, ribbon=True)
        Hk(p.X(0.3), fy, 1.3, hat=False, mood="wow", right="point", look=(1, -0.6))
        cap(p, "V předsíni, přesně ve výšce Hanky.", w=230)
        say(p, "Jehličí! A stužka!", *hd("hanka", p.X(0.3), fy, 1.3), w=110, area=(0.0, 0.5))
    with Pn(*R[1]) as p:
        fy = hallway(p)
        big_boots(p.X(0.5), fy + 4, 3.0, needles=True, ribbon=True)
        cap(p, "Dědovy boty. Ráno mokré.", w=170)
    with Pn(*R[2]) as p:
        kitchen(p, table=False)
        babicka(p.X(0.4), p.Y(0.03), 1.15, mood="surprised", right="front", look=(1, 0), item=lambda x, y: ribbon_spool(x, y - 4, 1.0))
        say(p, "Kde je moje červená stužka? Zbyl jen kousek!", *hd("babi", p.X(0.4), p.Y(0.03), 1.15), w=170)
    with Pn(*R[3]) as p:
        kitchen(p, table=False)
        shape([(p.X(0.55), p.Y(0.35)), (p.X(0.85), p.Y(0.35)), (p.X(0.83), p.Y(0.22)), (p.X(0.57), p.Y(0.22))], 0.8, BG)
        piping_bag(p.X(0.7), p.Y(0.37), 1.6, rot=-70)
        A(p.X(0.25), p.Y(0.03), 1.2, hat=False, mood="think", right="chin", look=(1, 0))
        gm(p.X(0.85), p.Y(0.35) + 13)                  # on the edge of the sink
        say(p, "A ve dřezu je sáček od bílé polevy. Kdo v noci zdobil?", *hd("alica", p.X(0.25), p.Y(0.03), 1.2), w=190, area=(0.0, 0.7))
    page_end()


# =================================================================== 15 Alica counts
def page_count():
    R = rows([(250, [1]), (260, [0.5, 0.5]), (240, [1])])
    with Pn(*R[0]) as p:
        bg_fill(p, 0.9)
        tally(p, ["1. ráno: bylo 12, zbylo 5. Pryč je 7.", "2. ráno: bylo 5, zbyly 3. Pryč jsou 2.", "", "Proč nejdřív 7 a potom 2?"])
    with Pn(*R[1]) as p:
        kitchen(p, table=False)
        club_photo7(p.X(0.08), p.Y(0.3), p.w*0.84, p.h*0.5)
        for i in range(7): hand_text(p.X(0.08) + p.w*0.84*(0.09 + i*0.135) - 8, p.Y(0.82), 16, str(i + 1), "SHB", 13)
        Hk(p.X(0.82), p.Y(0.0), 0.9, hat=False, flip=True, mood="wow", look=(1, 0.4))
    with Pn(*R[2]) as p:
        kitchen(p, table=False)
        Hk(p.X(0.3), p.Y(0.03), 1.25, hat=False, mood="grin", right="up", look=(1, 0))
        say(p, "V klubu je nás sedm!", *hd("hanka", p.X(0.3), p.Y(0.03), 1.25), w=120)
    with Pn(*R[3]) as p:
        kitchen(p, table=False)
        A(p.X(0.12), p.Y(0.03), 1.25, hat=False, mood="determined", right="up", look=(1, 0))
        Hk(p.X(0.88), p.Y(0.03), 1.15, hat=False, flip=True, mood="wow", look=(1, 0))
        gm(p.X(0.5), p.Y(0.06))
        say(p, "Sedm hvězdiček pro sedm členů! A jehličí… velký smrk roste jen u mlýna.",
            *hd("alica", p.X(0.12), p.Y(0.03), 1.25), w=220, x=p.X(0.2), y=p.Y(0.95))
        say(p, "U Věrky!", *hd("hanka", p.X(0.88), p.Y(0.03), 1.15), w=90, x=p.X(0.72), y=p.Y(0.72))
    page_end()


# =================================================================== 16 STOP, DETEKTIVE!
def page_stop():
    with Pn(M, 40, W-2*M, H-80, bg=0.95) as p:
        title(p.X(0.5), p.Y(0.92), "STOP, DETEKTIVE!", 44)
        hand_text(p.X(0.05), p.Y(0.86), p.w*0.9, "Už máš všechny stopy.", "SHB", 18)
        cw, ch = p.w*0.3, p.h*0.215
        items = [
            ("stopičky a ťukance za oknem", lambda x, y: [bird_print(x - 16 + i*10, y + 24 + (i % 2)*6, 1.6, 10) for i in range(4)]),
            ("past na myši: bez návnady", lambda x, y: mousetrap(x, y + 14, 1.6)),
            ("tmavé drobky, bílé hvězdičky", lambda x, y: (crumbs(x - 18, y + 30, 18, 8, 7), star_cookie(x + 18, y + 32, 1.4))),
            ("7 hvězdiček, potom 2", lambda x, y: (hand_text(x - 30, y + 30, 60, "7 … 2", "SHB", 22))),
            ("fotka klubu", lambda x, y: club_photo7(x - 34, y + 6, 68, 48)),
            ("jehličí a stužka na botách", lambda x, y: big_boots(x, y + 4, 1.1, needles=True, ribbon=True)),
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
        hand_text(p.X(0.12), by + 36, p.w*0.74, "Strana 7: co svítí u branky?", "SH", 14, align="left")
        magnifier(p.X(0.9), by + 30, ang=-30, r=12)
        hand_text(p.X(0.05), by - 32, p.w*0.9, "Kdo bere hvězdičky? Kam je nosí?", "SHB", 20)
        hand_text(p.X(0.05), by - 58, p.w*0.9, "A proč nejdřív sedm a potom dvě?", "SHB", 20)
        hand_text(p.X(0.05), by - 84, p.w*0.9, "Nápověda: prohlédni si znovu strany 2, 3 a 10.", "SH", 14)
        with T(p.X(0.5), p.Y(0.06), 1.0, rot=180):
            hand_text(-p.w*0.45, 0, p.w*0.9, "Děda! Nosí hvězdičky na smrk u mlýna, jednu pro každého člena klubu.", "SH", 12)
            hand_text(-p.w*0.45, -15, p.w*0.9, "Dvě mu tam snědly sýkorky, a tak vzal další dvě. Otoč na další stranu!", "SH", 12)
    page_end()


# =================================================================== 17 to the mill
def page_to_mill():
    R = rows([(260, [1]), (240, [0.5, 0.5]), (250, [1])])
    with Pn(*R[0]) as p:
        gy = p.Y(0.3)
        winter_garden(p, gy, 47, house_x=0.12, house_s=0.9, night=True)
        for i in range(7): boot_print(p.X(0.24) + i*p.w*0.1, p.Y(0.1) + (i % 2)*9, 0.8, -90, g=0.4)
        A(p.X(0.42), p.Y(0.03), 1.2, mood="whisper", right="front", look=(1, 0), item=lambda x, y: lantern(x, y - 18, 0.6, glow=True))
        Hk(p.X(0.56), p.Y(0.03), 1.1, mood="determined", look=(1, 0))
        joey(p.X(0.72), p.Y(0.03), 0.9, pose="sniff", mood="happy")
        cap(p, "První adventní neděle, za svítání.", w=240)
        say(p, "Půjdeme po dědových stopách.", *hd_h("alica", p.X(0.42), p.Y(0.03), 1.2), w=150, whisper=True, area=(0.3, 0.8))
    with Pn(*R[1]) as p:
        gy = p.Y(0.35)
        winter_garden(p, gy, 48, house_x=0.78, house_s=1.0, night=True)
        betka(p.X(0.38), p.Y(0.03), 1.4, mood="surprised", look=(1, 0))
        say(p, "Děda Franta taky odešel brzo ráno!", *hd_h("betka", p.X(0.38), p.Y(0.03), 1.4), w=140, whisper=True)
    with Pn(*R[2]) as p:
        winter_garden(p, p.Y(0.35), 49, hills_=False, night=True)
        tit(p.X(0.6), p.Y(0.72), 1.8, kind="great", pose="fly"); tit(p.X(0.75), p.Y(0.62), 1.6, kind="blue", pose="fly")
        Hk(p.X(0.25), p.Y(0.03), 1.35, mood="wow", right="point", look=(1, 0.6))
        say(p, "Sýkorky letí s námi!", *hd_h("hanka", p.X(0.25), p.Y(0.03), 1.35), w=110, area=(0.0, 0.5))
    with Pn(*R[3]) as p:
        gy = p.Y(0.3)
        mill_dawn(p, gy, 0.62, 0.9, SPRUCE_STARS, mill_x=0.22, lanterns=((0.5, 0.26), (0.74, 0.25)))
        gm(p.X(0.22) + 2, gy + 26)
        cap(p, "U mlýna svítí lucerny.", w=180)
    page_end()


# =================================================================== 18 the star spruce
def page_spruce():
    R = rows([(470, [1]), (280, [0.5, 0.5])])
    with Pn(*R[0]) as p:
        gy = p.Y(0.2)
        mill_dawn(p, gy, 0.5, 1.75, SPRUCE_FULL, mill_x=None)
        ladder(p.X(0.66), p.Y(0.03), p.Y(0.5))
        deda(p.X(0.78), p.Y(0.03), 1.05, flip=True, mood="surprised", right="front", look=(-1, 0),
             item=lambda x, y: star_cookie(x, y, 1.0))
        franta(p.X(0.9), p.Y(0.03), 1.0, flip=True, mood="grin", look=(-1, 0))
        verka_old(p.X(0.3), p.Y(0.03), 1.0, mood="happy", look=(1, 0), item=lambda x, y: lantern(x, y - 18, 0.6, glow=True))
        A(p.X(0.08), p.Y(0.03), 1.2, mood="wow", look=(1, 0.4))
        Hk(p.X(0.18), p.Y(0.03), 1.1, mood="wow", right="point", look=(1, 0.4))
        cap(p, "Hvězdičkový smrk.", w=150)
        say(p, "No jo. Prozradili jste nás.", *hd("deda", p.X(0.78), p.Y(0.03), 1.05), w=130, area=(0.6, 1.0))
    with Pn(*R[1]) as p:
        bg_fill(p, P.SPRUCE)
        for i, name in enumerate(("ALICA", "HANKA", "BĚTKA", "TONDA")):
            cx, cy = p.X(0.25 + (i % 2)*0.5), p.Y(0.72 - (i // 2)*0.45)
            stroke([(cx, cy + 40), (cx, cy + 60)], 2.0, g=P.RIBBON)
            star_cookie(cx, cy, 4.4)
            hand_text(cx - 30, cy - 4, 60, name, "SHB", 11, g=0.0)
    with Pn(*R[2]) as p:
        mill_dawn(p, p.Y(0.35), 0.8, 0.6, (), mill_x=None)
        A(p.X(0.25), p.Y(0.03), 1.3, mood="grin", right="up", look=(1, 0))
        say(p, "Hvězdičky s našimi jmény!", *hd_h("alica", p.X(0.25), p.Y(0.03), 1.3), w=120, area=(0.0, 0.6))
    page_end()


# =================================================================== 19 why two more
def page_why():
    R = rows([(260, [1]), (240, [0.5, 0.5]), (250, [1])])
    with Pn(*R[0]) as p:
        gy = p.Y(0.2)
        mill_dawn(p, gy, 0.55, 1.1, SPRUCE_STARS, mill_x=None)
        deda(p.X(0.2), p.Y(0.03), 1.05, mood="happy", right="point", look=(1, 0.5))
        say(p, "Vaše první hvězdičky snědly sýkorky. Tak jsem musel pro další dvě.", *hd("deda", p.X(0.2), p.Y(0.03), 1.05),
            w=200, area=(0.0, 0.45))
    with Pn(*R[1]) as p:
        mill_dawn(p, p.Y(0.35), 0.85, 0.5, (), mill_x=None)
        A(p.X(0.35), p.Y(0.03), 1.35, mood="wow", right="up", look=(1, 0))
        say(p, "Proto nejdřív sedm a potom dvě!", *hd_h("alica", p.X(0.35), p.Y(0.03), 1.35), w=130)
    with Pn(*R[2]) as p:
        mill_dawn(p, p.Y(0.35), 0.88, 0.5, (), mill_x=None)
        deda(p.X(0.55), p.Y(0.03), 1.05, flip=True, mood="grin", look=(1, 0))
        Hk(p.X(0.18), p.Y(0.03), 1.2, mood="grin", look=(1, 0))
        say(p, "A myši?", *hd_h("hanka", p.X(0.18), p.Y(0.03), 1.2), w=80, area=(0.0, 0.35))
        say(p, "Žádné nebyly. Proto jsem do pasti nic nedal.", *hd("deda", p.X(0.55), p.Y(0.03), 1.05), w=150, area=(0.3, 1.0))
    with Pn(*R[3]) as p:
        gy = p.Y(0.25)
        sky(p, P.SNOW_SKY); snow_field(p, gy, 8)
        star_spruce(p.X(0.55), gy - 4, 0.95, [(-0.5, 0.2, False), (0.4, 0.4, False), (0.0, 0.7, False)])
        young(p.X(0.25), p.Y(0.05), 1.1, "deda", mood="grin", right="up")
        young(p.X(0.78), p.Y(0.05), 1.1, "franta", flip=True, mood="happy", right="up")
        young(p.X(0.88), p.Y(0.05), 1.05, "verka", flip=True, mood="happy")
        gm(p.X(0.55) + 30, gy + 40)
        memory_frame(p)
        cap(p, "Před šedesáti lety věšel každý člen klubu svoji hvězdičku. Když se Věrka odstěhovala, přestali.", w=320)
    page_end()


# =================================================================== 20 the tradition is back
def page_back():
    R = rows([(260, [1]), (240, [0.5, 0.5]), (250, [1])])
    with Pn(*R[0]) as p:
        gy = p.Y(0.25)
        mill_dawn(p, gy, 0.65, 1.15, SPRUCE_FULL, mill_x=None)
        verka_old(p.X(0.25), p.Y(0.03), 1.05, mood="happy", right="up", look=(1, 0.3))
        say(p, "Šedesát let tu nevisela ani jedna.", *hd("verka", p.X(0.25), p.Y(0.03), 1.05), w=140, area=(0.0, 0.45))
    with Pn(*R[1]) as p:
        mill_dawn(p, p.Y(0.35), 0.85, 0.55, (), mill_x=None)
        betka(p.X(0.38), p.Y(0.03), 1.55, mood="wow", right="front", look=(1, 0), item=lambda x, y: star_cookie(x, y - 2, 1.2))
        say(p, "Mám hvězdičku… i když jsem na zkoušku?", *hd_h("betka", p.X(0.38), p.Y(0.03), 1.55), w=140, whisper=True)
    with Pn(*R[2]) as p:
        mill_dawn(p, p.Y(0.35), 0.15, 0.55, (), mill_x=None)
        franta(p.X(0.55), p.Y(0.03), 1.0, mood="happy", right="front", look=(-1, 0))
        say(p, "Hvězdička se nedává na zkoušku.", *hd("franta", p.X(0.55), p.Y(0.03), 1.0), w=140)
    with Pn(*R[3]) as p:
        gy = p.Y(0.3)
        mill_dawn(p, gy, 0.5, 0.95, SPRUCE_FULL, mill_x=None)
        for fx, fn in ((0.08, lambda x, y: deda(x, y, 0.95, mood="grin")), (0.18, lambda x, y: verka_old(x, y, 0.9, mood="happy")),
                       (0.3, lambda x, y: A(x, y, 1.05, mood="grin", right="wave")), (0.7, lambda x, y: Hk(x, y, 1.0, mood="grin")),
                       (0.8, lambda x, y: betka(x, y, 1.1, mood="grin", right="wave")), (0.92, lambda x, y: franta(x, y, 0.9, flip=True, mood="happy"))):
            fn(p.X(fx), p.Y(0.03))
        cap(p, "Klub Hvězdička je zase u svého smrku.", w=250)
    page_end()


# =================================================================== 21 for the birds
def page_birds():
    R = rows([(260, [1]), (240, [0.5, 0.5]), (250, [1])])
    with Pn(*R[0]) as p:
        gy = p.Y(0.25)
        mill_dawn(p, gy, 0.75, 1.0, SPRUCE_FULL, mill_x=None)
        babicka(p.X(0.25), p.Y(0.03), 1.1, mood="happy", right="front", look=(1, 0), item=lambda x, y: basket(x, y - 10))
        say(p, "Perník ptáčkům škodí. Tady jsou hvězdičky z loje a semínek!", *hd("babi", p.X(0.25), p.Y(0.03), 1.1), w=200,
            area=(0.0, 0.55))
    with Pn(*R[1]) as p:
        bg_fill(p, P.SPRUCE)
        for i, (fx, fy) in enumerate(((0.25, 0.65), (0.6, 0.75), (0.4, 0.3), (0.78, 0.35))):
            stroke([(p.X(fx), p.Y(fy) + 12), (p.X(fx), p.Y(fy) + 34)], 1.2, g=0.85)
            seed_star(p.X(fx), p.Y(fy), 2.2, string=False)
        tit(p.X(0.55), p.Y(0.42), 1.8, kind="great", pose="peck"); tit(p.X(0.3), p.Y(0.42), 1.6, flip=True, kind="blue")
        sfx(p.X(0.1), p.Y(0.88), "ŤUK!", 16, -6)
    with Pn(*R[2]) as p:
        winter_garden(p, p.Y(0.35), 50, hills_=False)
        Td(p.X(0.45), p.Y(0.03), 1.35, mood="worried", legs="walk", look=(1, 0))
        say(p, "Proč mě nikdo nevzbudil?!", *hd_h("tonda", p.X(0.45), p.Y(0.03), 1.35), w=130)
    with Pn(*R[3]) as p:
        kitchen(p, evening=True)
        for i, xx in enumerate((0.3, 0.44, 0.58, 0.72)):
            mug(p.X(xx), p.Y(0.38), 0.9); star_cookie(p.X(xx) + 14, p.Y(0.39), 0.8)
        deda(p.X(0.1), p.Y(0.03), 1.0, mood="grin", look=(1, 0))
        Hk(p.X(0.88), p.Y(0.03), 1.1, hat=False, flip=True, mood="grin", look=(1, 0))
        cap(p, "A perníkové hvězdičky? Ty se snědly doma u kakaa.", w=300)
    page_end()


# =================================================================== 22 activity
def page_quiz():
    with Pn(M, 40, W-2*M, H-80) as p:
        box = [(p.X(0.05), p.Y(0.905)), (p.X(0.95), p.Y(0.91)), (p.X(0.95), p.Y(0.905)+54), (p.X(0.05), p.Y(0.905)+52)]
        fill(box, 0.92)
        for a_, b_ in ((0, 1), (1, 2), (2, 3), (3, 0)): stroke([box[a_], box[b_]], 1.5)
        hand_text(p.X(0.05), p.Y(0.905)+18, p.w*0.9, "Detektivní zápisník", "SHB", 26)
        hand_text(p.X(0.05), p.Y(0.84), p.w*0.9, "Spočítej perníčky na talíři!", "SHB", 15)
        # the plate: every perníček in its own spot, none overlapping, so the count is fair
        shape(ell(p.X(0.3), p.Y(0.72), p.w*0.24, p.h*0.085, 40), 0.97, LINE*1.2)
        spots = [(-0.75, 0.25), (-0.45, 0.45), (-0.15, 0.55), (0.15, 0.55), (0.45, 0.45), (0.75, 0.25),
                 (-0.8, -0.2), (-0.5, -0.05), (-0.2, 0.1), (0.1, 0.1), (0.4, -0.05), (0.7, -0.2),
                 (-0.45, -0.5), (-0.1, -0.45), (0.25, -0.5)]
        kinds = [star_cookie, heart_cookie, moon_cookie, heart_cookie, star_cookie, moon_cookie, heart_cookie, moon_cookie,
                 star_cookie, heart_cookie, moon_cookie, heart_cookie, star_cookie, moon_cookie, heart_cookie]
        for (fx, fy), fn in zip(spots, kinds):
            fn(p.X(0.3) + fx*p.w*0.2, p.Y(0.72) + fy*p.h*0.07, 1.4, rot=fx*20)
        for i, txt in enumerate(("hvězdiček:", "srdíček:", "měsíčků:")):
            yy = p.Y(0.78) - i*26
            hand_text(p.X(0.58), yy, p.w*0.2, txt, "SH", 15, align="left")
            stroke([(p.X(0.8), yy - 3), (p.X(0.92), yy - 3)], 0.8, g=0.3)
        y = p.Y(0.6)
        qs = ["1. Proč neměla past na myši návnadu?", "2. Jaké drobky byly na Hančině polštáři?",
              "3. Kolik členů má Klub Hvězdička?", "4. Kdo snědl první dvě hvězdičky na smrku?"]
        for q in qs:
            hand_text(p.X(0.06), y, p.w*0.9, q, "SH", 15, align="left")
            stroke([(p.X(0.06), y - 24), (p.X(0.94), y - 24)], 0.5, g=0.5)
            y -= 50
        hand_text(p.X(0.06), y - 4, p.w*0.88, "Hvězdička pro ptáčky (s dospělým): rozpusť lůj, vmíchej semínka, nalij do formičky, nech ztuhnout a pověs ven.",
                  "SH", 13, align="left", lead=16)
        y -= 60
        hidden_gingerbread_man(p.X(0.09), y - 6, 13)        # the legend: not one of the hidden twelve
        hand_text(p.X(0.14), y - 4, p.w*0.82,
                  f"V sešitě se schovalo {N_HIDDEN} perníkových panáčků, jako je tenhle (ten se nepočítá). Najdeš je všechny?",
                  "SHB", 14, align="left", lead=18)
        pages = ", ".join(map(str, HID[:-1])) + " a " + str(HID[-1]) if HID else ""
        with T(p.X(0.5), p.Y(0.015), 1.0, rot=180):
            hand_text(-p.w*0.45, 0, p.w*0.9, f"Panáčci jsou na stranách {pages}.", "SH", 10)
            hand_text(-p.w*0.45, -13, p.w*0.9, "Na talíři: 4 hvězdičky, 6 srdíček, 5 měsíčků.", "SH", 10)
    page_end()


# =================================================================== 23 next time
def page_next():
    with Pn(M, 40, W-2*M, H-80, bg=0.95) as p:
        hand_text(p.X(0.1), p.Y(0.93), p.w*0.8, "Příště v sešitě č. 7:", "SHB", 20)
        title(p.X(0.5), p.Y(0.84), "JOEYHO VELKÝ DEN", 34)
        with Pn(p.X(0.08), p.Y(0.36), p.w*0.84, p.h*0.42, bg=0.9) as q:
            winter_garden(q, q.Y(0.35), 51, house_x=0.85, house_s=0.9, flakes=20)
            joey(q.X(0.5), q.Y(0.05), 1.6, pose="sniff", mood="happy")
            babicka(q.X(0.18), q.Y(0.03), 1.1, mood="worried", right="front", look=(1, 0))
            say(q, "Můj prstýnek! Spadl mi do sněhu…", *hd("babi", q.X(0.18), q.Y(0.03), 1.1), w=150)
        hand_text(p.X(0.1), p.Y(0.3), p.w*0.8, "Tentokrát vypráví Joey. A Joey má nejlepší nos ze všech.", "SH", 16, lead=21)
        hand_text(p.X(0.3), p.Y(0.19), p.w*0.4, "Detektivní tým:", "SHB", 16)
        A(p.X(0.06), p.Y(0.03), 0.85, mood="happy", right="wave")
        Hk(p.X(0.15), p.Y(0.03), 0.85, mood="grin")
        betka(p.X(0.24), p.Y(0.03), 0.95, mood="happy")
        joey(p.X(0.34), p.Y(0.03), 0.65, mood="happy")
        Td(p.X(0.45), p.Y(0.03), 0.8, mood="grin")
        babicka(p.X(0.56), p.Y(0.03), 0.78, mood="happy")
        deda(p.X(0.67), p.Y(0.03), 0.74, mood="happy")
        franta(p.X(0.78), p.Y(0.03), 0.7, flip=True, mood="happy")
        verka_old(p.X(0.9), p.Y(0.03), 0.72, flip=True, mood="happy")
    page_end()


# =================================================================== 24 back cover
def back_cover():
    with Pn(M, 40, W-2*M, H-80, bg=0.95) as p:
        gy = p.Y(0.24)
        sky(p, 0.72)
        snow_field(p, gy, 9)
        sx, ss = p.X(0.5), 2.4
        star_spruce(sx, gy - 10, ss, [(fx, fy, False) for fx, fy, _ in SPRUCE_FULL])
        for fx, fy in ((-0.55, 0.3), (0.5, 0.36), (-0.25, 0.62), (0.3, 0.75)):
            seed_star(sx + fx*70*ss, gy - 10 + (30 + fy*170)*ss, 2.0)
        tit(sx - 0.62*70*ss, gy - 10 + (30 + 0.22*170)*ss, 2.4, kind="great")
        tit(sx + 0.5*70*ss, gy - 10 + (30 + 0.58*170)*ss, 2.2, flip=True, kind="blue")
        title(p.X(0.5), p.Y(0.12), "HVĚZDIČKOVÝ SMRK", 32)
        hand_text(p.X(0.1), p.Y(0.06), p.w*0.8, "Klub Hvězdička zase visí na smrku.", "SHB", 18)
        hand_text(p.X(0.1), p.Y(0.015), p.w*0.8, "Velká a malá detektivka – sešit č. 6", "SH", 13, g=0.35)
    PAGE[0] += 1; cv.showPage()


cover(); page_cast(); page_baking(); page_morning(); page_lupa(); page_joey(); page_watch(); page_feeder()
page_turn(); page_locked(); page_hanka(); page_sorry(); page_board(); page_boots(); page_count(); page_stop()
page_to_mill(); page_spruce(); page_why(); page_back(); page_birds(); page_quiz(); page_next()
back_cover()
cv.save()
print("ok", PAGE[0] - 1, "pages")
import letter
if letter.MISSING: PROBLEMS.append("no glyph in the font for: " + " ".join(sorted(letter.MISSING)))
if len(HID) != N_HIDDEN: PROBLEMS.append(f"{len(HID)} hidden gingerbread men drawn, the notebook promises {N_HIDDEN}")
for pr in PROBLEMS: print("ORDER/LAYOUT:", pr)
if PROBLEMS: sys.exit(1)
