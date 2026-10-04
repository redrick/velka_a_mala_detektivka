"""táta's block letters for titles and sound words, built from his handwriting font until he draws a real alphabet.

He builds a block letter from straight bars of even width: every free end is cut off with one straight line across
the bar, and where bars meet the corner is sharp. So a glyph of his handwriting is thinned to its centre line, the
centre line is straightened into a few segments, and the segments are drawn as wide bars with flat ends.

bars(font_file, ch) -> [(points, closed, free_start, free_end[, width])], points in em units, y up from the baseline;
width (a share of the bar width) only on accent marks.
"""
import numpy as np, cv2

PX = 160          # raster size of one em while thinning
SPUR = 0.09       # side branches shorter than this (em) are thinning noise, not strokes
STRAIGHTEN = 0.04 # how far (em) the centre line may be pulled straight; bigger = fewer, longer bars
DOT = 0.07        # a dot or a tiny mark becomes a bar this long (em)
ACCENT_Y = 0.78   # a separate mark wholly above this (em) is an accent

_CACHE = {}


def _outline(font_file, ch):
    from fontTools.ttLib import TTFont
    from fontTools.pens.basePen import BasePen
    tt = TTFont(font_file); upm = tt["head"].unitsPerEm
    gname = tt.getBestCmap().get(ord(ch))
    contours = []

    class Flat(BasePen):
        def _moveTo(self, p): contours.append([p])
        def _lineTo(self, p): contours[-1].append(p)
        def _qCurveToOne(self, p1, p2):
            p0 = contours[-1][-1]
            for t in np.linspace(0.125, 1, 8):
                contours[-1].append(tuple((1-t)**2*np.array(p0) + 2*(1-t)*t*np.array(p1) + t*t*np.array(p2)))
        def _curveToOne(self, p1, p2, p3):
            p0 = contours[-1][-1]
            for t in np.linspace(0.125, 1, 8):
                u = 1 - t
                contours[-1].append(tuple(u**3*np.array(p0) + 3*u*u*t*np.array(p1) + 3*u*t*t*np.array(p2) + t**3*np.array(p3)))
    if gname: tt.getGlyphSet()[gname].draw(Flat(tt.getGlyphSet()))
    return [np.array(c, np.float64) / upm for c in contours if len(c) > 2]


def _thin(img):
    """Zhang-Suen thinning of a 0/1 image"""
    img = np.pad(img.astype(np.uint8), 1)
    while True:
        changed = False
        for step in (0, 1):
            P = [np.roll(np.roll(img, -dy, 0), -dx, 1) for dy, dx in
                 ((-1, 0), (-1, 1), (0, 1), (1, 1), (1, 0), (1, -1), (0, -1), (-1, -1))]  # P2..P9 clockwise
            B = sum(P)
            A = sum(((P[i] == 0) & (P[(i + 1) % 8] == 1)) for i in range(8))
            if step == 0: c = (P[0]*P[2]*P[4] == 0) & (P[2]*P[4]*P[6] == 0)
            else: c = (P[0]*P[2]*P[6] == 0) & (P[0]*P[4]*P[6] == 0)
            kill = (img == 1) & (B >= 2) & (B <= 6) & (A == 1) & c
            if kill.any(): img[kill] = 0; changed = True
        if not changed: return img[1:-1, 1:-1]


N8 = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 1), (1, -1), (1, 0), (1, 1)]


def _trace(sk):
    """skeleton pixels -> paths between nodes. Returns (paths, node_of) where each path is a list of pixels
    and node_of maps a pixel to its node id (junction clusters share one id; free ends get their own)"""
    pix = set(zip(*np.nonzero(sk)))
    nb = {p: [(p[0]+dy, p[1]+dx) for dy, dx in N8 if (p[0]+dy, p[1]+dx) in pix] for p in pix}
    junction = {p for p in pix if len(nb[p]) >= 3}
    node_of, nid = {}, 0
    for p in junction:  # neighbouring junction pixels are one node
        if p in node_of: continue
        stack = [p]; node_of[p] = nid
        while stack:
            q = stack.pop()
            for r in nb[q]:
                if r in junction and r not in node_of: node_of[r] = nid; stack.append(r)
        nid += 1
    for p in pix:
        if len(nb[p]) <= 1: node_of[p] = nid; nid += 1
    paths, visited, direct = [], set(), set()

    def walk(path):
        """extend path pixel by pixel; stop on reaching a node (taken into the path) or a dead end"""
        start = path[0]
        while True:
            cur = path[-1]
            cand = [r for r in nb[cur] if r not in visited and r != path[-2]]
            stop = [r for r in cand if r in node_of and (start not in node_of or node_of[r] != node_of[start] or len(path) > 4)]
            if stop: path.append(stop[0]); return path
            inner = [r for r in cand if r not in node_of]
            if not inner: return path
            inner.sort(key=lambda r: abs(r[0]-cur[0]) + abs(r[1]-cur[1]))  # straight on before a diagonal
            path.append(inner[0]); visited.add(inner[0])

    for s in [p for p in pix if p in node_of]:
        for n in nb[s]:
            if n in node_of:
                if node_of[n] != node_of[s] and (n, s) not in direct:
                    direct.add((s, n)); paths.append([s, n])
                continue
            if n in visited: continue
            visited.add(n)
            paths.append(walk([s, n]))
    for p in sorted(pix - visited - set(node_of)):  # closed loops with no node (O, 0)
        if p in visited: continue
        visited.add(p)
        path = [p]
        nxt = [r for r in nb[p] if r not in visited]
        if not nxt: paths.append(path); continue
        visited.add(nxt[0]); path = walk([p, nxt[0]])
        if path[-1] != p and p in nb[path[-1]]: path.append(p)
        paths.append(path)
    return paths, node_of


