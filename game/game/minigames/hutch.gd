extends "res://game/minigames/minigame_base.gd"
## Story 10 "Nový kotec": on the field day táta, pan Karel and the kids build Míša and Šiša a new winter hutch.
## Fill the wall frame with táta's plank pieces, no gaps and nothing sticking out. Pick a piece below,
## turn it with "Otoč" (or the O key), then click the square where its first plank (top left) should go.
## Click a placed piece to take it back. Every level can be done (tools/check_levels.py checks it).
## LEVELS: width, height, piece names (shapes in SHAPES).

const SHAPES := {
	"I2": [Vector2i(0, 0), Vector2i(1, 0)],
	"I3": [Vector2i(0, 0), Vector2i(1, 0), Vector2i(2, 0)],
	"L3": [Vector2i(0, 0), Vector2i(0, 1), Vector2i(1, 1)],
	"L4": [Vector2i(0, 0), Vector2i(0, 1), Vector2i(0, 2), Vector2i(1, 2)],
	"T4": [Vector2i(0, 0), Vector2i(1, 0), Vector2i(2, 0), Vector2i(1, 1)],
}
const LEVELS := [
	[3, 2, ["L3", "L3"]],
	[4, 3, ["L3", "L3", "L3", "L3"]],
	[6, 3, ["T4", "T4", "L4", "L3", "I3"]],
]
const COLORS := [Color("f4d6a0"), Color("e9c27e"), Color("f7e3b8"), Color("dcb06b"), Color("efcf96")]

var _size := Vector2i.ZERO
var _pieces: Array = []        # each: {"cells": Array[Vector2i] (current turn), "at": Vector2i or (-1,-1), "nodes": []}
var _selected := 0
var _grid := {}                # Vector2i -> piece index
var _tray: HBoxContainer
var _cursor := Vector2i.ZERO
var _frame: Panel
var _won := false


func _title() -> String: return tr("Nový kotec")
func _task_text() -> String:
	return tr("Poskládej stěnu kotce z prkýnek. Vyber dílek dole, otoč ho a klikni, kam patří jeho první prkýnko vlevo nahoře.")
func _levels() -> int: return LEVELS.size()


func _build(i: int) -> void:
	tile = 120.0
	var lv: Array = LEVELS[i]
	_size = Vector2i(lv[0], lv[1])
	_pieces.clear(); _grid.clear()
	_won = false
	_selected = 0
	set_board_size(_size.x, _size.y)
	for y in _size.y:
		for x in _size.x:
			piece("hutch_slot", Vector2i(x, y))
	for n in lv[2]:
		_pieces.append({"cells": (SHAPES[n] as Array).duplicate(), "at": Vector2i(-1, -1), "nodes": []})
	_frame = frame()
	_tray = HBoxContainer.new()
	_tray.add_theme_constant_override("separation", 26)
	extra_node(_tray)
	extra_button("Otoč", _turn, 30)
	_draw_tray()


static func turned(cells: Array) -> Array:
	## a quarter turn, then moved back to the top left corner
	var out: Array = []
	for c in cells:
		out.append(Vector2i(-c.y, c.x))
	return normalised(out)


static func flipped(cells: Array) -> Array:
	var out: Array = []
	for c in cells:
		out.append(Vector2i(-c.x, c.y))
	return normalised(out)


static func normalised(cells: Array) -> Array:
	var mx := 99
	var my := 99
	for c in cells:
		mx = mini(mx, c.x)
		my = mini(my, c.y)
	var out: Array = []
	for c in cells:
		out.append(Vector2i(c.x - mx, c.y - my))
	out.sort_custom(func(a, b): return a.y < b.y or (a.y == b.y and a.x < b.x))
	return out


## Every turn and mirror image of a piece (up to 8), so one button reaches them all.
static func turns_of(cells: Array) -> Array:
	var out: Array = []
	var c: Array = normalised(cells)
	for m in 2:
		for r in 4:
			if not out.has(c):
				out.append(c)
			c = turned(c)
		c = flipped(c)
	return out


func _turn() -> void:
	if _won or _selected < 0 or _pieces[_selected].at.x >= 0:
		return
	var all := turns_of(_pieces[_selected].cells)
	_pieces[_selected].cells = all[(all.find(normalised(_pieces[_selected].cells)) + 1) % all.size()]
	_draw_tray()


func _draw_tray() -> void:
	for c in _tray.get_children():
		c.queue_free()
	for k in _pieces.size():
		var p: Dictionary = _pieces[k]
		var box := Control.new()
		var cs := 30.0
		var w := 0
		var h := 0
		for c in p.cells:
			w = maxi(w, c.x + 1)
			h = maxi(h, c.y + 1)
		box.custom_minimum_size = Vector2(maxi(w, 3) * cs + 12, 3 * cs + 12)
		if p.at.x < 0:
			for c in p.cells:
				var r := ColorRect.new()
				r.color = COLORS[k % COLORS.size()]
				r.position = Vector2(c) * cs + Vector2(6, 6)
				r.size = Vector2(cs - 3, cs - 3)
				r.mouse_filter = Control.MOUSE_FILTER_IGNORE
				box.add_child(r)
		if k == _selected and p.at.x < 0:
			var sb := StyleBoxFlat.new()
			sb.bg_color = Color(0, 0, 0, 0)
			sb.border_color = Color("ffd43b")
			sb.set_border_width_all(4)
			sb.set_corner_radius_all(8)
			var pan := Panel.new()
			pan.add_theme_stylebox_override("panel", sb)
			pan.size = box.custom_minimum_size
			pan.mouse_filter = Control.MOUSE_FILTER_IGNORE
			box.add_child(pan)
		box.gui_input.connect(func(e: InputEvent):
			if e is InputEventMouseButton and e.pressed and _pieces[k].at.x < 0:
				_selected = k
				_draw_tray())
		_tray.add_child(box)


