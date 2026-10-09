"""Issue 6 (Kam mizí perníčky?): Advent gingerbread, tits at the window, a mousetrap with no bait, děda's boots,
the Klub Hvězdička star spruce by the mill.

The comic prints in grey on a laser printer, so every clue tells apart by tone or shape, never by colour:
the hearts are dipped in chocolate (dark), the stars have white icing (light)."""
import math, random
from lib import ell, bez, rrect
from style3 import *
from style3 import C
import palette as P
from scenes3 import BG, s_, sh_
from chars3 import star


# ------------------------------------------------------------------ the hidden-object game
def _man_outline(r):
    """a gingerbread man's silhouette, standing on y = -r, head top at y = r"""
    pts = []
    hx, hy, hr = 0, r*0.62, r*0.36
    a0 = math.radians(-62)
    for i in range(19):                                    # head, from the right of the neck over the top
        a = a0 + (math.pi + 2*math.radians(62))*i/18
        pts.append((hx + math.cos(a)*hr, hy + math.sin(a)*hr))
    pts = pts[::-1]                                        # now left of the neck to the right, over the top
    right = [(r*0.2, r*0.28), (r*0.66, r*0.24)] + \
            [(r*0.68 + math.cos(a)*r*0.15, r*0.1 + math.sin(a)*r*0.15) for a in (1.2, 0.4, -0.4, -1.2)] + \
            [(r*0.62, -r*0.04), (r*0.26, -r*0.06), (r*0.44, -r*0.82)] + \
            [(r*0.32 + math.cos(a)*r*0.17, -r*0.86 + math.sin(a)*r*0.17) for a in (-0.3, -1.1, -1.9, -2.6)] + \
            [(r*0.12, -r*0.8), (0, -r*0.46)]
    left = [(-x, y) for x, y in reversed(right[:-1])]
    return pts[-1:] + right + left[1:] + [(-r*0.2, r*0.28)] + pts[:-1]


def hidden_gingerbread_man(x, y, r=13):
    """one of the 12 gingerbread men hidden in the issue. Dark, with white icing dots, inside a white halo and a
    black line, so it reads on white snow and on dark wood alike (the comic prints in grey)"""
    with T(x, y, 1.0):
        o = _man_outline(r)
        stroke(o, LINE*4.4, closed=True, g=0.0, taper=False)
        stroke(o, LINE*2.8, closed=True, g=1.0, taper=False)
        fill(o, P.GINGER_DARK)
        stroke(o, LINE*0.5, closed=True, g=0.0, taper=False)
        for ex in (-0.13, 0.13): dot(ex*r, r*0.68, r*0.07, 1.0)
        stroke(bez((-r*0.14, r*0.52), (-r*0.06, r*0.44), (r*0.06, r*0.44), (r*0.14, r*0.52)), LINE*0.6, g=1.0)
        for by in (0.16, -0.08, -0.32): dot(0, by*r, r*0.075, 1.0)


# ------------------------------------------------------------------ gingerbread
def _star_pts(r, inner=0.5, n=5):
    return [(math.cos(math.pi/2 + i*math.pi/n)*(r if i % 2 == 0 else r*inner),
             math.sin(math.pi/2 + i*math.pi/n)*(r if i % 2 == 0 else r*inner)) for i in range(2*n)]


def star_cookie(x, y, s=1.0, rot=0, pecked=0):
    """a gingerbread star with a white icing outline (light, so it tells from the chocolate hearts in grey).
    pecked: how many bites the tits took out of it (0–3)"""
    with T(x, y, s, rot=rot):
        shape(_star_pts(10, 0.52), P.GINGER, LINE*0.8)
        stroke(_star_pts(7.4, 0.5), LINE*0.9, closed=True, g=P.ICING, taper=False)
        dot(0, 0, 1.4, P.ICING)
        for bx, by in ((6, 4), (-5, -6), (2, 8))[:pecked]:
            shape(ell(bx, by, 2.6, 2.2, 10), 1.0, LINE*0.4)


def heart_cookie(x, y, s=1.0, rot=0, bitten=False):
    """a gingerbread heart dipped in chocolate: the top half is dark"""
    with T(x, y, s, rot=rot):
        pts = bez((0, -8), (-10, 0), (-6, 9), (0, 5)) + bez((0, 5), (6, 9), (10, 0), (0, -8))
        shape(pts, P.GINGER, LINE*0.8)
        C.saveState(); C.clipPath(poly(pts), stroke=0, fill=0)
        fill(bez((-12, 0.5), (-4, 2.5), (4, -1.5), (12, 1)) + [(12, 12), (-12, 12)], P.CHOCOLATE)
        C.restoreState()
        stroke(pts, LINE*0.8, closed=True)
        if bitten: shape(ell(6, 4, 2.8, 2.4, 10), 1.0, LINE*0.4)


