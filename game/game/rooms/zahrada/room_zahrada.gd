# @popochiu-docs-ignore-class
@tool
extends PopochiuRoom

const Data := preload('room_zahrada_state.gd')
const Kit := preload("res://game/menu/ui_kit.gd")
const WINDOWS := [Vector2(1442, 558), Vector2(1630, 558)]

var state: Data = load("res://game/rooms/zahrada/room_zahrada.tres")
var _night_nodes: Array[Node] = []


#region Virtual ####################################################################################
func _on_room_entered() -> void:
	match C.player.last_room:
		"Kuchyne": C.player.position = get_marker_position("ZKuchyne")
		"Zahumenek": C.player.position = get_marker_position("ZeZahumenku")
		_: C.player.position = get_marker_position("Start")
	if Globals.phase == "ending":
		C.player.position = get_marker_position("Konec")
	Globals.bring_sister(self)
	if Globals.trap_planned and not Globals.shed_done and has_character("Babicka"):
		remove_character(C.Babicka)
	if Globals.shed_done:
		_bring_grandparents()
	_show_birdhouse()
	get_prop("Stopy").visible = Globals.footprints_found
	get_prop("Ponozka").visible = not Globals.joey_cleared
	get_prop("Silueta").hide()
	_show_trap_props()
	Globals.exit_arrow(self, "Cesta", true, Globals.thread_found)
	if Globals.phase == "night":
		_setup_night()


func _on_room_transition_finished() -> void:
	if Globals.phase == "night":
		await _play_night()
	elif Globals.phase == "ending":
		await _play_ending()


func _on_room_exited() -> void:
	pass


#endregion

#region Public #####################################################################################
func hit_nail(n: int) -> void:
	var nail := get_prop("Hrebik%d" % n)
	if Globals.phase != "nails" or not nail.visible:
		return
	await C.player.face_clicked()
	var tw := create_tween()
	tw.tween_property(nail, "position:y", nail.position.y + 26.0, 0.12)
	tw.tween_property(nail, "scale:y", nail.scale.y * 0.3, 0.08)
	var budka := get_prop("Budka")
	tw.parallel().tween_property(budka, "rotation", 0.03, 0.06)
	tw.tween_property(budka, "rotation", 0.0, 0.06)
	await C.player.say("Ťuk!")
	nail.hide()
	Globals.nails_done += 1
	if Globals.nails_done == 3:
		await _finish_story()


#endregion

#region Private ####################################################################################
func _bring_grandparents() -> void:
	for pair in [["Babicka", Vector2(1420, 830)], ["Deda", Vector2(1600, 840)]]:
		var chr := C.get_character(pair[0])
		if not has_character(pair[0]):
			add_character(chr)
		chr.position = pair[1]
		chr.show()


func _show_birdhouse() -> void:
	var building := Globals.phase == "ending" or Globals.phase == "nails"
	get_prop("Budka").visible = Globals.game_finished or Globals.phase == "nails"
	for i in range(1, 4):
		get_prop("Hrebik%d" % i).visible = Globals.phase == "nails" and i > Globals.nails_done
	if building:
		_place_nails()


func _place_nails() -> void:
	var budka := get_prop("Budka")
	var center: Vector2 = budka.get_node("Sprite2D").global_position
	var offsets := [Vector2(-85, -30), Vector2(85, -30), Vector2(-60, 70)]
	for i in range(1, 4):
		var nail := get_prop("Hrebik%d" % i)
		nail.global_position = center + offsets[i - 1] + Vector2(0, nail.baseline * nail.scale.y)


func _play_ending() -> void:
	C.player.face_right()
	await C.Alica.say("Babi, dědo! Víme, kdo bral ponožky!")
	C.Hanka.pose("grin")
	await C.Hanka.say("Plšíci! Mají hnízdo v botě.")
	C.Hanka.pose()
	await C.Babicka.say("Plši? Chudáci, jen si chystali pelíšek na zimu.")
	await C.Deda.say("Tak jim postavíme domeček, ať nemusí brát ponožky!")
	var budka := get_prop("Budka")
	var target: Vector2 = budka.scale
	budka.scale = Vector2.ZERO
	budka.show()
	var pop := create_tween()
	pop.tween_property(budka, "scale", target, 0.4).set_trans(Tween.TRANS_BACK).set_ease(Tween.EASE_OUT)
	await pop.finished
	Globals.phase = "nails"
	Globals.nails_done = 0
	_place_nails()
	for i in range(1, 4):
		get_prop("Hrebik%d" % i).show()
	await C.Deda.say("Zatlučte tři hřebíky. Ťuk, ťuk, ťuk!")


