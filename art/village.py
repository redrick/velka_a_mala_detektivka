"""Art for issue 4 "Hanka to vyřeší!": the village church with the stopped clock, hens and the old
henhouse, the Bota rock, the sexton, walkie-talkies, Hanka's crayon reports, Franta's new picture
letter, the clock key, hearts and the first snow."""
import math, random
import lib
from lib import ell, bez, rrect
import palette as P
from style3 import *
from style3 import C, draw_arm, draw_legs, head_outline, face, hand
from chars3 import Person, _neck, star
from scenes3 import BG, s_, sh_
from pond import far_trees


# ------------------------------------------------------------------ hearts
def heart_pts(x, y, r):
    """heart centred on (x, y), r = half its width"""
    right = bez((0, -r), (r*0.85, -r*0.25), (r*1.15, r*0.55), (r*0.55, r*0.82)) + \
            bez((r*0.55, r*0.82), (r*0.25, r*0.98), (0, r*0.8), (0, r*0.52))
    left = [(-px, py) for px, py in reversed(right)]
    return [(x + px, y + py) for px, py in right + left[1:]]


def heart(x, y, r=5, g=P.HEART, w=None):
    shape(heart_pts(x, y, r), g, LINE*0.8 if w is None else w)


def hidden_heart(x, y, r=4.4):
    """one of the 9 hearts Hanka hid for Alica (the activity page asks to find them)"""
    heart(x, y, r, 0.97, w=0.9)


# ------------------------------------------------------------------ hens
def hen(x, y, s=1.0, flip=False, pose="stand", g=P.HEN):
    """a hen (local height ~32). pose: stand, peck, sit"""
    with T(x, y, s, flip):
        by = 2 if pose == "sit" else 9
        if pose != "sit":
            for lx in (-3, 3):
                stroke([(lx, by + 2), (lx + 0.5, 1)], LINE*0.9, g=P.HEN_LEG)
                stroke([(lx - 2.5, 0.4), (lx + 3.5, 0.4)], LINE*0.8, g=P.HEN_LEG)
        tail = [(-9, by + 8)] + bez((-9, by + 8), (-14, by + 14), (-17, by + 21), (-14, by + 23)) + \
               bez((-14, by + 23), (-12, by + 17), (-10, by + 14), (-5, by + 13))
        shape(tail, g)
        stroke(bez((-10, by + 12), (-13, by + 16), (-14, by + 19), (-14.5, by + 21)), LINE*0.5)
        body = ell(0, by + 8, 11.5, 8.5, 32)
        form(body, g, sdx=-1.2, sdy=1)
        stroke(bez((-6, by + 10), (-2, by + 5), (4, by + 5), (6, by + 9)), LINE*0.6)
        stroke(bez((-3, by + 7), (0, by + 5.5), (3, by + 6), (4, by + 8)), LINE*0.5)
        hx, hy = (11, by + 3) if pose == "peck" else (8.5, by + 18)
        if pose != "peck":
            fill([(4, by + 12), (10, by + 12), (11, hy - 2), (6, hy - 2)], g)
            stroke([(10.5, by + 12), (11.4, hy - 2.5)], LINE*0.8)
        shape(ell(hx, hy, 4.6, 4.4, 20), g, LINE*0.9)
        shape([(hx - 3, hy + 3.2), (hx - 2.2, hy + 6.8), (hx - 0.6, hy + 4.6), (hx + 0.8, hy + 7.4), (hx + 2, hy + 4.6),
               (hx + 3.6, hy + 6), (hx + 3.4, hy + 2.6)], P.HEN_COMB, LINE*0.6)
        shape([(hx + 4, hy + 0.8), (hx + 8, hy - 0.6), (hx + 4, hy - 1.8)], P.HEN_BEAK, LINE*0.6)
        shape(ell(hx + 3.2, hy - 3.4, 1.3, 2.0, 10), P.HEN_COMB, LINE*0.5)
        dot(hx + 1.6, hy + 1, 0.9, 0.0)


def henhouse(x, y, s=1.0):
    """babička's new henhouse on short legs with a ramp (local width ~80)"""
    with T(x, y, s):
        for lx in (-32, 28):
            sh_([(lx, 0), (lx + 5, 0), (lx + 5, 14), (lx, 14)], P.POST)
        form([(-36, 14), (36, 14), (36, 50), (-36, 50)], P.HENHOUSE, w=BG*1.2, sdx=2, sdy=0, sh=0.1)
        for xx in range(-30, 36, 8): s_([(xx, 15), (xx, 49)], BG*0.4)
        sh_([(-42, 48), (0, 70), (42, 48), (42, 44), (0, 66), (-42, 44)], P.HENHOUSE_ROOF)
        sh_(rrect(-8, 16, 14, 16, 3), 0.15)
        form([(-6, 16), (6, 16), (-10, 0), (-22, 0)], P.PLANKS, w=BG, sdx=0, sdy=0, sh=0)
        for k_ in range(4): s_([(-8 - k_*3.5, 13 - k_*4), (4 - k_*3.5, 13 - k_*4)], BG*0.6)
        sh_([(14, 34), (28, 34), (28, 44), (14, 44)], P.WINDOW_GLASS)


