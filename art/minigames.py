"""Tiles and pieces for the logic minigames (game only). Each is drawn on a 64 x 64 pt box
(128 px after export) seen slightly from above, so boards are plain grids."""
import math, random
import lib
from lib import ell, bez, rrect
import palette as P
from style3 import *
from chars3 import star
from letter import hand_text
from scenes3 import BG, s_, sh_
from props_extra import flour_bag, pumpkin, stone
from attic import owlet, chest
from pond import reeds, stump, star_stone, water as pond_water, mud_patch


def _grass(b, g=P.GRASS, seed=1, tufts=3):
    fill([(0, 0), (b.w, 0), (b.w, b.h), (0, b.h)], g)
    r = random.Random(seed)
    for _ in range(tufts):
        x, y = r.uniform(8, b.w - 8), r.uniform(8, b.h - 8)
        for dx in (-2.5, 0, 2.5):
            stroke([(x + dx, y), (x + dx*1.6, y + 5)], BG*0.7, g=P.TUFT)


def grass(b): _grass(b, seed=3)


def grass_b(b): _grass(b, seed=8, tufts=2)


def flowerpot(b):
    _grass(b, seed=5, tufts=0)
    cast_shadow(b.w/2, 10, 20, 4)
    shape([(b.w/2 - 17, 38), (b.w/2 + 17, 38), (b.w/2 + 12, 10), (b.w/2 - 12, 10)], P.ROOF, LINE)
    shape([(b.w/2 - 19, 38), (b.w/2 + 19, 38), (b.w/2 + 19, 44), (b.w/2 - 19, 44)], P.ROOF_EDGE, LINE)
    for dx, dy, g in ((-8, 50, P.FLOWER), (6, 54, P.LEAF_LIGHT), (0, 58, P.FLOWER)):
        stroke([(b.w/2 + dx*0.4, 44), (b.w/2 + dx, dy - 3)], LINE, g=P.TUFT)
        shape(ell(b.w/2 + dx, dy, 5, 5, 16), g, LINE*0.8)


def pumpkin_tile(b):
    _grass(b, seed=6, tufts=0)
    cast_shadow(b.w/2, 12, 24, 4)
    pumpkin(b.w/2, 10, 1.9)


def bush(b):
    _grass(b, seed=7, tufts=0)
    cast_shadow(b.w/2, 10, 26, 4)
    pts = []
    for i in range(12):
        a = math.tau*i/12; k = 1 + 0.12*math.sin(i*2.3)
        pts.append((b.w/2 + math.cos(a)*25*k, 32 + math.sin(a)*21*k))
    shape(pts, P.BUSH, LINE)
    for (x, y) in ((22, 36), (38, 30), (30, 44), (44, 40)):
        shape(ell(x, y, 2.6, 2.6, 10), P.BERRY, LINE*0.6)


def sack(b):
    cast_shadow(b.w/2, 9, 20, 4)
    flour_bag(b.w/2, 7, 1.45)


def sack_done(b):
    fill(ell(b.w/2, 14, 28, 10, 30), P.FLOUR_PRINT)
    stroke(ell(b.w/2, 14, 28, 10, 30), BG*0.6, closed=True, g=0.6)
    flour_bag(b.w/2, 9, 1.35)
    for (x, y) in ((10, 8), (54, 12), (16, 22), (50, 24)):
        dot(x, y, 1.6, 0.95)


def target_prints(b):
    _grass(b, seed=9, tufts=0)
    for i, (x, y) in enumerate(((20, 18), (30, 28), (38, 36), (48, 46))):
        with T(x, y, 1, rot=35):
            fill(ell(0, 0, 2.3, 3.0, 12), P.FOOTPRINT)
            for t in range(4):
                a = math.radians(50 + t*27)
                dot(math.cos(a)*4.4, math.sin(a)*4.4, 0.9, P.FOOTPRINT)
    dash = lib.resample(ell(b.w/2, b.h/2, 27, 27, 40), 1.0, True)
    for i in range(0, len(dash) - 3, 7):
        stroke(dash[i:i + 4], 1.2, g=0.3)


def planks_tile(b):
    fill([(0, 0), (b.w, 0), (b.w, b.h), (0, b.h)], P.ATTIC_FLOOR)
    for x in (0, 21, 42, 64):
        stroke([(x, 0), (x, b.h)], BG*1.1)
    dot(10, 44, 1.2, 0.3); dot(52, 14, 1.2, 0.3)


