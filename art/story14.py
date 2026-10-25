"""Game art for story 14 "Poklad na hradě": Točník's gate bridge over the bear moat, the courtyard with the tower and
its putlog holes, the vaulted hall where the Klub sleeps; the kastelánka, the jackdaws, the clues, the second Klub
tin; the tiles of "Klíče od hradu", "Čtrnáctá díra", "Jméno pro kavku" and the suspect cards."""
import math, random
import lib
from lib import ell, bez, rrect
import palette as P
from style3 import *
from style3 import C
from chars3 import star, tonda, deda
from scenes3 import BG, s_, sh_, sky
from winter import betka
from pond import verka_old, rybar
from tocnik import (gate_bridge, nadvori, hall, medvedi_prikop, brtnik, tower, tower_holes, putlog, stuzka_hang, kavka,
                    kavci_pero, holubi_pero, holub, bird_prints, hnizdo, joey_lezi, stuzka, sponka, rohlik, drobky,
                    vetvicky, chlup, lavicka, velky_klic, svazek, klicek, hvezdna_mapa, plechovka2, vez_kresba, kastelanka,
                    lezi, lucerna, castle_far, zebrak_ruin, wooded_hill)
from attic import ladder

S = 2.2
TOWER = dict(tower_x=0.8, tower_w=0.3, tower_h=330)


def _fill(b, g, alpha=None):
    fill([(b.x, b.y), (b.x + b.w, b.y), (b.x + b.w, b.y + b.h), (b.x, b.y + b.h)], g, alpha)


# ------------------------------------------------------------------ rooms
def room_gate(b):
    gate_bridge(b, 0.3)


def room_court(b):
    nadvori(b, 0.3, 141, windows=(0.15, 0.33, 0.51), **TOWER)
    lavicka(b.X(0.36), b.Y(0.3), 2.2)


def room_hall(b):
    fy, (x0, x1, sy) = hall(b, 0.28, window=(0.72, 0.42, 0.16, 0.34))
    for k, (fx, g) in enumerate(((0.1, P.SLEEPING_BAG), (0.24, P.TENT_GREEN), (0.38, P.TENT_ORANGE))):
        shape(rrect(b.X(fx), b.Y(0.2), 220, 44, 20), g, LINE)
        shape(ell(b.X(fx) + 30, b.Y(0.2) + 22, 26, 14, 20), 0.95, LINE*0.8)
    lucerna(b.X(0.5), b.Y(0.28), 2.0, lit=True)


def hole_xy(n):
    """the room position (Godot px) of putlog hole n (1..18) on the courtyard tower"""
    b = _Box(960, 540)
    gy = b.Y(0.3)
    w = b.w*TOWER["tower_w"]
    h = TOWER["tower_h"]
    x0 = b.X(TOWER["tower_x"]) - w/2
    cx, cy, sz = tower_holes(x0, gy + h*0.3, w, h*0.7)[n - 1]
    return round(cx*2), round((540 - cy)*2)


class _Box:
    def __init__(self, w, h): self.x, self.y, self.w, self.h = 0, 0, w, h
    def X(self, f): return self.w*f
    def Y(self, f): return self.h*f


ROOMS = [("gate14", room_gate), ("court14", room_court), ("hall14", room_hall)]


# ------------------------------------------------------------------ slides
def slide_bears(b):
    gy = medvedi_prikop(b, 0.3)
    brtnik(b.X(0.35), b.Y(0.12), 2.4, pose="walk")
    brtnik(b.X(0.7), b.Y(0.14), 2.2, flip=True, pose="sit")


def slide_kavka(b):
    _fill(b, P.SUMMER_SKY)
    kavka(b.X(0.35), b.Y(0.2), 5.0, pose="perch")
    kavka(b.X(0.75), b.Y(0.5), 3.0, pose="fly")


def slide_nest(b):
    _fill(b, P.CASTLE_WALL)
    from tocnik import stone_wall
    stone_wall(0, 0, b.w, b.h, 9, rows=10)
    shape(rrect(b.X(0.3), b.Y(0.35), b.X(0.4), b.Y(0.4), 6), P.PUTLOG, LINE)
    hnizdo(b.X(0.5), b.Y(0.4), 4.0)
    vetvicky(b.X(0.5), b.Y(0.05), 160, 3, 2.4)


def slide_share(b):
    _fill(b, P.SUMMER_SKY)
    fill([(0, 0), (b.w, 0), (b.w, b.Y(0.3)), (0, b.Y(0.3))], P.CASTLE_STONE)
    kavka(b.X(0.35), b.Y(0.3), 4.0, pose="walk", item=lambda x, y: rohlik(x + 4, y, 0.5))
    kavka(b.X(0.65), b.Y(0.3), 4.0, flip=True, pose="walk", young=True)
    drobky(b.X(0.5), b.Y(0.3), 80, 14)


def slide_tin(b):
    _fill(b, P.TABLE)
    plechovka2(b.X(0.18), b.Y(0.22), 3.0, open_=True)
    hvezdna_mapa(b.X(0.36), b.Y(0.3), 300, 220, -3)
    klicek(b.X(0.82), b.Y(0.5), 3.0, -20)


SLIDES = [("k_bears", slide_bears), ("k_kavka", slide_kavka), ("k_nest", slide_nest), ("k_share", slide_share),
          ("k_tin", slide_tin)]


# ------------------------------------------------------------------ characters
def _kastel(mood="happy", **kw):
    return lambda b: kastelanka(b.w/2, 8, S*0.9, mood=mood, shadow=False, **kw)


