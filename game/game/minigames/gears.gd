extends "res://game/minigames/minigame_base.gd"
## Story 4 "Rozběhni hodiny": the church clock's works lie in pieces. Put gears on the pegs so the winding
## key turns the clock hands *clockwise*. Gears that touch turn opposite ways, so it matters how many
## gears are in the chain; three gears that all touch each other jam (SKŘÍP!). The pegs sit on a
## honeycomb, so there are short and long ways round. Click a peg to put a gear on it or take it off;
## arrows + Enter do the same. The gears turn as soon as they are connected.
## Levels: K the key gear (turns clockwise), H clock hands (must turn clockwise), F a gear that is
## already there, . an empty peg, space = nothing. Odd rows sit half a step to the right.

const LEVELS := [
	[
		"K..H",
		"... ",
	],
	[
		"..F..",
		"K...H",
		".....",
	],
	[
		"H...",
		"....",
		"K...",
		"....",
		"...H",
	],
]
const SPARE := [3, 4, 5]
const HINTS := [
	"Klíč se točí doprava. Další kolečko doleva, další zase doprava… Ručičky musí doprava!",
	"Tři kolečka, která se všechna dotýkají, se zaseknou. Zkus jít kolem dokola.",
	"Ručičky jsou dvoje a obě se musí točit doprava. Počítej pro každé zvlášť.",
]
const SPEED := 1.6

var _pegs := {}        # Vector2i -> kind: "." empty peg, "K", "H", "F"
var _gears := {}       # Vector2i -> TextureRect (placed gears, and K/H/F)
var _placed: Array[Vector2i] = []
var _history: Array = []
var _spare := 0
var _left: Label
var _cursor := Vector2i.ZERO
var _frame: Panel
var _dirs := {}        # Vector2i -> 1 (clockwise) / -1, for gears turning now
var _jam := false
var _arrows: Array = []
var _won := false


func _title() -> String: return tr("Rozběhni hodiny")
func _task_text() -> String: return tr("Dej kolečka na kolíčky. Klíč musí roztočit ručičky doprava, jako jdou hodiny!")
func _levels() -> int: return LEVELS.size()


func _build(i: int) -> void:
	tile = 128.0
	_pegs.clear(); _gears.clear(); _placed.clear(); _history.clear(); _dirs.clear(); _arrows.clear()
	_jam = false
	_won = false
	_spare = SPARE[i]
	var rows: Array = LEVELS[i]
	var cols := 0
	for r in rows.size():
		cols = maxi(cols, (rows[r] as String).length())
		for c in (rows[r] as String).length():
			var ch: String = rows[r][c]
			if ch != " ":
				_pegs[Vector2i(c, r)] = ch
	board.custom_minimum_size = Vector2((cols + 0.5) * tile, ((rows.size() - 1) * 0.866 + 1) * tile)
	board.size = board.custom_minimum_size
	var wall := TextureRect.new()
	wall.texture = load(ART + "tower_wall.png")
	wall.stretch_mode = TextureRect.STRETCH_TILE
	wall.size = board.size
	wall.mouse_filter = Control.MOUSE_FILTER_IGNORE
	board.add_child(wall)
	for p in _pegs:
		_tex("peg", p, 0.55, 1)
		match _pegs[p]:
			"K": _gears[p] = _tex("gear_key", p, 1.12, 3)
			"H": _gears[p] = _tex("gear_hands", p, 1.12, 3)
			"F": _gears[p] = _tex("gear_fixed", p, 1.12, 3)
		if _pegs[p] == "K":
			_cursor = p
	_left = Kit.label("", 32)
	extra_node(_left)
	_frame = frame()
	_frame.size = Vector2(tile, tile) * 1.1
	_update()


func _tex(name: String, p: Vector2i, k: float, z: int) -> TextureRect:
	var t := TextureRect.new()
	t.texture = load(ART + name + ".png")
	t.expand_mode = TextureRect.EXPAND_IGNORE_SIZE
	t.stretch_mode = TextureRect.STRETCH_KEEP_ASPECT_CENTERED
	t.size = Vector2(tile, tile) * k
	t.pivot_offset = t.size / 2.0
	t.position = _center(p) - t.size / 2.0
	t.z_index = z
	t.mouse_filter = Control.MOUSE_FILTER_IGNORE
	board.add_child(t)
	return t


func _center(p: Vector2i) -> Vector2:
	return Vector2((p.x + 0.5 * (p.y % 2) + 0.5) * tile, (p.y * 0.866 + 0.5) * tile)


## The six honeycomb neighbours (odd rows are shifted right).
static func neighbours(p: Vector2i) -> Array[Vector2i]:
	var odd := p.y % 2 == 1
	var out: Array[Vector2i] = [p + Vector2i(-1, 0), p + Vector2i(1, 0)]
	for dy in [-1, 1]:
		if odd:
			out += [p + Vector2i(0, dy), p + Vector2i(1, dy)]
		else:
			out += [p + Vector2i(-1, dy), p + Vector2i(0, dy)]
	return out


## Which way every gear connected to the key turns; {} plus jam=true when two touching gears
## would have to turn the same way. Static so the hint solver can try placements.
static func spin(pegs: Dictionary, filled: Dictionary) -> Dictionary:
	var start := Vector2i(-99, -99)
	for p in pegs:
		if pegs[p] == "K":
			start = p
	var dirs := {start: 1}
	var queue: Array[Vector2i] = [start]
	var jam := false
	while not queue.is_empty():
		var p: Vector2i = queue.pop_front()
		for n in neighbours(p):
			if not filled.has(n):
				continue
			if not dirs.has(n):
				dirs[n] = -dirs[p]
				queue.append(n)
			elif dirs[n] == dirs[p]:
				jam = true
	return {"dirs": dirs, "jam": jam}


