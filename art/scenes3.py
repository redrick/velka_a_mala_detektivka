import math, random
import lib
from lib import C, G, ell, bez, rrect, resample
import palette as P
from style3 import *

BG = 0.8   # background line weight (pt)

def s_(pts, w=BG, closed=False, g=0.0): stroke(pts, w, closed, g)
def sh_(pts, g, w=BG): shape(pts, g, w)

def sky(p, g=0.95):
    fill([(p.x, p.y), (p.x+p.w, p.y), (p.x+p.w, p.y+p.h), (p.x, p.y+p.h)], g)

def cloud(x, y, s=1.0):
    with T(x, y, s):
        pts = bez((-30, 0), (-34, 10), (-22, 15), (-16, 11)) + bez((-16, 11), (-13, 22), (5, 24), (8, 15)) + \
              bez((8, 15), (15, 22), (30, 17), (27, 6)) + bez((27, 6), (34, 3), (32, -4), (25, -4)) + [(-26, -4)] + \
              bez((-26, -4), (-33, -4), (-33, 0), (-30, 0))
        sh_(pts, 1.0)

def hills(p, y, h=25, g=0.86, seed=1):
    pts = [(p.x-5, p.y)]
    P = []
    n = 5
    ys = [y + h*(0.35+0.65*abs(math.sin(i*1.9+seed))) for i in range(n+1)]
    for i in range(n):
        x0 = p.x + p.w*i/n; x1 = p.x + p.w*(i+1)/n
        P += bez((x0, ys[i]), (x0+(x1-x0)*0.45, ys[i]), (x1-(x1-x0)*0.45, ys[i+1]), (x1, ys[i+1]), 10)
    fill([(p.x-5, p.y)] + P + [(p.x+p.w+5, p.y)], g)
    s_(P, BG*0.8)

def ground(p, y, g=0.88, seed=1):
    pts = [(p.x-5, p.y-5), (p.x-5, y), (p.x+p.w+5, y), (p.x+p.w+5, p.y-5)]
    fill(pts, g)
    s_([(p.x-5, y), (p.x+p.w+5, y)], BG)

def tufts(p, y0, y1, n=8, seed=3):
    r = random.Random(seed)
    for i in range(n):
        x = p.x + p.w*(0.04 + 0.92*r.random()); y = y0 + (y1-y0)*r.random()
        k = 0.7 + (1 - (y-y0)/max(1, (y1-y0)))*0.7
        pts = [(x-4*k, y), (x-3.2*k, y+4.5*k), (x-1.8*k, y+1.2*k), (x-0.3*k, y+7*k), (x+1.2*k, y+1.3*k),
               (x+3*k, y+5*k), (x+3.6*k, y+0.8*k), (x+4.2*k, y)]
        sh_(pts, P.TUFT, BG*0.7)
        # little ground line
        s_([(x-8*k, y-0.3), (x-5*k, y-0.3)], BG*0.6)

def path(p, pts_l, pts_r, g=0.93):
    fill(pts_l + list(reversed(pts_r)), g)
    s_(pts_l, BG*0.8); s_(pts_r, BG*0.8)

