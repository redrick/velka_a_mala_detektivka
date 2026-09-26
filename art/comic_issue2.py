import os
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
import math, random
import lib
from lib import G, ell, bez, rrect
from style3 import *
from style3 import C
from chars3 import *
from scenes3 import *
from props_extra import mug, night_sky
from attic import *
from letter import Panel, caption, bubble, sfx, title, hand_text, thought

W, H = A4
M = 28; GUT = 9; TOP = H - 30
# Finished issues are kept in the repo: comics/<series>/<nn>_<title>.pdf
OUT = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                   "comics", "velka_a_mala_detektivka", "02_tajemstvi_stareho_klice.pdf")
os.makedirs(os.path.dirname(OUT), exist_ok=True)
cv = canvas.Canvas(OUT, pagesize=A4); lib.set_canvas(cv)
cv.setTitle("Velká a malá detektivka – Případ č. 2: Tajemství starého klíče")
PAGE = [1]


def rows(spec):
    out = []; y = TOP
    for h, cols in spec:
        y -= h; x = M; tw = W - 2*M - GUT*(len(cols)-1)
        for f in cols:
            out.append((x, y, tw*f, h)); x += tw*f + GUT
        y -= GUT
    return out


def page_end():
    hand_text(W/2-20, 18, 40, f"– {PAGE[0]} –", "SH", 10, g=0.35)
    PAGE[0] += 1; cv.showPage()


def bg_fill(p, g, alpha=None):
    fill([(p.x, p.y), (p.x+p.w, p.y), (p.x+p.w, p.y+p.h), (p.x, p.y+p.h)], g, alpha)


def rays(p, cx, cy, g=0.9, n=18):
    for i in range(n):
        a = i*math.tau/n
        fill([(cx, cy), (cx+math.cos(a)*500, cy+math.sin(a)*500), (cx+math.cos(a+0.14)*500, cy+math.sin(a+0.14)*500)], g)


def garden(p, gy, seed=1, house_x=None, house_s=1.0, tree_x=None, tree_s=1.2, hills_=True, clouds=True):
    sky(p, 0.95)
    if clouds: cloud(p.X(0.55), p.Y(0.85), 0.8)
    if hills_: hills(p, gy + p.h*0.06, 16, 0.87, seed)
    ground(p, gy)
    if house_x is not None: house(p.X(house_x), gy-4, house_s)
    if tree_x is not None: tree(p.X(tree_x), gy-6, tree_s, seed=seed+3)


def jar(x, y, h=14, g=P.JAM):
    sh_(rrect(x-5, y, 10, h, 2), P.JAR)
    clip_fill(rrect(x-5, y, 10, h, 2), [(x-6, y), (x+6, y), (x+6, y+h*0.7), (x-6, y+h*0.7)], g)
    stroke(rrect(x-5, y, 10, h, 2), BG, closed=True)
    sh_([(x-6, y+h), (x+6, y+h), (x+6, y+h+3), (x-6, y+h+3)], P.CLOTH_CHECK, BG*0.6)


def wall_clock(x, y, r=12):
    shape(ell(x, y, r, r, 30), 1.0, BG*1.3)
    for a in range(0, 360, 30):
        ra = math.radians(a); dot(x+math.cos(ra)*r*0.78, y+math.sin(ra)*r*0.78, 0.6, 0.2)
    stroke([(x, y), (x, y+r*0.6)], 1.0); stroke([(x, y), (x+r*0.45, y-r*0.1)], 1.0)
    stroke([(x, y-r), (x, y-r-10)], 0.6); shape(ell(x, y-r-13, 3, 3, 12), P.BRASS, 0.6)


def kitchen(p, table=True, details=True):
    bg_fill(p, 0.92)
    for yy in range(int(p.Y(0.35)), int(p.y+p.h), 16): stroke([(p.x, yy), (p.x+p.w, yy)], BG*0.4, g=0.7)
    for xx in range(int(p.x), int(p.x+p.w), 16): stroke([(xx, p.Y(0.35)), (xx, p.y+p.h)], BG*0.4, g=0.7)
    if details:
        shelf(p.X(0.02), p.X(0.02)+120, p.Y(0.72))
        for i, g in enumerate((P.JAM, 0.75, P.JAM, 0.55)): jar(p.X(0.02)+22+i*22, p.Y(0.72)+5, 14 + (i % 2)*4, g)
        wall_clock(p.X(0.93), p.Y(0.8), 13)
        for hx in (0.55, 0.6, 0.65):
            dot(p.X(hx), p.Y(0.9), 1.2, 0.3)
        stroke([(p.X(0.55), p.Y(0.9)), (p.X(0.55), p.Y(0.8))], 1.2); shape(ell(p.X(0.55), p.Y(0.78), 5, 3, 12), P.METAL, 0.8)
        sh_(rrect(p.X(0.6)-3, p.Y(0.72), 6, 16, 1), 0.95, BG*0.6)
        stroke([(p.X(0.6), p.Y(0.9)), (p.X(0.6), p.Y(0.88))], 0.8)
    shape([(p.x, p.y), (p.x+p.w, p.y), (p.x+p.w, p.Y(0.35)), (p.x, p.Y(0.35))], 0.7, BG)
    if table:
        for k_ in range(1, 6): stroke([(p.x+p.w*k_/6, p.y), (p.x+p.w*k_/6, p.Y(0.35))], BG*0.6)
        shape([(p.X(0.03), p.Y(0.35)), (p.X(0.97), p.Y(0.35)), (p.X(0.97), p.Y(0.38)), (p.X(0.03), p.Y(0.38))], 0.5, BG)


def stove(x, y, w=70, h=80):
    form([(x, y), (x+w, y), (x+w, y+h), (x, y+h)], P.STOVE, w=BG, sdx=4, sdy=0)
    for yy in range(int(y)+14, int(y+h), 14): s_([(x, yy), (x+w, yy)], BG*0.5)
    sh_(rrect(x+w*0.25, y+h*0.25, w*0.5, h*0.22, 3), P.STOVE_DOOR)
    sh_([(x-4, y+h), (x+w+4, y+h), (x+w+4, y+h+5), (x-4, y+h+5)], 0.4)


def night_house(p, gy_f=0.18, hx=0.55, hs=2.4, lit=True):
    """the cottage at night with the round star window in the gable (as in issue 1)"""
    for (sx_, sy_) in ((0.1, 0.9), (0.3, 0.8), (0.55, 0.92), (0.65, 0.78), (0.9, 0.88), (0.2, 0.7), (0.45, 0.75)):
        star(p.X(sx_), p.Y(sy_), 4, 0.98)
    fill([(p.x-5, p.y-5), (p.x-5, p.Y(gy_f)), (p.x+p.w+5, p.Y(gy_f)), (p.x+p.w+5, p.y-5)], 0.5)
    stroke([(p.x-5, p.Y(gy_f)), (p.x+p.w+5, p.Y(gy_f))], BG)
    house(p.X(hx), p.Y(gy_f), hs, smoke=True)
    if lit:
        for wx in (-35, 17):
            gl = [(p.X(hx)+wx*hs, p.Y(gy_f)+20*hs), (p.X(hx)+(wx+18)*hs, p.Y(gy_f)+20*hs),
                  (p.X(hx)+(wx+18)*hs, p.Y(gy_f)+42*hs), (p.X(hx)+wx*hs, p.Y(gy_f)+42*hs)]
            fill(gl, 0.97, 0.85)
            stroke([((gl[0][0]+gl[1][0])/2, gl[0][1]), ((gl[0][0]+gl[1][0])/2, gl[2][1])], 1.2)
            stroke([(gl[0][0], (gl[0][1]+gl[2][1])/2), (gl[1][0], (gl[0][1]+gl[2][1])/2)], 1.2)
    cx, cy = p.X(hx), p.Y(gy_f)+70*hs
    shape(ell(cx, cy, 8.3*hs, 8.3*hs, 36), 1.0, 1.6)
    star(cx, cy, 4.6*hs, 0.35)
    return cx, cy


def zzz(p, x, y, big=False):
    for i, (dx, dy, sz) in enumerate(((0, 0, 11), (10, 9, 14), (22, 20, 18))):
        hand_text(x+dx, y+dy, 20, "Z" if i == 2 else "z", "SHB", sz + (4 if big else 0), align="left")


