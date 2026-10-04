"""The family's personal style ("osobni"), built by build_style.py from the scanned style sheets.

On by default since 2026-10-03 (game and comic). The previous look is one switch away:
    VMD_STYLE=puvodni .venv/bin/python export_assets.py
When on: palette.py takes the girls' crayon colours, style3.stroke() draws with táta's measured line,
hatch() with his hatching, face() with his expressions, and letter.py letters in his handwriting.
Must not import palette or style3 (both import this).
"""
import os, json, math

HERE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(HERE, "style_data")
ACTIVE = os.environ.get("VMD_STYLE", "osobni") == "osobni"
# which parts are on (all by default); e.g. VMD_STYLE_PARTS=faces,palette to compare one at a time
ALL_PARTS = ("lines", "hatch", "faces", "palette", "font", "crayon", "pencil", "paper", "balloons", "wallart",
             "lettering")
PARTS = set(os.environ.get("VMD_STYLE_PARTS", ",".join(ALL_PARTS)).split(",")) if ACTIVE else set()


def on(part): return part in PARTS
PT_PER_MM = 72 / 25.4


def _load(name):
    path = os.path.join(DATA, name)
    if not os.path.exists(path):
        raise SystemExit(f"VMD_STYLE=osobni, ale chybí {path} – spusť nejdřív build_style.py")
    with open(path, encoding="utf-8") as f: return json.load(f)


LINES = _load("lines.json") if ACTIVE else None
FACES = _load("faces.json") if ACTIVE else None
PALETTE = _load("palette.json") if ACTIVE else None
BALLOONS = _load("balloons.json") if ACTIVE else None

# the expression drawn for each mood the code asks for; moods without their own drawing borrow the nearest
FACE_FOR = {"happy": "happy", "calm": "happy", "grin": "grin", "laugh": "grin", "surprised": "surprised",
            "wow": "wow", "think": "think", "worried": "worried", "sad": "sad", "whisper": "whisper",
            "determined": "determined", "sleepy": "sleepy", "closed": "sleepy", "talk": "surprised"}


def palette_overrides():
    return PALETTE["overrides"] if on("palette") else {}


def stroke_params():
    """wobble/pressure in page pt, from táta's lines. The comic is printed about at the size he drew, so mm map
    to pt one to one; only the pressure swing is damped, because part of a pencil line's width noise is grain."""
    L = LINES
    p1, p2 = L["wobble_periods_mm"]; w1, w2 = L["wobble_weights"]
    period = max(p1, p2) * PT_PER_MM
    freqs = ((1.0, w1 if p1 >= p2 else w2), (max(p1, p2) / min(p1, p2), w2 if p1 >= p2 else w1))
    rms_unit = math.sqrt(sum(a * a for _, a in freqs) / 2)
    return dict(
        wob_amp=L["wobble_mm"] * PT_PER_MM / rms_unit,
        wob_freqs=freqs, wob_period=period,
        bow=L["bow_per_len"],
        prs_amp=min(0.5, L["pressure_cv"] * 0.7 / 0.54),
        taper_floor=min(0.9, max(0.25, L["end_width_ratio"] * 0.8)),
        width_k=max(0.85, min(1.25, L["width_mm"] * PT_PER_MM / 1.15)))


def hatch_params():
    h = LINES["hatch"]
    return dict(spacing_k=max(1.0, min(2.2, h["spacing_mm"] * PT_PER_MM / 1.6)),
                end_heavy=h.get("end_weight", 1.0) > 1.3)


def font_path(name): return os.path.join(HERE, "fonts", name)


# ------------------------------------------------------------------ materials
TEX = os.path.join(DATA, "textures")
CACHE = os.path.join(DATA, "cache")
TILE_MM = 34.0   # a texture tile covers this much of the page, about the size the girls coloured it
TILE_PX_BW = 192  # pencil tiles in the B&W comic are downsized to this


def _textures(kind):
    return sorted(os.path.join(TEX, f) for f in os.listdir(TEX) if f.startswith(kind)) if os.path.isdir(TEX) else []


