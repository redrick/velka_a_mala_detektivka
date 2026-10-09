"""Issue 8 (Stopy ve sněhu): the forest animals the family meets on Joey's walks (roe deer, wild boar, hare, fox,
squirrel), the prints each one leaves in the snow, the forester's krmelec, and the snowy meadow and forest.

Every animal faces right with its feet at y = 0, like Joey. The prints are drawn toes/front up (+y) and a trail
turns them along its path. In the comic a print in snow is a pale dent (P.TRACK); on the track guide the same print is
drawn in ink (P.TRACK_INK) so the kids can compare the shapes."""
import math, random
from lib import ell, bez, rrect, resample
from style3 import *
from style3 import C
import palette as P
from scenes3 import BG, s_, sh_, sky, hills
from chars3 import star
from winter import snow_field, bare_tree, parsnip
from advent import star_spruce, bird_print, paw_print


# ------------------------------------------------------------------ the hidden-object game
def _carrot_pts(L, w):
    """a carrot along the y axis, root tip at the bottom (0, -L/2), shoulder at the top"""
    return bez((-w, L*0.5), (-w*1.05, L*0.15), (-w*0.45, -L*0.3), (0, -L*0.5)) + \
           bez((0, -L*0.5), (w*0.45, -L*0.3), (w*1.05, L*0.15), (w, L*0.5)) + \
           bez((w, L*0.5), (w*0.5, L*0.6), (-w*0.5, L*0.6), (-w, L*0.5))


def hidden_carrot(x, y, r=13, rot=-30):
    """one of the 10 carrots hidden in the issue: inside a white halo and a black line, so it reads on snow, wood and
    fur alike (the comic prints in grey). r is about half its length."""
    with T(x, y, 1.0, rot=rot):
        o = _carrot_pts(r*1.5, r*0.32)
        top = [(-r*0.05, r*0.78), (-r*0.5, r*1.45), (-r*0.2, r*1.5), (0, r*0.9), (r*0.12, r*1.6), (r*0.38, r*1.5),
               (r*0.12, r*0.8)]
        for pts in (o, top):
            stroke(pts, LINE*4.4, closed=True, g=0.0, taper=False)
        for pts in (o, top):
            stroke(pts, LINE*2.8, closed=True, g=1.0, taper=False)
        fill(top, P.PARSNIP_LEAF); stroke(top, LINE*0.5, closed=True, g=0.0, taper=False)
        fill(o, P.CARROT); stroke(o, LINE*0.5, closed=True, g=0.0, taper=False)
        for k in (-0.25, 0.0, 0.25):
            stroke([(-r*0.22, r*k*1.2), (r*0.05, r*k*1.2 - r*0.06)], LINE*0.6, g=0.0)


def carrot(x, y, s=1.0, rot=0):
    """a plain carrot with its leaves; (x, y) = the root tip"""
    with T(x, y, s, rot=rot):
        with T(0, 13, 1.0):
            shape(_carrot_pts(26, 4.4), P.CARROT, LINE*0.7)
            for k in (-4, 1, 6): stroke([(-3, k), (0.5, k - 1)], LINE*0.35, g=0.35)
        for a in (-20, 0, 18):
            ra = math.radians(90 + a)
            stroke([(0, 26), (math.cos(ra)*9, 26 + math.sin(ra)*9)], LINE*1.2, g=P.PARSNIP_LEAF)


def apple(x, y, s=1.0):
    with T(x, y, s):
        shape(bez((0, 9), (-9, 13), (-11, 2), (-6, -4)) + bez((-6, -4), (-3, -7), (3, -7), (6, -4)) +
              bez((6, -4), (11, 2), (9, 13), (0, 9)), P.APPLE, LINE*0.7)
        stroke([(0, 9), (1, 13)], LINE*0.8, g=0.3)
        stroke(bez((-5, 6), (-6, 3), (-5, 0), (-4, -1)), LINE*0.5, g=1.0)


def beet(x, y, s=1.0, rot=0):
    """a fodder beet (řepa) for the krmelec"""
    with T(x, y, s, rot=rot):
        shape(bez((0, -12), (-3, -8), (-10, -2), (-9, 5)) + bez((-9, 5), (-8, 11), (8, 11), (9, 5)) +
              bez((9, 5), (10, -2), (3, -8), (0, -12)), P.BEET, LINE*0.7)
        for k in (-3, 1, 5): stroke([(-6, k), (-2, k + 1)], LINE*0.4, g=0.6)
        for a in (-25, 5, 30): stroke([(0, 10), (math.sin(math.radians(a))*8, 18)], LINE*1.1, g=P.PARSNIP_LEAF)


# ------------------------------------------------------------------ the roe deer (srnka)
def _hoof(x, y, a=0, g=P.DEER_DARK):
    with T(x, y, 1, rot=a):
        shape([(-1.8, 0), (2.4, 0), (1.6, 3.4), (-1.6, 3.4)], g, LINE*0.6)
        stroke([(0.3, 0), (0.3, 2.2)], LINE*0.4, g=0.8)


def _deer_head(hx, hy, ang, look=(0, 0), ears="up"):
    """the doe's head; (hx, hy) = the back of the skull, ang = direction the muzzle points (degrees)"""
    with T(hx, hy, 1, rot=ang):
        for k, (ex, ey) in enumerate(((-1.5, 4), (1.5, 5))):        # far ear, then near ear
            tip = (ex - 6, ey + 12) if ears == "up" else (ex - 11, ey + 6)
            e = bez((ex - 2.4, ey), (ex - 6, ey + 4), tip, tip) + bez(tip, tip, (ex + 3, ey + 5), (ex + 2.4, ey))
            shape(e, P.DEER if k else P.DEER_DARK, LINE*0.8)
            if k: stroke(bez((ex - 0.8, ey + 1), (ex - 3, ey + 4), (tip[0] + 2, tip[1] - 2), (tip[0] + 1.2, tip[1] - 1.2)),
                         LINE*0.5, g=0.85)
        head = bez((-3, -4.5), (-6, -1), (-5, 5), (0, 6)) + bez((0, 6), (5, 6.5), (9, 4), (13, 2)) + \
               bez((13, 2), (16, 1.2), (17.5, -0.5), (17, -2.5)) + bez((17, -2.5), (15, -5), (9, -5.5), (4, -6)) + \
               bez((4, -6), (1, -6.2), (-1, -5.6), (-3, -4.5))
        shape(head, P.DEER)
        stroke(bez((10.5, 1.6), (11, -1), (11, -3.5), (10.4, -5.3)), LINE*0.5, g=1.0)     # pale band behind the nose
        shape(bez((14.6, 1.4), (17.6, 1.2), (18, -2), (16.2, -3)) + [(14.2, -1)], 0.08, LINE*0.6)
        stroke(bez((14, -4), (15, -4.8), (16, -4.6), (16.6, -3.6)), LINE*0.5)
        ex_, ey_ = 4.6 + look[0]*0.4, 1.4 + look[1]*0.3
        shape(ell(ex_, ey_, 1.9, 1.5, 14, rot=10), 0.05, LINE*0.5)
        dot(ex_ + 0.5, ey_ + 0.5, 0.5, 1.0)
        shape(ell(1, -6.4, 3.6, 1.9, 12, rot=-10), 1.0, LINE*0.4)                          # white chin


