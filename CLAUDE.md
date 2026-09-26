# Velká a malá detektivka – point-and-click game

A small 2D point-and-click adventure for two sisters: **Alica (7)** and **Hanka (4)**. It is based on
the printed comic *Velká a malá detektivka*, issue 1, "Záhada zmizelých ponožek". The goal is to get
the girls onto the computer through play. Later, Alica may help build the game herself.

## Tech stack
- **Godot 4.6.3**, run as the official portable binary. Arch's pacman ships 4.7, but Popochiu
  only officially supports 4.6. Download `Godot_v4.6.3-stable_linux.x86_64.zip` from
  https://github.com/godotengine/godot-builds/releases, unzip it (for example to ~/apps/godot-4.6/) and run it directly.
  It can live alongside the system 4.7. The project file is pinned to 4.6; open it only with 4.6.3 until Popochiu
  lists 4.7 support.
- **Popochiu 2.1.1** (point-and-click plugin, MIT): https://github.com/carenalgas/popochiu/releases.
  It provides Rooms, Characters, Props, Hotspots, Inventory, Dialogs, audio and save/load.
- Optional experiment: try the same project on Godot 4.7 in a separate git branch. If the plugin loads cleanly,
  we can move up later.
- GDScript only, no C#.
- Export targets: first Linux/Windows desktop, then an Android tablet and Web.
  (Export templates must match the editor version: download the 4.6.3 templates.)

## Repo layout
- `comics/<series>/` – finished comic issues (`<nn>_<title>.pdf` and the printable `_BROZURA.pdf`).
  How to make the next issue: `docs/comic-workflow.md`.
- `game/` – the Godot project (`project.godot`). Popochiu's own content lives in `game/game/`
  (Popochiu hardcodes `res://game/`): rooms, characters, inventory items, GUI, autoloads.
- `game/assets/` – exported PNGs, written by `art/export_assets.py`.
- `game/addons/popochiu/` – vendored Popochiu 2.1.1, don't edit.
- GUI template: `simple_click_high_res` (left click = interact, right click = look).
- Game-progress flags live in `game/game/popochiu_globals.gd` (`Globals`), which Popochiu saves automatically.
- Cutscenes that span rooms set `Globals.phase`. The next room stages it in `_on_room_entered` and plays it
  in `_on_room_transition_finished`, because a script stops when `R.goto_room` frees its room.
- Characters extend `game/game/characters/animated_character.gd` (set `sprite_prefix`/`default_mood` in the
  scene). It swaps `assets/characters/<prefix>_<mood>.png` frames: `_walk` while walking, `_talk` while talking,
  plus a bob. `C.Alica.pose("lens")` holds a pose, `pose()` returns to default. New Popochiu characters need
  their `extends` line changed and `_talk`/`_walk` frames exported. Don't override `_process` in characters:
  Popochiu uses it for following and turns it off, so the animation runs in a child ticker node.
- Logic tests: run the game `--headless` with a temporary autoload that calls `obj._on_click()` directly
  (switch text to automatic first, see In-game menu).
- Night/evening lighting is done at runtime (`CanvasModulate` + `PointLight2D`), not with separate PNGs.
- Either sister can be the player: clicking the other one calls `Globals.switch_to()`. Use `C.player` for
  "whoever is playing", `Globals.sister()` for the other one, and `Globals.bring_sister(room)` on room entry.
  Scripted moves off the walkable area (fence gap, stepping stones) use `ignore_walkable_areas`.

Run: `~/apps/godot-4.6/Godot_v4.6.3-stable_linux.x86_64 --path game` (add `-e` for the editor).
Parse check without a window: `... --headless --editor --quit-after 300 --path game`.

## Series and stories (the long-term plan)
The game mirrors the printed comics: **several series, each with about 16 stories**, and every comic
issue gets a matching playable story. "Velká a malá detektivka" is series 1 (`docs/series-plan.md`).
- The main scene is the Popochiu room `Menu`, which shows the menu: pick a series, then a story.
  The catalog is `game/game/menu/series.json`. A story with `start_room` (and ideally `cover`) is
  playable; the others show as "Brzy".
- To add a story: build its rooms, draw a cover in `art/menu.py` (`ep_<series>_<nn>`), and add
  `start_room` and `cover` to its entry in `series.json`. To add a series: add a series entry with its cover.
- `Globals.start_episode(room)` starts fresh (flags, inventory, room states, fresh character instances).
  `Globals.go_to_menu()` returns. The house button (autoload `Home`) asks before leaving a story.
- `Globals` currently holds story 1's flags. When story 2 arrives, give each story its own state.

## Languages (Czech + English)
Every text the player sees exists in Czech and English, switchable in the main menu and the in-game menu
(remembered in `user://settings.cfg` by the `Lang` autoload).
- Write texts **in Czech** in the code. The Czech text is the translation key, stored in
  `game/game/i18n/strings.csv` (columns keys, cs, en).
- `say("…")` lines are translated by the character base, hover names by the hover component, and code
  texts must use `tr("…")`. Popochiu's own `use_translations` stays **off**: it rewrites descriptions to
  scene-prefixed keys.
