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
from props_extra import mug
from attic import (young, chest, attic, bedroom, bed_side, blanket_side, bunting, shelf_toys, kids_drawing,
                   owlet, owl_box, old_photo, map_half)
from pond import *
from letter import Panel, caption, bubble, sfx, title, series_title, hand_text, lines_of

W, H = A4
M = 28; GUT = 9; TOP = H - 30
OUT = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                   "comics", "velka_a_mala_detektivka", "03_mapa_ke_staremu_rybniku.pdf")
os.makedirs(os.path.dirname(OUT), exist_ok=True)
cv = canvas.Canvas(OUT, pagesize=A4); lib.set_canvas(cv)
cv.setTitle("Velká a malá detektivka – Případ č. 3: Mapa ke starému rybníku")
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
        "tonda": (94, 9.9), "verka": (103, 10.2), "rybar": (118, 11.2), "young": (94, 9.9)}


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


def hidden_star(x, y, r=4.2):
    """one of the 7 stars for the 'find the stars' game on the activity page"""
    star(x, y, r, 0.97, w=0.9)


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


def wading(x, feet_y, wl, w=46, seed=6):
    """pond water over the legs of somebody standing in it up to `wl`, with rings and splash"""
    r = random.Random(seed)
    top = [(x - w + i*(2*w)/16, wl + math.sin(i*1.3)*1.6) for i in range(17)]
    fill([(x - w, feet_y - 12)] + top + [(x + w, feet_y - 12)], P.POND_WATER)
    stroke(top[3:-3], LINE*0.9)
    for rx, ry in ((30, 5), (48, 8), (66, 11)):
        stroke(ell(x, wl, rx, ry, 30, 200, 340), BG*1.1, g=P.POND_RIPPLE)
        stroke(ell(x, wl, rx, ry, 30, 205, 335), 0.7)
    for k_ in range(7):
        a = math.radians(r.uniform(30, 150))
        d = r.uniform(22, 44)
        dx, dy = x + math.cos(a)*d, wl + 3 + math.sin(a)*d*0.6
        rad = r.uniform(1.0, 1.9)
        fill(ell(dx, dy, rad, rad*1.3, 12), P.POND_WATER)
        stroke(ell(dx, dy, rad, rad*1.3, 12), 0.8, closed=True)


def keep_clear(p, x0, y0, x1, y1, what="picture"):
    p.heads.append(dict(txt=what, l=x0, r=x1, top=y1, b=y0))


def hand_pt(kid_young, pose, x, y, s, flip=False):
    from style3 import Kid, arm_pts
    _, _, hh, _ = arm_pts(Kid(kid_young), 1, pose)
    return x + (-hh[0] if flip else hh[0])*s, y + hh[1]*s


def held_map(a, b):
    """the whole map held up by its two bottom corners at page points a and b"""
    d = math.hypot(b[0] - a[0], b[1] - a[1])
    full_map(a[0], a[1] - 3, d/240, math.degrees(math.atan2(b[1] - a[1], b[0] - a[0])))


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
        fy = pond_view(p, 0.3, 0.56, seed=31, mill_at=0.84, mill_s=0.75)
        willow(p.X(0.1), p.Y(0.26), 1.5, seed=3)
        reeds(p.X(0.63), p.Y(0.29), 1.3, seed=4); reeds(p.X(0.96), p.Y(0.29), 1.1, seed=7)
        duck(p.X(0.5), p.Y(0.4), 1.1); duck(p.X(0.58), p.Y(0.43), 0.9, flip=True)
        verka_old(p.X(0.72), fy + 2, 0.42, right="up", mood="happy", shadow=False)
        ax, hx = p.X(0.17), p.X(0.74)
        held_map(hand_pt(False, "up", ax, p.Y(0.03), 2.9), hand_pt(True, "up", hx, p.Y(0.03), 2.8, flip=True))
        alica(ax, p.Y(0.03), 2.9, mood="grin", right="up", look=(1, 0.3))
        hanka(hx, p.Y(0.03), 2.8, flip=True, mood="wow", right="up", look=(1, 0.3))
        joey(p.X(0.45), p.Y(0.03), 1.9, pose="sniff", mood="happy")
    box = [(M+34, H-236), (W-M-30, H-232), (W-M-34, H-48), (M+30, H-52)]
    fill([(x+3, y-3) for x, y in box], 0.0, 0.25); fill(box, 1.0)
    for a_, b_ in ((0, 1), (1, 2), (2, 3), (3, 0)): stroke([box[a_], box[b_]], 1.8)
    series_title(W/2, H-98, H-160, 40, 66)
    hand_text(M+40, H-190, W-2*M-80, "Alica a Hanka", "SHB", 20)
    hand_text(M+40, H-217, W-2*M-80, "Případ č. 3: Mapa ke starému rybníku", "SH", 15)
    magnifier(M+82, H-120, ang=-30, r=17)
    coin(W-M-100, H-118, 16)
    page_end()