def moon_cookie(x, y, s=1.0, rot=0):
    """a gingerbread crescent moon sprinkled with sugar dots"""
    with T(x, y, s, rot=rot):
        outer = [(math.cos(a)*9, math.sin(a)*9) for a in [math.radians(60 + i*12) for i in range(21)]]
        inner = [(3.5 + math.cos(a)*7, 1.5 + math.sin(a)*7) for a in [math.radians(300 - i*12) for i in range(21)]]
        shape(outer + inner, P.GINGER, LINE*0.8)
        for dx, dy in ((-6, 2), (-4, -4), (-5, 6), (-1, -7)): dot(dx, dy, 0.8, P.ICING)


def crumbs(x, y, w=20, h=8, n=9, g=P.CHOCOLATE, seed=1, k=1.0):
    r = random.Random(seed)
    for _ in range(n):
        cx, cy = x + r.uniform(-w/2, w/2), y + r.uniform(-h/2, h/2)
        k_ = r.uniform(0.8, 1.8)*k
        shape([(cx - k_, cy - k_*0.6), (cx + k_*0.9, cy - k_*0.8), (cx + k_*0.6, cy + k_*0.7), (cx - k_*0.7, cy + k_*0.5)], g, LINE*0.35)


def cookie_tin(x, y, w=150, stars=12, hearts=12, moons=12, lid=True):
    """the tin seen from above, three rows: stars, hearts, moons. Up to 12 in a row; the reader can count them"""
    h = w*0.62
    if lid:
        shape(ell(x + w + 26, y + h*0.5, 26, h*0.42, 30), P.TIN, LINE)
        star(x + w + 26, y + h*0.5, 9, 0.95)
    shape(rrect(x - 5, y - 5, w + 10, h + 10, 8), P.TIN, LINE*1.2)
    shape(rrect(x, y, w, h, 6), 0.86, LINE*0.6)
    step = (w - 12)/12
    for row, (n, fn) in enumerate(((stars, star_cookie), (hearts, heart_cookie), (moons, moon_cookie))):
        yy = y + h - (row + 0.5)*h/3
        for i in range(n):
            fn(x + 6 + step*(i + 0.5), yy, step/20, rot=(i % 3 - 1)*8)


def tray(x, y, w=110, pieces=6, pecked=True, seed=3):
    """the baking tray of broken and crooked pieces cooling on the sill outside"""
    shape([(x, y), (x + w, y), (x + w - 4, y + 7), (x + 4, y + 7)], P.TIN, LINE)
    r = random.Random(seed)
    for i in range(pieces):
        px = x + 12 + i*(w - 24)/max(1, pieces - 1); py = y + 9
        k = r.choice((0, 1, 2))
        pts = [(px + math.cos(a)*r.uniform(5, 8), py + 3 + math.sin(a)*r.uniform(3, 6)) for a in
               [math.tau*j/7 for j in range(7)]]
        shape(pts, P.GINGER, LINE*0.6)
        if pecked and k:
            for j in range(k): dot(px - 2 + j*4, py + 4 + (j % 2)*2, 1.0, 1.0)


# ------------------------------------------------------------------ birds
def tit(x, y, s=1.0, flip=False, kind="great", pose="perch"):
    """a great tit (black cap and bib, white cheek, a dark stripe down the yellow belly) or a blue tit
    (light cap, white face, a dark eye stripe). pose: perch, peck, fly"""
    cap = P.TIT_CAP if kind == "great" else P.BLUETIT_CAP
    with T(x, y, s, flip):
        with T(0, 0, 1.0, rot=-25 if pose == "peck" else 0):
            shape([(-6, 7), (-15, 4.5), (-14.5, 1.5), (-6, 3.5)], P.TIT_BACK, LINE*0.6)
            body = ell(0, 6, 8, 6, 24)
            shape(body, P.TIT_BELLY, LINE*0.8)
            C.saveState(); C.clipPath(poly(body), stroke=0, fill=0)
            fill(ell(-3.5, 10, 8, 4.6, 20), P.TIT_BACK)
            if kind == "great": stroke([(4.2, 7), (3.4, 0)], 1.8, g=P.TIT_CAP, taper=False)
            C.restoreState()
            stroke(bez((-8, 8), (-4, 6), (0, 6.5), (3, 8.5)), LINE*0.5, g=0.2)
            if pose == "fly": shape([(-2, 10), (-12, 22), (-4, 11)], P.TIT_BACK, LINE*0.6)
            head = ell(6, 11, 4.6, 4.4, 20)
            shape(head, 1.0, LINE*0.7)
            C.saveState(); C.clipPath(poly(head), stroke=0, fill=0)
            fill([(0, 12.4), (12, 12.8), (12, 17), (0, 17)], cap)
            if kind == "great": fill([(0, 5), (12, 5), (12, 8.6), (0, 8.2)], P.TIT_CAP)
            else: stroke([(1.5, 11.2), (11, 11.4)], 0.9, g=0.1, taper=False)
            C.restoreState()
            stroke(head, LINE*0.7, closed=True)
            dot(8, 11.6, 0.8, 0.0 if kind == "blue" else 0.05)
            shape([(10.4, 11.6), (12.8, 11), (10.5, 10.4)], 0.2, 0.5)
        if pose != "fly":
            stroke([(0, 1), (0, -3)], 0.6); stroke([(2, 1), (2.4, -3)], 0.6)

