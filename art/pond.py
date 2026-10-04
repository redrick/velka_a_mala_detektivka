"""Art for issue 3 "Mapa ke starému rybníku": the old pond with the mill, Věrka as she is today,
the fisherman, the badger, ducks, clues in the mud and the treasure from the tin."""
import math, random
import lib
from lib import ell, bez, rrect, resample
import palette as P
from style3 import *
from style3 import C, _SC, draw_arm, draw_legs, head_outline, face, notch, hand, arm_pts
from chars3 import Person, _neck, star
from scenes3 import BG, s_, sh_, cloud, tufts
from attic import young, _torn_edge
from letter import hand_text


# ------------------------------------------------------------------ Věrka today (paní od mlýna)
VERKA = dict(H=114, hr=10.2, hy=103, sh_y=88.5, sh_w=11, hip=52, knee=28, ankle=5, leg_w=(6.2, 5.0),
             arm_w=(6.0, 5.4), up=17.5, fo=16)


def walking_stick(x, y, length=62, rot=0):
    """stick with a round rubber tip; (x, y) = the tip on the ground"""
    with T(x, y, 1.0, rot=rot):
        tube([(0, 2), (0, length)], 2.4, 2.4, P.WALKING_STICK, sh=0)
        stroke(bez((0, length), (0, length + 7), (8, length + 8), (9, length + 2)), LINE*2.6)
        stroke(bez((0, length), (0, length + 7), (8, length + 8), (9, length + 2)), LINE*1.2, g=P.WALKING_STICK)
        shape(rrect(-2.2, -0.5, 4.4, 3.4, 1.4), 0.2, LINE*0.7)


def verka_old(x, y, s=1.0, flip=False, left="down", right="down", mood="happy", look=(0, 0), item=None,
              shadow=True, legs="stand", hat=True, stick=True):
    """Věrka about 60 years after the club: long grey plait, wide straw hat, teal coat, walking stick"""
    k = Person(**VERKA)
    if shadow: cast_shadow(x, y, 17*s, 2.8*s)
    with T(x, y, s, flip):
        r = k.hr; cy = k.hy
        draw_legs(k, legs, P.STOCKINGS, boots=P.BABI_SHOES, boot_top=k.ankle + 3)
        if stick and left == "down":
            walking_stick(-k.sh_w - 9, 0, 58, rot=-3)
        draw_arm(k, -1, left, P.VERKA_COAT)
        coat = bez((-5, k.sh_y + 2.5), (-9, k.sh_y + 2.2), (-k.sh_w - 1.2, k.sh_y + 0.5), (-k.sh_w - 1.8, k.sh_y - 4)) + \
               bez((-k.sh_w - 1.8, k.sh_y - 4), (-14, 64), (-16, 46), (-17.5, 26)) + \
               bez((-17.5, 26), (-6, 24), (6, 24), (17.5, 26)) + \
               bez((17.5, 26), (16, 46), (14, 64), (k.sh_w + 1.8, k.sh_y - 4)) + \
               bez((k.sh_w + 1.8, k.sh_y - 4), (k.sh_w + 1.2, k.sh_y + 0.5), (9, k.sh_y + 2.2), (5, k.sh_y + 2.5))
        form(coat, P.VERKA_COAT, sdx=-2.4, sdy=1.2)
        stroke([(1.5, k.sh_y - 2), (2.5, 25)], LINE*0.8)
        for by in (78, 68, 58, 48, 38): shape(ell(-1.2, by, 1.0, 1.0, 12), 0.9, LINE*0.6)
        for sx in (-1, 1):
            pk = [(sx*6, 44), (sx*13.5, 44), (sx*14, 38), (sx*6.3, 38)]
            stroke(pk, LINE*0.7, closed=True)
        shape([(-15, 55), (15, 55), (15.2, 58.5), (-15.2, 58.5)], P.VERKA_COAT, LINE*0.8)
        shape(rrect(-2.5, 54.5, 5, 4.5, 0.8), P.BRASS, LINE*0.6)
        # scarf
        sc = bez((-7, k.sh_y + 2.6), (-4, k.sh_y - 2), (4, k.sh_y - 2), (7, k.sh_y + 2.6)) + \
             bez((7, k.sh_y + 2.6), (3, k.sh_y + 4.5), (-3, k.sh_y + 4.5), (-7, k.sh_y + 2.6))
        shape(sc, P.VERKA_SCARF, LINE*0.8)
        shape([(2, k.sh_y - 1), (6, k.sh_y - 1.5), (7.5, k.sh_y - 14), (3.5, k.sh_y - 13)], P.VERKA_SCARF, LINE*0.8)
        h, fa = draw_arm(k, 1, right, P.VERKA_COAT)
        if item: item(*h)
        _neck(k, 2.6)
        shape(head_outline(k), P.SKIN)
        face(0, cy, r, mood, look)
        for sx in (-1, 1):   # smile wrinkles
            stroke([(sx*r*0.6, cy - r*0.05), (sx*r*0.72, cy - r*0.12)], LINE*0.5)
            stroke(bez((sx*r*0.35, cy - r*0.52), (sx*r*0.42, cy - r*0.62), (sx*r*0.45, cy - r*0.7), (sx*r*0.42, cy - r*0.78)), LINE*0.4)
        # grey hair, parted, one long plait over the right shoulder (like her pigtails once)
        capp = bez((-r*1.02, cy + r*0.05), (-r*1.1, cy + r*1.2), (r*1.1, cy + r*1.2), (r*1.02, cy + r*0.05)) + \
               bez((r*1.02, cy + r*0.05), (r*0.8, cy + r*0.45), (r*0.45, cy + r*0.55), (0, cy + r*0.62)) + \
               bez((0, cy + r*0.62), (-r*0.45, cy + r*0.55), (-r*0.8, cy + r*0.45), (-r*1.02, cy + r*0.05))
        shape(capp, P.VERKA_OLD_HAIR)
        for i in range(7):
            yy = cy - r*0.1 - i*r*0.42
            shape(ell(r*0.95 + i*0.2 + (0.9 if i % 2 else -0.9), yy, r*0.2, r*0.32, 14, rot=35 if i % 2 else -35),
                  P.VERKA_OLD_HAIR, LINE*0.7)
        with T(r*0.95 + 7*0.2, cy - r*0.1 - 7*r*0.42 + 2, 1):
            for bx in (-1, 1): shape([(0, 0), (bx*3.4, 2), (bx*3.4, -2)], P.HAT_BAND, LINE*0.6)
        if hat:
            crown = bez((-r*0.85, cy + r*0.8), (-r*0.9, cy + r*1.8), (r*0.9, cy + r*1.8), (r*0.85, cy + r*0.8))
            shape(crown + [(-r*0.85, cy + r*0.8)], P.VERKA_HAT)
            shape([(-r*0.86, cy + r*0.8), (r*0.86, cy + r*0.8), (r*0.88, cy + r*1.08), (-r*0.88, cy + r*1.08)], P.HAT_BAND, LINE*0.7)
            brim = ell(0, cy + r*0.78, r*2.0, r*0.38, 36)
            shape(brim, P.VERKA_HAT)
            stroke(ell(0, cy + r*0.8, r*1.7, r*0.24, 30, 200, 340), LINE*0.4, g=0.5)