static func solved(pegs: Dictionary, filled: Dictionary) -> bool:
	var s := spin(pegs, filled)
	if s.jam:
		return false
	for p in pegs:
		if pegs[p] == "H" and s.dirs.get(p, 0) != 1:
			return false
	return true


func _filled() -> Dictionary:
	var f := {}
	for p in _pegs:
		if _pegs[p] != "." or p in _placed:
			f[p] = true
	return f


func _update() -> void:
	_left.text = tr("Zbývá koleček: %d") % (_spare - _placed.size())
	_frame.position = _center(_cursor) - _frame.size / 2.0
	for a in _arrows:
		a.queue_free()
	_arrows.clear()
	var s := spin(_pegs, _filled())
	_jam = s.jam
	_dirs = {} if _jam else s.dirs
	for p in _gears:
		(_gears[p] as Control).modulate = Color(1, 0.6, 0.6) if _jam and s.dirs.has(p) else Color.WHITE
	for p in _pegs:
		if _pegs[p] == "H" and s.dirs.has(p) and not _jam:
			var a := _tex("turn_cw" if s.dirs[p] == 1 else "turn_ccw", p, 0.9, 6)
			a.position.y -= tile * 0.62
			_arrows.append(a)
	if _jam:
		say("SKŘÍP! Kolečka se zasekla. Tři kolečka, která se dotýkají, se točit nemůžou.")
	elif solved(_pegs, _filled()) and not _won:
		_won = true
		level_done("Ručičky jdou doprava! Tik tak!")
	else:
		var backwards := false
		for p in _pegs:
			if _pegs[p] == "H" and s.dirs.get(p, 0) == -1:
				backwards = true
		say("Ručičky jdou pozpátku! Zkus to jinudy." if backwards else "")


func _process(delta: float) -> void:
	if busy and not _won:
		return
	for p in _dirs:
		if _gears.has(p):
			(_gears[p] as Control).rotation += _dirs[p] * SPEED * delta


func _toggle(p: Vector2i) -> void:
	if not _pegs.has(p) or _pegs[p] != "." or _won:
		return
	if p in _placed:
		_placed.erase(p)
		(_gears[p] as Node).queue_free()
		_gears.erase(p)
	elif _placed.size() < _spare:
		_placed.append(p)
		_gears[p] = _tex("gear", p, 1.12, 3)
	else:
		say("Už nemáš žádné kolečko. Nějaké vezmi zpátky.")
		return
	_history.append(p)
	_update()


func _on_board_input(event: InputEvent) -> void:
	if busy:
		return
	if event is InputEventMouseButton and event.pressed and event.button_index == MOUSE_BUTTON_LEFT:
		var best := Vector2i(-1, -1)
		var dist := tile * 0.55
		for p in _pegs:
			var d := _center(p).distance_to(event.position)
			if d < dist:
				dist = d
				best = p
		if best.x >= 0:
			_cursor = best
			_toggle(best)


func _dir(d: Vector2i) -> void:
	var from := _center(_cursor)
	var want := Vector2(d)
	var best := _cursor
	var score := INF
	for p in _pegs:
		var v := _center(p) - from
		if v.length() < 1.0 or v.normalized().dot(want) < 0.5:
			continue
		if v.length() < score:
			score = v.length()
			best = p
	_cursor = best
	_update()


func _action() -> void:
	_toggle(_cursor)


func _undo() -> void:
	if _history.is_empty():
		return
	var p: Vector2i = _history.pop_back()
	if p in _placed:
		_placed.erase(p)
		(_gears[p] as Node).queue_free()
		_gears.erase(p)
	else:
		_placed.append(p)
		_gears[p] = _tex("gear", p, 1.12, 3)
	_update()


## Joey's hint: the level's tip, and a peg that belongs to a solution flashes.
func _hint() -> void:
	say(HINTS[level])
	var sol := _solve()
	for p in sol:
		if not p in _placed:
			var f := frame(Color("6cbf5a"))
			f.size = Vector2(tile, tile)
			f.position = _center(p) - f.size / 2.0
			var tw := create_tween()
			tw.tween_interval(1.6)
			tw.tween_callback(f.queue_free)
			return


## The smallest set of pegs that makes the clock run (tries 1, 2, … gears).
func _solve() -> Array:
	var free: Array = []
	for p in _pegs:
		if _pegs[p] == ".":
			free.append(p)
	for n in range(0, SPARE[level] + 1):
		var found := _combo(free, n, 0, [])
		if not found.is_empty() or n == 0 and solved(_pegs, _base_filled([])):
			return found
	return []


func _base_filled(extra: Array) -> Dictionary:
	var f := {}
	for p in _pegs:
		if _pegs[p] != ".":
			f[p] = true
	for p in extra:
		f[p] = true
	return f


func _combo(free: Array, n: int, start: int, chosen: Array) -> Array:
	if chosen.size() == n:
		return chosen.duplicate() if solved(_pegs, _base_filled(chosen)) and n > 0 else []
	for k in range(start, free.size()):
		chosen.append(free[k])
		var r := _combo(free, n, k + 1, chosen)
		chosen.pop_back()
		if not r.is_empty():
			return r
	return []


func solve_for_test() -> void:
	for p in _solve():
		_toggle(p)
