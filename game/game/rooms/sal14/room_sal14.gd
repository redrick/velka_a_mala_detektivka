@tool
extends "res://game/shared/story_room.gd"
## Story 14, the vaulted hall where the Klub sleeps: the deep window niche with its sill. Evening: Bětka's ribbon
## and Alica's clip on the sill, Tonda's Rudolf ghost story. Night: rustling outside in the wall, Hanka's torch.
## Morning: the things are gone; on the sill bird prints and a black feather; the kastelánka with her ladder.

const Data := preload('room_sal14_state.gd')
const NIGHT := Color(0.24, 0.24, 0.42)

var state: Data = load("res://game/rooms/sal14/room_sal14.tres")


func _night() -> bool:
	return Globals.h_evening and not Globals.h_night


func _on_room_entered() -> void:
	C.player.position = get_marker_position("Start")
	Globals.bring_sister(self, Vector2(170, 10))
	place("Joey", get_marker_position("Joey"))
	for who in ["Deda", "Verka", "Tonda", "Betka", "Rybar"]:
		place(who, get_marker_position(who))
	if Globals.h_sill and not Globals.h_kastel:
		place("Kastelanka", get_marker_position("Kastelanka"))
	else:
		remove("Kastelanka")
	get_prop("Stuzka").visible = _night()
	get_prop("Stopicky").visible = Globals.h_sill
	hidden_thing(null, "Klicek", "h_found", 10, "")
	Globals.exit_arrow(self, "Dvere", true, not _night())
	if _night():
		dark(NIGHT)


func _on_room_transition_finished() -> void:
	if Globals.h_bears and not Globals.h_evening:
		await _evening()
	elif _night() and C.player != C.Hanka:
		await hand_over(C.Hanka, "Hani, posviť baterkou. Kde to šramotí?")


func joey_goal() -> Vector2:
	if _night() or (Globals.h_night and not Globals.h_sill): return get_hotspot("Okno").walk_to_point
	if Globals.h_sill and not Globals.h_kastel: return get_marker_position("Kastelanka") + Vector2(-240, 0)
	return get_hotspot("Dvere").walk_to_point


func _evening() -> void:
	await C.Betka.say("Stužku si dám na okno.")
	await C.Alica.say("A já sponku s mašlí.")
	await pop("Stuzka")
	await C.Tonda.say("Teď vám povím pověst o strašidle!")
	await C.Tonda.say("Císař Rudolf se strašidla bál. Ale na úzké cestě se vozy nedaly otočit.")
	await C.Tonda.say("Tak tu musel přespat. Jako my!")
	await C.Hanka.say("Já se nebojím.")
	Globals.h_evening = true
	await fade(_night_set, "Noc…")
	sfx("ŠRAMOT…", Vector2(1400, 360), 60)
	await C.Tonda.say("Slyšíte to? Strašidlo!!!")
	await hand_over(C.Hanka, "Hani, posviť baterkou. Kde to šramotí?")


func _night_set() -> void:
	dark(NIGHT)
	Globals.show_exit(self, "Dvere", false)


func on_click(node: Node) -> void:
	if await hidden_thing(node, "Klicek", "h_found", 10, "Klíček"):
		return
	match node.script_name:
		"Okno", "Stuzka", "Stopicky": await _window()
		"Spacaky":
			await C.player.walk_to_clicked()
			await C.player.say("Naše spacáky. Spíme na hradě jako král!")
		"Dvere":
			await C.player.walk_to_clicked()
			if _night():
				await C.player.say("V noci ven nepůjdu. Všichni spí.")
				return
			R.goto_room("Nadvori14")
		_: await super(node)


func on_character(chr: PopochiuCharacter, action: String, _item: PopochiuInventoryItem = null) -> bool:
	if action == "look" or chr == C.Alica or chr == C.Hanka or chr == C.Joey:
		return false
	if _night():
		await C.player.say("Psst. Všichni spí.")
		return true
	await C.player.walk(chr.position + Vector2(-240, 20))
	match chr.script_name:
		"Kastelanka": await _kastelanka()
		"Tonda":
			if Globals.h_kastel:
				await C.Tonda.say("Tak kdo to byl? Strašidlo, nebo holub?")
			elif Globals.h_night:
				await C.Tonda.say("Strašidlo! Říkal jsem to!")
			else:
				await C.Tonda.say("Dneska v noci uvidíme strašidlo!")
		"Betka":
			if Globals.h_night:
				await C.Betka.say("Moje červená stužka… Byla moje nejhezčí.")
			else:
				await C.Betka.say("Na hradě se mi líbí. Je tu tolik věcí na kreslení.")
		"Deda": await C.Deda.say("Na hradě jsem nikdy nespal. Ani s Klubem!")
		"Verka": await C.Verka.say("XIV… Kdybych si jen vzpomněla.")
		"Rybar": await C.Rybar.say("Já bych spal i na rybářské stoličce.")
		_: return false
	return true


func _window() -> void:
	await C.player.walk(get_hotspot("Okno").walk_to_point)
	if _night():
		if C.player != C.Hanka:
			await hand_over(C.Hanka, "Hani, posviť baterkou. Kde to šramotí?")
		await C.Hanka.say("Posvítím na okno…")
		await C.Alica.say("Psst. To šramotí venku ve zdi.")
		await C.Hanka.say("Nikdo tu není.")
		Globals.h_night = true
		await fade(_morning, "Ráno…")
		await C.Betka.say("Moje stužka je pryč!")
		await C.Alica.say("A moje sponka taky!")
		await C.Tonda.say("Strašidlo! Říkal jsem to!")
		await C.Alica.say("Zakládám případ číslo čtrnáct: Kdo krade na hradě?")
		await C.Hanka.say("A taky najdeme poklad!")
		return
	if Globals.h_sill:
		await C.player.say("Ptačí stopičky v prachu a černé pírko. Modře se leskne.")
		return
	if not Globals.h_night:
		await C.player.say("Hluboké okno. Zdi jsou tu hrozně tlusté.")
		return
	C.Alica.pose("lens")
	await C.Alica.say("V prachu na okně jsou stopičky! Tři prstíky dopředu, jeden dozadu.")
	await pop("Stopicky")
	await C.Alica.say("A černé pírko. Modře se leskne.")
	C.Alica.pose()
	await C.Tonda.say("Ptačí stopy. To byl holub!")
	Globals.h_sill = true
	place("Kastelanka", Vector2(1860, 920))
	await C.Kastelanka.walk(get_marker_position("Kastelanka"))
	await C.Tonda.say("Paní kastelánka tu ráno byla. Se žebříkem!")


func _morning() -> void:
	light_up(0.1)
	get_prop("Stuzka").hide()
	Globals.show_exit(self, "Dvere", true)


func _kastelanka() -> void:
	if Globals.h_kastel:
		await C.Kastelanka.say("Pojďte ven na nádvoří, detektivové.")
		return
	await C.Hanka.say("Paní kastelánko, vzala jste nám stužku?")
	await C.Kastelanka.say("Ráno otvírám okenice, Hanko. Stužku jsem neviděla.")
	await C.Alica.say("A holubí pírko je šedé. Tohle je černé.")
	await C.Tonda.say("Takže ani holub, ani paní kastelánka…")
	Globals.h_kastel = true
	await C.Kastelanka.say("Pojďte ven na nádvoří, detektivové.")
	remove("Kastelanka")