def srnka(x, y, s=1.0, flip=False, pose="stand", look=(0, 0), shadow=True):
    """a roe doe in her grey-brown winter coat with the big white rump patch (zrcátko). About 100 tall to the ear tips
    and 70 long at s = 1: draw her at 0.8 x the children's scale, so her back comes to Alica's chest. pose: stand, reach (neck stretched up to a
    snowman's nose), low (head lowered, curious, nose to nose with a dog), run (bounding away, the white patch flared)."""
    if shadow and pose != "run": cast_shadow(x, y, 30*s, 3*s)
    with T(x, y, s, flip):
        if pose == "run":
            _srnka_run(look); return
        far_h = [(-21, 48), (-15, 33), (-25, 19), (-22, 2)]
        far_f = [(16, 46), (15, 32), (16, 18), (17, 2)]
        for lg in (far_h, far_f):
            tube(lg, 7 if lg is far_h else 5.5, 2.6, P.DEER_DARK, sh=0)
            _hoof(lg[-1][0], 0, g=0.15)
        body = bez((24, 49), (26, 58), (20, 64), (12, 63)) + bez((12, 63), (0, 62), (-14, 64), (-26, 61)) + \
               bez((-26, 61), (-34, 58), (-34, 46), (-27, 42)) + bez((-27, 42), (-14, 38), (6, 38), (18, 41)) + \
               bez((18, 41), (22, 43), (24, 46), (24, 49))
        form(notch(body, 0.5, 6), P.DEER, sdx=-2, sdy=1.2)
        rump = bez((-27, 61), (-35, 58), (-35, 45), (-28, 43)) + bez((-28, 43), (-24, 47), (-24, 57), (-27, 61))
        shape(rump, P.DEER_RUMP, LINE*0.6)
        stroke(bez((-14, 41), (-8, 44), (4, 44), (12, 42)), LINE*0.5, g=0.4)              # belly line
        near_h = [(-18, 50), (-11, 33), (-20, 19), (-17, 2)]
        near_f = [(20, 47), (19, 32), (20, 18), (21, 2)]
        for lg in (near_h, near_f):
            o = tube(lg, 9 if lg is near_h else 6.5, 3.0, P.DEER, sh=0.08)
            _hoof(lg[-1][0], 0)
        HX, HY, ang = {"stand": (30, 84, -28), "reach": (36, 94, 12), "low": (38, 54, -48)}[pose]
        nb, nf = (12, 62), (24, 50)                                    # neck: back and front at the shoulder
        if pose == "low":
            neck = bez(nb, (22, 66), (30, 62), (HX - 5, HY + 5)) + [(HX + 3, HY - 4)] + bez((HX + 3, HY - 4), (32, 46), (28, 46), nf)
        else:
            dx, dy = HX - 20, HY - 56
            neck = bez(nb, (nb[0] + dx*0.3, nb[1] + dy*0.5), (HX - 8, HY - 2), (HX - 4, HY + 4)) + [(HX + 4, HY - 6)] + \
                   bez((HX + 4, HY - 6), (HX - 2, HY - 14), (nf[0] + dx*0.25, nf[1] + dy*0.3), nf)
        form(notch(neck, 0.4, 5), P.DEER, sdx=-1.4, sdy=1, sh=0.08)
        if pose != "low":
            fill(ell(HX - 2, HY - 12, 3.2, 2.2, 12, rot=ang + 60), 1.0)                     # white throat spot
        _deer_head(HX, HY, ang, look)


def _srnka_run(look):
    """bounding away: legs tucked, body raised, the white rump patch flared wide (that's what you see of a fleeing deer)"""
    with T(0, 18, 1, rot=6):
        for lg, w in (([(-22, 44), (-34, 34), (-48, 30), (-58, 26)], 7), ([(16, 44), (24, 36), (18, 28), (24, 22)], 5)):
            tube(lg, w, 2.6, P.DEER_DARK, sh=0)
        body = bez((24, 49), (26, 58), (20, 64), (12, 63)) + bez((12, 63), (0, 62), (-14, 64), (-26, 61)) + \
               bez((-26, 61), (-34, 58), (-34, 46), (-27, 42)) + bez((-27, 42), (-14, 38), (6, 38), (18, 41)) + \
               bez((18, 41), (22, 43), (24, 46), (24, 49))
        form(notch(body, 0.5, 6), P.DEER, sdx=-2, sdy=1.2)
        rump = bez((-25, 64), (-40, 62), (-40, 40), (-27, 39)) + bez((-27, 39), (-20, 44), (-20, 58), (-25, 64))
        shape(rump, P.DEER_RUMP, LINE*0.7)
        for lg, w in (([(-18, 46), (-30, 30), (-44, 22), (-54, 16)], 9), ([(20, 46), (30, 40), (24, 30), (30, 24)], 6.5)):
            tube(lg, w, 3.0, P.DEER, sh=0.08)
        HX, HY, ang = 34, 80, -10
        neck = bez((12, 62), (18, 70), (HX - 8, HY - 2), (HX - 4, HY + 4)) + [(HX + 4, HY - 6)] + \
               bez((HX + 4, HY - 6), (HX - 2, HY - 14), (26, 56), (24, 50))
        form(notch(neck, 0.4, 5), P.DEER, sdx=-1.4, sdy=1, sh=0.08)
        _deer_head(HX, HY, ang, look, ears="back")
    for k in range(3):                                                                    # snow kicked up
        shape(ell(-62 - k*7, 6 + k*5, 3 - k*0.5, 2.4 - k*0.4, 10), P.SNOW, LINE*0.5)