def ivy_patch(x0, x1, y, h, seed=4, g=P.NETTLE):
    """tall weeds/nettles standing in front of something"""
    r = random.Random(seed)
    for i in range(int((x1 - x0)/6)):
        xx = x0 + i*6 + r.uniform(-2, 2); hh = h*r.uniform(0.6, 1.1)
        stroke(bez((xx, y), (xx + r.uniform(-3, 3), y + hh*0.4), (xx + r.uniform(-4, 4), y + hh*0.7), (xx + r.uniform(-5, 5), y + hh)), LINE*0.7)
        for k_ in range(3):
            ly = y + hh*(0.35 + k_*0.22); side = 1 if (i + k_) % 2 else -1
            shape([(xx, ly), (xx + side*6, ly + 3), (xx + side*9, ly + 7), (xx + side*3, ly + 4)], g, LINE*0.5)


def old_henhouse(x, y, s=1.0, door_open=True, seed=6):
    """the tiny old henhouse behind the barn: low, crooked, a door only a small child fits through"""
    with T(x, y, s):
        body = [(-30, 0), (30, 0), (29, 34), (-31, 38)]
        form(body, P.HENHOUSE_OLD, w=BG*1.2, sdx=2, sdy=0, sh=0.12)
        for xx in range(-26, 30, 7): s_([(xx, 1), (xx - 0.5, 34)], BG*0.4)
        sh_([(-36, 36), (-2, 54), (35, 32), (35, 28), (-2, 50), (-36, 32)], P.HENHOUSE_ROOF)
        s_([(-20, 44), (-6, 51)], BG*0.5); s_([(8, 46), (20, 40)], BG*0.5)
        if door_open:
            sh_(rrect(-6, 0, 13, 15, 2), 0.1)
            form([(7, 0), (13, 2), (13, 16), (7, 15)], P.HENHOUSE_OLD, w=BG, sdx=0, sdy=0, sh=0)
        else:
            sh_(rrect(-6, 0, 13, 15, 2), P.HENHOUSE)
        s_([(-24, 20), (-14, 26)], BG*0.5); s_([(18, 18), (25, 23)], BG*0.5)
        ivy_patch(-38, -10, -1, 24, seed); ivy_patch(12, 38, -1, 22, seed + 1)


# ------------------------------------------------------------------ church
def church_clock(x, y, r=11, hands=True, hour=3, minute=0):
    """clock face; it stood at three o'clock for sixty years"""
    shape(ell(x, y, r*1.14, r*1.14, 32), P.CLOCK_GOLD, LINE*0.8)
    shape(ell(x, y, r, r, 32), P.CLOCK_FACE, LINE*0.7)
    for a in range(0, 360, 30):
        ra = math.radians(a); k_ = 0.72 if a % 90 else 0.64
        stroke([(x + math.cos(ra)*r*k_, y + math.sin(ra)*r*k_), (x + math.cos(ra)*r*0.86, y + math.sin(ra)*r*0.86)],
               LINE*(0.9 if a % 90 == 0 else 0.5))
    if hands:
        ha = 90 - ((hour % 12) + minute/60)*30
        with T(x, y, 1.0, rot=ha):
            shape([(0, -r*0.08), (r*0.62, -r*0.02), (r*0.62, r*0.02), (0, r*0.08)], P.CLOCK_HAND, LINE*0.5)
            shape([(r*0.62, r*0.12), (r*0.78, 0), (r*0.62, -r*0.12)], P.CLOCK_HAND, LINE*0.4)
        with T(x, y, 1.0, rot=90 - minute*6):
            shape([(0, -r*0.05), (r*0.84, -r*0.03), (r*0.84, r*0.03), (0, r*0.05)], P.CLOCK_HAND, LINE*0.4)
    dot(x, y, r*0.08, 0.0)


def church(x, y, s=1.0, nave=True, hour=3, minute=0):
    """village church: tower on the left with the stopped clock, nave to the right.
    (x, y) = foot of the tower's centre; the clock sits at local (0, 108)"""
    with T(x, y, s):
        if nave:
            form([(20, 0), (150, 0), (150, 62), (20, 62)], P.CHURCH_WALL, w=BG*1.2, sdx=2, sdy=0, sh=0.08)
            sh_([(16, 60), (85, 98), (154, 60), (154, 56), (85, 94), (16, 56)], P.ROOF)
            sh_([(20, 60), (85, 95), (150, 60)], P.ROOF)
            C.saveState(); C.clipPath(poly([(20, 60), (85, 95), (150, 60)]), stroke=0, fill=0)
            for yy in range(64, 96, 6): s_([(18, yy), (152, yy)], BG*0.5)
            C.restoreState()
            for wx in (48, 84, 120):
                sh_([(wx - 7, 20), (wx + 7, 20), (wx + 7, 42)] + bez((wx + 7, 42), (wx + 7, 50), (wx - 7, 50), (wx - 7, 42)), P.WINDOW_GLASS)
                s_([(wx, 20), (wx, 48)], BG*0.6, g=1.0)
        tw = 24
        form([(-tw, 0), (tw, 0), (tw, 132), (-tw, 132)], P.CHURCH_WALL, w=BG*1.3, sdx=2, sdy=0, sh=0.1)
        s_([(-tw, 90), (tw, 90)], BG*0.6)
        sh_([(-9, 0), (9, 0), (9, 26)] + bez((9, 26), (9, 38), (-9, 38), (-9, 26)), P.DOOR)
        s_([(0, 0), (0, 36)], BG*0.6)
        sh_([(-6, 58), (6, 58), (6, 70)] + bez((6, 70), (6, 78), (-6, 78), (-6, 70)), 0.2)
        church_clock(0, 108, 13, hour=hour, minute=minute)
        sh_([(-tw - 4, 130), (tw + 4, 130), (tw + 4, 135), (-tw - 4, 135)], P.CHURCH_SHADE)
        sh_([(-tw - 2, 135), (tw + 2, 135), (0, 196)], P.CHURCH_ROOF)
        s_([(-tw*0.5, 150), (0, 196)], BG*0.5); s_([(tw*0.5, 150), (0, 196)], BG*0.5)
        stroke([(0, 196), (0, 212)], LINE*1.1)
        stroke([(-5, 206), (5, 206)], LINE*1.1)
        dot(0, 196, 2, P.CLOCK_GOLD)


