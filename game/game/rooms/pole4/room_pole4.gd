@tool
extends "res://game/shared/story_room.gd"
## Story 4, the field by the brook at the forest edge. Day 1: lots of rocks, which one? The magpie flies
## off with something shiny, Tonda fishes an old boot out of the brook; dusk, home. Day 2 (after the
## view from the tower): the Bota rock, the magpie drops a sweet wrapper, the zigzag prints and a float;
## dusk again: Hanka's torch finds the star in the crack at the toe, and the tin. On the way to the Bota rock
## Alica radios Hanka through the rocks ("Navigace vysílačkou").

const Data := preload('room_pole4_state.gd')
const RadioGame := preload("res://game/minigames/radio.gd")
const DUSK := Color(0.45, 0.45, 0.62)

var state: Data = load("res://game/rooms/pole4/room_pole4.tres")


func _on_room_entered() -> void:
	match C.player.last_room:
		"Molo4": C.player.position = get_marker_position("ZMola")
		_: C.player.position = get_marker_position("Start")
	var side := 1.0 if C.player.position.x < 700 else -1.0
	place("Babicka", C.player.position + Vector2(230 * side, 10))
	place("Joey", C.player.position + Vector2(330 * side, 40))
	if Globals.f_three and not Globals.f_tin:
		place("Tonda", Vector2(760, 960))
	else:
		remove("Tonda")
	get_prop("Straka").visible = not Globals.f_bota and not Globals.f_magpie
	for p in ["Obal", "Splavek", "StopyB"]:
		get_prop(p).visible = Globals.f_bota
	get_prop("Plechovka").visible = false
	if Globals.f_bota and not Globals.f_tin:
		dark(DUSK)
	Globals.exit_arrow(self, "DoVsi", true)
	Globals.exit_arrow(self, "KRybniku", false, Globals.f_read)
	get_hotspot("KRybniku").clickable = Globals.f_read


func _on_room_transition_finished() -> void:
	if Globals.f_rocks == 0 and not Globals.f_tower:
		await C.Hanka.say("Ručička ukazovala sem. Ale kamenů je tu hodně!")
		await C.Babicka.say("Který z nich je ten pravý?")
	elif Globals.f_tower and not Globals.f_bota:
		await C.Hanka.say("Z věže byla vidět bota. Ten velký kámen!")


func joey_goal() -> Vector2:
	if not Globals.f_three:
		return get_hotspot("DoVsi").walk_to_point
	if not Globals.f_tower:
		if not Globals.f_magpie:
			return get_marker_position("Bota") + Vector2(-200, 0)
		if not Globals.f_boot:
			return get_hotspot("Potok").walk_to_point
		return get_hotspot("Kamen3").walk_to_point if Globals.f_rocks > 0 else get_hotspot("Kamen1").walk_to_point
	if not Globals.f_bota:
		return get_marker_position("Bota")
	if not Globals.f_tin:
		return get_hotspot("Skulina").walk_to_point + Vector2(60, 20)
	if Globals.f_read:
		return Vector2(1760, 960)
	return Vector2(160, 960)


func on_click(node: Node) -> void:
	match node.script_name:
		"Kamen1", "Kamen2", "Kamen3": await _rock(node)
		"Bota": await _bota()
		"Skulina": await _crack()
		"Straka": await _magpie()
		"Potok": await _brook()
		"Splavek":
			await C.player.walk_to_clicked()
			await C.player.say("Červenobílý splávek. Na ryby.")
		"Obal":
			await C.player.walk_to_clicked()
			await C.player.say("Obal od bonbonu. Ten upustila straka.")
		"StopyB":
			await C.player.walk_to_clicked()
			await C.player.say("Zase ty obří cikcak stopy.")
		"DoVsi":
			await C.player.walk_to_clicked()
			R.goto_room("Ves4")
		"KRybniku":
			await C.player.walk_to_clicked()
			R.goto_room("Molo4")
		_: await super(node)


func on_item(node: Node, item: PopochiuInventoryItem) -> void:
	I.deselect_active()
	if item == I.Vysilacka:
		C.Hanka.pose("radio")
		await C.Hanka.say("Velitelství, slyšíš?")
		await radio("Slyším, Hani! Kam ukazuje ručička?" if not Globals.f_tower else "Bota a pak hvězdička. Hledej hvězdičku!")
		C.Hanka.pose()
	else:
		await on_click(node)


func on_character(chr: PopochiuCharacter, action: String, item: PopochiuInventoryItem = null) -> bool:
	if action == "look" or chr == C.Joey:
		return false
	if item:
		I.deselect_active()
	await C.player.walk_to_clicked(Vector2(-220, 0))
	await C.player.face_clicked()
	match chr.script_name:
		"Babicka": await C.Babicka.say("Vedeš ty, Hanko.")
		"Tonda": await C.Tonda.say("Tady je tolik kamenů… Hledáme hvězdičku, ne?")
		_: return false
	return true