# ------------------------------------------------------------------ the fisherman (rybář)
RYBAR = dict(H=130, hr=11.2, hy=118, sh_y=102, sh_w=15, hip=58, knee=31, ankle=6, leg_w=(10, 8.5),
             arm_w=(7.4, 6.6), up=20, fo=18)


def big_boot(ax, s=1.0, g=P.WADERS):
    b = [(ax - 5.5, 16), (ax + 5.5, 16)] + bez((ax + 5.5, 16), (ax + 6, 6), (ax + 7, 3.5), (ax + 13, 3)) + \
        bez((ax + 13, 3), (ax + 14.5, 2.6), (ax + 14.5, 0), (ax + 12.5, 0)) + [(ax - 6, 0)] + \
        bez((ax - 6, 0), (ax - 6.8, 2), (ax - 6, 8), (ax - 5.5, 16))
    form(b, g, sh=0.12)
    stroke([(ax - 6.2, 2), (ax + 14, 2)], LINE*0.8)


def rybar(x, y, s=1.0, flip=False, left="down", right="down", mood="happy", look=(0, 0), item=None, shadow=True, rod=True,
          hat=True, glasses=False):
    """big friendly fisherman in chest waders with a bucket hat (issue 4: he is Franta; hat off shows
    a grey fringe, and he wears round glasses like little Franta did)"""
    k = Person(**RYBAR)
    if shadow: cast_shadow(x, y, 22*s, 3.2*s)
    with T(x, y, s, flip):
        r = k.hr; cy = k.hy
        for lx in (-6, 6):
            tube([(lx, k.hip), (lx*1.05, k.knee), (lx*1.1, 14)], k.leg_w[0], k.leg_w[1], P.WADERS)
        for lx in (-6.6, 6.6): big_boot(lx)
        draw_arm(k, -1, left, P.RYBAR_SHIRT)
        tors = bez((-6, k.sh_y + 3), (-11, k.sh_y + 2.6), (-k.sh_w - 1.3, k.sh_y + 0.5), (-k.sh_w - 2, k.sh_y - 5)) + \
               bez((-k.sh_w - 2, k.sh_y - 5), (-19, 80), (-19.5, 66), (-17, 54)) + [(17, 54)] + \
               bez((17, 54), (19.5, 66), (19, 80), (k.sh_w + 2, k.sh_y - 5)) + \
               bez((k.sh_w + 2, k.sh_y - 5), (k.sh_w + 1.3, k.sh_y + 0.5), (11, k.sh_y + 2.6), (6, k.sh_y + 3))
        form(tors, P.RYBAR_SHIRT, sdx=-2.4, sdy=1.2)
        bib = [(-12, 86), (12, 86)] + bez((12, 86), (15, 76), (18, 64), (17.5, 54)) + [(-17.5, 54)] + \
              bez((-17.5, 54), (-18, 64), (-15, 76), (-12, 86))
        form(bib, P.WADERS, sdx=-2, sdy=1)
        for sx in (-1, 1):
            stroke([(sx*10, 86), (sx*9, k.sh_y + 1.5)], LINE*2.4); stroke([(sx*10, 86), (sx*9, k.sh_y + 1.5)], LINE*1.1, g=P.WADERS)
            shape(ell(sx*10, 85.5, 1.4, 1.4, 12), P.BRASS, LINE*0.5)
        shape(rrect(-6, 70, 12, 9, 1.5), P.WADERS, LINE*0.7)
        h, fa = draw_arm(k, 1, right, P.RYBAR_SHIRT)
        if rod and right in ("hold", "front", "up"):
            stroke([(h[0] - 2, h[1] - 10), (h[0] + 30, h[1] + 70)], LINE*1.6, g=P.FISHING_ROD)
            shape(ell(h[0] + 1, h[1] - 4, 3, 3, 14), 0.7, LINE*0.6)
            hand(h[0], h[1], fa)
        if item: item(*h)
        _neck(k, 3.4)
        for sx in (-1, 1): shape(ell(sx*r*0.98, cy - r*0.05, r*0.2, r*0.3, 14), P.SKIN, LINE*0.8)
        shape(head_outline(k), P.SKIN)
        bd = bez((-r*0.95, cy - r*0.1), (-r*1.1, cy - r*1.3), (-r*0.4, cy - r*1.6), (0, cy - r*1.6)) + \
             bez((0, cy - r*1.6), (r*0.4, cy - r*1.6), (r*1.1, cy - r*1.3), (r*0.95, cy - r*0.1)) + \
             bez((r*0.95, cy - r*0.1), (r*0.6, cy - r*0.45), (r*0.3, cy - r*0.45), (0, cy - r*0.48)) + \
             bez((0, cy - r*0.48), (-r*0.3, cy - r*0.45), (-r*0.6, cy - r*0.45), (-r*0.95, cy - r*0.1))
        shape(bd, P.RYBAR_BEARD)
        face(0, cy, r, mood if mood not in ("grin",) else "happy", look)
        if mood in ("grin", "laugh", "surprised", "talk"):
            shape(ell(0, cy - r*0.68, r*0.14, r*0.1, 12), P.MOUTH, LINE*0.6)
        stroke(bez((-r*0.5, cy - r*0.48), (-r*0.2, cy - r*0.3), (r*0.2, cy - r*0.3), (r*0.5, cy - r*0.48)), LINE*1.6, g=P.RYBAR_BEARD)
        stroke(bez((-r*0.5, cy - r*0.48), (-r*0.2, cy - r*0.3), (r*0.2, cy - r*0.3), (r*0.5, cy - r*0.48)), LINE*0.6)
        if glasses:
            for sx in (-1, 1):
                stroke(ell(sx*r*0.4, cy - r*0.02, r*0.27, r*0.27, 24), LINE*0.8, closed=True)
            stroke([(-r*0.13, cy), (r*0.13, cy)], LINE*0.7)
        if not hat:
            for sx in (-1, 1):
                shape(bez((sx*r*0.98, cy + r*0.55), (sx*r*1.12, cy + r*0.15), (sx*r*1.05, cy - r*0.2), (sx*r*0.9, cy - r*0.3)) +
                      [(sx*r*0.8, cy + r*0.5)], P.GREY_HAIR, LINE*0.7)
            stroke(bez((-r*0.1, cy + r*0.98), (-r*0.3, cy + r*1.25), (r*0.05, cy + r*1.35), (r*0.15, cy + r*1.1)), LINE*0.6)
            return
        # bucket hat with a fishing fly
        hatc = bez((-r*0.95, cy + r*0.5), (-r*1.0, cy + r*1.45), (r*1.0, cy + r*1.45), (r*0.95, cy + r*0.5))
        shape(hatc + [(-r*0.95, cy + r*0.5)], P.RYBAR_HAT)
        brim = [(-r*1.4, cy + r*0.3), (r*1.4, cy + r*0.3), (r*1.0, cy + r*0.62), (-r*1.0, cy + r*0.62)]
        shape(brim, P.RYBAR_HAT)
        with T(r*0.55, cy + r*0.95, 1):
            shape([(0, 0), (4, 2.5), (1, -2.5)], P.DUCK_BILL, LINE*0.5)
            stroke([(0, 0), (-2, -3)], LINE*0.5)


