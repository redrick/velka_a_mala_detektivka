"""Self-test for scan_reader.py: fake scans from the printable PDF, read them back, check the results.

Usage:  python scan_selftest.py <work_dir> [--pdf styl_listy.pdf --layout styl_listy_layout.json]
Draws ink in some boxes and colour in the swatches, then tilts, warps, flips, tints and blurs the pages like a
scanner or phone would. Exits non-zero when a page is misread, a box is misjudged or a colour is off.
"""
import os, sys, json, subprocess, argparse, random
import numpy as np
import cv2
import pymupdf

HERE = os.path.dirname(os.path.abspath(__file__))
VAULT = os.path.expanduser("~/SynologyDrive/redrick-obsidian/ai-memory/velka_a_mala_detektivka/topics/styl")
SWATCH_RGB = [(220, 40, 40), (40, 90, 200), (250, 210, 30), (60, 160, 60), (140, 70, 160)]


def render(pdf, num, dpi):
    pix = pymupdf.open(pdf)[num].get_pixmap(dpi=dpi)
    img = np.frombuffer(pix.samples, np.uint8).reshape(pix.height, pix.width, pix.n)[:, :, :3]
    return cv2.cvtColor(img, cv2.COLOR_RGB2BGR).copy()


def scribble(img, b, ppm, rnd):
    x0, y0, w, h = [v * ppm for v in (b["x"], b["y"], b["w"], b["h"])]
    pts = [(int(x0 + w * rnd.uniform(0.15, 0.85)), int(y0 + h * rnd.uniform(0.15, 0.85))) for _ in range(6)]
    cv2.polylines(img, [np.array(pts, np.int32)], False, (25, 25, 25), max(2, int(ppm * 0.4)), cv2.LINE_AA)


def colour_box(img, b, ppm, bgr):
    x0, y0, w, h = [int(v * ppm) for v in (b["x"], b["y"], b["w"], b["h"])]
    cv2.rectangle(img, (x0 + int(2 * ppm), y0 + int(2 * ppm)), (x0 + w - int(2 * ppm), y0 + h - int(2 * ppm)), bgr, -1)