def deer_bed(x, y, w=46, h=14, seed=3):
    """lože: the oval a deer melts into the snow where she slept, with a few grey hairs"""
    r = random.Random(seed)
    fill(ell(x, y, w*0.6, h*0.62, 30), P.SNOW_SHADE)
    shape(ell(x, y, w*0.5, h*0.5, 30), P.DEER_BED, BG*0.9)
    for _ in range(9):
        hx, hy = x + r.uniform(-w*0.35, w*0.35), y + r.uniform(-h*0.3, h*0.3); a = r.uniform(0, math.pi)
        stroke([(hx, hy), (hx + math.cos(a)*3, hy + math.sin(a)*1.5)], LINE*0.5, g=P.DEER_DARK)


# ------------------------------------------------------------------ the wild boar (divočák)
def divocak(x, y, s=1.0, flip=False, pose="stand", shadow=True):
    """a wild boar: wedge-shaped, bristly back, long snout with a flat disc, small ears, short legs.
    About 50 tall and 80 long at s = 1. pose: stand, root (snout in the snow, digging)."""
    if shadow: cast_shadow(x, y, 32*s, 3*s)
    dy_head = -14 if pose == "root" else 0
    with T(x, y, s, flip):
        for lx in (-24, 14):
            tube([(lx, 22), (lx + 1, 10), (lx, 2)], 7, 4.4, P.BOAR_DARK, sh=0)
            shape([(lx - 3, 0), (lx + 3, 0), (lx + 2.4, 4), (lx - 2.4, 4)], 0.1, LINE*0.6)
        tail = bez((-34, 34), (-40, 32), (-40, 26), (-38, 22))
        stroke(tail, LINE*1.2, g=P.BOAR_DARK)
        stroke([(-38, 22), (-37, 19)], LINE*2.4, g=P.BOAR_DARK)
        body = bez((-30, 18), (-37, 26), (-36, 38), (-26, 44)) + bez((-26, 44), (-12, 50), (4, 54), (16, 52)) + \
               bez((16, 52), (26, 48), (34, 40 + dy_head*0.5), (42, 28 + dy_head)) + \
               bez((42, 28 + dy_head), (46, 24 + dy_head), (50, 20 + dy_head), (52, 16 + dy_head)) + \
               bez((52, 16 + dy_head), (50, 12 + dy_head), (44, 12 + dy_head), (36, 14 + dy_head*0.6)) + \
               bez((36, 14 + dy_head*0.6), (24, 14), (0, 14), (-30, 18))
        form(notch(body, 1.2, 3), P.BOAR, sdx=-2.4, sdy=1.4, sh=0.1)
        for k in range(9):                                                          # bristles along the back
            bx = -22 + k*5; by = 47 + math.sin(k/8*math.pi)*6
            stroke([(bx, by), (bx - 1.5, by + 3.5)], LINE*0.7, g=0.1)
        stroke(bez((14, 44), (20, 38 + dy_head*0.3), (20, 28 + dy_head*0.3), (16, 22)), LINE*0.6, g=0.1)
        sx, sy = 52, 16 + dy_head
        shape(ell(sx, sy, 2.2, 3.6, 14), 0.5, LINE*0.7)                              # the snout's flat disc
        dot(sx + 0.3, sy + 1.2, 0.6, 0.1); dot(sx + 0.3, sy - 1.2, 0.6, 0.1)
        ex, ey = 30, 34 + dy_head*0.7
        shape(ell(ex, ey, 1.5, 1.3, 12), 0.05, LINE*0.4); dot(ex + 0.4, ey + 0.4, 0.4, 1.0)
        shape([(20, 42 + dy_head*0.4), (16, 52 + dy_head*0.4), (25, 46 + dy_head*0.4)], P.BOAR_DARK, LINE*0.7)
        for lx in (-18, 22):
            tube([(lx, 22), (lx + 1, 10), (lx, 2)], 8, 5, P.BOAR, sh=0.06)
            shape([(lx - 3.4, 0), (lx + 3.4, 0), (lx + 2.6, 4.4), (lx - 2.6, 4.4)], 0.1, LINE*0.6)
        if pose == "root":
            for k in range(6):
                a = 0.4 + k*0.35
                shape(ell(sx + 6 + math.cos(a)*10, sy - 4 + math.sin(a)*8, 2.4, 1.8, 10), P.SNOW, LINE*0.45)


def rooted_ground(x, y, w=80, h=14, seed=6):
    """snow turned over by boars looking for acorns: dark earth and lumps of snow"""
    r = random.Random(seed)
    fill(ell(x, y, w*0.55, h*0.7, 30), P.SNOW_SHADE)
    shape(ell(x, y, w*0.45, h*0.5, 30, rot=r.uniform(-4, 4)), P.EARTH, BG*0.8)
    for _ in range(9):
        a = r.uniform(0, math.tau); d = r.uniform(0.8, 1.15)
        shape(ell(x + math.cos(a)*w*0.48*d, y + math.sin(a)*h*0.55*d, r.uniform(2.5, 5), r.uniform(1.8, 3.2), 10),
              P.SNOW, LINE*0.45)
    for _ in range(4):
        shape(ell(x + r.uniform(-w*0.3, w*0.3), y + r.uniform(-h*0.2, h*0.2), 1.8, 1.4, 10), P.PINECONE, LINE*0.3)


