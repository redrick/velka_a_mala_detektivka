"""Issue 11 (Kam mizí vajíčka?): Easter at the chalupa. Babička's eight hens and Kropenatka the broody one, eggs and
kraslice (onion skins, wax, markers), the hen run with a gap under the wire, the barn with straw bales and Kropenatka's
secret nest, the magpie's nest, Věrka's rooster Pepík, the chicks, Alica's egg tally and the hidden kraslice."""
import math, random
import lib
from lib import ell, bez, rrect, resample
from style3 import *
from style3 import C
import palette as P
from scenes3 import BG, s_, sh_, sky, hills, ground, house, tree, cloud
from village import hen, henhouse
from chars3 import star
from letter import hand_text


def _panel_fill(p, g, alpha=None):
    fill([(p.x, p.y), (p.x + p.w, p.y), (p.x + p.w, p.y + p.h), (p.x, p.y + p.h)], g, alpha)


# ================================================================== eggs
def egg_pts(cx, cy, r, n=40):
    """an egg standing on its blunt end, r = half its height"""
    out = []
    for i in range(n):
        t = math.tau*i/n
        out.append((cx + r*0.72*math.cos(t)*(1 - 0.16*math.sin(t)), cy + r*math.sin(t)))
    return out


def egg(x, y, s=1.0, rot=0, g=None):
    """a plain egg, (x, y) = its centre, local height ~14"""
    with T(x, y, s, rot=rot):
        e = egg_pts(0, 0, 7)
        shape(e, P.EGG if g is None else g, LINE*0.8)
        stroke(bez((-3.2, 3.5), (-3.8, 1), (-3.6, -1.5), (-2.6, -3.5)), LINE*0.5, g=1.0)


def _pattern(kind, r, seed):
    """the decoration of a kraslice, drawn in its own coordinates (egg centred on 0, 0, half height r)"""
    rd = random.Random(seed)
    if kind == "onion":
        leaf = bez((-r*0.1, -r*0.55), (-r*0.5, -r*0.1), (-r*0.3, r*0.4), (0, r*0.55)) + \
               bez((0, r*0.55), (r*0.3, r*0.4), (r*0.4, -r*0.1), (-r*0.1, -r*0.55))
        fill(leaf, P.EGG_SHADE)
        stroke([(-r*0.08, -r*0.5), (0, r*0.5)], LINE*0.5, g=P.ONION_DYE)
        for k in (-0.2, 0.05, 0.3):
            stroke([(-r*0.03 + k*0.1*r, k*r), (r*0.25, k*r + r*0.15)], LINE*0.4, g=P.ONION_DYE)
            stroke([(-r*0.03 + k*0.1*r, k*r), (-r*0.25, k*r + r*0.12)], LINE*0.4, g=P.ONION_DYE)
    elif kind == "wax":
        for yy in (-0.45, 0.0, 0.45):
            for xx in range(-3, 4):
                dot(xx*r*0.22 + (0.11*r if yy == 0 else 0), yy*r, r*0.07, 1.0)
        stroke([(-r, r*0.22), (r, r*0.22)], LINE*0.7, g=1.0)
        stroke([(-r, -r*0.22), (r, -r*0.22)], LINE*0.7, g=1.0)
    elif kind == "marker":
        zz = [(-r + i*r*0.25, (0.12 if i % 2 else -0.12)*r) for i in range(9)]
        stroke(zz, LINE*1.4, g=P.CRAYON_RED)
        for yy, g in ((0.45, P.CRAYON_BLUE), (-0.45, P.KRASLICE_GREEN)):
            for xx in range(-2, 3): dot(xx*r*0.28, yy*r, r*0.08, g)
    elif kind == "opicka":
        shape(ell(0, 0, r*0.34, r*0.3, 18), P.CRAYON_ORANGE, LINE*0.6)
        for ex in (-1, 1): shape(ell(ex*r*0.36, r*0.08, r*0.1, r*0.1, 10), P.CRAYON_ORANGE, LINE*0.5)
        dot(-r*0.1, r*0.06, r*0.04, 0.0); dot(r*0.1, r*0.06, r*0.04, 0.0)
        stroke(bez((-r*0.12, -r*0.12), (-r*0.05, -r*0.18), (r*0.05, -r*0.18), (r*0.12, -r*0.12)), LINE*0.5)
    elif kind == "star":
        star(0, 0, r*0.36, P.KRASLICE_YELLOW, LINE*0.6)
        for yy in (0.62, -0.62): stroke([(-r, yy*r), (r, yy*r)], LINE*0.8, g=P.CRAYON_BLUE)
    elif kind == "stripes":
        for k, g in enumerate((P.CRAYON_BLUE, P.KRASLICE_YELLOW, P.CRAYON_RED, P.KRASLICE_GREEN)):
            yy = (-0.6 + k*0.4)*r
            fill([(-r, yy - r*0.1), (r, yy - r*0.1), (r, yy + r*0.1), (-r, yy + r*0.1)], g)


KR_BASE = {"onion": P.ONION_DYE, "wax": P.WAX_DYE, "marker": P.EGG, "opicka": P.EGG, "star": P.WAX_DYE,
           "stripes": P.EGG}


