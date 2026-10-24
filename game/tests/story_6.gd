extends "res://tests/story_test.gd"
## Story 6 "Kam mizí perníčky?" from the baking to the end card.


func run() -> void:
	await start("Kuchyne6", 6)
	check(Globals.p_intro and Globals.p_day == 1, "baking, morning 1")
	await click("Okno")
	await click("Plechovka")
	await click("Tlapky")
	await in_room("Kuchyne6")
	check(Globals.p_sill and Globals.p_tin1 and Globals.p_joey and Globals.p_birds, "day 1 clues, dawn watch")
	await go("Dvere", "Zahrada6")
	await click("Misto")
	await in_room("Kuchyne6")
	check(Globals.p_feeder and Globals.p_food and Globals.p_day == 2, "feeder built, birds fed, morning 2")
	await save_and_continue(6, "Kuchyne6")
	check(Globals.p_day == 2 and Globals.p_feeder, "state survives continue")
	await click("Plechovka")
	await click("Past")
	await talk("Tonda")
	if C.player != C.Alica:
		await talk("Alica")
	await talk("Hanka")
	check(Globals.p_tin2 and Globals.p_trap and Globals.p_tonda and Globals.p_hanka, "day 2: tin, trap, Tonda, Hanka")
	if C.player != C.Hanka:
		await talk("Hanka")
	await click("Boty")
	await in_room("Mlyn6")
	check(Globals.p_boots and Globals.p_who and Globals.p_spruce, "boots, who, caught at the spruce")
	await click("Smrk")
	check(Globals.p_stars, "stars hung")
	await in_room("Menu")
	check(Globals.is_finished(6), "story 6 finished")
