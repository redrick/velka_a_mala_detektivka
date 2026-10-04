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

## Shared work before stories 2 and 3
- Per-story state: story 1's flags now sit in `Globals`. Give each story its own flag set.
- Saving: autosave on room change plus "Pokračovat" in the main menu (still open from the story 1 status).
- A notebook screen (clues and suspects filling in): stories 2 and 3 lean on it heavily.
- Reuse: the torch light (shed → attic, dawn), the plank counting, the nails minigame, and the art in `attic.py` and `pond.py`.
