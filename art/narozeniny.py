"""Issue 12 (Tajemné šipky): Alica's 8th birthday at home in the village. The three kinds of chalk arrows (táta's
solid, máma's dashed with a heart, Hanka's small dotted ones), the hopscotch, the pink bike with a front fork and its
tyre tracks, děda's brown kitten (malá Micka) in her basket, Hanka's cat drawing and peeled stick, the cake with eight
candles, balloons, presents, the garden party, the house and garage, the stairs, the calendar and the hidden presents."""
import math, random
import lib
from lib import ell, bez, rrect, resample
from style3 import *
from style3 import C
import palette as P
from scenes3 import BG, s_, sh_, sky, hills, ground, house, tree, cloud, fence
from velikonoce import blossom_tree, forsythia, egg
from village import heart
from chars3 import star
from letter import hand_text


def _panel_fill(p, g, alpha=None):
    fill([(p.x, p.y), (p.x + p.w, p.y), (p.x + p.w, p.y + p.h), (p.x, p.y + p.h)], g, alpha)


# ================================================================== chalk arrows
CHALK = {"tata": P.CHALK_TATA, "mama": P.CHALK_MAMA, "hanka": P.CHALK_HANKA}


def _chalk_line(pts, w, g):
    """a chalk stroke with a dark edge, so it reads on grass, paving and planks alike"""
    stroke(pts, w*1.7, g=0.0, taper=False)
    stroke(pts, w, g=g, taper=False)


def _chalk_dot(x, y, r, g):
    fill(ell(x, y, r*1.45, r*1.45, 14), 0.0)
    fill(ell(x, y, r, r, 14), g)


def sipka(x, y, s=1.0, rot=0, kind="tata"):
    """one chalk arrow, (x, y) = its middle, pointing along rot (degrees, 0 = right).
    tata: long, straight, solid, a big head. mama: dashed, a neat head, a little heart at the tail.
    hanka: short, wobbly, made of dots"""
    g = CHALK[kind]
    with T(x, y, s, rot=rot):
        if kind == "tata":
            _chalk_line([(-24, 0), (20, 0)], LINE*2.3, g)
            _chalk_line([(8, 9), (22, 0), (8, -9)], LINE*2.3, g)
        elif kind == "mama":
            for x0 in (-18, -9, 0, 9):
                _chalk_line([(x0, 0), (x0 + 5.5, 0)], LINE*1.9, g)
            _chalk_line([(10, 6.5), (18, 0), (10, -6.5)], LINE*1.9, g)
            with T(-24, 0, 1.0, rot=-90):
                pts = [(math.sin(t)**3*4.2, (13*math.cos(t) - 5*math.cos(2*t) - 2*math.cos(3*t) - math.cos(4*t))*0.3)
                       for t in [math.tau*i/30 for i in range(30)]]
                stroke(pts, LINE*2.4, closed=True, g=0.0, taper=False)
                stroke(pts, LINE*1.2, closed=True, g=g, taper=False)
        else:
            rd = random.Random(int(x*7 + y*3) & 0xffff)
            for i in range(5):
                _chalk_dot(-14 + i*5.2, rd.uniform(-1.4, 1.4), 1.15, g)
            _chalk_dot(14, 0, 1.15, g)
            for k in (1, 2, 3):
                for sy in (-1, 1):
                    _chalk_dot(14 - k*4.0 + rd.uniform(-0.5, 0.5), sy*k*4.0 + rd.uniform(-0.6, 0.6), 1.15, g)


def oil_smudge(x, y, s=1.0):
    """black fingerprints of bike oil"""
    rd = random.Random(int(x + y) & 0xffff)
    with T(x, y, s):
        for k in range(3):
            fx, fy = k*4.5 + rd.uniform(-1, 1), rd.uniform(-1.5, 1.5)
            fill(ell(fx, fy, 2.0, 2.8, 14, rot=15), P.OIL, 0.75)
            for r_ in (0.9, 1.5): stroke(ell(fx, fy, r_, r_*1.4, 12, rot=15), 0.3, closed=True, g=0.45)


def chalk_stick(x, y, s=1.0, rot=0, kind="tata"):
    with T(x, y, s, rot=rot):
        shape(rrect(-6, -1.8, 12, 3.6, 1.2), CHALK[kind], LINE*0.7)


def panak(x, y, s=1.0, rot=0):
    """a chalk hopscotch (skákací panák) seen from above at a slant: 1, 2, 3, 4|5, 6, 7|8 and the round "nebe".
    (x, y) = the bottom of square 1. Returns the page point of the "nebe" """
    cells = [(0, 0, "1"), (0, 1, "2"), (0, 2, "3"), (-0.5, 3, "4"), (0.5, 3, "5"), (0, 4, "6"), (-0.5, 5, "7"), (0.5, 5, "8")]
    cw, ch = 16, 11
    with T(x, y, s, rot=rot):
        for cx, cy, lbl in cells:
            x0 = cx*cw - cw/2; y0 = cy*ch
            pts = [(x0, y0), (x0 + cw, y0), (x0 + cw, y0 + ch), (x0, y0 + ch)]
            _chalk_line(pts + [pts[0]], LINE*0.9, 1.0)
            hand_text(x0, y0 + 2.5, cw, lbl, "SHB", 7, g=0.15)
        top = 6*ch
        arc = [(math.cos(a)*cw*0.9, top + math.sin(a)*ch*0.9) for a in [math.pi*i/16 for i in range(17)]]
        _chalk_line(arc, LINE*0.9, 1.0)
    return x, y + (6*ch + ch*0.5)*s