#region Day 1 ######################################################################################
func _rock(node: Node) -> void:
	await C.player.walk_to_clicked()
	if Globals.f_tower:
		await C.player.say("Obyčejný kámen. Bota je ten velký.")
		return
	Globals.f_rocks += 1
	await C.player.say(["Tenhle? Nic tu není.", "Tady taky ne.", "Ani tady. Žádná hvězdička."][mini(Globals.f_rocks - 1, 2)])
	await _maybe_evening()


func _bota() -> void:
	if Globals.f_tower and not Globals.f_radio:
		C.Hanka.pose("radio")
		await C.Hanka.say("Velitelství! Je tu tolik kamenů a keřů. Kudy k Botě?")
		await radio("Vidím to jako z věže, Hani. Jdi rovně, dokud tě něco nezastaví. Navedu tě!")
		C.Hanka.pose()
		var mg: CanvasLayer = RadioGame.new()
		add_child(mg)
		await mg.finished
		Globals.f_radio = true
	await C.player.walk(get_marker_position("Bota"))
	if not Globals.f_tower:
		Globals.f_rocks += 1
		await C.Hanka.say("Velký kámen. Hvězdička tu není.")
		await _maybe_evening()
		return
	if Globals.f_bota:
		await C.player.say("Kamenná bota. Kde je hvězdička?")
		return
	await C.Hanka.say("Kamenná bota! Z věže to bylo vidět.")
	await pop("Obal")
	await C.Tonda.say("Tady je něco lesklého! Obal od bonbonu.")
	await C.Hanka.say("To upustila straka! Tak straka nic nevzala.")
	await pop("StopyB")
	C.Hanka.pose("point")
	await C.Hanka.say("A zase obří boty! Cikcak!")
	C.Hanka.pose()
	await pop("Splavek")
	await C.Tonda.say("Splávek. To tu ztratil nějaký rybář.")
	C.Hanka.pose("radio")
	await C.Hanka.say("Velitelství! U Boty jsou zase obří stopy. A splávek.")
	await radio("Zase ta velká bota! Je pořád před námi!")
	C.Hanka.pose()
	await C.Babicka.say("Ale hvězdička tu nikde není…")
	await C.Babicka.say("A už se stmívá.")
	Globals.f_bota = true
	dark(DUSK)
	C.Hanka.pose("torch")
	await C.Hanka.say("Nevadí. Já mám baterku!")


func _magpie() -> void:
	await C.player.walk(get_marker_position("Bota") + Vector2(-200, 0))
	sfx("ČAK ČAK!", get_prop("Straka").position + Vector2(-80, -120), 70)
	var s: Node2D = get_prop("Straka")
	var tw := create_tween()
	tw.tween_property(s, "position", s.position + Vector2(900, -500), 1.2)
	await tw.finished
	s.hide()
	Globals.f_magpie = true
	await C.Hanka.say("Straka něco odnesla! Něco lesklého!")
	C.Hanka.pose("radio")
	await radio("Straka! Straky kradou lesklé věci. Podezřelá číslo dvě!")
	C.Hanka.pose()
	await _maybe_evening()


func _brook() -> void:
	await C.player.walk_to_clicked()
	if Globals.f_boot or not Globals.f_three:
		await C.player.say("Potok. Studená voda.")
		return
	Globals.f_boot = true
	await C.Tonda.walk(Vector2(900, 880))
	await C.Tonda.say("Hele, něco tam je! Bota! Našel jsem botu z dopisu!")
	sfx("KVÁK!", Vector2(900, 540), 80)
	await C.Hanka.say("Hihi! To je jen stará bota. A vyskočila z ní žába.")
	await _maybe_evening()


## The first day ends once Hanka has looked around enough.
func _maybe_evening() -> void:
	if Globals.f_evening or Globals.f_tower or not (Globals.f_magpie and Globals.f_boot) or Globals.f_rocks < 2:
		return
	await C.Babicka.say("Stmívá se, Hanko. Pojďme domů. Alica na nás čeká.")
	await C.Hanka.say("Zítra najdu tu pravou botu!")
	Globals.phase = "f_evening"
	R.goto_room("Pokoj4")
#endregion


#region Day 2: the star and the tin ##################################################################
func _crack() -> void:
	await C.player.walk_to_clicked()
	if not Globals.f_bota:
		await C.player.say("Škvíra u kamene. Je tam tma.")
		return
	if Globals.f_tin:
		await C.player.say("Tady byla plechovka.")
		return
	await hand_over(C.Hanka, "Hani, posviť tam baterkou!")
	C.Hanka.pose("torch")
	await C.Hanka.say("Škvíra u špičky boty. Posvítím tam…")
	sfx("CVAK!", Vector2(1420, 600), 70)
	await C.Hanka.say("Hvězdička! Vyrytá do kamene!")
	await pop("Plechovka")
	await C.Hanka.say("A plechovka! MÁM JI!")
	get_prop("Plechovka").hide()
	I.Plechovka.add()
	Globals.f_tin = true
	C.Hanka.pose("radio")
	await radio("HURÁ! Hani, ty jsi to vyřešila! Přines ji domů!")
	C.Hanka.pose()
	await C.Babicka.say("Pojďme domů. Za Alicou.")
#endregion
