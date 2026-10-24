#!/usr/bin/env python3
"""Solves every minigame level and prints the shortest solution, so a level that can't be
solved (or is too easy) is caught before it reaches the game.

  python3 tools/check_levels.py

The levels are read from the minigame scripts themselves (the LEVELS constant), so this
always checks what the game ships.
"""
import itertools, os, re, sys
from collections import deque

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MG = os.path.join(ROOT, "game", "game", "minigames")


def levels(script):
    src = open(os.path.join(MG, script), encoding="utf-8").read()
    block = src[src.index("const LEVELS"):]
    block = block[:block.index("\n]\n")]
    return [[row for row in re.findall(r'"([^"]*)"', lvl)] for lvl in re.findall(r"\[(.*?)\]", block, re.S)]


def cells(rows):
    return {(x, y): ch for y, row in enumerate(rows) for x, ch in enumerate(row)}


DIRS = {"→": (1, 0), "←": (-1, 0), "↓": (0, 1), "↑": (0, -1)}


def solve_trap(rows):
    g = cells(rows)
    walls = {p for p, c in g.items() if c == "#"}
    goals = {p for p, c in g.items() if c in "T*+"}
    boxes = frozenset(p for p, c in g.items() if c in "B*")
    me = next(p for p, c in g.items() if c in "P+")
    start = (me, boxes)
    seen = {start: None}
    q = deque([start])
    while q:
        st = q.popleft()
        me, boxes = st
        if boxes == goals:
            path = []
            while seen[st]:
                st, d = seen[st]; path.append(d)
            return path[::-1]
        for d, (dx, dy) in DIRS.items():
            n = (me[0] + dx, me[1] + dy)
            if n in walls or n not in g:
                continue
            nb = boxes
            if n in boxes:
                b2 = (n[0] + dx, n[1] + dy)
                if b2 in walls or b2 in boxes or b2 not in g:
                    continue
                nb = (boxes - {n}) | {b2}
            ns = (n, frozenset(nb))
            if ns not in seen:
                seen[ns] = (st, d); q.append(ns)
    return None


def beam(g, flips):
    """trace the sunbeam; flips = {mirror pos: '/' or '\\'}; returns (cells passed, end cell char)"""
    src = next(p for p, c in g.items() if c == "S")
    x, y = src; dx, dy = 1, 0
    passed = []
    for _ in range(200):
        x, y = x + dx, y + dy
        c = g.get((x, y))
        if c is None:
            return passed, None
        passed.append((x, y))
        if c in "#O":
            return passed, c
        if c == "X":
            return passed, "X"
        if (x, y) in flips:
            dx, dy = (-dy, -dx) if flips[(x, y)] == "/" else (dy, dx)
    return passed, None


def solve_beam(rows):
    g = cells(rows)
    ms = sorted(p for p, c in g.items() if c == "M")
    wins = []
    for combo in itertools.product("/\\", repeat=len(ms)):
        flips = dict(zip(ms, combo))
        if beam(g, flips)[1] == "X":
            wins.append("".join(combo))
    return wins, len(ms)


def solve_steps(rows):
    g = cells(rows)
    start = next(p for p, c in g.items() if c == "S")
    goal = next(p for p, c in g.items() if c == "G")
    seen = {start: None}
    q = deque([start])
    while q:
        p = q.popleft()
        if p == goal:
            path = []
            while seen[p]:
                p, d = seen[p]; path.append(d)
            return path[::-1]
        for d, (dx, dy) in DIRS.items():
            n = (p[0] + dx, p[1] + dy)
            if g.get(n, "#") in "#~":
                continue
            if n not in seen:
                seen[n] = (p, d); q.append(n)
    return None


def const_list(script, name):
    src = open(os.path.join(MG, script), encoding="utf-8").read()
    m = re.search(rf"const {name} := \[(.*?)\]", src, re.S)
    return [int(v) for v in re.findall(r"-?\d+", m.group(1))]


def hex_nb(p):
    c, r = p
    if r % 2:
        return [(c - 1, r), (c + 1, r), (c, r - 1), (c + 1, r - 1), (c, r + 1), (c + 1, r + 1)]
    return [(c - 1, r), (c + 1, r), (c - 1, r - 1), (c, r - 1), (c - 1, r + 1), (c, r + 1)]


