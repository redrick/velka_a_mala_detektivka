"""Issue 5 (Kdo staví sněhuláky?): first snow, Bětka, snowmen that talk in pictures, star-soled prints."""
import math, random
from lib import ell, bez, rrect
from style3 import *
from style3 import C, Kid, arm_pts, draw_arm, draw_legs, head_outline, face, hand
import palette as P
from scenes3 import BG, s_, sh_, house, sky, hills, leaf, crate
from chars3 import star

# head centre (local y) and radius of the figures that get a winter hat, in figure units
HEADS = {"alica": (89.8, 9.8), "hanka": (70.2, 9.6), "tonda": (94, 9.9), "betka": (70.2, 9.6)}


# ------------------------------------------------------------------ the hidden-object game
def hidden_triangle(x, y, r=4.8):
    """one of the 10 triangles hidden in the issue: a small white triangle with a dot inside, so ordinary
    triangles in the drawing (roofs, fir trees, ears) don't count"""
    pts = [(x, y + r), (x - r*0.92, y - r*0.55), (x + r*0.92, y - r*0.55)]
    shape(pts, 0.98, 0.9)
    dot(x, y - r*0.05, r*0.16, 0.15)


# ------------------------------------------------------------------ clothes
# how wide the hat is around each hairstyle (Hanka's curls stick out), as a factor of the head radius
HAT_W = {"alica": 1.2, "hanka": 1.42, "tonda": 1.22, "betka": 1.14}


def winter_hat(x, y, s, who, g, flip=False, pompom=None):
    """a knitted hat pulled over a figure already drawn at (x, y, s); sits on the forehead, eyes stay free"""
    hy, hr = HEADS[who]
    with T(x, y, s, flip):
        r = hr*HAT_W[who]
        b0, b1 = hy + hr*0.5, hy + hr*0.86          # band: from just above the brows
        crown = hy + hr*(1.95 if who == "hanka" else 1.75)
        top = bez((-r*0.98, b1), (-r*1.02, crown), (r*1.02, crown), (r*0.98, b1)) + [(r*0.98, b0), (-r*0.98, b0)]
        shape(top, g)
        C.saveState(); C.clipPath(poly(top), stroke=0, fill=0)
        for k_ in range(-7, 8): stroke([(k_*2.6, b1), (k_*2.1, crown + 2)], LINE*0.35, g=0.35)
        C.restoreState()
        band = [(-r, b0), (r, b0), (r, b1), (-r, b1)]
        shape(band, g, LINE*0.9)
        offset_shadow(band, 0, 1.2, 0.12)
        if pompom is not None:
            pom(0, crown - hr*0.05, hr*0.46, pompom)


def pom(x, y, r, g=P.POMPOM):
    """a fluffy woollen pompom"""
    pts = []
    for i in range(28):
        a = i*math.tau/28; k = 1.0 + (0.13 if i % 2 else 0)
        pts.append((x + math.cos(a)*r*k, y + math.sin(a)*r*k))
    shape(pts, g, LINE*0.8)
    for i in range(6):
        a = i*math.tau/6 + 0.4
        stroke([(x + math.cos(a)*r*0.2, y + math.sin(a)*r*0.2), (x + math.cos(a)*r*0.7, y + math.sin(a)*r*0.7)], LINE*0.35, g=0.2)


def mitten(x, y, s=1.0, rot=0, g=P.HANKA_MITTEN):
    with T(x, y, s, rot=rot):
        m = bez((-4, 0), (-5, 6), (-4, 11), (0, 12)) + bez((0, 12), (4, 12), (5, 7), (4, 0)) + [(-4, 0)]
        shape(m, g)
        shape(bez((4, 5), (8, 6), (8, 10), (5, 10)) + [(4, 8)], g, LINE*0.8)
        shape([(-4.6, -3), (4.6, -3), (4.4, 1), (-4.4, 1)], 0.95, LINE*0.8)
        for k_ in range(-3, 4, 2): stroke([(k_, -2.6), (k_, 0.6)], LINE*0.3, g=0.4)