# ================================================================== the kitten, her basket, the shed clues
def kitten(x, y, s=1.0, flip=False, mood="happy", pose="sit", bow=False):
    """malá Micka: a brown tabby kitten, big head, big ears. pose: sit, walk, peek (only head and paws, for the basket).
    Local height ~34 sitting"""
    K, KD, KL = P.KITTEN, P.KITTEN_DARK, P.KITTEN_LIGHT
    with T(x, y, s, flip):
        if pose != "peek":
            tube(bez((8, 3), (20, 1), (23, 10), (18, 17), 12), 3.2, 2.4, K, sh=0)
            for t_ in (0.35, 0.7):
                q = bez((8, 3), (20, 1), (23, 10), (18, 17), 12)[int(t_*11)]
                stroke([(q[0] - 1.6, q[1] - 1.4), (q[0] + 1.6, q[1] + 1.4)], LINE*0.8, g=KD)
            if pose == "walk":
                body = bez((-14, 9), (-16, 18), (8, 20), (12, 12)) + bez((12, 12), (12, 6), (-12, 4), (-14, 9))
                form(body, K, sdx=-1.5, sdy=1)
                for lx in (-10, -6, 5, 9):
                    tube([(lx, 8), (lx + (1 if lx > 0 else -1), 0)], 2.6, 2.4, K, sh=0)
                hx, hy = 13, 21
            else:
                body = bez((-9, 0), (-11, 10), (-7, 19), (0, 20)) + bez((0, 20), (7, 19), (11, 10), (9, 0))
                form(body, K, sdx=-1.5, sdy=1)
                fill(ell(0, 9, 4, 7, 16), KL)
                for sx in (-1, 1): shape(ell(sx*3.6, 1, 3, 2, 14), KL, LINE*0.8)
                hx, hy = 0, 25
        else:
            for sx in (-1, 1): shape(ell(sx*6, 2, 3.2, 2.2, 14), KL, LINE*0.8)
            hx, hy = 0, 9
        with T(hx, hy, 1.0):
            for sx in (-1, 1):
                shape([(sx*3.5, 5.5), (sx*9.5, 13), (sx*9.5, 3)], K)
                fill([(sx*5.2, 6), (sx*8.6, 10.6), (sx*8.6, 4.6)], P.CAT_EAR)
            shape(ell(0, 0, 9.5, 8.2, 36), K)
            for k_ in (-2.5, 0, 2.5): stroke([(k_, 8), (k_*0.7, 4.5)], LINE*0.8, g=KD)
            fill(ell(0, -3.4, 4.2, 3, 16), KL)
            for sx in (-1, 1):
                if mood == "sleepy":
                    stroke(bez((sx*3.8 - 1.6, 0.6), (sx*3.8 - 0.5, -0.4), (sx*3.8 + 0.5, -0.4), (sx*3.8 + 1.6, 0.6)), LINE*0.8)
                else:
                    fill(ell(sx*3.8, 0.8, 1.7, 2.1, 12), 0.0); dot(sx*3.8 + 0.5, 1.6, 0.6, 1.0)
            fill([(-1.0, -2.0), (1.0, -2.0), (0, -3.0)], P.CAT_NOSE)
            if mood in ("meow", "happy"):
                shape(ell(0, -5.0, 1.4, 1.3 if mood == "meow" else 0.6, 10), 0.25, LINE*0.5)
            for sx in (-1, 1):
                for k_ in (-1, 1): stroke([(sx*3.2, -3 + k_*0.6), (sx*10, -2.6 + k_*1.8)], LINE*0.35)
            if bow:
                for sx in (-1, 1): shape([(0, -7.2), (sx*5, -5), (sx*5, -9.4)], P.RIBBON, LINE*0.6)
                shape(ell(0, -7.2, 1.4, 1.4, 10), P.RIBBON, LINE*0.6)


def cat_basket(x, y, s=1.0, kitten_in=False, lid=True, mood="happy"):
    """děda's wicker cat basket with a door of bars at the front and a carrying handle; kitten_in: malá Micka's face
    behind the bars (lid=False: the lid open, her head over the edge). Local width ~56, height ~36"""
    with T(x, y, s):
        body = [(-28, 0), (28, 0), (26, 30), (-26, 30)]
        shape(body, P.CAT_BASKET, LINE)
        C.saveState(); C.clipPath(poly(body), stroke=0, fill=0)
        for yy in range(3, 30, 5):
            stroke([(-30, yy), (30, yy)], LINE*0.45, g=0.3)
        for xx in range(-26, 28, 6):
            stroke([(xx, 0), (xx + 1, 30)], LINE*0.3, g=0.45)
        C.restoreState()
        if lid:
            shape([(-28, 30), (28, 30), (26, 35), (-26, 35)], P.CAT_BASKET, LINE)
            stroke(bez((-14, 35), (-12, 50), (12, 50), (14, 35)), LINE*2.4)
            stroke(bez((-14, 35), (-12, 50), (12, 50), (14, 35)), LINE*1.2, g=P.CAT_BASKET)
            shape(rrect(-12, 5, 24, 21, 4), P.BARN_DARK, LINE*0.8)
            if kitten_in:
                C.saveState(); C.clipPath(poly(rrect(-12, 5, 24, 21, 4)), stroke=0, fill=0)
                kitten(0, 8, 0.85, mood=mood, pose="peek")
                C.restoreState()
            for xx in (-6, 0, 6): stroke([(xx, 5), (xx, 26)], LINE*0.9, g=P.WIRE)
        else:
            if kitten_in:
                kitten(0, 24, 1.0, mood=mood, pose="peek", bow=True)
            stroke([(-28, 30), (28, 30)], LINE*1.4)


def milk_saucer(x, y, s=1.0):
    with T(x, y, s):
        shape(ell(0, 2, 12, 3.4, 24), P.SAUCER, LINE*0.8)
        fill(ell(0, 2.8, 8, 1.8, 20), 1.0)
        stroke(ell(0, 2.8, 8, 1.8, 20), LINE*0.4, closed=True, g=0.6)