# ------------------------------------------------------------------ animals
def badger(x, y, s=1.0, flip=False, mood="open", pose="walk"):
    """jezevec from the side (local length ~56, height ~24); pose: walk, peek (head out of a burrow)"""
    with T(x, y, s, flip):
        if pose == "walk":
            for lx in (-14, 10):
                tube([(lx - 2, 12), (lx - 3, 1)], 4.4, 4.0, P.BADGER_DARK, sh=0)
            C.saveState(); C.translate(0, 5)
            body = bez((-24, 10), (-28, 20), (-12, 26), (4, 25)) + bez((4, 25), (14, 24), (20, 20), (22, 13)) + \
                   bez((22, 13), (12, 7), (-8, 7), (-20, 7)) + bez((-20, 7), (-24, 7), (-25, 9), (-24, 10))
            form(notch(body, 0.8, 4), P.BADGER, sdx=-2, sdy=1.2)
            shape([(-24, 18), (-30, 17), (-29, 14), (-24, 14)], P.BADGER, LINE*0.8)
            C.restoreState()
            for lx in (-18, 6):
                tube([(lx, 14), (lx - 1, 1)], 4.8, 4.2, P.BADGER_DARK, sh=0)
                for c_ in (0, 1.5, 3): stroke([(lx + 1 + c_, 0.6), (lx + 2 + c_, -0.8)], LINE*0.5)
            hx, hy = 24, 20
        else:
            hx, hy = 0, 6
        with T(hx, hy, 1):
            head = bez((-6, 8), (-2, 10), (6, 8), (12, 3)) + bez((12, 3), (16, 0), (16, -2), (13, -3)) + \
                   bez((13, -3), (6, -5), (-2, -4), (-6, -1)) + bez((-6, -1), (-8, 2), (-8, 6), (-6, 8))
            shape(head, 1.0)
            C.saveState(); C.clipPath(poly(head), stroke=0, fill=0)
            fill(bez((-8, 5.5), (0, 6.5), (8, 3.2), (16, -0.5)) + [(16, -2)] + bez((16, -2), (8, 1), (0, 2.5), (-8, 1.8)), P.BADGER_DARK)
            C.restoreState()
            stroke(head, LINE, closed=True)
            shape(ell(-3.5, 8, 2.2, 1.8, 12), 1.0, LINE*0.7)
            if mood == "sleepy":
                stroke([(2, 3.8), (5, 3.8)], LINE*0.8, g=1.0)
            else:
                dot(3.6, 3.8, 1.1, 1.0); dot(3.8, 3.8, 0.6, 0.0)
            dot(15.2, -1.2, 1.3, 0.0)


def duck(x, y, s=1.0, flip=False, dive=False):
    """mallard sitting on the water (local length ~30)"""
    with T(x, y, s, flip):
        if dive:
            shape(bez((-4, 0), (-6, 8), (-2, 14), (0, 10)) + [(3, 0)], P.DUCK)
            shape([(-3, 12), (-1, 16), (1, 12)], P.DUCK_BILL, LINE*0.6)
            stroke(ell(0, 0, 10, 2, 20), LINE*0.6, closed=True)
            return
        body = bez((-14, 4), (-16, 12), (4, 13), (12, 9)) + bez((12, 9), (15, 6), (13, 0), (8, 0)) + [(-10, 0)] + \
               bez((-10, 0), (-13, 0), (-15, 2), (-14, 4))
        form(body, P.DUCK, sdx=-1.4, sdy=1)
        shape([(-14, 6), (-19, 10), (-16, 5)], P.DUCK, LINE*0.8)
        stroke(bez((-8, 7), (-4, 10), (2, 10), (6, 7)), LINE*0.6)
        shape([(6, 12), (10, 12), (10, 14), (6, 14)], 1.0, LINE*0.5)
        shape(ell(9, 17, 5, 4.5, 20), P.DUCK_HEAD)
        shape([(13, 17.5), (19, 16.5), (19, 15), (13.5, 15.2)], P.DUCK_BILL, LINE*0.7)
        dot(10.4, 18.2, 0.9, 0.0)


# ------------------------------------------------------------------ scenery
def willow(x, y, s=1.0, seed=5):
    """weeping willow (local height ~130)"""
    r = random.Random(seed)
    with T(x, y, s):
        trunk = bez((-12, 0), (-8, 20), (-10, 40), (-6, 58)) + [(6, 58)] + bez((6, 58), (9, 40), (7, 20), (12, 0))
        form(trunk, P.BARK, w=BG, sdx=2, sdy=0, sh=0.15)
        for bx in (-1, 1):
            stroke(bez((0, 54), (bx*8, 66), (bx*18, 74), (bx*26, 80)), BG*3.4)
            stroke(bez((0, 54), (bx*8, 66), (bx*18, 74), (bx*26, 80)), BG*1.8, g=P.BARK)
        crown = []
        N = 13
        for i in range(N + 1):
            a = math.pi*i/N
            k_ = 1 + r.uniform(-0.06, 0.1)
            crown.append((math.cos(a)*50*k_, 84 + math.sin(a)*40*k_))
        crown = resample(crown + [(-48, 76), (-30, 70), (0, 68), (30, 70), (48, 76)], 3.0, True)
        fill(crown, P.WILLOW); offset_shadow(crown, 6, 5, 0.1); stroke(crown, BG*1.1, closed=True)
        for i in range(26):
            sx = -58 + i*4.6 + r.uniform(-1.5, 1.5)
            top = 84 + 34*math.sqrt(max(0, 1 - (sx/56)**2)) - 6
            bot = 4 + r.uniform(0, 22) + abs(sx)*0.2
            pts = [(sx*(1 + 0.08*t/80) + math.sin(t*0.1)*1.2, top - t) for t in range(0, int(top - bot), 3)]
            if len(pts) > 2:
                stroke(pts, 2.4, g=0.0); stroke(pts, 1.2, g=P.WILLOW_DARK if i % 3 else P.WILLOW)