# =================================================================== 2 WHO IS WHO
def page_cast():
    with Pn(M, 40, W-2*M, H-80) as p:
        hand_text(p.X(0.05), p.Y(0.95), p.w*0.9, "Kdo je kdo", "SHB", 30)
        cells = [
            ("Alica", "čte, píše a má lupu", lambda x, y: alica(x, y, 1.35, mood="happy", right="lens", lens=True)),
            ("Hanka", "všimne si i malých věcí", lambda x, y: hanka(x, y, 1.45, mood="grin")),
            ("Joey", "má nejlepší nos", lambda x, y: joey(x, y, 1.3, mood="happy")),
            ("Děda Honza", "založil Klub Hvězdička", lambda x, y: deda(x, y, 1.05, mood="happy")),
            ("Babička", "ví všechno o zvířatech", lambda x, y: babicka(x, y, 1.15, mood="happy")),
            ("Tonda", "soused odvedle", lambda x, y: tonda(x, y, 1.25, mood="grin")),
        ]
        cw, ch = p.w/3, p.h*0.29
        for i, (name, line, fig) in enumerate(cells):
            cx = p.x + (i % 3)*cw; cy = p.Y(0.9) - (i//3 + 1)*ch
            shape(rrect(cx + 8, cy + 6, cw - 16, ch - 12, 10), 0.97, 1.2)
            fig(cx + cw/2, cy + 50)
            hand_text(cx + 10, cy + 34, cw - 20, name, "SHB", 16)
            hand_text(cx + 10, cy + 18, cw - 20, line, "SH", 11)
        by = p.Y(0.9) - 2*ch - p.h*0.26
        shape(rrect(p.x + 8, by, p.w - 16, p.h*0.25, 10), P.PHOTO_BG, 1.2)
        hand_text(p.x + 20, by + p.h*0.25 - 28, p.w - 40, "Klub Hvězdička – před mnoha lety", "SHB", 17)
        for i, (who, nm) in enumerate((("deda", "Honza"), ("franta", "Franta"), ("verka", "Věrka"))):
            xx = p.X(0.25 + i*0.25)
            young(xx, by + 34, 1.05, who, mood="grin" if who == "deda" else "happy")
            hand_text(xx - 50, by + 16, 100, nm, "SHB", 14)
    page_end()


# =================================================================== 3 the whole map (script 2)
def page_map():
    R = rows([(235, [1]), (262, [1]), (262, [0.5, 0.5])])
    with Pn(*R[0]) as p:
        kitchen(p)
        mug(p.X(0.1), p.Y(0.38), 1.2)
        alica(p.X(0.3), p.Y(0.03), 1.14, mood="wow", right="up", look=(1, 0.3))
        hanka(p.X(0.45), p.Y(0.03), 1.1, mood="grin", look=(1, 0.3))
        deda(p.X(0.8), p.Y(0.03), 1.01, flip=True, mood="laugh", right="front", look=(1, 0),
             item=lambda x, y: full_map(x - 56, y - 46, 0.24, rot=-4))
        cap(p, "Minule našly Alica a Hanka obě půlky staré mapy Klubu Hvězdička.", w=250)
        say(p, "Obě půlky jsou slepené. Mapa je celá!", *hd("alica", p.X(0.3), p.Y(0.03), 1.14), w=190)
        say(p, "Kde je poklad?", *hd("hanka", p.X(0.45), p.Y(0.03), 1.1), w=120)
    with Pn(*R[1]) as p:
        bg_fill(p, P.CHEST)
        for k_ in range(1, 6): stroke([(p.x, p.Y(k_/6)), (p.x+p.w, p.Y(k_/6))], BG*0.6)
        mx, my, ms = p.X(0.03), p.Y(0.07), 0.98
        full_map(mx, my, ms)
        tx_, ty_ = mx + 104*ms, my + 58*ms
        tube([(p.X(0.62), p.y - 6), (tx_ + 26, ty_ - 30)], 26, 22, P.SHIRT, sh=0.1)
        tube([(tx_ + 26, ty_ - 30), (tx_ + 2, ty_ - 2)], 9, 7.5, P.SKIN, sh=0)
        say(p, "Tady je naše chalupa. A tady starý rybník u mlýna.", p.X(0.66), p.Y(0.1), w=200, area=(0.5, 1.0))
        say(p, "Od velké vrby dvacet kroků. Tam je křížek!", p.X(0.66), p.Y(0.1), w=200, area=(0.5, 1.0))
    with Pn(*R[2]) as p:
        kitchen(p, table=False)
        deda(p.X(0.28), p.Y(0.03), 1.01, mood="think", right="up", look=(1, 0))
        alica(p.X(0.75), p.Y(0.03), 1.1, flip=True, mood="grin", right="up", look=(1, 0.3))
        say(p, "Ale pozor. Pravidlo klubu: poklad hledá jen celý klub.", *hd("deda", p.X(0.28), p.Y(0.03), 1.01), w=170)
        say(p, "My jsme přece nové členky!", *hd("alica", p.X(0.75), p.Y(0.03), 1.1), w=130)
    with Pn(*R[3]) as p:
        garden(p, p.Y(0.14), 5, clouds=False)
        tonda(p.X(0.8), p.Y(0.14) + 4, 1.1, mood="whisper", look=(-1, 0), shadow=False)
        board_fence(p.X(0.58), p.X(1.02), p.Y(0.14) - 4, 92)
        hanka(p.X(0.2), p.Y(0.03), 1.14, mood="grin", right="point", legs="walk", look=(1, 0))
        joey(p.X(0.4), p.Y(0.03), 0.95, pose="sniff", mood="happy")
        tufts(p, p.Y(0.02), p.Y(0.12), 4, 9)
        say(p, "Tak jdeme! Joey, hledej!", *hd("hanka", p.X(0.2), p.Y(0.03), 1.14), w=150)
    page_end()


# =================================================================== 4 at the pond (script 3)
def page_pond():
    R = rows([(380, [1]), (374, [0.5, 0.5])])
    with Pn(*R[0]) as p:
        fy = pond_view(p, 0.3, 0.6, seed=2, mill_at=0.83, mill_s=0.7, sign_at=0.6, sign_s=1.15, posts=True)
        reeds(p.X(0.72), p.Y(0.3), 1.1, seed=3)
        duck(p.X(0.6), fy - 26, 0.8, flip=True); duck(p.X(0.66), fy - 20, 0.7)
        verka_old(p.X(0.72), fy + 2, 0.4, right="up", mood="happy", shadow=False)
        rybar(p.X(0.93), p.Y(0.1), 0.95, flip=True, right="hold", mood="happy", look=(1, 0))
        hidden_star(p.X(0.5), p.Y(0.36))
        deda(p.X(0.12), p.Y(0.03), 1.14, mood="surprised", legs="walk", look=(1, 0.3))
        alica(p.X(0.27), p.Y(0.03), 1.28, mood="wow", legs="walk", look=(1, 0.3))
        hanka(p.X(0.39), p.Y(0.03), 1.23, mood="happy", legs="walk", look=(1, 0.3))
        joey(p.X(0.5), p.Y(0.03), 1.0, mood="happy")
        cap(p, "Starý rybník je za lesem. Jde celý klub – i Joey.", w=250)
        say(p, "Jé… Rybník je mnohem menší, než byl.", *hd("deda", p.X(0.12), p.Y(0.03), 1.14), w=220)
    with Pn(*R[1]) as p:
        pond_view(p, 0.26, 0.64, seed=5, posts=True, clouds_=False)
        alica(p.X(0.25), p.Y(0.03), 1.41, mood="think", right="point", look=(1, 0.3))
        deda(p.X(0.72), p.Y(0.03), 1.23, flip=True, mood="sad", look=(1, 0.3))
        say(p, "Kde je lávka z mapy?", *hd("alica", p.X(0.25), p.Y(0.03), 1.41), w=170)
        say(p, "Ta už tu dávno není. Všechno se změnilo.", *hd("deda", p.X(0.72), p.Y(0.03), 1.23), w=150)
    with Pn(*R[1 + 1]) as p:
        fy = pond_view(p, 0.26, 0.6, seed=6, mill_at=0.62, mill_s=0.6, clouds_=False)
        verka_old(p.X(0.78), fy + 2, 0.5, right="wave", mood="happy", shadow=False)
        duck(p.X(0.5), fy - 22, 0.8)
        hanka(p.X(0.22), p.Y(0.03), 1.41, mood="wow", right="point", look=(1, 0.5))
        alica(p.X(0.55), p.Y(0.03), 1.41, flip=True, mood="grin", right="wave", look=(-1, 0.5))
        say(p, "Ta paní s kloboukem nám mává!", *hd("hanka", p.X(0.22), p.Y(0.03), 1.41), w=170)
        say(p, "Ahoj!", *hd("alica", p.X(0.55), p.Y(0.03), 1.41), w=80)
    page_end()


# =================================================================== 5 which willow (script 4)
def page_willow():
    R = rows([(240, [1]), (285, [0.5, 0.5]), (235, [1])])
    with Pn(*R[0]) as p:
        pond_view(p, 0.26, 0.62, seed=8, clouds_=False)
        willow(p.X(0.42), p.Y(0.2), 0.95, seed=11); willow(p.X(0.62), p.Y(0.24), 0.8, seed=12); willow(p.X(0.86), p.Y(0.2), 0.95, seed=13)
        stump(p.X(0.74), p.Y(0.1), 0.9)
        alica(p.X(0.1), p.Y(0.03), 1.28, mood="think", right="chin", look=(1, 0.3), book=False)
        hanka(p.X(0.24), p.Y(0.03), 1.23, mood="wow", right="up", look=(1, 0.3))
        say(p, "Na mapě je jedna velká vrba.", *hd("alica", p.X(0.1), p.Y(0.03), 1.28), w=190)
        say(p, "Ale tady jsou tři!", *hd("hanka", p.X(0.24), p.Y(0.03), 1.23), w=130)
    with Pn(*R[1]) as p:
        pond_view(p, 0.22, 0.7, seed=9, clouds_=False, sky_g=0.95)
        alica(p.X(0.22), p.Y(0.03), 1.32, mood="surprised", look=(1, 0.3))
        deda(p.X(0.72), p.Y(0.03), 1.19, flip=True, mood="think", right="chin", look=(1, 0.3))
        say(p, "Dědo, pamatuješ si to?", *hd("alica", p.X(0.22), p.Y(0.03), 1.32), w=140)
        say(p, "Hm… Velká vrba byla nejtlustší ze všech. Tlustší než já!", *hd("deda", p.X(0.72), p.Y(0.03), 1.19), w=160)
    with Pn(*R[2]) as p:
        pond_view(p, 0.22, 0.7, seed=10, clouds_=False)
        stump(p.X(0.6), p.Y(0.04), 1.6)
        deda(p.X(0.28), p.Y(0.03), 1.23, mood="grin", right="point", look=(1, -0.5))
        say(p, "Tady! Tahle velká vrba spadla. Zbyl z ní jen pařez.", *hd("deda", p.X(0.28), p.Y(0.03), 1.23), w=p.w*0.9)
    with Pn(*R[3]) as p:
        pond_view(p, 0.24, 0.62, seed=14, clouds_=False)
        stump(p.X(0.12), p.Y(0.04), 1.1)
        alica(p.X(0.36), p.Y(0.03), 1.32, mood="determined", book=True, look=(1, -0.3))
        hanka(p.X(0.6), p.Y(0.03), 1.28, flip=True, mood="grin", right="up", look=(1, 0.3))
        say(p, "Takže od pařezu dvacet kroků.", *hd("alica", p.X(0.36), p.Y(0.03), 1.32), w=200)
        say(p, "Já umím počítat do dvaceti!", *hd("hanka", p.X(0.6), p.Y(0.03), 1.28), w=190)
    page_end()


# =================================================================== 6 twenty steps (script 5)
def page_steps():
    R = rows([(245, [0.5, 0.5]), (250, [1]), (265, [1])])
    with Pn(*R[0]) as p:
        pond_view(p, 0.2, 0.62, seed=15, clouds_=False)
        stump(p.X(0.12), p.Y(0.04), 0.7)
        footprints(p.X(0.2), p.Y(0.06), 3, 16, 4, 1.2, P.MUD_DARK)
        deda(p.X(0.55), p.Y(0.03), 1.1, mood="determined", legs="walk", look=(1, 0))
        alica(p.X(0.88), p.Y(0.03), 0.92, flip=True, mood="grin", look=(1, 0))
        hanka(p.X(0.96), p.Y(0.03), 0.88, flip=True, mood="grin", look=(1, 0))
        say(p, "Jedna… dva… tři…", *hd("deda", p.X(0.55), p.Y(0.03), 1.1), w=150)
        say(p, "…devatenáct… dvacet!", *hd("alica", p.X(0.9), p.Y(0.03), 0.92), w=125)
    with Pn(*R[1]) as p:
        # Twenty grown-up steps run straight off the bank: he stands in the pond up to his
        # knees, not beside a puddle. The bank is only a strip along the bottom.
        pond_view(p, 0.02, 0.7, seed=16, clouds_=False)
        gx, gy, gs = p.X(0.5), p.Y(0.02), 1.15
        wl = gy + 24*gs
        for k_ in range(9):
            a = math.radians(30 + k_*15)
            stroke([(gx + math.cos(a)*36, wl + 6 + math.sin(a)*20),
                    (gx + math.cos(a)*62, wl + 6 + math.sin(a)*40)], 1.2, g=0.3)
        deda(gx, gy, gs, shadow=False, mood="surprised", left="up", right="up", look=(0, 0.5))
        wading(gx, gy, wl)
        sfx(p.X(0.05), p.Y(0.28), "ŠPLOUCH!", 24, 8)
        say(p, "Jejda! To asi nebude ono.", *hd("deda", gx, gy, gs), w=p.w*0.85)
    with Pn(*R[2]) as p:
        pond_view(p, 0.26, 0.64, seed=17, clouds_=False)
        alica(p.X(0.15), p.Y(0.03), 1.14, mood="wow", right="front", look=(1, 0.3),
              item=lambda x, y: full_map(x - 4, y - 18, 0.2))
        deda(p.X(0.88), p.Y(0.03), 1.01, flip=True, mood="laugh", look=(1, 0.3))
        hidden_star(p.X(0.55), p.Y(0.12))
        say(p, "Dědo! Na mapě jsou malinké šlápoty.", *hd("alica", p.X(0.15), p.Y(0.03), 1.14), w=190)
        say(p, "Tys byl malý kluk. Musí to být dětské kroky!", *hd("alica", p.X(0.15), p.Y(0.03), 1.14), w=200)
        say(p, "Máš pravdu. Tak krokuj ty.", *hd("deda", p.X(0.88), p.Y(0.03), 1.01), w=150)
    with Pn(*R[3]) as p:
        pond_view(p, 0.3, 0.7, seed=18, clouds_=False)
        stump(p.X(0.06), p.Y(0.05), 0.6)
        footprints(p.X(0.1), p.Y(0.08), 6, 12, 3, 0.8, P.MUD_DARK)
        alica(p.X(0.3), p.Y(0.03), 1.28, mood="determined", legs="walk", look=(1, 0))
        star_stone(p.X(0.78), p.Y(0.05), 1.6)
        hanka(p.X(0.62), p.Y(0.03), 1.19, mood="wow", right="point", look=(1, -1))
        for gx in range(8):
            stroke(bez((p.X(0.55) + gx*14, p.Y(0.02)), (p.X(0.55) + gx*14 + 2, p.Y(0.1)), (p.X(0.55) + gx*14 + 4, p.Y(0.15)), (p.X(0.55) + gx*14 + 8, p.Y(0.2))), 1.6)
            stroke(bez((p.X(0.55) + gx*14, p.Y(0.02)), (p.X(0.55) + gx*14 + 2, p.Y(0.1)), (p.X(0.55) + gx*14 + 4, p.Y(0.15)), (p.X(0.55) + gx*14 + 8, p.Y(0.2))), 0.7, g=P.TUFT)
        say(p, "…devatenáct, dvacet! Tady někde.", *hd("alica", p.X(0.3), p.Y(0.03), 1.28), w=180)
        say(p, "Tady v trávě je kámen! A má hvězdičku!", *hd("hanka", p.X(0.62), p.Y(0.03), 1.19), w=190)
    page_end()


# =================================================================== 7 somebody was here (script 6)
def page_hole():
    R = rows([(245, [0.5, 0.5]), (215, [1]), (300, [1])])
    with Pn(*R[0]) as p:
        pond_view(p, 0.22, 0.68, seed=19, clouds_=False)
        star_stone(p.X(0.85), p.Y(0.06), 1.1)
        joey(p.X(0.58), p.Y(0.05), 1.35, pose="sniff", mood="happy", flip=True)
        for k_, (dx, dy) in enumerate(((0.3, 0.3), (0.25, 0.42), (0.36, 0.46), (0.2, 0.32))):
            fill(ell(p.X(dx), p.Y(dy), 4 + k_, 3, 12), P.MUD)
        deda(p.X(0.1), p.Y(0.03), 0.97, mood="grin", right="point", look=(1, 0))
        sfx(p.X(0.4), p.Y(0.6), "HRAB HRAB", 16, -6)
        say(p, "Joey, hrabej!", *hd("deda", p.X(0.1), p.Y(0.03), 0.97), w=130)
    with Pn(*R[1]) as p:
        pond_view(p, 0.2, 0.7, seed=20, clouds_=False)
        hole(p.X(0.5), p.Y(0.05), 40, 10, tin_print=False)
        alica(p.X(0.2), p.Y(0.03), 1.23, mood="think", right="lens", lens=True, look=(1, -1))
        deda(p.X(0.8), p.Y(0.03), 1.1, flip=True, mood="worried", look=(1, -0.5))
        say(p, "Ta hlína je nějaká měkká.", *hd("alica", p.X(0.2), p.Y(0.03), 1.23), w=150)
        say(p, "Jako by ji někdo nedávno kopal…", *hd("deda", p.X(0.8), p.Y(0.03), 1.1), w=150)
    with Pn(*R[2]) as p:
        bg_fill(p, P.GRASS)
        hole(p.X(0.5), p.Y(0.2), 150, 44)
        cap(p, "V díře je jen otisk hranaté plechovky. Plechovka tam není.", w=p.w*0.6)
    with Pn(*R[3]) as p:
        pond_view(p, 0.22, 0.66, seed=21, clouds_=False)
        hole(p.X(0.5), p.Y(0.04), 60, 14)
        hanka(p.X(0.18), p.Y(0.03), 1.36, mood="surprised", look=(1, -1))
        alica(p.X(0.36), p.Y(0.03), 1.41, mood="wow", look=(1, -1))
        deda(p.X(0.7), p.Y(0.03), 1.28, flip=True, mood="surprised", look=(1, -1))
        joey(p.X(0.86), p.Y(0.03), 1.1, flip=True, mood="calm")
        say(p, "Poklad je pryč!", *hd("hanka", p.X(0.18), p.Y(0.03), 1.36), w=160)
        say(p, "Někdo tu byl před námi!", *hd("alica", p.X(0.36), p.Y(0.03), 1.41), w=210)
    page_end()


# =================================================================== 8 clues (script 7)
def page_clues():
    R = rows([(260, [0.5, 0.5]), (250, [1]), (240, [1])])
    with Pn(*R[0]) as p:
        bg_fill(p, P.MUD)
        for (bx, by, rr) in ((0.3, 0.16, -10), (0.52, 0.32, 5), (0.72, 0.18, -8)):
            boot_print(p.X(bx), p.Y(by), 2.2, rr)
            stick_dot(p.X(bx) - 30, p.Y(by) + 14, 4.4)
        alica(p.X(0.8), head_y(p, 0.55, 89.8, 2.3), 2.3, mood="wow", right="lens", lens=True, look=(-1, -1), shadow=False)
        say(p, "Stopy od velkých bot!", p.X(0.5), p.Y(0.75), w=150)
    with Pn(*R[1]) as p:
        bg_fill(p, P.GRASS)
        mud_patch(p.X(0.5), p.Y(0.14), p.w*0.5, 26)
        boot_print(p.X(0.42), p.Y(0.12), 1.2, -8); stick_dot(p.X(0.33), p.Y(0.2), 2.4)
        boot_print(p.X(0.62), p.Y(0.16), 1.2, 4); stick_dot(p.X(0.53), p.Y(0.24), 2.4)
        hanka(p.X(0.15), p.Y(0.03), 1.1, mood="wow", right="point", look=(1, -1))
        alica(p.X(0.85), p.Y(0.03), 1.14, flip=True, mood="happy", book=True, look=(1, -0.5))
        say(p, "A tady jsou malé dírky.", *hd("hanka", p.X(0.15), p.Y(0.03), 1.1), w=130)
        say(p, "Jako když zobe ptáček.", *hd("hanka", p.X(0.15), p.Y(0.03), 1.1), w=130)
        say(p, "Dobře, Hanko. Zapíšu to.", *hd("alica", p.X(0.85), p.Y(0.03), 1.14), w=120)
    with Pn(*R[2]) as p:
        bg_fill(p, 0.9)
        notebook_big(p.X(0.1), p.Y(0.07), p.w*0.8, p.h*0.72, "PŘÍPAD Č. 3: KDO VYKOPAL POKLAD?",
                     ["Stopa č. 1: díra je znovu zasypaná", "Stopa č. 2: velké boty", "Stopa č. 3: malé dírky (ptáček?)"])
        magnifier(p.X(0.9), p.Y(0.2), ang=30, r=14)
        cap(p, "Alica si všechno zapisuje.", w=210)
    with Pn(*R[3]) as p:
        pond_view(p, 0.22, 0.66, seed=22, clouds_=False)
        deda(p.X(0.72), p.Y(0.03), 1.23, flip=True, mood="think", right="chin", look=(1, 0))
        say(p, "Kdo mohl vědět, kde poklad je? Mapa byla přece roztržená…", *hd("deda", p.X(0.72), p.Y(0.03), 1.23), w=p.w*0.55)
    page_end()


# =================================================================== 9 suspect 1 (script 8)
def page_tonda():
    R = rows([(265, [1]), (245, [0.5, 0.5]), (250, [1])])
    with Pn(*R[0]) as p:
        pond_view(p, 0.26, 0.62, seed=23, clouds_=False)
        tonda(p.X(0.72), p.Y(0.22), 1.2, mood="surprised", right="hold", look=(-1, 0),
              item=lambda x, y: spade(x + 3, y - 34, 1.0, rot=-8))
        for k_ in range(6): reeds(p.X(0.58) + k_*18, p.Y(0.2), 1.3, seed=30 + k_)
        for (dx, dy) in ((0.68, 0.62), (0.71, 0.66)): dot(p.X(dx), p.Y(dy), 2.4, P.MUD_DARK)
        alica(p.X(0.12), p.Y(0.03), 1.36, mood="surprised", right="point", look=(1, 0.3))
        hanka(p.X(0.27), p.Y(0.03), 1.28, mood="wow", look=(1, 0.3))
        say(p, "Hele! Tonda! A má lopatku!", *hd("alica", p.X(0.12), p.Y(0.03), 1.36), w=190)
    with Pn(*R[1]) as p:
        pond_view(p, 0.22, 0.66, seed=24, clouds_=False)
        alica(p.X(0.25), p.Y(0.03), 1.32, mood="determined", right="point", look=(1, 0))
        tonda(p.X(0.72), p.Y(0.03), 1.28, flip=True, mood="worried", right="back", left="back", look=(1, 0))
        backpack(p.X(0.72) + 22, p.Y(0.28), 0.9)
        for (dx, dy) in ((0.63, 0.34), (0.8, 0.3)): dot(p.X(dx), p.Y(dy), 2.2, P.MUD_DARK)
        say(p, "Tondo, cos tu kopal?", *hd("alica", p.X(0.25), p.Y(0.03), 1.32), w=140)
        say(p, "Nic! Nic nevím!", *hd("tonda", p.X(0.72), p.Y(0.03), 1.28), w=120)
    with Pn(*R[2]) as p:
        pond_view(p, 0.22, 0.66, seed=25, clouds_=False)
        tonda(p.X(0.7), p.Y(0.05), 1.4, mood="worried", legs="walk", look=(1, 0),
              item=lambda x, y: backpack(x - 2, y - 26, 0.8))
        for k_ in range(3):
            stroke([(p.X(0.22), p.Y(0.35) + k_*16), (p.X(0.5), p.Y(0.35) + k_*16)], 1.2, g=0.3)
        sfx(p.X(0.08), p.Y(0.78), "ŠUP!", 28, 8)
    with Pn(*R[3]) as p:
        pond_view(p, 0.22, 0.66, seed=26, clouds_=False)
        alica(p.X(0.2), p.Y(0.03), 1.32, mood="determined", right="up", look=(1, 0))
        hanka(p.X(0.82), p.Y(0.03), 1.28, flip=True, mood="think", look=(1, 0))
        say(p, "Utekl! A byl celý od bláta.", *hd("alica", p.X(0.2), p.Y(0.03), 1.32), w=190)
        say(p, "Podezřelý č. 1: Tonda!", *hd("alica", p.X(0.2), p.Y(0.03), 1.32), w=180)
        say(p, "Hm…", *hd("hanka", p.X(0.82), p.Y(0.03), 1.28), w=80)
    page_end()


# =================================================================== 10 suspect 2 (script 9)
def burrow(x, y, s=1.0):
    with T(x, y, s):
        shape(bez((-40, 0), (-30, 30), (30, 30), (40, 0)), P.MUD, BG)
        shape(ell(0, 8, 16, 11, 24), 0.08, BG)
        for dx in (-26, 24): fill(ell(dx, -2, 7, 3, 12), P.MUD_DARK)


def page_badger():
    R = rows([(245, [0.5, 0.5]), (215, [1]), (300, [1])])
    with Pn(*R[0]) as p:
        pond_view(p, 0.3, 0.75, seed=27, clouds_=False)
        burrow(p.X(0.72), p.Y(0.08), 1.2)
        joey(p.X(0.32), p.Y(0.05), 1.3, mood="bark")
        sfx(p.X(0.5), p.Y(0.62), "HAF HAF!", 18, -6)
        say(p, "Další díry!", p.X(0.1), p.Y(0.35), w=120)
    with Pn(*R[1]) as p:
        pond_view(p, 0.3, 0.75, seed=28, clouds_=False)
        burrow(p.X(0.5), p.Y(0.06), 0.9)
        deda(p.X(0.2), p.Y(0.03), 1.19, mood="happy", right="point", look=(1, 0))
        alica(p.X(0.8), p.Y(0.03), 1.28, flip=True, mood="determined", right="up", look=(1, 0))
        say(p, "To je nora. Tady bydlí jezevec.", *hd("deda", p.X(0.2), p.Y(0.03), 1.19), w=150)
        say(p, "Jezevec hrabe! Podezřelý č. 2!", *hd("alica", p.X(0.8), p.Y(0.03), 1.28), w=140)
    with Pn(*R[2]) as p:
        bg_fill(p, P.PHOTO_BG)
        ground(p, p.Y(0.2), P.GRASS)
        badger(p.X(0.3), p.Y(0.12), 2.6)
        badger_track(p.X(0.62), p.Y(0.2), 2.0); badger_track(p.X(0.7), p.Y(0.12), 2.0, rot=8)
        hand_text(p.X(0.55), p.Y(0.83), p.w*0.42, "Víš, že…?", "SHB", 18, align="left")
        hand_text(p.X(0.55), p.Y(0.68), p.w*0.42, "Jezevec v noci hrabe v zemi. Hledá žížaly a kořínky. Ve dne spí v noře.", "SH", 13, align="left")
        stroke([(p.X(0.47), p.Y(0.1)), (p.X(0.3) + 20, p.Y(0.12) + 6)], 0.9)
        hand_text(p.X(0.48), p.Y(0.07), 90, "drápky", "SHB", 12, align="left")
    with Pn(*R[3]) as p:
        pond_view(p, 0.26, 0.66, seed=29, clouds_=False, sign_at=0.18, sign_s=1.35)
        rybar(p.X(0.36), p.Y(0.03), 1.1, mood="talk", right="hold", look=(1, 0))
        alica(p.X(0.78), p.Y(0.03), 1.32, flip=True, mood="surprised", look=(1, 0.3))
        hidden_star(p.X(0.92), p.Y(0.9))
        say(p, "Samé díry! A ráno tu někdo svítí a straší ryby.", *hd("rybar", p.X(0.36), p.Y(0.03), 1.1), w=250)
        say(p, "Svítí? Kdo?", *hd("alica", p.X(0.78), p.Y(0.03), 1.32), w=130)
        say(p, "To já nevím. Ráno spím.", *hd("rybar", p.X(0.36), p.Y(0.03), 1.1), w=140)
    page_end()


# =================================================================== 11 quarrel (script 10)
def page_quarrel():
    R = rows([(250, [1]), (240, [0.5, 0.5]), (260, [0.5, 0.5])])
    with Pn(*R[0]) as p:
        kitchen(p, evening=True)
        notebook_big(p.X(0.44), p.Y(0.42), p.w*0.52, p.h*0.5, "PODEZŘELÍ:",
                     ["1. Tonda: lopatka, bláto,", "    utekl!", "2. jezevec: hrabe"])
        alica(p.X(0.22), p.Y(0.03), 1.32, mood="determined", right="point", look=(1, 0.3))
        cap(p, "Večer v kuchyni.", w=150)
        say(p, "Je to jasné. Byl to Tonda!", *hd("alica", p.X(0.22), p.Y(0.03), 1.32), w=170)
    with Pn(*R[1]) as p:
        kitchen(p, table=False, evening=True)
        alica(p.X(0.25), p.Y(0.03), 1.28, mood="determined", right="hip", look=(1, 0))
        hanka(p.X(0.72), p.Y(0.03), 1.28, flip=True, mood="determined", look=(1, 0))
        say(p, "Měl lopatku a utekl!", *hd("alica", p.X(0.25), p.Y(0.03), 1.28), w=140)
        say(p, "Tonda je hodný! On to nebyl!", *hd("hanka", p.X(0.72), p.Y(0.03), 1.28), w=140)
    with Pn(*R[2]) as p:
        kitchen(p, table=False, evening=True)
        alica(p.X(0.28), p.Y(0.03), 1.28, flip=True, mood="sad", right="hip", look=(1, 0))
        hanka(p.X(0.7), p.Y(0.03), 1.28, mood="sad", look=(1, -0.5))
        say(p, "Ty tomu nerozumíš. Jsi malá.", *hd("alica", p.X(0.28), p.Y(0.03), 1.28), w=150)
        say(p, "Nejsem!", *hd("hanka", p.X(0.7), p.Y(0.03), 1.28), w=90)
    with Pn(*R[3]) as p:
        kitchen(p, table=False, evening=True)
        alica(p.X(0.16), p.Y(0.03), 1.14, mood="sad", look=(1, 0.5))
        hanka(p.X(0.84), p.Y(0.03), 1.14, flip=True, mood="sad", look=(1, 0.5))
        deda(p.X(0.5), p.Y(0.03), 1.14, mood="happy", left="front", right="front", look=(0, -0.3))
        say(p, "Víte, co říkala Věrka? Klub Hvězdička drží spolu.", *hd("deda", p.X(0.5), p.Y(0.03), 1.14), w=190)
        say(p, "Jeden detektiv nevidí všechno. Dva vidí víc.", *hd("deda", p.X(0.5), p.Y(0.03), 1.14), w=150)
    with Pn(*R[4]) as p:
        kitchen(p, table=False, evening=True)
        alica(p.X(0.25), p.Y(0.03), 1.14, mood="happy", right="front", look=(1, 0))
        hanka(p.X(0.65), p.Y(0.03), 1.14, flip=True, mood="grin", look=(1, 0))
        say(p, "Promiň, Hanko.", *hd("alica", p.X(0.25), p.Y(0.03), 1.14), w=100, area=(0.0, 0.4))
        say(p, "Tak ráno zjistíme, co Tonda kopal. Spolu!", *hd("hanka", p.X(0.65), p.Y(0.03), 1.14), w=145, area=(0.4, 1.0))
    page_end()


# =================================================================== 12 stakeout at dawn (script 11)
DAWN = 0.82


def page_stakeout():
    R = rows([(265, [1]), (240, [0.5, 0.5]), (255, [1])])
    with Pn(*R[0]) as p:
        pond_view(p, 0.28, 0.62, seed=32, sky_g=DAWN, clouds_=False)
        hanka(p.X(0.3), p.Y(0.03), 1.28, mood="whisper", torch=True, right="lens", look=(1, 0))
        alica(p.X(0.45), p.Y(0.03), 1.32, mood="whisper", right="hush", look=(1, 0))
        deda(p.X(0.6), p.Y(0.03), 1.19, mood="whisper", look=(1, 0))
        for k_ in range(12): reeds(p.X(0.18) + k_*22, p.Y(0.02), 1.6, seed=40 + k_, n=6)
        mist(p, 3, 0.4)
        cap(p, "Druhý den za svítání. Detektivky drží hlídku.", w=240)
        say(p, "Mám baterku.", *hd("hanka", p.X(0.3), p.Y(0.03), 1.28), whisper=True, w=120)
        say(p, "Ještě nesviť!", *hd("alica", p.X(0.45), p.Y(0.03), 1.32), whisper=True, w=140)
    with Pn(*R[1]) as p:
        pond_view(p, 0.26, 0.66, seed=33, sky_g=DAWN, clouds_=False)
        mist(p, 3, 0.5, seed=4)
        tonda(p.X(0.62), p.Y(0.22), 1.0, mood="happy", legs="walk", look=(1, 0), shadow=False,
              item=lambda x, y: spade(x, y - 30, 0.8, rot=15))
        bg_fill(p, DAWN, 0.35)
        say(p, "Někdo jde…", p.X(0.1), p.Y(0.2), whisper=True, w=140)
    with Pn(*R[2]) as p:
        pond_view(p, 0.26, 0.66, seed=34, sky_g=DAWN, clouds_=False)
        willow(p.X(0.75), p.Y(0.2), 0.7, seed=35)
        tonda(p.X(0.6), p.Y(0.06), 1.3, mood="happy", right="hold", look=(1, -1),
              item=lambda x, y: spade(x + 4, y - 30, 0.9, rot=-10))
        mist(p, 2, 0.35, seed=6)
        say(p, "To je Tonda!", p.X(0.12), p.Y(0.1), whisper=True, w=130)
    with Pn(*R[3]) as p:
        pond_view(p, 0.26, 0.66, seed=36, sky_g=DAWN, clouds_=False)
        hx, hy = p.X(0.2), p.Y(0.03)
        torch_beam(hx + 22, hy + 70, p.X(0.62), p.Y(0.95), p.X(0.95), p.Y(0.05), 0.55)
        hanka(hx, hy, 1.5, mood="determined", torch=True, right="point", look=(1, 0))
        alica(p.X(0.36), p.Y(0.03), 1.36, mood="grin", right="point", look=(1, 0))
        tonda(p.X(0.78), p.Y(0.06), 1.4, flip=True, mood="surprised", left="up", right="up", look=(1, 0))
        shoebox(p.X(0.9), p.Y(0.05), 0.8, open_=False)
        sfx(p.X(0.05), p.Y(0.85), "CVAK!", 22, 8)
        say(p, "Máme tě!", *hd("alica", p.X(0.36), p.Y(0.03), 1.36), w=120)
        say(p, "Aaa!", *hd("tonda", p.X(0.78), p.Y(0.06), 1.4), w=90)
    page_end()


# =================================================================== 13 Tonda's secret (script 12)
def page_secret():
    R = rows([(240, [0.5, 0.5]), (225, [1]), (290, [0.62, 0.38])])
    with Pn(*R[0]) as p:
        pond_view(p, 0.24, 0.66, seed=37, clouds_=False)
        alica(p.X(0.24), p.Y(0.03), 1.28, mood="determined", look=(1, 0))
        tonda(p.X(0.72), p.Y(0.03), 1.23, flip=True, mood="sad", right="front", look=(1, 0),
              item=lambda x, y: shoebox(x - 4, y - 14, 0.55, open_=False))
        say(p, "Tak cos tu kopal, Tondo?", *hd("alica", p.X(0.24), p.Y(0.03), 1.28), w=140)
        say(p, "Zakopávám svůj poklad.", *hd("tonda", p.X(0.72), p.Y(0.03), 1.23), w=140)
    with Pn(*R[1]) as p:
        bg_fill(p, P.MUD)
        shoebox(p.X(0.5), p.Y(0.06), 2.8, open_=True)
        say(p, "Slyšel jsem vás přes plot. O klubu a o pokladu.", p.X(0.95), p.Y(0.2), w=160)
        say(p, "Chtěl jsem mít taky klub. Jenže jsem sám.", p.X(0.97), p.Y(0.15), w=160)
    with Pn(*R[2]) as p:
        pond_view(p, 0.24, 0.66, seed=38, clouds_=False)
        hanka(p.X(0.16), p.Y(0.03), 1.19, mood="grin", right="up", look=(1, 0))
        alica(p.X(0.42), p.Y(0.03), 1.23, mood="sad", look=(1, 0))
        tonda(p.X(0.82), p.Y(0.03), 1.14, flip=True, mood="happy", look=(1, 0))
        say(p, "Já říkala, že Tonda je hodný!", *hd("hanka", p.X(0.16), p.Y(0.03), 1.19), w=190)
        say(p, "Promiň, Tondo. Myslela jsem, žes vzal náš poklad.", *hd("alica", p.X(0.42), p.Y(0.03), 1.23), w=260)
    with Pn(*R[3]) as p:
        pond_view(p, 0.22, 0.66, seed=39, clouds_=False)
        tonda(p.X(0.24), p.Y(0.03), 1.14, mood="talk", right="point", look=(1, 0))
        alica(p.X(0.8), p.Y(0.03), 1.23, flip=True, mood="wow", book=True, look=(1, 0))
        say(p, "Váš poklad? Ten jsem nevzal.", *hd("tonda", p.X(0.24), p.Y(0.03), 1.14), w=118, area=(0.0, 0.38))
        say(p, "Ale minulou neděli ráno jsem šel s tátou pro rohlíky. A u vrby svítilo světýlko!", *hd("tonda", p.X(0.24), p.Y(0.03), 1.14), w=185, area=(0.38, 1.0))
        say(p, "Stopa č. 4!", *hd("alica", p.X(0.8), p.Y(0.03), 1.23), w=110)
    with Pn(*R[4]) as p:
        pond_view(p, 0.22, 0.66, seed=40, clouds_=False)
        hanka(p.X(0.25), p.Y(0.03), 1.14, mood="happy", right="front", look=(1, 0))
        tonda(p.X(0.72), p.Y(0.03), 1.1, flip=True, mood="grin", right="up", look=(1, 0))
        say(p, "Pomůžeš nám hledat?", *hd("hanka", p.X(0.25), p.Y(0.03), 1.14), w=120)
        say(p, "Jasně!", *hd("tonda", p.X(0.72), p.Y(0.03), 1.1), w=80)
    page_end()


# =================================================================== 14 who it wasn't (script 13)
def page_cleared():
    R = rows([(240, [1]), (290, [0.42, 0.58]), (230, [1])])
    with Pn(*R[0]) as p:
        pond_view(p, 0.26, 0.66, seed=41, clouds_=False)
        burrow(p.X(0.5), p.Y(0.05), 0.8)
        badger_track(p.X(0.4), p.Y(0.1), 1.3); badger_track(p.X(0.6), p.Y(0.12), 1.3, rot=10)
        babicka(p.X(0.18), p.Y(0.03), 1.19, mood="happy", right="point", look=(1, -0.3))
        alica(p.X(0.72), p.Y(0.03), 1.23, flip=True, mood="surprised", look=(1, 0.3))
        hanka(p.X(0.84), p.Y(0.03), 1.14, flip=True, mood="happy", look=(1, 0.3))
        tonda(p.X(0.95), p.Y(0.03), 1.1, flip=True, mood="happy", look=(1, 0.3))
        hidden_star(p.X(0.3), p.Y(0.1))
        say(p, "Jezevec? Ten hledá žížaly. Plechovku by neodnesl.", *hd("babi", p.X(0.18), p.Y(0.03), 1.19), w=240)
        say(p, "A kolem jeho nory jsou stopy s drápky.", *hd("babi", p.X(0.18), p.Y(0.03), 1.19), w=230)
    with Pn(*R[1]) as p:
        bg_fill(p, P.GRASS)
        mud_patch(p.X(0.55), p.Y(0.14), p.w*0.42, 26)
        bird_track(p.X(0.45), p.Y(0.1), 2.0); bird_track(p.X(0.55), p.Y(0.16), 2.0, rot=10)
        stick_dot(p.X(0.72), p.Y(0.1), 3.4); stick_dot(p.X(0.82), p.Y(0.17), 3.4)
        hanka(p.X(0.18), p.Y(0.03), 1.23, mood="determined", right="point", look=(1, -1))
        alica(p.X(0.88), p.Y(0.2), 1.1, flip=True, mood="wow", look=(1, -0.5), shadow=False)
        say(p, "Ptáček má nožičky jako vidličky.", *hd("hanka", p.X(0.18), p.Y(0.03), 1.23), w=140)
        say(p, "Ale tyhle dírky jsou kulaté!", *hd("hanka", p.X(0.18), p.Y(0.03), 1.23), w=140)
        say(p, "Takže to nebyl ptáček. Hanko, to je důležité!", *hd("alica", p.X(0.88), p.Y(0.2), 1.1), w=125)
    with Pn(*R[2]) as p:
        pond_view(p, 0.2, 0.7, seed=42, clouds_=False)
        boot_print(p.X(0.45), p.Y(0.08), 1.1, 90)
        alica(p.X(0.16), p.Y(0.03), 0.97, mood="think", book=True, look=(1, 0))
        rybar(p.X(0.78), p.Y(0.03), 0.79, flip=True, mood="talk", look=(1, 0), rod=False)
        say(p, "Pane rybáři, nebyl jste tu minulou neděli ráno?", *hd("alica", p.X(0.16), p.Y(0.03), 0.97), w=145, area=(0.0, 0.5))
        say(p, "Ráno spím. Na ryby chodím odpoledne.", *hd("rybar", p.X(0.78), p.Y(0.03), 0.79), w=140, area=(0.5, 1.0))
        say(p, "A moje holinky jsou obří. Podívej!", *hd("rybar", p.X(0.78), p.Y(0.03), 0.79), w=122, area=(0.28, 0.7))
    with Pn(*R[3]) as p:
        bg_fill(p, 0.9)
        notebook_big(p.X(0.08), p.Y(0.08), p.w*0.56, p.h*0.8, "PODEZŘELÍ:", ["Tonda", "jezevec", "ptáček", "rybář"])
        for i in range(4):
            yy = p.Y(0.08) + p.h*0.8 - 24 - (i+1)*19 + 5
            stroke([(p.X(0.08) + 26, yy), (p.X(0.08) + 26 + [48, 62, 56, 44][i], yy + 2)], 2.2, g=P.TAG_STAR)
        alica(p.X(0.8), p.Y(0.03), 1.14, flip=True, mood="worried", right="chin", look=(1, 0))
        say(p, "Tak kdo to byl?!", *hd("alica", p.X(0.8), p.Y(0.03), 1.14), w=120)
    page_end()


# =================================================================== 15 Joey's nose (script 14)
def page_nose():
    R = rows([(200, [1]), (255, [1]), (300, [0.56, 0.44])])
    with Pn(*R[0]) as p:
        pond_view(p, 0.26, 0.7, seed=43, clouds_=False)
        hole(p.X(0.62), p.Y(0.05), 40, 10, tin_print=False)
        joey(p.X(0.72), p.Y(0.05), 1.3, pose="sniff", mood="calm", flip=True)
        tonda(p.X(0.2), p.Y(0.03), 0.97, mood="wow", right="point", look=(1, -0.5))
        sfx(p.X(0.82), p.Y(0.6), "ČMUCH ČMUCH", 14, -6)
        say(p, "Joey něco čmuchá!", *hd("tonda", p.X(0.2), p.Y(0.03), 0.97), w=160)
    with Pn(*R[1]) as p:
        fy = pond_view(p, 0.28, 0.7, seed=44, mill_at=0.84, mill_s=0.55, lantern_=True, clouds_=False)
        bench(p.X(0.8), p.Y(0.3), 0.67)
        seated(verka_old, "verka", p.X(0.8), p.Y(0.3) + 23*0.67, 0.55, P.STOCKINGS, P.BABI_SHOES, P.VERKA_COAT, edge=5,
               mood="happy", right="front", stick=False)
        walking_stick(p.X(0.8) + 34, p.Y(0.3), 30, rot=16)
        duck(p.X(0.66), p.Y(0.35), 0.6); duck(p.X(0.7), p.Y(0.4), 0.5, flip=True)
        path_pts = [(p.X(0.1), p.Y(0.08)), (p.X(0.3), p.Y(0.14)), (p.X(0.5), p.Y(0.2)), (p.X(0.7), p.Y(0.26))]
        for (x0, y0), (x1, y1) in zip(path_pts, path_pts[1:]):
            for t in (0.2, 0.5, 0.8):
                fill(ell(x0 + (x1 - x0)*t, y0 + (y1 - y0)*t, 2.2, 1.4, 10), P.MUD_DARK)
        joey(p.X(0.56), p.Y(0.2), 0.8, pose="sniff", mood="calm")
        alica(p.X(0.3), p.Y(0.06), 1.0, mood="surprised", legs="walk", look=(1, 0.3))
        hanka(p.X(0.18), p.Y(0.04), 0.95, mood="happy", legs="walk", look=(1, 0.3))
        tonda(p.X(0.42), p.Y(0.1), 0.95, mood="happy", legs="walk", look=(1, 0.3))
        hidden_star(p.X(0.12), p.Y(0.92))
    with Pn(*R[2]) as p:
        pond_view(p, 0.3, 0.8, seed=45, clouds_=False)
        mill(p.X(0.76), p.Y(0.3), 1.25, lantern_=True, wheel=False)
        bench(p.X(0.5), p.Y(0.04), 1.5)
        walking_stick(p.X(0.5) + 70, p.Y(0.04), 62, rot=16)
        seated(verka_old, "verka", p.X(0.5), p.Y(0.04) + 23*1.5, 1.22, P.STOCKINGS, P.BABI_SHOES, P.VERKA_COAT, edge=5,
               mood="grin", right="point", stick=False, look=(-1, -0.5),
               item=lambda x, y: shape(rrect(x - 3, y - 2, 7, 4, 1.5), P.SHOEBOX, 0.7))
        joey(p.X(0.18), p.Y(0.04), 1.3, mood="happy")
        say(p, "Ty jsi ale krásný pejsek! Na, máš piškot.", *hd("verka", p.X(0.5), p.Y(0.04) + 23*1.5 - 50*1.22, 1.22), w=p.w*0.56)
    with Pn(*R[3]) as p:
        pond_view(p, 0.26, 0.7, seed=46, clouds_=False)
        alica(p.X(0.24), p.Y(0.03), 1.14, mood="sad", look=(1, 0))
        tonda(p.X(0.75), p.Y(0.03), 1.1, flip=True, mood="grin", look=(1, 0))
        say(p, "Joey nic nenašel. Jen chtěl dobrotu.", *hd("alica", p.X(0.24), p.Y(0.03), 1.14), w=145)
        say(p, "Tak to je typický Joey.", *hd("tonda", p.X(0.75), p.Y(0.03), 1.1), w=140)
    page_end()


# =================================================================== 16 dead end (script 15)
def page_deadend():
    R = rows([(225, [1]), (310, [0.5, 0.5]), (225, [1])])
    with Pn(*R[0]) as p:
        fy = pond_view(p, 0.12, 0.66, seed=47, clouds_=False)
        jetty(p.X(0.18), p.X(0.86), p.Y(0.3))
        for fn, who, xx, s_k, lg, bg_ in ((alica, "alica", 0.32, 1.25, P.TIGHTS, P.ALICA_BOOTS),
                                          (hanka, "hanka", 0.45, 1.2, P.DUNGAREES, P.HANKA_BOOTS),
                                          (tonda, "tonda", 0.58, 1.2, P.JEANS, 1.0)):
            seated(fn, who, p.X(xx), p.Y(0.3), s_k, lg, bg_, mood="sad", look=(0, -0.5), drop=18, edge=12)
        joey(p.X(0.73), p.Y(0.3), 0.9, mood="sleepy", shadow=False)
        cap(p, "Detektivové jsou v koncích.", w=220)
    with Pn(*R[1]) as p:
        pond_view(p, 0.22, 0.7, seed=48, clouds_=False)
        tonda(p.X(0.25), p.Y(0.03), 1.14, mood="think", right="chin", look=(1, 0))
        alica(p.X(0.75), p.Y(0.03), 1.19, flip=True, mood="think", look=(1, 0))
        say(p, "Kdo vůbec věděl, kde poklad je?", *hd("tonda", p.X(0.25), p.Y(0.03), 1.14), w=150)
        say(p, "Jen Klub Hvězdička. Děda, Franta a Věrka.", *hd("alica", p.X(0.75), p.Y(0.03), 1.19), w=150)
    with Pn(*R[2]) as p:
        pond_view(p, 0.22, 0.7, seed=49, clouds_=False)
        hanka(p.X(0.25), p.Y(0.03), 1.28, mood="grin", right="up", look=(1, 0))
        alica(p.X(0.75), p.Y(0.03), 1.23, flip=True, mood="happy", look=(1, -0.3))
        say(p, "Tak to byla Věrka!", *hd("hanka", p.X(0.25), p.Y(0.03), 1.28), w=140)
        say(p, "Věrka bydlí daleko ve městě, Hanko.", *hd("alica", p.X(0.75), p.Y(0.03), 1.23), w=150)
    with Pn(*R[3]) as p:
        pond_view(p, 0.22, 0.7, seed=50, clouds_=False)
        alica(p.X(0.72), head_y(p, 0.5, 89.8, 2.4), 2.4, mood="think", right="chin", look=(-1, 0.5), shadow=False)
        say(p, "A Franta taky… Hm.", p.X(0.62), p.Y(0.62), w=p.w*0.45)
    page_end()


# =================================================================== 17 STOP, DETEKTIVE!
def page_stop():
    with Pn(M, 40, W-2*M, H-80, bg=0.95) as p:
        title(p.X(0.5), p.Y(0.92), "STOP, DETEKTIVE!", 44)
        hand_text(p.X(0.05), p.Y(0.86), p.w*0.9, "Už máš všechny stopy.", "SHB", 18)
        cw, ch = p.w*0.3, p.h*0.215
        items = [
            ("díra je znovu zasypaná", lambda x, y: hole(x, y + 14, 30, 8)),
            ("velké boty", lambda x, y: (boot_print(x - 12, y + 24, 1.1, -8), boot_print(x + 14, y + 30, 1.1, 6))),
            ("kulaté dírky – ptáček to nebyl", lambda x, y: (stick_dot(x - 20, y + 20, 3.4), stick_dot(x, y + 32, 3.4), bird_track(x + 26, y + 16, 1.4))),
            ("světýlko u vrby minulou neděli ráno", lambda x, y: (willow(x - 14, y, 0.4, seed=3), lantern(x + 28, y + 2, 0.9, glow=True))),
            ("Joeyho stopa vede k lavičce u mlýna", lambda x, y: (bench(x + 24, y, 0.5), joey(x - 22, y, 0.62, pose="sniff"))),
            ("cedule: BAGRY OD PONDĚLÍ", lambda x, y: dredge_sign(x, y - 4, 0.9)),
        ]
        for i, (txt, pic) in enumerate(items):
            cx = p.X(0.04) + (i % 3)*(cw + p.w*0.02); cy = p.Y(0.82) - (i//3 + 1)*(ch + 10)
            shape(rrect(cx, cy, cw, ch, 8), 1.0, 1.2)
            hand_text(cx + 6, cy + ch - 20, 30, str(i + 1), "SHB", 16, align="left")
            with T(cx + cw/2, cy + 38, 1.45):
                pic(0, 0)
            hand_text(cx + 8, cy + 18, cw - 16, txt, "SH", 10.5)
        by = p.Y(0.82) - 2*(ch + 10) - 70
        shape(rrect(p.X(0.04), by, p.w*0.92, 60, 8), 1.0, 1.2)
        hand_text(p.X(0.06), by + 36, 30, "7", "SHB", 16, align="left")
        hand_text(p.X(0.12), by + 36, p.w*0.82, "Poklad vykopal jen ten, kdo věděl, kde je.", "SH", 14, align="left")
        magnifier(p.X(0.9), by + 30, ang=-30, r=12)
        hand_text(p.X(0.05), by - 34, p.w*0.9, "Kdo vykopal poklad? A proč?", "SHB", 24)
        hand_text(p.X(0.05), by - 58, p.w*0.9, "Nápověda: prohlédni si znovu strany 4 a 15.", "SH", 14)
        with T(p.X(0.5), p.Y(0.06), 1.0, rot=180):
            hand_text(-p.w*0.45, 0, p.w*0.9, "Paní od mlýna! Chodí s hůlkou a má lucernu. Bála se bagrů.", "SH", 12)
            hand_text(-p.w*0.45, -15, p.w*0.9, "Ale kdo to je? Otoč na další stranu!", "SH", 12)
    page_end()


# =================================================================== 18 Hanka tries (script 17)
def page_hanka():
    R = rows([(250, [0.42, 0.58]), (245, [0.45, 0.55]), (260, [1])])
    with Pn(*R[0]) as p:
        pond_view(p, 0.22, 0.7, seed=51, clouds_=False)
        jetty(p.X(-0.1), p.X(0.5), p.Y(0.3))
        alica(p.X(0.25), p.Y(0.3) - 2, 1.2, mood="surprised", look=(1, 0), shadow=False)
        hanka(p.X(0.72), p.Y(0.03), 1.14, mood="determined", legs="walk", look=(1, 0))
        say(p, "Kam jdeš?", *hd("alica", p.X(0.25), p.Y(0.3) - 2, 1.2), w=100)
        say(p, "Za tou paní. Je hodná.", *hd("hanka", p.X(0.72), p.Y(0.03), 1.14), w=130)
    with Pn(*R[1]) as p:
        pond_view(p, 0.26, 0.76, seed=52, clouds_=False)
        bench(p.X(0.72), p.Y(0.04), 1.45)
        seated(verka_old, "verka", p.X(0.72), p.Y(0.04) + 23*1.45, 1.2, P.STOCKINGS, P.BABI_SHOES, P.VERKA_COAT, edge=5,
               flip=True, mood="happy", stick=False, look=(1, -0.5))
        walking_stick(p.X(0.72) + 68, p.Y(0.04), 60, rot=16)
        hanka(p.X(0.3), p.Y(0.03), 1.28, mood="grin", look=(1, 0.3))
        say(p, "Paní, nechcete s námi hledat poklad?", *hd("hanka", p.X(0.3), p.Y(0.03), 1.28), w=170)
        say(p, "Jsme Klub Hvězdička!", *hd("hanka", p.X(0.3), p.Y(0.03), 1.28), w=140)
    with Pn(*R[2]) as p:
        bg_fill(p, 1.0); rays(p, p.X(0.5), p.Y(0.45), 0.9)
        verka_old(p.X(0.5), head_y(p, 0.45, 103, 2.4), 2.4, mood="surprised", right="chin", stick=False, look=(0, 0), shadow=False)
        say(p, "Klub… Hvězdička?", p.X(0.45), p.Y(0.6), w=p.w*0.8)
    with Pn(*R[3]) as p:
        bg_fill(p, 0.93)
        verka_old(p.X(0.72), head_y(p, 0.45, 103, 2.2), 2.2, mood="closed", stick=False, look=(0, 0), shadow=False)
        say(p, "„Od hvězdičky sedm prken, pod prknem, které zpívá…“", p.X(0.6), p.Y(0.55), whisper=True, w=p.w*0.62)
    with Pn(*R[4]) as p:
        pond_view(p, 0.24, 0.7, seed=53, clouds_=False)
        bench(p.X(0.84), p.Y(0.04), 1.35)
        seated(verka_old, "verka", p.X(0.84), p.Y(0.04) + 23*1.35, 1.1, P.STOCKINGS, P.BABI_SHOES, P.VERKA_COAT, edge=5,
               flip=True, mood="surprised", stick=False, look=(1, 0))
        hanka(p.X(0.62), p.Y(0.03), 1.14, mood="happy", look=(-1, 0), flip=True)
        alica(p.X(0.2), p.Y(0.03), 1.28, mood="wow", legs="walk", look=(1, 0))
        tonda(p.X(0.36), p.Y(0.03), 1.14, mood="surprised", legs="walk", look=(1, 0))
        say(p, "Tu hádanku zná jen… Věrka!", *hd("alica", p.X(0.2), p.Y(0.03), 1.28), w=250)
    page_end()


# =================================================================== 19 Věrka (script 18)
def page_verka():
    R = rows([(245, [0.5, 0.5]), (245, [0.5, 0.5]), (270, [0.5, 0.5])])
    with Pn(*R[0]) as p:
        pond_view(p, 0.24, 0.72, seed=54, clouds_=False)
        verka_old(p.X(0.25), p.Y(0.03), 1.14, mood="wow", right="up", look=(1, 0))
        deda(p.X(0.75), p.Y(0.03), 1.14, flip=True, mood="surprised", legs="walk", look=(1, 0))
        cap(p, "Tonda běžel pro dědu.", w=170)
        say(p, "Honzo?!", *hd("verka", p.X(0.25), p.Y(0.03), 1.14), w=90)
        say(p, "Věrko?!", *hd("deda", p.X(0.75), p.Y(0.03), 1.14), w=90)
    with Pn(*R[1]) as p:
        bg_fill(p, 1.0); rays(p, p.X(0.5), p.Y(0.5), 0.9)
        deda(p.X(0.42), p.Y(0.03), 1.28, mood="laugh", right="hug", left="hug", look=(1, 0))
        verka_old(p.X(0.6), p.Y(0.03), 1.19, flip=True, mood="laugh", right="hug", left="hug", stick=False, look=(1, 0))
        hanka(p.X(0.12), p.Y(0.03), 0.97, mood="grin", right="up")
        joey(p.X(0.86), p.Y(0.03), 0.9, flip=True, mood="happy")
        say(p, "Tolik let!", *hd("deda", p.X(0.42), p.Y(0.03), 1.28), w=110)
    with Pn(*R[2]) as p:
        pond_view(p, 0.24, 0.72, seed=55, mill_at=0.2, mill_s=0.55, clouds_=False)
        verka_old(p.X(0.28), p.Y(0.03), 1.14, mood="happy", right="point", look=(1, 0))
        alica(p.X(0.76), p.Y(0.03), 1.23, flip=True, mood="surprised", look=(1, 0))
        say(p, "Letos jsem se vrátila. Bydlím tady ve mlýnku.", *hd("verka", p.X(0.28), p.Y(0.03), 1.14), w=170)
        say(p, "Tak vy jste vykopala poklad?", *hd("alica", p.X(0.76), p.Y(0.03), 1.23), w=125)
    with Pn(*R[3]) as p:
        pond_view(p, 0.2, 0.7, seed=56, clouds_=False)
        dredge_sign(p.X(0.8), p.Y(0.02), 1.7)
        verka_old(p.X(0.28), p.Y(0.03), 1.1, mood="worried", right="chin", look=(1, 0.5))
        memory_frame(p)
        cap(p, "Věrka uviděla ceduli s bagry.", w=190)
        say(p, "Bála jsem se, že bagr poklad rozbije.", *hd("verka", p.X(0.28), p.Y(0.03), 1.1), w=150)
    with Pn(*R[4]) as p:
        pond_view(p, 0.22, 0.7, seed=57, sky_g=DAWN, clouds_=False)
        willow(p.X(0.82), p.Y(0.2), 0.6, seed=3)
        stump(p.X(0.14), p.Y(0.06), 0.6)
        lantern(p.X(0.72), p.Y(0.06), 1.1, glow=True)
        verka_old(p.X(0.45), p.Y(0.04), 1.25, mood="determined", right="hold", look=(1, -1),
                  item=lambda x, y: spade(x + 10, y - 28, 1.0, rot=-20))
        treasure_tin(p.X(0.6), p.Y(0.04), 0.5)
        mist(p, 2, 0.35)
        memory_frame(p)
        cap(p, "Minulou neděli za svítání vzala lucernu, hůlku a lopatu.", w=p.w - 30)
    with Pn(*R[5]) as p:
        pond_view(p, 0.22, 0.72, seed=58, clouds_=False)
        alica(p.X(0.24), p.Y(0.03), 1.19, mood="think", look=(1, 0))
        verka_old(p.X(0.74), p.Y(0.03), 1.1, flip=True, mood="happy", right="front", look=(1, 0))
        say(p, "A proč jste plechovku neotevřela?", *hd("alica", p.X(0.24), p.Y(0.03), 1.19), w=150)
        say(p, "Poklad smí otevřít jen celý klub. Tak jsem čekala.", *hd("verka", p.X(0.74), p.Y(0.03), 1.1), w=155)
    page_end()


# =================================================================== 20 the treasure (script 19)
def mill_room(p):
    bg_fill(p, P.MILL_WALL)
    for yy in range(int(p.Y(0.4)), int(p.y + p.h), 30): stroke([(p.x, yy), (p.x + p.w, yy)], BG*0.4, g=0.8)
    shape([(p.x - 5, p.y - 5), (p.x + p.w + 5, p.y - 5), (p.x + p.w + 5, p.Y(0.28)), (p.x - 5, p.Y(0.28))], 0.72, BG)
    shape([(p.X(0.08), p.Y(0.28)), (p.X(0.92), p.Y(0.28)), (p.X(0.92), p.Y(0.32)), (p.X(0.08), p.Y(0.32))], P.TABLE, BG)


def page_treasure():
    R = rows([(178, [1]), (212, [1]), (195, [0.5, 0.5]), (165, [1])])
    with Pn(*R[0]) as p:
        mill_room(p)
        lantern(p.X(0.94), p.Y(0.32), 0.8)
        treasure_tin(p.X(0.5), p.Y(0.32), 1.15, open_=True)
        alica(p.X(0.1), p.Y(0.03), 0.79, mood="wow", look=(1, 0.3))
        deda(p.X(0.27), p.Y(0.03), 0.75, mood="grin", right="front", look=(1, 0))
        tonda(p.X(0.63), p.Y(0.03), 0.75, flip=True, mood="wow", look=(1, 0))
        verka_old(p.X(0.76), p.Y(0.03), 0.72, flip=True, mood="grin", right="front", stick=False, look=(1, 0))
        hanka(p.X(0.9), p.Y(0.03), 0.79, flip=True, mood="wow")
        cap(p, "Plechovku otvírá celý klub.", w=190)
        say(p, "Tak… raz, dva, tři!", *hd("deda", p.X(0.27), p.Y(0.03), 0.75), w=150)
        sfx(p.X(0.55), p.Y(0.62), "SKŘÍP!", 20, -6)
    with Pn(*R[1]) as p:
        mill_room(p)
        coin(p.X(0.5), p.Y(0.3), 28, shine=True)
        keep_clear(p, p.X(0.5) - 50, p.Y(0.3) - 50, p.X(0.5) + 50, p.Y(0.3) + 50, "coin")
        alica(p.X(0.12), p.Y(0.03), 0.92, mood="wow", right="up", look=(1, 0.3))
        deda(p.X(0.88), p.Y(0.03), 0.84, flip=True, mood="happy", look=(1, 0))
        say(p, "Pravá stříbrná mince!", *hd("alica", p.X(0.12), p.Y(0.03), 0.92), w=120, area=(0.0, 0.24))
        say(p, "Stříbrný tolar. Našli jsme ho v bahně, když vypustili rybník. Je moc vzácný. Ale poklad klubu se neprodává.",
            *hd("deda", p.X(0.88), p.Y(0.03), 0.84), w=330, area=(0.3, 1.0))
    with Pn(*R[2]) as p:
        mill_room(p)
        verka_old(p.X(0.18), p.Y(0.03), 0.53, mood="happy", right="point", stick=False, look=(1, 0))
        tonda(p.X(0.8), p.Y(0.03), 0.55, flip=True, mood="grin", right="up", look=(1, 0.3),
              item=lambda x, y: spyglass(x - 8, y + 2, 0.4, rot=15))
        say(p, "Dalekohled po mém tátovi. Koukali jsme s ním na hvězdy.", *hd("verka", p.X(0.18), p.Y(0.03), 0.53), w=185)
        say(p, "Vidím až na mlýn!", *hd("tonda", p.X(0.8), p.Y(0.03), 0.55), w=100)
    with Pn(*R[3]) as p:
        bg_fill(p, P.TABLE)
        club_photo(p.X(0.3), p.Y(0.08), 110, 82, rot=-4)
        say(p, "To jste vy?", p.X(0.12), p.Y(0.0), w=90, area=(0.0, 0.4))
        say(p, "Honza, Franta a já.", p.X(0.95), p.Y(0.0), w=100, area=(0.6, 1.0))
    with Pn(*R[4]) as p:
        mill_room(p)
        hanka(p.X(0.07), p.Y(0.03), 0.66, mood="wow", right="up", look=(1, 0.3))
        picture_letter(p.X(0.13), p.Y(0.06), 0.85, rot=-4)
        keep_clear(p, p.X(0.13), p.Y(0.06), p.X(0.13) + 78, p.Y(0.06) + 56, "letter")
        verka_old(p.X(0.62), p.Y(0.03), 0.48, flip=True, mood="happy", stick=False, look=(1, 0))
        deda(p.X(0.9), p.Y(0.03), 0.46, flip=True, mood="think", right="chin", look=(1, 0))
        say(p, "A tady je obrázek!", *hd("hanka", p.X(0.07), p.Y(0.03), 0.66), w=100, area=(0.0, 0.2))
        say(p, "To nakreslil Franta. Byl nejmenší. Psát ještě neuměl.", *hd("verka", p.X(0.62), p.Y(0.03), 0.48), w=185, area=(0.2, 0.56))
        say(p, "Franta říkal, že má svůj vlastní poklad. Nikdy neprozradil kde.", *hd("deda", p.X(0.9), p.Y(0.03), 0.46), w=228, area=(0.56, 1.0))
    page_end()


# =================================================================== 21 a bigger club (script 20)
def page_club():
    R = rows([(230, [0.5, 0.5]), (225, [0.5, 0.5]), (300, [1])])
    with Pn(*R[0]) as p:
        pond_view(p, 0.22, 0.72, seed=59, clouds_=False)
        verka_old(p.X(0.28), p.Y(0.03), 1.1, mood="happy", right="front", stick=False, look=(1, 0),
                  item=lambda x, y: badge(x + 4, y + 2, 5))
        tonda(p.X(0.76), p.Y(0.03), 1.14, flip=True, mood="wow", look=(1, 0))
        say(p, "A tenhle odznak je pro nového člena.", *hd("verka", p.X(0.28), p.Y(0.03), 1.1), w=150)
        say(p, "Čekal tu na tebe, Tondo.", *hd("verka", p.X(0.28), p.Y(0.03), 1.1), w=130)
    with Pn(*R[1]) as p:
        bg_fill(p, 1.0); rays(p, p.X(0.5), p.Y(0.45), 0.9)
        tonda(p.X(0.5), p.Y(0.03), 1.41, mood="laugh", left="up", right="up")
        badge(p.X(0.5) - 6, p.Y(0.03) + 70*1.6, 6)
        hidden_star(p.X(0.9), p.Y(0.2))
        say(p, "Já jsem v klubu!", *hd("tonda", p.X(0.5), p.Y(0.03), 1.41), w=120)
    with Pn(*R[2]) as p:
        attic(p, floor_y=0.14, window=(0.85, 0.6), dark=0.15, seed=33)
        chest(p.X(0.45), p.Y(0.06), 0.8, open_=True)
        treasure_tin(p.X(0.4), p.Y(0.06) + 44, 0.5, dirty=True)
        shoebox(p.X(0.55), p.Y(0.06) + 44, 0.45, open_=False)
        for dx in (-20, 0, 20): owlet(p.X(0.22) + dx, p.Y(0.72), 0.9, mood="sleepy")
        cap(p, "Poklady se uloží do truhly na půdě. Sovičky hlídají.", w=p.w - 20, size=12, where="bl")
    with Pn(*R[3]) as p:
        pond_view(p, 0.2, 0.62, seed=60, clouds_=False)
        excavator(p.X(0.45), p.Y(0.24), 0.9)
        alica(p.X(0.08), p.Y(0.03), 0.88, mood="grin", right="wave"); hanka(p.X(0.18), p.Y(0.03), 0.88, mood="grin", right="wave")
        verka_old(p.X(0.85), p.Y(0.03), 0.84, flip=True, mood="happy", right="wave")
        cap(p, "V pondělí přijely bagry. Nikdo se nebál.", w=p.w - 20, size=12, where="tl")
    with Pn(*R[4]) as p:
        bg_fill(p, 1.0); rays(p, p.X(0.5), p.Y(0.62), 0.9, 24)
        cx, cy = p.X(0.5), p.Y(0.62)
        figs = [(babicka, 0.08, 1.2, "babi"), (deda, 0.22, 1.2, "deda"), (alica, 0.36, 1.45, "alica"),
                (hanka, 0.64, 1.45, "hanka"), (tonda, 0.78, 1.3, "tonda"), (verka_old, 0.92, 1.2, "verka")]
        for fn, fx, fs, who in figs:
            kw = dict(mood="laugh" if fn in (deda, babicka, tonda, verka_old) else "grin", look=(1 if fx < 0.5 else -1, 0.5))
            if fn is verka_old: kw["stick"] = False
            fn(p.X(fx), p.Y(0.03), fs, flip=fx > 0.5, right="up", **kw)
        joey(p.X(0.5), p.Y(0.03), 1.3, mood="happy")
        badge(cx, cy, 30)
        say(p, "Klub Hvězdička drží spolu!", cx, cy + 22, w=p.w*0.6)
    page_end()


# =================================================================== 22 activity
def page_quiz():
    with Pn(M, 40, W-2*M, H-80) as p:
        box = [(p.X(0.05), p.Y(0.905)), (p.X(0.95), p.Y(0.91)), (p.X(0.95), p.Y(0.905)+54), (p.X(0.05), p.Y(0.905)+52)]
        fill(box, 0.92)
        for a_, b_ in ((0, 1), (1, 2), (2, 3), (3, 0)): stroke([box[a_], box[b_]], 1.5)
        hand_text(p.X(0.05), p.Y(0.905)+18, p.w*0.9, "Detektivní zápisník", "SHB", 26)
        full_map(p.X(0.08), p.Y(0.47), 1.95)
        hand_text(p.X(0.06), p.Y(0.435), p.w*0.9, "Najdi na mapě: vrbu, kámen s hvězdičkou, mlýn a lávku, která už tu není.", "SH", 13)
        y = p.Y(0.38)
        qs = ["1. Proč děda krokoval špatně?", "2. Co našla Hanka v trávě?", "3. Co zakopával Tonda?",
              "4. Kdo vykopal poklad a proč?", "5. Co bylo v plechovce?"]
        for q in qs:
            hand_text(p.X(0.06), y, p.w*0.9, q, "SH", 15, align="left")
            stroke([(p.X(0.06), y - 18), (p.X(0.94), y - 18)], 0.5, g=0.5)
            y -= 42
        star(p.X(0.08), y - 4, 9, 0.97)
        hand_text(p.X(0.12), y - 10, p.w*0.82, "V sešitě je schováno 7 bílých hvězdiček. Najdeš je všechny?", "SHB", 14, align="left")
        with T(p.X(0.5), p.Y(0.015), 1.0, rot=180):
            hand_text(-p.w*0.45, 0, p.w*0.9, "Hvězdičky jsou na stranách 4, 6, 10, 14, 15, 21 a 23.", "SH", 10)
    page_end()


# =================================================================== 23 next time
def page_next():
    with Pn(M, 40, W-2*M, H-80, bg=0.95) as p:
        hand_text(p.X(0.1), p.Y(0.93), p.w*0.8, "Příště v sešitě č. 4:", "SHB", 20)
        title(p.X(0.5), p.Y(0.84), "HANKA TO VYŘEŠÍ!", 38)
        with Pn(p.X(0.08), p.Y(0.36), p.w*0.84, p.h*0.42, bg=0.9) as q:
            bg_fill(q, P.BEDROOM_WALL)
            for xx in range(int(q.x) + 12, int(q.x + q.w), 26): stroke([(xx, q.Y(0.36)), (xx, q.y + q.h)], 0.5, g=0.82)
            bunting(q)
            shelf_toys(q.X(0.08), q.Y(0.72), 80)
            x0, x1, top = q.X(0.04), q.X(0.62), q.Y(0.34)
            bed_side(x0, x1, top)
            ax = x1 - 30; waist = top + 8
            C.saveState(); C.clipPath(poly([(q.x, top - 10), (q.x + q.w, top - 10), (q.x + q.w, q.y + q.h), (q.x, q.y + q.h)]), stroke=0, fill=0)
            alica(ax, waist - 45*1.3, 1.3, mood="sad", right="front", look=(1, -0.3), shadow=False,
                  item=lambda x, y: (stroke([(x, y), (x + 10, y + 14)], 2.4), stroke([(x, y), (x + 10, y + 14)], 1.2, g=1.0)))
            C.restoreState()
            blanket_side(x0, ax + 14, top, waist + 4)
            picture_letter(q.X(0.18), top + 2, 0.75, rot=-6)
            hanka(q.X(0.76), q.Y(0.03), 1.4, flip=True, mood="determined", right="up", look=(1, 0))
            joey(q.X(0.9), q.Y(0.03), 1.0, flip=True, mood="happy")
            say(q, "Tohle umí přečíst jen Hanka.", *hd("alica", ax, waist - 45*1.3, 1.3), w=190)
        hand_text(p.X(0.1), p.Y(0.3), p.w*0.8, "Kam vede Frantův obrázkový dopis? A co je jeho tajný poklad?", "SH", 16, lead=21)
        hand_text(p.X(0.3), p.Y(0.19), p.w*0.4, "Detektivní tým:", "SHB", 16)
        alica(p.X(0.07), p.Y(0.03), 0.9, mood="happy", right="wave")
        hanka(p.X(0.17), p.Y(0.03), 0.9, mood="grin")
        joey(p.X(0.29), p.Y(0.03), 0.7, mood="happy")
        tonda(p.X(0.42), p.Y(0.03), 0.85, mood="grin")
        babicka(p.X(0.54), p.Y(0.03), 0.82, mood="happy")
        deda(p.X(0.66), p.Y(0.03), 0.78, mood="happy")
        verka_old(p.X(0.79), p.Y(0.03), 0.8, flip=True, mood="happy")
        owlet(p.X(0.93), p.Y(0.03), 1.0)
        hidden_star(p.X(0.92), p.Y(0.2))
    page_end()


# =================================================================== 24 back cover
def back_cover():
    with Pn(M, 40, W-2*M, H-80, bg=0.95) as p:
        rays(p, p.X(0.5), p.Y(0.58), 0.9, 24)
        shape(ell(p.X(0.5), p.Y(0.58), 120, 120, 60), P.BRASS, 2.4)
        star(p.X(0.5), p.Y(0.58), 90, P.TAG_STAR, w=2.4)
        title(p.X(0.5), p.Y(0.3), "KLUB HVĚZDIČKA", 40)
        hand_text(p.X(0.1), p.Y(0.24), p.w*0.8, "drží spolu!", "SHB", 24)
        hand_text(p.X(0.1), p.Y(0.06), p.w*0.8, "Velká a malá detektivka · sešit č. 3", "SH", 13, g=0.35)
    PAGE[0] += 1; cv.showPage()


cover(); page_cast(); page_map(); page_pond(); page_willow(); page_steps(); page_hole(); page_clues()
page_tonda(); page_badger(); page_quarrel(); page_stakeout(); page_secret(); page_cleared(); page_nose()
page_deadend(); page_stop(); page_hanka(); page_verka(); page_treasure(); page_club(); page_quiz(); page_next()
back_cover()
cv.save()
print("ok", PAGE[0] - 1, "pages")
for pr in PROBLEMS: print("ORDER/LAYOUT:", pr)
if PROBLEMS: sys.exit(1)
