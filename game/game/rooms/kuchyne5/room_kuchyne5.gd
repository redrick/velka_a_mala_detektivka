@tool
extends "res://game/shared/story_room.gd"
## Story 5, babička's kitchen in winter. The first snow (start); the night watch at the window where
## everyone falls asleep; the suspects board and babička cleared (dough on her gloves, baking for Advent),
## then the wet mittens by the stove get sorted ("Čí je rukavice?").
## When a day's clues are found, going to bed here moves the story to the next morning in the garden.

const Data := preload('room_kuchyne5_state.gd')
const MittensGame := preload("res://game/minigames/mittens.gd")
const NIGHT := Color(0.45, 0.47, 0.66)

var state: Data = load("res://game/rooms/kuchyne5/room_kuchyne5.tres")


func _on_room_entered() -> void:
	C.player.position = get_marker_position("ZeZahrady") if C.player.last_room == "Zahrada5" else get_marker_position("Start")
	Globals.bring_sister(self, Vector2(-170, 10))
	place("Babicka", Vector2(1100, 900))
	place("Joey", Vector2(1450, 1000))
	if not Globals.s_intro or _day_done():
		dark(NIGHT, false)
	Globals.exit_arrow(self, "Dvere", false, Globals.s_intro)


func _on_room_transition_finished() -> void:
	if not Globals.s_intro:
		await _first_snow()
	elif _day_done():
		await _night()


func joey_goal() -> Vector2:
	if Globals.s_day == 2 and Globals.s_dog and Globals.s_thread and not Globals.s_babicka:
		return C.Babicka.position + Vector2(240, 60)
	return get_hotspot("Dvere").walk_to_point


## All the clues of the current day are found: tonight is the night.
func _day_done() -> bool:
	match Globals.s_day:
		1: return Globals.s_nose and Globals.s_stars and Globals.s_road and Globals.s_tonda
		2: return Globals.s_dog and Globals.s_thread and Globals.s_babicka and Globals.s_tonda_ok and Globals.s_parsnip \
				and Globals.s_boots and Globals.s_curtain
		3: return Globals.s_answer
	return false


func _first_snow() -> void:
	C.Hanka.pose("point")
	await C.Hanka.say("Sněží! První sníh!")
	C.Hanka.pose()
	await C.Babicka.say("Ráno postavíme sněhuláka!")
	await C.Alica.say("Velkého! Až do nebe!")
	Globals.s_intro = true
	await _next_morning()


func _night() -> void:
	match Globals.s_day:
		1:
			C.Alica.pose("lens")
			await C.Alica.say("Dneska ho chytíme. Budu hlídat u okna celou noc!")
			C.Alica.pose()
			await C.Hanka.say("Já taky… Já budu hlídat taky…")
			sfx("ZÍV…", Vector2(700, 380), 70)
			await get_tree().create_timer(1.2).timeout
			sfx("CHRRR…", Vector2(1100, 420), 80)
			await get_tree().create_timer(1.4).timeout
			await C.Babicka.say("Usnuly obě. I Joey chrápe. Do postele, detektivky.")
		2:
			await C.Alica.say("Malé botičky s hvězdičkami… u Franty. Zítra ráno to uvidíme.")
		3:
			await C.Hanka.say("Myslíš, že nám odpoví?")
			await C.Alica.say("Uvidíme ráno.")
	await _next_morning()


func _next_morning() -> void:
	Globals.s_day += 1
	Globals.phase = "s_morning"
	R.goto_room("Zahrada5")


func _mittens() -> void:
	await C.Babicka.say("A teď všechny mokré rukavice ke kamnům. Ať do zítřka uschnou.")
	await C.Hanka.say("Babi, ony se pomíchaly! Která je čí?")
	var mg: CanvasLayer = MittensGame.new()
	add_child(mg)
	await mg.finished
	Globals.s_mittens = true
	await C.Babicka.say("Šikovné holky. Každá rukavice má zase svého majitele.")


func on_click(node: Node) -> void:
	match node.script_name:
		"Dvere":
			await C.player.walk_to_clicked()
			R.goto_room("Zahrada5")
		"Okno":
			await C.player.walk_to_clicked()
			await C.player.say("Z okna je vidět zahrada. Celá bílá.")
		"Kamna":
			await C.player.walk_to_clicked()
			await C.player.say("Kamna hřejí. Voní to tu perníkem.")
		_: await super(node)


func on_character(chr: PopochiuCharacter, action: String, _item: PopochiuInventoryItem = null) -> bool:
	if chr.script_name != "Babicka" or action == "look":
		return false
	await C.player.walk(chr.position + Vector2(260, 20))
	await C.player.face_clicked()
	if Globals.s_day == 2 and Globals.s_dog and Globals.s_thread and not Globals.s_babicka:
		C.Alica.pose("lens")
		if not Globals.s_tonda_ok:
			await C.Alica.say("Tabule podezřelých. Číslo jedna: Tonda. Staví sněhuláky a má sáně.")
		else:
			await C.Alica.say("Tabule podezřelých. Tondu už jsme škrtli.")
		await C.Alica.say("Babička! Vstává první a ráno má mokré rukavice!")
		await C.Alica.say("A někdo s červenou bambulí.")
		C.Alica.pose()
		await C.Babicka.say("Já? Hahaha!")
		C.Babicka.pose("flour")
		await C.Babicka.say("Rukavice mám mokré od těsta. Peču potají, ještě za tmy. To je překvapení na advent!")
		await C.Babicka.say("A mrkve mám všechny. Spočítala jsem je.")
		C.Babicka.pose()
		await C.Alica.say("Babička to nebyla. Škrtám!")
		Globals.s_babicka = true
		await _mittens()
		if not Globals.s_tonda_ok:
			await C.Hanka.say("A co Tonda? Zeptáme se ho na silnici.")
	elif _day_done():
		await _night()
	else:
		await C.Babicka.say("Venku je krásně. Běžte si hrát!")
	return true