def stump(x, y, s=1.0):
    with T(x, y, s):
        side = [(-22, 0), (22, 0), (20, 26), (-20, 26)]
        form(side, P.BARK, w=BG*1.2, sdx=3, sdy=0)
        for bx in (-12, -2, 9): s_(bez((bx, 2), (bx + 1, 10), (bx - 1, 18), (bx, 25)), BG*0.6)
        shape(ell(0, 26, 20, 6, 30), 0.85, BG*1.1)
        for rr in (14, 9, 4): stroke(ell(0.5, 26, rr, rr*0.3, 24), BG*0.5, closed=True, g=0.45)
        for bx in (-1, 1):
            stroke(bez((bx*20, 2), (bx*28, 0), (bx*32, -2), (bx*36, -2)), BG*2.4)


def reeds(x, y, s=1.0, seed=2, n=7):
    r = random.Random(seed)
    with T(x, y, s):
        for i in range(n):
            bx = (i - n/2)*4 + r.uniform(-1.5, 1.5); h = 34 + r.uniform(-8, 14); lean = r.uniform(-5, 5)
            stroke(bez((bx, 0), (bx + lean*0.3, h*0.4), (bx + lean*0.7, h*0.8), (bx + lean, h)), LINE*1.3, g=0.0)
            stroke(bez((bx, 0), (bx + lean*0.3, h*0.4), (bx + lean*0.7, h*0.8), (bx + lean, h)), LINE*0.5, g=P.REED)
            if i % 2 == 0:
                with T(bx + lean*0.8, h*0.82, 1, rot=-lean*2):
                    shape(rrect(-1.9, 0, 3.8, 10, 1.8), P.CATTAIL, LINE*0.7)
        for i in range(3):
            lx = (i - 1)*8
            shape(bez((lx, 0), (lx + 2, 10), (lx + 8, 18), (lx + 12, 22)) + bez((lx + 12, 22), (lx + 6, 14), (lx + 3, 8), (lx + 2.5, 0)),
                  P.REED, LINE*0.6)


def water(pts, seed=4, ripples=6):
    """flat pond water inside polygon pts, with a few ripple lines"""
    r = random.Random(seed)
    fill(pts, P.POND_WATER)
    x0, y0, x1, y1 = bbox(pts)
    C.saveState(); C.clipPath(poly(pts), stroke=0, fill=0)
    for _ in range(ripples):
        cx = r.uniform(x0 + 20, x1 - 20); cy = r.uniform(y0 + 4, y1 - 4); w_ = r.uniform(14, 34)
        stroke([(cx - w_, cy), (cx - w_*0.3, cy + 1), (cx + w_*0.4, cy - 0.5), (cx + w_, cy)], BG*1.1, g=P.POND_RIPPLE)
    C.restoreState()
    stroke(pts, BG, closed=True)


def far_trees(p, y, seed=3, g=P.TREE_CROWN):
    """a row of soft tree tops on the far bank"""
    r = random.Random(seed)
    xx = p.x - 20
    pts = [(p.x - 10, y)]
    while xx < p.x + p.w + 30:
        w_ = r.uniform(22, 40); h = r.uniform(18, 34)
        pts += bez((xx, y + h*0.4), (xx + w_*0.1, y + h*1.1), (xx + w_*0.9, y + h*1.1), (xx + w_, y + h*0.4), 8)
        xx += w_*0.85
    pts += [(p.x + p.w + 10, y)]
    fill(pts, g); stroke(pts[1:-1], BG*0.9)


def pond_bg(p, bank=0.3, far=0.55, seed=1, trees=True, clouds_=True, sky_g=None):
    """sky, far meadow + trees, the pond and the near bank. bank/far = panel fractions of the shorelines"""
    fill([(p.x, p.y), (p.x + p.w, p.y), (p.x + p.w, p.y + p.h), (p.x, p.y + p.h)], sky_g if sky_g is not None else P.SKY)
    if clouds_: cloud(p.X(0.2), p.Y(0.9), 0.8); cloud(p.X(0.78), p.Y(0.84), 0.6)
    fy = p.Y(far)
    if trees: far_trees(p, fy + 6, seed)
    fill([(p.x - 5, fy - 2), (p.x + p.w + 5, fy - 2), (p.x + p.w + 5, fy + 8), (p.x - 5, fy + 8)], P.GRASS)
    s_([(p.x - 5, fy + 8), (p.x + p.w + 5, fy + 8)], BG*0.8)
    wpts = [(p.x - 5, p.Y(bank) - 2)] + bez((p.x - 5, p.Y(bank) + 6), (p.X(0.3), fy + 4), (p.X(0.7), fy + 2), (p.x + p.w + 5, fy), 14)[1:] + \
           [(p.x + p.w + 5, p.Y(bank) - 2)]
    water(wpts, seed + 3)
    bank_pts = [(p.x - 5, p.y - 5), (p.x - 5, p.Y(bank))] + \
               bez((p.x - 5, p.Y(bank)), (p.X(0.35), p.Y(bank) + 8), (p.X(0.65), p.Y(bank) - 6), (p.x + p.w + 5, p.Y(bank) + 2), 14)[1:] + \
               [(p.x + p.w + 5, p.y - 5)]
    fill(bank_pts, P.GRASS); stroke(bank_pts[1:-1], BG)
    return fy


def mill(x, y, s=1.0, lantern_=False, wheel=True):
    """the small old mill house with a water wheel on its left side (local width ~120)"""
    with T(x, y, s):
        if wheel:
            with T(-58, 34, 1):
                shape(ell(0, 0, 32, 32, 40), P.MILL_WHEEL, BG*1.2)
                shape(ell(0, 0, 25, 25, 36), P.SKY, BG*0.8)
                for a in range(0, 360, 30):
                    ra = math.radians(a)
                    s_([(0, 0), (math.cos(ra)*30, math.sin(ra)*30)], BG*1.4)
                    shape([(math.cos(ra)*25 - 2, math.sin(ra)*25 - 2), (math.cos(ra)*34, math.sin(ra)*34)] +
                          [(math.cos(ra + 0.14)*34, math.sin(ra + 0.14)*34), (math.cos(ra + 0.14)*25, math.sin(ra + 0.14)*25)], P.MILL_WHEEL, BG*0.7)
                shape(ell(0, 0, 5, 5, 16), 0.3, BG)
        wall = [(-40, 0), (48, 0), (48, 64), (-40, 64)]
        sh_(wall, P.MILL_WALL)
        fill([(-40, 64), (48, 64), (48, 58), (-40, 58)], P.WALL_SHADE)
        sh_([(-40, 0), (48, 0), (48, 12), (-40, 12)], P.STONE_BASE)
        for xx in (-32, -20, -6, 8, 22, 36): s_([(xx, 0), (xx, 6)], BG*0.6); s_([(xx + 6, 6), (xx + 6, 12)], BG*0.6)
        roof = [(-50, 60), (4, 112), (58, 60)]
        sh_(roof, P.ROOF)
        C.saveState(); C.clipPath(poly(roof), stroke=0, fill=0)
        for row in range(1, 10): s_([(-52, 60 + row*5.5), (60, 60 + row*5.5)], BG*0.55)
        C.restoreState()
        sh_([(-52, 57.5), (60, 57.5), (60, 60.5), (-52, 60.5)], P.ROOF_EDGE)
        d = [(-30, 12), (-14, 12), (-14, 46), (-30, 46)]
        sh_(d, P.DOOR)
        for kk in (-26, -22, -18): s_([(kk, 13), (kk, 45)], BG*0.5)
        dot(-17, 29, 0.8, 0.9)
        wx = 8
        sh_([(wx - 1.5, 22.5), (wx + 23.5, 22.5), (wx + 23.5, 48.5), (wx - 1.5, 48.5)], 1.0)
        gl = [(wx, 24), (wx + 22, 24), (wx + 22, 47), (wx, 47)]
        sh_(gl, P.WINDOW_GLASS)
        s_([(wx + 11, 24), (wx + 11, 47)], BG*1.2, g=1.0); s_([(wx, 35.5), (wx + 22, 35.5)], BG*1.2, g=1.0)
        sh_([(wx - 3, 19.5), (wx + 25, 19.5), (wx + 25, 22.5), (wx - 3, 22.5)], P.SILL)
        if lantern_:
            lantern(wx + 18, 22.5, 0.55)
        sh_(ell(4, 80, 7, 7, 24), P.ROUND_WINDOW)


