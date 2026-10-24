extends "res://game/minigames/minigame_base.gd"
## Story 12 "Otoč šipky": máma, táta and Hanka lay a chalk-arrow trail for Alica's birthday, but the arrows
## point every which way. Turn them (click an arrow: a quarter turn) so the trail runs from the door past every
## paper star to the garden gate. The trail is drawn as far as it goes; it stops at a bush, at bare paving,
## at the edge, or where it would cross itself.
## Levels: D door (the trail leaves it to the right), G the gate, a arrow, s arrow with a star, # bush, . paving.
## tools/check_levels.py checks every level can be done.

const LEVELS := [
	[
		"Daas",
		"##.a",
		"Gaaa",
	],
	[
		"Daaas",
		"aa#aa",
		"saaaa",
		"G#...",
	],
	[
		"Daaa#a",
		"#s#aaa",
		"aaaas#",
		"a#.#aa",
		"aaGsaa",
	],
]
const DIRS: Array[Vector2i] = [Vector2i.RIGHT, Vector2i.DOWN, Vector2i.LEFT, Vector2i.UP]

var _g := {}             # Vector2i -> char
var _rot := {}           # Vector2i -> 0..3 (index into DIRS) for arrow cells
var _arrows := {}        # Vector2i -> TextureRect
var _size := Vector2i.ZERO
var _start := Vector2i.ZERO
var _trail: Array = []
var _cursor := Vector2i.ZERO
var _frame: Panel
var _history: Array = []
var _won := false


func _title() -> String: return tr("Otoč šipky")
func _task_text() -> String:
	return tr("Otoč šipky, ať cesta vede od dveří přes všechny hvězdy až k brance. Klikni na šipku a otočí se.")
func _levels() -> int: return LEVELS.size()


func _build(i: int) -> void:
	tile = 120.0
	_g.clear(); _rot.clear(); _arrows.clear(); _history.clear(); _trail.clear()
	_won = false
	var rows: Array = LEVELS[i]
	_size = Vector2i((rows[0] as String).length(), rows.size())
	set_board_size(_size.x, _size.y)
	var rd := RandomNumberGenerator.new()
	rd.seed = 77 + i
	for y in _size.y:
		for x in _size.x:
			var c := Vector2i(x, y)
			var ch: String = rows[y][x]
			_g[c] = ch
			match ch:
				"D": piece("arr_door", c); _start = c
				"G": piece("arr_gate", c)
				"#": piece("arr_bush", c)
				"s": piece("arr_star", c)
				_: piece("arr_tile", c)
			if ch == "a" or ch == "s":
				_rot[c] = rd.randi_range(0, 3)
				var t := piece("arr_arrow", c, 3)
				t.scale = Vector2(0.8, 0.8)
				_arrows[c] = t
	_cursor = _start + Vector2i.RIGHT
	if _missing(_follow()) == 0:
		_rot[_cursor] = (_rot[_cursor] + 1) % 4
	_frame = frame()
	_update()


func _update() -> void:
	for c in _arrows:
		(_arrows[c] as Control).rotation_degrees = 90.0 * _rot[c]
		(_arrows[c] as Control).modulate = Color.WHITE
	_frame.position = cell_pos(_cursor)
	var missing := _missing(_follow())
	var reached := missing >= 0
	for c in _trail:
		(_arrows[c] as Control).modulate = Color(0.55, 1.0, 0.55)
	if reached and missing == 0 and not _won:
		_won = true
		level_done("Cesta vede od dveří přes všechny hvězdy až k brance!")
	elif reached:
		if missing == 1:
			say("Cesta vede k brance, ale jedna hvězda chybí.")
		else:
			say("Cesta vede k brance, ale hvězdy chybí.")
	else:
		say("")


## Walks the trail from the door into _trail; true when it reaches the gate.
func _follow() -> bool:
	_trail.clear()
	var p := _start + Vector2i.RIGHT
	while _g.has(p) and not p in _trail:
		if _g[p] == "G":
			return true
		if not _rot.has(p):
			return false
		_trail.append(p)
		p += DIRS[_rot[p]]
	return false


## Stars the trail misses, or -1 when it doesn't reach the gate.
func _missing(reached: bool) -> int:
	if not reached:
		return -1
	var n := 0
	for c in _g:
		if _g[c] == "s" and not c in _trail:
			n += 1
	return n


func _rotate(c: Vector2i) -> void:
	if _won or not _rot.has(c):
		return
	_history.append([c, _rot[c]])
	_rot[c] = (_rot[c] + 1) % 4
	_update()


func _cell(c: Vector2i) -> void:
	if _g.has(c):
		_cursor = c
		if _rot.has(c):
			_rotate(c)
		else:
			_update()


func _dir(d: Vector2i) -> void:
	_cursor = Vector2i(clampi(_cursor.x + d.x, 0, _size.x - 1), clampi(_cursor.y + d.y, 0, _size.y - 1))
	_frame.position = cell_pos(_cursor)


func _action() -> void:
	_rotate(_cursor)


func _undo() -> void:
	if _history.is_empty() or _won:
		return
	var h: Array = _history.pop_back()
	_rot[h[0]] = h[1]
	_update()


## A working trail: a depth-first search over the arrow cells (the levels are small).
func _solve() -> Dictionary:
	var stars := []
	for c in _g:
		if _g[c] == "s":
			stars.append(c)
	var plan := {}
	if _search(_start + Vector2i.RIGHT, {}, plan, stars):
		return plan
	return {}


func _search(p: Vector2i, seen: Dictionary, plan: Dictionary, stars: Array) -> bool:
	if not _g.has(p):
		return false
	if _g[p] == "G":
		for s in stars:
			if not seen.has(s):
				return false
		return true
	if not _rot.has(p) or seen.has(p):
		return false
	seen[p] = true
	for k in 4:
		plan[p] = k
		if _search(p + DIRS[k], seen, plan, stars):
			return true
	plan.erase(p)
	seen.erase(p)
	return false


func _hint() -> void:
	var plan := _solve()
	for c in plan:
		if _rot[c] != plan[c]:
			_cursor = c
			_frame.position = cell_pos(c)
			say("Čmuch! Tuhle šipku otoč. Kam má vést další krok?")
			return
	say("Čmuch! Sleduj zelenou cestu od dveří.")


func solve_for_test() -> void:
	var plan := _solve()
	for c in plan:
		while _rot[c] != plan[c] and not _won:
			_rotate(c)
			await get_tree().process_frame
