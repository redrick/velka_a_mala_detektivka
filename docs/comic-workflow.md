# How to make the next comic issue (for Claude Code)

The comics and the game share one art library (`art/`). Always draw new characters, props and
backgrounds there, so the comic and the game stay identical.

## Rules
- Series title: **Velká a malá detektivka** (both sisters are equal detectives). Cover: "Alica a Hanka" plus the case line.
- Page count grows with the girls (issue 1: 16, issue 2: 20, issues 3–5: 24): cover, story pages, an activity page ("Detektivní zápisník"), and a teaser for the next issue. The total must be a multiple of 4: `make_booklet.py` asserts it, because each A4 sheet holds 4 booklet pages.
- **Before writing an issue, ask the dad for real details** (names, places, recent events) and weave them in.
- Czech text, short sentences (Alica is in 2nd grade). Nothing scary; every "culprit" is an animal or a kind person.
- **Bubble reading order.** A parent reads aloud top to bottom, left to right. In every panel the first bubble must sit
  higher or further left than the next one: whoever speaks first stands on the left, or their bubble goes a tier higher.
  Never put an answer left of or above its question. `comic_issue3.py`/`comic_issue4.py` enforce this: their `Pn` panel and `say()`
  place balloons automatically in reading order, keep them off faces, and the build fails listing every panel
  where order, overlap or a covered face goes wrong. Copy `comic_issue5.py` (not 1–4) as the template; winter art is in `art/winter.py`.
- **Don't make the mystery obvious.** Alica (7) solved issue 2 by page 5 because the clues named the answer. Keep key clues
  visual and let the characters dismiss them, keep red herrings plausible, don't name the culprit early, and add a
  "STOP, detektive!" page before the reveal.
- Story shape: case → false lead → plan/trap → journey (Hanka gets her own moment as the small one) → gentle reveal → a clue for the next case.
  Vary it now and then (other narrators, reader-solves pages, new settings) – see docs/series-plan.md.
- Hanka (4): can't read or write; always has her plush orangutan (opička) and a torch (baterka); nothing in her hair.
  Alica (7): the magnifier (lupa) and notebook; long straight hair with a clip.
  Joey: the family's real border collie.
- Greyscale only (the family prints on a B&W laser printer).

## Build
Finished issues live in the repo under `comics/<series>/`, named `<nn>_<title>.pdf` plus the
printable booklet `<nn>_<title>_BROZURA.pdf`. Set `OUT` in the issue script to that path.
```
cd art
.venv/bin/python comic_issueN.py                     # copy comic_issue4.py as a template
.venv/bin/python make_booklet.py ../comics/velka_a_mala_detektivka/NN_title.pdf \
                                 ../comics/velka_a_mala_detektivka/NN_title_BROZURA.pdf
```
Check pages visually (render PNGs with pdftoppm or pymupdf) for overlapping balloons and characters before handing over.