def lantern(x, y, s=1.0, glow=False):
    """old storm lantern standing on (x, y) (local height ~30)"""
    with T(x, y, s):
        if glow:
            fill(ell(0, 13, 26, 26, 30), P.LANTERN_GLOW, 0.45)
        shape([(-8, 0), (8, 0), (7, 3), (-7, 3)], P.LANTERN, LINE*0.8)
        glass = bez((-5, 3), (-8, 9), (-8, 17), (-5, 22)) + [(5, 22)] + bez((5, 22), (8, 17), (8, 9), (5, 3))
        shape(glass, P.LANTERN_GLOW if glow else 0.92, LINE*0.8)
        for bx in (-6.5, 6.5): stroke([(bx*0.8, 3), (bx, 12), (bx*0.8, 22)], LINE*0.6)
        shape([(-6, 22), (6, 22), (4, 26), (-4, 26)], P.LANTERN, LINE*0.8)
        stroke(bez((-6, 25), (-7, 33), (7, 33), (6, 25)), LINE*0.9)
        if glow: fill(ell(0, 11, 1.4, 3, 12), 0.2)


def bench(x, y, s=1.0):
    """wooden bench seen from the front (local width ~90)"""
    with T(x, y, s):
        for lx in (-36, 36):
            sh_([(lx - 3, 0), (lx + 3, 0), (lx + 3, 18), (lx - 3, 18)], P.BENCH)
        sh_([(-44, 18), (44, 18), (44, 23), (-44, 23)], P.BENCH)
        for lx in (-36, 36): sh_([(lx - 2.5, 23), (lx + 2.5, 23), (lx + 2.5, 44), (lx - 2.5, 44)], P.BENCH)
        for yy in (30, 38): sh_([(-44, yy), (44, yy), (44, yy + 5), (-44, yy + 5)], P.BENCH)


def jetty(x0, x1, y, h=12):
    """a short wooden jetty (molo) front-on, deck top at y"""
    for lx in (x0 + 10, (x0 + x1)/2, x1 - 10):
        sh_([(lx - 4, y - h - 30), (lx + 4, y - h - 30), (lx + 4, y), (lx - 4, y)], P.BARK)
    sh_([(x0, y - h), (x1, y - h), (x1, y), (x0, y)], P.JETTY)
    xx = x0 + 22
    while xx < x1 - 4:
        s_([(xx, y - h), (xx, y)], BG*0.6); xx += 22


def dredge_sign(x, y, s=1.0, readable=True):
    """the sign by the road: ODBAHNĚNÍ RYBNÍKA – BAGRY OD PONDĚLÍ"""
    with T(x, y, s):
        sh_([(-2.5, 0), (2.5, 0), (2.5, 44), (-2.5, 44)], P.SIGN_POST)
        form([(-32, 40), (32, 40), (32, 76), (-32, 76)], P.SIGN_BOARD, w=BG*1.1, sdx=2, sdy=0, sh=0.08)
        if readable:
            hand_text(-100, 67, 200, "ODBAHNĚNÍ RYBNÍKA", "SHB", 5.2)
            hand_text(-100, 59, 200, "BAGRY OD PONDĚLÍ", "SHB", 5.2)
            with T(-6, 43, 0.17):
                excavator(0, 0, 1.0, detail=False)
        else:
            for yy in (60, 52, 46): s_([(-24, yy), (24, yy)], BG*1.2, g=0.4)


def excavator(x, y, s=1.0, detail=True, flip=False):
    """small yellow digger (local width ~110)"""
    with T(x, y, s, flip):
        shape(rrect(-44, 0, 72, 14, 7), P.EXCAVATOR_DARK, LINE)
        for wx in (-36, -22, -8, 6, 20): shape(ell(wx, 7, 4, 4, 14), 0.6, LINE*0.6)
        form([(-40, 14), (22, 14), (22, 34), (-40, 34)], P.EXCAVATOR)
        form([(-36, 34), (-8, 34), (-8, 62), (-36, 62)], P.EXCAVATOR)
        shape([(-32, 40), (-12, 40), (-12, 58), (-32, 58)], P.WINDOW_GLASS, LINE*0.8)
        tube([(10, 32), (36, 66), (58, 50)], 8, 7, P.EXCAVATOR)
        tube([(58, 50), (64, 20)], 6, 6, P.EXCAVATOR)
        shape([(56, 22), (72, 22), (70, 8), (60, 4)], P.EXCAVATOR_DARK)
        if detail:
            for tx in (58, 62, 66, 70): stroke([(tx, 6), (tx - 1, 1)], LINE*0.8)


# ------------------------------------------------------------------ clues in the mud
def boot_print(x, y, s=1.0, rot=0, g=P.MUD_DARK):
    """grown-up boot sole print (local length ~30)"""
    with T(x, y, s, rot=rot):
        sole = bez((0, -15), (5.5, -15), (6, -8), (5, -3)) + bez((5, -3), (5.5, 4), (6.5, 10), (4, 15)) + \
               bez((4, 15), (0, 17), (-4, 17), (-6, 14)) + bez((-6, 14), (-7, 8), (-5.5, 2), (-5, -3)) + \
               bez((-5, -3), (-6, -8), (-5.5, -15), (0, -15))
        fill(sole, g)
        for yy in (-11, -7, -3, 4, 8, 12):
            stroke([(-4, yy), (4, yy)], LINE*0.9, g=P.MUD)
        stroke([(-5, 0.5), (5, 0.5)], LINE*1.4, g=P.MUD)


def stick_dot(x, y, r=2.2, g=P.MUD_DARK):
    fill(ell(x, y, r, r*0.8, 14), g)
    stroke(ell(x, y, r*1.25, r, 14, 20, 200), LINE*0.5, g=0.2)


