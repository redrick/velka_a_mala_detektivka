@tool
extends "res://game/shared/story_room.gd"
## Story 2, the kitchen in the morning: breakfast with babička and děda. Děda doesn't want to go
## to the attic; babička whispers that he hasn't been up there for ages. Then outside for clues.

const Data := preload('room_snidane_state.gd')

var state: Data = load("res://game/rooms/snidane/room_snidane.tres")


func _on_room_entered() -> void:
	C.player.position = get_marker_position("ZeZahrady" if C.player.last_room == "Stit" else "Start")
	Globals.bring_sister(self, Vector2(-170, 10))
	place("Babicka", Vector2(1250, 900))
	if not Globals.k_breakfast:
		place("Deda", Vector2(620, 900))
	else:
		remove("Deda")


func _on_room_transition_finished() -> void:
	if Globals.phase != "k_breakfast":
		return
	Globals.phase = ""
	# done at the start, so děda waits in the garden even if the girls run out mid-scene
	Globals.k_breakfast = true
	_card(["Ráno u snídaně…"], 1.6)
	await get_tree().create_timer(2.2).timeout
	C.Alica.pose("surprised")
	await C.Alica.say("Dědo, v noci něco ťukalo na půdě!")
	C.Alica.pose()
	await C.Hanka.say("A chrápalo!")
	await C.Deda.say("Na půdu se nechodí. Jsou tam jen staré krámy…")
	await C.Deda.say("Jdu na zahradu.")
	var deda := C.Deda
	await deda.walk(Vector2(1780, 830))
	remove("Deda")
	await C.Babicka.say("Děda na půdě nebyl už hrozně dlouho. Kdoví proč…")
	C.Alica.pose("think")
	await C.Alica.say("To je případ pro detektivky! Venku pod okýnkem najdeme stopy.")
	C.Alica.pose()


func on_click(node: Node) -> void:
	match node.script_name:
		"Dvere":
			await C.player.walk_to_clicked()
			R.goto_room("Stit")
		"Micka":
			await C.player.walk_to_clicked()
			await C.player.face_clicked()
			await C.player.say("Micka spí celou noc u kamen. To nebyla ona.")
		"Hrnek1", "Hrnek2":
			await C.player.say("Mňam, kakao.")
		_:
			await super(node)


func on_look(node: Node) -> void:
	match node.script_name:
		"Kamna": await C.player.say("Kamna hřejí. Micka u nich spí.")
		"Okno": await C.player.say("Venku svítí sluníčko.")
		_: await super(node)


func on_character(chr: PopochiuCharacter, action: String, item: PopochiuInventoryItem = null) -> bool:
	if chr == C.Babicka:
		if action == "look":
			await C.player.say("Naše babička. Peče buchty.")
		elif action == "item" and item == I.Klic:
			await C.Babicka.say("Klíček s hvězdičkou? Ukažte ho dědovi.")
		else:
			await C.player.walk_to_clicked(Vector2(-200, 0))
			await C.player.face_clicked()
			if Globals.k_window:
				await C.Babicka.say("Děda je na zahradě. Ukažte mu ten klíč.")
			else:
				await C.Babicka.say("Běžte se podívat ven, detektivky. Pod okýnko na půdu.")
		return true
	if chr == C.Deda:
		await C.Deda.say("Na půdu se nechodí.")
		return true
	return false