def _chars():
    out = []
    for mood in ("happy", "talk", "grin", "surprised", "worried"):
        out.append((f"kastelanka_{mood}", 150, 290, _kastel(mood)))
    out.append(("kastelanka_walk", 150, 290, _kastel("happy", legs="walk")))
    out.append(("kastelanka_keys", 170, 290, _kastel("grin", right="front", item=lambda x, y: svazek(x + 4, y - 10, 1.4))))
    out.append(("joey_lie", 200, 100, lambda b: joey_lezi(b.w/2, 8, S*0.9)))
    out.append(("tonda_rohlik", 140, 250, lambda b: tonda(b.w/2, 8, S, mood="grin", right="front", shadow=False,
                                                         item=lambda x, y: rohlik(x + 2, y, 1.4))))
    return out


CHARACTERS = _chars()


# ------------------------------------------------------------------ props
PROPS = [
    ("rohlik14", 70, 40, lambda b: rohlik(b.w/2, 10, 1.6)),
    ("kavka14", 90, 80, lambda b: kavka(40, 8, 1.6, pose="perch")),
    ("kavka14_walk", 110, 70, lambda b: kavka(50, 6, 1.4, pose="walk", item=lambda x, y: chlup(x + 2, y - 2, 0.6))),
    ("kavka14_fly", 140, 90, lambda b: kavka(80, 20, 1.6, pose="fly")),
    ("sill14", 110, 50, lambda b: (stuzka(30, 14, 1.6), sponka(80, 14, 1.6))),
    ("prints14", 120, 50, lambda b: (bird_prints(30, 18, 1.6, 4, 10), kavci_pero(90, 20, 1.6, 30))),
    ("twigs14", 160, 70, lambda b: (vetvicky(b.w/2, 10, 120, 4, 1.6), chlup(110, 18, 1.2))),
    ("eyes14", 50, 70, lambda b: (putlog(25, 50, 34, ribbon=True, eyes=True, glow=True))),
    ("ladder14", 120, 420, lambda b: ladder(60, 4, 416, 60)),
    ("tin14", 80, 70, lambda b: plechovka2(b.w/2, 8, 1.6)),
    ("hidkey14", 40, 60, lambda b: velky_klic(20, 50, 0.9)),
]


# ------------------------------------------------------------------ minigame tiles (64 x 64)
def _card(b):
    fill([(0, 0), (b.w, 0), (b.w, b.h), (0, b.h)], P.PAPER)


def _dots(n):
    def draw(b):
        _card(b)
        rows = [min(5, n - k) for k in range(0, n, 5)]
        for r, cnt in enumerate(rows):
            for c in range(cnt):
                dot(10 + c*11, 52 - r*13, 4.2, P.RED_RIBBON if r % 2 == 0 else P.JACKDAW)
    return draw


def _wall(b):
    from tocnik import stone_wall
    fill([(0, 0), (b.w, 0), (b.w, b.h), (0, b.h)], P.CASTLE_WALL)
    stone_wall(0, 0, 64, 64, 4, rows=4)


MG = [
    ("key14", lambda b: velky_klic(32, 52, 1.05)),
    ("hole_wall", _wall),
    ("hole_empty", lambda b: (_wall(b), shape(rrect(18, 18, 28, 28, 3), P.PUTLOG, LINE))),
    ("hole_ribbon", lambda b: (_wall(b), shape(rrect(18, 18, 28, 28, 3), P.PUTLOG, LINE), stuzka_hang(38, 22, 24))),
    ("hole_ivy", lambda b: (_wall(b), [shape(ell(10 + k*12, 20 + (k % 2)*16, 9, 7, 14), P.FOREST_DARK, LINE*0.6)
                                        for k in range(5)])),
    ("who_medved14", lambda b: (_card(b), brtnik(30, 10, 0.55, pose="sit"))),
    ("who_strasidlo14", lambda b: (_card(b), shape(bez((14, 6), (10, 50), (54, 50), (50, 6)) + [(42, 12), (34, 6), (26, 12), (20, 6)],
                                                      1.0, LINE), dot(26, 34, 3.5, 0.0), dot(38, 34, 3.5, 0.0))),
    ("who_holub14", lambda b: (_card(b), holub(32, 12, 1.2))),
    ("who_kastelanka14", lambda b: (_card(b), kastelanka(b.w/2, -84, 0.95, mood="grin", shadow=False))),
    ("who_kavka14", lambda b: (_card(b), kavka(30, 12, 1.4, pose="perch"))),
    ("clue_prints14", lambda b: (_card(b), bird_prints(20, 26, 1.6, 3, 10))),
    ("clue_feather14", lambda b: (_card(b), kavci_pero(32, 32, 1.8, 30))),
    ("clue_twigs14", lambda b: (_card(b), vetvicky(32, 14, 46, 4, 1.0), chlup(46, 22, 0.9))),
    ("clue_wall14", lambda b: (_wall(b), putlog(32, 32, 26, twigs=True))),
    ("clue_ribbon14", lambda b: (_wall(b), putlog(32, 36, 26, ribbon=True, eyes=True, glow=True))),
] + [(f"dots_{n}", _dots(n)) for n in (1, 2, 3, 4, 5, 6, 9, 10, 11, 14)]


def COVER(s):
    from tocnik import tocnik_view
    tocnik_view(s, 14)
    alica(s.X(0.3), s.Y(0.03), 0.85, mood="think", right="lens", lens=True, look=(1, 0.4), shadow=False)
    hanka(s.X(0.78), s.Y(0.03), 0.8, flip=True, mood="grin", right="point", shadow=False)
    kavka(s.X(0.55), s.Y(0.7), 0.6, pose="fly")


if __name__ == "__main__":
    print([hole_xy(n) for n in (1, 6, 13, 14, 18)])
