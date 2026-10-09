"""Turn the family's scanned style sheets (scan_reader.py output) into the personal style ("osobni").

Usage:  python build_style.py [vystup_dir]      default: the vault's topics/styl/vystup
Writes art/style_data/:
  lines.json     stroke wobble, bow, pressure and taper measured from táta's lines; hatching from his shading
  palette.json   palette.py overrides from the girls' crayon swatches (whole colour families follow their anchor)
  faces.json     táta's expressions as vector outlines, in units of the face circle he drew them in
  stamps/        trimmed ink PNGs: nature, motifs, sound words, balloons
and the fonts art/fonts/TataHand.ttf (comic lettering) and art/fonts/AlicaHand.ttf (Alica's capitals).
Nothing changes until the style is switched on: VMD_STYLE=osobni (see osobni.py).
"""
import os, sys, json, math, unicodedata
import numpy as np
import cv2

HERE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(HERE, "style_data")
VYSTUP = os.path.expanduser("~/SynologyDrive/redrick-obsidian/ai-memory/velka_a_mala_detektivka/topics/styl/vystup")
INSET_MM = 1.2
PT_PER_MM = 72 / 25.4


class Scans:
    def __init__(self, root):
        self.root = root
        self.man = json.load(open(os.path.join(root, "manifest.json")))
        self.layout = json.load(open(os.path.join(os.path.dirname(root.rstrip("/")), "styl_listy_layout.json")))
        self.ppm = {s["code"]: s["px_per_mm"] for s in self.man["scans"] if s["copy"] == 1}
        self.boxes = {b["id"]: (s["code"], b) for s in self.man["scans"] if s["copy"] == 1 for b in s["boxes"]}
        self.geom = {b["id"]: b for p in self.layout["pages"] for b in p["boxes"]}

    def ink(self, bid):
        """alpha 0..255, or None for an empty box"""
        code, b = self.boxes[bid]
        if b["empty"] or "ink" not in b: return None
        return cv2.imread(os.path.join(self.root, b["ink"]), cv2.IMREAD_UNCHANGED)[:, :, 3]

    def colour(self, bid):
        code, b = self.boxes[bid]
        return None if b["empty"] else cv2.imread(os.path.join(self.root, b["png"]))

    def ppm_of(self, bid): return self.ppm[self.boxes[bid][0]]

    def filled(self, prefix): return [k for k, (c, b) in self.boxes.items() if k.startswith(prefix) and not b["empty"]]


# ------------------------------------------------------------------ lines
def centrelines(alpha, ppm, vertical=False, thr=90):
    """each roughly straight stroke as (s, offset, width) arrays in mm; fragments of one light pencil line are merged"""
    a = alpha.T if vertical else alpha
    m = (a > thr).astype(np.uint8)
    glue = cv2.dilate(m, cv2.getStructuringElement(cv2.MORPH_RECT, (int(ppm * 6) | 1, int(ppm * 0.8) | 1)))
    n, lab, st, _ = cv2.connectedComponentsWithStats(glue, 8)
    out = []
    for i in range(1, n):
        x, y, w, h, _ = st[i]
        if w < ppm * 15: continue
        sub = m[y:y + h, x:x + w] * (lab[y:y + h, x:x + w] == i)
        cols = [(c, np.where(sub[:, c])[0]) for c in range(w)]
        cols = [(c, ys.mean() + y, len(ys)) for c, ys in cols if len(ys)]
        if len(cols) < ppm * 15: continue
        arr = np.array(cols, float) / ppm
        out.append(arr)
    return out


def measure_lines(S):
    bows, wob_rms, spectra, widths, cvs, tapers = [], [], [], [], [], []
    for bid, vertical in (("cary_vod_pomalu", 0), ("cary_vod_rychle", 0), ("cary_dlouhe", 0), ("cary_svisle", 1), ("cary_tlak", 0),
                          ("pismo_veta_0", 0), ("pismo_veta_2", 0)):
        a = S.ink(bid)
        if a is None: continue
        ppm = S.ppm_of(bid)
        for arr in centrelines(a, ppm, vertical):
            s, y, t = arr[:, 0] - arr[0, 0], arr[:, 1], arr[:, 2]
            L = s[-1]
            if bid.startswith("cary"):
                q = np.polyfit(s, y, 2); lin = np.polyfit(s, y, 1)
                bow = np.abs(np.polyval(q, s) - np.polyval(lin, s)).max()
                bows.append(bow / L)
                r = y - np.polyval(q, s)
                wob_rms.append(r.std())
                grid = np.arange(0, L, 0.25)
                rr = np.interp(grid, s, r)
                F = np.abs(np.fft.rfft(rr - rr.mean())) ** 2; fr = np.fft.rfftfreq(len(rr), d=0.25)
                band = (fr > 1 / 40) & (fr < 1 / 2)
                spectra.append((fr[band], F[band] / F[band].sum()))
            if bid.startswith("cary") and bid != "cary_tlak":
                med = np.median(t); widths.append(med); cvs.append(t.std() / med)
                k = max(3, int(len(t) * 0.1))
                tapers.append(min(t[:k].mean(), t[-k:].mean()) / med)
    # pool the spectra into wavelength bins, keep the two strongest wobble periods
    bins = np.array([2, 3, 4.5, 6.5, 9, 13, 18, 26, 40])
    power = np.zeros(len(bins) - 1)
    for fr, p in spectra:
        wl = 1 / fr
        for j in range(len(bins) - 1):
            power[j] += p[(wl >= bins[j]) & (wl < bins[j + 1])].sum()
    order = np.argsort(power)[::-1][:2]
    periods = [float(math.sqrt(bins[j] * bins[j + 1])) for j in order]
    weights = power[order] / power[order].sum()
    res = dict(
        strokes=len(bows),
        bow_per_len=round(float(np.median(bows)), 4),
        wobble_mm=round(float(np.median(wob_rms)), 3),
        wobble_periods_mm=[round(p, 1) for p in periods], wobble_weights=[round(float(w), 2) for w in weights],
        width_mm=round(float(np.median(widths)), 3), pressure_cv=round(float(np.median(cvs)), 3),
        end_width_ratio=round(float(np.median(tapers)), 3))
    res["hatch"] = measure_hatch(S)
    return res


