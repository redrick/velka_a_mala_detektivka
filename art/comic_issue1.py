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
from letter import Panel, caption, bubble, sfx, title, series_title, hand_text, thought

W, H = A4
M = 28; GUT = 9; TOP = H - 30
# Finished issues are kept in the repo: comics/<series>/<nn>_<title>.pdf
OUT = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                   "comics", "velka_a_mala_detektivka", "01_zahada_zmizelych_ponozek.pdf")
os.makedirs(os.path.dirname(OUT), exist_ok=True)
cv = canvas.Canvas(OUT, pagesize=A4); lib.set_canvas(cv)
cv.setTitle("Velká a malá detektivka – Případ č. 1: Záhada zmizelých ponožek")
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

def bg_fill(p, g):
    fill([(p.x, p.y), (p.x+p.w, p.y), (p.x+p.w, p.y+p.h), (p.x, p.y+p.h)], g)

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

# =================================================================== COVER
def cover():
    with Panel(M, 40, W-2*M, H-80) as p:
        sky(p, 0.95)
        cloud(p.X(0.22), p.Y(0.66), 1.3); cloud(p.X(0.8), p.Y(0.6), 1.0)
        hills(p, p.Y(0.3), 30, 0.87, 2)
        house(p.X(0.76), p.Y(0.27), 1.5)
        tree(p.X(0.12), p.Y(0.22), 2.3, seed=5)
        ground(p, p.Y(0.28), 0.9)
        path(p, [(p.X(0.52), p.Y(0.28)), (p.X(0.45), p.Y(0.15)), (p.X(0.35), p.y-5)],
                [(p.X(0.6), p.Y(0.28)), (p.X(0.62), p.Y(0.15)), (p.X(0.7), p.y-5)], 0.95)
        clothesline(p.X(0.28), p.X(0.56), p.Y(0.27), 95, ("shirt", "sock", "towel"))
        fence(p.X(0.86), p.x+p.w+5, p.Y(0.24), 38)
        tufts(p, p.Y(0.03), p.Y(0.26), 12, 4)
        footprints(p.X(0.48), p.Y(0.07), 3, 16, 5, 1.1)
        alica(p.X(0.3), p.Y(0.04), 3.2, right="lens", lens=True, mood="determined", look=(1, -0.3))
        hanka(p.X(0.62), p.Y(0.04), 3.2, mood="grin", flip=True)
        joey(p.X(0.8), p.Y(0.03), 2.0, pose="sniff", mood="happy")
        falling_leaves(p, 7, 9, 0.4)
        sock_item(p.X(0.94), p.Y(0.33), 1.6, rot=30)
    box = [(M+34, H-236), (W-M-30, H-232), (W-M-34, H-48), (M+30, H-52)]
    fill([(x+3, y-3) for x, y in box], 0.0, 0.25); fill(box, 1.0)
    for a_, b_ in ((0, 1), (1, 2), (2, 3), (3, 0)): stroke([box[a_], box[b_]], 1.8)
    series_title(W/2, H-98, H-160, 40, 66)
    hand_text(M+40, H-190, W-2*M-80, "Alica a Hanka", "SHB", 20)
    hand_text(M+40, H-217, W-2*M-80, "Případ č. 1: Záhada zmizelých ponožek", "SH", 15)
    magnifier(M+82, H-120, ang=-30, r=17)
    with T(W-M-88, H-112, 3.0):
        torch(0, 0, 25)
        for a in (5, 25, 45):
            ra = math.radians(a)
            stroke([(9.5*math.cos(math.radians(25))+math.cos(ra)*3, 9.5*math.sin(math.radians(25))+math.sin(ra)*3),
                    (9.5*math.cos(math.radians(25))+math.cos(ra)*7, 9.5*math.sin(math.radians(25))+math.sin(ra)*7)], 1.2)
    page_end()

# =================================================================== PAGE 2
def page2():
    R = rows([(262, [1]), (250, [0.5, 0.5]), (248, [1])])
    with Panel(*R[0]) as p:
        garden(p, p.Y(0.26), 1, house_x=0.87, house_s=0.95, tree_x=0.65, tree_s=1.3)
        tufts(p, p.Y(0.03), p.Y(0.24), 7, 2)
        alica(p.X(0.12), p.Y(0.05), 1.85, right="wave", mood="grin")
        hanka(p.X(0.28), p.Y(0.05), 1.85, mood="happy")
        joey(p.X(0.44), p.Y(0.05), 1.3, mood="happy")
        falling_leaves(p, 4, 1)
        caption(p, "Tohle je Alica. Je jí sedm let a nejvíc na světě má ráda záhady.", w=160)
        bubble(p.X(0.38), p.Y(0.96), 230, "Ahoj! Já jsem Alica. Tohle je moje sestřička Hanka a náš pes Joey.", p.X(0.16), p.Y(0.72))
    with Panel(*R[1]) as p:
        bg_fill(p, 0.93)
        shape(rrect(p.X(0.5), p.Y(0.1), p.w*0.46, p.h*0.62, 3), 0.85, 0.8)
        hanka(p.X(0.5), p.Y(-0.62), 4.1, mood="grin", shadow=False)
        caption(p, "Hance jsou čtyři roky. Všude s sebou nosí svoji opičku.", w=p.w-14, size=12)
    with Panel(*R[2]) as p:
        garden(p, p.Y(0.3), 5, clouds=False)
        tufts(p, p.Y(0.03), p.Y(0.27), 4, 12)
        joey(p.X(0.48), p.Y(0.06), 2.2, mood="happy")
        caption(p, "A Joey? Ten má nejlepší čumák v celé vesnici.", w=p.w-14, size=12)
        sfx(p.X(0.7), p.Y(0.62), "HAF!", 22, 10)
    with Panel(*R[3]) as p:
        garden(p, p.Y(0.24), 7, tree_x=0.07, tree_s=1.25)
        tufts(p, p.Y(0.03), p.Y(0.22), 6, 6)
        clothesline(p.X(0.4), p.X(0.8), p.Y(0.22), 112, ("shirt", "sock", "towel", "sock"))
        deda(p.X(0.9), p.Y(0.04), 1.4, flip=True, right="hold", mood="happy", look=(1, -0.3),
             item=lambda x, y: magnifier(x+1, y+8, ang=10, r=6))
        hanka(p.X(0.2), p.Y(0.05), 1.6, mood="surprised", look=(1, 0.3))
        alica(p.X(0.32), p.Y(0.05), 1.6, mood="wow", look=(1, 0.3))
        caption(p, "Na chalupě dostala Alica od dědy opravdovou detektivní lupu a zápisník.", w=250)
        bubble(p.X(0.55), p.Y(0.72), 150, "Každý detektiv potřebuje lupu!", p.X(0.84), p.Y(0.6))
    page_end()

