"""Issue 14 (Poklad na hradě): Klub Hvězdička sleeps over at Točník. The castle on its wooded hill (and the ruin of
Žebrák below it), the gate and the bridge over the moat, the bear moat with Martin and Agáta, the courtyard, the
residential tower with its rows of putlog holes (the jackdaws' hole is one of them), the vaulted hall where the Klub
sleeps, the deep window and its sill, the jackdaws, a pigeon, a bat, the twig heap, Joey's fur, the red ribbon and
Alica's bow clip, Tonda's rohlík, paní kastelánka and her keys, the second Klub tin with the star map and the little
key, Bětka's drawing of the tower wall, the king's kingfisher, the treadwheel crane and the hidden keys.

Animals face right with their feet at y = 0, like Joey."""
import math, random
import lib
from lib import ell, bez, rrect, resample
from style3 import *
from style3 import C, draw_arm, draw_legs, head_outline, face, notch
import palette as P
from scenes3 import BG, s_, sh_, hills, cloud, tree
from chars3 import Person, star, key
from pond import far_trees
from letter import hand_text


def _panel_fill(p, g, alpha=None):
    fill([(p.x, p.y), (p.x + p.w, p.y), (p.x + p.w, p.y + p.h), (p.x, p.y + p.h)], g, alpha)


def _rect(x0, y0, x1, y1):
    return [(x0, y0), (x1, y0), (x1, y1), (x0, y1)]


# ================================================================== the hidden-object game: 10 keys
def hidden_klic(x, y, r=13, rot=-20):
    """one of the 10 old keys hidden in the issue: inside a white halo and a black line, so it reads on stone, grass
    and dark wood alike. r = half its length"""
    k = r/13
    with T(x, y, 1.0, rot=rot):
        o = ell(0, 0, r*1.2, r*0.62, 30)
        stroke(o, LINE*4.4, closed=True, g=0.0, taper=False)
        stroke(o, LINE*2.8, closed=True, g=1.0, taper=False)
        fill(o, 1.0)
        with T(0, 0, k):
            shape(ell(-8, 0, 4.6, 4.6, 24), P.KEY_IRON, LINE*0.8)
            fill(ell(-8, 0, 2.0, 2.0, 14), 1.0); stroke(ell(-8, 0, 2.0, 2.0, 14), LINE*0.5, closed=True)
            shape(_rect(-3.6, -1.3, 10, 1.3), P.KEY_IRON, LINE*0.7)
            shape([(6, -1.3), (6, -5.2), (8, -5.2), (8, -3.4), (9.6, -3.4), (9.6, -5.2), (10.8, -5.2), (10.8, -1.3)],
                  P.KEY_IRON, LINE*0.6)


# ================================================================== the castle from afar
def castle_far(x, y, s=1.0, dusk=False):
    """Točník on the ridge as seen from below: the long burgrave's palace with its high roof on the left, the square
    tower in the middle, the royal palace on the right, walls round them; (x, y) = the rock foot in the middle"""
    wall = P.CASTLE_WALL_DARK if dusk else P.CASTLE_WALL
    with T(x, y, s):
        rock = bez((-120, 0), (-100, 14), (-80, 22), (-60, 24)) + [(70, 24)] + bez((70, 24), (90, 20), (108, 12), (124, 0))
        shape(rock, P.ROCK_DARK, BG)
        shape(_rect(-96, 22, 96, 44), wall, BG)                       # the outer wall
        for k in range(17):
            shape(_rect(-96 + k*11.4, 44, -91 + k*11.4, 49), wall, BG*0.8)
        shape(_rect(-84, 40, -10, 92), wall, LINE*0.9)                # burgrave's palace
        shape([(-88, 92), (-6, 92), (-22, 120), (-72, 120)], P.CASTLE_ROOF, LINE*0.9)
        for wx in range(-76, -14, 14):
            shape(_rect(wx, 58, wx + 6, 70), P.PUTLOG, BG*0.7)
            shape(_rect(wx, 76, wx + 6, 86), P.PUTLOG, BG*0.7)
        shape(_rect(-4, 40, 30, 132), wall, LINE*0.9)                 # the tower
        shape([(-7, 132), (33, 132), (13, 156)], P.CASTLE_ROOF, LINE*0.9)
        for row in range(3):
            for col in range(3):
                fill(_rect(1 + col*10, 96 + row*10, 5 + col*10, 100 + row*10), P.PUTLOG)
        shape(_rect(9, 74, 17, 86), P.PUTLOG, BG*0.7)
        shape(_rect(34, 40, 92, 80), wall, LINE*0.9)                  # royal palace
        shape([(30, 80), (96, 80), (84, 100), (42, 100)], P.CASTLE_ROOF, LINE*0.9)
        for wx in (42, 58, 74):
            shape(bez((wx, 52), (wx, 64), (wx + 8, 64), (wx + 8, 52)) + [(wx + 8, 50), (wx, 50)], P.PUTLOG, BG*0.7)


def zebrak_ruin(x, y, s=1.0):
    """the ruin of the older Žebrák castle lower on the same ridge: a round tower stump and broken walls"""
    with T(x, y, s):
        shape(bez((-40, 0), (-30, 10), (20, 12), (40, 0)), P.ROCK_DARK, BG)
        shape([(-26, 8), (-26, 30), (-20, 34), (-14, 28), (-10, 32), (-6, 24), (-6, 8)], P.CASTLE_WALL_DARK, BG)
        shape([(0, 8), (0, 50), (4, 54), (10, 50), (16, 54), (18, 8)], P.CASTLE_WALL_DARK, LINE*0.8)
        fill(_rect(6, 30, 11, 38), P.PUTLOG)
        shape([(22, 8), (22, 22), (28, 26), (34, 18), (34, 8)], P.CASTLE_WALL_DARK, BG)


def wooded_hill(p, top_y, seed=1, g=None, peak_x=0.5, depth=None):
    """a long wooded ridge across the panel, its crest at top_y over peak_x (a panel fraction), falling off to both sides"""
    g = g or P.HILL_FOREST
    depth = depth if depth is not None else p.h*0.28
    rd = random.Random(seed)
    crest = []
    for i in range(41):
        fx = -0.02 + i*1.04/40
        d = (fx - peak_x)/max(peak_x, 1 - peak_x)
        crest.append((p.X(fx), top_y - depth*min(1.0, d*d) + math.sin(i*1.7 + seed)*1.5))
    pts = [(p.x - 5, p.y - 5)] + crest + [(p.x + p.w + 5, p.y - 5)]
    fill(pts, g); stroke(crest, BG)
    for _ in range(int(p.w/14)):
        tx = rd.uniform(p.x, p.x + p.w); ty = rd.uniform(p.y, top_y - 14)
        stroke(ell(tx, ty, 6, 4, 12, 200, 340), BG*0.6, g=0.3)


def kavky_sky(x0, y0, x1, y1, n=5, seed=4, s=0.5):
    """a few jackdaws flying far off: small black ticks"""
    rd = random.Random(seed)
    for _ in range(n):
        x, y = rd.uniform(x0, x1), rd.uniform(y0, y1)
        k = rd.uniform(0.7, 1.2)*s*10
        stroke(bez((x - k, y + k*0.3), (x - k*0.4, y + k*0.6), (x - k*0.1, y + k*0.2), (x, y)), LINE*0.9, g=P.JACKDAW)
        stroke(bez((x, y), (x + k*0.1, y + k*0.2), (x + k*0.4, y + k*0.6), (x + k, y + k*0.3)), LINE*0.9, g=P.JACKDAW)