func _fits(cells: Array, at: Vector2i) -> bool:
	for c in cells:
		var q: Vector2i = at + c
		if q.x < 0 or q.y < 0 or q.x >= _size.x or q.y >= _size.y or _grid.has(q):
			return false
	return true


func _place(at: Vector2i) -> void:
	if _won:
		return
	if _grid.has(at):
		_take(_grid[at])
		return
	if _selected < 0 or _pieces[_selected].at.x >= 0:
		say("Vyber dole dílek.")
		return
	var p: Dictionary = _pieces[_selected]
	at -= (p.cells[0] as Vector2i)
	if not _fits(p.cells, at):
		say("Tady se nevejde. Zkus ho otočit, nebo jinam.")
		bump(_frame)
		return
	p.at = at
	for c in p.cells:
		_grid[at + c] = _selected
		var t := piece("hutch_plank", at + c, 2)
		t.modulate = COLORS[_selected % COLORS.size()]
		p.nodes.append(t)
	sfx_line()
	if _grid.size() == _size.x * _size.y:
		_won = true
		level_done("Stěna je hotová! Bez jediné škvíry.")
		return
	_selected = -1
	for k in _pieces.size():
		if _pieces[k].at.x < 0:
			_selected = k
			break
	_draw_tray()


func sfx_line() -> void:
	say("Ťuk ťuk! Prkýnko drží.")


func _take(k: int) -> void:
	var p: Dictionary = _pieces[k]
	for c in p.cells:
		_grid.erase(p.at + c)
	for n in p.nodes:
		n.queue_free()
	p.nodes = []
	p.at = Vector2i(-1, -1)
	_selected = k
	say("")
	_draw_tray()


func _cell(c: Vector2i) -> void:
	if c.x < _size.x and c.y < _size.y:
		_cursor = c
		_frame.position = cell_pos(c)
		_place(c)


func _dir(d: Vector2i) -> void:
	_cursor = Vector2i(clampi(_cursor.x + d.x, 0, _size.x - 1), clampi(_cursor.y + d.y, 0, _size.y - 1))
	_frame.position = cell_pos(_cursor)


func _action() -> void:
	_place(_cursor)


func _input(event: InputEvent) -> void:
	if event is InputEventKey and event.pressed and not event.echo and event.keycode == KEY_O:
		get_viewport().set_input_as_handled()
		_turn()
		return
	super(event)


func _undo() -> void:
	var last := -1
	for k in _pieces.size():
		if _pieces[k].at.x >= 0:
			last = k
	if last >= 0:
		_take(last)


## Places that can still be finished: a solver over the pieces left (the levels are small).
func _solve() -> Array:
	var left: Array = []
	for k in _pieces.size():
		if _pieces[k].at.x < 0:
			left.append(k)
	var plan: Array = []
	if _search(_grid.duplicate(), left, plan):
		return plan
	return []


func _search(grid: Dictionary, left: Array, plan: Array) -> bool:
	if left.is_empty():
		return true
	var first := Vector2i(-1, -1)
	for y in _size.y:
		for x in _size.x:
			if not grid.has(Vector2i(x, y)) and first.x < 0:
				first = Vector2i(x, y)
	for k in left:
		for cells in turns_of(_pieces[k].cells):
			var at: Vector2i = first - (cells[0] as Vector2i)
			var ok := true
			for c in cells:
				var q: Vector2i = at + c
				if q.x < 0 or q.y < 0 or q.x >= _size.x or q.y >= _size.y or grid.has(q):
					ok = false
			if not ok:
				continue
			for c in cells:
				grid[at + c] = k
			plan.append([k, cells, at])
			var rest: Array = left.duplicate()
			rest.erase(k)
			if _search(grid, rest, plan):
				return true
			plan.pop_back()
			for c in cells:
				grid.erase(at + c)
	return false


func _hint() -> void:
	var plan := _solve()
	if plan.is_empty():
		say("Takhle to nepůjde. Vezmi nějaký dílek zpátky.")
		return
	var step: Array = plan[0]
	_selected = step[0]
	_pieces[_selected].cells = step[1]
	_draw_tray()
	for c in step[1]:
		var f := frame(Color("6cbf5a"))
		f.position = cell_pos(step[2] + c)
		var tw := create_tween()
		tw.tween_interval(1.4)
		tw.tween_callback(f.queue_free)
	say("Čmuch! Tenhle dílek, takhle otočený, patří na zelená místa.")


func solve_for_test() -> void:
	for step in _solve():
		_selected = step[0]
		_pieces[_selected].cells = step[1]
		_place(step[2] + step[1][0])
		await get_tree().process_frame
