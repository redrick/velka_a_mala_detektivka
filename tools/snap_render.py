#!/usr/bin/env python3
"""Draws the scene snapshots that game/tests/story_test.gd writes with --snaps=<dir> (one JSON per step: every
sprite with its texture, place, size, colour and drawing order, plus the night tint) as 1920 x 1080 pictures.
Headless Godot can't render, so this is how the README gets pictures from the game without opening a window.

  art/.venv/bin/python tools/snap_render.py <snap.json> <out.png|.jpg> [width]
"""
import json, math, os, sys
from PIL import Image

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
_cache = {}


def texture(res):
    if res not in _cache:
        _cache[res] = Image.open(os.path.join(ROOT, "game", res[len("res://"):])).convert("RGBA")
    return _cache[res]


def render(snap):
    canvas = Image.new("RGBA", (1920, 1080), (255, 255, 255, 255))
    items = sorted(enumerate(snap["items"]), key=lambda e: (e[1]["z"], e[1]["key"], e[0]))
    for _, it in items:
        im = texture(it["tex"])
        if it["flip"]:
            im = im.transpose(Image.Transpose.FLIP_LEFT_RIGHT)
        sx, sy = it["sx"], it["sy"]
        w, h = max(1, round(im.width*abs(sx))), max(1, round(im.height*abs(sy)))
        im = im.resize((w, h))
        r, g, b, a = it["mod"]
        if (r, g, b, a) != (1, 1, 1, 1):
            px = im.split()
            im = Image.merge("RGBA", [c.point(lambda v, k=k: v*k) for c, k in zip(px, (r, g, b, a))])
        if abs(it["rot"]) > 1e-3:
            im = im.rotate(-math.degrees(it["rot"]), expand=True)
        cx = it["x"] + it["ox"]*sx
        cy = it["y"] + it["oy"]*sy
        if not it["centered"]:
            cx, cy = cx + w/2, cy + h/2
        canvas.paste(im, (round(cx - im.width/2), round(cy - im.height/2)), im)
    tint = snap.get("tint", [1, 1, 1])
    if tint != [1, 1, 1]:
        px = canvas.split()
        canvas = Image.merge("RGBA", [c.point(lambda v, k=k: v*k) for c, k in zip(px[:3], tint)] + [px[3]])
    return canvas.convert("RGB")


if __name__ == "__main__":
    img = render(json.load(open(sys.argv[1], encoding="utf-8")))
    if len(sys.argv) > 3:
        w = int(sys.argv[3])
        img = img.resize((w, round(w*1080/1920)), Image.Resampling.LANCZOS)
    img.save(sys.argv[2], quality=82)