def dominant_angles(alpha, ppm, n=2):
    """stroke directions (deg, 0 = horizontal, counter-clockwise) from the gradient orientation histogram"""
    g = alpha.astype(np.float32)
    gx = cv2.Sobel(g, cv2.CV_32F, 1, 0, ksize=5); gy = cv2.Sobel(g, cv2.CV_32F, 0, 1, ksize=5)
    mag = np.hypot(gx, gy)
    sel = mag > np.percentile(mag, 90)
    # a stroke runs perpendicular to its gradient; image y points down, so flip the sign
    ang = (np.degrees(np.arctan2(-gy[sel], gx[sel])) + 90) % 180
    hist, edges = np.histogram(ang, bins=36, range=(0, 180), weights=mag[sel])
    hist = np.convolve(np.r_[hist[-2:], hist, hist[:2]], [1, 2, 3, 2, 1], "same")[2:-2]
    peaks = []
    for i in np.argsort(hist)[::-1]:
        a = (edges[i] + edges[i + 1]) / 2
        if all(min(abs(a - p), 180 - abs(a - p)) > 25 for p in peaks): peaks.append(float(a))
        if len(peaks) == n: break
    return peaks


def spacing_along(alpha, ppm, ang):
    """distance between neighbouring hatch strokes: turn the strokes upright and count crossings on many rows"""
    h, w = alpha.shape
    M = cv2.getRotationMatrix2D((w / 2, h / 2), -(ang - 90), 1.0)
    rot = cv2.warpAffine(alpha, M, (w, h))
    core = rot[h // 5:4 * h // 5, w // 5:4 * w // 5]
    gaps = []
    for row in core[::max(1, int(ppm))]:
        # light pencil: count local peaks (one per stroke) rather than threshold crossings
        v = cv2.GaussianBlur(row.astype(np.float32).reshape(1, -1), (7, 1), 0)[0]
        r = max(2, int(ppm * 0.4))
        peaks = [i for i in range(r, len(v) - r) if v[i] > 15 and v[i] == v[i - r:i + r + 1].max()]
        if len(peaks) > 2: gaps.extend(np.diff(peaks) / ppm)
    return float(np.median(gaps)) if gaps else 2.0


def end_weight(alpha, ppm, ang):
    """how much darker a hatch stroke gets toward its far end (1 = even, >1 = pressed at the end)"""
    h, w = alpha.shape
    M = cv2.getRotationMatrix2D((w / 2, h / 2), -(ang - 90), 1.0)
    rot = cv2.warpAffine(alpha, M, (w, h)).astype(np.float32)
    prof = rot[:, w // 5:4 * w // 5].mean(axis=1)
    top, bot = prof[h // 6:h // 3].mean(), prof[2 * h // 3:5 * h // 6].mean()
    return float(bot / max(top, 1))  # >1: the stroke is pressed harder at its far end


def stroke_lengths(alpha, ppm):
    m = (alpha > 90).astype(np.uint8)
    n, lab, st, _ = cv2.connectedComponentsWithStats(m, 8)
    L = [math.hypot(st[i, 2], st[i, 3]) / ppm for i in range(1, n) if st[i, 4] > ppm * ppm * 0.5]
    return float(np.median(L)) if L else 10.0


def measure_hatch(S):
    out = {}
    a = S.ink("srafy_rovne")
    if a is not None:
        ppm = S.ppm_of("srafy_rovne"); ang = dominant_angles(a, ppm, 1)[0]
        out.update(angle=round(ang, 1), spacing_mm=round(spacing_along(a, ppm, ang), 2),
                   end_weight=round(end_weight(a, ppm, ang), 2))
    a = S.ink("srafy_krizove")
    if a is not None:
        ppm = S.ppm_of("srafy_krizove")
        out["cross_angles"] = [round(x, 1) for x in dominant_angles(a, ppm, 2)]
    a = S.ink("srafy_stin_postava")
    if a is not None:
        ppm = S.ppm_of("srafy_stin_postava"); ang = dominant_angles(a, ppm, 1)[0]
        out["shadow"] = dict(angle=round(ang, 1), spacing_mm=round(spacing_along(a, ppm, ang), 2))
    return out


# ------------------------------------------------------------------ vector outlines (faces, fonts)
def outlines(mask, eps=0.6, min_area=12):
    """outer contours and holes of a binary mask as point lists (pixel coords); smooth, simplified"""
    cnts, hier = cv2.findContours(mask.astype(np.uint8), cv2.RETR_CCOMP, cv2.CHAIN_APPROX_NONE)
    out = []
    if hier is None: return out
    for c, h in zip(cnts, hier[0]):
        if cv2.contourArea(c) < min_area: continue
        pts = c[:, 0, :].astype(np.float32)
        if len(pts) > 8:  # light smoothing along the outline before simplifying
            k = 2
            pts = np.stack([np.convolve(np.r_[pts[-k:, i], pts[:, i], pts[:k, i]], np.ones(2 * k + 1) / (2 * k + 1), "valid") for i in (0, 1)], 1)
        ap = cv2.approxPolyDP(pts.astype(np.float32).reshape(-1, 1, 2), eps, True)[:, 0, :]
        if len(ap) >= 3: out.append(dict(pts=ap.tolist(), hole=bool(h[3] >= 0)))
    return out


def clean_mask(alpha, ppm, thr=100, close_mm=0.15, min_mm2=0.25):
    m = (alpha > thr).astype(np.uint8)
    k = max(1, int(ppm * close_mm))
    m = cv2.morphologyEx(m, cv2.MORPH_CLOSE, cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (2 * k + 1, 2 * k + 1)))
    n, lab, st, _ = cv2.connectedComponentsWithStats(m, 8)
    keep = np.zeros(n, bool); keep[1:] = st[1:, 4] >= min_mm2 * ppm * ppm
    return keep[lab].astype(np.uint8)


FACE_MOODS = ["happy", "grin", "surprised", "wow", "think", "worried", "whisper", "determined", "sleepy", "sad"]


def build_faces(S):
    """expressions in face-circle units: x right, y up, circle radius 1. Strokes are thickened to the comic's
    feature weight (about 5 % of the radius) so they read at character size."""
    faces = {}
    for mood in FACE_MOODS:
        bid = f"obliceje_{mood}"
        a = S.ink(bid)
        if a is None: continue
        ppm = S.ppm_of(bid); g = S.geom[bid]
        r = min(g["w"], g["h"]) * 0.36 * ppm
        cx, cy = (g["w"] / 2 - INSET_MM) * ppm, (g["h"] / 2 - INSET_MM) * ppm
        m = clean_mask(a, ppm)
        # keep what lies inside the face circle (stray marks outside belong to nothing)
        yy, xx = np.mgrid[:m.shape[0], :m.shape[1]]
        m *= ((xx - cx) ** 2 + (yy - cy) ** 2 < (r * 1.05) ** 2).astype(np.uint8)
        width = cv2.distanceTransform(m, cv2.DIST_L2, 3).max() * 2
        grow = max(0, int(round((0.05 * r - width) / 2)))
        if grow: m = cv2.dilate(m, cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (2 * grow + 1, 2 * grow + 1)))
        polys = outlines(m, eps=r * 0.006, min_area=(r * 0.02) ** 2)
        for p in polys: p["pts"] = [[round((x - cx) / r, 4), round((cy - y) / r, 4)] for x, y in p["pts"]]
        faces[mood] = polys
    return faces


# ------------------------------------------------------------------ fonts
UPM = 1000
CAP = 700
XH = 470


def glyph_name(ch):
    from fontTools.agl import UV2AGL
    return UV2AGL.get(ord(ch), f"uni{ord(ch):04X}")


def glyph_from_cell(alpha, ppm, base_px, unit_px, min_mm2=0.2, weight=0.1):
    """contours in font units (y up from the baseline) and the ink's x extent. Pencil strokes are thickened to
    `weight` x cap height, or the letters turn to hairlines at subtitle size."""
    # light pencil breaks up: bridge gaps up to ~0.6 mm, then grey smudges where a letter met a guide fall to the area limit
    m = clean_mask(alpha, ppm, thr=80, close_mm=0.3, min_mm2=min_mm2)
    if not m.any(): return None
    dt = cv2.distanceTransform(m, cv2.DIST_L2, 3)
    width = 2 * float(np.percentile(dt[dt > 0], 90))
    grow = int(round((weight * unit_px * CAP / UPM - width) / 2))
    if grow > 0: m = cv2.dilate(m, cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (2 * grow + 1, 2 * grow + 1)))
    polys = outlines(m, eps=max(0.6, ppm * 0.05), min_area=ppm * ppm * min_mm2)
    sc = UPM / unit_px
    out = []
    for p in polys:
        out.append(dict(pts=[(x * sc, (base_px - y) * sc) for x, y in p["pts"]], hole=p["hole"]))
    xs = [x for p in out for x, _ in p["pts"]]; ys = [y for p in out for _, y in p["pts"]]
    parts = sum(1 for p in out if not p["hole"])
    return dict(polys=out, x0=min(xs), x1=max(xs), h=max(ys) - min(ys), parts=parts)


