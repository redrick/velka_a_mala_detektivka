"""Solver for the snowman minigame (game/game/minigames/snowman.gd), used by check_levels.py.
Push a ball: onto snow it grows (max 3) and the snow is gone; onto a bigger single ball or a 2-stack whose top is
bigger it stacks; stacks can't move. Win: a stack 3-2-1."""
import sys
from collections import deque

D = {"→": (1, 0), "←": (-1, 0), "↓": (0, 1), "↑": (0, -1)}


def parse(rows):
    walls, snow, balls, me = set(), set(), {}, None
    for y, row in enumerate(rows):
        for x, c in enumerate(row):
            p = (x, y)
            if c == "#": walls.add(p)
            elif c == "*": snow.add(p)
            elif c == "P": me = p
            elif c in "123": balls[p] = (int(c),)
    return walls, frozenset(snow), me, frozenset(balls.items())


def step(walls, state, d):
    me, snow, balls = state
    bd = dict(balls)
    t = (me[0] + d[0], me[1] + d[1])
    if t in walls: return None
    if t in bd:
        st = bd[t]
        if len(st) > 1: return None
        n = (t[0] + d[0], t[1] + d[1])
        if n in walls: return None
        s = st[0]
        if n in bd:
            st2 = bd[n]
            if len(st2) >= 3 or st2[-1] <= s: return None
            del bd[t]; bd[n] = st2 + (s,)
        else:
            del bd[t]
            if n in snow:
                s = min(3, s + 1); snow = snow - {n}
            bd[n] = (s,)
    return (t, snow, frozenset(bd.items()))


def won(state):
    return any(st == (3, 2, 1) for _, st in state[2])


def solve(rows, limit=400000):
    walls, snow, me, balls = parse(rows)
    W = max(len(r) for r in rows); H = len(rows)
    walls = walls | {(x, -1) for x in range(W)} | {(x, H) for x in range(W)} | {(-1, y) for y in range(H)} | {(W, y) for y in range(H)}
    start = (me, snow, balls)
    seen = {start: None}
    q = deque([start])
    while q and len(seen) < limit:
        s = q.popleft()
        if won(s):
            path = []
            while seen[s]:
                s, k = seen[s]; path.append(k)
            return path[::-1]
        for k, d in D.items():
            n = step(walls, s, d)
            if n is not None and n not in seen:
                seen[n] = (s, k); q.append(n)
    return None


if __name__ == "__main__":
    import ast
    for rows in ast.literal_eval(sys.stdin.read()):
        sol = solve(rows)
        print(len(sol) if sol else "NONE", "".join(sol or []))
