"""Printable A4 sheets the family fills in by hand, then scans, to personalise the art style.

Usage:  python scan_sheets.py <out_dir>
Writes <out_dir>/styl_listy.pdf (to print) and <out_dir>/styl_listy_layout.json (box positions for reading the scans).

Every page carries four corner squares (top-left one hollow = orientation) and a QR code with the page id,
so a scan or phone photo can be straightened and each box cropped from the layout. All coordinates in the JSON
are millimetres from the page's top-left corner. Pale cyan guides are meant to be removed from the scans.
"""
import os, sys, json, zlib, io
from reportlab.pdfgen import canvas
from reportlab.lib.units import mm
from reportlab.lib.colors import Color, black, white
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.graphics.barcode.qr import QrCodeWidget
from reportlab.graphics.shapes import Drawing
from reportlab.graphics import renderPDF
from reportlab.lib.utils import ImageReader
from PIL import Image, ImageChops, ImageFilter
import pymupdf
import lib
lib.MODE = "bw"
import style3
from style3 import alica, hanka, joey
from chars3 import babicka, deda, cat

HERE = os.path.dirname(os.path.abspath(__file__))
FONTS = os.path.join(HERE, "fonts")
pdfmetrics.registerFont(TTFont("Title", os.path.join(FONTS, "ShantellHandBold.ttf")))
pdfmetrics.registerFont(TTFont("Body", os.path.join(FONTS, "ComicNeue-Regular.ttf")))
pdfmetrics.registerFont(TTFont("BodyB", os.path.join(FONTS, "ComicNeue-Bold.ttf")))

VERSION = 1
PW, PH = 210, 297
CYAN = Color(0.55, 0.84, 0.96)
FRAME = Color(0.55, 0.55, 0.55)
INK = Color(0.15, 0.15, 0.15)
GREY = Color(0.45, 0.45, 0.45)
X0, X1, Y0, Y1 = 15, 195, 34, 268
FIDUCIALS = {"tl": (10, 10), "tr": (200, 10), "bl": (10, 287), "br": (200, 287)}
FID = 8
TOTAL = 20

cv = None
PAGES = []
page = None


def Y(y): return (PH - y) * mm


def rect(x, y, w, h, stroke=1, fill=0):
    cv.rect(x * mm, Y(y + h), w * mm, h * mm, stroke=stroke, fill=fill)


def text(x, y, s, font="Body", size=9, col=INK, align="left"):
    cv.setFont(font, size); cv.setFillColor(col)
    {"left": cv.drawString, "center": cv.drawCentredString, "right": cv.drawRightString}[align](x * mm, Y(y), s)


def guide_pen(width=0.6, dash=None):
    cv.setStrokeColor(CYAN); cv.setLineWidth(width); cv.setDash(*(dash or ([], 0)))


def line(x0, y0, x1, y1): cv.line(x0 * mm, Y(y0), x1 * mm, Y(y1))


def circle(x, y, r, fill=0): cv.circle(x * mm, Y(y), r * mm, stroke=1, fill=fill)


def ellipse(x, y, rx, ry): cv.ellipse((x - rx) * mm, Y(y + ry), (x + rx) * mm, Y(y - ry), stroke=1, fill=0)


def dot(x, y, r=0.9):
    cv.setFillColor(CYAN); cv.circle(x * mm, Y(y), r * mm, stroke=0, fill=1)


# ------------------------------------------------------------------ page frame
def new_page(code, title, who, hint):
    global page
    if page: cv.showPage()
    page = {"code": code, "num": len(PAGES), "title": title, "who": who, "boxes": []}
    PAGES.append(page)
    cv.setFillColor(black)
    for k, (cx, cy) in FIDUCIALS.items():
        rect(cx - FID / 2, cy - FID / 2, FID, FID, stroke=0, fill=1)
        if k == "tl":
            cv.setFillColor(white); rect(cx - 2, cy - 2, 4, 4, stroke=0, fill=1); cv.setFillColor(black)
    text(18, 16, title, "Title", 19)
    cv.setStrokeColor(INK); cv.setLineWidth(0.8)
    tw = pdfmetrics.stringWidth("Kreslí: " + who, "BodyB", 11) / mm + 8
    cv.roundRect((192 - tw) * mm, Y(19.5), tw * mm, 8 * mm, 2 * mm, stroke=1, fill=0)
    text(192 - tw / 2, 17, "Kreslí: " + who, "BodyB", 11, align="center")
    for i, h in enumerate(hint if isinstance(hint, list) else [hint]):
        text(18, 24.5 + i * 4.2, h, "Body", 9, GREY)
    qr = QrCodeWidget(f"VMD-STYL|v{VERSION}|{page['num']:02d}|{code}")
    qr.barLevel = "M"
    b = qr.getBounds(); s = 16 * mm
    d = Drawing(s, s, transform=[s / (b[2] - b[0]), 0, 0, s / (b[3] - b[1]), 0, 0]); d.add(qr)
    renderPDF.draw(d, cv, 18 * mm, Y(290))
    text(37, 280, f"List {page['num']:02d} / {TOTAL:02d} · {code} · v{VERSION}", "Body", 8, GREY)
    text(37, 284.5, "Tiskni na 100 % (ne „přizpůsobit stránce“). Nekresli do černých rohových čtverců.", "Body", 8, GREY)
    text(37, 289, "Kresli jen dovnitř šedých rámečků. Modré čáry jsou pomůcky – ze skenu zmizí.", "Body", 8, GREY)


def box(bid, label, x, y, w, h, kind, label_size=8, **meta):
    """label sits above the box; the box itself is the drawing area recorded in the layout"""
    if label: text(x + 0.5, y - 1.2, label, "Body", label_size, INK)
    cv.setStrokeColor(FRAME); cv.setLineWidth(0.5); cv.setDash([], 0)
    rect(x, y, w, h)
    page["boxes"].append(dict(id=bid, label=label, x=round(x, 2), y=round(y, 2), w=round(w, 2), h=round(h, 2), kind=kind, **meta))
    return x, y, w, h


