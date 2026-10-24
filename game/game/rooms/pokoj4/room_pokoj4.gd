@tool
extends "res://game/shared/story_room.gd"
## Story 4, Alica's room at the chalupa. Alica has a fever and stays in bed: she is HQ (velitelství) and
## talks to Hanka over the walkie-talkie. Here: the start (Franta's picture letter, the walkie-talkie), the
## evening suspects talk, and the tin opened at her bed (the new letter, "Kdo šel po stopě před Hankou?").

const Data := preload('room_pokoj4_state.gd')
const WhoGame := preload("res://game/minigames/who_4.gd")
const EVENING := Color(0.72, 0.7, 0.85)

var state: Data = load("res://game/rooms/pokoj4/room_pokoj4.tres")


func _on_room_entered() -> void:
	C.player.position = get_marker_position("ZVsi") if C.player.last_room == "Ves4" else get_marker_position("Start")
	place("Alica", get_marker_position("Postel")).pose("bed")
	place("Joey", Vector2(540, 1000))
	if not Globals.f_intro or Globals.phase == "f_evening" or (Globals.f_tin and not Globals.f_read):
		place("Babicka", Vector2(420, 940))
	else:
		remove("Babicka")
	if Globals.phase == "f_evening":
		dark(EVENING, false)
	Globals.exit_arrow(self, "Dvere", false, Globals.f_intro)


func _on_room_transition_finished() -> void:
	if not Globals.f_intro:
		await _intro()
	elif Globals.phase == "f_evening":
		await _evening()
	elif Globals.f_tin and not Globals.f_opened:
		await C.Alica.say("Hani! Tys ji našla? Ukaž!")


func joey_goal() -> Vector2:
	if Globals.f_tin and not Globals.f_read:
		return C.Alica.position + Vector2(-300, 40)
	return get_hotspot("Dvere").walk_to_point if Globals.f_intro else Vector2.ZERO


#region The start ##################################################################################
func _intro() -> void:
	await C.Babicka.say("Alica má horečku. Dneska zůstane v posteli.")
	await C.Alica.say("Ale my máme Frantův dopis! A nikdo ho neumí přečíst.")
	C.Hanka.pose("point")
	await C.Hanka.say("Já ho přečtu! Já umím číst obrázky!")
	C.Hanka.pose()
	await picture("res://assets/props/picture_letter.png", "Frantův obrázkový dopis")
	await C.Hanka.say("To je slepička. A hodiny. A bota. A hvězdička.")
	C.Alica.pose("bed_talk")
	await C.Alica.say("Dneska jsi detektiv ty, Hani. Já jsem velitelství.")
	C.Alica.pose("bed_radio")
	await C.Alica.say("Tady máš vysílačku. Hlas mi všechno, co najdeš!")
	I.Vysilacka.add()
	C.Alica.pose("bed")
	await C.Babicka.say("Půjdu s vámi. Ale vede Hanka.")
	Globals.f_intro = true
	Globals.show_exit(self, "Dvere")
	await C.Hanka.say("Jdeme hledat slepičku!")
#endregion


func on_click(node: Node) -> void:
	match node.script_name:
		"Dvere":
			await C.player.walk_to_clicked()
			R.goto_room("Ves4")
		"Okno":
			await C.player.walk_to_clicked()
			await C.player.say("Venku fouká vítr. Padá listí.")
		"Stolek":
			await C.player.walk_to_clicked()
			await C.player.say("Čaj s medem pro Alicu. Na horečku.")
		_: await super(node)


func on_item(node: Node, item: PopochiuInventoryItem) -> void:
	I.deselect_active()
	await on_click(node)


