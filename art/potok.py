"""Issue 13 (Stopy u potoka): Klub Hvězdička camps on Hvězdná louka by the Lišní potok. The meadow with the creek, the
stepping stones and the measuring rock (three water levels), the three tents, the campfire, the young willows, the
beaver's pencil stumps and chips, the drag slide, beaver / otter prints, the young beaver himself (sitting, swimming,
walking, slapping his tail), his dam with děda's walking stick in it, the wire mesh, the old footbridge, the Klub tin
with the castle drawing, Bětka's sketchbook drawings, the close-ups for the "who did it?" guide and the hidden frogs.

Animals face right with their feet at y = 0, like Joey. Prints are drawn toes up (+y)."""
import math, random
import lib
from lib import ell, bez, rrect, resample
from style3 import *
from style3 import C
import palette as P
from scenes3 import BG, s_, sh_, hills, cloud
from pond import far_trees, water, reeds, stump, treasure_tin, club_photo, badge
from village import frog, crayon
from joeyday import sausage
from chars3 import star
from letter import hand_text


def _panel_fill(p, g, alpha=None):
    fill([(p.x, p.y), (p.x + p.w, p.y), (p.x + p.w, p.y + p.h), (p.x, p.y + p.h)], g, alpha)


# ================================================================== the hidden-object game: 10 frogs
def hidden_zabka(x, y, r=12, rot=0):
    """one of the 10 frogs hidden in the issue: inside a white halo and a black line, so it reads on grass, water and
    mud alike. r = half its width"""
    k = r/13
    with T(x, y, 1.0, rot=rot):
        o = ell(0, 6*k, r*1.15, r*0.78, 30)
        stroke(o, LINE*4.4, closed=True, g=0.0, taper=False)
        stroke(o, LINE*2.8, closed=True, g=1.0, taper=False)
        fill(o, 1.0)
        frog(0, 0, k)


# ================================================================== the meadow and the creek
def night_tint(p, alpha=0.55):
    _panel_fill(p, P.NIGHT_MEADOW, alpha)


def night_stars(p, y0=0.6, n=24, seed=3):
    rd = random.Random(seed)
    for i in range(n):
        x = p.x + rd.uniform(6, p.w - 6); y = p.Y(rd.uniform(y0, 0.97))
        if i % 5 == 0: star(x, y, 2.6, 1.0, LINE*0.3)
        else: dot(x, y, rd.uniform(0.6, 1.1), 1.0)


def glow(x, y, r, alpha=0.14, n=4):
    """warm light round a fire or a torch: a few soft discs"""
    for i in range(n):
        rr = r*(1 - i/n)
        fill(ell(x, y, rr, rr*0.8, 30), P.LANTERN_GLOW, alpha)


def stone_top(x, y, rx, ry, under=0.0):
    """a flat creek stone seen from above the water; under = how much of it the water has covered (0..1)"""
    if under >= 0.95:
        fill(ell(x, y - ry*0.3, rx*0.95, ry*0.8, 20), P.CREEK_DEEP)
        for k in (1.15, 1.5):
            stroke(ell(x, y - ry*0.3, rx*k, ry*k, 24, 200, 340), BG*0.9, g=P.POND_RIPPLE)
        return
    h = ry*1.4*(1 - under)
    side = [(x - rx, y - ry*0.2)] + bez((x - rx, y - ry*0.2), (x - rx, y - ry*0.2 + h*0.4), (x + rx, y - ry*0.2 + h*0.4),
                                        (x + rx, y - ry*0.2), 10)[1:]
    shape(ell(x, y + h*0.4, rx, ry, 24), P.STONE, BG)
    for k in (1.12, 1.35):
        stroke(ell(x, y - ry*0.15, rx*k, ry*k*0.8, 24, 195, 345), BG*0.9, g=P.POND_RIPPLE)


def creek(p, y0, y1, seed=4, level=0):
    """the creek: a band across the panel between y0 (near bank) and y1 (far bank), a touch wider when the water
    rises. Returns the polygon"""
    rd = random.Random(seed)
    y1 = y1 + level*p.h*0.012
    y0 = y0 - level*p.h*0.012
    n = 12
    top = [(p.x - 5 + (p.w + 10)*i/n, y1 + 4*math.sin(i*1.7 + seed)) for i in range(n + 1)]
    bot = [(p.x - 5 + (p.w + 10)*i/n, y0 + 5*math.sin(i*1.3 + seed*2)) for i in range(n, -1, -1)]
    pts = top + bot
    fill(pts, P.CREEK)
    C.saveState(); C.clipPath(poly(pts), stroke=0, fill=0)
    for _ in range(int(p.w/40)):
        cx = rd.uniform(p.x, p.x + p.w); cy = rd.uniform(y0 + 3, y1 - 3); w_ = rd.uniform(10, 26)
        stroke([(cx - w_, cy), (cx - w_*0.3, cy + 1), (cx + w_*0.4, cy - 0.5), (cx + w_, cy)], BG*1.1, g=P.POND_RIPPLE)
    C.restoreState()
    stroke(top, BG); stroke(bot, BG)
    for i in range(0, n + 1, 3):   # a few reeds and pebbles on the banks
        bx = top[i][0] + rd.uniform(-10, 10)
        for k in range(3): stroke([(bx + k*3, top[i][1] - 1), (bx + k*3 + rd.uniform(-2, 2), top[i][1] + 7)], BG*0.6)
    return pts


def measuring_rock(x, y, s=1.0, level=0):
    """the tall rock in the creek Bětka draws each day; y = the creek's middle. level 0, 1, 2: less of it shows"""
    with T(x, y, s):
        wl = 4 + level*9
        rock = bez((-14, -2), (-17, 14), (-12, 30), (-4, 36)) + bez((-4, 36), (4, 40), (12, 32), (14, 18)) + \
               bez((14, 18), (16, 8), (15, 0), (12, -2))
        C.saveState(); C.clipPath(poly([(-40, wl), (40, wl), (40, 60), (-40, 60)]), stroke=0, fill=0)
        form(rock, P.STONE, w=BG*1.1, sdx=3, sdy=0)
        s_(bez((-6, 30), (-2, 22), (2, 16), (0, 8)), BG*0.6)
        C.restoreState()
        fill(ell(0, wl, 18, 3.4, 24), P.CREEK)
        stroke(ell(0, wl, 18, 3.4, 24, 195, 345), BG)
        for k in (1.3, 1.65):
            stroke(ell(0, wl - 1, 18*k, 3.4*k, 24, 200, 340), BG*0.9, g=P.POND_RIPPLE)


