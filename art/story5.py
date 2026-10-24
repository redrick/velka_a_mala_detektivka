"""Game art for story 5 "Kdo staví sněhuláky?": the snowy garden at the chalupa, the village road, Franta's
hallway; Bětka; the girls and Tonda in winter hats (also used by stories 6-8: prefixes alicaw/hankaw/tondaw);
the snowmen, the snow dog, the clues; the tiles of the "Postav sněhuláka" minigame and the suspect cards."""
import math, random
import lib
from lib import ell, bez, rrect
import palette as P
from style3 import *
from style3 import C
from chars3 import star, babicka, deda, tonda, torch, monkey
from scenes3 import BG, s_, sh_, sky, hills, ground, house, tree, cloud, planks
from interior import stove
from pond import rybar
from winter import (winter_hat, pom, mitten, betka, stick_arm, snowman_b, snow_dog, star_print, star_trail, big_print,
                    runner_tracks, red_thread, parsnip, parsnip_crate, small_boots, snowy_house, bare_tree, snow_fence,
                    snow_field, snowfall)
from letter import hand_text

S = 2.2


def _fill(b, g, alpha=None):
    fill([(b.x, b.y), (b.x + b.w, b.y), (b.x + b.w, b.y + b.h), (b.x, b.y + b.h)], g, alpha)


def winter_garden(b, gy, seed=1, house_x=None, house_s=1.0, trees=(), hills_=True):
    sky(b, P.SNOW_SKY)
    if hills_: hills(b, gy + b.h*0.06, 16, P.SNOW_HILL, seed)
    snow_field(b, gy, seed)
    if house_x is not None: snowy_house(b.X(house_x), gy - 4, house_s)
    for i, (tx, ts) in enumerate(trees):
        bare_tree(b.X(tx), gy - 6, ts, seed=seed + i)


# ------------------------------------------------------------------ rooms
def room_garden(b):
    gy = b.Y(0.34)
    winter_garden(b, gy, 51, house_x=0.17, house_s=3.4, trees=((0.52, 2.6), (0.94, 2.2)))
    snow_fence(b.X(0.36), b.X(1.02), gy - 2, 90, 26, gap_at=b.X(0.68))
    snowfall(b, 30, 51, 1.6)


def room_village(b):
    gy = b.Y(0.36)
    winter_garden(b, gy, 52, trees=((0.05, 1.6), (0.5, 1.5)))
    snowy_house(b.X(0.25), gy - 4, 3.0)
    snowy_house(b.X(0.78), gy - 4, 3.2)
    # the road with the tractor's ruts across the front
    fill([(-5, b.Y(0.12)), (b.w + 5, b.Y(0.14)), (b.w + 5, b.Y(0.26)), (-5, b.Y(0.24))], P.SNOW_HILL)
    for yy in (0.16, 0.22):
        s_(bez((-5, b.Y(yy)), (b.X(0.3), b.Y(yy) + 4), (b.X(0.7), b.Y(yy) - 3), (b.w + 5, b.Y(yy) + 2)), BG*2.2, g=0.55)
    hand_text(b.X(0.72), b.Y(0.78), 90, "FRANTA", "SHB", 14, g=0.25)
    snowfall(b, 24, 52, 1.6)


def room_hallway(b):
    planks(b, P.PLANKS, 26, 9, knots=False)
    fy = b.Y(0.27)
    shape([(-5, -5), (b.w + 5, -5), (b.w + 5, fy), (-5, fy)], P.FLOOR, BG)
    for k in range(1, 8): s_([(k*b.w/8 - 30, -5), (k*b.w/8, fy)], BG*0.4)
    # the door out (left), the stove (middle), the doorway with the curtain to the stairs (right)
    dx0, dx1 = b.X(0.03), b.X(0.14)
    shape([(dx0 - 6, fy - 4), (dx1 + 6, fy - 4), (dx1 + 6, b.Y(0.86)), (dx0 - 6, b.Y(0.86))], P.DOOR_FRAME, BG)
    shape([(dx0, fy - 4), (dx1, fy - 4), (dx1, b.Y(0.84)), (dx0, b.Y(0.84))], P.DOOR, BG)
    stove(b.X(0.48), b.X(0.66), fy - 6, b.Y(0.62))
    stroke([(b.X(0.6), b.Y(0.62)), (b.X(0.6), b.h + 5)], 8, g=0.3)
    cx0, cx1 = b.X(0.8), b.X(0.95)
    shape([(cx0, fy - 4), (cx1, fy - 4), (cx1, b.Y(0.86)), (cx0, b.Y(0.86))], 0.25, BG)
    curtain = [(cx0, b.Y(0.86))] + bez((cx0, b.Y(0.86)), (cx0 + 16, b.Y(0.5)), (cx0 + 6, b.Y(0.3)), (cx0 + 20, fy - 4)) + \
              [(cx1, fy - 4), (cx1, b.Y(0.86))]
    shape(curtain, P.CLOTH_CHECK, BG)
    parsnip_crate(b.X(0.27), fy - 6, 2.6)
    parsnip_crate(b.X(0.37), fy - 6, 2.2)
    for k in range(3):
        sh_(rrect(b.X(0.2) + k*90, b.Y(0.68), 60, 40, 4), P.FRAME_WOOD if hasattr(P, "FRAME_WOOD") else P.TABLE)


