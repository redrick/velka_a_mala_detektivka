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
## Which story (episode number) is being played; also its save slot. 0 = in the menu.
var story := 0

# story 2 "Tajemství starého klíče" --------------------------------------------------------------
var k_noises := 0          # noises heard from the attic at night (3 = all)
var k_breakfast := false   # děda said "na půdu se nechodí"
var k_feather := false
var k_pellets := false
var k_window := false      # the star on the attic window = the star on the key
var k_ladder := false      # děda agreed and put up the ladder
var k_chest := false       # chest opened, flashback and riddle seen
var k_owls := false        # the owls found; next morning in the attic
var k_sunbeam := false     # mirrors minigame done, the star of light is on the floor
var k_planks := 0          # planks counted from the star
var k_map := false         # both halves of the map
var k_nails := 0           # nails in the owl box

# story 3 "Mapa ke starému rybníku" ----------------------------------------------------------------
var r_intro := false       # the map scene in the kitchen
var r_stump := false       # děda recognised the stump of the big willow
var r_steps := false       # the 20 children's steps done, star stone found
var r_hole := false        # Joey dug: someone was here first
var r_boots := false
var r_dots := false
var r_tonda_ran := false
var r_burrow := false
var r_rybar := false
var r_evening := false     # the quarrel at home and making up
var r_tonda_ok := false    # dawn: Tonda's secret, he joins
var r_prints := false      # whose print is it? minigame
var r_trail := false       # Joey's nose leads to the mill
var r_verka := false       # the lady at the bench gave Joey a biscuit
var r_end := false

## Per-story progress next to Popochiu's save files: saved?, finished?, and the last story played.
const PROGRESS := "user://progress.cfg"


func _ready() -> void:
	# E is the next autoload: connect once everything is in the tree
	(func(): E.game_loaded.connect(_on_game_loaded)).call_deferred()


## Autosave: whenever a story room has been entered (after its setup, before its cutscene).
func _process(_delta: float) -> void:
	if story <= 0 or not E.in_room or not is_instance_valid(R.current) or R.current.script_name == "Menu":
		return
	if get_meta("saved_room", 0) != R.current.get_instance_id():
		set_meta("saved_room", R.current.get_instance_id())
		save_now()


func _notification(what: int) -> void:
	if what == NOTIFICATION_WM_CLOSE_REQUEST:
		save_now()


func save_now() -> void:
	if story <= 0 or not is_instance_valid(R.current) or R.current.script_name == "Menu":
		return
	if not get_tree().get_nodes_in_group("minigame").is_empty():
		return
	E.save_game(story, "story %d" % story)
	var cfg := _progress()
	cfg.set_value("story_%d" % story, "saved", true)
	cfg.set_value("story_%d" % story, "finished", game_finished)
	cfg.set_value("general", "last_story", story)
	cfg.save(PROGRESS)


func has_save(n: int) -> bool:
	return FileAccess.file_exists("user://save_%d.json" % n) and _progress().get_value("story_%d" % n, "saved", false)


func is_finished(n: int) -> bool:
	return _progress().get_value("story_%d" % n, "finished", false)


## The story to offer under "Pokračovat" on the first menu screen, or 0.
func last_story() -> int:
	var n: int = _progress().get_value("general", "last_story", 0)
	return n if has_save(n) and not is_finished(n) else 0


## An exit at the edge of a room: a wider click area and a pulsing yellow arrow, so the way on is
## visible. `left` = the exit is at the left edge. Show or hide it later with show_exit().
func exit_arrow(room: Node, hotspot: String, left: bool, on := true) -> void:
	var h: PopochiuHotspot = room.get_hotspot(hotspot)
	var x0 := 0.0 if left else 1690.0
	h.interaction_polygon = PackedVector2Array([Vector2(x0, 600), Vector2(x0 + 230, 600), Vector2(x0 + 230, 1060), Vector2(x0, 1060)])
	var a := Sprite2D.new()
	a.name = "Arrow" + hotspot
	a.texture = load("res://assets/minigames/%s.png" % ("arrow_left" if left else "arrow"))
	a.position = Vector2(130.0 if left else 1790.0, 820.0)
	a.z_index = 50
	room.add_child(a)
	var tw := a.create_tween().set_loops()
	tw.tween_property(a, "position:x", a.position.x + (-20.0 if left else 20.0), 0.6)
	tw.tween_property(a, "position:x", a.position.x, 0.6)
	show_exit(room, hotspot, on)


func show_exit(room: Node, hotspot: String, on := true) -> void:
	var a := room.get_node_or_null("Arrow" + hotspot)
	if a:
		a.visible = on


func _progress() -> ConfigFile:
	var cfg := ConfigFile.new()
	cfg.load(PROGRESS)
	return cfg


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


func start_episode(start_room: String, number: int) -> void:
	_reset_progress()
	story = number
	# what the girls already carry when a story starts
	if number == 2:
		I.Zapisnik.add(false)
		I.Klic.add(false)
	elif number == 3:
		I.Zapisnik.add(false)
		I.Mapa.add(false)
	G.show_interface()
	R.goto_room(start_room)


func continue_episode(number: int) -> void:
	_reset_progress()
	G.show_interface()
	E.load_game(number)


func go_to_menu() -> void:
	if not G.is_blocked or game_finished:
		save_now()
	story = 0
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


## After loading, put the sister next to the player (the room placed her by the entry door).
func _on_game_loaded(_data: Dictionary) -> void:
	nails_done = int(nails_done)
	story = int(story)
	var other := sister()
	if is_instance_valid(R.current) and R.current.has_character(other.script_name) and other.follow_character != "":
		other.position = C.player.position + Vector2(-170, 10)
