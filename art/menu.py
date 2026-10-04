"""Menu art: background, series and story covers, hand-inked UI skins."""
import math
from lib import C, ell, bez, rrect
import palette as P
from style3 import *
from chars3 import star, torch, sock_item, footprints
from scenes3 import BG, sky, cloud, hills, ground, tufts, tree, house, clothesline, fence
from letter import sfx, sfx_width, series_title, hand_text


def title_text(cx, y, txt, size, fill_g=P.TITLE_FILL):
    sfx(cx - sfx_width(txt, size, 7)/2, y, txt, size, 0, fill_g, True, seed=7)


def inked_box(x, y, w, h, fill_g, r=10, lw=2.2, shadow=True):
    pts = rrect(x, y, w, h, r)
    if shadow:
        fill([(px+3, py-3) for px, py in pts], 0.0, 0.22)
    fill(pts, fill_g)
    stroke(pts, lw, closed=True)


def menu_bg(b):
    sky(b, P.SKY)
    cloud(b.X(0.45), b.Y(0.86), 1.3); cloud(b.X(0.78), b.Y(0.9), 1.0); cloud(b.X(0.15), b.Y(0.92), 0.9)
    hills(b, b.Y(0.34), 30, P.HILLS, 3)
    house(b.X(0.9), b.Y(0.3), 1.2)
    ground(b, b.Y(0.3), P.GRASS)
    tufts(b, b.Y(0.02), b.Y(0.26), 12, 6)
    footprints(b.X(0.28), b.Y(0.08), 4, 16, 5, 1.1, P.FOOTPRINT)
    joey(b.X(0.2), b.Y(0.04), 1.9, pose="sniff", mood="happy")
    hanka(b.X(0.07), b.Y(0.03), 2.9, mood="grin")
    alica(b.X(0.15), b.Y(0.03), 3.1, right="lens", lens=True, mood="determined", look=(1, -0.3))


def series_cover(b):
    x, y, w, h = 6, 6, b.w-12, b.h-12
    inked_box(x, y, w, h, P.PAPER, r=6, shadow=False)
    scene = rect_pts = [(x+10, y+10), (x+w-10, y+10), (x+w-10, y+h*0.7), (x+10, y+h*0.7)]
    C.saveState(); C.clipPath(poly(scene), stroke=0, fill=0)
    class _S: pass
    s = _S(); s.x, s.y, s.w, s.h = x+10, y+10, w-20, h*0.7-10
    sky(s, P.SKY); cloud(s.x+s.w*0.75, s.y+s.h*0.85, 0.9)
    hills(s, s.y+s.h*0.42, 20, P.HILLS, 2)
    house(s.x+s.w*0.84, s.y+s.h*0.38, 0.9)
    ground(s, s.y+s.h*0.4, P.GRASS)
    clothesline(s.x+s.w*0.3, s.x+s.w*0.66, s.y+s.h*0.39, 70, ("shirt", "sock", "towel"))
    joey(s.x+s.w*0.82, s.y+6, 1.1, pose="sniff", mood="happy", flip=True)
    hanka(s.x+s.w*0.58, s.y+4, 1.9, mood="grin", flip=True)
    alica(s.x+s.w*0.3, s.y+4, 2.05, right="lens", lens=True, mood="determined", look=(1, -0.3))
    C.restoreState()
    stroke(scene, 2.0, closed=True)
    series_title(b.w/2, y+h*0.86, y+h*0.76, 26, 38, P.TITLE_FILL)


def episode_cover(b):
    x, y, w, h = 5, 5, b.w-10, b.h-10
    inked_box(x, y, w, h, P.PAPER, r=6, shadow=False)
    scene = [(x+8, y+8), (x+w-8, y+8), (x+w-8, y+h-8), (x+8, y+h-8)]
    C.saveState(); C.clipPath(poly(scene), stroke=0, fill=0)
    class _S: pass
    s = _S(); s.x, s.y, s.w, s.h = x+8, y+8, w-16, h-16
    sky(s, P.SKY); cloud(s.x+s.w*0.3, s.y+s.h*0.86, 0.8)
    hills(s, s.y+s.h*0.4, 16, P.HILLS, 5)
    ground(s, s.y+s.h*0.38, P.GRASS)
    clothesline(s.x+s.w*0.18, s.x+s.w*0.82, s.y+s.h*0.36, 85, ("shirt", "empty", "sock"))
    footprints(s.x+s.w*0.3, s.y+s.h*0.12, 4, 14, 5, 1.0, P.FOOTPRINT)
    sock_item(s.x+s.w*0.5, s.y+s.h*0.66, 2.0, g=P.SOCK_RED, rot=-20)
    for (sx, sy) in ((0.25, 0.8), (0.72, 0.62), (0.4, 0.5)):
        star(s.x+s.w*sx, s.y+s.h*sy, 4, P.TITLE_FILL)
    C.restoreState()
    stroke(scene, 1.8, closed=True)
    _number_badge(x+w-26, y+h-26, "1")


