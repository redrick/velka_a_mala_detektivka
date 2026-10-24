extends "res://game/minigames/minigame_base.gd"
## Story 6 "Hvězdy na smrčku": Klub Hvězdička's old Advent rule for the big spruce, as děda tells it:
## on every branch (row) each kind of ornament hangs once, and the same kind never hangs twice one above
## the other (column). A picture Latin square: stars, chocolate hearts, moons, and the seed stars for the
## birds. Some ornaments already hang (they can't be moved). Click a free spot to change what hangs
## there (nothing → star → heart → …); arrows + Enter do the same. Two of a kind in a row or column turn red.
## Levels: S star, H heart, M moon, Z seed star, . free. Each level has exactly one solution
## (tools/check_levels.py checks it).

const LEVELS := [
	[
		"S..",
		".H.",
		"...",
	],
	[
		"S.M.",
		"..Z.",
		".H..",
		"...S",
	],
	[
		"S..H",
		"H...",
		"....",
		".M..",
	],
]
const KINDS := ["S", "H", "M", "Z"]
const TEX := {"S": "orn_star", "H": "orn_heart", "M": "orn_moon", "Z": "orn_seed"}
const NAMES := {"S": "hvězdička", "H": "srdíčko", "M": "měsíček", "Z": "zrníčková hvězda"}

var _n := 3
var _grid := {}        # Vector2i -> kind or ""
var _fixed := {}
var _nodes := {}       # Vector2i -> TextureRect
var _marks := {}       # Vector2i -> ColorRect (red)
var _cursor := Vector2i.ZERO
var _frame: Panel
var _history: Array = []
var _won := false


func _title() -> String: return tr("Hvězdy na smrčku")
func _task_text() -> String:
	return tr("Na každé větvi visí od každého druhu jedna. A nad sebou nikdy dvě stejné! Klikni na volné místo.")
func _levels() -> int: return LEVELS.size()


func _build(i: int) -> void:
	tile = 150.0
	_grid.clear(); _fixed.clear(); _nodes.clear(); _marks.clear(); _history.clear()
	_won = false
	var rows: Array = LEVELS[i]
	_n = rows.size()
	set_board_size(_n, _n)
	for y in _n:
		for x in _n:
			var c := Vector2i(x, y)
			piece("branch", c)
			var ch: String = rows[y][x]
			_grid[c] = "" if ch == "." else ch
			if ch != ".":
				_fixed[c] = true
				var pin := ColorRect.new()
				pin.color = Color(1, 1, 1, 0.18)
				pin.size = Vector2(tile, tile)
				pin.position = cell_pos(c)
				pin.mouse_filter = Control.MOUSE_FILTER_IGNORE
				board.add_child(pin)
	_cursor = Vector2i.ZERO
	_frame = frame()
	var legend := HBoxContainer.new()
	legend.add_theme_constant_override("separation", 30)
	for k in KINDS.slice(0, _n):
		var t := TextureRect.new()
		t.texture = load(ART + TEX[k] + ".png")
		t.expand_mode = TextureRect.EXPAND_IGNORE_SIZE
		t.stretch_mode = TextureRect.STRETCH_KEEP_ASPECT_CENTERED
		t.custom_minimum_size = Vector2(64, 64)
		legend.add_child(t)
	extra_node(legend)
	_draw()


func _draw() -> void:
	for c in _grid:
		var k: String = _grid[c]
		if _nodes.has(c):
			_nodes[c].queue_free()
			_nodes.erase(c)
		if k != "":
			_nodes[c] = piece(TEX[k], c, 2)
	for m in _marks.values():
		m.queue_free()
	_marks.clear()
	for c in _clashes():
		var r := ColorRect.new()
		r.color = Color(0.9, 0.2, 0.2, 0.35)
		r.size = Vector2(tile, tile)
		r.position = cell_pos(c)
		r.z_index = 3
		r.mouse_filter = Control.MOUSE_FILTER_IGNORE
		board.add_child(r)
		_marks[c] = r
	_frame.position = cell_pos(_cursor)