def gears_ok(pegs, filled):
    key = next(p for p, c in pegs.items() if c == "K")
    dirs, q, jam = {key: 1}, deque([key]), False
    while q:
        p = q.popleft()
        for n in hex_nb(p):
            if n not in filled:
                continue
            if n not in dirs:
                dirs[n] = -dirs[p]; q.append(n)
            elif dirs[n] == dirs[p]:
                jam = True
    return not jam and all(dirs.get(p) == 1 for p, c in pegs.items() if c == "H")


def solve_gears(rows, spare):
    pegs = {(x, y): ch for y, row in enumerate(rows) for x, ch in enumerate(row) if ch != " "}
    free = sorted(p for p, c in pegs.items() if c == ".")
    base = {p for p, c in pegs.items() if c != "."}
    for n in range(0, spare + 1):
        sols = [s for s in itertools.combinations(free, n) if gears_ok(pegs, base | set(s))]
        if sols:
            return n, len(sols)
    return None, 0


def solve_snowman(rows, limit=400000):
    import sys as _s
    _s.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    from snowman_solver import solve
    return solve(rows, limit)


def latin(rows):
    """(number of solutions up to 2, solvable step by step with only forced places)"""
    n = len(rows); kinds = "SHMZ"[:n]
    g = {(x, y): (rows[y][x] if rows[y][x] != "." else "") for y in range(n) for x in range(n)}
    can = lambda g, c, k: all(not (o != c and g[o] == k and (o[0] == c[0] or o[1] == c[1])) for o in g)
    count = [0]
    def rec(g, cells):
        if count[0] > 1: return
        if not cells: count[0] += 1; return
        c = cells[0]
        for k in kinds:
            if can(g, c, k):
                g[c] = k; rec(g, cells[1:]); g[c] = ""
    rec(dict(g), [c for c in g if not g[c]])
    while True:
        moved = False
        for c in g:
            if not g[c]:
                cs = [k for k in kinds if can(g, c, k)]
                if len(cs) == 1: g[c] = cs[0]; moved = True
        for line in range(n):
            for k in kinds:
                for vert in (0, 1):
                    cells_ = [(line, j) if vert else (j, line) for j in range(n)]
                    if any(g[c] == k for c in cells_): continue
                    sp = [c for c in cells_ if not g[c] and can(g, c, k)]
                    if len(sp) == 1: g[sp[0]] = k; moved = True
        if not moved: break
    return count[0], all(g.values())


def deer_path(rows):
    g = cells(rows)
    S = next(p for p, c in g.items() if c == "S"); G = next(p for p, c in g.items() if c == "G")
    nb = lambda p: [(p[0] + dx, p[1] + dy) for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1))]
    path, cur, seen = [S], S, {S}
    while True:
        nxt = [n for n in nb(cur) if g.get(n) == "d" and n not in seen]
        if G in nb(cur) and cur != S and not nxt:
            break
        if len(nxt) != 1:
            return None
        cur = nxt[0]; seen.add(cur); path.append(cur)
    return path if sum(1 for c in g.values() if c == "d") == len(path) - 1 else None


def hutch_levels():
    src = open(os.path.join(MG, "hutch.gd"), encoding="utf-8").read()
    shapes = {n: [tuple(map(int, c)) for c in re.findall(r"Vector2i\((-?\d+), (-?\d+)\)", body)]
              for n, body in re.findall(r'"(\w+)": \[(.*?)\],', src[src.index("const SHAPES"):src.index("const LEVELS")])}
    block = src[src.index("const LEVELS"):src.index("const COLORS")]
    lv = [(int(w), int(h), re.findall(r'"(\w+)"', names)) for w, h, names in re.findall(r"\[(\d+), (\d+), \[(.*?)\]\]", block)]
    return shapes, lv


def tilings(W, H, cells_list):
    def orients(cells):
        out, c = set(), cells
        for _ in range(4):
            c = [(-y, x) for x, y in c]
            for cc in (c, [(-x, y) for x, y in c]):
                mx = min(x for x, y in cc); my = min(y for x, y in cc)
                out.add(tuple(sorted(((x - mx, y - my) for x, y in cc), key=lambda q: (q[1], q[0]))))
        return list(out)
    pieces = [orients(c) for c in cells_list]
    count = [0]
    def rec(filled, used):
        if count[0] > 0: return
        free = [(x, y) for y in range(H) for x in range(W) if (x, y) not in filled]
        if not free: count[0] += 1; return
        fx, fy = free[0]
        for i in range(len(pieces)):
            if i in used: continue
            for o in pieces[i]:
                ox, oy = o[0]
                cells = [(fx + x - ox, fy + y - oy) for x, y in o]
                if all(0 <= x < W and 0 <= y < H and (x, y) not in filled for x, y in cells):
                    rec(filled | set(cells), used | {i})
    if sum(len(c) for c in cells_list) == W*H:
        rec(frozenset(), frozenset())
    return count[0]


