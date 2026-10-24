"""Game art for story 8 "Stopy ve sněhu": the meadow behind the chalupa (oak, hedge, mousehole), the forest edge
(krmelec, the low spruce with the deer's bed); the snowman family (noses, no noses, pinecone noses); the animals;
the track guide and the twig slides; the print tiles of "Po stopě" and the suspect cards. The garden is story 5's."""
import math, random
import lib
from lib import ell, bez, rrect
import palette as P
from style3 import *
from style3 import C
from chars3 import star, tonda
from scenes3 import BG, s_, sh_, sky, hills
from winter import snowman_b, snow_field, bare_tree
from joeyday import hajny
from tracks import (srnka, deer_bed, divocak, rooted_ground, zajic, hare_form, liska, mousehole, pounce_hole, veverka,
                    deer_print, boar_print, hare_print, fox_print, dog_print, cat_print, squirrel_print, trail, nose_stub,
                    twig, krmelec, oak, spruce, low_spruce, winter_meadow, winter_forest, carrot, apple, beet)
from advent import bird_print
from letter import hand_text

S = 2.2


def _fill(b, g, alpha=None):
    fill([(b.x, b.y), (b.x + b.w, b.y), (b.x + b.w, b.y + b.h), (b.x, b.y + b.h)], g, alpha)


# ------------------------------------------------------------------ rooms
def room_meadow(b):
    gy = b.Y(0.34)
    winter_meadow(b, gy, 81, forest=True)
    oak(b.X(0.72), gy - 6, 2.4)
    for k in range(9):
        sh_(ell(b.X(0.08) + k*26, gy - 2 + (k % 2)*4, 22, 16, 18), P.SPRUCE_LIGHT)
    trail("zajic", [(b.X(0.05), b.Y(0.3)), (b.X(0.3), b.Y(0.28))], 1.6)
    trail("liska", [(b.X(0.35), b.Y(0.22)), (b.X(0.52), b.Y(0.24))], 1.6)
    mousehole(b.X(0.54), b.Y(0.24), 1.8)
    rooted_ground(b.X(0.72), b.Y(0.3), 160, 26)
    trail("divocak", [(b.X(0.62), b.Y(0.26)), (b.X(0.8), b.Y(0.27))], 1.6)


def room_forest(b):
    gy = b.Y(0.34)
    winter_forest(b, gy, 82, trees=((0.05, 1.9), (0.93, 2.1)))
    krmelec(b.X(0.32), gy - 4, 2.4, hay=True)
    low_spruce(b.X(0.7), gy - 4, 2.6)
    spruce(b.X(0.52), gy - 6, 1.4, seed=11)


ROOMS = [("meadow8", room_meadow), ("forest8", room_forest)]


