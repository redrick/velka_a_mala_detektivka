"""Game art for story 7 "Joeyho velký den": the snowy garden with the feeder, the woodshed and the kids' snow
fort, the forest at the forester's lodge; the hajný; Joey's morning slides (he tells it); the stash, the
glove, the ring, the foil; the tiles of "Čmuchej!" and the "where is the ring?" cards."""
import math, random
import lib
from lib import ell, bez, rrect
import palette as P
from style3 import *
from style3 import C
from chars3 import star, babicka, deda, tonda, magpie
from scenes3 import BG, s_, sh_, sky, hills
from winter import snowy_house, bare_tree, snow_fence, snow_field, snowfall, winter_hat, betka
from advent import bird_feeder
from joeyday import (bone, ring, ring_big, smell_trail, babi_glove, shovel, snow_pile, throw_arc, snow_block, snow_fort,
                     stash, foil, woodshed, hajny)
from tracks import winter_forest, krmelec, spruce
from letter import hand_text

S = 2.2


def _fill(b, g, alpha=None):
    fill([(b.x, b.y), (b.x + b.w, b.y), (b.x + b.w, b.y + b.h), (b.x, b.y + b.h)], g, alpha)


def _garden(b, gy, fort=True, pile=False):
    sky(b, P.SNOW_SKY)
    hills(b, gy + b.h*0.06, 16, P.SNOW_HILL, 71)
    snow_field(b, gy, 71)
    snowy_house(b.X(0.13), gy - 4, 3.0)
    bare_tree(b.X(0.48), gy - 6, 2.2, seed=72)
    snow_fence(b.X(0.3), b.X(1.02), gy - 2, 80, 26)
    woodshed(b.X(0.9), gy - 4, 2.0)
    bird_feeder(b.X(0.34), b.Y(0.2), 2.4)
    if pile: snow_pile(b.X(0.64), b.Y(0.2), 260, 90)
    if fort: snow_fort(b.X(0.64), b.Y(0.17), 1.9)


# ------------------------------------------------------------------ rooms
def room_garden(b):
    _garden(b, b.Y(0.36))


def room_forest(b):
    gy = b.Y(0.34)
    winter_forest(b, gy, 7, trees=((0.06, 1.8), (0.95, 2.0)))
    snowy_house(b.X(0.26), gy - 4, 2.4)
    krmelec(b.X(0.7), gy - 4, 2.2, hay=True, food=False)
    spruce(b.X(0.5), gy - 6, 1.3, seed=9)


ROOMS = [("garden7", room_garden), ("forest7", room_forest)]


# ------------------------------------------------------------------ slides: Joey tells the morning
def slide_feeder(b):
    _garden(b, b.Y(0.3), fort=False)
    babicka(b.X(0.4), b.Y(0.05), 1.7, mood="worried", right="front", shadow=False)
    babi_glove(b.X(0.27), b.Y(0.42), 1.8, rot=10)
    joey(b.X(0.62), b.Y(0.05), 1.7, collar=False, shadow=False)


def slide_glove(b):
    _garden(b, b.Y(0.3), fort=False)
    joey(b.X(0.55), b.Y(0.08), 2.0, collar=False, shadow=False)
    babi_glove(b.X(0.55) + 88, b.Y(0.08) + 62, 1.4, rot=-20)
    for k in range(4): stroke([(b.X(0.4) - k*24, b.Y(0.2) + k*10), (b.X(0.32) - k*24, b.Y(0.2) + k*10)], 3, g=0.4)


def slide_shovel(b):
    _garden(b, b.Y(0.3), fort=False, pile=True)
    deda(b.X(0.34), b.Y(0.05), 1.7, mood="happy", right="front", shadow=False,
         item=lambda x, y: shovel(x, y - 20, 1.6, rot=-30))
    throw_arc(b.X(0.42), b.Y(0.35), b.X(0.62), b.Y(0.3))


def slide_fort(b):
    _garden(b, b.Y(0.3), fort=True)
    alica(b.X(0.2), b.Y(0.04), 1.4, mood="grin", shadow=False)
    winter_hat(b.X(0.2), b.Y(0.04), 1.4, "alica", P.ALICA_WINTER_HAT)
    betka(b.X(0.86), b.Y(0.04), 1.5, mood="grin", shadow=False)
    tonda(b.X(0.42), b.Y(0.04), 1.4, mood="grin", right="up", shadow=False)


SLIDES = [("j_feeder", slide_feeder), ("j_glove", slide_glove), ("j_shovel", slide_shovel), ("j_fort", slide_fort)]


