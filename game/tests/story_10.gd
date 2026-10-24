extends "res://tests/story_test.gd"
## Story 10 "Záhada ve škole" from Monday morning to the end card.


func run() -> void:
	await start("Skola10", 10)
	check(Globals.q_intro and C.player == C.Alica, "the hutch is empty")
	await click("Kotec")
	await click("Stopy")
	await click("Seno")
	await talk("MalyKarel")
	await click("Srub")

	check(Globals.q_hutch and Globals.q_prints and Globals.q_nest and Globals.q_karel and Globals.q_box, "Monday clues, táta's box")
	await in_room("Skola10")
	check(Globals.q_who and Globals.q_day == 2, "evening: who, field day")
	await save_and_continue(10, "Skola10")
	check(Globals.q_day == 2, "state survives continue")
	if C.player != C.Hanka:
		await talk("Hanka")
	await click("Srub")
	await in_room("Kumbal10")
	check(Globals.q_wheek and Globals.q_found, "wheek, found in the hat")
	await go("Ven", "Skola10")
	await click("Kotec")
	check(Globals.q_new and Globals.q_pens, "new hutch, pens on the meadow")
	await in_room("Menu")
	check(Globals.is_finished(10), "story 10 finished")