# ------------------------------------------------------------------ the hare (zajíc)
def zajic(x, y, s=1.0, flip=False, pose="sit", shadow=True):
    """a brown hare: long ears with black tips, big hind feet, a big eye on the side of the head.
    pose: sit (about 34 tall to the ear tips at s = 1), run (stretched out, 44 long)."""
    if shadow: cast_shadow(x, y, 14*s, 2*s)
    with T(x, y, s, flip):
        if pose == "run":
            with T(0, 6, 1, rot=4):
                tube([(-10, 6), (-20, 2), (-28, 0)], 5, 3, P.HARE, sh=0)
                body = bez((-12, 4), (-20, 10), (-14, 18), (0, 18)) + bez((0, 18), (12, 18), (18, 14), (18, 9)) + \
                       bez((18, 9), (14, 4), (0, 2), (-12, 4))
                form(notch(body, 0.4, 4), P.HARE, sdx=-1.2, sdy=0.8)
                shape(ell(-16, 12, 3, 2.6, 12), 1.0, LINE*0.5)
                tube([(12, 6), (20, 2), (26, -2)], 4, 2.4, P.HARE, sh=0)
                hx, hy = 20, 16
                for k, a in enumerate((168, 160)):
                    ra = math.radians(a)
                    e = [(hx - 1, hy + 2), (hx + math.cos(ra)*18 - 1, hy + 2 + math.sin(ra)*18 + 2),
                         (hx + math.cos(ra)*19, hy + 2 + math.sin(ra)*19 - 1), (hx + 2, hy + 1)]
                    shape(e, P.HARE if k else P.HARE, LINE*0.6)
                    dot(hx + math.cos(ra)*18, hy + 2 + math.sin(ra)*18, 1.4, 0.1)
                shape(ell(hx + 2, hy, 6, 4.6, 16, rot=-10), P.HARE, LINE*0.8)
                shape(ell(hx + 3, hy + 1, 1.5, 1.6, 10), 0.05, LINE*0.3); dot(hx + 3.5, hy + 1.6, 0.4, 1.0)
                dot(hx + 7.6, hy - 1, 0.8, 0.2)
            return
        tube([(-6, 4), (6, 1)], 6, 4, P.HARE, sh=0)                                       # far hind foot
        body = bez((-8, 2), (-14, 8), (-13, 20), (-4, 24)) + bez((-4, 24), (2, 26), (8, 22), (9, 14)) + \
               bez((9, 14), (10, 6), (4, 1), (-8, 2))
        form(notch(body, 0.4, 4), P.HARE, sdx=-1.4, sdy=0.8)
        shape(ell(-12, 5, 3.2, 2.8, 12), 1.0, LINE*0.5)                                    # white scut
        stroke(bez((-6, 16), (-10, 12), (-9, 6), (-4, 4)), LINE*0.6, g=0.35)                # haunch
        tube([(-6, 2), (8, 0.5)], 6.5, 4.4, P.HARE, sh=0.08)                              # near hind foot
        for fx in (6, 9): tube([(fx, 14), (fx + 1, 6), (fx + 1.5, 1)], 3, 2.4, P.HARE, sh=0)
        hx, hy = 8, 26
        for k, (a, L) in enumerate(((112, 19), (100, 20))):
            ra = math.radians(a)
            tip = (hx + math.cos(ra)*L, hy + 4 + math.sin(ra)*L)
            e = bez((hx - 2.4, hy + 3), (hx - 3.6, hy + 12), (tip[0] - 2.6, tip[1] - 4), tip) + \
                bez(tip, (tip[0] + 2.6, tip[1] - 4), (hx + 3.2, hy + 12), (hx + 2, hy + 3))
            shape(e, P.HARE, LINE*0.7)
            clip_pts = e
            C.saveState(); C.clipPath(poly(clip_pts), stroke=0, fill=0)
            fill(ell(tip[0], tip[1], 4, 4.5, 12), 0.1)
            C.restoreState()
            if k: stroke(bez((hx, hy + 5), (hx - 0.5, hy + 10), (tip[0] - 0.6, tip[1] - 8), (tip[0], tip[1] - 5)), LINE*0.5,
                         g=0.85)
        head = bez((hx - 6, hy + 1), (hx - 6, hy + 6), (hx + 2, hy + 7), (hx + 6, hy + 3)) + \
               bez((hx + 6, hy + 3), (hx + 9, hy + 1), (hx + 9.5, hy - 2.5), (hx + 7, hy - 3.5)) + \
               bez((hx + 7, hy - 3.5), (hx + 2, hy - 5), (hx - 5, hy - 4), (hx - 6, hy + 1))
        shape(head, P.HARE)
        shape(ell(hx + 1.6, hy + 1.6, 1.9, 2.0, 12), P.FOX, LINE*0.4)
        dot(hx + 2, hy + 1.6, 1.1, 0.05); dot(hx + 2.4, hy + 2.2, 0.4, 1.0)
        dot(hx + 8.6, hy - 1, 0.8, 0.2)
        for k in (-1, 1): stroke([(hx + 8, hy - 1.6), (hx + 13, hy - 1.6 + k*1.6)], LINE*0.3)


def hare_form(x, y, w=26, h=8):
    """the shallow scrape where a hare sits out the day"""
    fill(ell(x, y, w*0.6, h*0.7, 24), P.SNOW_SHADE)
    shape(ell(x, y, w*0.45, h*0.45, 24), P.DEER_BED, BG*0.7)


# ------------------------------------------------------------------ the fox (liška)
def liska(x, y, s=1.0, flip=False, pose="stand", shadow=True):
    """a red fox: slim, pointed muzzle, big ears, black stockings, bushy tail with a white tip.
    About 40 tall at the ears and 80 long with the tail at s = 1. pose: stand, pounce (the mousing jump: arched
    high, front paws aimed down into the snow)."""
    if shadow and pose == "stand": cast_shadow(x, y, 22*s, 2.4*s)
    with T(x, y, s, flip):
        if pose == "pounce":
            with T(0, 26, 1, rot=-62):
                _fox_body(arched=True)
            return
        _fox_body()


