"""Issue 10 (Záhada ve škole): the girls' forest school on a hillside (two yurts joined by a small log building with
the kumbál), máma and táta, paní učitelka Lucie, pan Karel the školník, the class (Julca, Beatka, Stella, malý Karel),
the guinea pigs Míša and Šiša and their hutch, the hedgehog in the brushwood, the family's red van, boot prints,
wood shavings, the torn note, the phone video call, and the hidden crayons.

Grown-ups are built like the other adults (chars3.Person); the kids use Alica's frame (style3.Kid(False)), so
balloon anchors work with the issue script's hd()."""
import math, random
import lib
from lib import G, ell, bez, rrect, resample
from style3 import *
from style3 import C, _SC, Kid, arm_pts, draw_arm, draw_legs, head_outline, face, notch, hand
import palette as P
from scenes3 import BG, s_, sh_, sky, hills, planks, saw, rake
from chars3 import Person, babicka, deda, star
from attic import kids_drawing
from pond import far_trees
from letter import hand_text


def _neck(k, w=2.8):
    shape([(-w, k.hy - k.hr + 2), (w, k.hy - k.hr + 2), (w + 0.3, k.sh_y + 0.5), (-w - 0.3, k.sh_y + 0.5)], P.SKIN, 0)
    stroke([(-w, k.hy - k.hr + 2.5), (-w - 0.3, k.sh_y + 0.8)], LINE*0.8)
    stroke([(w, k.hy - k.hr + 2.5), (w + 0.3, k.sh_y + 0.8)], LINE*0.8)


def _torso(k, waist, hw=None, flare=0.0):
    """a top from the shoulders down to `waist`: hw = half width at the waist, flare widens the hem"""
    sw, sy = k.sh_w, k.sh_y
    hw = hw or sw + 1.5
    mid = (sy + waist)/2
    return bez((-5, sy + 2.8), (-9, sy + 2.5), (-sw - 1.3, sy + 0.5), (-sw - 1.8, sy - 4)) + \
        bez((-sw - 1.8, sy - 4), (-hw - 0.5, mid + 8), (-hw - flare*0.5, mid - 4), (-hw - flare, waist)) + [(hw + flare, waist)] + \
        bez((hw + flare, waist), (hw + flare*0.5, mid - 4), (hw + 0.5, mid + 8), (sw + 1.8, sy - 4)) + \
        bez((sw + 1.8, sy - 4), (sw + 1.3, sy + 0.5), (9, sy + 2.5), (5, sy + 2.8))


def _ears(k, g=None):
    r, cy = k.hr, k.hy
    for sx in (-1, 1): shape(ell(sx*r*0.98, cy - r*0.05, r*0.2, r*0.3, 14), P.SKIN if g is None else g, LINE*0.8)


def _glasses(r, cy, round_=False):
    for sx in (-1, 1):
        if round_:
            stroke(ell(sx*r*0.4, cy - r*0.02, r*0.25, r*0.23, 24), LINE*0.8, closed=True)
        else:
            stroke(rrect(sx*r*0.4 - r*0.27, cy - r*0.2, r*0.54, r*0.36, r*0.1), LINE*0.85, closed=True)
    stroke([(-r*0.14, cy + r*0.02), (r*0.14, cy + r*0.02)], LINE*0.7)
    for sx in (-1, 1): stroke([(sx*r*0.67, cy + r*0.04), (sx*r*0.96, cy + r*0.12)], LINE*0.6)


# ================================================================== the family
TATA = dict(H=134, hr=10.8, hy=122.6, sh_y=107, sh_w=14, hip=63, knee=33, ankle=5, leg_w=(8.4, 6.6), arm_w=(7.2, 6.4),
            up=21, fo=19)
MAMA = dict(H=118, hr=10.2, hy=107.6, sh_y=93, sh_w=11.6, hip=54, knee=29, ankle=5, leg_w=(7, 5.4), arm_w=(6.2, 5.4),
            up=18, fo=16)
LUCIE = dict(H=121, hr=10.3, hy=110.4, sh_y=95.6, sh_w=11.8, hip=56, knee=30, ankle=5, leg_w=(7, 5.4), arm_w=(6.2, 5.4),
             up=18.5, fo=16.5)
KAREL = dict(H=140, hr=10.6, hy=129.2, sh_y=113.6, sh_w=12.8, hip=67, knee=36, ankle=5, leg_w=(7.4, 6), arm_w=(6.4, 5.8),
             up=22.5, fo=20.5)


def tata(x, y, s=1.0, flip=False, left="down", right="down", mood="happy", look=(0, 0), item=None, shadow=True,
         legs="stand"):
    """táta: very short hair, a short trimmed beard and moustache, glasses, a fleece, trousers with lots of pockets,
    trekking shoes. The tallest of the family."""
    k = Person(**TATA)
    if shadow: cast_shadow(x, y, 19*s, 3*s)
    with T(x, y, s, flip):
        draw_legs(k, legs, P.TATA_CARGO, boots=P.TATA_SHOES, boot_top=k.ankle + 6)
        # the pockets: a big flap pocket on each thigh, a small one lower down
        if legs != "walk":
            for sx in (-1, 1):
                pk = [(sx*1.2, k.knee + 7), (sx*8.2, k.knee + 7), (sx*8.4, k.knee + 18), (sx*1.2, k.knee + 18)]
                shape(pk, P.TATA_CARGO, LINE*0.7)
                stroke([(sx*1.2, k.knee + 15.5), (sx*8.4, k.knee + 15.5)], LINE*0.6)
                dot(sx*4.8, k.knee + 13.5, 0.7, 0.2)
                shape([(sx*2.2, k.ankle + 10), (sx*7.4, k.ankle + 10), (sx*7.4, k.ankle + 16), (sx*2.2, k.ankle + 16)],
                      P.TATA_CARGO, LINE*0.5)
        draw_arm(k, -1, left, P.TATA_FLEECE)
        tors = _torso(k, 58, 16)
        form(tors, P.TATA_FLEECE, sdx=-2.2, sdy=1.2)
        shape([(-16.3, 58), (16.3, 58), (16.4, 62), (-16.4, 62)], P.TATA_FLEECE, LINE*0.8)
        stroke([(0.5, k.sh_y + 3), (0.5, 58)], LINE*0.8)
        shape([(-1.2, k.sh_y - 6), (2.2, k.sh_y - 6), (2.2, k.sh_y - 2), (-1.2, k.sh_y - 2)], 0.3, LINE*0.5)
        for sx in (-1, 1):   # chest pockets with zips
            stroke([(sx*5, k.sh_y - 12), (sx*11, k.sh_y - 14)], LINE*0.6)
            stroke([(sx*5, 74), (sx*12, 74)], LINE*0.5)
        # collar stand
        shape(bez((-6.5, k.sh_y + 5), (-4, k.sh_y + 2), (4, k.sh_y + 2), (6.5, k.sh_y + 5)) + [(6, k.sh_y + 0.5), (-6, k.sh_y + 0.5)],
              P.TATA_FLEECE, LINE*0.8)
        h, fa = draw_arm(k, 1, right, P.TATA_FLEECE)
        if item: item(*h)
        _neck(k, 3.2)
        r, cy = k.hr, k.hy
        _ears(k)
        shape(head_outline(k), P.SKIN)
        # short trimmed beard along the jaw and a moustache of the same length (drawn under the face lines)
        bd = bez((-r*0.97, cy - r*0.05), (-r*1.0, cy - r*0.8), (-r*0.5, cy - r*1.12), (0, cy - r*1.12)) + \
             bez((0, cy - r*1.12), (r*0.5, cy - r*1.12), (r*1.0, cy - r*0.8), (r*0.97, cy - r*0.05)) + \
             bez((r*0.97, cy - r*0.05), (r*0.75, cy - r*0.35), (r*0.45, cy - r*0.72), (0, cy - r*0.74)) + \
             bez((0, cy - r*0.74), (-r*0.45, cy - r*0.72), (-r*0.75, cy - r*0.35), (-r*0.97, cy - r*0.05))
        shape(bd, P.TATA_BEARD, LINE*0.6)
        mst = bez((-r*0.42, cy - r*0.5), (-r*0.3, cy - r*0.3), (r*0.3, cy - r*0.3), (r*0.42, cy - r*0.5)) + \
              bez((r*0.42, cy - r*0.5), (r*0.2, cy - r*0.44), (-r*0.2, cy - r*0.44), (-r*0.42, cy - r*0.5))
        fill(mst, P.TATA_BEARD)
        rr = random.Random(5)
        for _ in range(22):
            a = rr.uniform(200, 340); d = rr.uniform(0.8, 1.02)
            dot(math.cos(math.radians(a))*r*d, cy + math.sin(math.radians(a))*r*d, 0.25, 0.15)
        face(0, cy, r, mood, look)
        # very short hair: a thin cap close to the skull
        hair = bez((-r*1.0, cy + r*0.15), (-r*1.08, cy + r*1.12), (r*1.08, cy + r*1.12), (r*1.0, cy + r*0.15)) + \
               bez((r*1.0, cy + r*0.15), (r*0.92, cy + r*0.55), (r*0.6, cy + r*0.78), (0, cy + r*0.8)) + \
               bez((0, cy + r*0.8), (-r*0.6, cy + r*0.78), (-r*0.92, cy + r*0.55), (-r*1.0, cy + r*0.15))
        shape(hair, P.TATA_HAIR, LINE*0.8)
        for xx in (-0.6, -0.3, 0, 0.3, 0.6):
            stroke([(r*xx, cy + r*0.86), (r*xx*1.05, cy + r*0.98)], LINE*0.4, g=0.15)
        _glasses(r, cy)


