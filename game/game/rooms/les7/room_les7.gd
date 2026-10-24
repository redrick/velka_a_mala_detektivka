@tool
extends "res://game/shared/story_room.gd"
## Story 7, the forester's lodge in the forest. The magpie has a shiny thing: foil from a gingerbread
## wrapper. The hajný: magpies are actually wary of shiny things, the "thieving magpie" is a fairy tale.

const Data := preload('room_les7_state.gd')

var state: Data = load("res://game/rooms/les7/room_les7.tres")


func _on_room_entered() -> void:
	C.player.position = get_marker_position("Start")
	Globals.bring_sister(self, Vector2(170, 10))
	place("Joey", joey_spot())
	place("Hajny", get_marker_position("Hajny"))
	Globals.exit_arrow(self, "Zpet", true)


func _on_room_transition_finished() -> void:
	if not Globals.j_straka:
		_card(["Druhý den ráno…"], 1.6)
		await get_tree().create_timer(2.0).timeout
		await C.Hanka.say("Tamhle sedí straka! A má něco lesklého!")


func joey_goal() -> Vector2:
	return C.Hajny.position + Vector2(-240, 50) if not Globals.j_straka else Vector2(160, 960)


func on_click(node: Node) -> void:
	match node.script_name:
		"Straka":
			await C.player.walk(Vector2(1400, 900))
			await C.player.say("Straka s něčím lesklým v zobáku.")
		"Hajovna":
			await C.player.walk_to_clicked()
			await C.player.say("Hájovna. Tady bydlí pan hajný.")
		"Krmelec":
			await C.player.walk_to_clicked()
			await C.player.say("Krmelec. Seno pro srnky.")
		"Zpet":
			await C.player.walk_to_clicked()
			R.goto_room("Zahrada7")
		_: await super(node)


func on_character(chr: PopochiuCharacter, action: String, _item: PopochiuInventoryItem = null) -> bool:
	if chr.script_name != "Hajny" or action == "look":
		return false
	await C.player.walk(chr.position + Vector2(-260, 20))
	if Globals.j_straka:
		await C.Hajny.say("Tak hodně štěstí, detektivky. A pozdravujte Joeyho!")
		return true
	await C.Alica.say("Dobrý den, pane hajný. Straka babičce ukradla prstýnek!")
	await C.Hajny.say("Straka? Počkejte…")
	sfx("ČAK ČAK!", Vector2(1560, 360), 70)
	C.Hajny.pose("foil")
	await C.Hajny.say("Pustila to. Tohle je alobal z perníčku. Žádný prstýnek.")
	await C.Hajny.say("A víte co? Že straky kradou lesklé věci, je jen pohádka. Lesklých věcí se spíš bojí.")
	C.Hajny.pose()
	await C.Alica.say("Takže straka to taky nebyla… Kde ten prstýnek může být?")
	await C.Hanka.say("Joey pořád táhne domů. K pevnosti!")
	Globals.j_straka = true
	get_prop("Straka").hide()
	return true
