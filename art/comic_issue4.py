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
                   owlet, owl_box, old_photo, map_half, ladder)
from pond import *
from village import *
from letter import Panel, caption, bubble, sfx, title, series_title, hand_text, lines_of, thought

W, H = A4
M = 28; GUT = 9; TOP = H - 30
OUT = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                   "comics", "velka_a_mala_detektivka", "04_hanka_to_vyresi.pdf")
os.makedirs(os.path.dirname(OUT), exist_ok=True)
cv = canvas.Canvas(OUT, pagesize=A4); lib.set_canvas(cv)
cv.setTitle("Velká a malá detektivka – Případ č. 4: Hanka to vyřeší!")
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



# =================================================================== 1 COVER
def cover():
    with Pn(M, 40, W-2*M, H-80) as p:
        gy = p.Y(0.42)
        sky(p, P.NOV_SKY)
        hills(p, gy + 40, 18, 0.87, 4)
        far_trees(p, gy + 18, 7)
        church(p.X(0.82), gy + 4, 1.2)
        boot_rock(p.X(0.36), gy + 8, 0.3)
        ground(p, gy + 8, P.GRASS)
        falling_leaves(p, 5, 3, 0.2)
        tufts(p, p.Y(0.02), p.Y(0.3), 10, 5)
        picture_letter(p.X(0.72), p.Y(0.04), 1.5, rot=8)
        hanka(p.X(0.52), p.Y(0.03), 2.8, mood="determined", torch=True, right="lens", look=(1, 0.3))
        joey(p.X(0.25), p.Y(0.03), 1.9, pose="sniff", mood="happy")
        cx, cy, r = p.X(0.22), p.Y(0.6), 82
        C.saveState(); C.clipPath(poly(ell(cx, cy, r, r, 60)), stroke=0, fill=0)
        fill(ell(cx, cy, r, r, 60), P.BEDROOM_WALL)
        shape(ell(cx + 40, cy - 30, 34, 16, 30), P.PILLOW, BG)
        alica(cx + 6, cy - 150, 1.9, mood="grin", right="cheek", look=(1, 0), shadow=False)
        vysilacka(cx + 20, cy - 8, 1.4, rot=-12)
        fill([(cx - r, cy - r), (cx + r, cy - r), (cx + r, cy - 40), (cx - r, cy - 48)], P.BLANKET)
        stroke([(cx - r, cy - 48), (cx + r, cy - 40)], BG*1.2)
        C.restoreState()
        stroke(ell(cx, cy, r, r, 60), 2.2, closed=True)
        for k_ in range(3):
            stroke(ell(cx + r*0.7, cy - r*0.7, r*(0.35 + k_*0.12), r*(0.35 + k_*0.12), 20, 280, 350), 1.0, g=0.3)
    box = [(M+34, H-236), (W-M-30, H-232), (W-M-34, H-48), (M+30, H-52)]
    fill([(x+3, y-3) for x, y in box], 0.0, 0.25); fill(box, 1.0)
    for a_, b_ in ((0, 1), (1, 2), (2, 3), (3, 0)): stroke([box[a_], box[b_]], 1.8)
    series_title(W/2, H-98, H-160, 40, 66)
    hand_text(M+40, H-190, W-2*M-80, "Alica a Hanka", "SHB", 20)
    hand_text(M+40, H-217, W-2*M-80, "Případ č. 4: Hanka to vyřeší!", "SH", 15)
    magnifier(M+82, H-120, ang=-30, r=17)
    heart(W-M-100, H-118, 16)
    page_end()