def _mitten_on(hx, hy_, g):
    shape(ell(hx, hy_, 2.7, 3.0, 16), g, LINE*0.8)


# ------------------------------------------------------------------ Bětka
def betka(x, y, s=1.0, flip=False, left="down", right="down", mood="happy", look=(0, 0), item=None,
          legs="stand", shadow=True, hat=True):
    """Bětka (6), Franta's granddaughter: red puffy jacket, cream hat with a red pompom, two short plaits,
    purple boots with stars on the soles, yellow mittens. Drawn on Hanka's frame; use s ≈ 1.12 × Hanka."""
    k = Kid(True)
    if shadow: cast_shadow(x, y, 12*s, 2.2*s)
    r, cy = k.hr, k.hy
    with T(x, y, s, flip):
        for sx in (-1, 1):
            pl = bez((sx*r*0.75, cy - r*0.1), (sx*r*1.25, cy - r*0.6), (sx*r*1.25, cy - r*1.4), (sx*r*1.05, cy - r*1.95)) + \
                 bez((sx*r*1.05, cy - r*1.95), (sx*r*0.82, cy - r*1.45), (sx*r*0.82, cy - r*0.75), (sx*r*0.5, cy - r*0.25))
            shape(pl, P.BETKA_HAIR)
            for k_ in range(3):
                yy = cy - r*(0.6 + k_*0.42)
                stroke([(sx*r*0.86, yy), (sx*r*1.18, yy - r*0.18)], LINE*0.4, g=0.6)
            dot(sx*r*1.02, cy - r*1.95, 1.3, P.POMPOM)
        draw_legs(k, legs, P.BETKA_TROUSERS, boots=P.BETKA_BOOTS, boot_top=k.ankle + 7.5)
        for ax_ in ((-4.2, 0), (4.2, 0)):
            star(ax_[0] + 1.5, 4.5, 1.5, 1.0, w=LINE*0.4)
        draw_arm(k, -1, left, P.BETKA_COAT)
        _, _, lh, _ = arm_pts(k, -1, left)
        _mitten_on(lh[0], lh[1], P.BETKA_MITTEN)
        coat = bez((-3.5, k.sh_y + 2.2), (-7, k.sh_y + 2.2), (-k.sh_w - 1.6, k.sh_y + 0.5), (-k.sh_w - 2.2, k.sh_y - 3)) + \
               bez((-k.sh_w - 2.2, k.sh_y - 3), (-12.5, 46), (-13, 36), (-12.6, 26)) + \
               bez((-12.6, 26), (-5, 24.5), (5, 24.5), (12.6, 26)) + \
               bez((12.6, 26), (13, 36), (12.5, 46), (k.sh_w + 2.2, k.sh_y - 3)) + \
               bez((k.sh_w + 2.2, k.sh_y - 3), (k.sh_w + 1.6, k.sh_y + 0.5), (7, k.sh_y + 2.2), (3.5, k.sh_y + 2.2)) + [(0, k.sh_y + 0.8)]
        fill(coat, P.BETKA_COAT)
        C.saveState(); C.clipPath(poly(coat), stroke=0, fill=0)
        for yy in (33, 41, 49): stroke(bez((-14, yy), (-5, yy - 1.2), (5, yy - 1.2), (14, yy)), LINE*0.6, g=0.25)
        C.restoreState()
        offset_shadow(coat, -2, 1, 0.12)
        stroke(coat, LINE, closed=True)
        stroke([(0, k.sh_y + 0.5), (0, 25)], LINE*0.6)
        for yy in (30, 38, 46): dot(1.6, yy, 0.6, 0.1)
        h, fa = draw_arm(k, 1, right, P.BETKA_COAT)
        if item: item(*h)
        _mitten_on(h[0], h[1], P.BETKA_MITTEN)
        # scarf
        sc = [(-5.5, k.sh_y + 4.6), (5.5, k.sh_y + 4.6), (5.8, k.sh_y + 0.4), (-5.8, k.sh_y + 0.4)]
        shape(sc, P.BETKA_MITTEN, LINE*0.8)
        shape([(2.5, k.sh_y + 1), (6.2, k.sh_y + 0.6), (7, k.sh_y - 7), (3.6, k.sh_y - 6.6)], P.BETKA_MITTEN, LINE*0.8)
        ho = head_outline(k)
        shape(ho, P.SKIN)
        face(0, cy, r, mood, look, young=True)
        shape(bez((-r*0.95, cy + r*0.25), (-r*0.5, cy + r*0.55), (r*0.5, cy + r*0.55), (r*0.95, cy + r*0.25)) +
              [(r*0.95, cy + r*0.55), (-r*0.95, cy + r*0.55)], P.BETKA_HAIR, LINE*0.6)
    if hat:
        winter_hat(x, y, s, "betka", P.BETKA_HAT, flip, pompom=P.POMPOM)


