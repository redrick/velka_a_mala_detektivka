extends "res://game/minigames/minigame_base.gd"
## Story 11 "Kraslice podle vzoru": babička lays the dyed eggs in rows, and each row repeats its pattern.
## Some places are still empty: click an empty place to change its colour until the pattern goes on.
## When every place is full, the ones that break the pattern fade. Good for Hanka too.
## Levels: R red, Y yellow, B blue, G green, O onion brown; a lowercase letter is an empty place whose
## answer is that colour.

const LEVELS := [
	[
		"RYRYrYRy",
	],
	[
		"OOROOrOoR",
		"GBGbGBgB",
	],
	[
		"RYBrYB",
		"YbRYBr",
		"BRyBry",
	],
]
const TEX := {"R": "egg_r", "Y": "egg_y", "B": "egg_b", "G": "egg_g", "O": "egg_o"}

var _answer := {}        # Vector2i -> colour, for the empty places
var _put := {}           # Vector2i -> colour or ""
var _nodes := {}
var _colours: Array = []
var _cursor := Vector2i.ZERO
var _frame: Panel
var _history: Array = []
var _won := false


func _title() -> String: return tr("Kraslice podle vzoru")
func _task_text() -> String:
	return tr("Každá řada kraslic má svůj vzorek, který se opakuje. Klikni na prázdné místo a vyber barvu.")
func _levels() -> int: return LEVELS.size()


func _build(i: int) -> void:
	tile = 140.0
	_answer.clear(); _put.clear(); _nodes.clear(); _history.clear(); _colours.clear()
	_won = false
	var rows: Array = LEVELS[i]
	var w := 0
	for r in rows:
		w = maxi(w, (r as String).length())
	set_board_size(w, rows.size())
	for y in rows.size():
		for x in (rows[y] as String).length():
			var c := Vector2i(x, y)
			var ch: String = rows[y][x]
			var up := ch.to_upper()
			if not up in _colours:
				_colours.append(up)
			piece("egg_nest", c)
			if ch == up:
				piece(TEX[up], c, 2)
			else:
				_answer[c] = up
				_put[c] = ""
				_nodes[c] = piece("egg_blank", c, 2)
				if _cursor == Vector2i.ZERO or not _answer.has(_cursor):
					_cursor = c
	_frame = frame()
	_update()


func _update() -> void:
	var full := true
	for c in _put:
		var t: TextureRect = _nodes[c]
		t.texture = load(ART + (TEX[_put[c]] if _put[c] != "" else "egg_blank") + ".png")
		t.modulate = Color.WHITE
		full = full and _put[c] != ""
	_frame.position = cell_pos(_cursor)
	if not full:
		return
	var wrong := 0
	for c in _put:
		if _put[c] != _answer[c]:
			(_nodes[c] as Control).modulate = Color(1, 1, 1, 0.4)
			wrong += 1
	if wrong == 0 and not _won:
		_won = true
		level_done("Vzorek se opakuje. Krásné kraslice!")
	elif wrong > 0:
		say("Vybledlé kraslice do vzorku nepatří. Zkus jinou barvu.")


func _cell(c: Vector2i) -> void:
	if _won:
		return
	if not _put.has(c):
		say("Tahle kraslice už je hotová. Klikni na prázdné místo.")
		return
	_cursor = c
	_history.append([c, _put[c]])
	var order: Array = [""] + _colours
	_put[c] = order[(order.find(_put[c]) + 1) % order.size()]
	if _put[c] == "":
		_put[c] = order[1]
	say("")
	_update()


func _dir(d: Vector2i) -> void:
	var keys := _put.keys()
	keys.sort_custom(func(a: Vector2i, b: Vector2i): return a.y < b.y or (a.y == b.y and a.x < b.x))
	var k := keys.find(_cursor)
	_cursor = keys[posmod(k + (1 if d.x + d.y > 0 else -1), keys.size())]
	_frame.position = cell_pos(_cursor)


func _action() -> void:
	_cell(_cursor)


func _undo() -> void:
	if _history.is_empty() or _won:
		return
	var h: Array = _history.pop_back()
	_put[h[0]] = h[1]
	_update()


func _hint() -> void:
	for c in _put:
		if _put[c] != _answer[c]:
			_cursor = c
			_frame.position = cell_pos(c)
			say("Čmuch! Na tohle místo se podívej. Co se v řadě pořád opakuje?")
			return


func solve_for_test() -> void:
	for c in _answer:
		_put[c] = _answer[c]
	_update()
	await get_tree().process_frame