def louka(p, gy_f=0.5, seed=1, creek_=None, level=0, stones=None, rock_x=None, forest=True, clouds=True, night=False,
          sky_g=None):
    """Hvězdná louka in early summer: sky, the forest edge on the horizon, the meadow. creek_ = (y0, y1) panel
    fractions of the creek's near and far bank; stones = x fractions of the stepping stones across it (they go under
    as the level rises); rock_x = the measuring rock. Returns the horizon y"""
    gy = p.Y(gy_f)
    _panel_fill(p, P.NIGHT_MEADOW if night else (sky_g if sky_g is not None else P.SPRING_SKY))
    if night: night_stars(p, max(0.55, gy_f + 0.08), int(p.w/18), seed)
    elif clouds: cloud(p.X(0.25), p.Y(0.9), 0.6); cloud(p.X(0.8), p.Y(0.86), 0.45)
    hills(p, gy + p.h*0.05, 14, P.FAR_FIELD, seed)
    if forest: far_trees(p, gy - 2, seed, P.FOREST_DARK)
    fill([(p.x - 5, p.y - 5), (p.x - 5, gy), (p.x + p.w + 5, gy), (p.x + p.w + 5, p.y - 5)], P.EARLY_SUMMER_GRASS)
    s_([(p.x - 5, gy), (p.x + p.w + 5, gy)], BG)
    rd = random.Random(seed)
    for _ in range(max(1, int(p.w/160))):
        bx = p.x + rd.uniform(0.05, 0.95)*p.w
        with T(bx, gy - 3, rd.uniform(0.5, 0.8)):
            shape(bez((-26, 0), (-32, 24), (-8, 34), (0, 28)) + bez((0, 28), (10, 36), (32, 26), (26, 0)), P.FOREST_DARK, BG)
    for _ in range(int(p.w/18)):
        xx = p.x + rd.uniform(0, p.w); yy = rd.uniform(p.y + 4, gy - 6)
        for k in (-2, 0, 2): stroke([(xx + k, yy), (xx + k*1.6, yy + 4)], BG*0.5, g=0.4)
        if rd.random() < 0.25: dot(xx + 3, yy + 6, 1.4, 1.0 if rd.random() < 0.6 else P.FORSYTHIA)
    if creek_:
        y0, y1 = p.Y(creek_[0]), p.Y(creek_[1])
        creek(p, y0, y1, seed + 3, level)
        if stones:
            n = len(stones)
            for i, fx in enumerate(stones):
                t = (i + 0.5)/n
                stone_top(p.X(fx), y0 + (y1 - y0)*t, 11 - 2*t, 3.4 - t, [0, 0.55, 1.0][level])
        if rock_x is not None:
            measuring_rock(p.X(rock_x), (y0 + y1)/2, 0.8, level)
    if night: night_tint(p, 0.35)
    return gy


# ================================================================== the camp
def stan(x, y, s=1.0, kind="dome", g=None, door="closed", flip=False):
    """a tent, (x, y) = bottom centre. kind: dome (the family's, ~120 wide), small (Tonda and Bětka's, orange),
    old (děda's canvas ridge tent from the Klub days, seen three-quarter). door: closed, open, glow"""
    with T(x, y, s, flip):
        if kind in ("dome", "small"):
            g = g if g is not None else (P.TENT_GREEN if kind == "dome" else P.TENT_ORANGE)
            w, h = (60, 64) if kind == "dome" else (44, 46)
            for sx in (-1, 1):
                stroke([(sx*w*0.7, h*0.35), (sx*w*1.25, 0)], LINE*0.6, g=P.GUY_ROPE)
                stroke([(sx*w*1.25 - 1.5, 3), (sx*w*1.25 + 1.5, -2)], LINE*1.2)
            body = bez((-w, 0), (-w*0.95, h*1.25), (w*0.95, h*1.25), (w, 0), 20)
            form(body, g, sdx=3, sdy=0, sh=0.12)
            for k in (-0.5, 0.5):
                stroke(bez((-w*0.98, 0), (-w*0.4 + k*w*0.3, h*1.3), (w*0.4 + k*w*0.3, h*1.3), (w*0.98, 0)), LINE*0.8, g=0.3)
            dw, dh = w*0.42, h*0.7
            door_pts = bez((-dw, 0), (-dw*0.9, dh*1.25), (dw*0.9, dh*1.25), (dw, 0), 16)
            if door == "closed":
                fill(door_pts, g); stroke(door_pts, LINE*0.8, g=0.15)
                stroke([(0, 1), (0, dh*0.9)], LINE*0.6, g=0.2)
            else:
                shape(door_pts, P.TENT_GLOW if door == "glow" else P.TENT_DOOR, LINE*0.9)
                for sx in (-1, 1):   # the flap rolled back
                    shape(ell(sx*dw*1.05, dh*0.55, 4, 10, 16, rot=sx*-15), g, LINE*0.7)
        else:
            g = g if g is not None else P.TENT_CANVAS
            side = [(0, 62), (78, 68), (112, 4), (40, 0)]
            for (a, b) in (((0, 62), (-30, 0)), ((78, 68), (128, 30)), ((112, 4), (130, 0))):
                stroke([a, b], LINE*0.6, g=P.GUY_ROPE)
            form(side, g, sdx=0, sdy=0, sh=0.16)
            fill(side, 0.0, 0.1)
            stroke(side, LINE, closed=True)
            for k in (0.3, 0.6):
                stroke([(k*78, 62 + k*6), (40 + k*72, k*4)], LINE*0.5, g=0.45)
            front = [(-40, 0), (40, 0), (0, 62)]
            form(front, g, sdx=2, sdy=0, sh=0.1)
            hole = [(-18, 0), (18, 0), (0, 40)]
            shape(hole, P.TENT_GLOW if door == "glow" else P.TENT_DOOR, LINE*0.8)
            if door != "closed":
                for sx in (-1, 1):
                    shape([(sx*18, 0), (sx*30, 2), (sx*10, 36), (sx*4, 30)], g, LINE*0.7)
                    shape(ell(sx*20, 18, 3, 3, 10), 0.6, LINE*0.5)
            else:
                shape([(-18, 0), (18, 0), (0, 40)], g, LINE*0.7)
                stroke([(0, 1), (0, 38)], LINE*0.6, g=0.3)
            tube([(0, 0), (0, 70)], 2.4, 2.2, P.FIREWOOD, sh=0)
            star(0, 54, 4.5, P.TAG_STAR)   # the Klub star on the gable, sewn on fifty years ago


