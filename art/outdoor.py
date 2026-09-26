"""Outdoor game rooms (zahumenek)."""
import math, random
from lib import C, ell, bez, rrect
import palette as P
from style3 import *
from scenes3 import BG, s_, sh_, sky, cloud, hills, ground, tufts, tree, shed, fence
from props_extra import pumpkin, raspberry_bush, stone


def stream_across(b, y_top, top, bottom):
    """stream running from the horizon towards the viewer; top/bottom = (x_left, x_right)"""
    n = 12
    left = [(top[0] + (bottom[0]-top[0])*i/n + 4*math.sin(i*1.3), y_top - y_top*i/n) for i in range(n+1)]
    right = [(top[1] + (bottom[1]-top[1])*i/n + 4*math.sin(i*1.7+1), y_top - y_top*i/n) for i in range(n+1)]
    fill(left + list(reversed(right)) + [left[0]], P.WATER)
    s_(left, BG); s_(right, BG)
    r = random.Random(5)
    for i in range(14):
        t = r.random()
        y = y_top*(1-t)
        xl = top[0] + (bottom[0]-top[0])*t; xr = top[1] + (bottom[1]-top[1])*t
        x = xl + (xr-xl)*(0.15 + 0.6*r.random()); w = (xr-xl)*0.18
        stroke(bez((x, y), (x+w*0.3, y+1.5), (x+w*0.6, y-1.5), (x+w, y)), BG*0.8, g=1.0)


def pumpkin_patch(x, y):
    for (dx, dy, s) in ((0, 0, 2.2), (70, -18, 1.8), (150, 6, 2.0), (40, 40, 1.5)):
        stroke(bez((x+dx-30, y+dy+4), (x+dx-10, y+dy+14), (x+dx+10, y+dy-6), (x+dx+30, y+dy+6)), BG*1.2, g=P.TUFT)
        pumpkin(x+dx, y+dy, s)


def room_zahumenek(b):
    sky(b, P.SKY); cloud(b.X(0.15), b.Y(0.85), 1.0); cloud(b.X(0.62), b.Y(0.8), 1.2)
    hills(b, b.Y(0.5), 26, P.HILLS, 4)
    ground(b, b.Y(0.42), P.GRASS)
    tree(b.X(0.06), b.Y(0.4), 1.6, seed=9)
    shed(b.X(0.9), b.Y(0.42), 1.0)
    raspberry_bush(b.X(0.2), b.Y(0.395), 2.7)
    stream_across(b, b.Y(0.42), (b.X(0.72), b.X(0.79)), (b.X(0.66), b.X(0.86)))
    pumpkin_patch(b.X(0.08), b.Y(0.1))
    class _Left: pass
    left = _Left(); left.x, left.y, left.w, left.h = b.x, b.y, b.X(0.6), b.h
    tufts(left, b.Y(0.02), b.Y(0.3), 10, 8)


def fence_with_gap(b):
    fence(0, b.X(0.44), 4, 44)
    fence(b.X(0.535), b.w, 4, 44)


def nail(b):
    x = b.w/2
    shape([(x-1.3, 3), (x+1.3, 3), (x+1.3, 22), (x-1.3, 22)], P.METAL, LINE*0.7)
    shape([(x-1.3, 3), (x+1.3, 3), (x, 0)], P.METAL, LINE*0.6)
    shape(rrect(x-4.5, 22, 9, 3, 1), P.METAL, LINE*0.8)