def gear(x, y, r, teeth=12, g=P.IRON, rot=0):
    pts = []
    for i in range(teeth*4):
        a = math.radians(rot) + i*math.tau/(teeth*4)
        rr = r if (i % 4) in (0, 1) else r*0.84
        pts.append((x + math.cos(a)*rr, y + math.sin(a)*rr))
    shape(pts, g, LINE*0.7)
    shape(ell(x, y, r*0.55, r*0.55, 24), P.METAL, LINE*0.5)
    for k_ in range(4):
        a = math.radians(rot + k_*90)
        stroke([(x, y), (x + math.cos(a)*r*0.55, y + math.sin(a)*r*0.55)], LINE*0.9, g=g)
    shape(ell(x, y, r*0.15, r*0.15, 12), 0.2, LINE*0.5)


def clockwork(x, y, s=1.0):
    """the old clock mechanism in the tower, with the empty keyhole for the winding key"""
    with T(x, y, s):
        form([(-40, 0), (40, 0), (40, 56), (-40, 56)], P.PLANKS, w=BG, sdx=0, sdy=0, sh=0)
        for lx in (-36, 32):
            sh_([(lx, 0), (lx + 4, 0), (lx + 4, 60), (lx, 60)], P.IRON)
        sh_([(-38, 56), (38, 56), (38, 60), (-38, 60)], P.IRON)
        gear(-14, 34, 14, 14, rot=8); gear(10, 26, 10, 10, rot=0); gear(22, 44, 8, 8, g=P.BRASS, rot=12)
        shape(ell(-14, 12, 5, 5, 16), P.METAL, LINE*0.7)
        fill([(-15.5, 10.5), (-12.5, 10.5), (-12.5, 13.5), (-15.5, 13.5)], 0.05)
        stroke([(22, 0), (22, -30)], LINE*0.8)
        shape(ell(22, -34, 5, 5, 16), P.BRASS, LINE*0.7)


def church_bell(x, y, s=1.0):
    with T(x, y, s):
        b = bez((-14, 0), (-12, 8), (-8, 20), (-6, 26)) + bez((-6, 26), (-4, 31), (4, 31), (6, 26)) + \
            bez((6, 26), (8, 20), (12, 8), (14, 0))
        form(b + [(14, 0), (-14, 0)], P.BELL, sdx=-2, sdy=0)
        shape(ell(0, -2, 3, 3, 12), P.BELL, LINE*0.6)


# ------------------------------------------------------------------ the Bota rock
def boot_rock(x, y, s=1.0, view="side", crack=False, seed=3):
    """the rock the village calls "Bota". view="side": a clear boot, shaft left, toe right (seen from
    the church tower); view="front": just a mossy lump (seen from the path). local width ~100"""
    r = random.Random(seed)
    with T(x, y, s):
        if view == "side":
            out = [(-32, 0)] + bez((-32, 0), (-36, 30), (-37, 60), (-33, 88)) + bez((-33, 88), (-20, 94), (0, 95), (12, 90)) + \
                  bez((12, 90), (13, 70), (12, 55), (18, 45)) + bez((18, 45), (38, 42), (62, 36), (68, 18)) + \
                  bez((68, 18), (71, 8), (68, 2), (64, 0))
        else:
            out = [(-40, 0)] + bez((-40, 0), (-46, 30), (-30, 62), (0, 66)) + bez((0, 66), (30, 64), (48, 36), (44, 0))
        form(out + [(out[0][0], 0)], P.ROCK, w=LINE*1.1, sdx=3, sdy=0, sh=0.1)
        C.saveState(); C.clipPath(poly(out), stroke=0, fill=0)
        for _ in range(6):
            cx, cy = r.uniform(-30, 55 if view == "side" else 38), r.uniform(8, 80 if view == "side" else 55)
            stroke(bez((cx, cy), (cx + r.uniform(3, 8), cy + r.uniform(-4, 4)), (cx + r.uniform(8, 14), cy + r.uniform(-6, 2)),
                       (cx + r.uniform(12, 20), cy + r.uniform(-8, 0))), LINE*0.5, g=P.ROCK_DARK)
        for _ in range(5):
            cx, cy = r.uniform(-30, 40), r.uniform(50, 95) if view == "side" else r.uniform(40, 70)
            fill(ell(cx, cy, r.uniform(6, 12), r.uniform(3, 5), 16), P.MOSS, 0.9)
        if view == "side":
            stroke(bez((-33, 86), (-20, 90), (0, 91), (11, 87)), LINE*0.6, g=P.ROCK_DARK)
            stroke(bez((14, 44), (16, 30), (20, 18), (22, 0)), LINE*0.5, g=P.ROCK_DARK)
        C.restoreState()
        if crack:
            cr = [(46, 0), (50, 14), (55, 20), (60, 12), (62, 0)]
            fill(cr, 0.08)
            stroke(cr[:-1], LINE*0.8)
        for k_ in range(9):
            gx = r.uniform(-40, 70); k = r.uniform(0.7, 1.2)
            sh_([(gx - 4*k, 0), (gx - 3*k, 5*k), (gx - 1.5*k, 1.5*k), (gx, 8*k), (gx + 1.5*k, 1.5*k), (gx + 3*k, 5*k), (gx + 4*k, 0)],
                P.TUFT, BG*0.6)


