extends "res://game/minigames/minigame_base.gd"
## Story 3 "Dvacet dětských kroků": plan Alica's steps from the willow stump to the stone with the
## star, then press "Jdi!" and watch her walk them. Reeds stop her, water sends her back ("Brr!").
## The plan stays, so it can be fixed step by step: this is programming, for a 7-year-old.
## Arrows add a step, Backspace/Z removes the last one, Enter runs. Arrow buttons do the same.
## Levels: S stump (start), G star stone, # reeds, ~ water, . grass.

const LEVELS := [
	[
		".....",
		"S.#.G",
		".....",
	],
	[
		"S..#....",
		".#.#.~~.",
		".#...~G.",
		".####...",
		"........",
	],
	[
		"S..#.....",
		"##.#.~~~.",
		".....~G~.",
		".###.~.~.",
		".....#...",
		"~~~.#....",
	],
]
## Steps the plan may hold in each level; the last one is the map's "20 kroků".
const SLOTS := [8, 14, 20]
const ARROW_ROT := {Vector2i.RIGHT: 0.0, Vector2i.DOWN: 90.0, Vector2i.LEFT: 180.0, Vector2i.UP: 270.0}
## Containers ignore rotation, so buttons and the plan strip use one picture per direction.
const ARROW_TEX := {Vector2i.RIGHT: "arrow", Vector2i.DOWN: "arrow_down", Vector2i.LEFT: "arrow_left", Vector2i.UP: "arrow_up"}

var _grid := {}
var _start := Vector2i.ZERO
var _goal := Vector2i.ZERO
var _plan: Array[Vector2i] = []
var _me_node: TextureRect
var _strip: HBoxContainer
var _ghosts: Array[Node] = []
var _hint_len := 0


func _title() -> String: return tr("Dvacet dětských kroků")
func _task_text() -> String: return tr("Naplánuj kroky od pařezu ke kameni s hvězdičkou. Pak zmáčkni Jdi!")
func _levels() -> int: return LEVELS.size()


func _build(i: int) -> void:
	var rows: Array = LEVELS[i]
	_grid.clear(); _plan.clear(); _ghosts.clear(); _hint_len = 0
	set_board_size(rows[0].length(), rows.size())
	for y in rows.size():
		for x in rows[y].length():
			var c := Vector2i(x, y)
			var ch: String = rows[y][x]
			_grid[c] = ch
			match ch:
				"~": piece("water", c)
				"#": piece("reeds", c)
				"S":
					piece("stump", c); _start = c
				"G":
					piece("goal", c); _goal = c
				_: piece("pond_grass", c)
	_me_node = figure("res://assets/characters/alica_happy.png", _start, tile * 1.3)
	for d in [Vector2i.LEFT, Vector2i.UP, Vector2i.DOWN, Vector2i.RIGHT]:
		var b := TextureButton.new()
		b.texture_normal = load(ART + ARROW_TEX[d] + ".png")
		b.ignore_texture_size = true
		b.stretch_mode = TextureButton.STRETCH_KEEP_ASPECT_CENTERED
		b.custom_minimum_size = Vector2(76, 76)
		b.pressed.connect(func(): if not busy: _dir(d))
		extra_node(b)
	_strip = HBoxContainer.new()
	_strip.add_theme_constant_override("separation", 2)
	extra_node(_strip)
	extra_button("Jdi!", func(): if not busy: _action(), 34)
	_redraw_plan()


func _dir(d: Vector2i) -> void:
	if _plan.size() >= SLOTS[level]:
		say("Víc kroků se do plánu nevejde.")
		return
	_plan.append(d)
	say("")
	_redraw_plan()


func _cell(_c: Vector2i) -> void:
	say("Kroky přidáš šipkami.")


func _undo() -> void:
	if not _plan.is_empty():
		_plan.pop_back()
		_redraw_plan()


func _hint() -> void:
	var path := _shortest()
	_hint_len = mini(_hint_len + 3, path.size())
	for g in _ghosts:
		g.queue_free()
	_ghosts.clear()
	var c := _start
	for i in _hint_len:
		c += path[i]
		var p := piece("arrow", c, 4, ARROW_ROT[path[i]])
		p.modulate = Color(1, 1, 1, 0.55)
		p.scale = Vector2(0.6, 0.6)
		_ghosts.append(p)
	say("Čmuch čmuch! Joey ukazuje cestu.")


func _action() -> void:
	if _plan.is_empty():
		say("Nejdřív naplánuj kroky šipkami.")
		return
	busy = true
	var c := _start
	for i in _plan.size():
		var n := c + _plan[i]
		var ch: String = _grid.get(n, "#")
		_mark_slot(i)
		if ch == "#" or not _grid.has(n):
			bump(_me_node)
			say("Au, rákosí! Tudy to nejde. Oprav plán.")
			await get_tree().create_timer(1.0).timeout
			await _back_to_start()
			return
		c = n
		await slide(_me_node, figure_pos(c, _me_node), 0.28).finished
		if ch == "~":
			say("Brr, voda! Oprav plán.")
			await get_tree().create_timer(0.9).timeout
			await _back_to_start()
			return
	if c == _goal:
		level_done(tr("Dvacet kroků a jsme u kamene!") if level == _levels() - 1 else tr("Hurá! Kámen s hvězdičkou!"))
	else:
		say("Tady kámen není. Oprav plán a zkus to znovu.")
		await get_tree().create_timer(0.9).timeout
		await _back_to_start()


func _back_to_start() -> void:
	await slide(_me_node, figure_pos(_start, _me_node), 0.3).finished
	_redraw_plan()
	busy = false


func _redraw_plan() -> void:
	for c in _strip.get_children():
		c.queue_free()
	for i in SLOTS[level]:
		var slot := TextureRect.new()
		slot.texture = load(ART + (ARROW_TEX[_plan[i]] if i < _plan.size() else "slot") + ".png")
		slot.expand_mode = TextureRect.EXPAND_IGNORE_SIZE
		slot.stretch_mode = TextureRect.STRETCH_KEEP_ASPECT_CENTERED
		slot.custom_minimum_size = Vector2(46, 46)
		if i >= _plan.size():
			slot.modulate = Color(1, 1, 1, 0.6)
		_strip.add_child(slot)


func _mark_slot(i: int) -> void:
	for j in _strip.get_child_count():
		(_strip.get_child(j) as Control).modulate = Color(1.5, 1.5, 0.5) if j == i else Color.WHITE


func _shortest() -> Array[Vector2i]:
	var prev := {_start: null}
	var queue: Array[Vector2i] = [_start]
	while not queue.is_empty():
		var c: Vector2i = queue.pop_front()
		if c == _goal:
			var path: Array[Vector2i] = []
			while prev[c] != null:
				var p: Vector2i = prev[c]
				path.push_front(c - p)
				c = p
			return path
		for d in [Vector2i.UP, Vector2i.DOWN, Vector2i.LEFT, Vector2i.RIGHT]:
			var n: Vector2i = c + d
			if _grid.has(n) and not _grid[n] in ["#", "~"] and not prev.has(n):
				prev[n] = c
				queue.append(n)
	return []
