"""Art for issue 2 "Tajemství starého klíče" (and game 2 later): the attic, the barn owls,
děda's childhood club (young děda, Franta, Věrka), the chest, the torn map, the bedroom."""
import math, random
import lib
from lib import ell, bez, rrect, resample
import palette as P
from style3 import *
from style3 import C, _SC, draw_arm, draw_legs, head_outline, face, notch, hand
from chars3 import Person, TONDA, _neck, star
from scenes3 import planks, floor, BG, s_, sh_


# ------------------------------------------------------------------ owls (sova pálená)
def _heart_face(cx, cy, r):
    """barn owl's heart-shaped face disc, tip at the bottom"""
    return bez((cx, cy + r*0.55), (cx - r*0.35, cy + r*1.05), (cx - r*1.15, cy + r*0.9), (cx - r*1.05, cy + r*0.1)) + \
           bez((cx - r*1.05, cy + r*0.1), (cx - r*0.95, cy - r*0.55), (cx - r*0.35, cy - r*0.95), (cx, cy - r*1.15)) + \
           bez((cx, cy - r*1.15), (cx + r*0.35, cy - r*0.95), (cx + r*0.95, cy - r*0.55), (cx + r*1.05, cy + r*0.1)) + \
           bez((cx + r*1.05, cy + r*0.1), (cx + r*1.15, cy + r*0.9), (cx + r*0.35, cy + r*1.05), (cx, cy + r*0.55))


def _owl_eyes(cx, cy, r, mood):
    for sx in (-1, 1):
        ex = cx + sx*r*0.42
        if mood == "sleepy":
            stroke(bez((ex - r*0.2, cy), (ex - r*0.07, cy - r*0.13), (ex + r*0.07, cy - r*0.13), (ex + r*0.2, cy)), LINE*0.9)
        else:
            k = 1.3 if mood == "wide" else 1.0
            fill(ell(ex, cy, r*0.16*k, r*0.19*k, 16), 0.0)
            dot(ex + r*0.05, cy + r*0.07, r*0.055*k, 1.0)


def owl(x, y, s=1.0, flip=False, mood="open"):
    """adult barn owl standing (local height ~46); mood: open, wide, sleepy"""
    with T(x, y, s, flip):
        for sx in (-1, 1):
            for tx in (-1.5, 0, 1.5):
                stroke([(sx*4 + tx, 2), (sx*4 + tx*1.4, -1)], LINE*0.9)
        body = bez((-12, 6), (-14, 20), (-11, 30), (0, 32)) + bez((0, 32), (11, 30), (14, 20), (12, 6)) + \
               bez((12, 6), (8, 1), (-8, 1), (-12, 6))
        form(body, P.OWL, sdx=-2, sdy=1)
        belly = bez((-7, 5), (-8.5, 16), (-6, 26), (0, 27)) + bez((0, 27), (6, 26), (8.5, 16), (7, 5)) + \
                bez((7, 5), (4, 2.5), (-4, 2.5), (-7, 5))
        shape(belly, P.OWL_BELLY, LINE*0.7)
        for (dx, dy) in ((-3, 20), (2, 17), (-1, 12), (4, 10), (-4, 8), (1, 6)):
            dot(dx, dy, 0.55, 0.35)
        for sx in (-1, 1):
            wing = bez((sx*11, 28), (sx*15, 20), (sx*14, 9), (sx*10, 2)) + bez((sx*10, 2), (sx*8, 10), (sx*8, 20), (sx*11, 28))
            shape(wing, P.OWL_WING, LINE*0.8)
            for (dx, dy) in ((12.2, 20), (11.5, 13), (10.5, 7)):
                dot(sx*dx, dy, 0.5, 0.95)
        head = ell(0, 38, 12.5, 11, 36)
        form(head, P.OWL, sdx=-1.5, sdy=1)
        fc = _heart_face(0, 37, 9.5)
        shape(fc, P.OWL_FACE, LINE*0.8)
        _owl_eyes(0, 38, 9.5, mood)
        shape([(-1.1, 35), (1.1, 35), (0, 31.5)], P.OWL_BEAK, LINE*0.6)


def owlet(x, y, s=1.0, flip=False, mood="open"):
    """fluffy barn owl chick (local height ~26); mood: open, sleepy, hiss (beak open)"""
    with T(x, y, s, flip):
        body = notch(ell(0, 9, 9.5, 9.5, 40), 0.9, 3)
        form(body, P.OWLET, sdx=-1.6, sdy=1, sh=0.1)
        for sx in (-1, 1):
            stroke(bez((sx*6, 12), (sx*7.5, 8), (sx*7, 4), (sx*5, 2)), LINE*0.6, g=0.55)
        head = notch(ell(0, 20.5, 8.5, 7.8, 36), 0.8, 3)
        form(head, P.OWLET, sdx=-1.2, sdy=0.8, sh=0.1)
        shape(_heart_face(0, 20, 5.6), P.OWL_FACE, LINE*0.6)
        _owl_eyes(0, 20.8, 5.6, mood if mood != "hiss" else "wide")
        if mood == "hiss":
            shape(ell(0, 17, 1.4, 1.8, 12), P.MOUTH, LINE*0.6)
            shape([(-1.0, 18.4), (1.0, 18.4), (0, 16.8)], P.OWL_BEAK, LINE*0.5)
        else:
            shape([(-0.8, 19), (0.8, 19), (0, 16.8)], P.OWL_BEAK, LINE*0.5)
        for sx in (-1, 1):
            stroke([(sx*2.5, 0.2), (sx*2.8, -1.5)], LINE*0.8)