def tree(x, y, s=1.0, seed=3, g=P.TREE_CROWN):
    r = random.Random(seed)
    with T(x, y, s):
        trunk = bez((-8, 0), (-5.5, 20), (-6, 40), (-4, 60)) + [(4, 60)] + bez((4, 60), (6, 40), (5.5, 20), (8, 0))
        form(trunk, P.BARK, w=BG, sdx=2, sdy=0, sh=0.15)
        s_(bez((-2, 8), (-1.5, 18), (-2.5, 28), (-1.8, 36)), BG*0.6); s_(bez((2.5, 22), (2, 30), (3, 40), (2.2, 48)), BG*0.6)
        stroke(bez((0, 52), (-7, 60), (-13, 66), (-17, 70)), BG*3.2); stroke(bez((0, 52), (-7, 60), (-13, 66), (-17, 70)), BG*1.6, g=P.BARK)
        # crown: one clean scalloped mass
        pts = []
        cx, cy, rx, ry = 0, 88, 40, 30; N = 11
        for i in range(N):
            a0 = math.tau*i/N; a1 = math.tau*(i+1)/N
            p0 = (cx+math.cos(a0)*rx, cy+math.sin(a0)*ry); p1 = (cx+math.cos(a1)*rx, cy+math.sin(a1)*ry)
            am = (a0+a1)/2; k = 1.16 + 0.08*r.random()
            m = (cx+math.cos(am)*rx*k, cy+math.sin(am)*ry*k)
            pts += bez(p0, ((p0[0]+m[0])/2+(m[0]-cx)*0.18, (p0[1]+m[1])/2+(m[1]-cy)*0.18),
                       ((p1[0]+m[0])/2+(m[0]-cx)*0.18, (p1[1]+m[1])/2+(m[1]-cy)*0.18), p1, 6)
        fill(pts, g)
        offset_shadow(pts, 6, 5, 0.12)
        stroke(pts, BG*1.1, closed=True)
        # internal volume curls
        for (ax, ay, a0, a1) in ((-18, 80, 200, 330), (10, 76, 210, 330), (-4, 96, 200, 320), (20, 94, 210, 330), (-26, 94, 210, 320)):
            s_(ell(ax, ay, 9, 6, 12, a0, a1), BG*0.7)
        for i in range(6):
            leaf(r.uniform(-32, 32), r.uniform(72, 108), 3.2, r.uniform(0, 360), P.LEAF_LIGHT if i % 2 else P.LEAF_DARK)

def leaf(x, y, s=4, rot=0, g=0.8):
    with T(x, y, s/10, rot=rot):
        pts = bez((0, -10), (6, -7), (7, 2), (0, 10)) + bez((0, 10), (-7, 2), (-6, -7), (0, -10))
        sh_(pts, g, BG*0.8)
        s_([(0, -13), (0, 6)], BG*0.6)

def falling_leaves(p, n=5, seed=2, y0=0.35):
    r = random.Random(seed)
    for i in range(n):
        leaf(p.x + p.w*(0.05+0.9*r.random()), p.y + p.h*(y0+(0.92-y0)*r.random()), 4.5 + r.random()*1.5, r.random()*360,
             0.5 if i % 2 else 0.9)