def arrow_trails(rows):
    """Count the ways to turn the arrows so the trail goes door -> every star -> gate."""
    g = {(x, y): ch for y, r in enumerate(rows) for x, ch in enumerate(r)}
    start = next(c for c, ch in g.items() if ch == "D")
    stars = {c for c, ch in g.items() if ch == "s"}
    count = 0

    def rec(p, seen):
        nonlocal count
        if p not in g:
            return
        if g[p] == "G":
            count += stars <= seen
            return
        if g[p] not in "as" or p in seen:
            return
        for d in ((1, 0), (0, 1), (-1, 0), (0, -1)):
            rec((p[0] + d[0], p[1] + d[1]), seen | {p})
    rec((start[0] + 1, start[1]), frozenset())
    return count


def radio_calls(rows):
    """Fewest radio calls to get Hanka to the Bota rock (she walks on until something stops her)."""
    g = {(x, y): ch for y, r in enumerate(rows) for x, ch in enumerate(r)}
    start = next(c for c, ch in g.items() if ch == "H")
    goal = next(c for c, ch in g.items() if ch == "B")

    def run(c, d):
        while c != goal:
            n = (c[0] + d[0], c[1] + d[1])
            if n not in g or g[n] in "o*~":
                break
            c = n
        return c
    dist, queue = {start: 0}, [start]
    while queue:
        c = queue.pop(0)
        if c == goal:
            return dist[c]
        for d in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            n = run(c, d)
            if n not in dist:
                dist[n] = dist[c] + 1
                queue.append(n)
    return None


def pens_answers(rows):
    """Ways to fence the meadow: each rectangle holds one guinea pig and as many squares as its number."""
    W, H = len(rows[0]), len(rows)
    pigs = {(x, y): int(ch) for y, r in enumerate(rows) for x, ch in enumerate(r) if ch != "."}
    if sum(pigs.values()) != W*H:
        return 0
    opts = {}
    for c, n in pigs.items():
        opts[c] = []
        for w in (w for w in range(1, n + 1) if n % w == 0):
            h = n // w
            for x in range(c[0] - w + 1, c[0] + 1):
                for y in range(c[1] - h + 1, c[1] + 1):
                    cells = frozenset((i, j) for i in range(x, x + w) for j in range(y, y + h))
                    if x >= 0 and y >= 0 and x + w <= W and y + h <= H and len(cells & pigs.keys()) == 1:
                        opts[c].append(cells)
    order = sorted(pigs, key=lambda c: len(opts[c]))

    def rec(k, used):
        if k == len(order):
            return 1
        return sum(rec(k + 1, used | o) for o in opts[order[k]] if not o & used)
    return rec(0, frozenset())


