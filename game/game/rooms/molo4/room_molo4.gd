@tool
extends "res://game/shared/story_room.gd"
## Story 4, the jetty at three o'clock: the man with the bucket hat is Franta. Hanka shows him the new
## letter, he lifts his hat; děda and Věrka recognise him; his story (three old-photo slides).

const Data := preload('room_molo4_state.gd')

var state: Data = load("res://game/rooms/molo4/room_molo4.tres")


func _on_room_entered() -> void:
	C.player.position = get_marker_position("Start")
	place("Babicka", Vector2(880, 960))
	place("Joey", Vector2(1020, 1000))
	place("Rybar", get_marker_position("Rybar")).pose("nohat" if Globals.f_franta else "")
	if Globals.f_franta:
		place("Deda", get_marker_position("Deda"))
		place("Verka", get_marker_position("Verka"))
	else:
		remove("Deda")
		remove("Verka")
	Globals.exit_arrow(self, "Zpet", true)


func _on_room_transition_finished() -> void:
	if not Globals.f_franta:
		_card(["Ve tři hodiny na molu…"], 1.6)
		await get_tree().create_timer(2.0).timeout
		await C.Hanka.say("Pán s kloboukem. Je tady, přesně ve tři!")


func joey_goal() -> Vector2:
	return C.Rybar.position + Vector2(-240, 60) if not Globals.f_franta else Vector2(160, 960)


func on_click(node: Node) -> void:
	match node.script_name:
		"Molo":
			await C.player.walk_to_clicked()
			await C.player.say("Dřevěné molo. Tady se chytají ryby.")
		"Zpet":
			await C.player.walk_to_clicked()
			R.goto_room("Pole4")
		_: await super(node)


func on_character(chr: PopochiuCharacter, action: String, item: PopochiuInventoryItem = null) -> bool:
	if action == "look" or chr == C.Joey:
		return false
	if item:
		I.deselect_active()
	await C.player.walk(chr.position + Vector2(-260, 20))
	await C.player.face_clicked()
	match chr.script_name:
		"Rybar":
			if Globals.f_franta:
				await C.Rybar.say("Klíč patří do věže. Pojďte ke kostelu!")
			else:
				await _franta()
		"Deda": await C.Deda.say("Franta! Po tolika letech!")
		"Verka": await C.Verka.say("Klub Hvězdička je zase spolu.")
		"Babicka": await C.Babicka.say("Vedeš ty, Hanko.")
		_: return false
	return true


func _franta() -> void:
	await C.Hanka.say("Dobrý den. Tenhle dopis… Tys ho nakreslil.")
	C.Hanka.pose("point")
	await C.Hanka.say("Ty jsi Franta!")
	C.Hanka.pose()
	C.Rybar.pose("nohat")
	await C.Rybar.say("Poznalas mě podle obrázků. To nikdo předtím neuměl.")
	await C.Rybar.say("Ano. Jsem Franta.")
	place("Deda", Vector2(-120, 940))
	place("Verka", Vector2(-260, 960))
	C.Deda.ignore_walkable_areas = true
	C.Verka.ignore_walkable_areas = true
	C.Deda.walk(get_marker_position("Deda"))
	await C.Verka.walk(get_marker_position("Verka"))
	C.Deda.ignore_walkable_areas = false
	C.Verka.ignore_walkable_areas = false
	await C.Deda.say("Franto?! To jsi ty?")
	await C.Verka.say("Franto! Celou dobu jsi chodil kolem rybníka!")
	await slideshow([
		["franta_key", "Rybar", "Jako kluk jsem z věže vzal klíč od hodin. Do svého pokladu."],
		["franta_rock", "Rybar", "Poklad jsem schoval u Boty. A tvému dědovi Honzovi jsem nakreslil dopis."],
		["franta_van", "Rybar", "Druhý den jsme se odstěhovali. Dopis nikdo nepřečetl."],
		["", "Rybar", "Když jsem se vrátil, styděl jsem se zaklepat. Tak jsem ráno prošel stopu a nechal vám nový dopis."],
	])
	await C.Rybar.say("Kdo umí číst obrázky, ten mě najde. A Hanka to uměla.")
	C.Hanka.pose("grin")
	await C.Hanka.say("Já umím číst obrázky!")
	C.Hanka.pose()
	await C.Rybar.say("Ten klíč patří do věže. Pojďte, rozběhneme hodiny!")
	Globals.f_franta = true
	Globals.dress()