def mama(x, y, s=1.0, flip=False, left="down", right="down", mood="happy", look=(0, 0), item=None, shadow=True,
         legs="stand", outfit="out", hair="bun"):
    """máma, a head shorter than táta. outfit: "out" (neat coat, trousers, ankle boots, a scarf) or "home"
    (hoodie and sweatpants). hair: "bun" (a tight bun on top) or "down" (to her shoulders)"""
    k = Person(**MAMA)
    if shadow: cast_shadow(x, y, 16*s, 2.8*s)
    r, cy = k.hr, k.hy
    home = outfit == "home"
    with T(x, y, s, flip):
        if hair == "down":
            back = bez((-r*1.02, cy + r*0.2), (-r*1.25, cy - r*0.5), (-r*1.3, cy - r*1.2), (-r*1.15, cy - r*1.55)) + \
                   [(r*1.15, cy - r*1.55)] + bez((r*1.15, cy - r*1.55), (r*1.3, cy - r*1.2), (r*1.25, cy - r*0.5), (r*1.02, cy + r*0.2))
            shape(back, P.MAMA_HAIR)
        draw_legs(k, legs, P.SWEATPANTS if home else P.MAMA_TROUSERS, boots=0.95 if home else P.MAMA_SHOES,
                  boot_top=k.ankle + (2.5 if home else 6))
        top = P.MAMA_HOODIE if home else P.MAMA_COAT
        draw_arm(k, -1, left, top)
        if home:
            tors = _torso(k, 50, 13.5)
            form(tors, top, sdx=-2, sdy=1.2)
            shape([(-13.6, 50), (13.6, 50), (13.6, 53.5), (-13.6, 53.5)], top, LINE*0.8)
            stroke(bez((-8, 57), (-4, 60), (4, 60), (8, 57)) + [(8, 66), (-8, 66), (-8, 57)], LINE*0.6, closed=True)
            shape(bez((-7, k.sh_y + 3), (-9, k.sh_y + 8), (9, k.sh_y + 8), (7, k.sh_y + 3)) + [(0, k.sh_y + 0.5)], top, LINE*0.8)
            for sx in (-1, 1): stroke([(sx*2, k.sh_y + 1), (sx*2.4, k.sh_y - 9)], LINE*0.6)
        else:
            tors = _torso(k, 34, 14, flare=1.5)
            form(tors, top, sdx=-2.2, sdy=1.2)
            stroke([(0.5, k.sh_y + 2), (0.5, 34)], LINE*0.7)
            shape([(-14.4, 56), (14.4, 56), (14.6, 59.5), (-14.6, 59.5)], top, LINE*0.8)
            for by in (78, 68, 46): shape(ell(-2.6, by, 1.0, 1.0, 10), 0.2, LINE*0.5)
            for sx in (-1, 1):
                stroke([(sx*5, 48), (sx*12, 47)], LINE*0.6)
                shape([(sx*1, k.sh_y + 1.5), (sx*8.5, k.sh_y + 2.5), (sx*10.5, k.sh_y - 3), (sx*3, k.sh_y - 12)], top, LINE*0.7)
            # scarf
            shape([(-6, k.sh_y + 5), (6, k.sh_y + 5), (6.4, k.sh_y), (-6.4, k.sh_y)], P.MAMA_SCARF, LINE*0.8)
            shape([(1.5, k.sh_y + 0.5), (5.5, k.sh_y + 0.5), (6.2, k.sh_y - 13), (2.6, k.sh_y - 12.5)], P.MAMA_SCARF, LINE*0.8)
            for xx in (2.8, 4.2, 5.6): stroke([(xx, k.sh_y - 12.6), (xx + 0.2, k.sh_y - 15)], LINE*0.5)
        h, fa = draw_arm(k, 1, right, top)
        if item: item(*h)
        _neck(k, 2.7)
        _ears(k)
        shape(head_outline(k), P.SKIN)
        face(0, cy, r, mood, look)
        if hair == "bun":
            shape(ell(0, cy + r*1.42, r*0.48, r*0.4, 24), P.MAMA_HAIR, LINE)
            stroke(ell(0, cy + r*1.42, r*0.26, r*0.2, 12, 20, 300), LINE*0.5, g=0.15)
        cap = bez((-r*1.0, cy + r*0.05), (-r*1.1, cy + r*1.15), (r*1.1, cy + r*1.15), (r*1.0, cy + r*0.05)) + \
              bez((r*1.0, cy + r*0.05), (r*0.8, cy + r*0.55), (r*0.35, cy + r*0.6), (-r*0.15, cy + r*0.72)) + \
              bez((-r*0.15, cy + r*0.72), (-r*0.5, cy + r*0.5), (-r*0.8, cy + r*0.4), (-r*1.0, cy + r*0.05))
        shape(cap, P.MAMA_HAIR)
        if hair == "bun":
            for xx in (-0.6, -0.25, 0.15, 0.5):
                stroke(bez((r*xx, cy + r*0.7), (r*xx*0.8, cy + r*0.95), (r*xx*0.5, cy + r*1.08), (r*xx*0.2, cy + r*1.12)), LINE*0.45, g=0.15)
        else:
            for sx in (-1, 1):
                lock = bez((sx*r*0.95, cy + r*0.3), (sx*r*1.2, cy - r*0.3), (sx*r*1.25, cy - r*1.0), (sx*r*1.15, cy - r*1.5)) + \
                       [(sx*r*0.85, cy - r*1.45)] + bez((sx*r*0.85, cy - r*1.45), (sx*r*0.95, cy - r*0.9), (sx*r*0.95, cy - r*0.3), (sx*r*0.8, cy + r*0.1))
                shape(lock, P.MAMA_HAIR)


def lucie(x, y, s=1.0, flip=False, left="down", right="down", mood="happy", look=(0, 0), item=None, shadow=True,
          legs="stand"):
    """paní učitelka Lucie: a long skirt to her ankles, a warm sweater, a long plait over her shoulder"""
    k = Person(**LUCIE)
    if shadow: cast_shadow(x, y, 17*s, 2.8*s)
    r, cy = k.hr, k.hy
    with T(x, y, s, flip):
        draw_legs(k, legs, P.STOCKINGS, boots=P.KID_BOOTS, boot_top=k.ankle + 5)
        draw_arm(k, -1, left, P.LUCIE_TOP)
        skirt = [(-12.5, 60), (12.5, 60)] + bez((12.5, 60), (15, 40), (18, 22), (20, 8)) + \
                bez((20, 8), (6, 6), (-6, 6), (-20, 8)) + bez((-20, 8), (-18, 22), (-15, 40), (-12.5, 60))
        form(skirt, P.LUCIE_SKIRT, sdx=-2.4, sdy=1)
        for xx in (-9, -2, 6): stroke(bez((xx*0.6, 58), (xx*0.8, 40), (xx, 24), (xx*1.15, 9)), LINE*0.45, g=0.25)
        tors = _torso(k, 54, 14)
        form(tors, P.LUCIE_TOP, sdx=-2, sdy=1.2)
        shape([(-14.2, 54), (14.2, 54), (14.4, 58.5), (-14.4, 58.5)], P.LUCIE_TOP, LINE*0.8)
        for yy in (66, 74, 82):
            stroke(bez((-13, yy), (-5, yy - 1.5), (5, yy - 1.5), (13, yy)), LINE*0.4, g=0.35)
        shape(bez((-5.5, k.sh_y + 3), (-3, k.sh_y - 2), (3, k.sh_y - 2), (5.5, k.sh_y + 3)) + [(0, k.sh_y + 1)], P.LUCIE_TOP, LINE*0.7)
        h, fa = draw_arm(k, 1, right, P.LUCIE_TOP)
        if item: item(*h)
        _neck(k, 2.7)
        shape(head_outline(k), P.SKIN)
        face(0, cy, r, mood, look)
        cap = bez((-r*1.02, cy + r*0.05), (-r*1.12, cy + r*1.18), (r*1.12, cy + r*1.18), (r*1.02, cy + r*0.05)) + \
              bez((r*1.02, cy + r*0.05), (r*0.7, cy + r*0.45), (r*0.25, cy + r*0.62), (0, cy + r*0.66)) + \
              bez((0, cy + r*0.66), (-r*0.25, cy + r*0.62), (-r*0.7, cy + r*0.45), (-r*1.02, cy + r*0.05))
        shape(cap, P.LUCIE_HAIR)
        stroke(bez((0, cy + r*1.15), (0.2, cy + r*0.95), (0, cy + r*0.8), (0, cy + r*0.66)), LINE*0.5, g=0.3)
        # the plait over her right shoulder
        for i in range(5):
            yy = cy - r*0.4 - i*r*0.62
            shape(ell(r*0.95 + i*0.25, yy, r*0.3, r*0.36, 16, rot=10), P.LUCIE_HAIR, LINE*0.7)
        shape(ell(r*1.05 + 1.4, cy - r*3.4, r*0.12, r*0.14, 10), P.KULICH, LINE*0.5)


