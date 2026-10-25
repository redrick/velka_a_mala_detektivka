@tool
extends "res://game/shared/story_room.gd"
## Story 8, the forest edge: the krmelec (hay only) and the hajný's track guide; "make a clean page" sends
## everyone home for the night. After the trail game: Hanka finds the deer's bed under the low spruce,
## Joey meets the deer nose to nose, Alica's loud fact scares her off; hay into both racks evenly ("Seno do
## krmelce"), food for the krmelec, pinecone noses.

const Data := preload('room_les8_state.gd')
const ScaleGame := preload("res://game/minigames/scale.gd")

var state: Data = load("res://game/rooms/les8/room_les8.tres")


func _on_room_entered() -> void:
	C.player.position = get_marker_position("Start")
	Globals.bring_sister(self, Vector2(170, 10))
	place("Joey", joey_spot())
	if not Globals.n_guide or Globals.n_trail:
		place("Hajny", get_marker_position("Hajny"))
	else:
		remove("Hajny")
	if Globals.n_trail:
		place("Betka", Vector2(700, 960))
	else:
		remove("Betka")
	get_prop("Loze").visible = Globals.n_bed
	get_prop("Srnka").visible = false
	get_prop("Jidlo").visible = false
	Globals.exit_arrow(self, "Zpet", true)


func _on_room_transition_finished() -> void:
	if Globals.phase == "n_follow":
		Globals.phase = ""
		await C.Alica.say("Stopy vedou k tomu nízkému smrčku. Pomalu a potichu!")
	elif not Globals.n_guide:
		await _guide()
	elif Globals.n_bed and not Globals.n_scale:
		await _feed()


func joey_goal() -> Vector2:
	if Globals.n_trail and not Globals.n_bed:
		return get_hotspot("Smrcek").walk_to_point
	return get_hotspot("Zpet").walk_to_point


func _guide() -> void:
	await C.Hajny.say("Tady je můj krmelec. Teď je v něm jen seno.")
	await C.Hajny.say("A tady máte všechny stopy pohromadě. Zapamatujte si je.")
	await picture("res://assets/slides/track_guide.png", "Stopy ve sněhu")
	await C.Alica.say("Ale u sněhuláků je všechno pošlapané. Nepoznáme to.")
	await C.Hajny.say("Tak si udělejte čistou stránku. Uhlaďte večer sníh. Ráno si to přečtete.")
	Globals.n_guide = true
	await C.Alica.say("Domů! Dneska večer připravíme past. Čistý sníh a nové nosy.")


func on_click(node: Node) -> void:
	match node.script_name:
		"Krmelec":
			await C.player.walk_to_clicked()
			await C.player.say("Krmelec. Je v něm jen seno." if not Globals.n_bed else "Teď je v krmelci mrkev, jablka a řepa.")
		"Smrcek": await _spruce()
		"Srnka", "Loze":
			await C.player.walk_to_clicked()
			await C.player.say("Srnčí lože. Tady spí.")
		"Zpet":
			await C.player.walk_to_clicked()
			if Globals.n_guide and not Globals.n_trail and Globals.n_day == 1:
				Globals.phase = "n_evening"
				R.goto_room("Kuchyne8")
			else:
				R.goto_room("Louka8")
		_: await super(node)


func on_character(chr: PopochiuCharacter, action: String, _item: PopochiuInventoryItem = null) -> bool:
	if action == "look" or chr == C.Alica or chr == C.Hanka or chr == C.Joey:
		return false
	await C.player.walk(chr.position + Vector2(-240, 20))
	match chr.script_name:
		"Hajny": await C.Hajny.say("Přečtěte si to sami, detektivky." if not Globals.n_trail else "Zvířata se bojí. Nechte je v klidu.")
		"Betka": await C.Betka.say("Nesu pastináky. Ale tentokrát pro srnku do krmelce.")
		_: return false
	return true


func _spruce() -> void:
	await C.player.walk(get_hotspot("Smrcek").walk_to_point)
	if not Globals.n_trail:
		await C.player.say("Nízký smrček. Větve až do sněhu.")
		return
	if Globals.n_bed:
		if Globals.n_scale:
			await C.player.say("Srnčí lože pod smrčkem.")
		else:
			await _feed()
		return
	await hand_over(C.Hanka, "Pod větvemi je jako jeskyně. Hani, ty se tam vejdeš!")
	await C.Hanka.say("Lezu pod větve… Tady je ve sněhu vyhřátý ovál! Tady srnka spí!")
	await pop("Loze")
	Globals.n_bed = true
	await pop("Srnka")
	await C.Joey.walk(get_prop("Srnka").position + Vector2(-260, 160))
	await C.Hanka.say("Joey a srnka! Čuchají si nosíky!")
	await C.Alica.say("Srnka má vzadu bílé zrcátko! Když se lekne, ukáže ho!")
	sfx("HOP!", Vector2(1600, 460), 80)
	var s := get_prop("Srnka")
	var tw := create_tween()
	tw.tween_property(s, "position", s.position + Vector2(700, -100), 0.8)
	await tw.finished
	s.hide()
	await C.Alica.say("…Ukázala. Promiň, srnko.")
	await _feed()


func _feed() -> void:
	await C.Hajny.say("V hlubokém sněhu mají zvířata hlad. Proto přišla na vaše nosy.")
	await C.Betka.say("Tak jí dáme jídlo do krmelce. A sněhuláci dostanou nosy ze šišek!")
	await C.Hajny.say("Nejdřív seno. Do obou jeslí stejně, ať se srnky nestrkají.")
	await C.Hajny.say("Na cedulkách je, kolik který otýpek váží.")
	var mg: CanvasLayer = ScaleGame.new()
	add_child(mg)
	await mg.finished
	Globals.n_scale = true
	await pop("Jidlo")
	await C.Hanka.say("Mrkev, pastinák, jablíčka a řepa. Pro srnku!")
	await C.Hajny.say("A šišky srnka nejí. Výborně, detektivky.")
	await the_end("Konec 8. dílu")
