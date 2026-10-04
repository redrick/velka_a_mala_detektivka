extends "res://game/minigames/minigame_base.gd"
## Story 1 "Nastraž past": Hanka pushes flour sacks onto the tiny footprints under the clothesline,
## so the thief walks through flour tonight. A small push-the-boxes puzzle: a sack can be pushed,
## never pulled. Arrows/WASD move Hanka; a click walks her there (or pushes if next to a sack).
## Every game makes new levels: _generate() starts from the finished trap (sacks on the footprints)
## and walks Hanka backwards, pulling sacks, so a level can always be solved; the solver then keeps
## only levels whose shortest solution fits SPECS. LEVELS are the fallback if that ever fails.
## Levels: # bush/pot, . grass, P Hanka, B sack, T footprints, * sack on footprints.

const LEVELS := [
	[
		"#######",
		"#.....#",
		"#.PB.T#",
		"#.....#",
		"#######",
	],
	[
		"#######",
		"#..T..#",
		"#.B.#.#",
		"#P.B.T#",
		"#.....#",
		"#######",
	],
	[
		"########",
		"#T..#.T#",
		"#.B..B.#",
		"#..#...#",
		"#P.B.#T#",
		"#......#",
		"########",
	],
]
const OBSTACLES := ["bush", "flowerpot", "pumpkin"]
## size, sacks, bushes inside, and the allowed length of the shortest solution (moves).
const SPECS := [
	{"size": Vector2i(7, 5), "sacks": 1, "rocks": 1, "min": 4, "max": 14},
	{"size": Vector2i(8, 6), "sacks": 2, "rocks": 3, "min": 10, "max": 40},
	{"size": Vector2i(9, 7), "sacks": 3, "rocks": 5, "min": 16, "max": 70},
]
const DIRS4: Array[Vector2i] = [Vector2i.UP, Vector2i.DOWN, Vector2i.LEFT, Vector2i.RIGHT]

## The levels of this game, generated once (Znovu replays the same level).
var _made := {}

var _walls := {}
var _goals := {}
var _boxes: Array[Vector2i] = []
var _me := Vector2i.ZERO
var _me_node: TextureRect
var _box_nodes: Array[TextureRect] = []
var _history: Array = []
var _size := Vector2i.ZERO


func _title() -> String: return tr("Nastraž past")
func _task_text() -> String: return tr("Posuň pytlíky s moukou na malé stopy. Tudy v noci půjde zloděj!")
func _levels() -> int: return LEVELS.size()


func _build(i: int) -> void:
	if not _made.has(i):
		var rows_new := _generate(SPECS[i])
		_made[i] = rows_new if not rows_new.is_empty() else LEVELS[i]
	var rows: Array = _made[i]
	_walls.clear(); _goals.clear(); _boxes.clear(); _box_nodes.clear(); _history.clear()
	_size = Vector2i(rows[0].length(), rows.size())
	set_board_size(_size.x, _size.y)
	for y in rows.size():
		for x in rows[y].length():
			var c := Vector2i(x, y)
			var ch: String = rows[y][x]
			if ch == "#":
				_walls[c] = true
				piece(OBSTACLES[(x * 7 + y * 3) % OBSTACLES.size()], c)
				continue
			piece("grass" if (x + y) % 2 == 0 else "grass_b", c)
			if ch in ["T", "*", "+"]:
				_goals[c] = true
				piece("target", c, 1)
			if ch in ["B", "*"]:
				_boxes.append(c)
			if ch in ["P", "+"]:
				_me = c
	for b in _boxes:
		_box_nodes.append(piece("sack", b, 2))
	_me_node = figure("res://assets/characters/hanka_happy.png", _me)
	_refresh_sacks()


func _dir(d: Vector2i) -> void:
	_step(d)