def kraslice(x, y, s=1.0, rot=0, kind="onion", seed=1):
    """a decorated Easter egg: onion (onion-skin brown with a leaf print), wax (blue with white wax dots),
    marker (zigzag and dots), opicka (Hanka's, with opička), star (Klub Hvězdička), stripes"""
    with T(x, y, s, rot=rot):
        e = egg_pts(0, 0, 7)
        fill(e, KR_BASE[kind])
        C.saveState(); C.clipPath(poly(e), stroke=0, fill=0)
        _pattern(kind, 7, seed)
        C.restoreState()
        stroke(e, LINE*0.8, closed=True)
        stroke(bez((-3.2, 3.5), (-3.8, 1), (-3.6, -1.5), (-2.6, -3.5)), LINE*0.5, g=1.0, alpha=0.7)


HID_KINDS = ("marker", "stripes", "wax", "onion", "star")


def hidden_kraslice(x, y, r=13, rot=0, kind="marker"):
    """one of the 10 kraslice hidden in the issue: a white halo and a black line round it, so it reads on any ground.
    r = half its height"""
    with T(x, y, 1.0, rot=rot):
        e = egg_pts(0, 0, r)
        stroke(e, LINE*4.4, closed=True, g=0.0, taper=False)
        stroke(e, LINE*2.8, closed=True, g=1.0, taper=False)
        fill(e, KR_BASE[kind])
        C.saveState(); C.clipPath(poly(e), stroke=0, fill=0)
        _pattern(kind, r, 3)
        C.restoreState()
        stroke(e, LINE*0.6, closed=True, g=0.0, taper=False)


def egg_basket(x, y, s=1.0, n=7, kinds=None, seed=2):
    """babička's wicker egg basket with a handle, n eggs on top (kinds = kraslice kinds instead of plain eggs).
    Local width ~44"""
    rd = random.Random(seed)
    with T(x, y, s):
        stroke(bez((-20, 18), (-18, 46), (18, 46), (20, 18)), LINE*2.6)
        stroke(bez((-20, 18), (-18, 46), (18, 46), (20, 18)), LINE*1.2, g=P.PLANKS)
        spots = [(-12, 20), (-4, 21), (4, 21), (12, 20), (-8, 25), (0, 26), (8, 25), (-3, 30), (4, 30)][:n]
        for i, (ex, ey) in enumerate(sorted(spots, key=lambda q: -q[1])):
            if kinds: kraslice(ex, ey, 0.8, rd.uniform(-20, 20), kinds[i % len(kinds)], seed + i)
            else: egg(ex, ey, 0.8, rd.uniform(-20, 20))
        body = [(-21, 18), (21, 18), (16, 0), (-16, 0)]
        shape(body, P.PLANKS)
        for k in range(1, 4): stroke([(-21 + k*1.25, 18 - k*4.5), (21 - k*1.25, 18 - k*4.5)], LINE*0.5)
        for k in range(-16, 18, 5): stroke([(k*1.0, 1), (k*1.25, 17)], LINE*0.4)


def onion_skins(x, y, s=1.0, n=9, seed=4):
    rd = random.Random(seed)
    with T(x, y, s):
        for i in range(n):
            cx, cy = rd.uniform(-16, 16), rd.uniform(0, 8)
            a = rd.uniform(0, 180)
            pts = ell(cx, cy, rd.uniform(4, 7), rd.uniform(1.6, 3), 14, 0, 300, rot=a)
            shape(pts, P.ONION_DYE, LINE*0.5)


def dye_pot(x, y, s=1.0, dye=None):
    """a small pot of egg dye with a spoon in it"""
    with T(x, y, s):
        shape([(-16, 0), (16, 0), (18, 22), (-18, 22)], P.DYE_POT)
        shape(ell(0, 22, 18, 3.4, 24), P.ONION_DYE if dye is None else dye, LINE*0.8)
        for sx in (-1, 1): shape(rrect(sx*18 - (4 if sx > 0 else 0) + (0 if sx > 0 else -4) + 2*sx, 15, 6, 3, 1.4), P.DYE_POT, LINE*0.6)
        stroke([(6, 22), (14, 36)], LINE*1.6)


def candle(x, y, s=1.0, lit=True):
    with T(x, y, s):
        shape(rrect(-3, 0, 6, 18, 1.5), P.CANDLE, LINE*0.7)
        stroke([(0, 18), (0, 21)], LINE*0.6)
        if lit:
            shape(bez((0, 20), (-3, 23), (-1.5, 27), (0, 30)) + bez((0, 30), (1.5, 27), (3, 23), (0, 20)), P.FLAME, LINE*0.5)
        shape(ell(0, 0, 7, 2.2, 16), 0.85, LINE*0.6)


def fixa(x, y, s=1.0, rot=0, g=None):
    """a felt-tip marker"""
    with T(x, y, s, rot=rot):
        shape(rrect(-9, -1.8, 14, 3.6, 1.2), 0.95, LINE*0.6)
        shape(rrect(5, -1.9, 4, 3.8, 1), P.CRAYON_RED if g is None else g, LINE*0.6)
        shape([(9, -1), (11.5, 0), (9, 1)], P.CRAYON_RED if g is None else g, LINE*0.5)


