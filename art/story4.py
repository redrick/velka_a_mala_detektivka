"""Game art for story 4 "Hanka to vyřeší!": Alica's sickroom, the village with the old henhouse and the church
clock stopped at three, the field with the Bota rock, the jetty; the sexton and Alica in bed as characters; the
clue props, the slides (inside the old henhouse, the view from the tower, little Franta's flashback) and the
pictures for the gears minigame and the "Kdo šel po stopě?" round."""
import math, random
import lib
from lib import ell, bez, rrect
import palette as P
from style3 import *
from style3 import C
from chars3 import star, babicka, deda, tonda, magpie, torch
from scenes3 import BG, s_, sh_, sky, hills, ground, house, tree, cloud, fence, falling_leaves, tufts, planks
from props_extra import stream, stone, mug
from attic import bed_side, blanket_side, young, old_photo
from pond import (far_trees, pond_bg, mill, jetty, bench, rybar, treasure_tin, marbles, picture_letter, torch_beam,
                  verka_old, reeds, duck, mud_patch)
from village import (old_henhouse, henhouse, church, church_clock, clockwork, gear, boot_rock, kostelnik, vysilacka,
                     zig_print, splavek, clock_key, hen_whistle, new_letter, bucket_hat, candy_wrapper, letter_hen,
                     moving_van)
from velikonoce import stodola
from letter import hand_text

S = 2.2   # character scale, as in export_assets.py


def _fill(b, g, alpha=None):
    fill([(b.x, b.y), (b.x + b.w, b.y), (b.x + b.w, b.y + b.h), (b.x, b.y + b.h)], g, alpha)


# ------------------------------------------------------------------ rooms (960 x 540 pt; the floor is the lowest ~27 %)
def room_sickroom(b):
    _fill(b, P.BEDROOM_WALL)
    fy = b.Y(0.27)
    for xx in range(14, int(b.w), 30): stroke([(xx, fy), (xx, b.h)], 0.5, g=0.82)
    shape([(-5, -5), (b.w + 5, -5), (b.w + 5, fy), (-5, fy)], P.FLOOR, BG)
    for k in range(1, 8): s_([(k*b.w/8 - 40, -5), (k*b.w/8 + 10, fy)], BG*0.4)
    x0, x1, y0, y1 = b.X(0.06), b.X(0.26), b.Y(0.5), b.Y(0.88)
    shape([(x0 - 6, y0 - 6), (x1 + 6, y0 - 6), (x1 + 6, y1 + 6), (x0 - 6, y1 + 6)], P.DOOR_FRAME, BG)
    shape([(x0, y0), (x1, y0), (x1, y1), (x0, y1)], P.NOV_SKY, BG)
    stroke(bez((x0, y0 + 20), (x0 + 50, y0 + 44), (x0 + 100, y0 + 60), (x1, y0 + 88)), 3, g=P.BARK)
    s_([((x0 + x1)/2, y0), ((x0 + x1)/2, y1)], BG*1.6, g=1.0); s_([(x0, (y0 + y1)/2), (x1, (y0 + y1)/2)], BG*1.6, g=1.0)
    # the door on the right
    dx0, dx1 = b.X(0.86), b.X(0.97)
    shape([(dx0 - 6, fy - 4), (dx1 + 6, fy - 4), (dx1 + 6, b.Y(0.86)), (dx0 - 6, b.Y(0.86))], P.DOOR_FRAME, BG)
    shape([(dx0, fy - 4), (dx1, fy - 4), (dx1, b.Y(0.84)), (dx0, b.Y(0.84))], P.DOOR, BG)
    shape(ell(dx0 + 12, b.Y(0.5), 4, 4, 12), 0.85, LINE*0.6)
    # the bedside table: tea and tissues
    tx = b.X(0.4)
    with T(tx, fy - 8, 2.0):
        form([(-34, 50), (34, 50), (34, 56), (-34, 56)], P.TABLE, w=BG, sh=0)
        for lx in (-28, 24): sh_([(lx, 0), (lx + 5, 0), (lx + 5, 50), (lx, 50)], P.TABLE)
        mug(-12, 56, 1.3)
        shape(rrect(4, 56, 24, 14, 2), 0.95, BG)
        shape(bez((12, 70), (14, 80), (20, 78), (18, 70)) + [(12, 70)], 1.0, BG*0.8)
    from attic import kids_drawing
    kids_drawing(b.X(0.55), b.Y(0.72), 50, 38, 3)