def scratches(x, y, s=1.0):
    """little claw scratches low on a door"""
    with T(x, y, s):
        for gx in (0, 9):
            for k in range(3):
                stroke([(gx + k*2.2, 0), (gx + k*2.2 + 2.6, 7)], LINE*1.1, g=0.0, taper=False)
                stroke([(gx + k*2.2, 0), (gx + k*2.2 + 2.6, 7)], LINE*0.6, g=P.STICK, taper=False)


def kulna(x, y, s=1.0, door_open=False, kitten_out=False):
    """děda's wooden shed at the chalupa (kůlna): planks, a pent roof, a door with a padlock. (x, y) = bottom centre,
    local width ~90"""
    with T(x, y, s):
        wall = [(-45, 0), (45, 0), (45, 58), (-45, 66)]
        sh_(wall, P.SHED_WALL)
        for xx in range(-38, 45, 9): s_([(xx, 0), (xx, 66 - (xx + 45)*8/90)], BG*0.6)
        roof = [(-52, 62), (52, 53), (50, 61), (-50, 72)]
        sh_(roof, P.BARN_ROOF)
        door = [(-12, 0), (14, 0), (14, 46), (-12, 47)]
        if door_open:
            fill(door, P.BARN_DARK)
            sh_([(14, 0), (28, -4), (28, 44), (14, 46)], P.SHED_WALL)
        else:
            sh_(door, P.DOOR)
            for yy in (10, 36): s_([(-12, yy), (14, yy)], BG*0.6)
            s_([(-12, 10), (14, 36)], BG*0.6)
            shape(rrect(8, 22, 5, 6, 1.5), 0.55, LINE*0.6)
            stroke(bez((8.8, 28), (8.8, 31), (12.2, 31), (12.2, 28)), LINE*0.7)
            scratches(-8, 3, 0.8)


# ================================================================== the bike
def kolo(x, y, s=1.0, flip=False, bow=False):
    """Alica's new pink bike with a suspension fork at the front, knobbly tyres; side view, front to the right.
    (x, y) = the ground under its middle; local length ~96, wheel radius 19"""
    R = 19
    rear, front = (-32, R), (32, R)
    with T(x, y, s, flip):
        for cx, cy in (rear, front):
            stroke(ell(cx, cy, R, R, 44), LINE*4.2, closed=True, g=P.BIKE_TYRE, taper=False)
            for k in range(28):
                a = math.tau*k/28
                stroke([(cx + math.cos(a)*(R + 1.4), cy + math.sin(a)*(R + 1.4)),
                        (cx + math.cos(a)*(R + 2.8), cy + math.sin(a)*(R + 2.8))], LINE*1.1, g=P.BIKE_TYRE, taper=False)
            stroke(ell(cx, cy, R - 2.4, R - 2.4, 40), LINE*0.6, closed=True, g=0.5)
            for k in range(12):
                a = math.tau*k/12
                stroke([(cx, cy), (cx + math.cos(a)*(R - 2.6), cy + math.sin(a)*(R - 2.6))], 0.35, g=0.45)
            fill(ell(cx, cy, 2.2, 2.2, 12), 0.5)
        bb = (-4, R - 2)
        seat = (-14, R + 26)
        head = (22, R + 28)
        for a, b in ((rear, bb), (rear, seat), (bb, seat), (seat, head), (bb, head)):
            stroke([a, b], LINE*3.4, g=0.0, taper=False)
            stroke([a, b], LINE*2.2, g=P.BIKE_PINK, taper=False)
        # the suspension fork: fat lower legs, shiny stanchions, a crown under the head tube
        crown = (head[0] + 3, head[1] - 9)
        stroke([head, crown], LINE*3.0, g=P.BIKE_PINK, taper=False)
        mid = (crown[0] + (front[0] - crown[0])*0.45, crown[1] + (front[1] - crown[1])*0.45)
        stroke([crown, mid], LINE*2.6, g=0.0, taper=False); stroke([crown, mid], LINE*1.6, g=P.FORK, taper=False)
        stroke([mid, front], LINE*4.4, g=0.0, taper=False); stroke([mid, front], LINE*3.2, g=0.3, taper=False)
        shape(rrect(crown[0] - 5, crown[1] - 2, 10, 4, 1.5), 0.3, LINE*0.6)
        # handlebar, grips, saddle, pedals, chain
        stem = (head[0] - 1, head[1] + 7)
        stroke([head, stem], LINE*2.4, g=0.2, taper=False)
        stroke([(stem[0] - 6, stem[1] + 1), (stem[0] + 5, stem[1])], LINE*2.4, g=0.2, taper=False)
        stroke([(stem[0] - 9, stem[1] + 1.3), (stem[0] - 4, stem[1] + 1)], LINE*3.0, g=P.BIKE_PINK, taper=False)
        stroke([seat, (seat[0] - 1, seat[1] + 5)], LINE*2.2, g=0.35, taper=False)
        shape(bez((seat[0] - 9, seat[1] + 5), (seat[0] - 8, seat[1] + 9), (seat[0] + 6, seat[1] + 9), (seat[0] + 8, seat[1] + 6)) +
              [(seat[0] - 9, seat[1] + 5)], P.SADDLE, LINE*0.8)
        shape(ell(bb[0], bb[1], 5.5, 5.5, 20), 0.75, LINE*0.8)
        stroke([(bb[0] - 4, bb[1] - 7), (bb[0] + 4, bb[1] + 7)], LINE*1.6, g=0.2)
        stroke([(rear[0], rear[1] + 3), (bb[0], bb[1] + 5)], LINE*0.6, g=0.35)
        stroke([(rear[0], rear[1] - 3), (bb[0], bb[1] - 5)], LINE*0.6, g=0.35)
        if bow:
            for sx in (-1, 1):
                shape([(stem[0], stem[1] + 3), (stem[0] + sx*9, stem[1] + 9), (stem[0] + sx*9, stem[1] - 1)], P.RIBBON, LINE*0.7)
            shape(ell(stem[0], stem[1] + 3, 2.2, 2.2, 12), P.RIBBON, LINE*0.7)
            stroke(bez((stem[0], stem[1] + 1), (stem[0] - 2, stem[1] - 8), (stem[0] + 3, stem[1] - 12), (stem[0] + 1, stem[1] - 18)),
                   LINE*1.3, g=P.RIBBON)


