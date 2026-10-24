"""Game art for story 6 "Kam mizí perníčky?": the Advent kitchen (window with the sill, the pantry shelf),
the big spruce by the mill at dawn, the tin and its count, the tits, děda's boots with needles and ribbon,
the feeder; the ornament tiles of "Hvězdy na smrčku" and the suspect cards. The snowy garden is story 5's."""
import math, random
import lib
from lib import ell, bez, rrect
import palette as P
from style3 import *
from style3 import C
from chars3 import star, babicka, deda, tonda, dormouse, notebook_big
from scenes3 import BG, s_, sh_, sky, hills, shelf
from interior import stove
from pond import mill, lantern
from attic import ladder
from winter import snow_field, bare_tree, winter_hat
from advent import (star_cookie, heart_cookie, moon_cookie, crumbs, cookie_tin, tray, tit, bird_print, peck_marks,
                    frost, bird_feeder, seed_star, mousetrap, paw_trail, big_boots, ribbon_spool, piping_bag,
                    pillow_crumbs, star_spruce, club_photo7)
from tracks import apple
from letter import hand_text

S = 2.2


def _fill(b, g, alpha=None):
    fill([(b.x, b.y), (b.x + b.w, b.y), (b.x + b.w, b.y + b.h), (b.x, b.y + b.h)], g, alpha)


def jar(x, y, h=14, g=P.JAM):
    sh_(rrect(x - 5, y, 10, h, 2), P.JAR)
    clip_fill(rrect(x - 5, y, 10, h, 2), [(x - 6, y), (x + 6, y), (x + 6, y + h*0.7), (x - 6, y + h*0.7)], g)
    stroke(rrect(x - 5, y, 10, h, 2), BG, closed=True)


# ------------------------------------------------------------------ rooms
def room_kitchen(b):
    _fill(b, P.KITCHEN_WALL)
    fy = b.Y(0.27)
    for yy in range(int(fy), int(b.h), 22): stroke([(0, yy), (b.w, yy)], BG*0.4, g=0.7)
    for xx in range(0, int(b.w), 22): stroke([(xx, fy), (xx, b.h)], BG*0.4, g=0.7)
    shape([(-5, -5), (b.w + 5, -5), (b.w + 5, fy), (-5, fy)], P.FLOOR, BG)
    for k in range(1, 8): s_([(k*b.w/8 - 30, -5), (k*b.w/8, fy)], BG*0.4)
    stove(b.X(0.02), b.X(0.17), fy - 4, b.Y(0.62))
    # the window: frosty panes onto the snowy garden; the sill outside (the tray is a prop)
    x0, x1, y0, y1 = b.X(0.3), b.X(0.56), b.Y(0.45), b.Y(0.9)
    shape([(x0 - 10, y0 - 10), (x1 + 10, y0 - 10), (x1 + 10, y1 + 10), (x0 - 10, y1 + 10)], P.DOOR_FRAME, BG)
    shape([(x0, y0), (x1, y0), (x1, y1), (x0, y1)], P.SNOW_SKY, BG)
    fill([(x0, y0), (x1, y0), (x1, y0 + (y1 - y0)*0.32), (x0, y0 + (y1 - y0)*0.36)], P.SNOW)
    for k, bx in enumerate((0.25, 0.75)): bare_tree(x0 + (x1 - x0)*bx, y0 + (y1 - y0)*0.3, 0.9, seed=k + 2)
    fill([(x0, y0), (x1, y0), (x1, y0 + 14), (x0, y0 + 14)], P.SNOW)
    frost(x0, y0, x1, y1)
    s_([((x0 + x1)/2, y0 + 16), ((x0 + x1)/2, y1)], BG*3, g=P.DOOR_FRAME)
    s_([(x0, y0 + (y1 - y0)*0.62), (x1, y0 + (y1 - y0)*0.62)], BG*3, g=P.DOOR_FRAME)
    shape([(x0 - 20, y0 - 12), (x1 + 20, y0 - 12), (x1 + 20, y0 - 4), (x0 - 20, y0 - 4)], P.SILL, BG)
    # the table under the window
    form([(b.X(0.26), fy + 70), (b.X(0.6), fy + 70), (b.X(0.6), fy + 80), (b.X(0.26), fy + 80)], P.TABLE, w=BG, sh=0)
    for lx in (b.X(0.28), b.X(0.57)): sh_([(lx, fy - 8), (lx + 8, fy - 8), (lx + 8, fy + 70), (lx, fy + 70)], P.TABLE)
    # the pantry shelves (the tin is a prop)
    for k, sy in enumerate((0.5, 0.72)):
        y_ = b.Y(sy)
        shape([(b.X(0.66), y_ - 6), (b.X(0.86), y_ - 6), (b.X(0.86), y_), (b.X(0.66), y_)], P.SILL, BG)
        if k == 1:
            for i in range(5): jar(b.X(0.68) + i*36, y_, 26 + (i % 2)*8, (P.JAM, 0.75, 0.55)[i % 3])
    # the door out
    dx0, dx1 = b.X(0.88), b.X(0.98)
    shape([(dx0 - 6, fy - 4), (dx1 + 6, fy - 4), (dx1 + 6, b.Y(0.86)), (dx0 - 6, b.Y(0.86))], P.DOOR_FRAME, BG)
    shape([(dx0, fy - 4), (dx1, fy - 4), (dx1, b.Y(0.84)), (dx0, b.Y(0.84))], P.DOOR, BG)
    shape(ell(dx0 + 10, b.Y(0.5), 4, 4, 12), 0.85, LINE*0.6)
    for k in range(5):
        a = math.radians(90 + k*72)
        star(b.X(0.22) + math.cos(a)*30, b.Y(0.82) + math.sin(a)*30, 7, P.KRASLICE_YELLOW)
    stroke(ell(b.X(0.22), b.Y(0.82), 34, 34, 30), 3, closed=True, g=P.SPRUCE)


