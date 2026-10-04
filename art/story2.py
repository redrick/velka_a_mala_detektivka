"""Game art for story 2 "Tajemství starého klíče": the four rooms (bedroom, breakfast kitchen is
reused, under the attic window, the attic), the props, and the flashback slides.
Rooms are drawn on a 960 x 540 pt Box like the others; colour comes from palette.py."""
import math, random
import lib
from lib import ell, bez, rrect
import palette as P
from style3 import *
from chars3 import star
from scenes3 import (BG, s_, sh_, sky, cloud, hills, ground, tufts, tree, house, planks, floor, fence,
                     shelf, crate, boot)
from attic import (bedroom, bed_side, bunting, shelf_toys, kids_drawing, attic, star_window, star_spot,
                   chest, owl, owlet, feather, pellet, ladder, tin, map_half, gable_end, owl_box, young,
                   herbs, cobweb, sled, suitcase)
from pond import full_map, water, far_trees

# Floor boards of the attic, used by the room art and by the game (plank hotspots).
# Boards run across the floor band; the star of sunlight lands on board 0.
ATTIC_FLOOR_Y = 0.22
BOARD_X0 = 0.24          # left edge of board 0 (fraction of the room width)
BOARD_W = 0.08           # width of one board
BOARDS = 9


# ------------------------------------------------------------------ rooms
def room_bedroom(b):
    bedroom(b, night=False)
    fill([(0, 0), (b.w, 0), (b.w, b.Y(0.2)), (0, b.Y(0.2))], P.FLOOR)
    for x in range(0, int(b.w), 48): s_([(x, 0), (x + 20, b.Y(0.2))], BG*0.5)
    s_([(0, b.Y(0.2)), (b.w, b.Y(0.2))], BG)
    # ceiling beams (the attic is above)
    for fx in (0.0, 0.33, 0.66):
        tube([(b.X(fx) - 4, b.Y(0.95)), (b.X(fx + 0.34) + 4, b.Y(0.95))], 12, 12, P.ATTIC_BEAM, lw=BG, sh=0)
    fill([(0, b.Y(0.95) + 6), (b.w, b.Y(0.95) + 6), (b.w, b.h), (0, b.h)], P.ATTIC_WALL)
    bunting(b, 0.86)
    # window
    wx0, wy0, wx1, wy1 = b.X(0.05), b.Y(0.46), b.X(0.2), b.Y(0.78)
    fill([(wx0, wy0), (wx1, wy0), (wx1, wy1), (wx0, wy1)], P.SKY)
    stroke([(wx0, wy0), (wx1, wy0), (wx1, wy1), (wx0, wy1)], BG*1.4, closed=True)
    stroke([((wx0 + wx1)/2, wy0), ((wx0 + wx1)/2, wy1)], BG*1.6)
    stroke([(wx0, (wy0 + wy1)/2), (wx1, (wy0 + wy1)/2)], BG*1.2)
    shelf_toys(b.X(0.26), b.Y(0.66), 90)
    if not osobni.on("wallart"): kids_drawing(b.X(0.62), b.Y(0.62), 44, 34)
    # two beds along the back wall
    for x0, x1 in ((b.X(0.25), b.X(0.5)), (b.X(0.53), b.X(0.78))):
        bed_side(x0, x1, b.Y(0.36))
        form([(x0 + 2, b.Y(0.36) - 12), (x1 - 40, b.Y(0.36) - 12), (x1 - 40, b.Y(0.36) + 8), (x0 + 2, b.Y(0.36) + 8)],
             P.BLANKET, w=BG, sh=0.08)
    # door on the right
    d = [(b.X(0.86), b.Y(0.2)), (b.X(0.96), b.Y(0.2)), (b.X(0.96), b.Y(0.7)), (b.X(0.86), b.Y(0.7))]
    form(d, P.DOOR, w=BG*1.3, sdx=2, sdy=0)
    dot(b.X(0.875), b.Y(0.44), 2.2, P.BRASS)
    wall_art(b, "pokojicek")


def room_gable(b):
    sky(b, P.SKY); cloud(b.X(0.2), b.Y(0.86), 1.0); cloud(b.X(0.5), b.Y(0.92), 0.7)
    hills(b, b.Y(0.3), 24, P.HILLS, 8)
    ground(b, b.Y(0.3), P.GRASS)
    tree(b.X(0.09), b.Y(0.28), 2.0, seed=12)
    gable_end(b.X(0.66), b.Y(0.3), 190, 200, 360, seed=7, low_window=True, drainpipe=True, climber=True)
    fence(b.X(0.22), b.X(0.4), b.Y(0.28), 36)
    tufts(b, b.Y(0.03), b.Y(0.26), 12, 21)