def tyre_track(pts, wide=True, g=P.MUD_DARK, s=1.0):
    """a tyre track along pts: wide = a knobbly mountain-bike tyre (blocks in two rows), else a thin smooth line"""
    Pp = resample(pts, (4.0 if wide else 2.0)*s)
    for i in range(1, len(Pp) - 1):
        (x0, y0), (x1, y1) = Pp[i - 1], Pp[i + 1]
        a = math.atan2(y1 - y0, x1 - x0); nx, ny = -math.sin(a), math.cos(a)
        x, y = Pp[i]
        if wide:
            for off in ((-2.2*s, 2.2*s) if i % 2 else (0,)):
                cx, cy = x + nx*off, y + ny*off
                with T(cx, cy, s, rot=math.degrees(a)):
                    fill([(-1.2, -1.0), (1.2, -1.0), (1.2, 1.0), (-1.2, 1.0)], g)
        else:
            fill(ell(x, y, 0.9*s, 0.9*s, 8), g, 0.9)


def mud_puddle(x, y, w, h, seed=2):
    rd = random.Random(seed)
    pts = [(x + math.cos(a)*w/2*(1 + rd.uniform(-0.08, 0.08)), y + math.sin(a)*h/2*(1 + rd.uniform(-0.1, 0.1)))
           for a in [math.tau*i/26 for i in range(26)]]
    fill(pts, P.MUD)


# ================================================================== presents, balloons, the cake, the party
PRESENT_G = (P.PRESENT_RED, P.PRESENT_BLUE, P.PRESENT_YELLOW)


def darek(x, y, w=26, h=20, g=P.PRESENT_RED, ribbon=None, rot=0, bow=True):
    """a wrapped present with a ribbon cross and a bow; (x, y) = bottom centre"""
    rib = ribbon if ribbon is not None else (P.PRESENT_YELLOW if g != P.PRESENT_YELLOW else P.PRESENT_RED)
    with T(x, y, 1.0, rot=rot):
        box = [(-w/2, 0), (w/2, 0), (w/2, h), (-w/2, h)]
        shape(box, g, LINE*0.9)
        fill([(-2, 0), (2, 0), (2, h), (-2, h)], rib)
        fill([(-w/2, h*0.45), (w/2, h*0.45), (w/2, h*0.45 + 3.6), (-w/2, h*0.45 + 3.6)], rib)
        stroke(box, LINE*0.9, closed=True)
        if bow:
            for sx in (-1, 1):
                shape(bez((0, h + 1), (sx*3, h + 9), (sx*10, h + 8), (sx*7, h + 2)) + [(0, h + 1)], rib, LINE*0.7)
            shape(ell(0, h + 1.5, 2.2, 2.0, 12), rib, LINE*0.7)


def hidden_darek(x, y, r=12, rot=0, kind=0):
    """one of the 10 presents hidden in the issue: a white halo and a black line round it, so it reads on any ground.
    r = half its width"""
    w, h = r*2, r*1.6
    g = PRESENT_G[kind % 3]
    with T(x, y, 1.0, rot=rot):
        out = [(-w/2 - 1, -1), (w/2 + 1, -1), (w/2 + 1, h + 1), (r*0.7, h + 1), (r*0.55, h + r*0.75), (-r*0.55, h + r*0.75),
               (-r*0.7, h + 1), (-w/2 - 1, h + 1)]
        stroke(out, LINE*4.4, closed=True, g=0.0, taper=False)
        stroke(out, LINE*2.8, closed=True, g=1.0, taper=False)
        fill(out, 1.0)
        darek(0, 0, w, h, g)


def balonek(x, y, g=P.BALLOON_RED, s=1.0, string=40, sway=6):
    """a balloon, (x, y) = the end of its string"""
    with T(x, y, s):
        top = string
        stroke(bez((0, 0), (sway, top*0.3), (-sway, top*0.7), (0, top)), LINE*0.5, g=0.3)
        shape([(-1.6, top - 0.5), (1.6, top - 0.5), (0, top + 2.5)], g, LINE*0.5)
        b = [(math.cos(a)*9*(1 - 0.08*math.sin(a)), top + 12.5 + math.sin(a)*12) for a in [math.tau*i/36 for i in range(36)]]
        shape(b, g, LINE*0.8)
        stroke(bez((-5, top + 17), (-6, top + 13), (-5, top + 10), (-3.5, top + 8)), LINE*0.6, g=1.0)


def balonky(x, y, s=1.0, n=5, seed=3):
    """a bunch of balloons tied together; (x, y) = the knot"""
    rd = random.Random(seed)
    gs = (P.BALLOON_RED, P.BALLOON_YELLOW, P.BALLOON_BLUE, P.BALLOON_GREEN, P.CAKE_PINK)
    for i in range(n):
        a = math.radians(-40 + 80*i/max(1, n - 1)) + rd.uniform(-0.1, 0.1)
        L = 34 + rd.uniform(-4, 8)
        with T(x, y, s, rot=math.degrees(a)*-0.6):
            balonek(0, 0, gs[(i + seed) % len(gs)], 1.0, L, 3)


def girlanda(x0, x1, y, sag=18, n=12, seed=4):
    """a garland of little flags between two points"""
    pts = bez((x0, y), (x0 + (x1 - x0)*0.3, y - sag), (x0 + (x1 - x0)*0.7, y - sag), (x1, y), 40)
    stroke(pts, 0.7, g=0.3)
    gs = (P.BALLOON_RED, P.BALLOON_YELLOW, P.BALLOON_BLUE, P.BALLOON_GREEN)
    for i in range(1, n):
        a = pts[int(i*len(pts)/n)]; b = pts[min(len(pts) - 1, int(i*len(pts)/n) + 2)]
        shape([a, b, ((a[0] + b[0])/2, a[1] - 13)], gs[(i + seed) % 4], 0.6)