def tocnik_view(p, seed=1, sky_g=None, castle=(0.62, 0.52, 1.0), zebrak=(0.2, 0.3, 0.9), birds=True):
    """the ridge with Točník on top and Žebrák lower down: castle/zebrak = (x, y, scale) as panel fractions"""
    _panel_fill(p, sky_g if sky_g is not None else P.SUMMER_SKY)
    if sky_g is None:
        cloud(p.X(0.18), p.Y(0.88), 0.6); cloud(p.X(0.82), p.Y(0.92), 0.45)
    hills(p, p.Y(0.42), 20, P.FAR_FIELD, seed)
    wooded_hill(p, p.Y(castle[1]) + 8, seed, peak_x=castle[0], depth=p.Y(castle[1]) - p.Y(0.2))
    if zebrak: zebrak_ruin(p.X(zebrak[0]), p.Y(zebrak[1]), zebrak[2])
    castle_far(p.X(castle[0]), p.Y(castle[1]), castle[2], dusk=sky_g == P.DUSK_SKY)
    if birds: kavky_sky(p.X(castle[0]) - 40, p.Y(castle[1]) + 150*castle[2], p.X(castle[0]) + 80, p.Y(castle[1]) + 190*castle[2], 4, seed)


# ================================================================== walls, the tower, the courtyard
def stone_wall(x0, y0, x1, y1, seed=3, g=None, joint=None, rows=14):
    """a rubble-stone wall face: the fill and staggered stone outlines"""
    g = g if g is not None else P.CASTLE_WALL
    joint = joint if joint is not None else P.CASTLE_JOINT
    fill(_rect(x0, y0, x1, y1), g)
    rd = random.Random(seed)
    C.saveState(); C.clipPath(poly(_rect(x0, y0, x1, y1)), stroke=0, fill=0)
    yy = y0; i = 0
    while yy < y1:
        h = rows*rd.uniform(0.8, 1.2)
        xx = x0 - rd.uniform(0, 20)
        while xx < x1:
            w = rows*rd.uniform(1.4, 2.6)
            stroke(rrect(xx + 1, yy + 1, w - 2, h - 2, 3), BG*0.55, closed=True, g=joint)
            xx += w
        yy += h; i += 1
    C.restoreState()


def tower_holes(x0, y0, w, h, rows=3, cols=6):
    """the putlog holes of the tower face: rows of small square holes from the top down, numbered in reading order
    (left to right, top to bottom) like the kids count them. Returns [(cx, cy, size)]"""
    out = []
    sz = min(w/cols*0.36, 16)
    for r_ in range(rows):
        cy = y0 + h*(0.78 - r_*0.22)
        for c in range(cols):
            cx = x0 + w*(c + 0.5)/cols
            out.append((cx, cy, sz))
    return out


def putlog(cx, cy, sz, twigs=False, ribbon=False, eyes=False, glow=False, bird=False):
    """one putlog hole; twigs: twig ends sticking out; ribbon: the red ribbon hanging out; eyes: two pale jackdaw eyes
    looking out; glow: lit up by Hanka's torch; bird: a jackdaw's head peeking out"""
    hole = _rect(cx - sz/2, cy - sz/2, cx + sz/2, cy + sz/2)
    shape(hole, P.PUTLOG, BG)
    stroke([(cx - sz/2, cy - sz/2 - 1.2), (cx + sz/2 + 1, cy - sz/2 - 1.2)], BG, g=P.CASTLE_JOINT)
    if glow:
        fill(hole, P.LANTERN_GLOW, 0.35)
    if twigs:
        rd = random.Random(int(cx*7 + cy))
        for k in range(4):
            a = rd.uniform(-30, 30); L = sz*rd.uniform(0.5, 0.9)
            bx = cx + rd.uniform(-sz*0.35, sz*0.35); by = cy - sz*0.42
            stroke([(bx, by), (bx + math.sin(math.radians(a))*L, by - math.cos(math.radians(a))*L*0.4)], LINE*0.7, g=P.TWIGS)
    if eyes:
        for sx in (-1, 1):
            fill(ell(cx + sx*sz*0.17, cy + sz*0.08, sz*0.11, sz*0.11, 12), P.JACKDAW_EYE)
            dot(cx + sx*sz*0.17, cy + sz*0.08, sz*0.04, 0.0)
    if bird:
        kavka(cx - sz*0.1, cy - sz*0.5, sz/20, pose="peek")
    if ribbon:
        rx = cx + sz*0.2
        stuzka_hang(rx, cy - sz*0.45, sz*1.6)


def stuzka_hang(x, y, L=24):
    """the red ribbon hanging down from (x, y), a little wavy"""
    pts = bez((x, y), (x + 3, y - L*0.35), (x - 3, y - L*0.65), (x + 1, y - L), 16)
    stroke(pts, LINE*3.4, g=0.0)
    stroke(pts, LINE*2.2, g=P.RED_RIBBON)


def tower(x, y, w=150, h=300, seed=5, roof=True, holes=True, marks=None, door=True, shade=True):
    """Točník's square residential tower, its foot on (x, y) (the bottom middle). marks = {hole number (1..18):
    dict(twigs=, ribbon=, eyes=, glow=, bird=)} for putlog(). Returns the hole list"""
    x0, x1 = x - w/2, x + w/2
    stone_wall(x0, y, x1, y + h, seed, rows=max(9, w/11))
    if shade:
        fill(_rect(x1 - w*0.12, y, x1, y + h), 0.0, 0.08)
    stroke(_rect(x0, y, x1, y + h), LINE, closed=True)
    if roof:
        shape([(x0 - 8, y + h), (x1 + 8, y + h), (x + w*0.1, y + h + w*0.5), (x - w*0.1, y + h + w*0.5)], P.CASTLE_ROOF, LINE)
        for k in range(1, 6):
            yy = y + h + w*0.5*k/6
            hw = (w/2 + 8)*(1 - k/6) + w*0.1*k/6
            stroke([(x - hw, yy), (x + hw, yy)], BG*0.6, g=0.25)
    if door:
        dw = w*0.24
        shape(bez((x - dw/2, y), (x - dw/2, y + dw*1.5), (x + dw/2, y + dw*1.5), (x + dw/2, y)), P.CASTLE_WOOD, LINE)
        for k in (-1, 0, 1): stroke([(x + k*dw*0.25, y), (x + k*dw*0.25, y + dw*1.2)], BG*0.6, g=0.25)
    hl = []
    if holes:
        hl = tower_holes(x0, y + h*0.3, w, h*0.7)
        for i, (cx, cy, sz) in enumerate(hl):
            putlog(cx, cy, sz, **((marks or {}).get(i + 1, {})))
    return hl


