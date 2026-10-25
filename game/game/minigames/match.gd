extends "res://game/minigames/minigame_base.gd"
## Pairs: things on the left, what belongs to them on the right (like "Čí je to stopa?", but the data comes from
## the story). Pick a thing on the left, then its partner: a line joins them. A wrong partner gets a gentle
## explanation. A story's game extends this and returns its data from _data().
##
## _data() keys: title, task, levels. A level: left [[id, picture, label]], right [[id, picture, label]] (same ids,
## another order), why {id: text said when the partner is wrong}, win. A label is drawn over the picture
## ("" = none). Mouse: click left, then right. Keyboard: arrows, Enter picks.

var _lv: Dictionary
var _done := {}
var _picked := -1
var _cursor := Vector2i.ZERO
var _frame: Panel
var _pick_frame: Panel
var _right_nodes: Array = []


func _data() -> Dictionary: return {}
func _title() -> String: return tr(_data().get("title", ""))
func _task_text() -> String: return tr(_data().get("task", ""))
func _levels() -> int: return _data().levels.size()


func _build(i: int) -> void:
	_lv = _data().levels[i]
	var n: int = _lv.left.size()
	tile = minf(150.0, 700.0 / n)
	_done.clear()
	_right_nodes.clear()
	_picked = -1
	set_board_size(5, n)
	for r in n:
		_card(_lv.left[r], Vector2i(0, r))
		_right_nodes.append(_card(_lv.right[r], Vector2i(4, r)))
	_cursor = Vector2i.ZERO
	_frame = frame()
	_pick_frame = frame(Color("e25b4b"))
	_pick_frame.hide()
	_show()


func _card(entry: Array, c: Vector2i) -> Control:
	var t := piece(entry[1], c)
	if entry[2] != "":
		var l := Kit.title(tr(entry[2]), int(tile * 0.36))
		l.position = Vector2(0, tile * 0.5)
		l.size = Vector2(tile, tile * 0.45)
		l.add_theme_color_override("font_outline_color", Color.WHITE)
		l.add_theme_constant_override("outline_size", 10)
		t.add_child(l)
	return t


func _dir(d: Vector2i) -> void:
	if d.x != 0:
		_cursor.x = 0 if d.x < 0 else 4
	else:
		_cursor.y = clampi(_cursor.y + d.y, 0, _lv.left.size() - 1)
	_show()


func _action() -> void:
	_pick(_cursor)


func _cell(c: Vector2i) -> void:
	if (c.x == 0 or c.x == 4) and c.y >= 0 and c.y < _lv.left.size():
		_cursor = c
		_show()
		_pick(c)


func _undo() -> void:
	_picked = -1
	_pick_frame.hide()


func _partner(r: int) -> int:
	for k in _lv.right.size():
		if _lv.right[k][0] == _lv.left[r][0]:
			return k
	return -1


func _hint() -> void:
	for r in _lv.left.size():
		if not _done.has(r):
			for c in [Vector2i(0, r), Vector2i(4, _partner(r))]:
				var f := frame(Color("6ab04c"))
				f.position = cell_pos(c)
				get_tree().create_timer(2.0).timeout.connect(f.queue_free)
			say("Čmuch čmuch! Tyhle dvě patří k sobě.")
			return


func _pick(c: Vector2i) -> void:
	if c.x == 0:
		if _done.has(c.y):
			return
		_picked = c.y
		_pick_frame.position = cell_pos(c)
		_pick_frame.show()
		say("")
		return
	if _picked < 0:
		say("Nejdřív klikni na obrázek vlevo.")
		return
	if _lv.right[c.y][0] != _lv.left[_picked][0]:
		bump(_right_nodes[c.y])
		say(_lv.why.get(_lv.left[_picked][0], "Ještě jednou. Podívej se pořádně."))
		return
	_done[_picked] = true
	var line := Line2D.new()
	line.width = 10.0
	line.default_color = Color("e25b4b")
	line.points = [cell_pos(Vector2i(0, _picked)) + Vector2(tile, tile / 2.0), cell_pos(c) + Vector2(0, tile / 2.0)]
	board.add_child(line)
	_picked = -1
	_pick_frame.hide()
	say("Ano!")
	if _done.size() == _lv.left.size():
		level_done(tr(_lv.get("win", "Hurá!")))


func _show() -> void:
	_frame.position = cell_pos(_cursor)


func solve_for_test() -> void:
	for r in _lv.left.size():
		if busy:
			return
		if _done.has(r):
			continue
		_pick(Vector2i(0, r))
		_pick(Vector2i(4, _partner(r)))
		await get_tree().process_frame