def dort(x, y, s=1.0, candles=8, lit=True):
    """the birthday cake: a chocolate sponge with pink icing dripping over the edge and eight candles.
    (x, y) = bottom centre on the plate; local width ~60"""
    with T(x, y, s):
        shape(ell(0, 0, 34, 5, 30), P.SAUCER, LINE*0.8)
        side = [(-26, 2), (26, 2), (26, 22), (-26, 22)]
        shape(side, P.CAKE, LINE)
        fill([(-26, 11), (26, 11), (26, 13.5), (-26, 13.5)], P.CAKE_PINK)
        drip = [(-26, 22)] + [(-26 + i*52/12, 22 - (5 if i % 2 else 2.5)) for i in range(13)] + [(26, 22)]
        top = ell(0, 22, 26, 6, 36)
        shape([q for q in top if q[1] >= 22] + drip[::-1], P.CAKE_PINK, LINE*0.8)
        shape(top, P.CAKE_PINK, LINE*0.8)
        for i in range(candles):
            a = math.pi*(0.15 + 0.7*i/max(1, candles - 1))
            cx = math.cos(a)*-18; cy = 22 + math.sin(a)*-2.5 + (1.5 if i % 2 else -1)
            shape(rrect(cx - 1.4, cy, 2.8, 11, 0.8), (P.BALLOON_BLUE, P.ICING, P.BALLOON_YELLOW)[i % 3], LINE*0.5)
            for k in range(3): stroke([(cx - 1.4, cy + 2 + k*3), (cx + 1.4, cy + 3.2 + k*3)], 0.35, g=0.4)
            stroke([(cx, cy + 11), (cx, cy + 12.6)], 0.5)
            if lit:
                shape(bez((cx, cy + 12), (cx - 2.4, cy + 14), (cx - 0.6, cy + 18), (cx, cy + 19.5)) +
                      bez((cx, cy + 19.5), (cx + 0.6, cy + 18), (cx + 2.4, cy + 14), (cx, cy + 12)), P.FLAME, LINE*0.5)


def party_table(x0, x1, y, seed=1):
    """the long garden table: a white cloth, a jug of lemonade, cups, plates of chlebíčky and fruit. Returns its top y"""
    top = y + 34
    for lx in (x0 + 8, x1 - 8):
        stroke([(lx, y), (lx, top)], LINE*2.4, g=P.TABLE)
    shape([(x0, top - 10), (x1, top - 10), (x1, top), (x0, top)], P.TABLECLOTH, LINE)
    for k in range(int((x1 - x0)/14)):
        xx = x0 + 7 + k*14
        stroke(bez((xx, top - 10), (xx + 3, top - 13), (xx + 10, top - 13), (xx + 14, top - 10)), 0.4, g=0.6)
    rd = random.Random(seed)
    n = max(1, int((x1 - x0)/70))
    for i in range(n):
        cx = x0 + (x1 - x0)*(i + 0.5)/n
        if i % 2 == 0:
            with T(cx - 12, top, 1.0):
                shape([(-6, 0), (6, 0), (7, 18), (-7, 18)], P.LEMONADE, LINE*0.8)
                stroke(bez((7, 15), (12, 14), (12, 6), (6, 4)), LINE*0.9)
                fill([(-6.5, 14), (6.5, 14), (7, 18), (-7, 18)], 1.0, 0.6)
            for k in range(2):
                shape([(cx + 2 + k*9, top), (cx + 8 + k*9, top), (cx + 8.5 + k*9, top + 9), (cx + 1.5 + k*9, top + 9)],
                      (P.BALLOON_RED, P.BALLOON_BLUE)[k], LINE*0.6)
        else:
            shape(ell(cx, top + 1.5, 16, 3, 20), P.SAUCER, LINE*0.7)
            for k in range(4):
                shape(rrect(cx - 12 + k*6, top + 2, 5, 4, 1), (P.EGG, P.CRAYON_RED, P.KRASLICE_GREEN, P.EGG)[k], LINE*0.4)
    return top


def party_hat(x, y, s=1.0, rot=0, g=P.BALLOON_BLUE):
    """a paper cone party hat with stripes and a pompom; (x, y) = the middle of its rim"""
    with T(x, y, s, rot=rot):
        cone = [(-7, 0), (7, 0), (0, 18)]
        shape(cone, g, LINE*0.8)
        C.saveState(); C.clipPath(poly(cone), stroke=0, fill=0)
        for k in range(4): stroke([(-8, 3 + k*4.5), (8, 6 + k*4.5)], LINE*1.3, g=P.BALLOON_YELLOW)
        C.restoreState()
        stroke(cone, LINE*0.8, closed=True)
        for k in range(8):
            a = math.tau*k/8
            stroke([(0, 19), (math.cos(a)*3, 19 + math.sin(a)*3)], LINE*0.7, g=P.BALLOON_RED)


def sack(x, y, s=1.0, h=50):
    """a jute sack drawn over a child's legs for the sack race; (x, y) = its bottom centre"""
    with T(x, y, s):
        body = bez((-12, 0), (-15, h*0.4), (-13, h*0.8), (-14, h)) + [(14, h)] + bez((14, h), (13, h*0.8), (15, h*0.4), (12, 0))
        shape(body, P.SACK, LINE)
        for k in range(1, 6):
            stroke([(-12, k*h/6), (12, k*h/6 + 1)], 0.35, g=0.5)
        stroke([(-14, h - 3), (14, h - 3)], LINE*0.6, g=0.3)


