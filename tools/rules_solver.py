"""Counts the answers of the picture-rule puzzles (game/game/minigames/rules.gd): every way to put the items
into the slots that keeps all rules. Used by check_levels.py; the levels sit in each puzzle's LEVELS constant,
written so that it reads as JSON once trailing commas are dropped."""
import itertools, json, re


def load_levels(path):
    src = open(path, encoding="utf-8").read()
    block = src[src.index("const LEVELS := ") + len("const LEVELS := "):]
    block = block[:re.search(r"^\]", block, re.M).end()]
    return json.loads(re.sub(r",(\s*[\]}])", r"\1", block))


def holds(rule, at, slot_of):
    kind, a = rule[0], at[rule[1]]
    n = len(slot_of)
    if kind == "is": return a == slot_of[rule[2]]
    if kind == "not": return a != slot_of[rule[2]]
    if kind == "end": return a in (0, n - 1)
    b = at[rule[2]]
    if kind == "next": return abs(a - b) == 1
    if kind == "apart": return abs(a - b) != 1
    if kind == "before": return a < b
    raise ValueError(kind)


def answers(level):
    items = [it[0] for it in level["items"]]
    slot_of = {s[0]: k for k, s in enumerate(level["slots"])}
    out = []
    for perm in itertools.permutations(range(len(level["slots"])), len(items)):
        at = dict(zip(items, perm))
        if all(holds(r, at, slot_of) for r in level["rules"]):
            out.append(at)
    return out
