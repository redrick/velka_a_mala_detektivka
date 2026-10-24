extends "res://game/minigames/minigame_base.gd"
## Story 5 "Postav sněhuláka": the girls answer Bětka's snowmen with snowmen of their own. Hanka rolls
## snowballs: on fresh snow a ball grows (small → middle → big) and leaves green grass behind, on grass it
## stays the same. Push a smaller ball onto a bigger one to stack it. A snowman is big + middle + small.
## A ball can be pushed, never pulled, and a stack doesn't move. Arrows/WASD walk; a click on a
## neighbouring square steps there.
## Levels: # bush, . grass, * snow, P Hanka, 1/2/3 a small/middle/big ball (on grass).

const LEVELS := [
	[
		"########",
		"#......#",
		"#P1*.3.#",
		"#......#",
		"#....1.#",
		"#......#",
		"########",
	],
	[
		"########",
		"#*****.#",
		"#*1..*.#",
		"#P.#.**#",
		"#.1.*3.#",
		"#..*...#",
		"########",
	],
	[
		"#########",
		"#*.*.*.*#",
		"#.#.#.#.#",
		"#*.1P1.*#",
		"#.#.#.#.#",
		"#*.*1*.*#",
		"#########",
	],
]
## Shortest solutions from the start (tools/check_levels.py prints them): the hint follows these
## while the player's moves match, and searches a little otherwise.
const SOLUTIONS := [
	"→→→↓↓↓→↑↑",
	"↓→→→↑↑←↑←↓↓←↓→→→",
	"→→←↑↑→→↓↓↓↑←←←←↓↓→→→←←←←←↑↑→→→→→←↑↑→→↓↓↓",
]
const ARROW := {"→": Vector2i.RIGHT, "←": Vector2i.LEFT, "↓": Vector2i.DOWN, "↑": Vector2i.UP}
const HINTS := [
	"Na sněhu koule roste. Malou kouli kutálej přes sníh, ať je prostřední!",
	"Nejdřív velkou kouli. Prostřední na ni. A malou úplně nahoru.",
	"Sníh nekutálej zbytečně: koule větší než velká už nebude, ale sníh zmizí.",
]
const DIRS4: Array[Vector2i] = [Vector2i.RIGHT, Vector2i.LEFT, Vector2i.DOWN, Vector2i.UP]
const WAY := [
	"doprava",
	"doleva",
	"dolů",
	"nahoru",
]

var _walls := {}
var _snow := {}
var _balls := {}          # Vector2i -> Array of sizes, bottom first
var _me := Vector2i.ZERO
var _history: Array = []
var _moves: Array = []
var _size := Vector2i.ZERO
var _floor := {}          # Vector2i -> TextureRect (snow or grass)
var _ball_nodes: Array = []
var _me_node: TextureRect


func _title() -> String: return tr("Postav sněhuláka")
func _task_text() -> String: return tr("Kutálej koule. Na sněhu rostou. Postav sněhuláka: velkou, prostřední a malou kouli na sebe!")
func _levels() -> int: return LEVELS.size()


func _build(i: int) -> void:
	tile = 104.0
	_walls.clear(); _snow.clear(); _balls.clear(); _history.clear(); _floor.clear(); _ball_nodes.clear(); _moves.clear()
	var rows: Array = LEVELS[i]
	_size = Vector2i((rows[0] as String).length(), rows.size())
	set_board_size(_size.x, _size.y)
	for y in rows.size():
		for x in (rows[y] as String).length():
			var c := Vector2i(x, y)
			var ch: String = rows[y][x]
			if ch == "#":
				_walls[c] = true
				piece("snowbush", c)
				continue
			if ch == "*":
				_snow[c] = true
			_floor[c] = piece(("snow" if (x + y) % 2 == 0 else "snow_b") if ch == "*" else "cleared", c)
			if ch == "P":
				_me = c
			elif ch in ["1", "2", "3"]:
				_balls[c] = [int(ch)]
	_me_node = figure("res://assets/characters/hankaw_happy.png", _me)
	_draw()


func _draw() -> void:
	for n in _ball_nodes:
		n.queue_free()
	_ball_nodes.clear()
	for c in _floor:
		(_floor[c] as TextureRect).texture = load(ART + ((("snow" if (c.x + c.y) % 2 == 0 else "snow_b") if _snow.has(c) else "cleared")) + ".png")
	for c in _balls:
		var st: Array = _balls[c]
		var tex := "ball%d" % st[0] if st.size() == 1 else "stack%d" % st.size()
		var p := piece(tex, c, 3)
		if st.size() > 1:
			p.size = Vector2(tile, tile * 1.4)
			p.position.y -= tile * 0.4
		_ball_nodes.append(p)
	_me_node.position = figure_pos(_me, _me_node)


