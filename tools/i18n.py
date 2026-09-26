#!/usr/bin/env python3
"""Czech/English texts for the game.

  python3 tools/i18n.py            # scan the game, update game/game/i18n/strings.csv, list missing English

The CSV has columns keys,cs,en. The key is the Czech text exactly as written in the game, so cs == key.
Collected: say("...") lines, tr("...") texts, `description = "..."` in scenes, and titles in series.json.
Fill in the `en` column for new rows; Godot imports the CSV as two translations.
"""
import csv, glob, json, os, re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
GAME = os.path.join(ROOT, "game", "game")
CSV = os.path.join(GAME, "i18n", "strings.csv")

STR = re.compile(r'"((?:[^"\\]|\\.)*)"')
SAY = re.compile(r'\bsay\((.*)\)\s*$')
TR = re.compile(r'\btr\("((?:[^"\\]|\\.)*)"\)')
DESC = re.compile(r'^description = "((?:[^"\\]|\\.)*)"$', re.M)
# strings handed to say() through a constant
EXTRA = ["Velký!", "Malý!"]


def unescape(s):
    return s.encode().decode("unicode_escape").encode("latin-1").decode("utf-8")


def collect():
    keys = {}
    def add(text, where):
        text = unescape(text)
        if text.strip() and not text.isascii() or re.search(r"[a-zA-Z]{2}", text):
            keys.setdefault(text, where)
    for path in glob.glob(os.path.join(GAME, "**", "*.gd"), recursive=True):
        rel = os.path.relpath(path, GAME)
        for n, line in enumerate(open(path, encoding="utf-8"), 1):
            if line.lstrip().startswith("#") or "func say" in line:
                continue
            m = SAY.search(line.split("#", 1)[0].strip())
            if m:
                for t in STR.findall(m.group(1)):
                    add(t, f"{rel}:{n}")
            for t in TR.findall(line):
                add(t, f"{rel}:{n}")
    for path in glob.glob(os.path.join(GAME, "**", "*.tscn"), recursive=True):
        if os.sep + "gui" + os.sep in path:
            continue
        rel = os.path.relpath(path, GAME)
        for t in DESC.findall(open(path, encoding="utf-8").read()):
            add(t, rel)
    catalog = json.load(open(os.path.join(GAME, "menu", "series.json"), encoding="utf-8"))
    for s in catalog["series"]:
        add(s["title"], "series.json"); add(s.get("subtitle", ""), "series.json")
        for e in s["episodes"]:
            add(e["title"], "series.json")
    for t in EXTRA:
        add(t, "extra")
    return keys


def main():
    old = {}
    if os.path.exists(CSV):
        for row in csv.DictReader(open(CSV, encoding="utf-8")):
            old[row["keys"]] = row["en"]
    keys = collect()
    os.makedirs(os.path.dirname(CSV), exist_ok=True)
    with open(CSV, "w", encoding="utf-8", newline="") as f:
        w = csv.writer(f)
        w.writerow(["keys", "cs", "en"])
        for k in sorted(keys):
            w.writerow([k, k, old.get(k, "")])
    missing = [k for k in keys if not old.get(k)]
    print(f"{len(keys)} texts -> {os.path.relpath(CSV, ROOT)}, {len(missing)} without English")
    for k in missing:
        print("  missing en:", k)


if __name__ == "__main__":
    main()
