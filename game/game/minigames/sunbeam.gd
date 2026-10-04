extends "res://game/minigames/minigame_base.gd"
## Story 2 "Kam svítí hvězdička": the morning sun comes through the star window. Turn the old
## club mirrors so the beam throws the star on the floor (then Hanka counts seven planks from it). A beam that hits a crate stops; one that hits
## a sleeping owlet wakes it ("Hú!") and stops too. Click a mirror to turn it, or move the frame
## with the arrows and turn with Enter/Space.
## Levels: S window (beam goes right), M mirror, # crate, O owlet, X the spot on the floor, . floor.

const LEVELS := [
	[
		"S..M...",
		".......",
		"...X...",
	],
	[
		"S..M...",
		".......",
		".O.M..X",
		".......",
	],
	[
		"S.M...M.O",
		"....#....",
		"..M...M..",
		"...#.....",
		"......X..",
	],
]
## Starting turn of each mirror, in reading order ("/" or "\"); never the solution.
const START := ["/", "//", "////"]

var _grid := {}
var _mirrors := {}
var _mirror_nodes := {}
var _owls := {}
var _size := Vector2i.ZERO
var _cursor := Vector2i.ZERO
var _cursor_node: Panel
var _beam: Line2D
var _history: Array[Vector2i] = []


func _title() -> String: return tr("Kam svítí hvězdička")
func _task_text() -> String: return tr("Otáčej zrcátky, ať ranní sluníčko posvítí hvězdičkou na podlahu.")
func _levels() -> int: return LEVELS.size()


func _build(i: int) -> void:
	var rows: Array = LEVELS[i]
	_grid.clear(); _mirrors.clear(); _mirror_nodes.clear(); _owls.clear(); _history.clear()
	_size = Vector2i(rows[0].length(), rows.size())
	set_board_size(_size.x, _size.y)
	var turns: String = START[i]
	var m := 0
	for y in rows.size():
		for x in rows[y].length():
			var c := Vector2i(x, y)
			var ch: String = rows[y][x]
			_grid[c] = ch
			piece("sun" if ch == "S" else ("plank_star" if ch == "X" else "planks"), c)
			match ch:
				"#": piece("crate", c, 1)
				"O": _owls[c] = piece("owlet", c, 1)
				"M":
					_mirrors[c] = turns[m]
					_mirror_nodes[c] = piece("mirror", c, 2, _rot(turns[m]))
					m += 1
	_beam = Line2D.new()
	_beam.width = 22.0
	_beam.default_color = Color(1.0, 0.9, 0.35, 0.75)
	_beam.joint_mode = Line2D.LINE_JOINT_ROUND
	_beam.end_cap_mode = Line2D.LINE_CAP_ROUND
	_beam.z_index = 3
	board.add_child(_beam)
	_cursor = _mirrors.keys()[0]
	_cursor_node = Panel.new()
	var sb := StyleBoxFlat.new()
	sb.bg_color = Color(0, 0, 0, 0)
	sb.border_color = Color("ffd43b")
	sb.set_border_width_all(6)
	sb.set_corner_radius_all(14)
	_cursor_node.add_theme_stylebox_override("panel", sb)
	_cursor_node.size = Vector2(tile, tile)
	_cursor_node.z_index = 6
	_cursor_node.mouse_filter = Control.MOUSE_FILTER_IGNORE
	board.add_child(_cursor_node)
	_show_cursor()
	_trace()


func _dir(d: Vector2i) -> void:
	var n := _cursor + d
	if n.x >= 0 and n.y >= 0 and n.x < _size.x and n.y < _size.y:
		_cursor = n
		_show_cursor()


func _cell(c: Vector2i) -> void:
	_cursor = c
	_show_cursor()
	_turn(c)


func _action() -> void:
	_turn(_cursor)


func _undo() -> void:
	if _history.is_empty():
		return
	_turn(_history.pop_back(), false)


func _hint() -> void:
	var wrong := _wrong_mirror()
	if wrong == Vector2i(-1, -1):
		say("Čmuch… Tady to nepůjde. Zmáčkni Znovu.")
		return
	var node: TextureRect = _mirror_nodes[wrong]
	var tw := create_tween().set_loops(3)
	tw.tween_property(node, "modulate", Color(1.6, 1.6, 0.6), 0.25)
	tw.tween_property(node, "modulate", Color.WHITE, 0.25)
	say("Čmuch čmuch! Tohle zrcátko otoč.")


func _turn(c: Vector2i, remember := true) -> void:
	if not _mirrors.has(c):
		if _grid.get(c, "") == "O":
			say("Psst, sovička spí.")
		return
	_mirrors[c] = "\\" if _mirrors[c] == "/" else "/"
	if remember:
		_history.append(c)
	var node: TextureRect = _mirror_nodes[c]
	create_tween().tween_property(node, "rotation_degrees", _rot(_mirrors[c]), 0.18)
	say("")
	_trace()


func _rot(turn: String) -> float:
	return 0.0 if turn == "/" else 90.0


func _show_cursor() -> void:
	_cursor_node.position = cell_pos(_cursor)


## Follows the beam from the window, redraws it, and reacts to where it ends.
func _trace() -> void:
	for o in _owls.values():
		o.texture = load(ART + "owlet.png")
	var src: Vector2i = _grid.find_key("S")
	var c := src
	var d := Vector2i.RIGHT
	var pts: PackedVector2Array = [cell_pos(c) + Vector2(tile * 0.5, tile * 0.5)]
	var hit := ""
	for _i in 100:
		c += d
		var ch: String = _grid.get(c, "")
		if ch == "":
			pts.append(cell_pos(c - d) + Vector2(tile * 0.5, tile * 0.5) + Vector2(d) * tile * 0.5)
			break
		var mid := cell_pos(c) + Vector2(tile * 0.5, tile * 0.5)
		if ch in ["#", "O", "X"]:
			pts.append(mid - Vector2(d) * tile * (0.0 if ch == "X" else 0.35))
			hit = ch
			if ch == "O":
				_owls[c].texture = load(ART + "owlet_awake.png")
			break
		if _mirrors.has(c):
			pts.append(mid)
			d = Vector2i(-d.y, -d.x) if _mirrors[c] == "/" else Vector2i(d.y, d.x)
	_beam.points = pts
	if hit == "O":
		say("Hú! Sovička se probudila. Pošli světlo jinam.")
	elif hit == "X":
		level_done(tr("Hvězdička svítí na zem!") if level == _levels() - 1 else tr("Hurá! Sluníčko je na podlaze."))


## A mirror to turn on the way to a solution, or (-1, -1) if none leads there.
func _wrong_mirror() -> Vector2i:
	var keys: Array = _mirrors.keys()
	for mask in 1 << keys.size():
		var trial := {}
		for i in keys.size():
			trial[keys[i]] = "\\" if mask & (1 << i) else "/"
		if _ends_on_x(trial):
			for k in keys:
				if trial[k] != _mirrors[k]:
					return k
	return Vector2i(-1, -1)


func _ends_on_x(turns: Dictionary) -> bool:
	var c: Vector2i = _grid.find_key("S")
	var d := Vector2i.RIGHT
	for _i in 100:
		c += d
		var ch: String = _grid.get(c, "")
		if ch == "" or ch == "#" or ch == "O":
			return false
		if ch == "X":
			return true
		if turns.has(c):
			d = Vector2i(-d.y, -d.x) if turns[c] == "/" else Vector2i(d.y, d.x)
	return false
