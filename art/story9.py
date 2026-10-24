"""Game art for story 9 "Tajná zpráva v knihovně": the village library, the village green on Masopust day; the
librarian; the costumes (Alica the owl, Hanka the bear cub, Tonda the kobyla, Věrka the kominík, babička the bába s
nůší, děda the bear); the slips in the star code, děda's key, the borrowing card, babička's sewing corner; the glyph
tiles of "Hvězdičkové písmo" and the parade suspect cards."""
import math, random
import lib
from lib import ell, bez, rrect
import palette as P
from style3 import *
from style3 import C
from chars3 import star, babicka, deda, tonda, notebook_big
from scenes3 import BG, s_, sh_, sky, hills
from pond import verka_old, rybar
from joeyday import lavender_sprig
from winter import winter_hat
from masopust import (ROWS, CODE, glyph, star_pts, cipher_text, slip, cipher_key, pinking_shears, fabric_scrap,
                      sewing_corner, bookshelf, library, library_desk, library_card, knihovnice, jezevcik, alica_owl,
                      hanka_bear, medved, kobyla, kominik, baba, slameny, accordion, muzikant, streamers,
                      masopust_street, koblih)
from letter import hand_text

S = 2.2


def _fill(b, g, alpha=None):
    fill([(b.x, b.y), (b.x + b.w, b.y), (b.x + b.w, b.y + b.h), (b.x, b.y + b.h)], g, alpha)


# ------------------------------------------------------------------ rooms
def room_library(b):
    fy = library(b, 0.27, 91)
    library_desk(b.X(0.6), fy - 4, 300, 90)
    jezevcik(b.X(0.86), fy, 1.8)


def room_street(b):
    gy = b.Y(0.36)
    masopust_street(b, gy, 92, houses=((0.12, 2.4), (0.5, 2.0), (0.86, 2.6)), garlands=2)


ROOMS = [("library9", room_library), ("street9", room_street)]


# ------------------------------------------------------------------ slides
def slide_key(b):
    _fill(b, P.PAPER)
    hand_text(0, b.Y(0.88), b.w, "Hvězdičkové písmo – klíč z dědova zápisníku", "SHB", 28, g=0.2)
    cipher_key(b.X(0.1), b.Y(0.08), b.w*0.8, b.h*0.72, style="deda", title=False)


def slide_card(b):
    _fill(b, 0.82)
    library_card(b.X(0.3), b.Y(0.12), b.w*0.4, b.h*0.76,
                 [("H.", "únor 1966", True), ("J.", "únor 1966", True), ("Tonda", "prosinec", False)])


def _slip_slide(lines, old=False, style="jana"):
    def draw(b):
        _fill(b, 0.82)
        slip(b.w/2, b.h/2, b.w*0.86, b.h*0.8, lines, 80 if len(lines) < 3 else 60, rot=-2, old=old, style=style)
    return draw


def slide_stars(b):
    """děda draws a star in five lines; the stars in the message are one stroke, like babička's on her list"""
    _fill(b, P.PAPER)
    hand_text(b.X(0.05), b.Y(0.86), b.w*0.4, "Děda", "SHB", 30, g=0.2)
    hand_text(b.X(0.55), b.Y(0.86), b.w*0.4, "Zpráva", "SHB", 30, g=0.2)
    stroke(star_pts(b.X(0.27), b.Y(0.45), 120, "deda") + [star_pts(b.X(0.27), b.Y(0.45), 120, "deda")[0]], 5, g=0.2)
    stroke(star_pts(b.X(0.75), b.Y(0.45), 120, "jana"), 5, g=P.CIPHER_INK)
    for k in range(5):
        hand_text(b.X(0.27) + math.cos(math.radians(90 + k*72))*150 - 20, b.Y(0.45) + math.sin(math.radians(90 + k*72))*150 - 14,
                  40, str(k + 1), "SHB", 22, g=0.4)


SLIDES = [("cipher_key9", slide_key), ("library_card9", slide_card),
          ("slip1", _slip_slide(["HLEDEJ HVEZDU", "NA MASOPUSTU"])), ("slip2", _slip_slide(["PRIJD", "V MASCE"])),
          ("slip_old", _slip_slide(["PRIJD NA", "MASOPUST", "BUDU MEDVED"], old=True, style="deda")),
          ("stars9", slide_stars)]


# ------------------------------------------------------------------ characters: the librarian and the costumes
def _chars():
    out = []
    for mood in ("happy", "talk", "surprised"):
        out.append((f"knihovnice_{mood}", 150, 280, lambda b, m=mood: knihovnice(b.w/2, 8, S, mood=m, shadow=False)))
    out.append(("knihovnice_walk", 150, 280, lambda b: knihovnice(b.w/2, 8, S, legs="walk", shadow=False)))
    for mood in ("happy", "grin", "surprised", "think", "talk", "worried", "whisper"):
        out.append((f"alicao_{mood}", 170, 240, lambda b, m=mood: alica_owl(b.w/2, 8, S, mood=m, shadow=False)))
        out.append((f"hankab_{mood}", 120, 210, lambda b, m=mood: hanka_bear(b.w/2, 8, S, mood=m, shadow=False)))
    out.append(("alicao_walk", 170, 240, lambda b: alica_owl(b.w/2, 8, S, legs="walk", shadow=False)))
    out.append(("alicao_point", 200, 240, lambda b: alica_owl(b.w/2 - 20, 8, S, right="point", mood="surprised", shadow=False)))
    out.append(("alicao_lens", 190, 240, lambda b: alica_owl(b.w/2 - 10, 8, S, right="lens", mood="think", shadow=False)))
    out.append(("hankab_walk", 120, 210, lambda b: hanka_bear(b.w/2, 8, S, legs="walk", shadow=False)))
    out.append(("hankab_point", 160, 210, lambda b: hanka_bear(b.w/2 - 20, 8, S, right="point", mood="wow", shadow=False)))
    out.append(("tondaw_kobyla", 200, 260, lambda b: kobyla(b.w/2, 8, S, mood="grin", shadow=False)))
    out.append(("verka_kominik", 150, 300, lambda b: kominik(b.w/2, 8, S, mood="grin", shadow=False, stick=False)))
    out.append(("verka_hide", 170, 300, lambda b: verka_old(b.w/2, 8, S, mood="worried", right="hip", left="hip",
                                                           shadow=False, stick=False)))
    out.append(("babicka_baba", 200, 330, lambda b: baba(b.w/2, 8, S, mask=True, shadow=False)))
    out.append(("babicka_unmask", 200, 330, lambda b: baba(b.w/2, 8, S, mask=False, mood="grin", shadow=False)))
    out.append(("deda_bear", 170, 320, lambda b: medved(b.w/2, 8, S, head=True, shadow=False)))
    out.append(("deda_bearface", 170, 320, lambda b: medved(b.w/2, 8, S, head=False, mood="grin", shadow=False)))
    return out