# =================================================================== PAGE 3
def page3():
    R = rows([(250, [1]), (250, [0.5, 0.5]), (260, [1])])
    with Panel(*R[0]) as p:
        garden(p, p.Y(0.2), 3, tree_x=0.06, tree_s=1.2)
        tufts(p, p.Y(0.02), p.Y(0.18), 5, 7)
        clothesline(p.X(0.35), p.X(0.75), p.Y(0.2), 110, ("shirt", "sock", "towel", "sock"))
        basket(p.X(0.86), p.Y(0.05))
        babicka(p.X(0.66), p.Y(0.04), 1.45, flip=True, mood="worried", right="chin", look=(1, 0.8))
        alica(p.X(0.22), p.Y(0.04), 1.6, mood="surprised", look=(1, 0.3), right="point")
        hanka(p.X(0.1), p.Y(0.04), 1.6, mood="surprised", look=(1, 0.3))
        caption(p, "Jednoho rána…", w=110)
        bubble(p.X(0.42), p.Y(0.97), 300, "To je divné… Včera zmizela jedna ponožka, dneska druhá. A taky rukavice a klubíčko vlny!", p.X(0.63), p.Y(0.8))
    with Panel(*R[1]) as p:
        bg_fill(p, 1.0); rays(p, p.X(0.5), p.Y(0.45))
        hanka(p.X(0.2), p.Y(0.03), 1.75, mood="grin")
        alica(p.X(0.5), p.Y(0.03), 1.8, mood="determined", right="lens", lens=True, look=(1, 0.3))
        joey(p.X(0.82), p.Y(0.03), 1.05, mood="bark", flip=True)
        bubble(p.X(0.03), p.Y(0.97), 200, "To je případ pro detektivky Alicu a Hanku!", p.X(0.45), p.Y(0.8))
        sfx(p.X(0.7), p.Y(0.5), "HAF!", 22, -10)
    with Panel(*R[2]) as p:
        bg_fill(p, 0.9)
        notebook_big(p.X(0.1), p.Y(0.1), p.w*0.8, p.h*0.64, "ZMIZELO:",
                     ["1. ponožka", "2. ponožka", "3. rukavice", "4. klubíčko vlny"])
        with T(p.X(0.86), p.Y(0.24), 1.0, rot=-35):
            shape([(-3, 0), (3, 0), (3, 60), (-3, 60)], 0.8)
            shape([(-3, 0), (3, 0), (0, -9)], 1.0)
        caption(p, "Alica si všechno pečlivě zapíše.", w=p.w-14)
    with Panel(*R[3]) as p:
        garden(p, p.Y(0.36), 4, clouds=False)
        tufts(p, p.Y(0.02), p.Y(0.3), 5, 8)
        clothesline(p.X(0.03), p.X(0.4), p.Y(0.35), 95, ("sock", "towel"))
        footprints(p.X(0.33), p.Y(0.11), 4, 13, 5, 0.8)
        hanka(p.X(0.2), p.Y(0.05), 1.55, mood="wow", right="point", look=(1, -1))
        alica(p.X(0.08), p.Y(0.05), 1.55, mood="surprised", right="lens", lens=True, look=(1, -1))
        joey(p.X(0.5), p.Y(0.05), 0.95, pose="sniff")
        cx, cy, r = p.X(0.8), p.Y(0.45), 72
        shape(ell(cx, cy, r, r, 60), 0.9, 1.8)
        C.saveState(); C.clipPath(poly(ell(cx, cy, r-2, r-2, 60)), stroke=0, fill=0)
        footprints(cx-45, cy-30, 5, 22, 14, 2.1)
        C.restoreState()
        stroke([(p.X(0.43), p.Y(0.15)), (cx-r+6, cy-22)], 0.8)
        bubble(p.X(0.02), p.Y(0.97), 190, "Alico! Tady dole jsou malinkaté stopy!", p.X(0.2), p.Y(0.66))
        sfx(p.X(0.47), p.Y(0.42), "ČMUCH", 15, 12)
    page_end()

# =================================================================== PAGE 4
def page4():
    R = rows([(275, [1]), (240, [0.5, 0.5]), (245, [1])])
    with Panel(*R[0]) as p:
        garden(p, p.Y(0.14), 9, clouds=False)
        tufts(p, p.Y(0.02), p.Y(0.12), 4, 9)
        alica(p.X(0.15), p.Y(0.02), 1.8, mood="think", right="chin", look=(1, 1))
        caption(p, "Kdo to mohl být?", w=140)
        tb_x, tb_y, tb_w, tb_h = p.X(0.35), p.Y(0.95), p.w*0.6, p.h*0.72
        thought(tb_x, tb_y, tb_w, tb_h, p.X(0.25), p.Y(0.66))
        cat(tb_x+tb_w*0.17, tb_y-tb_h*0.86, 1.45, mood="sleepy")
        magpie(tb_x+tb_w*0.52, tb_y-tb_h*0.7, 1.3, item=spoon)
        tonda(tb_x+tb_w*0.82, tb_y-tb_h*0.93, 1.05, mood="happy")
        for fx in (0.17, 0.5, 0.82):
            hand_text(tb_x+tb_w*fx-10, tb_y-tb_h*0.25, 20, "?", "SHB", 24)
    with Panel(*R[1]) as p:
        garden(p, p.Y(0.12), 11, hills_=False, clouds=False)
        shape([(p.X(0.45), p.Y(0.3)), (p.X(0.98), p.Y(0.3)), (p.X(0.98), p.Y(0.36)), (p.X(0.45), p.Y(0.36))], 0.6, BG)
        for bx in (0.5, 0.92): shape([(p.X(bx), p.Y(0.1)), (p.X(bx)+6, p.Y(0.1)), (p.X(bx)+6, p.Y(0.3)), (p.X(bx), p.Y(0.3))], 0.5, BG)
        cat(p.X(0.72), p.Y(0.36), 1.55, mood="sleepy")
        alica(p.X(0.2), p.Y(0.03), 1.6, mood="happy", look=(1, 0))
        bubble(p.X(0.03), p.Y(0.97), 140, "Micko, nebyla jsi to náhodou ty?", p.X(0.2), p.Y(0.72))
        bubble(p.X(0.6), p.Y(0.8), 76, "Mňau…", p.X(0.72), p.Y(0.62))
    with Panel(*R[2]) as p:
        bg_fill(p, 0.9)
        cx, cy = p.X(0.3), p.Y(0.42)
        fill(ell(cx, cy, 20, 17, 30), 0.3)
        for k_ in range(4):
            a = math.radians(40 + k_*33); dot(cx+math.cos(a)*30, cy+math.sin(a)*27, 7.5, 0.3)
        footprints(p.X(0.72), p.Y(0.4), 1, 0, 0, 1.6)
        hand_text(p.X(0.1), p.Y(0.12), p.w*0.4, "tlapka Micky", "SH", 15)
        hand_text(p.X(0.52), p.Y(0.12), p.w*0.4, "stopa zloděje", "SH", 15)
        caption(p, "Stopa č. 1: Kočka má moc velké tlapky.", w=p.w-14, size=12)
    with Panel(*R[3]) as p:
        garden(p, p.Y(0.15), 13)
        tufts(p, p.Y(0.02), p.Y(0.13), 4, 10)
        fence(p.X(0.45), p.x+p.w+4, p.Y(0.15), 60)
        magpie(p.X(0.78), p.Y(0.15)+66, 1.8, flip=True, item=spoon)
        alica(p.X(0.12), p.Y(0.03), 1.6, mood="think", right="point", look=(1, 0.5))
        hanka(p.X(0.3), p.Y(0.03), 1.6, mood="happy", look=(1, 0.5))
        bubble(p.X(0.01), p.Y(0.97), 150, "Straky mají rády lesklé věci.", p.X(0.12), p.Y(0.75))
        bubble(p.X(0.3), p.Y(0.97), 150, "Ale ponožka se přece neleskne!", p.X(0.31), p.Y(0.66))
        bubble(p.X(0.83), p.Y(0.92), 70, "Krrr?", p.X(0.78), p.Y(0.72))
    page_end()

from props_extra import *