func _cell(c: Vector2i) -> void:
	var d := c - _me
	if absi(d.x) + absi(d.y) == 1:
		_step(d)
		return
	var path := _walk_path(c)
	if path.is_empty():
		bump(_me_node)
		return
	busy = true
	_history.append([_me, _boxes.duplicate()])
	for p in path:
		_me = p
		await slide(_me_node, figure_pos(_me, _me_node), 0.1).finished
	busy = false


func _undo() -> void:
	if _history.is_empty():
		return
	var last: Array = _history.pop_back()
	_me = last[0]
	_boxes.assign(last[1])
	_me_node.position = figure_pos(_me, _me_node)
	for i in _boxes.size():
		_box_nodes[i].position = cell_pos(_boxes[i])
	_refresh_sacks()
	say("")


func _hint() -> void:
	var first := _solve_first_move()
	if first == Vector2i.ZERO:
		say("Čmuch… Tady už to nepůjde. Zmáčkni Zpět, nebo Znovu.")
		return
	var arrow := piece("arrow", _me + first, 8, rad_to_deg(Vector2(first).angle()))
	arrow.modulate.a = 0.0
	var tw := create_tween()
	tw.tween_property(arrow, "modulate:a", 1.0, 0.2)
	tw.tween_interval(1.2)
	tw.tween_property(arrow, "modulate:a", 0.0, 0.3)
	tw.tween_callback(arrow.queue_free)
	say("Čmuch čmuch! Zkus to tudy.")


func _step(d: Vector2i) -> void:
	var n := _me + d
	if _walls.has(n) or not _inside(n):
		bump(_me_node)
		return
	var bi := _boxes.find(n)
	if bi >= 0:
		var b2 := n + d
		if _walls.has(b2) or _boxes.has(b2) or not _inside(b2):
			bump(_box_nodes[bi])
			say("Tenhle pytlík dál nepůjde.")
			return
		_history.append([_me, _boxes.duplicate()])
		_boxes[bi] = b2
		slide(_box_nodes[bi], cell_pos(b2))
	else:
		_history.append([_me, _boxes.duplicate()])
	_me = n
	slide(_me_node, figure_pos(_me, _me_node))
	say("")
	_refresh_sacks()
	if _goals.keys().all(func(g): return _boxes.has(g)):
		level_done(tr("Hurá! Mouka je na stopách. Past je nastražená!") if level == _levels() - 1 else tr("Hurá! Další past…"))


func _refresh_sacks() -> void:
	for i in _boxes.size():
		_box_nodes[i].texture = load(ART + ("sack_done" if _goals.has(_boxes[i]) else "sack") + ".png")


func _inside(c: Vector2i) -> bool:
	return c.x >= 0 and c.y >= 0 and c.x < _size.x and c.y < _size.y


## Walking path to `to` around bushes and sacks (no pushing), or [] if there is none.
func _walk_path(to: Vector2i) -> Array[Vector2i]:
	if _walls.has(to) or _boxes.has(to) or not _inside(to):
		return []
	var prev := {_me: _me}
	var queue: Array[Vector2i] = [_me]
	while not queue.is_empty():
		var c: Vector2i = queue.pop_front()
		if c == to:
			var path: Array[Vector2i] = []
			while c != _me:
				path.push_front(c)
				c = prev[c]
			return path
		for d in [Vector2i.UP, Vector2i.DOWN, Vector2i.LEFT, Vector2i.RIGHT]:
			var n: Vector2i = c + d
			if _inside(n) and not _walls.has(n) and not _boxes.has(n) and not prev.has(n):
				prev[n] = c
				queue.append(n)
	return []


## First move of a shortest solution from the current position, or ZERO when stuck.
func _solve_first_move() -> Vector2i:
	return _bfs(_me, _boxes, _walls, _goals, _size)[1]


