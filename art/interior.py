"""Interiors for the game rooms (kitchen)."""
import math
from lib import C, ell, bez, rrect
import palette as P
from style3 import *
from scenes3 import BG, s_, sh_, floor, shelf, hills, ground


def rect(x0, y0, x1, y1):
    return [(x0, y0), (x1, y0), (x1, y1), (x0, y1)]


def tiled_band(b, y0, y1, step=18):
    fill(rect(b.x, y0, b.x+b.w, y1), P.KITCHEN_TILE)
    for yy in range(int(y0), int(y1), step): s_([(b.x, yy), (b.x+b.w, yy)], BG*0.4)
    for row, yy in enumerate(range(int(y0), int(y1), step)):
        off = (step/2) if row % 2 else 0
        x = b.x + off
        while x < b.x + b.w:
            s_([(x, yy), (x, min(y1, yy+step))], BG*0.4)
            x += step
    s_([(b.x, y1), (b.x+b.w, y1)], BG)


def window(x0, y0, x1, y1):
    sh_(rect(x0-8, y0-8, x1+8, y1+8), 1.0)
    glass = rect(x0, y0, x1, y1)
    fill(glass, P.SKY)
    C.saveState(); C.clipPath(poly(glass), stroke=0, fill=0)
    class _B: pass
    v = _B(); v.x, v.y, v.w, v.h = x0, y0, x1-x0, y1-y0
    hills(v, y0+(y1-y0)*0.25, 18, P.HILLS, 3)
    fill(rect(x0, y0, x1, y0+(y1-y0)*0.25), P.GRASS)
    C.restoreState()
    s_(glass, BG*1.2, closed=True)
    mx, my = (x0+x1)/2, (y0+y1)/2
    for pts in ([(mx, y0), (mx, y1)], [(x0, my), (x1, my)]):
        stroke(pts, BG*3.2, g=1.0); s_(pts, BG*0.6)
    form(rect(x0-18, y0-16, x1+18, y0-6), P.SILL, w=BG, sh=0)
    for side in (-1, 1):
        cx = x0-16 if side < 0 else x1+16
        cur = [(cx-14*side, y1+14), (cx+10*side, y1+14)] + bez((cx+10*side, y1+14), (cx+16*side, y0+60), (cx+4*side, y0+20), (cx+12*side, y0-4)) + \
              [(cx-14*side, y0-4)]
        form(cur, P.CURTAIN, w=BG, sdx=2*side, sdy=0, sh=0.1)
        for k in range(1, 4):
            s_(bez((cx-10*side+k*5*side, y1+12), (cx-8*side+k*5*side, y0+60), (cx-12*side+k*5*side, y0+30), (cx-10*side+k*5*side, y0)), BG*0.5)
    sh_(rect(x0-40, y1+14, x1+40, y1+18), P.TABLE)


def stove(x0, x1, y0, y1):
    body = rect(x0, y0, x1, y1)
    form(body, P.STOVE, w=BG, sdx=4, sdy=0, sh=0.12)
    step = (x1-x0)/4
    for k in range(1, 4): s_([(x0+k*step, y0+14), (x0+k*step, y1)], BG*0.5)
    yy = y0 + 14
    while yy < y1:
        s_([(x0, yy), (x1, yy)], BG*0.5); yy += step
    sh_(rect(x0-6, y1, x1+6, y1+8), P.METAL)
    sh_(rect(x0-4, y0, x1+4, y0+14), P.STOVE_DOOR)
    d = rrect(x0+step*0.8, y0+30, step*2.4, 36, 4)
    sh_(d, P.STOVE_DOOR)
    dot(x0+step*2.8, y0+48, 2.2, P.METAL)
    pipe_x = (x0+x1)/2
    sh_(rect(pipe_x-8, y1+8, pipe_x+8, y1+160), P.METAL)


def table(x0, x1, y_top, y_floor):
    for lx in (x0+10, x1-18):
        form(rect(lx, y_floor, lx+8, y_top), P.TABLE, w=BG, sdx=2, sdy=0, sh=0.1)
    cloth = [(x0-6, y_top-26), (x1+6, y_top-26), (x1+2, y_top+6), (x0-2, y_top+6)]
    fill(cloth, P.TABLECLOTH)
    C.saveState(); C.clipPath(poly(cloth), stroke=0, fill=0)
    for k in range(int(x0)-10, int(x1)+10, 14): fill(rect(k, y_top-30, k+7, y_top+10), P.CLOTH_CHECK, 0.6)
    for k in range(int(y_top)-26, int(y_top)+6, 14): fill(rect(x0-10, k, x1+10, k+7), P.CLOTH_CHECK, 0.6)
    C.restoreState()
    s_(cloth, BG, closed=True)


def jar(x, y, h=26, jam=True):
    body = rrect(x-9, y, 18, h, 4)
    form(body, P.JAR, w=BG, sdx=2, sdy=0, sh=0.08)
    if jam: clip_fill(body, rect(x-10, y, x+10, y+h*0.65), P.JAM)
    sh_(rect(x-10, y+h, x+10, y+h+5), P.CLOTH_CHECK)


def door(x0, x1, y0, y1):
    sh_(rect(x0-8, y0, x1+8, y1+8), P.DOOR_FRAME)
    sh_(rect(x0, y0, x1, y1), P.DOOR)
    for k in range(1, 3): s_([(x0+(x1-x0)*k/3, y0+2), (x0+(x1-x0)*k/3, y1-2)], BG*0.5)
    dot(x1-10, (y0+y1)/2, 2.6, P.BRASS)


def room_kitchen(b):
    fill(rect(b.x, b.y, b.x+b.w, b.y+b.h), P.KITCHEN_WALL)
    tiled_band(b, b.Y(0.3), b.Y(0.52))
    floor(b, b.Y(0.3), P.KITCHEN_FLOOR)
    stove(b.X(0.03), b.X(0.17), b.Y(0.3), b.Y(0.66))
    window(b.X(0.38), b.Y(0.52), b.X(0.6), b.Y(0.86))
    shelf(b.X(0.66), b.X(0.86), b.Y(0.64))
    jar(b.X(0.69), b.Y(0.64)+5); jar(b.X(0.72), b.Y(0.64)+5, 22, jam=False)
    door(b.X(0.89), b.X(0.98), b.Y(0.3), b.Y(0.78))
    table(b.X(0.21), b.X(0.34), b.Y(0.42), b.Y(0.3))
