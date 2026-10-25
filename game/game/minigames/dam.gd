extends "res://game/minigames/minigame_base.gd"
## Story 13 "Hráz pro bobra": a map of the creek valley. Put branches where Hryzálek should build his dam: the
## water behind it must cover the entrance of his lodge (it is under water, so foxes can't get in), but not the
## tents. Water spreads over every low cell it can reach; while it can run away down the creek, only the creek is
## wet. Click a meadow or creek cell to put a branch there or take it away. tools/dam_solver.py checks the levels.
##
## ^ high bank, o stone, . meadow, ~ creek, S creek comes in, E creek runs away, L lodge entrance, T tent

const LEVELS := [
	["^^^^S^^^^",
	 "^^..~..^^",
	 "^..L~...^",
	 "^^^.~.^^^",
	 "^^^^~^^^^",
	 "^...~..T^",
	 "^^^^E^^^^"],
	["^^^^^S^^^^^",
	 "^^^^.~.^^^^",
	 "^^^^^~^^^^^",
	 "^^...~...^^",
	 "^^.L.~...^^",
	 "^^^^.~.^^^^",
	 "^^...~..T.^",
	 "^^^^^~^^^^^",
	 "^^^^^E^^^^^"],
	["^^^^^^S^^^^^",
	 "^^....~...^^",
	 "^^.L..~....^",
	 "^^^...~..o.^",
	 "^^^^^.~...^^",
	 "^^^^^.~^...^",
	 "^...^.~^^.T^",
	 "^.T...~^^^^^",
	 "^^^^^^E^^^^^"],
]
const BRANCHES := [1, 2, 3]
const LOW := ".~SELT"

var _g := {}
var _size := Vector2i.ZERO
var _branches: Array = []
var _branch_nodes := {}
var _water_nodes := {}
var _cursor := Vector2i.ZERO
var _frame: Panel
var _branch_label: Label
var _won := false


func _title() -> String: return tr("Hráz pro bobra")
func _task_text() -> String:
	return tr("Bobr staví hráz tam, kde je údolí úzké. Polož větve tak, aby voda zakryla vchod do bobřího hradu, ale stany zůstaly v suchu.")
func _levels() -> int: return LEVELS.size()


func _build(i: int) -> void:
	var rows: Array = LEVELS[i]
	_size = Vector2i(rows[0].length(), rows.size())
	tile = minf(110.0, minf(1500.0 / _size.x, 660.0 / _size.y))
	set_board_size(_size.x, _size.y)
	_g.clear(); _branches.clear(); _branch_nodes.clear(); _water_nodes.clear()
	_won = false
	for y in _size.y:
		for x in _size.x:
			var c := Vector2i(x, y)
			var ch: String = rows[y][x]
			_g[c] = ch
			match ch:
				"^": piece("dam_high", c)
				"o": piece("dam_stone", c)
				"~", "S", "E": piece("dam_water", c)
				_: piece("dam_low", c)
			var w := piece("dam_flood", c, 1)
			w.modulate.a = 0.0
			_water_nodes[c] = w
			if ch == "L": piece("dam_lodge", c, 3)
			if ch == "T": piece("dam_tent", c, 3)
	_branch_label = Kit.label("", 32)
	extra_node(_branch_label)
	_cursor = Vector2i(_size.x / 2, _size.y / 2)
	_frame = frame()
	_show()
	_flow(false)


func _dir(d: Vector2i) -> void:
	_cursor = (_cursor + d).clamp(Vector2i.ZERO, _size - Vector2i.ONE)
	_show()


func _action() -> void:
	_toggle(_cursor)


func _cell(c: Vector2i) -> void:
	if _g.has(c):
		_cursor = c
		_show()
		_toggle(c)


func _undo() -> void:
	if not _branches.is_empty():
		_toggle(_branches[-1])


func _toggle(c: Vector2i) -> void:
	if _won:
		return
	if c in _branches:
		_branches.erase(c)
		_branch_nodes[c].queue_free()
		_branch_nodes.erase(c)
	elif not _g[c] in ".~":
		say({"^": "Tady je vysoký břeh. Sem voda nedosáhne.", "o": "Tady je velký kámen.",
			"S": "Tudy přitéká potok.", "E": "Tudy potok odtéká.", "L": "Tady je vchod do bobřího hradu.",
			"T": "Tady stojí stan."}.get(_g[c], ""))
		return
	elif _branches.size() >= BRANCHES[level]:
		say("Víc větví nemáš. Jednu vezmi a polož ji jinam.")
		return
	else:
		_branches.append(c)
		_branch_nodes[c] = piece("dam_branch", c, 4)
	_flow(true)


