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


ok = True
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
