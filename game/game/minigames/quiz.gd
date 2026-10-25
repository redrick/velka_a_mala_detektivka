extends "res://game/minigames/minigame_base.gd"
## "Pravda, nebo ne?": read a short sentence (Alica reads, a grown-up reads for Hanka) and say if it is true.
## Facts the story has just told. A wrong answer is never "wrong": the explanation shows and the question stays
## until it is answered right. A story's quiz extends this and returns its data from _data().
##
## _data() keys: title, task, questions [[picture, sentence, true/false, why]], win.

var _q := 0
var _pic: TextureRect
var _sentence: Label
var _answered := false


func _data() -> Dictionary: return {}
func _title() -> String: return tr(_data().get("title", "Pravda, nebo ne?"))
func _task_text() -> String: return tr(_data().get("task", "Přečti větu. Je to pravda?"))
func _levels() -> int: return 1


func _build(_i: int) -> void:
	tile = 100.0
	set_board_size(15, 6)
	_pic = TextureRect.new()
	_pic.expand_mode = TextureRect.EXPAND_IGNORE_SIZE
	_pic.stretch_mode = TextureRect.STRETCH_KEEP_ASPECT_CENTERED
	_pic.position = Vector2(0, 20)
	_pic.size = Vector2(420, 420)
	_pic.mouse_filter = Control.MOUSE_FILTER_IGNORE
	board.add_child(_pic)
	_sentence = Kit.title("", 56)
	_sentence.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART
	_sentence.position = Vector2(460, 40)
	_sentence.size = Vector2(1000, 300)
	board.add_child(_sentence)
	var row := HBoxContainer.new()
	row.position = Vector2(560, 400)
	row.add_theme_constant_override("separation", 60)
	board.add_child(row)
	row.add_child(Kit.button(tr("✔ Pravda"), func(): _answer(true), 48))
	row.add_child(Kit.button(tr("✘ Není pravda"), func(): _answer(false), 48))
	_q = 0
	_show_q()


func _show_q() -> void:
	var q: Array = _data().questions[_q]
	_pic.texture = load(q[0] if q[0].begins_with("res://") else ART + q[0] + ".png")
	_sentence.text = tr(q[1])
	_count.text = "%d / %d" % [_q + 1, _data().questions.size()]
	_answered = false


func _answer(yes: bool) -> void:
	if busy or _answered:
		return
	var q: Array = _data().questions[_q]
	if yes != q[2]:
		say(tr("Ještě jednou. ") + tr(q[3]))
		bump(_sentence)
		return
	_answered = true
	say(tr("Ano! ") + tr(q[3]))
	await get_tree().create_timer(2.2).timeout
	if not is_instance_valid(self):
		return
	_q += 1
	if _q >= _data().questions.size():
		level_done(tr(_data().get("win", "Hurá!")))
	else:
		say("")
		_show_q()


func _hint() -> void:
	var q: Array = _data().questions[_q]
	say(tr("Čmuch čmuch! ") + tr("Je to pravda.") if q[2] else tr("Čmuch čmuch! ") + tr("Není to pravda."))


func _action() -> void:
	pass


func solve_for_test() -> void:
	while not busy and is_instance_valid(self):
		var q: Array = _data().questions[_q]
		await _answer(q[2])
		await get_tree().process_frame
