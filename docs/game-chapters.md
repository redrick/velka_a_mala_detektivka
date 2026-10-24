# Game chapters: one playable story per comic issue

Each story follows its comic, but the game adds puzzles the comic doesn't have, so a child who has
read the comic still has something new to solve. Every story gets at least one **logic minigame**
(mouse and keyboard, no fail state, Joey gives hints).

## Minigames (built)
All live in `game/game/minigames/` and share `minigame_base.gd`: a paper sheet over the room, a title,
a one-line task, the board, Joey's hint line, and the buttons **↶ Zpět / Znovu / Joey poradí**.
Keys: arrows/WASD, Z or Backspace = back, R = again, H = hint, Enter/Space = action.
Tiles are drawn in `art/minigames.py` (`export_assets.py --only minigames`).
`tools/check_levels.py` solves every level and fails if one can't be solved. Main menu → **Minihry** lists them for testing.

| story | minigame | what it trains | where in the story |
|---|---|---|---|
| 1 Ponožky | **Nastraž past**: push flour sacks onto the tiny footprints (3 levels) | planning ahead: a sack can be pushed, never pulled | at the clothesline, between "pověsíme ponožku" and "past je hotová" (**wired in**) |
| 2 Klíč | **Kam svítí hvězdička**: turn mirrors so the morning sun lands on the 7th plank; owlets must not be woken (3 levels) | cause and effect, trying ideas | attic, morning, before counting the planks |
| 3 Rybník | **Dvacet dětských kroků**: plan the steps from the stump to the star stone, then press Jdi! The last level is exactly 20 steps, like the map | sequencing, first programming | at the stump, after děda's steps land him in the pond |

## Story 1 – Záhada zmizelých ponožek (exists, to polish)
Possible second minigame: **Mouka ze spíže**. Babička gives picture clues ("není nahoře", "vedle medu") and the
player finds the right jar on the pantry shelf. It is deduction, and the clues are pictures, so Hanka can play too.

## Story 2 – Tajemství starého klíče (built)
Rooms: **Loznice** (noc) · **Snidane** (kuchyně) · **Stit** (zahrada pod okýnkem) · **Puda** (tma → ráno).
Built as described below. In the game the mirrors minigame throws the star of light on the floor, and Hanka then
counts the 7 planks. The flashback is six "old photo" slides (`art/story2.py`) that děda narrates.
1. Night, bedroom: noises (ťuk, šššš, chrrr). Clicking the ceiling adds each noise to the notebook.
2. Breakfast: děda doesn't want to go up. Babička hints why.
3. Under the attic window: Hanka finds the feather, Alica uses the magnifier on the pellets. False leads Micka and Joey get crossed out.
4. Show děda the star key → he fetches the ladder. Only together: děda holds the ladder, Hanka goes first with the torch.
5. Dark attic: the torch follows the mouse (as in the shed) → the chest with the star. Using the key opens it: notebook, badge, half a map.
6. Flashback cutscene (Klub Hvězdička). The riddle goes into the notebook.
7. Noises again: the torch finds the owl and three owlets. A short owl fact for the kids.
8. Morning: **Kam svítí hvězdička** (mirrors). Hanka counts 7 planks (click them in order, she says the numbers).
9. The seventh plank is under the low roof: only Hanka fits → the tin with Věrka's half.
10. The halves join → the owl box: build it (děda holds, the girls hammer, like the birdhouse nails) → "Pokračování příště".

## Story 3 – Mapa ke starému rybníku (built)
Rooms: **Kuchyne3** (the map; the evening quarrel) · **Rybnik** (day, and dawn with the torch) · **Mlyn** (bench, reveal,
treasure). New characters Věrka and Rybář (`art/story3.py`). Minigames: Dvacet dětských kroků, **Čí je to stopa?**
(`prints.gd`), **Kdo to byl?** (`culprit.gd`, the STOP page). Ends with Franta's picture letter in the inventory for story 4.
1. Kitchen: the map (clickable parts: willow, footprints, X). Tonda peeks over the fence (only visible, never mentioned).
2. Pond: three willows. Talk to děda → the stump. Děda's big steps end in the pond (cutscene).
3. **Dvacet dětských kroků** → the star stone (Hanka must look low: switch to Hanka).
4. Joey digs → empty hole. Clues go into the notebook with the magnifier: boot prints, round dots.
5. Suspects: Tonda (runs off), the badger burrow, the fisherman ("ráno spím").
6. Evening quarrel (cutscene). Děda: "Klub drží spolu."
7. Dawn stakeout: the torch catches Tonda → his secret, and he joins the team.
8. **Čí je to stopa?** (second minigame): match each print in the mud to what made it (bird fork, badger claws, big boot, stick). Pictures only, logic by elimination.
9. Joey's nose → the bench by the mill. The stick and the lantern are clickable, but nobody comments.
10. **STOP, detektive!** In the game: pick the culprit from portraits and pin the evidence to them. A wrong pick is never "wrong": Alica explains which clue doesn't fit.
11. Hanka invites the lady → the riddle line → Věrka → the treasure opened together → Tonda gets the badge → "Pokračování příště".