def house(x, y, s=1.0, smoke=True):
    with T(x, y, s):
        wall = [(-50, 0), (50, 0), (50, 56), (-50, 56)]
        sh_(wall, P.WALL)
        fill([(-50, 56), (50, 56), (50, 51), (-50, 51)], P.WALL_SHADE)
        base = [(-50, 0), (50, 0), (50, 10), (-50, 10)]
        sh_(base, P.STONE_BASE)
        for xx in (-40, -28, -15, -2, 11, 24, 37): s_([(xx, 0), (xx, 5)], BG*0.6); s_([(xx+6, 5), (xx+6, 10)], BG*0.6)
        s_([(-50, 5), (50, 5)], BG*0.6)
        roof = [(-61, 53), (0, 104), (61, 53)]
        sh_(roof, P.ROOF)
        C.saveState(); C.clipPath(poly(roof), stroke=0, fill=0)
        for row in range(1, 10):
            yy = 53 + row*5.2
            s_([(-62, yy), (62, yy)], BG*0.55)
        C.restoreState()
        sh_([(-63, 50.5), (63, 50.5), (63, 53.5), (-63, 53.5)], P.ROOF_EDGE)
        ch = [(22, 80), (22, 104), (32, 104), (32, 72)]
        sh_(ch, P.CHIMNEY)
        sh_([(20, 104), (34, 104), (34, 107.5), (20, 107.5)], P.CHIMNEY_CAP)
        if smoke:
            for (sx, sy, rr) in ((29, 115, 4.5), (35, 125, 6), (44, 135, 7.5)):
                sh_(ell(sx, sy, rr, rr*0.75, 22), 1.0, BG*0.7)
        sh_(ell(0, 70, 8, 8, 30), P.ROUND_WINDOW); s_([(-8, 70), (8, 70)], BG*0.9, g=0.85); s_([(0, 62), (0, 78)], BG*0.9, g=0.85)
        for wx in (-35, 17):
            sh_([(wx-1.5, 18.5), (wx+19.5, 18.5), (wx+19.5, 43.5), (wx-1.5, 43.5)], 1.0)
            gl = [(wx, 20), (wx+18, 20), (wx+18, 42), (wx, 42)]
            sh_(gl, P.WINDOW_GLASS)
            clip_fill(gl, [(wx+3, 20), (wx+7, 20), (wx+14, 42), (wx+10, 42)], P.WINDOW_GLINT)
            s_([(wx+9, 20), (wx+9, 42)], BG*1.2, g=1.0); s_([(wx, 31), (wx+18, 31)], BG*1.2, g=1.0)
            s_([(wx+9, 20), (wx+9, 42)], BG*0.5); s_([(wx, 31), (wx+18, 31)], BG*0.5)
            for xx in (wx-8, wx+19.5):
                sh_([(xx, 18.5), (xx+6.5, 18.5), (xx+6.5, 43.5), (xx, 43.5)], P.SHUTTER)
                for kk in range(5): s_([(xx+1, 21.5+kk*4.5), (xx+5.5, 21.5+kk*4.5)], BG*0.5)
            sh_([(wx-3, 15.5), (wx+21, 15.5), (wx+21, 18.5), (wx-3, 18.5)], P.SILL)
            for fx in range(4):
                sh_(ell(wx+2+fx*4.8, 21, 1.9, 1.9, 14), P.FLOWER, BG*0.6)
        d = [(-8, 10), (7, 10), (7, 43), (-8, 43)]
        sh_(d, P.DOOR)
        for kk in (-4.2, -0.5, 3.2): s_([(kk, 11), (kk, 42)], BG*0.5)
        dot(4.5, 26, 0.8, 0.9)

def fence(x0, x1, y, h=40, step=15, g=0.95):
    for yy in (y+h*0.28, y+h*0.7):
        sh_([(x0, yy), (x1, yy), (x1, yy+4), (x0, yy+4)], P.FENCE_RAIL)
    x = x0 + 3
    while x < x1:
        pk = [(x, y), (x+10, y), (x+10, y+h), (x+5, y+h+6), (x, y+h)]
        form(pk, g, w=BG, sdx=3, sdy=0, sh=0.1)
        x += step

def clothesline(x0, x1, y, h=70, items=("shirt", "sock", "towel")):
    for px in (x0, x1):
        sh_([(px-2.5, y), (px+2.5, y), (px+2.5, y+h), (px-2.5, y+h)], P.POST)
        sh_([(px-11, y+h-4), (px+11, y+h-4), (px+11, y+h), (px-11, y+h)], P.POST)
    rope = bez((x0+9, y+h-2), (x0+(x1-x0)*0.35, y+h-16), (x0+(x1-x0)*0.65, y+h-16), (x1-9, y+h-2), 30)
    s_(rope, BG*0.7)
    n = len(items)
    for i, it in enumerate(items):
        k = int((i+1)/(n+1)*30); rx, ry = rope[k]
        if it == "empty": continue
        if it == "sock":
            pts = bez((rx-4, ry), (rx-4, ry-8), (rx-4, ry-14), (rx-3.5, ry-16)) + bez((rx-3.5, ry-16), (rx, ry-24), (rx+8, ry-27), (rx+9.5, ry-23)) + \
                  bez((rx+9.5, ry-23), (rx+10, ry-19), (rx+5, ry-17), (rx+4, ry-14)) + [(rx+4, ry)]
            sh_(pts, P.SOCK_RED)
            sh_([(rx-4, ry), (rx+4, ry), (rx+4, ry-4), (rx-4, ry-4)], 0.9)
        elif it == "shirt":
            pts = [(rx-11, ry), (rx-4, ry+1), (rx, ry-2), (rx+4, ry+1), (rx+11, ry), (rx+17, ry-7), (rx+12, ry-11), (rx+10, ry-8),
                   (rx+10, ry-28), (rx-10, ry-28), (rx-10, ry-8), (rx-12, ry-11), (rx-17, ry-7)]
            form(pts, 1.0, w=BG, sdx=3, sdy=0, sh=0.08)
            for kk in range(3): dot(rx, ry-7-kk*6, 0.8, 0.4)
        elif it == "towel":
            pts = [(rx-11, ry), (rx+11, ry), (rx+11.5, ry-26), (rx-10.5, ry-26.5)]
            sh_(pts, P.TOWEL)
            for kk in (-6, 6): s_([(rx+kk, ry-2), (rx+kk+0.3, ry-24)], BG*0.5)
        sh_([(rx-1.2, ry+3), (rx+1.2, ry+3), (rx+1.2, ry-4), (rx-1.2, ry-4)], P.PEG, BG*0.6)