def palace_wall(x0, x1, y, h, seed=7, windows=(), sgraffito=True, roof=True):
    """a palace front behind the courtyard: wall, Renaissance sgraffito band, the window openings (x fractions), roof"""
    stone_wall(x0, y, x1, y + h, seed, g=P.CASTLE_WALL, rows=13)
    if sgraffito:
        band = _rect(x0, y + h*0.82, x1, y + h*0.94)
        fill(band, P.SGRAFFITO)
        xx = x0 + 4
        while xx < x1 - 10:
            stroke(_rect(xx, y + h*0.84, xx + 12, y + h*0.92), BG*0.6, closed=True, g=0.45)
            stroke([(xx, y + h*0.84), (xx + 12, y + h*0.92)], BG*0.5, g=0.45)
            xx += 14
        stroke(band, BG, closed=True)
    for fx in windows:
        wx = x0 + (x1 - x0)*fx
        win = bez((wx - 9, y + h*0.4), (wx - 9, y + h*0.62), (wx + 9, y + h*0.62), (wx + 9, y + h*0.4)) + \
              [(wx + 9, y + h*0.3), (wx - 9, y + h*0.3)]
        shape(win, P.PUTLOG, BG)
    stroke(_rect(x0, y, x1, y + h), LINE, closed=True)
    if roof:
        shape([(x0 - 6, y + h), (x1 + 6, y + h), (x1 - 20, y + h + 46), (x0 + 20, y + h + 46)], P.CASTLE_ROOF, LINE)


def battlement(x0, x1, y, h=12, g=None):
    """a wall top with merlons"""
    g = g if g is not None else P.CASTLE_WALL
    xx = x0
    while xx < x1:
        shape(_rect(xx, y, min(x1, xx + h*0.9), y + h), g, BG)
        xx += h*1.6


def cobbles(p, y0, y1, seed=2, g=None):
    """the courtyard floor: worn grass and paving stones"""
    fill(_rect(p.x - 5, p.y - 5, p.x + p.w + 5, y1), g if g is not None else P.SPRING_GRASS)
    rd = random.Random(seed)
    for _ in range(int(p.w*(y1 - y0)/700)):
        cx, cy = rd.uniform(p.x, p.x + p.w), rd.uniform(p.y, y1 - 4)
        k = 0.6 + (y1 - cy)/(y1 - p.y + 1)*0.8
        stroke(ell(cx, cy, 7*k, 3*k, 14), BG*0.6, closed=True, g=0.45)
    s_([(p.x - 5, y1), (p.x + p.w + 5, y1)], BG)


def nadvori(p, gy_f=0.32, seed=1, tower_x=0.78, tower_w=0.3, tower_h=None, marks=None, windows=(0.2, 0.45),
            sky_g=None, birds=True, night=False, palace=True):
    """the courtyard: sky, the palace front behind, the tower on the right (or tower_x=None), the ground. Returns
    (ground y, hole list)"""
    gy = p.Y(gy_f)
    _panel_fill(p, P.NIGHT_MEADOW if night else (sky_g if sky_g is not None else P.SUMMER_SKY))
    if not night and sky_g is None: cloud(p.X(0.3), p.Y(0.9), 0.5)
    if palace:
        palace_wall(p.x - 10, p.X(0.62), gy, p.h*0.5, seed, windows=windows)
        battlement(p.X(0.62), p.x + p.w + 5, gy + p.h*0.28, 12)
        fill(_rect(p.X(0.62), gy, p.x + p.w + 5, gy + p.h*0.28), P.CASTLE_WALL)
        stone_wall(p.X(0.62), gy, p.x + p.w + 5, gy + p.h*0.28, seed + 1)
        stroke([(p.X(0.62), gy + p.h*0.28), (p.x + p.w + 5, gy + p.h*0.28)], BG)
    hl = []
    if tower_x is not None:
        th = tower_h or p.h*0.78
        hl = tower(p.X(tower_x), gy, p.w*tower_w, th, seed + 2, roof=gy + th < p.y + p.h - 10, marks=marks)
    cobbles(p, p.y, gy, seed)
    if birds and not night:
        kavky_sky(p.X(0.4), p.Y(0.82), p.X(0.95), p.Y(0.97), 3, seed)
    if night: night_tint(p, 0.35)
    return gy, hl


def night_tint(p, alpha=0.4):
    _panel_fill(p, P.NIGHT_MEADOW, alpha)


def night_stars(p, y0=0.6, n=24, seed=3):
    rd = random.Random(seed)
    for _ in range(n):
        x, y = p.X(rd.uniform(0.02, 0.98)), p.Y(rd.uniform(y0, 0.98))
        if rd.random() < 0.2: star(x, y, 2.6, 1.0)
        else: dot(x, y, rd.uniform(0.6, 1.2), 1.0)


# ================================================================== the gate, the bridge, the bear moat
def gate_bridge(p, gy_f=0.3, seed=2):
    """the gate tower at the end of the stone bridge over the rock-cut moat; returns (bridge deck y, gate x)"""
    _panel_fill(p, P.SUMMER_SKY)
    cloud(p.X(0.2), p.Y(0.88), 0.55)
    wooded_hill(p, p.Y(0.55), seed, P.FOREST_DARK)
    gy = p.Y(gy_f)
    gx = p.X(0.7)
    stone_wall(p.X(0.42), gy, p.x + p.w + 5, gy + p.h*0.42, seed, rows=12)
    battlement(p.X(0.42), p.x + p.w + 5, gy + p.h*0.42, 12)
    stone_wall(gx - p.w*0.12, gy, gx + p.w*0.12, gy + p.h*0.62, seed + 3, rows=12)
    stroke(_rect(gx - p.w*0.12, gy, gx + p.w*0.12, gy + p.h*0.62), LINE, closed=True)
    battlement(gx - p.w*0.12, gx + p.w*0.12, gy + p.h*0.62, 12)
    aw = p.w*0.07
    shape(bez((gx - aw, gy), (gx - aw, gy + aw*2.1), (gx + aw, gy + aw*2.1), (gx + aw, gy)), P.PUTLOG, LINE)
    fill(_rect(p.x - 5, p.y - 5, p.x + p.w + 5, gy - p.h*0.08), P.ROCK_DARK)
    rd = random.Random(seed)
    for _ in range(14):
        stroke([(rd.uniform(p.x, p.x + p.w), rd.uniform(p.y, gy - 20)), (rd.uniform(p.x, p.x + p.w), rd.uniform(p.y, gy - 20))],
               BG*0.5, g=0.3)
    deck = _rect(p.x - 5, gy - p.h*0.08, gx + aw, gy)
    shape(deck, P.CASTLE_STONE, LINE)
    for k in range(4):
        px0 = p.x + p.w*(0.08 + k*0.2)
        shape(bez((px0, p.y - 5), (px0, gy - p.h*0.24), (px0 + p.w*0.16, gy - p.h*0.24), (px0 + p.w*0.16, p.y - 5)),
              P.ROCK, BG)
    s_([(p.x - 5, gy - 0.5), (gx + aw, gy - 0.5)], BG)
    for k in range(10):
        bx = p.x + k*p.w*0.07
        stroke([(bx, gy), (bx, gy + 16)], LINE*0.8, g=P.CASTLE_WOOD)
    stroke([(p.x - 5, gy + 16), (gx - aw, gy + 16)], LINE*1.4, g=P.CASTLE_WOOD)
    return gy, gx