def bird_print(x, y, s=1.0, rot=0, g=0.35):
    """a tit's three-toed print, the size of a fingernail"""
    with T(x, y, s, rot=rot):
        for a in (-30, 0, 30):
            ra = math.radians(90 + a)
            stroke([(0, 0), (math.cos(ra)*4, math.sin(ra)*4)], LINE*0.8, g=g)
        stroke([(0, 0), (0, -2.5)], LINE*0.8, g=g)


def peck_marks(x, y, w=30, n=8, seed=2):
    """little peck marks in the frost on the glass"""
    r = random.Random(seed)
    for _ in range(n):
        cx, cy = x + r.uniform(0, w), y + r.uniform(-4, 4)
        shape(ell(cx, cy, 2.2, 1.7, 8), 0.5, LINE*0.4)


def frost(x0, y0, x1, y1, seed=4):
    """frost ferns in the corners of a window pane"""
    r = random.Random(seed)
    for cx, cy, sx, sy in ((x0, y0, 1, 1), (x1, y0, -1, 1), (x0, y1, 1, -1), (x1, y1, -1, -1)):
        for _ in range(4):
            a = r.uniform(0.2, 1.3); L = r.uniform(10, 22)
            ex, ey = cx + sx*math.cos(a)*L, cy + sy*math.sin(a)*L
            stroke([(cx, cy), (ex, ey)], 0.7, g=1.0)
            for k in (0.4, 0.7):
                mx, my = cx + (ex - cx)*k, cy + (ey - cy)*k
                stroke([(mx, my), (mx + sx*4, my + sy*1)], 0.5, g=1.0)
                stroke([(mx, my), (mx + sx*1, my + sy*4)], 0.5, g=1.0)


def bird_feeder(x, y, s=1.0, birds=0):
    """a little roofed feeder on a post, seeds on the tray"""
    with T(x, y, s):
        sh_([(-2.5, 0), (2.5, 0), (2.5, 46), (-2.5, 46)], P.FEEDER)
        shape([(-20, 46), (20, 46), (20, 50), (-20, 50)], P.FEEDER, LINE)
        for sx in (-17, 17): sh_([(sx - 1.5, 50), (sx + 1.5, 50), (sx + 1.5, 64), (sx - 1.5, 64)], P.FEEDER, BG*0.7)
        shape([(-26, 62), (0, 78), (26, 62), (22, 59), (0, 72), (-22, 59)], P.FEEDER_ROOF, LINE)
        fill([(-26, 62), (0, 78), (26, 62), (0, 74)], P.SNOW)
        r = random.Random(3)
        for _ in range(14): dot(r.uniform(-15, 15), 51.5 + r.uniform(0, 2), 0.9, P.SEEDS)
        if birds >= 1: tit(-10, 50, 0.9, kind="great", pose="peck")
        if birds >= 2: tit(10, 50, 0.85, flip=True, kind="blue")


def seed_star(x, y, s=1.0, rot=0, string=True):
    """a star of lard and seeds, hung up for the birds instead of gingerbread"""
    with T(x, y, s, rot=rot):
        if string: stroke([(0, 9), (0, 20)], 0.6, g=0.3)
        shape(_star_pts(10, 0.5), P.LARD, LINE*0.8)
        r = random.Random(int(x*7 + y))
        for _ in range(12):
            a = r.uniform(0, math.tau); d = r.uniform(0, 5)
            dot(math.cos(a)*d, math.sin(a)*d, 0.8, P.SEEDS)