def night_bed_scene(p, alica_mood="sleepy", hanka_mood="wow", alica_right="down", hanka_right="down",
                    alica_look=(0, 0), hanka_look=(0, 0), s=1.5):
    """the girls' room at night: two beds in an L, heads close together in the corner.
    Alica's bed runs along the back wall (head on the right), Hanka's comes towards us.
    Returns (alica_head, hanka_head) as page points for speech balloon tails."""
    bedroom(p, night=True)
    bunting(p)
    wx0, wy0, wx1, wy1 = p.X(0.05), p.Y(0.6), p.X(0.24), p.Y(0.86)
    fill([(wx0, wy0), (wx1, wy0), (wx1, wy1), (wx0, wy1)], 0.4)
    moon(wx0+(wx1-wx0)*0.62, wy0+(wy1-wy0)*0.6, 9)
    star(wx0+(wx1-wx0)*0.25, wy0+(wy1-wy0)*0.75, 2.5, 0.95)
    stroke([(wx0, wy0), (wx1, wy0), (wx1, wy1), (wx0, wy1)], BG*1.4, closed=True)
    stroke([((wx0+wx1)/2, wy0), ((wx0+wx1)/2, wy1)], BG*1.6)
    shelf_toys(p.X(0.3), p.Y(0.7), min(80, p.w*0.2))
    kids_drawing(p.X(0.88), p.Y(0.68), min(40, p.w*0.09), min(30, p.h*0.12))
    k = s/1.5
    # Alica's bed along the back wall
    x0, x1, top = p.X(0.04), p.X(0.6), p.Y(0.36)
    bed_side(x0, x1, top)
    ax = x1 - 26*k; waist = top + 8
    C.saveState()   # she sits in bed: nothing of her below the mattress
    C.clipPath(poly([(p.x, top - 10), (p.x + p.w, top - 10), (p.x + p.w, p.y + p.h), (p.x, p.y + p.h)]), stroke=0, fill=0)
    alica(ax, waist - 45*s, s, mood=alica_mood, right=alica_right, look=alica_look, shadow=False)
    C.restoreState()
    blanket_side(x0, ax + 14*k, top, waist + 4)
    # Hanka's bed, its head in the corner next to Alica's pillow
    hs = s*0.95; bw = p.w*0.28; cx = x1 + 12 + bw/2; hwaist = p.Y(0.22)
    hy_ = hwaist - 31*hs
    bed_back(cx, bw, hwaist, hy_ + 92*hs, hy_ + 82*hs, 10*hs, pillows=(0,))
    hanka(cx, hy_, hs, mood=hanka_mood, right=hanka_right, look=hanka_look, shadow=False)
    bed_front(p, cx, bw, hwaist + 4)
    return (ax, waist - 45*s + 89.8*s), (cx, hy_ + 70.2*hs)


def head_y(p, frac, hy, s):
    """feet y that puts a figure's head centre at `frac` of the panel height (for close-ups)"""
    return p.Y(frac) - hy*s


# =================================================================== COVER
def cover():
    with Panel(M, 40, W-2*M, H-80) as p:
        attic(p, floor_y=0.24, window=(0.5, 0.55), dark=0.45, seed=7)
        # sunbeam-like torch beam onto the chest
        beam_light(p.X(0.42)+100, p.Y(0.03)+168, p.X(0.55), p.Y(0.02), p.X(0.98), p.Y(0.2), 0.35)
        chest(p.X(0.72), p.Y(0.08), 1.25)
        sled(p.X(0.14), p.Y(0.2), 1.0); suitcase(p.X(0.02), p.Y(0.23), 70, 44)
        cobweb(p.x+p.w, p.y+p.h, 60, flip=True); cobweb(p.x, p.y+p.h, 50)
        owl(p.X(0.66), p.Y(0.47), 1.6, flip=True, mood="wide")
        owlet(p.X(0.76), p.Y(0.47), 1.3, mood="open"); owlet(p.X(0.83), p.Y(0.47), 1.2, mood="sleepy")
        alica(p.X(0.18), p.Y(0.03), 3.1, right="up", mood="wow", look=(1, 0.3),
              item=lambda x, y: key(x+1, y+3, 0.45, rot=70, tag=True))
        hanka(p.X(0.42), p.Y(0.03), 3.0, mood="surprised", torch=True, right="lens", look=(1, 0.3))
    box = [(M+34, H-236), (W-M-30, H-232), (W-M-34, H-48), (M+30, H-52)]
    fill([(x+3, y-3) for x, y in box], 0.0, 0.25); fill(box, 1.0)
    for a_, b_ in ((0, 1), (1, 2), (2, 3), (3, 0)): stroke([box[a_], box[b_]], 1.8)
    title(W/2, H-98, "VELKÁ A MALÁ", 40)
    title(W/2, H-160, "DETEKTIVKA", 66)
    hand_text(M+40, H-190, W-2*M-80, "Alica a Hanka", "SHB", 20)
    hand_text(M+40, H-217, W-2*M-80, "Případ č. 2: Tajemství starého klíče", "SH", 15)
    magnifier(M+82, H-120, ang=-30, r=17)
    key(W-M-110, H-118, 2.0, rot=-20, tag=False)
    page_end()


# =================================================================== 2 – noises at night
def page_night():
    R = rows([(250, [1]), (245, [0.5, 0.5]), (265, [1])])
    with Panel(*R[0], bg=0.7) as p:
        moon(p.X(0.88), p.Y(0.75), 22)
        cx, cy = night_house(p, 0.14, 0.52, 2.2)
        tree(p.X(0.12), p.Y(0.14), 1.6, seed=20, g=0.55)
        caption(p, "Minule našly Alica a Hanka ve staré botě klíč se hvězdičkou.", w=250)
        sfx(cx+34, cy+18, "ŤUK…", 16, 8)
        sfx(cx+46, cy-20, "ŤUK…", 13, -6)
    with Panel(*R[1]) as p:
        night_bed_scene(p, "sleepy", "wow", hanka_look=(0, 1), s=1.05)
        sfx(p.X(0.3), p.Y(0.9), "ŤUK! ŤUK!", 16, 6)
        caption(p, "Tu noc Hanka nemůže usnout.", w=p.w-14, size=12, where="bl")
    with Panel(*R[2]) as p:
        planks(p, 0.45, 24, 5)
        fill([(p.x, p.y), (p.x+p.w, p.y), (p.x+p.w, p.y+p.h), (p.x, p.y+p.h)], 0.0, 0.3)
        sfx(p.X(0.12), p.Y(0.6), "ŠŠŠŠ…", 24, 8)
        sfx(p.X(0.5), p.Y(0.3), "CHRRR…", 22, -6)
        caption(p, "Nad postýlkou, na půdě, něco ťuká, syčí a chrápe.", w=p.w-14, size=12)
    with Panel(*R[3]) as p:
        (ahx, ahy), (hhx, hhy) = night_bed_scene(p, "whisper", "worried", alica_right="hush", hanka_look=(-1, 0.5),
                                                 alica_look=(1, -0.3), s=1.4)
        bubble(p.X(0.7), p.Y(0.97), 155, "Alico… slyšíš to? Co to je?", hhx, hhy+16, whisper=True)
        bubble(p.X(0.33), p.Y(0.97), 160, "Něco je nad námi na půdě.", ahx, ahy+16, whisper=True)
        bubble(p.X(0.02), p.Y(0.55), 150, "Detektivky se nebojí. Ráno to prozkoumáme!", ahx-14, ahy)
    page_end()


# =================================================================== 3 – breakfast
def page_breakfast():
    R = rows([(255, [1]), (250, [0.5, 0.5]), (255, [1])])
    with Panel(*R[0]) as p:
        kitchen(p)
        mug(p.X(0.35), p.Y(0.38), 1.3); mug(p.X(0.6), p.Y(0.38), 1.3, steam=False)
        babicka(p.X(0.82), p.Y(0.03), 1.45, flip=True, mood="surprised", look=(1, 0))
        deda(p.X(0.65), p.Y(0.03), 1.45, flip=True, mood="happy", look=(1, 0))
        hanka(p.X(0.13), p.Y(0.03), 1.55, mood="wow", right="up")
        alica(p.X(0.3), p.Y(0.03), 1.65, mood="determined", right="point", look=(1, 0))
        caption(p, "Ráno u snídaně…", w=130)
        bubble(p.X(0.3), p.Y(0.97), 200, "Dědo, v noci něco ťukalo na půdě!", p.X(0.33), p.Y(0.7))
        bubble(p.X(0.02), p.Y(0.82), 110, "A chrápalo!", p.X(0.12), p.Y(0.6))
    with Panel(*R[1]) as p:
        kitchen(p, table=False)
        deda(p.X(0.66), head_y(p, 0.42, 114.8, 2.6), 2.6, flip=True, mood="think", look=(1, -0.5), shadow=False)
        bubble(p.X(0.03), p.Y(0.97), p.w*0.56, "Na půdu se nechodí. Jsou tam jen staré krámy…", p.X(0.5), p.Y(0.5))
    with Panel(*R[2]) as p:
        kitchen(p, table=False)
        babicka(p.X(0.72), p.Y(0.03), 1.55, flip=True, mood="whisper", right="hush", look=(1, -0.3))
        hanka(p.X(0.18), p.Y(0.03), 1.45, mood="surprised", look=(1, 0.3))
        alica(p.X(0.38), p.Y(0.03), 1.5, mood="surprised", look=(1, 0.3))
        bubble(p.X(0.03), p.Y(0.97), p.w*0.62, "Děda na půdě nebyl už hrozně dlouho. Kdoví proč…", p.X(0.66), p.Y(0.72), whisper=True)
    with Panel(*R[3]) as p:
        bg_fill(p, 0.9)
        notebook_big(p.X(0.1), p.Y(0.08), p.w*0.8, p.h*0.72, "PŘÍPAD Č. 2: ZVUKY NA PŮDĚ",
                     ["1. ťukání: ťuk ťuk", "2. syčení: šššš", "3. chrápání: chrrr", "4. Proč děda nechce na půdu?"])
        with T(p.X(0.87), p.Y(0.2), 1.0, rot=-35):
            shape([(-3, 0), (3, 0), (3, 60), (-3, 60)], 0.8)
            shape([(-3, 0), (3, 0), (0, -9)], 1.0)
        caption(p, "Alica si všechno zapíše do zápisníku.", w=p.w-14)
    page_end()