def grid(items, cols, x0=X0, y0=Y0, x1=X1, y1=Y1, gap=3, label_h=4.5):
    """lay items out in a grid; yields (item, x, y, w, h) of each box (below its label row)"""
    rows = (len(items) + cols - 1) // cols
    cw = (x1 - x0 - gap * (cols - 1)) / cols
    ch = (y1 - y0 - gap * (rows - 1)) / rows - label_h
    for i, it in enumerate(items):
        r, c = divmod(i, cols)
        yield it, x0 + c * (cw + gap), y0 + label_h + r * (ch + label_h + gap), cw, ch


# ------------------------------------------------------------------ guide shapes
def guide_dot_rows(x, y, w, h, n, vertical=False):
    for i in range(n):
        f = (i + 0.5) / n
        if vertical: dot(x + w * f, y + 4); dot(x + w * f, y + h - 4)
        else: dot(x + 6, y + h * f); dot(x + w - 6, y + h * f)


def guide_lines(x, y, w, ys, dash=None):
    guide_pen(0.5, dash)
    for gy in ys: line(x + 2, y + gy, x + w - 2, y + gy)


def glyph_cell(x, y, w, h, glyph, lower):
    guide_pen(0.5)
    base = y + h * 0.72
    if lower:
        line(x + 1, base, x + w - 1, base)
        guide_pen(0.4, ([1.5, 1.5], 0))
        line(x + 1, base - h * 0.24, x + w - 1, base - h * 0.24)
        line(x + 1, base - h * 0.48, x + w - 1, base - h * 0.48)
        line(x + 1, base + h * 0.18, x + w - 1, base + h * 0.18)
    else:
        line(x + 1, base, x + w - 1, base)
        guide_pen(0.4, ([1.5, 1.5], 0)); line(x + 1, base - h * 0.48, x + w - 1, base - h * 0.48)
    text(x + 1.2, y + 4, glyph, "BodyB", 8, CYAN)


def pictogram(kind, cx, cy, r):
    """small grey example drawings so Hanka (who can't read) knows what each box wants"""
    cv.setStrokeColor(GREY); cv.setLineWidth(1.1); cv.setDash([], 0)
    page["boxes"][-1].setdefault("ignore", []).append([round(cx - r * 1.3, 2), round(cy - r * 1.3, 2), round(r * 2.6, 2), round(r * 2.6, 2)])
    if kind == "slunce":
        circle(cx, cy, r * 0.45)
        for i in range(8):
            import math
            a = i * math.pi / 4
            line(cx + math.cos(a) * r * 0.6, cy + math.sin(a) * r * 0.6, cx + math.cos(a) * r, cy + math.sin(a) * r)
    elif kind == "kytka":
        for dx, dy in ((0, -0.35), (0.35, 0), (0, 0.35), (-0.35, 0)):
            circle(cx + dx * r, cy - 0.3 * r + dy * r, r * 0.22)
        circle(cx, cy - 0.3 * r, r * 0.12); line(cx, cy + 0.05 * r, cx, cy + r)
    elif kind == "srdce":
        p = cv.beginPath(); p.moveTo(cx * mm, Y(cy + r * 0.8))
        p.curveTo((cx - r * 1.1) * mm, Y(cy), (cx - r * 0.6) * mm, Y(cy - r * 0.9), cx * mm, Y(cy - r * 0.35))
        p.curveTo((cx + r * 0.6) * mm, Y(cy - r * 0.9), (cx + r * 1.1) * mm, Y(cy), cx * mm, Y(cy + r * 0.8))
        cv.drawPath(p, stroke=1, fill=0)
    elif kind == "hlavonozec":
        circle(cx, cy - r * 0.3, r * 0.5); circle(cx - r * 0.18, cy - r * 0.4, r * 0.05); circle(cx + r * 0.18, cy - r * 0.4, r * 0.05)
        cv.arc((cx - r * 0.2) * mm, Y(cy - r * 0.05), (cx + r * 0.2) * mm, Y(cy - r * 0.35), 200, 140)
        line(cx - r * 0.2, cy + r * 0.18, cx - r * 0.35, cy + r); line(cx + r * 0.2, cy + r * 0.18, cx + r * 0.35, cy + r)
        line(cx - r * 0.5, cy - r * 0.3, cx - r, cy - r * 0.1); line(cx + r * 0.5, cy - r * 0.3, cx + r, cy - r * 0.1)
    elif kind == "opicka":
        circle(cx, cy, r * 0.55); circle(cx - r * 0.65, cy - r * 0.15, r * 0.2); circle(cx + r * 0.65, cy - r * 0.15, r * 0.2)
        ellipse(cx, cy + r * 0.18, r * 0.3, r * 0.2); circle(cx - r * 0.18, cy - r * 0.15, r * 0.05); circle(cx + r * 0.18, cy - r * 0.15, r * 0.05)
    elif kind == "cmaranice":
        p = cv.beginPath(); p.moveTo((cx - r) * mm, Y(cy))
        import math
        for i in range(1, 40):
            t = i / 39
            p.lineTo((cx - r + 2 * r * t + math.sin(t * 31) * r * 0.25) * mm, Y(cy + math.sin(t * 17) * r * 0.7))
        cv.drawPath(p, stroke=1, fill=0)
    elif kind == "dlan":
        ellipse(cx, cy + r * 0.25, r * 0.45, r * 0.5)
        for i, dx in enumerate((-0.38, -0.13, 0.12, 0.36)):
            ellipse(cx + dx * r, cy - r * 0.45 - (0.1 if i in (1, 2) else 0) * r, r * 0.1, r * 0.3)
        ellipse(cx - r * 0.62, cy + r * 0.1, r * 0.25, r * 0.1)
    elif kind == "prst":
        for i in range(3): ellipse(cx - r * 0.6 + i * r * 0.6, cy, r * 0.2, r * 0.28)
    elif kind == "tlapka":
        ellipse(cx, cy + r * 0.25, r * 0.38, r * 0.3)
        for dx, dy in ((-0.5, -0.2), (-0.18, -0.55), (0.18, -0.55), (0.5, -0.2)): circle(cx + dx * r, cy + dy * r, r * 0.15)