def egg_cracked(x, y, s=1.0, chick=True):
    """a hatching egg: the top cracked off, a chick's head poking out"""
    with T(x, y, s):
        e = egg_pts(0, 0, 7)
        if chick:
            shape(ell(0.5, 4.5, 3.6, 3.4, 16), P.CHICK, LINE*0.7)
            shape([(3.6, 5.2), (6.2, 4.6), (3.6, 3.8)], P.HEN_BEAK, LINE*0.5)
            dot(2, 5.8, 0.6, 0.0)
        zig = [(-5, 2), (-3, 4), (-1.5, 1.5), (0, 4.2), (1.5, 1.5), (3, 4), (5, 2)]
        shape(_egg_bottom(e) + zig, P.EGG, LINE*0.8)
        shape([(-2, 9), (-0.5, 11.5), (1.2, 9.2), (2.2, 11.6), (0, 13)], P.EGG, LINE*0.6)


def _egg_bottom(e):
    """the egg outline below the crack, from its right side round the bottom to its left side"""
    pts = [q for q in e if q[1] <= 2]
    pts.sort(key=lambda q: (math.atan2(q[1], q[0]) - 0.3) % math.tau, reverse=True)
    return pts


# ================================================================== birds
HEN_LOOKS = (P.HEN, P.HEN_WHITE, P.HEN_DARK, P.HEN, P.HEN_WHITE, P.HEN_DARK, P.HEN)


def slepice(x, y, s=1.0, flip=False, pose="stand", who=0):
    """one of babička's seven other hens (who = 0..6: brown, white or dark)"""
    hen(x, y, s, flip, pose, HEN_LOOKS[who % len(HEN_LOOKS)])


def kropenatka(x, y, s=1.0, flip=False, pose="stand", puff=False, straw=False, grumpy=None):
    """Kropenatka, the grey hen with lots of white freckles (drawn like village.hen, with a freckled body and a folded wing). puff: feathers
    fluffed up (a broody hen); straw: stalks caught in her feathers"""
    grumpy = puff if grumpy is None else grumpy
    g = P.KROPENATKA
    by = 2 if pose == "sit" else 9
    rd = random.Random(7)
    with T(x, y, s, flip):
        if pose != "sit":
            for lx in (-3, 3):
                stroke([(lx, by + 2), (lx + 0.5, 1)], LINE*0.9, g=P.HEN_LEG)
                stroke([(lx - 2.5, 0.4), (lx + 3.5, 0.4)], LINE*0.8, g=P.HEN_LEG)
        if puff:
            fl = []
            for i in range(14):
                a0, a1 = math.tau*i/14, math.tau*(i + 1)/14
                p0 = (math.cos(a0)*14, by + 9 + math.sin(a0)*10.5); p1 = (math.cos(a1)*14, by + 9 + math.sin(a1)*10.5)
                am = (a0 + a1)/2; m = (math.cos(am)*16, by + 9 + math.sin(am)*12.2)
                fl += bez(p0, m, m, p1, 5)
            shape(fl, g, LINE*0.8)
        tail = [(-9, by + 8)] + bez((-9, by + 8), (-14, by + 14), (-17, by + 21), (-14, by + 23)) + \
               bez((-14, by + 23), (-12, by + 17), (-10, by + 14), (-5, by + 13))
        shape(tail, g)
        body = ell(0, by + 8, 11.5, 8.5, 32)
        form(body, g, sdx=-1.2, sdy=1)
        C.saveState(); C.clipPath(poly(body), stroke=0, fill=0)
        for _ in range(60):
            dot(rd.uniform(-12, 12), by + 8 + rd.uniform(-8, 8), rd.uniform(0.45, 0.7), P.KROPENATKA_DOT)
        C.restoreState()
        wing = bez((5, by + 11), (2, by + 14), (-6, by + 13), (-9, by + 8)) + [(-6, by + 7.5), (-7.5, by + 5.5), (-3.5, by + 5.8),
                                                                               (-4.5, by + 3.8)] + bez((-4.5, by + 3.8), (1, by + 4), (5, by + 7), (5, by + 11))
        shape(wing, P.KROPENATKA_WING, LINE*0.6)
        for _ in range(6):
            dot(rd.uniform(-5, 3), by + rd.uniform(6.5, 11), 0.5, P.KROPENATKA_DOT)
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
        for dx, dy in ((-2.2, -1.5), (-1, -3), (-2.8, 1)):
            dot(hx + dx, hy + dy, 0.45, P.KROPENATKA_DOT)
        if grumpy and pose != "peck":
            stroke([(hx + 0.2, hy + 2.7), (hx + 3, hy + 1.8)], LINE*0.9)
        if straw:
            for a_, b_ in (((-13, by + 15), (-2, by + 18)), ((-6, by + 2), (7, by + 4)), ((1, by + 13), (12, by + 9)),
                           ((-15, by + 6), (-6, by + 9))):
                stroke([a_, b_], LINE*2.4, g=0.0, taper=False); stroke([a_, b_], LINE*1.3, g=P.STRAW, taper=False)