def room_mill(b):
    sky(b, P.SNOW_SKY)
    gy = b.Y(0.32)
    fill([(-5, b.Y(0.7)), (b.w + 5, b.Y(0.7)), (b.w + 5, b.h + 5), (-5, b.h + 5)], P.NOV_SKY)
    hills(b, gy + b.h*0.06, 16, P.SNOW_HILL, 3)
    snow_field(b, gy, 6)
    mill(b.X(0.17), gy + 2, 2.6)
    stars = [(-0.6, 0.1, False), (0.55, 0.15, False), (-0.3, 0.38, False), (0.3, 0.42, True), (-0.45, 0.62, True),
             (0.2, 0.68, False), (0.0, 0.88, False)]
    star_spruce(b.X(0.6), gy - 4, 1.8, stars)
    bare_tree(b.X(0.92), gy - 6, 1.6, seed=8)


ROOMS = [("kitchen6", room_kitchen), ("mill6", room_mill)]


# ------------------------------------------------------------------ slides: the tin, counted
def _tin_slide(stars, hearts, moons):
    def draw(b):
        _fill(b, 0.82)
        cookie_tin(b.X(0.06), b.Y(0.1), b.w*0.62, stars, hearts, moons, lid=False)
        x = b.X(0.72)
        for k, (fn, n) in enumerate(((lambda xx, yy: star_cookie(xx, yy, 1.6), stars),
                                     (lambda xx, yy: heart_cookie(xx, yy, 1.6), hearts),
                                     (lambda xx, yy: moon_cookie(xx, yy, 1.6), moons))):
            yy = b.Y(0.72) - k*b.h*0.22
            fn(x, yy)
            hand_text(x + 30, yy - 18, 200, f"{n}", "SHB", 48, g=0.15, align="left")
    return draw


SLIDES = [("tin12", _tin_slide(12, 12, 12)), ("tin5", _tin_slide(5, 11, 12)), ("tin3", _tin_slide(3, 11, 12))]


# ------------------------------------------------------------------ characters
def _chars():
    out = []
    out.append(("deda_boots", 150, 300, lambda b: deda(b.w/2, 8, S, mood="worried", right="chin", shadow=False)))
    out.append(("deda_caught", 160, 300, lambda b: deda(b.w/2, 8, S, mood="grin", right="up", shadow=False)))
    out.append(("babicka_ribbon", 150, 270, lambda b: babicka(b.w/2, 8, S, mood="surprised", right="front", shadow=False,
                                                              item=lambda x, y: ribbon_spool(x, y - 6, 1.6))))
    out.append(("hankaw_cry", 110, 200, lambda b: (hanka(b.w/2, 8, S, mood="sad", shadow=False),
                                                   winter_hat(b.w/2, 8, S, "hanka", P.HANKA_WINTER_HAT))))
    out.append(("hankaw_photo", 160, 200, lambda b: (hanka(b.w/2 - 10, 8, S, mood="grin", right="front", shadow=False,
                                                           item=lambda x, y: club_photo7(x - 20, y - 26, 60, 40)),
                                                     winter_hat(b.w/2 - 10, 8, S, "hanka", P.HANKA_WINTER_HAT))))
    return out


CHARACTERS = _chars()