ROOMS = [("garden5", room_garden), ("village5", room_village), ("hallway5", room_hallway)]


# ------------------------------------------------------------------ slides
def slide_snowmen(b):
    """the three snowmen in a row, read like Franta's picture letter"""
    _fill(b, P.PAPER)
    hand_text(0, b.Y(0.86), b.w, "Sněhuláci jsou dopis!", "SHB", 44, g=0.2)
    gy = b.Y(0.22)
    for k, (fn, label) in enumerate(((lambda x: snowman_b(x, gy, 3.0, right="wave"), "AHOJ"),
                                     (lambda x: (snowman_b(x - 40, gy, 3.0), snow_dog(x + 80, gy, 2.0)), "MÁM RÁDA PEJSKA"),
                                     (lambda x: snowman_b(x, gy, 3.0, right="hold", item=lambda hx, hy: mitten(hx, hy, 1.2)),
                                      "NAŠLA JSEM TOHLE"))):
        x = b.X(0.18 + k*0.32)
        fn(x)
        hand_text(x - 150, b.Y(0.08), 300, label, "SHB", 28, g=0.25)
        if k < 2:
            stroke([(x + 110, b.Y(0.45)), (x + 170, b.Y(0.45))], 3, g=0.3)
            stroke([(x + 158, b.Y(0.48)), (x + 172, b.Y(0.45)), (x + 158, b.Y(0.42))], 3, g=0.3)


SLIDES = [("snowmen_letter", slide_snowmen)]


# ------------------------------------------------------------------ characters
def _w(fn, who, hat, **kw):
    def draw(b):
        fn(b.w/2 + kw.pop("dx", 0), 8, S, shadow=False, **kw)
        winter_hat(b.w/2, 8, S, who, hat, kw.get("flip", False))
    return draw


