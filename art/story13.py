"""Game art for story 13 "Stopy u potoka": the camp on Hvězdná louka (three tents, the campfire, the willows), the
creek by the camp (stepping stones, Bětka's measuring rock, the mud bank), the beaver's pond upstream (the dam,
the lodge, the old footbridge); the clues, Hryzálek, the tin; the tiles of "Čím to bylo?", "Kámen v potoce",
"Hráz pro bobra" and the suspect cards."""
import math, random
import lib
from lib import ell, bez, rrect
import palette as P
from style3 import *
from style3 import C
from chars3 import star, tonda, deda
from scenes3 import BG, s_, sh_, sky
from skola import tata, mama
from winter import betka
from pond import verka_old, rybar, treasure_tin, club_photo, badge
from joeyday import hajny
from potok import (louka, creek, stan, taborak, polena, pila, vrbka, pahyl, padla_vrbka, tresky, kudrlinky, pletivo,
                   deda_hul, bobr_print, bobr_front, vydra_print, bobr_trail, drag_slide, zuby_closeup, saw_closeup,
                   dog_bite, bobr, eyeshine, plesk, hraz, lavka, hrad_kresba, skicak, bobri_hrad, leknin, stone_top,
                   measuring_rock, night_stars)
from village import frog

S = 2.2


def _fill(b, g, alpha=None):
    fill([(b.x, b.y), (b.x + b.w, b.y), (b.x + b.w, b.y + b.h), (b.x, b.y + b.h)], g, alpha)


# ------------------------------------------------------------------ rooms
def room_camp(b):
    gy = louka(b, 0.6, 131)
    for fx, s_k in ((0.9, 2.6), (0.98, 2.2), (0.04, 2.0)):
        vrbka(b.X(fx), b.Y(0.33), s_k, seed=int(fx*100))
    stan(b.X(0.14), b.Y(0.3), 3.0, "dome")
    stan(b.X(0.45), b.Y(0.32), 2.5, "old")
    stan(b.X(0.76), b.Y(0.3), 2.9, "small")


def room_creek(b):
    louka(b, 0.62, 132, creek_=(0.3, 0.44))
    for fx, s_k in ((0.08, 2.2), (0.22, 1.8), (0.88, 2.4)):
        vrbka(b.X(fx), b.Y(0.47), s_k, seed=int(fx*90))


def room_dam(b):
    gy = louka(b, 0.64, 133, creek_=(0.3, 0.5))
    bobri_hrad(b.X(0.2), b.Y(0.43), 160, 70, 0.2)
    for fx, s_k in ((0.06, 2.0), (0.93, 2.2), (0.75, 1.6)):
        vrbka(b.X(fx), b.Y(0.53), s_k, seed=int(fx*70))
    leknin(b.X(0.44), b.Y(0.46), 1.4)
    leknin(b.X(0.6), b.Y(0.44), 1.1)
    lavka(b.X(0.68), b.X(0.98), b.Y(0.33), 1.6)


ROOMS = [("camp13", room_camp), ("creek13", room_creek), ("dam13", room_dam)]


# ------------------------------------------------------------------ slides
def _slide(b, g=P.PAPER):
    _fill(b, g)


def slide_teeth(b):
    _slide(b)
    zuby_closeup(b.X(0.3), b.Y(0.5), 2.6)
    bobr(b.X(0.72), b.Y(0.25), 4.0, pose="sit", branch=True)


def slide_lodge(b):
    _slide(b, P.SPRING_SKY)
    fill([(0, 0), (b.w, 0), (b.w, b.Y(0.5)), (0, b.Y(0.5))], P.CREEK)
    bobri_hrad(b.X(0.5), b.Y(0.12), 560, 300, 0.4)


def slide_tail(b):
    _slide(b, P.NIGHT_MEADOW)
    night_stars(b, 0.6, 40, 5)
    fill([(0, 0), (b.w, 0), (b.w, b.Y(0.55)), (0, b.Y(0.55))], P.CREEK_DEEP)
    bobr(b.X(0.4), b.Y(0.35), 4.0, pose="slap", wet=True)
    plesk(b.X(0.62), b.Y(0.35), 3.0)