def spoon_egg(x, y, s=1.0):
    """a wooden spoon held out with an egg on it (item for the egg-and-spoon race)"""
    with T(x, y, s):
        stroke([(0, 0), (16, 3)], LINE*1.6, g=P.TABLE)
        shape(ell(19, 3.4, 4.5, 2.6, 14), P.TABLE, LINE*0.6)
    egg(x + 19*s, y + 9*s, 0.7*s)


# ================================================================== Hanka's presents, invitations, notes
def cat_drawing(x, y, w=60, h=46, rot=-4):
    """Hanka's present from the forest school: a crayon cat on brown paper, a sun and her wobbly H"""
    with T(x, y, 1.0, rot=rot):
        shape([(0, 0), (w, 0), (w, h), (0, h)], 1.0, LINE*0.8)
        k = w/60
        with T(w*0.45, h*0.18, k):
            stroke(ell(0, 10, 11, 9, 20), 1.1, closed=True, g=P.CRAYON_BROWN)
            stroke(ell(2, 24, 8, 7, 20), 1.1, closed=True, g=P.CRAYON_BROWN)
            for sx in (-1, 1): stroke([(2 + sx*3, 30), (2 + sx*7, 36), (2 + sx*7.5, 28)], 1.1, g=P.CRAYON_BROWN)
            dot(-1, 25, 1.0); dot(5, 25, 1.0)
            stroke(bez((10, 6), (22, 6), (20, 22), (14, 20)), 1.1, g=P.CRAYON_BROWN)
            for sx in (-1, 1): stroke([(2 + sx*2, 22), (2 + sx*10, 23)], 0.6)
        stroke(ell(w - 10, h - 9, 5, 5, 14), 0.9, closed=True, g=P.KRASLICE_YELLOW)
        for a in range(0, 360, 45):
            ra = math.radians(a)
            stroke([(w - 10 + math.cos(ra)*7, h - 9 + math.sin(ra)*7), (w - 10 + math.cos(ra)*10, h - 9 + math.sin(ra)*10)],
                   0.7, g=P.KRASLICE_YELLOW)
        stroke([(5, 6), (6, 15)], 0.9, g=P.CRAYON_RED); stroke([(10, 5), (9, 15)], 0.9, g=P.CRAYON_RED)
        stroke([(5.5, 10), (9.5, 10.5)], 0.9, g=P.CRAYON_RED)


def loupana_hul(x, y, s=1.0, rot=0, length=70):
    """Hanka's walking stick she peeled herself with a knife: pale wood with rings of bark left on. (x, y) = its foot"""
    with T(x, y, s, rot=rot):
        body = [(-2.2, 0), (2.2, 0), (1.8, length), (-1.8, length)]
        shape(body, P.STICK, LINE*0.8)
        C.saveState(); C.clipPath(poly(body), stroke=0, fill=0)
        for k in range(int(length/11)):
            yy = 6 + k*11
            fill([(-3, yy), (3, yy + 2.2), (3, yy + 5.4), (-3, yy + 3.2)], P.BARK)
        C.restoreState()
        stroke(body, LINE*0.8, closed=True)
        stroke([(1.6, length*0.6), (5, length*0.6 + 6)], LINE*1.0, g=P.STICK)


def pozvanka(x, y, s=1.0, rot=0, word=True):
    """an invitation card with a star and balloons on it"""
    with T(x, y, s, rot=rot):
        shape([(0, 0), (34, 0), (34, 22), (0, 22)], P.INVITE, LINE*0.8)
        star(8, 14, 4.6, P.KRASLICE_YELLOW)
        balonek(24, 2, P.BALLOON_RED, 0.32, 18, 1)
        if word: hand_text(1, 3, 22, "POZVÁNKA", "SHB", 4.2, g=0.2)


def lunch_note(x, y, s=1.0, rot=4):
    """máma's note in the lunchbox, signed with a heart"""
    with T(x, y, s, rot=rot):
        shape([(0, 0), (52, 0), (52, 30), (0, 30)], 1.0, LINE*0.8)
        hand_text(3, 17, 46, "Dobrou chuť!", "SH", 7.5, g=0.2)
        heart(40, 8, 4.4)


def seznam(x, y, w, h, rot=-3):
    """máma's shopping list with its bottom torn off: what is left reads "balónky, limo, 8 sv…" """
    with T(x, y, 1.0, rot=rot):
        rd = random.Random(8)
        tear = [(w*i/10, rd.uniform(0, 6)) for i in range(11)]
        shape(tear + [(w, h), (0, h)], 1.0, LINE*0.9)
        k = w/100
        for j in range(4): stroke([(6*k, h - (24 + j*20)*k), (w - 6*k, h - (24 + j*20)*k)], 0.4, g=0.75)
        for i, ln in enumerate(("balónky", "limo", "8 sv")):
            hand_text(10*k, h - (40 + i*20)*k, w - 16*k, ln, "SH", 14*k, align="left", g=0.15)
        heart(w - 16*k, h - 14*k, 5*k)


def kalendar(x, y, w=60, h=70, circle=(4, 3)):
    """the kitchen calendar: a picture on top, a grid of days below, one day circled in red with a heart.
    No numbers that could be read."""
    shape([(x, y), (x + w, y), (x + w, y + h), (x, y + h)], 1.0, LINE*0.8)
    ph = h*0.38
    fill([(x + 3, y + h - ph), (x + w - 3, y + h - ph), (x + w - 3, y + h - 3), (x + 3, y + h - 3)], P.SPRING_SKY)
    fill([(x + 3, y + h - ph), (x + w - 3, y + h - ph), (x + w - 3, y + h - ph*0.6), (x + 3, y + h - ph*0.4)], P.SPRING_GRASS)
    fill(ell(x + w*0.7, y + h - ph*0.3, 4, 4, 12), P.KRASLICE_YELLOW)
    cols, rws = 7, 5
    gw = (w - 6)/cols; gh = (h - ph - 8)/rws
    for r in range(rws):
        for c in range(cols):
            cx = x + 3 + c*gw + gw/2; cy = y + 4 + (rws - 1 - r)*gh + gh/2
            dot(cx, cy, 0.7, 0.45)
    cc, cr = circle
    cx = x + 3 + cc*gw + gw/2; cy = y + 4 + (rws - 1 - cr)*gh + gh/2
    stroke(ell(cx, cy, gw*0.75, gh*0.75, 18), LINE*1.3, closed=True, g=P.CRAYON_RED)
    heart(cx + gw*0.55, cy + gh*0.7, 2.4)
    stroke([(x + w/2, y + h), (x + w/2, y + h + 6)], 0.6)
    dot(x + w/2, y + h + 6, 1.2, 0.3)


