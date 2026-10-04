"""Export comic-style art as transparent PNGs for Godot.

Usage:  python export_assets.py            -> writes colour PNGs into ../game/assets/
        python export_assets.py --bw       -> greyscale, as printed in the comic
Each asset is drawn on its own PDF page (transparent), then rasterised with PyMuPDF.
Add new entries to CHARACTERS / PROPS / ROOMS below.
"""
import os, sys, math, zlib
from reportlab.pdfgen import canvas
import pymupdf
import lib
import osobni
import style3
import palette as P
lib.MODE = "bw" if "--bw" in sys.argv else "color"
from style3 import *
from style3 import C
from chars3 import *
from scenes3 import *
from props_extra import *
from interior import room_kitchen
from outdoor import room_zahumenek, fence_with_gap, nail
import menu
import minigames
import story2
import story3

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "..", "game", "assets")
SCALE = 2.0   # raster scale: 1 pt -> 2 px

class Box:
    """minimal stand-in for a comic panel, used by scene helpers"""
    def __init__(self, w, h): self.x, self.y, self.w, self.h = 0, 0, w, h
    def X(self, f): return self.w*f
    def Y(self, f): return self.h*f

def render(name, w, h, draw, folder):
    os.makedirs(os.path.join(OUT, folder), exist_ok=True)
    tmp = os.path.join(OUT, "_tmp.pdf")
    cv = canvas.Canvas(tmp, pagesize=(w, h)); lib.set_canvas(cv)
    style3._R.seed(zlib.crc32(name.encode()))
    draw(Box(w, h)); cv.showPage(); cv.save()
    doc = pymupdf.open(tmp)
    pix = doc[0].get_pixmap(matrix=pymupdf.Matrix(SCALE, SCALE), alpha=True)
    path = os.path.join(OUT, folder, name + ".png"); pix.save(path); doc.close(); os.remove(tmp)
    if folder in ("rooms", "slides"): osobni.paper(path)  # scanned paper grain (personal style)
    print("wrote", os.path.relpath(path, HERE))

# ------------------------------------------------------------------ characters
# (name, canvas w, h, draw fn). Characters stand with feet at bottom-centre; 1 unit = Alica height/100.
S = 2.2
CHARACTERS = []
for mood in ("happy", "grin", "surprised", "think", "worried", "whisper"):
    CHARACTERS.append((f"alica_{mood}", 120, 240, lambda b, m=mood: alica(b.w/2, 8, S, mood=m, shadow=False)))
    CHARACTERS.append((f"hanka_{mood}", 110, 200, lambda b, m=mood: hanka(b.w/2, 8, S, mood=m, shadow=False)))