def brtnik(x, y, s=1.0, flip=False, pose="walk", mood="open"):
    """a brown bear (Martin or Agáta) side on: pose walk | sit | stand (on its hind legs, reaching up); mood open | sleepy"""
    G_ = P.BEAR_FUR; D_ = P.BEAR_DARK; L_ = P.BEAR_LIGHT
    with T(x, y, s, flip):
        if pose == "sit":
            shape(ell(-4, 26, 26, 28, 40), G_, LINE)
            shape(ell(4, 8, 14, 9, 24), G_, LINE)               # hind foot
            shape(ell(12, 22, 7, 14, 20, rot=-10), G_, LINE)     # front leg
            hx, hy = 10, 58
        elif pose == "stand":
            shape(bez((-14, 4), (-22, 40), (-16, 76), (0, 84)) + bez((0, 84), (16, 80), (20, 40), (12, 4)), G_, LINE)
            for sx in (-1, 1): shape(ell(sx*8, 4, 9, 5, 16), D_, LINE*0.8)
            shape(bez((8, 70), (20, 80), (26, 94), (24, 104)) + [(16, 104)] + bez((16, 104), (16, 92), (8, 82), (2, 76)), G_, LINE)
            hx, hy = 2, 96
        else:
            body = bez((-40, 18), (-46, 44), (-10, 52), (16, 46)) + bez((16, 46), (30, 42), (34, 26), (28, 14)) + \
                   [(28, 4), (18, 4), (16, 14), (-20, 14), (-22, 4), (-32, 4), (-34, 14)]
            for lx in (-26, 22):
                shape(_rect(lx - 6, 0, lx + 5, 20), D_, LINE*0.8)
            shape(body, G_, LINE)
            fill(ell(-14, 46, 20, 4, 20), L_, 0.4)
            hx, hy = 34, 38
        with T(hx, hy, 1.0):
            for sx in (-1, 1):
                shape(ell(-4 + sx*6, 12, 4.4, 4.4, 16), G_, LINE*0.8)
                fill(ell(-4 + sx*6, 12, 2.2, 2.2, 10), L_)
            shape(notch(ell(0, 0, 14, 12, 34), 0.8, 4), G_, LINE)
            shape(ell(11, -3, 8, 6, 20), L_, LINE*0.8)
            shape(ell(17, -1, 3, 2.4, 12), 0.1, LINE*0.5)
            stroke(bez((10, -7), (13, -9), (16, -8), (18, -6)), LINE*0.6)
            if mood == "sleepy":
                stroke(bez((1, 3), (3, 2), (5, 2), (7, 3)), LINE*0.7)
            else:
                dot(4, 3, 1.6, 0.0); dot(4.5, 3.6, 0.5, 1.0)


def medvedi_prikop(p, gy_f=0.25, seed=3, fence=True):
    """the bear moat seen from its edge: rock walls going down, the grassy floor with a pool and a log; returns the
    floor y"""
    _panel_fill(p, P.SUMMER_SKY)
    gy = p.Y(gy_f)
    stone_wall(p.x - 5, p.Y(0.55), p.x + p.w + 5, p.y + p.h + 5, seed, g=P.CASTLE_WALL, rows=13)
    battlement(p.x - 5, p.x + p.w + 5, p.Y(0.92), 10)
    rockL = [(p.x - 5, p.y - 5), (p.x - 5, p.Y(0.8)), (p.X(0.1), p.Y(0.6)), (p.X(0.16), gy + 6), (p.X(0.2), p.y - 5)]
    rockR = [(p.x + p.w + 5, p.y - 5), (p.x + p.w + 5, p.Y(0.8)), (p.X(0.9), p.Y(0.6)), (p.X(0.86), gy + 6), (p.X(0.82), p.y - 5)]
    fill(_rect(p.x - 5, p.y - 5, p.x + p.w + 5, p.Y(0.56)), P.ROCK)
    stroke([(p.x - 5, p.Y(0.56)), (p.x + p.w + 5, p.Y(0.56))], BG)
    fill(_rect(p.x - 5, p.y - 5, p.x + p.w + 5, gy), P.SPRING_GRASS)
    s_([(p.x - 5, gy), (p.x + p.w + 5, gy)], BG)
    for r_ in (rockL, rockR): shape(r_, P.ROCK_DARK, BG)
    shape(ell(p.X(0.66), p.Y(0.12), p.w*0.12, p.h*0.05, 30), P.POND_WATER, BG)
    tube([(p.X(0.28), p.Y(0.2)), (p.X(0.46), p.Y(0.22))], 9, 9, P.LOG, lw=BG)
    if fence:
        for k in range(int(p.w/26) + 1):
            fx = p.x + k*26
            stroke([(fx, p.Y(0.56)), (fx, p.Y(0.66))], LINE*0.8, g=0.25)
        for yy in (0.6, 0.65): stroke([(p.x - 5, p.Y(yy)), (p.x + p.w + 5, p.Y(yy))], LINE*0.7, g=0.25)
    return gy


# ================================================================== the hall where the Klub sleeps
def hall(p, floor_f=0.2, seed=4, night=False, window=(0.7, 0.42, 0.2, 0.36), sill_items=None, vault=True):
    """the vaulted hall: plastered walls, a cross vault, the deep window niche (x, y, w, h as panel fractions) and its
    sill. sill_items(x0, x1, y) draws on the sill. Returns (floor y, (sill x0, sill x1, sill y))"""
    _panel_fill(p, P.HALL_WALL)
    fy = p.Y(floor_f)
    if vault:
        for fx in (0.0, 0.5, 1.0):
            stroke(bez((p.X(fx - 0.5), p.Y(0.55)), (p.X(fx - 0.3), p.Y(1.05)), (p.X(fx + 0.3), p.Y(1.05)), (p.X(fx + 0.5), p.Y(0.55))),
                   LINE*0.9, g=0.5)
        for fx in (0.0, 1.0):
            stroke([(p.X(fx), p.Y(0.55)), (p.X(fx), fy)], LINE*0.6, g=0.6)
    wx, wy, ww, wh = window
    x0, x1, y0, y1 = p.X(wx - ww/2), p.X(wx + ww/2), p.Y(wy), p.Y(wy + wh)
    niche = [(x0 - 14, y0 - 8), (x1 + 14, y0 - 8)] + bez((x1 + 14, y1), (x1 + 14, y1 + (x1 - x0)*0.5), (x0 - 14, y1 + (x1 - x0)*0.5), (x0 - 14, y1))
    niche = [(x0 - 14, y0 - 8), (x1 + 14, y0 - 8), (x1 + 14, y1)] + niche[3:]
    shape(niche, P.CASTLE_WALL_DARK, LINE*0.9)
    win = [(x0, y0), (x1, y0), (x1, y1)] + bez((x1, y1), (x1, y1 + (x1 - x0)*0.42), (x0, y1 + (x1 - x0)*0.42), (x0, y1))[1:]
    shape(win, P.NIGHT_MEADOW if night else P.SUMMER_SKY, LINE)
    if night:
        for k in range(5): dot(x0 + (x1 - x0)*(0.15 + k*0.18), y0 + (y1 - y0)*(0.4 + (k % 2)*0.35), 0.9, 1.0)
    else:
        cloud((x0 + x1)/2, y0 + (y1 - y0)*0.7, 0.3)
    sill = _rect(x0 - 16, y0 - 12, x1 + 16, y0)
    shape(sill, P.CASTLE_STONE, LINE*0.9)
    if sill_items: sill_items(x0, x1, y0)
    fill(_rect(p.x - 5, p.y - 5, p.x + p.w + 5, fy), P.HALL_FLOOR)
    rd = random.Random(seed)
    for k in range(int(p.w/40) + 2):
        bx = p.x + k*40 + rd.uniform(-6, 6)
        stroke([(bx, p.y), (bx + (bx - p.X(0.5))*0.2, fy)], BG*0.6, g=0.4)
    s_([(p.x - 5, fy), (p.x + p.w + 5, fy)], BG)
    if night: night_tint(p, 0.38)
    return fy, (x0 - 16, x1 + 16, y0)