def slide_young(b):
    _slide(b, P.SPRING_SKY)
    fill([(0, b.Y(0.3)), (b.w, b.Y(0.3)), (b.w, b.Y(0.5)), (0, b.Y(0.5))], P.CREEK)
    bobri_hrad(b.X(0.15), b.Y(0.28), 220, 120, 0.3)
    bobr(b.X(0.5), b.Y(0.4), 2.4, pose="swim", branch=True)
    for k in range(5):
        fill(ell(b.X(0.6) + k*30, b.Y(0.4), 6, 3, 12), 0.25)
    hraz(b.X(0.76), b.X(0.98), b.Y(0.3), 40, 7)


def slide_tin(b):
    _slide(b, P.TABLE)
    treasure_tin(b.X(0.2), b.Y(0.22), 3.0, open_=True)
    hrad_kresba(b.X(0.42), b.Y(0.2), 220, 270, -4)
    club_photo(b.X(0.72), b.Y(0.45), 200, 150, 6)
    badge(b.X(0.8), b.Y(0.25), 26)


SLIDES = [("b_teeth", slide_teeth), ("b_lodge", slide_lodge), ("b_tail", slide_tail), ("b_young", slide_young),
          ("b_tin", slide_tin)]


# ------------------------------------------------------------------ characters
def _betka(mood="happy", **kw):
    return lambda b: betka(b.w/2, 8, S*1.12, hat=False, mood=mood, shadow=False, **kw)


def _chars():
    out = []
    for mood in ("happy", "talk", "grin", "worried", "surprised", "whisper"):
        out.append((f"betkal_{mood}", 130, 230, _betka(mood)))
    out.append(("betkal_walk", 130, 230, _betka("happy", legs="walk")))
    out.append(("betkal_sketch", 150, 230, _betka("grin", right="front",
                                                  item=lambda x, y: skicak(x - 8, y - 34, 28, 22, 0, rot=8))))
    out.append(("tata_saw", 180, 320, lambda b: tata(b.w/2, 8, S, mood="happy", right="front", shadow=False,
                                                     item=lambda x, y: pila(x + 2, y, 1.4, 30))))
    out.append(("hanka_stick", 140, 200, lambda b: hanka(b.w/2 - 6, 8, S, mood="grin", right="front", shadow=False,
                                                         item=lambda x, y: deda_hul(x - 4, y - 30, 0.5, -25, peeled=True, length=80))))
    out.append(("verka_buchty", 170, 300, lambda b: verka_old(b.w/2, 8, S, mood="grin", right="front", shadow=False,
                                                              stick=False, item=lambda x, y: _buchty(x + 4, y - 26))))
    return out


def _buchty(x, y):
    shape(ell(x, y, 22, 6, 24), 0.95, LINE)
    for k in range(4):
        shape(ell(x - 12 + k*8, y + 4 + (k % 2)*2, 6, 5, 14), P.LOG_END, LINE*0.6)


CHARACTERS = _chars()


# ------------------------------------------------------------------ props
def _willow_down(b):
    padla_vrbka(60, 40, 2.0, seed=5)
    pahyl(40, 12, 2.0, 30)
    tresky(40, 14, 90, 24, 3, 1.4)


def _stones(level):
    def draw(b):
        for k, fx in enumerate((0.12, 0.3, 0.48, 0.66)):
            stone_top(b.X(fx), b.Y(0.32) + k*6, 34, 10, [0, 0.55, 1.0][level])
        measuring_rock(b.X(0.86), b.Y(0.3), 2.8, level)
    return draw


def _tracks(b):
    drag_slide([(20, 120), (140, 90), (300, 60), (420, 30)], 40)
    bobr_trail([(40, 70), (160, 54), (300, 40), (430, 20)], 1.8)


def _otter(b):
    shape(rrect(6, 6, b.w - 12, b.h - 12, 20), P.DRAG_MUD, None)
    vydra_print(b.w/2, b.h/2, 2.6, ink=True)