CHARACTERS += [
    ("alica_lens", 150, 240, lambda b: alica(b.w/2-10, 8, S, right="lens", lens=True, mood="determined", shadow=False)),
    ("alica_point", 170, 240, lambda b: alica(b.w/2-25, 8, S, right="point", mood="surprised", shadow=False)),
    ("alica_walk", 120, 240, lambda b: alica(b.w/2, 8, S, legs="walk", mood="happy", shadow=False)),
    ("hanka_point", 150, 200, lambda b: hanka(b.w/2-20, 8, S, right="point", mood="wow", shadow=False)),
    ("hanka_torch", 150, 200, lambda b: hanka(b.w/2-20, 8, S, right="lens", torch=True, mood="wow", shadow=False)),
    ("hanka_walk", 110, 200, lambda b: hanka(b.w/2, 8, S, legs="walk", mood="happy", shadow=False)),
    ("joey_stand", 180, 140, lambda b: joey(b.w/2-5, 8, S, mood="happy", shadow=False)),
    ("joey_sniff", 180, 120, lambda b: joey(b.w/2-5, 8, S, pose="sniff", shadow=False)),
    ("joey_sleepy", 180, 140, lambda b: joey(b.w/2-5, 8, S, mood="sleepy", shadow=False)),
    ("babicka", 130, 270, lambda b: babicka(b.w/2, 8, S, mood="happy", shadow=False)),
    ("deda", 140, 300, lambda b: deda(b.w/2, 8, S, mood="happy", shadow=False)),
    ("tonda", 130, 250, lambda b: tonda(b.w/2, 8, S, mood="grin", shadow=False)),
    ("babicka_happy", 130, 270, lambda b: babicka(b.w/2, 8, S, mood="happy", shadow=False)),
    ("babicka_talk", 130, 270, lambda b: babicka(b.w/2, 8, S, mood="talk", shadow=False)),
    ("babicka_walk", 130, 270, lambda b: babicka(b.w/2, 8, S, mood="happy", legs="walk", shadow=False)),
    ("deda_happy", 140, 300, lambda b: deda(b.w/2, 8, S, mood="happy", shadow=False)),
    ("deda_talk", 140, 300, lambda b: deda(b.w/2, 8, S, mood="talk", shadow=False)),
    ("deda_walk", 140, 300, lambda b: deda(b.w/2, 8, S, mood="happy", legs="walk", shadow=False)),
    ("tonda_happy", 130, 250, lambda b: tonda(b.w/2, 8, S, mood="grin", shadow=False)),
    ("tonda_talk", 130, 250, lambda b: tonda(b.w/2, 8, S, mood="talk", shadow=False)),
    ("tonda_walk", 130, 250, lambda b: tonda(b.w/2, 8, S, mood="grin", legs="walk", shadow=False)),
    ("alica_talk", 120, 240, lambda b: alica(b.w/2, 8, S, mood="talk", shadow=False)),
    ("hanka_talk", 110, 200, lambda b: hanka(b.w/2, 8, S, mood="talk", shadow=False)),
    ("joey_bark", 180, 140, lambda b: joey(b.w/2-5, 8, S, mood="bark", shadow=False)),
    ("cat_micka", 110, 110, lambda b: cat(b.w/2-8, 8, S, mood="sleepy")),
    ("magpie", 110, 80, lambda b: magpie(b.w/2+10, 12, S)),
    ("dormouse", 150, 80, lambda b: dormouse(b.w/2+25, 8, S)),
    ("hanka_sleepy", 110, 200, lambda b: hanka(b.w/2, 8, S, mood="sleepy", shadow=False)),
]

# ------------------------------------------------------------------ inventory / props
PROPS = [
    ("magnifier", 60, 60, lambda b: magnifier(b.w/2, b.h/2+8, ang=-30, r=14)),
    ("key", 110, 80, lambda b: key(b.w/2-10, b.h/2-10, 2.0)),
    ("sock_red", 60, 80, lambda b: sock_item(b.w/2-8, b.h-8, 2.4, g=P.SOCK_RED)),
    ("flour_bag", 70, 80, lambda b: flour_bag(b.w/2, 6, 2.2)),
    ("wool", 50, 50, lambda b: wool(b.w/2, b.h/2, 20, P.WOOL)),
    ("glove", 50, 80, lambda b: glove(b.w/2, 6, 2.2, P.GLOVE)),
    ("old_boot", 120, 140, lambda b: boot(b.w/2-15, 6, 2.5)),
    ("birdhouse", 120, 120, lambda b: birdhouse(b.w/2, 8, 2.4)),
    ("monkey_toy", 80, 90, lambda b: monkey(b.w/2, 6, 2.6)),
    ("notebook", 70, 55, lambda b: notebook(b.w/2, b.h/2, 3.6)),
    ("footprints", 110, 40, lambda b: footprints(12, 14, 6, 14, 6, 1.3, P.FOOTPRINT)),
    ("dog_bed", 130, 45, lambda b: dog_bed(b.w/2, 4, 2.2)),
    ("old_sock", 60, 80, lambda b: old_sock(b.w/2-8, b.h-8, 2.4)),
    ("mug", 40, 40, lambda b: mug(b.w/2-3, 4, 2.4)),
    ("flour_patch", 180, 50, lambda b: flour_patch(b.w/2, b.h/2, 150, 36)),
    ("floury_prints", 200, 50, lambda b: footprints(14, 16, 8, 23, 10, 1.4, P.FLOUR_PRINT)),
    ("thread", 150, 40, lambda b: red_thread(bez((8, 20), (50, 36), (90, 4), (142, 22)), 1.6)),
    ("thread_icon", 60, 60, lambda b: red_thread([(30+math.cos(a/6)*(4+a*0.45), 30+math.sin(a/6)*(4+a*0.45)) for a in range(0, 48)], 1.8)),
    ("dormouse_silhouette", 80, 60, lambda b: silhouette_dormouse(b.w/2+10, 4, 2.0)),
    ("fence_gap", 650, 60, fence_with_gap),
    ("stone_big", 70, 34, lambda b: stone(35, 15, 30, 13)),
    ("stone_small", 46, 26, lambda b: stone(23, 11, 19, 9)),
    ("nail", 14, 28, nail),
]

