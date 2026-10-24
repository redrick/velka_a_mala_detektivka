"""Game art for story 12 "Tajemné šipky": the street at home in the village (house, garage, fence and garden gate,
paving), the hallway with the stairs, the garden party; the three kinds of chalk arrows, the hopscotch, the
garage clues, the presents (pink bike, kitten, Hanka's drawing and stick); the arrow tiles of "Otoč šipky" and
the "who drew this arrow?" cards."""
import math, random
import lib
from lib import ell, bez, rrect
import palette as P
from style3 import *
from style3 import C
from chars3 import star, tonda, babicka, deda
from scenes3 import BG, s_, sh_, sky
from skola import mama, tata, hobliny
from winter import betka
from narozeniny import (sipka, oil_smudge, chalk_stick, panak, kitten, cat_basket, kolo, tyre_track, mud_puddle, darek,
                        hidden_darek, balonek, balonky, girlanda, dort, party_table, party_hat, cat_drawing, loupana_hul,
                        pozvanka, seznam, kalendar, paper_star, phone, garaz, branka, domov, chodba, sekacka, transparent)
from letter import hand_text

S = 2.2


def _fill(b, g, alpha=None):
    fill([(b.x, b.y), (b.x + b.w, b.y), (b.x + b.w, b.y + b.h), (b.x, b.y + b.h)], g, alpha)


# ------------------------------------------------------------------ rooms
def room_street(b):
    gy = domov(b, 0.36, 121, house_x=0.17, house_s=3.0, garage_x=0.52, garage_kw=dict(door="closed"),
               fence_=(0.66, 1.02), gate_x=0.8, paving=0.2, trees=((0.36, 1.8),))


def room_hall(b):
    chodba(b, 0.27)


def room_party(b):
    gy = domov(b, 0.36, 123, trees=((0.06, 2.4), (0.94, 2.2)), clouds=True)
    girlanda(b.X(0.0), b.X(1.0), b.Y(0.9), 40, 18)
    transparent(b.X(0.25), b.X(0.75), b.Y(0.84), "VŠECHNO NEJLEPŠÍ, ALICO!", 26)
    top = party_table(b.X(0.3), b.X(0.7), gy - 60)
    balonky(b.X(0.18), gy - 20, 2.2, 5, 2)
    balonky(b.X(0.82), gy - 20, 2.2, 5, 5)


ROOMS = [("street12", room_street), ("hall12", room_hall), ("party12", room_party)]


# ------------------------------------------------------------------ slides
def slide_guide(b):
    _fill(b, P.PAPER)
    hand_text(0, b.Y(0.88), b.w, "Tři různé šipky", "SHB", 36, g=0.2)
    for k, (kind, t1, t2) in enumerate((("tata", "dlouhá, rovná", "vysoko, vedle černé otisky"),
                                         ("mama", "čárkovaná", "na konci srdíčko"),
                                         ("hanka", "z teček, malá", "těsně u země"))):
        y = b.Y(0.68 - k*0.27)
        fill(rrect(b.X(0.06), y - 50, b.w*0.36, 100, 10), P.PAVING)
        sipka(b.X(0.24), y, 4.0, 0, kind)
        if kind == "tata": oil_smudge(b.X(0.37), y - 6, 2.2)
        hand_text(b.X(0.46), y + 6, b.w*0.5, t1, "SHB", 28, g=0.2, align="left")
        hand_text(b.X(0.46), y - 30, b.w*0.5, t2, "SH", 22, g=0.3, align="left")


SLIDES = [("arrows_guide12", slide_guide),
          ("list12", lambda b: (_fill(b, P.TABLE), seznam(b.X(0.32), b.Y(0.12), 360, 400, -4)))]


# ------------------------------------------------------------------ characters
CHARACTERS = [
    ("tata_oil", 170, 320, lambda b: tata(b.w/2, 8, S, mood="surprised", right="front", left="front", shadow=False)),
    ("mama_phone", 160, 290, lambda b: mama(b.w/2, 8, S, mood="whisper", right="chin", shadow=False, outfit="home",
                                            item=lambda x, y: phone(x + 2, y + 6, 1.6, 70))),
    ("tonda_chalk", 160, 250, lambda b: tonda(b.w/2, 8, S, mood="surprised", right="front", shadow=False,
                                              item=lambda x, y: chalk_stick(x, y - 2, 1.0, 20, "tata"))),
    ("hanka_secret", 120, 200, lambda b: hanka(b.w/2, 8, S, mood="grin", right="hush", shadow=False)),
    ("hanka_chalk", 150, 200, lambda b: hanka(b.w/2 - 10, 8, S, mood="grin", right="front", shadow=False,
                                              item=lambda x, y: chalk_stick(x, y - 2, 1.0, 30, "hanka"))),
    ("alica_glum", 120, 240, lambda b: alica(b.w/2, 8, S, mood="sad", shadow=False)),
    ("alica_kitten", 140, 240, lambda b: alica(b.w/2, 8, S, mood="grin", right="hug", shadow=False,
                                               item=lambda x, y: kitten(x + 4, y - 50, 1.0, mood="happy"))),
    ("deda_basket", 170, 300, lambda b: deda(b.w/2, 8, S, mood="grin", right="front", shadow=False,
                                             item=lambda x, y: cat_basket(x + 4, y - 40, 1.0))),
]


