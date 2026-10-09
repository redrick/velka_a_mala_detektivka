"""Issue 7 (Joeyho velký den): babička's ring with the club star, her lavender hand cream and the smell trails Joey
follows, děda's snow shovel, the snow pile and the kids' fort of snow blocks, Joey's stash, the forester.

The comic prints in grey, so a smell is a wavy dashed line with its own little symbol (a lavender sprig for
babička's hand cream), never a colour."""
import math, random
from lib import ell, bez, rrect, resample
from style3 import *
from style3 import C, draw_arm, draw_legs, head_outline, face
import palette as P
from scenes3 import BG, s_, sh_
from chars3 import Person, _neck, star


# ------------------------------------------------------------------ the hidden-object game
def _bone_outline(L, r):
    """a cartoon bone along the x axis, total length about 2L, knob radius r: the outline of a bar and four knobs,
    found by casting rays from the middle"""
    kx = L - r
    def inside(px, py):
        if abs(px) <= kx and abs(py) <= r*0.6: return True
        return any((px - sx*kx)**2 + (py - sy*r*0.85)**2 <= r*r for sx in (-1, 1) for sy in (-1, 1))
    pts = []
    for i in range(96):
        a = i*math.tau/96; c, s_a = math.cos(a), math.sin(a); t = 0
        while inside(c*(t + 0.25), s_a*(t + 0.25)): t += 0.25
        pts.append((c*t, s_a*t))
    return pts


def hidden_bone(x, y, r=13, rot=20):
    """one of the 10 bones hidden in the issue. Old-bone tan inside a white halo and a black line, so it reads on
    white snow and on dark wood alike (the comic prints in grey)"""
    with T(x, y, 1.0, rot=rot):
        o = _bone_outline(r, r*0.38)
        stroke(o, LINE*4.4, closed=True, g=0.0, taper=False)
        stroke(o, LINE*2.8, closed=True, g=1.0, taper=False)
        fill(o, P.BONE_OLD)
        stroke(o, LINE*0.5, closed=True, g=0.0, taper=False)
        stroke([(-r*0.45, r*0.12), (r*0.45, r*0.12)], LINE*0.7, g=1.0)


def bone(x, y, s=1.0, rot=0, g=P.BONE):
    with T(x, y, s, rot=rot):
        shape(_bone_outline(10, 3.6), g, LINE*0.8)


# ------------------------------------------------------------------ babička's ring and her hand cream
def ring(x, y, s=1.0, rot=0, glint=True):
    """babička's gold ring, seen at a slant, with the little Klub Hvězdička star děda had engraved on top"""
    with T(x, y, s, rot=rot):
        shape(ell(0, 0, 7, 4.2, 30), P.RING_GOLD, LINE*0.9)
        shape(ell(0, 0.6, 4.6, 2.4, 24), 1.0, LINE*0.6)
        star(0, 3.6, 2.2, 0.2, LINE*0.4)
        if glint:
            for a in (40, 80, 120):
                ra = math.radians(a)
                stroke([(math.cos(ra)*9, 2 + math.sin(ra)*7), (math.cos(ra)*13, 2 + math.sin(ra)*10)], LINE*0.7)


def ring_big(x, y, s=1.0):
    """the ring close up, the engraved star readable"""
    with T(x, y, s):
        shape(ell(0, 0, 30, 18, 40), P.RING_GOLD, LINE*1.2)
        shape(ell(0, 2.5, 21, 11, 36), 1.0, LINE*0.9)
        stroke(ell(0, 0, 26.5, 15.5, 40), LINE*0.5, closed=True, g=0.4)
        star(0, 15.2, 4.4, 0.25, LINE*0.6)


def lavender_sprig(x, y, s=1.0, rot=0, g=None):
    """the smell symbol for babička's hand cream: a stem with small flower buds"""
    g = P.LAVENDER if g is None else g
    with T(x, y, s, rot=rot):
        stroke([(0, -5), (0, 6)], LINE*0.8, g=0.3)
        for i, (bx, by) in enumerate(((0, 7.5), (-1.6, 5), (1.6, 4.4), (-1.6, 2.2), (1.6, 1.6))):
            shape(ell(bx, by, 1.3, 1.8, 10), g, LINE*0.4)