def feather(x, y, s=1.0, rot=0):
    with T(x, y, s, rot=rot):
        vane = bez((0, 0), (-4.5, 6), (-4, 16), (0, 24)) + bez((0, 24), (4, 16), (4.5, 6), (0, 0))
        shape(vane, P.FEATHER, LINE*0.7)
        stroke([(0, -4), (0, 22)], LINE*0.6)
        for yy in (6, 11, 16):
            stroke([(0, yy), (-3, yy + 3)], LINE*0.35); stroke([(0, yy - 2), (3, yy + 1)], LINE*0.35)


def pellet(x, y, s=1.0, rot=0):
    """owl pellet: small grey fuzzy capsule"""
    with T(x, y, s, rot=rot):
        shape(notch(ell(0, 0, 7, 3.6, 30), 0.5, 2), P.PELLET, LINE*0.7)
        for dx in (-4, -1, 2, 4.5):
            stroke([(dx, -1.5), (dx + 1.2, 1.4)], LINE*0.35, g=0.25)


# ------------------------------------------------------------------ děda's childhood club (young kids)
def _kid_head(k, mood, look, ears=True):
    r = k.hr; cy = k.hy
    if ears:
        for sx in (-1, 1): shape(ell(sx*r*0.98, cy - r*0.05, r*0.2, r*0.3, 14), P.SKIN, LINE*0.8)
    shape(head_outline(k), P.SKIN)
    face(0, cy, r, mood, look)


def _shoes(k, legs):
    for ax in ((-9, 7.2) if legs == "walk" else (-4.2, 4.2)):
        ay = k.ankle; bt = ay + 2.5
        b = [(ax - 3.0, bt), (ax + 3.0, bt)] + bez((ax + 3.0, bt), (ax + 3.1, ay), (ax + 3.5, 2.2), (ax + 6.8, 2)) + \
            bez((ax + 6.8, 2), (ax + 7.6, 1.8), (ax + 7.4, 0), (ax + 6.5, 0)) + [(ax - 3.2, 0)] + \
            bez((ax - 3.2, 0), (ax - 3.6, 1), (ax - 3.2, ay), (ax - 3.0, bt))
        form(b, P.KID_SHOES, sh=0.12)