def lezi(fn, x, y, s=1.0, g=P.SLEEPING_BAG, length=120, **kw):
    """a child lying in a sleeping bag, head to the left, asleep; (x, y) = the bag's right end on the floor"""
    with T(x - 8*s, y + 12*s, 1.0, rot=90):
        C.saveState()
        C.clipPath(poly([(-60*s, -length*s*0.62), (60*s, -length*s*0.62), (60*s, 400), (-60*s, 400)]), stroke=0, fill=0)
        fn(0, 0, s, shadow=False, **kw)
        C.restoreState()
    bag = bez((x, y), (x + 6*s, y + 22*s), (x - 20*s, y + 30*s), (x - length*s*0.4, y + 26*s)) + \
          bez((x - length*s*0.4, y + 26*s), (x - length*s*0.62, y + 24*s), (x - length*s*0.66, y + 6*s), (x - length*s*0.6, y))
    cast_shadow(x - length*s*0.3, y, length*s*0.36, 3*s)
    shape(bag, g, LINE)
    for k in (0.2, 0.36, 0.5): stroke([(x - length*s*k, y + 2*s), (x - length*s*k - 2*s, y + 24*s)], LINE*0.5, g=0.35)


def lucerna(x, y, s=1.0, lit=True):
    """a camping lantern standing on the floor"""
    with T(x, y, s):
        if lit: fill(ell(0, 12, 26, 26, 30), P.LANTERN_GLOW, 0.3)
        shape(_rect(-6, 0, 6, 4), 0.3, LINE*0.8)
        shape(_rect(-5, 4, 5, 18), P.TENT_GLOW if lit else 0.85, LINE*0.8)
        shape(_rect(-6, 18, 6, 21), 0.3, LINE*0.8)
        stroke(bez((-4, 21), (-4, 28), (4, 28), (4, 21)), LINE*0.8)


# ================================================================== the birds
def kavka(x, y, s=1.0, flip=False, pose="perch", item=None, young=False):
    """a jackdaw: black, silver-grey nape, pale eye, short beak. pose perch | walk | fly | peek (only the head, out of
    a hole). item(x, y) is drawn in the beak"""
    eye_g = 0.45 if young else P.JACKDAW_EYE
    with T(x, y, s, flip):
        if pose == "fly":
            shape(bez((-4, 10), (-18, 30), (-34, 34), (-40, 28)) + bez((-40, 28), (-30, 22), (-16, 14), (-6, 6)), P.JACKDAW, LINE*0.8)
            shape(ell(0, 6, 14, 6.5, 30, rot=8), P.JACKDAW, LINE*0.9)
            shape([(-12, 4), (-26, 0), (-26, 8), (-12, 8)], P.JACKDAW, LINE*0.8)
            shape(bez((-2, 6), (6, 22), (22, 30), (34, 30)) + bez((34, 30), (24, 18), (12, 8), (4, 4)), P.JACKDAW, LINE*0.8)
            hx, hy = 14, 9
        elif pose == "peek":
            hx, hy = 0, 0
        else:
            shape([(-10, 8), (-26, 0), (-25, 4), (-8, 13)], P.JACKDAW, LINE*0.8)     # tail
            shape(ell(0, 12, 12, 8, 30, rot=18), P.JACKDAW, LINE*0.9)
            stroke(bez((-8, 10), (-2, 14), (4, 14), (9, 11)), LINE*0.5, g=0.4)
            legs = ((-1, 4), (3, 4)) if pose == "perch" else ((-3, 4), (5, 4))
            for lx, ly in legs:
                stroke([(lx, ly + 2), (lx + (2 if pose == "walk" and lx > 0 else 0), -1)], LINE*0.9)
                stroke([(lx - 2, -1), (lx + 3, -1)], LINE*0.8)
            hx, hy = 9, 21
        with T(hx, hy, 1.0):
            shape(ell(0, 0, 7, 6.4, 24), P.JACKDAW, LINE*0.9)
            nape = bez((-6.8, -2), (-7, 2.5), (-5, 5.6), (-2.2, 6.2)) + bez((-2.2, 6.2), (-2.6, 3), (-3, -1), (-4.6, -5.4))
            fill(nape, P.JACKDAW_NAPE)
            shape([(5.6, 1.4), (11.5, -0.4), (5.8, -1.8)], 0.2, LINE*0.7)
            fill(ell(2.6, 1.4, 1.9, 1.9, 12), eye_g); dot(2.9, 1.4, 0.75, 0.0)
            if item: item(11.5, -0.6)


def kavci_pero(x, y, s=1.0, rot=0):
    """a jackdaw feather: black with a bluish sheen stripe"""
    with T(x, y, s, rot=rot):
        vane = bez((0, 0), (-4.5, 6), (-4, 18), (0, 26)) + bez((0, 26), (4, 18), (4.5, 6), (0, 0))
        shape(vane, P.JACKDAW, LINE*0.7)
        stroke(bez((1.5, 4), (2.6, 10), (2.6, 16), (1.2, 22)), LINE*0.8, g=P.PIGEON_DARK)
        stroke([(0, -4), (0, 24)], LINE*0.5, g=0.5)


def holubi_pero(x, y, s=1.0, rot=0):
    """a pigeon feather: grey with a darker tip"""
    with T(x, y, s, rot=rot):
        vane = bez((0, 0), (-4.5, 6), (-4, 18), (0, 26)) + bez((0, 26), (4, 18), (4.5, 6), (0, 0))
        shape(vane, P.PIGEON, LINE*0.7)
        fill(bez((-3.6, 18), (-2, 24), (2, 24), (3.6, 18)), P.PIGEON_DARK)
        stroke([(0, -4), (0, 24)], LINE*0.5)


def holub(x, y, s=1.0, flip=False):
    """a town pigeon: grey, shiny green neck, two dark wing bars"""
    with T(x, y, s, flip):
        shape([(-10, 8), (-24, 4), (-23, 10), (-8, 14)], P.PIGEON_DARK, LINE*0.8)
        shape(ell(0, 12, 13, 9, 30, rot=10), P.PIGEON, LINE*0.9)
        for k in (0, 4): stroke([(-6 + k, 9), (2 + k, 13)], LINE*1.2, g=P.PIGEON_DARK)
        for lx in (-1, 3):
            stroke([(lx, 4), (lx, -1)], LINE*0.9, g=P.CRAYON_RED)
        with T(10, 22, 1.0):
            fill(ell(-3, -4, 6, 5, 20), P.PIGEON_NECK)
            shape(ell(0, 0, 5.6, 5, 20), P.PIGEON, LINE*0.9)
            shape([(4.6, 0.6), (9, -0.6), (4.6, -1.4)], 0.6, LINE*0.6)
            dot(2, 1, 1.1, 0.0)


def netopyr(x, y, s=1.0, hang=True):
    """a bat: hanging upside down, wings folded (hang) or flying"""
    with T(x, y, s):
        if hang:
            stroke([(-2, 0), (-2, -3)], LINE*0.7); stroke([(2, 0), (2, -3)], LINE*0.7)
            shape(ell(0, -12, 6, 10, 20), P.BAT, LINE*0.8)
            shape(ell(0, -23, 4.5, 4, 16), P.BAT, LINE*0.8)
            for sx in (-1, 1): shape([(sx*2, -26), (sx*4.5, -31), (sx*4.5, -25)], P.BAT, LINE*0.6)
            for sx in (-1, 1): dot(sx*1.6, -22, 0.6, 1.0)
        else:
            for sx in (-1, 1):
                shape([(0, 0), (sx*8, 8), (sx*16, 4), (sx*24, 10), (sx*20, -2), (sx*12, -4), (sx*6, -6)], P.BAT, LINE*0.7)
            shape(ell(0, 0, 4, 6, 14), P.BAT, LINE*0.7)
            for sx in (-1, 1): shape([(sx*1.5, 5), (sx*3, 10), (sx*3.5, 5)], P.BAT, LINE*0.5)