# ------------------------------------------------------------------ trace guides from the comic characters
class _Box:
    def __init__(self, w, h): self.x, self.y, self.w, self.h = 0, 0, w, h


def trace_image(name, w, h, draw, scale=7):
    """render a character in B&W, keep only its ink lines, recolour them pale cyan"""
    buf = io.BytesIO()
    c = canvas.Canvas(buf, pagesize=(w, h)); lib.set_canvas(c)
    style3._R.seed(zlib.crc32(name.encode()))
    draw(_Box(w, h)); c.showPage(); c.save()
    lib.set_canvas(cv)
    doc = pymupdf.open(stream=buf.getvalue(), filetype="pdf")
    pix = doc[0].get_pixmap(matrix=pymupdf.Matrix(scale, scale), alpha=True)
    im = Image.frombytes("RGBA", (pix.width, pix.height), pix.samples)
    ink = im.convert("L").point(lambda v: 255 if v < 80 else 0)
    mask = ImageChops.multiply(ink, im.getchannel("A").point(lambda v: 255 if v > 128 else 0))
    # solid black fills (boots, Joey's fur) would print as cyan blobs: keep only their rim
    fills = mask.filter(ImageFilter.MinFilter(15)).filter(ImageFilter.MaxFilter(9))
    mask = ImageChops.subtract(mask, fills)
    out = Image.new("RGBA", im.size, (140, 214, 245, 0)); out.putalpha(mask)
    return ImageReader(out), w / h


def place_trace(img, aspect, x, y, w, h, pad=4):
    bw, bh = w - 2 * pad, h - 2 * pad
    iw, ih = (bw, bw / aspect) if bw / aspect <= bh else (bh * aspect, bh)
    cv.drawImage(img, (x + (w - iw) / 2) * mm, Y(y + h - pad), iw * mm, ih * mm, mask="auto")


# ------------------------------------------------------------------ the sheets
UPPER = list("AÁBCČDĎEÉĚFGHIÍJKLMNŇOÓPQRŘSŠTŤUÚŮVWXYÝZŽ")
LOWER = [c.lower() for c in UPPER]
DIGITS = list("0123456789")
PUNCT = list(".,!?:;-–„“()…'+=/%")


def p_navod():
    new_page("navod", "Náš vlastní styl – návod", "táta", "Přečti si nejdřív tenhle list. Ten se neskenuje.")
    y = Y0 + 2
    blocks = [
        ("Proč to děláme", [
            "Komiks i hra se zatím kreslí programem. Z vašich čar, písma, barev a otisků",
            "uděláme styl, který nikdo jiný nemá: tátova ruka, Aličino písmo, Hančiny čmáranice.",
        ]),
        ("Tisk", [
            "Formát A4, měřítko 100 % (vypni „přizpůsobit stránce“). Stačí obyčejný papír.",
            "Kontrola: čára níže musí mít přesně 10 cm. Když ne, tiskárna zmenšuje – oprav nastavení.",
            "Listy 09–11 (tátovo písmo) klidně vytiskni 2× – víc variant = živější písmo.",
            "Listy 14 a 20 (vodovky, otisky) vytiskni na silnější papír, pokud máš.",
        ]),
        ("Čím kreslit", [
            "Táta: stejné pero, kterým bys kreslil komiks (liner/fix 0,3–0,8 mm, černý). Na šrafy totéž.",
            "Holky: svoje pastelky, fixy, voskovky – ty, které opravdu používají. To je ta osobní barva.",
            "Nekreslete modře přes modré pomůcky (modrou pak ze skenu mažu). Modrá jen na listu Barvy.",
        ]),
        ("Pravidla", [
            "Kresli jen dovnitř šedého rámečku, klidně až k okraji. Nevadí, když něco nevyjde – nepřepisuj, prostě pokračuj.",
            "Nezakrývej černé čtverce v rozích ani QR kód – podle nich se sken rovná a pozná list.",
            "Nemusí být nic dokonalé. Chceme, jak kreslíte VY, ne jak by to vypadalo z počítače.",
        ]),
        ("Skenování", [
            "Nejlépe skener: barevně, 600 DPI (stačí 300), celá stránka A4, bez ořezu a „vylepšení“.",
            "Uložit jako PNG nebo TIFF (JPG jen v nejvyšší kvalitě). Jeden soubor na list, název je jedno.",
            "Jde i mobil: list rovně na stole, denní světlo, bez stínu, všechny 4 rohové čtverce v záběru.",
            "Navíc naskenuj jeden prázdný list papíru, na který holky běžně kreslí (textura papíru).",
            "Skeny dej do: ~/SynologyDrive/redrick-obsidian/ai-memory/velka_a_mala_detektivka/topics/styl/skeny/",
        ]),
    ]
    for head, lines in blocks:
        text(X0, y + 4, head, "BodyB", 12); y += 7
        for l in lines:
            text(X0 + 3, y + 3.5, l, "Body", 9.5); y += 5
        y += 3
    cv.setStrokeColor(black); cv.setLineWidth(1); cv.setDash([], 0)
    line(X0 + 3, y + 2, X0 + 103, y + 2)
    for i in range(11): line(X0 + 3 + i * 10, y, X0 + 3 + i * 10, y + (4 if i % 5 == 0 else 2.5))
    text(X0 + 108, y + 3, "← 10 cm", "Body", 9)
    y += 10
    text(X0, y + 4, "Listy", "BodyB", 12); y += 7
    return y