def _fox_body(arched=False):
    for lg in ([(-14, 18), (-12, 10), (-16, 4), (-15, 0)], [(12, 18), (13, 8), (13, 0)]):
        tube(lg, 4.2, 2.6, P.FOX_DARK, sh=0)
    tail = bez((-18, 22), (-30, 26), (-42, 20), (-46, 10)) + bez((-46, 10), (-44, 6), (-38, 8), (-34, 12)) + \
           bez((-34, 12), (-28, 16), (-22, 15), (-17, 16))
    form(notch(tail, 0.7, 3), P.FOX, sdx=-1.4, sdy=1)
    tip = bez((-42, 15), (-46, 12), (-46, 8), (-45, 7)) + bez((-45, 7), (-42, 5.6), (-39, 7), (-38, 9)) + [(-40, 13)]
    shape(tip, P.FOX_WHITE, LINE*0.6)
    body = bez((-18, 16), (-22, 22), (-18, 28), (-8, 28)) + bez((-8, 28), (2, 28), (10, 28), (16, 26)) + \
           bez((16, 26), (20, 24), (20, 18), (16, 15)) + bez((16, 15), (6, 13), (-8, 13), (-18, 16))
    form(notch(body, 0.4, 5), P.FOX, sdx=-1.6, sdy=1)
    fill(bez((12, 16), (16, 18), (18, 22), (19, 25)) + [(16, 26), (10, 17)], P.FOX_WHITE)          # white chest
    for lg in ([(-12, 18), (-9, 10), (-13, 4), (-12, 0)], [(15, 18), (16, 8), (16, 0)]):
        o = tube(lg, 5, 3, P.FOX, sh=0.06)
        C.saveState(); C.clipPath(poly(o), stroke=0, fill=0)
        fill([(lg[-1][0] - 6, -2), (lg[-1][0] + 6, -2), (lg[-1][0] + 6, 8), (lg[-1][0] - 6, 8)], P.FOX_DARK)
        C.restoreState()
    hx, hy = 20, 31
    neck = [(12, 26), (hx - 4, hy + 4), (hx + 4, hy - 2), (18, 20)]
    fill(neck, P.FOX)
    for k, ex in enumerate((-1.6, 1.6)):
        e = [(hx + ex - 3, hy + 3), (hx + ex - 1.5, hy + 12), (hx + ex + 2.4, hy + 3.4)]
        shape(e, P.FOX if k else P.FOX_DARK, LINE*0.7)
        if k: fill([(hx + ex - 1.6, hy + 4), (hx + ex - 1.2, hy + 9), (hx + ex + 1, hy + 4.2)], P.FOX_DARK)
    head = bez((hx - 5, hy + 2), (hx - 4, hy + 6), (hx + 3, hy + 5), (hx + 6, hy + 2)) + \
           bez((hx + 6, hy + 2), (hx + 10, hy + 0.5), (hx + 13, hy - 0.5), (hx + 14, hy - 1.5)) + \
           bez((hx + 14, hy - 1.5), (hx + 11, hy - 3.5), (hx + 4, hy - 5), (hx - 2, hy - 3)) + [(hx - 5, hy + 2)]
    shape(head, P.FOX)
    C.saveState(); C.clipPath(poly(head), stroke=0, fill=0)
    fill(bez((hx - 2, hy - 1), (hx + 4, hy - 0.5), (hx + 10, hy - 1), (hx + 15, hy - 1.5)) + [(hx + 15, hy - 6), (hx - 2, hy - 6)],
         P.FOX_WHITE)
    C.restoreState()
    stroke(head, LINE, closed=True)
    dot(hx + 13.8, hy - 1.4, 1.1, 0.05)
    stroke(bez((hx + 1.6, hy + 1.8), (hx + 2.6, hy + 2.6), (hx + 3.8, hy + 2.4), (hx + 4.4, hy + 1.6)), LINE*0.9)


def mousehole(x, y, s=1.0):
    """a little hole in the snow where a mouse tunnel comes up"""
    with T(x, y, s):
        fill(ell(0, 0, 7, 3, 16), P.SNOW_SHADE)
        shape(ell(0, 0, 3.2, 1.8, 14), 0.2, LINE*0.5)


def pounce_hole(x, y, s=1.0):
    """the hole a fox's mousing jump leaves: a dent with prints of both front paws"""
    with T(x, y, s):
        fill(ell(0, 0, 12, 5, 20), P.SNOW_SHADE)
        shape(ell(0, 0, 7, 3, 18), P.TRACK, BG*0.6)


# ------------------------------------------------------------------ the squirrel (veverka)
def veverka(x, y, s=1.0, flip=False, item="cone"):
    """a red squirrel sitting up, winter ear tufts, the bushy tail curled up its back; nibbling a spruce cone"""
    with T(x, y, s, flip):
        tail = bez((-4, 2), (-16, 2), (-18, 18), (-12, 28)) + bez((-12, 28), (-8, 34), (-2, 34), (-4, 28)) + \
               bez((-4, 28), (-10, 22), (-10, 12), (-2, 8))
        form(notch(tail, 0.8, 3), P.SQUIRREL, sdx=-1, sdy=0.6)
        body = bez((-4, 1), (-9, 6), (-8, 16), (-2, 20)) + bez((-2, 20), (4, 22), (7, 14), (6, 6)) + \
               bez((6, 6), (5, 1), (0, 0), (-4, 1))
        form(body, P.SQUIRREL, sdx=-1, sdy=0.6)
        fill(bez((1, 4), (5, 6), (6, 12), (4, 17)) + [(1, 14)], P.FOX_WHITE)
        shape(ell(-2, 2, 5, 2.4, 14), P.SQUIRREL, LINE*0.7)
        hx, hy = 3, 24
        for k, ex in enumerate((-1.5, 1.5)):
            e = [(hx + ex - 2, hy + 3), (hx + ex - 1, hy + 9), (hx + ex + 0.6, hy + 10.5), (hx + ex + 1.6, hy + 3)]
            shape(e, P.SQUIRREL, LINE*0.6)
        shape(ell(hx, hy, 4.6, 4.2, 16), P.SQUIRREL, LINE*0.8)
        shape(ell(hx + 4.2, hy - 1, 2.6, 2.2, 12), P.SQUIRREL, LINE*0.6)
        dot(hx + 1.6, hy + 1, 1.0, 0.05); dot(hx + 1.9, hy + 1.4, 0.35, 1.0)
        dot(hx + 6.6, hy - 0.8, 0.6, 0.1)
        if item == "cone":
            with T(hx + 6, hy - 8, 1, rot=-15):
                shape(ell(0, 0, 2.6, 5, 14), P.PINECONE, LINE*0.5)
                for k in range(-3, 4, 2): stroke([(-2.2, k), (2.2, k + 1)], LINE*0.3, g=0.75)
        tube([(4, 14), (8, 12), (9, 17)], 2.6, 2, P.SQUIRREL, sh=0)