def skolnik(x, y, s=1.0, flip=False, left="down", right="down", mood="happy", look=(0, 0), item=None, shadow=True,
            legs="stand", hat=True):
    """pan Karel, the školník: tall and slim, no beard, a work jacket with pockets, trousers tucked into green holínky,
    a red woolly hat (kulich). hat=False: his hat is gone (it's the guinea pigs' bed) and his ears go red with cold"""
    k = Person(**KAREL)
    if shadow: cast_shadow(x, y, 17*s, 2.8*s)
    r, cy = k.hr, k.hy
    with T(x, y, s, flip):
        draw_legs(k, legs, P.KAREL_TROUSERS, boots=P.HOLINKY, boot_top=k.knee + 3)
        for ax in ((-9, 7.2) if legs == "walk" else (-4.2, 4.2)):
            stroke([(ax - 3.2, k.knee + 1), (ax + 3.2, k.knee + 1)], LINE*0.5, g=0.5)
        draw_arm(k, -1, left, P.KAREL_JACKET)
        tors = _torso(k, 60, 14)
        form(tors, P.KAREL_JACKET, sdx=-2.2, sdy=1.2)
        stroke([(0.5, k.sh_y + 2.5), (0.5, 60)], LINE*0.7)
        for by in (104, 94, 84, 74, 66): shape(ell(-2.2, by, 0.9, 0.9, 10), 0.2, LINE*0.5)
        for sx in (-1, 1):
            shape([(sx*4.5, 63), (sx*12.5, 63), (sx*12.5, 73), (sx*4.5, 73)], P.KAREL_JACKET, LINE*0.6)
            stroke([(sx*4.5, 71), (sx*12.5, 71)], LINE*0.5)
            shape([(sx*4, 92), (sx*10, 92), (sx*10, 99), (sx*4, 99)], P.KAREL_JACKET, LINE*0.5)
            shape([(sx*1, k.sh_y + 2), (sx*8, k.sh_y + 2.4), (sx*9.5, k.sh_y - 4), (sx*3, k.sh_y - 6)], P.KAREL_JACKET, LINE*0.7)
        stroke([(9, 92), (9.6, 101)], LINE*1.2, g=P.CRAYON_ORANGE)   # a carpenter's pencil in the pocket
        h, fa = draw_arm(k, 1, right, P.KAREL_JACKET)
        if item: item(*h)
        _neck(k, 2.8)
        _ears(k, None if hat else P.EAR_RED)
        shape(head_outline(k), P.SKIN)
        face(0, cy, r, mood, look)
        if hat:
            crown = bez((-r*1.05, cy + r*0.45), (-r*1.15, cy + r*1.75), (r*1.15, cy + r*1.75), (r*1.05, cy + r*0.45)) + [(-r*1.05, cy + r*0.45)]
            shape(crown, P.KULICH)
            for xx in (-0.6, -0.2, 0.2, 0.6):
                stroke([(r*xx, cy + r*0.85), (r*xx*0.9, cy + r*1.55)], LINE*0.4, g=0.25)
            shape([(-r*1.1, cy + r*0.38), (r*1.1, cy + r*0.38), (r*1.12, cy + r*0.82), (-r*1.12, cy + r*0.82)], P.KULICH, LINE*0.8)
            for xx in range(-9, 10, 3): stroke([(r*xx/9, cy + r*0.42), (r*xx/9, cy + r*0.78)], LINE*0.3, g=0.25)
            shape(ell(0, cy + r*1.85, r*0.32, r*0.28, 16), P.KULICH, LINE*0.7)
        else:
            hair = bez((-r*1.0, cy + r*0.15), (-r*1.12, cy + r*1.2), (r*1.12, cy + r*1.2), (r*1.0, cy + r*0.15)) + \
                   bez((r*1.0, cy + r*0.15), (r*0.8, cy + r*0.6), (r*0.2, cy + r*0.55), (-r*0.2, cy + r*0.72)) + \
                   bez((-r*0.2, cy + r*0.72), (-r*0.6, cy + r*0.55), (-r*0.85, cy + r*0.45), (-r*1.0, cy + r*0.15))
            shape(hair, P.KAREL_HAIR)
            for xx in (-0.5, 0.0, 0.45):
                stroke(bez((r*xx, cy + r*1.1), (r*xx + 1, cy + r*1.25), (r*xx + 2, cy + r*1.3), (r*xx + 3, cy + r*1.25)), LINE*0.6)


# ================================================================== the class
KIDS = ("julca", "beatka", "stella", "karel")
_JACKET = {"julca": "JULCA_JACKET", "beatka": "BEATKA_JACKET", "stella": "STELLA_JACKET", "karel": "KARELK_JACKET"}


def spoluzak(x, y, s=1.0, who="julca", flip=False, left="down", right="down", mood="happy", look=(0, 0), item=None,
             shadow=True, legs="stand"):
    """Alica's classmates, dressed for a day outdoors: an anorak, rain trousers, rubber boots.
    julca: dark low pigtails and round glasses; beatka: a blonde bob with a hairband; stella: a long auburn ponytail;
    karel (malý Karel): short dark tousled hair"""
    k = Kid(False)
    if shadow: cast_shadow(x, y, 15*s, 2.6*s)
    r, cy = k.hr, k.hy
    jacket = getattr(P, _JACKET[who])
    with T(x, y, s, flip):
        if who == "julca":
            for sx in (-1, 1):
                pig = bez((sx*r*0.85, cy - r*0.3), (sx*r*1.4, cy - r*0.7), (sx*r*1.45, cy - r*1.5), (sx*r*1.25, cy - r*2.0)) + \
                      bez((sx*r*1.25, cy - r*2.0), (sx*r*1.0, cy - r*1.5), (sx*r*0.95, cy - r*0.9), (sx*r*0.6, cy - r*0.55))
                shape(pig, P.JULCA_HAIR)
                shape(ell(sx*r*1.18, cy - r*0.62, r*0.16, r*0.12, 10), P.CRAYON_RED, LINE*0.5)
        elif who == "stella":
            tail = bez((r*0.3, cy + r*0.6), (r*1.6, cy + r*0.5), (r*1.6, cy - r*1.2), (r*1.2, cy - r*2.6)) + \
                   bez((r*1.2, cy - r*2.6), (r*0.95, cy - r*1.6), (r*1.0, cy - r*0.5), (r*0.2, cy + r*0.2))
            shape(tail, P.STELLA_HAIR)
        draw_legs(k, legs, P.RAIN_TROUSERS, boots=P.KID_BOOTS, boot_top=k.ankle + 9)
        draw_arm(k, -1, left, jacket)
        body = bez((-4.2, k.sh_y + 2.8), (-7.5, k.sh_y + 2.5), (-k.sh_w - 1.2, k.sh_y + 1), (-k.sh_w - 1.6, k.sh_y - 3)) + \
               bez((-k.sh_w - 1.6, k.sh_y - 3), (-12, 60), (-12.5, 50), (-12.6, 42)) + [(12.6, 42)] + \
               bez((12.6, 42), (12.5, 50), (12, 60), (k.sh_w + 1.6, k.sh_y - 3)) + \
               bez((k.sh_w + 1.6, k.sh_y - 3), (k.sh_w + 1.2, k.sh_y + 1), (7.5, k.sh_y + 2.5), (4.2, k.sh_y + 2.8))
        form(body, jacket, sdx=-2, sdy=1.2)
        shape([(-12.7, 42), (12.7, 42), (12.8, 45.5), (-12.8, 45.5)], jacket, LINE*0.8)
        stroke([(0.5, k.sh_y + 1), (0.6, 42)], LINE*0.7)
        for sx in (-1, 1): stroke([(sx*4.5, 54), (sx*10.5, 52)], LINE*0.6)
        # the hood lying on the shoulders
        shape(bez((-8, k.sh_y + 2), (-10, k.sh_y + 7), (10, k.sh_y + 7), (8, k.sh_y + 2)) + [(0, k.sh_y)], jacket, LINE*0.8)
        h, fa = draw_arm(k, 1, right, jacket)
        if item: item(*h)
        shape([(-2.6, k.sh_y + 5), (2.6, k.sh_y + 5), (2.8, k.sh_y + 0.8), (-2.8, k.sh_y + 0.8)], P.SKIN, 0)
        _ears(k)
        shape(head_outline(k), P.SKIN)
        face(0, cy, r, mood, look, freckles=who == "karel")
        if who == "julca":
            cap = bez((-r*1.0, cy + r*0.0), (-r*1.1, cy + r*1.2), (r*1.1, cy + r*1.2), (r*1.0, cy + r*0.0)) + \
                  bez((r*1.0, cy + r*0.0), (r*0.75, cy + r*0.55), (r*0.3, cy + r*0.6), (0, cy + r*0.62)) + \
                  bez((0, cy + r*0.62), (-r*0.3, cy + r*0.6), (-r*0.75, cy + r*0.55), (-r*1.0, cy + r*0.0))
            shape(cap, P.JULCA_HAIR)
            stroke([(0, cy + r*1.15), (0, cy + r*0.64)], LINE*0.5, g=0.7)
            _glasses(r, cy, round_=True)
        elif who == "beatka":
            bob = bez((-r*1.08, cy - r*0.55), (-r*1.22, cy + r*1.3), (r*1.22, cy + r*1.3), (r*1.08, cy - r*0.55)) + \
                  bez((r*1.08, cy - r*0.55), (r*0.95, cy - r*0.1), (r*0.9, cy + r*0.35), (r*0.5, cy + r*0.45)) + \
                  [(-r*0.5, cy + r*0.45)] + bez((-r*0.5, cy + r*0.45), (-r*0.9, cy + r*0.35), (-r*0.95, cy - r*0.1), (-r*1.08, cy - r*0.55))
            shape(bob, P.BEATKA_HAIR)
            stroke(bez((-r*1.0, cy + r*0.55), (-r*0.6, cy + r*1.12), (r*0.6, cy + r*1.12), (r*1.0, cy + r*0.55)), LINE*2.2, g=0.0)
            stroke(bez((-r*1.0, cy + r*0.55), (-r*0.6, cy + r*1.12), (r*0.6, cy + r*1.12), (r*1.0, cy + r*0.55)), LINE*1.2, g=P.BEATKA_BAND)
        elif who == "stella":
            cap = bez((-r*1.02, cy + r*0.0), (-r*1.1, cy + r*1.2), (r*1.1, cy + r*1.2), (r*1.02, cy + r*0.0)) + \
                  bez((r*1.02, cy + r*0.0), (r*0.8, cy + r*0.6), (r*0.2, cy + r*0.5), (-r*0.4, cy + r*0.68)) + \
                  bez((-r*0.4, cy + r*0.68), (-r*0.7, cy + r*0.5), (-r*0.9, cy + r*0.35), (-r*1.02, cy + r*0.0))
            shape(cap, P.STELLA_HAIR)
            shape(ell(r*0.95, cy + r*0.55, r*0.18, r*0.18, 10), P.CRAYON_BLUE, LINE*0.5)
        else:
            hair = [(-r*1.02, cy + r*0.1), (-r*1.2, cy + r*0.6), (-r*0.92, cy + r*0.62), (-r*1.0, cy + r*1.05),
                    (-r*0.5, cy + r*0.95), (-r*0.4, cy + r*1.32), (0, cy + r*1.05), (r*0.35, cy + r*1.38), (r*0.5, cy + r*1.0),
                    (r*0.95, cy + r*1.15), (r*0.88, cy + r*0.7), (r*1.18, cy + r*0.55), (r*1.02, cy + r*0.1),
                    (r*0.7, cy + r*0.45), (r*0.3, cy + r*0.5), (0, cy + r*0.62), (-r*0.4, cy + r*0.45), (-r*0.75, cy + r*0.52)]
            shape(hair, P.KARELK_HAIR)