def bird_track(x, y, s=1.0, rot=0, g=P.MUD_DARK):
    with T(x, y, s, rot=rot):
        for a in (-35, 0, 35):
            ra = math.radians(90 + a)
            stroke([(0, 0), (math.cos(ra)*7, math.sin(ra)*7)], LINE*1.1, g=g)
        stroke([(0, 0), (0, -3.5)], LINE*1.1, g=g)


def badger_track(x, y, s=1.0, rot=0, g=P.MUD_DARK):
    with T(x, y, s, rot=rot):
        fill(bez((-5, 0), (-5, 4), (5, 4), (5, 0)) + bez((5, 0), (4, -3), (-4, -3), (-5, 0)), g)
        for i in range(5):
            tx = -5 + i*2.5
            fill(ell(tx, 7, 1.1, 1.4, 10), g)
            stroke([(tx, 8.6), (tx + 0.2, 12.5)], LINE*0.8, g=g)


def mud_patch(x, y, w, h, seed=3):
    r = random.Random(seed)
    pts = [(x + math.cos(a)*w*(1 + r.uniform(-0.08, 0.08)), y + math.sin(a)*h*(1 + r.uniform(-0.1, 0.1)))
           for a in [i*math.tau/28 for i in range(28)]]
    fill(pts, P.MUD); stroke(pts, BG*0.6, closed=True, g=0.3)


def hole(x, y, w=60, h=18, tin_print=True, fresh=False):
    """a dug hole seen from above at an angle; with the square dent of the missing tin"""
    fill(ell(x, y + h*0.9, w*1.3, h*0.9, 30), P.MUD)
    for dx, dy, rr in ((-w*1.05, h*0.6, 9), (w*1.1, h*0.9, 7), (w*0.7, h*1.6, 6), (-w*0.6, h*1.7, 8)):
        shape(ell(x + dx, y + dy, rr*1.3, rr*0.7, 16), P.MUD, BG*0.7)
    pit = ell(x, y + h*0.5, w, h, 34)
    shape(pit, P.MUD_DARK, BG*1.1)
    if tin_print:
        dent = [(x - w*0.38, y + h*0.12), (x + w*0.4, y + h*0.12), (x + w*0.34, y + h*0.62), (x - w*0.32, y + h*0.62)]
        fill(dent, 0.15)
        stroke(dent, LINE*0.8, closed=True, g=P.MUD)
    if fresh:
        for i in range(5):
            dot(x - w*0.8 + i*w*0.4, y + h*1.35 + (i % 2)*3, 1.6, P.MUD_DARK)


def star_stone(x, y, s=1.0, grass=True):
    """flat stone half hidden in grass, a star scratched into it"""
    with T(x, y, s):
        st = bez((-16, 0), (-18, 8), (-8, 13), (2, 12)) + bez((2, 12), (12, 12), (18, 7), (16, 0)) + \
             bez((16, 0), (8, -2), (-8, -2), (-16, 0))
        form(st, P.STONE, w=LINE, sdx=-1.5, sdy=1)
        pts = []
        for i in range(6):
            a = math.pi/2 + i*4*math.pi/5
            pts.append((math.cos(a)*5.5, 5.5 + math.sin(a)*4.2))
        stroke(pts, LINE*0.9, g=0.2)
        if grass:
            for gx in (-18, -13, -7, 9, 14, 19):
                stroke(bez((gx, -2), (gx + 1, 4), (gx + 2, 8), (gx + 4, 12)), LINE*1.2)
                stroke(bez((gx, -2), (gx + 1, 4), (gx + 2, 8), (gx + 4, 12)), LINE*0.5, g=P.TUFT)


def spade(x, y, s=1.0, rot=0):
    """kid's garden spade; (x, y) = blade tip"""
    with T(x, y, s, rot=rot):
        shape(bez((-5, 6), (-5, 1), (-2, -2), (0, -2)) + bez((0, -2), (2, -2), (5, 1), (5, 6)) + [(4, 12), (-4, 12)], P.METAL)
        tube([(0, 12), (0, 40)], 2.6, 2.6, P.RAKE_HANDLE, sh=0)
        shape(rrect(-5, 39, 10, 3.5, 1.2), P.RAKE_HANDLE, LINE*0.8)


def shoebox(x, y, s=1.0, open_=True):
    """Tonda's shoebox treasure: green pebble, feather, toy car, a drawn star"""
    with T(x, y, s):
        if open_:
            form([(-26, 0), (26, 0), (26, 16), (-26, 16)], P.SHOEBOX, sdx=2, sdy=0)
            fill([(-24, 14), (24, 14), (24, 16), (-24, 16)], 0.35)
            shape([(-26, 16), (26, 16), (30, 34), (-22, 34)], P.SHOEBOX, LINE)
            with T(4, 25, 0.9):
                star(0, 0, 6, P.HOODIE_STAR)
            shape(ell(-14, 18, 4, 3, 16), P.GRASS, LINE*0.7)
            shape(rrect(6, 15, 12, 5, 2), P.TORCH_BODY, LINE*0.7)
            for wx in (9, 15): shape(ell(wx, 15, 1.6, 1.6, 10), 0.2, LINE*0.4)
            with T(-4, 16, 0.55, rot=-70):
                vane = bez((0, 0), (-4.5, 6), (-4, 16), (0, 24)) + bez((0, 24), (4, 16), (4.5, 6), (0, 0))
                shape(vane, P.FEATHER, LINE*0.9)
        else:
            form([(-26, 0), (26, 0), (26, 16), (-26, 16)], P.SHOEBOX, sdx=2, sdy=0)
            shape(rrect(-27.5, 13, 55, 6, 1), P.SHOEBOX, LINE)


def backpack(x, y, s=1.0):
    with T(x, y, s):
        form(rrect(-12, 0, 24, 30, 6), P.JEANS, sdx=2, sdy=0)
        shape(bez((-12, 22), (-12, 30), (12, 30), (12, 22)) + [(12, 16), (-12, 16)], P.JEANS, LINE*0.9)
        shape(rrect(-7, 3, 14, 9, 2), P.JEANS, LINE*0.7)
        stroke(bez((-6, 30), (-6, 36), (6, 36), (6, 30)), LINE*1.6)


# ------------------------------------------------------------------ the treasure
def treasure_tin(x, y, s=1.0, open_=False, dirty=True):
    """the club's big biscuit tin with a star, rusty from 60 years in the mud (local width 64)"""
    r = random.Random(11)
    with T(x, y, s):
        body = rrect(-32, 0, 64, 24, 3)
        form(body, P.TIN, sdx=3, sdy=0)
        for bx in (-26, 26): stroke([(bx, 2), (bx, 22)], LINE*0.5, g=0.45)
        if open_:
            fill([(-30, 21), (30, 21), (30, 24), (-30, 24)], 0.25)
            lid = [(-32, 24), (32, 24), (38, 46), (-26, 46)]
            form(lid, P.TIN, sdx=0, sdy=0, sh=0)
            star(6, 35, 7, 0.95)
        else:
            shape(rrect(-34, 20, 68, 7, 2.5), P.TIN, LINE)
            star(0, 11, 7, 0.95)
        if dirty:
            for _ in range(10):
                dot(r.uniform(-28, 28), r.uniform(2, 20), r.uniform(0.8, 2.2), P.RUST)


