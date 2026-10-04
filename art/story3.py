"""Game art for story 3 "Mapa ke starému rybníku": the pond and the mill rooms (the kitchen is
reused), Věrka and the fisherman as game characters, the props and the pictures for the two new
minigames (whose print is it? / who was it?)."""
import math
import lib
from lib import ell, rrect
import palette as P
from style3 import *
from chars3 import star, tonda, magpie
from scenes3 import BG, s_, sh_, tufts
from pond import (pond_bg, willow, stump, reeds, mill, bench, dredge_sign, duck, verka_old, rybar, badger,
                  hole, boot_print, stick_dot, bird_track, badger_track, star_stone, lantern, walking_stick,
                  spade, shoebox, treasure_tin, coin, spyglass, badge, whistle, marbles, club_photo,
                  picture_letter, mud_patch, jetty, full_map)

S = 2.2   # character scale, as in export_assets.py


# ------------------------------------------------------------------ rooms
def room_pond(b):
    fy = pond_bg(b, 0.36, 0.64, seed=4)
    mill(b.X(0.9), fy + 4, 0.5)
    for i, px in enumerate((0.44, 0.48, 0.52)):
        yy = b.Y(0.36) + 12 + (fy - b.Y(0.36))*0.3
        sh_([(b.X(px) - 3, yy - 4), (b.X(px) + 3, yy - 4), (b.X(px) + 3, yy + 10 + (i % 2)*5), (b.X(px) - 3, yy + 10 + (i % 2)*5)], P.BARK)
    duck(b.X(0.62), fy - 24, 0.9, flip=True); duck(b.X(0.68), fy - 18, 0.8)
    willow(b.X(0.12), b.Y(0.3), 1.35, seed=11)
    willow(b.X(0.36), b.Y(0.34), 0.95, seed=12)
    willow(b.X(0.8), b.Y(0.3), 1.25, seed=13)
    stump(b.X(0.56), b.Y(0.2), 1.1)
    for x in (0.25, 0.93):
        reeds(b.X(x), b.Y(0.34), 1.2, seed=int(x*100))
    tufts(b, b.Y(0.02), b.Y(0.3), 16, 7)


def room_mill(b):
    fy = pond_bg(b, 0.3, 0.7, seed=9, trees=True)
    mill(b.X(0.62), b.Y(0.3), 1.75, lantern_=False, wheel=True)
    bench(b.X(0.3), b.Y(0.12), 1.3)
    reeds(b.X(0.06), b.Y(0.28), 1.2, seed=5)
    duck(b.X(0.12), b.Y(0.45), 0.9)
    tufts(b, b.Y(0.02), b.Y(0.25), 12, 3)


ROOMS = [("pond", room_pond), ("mill_yard", room_mill)]


# ------------------------------------------------------------------ characters (feet at bottom centre)
def _chars():
    out = []
    for mood in ("happy", "talk", "surprised", "grin", "worried"):
        out.append((f"verka_{mood}", 140, 290, lambda b, m=mood: verka_old(b.w/2, 8, S, mood=m, shadow=False, stick=False)))
    out.append(("verka_walk", 140, 290, lambda b: verka_old(b.w/2, 8, S, legs="walk", shadow=False, stick=False)))
    for mood in ("happy", "talk", "surprised"):
        out.append((f"rybar_{mood}", 160, 320, lambda b, m=mood: rybar(b.w/2, 8, S, mood=m, shadow=False, rod=False)))
    out.append(("rybar_walk", 160, 320, lambda b: rybar(b.w/2, 8, S, shadow=False, rod=False)))
    out.append(("tonda_spade", 190, 250, lambda b: tonda(b.w/2, 8, S, mood="surprised", right="hold",
                                                          item=lambda x, y: spade(x + 3, y - 34, 1.0, rot=-8), shadow=False)))
    out.append(("tonda_box", 150, 250, lambda b: tonda(b.w/2, 8, S, mood="happy", right="front",
                                                        item=lambda x, y: shoebox(x - 4, y - 14, 0.55, open_=False), shadow=False)))
    return out


CHARACTERS = _chars()


# ------------------------------------------------------------------ props
def prints_group(b):
    mud_patch(b.w/2, b.h/2, b.w*0.46, b.h*0.4)
    boot_print(b.w*0.36, b.h*0.45, 1.3, -10); stick_dot(b.w*0.24, b.h*0.62, 3.2)
    boot_print(b.w*0.62, b.h*0.55, 1.3, 6); stick_dot(b.w*0.5, b.h*0.72, 3.2)