def paper_star(x, y, r=14, word=None, rot=8):
    """a yellow paper star taped up along the trail, sometimes with one word written on it for Alica"""
    with T(x, y, 1.0, rot=rot):
        star(0, 0, r, P.KRASLICE_YELLOW, LINE*0.9)
        if word: hand_text(-r, -r*0.22, r*2, word, "SHB", r*0.55, g=0.1)


def sekacka(x, y, s=1.0, flip=False):
    """the lawnmower, standing outside the garage; (x, y) = the ground under its middle, local width ~40"""
    with T(x, y, s, flip):
        shape([(-18, 6), (14, 6), (16, 16), (-16, 18)], P.KRASLICE_GREEN, LINE)
        shape(rrect(-10, 16, 16, 7, 2), 0.3, LINE*0.8)
        for wx in (-12, 10):
            shape(ell(wx, 5, 5, 5, 16), P.BIKE_TYRE, LINE*0.8); dot(wx, 5, 1.4, 0.7)
        stroke([(-14, 16), (-30, 42)], LINE*1.8, g=0.35)
        stroke([(-34, 44), (-26, 39)], LINE*2.6, g=0.2)


def transparent(x0, x1, y, txt, size=16):
    """Bětka's painted banner hung between two points"""
    h = size*1.9
    shape([(x0, y), (x1, y), (x1, y - h), (x0, y - h)], 1.0, LINE)
    for k, g in enumerate((P.BALLOON_RED, P.BALLOON_YELLOW, P.BALLOON_BLUE, P.BALLOON_GREEN)):
        fill(ell(x0 + 8 + k*5, y - 7, 2, 2, 8), g); fill(ell(x1 - 8 - k*5, y - h + 7, 2, 2, 8), g)
    hand_text(x0, y - h*0.68, x1 - x0, txt, "SHB", size, g=0.15)
    for xx in (x0, x1): stroke([(xx, y), (xx + (6 if xx == x0 else -6), y + 12)], 0.6, g=0.3)


def phone(x, y, s=1.0, rot=70):
    with T(x, y, s, rot=rot):
        shape(rrect(-3, -6, 6, 12, 1.5), P.PHONE, LINE*0.6)


# ================================================================== home: the house, the garage, the garden
def garaz(x, y, s=1.0, door="closed", bike=False):
    """the garage next to the house: a flat roof, an up-and-over door. door: closed, open, ajar (a dark gap at the
    bottom). (x, y) = bottom centre, local width ~84"""
    with T(x, y, s):
        wall = [(-42, 0), (42, 0), (42, 56), (-42, 56)]
        sh_(wall, P.GARAGE)
        sh_([(-46, 56), (46, 56), (46, 62), (-46, 62)], P.ROOF_EDGE)
        dr = [(-32, 0), (32, 0), (32, 44), (-32, 44)]
        if door == "open":
            fill(dr, P.BARN_DARK)
            if bike:
                kolo(0, 2, 0.55, bow=True)
            sh_([(-32, 40), (32, 40), (32, 44), (-32, 44)], P.GARAGE_DOOR)
        else:
            sh_(dr, P.GARAGE_DOOR)
            for k in range(1, 7): s_([(-32, k*6.3), (32, k*6.3)], BG*0.5)
            shape(rrect(-5, 4, 10, 3, 1), 0.3, LINE*0.5)
            if door == "ajar":
                fill([(-32, 0), (32, 0), (32, 5), (-32, 5)], P.BARN_DARK)


def branka(x, y, h=40, w=34, open_=False):
    """a garden gate between two posts; (x, y) = bottom left of the left post"""
    for px in (x, x + w + 6):
        sh_([(px, y), (px + 6, y), (px + 6, y + h + 8), (px, y + h + 8)], P.FENCE_RAIL)
        sh_([(px - 1, y + h + 8), (px + 7, y + h + 8), (px + 3, y + h + 12)], P.FENCE_RAIL)
    if open_:
        fill([(x + 6, y), (x + w + 6, y), (x + w + 6, y + h), (x + 6, y + h)], P.SPRING_GRASS)
        for k in range(4):
            sh_([(x + 6 + k*3, y + 2 - k), (x + 9 + k*3, y + 2 - k), (x + 9 + k*3, y + h - k), (x + 6 + k*3, y + h - k)], 0.95)
    else:
        for k in range(4):
            px = x + 8 + k*(w - 4)/4
            sh_([(px, y + 2), (px + 6, y + 2), (px + 6, y + h - 2), (px + 3, y + h + 2), (px, y + h - 2)], 0.95)
        for yy in (y + 8, y + h - 10):
            sh_([(x + 6, yy), (x + w + 6, yy), (x + w + 6, yy + 4), (x + 6, yy + 4)], P.FENCE_RAIL)
        shape(ell(x + w, y + h*0.5, 2, 2, 10), 0.3, LINE*0.5)