# =================================================================== 2 WHO IS WHO
def page_cast():
    with Pn(M, 40, W-2*M, H-80) as p:
        hand_text(p.X(0.05), p.Y(0.95), p.w*0.9, "Kdo je kdo", "SHB", 30)
        cells = [
            ("Alica", "je nemocná, ale přemýšlí", lambda x, y: alica(x, y, 0.9, mood="sleepy", right="lens", lens=True)),
            ("Hanka", "umí číst obrázky", lambda x, y: hanka(x, y, 1.1, mood="grin", torch=True, right="lens")),
            ("Joey", "má nejlepší nos", lambda x, y: joey(x, y, 1.2, mood="happy")),
            ("Babička", "jde s Hankou", lambda x, y: babicka(x, y, 0.82, mood="happy")),
            ("Děda Honza", "založil Klub Hvězdička", lambda x, y: deda(x, y, 0.74, mood="happy")),
            ("Tonda", "soused a člen klubu", lambda x, y: tonda(x, y, 0.88, mood="grin")),
            ("Věrka", "bydlí u mlýna", lambda x, y: verka_old(x, y, 0.8, mood="happy")),
            ("Kostelník", "hlídá kostel", lambda x, y: kostelnik(x, y, 0.75, mood="happy")),
            ("Rybář", "chodí na ryby odpoledne", lambda x, y: rybar(x, y, 0.7, mood="happy", right="hold")),
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
        hand_text(p.x + 20, by + bh - 28, p.w*0.55, "Minule…", "SHB", 17, align="left")
        hand_text(p.x + 20, by + bh - 52, p.w*0.55,
                  "V plechovce Klubu Hvězdička byl Frantův obrázkový dopis. Franta byl nejmenší z klubu a psát ještě neuměl.",
                  "SH", 13, align="left", lead=17)
        picture_letter(p.X(0.66), by + 18, 1.55, rot=-4)
    page_end()


# =================================================================== 3 Alica is ill
def page_sick():
    R = rows([(230, [1]), (250, [0.5, 0.5]), (270, [0.55, 0.45])])
    with Pn(*R[0]) as p:
        sickroom(p)
        ax, ay = alica_in_bed(p.X(0.55), p.X(0.92), p.y + 48, 1.4, mood="sad", right="front", look=(-1, 0),
                              item=lambda x, y: mug(x + 4, y - 4, 0.8))
        babicka(p.X(0.34), p.y + 14, 1.15, mood="worried", right="front", look=(1, 0))
        cap(p, "Venku je listopad. Alica má horečku.", w=210)
        say(p, "Dneska zůstaneš v posteli, Alico.", *hd("babi", p.X(0.34), p.y + 14, 1.15), w=160)
        say(p, "Ale my máme případ!", *hd("alica", ax, ay, 1.4), w=130)
    with Pn(*R[1]) as p:
        bg_fill(p, P.BLANKET)
        for xx in range(int(p.x), int(p.x + p.w) + 16, 16):
            for yy in range(int(p.y), int(p.y + p.h) + 16, 16):
                dot(xx + ((yy//16) % 2)*8, yy, 1.8, P.BLANKET_DOT)
        picture_letter(p.X(0.14), p.Y(0.1), 2.3, rot=-3)
        keep_clear(p, p.X(0.12), p.Y(0.08), p.X(0.14) + 215, p.Y(0.1) + 150, "letter")
        say(p, "Frantův dopis. Nejsou tam žádná písmena!", p.X(0.5), p.Y(0.72), w=200)
    with Pn(*R[2]) as p:
        sickroom(p, window=False)
        alica_in_bed(p.x - 10, p.X(0.46), p.y + 48, 1.3, mood="surprised", look=(1, 0))
        hanka(p.X(0.72), p.y + 14, 1.3, flip=True, mood="grin", right="point", look=(1, 0))
        say(p, "To je slepička! A hodiny. A bota. A hvězdička.", *hd("hanka", p.X(0.72), p.y + 14, 1.3), w=170)
    with Pn(*R[3]) as p:
        sickroom(p, window=False)
        ax, ay = alica_in_bed(p.x - 20, p.X(0.4), p.y + 48, 1.3, mood="grin", right="front", look=(1, 0),
                              item=lambda x, y: vysilacka(x + 2, y - 6, 1.1, rot=-20))
        hanka(p.X(0.82), p.y + 14, 1.2, flip=True, mood="wow", right="up", look=(1, 0.3))
        say(p, "Dneska jsi detektiv ty, Hanko. Tady máš vysílačku. Co najdeš, to mi nakresli!", *hd("alica", ax, ay, 1.3), w=215,
            area=(0.0, 0.75))
        say(p, "Jasně!", *hd("hanka", p.X(0.82), p.y + 14, 1.2), w=80)
    with Pn(*R[4]) as p:
        autumn(p, p.Y(0.2), 3, trees=((0.85, 0.9),))
        babicka(p.X(0.24), p.Y(0.03), 1.2, mood="happy", right="point", look=(1, 0))
        hanka(p.X(0.55), p.Y(0.03), 1.2, flip=True, mood="determined", right="up", look=(1, 0.3),
              item=lambda x, y: vysilacka(x - 3, y - 4, 0.9))
        joey(p.X(0.8), p.Y(0.03), 0.9, flip=True, mood="happy")
        say(p, "Půjdu s tebou. Ale vedeš ty.", *hd("babi", p.X(0.24), p.Y(0.03), 1.2), w=150)
    page_end()


# =================================================================== 4 the letter up close
def page_letter():
    R = rows([(360, [1]), (190, [1]), (200, [1])])
    with Pn(*R[0]) as p:
        bg_fill(p, P.TABLE)
        for k_ in range(1, 6): stroke([(p.x, p.Y(k_/6)), (p.x + p.w, p.Y(k_/6))], BG*0.6)
        picture_letter(p.X(0.14), p.Y(0.05), 4.0, rot=-2)
        keep_clear(p, p.X(0.12), p.Y(0.03), p.X(0.14) + 372, p.Y(0.05) + 262, "letter")
        cap(p, "Frantův obrázkový dopis. Co v něm vidíš?", w=250)
    with Pn(*R[1]) as p:
        kitchen(p, table=False)
        deda(p.X(0.25), p.Y(0.03), 1.1, mood="grin", right="point", look=(1, 0))
        babicka(p.X(0.75), p.Y(0.03), 1.15, flip=True, mood="happy", look=(1, 0))
        say(p, "Slepice? To bude přece náš kurník!", *hd("deda", p.X(0.25), p.Y(0.03), 1.1), w=190)
        say(p, "A kostel s hodinami je ve vsi jen jeden.", *hd("babi", p.X(0.75), p.Y(0.03), 1.15), w=180)
    with Pn(*R[2]) as p:
        autumn(p, p.Y(0.22), 5, house_x=0.12, house_s=0.9, trees=((0.9, 1.0),))
        joey(p.X(0.62), p.Y(0.04), 1.3, pose="sniff", mood="happy")
        hanka(p.X(0.36), p.Y(0.03), 1.3, mood="grin", right="point", legs="walk", look=(1, 0),
              bunny_toy=False)
        hidden_heart(p.X(0.82), p.Y(0.1))
        sfx(p.X(0.72), p.Y(0.62), "ČMUCH ČMUCH!", 16, -6)
        say(p, "Joey už ví, kam jít! Jdeme!", *hd("hanka", p.X(0.36), p.Y(0.03), 1.3), w=170)
    page_end()


# =================================================================== 5 the henhouse
def page_henhouse():
    R = rows([(250, [1]), (245, [0.5, 0.5]), (255, [1])])
    with Pn(*R[0]) as p:
        autumn(p, p.Y(0.2), 7, trees=((0.08, 0.9),))
        henhouse(p.X(0.62), p.Y(0.17), 1.3)
        for hx, fl, ps, g in ((0.35, False, "peck", P.HEN), (0.84, True, "stand", P.HEN_WHITE), (0.93, True, "peck", P.HEN)):
            hen(p.X(hx), p.Y(0.06), 1.1, flip=fl, pose=ps, g=g)
        hanka(p.X(0.2), p.Y(0.03), 1.2, mood="think", look=(1, 0))
        babicka(p.X(0.47), p.Y(0.03), 1.1, mood="happy", right="front", look=(1, 0))
        cap(p, "Babiččin kurník.", w=150)
        say(p, "Tady nic není. Jen slepičky.", *hd("hanka", p.X(0.2), p.Y(0.03), 1.2), w=140)
        say(p, "A vajíčka.", *hd("babi", p.X(0.47), p.Y(0.03), 1.1), w=100)
    with Pn(*R[1]) as p:
        autumn(p, p.Y(0.2), 8, leaves=False)
        shed(p.X(0.78), p.Y(0.18), 0.8)
        joey(p.X(0.55), p.Y(0.04), 1.2, pose="sniff", mood="happy")
        hanka(p.X(0.2), p.Y(0.03), 1.2, mood="surprised", legs="walk", look=(1, 0))
        say(p, "Joey, kam jdeš?", *hd("hanka", p.X(0.2), p.Y(0.03), 1.2), w=120)
    with Pn(*R[2]) as p:
        autumn(p, p.Y(0.2), 9, leaves=False)
        old_henhouse(p.X(0.62), p.Y(0.1), 1.9)
        babicka(p.X(0.18), p.Y(0.03), 1.1, mood="surprised", right="point", look=(1, 0))
        say(p, "Starý kurník! Tam už léta nikdo nechodí.", *hd("babi", p.X(0.18), p.Y(0.03), 1.1), w=160)
    with Pn(*R[3]) as p:
        autumn(p, p.Y(0.2), 10, leaves=False)
        old_henhouse(p.X(0.72), p.Y(0.06), 3.0)
        babicka(p.X(0.18), p.Y(0.03), 1.2, mood="worried", right="front", look=(1, -0.3))
        hanka(p.X(0.43), p.Y(0.03), 1.25, mood="determined", torch=True, right="lens", look=(1, 0))
        say(p, "Tam se nevejdu. Jsem moc velká.", *hd("babi", p.X(0.18), p.Y(0.03), 1.2), w=160)
        say(p, "Já jo! Jsem malá.", *hd("hanka", p.X(0.43), p.Y(0.03), 1.25), w=130)
    page_end()


# =================================================================== 6 inside
def plank_scratch(x, y, s=1.0):
    """a hen, a star and an F scratched into a beam"""
    with T(x, y, s):
        letter_hen(0, 0, LINE*0.9, 0.2)
        star(26, 2, 7, 1.0, w=LINE*0.9)
        stroke([(40, -8), (40, 10), (50, 10)], LINE*1.1); stroke([(40, 1), (47, 1)], LINE*1.1)


def page_inside():
    R = rows([(255, [1]), (245, [0.5, 0.5]), (255, [1])])
    with Pn(*R[0]) as p:
        bg_fill(p, 0.14)
        for k_ in range(6): stroke([(p.X(k_/6 + 0.05), p.y), (p.X(k_/6 + 0.03), p.y + p.h)], BG, g=0.3)
        shape([(p.x - 5, p.Y(0.62)), (p.x + p.w + 5, p.Y(0.6)), (p.x + p.w + 5, p.Y(0.72)), (p.x - 5, p.Y(0.74))], 0.3, BG)
        hx, hy = p.X(0.14), p.Y(0.03)
        torch_beam(hx + 26, hy + 56, p.X(0.5), p.Y(0.98), p.X(0.88), p.Y(0.5), 0.5)
        plank_scratch(p.X(0.58), p.Y(0.67), 1.3)
        hanka(hx, hy, 1.4, mood="wow", torch=True, right="lens", look=(1, 0.5))
        say(p, "Slepička! Úplně stejná jako v dopise!", *hd("hanka", hx, hy, 1.4), w=200, area=(0.0, 0.5))
    with Pn(*R[1]) as p:
        planks(p, P.HENHOUSE_OLD, 22, 5, knots=True)
        torch_beam(p.x, p.Y(0.2), p.X(1.1), p.Y(0.95), p.X(1.1), p.y - 10, 0.45)
        plank_scratch(p.X(0.25), p.Y(0.35), 2.2)
        babicka(p.X(0.9), head_y(p, 0.4, 101.2, 1.6), 1.6, flip=True, mood="surprised", look=(1, 0), shadow=False)
        say(p, "Písmenko F. Jako Franta!", *hd("babi", p.X(0.9), head_y(p, 0.4, 101.2, 1.6), 1.6), w=140, area=(0.0, 0.7))
    with Pn(*R[2]) as p:
        bg_fill(p, P.GRASS)
        mud_patch(p.X(0.5), p.Y(0.12), p.w*0.6, 30)
        zig_print(p.X(0.55), p.Y(0.2), 2.3, 70)
        hanka(p.X(0.16), p.Y(0.03), 1.3, mood="wow", right="point", look=(1, -1))
        say(p, "Tady je obří bota!", *hd("hanka", p.X(0.16), p.Y(0.03), 1.3), w=130)
    with Pn(*R[3]) as p:
        autumn(p, p.Y(0.24), 11, leaves=False)
        old_henhouse(p.X(0.85), p.Y(0.2), 1.3)
        hanka_drawing(p.X(0.28), p.Y(0.05), 90, 62, "print", rot=4)
        hanka(p.X(0.16), p.Y(0.03), 1.2, mood="determined", right="front", look=(1, -1))
        babicka(p.X(0.62), p.Y(0.03), 1.2, flip=True, mood="think", right="chin", look=(1, -0.3))
        hidden_heart(p.X(0.94), p.Y(0.08))
        say(p, "Nakreslím to Alice.", *hd("hanka", p.X(0.16), p.Y(0.03), 1.2), w=130)
        say(p, "Tak velké boty nemá nikdo z nás.", *hd("babi", p.X(0.62), p.Y(0.03), 1.2), w=160)
    page_end()


# =================================================================== 7 report no. 1
def page_report1():
    R = rows([(230, [1]), (265, [1]), (255, [0.5, 0.5])])
    with Pn(*R[0]) as p:
        sickroom(p)
        ax, ay = alica_in_bed(p.X(0.3), p.X(0.62), p.y + 48, 1.4, mood="happy", right="front", look=(1, 0))
        hanka(p.X(0.82), p.y + 14, 1.3, flip=True, mood="grin", right="front", look=(1, 0),
              item=lambda x, y: hanka_drawing(x - 36, y - 20, 44, 31, "print", rot=-6))
        cap(p, "Hlášení číslo 1.", w=150)
        say(p, "Ukaž!", *hd("alica", ax, ay, 1.4), w=80, area=(0.3, 0.7))
        say(p, "Nakreslila jsem ti to!", *hd("hanka", p.X(0.82), p.y + 14, 1.3), w=140, area=(0.55, 1.0))
    with Pn(*R[1]) as p:
        bg_fill(p, P.BLANKET)
        hanka_drawing(p.X(0.1), p.Y(0.1), p.w*0.5, p.h*0.78, "print", rot=-3)
        alica(p.X(0.82), head_y(p, 0.52, 89.8, 2.2), 2.2, mood="wow", right="lens", lens=True, look=(-1, -0.5), shadow=False)
        say(p, "Velká bota s podrážkou cik-cak.", p.X(0.78), p.Y(0.9), w=170, area=(0.6, 1.0))
    with Pn(*R[2]) as p:
        sickroom(p, window=False)
        ax, ay = alica_in_bed(p.x - 20, p.X(0.5), p.y + 48, 1.3, mood="think", right="chin", look=(1, 0.3))
        hanka(p.X(0.84), p.y + 14, 1.1, flip=True, mood="happy", look=(1, 0))
        say(p, "V noci pršelo a ta stopa je ostrá. Takže je z dneška!", *hd("alica", ax, ay, 1.3), w=200)
    with Pn(*R[3]) as p:
        bg_fill(p, 0.9)
        notebook_big(p.X(0.07), p.Y(0.3), p.w*0.86, p.h*0.62, "PŘÍPAD Č. 4:", ["1. slepička: starý kurník", "   obří bota cik-cak!", "2. hodiny: ?"])
        say(p, "Někdo jde po stopě před námi!", p.X(0.5), p.Y(0.24), w=180, x=p.X(0.2), y=p.Y(0.26))
    page_end()


# =================================================================== 8 the church
def page_church():
    R = rows([(300, [1]), (230, [0.5, 0.5]), (220, [1])])
    with Pn(*R[0]) as p:
        village(p, p.Y(0.2), 0.7, 1.1, houses=((0.12, 0.8), (0.38, 0.7)), seed=2)
        hanka(p.X(0.1), p.Y(0.03), 1.2, mood="wow", right="point", look=(1, 1))
        babicka(p.X(0.26), p.Y(0.03), 1.05, mood="happy", legs="walk", look=(1, 0.5))
        deda(p.X(0.4), p.Y(0.03), 1.0, mood="happy", legs="walk", look=(1, 0.5))
        hd("deda", p.X(0.4), p.Y(0.03), 1.0)
        joey(p.X(0.53), p.Y(0.03), 0.9, mood="happy")
        cap(p, "Druhý obrázek: kostel s hodinami.", w=230)
        say(p, "Hodiny! Stejné jako v dopise!", *hd("hanka", p.X(0.1), p.Y(0.03), 1.2), w=170, area=(0.0, 0.62))
        say(p, "Ty hodiny stojí, co pamatuju. Pořád jsou tři.", *hd("babi", p.X(0.26), p.Y(0.03), 1.05), w=190, area=(0.0, 0.62))
    with Pn(*R[1]) as p:
        village(p, p.Y(0.2), seed=3)
        deda(p.X(0.25), p.Y(0.03), 0.9, mood="grin", right="up", look=(1, 0))
        hanka(p.X(0.8), p.Y(0.03), 1.0, flip=True, mood="surprised", look=(1, 0.3))
        say(p, "Na dopise jsou tři hodiny. Tak přijdeme ve tři!", *hd("deda", p.X(0.25), p.Y(0.03), 0.9), w=175)
        say(p, "A ve tři se něco stane?", *hd("hanka", p.X(0.8), p.Y(0.03), 1.0), w=120)
    with Pn(*R[2]) as p:
        bg_fill(p, P.CHURCH_WALL)
        shape([(p.X(0.35), p.y - 5), (p.X(0.35), p.Y(0.62))] + bez((p.X(0.35), p.Y(0.62)), (p.X(0.35), p.Y(0.95)), (p.X(0.75), p.Y(0.95)), (p.X(0.75), p.Y(0.62))) +
              [(p.X(0.75), p.y - 5)], P.DOOR, BG)
        ladder(p.X(0.45), p.y, p.Y(0.7))
        kostelnik(p.X(0.62), p.Y(0.03), 1.15, flip=True, mood="determined", right="point", look=(1, 0))
        hanka(p.X(0.2), p.Y(0.03), 1.1, mood="surprised", look=(1, 0.3))
        say(p, "Dobrý den!", *hd("hanka", p.X(0.2), p.Y(0.03), 1.1), w=90, area=(0.0, 0.4))
        say(p, "Na věž nesmíte! Je tam zamčeno.", *hd("kostelnik", p.X(0.62), p.Y(0.03), 1.15), w=140, area=(0.3, 1.0))
    with Pn(*R[3]) as p:
        village(p, p.Y(0.2), 0.88, 0.7, seed=4)
        hx, hy = p.X(0.22), p.Y(0.03)
        hanka(hx, hy, 1.3, mood="whisper", right="cheek", look=(1, 0),
              item=lambda x, y: vysilacka(x - 3, y - 12, 1.0, rot=-10))
        kostelnik(p.X(0.72), p.Y(0.12), 0.8, mood="determined", right="up", look=(1, 0))
        wx, wy = hand_pt(True, "cheek", hx, hy, 1.3)
        say(p, "Tady Hanka. Pán s klíči je velký. A zlobí se.", *hd("hanka", hx, hy, 1.3), whisper=True, w=200)
        say(p, "Velký? Podezřelý číslo 1! Příjem.", wx, wy + 16, w=170)
    page_end()



# =================================================================== 9 three o'clock
def page_three():
    R = rows([(225, [1]), (255, [0.5, 0.5]), (270, [1])])
    with Pn(*R[0]) as p:
        village(p, p.Y(0.25), 0.84, 0.75, houses=((0.3, 0.6),), seed=5)
        bench(p.X(0.42), p.Y(0.04), 1.3)
        for fn, who, xx, s_k, lg, bt in ((babicka, "babi", 0.33, 1.0, P.STOCKINGS, P.BABI_SHOES),
                                         (hanka, "hanka", 0.44, 1.1, P.DUNGAREES, P.HANKA_BOOTS),
                                         (deda, "deda", 0.54, 0.95, P.TROUSERS, P.DEDA_BOOTS)):
            seated(fn, who, p.X(xx), p.Y(0.04) + 23*1.3, s_k, lg, bt, edge=5, mood="happy", look=(1, 0.5))
        joey(p.X(0.72), p.Y(0.03), 0.9, flip=True, mood="sleepy")
        cap(p, "Odpoledne. Všichni čekají, až budou tři.", w=250)
        say(p, "Už je skoro tři!", *hd("deda", p.X(0.54), p.Y(0.04) + 23*1.3 - HIPS["deda"]*0.95, 0.95), w=140)
    with Pn(*R[1]) as p:
        bg_fill(p, P.NOV_SKY)
        church(p.X(0.5), p.Y(0.02) - 60, 1.3, nave=False)
        cap(p, "Tři hodiny.", w=110)
        say(p, "Nic se neděje.", p.X(0.25), p.Y(0.3), w=120, area=(0.0, 0.5))
        say(p, "Ani zvon nezvoní.", p.X(0.8), p.Y(0.3), w=120, area=(0.5, 1.0))
    with Pn(*R[2]) as p:
        village(p, p.Y(0.22), seed=6)
        church(p.X(0.14), p.Y(0.22) - 2, 0.95, nave=False)
        rx, ry = p.X(0.66), p.Y(0.06)
        rybar(rx, ry, 0.95, flip=True, mood="grin", right="hold", look=(1, 1))
        bx = rx + 20*0.95
        shape([(bx - 5, ry + 40), (bx + 9, ry + 40), (bx + 10, ry + 54), (bx - 6, ry + 54)], P.METAL, LINE)
        stroke(bez((bx - 6, ry + 54), (bx - 3, ry + 62), (bx + 7, ry + 62), (bx + 10, ry + 54)), LINE*0.6)
        for k_ in range(3):
            stroke([(p.X(0.84), ry + 40 + k_*14), (p.X(0.98), ry + 40 + k_*14)], 1.0, g=0.4)
        hidden_heart(p.X(0.45), p.Y(0.08))
    with Pn(*R[3]) as p:
        bg_fill(p, P.NOV_SKY)
        church(p.X(0.14), p.Y(0.72) - 108*1.9, 1.9, nave=False)
        ground(p, p.Y(0.2), P.GRASS)
        hx, hy = p.X(0.46), p.Y(0.03)
        hanka(hx, hy, 1.35, mood="determined", right="point", look=(1, 0.5))
        tonda(p.X(0.82), p.Y(0.03), 1.25, flip=True, mood="surprised", legs="walk", look=(1, 0))
        say(p, "Ručička neukazuje čas. Ukazuje TAM!", *hd("hanka", hx, hy, 1.35), w=180, area=(0.3, 0.75))
        say(p, "Co tu děláte?", *hd("tonda", p.X(0.82), p.Y(0.03), 1.25), w=110, area=(0.7, 1.0))
    page_end()


# =================================================================== 10 where the hand points
def page_brook():
    R = rows([(245, [1]), (260, [0.5, 0.5]), (245, [1])])
    with Pn(*R[0]) as p:
        countryside(p, 0.5, 3)
        church(p.X(0.05), p.Y(0.5) - 2, 0.5)
        stroke(bez((p.X(0.0), p.Y(0.08)), (p.X(0.3), p.Y(0.2)), (p.X(0.6), p.Y(0.35)), (p.X(1.0), p.Y(0.45))), 5, g=P.GRASS_TRAIL)
        joey(p.X(0.82), p.Y(0.05), 0.9, pose="sniff", mood="happy")
        hanka(p.X(0.66), p.Y(0.04), 1.1, mood="determined", legs="walk", look=(1, 0))
        tonda(p.X(0.5), p.Y(0.04), 1.05, mood="happy", legs="walk", look=(1, 0))
        babicka(p.X(0.34), p.Y(0.04), 1.0, mood="happy", legs="walk", look=(1, 0))
        deda(p.X(0.2), p.Y(0.04), 0.95, mood="happy", legs="walk", look=(1, 0))
        cap(p, "Jdou tam, kam ukazuje malá ručička. Tonda jde taky.", w=260)
        hidden_heart(p.X(0.93), p.Y(0.14))
    with Pn(*R[1]) as p:
        countryside(p, 0.72, 4, brook=(0.04, 0.2))
        tonda(p.X(0.55), p.Y(0.16), 1.15, mood="grin", right="up", look=(1, 0.3),
              item=lambda x, y: old_boot_prop(x - 8, y - 30, 0.8, rot=160))
        say(p, "Bota! Našel jsem botu!", *hd("tonda", p.X(0.55), p.Y(0.16), 1.15), w=150)
    with Pn(*R[2]) as p:
        countryside(p, 0.72, 5, brook=(0.04, 0.2))
        old_boot_prop(p.X(0.34), p.Y(0.24), 1.1, rot=-20)
        frog(p.X(0.55), p.Y(0.5), 1.8, jump=True)
        hanka(p.X(0.82), p.Y(0.2), 1.1, flip=True, mood="laugh", look=(1, 0))
        sfx(p.X(0.08), p.Y(0.8), "KVAK!", 24, 8)
        say(p, "To je žabí domeček!", *hd("hanka", p.X(0.82), p.Y(0.2), 1.1), w=120, area=(0.45, 1.0))
    with Pn(*R[3]) as p:
        countryside(p, 0.55, 6, dusk=True)
        for rx, rs, sd in ((0.2, 0.55, 1), (0.42, 0.7, 2), (0.66, 0.5, 3), (0.9, 0.62, 4)):
            boot_rock(p.X(rx), p.Y(0.3), rs, view="front", seed=sd)
        magpie(p.X(0.55), p.Y(0.72), 1.3, flip=True, item=lambda x, y: coin(x + 3, y, 3))
        babicka(p.X(0.12), p.Y(0.03), 1.05, mood="think", right="chin", look=(1, 0.3))
        deda(p.X(0.85), p.Y(0.03), 1.0, flip=True, mood="happy", right="point", look=(1, 0))
        say(p, "Tady je kamenů! Který je bota?", *hd("babi", p.X(0.12), p.Y(0.03), 1.05), w=150)
        say(p, "Stmívá se. Zítra budeme hledat dál.", *hd("deda", p.X(0.85), p.Y(0.03), 1.0), w=160)
    page_end()


# =================================================================== 11 the suspect board
def page_board():
    R = rows([(265, [1]), (235, [0.5, 0.5]), (250, [1])])
    with Pn(*R[0]) as p:
        sickroom(p, evening=True)
        ax, ay = alica_in_bed(p.X(0.25), p.X(0.58), p.y + 48, 1.4, mood="think", right="lens", lens=True, look=(1, 0))
        hanka(p.X(0.84), p.y + 14, 1.3, flip=True, mood="happy", right="front", look=(1, 0),
              item=lambda x, y: hanka_drawing(x - 40, y - 24, 48, 34, "tower", rot=-5))
        cap(p, "Večer. Hlášení číslo 2.", w=180)
        say(p, "Kdo je ten pán s kloboukem?", *hd("alica", ax, ay, 1.4), w=150)
        say(p, "Pan rybář. Šel kolem přesně ve tři.", *hd("hanka", p.X(0.84), p.y + 14, 1.3), w=150)
    with Pn(*R[1]) as p:
        sickroom(p, evening=True, window=False)
        ax, ay = alica_in_bed(p.x - 20, p.X(0.5), p.y + 48, 1.3, mood="determined", right="point", look=(1, 0))
        hanka(p.X(0.82), p.y + 14, 1.1, flip=True, mood="sleepy", look=(1, 0))
        say(p, "Někdo chce Frantův poklad najít dřív než my!", *hd("alica", ax, ay, 1.3), w=190)
    with Pn(*R[2]) as p:
        bg_fill(p, 0.9)
        notebook_big(p.X(0.08), p.Y(0.1), p.w*0.84, p.h*0.8, "PODEZŘELÍ:",
                     ["1. kostelník: velký,", "    má klíče", "2. straka: bere", "    lesklé věci", "3. rybář: byl u", "    kostela ve tři"])
    with Pn(*R[3]) as p:
        sickroom(p, evening=True, window=False)
        alica_in_bed(p.X(0.52), p.X(0.92), p.y + 48, 1.3, mood="sleepy", look=(1, 0))
        seated(hanka, "hanka", p.X(0.58), p.y + 48 - 10, 1.1, P.DUNGAREES, P.HANKA_BOOTS, edge=2, mood="sleepy", look=(0, 0))
        thought(p.X(0.04), p.Y(0.95), p.w*0.46, p.h*0.52, p.X(0.54), p.Y(0.5), seed=3)
        for hx, fl in ((0.1, False), (0.2, True), (0.3, False)):
            hen(p.X(hx), p.Y(0.6), 1.0, flip=fl)
        church_clock(p.X(0.4), p.Y(0.72), 12)
        cap(p, "Hanka usnula. Zdají se jí slepičky.", w=160, where="tr")
    page_end()


# =================================================================== 12 the sexton
def page_sexton():
    R = rows([(250, [1]), (250, [0.5, 0.5]), (250, [1])])
    with Pn(*R[0]) as p:
        village(p, p.Y(0.2), 0.84, 0.9, seed=7)
        babicka(p.X(0.12), p.Y(0.03), 1.0, mood="happy", look=(1, 0))
        hanka(p.X(0.25), p.Y(0.03), 1.1, mood="happy", look=(1, 0))
        hd("hanka", p.X(0.25), p.Y(0.03), 1.1)
        kostelnik(p.X(0.66), p.Y(0.03), 1.05, flip=True, mood="happy", right="front", look=(1, 0))
        cap(p, "Ráno u kostela.", w=150)
        say(p, "Dobré ráno. Proč vaše hodiny stojí?", *hd("babi", p.X(0.14), p.Y(0.03), 1.0), w=160)
        say(p, "Ztratil se klíč na natahování. Už když jsem byl kluk.", *hd("kostelnik", p.X(0.66), p.Y(0.03), 1.05), w=200)
    with Pn(*R[1]) as p:
        bg_fill(p, P.CHURCH_WALL)
        ground(p, p.Y(0.1), P.STONE_BASE)
        kx = p.X(0.72)
        C.saveState(); C.clipPath(poly([(p.x, p.y), (p.x + p.w, p.y), (p.x + p.w, p.Y(0.62)), (p.x, p.Y(0.62))]), stroke=0, fill=0)
        kostelnik(kx, p.Y(0.08), 2.1, flip=True, mood="happy", look=(1, -1))
        C.restoreState()
        lx, ly, lr = p.X(0.5), p.Y(0.2), 28
        shape(ell(lx, ly, lr, lr, 40), 1.0, 1.6)
        C.saveState(); C.clipPath(poly(ell(lx, ly, lr, lr, 40)), stroke=0, fill=0)
        with T(lx, ly, 1.0, rot=-20):
            fill(ell(0, 0, 9, 20, 30), P.GALOSHES)
            stroke(ell(0, 0, 6.5, 16, 30), 0.6, closed=True, g=0.4)
        C.restoreState()
        stroke([(lx + lr*0.7, ly - lr*0.7), (lx + lr*1.3, ly - lr*1.3)], 3.4)
        hanka(p.X(0.18), p.Y(0.03), 1.3, mood="wow", right="point", look=(1, -0.5))
        say(p, "Vaše boty jsou hladké. Žádné cik-cak!", *hd("hanka", p.X(0.18), p.Y(0.03), 1.3), w=150)
        say(p, "Hladké gumáky. Proč?", p.X(0.8), p.Y(0.66), w=120, area=(0.45, 1.0))
    with Pn(*R[2]) as p:
        village(p, p.Y(0.2), seed=8)
        hx, hy = p.X(0.22), p.Y(0.03)
        hanka(hx, hy, 1.3, mood="happy", right="cheek", look=(1, 0),
              item=lambda x, y: vysilacka(x - 3, y - 12, 1.0, rot=-10))
        wx, wy = hand_pt(True, "cheek", hx, hy, 1.3)
        say(p, "Tady Hanka. Pan kostelník to nebyl.", *hd("hanka", hx, hy, 1.3), w=160)
        say(p, "Škrtám! Příjem.", wx, wy + 16, w=110)
    with Pn(*R[3]) as p:
        village(p, p.Y(0.2), 0.9, 0.75, seed=9)
        kostelnik(p.X(0.2), p.Y(0.03), 1.05, mood="talk", right="up", look=(1, 0.5))
        hanka(p.X(0.55), p.Y(0.03), 1.1, flip=True, mood="wow", look=(1, 0.3))
        babicka(p.X(0.68), p.Y(0.03), 1.0, flip=True, mood="surprised", look=(1, 0.3))
        say(p, "Na věž lezl kdysi jen jeden kluk. Malý Franta. Pak se odstěhoval.", *hd("kostelnik", p.X(0.2), p.Y(0.03), 1.05), w=230)
        say(p, "Pojďte nahoru. Ukážu vám hodiny zevnitř.", *hd("kostelnik", p.X(0.2), p.Y(0.03), 1.05), w=190)
    page_end()


# =================================================================== 13 from the tower
def tower_view(p, seed=3):
    sky(p, P.NOV_SKY)
    hy = p.Y(0.72)
    far_trees(p, hy + 4, seed)
    fill([(p.x - 5, p.y - 5), (p.x + p.w + 5, p.y - 5), (p.x + p.w + 5, hy), (p.x - 5, hy)], P.FIELD)
    for k_, g in enumerate((P.FIELD_DARK, P.GRASS, P.FIELD_DARK, P.GRASS)):
        x0 = p.x - 10 + k_*p.w*0.28
        fill([(x0, p.y - 5), (x0 + p.w*0.25, p.y - 5), (x0 + p.w*0.36, hy - 30), (x0 + p.w*0.14, hy - 30)], g)
    s_([(p.x - 5, hy), (p.x + p.w + 5, hy)], BG)
    stroke(bez((p.X(0.1), p.y - 5), (p.X(0.3), p.Y(0.3)), (p.X(0.55), p.Y(0.45)), (p.X(0.7), hy - 6)), 6, g=P.WATER)
    for tx in (0.6, 0.66, 0.9, 0.96):
        tree(p.X(tx), hy - 16, 0.55, seed=int(tx*100), g=P.LEAF_DARK)


def page_tower():
    R = rows([(260, [0.5, 0.5]), (300, [1]), (190, [1])])
    with Pn(*R[0]) as p:
        bg_fill(p, 0.7)
        for yy in range(int(p.y), int(p.y + p.h), 18):
            for xx in range(int(p.x) - (18 if (yy//18) % 2 else 0), int(p.x + p.w), 36):
                shape(rrect(xx + 1, yy + 1, 34, 16, 2), P.STONE_BASE, BG*0.5)
        clockwork(p.X(0.62), p.Y(0.1), 1.6)
        kostelnik(p.X(0.2), p.Y(0.03), 1.0, mood="happy", right="point", look=(1, 0))
        say(p, "Tady je díra na klíč. Ale klíč nemáme.", *hd("kostelnik", p.X(0.2), p.Y(0.03), 1.0), w=160)
    with Pn(*R[1]) as p:
        bg_fill(p, 0.7)
        wx0, wx1, wy0, wy1 = p.X(0.45), p.X(0.85), p.Y(0.4), p.Y(0.9)
        win = [(wx0, wy0), (wx1, wy0), (wx1, wy1 - 30)] + bez((wx1, wy1 - 30), (wx1, wy1 + 12), (wx0, wy1 + 12), (wx0, wy1 - 30))
        fill(win, P.NOV_SKY); stroke(win, LINE*1.2, closed=True)
        shape([(wx0 - 8, wy0 - 10), (wx1 + 8, wy0 - 10), (wx1 + 8, wy0), (wx0 - 8, wy0)], P.STONE_BASE, BG)
        seated(hanka, "hanka", p.X(0.62), wy0, 1.1, P.DUNGAREES, P.HANKA_BOOTS, edge=2, mood="wow", look=(1, 0.3), right="point")
        babicka(p.X(0.25), p.Y(0.03), 1.05, mood="worried", right="front", look=(1, 0.3))
        say(p, "Opatrně. Držím tě.", *hd("babi", p.X(0.25), p.Y(0.03), 1.05), w=110, area=(0.0, 0.45))
        say(p, "Vidím celou vesnici!", *hd("hanka", p.X(0.62), wy0 - HIPS["hanka"]*1.1, 1.1), w=120, area=(0.45, 1.0))
    with Pn(*R[2]) as p:
        tower_view(p)
        boot_rock(p.X(0.68), p.Y(0.46), 1.25)
        hand_ = [(p.x - 5, p.Y(0.66)), (p.X(0.3), p.Y(0.6)), (p.X(0.36), p.Y(0.6)), (p.X(0.44), p.Y(0.57)),
                 (p.X(0.36), p.Y(0.54)), (p.X(0.3), p.Y(0.55)), (p.x - 5, p.Y(0.6))]
        shape(hand_, P.CLOCK_HAND, LINE)
        hidden_heart(p.X(0.2), p.Y(0.12))
        say(p, "Kamenná bota!", p.X(0.74), p.Y(0.72), w=120, x=p.X(0.08), y=p.Y(0.94))
    with Pn(*R[3]) as p:
        bg_fill(p, 0.7)
        kostelnik(p.X(0.22), p.Y(0.03), 0.95, mood="happy", right="point", look=(1, 0))
        deda(p.X(0.78), p.Y(0.03), 0.92, flip=True, mood="grin", right="up", look=(1, 0))
        say(p, "Tomu kameni se odjakživa říká Bota.", *hd("kostelnik", p.X(0.22), p.Y(0.03), 0.95), w=180)
        say(p, "Tak jdeme k Botě!", *hd("deda", p.X(0.78), p.Y(0.03), 0.92), w=120)
    page_end()


# =================================================================== 14 at the Bota
def page_bota():
    R = rows([(260, [1]), (240, [0.5, 0.5]), (250, [1])])
    with Pn(*R[0]) as p:
        countryside(p, 0.6, 8)
        boot_rock(p.X(0.55), p.Y(0.08), 1.7, crack=False)
        magpie(p.X(0.58), p.Y(0.08) + 95*1.7 - 4, 1.4, flip=True)
        candy_wrapper(p.X(0.72), p.Y(0.52), 1.4, rot=30)
        for k_ in range(3):
            stroke([(p.X(0.69) - 6 + k_*6, p.Y(0.6)), (p.X(0.69) - 3 + k_*6, p.Y(0.68))], 0.9, g=0.35)
        tonda(p.X(0.14), p.Y(0.03), 1.15, mood="surprised", right="point", look=(1, 0.5))
        hanka(p.X(0.28), p.Y(0.03), 1.15, mood="wow", look=(1, 0.5))
        say(p, "Straka něco pustila!", *hd("tonda", p.X(0.14), p.Y(0.03), 1.15), w=140)
    with Pn(*R[1]) as p:
        bg_fill(p, P.GRASS)
        tufts(p, p.Y(0.05), p.Y(0.8), 10, 7)
        candy_wrapper(p.X(0.62), p.Y(0.25), 3.2, rot=10)
        hanka(p.X(0.2), p.Y(0.03), 1.25, mood="happy", right="point", look=(1, -1))
        say(p, "Jen papírek od bonbonu.", *hd("hanka", p.X(0.2), p.Y(0.03), 1.25), w=130)
        say(p, "Straka to nebyla.", p.X(0.8), p.Y(0.5), w=110, area=(0.5, 1.0))
    with Pn(*R[2]) as p:
        bg_fill(p, P.GRASS)
        mud_patch(p.X(0.55), p.Y(0.12), p.w*0.6, 30)
        zig_print(p.X(0.48), p.Y(0.2), 1.6, 80); zig_print(p.X(0.7), p.Y(0.26), 1.6, 60)
        splavek(p.X(0.86), p.Y(0.08), 1.6, rot=70)
        hanka(p.X(0.14), p.Y(0.03), 1.2, mood="wow", right="point", look=(1, -1))
        say(p, "Zase obří bota! A tohle je co?", *hd("hanka", p.X(0.14), p.Y(0.03), 1.2), w=140, area=(0.0, 0.55))
        say(p, "Splávek. Ten tu ztratil nějaký rybář.", p.X(0.95), p.Y(0.5), w=140, area=(0.45, 1.0))
    with Pn(*R[3]) as p:
        countryside(p, 0.6, 9)
        boot_rock(p.X(0.76), p.Y(0.06), 0.95)
        dx_, dy_ = p.X(0.76) - 12, p.Y(0.06) + 92*0.95
        deda(dx_, dy_, 0.6, mood="think", look=(0, -1), shadow=False)
        tonda(p.X(0.34), p.Y(0.03), 1.1, mood="happy", right="front", look=(1, 0),
              item=lambda x, y: splavek(x, y - 6, 1.0))
        hx, hy = p.X(0.14), p.Y(0.03)
        hanka(hx, hy, 1.15, mood="happy", right="cheek", look=(1, 0),
              item=lambda x, y: vysilacka(x - 3, y - 12, 0.9, rot=-10))
        wx, wy = hand_pt(True, "cheek", hx, hy, 1.15)
        hidden_heart(p.X(0.48), p.Y(0.08))
        hd("tonda", p.X(0.34), p.Y(0.03), 1.1)
        say(p, "Zase cik-cak? Ten někdo je pořád před námi!", wx, wy + 16, w=180, area=(0.0, 0.5))
        say(p, "Hvězdičku tu nikde nevidím.", *hd("deda", dx_, dy_, 0.6), w=130, area=(0.45, 1.0))
    page_end()


# =================================================================== 15 the star
def page_star():
    R = rows([(240, [1]), (260, [0.5, 0.5]), (250, [1])])
    with Pn(*R[0]) as p:
        countryside(p, 0.6, 10, dusk=True)
        boot_rock(p.X(0.6), p.Y(0.08), 1.5, crack=True)
        babicka(p.X(0.12), p.Y(0.03), 1.05, mood="worried", look=(1, 0))
        hanka(p.X(0.28), p.Y(0.03), 1.15, mood="determined", torch=True, right="up", look=(1, 0))
        cap(p, "Stmívá se. Hvězdička nikde.", w=200)
        say(p, "Musíme domů. Je tma.", *hd("babi", p.X(0.12), p.Y(0.03), 1.05), w=120)
        say(p, "Počkejte! Mám baterku!", *hd("hanka", p.X(0.28), p.Y(0.03), 1.15), w=140)
    with Pn(*R[1]) as p:
        countryside(p, 0.7, 11, dusk=True)
        boot_rock(p.X(0.1), p.Y(0.05), 2.6, crack=True)
        hx, hy = p.X(0.8), p.Y(0.05)
        torch_beam(hx - 24, hy + 40, p.X(0.3), p.Y(0.25), p.X(0.4), p.Y(0.02), 0.55)
        hanka(hx, hy, 1.2, flip=True, mood="determined", torch=True, right="lens", look=(1, -0.5))
        say(p, "Tam se vejde jen Hanka.", p.X(0.6), p.Y(0.9), w=130, area=(0.4, 1.0))
    with Pn(*R[2]) as p:
        bg_fill(p, 0.1)
        torch_beam(p.X(0.9), p.Y(0.5), p.X(0.0), p.Y(1.0), p.X(0.0), p.Y(0.0), 0.5)
        star(p.X(0.36), p.Y(0.66), 18, 0.85, w=LINE*1.2)
        treasure_tin(p.X(0.4), p.Y(0.12), 1.3, dirty=True)
        say(p, "Hvězdička…", p.X(0.7), p.Y(0.9), whisper=True, w=110, area=(0.5, 1.0))
    with Pn(*R[3]) as p:
        bg_fill(p, 1.0); rays(p, p.X(0.5), p.Y(0.5), 0.9)
        hanka(p.X(0.5), p.Y(0.03), 1.5, mood="laugh", right="up", look=(0, 0.5),
              item=lambda x, y: treasure_tin(x, y + 2, 0.45))
        tonda(p.X(0.82), p.Y(0.03), 1.1, flip=True, mood="laugh", right="up")
        babicka(p.X(0.16), p.Y(0.03), 1.0, mood="laugh", right="up")
        joey(p.X(0.3), p.Y(0.03), 0.9, mood="happy")
        sfx(p.X(0.05), p.Y(0.8), "HURÁ!", 28, 8)
        say(p, "MÁM HO!", *hd("hanka", p.X(0.5), p.Y(0.03), 1.5), w=100)
        say(p, "Hanka to vyřešila!", *hd("tonda", p.X(0.82), p.Y(0.03), 1.1), w=130)
    page_end()


# =================================================================== 16 the tin at Alica's bed
def page_tin():
    R = rows([(225, [1]), (245, [1]), (280, [0.5, 0.5])])
    with Pn(*R[0]) as p:
        sickroom(p, evening=True)
        ax, ay = alica_in_bed(p.X(0.28), p.X(0.6), p.y + 48, 1.35, mood="grin", right="front", look=(1, 0),
                              item=lambda x, y: treasure_tin(x - 4, y - 6, 0.4))
        for fn, xx, fs, who in ((deda, 0.08, 0.92, "deda"), (babicka, 0.18, 0.95, "babi"), (hanka, 0.72, 1.1, "hanka"), (tonda, 0.86, 1.0, "tonda")):
            fn(p.X(xx), p.y + 14, fs, flip=xx > 0.5, mood="grin", look=(1, 0))
            hd(who, p.X(xx), p.y + 14, fs)
        cap(p, "Plechovku otevřou u Alicy. Celý klub.", w=200)
        say(p, "Raz, dva, tři!", *hd("alica", ax, ay, 1.35), w=110)
    with Pn(*R[1]) as p:
        bg_fill(p, P.BLANKET)
        for xx in range(int(p.x), int(p.x + p.w) + 16, 16):
            for yy in range(int(p.y), int(p.y + p.h) + 16, 16):
                dot(xx + ((yy//16) % 2)*8, yy, 1.8, P.BLANKET_DOT)
        hen_whistle(p.X(0.12), p.Y(0.12), 2.6)
        marbles(p.X(0.3), p.Y(0.12), 2.2)
        clock_key(p.X(0.42), p.Y(0.18), 2.4, rot=8)
        new_letter(p.X(0.7), p.Y(0.1), 1.7, rot=5)
        hidden_heart(p.X(0.36), p.Y(0.42))
        say(p, "Dřevěná slepička! A kuličky!", p.X(0.15), p.Y(0.4), w=150, area=(0.0, 0.45))
        say(p, "A takový velký klíč… Od čeho asi?", p.X(0.5), p.Y(0.4), w=170, area=(0.3, 0.7))
    with Pn(*R[2]) as p:
        sickroom(p, evening=True, window=False)
        ax, ay = alica_in_bed(p.x - 20, p.X(0.52), p.y + 48, 1.35, mood="wow", right="front", look=(1, 0),
                              item=lambda x, y: new_letter(x - 10, y - 6, 0.45, rot=-4))
        say(p, "Tenhle papír je bílý a nový. Není vůbec starý!", *hd("alica", ax, ay, 1.35), w=190)
    with Pn(*R[3]) as p:
        sickroom(p, evening=True, window=False)
        babicka(p.X(0.25), p.y + 14, 1.2, mood="surprised", look=(1, 0))
        alica(p.X(0.72), head_y(p, 0.55, 89.8, 1.8), 1.8, flip=True, mood="determined", right="point", look=(1, 0), shadow=False)
        bl = [(p.X(0.45), p.y - 5)] + bez((p.X(0.45), p.Y(0.3)), (p.X(0.6), p.Y(0.36)), (p.X(0.8), p.Y(0.3)), (p.x + p.w + 5, p.Y(0.33))) + \
             [(p.x + p.w + 5, p.y - 5)]
        fill(bl, P.BLANKET)
        C.saveState(); C.clipPath(poly(bl), stroke=0, fill=0)
        for xx in range(int(p.X(0.44)), int(p.x + p.w) + 16, 16):
            for yy in range(int(p.y), int(p.Y(0.4)), 16): dot(xx + ((yy//16) % 2)*8, yy, 1.8, P.BLANKET_DOT)
        C.restoreState(); stroke(bl, BG*1.2, closed=True)
        say(p, "Kdo ho tam dal?", *hd("babi", p.X(0.25), p.y + 14, 1.2), w=110)
        say(p, "Ten, kdo jde po stopě před námi!", *hd("alica", p.X(0.72), head_y(p, 0.55, 89.8, 1.8), 1.8), w=150)
    page_end()



# =================================================================== 17 STOP, DETEKTIVE!
def page_stop():
    with Pn(M, 40, W-2*M, H-80, bg=0.95) as p:
        title(p.X(0.5), p.Y(0.92), "STOP, DETEKTIVE!", 44)
        hand_text(p.X(0.05), p.Y(0.86), p.w*0.9, "Už máš všechny stopy.", "SHB", 18)
        cw, ch = p.w*0.3, p.h*0.215
        items = [
            ("obří bota cik-cak u kurníku i u Boty", lambda x, y: (zig_print(x - 14, y + 26, 0.9, 80), zig_print(x + 16, y + 34, 0.9, 70))),
            ("splávek v trávě u Boty", lambda x, y: (boot_rock(x - 22, y, 0.3), splavek(x + 22, y + 6, 1.1, rot=60))),
            ("rybář šel ve tři kolem hodin a usmál se", lambda x, y: (church_clock(x - 22, y + 44, 12), rybar(x + 18, y, 0.44, mood="grin", right="hold"))),
            ("kostelník: „Na věž lezl jen malý Franta.“", lambda x, y: kostelnik(x, y, 0.5, mood="talk", right="up")),
            ("velký železný klíč v plechovce", lambda x, y: clock_key(x - 26, y + 24, 1.05)),
            ("nový dopis – v rohu stejná slepička jako ve starém", lambda x, y: new_letter(x - 30, y + 2, 0.64)),
        ]
        for i, (txt, pic) in enumerate(items):
            cx = p.X(0.04) + (i % 3)*(cw + p.w*0.02); cy = p.Y(0.82) - (i//3 + 1)*(ch + 10)
            shape(rrect(cx, cy, cw, ch, 8), 1.0, 1.2)
            hand_text(cx + 6, cy + ch - 20, 30, str(i + 1), "SHB", 16, align="left")
            with T(cx + cw/2, cy + 38, 1.45):
                pic(0, 0)
            hand_text(cx + 8, cy + 20, cw - 16, txt, "SH", 10.5, lead=12)
        by = p.Y(0.82) - 2*(ch + 10) - 70
        shape(rrect(p.X(0.04), by, p.w*0.92, 60, 8), 1.0, 1.2)
        hand_text(p.X(0.06), by + 36, 30, "7", "SHB", 16, align="left")
        hand_text(p.X(0.12), by + 36, p.w*0.74, "V sešitě č. 3 řekl rybář: „Moje holinky jsou obří.“", "SH", 14, align="left")
        magnifier(p.X(0.9), by + 30, ang=-30, r=12)
        hand_text(p.X(0.05), by - 32, p.w*0.9, "Kdo šel po stopě před Hankou?", "SHB", 20)
        hand_text(p.X(0.05), by - 58, p.w*0.9, "Kdo je dnes Franta? A proč stojí hodiny?", "SHB", 20)
        hand_text(p.X(0.05), by - 84, p.w*0.9, "Nápověda: prohlédni si znovu strany 9 a 16.", "SH", 14)
        with T(p.X(0.5), p.Y(0.06), 1.0, rot=180):
            hand_text(-p.w*0.45, 0, p.w*0.9, "Rybář! Rybář je Franta. Malý Franta schoval klíč od hodin do svého pokladu.", "SH", 12)
            hand_text(-p.w*0.45, -15, p.w*0.9, "Proto hodiny stojí. Otoč na další stranu!", "SH", 12)
    page_end()


# =================================================================== 18 Hanka reads the new letter
def hen_circle(x, y, r):
    stroke(ell(x, y, r, r*0.8, 30), 2.2, closed=True, g=P.CRAYON_RED)


def page_read():
    R = rows([(240, [1]), (235, [1]), (275, [0.5, 0.5])])
    with Pn(*R[0]) as p:
        sickroom(p, evening=True, window=False)
        ax, ay = alica_in_bed(p.X(0.52), p.X(0.9), p.y + 48, 1.4, mood="wow", look=(-1, 0))
        hanka(p.X(0.24), p.y + 14, 1.3, mood="determined", right="front", look=(1, 0),
              item=lambda x, y: new_letter(x - 4, y - 20, 0.5, rot=-4))
        say(p, "Rybička. Molo. Tři hodiny. Klobouk.", *hd("hanka", p.X(0.24), p.y + 14, 1.3), w=170)
        say(p, "Ty to umíš přečíst?", *hd("alica", ax, ay, 1.4), w=120)
    with Pn(*R[1]) as p:
        bg_fill(p, P.TABLE)
        for k_ in range(1, 5): stroke([(p.x, p.Y(k_/5)), (p.x + p.w, p.Y(k_/5))], BG*0.6)
        ox, oy, os_ = p.X(0.04), p.Y(0.1), 2.0
        picture_letter(ox, oy, os_)
        nx, ny, ns = p.X(0.52), p.Y(0.1), 2.0
        new_letter(nx, ny, ns)
        hen_circle(ox + 18*os_, oy + 44*os_, 17*os_)
        hen_circle(nx + 82*ns, ny + 12*ns, 17*ns)
        keep_clear(p, ox, oy, nx + 94*ns, oy + 66*os_, "letters")
        say(p, "Koukej! Stejná slepička! Kreslil to stejný člověk.", p.X(0.5), p.Y(0.92), w=260, x=p.X(0.25), y=p.Y(0.97))
    with Pn(*R[2]) as p:
        sickroom(p, evening=True, window=False)
        ax, ay = alica_in_bed(p.x - 20, p.X(0.55), p.y + 48, 1.4, mood="worried", right="chin", look=(1, 0))
        say(p, "Ve tři na molu čeká pán s kloboukem. A co když chce Frantův poklad?", *hd("alica", ax, ay, 1.4), w=210)
    with Pn(*R[3]) as p:
        sickroom(p, evening=True, window=False)
        ax, ay = alica_in_bed(p.X(0.5), p.X(0.94), p.y + 48, 1.3, mood="happy", look=(-1, 0))
        hanka(p.X(0.2), p.y + 14, 1.2, mood="happy", look=(1, 0))
        say(p, "Nechce. Nic nevzal. Jenom kreslil.", *hd("hanka", p.X(0.2), p.y + 14, 1.2), w=150)
        say(p, "…Máš pravdu, Hanko.", *hd("alica", ax, ay, 1.3), w=120)
    page_end()


# =================================================================== 19 at the jetty
def page_jetty():
    R = rows([(240, [1]), (265, [0.5, 0.5]), (245, [1])])
    with Pn(*R[0]) as p:
        fy = pond_view(p, 0.2, 0.62, seed=61, mill_at=0.12, mill_s=0.5, clouds_=False)
        jetty(p.X(0.62), p.X(1.05), p.Y(0.26))
        rybar(p.X(0.88), p.Y(0.26), 0.95, flip=True, mood="happy", right="hold", look=(1, 0))
        joey(p.X(0.08), p.Y(0.03), 0.8, mood="happy")
        hanka(p.X(0.2), p.Y(0.03), 1.0, mood="determined", legs="walk", look=(1, 0))
        for fn, xx, fs in ((babicka, 0.32, 0.9), (deda, 0.42, 0.85), (tonda, 0.52, 0.9)):
            fn(p.X(xx), p.Y(0.03), fs, mood="happy", legs="walk", look=(1, 0))
        verka_old(p.X(0.02), p.Y(0.1), 0.8, mood="happy", legs="walk", look=(1, 0))
        cap(p, "Tři hodiny. Molo u rybníka. Věrka jde taky.", w=260)
    with Pn(*R[1]) as p:
        pond_view(p, 0.22, 0.7, seed=62, clouds_=False)
        jetty(p.X(0.5), p.X(1.05), p.Y(0.22))
        hanka(p.X(0.25), p.Y(0.03), 1.2, mood="determined", right="up", look=(1, 0.5),
              item=lambda x, y: new_letter(x - 8, y - 4, 0.4, rot=6))
        rybar(p.X(0.8), p.Y(0.22), 1.05, flip=True, mood="surprised", right="down", look=(1, -0.5))
        say(p, "Tys to nakreslil. Ty jsi Franta!", *hd("hanka", p.X(0.25), p.Y(0.03), 1.2), w=150)
    with Pn(*R[2]) as p:
        pond_view(p, 0.22, 0.7, seed=63, clouds_=False)
        rybar(p.X(0.5), p.Y(0.03), 1.3, mood="grin", right="front", look=(-1, -0.3), hat=False, glasses=True, rod=False,
              item=lambda x, y: bucket_hat(x + 6, y - 6, 1.0, rot=-10))
        say(p, "Poznalas mě podle obrázků. To ještě nikdo neuměl.", *hd("rybar", p.X(0.5), p.Y(0.03), 1.3), w=190)
    with Pn(*R[3]) as p:
        bg_fill(p, 1.0); rays(p, p.X(0.5), p.Y(0.5), 0.9)
        rybar(p.X(0.5), p.Y(0.04), 1.1, mood="laugh", left="hug", right="hug", hat=False, glasses=True, rod=False)
        deda(p.X(0.4), p.Y(0.04), 1.2, mood="surprised", left="hug", right="hug", look=(1, 0))
        verka_old(p.X(0.6), p.Y(0.04), 1.15, flip=True, mood="laugh", left="hug", right="hug", stick=False, look=(1, 0))
        hd("rybar", p.X(0.5), p.Y(0.04), 1.1)
        hanka(p.X(0.9), p.Y(0.03), 0.95, flip=True, mood="grin", right="up")
        hidden_heart(p.X(0.08), p.Y(0.1))
        say(p, "Franto?!", *hd("deda", p.X(0.4), p.Y(0.04), 1.2), w=90, area=(0.0, 0.45))
        say(p, "Franto! Tolik let!", *hd("verka", p.X(0.6), p.Y(0.04), 1.15), w=120, area=(0.55, 1.0))
    page_end()


# =================================================================== 20 Franta's story
def tower_room(p):
    bg_fill(p, 0.7)
    for yy in range(int(p.y), int(p.y + p.h), 18):
        for xx in range(int(p.x) - (18 if (yy//18) % 2 else 0), int(p.x + p.w), 36):
            shape(rrect(xx + 1, yy + 1, 34, 16, 2), P.STONE_BASE, BG*0.5)


def page_story():
    R = rows([(250, [0.5, 0.5]), (250, [0.5, 0.5]), (250, [1])])
    with Pn(*R[0]) as p:
        tower_room(p)
        clockwork(p.X(0.66), p.Y(0.14), 1.3)
        young(p.X(0.25), p.Y(0.06), 1.3, "franta", mood="grin", right="up", look=(1, 0),
              item=lambda x, y: clock_key(x - 6, y + 2, 0.7, rot=20))
        old_photo(p)
        cap(p, "Před mnoha lety si malý Franta vzal z věže klíč. Do svého pokladu.", w=p.w - 30)
    with Pn(*R[1]) as p:
        bg_fill(p, P.NOV_SKY)
        church(p.X(0.5), p.Y(0.5) - 108*1.6, 1.6, nave=False)
        old_photo(p)
        cap(p, "Hodiny se zastavily. Přesně ve tři.", w=p.w - 30)
    with Pn(*R[2]) as p:
        countryside(p, 0.6, 12)
        boot_rock(p.X(0.62), p.Y(0.1), 1.3, crack=True)
        young(p.X(0.28), p.Y(0.06), 1.25, "franta", mood="happy", right="front", look=(1, 0),
              item=lambda x, y: picture_letter(x - 14, y - 10, 0.35, rot=-5))
        treasure_tin(p.X(0.47), p.Y(0.06), 0.45)
        old_photo(p)
        cap(p, "Poklad schoval pod Botu. A nakreslil dopis pro Honzu.", w=p.w - 30)
    with Pn(*R[3]) as p:
        village(p, p.Y(0.14), seed=13)
        moving_van(p.X(0.58), p.Y(0.06), 1.3)
        young(p.X(0.2), p.Y(0.06), 1.2, "franta", mood="sad", right="wave", look=(1, 0))
        old_photo(p)
        cap(p, "Druhý den se odstěhoval. Dopis nikdo nepřečetl.", w=p.w - 30)
    with Pn(*R[4]) as p:
        pond_view(p, 0.22, 0.7, seed=64, clouds_=False)
        rybar(p.X(0.18), p.Y(0.03), 1.05, mood="talk", right="front", hat=False, glasses=True, rod=False, look=(1, 0))
        for fn, who, xx, fs in ((deda, "deda", 0.62, 0.95), (verka_old, "verka", 0.76, 0.95), (hanka, "hanka", 0.9, 1.0)):
            fn(p.X(xx), p.Y(0.03), fs, flip=True, mood="happy", look=(1, 0))
            hd(who, p.X(xx), p.Y(0.03), fs)
        say(p, "Když jsem se vrátil, byl ze mě vousatý rybář. Styděl jsem se zaklepat.",
            *hd("rybar", p.X(0.18), p.Y(0.03), 1.05), w=220, area=(0.0, 0.46))
        say(p, "Pak mi Věrka řekla o vás a o dopisu. Tak jsem ráno prošel stopu. A nechal vám nový.",
            *hd("rybar", p.X(0.18), p.Y(0.03), 1.05), w=240, area=(0.5, 1.0))
    page_end()


# =================================================================== 21 the clock runs again
def page_clock():
    R = rows([(250, [0.5, 0.5]), (230, [1]), (270, [1])])
    with Pn(*R[0]) as p:
        sickroom(p, window=False)
        rybar(p.X(0.22), p.y + 14, 0.9, mood="happy", right="front", hat=False, glasses=True, rod=False, look=(1, 0),
              item=lambda x, y: getwell_drawing(x - 4, y - 16, 44, 32, rot=-4))
        ax, ay = alica_in_bed(p.X(0.5), p.X(0.94), p.y + 48, 1.25, mood="grin", look=(-1, 0))
        say(p, "Obrázkový dopis pro tebe. Znamená: brzy se uzdrav!", *hd("rybar", p.X(0.22), p.y + 14, 0.9), w=190)
        say(p, "Děkuju!", *hd("alica", ax, ay, 1.25), w=90)
    with Pn(*R[1]) as p:
        sickroom(p, window=False)
        rybar(p.X(0.3), p.y + 14, 0.9, mood="happy", right="front", hat=False, glasses=True, rod=False, look=(1, 0),
              item=lambda x, y: hen_whistle(x + 4, y - 4, 0.8))
        hanka(p.X(0.72), p.y + 14, 1.2, flip=True, mood="happy", right="hush", look=(1, 0.3),
              item=lambda x, y: hen_whistle(x - 14, y - 4, 0.6, flip=True))
        say(p, "A tahle slepička je pro tebe.", *hd("rybar", p.X(0.3), p.y + 14, 0.9), w=140)
        sfx(p.X(0.5), p.Y(0.5), "FÍÍÍ!", 20, -6)
    with Pn(*R[2]) as p:
        village(p, p.Y(0.2), 0.86, 0.8, seed=15)
        rybar(p.X(0.22), p.Y(0.03), 0.95, mood="happy", right="front", hat=False, glasses=True, rod=False, look=(1, 0),
              item=lambda x, y: clock_key(x - 2, y - 2, 0.8, rot=-8))
        kostelnik(p.X(0.55), p.Y(0.03), 1.0, flip=True, mood="wow", right="up", look=(1, 0))
        say(p, "Tohle patří vám. Promiňte. Byl jsem malý uličník.", *hd("rybar", p.X(0.22), p.Y(0.03), 0.95), w=180)
        say(p, "Klíč od hodin! Po tolika letech!", *hd("kostelnik", p.X(0.55), p.Y(0.03), 1.0), w=150)
    with Pn(*R[3]) as p:
        village(p, p.Y(0.16), 0.5, 1.05, seed=16, hour=12)
        figs = [(babicka, "babi", 0.07, 0.9), (deda, "deda", 0.17, 0.85), (verka_old, "verka", 0.28, 0.88),
                (alica, "alica", 0.62, 1.0), (hanka, "hanka", 0.71, 1.05), (tonda, "tonda", 0.8, 0.95)]
        for fn, who, xx, fs in figs:
            kw = dict(stick=False) if fn is verka_old else {}
            fn(p.X(xx), p.Y(0.03), fs, flip=xx > 0.5, mood="grin", right="wave", **kw)
        rybar(p.X(0.92), p.Y(0.03), 0.85, flip=True, mood="grin", right="up", hat=False, glasses=True, rod=False)
        joey(p.X(0.4), p.Y(0.03), 0.75, mood="happy")
        hidden_heart(p.X(0.55), p.Y(0.06))
        for k_ in range(3):
            stroke(ell(p.X(0.5), p.Y(0.16) + 108*1.05, 22 + k_*9, 22 + k_*9, 20, 20, 70), 1.2, g=0.3)
            stroke(ell(p.X(0.5), p.Y(0.16) + 108*1.05, 22 + k_*9, 22 + k_*9, 20, 110, 160), 1.2, g=0.3)
        sfx(p.X(0.64), p.Y(0.8), "BIM BAM!", 24, -6)
        cap(p, "O týden později. Alice je líp a hodiny zase jdou.", w=220)
        say(p, "Klub Hvězdička je zase celý!", p.X(0.5), p.Y(0.36), w=200, area=(0.0, 0.46))
    page_end()


# =================================================================== 22 activity
def page_quiz():
    with Pn(M, 40, W-2*M, H-80) as p:
        box = [(p.X(0.05), p.Y(0.905)), (p.X(0.95), p.Y(0.91)), (p.X(0.95), p.Y(0.905)+54), (p.X(0.05), p.Y(0.905)+52)]
        fill(box, 0.92)
        for a_, b_ in ((0, 1), (1, 2), (2, 3), (3, 0)): stroke([box[a_], box[b_]], 1.5)
        hand_text(p.X(0.05), p.Y(0.905)+18, p.w*0.9, "Detektivní zápisník", "SHB", 26)
        hand_text(p.X(0.05), p.Y(0.84), p.w*0.9, "Nakresli svůj obrázkový dopis! Kam má kamarád dojít?", "SHB", 15)
        bw, bh = p.w*0.36, p.h*0.14
        spots = [(p.X(0.07), p.Y(0.64)), (p.X(0.57), p.Y(0.64)), (p.X(0.57), p.Y(0.46)), (p.X(0.07), p.Y(0.46))]
        for i, (bx, by) in enumerate(spots):
            shape(rrect(bx, by, bw, bh, 8), 1.0, 1.2)
            hand_text(bx + 6, by + bh - 20, 30, str(i + 1), "SHB", 14, align="left")
        _a = lambda a, b: (stroke([a, b], 1.6), stroke([b, (b[0] - 7, b[1] + 5)], 1.6), stroke([b, (b[0] - 7, b[1] - 5)], 1.6)) if a[0] < b[0] else \
            (stroke([a, b], 1.6), stroke([b, (b[0] + 7, b[1] + 5)], 1.6), stroke([b, (b[0] + 7, b[1] - 5)], 1.6))
        _a((p.X(0.44), p.Y(0.64) + bh/2), (p.X(0.56), p.Y(0.64) + bh/2))
        stroke([(p.X(0.75), p.Y(0.635)), (p.X(0.75), p.Y(0.465) + bh + 3)], 1.6)
        stroke([(p.X(0.75), p.Y(0.465) + bh + 3), (p.X(0.73), p.Y(0.465) + bh + 10)], 1.6)
        stroke([(p.X(0.75), p.Y(0.465) + bh + 3), (p.X(0.77), p.Y(0.465) + bh + 10)], 1.6)
        _a((p.X(0.56), p.Y(0.46) + bh/2), (p.X(0.44), p.Y(0.46) + bh/2))
        y = p.Y(0.4)
        qs = ["1. Kolik hodin ukazovaly hodiny na věži?", "2. Proč se kámen jmenuje Bota?",
              "3. Co bylo ve Frantově plechovce?", "4. Proč hodiny tolik let stály?"]
        for q in qs:
            hand_text(p.X(0.06), y, p.w*0.9, q, "SH", 15, align="left")
            stroke([(p.X(0.06), y - 18), (p.X(0.94), y - 18)], 0.5, g=0.5)
            y -= 42
        heart(p.X(0.08), y - 4, 10)
        hand_text(p.X(0.12), y - 10, p.w*0.84, "Hanka schovala pro nemocnou Alici 9 bílých srdíček pro zdraví. Najdeš je všechny?",
                  "SHB", 14, align="left", lead=18)
        with T(p.X(0.5), p.Y(0.015), 1.0, rot=180):
            hand_text(-p.w*0.45, 0, p.w*0.9, "Srdíčka jsou na stranách 4, 6, 9, 10, 13, 14, 16, 19 a 21.", "SH", 10)
    page_end()


# =================================================================== 23 next time
def page_next():
    with Pn(M, 40, W-2*M, H-80, bg=0.95) as p:
        hand_text(p.X(0.1), p.Y(0.93), p.w*0.8, "Příště v sešitě č. 5:", "SHB", 20)
        title(p.X(0.5), p.Y(0.84), "KDO STAVÍ SNĚHULÁKY?", 34)
        with Pn(p.X(0.08), p.Y(0.36), p.w*0.84, p.h*0.42, bg=0.9) as q:
            sky(q, 0.8)
            house(q.X(0.18), q.Y(0.3), 1.3, smoke=True)
            snow_ground(q, q.Y(0.3))
            for i in range(7):
                fill(ell(q.X(0.66) + i*16, q.Y(0.12) + i*10 + (4 if i % 2 else 0), 2.4, 3.6, 12), P.SNOW_SHADE)
                stroke(ell(q.X(0.66) + i*16, q.Y(0.12) + i*10 + (4 if i % 2 else 0), 2.4, 3.6, 12), 0.5, closed=True, g=0.5)
            snowman(q.X(0.55), q.Y(0.12), 1.8)
            alica(q.X(0.14), q.Y(0.04), 1.1, mood="wow", look=(1, 0))
            hanka(q.X(0.28), q.Y(0.04), 1.15, mood="surprised", right="point", look=(1, 0))
            snowflakes(q, 40, 5)
            say(q, "Kdo ho postavil? My ne!", *hd("hanka", q.X(0.28), q.Y(0.04), 1.15), w=150)
        hand_text(p.X(0.1), p.Y(0.3), p.w*0.8, "Ráno stojí na zahradě sněhulák. Nikdo z nás ho nestavěl. A od něj vedou malé stopy…", "SH", 16, lead=21)
        hand_text(p.X(0.3), p.Y(0.19), p.w*0.4, "Detektivní tým:", "SHB", 16)
        alica(p.X(0.06), p.Y(0.03), 0.85, mood="happy", right="wave")
        hanka(p.X(0.15), p.Y(0.03), 0.85, mood="grin")
        joey(p.X(0.26), p.Y(0.03), 0.65, mood="happy")
        tonda(p.X(0.37), p.Y(0.03), 0.8, mood="grin")
        babicka(p.X(0.48), p.Y(0.03), 0.78, mood="happy")
        deda(p.X(0.59), p.Y(0.03), 0.74, mood="happy")
        verka_old(p.X(0.7), p.Y(0.03), 0.76, flip=True, mood="happy")
        rybar(p.X(0.82), p.Y(0.03), 0.7, flip=True, mood="happy", hat=False, glasses=True, rod=False)
        hen(p.X(0.93), p.Y(0.03), 0.9, flip=True)
    page_end()


# =================================================================== 24 back cover
def back_cover():
    with Pn(M, 40, W-2*M, H-80, bg=0.95) as p:
        rays(p, p.X(0.5), p.Y(0.58), 0.9, 24)
        church_clock(p.X(0.5), p.Y(0.58), 110, hour=12)
        star(p.X(0.5), p.Y(0.58) - 50, 14, P.TAG_STAR, w=1.6)
        title(p.X(0.5), p.Y(0.3), "HODINY ZASE JDOU!", 34)
        hand_text(p.X(0.1), p.Y(0.24), p.w*0.8, "Klub Hvězdička je zase celý.", "SHB", 22)
        hand_text(p.X(0.1), p.Y(0.06), p.w*0.8, "Velká a malá detektivka · sešit č. 4", "SH", 13, g=0.35)
    PAGE[0] += 1; cv.showPage()


cover(); page_cast(); page_sick(); page_letter(); page_henhouse(); page_inside(); page_report1(); page_church()
page_three(); page_brook(); page_board(); page_sexton(); page_tower(); page_bota(); page_star(); page_tin()
page_stop(); page_read(); page_jetty(); page_story(); page_clock(); page_quiz(); page_next()
back_cover()
cv.save()
print("ok", PAGE[0] - 1, "pages")
for pr in PROBLEMS: print("ORDER/LAYOUT:", pr)
if PROBLEMS: sys.exit(1)