func _finish_story() -> void:
	await C.Deda.say("Hotovo! Domeček pro plšíky.")
	await C.Hanka.say("Dědo, a tohle bylo v botě!")
	await C.Deda.say("Ukaž… To je přece klíč od Klubu Hvězdička!")
	await C.Deda.say("Ztratil jsem ho, když jsem byl malý kluk. Co asi odemyká?")
	C.Alica.pose("grin")
	await C.Alica.say("To je další případ pro detektivky Alicu a Hanku!")
	C.Alica.pose()
	Globals.game_finished = true
	Globals.phase = ""
	await _show_the_end()


func _show_the_end() -> void:
	var layer := CanvasLayer.new()
	layer.layer = 50
	add_child(layer)
	var shade := ColorRect.new()
	shade.color = Color(0, 0, 0, 0.55)
	shade.set_anchors_preset(Control.PRESET_FULL_RECT)
	shade.mouse_filter = Control.MOUSE_FILTER_IGNORE
	layer.add_child(shade)
	var label := VBoxContainer.new()
	label.alignment = BoxContainer.ALIGNMENT_CENTER
	label.set_anchors_preset(Control.PRESET_FULL_RECT)
	label.mouse_filter = Control.MOUSE_FILTER_IGNORE
	label.add_theme_constant_override("separation", 60)
	label.theme = Kit.theme()
	label.add_child(Kit.title(tr("Pokračování příště…"), 110))
	label.add_child(Kit.title(tr("Konec 1. dílu"), 70))
	layer.add_child(label)
	layer.follow_viewport_enabled = false
	var tw := create_tween()
	layer.offset = Vector2.ZERO
	shade.modulate.a = 0.0
	label.modulate.a = 0.0
	tw.tween_property(shade, "modulate:a", 1.0, 1.0)
	tw.parallel().tween_property(label, "modulate:a", 1.0, 1.0)
	tw.tween_interval(6.0)
	tw.tween_property(shade, "modulate:a", 0.0, 1.0)
	tw.parallel().tween_property(label, "modulate:a", 0.0, 1.0)
	await tw.finished
	layer.queue_free()
	Globals.go_to_menu()


func _show_trap_props() -> void:
	get_prop("Past").visible = Globals.trap_set
	get_prop("Navnada").visible = Globals.trap_set and not Globals.night_done
	get_prop("MoucneStopy").visible = Globals.night_done
	get_prop("Nitka").visible = Globals.night_done and not Globals.thread_found


func _setup_night() -> void:
	set_meta("mood", "night")
	Music.play("night")
	C.Alica.hide()
	C.Hanka.hide()
	C.Tonda.hide()
	C.Joey.pose("sleepy")
	get_prop("Navnada").show()
	var tint := CanvasModulate.new()
	tint.color = Color(0.3, 0.34, 0.6)
	add_child(tint)
	_night_nodes.append(tint)
	for pos: Vector2 in WINDOWS:
		var light := PointLight2D.new()
		light.texture = _glow_texture()
		light.color = Color(1.0, 0.8, 0.45)
		light.energy = 1.6
		light.texture_scale = 1.3
		light.position = pos
		add_child(light)
		_night_nodes.append(light)


func _play_night() -> void:
	G.block()
	var mouse := get_prop("Silueta")
	mouse.show()
	var tw := create_tween()
	tw.tween_property(mouse, "position:x", 1110.0, 5.0)
	await tw.finished
	await get_tree().create_timer(0.8).timeout
	get_prop("Navnada").hide()
	tw = create_tween()
	tw.tween_property(mouse, "position:x", -200.0, 6.0)
	await tw.finished

	await T.play_transition("fade", 1.0, T.PLAY_MODE.OUT)
	_setup_morning()
	await T.play_transition("fade", 1.0, T.PLAY_MODE.IN)
	G.unblock()

	C.Alica.pose("surprised")
	await C.Alica.say("Ponožka zmizela!")
	C.Hanka.pose("point")
	await C.Hanka.say("Koukej! Stopy v mouce!")
	C.Alica.pose("think")
	await C.Alica.say("Malinkaté tlapky… a vedou pryč, k zahumenku.")
	C.Alica.pose()
	C.Hanka.pose()


func _setup_morning() -> void:
	Music.play("day")
	for n in _night_nodes:
		n.queue_free()
	_night_nodes.clear()
	get_prop("Silueta").hide()
	C.Joey.pose()
	C.Tonda.show()
	C.player.position = get_marker_position("ZKuchyne")
	Globals.sister().position = C.player.position + Vector2(-170, 10)
	C.Alica.show()
	C.Hanka.show()
	Globals.night_done = true
	Globals.phase = ""
	_show_trap_props()


func _glow_texture() -> GradientTexture2D:
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
