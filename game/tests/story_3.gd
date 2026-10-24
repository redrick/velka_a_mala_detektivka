extends "res://tests/story_test.gd"
## Story 3 "Mapa ke starému rybníku" from the map on the kitchen table to the end card.


func run() -> void:
	await start("Kuchyne3", 3)
	check(C.player == C.Alica and has_item("Mapa"), "Alica plays, the whole map")
	check(Globals.r_intro, "the map scene in the kitchen")
	await go("Dvere", "Rybnik")
	await talk("Deda")
	check(Globals.r_stump, "děda knows the stump of the big willow")
	# děda's big steps land in the pond, then the 20 children's steps (minigame), the star stone, Joey digs
	await click("Parez")
	check(Globals.r_steps and Globals.r_hole, "star stone found, the hole is empty")
	if C.player != C.Alica:
		await talk("Alica")
	await click("Stopy")
	check(Globals.r_boots, "Alica: big boot prints")
	await talk("Tonda")
	check(Globals.r_tonda_ran, "Tonda ran off with his spade")
	await click("Nora")
	check(Globals.r_burrow, "the badger's burrow")
	await talk("Rybar")
	check(Globals.r_rybar, "the fisherman: someone shines a light in the morning")
	await talk("Hanka")
	await click("Stopy")
	check(Globals.r_dots, "Hanka: small round dots")
	# all the clues: the evening quarrel in the kitchen, then dawn at the pond
	await until(func(): return Globals.r_evening, "evening at home: the sisters make up")
	await in_room("Rybnik")
	check(R.current.is_dark() and R.current.has_character("Tonda"), "dawn: someone digs by the willow")
	if C.player != C.Hanka:
		await talk("Hanka")
	await talk("Tonda")
	check(Globals.r_tonda_ok and not R.current.is_dark(), "Hanka's torch: Tonda's secret, he joins")
	await save_and_continue(3, "Rybnik")
	check(Globals.r_tonda_ok and Globals.r_evening, "state survives save + continue")
	await click("Stopy")
	check(Globals.r_prints and Globals.r_trail, "whose print is it? Joey's nose leads to the mill")
	# the bench, "Kdo to byl?" (minigame), Věrka, the tin and the end card all play on entering
	await go("KMlynu", "Mlyn")
	await in_room("Menu")
	check(Globals.r_verka and Globals.r_end, "Věrka found, the club opened the tin")
	check(Globals.is_finished(3), "story 3 finished")


## Waits for a flag set by a cutscene in another room (idle() returns in its quiet moments).
func until(cond: Callable, what: String, limit := 120.0) -> void:
	var t := 0.0
	while not cond.call() and t < limit:
		await get_tree().process_frame
		t += get_process_delta_time()
	check(cond.call(), what)


## steps.gd, prints.gd and culprit.gd have no solve_for_test yet: end their levels the way a
## solved level ends.
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
