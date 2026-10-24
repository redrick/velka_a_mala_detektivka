#!/usr/bin/env python3
"""Fills the English column of game/game/i18n/strings.csv from a file of "czech => english" lines
(a tab works as the separator too).

  python3 tools/i18n_add.py translations.tsv

Only keys already in the CSV are filled (run tools/i18n.py first); keys it doesn't know are listed.
"""
import csv, os, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CSV = os.path.join(ROOT, "game", "game", "i18n", "strings.csv")

pairs = {}
for line in open(sys.argv[1], encoding="utf-8"):
    line = line.rstrip("\n")
    sep = " => " if " => " in line else "\t" if "\t" in line else None
    if sep:
        cs, en = line.split(sep, 1)
        pairs[cs] = en
rows = list(csv.DictReader(open(CSV, encoding="utf-8")))
known = {r["keys"] for r in rows}
for r in rows:
    if r["keys"] in pairs:
        r["en"] = pairs[r["keys"]]
with open(CSV, "w", encoding="utf-8", newline="") as f:
    w = csv.writer(f)
    w.writerow(["keys", "cs", "en"])
    for r in rows:
        w.writerow([r["keys"], r["cs"], r["en"]])
for k in pairs:
    if k not in known:
        print("not in the CSV:", k)
print(f"filled {sum(1 for k in pairs if k in known)} texts")