# what was written into the wrong cell on the printed sheet
CELL_FIXES = {".": ",", ",": "."}
# variants that came out broken on the scan (index in sheet order)
DROP_VARIANTS = {"J": [0]}


def tidy_variants(glyphs):
    """apply CELL_FIXES and drop a variant that came out much smaller than its pair (a slip, not a style)"""
    fixed = {}
    for ch, vs in glyphs.items():
        fixed.setdefault(CELL_FIXES.get(ch, ch), []).extend(vs)
    for ch, drop in DROP_VARIANTS.items():
        if ch in fixed and len(fixed[ch]) > 1:
            fixed[ch] = [v for i, v in enumerate(fixed[ch]) if i not in drop]
    for ch, vs in fixed.items():
        if len(vs) > 1:
            top = max(v["h"] for v in vs)
            fewest = min(v["parts"] for v in vs)
            fixed[ch] = [v for v in vs if v["h"] >= top * 0.6 and v["parts"] <= fewest + 1]
    return fixed


def normalise(glyphs, cap=750):
    """scale so a plain capital stands `cap` units tall: people write smaller than the guide lines,
    and the comic's balloons are sized for a font with big capitals"""
    hs = [vs[0]["h"] for ch, vs in glyphs.items() if ch in "ABDEFHIKLMNPRTUVWXZ"]
    if not hs: return glyphs
    k = cap / float(np.median(hs))
    for vs in glyphs.values():
        for v in vs:
            for p in v["polys"]: p["pts"] = [(x * k, y * k) for x, y in p["pts"]]
            v["x0"] *= k; v["x1"] *= k; v["h"] *= k
    return glyphs


