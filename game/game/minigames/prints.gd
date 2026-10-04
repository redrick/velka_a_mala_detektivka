extends "res://game/minigames/minigame_base.gd"
## Story 3 "Čí je to stopa?": prints in the mud on the left, who could have made them on the right.
## Pick a print, then its owner: a line joins them. A wrong owner gets a gentle "look at the shape"
## explanation. Mouse: click a print, then a card. Keyboard: arrows move, Enter/Space picks.

const LEVELS := [
	["bird", "badger", "boot"],
	["bird", "badger", "boot", "stick"],
]
## Cards come in this order on each level (never the same as the prints).
const CARD_ORDER := [[2, 0, 1], [3, 2, 0, 1]]
const WHY := {
	"bird": "Ptáček má nožičky jako vidličky.",
	"badger": "Jezevec má pět drápků.",
	"boot": "Taková velká stopa je od velké holinky.",
	"stick": "Kulaté dírky dělá hůlka.",
}

var _prints: Array = []
var _cards: Array = []
var _card_nodes: Array = []
var _done := {}
var _picked := -1
var _cursor := Vector2i.ZERO
var _frame: Panel
var _pick_frame: Panel


func _title() -> String: return tr("Čí je to stopa?")
func _task_text() -> String: return tr("Klikni na stopu v bahně a pak na toho, kdo ji udělal.")
func _levels() -> int: return LEVELS.size()


func _build(i: int) -> void:
	tile = 150.0
	_prints = LEVELS[i]
	_cards = []
	for k in CARD_ORDER[i]:
		_cards.append(_prints[k])
	_done.clear()
	_card_nodes.clear()
	_picked = -1
	set_board_size(5, _prints.size())
	for r in _prints.size():
		piece("print_" + _prints[r], Vector2i(0, r))
		_card_nodes.append(piece("card_" + _cards[r], Vector2i(4, r)))
	_cursor = Vector2i.ZERO
	_frame = frame()
	_pick_frame = frame(Color("e25b4b"))
	_pick_frame.hide()
	_show()


func _dir(d: Vector2i) -> void:
	if d.x != 0:
		_cursor.x = 0 if d.x < 0 else 4
	else:
		_cursor.y = clampi(_cursor.y + d.y, 0, _prints.size() - 1)
	_show()


func _action() -> void:
	_pick(_cursor)


func _cell(c: Vector2i) -> void:
	if c.x == 0 or c.x == 4:
		_cursor = c
		_show()
		_pick(c)


func _undo() -> void:
	_picked = -1
	_pick_frame.hide()


func _hint() -> void:
	for r in _prints.size():
		if not _done.has(r):
			var tw := create_tween().set_loops(3)
			var a := piece("print_" + _prints[r], Vector2i(0, r), 3)
			var b := piece("card_" + _prints[r], Vector2i(4, _cards.find(_prints[r])), 3)
			for n in [a, b]:
				n.modulate = Color(1.6, 1.6, 0.6)
			tw.tween_property(a, "modulate:a", 0.2, 0.3)
			tw.tween_property(a, "modulate:a", 1.0, 0.3)
			get_tree().create_timer(1.9).timeout.connect(_forget.bind([a, b]))
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
		say("Nejdřív klikni na stopu vlevo.")
		return
	var card: String = _cards[c.y]
	var print_name: String = _prints[_picked]
	if card != print_name:
		bump(_card_nodes[c.y])
		say(WHY[print_name])
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
	if _done.size() == _prints.size():
		level_done(tr("Velká holinka a hůlka… Kdo chodí s hůlkou?") if level == _levels() - 1 else tr("Hurá! Všechny stopy sedí."))


func _show() -> void:
	_frame.position = cell_pos(_cursor)


func _forget(nodes: Array) -> void:
	for n in nodes:
		if is_instance_valid(n):
			n.queue_free()
