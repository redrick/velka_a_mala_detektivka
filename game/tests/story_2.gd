extends "res://tests/story_test.gd"
## Story 2 "Tajemství starého klíče" from the night noises to the end card.


func run() -> void:
	await start("Loznice", 2)
	check(C.player == C.Alica and has_item("Klic") and has_item("Zapisnik"), "Alica plays, key and notebook")
	await click("Strop")
	await click("Strop")
	check(Globals.k_noises == 2, "two noises from the attic")
	await click("Strop")
	await in_room("Snidane")
	check(Globals.k_noises == 3 and Globals.k_breakfast, "three noises, breakfast: děda won't go to the attic")
	await go("Dvere", "Stit")
	if C.player != C.Hanka:
		await talk("Hanka")
	await click("Pirko")
	check(Globals.k_feather, "Hanka found the white feather")
	if C.player != C.Alica:
		await talk("Alica")
	await click("Vyvrzky")
	check(Globals.k_pellets, "Alica's magnifier: owl pellets")
	await click("Okynko")
	check(Globals.k_window, "the star on the attic window = the star on the key")
	await talk("Deda")
	check(Globals.k_ladder, "děda saw the key and put up the ladder")
	await save_and_continue(2, "Stit")
	check(Globals.k_ladder and has_item("Klic"), "state survives save + continue")
	await go("Zebrik", "Puda")
	if C.player != C.Hanka:
		await talk("Hanka")
	await click("Truhla")
	check(Globals.k_chest and has_item("Pulmapa") and not has_item("Klic"), "chest opened: half a map, the riddle")
	# the owls, the next morning, then the mirrors (minigame)
	await click("Tram")
	check(Globals.k_owls and Globals.k_sunbeam, "owls on the beam, the star of light on the floor")
	for i in range(1, 7):
		await click("Prkno%d" % i)
	check(Globals.k_planks == 6, "six planks counted")
	await click("Prkno7")
	await in_room("Stit")
	check(Globals.k_map and has_item("Mapa"), "the singing plank: the whole map")
	check(Globals.phase == "k_nails", "ending: the owl box, three nails")
	await click("Hrebik1")
	await click("Hrebik2")
	await click("Hrebik3")
	await in_room("Menu")
	check(Globals.k_nails == 3 and Globals.game_finished, "owl box nailed up, the end card")
	check(Globals.is_finished(2), "story 2 finished")


## sunbeam.gd has no solve_for_test yet: end its levels the way a solved level ends.
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
