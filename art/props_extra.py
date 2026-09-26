"""Extra props used by the longer issue-1 story (and the game)."""
import math, random
from lib import G, ell, bez, rrect
import palette as P
from style3 import *
from style3 import C
from chars3 import *
from scenes3 import *
from letter import hand_text

# ---------------------------------------------------------------- extra props for the longer story
def dog_bed(x, y, s=1.0):
    with T(x, y, s):
        shape(ell(0, 6, 26, 9, 40), P.DOG_BED, BG*1.2)
        shape(ell(0, 9, 20, 5.5, 36), P.DOG_BED_CUSHION, BG)
        for k_ in range(-20, 22, 6): stroke([(k_, 0.5), (k_*1.05, 5)], BG*0.5)

def old_sock(x, y, s=1.0, rot=0):
    sock_item(x, y, s, g=P.OLD_SOCK, rot=rot)
    with T(x, y, s, rot=rot):
        for (hx, hy) in ((1, -9), (5, -20), (-1, -14)):
            shape(ell(hx, hy, 1.2, 0.9, 10), 0.3, LINE*0.4)

def flour_bag(x, y, s=1.0):
    with T(x, y, s):
        bag = bez((-10, 0), (-12, 10), (-11, 20), (-8, 26)) + [(-4, 30), (0, 27), (4, 31), (8, 26)] + bez((8, 26), (11, 20), (12, 10), (10, 0))
        form(bag, P.FLOUR_BAG, sdx=2.5, sdy=0)
        hand_text(-10, 10, 20, "MOUKA", "SHB", 5.5)
        stroke([(-7, 24), (7, 24)], LINE*0.8)

def mug(x, y, s=1.0, steam=True):
    with T(x, y, s):
        form(rrect(-5, 0, 10, 11, 2), P.MUG, sdx=1.5, sdy=0)
        stroke(ell(6.5, 5.5, 3, 3, 16, -90, 90), LINE*1.2)
        fill(ell(0, 10.3, 4.3, 1.1, 16), P.COCOA)
        if steam:
            for dx in (-2, 1.5):
                stroke(bez((dx, 13), (dx-2, 16), (dx+2, 18), (dx, 21)), LINE*0.6, g=0.5)

def binoculars(x, y, s=1.0, rot=0):
    with T(x, y, s, rot=rot):
        for sx in (-1, 1):
            shape(rrect(sx*4.5-3.2, -8, 6.4, 13, 1.5), 0.25)
            shape(ell(sx*4.5, 5, 3.2, 1.3, 14), 0.6, LINE*0.7)
        shape([(-1.5, -2), (1.5, -2), (1.5, 2), (-1.5, 2)], 0.4, LINE*0.6)

def pumpkin(x, y, s=1.0):
    with T(x, y, s):
        for dx, rx in ((-7, 7), (7, 7), (0, 8)):
            shape(ell(dx, 8, rx, 8, 30), P.PUMPKIN_MID if dx == 0 else P.PUMPKIN, BG)
        stroke(bez((0, 15), (0.5, 18), (2, 20), (3.5, 21)), BG*2.4)
        stroke(bez((3.5, 21), (6, 22), (8, 20), (9, 22)), BG*0.8)

def raspberry_bush(x, y, s=1.0, seed=4):
    r = random.Random(seed)
    with T(x, y, s):
        pts = []
        N = 9
        for i in range(N):
            a0 = math.pi*i/N; a1 = math.pi*(i+1)/N
            p0 = (math.cos(a0)*28, math.sin(a0)*24); p1 = (math.cos(a1)*28, math.sin(a1)*24)
            am = (a0+a1)/2; m = (math.cos(am)*33, math.sin(am)*28)
            pts += bez(p0, ((p0[0]+m[0])/2, (p0[1]+m[1])/2+2), ((p1[0]+m[0])/2, (p1[1]+m[1])/2+2), p1, 5)
        shape(pts + [(-28, 0), (28, 0)], P.BUSH, BG)
        for i in range(10):
            bx, by = r.uniform(-22, 22), r.uniform(4, 20)
            shape(ell(bx, by, 1.8, 1.8, 10), P.BERRY, BG*0.5)
        for i in range(6):
            lx, ly = r.uniform(-20, 20), r.uniform(4, 22)
            stroke(ell(lx, ly, 3, 2, 10, 200, 340), BG*0.6)

def stream(p, y0, y1):
    top = [(p.x-5, y1)] + [(p.x+p.w*i/10, y1 + 3*math.sin(i*1.3)) for i in range(11)] + [(p.x+p.w+5, y1)]
    bot = [(p.x-5, y0)] + [(p.x+p.w*i/10, y0 + 3*math.sin(i*1.7+1)) for i in range(11)] + [(p.x+p.w+5, y0)]
    fill(top + list(reversed(bot)), P.WATER)
    stroke(top, BG); stroke(bot, BG)
    r = random.Random(3)
    for i in range(10):
        wx = p.x + p.w*r.random(); wy = y0 + (y1-y0)*(0.2 + 0.6*r.random())
        stroke(bez((wx, wy), (wx+5, wy+2), (wx+10, wy-2), (wx+15, wy)), BG*0.9, g=0.9)

def stone(x, y, rx, ry, g=P.STONE):
    form(ell(x, y, rx, ry, 30), g, w=BG*1.1, sdx=0, sdy=ry*0.5, sh=0.12)

def flour_patch(x, y, w, h):
    pts = []
    r = random.Random(9)
    for i in range(24):
        a = math.tau*i/24
        k = 1 + 0.12*math.sin(a*3+1) + r.uniform(-0.05, 0.05)
        pts.append((x + math.cos(a)*w/2*k, y + math.sin(a)*h/2*k))
    fill(pts, 0.99)
    C.saveState(); C.setDash(2, 2); C.setLineWidth(0.6); C.setStrokeColor(G(0.55))
    C.drawPath(poly(pts), fill=0, stroke=1); C.restoreState()

def tail_swish(x, y, L=30):
    stroke(bez((x, y), (x+L*0.3, y+4), (x+L*0.6, y-4), (x+L, y+1)), 2.2, g=0.55)

def silhouette_dormouse(x, y, s=1.0):
    with T(x, y, s):
        tube(bez((-6, 5), (-20, 2), (-26, 16), (-17, 24), 10), 5, 9, P.SILHOUETTE, sh=0)
        shape(ell(0, 9, 10, 9, 30), P.SILHOUETTE)
        shape(ell(2, 19, 8.5, 7.5, 30), P.SILHOUETTE)
        for sx in (-1, 1): shape(ell(sx*6+2, 26, 4, 4.3, 20), P.SILHOUETTE)
        dot(-1.6, 20.5, 1.1, 0.95); dot(5.6, 20.5, 1.1, 0.95)

def window_frame(p, x0, y0, x1, y1, night=True):
    """window in an interior wall; returns inner rect for outside view"""
    return (x0, y0, x1, y1)

def night_sky(p, g=0.55):
    fill([(p.x, p.y), (p.x+p.w, p.y), (p.x+p.w, p.y+p.h), (p.x, p.y+p.h)], g)

def dusk_sky(p, g=0.8):
    fill([(p.x, p.y), (p.x+p.w, p.y), (p.x+p.w, p.y+p.h), (p.x, p.y+p.h)], g)

