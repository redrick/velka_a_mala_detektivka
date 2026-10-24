extends Node
## Base for the story tests: helpers to click things, talk to people, use items, wait until a
## cutscene is over, and a watcher that solves any minigame that opens.

var runner: Node
var _shots := ""
var _shot_n := 0


func run() -> void:
	pass


func _enter_tree() -> void:
	for a in OS.get_cmdline_user_args():
		if a.begins_with("--shots="):
			_shots = a.substr(8)
			DirAccess.make_dir_recursive_absolute(_shots)


## With --shots=<dir> (and a window): a plain screenshot and one with the debug overlay.
func shot(tag: String) -> void:
	if _shots == "" or not is_instance_valid(R.current):
		return
	_shot_n += 1
	var base := "%s/%03d_%s_%s" % [_shots, _shot_n, R.current.script_name, tag.validate_filename()]
	await RenderingServer.frame_post_draw
	get_viewport().get_texture().get_image().save_png(base + ".png")
	var o: Node2D = load("res://tests/tour_overlay.gd").new()
	o.z_index = 4000
	R.current.add_child(o)
	await RenderingServer.frame_post_draw
	await RenderingServer.frame_post_draw
	get_viewport().get_texture().get_image().save_png(base + "_dbg.png")
	o.queue_free()


func _process(_delta: float) -> void:
	for mg in get_tree().get_nodes_in_group("minigame"):
		if not mg.busy and not mg.has_meta("solving"):
			mg.set_meta("solving", true)
			_solve.call_deferred(mg)


## Plays one level of the open minigame; the game moves on to the next level by itself.
func _solve(mg: Node) -> void:
	await get_tree().create_timer(0.3).timeout
	if not is_instance_valid(mg):
		return
	if mg.has_method("solve_for_test"):
		await mg.solve_for_test()
	else:
		push_error("no solve_for_test in " + str(mg.get_script().resource_path))
	await get_tree().create_timer(0.2).timeout
	if is_instance_valid(mg):
		mg.remove_meta("solving")


func check(ok: bool, what: String) -> void:
	runner.checks += 1
	if not ok:
		runner.fails += 1
		print("  FAIL: ", what)
	else:
		print("  ok: ", what)


## Waits until nobody talks or walks, no picture/radio card or minigame is open, for `quiet` seconds.
func idle(quiet := 1.6, limit := 300.0) -> void:
	var calm := 0.0
	var t := 0.0
	var next_note := 10.0
	while calm < quiet and t < limit:
		await get_tree().process_frame
		var dt := get_process_delta_time()
		t += dt
		calm = 0.0 if _busy() else calm + dt
		if t > next_note:
			next_note += 10.0
			print("  … still busy: ", _why())
	if t >= limit:
		check(false, "idle timeout: " + _why())


func _why() -> String:
	if not E.in_room or not is_instance_valid(R.current):
		return "no room"
	var out := []
	if not get_tree().get_nodes_in_group("minigame").is_empty():
		out.append("minigame")
	for c in R.current.get_characters():
		if c.is_talking: out.append(c.script_name + " talks")
		if c.is_moving: out.append(c.script_name + " walks")
	for n in R.current.get_children():
		if n is CanvasLayer and n.layer >= 40: out.append("layer " + n.name)
	return ", ".join(out)


func _busy() -> bool:
	if not E.in_room or not is_instance_valid(R.current):
		return true
	if not get_tree().get_nodes_in_group("minigame").is_empty():
		return true
	for c in R.current.get_characters():
		if c.is_talking or c.is_moving:
			return true
	for n in R.current.get_children():
		if n is CanvasLayer and n.layer >= 40:
			return true
	return false


func start(room: String, number: int) -> void:
	Globals.start_episode(room, number)
	await in_room(room)


func in_room(room: String) -> void:
	var t := 0.0
	while not (E.in_room and is_instance_valid(R.current) and R.current.script_name == room) and t < 30.0:
		await get_tree().process_frame
		t += get_process_delta_time()
	check(is_instance_valid(R.current) and R.current.script_name == room, "in room " + room)
	await idle()
	await shot("enter")


func _node(name: String) -> Node:
	if R.current.has_node("Props/" + name):
		return R.current.get_prop(name)
	if R.current.has_node("Hotspots/" + name):
		return R.current.get_hotspot(name)
	return null


func click(name: String) -> void:
	var n := _node(name)
	if n == null:
		check(false, "no prop/hotspot " + name + " in " + R.current.script_name)
		return
	E.clicked = n
	await R.current.on_click(n)
	await idle()
	await shot(name)


## Clicks an exit and waits for the next room.
func go(exit_name: String, room: String) -> void:
	await click(exit_name)
	await in_room(room)


func talk(chr_name: String) -> void:
	var chr := C.get_character(chr_name)
	if chr == C.player:
		check(false, "clicked " + chr_name + ", but she is the player (not clickable in the game)")
		return
	E.clicked = chr
	await chr._on_click()
	await idle()
	await shot(chr_name)


func use(item_name: String, target: String) -> void:
	var item: PopochiuInventoryItem = I.get_item_instance(item_name)
	I.active = item
	var chr := C.get_character(target) if R.current.has_character(target) else null
	if chr:
		E.clicked = chr
		await chr._on_item_used(item)
	else:
		var n := _node(target)
		E.clicked = n
		await R.current.on_item(n, item)
	I.active = null
	await idle()


func has_item(item_name: String) -> bool:
	return I.get_item_instance(item_name).in_inventory


## Saves, goes to the menu and continues the story: the state must survive.
func save_and_continue(number: int, room: String) -> void:
	Globals.go_to_menu()
	await in_room("Menu")
	Globals.continue_episode(number)
	await in_room(room)
