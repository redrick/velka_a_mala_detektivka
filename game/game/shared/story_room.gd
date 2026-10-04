@tool
extends PopochiuRoom
## Base for the rooms of story 2 and later (made by tools/popochiu_gen.py). Props and hotspots
## pass their clicks here: override on_click / on_look / on_item, and on_character for the people
## in the room. Shared tricks live here too: darkness with Hanka's torch, floating sound words,
## pop-in props, the flashback slideshow and the end-of-story card.

const Kit := preload("res://game/menu/ui_kit.gd")

var _dark: CanvasModulate
var _torch: PointLight2D


#region Hooks ######################################################################################
func on_click(node: Node) -> void:
	await C.player.walk_to_clicked()
	await C.player.face_clicked()
	await on_look(node)


func on_look(node: Node) -> void:
	await C.player.say(node.description)


## Using an item the room has no special use for counts as clicking (see gui_commands.gd).
func on_item(node: Node, _item: PopochiuInventoryItem) -> void:
	I.deselect_active()
	await on_click(node)


## People in the room. Return true when handled, false to let the character's own script answer.
func on_character(_chr: PopochiuCharacter, _action: String, _item: PopochiuInventoryItem = null) -> bool:
	return false


## Where Joey runs when he is clicked (the next thing to do). Vector2.ZERO = sniff where he is.
func joey_goal() -> Vector2:
	return Vector2.ZERO
#endregion


func _process(_delta: float) -> void:
	if Engine.is_editor_hint() or not is_instance_valid(_torch):
		return
	_torch.global_position = get_global_mouse_position()


#region Helpers #####################################################################################
## Puts a character into this room at `pos` (adding it if needed) and shows it.
func place(chr_name: String, pos: Vector2) -> PopochiuCharacter:
	var chr := C.get_character(chr_name)
	if not has_character(chr_name):
		add_character(chr)
	chr.position = pos
	chr.show()
	return chr


func remove(chr_name: String) -> void:
	if has_character(chr_name):
		remove_character(C.get_character(chr_name))


func dark(color: Color, torch := true) -> void:
	set_meta("mood", "night")
	Music.play("night")
	_dark = CanvasModulate.new()
	_dark.color = color
	add_child(_dark)
	if torch:
		_torch = PointLight2D.new()
		_torch.texture = glow_texture()
		_torch.color = Color(1.0, 0.95, 0.75)
		_torch.energy = 1.8
		_torch.texture_scale = 1.8
		add_child(_torch)
		if not C.player_changed.is_connected(_update_torch):
			C.player_changed.connect(_update_torch)
		_update_torch()


func light_up(secs := 1.5) -> void:
	set_meta("mood", "day")
	Music.play("day")
	if is_instance_valid(_torch):
		_torch.queue_free()
	if is_instance_valid(_dark):
		var tw := create_tween()
		tw.tween_property(_dark, "color", Color.WHITE, secs)
		await tw.finished
		_dark.queue_free()
	C.Hanka.pose()


func is_dark() -> bool:
	return is_instance_valid(_dark)


func glow(pos: Vector2, color: Color, energy := 1.2, size := 2.0) -> PointLight2D:
	var l := PointLight2D.new()
	l.texture = glow_texture()
	l.color = color
	l.energy = energy
	l.texture_scale = size
	l.position = pos
	add_child(l)
	return l


func _update_torch(_old = null, _new = null) -> void:
	if not is_instance_valid(_torch):
		return
	_torch.visible = C.player == C.Hanka
	C.Hanka.pose("torch" if _torch.visible else "happy")


func _on_room_exited() -> void:
	if C.player_changed.is_connected(_update_torch):
		C.player_changed.disconnect(_update_torch)
	C.Hanka.pose()


## A big sound word (ŤUK!, CHRRR…) that floats up and fades.
func sfx(text: String, pos: Vector2, size := 90) -> void:
	var l := Kit.title(tr(text), size)
	l.position = pos
	l.z_index = 50
	add_child(l)
	var tw := create_tween()
	tw.tween_property(l, "position:y", pos.y - 80, 1.4)
	tw.parallel().tween_property(l, "modulate:a", 0.0, 1.4).set_delay(0.6)
	tw.tween_callback(l.queue_free)


## Shows a hidden prop with a little bounce.
func pop(prop_name: String) -> void:
	var prop := get_prop(prop_name)
	var target: Vector2 = prop.scale
	prop.scale = Vector2.ZERO
	prop.show()
	var tw := create_tween()
	tw.tween_property(prop, "scale", target, 0.35).set_trans(Tween.TRANS_BACK).set_ease(Tween.EASE_OUT)
	await tw.finished


## A fade to black and back, with the room changed in between by `middle`.
func fade(middle: Callable, text := "") -> void:
	G.block()
	await T.play_transition("fade", 0.8, T.PLAY_MODE.OUT)
	var card: CanvasLayer = null
	if text != "":
		card = _card([text], 0.0)
		await get_tree().create_timer(1.6).timeout
	await middle.call()
	if card:
		card.queue_free()
	await T.play_transition("fade", 0.8, T.PLAY_MODE.IN)
	G.unblock()