def taborak(x, y, s=1.0, lit=True, burty=False, seed=2):
    """the campfire: a ring of stones, crossed logs and (lit) flames; (x, y) = its middle on the ground"""
    rd = random.Random(seed)
    with T(x, y, s):
        if lit:
            glow(0, 10, 60, 0.12)
        for i in range(10):
            a = math.tau*i/10
            sx, sy = math.cos(a)*24, math.sin(a)*6
            if sy > 0: shape(ell(sx, sy + 2, 5.5, 4, 14), P.FIRE_STONE, LINE*0.8)
        fill(ell(0, 0, 21, 5, 24), 0.25 if lit else 0.7)
        for a in (-35, 35, -10, 15):
            with T(0, 0, 1.0, rot=a):
                tube([(-2, -2), (0, 22)], 4.2, 3.4, P.FIREWOOD, sh=0)
        if lit:
            out = bez((-14, 0), (-16, 14), (-6, 22), (-4, 34)) + bez((-4, 34), (0, 26), (4, 30), (6, 40)) + \
                  bez((6, 40), (10, 28), (16, 20), (14, 0))
            shape(out, P.FIRE_RED, LINE*0.9)
            inner = bez((-8, 0), (-9, 10), (-2, 14), (0, 24)) + bez((0, 24), (3, 16), (8, 12), (8, 0))
            fill(inner, P.FLAME)
            for _ in range(6):
                dot(rd.uniform(-14, 14), rd.uniform(40, 62), rd.uniform(0.7, 1.3), P.FLAME)
        else:
            for _ in range(5): dot(rd.uniform(-14, 14), rd.uniform(-2, 3), 1.2, 0.4)
            for k in range(3):
                stroke(bez((k*4 - 4, 10), (k*4 - 8, 20), (k*4, 26), (k*4 - 4, 36)), LINE*0.7, g=0.65)
        for i in range(10):
            a = math.tau*i/10
            sx, sy = math.cos(a)*24, math.sin(a)*6
            if sy <= 0: shape(ell(sx, sy + 2, 5.5, 4, 14), P.FIRE_STONE, LINE*0.8)
        if burty:
            for sx in (-1, 1):
                stroke([(sx*44, -2), (sx*12, 30)], LINE*2.4); stroke([(sx*44, -2), (sx*12, 30)], LINE*1.2, g=P.FIREWOOD)
                sausage(sx*14, 31, 0.6, math.degrees(math.atan2(34, -sx*58)))


def opekacka(x, y, s=1.0, rot=40):
    """a roasting stick with a buřt on its end; (x, y) = where a hand holds it"""
    with T(x, y, s, rot=rot):
        stroke([(-6, 0), (50, 0)], LINE*2.6); stroke([(-6, 0), (50, 0)], LINE*1.4, g=P.FIREWOOD)
        sausage(56, 0, 0.75)


