"""Velká a malá detektivka, issue 7: Joeyho velký den (outline: vault topics/comic-series/issue7-outline)"""
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
import chars3

W, H = A4
M = 28; GUT = 9; TOP = H - 30
OUT = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                   "comics", "velka_a_mala_detektivka", "07_joeyho_velky_den.pdf")
os.makedirs(os.path.dirname(OUT), exist_ok=True)
cv = canvas.Canvas(OUT, pagesize=A4); lib.set_canvas(cv)
cv.setTitle("Velká a malá detektivka – Případ č. 7: Joeyho velký den")
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



# =================================================================== issue 7 helpers
HEAD.update({"hajny": (116, 11)})
HID = []   # pages with a hidden bone, in order; the notebook's answer key is built from it
N_HIDDEN = 10


def kb(x, y, rot=20):
    """one of the 10 hidden bones (see joeyday.hidden_bone)"""
    hidden_bone(x, y, 13, rot)
    HID.append(PAGE[0])


def J(p, x, y, s, flip=False, pose="stand", **kw):
    """Joey, with his head kept clear of balloons"""
    joey(x, y, s, flip=flip, pose=pose, **kw)
    l, r, b, t = (23, 46, 15, 40) if pose == "sniff" else (18, 41, 36, 61)
    if flip: l, r = -r, -l
    keep_clear(p, x + l*s, y + b*s, x + r*s, y + t*s, "joey")


def jmouth(x, y, s, flip=False, sniff=False):
    """where something Joey carries in his mouth goes"""
    lx, ly = (41, 16) if sniff else (36, 37)
    return x + (-lx if flip else lx)*s, y + ly*s


def jc(p, txt, w=None, size=12.5, where="tl"):
    """Joey's caption: he tells the story, so his boxes carry his paw prints"""
    cap(p, txt, w, size, where)
    b = p.reads[-1]
    for k, px in enumerate((b["l"] + 7, b["r"] - 7)):
        paw_print(px, b["top"] - 1, 1.15, (-15, 15)[k], g=0.2, line=0.4)


def post(x, y, s=1.0):
    """a fence post with a cap of snow; returns the top"""
    sh_([(x - 5*s, y), (x + 5*s, y), (x + 5*s, y + 48*s), (x - 5*s, y + 48*s)], P.POST)
    shape(bez((x - 7*s, y + 47*s), (x - 6*s, y + 55*s), (x + 6*s, y + 55*s), (x + 7*s, y + 47*s)) + [(x - 7*s, y + 47*s)], P.SNOW, LINE*0.6)
    return y + 48*s


def garden7(p, gy, seed=1, house_x=None, feeder_x=None, feeder_s=1.0, shed_x=None, shed_s=0.8, pile_x=None, pile_w=110,
            fort_x=None, fort_s=0.8, night=False, flakes=0, removed=(), birds=0):
    """the snowy chalupa garden: house, the bird feeder, the woodshed, the snow pile, the fort"""
    winter_garden(p, gy, seed, house_x=house_x, house_s=0.9, night=False, hills_=True, flakes=flakes)
    if shed_x is not None: woodshed(p.X(shed_x), gy - 2, shed_s)
    if pile_x is not None: snow_pile(p.X(pile_x), gy - 4, pile_w, pile_w*0.38)
    if feeder_x is not None: bird_feeder(p.X(feeder_x), gy - 6, feeder_s, birds)
    c = snow_fort(p.X(fort_x), gy - 6, fort_s, removed=removed) if fort_x is not None else {}
    if night: bg_fill(p, 0.0, 0.22)
    return c


def kids_room_window(p):
    """the hallway window looking out at the fort"""
    x0, x1, y0, y1 = p.X(0.6), p.X(0.92), p.Y(0.42), p.Y(0.88)
    shape([(x0 - 6, y0 - 6), (x1 + 6, y0 - 6), (x1 + 6, y1 + 6), (x0 - 6, y1 + 6)], P.DOOR_FRAME, BG)
    shape([(x0, y0), (x1, y0), (x1, y1), (x0, y1)], P.SNOW_SKY, BG)
    fill([(x0, y0), (x1, y0), (x1, y0 + (y1 - y0)*0.35), (x0, y0 + (y1 - y0)*0.35)], P.SNOW)
    snow_fort((x0 + x1)/2, y0 + (y1 - y0)*0.3, 0.32, flag=True)
    s_([((x0 + x1)/2, y0), ((x0 + x1)/2, y1)], BG*1.6, g=P.DOOR_FRAME); s_([(x0, (y0 + y1)/2), (x1, (y0 + y1)/2)], BG*1.6, g=P.DOOR_FRAME)
    return (x0 + x1)/2, y0 + (y1 - y0)*0.4


RING_BLOCK = (1, 1)                        # the block the ring froze into: low on the left, where Bětka put the feeder-end blocks


# =================================================================== 1 COVER
def cover():
    with Pn(M, 40, W-2*M, H-80) as p:
        gy = p.Y(0.3)
        c = garden7(p, gy, 71, house_x=0.12, feeder_x=0.3, feeder_s=1.3, fort_x=0.7, fort_s=1.25, birds=1)
        rx, ry = c[RING_BLOCK]
        ring(rx, ry, 1.6)
        J(p, p.X(0.4), p.Y(0.05), 2.4, pose="sniff", mood="happy")
        smell_trail([(p.X(0.4) + 46*2.4, p.Y(0.05) + 22*2.4), (p.X(0.5), p.Y(0.2)), (rx - 30, ry - 10), (rx, ry)], 1.6)
        A(p.X(0.1), p.Y(0.03), 2.1, mood="surprised", right="lens", lens=True, look=(1, 0.2))
        Hk(p.X(0.88), p.Y(0.03), 2.0, flip=True, mood="grin", right="point", look=(-1, 0.3))
    box = [(M+34, H-236), (W-M-30, H-232), (W-M-34, H-48), (M+30, H-52)]
    fill([(x+3, y-3) for x, y in box], 0.0, 0.25); fill(box, 1.0)
    for a_, b_ in ((0, 1), (1, 2), (2, 3), (3, 0)): stroke([box[a_], box[b_]], 1.8)
    series_title(W/2, H-98, H-160, 40, 66)
    hand_text(M+40, H-190, W-2*M-80, "Alica, Hanka a Joey", "SHB", 20)
    hand_text(M+40, H-217, W-2*M-80, "Případ č. 7: Joeyho velký den", "SH", 15)
    magnifier(M+82, H-120, ang=-30, r=17)
    paw_print(W-M-100, H-118, 3.0, 15, g=0.2)
    page_end()


