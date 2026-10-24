"""Game art for story 10 "Záhada ve škole": the forest school meadow (yurts, the log building, the hutch, the
brushwood), pan Karel's kumbál, the family kitchen at home in the evening; máma, táta, paní učitelka Lucie,
pan Karel the školník, malý Karel; the hutches, the hay trail, the prints, the torn note, the woolly-hat bed; the
plank tiles of "Nový kotec" and the suspect cards."""
import math, random
import lib
from lib import ell, bez, rrect
import palette as P
from style3 import *
from style3 import C
from chars3 import star
from scenes3 import BG, s_, sh_, sky
from tracks import liska
from skola import (tata, mama, lucie, skolnik, spoluzak, morce, jezek, hay_wisp, hay_trail, holinka_print, trek_print,
                   kid_print, mud_strip, hobliny, kulich, paper_bag, box_holes, diely, kotec, novy_kotec, torn_note,
                   video_call, school_garden, kumbal, home, table, klesti, srub)
from letter import hand_text

S = 2.2


def _fill(b, g, alpha=None):
    fill([(b.x, b.y), (b.x + b.w, b.y), (b.x + b.w, b.y + b.h), (b.x, b.y + b.h)], g, alpha)


# ------------------------------------------------------------------ rooms
def room_school(b):
    school_garden(b, 0.4, 0.34, 101, school_x=0.5, school_s=2.9, pile_x=0.07, pile_s=2.6,
                  pile_kw=dict(nest=True, hay=True), drops=True)


def room_kumbal(b):
    kumbal(b, 0.27, 102)


def room_home(b):
    home(b, 0.27, evening=True, seed=103)


ROOMS = [("school10", room_school), ("kumbal10", room_kumbal), ("home10", room_home)]


# ------------------------------------------------------------------ slides
def slide_note(b):
    _fill(b, 0.82)
    torn_note(b.w/2, b.h/2, b.w*0.6, b.h*0.6, ["…JSOU U MĚ", "V TEPLE. K."], 46, rot=-3)


def slide_call(b):
    _fill(b, P.KITCHEN_WALL)
    video_call(b.w/2, b.h/2, 260, 460)


SLIDES = [("torn_note10", slide_note), ("video_call10", slide_call)]


# ------------------------------------------------------------------ characters
def _chars():
    out = []
    for mood in ("happy", "talk", "surprised", "grin", "think", "worried"):
        out.append((f"mama_{mood}", 150, 290, lambda b, m=mood: mama(b.w/2, 8, S, mood=m, shadow=False, outfit="out")))
        out.append((f"tata_{mood}", 160, 320, lambda b, m=mood: tata(b.w/2, 8, S, mood=m, shadow=False)))
    out.append(("mama_walk", 150, 290, lambda b: mama(b.w/2, 8, S, legs="walk", shadow=False, outfit="out")))
    out.append(("mama_home", 150, 290, lambda b: mama(b.w/2, 8, S, mood="happy", shadow=False, outfit="home", hair="down")))
    out.append(("tata_walk", 160, 320, lambda b: tata(b.w/2, 8, S, legs="walk", shadow=False)))
    out.append(("tata_box", 190, 320, lambda b: tata(b.w/2, 8, S, mood="grin", right="front", left="front", shadow=False,
                                                    item=lambda x, y: box_holes(x - 4, y - 30, 0.8))))
    for mood in ("happy", "talk", "worried"):
        out.append((f"lucie_{mood}", 150, 290, lambda b, m=mood: lucie(b.w/2, 8, S, mood=m, shadow=False)))
    out.append(("lucie_walk", 150, 290, lambda b: lucie(b.w/2, 8, S, legs="walk", shadow=False)))
    for mood in ("happy", "talk", "grin"):
        out.append((f"skolnik_{mood}", 160, 330, lambda b, m=mood: skolnik(b.w/2, 8, S, mood=m, shadow=False, hat=False)))
    out.append(("skolnik_walk", 160, 330, lambda b: skolnik(b.w/2, 8, S, legs="walk", shadow=False, hat=False)))
    for mood in ("happy", "talk", "worried"):
        out.append((f"malykarel_{mood}", 120, 240, lambda b, m=mood: spoluzak(b.w/2, 8, S, who="karel", mood=m, shadow=False)))
    out.append(("malykarel_walk", 120, 240, lambda b: spoluzak(b.w/2, 8, S, who="karel", legs="walk", shadow=False)))
    out.append(("hanka_bag", 150, 200, lambda b: hanka(b.w/2 - 10, 8, S, mood="grin", right="front", shadow=False,
                                                      item=lambda x, y: paper_bag(x, y - 10, 1.1))))
    return out


CHARACTERS = _chars()


