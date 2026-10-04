"""Read filled-in style sheets (see scan_sheets.py) back from scans or phone photos.

Usage:  python scan_reader.py [scan_dir] [out_dir] [--layout styl_listy_layout.json] [--pdf styl_listy.pdf]
Defaults point at the Obsidian vault: topics/styl/skeny -> topics/styl/vystup.

Per scan: find the four corner squares, straighten the page, identify it by its QR code (or, failing that, by
comparing it with the printed PDF), then cut out every box from the layout, drop the pale cyan guides and save
  <out>/<page code>/<box id>.png      cleaned colour crop on white
  <out>/<page code>/<box id>_ink.png  black ink with transparency (line and lettering boxes only)
  <out>/<page code>/_nahled.png       downscaled page with the boxes marked (green = filled, red = empty)
plus <out>/manifest.json for every box and <out>/palette.json from the colour sheet.
Accepts PNG, JPG, TIFF and multi-page PDF scans.
"""
import os, sys, json, glob, argparse
import numpy as np
import cv2
import pymupdf

VAULT = os.path.expanduser("~/SynologyDrive/redrick-obsidian/ai-memory/velka_a_mala_detektivka/topics/styl")
INK_KINDS = {"lines", "curves", "shapes", "hatch", "panel", "balloon", "face", "trace", "glyph", "sentence",
             "title", "sound", "object", "word", "signature"}
COLOUR_KINDS = {"texture", "swatch", "kid_drawing", "print"}
EMPTY_BELOW = 0.0015
INSET_MM = 1.2


# ------------------------------------------------------------------ loading
def load_scans(scan_dir):
    exts = (".png", ".jpg", ".jpeg", ".tif", ".tiff", ".bmp", ".webp")
    for path in sorted(glob.glob(os.path.join(scan_dir, "*"))):
        low = path.lower()
        if low.endswith(".pdf"):
            doc = pymupdf.open(path)
            for i, p in enumerate(doc):
                pix = p.get_pixmap(dpi=300)
                img = np.frombuffer(pix.samples, np.uint8).reshape(pix.height, pix.width, pix.n)[:, :, :3]
                yield f"{os.path.basename(path)}#{i + 1}", cv2.cvtColor(img, cv2.COLOR_RGB2BGR)
        elif low.endswith(exts):
            img = cv2.imread(path, cv2.IMREAD_COLOR)
            if img is not None: yield os.path.basename(path), img


