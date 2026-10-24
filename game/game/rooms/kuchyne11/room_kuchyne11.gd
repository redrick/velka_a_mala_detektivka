@tool
extends "res://game/shared/story_room.gd"
## Story 11, babička's kitchen: Bílá sobota, dyeing the eggs (onion skins, wax, markers), laying them out in
## repeating rows ("Kraslice podle vzoru"), then the evening when Kropenatka doesn't come to roost.

const Data := preload('room_kuchyne11_state.gd')
const PatternGame := preload("res://game/minigames/pattern.gd")

var state: Data = load("res://game/rooms/kuchyne11/room_kuchyne11.tres")


func _on_room_entered() -> void:
	C.player.position = get_marker_position("ZeDvora") if C.player.last_room == "Dvur11" else get_marker_position("Start")
	Globals.bring_sister(self, Vector2(-170, 10))
	place("Babicka", Vector2(420, 900))
	place("Mama", Vector2(1100, 920))
	place("Tata", Vector2(1350, 930))
	place("Joey", Vector2(1550, 1000))
	get_prop("Kraslice").visible = Globals.v_missing
	Globals.exit_arrow(self, "Dvere", false)


func _on_room_transition_finished() -> void:
	if _friday_done() and not Globals.v_missing:
		await _saturday()


func _friday_done() -> bool:
	return Globals.v_count and Globals.v_fox and Globals.v_shells and Globals.v_magpie and Globals.v_tonda and Globals.v_straw


func joey_goal() -> Vector2:
	return get_hotspot("Dvere").walk_to_point


func _saturday() -> void:
	_card(["Bílá sobota. Barví se!"], 1.8)
	await get_tree().create_timer(2.2).timeout
	await C.Babicka.say("Já barvím v cibulových slupkách.")
	await C.Mama.say("Já kreslím voskem.")
	await C.Hanka.say("A my fixama! Na mojí je opička!")
	await C.Tata.say("Tohle měl být zajíc…")
	await pop("Kraslice")
	await C.Alica.say("A na mojí hvězdička. Jako Klub Hvězdička!")
	await C.Babicka.say("Teď je rozložíme do řad. Každá řada má svůj vzorek, který se opakuje.")
	var mg: CanvasLayer = PatternGame.new()
	add_child(mg)
	await mg.finished
	Globals.v_pattern = true
	await fade(func(): pass, "Sobota večer…")
	Globals.v_missing = true
	Globals.phase = "v_evening"
	R.goto_room("Dvur11")


func on_click(node: Node) -> void:
	match node.script_name:
		"Dvere":
			await C.player.walk_to_clicked()
			R.goto_room("Dvur11")
		"Kraslice":
			await C.player.walk_to_clicked()
			await C.player.say("Kraslice! Cibulové, voskové a malované fixami.")
		_: await super(node)


func on_character(chr: PopochiuCharacter, action: String, _item: PopochiuInventoryItem = null) -> bool:
	if action == "look" or chr == C.Alica or chr == C.Hanka or chr == C.Joey:
		return false
	await C.player.walk(chr.position + Vector2(-240, 20))
	match chr.script_name:
		"Babicka": await C.Babicka.say("Vajíčka na barvení sbírám celý týden.")
		"Mama": await C.Mama.say("Hlavně ať najdete, kam se ta vajíčka ztrácejí.")
		"Tata": await C.Tata.say("Nesl jsem slepičkám hobliny z dílny. Na podestýlku.")
		_: return false
	return true