- **After adding or changing any text**, run `python3 tools/i18n.py`. It adds new keys to the CSV and lists
  those still missing English; fill in the `en` column, then run `godot --headless --import`.
- Keep one text per key. Split multi-line texts into separate labels instead of using `\n` in a key.

## In-game menu
`InGameMenu` autoload (`game/game/menu/ingame_menu.gd`), opened by the house button bottom-left or the top
bar's house icon: Pokračovat, text continues on click / automatically (**default: on click**), text speed
(slow/normal/fast), language, Historie (lines spoken in this story, shown in the current language),
Hlavní menu (with confirm). Text options live in the `Prefs` autoload and are
saved to `user://settings.cfg`. Popochiu's own settings popup (save slots, volume, history) isn't reachable.
All menus share `game/game/menu/ui_kit.gd` for the look.
- Scripted tests must call `Prefs.set_auto_continue(true)` (and set it back), otherwise every `say()` waits
  for a click.

## Design rules (important – players are 7 and 4)
- **Czech language everywhere.** Alica reads a little, Hanka can't read. Subtitles are large
  (`art/fonts/ShantellHand.ttf`). No voiceover: a TTS + in-game recorder version was tried and dropped
  (sounded bad); a parent reads along for Hanka.
- **Single-click interaction.** Clicking does the obvious thing (look/take/use/talk).
  Use no verb menus. Pick the simplest Popochiu GUI template, or write a custom one.
- Big hotspots. Show a hover highlight and a hand cursor.
- **No fail states and no time pressure.** Nothing is scary. Every "culprit" is an animal or a kind person.
- **Hint system.** Clicking Joey the dog makes him sniff and walk towards the next goal, and he says "Čmuch čmuch!".
- The player can switch between Alica and Hanka. Some puzzles need Hanka, because she is small
  (for example, the gap in the fence).
- Save automatically on every room change.

## Characters (see art/ – drawn in code, exported to PNG)
| id | who | notes |
|---|---|---|
| alica | 7 y, long straight light-brown, almost blonde hair with a side parting and clip, light raincoat, striped tights, boots | carries the magnifier (lupa) and notebook |
| hanka | 4 y, curly shoulder-length hair with nothing in it, dungarees, striped top | always carries her plush orangutan (opička); has a torch (baterka) |
| joey | black & white border collie | the real family dog; hint giver |
| babicka, deda | grandparents at the cottage (chalupa) | děda's flat cap and beard; babička's glasses and bun |
| tonda | neighbour boy (~8) | hoodie with a star |
| micka (cat), straka (magpie), plši (dormice) | animals | the dormice are the "thieves" |

## Art pipeline
`art/` holds the Python drawing library used for the comic:
- lib.py: base geometry
- style3.py: hand-inked lines, Alica, Hanka and Joey
- chars3.py: other characters and props
- scenes3.py: backgrounds
- props_extra.py: extra props
- palette.py: game colours (see below)
- interior.py, outdoor.py: game-only rooms (kitchen, zahumenek)
- letter.py: hand lettering, speech balloons and panels

To set it up and export the art:
```
cd art && python -m venv .venv && .venv/bin/pip install -r requirements.txt
.venv/bin/python export_assets.py        # colour -> ../game/assets/{characters,props,rooms}/*.png (transparent)
.venv/bin/python export_assets.py --bw   # greyscale, as printed
.venv/bin/python comic_issue1.py         # rebuilds the B&W comic PDF into comics/velka_a_mala_detektivka/
.venv/bin/python make_booklet.py <issue>.pdf <issue>_BROZURA.pdf   # A5 saddle-stitch booklet for printing
```
After re-exporting, run `godot --headless --import --path game` so Godot picks up the new PNGs.
- Style: clean "ligne claire" with a hand-inked wobble, flat fills and hatched ground shadows.
- **Colour lives in `art/palette.py`.** Each entry is `Col(grey, "#hex")`: the comic (printed on a B&W laser
  printer) uses the grey, the game uses the hex. Pass palette constants (`P.ALICA_COAT`) instead of grey
  literals when drawing anything new. Change a colour there, never by recolouring PNGs. The palette's grey must
  equal the literal it replaces, so `--bw` output keeps the comic's tones.
- `export_assets.py` seeds the hand wobble from each asset's name, so adding an asset doesn't change the others.
- To add a pose or asset, add an entry in `export_assets.py`. The character functions take
  `mood=` (happy, grin, surprised, wow, think, worried, whisper, determined, sleepy),
  `right=/left=` arm poses (down, wave, up, lens, point, hip, front, chin, hush, hold, hug), and `legs="walk"`.
- For walk and talk animation, prefer exporting body parts separately and animating them as a
  cut-out in Godot (AnimationPlayer). A 2–4 frame bob is fine for a first version.
- Rooms are 960x540 pt, rendered at 2x, which gives 1920x1080.

## First milestone: "Záhada zmizelých ponožek" playable (see docs/game-design.md)
5 rooms, ~4 puzzles, about 15–20 minutes of play.
