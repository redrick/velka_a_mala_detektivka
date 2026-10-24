@tool
extends "res://game/shared/story_room.gd"
## Story 5, the village road in snow. Day 1: the star prints vanish where the tractor drove; Tonda with
## his sled ("já stavím jenom obry"). Day 2: Tonda is cleared (big boots, blue hat without a pompom, his
## sled leaves long runner tracks) and tells that only Franta grows parsnips. Franta's house.

const Data := preload('room_ves5_state.gd')

var state: Data = load("res://game/rooms/ves5/room_ves5.tres")


func _on_room_entered() -> void:
	match C.player.last_room:
		"Franta5": C.player.position = get_marker_position("ZFranty")
		_: C.player.position = get_marker_position("Start")
	Globals.bring_sister(self, Vector2(170, 10))
	place("Joey", joey_spot())
	if Globals.s_day <= 2:
		place("Tonda", get_marker_position("Tonda"))
	else:
		remove("Tonda")
	Globals.exit_arrow(self, "Zpet", true)


func _on_room_transition_finished() -> void:
	if Globals.s_day == 1 and not Globals.s_road:
		await C.player.say("Stopičky vedou po silnici…")


func joey_goal() -> Vector2:
	if Globals.s_day == 1 and not Globals.s_road:
		return get_hotspot("Koleje").walk_to_point
	if Globals.s_day == 1 and not Globals.s_tonda or Globals.s_day == 2 and not Globals.s_tonda_ok:
		return C.Tonda.position + Vector2(-230, 60)
	if Globals.s_day == 2 and Globals.s_tonda_ok and not (Globals.s_parsnip and Globals.s_boots and Globals.s_curtain):
		return get_hotspot("DumFranta").walk_to_point
	return Vector2(160, 960)


func on_click(node: Node) -> void:
	match node.script_name:
		"Koleje":
			await C.player.walk_to_clicked()
			if Globals.s_day == 1 and not Globals.s_road:
				await C.Alica.say("Tady jel traktor. Stopičky jsou pryč!")
				await C.Hanka.say("Škoda…")
				Globals.s_road = true
				await _day1_done()
			else:
				await C.player.say("Koleje od traktoru.")
		"Sane":
			await C.player.walk_to_clicked()
			await C.player.say("Dlouhé koleje od saní. Na zahradě žádné nebyly.")
		"VelkeStopy":
			await C.player.walk_to_clicked()
			await C.player.say("Velké stopy od bot. Bez hvězdiček.")
		"DumTonda":
			await C.player.walk_to_clicked()
			await C.player.say("Tondův dům.")
		"DumFranta":
			await C.player.walk_to_clicked()
			if Globals.s_tonda_ok:
				R.goto_room("Franta5")
			else:
				await C.player.say("Tady bydlí pan Franta. Z komína se kouří.")
		"Zpet":
			await C.player.walk_to_clicked()
			R.goto_room("Zahrada5")
		_: await super(node)


func on_character(chr: PopochiuCharacter, action: String, _item: PopochiuInventoryItem = null) -> bool:
	if chr.script_name != "Tonda" or action == "look":
		return false
	await C.player.walk(chr.position + Vector2(-240, 30))
	await C.player.face_clicked()
	if Globals.s_day == 1:
		if Globals.s_tonda:
			await C.Tonda.say("Dneska postavím největšího sněhuláka ve vsi!")
			return true
		await C.Alica.say("Tondo, nestavěl jsi v noci sněhuláka u nás na zahradě?")
		await C.Tonda.say("Já? Já stavím jenom obry! Malí sněhuláci jsou pro mimina.")
		await C.Alica.say("Hm… Podezřelý číslo jedna.")
		Globals.s_tonda = true
		await _day1_done()
	elif not Globals.s_tonda_ok:
		await C.Alica.say("Tondo, ukaž nám boty. A čepici.")
		await C.Tonda.say("Prosím. Velké boty po bráchovi. A modrá čepice. Bez bambule.")
		await C.Hanka.say("Velké stopy. Bez hvězdiček.")
		await C.Tonda.say("A když jedu na saních, jsou za mnou dlouhé koleje.")
		await C.Alica.say("Na zahradě žádné koleje nebyly. Tak jsi to nebyl ty. Škrtám!")
		await C.Alica.say("Ale ten bílý nos… Nevíš, co je to za zeleninu?")
		await C.Tonda.say("Bílá mrkev? To je pastinák! Ten tu pěstuje jenom pan Franta.")
		Globals.s_tonda_ok = true
		await C.Hanka.say("Půjdeme k Frantovi!")
	else:
		await C.Tonda.say("Pastinák pěstuje jenom pan Franta. Jeho dům je tamhle.")
	return true


func _day1_done() -> void:
	if Globals.s_day == 1 and Globals.s_road and Globals.s_tonda:
		await C.Alica.say("Stopy jsou pryč. Dneska v noci budeme hlídat u okna. Chytíme ho!")