## Stories 4–12 (built 2026-10-18)
Each story: three rooms that follow its comic, one **story minigame** whose rules come from the plot (like the flour
trap in story 1: you build the thing the detectives build), and one **Kdo to byl?** round (`whodunit.gd`, the comic's
STOP page: pick a suspect, a clue that doesn't fit rules them out, never "wrong"). Joey always hints.

| story | rooms | story minigame | why it fits |
|---|---|---|---|
| 4 Hanka to vyřeší! | Pokoj4 (Alica sick, vysílačka) · Ves4 · Pole4 · Molo4 | **Rozběhni hodiny** (`gears.gd`): put gears on pegs so the winding key turns the hands *clockwise*; neighbouring gears turn opposite ways, a gear squeezed between two that disagree jams | Franta brings back the winding key; the girls get the clock going after 60 years |
| 5 Kdo staví sněhuláky? | Zahrada5 (a new snowman each morning) · Ves5 (Bětka) · Franta5 · Kuchyne5 | **Postav sněhuláka** (`snowman.gd`): roll snowballs; they grow on fresh snow and leave a path; stack big, middle, small | Hanka answers Bětka's snowman letters with a snowman |
| 6 Kam mizí perníčky? | Kuchyne6 (the tin) · Zahrada6 (feeder) · Mlyn6 (the spruce) | **Hvězdy na smrčku** (`stars.gd`): a picture Latin square, every branch row and every column gets each ornament once | děda's club rule for the Advent stars |
| 7 Joeyho velký den | Zahrada7 (snow fort) · Kuchyne7 (babička lost her ring) · Les7 (hajný) | **Čmuchej!** (`sniff.gd`): Joey sniffs snow squares; paws show how close the smell is; find the ring in few sniffs | the whole issue is Joey's nose |
| 8 Stopy ve sněhu | Kuchyne8 · Zahrada8 (snowmen without noses) · Louka8 (tracks) · Les8 (krmelec) | **Po stopě** (`trail.gd`): follow one animal's prints across a field where trails cross; only the right kind of print may follow | the hajný's track lesson |
| 9 Tajná zpráva v knihovně | Kuchyne9 (hub) · Knihovna9 · Mlyn9 · Masopust9 | **Hvězdičkové písmo** (`cipher.gd`): decode the slip with the key (shape = letter group, dots = which letter), then write the answer | the club's star code |
| 10 Záhada ve škole | Skola10 (jurty, empty hutch) · Kumbal10 · Domov10 | **Nový kotec** (`hutch.gd`): fit plank pieces into the hutch frame (turn and place) | the field day builds a new hutch |
| 11 Kam mizí vajíčka? | Dvur11 · Kurnik11 · Stodola11 · Kuchyne11 | **Balíky slámy** (`bales.gd`): slide bales (each only along its length) to open the way to the hidden nest | Kropenatka's nest behind the bales |
| 12 Tajemné šipky | Chalupa12 (kůlna, mouka) · Ves12 (our street) · Chodba12 (stairs) · Zahrada12 (the party) | **Otoč šipky** (`arrows.gd`): the rain smudged the chalk arrows; turn them so one trail leads from the door past every star to the garden gate. Kdo to byl? runs three times, once per arrow style (`who_12.gd`, `kind`) | máma, táta and Hanka lay the arrow trail |

### Second puzzles (2026-10-18)
Each story 4–12 also has a second logic puzzle that comes out of its plot. Five of them share `rules.gd`: put
things in places by picture rule cards (is / is not / side by side / not side by side / before / at an end),
data in each puzzle's `LEVELS`, exactly one answer per level (checked by `tools/rules_solver.py`).

| story | puzzle | where it happens |
|---|---|---|
| 4 | **Navigace vysílačkou** (`radio.gd`): Hanka walks straight until a rock, bush or the brook stops her; radio her to the Bota rock | Pole4, day 2, on the way to the Bota |
| 5 | **Čí je rukavice?** (`mittens.gd`, rules): the wet mittens by the stove got mixed up | Kuchyne5, right after babička is cleared |
| 6 | **Kdo co zobe?** (`birds.gd`, rules): each bird at the new feeder gets its food | Zahrada6, when the feeder goes up |
| 7 | **Co se ráno dělo?** (`joey_morning.gd`, rules): put the true morning in order from what everyone says | Kuchyne7, the evening the ring is gone |
| 8 | **Seno do krmelce** (`scale.gd`): split hay bundles (dots on the tag = weight) evenly between the two racks | Les8, before the food for the deer |
| 9 | **Masopustní průvod** (`parade.gd`, rules): line up the masks | Masopust9, before "Kdo napsal zprávu?" |
| 10 | **Ohrádky pro morčata** (`pens.gd`): split the meadow into rectangles, one guinea pig each, the number = squares | Skola10, after the new hutch |
| 11 | **Kraslice podle vzoru** (`pattern.gd`): fill the gaps so each egg row repeats | Kuchyne11, after the dyeing |
| 12 | **Kdo kde sedí?** (`seating.gd`, rules): seat the guests by their wishes | Zahrada12, after PŘEKVAPENÍ |

`game/tests/story_mg2.gd` plays all of them headless (`tools/test_story.sh mg2`).

## Shared work before stories 2 and 3
- Per-story state: story 1's flags now sit in `Globals`. Give each story its own flag set.
- Saving: autosave on room change plus "Pokračovat" in the main menu (still open from the story 1 status).
- A notebook screen (clues and suspects filling in): stories 2 and 3 lean on it heavily.
- Reuse: the torch light (shed → attic, dawn), the plank counting, the nails minigame, and the art in `attic.py` and `pond.py`.
