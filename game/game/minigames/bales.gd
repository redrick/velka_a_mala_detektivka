extends "res://game/minigames/minigame_base.gd"
## Story 11 "Balíky slámy": in the dark barn something clucks behind the straw bales. Slide the bales so
## Hanka (with her torch) can crawl through to the gap on the right, where the hidden nest is. A bale
## only slides along its length: a lying one left and right, a standing one up and down. Click a bale,
## then click where it should slide (or use the arrows). Hanka herself only crawls left and right.
## Levels: H Hanka, letters = bales (2 or 3 long), . straw floor. The way out is to the right of Hanka's row.
## tools/check_levels.py solves every level.

const LEVELS := [
	[
		"BBB..",
		"H..A.",
		".D.A.",
		".D.CC",
	],
	[
		"FF.B..",
		".C.B..",
		"HC.AGE",
		"...AGE",
		"...DDD",
	],
	[
		"J.E.GG",
		"J.EBBD",
		"HCAF.D",
		".CAF.D",
		".CAKK.",
		".III..",
	],
]

var _size := Vector2i.ZERO
var _row := 0
var _pos := {}          # name -> Vector2i (top left cell)
var _len := {}
var _horiz := {}
var _nodes := {}
var _selected := "H"
var _frame: Panel
var _history: Array = []
var _won := false


func _title() -> String: return tr("Balíky slámy")
func _task_text() -> String:
	return tr("Odsuň balíky, ať Hanka proleze až doprava ke škvíře. Ležící balík jde jen do stran, stojící jen nahoru a dolů.")
func _levels() -> int: return LEVELS.size()


func _build(i: int) -> void:
	tile = 116.0
	_pos.clear(); _len.clear(); _horiz.clear(); _nodes.clear(); _history.clear()
	_won = false
	var rows: Array = LEVELS[i]
	_size = Vector2i((rows[0] as String).length(), rows.size())
	set_board_size(_size.x + 1, _size.y)
	var cells := {}
	for y in _size.y:
		for x in _size.x:
			var ch: String = rows[y][x]
			piece("bale_floor", Vector2i(x, y))
			if ch != ".":
				cells.get_or_add(ch, []).append(Vector2i(x, y))
	for n in cells:
		var cs: Array = cells[n]
		_pos[n] = cs[0]
		_len[n] = cs.size()
		_horiz[n] = cs.size() == 1 or cs[0].y == cs[1].y
		if n == "H":
			_row = cs[0].y
	for y in _size.y:
		piece("bale_wall" if y != _row else "bale_gap", Vector2i(_size.x, y))
	for n in _pos:
		_nodes[n] = _make(n)
	_selected = "H"
	_frame = frame()
	_draw()


func _make(n: String) -> TextureRect:
	var t: TextureRect
	if n == "H":
		t = figure("res://assets/characters/hanka_torch.png", _pos[n], tile * 1.0)
		t.z_index = 4
		return t
	t = TextureRect.new()
	t.texture = load(ART + ("bale_h" if _horiz[n] else "bale_v") + ".png")
	t.expand_mode = TextureRect.EXPAND_IGNORE_SIZE
	t.stretch_mode = TextureRect.STRETCH_SCALE
	t.mouse_filter = Control.MOUSE_FILTER_IGNORE
	t.z_index = 3
	board.add_child(t)
	return t


func _draw() -> void:
	for n in _pos:
		var t: TextureRect = _nodes[n]
		if n == "H":
			t.position = figure_pos(_pos[n], t)
			continue
		t.position = cell_pos(_pos[n]) + Vector2(4, 4)
		t.size = (Vector2(_len[n], 1) if _horiz[n] else Vector2(1, _len[n])) * tile - Vector2(8, 8)
	var p: Vector2i = _pos[_selected]
	_frame.position = cell_pos(p)
	_frame.size = (Vector2(_len[_selected], 1) if _horiz[_selected] else Vector2(1, _len[_selected])) * tile


func _cells_of(n: String, at: Vector2i) -> Array:
	var out := []
	for k in _len[n]:
		out.append(at + (Vector2i(k, 0) if _horiz[n] else Vector2i(0, k)))
	return out


