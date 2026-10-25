#!/usr/bin/env python3
"""Story 13 "Hráz pro bobra": which cells to block with branches.

Cells: ^ high bank, o stone, . low meadow, ~ creek, S creek comes in, E creek runs away, L lodge entrance,
T tent. Branches go on . and ~ only. Water spreads from S over every low cell it can reach; if it reaches E the
creek runs away and only the creek itself is wet. Solved = E cut off, L under water, every T dry.
"""
import itertools

LOW = set(".~SELT")


def grid(rows):
    return {(x, y): c for y, r in enumerate(rows) for x, c in enumerate(r)}


def water(g, branches):
    start = next(p for p, c in g.items() if c == "S")
    seen, todo = {start}, [start]
    while todo:
        x, y = todo.pop()
        for n in ((x + 1, y), (x - 1, y), (x, y + 1), (x, y - 1)):
            if n in g and n not in seen and g[n] in LOW and n not in branches:
                seen.add(n)
                todo.append(n)
    if any(g[p] == "E" for p in seen):
        return {p for p in seen if g[p] in "~SE"}, False
    return seen, True


def solved(g, branches):
    wet, pond = water(g, branches)
    return pond and all((g[p] == "L") <= (p in wet) for p in g) and not any(g[p] == "T" and p in wet for p in g)


def answers(rows, k):
    g = grid(rows)
    spots = [p for p, c in g.items() if c in ".~"]
    out = []
    for n in range(1, k + 1):
        out += [set(c) for c in itertools.combinations(spots, n) if solved(g, set(c))]
        if out:
            return n, out
    return None, []


if __name__ == "__main__":
    import sys
    sys.path.insert(0, ".")