def collect_tata(S):
    """{char: [variants]} from táta's letter pages; cell geometry from scan_sheets.glyph_cell"""
    glyphs = {}
    for prefix in ("pismo_velka_", "pismo_mala_", "pismo_znaky_"):
        for bid in sorted(S.filled(prefix)):
            code, b = S.boxes[bid]; g = S.geom[bid]
            ppm = S.ppm_of(bid)
            a = S.ink(bid)
            if a is None: continue
            base = (g["h"] * 0.72 - INSET_MM) * ppm
            unit = (g["h"] * 0.48) * ppm / CAP * UPM  # cap line sits 0.48 h above the baseline
            gl = glyph_from_cell(a, ppm, base, unit)
            if gl: glyphs.setdefault(b["glyph"], []).append(gl)
    return centre_accents(normalise(tidy_variants(glyphs)))


def centre_accents(glyphs):
    """a capital's accent that landed beside the letter (táta's Í: I, then a čárka off to the right) is moved
    over it, or "PŘÍPAD" reads as "PŘI´PAD" now that the comic letters in capitals"""
    for ch, vs in glyphs.items():
        if not (ch.isupper() and len(unicodedata.normalize("NFD", ch)) > 1): continue
        for v in vs:
            solid = [p for p in v["polys"] if not p["hole"]]
            low = lambda p: min(y for _, y in p["pts"])
            standing = [max(y for _, y in p["pts"]) for p in solid if low(p) < 200]  # the letter stands on the baseline
            if not standing: continue
            top = max(standing)
            marks = [p for p in solid if low(p) > top * 0.8]
            body = [p for p in v["polys"] if p not in marks]
            if not marks or not body: continue
            bx = [x for p in body for x, _ in p["pts"]]; mx = [x for p in marks for x, _ in p["pts"]]
            b0, b1, m0, m1 = min(bx), max(bx), min(mx), max(mx)
            if b0 <= (m0 + m1) / 2 <= b1: continue
            dx = (b0 + b1) / 2 - (m0 + m1) / 2 + (m1 - m0) * 0.2  # centred, leaning right a little as he writes them
            for p in marks: p["pts"] = [(x + dx, y) for x, y in p["pts"]]
            xs = [x for p in v["polys"] for x, _ in p["pts"]]
            v["x0"], v["x1"] = min(xs), max(xs)
    return glyphs


def collect_alica(S):
    glyphs = {}
    cells = [(bid, 0.8) for bid in S.filled("alica_pismeno_")] + [(bid, 0.8) for bid in S.filled("alica_cislo_")]
    heights = []
    raw = []
    for bid, basef in cells:
        code, b = S.boxes[bid]; g = S.geom[bid]; ppm = S.ppm_of(bid)
        a = S.ink(bid)
        if a is None: continue
        m = clean_mask(a, ppm, thr=95)
        ys = np.where(m.any(axis=1))[0]
        if not len(ys): continue
        base = (g["h"] * basef - INSET_MM) * ppm
        heights.append((base - ys.min()) / ppm)
        raw.append((b["glyph"], a, ppm, base))
    # her letters vary a lot in size: one scale for all, from the median height of the plain capitals
    cap_mm = float(np.median(heights)) if heights else 20.0
    for ch, a, ppm, base in raw:
        gl = glyph_from_cell(a, ppm, base, cap_mm * ppm / CAP * UPM, weight=0.08)
        if gl: glyphs.setdefault(ch, []).append(gl)
    return normalise(glyphs)