# =================================================================== 2 WHO IS WHO (as Joey smells them)
def page_cast():
    with Pn(M, 40, W-2*M, H-80) as p:
        hand_text(p.X(0.05), p.Y(0.95), p.w*0.9, "Kdo je kdo (jak voní Joeymu)", "SHB", 26)
        cells = [
            ("Velká", "Alica. Voní pastelkami.", lambda x, y: A(x, y, 0.9, hat=False, mood="happy", right="lens", lens=True)),
            ("Malá", "Hanka. Voní opičkou.", lambda x, y: Hk(x, y, 1.1, hat=False, mood="grin")),
            ("Joey", "To jsem já. Mám nejlepší nos.", lambda x, y: joey(x, y, 1.2, mood="happy")),
            ("Babička", "Voní levandulí.", lambda x, y: babicka(x, y, 0.82, mood="happy")),
            ("Děda", "Voní dřevem a kouřem.", lambda x, y: deda(x, y, 0.74, mood="happy")),
            ("Bětka", "Voní sněhem.", lambda x, y: betka(x, y, 1.0, mood="happy")),
            ("Tonda", "Voní svačinou.", lambda x, y: Td(x, y, 0.88, hat=False, mood="grin")),
            ("Pan hajný", "Voní lesem.", lambda x, y: hajny(x, y, 0.72, mood="happy")),
            ("Straka", "Nevím. Nikdy mě k ní nepustí.", lambda x, y: magpie(x, y + 20, 1.6)),
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
        hand_text(p.x + 20, by + bh - 28, p.w*0.55, "Tentokrát vypráví Joey.", "SHB", 17, align="left")
        hand_text(p.x + 20, by + bh - 52, p.w*0.55,
                  "Joeyho slova jsou v rámečcích s tlapkou. Lidé mu nerozumějí. Ty ano!",
                  "SH", 13, align="left", lead=17)
        lx, ly = p.X(0.68), by + bh*0.62
        smell_trail([(lx - 20, ly - 6), (lx + 40, ly + 4), (lx + 110, ly - 4)], 1.4, every=60)
        hand_text(p.X(0.62), by + 18, p.w*0.34, "Takhle Joey kreslí vůni babiččina krému: levandule.", "SH", 11.5, align="left", lead=14)
        paw_print(p.X(0.06), by + 14, 1.6, 10, g=0.2)
    page_end()


# =================================================================== 3 Joey introduces himself; the ring
def page_hello():
    R = rows([(270, [1]), (220, [0.5, 0.5]), (260, [1])])
    with Pn(*R[0]) as p:
        garden7(p, p.Y(0.3), 72, house_x=0.82)
        J(p, p.X(0.35), p.Y(0.04), 2.2, mood="happy")
        jc(p, "Ahoj, já jsem Joey. Psi neumějí číst. Zato umějí čmuchat. A já čmuchám nejlíp ze všech.", w=250)
    with Pn(*R[1]) as p:
        bg_fill(p, 0.9)
        J(p, p.X(0.2), p.Y(0.05), 2.0, pose="sniff", mood="happy")
        smell_trail([(p.X(0.98), p.Y(0.7)), (p.X(0.75), p.Y(0.45)), (p.X(0.2) + 50*2.0, p.Y(0.05) + 22*2.0)], 1.3, every=55)
        jc(p, "Každá věc má svou vůni.", w=170)
    with Pn(*R[2]) as p:
        kitchen(p, table=False)
        babicka(p.X(0.5), p.Y(0.03), 1.2, mood="happy", right="front", look=(1, 0), item=lambda x, y: hand_cream(x, y - 8, 0.8))
        smell_trail([(p.X(0.55), p.Y(0.55)), (p.X(0.8), p.Y(0.6)), (p.X(0.98), p.Y(0.5))], 1.2, every=50)
        jc(p, "Babička si maže ruce krémem. Levandule! Moje nejmilejší vůně.", w=150)
    with Pn(*R[3]) as p:
        kitchen(p, table=False)
        babicka(p.X(0.22), p.Y(0.03), 1.15, mood="happy", right="front", look=(1, 0), item=lambda x, y: ring(x + 4, y + 2, 0.7))
        Hk(p.X(0.5), p.Y(0.03), 1.15, hat=False, flip=True, mood="wow", look=(-1, 0.2))
        J(p, p.X(0.74), p.Y(0.03), 1.05, flip=True, mood="happy")
        ring_big(p.X(0.88), p.Y(0.72), 0.9)
        say(p, "Tenhle prstýnek mi dal děda. Je na něm hvězdička jejich klubu.", *hd("babi", p.X(0.22), p.Y(0.03), 1.15),
            w=200, area=(0.0, 0.5))
        say(p, "Klub Hvězdička!", *hd("hanka", p.X(0.5), p.Y(0.03), 1.15), w=110, area=(0.3, 0.75))
        jc(p, "Prstýnek? Co to je? Dá se to jíst?", w=150, where="br")
    page_end()


# =================================================================== 4 the morning at the feeder
def page_feeder():
    R = rows([(280, [1]), (220, [0.5, 0.5]), (250, [1])])
    with Pn(*R[0]) as p:
        gy = p.Y(0.3)
        garden7(p, gy, 73, house_x=0.08, feeder_x=0.5, feeder_s=1.3, birds=2)
        post(p.X(0.72), gy - 8, 1.0)
        snow_fence(p.X(0.72), p.x + p.w + 5, gy - 6, 40)
        babicka(p.X(0.32), p.Y(0.03), 1.15, mood="worried", right="front", look=(1, 0.3))
        J(p, p.X(0.85), p.Y(0.03), 1.0, flip=True, mood="happy")
        kb(p.X(0.04), p.Y(0.06))
        jc(p, "Ráno. Mrzne, až praští.", w=170)
        say(p, "Brr! Mám studené ruce a prstýnek mi padá.", *hd("babi", p.X(0.32), p.Y(0.03), 1.15), w=170, area=(0.0, 0.62))
    with Pn(*R[1]) as p:
        winter_garden(p, p.Y(0.3), 74, hills_=False)
        top = post(p.X(0.6), p.Y(0.1), 2.0)
        babi_glove(p.X(0.6), top + 6, 1.2, rot=-90)
        jc(p, "Babička si sundala rukavici a dala ji na sloupek.", w=150)
    with Pn(*R[2]) as p:
        bg_fill(p, P.SNOW_SKY)
        fill([(p.x - 5, p.y - 5), (p.x + p.w + 5, p.y - 5), (p.x + p.w + 5, p.Y(0.3)), (p.x - 5, p.Y(0.3))], P.SNOW)
        hx, hy = p.X(0.55), p.Y(0.72)
        shape([(hx + 14, hy - 8), (p.x + p.w + 5, hy + 6), (p.x + p.w + 5, hy + 34), (hx + 14, hy + 12)], P.CARDIGAN, LINE)
        for k, (fx, fy, a) in enumerate(((-24, 8, 10), (-26, -1, 0), (-24, -10, -10), (-19, -17, -20))):
            shape(ell(hx + fx, hy + fy, 11, 4.2, 16, rot=a), P.SKIN, LINE*0.8)
        shape(ell(hx - 4, hy, 18, 14, 24), P.SKIN, LINE)
        shape(ell(hx - 10, hy + 14, 8, 4, 14, rot=40), P.SKIN, LINE*0.8)
        for k in range(6): dot(hx - 12 + k*4, hy + 2 - (k % 2)*3, 1.2, P.SEEDS)
        ring(p.X(0.42), p.Y(0.38), 1.6, rot=30)
        for k in range(3): stroke([(p.X(0.42), p.Y(0.48) + k*10), (p.X(0.42) + 3, p.Y(0.52) + k*10)], LINE*0.6, g=0.4)
        sfx(p.X(0.14), p.Y(0.32), "PLUP", 14, -8)
        jc(p, "Něco malého spadlo do sněhu. Nikdo to neviděl. Jen já.", w=170)
    with Pn(*R[3]) as p:
        gy = p.Y(0.3)
        garden7(p, gy, 75, house_x=0.08, feeder_x=0.4, feeder_s=1.2, birds=1)
        sx, sy = p.X(0.5), gy - 4
        shape(ell(sx, sy, 7, 2.5, 14), 0.75, LINE*0.4)
        smell_trail([(sx, sy), (sx + 20, sy + 40), (p.X(0.7), p.Y(0.55)), (p.X(0.72) + 34*1.3, p.Y(0.03) + 46*1.3)], 1.3, every=50)
        J(p, p.X(0.72), p.Y(0.03), 1.3, mood="happy")
        jc(p, "Voní to jako babiččiny ruce. Ale rukavice voní ještě víc!", w=230)
    page_end()


# =================================================================== 5 Joey's stash
def page_stash():
    R = rows([(270, [1]), (230, [0.5, 0.5]), (250, [1])])
    with Pn(*R[0]) as p:
        gy = p.Y(0.3)
        garden7(p, gy, 76, feeder_x=0.2, feeder_s=1.1)
        post(p.X(0.4), gy - 8, 1.1)
        J(p, p.X(0.6), p.Y(0.03), 1.4, mood="bark")
        gx, gy_ = jmouth(p.X(0.6), p.Y(0.03), 1.4)
        babi_glove(gx - 4, gy_ - 2, 0.9, rot=-100)
        kb(p.X(0.95), p.Y(0.07))
        jc(p, "Rukavice! Ta voní nejvíc. Poklad!", w=200)
    with Pn(*R[1]) as p:
        gy = p.Y(0.3)
        garden7(p, gy, 77, shed_x=0.65, shed_s=0.9)
        J(p, p.X(0.35), p.Y(0.06), 1.3, pose="sniff", mood="happy")
        snow_spray(p.X(0.35) - 10, p.Y(0.1), 1.2)
        sfx(p.X(0.08), p.Y(0.82), "HRAB HRAB", 15, -5)
    with Pn(*R[2]) as p:
        bg_fill(p, P.SNOW_SKY)
        fill([(p.x - 5, p.y - 5), (p.x + p.w + 5, p.y - 5), (p.x + p.w + 5, p.Y(0.6)), (p.x - 5, p.Y(0.6))], P.SNOW)
        stash(p.X(0.5), p.Y(0.15), 70, 20)
        jc(p, "Moje tajná skrýš: kost, stará ponožka a teď i rukavice.", w=200)
    with Pn(*R[3]) as p:
        gy = p.Y(0.3)
        garden7(p, gy, 78, house_x=0.15, feeder_x=0.55, feeder_s=1.1, birds=2)
        babicka(p.X(0.3), p.Y(0.03), 1.1, flip=True, mood="happy", legs="walk", look=(-1, 0))
        jc(p, "Babička šla domů. Na rukavici zapomněla. A na prstýnek taky.", w=230, where="tr")
        say(p, "Jdu uvařit čaj!", *hd("babi", p.X(0.3), p.Y(0.03), 1.1), w=110, area=(0.0, 0.5))
    page_end()


# =================================================================== 6 děda shovels
def page_shovel():
    R = rows([(290, [1]), (220, [0.5, 0.5]), (240, [1])])
    with Pn(*R[0]) as p:
        gy = p.Y(0.3)
        garden7(p, gy, 79, house_x=0.06, feeder_x=0.35, feeder_s=1.1, pile_x=0.85, pile_w=90)
        deda(p.X(0.55), p.Y(0.03), 1.1, mood="grin", right="front", look=(1, 0.3))
        shovel(p.X(0.55) + 26, p.Y(0.03) + 30, 0.9, rot=-55)
        throw_arc(p.X(0.62), p.Y(0.35), p.X(0.83), gy + 30)
        smell_trail([(p.X(0.4), gy - 2), (p.X(0.6), p.Y(0.38)), (p.X(0.75), p.Y(0.6)), (p.X(0.85), gy + 24)], 1.3, every=55)
        J(p, p.X(0.2), p.Y(0.03), 1.0, mood="happy")
        jc(p, "Děda hází sníh na hromadu. I ten sníh, co voní levandulí!", w=210)
        say(p, "Pěšinka musí být čistá!", *hd("deda", p.X(0.55), p.Y(0.03), 1.1), w=120, area=(0.4, 1.0))
    with Pn(*R[1]) as p:
        bg_fill(p, P.SNOW_SKY)
        for k, (fx, fy, rr) in enumerate(((0.3, 0.45, 26), (0.6, 0.6, 18), (0.78, 0.38, 14))):
            shape(ell(p.X(fx), p.Y(fy), rr, rr*0.8, 18), P.SNOW, LINE)
        ring(p.X(0.3), p.Y(0.45), 1.3, glint=False)
        lavender_sprig(p.X(0.3) + 30, p.Y(0.45) + 22, 1.6, -20)
        sfx(p.X(0.55), p.Y(0.18), "ŠUP!", 18, 6)
    with Pn(*R[2]) as p:
        gy = p.Y(0.3)
        garden7(p, gy, 80, pile_x=0.7, pile_w=120)
        J(p, p.X(0.3), p.Y(0.03), 1.2, mood="bark")
        sfx(p.X(0.55), p.Y(0.8), "HAF!", 16, -8)
        deda(p.X(0.88), p.Y(0.03), 0.9, flip=True, mood="happy", look=(-1, 0))
        say(p, "Neštěkej, Joey. Sníh ti neuteče.", *hd("deda", p.X(0.88), p.Y(0.03), 0.9), w=130, area=(0.3, 1.0))
    with Pn(*R[3]) as p:
        gy = p.Y(0.28)
        garden7(p, gy, 81, house_x=0.06, feeder_x=0.3, feeder_s=1.1, pile_x=0.62, pile_w=200, shed_x=0.9)
        for i in range(6): boot_print(p.X(0.36) + i*p.w*0.04, gy - 10 - (i % 2)*5, 0.6, -90, g=0.75)
        kb(p.X(0.47), gy - 18)
        jc(p, "Hromada je velká jako děda. A ta vůně je v ní.", w=220)
    page_end()


# =================================================================== 7 the snow fort
def page_fort():
    R = rows([(280, [1]), (220, [0.5, 0.5]), (250, [1])])
    with Pn(*R[0]) as p:
        gy = p.Y(0.28)
        garden7(p, gy, 82, pile_x=0.75, pile_w=170)
        snow_block(p.X(0.42), p.Y(0.05), 30, 18)
        betka(p.X(0.58), p.Y(0.03), 1.3, mood="grin", right="front", look=(1, 0), item=lambda x, y: block_saw(x, y, 0.8, rot=-20))
        A(p.X(0.12), p.Y(0.03), 1.2, mood="happy", right="front", look=(1, 0))
        Td(p.X(0.3), p.Y(0.03), 1.15, mood="grin", right="up", look=(1, 0))
        jc(p, "Odpoledne přišli Bětka a Tonda.", w=200)
        say(p, "Kostky řežeme z té velké hromady!", *hd_h("betka", p.X(0.58), p.Y(0.03), 1.3), w=150, area=(0.35, 1.0))
    with Pn(*R[1]) as p:
        gy = p.Y(0.28)
        garden7(p, gy, 83, fort_x=0.55, fort_s=0.95, removed={(3, c) for c in range(7)} | {(4, c) for c in range(0, 7, 2)})
        Hk(p.X(0.15), p.Y(0.03), 1.2, mood="grin", right="front", look=(1, 0), item=lambda x, y: snow_block(x - 12, y - 6, 24, 14))
        say(p, "Pevnost!", *hd_h("hanka", p.X(0.15), p.Y(0.03), 1.2), w=90, area=(0.0, 0.45))
    with Pn(*R[2]) as p:
        gy = p.Y(0.2)
        c = garden7(p, gy, 84, fort_x=0.6, fort_s=1.25)
        rx, ry = c[RING_BLOCK]
        J(p, p.X(0.08), p.Y(0.04), 1.1, pose="sniff", mood="happy")
        smell_trail([(rx, ry), (rx - 30, ry - 10), (p.X(0.08) + 46*1.1, p.Y(0.04) + 22*1.1)], 1.2, every=40)
        jc(p, "Levandule! V téhle kostce!", w=180)
    with Pn(*R[3]) as p:
        gy = p.Y(0.28)
        garden7(p, gy, 85, fort_x=0.5, fort_s=1.1)
        J(p, p.X(0.36), p.Y(0.04), 1.15, pose="sniff", mood="happy")
        snow_spray(p.X(0.36) - 6, p.Y(0.08), 1.1, seed=8)
        A(p.X(0.08), p.Y(0.03), 1.15, mood="surprised", right="point", look=(1, 0))
        Td(p.X(0.88), p.Y(0.03), 1.1, flip=True, mood="worried", right="hip", look=(-1, 0))
        kb(p.X(0.97), p.Y(0.75))
        say(p, "Joey, nekaž nám pevnost!", *hd_h("alica", p.X(0.08), p.Y(0.03), 1.15), w=130, area=(0.0, 0.45))
        say(p, "Jdi pryč, Joey!", *hd_h("tonda", p.X(0.88), p.Y(0.03), 1.1), w=100, area=(0.6, 1.0))
        jc(p, "Nikdo mi nerozumí.", w=140, where="br")
    page_end()


# =================================================================== 8 evening: the ring is gone
def page_gone():
    R = rows([(260, [1]), (230, [0.5, 0.5]), (260, [1])])
    with Pn(*R[0]) as p:
        kitchen(p, table=False, evening=True)
        babicka(p.X(0.4), p.Y(0.03), 1.2, mood="worried", right="up", look=(1, 0.3))
        A(p.X(0.7), p.Y(0.03), 1.15, hat=False, flip=True, mood="surprised", look=(-1, 0))
        jc(p, "Večer.", w=80)
        say(p, "Můj prstýnek! Je pryč!", *hd("babi", p.X(0.4), p.Y(0.03), 1.2), w=140)
    with Pn(*R[1]) as p:
        kitchen(p, table=False, evening=True)
        A(p.X(0.4), p.Y(0.03), 1.3, hat=False, mood="think", right="chin", look=(1, 0))
        say(p, "Kdy jsi ho měla naposledy?", *hd("alica", p.X(0.4), p.Y(0.03), 1.3), w=130)
    with Pn(*R[2]) as p:
        kitchen(p, table=False, evening=True)
        babicka(p.X(0.45), p.Y(0.03), 1.15, mood="worried", right="front", look=(1, 0))
        say(p, "Ráno u krmítka. Padal mi, jak jsem měla studené ruce.", *hd("babi", p.X(0.45), p.Y(0.03), 1.15), w=170)
    with Pn(*R[3]) as p:
        kitchen(p, table=False, evening=True)
        babicka(p.X(0.3), p.Y(0.03), 1.15, mood="sad", right="front", look=(1, -0.3))
        J(p, p.X(0.48), p.Y(0.03), 1.15, pose="sniff", mood="happy")
        deda(p.X(0.85), p.Y(0.03), 1.0, flip=True, mood="happy", look=(-1, 0))
        jc(p, "Prstýnek voní jako babiččiny ruce? Tak to je ta věc, co ráno spadla do sněhu! Já vím, kde je!", w=250)
        sfx(p.X(0.66), p.Y(0.38), "HAF HAF!", 15, 6)
        say(p, "Joey má hlad.", *hd("deda", p.X(0.85), p.Y(0.03), 1.0), w=100, area=(0.65, 1.0))
    page_end()


# =================================================================== 9 searching at the feeder
def page_search():
    R = rows([(280, [1]), (220, [0.5, 0.5]), (250, [1])])
    with Pn(*R[0]) as p:
        gy = p.Y(0.3)
        garden7(p, gy, 86, house_x=0.08, feeder_x=0.5, feeder_s=1.3, night=True)
        Hk(p.X(0.3), p.Y(0.03), 1.2, mood="determined", right="front", look=(1, 0), item=lambda x, y: torch(x, y, 10))
        hx_, hy_ = hand_pt(True, "front", p.X(0.3), p.Y(0.03), 1.2)
        torch_beam(hx_ + 8, hy_, p.X(0.62), p.Y(0.03), p.X(0.5), p.Y(0.02), 0.45)
        A(p.X(0.7), p.Y(0.03), 1.25, flip=True, mood="think", right="lens", lens=True, look=(-1, -0.4))
        jc(p, "Velká a Malá hledají u krmítka.", w=210)
    with Pn(*R[1]) as p:
        bg_fill(p, P.SNOW_SKY); bg_fill(p, 0.0, 0.18)
        fill([(p.x - 5, p.y - 5), (p.x + p.w + 5, p.y - 5), (p.x + p.w + 5, p.Y(0.55)), (p.x - 5, p.Y(0.55))], 0.8)
        for k in range(8): stroke([(p.X(0.05) + k*p.w*0.12, p.Y(0.1)), (p.X(0.12) + k*p.w*0.12, p.Y(0.5))], LINE*0.6, g=0.65)
        lx_, ly_ = p.X(0.5), p.Y(0.32)
        magnifier(lx_, ly_, ang=-30, r=34)
        say(p, "Tady je jen čistá pěšinka.", p.X(0.5), p.Y(0.6), w=140, x=p.X(0.05), y=p.Y(0.95))
    with Pn(*R[2]) as p:
        bg_fill(p, P.SNOW_SKY); bg_fill(p, 0.0, 0.18)
        bird_feeder(p.X(0.65), p.Y(0.02), 2.2)
        Hk(p.X(0.18), p.Y(0.03), 1.25, mood="worried", look=(1, 0.3))
        say(p, "Jen semínka.", *hd_h("hanka", p.X(0.18), p.Y(0.03), 1.25), w=100, area=(0.0, 0.45))
    with Pn(*R[3]) as p:
        gy = p.Y(0.3)
        garden7(p, gy, 87, feeder_x=0.12, feeder_s=1.0, fort_x=0.82, fort_s=0.8, night=True)
        A(p.X(0.32), p.Y(0.03), 1.2, flip=True, mood="worried", look=(-1, 0))
        J(p, p.X(0.48), p.Y(0.03), 1.1, mood="bark")
        kb(p.X(0.04), p.Y(0.06))
        say(p, "Joey, teď si hrát nebudeme.", *hd_h("alica", p.X(0.32), p.Y(0.03), 1.2), w=130, area=(0.0, 0.5))
        jc(p, "Ne tady! Tam! V pevnosti!", w=160, where="tr")
    page_end()


# =================================================================== 10 the glove is missing
def page_glove():
    R = rows([(250, [1]), (240, [0.5, 0.5]), (260, [1])])
    with Pn(*R[0]) as p:
        kitchen(p, table=False, evening=True)
        babicka(p.X(0.3), p.Y(0.03), 1.15, mood="surprised", right="hip", look=(1, 0))
        A(p.X(0.75), p.Y(0.03), 1.15, hat=False, flip=True, mood="think", right="chin", look=(-1, 0))
        say(p, "A kde je moje rukavice? Nechala jsem ji na sloupku.", *hd("babi", p.X(0.3), p.Y(0.03), 1.15), w=190)
    with Pn(*R[1]) as p:
        kitchen(p, table=False, evening=True)
        Td(p.X(0.4), p.Y(0.03), 1.3, hat=False, mood="determined", right="point", look=(1, 0))
        say(p, "Joey pořád něco nosí a zahrabává!", *hd("tonda", p.X(0.4), p.Y(0.03), 1.3), w=150)
    with Pn(*R[2]) as p:
        kitchen(p, table=False, evening=True)
        A(p.X(0.4), p.Y(0.03), 1.3, hat=False, mood="surprised", right="up", look=(1, 0))
        say(p, "Co když byl prstýnek v rukavici?", *hd("alica", p.X(0.4), p.Y(0.03), 1.3), w=140)
    with Pn(*R[3]) as p:
        kitchen(p, table=False, evening=True)
        J(p, p.X(0.5), p.Y(0.03), 1.5, mood="sad")
        for i, (fn, fx, fl) in enumerate(((A, 0.12, False), (Hk, 0.24, False), (Td, 0.8, True))):
            fn(p.X(fx), p.Y(0.03), 1.0, hat=False, flip=fl, mood="worried", look=(-1 if fl else 1, -0.3))
        jc(p, "Všichni se na mě dívají. Rukavici jsem vzal, to jo. Ale prstýnek ne!", w=270)
    page_end()


# =================================================================== 11 the stash dug up
def page_dig():
    R = rows([(270, [1]), (230, [0.5, 0.5]), (250, [1])])
    with Pn(*R[0]) as p:
        gy = p.Y(0.3)
        garden7(p, gy, 88, shed_x=0.82, shed_s=0.9, night=True)
        post(p.X(0.12), gy - 8, 1.0)
        paw_trail(p.X(0.15), p.Y(0.12), p.X(0.72), p.Y(0.18), 8, 1.6)
        Hk(p.X(0.4), p.Y(0.03), 1.2, mood="wow", right="point", look=(1, -0.3), item=lambda x, y: torch(x, y, -15))
        kb(p.X(0.05), p.Y(0.07))
        say(p, "Tlapky vedou k dřevníku!", *hd_h("hanka", p.X(0.4), p.Y(0.03), 1.2), w=130, area=(0.15, 0.7))
    with Pn(*R[1]) as p:
        bg_fill(p, P.SNOW_SKY); bg_fill(p, 0.0, 0.15)
        fill([(p.x - 5, p.y - 5), (p.x + p.w + 5, p.y - 5), (p.x + p.w + 5, p.Y(0.62)), (p.x - 5, p.Y(0.62))], P.SNOW)
        stash(p.X(0.5), p.Y(0.12), 70, 20)
        jc(p, "Moje skrýš! No jo…", w=150)
    with Pn(*R[2]) as p:
        winter_garden(p, p.Y(0.3), 89, hills_=False, night=True)
        Hk(p.X(0.4), p.Y(0.03), 1.4, mood="wow", right="up", look=(1, 0.3), item=lambda x, y: old_sock(x, y + 4, 1.2, rot=170))
        say(p, "Moje ponožka! Ta, co se ztratila v létě!", *hd_h("hanka", p.X(0.4), p.Y(0.03), 1.4), w=150)
    with Pn(*R[3]) as p:
        winter_garden(p, p.Y(0.3), 90, hills_=False, night=True)
        A(p.X(0.15), p.Y(0.03), 1.2, mood="think", right="lens", lens=True, look=(1, 0))
        babi_glove(p.X(0.32), p.Y(0.42), 1.6, rot=-30)
        deda(p.X(0.62), p.Y(0.03), 1.0, mood="happy", look=(1, 0))
        J(p, p.X(0.84), p.Y(0.03), 1.0, flip=True, mood="happy")
        say(p, "V rukavici prstýnek není.", *hd_h("alica", p.X(0.15), p.Y(0.03), 1.2), w=120, area=(0.0, 0.45))
        say(p, "Tak je Joey nevinný.", *hd("deda", p.X(0.62), p.Y(0.03), 1.0), w=110, area=(0.4, 0.8))
        jc(p, "No konečně.", w=110, where="br")
    page_end()


# =================================================================== 12 the magpie
def page_magpie():
    R = rows([(250, [1]), (230, [0.5, 0.5]), (270, [1])])
    with Pn(*R[0]) as p:
        fy = hallway(p)
        dog_bed(p.X(0.5), fy, 1.5)
        joey(p.X(0.5), fy + 4, 1.0, mood="sad")
        keep_clear(p, p.X(0.5) + 18, fy + 40, p.X(0.5) + 42, fy + 66, "joey")
        jc(p, "Rukavici babička zase má. Ale prstýnek pořád leží v pevnosti. A nikdo mě neposlouchá.", w=300)
    with Pn(*R[1]) as p:
        gy = p.Y(0.3)
        winter_garden(p, gy, 91, hills_=False)
        snow_fence(p.x - 5, p.x + p.w + 5, gy - 6, 40)
        magpie(p.X(0.5), gy + 36, 2.2, item=lambda x, y: foil(x + 4, y, 0.8, sparkle=True))
        jc(p, "Ráno.", w=70)
        sfx(p.X(0.15), p.Y(0.78), "ČÁ ČÁ!", 15, -6)
    with Pn(*R[2]) as p:
        winter_garden(p, p.Y(0.3), 92, hills_=False)
        Td(p.X(0.4), p.Y(0.03), 1.3, mood="determined", right="point", look=(1, 0.4))
        say(p, "Straka! Straky kradou lesklé věci! To ví každý!", *hd_h("tonda", p.X(0.4), p.Y(0.03), 1.3), w=160)
    with Pn(*R[3]) as p:
        gy = p.Y(0.3)
        garden7(p, gy, 93, house_x=0.06, fort_x=0.2, fort_s=0.65)
        magpie(p.X(0.9), p.Y(0.78), 1.4)
        for fn, fx in ((A, 0.45), (Td, 0.58), (Hk, 0.7)):
            fn(p.X(fx), p.Y(0.03), 1.0, mood="determined", legs="walk", look=(1, 0.4))
        J(p, p.X(0.32), p.Y(0.03), 1.0, flip=True, mood="bark")
        kb(p.X(0.08), p.Y(0.06))
        jc(p, "Ne! Opačně! Pevnost je tady!", w=200, where="tl")
    page_end()


# =================================================================== 13 the forester
def page_hajny():
    R = rows([(270, [1]), (230, [0.5, 0.5]), (250, [1])])
    with Pn(*R[0]) as p:
        gy = p.Y(0.3)
        winter_garden(p, gy, 94, trees=((0.62, 1.4), (0.8, 1.2), (0.95, 1.5)))
        magpie(p.X(0.62) + 16, p.Y(0.82), 1.2)
        hajny(p.X(0.72), p.Y(0.03), 1.05, flip=True, mood="happy", look=(-1, 0))
        A(p.X(0.12), p.Y(0.03), 1.15, mood="surprised", look=(1, 0))
        Hk(p.X(0.24), p.Y(0.03), 1.05, mood="wow", look=(1, 0))
        Td(p.X(0.36), p.Y(0.03), 1.1, mood="happy", look=(1, 0))
        say(p, "Copak hledáte, detektivové?", *hd("hajny", p.X(0.72), p.Y(0.03), 1.05, up=2.0), w=140, area=(0.5, 1.0))
    with Pn(*R[1]) as p:
        bg_fill(p, P.SNOW_SKY)
        fill([(p.x - 5, p.y - 5), (p.x + p.w + 5, p.y - 5), (p.x + p.w + 5, p.Y(0.35)), (p.x - 5, p.Y(0.35))], P.SNOW)
        foil(p.X(0.5), p.Y(0.42), 4.0)
        say(p, "To je jen papírek od perníčku.", p.x + p.w, p.Y(0.6), w=150, x=p.X(0.04), y=p.Y(0.95))
    with Pn(*R[2]) as p:
        winter_garden(p, p.Y(0.3), 95, hills_=False, trees=((0.85, 1.2),))
        hajny(p.X(0.45), p.Y(0.03), 1.05, mood="happy", right="up", look=(1, 0))
        say(p, "Straky se lesklých věcí spíš bojí. Vědci to zkoušeli.", *hd("hajny", p.X(0.45), p.Y(0.03), 1.05, up=2.0), w=170)
    with Pn(*R[3]) as p:
        winter_garden(p, p.Y(0.3), 96, trees=((0.75, 1.4), (0.95, 1.2)))
        A(p.X(0.12), p.Y(0.03), 1.15, mood="think", right="chin", look=(1, 0))
        hajny(p.X(0.62), p.Y(0.03), 1.0, flip=True, mood="grin", look=(-1, 0))
        J(p, p.X(0.32), p.Y(0.03), 0.95, mood="happy")
        say(p, "Tak to byla falešná stopa.", *hd_h("alica", p.X(0.12), p.Y(0.03), 1.15), w=120, area=(0.0, 0.4))
        say(p, "Zítra vám ukážu, jak se čtou stopy ve sněhu.", *hd("hajny", p.X(0.62), p.Y(0.03), 1.0, up=2.0), w=170, area=(0.3, 0.85))
        jc(p, "Já stopy čtu pořád. Čumákem.", w=160, where="br")
    page_end()


# =================================================================== 14 the suspect list
def page_board():
    R = rows([(240, [1]), (520, [1])])
    with Pn(*R[0]) as p:
        kitchen(p, table=False)
        A(p.X(0.25), p.Y(0.03), 1.2, hat=False, mood="think", right="chin", look=(1, 0))
        Hk(p.X(0.75), p.Y(0.03), 1.1, hat=False, flip=True, mood="think", look=(-1, 0))
        say(p, "Kam se mohl prstýnek ztratit?", *hd("alica", p.X(0.25), p.Y(0.03), 1.2), w=150)
    with Pn(*R[1]) as p:
        bg_fill(p, 0.9)
        notebook_big(p.X(0.08), p.Y(0.06), p.w*0.84, p.h*0.88, "PŘÍPAD Č. 7: PRSTÝNEK",
                     ["1. ráno u krmítka babičce padal", "    (studené ruce)",
                      "2. u krmítka teď nic není,", "    jen čistá pěšinka",
                      "3. Joey: NE. V rukavici nebyl.", "4. straka: NE. Měla papírek", "    od perníčku.", "",
                      "5. ??? Kam se poděl sníh", "    od krmítka?"])
    page_end()


# =================================================================== 15 STOP, DETEKTIVE!
def page_stop():
    with Pn(M, 40, W-2*M, H-80, bg=0.95) as p:
        title(p.X(0.5), p.Y(0.92), "STOP, DETEKTIVE!", 44)
        hand_text(p.X(0.05), p.Y(0.86), p.w*0.9, "Už máš všechny stopy. A víš víc než lidi!", "SHB", 18)
        cw, ch = p.w*0.3, p.h*0.215
        items = [
            ("studené ruce: prstýnek padá", lambda x, y: ring(x, y + 30, 2.2)),
            ("rukavice na sloupku", lambda x, y: babi_glove(x, y + 12, 1.3)),
            ("levandule: vůně babiččina krému", lambda x, y: lavender_sprig(x, y + 32, 3.0)),
            ("děda hází sníh na hromadu", lambda x, y: shovel(x, y + 8, 0.6, rot=-20)),
            ("pevnost z kostek z hromady", lambda x, y: snow_fort(x, y + 14, 0.3, flag=False)),
            ("papírek od perníčku", lambda x, y: foil(x, y + 32, 2.6)),
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
        hand_text(p.X(0.12), by + 36, p.w*0.74, "Strana 7: ke které kostce Joey čmuchá?", "SH", 14, align="left")
        paw_print(p.X(0.9), by + 30, 2.0, 10, g=0.2)
        hand_text(p.X(0.05), by - 32, p.w*0.9, "Kde je prstýnek? Jak se tam dostal?", "SHB", 20)
        hand_text(p.X(0.05), by - 58, p.w*0.9, "A jak to má Joey lidem říct?", "SHB", 20)
        hand_text(p.X(0.05), by - 84, p.w*0.9, "Nápověda: prohlédni si znovu strany 4, 6 a 7.", "SH", 14)
        with T(p.X(0.5), p.Y(0.06), 1.0, rot=180):
            hand_text(-p.w*0.45, 0, p.w*0.9, "V pevnosti! Spadl do sněhu u krmítka, děda ho odházel na hromadu", "SH", 12)
            hand_text(-p.w*0.45, -15, p.w*0.9, "a z hromady děti nařezaly kostky. Otoč na další stranu!", "SH", 12)
    page_end()


# =================================================================== 16 Joey tries to tell them
def page_try():
    R = rows([(240, [1]), (260, [0.5, 0.5]), (250, [1])])
    with Pn(*R[0]) as p:
        fy = hallway(p)
        J(p, p.X(0.5), fy, 1.8, mood="happy")
        jc(p, "Musím jim to říct. Psí řečí. Mám tři slova.", w=250)
    with Pn(*R[1]) as p:
        kitchen(p, table=False)
        A(p.X(0.74), p.Y(0.03), 1.3, hat=False, flip=True, mood="happy", right="front", look=(-1, -0.4))
        J(p, p.X(0.74) - 66, p.Y(0.03), 1.1, pose="paw", mood="happy")
        jc(p, "Tlapka na koleni znamená: POJĎ!", w=130)
        say(p, "Chceš piškot?", *hd("alica", p.X(0.74), p.Y(0.03), 1.3), w=100, area=(0.45, 1.0))
    with Pn(*R[2]) as p:
        kitchen(p, table=False)
        babicka(p.X(0.72), p.Y(0.03), 1.1, flip=True, mood="happy", look=(-1, -0.3))
        J(p, p.X(0.25), p.Y(0.03), 1.2, mood="sad")
        say(p, "Joey je dneska nějaký unavený.", *hd("babi", p.X(0.72), p.Y(0.03), 1.1), w=130, area=(0.4, 1.0))
        jc(p, "Já se dívám! To znamená: POSLOUCHEJ!", w=150, where="bl")
    with Pn(*R[3]) as p:
        gy = p.Y(0.28)
        garden7(p, gy, 97, fort_x=0.85, fort_s=0.75)
        Td(p.X(0.4), p.Y(0.03), 1.2, flip=True, mood="grin", right="up", look=(-1, 0))
        J(p, p.X(0.25), p.Y(0.03), 1.1, pose="sniff", mood="happy")
        say(p, "Chceš si hrát? Hoď mi míček!", *hd_h("tonda", p.X(0.4), p.Y(0.03), 1.2), w=140, area=(0.0, 0.65))
        jc(p, "Šťouchám čumákem. To znamená: TAM!", w=170, where="br")
    page_end()


# =================================================================== 17 sent inside
def page_inside():
    R = rows([(270, [1]), (230, [0.5, 0.5]), (250, [1])])
    with Pn(*R[0]) as p:
        gy = p.Y(0.24)
        garden7(p, gy, 98, fort_x=0.55, fort_s=1.2)
        J(p, p.X(0.42), p.Y(0.04), 1.2, pose="sniff", mood="happy")
        snow_spray(p.X(0.42) - 8, p.Y(0.08), 1.2, seed=9)
        betka(p.X(0.88), p.Y(0.03), 1.3, flip=True, mood="surprised", right="up", look=(-1, 0))
        A(p.X(0.1), p.Y(0.03), 1.2, mood="worried", look=(1, 0))
        kb(p.X(0.25), p.Y(0.06))
        sfx(p.X(0.3), p.Y(0.85), "HRAB HRAB!", 15, -5)
        say(p, "Joey! Zbouráš ji!", *hd_h("betka", p.X(0.88), p.Y(0.03), 1.3), w=110, area=(0.65, 1.0))
    with Pn(*R[1]) as p:
        winter_garden(p, p.Y(0.3), 99, house_x=0.8, hills_=False)
        deda(p.X(0.4), p.Y(0.03), 1.05, mood="happy", right="front", look=(1, -0.3))
        J(p, p.X(0.62), p.Y(0.03), 0.95, mood="sad")
        say(p, "Dneska zůstaneš v předsíni, kamaráde.", *hd("deda", p.X(0.4), p.Y(0.03), 1.05), w=150)
    with Pn(*R[2]) as p:
        fy = hallway(p)
        dog_bed(p.X(0.5), fy, 1.4)
        joey(p.X(0.5), fy + 4, 0.95, mood="sad")
        jc(p, "Psi mají nejlepší nos. Ale žádná slova.", w=180)
    with Pn(*R[3]) as p:
        fy = hallway(p)
        shape([(p.X(0.82), fy), (p.X(0.98), fy), (p.X(0.98), p.Y(0.92)), (p.X(0.82), p.Y(0.92))], P.DOOR_FRAME, BG)
        Hk(p.X(0.2), fy, 1.2, hat=False, mood="sad", right="hug", look=(1, 0))
        A(p.X(0.42), fy, 1.2, hat=False, flip=True, mood="sad", look=(-1, 0))
        say(p, "Mně je Joeyho líto.", *hd("hanka", p.X(0.2), fy, 1.2), w=110, area=(0.0, 0.4))
        say(p, "Mně taky.", *hd("alica", p.X(0.42), fy, 1.2), w=90, area=(0.35, 0.8))
    page_end()


# =================================================================== 18 Hanka understands
def page_hanka():
    R = rows([(270, [1]), (230, [0.5, 0.5]), (250, [1])])
    with Pn(*R[0]) as p:
        fy = hallway(p)
        wx, wy = kids_room_window(p)
        dog_bed(p.X(0.4), fy, 1.4)
        joey(p.X(0.4), fy + 4, 1.0, mood="sad")
        keep_clear(p, p.X(0.4) + 18, fy + 40, p.X(0.4) + 42, fy + 66, "joey")
        Hk(p.X(0.18), fy, 1.25, hat=False, mood="worried", right="hug", look=(1, -0.3))
        say(p, "Joey, co mi chceš říct?", *hd("hanka", p.X(0.18), fy, 1.25), w=120, area=(0.0, 0.55))
    with Pn(*R[1]) as p:
        fy = hallway(p)
        wx, wy = kids_room_window(p)
        J(p, p.X(0.3), fy, 1.3, mood="happy")
        stroke([(p.X(0.3) + 40*1.3, fy + 52*1.3), (wx, wy)], LINE*0.8, g=0.4)
        jc(p, "Malá se dívá tam, kam já.", w=140, where="bl")
    with Pn(*R[2]) as p:
        fy = hallway(p)
        Hk(p.X(0.4), fy, 1.4, hat=False, mood="think", right="chin", look=(1, 0))
        say(p, "Já taky neumím číst. A stejně všemu rozumím.", *hd("hanka", p.X(0.4), fy, 1.4), w=150)
    with Pn(*R[3]) as p:
        kitchen(p, table=False)
        Hk(p.X(0.2), p.Y(0.03), 1.25, hat=False, mood="determined", right="up", look=(1, 0), legs="walk")
        A(p.X(0.72), p.Y(0.03), 1.2, hat=False, flip=True, mood="surprised", look=(-1, 0))
        say(p, "Joey nic nekazí! Joey hledá! Pořád u jedné kostky!", *hd("hanka", p.X(0.2), p.Y(0.03), 1.25), w=180, area=(0.0, 0.6))
        jc(p, "Malá mi rozumí!", w=130, where="br")
    page_end()


# =================================================================== 19 Alica's timeline, Bětka's blocks
def page_timeline():
    R = rows([(300, [1]), (220, [0.5, 0.5]), (230, [1])])
    with Pn(*R[0]) as p:
        bg_fill(p, 0.9)
        notebook_big(p.X(0.06), p.Y(0.06), p.w*0.88, p.h*0.88, "CO SE DĚLO S PRSTÝNKEM?",
                     ["ráno: u krmítka babičce padal", "ráno: děda odhazoval sníh", "    od krmítka na hromadu",
                      "odpoledne: z hromady jsme řezali", "    kostky na pevnost", "večer: Joey čmuchá u pevnosti"])
        kb(p.X(0.9), p.Y(0.1))
    with Pn(*R[1]) as p:
        kitchen(p, table=False)
        deda(p.X(0.4), p.Y(0.03), 1.05, mood="think", right="chin", look=(1, 0))
        say(p, "Házel jsem sníh od krmítka. Rovnou na hromadu.", *hd("deda", p.X(0.4), p.Y(0.03), 1.05), w=150)
    with Pn(*R[2]) as p:
        kitchen(p, table=False)
        betka(p.X(0.4), p.Y(0.03), 1.4, hat=False, mood="wow", right="point", look=(1, 0))
        say(p, "Kostky od krmítka jsem dala dolů, na levou stranu!", *hd("betka", p.X(0.4), p.Y(0.03), 1.4), w=160)
    with Pn(*R[3]) as p:
        kitchen(p, table=False)
        A(p.X(0.15), p.Y(0.03), 1.25, hat=False, mood="determined", right="up", look=(1, 0))
        Hk(p.X(0.85), p.Y(0.03), 1.15, hat=False, flip=True, mood="grin", right="up", look=(-1, 0))
        say(p, "Prstýnek je v pevnosti! Joey to celou dobu věděl!", *hd("alica", p.X(0.15), p.Y(0.03), 1.25), w=190,
            area=(0.0, 0.62))
        say(p, "Pusťte Joeyho!", *hd("hanka", p.X(0.85), p.Y(0.03), 1.15), w=100, area=(0.62, 1.0))
    page_end()


# =================================================================== 20 taking the fort apart
TOPS = {(3, c) for c in range(8)} | {(4, c) for c in range(0, 7, 2)}


def page_apart():
    R = rows([(280, [1]), (230, [0.5, 0.5]), (240, [1])])
    with Pn(*R[0]) as p:
        gy = p.Y(0.22)
        garden7(p, gy, 100, fort_x=0.55, fort_s=1.3, removed=TOPS)
        for k in range(4): snow_block(p.X(0.05) + k*30, p.Y(0.03), 26, 16)
        A(p.X(0.92), p.Y(0.03), 1.15, flip=True, mood="whisper", right="front", look=(-1, 0))
        Td(p.X(0.24), p.Y(0.03), 1.1, mood="happy", right="front", look=(1, 0), item=lambda x, y: snow_block(x - 12, y - 6, 24, 14))
        say(p, "Opatrně. Kostku po kostce.", *hd_h("alica", p.X(0.92), p.Y(0.03), 1.15), w=130, area=(0.55, 1.0), whisper=True)
    with Pn(*R[1]) as p:
        gy = p.Y(0.1)
        c = snow_fort(p.X(0.68), gy, 1.15, removed=TOPS, flag=False)
        rx, ry = c[RING_BLOCK]
        J(p, p.X(0.12), p.y + 6, 1.2, pose="sniff", mood="happy")
        smell_trail([(rx, ry), (rx - 22, ry + 6), (p.X(0.12) + 46*1.2, p.y + 6 + 22*1.2)], 1.0, every=30)
        jc(p, "Tahle!", w=80)
    with Pn(*R[2]) as p:
        bg_fill(p, P.SNOW_SKY)
        fill([(p.x - 5, p.y - 5), (p.x + p.w + 5, p.y - 5), (p.x + p.w + 5, p.Y(0.25)), (p.x - 5, p.Y(0.25))], P.SNOW)
        betka(p.X(0.4), p.Y(0.03), 1.45, mood="determined", right="front", look=(1, -0.3),
              item=lambda x, y: snow_block(x - 16, y - 10, 32, 20, crack=True))
        say(p, "Je nějaká těžší!", *hd_h("betka", p.X(0.4), p.Y(0.03), 1.45), w=110)
    with Pn(*R[3]) as p:
        bg_fill(p, P.SNOW_SKY)
        fill([(p.x - 5, p.y - 5), (p.x + p.w + 5, p.y - 5), (p.x + p.w + 5, p.Y(0.35)), (p.x - 5, p.Y(0.35))], P.SNOW)
        bx, by = p.X(0.5), p.Y(0.12)
        for sx, a in ((-1, 12), (1, -12)):
            with T(bx + sx*34, by, 1.0, rot=a):
                shape([(-30, 0), (30, 0), (30, 36), (-30, 36)], P.SNOW, LINE)
        ring(bx, by + 30, 2.2)
        sfx(p.X(0.1), p.Y(0.8), "KŘUP!", 18, -6)
        Hk(p.X(0.88), p.Y(0.03), 1.2, flip=True, mood="wow", right="point", look=(-1, -0.3))
        say(p, "Prstýnek!", *hd_h("hanka", p.X(0.88), p.Y(0.03), 1.2), w=100, area=(0.6, 1.0))
    page_end()


# =================================================================== 21 found
def page_found():
    R = rows([(280, [1]), (220, [0.5, 0.5]), (250, [1])])
    with Pn(*R[0]) as p:
        gy = p.Y(0.3)
        garden7(p, gy, 101, house_x=0.1, fort_x=0.85, fort_s=0.7, removed=TOPS)
        babicka(p.X(0.45), p.Y(0.03), 1.15, mood="happy", right="hug", look=(1, -0.3))
        J(p, p.X(0.6), p.Y(0.03), 1.1, flip=True, mood="happy")
        kb(p.X(0.3), p.Y(0.08))
        say(p, "Joey má nejlepší nos ze všech!", *hd("babi", p.X(0.45), p.Y(0.03), 1.15), w=150, area=(0.15, 0.7))
    with Pn(*R[1]) as p:
        bg_fill(p, 0.9)
        ring_big(p.X(0.5), p.Y(0.5), 2.4)
        jc(p, "Tak tohle je prstýnek. Jíst se nedá.", w=170, where="bl")
    with Pn(*R[2]) as p:
        winter_garden(p, p.Y(0.3), 102, hills_=False)
        deda(p.X(0.3), p.Y(0.03), 1.05, mood="grin", right="front", look=(1, 0))
        babicka(p.X(0.72), p.Y(0.03), 1.05, flip=True, mood="happy", look=(-1, 0))
        say(p, "V zimě ho nos na řetízku. Ať nepadá.", *hd("deda", p.X(0.3), p.Y(0.03), 1.05), w=140, area=(0.0, 0.6))
    with Pn(*R[3]) as p:
        kitchen(p, table=False)
        A(p.X(0.18), p.Y(0.03), 1.2, hat=False, mood="grin", right="front", look=(1, -0.3), item=lambda x, y: notebook(x, y - 4, 0.9))
        J(p, p.X(0.5), p.Y(0.03), 1.1, mood="happy")
        say(p, "Detektiv se řídí stopami. I psími.", *hd("alica", p.X(0.18), p.Y(0.03), 1.2), w=150, area=(0.0, 0.5))
        jc(p, "Případ vyřešil: Joey.", w=150, where="br")
    page_end()


# =================================================================== 22 Joey's reward
def page_reward():
    R = rows([(280, [1]), (220, [0.5, 0.5]), (250, [1])])
    with Pn(*R[0]) as p:
        kitchen(p, evening=True)
        J(p, p.X(0.5), p.Y(0.03), 1.4, mood="happy")
        sausage(p.X(0.5) + 62, p.Y(0.03) + 52, 1.3, rot=10)
        Td(p.X(0.82), p.Y(0.03), 1.15, hat=False, flip=True, mood="grin", right="front", look=(-1, 0))
        Hk(p.X(0.15), p.Y(0.03), 1.15, hat=False, mood="grin", right="up", look=(1, 0))
        say(p, "Buřtík pro hrdinu!", *hd("tonda", p.X(0.82), p.Y(0.03), 1.15), w=110, area=(0.6, 1.0))
    with Pn(*R[1]) as p:
        gy = p.Y(0.24)
        garden7(p, gy, 103, fort_x=0.5, fort_s=0.95)
        J(p, p.X(0.5), gy - 6 + 4*16*0.95 + 13, 0.6, mood="happy")
        sfx(p.X(0.06), p.Y(0.85), "HAF!", 15, -6)
    with Pn(*R[2]) as p:
        winter_garden(p, p.Y(0.3), 104, hills_=False)
        betka(p.X(0.4), p.Y(0.03), 1.4, mood="grin", right="up", look=(1, 0))
        say(p, "Pevnost je zase celá. A Joey ji hlídá!", *hd_h("betka", p.X(0.4), p.Y(0.03), 1.4), w=150)
    with Pn(*R[3]) as p:
        fy = bedroom_night(p)
        dog_bed(p.X(0.3), fy, 1.5)
        joey(p.X(0.3), fy + 4, 1.0, mood="sleepy")
        keep_clear(p, p.X(0.3) + 18, fy + 40, p.X(0.3) + 42, fy + 66, "joey")
        jc(p, "Teď už mi Velká a Malá rozumějí. Malá hned. Velká potřebovala zápisník. Dobrou noc.", w=230, where="tr")
    page_end()


# =================================================================== 23 activity
def page_quiz():
    with Pn(M, 40, W-2*M, H-80) as p:
        box = [(p.X(0.05), p.Y(0.905)), (p.X(0.95), p.Y(0.91)), (p.X(0.95), p.Y(0.905)+54), (p.X(0.05), p.Y(0.905)+52)]
        fill(box, 0.92)
        for a_, b_ in ((0, 1), (1, 2), (2, 3), (3, 0)): stroke([box[a_], box[b_]], 1.5)
        hand_text(p.X(0.05), p.Y(0.905)+18, p.w*0.9, "Detektivní zápisník", "SHB", 26)
        hand_text(p.X(0.05), p.Y(0.84), p.w*0.9, "Která vůně vede k prstýnku?", "SHB", 15)
        # three tangled smell lines from three noses to three things; line 2 ends at the ring
        y0, y1 = p.Y(0.8), p.Y(0.58)
        starts = [p.X(0.15), p.X(0.5), p.X(0.85)]
        ends = {0: (p.X(0.5), "bone"), 1: (p.X(0.85), "ring"), 2: (p.X(0.15), "sausage")}
        for i, sx in enumerate(starts):
            ex, what = ends[i]
            mid = (sx + ex)/2
            smell_trail([(sx, y0 - 14), (sx + (12 if i % 2 else -12), y0 - 50), (mid + (30 if i == 1 else -30), (y0 + y1)/2),
                         (ex + (-10 if i == 0 else 10), y1 + 40), (ex, y1 + 16)], 1.0, every=90, seed=i)
            paw_print(sx, y0 - 6, 1.6, 0, g=0.2)
            hand_text(sx - 20, y0 + 4, 40, str(i + 1), "SHB", 14)
        for ex, what in ends.values():
            if what == "bone": bone(ex, y1 + 4, 1.4)
            elif what == "ring": ring(ex, y1 + 4, 1.5)
            else: sausage(ex, y1 + 4, 1.4)
        y = p.Y(0.5)
        qs = ["1. Proč babičce padal prstýnek?", "2. Co všechno měl Joey ve skrýši?",
              "3. Čeho se straky spíš bojí?", "4. Co znamená, když Joey dá tlapku na koleno?"]
        for q in qs:
            hand_text(p.X(0.06), y, p.w*0.9, q, "SH", 15, align="left")
            stroke([(p.X(0.06), y - 24), (p.X(0.94), y - 24)], 0.5, g=0.5)
            y -= 50
        y -= 20
        hidden_bone(p.X(0.09), y - 6, 13)        # the legend: not one of the hidden ten
        hand_text(p.X(0.14), y - 4, p.w*0.82,
                  f"Joey schoval v sešitě {N_HIDDEN} kostiček, jako je tahle (ta se nepočítá). Najdeš je všechny?",
                  "SHB", 14, align="left", lead=18)
        pages = ", ".join(map(str, HID[:-1])) + " a " + str(HID[-1]) if HID else ""
        with T(p.X(0.5), p.Y(0.015), 1.0, rot=180):
            hand_text(-p.w*0.45, 0, p.w*0.9, f"Kostičky jsou na stranách {pages}.", "SH", 10)
            hand_text(-p.w*0.45, -13, p.w*0.9, "K prstýnku vede vůně číslo 2.", "SH", 10)
    page_end()


# =================================================================== 24 back cover: next time
def back_cover():
    with Pn(M, 40, W-2*M, H-80, bg=0.95) as p:
        hand_text(p.X(0.1), p.Y(0.93), p.w*0.8, "Příště v sešitě č. 8:", "SHB", 20)
        title(p.X(0.5), p.Y(0.84), "STOPY VE SNĚHU", 34)
        with Pn(p.X(0.08), p.Y(0.3), p.w*0.84, p.h*0.48, bg=0.9) as q:
            winter_garden(q, q.Y(0.3), 105, trees=((0.75, 1.4), (0.92, 1.2)))
            for i in range(6): paw_print(q.X(0.15) + i*q.w*0.08, q.Y(0.12) + (i % 2)*8, 1.4, -80, g=0.35)
            for i in range(5): bird_print(q.X(0.2) + i*q.w*0.07, q.Y(0.22) + (i % 2)*5, 1.8, 10, g=0.35)
            hajny(q.X(0.62), q.Y(0.03), 1.0, flip=True, mood="happy", right="point", look=(-1, -0.4))
            J(q, q.X(0.12), q.Y(0.03), 1.0, pose="sniff", mood="happy")
            say(q, "Kdo tu chodil v noci? To vám povědí stopy.", *hd("hajny", q.X(0.62), q.Y(0.03), 1.0, up=2.0), w=170,
                area=(0.3, 1.0))
        hand_text(p.X(0.1), p.Y(0.24), p.w*0.8, "Pan hajný učí Klub Hvězdička číst stopy.", "SH", 16, lead=21)
        hand_text(p.X(0.1), p.Y(0.17), p.w*0.8, "A Joey už to umí.", "SHB", 16)
        hand_text(p.X(0.1), p.Y(0.015), p.w*0.8, "Velká a malá detektivka – sešit č. 7", "SH", 13, g=0.35)
    PAGE[0] += 1; cv.showPage()


cover(); page_cast(); page_hello(); page_feeder(); page_stash(); page_shovel(); page_fort(); page_gone()
page_search(); page_glove(); page_dig(); page_magpie(); page_hajny(); page_board(); page_stop(); page_try()
page_inside(); page_hanka(); page_timeline(); page_apart(); page_found(); page_reward(); page_quiz()
back_cover()
cv.save()
print("ok", PAGE[0] - 1, "pages")
import letter
if letter.MISSING: PROBLEMS.append("no glyph in the font for: " + " ".join(sorted(letter.MISSING)))
if len(HID) != N_HIDDEN: PROBLEMS.append(f"{len(HID)} hidden bones drawn, the notebook promises {N_HIDDEN}")
for pr in PROBLEMS: print("ORDER/LAYOUT:", pr)
if PROBLEMS: sys.exit(1)