## Shortest solution by breadth-first search: [moves, first move]; [-1, ZERO] if none (or too big).
func _bfs(me0: Vector2i, boxes0: Array, walls: Dictionary, goals: Dictionary, size: Vector2i, cap := 150000) -> Array:
	var goal_list: Array = goals.keys()
	var start := _key(me0, boxes0)
	var info := {start: [0, Vector2i.ZERO]}
	var queue: Array = [[me0, boxes0.duplicate()]]
	var head := 0
	while head < queue.size() and info.size() < cap:
		var st: Array = queue[head]
		head += 1
		var me: Vector2i = st[0]
		var boxes: Array = st[1]
		var here: Array = info[_key(me, boxes)]
		if goal_list.all(func(g): return boxes.has(g)):
			return here
		for d in DIRS4:
			var n: Vector2i = me + d
			if walls.has(n) or n.x < 0 or n.y < 0 or n.x >= size.x or n.y >= size.y:
				continue
			var nb := boxes.duplicate()
			var bi := nb.find(n)
			if bi >= 0:
				var b2: Vector2i = n + d
				if walls.has(b2) or nb.has(b2) or b2.x < 0 or b2.y < 0 or b2.x >= size.x or b2.y >= size.y:
					continue
				nb[bi] = b2
			var k := _key(n, nb)
			if not info.has(k):
				info[k] = [here[0] + 1, d if here[0] == 0 else here[1]]
				queue.append([n, nb])
	return [-1, Vector2i.ZERO]


## A new level for `spec`, or [] if none fitted after many tries.
func _generate(spec: Dictionary) -> Array:
	var rng := RandomNumberGenerator.new()
	rng.randomize()
	var size: Vector2i = spec.size
	for _attempt in 600:
		var walls := {}
		for x in size.x:
			for y in size.y:
				if x == 0 or y == 0 or x == size.x - 1 or y == size.y - 1:
					walls[Vector2i(x, y)] = true
		var floor_cells: Array[Vector2i] = []
		for x in range(1, size.x - 1):
			for y in range(1, size.y - 1):
				floor_cells.append(Vector2i(x, y))
		for _r in spec.rocks:
			var c: Vector2i = floor_cells.pick_random()
			walls[c] = true
			floor_cells.erase(c)
		if not _connected(floor_cells, walls):
			continue
		floor_cells.shuffle()
		var goals := {}
		var boxes: Array = []
		for k in spec.sacks:
			goals[floor_cells[k]] = true
			boxes.append(floor_cells[k])
		var me: Vector2i = floor_cells[spec.sacks]
		# walk backwards from the solved trap, sometimes pulling the sack behind Hanka
		for _s in rng.randi_range(40, 120):
			var d: Vector2i = DIRS4[rng.randi() % 4]
			var n := me + d
			if walls.has(n) or boxes.has(n):
				continue
			var bi := boxes.find(me - d)
			if bi >= 0 and rng.randf() < 0.75:
				boxes[bi] = me
			me = n
		if boxes.any(func(b): return goals.has(b)):
			continue
		var moves: int = _bfs(me, boxes, walls, goals, size, 40000)[0]
		if moves < spec.min or moves > spec.max:
			continue
		var rows: Array = []
		for y in size.y:
			var row := ""
			for x in size.x:
				var c := Vector2i(x, y)
				if walls.has(c): row += "#"
				elif c == me: row += "+" if goals.has(c) else "P"
				elif boxes.has(c): row += "*" if goals.has(c) else "B"
				elif goals.has(c): row += "T"
				else: row += "."
			rows.append(row)
		return rows
	return []


func _connected(cells: Array[Vector2i], walls: Dictionary) -> bool:
	var seen := {cells[0]: true}
	var queue: Array[Vector2i] = [cells[0]]
	while not queue.is_empty():
		var c: Vector2i = queue.pop_front()
		for d in DIRS4:
			var n := c + d
			if not walls.has(n) and cells.has(n) and not seen.has(n):
				seen[n] = true
				queue.append(n)
	return seen.size() == cells.size()


func _key(me: Vector2i, boxes: Array) -> String:
	var s := boxes.duplicate()
	s.sort()
	return str(me) + str(s)
