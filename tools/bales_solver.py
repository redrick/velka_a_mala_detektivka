"""Solver for the straw-bale minigame (game/game/minigames/bales.gd), used by check_levels.py. Rush-hour style:
Pieces: letters; horizontal if its cells share a row. Level string rows; '.' empty, '#' wall."""
import random, sys
from collections import deque
def parse(rows):
    pcs={}
    for y,r in enumerate(rows):
        for x,c in enumerate(r):
            if c not in '.#': pcs.setdefault(c,[]).append((x,y))
    walls={(x,y) for y,r in enumerate(rows) for x,c in enumerate(r) if c=='#'}
    return pcs, walls
def solve(rows):
    W=len(rows[0]); H=len(rows)
    pcs,walls=parse(rows)
    names=sorted(pcs)
    horiz={n:(len(pcs[n])==1 or pcs[n][0][1]==pcs[n][1][1]) for n in names}
    length={n:len(pcs[n]) for n in names}
    start=tuple(min(pcs[n]) for n in names)
    hi=names.index('H')
    def occ(st):
        o={}
        for i,n in enumerate(names):
            x,y=st[i]
            for k in range(length[n]):
                o[(x+k,y) if horiz[n] else (x,y+k)]=i
        return o
    seen={start:None}; q=deque([start])
    while q:
        st=q.popleft()
        if st[hi][0]+length['H']-1==W-1:
            path=[];s=st
            while seen[s]: s,m=seen[s]; path.append(m)
            return path[::-1], len(seen)
        o=occ(st)
        for i,n in enumerate(names):
            x,y=st[i]
            for d in (-1,1):
                k=1
                while True:
                    nx,ny=(x+d*k,y) if horiz[n] else (x,y+d*k)
                    cells=[(nx+j,ny) if horiz[n] else (nx,ny+j) for j in range(length[n])]
                    if any(not(0<=cx<W and 0<=cy<H) or (cx,cy) in walls or o.get((cx,cy),i)!=i for cx,cy in cells): break
                    ns=list(st); ns[i]=(nx,ny); ns=tuple(ns)
                    if ns not in seen: seen[ns]=(st,(n,d*k)); q.append(ns)
                    k+=1
    return None, len(seen)