def crayon_tile(rgb, key, bw=False):
    """RGBA tile: the colour laid down with a real crayon (or pencil, for the B&W comic), transparent in the gaps.
    `key` picks one of the scanned colourings, so neighbouring areas don't share the same strokes."""
    from PIL import Image
    tex = _textures("pencil" if bw else "crayon")
    if not tex: return None
    src = tex[key % len(tex)]
    hexs = "%02x%02x%02x" % tuple(int(round(c * 255)) for c in rgb)
    # the B&W comic draws hundreds of tiles a page, and PDF viewers pay for every pixel of every soft mask:
    # at full size a page took seconds to show. Half size (~140 ppi) still prints as pencil grain.
    px = TILE_PX_BW if bw else None
    path = os.path.join(CACHE, f"{os.path.basename(src)[:-4]}_{hexs}{f'_{px}' if px else ''}.png")
    if not os.path.exists(path):
        os.makedirs(CACHE, exist_ok=True)
        a = Image.open(src).convert("L")
        if px: a = a.resize((px, px), Image.LANCZOS)
        im = Image.new("RGBA", a.size, tuple(int(round(c * 255)) for c in rgb) + (0,)); im.putalpha(a)
        tmp = f"{path}.{os.getpid()}.tmp"  # several builds may run at once: never let one read a half-written tile
        im.save(tmp, format="PNG"); os.replace(tmp, path)
    return path


def paper(png_path, strength=0.22):
    """press the scanned paper grain into a finished picture (rooms; characters sit on them)"""
    from PIL import Image, ImageChops
    src = os.path.join(TEX, "paper.png")
    if not on("paper") or not os.path.exists(src): return
    im = Image.open(png_path); mode = im.mode
    rgb = im.convert("RGB")
    g = Image.open(src).convert("L")
    tiled = Image.new("L", rgb.size)
    for y in range(0, rgb.size[1], g.size[1]):
        for x in range(0, rgb.size[0], g.size[0]): tiled.paste(g, (x, y))
    # grain around mid-grey: darker specks multiply in, lighter ones lift a little
    lut = [max(0, min(255, int(255 - (128 - v) * strength * 2))) if v < 128 else 255 for v in range(256)]
    out = ImageChops.multiply(rgb, Image.merge("RGB", [tiled.point(lut)] * 3))
    if mode == "RGBA": out.putalpha(im.getchannel("A"))
    out.save(png_path)


# ------------------------------------------------------------------ balloons
def balloon_outline(kind, cx, cy, rx, ry, n=None):
    """táta's balloon shape (speech, thought, shout, whisper) stretched over the ellipse rx, ry; None if off"""
    if not on("balloons") or kind not in BALLOONS: return None
    prof = BALLOONS[kind]["profile"]
    if kind == "shout": prof = [1 + (k - 1) * 1.6 for k in prof]  # his spikes, a bit bolder at comic size
    n = n or len(prof)
    pts = []
    for j in range(n):  # parametric angle from 0, counter-clockwise, like letter.wobbly_ellipse
        t = 2 * math.pi * j / n
        k = prof[int(((t + math.pi) / (2 * math.pi)) * len(prof)) % len(prof)]
        pts.append((cx + math.cos(t) * rx * k, cy + math.sin(t) * ry * k))
    return pts


def whisper_dashes():
    w = BALLOONS.get("whisper", {}) if on("balloons") else {}
    return (w["dash_mm"] * PT_PER_MM, w["dash_cv"], w["gap_mm"] * PT_PER_MM) if "dash_mm" in w else None


def frame_overshoot():
    f = BALLOONS.get("frame") if on("balloons") else None
    return (f["overshoot_mm"] * PT_PER_MM, f["overshoot_max_mm"] * PT_PER_MM) if f else None


# ------------------------------------------------------------------ titles and sound words
# táta's hand-drawn block letters from the "Zvuky a nadpisy" sheet (scan_sheets.p_zvuky); stamp = zvuky_<crc of word>
SOUND_WORDS = ["BUM!", "PRÁSK!", "ŤUK ŤUK", "ČMUCH ČMUCH!", "HAF! HAF!", "MŇAU", "ŠUST ŠUST", "CVAK!", "ŽBLUŇK!",
               "CHRRR…", "HURÁ!", "KONEC"]