# ================================================================== animals
def morce(x, y, s=1.0, flip=False, who="misa", look=(0, 0)):
    """the class guinea pigs, both brown. Míša: big and round, a pale patch on her chest. Šiša: smaller, with a
    swirly tuft (rozcuch) on her head. Faces right, (x, y) = the ground under her"""
    k = 1.0 if who == "misa" else 0.8
    with T(x, y, s*k, flip):
        if who == "misa":
            body = bez((-17, 4), (-20, 20), (2, 23), (10, 18)) + bez((10, 18), (17, 16), (19.5, 9), (17.5, 4)) + \
                   bez((17.5, 4), (12, -0.5), (-12, -0.5), (-17, 4))
        else:
            body = bez((-15, 4), (-17, 18), (2, 21), (10, 17)) + bez((10, 17), (17, 15), (19, 9), (17, 4)) + \
                   bez((17, 4), (12, 0), (-10, 0), (-15, 4))
        fill(body, P.MORCE)
        C.saveState(); C.clipPath(poly(body), stroke=0, fill=0)
        if who == "misa":
            fill(ell(12, 4, 7, 6, 20), P.MORCE_LIGHT)
            fill(ell(-10, 16, 10, 7, 20), P.MORCE_DARK)
        else:
            fill(ell(-6, 17, 9, 6, 20), P.MORCE_DARK)
        C.restoreState()
        offset_shadow(body, -1.2, 1, 0.12)
        stroke(body, LINE, closed=True)
        rr = random.Random(7 if who == "misa" else 8)
        for _ in range(9):
            px, py = rr.uniform(-12, 6), rr.uniform(8, 18)
            stroke([(px, py), (px - 1.5, py - 1.2)], LINE*0.35, g=0.25)
        shape(ell(9, 17.5, 2.8, 2.1, 12, rot=20), P.MORCE_DARK, LINE*0.6)
        dot(13.5 + look[0]*0.4, 11.5 + look[1]*0.4, 1.2, 0.0); dot(13.9, 12, 0.4, 1.0)
        dot(18.3, 7.5, 0.8, 0.2)
        for sx in (-1, 1):
            stroke([(18.2, 6.6), (24, 6.6 + sx*2.2)], LINE*0.3)
        for fx in (-9, 9): shape(ell(fx, 0.8, 2.4, 1.1, 10), P.MORCE_LIGHT, LINE*0.5)
        if who == "sisa":
            cx, cyy = 5, 20
            for i in range(9):
                a = math.radians(i*40)
                stroke(bez((cx, cyy), (cx + math.cos(a)*2, cyy + math.sin(a)*2 + 1), (cx + math.cos(a + 0.6)*4, cyy + math.sin(a + 0.6)*4 + 1.5),
                           (cx + math.cos(a + 0.9)*5.5, cyy + math.sin(a + 0.9)*5 + 2)), LINE*0.6, g=P.MORCE_DARK)
            stroke(ell(cx, cyy + 0.5, 1.6, 1.4, 10, 0, 300), LINE*0.5)


def jezek(x, y, s=1.0, flip=False, pose="walk", hay=False, mood="open"):
    """the hedgehog from the brushwood, just woken from his winter sleep. Faces right, (x, y) = the ground.
    pose: walk, curl (a spiky ball). hay: wisps of hay caught on his spines"""
    with T(x, y, s, flip):
        cast_shadow(0, 0, 18, 2.2)
        if pose == "curl":
            pts = []
            for i in range(60):
                a = math.tau*i/60; rr = 14 if i % 2 == 0 else 11.5
                pts.append((math.cos(a)*rr, 13 + math.sin(a)*rr))
            shape(pts, P.JEZEK, LINE*0.8)
            for i in range(0, 60, 2):
                a = math.tau*i/60
                stroke([(math.cos(a)*9, 13 + math.sin(a)*9), (math.cos(a)*13, 13 + math.sin(a)*13)], LINE*0.5, g=P.JEZEK_TIP)
            dot(9, 9, 1.0, 0.0)
        else:
            for fx in (-10, -4, 8, 12): shape(ell(fx, 1.2, 2.4, 1.4, 10), 0.25, LINE*0.5)
            snout = bez((4, 3), (6, 13), (12, 13), (16, 10)) + bez((16, 10), (20, 8), (24, 6), (25.5, 5)) + \
                    bez((25.5, 5), (24, 3), (18, 2.5), (12, 2)) + [(4, 3)]
            form(snout, P.JEZEK_FACE, sdx=-0.8, sdy=0.6, sh=0.1)
            dot(25.2, 5, 1.2, 0.0)
            if mood == "sleepy":
                stroke(bez((14, 8.5), (15, 7.5), (16.5, 7.5), (17.2, 8.5)), LINE*0.8)
            else:
                dot(15.8, 8.6, 1.2, 0.0); dot(16.2, 9.1, 0.4, 1.0)
            shape(ell(10.5, 12.5, 2, 1.7, 10), P.JEZEK_FACE, LINE*0.6)
            N = 46
            pts = [(11, 13)] + [(-3 + math.cos(math.pi*(0.06 + 0.9*i/N))*17*(1.0 if i % 2 == 0 else 0.82),
                                 2 + math.sin(math.pi*(0.06 + 0.9*i/N))*19*(1.0 if i % 2 == 0 else 0.82)) for i in range(N + 1)] + \
                  [(-20.5, 3), (-6, 1.5), (6, 2.5)]
            shape(pts, P.JEZEK, LINE*0.8)
            for i in range(1, N, 2):
                a = math.pi*(0.06 + 0.9*i/N)
                stroke([(-3 + math.cos(a)*11, 2 + math.sin(a)*12), (-3 + math.cos(a)*16, 2 + math.sin(a)*18)], LINE*0.5, g=P.JEZEK_TIP)
        if hay:
            r = random.Random(4)
            for _ in range(7):
                px, py = r.uniform(-14, 6), r.uniform(10, 19)
                a = r.uniform(-30, 30)
                stroke(bez((px - 6, py), (px - 2, py + 2), (px + 2, py + 1), (px + 7, py + 3 + a*0.05)), LINE*1.0, g=0.0)
                stroke(bez((px - 6, py), (px - 2, py + 2), (px + 2, py + 1), (px + 7, py + 3 + a*0.05)), LINE*0.6, g=P.HAY)


# ================================================================== props
def hay_wisp(x, y, s=1.0, rot=0, seed=1):
    r = random.Random(seed)
    with T(x, y, s, rot=rot):
        for _ in range(5):
            y0 = r.uniform(-1.5, 1.5)
            pts = bez((-6, y0), (-2, y0 + r.uniform(-1.5, 1.5)), (2, y0 + r.uniform(-1.5, 1.5)), (6 + r.uniform(-1, 2), y0 + r.uniform(-2, 2)), 6)
            stroke(pts, LINE*1.6, g=0.0); stroke(pts, LINE*0.9, g=P.HAY)


def hay_trail(pts, n=10, s=1.0, seed=3):
    """wisps of hay dropped along a path (pts = a polyline)"""
    P_ = resample(pts, 2.0)
    r = random.Random(seed)
    for i in range(n):
        q = P_[min(len(P_) - 1, int(i*(len(P_) - 1)/max(1, n - 1)))]
        hay_wisp(q[0] + r.uniform(-3, 3), q[1] + r.uniform(-2, 2), s*r.uniform(0.8, 1.1), r.uniform(-40, 40), seed + i)


def holinka_print(x, y, s=1.0, rot=0, g=P.MUD_DARK):
    """a big rubber-boot print with a herringbone tread (pan Karel's holínky). Local length ~34, toe at +y"""
    with T(x, y, s, rot=rot):
        sole = bez((0, -17), (6.5, -17), (7, -9), (6, -3)) + bez((6, -3), (6.5, 5), (7.5, 11), (5, 17)) + \
               bez((5, 17), (0, 19), (-5, 19), (-7, 15)) + bez((-7, 15), (-8, 8), (-6.5, 2), (-6, -3)) + \
               bez((-6, -3), (-7, -9), (-6.5, -17), (0, -17))
        fill(sole, g)
        C.saveState(); C.clipPath(poly(sole), stroke=0, fill=0)
        for yy in range(-17, 20, 4):
            stroke([(-8, yy - 2), (0, yy + 1), (8, yy - 2)], LINE*0.9, g=P.MUD, taper=False)
        C.restoreState()
        stroke([(-6.5, -1), (6.5, -1)], LINE*1.6, g=P.MUD)


def trek_print(x, y, s=1.0, rot=0, g=P.MUD_DARK):
    """táta's trekking shoe: a shorter sole with square lugs (local length ~30)"""
    with T(x, y, s, rot=rot):
        sole = bez((0, -14), (5.5, -14), (6, -7), (5, -2)) + bez((5, -2), (5.5, 5), (6.5, 10), (4, 15)) + \
               bez((4, 15), (0, 16.5), (-4, 16.5), (-6, 13)) + bez((-6, 13), (-7, 7), (-5.5, 1), (-5, -2)) + \
               bez((-5, -2), (-6, -7), (-5.5, -14), (0, -14))
        fill(sole, g)
        for yy in (-11, -6, 3, 8, 12):
            for xx in (-3, 1.5):
                fill([(xx, yy), (xx + 2.6, yy), (xx + 2.6, yy + 2.6), (xx, yy + 2.6)], P.MUD)


def kid_print(x, y, s=1.0, rot=0, g=P.MUD_DARK):
    """a child's rubber boot (small, plain stripes)"""
    with T(x, y, s, rot=rot):
        sole = ell(0, 0, 4.2, 9, 20)
        fill(sole, g)
        for yy in (-6, -3, 3, 6): stroke([(-3, yy), (3, yy)], LINE*0.7, g=P.MUD)


