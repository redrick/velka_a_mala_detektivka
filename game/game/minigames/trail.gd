extends "res://game/minigames/minigame_base.gd"
## Story 8 "Po stopě": follow the roe deer from the snowman to her bed under the low spruce. Other animals'
## trails cross hers; only a deer print may come next (two drops, a narrow heart, no dots behind). Click
## the next print next to the last one (not diagonally), or use the arrows. A wrong print is never a fail:
## the girls say whose it is. The track guide is under the board.
## Levels: S the snowman, G the spruce, d deer, b boar, h hare, f fox, p dog, . clean snow.
## tools/check_levels.py checks that the deer prints make one path from S to G.

const LEVELS := [
	[
		"Sdd....",
		"..dhhh.",
		".hddd..",
		".h..ddG",
	],
	[
		"S.ppppp.",
		"d.p.dddf",
		"dddfdfdf",
		".pddd.dG",
		".p..fff.",
	],
	[
		"Sdd..bb..",
		"..d..ddd.",
		"dddbbd.d.",
		"d..ddd.d.",
		"ddddbbbdG",
		".fffff...",
	],
]
const TEX := {"S": "tr_start", "G": "tr_goal", "d": "tr_deer", "b": "tr_boar", "h": "tr_hare", "f": "tr_fox",
	"p": "tr_dog", ".": "tr_snow"}
const WHO := {
	"b": "To je divočák. Je širší a vzadu má dvě tečky!",
	"h": "To je zajíc. Jeho stopa vypadá jako Y.",
	"f": "To je liška. Malý ovál s polštářky, jedna stopa za druhou.",
	"p": "To je pes. Kulatá tlapka s drápky.",
	".": "Tady je čistý sníh. Žádná stopa.",
}
const GUIDE := ["tr_deer", "tr_boar", "tr_hare", "tr_fox", "tr_dog"]
const GUIDE_NAMES := ["srnka", "divočák", "zajíc", "liška", "pes"]

var _g := {}
var _size := Vector2i.ZERO
var _path: Array[Vector2i] = []
var _marks: Array = []
var _me: TextureRect
var _won := false


func _title() -> String: return tr("Po stopě")
func _task_text() -> String:
	return tr("Jdi po stopě srnky od sněhuláka až ke smrčku. Klikni na další srnčí stopu vedle té poslední.")
func _levels() -> int: return LEVELS.size()


func _build(i: int) -> void:
	tile = 120.0
	_g.clear(); _path.clear(); _marks.clear()
	_won = false
	var rows: Array = LEVELS[i]
	_size = Vector2i((rows[0] as String).length(), rows.size())
	tile = minf(tile, 640.0 / _size.y)
	set_board_size(_size.x, _size.y)
	for y in _size.y:
		for x in _size.x:
			var c := Vector2i(x, y)
			var ch: String = rows[y][x]
			_g[c] = ch
			piece(TEX[ch], c)
			if ch == "S":
				_path.append(c)
	_me = figure("res://assets/characters/joey_sniff.png", _path[0], tile * 0.8)
	var guide := HBoxContainer.new()
	guide.add_theme_constant_override("separation", 18)
	for k in GUIDE.size():
		var col := VBoxContainer.new()
		var t := TextureRect.new()
		t.texture = load(ART + GUIDE[k] + ".png")
		t.expand_mode = TextureRect.EXPAND_IGNORE_SIZE
		t.stretch_mode = TextureRect.STRETCH_KEEP_ASPECT_CENTERED
		t.custom_minimum_size = Vector2(70, 70)
		col.add_child(t)
		col.add_child(Kit.label(tr(GUIDE_NAMES[k]), 22))
		guide.add_child(col)
	extra_node(guide)


func _step(c: Vector2i) -> void:
	if _won or not _g.has(c):
		return
	var last: Vector2i = _path[-1]
	if absi(c.x - last.x) + absi(c.y - last.y) != 1:
		say("Stopa musí být hned vedle té poslední. Ne šikmo!")
		return
	var ch: String = _g[c]
	if ch == "G":
		if last == _path[0]:
			return
		_won = true
		_me.position = figure_pos(c, _me)
		level_done("Stopa vede pod smrček. Tady srnka spí!")
		return
	if c in _path:
		return
	if ch != "d":
		say(WHO.get(ch, ""))
		bump(_me)
		return
	_path.append(c)
	var m := frame(Color("6cbf5a"))
	m.position = cell_pos(c)
	_marks.append(m)
	_me.position = figure_pos(c, _me)
	say("Srnka! Dvě kapky, žádné tečky.")


func _cell(c: Vector2i) -> void:
	_step(c)


func _dir(d: Vector2i) -> void:
	_step(_path[-1] + d)


func _undo() -> void:
	if _path.size() <= 1:
		return
	_path.pop_back()
	_marks.pop_back().queue_free()
	_me.position = figure_pos(_path[-1], _me)
	say("")


func _next() -> Vector2i:
	var last: Vector2i = _path[-1]
	for d in [Vector2i.RIGHT, Vector2i.DOWN, Vector2i.LEFT, Vector2i.UP]:
		var n: Vector2i = last + d
		if _g.get(n, "") == "d" and not n in _path:
			return n
	for d in [Vector2i.RIGHT, Vector2i.DOWN, Vector2i.LEFT, Vector2i.UP]:
		if _g.get(last + d, "") == "G" and last != _path[0]:
			return last + d
	return Vector2i(-1, -1)


func _hint() -> void:
	var n := _next()
	if n.x < 0:
		say("Vrať se o krok zpátky.")
		return
	var f := frame(Color("ffd43b"))
	f.position = cell_pos(n)
	var tw := create_tween()
	tw.tween_interval(1.4)
	tw.tween_callback(f.queue_free)
	say("Čmuch! Tady je další srnčí stopa. Porovnej ji s obrázkem dole.")


func solve_for_test() -> void:
	while not _won:
		var n := _next()
		if n.x < 0:
			return
		_step(n)
		await get_tree().process_frame