# ------------------------------------------------------------------ the kitchen and the hall
def mousetrap(x, y, s=1.0, bait=False):
    """a wooden mousetrap, set. Without bait the hook is empty: děda doesn't believe in his mice"""
    with T(x, y, s):
        form([(-16, 0), (16, 0), (16, 5), (-16, 5)], P.TRAP_WOOD, w=LINE*0.8, sdx=1.5, sdy=0)
        stroke([(-12, 5.4), (12, 5.4)], 0.9, g=0.3)
        stroke([(-11, 5.4), (-11, 11), (5, 11), (5, 5.4)], 1.0, g=0.3)
        shape(ell(-2, 5.8, 2.4, 1.2, 10), 0.4, 0.4)
        stroke([(6, 6), (10, 9), (13, 8)], 0.7, g=0.3)                # the empty hook
        if bait: shape([(9, 8), (15, 8), (12, 12)], 0.92, LINE*0.6)


def paw_print(x, y, s=1.0, rot=0, g=1.0, line=0.5):
    """a dog's paw print: a pad and four toes. White = floury, on a darker floor"""
    with T(x, y, s, rot=rot):
        shape(bez((-4, 0), (-5, 4), (5, 4), (4, 0)) + bez((4, 0), (3, -3), (-3, -3), (-4, 0)), g, line)
        for tx_, ty_ in ((-4.6, 5.6), (-1.6, 7.6), (1.6, 7.6), (4.6, 5.6)):
            shape(ell(tx_, ty_, 1.5, 1.9, 10), g, line)


def paw_trail(x0, y0, x1, y1, n=5, s=1.0):
    ang = math.degrees(math.atan2(y1 - y0, x1 - x0)) - 90
    for i in range(n):
        t = i/(n - 1)
        off = 4*s*(1 if i % 2 else -1)
        nx, ny = -math.sin(math.radians(ang + 90)), math.cos(math.radians(ang + 90))
        paw_print(x0 + (x1 - x0)*t + nx*off, y0 + (y1 - y0)*t + ny*off, s, ang)


def needle(x, y, s=1.0, rot=0):
    with T(x, y, s, rot=rot):
        stroke([(-3, 0), (3, 0)], 0.9, g=P.SPRUCE)


def big_boots(x, y, s=1.0, needles=False, ribbon=False):
    """děda's felt winter boots standing in the hall, wet at the toes. needles and ribbon: what clings to them
    after a walk to the spruce (dark needles on the light felt cuffs and on the floor, so they show in grey)"""
    with T(x, y, s):
        for bx in (-13, 13):
            shp = [(bx - 9, 0), (bx + 13, 0), (bx + 13, 6), (bx + 5, 9), (bx + 4, 34), (bx - 8, 34), (bx - 9, 6)]
            form(shp, 0.45, w=LINE, sdx=1.2, sdy=0)
            shape([(bx - 10, 30), (bx + 5, 30), (bx + 5, 38), (bx - 10, 38)], 0.88, LINE*0.7)
            fill(ell(bx + 2, 1.5, 11, 2.4, 16), 0.3, 0.5)                                     # wet toes
        if needles:
            for nx, ny, a in ((-19, 34, 20), (-12, 35, -30), (-6, 33, 60), (10, 35, -10), (15, 33, 40), (-24, -2, 30),
                              (-30, 1, -20), (28, -1, 10), (34, 2, 70), (2, -3, -40)):
                needle(nx, ny, 1.1, a)
        if ribbon:
            stroke(bez((14, 36), (22, 30), (26, 24), (24, 14)), 2.2, g=P.RIBBON)
            stroke(bez((14, 36), (9, 30), (7, 27), (9, 20)), 2.2, g=P.RIBBON)

def ribbon_spool(x, y, s=1.0, full=False):
    """babička's spool of ribbon; almost empty, a few turns left"""
    with T(x, y, s):
        shape(ell(0, 0, 9, 3.5, 20), P.FEEDER, LINE*0.7)
        r_ = 8 if full else 4.5
        shape([(-r_, 0), (r_, 0), (r_, 10), (-r_, 10)], P.RIBBON, LINE*0.6)
        shape(ell(0, 10, 9, 3.5, 20), P.FEEDER, LINE*0.7)
        dot(0, 10, 1.6, 0.2)
        stroke(bez((r_, 4), (14, 2), (16, -4), (22, -3)), 1.6, g=P.RIBBON)


def piping_bag(x, y, s=1.0, rot=0):
    """an icing bag, white icing at the tip"""
    with T(x, y, s, rot=rot):
        shape([(-8, 22), (8, 22), (1.5, 0), (-1.5, 0)], 0.93, LINE*0.8)
        stroke([(-8.5, 22), (8.5, 22)], LINE*1.4)
        shape(ell(0, -1.5, 2, 2.4, 10), P.ICING, LINE*0.5)