def _tin(b):
    treasure_tin(b.w/2, 10, 1.6, dirty=True)


PROPS = [
    ("fire13", 280, 220, lambda b: taborak(b.w/2, 40, 2.2, lit=True)),
    ("fire13_out", 280, 220, lambda b: taborak(b.w/2, 40, 2.2, lit=False)),
    ("logs13", 160, 80, lambda b: (polena(60, 10, 1.6), pila(120, 14, 1.2, 10))),
    ("willow13", 420, 150, _willow_down),
    ("stump13", 120, 80, lambda b: (pahyl(60, 10, 1.6, 34), tresky(60, 12, 80, 22, 7, 1.2))),
    ("stones13_0", 380, 180, _stones(0)),
    ("stones13_1", 380, 180, _stones(1)),
    ("stones13_2", 380, 180, _stones(2)),
    ("tracks13", 450, 140, _tracks),
    ("otter13", 90, 90, _otter),
    ("eyes13", 120, 60, lambda b: eyeshine(b.w/2, b.h/2, 3.0)),
    ("dam13p", 440, 120, lambda b: hraz(10, 430, 12, 80, 5, stick_at=270)),
    ("beaver13_swim", 200, 80, lambda b: bobr(70, 30, 2.2, pose="swim", branch=True)),
    ("beaver13_sit", 170, 150, lambda b: bobr(60, 10, 2.2, pose="sit", branch=True)),
    ("tin13", 90, 70, _tin),
    ("mesh13", 120, 260, lambda b: (vrbka(b.w/2, 10, 2.2, seed=9), pletivo(b.w/2, 10, 34, 50))),
    ("frog13", 50, 50, lambda b: frog(b.w/2, b.h/2 - 8, 1.6)),
]

ITEMS = [
    ("klacik13", 80, 80, lambda b: deda_hul(16, 8, 0.55, -40, peeled=True, length=90)),
]


# ------------------------------------------------------------------ minigame tiles (64 x 64)
def _card(b):
    fill([(0, 0), (b.w, 0), (b.w, b.h), (0, b.h)], P.PAPER)


def _grass(b, g=P.EARLY_SUMMER_GRASS):
    fill([(0, 0), (b.w, 0), (b.w, b.h), (0, b.h)], g)
    rd = random.Random(3)
    for _ in range(6):
        x, y = rd.uniform(6, 58), rd.uniform(6, 58)
        for k in (-2, 0, 2): stroke([(x + k, y), (x + k*1.6, y + 5)], BG*0.5, g=0.4)


def _hill(b):
    _grass(b, P.FOREST_DARK)
    for k in range(3):
        stroke(bez((4, 14 + k*16), (22, 20 + k*16), (42, 10 + k*16), (60, 16 + k*16)), LINE*0.6, g=0.25)


def _water(b, g=P.CREEK):
    fill([(0, 0), (b.w, 0), (b.w, b.h), (0, b.h)], g)
    for k in range(3):
        stroke([(8 + k*14, 18 + k*14), (22 + k*14, 20 + k*14), (34 + k*14, 18 + k*14)], BG*1.1, g=P.POND_RIPPLE)


def _knife(b):
    _card(b)
    with T(32, 32, 1.0, rot=35):
        shape([(-4, -24), (4, -24), (4, 0), (-4, 0)], 0.35, LINE)
        shape([(-4, 0), (4, 0), (2, 22), (-4, 26)], 0.85, LINE)
    kudrlinky(44, 14, 0.7, 2, 4)


def _who_card(fn):
    return lambda b: (_card(b), fn(b))