# ------------------------------------------------------------------ props
PROPS = [
    ("hutch_empty", 330, 260, lambda b: kotec(b.w/2, 10, 2.5, open_=True, latch="broken", shavings=True)),
    ("hutch_new", 360, 280, lambda b: novy_kotec(b.w/2, 10, 2.3, names=True, misa=True, sisa=True)),
    ("hay_trail10", 420, 60, lambda b: hay_trail([(10, 30), (140, 22), (280, 34), (410, 26)], 12, 1.6)),
    ("prints_mud10", 300, 70, lambda b: (mud_strip(10, 30, 290, 34, 16),
                                         [holinka_print(40 + k*60, 32 + (k % 2)*6, 1.2, 80) for k in range(4)])),
    ("classmates", 300, 250, lambda b: (spoluzak(60, 8, 1.5, who="julca"), spoluzak(150, 8, 1.5, who="stella", mood="worried"),
                                        spoluzak(240, 8, 1.5, who="beatka"))),
    ("hat_nest", 300, 160, lambda b: (kulich(b.w/2, 10, 3.0, nest=True), morce(b.w/2 - 50, 40, 2.2, who="misa"),
                                      morce(b.w/2 + 44, 36, 1.9, who="sisa", flip=True))),
    ("box10", 120, 100, lambda b: box_holes(b.w/2, 8, 1.4)),
    ("parts10", 200, 90, lambda b: diely(b.w/2, 8, 1.3)),
    ("hedgehog", 90, 60, lambda b: jezek(b.w/2, 8, 1.6, hay=True)),
]


# ------------------------------------------------------------------ minigame tiles (64 x 64)
def _slot(b):
    fill([(0, 0), (b.w, 0), (b.w, b.h), (0, b.h)], 0.88)
    for k in range(0, 64, 8):
        stroke([(k, 0), (k, 64)], 0.4, g=P.WIRE)
        stroke([(0, k), (64, k)], 0.4, g=P.WIRE)
    stroke([(1, 1), (63, 1), (63, 63), (1, 63), (1, 1)], 1.2, g=0.35)


def _plank(b):
    fill([(0, 0), (b.w, 0), (b.w, b.h), (0, b.h)], P.NEW_WOOD)
    r = random.Random(4)
    for k in range(4):
        y = 10 + k*14 + r.uniform(-2, 2)
        stroke(bez((0, y), (20, y + 2), (44, y - 2), (64, y + 1)), 0.6, g=0.55)
    dot(10, 10, 1.6, 0.35); dot(54, 54, 1.6, 0.35)


def _card(b):
    fill([(0, 0), (b.w, 0), (b.w, b.h), (0, b.h)], P.PAPER)


MG = [
    ("pen_morce", lambda b: morce(b.w/2 - 4, 12, 1.25)),
    ("hutch_slot", _slot), ("hutch_plank", _plank),
    ("who_jezek", lambda b: (_card(b), jezek(b.w/2, 16, 1.2))),
    ("who_malykarel", lambda b: (_card(b), spoluzak(b.w/2, -46, 1.1, who="karel", shadow=False))),
    ("who_tata10", lambda b: (_card(b), tata(b.w/2, -96, 0.95, mood="grin", shadow=False))),
    ("who_liska10", lambda b: (_card(b), liska(b.w/2 + 4, 10, 0.75))),
    ("who_skolnik", lambda b: (_card(b), skolnik(b.w/2, -104, 0.95, shadow=False))),
    ("clue_holinka", lambda b: (_card(b), holinka_print(b.w/2, b.h/2, 1.4, 80))),
    ("clue_note10", lambda b: (_card(b), torn_note(b.w/2, b.h/2, 52, 40, ["V TEPLE.", "K."], 8))),
    ("clue_hook", lambda b: (_card(b), stroke(bez((b.w/2, 50), (b.w/2, 30), (b.w/2 + 10, 26), (b.w/2 + 12, 34)), 2.4, g=0.3))),
    ("clue_shavings", lambda b: (_card(b), hobliny(b.w/2, 20, 1.3, 4, 2))),
]


def COVER(s):
    school_garden(s, 0.4, 0.3, 7, school_x=0.6, school_s=0.6, hutch_x=None, pile_x=None, far=False)
    kotec(s.X(0.3), s.Y(0.12), 0.7, open_=True, latch="broken")
    hay_trail([(s.X(0.45), s.Y(0.1)), (s.X(0.9), s.Y(0.08))], 6, 0.8)
    alica(s.X(0.2), s.Y(0.02), 0.85, mood="think", right="lens", lens=True, look=(1, 0.4), shadow=False)
    morce(s.X(0.8), s.Y(0.45), 1.4, who="misa")