# ------------------------------------------------------------------ snowmen
def stick_arm(x0, y0, x1, y1, fingers=True):
    stroke([(x0, y0), (x1, y1)], LINE*1.3, g=P.BARK)
    if fingers:
        a = math.atan2(y1 - y0, x1 - x0)
        for da in (-0.6, 0.5):
            stroke([(x1, y1), (x1 + math.cos(a + da)*4, y1 + math.sin(a + da)*4)], LINE*0.9, g=P.BARK)


def snowman_b(x, y, s=1.0, right="down", left="down", nose="parsnip", item=None, pompom=False, flip=False, scarf=None):
    """Bětka's snowman (and the girls' answer): walnut eyes, pinecone buttons, stick arms.
    right/left: down, wave, hold (forward, item drawn at the end), up. nose: parsnip or carrot."""
    with T(x, y, s, flip):
        shape(ell(0, 15, 18, 15, 30), P.SNOW, LINE)
        fill(ell(-5, 11, 11, 9, 20), P.SNOW_SHADE, 0.6)
        shape(ell(0, 38, 12.5, 11, 28), P.SNOW, LINE)
        shape(ell(0, 56, 9, 8.6, 26), P.SNOW, LINE)
        for sx in (-1, 1): shape(ell(sx*3.4, 58.5, 1.5, 1.25, 12), P.WALNUT, LINE*0.4)
        if nose == "parsnip":
            shape([(0, 56.6), (12.5, 54.6), (0, 53.8)], P.PARSNIP, LINE*0.6)
            for k_ in (3, 6, 9): stroke([(k_, 55.9 - k_*0.12), (k_ + 0.6, 54.5 - k_*0.06)], LINE*0.3, g=0.5)
        elif nose == "none":                       # issue 8: eaten, only a hole in the snow
            shape(ell(0.6, 55.2, 1.6, 1.3, 10), P.SNOW_SHADE, LINE*0.4)
        elif nose == "stub":                       # issue 8: bitten off, a torn stub left
            shape([(0, 56.6), (3.4, 56.4), (2.6, 55.6), (3.8, 55), (2.8, 54.2), (3.2, 53.8), (0, 53.8)], P.PARSNIP, LINE*0.5)
        elif nose == "cone":                       # issue 8: a spruce cone, which the deer doesn't eat
            with T(5, 55.2, 1, rot=-90):
                shape(ell(0, 0, 2.4, 5.4, 14), P.PINECONE, LINE*0.5)
                for k_ in range(-3, 4, 2): stroke([(-2, k_), (2, k_ + 1)], LINE*0.3, g=0.75)
        else:
            shape([(0, 56.6), (11, 55), (0, 53.8)], P.CARROT, LINE*0.6)
        for k_ in range(5): dot(-3.2 + k_*1.6, 50.8 - abs(k_ - 2)*0.6, 0.6, 0.1)
        for by in (42, 36, 30):
            shape(ell(0, by, 1.6, 2.1, 12), P.PINECONE, LINE*0.4)
            stroke([(-1.3, by + 0.6), (1.3, by - 0.6)], LINE*0.25, g=0.8)
        ends = {"down": (22, 24), "wave": (20, 60), "hold": (26, 38), "up": (15, 66)}
        for side, pose in ((1, right), (-1, left)):
            ex, ey = ends[pose]
            stick_arm(side*10.5, 41, side*ex, ey, fingers=pose != "hold")
            if pose == "hold" and item is not None and side == 1:
                item(ex, ey)
        if scarf is not None:
            shape(bez((-9, 48.5), (-3, 46.5), (3, 46.5), (9, 48.5)) + [(9, 51), (-9, 51)], scarf, LINE*0.8)
        if pompom:
            pom(0, 65.5, 3.4)


