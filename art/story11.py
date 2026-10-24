"""Game art for story 11 "Kam mizí vajíčka?": the chalupa yard at Easter (henhouse, hen run with the gap under
the wire, the barn), inside the henhouse, inside the barn (the bale wall, the dark gap); the hens and Kropenatka,
the eggs, the clues, the nest, the chicks, the kraslice; the bale tiles of "Balíky slámy" and the suspect cards."""
import math, random
import lib
from lib import ell, bez, rrect
import palette as P
from style3 import *
from style3 import C
from chars3 import star, tonda, magpie
from scenes3 import BG, s_, sh_, sky
from tracks import liska, dog_print, fox_print
from skola import jezek, hay_wisp, hobliny
from velikonoce import (egg_pts, egg, kraslice, egg_basket, slepice, kropenatka, nest, kohout, kure, pirko, hen_print, hen_trail,
                        run_fence, balik, stodola, barn_inside, kurnik_inside, dvur, straci_hnizdo, egg_cracked, foil_ball,
                        dye_pot, onion_skins, candle)
from letter import hand_text

S = 2.2


def _fill(b, g, alpha=None):
    fill([(b.x, b.y), (b.x + b.w, b.y), (b.x + b.w, b.y + b.h), (b.x, b.y + b.h)], g, alpha)


# ------------------------------------------------------------------ rooms
def room_yard(b):
    gy = dvur(b, 0.36, 111, house_x=0.12, house_s=2.6, henhouse_x=0.42, henhouse_s=2.6, barn_x=0.84, barn_s=2.1,
              trees=((0.62, 1.6),), bushes=())
    run_fence(b.X(0.27), b.X(0.6), gy - 16, 70, b.X(0.56))


def room_henhouse(b):
    kurnik_inside(b, 0.27)


def room_barn(b):
    barn_inside(b, 0.27, 0.66, light=True, dark=0.15)


ROOMS = [("yard11", room_yard), ("henhouse11", room_henhouse), ("barn11", room_barn)]


# ------------------------------------------------------------------ slides
def slide_magpie(b):
    _fill(b, P.SPRING_SKY)
    r = min(b.w*0.215, b.h*0.42)
    eyes = [(b.X(0.5) + sx*(r + 10), b.Y(0.5)) for sx in (-1, 1)]
    C.saveState()
    pth = C.beginPath()
    for ex, ey in eyes:
        E = ell(ex, ey, r, r, 48); pth.moveTo(*E[0])
        for q in E[1:]: pth.lineTo(*q)
        pth.close()
    C.clipPath(pth, stroke=0, fill=0)
    straci_hnizdo(b.X(0.5), b.Y(0.3), 4.6)
    C.restoreState()
    for ex, ey in eyes: stroke(ell(ex, ey, r, r, 48), LINE*3, closed=True)


def slide_chicks(b):
    gy = dvur(b, 0.4, 117, henhouse_x=0.82, henhouse_s=2.2)
    kropenatka(b.X(0.5), b.Y(0.08), 3.6)
    for k, (fx, fy) in enumerate(((0.36, 0.04), (0.41, 0.1), (0.6, 0.05), (0.64, 0.11), (0.68, 0.03), (0.44, 0.02),
                                  (0.3, 0.1), (0.72, 0.08))):
        kure(b.X(fx), b.Y(fy), 3.0, flip=k % 2 == 0, pose="peck" if k % 3 == 0 else "stand")
    hand_text(0, b.Y(0.88), b.w, "O tři týdny později…", "SHB", 40, g=0.2)


SLIDES = [("magpie_nest11", slide_magpie), ("chicks11", slide_chicks)]


