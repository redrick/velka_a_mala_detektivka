@tool
extends "res://game/shared/story_room.gd"
## Story 7, the kitchen in the evening: babička's ring is gone ("od dědy, s hvězdičkou").

const Data := preload('room_kuchyne7_state.gd')
const OrderGame := preload("res://game/minigames/joey_morning.gd")
const EVENING := Color(0.75, 0.7, 0.66)

var state: Data = load("res://game/rooms/kuchyne7/room_kuchyne7.tres")


func _on_room_entered() -> void:
	C.player.position = get_marker_position("ZeZahrady") if C.player.last_room == "Zahrada7" else get_marker_position("Start")
	Globals.bring_sister(self, Vector2(-170, 10))
	place("Babicka", Vector2(420, 900))
	place("Deda", Vector2(1100, 920))
	place("Joey", Vector2(1300, 990))
	if not Globals.j_straka:
		dark(EVENING, false)
	Globals.exit_arrow(self, "Dvere", false)


func _on_room_transition_finished() -> void:
	if Globals.j_morning and not Globals.j_case:
		await _case()


func joey_goal() -> Vector2:
	return get_hotspot("Dvere").walk_to_point


func _case() -> void:
	_card(["Večer…"], 1.6)
	await get_tree().create_timer(2.0).timeout
	await C.Babicka.say("Můj prstýnek! Je pryč!")
	await C.Deda.say("Ten s hvězdičkou? Ten jsem ti dal, když jsme byli mladí.")
	await C.Babicka.say("Ráno u krmítka jsem ho ještě měla. Ruce jsem měla studené…")
	C.Alica.pose("lens")
	await C.Alica.say("Nejdřív seřadíme, co se dneska dělo.")
	C.Alica.pose()
	var mg: CanvasLayer = OrderGame.new()
	add_child(mg)
	await mg.finished
	Globals.j_order = true
	C.Alica.pose("lens")
	await C.Alica.say("Velká a malá detektivka to vyřeší! Hani, vezmi baterku. Jdeme na zahradu!")
	C.Alica.pose()
	Globals.j_case = true


func on_click(node: Node) -> void:
	match node.script_name:
		"Dvere":
			await C.player.walk_to_clicked()
			R.goto_room("Zahrada7")
		"Kamna":
			await C.player.walk_to_clicked()
			await C.player.say("U kamen je teplo. Tady babička hřála ruce.")
		_: await super(node)


func on_character(chr: PopochiuCharacter, action: String, _item: PopochiuInventoryItem = null) -> bool:
	if action == "look" or chr == C.Alica or chr == C.Hanka or chr == C.Joey:
		return false
	await C.player.walk(chr.position + Vector2(-240, 20))
	match chr.script_name:
		"Babicka": await C.Babicka.say("Ráno u krmítka jsem ho ještě měla.")
		"Deda": await C.Deda.say("Ráno jsem odházel sníh od krmítka. Na velkou hromadu.")
		_: return false
	return true