def nest(x, y, s=1.0, eggs=9, hen_on=True, straw_g=None):
    """Kropenatka's secret nest: a ring of straw with eggs, and (hen_on) Kropenatka sitting puffed up on them.
    Local width ~44"""
    rd = random.Random(5)
    with T(x, y, s):
        shape(ell(0, 4, 22, 7, 30), P.STRAW_DARK if straw_g is None else straw_g, LINE*0.8)
        spots = [(-10, 6), (-3, 7), (4, 7), (11, 6), (-7, 3), (0, 2.5), (7, 3), (-13, 3), (13, 3)][:eggs]
        if not hen_on:
            for ex, ey in sorted(spots, key=lambda q: -q[1]): egg(ex, ey + 3, 0.75, rd.uniform(-25, 25))
        else:
            for ex, ey in ((-14, 4), (14, 4), (-9, 1.5), (9, 1.5)): egg(ex, ey + 3, 0.7, rd.uniform(-25, 25))
        for i in range(26):
            a = rd.uniform(0, math.tau); rr = rd.uniform(15, 23)
            px, py = math.cos(a)*rr, 4 + math.sin(a)*rr*0.32
            if not hen_on or py < 4:
                stroke([(px, py), (px + rd.uniform(-7, 7), py + rd.uniform(-2, 2))], LINE*0.7, g=P.STRAW)
    if hen_on:
        kropenatka(x, y + 2*s, s*1.05, False, "sit", puff=True)
        with T(x, y, s):
            for i in range(10):
                px = -20 + i*4.4
                stroke([(px, 2), (px + rd.uniform(-5, 5), 6 + rd.uniform(-1, 2))], LINE*0.8, g=P.STRAW)


def kohout(x, y, s=1.0, flip=False, crow=False):
    """Pepík, Věrka's rooster: tall, a big comb and wattles, a sickle tail. Local height ~46"""
    with T(x, y, s, flip):
        for lx in (-3.5, 3.5):
            stroke([(lx, 13), (lx + 0.5, 1)], LINE*1.1, g=P.HEN_LEG)
            stroke([(lx - 3, 0.4), (lx + 4, 0.4)], LINE*0.9, g=P.HEN_LEG)
            stroke([(lx - 1, 5), (lx - 3, 4)], LINE*0.8, g=P.HEN_LEG)
        for k, (dx, dy, g) in enumerate(((-24, 40, P.ROOSTER_TAIL), (-28, 32, P.ROOSTER_TAIL), (-26, 24, P.ROOSTER_TAIL))):
            sick = bez((-10, 18 + k*2), (-14, 26 + k*4), (dx - 4, dy + 2), (dx, dy - 10)) + \
                   bez((dx, dy - 10), (dx + 2, dy - 4), (-12, 24 + k*2), (-8, 16 + k*2))
            shape(sick, g, LINE*0.8)
        body = ell(0, 19, 12.5, 9.5, 32, rot=12)
        form(body, P.ROOSTER, sdx=-1.2, sdy=1)
        stroke(bez((-7, 21), (-2, 15), (5, 15), (7, 19)), LINE*0.6)
        neck = [(5, 41), (14, 41)] + bez((14, 41), (16, 36), (15.5, 31), (13, 27)) + \
               [(11, 24), (9.5, 27.5), (7.5, 24.5), (6, 28), (3.5, 25.5), (3, 29)] + bez((3, 29), (2.5, 33), (3.5, 37), (5, 41))
        shape(neck, P.ROOSTER_HACKLE, LINE*0.8)
        for k in range(3): stroke(bez((6 + k*3, 38), (6 + k*3, 34), (6.5 + k*3, 31), (5.5 + k*3, 28)), LINE*0.4)
        hx, hy = (11, 42)
        shape(ell(hx, hy, 5, 4.8, 20), P.ROOSTER, LINE*0.9)
        comb = [(hx - 4, hy + 3)]
        for k in range(5):
            comb += [(hx - 3.6 + k*1.9, hy + 8 + (k % 2)*1.5 + (2 if k == 2 else 0)), (hx - 2.6 + k*1.9, hy + 4.5)]
        comb += [(hx + 4, hy + 3)]
        shape(comb, P.HEN_COMB, LINE*0.7)
        if crow:
            shape([(hx + 4.4, hy + 1.6), (hx + 10, hy + 3.6), (hx + 4.6, hy + 0.2)], P.HEN_BEAK, LINE*0.6)
            shape([(hx + 4.4, hy - 0.4), (hx + 9.4, hy - 2.6), (hx + 4.2, hy - 1.6)], P.HEN_BEAK, LINE*0.6)
        else:
            shape([(hx + 4.4, hy + 0.8), (hx + 9, hy - 0.6), (hx + 4.4, hy - 1.8)], P.HEN_BEAK, LINE*0.6)
        shape(ell(hx + 3.2, hy - 4.6, 1.6, 3, 12), P.HEN_COMB, LINE*0.5)
        dot(hx + 1.8, hy + 1.2, 1.0, 0.0)


