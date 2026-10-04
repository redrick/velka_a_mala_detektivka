"""Render a sample of characters, a room and a comic panel in the current style (VMD_STYLE decides which).

Usage:  python preview_style.py <out_dir>                       (personal style, the default)
        VMD_STYLE=puvodni python preview_style.py <out_dir>     (the old look)
Writes <out_dir>/<style>_*.png. Draws exactly like export_assets.render (same seeds, 2x), so with the style off
the characters must match the PNGs in game/assets byte for byte.
"""
import os, sys, zlib
import pymupdf
from reportlab.pdfgen import canvas
import lib
import osobni

STYLE = "osobni" if osobni.ACTIVE else "puvodni"
OUT = sys.argv[1] if len(sys.argv) > 1 else os.path.join(os.path.dirname(os.path.abspath(__file__)), "out", "styl")


class Box:
    def __init__(self, w, h): self.x, self.y, self.w, self.h = 0, 0, w, h
    def X(self, f): return self.w*f
    def Y(self, f): return self.h*f


def render(name, w, h, draw, mode="color", scale=2.0):
    import style3
    lib.MODE = mode
    path = os.path.join(OUT, f"{STYLE}_{name}.png")
    tmp = path + ".pdf"
    cv = canvas.Canvas(tmp, pagesize=(w, h)); lib.set_canvas(cv)
    style3._R.seed(zlib.crc32(name.encode()))
    draw(Box(w, h)); cv.showPage(); cv.save()
    doc = pymupdf.open(tmp)
    doc[0].get_pixmap(matrix=pymupdf.Matrix(scale, scale), alpha=(mode == "color")).save(path)
    doc.close(); os.remove(tmp)
    return path


def main():
    os.makedirs(OUT, exist_ok=True)
    from style3 import alica, hanka, joey
    from chars3 import babicka, deda, tonda
    from interior import room_kitchen
    import letter
    S = 2.2
    chars = [
        ("alica_happy", 120, 240, lambda b: alica(b.w/2, 8, S, mood="happy", shadow=False)),
        ("alica_grin", 120, 240, lambda b: alica(b.w/2, 8, S, mood="grin", shadow=False)),
        ("alica_surprised", 120, 240, lambda b: alica(b.w/2, 8, S, mood="surprised", shadow=False)),
        ("hanka_happy", 110, 200, lambda b: hanka(b.w/2, 8, S, mood="happy", shadow=False)),
        ("hanka_worried", 110, 200, lambda b: hanka(b.w/2, 8, S, mood="worried", shadow=False)),
        ("joey_stand", 180, 140, lambda b: joey(b.w/2-5, 8, S, mood="happy", shadow=False)),
        ("babicka", 130, 270, lambda b: babicka(b.w/2, 8, S, mood="happy", shadow=False)),
        ("deda", 140, 300, lambda b: deda(b.w/2, 8, S, mood="happy", shadow=False)),
        ("tonda", 130, 250, lambda b: tonda(b.w/2, 8, S, mood="grin", shadow=False)),
    ]
    for name, w, h, fn in chars: print(render(name, w, h, fn))
    from story2 import room_bedroom
    for name, fn in (("room_kuchyne", room_kitchen), ("room_pokojicek", room_bedroom)):
        room = render(name, 960, 540, fn, scale=1.0)
        osobni.paper(room); print(room)

    def panel(b):
        import style3
        style3.hatch([(20, 20), (380, 20), (380, 70), (20, 70)], ang=60, g=0.0, alpha=0.5)
        alica(150, 40, 1.6, mood="surprised", right="point")
        hanka(250, 40, 1.6, mood="wow")
        letter.bubble(40, 300, 230, "Čmuch čmuch! Joey něco našel u kůlny!", 150, 225, size=15)
        letter.hand_text(20, 380, 360, "MEZITÍM NA ZAHRADĚ…", font="SHB", size=13, align="left")
    print(render("komiks", 400, 400, panel, mode="bw"))

    def balloons(b):
        with letter.Panel(10, 10, 580, 380):
            letter.bubble(30, 370, 240, "Psst… Hanko, slyšíš to?", 120, 200, size=14, whisper=True)
            letter.thought(330, 370, 220, 70, 450, 220, seed=3)
            letter.hand_text(345, 342, 190, "Kde jsou ty ponožky?", size=13)
            letter.shout(60, 180, 260, "ČMUCH ČMUCH! HAF!", size=16)
            letter.bubble(340, 170, 220, "Joey něco našel!", 470, 30, size=14)
    print(render("bubliny", 600, 400, balloons, mode="bw"))


if __name__ == "__main__":
    main()
