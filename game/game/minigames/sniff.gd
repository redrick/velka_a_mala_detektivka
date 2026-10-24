extends "res://game/minigames/minigame_base.gd"
## Story 7 "Čmuchej!": the player is Joey's nose. Click a square of snow (in the last level a block of the
## snow fort): Joey sniffs there and says how many steps away the smell is (steps go along rows and
## columns, not diagonally). Two or three sniffs are enough to work out the place: everything that fits
## all the numbers so far. Joey's hint lights up the squares that still fit. Training with a bone and with
## babička's glove first, then the ring in the fort. The hidden thing moves every time a level starts.
## LEVELS: columns, rows, square picture, what is hidden, how it's called.

const LEVELS := [
	[5, 4, "sniff_snow", "find_bone", "kost"],
	[6, 4, "sniff_snow", "find_glove", "rukavici"],
	[7, 4, "sniff_block", "find_ring", "prstýnek"],
]

var _size := Vector2i.ZERO
var _target := Vector2i.ZERO
var _sniffed := {}      # Vector2i -> steps
var _tiles := {}        # Vector2i -> TextureRect
var _cursor := Vector2i.ZERO
var _frame: Panel
var _glow: Array = []
var _rng := RandomNumberGenerator.new()
var _won := false
var fixed_target := Vector2i(-1, -1)   # tests set this to know where it is


func _title() -> String: return tr("Čmuchej!")
func _task_text() -> String:
	return tr("Klikni, kde má Joey čmuchat. Řekne ti, kolik krůčků je to daleko. Krůčky jdou rovně, ne šikmo.")
func _levels() -> int: return LEVELS.size()


func _build(i: int) -> void:
	tile = 150.0
	var lv: Array = LEVELS[i]
	_size = Vector2i(lv[0], lv[1])
	_sniffed.clear(); _tiles.clear(); _glow.clear()
	_won = false
	set_board_size(_size.x, _size.y)
	for y in _size.y:
		for x in _size.x:
			var c := Vector2i(x, y)
			_tiles[c] = piece(lv[2], c)
	_rng.randomize()
	_target = fixed_target if fixed_target.x >= 0 else Vector2i(_rng.randi_range(0, _size.x - 1), _rng.randi_range(0, _size.y - 1))
	_cursor = Vector2i(_size.x / 2, _size.y / 2)
	_frame = frame()
	_frame.position = cell_pos(_cursor)
	say(tr("Joey hledá %s. Čmuch čmuch!") % tr(lv[4]))


static func steps(a: Vector2i, b: Vector2i) -> int:
	return absi(a.x - b.x) + absi(a.y - b.y)


## The places that fit every number Joey has sniffed so far.
func _possible() -> Array:
	var out := []
	for y in _size.y:
		for x in _size.x:
			var c := Vector2i(x, y)
			if _sniffed.has(c):
				continue
			var fits := true
			for s in _sniffed:
				if steps(c, s) != _sniffed[s]:
					fits = false
					break
			if fits:
				out.append(c)
	return out


func _sniff(c: Vector2i) -> void:
	if _won or _sniffed.has(c):
		return
	_clear_glow()
	if c == _target:
		_won = true
		(_tiles[c] as TextureRect).texture = load(ART + LEVELS[level][3] + ".png")
		level_done(tr("HAF! Tady je %s!") % tr(LEVELS[level][4]) if level < 2 else "HAF HAF! Prstýnek s hvězdičkou! Joey má nejlepší nos!")
		return
	var d := steps(c, _target)
	_sniffed[c] = d
	(_tiles[c] as TextureRect).texture = load(ART + "sniff_dug.png")
	var l := Kit.title(str(d), 70)
	l.position = cell_pos(c) + Vector2(0, tile * 0.18)
	l.size = Vector2(tile, tile * 0.6)
	l.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
	l.modulate = Color(0.9, 0.3, 0.2) if d <= 1 else (Color(0.95, 0.6, 0.2) if d <= 3 else Color(0.3, 0.45, 0.8))
	l.z_index = 4
	board.add_child(l)
	var left := _possible()
	if d == 1:
		say("Čmuch! Hodně blízko, jen jeden krůček!")
	elif left.size() == 1:
		say("Joey ví, kde to je! Víš to taky?")
	else:
		say(tr("Čmuch. %d krůčky daleko.") % d if d < 5 else tr("Čmuch… %d krůčků daleko. Daleko.") % d)


func _clear_glow() -> void:
	for g in _glow:
		g.queue_free()
	_glow.clear()


func _cell(c: Vector2i) -> void:
	if c.x < _size.x and c.y < _size.y:
		_cursor = c
		_frame.position = cell_pos(c)
		_sniff(c)


func _dir(d: Vector2i) -> void:
	_cursor = Vector2i(clampi(_cursor.x + d.x, 0, _size.x - 1), clampi(_cursor.y + d.y, 0, _size.y - 1))
	_frame.position = cell_pos(_cursor)


func _action() -> void:
	_sniff(_cursor)


## Joey lights up every place that still fits the numbers.
func _hint() -> void:
	_clear_glow()
	if _sniffed.is_empty():
		say("Začni někde uprostřed. Pak ti Joey řekne, kolik krůčků to je.")
		return
	for c in _possible():
		var f := frame(Color("6cbf5a"))
		f.position = cell_pos(c)
		_glow.append(f)
	if level == 2:
		say("Prstýnek může být jen na zelených místech. Sedí tam všechna čísla.")
	else:
		say("Hledaná věc může být jen na zelených místech. Sedí tam všechna čísla.")


func solve_for_test() -> void:
	_sniff(Vector2i(0, 0))
	await get_tree().create_timer(0.1).timeout
	if not _won:
		_sniff(_target)