func _owner(c: Vector2i) -> String:
	for n in _pos:
		if c in _cells_of(n, _pos[n]):
			return n
	return ""


## Slides piece n by d cells if everything on the way is free.
func _slide(n: String, d: int) -> bool:
	if d == 0:
		return false
	var step := Vector2i(signi(d), 0) if _horiz[n] else Vector2i(0, signi(d))
	var at: Vector2i = _pos[n]
	for k in absi(d):
		var nxt := at + step
		for c in _cells_of(n, nxt):
			if c.x < 0 or c.y < 0 or c.x >= _size.x or c.y >= _size.y:
				return false
			var o := _owner(c)
			if o != "" and o != n:
				return false
		at = nxt
	_history.append([n, _pos[n]])
	_pos[n] = at
	_draw()
	if _pos["H"].x + _len["H"] - 1 == _size.x - 1:
		_won = true
		_selected = "H"
		level_done("Hanka prolezla ke škvíře! Kvok kvok!")
	return true


func _cell(c: Vector2i) -> void:
	if _won:
		return
	if c.x == _size.x and c.y == _row:
		c.x -= 1
	var o := _owner(c)
	if o != "":
		_selected = o
		say("")
		_draw()
		return
	var p: Vector2i = _pos[_selected]
	var d := 0
	if _horiz[_selected] and c.y == p.y:
		d = c.x - p.x if c.x < p.x else c.x - (p.x + _len[_selected] - 1)
	elif not _horiz[_selected] and c.x == p.x:
		d = c.y - p.y if c.y < p.y else c.y - (p.y + _len[_selected] - 1)
	if d == 0 or not _slide(_selected, d):
		if _selected == "H":
			say("Hanka leze jen doleva a doprava. Něco jí stojí v cestě.")
		else:
			say("Tam to nejde. Ležící balík jezdí jen do stran, stojící jen nahoru a dolů.")


func _dir(d: Vector2i) -> void:
	if _won:
		return
	var amount := d.x if _horiz[_selected] else d.y
	if amount != 0:
		_slide(_selected, amount)


func _undo() -> void:
	if _history.is_empty() or _won:
		return
	var h: Array = _history.pop_back()
	_pos[h[0]] = h[1]
	_draw()


func _key() -> String:
	var keys := _pos.keys()
	keys.sort()
	var s := ""
	for n in keys:
		s += "%s%d,%d;" % [n, _pos[n].x, _pos[n].y]
	return s


## Breadth-first over slides from here; returns [[name, amount], ...].
func _solve() -> Array:
	var start := _pos.duplicate()
	var seen := {_key(): []}
	var queue := [start]
	var qi := 0
	while qi < queue.size() and seen.size() < 60000:
		var st: Dictionary = queue[qi]
		qi += 1
		_pos = st.duplicate()
		var path: Array = seen[_key()]
		if _pos["H"].x + _len["H"] - 1 == _size.x - 1:
			_pos = start
			return path
		for n in st:
			for sgn in [-1, 1]:
				var k := 1
				while true:
					_pos = st.duplicate()
					var step := Vector2i(sgn * k, 0) if _horiz[n] else Vector2i(0, sgn * k)
					var ok := true
					for c in _cells_of(n, st[n] + step):
						if c.x < 0 or c.y < 0 or c.x >= _size.x or c.y >= _size.y:
							ok = false
						else:
							var o := _owner(c)
							if o != "" and o != n:
								ok = false
					if not ok:
						break
					_pos[n] = st[n] + step
					var key := _key()
					if not seen.has(key):
						seen[key] = path + [[n, sgn * k]]
						queue.append(_pos.duplicate())
					k += 1
	_pos = start
	return []


func _hint() -> void:
	var sol := _solve()
	_draw()
	if sol.is_empty():
		say("Zkus Znovu.")
		return
	_selected = sol[0][0]
	_draw()
	if _selected == "H":
		say("Čmuch! Teď může Hanka lézt doprava!")
	else:
		say("Čmuch! Tenhle balík. Posuň ho.")


func solve_for_test() -> void:
	for m in _solve():
		_selected = m[0]
		_slide(m[0], m[1])
		await get_tree().process_frame