def p_cary():
    new_page("cary", "Čáry", "táta", ["Tvoje obvyklé komiksové pero. Začni a skonči u modrých teček, mezi nimi veď čáru sám.",
                                      "Kresli normální rychlostí, jak kreslíš komiks – nesnaž se o pravítko."])
    rows = [("cary_vod_pomalu", "Vodorovné čáry – pomalu, pečlivě (5×)", 5, False),
            ("cary_vod_rychle", "Vodorovné čáry – rychle, jedním tahem (5×)", 5, False),
            ("cary_svisle", "Svislé čáry shora dolů (12×)", 12, True),
            ("cary_sikme", "Šikmé čáry – zleva dolů i zprava dolů, střídej", 0, None),
            ("cary_tlak", "Čára, která sílí: začni lehce, skonči silně (4×)", 4, False),
            ("cary_dlouhe", "Dlouhá klidná čára přes celý rámeček – jako obrys kopce (3×)", 3, False),
            ("cary_volne", "Volné čáry – jak tě baví", 0, None)]
    for (bid, label, n, vert), x, y, w, h in grid(rows, 1):
        box(bid, label, x, y, w, h, "lines")
        if n and vert is not None: guide_dot_rows(x, y, w, h, n, vertical=vert)
        if bid == "cary_sikme":
            for i in range(9):
                cx = x + 12 + i * (w - 24) / 8
                if i % 2: dot(cx - 7, y + 4); dot(cx + 7, y + h - 4)
                else: dot(cx + 7, y + 4); dot(cx - 7, y + h - 4)


def p_krivky():
    new_page("krivky", "Křivky", "táta", "Modré tvary obtáhni svou rukou, jinde kresli bez předlohy. Klidně víc tahů přes sebe, jak jsi zvyklý.")
    items = [("krivky_kruhy_obtah", "Kruhy – obtáhni modré"), ("krivky_kruhy_volne", "Kruhy – od ruky, bez předlohy"),
             ("krivky_ovaly", "Ovály – obtáhni (hlavy, oči)"), ("krivky_vlnovky", "Vlnovky – voda, vlasy"),
             ("krivky_spiraly", "Spirály a kudrlinky – Hančiny vlasy"), ("krivky_oblouky", "Oblouky – duha, záda, střecha"),
             ("krivky_esicka", "Esíčka – ocásek, cestička"), ("krivky_smycky", "Smyčky – tkanička, šňůra na prádlo")]
    for (bid, label), x, y, w, h in grid(items, 2):
        box(bid, label, x, y, w, h, "curves")
        guide_pen(0.6)
        if bid == "krivky_kruhy_obtah":
            cx = x + 4
            for r in (4, 7, 10, 14):
                circle(cx + r, y + h / 2, r); cx += 2 * r + 4
        elif bid == "krivky_ovaly":
            cx = x + 4
            for rx, ry in ((5, 8), (10, 7), (7, 13), (11, 8)):
                ellipse(cx + rx, y + h / 2, rx, ry); cx += 2 * rx + 4
        elif bid == "krivky_vlnovky":
            guide_lines(x, y, w, [h * f for f in (0.25, 0.5, 0.75)], ([2, 2], 0))


def p_obrysy():
    new_page("obrysy", "Obrysy, rohy a konce čar", "táta", "Tady se ukáže tvoje ruka nejvíc – jak končíš čáru, jak lámeš roh, jak kreslíš kámen nebo keř.")
    items = [("obrysy_konce", "Konce čar: rychlý odtah do špičky (8×)"), ("obrysy_ostre", "Ostré rohy – cik cak"),
             ("obrysy_kulate", "Zakulacené rohy – polštář, krabice"), ("obrysy_kameny", "Kameny a oblázky"),
             ("obrysy_kere", "Keř a koruna stromu – vlnitý obrys"), ("obrysy_mraky", "Mráčky"),
             ("obrysy_zuby", "Zubatá hrana – tráva, srst, roztržený papír"), ("obrysy_ruce", "Dlaně a prstíky (4 ručičky, jak je kreslíš)")]
    for (bid, label), x, y, w, h in grid(items, 2):
        box(bid, label, x, y, w, h, "shapes")


def p_srafy():
    new_page("srafy", "Šrafování a stíny", "táta", "Stínuj tak, jak stínuješ v komiksu. Vyplň celý rámeček (u elipsy jen ji).")
    items = [("srafy_rovne", "Rovnoběžné šrafy"), ("srafy_krizove", "Křížové šrafy"),
             ("srafy_stin_postava", "Stín pod postavou – vyšrafuj modrou elipsu"), ("srafy_prechod", "Od hustých k řídkým (zleva doprava)"),
             ("srafy_tecky", "Tečkování"), ("srafy_drevo", "Dřevo – prkna, suky, letokruhy"),
             ("srafy_zed", "Kameny a cihly ve zdi"), ("srafy_trava", "Tráva a trsy"),
             ("srafy_srst", "Srst – jako má Joey"), ("srafy_voda", "Voda – vlnky a odlesky")]
    for (bid, label), x, y, w, h in grid(items, 2):
        box(bid, label, x, y, w, h, "hatch")
        guide_pen(0.6)
        if bid == "srafy_stin_postava": ellipse(x + w / 2, y + h / 2, w * 0.38, h * 0.22)
        if bid == "srafy_prechod":
            text(x + 2, y + h - 2, "hustě", "Body", 7, CYAN); text(x + w - 2, y + h - 2, "řídce", "Body", 7, CYAN, "right")