def _chars():
    out = []
    for mood in ("happy", "grin", "surprised", "think", "worried", "whisper", "talk"):
        out.append((f"alicaw_{mood}", 120, 240, _w(alica, "alica", P.ALICA_WINTER_HAT, mood=mood)))
        out.append((f"hankaw_{mood}", 110, 200, _w(hanka, "hanka", P.HANKA_WINTER_HAT, mood=mood)))
    out += [
        ("alicaw_lens", 150, 240, lambda b: (alica(b.w/2 - 10, 8, S, right="lens", lens=True, mood="determined", shadow=False),
                                             winter_hat(b.w/2 - 10, 8, S, "alica", P.ALICA_WINTER_HAT))),
        ("alicaw_point", 170, 240, lambda b: (alica(b.w/2 - 25, 8, S, right="point", mood="surprised", shadow=False),
                                              winter_hat(b.w/2 - 25, 8, S, "alica", P.ALICA_WINTER_HAT))),
        ("alicaw_walk", 120, 240, lambda b: (alica(b.w/2, 8, S, legs="walk", shadow=False),
                                             winter_hat(b.w/2, 8, S, "alica", P.ALICA_WINTER_HAT))),
        ("hankaw_point", 150, 200, lambda b: (hanka(b.w/2 - 20, 8, S, right="point", mood="wow", shadow=False),
                                              winter_hat(b.w/2 - 20, 8, S, "hanka", P.HANKA_WINTER_HAT))),
        ("hankaw_torch", 150, 200, lambda b: (hanka(b.w/2 - 20, 8, S, right="lens", torch=True, mood="wow", shadow=False),
                                              winter_hat(b.w/2 - 20, 8, S, "hanka", P.HANKA_WINTER_HAT))),
        ("hankaw_walk", 110, 200, lambda b: (hanka(b.w/2, 8, S, legs="walk", shadow=False),
                                             winter_hat(b.w/2, 8, S, "hanka", P.HANKA_WINTER_HAT))),
        ("hankaw_sleepy", 110, 200, lambda b: (hanka(b.w/2, 8, S, mood="sleepy", shadow=False),
                                               winter_hat(b.w/2, 8, S, "hanka", P.HANKA_WINTER_HAT))),
        ("hankaw_nomonkey", 130, 200, lambda b: (hanka(b.w/2 - 10, 8, S, monkey=False, right="front", mood="grin", shadow=False),
                                                 winter_hat(b.w/2 - 10, 8, S, "hanka", P.HANKA_WINTER_HAT))),
    ]
    for mood in ("happy", "talk", "worried", "grin"):
        out.append((f"tondaw_{mood}", 130, 250, _w(tonda, "tonda", P.TONDA_WINTER_HAT, mood=mood)))
    out.append(("tondaw_walk", 130, 250, _w(tonda, "tonda", P.TONDA_WINTER_HAT, legs="walk")))
    for mood in ("happy", "talk", "whisper", "grin", "worried"):
        out.append((f"betka_{mood}", 130, 230, lambda b, m=mood: betka(b.w/2, 8, S*1.1, mood=m, shadow=False)))
    out.append(("betka_walk", 130, 230, lambda b: betka(b.w/2, 8, S*1.1, legs="walk", shadow=False)))
    out.append(("betka_monkey", 160, 230, lambda b: betka(b.w/2, 8, S*1.1, mood="grin", right="front", shadow=False,
                                                          item=lambda x, y: monkey(x + 4, y - 22, 0.8))))
    out.append(("babicka_flour", 150, 270, lambda b: babicka(b.w/2, 8, S, mood="grin", right="front", left="front",
                                                             shadow=False)))
    out.append(("rybar_home", 160, 320, lambda b: rybar(b.w/2, 8, S, mood="happy", hat=False, glasses=True, rod=False,
                                                       shadow=False)))
    out.append(("rybar_hometalk", 160, 320, lambda b: rybar(b.w/2, 8, S, mood="talk", hat=False, glasses=True, rod=False,
                                                           shadow=False)))
    return out


CHARACTERS = _chars()


# ------------------------------------------------------------------ props
PROPS = [
    ("snowman1", 170, 220, lambda b: snowman_b(b.w/2, 8, 2.4, right="wave")),
    ("snowman2", 280, 220, lambda b: (snowman_b(b.w/2 - 50, 8, 2.4), snow_dog(b.w/2 + 90, 8, 1.8))),
    ("snowman3", 200, 220, lambda b: snowman_b(b.w/2 - 14, 8, 2.4, right="hold",
                                               item=lambda x, y: mitten(x, y, 1.0))),
    ("answer", 300, 190, lambda b: (snowman_b(b.w*0.22, 8, 1.9, right="wave", nose="carrot"),
                                    snowman_b(b.w*0.52, 8, 1.1, left="up", right="up", nose="carrot"),
                                    snowman_b(b.w*0.68, 8, 1.1, left="up", right="up", nose="carrot"),
                                    snowman_b(b.w*0.84, 8, 1.1, left="up", right="up", nose="carrot"))),
    ("twig_star", 80, 80, lambda b: [stroke([(b.w/2 + math.cos(math.radians(90 + k*144))*34, b.h/2 + math.sin(math.radians(90 + k*144))*34),
                                             (b.w/2 + math.cos(math.radians(90 + (k + 1)*144))*34, b.h/2 + math.sin(math.radians(90 + (k + 1)*144))*34)],
                                            4, g=P.BARK) for k in range(5)]),
    ("tiny_snowman", 80, 110, lambda b: snowman_b(b.w/2, 8, 1.0, pompom=True)),
    ("star_prints", 220, 70, lambda b: star_trail([(10, 20), (60, 40), (110, 26), (160, 44), (210, 30)], 1.3)),
    ("red_thread", 60, 60, lambda b: red_thread(b.w/2, b.h/2, 2.0)),
    ("mitten_lost", 50, 50, lambda b: mitten(b.w/2, b.h/2, 1.6, rot=30)),
    ("sled_tracks", 260, 60, lambda b: runner_tracks(10, 20, b.w - 10, 34)),
    ("big_prints", 200, 60, lambda b: [big_print(30 + k*50, 22 + (k % 2)*16, 1.3, 90) for k in range(4)]),
    ("small_boots", 120, 70, lambda b: small_boots(b.w/2, 8, 1.6)),
    ("curtain_peek", 80, 120, lambda b: (pom(b.w/2, b.h - 30, 14), stroke([(b.w/2, b.h - 46), (b.w/2, b.h - 60)], 3))),
]