def distort(img, kind, rnd):
    h, w = img.shape[:2]
    if kind == "flip":
        img = cv2.rotate(img, cv2.ROTATE_180)
    if kind in ("tilt", "flip", "tint", "bw"):
        M = cv2.getRotationMatrix2D((w / 2, h / 2), rnd.uniform(-3, 3), 0.97)
        img = cv2.warpAffine(img, M, (w, h), borderValue=(250, 250, 250))
    if kind == "phone":
        canvas = np.full((int(h * 1.25), int(w * 1.3), 3), (90, 110, 130), np.uint8)
        src = np.float32([[0, 0], [w, 0], [w, h], [0, h]])
        cw, ch = canvas.shape[1], canvas.shape[0]
        dst = np.float32([[cw * 0.12, ch * 0.06], [cw * 0.86, ch * 0.1], [cw * 0.9, ch * 0.93], [cw * 0.08, ch * 0.9]])
        H = cv2.getPerspectiveTransform(src, dst)
        img = cv2.warpPerspective(img, H, (cw, ch), dst=canvas, borderMode=cv2.BORDER_TRANSPARENT)
        img = cv2.rotate(img, cv2.ROTATE_90_CLOCKWISE)
    if kind in ("tint", "phone"):
        img = np.clip(img.astype(np.float32) * np.array([0.88, 0.95, 1.04]) + np.array([4, 0, -6]), 0, 255).astype(np.uint8)
    img = cv2.GaussianBlur(img, (3, 3), 0)
    noise = np.random.default_rng(1).normal(0, 3, img.shape)
    return np.clip(img + noise, 0, 255).astype(np.uint8)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("work_dir")
    ap.add_argument("--pdf", default=os.path.join(VAULT, "styl_listy.pdf"))
    ap.add_argument("--layout", default=os.path.join(VAULT, "styl_listy_layout.json"))
    a = ap.parse_args()
    layout = json.load(open(a.layout))
    scans, out = os.path.join(a.work_dir, "skeny"), os.path.join(a.work_dir, "vystup")
    os.makedirs(scans, exist_ok=True)
    for f in os.listdir(scans): os.remove(os.path.join(scans, f))
    rnd = random.Random(3)
    # bw = printed on a B&W printer: guides and calibration come out grey, only what the kids colour is in colour
    plan = {1: ("tilt", 300), 6: ("flip", 300), 9: ("phone", 200), 10: ("bw", 300), 15: ("tint", 300), 16: ("tilt", 600), 19: ("tilt", 300)}
    bw_pages = {10, 15}
    expect = {}
    pdf_pages = []
    for num, (kind, dpi) in plan.items():
        page = layout["pages"][num]
        ppm = dpi / 25.4
        img = render(a.pdf, num, dpi)
        if num in bw_pages: img = cv2.cvtColor(cv2.cvtColor(img, cv2.COLOR_BGR2GRAY), cv2.COLOR_GRAY2BGR)
        filled = set()
        for i, b in enumerate(page["boxes"]):
            if b["kind"] == "swatch":
                if i < len(SWATCH_RGB):
                    colour_box(img, b, ppm, SWATCH_RGB[i][::-1]); filled.add(b["id"])
            elif i % 3 == 0:
                scribble(img, b, ppm, rnd); filled.add(b["id"])
        expect[page["code"]] = filled
        img = distort(img, kind, rnd)
        if num == 19: pdf_pages.append(img)
        else: cv2.imwrite(os.path.join(scans, f"scan_{num:02d}_{kind}.{'jpg' if kind == 'phone' else 'png'}"), img)
    doc = pymupdf.open()
    for img in pdf_pages:
        ok, buf = cv2.imencode(".png", img)
        p = doc.new_page(width=595, height=842); p.insert_image(p.rect, stream=buf.tobytes())
    doc.save(os.path.join(scans, "multi.pdf"))

    r = subprocess.run([sys.executable, os.path.join(HERE, "scan_reader.py"), scans, out, "--layout", a.layout, "--pdf", a.pdf])
    man = json.load(open(os.path.join(out, "manifest.json")))
    errors = [f"selhal: {f['source']}: {f['error']}" for f in man["failed"]]
    got = {s["code"]: s for s in man["scans"]}
    for code, filled in expect.items():
        if code not in got: errors.append(f"list {code} nepřečten"); continue
        for b in got[code]["boxes"]:
            if (b["id"] in filled) == b["empty"]:
                errors.append(f"{code}/{b['id']}: čekal jsem {'vyplněno' if b['id'] in filled else 'prázdno'}, coverage {b['coverage']}")
    # empty boxes that had printed guides must come out blank once the guides are dropped
    for code in ("cary", "obliceje", "pismo_velka", "pismo_mala"):
        for b in got.get(code, {}).get("boxes", []):
            if b["id"] in expect[code]: continue
            crop = cv2.imread(os.path.join(out, b["png"]))
            left = float((crop.min(axis=2) < 200).mean())
            if left > 0.002: errors.append(f"{code}/{b['id']}: po smazání vodítek zbylo {left:.2%} pixelů")
    palette = json.load(open(os.path.join(out, "palette.json")))
    if palette["print"] != "bw": errors.append(f"barvy: tisk poznán jako {palette['print']}, má být bw")
    pal = palette["swatches"]
    for want, p in zip(SWATCH_RGB, pal):
        got_rgb = np.array([int(p["hex"][i:i + 2], 16) for i in (1, 3, 5)])
        d = np.abs(got_rgb - np.array(want)).max()
        print(f"  barva {p['target']}: chtěl {want}, mám {p['hex']} (syrová {p['raw_hex']}), odchylka {d}")
        if d > 24: errors.append(f"barva {p['target']} mimo: {p['hex']} vs {want}")
    print("\n".join(errors) if errors else "SELFTEST OK")
    return 1 if errors or r.returncode else 0


if __name__ == "__main__":
    sys.exit(main())