def room_village(b):
    sky(b, P.NOV_SKY)
    gy = b.Y(0.32)
    hills(b, gy + b.h*0.08, 22, 0.87, 41)
    cloud(b.X(0.4), b.Y(0.9), 0.8)
    ground(b, gy, P.GRASS)
    tree(b.X(0.57), gy - 6, 1.8, seed=7, g=P.LEAF_DARK)
    stodola(b.X(0.1), gy - 2, 1.6)
    old_henhouse(b.X(0.29), gy - 4, 2.2)
    henhouse(b.X(0.45), gy - 6, 1.6)
    church(b.X(0.76), gy - 2, 2.6)
    bench(b.X(0.6), gy - 34, 1.4)
    s_(bez((b.X(0.5), -5), (b.X(0.58), gy*0.5), (b.X(0.72), gy - 10), (b.X(0.98), gy - 6)), BG*0.6)
    falling_leaves(b, 6, 41)
    tufts(b, 6, gy - 20, 14, 4)


def room_field(b):
    sky(b, P.NOV_SKY)
    hy = b.Y(0.6)
    far_trees(b, hy + 4, 7, P.LEAF_DARK)
    fill([(-5, -5), (b.w + 5, -5), (b.w + 5, hy), (-5, hy)], P.FIELD)
    s_([(-5, hy), (b.w + 5, hy)], BG)
    r = random.Random(7)
    for k in range(4):
        yy = b.Y(0.34) + (hy - b.Y(0.34))*(0.2 + k*0.22) + r.uniform(-4, 4)
        s_(bez((-5, yy), (b.X(0.3), yy + 6), (b.X(0.7), yy - 6), (b.w + 5, yy + 2)), BG*0.5, g=P.FIELD_DARK)
    stream(b, b.Y(0.36), b.Y(0.42))
    fill([(-5, -5), (b.w + 5, -5), (b.w + 5, b.Y(0.35)), (-5, b.Y(0.35))], P.GRASS)
    s_([(-5, b.Y(0.35)), (b.w + 5, b.Y(0.35))], BG)
    for tx in (0.04, 0.2, 0.86):
        tree(b.X(tx), b.Y(0.3), 1.2, seed=int(tx*100), g=P.LEAF_DARK)
    stone(b.X(0.3), b.Y(0.3), 34, 18)
    stone(b.X(0.45), b.Y(0.36), 22, 12)
    stone(b.X(0.86), b.Y(0.27), 40, 20)
    boot_rock(b.X(0.64), b.Y(0.26), 1.9, view="front", crack=True)
    tufts(b, 6, b.Y(0.28), 14, 9)


def room_jetty(b):
    fy = pond_bg(b, 0.3, 0.62, seed=44)
    mill(b.X(0.88), fy + 4, 0.55)
    jetty(b.X(0.5), b.X(0.72), b.Y(0.36), 14)
    reeds(b.X(0.08), b.Y(0.3), 1.2, seed=3)
    reeds(b.X(0.95), b.Y(0.3), 1.0, seed=5)
    duck(b.X(0.32), b.Y(0.45), 0.9)
    tufts(b, 6, b.Y(0.26), 12, 5)


ROOMS = [("sickroom4", room_sickroom), ("village4", room_village), ("field4", room_field), ("jetty4", room_jetty)]


# ------------------------------------------------------------------ slides (960 x 540)
def slide_henhouse(b):
    _fill(b, 0.12)
    for k in range(7): stroke([(b.X(k/7 + 0.04), 0), (b.X(k/7 + 0.02), b.h)], BG*2, g=0.25)
    shape([(-5, b.Y(0.55)), (b.w + 5, b.Y(0.53)), (b.w + 5, b.Y(0.7)), (-5, b.Y(0.72))], 0.32, BG*1.5)
    torch_beam(b.X(0.1), b.Y(0.05), b.X(0.35), b.Y(1.0), b.X(0.95), b.Y(0.35), 0.5)
    with T(b.X(0.36), b.Y(0.6), 6.5):
        letter_hen(0, 0, LINE*0.9, 0.2)
        star(26, 2, 7, 1.0, w=LINE*0.9)
        stroke([(40, -8), (40, 10), (50, 10)], LINE*1.1); stroke([(40, 1), (47, 1)], LINE*1.1)


