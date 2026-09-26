# @popochiu-docs-ignore-class
@tool
extends PopochiuRoom

const Data := preload('room_zahumenek_state.gd')
const GAP_FRONT := Vector2(634, 780)
const GAP_MIDDLE := Vector2(634, 700)
const STONE_WORDS := ["Velký!", "Malý!", "Velký!"]

var state: Data = load("res://game/rooms/zahumenek/room_zahumenek.tres")
var _stones_done := 0


#region Virtual ####################################################################################
func _on_room_entered() -> void:
	C.player.position = get_marker_position("PrechodP" if Globals.stream_crossed else "ZeZahrady")
	Globals.bring_sister(self)
	if Globals.stream_crossed:
		C.Joey.position = get_marker_position("PrechodP") + Vector2(150, 90)
	_stones_done = 0


func _on_room_transition_finished() -> void:
	if state.visited_first_time:
		await C.Alica.say("Stopy vedou k plotu. Tam je nějaká díra!")


func _on_room_exited() -> void:
	pass


#endregion

#region Public #####################################################################################
func squeeze_through_gap() -> void:
	var hanka: PopochiuCharacter = C.Hanka
	if not Globals.hanka_behind_fence:
		C.Alica.stop_following_character()
		await _walk_free(hanka, [GAP_FRONT, GAP_MIDDLE, get_marker_position("ZaPlotem")])
		hanka.can_move = false
		Globals.hanka_behind_fence = true
		await hanka.say("Jsem za plotem!")
	else:
		await _walk_free(hanka, [GAP_MIDDLE, GAP_FRONT])
		hanka.can_move = true
		Globals.hanka_behind_fence = false
		C.Alica.start_following_character(hanka)
		await hanka.say("Zase venku!")


func stone_clicked(n: int) -> void:
	if Globals.stream_crossed:
		await _cross(false)
		return
	if Globals.hanka_behind_fence:
		await C.Hanka.say("Nejdřív se musím vrátit zpátky dírou.")
		return
	if not Globals.bush_found:
		await C.player.say("Kameny v potoce. Ale kudy šel zloděj?")
		return
	await C.player.walk(get_marker_position("PrechodL"))
	if n != _stones_done + 1:
		_reset_stones()
		await _joey_splash()
		await C.Alica.say("Ne, ne! Velký, malý, velký. Znovu od začátku!")
		return
	_stones_done += 1
	_bounce(get_prop("Kamen%d" % n))
	await C.player.say(STONE_WORDS[n - 1])
	if _stones_done == 3:
		await _cross(true)


#endregion

#region Private ####################################################################################
func _walk_free(chr: PopochiuCharacter, points: Array) -> void:
	chr.ignore_walkable_areas = true
	for p: Vector2 in points:
		await chr.walk(p)
	chr.ignore_walkable_areas = false


func _cross(forward: bool) -> void:
	var stones := [get_prop("Kamen1"), get_prop("Kamen2"), get_prop("Kamen3")]
	var path: Array = []
	for s in stones:
		path.append(s.global_position + Vector2(0, -6))
	var start := get_marker_position("PrechodL")
	var end := get_marker_position("PrechodP")
	if not forward:
		path.reverse()
		var t := start
		start = end
		end = t
	var other := Globals.sister()
	other.stop_following_character()
	if forward:
		await C.Alica.say("Podej mi ruku, Hanko!")
	await _walk_free(C.player, [start] + path + [end])
	await _walk_free(other, [start] + path + [end + Vector2(-170, 10)])
	other.start_following_character(C.player)
	Globals.stream_crossed = forward
	_reset_stones()
	if forward:
		var joey: PopochiuCharacter = C.Joey
		joey.ignore_walkable_areas = true
		await joey.walk(Vector2(1460, 960))
		await joey.say("Haf! Žbluňk!")
		await joey.walk(end + Vector2(150, 90))
		joey.ignore_walkable_areas = false
		await C.Hanka.say("Joey je celý mokrý!")
		await C.Alica.say("Stopy vedou ke kůlně!")


func _joey_splash() -> void:
	var joey: PopochiuCharacter = C.Joey
	var home := joey.position
	joey.ignore_walkable_areas = true
	await joey.walk(Vector2(1420, 990))
	await joey.say("Žbluňk!")
	await joey.walk(home)
	joey.ignore_walkable_areas = false
	await C.Hanka.say("Joey skočil do vody!")


func _reset_stones() -> void:
	_stones_done = 0
	for i in range(1, 4):
		get_prop("Kamen%d" % i).modulate = Color.WHITE


func _bounce(prop: Node2D) -> void:
	var tw := create_tween()
	tw.tween_property(prop, "scale", Vector2(1.15, 1.15), 0.12)
	tw.tween_property(prop, "scale", Vector2.ONE, 0.12)
	prop.modulate = Color(1.0, 1.0, 0.75)


#endregion