def snow_dog(x, y, s=1.0, flip=False):
    """a dog of snow next to snowman no. 2: Bětka's picture of Joey"""
    with T(x, y, s, flip):
        shape(ell(0, 9, 17, 9, 28), P.SNOW, LINE)
        fill(ell(-4, 6, 10, 5, 18), P.SNOW_SHADE, 0.6)
        for lx in (-11, -4, 6, 12):
            shape(ell(lx, 2, 3.4, 3, 14), P.SNOW, LINE*0.8)
        shape(ell(18, 17, 8, 7, 24), P.SNOW, LINE)
        shape(ell(25, 15, 4.4, 3.2, 16), P.SNOW, LINE*0.8)
        dot(28.6, 15.6, 1.2, 0.1)
        dot(19.5, 19, 0.9, 0.1)
        leaf(14.5, 22.5, 4.5, 110, P.LEAF_DARK)
        leaf(20.5, 23.5, 4.5, 70, P.LEAF_DARK)
        stroke(bez((-16, 11), (-22, 14), (-24, 19), (-22, 23)), LINE*1.1, g=P.BARK)


# ------------------------------------------------------------------ prints and traces
def star_print(x, y, s=1.0, rot=0):
    """a small child's boot print with three stars on the sole"""
    with T(x, y, s, rot=rot):
        sole = bez((0, -8), (-4, -8), (-4.4, -2), (-3.6, 2)) + bez((-3.6, 2), (-3.4, 7), (3.4, 7), (3.6, 2)) + \
               bez((3.6, 2), (4.4, -2), (4, -8), (0, -8))
        shape(sole, P.PRINT_SHADE, 0.6)
        star(0, 3, 1.6, 1.0, w=0.4); star(-1.5, -1.6, 1.3, 1.0, w=0.4); star(1.5, -5, 1.3, 1.0, w=0.4)


def star_trail(points, s=1.0):
    """prints along a path of (x, y) points, alternating feet"""
    for i in range(len(points) - 1):
        (x0, y0), (x1, y1) = points[i], points[i + 1]
        a = math.degrees(math.atan2(y1 - y0, x1 - x0)) - 90
        nx, ny = -(y1 - y0), (x1 - x0); L = math.hypot(nx, ny) or 1
        side = 3.2*s*(1 if i % 2 else -1)
        star_print(x0 + nx/L*side, y0 + ny/L*side, s, a)


def big_print(x, y, s=1.0, rot=0):
    """Tonda's big winter boot print: ribs across, no stars"""
    with T(x, y, s, rot=rot):
        sole = bez((0, -11), (-6, -11), (-6.4, -2), (-5.4, 3)) + bez((-5.4, 3), (-5, 10), (5, 10), (5.4, 3)) + \
               bez((5.4, 3), (6.4, -2), (6, -11), (0, -11))
        shape(sole, P.PRINT_SHADE, 0.6)
        for yy in (-7, -3, 1, 5): stroke([(-4, yy), (4, yy)], 0.6, g=0.5)


def runner_tracks(x0, y0, x1, y1, gap=12):
    a = math.atan2(y1 - y0, x1 - x0); nx, ny = -math.sin(a)*gap/2, math.cos(a)*gap/2
    for sd in (-1, 1):
        stroke([(x0 + nx*sd, y0 + ny*sd), (x1 + nx*sd, y1 + ny*sd)], 1.4, g=P.PRINT_SHADE)
        stroke([(x0 + nx*sd, y0 + ny*sd - 1), (x1 + nx*sd, y1 + ny*sd - 1)], 0.5, g=0.55)