MG = [
    ("mark_flat", lambda b: (_card(b), saw_closeup(32, 32, 0.85))),
    ("mark_curls", lambda b: (_card(b), kudrlinky(32, 30, 1.3, 4, 2))),
    ("mark_holes", lambda b: (_card(b), dog_bite(32, 32, 0.9, 20))),
    ("mark_grooves", lambda b: (_card(b), zuby_closeup(32, 32, 0.45))),
    ("by_saw", lambda b: (_card(b), pila(4, 26, 1.0, 15))),
    ("by_knife", _knife),
    ("by_joey", lambda b: (_card(b), joey(30, 8, 0.7, mood="happy", shadow=False))),
    ("by_teeth", lambda b: (_card(b), stroke([(20, 46), (44, 46)], LINE*0.5, g=0.5),
                            shape(rrect(22, 22, 9, 18, 3), P.FORSYTHIA, LINE),
                            shape(rrect(33, 22, 9, 18, 3), P.FORSYTHIA, LINE))),
    ("rock_0", lambda b: skicak(0, 4, 64, 56, 0, day=1)),
    ("rock_1", lambda b: skicak(0, 4, 64, 56, 1, day=2)),
    ("rock_2", lambda b: skicak(0, 4, 64, 56, 2, day=3)),
    ("rock_3", lambda b: skicak(0, 4, 64, 56, 3.2, day=0)),
    ("rock_low", lambda b: skicak(0, 4, 64, 56, -0.6, day=0)),
    ("dam_low", _grass),
    ("dam_high", _hill),
    ("dam_stone", lambda b: (_grass(b), shape(bez((8, 8), (2, 40), (30, 62), (56, 40)) + bez((56, 40), (64, 14), (40, 2), (8, 8)),
                                                P.STONE, LINE))),
    ("dam_water", _water),
    ("dam_flood", lambda b: _water(b, P.CREEK_DEEP)),
    ("dam_branch", lambda b: [tube([(6, 10 + k*14), (58, 20 + k*12)], 5, 4, P.BARK, sh=0) for k in range(4)]),
    ("dam_tent", lambda b: (_grass(b), stan(32, 8, 0.48, "small"))),
    ("dam_lodge", lambda b: [_water(b, P.CREEK_DEEP)] + [stroke([(8 + k*5, 10), (32, 46 + (k % 3)*4)], LINE*1.6, g=P.BARK) for k in range(10)]),
    ("who_tata13", lambda b: (_card(b), tata(b.w/2, -96, 0.95, mood="happy", shadow=False))),
    ("who_hanka13", lambda b: (_card(b), hanka(b.w/2, -40, 1.2, mood="grin", shadow=False))),
    ("who_vydra13", lambda b: (_card(b), vydra_print(b.w/2, b.h/2, 2.2, ink=True))),
    ("who_vlkodlak13", lambda b: (_card(b), fill(ell(32, 40, 16, 16, 24), P.FORSYTHIA),
                                 fill(ell(40, 46, 13, 13, 24), P.PAPER))),
    ("who_bobr13", lambda b: (_card(b), bobr(24, 8, 0.8, pose="sit"))),
    ("clue_stump13", lambda b: (_card(b), pahyl(32, 10, 1.1, 30), tresky(32, 12, 40, 10, 2, 0.7))),
    ("clue_grooves13", lambda b: (_card(b), zuby_closeup(32, 32, 0.45))),
    ("clue_webbed13", lambda b: (_card(b), bobr_print(32, 30, 2.0, ink=True))),
    ("clue_rock13", lambda b: (_card(b), skicak(4, 8, 26, 22, 0, day=1), skicak(19, 20, 26, 22, 1, day=2),
                               skicak(34, 32, 26, 22, 2, day=3))),
    ("clue_plesk13", lambda b: (_card(b), plesk(32, 24, 1.0))),
    ("clue_stick13", lambda b: (_card(b), deda_hul(14, 10, 0.5, -45, peeled=True, length=80))),
]


def COVER(s):
    gy = louka(s, 0.5, 13, creek_=(0.22, 0.34))
    stan(s.X(0.2), s.Y(0.42), 0.7, "old")
    bobr(s.X(0.7), s.Y(0.28), 0.9, pose="sit", branch=True)
    alica(s.X(0.35), s.Y(0.03), 0.85, mood="think", right="lens", lens=True, look=(1, -0.4), shadow=False)
    hanka(s.X(0.86), s.Y(0.03), 0.8, flip=True, mood="grin", shadow=False)
