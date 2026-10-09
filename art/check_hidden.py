"""Checks a comic's hidden-object game: renders the issue with and without the hidden objects and reports, for each
one, its page, how much of it actually shows and how much it stands out from what's around it. Writes a contact
sheet at booklet (A5) print size, so the objects can be judged at the size the kids will hunt for them.

    .venv/bin/python check_hidden.py comic_issue5.py winter.hidden_triangle 10 --skip 22

--skip lists pages whose calls aren't hidden objects (the notebook page's answer-key icon).

Issue 5 promised 10 triangles and the kids found 7: all 10 were drawn, but they were ~3 mm wide and five sat on
plain white snow. Run this before calling an issue done, and print the sheet.
"""
import sys, os, json, shutil, subprocess, tempfile
import numpy as np
from PIL import Image, ImageDraw

HERE = os.path.dirname(os.path.abspath(__file__))
DPI = 200
A5 = 0.707          # the booklet prints each A4 page at A5
MIN_MM = 6.0        # smallest width that a 7-year-old finds on a printed A5 page
MIN_CONTRAST = 60   # grey levels between the object and its surroundings
MIN_SHOWN = 0.6     # share of the object left uncovered, against the best-shown one


def render(script, spec, mode, log_path):
    """runs the issue script in a subprocess with the hidden-object function wrapped; returns the PDF it wrote"""
    code = f"""
import sys, json, runpy, os
sys.path.insert(0, {HERE!r}); os.chdir({HERE!r})
import importlib, style3
mod = importlib.import_module({spec.rsplit('.', 1)[0]!r}); name = {spec.rsplit('.', 1)[1]!r}
orig = getattr(mod, name); log = []
def probe(x, y, *a, **kw):
    import inspect
    r = inspect.signature(orig).bind(x, y, *a, **kw); r.apply_defaults()
    size = r.arguments.get("r", r.arguments.get("s", 5))
    cv = style3.C; m = cv._currentMatrix
    log.append(dict(page=cv.getPageNumber(), x=m[0]*x + m[2]*y + m[4], y=m[1]*x + m[3]*y + m[5], r=size*abs(m[0])))
    if {mode!r} == "on": orig(x, y, *a, **kw)
setattr(mod, name, probe)
runpy.run_path({script!r}, run_name="__main__")
json.dump(log, open({log_path!r}, "w"))
"""
    out = subprocess.run([sys.executable, "-c", code], capture_output=True, text=True)
    if out.returncode: sys.exit(out.stderr[-2000:])
    return json.load(open(log_path))


def page_img(pdf, page, tmp, tag):
    base = os.path.join(tmp, f"{tag}{page}")
    subprocess.run(["pdftoppm", "-r", str(DPI), "-f", str(page), "-l", str(page), "-gray", "-singlefile", pdf, base], check=True)
    return np.asarray(Image.open(base + ".pgm")).astype(float)


def main():
    args = sys.argv[1:]
    skip = set()
    if "--skip" in args:
        i = args.index("--skip"); skip = {int(p) for p in args[i + 1].split(",")}; del args[i:i + 2]
    script, spec = args[0], args[1]
    want = int(args[2]) if len(args) > 2 else None
    script = os.path.abspath(script)
    # the issue script names its own output; find it by what changed after a run
    tmp = tempfile.mkdtemp(prefix="hidden_")
    comics = os.path.join(os.path.dirname(HERE), "comics")
    before = {os.path.join(d, f): os.path.getmtime(os.path.join(d, f)) for d, _, fs in os.walk(comics) for f in fs}
    log = render(script, spec, "off", os.path.join(tmp, "off.json"))
    after = {os.path.join(d, f): os.path.getmtime(os.path.join(d, f)) for d, _, fs in os.walk(comics) for f in fs}
    pdf = max((p for p in after if after[p] != before.get(p)), key=lambda p: after[p])
    off = os.path.join(tmp, "off.pdf"); shutil.copy(pdf, off)
    log = render(script, spec, "on", os.path.join(tmp, "on.json"))  # leaves the real issue in place
    log = [t for t in log if t["page"] not in skip]
    k = DPI / 72
    rows, crops = [], []
    for i, t in enumerate(log):
        on, of = page_img(pdf, t["page"], tmp, "on"), page_img(off, t["page"], tmp, "off")
        H = on.shape[0]
        cx, cy, R = int(t["x"]*k), int(H - t["y"]*k), int(t["r"]*k*1.4)
        a, b = on[cy-R:cy+R, cx-R:cx+R], of[cy-R:cy+R, cx-R:cx+R]
        mask = np.abs(a - b) > 25
        shown = int(mask.sum())
        # contrast: the object's own pixels against the same spot without it
        contrast = float(np.abs(a[mask] - b[mask]).mean()) if shown else 0.0
        mm = 2 * t["r"] / 72 * 25.4 * A5
        rows.append(dict(n=i + 1, page=t["page"], mm=mm, shown=shown, contrast=contrast))
        W = int(t["r"]*k*7)
        crop = Image.fromarray(on[max(0, cy-W):cy+W, max(0, cx-W):cx+W].astype("uint8")).convert("RGB")
        crops.append((crop, t["page"]))
    best = max((r["shown"] for r in rows), default=1)
    bad = 0
    print(f"{'#':>2} {'str.':>4} {'šířka A5':>9} {'vidět':>6} {'kontrast':>8}  problém")
    for r in rows:
        why = []
        if r["mm"] < MIN_MM: why.append(f"malý (< {MIN_MM:.0f} mm)")
        if r["shown"] < best * MIN_SHOWN: why.append("zakrytý")
        if r["contrast"] < MIN_CONTRAST: why.append("splývá")
        bad += bool(why)
        print(f"{r['n']:>2} {r['page']:>4} {r['mm']:>7.1f}mm {r['shown']/best:>6.0%} {r['contrast']:>8.0f}  {', '.join(why) or 'ok'}")
    pages = [r["page"] for r in rows]
    if want is not None and len(rows) != want:
        print(f"!! počet: nakresleno {len(rows)}, sešit slibuje {want}"); bad += 1
    if len(set(pages)) != len(pages): print("!! víc objektů na jedné stránce:", sorted(pages))
    print("stránky:", ", ".join(map(str, pages)))
    # contact sheet: each crop scaled to booklet print size at 150 dpi screen
    s = 150 / DPI * A5
    cells = [c.resize((max(1, int(c.width*s)), max(1, int(c.height*s)))) for c, _ in crops]
    cw = max(c.width for c in cells) + 10; ch = max(c.height for c in cells) + 24
    sheet = Image.new("RGB", (cw * min(6, len(cells)), ch * ((len(cells) + 5) // 6)), "white")
    d = ImageDraw.Draw(sheet)
    for i, (c, (_, page)) in enumerate(zip(cells, crops)):
        x, y = (i % 6) * cw, (i // 6) * ch
        sheet.paste(c, (x + 5, y + 20)); d.text((x + 5, y + 4), f"#{i+1} str. {page}", fill="black")
    out = os.path.join(tmp, "hidden_sheet.png"); sheet.save(out)
    print("náhled:", out)
    sys.exit(1 if bad else 0)


if __name__ == "__main__":
    main()