ITEMS = [
    ("mitten_icon", 60, 60, lambda b: mitten(b.w/2, b.h/2, 1.6)),
]


# ------------------------------------------------------------------ minigame tiles (64 x 64): the snowman game
def _snow(b, seed=1):
    fill([(0, 0), (b.w, 0), (b.w, b.h), (0, b.h)], P.SNOW)
    r = random.Random(seed)
    for _ in range(5):
        x, y = r.uniform(6, 58), r.uniform(6, 58)
        stroke(bez((x - 5, y), (x - 2, y + 2), (x + 2, y + 2), (x + 5, y)), BG*0.6, g=0.82)


def _cleared(b):
    fill([(0, 0), (b.w, 0), (b.w, b.h), (0, b.h)], P.GRASS)
    r = random.Random(3)
    for _ in range(6):
        x, y = r.uniform(6, 58), r.uniform(6, 58)
        fill(ell(x, y, 3, 2, 10), P.SNOW, 0.8)
    for dx in (-3, 0, 3): stroke([(32 + dx, 30), (32 + dx*1.6, 36)], BG*0.7, g=P.TUFT)


def _bush(b):
    _snow(b, 5)
    cast_shadow(b.w/2, 12, 22, 4)
    for (dx, dy, r) in ((-10, 24, 13), (10, 24, 13), (0, 34, 15)):
        shape(ell(b.w/2 + dx, dy, r, r*0.85, 24), P.KRASLICE_GREEN, LINE*0.8)
    for (dx, dy, r) in ((-8, 34, 7), (8, 36, 6), (0, 44, 6)):
        fill(ell(b.w/2 + dx, dy, r, r*0.5, 16), P.SNOW)


def _ball(b, r):
    cast_shadow(b.w/2, b.h/2 - r*0.8, r*0.9, r*0.25)
    shape(ell(b.w/2, b.h/2, r, r, 36), P.SNOW, LINE)
    fill(ell(b.w/2 + r*0.25, b.h/2 - r*0.3, r*0.7, r*0.6, 24), 0.9, 0.5)
    stroke(bez((b.w/2 - r*0.6, b.h/2 + r*0.2), (b.w/2 - r*0.5, b.h/2 + r*0.5), (b.w/2 - r*0.2, b.h/2 + r*0.65), (b.w/2, b.h/2 + r*0.66)),
           LINE*0.6, g=1.0)


def _stack(b, n):
    sizes = [20, 14, 9][:n]
    y = 6
    for k, r in enumerate(sizes):
        shape(ell(b.w/2, y + r*0.9, r*0.9, r*0.9, 32), P.SNOW, LINE)
        y += r*1.5
    if n == 3:
        cy = y - 13*0.6
        for sx in (-1, 1): dot(b.w/2 + sx*4, cy + 2, 1.4, 0.15)
        shape([(b.w/2, cy - 2), (b.w/2 + 12, cy - 4), (b.w/2, cy - 5)], P.CARROT if hasattr(P, "CARROT") else P.CRAYON_ORANGE, LINE*0.5)