# ------------------------------------------------------------------ props
PROPS = [
    ("tray_pecked", 160, 60, lambda b: tray(10, 10, 140, 6, True)),
    ("tray_whole", 160, 60, lambda b: tray(10, 10, 140, 6, False)),
    ("tits", 200, 70, lambda b: (tit(50, 10, 1.6, kind="great", pose="peck"), tit(140, 10, 1.6, flip=True, kind="blue"))),
    ("bird_prints", 140, 30, lambda b: [bird_print(15 + i*25, 12 + (i % 2)*5, 1.4, 10) for i in range(5)]),
    ("tin_shelf", 130, 70, lambda b: cookie_tin(10, 8, 110, 12, 12, 12, lid=True)),
    ("paws_flour", 300, 70, lambda b: paw_trail(15, 20, b.w - 20, 40, 6, 1.4)),
    ("mousetrap", 90, 40, lambda b: mousetrap(b.w/2, 8, 1.6, bait=False)),
    ("deda_boots_needles", 140, 110, lambda b: big_boots(b.w/2, 8, 1.4, needles=True, ribbon=True)),
    ("piping_bag", 80, 50, lambda b: piping_bag(b.w/2, b.h/2, 1.6, rot=20)),
    ("feeder", 140, 220, lambda b: bird_feeder(b.w/2, 8, 2.4, birds=2)),
    ("new_stars", 200, 140, lambda b: (star_cookie(50, 70, 2.2), star_cookie(150, 60, 2.2),
                                       hand_text(10, 18, 80, "ALICA", "SHB", 13, g=0.2),
                                       hand_text(110, 8, 80, "HANKA", "SHB", 13, g=0.2))),
    ("seed_stars", 220, 120, lambda b: [seed_star(30 + k*55, 20 + (k % 2)*30, 1.6) for k in range(4)]),
    ("ladder6", 60, 260, lambda b: ladder(b.w/2, 4, 250, 34)),
    ("club_photo7", 170, 120, lambda b: club_photo7(10, 10, 150, 100)),
]


# ------------------------------------------------------------------ minigame tiles (64 x 64)
def _branch(b):
    fill([(0, 0), (b.w, 0), (b.w, b.h), (0, b.h)], P.SPRUCE)
    for k in range(5):
        y = 8 + k*12
        stroke([(4, y), (60, y + 4)], LINE*0.6, g=P.SPRUCE_LIGHT)
        for x in range(8, 60, 8): stroke([(x, y + 1), (x - 3, y - 4)], LINE*0.4, g=P.SPRUCE_LIGHT)
    fill([(0, b.h - 6), (b.w, b.h - 4), (b.w, b.h), (0, b.h)], P.SNOW)


def _bird(x, y, s, back, belly, cap, beak=0.15, bib=None, eye_ring=None):
    """a small round songbird facing right for "Kdo co zobe?"; (x, y) = its feet"""
    with T(x, y, s):
        for lx in (-2, 2):
            stroke([(lx, 0), (lx, 5)], LINE*0.6, g=0.3, taper=False)
        shape([(-9, 13), (-20, 8), (-19, 4), (-8, 9)], back, LINE*0.7)
        body = ell(0, 12, 11, 8.5, 28)
        shape(body, back, LINE*0.8)
        shape(ell(2.5, 10, 7, 6, 24), belly, LINE*0.5)
        shape(ell(8, 21, 6.5, 6.2, 24), back, LINE*0.8)
        shape(bez((2.2, 22), (4, 28.5), (12, 28.5), (14.2, 22)) + [(8, 23)], cap, LINE*0.5)
        if bib is not None:
            shape(ell(11, 15.5, 3, 3.2, 16), bib, LINE*0.3)
        shape([(14, 22), (19, 20.5), (14, 19)], beak, LINE*0.5)
        if eye_ring is not None:
            shape(ell(10.5, 22, 1.9, 1.9, 12), eye_ring, LINE*0.3)
        dot(10.5, 22, 1.1, 0.0)


def _fat_ball(b):
    with T(b.w/2, b.h/2 - 2, 1):
        stroke([(0, 18), (0, 26)], LINE*0.8, g=P.FAT_NET)
        ball = ell(0, 0, 18, 18, 32)
        shape(ball, P.FAT_BALL, LINE)
        C.saveState(); C.clipPath(poly(ball), stroke=0, fill=0)
        for k in range(-24, 25, 8):
            stroke([(k - 20, -20), (k + 20, 20)], LINE*0.5, g=P.FAT_NET, taper=False)
            stroke([(k - 20, 20), (k + 20, -20)], LINE*0.5, g=P.FAT_NET, taper=False)
        C.restoreState()


def _rowan(b):
    stroke([(b.w/2, 56), (b.w/2 - 2, 40)], LINE*0.8, g=0.35)
    shape(bez((b.w/2, 50), (b.w/2 + 12, 58), (b.w/2 + 22, 54), (b.w/2 + 24, 48)) + [(b.w/2 + 6, 49)], P.FAT_NET, LINE*0.6)
    r = random.Random(6)
    for _ in range(11):
        x, y = b.w/2 + r.uniform(-14, 14), 24 + r.uniform(-10, 12)
        stroke([(b.w/2 - 2, 40), (x, y + 4)], LINE*0.3, g=0.35)
        shape(ell(x, y, 4.2, 4.2, 14), P.BERRY, LINE*0.5)