def kure(x, y, s=1.0, flip=False, pose="stand"):
    """a fluffy chick (local height ~16). pose: stand, peck"""
    with T(x, y, s, flip):
        for lx in (-1.6, 1.6):
            stroke([(lx, 3), (lx, 0.3)], LINE*0.7, g=P.HEN_LEG)
            stroke([(lx - 1.5, 0.3), (lx + 2, 0.3)], LINE*0.6, g=P.HEN_LEG)
        body = notch(ell(0, 6.5, 6.5, 5, 30), 0.5, 4)
        shape(body, P.CHICK, LINE*0.8)
        stroke(bez((-3, 7), (-1, 5), (2, 5.5), (3, 7.5)), LINE*0.5)
        hx, hy = (6, 5) if pose == "peck" else (4, 12)
        shape(notch(ell(hx, hy, 3.8, 3.6, 20), 0.4, 4), P.CHICK, LINE*0.8)
        shape([(hx + 3.3, hy + 0.8), (hx + 6, hy), (hx + 3.3, hy - 0.8)], P.HEN_BEAK, LINE*0.5)
        dot(hx + 1.4, hy + 1, 0.7, 0.0)


def pirko(x, y, s=1.0, rot=0):
    """one of Kropenatka's speckled feathers"""
    with T(x, y, s, rot=rot):
        vane = bez((0, 0), (-4.5, 6), (-4, 16), (0, 24)) + bez((0, 24), (4, 16), (4.5, 6), (0, 0))
        shape(vane, P.KROPENATKA, LINE*0.7)
        stroke([(0, -4), (0, 22)], LINE*0.6)
        for yy in (6, 11, 16):
            stroke([(0, yy), (-3, yy + 3)], LINE*0.35); stroke([(0, yy - 2), (3, yy + 1)], LINE*0.35)
        for dx, dy in ((-2.2, 5), (2, 9), (-2.4, 13), (1.8, 17), (-1, 20), (2.4, 4)):
            dot(dx, dy, 0.8, P.KROPENATKA_DOT)


def hen_print(x, y, s=1.0, rot=0, g=None):
    """a hen's three-toed print (toes forward = +y)"""
    with T(x, y, s, rot=rot):
        for a in (-38, 0, 38):
            ra = math.radians(90 + a)
            stroke([(0, 0), (math.cos(ra)*8, math.sin(ra)*8)], LINE*1.3, g=P.MUD_DARK if g is None else g)
        stroke([(0, 0), (0, -3)], LINE*1.2, g=P.MUD_DARK if g is None else g)


def hen_trail(pts, n=6, s=1.0, g=None):
    """hen prints walking along a polyline"""
    Pp = resample(pts, 2.0)
    for i in range(n):
        j = min(len(Pp) - 2, int(i*(len(Pp) - 2)/max(1, n - 1)))
        (x0, y0), (x1, y1) = Pp[j], Pp[j + 1]
        a = math.degrees(math.atan2(y1 - y0, x1 - x0)) - 90
        off = 4*s*(1 if i % 2 else -1)
        nx, ny = -math.sin(math.radians(a + 90)), math.cos(math.radians(a + 90))
        hen_print(x0 + nx*off, y0 + ny*off, s, a, g)


# ================================================================== the run, the barn
def run_fence(x0, x1, y, h=48, gap_at=None, gap_w=30, posts=60):
    """chicken wire on wooden posts round the hen run. gap_at = x of a scooped-out gap under the wire"""
    C.saveState(); C.clipPath(poly([(x0, y), (x1, y), (x1, y + h), (x0, y + h)]), stroke=0, fill=0)
    step = 8
    k = x0 - h
    while k < x1 + h:
        stroke([(k, y), (k + h, y + h)], LINE*0.35, g=P.WIRE)
        stroke([(k + h, y), (k, y + h)], LINE*0.35, g=P.WIRE)
        k += step
    C.restoreState()
    if gap_at is not None:
        fill(bez((gap_at - gap_w/2, y + 1), (gap_at - gap_w*0.35, y - 9), (gap_at + gap_w*0.35, y - 9), (gap_at + gap_w/2, y + 1)), P.MUD)
        shape(bez((gap_at - gap_w*0.4, y), (gap_at - gap_w*0.3, y - 6), (gap_at + gap_w*0.3, y - 6), (gap_at + gap_w*0.4, y)), P.MUD_DARK, LINE*0.6)
        stroke(bez((gap_at - gap_w/2, y + 2), (gap_at - gap_w*0.2, y + 9), (gap_at + gap_w*0.2, y + 9), (gap_at + gap_w/2, y + 2)), LINE*0.7, g=P.WIRE)
    stroke([(x0, y + h), (x1, y + h)], LINE*0.8, g=P.WIRE)
    xx = x0
    while xx <= x1 + 1:
        sh_([(xx - 2.5, y - 3), (xx + 2.5, y - 3), (xx + 2.5, y + h + 4), (xx - 2.5, y + h + 4)], P.POST)
        xx += posts