def polena(x, y, s=1.0, n=5):
    """táta's firewood: logs with flat, straight saw cuts"""
    with T(x, y, s):
        for i in range(n):
            lx = (i % 3)*15 - 15 + (i//3)*7; ly = (i//3)*12
            shape(rrect(lx - 26, ly, 34, 11, 4), P.FIREWOOD, LINE*0.8)
            shape(ell(lx + 8, ly + 5.5, 5.5, 5.5, 18), P.LOG_END, LINE*0.8)
            stroke(ell(lx + 8, ly + 5.5, 2.6, 2.6, 14), LINE*0.4, closed=True, g=0.5)


def pila(x, y, s=1.0, rot=0):
    """táta's new folding saw: a curved blade with fine teeth and a rubber handle (local length ~60)"""
    with T(x, y, s, rot=rot):
        shape(rrect(-26, -4, 26, 8, 3.5), P.TENT_ORANGE, LINE*0.9)
        blade = bez((0, -3), (14, -5), (28, -4), (38, 1)) + bez((38, 1), (30, 3), (14, 4), (0, 3))
        shape(blade, P.SAW_BLADE, LINE*0.8)
        for k in range(0, 36, 3):
            t = k/38
            stroke([(k, -3.4 - 1.5*math.sin(t*3)), (k + 1.5, -5.4 - 1.5*math.sin(t*3))], LINE*0.4)
        dot(-2, 0, 1.2, 0.3)


# ================================================================== willows, stumps, chips
def vrbka(x, y, s=1.0, seed=3, cut=False):
    """a young willow (local height ~110): two or three slim stems and a narrow leafy crown. cut: drawn lying, its
    trunk end gnawed to a cone (see padla_vrbka)"""
    rd = random.Random(seed)
    with T(x, y, s):
        stems = [(-3, 0, -6, 70), (2, 0, 6, 76)] if seed % 2 else [(0, 0, -2, 80), (2, 0, 8, 64), (-2, 0, -9, 60)]
        for x0, y0, x1, y1 in stems:
            tube(bez((x0, y0), (x0, (y0 + y1)*0.4), (x1, (y0 + y1)*0.6), (x1, y1)), 4.4, 2.4, P.BARK, sh=0)
        ph = rd.uniform(0, 6)
        crown = [(math.cos(a)*22*(1 + 0.07*math.sin(a*5 + ph)), 80 + math.sin(a)*33*(1 + 0.07*math.sin(a*5 + ph)))
                 for a in [math.tau*i/48 for i in range(48)]]
        fill(crown, P.WILLOW); offset_shadow(crown, 4, 4, 0.1); stroke(crown, BG, closed=True)
        for i in range(34):
            lx, ly = rd.uniform(-19, 19), rd.uniform(52, 108)
            if ((lx/22)**2 + ((ly - 80)/32)**2) > 0.9: continue
            with T(lx, ly, 1.0, rot=rd.uniform(-60, -120)):
                stroke([(-3, 0), (3, 0)], LINE*0.7, g=P.WILLOW_DARK)


def _cone(w, h, g=P.WOOD_PALE):
    """the gnawed point of a beaver-cut trunk: a cone of pale wood with gouge marks, base on y = 0, width w"""
    pts = [(-w/2, 0), (-w*0.12, h*0.95), (w*0.06, h), (w/2, 0)]
    shape(pts, g, LINE*0.8)
    for k in range(5):
        t = (k + 0.5)/5
        stroke(bez((-w/2*(1 - t) - 1, h*t*0.9), (-w*0.1, h*t*0.9 + 2), (w*0.1, h*t*0.9 + 1), (w/2*(1 - t) + 1, h*t*0.9)),
               LINE*0.4, g=P.CHIPS)


def pahyl(x, y, s=1.0, h=30):
    """the beaver's pencil stump: a knee-high stub, gnawed all round to a point (local width 16, height ~h)"""
    with T(x, y, s):
        stub_h = h*0.45
        side = [(-8, 0), (8, 0), (7.5, stub_h), (-7.5, stub_h)]
        form(side, P.BARK, w=BG, sdx=2, sdy=0)
        s_(bez((-3, 2), (-2, stub_h*0.4), (-3, stub_h*0.7), (-2, stub_h - 1)), BG*0.5)
        with T(0, stub_h, 1.0):
            _cone(15, h - stub_h)
        for sx in (-1, 1):
            stroke(bez((sx*8, 2), (sx*12, 0), (sx*15, -1), (sx*18, -1)), BG*2.0)


def padla_vrbka(x, y, s=1.0, flip=False, seed=3):
    """the felled willow lying on the grass: its gnawed cone end at (x, y), crown towards +x"""
    with T(x, y, s, flip):
        with T(0, 4, 1.0, rot=-88):
            C.saveState(); C.clipPath(poly([(-60, 10), (60, 10), (60, 160), (-60, 160)]), stroke=0, fill=0)
            vrbka(0, 0, 1.0, seed)
            C.restoreState()
            with T(0, 10, 1.0, rot=180):
                _cone(8, 9)


def tresky(x, y, w=40, n=14, seed=2, s=1.0):
    """the beaver's chips round a stump: thick, short, curved chips the size of a fingernail"""
    rd = random.Random(seed)
    for i in range(n):
        cx = x + rd.uniform(-w/2, w/2); cy = y + rd.uniform(-4, 4)*s
        with T(cx, cy, s, rot=rd.uniform(0, 360)):
            chip = bez((-3.6, -1), (-2, 1.6), (2, 1.8), (3.6, -0.4)) + bez((3.6, -0.4), (2, 0.2), (-2, 0.2), (-3.6, -1))
            shape(chip, P.CHIPS, LINE*0.5)


def kudrlinky(x, y, s=1.0, n=4, seed=1):
    """Hanka's knife shavings: long, thin, curly strips"""
    rd = random.Random(seed)
    with T(x, y, s):
        for i in range(n):
            cx, cy = rd.uniform(-12, 12), rd.uniform(-2, 4)
            L = rd.uniform(16, 24)
            pts = [(cx - L/2 + t*L/40, cy + math.sin(t*0.6)*2.4) for t in range(41)]
            stroke(pts, LINE*1.8, g=0.0); stroke(pts, LINE*0.9, g=P.STICK)


def pletivo(x, y, w=22, h=30):
    """wire mesh wrapped round a trunk's foot; (x, y) = bottom centre"""
    pts = [(x - w/2, y), (x + w/2, y), (x + w/2, y + h), (x - w/2, y + h)]
    C.saveState(); C.clipPath(poly(pts), stroke=0, fill=0)
    for k in range(-int(h), int(w) + int(h), 6):
        stroke([(x - w/2 + k, y), (x - w/2 + k + h, y + h)], LINE*0.35, g=P.MESH)
        stroke([(x - w/2 + k, y + h), (x - w/2 + k + h, y)], LINE*0.35, g=P.MESH)
    C.restoreState()
    for yy in (y + 1, y + h):
        stroke(bez((x - w/2, yy), (x - w/4, yy - 2), (x + w/4, yy - 2), (x + w/2, yy)), LINE*0.8, g=P.MESH)
    stroke([(x - w/2, y), (x - w/2, y + h)], LINE*0.6, g=P.MESH); stroke([(x + w/2, y), (x + w/2, y + h)], LINE*0.6, g=P.MESH)


def deda_hul(x, y, s=1.0, rot=0, peeled=False, length=92):
    """děda's hazel walking stick with a crook and a carved Klub star; peeled: the beaver ate the bark off, it is pale
    and gnawed, the star still shows. (x, y) = its foot"""
    with T(x, y, s, rot=rot):
        g = P.WOOD_PALE if peeled else P.WALKING_STICK
        tube([(0, 0), (0, length)], 3.4, 3.2, g, sh=0)
        stroke(bez((0, length), (0, length + 9), (10, length + 11), (11, length + 3)), LINE*3.4)
        stroke(bez((0, length), (0, length + 9), (10, length + 11), (11, length + 3)), LINE*2.0, g=g)
        star(0, length*0.72, 2.6, P.TAG_STAR if not peeled else P.CHIPS, LINE*0.4)
        if peeled:
            for k in range(6):
                yy = 8 + k*length/7
                stroke([(-1.6, yy), (1.6, yy + 1.4)], LINE*0.4, g=P.CHIPS)
        else:
            for yy in (length*0.3, length*0.55):
                dot(1, yy, 0.9, 0.25)


# ================================================================== tracks and signs
def bobr_print(x, y, s=1.0, rot=0, g=None, ink=False):
    """beaver hind foot: big and broad like a duck's flipper, five long spread toes joined by webbing, a short heel
    (local length ~20, width ~22)"""
    g = (P.TRACK_INK if ink else P.MUD_DARK) if g is None else g
    with T(x, y, s, rot=rot):
        bases, tips = [], []
        for i, a in enumerate((52, 26, 0, -26, -52)):
            ra = math.radians(90 + a)
            L = 10 if i in (1, 2, 3) else 8.5
            bx, by = (i - 2)*2.6, 2.5 - abs(i - 2)*0.6
            bases.append((bx, by)); tips.append((bx + math.cos(ra)*L, by + math.sin(ra)*L))
        web = [bases[0], tips[0]]
        for i in range(4):
            (ax, ay), (bx, by) = tips[i], tips[i + 1]
            mx, my = (bases[i][0] + bases[i + 1][0])/2, (bases[i][1] + bases[i + 1][1])/2
            web += [(mx + ((ax + bx)/2 - mx)*0.55, my + ((ay + by)/2 - my)*0.55), (bx, by)]
        web += [bases[4]]
        fill(web, g, 0.4)
        stroke(web, LINE*0.45, closed=True, g=g)
        sole = bez((-5.6, 2.4), (-5.6, -2), (-2.4, -6), (0, -6)) + bez((0, -6), (2.4, -6), (5.6, -2), (5.6, 2.4))
        fill(sole, g)
        for (bx, by), (tx, ty) in zip(bases, tips):
            stroke([(bx, by), (tx, ty)], LINE*2.2, g=g, taper=False)
            fill(ell(tx, ty, 1.3, 1.3, 10), g)


def bobr_front(x, y, s=1.0, rot=0, g=None, ink=False):
    """beaver front paw: small, like a little hand with five thin fingers"""
    g = (P.TRACK_INK if ink else P.MUD_DARK) if g is None else g
    with T(x, y, s, rot=rot):
        fill(ell(0, 0, 3, 2.6, 14), g)
        for a in (-60, -30, 0, 30, 60):
            ra = math.radians(90 + a)
            stroke([(math.cos(ra)*2, math.sin(ra)*2), (math.cos(ra)*6, math.sin(ra)*6 + 1)], LINE*1.0, g=g)


def vydra_print(x, y, s=1.0, rot=0, g=None, ink=False):
    """otter: a small round print, a round pad and five round toes in an arc (local width ~10)"""
    g = (P.TRACK_INK if ink else P.MUD_DARK) if g is None else g
    with T(x, y, s, rot=rot):
        fill(bez((-3.6, 0), (-4.4, 3.4), (4.4, 3.4), (3.6, 0)) + bez((3.6, 0), (3, -3.4), (-3, -3.4), (-3.6, 0)), g)
        for a in (-62, -30, 0, 30, 62):
            ra = math.radians(90 + a)
            fill(ell(math.cos(ra)*6.2, 1.2 + math.sin(ra)*5.6, 1.4, 1.6, 10), g)


def ocas_smouha(pts, w=9, g=None):
    """the smear a dragged beaver tail leaves between its prints"""
    g = P.DRAG_MUD if g is None else g
    stroke(pts, w*1.2, g=P.MUD_DARK, alpha=0.35)
    stroke(pts, w, g=g, alpha=0.7)


def bobr_trail(pts, s=1.0, n=None, g=None, ink=False, tail=True):
    """beaver tracks along pts (page coordinates): hind and front prints left and right, the tail smear between"""
    if tail: ocas_smouha(pts, 7*s)
    path = []
    for i in range(len(pts) - 1):
        (x0, y0), (x1, y1) = pts[i], pts[i + 1]
        path += [(x0 + (x1 - x0)*t/20, y0 + (y1 - y0)*t/20) for t in range(20)]
    path.append(pts[-1])
    path = resample(path, 1.0)
    d = 0; d_next = 4*s; k = 0
    for i in range(1, len(path)):
        d += math.hypot(path[i][0] - path[i - 1][0], path[i][1] - path[i - 1][1])
        if d < d_next: continue
        if n is not None and k >= n: break
        a = math.atan2(path[i][1] - path[i - 1][1], path[i][0] - path[i - 1][0])
        nx, ny = -math.sin(a), math.cos(a)
        side = 1 if k % 2 else -1
        bx, by = path[i][0] + nx*side*9*s, path[i][1] + ny*side*9*s
        bobr_print(bx, by, s*0.8, math.degrees(a) - 90, g=g, ink=ink)
        bobr_front(bx + math.cos(a)*14*s, by + math.sin(a)*14*s, s*0.8, math.degrees(a) - 90, g=g, ink=ink)
        k += 1; d_next = d + 30*s


def drag_slide(pts, w=24, seed=3):
    """the smooth muddy slide where branches were dragged down to the water: a trodden, shiny strip of mud with soft
    edges, leaves and bits of twig pressed flat into it"""
    rd = random.Random(seed)
    path = resample(pts, 3.0)
    n = len(path)
    path = [(x + math.sin(i*0.35)*w*0.18, y) for i, (x, y) in enumerate(path)]
    for i, (x, y) in enumerate(path):
        ww = w*(0.55 - 0.2*i/n)*(1 + 0.25*math.sin(i*0.7 + seed))
        fill(ell(x + rd.uniform(-1.5, 1.5), y, ww, ww*0.55, 18), P.MUD_DARK, 0.25)
    for i, (x, y) in enumerate(path):
        ww = w*(0.45 - 0.16*i/n)
        fill(ell(x, y, ww, ww*0.5, 18), P.DRAG_MUD, 0.8)
    for i in range(0, n, max(1, n//7)):
        x, y = path[i]
        with T(x + rd.uniform(-w*0.25, w*0.25), y + rd.uniform(-w*0.1, w*0.1), 1.0, rot=rd.uniform(0, 360)):
            shape(ell(0, 0, 1.8, 4.6, 10), P.WILLOW_DARK, LINE*0.4)
    for i in range(2):
        x, y = path[int(n*(i + 0.4)/2)]
        stroke([(x - 7, y - 1.5), (x + 7, y + 1.5)], LINE*0.9, g=P.BARK)


# ================================================================== close-ups for the guide and the lupa
def zuby_closeup(x, y, s=1.0):
    """gnawed wood seen through the lupa: pairs of wide, flat grooves side by side (two big front teeth)"""
    with T(x, y, s):
        fill([(-60, -50), (60, -50), (60, 50), (-60, 50)], P.WOOD_PALE)
        for row in range(4):
            yy = -36 + row*24
            for col in range(3):
                xx = -40 + col*36 + (row % 2)*14
                for sx in (-1, 1):   # one tooth-mark pair: two scoops with a ridge between
                    gx = xx + sx*6
                    shape(rrect(gx - 5, yy - 9, 10, 18, 4.5), P.CHIPS, LINE*0.6)
                    stroke([(gx - 2.5, yy - 6), (gx - 2.5, yy + 6)], LINE*0.4, g=0.55)
                stroke([(xx, yy - 8), (xx, yy + 8)], LINE*0.9, g=0.4)


def saw_closeup(x, y, s=1.0):
    """a saw cut: flat and smooth, the year rings and fine straight scratches"""
    with T(x, y, s):
        shape(ell(0, 0, 30, 24, 40), P.LOG_END, LINE)
        for r in (22, 15, 8, 3):
            stroke(ell(0.5, 0.3, r*1.2, r, 30), LINE*0.4, closed=True, g=0.5)
        for k in range(-24, 25, 5):
            stroke([(k - 6, -14), (k + 6, 14)], LINE*0.25, g=0.6)
        stroke(ell(0, 0, 33, 27, 40), LINE*2.6, closed=True, g=P.BARK)


def dog_bite(x, y, s=1.0, rot=0):
    """a stick Joey chewed: wet, frayed, little round tooth holes"""
    with T(x, y, s, rot=rot):
        tube([(-30, 0), (26, 0)], 7, 6.4, P.BARK, sh=0)
        for tx in (-12, -4, 6, 14):
            for sy in (-1, 1):
                fill(ell(tx, sy*1.8, 1.2, 1.1, 10), 0.15)
        shape([(26, -3.2), (26, 3.2), (29, 2.4), (28, 0.6), (31, 0.4), (28.6, -1.4), (30, -2.6)], P.TRAP_WOOD, LINE*0.6)


# ================================================================== the beaver
def bobr(x, y, s=1.0, flip=False, pose="sit", branch=False, mood="open", wet=False):
    """Hryzálek, the young beaver, facing right (sitting ~50 high, ~70 long with his tail).
    pose: sit (upright, front paws at his chest holding a stick, eating the bark like corn on the cob),
    walk (on all fours, tail dragging), swim (head and back above the water line y = 0, a V wake behind; branch: a
    willow branch in his mouth), slap (diving: the back arching under, the tail raised to slap the water)"""
    with T(x, y, s, flip):
        if pose == "sit":
            tail = rrect(-40, -1, 34, 11, 5.5)
            with T(-6, 2, 1.0, rot=-6):
                shape([(px, py - 3) for px, py in tail], P.BEAVER_TAIL, LINE)
                hatch([(px, py - 3) for px, py in tail], 3.2, 45, 0.4, 0.75, 0.7)
                hatch([(px, py - 3) for px, py in tail], 3.2, -45, 0.4, 0.75, 0.7)
            body = bez((-18, 2), (-28, 18), (-16, 42), (0, 44)) + bez((0, 44), (12, 45), (20, 32), (18, 16)) + \
                   bez((18, 16), (20, 6), (12, 0), (0, 0)) + [(-18, 2)]
            form(notch(body, 0.8, 4), P.BEAVER, sdx=-3, sdy=0, sh=0.14)
            shape(ell(4, 2, 12, 4, 20), P.BEAVER_DARK, LINE*0.9)            # the big hind foot
            for k in range(4): stroke([(10 + k*2, 0.5), (13 + k*2.4, 0)], LINE*0.4, g=0.7)
            hx, hy = 8, 44
            if branch:
                with T(14, 32, 1.0, rot=-8):
                    tube([(-16, 0), (16, 0)], 5, 5, P.WOOD_PALE, sh=0)
                    for bx in (-12, -4, 9): fill(rrect(bx, -2.5, 4, 5, 1.5), P.BARK)
            for sx in (-2, 4):   # front paws round the stick
                shape(ell(14 + sx, 31, 3.4, 3, 12), P.BEAVER_DARK, LINE*0.6)
        elif pose == "walk":
            tail = rrect(-62, 1, 30, 9, 4.5)
            shape(tail, P.BEAVER_TAIL, LINE)
            hatch(tail, 3.2, 45, 0.4, 0.75, 0.7)
            for lx in (-14, 12):
                tube([(lx, 10), (lx - 1, 1)], 6, 5, P.BEAVER_DARK, sh=0)
            body = bez((-34, 6), (-38, 26), (-6, 34), (12, 30)) + bez((12, 30), (24, 27), (28, 18), (26, 10)) + \
                   bez((26, 10), (16, 4), (-10, 4), (-30, 4)) + [(-34, 6)]
            form(notch(body, 0.8, 4), P.BEAVER, sdx=-2, sdy=1.2)
            for lx in (-20, 8):
                tube([(lx, 12), (lx + 1, 1)], 7, 6, P.BEAVER_DARK, sh=0)
            hx, hy = 30, 24
        elif pose == "swim":
            for k in (1, 2, 3):   # the V wake
                stroke(bez((-4 - k*12, -1 - k*1.6), (-k*6, 0), (4, 1), (10, 1)), LINE*0.9, g=P.POND_RIPPLE)
                stroke(bez((-4 - k*12, 2 + k*1.6), (-k*6, 1), (4, 0), (10, 0)), LINE*0.6, g=0.3)
            back = bez((-30, 0), (-24, 7), (-8, 8), (4, 4)) + [(4, 0)]
            form(back, P.BEAVER, sdx=0, sdy=0, sh=0.1)
            hx, hy = 10, 4
            if branch:
                with T(22, 2, 1.0, rot=-14):
                    tube([(-62, 0), (4, 0)], 3.4, 2.4, P.BARK, sh=0)
                    rd = random.Random(7)
                    for i in range(16):
                        bx = -60 + i*4
                        side = 1 if i % 2 else -1
                        with T(bx, side*2.4, 1.0, rot=side*(40 + rd.uniform(-10, 10)) + 180):
                            shape(ell(-4.5, 0, 5, 1.5, 12), P.WILLOW_DARK if i % 3 else P.WILLOW, LINE*0.4)
        else:   # slap
            back = bez((-6, 0), (-4, 10), (8, 14), (16, 6)) + [(18, 0)]
            form(back, P.BEAVER, sdx=0, sdy=0, sh=0.1)
            with T(-8, 2, 1.0, rot=-58):
                tail = rrect(-36, -5, 34, 11, 5.5)
                shape(tail, P.BEAVER_TAIL, LINE)
                hatch(tail, 3.2, 45, 0.4, 0.75, 0.7)
            rd = random.Random(4)
            for i in range(14):
                a = math.radians(rd.uniform(20, 160)); d = rd.uniform(16, 40)
                dx, dy = -26 + math.cos(a)*d, 4 + math.sin(a)*d
                fill(ell(dx, dy, 1.5, 2.2, 10), P.POND_WATER); stroke(ell(dx, dy, 1.5, 2.2, 10), 0.7, closed=True)
            for k in (1.0, 1.6, 2.2):
                stroke(ell(-26, 0, 16*k, 3*k, 24), BG, closed=True, g=P.POND_RIPPLE)
            return
        # the head (local frame at hx, hy)
        with T(hx, hy, 1.0):
            head = bez((-10, 0), (-11, 10), (-2, 14), (6, 12)) + bez((6, 12), (12, 10), (16, 6), (17, 2)) + \
                   bez((17, 2), (17, -3), (12, -6), (4, -6)) + bez((4, -6), (-6, -6), (-10, -4), (-10, 0))
            if pose == "swim":
                C.saveState(); C.clipPath(poly([(-40, -hy), (40, -hy), (40, 40), (-40, 40)]), stroke=0, fill=0)
            form(notch(head, 0.6, 4), P.BEAVER, sdx=-1.4, sdy=1)
            shape(ell(-6, 12.5, 2.8, 2.4, 12), P.BEAVER_DARK, LINE*0.7)   # the small round ear
            shape(ell(15.5, 3, 3, 2.6, 12), 0.1, LINE*0.6)                 # the nose
            dot(16.4, 3.8, 0.5, 0.8)
            if mood == "sleepy":
                stroke([(5, 6.5), (8.4, 6.5)], LINE*0.8)
            else:
                dot(6.8, 6.6, 1.6, 0.0); dot(7.3, 7.2, 0.5, 1.0)
            for k in (0.5, 1.5, 2.5): stroke([(15 - k*2, -0.5), (19, -1.6 + k*1.2)], LINE*0.3, g=0.6)   # whiskers
            if pose != "swim":
                shape(rrect(11.6, -9.6, 2.6, 6, 0.8), P.BEAVER_TEETH, LINE*0.5)
                shape(rrect(14.2, -9.6, 2.6, 6, 0.8), P.BEAVER_TEETH, LINE*0.5)
            if pose == "swim":
                C.restoreState()
                stroke(ell(4, 0, 18, 2.6, 24, 200, 340), BG, g=P.POND_RIPPLE)
        if wet:
            for k in range(3): fill(ell(-10 + k*12, -3, 1.2, 1.8, 10), P.POND_WATER)


def eyeshine(x, y, s=1.0):
    """two little eyes shining in the torch light on the dark water"""
    for sx in (-1, 1):
        fill(ell(x + sx*4*s, y, 2.4*s, 1.6*s, 12), P.TENT_GLOW)
        dot(x + sx*4*s, y, 0.8*s, 1.0)
    for k in (1.0, 1.6):
        stroke(ell(x, y - 4*s, 16*s*k, 2.4*s*k, 24), BG*0.8, closed=True, g=P.POND_RIPPLE)


def plesk(x, y, s=1.0, seed=3):
    """a tail slap on dark water: rings and a crown of drops"""
    rd = random.Random(seed)
    with T(x, y, s):
        for k in (1.0, 1.6, 2.3):
            stroke(ell(0, 0, 14*k, 3*k, 24), BG, closed=True, g=P.POND_RIPPLE)
        for i in range(12):
            a = math.radians(rd.uniform(25, 155)); d = rd.uniform(12, 30)
            fill(ell(math.cos(a)*d, 4 + math.sin(a)*d, 1.4, 2, 10), P.POND_RIPPLE)


# ================================================================== the dam and the pond above it
def hraz(x0, x1, y, h=30, seed=5, stick_at=None):
    """the beaver's dam across the creek, x0..x1 at y (its foot on the downstream side): mud and stones, a tangle of
    branches, some peeled white; stick_at = x of děda's walking stick woven in. Returns the top y"""
    rd = random.Random(seed)
    w = x1 - x0
    mound = [(x0, y)] + bez((x0, y), (x0 + w*0.1, y + h*1.1), (x1 - w*0.1, y + h*1.15), (x1, y), 20)[1:]
    form(mound, P.MUD, sdx=0, sdy=-3, sh=0.14)
    for i in range(int(w/7)):
        bx = x0 + rd.uniform(w*0.04, w*0.96)
        t = (bx - x0)/w
        top = y + h*(1 - (2*t - 1)**2)*0.95
        by = rd.uniform(y + 2, top - 2)
        a = rd.uniform(-35, 35) + (180 if rd.random() < 0.5 else 0)
        L = rd.uniform(18, 34)
        ra = math.radians(a)
        pts = [(bx - math.cos(ra)*L/2, by - math.sin(ra)*L/2), (bx + math.cos(ra)*L/2, by + math.sin(ra)*L/2)]
        peeled = rd.random() < 0.3
        stroke(pts, LINE*3.2)
        stroke(pts, LINE*2.0, g=P.WOOD_PALE if peeled else P.BARK)
    for i in range(int(w/26)):
        shape(ell(x0 + rd.uniform(w*0.08, w*0.92), y + rd.uniform(0, 4), rd.uniform(4, 7), 3.4, 14), P.STONE, LINE*0.7)
    if stick_at is not None:
        t = (stick_at - x0)/w
        deda_hul(stick_at - 40, y + h*0.45 + 4, 0.9, -78, peeled=True)
    return y + h


def lavka(x0, x1, y, s=1.0):
    """the old wooden footbridge over the creek: two logs and grey planks across"""
    for dy in (0, 6*s):
        tube([(x0, y + dy), (x1, y + dy)], 6*s, 6*s, P.BARK, sh=0)
    for k in range(int((x1 - x0)/(9*s))):
        xx = x0 + 4*s + k*9*s
        shape([(xx, y + 3*s), (xx + 7.5*s, y + 3*s), (xx + 7.5*s, y + 11*s), (xx, y + 11*s)], 0.72, LINE*0.6)
    for xx in (x0 + 6*s, x1 - 6*s):
        tube([(xx, y), (xx, y - 18*s)], 5*s, 5*s, P.BARK, sh=0)


def hrad_kresba(x, y, w=70, h=86, rot=0, torn=True):
    """the drawing from the Klub tin: a castle tower with a star flag and XIV under it, the bottom torn off
    ("Další poklad je na…"). (x, y) = bottom left"""
    rd = random.Random(14)
    with T(x, y, 1.0, rot=rot):
        bot = [(w - k*w/10, rd.uniform(-3, 3)) for k in range(11)] if torn else [(w, 0), (0, 0)]
        paper = [(0, h)] + [(w, h)] + bot
        shape(paper, P.LETTER_PAPER, LINE*0.8)
        ink = 0.25
        tx0, tx1 = w*0.34, w*0.66
        stroke([(tx0, h*0.3), (tx0, h*0.72), (tx1, h*0.72), (tx1, h*0.3)], LINE*0.9, g=ink)
        for k in range(4):
            cx = tx0 + (tx1 - tx0)*k/3
            stroke([(cx - 2.5, h*0.72), (cx - 2.5, h*0.77), (cx + 2.5, h*0.77), (cx + 2.5, h*0.72)], LINE*0.8, g=ink)
        stroke(bez((w*0.46, h*0.48), (w*0.46, h*0.56), (w*0.54, h*0.56), (w*0.54, h*0.48)) + [(w*0.54, h*0.44), (w*0.46, h*0.44)],
               LINE*0.7, closed=True, g=ink)
        stroke([(w*0.5, h*0.77), (w*0.5, h*0.93)], LINE*0.8, g=ink)
        shape([(w*0.5, h*0.93), (w*0.66, h*0.89), (w*0.5, h*0.85)], P.TAG_STAR, LINE*0.5)
        stroke(bez((w*0.08, h*0.3), (w*0.3, h*0.36), (w*0.7, h*0.36), (w*0.92, h*0.3)), LINE*0.7, g=ink)   # the hill
        hand_text(w*0.1, h*0.12, w*0.8, "XIV", "SHB", 13, g=ink)
        if torn: hand_text(w*0.02, h*0.02 + 2, w*0.96, "Další poklad je na", "SH", 7, g=ink)


def skicak(x, y, w=70, h=56, level=0, rot=0, day=1):
    """one of Bětka's sketchbook drawings of the measuring rock in the creek; level 0..2: the water line higher.
    day = how many dots in the corner (Bětka can't write the date yet, she counts)"""
    with T(x, y, 1.0, rot=rot):
        shape([(0, 0), (w, 0), (w, h), (0, h)], 1.0, LINE*0.8)
        for k in range(3): stroke([(4, h - 6 - k*0.8), (w - 4, h - 6 - k*0.8)], LINE*0.2, g=0.85)
        rx, rb = w*0.5, h*0.18
        rock = bez((rx - 12, rb), (rx - 15, rb + 18), (rx - 4, rb + 30), (rx + 4, rb + 28)) + \
               bez((rx + 4, rb + 28), (rx + 13, rb + 22), (rx + 13, rb + 8), (rx + 11, rb))
        fill(rock, P.STONE)
        crayon(rock, 0.25, LINE*1.0, closed=True)
        wl = rb + 6 + level*8
        C.saveState(); C.clipPath(poly([(2, 2), (w - 2, 2), (w - 2, wl), (2, wl)]), stroke=0, fill=0)
        fill([(2, 2), (w - 2, 2), (w - 2, wl), (2, wl)], P.CREEK, 0.85)
        C.restoreState()
        crayon([(3 + k*(w - 6)/10, wl + (1.5 if k % 2 else -1.5)) for k in range(11)], P.CREEK_DEEP, LINE*1.4)
        fill(ell(w - 12, h - 14, 5, 5, 16), P.KRASLICE_YELLOW)
        for k in range(day):
            dot(6 + k*5, h - 8, 1.4, 0.2)


def bobri_hrad(x, y, w=150, h=80, wl=0.5):
    """a beaver lodge cut in half for the fact page: a dome of sticks and mud, a dry room inside above the water and
    a tunnel going down to an entrance UNDER the water. (x, y) = bottom centre; wl = the water line (0..1 of h)"""
    yw = y + h*wl
    fill([(x - w*0.75, y - 6), (x + w*0.75, y - 6), (x + w*0.75, yw), (x - w*0.75, yw)], P.CREEK)
    stroke([(x - w*0.75, yw), (x + w*0.75, yw)], BG, g=0.3)
    fill([(x - w*0.75, y - 10), (x + w*0.75, y - 10), (x + w*0.75, y), (x - w*0.75, y)], P.MUD_DARK)
    dome = [(x - w/2, y)] + bez((x - w/2, y), (x - w*0.4, y + h*1.2), (x + w*0.4, y + h*1.2), (x + w/2, y), 20)[1:]
    form(dome, P.MUD, sdx=0, sdy=-2, sh=0.12)
    rd = random.Random(9)
    for i in range(26):
        bx = x + rd.uniform(-w*0.42, w*0.42); by = y + rd.uniform(4, h*0.9*(1 - (abs(bx - x)/(w*0.5))**2))
        a = math.radians(rd.uniform(-40, 40)); L = rd.uniform(10, 22)
        stroke([(bx - math.cos(a)*L/2, by - math.sin(a)*L/2), (bx + math.cos(a)*L/2, by + math.sin(a)*L/2)], LINE*2.0, g=P.BARK)
    room = ell(x + w*0.06, yw + h*0.16, w*0.2, h*0.16, 30)
    shape(room, P.BARN_DARK, LINE)
    fill(ell(x + w*0.06, yw + h*0.04, w*0.17, h*0.04, 20), P.NEST_STRAW)
    tunnel = bez((x - w*0.12, yw + h*0.12), (x - w*0.22, yw), (x - w*0.24, y + h*0.12), (x - w*0.36, y + h*0.08))
    tube(tunnel, h*0.14, h*0.13, P.BARN_DARK, lw=LINE*0.8, sh=0)
    fill(ell(x - w*0.37, y + h*0.08, h*0.07, h*0.08, 14), P.CREEK_DEEP)
    return (x - w*0.37, y + h*0.08), (x + w*0.06, yw + h*0.16)


def leknin(x, y, s=1.0):
    """a water-lily pad with a flower (for the activity page)"""
    with T(x, y, s):
        shape(ell(0, 0, 20, 7, 24, 20, 340) + [(0, 0)], P.WILLOW_DARK, LINE*0.8)
        for a in range(0, 360, 45):
            ra = math.radians(a)
            shape(ell(math.cos(ra)*4, 6 + math.sin(ra)*2.6, 3.4, 2.2, 12, rot=a), 1.0, LINE*0.5)
        fill(ell(0, 6.5, 2, 1.6, 10), P.FORSYTHIA)


def ve_spacaku(fn, hip, x, y, s=1.0, g=P.SLEEPING_BAG, **kw):
    """a child sitting up in a sleeping bag, legs stretched out inside it: the figure from the waist up, the puffy bag
    in front; (x, y) = the bag's bottom middle"""
    waist = y + hip*s*0.42
    C.saveState()
    C.clipPath(poly([(x - 200, waist), (x + 200, waist), (x + 200, waist + 400), (x - 200, waist + 400)]), stroke=0, fill=0)
    fn(x, y - hip*s*0.5, s, shadow=False, **kw)
    C.restoreState()
    bag = bez((-24, 0), (-30, hip*0.3), (-20, hip*0.62), (0, hip*0.6)) + bez((0, hip*0.6), (20, hip*0.62), (30, hip*0.3), (24, 0))
    bag = [(x + px*s, y + py*s) for px, py in bag]
    cast_shadow(x, y, 26*s, 3*s)
    shape(bag, g, LINE)
    for k in (-10, 0, 10): stroke([(x + k*s, y + 2*s), (x + k*1.1*s, y + hip*s*0.56)], LINE*0.5, g=0.35)
