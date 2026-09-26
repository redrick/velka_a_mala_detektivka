extends Node

var case_started := false
var footprints_found := false
var joey_cleared := false
var trap_planned := false
var got_flour := false
var trap_set := false
var night_done := false
var thread_found := false
var bush_found := false
var stream_crossed := false
var hanka_behind_fence := false
var shed_done := false
var nails_done := 0
var game_finished := false
# "", "evening", "night", "ending": which cutscene the next room entry should play
var phase := ""


func sister() -> PopochiuCharacter:
	return C.get_character("Hanka" if C.player.script_name == "Alica" else "Alica")


func bring_sister(room: PopochiuRoom, offset := Vector2(-170, 10)) -> void:
	var other := sister()
	if not room.has_character(other.script_name):
		room.add_character(other)
	other.position = C.player.position + offset


func switch_to(chr: PopochiuCharacter) -> void:
	var old := C.player
	chr.stop_following_character()
	C.player = chr
	old.start_following_character(chr)


func start_episode(start_room: String) -> void:
	_reset_progress()
	G.show_interface()
	R.goto_room(start_room)


func go_to_menu() -> void:
	sister().stop_following_character()
	I.deselect_active()
	I.clean_inventory(true)
	R.goto_room("Menu")


func _reset_progress() -> void:
	var fresh: Node = get_script().new()
	for prop in get_script().get_script_property_list():
		if prop.usage & PROPERTY_USAGE_SCRIPT_VARIABLE:
			set(prop.name, fresh.get(prop.name))
	fresh.free()
	I.clean_inventory(true)
	InGameMenu.history.clear()
	for item_name in PopochiuConfig.get_inventory_items_on_start():
		I.get_item_instance(item_name).add(false)
	for room_path in PopochiuResources.get_section("rooms"):
		var room_state: PopochiuRoomData = load(room_path)
		if R.current and R.current.state == room_state:
			continue
		for children in PopochiuResources.ROOM_CHILDREN:
			(room_state.get(children) as Dictionary).clear()
		room_state.characters.clear()
		room_state.visited = false
		room_state.visited_times = 0
		room_state.visited_first_time = false
	R.store_states()
	for chr in C._characters.values():
		if is_instance_valid(chr) and not chr.is_inside_tree():
			chr.queue_free()
	C._characters.clear()
	C.player = C.get_character("Alica")
