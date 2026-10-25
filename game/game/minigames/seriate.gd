extends "res://game/minigames/minigame_base.gd"
## Put cards into places in the right order: pictures by how much water there is, day words in the week's
## order, or the one picture that comes next. A story's game extends this and returns its data from _data().
## Click a card in the tray, then a place (a full place sends its card back); click a placed card to take it
## back. When every place is full, the order is checked.
##
## _data() keys: title, task, levels. A level: task (optional, replaces the sheet's task), slots [[picture,
## caption]] (picture above the place, caption faint inside it; "" = none), items [[id, picture, word]] (picture "" = a word card),
## answer [item id for each slot], wrong (said when the order isn't right), win.

var _lv: Dictionary
var _at := {}
var _item_nodes := {}
var _slot_cells: Array = []
var _tray_cells := {}
var _sel := ""
var _sel_frame: Panel
var _history: Array = []


func _data() -> Dictionary: return {}
func _title() -> String: return tr(_data().get("title", ""))
func _task_text() -> String: return tr(_data().get("task", ""))
func _levels() -> int: return _data().levels.size()


func _build(i: int) -> void:
	_lv = _data().levels[i]
	_task.text = tr(_lv.get("task", _task_text()))
	tile = 150.0
	_at.clear(); _item_nodes.clear(); _slot_cells.clear(); _tray_cells.clear(); _history.clear()
	_sel = ""
	var n: int = _lv.slots.size()
	var m: int = _lv.items.size()
	var cols: int = maxi(n, m) * 2 - 1
	set_board_size(cols, 4)
	var x0 := int((cols - (n * 2 - 1)) / 2)
	for k in n:
		var c := Vector2i(x0 + k * 2, 1)
		_slot_cells.append(c)
		var s: Array = _lv.slots[k]
		if s[0] != "":
			piece(s[0], c - Vector2i(0, 1))
		if s[1] != "":
			var l := Kit.title(tr(s[1]), 40)
			l.position = cell_pos(c) + Vector2(-30, tile * 0.3)
			l.size = Vector2(tile + 60, tile * 0.4)
			l.modulate.a = 0.45
			board.add_child(l)
		var box := Panel.new()
		var sb := StyleBoxFlat.new()
		sb.bg_color = Color(1, 1, 1, 0.35)
		sb.border_color = Color("8a7f6a")
		sb.set_border_width_all(4)
		sb.set_corner_radius_all(14)
		box.add_theme_stylebox_override("panel", sb)
		box.size = Vector2(tile, tile)
		box.position = cell_pos(c)
		box.mouse_filter = Control.MOUSE_FILTER_IGNORE
		board.add_child(box)
	var t0 := int((cols - (m * 2 - 1)) / 2)
	for k in m:
		var it: Array = _lv.items[k]
		var c := Vector2i(t0 + k * 2, 3)
		_tray_cells[c] = it[0]
		_at[it[0]] = -1
		var node: Control
		if it[1] != "":
			node = piece(it[1], c, 2)
		else:
			node = Kit.panel()
			node.size = Vector2(tile + 40, tile * 0.6)
			node.position = cell_pos(c) + Vector2(-20, tile * 0.2)
			node.z_index = 2
			node.mouse_filter = Control.MOUSE_FILTER_IGNORE
			var l := Kit.title(tr(it[2]), 38)
			l.mouse_filter = Control.MOUSE_FILTER_IGNORE
			node.add_child(l)
			board.add_child(node)
		node.set_meta("home", node.position)
		_item_nodes[it[0]] = node
	_sel_frame = frame(Color("e25b4b"))
	_sel_frame.hide()


func _item_at_slot(k: int) -> String:
	for id in _at:
		if _at[id] == k:
			return id
	return ""


func _cell(c: Vector2i) -> void:
	if _tray_cells.has(c) and _at[_tray_cells[c]] == -1:
		_select(_tray_cells[c])
		return
	var k := _slot_cells.find(c)
	if k < 0:
		return
	if _sel == "":
		var there := _item_at_slot(k)
		if there != "":
			_place(there, -1)
		return
	_place(_sel, k)
	_select("")


func _select(id: String) -> void:
	_sel = id
	if id == "":
		_sel_frame.hide()
		return
	_sel_frame.position = _item_nodes[id].get_meta("home") if _item_nodes[id] is TextureRect else \
		_item_nodes[id].get_meta("home") + Vector2(20, -tile * 0.2)
	_sel_frame.show()
	say("")


func _place(id: String, k: int, record := true) -> void:
	if record:
		_history.append([id, _at[id]])
	if k >= 0:
		var there := _item_at_slot(k)
		if there != "" and there != id:
			_place(there, -1, false)
	_at[id] = k
	var node: Control = _item_nodes[id]
	var home: Vector2 = node.get_meta("home")
	if k < 0:
		slide(node, home)
	else:
		var target := cell_pos(_slot_cells[k])
		if not node is TextureRect:
			target += Vector2(-20, tile * 0.2)
		slide(node, target)
	_check()


func _check() -> void:
	for k in _slot_cells.size():
		if _item_at_slot(k) == "":
			return
	for k in _slot_cells.size():
		if _item_at_slot(k) != _lv.answer[k]:
			say(_lv.get("wrong", "Ještě to není ono. Zkus to jinak."))
			return
	level_done(tr(_lv.get("win", "Hurá!")))


func _undo() -> void:
	if _history.is_empty():
		return
	var last: Array = _history.pop_back()
	_place(last[0], last[1], false)


func _hint() -> void:
	for k in _slot_cells.size():
		if _item_at_slot(k) != _lv.answer[k]:
			_place(_lv.answer[k], k)
			say("Čmuch čmuch! Tenhle patří sem.")
			return


func solve_for_test() -> void:
	for k in _slot_cells.size():
		if busy:
			return
		_place(_lv.answer[k], k)
		await get_tree().process_frame
