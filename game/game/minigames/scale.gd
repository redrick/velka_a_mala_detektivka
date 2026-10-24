extends "res://game/minigames/minigame_base.gd"
## Story 8 "Seno do krmelce": the hajný wants the same amount of hay in both racks, or the deer push and
## shove at one side. Each bundle has a tag with dots: one dot, one armful. Click a bundle on the pile and it goes
## to the left rack, click it again for the right rack, once more and it is back on the pile. The beam on
## top leans to the heavier side. All bundles in the racks and the beam level = done.
## Levels: the dots on each bundle. tools/check_levels.py checks each level can be split evenly.

const LEVELS := [
	[1, 2, 3],
	[2, 2, 3, 4, 5],
	[1, 3, 4, 5, 6, 7],
]
const COLS := 10

var _w: Array = []
var _side: Array = []        # -1 left rack, 1 right rack, 0 pile
var _nodes: Array = []
var _beam: ColorRect
var _frame: Panel
var _history: Array = []
var _won := false


func _title() -> String: return tr("Seno do krmelce")
func _task_text() -> String:
	return tr("Do obou jeslí dej stejně sena. Kolik teček má otýpek na cedulce, tolik váží. Klikni na otýpek.")
func _levels() -> int: return LEVELS.size()


func _build(i: int) -> void:
	tile = 110.0
	_w = LEVELS[i].duplicate()
	_side.clear(); _nodes.clear(); _history.clear()
	_won = false
	set_board_size(COLS, 6)
	for x in [0, 1, 2, 3]:
		for y in [2, 3]:
			piece("sc_rack", Vector2i(x, y))
	for x in [6, 7, 8, 9]:
		for y in [2, 3]:
			piece("sc_rack", Vector2i(x, y))
	var post := ColorRect.new()
	post.color = Color("6b4a2f")
	post.size = Vector2(20, tile * 1.6)
	post.position = Vector2(COLS * tile / 2.0 - 10, tile * 0.6)
	post.mouse_filter = Control.MOUSE_FILTER_IGNORE
	board.add_child(post)
	_beam = ColorRect.new()
	_beam.color = Color("8a6240")
	_beam.size = Vector2(tile * 8.4, 22)
	_beam.position = Vector2(COLS * tile / 2.0 - _beam.size.x / 2.0, tile * 0.6)
	_beam.pivot_offset = _beam.size / 2.0
	_beam.mouse_filter = Control.MOUSE_FILTER_IGNORE
	board.add_child(_beam)
	for k in _w.size():
		_side.append(0)
		_nodes.append(piece("hay_%d" % _w[k], Vector2i.ZERO, 3))
	_frame = frame(Color("4dabf7"))
	_frame.hide()
	_update()


## Each bundle's cell: left rack cells, right rack cells, or the pile along the bottom.
func _cells() -> Array:
	var out := []
	var count := {-1: 0, 0: 0, 1: 0}
	var pile := _side.count(0)
	var px := int((COLS - pile) / 2)
	for k in _w.size():
		var s: int = _side[k]
		var n: int = count[s]
		count[s] += 1
		match s:
			-1: out.append(Vector2i(n % 4, 2 + n / 4))
			1: out.append(Vector2i(6 + n % 4, 2 + n / 4))
			_: out.append(Vector2i(px + n, 5))
	return out


func _sum(s: int) -> int:
	var t := 0
	for k in _w.size():
		if _side[k] == s:
			t += _w[k]
	return t


func _update() -> void:
	var diff := clampi(_sum(-1) - _sum(1), -4, 4)
	_beam.rotation_degrees = -diff * 3.0
	var cells := _cells()
	for k in _w.size():
		var drop := float(diff * 8 * -_side[k]) if _side[k] != 0 else 0.0
		(_nodes[k] as Control).position = cell_pos(cells[k]) + Vector2(0, drop)
	if _side.count(0) == 0 and diff == 0 and not _won:
		_won = true
		_frame.hide()
		level_done("V obou jeslích je stejně. Srnky se nebudou strkat!")
	elif _side.count(0) == 0:
		say("Vlevo je víc sena." if diff > 0 else "Vpravo je víc sena.")
	elif diff == 0 and _sum(-1) > 0:
		say("Zatím stejně! Ale na hromadě ještě něco leží.")
	else:
		say("")


func _cell(c: Vector2i) -> void:
	if _won:
		return
	_frame.hide()
	var cells := _cells()
	var k := cells.find(c)
	if k < 0:
		return
	_history.append([k, _side[k]])
	_side[k] = {0: -1, -1: 1, 1: 0}[_side[k]]
	_update()


func _undo() -> void:
	if _history.is_empty() or _won:
		return
	var h: Array = _history.pop_back()
	_side[h[0]] = h[1]
	_update()


## One even split: -1 / 1 for each bundle (the levels are tiny, so try them all).
func _split() -> Array:
	var n := _w.size()
	var total := 0
	for x in _w:
		total += x
	for mask in range(1 << n):
		var left := 0
		for k in n:
			if mask & (1 << k):
				left += _w[k]
		if left * 2 == total:
			var out := []
			for k in n:
				out.append(-1 if mask & (1 << k) else 1)
			return out
	return []


func _hint() -> void:
	var plan := _split()
	# keep whatever already agrees with the plan or with its mirror
	var same := 0
	var mirror := 0
	for k in _w.size():
		same += int(_side[k] == plan[k])
		mirror += int(_side[k] == -plan[k])
	if mirror > same:
		for k in plan.size():
			plan[k] = -plan[k]
	for k in _w.size():
		if _side[k] != plan[k]:
			_frame.position = cell_pos(_cells()[k])
			_frame.show()
			say("Čmuch! Tenhle otýpek patří do levých jeslí." if plan[k] < 0 else "Čmuch! Tenhle otýpek patří do pravých jeslí.")
			return


func solve_for_test() -> void:
	var plan := _split()
	for k in plan.size():
		_side[k] = plan[k]
	_update()
	await get_tree().process_frame