# ------------------------------------------------------------------ the sexton
KOSTELNIK = dict(H=122, hr=10.4, hy=111, sh_y=96, sh_w=12.2, hip=56, knee=30, ankle=5, leg_w=(7, 5.6),
                 arm_w=(6.4, 5.6), up=19, fo=17)


def key_ring(x, y, s=1.0):
    with T(x, y, s):
        stroke(ell(0, 0, 3.4, 3.4, 16), LINE*0.8, closed=True, g=0.2)
        for k_, a in enumerate((-110, -80, -50)):
            ra = math.radians(a)
            x1, y1 = math.cos(ra)*3.4, math.sin(ra)*3.4
            x2, y2 = x1 + math.cos(ra)*8, y1 + math.sin(ra)*8
            stroke([(x1, y1), (x2, y2)], LINE*1.1, g=P.IRON if k_ != 1 else P.BRASS)
            stroke([(x2, y2), (x2 + 2, y2 + 1)], LINE*1.0, g=P.IRON)


def kostelnik(x, y, s=1.0, flip=False, left="down", right="down", mood="happy", look=(0, 0), item=None, shadow=True,
              legs="stand", keys=True):
    """the sexton: thin older man, long dark coat, beret, grey moustache, small black galoshes"""
    k = Person(**KOSTELNIK)
    if shadow: cast_shadow(x, y, 16*s, 2.8*s)
    with T(x, y, s, flip):
        r = k.hr; cy = k.hy
        draw_legs(k, legs, P.TROUSERS, boots=P.GALOSHES, boot_top=k.ankle + 3)
        draw_arm(k, -1, left, P.KOSTELNIK_COAT)
        coat = bez((-5, k.sh_y + 2.6), (-9, k.sh_y + 2.3), (-k.sh_w - 1.2, k.sh_y + 0.5), (-k.sh_w - 1.8, k.sh_y - 4)) + \
               bez((-k.sh_w - 1.8, k.sh_y - 4), (-13.5, 70), (-14.5, 50), (-15, 30)) + \
               bez((-15, 30), (-5, 28.5), (5, 28.5), (15, 30)) + \
               bez((15, 30), (14.5, 50), (13.5, 70), (k.sh_w + 1.8, k.sh_y - 4)) + \
               bez((k.sh_w + 1.8, k.sh_y - 4), (k.sh_w + 1.2, k.sh_y + 0.5), (9, k.sh_y + 2.3), (5, k.sh_y + 2.6))
        form(coat, P.KOSTELNIK_COAT, sdx=-2.2, sdy=1.2)
        stroke([(1, k.sh_y - 1), (1.5, 29)], LINE*0.7, g=0.6)
        for by in (84, 72, 60, 48): shape(ell(-1.5, by, 1.0, 1.0, 10), 0.6, LINE*0.5)
        shape(bez((-5, k.sh_y + 2.4), (-2, k.sh_y - 3), (2, k.sh_y - 3), (5, k.sh_y + 2.4)) + [(0, k.sh_y + 1)], 1.0, LINE*0.7)
        if keys: key_ring(10, 56, 1.1)
        h, fa = draw_arm(k, 1, right, P.KOSTELNIK_COAT)
        if item: item(*h)
        _neck(k, 2.6)
        for sx in (-1, 1): shape(ell(sx*r*0.98, cy - r*0.05, r*0.2, r*0.3, 14), P.SKIN, LINE*0.8)
        shape(head_outline(k), P.SKIN)
        for sx in (-1, 1):
            shape(bez((sx*r*0.98, cy + r*0.45), (sx*r*1.1, cy + r*0.1), (sx*r*1.04, cy - r*0.2), (sx*r*0.9, cy - r*0.3)) +
                  [(sx*r*0.8, cy + r*0.4)], P.GREY_HAIR, LINE*0.7)
        face(0, cy, r, mood, look)
        mst = bez((-r*0.55, cy - r*0.42), (-r*0.3, cy - r*0.22), (r*0.3, cy - r*0.22), (r*0.55, cy - r*0.42)) + \
              bez((r*0.55, cy - r*0.42), (r*0.25, cy - r*0.36), (-r*0.25, cy - r*0.36), (-r*0.55, cy - r*0.42))
        shape(mst, P.GREY_HAIR, LINE*0.8)
        for sx in (-1, 1):
            shape(ell(sx*r*0.4, cy + r*0.33, r*0.22, r*0.07, 12), P.GREY_HAIR, LINE*0.6)
        beret = bez((-r*1.05, cy + r*0.5), (-r*1.3, cy + r*1.25), (r*0.9, cy + r*1.4), (r*1.1, cy + r*0.55)) + \
                bez((r*1.1, cy + r*0.55), (r*0.4, cy + r*0.72), (-r*0.4, cy + r*0.72), (-r*1.05, cy + r*0.5))
        form(beret, P.BERET, sdx=-1.2, sdy=1)
        stroke([(r*0.1, cy + r*1.36), (r*0.2, cy + r*1.6)], LINE*1.2)