def domov(p, gy_f=0.38, seed=1, house_x=None, house_s=1.0, garage_x=None, garage_kw=None, fence_=None, gate_x=None,
          gate_open=False, paving=0.0, trees=(), bushes=(), clouds=True, evening=False):
    """home in the village in late April: sky, hills, a lawn, optionally the house, the garage, the garden fence
    (fence_ = (x0, x1) fractions) with a gate, a paved strip along the bottom (paving = its height as a fraction),
    blossoming trees and forsythia. Returns the ground y"""
    gy = p.Y(gy_f)
    sky(p, P.SPRING_SKY)
    if clouds: cloud(p.X(0.3), p.Y(0.88), 0.7)
    hills(p, gy + p.h*0.07, 16, P.FAR_FIELD, seed)
    ground(p, gy, P.SPRING_GRASS)
    rd = random.Random(seed)
    for _ in range(int(p.w/26)):
        xx = p.x + rd.uniform(0, p.w); yy = rd.uniform(p.y + 4, gy - 6)
        for k in (-2, 0, 2): stroke([(xx + k, yy), (xx + k*1.6, yy + 4)], BG*0.5, g=0.4)
    for tx, ts in trees: blossom_tree(p.X(tx), gy - 4, ts, seed=seed + int(tx*10))
    if house_x is not None: house(p.X(house_x), gy - 4, house_s, smoke=False)
    if garage_x is not None: garaz(p.X(garage_x), gy - 3, house_s*0.9, **(garage_kw or {}))
    if fence_ is not None:
        f0, f1 = p.X(fence_[0]), p.X(fence_[1])
        if gate_x is not None:
            gx = p.X(gate_x)
            fence(f0, gx, gy - 14, 34)
            branka(gx, gy - 14, 34, 34, gate_open)
            fence(gx + 46, f1, gy - 14, 34)
        else:
            fence(f0, f1, gy - 14, 34)
    for bx, bs in bushes: forsythia(p.X(bx), gy - 4, bs, seed=seed + int(bx*10))
    if paving:
        py_ = p.Y(paving)
        shape([(p.x - 5, p.y - 5), (p.x + p.w + 5, p.y - 5), (p.x + p.w + 5, py_), (p.x - 5, py_)], P.PAVING, BG)
        for k in range(int(p.w/40) + 1):
            s_([(p.x + k*40 + 20, p.y), (p.x + k*40 + 14, py_)], BG*0.5)
    if evening:
        _panel_fill(p, P.WINTER_NIGHT, 0.35)
    return gy


def chodba(p, floor=0.08, dark=0.0):
    """the hallway at home: the front door on the left, the wooden stairs going up to the right with a dark cubby
    under them. Returns (floor y, x of the cubby's middle)"""
    _panel_fill(p, P.KITCHEN_WALL)
    fy = p.Y(floor)
    dx0, dx1 = p.X(0.05), p.X(0.2)
    shape([(dx0 - 4, fy), (dx1 + 4, fy), (dx1 + 4, p.Y(0.82)), (dx0 - 4, p.Y(0.82))], P.DOOR_FRAME, BG)
    shape([(dx0, fy), (dx1, fy), (dx1, p.Y(0.79)), (dx0, p.Y(0.79))], P.DOOR, BG)
    shape(ell(dx1 - 8, p.Y(0.42), 2.4, 2.4, 10), 0.85, LINE*0.6)
    sx0, sx1 = p.X(0.42), p.X(0.98)
    steps = 9
    stp_w = (sx1 - sx0)/steps; stp_h = (p.Y(0.92) - fy)/steps
    under = [(sx0, fy)] + [(sx0 + (i + 1)*stp_w, fy + i*stp_h + stp_h) for i in range(steps)] + [(sx1, fy)]
    shape(under, P.PLANKS, BG)
    for i in range(1, steps):
        xx = sx0 + i*stp_w
        s_([(xx, fy), (xx, fy + i*stp_h)], BG*0.5)
    cx0, cx1 = sx0 + stp_w*3.2, sx0 + stp_w*6
    ch_ = min(stp_h*3.4, (cx0 - sx0)/stp_w*stp_h + stp_h*0.8)
    shape([(cx0, fy), (cx1, fy), (cx1, fy + ch_), (cx0, fy + ch_)], P.BARN_DARK, BG)
    for i in range(steps):
        x0 = sx0 + i*stp_w; y0 = fy + i*stp_h
        sh_([(x0, y0 + stp_h - 3), (x0 + stp_w + 3, y0 + stp_h - 3), (x0 + stp_w + 3, y0 + stp_h + 1),
             (x0, y0 + stp_h + 1)], P.PLANKS)
    stroke([(sx0 + 4, fy + stp_h + 30), (sx1, fy + steps*stp_h + 30)], LINE*1.6, g=P.TABLE)
    for i in range(0, steps, 2):
        xx = sx0 + 4 + i*stp_w
        stroke([(xx, fy + (i + 1)*stp_h), (xx, fy + (i + 1)*stp_h + 30)], LINE*0.9, g=P.TABLE)
    shape([(p.x - 5, p.y - 5), (p.x + p.w + 5, p.y - 5), (p.x + p.w + 5, fy), (p.x - 5, fy)], P.FLOOR, BG)
    if dark:
        _panel_fill(p, 0.0, dark)
    return fy, (cx0 + cx1)/2


def suspect_card(x, y, w, h, fn, label=None, rot=0):
    """a photo of a suspect pinned to Alica's board: the figure clipped to a white-edged frame"""
    with T(x, y, 1.0, rot=rot):
        shape([(0, 0), (w, 0), (w, h), (0, h)], 1.0, LINE*0.9)
        inner = [(4, 4 + (12 if label else 0)), (w - 4, 4 + (12 if label else 0)), (w - 4, h - 4), (4, h - 4)]
        fill(inner, P.SPRING_SKY)
        C.saveState(); C.clipPath(poly(inner), stroke=0, fill=0)
        fn(w/2, inner[0][1])
        C.restoreState()
        stroke(inner, 0.6, closed=True, g=0.4)
        if label: hand_text(2, 4, w - 4, label, "SHB", 9, g=0.15)
        shape(ell(w/2, h - 2, 3, 3, 12), P.CRAYON_RED, LINE*0.6)