# ------------------------------------------------------------------ characters
CHARACTERS = [
    ("tonda_eggs", 170, 250, lambda b: tonda(b.w/2, 8, S, mood="happy", right="front", shadow=False,
                                             item=lambda x, y: egg_basket(x + 4, y - 18, 1.0, 9))),
    ("verka_eggs", 180, 290, lambda b: __import__("pond").verka_old(b.w/2, 8, S, mood="happy", right="front", shadow=False,
                                                                   stick=False, item=lambda x, y: egg_basket(x - 4, y - 18, 1.0, 9))),
    ("babicka_basket", 170, 270, lambda b: __import__("chars3").babicka(b.w/2, 8, S, mood="worried", right="front", shadow=False,
                                                                        item=lambda x, y: egg_basket(x + 4, y - 18, 1.0, 4))),
    ("hanka_torch_low", 150, 200, lambda b: hanka(b.w/2 - 20, 8, S, monkey=False, right="front", mood="wow", shadow=False,
                                                  item=lambda x, y: __import__("chars3").torch(x, y, 10))),
]


# ------------------------------------------------------------------ props
PROPS = [
    ("hens11", 380, 120, lambda b: [slepice(30 + k*52, 8 + (k % 2)*10, 1.6, flip=k > 3, pose="peck" if k % 3 == 0 else "stand",
                                            who=k % 7) for k in range(7)]),
    ("kropenatka_puff", 120, 100, lambda b: kropenatka(b.w/2, 8, 2.6, flip=True, puff=True, straw=True)),
    ("eggs7", 300, 60, lambda b: [egg(20 + k*40, 26, 1.8) for k in range(7)]),
    ("feather_prints", 240, 70, lambda b: (pirko(30, 30, 2.0, -40), hen_trail([(60, 20), (230, 34)], 5, 1.6))),
    ("dog_prints11", 220, 60, lambda b: [dog_print(30 + k*50, 26 + (k % 2)*10, 1.6, 80) for k in range(4)]),
    ("nest11", 200, 120, lambda b: nest(b.w/2, 10, 3.2)),
    ("nest11_eggs", 200, 120, lambda b: nest(b.w/2, 10, 3.2, hen_on=False)),
    ("bales_gap", 200, 140, lambda b: (balik(10, 8, 80, 50, 1), balik(110, 8, 80, 50, 2), balik(50, 64, 90, 50, 3))),
    ("eggs_basket", 120, 110, lambda b: egg_basket(b.w/2, 8, 2.2, 9)),
    ("kraslice_row", 300, 70, lambda b: [kraslice(30 + k*48, 34, 2.0, (k*13) % 30 - 15, kind) for k, kind in
                                          enumerate(("onion", "wax", "marker", "opicka", "star", "stripes"))]),
    ("rooster", 140, 150, lambda b: kohout(b.w/2, 8, 2.6)),
]


# ------------------------------------------------------------------ minigame tiles (64 x 64)
def _floor(b):
    fill([(0, 0), (b.w, 0), (b.w, b.h), (0, b.h)], P.BARN_DARK)
    r = random.Random(4)
    for _ in range(8):
        x, y = r.uniform(4, 60), r.uniform(4, 60)
        stroke([(x, y), (x + r.uniform(-8, 8), y + r.uniform(-3, 3))], 0.8, g=P.STRAW)


def _wall(b):
    fill([(0, 0), (b.w, 0), (b.w, b.h), (0, b.h)], P.BARN)
    for x in (0, 16, 32, 48): stroke([(x, 0), (x, 64)], BG, g=0.3)


def _gap(b):
    _floor(b)
    nest(b.w/2, 10, 1.0)


def _card(b):
    fill([(0, 0), (b.w, 0), (b.w, b.h), (0, b.h)], P.PAPER)