def mud_strip(x0, y0, x1, y1, h=10, seed=2):
    """a soft muddy strip along the ground between (x0, y0) and (x1, y1), where prints show"""
    r = random.Random(seed)
    n = 14
    top, bot = [], []
    for i in range(n + 1):
        t = i/n; xx = x0 + (x1 - x0)*t; yy = y0 + (y1 - y0)*t
        top.append((xx, yy + h/2 + r.uniform(-2, 2))); bot.append((xx, yy - h/2 + r.uniform(-2, 2)))
    fill(top + bot[::-1], P.MUD, 0.75)


def hobliny(x, y, s=1.0, n=5, seed=1):
    """curly wood shavings"""
    r = random.Random(seed)
    with T(x, y, s):
        for i in range(n):
            cx, cy = r.uniform(-12, 12), r.uniform(-3, 4)
            rr = r.uniform(2.4, 4)
            pts = [(cx + math.cos(a/10)*rr*(1 - a/120), cy + math.sin(a/10)*rr*0.7*(1 - a/120)) for a in range(0, 90)]
            stroke(pts, LINE*2.2, g=0.0); stroke(pts, LINE*1.4, g=P.HOBLINY)


def kulich(x, y, s=1.0, rot=0, nest=False):
    """pan Karel's red woolly hat lying on its side; nest=True: turned up as a soft bed, straw round it"""
    with T(x, y, s, rot=rot):
        if nest:
            r = random.Random(3)
            for _ in range(16):
                px = r.uniform(-34, 34); py = r.uniform(-2, 4)
                stroke([(px - 6, py), (px + 6, py + r.uniform(-2, 2))], LINE*1.3, g=P.STRAW)
            b = bez((-30, 2), (-32, 16), (32, 16), (30, 2)) + bez((30, 2), (20, -4), (-20, -4), (-30, 2))
            shape(b, P.KULICH, LINE)
            shape(ell(0, 13, 29, 5, 30), 0.3, LINE*0.6)
            for xx in range(-26, 28, 5): stroke([(xx, 0), (xx*0.95, 12)], LINE*0.3, g=0.25)
            return
        crown = bez((-14, 0), (-15, 18), (12, 20), (16, 4)) + [(16, 0)]
        shape(crown, P.KULICH, LINE)
        shape([(-15, 0), (17, 0), (17, 6), (-15, 6)], P.KULICH, LINE*0.8)
        for xx in range(-13, 16, 3): stroke([(xx, 0.5), (xx, 5.5)], LINE*0.3, g=0.25)
        shape(ell(6, 21, 4.4, 3.8, 14), P.KULICH, LINE*0.7)


def pastelka(x, y, s=1.0, rot=0, g=None):
    """a wax crayon: a short six-sided stick with a paper wrap and a sharpened tip; (x, y) = its middle"""
    g = P.CRAYON_RED if g is None else g
    with T(x, y, s, rot=rot):
        body = [(-12, -2.6), (8, -2.6), (8, 2.6), (-12, 2.6)]
        shape(body, g, LINE*0.6)
        shape([(-7, -2.6), (4, -2.6), (4, 2.6), (-7, 2.6)], 1.0, LINE*0.5)
        for xx in (-5, 2): stroke([(xx, -2.4), (xx, 2.4)], LINE*0.3, g=0.4)
        shape([(8, -2.6), (13, -0.9), (14, 0), (13, 0.9), (8, 2.6)], g, LINE*0.6)
        stroke([(-12, 0.6), (8, 0.6)], LINE*0.3, g=0.3)


def _crayon_out(r):
    w = r*0.38; L = r*1.6
    return [(-L/2, -w), (L*0.3, -w), (L/2, -w*0.3), (L/2 + w*0.6, 0), (L/2, w*0.3), (L*0.3, w), (-L/2, w)]


def hidden_pastelka(x, y, r=13, rot=-25, g=None):
    """one of the 10 crayons hidden in the issue: a white halo and a black line round it, so it reads on any ground.
    r is about half its length"""
    g = P.CRAYON_RED if g is None else g
    with T(x, y, 1.0, rot=rot):
        o = _crayon_out(r)
        stroke(o, LINE*4.4, closed=True, g=0.0, taper=False)
        stroke(o, LINE*2.8, closed=True, g=1.0, taper=False)
        fill(o, g)
        w = r*0.38; L = r*1.6
        fill([(-L*0.3, -w), (L*0.15, -w), (L*0.15, w), (-L*0.3, w)], 1.0)
        for xx in (-L*0.2, L*0.05): stroke([(xx, -w*0.9), (xx, w*0.9)], LINE*0.5, g=0.0, taper=False)
        stroke(o, LINE*0.5, closed=True, g=0.0, taper=False)


def paper_bag(x, y, s=1.0, carrots=True, rot=0):
    """Hanka's paper bag with carrot sticks (it rustles: šust šust)"""
    with T(x, y, s, rot=rot):
        if carrots:
            for i, (dx, a) in enumerate(((-4, -12), (0, 4), (4, 16))):
                with T(dx, 14, 1.0, rot=a):
                    shape([(-1.6, 0), (1.6, 0), (1.4, 10), (-1.4, 10)], P.CARROT, LINE*0.5)
        bag = [(-8, 0), (8, 0), (8.5, 16), (6, 18), (3, 15.5), (0, 18), (-3, 15.5), (-6, 18), (-8.5, 16)]
        form(bag, P.PAPER_BAG, w=LINE*0.8, sdx=-1, sdy=0, sh=0.1)
        stroke([(-6, 3), (-5.5, 13)], LINE*0.3, g=0.4); stroke([(3, 2), (4, 12)], LINE*0.3, g=0.4)


def box_holes(x, y, s=1.0, open_=False, label=False):
    """táta's big cardboard box with air holes; (x, y) = the middle of its bottom"""
    with T(x, y, s):
        form([(-26, 0), (26, 0), (26, 32), (-26, 32)], P.BOX, sdx=2, sdy=0, sh=0.12)
        shape([(26, 0), (36, 6), (36, 38), (26, 32)], P.BOX*0.9 if lib.MODE == "bw" else P.BOX, LINE)
        shape([(-26, 32), (26, 32), (36, 38), (-16, 38)], P.BOX, LINE)
        if open_:
            shape([(-26, 32), (-34, 46), (16, 50), (26, 32)], P.BOX, LINE*0.8)
        else:
            stroke([(-21, 35), (31, 35)], LINE*1.6, g=0.6)
        for i in range(3):
            for j in range(2):
                shape(ell(-16 + i*16, 12 + j*10, 2, 2, 10), 0.15, LINE*0.4)
        for j in range(3): shape(ell(31, 14 + j*8, 1.3, 1.8, 10), 0.15, LINE*0.3)
        if label:
            stroke([(-8, 26), (0, 30), (8, 26)], LINE*0.6)


def diely(x, y, s=1.0):
    """the parts of the new hutch táta made in his workshop: planks, a mesh panel, a little ramp with slats"""
    with T(x, y, s):
        for i in range(4):
            shape([(-40 + i*2, i*5), (30 + i*2, i*5), (30 + i*2, i*5 + 4.5), (-40 + i*2, i*5 + 4.5)], P.NEW_WOOD, LINE*0.6)
        shape([(-30, 22), (10, 22), (10, 46), (-30, 46)], 0.95, LINE*0.7)
        C.saveState(); C.clipPath(poly([(-30, 22), (10, 22), (10, 46), (-30, 46)]), stroke=0, fill=0)
        for k in range(-30, 11, 4): stroke([(k, 22), (k, 46)], LINE*0.35, g=0.5)
        for k in range(22, 47, 4): stroke([(-30, k), (10, k)], LINE*0.35, g=0.5)
        C.restoreState()
        with T(24, 22, 1.0, rot=25):
            shape([(0, 0), (30, 0), (30, 7), (0, 7)], P.NEW_WOOD, LINE*0.6)
            for k in range(3, 30, 5): stroke([(k, 7), (k, 9)], LINE*1.0, g=P.SHELF)


def kotec(x, y, s=1.0, open_=True, latch="broken", shavings=False, misa=False, sisa=False, hay=True):
    """the school's outdoor guinea-pig hutch: a wooden box on legs, a mesh run, a closed sleeping room with a round
    door hole, a sloping roof. open_: the side door hangs open. latch: "broken" (snapped off, hanging) or "ok".
    (x, y) = the ground"""
    with T(x, y, s):
        for lx in (-38, 34): sh_([(lx, 0), (lx + 4, 0), (lx + 4, 12), (lx, 12)], P.KRMELEC)
        sh_([(-40, 12), (40, 12), (40, 46), (-40, 46)], P.SHELF)
        fill([(-34, 15), (6, 15), (6, 43), (-34, 43)], 0.25)
        if hay:
            fill(bez((-34, 15), (-30, 23), (-16, 24), (-8, 15)), P.HAY)
            for k in range(6): stroke([(-32 + k*4, 16), (-30 + k*4, 21)], LINE*0.4, g=P.STRAW_DARK)
        if shavings:
            hobliny(-12, 18, 0.55, 3, seed=9)
        if misa: morce(-24, 15, 0.42, who="misa")
        if sisa: morce(-6, 15, 0.42, who="sisa", flip=True)
        C.saveState(); C.clipPath(poly([(-34, 15), (6, 15), (6, 43), (-34, 43)]), stroke=0, fill=0)
        for k in range(-34, 7, 4): stroke([(k, 15), (k, 43)], LINE*0.35, g=0.75)
        for k in range(15, 44, 4): stroke([(-34, k), (6, k)], LINE*0.35, g=0.75)
        C.restoreState()
        stroke([(-34, 15), (6, 15), (6, 43), (-34, 43), (-34, 15)], LINE*0.8)
        sh_([(10, 15), (36, 15), (36, 43), (10, 43)], P.SHELF)
        shape(ell(23, 29, 6, 6, 20), 0.15, LINE*0.6)
        if open_:
            shape([(36, 15), (54, 8), (54, 36), (36, 43)], 0.9, LINE*0.8)
            for k in range(1, 5): stroke([(36 + k*3.6, 15 - k*1.4), (36 + k*3.6, 43 - k*1.4)], LINE*0.3, g=0.5)
        if latch == "broken":
            # the snapped wooden latch hangs by one nail
            with T(38, 30, 1.0, rot=-70):
                shape([(0, -1.6), (11, -1.6), (11, 1.6), (0, 1.6)], P.KRMELEC, LINE*0.6)
            dot(38, 30, 0.9, 0.2)
        else:
            shape([(30, 28), (44, 28), (44, 31), (30, 31)], P.KRMELEC, LINE*0.6)
        sh_([(-46, 44), (46, 44), (40, 58), (-40, 58)], P.KRMELEC)
        stroke([(-44, 47), (44, 47)], LINE*0.4, g=0.3)