def plank_star(b):
    planks_tile(b)
    fill(ell(b.w/2, b.h/2, 22, 17, 30), P.SUNBEAM, 0.9)
    star(b.w/2, b.h/2, 12, 0.98)


def mirror(b):
    """a small standing mirror, turned like '/' (bottom-left to top-right)"""
    with T(b.w/2, b.h/2, 1, rot=45):
        form(rrect(-30, -7, 60, 14, 5), P.CHEST, sdx=0, sdy=-1.5)
        shape(rrect(-27, -4, 54, 8, 3), P.GLASS, LINE*0.8)
        stroke([(-18, 1.5), (-6, 1.5)], LINE*1.4, g=1.0)
    dot(b.w/2, b.h/2, 3.2, P.BRASS)


def sun_window(b):
    fill([(0, 0), (b.w, 0), (b.w, b.h), (0, b.h)], P.ATTIC_WALL)
    shape(ell(b.w/2, b.h/2, 25, 25, 40), P.SHUTTER, LINE*1.2)
    pts = []
    for i in range(10):
        a = math.pi/2 + i*math.pi/5; rr = 17 if i % 2 == 0 else 7
        pts.append((b.w/2 + math.cos(a)*rr, b.h/2 + math.sin(a)*rr))
    shape(pts, P.SUNBEAM, LINE)


def crate_tile(b):
    planks_tile(b)
    form([(8, 6), (56, 6), (56, 50), (8, 50)], P.CRATE, sdx=3, sdy=0)
    for y in (20, 35): s_([(8, y), (56, y)], BG*0.7)
    stroke([(8, 6), (56, 50)], BG*0.7); stroke([(56, 6), (8, 50)], BG*0.7)


def owlet_tile(b):
    planks_tile(b)
    fill(ell(b.w/2, 12, 22, 6, 20), 0.0, 0.12)
    owlet(b.w/2, 10, 1.7, mood="sleepy")


def owlet_awake(b):
    planks_tile(b)
    fill(ell(b.w/2, 12, 22, 6, 20), 0.0, 0.12)
    owlet(b.w/2, 10, 1.7, mood="wide")


def pond_grass(b): _grass(b, P.GRASS, seed=11, tufts=2)


def pond_water_tile(b):
    fill([(0, 0), (b.w, 0), (b.w, b.h), (0, b.h)], P.POND_WATER)
    r = random.Random(4)
    for _ in range(3):
        x, y = r.uniform(10, 50), r.uniform(10, 54)
        stroke([(x, y), (x + 8, y + 1), (x + 16, y)], BG*1.2, g=P.POND_RIPPLE)


def reeds_tile(b):
    _grass(b, seed=12, tufts=0)
    fill(ell(b.w/2, 10, 26, 7, 20), P.MUD)
    reeds(b.w/2 + 2, 8, 1.2, seed=3, n=8)


def stump_tile(b):
    _grass(b, seed=13, tufts=0)
    stump(b.w/2, 14, 0.9)


def goal_tile(b):
    _grass(b, seed=14, tufts=0)
    star_stone(b.w/2, 20, 1.5, grass=True)


def arrow(b, rot=0):
    """arrow pointing right (rot=0), for the step programme; rot turns it counter-clockwise"""
    with T(b.w/2, b.h/2, 1, rot=rot):
        pts = [(-22, -6), (4, -6), (4, -18), (24, 0), (4, 18), (4, 6), (-22, 6)]
        shape(pts, P.BUTTON, LINE*1.6)


def slot(b):
    shape(rrect(4, 4, b.w - 8, b.h - 8, 10), 0.95, LINE)


TILES = [("grass", grass), ("grass_b", grass_b), ("flowerpot", flowerpot), ("pumpkin", pumpkin_tile), ("bush", bush),
         ("sack", sack), ("sack_done", sack_done), ("target", target_prints),
         ("planks", planks_tile), ("plank_star", plank_star), ("mirror", mirror), ("sun", sun_window),
         ("crate", crate_tile), ("owlet", owlet_tile), ("owlet_awake", owlet_awake),
         ("pond_grass", pond_grass), ("water", pond_water_tile), ("reeds", reeds_tile), ("stump", stump_tile),
         ("goal", goal_tile), ("arrow", arrow), ("slot", slot),
         ("arrow_up", lambda b: arrow(b, 90)), ("arrow_left", lambda b: arrow(b, 180)), ("arrow_down", lambda b: arrow(b, 270))]