# ------------------------------------------------------------------ small props
def vysilacka(x, y, s=1.0, rot=0):
    """toy walkie-talkie (local height ~26 with antenna)"""
    with T(x, y, s, rot=rot):
        stroke([(3, 16), (3, 27)], LINE*1.4)
        dot(3, 27.5, 1.3, 0.2)
        shape(rrect(-5, 0, 10, 17, 2.5), P.WALKIE, LINE*0.8)
        shape(rrect(-3.5, 9, 7, 6, 1.2), P.WALKIE_DARK, LINE*0.5)
        for gy in (10.5, 12, 13.5): stroke([(-2.5, gy), (2.5, gy)], LINE*0.4, g=0.7)
        shape(ell(0, 4.5, 2, 2, 12), P.WALKIE_DARK, LINE*0.5)


def zig_print(x, y, s=1.0, rot=0, g=P.MUD_DARK):
    """a big grown-up boot print with a zigzag sole (local length ~34)"""
    with T(x, y, s, rot=rot):
        sole = bez((0, -17), (6, -17), (7, -9), (6, -3)) + bez((6, -3), (6.5, 4), (7.5, 11), (5, 17)) + \
               bez((5, 17), (0, 19), (-5, 19), (-7, 16)) + bez((-7, 16), (-8, 9), (-6.5, 2), (-6, -3)) + \
               bez((-6, -3), (-7, -9), (-6.5, -17), (0, -17))
        fill(sole, g)
        for y0 in (-14, 3):
            zz = [(-5 + i*2.2, y0 + (2.4 if i % 2 else 0)) for i in range(6)]
            stroke(zz, LINE*0.9, g=P.MUD)
            zz = [(-5 + i*2.2, y0 + 5 + (2.4 if i % 2 else 0)) for i in range(6)]
            stroke(zz, LINE*0.9, g=P.MUD)
        stroke([(-6, -1), (6, -1)], LINE*1.4, g=P.MUD)


def splavek(x, y, s=1.0, rot=0):
    """fishing float, red top and white bottom (local height ~22)"""
    with T(x, y, s, rot=rot):
        stroke([(0, -4), (0, 20)], LINE*0.8)
        b = ell(0, 8, 3.6, 8, 24)
        shape(b, 1.0, LINE*0.8)
        C.saveState(); C.clipPath(poly(b), stroke=0, fill=0)
        fill([(-5, 8), (5, 8), (5, 18), (-5, 18)], P.FLOAT_RED)
        C.restoreState()
        stroke(b, LINE*0.8, closed=True)


def clock_key(x, y, s=1.0, rot=0):
    """the big iron winding key of the church clock (local length ~50, grip on the left)"""
    with T(x, y, s, rot=rot):
        grip = [(-4, -11), (4, -11), (4, 11), (-4, 11)]
        shape(rrect(-6, -12, 12, 24, 5), P.IRON, LINE*0.9)
        shape(rrect(-2.5, -7, 5, 14, 2.5), 0.95, LINE*0.6)
        shape([(6, -2.2), (42, -2.2), (42, 2.2), (6, 2.2)], P.IRON, LINE*0.8)
        shape([(40, -4.5), (50, -4.5), (50, 4.5), (40, 4.5)], P.IRON, LINE*0.8)
        fill([(46, -2), (50, -2), (50, 2), (46, 2)], 0.05)


def hen_whistle(x, y, s=1.0, flip=False):
    """Franta's carved wooden hen whistle"""
    with T(x, y, s, flip):
        shape([(-14, 5), (-22, 7), (-22, 3), (-14, 2)], P.WOOD_TOY, LINE*0.7)
        shape(ell(0, 6, 12, 7, 28), P.WOOD_TOY, LINE*0.9)
        shape(ell(10, 14, 5, 4.6, 18), P.WOOD_TOY, LINE*0.8)
        shape([(8, 18), (9.5, 21), (11, 18.5), (12.5, 21), (13.5, 17)], P.WOOD_TOY, LINE*0.6)
        shape([(14.5, 14.5), (19, 13.5), (14.5, 12)], P.WOOD_TOY, LINE*0.6)
        dot(11.5, 15, 0.9, 0.0)
        shape(ell(-2, 8, 2.4, 1.8, 12), 0.1, LINE*0.4)
        stroke(bez((-6, 4), (-2, 1.5), (3, 2), (6, 5)), LINE*0.5)