def p_bubliny():
    new_page("bubliny", "Rámečky, bubliny a pohyb", "táta", "Obtáhni modré předlohy od ruky – jako okna a bubliny v sešitě. Bubliny nech prázdné, text dopíšu já.")
    x, y = X0, Y0 + 4.5
    box("bubliny_ramecek_siroky", "Rámeček komiksového okénka – obtáhni (široký)", x, y, 180, 38, "panel")
    guide_pen(0.7); rect(x + 5, y + 5, 170, 28)
    y += 38 + 3 + 4.5
    for i in range(2):
        bx = x + i * 91.5
        box(f"bubliny_ramecek_{i + 1}", f"Rámeček okénka – obtáhni ({i + 1})", bx, y, 88.5, 50, "panel")
        guide_pen(0.7); rect(bx + 5, y + 5, 78.5, 40)
    y += 50 + 3
    items = [("bubliny_rec", "Řečová bublina se šipkou"), ("bubliny_mysl", "Myšlenková bublina (obláček + kolečka)"),
             ("bubliny_krik", "Výkřik – zubatá bublina"), ("bubliny_septani", "Šeptání – čárkovaná bublina"),
             ("bubliny_pohyb", "Čárky pohybu – běh, skok, zatřesení"), ("bubliny_efekty", "Hvězdičky, kapky potu, otazníky, nápady")]
    for (bid, label), bx, by, w, h in grid(items, 2, y0=y):
        box(bid, label, bx, by, w, h, "balloon")
        cx, cy = bx + w / 2, by + h / 2 - 3
        if bid == "bubliny_rec":
            guide_pen(0.6); ellipse(cx, cy, w * 0.36, h * 0.3)
            line(cx - 8, cy + h * 0.28, cx - 18, cy + h * 0.45); line(cx - 18, cy + h * 0.45, cx - 1, cy + h * 0.3)
        elif bid == "bubliny_mysl":
            guide_pen(0.6, ([2, 2], 0)); ellipse(cx, cy, w * 0.34, h * 0.27)
            circle(cx - 20, cy + h * 0.36, 2); circle(cx - 25, cy + h * 0.42, 1.2)
        elif bid == "bubliny_krik":
            guide_pen(0.6, ([2, 2], 0)); ellipse(cx, cy, w * 0.3, h * 0.24)
        elif bid == "bubliny_septani":
            guide_pen(0.6, ([2, 2], 0)); ellipse(cx, cy, w * 0.34, h * 0.27)


def p_obliceje():
    new_page("obliceje", "Obličeje a nálady", "táta", "Do modrého kolečka nakresli oči, obočí a pusu – jak je kreslíš ty. Klidně i nos a vlasy.")
    moods = [("happy", "šťastná"), ("grin", "zubí se"), ("surprised", "překvapená"), ("wow", "jů! nadšená"),
             ("think", "přemýšlí"), ("worried", "ustaraná"), ("whisper", "šeptá"), ("determined", "odhodlaná"),
             ("sleepy", "ospalá"), ("sad", "trochu smutná"), ("joey_happy", "Joey – radost (celá hlava)"), ("joey_sniff", "Joey – čmuchá (celá hlava)")]
    for (mood, label), x, y, w, h in grid(moods, 3):
        box(f"obliceje_{mood}", label, x, y, w, h, "face", mood=mood)
        if not mood.startswith("joey"):
            guide_pen(0.6); r = min(w, h) * 0.36; circle(x + w / 2, y + h / 2, r)
            guide_pen(0.4, ([1.5, 1.5], 0)); line(x + w / 2 - r, y + h / 2, x + w / 2 + r, y + h / 2)


def p_obtah(code, title, chars, cols):
    new_page(code, title, "táta", ["Obtáhni modrou předlohu svou čarou. Nemusí to být přesně – chceme právě tvou ruku.",
                                   "Co bys nakreslil jinak, uprav. Stíny a šrafy přidej, jak bys je kreslil do komiksu."])
    for (bid, label, w0, h0, fn), x, y, w, h in grid(chars, cols):
        box(bid, label, x, y, w, h, "trace", source=bid.split("_", 1)[1])
        img, aspect = trace_image(bid, w0, h0, fn)
        place_trace(img, aspect, x, y, w, h)


def p_pismo(code, title, glyphs, lower, per=2, cols=12):
    new_page(code, title, "táta", ["Piš písmo, kterým píšeš do bublin. Každé písmeno 2× – pokaždé trochu jinak je dobře.",
                                   "Malé modré písmeno v rohu ukazuje, co napsat. Sedni písmenem na plnou modrou čáru."])
    cells = [g for g in glyphs for _ in range(per)]
    for i, (g, x, y, w, h) in enumerate((g, x, y, w, h) for g, x, y, w, h in grid(cells, cols, gap=0, label_h=0)):
        box(f"{code}_{i:03d}", "", x, y, w, h, "glyph", glyph=g, variant=i % per, case="lower" if lower else "upper")
        glyph_cell(x, y, w, h, g, lower)


def p_znaky():
    new_page("pismo_znaky", "Tátovo písmo – číslice, znaky, věty", "táta",
             ["Číslice a znaky 2×. Pak opiš věty svým písmem na plnou modrou čáru – tak se naučím mezery a spojení."])
    cells = [g for g in DIGITS for _ in range(2)] + [g for g in PUNCT for _ in range(2)]
    for i, (g, x, y, w, h) in enumerate(grid(cells, 14, y1=Y0 + 98, gap=0, label_h=0)):
        box(f"pismo_znaky_{i:03d}", "", x, y, w, h, "glyph", glyph=g, variant=i % 2, case="sign")
        glyph_cell(x, y, w, h, g, False)
    sentences = ["AHOJ, JÁ JSEM ALICA A TOHLE JE HANKA!", "Čmuch čmuch! Joey něco našel u kůlny.",
                 "PŘÍLIŠ ŽLUŤOUČKÝ KŮŇ ÚPĚL ĎÁBELSKÉ ÓDY.", "Příliš žluťoučký kůň úpěl ďábelské ódy.",
                 "KDE JSOU PONOŽKY? TO JE ZÁHADA!", "Babička peče buchty, děda spí v houpací síti."]
    for i, (s, x, y, w, h) in enumerate(grid(sentences, 1, y0=Y0 + 104, label_h=5, gap=2)):
        box(f"pismo_veta_{i}", s, x, y, w, h, "sentence", text=s, label_size=9)
        guide_pen(0.5); line(x + 2, y + h * 0.75, x + w - 2, y + h * 0.75)


def p_zvuky():
    new_page("zvuky", "Zvuky a nadpisy", "táta", "Velká komiksová písmena – tlustá, obtažená, vybarvená nebo se stínem. Přesně jak by byla v sešitě.")
    box("zvuky_nadpis", "Nadpis série: Velká a malá detektivka", X0, Y0 + 4.5, 180, 36, "title", text="Velká a malá detektivka")
    words = ["BUM!", "PRÁSK!", "ŤUK ŤUK", "ČMUCH ČMUCH!", "HAF! HAF!", "MŇAU", "ŠUST ŠUST", "CVAK!", "ŽBLUŇK!", "CHRRR…", "HURÁ!", "KONEC"]
    for w_, x, y, w, h in grid(words, 2, y0=Y0 + 44):
        box(f"zvuky_{zlib.crc32(w_.encode()) & 0xffff:04x}", w_, x, y, w, h, "sound", text=w_, label_size=10)