def balik(x, y, w=60, h=30, seed=1, g=None):
    """a straw bale, (x, y) = bottom left"""
    rd = random.Random(seed)
    form(rrect(x, y, w, h, 4), P.STRAW if g is None else g, w=BG, sdx=2, sdy=0, sh=0.1)
    C.saveState(); C.clipPath(poly(rrect(x, y, w, h, 4)), stroke=0, fill=0)
    for _ in range(int(w*h/40)):
        px, py = x + rd.uniform(0, w), y + rd.uniform(0, h)
        stroke([(px, py), (px + rd.uniform(-8, 8), py + rd.uniform(-1.5, 1.5))], LINE*0.4, g=P.STRAW_DARK)
    C.restoreState()
    for f in (0.28, 0.72):
        stroke([(x + w*f, y), (x + w*f, y + h)], LINE*0.9, g=0.3)


def stodola(x, y, s=1.0, door_open=False, hole=True):
    """the old barn behind the chalupa: dark planks, a steep roof, big double doors, and a low hole between two
    boards where a hen fits through. (x, y) = bottom centre, local width ~150"""
    with T(x, y, s):
        wall = [(-75, 0), (75, 0), (75, 70), (-75, 70)]
        form(wall, P.BARN, w=BG*1.2, sdx=2, sdy=0, sh=0.1)
        for xx in range(-69, 75, 9): s_([(xx, 1), (xx, 69)], BG*0.45)
        sh_([(-86, 66), (0, 128), (86, 66), (86, 60), (0, 122), (-86, 60)], P.BARN_ROOF)
        sh_([(-75, 70), (0, 122), (75, 70)], P.BARN)
        for xx in range(-60, 61, 9): s_([(xx, 71), (xx, 70 + (75 - abs(xx))*0.69)], BG*0.4)
        sh_(ell(0, 92, 8, 8, 20), P.BARN_DARK)
        if door_open:
            sh_([(-26, 0), (26, 0), (26, 58), (-26, 58)], P.BARN_DARK)
            form([(-26, 0), (-44, -2), (-44, 56), (-26, 58)], P.BARN, w=BG, sdx=0, sdy=0, sh=0)
            form([(26, 0), (44, -2), (44, 56), (26, 58)], P.BARN, w=BG, sdx=0, sdy=0, sh=0)
            for k in range(4): balik(-20 + (k % 2)*20, 0 + (k//2)*16, 20, 16, k)
        else:
            sh_([(-26, 0), (26, 0), (26, 58), (-26, 58)], P.BARN)
            for xx in range(-22, 26, 8): s_([(xx, 1), (xx, 57)], BG*0.4)
            s_([(0, 0), (0, 58)], BG*0.9)
            s_([(-26, 0), (0, 58)], BG*0.7); s_([(26, 0), (0, 58)], BG*0.7)
            sh_(rrect(-6, 26, 4, 8, 1), P.IRON)
        if hole:
            sh_(bez((44, 0), (45, 7), (53, 7), (54, 0)) + [(44, 0)], P.BARN_DARK)


def barn_inside(p, floor=0.1, gap_x=0.62, light=True, seed=3, dark=0.3):
    """inside the barn: plank walls with bright cracks, a wall of straw bales, and a dark gap low between two bales
    (only Hanka fits). Returns (floor y, gap centre x, gap centre y)"""
    _panel_fill(p, P.BARN)
    for xx in range(int(p.x), int(p.x + p.w), 14): s_([(xx, p.y), (xx, p.y + p.h)], BG*0.4)
    fy = p.Y(floor)
    if light:
        rd = random.Random(seed)
        for k in range(4):
            cx = p.X(rd.uniform(0.05, 0.4))
            fill([(cx, p.y + p.h), (cx + 3, p.y + p.h), (cx + 40, fy), (cx + 24, fy)], P.LANTERN_GLOW, 0.25)
    shape([(p.x - 5, p.y - 5), (p.x + p.w + 5, p.y - 5), (p.x + p.w + 5, fy), (p.x - 5, fy)], P.STRAW_DARK, BG)
    rd = random.Random(seed + 1)
    for _ in range(int(p.w/6)):
        px = p.x + rd.uniform(0, p.w); py = p.y + rd.uniform(0, fy - p.y)
        stroke([(px, py), (px + rd.uniform(-8, 8), py + rd.uniform(-1, 1))], LINE*0.5, g=P.STRAW)
    bw, bh = 74, 34
    gx = p.X(gap_x)
    x0 = gx + 14
    rows_ = int((p.Y(0.9) - fy)/bh)
    for r_ in range(rows_):
        yy = fy + r_*bh
        off = (r_ % 2)*bw/2
        xx = x0 - off
        while xx < p.x + p.w:
            balik(xx, yy, bw, bh, seed + r_*7 + int(xx))
            xx += bw
    xx = gx - 14 - bw
    for r_ in range(rows_ - 1):
        yy = fy + r_*bh
        balik(xx - (r_ % 2)*bw/2, yy, bw, bh, seed + 50 + r_)
    for r_ in range(1, rows_ - 1):
        balik(gx - bw/2, fy + r_*bh, bw, bh, seed + 90 + r_)
    gap = [(gx - 14, fy)] + bez((gx - 14, fy), (gx - 15, fy + bh*0.8), (gx - 8, fy + bh*1.05), (gx, fy + bh*1.05)) + \
          bez((gx, fy + bh*1.05), (gx + 9, fy + bh*1.05), (gx + 15, fy + bh*0.8), (gx + 14, fy)) + [(gx - 14, fy)]
    fill(gap, P.BARN_DARK)
    for k in range(6):
        sx = gx - 14 + k*5.6
        stroke([(sx, fy + 1), (sx + rd.uniform(-5, 5), fy + rd.uniform(3, 7))], LINE*0.6, g=P.STRAW)
    if dark: _panel_fill(p, 0.0, dark)
    return fy, gx, fy + bh*0.5


def kurnik_inside(p, floor=0.1, seed=2):
    """inside babička's henhouse: planks, a perch, three nest boxes with wood shavings; returns (floor y, list of
    nest-box centres)"""
    _panel_fill(p, P.HENHOUSE)
    for xx in range(int(p.x), int(p.x + p.w), 16): s_([(xx, p.y), (xx, p.y + p.h)], BG*0.4)
    fy = p.Y(floor)
    shape([(p.x - 5, p.y - 5), (p.x + p.w + 5, p.y - 5), (p.x + p.w + 5, fy), (p.x - 5, fy)], P.HOBLINY, BG)
    rd = random.Random(seed)
    for _ in range(int(p.w/5)):
        px = p.x + rd.uniform(0, p.w); py = p.y + rd.uniform(0, fy - p.y)
        stroke(ell(px, py, 2.4, 1.4, 8, 0, 270), LINE*0.4, g=P.STRAW_DARK)
    sh_([(p.X(0.02), p.Y(0.62)), (p.X(0.45), p.Y(0.62)), (p.X(0.45), p.Y(0.655)), (p.X(0.02), p.Y(0.655))], P.POST)
    boxes = []
    bw = p.w*0.15; by = p.Y(0.3)
    for i in range(3):
        bx = p.X(0.5) + i*(bw + 6)
        shape([(bx, by), (bx + bw, by), (bx + bw, by + bw*0.8), (bx, by + bw*0.8)], P.PLANKS)
        fill(ell(bx + bw/2, by + bw*0.35, bw*0.42, bw*0.28, 20), P.BARN_DARK)
        shape(bez((bx + 3, by + 2), (bx + bw*0.3, by + bw*0.28), (bx + bw*0.7, by + bw*0.28), (bx + bw - 3, by + 2)) + [(bx + 3, by + 2)],
              P.HOBLINY, LINE*0.6)
        boxes.append((bx + bw/2, by + 6))
    sh_([(p.X(0.5) - 4, by - 6), (p.X(0.5) + 3*(bw + 6), by - 6), (p.X(0.5) + 3*(bw + 6), by), (p.X(0.5) - 4, by)], P.POST)
    return fy, boxes


# ================================================================== the garden, the yard
def blossom_tree(x, y, s=1.0, seed=3):
    """a fruit tree in blossom"""
    tree(x, y, s, seed=seed)
    rd = random.Random(seed)
    with T(x, y, s):
        for _ in range(60):
            a = rd.uniform(0, math.tau); rr = math.sqrt(rd.random())
            px, py = math.cos(a)*rr*42, 88 + math.sin(a)*rr*32
            for k in range(5):
                b = k*math.tau/5
                dot(px + math.cos(b)*1.4, py + math.sin(b)*1.4, 1.1, P.BLOSSOM)
            dot(px, py, 0.5, P.KRASLICE_YELLOW)


def forsythia(x, y, s=1.0, seed=5):
    """zlatý déšť: arching sprays of yellow flowers"""
    rd = random.Random(seed)
    with T(x, y, s):
        for i in range(9):
            a = math.radians(rd.uniform(35, 145)); L = rd.uniform(30, 46)
            ex, ey = math.cos(a)*L, math.sin(a)*L*0.9
            pts = bez((0, 0), (ex*0.3, ey*0.7), (ex*0.8, ey*1.05), (ex*1.1, ey*0.75), 10)
            stroke(pts, LINE*0.8, g=P.BARK)
            for q in pts[2::1]:
                for _ in range(2):
                    dot(q[0] + rd.uniform(-2.5, 2.5), q[1] + rd.uniform(-2.5, 2.5), 1.5, P.FORSYTHIA)
        for _ in range(20):
            dot(rd.uniform(-30, 30), rd.uniform(8, 40), 1.4, P.FORSYTHIA)


def dvur(p, gy_f=0.4, seed=1, house_x=None, house_s=1.0, henhouse_x=None, henhouse_s=1.0, barn_x=None, barn_s=1.0,
         barn_kw=None, run=None, gap_at=None, trees=(), bushes=(), clouds=True, evening=False):
    """the chalupa yard in spring: sky, hills, grass, optionally the house, babička's henhouse, the old barn, the
    hen run (run = (x0, x1) fractions, gap_at = fraction), blossoming trees and forsythia. Returns the ground y"""
    gy = p.Y(gy_f)
    sky(p, P.SPRING_SKY)
    if clouds: cloud(p.X(0.62), p.Y(0.86), 0.7)
    hills(p, gy + p.h*0.07, 16, P.FAR_FIELD, seed)
    ground(p, gy, P.SPRING_GRASS)
    rd = random.Random(seed)
    for _ in range(int(p.w/26)):
        xx = p.x + rd.uniform(0, p.w); yy = rd.uniform(p.y + 4, gy - 6)
        for k in (-2, 0, 2): stroke([(xx + k, yy), (xx + k*1.6, yy + 4)], BG*0.5, g=0.4)
    for tx, ts in trees: blossom_tree(p.X(tx), gy - 4, ts, seed=seed + int(tx*10))
    if barn_x is not None: stodola(p.X(barn_x), gy - 2, barn_s, **(barn_kw or {}))
    if house_x is not None: house(p.X(house_x), gy - 4, house_s, smoke=True)
    if henhouse_x is not None: henhouse(p.X(henhouse_x), gy - 6, henhouse_s)
    for bx, bs in bushes: forsythia(p.X(bx), gy - 4, bs, seed=seed + int(bx*10))
    if run is not None:
        run_fence(p.X(run[0]), p.X(run[1]), gy - 16, 46, p.X(gap_at) if gap_at is not None else None)
    if evening:
        _panel_fill(p, P.WINTER_NIGHT, 0.35)
    return gy


# ================================================================== the magpie, sweets, the tally
def straci_hnizdo(x, y, s=1.0, items=True):
    """the magpie's domed nest of twigs, its treasures spilling out of the side: chocolate-egg foil, a ribbon and the
    teaspoon from issue 1. Local width ~60"""
    rd = random.Random(9)
    with T(x, y, s):
        shape(ell(0, 14, 28, 18, 30), P.BARK, LINE*0.9)
        for _ in range(70):
            a = rd.uniform(0, math.tau); rr = rd.uniform(0.4, 1.0)
            px, py = math.cos(a)*26*rr, 14 + math.sin(a)*16*rr
            b = rd.uniform(0, math.pi)
            stroke([(px, py), (px + math.cos(b)*9, py + math.sin(b)*5)], LINE*0.6, g=0.15)
        fill(ell(14, 12, 9, 7, 20), P.BARN_DARK)
        if items:
            foil_ball(-6, 30, 1.3)
            stroke(bez((6, 31), (14, 36), (22, 30), (34, 26)), LINE*2.2, g=0.0)
            stroke(bez((6, 31), (14, 36), (22, 30), (34, 26)), LINE*1.3, g=P.RIBBON)
            with T(-22, 24, 1.0, rot=35):
                shape(ell(6, 0, 4.2, 2.8, 16), 0.92, LINE*0.8); stroke([(-9, 0), (2, 0)], LINE*1.5)


def choc_egg(x, y, s=1.0, rot=0, open_=False):
    """a chocolate egg in stripy foil (open_: the foil peeled off half)"""
    with T(x, y, s, rot=rot):
        e = egg_pts(0, 0, 7)
        fill(e, P.CHOC)
        if not open_:
            fill(e, P.FOIL)
            C.saveState(); C.clipPath(poly(e), stroke=0, fill=0)
            for yy in (-3, 3): fill([(-8, yy - 1.2), (8, yy - 1.2), (8, yy + 1.2), (-8, yy + 1.2)], P.RIBBON)
            C.restoreState()
        else:
            C.saveState(); C.clipPath(poly(e), stroke=0, fill=0)
            fill([(-8, -8), (8, -8), (8, -1), (-8, 1)], P.FOIL)
            C.restoreState()
        stroke(e, LINE*0.8, closed=True)


def foil_ball(x, y, s=1.0):
    with T(x, y, s):
        pts = [(math.cos(math.tau*i/14)*(4.6 if i % 2 else 3.0), math.sin(math.tau*i/14)*(4.2 if i % 2 else 2.8)) for i in range(14)]
        shape(pts, P.FOIL, LINE*0.6)
        for a in (30, 100, 200):
            ra = math.radians(a)
            stroke([(math.cos(ra)*1.5, math.sin(ra)*1.5), (math.cos(ra)*3.4, math.sin(ra)*3.4)], LINE*0.4, g=1.0)


def egg_tally(x, y, w, rows_, size=14):
    """Alica's tally drawn in her notebook: one row per morning, 8 egg outlines; filled = an egg was there,
    dashed with a question mark = missing. rows_ = [(label, n present), ...]. (x, y) = top left"""
    lh = size*2.2
    for i, (lbl, n) in enumerate(rows_):
        yy = y - (i + 0.6)*lh
        hand_text(x, yy - size*0.35, size*2.6, lbl, "SHB", size, align="left")
        for k in range(8):
            ex = x + size*3.2 + k*(w - size*3.4)/8
            if k < n:
                egg(ex, yy, size/14*1.15)
            else:
                e = egg_pts(ex, yy, 7*size/14*1.15, 60)
                fill(e, 1.0)
                Pp = lib.resample(e + [e[0]], 0.8)
                for j in range(0, len(Pp) - 4, 8): stroke(Pp[j:j + 5], LINE*0.9, taper=False)