def bucket_hat(x, y, s=1.0, rot=0):
    """the fisherman's hat held in a hand (local width ~34)"""
    with T(x, y, s, rot=rot):
        shape(bez((-11, 0), (-12, 13), (12, 13), (11, 0)) + [(-11, 0)], P.RYBAR_HAT, LINE*0.8)
        shape([(-16, -3), (16, -3), (11, 1), (-11, 1)], P.RYBAR_HAT, LINE*0.8)
        shape([(5, 6), (9, 8.5), (6, 3.5)], P.DUCK_BILL, LINE*0.5)


def getwell_drawing(x, y, w=60, h=44, rot=0):
    """Franta's get-well picture letter for Alica: bed -> sun -> a girl jumping -> heart"""
    with T(x, y, 1.0, rot=rot):
        _paper(w, h, 1.0)
        ink = P.MAP_INK; w_ = LINE*0.7; k = w/60
        stroke([(4*k, 30*k), (4*k, 38*k)], w_, g=ink); stroke([(4*k, 32*k), (16*k, 32*k), (16*k, 35*k)], w_, g=ink)
        _arrow((19*k, 34*k), (26*k, 34*k), w_, ink)
        stroke(ell(35*k, 34*k, 4*k, 4*k, 16), w_, closed=True, g=P.CRAYON_ORANGE)
        for a in range(0, 360, 45):
            ra = math.radians(a)
            stroke([(35*k + math.cos(ra)*5.5*k, 34*k + math.sin(ra)*5.5*k), (35*k + math.cos(ra)*7.5*k, 34*k + math.sin(ra)*7.5*k)], w_*0.8, g=P.CRAYON_ORANGE)
        _arrow((46*k, 30*k), (40*k, 22*k), w_, ink)
        stroke(ell(28*k, 17*k, 2.4*k, 2.4*k, 12), w_, closed=True, g=ink)
        stroke([(28*k, 14.5*k), (28*k, 8*k)], w_, g=ink)
        stroke([(23*k, 17*k), (28*k, 12*k), (33*k, 17*k)], w_, g=ink)
        stroke([(25*k, 3*k), (28*k, 8*k), (31*k, 3*k)], w_, g=ink)
        _arrow((20*k, 10*k), (13*k, 10*k), w_, ink)
        heart(7*k, 10*k, 4*k, P.HEART, w=w_)
        with T(w - 10*k, 7*k, 0.5*k):
            letter_hen(0, 0, w_*1.4, ink)


def candy_wrapper(x, y, s=1.0, rot=0):
    with T(x, y, s, rot=rot):
        shape([(-9, -3), (-5, 0), (-9, 3)], P.WRAPPER, LINE*0.6)
        shape([(9, -3), (5, 0), (9, 3)], P.WRAPPER, LINE*0.6)
        shape(ell(0, 0, 5.4, 3.4, 16), P.WRAPPER, LINE*0.7)
        stroke([(-2, -1), (2, 1)], LINE*0.4, g=1.0)


def frog(x, y, s=1.0, flip=False, jump=False):
    with T(x, y, s, flip):
        if jump:
            for sx in (-1, 1):
                stroke([(sx*4, 2), (sx*10, -6), (sx*12, -12)], LINE*1.8); stroke([(sx*4, 2), (sx*10, -6), (sx*12, -12)], LINE*0.9, g=P.FROG)
        else:
            for sx in (-1, 1): shape(ell(sx*8, 1.5, 5, 2.4, 14), P.FROG, LINE*0.7)
        shape(ell(0, 5, 9, 6, 24), P.FROG, LINE*0.9)
        for sx in (-1, 1):
            shape(ell(sx*4.5, 10.5, 2.8, 2.8, 14), P.FROG, LINE*0.7)
            dot(sx*4.5, 11, 1.2, 0.0)
        stroke(bez((-4, 5.5), (-1.5, 3.6), (1.5, 3.6), (4, 5.5)), LINE*0.6)


def old_boot_prop(x, y, s=1.0, rot=0):
    """a soggy old boot out of the brook"""
    from scenes3 import boot
    with T(x, y, 1.0, rot=rot):
        boot(0, 0, s)


def snowman(x, y, s=1.0):
    with T(x, y, s):
        shape(ell(0, 16, 20, 17, 30), P.SNOW, LINE)
        shape(ell(0, 42, 14, 12, 28), P.SNOW, LINE)
        shape(ell(0, 62, 10, 9.5, 26), P.SNOW, LINE)
        fill(ell(-5, 12, 12, 10, 20), P.SNOW_SHADE, 0.6)
        for by in (46, 40, 34): dot(0, by, 1.4, 0.1)
        for sx in (-1, 1): dot(sx*3.5, 65, 1.3, 0.05)
        shape([(0, 62), (11, 60), (0, 59.5)], P.CARROT, LINE*0.6)
        for k_ in range(5): dot(-4 + k_*2, 56.5 - abs(k_ - 2)*0.8, 0.7, 0.1)
        for sx in (-1, 1):
            stroke([(sx*12, 46), (sx*24, 56), (sx*28, 60)], LINE*1.2, g=P.BARK)
        shape([(-7, 70), (7, 70), (6, 80), (-6, 80)], 0.2, LINE*0.7)
        shape([(-10, 69), (10, 69), (10, 71.5), (-10, 71.5)], 0.2, LINE*0.7)