def pillow_crumbs(x, y, w=60):
    """a pillow with dark (chocolate) crumbs on it"""
    shape(bez((x, y), (x - 6, y + 14), (x + w + 6, y + 16), (x + w, y)) + [(x, y)], 0.96, LINE)
    crumbs(x + w*0.55, y + 7, 22, 6, 8, P.CHOCOLATE, seed=5)


# ------------------------------------------------------------------ the star spruce
def star_spruce(x, y, s=1.0, stars=(), seed=3, snow=True):
    """the big spruce by the mill. stars: (fx, fy, pecked) in tree fractions, each a gingerbread star on a ribbon
    (pecked = only the ribbon and crumbs are left)"""
    with T(x, y, s):
        sh_([(-6, 0), (6, 0), (6, 18), (-6, 18)], P.BARK)
        for i in range(6):
            y0 = 14 + i*30; hw = 78 - i*12
            r = random.Random(seed + i)
            jag = [(-hw + 2*hw*k/8, y0 - (5 if k % 2 else 0) + r.uniform(-1, 1)) for k in range(9)]
            shape(jag + [(0, y0 + 64)], P.SPRUCE, LINE)
            for k in range(1, 8, 2):
                stroke([(jag[k][0]*0.9, jag[k][1] + 4), (jag[k][0]*0.55, y0 + 22)], 0.5, g=P.SPRUCE_LIGHT)
            if snow:
                for k in (0, 2, 4, 6, 8):
                    sx_, sy_ = jag[k]
                    if abs(sx_) < hw*0.2: continue
                    shape(bez((sx_ - 7, sy_ + 3), (sx_ - 4, sy_ + 8), (sx_ + 4, sy_ + 8), (sx_ + 7, sy_ + 3)) +
                          [(sx_ + 6, sy_ + 1), (sx_ - 6, sy_ + 1)], P.SNOW, LINE*0.5)
        for fx, fy, pecked in stars:
            sx, sy = fx*70, 30 + fy*170
            stroke([(sx, sy + 13), (sx, sy + 6)], 1.4, g=P.RIBBON)
            stroke(bez((sx, sy + 13), (sx - 4, sy + 16), (sx + 4, sy + 16), (sx, sy + 13)), 1.0, g=P.RIBBON)
            if pecked:
                stroke([(sx, sy + 6), (sx + 1, sy + 1)], 1.4, g=P.RIBBON)
                crumbs(sx, sy - 8, 12, 5, 5, P.GINGER, seed=int(sx*3))
            else:
                star_cookie(sx, sy, 0.62)

def club_photo7(x, y, w=150, h=100, rot=0):
    """this winter's photo of Klub Hvězdička: seven members in a row (děda, Franta, Věrka, Alica, Hanka, Tonda, Bětka).
    Readers count them on p. 2 and need the 7 on p. 15"""
    from style3 import alica, hanka
    from chars3 import deda, tonda
    from pond import verka_old, rybar
    from winter import betka
    with T(x, y, 1.0, rot=rot):
        shape([(0, 0), (w, 0), (w, h), (0, h)], P.PHOTO_FRAME, LINE)
        inner = [(5, 12), (w - 5, 12), (w - 5, h - 5), (5, h - 5)]
        fill(inner, P.SNOW_SKY)
        C.saveState(); C.clipPath(poly(inner), stroke=0, fill=0)
        fill([(5, 12), (w - 5, 12), (w - 5, h*0.38), (5, h*0.38)], P.SNOW)
        fs = (h - 22)/150
        figs = [(0.09, lambda X, Y: deda(X, Y, fs*0.95, mood="grin", shadow=False)),
                (0.22, lambda X, Y: rybar(X, Y, fs*0.9, mood="happy", shadow=False, hat=False, glasses=True, rod=False)),
                (0.35, lambda X, Y: verka_old(X, Y, fs*0.95, mood="happy", shadow=False, stick=False)),
                (0.5, lambda X, Y: alica(X, Y, fs*1.18, mood="grin", shadow=False)),
                (0.63, lambda X, Y: hanka(X, Y, fs*1.25, mood="grin", shadow=False)),
                (0.77, lambda X, Y: tonda(X, Y, fs*1.1, mood="grin", shadow=False)),
                (0.9, lambda X, Y: betka(X, Y, fs*1.35, mood="happy", shadow=False))]
        for fx, fn in figs: fn(w*fx, 13)
        C.restoreState()
        star(w - 12, h - 12, 5, P.TAG_STAR)
        stroke(inner, LINE*0.5, closed=True, g=0.4)