def cone_scales(x, y, n=8, seed=5):
    """spruce cone scales a squirrel drops under the tree"""
    r = random.Random(seed)
    for _ in range(n):
        shape(ell(x + r.uniform(-14, 14), y + r.uniform(-3, 3), 1.6, 1.0, 8, rot=r.uniform(0, 180)), P.PINECONE, LINE*0.3)


# ------------------------------------------------------------------ prints (toes / front up, about life-size relative to each other)
def deer_print(x, y, s=1.0, rot=0, g=None, ink=False):
    """roe deer: two narrow pointed halves, together a slim heart; no dots behind"""
    g = (P.TRACK_INK if ink else P.TRACK) if g is None else g
    with T(x, y, s, rot=rot):
        for sx in (-1, 1):
            half = bez((sx*0.6, 6.5), (sx*2.6, 5), (sx*3.6, -1), (sx*3, -4.5)) + bez((sx*3, -4.5), (sx*2.2, -6), (sx*0.8, -5.6), (sx*0.6, -4.5))
            shape(half, g, LINE*0.5)


def boar_print(x, y, s=1.0, rot=0, g=None, ink=False):
    """wild boar: two wider, rounded halves and two dots behind them, wider than the print (dewclaws)"""
    g = (P.TRACK_INK if ink else P.TRACK) if g is None else g
    with T(x, y, s, rot=rot):
        for sx in (-1, 1):
            half = bez((sx*0.8, 6), (sx*4.4, 5.6), (sx*5, -1), (sx*4, -4)) + bez((sx*4, -4), (sx*3, -5.4), (sx*1, -5), (sx*0.8, -3.6))
            shape(half, g, LINE*0.5)
            shape(ell(sx*5.6, -8.6, 1.5, 1.3, 10), g, LINE*0.5)


def hare_print(x, y, s=1.0, rot=0, g=None, ink=False):
    """hare, one hop: the two long hind feet land side by side in FRONT, the two small front feet one behind the other
    (together a Y)"""
    g = (P.TRACK_INK if ink else P.TRACK) if g is None else g
    with T(x, y, s, rot=rot):
        for sx in (-1, 1): shape(ell(sx*3.6, 8, 2.2, 5, 14, rot=sx*8), g, LINE*0.5)
        shape(ell(0, -2.5, 1.9, 2.4, 12), g, LINE*0.5)
        shape(ell(-0.4, -9, 1.9, 2.4, 12), g, LINE*0.5)


def fox_print(x, y, s=1.0, rot=0, g=None, ink=False):
    """fox: a narrow oval, four toes, the front two well forward, small claw dots"""
    g = (P.TRACK_INK if ink else P.TRACK) if g is None else g
    with T(x, y, s, rot=rot):
        shape(bez((-2, -3), (-2.8, 0), (2.8, 0), (2, -3)) + bez((2, -3), (1.4, -4.6), (-1.4, -4.6), (-2, -3)), g, LINE*0.45)
        for tx, ty in ((-2.6, 2.2), (2.6, 2.2), (-1, 5), (1, 5)):
            shape(ell(tx, ty, 1.0, 1.4, 10), g, LINE*0.45)
            dot(tx*1.05, ty + 2, 0.4, 0.2 if ink else 0.5)


def dog_print(x, y, s=1.0, rot=0, g=None, ink=False):
    """dog: round, four toes spread wide, blunt claws"""
    g = (P.TRACK_INK if ink else P.TRACK) if g is None else g
    with T(x, y, s, rot=rot):
        shape(bez((-3.4, -1), (-4.4, 2.6), (4.4, 2.6), (3.4, -1)) + bez((3.4, -1), (2.6, -3.6), (-2.6, -3.6), (-3.4, -1)), g, LINE*0.45)
        for tx, ty in ((-4.2, 3.6), (4.2, 3.6), (-1.5, 5.6), (1.5, 5.6)):
            shape(ell(tx, ty, 1.4, 1.7, 10), g, LINE*0.45)
            dot(tx*1.08, ty + 2.4, 0.5, 0.2 if ink else 0.5)


def cat_print(x, y, s=1.0, rot=0, g=None, ink=False):
    """cat: small and round, four toes, no claws (a cat keeps them in)"""
    g = (P.TRACK_INK if ink else P.TRACK) if g is None else g
    with T(x, y, s, rot=rot):
        shape(ell(0, -0.6, 2.6, 2.1, 14), g, LINE*0.45)
        for tx, ty in ((-2.8, 2.4), (2.8, 2.4), (-1, 4), (1.2, 4)):
            shape(ell(tx, ty, 0.95, 1.1, 10), g, LINE*0.45)


def squirrel_print(x, y, s=1.0, rot=0, g=None, ink=False):
    """squirrel, one hop: the long hind feet land side by side in front, the small front feet side by side behind"""
    g = (P.TRACK_INK if ink else P.TRACK) if g is None else g
    with T(x, y, s, rot=rot):
        for sx in (-1, 1):
            shape(ell(sx*3, 4, 1.4, 3, 12, rot=-sx*10), g, LINE*0.45)
            for k in range(4): dot(sx*3 + (k - 1.5)*0.9*sx, 7.6 + abs(k - 1.5)*-0.4, 0.45, g)
            shape(ell(sx*1.8, -3.5, 1.1, 1.3, 10), g, LINE*0.45)


PRINTS = {"srnka": deer_print, "divocak": boar_print, "zajic": hare_print, "liska": fox_print, "pes": dog_print,
          "kocka": cat_print, "veverka": squirrel_print, "ptacek": None}