def red_thread(x, y, s=1.0):
    """a red woollen thread and a few fluffs, caught on the fence"""
    with T(x, y, s):
        stroke(bez((0, 0), (5, 4), (8, -3), (14, 1)), 1.1, g=P.POMPOM)
        for fx, fy in ((15, 1), (17, -1), (16, 3)): dot(fx, fy, 1.1, P.POMPOM)


def parsnip(x, y, s=1.0, rot=0):
    with T(x, y, s, rot=rot):
        shape(bez((-3, 0), (-3.4, -8), (-1, -18), (0, -26)) + bez((0, -26), (1, -18), (3.4, -8), (3, 0)) + [(-3, 0)],
              P.PARSNIP, LINE*0.7)
        for k_ in (-6, -11, -16): stroke([(-1.8, k_), (1.2, k_ - 1)], LINE*0.3, g=0.5)
        for a in (-25, 0, 25):
            leaf(math.sin(math.radians(a))*4, 4 + math.cos(math.radians(a))*2, 3.6, 90 + a, P.PARSNIP_LEAF)


def parsnip_crate(x, y, s=1.0):
    with T(x, y, s):
        for k_ in range(6):  # roots down in the crate, leaves up
            parsnip(-22 + k_*9, 34 + (k_ % 2)*3, 0.9, rot=(k_ % 3 - 1)*10)
        crate(-30, 0, 60, 26)
        parsnip(-6, 30, 0.8, rot=-78); parsnip(14, 29, 0.8, rot=-96)  # two lying on top, white roots showing


def small_boots(x, y, s=1.0):
    """Bětka's boots drying by the stove; one lies on its side so the stars on the sole show"""
    with T(x, y, s):
        b = [(-4, 18), (4, 18), (4.2, 6), (10, 4), (10.6, 0), (-4.4, 0)]
        shape(b, P.BETKA_BOOTS)
        stroke([(-4.4, 1.6), (10.4, 1.6)], LINE*0.6)
        with T(20, 6, 1, rot=90):
            sole = [(-8, -4.4), (10, -4.4), (11, 0), (10, 4.4), (-8, 4.4)]
            shape(sole, 0.75)
            for sx in (-4, 1, 6): star(sx, 0, 1.6, 1.0, w=0.4)


# ------------------------------------------------------------------ snowy scenery
def snow_roof(x, y, s=1.0):
    """a snow cap on top of scenes3.house at the same x, y, s"""
    with T(x, y, s):
        cap = [(-64, 52), (-60, 56.5)] + [(0, 108)] + [(60, 56.5), (64, 52), (58, 54), (52, 51), (0, 101), (-52, 51), (-58, 54)]
        shape(cap, P.SNOW, BG)
        for wx in (-35, 17): sh_([(wx - 3, 18.5), (wx + 21, 18.5), (wx + 20, 21.5), (wx - 2, 21.5)], P.SNOW, BG*0.6)


def snowy_house(x, y, s=1.0, smoke=True):
    house(x, y, s, smoke)
    snow_roof(x, y, s)


def bare_tree(x, y, s=1.0, seed=3):
    """a leafless winter tree with snow along its branches"""
    r = random.Random(seed)
    with T(x, y, s):
        tube([(0, 0), (1, 30), (-1, 70)], 11, 5, P.BARK, lw=BG, sh=0.1)

        def branch(x0, y0, ang, L, w, depth):
            x1, y1 = x0 + math.cos(ang)*L, y0 + math.sin(ang)*L
            stroke([(x0, y0), (x1, y1)], w, g=P.BARK)
            if depth < 2:
                stroke(bez((x0, y0 + w*0.5), ((x0 + x1)/2, (y0 + y1)/2 + w), ((x0 + x1)/2, (y0 + y1)/2 + w), (x1, y1 + w*0.4)),
                       w*0.9, g=P.SNOW)
            if depth < 3:
                for da in (-0.45, 0.4):
                    branch(x1, y1, ang + da + r.uniform(-0.15, 0.15), L*0.62, w*0.62, depth + 1)

        for k_ in range(5):
            yy = 30 + k_*9
            sd = -1 if k_ % 2 else 1
            branch(0, yy, math.pi/2 - sd*(0.75 - k_*0.08), 22 - k_*2, BG*2.6 - k_*0.25, 0)
        branch(-1, 70, math.pi/2, 14, BG*1.8, 1)