def planks(p, g=0.78, step=24, seed=11, knots=True):
    r = random.Random(seed)
    fill([(p.x, p.y), (p.x+p.w, p.y), (p.x+p.w, p.y+p.h), (p.x, p.y+p.h)], g)
    x = p.x + r.uniform(4, step)
    while x < p.x + p.w:
        s_([(x, p.y), (x, p.y+p.h)], BG)
        if knots and r.random() < 0.35:
            kx, ky = x - step*r.uniform(0.3, 0.7), p.y + p.h*r.uniform(0.2, 0.85)
            s_(ell(kx, ky, 2.4, 1.5, 16) + [(kx+2.4, ky)], BG*0.6)
        if r.random() < 0.5:
            gx = x - step*r.uniform(0.3, 0.7); gy = p.y + p.h*r.uniform(0.1, 0.6)
            s_([(gx, gy), (gx+0.5, gy+p.h*0.25)], BG*0.5)
        x += step*r.uniform(0.9, 1.1)

def floor(p, y_top, g=0.6):
    fill([(p.x, p.y), (p.x+p.w, p.y), (p.x+p.w, y_top), (p.x, y_top)], g)
    for k in range(1, 4):
        yy = p.y + (y_top-p.y)*(1 - (k/4)**1.5)
        s_([(p.x, yy), (p.x+p.w, yy)], BG*0.6)
    s_([(p.x, y_top), (p.x+p.w, y_top)], BG)

def sunbeam(x_top0, x_top1, y_top, x_bot0, x_bot1, y_bot, alpha=0.3):
    fill([(x_top0, y_top), (x_top1, y_top), (x_bot1, y_bot), (x_bot0, y_bot)], P.SUNBEAM, alpha)

def shelf(x0, x1, y):
    sh_([(x0, y), (x1, y), (x1, y+5), (x0, y+5)], P.SHELF)
    fill([(x0, y), (x1, y), (x1, y-3), (x0, y-3)], 0.0, 0.12)
    for bx in (x0+14, x1-14):
        sh_([(bx-2, y), (bx+2, y), (bx+10, y-13), (bx+6, y-13)], P.SHELF_BRACKET)

def boot(x, y, s=1.0):
    with T(x, y, s):
        sh_([(-11, 0), (27, 0), (29, 2.5), (-11, 2.5)], 0.2)
        body = [(-11, 2.5)] + bez((-11, 2.5), (-12, 20), (-12, 34), (-12.5, 44)) + [(8.5, 44)] + \
               bez((8.5, 44), (8, 30), (8.5, 20), (11, 15)) + bez((11, 15), (20, 13), (29, 10), (28.5, 2.5))
        form(body, P.BOOT, w=BG*1.2, sdx=3, sdy=0, sh=0.15)
        s_(bez((12, 3), (14, 9), (20, 11), (28, 9)), BG*0.6)
        for kk in range(4):
            yy = 19 + kk*5.5
            s_([(3, yy), (7, yy+4)], BG*0.7, g=0.95); s_([(7, yy), (3, yy+4)], BG*0.7, g=0.95)
        sh_([(-13.5, 43), (9.5, 43), (9.5, 47), (-13.5, 47)], P.BOOT_TOP)
        fill(ell(-2, 46.5, 10.5, 2.3, 24), 0.05)