def p_priroda():
    new_page("priroda", "Příroda a věci", "táta", "Jak kreslíš tyhle věci ty. Z nich budu skládat pozadí a drobnosti ve hře.")
    items = [("strom", "Listnatý strom"), ("smrk", "Smrk / jehličnan"), ("ker", "Keř"), ("trava", "Tráva a kytky"), ("kamen", "Kámen a oblázky"),
             ("mrak", "Mrak"), ("houba", "Houba"), ("list", "List"), ("plot", "Kus plotu"), ("lupa", "Lupa"),
             ("srdce", "Srdíčko – naše skryté srdce"), ("tlapka", "Tlapka Joeyho"), ("hvezda", "Hvězdička – Klub Hvězdička"),
             ("ponozka", "Ponožka"), ("klic", "Starý klíč")]
    for (bid, label), x, y, w, h in grid(items, 3):
        box(f"priroda_{bid}", label, x, y, w, h, "object")


def p_textury():
    new_page("textury", "Textury", "táta + holky", "Vybarvi celý rámeček. Tužku drž normálně, vodovky klidně přetečou – nevadí.")
    items = [("tuzka_slabe", "Tužka – slabě"), ("tuzka_stredne", "Tužka – středně"), ("tuzka_silne", "Tužka – silně"),
             ("tuzka_prechod", "Tužka – od světlé k tmavé"), ("pastelka", "Pastelka – vybarvi"), ("voskovka", "Voskovka – vybarvi"),
             ("fix", "Fix – vybarvi"), ("vodovky_1", "Vodovky – jedna barva"), ("vodovky_2", "Vodovky – dvě barvy do sebe"),
             ("prsty", "Otisky prstů (barva nebo razítkovka)"), ("houbicka", "Houbička nebo zmačkaný papír"), ("papir", "NECH PRÁZDNÉ – jen papír")]
    for (bid, label), x, y, w, h in grid(items, 3):
        box(f"textury_{bid}", label, x, y, w, h, "texture")


def p_barvy():
    new_page("barvy", "Naše barvy", "holky", ["Vybarvi celé pole pastelkami nebo fixy, které holky opravdu používají.",
                                             "Horní pruh NEVYBARVUJ – je to kalibrace barev skeneru."])
    y = Y0 + 4.5
    text(X0 + 0.5, y - 1.2, "Kalibrace – nevybarvovat", "BodyB", 8)
    patches = [(1 - i / 10,) * 3 for i in range(11)] + [(0, 1, 1), (1, 0, 1), (1, 1, 0), (1, 0, 0), (0, 0.6, 0), (0, 0, 1)]
    pw = 180 / len(patches)
    for i, rgb in enumerate(patches):
        cv.setFillColor(Color(*rgb)); cv.setStrokeColor(FRAME); cv.setLineWidth(0.3); rect(X0 + i * pw, y, pw, 12, stroke=1, fill=1)
    page["calibration"] = dict(x=X0, y=y, w=180, h=12, patches=[list(p) for p in patches])
    items = ["Alicina pláštěnka", "Hančiny lacláče", "proužky Hančina trička", "Aličiny vlasy", "Hančiny vlasy",
             "obličej – kůže", "Joey – černá srst", "tráva", "nebe", "voda v rybníce", "střecha chalupy", "dřevo – kůlna",
             "cesta a hlína", "kytky – červená", "kytky – žlutá", "opička (Hančin orangutan)",
             "Aličina nejoblíbenější", "Hančina nejoblíbenější", "tátova nejoblíbenější", "mámina nejoblíbenější"]
    for i, (label, x, y_, w, h) in enumerate(grid(items, 4, y0=Y0 + 20)):
        box(f"barvy_{i:02d}", label, x, y_, w, h, "swatch", target=label, label_size=8.5)


def p_alica_kresli():
    new_page("alica_kresli", "Alica kreslí", "Alica", "Nakresli, jak to kreslíš ty. Klidně vybarvi. Žádné špatně neexistuje!")
    items = [("joey", "JOEY"), ("ja", "JÁ – ALICA"), ("hanka", "HANKA"), ("rodice", "MÁMA A TÁTA"), ("chalupa", "CHALUPA"), ("strom", "STROM"),
             ("kytka", "KYTKA"), ("slunce", "SLUNÍČKO"), ("micka", "KOČKA MICKA"), ("lupa", "LUPA"), ("srdce", "SRDÍČKO"), ("cokoli", "CO CHCEŠ")]
    for (bid, label), x, y, w, h in grid(items, 3, label_h=6):
        box(f"alica_{bid}", label, x, y, w, h, "kid_drawing", label_size=12)


def p_alica_pismena():
    new_page("alica_pismena", "Alica píše písmena", "Alica", "Napiš každé písmeno do jeho okénka. Velkými písmeny, jak umíš.")
    for i, (g, x, y, w, h) in enumerate(grid(UPPER, 7, label_h=6, gap=2.5)):
        box(f"alica_pismeno_{i:02d}", g, x, y, w, h, "glyph", glyph=g, case="upper", label_size=13)
        guide_pen(0.6); line(x + 2, y + h * 0.8, x + w - 2, y + h * 0.8)


