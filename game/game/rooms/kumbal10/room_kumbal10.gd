@tool
extends "res://game/shared/story_room.gd"
## Story 10, pan Karel's kumbál: Míša and Šiša asleep in his woolly hat on straw. He explains: the latch was
## broken and it was −5 °C, so on Sunday evening he carried them here and pinned a note to the hutch.

const Data := preload('room_kumbal10_state.gd')

var state: Data = load("res://game/rooms/kumbal10/room_kumbal10.tres")


func _on_room_entered() -> void:
	C.player.position = get_marker_position("Start")
	Globals.bring_sister(self, Vector2(170, 10))
	place("Skolnik", get_marker_position("Karel"))
	remove("Joey")
	Globals.exit_arrow(self, "Ven", true)


func _on_room_transition_finished() -> void:
	if get_meta("told", false) or Globals.q_new:
		return
	set_meta("told", true)
	C.Hanka.pose("point")
	await C.Hanka.say("Míša a Šiša! Spinkají v čepici!")
	C.Hanka.pose()
	await C.Skolnik.say("V neděli večer jsem šel zkontrolovat kotec. Západka byla rozbitá.")
	await C.Skolnik.say("A v noci mělo mrznout. Minus pět stupňů! Tak jsem je odnesl sem, do tepla.")
	await C.Skolnik.say("Udělal jsem jim pelíšek ve své čepici. A na kotec jsem připíchl lístek.")
	await C.Alica.say("Ten lístek odfoukl vítr. A ježek si ho odnesl do pelíšku!")
	await C.Skolnik.say("Tak proto jste mě hledali… Promiňte. V lese nemám signál.")
	await C.Alica.say("Velké holínky, hobliny z ponku, prázdný háček a K. Všechno sedí!")
	await C.Skolnik.say("Pojďte ven. Postavíme jim nový kotec. Takový, co vydrží mráz.")


func on_click(node: Node) -> void:
	match node.script_name:
		"Cepice":
			await C.player.walk_to_clicked(Vector2(-300, 40))
			await C.player.say("Míša a Šiša v teplé čepici. Spinkají.")
		"Ven":
			await C.player.walk_to_clicked()
			R.goto_room("Skola10")
		_: await super(node)


func on_character(chr: PopochiuCharacter, action: String, _item: PopochiuInventoryItem = null) -> bool:
	if chr.script_name != "Skolnik" or action == "look":
		return false
	await C.player.walk(chr.position + Vector2(-260, 20))
	await C.Skolnik.say("Pojďte ven, postavíme nový kotec!")
	return true