def pattern_ok(rows):
    """Every egg row repeats a pattern shorter than the row, and the empty places' answers fit it."""
    for row in rows:
        full = row.upper()
        if not any(all(full[i] == full[i % p] for i in range(len(full))) for p in range(1, len(full) // 2 + 1)):
            return False
    return True


def int_levels(script):
    src = open(os.path.join(MG, script), encoding="utf-8").read()
    block = src[src.index("const LEVELS"):]
    block = block[:block.index("\n]") + 2]
    return [[int(n) for n in re.findall(r"\d+", lv)] for lv in re.findall(r"\[([\d, ]+)\]", block)]


ok = True
from rules_solver import load_levels as rule_levels, answers as rule_answers
for name in ("mittens.gd", "birds.gd", "joey_morning.gd", "parade.gd", "seating.gd"):
    for i, lv in enumerate(rule_levels(os.path.join(MG, name)), 1):
        n = len(rule_answers(lv))
        print(f"{name[:-3]} {i}: {n} řešení{'' if n == 1 else ' (MÁ BÝT 1)'}, {len(lv['rules'])} pravidel")
        ok &= n == 1 and len(lv["rules"]) <= 8
for i, rows in enumerate(levels("radio.gd"), 1):
    n = radio_calls(rows)
    print(f"vysílačka {i}: {'NESPLNITELNÉ' if n is None else f'nejméně {n} hlášení'}")
    ok &= n is not None
for i, w in enumerate(int_levels("scale.gd"), 1):
    can = any(sum(c) * 2 == sum(w) for k in range(1, len(w)) for c in itertools.combinations(w, k))
    print(f"krmelec {i}: {w} {'jde rozdělit' if can else 'NEJDE ROZDĚLIT'}")
    ok &= can
for i, rows in enumerate(levels("pens.gd"), 1):
    n = pens_answers(rows)
    print(f"ohrádky {i}: {n} řešení{'' if n == 1 else ' (MÁ BÝT 1)'}")
    ok &= n == 1
for i, rows in enumerate(levels("pattern.gd"), 1):
    good = pattern_ok(rows)
    print(f"kraslice {i}: {'vzorek sedí' if good else 'VZOREK SE NEOPAKUJE'}")
    ok &= good
for i, rows in enumerate(levels("arrows.gd"), 1):
    n = arrow_trails(rows)
    print(f"šipky {i}: {'NESPLNITELNÉ' if n == 0 else f'{n} cest'}")
    ok &= n > 0
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from bales_solver import solve as solve_bales
for i, rows in enumerate(levels("bales.gd"), 1):
    sol, _ = solve_bales(rows)
    print(f"balíky {i}: {'NESPLNITELNÉ' if sol is None else f'nejméně {len(sol)} posunů'}")
    ok &= sol is not None
shapes, hl = hutch_levels()
for i, (w, h, names) in enumerate(hl, 1):
    n = tilings(w, h, [shapes[k] for k in names])
    print(f"kotec {i}: {w}x{h} z {', '.join(names)}: {'jde' if n else 'NEJDE'}")
    ok &= n > 0
for i, rows in enumerate(levels("trail.gd"), 1):
    pth = deer_path(rows)
    print(f"po stopě {i}: {'CHYBA: srnčí stopy nejsou jedna cesta' if pth is None else f'{len(pth) - 1} srnčích stop'}")
    ok &= pth is not None
for i, rows in enumerate(levels("stars.gd"), 1):
    n, easy = latin(rows)
    print(f"smrček {i}: {n} řešení{'' if n == 1 else ' (MÁ BÝT 1)'}, {'jde krok za krokem' if easy else 'NEJDE BEZ ZKOUŠENÍ'}")
    ok &= n == 1 and easy
for i, rows in enumerate(levels("snowman.gd"), 1):
    sol = solve_snowman(rows)
    print(f"sněhulák {i}: {'NESPLNITELNÉ' if sol is None else f'nejkratší {len(sol)} kroků'}", "".join(sol or []))
    ok &= sol is not None
    want = re.findall(r'"([→←↓↑]+)"', open(os.path.join(MG, "snowman.gd"), encoding="utf-8").read())
    if sol and (i > len(want) or len(want[i - 1]) != len(sol)):
        print(f"  SOLUTIONS[{i - 1}] in snowman.gd should be: {''.join(sol)}"); ok = False
for i, (rows, spare) in enumerate(zip(levels("gears.gd"), const_list("gears.gd", "SPARE")), 1):
    n, count = solve_gears(rows, spare)
    print(f"kolečka {i}: {'NESPLNITELNÉ' if n is None else f'nejméně {n} koleček (máš {spare}), {count} takových řešení'}")
    ok &= n is not None and n > 0
for i, rows in enumerate(levels("trap.gd"), 1):
    sol = solve_trap(rows)
    print(f"past {i}: {'NESPLNITELNÉ' if sol is None else f'{len(sol)} kroků'}", "".join(sol or []))
    ok &= sol is not None
for i, rows in enumerate(levels("sunbeam.gd"), 1):
    wins, n = solve_beam(rows)
    print(f"paprsek {i}: {n} zrcátek, řešení {len(wins)} z {2**n}: {wins}")
    ok &= bool(wins)
for i, rows in enumerate(levels("steps.gd"), 1):
    sol = solve_steps(rows)
    print(f"kroky {i}: {'NESPLNITELNÉ' if sol is None else f'nejkratší {len(sol)} kroků'}", "".join(sol or []))
    ok &= sol is not None
sys.exit(0 if ok else 1)
