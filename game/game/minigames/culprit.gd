extends "res://game/minigames/minigame_base.gd"
## Story 3 "Kdo to byl?" (the comic's STOP, detektive! page, playable): the clues on top, four
## suspects below. Picking a suspect whom a clue doesn't fit is never "wrong": Alica says which
## clue rules them out and the card gets crossed. Mouse: click a card. Keyboard: arrows + Enter.

const SUSPECTS := ["tonda", "badger", "rybar", "lady"]
const NAMES := {"tonda": "Tonda", "badger": "Jezevec", "rybar": "Rybář", "lady": "Paní od mlýna"}
const WHY := {
	"tonda": "Tonda byl v neděli ráno s tátou pro rohlíky. A hůlku nemá.",
	"badger": "Jezevec má drápky, ne boty. A plechovku by neodnesl.",
	"rybar": "Rybář ráno spí. A jeho holinky jsou obří.",
}
const CLUES := ["print_boot", "print_stick", "res://assets/props/lantern_lit.png", "res://assets/props/stick_lean.png"]

var _cursor := 0
var _frame: Panel
var _out := {}


func _title() -> String: return tr("Kdo to byl?")
func _task_text() -> String: return tr("Už máš všechny stopy. Kdo vykopal poklad?")
func _levels() -> int: return 1


func _build(_i: int) -> void:
	tile = 170.0
	_out.clear()
	set_board_size(7, 3)
	for k in CLUES.size():
		var p := piece(CLUES[k], Vector2i(k + 1, 0))
		p.scale = Vector2(0.75, 0.75)
	for k in SUSPECTS.size():
		piece("who_" + SUSPECTS[k], Vector2i(k * 2, 1)).scale = Vector2(1.15, 1.15)
		var name_label := Kit.label(tr(NAMES[SUSPECTS[k]]), 28)
		name_label.position = cell_pos(Vector2i(k * 2, 2)) + Vector2(-40, 20)
		name_label.size = Vector2(tile + 80, 44)
		board.add_child(name_label)
	_frame = frame()
	_show()


func _dir(d: Vector2i) -> void:
	_cursor = clampi(_cursor + d.x, 0, SUSPECTS.size() - 1)
	_show()


func _cell(c: Vector2i) -> void:
	if c.y >= 1 and c.x % 2 == 0 and c.x / 2 < SUSPECTS.size():
		_cursor = c.x / 2
		_show()
		_accuse()


func _action() -> void:
	_accuse()


func _hint() -> void:
	say("Čmuch čmuch! Joey šel od díry až k lavičce u mlýna.")


func _accuse() -> void:
	var who: String = SUSPECTS[_cursor]
	if who == "lady":
		level_done(tr("Paní od mlýna! Chodí s hůlkou a má lucernu. Ale kdo to je?"))
		return
	say(WHY[who])
	if not _out.has(who):
		_out[who] = true
		var cross := Kit.title("X", 120)
		cross.position = cell_pos(Vector2i(_cursor * 2, 1)) + Vector2(10, -30)
		cross.z_index = 8
		board.add_child(cross)


func _show() -> void:
	_frame.position = cell_pos(Vector2i(_cursor * 2, 1))