def hand_cream(x, y, s=1.0, rot=0):
    """babička's tube of lavender hand cream"""
    with T(x, y, s, rot=rot):
        shape([(-6, 0), (6, 0), (5, 26), (-5, 26)], P.CREAM_TUBE, LINE*0.8)
        shape(rrect(-3, -6, 6, 6, 1.2), 0.3, LINE*0.6)
        stroke([(-6, 25), (6, 25)], LINE*1.2)
        lavender_sprig(0, 12, 1.0)


def smell_trail(pts, s=1.0, sym=True, every=70, seed=1, g=None):
    """a smell: a wavy dashed line through pts with lavender sprigs along it (pts in page coordinates)"""
    g = P.SMELL if g is None else g
    path = []
    for i in range(len(pts) - 1):
        (x0, y0), (x1, y1) = pts[i], pts[i + 1]
        path += [(x0 + (x1 - x0)*t/12, y0 + (y1 - y0)*t/12) for t in range(12)]
    path.append(pts[-1])
    path = resample(path, 1.5)
    out = []; d = 0
    for i, (px, py) in enumerate(path):
        a = path[max(0, i - 1)]; b = path[min(len(path) - 1, i + 1)]
        dx, dy = b[0] - a[0], b[1] - a[1]; L = math.hypot(dx, dy) or 1
        if i: d += math.hypot(px - path[i - 1][0], py - path[i - 1][1])
        w = math.sin(d/9.0)*3.2*s
        out.append((px - dy/L*w, py + dx/L*w, d))
    seg = []
    for px, py, d in out:
        if (d // (9*s)) % 2 == 0:
            seg.append((px, py))
        elif seg:
            if len(seg) > 1: stroke(seg, LINE*1.1*s, g=g, taper=False)
            seg = []
    if len(seg) > 1: stroke(seg, LINE*1.1*s, g=g, taper=False)
    if sym:
        r = random.Random(seed); nxt = every*0.5
        for px, py, d in out:
            if d >= nxt:
                lavender_sprig(px, py + 7*s, 1.1*s, r.uniform(-25, 25)); nxt += every


def babi_glove(x, y, s=1.0, rot=0):
    """babička's knitted glove"""
    with T(x, y, s, rot=rot):
        pts = [(-7, 0), (7, 0), (7, 14), (10, 16), (9, 19), (6, 18), (6, 26), (3, 26), (3, 20), (1, 28), (-2, 28),
               (-2, 20), (-4, 27), (-7, 26), (-7, 14)]
        shape(pts, P.BABI_GLOVE)
        shape([(-7, 0), (7, 0), (7, 5), (-7, 5)], P.BABI_GLOVE_CUFF, LINE*0.8)
        for k in range(-5, 7, 3): stroke([(k, 1), (k, 4)], LINE*0.4, g=0.4)


# ------------------------------------------------------------------ snow work
def shovel(x, y, s=1.0, rot=0, snow=True):
    """děda's wide snow shovel; (x, y) = bottom edge of the blade"""
    with T(x, y, s, rot=rot):
        tube([(0, 14), (0, 70)], 3.2, 3.0, P.SHOVEL_HANDLE, sh=0)
        shape([(-8, 70), (8, 70), (8, 74), (-8, 74)], 0.3, LINE*0.8)
        shape([(-20, 0), (20, 0), (16, 16), (-16, 16)], P.SHOVEL_BLADE, LINE)
        if snow: shape(bez((-17, 3), (-12, 12), (10, 13), (17, 3)) + [(-17, 3)], P.SNOW, LINE*0.6)


def snow_pile(x, y, w=120, h=45, seed=2):
    """the heap of shovelled snow beside the path; (x, y) = middle of its foot"""
    r = random.Random(seed)
    top = [(x - w/2, y)]
    for i in range(1, 9):
        t = i/9
        top.append((x - w/2 + w*t, y + h*math.sin(math.pi*t)**0.8 + r.uniform(-4, 4)))
    top.append((x + w/2, y))
    shape(top, P.SNOW, BG*1.1)
    for i in range(4):
        t = 0.2 + i*0.18
        s_(bez((x - w/2 + w*t, y + 3), (x - w/2 + w*t + 6, y + h*0.3), (x - w/2 + w*t + 2, y + h*0.55),
               (x - w/2 + w*t + 10, y + h*0.7)), BG*0.5, g=P.SNOW_SHADE)


def throw_arc(x0, y0, x1, y1, n=9, seed=4):
    """lumps of snow flying off the shovel onto the pile"""
    r = random.Random(seed)
    for i in range(n):
        t = (i + 1)/(n + 1)
        px = x0 + (x1 - x0)*t; py = y0 + (y1 - y0)*t + math.sin(math.pi*t)*40
        rr = r.uniform(2.4, 4.4)
        shape(ell(px, py, rr, rr*0.8, 10), P.SNOW, LINE*0.5)


def snow_spray(x, y, s=1.0, seed=5, n=10):
    """snow kicked up behind a digging dog"""
    r = random.Random(seed)
    for _ in range(n):
        a = r.uniform(0.3, 2.8); d = r.uniform(8, 26)*s
        shape(ell(x + math.cos(a)*d, y + math.sin(a)*d, 2.2*s, 1.8*s, 10), P.SNOW, LINE*0.45)


def snow_block(x, y, w=26, h=16, crack=False):
    """one sawn block of snow"""
    shape([(x, y), (x + w, y), (x + w, y + h), (x, y + h)], P.SNOW, LINE*0.8)
    stroke([(x + 2, y + 2), (x + w - 2, y + 2)], LINE*0.5, g=P.SNOW_SHADE)
    if crack:
        stroke([(x + w*0.3, y + h), (x + w*0.45, y + h*0.55), (x + w*0.4, y + h*0.3), (x + w*0.55, y)], LINE*0.9)


FORT_ROWS, FORT_COLS = 4, 7


def snow_fort(x, y, s=1.0, removed=(), cracked=None, door=True, flag=True):
    """the kids' snow fort seen from the front: brick-laid rows of blocks, battlements on top, a doorway.
    removed: (row, col) blocks taken out (row 0 at the bottom). Returns the page centre of every block that is
    still standing, by (row, col)."""
    bw, bh = 26, 16
    W = FORT_COLS*bw
    centres = {}
    with T(x, y, s):
        for row in range(FORT_ROWS):
            # brick bond: odd rows start and end with a half block
            widths = [bw]*FORT_COLS if row % 2 == 0 else [bw/2] + [bw]*(FORT_COLS - 1) + [bw/2]
            bx = -W/2
            for col, w_ in enumerate(widths):
                if (row, col) not in removed:
                    snow_block(bx, row*bh, w_, bh, crack=cracked == (row, col))
                    centres[(row, col)] = (x + (bx + w_/2)*s, y + (row*bh + bh/2)*s)
                bx += w_
        for col in range(0, FORT_COLS, 2):
            bx = -FORT_COLS*bw/2 + col*bw
            if (FORT_ROWS, col) not in removed:
                snow_block(bx, FORT_ROWS*bh, bw, bh*0.8)
        if door and not any(r_ < 2 and c_ in (3, 4) for r_, c_ in removed):
            shape(bez((-bw*0.5, 0), (-bw*0.5, bh*2.3), (bw*0.5, bh*2.3), (bw*0.5, 0)), 0.45, LINE)
        if flag:
            fx = FORT_COLS*bw/2 - bw*0.6
            stroke([(fx, FORT_ROWS*bh + bh*0.8), (fx, FORT_ROWS*bh + bh*0.8 + 40)], LINE*1.2, g=0.3)
            shape([(fx, FORT_ROWS*bh + bh*0.8 + 40), (fx + 22, FORT_ROWS*bh + bh*0.8 + 34), (fx, FORT_ROWS*bh + bh*0.8 + 28)],
                  P.RIBBON, LINE*0.8)
            star(fx + 8, FORT_ROWS*bh + bh*0.8 + 34, 3.2, 1.0, LINE*0.4)
    return centres


def block_saw(x, y, s=1.0, rot=0):
    """an old wood saw for cutting snow blocks"""
    with T(x, y, s, rot=rot):
        shape([(0, 0), (40, -3), (40, 5), (0, 6)], 0.85, LINE*0.8)
        for i in range(10): stroke([(2 + i*4, -0.4 - i*0.3), (4 + i*4, -2 - i*0.3)], LINE*0.5)
        shape(rrect(-14, -1, 15, 9, 3), P.SHOVEL_HANDLE, LINE*0.8)


# ------------------------------------------------------------------ Joey's stash and other things
def stash(x, y, w=50, h=16, items=("glove", "bone", "sock")):
    """Joey's secret stash under the woodshed, dug open: a dark hole in the snow with his treasures beside it"""
    from props_extra import old_sock
    fill(ell(x, y + h*0.9, w*1.3, h*0.9, 30), P.SNOW_SHADE)
    for dx, dy, rr in ((-w*1.05, h*0.6, 9), (w*1.1, h*0.9, 7), (w*0.7, h*1.6, 6), (-w*0.6, h*1.7, 8)):
        shape(ell(x + dx, y + dy, rr*1.3, rr*0.7, 16), P.SNOW, BG*0.7)
    shape(ell(x, y + h*0.5, w, h, 34), P.STASH_EARTH, BG*1.1)
    spots = {"glove": (-w*0.75, h*1.9, 1.0, -70), "bone": (w*0.2, h*2.3, 1.3, 15), "sock": (w*0.95, h*2.0, 1.0, 120)}
    for it in items:
        dx, dy, k, a = spots[it]
        if it == "glove": babi_glove(x + dx, y + dy, k, rot=a)
        elif it == "bone": bone(x + dx, y + dy, k, rot=a)
        elif it == "sock": old_sock(x + dx, y + dy, k, rot=a)


def foil(x, y, s=1.0, rot=0, sparkle=True):
    """a crumpled scrap of shiny wrapper foil (from one of babička's perníčky)"""
    with T(x, y, s, rot=rot):
        pts = [(-6, -3), (-2, -5), (3, -4), (6, -1), (5, 3), (1, 5), (-4, 4), (-7, 1)]
        shape(pts, P.FOIL, LINE*0.7)
        for a, b in (((-4, -2), (1, 2)), ((2, -3), (-1, 1)), ((3, 2), (5, -1))): stroke([a, b], LINE*0.4, g=0.45)
        if sparkle:
            for a in (30, 90, 150):
                ra = math.radians(a)
                stroke([(math.cos(ra)*8, math.sin(ra)*7), (math.cos(ra)*12, math.sin(ra)*10)], LINE*0.6)


def sausage(x, y, s=1.0, rot=0):
    with T(x, y, s, rot=rot):
        shape(bez((-10, 0), (-11, 5), (11, 5), (10, 0)) + bez((10, 0), (11, -5), (-11, -5), (-10, 0)), P.SAUSAGE, LINE*0.8)
        for sx in (-1, 1): stroke([(sx*10.5, 0), (sx*13, 0.8)], LINE*0.7)
        stroke(bez((-5, 2), (-2, 3), (2, 3), (5, 2)), LINE*0.5, g=1.0)


def woodshed(x, y, s=1.0):
    """the little woodshed at the back of the garden, logs stacked inside; (x, y) = middle of its foot"""
    with T(x, y, s):
        form([(-50, 0), (50, 0), (50, 62), (-50, 62)], P.PLANKS, w=BG, sdx=2, sdy=0)
        for xx in range(-46, 50, 10): stroke([(xx, 2), (xx, 60)], LINE*0.4, g=0.45)
        for row in range(3):
            for k in range(6):
                shape(ell(-34 + k*13 + (row % 2)*6, 14 + row*12, 6, 5.5, 16), P.SHOVEL_HANDLE, LINE*0.6)
                dot(-34 + k*13 + (row % 2)*6, 14 + row*12, 1.2, 0.4)
        shape([(-60, 60), (60, 60), (54, 76), (-54, 76)], P.FEEDER_ROOF, LINE)
        fill([(-60, 70), (60, 70), (54, 78), (-54, 78)], P.SNOW)


# ------------------------------------------------------------------ the forester (hajný)
HAJNY = dict(H=128, hr=11, hy=116, sh_y=100.5, sh_w=14, hip=58, knee=31, ankle=5, leg_w=(8.4, 6.8), arm_w=(7.2, 6.4),
             up=20, fo=18)


def hajny(x, y, s=1.0, flip=False, left="down", right="down", mood="happy", look=(0, 0), item=None, shadow=True,
          legs="stand", binoculars=True):
    """the village forester: long green coat with pockets, felt hat with a little brush, a big moustache,
    binoculars on a strap. He comes back in issue 8 (Stopy ve sněhu)."""
    k = Person(**HAJNY)
    if shadow: cast_shadow(x, y, 19*s, 3*s)
    with T(x, y, s, flip):
        draw_legs(k, legs, P.HAJNY_TROUSERS, boots=P.HAJNY_BOOTS, boot_top=k.ankle + 14)
        draw_arm(k, -1, left, P.HAJNY_COAT)
        tors = bez((-5.5, k.sh_y + 2.8), (-10, k.sh_y + 2.5), (-k.sh_w - 1.3, k.sh_y + 0.5), (-k.sh_w - 1.8, k.sh_y - 4)) + \
               bez((-k.sh_w - 1.8, k.sh_y - 4), (-17, 76), (-18, 56), (-19, 36)) + [(19, 36)] + \
               bez((19, 36), (18, 56), (17, 76), (k.sh_w + 1.8, k.sh_y - 4)) + \
               bez((k.sh_w + 1.8, k.sh_y - 4), (k.sh_w + 1.3, k.sh_y + 0.5), (10, k.sh_y + 2.5), (5.5, k.sh_y + 2.8))
        form(tors, P.HAJNY_COAT, sdx=-2.2, sdy=1.2)
        stroke([(0, k.sh_y + 1), (0, 37)], LINE*0.7)
        for by in (90, 78, 66, 54): shape(ell(-2.6, by, 1.0, 1.0, 10), P.BRASS, LINE*0.5)
        for sx in (-1, 1):
            shape([(sx*5, 52), (sx*15, 52), (sx*15, 62), (sx*5, 62)], P.HAJNY_COAT, LINE*0.7)
            stroke([(sx*5, 60), (sx*15, 60)], LINE*0.5)
            shape([(sx*3, k.sh_y + 2), (sx*10, k.sh_y - 6), (sx*7, k.sh_y - 10), (sx*1, k.sh_y - 1)], P.HAJNY_HAT, LINE*0.6)
        if binoculars:
            stroke(bez((-9, k.sh_y + 1), (-4, 86), (4, 86), (9, k.sh_y + 1)), LINE*0.7, g=0.25)
            for bx in (-3.4, 3.4): shape(rrect(bx - 2.8, 76, 5.6, 9, 1.4), 0.2, LINE*0.6)
        h, fa = draw_arm(k, 1, right, P.HAJNY_COAT)
        if item: item(*h)
        _neck(k, 3.2)
        r = k.hr; cy = k.hy
        for sx in (-1, 1): shape(ell(sx*r*0.98, cy - r*0.05, r*0.2, r*0.3, 14), P.SKIN, LINE*0.8)
        shape(head_outline(k), P.SKIN)
        face(0, cy, r, mood if mood not in ("grin",) else "happy", look)
        mst = bez((-r*0.75, cy - r*0.62), (-r*0.45, cy - r*0.22), (r*0.45, cy - r*0.22), (r*0.75, cy - r*0.62)) + \
              bez((r*0.75, cy - r*0.62), (r*0.35, cy - r*0.5), (-r*0.35, cy - r*0.5), (-r*0.75, cy - r*0.62))
        shape(mst, P.HAJNY_MOUSTACHE, LINE*0.8)
        if mood in ("grin", "laugh", "surprised"):
            shape(ell(0, cy - r*0.72, r*0.14, r*0.1, 12), P.MOUTH, LINE*0.6)
        crown = bez((-r*0.85, cy + r*0.55), (-r*0.9, cy + r*1.55), (r*0.9, cy + r*1.55), (r*0.85, cy + r*0.55)) + \
                [(-r*0.85, cy + r*0.55)]
        shape(crown, P.HAJNY_HAT)
        stroke(bez((-r*0.3, cy + r*1.45), (-r*0.1, cy + r*1.2), (r*0.1, cy + r*1.2), (r*0.3, cy + r*1.45)), LINE*0.6)
        shape([(-r*0.86, cy + r*0.55), (r*0.86, cy + r*0.55), (r*0.86, cy + r*0.72), (-r*0.86, cy + r*0.72)], 0.15, LINE*0.5)
        shape(bez((-r*1.45, cy + r*0.48), (-r*1.2, cy + r*0.68), (r*1.2, cy + r*0.68), (r*1.45, cy + r*0.48)) +
              bez((r*1.45, cy + r*0.48), (r*1.0, cy + r*0.4), (-r*1.0, cy + r*0.4), (-r*1.45, cy + r*0.48)), P.HAJNY_HAT, LINE*0.8)
        for k_ in range(5):                                           # the little brush on the hatband
            a = math.radians(70 + k_*10)
            stroke([(-r*0.6, cy + r*0.72), (-r*0.6 + math.cos(a)*r*0.9, cy + r*0.72 + math.sin(a)*r*0.9)], LINE*0.9, g=0.25)