def _length(path): return sum(np.hypot(a[0]-b[0], a[1]-b[1]) for a, b in zip(path, path[1:]))


# Letters his handwriting can't give as block letters: the bowl of D or the loops of 6 and 8 close up when
# thinned, and his handwritten H, M, K are lowercase-like where his drawn capitals (HURÁ!, MŇAU, DETEKTIVKA) are
# not. Drawn here as bars on a box 1 high (cap height), width as given: [(points, closed, free_start, free_end)].
F, J = True, False  # a free end (cut straight across), an end inside another bar
MANUAL = {
    "D": (0.66, [([(0, 0), (0, 1), (0.42, 1), (0.66, 0.72), (0.66, 0.28), (0.42, 0)], True, J, J)]),
    "O": (0.74, [([(0.2, 0), (0.54, 0), (0.74, 0.3), (0.74, 0.7), (0.54, 1), (0.2, 1), (0, 0.7), (0, 0.3)], True, J, J)]),
    "0": (0.62, [([(0.16, 0), (0.46, 0), (0.62, 0.28), (0.62, 0.72), (0.46, 1), (0.16, 1), (0, 0.72), (0, 0.28)], True, J, J)]),
    "H": (0.62, [([(0, 0), (0, 1)], False, F, F), ([(0.62, 0), (0.62, 1)], False, F, F),
                 ([(0, 0.5), (0.62, 0.52)], False, J, J)]),
    "M": (0.82, [([(0, 0), (0, 1)], False, F, F), ([(0.82, 0), (0.82, 1)], False, F, F),
                 ([(0, 0.86), (0.41, 0.4), (0.82, 0.86)], False, J, J)]),
    "K": (0.64, [([(0, 0), (0, 1)], False, F, F), ([(0.62, 1), (0, 0.44)], False, F, J),
                 ([(0.18, 0.6), (0.64, 0)], False, J, F)]),
    "I": (0.0, [([(0, 0), (0, 1)], False, F, F)]),
    "J": (0.52, [([(0.52, 1), (0.52, 0.22), (0.36, 0), (0.1, 0), (0, 0.2)], False, F, F)]),
    "N": (0.64, [([(0, 0), (0, 1)], False, F, F), ([(0.64, 0), (0.64, 1)], False, F, F),
                 ([(0, 0.78), (0.64, 0.22)], False, J, J)]),
    "P": (0.58, [([(0, 0), (0, 1), (0.4, 1), (0.58, 0.84), (0.58, 0.6), (0.4, 0.44), (0, 0.44)], False, F, J)]),
    "T": (0.66, [([(0, 1), (0.66, 1)], False, F, F), ([(0.33, 1), (0.33, 0)], False, J, F)]),
    "U": (0.62, [([(0, 1), (0, 0.22), (0.16, 0), (0.46, 0), (0.62, 0.22), (0.62, 1)], False, F, F)]),
    "V": (0.7, [([(0, 1), (0.35, 0), (0.7, 1)], False, F, F)]),
    "6": (0.62, [([(0.54, 1), (0.08, 0.5), (0, 0.24), (0.18, 0), (0.46, 0), (0.62, 0.22), (0.48, 0.48), (0.06, 0.44)], False, F, J)]),
    "8": (0.62, [([(0.31, 0), (0.62, 0.24), (0.31, 0.5), (0, 0.24)], True, J, J),
                ([(0.31, 0.5), (0.57, 0.76), (0.31, 1), (0.05, 0.76)], True, J, J)]),
    ",": (0.0, [([(0.06, 0.12), (-0.02, -0.22)], False, F, F)]),
    "!": (0.0, [([(0, 0.34), (0, 1)], False, F, F), ([(0, 0), (0, 0.1)], False, F, F)]),
}
# accents, on a box 1 high above the letter, centred on it
MARKS = {
    "\u0301": [([(-0.08, 0), (0.14, 0.3)], False, F, F)],                    # čárka
    "\u030c": [([(-0.2, 0.28), (0, 0.02), (0.2, 0.28)], False, F, F)],       # háček, his little V
    "\u030a": [([(-0.09, 0.04), (0.09, 0.04), (0.09, 0.24), (-0.09, 0.24)], True, J, J)],  # kroužek
}
MARK_GAP = 0.17  # em between the letter's top and the mark: wide bars need room, or the outlines merge
MARK_W = 0.6     # a mark's bars are this much of a letter's bar width
# every capital and digit stands on one baseline and reaches one cap height (em), as in a drawn title;
# his handwriting wanders between 0.45 and 0.75 em tall
BASE, CAP = 0.12, 0.8
LEVEL = set("ABCDEFGHIJKLMNOPRSTUVWXYZ0123456789")