def room_attic(b):
    attic(b, floor_y=ATTIC_FLOOR_Y, window=(0.2, 0.62), seed=9, beam=0.78)
    fy = b.Y(ATTIC_FLOOR_Y)
    # the floor boards, clear so they can be counted
    fill([(0, 0), (b.w, 0), (b.w, fy), (0, fy)], P.ATTIC_FLOOR)
    for i in range(BOARDS + 4):
        x = b.X(BOARD_X0 + (i - 2)*BOARD_W)
        stroke([(x, 0), (x + 6, fy)], BG*1.3)
    s_([(0, fy), (b.w, fy)], BG*1.2)
    # junk
    sled(b.X(0.08), b.Y(0.16), 1.0)
    suitcase(b.X(0.52), b.Y(0.2), 64, 40)
    crate(b.X(0.62), b.Y(0.2), 50, 56)
    cobweb(b.w, b.h, 60, flip=True); cobweb(0, b.h, 50)
    # the low roof over the far right boards
    slope = [(b.X(0.8), b.h + 2), (b.w + 2, b.Y(0.3)), (b.w + 2, b.h + 2)]
    form(slope, P.ATTIC_ROOF, w=BG, sh=0)
    tube([(b.X(0.8), b.h + 4), (b.w + 4, b.Y(0.3))], 14, 14, P.ATTIC_BEAM, lw=BG, sh=0)
    fill([(b.X(0.86), 0), (b.w, 0), (b.w, b.Y(0.3)), (b.X(0.9), b.Y(0.26))], 0.0, 0.25)


# ------------------------------------------------------------------ props (canvas w, h, draw)
def owls_on_beam(b):
    owl(b.w - 40, 8, 2.3, flip=True, mood="wide")
    bx = b.w*0.38
    for dx, m in ((-46, "sleepy"), (0, "hiss"), (46, "open")):
        owlet(bx + dx, 12, 1.8, mood=m)
    shape([(bx - 72, 8), (bx + 72, 8), (bx + 66, 32), (bx - 66, 32)], 0.7, BG)
    for k_ in range(-66, 70, 10): s_([(bx + k_, 8), (bx + k_*0.95, 32)], BG*0.5)


def two_pellets(b):
    pellet(b.w*0.35, b.h*0.5, 2.2, rot=10); pellet(b.w*0.7, b.h*0.45, 1.9, rot=-20)


def star_of_light(b):
    star_spot(b.w/2, b.h/2, 50, 0.85)


def plank_glow(b):
    fill([(4, 4), (b.w - 4, 4), (b.w - 4, b.h - 4), (4, b.h - 4)], P.SUNBEAM, 0.55)


def sunbeam_wedge(b):
    fill([(0, b.h), (b.w*0.16, b.h), (b.w, 0), (b.w*0.7, 0)], P.SUNBEAM, 0.35)


PROPS = [
    ("chest_closed", 160, 110, lambda b: chest(b.w/2, 6, 1.0)),
    ("chest_open", 160, 120, lambda b: chest(b.w/2, 6, 1.0, open_=True)),
    ("owls_beam", 320, 110, owls_on_beam),
    ("feather", 40, 70, lambda b: feather(b.w/2, 10, 2.0)),
    ("pellets", 90, 40, two_pellets),
    ("ladder_tall", 60, 330, lambda b: ladder(b.w/2, 4, b.h - 4, 44)),
    ("tin_star", 80, 50, lambda b: tin(b.w/2, 6, 2.0)),
    ("star_light", 160, 50, star_of_light),
    ("plank_glow", 80, 120, plank_glow),
    ("sunbeam", 520, 300, sunbeam_wedge),
    ("owl_box", 90, 110, lambda b: owl_box(b.w/2, 30, 1.4)),
]

ITEMS = [
    ("map_half", 70, 90, lambda b: map_half(6, 6, 0.95, "L")),
    ("map_full", 130, 90, lambda b: full_map(5, 5, 0.5)),
]


# ------------------------------------------------------------------ flashback slides
def _photo(b):
    b2 = 8
    ring = [(0, 0), (b.w, 0), (b.w, b.h), (0, b.h), (0, 0), (b2, b2), (b2, b.h - b2), (b.w - b2, b.h - b2), (b.w - b2, b2), (b2, b2)]
    fill(ring, P.PHOTO_FRAME)
    for (cx, cy, dx, dy) in ((0, 0, 1, 1), (b.w, 0, -1, 1), (0, b.h, 1, -1), (b.w, b.h, -1, -1)):
        shape([(cx, cy), (cx + dx*40, cy), (cx, cy + dy*40)], P.CHEST_BAND, 0.8)