def _mitten_tile(b, kind):
    """a mitten for "Čí je rukavice?": the same knitted mitten, told apart only by its pattern"""
    mitten(b.w/2 - 2, 14, 3.4, g=P.PAPER)
    with T(b.w/2 - 2, 14, 3.4):
        if kind == "star":
            star(0, 6.5, 3.0, P.CRAYON_ORANGE)
        elif kind == "stripe":
            for yy in (3.5, 6.5, 9.5):
                stroke([(-4.2, yy), (4.2, yy)], LINE*0.6, g=P.CRAYON_BLUE, taper=False)
        elif kind == "heart":
            shape(bez((0, 3.5), (-4, 6.5), (-2.5, 9.5), (0, 8)) + bez((0, 8), (2.5, 9.5), (4, 6.5), (0, 3.5)), P.CRAYON_RED,
                  LINE*0.4)
        else:
            for dx, dy in ((-2, 4), (1.6, 5.5), (-1.2, 8), (2, 9.6), (0.3, 2)):
                dot(dx, dy, 0.9, P.CRAYON_GREEN)


def _who_card(b):
    fill([(0, 0), (b.w, 0), (b.w, b.h), (0, b.h)], P.PAPER)


def _pompom_card(b):
    _who_card(b)
    fill(ell(b.w/2, 26, 16, 24, 30), 0.35)
    fill(ell(b.w/2, 52, 9, 9, 24), 0.35)
    pom(b.w/2, 62, 6)
    hand_text(0, 30, b.w, "?", "SHB", 22, g=1.0)


MG = [
    ("snow", lambda b: _snow(b, 1)), ("snow_b", lambda b: _snow(b, 7)), ("cleared", _cleared), ("snowbush", _bush),
    ("ball1", lambda b: _ball(b, 11)), ("ball2", lambda b: _ball(b, 17)), ("ball3", lambda b: _ball(b, 24)),
    ("stack2", lambda b: _stack(b, 2)), ("stack3", lambda b: _stack(b, 3)),
    ("who_tonda5", lambda b: (_who_card(b), tonda(b.w/2, -60, 1.05, mood="happy", shadow=False),
                              winter_hat(b.w/2, -60, 1.05, "tonda", P.TONDA_WINTER_HAT))),
    ("who_babicka5", lambda b: (_who_card(b), babicka(b.w/2, -70, 0.95, mood="grin", shadow=False))),
    ("who_joey5", lambda b: (_who_card(b), joey(b.w/2 - 4, 6, 1.2, collar=False, shadow=False))),
    ("who_pompom", _pompom_card),
    ("clue_starprint", lambda b: (_snow(b), star_print(b.w/2, b.h/2, 1.9, 10))),
    ("clue_parsnip", lambda b: (_who_card(b), parsnip(b.w/2 - 16, b.h/2, 1.6, 20))),
    ("clue_thread", lambda b: (_who_card(b), red_thread(b.w/2, b.h/2, 2.0))),
    ("clue_boots", lambda b: (_who_card(b), small_boots(b.w/2, 10, 1.2))),
    ("who_alica5", lambda b: (_who_card(b), alica(b.w/2, -68, 1.2, mood="grin", shadow=False),
                              winter_hat(b.w/2, -68, 1.2, "alica", P.ALICA_WINTER_HAT))),
    ("who_hanka5", lambda b: (_who_card(b), hanka(b.w/2, -40, 1.2, mood="grin", shadow=False),
                              winter_hat(b.w/2, -40, 1.2, "hanka", P.HANKA_WINTER_HAT))),
    ("m_star", lambda b: _mitten_tile(b, "star")), ("m_stripe", lambda b: _mitten_tile(b, "stripe")),
    ("m_heart", lambda b: _mitten_tile(b, "heart")), ("m_dots", lambda b: _mitten_tile(b, "dots")),
]


def COVER(s):
    sky(s, P.SNOW_SKY)
    gy = s.Y(0.3)
    hills(s, gy + 10, 10, P.SNOW_HILL, 3)
    snow_field(s, gy, 3)
    snowman_b(s.X(0.62), s.Y(0.12), 0.9, right="wave")
    star_trail([(s.X(0.1), s.Y(0.08)), (s.X(0.25), s.Y(0.14)), (s.X(0.4), s.Y(0.1))], 0.6)
    alica(s.X(0.25), s.Y(0.04), 0.9, mood="think", right="lens", lens=True, look=(1, -0.3), shadow=False)
    winter_hat(s.X(0.25), s.Y(0.04), 0.9, "alica", P.ALICA_WINTER_HAT)
    pom(s.X(0.9), s.Y(0.42), 6)
    snowfall(s, 16, 3, 1.2)
