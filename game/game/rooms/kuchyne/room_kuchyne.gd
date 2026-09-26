# @popochiu-docs-ignore-class
@tool
extends PopochiuRoom

const Data := preload('room_kuchyne_state.gd')
const WINDOW_GLASS := Rect2(730, 150, 422, 368)

var state: Data = load("res://game/rooms/kuchyne/room_kuchyne.tres")


#region Virtual ####################################################################################
func _on_room_entered() -> void:
	var evening := Globals.phase == "evening"
	C.player.position = get_marker_position("Okno" if evening else "Vstup")
	Globals.bring_sister(self, Vector2(170, 10) if evening else Vector2(-170, 10))
	get_prop("Mouka").visible = not Globals.got_flour
	get_prop("Hrnek1").visible = evening
	get_prop("Hrnek2").visible = evening
	if evening:
		_setup_evening()


func _on_room_transition_finished() -> void:
	if Globals.phase == "evening":
		await _play_evening()


func _on_room_exited() -> void:
	pass


#endregion

#region Private ####################################################################################
func _setup_evening() -> void:
	var night_sky := Polygon2D.new()
	night_sky.color = Color(0.12, 0.15, 0.35)
	night_sky.polygon = PackedVector2Array([
		WINDOW_GLASS.position, Vector2(WINDOW_GLASS.end.x, WINDOW_GLASS.position.y),
		WINDOW_GLASS.end, Vector2(WINDOW_GLASS.position.x, WINDOW_GLASS.end.y),
	])
	night_sky.z_index = -1
	add_child(night_sky)
	var moon := Polygon2D.new()
	var pts := PackedVector2Array()
	for i in 24:
		pts.append(Vector2(1080, 220) + Vector2.from_angle(TAU * i / 24.0) * 28.0)
	moon.polygon = pts
	moon.color = Color(1.0, 0.95, 0.7)
	moon.z_index = -1
	add_child(moon)
	var mid := WINDOW_GLASS.get_center()
	for seg in [[Vector2(mid.x, WINDOW_GLASS.position.y), Vector2(mid.x, WINDOW_GLASS.end.y)],
			[Vector2(WINDOW_GLASS.position.x, mid.y), Vector2(WINDOW_GLASS.end.x, mid.y)]]:
		var bar := Line2D.new()
		bar.points = PackedVector2Array(seg)
		bar.width = 9.0
		bar.default_color = Color.WHITE
		bar.z_index = -1
		add_child(bar)
	var tint := CanvasModulate.new()
	tint.color = Color(0.85, 0.72, 0.6)
	add_child(tint)


func _play_evening() -> void:
	C.player.face_left()
	C.Hanka.face_left()
	await C.Babicka.say("Tady máte kakao, detektivky.")
	await C.Alica.say("Budeme hlídat celou noc!")
	C.Hanka.pose("sleepy")
	await C.Hanka.say("Já vůbec nejsem ospalá…")
	await C.Hanka.say("Chrrr…")
	C.Alica.pose("whisper")
	await C.Alica.say("Pst! Něco se venku hýbe!")
	C.Alica.pose()
	C.Hanka.pose()
	Globals.phase = "night"
	R.goto_room("Zahrada")


#endregion