def novy_kotec(x, y, s=1.0, names=True, misa=True, sisa=True, paint=True):
    """the new winter hutch from the field day: light new wood, a straw loft with a ramp, a proper latch the hedgehog
    can't open, the names painted on the board. (x, y) = the ground"""
    with T(x, y, s):
        for lx in (-50, 46): sh_([(lx, 0), (lx + 5, 0), (lx + 5, 14), (lx, 14)], P.NEW_WOOD)
        sh_([(-52, 14), (52, 14), (52, 64), (-52, 64)], P.NEW_WOOD)
        fill([(-46, 18), (8, 18), (8, 38), (-46, 38)], 0.3)
        fill(bez((-46, 18), (-40, 25), (-20, 26), (-10, 18)), P.HAY)
        if misa: morce(-30, 18, 0.5, who="misa")
        if sisa: morce(-6, 18, 0.45, who="sisa", flip=True)
        C.saveState(); C.clipPath(poly([(-46, 18), (8, 18), (8, 38), (-46, 38)]), stroke=0, fill=0)
        for k in range(-46, 9, 4): stroke([(k, 18), (k, 38)], LINE*0.35, g=0.8)
        C.restoreState()
        stroke([(-46, 18), (8, 18), (8, 38), (-46, 38), (-46, 18)], LINE*0.8)
        # the loft with straw, and a ramp up to it
        sh_([(-46, 42), (8, 42), (8, 60), (-46, 60)], P.NEW_WOOD)
        fill([(-42, 44), (4, 44), (4, 52), (-42, 52)], P.STRAW)
        for k in range(10): stroke([(-40 + k*4.6, 45), (-38 + k*4.6, 51)], LINE*0.4, g=P.STRAW_DARK)
        with T(-6, 20, 1.0, rot=38):
            shape([(0, -2.5), (26, -2.5), (26, 2.5), (0, 2.5)], P.NEW_WOOD, LINE*0.6)
            for k in range(3, 26, 5): stroke([(k, 2.5), (k, 4)], LINE*0.9, g=P.SHELF)
        sh_([(12, 18), (48, 18), (48, 60), (12, 60)], P.NEW_WOOD)
        shape(ell(30, 32, 7, 7, 20), 0.15, LINE*0.6)
        shape([(40, 40), (54, 40), (54, 44), (40, 44)], P.SHELF, LINE*0.6)
        shape([(44, 38), (47, 38), (47, 46), (44, 46)], 0.5, LINE*0.5)
        sh_([(-58, 62), (58, 62), (52, 80), (-52, 80)], P.SHED_ROOF)
        if names:
            shape([(-38, 64.5), (40, 64.5), (40, 61), (-38, 61)], P.NEW_WOOD, 0)
            hand_text(-40, 64, 40, "MÍŠA", "SHB", 9, g=P.NAME_PAINT)
            hand_text(0, 64, 40, "ŠIŠA", "SHB", 9, g=P.NAME_PAINT)
            if paint:
                for i, (fx, fy) in enumerate(((-44, 70), (-30, 74), (34, 72), (46, 68))):
                    star(fx, fy, 2.6, P.STREAMERS[i % 4], LINE*0.4)


# ------------------------------------------------------------------ notes
def torn_note(x, y, w, h, lines=(), size=10, rot=0, torn=True, wet=False, seed=4):
    """a note on squared paper, centred on (x, y). torn: the left part is missing (only the end of each line is
    left); wet: blotches from a night outside"""
    r = random.Random(seed)
    with T(x, y, 1.0, rot=rot):
        if torn:
            left = [(-w/2 + r.uniform(-4, 5) + (6 if i % 2 else 0), h/2 - i/10*h) for i in range(11)]
            o = [(w/2, h/2), (w/2, -h/2)] + left[::-1]
        else:
            o = [(-w/2, -h/2), (w/2, -h/2), (w/2, h/2), (-w/2, h/2)]
        fill([(px + 1.5, py - 1.5) for px, py in o], 0.0, 0.15)
        shape(o, P.SLIP, LINE*0.6)
        C.saveState(); C.clipPath(poly(o), stroke=0, fill=0)
        for k in range(int(-w/2), int(w/2), 6): stroke([(k, -h/2), (k, h/2)], LINE*0.2, g=0.82)
        for k in range(int(-h/2), int(h/2), 6): stroke([(-w/2, k), (w/2, k)], LINE*0.2, g=0.82)
        if wet:
            for _ in range(3):
                fill(ell(r.uniform(-w*0.3, w*0.3), r.uniform(-h*0.3, h*0.3), r.uniform(5, 10), r.uniform(4, 8), 16), 0.6, 0.25)
        C.restoreState()
        n = len(lines)
        for i, ln in enumerate(lines):
            yy = h/2 - (h - n*size*1.3)/2 - (i + 1)*size*1.3 + size*0.25
            hand_text(-w/2 + 6, yy, w - 12, ln, "SH", size, align="right" if torn else "center", g=P.CIPHER_INK)


# ------------------------------------------------------------------ the van
def vito(x, y, s=1.0, flip=False, back_open=False, box=False):
    """the family's dark red van (a Mercedes Vito), side view, front to the right; (x, y) = the ground under its
    middle. back_open: the tailgate up; box: táta's box in the back"""
    with T(x, y, s, flip):
        body = [(-78, 12), (-78, 66)] + bez((-78, 66), (-78, 70), (-75, 72), (-70, 72)) + [(34, 72)] + \
               bez((34, 72), (42, 72), (52, 52), (56, 44)) + bez((56, 44), (66, 42), (78, 40), (80, 32)) + [(80, 14)] + \
               bez((80, 14), (80, 12), (78, 11), (76, 11)) + [(-76, 11)]
        form(body, P.VITO, sdx=2, sdy=0, sh=0.1)
        win = [(-72, 44), (30, 44), (30, 66), (-72, 66)]
        shape([(-72, 46), (-40, 46), (-40, 66), (-72, 66)], P.WINDOW_GLASS, LINE*0.7)
        shape([(-36, 46), (-2, 46), (-2, 66), (-36, 66)], P.WINDOW_GLASS, LINE*0.7)
        shape([(2, 46), (30, 46), (30, 66), (2, 66)], P.WINDOW_GLASS, LINE*0.7)
        shape([(34, 46), (50, 46)] + bez((50, 46), (46, 56), (40, 66), (35, 68)) + [(34, 46)], P.WINDOW_GLASS, LINE*0.7)
        stroke([(32, 14), (32, 70)], LINE*0.6); stroke([(-2, 14), (-2, 44)], LINE*0.5)
        stroke([(-38, 40), (-30, 40)], LINE*1.0); stroke([(24, 40), (28, 40)], LINE*1.0)
        stroke([(-78, 26), (80, 26)], LINE*0.4, g=0.2)
        shape([(70, 34), (79, 33), (79, 37), (70, 38)], 0.95, LINE*0.5)
        shape([(-78, 30), (-74, 30), (-74, 40), (-78, 40)], P.CRAYON_RED, LINE*0.5)
        shape([(76, 14), (82, 14), (82, 20), (76, 20)], 0.3, LINE*0.5)
        if back_open:
            shape([(-78, 70), (-106, 92), (-104, 96), (-75, 74)], P.VITO, LINE)
            fill([(-77, 14), (-72, 14), (-72, 64), (-77, 64)], 0.15)
            if box: box_holes(-90, 16, 0.55)
        for wx in (-52, 50):
            shape(ell(wx, 12, 12, 12, 28), 0.12, LINE)
            shape(ell(wx, 12, 6, 6, 18), 0.7, LINE*0.6)
            fill(ell(wx, 12, 14, 14, 28, 0, 180), P.VITO_DARK, 0.0)


# ------------------------------------------------------------------ the phone (video call)
def video_call(x, y, w=70, h=124, who=("babi", "deda"), rot=0):
    """a phone held up for a video call with babička and děda (their faces fill the screen); (x, y) = its middle"""
    with T(x, y, 1.0, rot=rot):
        shape(rrect(-w/2, -h/2, w, h, 8), P.PHONE, LINE)
        scr = rrect(-w/2 + 4, -h/2 + 10, w - 8, h - 20, 4)
        fill(scr, P.SPRING_SKY)
        C.saveState(); C.clipPath(poly(scr), stroke=0, fill=0)
        fill([(-w, -h/2 + 10), (w, -h/2 + 10), (w, -h*0.05), (-w, -h*0.05)], P.KITCHEN_WALL)
        k = h/124
        if "babi" in who: babicka(-w*0.2, -h*0.62, 0.72*k, shadow=False, mood="happy", right="wave", look=(0.5, 0))
        if "deda" in who: deda(w*0.22, -h*0.75, 0.68*k, shadow=False, mood="happy", look=(-0.5, 0))
        C.restoreState()
        stroke(scr, LINE*0.6, closed=True)
        shape(ell(0, -h/2 + 5, 3, 3, 12), 0.35, LINE*0.4)
        shape(rrect(w/2 - 22, h/2 - 32, 16, 20, 2), P.SKIN, LINE*0.5)   # her own little picture in the corner


