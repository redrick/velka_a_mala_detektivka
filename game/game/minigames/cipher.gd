extends "res://game/minigames/minigame_base.gd"
## Story 9 "Hvězdičkové písmo": decode Klub Hvězdička's star code with děda's key. Every letter is a shape
## (star, moon, heart, circle = the row of the key) with 1–6 dots like a die (= the place in that row).
## The yellow frame shows which sign is next; click its letter in the key (or move with the arrows and
## press Enter). A wrong letter isn't a fail: the line says what to compare. No háčky or čárky in the code.
## `messages` can be set before the game starts; "|" breaks a line.

const ROWS := ["ABCDEF", "GHIJKL", "MNOPRS", "TUVYZ"]
const SHAPES := ["hvězdička", "měsíček", "srdíčko", "kolečko"]

var messages: Array = ["HLEDEJ HVEZDU|NA MASOPUSTU", "PRIJD|V MASCE", "BUDU MEDVED"]

var _slots: Array = []        # [letter, Vector2i cell of the glyph]
var _labels: Array = []       # Label under each glyph
var _next := 0
var _frame: Panel
var _key_frame: Panel
var _key_cursor := Vector2i.ZERO
var _key_y := 0
var _won := false


func _title() -> String: return tr("Hvězdičkové písmo")
func _task_text() -> String:
	return tr("Tvar je řádek v klíči, tečky jako na kostce jsou místo v řádku. Klikni v klíči na písmeno pro žluté znamení.")
func _levels() -> int: return messages.size()


func _build(i: int) -> void:
	tile = 78.0
	_slots.clear(); _labels.clear()
	_next = 0
	_won = false
	var lines: PackedStringArray = (messages[i] as String).split("|")
	var cols := 6
	for l in lines:
		cols = maxi(cols, l.length())
	_key_y = lines.size() * 2 + 1
	set_board_size(cols, _key_y + ROWS.size())
	for li in lines.size():
		var line: String = lines[li]
		for k in line.length():
			var ch := line[k]
			if ch == " ":
				continue
			var c := Vector2i(k, li * 2)
			piece("cg_" + ch, c)
			piece("cg_slot", c + Vector2i(0, 1))
			var l := Kit.title("", 52)
			l.position = cell_pos(c + Vector2i(0, 1))
			l.size = Vector2(tile, tile)
			l.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
			l.vertical_alignment = VERTICAL_ALIGNMENT_CENTER
			l.z_index = 3
			board.add_child(l)
			_slots.append([ch, c])
			_labels.append(l)
	for r in ROWS.size():
		for k in (ROWS[r] as String).length():
			var c := Vector2i(k, _key_y + r)
			var p := piece("cg_" + ROWS[r][k], c)
			p.scale = Vector2(0.86, 0.86)
			var l := Kit.label(ROWS[r][k], 26)
			l.position = cell_pos(c) + Vector2(tile * 0.62, tile * 0.5)
			l.z_index = 3
			board.add_child(l)
	_frame = frame()
	_key_frame = frame(Color("6cbf5a"))
	_key_cursor = Vector2i.ZERO
	_show()


func _show() -> void:
	if _next < _slots.size():
		_frame.position = cell_pos(_slots[_next][1])
	_key_frame.position = cell_pos(_key_cursor + Vector2i(0, _key_y))


static func where(ch: String) -> Vector2i:
	for r in ROWS.size():
		var k := (ROWS[r] as String).find(ch)
		if k >= 0:
			return Vector2i(k, r)
	return Vector2i(-1, -1)


func _pick(letter: String) -> void:
	if _won or _next >= _slots.size():
		return
	var want: String = _slots[_next][0]
	if letter == want:
		_labels[_next].text = letter
		_next += 1
		if _next >= _slots.size():
			_won = true
			_frame.hide()
			level_done(tr("Rozluštěno: %s") % (messages[level] as String).replace("|", " "))
			return
		say("")
		_show()
		return
	var a := where(want)
	var b := where(letter)
	if a.y != b.y:
		say(tr("Podívej se na tvar. Tohle je %s, ne %s.") % [tr(SHAPES[a.y]), tr(SHAPES[b.y])])
	else:
		say(tr("Tvar sedí! Teď spočítej tečky. Kolik jich je?"))


func _cell(c: Vector2i) -> void:
	var r := c.y - _key_y
	if r >= 0 and r < ROWS.size() and c.x < (ROWS[r] as String).length():
		_key_cursor = Vector2i(c.x, r)
		_show()
		_pick(ROWS[r][c.x])
		return
	for k in _slots.size():
		if _slots[k][1] == c and _labels[k].text == "":
			say("Luštíme popořadě. Žlutý rámeček ukazuje, které je na řadě.")


func _dir(d: Vector2i) -> void:
	var r := clampi(_key_cursor.y + d.y, 0, ROWS.size() - 1)
	var x := clampi(_key_cursor.x + d.x, 0, (ROWS[r] as String).length() - 1)
	_key_cursor = Vector2i(x, r)
	_show()


func _action() -> void:
	_pick(ROWS[_key_cursor.y][_key_cursor.x])


func _undo() -> void:
	if _next > 0 and not _won:
		_next -= 1
		_labels[_next].text = ""
		_show()


func _hint() -> void:
	if _next >= _slots.size():
		return
	var a := where(_slots[_next][0])
	say(tr("Čmuch! Je to %s. Spočítej tečky: %d. Hledej v řádku s tímhle tvarem.") % [tr(SHAPES[a.y]), a.x + 1])


func solve_for_test() -> void:
	while not _won:
		_pick(_slots[_next][0])
		await get_tree().process_frame
