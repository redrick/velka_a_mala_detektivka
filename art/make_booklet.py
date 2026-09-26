"""Impose an A4 comic PDF into an A5 saddle-stitch booklet (A4 landscape, 2 pages per side).
Usage: python make_booklet.py input.pdf output_BROZURA.pdf
Print duplex, flip on SHORT edge, fold each sheet, nest sheet 2 inside sheet 1, etc."""
import sys
from pypdf import PdfReader, PdfWriter, PageObject, Transformation

src = PdfReader(sys.argv[1]); n = len(src.pages)
assert n % 4 == 0, f"page count {n} must be a multiple of 4"
W, H = 842, 595; s = (W/2)/595.28
out = PdfWriter()
for i in range(n//4):
    for L, R in ((n-1-2*i, 2*i), (2*i+1, n-2-2*i)):
        pg = PageObject.create_blank_page(width=W, height=H)
        for idx, xo in ((L, 0), (R, W/2)):
            pg.merge_transformed_page(src.pages[idx], Transformation().scale(s, s).translate(xo, (H-842*s)/2))
        out.add_page(pg)
out.write(sys.argv[2]); print("booklet:", sys.argv[2])