# ------------------------------------------------------------------ the forest school
def hillside(p, y0=0.42, y1=0.22, seed=1, far=True, sky_g=None):
    """the school meadow on a slope, high on the left, low on the right; returns gy(f): the ground at panel
    fraction f"""
    sky(p, P.SPRING_SKY if sky_g is None else sky_g)
    a, b = p.Y(y0), p.Y(y1)
    gy = lambda f: a + (b - a)*f + math.sin(f*math.pi)*p.h*0.03
    if far:
        ty = max(a, b) + p.h*0.12
        far_trees(p, ty, seed)
        fill([(p.x - 5, p.y - 5), (p.x + p.w + 5, p.y - 5), (p.x + p.w + 5, ty), (p.x - 5, ty)], P.FAR_FIELD)
        s_([(p.x - 5, ty), (p.x + p.w + 5, ty)], BG*0.6)
    pts = [(p.x - 5, p.y - 5)] + [(p.x + p.w*i/20, gy(i/20)) for i in range(21)] + [(p.x + p.w + 5, p.y - 5)]
    fill(pts, P.SPRING_GRASS)
    s_([(p.x + p.w*i/20, gy(i/20)) for i in range(21)], BG)
    r = random.Random(seed)
    for _ in range(int(p.w/22)):
        f = r.random(); yy = r.uniform(p.y + 4, gy(f) - 4)
        xx = p.x + p.w*f
        for k in (-2, 0, 2): stroke([(xx + k, yy), (xx + k*1.6, yy + 4)], BG*0.5, g=0.4)
    return gy


def snowdrops(x, y, n=3, seed=1, s=1.0):
    r = random.Random(seed)
    for i in range(n):
        xx = x + i*5*s + r.uniform(-1, 1); hh = r.uniform(8, 12)*s
        stroke(bez((xx, y), (xx, y + hh*0.5), (xx + 1, y + hh), (xx + 2.5, y + hh*0.9)), LINE*0.6, g=P.GRASS)
        shape(ell(xx + 2.8, y + hh*0.75, 1.4*s, 2.2*s, 10), P.SNOWDROP, LINE*0.4)


def sapling(x, y, s=1.0, seed=2):
    """a young tree planted by the kids: a thin trunk tied to a stake, bare twigs with buds"""
    r = random.Random(seed)
    with T(x, y, s):
        stroke([(5, 0), (5, 40)], LINE*2.2, g=0.0); stroke([(5, 0), (5, 40)], LINE*1.2, g=P.KRMELEC)
        stroke(bez((0, 0), (1, 20), (-1, 40), (0, 60)), LINE*1.6, g=P.BARK)
        stroke([(0, 30), (5, 31)], LINE*0.8, g=0.3)
        for i in range(7):
            yy = r.uniform(32, 58); sx = r.choice((-1, 1)); L = r.uniform(8, 14)
            stroke(bez((0, yy), (sx*L*0.4, yy + 3), (sx*L*0.7, yy + 6), (sx*L, yy + 9)), LINE*0.8, g=P.BARK)
            dot(sx*L, yy + 9, 1.1, P.LEAF_LIGHT)


def kadibudka(x, y, s=1.0):
    """the little wooden outhouse with a heart in the door"""
    with T(x, y, s):
        form([(-14, 0), (14, 0), (14, 44), (-14, 46)], P.PLANKS, w=BG, sdx=2, sdy=0)
        for xx in (-7, 0, 7): stroke([(xx, 1), (xx, 44)], LINE*0.4, g=0.45)
        shape([(-18, 44), (18, 41), (18, 46), (-18, 50)], P.SHED_ROOF, LINE*0.8)
        from village import heart_pts
        shape(heart_pts(0, 34, 3.4), 0.1, LINE*0.5)
        dot(9, 22, 1, 0.2)


def klesti(x, y, s=1.0, nest=False, hay=True, seed=4, note=False):
    """the brushwood pile at the bottom of the meadow: a heap of branches over a few logs, a dark hollow at the
    front. nest: the hedgehog's nest of hay in the hollow; note: a scrap of paper caught in the hay"""
    r = random.Random(seed)
    with T(x, y, s):
        mass = bez((-66, 0), (-60, 44), (44, 54), (68, 0))
        fill(mass, P.BARK)
        hatch(mass, 2.2, 60, 0.4, 0.0, 0.5)
        for side in (-1, 1):
            for i in range(3):
                for j in range(2 - (i == 2)):
                    lx = side*(26 + j*13 + (i % 2)*6); ly = 6 + i*10
                    shape(ell(lx, ly, 6.2, 5.6, 16), P.LOG_END, LINE*0.6)
                    stroke(ell(lx, ly, 3, 2.7, 12), LINE*0.3, g=0.5)
        hol = bez((-15, 0), (-15, 20), (17, 20), (17, 0))
        fill(hol, 0.08)
        if nest and hay:
            fill(bez((-13, 0), (-11, 10), (13, 10), (15, 0)), P.HAY)
            for k in range(8): stroke([(-11 + k*3, 1), (-9 + k*3, 8)], LINE*0.5, g=P.STRAW_DARK)
            if note: torn_note(5, 10, 13, 10, rot=-20, seed=2)
        for _ in range(34):
            x0 = r.uniform(-62, 56); y0 = r.uniform(10, 46 - abs(x0)*0.45); L = r.uniform(24, 46); a = r.uniform(-30, 30)
            if -18 < x0 < 20 and y0 < 22: continue
            x1 = x0 + math.cos(math.radians(a))*L; y1 = y0 + math.sin(math.radians(a))*L*0.5
            stroke([(x0, y0), (x1, y1)], LINE*1.4, g=P.BARK*0.6 if lib.MODE == "bw" else P.BARK)
            mx, my = (x0 + x1)/2, (y0 + y1)/2
            stroke([(mx, my), (mx + r.uniform(-6, 6), my + r.uniform(3, 9))], LINE*0.8, g=0.15)
            stroke([(x1, y1), (x1 + r.uniform(2, 6)*(1 if a > 0 else -1), y1 + r.uniform(1, 5))], LINE*0.6, g=0.15)
        stroke(mass, BG)


def yurt(x, y, s=1.0, door=True, smoke=False, door_open=False):
    """one of the school's two yurts: a round felt wall with a lattice, a low cone roof, a painted door.
    (x, y) = the middle of its foot"""
    with T(x, y, s):
        wall = bez((-60, 3), (-30, -3), (30, -3), (60, 3)) + [(60, 46)] + bez((60, 46), (30, 40), (-30, 40), (-60, 46))
        fill(wall, P.YURT)
        C.saveState(); C.clipPath(poly(wall), stroke=0, fill=0)
        for k in range(-80, 81, 9):
            stroke([(k, -4), (k + 48, 48)], LINE*0.3, g=0.7); stroke([(k, -4), (k - 48, 48)], LINE*0.3, g=0.7)
        C.restoreState()
        offset_shadow(wall, 6, 0, 0.1)
        stroke(wall, BG, closed=True)
        stroke(bez((-60, 30), (-30, 24), (30, 24), (60, 30)), LINE*1.6, g=P.YURT_BAND)
        roof = bez((-66, 46), (-30, 39), (30, 39), (66, 46)) + [(14, 80)] + bez((14, 80), (6, 82), (-6, 82), (-14, 80))
        form(roof, P.YURT_ROOF, w=BG, sdx=4, sdy=0, sh=0.1)
        for k in (-44, -22, 0, 22, 44): s_([(k, 41.5 if k else 39.5), (k*0.22, 80)], BG*0.4)
        shape(ell(0, 81, 14, 3, 20), P.YURT_BAND, BG)
        stroke([(36, 58), (38, 92)], LINE*3.2, g=0.0); stroke([(36, 58), (38, 92)], LINE*2.2, g=P.STOVE_IRON)
        if smoke:
            for i in range(3): stroke(bez((38 + i*3, 94 + i*8), (34 + i*4, 100 + i*8), (44 + i*3, 104 + i*8), (40 + i*4, 110 + i*8)), LINE*0.6, g=0.6)
        if door:
            d = [(-10, -2.5), (10, -2.5), (10, 30), (-10, 30)]
            if door_open:
                fill(d, 0.12)
                shape([(10, -2.5), (19, 0), (19, 28), (10, 30)], P.YURT_DOOR, LINE*0.7)
            else:
                form(d, P.YURT_DOOR, sdx=1.2, sdy=0, sh=0.1)
                for xx in (-3.5, 3.5): stroke([(xx, 1), (xx, 27)], LINE*0.4, g=0.3)
                shape(ell(0, 22, 4, 3, 14), P.YURT_BAND, LINE*0.5)
                dot(7, 13, 1.0, 0.85)
            shape([(-12, 30), (12, 30), (12, 33), (-12, 33)], P.YURT_BAND, LINE*0.6)


def srub(x, y, s=1.0, door_open=False, lock=True, window_light=False):
    """the little log building between the yurts: a cloakroom and the kumbál (pan Karel's storeroom and workshop);
    (x, y) = the middle of its foot"""
    with T(x, y, s):
        w, h = 46, 50
        fill([(-w, 0), (w, 0), (w, h), (-w, h)], P.LOG)
        for i in range(10):
            yy = i*5
            stroke([(-w, yy + 4.6), (w, yy + 4.6)], LINE*0.5, g=0.3)
            for sx in (-1, 1): shape(ell(sx*w, yy + 2.5, 2.8, 2.6, 10), P.LOG_END, LINE*0.4)
        offset_shadow([(-w, 0), (w, 0), (w, h), (-w, h)], 5, 0, 0.1)
        stroke([(-w, 0), (w, 0), (w, h), (-w, h)], BG, closed=True)
        roof = [(-w - 8, h - 2), (w + 8, h - 2), (0, h + 26)]
        form(roof, P.SHED_ROOF, w=BG, sdx=3, sdy=0)
        shape([(-6, h + 6), (6, h + 6), (6, h + 14), (-6, h + 14)], P.LOG, LINE*0.5)
        d = [(-12, 0), (12, 0), (12, 38), (-12, 38)]
        if door_open:
            fill(d, 0.15)
            shape([(12, 0), (20, 3), (20, 36), (12, 38)], P.SHED_DOOR, LINE*0.7)
        else:
            form(d, P.SHED_DOOR, sdx=1.4, sdy=0, sh=0.1)
            for xx in (-6, 0, 6): stroke([(xx, 1), (xx, 37)], LINE*0.4, g=0.35)
            stroke([(-12, 8), (12, 30)], LINE*0.9, g=0.3)
            if lock:
                shape(rrect(7, 15, 5, 5, 1), 0.3, LINE*0.5)
                stroke(ell(9.5, 20, 1.8, 2.2, 10, 0, 180), LINE*0.6)
        shape([(22, 22), (38, 22), (38, 36), (22, 36)], P.LANTERN_GLOW if window_light else P.WINDOW_GLASS, LINE*0.7)
        stroke([(30, 22), (30, 36)], LINE*0.5); stroke([(22, 29), (38, 29)], LINE*0.5)
        shape([(-40, 20), (-22, 20), (-22, 36), (-40, 36)], P.WINDOW_GLASS, LINE*0.7)


