@tool
extends "res://game/shared/story_room.gd"
## Story 8, the kitchen: the start (the evening before) and the clean-page night: děda smooths the snow,
## Bětka brings new parsnip noses, the night watch at the window (no torch on animals), everyone falls asleep.

const Data := preload('room_kuchyne8_state.gd')
const EVENING := Color(0.7, 0.68, 0.8)

var state: Data = load("res://game/rooms/kuchyne8/room_kuchyne8.tres")


func _on_room_entered() -> void:
	C.player.position = get_marker_position("ZeZahrady") if C.player.last_room == "Zahrada8" else get_marker_position("Start")
	Globals.bring_sister(self, Vector2(-170, 10))
	place("Babicka", Vector2(420, 900))
	place("Deda", Vector2(1150, 920))
	place("Joey", Vector2(1350, 990))
	if Globals.phase == "n_evening" or Globals.phase == "n_start":
		dark(EVENING, false)
		place("Betka", Vector2(620, 960))
	else:
		remove("Betka")
	Globals.exit_arrow(self, "Dvere", false)


func _on_room_transition_finished() -> void:
	if Globals.phase == "n_start":
		G.block()
		Globals.phase = ""
		await C.Babicka.say("Sněhuláci jsou hotoví. A mají nosy z Frantova pastináku.")
		await C.Deda.say("A ten můj je největší! Vyšší než Alica.")
		await C.Betka.say("Dobrou noc, sněhuláci!")
		Globals.phase = "n_morning"
		R.goto_room("Zahrada8")
	elif Globals.phase == "n_evening":
		Globals.phase = ""
		await _night()


func joey_goal() -> Vector2:
	return get_hotspot("Dvere").walk_to_point


func _night() -> void:
	# no clicks while it runs: the door clicked in a pause cut the night short (the next room unblocks)
	G.block()
	C.Alica.pose("lens")
	await C.Alica.say("Plán: čistá stránka. Uhladíme sníh kolem sněhuláků. Ráno si stopy přečteme.")
	C.Alica.pose()
	await C.Deda.say("To zařídím. Hrábě a koště. Sníh bude hladký jako papír.")
	await C.Betka.say("A tady jsou nové nosy. Z pastináku.")
	await C.Hanka.say("Budeme hlídat u okna! S baterkou.")
	await C.Babicka.say("Ale nesviťte na zvířata. Bojí se. A Joey spí v chodbě.")
	await C.Babicka.say("Tady máte kakao.")
	sfx("ZÍV…", Vector2(800, 380), 70)
	await get_tree().create_timer(1.2).timeout
	sfx("CHRRR…", Vector2(1100, 420), 80)
	await get_tree().create_timer(1.4).timeout
	Globals.n_day = 2
	Globals.phase = "n_morning"
	R.goto_room("Zahrada8")


func on_click(node: Node) -> void:
	match node.script_name:
		"Dvere":
			await C.player.walk_to_clicked()
			R.goto_room("Zahrada8")
		"Okno":
			await C.player.walk_to_clicked()
			await C.player.say("Z okna je vidět na sněhuláky.")
		_: await super(node)


func on_character(chr: PopochiuCharacter, action: String, _item: PopochiuInventoryItem = null) -> bool:
	if action == "look" or chr == C.Alica or chr == C.Hanka or chr == C.Joey:
		return false
	await C.player.walk(chr.position + Vector2(-240, 20))
	match chr.script_name:
		"Babicka": await C.Babicka.say("Venku je hluboký sníh. Zvířátka mají hlad.")
		"Deda": await C.Deda.say("Můj sněhulák je vyšší než ty, Alico!")
		"Betka": await C.Betka.say("Děda Franta pěstuje pastinák. Je sladký.")
		_: return false
	return true