def orient(pts, clockwise):
    area = sum(x0 * y1 - x1 * y0 for (x0, y0), (x1, y1) in zip(pts, pts[1:] + pts[:1]))
    return pts if (area < 0) == clockwise else list(reversed(pts))


def build_font(glyphs, family, path, space=280, side=40, alternates=True):
    from fontTools.fontBuilder import FontBuilder
    from fontTools.pens.ttGlyphPen import TTGlyphPen
    from fontTools.feaLib.builder import addOpenTypeFeaturesFromString
    order = [".notdef", "space"]
    cmap, metrics, glyf = {32: "space"}, {}, {}
    pen = TTGlyphPen(None); glyf[".notdef"] = pen.glyph(); metrics[".notdef"] = (500, 0)
    glyf["space"] = TTGlyphPen(None).glyph(); metrics["space"] = (space, 0)
    alts = []

    def add(name, gl):
        pen = TTGlyphPen(None)
        dx = side - gl["x0"]
        for p in gl["polys"]:
            pts = [(round(x + dx), round(y)) for x, y in p["pts"]]
            pts = orient(pts, clockwise=not p["hole"])  # TrueType: outer contours clockwise
            pen.moveTo(pts[0])
            for q in pts[1:]: pen.lineTo(q)
            pen.closePath()
        glyf[name] = pen.glyph()
        metrics[name] = (round(gl["x1"] - gl["x0"] + 2 * side), side)
        order.append(name)

    for ch, vs in sorted(glyphs.items()):
        name = glyph_name(ch)
        add(name, vs[0]); cmap[ord(ch)] = name
        if alternates and len(vs) > 1:
            add(name + ".alt", vs[1]); alts.append(name)
    fb = FontBuilder(UPM, isTTF=True)
    fb.setupGlyphOrder(order)
    fb.setupCharacterMap(cmap)
    fb.setupGlyf(glyf)
    fb.setupHorizontalMetrics(metrics)
    fb.setupHorizontalHeader(ascent=900, descent=-300)
    fb.setupNameTable(dict(familyName=family, styleName="Regular", uniqueFontIdentifier=f"{family}-Regular",
                           fullName=family, psName=family.replace(" ", ""), version="1.0",
                           copyright="Drawn by hand by the Antas family, 2026"))
    fb.setupOS2(sTypoAscender=900, sTypoDescender=-300, usWinAscent=1000, usWinDescent=350, sCapHeight=CAP, sxHeight=XH)
    fb.setupPost()
    if alts:
        # alternate every other letter, so a doubled letter (ČMUCH ČMUCH, "kk") never repeats the same drawing
        base = " ".join(alts); alt = " ".join(a + ".alt" for a in alts)
        # a letter after a plain letter takes its alternate; the lookback sees the substituted glyph, so it alternates
        fea = f"""languagesystem DFLT dflt;\nlanguagesystem latn dflt;\n@base = [{base}];\n@alt = [{alt}];\n
feature calt {{ sub @base @base' by @alt; }} calt;"""
        addOpenTypeFeaturesFromString(fb.font, fea)
    fb.save(path)
    return len(cmap) - 1, len(alts)


# ------------------------------------------------------------------ palette
def lab(hexs):
    rgb = np.array([[[int(hexs[i:i + 2], 16) for i in (5, 3, 1)]]], np.uint8)  # BGR for OpenCV
    return cv2.cvtColor(rgb, cv2.COLOR_BGR2LAB)[0, 0].astype(np.float32)


def lch(v):
    a, b = v[1] - 128, v[2] - 128
    return v[0], math.hypot(a, b), math.atan2(b, a)


def relate(o, old, new):
    """move `o` the way the anchor moved from `old` to `new`: hue turns with it, chroma scales, lightness shifts"""
    oL, oC, oh = lch(o); aL, aC, ah = lch(old); nL, nC, nh = lch(new)
    L = oL + (nL - aL) * 0.8
    C = oC * (nC / aC if aC > 4 else 1.0)
    h = oh + (nh - ah) if aC > 4 else nh
    return np.array([L, 128 + C * math.cos(h), 128 + C * math.sin(h)])


def hexs_of(labv):
    bgr = cv2.cvtColor(np.clip(labv, 0, 255).astype(np.uint8).reshape(1, 1, 3), cv2.COLOR_LAB2BGR)[0, 0]
    return "#%02x%02x%02x" % (bgr[2], bgr[1], bgr[0])