# =================================================================== 4 – suspects
def page_suspects():
    R = rows([(270, [1]), (240, [0.5, 0.5]), (250, [1])])
    with Panel(*R[0]) as p:
        garden(p, p.Y(0.14), 9, clouds=False)
        tufts(p, p.Y(0.02), p.Y(0.12), 4, 9)
        alica(p.X(0.15), p.Y(0.02), 1.8, mood="think", right="chin", look=(1, 1))
        caption(p, "Kdo dělá na půdě takový rámus?", w=200)
        tb_x, tb_y, tb_w, tb_h = p.X(0.35), p.Y(0.95), p.w*0.6, p.h*0.72
        thought(tb_x, tb_y, tb_w, tb_h, p.X(0.25), p.Y(0.66))
        cat(tb_x+tb_w*0.17, tb_y-tb_h*0.86, 1.4, mood="sleepy")
        joey(tb_x+tb_w*0.5, tb_y-tb_h*0.9, 1.05, mood="happy", shadow=False)
        cloud(tb_x+tb_w*0.8, tb_y-tb_h*0.62, 0.7)
        for k_ in range(3):
            yy = tb_y-tb_h*0.7 - k_*9
            stroke(bez((tb_x+tb_w*0.7, yy), (tb_x+tb_w*0.76, yy+4), (tb_x+tb_w*0.84, yy-4), (tb_x+tb_w*0.92, yy)), 1.0)
        for fx in (0.17, 0.5, 0.82):
            hand_text(tb_x+tb_w*fx-10, tb_y-tb_h*0.25, 20, "?", "SHB", 24)
    with Panel(*R[1]) as p:
        kitchen(p, table=False)
        stove(p.X(0.55), p.Y(0.02), 80, 95)
        shape([(p.X(0.1), p.Y(0.25)), (p.X(0.5), p.Y(0.25)), (p.X(0.5), p.Y(0.3)), (p.X(0.1), p.Y(0.3))], 0.55, BG)
        for bx in (0.13, 0.45): shape([(p.X(bx), p.Y(0.02)), (p.X(bx)+6, p.Y(0.02)), (p.X(bx)+6, p.Y(0.25)), (p.X(bx), p.Y(0.25))], 0.5, BG)
        cat(p.X(0.3), p.Y(0.3), 1.5, mood="sleepy")
        zzz(p, p.X(0.36), p.Y(0.62))
        bubble(p.X(0.03), p.Y(0.97), p.w*0.9, "Micka spí celou noc u kamen. To nebyla ona.", p.X(0.25), p.Y(0.55))
    with Panel(*R[2]) as p:
        bg_fill(p, 0.9)
        ladder(p.X(0.62), p.Y(0.0), p.Y(1.02), 44)
        joey(p.X(0.3), p.Y(0.03), 1.5, mood="calm", flip=False)
        sfx(p.X(0.1), p.Y(0.7), "KŇUK…", 18, 8)
        caption(p, "A Joey? Ten na žebřík nevyleze.", w=p.w-14, size=12, where="bl")
    with Panel(*R[3]) as p:
        garden(p, p.Y(0.2), 51, hills_=False, clouds=False)
        gable_end(p.X(0.9), p.Y(0.2), 200, 400, 520, seed=7, climber=True, drainpipe=False)
        tufts(p, p.Y(0.03), p.Y(0.18), 6, 21)
        feather(p.X(0.58), p.Y(0.07), 1.8, rot=70)
        pellet(p.X(0.7), p.Y(0.08), 1.8); pellet(p.X(0.78), p.Y(0.12), 1.5, rot=20)
        hanka(p.X(0.42), p.Y(0.03), 1.6, mood="wow", right="point", look=(1, -1))
        alica(p.X(0.18), p.Y(0.03), 1.7, mood="surprised", right="lens", lens=True, look=(1, -1))
        caption(p, "Pod okýnkem z půdy…", w=150)
        bubble(p.X(0.63), p.Y(0.97), 150, "Alico! Tady je bílé peříčko!", p.X(0.45), p.Y(0.62))
        bubble(p.X(0.31), p.Y(0.97), 140, "A divné šedé kuličky…", p.X(0.2), p.Y(0.7))
    page_end()


# =================================================================== 5 – clues + Tonda + key to děda
def page_clues():
    R = rows([(245, [0.5, 0.5]), (255, [1]), (260, [1])])
    with Panel(*R[0]) as p:
        bg_fill(p, 0.93)
        feather(p.X(0.3), p.Y(0.3), 4.0, rot=-20)
        pellet(p.X(0.72), p.Y(0.42), 4.5, rot=10)
        magnifier(p.X(0.78), p.Y(0.46), ang=20, r=26)
        caption(p, "Stopa č. 1: bílé peříčko. Stopa č. 2: chlupaté šedé kuličky.", w=p.w-14, size=12)
    with Panel(*R[1]) as p:
        garden(p, p.Y(0.1), 17, hills_=False, clouds=False)
        tonda(p.X(0.5), p.Y(0.02), 1.6, mood="grin", right="up", look=(1, 0))
        fence(p.x-4, p.x+p.w+4, p.Y(0.02), 58)
        bubble(p.X(0.03), p.Y(0.97), p.w*0.92, "To jsou vývržky! Vyplivují je sovy. Učili jsme se to ve škole.", p.X(0.48), p.Y(0.82))
    with Panel(*R[2]) as p:
        sky(p, 0.95)
        cloud(p.X(0.2), p.Y(0.85), 0.9)
        ground(p, p.Y(0.1))
        gable_end(p.X(0.7), p.Y(0.1), 140, 120, 250, seed=9)
        tufts(p, p.Y(0.02), p.Y(0.09), 5, 22)
        for (bx_, by_) in ((0.32, 0.86), (0.36, 0.9)):
            stroke(bez((p.X(bx_)-6, p.Y(by_)), (p.X(bx_)-3, p.Y(by_)+4), (p.X(bx_), p.Y(by_)+1), (p.X(bx_), p.Y(by_))), 0.9)
            stroke(bez((p.X(bx_), p.Y(by_)), (p.X(bx_), p.Y(by_)+1), (p.X(bx_)+3, p.Y(by_)+4), (p.X(bx_)+6, p.Y(by_))), 0.9)
        alica(p.X(0.14), p.Y(0.03), 1.75, mood="wow", right="point", look=(1, 1))
        hanka(p.X(0.32), p.Y(0.03), 1.6, mood="wow", look=(1, 1))
        bubble(p.X(0.02), p.Y(0.97), 150, "Sova? Na naší půdě?", p.X(0.14), p.Y(0.72))
        bubble(p.X(0.38), p.Y(0.55), 150, "Okýnko má hvězdičku… a klíč taky!", p.X(0.35), p.Y(0.5))
    with Panel(*R[3]) as p:
        garden(p, p.Y(0.2), 19, house_x=0.88, house_s=0.9, clouds=False)
        deda(p.X(0.7), p.Y(0.03), 1.4, flip=True, mood="surprised", right="front", look=(1, -0.3))
        alica(p.X(0.3), p.Y(0.03), 1.6, mood="grin", right="front", look=(1, 0),
              item=lambda x, y: key(x+4, y+1, 0.55, rot=10, tag=True), legs="walk")
        hanka(p.X(0.12), p.Y(0.03), 1.55, mood="happy", legs="walk", look=(1, 0))
        joey(p.X(0.88), p.Y(0.03), 0.9, flip=True, mood="happy")
        bubble(p.X(0.02), p.Y(0.97), 200, "Dědo! Tenhle klíč jsme našly ve staré botě v kůlně.", p.X(0.28), p.Y(0.72))
        bubble(p.X(0.42), p.Y(0.97), 160, "To je přece… můj starý klíč od truhly!", p.X(0.68), p.Y(0.72))
    page_end()