def young(x, y, s=1.0, who="deda", flip=False, left="down", right="down", mood="happy", look=(0, 0),
          item=None, shadow=True, legs="stand"):
    """děda and his friends as children, about 60 years ago. who: deda, franta, verka"""
    k = Person(**TONDA)
    if shadow: cast_shadow(x, y, 15*s, 2.6*s)
    with T(x, y, s, flip):
        r = k.hr; cy = k.hy
        if who == "verka":
            # pigtails behind the head
            for sx in (-1, 1):
                pig = bez((sx*r*0.9, cy - r*0.1), (sx*r*1.6, cy - r*0.6), (sx*r*1.7, cy - r*1.6), (sx*r*1.35, cy - r*2.3)) + \
                      bez((sx*r*1.35, cy - r*2.3), (sx*r*1.05, cy - r*1.7), (sx*r*1.05, cy - r*0.8), (sx*r*0.7, cy - r*0.3))
                shape(pig, P.VERKA_HAIR)
                with T(sx*r*1.35, cy - r*0.55, 1):
                    for bx in (-1, 1):
                        shape([(0, 0), (bx*4, 2.4), (bx*4, -2.4)], P.VERKA_BOW, LINE*0.7)
                    dot(0, 0, 1.0, 0.3)
            draw_legs(k, legs, P.TIGHTS, boots=P.KID_SHOES, boot_top=k.ankle + 2.5)
            draw_arm(k, -1, left, P.VERKA_DRESS)
            dress = bez((-4.5, k.sh_y + 2.6), (-8, k.sh_y + 2.4), (-k.sh_w - 1.1, k.sh_y + 0.5), (-k.sh_w - 1.5, k.sh_y - 3.5)) + \
                    bez((-k.sh_w - 1.5, k.sh_y - 3.5), (-12, 60), (-15, 45), (-17, 30)) + \
                    bez((-17, 30), (-6, 28), (6, 28), (17, 30)) + \
                    bez((17, 30), (15, 45), (12, 60), (k.sh_w + 1.5, k.sh_y - 3.5)) + \
                    bez((k.sh_w + 1.5, k.sh_y - 3.5), (k.sh_w + 1.1, k.sh_y + 0.5), (8, k.sh_y + 2.4), (4.5, k.sh_y + 2.6))
            fill(dress, P.VERKA_DRESS)
            C.saveState(); C.clipPath(poly(dress), stroke=0, fill=0)
            for yy in range(30, 80, 5):
                for xx in range(-18, 19, 5):
                    dot(xx + (2.5 if (yy//5) % 2 else 0), yy, 0.7, 0.95)
            C.restoreState()
            offset_shadow(dress, -2, 1, 0.12); stroke(dress, LINE, closed=True)
            shape(bez((-5, k.sh_y + 2.2), (-2, k.sh_y - 1.5), (2, k.sh_y - 1.5), (5, k.sh_y + 2.2)) + [(0, k.sh_y + 1)], 1.0, LINE*0.7)
            h, fa = draw_arm(k, 1, right, P.VERKA_DRESS)
            if item: item(*h)
            _neck(k, 2.4)
            _kid_head(k, mood, look, ears=False)
            cap = bez((-r*1.02, cy + r*0.05), (-r*1.1, cy + r*1.2), (r*1.1, cy + r*1.2), (r*1.02, cy + r*0.05)) + \
                  bez((r*1.02, cy + r*0.05), (r*0.8, cy + r*0.45), (r*0.45, cy + r*0.55), (0, cy + r*0.62)) + \
                  bez((0, cy + r*0.62), (-r*0.45, cy + r*0.55), (-r*0.8, cy + r*0.45), (-r*1.02, cy + r*0.05))
            shape(cap, P.VERKA_HAIR)
            stroke(bez((0, cy + r*1.12), (0.3, cy + r*0.95), (0.2, cy + r*0.8), (0, cy + r*0.64)), LINE*0.5, g=0.7)
            return
        # boys: bare knees, knee socks, short trousers with braces
        draw_legs(k, legs, P.SKIN, boots=P.KNEE_SOCKS, boot_top=k.knee - 2)
        _shoes(k, legs)
        top_g = P.YOUNG_SHIRT if who == "deda" else P.FRANTA_SWEATER
        draw_arm(k, -1, left, top_g)
        tors = bez((-4.5, k.sh_y + 2.6), (-8, k.sh_y + 2.4), (-k.sh_w - 1.1, k.sh_y + 0.5), (-k.sh_w - 1.5, k.sh_y - 3.5)) + \
               bez((-k.sh_w - 1.5, k.sh_y - 3.5), (-12.5, 62), (-12.8, 54), (-12.5, 48)) + [(12.5, 48)] + \
               bez((12.5, 48), (12.8, 54), (12.5, 62), (k.sh_w + 1.5, k.sh_y - 3.5)) + \
               bez((k.sh_w + 1.5, k.sh_y - 3.5), (k.sh_w + 1.1, k.sh_y + 0.5), (8, k.sh_y + 2.4), (4.5, k.sh_y + 2.6))
        form(tors, top_g, sdx=-2, sdy=1)
        if who == "franta":
            for yy in (60, 66, 72):
                stroke([(-11, yy), (11, yy)], LINE*0.5, g=0.35)
        shorts = [(-12.8, 50), (12.8, 50), (13.2, 36), (1.5, 36), (0, 42), (-1.5, 36), (-13.2, 36)]
        form(shorts, P.SHORTS, sdx=-1.8, sdy=1)
        if who == "deda":
            for sx in (-1, 1):
                stroke([(sx*6, 50), (sx*6.5, k.sh_y + 1)], LINE*2.2, g=0.0)
                stroke([(sx*6, 50), (sx*6.5, k.sh_y + 1)], LINE*1.0, g=P.SHORTS)
                shape(ell(sx*6, 48.5, 1.0, 1.0, 10), 0.9, LINE*0.5)
        h, fa = draw_arm(k, 1, right, top_g)
        if item: item(*h)
        _neck(k, 2.6)
        _kid_head(k, mood, look)
        if who == "deda":
            # a boy's flat cap, like děda wears today
            tuft = [(-r*0.95, cy + r*0.35), (-r*1.05, cy + r*0.0), (-r*0.8, cy + r*0.25), (-r*0.7, cy + r*0.5)]
            shape(tuft, P.TONDA_HAIR, LINE*0.7)
            capb = bez((-r*1.05, cy + r*0.35), (-r*1.15, cy + r*1.25), (r*0.5, cy + r*1.45), (r*1.05, cy + r*0.65)) + \
                   [(r*1.6, cy + r*0.45), (r*1.55, cy + r*0.3), (r*1.0, cy + r*0.35)]
            form(capb, P.FLAT_CAP, sdx=-1.5, sdy=1)
            stroke(bez((-r*0.2, cy + r*1.3), (r*0.2, cy + r*1.0), (r*0.6, cy + r*0.8), (r*1.0, cy + r*0.62)), LINE*0.6)
        else:
            hair = [(-r*1.02, cy + r*0.1), (-r*1.1, cy + r*0.8), (-r*0.6, cy + r*1.2), (0, cy + r*1.25), (r*0.6, cy + r*1.2),
                    (r*1.1, cy + r*0.8), (r*1.02, cy + r*0.1), (r*0.8, cy + r*0.55), (r*0.3, cy + r*0.7), (-r*0.2, cy + r*0.55),
                    (-r*0.6, cy + r*0.7)]
            shape(hair, P.FRANTA_HAIR)
            for sx in (-1, 1):   # round glasses
                stroke(ell(sx*r*0.4, cy - r*0.02, r*0.26, r*0.26, 24), LINE*0.8, closed=True)
            stroke([(-r*0.14, cy), (r*0.14, cy)], LINE*0.7)


# ------------------------------------------------------------------ props
def chest(x, y, s=1.0, open_=False, dark_inside=0.18):
    """old wooden chest with a star on its lock (local width 140)"""
    with T(x, y, s):
        if open_:
            # lid tipped back: we see its darker inside face above the box
            lid = [(-70, 58), (70, 58), (62, 104), (-62, 104)]
            form(lid, P.CHEST_BAND, w=1.4, sh=0)
            shape([(-64, 62), (64, 62), (57, 100), (-57, 100)], P.CHEST, 0.8)
            fill([(-68, 49), (68, 49), (68, 58), (-68, 58)], dark_inside)
        form([(-70, 0), (70, 0), (70, 55), (-70, 55)], P.CHEST, w=1.4, sdx=6, sdy=0)
        for k_ in range(1, 4): s_([(-70, k_*13.7), (70, k_*13.7)], BG*0.6)
        if not open_:
            shape(ell(0, 55, 70, 30, 40, 0, 180) + [(-70, 55)], P.CHEST, 1.4)
            for k_ in (-45, 45): shape([(k_ - 6, 0), (k_ + 6, 0), (k_ + 6, 80), (k_ - 6, 80)], P.CHEST_BAND, 1.0)
        else:
            for k_ in (-45, 45): shape([(k_ - 6, 0), (k_ + 6, 0), (k_ + 6, 55), (k_ - 6, 55)], P.CHEST_BAND, 1.0)
        shape(rrect(-12, 36, 24, 26, 4), P.BRASS, 1.1)
        star(0, 50, 7, 0.2 if not open_ else P.TAG_STAR)
        fill(ell(0, 42, 2, 3, 10), 0.0)


def ladder(x, y0, y1, w=34, g=P.LADDER):
    for sx in (-1, 1):
        tube([(x + sx*w/2, y0), (x + sx*w/2, y1)], 5, 5, g, lw=BG, sh=0)
    yy = y0 + 14
    while yy < y1 - 4:
        shape([(x - w/2, yy), (x + w/2, yy), (x + w/2, yy + 4), (x - w/2, yy + 4)], g, BG)
        yy += 24


def sled(x, y, s=1.0):
    with T(x, y, s):
        stroke(bez((-40, 0), (30, 0), (44, 0), (46, 12)), BG*3.2); stroke(bez((-40, 0), (30, 0), (44, 0), (46, 12)), BG*1.6, g=P.METAL)
        for lx in (-28, 22): s_([(lx, 0), (lx, 12)], BG*2.2)
        sh_([(-42, 12), (40, 12), (40, 18), (-42, 18)], P.SLED)
        for k_ in (-24, -4, 16): s_([(k_, 12), (k_, 18)], BG*0.5)


def suitcase(x, y, w=60, h=40):
    form(rrect(x, y, w, h, 4), P.SUITCASE, w=BG, sdx=3, sdy=0)
    stroke(bez((x + w*0.35, y + h), (x + w*0.35, y + h + 9), (x + w*0.65, y + h + 9), (x + w*0.65, y + h)), BG*1.6)
    for bx in (0.2, 0.8): sh_([(x + w*bx - 2, y), (x + w*bx + 2, y), (x + w*bx + 2, y + h), (x + w*bx - 2, y + h)], 0.3, BG*0.6)


def tin(x, y, s=1.0, open_=False):
    """small tin box with a star on the lid"""
    with T(x, y, s):
        form(rrect(-16, 0, 32, 16, 2), P.TIN, sdx=2, sdy=0)
        if open_:
            shape([(-16, 16), (16, 16), (19, 30), (-13, 30)], P.TIN, LINE)
            fill([(-14, 14), (14, 14), (14, 16), (-14, 16)], 0.2)
        else:
            shape(rrect(-17, 14, 34, 5, 2), P.TIN, LINE)
            star(0, 8, 4, 0.95)


def _torn_edge(x, y0, y1, seed, amp=4):
    r = random.Random(seed); pts = []; yy = y1
    while yy > y0:
        pts.append((x + r.uniform(-amp, amp), yy)); yy -= r.uniform(4, 8)
    pts.append((x, y0))
    return pts


def map_half(x, y, s=1.0, side="L", rot=0):
    """one half of Klub Hvězdička's treasure map (local 60 x 80); both halves join at x=0/60"""
    with T(x, y, s, rot=rot):
        if side == "L":
            outline = [(0, 0), (60, 0)] + _torn_edge(60, 0, 80, 5)[::-1][1:] + [(0, 80)]
        else:
            outline = _torn_edge(60, 0, 80, 5) + [(120, 0), (120, 80)]
        shape(outline, P.MAP_PAPER, LINE*0.9)
        C.saveState(); C.clipPath(poly(outline), stroke=0, fill=0)
        # dashed path from the house (left half) to the pond (right half)
        path = resample(bez((14, 20), (40, 40), (70, 10), (96, 44)), 1.0)
        for i in range(0, len(path) - 4, 9):
            stroke(path[i:i + 5], LINE*0.9, g=P.MAP_INK)
        # house
        shape([(6, 12), (20, 12), (20, 22), (6, 22)], 1.0, LINE*0.7)
        shape([(4, 22), (13, 29), (22, 22)], P.MAP_PAPER, LINE*0.7)
        # tree
        stroke([(38, 58), (38, 66)], LINE*0.8, g=P.MAP_INK)
        stroke(ell(38, 70, 6, 5, 16), LINE*0.8, closed=True, g=P.MAP_INK)
        # pond + reeds
        stroke(ell(98, 52, 15, 9, 30), LINE*0.9, closed=True, g=P.MAP_INK)
        for rx in (84, 87, 111):
            stroke([(rx, 60), (rx + 1, 67)], LINE*0.6, g=P.MAP_INK)
        # the X and the star
        stroke([(92, 34), (100, 42)], LINE*1.6, g=P.TAG_STAR); stroke([(100, 34), (92, 42)], LINE*1.6, g=P.TAG_STAR)
        star(108, 30, 3.5, P.TAG_STAR)
        C.restoreState()
        from letter import hand_text
        if side == "L":
            hand_text(4, 70, 50, "KLUB", "SHB", 7, align="left")
        else:
            hand_text(66, 70, 50, "HVĚZDIČKA", "SHB", 7, align="left")


def star_window(cx, cy, r=22, shutter=True):
    """the round attic window from inside: wooden shutter with a star cut out of it"""
    shape(ell(cx, cy, r + 5, r + 5, 40), P.ATTIC_BEAM, BG)
    if shutter:
        shape(ell(cx, cy, r, r, 40), P.SHUTTER, BG*0.8)
        for k_ in (-0.5, 0, 0.5): s_([(cx + r*k_, cy - r*0.85), (cx + r*k_, cy + r*0.85)], BG*0.4, g=0.2)
        star(cx, cy, r*0.62, 0.98, w=BG)
    else:
        shape(ell(cx, cy, r, r, 40), 0.95, BG*0.8)


def star_spot(cx, cy, r=18, alpha=0.75):
    """the star of sunlight the window throws on the floor (squashed by perspective)"""
    pts = []
    for i in range(10):
        a = math.pi/2 + i*math.pi/5; rr = r if i % 2 == 0 else r*0.45
        pts.append((cx + math.cos(a)*rr*1.3, cy + math.sin(a)*rr*0.45))
    fill(pts, P.SUNBEAM, alpha)


def attic(p, floor_y=0.2, window=None, dark=0.0, seed=3, beam=0.8, herbs_=True):
    """attic interior. window=(fx, fy) puts the star window there. dark: 0..1 shadow over everything"""
    planks(p, P.ATTIC_WALL, 26, seed)
    floor(p, p.Y(floor_y), P.ATTIC_FLOOR)
    # sloping roof on both sides with rafters
    for sx in (-1, 1):
        x_out = p.x if sx < 0 else p.x + p.w
        x_in = p.X(0.5 + sx*0.26)
        roof = [(x_out, p.Y(floor_y + 0.18)), (x_in, p.y + p.h + 2), (x_out, p.y + p.h + 2)]
        form(roof, P.ATTIC_ROOF, w=BG, sh=0)
        for t in (0.25, 0.55, 0.85):
            bx0 = x_out + (x_in - x_out)*t; by0 = p.y + p.h + 2
            s_([(bx0, by0), (x_out, p.Y(floor_y + 0.18) + (p.y + p.h - p.Y(floor_y + 0.18))*t)], BG*0.5)
        tube([(x_out, p.Y(floor_y + 0.18)), (x_in, p.y + p.h + 4)], 11, 11, P.ATTIC_BEAM, lw=BG, sh=0)
    # tie beam across
    if beam:
        tube([(p.x - 4, p.Y(beam)), (p.x + p.w + 4, p.Y(beam))], 10, 10, P.ATTIC_BEAM, lw=BG, sh=0)
        r = random.Random(seed)
        for k_ in range(int(p.w/170) + 1):
            dot(p.X(r.uniform(0.05, 0.95)), p.Y(beam) + r.uniform(-2, 2), 0.9, 0.2)
        if herbs_:
            for fx in (0.08, 0.2):
                herbs(p.X(fx + r.uniform(-0.03, 0.03)), p.Y(beam) - 5, 0.9, seed=seed + int(fx*100))
    if window:
        star_window(p.X(window[0]), p.Y(window[1]), min(p.w, p.h)*0.09)
    if dark:
        fill([(p.x, p.y), (p.x + p.w, p.y), (p.x + p.w, p.y + p.h), (p.x, p.y + p.h)], 0.0, dark)


def beam_light(x0, y0, x1a, y1a, x1b, y1b, alpha=0.4):
    """torch or sun beam: a bright wedge"""
    fill([(x0, y0), (x1a, y1a), (x1b, y1b)], 1.0, alpha)


def cobweb(x, y, r=20, flip=False):
    sx = -1 if flip else 1
    for a in (0, 30, 60, 90):
        ra = math.radians(a)
        stroke([(x, y), (x + sx*math.cos(ra)*r, y - math.sin(ra)*r)], 0.4, g=0.3)
    for rr in (0.35, 0.65, 0.95):
        pts = [(x + sx*math.cos(math.radians(a))*r*rr, y - math.sin(math.radians(a))*r*rr) for a in range(0, 91, 15)]
        stroke(pts, 0.35, g=0.3)


# ------------------------------------------------------------------ bedroom
def bedroom(p, night=True):
    fill([(p.x, p.y), (p.x + p.w, p.y), (p.x + p.w, p.y + p.h), (p.x, p.y + p.h)], P.BEDROOM_WALL)
    for xx in range(int(p.x) + 10, int(p.x + p.w), 22):
        for yy in range(int(p.y) + 10, int(p.y + p.h), 22):
            star(xx + ((yy//22) % 2)*11, yy, 2.2, 0.8, w=0.3)
    if night:
        fill([(p.x, p.y), (p.x + p.w, p.y), (p.x + p.w, p.y + p.h), (p.x, p.y + p.h)], 0.0, 0.28)


def bed_back(cx, bw, waist_y, top_y, pillow_y, pillow_r=16, pillows=(-0.24, 0.24)):
    """bed seen from its foot end: headboard and pillows behind the kids. Draw the kids next, then bed_front()"""
    form(rrect(cx - bw/2, waist_y - 10, bw, top_y - waist_y + 10, 14), P.BED, w=BG*1.2, sh=0)
    for k_ in (0.25, 0.5, 0.75):
        s_([(cx - bw/2 + bw*k_, waist_y), (cx - bw/2 + bw*k_, top_y - 8)], BG*0.5)
    for sx in pillows:
        pw = bw*(0.2 if len(pillows) > 1 else 0.3)
        shape(ell(cx + bw*sx, pillow_y, pw, pillow_r, 30), P.PILLOW, BG)
        s_(bez((cx + bw*sx - pw*0.5, pillow_y - pillow_r*0.2), (cx + bw*sx - pw*0.2, pillow_y + pillow_r*0.1),
               (cx + bw*sx + pw*0.2, pillow_y + pillow_r*0.1), (cx + bw*sx + pw*0.5, pillow_y - pillow_r*0.2)), BG*0.4)


def bed_side(x0, x1, top):
    """a bed along the back wall seen from the side, head end on the right"""
    for lx in (x0 + 4, x1 - 8):
        sh_([(lx, top - 34), (lx + 5, top - 34), (lx + 5, top - 20), (lx, top - 20)], P.BED)
    form([(x0, top - 22), (x1, top - 22), (x1, top - 10), (x0, top - 10)], P.BED, w=BG*1.2, sh=0)
    sh_([(x0 + 2, top - 10), (x1 - 2, top - 10), (x1 - 2, top), (x0 + 2, top)], 0.97)
    form(rrect(x1 - 2, top - 34, 12, 100, 5), P.BED, w=BG*1.2, sh=0)
    form(rrect(x0 - 10, top - 34, 12, 62, 5), P.BED, w=BG*1.2, sh=0)
    for xx in (x1 + 4, x0 - 4): dot(xx, top + (58 if xx > x0 else 22), 2.2, 0.35)
    shape(ell(x1 - 26, top + 10, 24, 11, 30), P.PILLOW, BG)


def blanket_side(x0, x_end, top, waist_y, seed=3):
    """the blanket over a kid sitting up in bed_side(): rises from the foot end to her waist"""
    r = random.Random(seed)
    bl = [(x0 - 3, top - 16), (x0 - 3, top + 6)] + \
         bez((x0 - 3, top + 6), (x0 + (x_end - x0)*0.3, top + 16 + r.uniform(-2, 2)),
             (x0 + (x_end - x0)*0.7, top + 10), (x_end - 6, waist_y)) + \
         bez((x_end - 6, waist_y), (x_end + 2, waist_y - 2), (x_end + 4, top), (x_end + 2, top - 16))
    fill(bl, P.BLANKET)
    C.saveState(); C.clipPath(poly(bl), stroke=0, fill=0)
    for xx in range(int(x0), int(x_end) + 16, 14):
        for yy in range(int(top - 16), int(waist_y + 10), 14):
            dot(xx + ((yy//14) % 2)*7, yy, 1.6, P.BLANKET_DOT)
    C.restoreState()
    stroke(bl, BG*1.2, closed=True)
    s_(bez((x0 + 20, top + 2), (x0 + 40, top + 8), (x0 + 70, top + 6), (x0 + 90, top + 1)), BG*0.5)


def bunting(p, y=0.93, n=11, seed=4):
    """a garland of little flags across the top of the room"""
    r = random.Random(seed)
    pts = bez((p.x - 5, p.Y(y)), (p.X(0.3), p.Y(y) - 20), (p.X(0.7), p.Y(y) - 20), (p.x + p.w + 5, p.Y(y)), 40)
    stroke(pts, 0.6, g=0.3)
    for i in range(1, n):
        a = pts[int(i*len(pts)/n)]; b = pts[min(len(pts) - 1, int(i*len(pts)/n) + 2)]
        g = (0.95, 0.75, 0.55)[i % 3]
        shape([a, b, ((a[0] + b[0])/2, a[1] - 13)], g, 0.6)


def shelf_toys(x, y, w=70):
    """a small wall shelf with books and a toy"""
    sh_([(x, y), (x + w, y), (x + w, y + 4), (x, y + 4)], P.SHELF)
    for i, (bw_, bh, g) in enumerate(((6, 18, 0.5), (5, 22, 0.8), (7, 16, 0.35), (5, 20, 0.65))):
        bx = x + 4 + sum((6, 5, 7, 5)[:i]) + i
        sh_([(bx, y + 4), (bx + bw_, y + 4), (bx + bw_, y + 4 + bh), (bx, y + 4 + bh)], g, BG*0.6)
    # a little plush bear
    bx, by = x + w - 16, y + 4
    shape(ell(bx, by + 7, 7, 7, 20), 0.7, BG*0.7)
    shape(ell(bx, by + 18, 6, 5.5, 20), 0.7, BG*0.7)
    for sx in (-1, 1): shape(ell(bx + sx*4.5, by + 22.5, 2.2, 2.2, 12), 0.7, BG*0.6)
    dot(bx - 2, by + 19, 0.7); dot(bx + 2, by + 19, 0.7); dot(bx, by + 16.5, 0.9)


def kids_drawing(x, y, w=40, h=30, rot=4):
    """a child's drawing pinned to the wall: house, sun and a stick dog"""
    with T(x, y, 1, rot=rot):
        shape([(0, 0), (w, 0), (w, h), (0, h)], 1.0, BG*0.8)
        dot(w/2, h - 2, 1.2, 0.3)
        stroke([(4, 4), (16, 4), (16, 13), (10, 19), (4, 13), (4, 4)], 0.5)
        stroke(ell(w - 8, h - 9, 4, 4, 12), 0.5, closed=True)
        for a in range(0, 360, 60):
            ra = math.radians(a); stroke([(w - 8 + math.cos(ra)*5.5, h - 9 + math.sin(ra)*5.5), (w - 8 + math.cos(ra)*7.5, h - 9 + math.sin(ra)*7.5)], 0.4)
        stroke([(20, 6), (30, 6)], 0.5); stroke([(21, 6), (21, 2)], 0.5); stroke([(29, 6), (29, 2)], 0.5)
        stroke(ell(32, 8, 2.5, 2.2, 10), 0.5, closed=True)


def herbs(x, y, s=1.0, seed=1):
    """a bunch of dried herbs hanging upside down from a beam"""
    r = random.Random(seed)
    with T(x, y, s):
        stroke([(0, 0), (0, -8)], 0.6, g=0.3)
        shape([(-2.5, -8), (2.5, -8), (2.5, -12), (-2.5, -12)], 0.55, 0.5)
        for i in range(7):
            ang = -90 + r.uniform(-28, 28); L = r.uniform(14, 22)
            ex, ey = math.cos(math.radians(ang))*L, -12 + math.sin(math.radians(ang))*L
            stroke([(0, -12), (ex, ey)], 0.45, g=0.3)
            for t in (0.4, 0.65, 0.9):
                shape(ell(ex*t, -12 + (ey + 12)*t, 1.6, 2.6, 8, rot=ang + 90), P.LEAF_DARK if i % 2 else P.LEAF_LIGHT, 0.35)


def owl_box(x, y, s=1.0, peek=True):
    """nesting box for barn owls: planks, shingled roof, perch, an owlet peeking out"""
    with T(x, y, s):
        sh_([(-3, -8), (3, -8), (3, 44), (-3, 44)], P.BOOT)
        form([(-22, 0), (22, 0), (22, 40), (-22, 40)], P.BIRDHOUSE_WOOD, w=BG*1.2, sdx=3, sdy=0)
        for k_ in (-11, 0, 11): s_([(k_, 1), (k_, 39)], BG*0.5)
        for (nx, ny) in ((-18, 4), (18, 4), (-18, 36), (18, 36)): dot(nx, ny, 0.7, 0.3)
        shape(ell(0, 22, 9, 9, 24), 0.12, BG)
        if peek:
            C.saveState(); C.clipPath(poly(ell(0, 22, 9, 9, 24)), stroke=0, fill=0)
            owlet(0, 8, 0.75, mood="open")
            C.restoreState()
            stroke(ell(0, 22, 9, 9, 24), BG, closed=True)
        sh_([(-4, 9), (4, 9), (4, 11.5), (-4, 11.5)], P.BIRDHOUSE_PERCH)
        s_([(0, 10), (0, 6)], BG*1.2)
        roof = [(-28, 38), (28, 38), (26, 50), (-26, 50)]
        sh_(roof, P.BIRDHOUSE_ROOF)
        for row in (41, 45):
            for k_ in range(-26, 27, 6):
                s_(ell(k_ + (3 if row == 45 else 0), row, 3, 2, 8, 180, 360), BG*0.4)
        fill([(-22, 38), (22, 38), (22, 35), (-22, 35)], 0.0, 0.15)


def ivy(x0, y0, x1, y1, seed=2, n=14):
    r = random.Random(seed)
    stem = resample(bez((x0, y0), (x0 + (x1 - x0)*0.2, y0 + (y1 - y0)*0.4), (x1 - (x1 - x0)*0.3, y1 - (y1 - y0)*0.3), (x1, y1)), 1.0)
    stroke(stem, 0.7, g=0.3)
    from scenes3 import leaf
    for i in range(n):
        q = stem[int(i*(len(stem) - 1)/(n - 1))]
        leaf(q[0] + r.uniform(-5, 5), q[1] + r.uniform(-3, 3), 3.4 + r.random(), r.uniform(0, 360), P.LEAF_DARK if i % 2 else P.LEAF_LIGHT)


def gable_end(gx, gy, hw, eave_h, apex_h, seed=5, low_window=True, drainpipe=True, climber=True):
    """the cottage's gable end up close: plaster, stone plinth, wooden boards under the roof,
    tiled roof edge, the round star window. Returns the window centre and radius."""
    r = random.Random(seed)
    top_l, top_r, apex = (gx - hw, gy + eave_h), (gx + hw, gy + eave_h), (gx, gy + apex_h)
    wall = [(gx - hw, gy), (gx + hw, gy), top_r, top_l]
    form(wall, P.WALL, w=BG*1.2, sh=0)
    C.saveState(); C.clipPath(poly(wall), stroke=0, fill=0)
    for _ in range(9):   # plaster: little cracks and rough patches
        cx_, cy_ = gx + r.uniform(-hw, hw), gy + r.uniform(22, eave_h - 10)
        s_([(cx_, cy_), (cx_ + r.uniform(4, 9), cy_ - r.uniform(2, 6)), (cx_ + r.uniform(8, 14), cy_ - r.uniform(1, 9))], BG*0.45)
    for _ in range(5):
        cx_, cy_ = gx + r.uniform(-hw, hw), gy + r.uniform(22, eave_h - 10)
        fill(ell(cx_, cy_, r.uniform(8, 16), r.uniform(4, 7), 16), P.WALL_SHADE, 0.35)
    C.restoreState()
    base = [(gx - hw, gy), (gx + hw, gy), (gx + hw, gy + 18), (gx - hw, gy + 18)]
    sh_(base, P.STONE_BASE)
    xx = gx - hw
    while xx < gx + hw:
        w_ = r.uniform(14, 24); s_([(xx, gy), (xx, gy + 9)], BG*0.6); s_([(xx + w_/2, gy + 9), (xx + w_/2, gy + 18)], BG*0.6); xx += w_
    s_([(gx - hw, gy + 9), (gx + hw, gy + 9)], BG*0.6)
    # wooden boards in the gable triangle
    tri = [top_l, top_r, apex]
    form(tri, P.SHED_WALL, w=BG*1.2, sh=0)
    C.saveState(); C.clipPath(poly(tri), stroke=0, fill=0)
    bx = gx - hw
    while bx < gx + hw:
        s_([(bx, gy + eave_h), (bx, gy + apex_h)], BG*0.6); bx += 12
    C.restoreState()
    tube([(gx - hw - 6, gy + eave_h), (gx + hw + 6, gy + eave_h)], 7, 7, P.ATTIC_BEAM, lw=BG, sh=0)
    # roof edges with tiles
    for sx in (-1, 1):
        a = (gx + sx*(hw + 26), gy + eave_h - 10); b = (gx, gy + apex_h + 16)
        nx_, ny_ = (0, 14)
        band = [a, b, (b[0], b[1] + 14), (a[0], a[1] + 14)]
        sh_(band, P.ROOF)
        L = math.hypot(b[0] - a[0], b[1] - a[1]); n = int(L/8)
        for i in range(n):
            t = i/n; px, py = a[0] + (b[0] - a[0])*t, a[1] + (b[1] - a[1])*t
            s_(ell(px, py + 3, 4, 3, 8, 180, 360), BG*0.4)
        s_([a, b], BG*1.2)
    # round star window
    wy = gy + eave_h + (apex_h - eave_h)*0.42
    wr = min(hw*0.18, (apex_h - eave_h)*0.2)
    shape(ell(gx, wy, wr + 5, wr + 5, 36), P.ATTIC_BEAM, BG)
    shape(ell(gx, wy, wr, wr, 36), 1.0, 1.4)
    star(gx, wy, wr*0.6, 0.35)
    if low_window:
        wx = gx - hw*0.55; wy0 = gy + 30
        sh_([(wx - 20, wy0), (wx + 20, wy0), (wx + 20, wy0 + 44), (wx - 20, wy0 + 44)], 1.0)
        gl = [(wx - 17, wy0 + 3), (wx + 17, wy0 + 3), (wx + 17, wy0 + 41), (wx - 17, wy0 + 41)]
        sh_(gl, P.WINDOW_GLASS)
        clip_fill(gl, [(wx - 12, wy0 + 3), (wx - 5, wy0 + 3), (wx + 6, wy0 + 41), (wx - 1, wy0 + 41)], P.WINDOW_GLINT)
        for cx_ in (wx - 17, wx + 17):   # curtains
            sh_([(cx_, wy0 + 41), (cx_ + (8 if cx_ < wx else -8), wy0 + 41), (cx_ + (4 if cx_ < wx else -4), wy0 + 12), (cx_, wy0 + 10)], P.CURTAIN, BG*0.6)
        s_([(wx, wy0 + 3), (wx, wy0 + 41)], BG*1.4, g=1.0); s_([(wx, wy0 + 3), (wx, wy0 + 41)], BG*0.5)
        sh_([(wx - 24, wy0 - 3), (wx + 24, wy0 - 3), (wx + 24, wy0), (wx - 24, wy0)], P.SILL)
        sh_([(wx - 20, wy0 - 10), (wx + 20, wy0 - 10), (wx + 20, wy0 - 3), (wx - 20, wy0 - 3)], P.CRATE)
        for fx in range(5):
            stroke([(wx - 16 + fx*8, wy0 - 3), (wx - 16 + fx*8, wy0 + 5)], 0.5, g=0.3)
            sh_(ell(wx - 16 + fx*8, wy0 + 6, 2.6, 2.6, 12), P.FLOWER, BG*0.6)
    if drainpipe:
        px = gx + hw - 8
        tube([(px, gy + 2), (px, gy + eave_h - 6), (px - 6, gy + eave_h + 2)], 5, 5, P.METAL, lw=BG, sh=0)
        for yy in (gy + 30, gy + eave_h*0.6): sh_([(px - 4, yy), (px + 4, yy), (px + 4, yy + 2.5), (px - 4, yy + 2.5)], 0.3, BG*0.5)
    if climber:
        ivy(gx + hw - 22, gy + 16, gx + hw - 40, gy + eave_h*0.7, seed)
    return gx, wy, wr



def bed_front(p, cx, bw, waist_y):
    """the blanket from the kids' waists down, and the footboard in front"""
    bl = [(cx - bw/2 - 6, p.y - 5), (cx - bw/2 - 6, waist_y)] + \
         bez((cx - bw/2 - 6, waist_y), (cx - bw*0.2, waist_y + 10), (cx + bw*0.2, waist_y - 6), (cx + bw/2 + 6, waist_y + 2)) + \
         [(cx + bw/2 + 6, p.y - 5)]
    fill(bl, P.BLANKET)
    C.saveState(); C.clipPath(poly(bl), stroke=0, fill=0)
    for xx in range(int(cx - bw/2), int(cx + bw/2) + 16, 16):
        for yy in range(int(p.y), int(waist_y + 12), 16):
            dot(xx + ((yy//16) % 2)*8, yy, 1.8, P.BLANKET_DOT)
    C.restoreState()
    stroke(bl, BG*1.2, closed=True)
    foot = waist_y - (waist_y - p.y)*0.45
    form([(cx - bw/2 - 10, p.y - 5), (cx + bw/2 + 10, p.y - 5), (cx + bw/2 + 10, foot), (cx - bw/2 - 10, foot)], P.BED, w=BG*1.2, sh=0)
    s_([(cx - bw/2 - 10, foot - 8), (cx + bw/2 + 10, foot - 8)], BG*0.6)


# ------------------------------------------------------------------ flashback look
def old_photo(p, tone=0.0):
    """frame a panel like an old photograph: white border, corner mounts"""
    b = 7
    ring = [(p.x, p.y), (p.x + p.w, p.y), (p.x + p.w, p.y + p.h), (p.x, p.y + p.h), (p.x, p.y),
            (p.x + b, p.y + b), (p.x + b, p.y + p.h - b), (p.x + p.w - b, p.y + p.h - b), (p.x + p.w - b, p.y + b), (p.x + b, p.y + b)]
    fill(ring, P.PHOTO_FRAME)
    stroke([(p.x + b, p.y + b), (p.x + b, p.y + p.h - b), (p.x + p.w - b, p.y + p.h - b), (p.x + p.w - b, p.y + b)], 0.6, closed=True, g=0.4)
    for (cx, cy, dx, dy) in ((p.x, p.y, 1, 1), (p.x + p.w, p.y, -1, 1), (p.x, p.y + p.h, 1, -1), (p.x + p.w, p.y + p.h, -1, -1)):
        shape([(cx, cy), (cx + dx*22, cy), (cx, cy + dy*22)], 0.25, 0.8)