def skola(x, y, s=1.0, door_open=False, smoke=True, lock=True):
    """the whole school: yurt, log building, yurt; (x, y) = the middle of the log building's foot. ~330 wide"""
    yurt(x - 110*s, y + 2*s, s, smoke=smoke)
    yurt(x + 110*s, y + 2*s, s)
    with T(x, y, s):
        for sx in (-1, 1):
            shape([(sx*44, 0), (sx*58, 0), (sx*58, 30), (sx*44, 30)], P.LOG, BG)
            shape([(sx*42, 30), (sx*62, 28), (sx*62, 33), (sx*42, 35)], P.SHED_ROOF, BG)
    srub(x, y, s, door_open=door_open, lock=lock)


def school_garden(p, y0=0.5, y1=0.3, seed=1, school_x=0.5, school_s=0.7, hutch_x=None, hutch_s=0.8, pile_x=None,
                  pile_s=0.8, budka_x=None, saplings=(), hutch_kw=None, pile_kw=None, door_open=False, far=True, drops=True):
    """the meadow with the school high up and the hutch and the brushwood further down. Returns gy"""
    gy = hillside(p, y0, y1, seed, far=far)
    if school_x is not None:
        f = school_x; skola(p.X(f), gy(f) + p.h*0.02, school_s, door_open=door_open)
    if budka_x is not None: kadibudka(p.X(budka_x), gy(budka_x) - 2, 0.9*school_s/0.7)
    for i, (f, ss) in enumerate(saplings): sapling(p.X(f), gy(f) - 3, ss, seed + i)
    if pile_x is not None: klesti(p.X(pile_x), gy(pile_x) - 6, pile_s, **(pile_kw or {}))
    if hutch_x is not None: kotec(p.X(hutch_x), gy(hutch_x) - 6, hutch_s, **(hutch_kw or {}))
    if drops:
        r = random.Random(seed)
        for _ in range(3):
            f = r.uniform(0.05, 0.95)
            snowdrops(p.X(f), gy(f) - r.uniform(6, 14), 3, seed + 7)
    return gy


# ------------------------------------------------------------------ inside
def yurt_inside(p, floor=0.1, stove_x=0.85, seed=1):
    """inside a yurt: the lattice wall all round, the roof poles meeting at the crown, a wood stove, a plank floor.
    Returns the floor line"""
    fill([(p.x - 5, p.y - 5), (p.x + p.w + 5, p.y - 5), (p.x + p.w + 5, p.y + p.h + 5), (p.x - 5, p.y + p.h + 5)], P.YURT)
    fy = p.Y(floor); top = p.Y(0.62)
    C.saveState(); C.clipPath(poly([(p.x, fy), (p.x + p.w, fy), (p.x + p.w, top), (p.x, top)]), stroke=0, fill=0)
    for k in range(int(p.x) - 200, int(p.x + p.w) + 200, 16):
        stroke([(k, fy), (k + (top - fy), top)], LINE*0.7, g=P.YURT_BAND)
        stroke([(k, fy), (k - (top - fy), top)], LINE*0.7, g=P.YURT_BAND)
    C.restoreState()
    stroke([(p.x, top), (p.x + p.w, top)], LINE*1.4, g=P.YURT_BAND)
    cx = p.X(0.5); cyy = p.y + p.h + 40
    for i in range(-10, 11):
        stroke([(cx + i*p.w/12, top), (cx + i*8, cyy)], LINE*0.9, g=P.YURT_BAND)
    shape([(p.x - 5, p.y - 5), (p.x + p.w + 5, p.y - 5), (p.x + p.w + 5, fy), (p.x - 5, fy)], P.FLOOR, BG)
    for k in range(1, 8): s_([(p.x + p.w*k/8, p.y), (p.x + p.w*k/8, fy)], BG*0.4)
    if stove_x is not None:
        sx = p.X(stove_x)
        sh_(rrect(sx - 22, fy, 44, 40, 4), P.STOVE_IRON)
        shape(rrect(sx - 12, fy + 10, 24, 16, 3), P.LANTERN_GLOW, LINE*0.6)
        for k in range(3): stroke([(sx - 9 + k*9, fy + 12), (sx - 9 + k*9, fy + 24)], LINE*0.5, g=0.2)
        stroke([(sx, fy + 40), (sx, p.y + p.h + 10)], LINE*5, g=0.0); stroke([(sx, fy + 40), (sx, p.y + p.h + 10)], LINE*3.6, g=P.STOVE_IRON)
    return fy


def kumbal(p, floor=0.1, seed=1, window=True, hook=True, bench=True):
    """pan Karel's kumbál in the log building: plank walls, a window, tools on the wall, a workbench with shavings,
    a straw bale, an empty hook where his hat hangs. Returns the floor line"""
    planks(p, P.PLANKS, 26, seed, knots=True)
    fy = p.Y(floor)
    shape([(p.x - 5, p.y - 5), (p.x + p.w + 5, p.y - 5), (p.x + p.w + 5, fy), (p.x - 5, fy)], P.FLOOR, BG)
    if window:
        x0, x1, y0, y1 = p.X(0.06), p.X(0.22), p.Y(0.55), p.Y(0.85)
        shape([(x0 - 4, y0 - 4), (x1 + 4, y0 - 4), (x1 + 4, y1 + 4), (x0 - 4, y1 + 4)], P.DOOR_FRAME, BG)
        shape([(x0, y0), (x1, y0), (x1, y1), (x0, y1)], P.SPRING_SKY, BG)
        s_([((x0 + x1)/2, y0), ((x0 + x1)/2, y1)], BG*1.4, g=1.0); s_([(x0, (y0 + y1)/2), (x1, (y0 + y1)/2)], BG*1.4, g=1.0)
    sh_([(p.X(0.3), p.Y(0.82)), (p.X(0.62), p.Y(0.82)), (p.X(0.62), p.Y(0.84)), (p.X(0.3), p.Y(0.84))], P.SHELF)
    saw(p.X(0.36), p.Y(0.62), 0.9)
    with T(p.X(0.5), p.Y(0.6), 1.0, rot=90): rake(0, 0, 0.6)
    if hook:
        stroke([(p.X(0.72), p.Y(0.75)), (p.X(0.72) + 6, p.Y(0.75)), (p.X(0.72) + 6, p.Y(0.75) + 5)], LINE*1.2, g=0.3)
    if bench:
        bx0, bx1, by = p.X(0.55), p.X(0.98), fy + 52
        sh_([(bx0, by), (bx1, by), (bx1, by + 7), (bx0, by + 7)], P.SHELF)
        for lx in (bx0 + 6, bx1 - 12): sh_([(lx, fy), (lx + 6, fy), (lx + 6, by), (lx, by)], P.SHELF)
        hobliny((bx0 + bx1)/2, by + 9, 0.9, 6, seed + 1)
        hobliny(bx0 + 30, fy + 3, 0.8, 4, seed + 2)
    return fy


def home(p, floor=0.1, evening=False, seed=1):
    """the family's kitchen at home: a big window, a long table, the girls' drawings on the wall. Returns the floor"""
    fill([(p.x - 5, p.y - 5), (p.x + p.w + 5, p.y - 5), (p.x + p.w + 5, p.y + p.h + 5), (p.x - 5, p.y + p.h + 5)], P.KITCHEN_WALL)
    fy = p.Y(floor)
    x0, x1, y0, y1 = p.X(0.6), p.X(0.92), p.Y(0.42), p.Y(0.9)
    shape([(x0 - 5, y0 - 5), (x1 + 5, y0 - 5), (x1 + 5, y1 + 5), (x0 - 5, y1 + 5)], 0.98, BG)
    shape([(x0, y0), (x1, y0), (x1, y1), (x0, y1)], P.WINTER_NIGHT if evening else P.SPRING_SKY, BG)
    if not evening:
        fill(bez((x0, y0), (x0 + (x1 - x0)*0.3, y0 + (y1 - y0)*0.4), (x0 + (x1 - x0)*0.7, y0 + (y1 - y0)*0.3), (x1, y0 + (y1 - y0)*0.2)) +
             [(x1, y0)], P.TREE_CROWN)
    s_([((x0 + x1)/2, y0), ((x0 + x1)/2, y1)], BG*1.6, g=1.0)
    for i, (fx, fy_, rr) in enumerate(((0.1, 0.7, 4), (0.26, 0.74, -3), (0.42, 0.68, 2))):
        kids_drawing(p.X(fx), p.Y(fy_), 40, 30, rr)
    shape([(p.x - 5, p.y - 5), (p.x + p.w + 5, p.y - 5), (p.x + p.w + 5, fy), (p.x - 5, fy)], P.KITCHEN_FLOOR, BG)
    if evening:
        fill([(p.x, p.y), (p.x + p.w, p.y), (p.x + p.w, p.y + p.h), (p.x, p.y + p.h)], 0.0, 0.18)
    return fy


def table(p, y=0.3, x0=0.04, x1=0.96):
    shape([(p.X(x0), p.Y(y)), (p.X(x1), p.Y(y)), (p.X(x1), p.Y(y + 0.035)), (p.X(x0), p.Y(y + 0.035))], P.TABLE, BG)