def _dye_egg(b, kind):
    """a dyed egg for "Kraslice podle vzoru": colour plus a simple mark, so the rows read without colour too"""
    g = {"r": P.DYE_RED, "y": P.DYE_YELLOW, "b": P.DYE_BLUE, "g": P.DYE_GREEN, "o": P.ONION_DYE}[kind]
    with T(b.w/2, b.h/2 + 2, 3.4):
        e = egg_pts(0, 0, 7)
        shape(e, g, LINE*0.5)
        C.saveState(); C.clipPath(poly(e), stroke=0, fill=0)
        if kind == "r":
            for dx, dy in ((-2.4, 1.6), (2.4, 1.6), (0, -2.2)):
                dot(dx, dy, 1.1, P.PAPER)
        elif kind == "y":
            stroke([(-6, 0), (6, 0)], LINE*0.5, g=P.PAPER, taper=False)
        elif kind == "b":
            stroke([(-6, -1), (-3, 1.5), (0, -1), (3, 1.5), (6, -1)], LINE*0.35, g=P.PAPER, taper=False)
        elif kind == "g":
            for yy in (-2.5, 2.5):
                stroke([(-6, yy), (6, yy)], LINE*0.35, g=P.PAPER, taper=False)
        C.restoreState()
        stroke(bez((-3.2, 3.5), (-3.8, 1), (-3.6, -1.5), (-2.6, -3.5)), LINE*0.25, g=1.0, alpha=0.7)


def _egg_blank(b):
    with T(b.w/2, b.h/2 + 2, 3.4):
        stroke(egg_pts(0, 0, 7), LINE*0.35, closed=True, g=0.55)


def _egg_nest(b):
    shape(ell(b.w/2, 14, 28, 9, 30), P.NEST_STRAW, LINE*0.8)
    r = random.Random(3)
    for _ in range(10):
        x = r.uniform(8, 56)
        stroke([(x - 6, 12 + r.uniform(-3, 3)), (x + 6, 14 + r.uniform(-3, 3))], LINE*0.4, g=P.STRAW_DARK)


MG = [(f"egg_{k}", lambda b, k=k: _dye_egg(b, k)) for k in "rybgo"] + [("egg_blank", _egg_blank), ("egg_nest", _egg_nest)] + [
    ("bale_floor", _floor), ("bale_wall", _wall), ("bale_gap", _gap),
    ("bale_h", lambda b: balik(2, 10, 60, 44, 1)), ("bale_v", lambda b: balik(10, 2, 44, 60, 2)),
    ("who_fox11", lambda b: (_card(b), liska(b.w/2 + 4, 10, 0.75))),
    ("who_magpie11", lambda b: (_card(b), magpie(b.w/2 - 4, 18, 1.4, item=lambda x, y: foil_ball(x + 3, y, 0.6)))),
    ("who_tonda11", lambda b: (_card(b), tonda(b.w/2, -60, 1.05, mood="happy", shadow=False))),
    ("who_jezek11", lambda b: (_card(b), jezek(b.w/2, 16, 1.2))),
    ("who_kropenatka", lambda b: (_card(b), kropenatka(b.w/2, 8, 1.6, puff=True, straw=True))),
    ("clue_noshells", lambda b: (_card(b), egg_cracked(b.w/2, 22, 1.6, chick=False),
                                 stroke([(10, 10), (54, 54)], 3, g=P.CRAYON_RED), stroke([(54, 10), (10, 54)], 3, g=P.CRAYON_RED))),
    ("clue_straw", lambda b: (_card(b), hay_wisp(b.w/2, b.h/2, 2.6))),
    ("clue_feather", lambda b: (_card(b), pirko(b.w/2 - 8, b.h/2 - 4, 1.6, -30), hen_print(b.w/2 + 14, b.h/2 + 8, 1.6))),
    ("clue_kvok", lambda b: (_card(b), hand_text(0, 24, 64, "KVOK", "SHB", 16, g=0.2))),
]


def COVER(s):
    gy = dvur(s, 0.38, 113, henhouse_x=0.25, henhouse_s=0.9, barn_x=0.78, barn_s=0.9)
    egg_basket(s.X(0.5), s.Y(0.06), 1.2, 6)
    alica(s.X(0.3), s.Y(0.02), 0.85, mood="think", right="lens", lens=True, look=(1, 0.3), shadow=False)
    kropenatka(s.X(0.72), s.Y(0.04), 1.4, flip=True, puff=True)