def tower_view(b, seed=3):
    sky(b, P.NOV_SKY)
    hy = b.Y(0.72)
    far_trees(b, hy + 4, seed)
    fill([(-5, -5), (b.w + 5, -5), (b.w + 5, hy), (-5, hy)], P.FIELD)
    for k_, g in enumerate((P.FIELD_DARK, P.GRASS, P.FIELD_DARK, P.GRASS)):
        x0 = -10 + k_*b.w*0.28
        fill([(x0, -5), (x0 + b.w*0.25, -5), (x0 + b.w*0.36, hy - 30), (x0 + b.w*0.14, hy - 30)], g)
    s_([(-5, hy), (b.w + 5, hy)], BG)
    stroke(bez((b.X(0.1), -5), (b.X(0.3), b.Y(0.3)), (b.X(0.55), b.Y(0.45)), (b.X(0.7), hy - 6)), 6, g=P.WATER)
    for tx in (0.6, 0.66, 0.9, 0.96):
        tree(b.X(tx), hy - 16, 0.55, seed=int(tx*100), g=P.LEAF_DARK)


def slide_tower(b):
    tower_view(b, 5)
    boot_rock(b.X(0.76), b.Y(0.6), 2.0, view="side")
    # the clock face in front, its little hand pointing at the rock
    cx, cy = b.X(0.12), b.Y(0.1)
    shape(ell(cx, cy, 190, 190, 60), P.CLOCK_FACE, LINE*2)
    stroke(ell(cx, cy, 172, 172, 60), LINE, closed=True, g=0.4)
    for k in range(12):
        a = math.radians(90 - k*30)
        dot(cx + math.cos(a)*160, cy + math.sin(a)*160, 4, 0.2)
    ang = math.atan2(b.Y(0.66) + 20 - cy, b.X(0.78) - cx)
    stroke([(cx, cy), (cx + math.cos(ang)*150, cy + math.sin(ang)*150)], 12, g=0.1)
    stroke([(cx, cy), (cx, cy + 165)], 7, g=0.1)
    for sgn in (1, -1):
        stroke([(b.X(0.7), b.Y(0.82) + sgn*20), (b.X(0.75), b.Y(0.75))], 5, g=P.CRAYON_RED)


