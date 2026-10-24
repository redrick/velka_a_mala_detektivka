extends "res://tests/story_test.gd"
## Story 7 "Joeyho velký den" from Joey's morning to the end card.


func run() -> void:
	await start("Zahrada7", 7)
	check(Globals.j_morning, "Joey told the morning")
	await go("Dum", "Kuchyne7")
	check(Globals.j_case and Globals.j_order, "the ring is gone, the day put in order")
	await go("Dvere", "Zahrada7")
	await click("Krmitko")
	check(Globals.j_feeder and Globals.j_glove, "feeder searched, glove gone")
	await click("Kulna")
	check(Globals.j_stash and Globals.j_tonda, "stash dug up, Tonda's magpie")
	await save_and_continue(7, "Zahrada7")
	check(Globals.j_tonda, "state survives continue")
	await go("KLesu", "Les7")
	await talk("Hajny")
	check(Globals.j_straka, "hajný: only foil")
	await go("Zpet", "Zahrada7")
	await click("Pevnost")
	check(Globals.j_where and Globals.j_ring, "where, then Joey sniffs the ring")
	await in_room("Menu")
	check(Globals.is_finished(7), "story 7 finished")
