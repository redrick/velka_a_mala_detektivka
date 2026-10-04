extends CanvasLayer
## Shared frame for the logic minigames: a paper sheet over the room with a title, a one-line
## task, the board, a line where Joey or a sister comments, and Zpět / Znovu / Joey poradí buttons.
## Mouse and keyboard both work: arrows or WASD, Z or Backspace = back, R = again, H = hint,
## Enter or Space = the game's main action. There is no way to lose: back and again are always there.
##
## A game extends this, fills LEVELS and overrides the `_` hooks below. Start one with
## `var mg := Trap.new(); add_child(mg); await mg.finished`.

signal finished

const Kit := preload("res://game/menu/ui_kit.gd")
const ART := "res://assets/minigames/"
const TILE := 112.0
const KEYS := {
	KEY_UP: Vector2i.UP, KEY_W: Vector2i.UP, KEY_DOWN: Vector2i.DOWN, KEY_S: Vector2i.DOWN,
	KEY_LEFT: Vector2i.LEFT, KEY_A: Vector2i.LEFT, KEY_RIGHT: Vector2i.RIGHT, KEY_D: Vector2i.RIGHT,
}

## True when started from the main menu's test list: shows a "Zavřít" button.
var closable := false
var level := 0
## Board cell size in px; a game may set a bigger one in _build before placing pieces.
var tile := TILE
var board: Control
var busy := false

var _count: Label
var _task: Label
var _line: Label
var _extra: HBoxContainer


#region Hooks for the games ######################################################################
func _title() -> String: return ""
func _task_text() -> String: return ""
func _levels() -> int: return 1
func _build(_i: int) -> void: pass
func _dir(_d: Vector2i) -> void: pass
func _cell(_c: Vector2i) -> void: pass
func _action() -> void: pass
func _undo() -> void: pass
func _hint() -> void: pass
#endregion


func _ready() -> void:
	add_to_group("minigame")
	layer = 60
	var shade := ColorRect.new()
	shade.color = Color(0, 0, 0, 0.45)
	shade.set_anchors_preset(Control.PRESET_FULL_RECT)
	add_child(shade)

	var sheet := Kit.panel()
	sheet.theme = Kit.theme()
	sheet.position = Vector2(70, 24)
	sheet.size = Vector2(1780, 1032)
	add_child(sheet)
	var col := VBoxContainer.new()
	col.add_theme_constant_override("separation", 8)
	sheet.add_child(col)

	var top := HBoxContainer.new()
	col.add_child(top)
	var heading := Kit.title(tr(_title()), 56)
	heading.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	heading.horizontal_alignment = HORIZONTAL_ALIGNMENT_LEFT
	top.add_child(heading)
	_count = Kit.label("", 34)
	top.add_child(_count)
	if closable:
		top.add_child(Kit.button(tr("Zavřít"), _close, 28))

	_task = Kit.label(tr(_task_text()), 30)
	_task.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART
	col.add_child(_task)

	var middle := CenterContainer.new()
	middle.size_flags_vertical = Control.SIZE_EXPAND_FILL
	col.add_child(middle)
	board = Control.new()
	board.mouse_filter = Control.MOUSE_FILTER_STOP
	board.gui_input.connect(_on_board_input)
	middle.add_child(board)

	_extra = HBoxContainer.new()
	_extra.alignment = BoxContainer.ALIGNMENT_CENTER
	_extra.add_theme_constant_override("separation", 14)
	col.add_child(_extra)

	var bottom := HBoxContainer.new()
	bottom.add_theme_constant_override("separation", 16)
	col.add_child(bottom)
	var joey := TextureRect.new()
	joey.texture = load("res://assets/characters/joey_sniff.png")
	joey.expand_mode = TextureRect.EXPAND_IGNORE_SIZE
	joey.stretch_mode = TextureRect.STRETCH_KEEP_ASPECT_CENTERED
	joey.custom_minimum_size = Vector2(120, 80)
	bottom.add_child(joey)
	_line = Kit.label("", 32)
	_line.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	_line.horizontal_alignment = HORIZONTAL_ALIGNMENT_LEFT
	_line.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART
	bottom.add_child(_line)
	bottom.add_child(Kit.button(tr("↶ Zpět"), func(): if not busy: _undo(), 30))
	bottom.add_child(Kit.button(tr("Znovu"), func(): if not busy: start_level(level), 30))
	bottom.add_child(Kit.button(tr("Joey poradí"), func(): if not busy: _hint(), 30))
	start_level(0)


func start_level(i: int) -> void:
	level = i
	busy = false
	for c in board.get_children():
		c.queue_free()
	for c in _extra.get_children():
		c.queue_free()
	_count.text = "%d / %d" % [i + 1, _levels()]
	say("")
	_build(i)


## The bottom line: Joey's hints and the girls' comments.
func say(text: String) -> void:
	_line.text = tr(text)