def bird_prints(x, y, s=1.0, n=4, rot=10, g=None):
    """a little trail of bird prints in the dust: three toes forward, one back"""
    g = g if g is not None else 0.35
    for i in range(n):
        px = x + i*12*s*math.cos(math.radians(rot)); py = y + i*12*s*math.sin(math.radians(rot)) + (3*s if i % 2 else -3*s)
        with T(px, py, s, rot=rot - 90):
            for a in (-30, 0, 30):
                ra = math.radians(90 + a)
                stroke([(0, 0), (math.cos(ra)*6, math.sin(ra)*6)], LINE*1.0, g=g)
            stroke([(0, 0), (0, -4)], LINE*1.0, g=g)


def hnizdo(x, y, s=1.0, items=True):
    """the jackdaws' nest as Hanka sees it inside the hole: a heap of twigs, lined with wool, hair and rags"""
    rd = random.Random(14)
    with T(x, y, s):
        shape(bez((-40, 0), (-44, 18), (-20, 26), (0, 24)) + bez((0, 24), (20, 26), (44, 18), (40, 0)), P.TWIGS, LINE)
        for _ in range(26):
            a = math.radians(rd.uniform(-20, 20) + (0 if rd.random() < 0.5 else 180)); bx, by = rd.uniform(-34, 34), rd.uniform(2, 22)
            stroke([(bx - math.cos(a)*14, by - math.sin(a)*14), (bx + math.cos(a)*14, by + math.sin(a)*14)], LINE*0.8, g=0.25)
        fill(ell(0, 20, 26, 7, 24), P.NEST_STRAW)
        stroke(ell(0, 20, 26, 7, 24), LINE*0.7, closed=True)
        if items:
            chlup(-14, 22, 1.0)
            chlup(10, 23, 0.8, flip=True)
            stroke(bez((-4, 20), (2, 24), (8, 18), (16, 22)), LINE*3.2, g=0.0)
            stroke(bez((-4, 20), (2, 24), (8, 18), (16, 22)), LINE*2.0, g=P.RED_RIBBON)
            sponka(-20, 18, 0.9, rot=10)


def joey_lezi(x, y, s=1.0, flip=False, mood="sleepy"):
    """Joey lying down on (x, y): his standing figure sunk to the ground (legs hidden), front paws stretched out"""
    from style3 import joey
    drop = 22*s
    cast_shadow(x + (4 if not flip else -4)*s, y, 34*s, 3.2*s)
    C.saveState()
    C.clipPath(poly([(x - 200, y), (x + 200, y), (x + 200, y + 400), (x - 200, y + 400)]), stroke=0, fill=0)
    joey(x, y - drop, s, flip=flip, mood=mood, collar=False, shadow=False)
    C.restoreState()
    d = -1 if flip else 1
    for k in (0, 7):
        shape(ell(x + d*(30 + k)*s, y + 2.2*s, 7*s, 3*s, 16), 1.0, LINE*0.8)


# ================================================================== small things
def stuzka(x, y, s=1.0, rot=0):
    """Bětka's red wool ribbon, loosely coiled"""
    with T(x, y, s, rot=rot):
        pts = bez((-16, 0), (-8, 8), (0, -6), (6, 4)) + bez((6, 4), (12, 12), (16, 0), (20, 4))[1:]
        stroke(pts, LINE*3.6, g=0.0); stroke(pts, LINE*2.4, g=P.RED_RIBBON)


def sponka(x, y, s=1.0, rot=0):
    """Alica's spare hair clip with a pink fabric bow"""
    with T(x, y, s, rot=rot):
        stroke([(-8, -3), (8, -3)], LINE*1.6, g=0.35)
        for sx in (-1, 1):
            shape([(0, 0), (sx*8, 5), (sx*9, -4)], P.BOW_CLIP, LINE*0.7)
        shape(ell(0, 0, 2.2, 2.6, 12), P.BOW_CLIP, LINE*0.7)
        for sx in (-1, 1): dot(sx*5, 0.5, 0.6, 1.0)


def rohlik(x, y, s=1.0, rot=0, bitten=False):
    """a rohlík (crescent bread roll)"""
    with T(x, y, s, rot=rot):
        out = bez((-14, 0), (-12, 10), (12, 10), (14, 0)) + bez((14, 0), (10, 4), (-10, 4), (-14, 0))
        shape(out, P.ROHLIK, LINE*0.8)
        for k in (-6, 0, 6): stroke(bez((k - 2, 3.5), (k, 8), (k + 1, 8.5), (k + 2, 4)), LINE*0.5, g=0.4)
        if bitten:
            fill(ell(13, 3, 4, 4, 14), 1.0)
    if bitten:
        rd = random.Random(int(x))
        for _ in range(6): dot(x + rd.uniform(-16, 16)*s, y - rd.uniform(2, 8)*s, 0.8*s, P.ROHLIK)


def drobky(x, y, w=30, n=10, seed=2):
    rd = random.Random(seed)
    for _ in range(n):
        cx, cy = x + rd.uniform(-w/2, w/2), y + rd.uniform(-3, 3)
        shape(ell(cx, cy, 1.4, 1.0, 8), P.ROHLIK, LINE*0.3)


def vetvicky(x, y, w=60, seed=3, s=1.0):
    """the twigs dropped under the jackdaws' hole: a loose heap of thin dry sticks"""
    rd = random.Random(seed)
    for i in range(int(w/3.5)):
        a = math.radians(rd.uniform(-35, 35) + (180 if i % 2 else 0)); L = rd.uniform(8, 18)*s
        bx, by = x + rd.uniform(-w/2, w/2), y + rd.uniform(0, 10*s)*(1 - abs(rd.uniform(-1, 1))*0.5)
        p0 = (bx - math.cos(a)*L, by - math.sin(a)*L*0.4); p1 = (bx + math.cos(a)*L, by + math.sin(a)*L*0.4)
        stroke([p0, p1], LINE*1.5, g=0.0)
        stroke([p0, p1], LINE*0.8, g=P.TWIGS)


def chlup(x, y, s=1.0, flip=False):
    """a tuft of Joey's fur: black and white hairs"""
    with T(x, y, s, flip):
        for i in range(9):
            a = -50 + i*12
            g = P.JOEY_BLACK if i % 3 else 1.0
            pts = bez((0, 0), (math.cos(math.radians(a))*4, 3 + math.sin(math.radians(a))*4),
                      (math.cos(math.radians(a))*8, 5 + math.sin(math.radians(a))*8),
                      (math.cos(math.radians(a))*11, 4 + math.sin(math.radians(a))*11))
            stroke(pts, LINE*1.6, g=0.0); stroke(pts, LINE*0.8, g=g)


