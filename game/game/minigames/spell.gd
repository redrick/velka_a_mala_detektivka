extends "res://game/minigames/minigame_base.gd"
## Write a word from letter tiles: the empty boxes on top, the letters (and a few that don't belong) below.
## Click the letters in order. A story's game extends this and returns its data from _data().
##
## _data() keys: title, task, levels [{word, extra (letters that don't belong), picture, win}]. The word goes
## through tr(), so the English game spells the English word.

var _word := ""
var _have := 0
var _tiles: Array = []
var _boxes: Array = []
var _cursor := 0
var _frame: Panel


func _data() -> Dictionary: return {}
func _title() -> String: return tr(_data().get("title", ""))
func _task_text() -> String: return tr(_data().get("task", ""))
func _levels() -> int: return _data().levels.size()


func _build(i: int) -> void:
	var lv: Dictionary = _data().levels[i]
	_word = tr(lv.word)
	var letters: Array = []
	for ch in _word + tr(lv.get("extra", "")):
		letters.append(ch)
	var rng := RandomNumberGenerator.new()
	rng.seed = hash(_word)
	for k in range(letters.size() - 1, 0, -1):
		var j := rng.randi_range(0, k)
		var t = letters[k]; letters[k] = letters[j]; letters[j] = t
	tile = minf(130.0, 1500.0 / maxi(letters.size() + 3, _word.length() + 3))
	var cols := maxi(letters.size(), _word.length() + 3)
	set_board_size(cols, 4)
	_have = 0
	_tiles.clear(); _boxes.clear()
	if lv.has("picture"):
		piece(lv.picture, Vector2i(0, 0)).scale = Vector2(1.4, 1.4)
	for k in _word.length():
		var box := Kit.panel()
		box.size = Vector2(tile * 0.9, tile * 0.9)
		box.position = cell_pos(Vector2i(k + 2, 0)) + Vector2(tile * 0.05, tile * 0.05)
		box.mouse_filter = Control.MOUSE_FILTER_IGNORE
		board.add_child(box)
		_boxes.append(box)
	var x0 := int((cols - letters.size()) / 2)
	for k in letters.size():
		var t := Kit.panel()
		t.size = Vector2(tile * 0.9, tile * 0.9)
		t.position = cell_pos(Vector2i(x0 + k, 2)) + Vector2(tile * 0.05, tile * 0.05)
		t.mouse_filter = Control.MOUSE_FILTER_IGNORE
		var l := Kit.title(letters[k], int(tile * 0.55))
		l.mouse_filter = Control.MOUSE_FILTER_IGNORE
		t.add_child(l)
		t.set_meta("letter", letters[k])
		t.set_meta("cell", Vector2i(x0 + k, 2))
		board.add_child(t)
		_tiles.append(t)
	_cursor = 0
	_frame = frame()
	_show()


func _tile_at(c: Vector2i) -> int:
	for k in _tiles.size():
		if _tiles[k].get_meta("cell") == c and not _tiles[k].has_meta("used"):
			return k
	return -1


func _cell(c: Vector2i) -> void:
	var k := _tile_at(c)
	if k >= 0:
		_cursor = k
		_show()
		_pick(k)


func _dir(d: Vector2i) -> void:
	_cursor = clampi(_cursor + d.x, 0, _tiles.size() - 1)
	_show()


func _action() -> void:
	_pick(_cursor)


func _pick(k: int) -> void:
	var t: Control = _tiles[k]
	if t.has_meta("used") or _have >= _word.length():
		return
	var want := _word[_have]
	if t.get_meta("letter") != want:
		bump(t)
		say(tr("To je %s. Řekni si slovo nahlas: %s. Které písmeno je teď na řadě?") % [t.get_meta("letter"), _spelled()])
		return
	t.set_meta("used", true)
	slide(t, _boxes[_have].position)
	_have += 1
	say(_word.substr(0, _have))
	if _have == _word.length():
		level_done(tr(_data().levels[level].get("win", "Hurá!")))


func _spelled() -> String:
	var parts: Array = []
	for ch in _word:
		parts.append(ch)
	return "-".join(parts)


func _undo() -> void:
	if _have == 0:
		return
	_have -= 1
	for t in _tiles:
		if t.has_meta("used") and t.position == _boxes[_have].position:
			t.remove_meta("used")
			slide(t, cell_pos(t.get_meta("cell")) + Vector2(tile * 0.05, tile * 0.05))
			return


func _hint() -> void:
	for k in _tiles.size():
		if not _tiles[k].has_meta("used") and _tiles[k].get_meta("letter") == _word[_have]:
			var f := frame(Color("6ab04c"))
			f.position = cell_pos(_tiles[k].get_meta("cell"))
			get_tree().create_timer(2.0).timeout.connect(f.queue_free)
			say("Čmuch čmuch! Tohle písmeno.")
			return


func _show() -> void:
	if not _tiles.is_empty():
		_frame.position = cell_pos(_tiles[_cursor].get_meta("cell"))


func solve_for_test() -> void:
	while not busy and _have < _word.length():
		for k in _tiles.size():
			if not _tiles[k].has_meta("used") and _tiles[k].get_meta("letter") == _word[_have]:
				_pick(k)
				break
		await get_tree().process_frame