def rake(x, y, s=1.0):
    with T(x, y, s):
        tube([(0, 0), (0, 85)], 2.4, 2.2, P.RAKE_HANDLE, lw=BG, sh=0)
        sh_([(-14, -1), (14, -1), (14, 3), (-14, 3)], P.METAL)
        for kk in range(-12, 14, 4): s_([(kk, -1), (kk, -9)], BG*1.2)

def saw(x, y, s=1.0):
    with T(x, y, s):
        sh_([(0, 0), (50, 4), (50, 13), (0, 16)], P.SAW_BLADE)
        for kk in range(0, 49, 3): s_([(kk, 0.08*kk), (kk+1.5, 0.08*kk-2)], BG*0.5)
        sh_(rrect(-15, 0, 17, 16, 5), P.SAW_HANDLE)
        sh_(rrect(-11, 4.5, 9, 7, 2.5), 0.78)

def crate(x, y, w, h, g=P.CRATE):
    form([(x, y), (x+w, y), (x+w, y+h), (x, y+h)], g, w=BG, sdx=4, sdy=0, sh=0.1)
    for k in range(1, 3): s_([(x, y+h*k/3), (x+w, y+h*k/3)], BG*0.8)
    s_([(x+3, y+3), (x+w-3, y+h-3)], BG*0.8)

def watering_can(x, y, s=1.0):
    with T(x, y, s):
        sh_([(8, 6), (24, 18), (26, 17), (10, 3)], P.CAN_SPOUT)
        form(rrect(-10, 0, 20, 18, 3), P.CAN, w=BG, sdx=3, sdy=0, sh=0.1)
        stroke(bez((-8, 16), (-12, 28), (8, 28), (6, 17)), BG*2.4); stroke(bez((-8, 16), (-12, 28), (8, 28), (6, 17)), BG*1.0, g=P.CAN)

def red_thread(pts, w=1.2):
    line = resample(pts, 2.0)
    line = [(x + 0.6*math.sin(i*0.9), y + 0.4*math.cos(i*1.3)) for i, (x, y) in enumerate(line)]
    stroke(line, w+1.4, g=1.0); stroke(line, w, g=P.THREAD)

def shed(x, y, s=1.0, door_open=True):
    with T(x, y, s):
        wall = [(-40, 0), (40, 0), (40, 55), (-40, 60)]
        sh_(wall, P.SHED_WALL)
        for xx in range(-31, 40, 9): s_([(xx, 0), (xx, 60 - (xx+40)*5/80)], BG*0.6)
        roof = [(-48, 56), (48, 49.5), (46, 62), (-46, 70)]
        sh_(roof, P.SHED_ROOF)
        fill([(-40, 58), (40, 52), (40, 48), (-40, 54)], 0.0, 0.15)
        if door_open:
            sh_([(-12, 0), (12, 0), (12, 42), (-12, 42)], 0.12)
            sh_([(12, 0), (23, 3), (23, 45), (12, 42)], P.SHED_DOOR)
            s_([(17.5, 2), (17.5, 43)], BG*0.5)
        else:
            sh_([(-12, 0), (12, 0), (12, 42), (-12, 42)], P.SHED_DOOR_SHUT)
        sh_([(24, 28), (35, 28), (35, 40), (24, 40)], P.ROUND_WINDOW)
        s_([(29.5, 28), (29.5, 40)], BG*0.8, g=0.8); s_([(24, 34), (35, 34)], BG*0.8, g=0.8)