def snow_fence(x0, x1, y, h=40, step=15, gap_at=None):
    """picket fence with snow on top; gap_at = x of a missing picket (the gap only Hanka fits through)"""
    xx = x0
    while xx < x1:
        if gap_at is None or abs(xx - gap_at) > step*0.6:
            sh_([(xx, y), (xx + 9, y), (xx + 9, y + h), (xx + 4.5, y + h + 5), (xx, y + h)], P.FENCE_RAIL)
            sh_([(xx - 1, y + h - 1), (xx + 10, y + h - 1), (xx + 4.5, y + h + 8)], P.SNOW, 0.6)
        xx += step
    for yy in (y + h*0.25, y + h*0.7):
        sh_([(x0 - 2, yy), (x1 + 2, yy), (x1 + 2, yy + 4), (x0 - 2, yy + 4)], P.POST)


def snow_field(p, y, seed=3, g=P.SNOW):
    r = random.Random(seed)
    top = [(p.x - 5 + i*(p.w + 10)/20, y + r.uniform(-2, 3)) for i in range(21)]
    fill([(p.x - 5, p.y - 5)] + top + [(p.x + p.w + 5, p.y - 5)], g)
    stroke(top, BG)
    for _ in range(7):
        sx = p.x + r.random()*p.w; sy = p.y + r.random()*(y - p.y)*0.9
        stroke(bez((sx - 14, sy), (sx - 5, sy + 2), (sx + 5, sy + 2), (sx + 14, sy)), 0.5, g=0.6)


def snowfall(p, n=40, seed=5, r_=1.5):
    r = random.Random(seed)
    for _ in range(n):
        x, y = p.x + r.random()*p.w, p.y + r.random()*p.h
        shape(ell(x, y, r_, r_, 10), 1.0, 0.4)


# ------------------------------------------------------------------ for the teaser (issue 6)
def sykorka(x, y, s=1.0, flip=False):
    """a great tit: round body, dark cap, white cheek"""
    with T(x, y, s, flip):
        shape(ell(0, 6, 7, 5.5, 22), P.HEN_WHITE if hasattr(P, "HEN_WHITE") else 0.9)
        shape(ell(5.5, 11, 4.2, 4, 18), 0.25)
        shape(ell(6.2, 10.4, 2.2, 1.8, 12), 1.0, 0.4)
        dot(7.6, 12, 0.6, 1.0)
        shape([(9.5, 11), (12, 10.4), (9.6, 9.8)], 0.3, 0.5)
        stroke([(-6, 6), (-12, 3)], 1.6, g=0.3)
        stroke([(0, 1), (0, -3)], 0.6); stroke([(2, 1), (2.4, -3)], 0.6)


def pernicek(x, y, s=1.0, rot=0, bitten=False):
    """a gingerbread heart with icing dots; bitten = tiny peck marks along the edge"""
    with T(x, y, s, rot=rot):
        pts = bez((0, -8), (-10, 0), (-6, 9), (0, 5)) + bez((0, 5), (6, 9), (10, 0), (0, -8))
        shape(pts, 0.55, LINE*0.8)
        stroke(bez((0, -5), (-7, 0), (-4, 6), (0, 3)) + bez((0, 3), (4, 6), (7, 0), (0, -5)), LINE*0.5, g=1.0)
        if bitten:
            for bx, by in ((6, 4), (8, 1), (7.5, 6)): dot(bx, by, 1.1, 1.0)
