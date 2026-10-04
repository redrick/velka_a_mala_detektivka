# @popochiu-docs-ignore-class
@tool
extends PopochiuRoom

const Data := preload('room_kulna_state.gd')
const DARK := Color(0.1, 0.1, 0.18)

var state: Data = load("res://game/rooms/kulna/room_kulna.tres")
var _dark: CanvasModulate
var _torch: PointLight2D


#region Virtual ####################################################################################
func _process(_delta: float) -> void:
	if Engine.is_editor_hint() or not is_instance_valid(_torch):
		return
	_torch.global_position = get_global_mouse_position()


func _on_room_entered() -> void:
	Globals.exit_arrow(self, "Ven", true)
	C.player.position = get_marker_position("Vstup")
	Globals.bring_sister(self, Vector2(170, 10))
	for n in ["Plsik1", "Plsik2", "Hnizdo"]:
		get_prop(n).visible = Globals.shed_done
	if not Globals.shed_done:
		_setup_dark()
	if not C.player_changed.is_connected(_on_player_changed):
		C.player_changed.connect(_on_player_changed)
	_update_torch()


func _on_room_transition_finished() -> void:
	if Globals.shed_done:
		return
	await C.Alica.say("Tady je tma jako v pytli!")
	if C.player == C.Hanka:
		await C.Hanka.say("Posvítím baterkou!")
	else:
		await C.Hanka.say("Klikni na mě, já mám baterku!")


func _on_room_exited() -> void:
	if C.player_changed.is_connected(_on_player_changed):
		C.player_changed.disconnect(_on_player_changed)
	C.Hanka.pose()


#endregion

#region Public #####################################################################################
func reveal() -> void:
	await C.Hanka.say("Tam! V botě!")
	await C.Alica.say("Rozsvítím!")
	_torch.hide()
	Music.play("day")
	var tw := create_tween()
	tw.tween_property(_dark, "color", Color.WHITE, 1.5)
	await tw.finished
	C.Hanka.pose()
	for n in ["Hnizdo", "Plsik1", "Plsik2"]:
		var prop := get_prop(n)
		var target: Vector2 = prop.scale
		prop.scale = Vector2.ZERO
		prop.show()
		var pop := create_tween()
		pop.tween_property(prop, "scale", target, 0.35).set_trans(Tween.TRANS_BACK).set_ease(Tween.EASE_OUT)
		await pop.finished
	C.Alica.pose("surprised")
	await C.Alica.say("Plši! To oni brali ponožky!")
	C.Hanka.pose("grin")
	await C.Hanka.say("Mají z nich hnízdo! Je jim zima.")
	C.Alica.pose()
	await C.Alica.say("Nejsou to zloději. Jen si stavěli teplý pelíšek na zimu.")
	C.Hanka.pose("surprised")
	await C.Hanka.say("A v botě je ještě něco… klíč!")
	C.Hanka.pose()
	await I.Klic.add()
	await C.Alica.say("Klíč s hvězdičkou? Musíme ho ukázat dědovi!")
	Globals.shed_done = true
	Globals.phase = "ending"
	R.goto_room("Zahrada")


#endregion

#region Private ####################################################################################
func _setup_dark() -> void:
	set_meta("mood", "night")
	Music.play("night")
	_dark = CanvasModulate.new()
	_dark.color = DARK
	add_child(_dark)
	var door_light := PointLight2D.new()
	door_light.texture = _glow_texture()
	door_light.color = Color(1.0, 0.85, 0.6)
	door_light.energy = 0.9
	door_light.texture_scale = 3.0
	door_light.position = Vector2(80, 620)
	add_child(door_light)
	_torch = PointLight2D.new()
	_torch.texture = _glow_texture()
	_torch.color = Color(1.0, 0.95, 0.75)
	_torch.energy = 1.8
	_torch.texture_scale = 1.6
	add_child(_torch)


func _update_torch() -> void:
	var lit := C.player == C.Hanka and not Globals.shed_done
	if is_instance_valid(_torch):
		_torch.visible = lit
	C.Hanka.pose("torch" if lit else "happy")


func _on_player_changed(_old: PopochiuCharacter, _new: PopochiuCharacter) -> void:
	_update_torch()


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