def burrow(b):
    arc = [(b.w/2 - (b.w/2 - 10)*math.cos(a/20*math.pi), 4 + 34*math.sin(a/20*math.pi)) for a in range(21)]
    shape(arc, P.MUD, BG)
    shape(ell(b.w/2, 16, 20, 13, 24), 0.08, BG)
    for dx in (-30, 30): badger_track(b.w/2 + dx, 8, 0.9)


PROPS = [
    ("map_big", 500, 340, lambda b: full_map(10, 10, 2.0)),
    ("star_stone", 90, 40, lambda b: star_stone(b.w/2, 10, 1.6)),
    ("hole_empty", 150, 60, lambda b: hole(b.w/2, 12, 50, 13)),
    ("prints_mud", 160, 90, prints_group),
    ("burrow", 120, 50, burrow),
    ("lantern_lit", 50, 60, lambda b: lantern(b.w/2, 6, 1.2, glow=False)),
    ("stick_lean", 40, 150, lambda b: walking_stick(b.w/2 - 6, 4, 125, rot=8)),
    ("shoebox_open", 110, 80, lambda b: shoebox(b.w/2, 6, 1.7, open_=True)),
    ("tin_open", 160, 110, lambda b: treasure_tin(b.w/2, 6, 2.0, open_=True)),
    ("coin", 60, 60, lambda b: coin(b.w/2, b.h/2, 18, shine=False)),
    ("coin_shine", 110, 110, lambda b: coin(b.w/2, b.h/2, 26, shine=True)),
    ("spyglass", 130, 40, lambda b: spyglass(8, b.h/2, 1.9)),
    ("club_photo", 130, 100, lambda b: club_photo(6, 6, 118, 88)),
    ("badge", 40, 40, lambda b: badge(b.w/2, b.h/2, 15)),
    ("picture_letter", 150, 110, lambda b: picture_letter(8, 6, 1.5)),
]

ITEMS = [
    ("letter_icon", 100, 80, lambda b: picture_letter(4, 4, 1.0)),
]


# ------------------------------------------------------------------ minigame pictures (64 x 64 pt)
def _mud(b):
    fill([(0, 0), (b.w, 0), (b.w, b.h), (0, b.h)], P.MUD)
    for (x, y) in ((10, 50), (52, 14), (30, 8)): dot(x, y, 1.5, P.MUD_DARK)


def _boots(b):
    from pond import big_boot
    with T(b.w/2 - 6, 10, 1.7):
        for lx in (-7, 7):
            tube([(lx, 26), (lx, 14)], 10, 9, P.WADERS, sh=0)
            big_boot(lx)


def _card(b):
    fill([(0, 0), (b.w, 0), (b.w, b.h), (0, b.h)], P.PAPER)


MG = [
    ("print_bird", lambda b: (_mud(b), bird_track(b.w/2, b.h/2 - 8, 3.2))),
    ("print_badger", lambda b: (_mud(b), badger_track(b.w/2, b.h/2 - 10, 2.6))),
    ("print_boot", lambda b: (_mud(b), boot_print(b.w/2, b.h/2, 1.6, 0))),
    ("print_stick", lambda b: (_mud(b), stick_dot(b.w/2 - 10, b.h/2 + 8, 5.5), stick_dot(b.w/2 + 12, b.h/2 - 10, 5.5))),
    ("card_bird", lambda b: (_card(b), magpie(b.w/2 - 6, 14, 1.3))),
    ("card_badger", lambda b: (_card(b), badger(b.w/2 - 10, 16, 1.0))),
    ("card_boot", lambda b: (_card(b), _boots(b))),
    ("card_stick", lambda b: (_card(b), walking_stick(b.w/2 - 4, 6, 44, rot=12))),
    ("who_tonda", lambda b: (_card(b), tonda(b.w/2, -60, 1.05, mood="worried", shadow=False))),
    ("who_badger", lambda b: (_card(b), badger(b.w/2 - 10, 16, 1.0))),
    ("who_rybar", lambda b: (_card(b), rybar(b.w/2, -80, 0.95, mood="happy", shadow=False, rod=False))),
    ("who_lady", lambda b: (_card(b), verka_old(b.w/2, -68, 0.98, mood="happy", shadow=False, stick=False))),
]