## One move as in the Python solver (tools/check_levels.py); returns the new state or {} when blocked.
static func step(walls: Dictionary, size: Vector2i, me: Vector2i, snow: Dictionary, balls: Dictionary, d: Vector2i) -> Dictionary:
	var t := me + d
	if walls.has(t) or t.x < 0 or t.y < 0 or t.x >= size.x or t.y >= size.y:
		return {}
	var nb := balls.duplicate(true)
	var ns := snow.duplicate()
	if nb.has(t):
		var st: Array = nb[t]
		if st.size() > 1:
			return {}
		var n := t + d
		if walls.has(n) or n.x < 0 or n.y < 0 or n.x >= size.x or n.y >= size.y:
			return {}
		var s: int = st[0]
		if nb.has(n):
			var st2: Array = nb[n]
			if st2.size() >= 3 or st2[-1] <= s:
				return {}
			nb.erase(t)
			st2.append(s)
		else:
			nb.erase(t)
			if ns.has(n):
				s = mini(3, s + 1)
				ns.erase(n)
			nb[n] = [s]
	return {"me": t, "snow": ns, "balls": nb}


static func is_won(balls: Dictionary) -> bool:
	for c in balls:
		if balls[c] == [3, 2, 1]:
			return true
	return false


func _move(d: Vector2i) -> void:
	var r := step(_walls, _size, _me, _snow, _balls, d)
	if r.is_empty():
		bump(_me_node)
		return
	_history.append([_me, _snow.duplicate(), _balls.duplicate(true)])
	_moves.append(d)
	var grew := false
	for c in r.balls:
		if not _balls.has(c) and _snow.has(c):
			grew = true
	_me = r.me
	_snow = r.snow
	_balls = r.balls
	_draw()
	if is_won(_balls):
		level_done("Sněhulák stojí! Ahoj, sněhuláku!")
	elif grew:
		say("Koule na sněhu vyrostla!")
	else:
		say("")


func _dir(d: Vector2i) -> void:
	_move(d)


func _cell(c: Vector2i) -> void:
	var d := c - _me
	if absi(d.x) + absi(d.y) == 1:
		_move(d)


func _undo() -> void:
	if _history.is_empty():
		return
	var h: Array = _history.pop_back()
	_moves.pop_back()
	_me = h[0]
	_snow = h[1]
	_balls = h[2]
	_draw()
	say("")


func _key(me: Vector2i, snow: Dictionary, balls: Dictionary) -> String:
	var bs := []
	for c in balls:
		bs.append("%d,%d:%s" % [c.x, c.y, str(balls[c])])
	bs.sort()
	var ss := []
	for c in snow:
		ss.append("%d,%d" % [c.x, c.y])
	ss.sort()
	return "%d,%d|%s|%s" % [me.x, me.y, ",".join(bs), ",".join(ss)]


## The first moves of a shortest solution from here (breadth-first, capped).
func _solve() -> Array:
	var known: Array = []
	for ch in SOLUTIONS[level]:
		known.append(ARROW[ch])
	if _moves.size() <= known.size() and known.slice(0, _moves.size()) == _moves:
		return known.slice(_moves.size())
	var start := {"me": _me, "snow": _snow, "balls": _balls}
	var seen := {_key(_me, _snow, _balls): []}
	var queue := [start]
	var qi := 0
	while qi < queue.size() and seen.size() < 20000:
		var s: Dictionary = queue[qi]
		qi += 1
		var path: Array = seen[_key(s.me, s.snow, s.balls)]
		if is_won(s.balls):
			return path
		for d in DIRS4:
			var n := step(_walls, _size, s.me, s.snow, s.balls, d)
			if n.is_empty():
				continue
			var k := _key(n.me, n.snow, n.balls)
			if not seen.has(k):
				seen[k] = path + [d]
				queue.append(n)
	return []


func _hint() -> void:
	var sol := _solve()
	if sol.is_empty():
		say("Takhle už to nepůjde. Zkus Zpět nebo Znovu.")
		return
	say(tr(HINTS[level]) + " " + tr("Teď zkus: %s.") % tr(WAY[DIRS4.find(sol[0])]))


func solve_for_test() -> void:
	for d in _solve():
		_move(d)
		await get_tree().create_timer(0.05).timeout