def episode_cover_2(b):
    """story 2: the attic, the star window, an owl on the beam and the star key"""
    from attic import attic as attic_room, owl, owlet, chest
    from chars3 import key
    x, y, w, h = 5, 5, b.w-10, b.h-10
    inked_box(x, y, w, h, P.PAPER, r=6, shadow=False)
    scene = [(x+8, y+8), (x+w-8, y+8), (x+w-8, y+h-8), (x+8, y+h-8)]
    C.saveState(); C.clipPath(poly(scene), stroke=0, fill=0)
    class _S: pass
    s = _S(); s.x, s.y, s.w, s.h = x+8, y+8, w-16, h-16
    s.X = lambda f: s.x + s.w*f; s.Y = lambda f: s.y + s.h*f
    attic_room(s, floor_y=0.2, window=(0.3, 0.55), seed=5, beam=0.72, herbs_=False)
    owl(s.X(0.62), s.Y(0.72) + 4, 1.2, flip=True, mood="wide")
    owlet(s.X(0.4), s.Y(0.72) + 5, 0.8, mood="sleepy")
    chest(s.X(0.5), s.Y(0.04), 0.5)
    key(s.X(0.3), s.Y(0.3), 1.3, rot=20, tag=True)
    C.restoreState()
    stroke(scene, 1.8, closed=True)
    _number_badge(x+w-26, y+h-26, "2")


def episode_cover_3(b):
    """story 3: the old pond, the willow stump, the map and the star stone"""
    from pond import pond_bg, willow, stump, star_stone, full_map, mill
    x, y, w, h = 5, 5, b.w-10, b.h-10
    inked_box(x, y, w, h, P.PAPER, r=6, shadow=False)
    scene = [(x+8, y+8), (x+w-8, y+8), (x+w-8, y+h-8), (x+8, y+h-8)]
    C.saveState(); C.clipPath(poly(scene), stroke=0, fill=0)
    class _S: pass
    s = _S(); s.x, s.y, s.w, s.h = x+8, y+8, w-16, h-16
    s.X = lambda f: s.x + s.w*f; s.Y = lambda f: s.y + s.h*f
    fy = pond_bg(s, 0.35, 0.62, seed=3)
    mill(s.X(0.78), fy + 2, 0.35)
    willow(s.X(0.2), s.Y(0.33), 0.7, seed=4)
    stump(s.X(0.62), s.Y(0.25), 0.55)
    star_stone(s.X(0.45), s.Y(0.1), 1.0)
    full_map(s.X(0.08), s.Y(0.66), 0.32, rot=-6)
    C.restoreState()
    stroke(scene, 1.8, closed=True)
    _number_badge(x+w-26, y+h-26, "3")


def episode_locked(b):
    x, y, w, h = 5, 5, b.w-10, b.h-10
    inked_box(x, y, w, h, P.PAPER, r=6, shadow=False)
    scene = [(x+8, y+8), (x+w-8, y+8), (x+w-8, y+h-8), (x+8, y+h-8)]
    fill(scene, P.LOCKED_SKY)
    for (sx, sy, r_) in ((0.2, 0.8, 5), (0.78, 0.72, 4), (0.3, 0.22, 3.5), (0.8, 0.3, 5)):
        star(x+w*sx, y+h*sy, r_, P.TITLE_FILL)
    stroke(scene, 1.8, closed=True)
    title_text(b.w/2, y+h*0.4, "?", 90, P.BUTTON)
    magnifier(x+w*0.7, y+h*0.24, ang=-30, r=12)


def _number_badge(cx, cy, txt):
    shape(ell(cx, cy, 17, 17, 30), P.TITLE_FILL, 1.8)
    title_text(cx, cy-9, txt, 24, 1.0)


def panel(b):
    inked_box(4, 6, b.w-10, b.h-10, P.PAPER, r=14, lw=2.4)


def button(fill_g):
    def draw(b):
        inked_box(4, 5, b.w-9, b.h-9, fill_g, r=12, lw=2.4)
    return draw


def home_icon(b):
    shape(ell(b.w/2, b.h/2, b.w/2-3, b.h/2-3, 36), P.BUTTON, 2.2)
    cx, cy = b.w/2, b.h/2
    shape([(cx-11, cy-10), (cx+11, cy-10), (cx+11, cy+3), (cx-11, cy+3)], P.WALL, 1.6)
    shape([(cx-15, cy+2), (cx, cy+14), (cx+15, cy+2)], P.ROOF, 1.6)
    shape([(cx-3, cy-10), (cx+3, cy-10), (cx+3, cy-2), (cx-3, cy-2)], P.DOOR, 1.2)