def tower_room(b):
    _fill(b, 0.7)
    for yy in range(0, int(b.h), 18):
        for xx in range(-(18 if (yy//18) % 2 else 0), int(b.w), 36):
            shape(rrect(xx + 1, yy + 1, 34, 16, 2), P.STONE_BASE, BG*0.5)


def slide_franta_key(b):
    tower_room(b)
    clockwork(b.X(0.66), b.Y(0.12), 3.2)
    young(b.X(0.25), b.Y(0.05), 3.0, "franta", mood="grin", right="up", look=(1, 0),
          item=lambda x, y: clock_key(x - 6, y + 2, 0.7, rot=20))
    old_photo(b)


def slide_franta_rock(b):
    sky(b, P.NOV_SKY)
    hy = b.Y(0.55)
    far_trees(b, hy + 4, 12)
    fill([(-5, -5), (b.w + 5, -5), (b.w + 5, hy), (-5, hy)], P.FIELD)
    boot_rock(b.X(0.62), b.Y(0.1), 2.8, crack=True)
    young(b.X(0.26), b.Y(0.06), 2.8, "franta", mood="happy", right="front", look=(1, 0),
          item=lambda x, y: picture_letter(x - 14, y - 10, 0.35, rot=-5))
    treasure_tin(b.X(0.45), b.Y(0.06), 1.0)
    old_photo(b)


def slide_franta_van(b):
    sky(b, P.NOV_SKY)
    gy = b.Y(0.2)
    hills(b, gy + b.h*0.08, 18, 0.87, 13)
    house(b.X(0.15), gy - 2, 1.8, smoke=False)
    ground(b, gy, P.GRASS)
    moving_van(b.X(0.6), b.Y(0.08), 3.0)
    young(b.X(0.25), b.Y(0.06), 2.8, "franta", mood="sad", right="wave", look=(1, 0))
    old_photo(b)


SLIDES = [("henhouse_inside", slide_henhouse), ("tower_view4", slide_tower), ("franta_key", slide_franta_key),
          ("franta_rock", slide_franta_rock), ("franta_van", slide_franta_van)]


# ------------------------------------------------------------------ characters (feet at bottom centre)
def _alica_bed(b, **kw):
    k = S/1.2
    with T(b.w/2 + 40, 8, k):
        top = 34
        x0, x1 = -110, 62
        bed_side(x0, x1, top)
        ax = x1 - 30; waist = top + 8; ay = waist - 45*1.2
        C.saveState()
        C.clipPath(poly([(x0 - 80, top - 10), (x1 + 80, top - 10), (x1 + 80, top + 500), (x0 - 80, top + 500)]), stroke=0, fill=0)
        alica(ax, ay, 1.2, shadow=False, **kw)
        C.restoreState()
        blanket_side(x0, ax + 14, top, waist + 4)


def _chars():
    out = []
    for mood in ("happy", "talk", "surprised", "worried"):
        out.append((f"kostelnik_{mood}", 150, 300, lambda b, m=mood: kostelnik(b.w/2, 8, S, mood=m, shadow=False)))
    out.append(("kostelnik_walk", 150, 300, lambda b: kostelnik(b.w/2, 8, S, legs="walk", shadow=False)))
    out.append(("kostelnik_galoshes", 170, 300, lambda b: kostelnik(b.w/2, 8, S, mood="grin", right="point", shadow=False)))
    for mood, kw in (("bed", dict(mood="worried")), ("bed_talk", dict(mood="talk")), ("bed_grin", dict(mood="grin")),
                     ("bed_lens", dict(mood="think", right="lens", lens=True)),
                     ("bed_radio", dict(mood="talk", right="front", item=lambda x, y: vysilacka(x, y - 4, 1.0)))):
        out.append((f"alica_{mood}", 360, 240, lambda b, kw=kw: _alica_bed(b, **kw)))
    out.append(("rybar_nohat", 190, 320, lambda b: rybar(b.w/2, 8, S, mood="grin", hat=False, glasses=True, rod=False,
                                                        right="up", item=lambda x, y: bucket_hat(x, y + 4, 0.9), shadow=False)))
    out.append(("rybar_grin", 160, 320, lambda b: rybar(b.w/2, 8, S, mood="grin", rod=False, shadow=False)))
    out.append(("hanka_radio", 150, 200, lambda b: hanka(b.w/2 - 10, 8, S, mood="talk", right="front", shadow=False,
                                                        item=lambda x, y: vysilacka(x, y - 4, 1.0))))
    return out


CHARACTERS = _chars()


# ------------------------------------------------------------------ props and items
def zig_group(b):
    mud_patch(b.w/2, b.h/2, b.w*0.46, b.h*0.4)
    zig_print(b.w*0.4, b.h*0.42, 1.4, 70)
    zig_print(b.w*0.64, b.h*0.6, 1.4, 64)


PROPS = [
    ("zig_prints", 150, 80, zig_group),
    ("splavek", 40, 50, lambda b: splavek(b.w/2, 12, 1.4, rot=-20)),
    ("wrapper", 40, 24, lambda b: candy_wrapper(b.w/2, b.h/2, 1.6, rot=15)),
    ("magpie_fly", 90, 60, lambda b: magpie(b.w/2, 10, 1.6, item=lambda x, y: candy_wrapper(x + 3, y, 0.8))),
    ("tin_closed", 120, 80, lambda b: treasure_tin(b.w/2, 6, 1.6)),
    ("tin_open4", 140, 100, lambda b: treasure_tin(b.w/2, 6, 1.8, open_=True)),
    ("clock_key", 110, 50, lambda b: clock_key(14, b.h/2, 1.8)),
    ("hen_whistle", 80, 50, lambda b: hen_whistle(b.w/2 + 6, 12, 1.6)),
    ("marbles", 60, 40, lambda b: marbles(b.w/2 - 8, 12, 2.4)),
    ("new_letter", 150, 110, lambda b: new_letter(8, 6, 1.5)),
    ("church_clock_big", 120, 120, lambda b: church_clock(b.w/2, b.h/2, 54)),
]

ITEMS = [
    ("radio_icon", 60, 80, lambda b: vysilacka(b.w/2, 10, 2.2)),
    ("tin_icon", 100, 70, lambda b: treasure_tin(b.w/2, 6, 1.3)),
    ("newletter_icon", 100, 80, lambda b: new_letter(4, 4, 1.0)),
    ("clockkey_icon", 100, 50, lambda b: clock_key(12, b.h/2, 1.5)),
]


# ------------------------------------------------------------------ minigame pictures (64 x 64 pt)
def _card(b, g=P.PAPER):
    fill([(0, 0), (b.w, 0), (b.w, b.h), (0, b.h)], g)


def _stone_wall(b):
    fill([(0, 0), (b.w, 0), (b.w, b.h), (0, b.h)], P.STONE_BASE)
    for yy in range(0, 64, 16):
        for xx in range(-(16 if (yy//16) % 2 else 0), 64, 32):
            stroke(rrect(xx + 1, yy + 1, 30, 14, 2), BG*0.6, closed=True, g=0.45)


def _peg(b):
    fill(ell(b.w/2, b.h/2, 7, 7, 16), 0.35)
    fill(ell(b.w/2 - 1.5, b.h/2 + 1.5, 2.5, 2.5, 10), 0.75)


def _gear(b, g):
    gear(b.w/2, b.h/2, 27, 12, g)
    shape(ell(b.w/2, b.h/2, 7, 7, 16), 0.3, LINE*0.8)
    for a in (0, 120, 240):
        ra = math.radians(a)
        stroke([(b.w/2 + math.cos(ra)*9, b.h/2 + math.sin(ra)*9), (b.w/2 + math.cos(ra)*20, b.h/2 + math.sin(ra)*20)],
               LINE*1.6, g=0.25)


def _key_gear(b):
    _gear(b, P.CLOCK_GOLD)
    clock_key(b.w/2 + 10, b.h/2 - 18, 0.55, rot=0)


def _hands_gear(b):
    shape(ell(b.w/2, b.h/2, 29, 29, 40), P.CLOCK_FACE, LINE)
    for k in range(12):
        a = math.radians(90 - k*30)
        dot(b.w/2 + math.cos(a)*24, b.h/2 + math.sin(a)*24, 1.4, 0.2)
    stroke([(b.w/2, b.h/2), (b.w/2 + 13, b.h/2 - 6)], LINE*2.6, g=0.1)
    stroke([(b.w/2, b.h/2), (b.w/2, b.h/2 + 21)], LINE*1.8, g=0.1)
    dot(b.w/2, b.h/2, 2.4, 0.1)


def _dir_arrow(b, cw=True):
    pts = [(b.w/2 + math.cos(math.radians(a))*24, b.h/2 + math.sin(math.radians(a))*24) for a in range(150, 20, -10)]
    if not cw: pts = pts[::-1]
    stroke(pts, LINE*2.6, g=P.KRASLICE_GREEN if cw else P.CRAYON_RED)
    ex, ey = pts[-1]; px, py = pts[-3]
    ang = math.atan2(ey - py, ex - px)
    for da in (2.5, -2.5):
        stroke([(ex, ey), (ex - math.cos(ang + da*0.25)*9, ey - math.sin(ang + da*0.25)*9)], LINE*2.6,
               g=P.KRASLICE_GREEN if cw else P.CRAYON_RED)


MG = [
    ("tower_wall", _stone_wall),
    ("peg", lambda b: (_stone_wall(b), _peg(b))),
    ("gear", lambda b: _gear(b, P.IRON)),
    ("gear_fixed", lambda b: _gear(b, P.WOOD_TOY)),
    ("gear_key", _key_gear),
    ("gear_hands", _hands_gear),
    ("turn_cw", lambda b: _dir_arrow(b, True)),
    ("turn_ccw", lambda b: _dir_arrow(b, False)),
    ("who_kostelnik", lambda b: (_card(b), kostelnik(b.w/2, -72, 0.95, mood="worried", shadow=False))),
    ("who_straka", lambda b: (_card(b), magpie(b.w/2 - 4, 16, 1.4, item=lambda x, y: candy_wrapper(x + 3, y, 0.8)))),
    ("who_tonda4", lambda b: (_card(b), tonda(b.w/2, -60, 1.05, mood="happy", shadow=False))),
    ("who_rybar4", lambda b: (_card(b), rybar(b.w/2, -80, 0.95, mood="happy", shadow=False, rod=False))),
    ("clue_zig", lambda b: (_card(b, P.MUD), zig_print(b.w/2, b.h/2, 1.5, 80))),
    ("clue_splavek", lambda b: (_card(b), splavek(b.w/2, 18, 1.6, rot=-15))),
    ("clue_clock3", lambda b: (_card(b), church_clock(b.w/2, b.h/2, 24))),
    ("clue_letter", lambda b: (_card(b), new_letter(4, 14, 0.6))),
    ("rad_rock", lambda b: (cast_shadow(b.w/2, 14, 24, 5), stone(b.w/2, 26, 23, 17))),
    ("rad_bota", lambda b: (cast_shadow(b.w/2, 10, 28, 5), boot_rock(b.w/2, 10, 0.55, view="side"))),
]


# ------------------------------------------------------------------ menu cover
def COVER(s):
    sky(s, P.NOV_SKY)
    gy = s.Y(0.3)
    hills(s, gy + 12, 10, 0.87, 4)
    ground(s, gy, P.GRASS)
    church(s.X(0.72), gy - 2, 0.75)
    boot_rock(s.X(0.3), gy - 6, 0.5, view="side")
    hanka(s.X(0.4), s.Y(0.04), 0.95, mood="wow", right="front", look=(1, 0.3), shadow=False,
          item=lambda x, y: vysilacka(x, y - 4, 0.6))