## Adds a button under the board (for games that need more than the board).
func extra_button(text: String, on_press: Callable, size := 30) -> Button:
	var b := Kit.button(tr(text), on_press, size)
	_extra.add_child(b)
	return b


func extra_node(c: Control) -> void:
	_extra.add_child(c)


## A picture filling one board cell; `z` orders layers (floor 0, pieces 2...).
func piece(tex_name: String, cell: Vector2i, z := 0, rot := 0.0) -> TextureRect:
	var t := TextureRect.new()
	t.texture = load(tex_name if tex_name.begins_with("res://") else ART + tex_name + ".png")
	t.expand_mode = TextureRect.EXPAND_IGNORE_SIZE
	t.stretch_mode = TextureRect.STRETCH_KEEP_ASPECT_CENTERED
	t.size = Vector2(tile, tile)
	t.pivot_offset = Vector2(tile, tile) / 2.0
	t.rotation_degrees = rot
	t.position = cell_pos(cell)
	t.z_index = z
	t.mouse_filter = Control.MOUSE_FILTER_IGNORE
	board.add_child(t)
	return t


## A character sprite standing in a cell (feet near the bottom of the cell).
func figure(path: String, cell: Vector2i, height := -1.0) -> TextureRect:
	if height < 0:
		height = tile * 1.25
	var t := TextureRect.new()
	t.texture = load(path)
	t.expand_mode = TextureRect.EXPAND_IGNORE_SIZE
	t.stretch_mode = TextureRect.STRETCH_KEEP_ASPECT_CENTERED
	t.size = Vector2(tile, height)
	t.z_index = 5
	t.mouse_filter = Control.MOUSE_FILTER_IGNORE
	t.position = figure_pos(cell, t)
	board.add_child(t)
	return t


## A yellow rounded frame (selection); move it with `frame.position = cell_pos(c)`.
func frame(color := Color("ffd43b")) -> Panel:
	var f := Panel.new()
	var sb := StyleBoxFlat.new()
	sb.bg_color = Color(0, 0, 0, 0)
	sb.border_color = color
	sb.set_border_width_all(6)
	sb.set_corner_radius_all(14)
	f.add_theme_stylebox_override("panel", sb)
	f.size = Vector2(tile, tile)
	f.z_index = 6
	f.mouse_filter = Control.MOUSE_FILTER_IGNORE
	board.add_child(f)
	return f


func cell_pos(c: Vector2i) -> Vector2:
	return Vector2(c) * tile


func figure_pos(c: Vector2i, t: Control) -> Vector2:
	return cell_pos(c) + Vector2(0, tile - t.size.y - 6)


func set_board_size(cols: int, rows: int) -> void:
	board.custom_minimum_size = Vector2(cols, rows) * tile
	board.size = board.custom_minimum_size


func slide(node: Control, to: Vector2, secs := 0.14) -> Tween:
	var tw := create_tween()
	tw.tween_property(node, "position", to, secs)
	return tw


## A little shake: the move was not possible.
func bump(node: Control) -> void:
	var p := node.position
	var tw := create_tween()
	tw.tween_property(node, "position:x", p.x + 8, 0.05)
	tw.tween_property(node, "position:x", p.x - 8, 0.08)
	tw.tween_property(node, "position:x", p.x, 0.05)


## Level solved: a cheer, then the next level, or the end.
func level_done(cheer := "Hurá!") -> void:
	busy = true
	say(cheer)
	var star_label := Kit.title("★", 160)
	star_label.position = board.size / 2.0 - Vector2(80, 110)
	star_label.pivot_offset = Vector2(80, 110)
	star_label.scale = Vector2.ZERO
	star_label.z_index = 20
	board.add_child(star_label)
	var tw := create_tween()
	tw.tween_property(star_label, "scale", Vector2.ONE, 0.35).set_trans(Tween.TRANS_BACK).set_ease(Tween.EASE_OUT)
	tw.tween_interval(1.3)
	await tw.finished
	if level + 1 < _levels():
		start_level(level + 1)
	else:
		_close()


func _close() -> void:
	finished.emit()
	queue_free()


func _on_board_input(event: InputEvent) -> void:
	if busy:
		return
	if event is InputEventMouseButton and event.pressed and event.button_index == MOUSE_BUTTON_LEFT:
		var c := Vector2i((event.position / tile).floor())
		_cell(c)


func _input(event: InputEvent) -> void:
	if not event is InputEventKey or not event.pressed or event.echo:
		return
	get_viewport().set_input_as_handled()
	if busy:
		return
	var k: Key = event.keycode
	if KEYS.has(k):
		_dir(KEYS[k])
	elif k in [KEY_ENTER, KEY_KP_ENTER, KEY_SPACE]:
		_action()
	elif k in [KEY_Z, KEY_BACKSPACE]:
		_undo()
	elif k == KEY_R:
		start_level(level)
	elif k == KEY_H:
		_hint()
	elif k == KEY_ESCAPE and closable:
		_close()