def trail(kind, pts, s=1.0, n=None, g=None, ink=False, wander=0.0, seed=1):
    """a line of prints of one animal along a path of points (page coordinates).
    deer, boar, dog, cat: alternating left/right; fox: one straight line (it puts each hind foot into the front print);
    hare, squirrel: hop groups spaced wider; wander > 0 lets a dog weave and turn"""
    fn = PRINTS[kind] if kind != "ptacek" else (lambda x, y, s=1.0, rot=0, g=None, ink=False:
                                                 bird_print(x, y, s*1.6, rot, g=(P.TRACK_INK if ink else P.TRACK) if g is None else g))
    path = []
    for i in range(len(pts) - 1):
        (x0, y0), (x1, y1) = pts[i], pts[i + 1]
        path += [(x0 + (x1 - x0)*t/20, y0 + (y1 - y0)*t/20) for t in range(20)]
    path.append(pts[-1])
    step = {"srnka": 15, "divocak": 14, "pes": 13, "kocka": 9, "liska": 13, "zajic": 34, "veverka": 26, "ptacek": 7}[kind]*s
    path = resample(path, 1.0)
    side_off = {"srnka": 3.2, "divocak": 4.2, "pes": 4.2, "kocka": 2.8, "liska": 0.6, "ptacek": 2.4}.get(kind, 0)*s
    r = random.Random(seed)
    d_next = 0; d = 0; k = 0
    for i in range(1, len(path)):
        d += math.hypot(path[i][0] - path[i - 1][0], path[i][1] - path[i - 1][1])
        if d < d_next: continue
        if n is not None and k >= n: break
        a = math.atan2(path[i][1] - path[i - 1][1], path[i][0] - path[i - 1][0])
        nx, ny = -math.sin(a), math.cos(a)
        off = side_off*(1 if k % 2 else -1)
        jit = r.uniform(-wander, wander)
        fn(path[i][0] + nx*(off + jit*8), path[i][1] + ny*(off + jit*8), s, math.degrees(a) - 90 + jit*40, g=g, ink=ink)
        k += 1; d_next = d + step*(1 + r.uniform(-0.15, 0.15)*bool(wander))


# ------------------------------------------------------------------ evidence close-ups
def nose_stub(x, y, s=1.0, cut="frayed", rot=0):
    """the bitten end of a parsnip nose. cut: frayed (torn, a deer has no upper front teeth) or clean (a slanted cut
    like scissors: a hare)"""
    with T(x, y, s, rot=rot):
        if cut == "clean":
            pts = [(-5, -2), (-5.4, 6), (5, 10), (5.2, -2)]
        else:
            pts = [(-5, -2), (-5.4, 6), (-3.6, 9), (-2, 6.4), (-0.6, 10.4), (1, 7), (2.6, 10.6), (3.8, 7.2), (5.4, 8.6), (5.2, -2)]
        pts += bez((5.2, -2), (5, -6), (-5, -6), (-5, -2))
        shape(pts, P.PARSNIP, LINE*0.7)
        for k in (-1, 2): stroke([(-3.6, k), (0.6, k + 0.6)], LINE*0.35, g=0.5)
        if cut == "frayed":
            for (a, b) in (((-3, 7), (-3.4, 11.4)), ((0.8, 8), (1.6, 12.4)), ((3.4, 8), (4.6, 11.6))):
                stroke([a, b], LINE*0.4, g=0.45)


def twig(x, y, s=1.0, cut="clean", rot=0):
    """a bitten twig: a clean slanted cut (hare) or a torn, frayed end (deer)"""
    with T(x, y, s, rot=rot):
        tube([(-30, 0), (0, 0)], 4.4, 4, P.BARK, sh=0, cap=False)
        stroke([(-22, 1.6), (-28, 8)], LINE*1.4, g=P.BARK)
        if cut == "clean":
            shape([(0, -2.2), (0, 2.2), (6, 2.2)], P.TRAP_WOOD, LINE*0.7)
        else:
            shape([(0, -2.2), (0, 2.2), (2.4, 2.6), (3.2, 1), (4.6, 1.8), (3.6, -0.4), (5, -1.2), (2.8, -1.6), (2.6, -2.8)],
                  P.TRAP_WOOD, LINE*0.6)
            for (a, b) in (((3, 1.4), (6.4, 3.4)), ((3.6, -0.6), (7, -0.4)), ((2.6, -2), (5.4, -4))):
                stroke([a, b], LINE*0.4, g=0.4)


# ------------------------------------------------------------------ the krmelec and the forest
def krmelec(x, y, s=1.0, hay=True, food=False, snow=True):
    """the forester's feeding rack: a slatted hay rack under a little shingled roof, on four posts, a trough in front.
    food = carrots, apples and beets in the trough. (x, y) = middle of its foot"""
    with T(x, y, s):
        for px in (-34, 34):
            sh_([(px - 3, 0), (px + 3, 0), (px + 3, 78), (px - 3, 78)], P.KRMELEC)
        rack = [(-30, 34), (30, 34), (36, 68), (-36, 68)]
        if hay:
            fill(rack, P.HAY)
            r = random.Random(4)
            for _ in range(24):
                hx = r.uniform(-30, 30); hy = r.uniform(38, 64)
                stroke([(hx, hy), (hx + r.uniform(-5, 5), hy + r.uniform(-3, 5))], LINE*0.4, g=0.5)
        else:
            fill(rack, 0.6)
        for k in range(9):
            t = k/8
            sh_([(-30 + 60*t - 1.2, 34), (-30 + 60*t + 1.2, 34), (-36 + 72*t + 1.2, 68), (-36 + 72*t - 1.2, 68)], P.KRMELEC, BG*0.6)
        sh_([(-38, 32), (38, 32), (38, 36), (-38, 36)], P.KRMELEC)
        sh_([(-40, 66), (40, 66), (40, 70), (-40, 70)], P.KRMELEC)
        roof = [(-50, 72), (50, 72), (0, 100)]
        shape(roof, P.FEEDER_ROOF, BG*1.1)
        for k in range(1, 4):
            t = k/4
            s_([(-50*(1 - t), 72 + 28*t), (50*(1 - t), 72 + 28*t)], BG*0.5)
        if snow:
            shape(bez((-52, 74), (-30, 92), (-10, 100), (0, 103)) + bez((0, 103), (10, 100), (30, 92), (52, 74)) +
                  [(46, 76), (0, 98), (-46, 76)], P.SNOW, BG*0.7)
        trough = [(-36, 14), (36, 14), (32, 4), (-32, 4)]
        if food:
            for k in range(5): carrot(-28 + k*7, 14, 0.42, rot=-80 + k*12)
            for k in range(3): apple(4 + k*9, 15, 0.42)
            beet(-8, 15, 0.45, rot=20); beet(28, 15, 0.42, rot=-15)
        sh_(trough, P.KRMELEC)
        s_([(-34, 11), (34, 11)], BG*0.5)
        for px in (-26, 26): sh_([(px - 2, 0), (px + 2, 0), (px + 2, 5), (px - 2, 5)], P.KRMELEC, BG*0.6)