## Old-photo slides in front of the room while the lines are spoken: [[image, speaker, text], ...].
## A slide stays until its line is done; speaker "" keeps the previous picture silent for a moment.
func slideshow(steps: Array) -> void:
	var pic := Sprite2D.new()
	pic.position = Vector2(960, 540)
	pic.z_index = 100
	pic.modulate.a = 0.0
	add_child(pic)
	var tw := create_tween()
	tw.tween_property(pic, "modulate:a", 1.0, 0.6)
	for step in steps:
		if step[0] != "":
			pic.texture = load("res://assets/slides/%s.png" % step[0])
		if step[1] == "":
			await get_tree().create_timer(1.2).timeout
		else:
			await C.get_character(step[1]).say(step[2])
	tw = create_tween()
	tw.tween_property(pic, "modulate:a", 0.0, 0.6)
	await tw.finished
	pic.queue_free()


## A paper card with a few lines (the riddle): stays until clicked.
func paper(lines: Array, title := "") -> void:
	var layer := CanvasLayer.new()
	layer.layer = 40
	add_child(layer)
	var shade := ColorRect.new()
	shade.color = Color(0, 0, 0, 0.4)
	shade.set_anchors_preset(Control.PRESET_FULL_RECT)
	layer.add_child(shade)
	var sheet := Kit.panel()
	sheet.theme = Kit.theme()
	sheet.custom_minimum_size = Vector2(1000, 0)
	sheet.position = Vector2(460, 220)
	layer.add_child(sheet)
	var col := VBoxContainer.new()
	col.add_theme_constant_override("separation", 14)
	sheet.add_child(col)
	if title != "":
		col.add_child(Kit.title(tr(title), 54))
	for l in lines:
		col.add_child(Kit.label(tr(l), 44))
	col.add_child(Kit.label(tr("(klikni)"), 24, Color("8a7f6a")))
	await _next_click(shade)
	layer.queue_free()


## A big picture (the map…) on paper until clicked.
func picture(path: String, caption := "") -> void:
	var layer := CanvasLayer.new()
	layer.layer = 40
	add_child(layer)
	var shade := ColorRect.new()
	shade.color = Color(0, 0, 0, 0.45)
	shade.set_anchors_preset(Control.PRESET_FULL_RECT)
	layer.add_child(shade)
	var img := TextureRect.new()
	img.texture = load(path)
	img.expand_mode = TextureRect.EXPAND_IGNORE_SIZE
	img.stretch_mode = TextureRect.STRETCH_KEEP_ASPECT_CENTERED
	img.position = Vector2(360, 120)
	img.size = Vector2(1200, 800)
	img.mouse_filter = Control.MOUSE_FILTER_IGNORE
	layer.add_child(img)
	if caption != "":
		var l := Kit.title(tr(caption), 50)
		l.position = Vector2(0, 940)
		l.size = Vector2(1920, 80)
		layer.add_child(l)
	await _next_click(shade)
	layer.queue_free()


## Waits for a click on `c` (with automatic text: at most a few seconds).
func _next_click(c: Control) -> void:
	var got := [false]
	var f := func(e: InputEvent):
		if e is InputEventMouseButton and e.pressed:
			got[0] = true
	c.gui_input.connect(f)
	var left := 6.0
	while not got[0] and (not Prefs.auto_continue or left > 0):
		await get_tree().process_frame
		left -= get_process_delta_time()
	c.gui_input.disconnect(f)


## Title card over everything ("Pokračování příště…"); fades out after `secs` (0 = stays).
func _card(lines: Array, secs: float) -> CanvasLayer:
	var layer := CanvasLayer.new()
	layer.layer = 50
	add_child(layer)
	var shade := ColorRect.new()
	shade.color = Color(0, 0, 0, 0.6)
	shade.set_anchors_preset(Control.PRESET_FULL_RECT)
	shade.mouse_filter = Control.MOUSE_FILTER_IGNORE
	layer.add_child(shade)
	var col := VBoxContainer.new()
	col.alignment = BoxContainer.ALIGNMENT_CENTER
	col.set_anchors_preset(Control.PRESET_FULL_RECT)
	col.mouse_filter = Control.MOUSE_FILTER_IGNORE
	col.add_theme_constant_override("separation", 50)
	col.theme = Kit.theme()
	for i in lines.size():
		col.add_child(Kit.title(tr(lines[i]), 100 if i == 0 else 64))
	layer.add_child(col)
	if secs > 0:
		var tw := create_tween()
		tw.tween_interval(secs)
		tw.tween_property(col, "modulate:a", 0.0, 0.8)
		tw.parallel().tween_property(shade, "modulate:a", 0.0, 0.8)
		tw.tween_callback(layer.queue_free)
	return layer


## The end of a story: the card, then the save is marked finished and we go back to the menu.
func the_end(part_line: String) -> void:
	Globals.game_finished = true
	Globals.phase = ""
	Globals.save_now()
	_card(["Pokračování příště…", part_line], 6.0)
	await get_tree().create_timer(7.0).timeout
	Globals.go_to_menu()


func glow_texture() -> GradientTexture2D:
	var g := Gradient.new()
	g.set_color(0, Color(1, 1, 1, 1))
	g.set_color(1, Color(0, 0, 0, 0))
	var tex := GradientTexture2D.new()
	tex.gradient = g
	tex.fill = GradientTexture2D.FILL_RADIAL
	tex.fill_from = Vector2(0.5, 0.5)
	tex.fill_to = Vector2(1.0, 0.5)
	tex.width = 256
	tex.height = 256
	return tex
#endregion