def _letters(txt): return "".join(ch for ch in txt.upper() if ch.isalpha() or ch == " ").split()


def sound_stamp(txt):
    """the stamp táta drew for this word (punctuation may differ), or None"""
    if not on("lettering"): return None
    import zlib
    for w in SOUND_WORDS:
        if _letters(w) == _letters(txt):
            path = os.path.join(DATA, "stamps", f"zvuky_{zlib.crc32(w.encode()) & 0xffff:04x}.png")
            return path if os.path.exists(path) else None
    return None


def title_stamp():
    path = os.path.join(DATA, "stamps", "zvuky_nadpis.png")
    return path if on("lettering") and os.path.exists(path) else None


def filled_stamp(path, rgb, shadow=False):
    """outline lettering made solid: inside the letters `rgb`, the pencil outline on top; outside transparent.
    shadow=True gives the whole silhouette in one flat grey, for a drop shadow."""
    import numpy as np, cv2
    from PIL import Image
    hexs = "%02x%02x%02x" % tuple(int(round(c * 255)) for c in rgb)
    out = os.path.join(CACHE, f"{os.path.basename(path)[:-4]}_{'shadow' if shadow else hexs}.png")
    if os.path.exists(out): return out
    # pressed harder: a light pencil outline goes grey and fuzzy at comic size
    a = np.clip(np.array(Image.open(path).getchannel("A")).astype(np.float32) * 1.8, 0, 255).astype(np.uint8)
    # close the gaps a pencil line leaves, then everything the outside can't reach is inside a letter
    ink = cv2.morphologyEx((a > 50).astype(np.uint8), cv2.MORPH_CLOSE, cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (15, 15)))
    ink = cv2.dilate(ink, np.ones((3, 3), np.uint8))
    ink = cv2.copyMakeBorder(ink, 1, 1, 1, 1, cv2.BORDER_CONSTANT, value=0)
    mask = np.zeros((ink.shape[0] + 2, ink.shape[1] + 2), np.uint8)
    flood = ink.copy(); cv2.floodFill(flood, mask, (0, 0), 2)
    inside = (flood[1:-1, 1:-1] != 2).astype(np.float32)
    ak = a.astype(np.float32) / 255
    if shadow:
        rgba = np.dstack([np.full_like(a, 110)] * 3 + [np.maximum(inside * 255, a).astype(np.uint8)])
    else:
        col = np.array([c * 255 for c in rgb], np.float32)
        px = col * (1 - ak[..., None])  # the outline is black ink over the fill
        rgba = np.dstack([px.astype(np.uint8), np.maximum(inside * 255, a).astype(np.uint8)])
    os.makedirs(CACHE, exist_ok=True)
    tmp = f"{out}.{os.getpid()}.tmp.png"
    Image.fromarray(rgba, "RGBA").save(tmp); os.replace(tmp, out)
    return out


# ------------------------------------------------------------------ the girls' drawings on the walls
# room -> (drawing in style_data/stamps, x, y of the sheet's centre as a fraction of the room, sheet width pt)
WALL_ART = {
    "pokojicek": [("alica_joey", 0.63, 0.63, 104), ("hanka_slunce", 0.40, 0.55, 80), ("alica_ja", 0.505, 0.67, 70),
                  ("hanka_hlavonozec", 0.735, 0.52, 80), ("alica_hanka", 0.29, 0.52, 74)],
    "kuchyne": [("hanka_kytka", 0.225, 0.66, 74), ("alica_rodice", 0.315, 0.72, 86), ("hanka_srdce", 0.705, 0.79, 64),
                ("alica_joey", 0.80, 0.78, 80)],
    "kulna": [("hanka_opicka", 0.40, 0.56, 84)],
}


def wall_art(room):
    if not on("wallart"): return []
    out = []
    for name, x, y, w in WALL_ART.get(room, []):
        path = os.path.join(DATA, "stamps", name + ".png")
        if os.path.exists(path): out.append((path, x, y, w))
    return out
