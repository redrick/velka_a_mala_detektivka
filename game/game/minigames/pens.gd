extends "res://game/minigames/minigame_base.gd"
## Story 10 "Ohrádky": on the school meadow every guinea pig gets its own pen, and the number on it
## says how many squares the pen has. Pens are rectangles and cover the whole meadow. Click one corner,
## then the opposite corner: the fence goes up. Click inside a pen to take it down. A pen that is just right
## turns green. Arrows + Enter: move the frame and set a corner.
## Levels: a digit = a guinea pig wanting that many squares, . grass. Each level has exactly one answer
## (tools/check_levels.py checks it).

const LEVELS := [
	[
		"22..",
		"..4.",
	],
	[
		"3.2.",
		".3..",
		"..4.",
	],
	[
		".....",
		"..3.4",
		"6...2",
		"2.3..",
	],
]
const GOOD := Color(0.45, 0.8, 0.4, 0.4)
const WRONG := Color(0.95, 0.6, 0.25, 0.4)

var _size := Vector2i.ZERO
var _rabbits := {}       # guinea pig: Vector2i -> wanted size
var _pens: Array = []    # Rect2i
var _pen_nodes: Array = []
var _anchor := Vector2i(-1, -1)
var _cursor := Vector2i.ZERO
var _frame: Panel
var _anchor_frame: Panel
var _history: Array = []
var _won := false


func _title() -> String: return tr("Ohrádky pro morčata")
func _task_text() -> String:
	return tr("Každé morče má svou ohrádku. Číslo říká, kolik má políček. Klikni na jeden roh a pak na druhý.")
func _levels() -> int: return LEVELS.size()


func _build(i: int) -> void:
	tile = 130.0
	_rabbits.clear(); _pens.clear(); _pen_nodes.clear(); _history.clear()
	_anchor = Vector2i(-1, -1)
	_won = false
	var rows: Array = LEVELS[i]
	_size = Vector2i((rows[0] as String).length(), rows.size())
	set_board_size(_size.x, _size.y)
	for y in _size.y:
		for x in _size.x:
			var c := Vector2i(x, y)
			piece("grass" if (x + y) % 2 == 0 else "grass_b", c)
			var ch: String = rows[y][x]
			if ch != ".":
				_rabbits[c] = int(ch)
				piece("pen_morce", c, 4)
				var l := Kit.label(ch, 52, Color.WHITE, true)
				l.position = cell_pos(c) + Vector2(tile - 46, tile - 62)
				l.size = Vector2(40, 50)
				l.z_index = 5
				board.add_child(l)
	_cursor = Vector2i.ZERO
	_frame = frame()
	_anchor_frame = frame(Color("4dabf7"))
	_anchor_frame.hide()
	_update()


func _inside(r: Rect2i) -> Array:
	var out := []
	for c in _rabbits:
		if r.has_point(c):
			out.append(c)
	return out


func _good(r: Rect2i) -> bool:
	var rs := _inside(r)
	return rs.size() == 1 and _rabbits[rs[0]] == r.get_area()


func _update() -> void:
	for n in _pen_nodes:
		n.queue_free()
	_pen_nodes.clear()
	var covered := 0
	var all_good := true
	for r in _pens:
		var p := Panel.new()
		var sb := StyleBoxFlat.new()
		var ok := _good(r)
		sb.bg_color = GOOD if ok else WRONG
		sb.border_color = Color("7a5230")
		sb.set_border_width_all(8)
		sb.set_corner_radius_all(6)
		p.add_theme_stylebox_override("panel", sb)
		p.position = cell_pos(r.position) + Vector2(4, 4)
		p.size = Vector2(r.size) * tile - Vector2(8, 8)
		p.z_index = 2
		p.mouse_filter = Control.MOUSE_FILTER_IGNORE
		board.add_child(p)
		_pen_nodes.append(p)
		covered += r.get_area()
		all_good = all_good and ok
	_frame.position = cell_pos(_cursor)
	if all_good and covered == _size.x * _size.y and not _won:
		_won = true
		level_done("Každé morče má svou ohrádku!")