def oak(x, y, s=1.0, seed=4):
    """the big old oak in the meadow, bare in winter, snow along its limbs"""
    bare_tree(x, y, s*1.25, seed=seed)


def spruce(x, y, s=1.0, seed=3, snow=True):
    star_spruce(x, y, s, stars=(), seed=seed, snow=snow)


def low_spruce(x, y, s=1.0, seed=8):
    """a young spruce with its lowest branches down on the snow: a cave under it, just Hanka's size"""
    with T(x, y, s):
        sh_([(-4, 0), (4, 0), (4, 12), (-4, 12)], P.BARK)
        fill(ell(0, 6, 34, 9, 24), 0.35)
        for i in range(4):
            y0 = 4 + i*24; hw = 62 - i*13
            r = random.Random(seed + i)
            jag = [(-hw + 2*hw*k/8, y0 - (5 if k % 2 else 0) + r.uniform(-1, 1)) for k in range(9)]
            if i == 0:
                shape(jag + [(hw*0.5, y0 + 30), (-hw*0.5, y0 + 30)], P.SPRUCE, LINE)
            else:
                shape(jag + [(0, y0 + 52)], P.SPRUCE, LINE)
            for k in (0, 2, 6, 8):
                sx_, sy_ = jag[k]
                shape(bez((sx_ - 6, sy_ + 3), (sx_ - 3, sy_ + 7), (sx_ + 3, sy_ + 7), (sx_ + 6, sy_ + 3)) +
                      [(sx_ + 5, sy_ + 1), (sx_ - 5, sy_ + 1)], P.SNOW, LINE*0.5)


def winter_meadow(p, gy, seed=1, forest=True, oak_x=None, sky_g=None, dusk=False):
    """the meadow behind the chalupa: open snow sloping up to the dark edge of the forest"""
    sky(p, P.SNOW_SKY if sky_g is None else sky_g)
    if forest:
        r = random.Random(seed)
        fy = gy + p.h*0.12
        xx = p.x - 20
        while xx < p.x + p.w + 20:
            spruce(xx, fy - 6, r.uniform(0.18, 0.26), seed=seed + int(xx))
            xx += r.uniform(16, 26)
        hills(p, fy - 4, 6, P.SNOW_HILL, seed)
    snow_field(p, gy, seed)
    if oak_x is not None: oak(p.X(oak_x), gy - 10, 1.0, seed)
    if dusk: fill([(p.x, p.y), (p.x + p.w, p.y), (p.x + p.w, p.y + p.h), (p.x, p.y + p.h)], 0.0, 0.2)


def winter_forest(p, gy, seed=1, trees=((0.1, 0.9), (0.85, 1.0)), far=True, bare=()):
    """among the spruces: far trunks, near spruces at the given (x fraction, scale), snow on the ground"""
    sky(p, P.SNOW_SKY)
    r = random.Random(seed)
    if far:
        for k in range(14):
            tx = p.x + r.random()*p.w
            sh_([(tx - 2.5, gy - 4), (tx + 2.5, gy - 4), (tx + 2, p.y + p.h + 5), (tx - 2, p.y + p.h + 5)], 0.72, BG*0.5)
        for k in range(8):
            spruce(p.x + r.random()*p.w, gy + 2, r.uniform(0.3, 0.45), seed=seed + k)
    snow_field(p, gy, seed)
    for tx, ts in bare: bare_tree(p.X(tx), gy - 6, ts, seed=seed)
    for tx, ts in trees: spruce(p.X(tx), gy - 8, ts, seed=seed + 7)


# ------------------------------------------------------------------ the teaser (issue 9)
def cipher_note(x, y, s=1.0, rot=0):
    """a folded paper slip covered in little star-and-dot signs (the cipher of issue 9), sticking out of a book"""
    with T(x, y, s, rot=rot):
        shape([(-22, -16), (22, -16), (24, 16), (-20, 18)], P.LETTER_PAPER if hasattr(P, "LETTER_PAPER") else 0.98, LINE*0.8)
        stroke([(-21, 0), (23, 1)], LINE*0.4, g=0.6)
        r = random.Random(9)
        for row in range(3):
            for col in range(6):
                cx, cy = -16 + col*6.6, 10 - row*8.5
                k = r.randrange(3)
                if k == 0: star(cx, cy, 2.2, 0.2, LINE*0.3)
                elif k == 1: dot(cx, cy, 1.2, 0.1)
                else: stroke([(cx - 2, cy - 1.6), (cx + 2, cy + 1.6)], LINE*0.8)


def book(x, y, s=1.0, rot=0, g=0.45):
    with T(x, y, s, rot=rot):
        shape([(-26, 0), (26, 0), (26, 8), (-26, 8)], 0.95, LINE*0.8)
        for k in range(1, 4): stroke([(-24, k*2), (24, k*2)], LINE*0.3, g=0.6)
        shape([(-27, 8), (27, 8), (27, 12), (-27, 12)], g, LINE*0.8)
        shape([(-27, -4), (27, -4), (27, 0), (-27, 0)], g, LINE*0.8)


def masopust_mask(x, y, s=1.0, rot=0):
    """a paper carnival mask (Masopust): eye holes, a ribbon fringe, a star"""
    with T(x, y, s, rot=rot):
        m = bez((-22, 0), (-24, 12), (-10, 16), (0, 10)) + bez((0, 10), (10, 16), (24, 12), (22, 0)) + \
            bez((22, 0), (18, -10), (6, -8), (0, -3)) + bez((0, -3), (-6, -8), (-18, -10), (-22, 0))
        shape(m, P.MASK, LINE)
        for sx in (-1, 1): shape(ell(sx*10, 3, 5, 3.4, 16, rot=sx*10), 1.0, LINE*0.8)
        star(0, 11, 3, 0.95, LINE*0.4)
        for k in range(5):
            stroke(bez((-22 + k*2, -2), (-26 - k, -8), (-24 - k*2, -16), (-28 - k, -22)), LINE*0.9,
                   g=(P.RIBBON, 0.3, P.APPLE, 0.6, P.RIBBON)[k])