func on_character(chr: PopochiuCharacter, action: String, item: PopochiuInventoryItem = null) -> bool:
	if chr != C.Alica or action == "look":
		return false
	if item:
		I.deselect_active()
	await C.player.walk(C.Alica.position + Vector2(-330, 20))
	await C.player.face_clicked()
	if Globals.f_tin and not Globals.f_opened:
		await _open_tin()
	elif Globals.f_opened and not Globals.f_read:
		await _who_and_read()
	elif not Globals.f_prints:
		await C.Alica.say("Najdi slepičku z dopisu, Hani. A hlas mi to!")
	elif not Globals.f_three:
		await C.Alica.say("Další obrázek jsou hodiny. Na věži jsou hodiny!")
	elif not Globals.f_tin:
		await C.Alica.say("Bota a hvězdička… Kde je ta hvězdička?")
	elif not Globals.f_franta:
		await C.Alica.say("Běž, Hani! Ve tři na molu!")
	else:
		await C.Alica.say("Ať hodiny zase jdou!")
	return true


#region Evening: the suspects #######################################################################
func _evening() -> void:
	Globals.phase = ""
	C.Alica.pose("bed_lens")
	await C.Alica.say("Tak co víme? Někdo jde po stopě před námi. Má velké boty.")
	await C.Alica.say("Podezřelý číslo jedna: kostelník. Má velké boty a nechce nás pustit na věž.")
	await C.Alica.say("Číslo dvě: straka. Odnesla něco lesklého.")
	await C.Alica.say("A číslo tři: pan rybář. Šel kolem přesně ve tři!")
	C.Alica.pose("bed")
	await C.Hanka.say("Pan rybář je hodný. Mával na mě.")
	await C.Alica.say("Detektiv musí podezírat každého, Hani.")
	await C.Babicka.say("Spát, detektivky. Zítra je taky den.")
	Globals.f_evening = true
	Globals.phase = "f_morning"
	R.goto_room("Ves4")
#endregion


#region The tin, the new letter #####################################################################
func _open_tin() -> void:
	I.Plechovka.remove()
	await C.Hanka.say("Tady je! Byla schovaná u špičky Boty.")
	await pop("Plechovka")
	sfx("SKŘÍP!", Vector2(700, 380), 70)
	C.Alica.pose("bed_lens")
	await pop("Pistalka")
	await C.Alica.say("Píšťalka slepička!")
	await pop("Kulicky")
	await C.Alica.say("Kuličky.")
	await pop("Klic")
	await C.Babicka.say("A obří železný klíč. Od čeho takový klíč?")
	await pop("Dopis")
	C.Alica.pose("bed_talk")
	await C.Alica.say("Počkej! Tenhle dopis je nový. Papír je bílý a čistý.")
	await C.Alica.say("Někdo sem dal nový dopis! Ten, kdo šel po stopě před tebou.")
	C.Alica.pose("bed")
	for p in ["Plechovka", "Pistalka", "Kulicky", "Klic", "Dopis"]:
		get_prop(p).hide()
	I.NovyDopis.add()
	I.KlicHodin.add()
	Globals.f_opened = true
	await _who_and_read()


func _who_and_read() -> void:
	if not Globals.f_who:
		await C.Alica.say("Tak, detektive Hanko. Kdo šel po stopě před tebou?")
		var mg: CanvasLayer = WhoGame.new()
		add_child(mg)
		await mg.finished
		Globals.f_who = true
		await C.Alica.say("Pan rybář? Ale proč? Chce Frantův poklad?")
		await C.Hanka.say("Nechce. Nic nevzal. Jenom kreslil.")
		await C.Alica.say("…Máš pravdu, Hani.")
	await picture("res://assets/props/new_letter.png", "Nový dopis")
	await C.Hanka.say("Rybička. Molo. Hodiny ve tři. Klobouk.")
	C.Hanka.pose("point")
	await C.Hanka.say("Ve tři hodiny na molu čeká pán s kloboukem!")
	C.Hanka.pose()
	await C.Alica.say("Tak běž, Hani! Molo je u rybníka. Babička půjde s tebou.")
	Globals.f_read = true
#endregion