# ------------------------------------------------------------------ registration
def find_fiducials(img, layout):
    """the four solid corner squares: return their centres ordered tl, tr, br, bl, or raise"""
    grey = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    long_side = max(grey.shape)
    blur = cv2.GaussianBlur(grey, (5, 5), 0)
    otsu, _ = cv2.threshold(blur, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
    # light toner prints the squares mid-grey and colourful pages skew Otsu: try a few cut-offs, pool the squares
    cands = []
    for thr in sorted({float(np.clip(otsu, 100, 170)), 110.0, 140.0, 170.0, 190.0}):
        for c in square_blobs(blur < thr, long_side):
            if all(np.hypot(c[1] - o[1], c[2] - o[2]) > np.sqrt(c[0]) / 2 for o in cands): cands.append(c)
    if len(cands) < 4: raise ValueError(f"našel jsem jen {len(cands)} rohových čtverců")
    cands.sort(reverse=True)
    # the corner squares are the four biggest squares of similar size spanning the page
    pw, ph = layout["page"]
    want = (layout["fiducials"]["tr"][0] - layout["fiducials"]["tl"][0]) / (layout["fiducials"]["bl"][1] - layout["fiducials"]["tl"][1])
    best = None
    top = cands[:40]
    import itertools
    for combo in itertools.combinations(top, 4):
        areas = [c[0] for c in combo]
        if max(areas) / min(areas) > 1.8: continue
        pts = np.array([(c[1], c[2]) for c in combo], np.float32)
        quad = order_quad(pts)
        w = (np.linalg.norm(quad[1] - quad[0]) + np.linalg.norm(quad[2] - quad[3])) / 2
        h = (np.linalg.norm(quad[3] - quad[0]) + np.linalg.norm(quad[2] - quad[1])) / 2
        if h == 0: continue
        r = min(w / h, h / w)
        err = abs(r - want)
        if err > 0.12: continue
        d1, d2 = np.linalg.norm(quad[2] - quad[0]), np.linalg.norm(quad[3] - quad[1])
        if abs(d1 - d2) / max(d1, d2) > 0.08: continue  # a photo bends the rectangle a little, not this much
        side = h * layout["fiducial_size"] / (layout["fiducials"]["bl"][1] - layout["fiducials"]["tl"][1])
        if not all(0.6 < np.sqrt(a) / side < 1.6 for a in areas): continue
        # the real corner squares span the whole sheet; blobs inside a drawing span less
        score = (round(w * h / (long_side ** 2), 2), -err)
        if best is None or score > best[0]: best = (score, quad)
    if best is None: raise ValueError("rohové čtverce netvoří stránku A4")
    quad = best[1]
    if np.linalg.norm(quad[1] - quad[0]) > np.linalg.norm(quad[3] - quad[0]):
        quad = np.roll(quad, -1, axis=0)  # landscape photo: make tl->tr the short edge
    # the hollow one is top-left; rotate the order until it comes first
    holes = [hollow(grey, p, np.linalg.norm(quad[1] - quad[0]) / (pw - 20) * layout["fiducial_size"]) for p in quad]
    i = int(np.argmax(holes))
    quad = np.roll(quad, -i, axis=0)
    return quad, holes[i]


def square_blobs(mask, long_side):
    """solid, roughly square dark blobs: (area, cx, cy, w, h)"""
    bw = mask.astype(np.uint8) * 255
    # thin pencil lines touching a square would bend its outline: open them away first
    k = max(3, long_side // 250)
    bw = cv2.morphologyEx(bw, cv2.MORPH_CLOSE, cv2.getStructuringElement(cv2.MORPH_RECT, (k // 2 + 1, k // 2 + 1)))  # speckled toner
    bw = cv2.morphologyEx(bw, cv2.MORPH_OPEN, cv2.getStructuringElement(cv2.MORPH_RECT, (k, k)))
    # RETR_LIST: a dark table around a photographed sheet encloses the squares
    cnts, _ = cv2.findContours(bw, cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)
    out = []
    for c in cnts:
        area = cv2.contourArea(c)
        if area < (long_side / 400) ** 2 or area > (long_side / 10) ** 2: continue
        (cx, cy), (w, h), _ = cv2.minAreaRect(c)
        if min(w, h) == 0 or max(w, h) / min(w, h) > 1.3: continue
        if area / (w * h) < 0.85: continue
        # an empty box frame has a square outline too: the corner squares are solid ink
        x, y, bw_, bh_ = cv2.boundingRect(c)
        m = np.zeros((bh_, bw_), np.uint8); cv2.drawContours(m, [c - (x, y)], -1, 255, -1)
        if (bw[y:y + bh_, x:x + bw_][m > 0] > 0).mean() < 0.55: continue  # the hollow tl square is ~75 % ink
        out.append((area, cx, cy, w, h))
    return out


def order_quad(pts):
    c = pts.mean(axis=0)
    ang = np.arctan2(pts[:, 1] - c[1], pts[:, 0] - c[0])
    pts = pts[np.argsort(ang)]  # clockwise in image coords, starting near the left
    s = pts.sum(axis=1)
    return np.roll(pts, -int(np.argmin(s)), axis=0)


def hollow(grey, p, size):
    """how much brighter the centre of a square is than its body (the tl square has a white hole)"""
    x, y, r = int(p[0]), int(p[1]), max(2, int(size * 0.12))
    centre = grey[max(0, y - r):y + r, max(0, x - r):x + r].mean()
    o = int(size * 0.38)
    ring = np.mean([grey[y + dy - 1:y + dy + 2, x + dx - 1:x + dx + 2].mean() for dx, dy in ((o, 0), (-o, 0), (0, o), (0, -o))])
    return centre - ring


def warp_page(img, quad, layout, ppm):
    pw, ph = layout["page"]
    f = layout["fiducials"]
    dst = np.array([f["tl"], f["tr"], f["br"], f["bl"]], np.float32) * ppm
    H = cv2.getPerspectiveTransform(quad.astype(np.float32), dst)
    return cv2.warpPerspective(img, H, (int(pw * ppm), int(ph * ppm)), flags=cv2.INTER_CUBIC, borderValue=(255, 255, 255))


def read_qr(page, ppm):
    region = page[int(268 * ppm):int(294 * ppm), int(12 * ppm):int(42 * ppm)]
    det = cv2.QRCodeDetector()
    grey = cv2.cvtColor(region, cv2.COLOR_BGR2GRAY)
    # light toner leaves a soft, grey code: also try it sharpened into pure black and white
    big = cv2.resize(grey, None, fx=3, fy=3, interpolation=cv2.INTER_CUBIC)
    variants = [region, cv2.resize(region, None, fx=2, fy=2, interpolation=cv2.INTER_NEAREST)]
    for blur in (0, 3, 5):
        g = cv2.GaussianBlur(big, (blur * 2 + 1,) * 2, 0) if blur else big
        variants.append(cv2.threshold(g, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)[1])
    variants.append(page)
    for im in variants:
        txt, _, _ = det.detectAndDecode(im)
        if txt.startswith("VMD-STYL|"):
            _, ver, num, code = txt.split("|")
            return int(ver[1:]), int(num), code
    return None


class PdfMatcher:
    """the printed PDF as reference: identifies a page without its QR, and says where its guides were printed"""
    def __init__(self, pdf, layout):
        self.refs, self.doc, self.masks = [], None, {}
        if not pdf or not os.path.exists(pdf): return
        self.doc = pymupdf.open(pdf)
        for i, p in enumerate(self.doc):
            pix = p.get_pixmap(dpi=40, colorspace=pymupdf.csGRAY)
            self.refs.append(np.frombuffer(pix.samples, np.uint8).reshape(pix.height, pix.width).astype(np.float32))

    def match(self, page):
        if not self.refs: return None, 0
        g = cv2.cvtColor(page, cv2.COLOR_BGR2GRAY)
        g = cv2.resize(g, self.refs[0].shape[::-1], interpolation=cv2.INTER_AREA).astype(np.float32)
        scores = [float(cv2.matchTemplate(g, r, cv2.TM_CCOEFF_NORMED)[0, 0]) for r in self.refs]
        i = int(np.argmax(scores))
        return i, scores[i]

    def guide_mask(self, num, ppm, shape):
        """(pixels near a printed guide, widened to absorb registration error; the guide pixels themselves),
        or (None, None) without the PDF"""
        if self.doc is None: return None, None
        if (num, ppm) not in self.masks:
            pix = self.doc[num].get_pixmap(matrix=pymupdf.Matrix(ppm / 72 * 25.4, ppm / 72 * 25.4))
            ref = np.frombuffer(pix.samples, np.uint8).reshape(pix.height, pix.width, pix.n)[:, :, :3]
            ref = cv2.resize(ref, (shape[1], shape[0]), interpolation=cv2.INTER_NEAREST)
            hsv = cv2.cvtColor(ref, cv2.COLOR_RGB2HSV)
            m = ((hsv[:, :, 0] >= 85) & (hsv[:, :, 0] <= 110) & (hsv[:, :, 1] >= 30)).astype(np.uint8) * 255
            r = max(2, int(ppm * 0.8))
            self.masks[(num, ppm)] = (cv2.dilate(m, cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (2 * r + 1, 2 * r + 1))), m)
        return self.masks[(num, ppm)]


# ------------------------------------------------------------------ cleaning
def white_balance(page):
    """scale each channel so the paper comes out white, whatever the lamp or scanner tint"""
    h, w = page.shape[:2]
    body = page[h // 8:h * 7 // 8, w // 8:w * 7 // 8].reshape(-1, 3).astype(np.float32)
    paper = np.percentile(body, 95, axis=0)
    return np.clip(page.astype(np.float32) * (250.0 / np.maximum(paper, 30)), 0, 255).astype(np.uint8)


def guide_cut(page, core, ppm):
    """grey level that separates the printed guides from drawing on this page: just darker than the guides'
    own tone (a laser printer's grey is toner dots, so it is measured on a blurred copy)"""
    grey = cv2.cvtColor(page, cv2.COLOR_BGR2GRAY)
    paper = paper_level(grey)
    if core is None or not core.any(): return paper * 0.76
    k = max(3, int(ppm * 0.6) | 1)
    # upper quartile: where someone traced over a guide its pixels read as pencil, the untouched rest as guide
    tone = float(np.percentile(cv2.GaussianBlur(grey, (k, k), 0)[core > 0], 75))
    return float(np.clip(tone - paper * 0.1, paper * 0.6, paper * 0.85))


def drop_guides(crop, printed=None, ppm=12, cut=None):
    """remove the printed guides (cyan, or light grey from a B&W printer) and repair the drawing across them.
    Pencil crossing a guide is darker than the guide, so it stays; the gaps it leaves are inpainted."""
    hsv = cv2.cvtColor(crop, cv2.COLOR_BGR2HSV)
    h, s, v = hsv[:, :, 0], hsv[:, :, 1], hsv[:, :, 2]
    cyan = ((h >= 80) & (h <= 115) & (s >= 25) & (v >= 120)).astype(np.uint8) * 255
    cyan = cv2.dilate(cyan, np.ones((3, 3), np.uint8))
    grey = cv2.cvtColor(crop, cv2.COLOR_BGR2GRAY)
    paper = paper_level(grey)
    zone = cyan | printed if printed is not None else cyan.copy()
    # a colour print: whatever is still cyan goes, unless dark ink lies on it
    mask = cyan & (grey >= paper * 0.6).astype(np.uint8) * 255
    if printed is not None:
        # a B&W print: judge on a blurred copy, where toner dots of a guide average out light
        # and a pencil stroke stays dark
        k = max(3, int(ppm * 0.6) | 1)
        soft = cv2.GaussianBlur(grey, (k, k), 0)
        mask |= printed & (soft >= (cut if cut is not None else paper * 0.76)).astype(np.uint8) * 255
    # clumps of toner dots read dark even blurred; a small dark speck lying inside the guide zone is guide too,
    # while a pencil stroke crossing the guide runs on beyond it
    dark = (grey < paper * 0.85).astype(np.uint8)
    n, lab, stats, _ = cv2.connectedComponentsWithStats(dark, connectivity=8)
    if n > 1:
        inside = np.bincount(lab[zone > 0].ravel(), minlength=n)
        area = stats[:, cv2.CC_STAT_AREA]
        tone = np.bincount(lab.ravel(), weights=grey.ravel().astype(np.float64), minlength=n) / np.maximum(area, 1)
        # flat mid-grey (an inkjet's grey guide or hint letter) may be a little bigger than a toner clump
        small = ((area < (0.7 * ppm) ** 2) | ((area < (1.1 * ppm) ** 2) & (tone >= paper * 0.72))) & (inside >= area * 0.8)
        small[0] = False
        grow = cv2.dilate(np.isin(lab, np.where(small)[0]).astype(np.uint8) * 255, np.ones((3, 3), np.uint8))
        mask |= grow
    out = cv2.inpaint(crop, mask, max(2, int(ppm * 0.3)), cv2.INPAINT_TELEA) if mask.any() else crop.copy()
    return despeckle(out, ppm)


def despeckle(crop, ppm):
    """drop isolated dots: halftone left-overs from a laser-printed grey, dust on the scanner glass"""
    grey = cv2.cvtColor(crop, cv2.COLOR_BGR2GRAY)
    paper = paper_level(grey)
    dark = (grey < paper * 0.85).astype(np.uint8)
    n, lab, stats, _ = cv2.connectedComponentsWithStats(dark, connectivity=8)
    small = np.isin(lab, np.where(stats[:, cv2.CC_STAT_AREA] < (0.45 * ppm) ** 2)[0][1:])
    if not small.any(): return crop
    out = crop.copy()
    rest = crop[(dark == 0)]
    out[small] = np.median(rest, axis=0) if len(rest) else (255, 255, 255)
    return out


def paper_level(grey):
    return float(np.percentile(grey, 90))


def ink_alpha(crop):
    """ink as alpha, stretched so the darkest stroke in the box is opaque: pencil comes out as solid as pen,
    while its grain stays in the alpha"""
    grey = cv2.cvtColor(crop, cv2.COLOR_BGR2GRAY).astype(np.float32)
    paper = max(paper_level(grey), 60.0)
    darkest = min(float(np.percentile(grey, 0.5)), paper - 80)
    a = np.clip((paper - 10 - grey) / max(paper - 10 - darkest, 1) * 255, 0, 255)
    return a.astype(np.uint8)


def coverage(crop, kind):
    if kind in COLOUR_KINDS:
        lab = cv2.cvtColor(crop, cv2.COLOR_BGR2LAB).astype(np.float32)
        ref = np.median(lab.reshape(-1, 3), axis=0) if kind != "swatch" else np.array([250, 128, 128], np.float32)
        paper = np.array([max(ref[0], 200), 128, 128], np.float32) if kind == "swatch" else ref
        d = np.linalg.norm(lab - paper, axis=2)
        return float((d > 25).mean())
    grey = cv2.cvtColor(crop, cv2.COLOR_BGR2GRAY).astype(np.float32)
    return float((grey < paper_level(grey) * 0.75).mean())


# ------------------------------------------------------------------ colour
def print_mode(page, cal, ppm):
    """'colour' when the calibration strip's colour patches came out coloured, else 'bw' (B&W printer)"""
    x, y, w, h = cal["x"], cal["y"], cal["w"], cal["h"]
    pw = w / len(cal["patches"])
    sats = []
    for i, rgb in enumerate(cal["patches"]):
        if len(set(rgb)) == 1: continue
        patch = page[int((y + h * 0.25) * ppm):int((y + h * 0.75) * ppm), int((x + i * pw + pw * 0.25) * ppm):int((x + i * pw + pw * 0.75) * ppm)]
        sats.append(np.median(cv2.cvtColor(patch, cv2.COLOR_BGR2HSV)[:, :, 1]))
    return "colour" if np.mean(sats) > 60 else "bw"


def colour_fix(page, cal, ppm, mode):
    """per-channel curve that makes the paper white and, on a colour print, the grey ramp neutral.
    A B&W laser print's greys are halftone guesses, so there only the paper counts."""
    x, y, w, h = cal["x"], cal["y"], cal["w"], cal["h"]
    n = len(cal["patches"]); pw = w / n
    meas, ref = [], []
    for i, rgb in enumerate(cal["patches"]):
        if len(set(rgb)) != 1: continue
        if mode == "bw" and rgb[0] < 1: continue
        cx0, cx1 = int((x + i * pw + pw * 0.25) * ppm), int((x + i * pw + pw * 0.75) * ppm)
        cy0, cy1 = int((y + h * 0.25) * ppm), int((y + h * 0.75) * ppm)
        meas.append(np.median(page[cy0:cy1, cx0:cx1].reshape(-1, 3), axis=0)[::-1])
        ref.append(rgb[0] * 255)
    meas.append(np.zeros(3)); ref.append(0.0)
    meas, ref = np.array(meas), np.array(ref)
    curves = []
    for ch in range(3):
        order = np.argsort(meas[:, ch])
        xs, ys = meas[order, ch], ref[order]
        keep = np.concatenate([[True], np.diff(ys) > 0])  # the curve must climb, or interp folds back
        curves.append((xs[keep].tolist(), ys[keep].tolist()))
    return curves


def apply_fix(rgb, curves):
    return [float(np.clip(np.interp(rgb[i], *curves[i]), 0, 255)) for i in range(3)]


def swatch_colour(crop):
    """the crayon's own colour (median of the densest quarter of strokes) and the coloured-in look
    (median of everything that isn't bare paper). Crayon leaves white gaps, so the two differ a lot."""
    lab = cv2.cvtColor(crop, cv2.COLOR_BGR2LAB).astype(np.float32)
    flat = lab.reshape(-1, 3)
    paper = np.array([np.percentile(flat[:, 0], 98), 128, 128])
    d = np.linalg.norm(flat - paper, axis=1)
    coloured = d > 20
    if coloured.sum() < 50: return None, None, 0.0
    rgb = crop.reshape(-1, 3)[:, ::-1]
    dense = coloured & (d >= np.percentile(d[coloured], 75))
    return np.median(rgb[dense], axis=0), np.median(rgb[coloured], axis=0), float(coloured.mean())


def hexcol(rgb): return "#%02x%02x%02x" % tuple(int(round(c)) for c in rgb)


# ------------------------------------------------------------------ main
def process(name, img, layout, pages_by_num, matcher, out_dir, seen):
    rec = dict(source=name, warnings=[])
    quad, hole = find_fiducials(img, layout)
    side = np.linalg.norm(quad[3] - quad[0]) / (layout["fiducials"]["bl"][1] - layout["fiducials"]["tl"][1])
    ppm = float(np.clip(round(side), 8, 24))
    rec["px_per_mm"] = ppm
    rec["scan_dpi"] = round(side * 25.4)
    if rec["scan_dpi"] < 250: rec["warnings"].append(f"nízké rozlišení ({rec['scan_dpi']} DPI), ideálně 300–600")
    if hole < 40: rec["warnings"].append("nejistý levý horní roh – zkontroluj natočení v náhledu")
    page = white_balance(warp_page(img, quad, layout, ppm))
    qr = read_qr(page, ppm)
    if qr:
        ver, num, code = qr
        rec["identified_by"] = "qr"
        if ver != layout["version"]: rec["warnings"].append(f"list je verze v{ver}, layout v{layout['version']}")
    else:
        num, score = matcher.match(page)
        if num is None or score < 0.45: raise ValueError("nepřečetl jsem QR kód ani nepoznal list")
        code = pages_by_num[num]["code"]
        rec["identified_by"] = f"pdf ({score:.2f})"
        rec["warnings"].append("QR nepřečten, list poznán podle vzhledu")
    lp = pages_by_num[num]
    seen[code] = seen.get(code, 0) + 1
    suffix = "" if seen[code] == 1 else f"_{seen[code]}"
    folder = os.path.join(out_dir, code + suffix)
    os.makedirs(folder, exist_ok=True)
    rec.update(page=num, code=code, copy=seen[code], folder=os.path.relpath(folder, out_dir), boxes=[])

    preview = page.copy()
    printed, core = matcher.guide_mask(num, ppm, page.shape)
    cut = guide_cut(page, core, ppm)
    rec["guide_cut"] = round(cut / paper_level(cv2.cvtColor(page, cv2.COLOR_BGR2GRAY)), 3)
    if printed is None: rec["warnings"].append("chybí PDF listů – vodítka mažu jen podle barvy")
    for b in lp["boxes"]:
        x0, y0 = int((b["x"] + INSET_MM) * ppm), int((b["y"] + INSET_MM) * ppm)
        x1, y1 = int((b["x"] + b["w"] - INSET_MM) * ppm), int((b["y"] + b["h"] - INSET_MM) * ppm)
        crop = page[y0:y1, x0:x1]
        if b["kind"] not in COLOUR_KINDS: crop = drop_guides(crop, None if printed is None else printed[y0:y1, x0:x1], ppm, cut)
        probe = crop.copy()
        for ix, iy, iw, ih in b.get("ignore", []):
            probe[max(0, int((iy - b["y"] - INSET_MM) * ppm)):int((iy + ih - b["y"] - INSET_MM) * ppm),
                  max(0, int((ix - b["x"] - INSET_MM) * ppm)):int((ix + iw - b["x"] - INSET_MM) * ppm)] = 255
        cov = coverage(probe, b["kind"])
        entry = {k: v for k, v in b.items() if k not in ("x", "y", "w", "h", "ignore")}
        entry.update(coverage=round(cov, 4), empty=cov < EMPTY_BELOW, png=os.path.join(rec["folder"], b["id"] + ".png"))
        cv2.imwrite(os.path.join(folder, b["id"] + ".png"), crop)
        if b["kind"] in INK_KINDS:
            rgba = np.dstack([np.zeros_like(crop[:, :, 0])] * 3 + [ink_alpha(crop)])
            cv2.imwrite(os.path.join(folder, b["id"] + "_ink.png"), rgba)
            entry["ink"] = os.path.join(rec["folder"], b["id"] + "_ink.png")
        rec["boxes"].append(entry)
        cv2.rectangle(preview, (x0, y0), (x1, y1), (0, 0, 220) if entry["empty"] else (0, 170, 0), max(2, int(ppm / 3)))
    if "calibration" in lp:
        rec["print"] = print_mode(page, lp["calibration"], ppm)
        rec["calibration"] = colour_fix(page, lp["calibration"], ppm, rec["print"])
    cv2.imwrite(os.path.join(folder, "_nahled.png"), cv2.resize(preview, None, fx=4 / ppm, fy=4 / ppm, interpolation=cv2.INTER_AREA))
    rec["_page"] = page
    return rec


def build_palette(rec, out_dir):
    curves = rec.pop("calibration")
    out = []
    for b in rec["boxes"]:
        if b["kind"] != "swatch": continue
        crop = cv2.imread(os.path.join(out_dir, b["png"]))
        dense, look, cov = swatch_colour(crop)
        if dense is None:
            out.append(dict(id=b["id"], target=b["target"], empty=True)); continue
        out.append(dict(id=b["id"], target=b["target"], hex=hexcol(apply_fix(dense, curves)),
                        look_hex=hexcol(apply_fix(look, curves)), raw_hex=hexcol(dense), filled=round(cov, 3)))
    return dict(print=rec["print"], swatches=out)


def palette_sheet(palette, path):
    """the swatches side by side: crayon colour, coloured-in look, name"""
    from PIL import Image, ImageDraw, ImageFont
    font = ImageFont.truetype(os.path.join(os.path.dirname(os.path.abspath(__file__)), "fonts", "ComicNeue-Regular.ttf"), 22)
    rows = palette["swatches"]
    im = Image.new("RGB", (900, 60 + 56 * len(rows)), "white"); d = ImageDraw.Draw(im)
    d.text((20, 15), f"tisk: {palette['print']}   ·   barva pastelky   ·   jak vypadá vybarvené", fill="black", font=font)
    for i, r in enumerate(rows):
        y = 60 + i * 56
        if r.get("empty"): d.text((300, y + 12), f"(prázdné)  {r['target']}", fill="grey", font=font); continue
        d.rectangle([20, y, 140, y + 46], fill=r["hex"]); d.rectangle([150, y, 270, y + 46], fill=r["look_hex"])
        d.text((290, y + 10), f"{r['target']}   {r['hex']}", fill="black", font=font)
    im.save(path)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("scan_dir", nargs="?", default=os.path.join(VAULT, "skeny"))
    ap.add_argument("out_dir", nargs="?", default=os.path.join(VAULT, "vystup"))
    ap.add_argument("--layout", default=os.path.join(VAULT, "styl_listy_layout.json"))
    ap.add_argument("--pdf", default=os.path.join(VAULT, "styl_listy.pdf"))
    a = ap.parse_args()
    layout = json.load(open(a.layout))
    pages_by_num = {p["num"]: p for p in layout["pages"]}
    matcher = PdfMatcher(a.pdf, layout)
    os.makedirs(a.out_dir, exist_ok=True)
    manifest, seen, palette = dict(layout_version=layout["version"], scans=[], failed=[]), {}, None
    for name, img in load_scans(a.scan_dir):
        try:
            rec = process(name, img, layout, pages_by_num, matcher, a.out_dir, seen)
        except Exception as e:
            manifest["failed"].append(dict(source=name, error=str(e)))
            print(f"✗ {name}: {e}")
            continue
        rec.pop("_page")
        if "calibration" in rec: palette = build_palette(rec, a.out_dir)
        empty = sum(b["empty"] for b in rec["boxes"])
        print(f"✓ {name} → {rec['page']:02d} {rec['code']} ({rec['identified_by']}, {rec['scan_dpi']} DPI), "
              f"{len(rec['boxes']) - empty}/{len(rec['boxes'])} vyplněno" + "".join(f"\n    ! {w}" for w in rec["warnings"]))
        manifest["scans"].append(rec)
    got = {s["code"] for s in manifest["scans"]}
    manifest["missing_pages"] = [p["code"] for p in layout["pages"] if p["num"] > 0 and p["code"] not in got]
    with open(os.path.join(a.out_dir, "manifest.json"), "w") as f: json.dump(manifest, f, ensure_ascii=False, indent=1)
    if palette is not None:
        with open(os.path.join(a.out_dir, "palette.json"), "w") as f: json.dump(palette, f, ensure_ascii=False, indent=1)
        palette_sheet(palette, os.path.join(a.out_dir, "palette.png"))
    if manifest["missing_pages"]: print("chybí listy:", ", ".join(manifest["missing_pages"]))
    print("výstup:", a.out_dir)
    return 1 if manifest["failed"] else 0


if __name__ == "__main__":
    sys.exit(main())
