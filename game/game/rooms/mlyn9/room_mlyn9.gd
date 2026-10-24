@tool
extends "res://game/shared/story_room.gd"
## Story 9, at the mill: Věrka hides something with a star behind her back. It's her kominík hat for the
## parade; Joey smells flour on her, not lavender.

const Data := preload('room_mlyn9_state.gd')

var state: Data = load("res://game/rooms/mlyn9/room_mlyn9.tres")


func _on_room_entered() -> void:
	C.player.position = get_marker_position("Start")
	Globals.bring_sister(self, Vector2(170, 10))
	place("Joey", joey_spot())
	place("Verka", get_marker_position("Verka")).pose("hide" if not Globals.z_verka else "")
	Globals.exit_arrow(self, "Zpet", true)


func joey_goal() -> Vector2:
	return C.Verka.position + Vector2(-240, 40) if not Globals.z_verka else get_hotspot("Zpet").walk_to_point


func on_click(node: Node) -> void:
	match node.script_name:
		"Mlyn":
			await C.player.walk_to_clicked()
			await C.player.say("Mlýn paní Věrky. Z okna voní chleba.")
		"Zpet":
			await C.player.walk_to_clicked()
			R.goto_room("Kuchyne9")
		_: await super(node)


func on_character(chr: PopochiuCharacter, action: String, _item: PopochiuInventoryItem = null) -> bool:
	if chr.script_name != "Verka" or action == "look":
		return false
	await C.player.walk(chr.position + Vector2(-260, 20))
	if Globals.z_verka:
		await C.Verka.say("Uvidíme se na masopustu!")
		return true
	await C.Alica.say("Paní Věrko, co schováváte za zády? Něco s hvězdičkou!")
	await C.Verka.say("Ale nic, to je… překvapení!")
	await C.Joey.walk(chr.position + Vector2(-160, 60))
	await C.Joey.say("Čmuch čmuch.")
	await C.Hanka.say("Joey čmuchá. Paní Věrka voní moukou. Ne levandulí.")
	C.Verka.pose()
	await C.Verka.say("No dobře. To je můj klobouk na masopust. Budu kominík! S hvězdičkou.")
	await C.Alica.say("Ten klobouk má rovný kraj. Žádné zoubky. A papírek voněl levandulí… Škrtám.")
	Globals.z_verka = true
	await C.Hanka.say("Půjdeme domů!")
	return true