# =================================================================== NEW: Joey red herring
def page_joey():
    R = rows([(255, [1]), (245, [0.5, 0.5]), (260, [1])])
    with Panel(*R[0]) as p:
        garden(p, p.Y(0.2), 31, clouds=False)
        # house wall on the right
        shape([(p.X(0.62), p.Y(0.2)), (p.x+p.w+5, p.Y(0.2)), (p.x+p.w+5, p.y+p.h+5), (p.X(0.62), p.y+p.h+5)], 0.94, BG)
        shape([(p.X(0.62), p.Y(0.2)), (p.x+p.w+5, p.Y(0.2)), (p.x+p.w+5, p.Y(0.28)), (p.X(0.62), p.Y(0.28))], 0.72, BG)
        shape([(p.X(0.72), p.Y(0.5)), (p.X(0.9), p.Y(0.5)), (p.X(0.9), p.Y(0.85)), (p.X(0.72), p.Y(0.85))], 0.45, BG)
        dog_bed(p.X(0.72), p.Y(0.06), 1.6)
        joey(p.X(0.9), p.Y(0.04), 1.0, flip=True, mood="calm")
        hanka(p.X(0.52), p.Y(0.03), 1.75, mood="wow", right="hold", look=(-1, 0),
              item=lambda x, y: old_sock(x+1, y+1, 0.65, rot=160))
        alica(p.X(0.22), p.Y(0.03), 1.8, mood="surprised", look=(1, 0))
        bubble(p.X(0.28), p.Y(0.97), 210, "Alico! Joey má v pelíšku ponožku!", p.X(0.5), p.Y(0.78))
    with Panel(*R[1]) as p:
        bg_fill(p, 1.0); rays(p, p.X(0.6), p.Y(0.4), 0.9)
        joey(p.X(0.55), p.Y(0.06), 1.9, mood="calm")
        hanka(p.X(0.15), p.Y(0.03), 1.6, mood="determined", right="point", look=(1, 0))
        bubble(p.X(0.02), p.Y(0.97), 120, "Joey je zloděj!", p.X(0.13), p.Y(0.78))
        sfx(p.X(0.62), p.Y(0.72), "KŇUK…", 18, -6)
    with Panel(*R[2]) as p:
        bg_fill(p, 0.9)
        old_sock(p.X(0.45), p.Y(0.75), 4.2, rot=15)
        magnifier(p.X(0.62), p.Y(0.52), ang=20, r=28)
        caption(p, "Alica si ponožku pořádně prohlédne.", w=p.w-14, size=12)
        bubble(p.X(0.05), p.Y(0.3), p.w*0.9, "Tahle ponožka je stará a celá rozkousaná.", p.X(0.4), p.Y(0.42))
    with Panel(*R[3]) as p:
        garden(p, p.Y(0.2), 33, tree_x=0.08, tree_s=1.1, clouds=False)
        babicka(p.X(0.3), p.Y(0.03), 1.5, mood="laugh", right="front", look=(1, 0))
        alica(p.X(0.52), p.Y(0.03), 1.65, mood="happy", right="up", look=(-1, 0))
        hanka(p.X(0.74), p.Y(0.03), 1.6, mood="grin", right="hug", look=(1, -0.5))
        joey(p.X(0.88), p.Y(0.03), 0.95, flip=True, mood="happy")
        bubble(p.X(0.02), p.Y(0.97), 175, "To je přece Joeyho stará ponožka na hraní!", p.X(0.28), p.Y(0.75))
        bubble(p.X(0.38), p.Y(0.97), 165, "A stopy byly malinkaté. Joey je nevinný!", p.X(0.5), p.Y(0.8))
        bubble(p.X(0.72), p.Y(0.97), 140, "Promiň, Joey!", p.X(0.74), p.Y(0.66))
    page_end()

# =================================================================== NEW: Tonda + the plan
def page_tonda():
    R = rows([(250, [1]), (255, [0.5, 0.5]), (255, [1])])
    with Panel(*R[0]) as p:
        garden(p, p.Y(0.22), 15, house_x=0.87, house_s=0.85)
        tufts(p, p.Y(0.02), p.Y(0.2), 4, 11)
        tonda(p.X(0.65), p.Y(0.02), 1.6, flip=True, mood="grin", right="wave")
        fence(p.X(0.42), p.X(0.96), p.Y(0.02), 78)
        ball(p.X(0.9), p.Y(0.07), 11)
        alica(p.X(0.12), p.Y(0.02), 1.65, mood="happy", right="hip", look=(1, 0))
        hanka(p.X(0.28), p.Y(0.02), 1.6, mood="happy", look=(1, 0))
        caption(p, "Přes plot kouká soused Tonda.", w=190)
        bubble(p.X(0.47), p.Y(0.97), 220, "Ahoj, holky! Já žádné ponožky nevzal, čestné slovo!", p.X(0.6), p.Y(0.78))
    with Panel(*R[1]) as p:
        garden(p, p.Y(0.1), 17, hills_=False, clouds=False)
        tonda(p.X(0.5), p.Y(0.02), 1.6, mood="surprised", right="up", look=(1, 0))
        fence(p.x-4, p.x+p.w+4, p.Y(0.02), 58)
        bubble(p.X(0.03), p.Y(0.97), p.w*0.92, "Ale ráno jsem viděl něco malého a chlupatého. Mělo to huňatý ocásek!", p.X(0.48), p.Y(0.82))
    with Panel(*R[2]) as p:
        bg_fill(p, 1.0); rays(p, p.X(0.45), p.Y(0.45), 0.9)
        alica(p.X(0.45), p.Y(0.02), 1.8, mood="determined", right="up", look=(1, 0))
        hanka(p.X(0.78), p.Y(0.02), 1.6, mood="wow", flip=True)
        bubble(p.X(0.03), p.Y(0.97), p.w*0.62, "Mám plán! Dnes večer nastražíme past.", p.X(0.42), p.Y(0.8))
    with Panel(*R[3]) as p:
        # kitchen: tiled wall, table
        bg_fill(p, 0.92)
        for yy in range(int(p.Y(0.35)), int(p.y+p.h), 16): stroke([(p.x, yy), (p.x+p.w, yy)], BG*0.4, g=0.7)
        for xx in range(int(p.x), int(p.x+p.w), 16): stroke([(xx, p.Y(0.35)), (xx, p.y+p.h)], BG*0.4, g=0.7)
        shape([(p.x, p.y), (p.x+p.w, p.y), (p.x+p.w, p.Y(0.35)), (p.x, p.Y(0.35))], 0.7, BG)
        for k_ in range(1, 6): stroke([(p.x+p.w*k_/6, p.y), (p.x+p.w*k_/6, p.Y(0.35))], BG*0.6)
        shape([(p.X(0.03), p.Y(0.35)), (p.X(0.97), p.Y(0.35)), (p.X(0.97), p.Y(0.38)), (p.X(0.03), p.Y(0.38))], 0.5, BG)
        mug(p.X(0.12), p.Y(0.38), 1.3, steam=False)
        babicka(p.X(0.55), p.Y(0.03), 1.45, flip=True, mood="surprised", right="front", look=(1, -0.3),
                item=lambda x, y: flour_bag(x-6, y-14, 1.2))
        alica(p.X(0.28), p.Y(0.03), 1.6, mood="grin", right="up", look=(1, 0))
        hanka(p.X(0.85), p.Y(0.03), 1.5, mood="whisper", right="hush", flip=True, monkey=True)
        bubble(p.X(0.36), p.Y(0.97), 160, "Mouka? A na co vám bude?", p.X(0.52), p.Y(0.8))
        bubble(p.X(0.02), p.Y(0.97), 150, "To je detektivní tajemství!", p.X(0.26), p.Y(0.78))
        bubble(p.X(0.72), p.Y(0.72), 70, "Pssst!", p.X(0.83), p.Y(0.6))
    page_end()