# ------------------------------------------------------------------ characters
def _chars():
    out = []
    for mood in ("happy", "talk", "surprised", "grin"):
        out.append((f"hajny_{mood}", 160, 310, lambda b, m=mood: hajny(b.w/2, 8, S, mood=m, shadow=False)))
    out.append(("hajny_walk", 160, 310, lambda b: hajny(b.w/2, 8, S, legs="walk", shadow=False)))
    out.append(("hajny_foil", 180, 310, lambda b: hajny(b.w/2, 8, S, mood="grin", right="front", shadow=False,
                                                       item=lambda x, y: foil(x + 4, y, 1.4))))
    out.append(("joey_sad", 180, 140, lambda b: joey(b.w/2 - 5, 8, S, mood="sad", shadow=False, collar=False)))
    out.append(("babicka_ring", 160, 270, lambda b: babicka(b.w/2, 8, S, mood="grin", right="up", shadow=False,
                                                            item=lambda x, y: ring(x, y + 4, 1.6))))
    return out


CHARACTERS = _chars()


# ------------------------------------------------------------------ props
PROPS = [
    ("stash_open", 200, 80, lambda b: stash(b.w/2, 8, 60, 18)),
    ("glove_found", 70, 70, lambda b: babi_glove(b.w/2, b.h/2, 1.6, rot=20)),
    ("ring_glint", 80, 80, lambda b: ring_big(b.w/2, b.h/2, 1.4)),
    ("foil_ball", 50, 50, lambda b: foil(b.w/2, b.h/2, 1.8)),
    ("magpie7", 110, 80, lambda b: magpie(b.w/2 + 10, 12, 1.8, item=lambda x, y: foil(x + 3, y, 0.6))),
    ("fort_open", 240, 120, lambda b: snow_fort(b.w/2, 8, 1.2, removed=((1, 2), (1, 3), (2, 3)))),
]


# ------------------------------------------------------------------ minigame tiles (64 x 64)
def _snow(b):
    fill([(0, 0), (b.w, 0), (b.w, b.h), (0, b.h)], P.SNOW)
    r = random.Random(4)
    for _ in range(4):
        x, y = r.uniform(6, 58), r.uniform(6, 58)
        stroke(bez((x - 5, y), (x - 2, y + 2), (x + 2, y + 2), (x + 5, y)), BG*0.6, g=0.82)


def _block(b):
    fill([(0, 0), (b.w, 0), (b.w, b.h), (0, b.h)], P.SNOW_SHADE if hasattr(P, "SNOW_SHADE") else 0.9)
    snow_block(3, 4, 58, 54)


def _dug(b):
    _snow(b)
    fill(ell(b.w/2, b.h/2, 24, 18, 24), P.SNOW_SHADE if hasattr(P, "SNOW_SHADE") else 0.85)
    stroke(ell(b.w/2, b.h/2, 24, 18, 24), BG, closed=True, g=0.55)


def _card(b):
    fill([(0, 0), (b.w, 0), (b.w, b.h), (0, b.h)], P.PAPER)


def _paw(b):
    fill(ell(b.w/2, b.h/2 - 6, 11, 9, 20), 0.25)
    for dx, dy in ((-12, 8), (-4, 14), (4, 14), (12, 8)):
        fill(ell(b.w/2 + dx, b.h/2 + dy, 4.5, 5.5, 14), 0.25)


MG = [
    ("sniff_snow", _snow), ("sniff_block", _block), ("sniff_dug", _dug), ("paw", _paw),
    ("find_bone", lambda b: (_dug(b), bone(b.w/2, b.h/2, 1.6, rot=20))),
    ("find_glove", lambda b: (_dug(b), babi_glove(b.w/2, b.h/2, 1.2, rot=10))),
    ("find_ring", lambda b: (_dug(b), ring_big(b.w/2, b.h/2, 0.55))),
    ("where_feeder", lambda b: (_card(b), bird_feeder(b.w/2, 4, 0.9))),
    ("where_stash", lambda b: (_card(b), stash(b.w/2, 14, 16, 6))),
    ("where_magpie", lambda b: (_card(b), magpie(b.w/2 - 4, 18, 1.4, item=lambda x, y: foil(x + 3, y, 0.5)))),
    ("where_fort", lambda b: (_card(b), snow_fort(b.w/2, 10, 0.3))),
    ("clue_glove7", lambda b: (_card(b), babi_glove(b.w/2, b.h/2, 1.3))),
    ("clue_shovel", lambda b: (_card(b), shovel(b.w/2, 8, 0.9, rot=-20))),
    ("clue_pile", lambda b: (_card(b), snow_pile(b.w/2, 14, 50, 22))),
    ("clue_foil", lambda b: (_card(b), foil(b.w/2, b.h/2, 1.6))),
]


def COVER(s):
    sky(s, P.SNOW_SKY)
    gy = s.Y(0.3)
    snow_field(s, gy, 5)
    snow_fort(s.X(0.62), s.Y(0.12), 0.45)
    joey(s.X(0.35), s.Y(0.05), 1.0, pose="sniff", collar=False, shadow=False)
    smell_trail([(s.X(0.4), s.Y(0.16)), (s.X(0.5), s.Y(0.22)), (s.X(0.6), s.Y(0.2))], 0.6)
    ring(s.X(0.7), s.Y(0.42), 1.4)
    snowfall(s, 14, 5, 1.2)