# =================================================================== 6 – up into the attic
def page_climb():
    R = rows([(260, [1]), (245, [0.5, 0.5]), (255, [1])])
    with Panel(*R[0]) as p:
        bg_fill(p, 0.92)
        for xx in range(int(p.x)+10, int(p.x+p.w), 24):
            for yy in range(int(p.y)+10, int(p.Y(0.8)), 24): dot(xx + ((yy//24) % 2)*12, yy, 1.1, 0.78)
        shape([(p.x-5, p.Y(0.82)), (p.x+p.w+5, p.Y(0.82)), (p.x+p.w+5, p.y+p.h+5), (p.x-5, p.y+p.h+5)], 0.85, BG)
        hx0, hx1 = p.X(0.5), p.X(0.66)
        shape([(hx0, p.Y(0.82)), (hx1, p.Y(0.82)), (hx1, p.y+p.h+5), (hx0, p.y+p.h+5)], 0.12, BG)
        shape([(hx1, p.Y(0.82)), (hx1+40, p.Y(0.9)), (hx1+40, p.y+p.h+5), (hx1, p.y+p.h+5)], 0.6, BG)
        floor(p, p.Y(0.1), 0.6)
        shape(rrect(p.X(0.06), p.Y(0.5), 70, 52, 2), P.SHELF, 1.2)
        with T(p.X(0.06)+35, p.Y(0.5)+14, 0.55): joey(0, 0, 1.0, mood="happy", shadow=False)
        sh_([(p.X(0.28), p.Y(0.72)), (p.X(0.44), p.Y(0.72)), (p.X(0.44), p.Y(0.75)), (p.X(0.28), p.Y(0.75))], P.SHELF)
        for hx, g in ((0.31, P.ALICA_COAT), (0.37, P.DUNGAREES), (0.42, P.CARDIGAN)):
            dot(p.X(hx), p.Y(0.72), 1.5, 0.3)
            sh_([(p.X(hx)-9, p.Y(0.71)), (p.X(hx)+9, p.Y(0.71)), (p.X(hx)+12, p.Y(0.46)), (p.X(hx)-12, p.Y(0.46))], g)
        fill(ell(p.X(0.36), p.Y(0.07), 60, 8, 30), P.CLOTH_CHECK, 0.6)
        ladder((hx0+hx1)/2, p.Y(0.05), p.Y(0.84), 40)
        deda(p.X(0.78), p.Y(0.03), 1.5, flip=True, mood="happy", right="up", look=(1, 0.5))
        hanka(p.X(0.14), p.Y(0.03), 1.5, mood="grin", torch=True, right="lens", look=(1, 0.5))
        alica(p.X(0.3), p.Y(0.03), 1.6, mood="determined", look=(1, 0.5),
              item=lambda x, y: key(x+2, y+4, 0.5, rot=70, tag=False))
        bubble(p.X(0.02), p.Y(0.97), 250, "Tak dobře. Půjdeme nahoru spolu. A potichu!", p.X(0.76), p.Y(0.66))
    with Panel(*R[1]) as p:
        bg_fill(p, 0.9)
        ladder(p.X(0.5), p.y-5, p.y+p.h+5, 50)
        hanka(p.X(0.47), p.Y(0.18), 1.6, mood="determined", torch=True, right="up", look=(0, 1), shadow=False)
        sfx(p.X(0.1), p.Y(0.2), "VRZ!", 22, 10); sfx(p.X(0.72), p.Y(0.5), "VRZ!", 18, -10)
    with Panel(*R[2]) as p:
        attic(p, floor_y=0.3, dark=0.55, seed=4)
        alica(p.X(0.5), head_y(p, 0.52, 89.8, 2.4), 2.4, mood="surprised", look=(1, 0.3), shadow=False)
        shape([(p.x-5, p.y-5), (p.x+p.w+5, p.y-5), (p.x+p.w+5, p.Y(0.3)), (p.x-5, p.Y(0.3))], P.ATTIC_FLOOR, BG)
        fill([(p.X(0.25), p.Y(0.3)), (p.X(0.75), p.Y(0.3)), (p.X(0.75), p.Y(0.33)), (p.X(0.25), p.Y(0.33))], 0.1)
        bubble(p.X(0.05), p.Y(0.97), p.w*0.9, "Tady je tma jako v pytli!", p.X(0.5), p.Y(0.75))
    with Panel(*R[3]) as p:
        attic(p, floor_y=0.18, window=(0.5, 0.6), dark=0.5, seed=8)
        beam_light(p.X(0.22), p.Y(0.35), p.X(0.55), p.Y(0.02), p.X(0.95), p.Y(0.35), 0.35)
        chest(p.X(0.75), p.Y(0.06), 0.75)
        sled(p.X(0.38), p.Y(0.12), 0.8); suitcase(p.X(0.5), p.Y(0.07), 50, 32)
        crate(p.X(0.9), p.Y(0.07), 44, 50)
        cobweb(p.x+p.w, p.y+p.h, 40, flip=True); cobweb(p.x, p.y+p.h, 36)
        hanka(p.X(0.18), p.Y(0.03), 1.55, mood="wow", torch=True, right="lens", look=(1, 0))
        alica(p.X(0.06), p.Y(0.03), 1.6, mood="wow", look=(1, 0))
        caption(p, "Na půdě je spousta starých věcí.", w=220)
        bubble(p.X(0.25), p.Y(0.8), 170, "Tam! Truhla se hvězdičkou!", p.X(0.2), p.Y(0.6))
    page_end()


# =================================================================== 7 – the chest opens
def page_chest():
    R = rows([(240, [0.5, 0.5]), (260, [1]), (260, [1])])
    with Panel(*R[0]) as p:
        bg_fill(p, P.CHEST)
        with T(p.X(0.42), p.Y(0.5) - 49*4.2, 4.2):
            shape(rrect(-12, 36, 24, 26, 4), P.BRASS, 1.1)
            star(0, 55, 4.5, 0.2)
            fill(ell(0, 42, 2, 3, 10), 0.0)
        key(p.X(0.42) + 30*2.6, p.Y(0.5) - 7*4.2, 2.6, rot=180, tag=True)
        sfx(p.X(0.1), p.Y(0.72), "CVAK!", 28, 8)
    with Panel(*R[1]) as p:
        bg_fill(p, 1.0); rays(p, p.X(0.5), p.Y(0.55), 0.88)
        chest(p.X(0.5), p.Y(0.06), 1.05, open_=True)
        sfx(p.X(0.08), p.Y(0.8), "VRŽŽŽ…", 18, 8)
    with Panel(*R[2]) as p:
        attic(p, floor_y=0.2, dark=0.3, seed=9)
        with T(p.X(0.5), p.Y(0.02), 1.0):
            form([(-150, 0), (150, 0), (150, 120), (-150, 120)], P.CHEST, w=1.4, sdx=6, sdy=0)
            fill([(-142, 8), (142, 8), (142, 116), (-142, 116)], 0.3)
        # what lies inside
        with T(p.X(0.36), p.Y(0.12), 1.0, rot=-6):
            shape(rrect(-38, 0, 76, 54, 3), P.NOTEBOOK_COVER, 1.2)
            star(0, 34, 9, 0.95)
            hand_text(-36, 10, 72, "KLUB HVĚZDIČKA", "SHB", 8)
        map_half(p.X(0.52), p.Y(0.1), 0.9, "L", rot=8)
        star(p.X(0.78), p.Y(0.3), 10, P.BRASS)
        alica(p.X(0.08), p.Y(0.02), 1.6, mood="wow", look=(1, -1))
        hanka(p.X(0.93), p.Y(0.02), 1.5, flip=True, mood="wow", look=(1, -1))
        caption(p, "V truhle leží zápisník, odznak se hvězdičkou a kus staré mapy.", w=260)
        bubble(p.X(0.55), p.Y(0.97), 220, "Zápisník! A půlka nějaké mapy!", p.X(0.12), p.Y(0.72))
    with Panel(*R[3]) as p:
        attic(p, floor_y=0.18, window=(0.14, 0.62), dark=0.2, seed=10)
        deda(p.X(0.47), p.Y(0.03), 1.45, mood="happy", right="front", look=(0, -0.5),
             item=lambda x, y: notebook(x, y+2, 1.4))
        hanka(p.X(0.28), p.Y(0.03), 1.4, mood="happy", look=(1, 0.5))
        alica(p.X(0.68), p.Y(0.03), 1.5, flip=True, mood="happy", look=(1, 0.5))
        bubble(p.X(0.55), p.Y(0.97), 250, "Tohle je zápisník našeho klubu. Klub Hvězdička! Založili jsme ho tady na půdě, když jsem byl malý kluk…", p.X(0.5), p.Y(0.66))
    page_end()


# =================================================================== 8 – flashback: the club is founded
def page_fb1():
    R = rows([(255, [1]), (250, [0.5, 0.5]), (255, [1])])
    with Panel(*R[0]) as p:
        garden(p, p.Y(0.22), 61, house_x=0.86, house_s=1.0, tree_x=0.1, tree_s=1.1)
        tufts(p, p.Y(0.03), p.Y(0.2), 6, 3)
        young(p.X(0.35), p.Y(0.04), 1.65, "deda", right="wave", mood="grin")
        young(p.X(0.52), p.Y(0.04), 1.6, "franta", mood="happy", look=(-1, 0))
        young(p.X(0.68), p.Y(0.04), 1.55, "verka", mood="happy", right="up", look=(-1, 0))
        old_photo(p)
        caption(p, "Před mnoha lety… Malý děda a jeho nejlepší kamarádi Franta a Věrka.", w=280)
    with Panel(*R[1]) as p:
        attic(p, floor_y=0.12, window=(0.62, 0.6), seed=12)
        young(p.X(0.28), p.Y(0.02), 1.5, "verka", right="up", mood="grin", look=(1, 0.5),
              item=lambda x, y: stroke([(x, y), (x+6, y+12)], 2.0))
        old_photo(p)
        bubble(p.X(0.05), p.Y(0.95), p.w*0.6, "Naše znamení bude hvězdička!", p.X(0.28), p.Y(0.66))
    with Panel(*R[2]) as p:
        attic(p, floor_y=0.12, seed=13)
        chest(p.X(0.62), p.Y(0.05), 0.6, open_=True)
        young(p.X(0.25), p.Y(0.02), 1.5, "franta", right="point", mood="happy", look=(1, 0))
        old_photo(p)
        bubble(p.X(0.05), p.Y(0.95), p.w*0.88, "A do truhly budeme schovávat naše poklady!", p.X(0.25), p.Y(0.7))
    with Panel(*R[3]) as p:
        attic(p, floor_y=0.18, dark=0.45, seed=14, beam=0.7)
        beam_light(p.X(0.48), p.Y(0.2), p.X(0.2), p.Y(0.0), p.X(0.75), p.Y(0.0), 0.25)
        owl(p.X(0.8), p.Y(0.7)+5, 1.3, mood="open", flip=True)
        young(p.X(0.12), p.Y(0.03), 1.4, "franta", mood="happy", look=(1, 0.5))
        young(p.X(0.3), p.Y(0.03), 1.4, "verka", mood="happy", look=(1, 0.5))
        young(p.X(0.48), p.Y(0.03), 1.45, "deda", right="hush", mood="whisper", look=(1, 0.5))
        old_photo(p)
        caption(p, "Každý večer se scházeli na půdě. A z trámu se na ně dívala sova.", w=260)
        bubble(p.X(0.58), p.Y(0.62), 140, "Psst! Ať nevzbudíme sovu!", p.X(0.5), p.Y(0.56), whisper=True)
    page_end()


# =================================================================== 9 – flashback: treasure, map torn in two
def pond(p, y0, x0=0.45, x1=0.98):
    pts = ell(p.X((x0+x1)/2), y0, p.w*(x1-x0)/2, 26, 40)
    shape(pts, P.WATER, BG)
    for rx in (x0+0.02, x0+0.05, x1-0.04):
        for k_ in range(3):
            stroke([(p.X(rx)+k_*4, y0+10), (p.X(rx)+k_*4+2, y0+34+k_*4)], BG*1.2, g=0.3)


def page_fb2():
    R = rows([(255, [1]), (245, [0.5, 0.5]), (260, [1])])
    with Panel(*R[0]) as p:
        garden(p, p.Y(0.42), 63, clouds=True)
        pond(p, p.Y(0.32))
        tree(p.X(0.9), p.Y(0.4), 1.4, seed=64)
        shape(ell(p.X(0.4), p.Y(0.08), 30, 8, 24), 0.4, BG)
        tin(p.X(0.4), p.Y(0.06), 1.2)
        young(p.X(0.22), p.Y(0.04), 1.5, "deda", right="point", mood="happy", look=(1, -1))
        young(p.X(0.58), p.Y(0.04), 1.45, "verka", flip=True, mood="grin", look=(1, -1))
        young(p.X(0.08), p.Y(0.04), 1.45, "franta", mood="happy", right="hold", look=(1, -1),
              item=lambda x, y: stroke([(x, y), (x+2, y-30)], 2.4, g=0.4))
        old_photo(p)
        caption(p, "Jednou zakopali u starého rybníka svůj největší poklad.", w=250)
    with Panel(*R[1]) as p:
        bg_fill(p, P.PHOTO_BG)
        map_half(p.X(0.12), p.Y(0.12), 1.3, "L"); map_half(p.X(0.12), p.Y(0.12), 1.3, "R")
        young(p.X(0.83), p.Y(0.02), 1.4, "deda", right="point", mood="happy", flip=True, look=(1, -0.3))
        old_photo(p)
        bubble(p.X(0.05), p.Y(0.95), p.w*0.7, "Nakreslím mapu, ať ten poklad zase najdeme.", p.X(0.78), p.Y(0.75))
    with Panel(*R[2]) as p:
        bg_fill(p, 1.0); rays(p, p.X(0.5), p.Y(0.5), 0.9)
        map_half(p.X(0.5)-78, p.Y(0.42), 1.0, "L", rot=10)
        map_half(p.X(0.5)-50, p.Y(0.42), 1.0, "R", rot=-10)
        young(p.X(0.14), p.Y(0.02), 1.3, "deda", right="point", mood="determined", look=(1, 0.5))
        young(p.X(0.86), p.Y(0.02), 1.25, "verka", right="point", flip=True, mood="determined", look=(1, 0.5))
        sfx(p.X(0.4), p.Y(0.85), "RUP!", 26, -6)
        old_photo(p)
        caption(p, "A mapu roztrhli napůl. Poklad smí hledat jen celý klub!", w=p.w-14, size=12, where="bl")
    with Panel(*R[3]) as p:
        attic(p, floor_y=0.16, window=(0.5, 0.62), seed=15)
        chest(p.X(0.3), p.Y(0.05), 0.55, open_=True)
        young(p.X(0.14), p.Y(0.03), 1.3, "deda", right="front", mood="surprised", look=(1, 0),
              item=lambda x, y: map_half(x-8, y-20, 0.45, "L"))
        young(p.X(0.8), p.Y(0.03), 1.3, "verka", flip=True, right="back", left="back", mood="grin", look=(1, 0))
        old_photo(p)
        bubble(p.X(0.3), p.Y(0.95), 210, "Svou půlku schovám tak, že ji nikdo nenajde!", p.X(0.76), p.Y(0.6))
        bubble(p.X(0.04), p.Y(0.95), 90, "Ani já?", p.X(0.15), p.Y(0.6))
        bubble(p.X(0.62), p.Y(0.78), 180, "Ani ty! Ale nechám ti hádanku.", p.X(0.8), p.Y(0.58))
    page_end()


# =================================================================== 10 – flashback: Věrka moves away, key hidden
def page_fb3():
    R = rows([(260, [1]), (245, [0.5, 0.5]), (255, [1])])
    with Panel(*R[0]) as p:
        garden(p, p.Y(0.22), 67, house_x=0.82, house_s=1.05)
        fence(p.X(0.3), p.X(0.62), p.Y(0.2), 40)
        young(p.X(0.5), p.Y(0.04), 1.55, "verka", right="wave", mood="happy", look=(-1, 0), flip=True)
        suitcase(p.X(0.56), p.Y(0.04), 46, 30)
        young(p.X(0.12), p.Y(0.04), 1.55, "deda", right="wave", mood="sad", look=(1, 0))
        young(p.X(0.27), p.Y(0.04), 1.5, "franta", right="wave", mood="sad", look=(1, 0))
        old_photo(p)
        caption(p, "Pak se Věrka s rodiči odstěhovala daleko do města.", w=250)
        bubble(p.X(0.55), p.Y(0.82), 200, "Nezapomeňte na Klub Hvězdička!", p.X(0.5), p.Y(0.62))
    with Panel(*R[1]) as p:
        attic(p, floor_y=0.14, dark=0.45, seed=16)
        beam_light(p.X(0.42), p.Y(0.42), p.X(0.8), p.Y(0.0), p.X(1.0), p.Y(0.25), 0.3)
        young(p.X(0.3), p.Y(0.02), 1.5, "deda", right="lens", mood="sad", look=(1, -0.5),
              item=lambda x, y: torch(x, y, 10))
        old_photo(p)
        caption(p, "„Hledal jsem Věrčinu půlku mapy… ale nikdy jsem ji nenašel.“", w=p.w-14, size=12)
    with Panel(*R[2]) as p:
        planks(p, 0.72, 22, 3)
        floor(p, p.Y(0.14), 0.52)
        shelf(p.X(0.45), p.X(1.02), p.Y(0.42))
        boot(p.X(0.72), p.Y(0.445), 1.4)
        young(p.X(0.3), p.Y(0.02), 1.5, "deda", right="up", mood="think", look=(1, 0.5),
              item=lambda x, y: key(x+4, y+6, 0.8, rot=70, tag=True))
        old_photo(p)
        caption(p, "„Tak jsem truhlu zamkl a klíč schoval do staré boty v kůlně.“", w=p.w-14, size=12)
    with Panel(*R[3]) as p:
        attic(p, floor_y=0.18, window=(0.86, 0.62), dark=0.2, seed=17)
        deda(p.X(0.47), p.Y(0.03), 1.45, mood="sad", right="front", look=(0, -0.5),
             item=lambda x, y: notebook(x, y+2, 1.4))
        hanka(p.X(0.27), p.Y(0.03), 1.4, mood="worried", right="up", look=(1, 0.5))
        alica(p.X(0.68), p.Y(0.03), 1.5, flip=True, mood="determined", right="up", look=(1, 0.5))
        caption(p, "„A pak jsem na ten klíč úplně zapomněl.“", w=230)
        bubble(p.X(0.02), p.Y(0.78), 140, "Dědo, nebuď smutný.", p.X(0.22), p.Y(0.6))
        bubble(p.X(0.68), p.Y(0.97), 170, "My tu druhou půlku najdeme!", p.X(0.7), p.Y(0.72))
    page_end()


# =================================================================== 11 – Věrka's riddle + the noises again
def page_riddle():
    R = rows([(270, [1]), (230, [0.5, 0.5]), (260, [1])])
    with Panel(*R[0]) as p:
        bg_fill(p, 0.9)
        notebook_big(p.X(0.1), p.Y(0.07), p.w*0.8, p.h*0.72, "HÁDANKA OD VĚRKY:",
                     ["Moje půlka spí tam,", "kam ráno svítí hvězdička.", "Od hvězdičky sedm prken,", "pod prknem, které zpívá."])
        star(p.X(0.82), p.Y(0.66), 12, 0.95)
        caption(p, "Na poslední stránce zápisníku je hádanka.", w=280)
    with Panel(*R[1]) as p:
        attic(p, floor_y=0.12, dark=0.3, seed=18)
        alica(p.X(0.72), head_y(p, 0.48, 89.8, 2.5), 2.5, mood="think", right="chin", look=(-1, 0.5), shadow=False)
        bubble(p.X(0.03), p.Y(0.95), p.w*0.55, "Kam svítí hvězdička? Hvězdy přece svítí v noci…", p.X(0.6), p.Y(0.55))
    with Panel(*R[2]) as p:
        attic(p, floor_y=0.12, dark=0.3, seed=19)
        deda(p.X(0.68), head_y(p, 0.42, 114.8, 2.3), 2.3, flip=True, mood="sad", look=(1, -0.5), shadow=False)
        bubble(p.X(0.03), p.Y(0.95), p.w*0.55, "Tu hádanku jsem nikdy nerozluštil.", p.X(0.55), p.Y(0.5))
    with Panel(*R[3]) as p:
        attic(p, floor_y=0.18, window=(0.86, 0.66), dark=0.6, seed=20)
        chest(p.X(0.16), p.Y(0.05), 0.55, open_=True)
        deda(p.X(0.42), p.Y(0.03), 1.45, mood="surprised", look=(1, 0.5))
        alica(p.X(0.55), p.Y(0.03), 1.55, mood="surprised", look=(1, 0.5))
        hanka(p.X(0.67), p.Y(0.03), 1.45, mood="wow", torch=True, right="lens", look=(1, 0.5))
        sfx(p.X(0.72), p.Y(0.85), "ŠŠŠŠ!", 22, -8)
        sfx(p.X(0.83), p.Y(0.55), "CHRRR!", 18, 8)
        sfx(p.X(0.05), p.Y(0.85), "ŤUK ŤUK!", 16, 6)
        bubble(p.X(0.25), p.Y(0.97), 150, "Zase ty zvuky!", p.X(0.63), p.Y(0.66), whisper=True)
    page_end()


# =================================================================== 12 – the owls
def page_owls():
    R = rows([(220, [1]), (320, [1]), (220, [0.5, 0.5])])
    with Panel(*R[0], bg=0.12) as p:
        for (ex, ey, r) in ((0.6, 0.64, 13), (0.73, 0.46, 6), (0.82, 0.5, 6), (0.91, 0.45, 6)):
            for sx in (-1, 1):
                shape(ell(p.X(ex)+sx*r*1.1, p.Y(ey), r, r, 24), 0.95, 1.0)
                dot(p.X(ex)+sx*r*1.1, p.Y(ey), r*0.45, 0.0)
        beam_light(p.X(0.22), p.Y(0.36), p.X(0.55), p.Y(0.05), p.X(0.55), p.Y(0.35), 0.2)
        hanka(p.X(0.14), p.Y(0.02), 1.35, mood="wow", torch=True, right="lens", look=(1, 0.3))
        alica(p.X(0.03), p.Y(0.02), 1.4, mood="whisper", right="hush", look=(1, 0.3))
        bubble(p.X(0.24), p.Y(0.95), 170, "Hanko, posviť tam…", p.X(0.08), p.Y(0.75), whisper=True)
    with Panel(*R[1]) as p:
        attic(p, floor_y=0.12, window=(0.18, 0.75), dark=0.25, seed=21, beam=0.42)
        beam_light(p.X(0.0), p.Y(0.0), p.X(0.3), p.Y(1.0), p.X(1.0), p.Y(0.85), 0.3)
        # nest: an old basket on the tie beam
        bx, by = p.X(0.55), p.Y(0.42)+5
        owl(p.X(0.82), by, 2.4, flip=True, mood="wide")
        for i, (dx, m) in enumerate(((-48, "sleepy"), (0, "hiss"), (48, "open"))):
            owlet(bx+dx, by+4, 1.9, mood=m)
        shape([(bx-74, by-4), (bx+74, by-4), (bx+68, by+22), (bx-68, by+22)], 0.7, BG)
        for k_ in range(-68, 72, 10): stroke([(bx+k_, by-4), (bx+k_*0.95, by+22)], BG*0.5)
        caption(p, "Na trámu sedí sova pálená. A v košíku má tři malé sovičky!", w=280, where="bl")
        sfx(p.X(0.5), p.Y(0.82), "ŠŠŠ!", 20, -6)
    with Panel(*R[2]) as p:
        attic(p, floor_y=0.12, dark=0.35, seed=22)
        deda(p.X(0.7), head_y(p, 0.4, 114.8, 2.2), 2.2, flip=True, mood="whisper", right="hush", look=(1, 0.3), shadow=False)
        bubble(p.X(0.03), p.Y(0.95), p.w*0.55, "Malé sovičky syčí a chrápou, když mají hlad.", p.X(0.58), p.Y(0.5), whisper=True)
    with Panel(*R[3]) as p:
        attic(p, floor_y=0.12, dark=0.35, seed=23)
        hanka(p.X(0.7), head_y(p, 0.4, 70.2, 2.6), 2.6, mood="grin", look=(1, 0.3), shadow=False)
        bubble(p.X(0.03), p.Y(0.95), p.w*0.55, "Tak to vy jste dělaly ty zvuky!", p.X(0.56), p.Y(0.5), whisper=True)
    page_end()


# =================================================================== 13 – owl facts
def page_owl_facts():
    R = rows([(250, [1]), (250, [0.5, 0.5]), (260, [1])])
    with Panel(*R[0]) as p:
        night_sky(p, 0.55)
        moon(p.X(0.88), p.Y(0.35), 22)
        for (sx_, sy_) in ((0.5, 0.7), (0.62, 0.55), (0.7, 0.8), (0.95, 0.6), (0.45, 0.4), (0.8, 0.15)):
            star(p.X(sx_), p.Y(sy_), 3, 0.95)
        tube([(p.x-5, p.Y(0.12)), (p.X(0.45), p.Y(0.1)), (p.X(0.55), p.Y(0.14))], 12, 7, P.BARK, sh=0)
        for lx in (0.08, 0.36, 0.5):
            leaf(p.X(lx), p.Y(0.17), 6, 30, P.LEAF_LIGHT)
        owl(p.X(0.25), p.Y(0.1)+4, 3.6, mood="open")
        caption(p, "Sova pálená loví v noci myši. Létá úplně potichu, nikdo ji neuslyší.", w=260, where="tr")
        for k_ in range(3):
            stroke(bez((p.X(0.55), p.Y(0.35)-k_*14), (p.X(0.65), p.Y(0.4)-k_*14), (p.X(0.75), p.Y(0.3)-k_*14), (p.X(0.85), p.Y(0.35)-k_*14)), 1.0, g=0.5)
    with Panel(*R[1]) as p:
        bg_fill(p, 0.93)
        owl(p.X(0.4), p.Y(0.08), 3.0, mood="open", flip=True)
        stroke(ell(p.X(0.4), p.Y(0.08)+38*3, 60, 50, 30, 20, 250), 1.6)
        shape([(p.X(0.4)+52, p.Y(0.08)+38*3+30), (p.X(0.4)+64, p.Y(0.08)+38*3+18), (p.X(0.4)+44, p.Y(0.08)+38*3+16)], 0.0, 1.0)
        caption(p, "Umí otočit hlavu skoro dozadu!", w=p.w-14, size=12)
    with Panel(*R[2]) as p:
        bg_fill(p, 0.93)
        pellet(p.X(0.45), p.Y(0.4), 6.0, rot=10)
        magnifier(p.X(0.8), p.Y(0.2), ang=30, r=16)
        hand_text(p.X(0.55), p.Y(0.66), 90, "chlupy", "SHB", 14, align="left")
        stroke([(p.X(0.58), p.Y(0.64)), (p.X(0.5), p.Y(0.47))], 0.9)
        hand_text(p.X(0.08), p.Y(0.18), 90, "kostičky", "SHB", 14, align="left")
        stroke([(p.X(0.2), p.Y(0.23)), (p.X(0.35), p.Y(0.36))], 0.9)
        caption(p, "Co sova sní a nestráví, to vyplivne. Tomu se říká vývržek.", w=p.w-14, size=12)
    with Panel(*R[3]) as p:
        attic(p, floor_y=0.12, dark=0.15, seed=24, beam=0.7)
        bx, by = p.X(0.8), p.Y(0.7)+5
        for dx in (-26, 0, 26): owlet(bx+dx, by+4, 1.0, mood="sleepy")
        owl(bx+56, by, 1.2, flip=True, mood="sleepy")
        deda(p.X(0.62), p.Y(0.03), 1.45, flip=True, mood="happy", look=(1, 0))
        alica(p.X(0.12), p.Y(0.03), 1.55, mood="happy", look=(1, 0))
        hanka(p.X(0.27), p.Y(0.03), 1.45, mood="grin", look=(1, 0))
        bubble(p.X(0.02), p.Y(0.97), 170, "Tak to nebylo žádné strašidlo, jenom sovičky!", p.X(0.25), p.Y(0.6), whisper=True)
        bubble(p.X(0.36), p.Y(0.97), 170, "Sovy jsou vzácné. Necháme je tu v klidu bydlet.", p.X(0.6), p.Y(0.74), whisper=True)
    page_end()


# =================================================================== 14 – the star of light
def page_starlight():
    R = rows([(275, [1]), (230, [0.5, 0.5]), (255, [1])])
    with Panel(*R[0]) as p:
        attic(p, floor_y=0.3, window=(0.66, 0.62), seed=25)
        wx, wy = p.X(0.66), p.Y(0.62)
        beam_light(wx, wy, p.X(0.74), p.Y(0.12), p.X(0.92), p.Y(0.2), 0.3)
        star_spot(p.X(0.84), p.Y(0.16), 16)
        hanka(p.X(0.28), p.Y(0.03), 1.55, mood="wow", right="point", look=(1, -1))
        alica(p.X(0.1), p.Y(0.03), 1.6, mood="surprised", look=(1, -0.5))
        caption(p, "Ráno vyšlo sluníčko a posvítilo okýnkem na půdu.", w=230, where="tr")
        bubble(p.X(0.02), p.Y(0.97), 160, "Alico! Hvězdička svítí na zem!", p.X(0.28), p.Y(0.62))
    with Panel(*R[1]) as p:
        attic(p, floor_y=0.12, dark=0.1, seed=26)
        alica(p.X(0.55), p.Y(-0.6), 2.9, mood="wow", book=True, look=(-1, 0.5), shadow=False)
        bubble(p.X(0.03), p.Y(0.95), p.w*0.6, "Kam ráno svítí hvězdička! To je z hádanky!", p.X(0.45), p.Y(0.66))
    with Panel(*R[2]) as p:
        fill([(p.x, p.y), (p.x+p.w, p.y), (p.x+p.w, p.y+p.h), (p.x, p.y+p.h)], P.ATTIC_FLOOR)
        step = p.w/8.2
        for i in range(9):
            stroke([(p.x+8+i*step, p.y), (p.x+8+i*step, p.y+p.h)], BG*1.2)
        star_spot(p.x+8+step*0.5, p.Y(0.5), 18, 0.9)
        for i in range(1, 8):
            hand_text(p.x+8+i*step+2, p.Y(0.15), step-4, str(i), "SHB", 22)
        caption(p, "…pět, šest, sedm!", w=p.w-14, size=12)
    with Panel(*R[3]) as p:
        attic(p, floor_y=0.18, seed=27)
        # the low corner under the roof slope
        slope = [(p.X(0.62), p.y+p.h+5), (p.x+p.w+5, p.Y(0.38)), (p.x+p.w+5, p.y+p.h+5)]
        form(slope, P.ATTIC_ROOF, w=BG, sh=0)
        tube([(p.X(0.62), p.y+p.h+5), (p.x+p.w+5, p.Y(0.38))], 12, 12, P.ATTIC_BEAM, lw=BG, sh=0)
        fill([(p.X(0.85), p.Y(0.18)), (p.X(0.95), p.Y(0.18)), (p.X(0.95), p.Y(0.2)), (p.X(0.85), p.Y(0.2))], 0.3)
        fill([(p.X(0.78), p.Y(0.18)), (p.x+p.w+5, p.Y(0.18)), (p.x+p.w+5, p.Y(0.38))], 0.1, 0.55)
        deda(p.X(0.54), p.Y(0.03), 1.3, flip=True, mood="worried", look=(1, 0))
        alica(p.X(0.38), p.Y(0.03), 1.5, mood="worried", right="point", look=(1, 0))
        hanka(p.X(0.14), p.Y(0.03), 1.45, mood="determined", right="up", look=(1, 0.3))
        bubble(p.X(0.26), p.Y(0.97), 170, "Sedmé prkno je až vzadu pod střechou.", p.X(0.38), p.Y(0.66))
        bubble(p.X(0.6), p.Y(0.97), 110, "Tam se nevejdu.", p.X(0.54), p.Y(0.72))
        bubble(p.X(0.01), p.Y(0.97), 120, "Ale já jo! Jsem malá detektivka!", p.X(0.12), p.Y(0.55))
    page_end()


def held_map(x, y):
    """Věrka's half of the map in a flipped figure's hand, un-mirrored so the writing reads"""
    with T(x, y, 1.0, flip=True):
        map_half(-38, -34, 0.42, "R")


# =================================================================== 15 – Hanka finds the tin
def page_found():
    R = rows([(250, [0.5, 0.5]), (255, [1]), (255, [1])])
    with Panel(*R[0]) as p:
        attic(p, floor_y=0.14, dark=0.3, seed=28)
        slope = [(p.x-5, p.Y(0.72)), (p.x+p.w+5, p.Y(0.98)), (p.x+p.w+5, p.y+p.h+5), (p.x-5, p.y+p.h+5)]
        form(slope, P.ATTIC_ROOF, w=BG, sh=0)
        owlet(p.X(0.78), p.Y(0.72), 1.0, mood="sleepy"); owlet(p.X(0.9), p.Y(0.73), 1.0, mood="open")
        hanka(p.X(0.42), p.Y(0.03), 1.6, mood="whisper", torch=True, right="lens", look=(1, -0.5))
        bubble(p.X(0.03), p.Y(0.97), p.w*0.6, "Potichoučku… ať sovičky nevzbudím.", p.X(0.36), p.Y(0.56), whisper=True)
    with Panel(*R[1]) as p:
        fill([(p.x, p.y), (p.x+p.w, p.y), (p.x+p.w, p.y+p.h), (p.x, p.y+p.h)], P.ATTIC_FLOOR)
        for i in range(-1, 6): stroke([(p.X(0.2*i+0.1), p.y), (p.X(0.2*i+0.1), p.y+p.h)], BG*1.2)
        # close-up: Hanka's boots on the squeaky plank
        hanka(p.X(0.55), p.Y(0.12), 6.0, mood="whisper", shadow=False)
        sfx(p.X(0.12), p.Y(0.65), "VRZ!", 28, 10)
        bubble(p.X(0.4), p.Y(0.95), p.w*0.55, "Tohle prkno zpívá!", p.X(0.5), p.Y(0.4), whisper=True)
    with Panel(*R[2]) as p:
        attic(p, floor_y=0.3, dark=0.2, seed=29)
        fill([(p.X(0.45), p.Y(0.08)), (p.X(0.75), p.Y(0.08)), (p.X(0.75), p.Y(0.22)), (p.X(0.45), p.Y(0.22))], 0.1)
        with T(p.X(0.78), p.Y(0.15), 1.0, rot=35):
            form([(-4, -8), (90, -8), (90, 8), (-4, 8)], P.ATTIC_FLOOR, w=BG*1.2, sh=0)
        tin(p.X(0.6), p.Y(0.1), 1.8)
        hanka(p.X(0.26), p.Y(0.03), 1.75, mood="wow", right="point", look=(1, -1))
        bubble(p.X(0.03), p.Y(0.97), 200, "Mám to! Plechovka se hvězdičkou!", p.X(0.25), p.Y(0.72), whisper=True)
    with Panel(*R[3]) as p:
        attic(p, floor_y=0.18, window=(0.1, 0.62), seed=30)
        chest(p.X(0.5), p.Y(0.02), 0.55)
        tin(p.X(0.5), p.Y(0.02)+47, 1.3, open_=True)
        deda(p.X(0.74), p.Y(0.03), 1.4, flip=True, mood="laugh", right="front", look=(1, -0.3),
             item=held_map)
        alica(p.X(0.28), p.Y(0.03), 1.6, mood="grin", look=(1, -0.3))
        hanka(p.X(0.14), p.Y(0.03), 1.45, mood="grin", right="up", look=(1, -0.3))
        bubble(p.X(0.55), p.Y(0.97), 200, "Věrčina půlka mapy! Po tolika letech!", p.X(0.74), p.Y(0.74))
        bubble(p.X(0.02), p.Y(0.97), 210, "Alica četla hádanku a já hledala!", p.X(0.14), p.Y(0.66))
    page_end()


# =================================================================== 16 – the whole map
def page_map():
    R = rows([(330, [1]), (200, [0.5, 0.5]), (230, [1])])
    with Panel(*R[0]) as p:
        bg_fill(p, P.CHEST)
        for k_ in range(1, 6): stroke([(p.x, p.Y(k_/6)), (p.x+p.w, p.Y(k_/6))], BG*0.6)
        map_half(p.X(0.5)-3.2*60-4, p.Y(0.12), 3.2, "L", rot=-2)
        map_half(p.X(0.5)-3.2*60+4, p.Y(0.12), 3.2, "R", rot=1)
        caption(p, "Obě půlky do sebe přesně zapadly.", w=240)
    with Panel(*R[1]) as p:
        attic(p, floor_y=0.12, dark=0.1, seed=31)
        alica(p.X(0.5), p.Y(-0.9), 3.0, mood="wow", look=(1, 0), shadow=False)
        bubble(p.X(0.03), p.Y(0.95), p.w*0.92, "Je to mapa ke starému rybníku!", p.X(0.5), p.Y(0.5))
    with Panel(*R[2]) as p:
        bg_fill(p, 1.0); rays(p, p.X(0.5), p.Y(0.4), 0.9)
        hanka(p.X(0.5), p.Y(0.02), 1.5, mood="grin", right="up", look=(0, 0.5))
        sfx(p.X(0.05), p.Y(0.72), "POKLAD!", 22, 8)
    with Panel(*R[3]) as p:
        attic(p, floor_y=0.18, window=(0.5, 0.66), seed=32)
        deda(p.X(0.5), p.Y(0.03), 1.55, mood="laugh", left="wave", right="wave")
        alica(p.X(0.28), p.Y(0.03), 1.55, mood="grin", right="up", look=(1, 0.5))
        hanka(p.X(0.72), p.Y(0.03), 1.45, flip=True, mood="grin", right="up", look=(1, 0.5))
        bubble(p.X(0.58), p.Y(0.97), 230, "Klub Hvězdička je zpátky! A vy dvě jste jeho nové členky.", p.X(0.52), p.Y(0.72))
        bubble(p.X(0.03), p.Y(0.97), 100, "Hurá!", p.X(0.26), p.Y(0.72))
    page_end()


# =================================================================== 17 – owl box, cocoa, solved, good night
def page_end_story():
    R = rows([(260, [1]), (240, [0.5, 0.5]), (260, [1])])
    with Panel(*R[0]) as p:
        garden(p, p.Y(0.14), 71, clouds=True)
        gx = p.X(0.64)
        gable_end(gx, p.Y(0.14), 150, 120, 238, seed=11, low_window=False)
        tufts(p, p.Y(0.02), p.Y(0.12), 6, 23)
        owl_box(gx+100, p.Y(0.62), 1.15)
        ladder(gx+45, p.Y(0.04), p.Y(0.62), 36)
        deda(gx+45, p.Y(0.2), 1.3, mood="happy", right="up", look=(1, 1), shadow=False,
             item=lambda x, y: hammer(x, y))
        crate(p.X(0.42), p.Y(0.03), 40, 26)
        saw(p.X(0.42)+4, p.Y(0.03)+26, 0.45)
        alica(p.X(0.18), p.Y(0.03), 1.6, mood="grin", right="up", look=(1, 0.5))
        hanka(p.X(0.33), p.Y(0.03), 1.5, mood="happy", look=(1, 0.5))
        caption(p, "Odpoledne vyrobí budku pro sovy, aby tu mohly bydlet napořád.", w=250)
        sfx(gx+95, p.Y(0.42), "ŤUK!", 16, -8)
    with Panel(*R[1]) as p:
        kitchen(p)
        mug(p.X(0.2), p.Y(0.38), 1.4); mug(p.X(0.4), p.Y(0.38), 1.4)
        babicka(p.X(0.72), p.Y(0.03), 1.55, flip=True, mood="laugh", right="front", look=(1, 0),
                item=lambda x, y: mug(x-8, y-6, 1.1))
        bubble(p.X(0.03), p.Y(0.95), p.w*0.6, "Detektivky si zaslouží kakao!", p.X(0.66), p.Y(0.8))
    with Panel(*R[2]) as p:
        bg_fill(p, 0.9)
        notebook_big(p.X(0.08), p.Y(0.1), p.w*0.84, p.h*0.72, "PŘÍPAD Č. 2:",
                     ["Zvuky na půdě", "Byly to sovičky!", "", "VYŘEŠENO!"], check=True)
    with Panel(*R[3]) as p:
        (ahx, ahy), (hhx, hhy) = night_bed_scene(p, "happy", "sleepy", alica_look=(1, 0.5), s=1.4)
        sfx(p.X(0.36), p.Y(0.93), "chrrr…", 14, 4)
        bubble(p.X(0.3), p.Y(0.84), 150, "Dobrou noc, sovičky.", ahx, ahy+16, whisper=True)
        box = [(p.X(0.03), p.Y(0.04)), (p.X(0.4), p.Y(0.04)+2), (p.X(0.4)-1, p.Y(0.04)+44), (p.X(0.03)+1, p.Y(0.04)+43)]
        fill(box, 1.0)
        for a_, b_ in ((0, 1), (1, 2), (2, 3), (3, 0)): stroke([box[a_], box[b_]], 1.5)
        hand_text(p.X(0.03), p.Y(0.04)+16, p.w*0.37, "Pokračování příště…", "SHB", 17)
    page_end()


# =================================================================== 18 – activity: quiz
def page_quiz():
    with Panel(M, 40, W-2*M, H-80) as p:
        box = [(p.X(0.05), p.Y(0.885)), (p.X(0.95), p.Y(0.89)), (p.X(0.95), p.Y(0.885)+64), (p.X(0.05), p.Y(0.885)+62)]
        fill(box, 0.92)
        for a_, b_ in ((0, 1), (1, 2), (2, 3), (3, 0)): stroke([box[a_], box[b_]], 1.5)
        hand_text(p.X(0.05), p.Y(0.885)+24, p.w*0.9, "Detektivní zápisník", "SHB", 26)
        magnifier(p.X(0.1), p.Y(0.87), ang=-30, r=12)
        y = p.Y(0.82)
        qs = [("1. Kdo v noci ťukal a chrápal na půdě?", ["strašidlo", "sovičky", "Micka"]),
              ("2. Co bylo na okýnku a na klíči?", ["srdíčko", "měsíc", "hvězdička"]),
              ("3. Jak se jmenoval dědův klub?", ["Klub Hvězdička", "Klub Sova", "Klub Klíč"]),
              ("4. Kdo se vešel až pod střechu?", ["děda", "Alica", "Hanka"]),
              ("5. Kam vede celá mapa?", ["k rybníku", "do lesa", "do kůlny"])]
        for q, opts in qs:
            hand_text(p.X(0.06), y, p.w*0.9, q, "SH", 16, align="left")
            for i, o in enumerate(opts):
                hand_text(p.X(0.12) + i*150, y-28, 140, o, "SHB", 16, align="left")
            y -= 70
        y -= 10
        hand_text(p.X(0.06), y, p.w*0.9, "Nakresli, co myslíš, že je zakopané u rybníka:", "SHB", 16, align="left")
        shape(rrect(p.X(0.06), p.Y(0.05), p.w*0.88, y - p.Y(0.05) - 16, 10), 1.0, 1.6)
        map_half(p.X(0.72), p.Y(0.07), 0.8, "L"); map_half(p.X(0.72), p.Y(0.07), 0.8, "R")
    page_end()


# =================================================================== 19 – activity: owl maze
def maze_cells(n, m, seed=7):
    r = random.Random(seed)
    walls = {(x, y): {"N", "S", "E", "W"} for x in range(n) for y in range(m)}
    D = {"N": (0, 1, "S"), "S": (0, -1, "N"), "E": (1, 0, "W"), "W": (-1, 0, "E")}
    stack = [(0, m-1)]; seen = {(0, m-1)}
    while stack:
        cx, cy = stack[-1]
        opts = [(d, cx+dx, cy+dy, o) for d, (dx, dy, o) in D.items() if (cx+dx, cy+dy) in walls and (cx+dx, cy+dy) not in seen]
        if not opts:
            stack.pop(); continue
        d, nx, ny, o = r.choice(opts)
        walls[(cx, cy)].discard(d); walls[(nx, ny)].discard(o)
        seen.add((nx, ny)); stack.append((nx, ny))
    return walls


def page_maze():
    with Panel(M, 40, W-2*M, H-80) as p:
        box = [(p.X(0.05), p.Y(0.885)), (p.X(0.95), p.Y(0.89)), (p.X(0.95), p.Y(0.885)+64), (p.X(0.05), p.Y(0.885)+62)]
        fill(box, 0.92)
        for a_, b_ in ((0, 1), (1, 2), (2, 3), (3, 0)): stroke([box[a_], box[b_]], 1.5)
        hand_text(p.X(0.05), p.Y(0.885)+24, p.w*0.9, "Pomoz mamince sově k sovičkám", "SHB", 24)
        n, m = 9, 11
        cell = min(p.w*0.84/n, p.h*0.66/m)
        x0 = p.X(0.5) - cell*n/2; y0 = p.Y(0.13)
        walls = maze_cells(n, m)
        for (cx, cy), ws in walls.items():
            X0, Y0 = x0 + cx*cell, y0 + cy*cell
            if "S" in ws and not (cx == n-1 and cy == 0): stroke([(X0, Y0), (X0+cell, Y0)], 2.0)
            if "W" in ws and not (cx == 0 and cy == m-1): stroke([(X0, Y0), (X0, Y0+cell)], 2.0)
            if cy == m-1 and "N" in ws: stroke([(X0, Y0+cell), (X0+cell, Y0+cell)], 2.0)
            if cx == n-1 and "E" in ws: stroke([(X0+cell, Y0), (X0+cell, Y0+cell)], 2.0)
        owl(x0 - 36, y0 + (m-1)*cell + 4, 1.1, mood="open")
        for i, dx in enumerate((-18, 0, 18)):
            owlet(x0 + n*cell + 30 + dx, y0 - 30 + (i % 2)*4, 0.9, mood="open")
        hand_text(p.X(0.08), p.Y(0.06), p.w*0.84, "Najdi cestu a pak si sovičky vybarvi!", "SH", 16)
    page_end()


# =================================================================== 20 – next time
def page_next():
    with Panel(M, 40, W-2*M, H-80, bg=0.95) as p:
        hand_text(p.X(0.1), p.Y(0.93), p.w*0.8, "Příště v sešitě č. 3:", "SHB", 20)
        title(p.X(0.5), p.Y(0.84), "MAPA KE STARÉMU RYBNÍKU", 34)
        with Panel(p.X(0.08), p.Y(0.38), p.w*0.84, p.h*0.4, bg=0.9) as q:
            sky(q, 0.95); cloud(q.X(0.25), q.Y(0.85), 1.0)
            ground(q, q.Y(0.5))
            pond(q, q.Y(0.38), 0.4, 0.95)
            tree(q.X(0.12), q.Y(0.48), 1.6, seed=81)
            with T(q.X(0.68), q.Y(0.14), 1.0):
                stroke([(-9, -7), (9, 7)], 3.2, g=P.TAG_STAR); stroke([(9, -7), (-9, 7)], 3.2, g=P.TAG_STAR)
            alica(q.X(0.3), q.Y(0.05), 1.5, mood="determined", right="front", look=(1, 0),
                  item=lambda x, y: (map_half(x-2, y-14, 0.35, "L"), map_half(x-2, y-14, 0.35, "R")))
            hanka(q.X(0.45), q.Y(0.05), 1.45, mood="grin", look=(1, 0))
            joey(q.X(0.57), q.Y(0.05), 0.9, pose="sniff")
            hand_text(q.X(0.8), q.Y(0.7), 40, "?", "SHB", 34, align="left")
        hand_text(p.X(0.1), p.Y(0.32), p.w*0.8,
                  "Holky mají celou mapu! Co je zakopané u starého rybníka? A najde se někdy Věrka?", "SH", 16, lead=21)
        hand_text(p.X(0.3), p.Y(0.2), p.w*0.4, "Detektivní tým:", "SHB", 16)
        alica(p.X(0.08), p.Y(0.03), 0.95, mood="happy", right="wave")
        hanka(p.X(0.19), p.Y(0.03), 0.95, mood="grin")
        joey(p.X(0.33), p.Y(0.03), 0.75, mood="happy")
        tonda(p.X(0.5), p.Y(0.03), 0.9, mood="grin")
        babicka(p.X(0.63), p.Y(0.03), 0.88, mood="happy")
        deda(p.X(0.77), p.Y(0.03), 0.82, mood="happy", flip=True)
        owl(p.X(0.9), p.Y(0.03), 1.1, mood="open", flip=True)
        owlet(p.X(0.96), p.Y(0.03), 0.8)
    page_end()


cover(); page_night(); page_breakfast(); page_suspects(); page_clues(); page_climb(); page_chest()
page_fb1(); page_fb2(); page_fb3(); page_riddle(); page_owls(); page_owl_facts(); page_starlight()
page_found(); page_map(); page_end_story(); page_quiz(); page_maze(); page_next()
cv.save(); print("ok", PAGE[0] - 1, "pages")