# swatch on the colour sheet -> palette anchor, then entries that keep their relation to the anchor
FAMILIES = {
    "Alicina pláštěnka": ("ALICA_COAT", ["ALICA_COAT_FOLD", "ALICA_COLLAR"]),
    "Hančiny lacláče": ("DUNGAREES", []),
    "proužky Hančina trička": ("SWEATER_STRIPE", []),
    "Aličiny vlasy": ("ALICA_HAIR", ["ALICA_HAIR_LINE"]),
    "Hančiny vlasy": ("HANKA_HAIR", ["HANKA_CURL"]),
    "obličej – kůže": ("SKIN", ["SKIN_SHADE"]),
    "tráva": ("GRASS", ["GRASS_TRAIL", "HILLS", "TUFT", "TREE_CROWN", "BUSH", "REED"]),
    "nebe": ("SKY", []),
    "voda v rybníce": ("POND_WATER", ["POND_RIPPLE", "WATER"]),
    "střecha chalupy": ("ROOF", ["ROOF_EDGE", "BIRDHOUSE_ROOF"]),
    "dřevo – kůlna": ("SHED_WALL", ["PLANKS", "CRATE", "CRATE_DARK", "SHELF", "SHELF_BRACKET", "POST", "BIRDHOUSE_WOOD"]),
    "cesta a hlína": ("MUD", ["MUD_DARK"]),
    "kytky – červená": ("FLOWER", ["BERRY"]),
    "kytky – žlutá": ("LEAF_LIGHT", []),
    "opička (Hančin orangutan)": ("FUR", ["FUR_FACE", "FUR_BELLY"]),
}
FAVOURITES = {"Aličina nejoblíbenější": "alica", "Hančina nejoblíbenější": "hanka",
              "tátova nejoblíbenější": "tata", "mámina nejoblíbenější": "mama"}


def build_palette(root):
    sys.path.insert(0, HERE)
    import palette as P
    pal = json.load(open(os.path.join(root, "palette.json")))
    over, fav, notes = {}, {}, []
    for sw in pal["swatches"]:
        if sw.get("empty"): continue
        t = sw["target"]
        if t in FAVOURITES: fav[FAVOURITES[t]] = sw["hex"]; continue
        if t not in FAMILIES: notes.append(f"{t}: nemá v paletě protějšek"); continue
        anchor, family = FAMILIES[t]
        old = lab(getattr(P, anchor).hex); new = lab(sw["hex"])
        over[anchor] = sw["hex"]
        for name in family:
            if not hasattr(P, name): continue
            o = lab(getattr(P, name).hex)
            # keep the entry's relation to its anchor in LCh: lightness step, chroma ratio, hue offset
            over[name] = hexs_of(relate(o, old, new))
    return dict(print=pal["print"], overrides=over, favourites=fav, notes=notes)


# ------------------------------------------------------------------ stamps
def trim_save(alpha, path, pad=6):
    ys, xs = np.where(alpha > 40)
    if not len(ys): return False
    a = alpha[max(0, ys.min() - pad):ys.max() + pad, max(0, xs.min() - pad):xs.max() + pad]
    rgba = np.dstack([np.zeros_like(a)] * 3 + [a])
    cv2.imwrite(path, rgba)
    return True


def build_stamps(S):
    d = os.path.join(DATA, "stamps"); os.makedirs(d, exist_ok=True)
    n = 0
    for prefix in ("priroda_", "zvuky_", "bubliny_", "obrysy_", "alica_podpis", "otisky_hanka_podpis"):
        for bid in S.filled(prefix):
            a = S.ink(bid)
            if a is not None and trim_save(a, os.path.join(d, bid + ".png")): n += 1
    for bid in S.filled("alica_") + S.filled("hanka_") + S.filled("otisky_"):
        if bid.startswith(("alica_pismeno", "alica_cislo", "alica_slovo", "alica_podpis", "otisky_hanka_podpis")): continue
        c = S.colour(bid)
        if c is None: continue
        g = cv2.cvtColor(c, cv2.COLOR_BGR2LAB).astype(np.float32)
        paper = np.median(g.reshape(-1, 3), axis=0)
        a = np.clip((np.linalg.norm(g - paper, axis=2) - 8) * 6, 0, 255).astype(np.uint8)
        ys, xs = np.where(a > 40)
        if not len(ys): continue
        y0, y1, x0, x1 = ys.min(), ys.max() + 1, xs.min(), xs.max() + 1
        # a light pencil drawing would vanish when shrunk onto a wall: stretch its lightness (colour stays)
        lab_c = cv2.cvtColor(c, cv2.COLOR_BGR2LAB).astype(np.float32)
        ink = a > 60
        if ink.any():
            lo = np.percentile(lab_c[:, :, 0][ink], 3); hi = paper[0]
            lab_c[:, :, 0] = np.clip((lab_c[:, :, 0] - lo) / max(hi - lo, 1) * (hi - 30) + 30, 0, 255)
            c = cv2.cvtColor(lab_c.astype(np.uint8), cv2.COLOR_LAB2BGR)
        a = np.clip(a.astype(np.float32) * 1.6, 0, 255).astype(np.uint8)
        cv2.imwrite(os.path.join(d, bid + ".png"), np.dstack([c[y0:y1, x0:x1], a[y0:y1, x0:x1]])); n += 1
    return n


