extends "res://tests/story_test.gd"
## Story 11 "Kam mizí vajíčka?" from Maundy Thursday to the end card.


func run() -> void:
	await start("Dvur11", 11)
	check(Globals.v_intro, "eight hens, one egg short")
	await go("Kurnik", "Kurnik11")
	await click("Hnizda")
	check(Globals.v_count, "seven eggs")
	await go("Ven", "Dvur11")
	await click("PsiStopy")
	await click("Slepice")
	await click("Straka")
	await talk("Tonda")
	await click("Kropenatka")
	check(Globals.v_fox and Globals.v_shells and Globals.v_magpie and Globals.v_tonda and Globals.v_straw, "Thursday clues")
	await save_and_continue(11, "Dvur11")
	check(Globals.v_straw, "state survives continue")
	await click("Dum")
	await in_room("Dvur11")
	check(Globals.v_pattern and Globals.v_missing, "Saturday: kraslice in rows, Kropenatka missing")
	await click("Mezera")
	check(Globals.v_gap, "the gap, the feather")
	await go("Stodola", "Stodola11")
	if C.player != C.Hanka:
		await talk("Hanka")
	await click("Skvira")
	check(Globals.v_who and Globals.v_bales and Globals.v_swap, "who, the bales, the nest, Věrka's eggs")
	await in_room("Menu")
	check(Globals.is_finished(11), "story 11 finished")