## The places that share their kind with another one in the same row or column.
func _clashes() -> Array:
	var out := []
	for c in _grid:
		var k: String = _grid[c]
		if k == "":
			continue
		for o in _grid:
			if o != c and _grid[o] == k and (o.x == c.x or o.y == c.y):
				out.append(c)
				break
	return out


func _full() -> bool:
	for c in _grid:
		if _grid[c] == "":
			return false
	return true


func _cycle(c: Vector2i) -> void:
	if _won or not _grid.has(c):
		return
	if _fixed.has(c):
		say("Tahle už visí. Tu nech být.")
		return
	_history.append([c, _grid[c]])
	var order: Array = [""] + KINDS.slice(0, _n)
	_grid[c] = order[(order.find(_grid[c]) + 1) % order.size()]
	_draw()
	var bad := _clashes()
	if not bad.is_empty():
		say("Dvě stejné na jedné větvi nebo nad sebou. To pravidlo nedovolí!")
	elif _full():
		_won = true
		level_done("Smrček je ozdobený podle pravidla Klubu Hvězdička!")
	else:
		say("")


func _cell(c: Vector2i) -> void:
	_cursor = c
	_cycle(c)


func _dir(d: Vector2i) -> void:
	_cursor = Vector2i(clampi(_cursor.x + d.x, 0, _n - 1), clampi(_cursor.y + d.y, 0, _n - 1))
	_draw()


func _action() -> void:
	_cycle(_cursor)


func _undo() -> void:
	if _history.is_empty():
		return
	var h: Array = _history.pop_back()
	_grid[h[0]] = h[1]
	_won = false
	_draw()


func _can(c: Vector2i, k: String) -> bool:
	for o in _grid:
		if o != c and _grid[o] == k and (o.x == c.x or o.y == c.y):
			return false
	return true


## A free place and the one kind that must go there: either nothing else fits there, or on its
## branch (or in its column) that kind fits nowhere else. [] when there is no such place.
func _forced() -> Array:
	var kinds: Array = KINDS.slice(0, _n)
	for c in _grid:
		if _grid[c] != "":
			continue
		var can := kinds.filter(func(k): return _can(c, k))
		if can.size() == 1:
			return [c, can[0], "cell"]
	for line in range(_n):
		for k in kinds:
			for vertical in [false, true]:
				var spots := []
				var done := false
				for j in range(_n):
					var c := Vector2i(line, j) if vertical else Vector2i(j, line)
					if _grid[c] == k:
						done = true
					elif _grid[c] == "" and _can(c, k):
						spots.append(c)
				if not done and spots.size() == 1:
					return [spots[0], k, "column" if vertical else "row"]
	return []


## Joey points at a free place where only one kind can hang, and says which.
func _hint() -> void:
	for c in _clashes():
		if not _fixed.has(c):
			_cursor = c
			_draw()
			say("Tady něco nesedí. Podívej se na větev a nad sebe.")
			return
	var f := _forced()
	if f.is_empty():
		say("Najdi větev, kde chybí jen jedna ozdoba.")
		return
	_cursor = f[0]
	_draw()
	match f[2]:
		"cell": say(tr("Sem patří jen jedno: %s.") % tr(NAMES[f[1]]))
		"row": say(tr("Na téhle větvi se %s vejde jen sem.") % tr(NAMES[f[1]]))
		_: say(tr("V tomhle sloupci se %s vejde jen sem.") % tr(NAMES[f[1]]))


func solve_for_test() -> void:
	var guard := 0
	while not _won and guard < 64:
		guard += 1
		var f := _forced()
		if f.is_empty():
			return
		while _grid[f[0]] != f[1]:
			_cycle(f[0])
		await get_tree().process_frame