def coin(x, y, rad=10, shine=False):
    """stříbrný tolar: silver coin with a lion and dots around the rim"""
    if shine:
        for i in range(8):
            a = i*math.tau/8
            stroke([(x + math.cos(a)*rad*1.35, y + math.sin(a)*rad*1.35), (x + math.cos(a)*rad*1.9, y + math.sin(a)*rad*1.9)], LINE*1.1)
    shape(ell(x, y, rad, rad, 36), P.SILVER, LINE*1.0)
    stroke(ell(x, y, rad*0.8, rad*0.8, 30), LINE*0.5, closed=True, g=P.SILVER_DARK)
    for i in range(18):
        a = i*math.tau/18
        dot(x + math.cos(a)*rad*0.9, y + math.sin(a)*rad*0.9, rad*0.035, 0.35)
    with T(x, y, rad/10):
        lion = bez((-4, -4), (-5, 0), (-3, 3), (-1, 4)) + bez((-1, 4), (0, 6), (3, 6), (3, 3)) + \
               bez((3, 3), (5, 1), (4, -3), (3, -4)) + [(1, -2), (-1, -4)]
        shape(lion, P.SILVER_DARK, LINE*0.4)
        for cx_ in (-2, 0, 2): dot(cx_, 7.2, 0.6, 0.35)
    stroke(ell(x - rad*0.3, y + rad*0.35, rad*0.35, rad*0.2, 12, 100, 200), LINE*1.0, g=1.0)


def spyglass(x, y, s=1.0, rot=0):
    """brass pocket telescope, pulled out (local length ~60)"""
    with T(x, y, s, rot=rot):
        segs = ((0, 20, 9.0), (18, 38, 7.4), (36, 54, 6.0))
        for x0, x1, w_ in segs:
            form([(x0, -w_/2), (x1, -w_/2), (x1, w_/2), (x0, w_/2)], P.BRASS, sdx=0, sdy=-1.2)
            shape([(x0 - 1, -w_/2 - 0.8), (x0 + 2, -w_/2 - 0.8), (x0 + 2, w_/2 + 0.8), (x0 - 1, w_/2 + 0.8)], P.BRASS, LINE*0.7)
        shape(ell(-1, 0, 1.6, 4.4, 14), P.GLASS, LINE*0.7)
        shape(ell(55, 0, 1.2, 3, 12), 0.3, LINE*0.6)


def badge(x, y, r=7):
    """club star badge (brass star on a round pin)"""
    shape(ell(x, y, r, r, 30), P.BRASS, LINE*0.9)
    star(x, y, r*0.72, P.TAG_STAR)


def whistle(x, y, s=1.0, rot=0):
    with T(x, y, s, rot=rot):
        shape(ell(0, 0, 5, 5, 20), P.METAL, LINE*0.8)
        shape([(0, 1.5), (13, 1.5), (13, 5), (0, 5)], P.METAL, LINE*0.8)
        fill([(6, 2.5), (9, 2.5), (9, 4), (6, 4)], 0.1)


def marbles(x, y, s=1.0):
    for (dx, dy, g) in ((0, 0, 0.7), (7, 1, 0.45), (3.5, 5.5, 0.85)):
        shape(ell(x + dx*s, y + dy*s, 3.2*s, 3.2*s, 16), g, LINE*0.7)
        stroke(ell(x + dx*s - 0.8*s, y + dy*s + 0.8*s, 1.2*s, 0.8*s, 10, 90, 200), LINE*0.6, g=1.0)


def club_photo(x, y, w=70, h=52, rot=0, figures=True):
    """the old photo of Honza, Franta and Věrka at the pond, a star drawn in the corner"""
    with T(x, y, 1.0, rot=rot):
        shape([(0, 0), (w, 0), (w, h), (0, h)], P.PHOTO_FRAME, LINE*0.8)
        fill([(4, 10), (w - 4, 10), (w - 4, h - 4), (4, h - 4)], P.PHOTO_BG)
        C.saveState(); C.clipPath(poly([(4, 10), (w - 4, 10), (w - 4, h - 4), (4, h - 4)]), stroke=0, fill=0)
        fill([(4, 10), (w - 4, 10), (w - 4, h*0.45), (4, h*0.45)], 0.8)
        if figures:
            fs = (h - 14)/112
            young(w*0.3, 12, fs, "deda", mood="grin", shadow=False)
            young(w*0.5, 12, fs, "franta", mood="happy", shadow=False)
            young(w*0.7, 12, fs, "verka", mood="happy", shadow=False)
        C.restoreState()
        star(w - 10, h - 10, 4, P.TAG_STAR)
        stroke([(4, 10), (w - 4, 10), (w - 4, h - 4), (4, h - 4)], LINE*0.5, closed=True, g=0.4)


def picture_letter(x, y, s=1.0, rot=0):
    """Franta's letter: no words, only a child's drawings: hen -> church clock -> boot -> star"""
    with T(x, y, s, rot=rot):
        paper = [(0, 0), (90, 2), (92, 64), (-2, 62)]
        shape(paper, P.LETTER_PAPER, LINE*0.8)
        ink = P.MAP_INK
        w_ = LINE*0.8
        # hen
        stroke(ell(16, 42, 8, 6, 24), w_, closed=True, g=ink)
        stroke(ell(24, 49, 3.4, 3.4, 16), w_, closed=True, g=ink)
        stroke([(27, 49), (30.5, 48), (27, 47)], w_, g=ink)
        stroke([(22, 52.5), (23, 55), (24.5, 53), (26, 55), (26.5, 52)], w_, g=P.TAG_STAR)
        stroke([(8, 44), (4, 50), (8, 47)], w_, g=ink)
        for lx in (14, 18): stroke([(lx, 36), (lx, 32), (lx + 2, 31)], w_, g=ink)
        dot(24.5, 50, 0.6, 0.0)
        # arrow
        stroke([(34, 44), (44, 44)], w_, g=ink); stroke([(41, 46.5), (44, 44), (41, 41.5)], w_, g=ink)
        # church tower with a clock at three
        stroke([(52, 30), (52, 50), (64, 50), (64, 30)], w_, g=ink)
        stroke([(50, 50), (58, 60), (66, 50)], w_, g=ink)
        stroke([(58, 60), (58, 64)], w_, g=ink); stroke([(56, 62.5), (60, 62.5)], w_, g=ink)
        stroke(ell(58, 43, 4, 4, 18), w_, closed=True, g=ink)
        stroke([(58, 43), (58, 46)], w_*0.8, g=ink); stroke([(58, 43), (60.6, 43)], w_*0.8, g=ink)
        stroke([(55, 30), (55, 36), (61, 36), (61, 30)], w_, g=ink)
        # arrow down-left
        stroke([(62, 26), (54, 18)], w_, g=ink); stroke([(54, 21.5), (54, 18), (57.5, 18)], w_, g=ink)
        # boot
        stroke([(34, 6), (34, 22), (42, 22), (42, 12), (50, 10), (50, 6), (34, 6)], w_, g=ink)
        # arrow to the star
        stroke([(30, 12), (20, 12)], w_, g=ink); stroke([(23, 14.5), (20, 12), (23, 9.5)], w_, g=ink)
        pts = []
        for i in range(6):
            a = math.pi/2 + i*4*math.pi/5
            pts.append((10 + math.cos(a)*7, 13 + math.sin(a)*7))
        stroke(pts, w_*1.2, g=P.TAG_STAR)