def _cap_box(font_file):
    return BASE, CAP, 0.05


def _level(parts):
    """scale a letter to the common cap height, keeping its proportions"""
    xs = [x for pts, *_ in parts for x, _ in pts]; ys = [y for pts, *_ in parts for _, y in pts]
    k = (CAP - BASE) / max(max(ys) - min(ys), 1e-6)
    return [([(0.05 + (x - min(xs)) * k, BASE + (y - min(ys)) * k) for x, y in pts], *rest) for pts, *rest in parts]


def _manual(font_file, ch):
    import random, zlib
    w, parts = MANUAL[ch]
    y0, y1, x0 = _cap_box(font_file)
    h = y1 - y0
    r = random.Random(zlib.crc32((font_file + ch).encode()))  # each of his two hands a touch different
    j = lambda: r.uniform(-0.035, 0.035)
    out = []
    for pts, closed, fs, fe in parts:
        out.append(([(x0 + (x + j()) * h, y0 + (y + j()) * h) for x, y in pts], closed, fs, fe))
    return out


def bars(font_file, ch):
    key = (font_file, ch)
    if key in _CACHE: return _CACHE[key]
    import unicodedata
    nfd = unicodedata.normalize("NFD", ch)
    if len(nfd) == 2 and nfd[1] in MARKS:
        base = bars(font_file, nfd[0])
        y0, y1, _ = _cap_box(font_file)
        h = y1 - y0
        xs = [x for pts, *_ in base for x, _ in pts]; ys = [y for pts, *_ in base for _, y in pts]
        cx, top = (min(xs) + max(xs)) / 2, max(ys) + MARK_GAP
        out = base + [([(cx + x * h, top + y * h) for x, y in pts], closed, fs, fe, MARK_W) for pts, closed, fs, fe in MARKS[nfd[1]]]
    elif ch in MANUAL:
        out = _manual(font_file, ch)
    else:
        out = _from_font(font_file, ch)
        if ch in LEVEL and out: out = _level(out)
    _CACHE[key] = out
    return out


