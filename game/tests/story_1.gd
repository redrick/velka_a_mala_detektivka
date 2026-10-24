extends "res://tests/story_test.gd"
## Story 1 "Záhada zmizelých ponožek" from the washing line to the end card.
## Story 1's rooms are plain PopochiuRooms (no on_click): props and hotspots have their own
## _on_click(), so they are pressed directly with press().


func run() -> void:
	await start("Zahrada", 1)
	check(C.player == C.Alica, "Alica plays")
	await talk("Babicka")
	check(Globals.case_started and has_item("Zapisnik"), "case started, notebook")
	await press("Trava")
	check(Globals.footprints_found, "tiny footprints under the line")
	await press("Pelisek")
	check(Globals.joey_cleared and has_item("StaraPonozka"), "Joey cleared: his old chewed sock")
	await talk("Tonda")
	check(Globals.trap_planned, "Tonda saw a bushy tail: trap planned")
	await press("Dvere")
	await in_room("Kuchyne")
	await talk("Babicka")
	check(Globals.got_flour and has_item("Mouka") and has_item("NovaPonozka"), "flour and a new sock")
	await press("Dvere")
	await in_room("Zahrada")
	# the trap (minigame), then the evening in the kitchen and the night in the garden play by themselves
	await press("Snura")
	check(Globals.trap_set, "trap set")
	await until(func(): return Globals.night_done, "the night: the bait is gone")
	await in_room("Zahrada")
	check(Globals.night_done and Globals.phase == "", "morning: floury prints")
	await save_and_continue(1, "Zahrada")
	check(Globals.night_done and Globals.trap_set, "state survives save + continue")
	await press("Nitka")
	check(Globals.thread_found and has_item("Nitka"), "the red thread")
	await press("Cesta")
	await in_room("Zahumenek")
	if C.player != C.Hanka:
		await talk("Hanka")
	check(C.player == C.Hanka, "Hanka plays (she fits through the gap)")
	await press("Diera")
	check(Globals.hanka_behind_fence, "Hanka behind the fence")
	await press("Ker")
	check(Globals.bush_found and not Globals.hanka_behind_fence, "thread and fur on the bush, Hanka back")
	await press("Kamen1")
	await press("Kamen2")
	await press("Kamen3")
	check(Globals.stream_crossed, "big, small, big: across the stream")
	await press("Kulna")
	await in_room("Kulna")
	if C.player != C.Hanka:
		await talk("Hanka")
	await press("Bota")
	check(Globals.shed_done and has_item("Klic"), "dormice in the boot, the old key")
	await in_room("Zahrada")
	check(Globals.phase == "nails", "ending: the dormouse house, three nails")
	await press("Hrebik1")
	await press("Hrebik2")
	await press("Hrebik3")
	await in_room("Menu")
	check(Globals.game_finished, "three nails, the end card")
	check(Globals.is_finished(1), "story 1 finished")


## Story 1's props and hotspots handle their own clicks.
func press(name: String) -> void:
	var n := _node(name)
	if n == null:
		check(false, "no prop/hotspot " + name + " in " + R.current.script_name)
		return
	E.clicked = n
	await n._on_click()
	await idle()
	await shot(name)


## Waits for a flag set by a cutscene in another room (idle() returns in its quiet moments).
func until(cond: Callable, what: String, limit := 120.0) -> void:
	var t := 0.0
	while not cond.call() and t < limit:
		await get_tree().process_frame
		t += get_process_delta_time()
	check(cond.call(), what)


## trap.gd has no solve_for_test yet: end its levels the way a solved level ends.
func _solve(mg: Node) -> void:
	if mg.has_method("solve_for_test"):
		await super(mg)
		return
	await get_tree().create_timer(0.3).timeout
	if not is_instance_valid(mg):
		return
	print("  note: no solve_for_test in ", mg.get_script().resource_path, ", level skipped")
	await mg.level_done()
	await get_tree().create_timer(0.2).timeout
	if is_instance_valid(mg):
		mg.remove_meta("solving")