def _seeds(b):
    shape(bez((8, 12), (16, 34), (48, 34), (56, 12)) + [(8, 12)], P.SEEDS, LINE*0.8)
    r = random.Random(4)
    for _ in range(16):
        x, y = r.uniform(16, 48), r.uniform(15, 27)
        shape(ell(x, y, 2.4, 1.3, 10), P.HAY, LINE*0.25)


def _card(b):
    fill([(0, 0), (b.w, 0), (b.w, b.h), (0, b.h)], P.PAPER)


def _hang(fn):
    def draw(b):
        stroke([(b.w/2, b.h - 2), (b.w/2, b.h/2 + 16)], 1.6, g=P.RIBBON)
        fn(b.w/2, b.h/2 - 2)
    return draw


MG = [
    ("branch", _branch),
    ("orn_star", _hang(lambda x, y: star_cookie(x, y, 2.4))),
    ("orn_heart", _hang(lambda x, y: heart_cookie(x, y, 2.4))),
    ("orn_moon", _hang(lambda x, y: moon_cookie(x, y, 2.4))),
    ("orn_seed", _hang(lambda x, y: seed_star(x, y - 6, 1.9, string=False))),
    ("who_mice", lambda b: (_card(b), dormouse(b.w/2 - 14, 16, 1.4))),
    ("who_hanka6", lambda b: (_card(b), hanka(b.w/2, -40, 1.2, mood="worried", shadow=False),
                              winter_hat(b.w/2, -40, 1.2, "hanka", P.HANKA_WINTER_HAT))),
    ("who_birds", lambda b: (_card(b), tit(b.w/2 - 4, 18, 1.5))),
    ("who_deda6", lambda b: (_card(b), deda(b.w/2, -76, 0.95, mood="grin", shadow=False))),
    ("bird_sykorka", lambda b: (_card(b), tit(b.w/2 - 2, 14, 1.7))),
    ("bird_hyl", lambda b: (_card(b), _bird(b.w/2 - 2, 10, 1.45, P.BULLFINCH_BACK, P.BULLFINCH_CHEST, P.BLACKBIRD, P.BLACKBIRD))),
    ("bird_kos", lambda b: (_card(b), _bird(b.w/2 - 2, 10, 1.5, P.BLACKBIRD, P.BLACKBIRD, P.BLACKBIRD, P.BLACKBIRD_BEAK,
                                              eye_ring=P.BLACKBIRD_BEAK))),
    ("bird_vrabec", lambda b: (_card(b), _bird(b.w/2 - 2, 10, 1.4, P.SPARROW, P.SPARROW_BELLY, P.SPARROW_DARK, 0.3,
                                                 bib=P.SPARROW_DARK))),
    ("food_lojova", _fat_ball), ("food_jerabiny", _rowan), ("food_jablko", lambda b: apple(b.w/2, b.h/2 - 4, 2.2)),
    ("food_zrni", _seeds),
    ("clue_trap", lambda b: (_card(b), mousetrap(b.w/2, 20, 1.2, bait=False))),
    ("clue_crumbs", lambda b: (_card(b), crumbs(b.w*0.3, b.h*0.55, 18, 8, 9, P.CHOCOLATE, 3, 1.4),
                               star_cookie(b.w*0.68, b.h*0.45, 1.3))),
    ("clue_needles", lambda b: (_card(b), big_boots(b.w/2, 8, 0.8, needles=True, ribbon=True))),
    ("clue_photo7", lambda b: (_card(b), club_photo7(6, 14, 52, 36))),
]


def COVER(s):
    _fill(s, P.KITCHEN_WALL)
    x0, x1, y0, y1 = s.X(0.12), s.X(0.88), s.Y(0.4), s.Y(0.85)
    shape([(x0, y0), (x1, y0), (x1, y1), (x0, y1)], P.SNOW_SKY, BG)
    fill([(x0, y0), (x1, y0), (x1, y0 + 12), (x0, y0 + 12)], P.SNOW)
    tray(x0 + 8, y0 + 2, (x1 - x0)*0.6, 5, True)
    tit(x1 - 26, y0 + 8, 1.3, flip=True)
    frost(x0, y0, x1, y1)
    alica(s.X(0.3), s.Y(0.02), 0.85, mood="think", right="lens", lens=True, look=(1, 0.4), shadow=False)
    hanka(s.X(0.72), s.Y(0.02), 0.85, flip=True, mood="grin", shadow=False)
    star_cookie(s.X(0.86), s.Y(0.12), 1.4)
