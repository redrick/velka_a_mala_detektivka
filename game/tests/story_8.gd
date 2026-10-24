extends "res://tests/story_test.gd"
## Story 8 "Stopy ve sněhu" from the evening before to the end card.


func run() -> void:
	await start("Kuchyne8", 8)
	await in_room("Zahrada8")
	check(Globals.n_day == 1, "morning 1")
	await click("Snehulaci")
	await click("Stopy")
	if C.player != C.Hanka:
		await talk("Hanka")
	await click("Pahyl")
	check(Globals.n_high and Globals.n_trampled and Globals.n_stub and Globals.n_hajny, "noses, prints, stub, hajný")
	await go("NaLouku", "Louka8")
	await click("ZajiciStopy")
	await click("LisciStopy")
	await click("Dub")
	check(Globals.n_hare and Globals.n_fox and Globals.n_boar, "hare, fox, boar")
	await save_and_continue(8, "Louka8")
	check(Globals.n_boar, "state survives continue")
	await go("DoLesa", "Les8")
	check(Globals.n_guide, "track guide")
	await click("Zpet")
	await in_room("Zahrada8")
	check(Globals.n_day == 2, "the clean-page night, morning 2")
	await click("CisteStopy")
	await in_room("Les8")
	check(Globals.n_clean and Globals.n_who and Globals.n_trail, "clean prints, who, trail")
	if C.player != C.Hanka:
		await talk("Hanka")
	await click("Smrcek")
	check(Globals.n_bed and Globals.n_scale, "the deer's bed, hay in both racks")
	await in_room("Menu")
	check(Globals.is_finished(8), "story 8 finished")