def snow_ground(p, y, seed=3):
    r = random.Random(seed)
    top = [(p.x - 5 + i*(p.w + 10)/20, y + r.uniform(-2, 3)) for i in range(21)]
    fill([(p.x - 5, p.y - 5)] + top + [(p.x + p.w + 5, p.y - 5)], P.SNOW)
    stroke(top, BG)


def snowflakes(p, n=40, seed=5, r_=1.6):
    r = random.Random(seed)
    for _ in range(n):
        x, y = p.x + r.random()*p.w, p.y + r.random()*p.h
        shape(ell(x, y, r_, r_, 10), 1.0, 0.4)


def moving_van(x, y, s=1.0, flip=False):
    """an old-fashioned small removal van (local width ~110)"""
    with T(x, y, s, flip):
        form([(-55, 10), (20, 10), (20, 58), (-55, 58)], P.VAN, w=LINE, sdx=2, sdy=0, sh=0.1)
        form([(20, 10), (50, 10), (50, 30)] + bez((50, 30), (48, 40), (40, 42), (34, 42)) + [(20, 42)], P.VAN, w=LINE, sdx=2, sdy=0, sh=0.1)
        shape([(26, 26), (40, 26), (40, 38), (26, 38)], P.WINDOW_GLASS, LINE*0.7)
        for wx in (-38, 34):
            shape(ell(wx, 10, 9, 9, 24), 0.15, LINE)
            shape(ell(wx, 10, 3.5, 3.5, 14), 0.7, LINE*0.6)
        for xx in (-40, -20, 0): s_([(xx, 12), (xx, 56)], BG*0.5)


# ------------------------------------------------------------------ drawings on paper
def _paper(w, h, g=P.LETTER_PAPER):
    shape([(0, 0), (w, 1.5), (w + 1.5, h), (-1.5, h - 1)], g, LINE*0.8)


def _arrow(a, b, w_, ink):
    stroke([a, b], w_, g=ink)
    ang = math.atan2(b[1] - a[1], b[0] - a[0])
    for da in (2.5, -2.5):
        stroke([b, (b[0] - math.cos(ang + da*0.2)*3.5, b[1] - math.sin(ang + da*0.2)*3.5)], w_, g=ink)


def letter_hen(ox, oy, w_, ink):
    """Franta's hen, exactly as in the old picture letter (pond.picture_letter): same egg body,
    round head, three-bump comb in red and a tail hook"""
    stroke(ell(ox, oy, 8, 6, 24), w_, closed=True, g=ink)
    stroke(ell(ox + 8, oy + 7, 3.4, 3.4, 16), w_, closed=True, g=ink)
    stroke([(ox + 11, oy + 7), (ox + 14.5, oy + 6), (ox + 11, oy + 5)], w_, g=ink)
    stroke([(ox + 6, oy + 10.5), (ox + 7, oy + 13), (ox + 8.5, oy + 11), (ox + 10, oy + 13), (ox + 10.5, oy + 10)], w_, g=P.TAG_STAR)
    stroke([(ox - 8, oy + 2), (ox - 12, oy + 8), (ox - 8, oy + 5)], w_, g=ink)
    for lx in (-2, 2): stroke([(ox + lx, oy - 6), (ox + lx, oy - 10), (ox + lx + 2, oy - 11)], w_, g=ink)
    dot(ox + 8.5, oy + 8, 0.6, 0.0)


def new_letter(x, y, s=1.0, rot=0):
    """Franta's new picture letter, on clean white paper: fish -> jetty -> clock at three -> bucket hat,
    with his hen drawn small in the corner (local 92 x 64)"""
    with T(x, y, s, rot=rot):
        _paper(92, 64, 1.0)
        ink = P.MAP_INK; w_ = LINE*0.8
        # fish
        stroke(ell(16, 48, 9, 5, 24), w_, closed=True, g=ink)
        stroke([(7, 48), (2, 53), (2, 43), (7, 48)], w_, g=ink)
        dot(21, 49, 0.7, 0.0)
        stroke(bez((12, 52), (14, 50), (14, 46), (12, 44)), w_*0.7, g=ink)
        _arrow((30, 48), (42, 48), w_, ink)
        # jetty over water
        stroke([(48, 48), (80, 48)], w_, g=ink); stroke([(48, 51), (80, 51)], w_, g=ink)
        for px in (52, 64, 76): stroke([(px, 48), (px, 38)], w_, g=ink)
        for wx in (48, 58, 68):
            stroke(bez((wx, 40), (wx + 2.5, 42), (wx + 5, 38), (wx + 8, 40)), w_*0.8, g=ink)
        _arrow((66, 32), (58, 24), w_, ink)
        # clock at three
        stroke(ell(50, 13, 8, 8, 24), w_, closed=True, g=ink)
        stroke([(50, 13), (50, 19)], w_*0.9, g=ink); stroke([(50, 13), (55, 13)], w_*0.9, g=ink)
        _arrow((38, 13), (28, 13), w_, ink)
        # bucket hat
        stroke(bez((8, 10), (8, 20), (20, 20), (20, 10)), w_, g=ink)
        stroke([(3, 9), (25, 9), (21, 12), (7, 12), (3, 9)], w_, g=ink)
        letter_hen(80, 10, w_*0.8, ink)


