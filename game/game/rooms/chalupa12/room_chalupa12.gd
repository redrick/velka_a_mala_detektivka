@tool
extends "res://game/shared/story_room.gd"
## Story 12, the chalupa three weeks after Easter: the chicks, the first chalk arrow (dashed, a heart at the end,
## like máma's lunchbox notes), děda's locked shed ("mňau" from inside, "To byla… straka!"), babička all floury
## at the kitchen door. Then the drive home.

const Data := preload('room_chalupa12_state.gd')

var state: Data = load("res://game/rooms/chalupa12/room_chalupa12.tres")


func _on_room_entered() -> void:
	C.player.position = get_marker_position("Start")
	Globals.bring_sister(self, Vector2(170, 10))
	place("Joey", joey_spot())
	place("Deda", get_marker_position("Deda"))
	place("Mama", get_marker_position("Mama"))
	place("Babicka", get_marker_position("Babicka")).pose("flour" if Globals.a_flour else "")
	get_prop("Mouka").visible = Globals.a_flour
	Globals.exit_arrow(self, "Auto", true, _done())


func _on_room_transition_finished() -> void:
	if not Globals.a_intro:
		_card(["O tři týdny později…"], 2.0)
		await get_tree().create_timer(2.4).timeout
		await C.Hanka.say("Kuřátka! Pípají!")
		await C.Mama.say("Svačinu máte v batůžku. S lístečkem.")
		C.Alica.pose("lens")
		await C.Alica.say("Na lístečku je srdíčko. Máma se tak vždycky podepisuje.")
		C.Alica.pose()
		Globals.a_intro = true


func _done() -> bool:
	return Globals.a_arrow and Globals.a_shed and Globals.a_flour


func joey_goal() -> Vector2:
	if not Globals.a_arrow: return get_prop("Sipka").position + Vector2(-260, 20)
	if not Globals.a_shed: return get_hotspot("Kulna").walk_to_point
	if not Globals.a_flour: return get_hotspot("Dum").walk_to_point
	return get_hotspot("Auto").walk_to_point


func on_click(node: Node) -> void:
	match node.script_name:
		"Sipka": await _arrow()
		"Kulna": await _shed()
		"Dum", "Mouka": await _kitchen()
		"Kurnik":
			await C.player.walk_to_clicked()
			await C.player.say("Kropenatka hlídá svých osm kuřátek.")
		"Auto": await _drive_home()
		_: await super(node)


func on_character(chr: PopochiuCharacter, action: String, _item: PopochiuInventoryItem = null) -> bool:
	if action == "look" or chr == C.Alica or chr == C.Hanka or chr == C.Joey:
		return false
	await C.player.walk(chr.position + Vector2(-240, 20))
	match chr.script_name:
		"Deda":
			if Globals.a_shed:
				await C.Deda.say("Kůlna je zamčená. Kvůli… strace.")
			else:
				await C.Deda.say("Holčičky, ke kůlně dneska nechoďte.")
		"Babicka":
			if Globals.a_flour:
				await C.Babicka.say("Nesmíš sem! Ani nakouknout!")
			else:
				await C.Babicka.say("Mám v kuchyni moc práce.")
		"Mama":
			if _done():
				await C.Mama.say("Jedeme domů, holky!")
			else:
				await C.Mama.say("Ještě chvilku a jedeme domů.")
		_: return false
	return true


func _arrow() -> void:
	await C.player.walk(get_prop("Sipka").position + Vector2(-260, 20))
	if Globals.a_arrow:
		await C.player.say("Čárkovaná šipka. Na konci srdíčko.")
		return
	C.Alica.pose("lens")
	await C.Alica.say("Šipka z křídy! Čárkovaná. A na konci srdíčko.")
	C.Alica.pose()
	await C.Alica.say("Kdo ji nakreslil? A kam vede?")
	await C.Hanka.say("Hihi. Nevím!")
	Globals.a_arrow = true
	await _check_done()


func _shed() -> void:
	await C.player.walk(get_hotspot("Kulna").walk_to_point)
	if Globals.a_shed:
		await C.player.say("Kůlna je zamčená. Dole je díra a škrábance.")
		return
	await C.Alica.say("Kůlna je zamčená. Dědo, co tam máš?")
	sfx("MŇAU!", Vector2(1810, 600), 70)
	await C.Alica.say("Mňau?")
	await C.Deda.say("To byla… straka!")
	await C.Alica.say("Straka nemňouká, dědo!")
	await C.Deda.say("Tahle jo.")
	Globals.a_shed = true
	await _check_done()


func _kitchen() -> void:
	await C.player.walk(get_hotspot("Dum").walk_to_point)
	if Globals.a_flour:
		await C.player.say("Babička je celá od mouky. A nepustí nás dovnitř.")
		return
	C.Babicka.pose("flour")
	await pop("Mouka")
	await C.Babicka.say("Nesmíš sem! Ani nakouknout!")
	await C.Alica.say("Babi, ty jsi celá od mouky!")
	await C.Babicka.say("To nic. To já jen tak… peču.")
	Globals.a_flour = true
	await _check_done()


func _check_done() -> void:
	if not _done():
		return
	await C.Alica.say("Všichni se chovají nějak divně.")
	await C.Mama.say("Jedeme domů, holky!")
	Globals.exit_arrow(self, "Auto", true)


func _drive_home() -> void:
	await C.player.walk_to_clicked()
	if not _done():
		await C.Mama.say("Ještě chvilku a jedeme domů.")
		return
	await fade(func(): pass, "Cestou domů…")
	R.goto_room("Ves12")