def lavicka(x, y, s=1.0):
    """a wooden bench in the courtyard"""
    with T(x, y, s):
        for lx in (-26, 22): shape(_rect(lx, 0, lx + 4, 14), P.CASTLE_WOOD, LINE*0.8)
        shape(_rect(-32, 14, 32, 19), P.CASTLE_WOOD, LINE*0.9)
        shape(_rect(-30, 24, 30, 28), P.CASTLE_WOOD, LINE*0.9)
        for lx in (-24, 24): stroke([(lx, 19), (lx, 24)], LINE*1.4)


def velky_klic(x, y, s=1.0, rot=0):
    """the big old iron castle key"""
    with T(x, y, s, rot=rot):
        stroke(ell(0, 0, 8, 10, 30), LINE*3.4, closed=True, g=0.0, taper=False)
        stroke(ell(0, 0, 8, 10, 30), LINE*2.0, closed=True, g=P.KEY_IRON, taper=False)
        shape(_rect(-1.8, -40, 1.8, -9), P.KEY_IRON, LINE*0.8)
        shape([(-1.8, -40), (-10, -40), (-10, -34), (-6, -34), (-6, -30), (-1.8, -30)], P.KEY_IRON, LINE*0.8)


def svazek(x, y, s=1.0):
    """the kastelánka's big ring of keys"""
    with T(x, y, s):
        stroke(ell(0, 0, 7, 7, 24), LINE*1.6, closed=True, g=P.KEY_IRON, taper=False)
        for k, a in enumerate((-140, -110, -80, -50)):
            with T(math.cos(math.radians(a))*7, math.sin(math.radians(a))*7, 0.38, rot=a + 90):
                velky_klic(0, -8, 1.0)


def klicek(x, y, s=1.0, rot=0):
    """the little brass key with the Klub star tag from the second tin"""
    key(x, y, s, rot, tag=True)


def hvezdna_mapa(x, y, w=110, h=80, rot=0):
    """the Klub kids' star map of the summer sky: dark paper, stars joined into the Summer Triangle and the Big Dipper,
    shooting stars falling from Perseus, and "12. 8." written under them. (x, y) = bottom left"""
    with T(x, y, 1.0, rot=rot):
        shape(_rect(0, 0, w, h), P.STAR_MAP, LINE*0.9)
        stroke(_rect(3, 3, w - 3, h - 3), BG*0.6, closed=True, g=0.85)
        dip = [(0.12, 0.78), (0.2, 0.82), (0.28, 0.8), (0.34, 0.74), (0.36, 0.62), (0.47, 0.6), (0.48, 0.72)]
        stroke([(w*a, h*b) for a, b in dip[:5]] + [(w*a, h*b) for a, b in dip[5:]] + [(w*dip[3][0], h*dip[3][1])], BG*0.7, g=0.85)
        for a, b in dip: star(w*a, h*b, 2.2, 1.0)
        tri = [(0.62, 0.7), (0.86, 0.62), (0.7, 0.36)]
        stroke([(w*a, h*b) for a, b in tri], BG*0.7, closed=True, g=0.85)
        for a, b in tri: star(w*a, h*b, 2.6, 1.0)
        for k in range(4):
            sx, sy = w*(0.18 + k*0.07), h*(0.44 - k*0.04)
            stroke([(sx, sy), (sx - 12, sy - 10)], LINE*0.9, g=1.0)
            star(sx, sy, 1.8, 1.0)
        hand_text(w*0.08, h*0.08, w*0.5, "12. 8.", "SHB", 10, g=1.0)
        rd = random.Random(12)
        for _ in range(16): dot(rd.uniform(6, w - 6), rd.uniform(6, h - 6), 0.6, 1.0)


def plechovka2(x, y, s=1.0, open_=False, dirty=True):
    """the second Klub tin (a smaller round tea tin) from the jackdaws' hole"""
    rd = random.Random(21)
    with T(x, y, s):
        body = _rect(-18, 0, 18, 30)
        form(body, P.TIN, sdx=3, sdy=0)
        for bx in (-14, 14): stroke([(bx, 2), (bx, 28)], LINE*0.5, g=0.45)
        if open_:
            fill(_rect(-16, 27, 16, 30), 0.25)
            shape(_rect(14, 28, 40, 34), P.TIN, LINE*0.8)
        else:
            shape(_rect(-20, 28, 20, 35), P.TIN, LINE)
        star(0, 15, 6, 0.95)
        if dirty:
            for _ in range(8): dot(rd.uniform(-15, 15), rd.uniform(3, 26), rd.uniform(0.8, 2.0), P.RUST)


def vez_kresba(x, y, w=110, h=140, rot=0, mark=None, numbers=False):
    """Bětka's drawing of the tower wall with its putlog holes (3 rows of 6); mark = the hole number circled; numbers:
    small counting numbers next to the holes. (x, y) = bottom left"""
    with T(x, y, 1.0, rot=rot):
        shape(_rect(0, 0, w, h), P.LETTER_PAPER, LINE*0.8)
        ink = 0.25
        tx0, tx1, ty0, ty1 = w*0.18, w*0.82, h*0.06, h*0.8
        stroke(_rect(tx0, ty0, tx1, ty1), LINE*0.9, closed=True, g=ink)
        stroke([(tx0 - 4, ty1), (w*0.5, h*0.96), (tx1 + 4, ty1)], LINE*0.9, g=ink)
        for i, (cx, cy, sz) in enumerate(tower_holes(tx0, ty0 + (ty1 - ty0)*0.3, tx1 - tx0, (ty1 - ty0)*0.7)):
            fill(_rect(cx - sz/2, cy - sz/2, cx + sz/2, cy + sz/2), ink)
            if numbers:
                hand_text(cx - 8, cy + sz*0.7, 16, str(i + 1), "SH", 6.5, g=ink)
            if mark == i + 1:
                stroke(ell(cx, cy, sz*1.3, sz*1.3, 24), LINE*1.2, closed=True, g=P.RED_RIBBON)
        stroke(bez((w*0.44, ty0), (w*0.44, ty0 + 16), (w*0.56, ty0 + 16), (w*0.56, ty0)), LINE*0.8, g=ink)


def lednacek(x, y, s=1.0):
    """Václav IV.'s emblem: a kingfisher inside a twisted veil (věník)"""
    with T(x, y, s):
        ring = ell(0, 0, 26, 26, 40)
        stroke(ring, LINE*5, closed=True, g=0.0, taper=False)
        stroke(ring, LINE*3.4, closed=True, g=0.95, taper=False)
        for k in range(12):
            a = math.radians(k*30)
            stroke([(math.cos(a)*24, math.sin(a)*24), (math.cos(a + 0.3)*28, math.sin(a + 0.3)*28)], LINE*0.7)
        shape(ell(0, 0, 9, 6, 24, rot=12), P.DYE_BLUE, LINE*0.8)
        shape([(-7, -2), (-16, -6), (-14, 0)], P.DYE_BLUE, LINE*0.6)
        shape(ell(8, 4, 5, 4.4, 16), P.DYE_BLUE, LINE*0.8)
        fill(ell(5, -1, 5, 3, 14), P.FOX)
        shape([(12, 5), (22, 3), (12, 2.6)], 0.2, LINE*0.6)
        dot(9, 5, 0.9, 0.0)