func _pen_at(c: Vector2i) -> int:
	for k in _pens.size():
		if (_pens[k] as Rect2i).has_point(c):
			return k
	return -1


func _cell(c: Vector2i) -> void:
	if _won or c.x < 0 or c.y < 0 or c.x >= _size.x or c.y >= _size.y:
		return
	_cursor = c
	var k := _pen_at(c)
	if _anchor.x < 0 and k >= 0:
		_history.append(_pens.duplicate())
		_pens.remove_at(k)
		say("Ohrádka je pryč.")
		_update()
		return
	if _anchor.x < 0:
		_anchor = c
		_anchor_frame.position = cell_pos(c)
		_anchor_frame.show()
		say("A teď druhý roh.")
		_update()
		return
	var r := Rect2i(Vector2i(mini(_anchor.x, c.x), mini(_anchor.y, c.y)), (_anchor - c).abs() + Vector2i.ONE)
	_anchor = Vector2i(-1, -1)
	_anchor_frame.hide()
	for p in _pens:
		if (p as Rect2i).intersects(r):
			say("Tady už ohrádka stojí.")
			_update()
			return
	_history.append(_pens.duplicate())
	_pens.append(r)
	var rs := _inside(r)
	if rs.is_empty():
		say("V téhle ohrádce není žádné morče.")
	elif rs.size() > 1:
		say("Dvě morčata v jedné ohrádce? Každé chce svou!")
	elif _rabbits[rs[0]] != r.get_area():
		say(tr("Morče chce %d políček, ohrádka jich má %d.") % [_rabbits[rs[0]], r.get_area()])
	else:
		say("Tak akorát!")
	_update()


func _dir(d: Vector2i) -> void:
	_cursor = Vector2i(clampi(_cursor.x + d.x, 0, _size.x - 1), clampi(_cursor.y + d.y, 0, _size.y - 1))
	_frame.position = cell_pos(_cursor)


func _action() -> void:
	_cell(_cursor)


func _undo() -> void:
	if _history.is_empty() or _won:
		return
	_pens = _history.pop_back()
	_anchor = Vector2i(-1, -1)
	_anchor_frame.hide()
	_update()


## Every rectangle that could be this rabbit's pen.
func _options(c: Vector2i) -> Array:
	var n: int = _rabbits[c]
	var out := []
	for w in range(1, n + 1):
		if n % w != 0:
			continue
		var h := n / w
		for x in range(c.x - w + 1, c.x + 1):
			for y in range(c.y - h + 1, c.y + 1):
				var r := Rect2i(x, y, w, h)
				if x >= 0 and y >= 0 and x + w <= _size.x and y + h <= _size.y and _inside(r).size() == 1:
					out.append(r)
	return out


func _solve() -> Array:
	var out := []
	_search(_rabbits.keys(), [], out)
	return out


func _search(left: Array, chosen: Array, out: Array) -> bool:
	if left.is_empty():
		out.append_array(chosen)
		return true
	var c: Vector2i = left[0]
	for r in _options(c):
		var free := true
		for p in chosen:
			if (p as Rect2i).intersects(r):
				free = false
				break
		if free:
			chosen.append(r)
			if _search(left.slice(1), chosen, out):
				return true
			chosen.pop_back()
	return false


func _hint() -> void:
	var sol := _solve()
	for r in _pens:
		if not r in sol:
			_cursor = (r as Rect2i).position
			_frame.position = cell_pos(_cursor)
			say("Čmuch! Tahle ohrádka nesedí. Klikni do ní a zbourej ji.")
			return
	for r in sol:
		if not r in _pens:
			_anchor = Vector2i(-1, -1)
			_anchor_frame.position = cell_pos((r as Rect2i).position)
			_anchor_frame.show()
			_cursor = (r as Rect2i).end - Vector2i.ONE
			_frame.position = cell_pos(_cursor)
			say("Čmuch! Zkus ohrádku od modrého rohu ke žlutému.")
			return


func solve_for_test() -> void:
	_pens = _solve()
	_update()
	await get_tree().process_frame
