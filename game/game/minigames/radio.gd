extends "res://game/minigames/minigame_base.gd"
## Story 4 "Navigace vysílačkou": Alica sees the field from the tower picture and radios Hanka the way to
## the Bota rock. Hanka is little and brave: told "doleva!", she walks left and keeps going until a rock,
## a bush or the brook stops her (or she reaches the Bota rock). Fewest calls wins nothing extra; any way
## there is fine. Arrows or the arrow buttons send a call; clicking a square in line with Hanka does too.
## Levels: H Hanka, B the Bota rock, o rock, * bush, ~ brook, . grass.
## tools/check_levels.py checks every level can be done (and how many calls it takes at least).

const LEVELS := [
	[
		"H...o",
		".....",
		"o..B.",
		"...o.",
	],
	[
		"....*.o",
		".***.H.",
		".......",
		"....o..",
		"...Bo..",
	],
	[
		"........",
		".......~",
		".....o..",
		"o*o.B.oH",
		"*..*...o",
		"....o...",
	],
]
const BLOCK := ["o", "*", "~"]
const CALL := {Vector2i.LEFT: "Doleva!", Vector2i.RIGHT: "Doprava!", Vector2i.UP: "Nahoru!", Vector2i.DOWN: "Dolů!"}
const ARROW_TEX := {Vector2i.RIGHT: "arrow", Vector2i.DOWN: "arrow_down", Vector2i.LEFT: "arrow_left", Vector2i.UP: "arrow_up"}

var _grid := {}
var _start := Vector2i.ZERO
var _goal := Vector2i.ZERO
var _at := Vector2i.ZERO
var _me: TextureRect
var _history: Array = []
var _calls := 0


func _title() -> String: return tr("Navigace vysílačkou")
func _task_text() -> String:
	return tr("Hanka jde rovně, dokud ji nezastaví kámen, keř nebo potok. Pošli ji vysílačkou až ke kameni Bota!")
func _levels() -> int: return LEVELS.size()


func _build(i: int) -> void:
	tile = 115.0
	_grid.clear(); _history.clear()
	_calls = 0
	var rows: Array = LEVELS[i]
	tile = minf(tile, 640.0 / rows.size())
	set_board_size(rows[0].length(), rows.size())
	for y in rows.size():
		for x in rows[y].length():
			var c := Vector2i(x, y)
			var ch: String = rows[y][x]
			_grid[c] = ch
			piece("grass" if (x + y) % 2 == 0 else "grass_b", c)
			match ch:
				"o": piece("rad_rock", c, 1)
				"*": piece("bush", c, 1)
				"~": piece("water", c, 1)
				"B":
					piece("rad_bota", c, 1); _goal = c
				"H": _start = c
	_at = _start
	_me = figure("res://assets/characters/hanka_radio.png", _start, tile * 1.2)
	for d in [Vector2i.LEFT, Vector2i.UP, Vector2i.DOWN, Vector2i.RIGHT]:
		var b := TextureButton.new()
		b.texture_normal = load(ART + ARROW_TEX[d] + ".png")
		b.ignore_texture_size = true
		b.stretch_mode = TextureButton.STRETCH_KEEP_ASPECT_CENTERED
		b.custom_minimum_size = Vector2(76, 76)
		b.pressed.connect(func(): if not busy: _dir(d))
		extra_node(b)


func _blocked(c: Vector2i) -> bool:
	return not _grid.has(c) or _grid[c] in BLOCK


## Where Hanka ends up when sent from `c` in direction `d`.
func _run(c: Vector2i, d: Vector2i) -> Vector2i:
	while not _blocked(c + d) and c != _goal:
		c += d
	return c


func _dir(d: Vector2i) -> void:
	if busy:
		return
	var to := _run(_at, d)
	say(CALL[d])
	if to == _at:
		bump(_me)
		say("Tudy to nejde, Hanka stojí u překážky.")
		return
	busy = true
	_history.append(_at)
	_calls += 1
	await slide(_me, figure_pos(to, _me), 0.18 * (to - _at).length()).finished
	_at = to
	busy = false
	if _at == _goal:
		level_done(tr("Hanka je u kamene Bota!") if level == _levels() - 1 else tr("Hanka je u cíle! Slyším tě, Hani!"))


func _cell(c: Vector2i) -> void:
	if c == _at or (c.x != _at.x and c.y != _at.y):
		say("Klikni na políčko v řadě nebo sloupci s Hankou. Nebo použij šipky.")
		return
	_dir(Vector2i(signi(c.x - _at.x), signi(c.y - _at.y)))


func _undo() -> void:
	if _history.is_empty() or busy:
		return
	_at = _history.pop_back()
	_me.position = figure_pos(_at, _me)
	say("")


## The fewest calls from where Hanka stands (breadth-first over stopping places).
func _plan() -> Array:
	var prev := {_at: null}
	var queue: Array = [_at]
	while not queue.is_empty():
		var c: Vector2i = queue.pop_front()
		if c == _goal:
			var path := []
			while prev[c] != null:
				path.push_front(prev[c][1])
				c = prev[c][0]
			return path
		for d in CALL:
			var n := _run(c, d)
			if n != c and not prev.has(n):
				prev[n] = [c, d]
				queue.append(n)
	return []


func _hint() -> void:
	var p := _plan()
	if p.is_empty():
		say("Zkus to znovu.")
		return
	say(tr("Čmuch! Zkus: %s") % tr(CALL[p[0]]))


func solve_for_test() -> void:
	for d in _plan():
		await _dir(d)
		while busy and not _at == _goal:
			await get_tree().process_frame