## Where the water is, the same way as tools/dam_solver.py: [wet cells, true when a pond holds].
func _water() -> Array:
	var start := Vector2i.ZERO
	for c in _g:
		if _g[c] == "S":
			start = c
	var seen := {start: 0}
	var todo := [start]
	var drains := false
	while not todo.is_empty():
		var c: Vector2i = todo.pop_front()
		if _g[c] == "E":
			drains = true
		for d in [Vector2i.RIGHT, Vector2i.LEFT, Vector2i.DOWN, Vector2i.UP]:
			var n: Vector2i = c + d
			if _g.has(n) and not seen.has(n) and _g[n] in LOW and not n in _branches:
				seen[n] = seen[c] + 1
				todo.append(n)
	if drains:
		for c in seen.keys():
			if not _g[c] in "~SE":
				seen.erase(c)
	return [seen, not drains]


func _flow(animate: bool) -> void:
	var res := _water()
	var wet: Dictionary = res[0]
	var pond: bool = res[1]
	for c in _water_nodes:
		var on: bool = wet.has(c) and (pond or not _g[c] in "~SE")
		var target := 0.85 if on else 0.0
		var node: Control = _water_nodes[c]
		if not animate:
			node.modulate.a = target
		elif node.modulate.a != target:
			var tw := create_tween()
			tw.tween_interval(0.06 * wet.get(c, 0) if on else 0.0)
			tw.tween_property(node, "modulate:a", target, 0.25)
	_branch_label.text = tr("Větve: %d z %d") % [_branches.size(), BRANCHES[level]]
	var lodge_wet := true
	var tent_wet := false
	for c in _g:
		if _g[c] == "L" and not (pond and wet.has(c)): lodge_wet = false
		if _g[c] == "T" and pond and wet.has(c): tent_wet = true
	if not animate:
		return
	if not pond:
		say("Voda uteče potokem pryč. Hráz ještě není celá.")
	elif tent_wet:
		say("Pozor, stan je pod vodou! Postav hráz jinde.")
	elif not lodge_wet:
		say("Stany jsou v suchu. Ale vchod do bobřího hradu ještě není pod vodou.")
	else:
		_won = true
		get_tree().create_timer(1.0).timeout.connect(func(): level_done(tr("Vchod je pod vodou a stany v suchu. Hryzálek by byl spokojený!")))


func _show() -> void:
	_frame.position = cell_pos(_cursor)


## The first answer (fewest branches) that keeps the branches already placed, else any answer.
func _answer() -> Array:
	var spots: Array = []
	for c in _g:
		if _g[c] in ".~" and not c in _branches:
			spots.append(c)
	var found := _search(spots, 0, _branches.duplicate(), BRANCHES[level] - _branches.size())
	if found.is_empty():
		spots.append_array(_branches)
		found = _search(spots, 0, [], BRANCHES[level])
	return found


func _search(spots: Array, from: int, picked: Array, left: int) -> Array:
	if not picked.is_empty() and _solves(picked):
		return picked
	if left <= 0:
		return []
	for k in range(from, spots.size()):
		var r := _search(spots, k + 1, picked + [spots[k]], left - 1)
		if not r.is_empty():
			return r
	return []


func _solves(cells: Array) -> bool:
	var saved := _branches
	_branches = cells
	var res := _water()
	_branches = saved
	if not res[1]:
		return false
	for c in _g:
		if _g[c] == "L" and not res[0].has(c): return false
		if _g[c] == "T" and res[0].has(c): return false
	return true


func _hint() -> void:
	var ans := _answer()
	for c in ans:
		if not c in _branches:
			var f := frame(Color("6ab04c"))
			f.position = cell_pos(c)
			get_tree().create_timer(2.0).timeout.connect(f.queue_free)
			if _branches.size() >= BRANCHES[level]:
				say("Čmuch čmuch! Jednu větev přenes sem.")
			else:
				say("Čmuch čmuch! Zkus větev sem.")
			return
	say("Čmuch čmuch! Kde je údolí nejužší?")


func solve_for_test() -> void:
	for c in _branches.duplicate():
		_toggle(c)
	_branches.clear()
	for c in _answer():
		_toggle(c)
		await get_tree().process_frame
