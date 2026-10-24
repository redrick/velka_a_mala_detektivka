extends "res://game/minigames/minigame_base.gd"
## "Kdo to byl?" for any story (the comic's STOP, detektive! page, playable): the clues on top, the
## suspects below. Picking a suspect whom a clue doesn't fit is never "wrong": a girl says which clue
## rules them out and the card gets crossed. A story's round extends this and returns its case from
## _case(). Mouse: click a card. Keyboard: arrows + Enter.
##
## _case() keys: title, task, hint, win (said when the right one is picked), culprit (an id),
## clues (pictures: names in assets/minigames or res:// paths), suspects ([id, name, picture, why]).

var _cursor := 0
var _frame: Panel
var _out := {}
var _cards: Array = []


func _case() -> Dictionary: return {}


func _title() -> String: return tr(_case().get("title", "Kdo to byl?"))
func _task_text() -> String: return tr(_case().get("task", ""))
func _levels() -> int: return 1


func _build(_i: int) -> void:
	var c := _case()
	_cards = c.suspects
	var cols: int = _cards.size() * 2 - 1
	tile = minf(170.0, 1560.0 / cols)
	_out.clear()
	set_board_size(cols, 3)
	var clues: Array = c.clues
	var c0 := int(floor((cols - clues.size()) / 2.0))
	for k in clues.size():
		piece(clues[k], Vector2i(c0 + k, 0)).scale = Vector2(0.8, 0.8)
	for k in _cards.size():
		piece(_cards[k][2], Vector2i(k * 2, 1)).scale = Vector2(1.15, 1.15)
		var name_label := Kit.label(tr(_cards[k][1]), 26)
		name_label.position = cell_pos(Vector2i(k * 2, 2)) + Vector2(-50, 24)
		name_label.size = Vector2(tile + 100, 44)
		board.add_child(name_label)
	_frame = frame()
	_cursor = 0
	_show()


func _dir(d: Vector2i) -> void:
	_cursor = clampi(_cursor + d.x, 0, _cards.size() - 1)
	_show()


func _cell(c: Vector2i) -> void:
	if c.y >= 1 and c.x % 2 == 0 and c.x / 2 < _cards.size():
		_cursor = c.x / 2
		_show()
		_accuse()


func _action() -> void:
	_accuse()


func _hint() -> void:
	say(_case().get("hint", "Čmuch čmuch!"))


func _accuse() -> void:
	var card: Array = _cards[_cursor]
	if card[0] == _case().culprit:
		level_done(tr(_case().win))
		return
	say(card[3])
	if not _out.has(card[0]):
		_out[card[0]] = true
		var cross := Kit.title("X", 120)
		cross.position = cell_pos(Vector2i(_cursor * 2, 1)) + Vector2(tile / 2.0 - 40, -20)
		cross.z_index = 8
		board.add_child(cross)


func _show() -> void:
	_frame.position = cell_pos(Vector2i(_cursor * 2, 1))


func solve_for_test() -> void:
	for k in _cards.size():
		if _cards[k][0] == _case().culprit:
			_cursor = k
			_accuse()