# ------------------------------------------------------------------ rooms (960 x 540, 16:9)
def room_garden(b):
    sky(b, P.SKY); cloud(b.X(0.2), b.Y(0.82), 1.2); cloud(b.X(0.75), b.Y(0.78), 0.9)
    hills(b, b.Y(0.45), 30, P.HILLS, 2)
    house(b.X(0.8), b.Y(0.38), 1.8)
    tree(b.X(0.1), b.Y(0.33), 2.2, seed=5)
    ground(b, b.Y(0.4), P.GRASS)
    clothesline(b.X(0.35), b.X(0.6), b.Y(0.38), 110, ("shirt", "sock", "towel"))
    fence(b.X(0.9), b.w+5, b.Y(0.35), 40)
    tufts(b, b.Y(0.02), b.Y(0.36), 14, 4)

def room_shed_inside(b):
    planks(b, P.PLANKS, 30, 12); floor(b, b.Y(0.2), P.FLOOR)
    sunbeam(b.X(0.05), b.X(0.2), b.h, b.X(0.42), b.X(0.8), 0, 0.3)
    shelf(b.X(0.55), b.X(0.95), b.Y(0.55)); rake(b.X(0.1), b.Y(0.3), 1.4)
    saw(b.X(0.3), b.Y(0.78), 1.3); crate(b.X(0.6), b.Y(0.08), 90, 70); crate(b.X(0.8), b.Y(0.08), 70, 100, P.CRATE_DARK)
    watering_can(b.X(0.45), b.Y(0.1), 1.6)
    style3.wall_art(b, "kulna")

def room_pond_trail(b):
    sky(b, P.SKY); hills(b, b.Y(0.6), 20, P.HILLS, 5); ground(b, b.Y(0.58), P.GRASS_TRAIL)
    shed(b.X(0.85), b.Y(0.56), 1.2)
    tree(b.X(0.2), b.Y(0.55), 1.4, seed=7)

MENU = [
    ("bg", 960, 540, menu.menu_bg),
    ("series_vamd", 300, 400, menu.series_cover),
    ("ep_vamd_01", 180, 240, menu.episode_cover),
    ("ep_vamd_02", 180, 240, menu.episode_cover_2),
    ("ep_vamd_03", 180, 240, menu.episode_cover_3),
    ("ep_locked", 180, 240, menu.episode_locked),
    ("panel", 120, 90, menu.panel),
    ("button", 120, 44, menu.button(P.BUTTON)),
    ("button_hover", 120, 44, menu.button(P.BUTTON_HOVER)),
    ("button_off", 120, 44, menu.button(P.BUTTON_OFF)),
    ("home", 44, 44, menu.home_icon),
]

ROOMS = [("garden", 960, 540, room_garden), ("kitchen", 960, 540, room_kitchen), ("zahumenek", 960, 540, room_zahumenek), ("shed_inside", 960, 540, room_shed_inside), ("trail", 960, 540, room_pond_trail)]

MINIGAMES = [(name, 64, 64, fn) for name, fn in minigames.TILES]

if __name__ == "__main__":
    # --only <folder> renders just one group, e.g. --only minigames
    only = sys.argv[sys.argv.index("--only") + 1] if "--only" in sys.argv else None
    for folder, items in (("characters", CHARACTERS), ("props", PROPS), ("rooms", ROOMS), ("menu", MENU), ("minigames", MINIGAMES)):
        if only in (None, folder):
            for name, w, h, fn in items: render(name, w, h, fn, folder)
    if only in (None, "story2"):
        for name, fn in story2.ROOMS: render(name, 960, 540, fn, "rooms")
        for name, w, h, fn in story2.PROPS + story2.ITEMS: render(name, w, h, fn, "props")
        for name, fn in story2.SLIDES: render(name, 960, 540, fn, "slides")
    if only in (None, "story3"):
        for name, fn in story3.ROOMS: render(name, 960, 540, fn, "rooms")
        for name, w, h, fn in story3.CHARACTERS: render(name, w, h, fn, "characters")
        for name, w, h, fn in story3.PROPS + story3.ITEMS: render(name, w, h, fn, "props")
        for name, fn in story3.MG: render(name, 64, 64, fn, "minigames")