def jerab(x, y, s=1.0):
    """the wooden treadwheel crane copied from the Bible of Václav IV.: a big wheel, a mast and a jib"""
    with T(x, y, s):
        stroke(ell(-10, 24, 22, 22, 36), LINE*1.6, closed=True, g=P.CASTLE_WOOD, taper=False)
        for k in range(8):
            a = math.radians(k*22.5)
            stroke([(-10 - math.cos(a)*22, 24 - math.sin(a)*22), (-10 + math.cos(a)*22, 24 + math.sin(a)*22)], LINE*0.6, g=P.CASTLE_WOOD)
        stroke([(-34, 0), (14, 0)], LINE*2)
        stroke([(10, 0), (10, 70)], LINE*2.4, g=P.CASTLE_WOOD)
        stroke([(10, 64), (44, 48)], LINE*2.0, g=P.CASTLE_WOOD)
        stroke([(44, 48), (44, 20)], LINE*0.6)
        shape(_rect(38, 10, 50, 20), P.CASTLE_STONE, LINE*0.7)


# ================================================================== paní kastelánka
KASTEL = dict(H=120, hr=10.3, hy=109.4, sh_y=94.6, sh_w=11.8, hip=55, knee=29.5, ankle=5, leg_w=(7, 5.4),
              arm_w=(6.2, 5.4), up=18.5, fo=16.5)


def _k_neck(k, w=2.7):
    shape([(-w, k.hy - k.hr + 2), (w, k.hy - k.hr + 2), (w + 0.3, k.sh_y + 0.5), (-w - 0.3, k.sh_y + 0.5)], P.SKIN, 0)
    stroke([(-w, k.hy - k.hr + 2.5), (-w - 0.3, k.sh_y + 0.8)], LINE*0.8)
    stroke([(w, k.hy - k.hr + 2.5), (w + 0.3, k.sh_y + 0.8)], LINE*0.8)


def kastelanka(x, y, s=1.0, flip=False, left="down", right="down", mood="happy", look=(0, 0), item=None, shadow=True,
               legs="stand", keys=True):
    """paní kastelánka: a friendly woman in a light blue blouse with rolled sleeves, a dark blue skirt, flat shoes,
    a short reddish-brown bob with a fringe, a lanyard with a badge, the big key ring at her belt"""
    k = Person(**KASTEL)
    if shadow: cast_shadow(x, y, 16*s, 2.8*s)
    r, cy = k.hr, k.hy
    with T(x, y, s, flip):
        back = bez((-r*1.04, cy + r*0.3), (-r*1.22, cy - r*0.3), (-r*1.18, cy - r*0.8), (-r*0.9, cy - r*0.95)) + \
               [(r*0.9, cy - r*0.95)] + bez((r*0.9, cy - r*0.95), (r*1.18, cy - r*0.8), (r*1.22, cy - r*0.3), (r*1.04, cy + r*0.3))
        shape(back, P.KASTEL_HAIR)
        draw_legs(k, legs, 0.95, boots=P.KASTEL_SHOES, boot_top=k.ankle + 3)
        draw_arm(k, -1, left, P.KASTEL_TOP)
        skirt = [(-12.5, 58), (12.5, 58)] + bez((12.5, 58), (14.5, 46), (16, 36), (17, 26)) + \
                bez((17, 26), (6, 24), (-6, 24), (-17, 26)) + bez((-17, 26), (-16, 36), (-14.5, 46), (-12.5, 58))
        form(skirt, P.KASTEL_SKIRT, sdx=-2, sdy=1)
        tors = bez((-5, k.sh_y + 2.8), (-9, k.sh_y + 2.5), (-k.sh_w - 1.3, k.sh_y + 0.5), (-k.sh_w - 1.8, k.sh_y - 4)) + \
               bez((-k.sh_w - 1.8, k.sh_y - 4), (-13.5, 76), (-13, 66), (-12.8, 57)) + [(12.8, 57)] + \
               bez((12.8, 57), (13, 66), (13.5, 76), (k.sh_w + 1.8, k.sh_y - 4)) + \
               bez((k.sh_w + 1.8, k.sh_y - 4), (k.sh_w + 1.3, k.sh_y + 0.5), (9, k.sh_y + 2.5), (5, k.sh_y + 2.8))
        form(tors, P.KASTEL_TOP, sdx=-2.2, sdy=1.2)
        shape(_rect(-13, 55.5, 13, 59), 0.3, LINE*0.7)              # belt
        for by in (84, 76, 68): shape(ell(0.5, by, 0.9, 0.9, 10), 1.0, LINE*0.4)
        stroke([(0.5, k.sh_y + 1), (0.5, 59)], LINE*0.6)
        for sx in (-1, 1):
            shape([(sx*1, k.sh_y + 1.5), (sx*7.5, k.sh_y + 2.5), (sx*8, k.sh_y - 4), (sx*2.5, k.sh_y - 6)], P.KASTEL_TOP, LINE*0.7)
        stroke(bez((-6, k.sh_y + 1), (-3, 82), (3, 82), (6, k.sh_y + 1)), LINE*0.6, g=P.DYE_RED)   # lanyard
        shape(rrect(-3.5, 74, 7, 8, 1.2), 1.0, LINE*0.6)
        star(0, 78, 2, 0.4)
        if keys:
            stroke([(9, 57), (10, 50)], LINE*0.8, g=0.3)
            svazek(10, 46, 0.9)
        h, fa = draw_arm(k, 1, right, P.KASTEL_TOP)
        if item: item(*h)
        _k_neck(k)
        shape(head_outline(k), P.SKIN)
        face(0, cy, r, mood, look)
        cap = bez((-r*1.06, cy - r*0.35), (-r*1.18, cy + r*1.2), (r*1.18, cy + r*1.2), (r*1.06, cy - r*0.35)) + \
              bez((r*1.06, cy - r*0.35), (r*0.95, cy + r*0.25), (r*0.7, cy + r*0.4), (r*0.4, cy + r*0.42)) + \
              [(r*0.2, cy + r*0.3), (0, cy + r*0.44), (-r*0.2, cy + r*0.3), (-r*0.4, cy + r*0.44)] + \
              bez((-r*0.4, cy + r*0.44), (-r*0.7, cy + r*0.4), (-r*0.95, cy + r*0.25), (-r*1.06, cy - r*0.35))
        shape(cap, P.KASTEL_HAIR)
        for xx in (-0.6, -0.2, 0.2, 0.6):
            stroke(bez((r*xx, cy + r*0.5), (r*xx*1.05, cy + r*0.8), (r*xx*0.9, cy + r*1.0), (r*xx*0.6, cy + r*1.1)), LINE*0.4, g=0.2)


# ================================================================== the activity page
def mini_tower(q, variant=0, seed=41):
    """one of the two "spot the difference" pictures: the tower, a jackdaw, a bear in the moat; variant 1 has 5 changes"""
    _panel_fill(q, P.SUMMER_SKY)
    if variant == 0: cloud(q.X(0.25), q.Y(0.86), 0.4)
    gy = q.Y(0.3)
    fill(_rect(q.x - 5, q.y - 5, q.x + q.w + 5, gy), P.SPRING_GRASS)
    s_([(q.x - 5, gy), (q.x + q.w + 5, gy)], BG)
    tower(q.X(0.5), gy, q.w*0.42, q.h*0.56, seed, roof=True, door=variant == 0)
    if variant == 0:
        kavka(q.X(0.5) - q.w*0.12, gy + q.h*0.56 + 1, 0.55, pose="perch")
    if variant == 0:
        kavka(q.X(0.85), q.Y(0.86), 0.45, pose="fly")
    brtnik(q.X(0.18), q.Y(0.04), 0.42, pose="walk")
    if variant == 1:
        rohlik(q.X(0.86), q.Y(0.08), 0.8)