def p_alica_slova():
    new_page("alica_slova", "Alica – čísla, slova a podpis", "Alica", "Napiš čísla a slova. Dole se třikrát podepiš.")
    for i, (g, x, y, w, h) in enumerate(grid(DIGITS, 10, y1=Y0 + 34, label_h=6, gap=2)):
        box(f"alica_cislo_{i}", g, x, y, w, h, "glyph", glyph=g, case="digit", label_size=13)
        guide_pen(0.6); line(x + 1, y + h * 0.8, x + w - 1, y + h * 0.8)
    words = ["ALICA", "HANKA", "JOEY", "MÁMA", "TÁTA", "AHOJ!", "KONEC", "DETEKTIVKA", "ČMUCH ČMUCH", "LUPA"]
    for i, (s, x, y, w, h) in enumerate(grid(words, 2, y0=Y0 + 40, y1=Y0 + 190, label_h=6)):
        box(f"alica_slovo_{i}", s, x, y, w, h, "word", text=s, label_size=12)
        guide_pen(0.6); line(x + 2, y + h * 0.78, x + w - 2, y + h * 0.78)
    for i, (_, x, y, w, h) in enumerate(grid([0, 1, 2], 3, y0=Y0 + 196, label_h=6)):
        box(f"alica_podpis_{i}", "PODPIS", x, y, w, h, "signature", label_size=12)


def p_hanka():
    new_page("hanka_cmara", "Hanka kreslí", "Hanka", ["Obrázek nahoře v rohu ukazuje, co nakreslit. Rodič přečte nápis.",
                                                     "Cokoli Hanka nakreslí, je správně. Pastelky i fixy."])
    items = [("slunce", "sluníčko"), ("kytka", "kytička"), ("srdce", "srdíčko"),
             ("hlavonozec", "člověk – máma, táta, Alica nebo já"), ("opicka", "opička"), ("cmaranice", "čmáranice – jak chce")]
    for (bid, label), x, y, w, h in grid(items, 2, label_h=6):
        box(f"hanka_{bid}", label, x, y, w, h, "kid_drawing", label_size=11)
        pictogram(bid, x + w - 9, y + 9, 6)


def p_otisky():
    new_page("otisky", "Otisky", "holky", ["Omyvatelná barva nebo razítkovka. Dlaň celou do barvy, pak pevně přitisknout.",
                                           "Tlapku Joeyho jen když bude chtít – a hned umýt."])
    x, y = X0, Y0 + 6
    for i, (bid, label) in enumerate((("hanka_dlan", "Hančina dlaň"), ("alica_dlan", "Aličina dlaň"))):
        box(f"otisky_{bid}", label, x + i * 91.5, y, 88.5, 120, "print", label_size=11)
        pictogram("dlan", x + i * 91.5 + 80, y + 9, 6)
    y += 120 + 3 + 6
    items = [("hanka_prsty", "Prstíky – Hanka", "prst"), ("alica_prsty", "Prstíky – Alica", "prst"),
             ("joey_tlapka", "Tlapka Joeyho", "tlapka"), ("hanka_podpis", "Hančin podpis – H nebo čmáranice", "cmaranice")]
    for (bid, label, pic), bx, by, w, h in grid(items, 2, y0=y, label_h=6):
        box(f"otisky_{bid}", label, bx, by, w, h, "print", label_size=11)
        pictogram(pic, bx + w - 10, by + 9, 6)


def build(out_dir):
    global cv, page
    os.makedirs(out_dir, exist_ok=True)
    pdf = os.path.join(out_dir, "styl_listy.pdf")
    cv = canvas.Canvas(pdf, pagesize=(PW * mm, PH * mm))
    cv.setTitle("Velká a malá detektivka – listy pro vlastní styl"); cv.setAuthor("Andrej Antas")
    lib.set_canvas(cv)
    toc_y = p_navod()
    p_cary(); p_krivky(); p_obrysy(); p_srafy(); p_bubliny(); p_obliceje()
    p_obtah("obtah_holky", "Obtáhni Alici a Hanku", [
        ("obtah_alica", "Alica", 120, 240, lambda b: alica(b.w / 2, 8, 2.2, mood="happy", shadow=False)),
        ("obtah_hanka", "Hanka", 110, 200, lambda b: hanka(b.w / 2, 8, 2.2, mood="happy", shadow=False))], 2)
    p_obtah("obtah_ostatni", "Obtáhni Joeyho, Micku, babičku a dědu", [
        ("obtah_joey", "Joey", 180, 140, lambda b: joey(b.w / 2 - 5, 8, 2.2, mood="happy", shadow=False)),
        ("obtah_micka", "Micka", 110, 110, lambda b: cat(b.w / 2 - 8, 8, 2.2, mood="sleepy")),
        ("obtah_babicka", "Babička", 130, 270, lambda b: babicka(b.w / 2, 8, 2.2, mood="happy", shadow=False)),
        ("obtah_deda", "Děda", 140, 300, lambda b: deda(b.w / 2, 8, 2.2, mood="happy", shadow=False))], 2)
    p_pismo("pismo_velka", "Tátovo písmo – velká písmena", UPPER, False)
    p_pismo("pismo_mala", "Tátovo písmo – malá písmena", LOWER, True)
    p_znaky(); p_zvuky(); p_priroda(); p_textury(); p_barvy()
    p_alica_kresli(); p_alica_pismena(); p_alica_slova(); p_hanka(); p_otisky()
    cv.showPage(); cv.save()

    # the table of contents on page 00 needs the finished page list: stamp it in a second pass
    assert len(PAGES) - 1 == TOTAL, len(PAGES)
    doc = pymupdf.open(pdf)
    fontfile = os.path.join(FONTS, "ComicNeue-Regular.ttf")
    toc = doc[0]
    col_w = 90
    for i, pg in enumerate(PAGES[1:]):
        c, r = divmod(i, 10)
        toc.insert_text(((X0 + 3 + c * col_w) * mm, (toc_y + 3.5 + r * 4.6) * mm),
                        f"{pg['num']:02d}  {pg['title']}  ({pg['who']})", fontsize=8.5, fontname="cn", fontfile=fontfile)
    doc.saveIncr(); doc.close()

    layout = dict(version=VERSION, units="mm", page=[PW, PH], fiducials=FIDUCIALS, fiducial_size=FID,
                  fiducial_note="tl square has a white 4 mm hole (orientation)",
                  qr="VMD-STYL|v<version>|<page num>|<code>", guide_rgb=[140, 214, 245], pages=PAGES)
    with open(os.path.join(out_dir, "styl_listy_layout.json"), "w") as f:
        json.dump(layout, f, ensure_ascii=False, indent=1)
    print(pdf, len(PAGES), "pages,", sum(len(p["boxes"]) for p in PAGES), "boxes")