# ------------------------------------------------------------------ props
PROPS = [
    ("arrow_high", 200, 80, lambda b: (sipka(80, 40, 2.4, 0, "tata"), oil_smudge(170, 34, 1.4))),
    ("arrow_dashed", 180, 70, lambda b: sipka(90, 35, 2.4, 0, "mama")),
    ("arrow_dotted", 120, 60, lambda b: sipka(60, 30, 2.0, 180, "hanka")),
    ("hopscotch12", 120, 220, lambda b: panak(b.w/2, 6, 2.2)),
    ("tracks12", 300, 90, lambda b: (mud_puddle(150, 45, 260, 60), tyre_track([(20, 40), (280, 52)], True, s=2.0))),
    ("mower12", 110, 100, lambda b: sekacka(b.w/2 + 20, 8, 2.0)),
    ("card12", 70, 50, lambda b: pozvanka(6, 6, 1.6, 8)),
    ("star_tam", 90, 90, lambda b: paper_star(b.w/2, b.h/2, 36, "TAM", 8)),
    ("star_skoc", 90, 90, lambda b: paper_star(b.w/2, b.h/2, 36, "SKOČ", -6)),
    ("cake12", 140, 110, lambda b: dort(b.w/2, 10, 2.0)),
    ("bike12", 220, 120, lambda b: kolo(b.w/2, 6, 2.0, bow=True)),
    ("gifts12", 260, 120, lambda b: (cat_drawing(10, 20, 100, 76, -4), loupana_hul(170, 6, 1.6, 30, 70))),
    ("presents12", 200, 80, lambda b: [darek(30 + k*48, 6, 40, 30, g) for k, g in
                                        enumerate((P.PRESENT_RED, P.PRESENT_BLUE, P.PRESENT_YELLOW, P.PRESENT_RED))]),
    ("calendar12", 120, 140, lambda b: kalendar(10, 10, 100, 120)),
    ("party_hat12", 50, 60, lambda b: party_hat(b.w/2, 8, 2.0, 15)),
]


# ------------------------------------------------------------------ minigame tiles (64 x 64)
def _paving(b):
    fill([(0, 0), (b.w, 0), (b.w, b.h), (0, b.h)], P.PAVING)
    stroke([(0, 0), (64, 0), (64, 64), (0, 64), (0, 0)], BG, g=0.55)


def _card(b):
    fill([(0, 0), (b.w, 0), (b.w, b.h), (0, b.h)], P.PAPER)


MG = [
    ("arr_tile", _paving),
    ("arr_arrow", lambda b: sipka(b.w/2 + 2, b.h/2, 1.2, 0, "tata")),
    ("arr_star", lambda b: (_paving(b), paper_star(b.w/2, b.h/2, 20, None, 0))),
    ("arr_door", lambda b: (_paving(b), shape(rrect(14, 4, 36, 56, 3), P.DOOR, LINE), dot(42, 32, 2.4, 0.85))),
    ("arr_gate", lambda b: (_paving(b), branka(6, 8, 44, 40, False))),
    ("arr_bush", lambda b: (_paving(b), shape(ell(32, 32, 26, 24, 24), P.KRASLICE_GREEN, LINE))),
    ("who_alica12", lambda b: (_card(b), alica(b.w/2, -68, 1.2, mood="grin", shadow=False))),
    ("who_tata12", lambda b: (_card(b), tata(b.w/2, -96, 0.95, mood="grin", shadow=False))),
    ("who_mama12", lambda b: (_card(b), mama(b.w/2, -84, 0.95, mood="grin", shadow=False, outfit="home"))),
    ("who_hanka12", lambda b: (_card(b), hanka(b.w/2, -40, 1.2, mood="grin", shadow=False))),
    ("who_tonda12", lambda b: (_card(b), tonda(b.w/2, -60, 1.05, mood="happy", shadow=False))),
    ("who_betka12", lambda b: (_card(b), betka(b.w/2, -46, 1.2, hat=False, mood="grin", shadow=False))),
    ("clue_arrow_tata", lambda b: (_card(b), sipka(b.w/2 - 4, b.h/2 + 4, 1.0, 0, "tata"), oil_smudge(50, 18, 0.8))),
    ("clue_arrow_mama", lambda b: (_card(b), sipka(b.w/2 + 4, b.h/2, 1.1, 0, "mama"))),
    ("clue_arrow_hanka", lambda b: (_card(b), sipka(b.w/2, 16, 1.3, 0, "hanka"))),
]


def COVER(s):
    gy = domov(s, 0.4, 7, house_x=0.3, house_s=1.2, fence_=(0.0, 1.0), gate_x=0.7, paving=0.2)
    for fx, kind, rot in ((0.15, "tata", 0), (0.45, "mama", 10), (0.75, "hanka", 20)):
        sipka(s.X(fx), s.Y(0.08), 1.0, rot, kind)
    alica(s.X(0.4), s.Y(0.03), 0.85, mood="think", right="lens", lens=True, look=(1, -0.4), shadow=False)
    hanka(s.X(0.78), s.Y(0.03), 0.85, flip=True, mood="grin", right="hush", shadow=False)
