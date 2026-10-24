@tool
extends "res://game/shared/story_room.gd"
## Story 6, the snowy garden: after the dawn watch the girls and děda build a bird feeder under the kitchen
## window, every bird gets its own food ("Kdo co zobe?"), "Případ vyřešen!", and that evening passes. Later
## the way to the mill starts here.

const Data := preload('room_zahrada6_state.gd')
const BirdsGame := preload("res://game/minigames/birds.gd")

var state: Data = load("res://game/rooms/zahrada6/room_zahrada6.tres")


func _on_room_entered() -> void:
	C.player.position = get_marker_position("ZMlyna") if C.player.last_room == "Mlyn6" else get_marker_position("Start")
	Globals.bring_sister(self, Vector2(170, 10))
	place("Joey", joey_spot())
	if Globals.p_birds and not Globals.p_feeder:
		place("Deda", Vector2(1200, 900))
	else:
		remove("Deda")
	get_prop("Krmitko").visible = Globals.p_feeder
	Globals.exit_arrow(self, "KMlynu", false, Globals.p_who)
	get_hotspot("KMlynu").clickable = Globals.p_who


func joey_goal() -> Vector2:
	if Globals.p_birds and not Globals.p_feeder:
		return get_hotspot("Misto").walk_to_point
	return get_hotspot("Dum").walk_to_point


func on_click(node: Node) -> void:
	match node.script_name:
		"Misto", "Krmitko": await _feeder()
		"Dum":
			await C.player.walk_to_clicked()
			R.goto_room("Kuchyne6")
		"KMlynu":
			await C.player.walk_to_clicked()
			R.goto_room("Mlyn6")
		_: await super(node)


func on_character(chr: PopochiuCharacter, action: String, _item: PopochiuInventoryItem = null) -> bool:
	if chr.script_name != "Deda" or action == "look":
		return false
	await _feeder()
	return true


func _feeder() -> void:
	await C.player.walk(get_hotspot("Misto").walk_to_point)
	if not Globals.p_birds:
		await C.player.say("Místo pod kuchyňským oknem.")
		return
	if Globals.p_feeder:
		await C.player.say("Krmítko! Sýkorky už zobou semínka.")
		return
	await C.Deda.say("Tady ho postavíme. Já zatluču kůl, vy nasypete semínka.")
	sfx("ŤUK ŤUK!", Vector2(980, 500), 70)
	await pop("Krmitko")
	await C.Deda.say("Přiletí sýkorky, hýli, kos i vrabci. A každý má rád něco jiného.")
	var mg: CanvasLayer = BirdsGame.new()
	add_child(mg)
	await mg.finished
	Globals.p_food = true
	await C.Hanka.say("Semínka a lůj. Ne perníček!")
	await C.Alica.say("Ptáčci mají krmítko. Případ vyřešen!")
	await C.Deda.say("Výborně, detektivky. Tak a teď spát.")
	Globals.p_feeder = true
	remove("Deda")
	await fade(func(): pass, "Večer… a ráno…")
	Globals.p_day = 2
	Globals.phase = "p_morning"
	R.goto_room("Kuchyne6")