def slide_club(b):
    sky(b, P.SKY); cloud(b.X(0.3), b.Y(0.85), 1.1)
    hills(b, b.Y(0.3), 20, P.HILLS, 3); ground(b, b.Y(0.28), P.GRASS)
    house(b.X(0.84), b.Y(0.26), 1.9); tree(b.X(0.1), b.Y(0.26), 1.8, seed=4)
    young(b.X(0.33), b.Y(0.05), 2.8, "deda", right="wave", mood="grin")
    young(b.X(0.5), b.Y(0.05), 2.7, "franta", mood="happy", look=(-1, 0))
    young(b.X(0.66), b.Y(0.05), 2.65, "verka", right="up", mood="happy", look=(-1, 0))
    _photo(b)


def slide_attic(b):
    attic(b, floor_y=0.16, window=(0.62, 0.62), seed=12)
    chest(b.X(0.8), b.Y(0.06), 1.2, open_=True)
    owl(b.X(0.9), b.Y(0.78) + 8, 1.9, mood="open", flip=True)
    young(b.X(0.18), b.Y(0.04), 2.6, "franta", mood="happy", look=(1, 0.5))
    young(b.X(0.36), b.Y(0.04), 2.6, "verka", mood="grin", right="up", look=(1, 0.5))
    young(b.X(0.54), b.Y(0.04), 2.7, "deda", right="hush", mood="whisper", look=(1, 0.5))
    _photo(b)


def slide_pond(b):
    sky(b, P.SKY); cloud(b.X(0.7), b.Y(0.86), 1.0)
    ground(b, b.Y(0.44), P.GRASS)
    far_trees(b, b.Y(0.52), 3)
    water(ell(b.X(0.7), b.Y(0.4), b.w*0.3, 44, 40), 5)
    tree(b.X(0.12), b.Y(0.4), 1.9, seed=64)
    fill(ell(b.X(0.42), b.Y(0.1), 60, 14, 24), P.MUD)
    tin(b.X(0.42), b.Y(0.08), 2.2)
    young(b.X(0.24), b.Y(0.04), 2.6, "deda", right="point", mood="happy", look=(1, -1))
    young(b.X(0.6), b.Y(0.04), 2.5, "verka", flip=True, mood="grin", look=(1, -1))
    young(b.X(0.76), b.Y(0.04), 2.5, "franta", flip=True, right="hold", mood="happy", look=(1, -1),
          item=lambda x, y: stroke([(x, y), (x + 2, y - 30)], 2.4, g=0.4))
    _photo(b)


def slide_map(b):
    fill([(0, 0), (b.w, 0), (b.w, b.h), (0, b.h)], P.PHOTO_BG)
    map_half(b.X(0.5) - 170, b.Y(0.3), 2.4, "L", rot=8)
    map_half(b.X(0.5) - 110, b.Y(0.3), 2.4, "R", rot=-8)
    young(b.X(0.14), b.Y(0.04), 2.5, "deda", right="point", mood="determined", look=(1, 0.5))
    young(b.X(0.86), b.Y(0.04), 2.4, "verka", right="point", flip=True, mood="determined", look=(1, 0.5))
    _photo(b)


def slide_goodbye(b):
    sky(b, P.SKY); hills(b, b.Y(0.3), 20, P.HILLS, 6); ground(b, b.Y(0.28), P.GRASS)
    house(b.X(0.86), b.Y(0.26), 1.9)
    fence(b.X(0.3), b.X(0.66), b.Y(0.24), 50)
    young(b.X(0.52), b.Y(0.05), 2.6, "verka", right="wave", mood="happy", look=(-1, 0), flip=True)
    suitcase(b.X(0.58), b.Y(0.05), 80, 52)
    young(b.X(0.14), b.Y(0.05), 2.6, "deda", right="wave", mood="sad", look=(1, 0))
    young(b.X(0.3), b.Y(0.05), 2.55, "franta", right="wave", mood="sad", look=(1, 0))
    _photo(b)


def slide_key(b):
    planks(b, P.PLANKS, 30, 3)
    floor(b, b.Y(0.16), P.FLOOR)
    shelf(b.X(0.5), b.X(1.02), b.Y(0.44))
    boot(b.X(0.76), b.Y(0.445), 2.4)
    from chars3 import key
    young(b.X(0.3), b.Y(0.03), 2.6, "deda", right="up", mood="think", look=(1, 0.5),
          item=lambda x, y: key(x + 4, y + 6, 0.8, rot=70, tag=True))
    _photo(b)


SLIDES = [("fb_club", slide_club), ("fb_attic", slide_attic), ("fb_pond", slide_pond),
          ("fb_map", slide_map), ("fb_goodbye", slide_goodbye), ("fb_key", slide_key)]
ROOMS = [("bedroom", room_bedroom), ("gable", room_gable), ("attic", room_attic)]