# ------------------------------------------------------------------ balloons and frames
def balloon_profile(alpha, ppm, n=180, tail=False, bridge_mm=0.8):
    """the drawn balloon as k(θ): its radius divided by the radius of the best-fitting ellipse, at n angles
    (θ counter-clockwise from +x, y up). A speech balloon's tail is cut out and bridged."""
    m = (alpha > 70).astype(np.uint8)
    k = max(1, int(ppm * bridge_mm))
    m = cv2.morphologyEx(m, cv2.MORPH_CLOSE, cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (2 * k + 1, 2 * k + 1)))
    filled = m.copy(); h, w = m.shape
    ff = np.zeros((h + 2, w + 2), np.uint8); cv2.floodFill(filled, ff, (0, 0), 2)
    inside = ((filled != 2) | (m > 0)).astype(np.uint8)
    cnts, _ = cv2.findContours(inside, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
    c = max(cnts, key=cv2.contourArea)[:, 0, :].astype(np.float64)
    # an axis-aligned ellipse through the drawing's own extent (his balloons are drawn level); work in its
    # parametric angle u, so the shape survives being stretched to any balloon's proportions
    cx = (np.percentile(c[:, 0], 99) + np.percentile(c[:, 0], 1)) / 2
    cy = (np.percentile(c[:, 1], 99) + np.percentile(c[:, 1], 1)) / 2
    rx = (np.percentile(c[:, 0], 99) - np.percentile(c[:, 0], 1)) / 2
    ry = (np.percentile(c[:, 1], 99) - np.percentile(c[:, 1], 1)) / 2
    X, Y = (c[:, 0] - cx) / rx, -(c[:, 1] - cy) / ry
    ang, rad = np.arctan2(Y, X), np.hypot(X, Y)
    th = np.linspace(-math.pi, math.pi, n, endpoint=False)
    out = []
    for t in th:
        d = np.abs((ang - t + math.pi) % (2 * math.pi) - math.pi)
        sel = d < (math.pi / n) * 1.5
        out.append(rad[sel].max() if sel.any() else np.nan)
    k = np.array(out)
    if tail:
        # the tail: where the outline bulges past its neighbourhood, plus a margin for its base
        local = np.array([np.nanmedian(np.take(k, range(i - 12, i + 13), mode="wrap")) for i in range(n)])
        bad = k > local * 1.04
        bad = np.convolve(np.r_[bad[-4:], bad, bad[:4]].astype(float), np.ones(9), "valid") > 0
        k[bad] = np.nan
    idx = np.arange(n); ok = ~np.isnan(k)
    k = np.interp(idx, idx[ok], k[ok], period=n)
    if n <= 180:  # smooth pixel steps; the shout keeps its sharp spikes
        k = np.convolve(np.r_[k[-2:], k, k[:2]], np.ones(5) / 5, "valid")
    k /= np.median(k)
    return [round(float(v), 4) for v in k], round(float(ry / rx), 3)


def dash_pattern(alpha, ppm):
    """lengths (mm) of the dashes and gaps going round a dashed balloon"""
    m = (alpha > 70).astype(np.uint8)
    n, lab, st, cen = cv2.connectedComponentsWithStats(m, 8)
    comps = [(cen[i], st[i, 4]) for i in range(1, n) if st[i, 4] > ppm * ppm * 0.3]
    if len(comps) < 4: return None
    c0 = np.mean([c for c, _ in comps], axis=0)
    comps.sort(key=lambda t: math.atan2(t[0][1] - c0[1], t[0][0] - c0[0]))
    lens = [math.hypot(st[i, 2], st[i, 3]) / ppm for i in range(1, n) if st[i, 4] > ppm * ppm * 0.3]
    pts = np.array([c for c, _ in comps])
    steps = np.hypot(*(np.roll(pts, -1, axis=0) - pts).T) / ppm
    return dict(dash_mm=round(float(np.median(lens)), 2), dash_cv=round(float(np.std(lens) / np.mean(lens)), 2),
                gap_mm=round(float(max(0.5, np.median(steps) - np.median(lens))), 2))


def frame_overshoot(alpha, ppm):
    """how far the frame lines run past the corners (mm), from a hand-drawn panel frame"""
    m = alpha > 90
    rows, cols = m.sum(axis=1), m.sum(axis=0)
    h, w = m.shape
    top = int(np.argmax(rows[:h // 3])); bot = h // 3 * 2 + int(np.argmax(rows[h // 3 * 2:]))
    left = int(np.argmax(cols[:w // 3])); right = w // 3 * 2 + int(np.argmax(cols[w // 3 * 2:]))
    band = max(2, int(ppm * 0.6))
    over = []
    for y in (top, bot):
        xs = np.where(m[max(0, y - band):y + band].any(axis=0))[0]
        if len(xs): over += [left - xs.min(), xs.max() - right]
    for x in (left, right):
        ys = np.where(m[:, max(0, x - band):x + band].any(axis=1))[0]
        if len(ys): over += [top - ys.min(), ys.max() - bot]
    over = [max(0, o) / ppm for o in over]
    return round(float(np.median(over)), 2), round(float(np.max(over)), 2)


def build_balloons(S):
    out = {}
    for key, bid, tail in (("speech", "bubliny_rec", True), ("thought", "bubliny_mysl", False),
                           ("shout", "bubliny_krik", False), ("whisper", "bubliny_septani", False)):
        a = S.ink(bid)
        if a is None: continue
        ppm = S.ppm_of(bid)
        # a dashed outline needs its gaps bridged before it can be filled
        prof, aspect = balloon_profile(a, ppm, n=360 if key == "shout" else 180, tail=tail,
                                       bridge_mm=2.5 if key == "whisper" else 0.8)
        out[key] = dict(profile=prof, aspect=aspect)
        if key == "whisper":
            dp = dash_pattern(a, ppm)
            if dp: out[key].update(dp)
    a = S.ink("bubliny_ramecek_siroky")
    if a is not None:
        med, mx = frame_overshoot(a, S.ppm_of("bubliny_ramecek_siroky"))
        out["frame"] = dict(overshoot_mm=med, overshoot_max_mm=mx)
    return out


# ------------------------------------------------------------------ textures
def coverage_tile(img, size=384):
    """how much pigment covers each pixel (0..255), from a coloured-in box; mirrored 2x2 so it tiles seamlessly"""
    labi = cv2.cvtColor(img, cv2.COLOR_BGR2LAB).astype(np.float32)
    paper = np.array([np.percentile(labi[:, :, 0], 99), 128, 128], np.float32)
    d = np.linalg.norm(labi - paper, axis=2)
    hi = max(np.percentile(d, 95), 10)
    cov = np.clip(d / hi, 0, 1)
    h, w = cov.shape
    c = cov[h // 8:h * 7 // 8, w // 8:w * 7 // 8]  # skip the edges, where colouring runs out
    side = min(c.shape)
    c = cv2.resize(c[:side, :side], (size // 2, size // 2), interpolation=cv2.INTER_AREA)
    tile = np.vstack([np.hstack([c, c[:, ::-1]]), np.hstack([c[::-1], c[::-1, ::-1]])])
    return (tile * 255).astype(np.uint8), float(cov.mean())


def build_textures(S):
    d = os.path.join(DATA, "textures"); os.makedirs(d, exist_ok=True)
    for f in os.listdir(d): os.remove(os.path.join(d, f))
    made = {"crayon": 0, "pencil": 0}
    # the girls' crayon colouring: dense swatches only, so a fill reads as coloured-in, not as a few scribbles
    for bid in sorted(S.filled("barvy_")) + ["textury_pastelka", "textury_voskovka"]:
        img = S.colour(bid)
        if img is None: continue
        tile, mean = coverage_tile(img)
        if mean < 0.45: continue
        cv2.imwrite(os.path.join(d, f"crayon_{made['crayon']:02d}.png"), tile); made["crayon"] += 1
    for bid in ("textury_tuzka_slabe", "textury_tuzka_stredne", "textury_tuzka_silne"):
        img = S.colour(bid)
        if img is None: continue
        tile, _ = coverage_tile(img)
        cv2.imwrite(os.path.join(d, f"pencil_{made['pencil']:02d}.png"), tile); made["pencil"] += 1
    # paper grain: the box left empty on purpose, high-passed and stretched
    img = S.colour("textury_papir")
    if img is not None:
        g = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY).astype(np.float32)
        grain = g - cv2.GaussianBlur(g, (0, 0), 6)
        grain = np.clip(128 + grain * 10, 0, 255).astype(np.uint8)
        side = min(grain.shape); c = cv2.resize(grain[:side, :side], (256, 256))
        cv2.imwrite(os.path.join(d, "paper.png"), np.vstack([np.hstack([c, c[:, ::-1]]), np.hstack([c[::-1], c[::-1, ::-1]])]))
    return made


def main():
    root = sys.argv[1] if len(sys.argv) > 1 else VYSTUP
    S = Scans(root)
    os.makedirs(DATA, exist_ok=True)
    lines = measure_lines(S)
    json.dump(lines, open(os.path.join(DATA, "lines.json"), "w"), indent=1)
    print("čára:", lines)
    faces = build_faces(S)
    json.dump(faces, open(os.path.join(DATA, "faces.json"), "w"))
    print("obličeje:", ", ".join(faces))
    pal = build_palette(root)
    json.dump(pal, open(os.path.join(DATA, "palette.json"), "w"), ensure_ascii=False, indent=1)
    print("paleta:", len(pal["overrides"]), "barev", "; ".join(pal["notes"]))
    tata = collect_tata(S)
    n, a = build_font(tata, "Tata Hand", os.path.join(HERE, "fonts", "TataHand.ttf"))
    # the same letters with the second version first, for the comic (ReportLab ignores OpenType alternates)
    build_font({ch: vs[::-1] for ch, vs in tata.items()}, "Tata Hand B", os.path.join(HERE, "fonts", "TataHandB.ttf"), alternates=False)
    print(f"písmo táty: {n} znaků, {a} se dvěma variantami")
    n, a = build_font(collect_alica(S), "Alica Hand", os.path.join(HERE, "fonts", "AlicaHand.ttf"), side=45, alternates=False)
    print(f"písmo Alice: {n} znaků")
    print("razítka:", build_stamps(S))
    print("textury:", build_textures(S))
    bal = build_balloons(S)
    json.dump(bal, open(os.path.join(DATA, "balloons.json"), "w"))
    print("bubliny:", {k: {kk: vv for kk, vv in v.items() if kk != "profile"} for k, v in bal.items()})


if __name__ == "__main__":
    main()