def crayon(pts, g, w=LINE*1.7, closed=False):
    stroke(pts, w, closed=closed, g=g)


def opicka_sig(x, y, r=4):
    """Hanka's signature: her plush orangutan, drawn with crayons"""
    for sx in (-1, 1): crayon(ell(x + sx*r*1.05, y + r*0.3, r*0.38, r*0.38, 12), P.CRAYON_ORANGE, LINE*1.1, True)
    crayon(ell(x, y, r, r, 18), P.CRAYON_ORANGE, LINE*1.2, True)
    dot(x - r*0.35, y + r*0.15, 0.6, 0.0); dot(x + r*0.35, y + r*0.15, 0.6, 0.0)
    crayon(bez((x - r*0.4, y - r*0.35), (x - r*0.1, y - r*0.6), (x + r*0.1, y - r*0.6), (x + r*0.4, y - r*0.35)), P.CRAYON_BROWN, LINE*0.8)


def hanka_drawing(x, y, w=80, h=56, kind="print", rot=0):
    """Hanka's crayon report for Alica. kind: print (henhouse + giant boot print), tower (stopped clock,
    a man in a hat with a fishing rod), rock (boot rock, magpie, red-white float)"""
    with T(x, y, 1.0, rot=rot):
        _paper(w, h, 1.0)
        k = w/80
        if kind == "print":
            crayon([(8*k, 26*k), (8*k, 44*k), (18*k, 52*k), (28*k, 44*k), (28*k, 26*k), (8*k, 26*k)], P.CRAYON_BROWN)
            crayon(rrect(15*k, 26*k, 6*k, 8*k, 1), 0.1, LINE*1.4, True)
            crayon(ell(40*k, 38*k, 5*k, 4*k, 14), P.CRAYON_BROWN, LINE*1.4, True)
            crayon([(44*k, 40*k), (47*k, 41*k)], P.CRAYON_ORANGE, LINE*1.2)
            crayon([(39*k, 42*k), (40*k, 45*k), (42*k, 43*k)], P.CRAYON_RED, LINE*1.2)
            sole = ell(58*k, 26*k, 10*k, 20*k, 24)
            crayon(sole, P.CRAYON_BROWN, LINE*1.8, True)
            for yy in (14, 20, 30, 36):
                crayon([(50*k + i*3.2*k, (yy + (2.4 if i % 2 else 0))*k) for i in range(6)], P.CRAYON_BROWN, LINE*1.2)
            for sx in (40, 46): crayon([(sx*k, 8*k), (sx*k + 2*k, 12*k)], 0.2, LINE)
        elif kind == "tower":
            crayon([(14*k, 6*k), (14*k, 42*k), (26*k, 42*k), (26*k, 6*k)], P.CRAYON_BROWN)
            crayon([(12*k, 42*k), (20*k, 54*k), (28*k, 42*k)], P.CRAYON_GREEN)
            crayon(ell(20*k, 32*k, 4.5*k, 4.5*k, 16), 0.2, LINE*1.3, True)
            crayon([(20*k, 32*k), (20*k, 35.5*k)], 0.1, LINE*1.2); crayon([(20*k, 32*k), (23.5*k, 32*k)], 0.1, LINE*1.2)
            # big man with a bucket hat and a rod
            crayon(ell(56*k, 38*k, 5*k, 5*k, 16), P.CRAYON_BROWN, LINE*1.3, True)
            crayon([(50*k, 43*k), (62*k, 43*k), (59*k, 47*k), (53*k, 47*k), (50*k, 43*k)], P.CRAYON_GREEN)
            crayon([(56*k, 33*k), (56*k, 16*k)], P.CRAYON_BLUE)
            crayon([(56*k, 16*k), (50*k, 5*k)], P.CRAYON_BLUE); crayon([(56*k, 16*k), (62*k, 5*k)], P.CRAYON_BLUE)
            crayon([(46*k, 28*k), (66*k, 28*k)], P.CRAYON_BLUE)
            crayon([(66*k, 28*k), (76*k, 52*k)], P.CRAYON_BROWN, LINE*1.1)
        else:
            crayon([(8*k, 6*k), (8*k, 36*k), (22*k, 38*k), (24*k, 22*k), (40*k, 18*k), (42*k, 6*k), (8*k, 6*k)], 0.35)
            crayon(ell(56*k, 42*k, 6*k, 3.5*k, 14), 0.1, LINE*1.4, True)
            crayon([(50*k, 42*k), (40*k, 40*k)], 0.1, LINE*1.4)
            crayon([(62*k, 43*k), (66*k, 42*k)], 0.1, LINE*1.1)
            crayon(ell(60*k, 16*k, 2.6*k, 6*k, 14), P.CRAYON_RED, LINE*1.4, True)
            crayon([(60*k, 22*k), (60*k, 27*k)], 0.1, LINE)
        opicka_sig(w - 8*k, h - 8*k, 3.6*k)