# ------------------------------------------------------------------ supplement: the block-letter alphabet
# Titles and sound words only had táta's 12 words and the series title, so every other title fell back to his
# handwriting drawn fat. These sheets collect the whole alphabet in his outlined block letters for a title font.
# A separate set with its own PDF and layout, so the first set's page numbers (already scanned) stay valid.
BLOCK_PAGES = [
    list("AÁBCČDĎEÉĚFGHIÍJKL"),
    list("MNŇOÓPQRŘSŠTŤUÚŮVW"),
]
BLOCK_LAST = list("XYÝZŽ")
BLOCK_ONCE = DIGITS + list(",.…–:()„“'+=")


def p_nadpisy_navod():
    new_page("nadpisy_navod", "Komiksová abeceda – návod", "táta", "Přečti si nejdřív tenhle list. Ten se neskenuje.")
    y = Y0 + 2
    blocks = [
        ("Co kreslit", [
            "Velká komiksová písmena, jako jsi nakreslil nadpis a zvuky (ukázka níže). Z nich bude písmo pro všechny",
            "nadpisy a zvuky v komiksu i ve hře – i ta slova, která jsi zatím nenakreslil.",
            "Jen obrys, uvnitř nech prázdné. Nevybarvuj a nedělej stín – výplň a stín přidá počítač stejně u všech.",
            "Každé písmeno 2×, pokaždé trochu jinak (střídají se, ať nápis nevypadá jako z tiskárny).",
        ]),
        ("Jak velké", [
            "Spodek písmene na plnou modrou čáru, vršek k čárkované. Háčky a čárky nad čárkovanou,",
            "ocásek čárky a Q pod plnou. Šířka je na tobě – úzké I, široké M, jak to kreslíš normálně.",
            "Písmeno se nesmí dotknout šedého rámečku a nesmí přetéct do vedlejšího.",
        ]),
        ("Čím", [
            "Stejnou tužkou nebo perem, jakým jsi kreslil list Zvuky a nadpisy – ať písmena sedí k sobě.",
        ]),
        ("Tisk a sken", [
            "A4, měřítko 100 %. Sken barevně 300–600 DPI, PNG. Rohové čtverce a QR kód nezakrývej.",
            "Skeny dej do: ~/SynologyDrive/redrick-obsidian/ai-memory/velka_a_mala_detektivka/topics/styl/skeny_nadpisy/",
        ]),
    ]
    for head, lines in blocks:
        text(X0, y + 4, head, "BodyB", 12); y += 7
        for l in lines:
            text(X0 + 3, y + 3.5, l, "Body", 9.5); y += 5
        y += 3
    text(X0, y + 4, "Ukázka – tvůj nadpis ze skenu:", "BodyB", 12); y += 8
    sample = os.path.join(HERE, "style_data", "stamps", "zvuky_nadpis.png")
    if os.path.exists(sample):
        img = Image.open(sample)
        w = 120; h = w * img.height / img.width
        cv.drawImage(ImageReader(img), (X0 + 3) * mm, Y(y + h), w * mm, h * mm, mask="auto")


def p_nadpisy(code, title, cells, hint_extra=None):
    hint = ["Jen obrys, nevybarvuj, bez stínu. Každé písmeno tak, jak ho kreslíš v nadpisech.",
            "Spodek na plnou modrou čáru, vršek k čárkované; háčky a čárky nad ni."]
    new_page(code, title, "táta", hint + ([hint_extra] if hint_extra else []))
    for i, ((g, variant), x, y, w, h) in enumerate(grid(cells, 6, y0=Y0 + (3 if hint_extra else 0), gap=0, label_h=0)):
        box(f"{code}_{i:03d}", "", x, y, w, h, "glyph", glyph=g, variant=variant, case="block")
        glyph_cell(x, y, w, h, g, False)


def build_nadpisy(out_dir):
    global cv, page, TOTAL
    os.makedirs(out_dir, exist_ok=True)
    PAGES.clear(); page = None
    pdf = os.path.join(out_dir, "nadpisy_listy.pdf")
    cv = canvas.Canvas(pdf, pagesize=(PW * mm, PH * mm))
    cv.setTitle("Velká a malá detektivka – komiksová abeceda"); cv.setAuthor("Andrej Antas")
    lib.set_canvas(cv)
    TOTAL = len(BLOCK_PAGES) + 1
    p_nadpisy_navod()
    for i, letters in enumerate(BLOCK_PAGES):
        p_nadpisy(f"nadpisy_{i + 1}", f"Komiksová abeceda {letters[0]}–{letters[-1]}", [(g, v) for g in letters for v in (0, 1)])
    p_nadpisy("nadpisy_3", "Komiksová abeceda X–Ž, číslice, znaky",
              [(g, v) for g in BLOCK_LAST + list("!?") for v in (0, 1)] + [(g, 0) for g in BLOCK_ONCE],
              "Číslice a znaky stačí jednou.")
    cv.showPage(); cv.save()
    layout = dict(version=VERSION, units="mm", page=[PW, PH], fiducials=FIDUCIALS, fiducial_size=FID,
                  fiducial_note="tl square has a white 4 mm hole (orientation)",
                  qr="VMD-STYL|v<version>|<page num>|<code>", guide_rgb=[140, 214, 245], pages=PAGES)
    with open(os.path.join(out_dir, "nadpisy_listy_layout.json"), "w") as f:
        json.dump(layout, f, ensure_ascii=False, indent=1)
    print(pdf, len(PAGES), "pages,", sum(len(p["boxes"]) for p in PAGES), "boxes")


if __name__ == "__main__":
    # --nadpisy: the supplement with the block-letter alphabet instead of the main set
    args = [a for a in sys.argv[1:] if a != "--nadpisy"]
    out = args[0] if args else os.path.join(HERE, "out", "styl")
    build_nadpisy(out) if "--nadpisy" in sys.argv else build(out)
