@tool
extends "res://game/shared/story_room.gd"
## Story 5, Franta's hallway: crates of parsnips, small star-soled boots drying by the stove, and the
## curtain to the stairs moves. Franta only smiles: "Sněhuláci? Ti chodí sami."

const Data := preload('room_franta5_state.gd')

var state: Data = load("res://game/rooms/franta5/room_franta5.tres")


func _on_room_entered() -> void:
	C.player.position = get_marker_position("Start")
	Globals.bring_sister(self, Vector2(170, 10))
	remove("Joey")
	place("Rybar", get_marker_position("Franta")).pose("home")
	Globals.exit_arrow(self, "Ven", true)


func _on_room_transition_finished() -> void:
	if not Globals.s_parsnip and not Globals.s_boots:
		await C.Rybar.say("Holky! Pojďte dál, venku mrzne.")


func joey_goal() -> Vector2:
	return Vector2.ZERO


func on_click(node: Node) -> void:
	match node.script_name:
		"Pastinak":
			await C.player.walk_to_clicked()
			if C.player == C.Alica:
				C.Alica.pose("lens")
			await C.player.say("Bedýnky s pastinákem! Bílý jako nos sněhuláků.")
			C.player.pose()
			Globals.s_parsnip = true
			await _done()
		"Boticky":
			await C.player.walk_to_clicked(Vector2(-200, 20))
			await hand_over(C.Hanka, "Malé botičky u kamen. Hani, podívej se na podrážky. Ty vidíš malé věci.")
			C.Hanka.pose("point")
			await C.Hanka.say("Malé botičky! A na podrážce mají hvězdičky!")
			C.Hanka.pose()
			Globals.s_boots = true
			await _done()
		"Kamna":
			await C.player.walk_to_clicked()
			await C.player.say("Kamna hřejí. Suší se tu botičky.")
		"Zaves":
			await C.player.walk_to_clicked()
			sfx("ŠUST!", Vector2(1680, 300), 70)
			await C.player.say("Závěs se pohnul! Je tam někdo?")
			await C.Rybar.say("To je jenom průvan.")
			Globals.s_curtain = true
			await _done()
		"Ven":
			await C.player.walk_to_clicked()
			R.goto_room("Ves5")
		_: await super(node)


func on_character(chr: PopochiuCharacter, action: String, _item: PopochiuInventoryItem = null) -> bool:
	if chr.script_name != "Rybar" or action == "look":
		return false
	await C.player.walk(chr.position + Vector2(-260, 30))
	await C.player.face_clicked()
	await C.Alica.say("Pane Franto, nevíte, kdo nám staví sněhuláky?")
	await C.Rybar.say("Sněhuláci? Ti chodí sami, holky.")
	await C.Hanka.say("Usmívá se. On něco ví!")
	return true


func _done() -> void:
	if Globals.s_parsnip and Globals.s_boots and Globals.s_curtain:
		await C.Alica.say("Pastinák, botičky s hvězdičkami, někdo za závěsem… Pojďme domů. Musím to promyslet.")
