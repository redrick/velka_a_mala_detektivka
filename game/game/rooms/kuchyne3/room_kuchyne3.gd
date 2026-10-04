@tool
extends "res://game/shared/story_room.gd"
## Story 3, the kitchen. It starts here with the whole map on the table, and the evening after the
## first day at the pond is here too: the sisters quarrel about Tonda and děda makes them friends again.

const Data := preload('room_kuchyne3_state.gd')

var state: Data = load("res://game/rooms/kuchyne3/room_kuchyne3.tres")


func _on_room_entered() -> void:
	C.player.position = get_marker_position("ZRybnika" if C.player.last_room == "Rybnik" else "Start")
	Globals.bring_sister(self, Vector2(-170, 10))
	if Globals.phase == "r_evening":
		place("Deda", Vector2(1250, 900))
		remove("Babicka")
		dark(Color(0.62, 0.55, 0.5), false)
		glow(Vector2(960, 300), Color(1.0, 0.85, 0.55), 1.1, 4.0)
	elif not Globals.r_intro:
		place("Deda", Vector2(1250, 900))
		place("Babicka", Vector2(1500, 900))
	else:
		remove("Deda")
		place("Babicka", Vector2(1500, 900))


func _on_room_transition_finished() -> void:
	if Globals.phase == "r_evening":
		await _evening()
	elif not Globals.r_intro:
		Globals.r_intro = true
		await _intro()


func _intro() -> void:
	await C.Alica.say("Obě půlky jsou slepené. Mapa je celá!")
	await C.Hanka.say("Kde je poklad?")
	await picture("res://assets/props/map_big.png", "Mapa ke starému rybníku")
	await C.Deda.say("Tady je naše chalupa. A tady starý rybník u mlýna.")
	await C.Deda.say("Od velké vrby dvacet kroků. Tam je křížek!")
	await C.Deda.say("Ale pozor. Pravidlo klubu: poklad hledá jen celý klub.")
	C.Alica.pose("grin")
	await C.Alica.say("My jsme přece nové členky! Jdeme k rybníku!")
	C.Alica.pose()


func _evening() -> void:
	Globals.phase = ""
	await C.Alica.say("Je to jasné. Byl to Tonda! Měl lopatku a utekl!")
	C.Hanka.pose("worried")
	await C.Hanka.say("Tonda je hodný! On to nebyl!")
	await C.Alica.say("Ty tomu nerozumíš. Jsi malá.")
	await C.Hanka.say("Nejsem!")
	C.Hanka.pose()
	await C.Deda.say("Víte, co říkala Věrka? Klub Hvězdička drží spolu.")
	await C.Deda.say("Jeden detektiv nevidí všechno. Dva vidí víc.")
	await C.Alica.say("Promiň, Hanko.")
	C.Hanka.pose("grin")
	await C.Hanka.say("Tak ráno zjistíme, co Tonda kopal. Spolu!")
	C.Hanka.pose()
	Globals.r_evening = true
	Globals.phase = "r_dawn"
	R.goto_room("Rybnik")


func on_click(node: Node) -> void:
	match node.script_name:
		"Dvere":
			await C.player.walk_to_clicked()
			R.goto_room("Rybnik")
		"MapaStul":
			await C.player.walk_to_clicked()
			await picture("res://assets/props/map_big.png", "Od velké vrby dvacet kroků")
		_:
			await super(node)


func on_look(node: Node) -> void:
	match node.script_name:
		"Okno": await C.player.say("Za oknem je zahrada.")
		"Kamna": await C.player.say("Kamna hřejí.")
		_: await super(node)


func on_character(chr: PopochiuCharacter, action: String, _item: PopochiuInventoryItem = null) -> bool:
	if action == "look":
		return false
	if chr == C.Deda:
		await C.Deda.say("Od velké vrby dvacet kroků. Běžte, já půjdu s vámi!")
		return true
	if chr == C.Babicka:
		await C.Babicka.say("Hodně štěstí, detektivky! A vraťte se na večeři.")
		return true
	return false
