"""README art: round logo badge and a wide banner, drawn with the comic library.

Usage:  .venv/bin/python readme_art.py   -> ../docs/img/{logo,banner}.png
"""
import os
import export_assets as E
import palette as P
from lib import ell
from style3 import *
from chars3 import star, sock_item, footprints
from scenes3 import sky, cloud, hills, ground, tufts, house, clothesline
from menu import title_text, inked_box

E.OUT = os.path.join(E.HERE, "..", "docs")


def logo(b):
    cx, cy, r = b.w/2, b.h/2 + 10, b.w/2 - 16
    fill([(px+5, py-5) for px, py in ell(cx, cy, r, r, 60)], 0.0, 0.22)
    circle = ell(cx, cy, r, r, 60)
    C.saveState(); C.clipPath(poly(circle), stroke=0, fill=0)
    class _S: pass
    s = _S(); s.x, s.y, s.w, s.h = cx-r, cy-r, 2*r, 2*r
    sky(s, P.SKY); cloud(s.x+s.w*0.3, s.y+s.h*0.82, 0.9)
    hills(s, s.y+s.h*0.4, 18, P.HILLS, 4)
    ground(s, s.y+s.h*0.38, P.GRASS)
    footprints(s.x+s.w*0.12, s.y+s.h*0.12, 4, 12, 4, 0.9, P.FOOTPRINT)
    for (sx, sy) in ((0.72, 0.84), (0.86, 0.66), (0.18, 0.62)):
        star(s.x+s.w*sx, s.y+s.h*sy, 5, P.TITLE_FILL)
    sock_item(s.x+s.w*0.84, s.y+s.h*0.62, 1.6, g=P.SOCK_RED, rot=-25)
    joey(s.x+s.w*0.84, s.y+s.h*0.06, 1.2, pose="sniff", mood="happy", flip=True)
    hanka(s.x+s.w*0.6, s.y+s.h*0.05, 1.9, mood="grin", flip=True)
    alica(s.x+s.w*0.22, s.y+s.h*0.05, 2.1, right="lens", lens=True, mood="determined", look=(1, -0.3))
    C.restoreState()
    stroke(circle, 3.2, closed=True)
    stroke(ell(cx, cy, r+7, r+7, 60), 1.6, closed=True)
    inked_box(cx-r*0.95, cy-r-34, r*1.9, 70, P.BUTTON, r=14, lw=2.6)
    title_text(cx, cy-r+1, "VELKÁ A MALÁ", 24)
    title_text(cx, cy-r-27, "DETEKTIVKA", 36)


def banner(b):
    sky(b, P.SKY)
    cloud(b.X(0.42), b.Y(0.86), 1.2); cloud(b.X(0.7), b.Y(0.9), 0.9); cloud(b.X(0.1), b.Y(0.9), 0.8)
    hills(b, b.Y(0.36), 30, P.HILLS, 3)
    house(b.X(0.93), b.Y(0.3), 1.0)
    ground(b, b.Y(0.3), P.GRASS)
    clothesline(b.X(0.76), b.X(0.86), b.Y(0.3), 80, ("empty", "sock"))
    tufts(b, b.Y(0.02), b.Y(0.26), 14, 6)
    footprints(b.X(0.3), b.Y(0.08), 5, 18, 5, 1.1, P.FOOTPRINT)
    joey(b.X(0.26), b.Y(0.04), 1.6, pose="sniff", mood="happy")
    hanka(b.X(0.07), b.Y(0.03), 2.4, mood="grin")
    alica(b.X(0.15), b.Y(0.03), 2.6, right="lens", lens=True, mood="determined", look=(1, -0.3))
    for (sx, sy) in ((0.36, 0.78), (0.9, 0.7), (0.58, 0.9)):
        star(b.X(sx), b.Y(sy), 6, P.TITLE_FILL)
    title_text(b.X(0.5), b.Y(0.62), "VELKÁ A MALÁ", 38)
    title_text(b.X(0.5), b.Y(0.4), "DETEKTIVKA", 56)
    stroke([(2, 2), (b.w-2, 2), (b.w-2, b.h-2), (2, b.h-2)], 3.0, closed=True)


if __name__ == "__main__":
    E.render("logo", 320, 360, logo, "img")
    E.render("banner", 960, 300, banner, "img")
