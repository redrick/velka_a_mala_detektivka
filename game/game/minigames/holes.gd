extends "res://game/minigames/minigame_base.gd"
## Story 14 "Čtrnáctá díra": count the holes in a wall the way you read (left to right, then the next row) and
## find the one with the Roman number. Each hole clicked in the right order gets its number; ivy has no hole.
## o hole, # ivy (no hole), r the hole with the red ribbon

const LEVELS := [
	["ooo",
	 "ooo"],
	["oo#o",
	 "#ooo",
	 "oooo"],
	["oooooo",
	 "oooooo",
	 "oroooo"],
]
const TARGET := [4, 9, 14]
const NAMES := ["IV (čtyři)", "IX (devět)", "XIV (čtrnáct)"]

var _holes: Array = []
var _next := 0
var _nodes := {}
var _cursor := Vector2i.ZERO
var _frame: Panel
var _size := Vector2i.ZERO


func _title() -> String: return tr("Čtrnáctá díra")
func _task_text() -> String: return ""
func _levels() -> int: return LEVELS.size()


func _build(i: int) -> void:
	var rows: Array = LEVELS[i]
	_size = Vector2i(rows[0].length(), rows.size())
	tile = minf(150.0, 1400.0 / _size.x)
	set_board_size(_size.x, _size.y)
	_task.text = tr("Najdi díru %s. Počítej, jako když čteš: zleva doprava, a pak další řádek.") % tr(NAMES[i])
	_holes.clear(); _nodes.clear()
	_next = 0
	for y in _size.y:
		for x in _size.x:
			var c := Vector2i(x, y)
			match rows[y][x]:
				"#": piece("hole_ivy", c)
				"r":
					_nodes[c] = piece("hole_ribbon" if i == LEVELS.size() - 1 else "hole_empty", c)
					_holes.append(c)
				_:
					_nodes[c] = piece("hole_empty", c)
					_holes.append(c)
	_cursor = Vector2i.ZERO
	_frame = frame()
	_show()


func _dir(d: Vector2i) -> void:
	_cursor = (_cursor + d).clamp(Vector2i.ZERO, _size - Vector2i.ONE)
	_show()


func _action() -> void:
	_cell(_cursor)


func _cell(c: Vector2i) -> void:
	if c.x < 0 or c.y < 0 or c.x >= _size.x or c.y >= _size.y:
		return
	_cursor = c
	_show()
	if not _nodes.has(c):
		say("Tady je břečťan. Díra tu není, tu přeskoč.")
		return
	var k := _holes.find(c)
	if k < _next:
		say("Tuhle už máme spočítanou.")
		return
	if k > _next:
		bump(_nodes[c])
		say("Počítáme jako čteme: zleva doprava, a pak další řádek. Která je na řadě?")
		return
	_next += 1
	var l := Kit.title(str(_next), int(tile * 0.4))
	l.size = Vector2(tile, tile * 0.5)
	l.position = Vector2(0, tile * 0.5)
	l.add_theme_color_override("font_color", Color("ffd43b"))
	l.add_theme_color_override("font_outline_color", Color.BLACK)
	l.add_theme_constant_override("outline_size", 10)
	_nodes[c].add_child(l)
	say(str(_next))
	if _next == TARGET[level]:
		_nodes[c].modulate = Color(1.5, 1.4, 0.7)
		level_done(tr("Tady je! Díra %s!") % tr(NAMES[level]))


func _undo() -> void:
	if _next > 0:
		var c: Vector2i = _holes[_next - 1]
		for ch in _nodes[c].get_children():
			ch.queue_free()
		_next -= 1


func _hint() -> void:
	var f := frame(Color("6ab04c"))
	f.position = cell_pos(_holes[_next])
	get_tree().create_timer(2.0).timeout.connect(f.queue_free)
	say(tr("Čmuch čmuch! Teď je na řadě číslo %d.") % (_next + 1))


func _show() -> void:
	_frame.position = cell_pos(_cursor)


func solve_for_test() -> void:
	while not busy and _next < _holes.size():
		_cell(_holes[_next])
		await get_tree().process_frame
