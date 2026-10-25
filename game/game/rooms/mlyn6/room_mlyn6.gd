@tool
extends "res://game/shared/story_room.gd"
## Story 6, the big spruce by the mill on the first Advent Sunday at dawn: gingerbread stars on red ribbons,
## a name in white icing on each. Děda, Franta and Věrka caught with the ladder; two ribbons hold only
## crumbs (the tits ate the girls' first stars, so děda took two more). The club's rule for hanging
## (minigame), seed stars for the birds, Bětka's star, Tonda late.

const Data := preload('room_mlyn6_state.gd')
const StarsGame := preload("res://game/minigames/stars.gd")
const DAWN := Color(0.78, 0.74, 0.88)

var state: Data = load("res://game/rooms/mlyn6/room_mlyn6.tres")


func _on_room_entered() -> void:
	C.player.position = get_marker_position("Start")
	Globals.bring_sister(self, Vector2(170, 10))
	place("Joey", joey_spot())
	place("Deda", get_marker_position("Deda")).pose("caught" if not Globals.p_spruce else "")
	place("Rybar", get_marker_position("Franta"))
	place("Verka", get_marker_position("Verka"))
	place("Betka", get_marker_position("Betka"))
	get_prop("NoveHvezdy").visible = Globals.p_stars
	get_prop("Zrnicka").visible = Globals.p_stars
	if not Globals.p_spruce:
		dark(DAWN, false)
	Globals.exit_arrow(self, "Zpet", true)


func _on_room_transition_finished() -> void:
	if Globals.phase == "p_spruce" or (Globals.p_who and not Globals.p_spruce):
		Globals.phase = ""
		await _caught()
	elif Globals.p_stars:
		await _finale()


func joey_goal() -> Vector2:
	return get_hotspot("Smrk").walk_to_point if not Globals.p_stars else Vector2.ZERO


func _caught() -> void:
	await C.Betka.say("Děda Franta šel taky brzy ráno ven…")
	await C.Alica.say("Dědovy stopy vedou až sem. K velkému smrku!")
	C.Hanka.pose("point")
	await C.Hanka.say("Na smrku visí perníčkové hvězdičky! Na červených stužkách!")
	C.Hanka.pose()
	await C.Deda.say("No jo. Prozradili jste nás.")
	await C.Verka.say("Klub Hvězdička měl tradici.")
	await C.Verka.say("První adventní neděli pověsil každý člen na smrk hvězdičku se svým jménem.")
	await C.Rybar.say("Šedesát let tu nevisela ani jedna.")
	await C.Rybar.say("Teď je klub zase celý. Tak jsme to chtěli obnovit. Jako překvapení.")
	await C.Alica.say("Sedm hvězdiček pro sedm členů! Ale proč pak ještě dvě?")
	await C.Deda.say("Podívejte na ty dvě stužky. Jsou na nich jen drobečky.")
	await C.Deda.say("Sýkorky snědly vaše první hvězdičky, Alico a Hanko. Tak jsem musel pro další.")
	await C.Alica.say("Proto sedm a potom dvě! Sýkorky byly na obou stopách!")
	C.Deda.pose()
	Globals.p_spruce = true
	await light_up(1.5)
	await C.Deda.say("Pomůžete nám je pověsit? Ale podle klubového pravidla!")


func on_click(node: Node) -> void:
	match node.script_name:
		"Smrk", "Zebrik", "NoveHvezdy", "Zrnicka": await _spruce()
		"Mlyn":
			await C.player.walk_to_clicked()
			await C.player.say("Mlýn paní Věrky.")
		"Zpet":
			await C.player.walk_to_clicked()
			R.goto_room("Zahrada6")
		_: await super(node)


func on_character(chr: PopochiuCharacter, action: String, _item: PopochiuInventoryItem = null) -> bool:
	if action == "look" or chr == C.Joey or chr == C.Alica or chr == C.Hanka:
		return false
	await C.player.walk(chr.position + Vector2(-240, 20))
	match chr.script_name:
		"Deda": await C.Deda.say("Na každé větvi jiná ozdoba. A nad sebou nikdy dvě stejné!" if not Globals.p_stars else "Veselý advent!")
		"Rybar":
			if Globals.p_stars:
				await C.Rybar.say("Hvězdička se nedává na zkoušku.")
			else:
				await C.Rybar.say("Hvězdičky věšíme podle klubového pravidla.")
		"Verka": await C.Verka.say("Šedesát let jsem na tenhle smrk čekala.")
		"Betka":
			if Globals.p_stars:
				await C.Betka.say("Mám taky hvězdičku!")
			else:
				await C.Betka.say("Já jsem tu s dědou Frantou. Je to tajné!")
		_: return false
	return true


func _spruce() -> void:
	await C.player.walk(get_hotspot("Smrk").walk_to_point)
	if not Globals.p_spruce:
		return
	if Globals.p_stars:
		await _finale()
		return
	await C.Deda.say("Pravidlo Klubu Hvězdička: na každé větvi visí od každé ozdoby jedna.")
	await C.Deda.say("A nad sebou nikdy dvě stejné.")
	var mg: CanvasLayer = StarsGame.new()
	add_child(mg)
	await mg.finished
	Globals.p_stars = true
	await _finale()


func _finale() -> void:
	await pop("NoveHvezdy")
	await C.Hanka.say("ALICA a HANKA! Naše hvězdičky!")
	place("Babicka", Vector2(-150, 940))
	C.Babicka.ignore_walkable_areas = true
	await C.Babicka.walk(Vector2(680, 1020))
	C.Babicka.ignore_walkable_areas = false
	await C.Babicka.say("A tady jsou zrníčkové hvězdy pro ptáčky. Perníčky si sníme doma u kakaa.")
	await pop("Zrnicka")
	sfx("PÍP PÍP!", Vector2(1200, 460), 70)
	await C.Betka.say("Mám taky hvězdičku… i když jsem na zkoušku?")
	await C.Rybar.say("Hvězdička se nedává na zkoušku, Bětko.")
	place("Tonda", Vector2(-150, 960))
	C.Tonda.ignore_walkable_areas = true
	await C.Tonda.walk(Vector2(1100, 1000))
	C.Tonda.ignore_walkable_areas = false
	await C.Tonda.say("Uf! Proč mě nikdo nevzbudil?!")
	await C.Alica.say("Případ vyřešen. Oba případy!")
	await the_end("Konec 6. dílu")
