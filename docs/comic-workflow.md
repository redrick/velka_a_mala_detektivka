# How to make the next comic issue (for Claude Code)

The comics and the game share one art library (`art/`). Always draw new characters, props and
backgrounds there, so the comic and the game stay identical.

## Rules
- Series title: **Velká a malá detektivka** (both sisters are equal detectives). Cover: "Alica a Hanka" plus the case line.
- **16 pages** per issue: cover, 13 story pages, an activity page ("Detektivní zápisník"), and a teaser for the next issue.
- **Before writing an issue, ask the dad for real details** (names, places, recent events) and weave them in.
- Czech text, short sentences (Alica is in 2nd grade). Nothing scary; every "culprit" is an animal or a kind person.
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
.venv/bin/python comic_issueN.py                     # copy comic_issue1.py as a template
.venv/bin/python make_booklet.py ../comics/velka_a_mala_detektivka/NN_title.pdf \
                                 ../comics/velka_a_mala_detektivka/NN_title_BROZURA.pdf
```
Check pages visually (render PNGs with pdftoppm or pymupdf) for overlapping balloons and characters before handing over.