CHARACTERS = _chars()


# ------------------------------------------------------------------ props
PROPS = [
    ("slip_small", 70, 40, lambda b: slip(b.w/2, b.h/2, 60, 28, ["HLEDEJ"], 7, rot=8)),
    ("slip_small2", 70, 40, lambda b: slip(b.w/2, b.h/2, 60, 28, ["PRIJD"], 7, rot=-8)),
    ("book9", 70, 50, lambda b: (shape(rrect(8, 8, 54, 36, 3), 0.45, LINE), stroke([(14, 8), (14, 44)], LINE*0.6, g=0.8))),
    ("sewing9", 160, 120, lambda b: (sewing_corner(b.w/2, 8, 1.4), pinking_shears(b.w*0.25, 14, 1.4, 20))),
    ("boot9", 70, 80, lambda b: (shape([(14, 6), (52, 6), (54, 22), (36, 26), (34, 70), (16, 70)], P.ALICA_BOOTS, LINE),
                                 slip(34, 66, 36, 18, ["PRIJD"], 4.5, rot=-25))),
    ("list9", 80, 100, lambda b: (shape([(4, 4), (76, 4), (76, 96), (4, 96)], 1.0, LINE*0.8),
                                  [hand_text(10, 70 - k*16, 60, t, "SH", 11, g=0.2, align="left") for k, t in
                                   enumerate(("mouka", "vejce", "povidla"))],
                                  stroke(star_pts(56, 22, 12, "jana"), 1.4, g=P.CIPHER_INK))),
    ("star_hat", 80, 70, lambda b: (shape([(14, 10), (66, 10), (60, 60), (20, 60)], P.KOMINIK, LINE),
                                    star(40, 36, 10, 1.0))),
    ("koblihy", 120, 50, lambda b: [koblih(20 + k*28, 18, 1.2) for k in range(4)]),
]


# ------------------------------------------------------------------ minigame tiles (64 x 64): one per letter
def _cell(b, g=P.PAPER):
    fill([(0, 0), (b.w, 0), (b.w, b.h), (0, b.h)], g)


def _glyph_tile(ch):
    def draw(b):
        _cell(b)
        glyph(ch, b.w/2, 6, 54, style="deda")
    return draw


def _card(b):
    fill([(0, 0), (b.w, 0), (b.w, b.h), (0, b.h)], P.PAPER)


MG = [(f"cg_{ch}", _glyph_tile(ch)) for row in ROWS for ch in row] + [
    ("cg_slot", lambda b: (_cell(b, 0.95), stroke([(12, 10), (52, 10)], 2, g=0.4))),
    ("who_kobyla", lambda b: (_card(b), kobyla(b.w/2, -50, 0.95, shadow=False))),
    ("who_kominik", lambda b: (_card(b), kominik(b.w/2, -80, 0.95, shadow=False, stick=False))),
    ("who_medved", lambda b: (_card(b), medved(b.w/2, -84, 0.95, shadow=False))),
    ("who_franta9", lambda b: (_card(b), rybar(b.w/2, -84, 0.95, shadow=False, rod=False))),
    ("who_baba", lambda b: (_card(b), baba(b.w/2, -46, 0.7, mask=True, shadow=False))),
    ("clue_zig9", lambda b: (_card(b), slip(b.w/2, b.h/2, 50, 30, ["AHOJ"], 7, rot=6))),
    ("clue_lavender", lambda b: (_card(b), lavender_sprig(b.w/2, 10, 1.6, rot=10))),
    ("clue_onestar", lambda b: (_card(b), stroke(star_pts(b.w/2, b.h/2, 22, "jana"), 1.8, g=P.CIPHER_INK))),
    ("clue_db", lambda b: (_card(b), glyph("D", b.w/2 - 14, 14, 30, style="deda"), hand_text(b.w/2 + 2, 22, 30, "D", "SHB", 22))),
]


def COVER(s):
    _fill(s, P.LIB_WALL)
    bookshelf(s.x + 4, s.x + s.w - 4, s.Y(0.25), s.Y(0.98), 4, 3)
    slip(s.X(0.5), s.Y(0.42), s.w*0.7, 40, ["HLEDEJ HVEZDU"], 9, rot=-5)
    alica(s.X(0.3), s.Y(0.02), 0.8, mood="think", right="lens", lens=True, look=(1, 0.4), shadow=False)
    hanka_bear(s.X(0.75), s.Y(0.02), 0.85, mood="grin", shadow=False)