def _from_font(font_file, ch):
    key = ("font", font_file, ch)
    if key in _CACHE: return _CACHE[key]
    out = []
    contours = _outline(font_file, ch)
    if contours:
        allp = np.vstack(contours)
        x0, y0 = allp.min(0) - 0.05; x1, y1 = allp.max(0) + 0.05
        w, h = int((x1 - x0) * PX) + 1, int((y1 - y0) * PX) + 1
        img = np.zeros((h, w), np.uint8)
        polys = [np.stack([(c[:, 0] - x0) * PX, (y1 - c[:, 1]) * PX], 1).round().astype(np.int32) for c in contours]
        cv2.fillPoly(img, polys, 1)
        to_em = lambda r, c: (c / PX + x0, y1 - r / PX)
        for lab in range(1, cv2.connectedComponents(img)[0]):
            comp = cv2.connectedComponents(img)[1] == lab
            ys, xs = np.nonzero(comp)
            if max(np.ptp(ys), np.ptp(xs)) < DOT * PX * 1.4:  # a dot, a tiny accent: one short bar
                cy, cx = ys.mean(), xs.mean()
                out.append(([to_em(cy + DOT*PX/2, cx), to_em(cy - DOT*PX/2, cx)], False, True, True)); continue
            paths, node_of = _trace(_thin(comp))
            # prune short side branches, then rejoin what pruning left as a plain bend
            for _ in range(2):
                deg = {}
                for p in paths:
                    for e in (p[0], p[-1]):
                        if e in node_of: deg[node_of[e]] = deg.get(node_of[e], 0) + 1
                keep = []
                for p in paths:
                    d = sorted(deg.get(node_of.get(e), 0) for e in (p[0], p[-1]))
                    if d[0] <= 1 and d[1] >= 3 and _length(p) < SPUR * PX: continue  # hangs off a junction
                    keep.append(p)
                paths = keep
            merged = True
            while merged:
                merged = False
                ends = {}
                for i, p in enumerate(paths):
                    if p[0] == p[-1]: continue
                    for j, e in enumerate((p[0], p[-1])):
                        if e in node_of: ends.setdefault(node_of[e], []).append((i, j))
                for n, lst in ends.items():
                    if len(lst) == 2 and lst[0][0] != lst[1][0]:
                        (i, a), (k, b) = lst
                        pi = paths[i] if a == 1 else paths[i][::-1]
                        pk = paths[k] if b == 0 else paths[k][::-1]
                        paths[i] = pi + pk[1:]; paths.pop(k); merged = True; break
            deg = {}
            for p in paths:
                for e in (p[0], p[-1]):
                    if e in node_of: deg[node_of[e]] = deg.get(node_of[e], 0) + 1
            centre = {}
            for p, n in node_of.items(): centre.setdefault(n, []).append(p)
            centre = {n: np.mean(v, 0) for n, v in centre.items()}
            for p in paths:
                closed = len(p) > 3 and p[0] == p[-1]
                pts = np.array([(c, r) for r, c in p], np.float32)
                if not closed:  # ends meeting other bars sit on the junction's middle
                    for idx in (0, -1):
                        e = p[idx]
                        if e in node_of and deg.get(node_of[e], 0) > 1:
                            cr, cc = centre[node_of[e]]; pts[idx] = (cc, cr)
                q = cv2.approxPolyDP(pts.reshape(-1, 1, 2), STRAIGHTEN * PX, closed).reshape(-1, 2)
                if len(q) < 2: q = pts[[0, -1]]
                em = [to_em(r, c) for c, r in q]
                if not closed and np.hypot(em[-1][0] - em[0][0], em[-1][1] - em[0][1]) < DOT and len(em) <= 2:
                    # a dab of the pen (an accent, a dot): at least a short bar, leaning the way he pushed it
                    (ax, ay), (bx, by) = em[0], em[-1]
                    d = np.hypot(bx - ax, by - ay)
                    ux, uy = ((bx - ax) / d, (by - ay) / d) if d > 1e-6 else (0.35, 0.94)
                    mx, my = (ax + bx) / 2, (ay + by) / 2
                    em = [(mx - ux*DOT/2, my - uy*DOT/2), (mx + ux*DOT/2, my + uy*DOT/2)]
                fs = not closed and deg.get(node_of.get(p[0]), 1) <= 1
                fe = not closed and deg.get(node_of.get(p[-1]), 1) <= 1
                out.append((em, closed, fs, fe))
    # his handwriting puts čárky and háčky off to the right; on a block letter they sit over its middle
    if len(out) > 1:
        tops = [min(y for _, y in b[0]) for b in out]
        body = [b for b, t in zip(out, tops) if t < ACCENT_Y]
        marks = [i for i, t in enumerate(tops) if t >= ACCENT_Y]
        if body and marks:
            bx = [x for b in body for x, _ in b[0]]; mid = (min(bx) + max(bx)) / 2
            mx = [x for i in marks for x, _ in out[i][0]]; shift = mid - (min(mx) + max(mx)) / 2
            for i in marks:
                pts, closed, fs, fe = out[i]
                out[i] = ([(x + shift, y) for x, y in pts], closed, fs, fe)
    _CACHE[key] = out
    return out


def profile(font_file, ch, half, widen=1.0, rot=0.0, step=0.08):
    """the letter's left and right edge in horizontal bands of `step`, as drawn: x stretched by `widen`, then
    turned `rot` degrees about the origin (em units): {band: (left, right)}.
    `half` is half a bar's width: a bar reaches that far sideways only where it runs up and down;
    a level bar's straight-cut end stops at its end point."""
    import math
    c, s_ = math.cos(math.radians(rot)), math.sin(math.radians(rot))
    edges = {}
    for b in bars(font_file, ch):
        hw = half * (b[4] if len(b) > 4 else 1)
        pts = list(b[0]) + ([b[0][0]] if b[1] else [])
        if len(pts) == 1: pts = pts * 2
        pts = [(x*widen*c - y*s_, x*widen*s_ + y*c) for x, y in pts]
        for (ax, ay), (bx, by) in zip(pts, pts[1:]):
            d = np.hypot(bx - ax, by - ay)
            reach = hw * (abs(by - ay) / d if d > 1e-9 else 1)
            n = max(2, int(d / (step / 3)) + 1)
            for t in np.linspace(0, 1, n):
                x, y = ax + (bx - ax) * t, ay + (by - ay) * t
                k = int(np.floor(y / step))
                lo, hi = edges.get(k, (x - reach, x + reach))
                edges[k] = (min(lo, x - reach), max(hi, x + reach))
    return edges