# =================================================================== NEW: evening stakeout
def page_stakeout():
    R = rows([(255, [1]), (250, [1]), (255, [0.5, 0.5])])
    with Panel(*R[0]) as p:
        dusk_sky(p, 0.8)
        moon(p.X(0.88), p.Y(0.8), 16)
        hills(p, p.Y(0.28), 18, 0.68, 5)
        ground(p, p.Y(0.24), 0.72)
        clothesline(p.X(0.3), p.X(0.8), p.Y(0.22), 112, ("empty", "sock", "empty"))
        flour_patch(p.X(0.55), p.Y(0.1), 150, 34)
        alica(p.X(0.36), p.Y(0.03), 1.6, mood="determined", right="front", look=(1, -1),
              item=lambda x, y: flour_bag(x-4, y-12, 1.0))
        hanka(p.X(0.17), p.Y(0.03), 1.55, mood="happy", look=(1, -0.5))
        joey(p.X(0.86), p.Y(0.03), 0.9, flip=True, mood="calm")
        caption(p, "Večer holky pověsí na šňůru novou ponožku. A pod ni nasypou mouku.", w=270)
    with Panel(*R[1]) as p:
        # inside: wall with window
        bg_fill(p, 0.88)
        for xx in range(int(p.x)+10, int(p.x+p.w), 24):
            for yy in range(int(p.y)+10, int(p.y+p.h), 24): dot(xx + ((yy//24) % 2)*12, yy, 1.2, 0.78)
        wx0, wy0, wx1, wy1 = p.X(0.3), p.Y(0.28), p.X(0.72), p.Y(0.92)
        fill([(wx0, wy0), (wx1, wy0), (wx1, wy1), (wx0, wy1)], 0.55)
        C.saveState(); C.clipPath(poly([(wx0, wy0), (wx1, wy0), (wx1, wy1), (wx0, wy1)]), stroke=0, fill=0)
        for (sx_, sy_) in ((0.1, 0.8), (0.5, 0.9), (0.8, 0.7), (0.3, 0.6)): star(wx0+(wx1-wx0)*sx_, wy0+(wy1-wy0)*sy_, 3, 0.95)
        moon(wx0+(wx1-wx0)*0.75, wy0+(wy1-wy0)*0.75, 12)
        C.restoreState()
        form([(wx0-6, wy0-6), (wx1+6, wy0-6), (wx1+6, wy1+6), (wx0-6, wy1+6)], 0.95, w=BG, sh=0)
        fill([(wx0, wy0), (wx1, wy0), (wx1, wy1), (wx0, wy1)], 0.55)
        C.saveState(); C.clipPath(poly([(wx0, wy0), (wx1, wy0), (wx1, wy1), (wx0, wy1)]), stroke=0, fill=0)
        for (sx_, sy_) in ((0.1, 0.8), (0.5, 0.9), (0.8, 0.7), (0.3, 0.6)): star(wx0+(wx1-wx0)*sx_, wy0+(wy1-wy0)*sy_, 3, 0.95)
        moon(wx0+(wx1-wx0)*0.75, wy0+(wy1-wy0)*0.75, 12)
        C.restoreState()
        stroke([(wx0, wy0), (wx1, wy0), (wx1, wy1), (wx0, wy1)], BG*1.2, closed=True)
        stroke([((wx0+wx1)/2, wy0), ((wx0+wx1)/2, wy1)], BG*2.5, g=0.95); stroke([(wx0, (wy0+wy1)/2), (wx1, (wy0+wy1)/2)], BG*2.5, g=0.95)
        stroke([((wx0+wx1)/2, wy0), ((wx0+wx1)/2, wy1)], BG*0.6); stroke([(wx0, (wy0+wy1)/2), (wx1, (wy0+wy1)/2)], BG*0.6)
        # sill
        form([(wx0-14, wy0-12), (wx1+14, wy0-12), (wx1+14, wy0-4), (wx0-14, wy0-4)], 0.65, w=BG, sh=0)
        mug(wx0+8, wy0-4, 1.2); mug(wx1-14, wy0-4, 1.2)
        alica(p.X(0.4), p.Y(-0.35), 2.4, mood="happy", look=(1, 1), shadow=False,
              item=None, right="front")
        hanka(p.X(0.6), p.Y(-0.18), 2.4, mood="grin", shadow=False)
        deda(p.X(0.87), p.Y(-0.45), 2.2, flip=True, mood="happy", right="hold", shadow=False,
             item=lambda x, y: binoculars(x+1, y+3, 0.6, rot=-10))
        caption(p, "Pak čekají u okna. Děda jim půjčil dalekohled.", w=240)
        bubble(p.X(0.72), p.Y(0.97), 140, "Detektivové musí být trpěliví.", p.X(0.86), p.Y(0.72))
    with Panel(*R[2]) as p:
        bg_fill(p, 0.8)
        shape([(p.x, p.y), (p.x+p.w, p.y), (p.x+p.w, p.Y(0.3)), (p.x, p.Y(0.3))], 0.6, BG)
        hanka(p.X(0.5), p.Y(-0.62), 4.0, mood="sleepy", shadow=False)
        shape([(p.x, p.y), (p.x+p.w, p.y), (p.x+p.w, p.Y(0.18)), (p.x, p.Y(0.18))], 0.62, BG)
        for i, (dx, dy, sz) in enumerate(((0.72, 0.72, 13), (0.78, 0.79, 16), (0.85, 0.87, 20))):
            hand_text(p.X(dx), p.Y(dy), 20, "Z" if i == 2 else "z", "SHB", sz, align="left")
        caption(p, "Hanka usnula i s opičkou.", w=p.w-14, size=12)
    with Panel(*R[3]) as p:
        night_sky(p, 0.5)
        moon(p.X(0.8), p.Y(0.8), 16)
        for (sx_, sy_) in ((0.15, 0.85), (0.4, 0.92), (0.6, 0.75)): star(p.X(sx_), p.Y(sy_), 3, 0.95)
        ground(p, p.Y(0.2), 0.4)
        clothesline(p.X(0.1), p.X(0.9), p.Y(0.2), 110, ("empty", "sock", "empty"))
        silhouette_dormouse(p.X(0.47), p.Y(0.2)+88, 1.3)
        bubble(p.X(0.05), p.Y(0.5), 150, "Tam! Něco tam je…", p.X(0.3), p.Y(0.7), whisper=True)
    page_end()

# =================================================================== NEW: floury footprints in the morning
def page_flour():
    R = rows([(260, [1]), (240, [0.5, 0.5]), (260, [1])])
    with Panel(*R[0]) as p:
        garden(p, p.Y(0.3), 35)
        clothesline(p.X(0.25), p.X(0.75), p.Y(0.28), 110, ("empty", "empty", "empty"))
        flour_patch(p.X(0.5), p.Y(0.14), 170, 40)
        footprints(p.X(0.43), p.Y(0.1), 5, 12, 5, 0.75)
        tail_swish(p.X(0.42), p.Y(0.2), 26)
        alica(p.X(0.12), p.Y(0.03), 1.7, mood="wow", look=(1, -0.5))
        hanka(p.X(0.88), p.Y(0.03), 1.6, mood="surprised", flip=True, look=(1, -0.5))
        caption(p, "Ráno je ponožka pryč! Ale v mouce zůstaly stopy.", w=240)
    with Panel(*R[1]) as p:
        bg_fill(p, 0.97)
        footprints(p.X(0.2), p.Y(0.35), 3, 36, 18, 2.0, g=0.45)
        stroke(bez((p.X(0.12), p.Y(0.2)), (p.X(0.35), p.Y(0.3)), (p.X(0.55), p.Y(0.12)), (p.X(0.85), p.Y(0.22))), 5, g=0.55)
        alica(p.X(0.8), p.Y(-0.9), 3.6, mood="determined", right="lens", lens=True, look=(-1, -1), shadow=False)
        bubble(p.X(0.03), p.Y(0.97), 170, "Malé tlapky… a tohle je otisk ocásku!", p.X(0.25), p.Y(0.55))
    with Panel(*R[2]) as p:
        garden(p, p.Y(0.2), 37, hills_=False, clouds=False)
        flour_patch(p.X(0.55), p.Y(0.1), 120, 30)
        joey(p.X(0.55), p.Y(0.05), 1.3, pose="sniff", flip=True)
        fill(ell(p.X(0.55)-41, p.Y(0.05)+30, 9, 6, 20), 0.99)
        hanka(p.X(0.2), p.Y(0.03), 1.5, mood="grin", look=(1, -0.3))
        sfx(p.X(0.55), p.Y(0.55), "HAPČÍ!", 22, 8)
        bubble(p.X(0.02), p.Y(0.97), 130, "Joey má bílý čumák!", p.X(0.18), p.Y(0.72))
    with Panel(*R[3]) as p:
        garden(p, p.Y(0.36), 39, tree_x=0.8, tree_s=1.0)
        tufts(p, p.Y(0.02), p.Y(0.33), 6, 13)
        footprints(p.X(0.32), p.Y(0.1), 5, 14, 5, 0.7, g=0.75)
        red_thread([(p.X(0.55), p.Y(0.14)), (p.X(0.7), p.Y(0.2)), (p.X(0.85), p.Y(0.28)), (p.X(1.02), p.Y(0.33))])
        hanka(p.X(0.08), p.Y(0.03), 1.6, mood="wow", look=(1, -0.3), legs="walk")
        alica(p.X(0.25), p.Y(0.03), 1.7, mood="surprised", right="point", look=(1, -0.3), legs="walk")
        joey(p.X(0.5), p.Y(0.03), 0.95, pose="sniff")
        caption(p, "Stopy vedou přes zahradu. A dál je vidět červená nitka!", w=260)
        bubble(p.X(0.42), p.Y(0.82), 150, "Stopa! Nitka z ponožky!", p.X(0.27), p.Y(0.7))
    page_end()

# =================================================================== NEW: the trail adventure
def page_trail():
    R = rows([(245, [1]), (250, [0.5, 0.5]), (265, [1])])
    with Panel(*R[0]) as p:
        garden(p, p.Y(0.46), 41, clouds=True)
        # vegetable patch
        shape([(p.x-5, p.Y(0.04)), (p.x+p.w+5, p.Y(0.04)), (p.x+p.w+5, p.Y(0.42)), (p.x-5, p.Y(0.42))], 0.62, BG)
        for k_ in range(1, 4): stroke([(p.x, p.Y(0.04)+k_*p.h*0.095), (p.x+p.w, p.Y(0.04)+k_*p.h*0.095)], BG*0.6, g=0.35)
        for (px_, py_, s_) in ((0.08, 0.3, 1.1), (0.22, 0.14, 1.4), (0.62, 0.3, 1.0), (0.78, 0.12, 1.5), (0.92, 0.3, 1.0), (0.45, 0.33, 0.9)):
            pumpkin(p.X(px_), p.Y(py_), s_)
        red_thread([(p.X(0.02), p.Y(0.08)), (p.X(0.3), p.Y(0.2)), (p.X(0.55), p.Y(0.1)), (p.X(0.7), p.Y(0.24)), (p.X(1.0), p.Y(0.3))])
        alica(p.X(0.38), p.Y(0.06), 1.6, mood="determined", legs="walk", right="lens", lens=True, look=(1, -0.5))
        hanka(p.X(0.52), p.Y(0.06), 1.5, mood="happy", legs="walk", look=(1, -0.3))
        caption(p, "Nitka vede přes záhonek s dýněmi…", w=240)
    with Panel(*R[1]) as p:
        garden(p, p.Y(0.1), 43, hills_=False, clouds=False)
        # fence with a gap
        fence(p.x-4, p.X(0.42), p.Y(0.1), 90)
        fence(p.X(0.58), p.x+p.w+4, p.Y(0.1), 90)
        stroke([(p.X(0.42), p.Y(0.1)+27), (p.X(0.58), p.Y(0.1)+27)], BG*4); stroke([(p.X(0.42), p.Y(0.1)+27), (p.X(0.58), p.Y(0.1)+27)], BG*2.4, g=0.75)
        stroke([(p.X(0.42), p.Y(0.1)+65), (p.X(0.58), p.Y(0.1)+65)], BG*4); stroke([(p.X(0.42), p.Y(0.1)+65), (p.X(0.58), p.Y(0.1)+65)], BG*2.4, g=0.75)
        alica(p.X(0.2), p.Y(0.02), 1.7, mood="worried", look=(1, 0))
        hanka(p.X(0.73), p.Y(0.02), 1.55, mood="grin", flip=True, right="wave", look=(1, 0))
        bubble(p.X(0.02), p.Y(0.97), 120, "Tudy se neprotáhnu…", p.X(0.18), p.Y(0.78))
        bubble(p.X(0.58), p.Y(0.97), 90, "Já jo!", p.X(0.72), p.Y(0.75))
    with Panel(*R[2]) as p:
        garden(p, p.Y(0.1), 45, hills_=False, clouds=False)
        raspberry_bush(p.X(0.62), p.Y(0.1), 2.2)
        red_thread([(p.X(0.02), p.Y(0.15)), (p.X(0.3), p.Y(0.2)), (p.X(0.5), p.Y(0.35)), (p.X(0.58), p.Y(0.42))])
        hanka(p.X(0.28), p.Y(0.02), 1.7, mood="wow", right="point", look=(1, 0.3))
        bubble(p.X(0.02), p.Y(0.97), 140, "Alico! Tady se nitka zachytila!", p.X(0.25), p.Y(0.78))
    with Panel(*R[3]) as p:
        garden(p, p.Y(0.5), 47, clouds=False)
        shed(p.X(0.86), p.Y(0.48), 0.75, door_open=True)
        stream(p, p.Y(0.06), p.Y(0.3))
        for (sx_, sy_, rx_) in ((0.12, 0.2, 16), (0.3, 0.14, 15), (0.48, 0.2, 16), (0.66, 0.14, 15), (0.84, 0.19, 15)):
            stone(p.X(sx_), p.Y(sy_), rx_+4, 7, 0.82)
        alica(p.X(0.48), p.Y(0.19), 1.45, mood="happy", right="back", left="down", look=(-1, 0), flip=True)
        hanka(p.X(0.31), p.Y(0.14), 1.35, mood="wow", right="up", look=(1, 0), monkey=True)
        joey(p.X(0.72), p.Y(0.08), 1.0, mood="happy")
        sfx(p.X(0.72), p.Y(0.42), "ŠPLÍCH!", 20, -6)
        caption(p, "…přes potůček až ke staré kůlně na konci zahrady.", w=280)
    page_end()

# =================================================================== PAGE 6
def page6():
    R = rows([(265, [1]), (240, [0.5, 0.5]), (255, [1])])
    with Panel(*R[0]) as p:
        garden(p, p.Y(0.22), 4, clouds=True)
        tree(p.X(0.12), p.Y(0.2), 1.25, seed=14)
        shed(p.X(0.62), p.Y(0.2), 2.2, door_open=True)
        red_thread([(p.X(0.02), p.Y(0.05)), (p.X(0.3), p.Y(0.1)), (p.X(0.5), p.Y(0.16)), (p.X(0.6), p.Y(0.21))])
        tufts(p, p.Y(0.02), p.Y(0.2), 5, 9)
        alica(p.X(0.24), p.Y(0.03), 1.75, mood="worried", look=(1, 0.3))
        hanka(p.X(0.36), p.Y(0.03), 1.65, mood="worried", look=(1, 0.3))
        joey(p.X(0.88), p.Y(0.03), 0.95, flip=True, pose="sniff")
        caption(p, "Stará kůlna. Dveře jsou pootevřené.", w=230)
    with Panel(*R[1]) as p:
        planks(p, 0.72, 22, 3)
        shape([(p.X(0.64), p.y), (p.x+p.w+2, p.y), (p.x+p.w+2, p.Y(0.86)), (p.X(0.64), p.Y(0.86))], 0.12, BG*1.2)
        fill([(p.x, p.y), (p.x+p.w, p.y), (p.x+p.w, p.Y(0.06)), (p.x, p.Y(0.06))], 0.55)
        alica(p.X(0.4), p.Y(0.04), 1.9, mood="whisper", right="hush", look=(-1, -0.3))
        hanka(p.X(0.14), p.Y(0.04), 1.9, mood="whisper", look=(1, 0.3))
        joey(p.X(0.8), p.Y(0.04), 0.9, flip=True, mood="calm")
        bubble(p.X(0.36), p.Y(0.97), 150, "Psst, Joey. Musíme být úplně potichu.", p.X(0.44), p.Y(0.8), whisper=True)
    with Panel(*R[2]) as p:
        planks(p, 0.5, 22, 9)
        floor(p, p.Y(0.14), 0.42)
        rake(p.X(0.1), p.Y(0.24), 1.1)
        saw(p.X(0.52), p.Y(0.8), 1.0)
        crate(p.X(0.74), p.Y(0.06), 52, 40)
        watering_can(p.X(0.64), p.Y(0.07), 1.1)
        # torch beam from Hanka
        sunbeam(p.X(0.34), p.X(0.36), p.Y(0.5), p.X(0.95), p.X(0.95), p.Y(0.9), 0.0)
        fill([(p.X(0.33), p.Y(0.49)), (p.X(0.98), p.Y(0.95)), (p.X(0.98), p.Y(0.55))], 1.0, 0.35)
        hanka(p.X(0.25), p.Y(0.05), 1.85, mood="wow", right="lens", torch=True, look=(1, 0.6))
        alica(p.X(0.1), p.Y(0.05), 1.85, mood="wow", look=(1, 0.6))
        joey(p.X(0.8), p.Y(0.05), 0.82, pose="sniff", flip=True)
        caption(p, "V kůlně je šero. Hanka si posvítí baterkou.", w=p.w-14, size=12)
        sfx(p.X(0.62), p.Y(0.3), "ČMUCH", 15, -8)
    with Panel(*R[3]) as p:
        planks(p, 0.7, 26, 12)
        floor(p, p.Y(0.12), 0.52)
        sunbeam(p.X(0.05), p.X(0.2), p.y+p.h, p.X(0.42), p.X(0.8), p.y, 0.3)
        shelf(p.X(0.55), p.X(0.99), p.Y(0.56))
        boot(p.X(0.72), p.Y(0.58), 1.55)
        crate(p.X(0.6), p.Y(0.05), 62, 46); crate(p.X(0.82), p.Y(0.05), 46, 62, 0.7)
        red_thread([(p.X(0.02), p.Y(0.1)), (p.X(0.35), p.Y(0.12)), (p.X(0.5), p.Y(0.3)), (p.X(0.58), p.Y(0.5)),
                    (p.X(0.66), p.Y(0.62)), (p.X(0.7), p.Y(0.72))])
        hanka(p.X(0.14), p.Y(0.04), 1.9, mood="surprised", right="point", look=(1, 1))
        alica(p.X(0.34), p.Y(0.04), 1.9, mood="surprised", right="point", look=(1, 1))
        bubble(p.X(0.03), p.Y(0.97), 110, "Tam! V botě!", p.X(0.14), p.Y(0.6))
        bubble(p.X(0.3), p.Y(0.97), 170, "Nitka vede až do té staré boty!", p.X(0.36), p.Y(0.76))
    page_end()

# =================================================================== PAGE 7
def page7():
    R = rows([(220, [0.5, 0.5]), (330, [1]), (210, [1])])
    with Panel(*R[0]) as p:
        planks(p, 0.72, 30, 4)
        shelf(p.x-10, p.x+p.w+10, p.Y(0.1))
        boot(p.X(0.45), p.Y(0.13), 3.3)
        C.saveState(); C.clipPath(poly([(p.x, p.Y(0.13)+153), (p.x+p.w, p.Y(0.13)+153), (p.x+p.w, p.y+p.h), (p.x, p.y+p.h)]), stroke=0, fill=0)
        dormouse(p.X(0.4), p.Y(0.13)+118, 3.0, tail=False)
        C.restoreState()
        sfx(p.X(0.78), p.Y(0.72), "?!", 30, 10)
    with Panel(*R[1]) as p:
        bg_fill(p, 1.0); rays(p, p.X(0.5), p.Y(0.5), 0.88)
        alica(p.X(0.33), p.Y(0.02), 1.75, mood="wow", left="up", right="up")
        hanka(p.X(0.7), p.Y(0.02), 1.75, mood="surprised")
        sfx(p.X(0.08), p.Y(0.75), "ACH!", 30, 12)
    with Panel(*R[2]) as p:
        planks(p, 0.74, 34, 6)
        sunbeam(p.X(0.9), p.X(0.99), p.y+p.h, p.X(0.35), p.X(0.75), p.y, 0.3)
        shelf(p.x-10, p.x+p.w+10, p.Y(0.07))
        sc = 4.3; bx = p.X(0.45); by = p.Y(0.07)
        boot(bx, by, sc)
        rx0 = bx - 2*sc; ry0 = by + 46*sc
        C.saveState(); C.clipPath(poly([(p.x, by+45*sc), (p.x+p.w, by+45*sc), (p.x+p.w, p.y+p.h), (p.x, p.y+p.h)]), stroke=0, fill=0)
        dormouse(rx0-50, ry0-10, 1.6, mood="happy")
        dormouse(rx0+48, ry0-10, 1.6, mood="sleepy", flip=True)
        dormouse(rx0-4, ry0-24, 3.0, mood="happy")
        dormouse(rx0+24, ry0-8, 1.3, mood="happy", tail=False)
        C.restoreState()
        shape([(bx-13.5*sc, by+43*sc), (bx+9.5*sc, by+43*sc), (bx+9.5*sc, by+47*sc), (bx-13.5*sc, by+47*sc)], 0.3, BG*1.2)
        sock_item(bx-13.5*sc+12, ry0+6, 2.6, g=0.4, rot=-8)
        glove(bx+9.5*sc-8, ry0+10, 2.1, 0.55, rot=190)
        wool(bx+9.5*sc+18, ry0-4, 15, 0.7)
        crate(p.X(0.04), p.Y(0.07), 70, 50); crate(p.X(0.83), p.Y(0.07), 60, 70, 0.7)
    with Panel(*R[3]) as p:
        bg_fill(p, 0.93)
        caption(p, "Ve staré botě bydlí rodinka plchů! A pelíšek mají z ponožek, rukavice a vlny.", w=p.w*0.55)
        alica(p.X(0.72), p.Y(0.02), 1.55, mood="grin", right="hush", look=(-1, -0.5), flip=True)
        hanka(p.X(0.88), p.Y(0.02), 1.5, mood="grin", flip=True, look=(-1, -0.5))
        bubble(p.X(0.05), p.Y(0.55), p.w*0.5, "Tak to vy jste ti zloději ponožek!", p.X(0.68), p.Y(0.66), whisper=True)
        dormouse(p.X(0.1), p.Y(0.06), 1.3, mood="happy")
        bubble(p.X(0.15), p.Y(0.3), 60, "Píp?", p.X(0.12), p.Y(0.2))
    page_end()

# =================================================================== PAGE 8
def page8():
    R = rows([(255, [1]), (245, [0.5, 0.5]), (260, [1])])
    with Panel(*R[0]) as p:
        bg_fill(p, 0.95)
        caption(p, "Plch je malé zvířátko s huňatým ocáskem. Na zimu si staví teplý pelíšek a spí v něm až do jara.", w=255)
        wool(p.X(0.25), p.Y(0.2), 45, 0.75)
        shape(ell(p.X(0.25), p.Y(0.22), 55, 22, 40), 0.85, BG)
        dormouse(p.X(0.25), p.Y(0.18), 2.4, mood="sleepy")
        for i, (dx, dy, sz) in enumerate(((0.33, 0.45, 14), (0.36, 0.5, 17), (0.4, 0.56, 21))):
            hand_text(p.X(dx), p.Y(dy), 20, "Z" if i == 2 else "z", "SHB", sz, align="left")
        alica(p.X(0.72), p.Y(0.02), 1.7, mood="happy", right="chin", look=(-1, -0.3), flip=True)
        bubble(p.X(0.53), p.Y(0.97), 235, "Oni vůbec nejsou zloději. Jen se chystají na zimu!", p.X(0.7), p.Y(0.76))
    with Panel(*R[1]) as p:
        garden(p, p.Y(0.15), 23, clouds=False)
        shed(p.X(0.2), p.Y(0.15), 1.0)
        alica(p.X(0.52), p.Y(0.02), 1.55, mood="grin", right="wave", look=(1, 0))
        hanka(p.X(0.72), p.Y(0.02), 1.5, mood="grin", right="up", look=(1, 0))
        joey(p.X(0.88), p.Y(0.02), 0.72, mood="bark")
        bubble(p.X(0.3), p.Y(0.97), p.w*0.66, "Babi! Dědo! Záhada je vyřešená!", p.X(0.55), p.Y(0.76))
    with Panel(*R[2]) as p:
        planks(p, 0.74, 30, 7)
        babicka(p.X(0.3), p.Y(0.02), 1.55, mood="laugh", right="up", look=(1, 0.5))
        deda(p.X(0.72), p.Y(0.02), 1.45, flip=True, mood="happy", look=(1, 0.5))
        bubble(p.X(0.03), p.Y(0.97), p.w*0.9, "No tohle! Tak ať si ty ponožky klidně nechají.", p.X(0.3), p.Y(0.78))
    with Panel(*R[3]) as p:
        planks(p, 0.74, 30, 8)
        shelf(p.X(0.03), p.X(0.5), p.Y(0.35))
        boot(p.X(0.2), p.Y(0.375), 1.5)
        babicka(p.X(0.42), p.Y(0.02), 1.5, flip=True, mood="happy", right="front", look=(1, 0.5),
                item=lambda x, y: wool(x-5, y+5, 9, 0.7))
        deda(p.X(0.68), p.Y(0.02), 1.4, flip=True, mood="grin", right="hip")
        alica(p.X(0.86), p.Y(0.02), 1.35, flip=True, mood="happy", look=(1, 0.3))
        hanka(p.X(0.96), p.Y(0.02), 1.3, flip=True, mood="happy", look=(1, 0.3))
        bubble(p.X(0.03), p.Y(0.97), 180, "Tady mají ještě trochu vlny, ať jim není zima.", p.X(0.38), p.Y(0.75))
        bubble(p.X(0.5), p.Y(0.97), 190, "A já jim postavím pořádný domeček!", p.X(0.66), p.Y(0.84))
    page_end()

# =================================================================== PAGE 9
def page9():
    R = rows([(270, [1]), (240, [0.5, 0.5]), (250, [1])])
    with Panel(*R[0]) as p:
        planks(p, 0.86, 40, 2)
        hanka(p.X(0.36), p.Y(0.02), 1.55, mood="happy", look=(1, -0.5))
        for bx in (0.28, 0.7): shape([(p.X(bx), p.Y(0.02)), (p.X(bx)+8, p.Y(0.02)), (p.X(bx)+8, p.Y(0.35)), (p.X(bx), p.Y(0.35))], 0.55, BG)
        form([(p.X(0.25), p.Y(0.35)), (p.X(0.75), p.Y(0.35)), (p.X(0.75), p.Y(0.42)), (p.X(0.25), p.Y(0.42))], 0.55, w=BG, sdx=0, sdy=3)
        birdhouse(p.X(0.52), p.Y(0.42), 1.5)
        saw(p.X(0.58), p.Y(0.82), 1.0)
        deda(p.X(0.86), p.Y(0.02), 1.5, flip=True, mood="happy", right="front", look=(1, -0.5), item=hammer)
        alica(p.X(0.12), p.Y(0.02), 1.6, mood="grin", right="front", look=(1, -0.5), item=hammer)
        caption(p, "Odpoledne staví holky s dědou domeček pro plchy.", w=230)
        sfx(p.X(0.24), p.Y(0.58), "ŤUK!", 20, 10); sfx(p.X(0.6), p.Y(0.62), "ŤUK!", 16, -10)
        bubble(p.X(0.65), p.Y(0.97), 170, "Opatrně na prstíky, detektivko!", p.X(0.83), p.Y(0.8))
    with Panel(*R[1]) as p:
        planks(p, 0.74, 30, 5)
        shelf(p.x-10, p.x+p.w+10, p.Y(0.2))
        birdhouse(p.X(0.45), p.Y(0.23), 2.3)
        dormouse(p.X(0.47), p.Y(0.23)+100, 1.3, mood="happy")
        dormouse(p.X(0.22), p.Y(0.23), 1.0, mood="happy")
        caption(p, "Plchům se nový domeček moc líbí.", w=p.w-14, size=12)
    with Panel(*R[2]) as p:
        bg_fill(p, 0.9)
        notebook_big(p.X(0.08), p.Y(0.1), p.w*0.84, p.h*0.7, "PŘÍPAD Č. 1:", ["Zmizelé ponožky", "", "VYŘEŠENO!"], check=True)
    with Panel(*R[3]) as p:
        planks(p, 0.74, 30, 9)
        shelf(p.X(0.4), p.X(1.02), p.Y(0.45))
        boot(p.X(0.7), p.Y(0.475), 1.6)
        for (sx_, sy_, r_) in ((0.6, 0.86, 6), (0.8, 0.9, 4), (0.66, 0.95, 3)): star(p.X(sx_), p.Y(sy_), r_, 0.95)
        hanka(p.X(0.1), p.Y(0.02), 1.6, mood="surprised", look=(1, 1))
        alica(p.X(0.28), p.Y(0.02), 1.7, mood="surprised", right="lens", lens=True, look=(1, 1))
        bubble(p.X(0.02), p.Y(0.97), 200, "Počkat… Co se to tam na dně blýská?", p.X(0.27), p.Y(0.78))
    page_end()

# =================================================================== PAGE 10
def page10():
    R = rows([(250, [0.5, 0.5]), (510, [1])])
    with Panel(*R[0]) as p:
        bg_fill(p, 0.9)
        key(p.X(0.42), p.Y(0.38), 3.6, rot=-10)
        for (sx_, sy_, r_) in ((0.85, 0.5, 7), (0.8, 0.28, 4), (0.12, 0.3, 5)): star(p.X(sx_), p.Y(sy_), r_, 0.95)
        caption(p, "Na dně boty leží starý klíč. A na visačce je hvězdička.", w=p.w-14, size=12)
    with Panel(*R[1]) as p:
        garden(p, p.Y(0.1), 25, hills_=False, clouds=False)
        tufts(p, p.Y(0.02), p.Y(0.09), 3, 15)
        alica(p.X(0.36), p.Y(0.02), 1.75, mood="wow", right="up", look=(1, 1),
              item=lambda x, y: key(x+4, y+8, 1.0, rot=70, tag=False))
        hanka(p.X(0.13), p.Y(0.02), 1.65, mood="wow", look=(1, 1))
        joey(p.X(0.8), p.Y(0.02), 0.85, flip=True, mood="happy")
        bubble(p.X(0.42), p.Y(0.97), 130, "Starý klíč! Ale od čeho asi je?", p.X(0.4), p.Y(0.78))
        bubble(p.X(0.72), p.Y(0.6), 60, "Haf?", p.X(0.8), p.Y(0.36))
    with Panel(*R[2], bg=0.7) as p:
        for (sx_, sy_) in ((0.1, 0.9), (0.3, 0.8), (0.55, 0.92), (0.65, 0.78), (0.9, 0.88), (0.2, 0.7), (0.45, 0.75)):
            star(p.X(sx_), p.Y(sy_), 4, 0.98)
        moon(p.X(0.85), p.Y(0.75), 26)
        fill([(p.x-5, p.y-5), (p.x-5, p.Y(0.18)), (p.x+p.w+5, p.Y(0.18)), (p.x+p.w+5, p.y-5)], 0.5)
        stroke([(p.x-5, p.Y(0.18)), (p.x+p.w+5, p.Y(0.18))], BG)
        tree(p.X(0.1), p.Y(0.18), 1.8, seed=20, g=0.55)
        house(p.X(0.55), p.Y(0.18), 2.4, smoke=True)
        # lit windows
        for wx in (-35, 17):
            gl = [(p.X(0.55)+wx*2.4, p.Y(0.18)+20*2.4), (p.X(0.55)+(wx+18)*2.4, p.Y(0.18)+20*2.4),
                  (p.X(0.55)+(wx+18)*2.4, p.Y(0.18)+42*2.4), (p.X(0.55)+wx*2.4, p.Y(0.18)+42*2.4)]
            fill(gl, 0.97, 0.85)
            stroke([((gl[0][0]+gl[1][0])/2, gl[0][1]), ((gl[0][0]+gl[1][0])/2, gl[2][1])], 1.2)
            stroke([(gl[0][0], (gl[0][1]+gl[2][1])/2), (gl[1][0], (gl[0][1]+gl[2][1])/2)], 1.2)
        cx, cy = p.X(0.55), p.Y(0.18)+70*2.4
        shape(ell(cx, cy, 20, 20, 36), 1.0, 1.6)
        star(cx, cy, 11, 0.35)
        alica(p.X(0.17), p.Y(0.03), 1.6, mood="think", right="chin", look=(1, 1))
        hanka(p.X(0.3), p.Y(0.03), 1.5, mood="surprised", right="point", look=(1, 1))
        joey(p.X(0.05), p.Y(0.03), 0.9, mood="sleepy")
        caption(p, "Ten večer se holky dlouho dívají na okýnko na půdě. Není na něm taky hvězdička?", w=300)
        box = [(p.X(0.53), p.Y(0.03)), (p.X(0.97), p.Y(0.03)+2), (p.X(0.97)-1, p.Y(0.03)+44), (p.X(0.53)+1, p.Y(0.03)+43)]
        fill(box, 1.0)
        for a_, b_ in ((0, 1), (1, 2), (2, 3), (3, 0)): stroke([box[a_], box[b_]], 1.5)
        hand_text(p.X(0.53), p.Y(0.03)+16, p.w*0.44, "Pokračování příště…", "SHB", 18)
    page_end()

# =================================================================== PAGE 11 – activity
def page11():
    with Panel(M, 40, W-2*M, H-80) as p:
        box = [(p.X(0.05), p.Y(0.885)), (p.X(0.95), p.Y(0.89)), (p.X(0.95), p.Y(0.885)+64), (p.X(0.05), p.Y(0.885)+62)]
        fill(box, 0.92)
        for a_, b_ in ((0, 1), (1, 2), (2, 3), (3, 0)): stroke([box[a_], box[b_]], 1.5)
        hand_text(p.X(0.05), p.Y(0.885)+24, p.w*0.9, "Detektivní zápisník", "SHB", 26)
        magnifier(p.X(0.1), p.Y(0.87), ang=-30, r=12)
        y = p.Y(0.82)
        qs = [("1. Co nasypaly holky pod šňůru?", ["cukr", "mouku", "písek"]),
              ("2. Kdo se protáhl dírou v plotě?", ["Alica", "Hanka", "Tonda"]),
              ("3. Kdo si z věcí postavil pelíšek?", ["kočka", "straka", "plši"]),
              ("4. Co našla Alica na dně boty?", ["klíč", "minci", "prsten"])]
        for q, opts in qs:
            hand_text(p.X(0.06), y, p.w*0.9, q, "SH", 16, align="left")
            for i, o in enumerate(opts):
                hand_text(p.X(0.12) + i*150, y-28, 140, o, "SHB", 16, align="left")
            y -= 70
        hand_text(p.X(0.06), y, p.w*0.6, "5. Proč Joey není zloděj?", "SH", 16, align="left")
        stroke([(p.X(0.58), y-3), (p.X(0.9), y-3)], 0.8, g=0.4)
        y -= 50
        hand_text(p.X(0.06), y, p.w*0.9, "Nakresli, co myslíš, že ten klíč odemyká:", "SHB", 16, align="left")
        shape(rrect(p.X(0.06), p.Y(0.05), p.w*0.88, y - p.Y(0.05) - 16, 10), 1.0, 1.6)
        key(p.X(0.82), p.Y(0.1), 1.3, rot=-20, tag=True)
    page_end()

# =================================================================== PAGE 12 – next time
def page12():
    with Panel(M, 40, W-2*M, H-80, bg=0.95) as p:
        hand_text(p.X(0.1), p.Y(0.93), p.w*0.8, "Příště v sešitě č. 2:", "SHB", 20)
        title(p.X(0.5), p.Y(0.84), "TAJEMSTVÍ STARÉHO KLÍČE", 34)
        with Panel(p.X(0.08), p.Y(0.38), p.w*0.84, p.h*0.4, bg=0.8) as q:
            shape([(q.x-5, q.Y(0.72)), (q.X(0.5), q.y+q.h+40), (q.x+q.w+5, q.Y(0.72))], 0.62, BG)
            for k_ in range(1, 6): stroke([(q.X(k_/6), q.y), (q.X(k_/6), q.Y(0.72) + (1-abs(k_/6-0.5)*2)*80)], BG)
            floor(q, q.Y(0.15), 0.55)
            sunbeam(q.X(0.45), q.X(0.55), q.y+q.h, q.X(0.3), q.X(0.62), q.y, 0.35)
            with T(q.X(0.58), q.Y(0.12), 1.0):
                form([(-70, 0), (70, 0), (70, 55), (-70, 55)], 0.45, w=1.4, sdx=6, sdy=0)
                shape(ell(0, 55, 70, 30, 40, 0, 180) + [(-70, 55)], 0.4, 1.4)
                for k_ in (-45, 45): shape([(k_-6, 0), (k_+6, 0), (k_+6, 80), (k_-6, 80)], 0.25, 1.0)
                shape(rrect(-12, 36, 24, 26, 4), 0.75, 1.1)
                star(0, 50, 7, 0.2)
            hanka(q.X(0.1), q.Y(0.05), 1.5, mood="surprised", look=(1, -0.3))
            alica(q.X(0.25), q.Y(0.05), 1.55, mood="wow", right="lens", lens=True, look=(1, -0.3))
            hand_text(q.X(0.78), q.Y(0.7), 40, "?", "SHB", 34, align="left")
            hand_text(q.X(0.84), q.Y(0.78), 30, "?", "SHB", 22, align="left")
        hand_text(p.X(0.1), p.Y(0.32), p.w*0.8,
                  "Na půdě stojí stará truhla se hvězdičkou na zámku. Co je uvnitř? A proč o ní děda nikdy nemluvil?", "SH", 16, lead=21)
        hand_text(p.X(0.3), p.Y(0.2), p.w*0.4, "Detektivní tým:", "SHB", 16)
        alica(p.X(0.08), p.Y(0.03), 0.95, mood="happy", right="wave")
        hanka(p.X(0.19), p.Y(0.03), 0.95, mood="grin")
        joey(p.X(0.33), p.Y(0.03), 0.75, mood="happy")
        tonda(p.X(0.52), p.Y(0.03), 0.9, mood="grin")
        babicka(p.X(0.66), p.Y(0.03), 0.88, mood="happy")
        deda(p.X(0.81), p.Y(0.03), 0.82, mood="happy", flip=True)
        dormouse(p.X(0.94), p.Y(0.03), 0.9, flip=True)
    page_end()

cover(); page2(); page3(); page4(); page_joey(); page_tonda(); page_stakeout(); page_flour(); page_trail(); page6(); page7(); page8(); page9(); page10(); page11(); page12()
cv.save(); print("ok")