# ------------------------------------------------------------------ the whole map, big
def full_map(x, y, s=1.0, rot=0):
    """both halves taped together (local 240 x 160): cottage, path, big willow, 20 child steps,
    star stone, X by the pond, the mill and the footbridge that isn't there any more"""
    with T(x, y, s, rot=rot):
        outline = [(0, 0), (240, 0), (240, 160), (0, 160)]
        shape(outline, P.MAP_PAPER, LINE*0.9)
        seam = _torn_edge(120, 0, 160, 5)
        stroke(seam, LINE*0.6, g=0.45)
        for ty in (30, 90, 140):
            fill([(112, ty), (128, ty + 2), (127, ty + 12), (111, ty + 10)], 0.97, 0.7)
        ink = P.MAP_INK
        # cottage
        shape([(14, 108), (40, 108), (40, 128), (14, 128)], 1.0, LINE*0.7)
        shape([(10, 128), (27, 142), (44, 128)], P.MAP_PAPER, LINE*0.7)
        shape(ell(27, 134, 3, 3, 12), P.MAP_PAPER, LINE*0.5)
        # dashed path
        path = resample(bez((42, 112), (80, 100), (70, 70), (96, 62)), 1.0)
        for i in range(0, len(path) - 4, 9):
            stroke(path[i:i + 5], LINE*0.9, g=ink)
        # the big willow
        stroke([(100, 50), (100, 62)], LINE*1.2, g=ink)
        stroke(ell(100, 70, 12, 9, 20), LINE*0.9, closed=True, g=ink)
        for dx in (-9, -4, 2, 7):
            stroke([(100 + dx, 66), (100 + dx*1.1, 56)], LINE*0.5, g=ink)
        hand_text(84, 84, 40, "VRBA", "SHB", 6.5, g=0.3)
        # twenty small footprints
        for i in range(10):
            fx = 108 + i*7.4; fy = 52 - i*1.6
            for side in (0, 1):
                fill(ell(fx + side*3, fy + (2.4 if side else -1.2), 1.2, 1.8, 10, rot=-20), ink)
        hand_text(112, 24, 60, "20 KROKŮ", "SHB", 6.5, g=0.3)
        # star stone and the X
        shape(ell(186, 36, 7, 4, 16), 0.85, LINE*0.6); star(186, 36.5, 2.6, P.TAG_STAR)
        stroke([(194, 22), (204, 32)], LINE*1.6, g=P.TAG_STAR); stroke([(204, 22), (194, 32)], LINE*1.6, g=P.TAG_STAR)
        # pond, reeds, footbridge, mill wheel
        stroke(ell(200, 88, 32, 20, 30), LINE*0.9, closed=True, g=ink)
        for rx in (170, 174, 228):
            stroke([(rx, 76), (rx + 1, 84)], LINE*0.6, g=ink)
        for i in range(4):
            stroke([(160 + i*4, 100), (160 + i*4, 108)], LINE*0.6, g=ink)
        stroke([(156, 100), (176, 100)], LINE*0.6, g=ink); stroke([(156, 108), (176, 108)], LINE*0.6, g=ink)
        hand_text(146, 114, 50, "LÁVKA", "SHB", 6, g=0.3)
        stroke(ell(222, 128, 8, 8, 20), LINE*0.8, closed=True, g=ink)
        for a in range(0, 360, 45):
            ra = math.radians(a)
            stroke([(222, 128), (222 + math.cos(ra)*8, 128 + math.sin(ra)*8)], LINE*0.5, g=ink)
        hand_text(200, 144, 50, "MLÝN", "SHB", 6.5, g=0.3)
        hand_text(8, 8, 100, "KLUB", "SHB", 11, align="left")
        hand_text(132, 8, 120, "HVĚZDIČKA", "SHB", 11, align="left")


# ------------------------------------------------------------------ light
def mist(p, bands=4, alpha=0.45, seed=2):
    r = random.Random(seed)
    for i in range(bands):
        yy = p.Y(0.15 + i*0.18) + r.uniform(-6, 6)
        pts = bez((p.x - 20, yy), (p.X(0.3), yy + 14), (p.X(0.7), yy - 10), (p.x + p.w + 20, yy + 4), 20) + \
              bez((p.x + p.w + 20, yy - 14), (p.X(0.7), yy - 26), (p.X(0.3), yy - 4), (p.x - 20, yy - 16), 20)
        fill(pts, P.MIST, alpha)


def torch_beam(x0, y0, x1a, y1a, x1b, y1b, alpha=0.5):
    fill([(x0, y0), (x1a, y1a), (x1b, y1b)], P.LANTERN_GLOW, alpha)


# ------------------------------------------------------------------ sitting
HIPS = {"alica": 45, "hanka": 31, "tonda": 47, "verka": 50, "deda": 59, "babi": 50}


def seated(fn, who, x, seat_y, s, leg_g, boot_g, thigh_g=None, drop=24, edge=0, **kw):
    """a front-facing figure sitting on a seat/jetty edge at seat_y: body clipped at the seat,
    short foreshortened thighs over the edge, shins hanging down, boots pointing at us"""
    C.saveState()
    C.clipPath(poly([(x - 200, seat_y), (x + 200, seat_y), (x + 200, seat_y + 400), (x - 200, seat_y + 400)]), stroke=0, fill=0)
    fn(x, seat_y - HIPS[who]*s, s, shadow=False, **kw)
    C.restoreState()
    tg = thigh_g if thigh_g is not None else leg_g
    top = seat_y - edge
    for sx in (-1, 1):
        tube([(x + sx*4.6*s, top), (x + sx*5.2*s, top - drop*s)], 5.2*s, 4.4*s, leg_g, sh=0.1)
        shape(ell(x + sx*5.4*s, top - drop*s - 1.5*s, 3.8*s, 3.0*s, 16), boot_g, LINE)
    for sx in (-1, 1):   # knees poking over the edge, towards us
        shape(ell(x + sx*4.4*s, seat_y + 0.5*s, 4.2*s, 3.6*s, 20), tg, LINE)
