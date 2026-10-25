#!/usr/bin/env python3
"""The README's story pictures: one game scene and the comic cover per story, into docs/img/stories/.

The scenes come from the story tests' snapshots (headless, no window):
  run each tests/story_<n>.gd headless with  -- --test=res://tests/story_<n>.gd --snaps=<dir>/<n>
  then  art/.venv/bin/python tools/readme_shots.py <dir>
"""
import os, sys
import pymupdf
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import json
from snap_render import render

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "docs", "img", "stories")
COMICS = os.path.join(ROOT, "comics", "velka_a_mala_detektivka")
SCENE = {1: "003_Zahrada_Trava", 2: "021_Puda_Prkno1", 3: "005_Rybnik_Parez", 4: "007_Ves4_Hodiny",
         5: "014_Zahrada5_Snehulak", 6: "018_Mlyn6_enter", 7: "012_Les7_Hajny", 8: "009_Louka8_ZajiciStopy",
         9: "020_Masopust9_enter", 10: "004_Skola10_Seno", 11: "008_Dvur11_Slepice", 12: "031_Zahrada12_Hanka",
         13: "027_Hraz13_enter", 14: "006_Nadvori14_Lavicka"}

os.makedirs(OUT, exist_ok=True)
for n, name in SCENE.items():
    img = render(json.load(open(os.path.join(sys.argv[1], str(n), name + ".json"), encoding="utf-8")))
    img.resize((960, 540)).save(os.path.join(OUT, f"{n:02d}_game.jpg"), quality=80)
    pdf = next(f for f in sorted(os.listdir(COMICS)) if f.startswith(f"{n:02d}_") and "BROZURA" not in f)
    doc = pymupdf.open(os.path.join(COMICS, pdf))
    page = doc[0]
    page.get_pixmap(matrix=pymupdf.Matrix(300/page.rect.width, 300/page.rect.width)).save(
        os.path.join(OUT, f"{n:02d}_comic.jpg"), jpg_quality=80)
    print(n, name, pdf)