# ------------------------------------------------------------------ slides
def slide_guide(b):
    _fill(b, P.PAPER)
    hand_text(0, b.Y(0.9), b.w, "Stopy ve sněhu – jak učil pan hajný", "SHB", 30, g=0.2)
    items = [("srnka", "dvě kapky, úzké srdíčko", lambda x, y: deer_print(x, y, 3.4, ink=True)),
             ("divočák", "širší, vzadu dvě tečky", lambda x, y: boar_print(x, y, 3.4, ink=True)),
             ("zajíc", "jako Y", lambda x, y: hare_print(x, y, 2.6, ink=True)),
             ("liška", "ovál, v jedné řadě", lambda x, y: fox_print(x, y, 3.4, ink=True)),
             ("pes", "kulatý, s drápky", lambda x, y: dog_print(x, y, 3.4, ink=True)),
             ("kočka", "kulatá, bez drápků", lambda x, y: cat_print(x, y, 3.4, ink=True)),
             ("veverka", "čtyři u sebe", lambda x, y: squirrel_print(x, y, 2.6, ink=True)),
             ("ptáček", "tři prstíky dopředu", lambda x, y: bird_print(x, y, 4.0))]
    for i, (name, note, fn) in enumerate(items):
        cx = b.X(0.13 + (i % 4)*0.245); cy = b.Y(0.62 - (i//4)*0.42)
        shape(rrect(cx - 100, cy - 90, 200, 190, 12), 1.0, LINE)
        fn(cx, cy + 25)
        hand_text(cx - 95, cy - 50, 190, name, "SHB", 22, g=0.15)
        hand_text(cx - 95, cy - 78, 190, note, "SH", 15, g=0.25)


def slide_twigs(b):
    _fill(b, P.PAPER)
    hand_text(0, b.Y(0.86), b.w, "Kdo kousal?", "SHB", 36, g=0.2)
    twig(b.X(0.28), b.Y(0.45), 5.0, cut="clean", rot=-20)
    twig(b.X(0.72), b.Y(0.45), 5.0, cut="frayed", rot=-20)
    hand_text(b.X(0.08), b.Y(0.12), b.w*0.4, "zajíc: rovně, jako nůžky", "SHB", 24, g=0.25)
    hand_text(b.X(0.52), b.Y(0.12), b.w*0.4, "srnka: roztřepené", "SHB", 24, g=0.25)


SLIDES = [("track_guide", slide_guide), ("twigs", slide_twigs)]


# ------------------------------------------------------------------ props
def _family(nose):
    def draw(b):
        snowman_b(b.w*0.18, 8, 2.6, right="wave", nose=nose)
        snowman_b(b.w*0.5, 8, 4.2, nose=nose, left="up")
        snowman_b(b.w*0.83, 8, 2.1, nose=nose)
    return draw


PROPS = [
    ("family_noses", 560, 440, _family("parsnip")),
    ("family_none", 560, 440, _family("none")),
    ("family_cones", 560, 440, _family("cone")),
    ("stub_frayed", 50, 40, lambda b: nose_stub(b.w/2, b.h/2, 2.0, "frayed", 20)),
    ("prints_trampled", 300, 80, lambda b: (trail("pes", [(10, 30), (290, 50)], 1.6, wander=0.3, seed=2),
                                           trail("srnka", [(40, 20), (260, 40)], 1.4, n=5))),
    ("prints_clean", 320, 70, lambda b: trail("srnka", [(10, 20), (310, 46)], 1.7, n=6)),
    ("hare_sit", 90, 90, lambda b: zajic(b.w/2, 8, 2.0, pose="sit")),
    ("fox_pounce", 200, 120, lambda b: liska(b.w/2, 8, 1.8, pose="pounce")),
    ("boar_root", 220, 130, lambda b: divocak(b.w/2, 8, 1.8, pose="root")),
    ("deer_stand", 240, 200, lambda b: srnka(b.w/2, 8, 1.8)),
    ("deer_bed", 140, 50, lambda b: deer_bed(b.w/2, 10, 120, 30)),
    ("krmelec_food", 160, 60, lambda b: (carrot(30, 20, 1.8, 10), apple(80, 20, 1.6), beet(125, 20, 1.6))),
]

ITEMS = [("stub_icon", 60, 50, lambda b: nose_stub(b.w/2, b.h/2, 2.0, "frayed", 20))]


# ------------------------------------------------------------------ characters
CHARACTERS = [
    ("hajny_twig", 190, 310, lambda b: hajny(b.w/2, 8, S, mood="talk", right="front", shadow=False,
                                             item=lambda x, y: twig(x + 4, y, 1.4, "frayed"))),
    ("hankaw_stub", 150, 200, lambda b: (hanka(b.w/2 - 10, 8, S, mood="wow", right="up", shadow=False,
                                               item=lambda x, y: nose_stub(x, y + 4, 1.2, "frayed")),
                                         __import__("winter").winter_hat(b.w/2 - 10, 8, S, "hanka", P.HANKA_WINTER_HAT))),
]


# ------------------------------------------------------------------ minigame tiles (64 x 64)
def _snow(b, seed=3):
    fill([(0, 0), (b.w, 0), (b.w, b.h), (0, b.h)], P.SNOW)
    r = random.Random(seed)
    for _ in range(3):
        x, y = r.uniform(6, 58), r.uniform(6, 58)
        stroke(bez((x - 5, y), (x - 2, y + 2), (x + 2, y + 2), (x + 5, y)), BG*0.6, g=0.84)


DICE = {1: [(0, 0)], 2: [(-1, -1), (1, 1)], 3: [(-1, -1), (0, 0), (1, 1)], 4: [(-1, -1), (1, -1), (-1, 1), (1, 1)],
        5: [(-1, -1), (1, -1), (0, 0), (-1, 1), (1, 1)], 6: [(-1, -1), (1, -1), (-1, 0), (1, 0), (-1, 1), (1, 1)],
        7: [(-1, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (1, 1)]}


def _hay(b, n):
    """a bundle of hay for the krmelec scale; the knots on its tag (dice dots) say how heavy it is"""
    r = random.Random(n)
    bundle = ell(b.w/2, 30, 26, 17, 30)
    shape(bundle, P.HAY, LINE)
    C.saveState(); C.clipPath(poly(bundle), stroke=0, fill=0)
    for _ in range(22):
        x, y = r.uniform(8, 56), r.uniform(14, 46)
        stroke([(x - 7, y + r.uniform(-1, 1)), (x + 7, y + r.uniform(-1, 1))], LINE*0.35, g=P.STRAW_DARK)
    C.restoreState()
    stroke([(b.w/2 - 4, 14), (b.w/2 - 4, 46)], LINE*1.1, g=P.CRAYON_BROWN, taper=False)
    shape(rrect(b.w/2, 12, 31, 31, 4), P.PAPER, LINE*0.8)
    for dx, dy in DICE[n]:
        dot(b.w/2 + 15.5 + dx*8, 27.5 + dy*8, 3.1, 0.1)


def _rack(b):
    fill([(0, 0), (b.w, 0), (b.w, b.h), (0, b.h)], P.SNOW)
    for x in range(4, 64, 10):
        stroke([(x, 2), (x + 3, 62)], LINE*1.4, g=P.CRAYON_BROWN, taper=False)
    stroke([(0, 58), (64, 58)], LINE*2, g=P.CRAYON_BROWN, taper=False)


def _card(b):
    fill([(0, 0), (b.w, 0), (b.w, b.h), (0, b.h)], P.PAPER)


MG = [(f"hay_{n}", lambda b, n=n: _hay(b, n)) for n in range(1, 8)] + [("sc_rack", _rack)] + [
    ("tr_snow", _snow),
    ("tr_deer", lambda b: (_snow(b, 1), deer_print(b.w/2, b.h/2 + 2, 2.6, ink=True))),
    ("tr_boar", lambda b: (_snow(b, 2), boar_print(b.w/2, b.h/2 + 4, 2.6, ink=True))),
    ("tr_hare", lambda b: (_snow(b, 4), hare_print(b.w/2, b.h/2, 2.0, ink=True))),
    ("tr_fox", lambda b: (_snow(b, 5), fox_print(b.w/2, b.h/2, 2.6, ink=True))),
    ("tr_dog", lambda b: (_snow(b, 6), dog_print(b.w/2, b.h/2, 2.6, ink=True))),
    ("tr_start", lambda b: (_snow(b, 7), snowman_b(b.w/2, 4, 0.55, nose="none"))),
    ("tr_goal", lambda b: (_snow(b, 8), low_spruce(b.w/2, 4, 0.55))),
    ("who_hare", lambda b: (_card(b), zajic(b.w/2, 10, 1.4))),
    ("who_fox", lambda b: (_card(b), liska(b.w/2 + 4, 10, 0.75))),
    ("who_boar", lambda b: (_card(b), divocak(b.w/2, 10, 0.7))),
    ("who_deer", lambda b: (_card(b), srnka(b.w/2, 6, 0.55))),
    ("clue_high", lambda b: (_card(b), snowman_b(b.w/2, 4, 0.75, nose="none"),
                             stroke([(b.w - 10, 6), (b.w - 10, 58)], 1.4, g=0.3))),
    ("clue_stub", lambda b: (_card(b), nose_stub(b.w/2, b.h/2, 2.2, "frayed", 20))),
    ("clue_deerprint", lambda b: (_card(b), deer_print(b.w/2, b.h/2, 2.6, ink=True))),
    ("clue_alibi", lambda b: (_card(b), joey(b.w/2 - 4, 8, 1.1, mood="sleepy", collar=False, shadow=False))),
]


def COVER(s):
    sky(s, P.SNOW_SKY)
    gy = s.Y(0.32)
    snow_field(s, gy, 8)
    snowman_b(s.X(0.3), s.Y(0.1), 0.8, nose="none")
    trail("srnka", [(s.X(0.4), s.Y(0.12)), (s.X(0.9), s.Y(0.22))], 0.7)
    alica(s.X(0.7), s.Y(0.04), 0.85, mood="think", right="lens", lens=True, look=(-1, -0.4), shadow=False, flip=True)
    srnka(s.X(0.85), s.Y(0.45), 0.4)
