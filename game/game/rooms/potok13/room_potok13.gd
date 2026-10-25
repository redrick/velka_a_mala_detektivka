@tool
extends "res://game/shared/story_room.gd"
## Story 13, the creek by the camp: the stepping stones and Bětka's measuring rock (less of it shows each day),
## the mud bank. Day 2: Franta fishing ("to bude vydra"), drawing 2, the big webbed prints, the night stake-out
## (eyes, PLESK). Day 3: another stump, drawing 3, "Kámen v potoce", "Kdo kácí vrby?", then upstream.

const Data := preload('room_potok13_state.gd')
const RockGame := preload("res://game/minigames/rock.gd")
const WhoGame := preload("res://game/minigames/who_13.gd")
const NIGHT := Color(0.2, 0.22, 0.4)

var state: Data = load("res://game/rooms/potok13/room_potok13.tres")


func _night() -> bool:
	return Globals.b_tracks and not Globals.b_night2


func _level() -> int:
	if Globals.b_night2: return 2
	if Globals.b_cuts: return 1
	return 0


func _on_room_entered() -> void:
	match C.player.last_room:
		"Hraz13": C.player.position = get_hotspot("Hraz").walk_to_point + Vector2(-80, 40)
		_: C.player.position = get_marker_position("Start")
	Globals.bring_sister(self, Vector2(170, 10))
	place("Joey", joey_spot())
	if _night():
		remove("Betka"); remove("Rybar")
	else:
		place("Betka", get_marker_position("Betka"))
		if Globals.b_cuts and not Globals.b_night2:
			place("Rybar", get_marker_position("Franta"))
		else:
			remove("Rybar")
	if Globals.b_day >= 2:
		place("Tonda", get_marker_position("Tonda"))
	else:
		remove("Tonda")
	_stones()
	get_prop("Vydra").visible = Globals.b_franta
	get_prop("Stopy").visible = Globals.b_franta and Globals.b_rock2
	get_prop("Pahyl").visible = Globals.b_night2
	get_prop("Oci").visible = _night()
	hidden_thing(null, "Zaba", "b_frogs", 10, "")
	Globals.exit_arrow(self, "Louka", true, not _night())
	Globals.exit_arrow(self, "Hraz", false, Globals.b_who)
	if _night():
		dark(NIGHT)


func _stones() -> void:
	var p := get_prop("Kameny")
	p.texture = load("res://assets/props/stones13_%d.png" % _level())
	p.get_node("Sprite2D").texture = p.texture


func _on_room_transition_finished() -> void:
	if _night() and C.player != C.Hanka:
		await hand_over(C.Hanka, "Hani, ty hlídáš s baterkou. Posviť na vodu.")
	else:
		await _who()


func joey_goal() -> Vector2:
	if not Globals.b_rock1: return get_marker_position("Betka") + Vector2(-240, 20)
	if not Globals.b_evening: return get_hotspot("Louka").walk_to_point
	if not Globals.b_cuts: return get_hotspot("Louka").walk_to_point
	if not Globals.b_franta: return get_marker_position("Franta") + Vector2(-260, 20)
	if not Globals.b_rock2: return get_marker_position("Betka") + Vector2(-240, 20)
	if not Globals.b_tracks: return get_prop("Stopy").position + Vector2(-300, 60)
	if _night(): return get_prop("Oci").position + Vector2(0, 220)
	if not Globals.b_stump2: return get_prop("Pahyl").position + Vector2(220, 60)
	if not Globals.b_rock: return get_marker_position("Betka") + Vector2(-240, 20)
	return get_hotspot("Hraz").walk_to_point


func on_click(node: Node) -> void:
	if await hidden_thing(node, "Zaba", "b_frogs", 10, "Žabka"):
		return
	match node.script_name:
		"Kameny": await _stones_click()
		"Voda": await _water()
		"Oci": await _eyes()
		"Stopy": await _tracks()
		"Vydra":
			await C.player.walk(get_prop("Vydra").position + Vector2(-220, -60))
			await C.player.say("Vydra má malou kulatou stopu. Pět prstů a žádná blána.")
		"Pahyl": await _stump()
		"Louka":
			await C.player.walk_to_clicked()
			if _night():
				await C.player.say("Teď hlídáme. Nikam nejdu.")
				return
			R.goto_room("Louka13")
		"Hraz":
			await C.player.walk_to_clicked()
			if not Globals.b_who:
				await C.player.say("Proti proudu. Nejdřív musíme zjistit, kdo to byl.")
				return
			R.goto_room("Hraz13")
		_: await super(node)


func on_character(chr: PopochiuCharacter, action: String, _item: PopochiuInventoryItem = null) -> bool:
	if action == "look" or chr == C.Alica or chr == C.Hanka or chr == C.Joey:
		return false
	await C.player.walk(chr.position + Vector2(-240, 20))
	match chr.script_name:
		"Betka": await _betka()
		"Rybar": await _franta()
		"Tonda":
			if Globals.b_tracks:
				await C.Tonda.say("Já jsem se vůbec nebál. Skoro.")
			else:
				await C.Tonda.say("Byl to vlkodlak! Určitě!")
		_: return false
	return true


#region Bětka's drawings ##########################################################################
func _betka() -> void:
	if not Globals.b_rock1:
		await C.Alica.say("Co kreslíš?")
		C.Betka.pose("sketch")
		await C.Betka.say("Ten velký kámen v potoce. Každý den jeden obrázek!")
		C.Betka.pose()
		Globals.b_rock1 = true
		await C.Alica.say("Hezký. Půjdeme k ohni, Bětko?")
		return
	if Globals.b_cuts and not Globals.b_rock2:
		C.Betka.pose("sketch")
		await C.Betka.say("Druhý obrázek. Můj kámen se zmenšil!")
		C.Betka.pose()
		await C.Alica.say("Ne. Voda je vyšší!")
		await C.Hanka.say("Kameny přes potok jsou napůl pod vodou.")
		Globals.b_rock2 = true
		await _tracks_appear()
		return
	if Globals.b_stump2 and not Globals.b_rock:
		await _drawings()
		return
	if Globals.b_night2 and not Globals.b_stump2:
		await C.Betka.say("Ráno nakreslím třetí obrázek. Ale nejdřív se podívej na ten pahýl!")
		return
	await C.Betka.say("Kreslím každý den jeden obrázek. Tak poznám, co se děje.")


func _drawings() -> void:
	C.Betka.pose("sketch")
	await C.Betka.say("Třetí obrázek. Kámen skoro zmizel!")
	C.Betka.pose("worried")
	sfx("FŮŮ!", C.Betka.position + Vector2(0, -400), 70)
	await C.Betka.say("Ojej! Vítr mi vyfoukl obrázky ze skicáku!")
	await C.Alica.say("Pomůžeme ti je srovnat.")
	var mg: CanvasLayer = RockGame.new()
	add_child(mg)
	await mg.finished
	C.Betka.pose()
	Globals.b_rock = true
	await C.Alica.say("Voda stoupá každý den. Někdo ten potok hradí!")
	await _who()


func _tracks_appear() -> void:
	if Globals.b_franta and Globals.b_rock2 and not get_prop("Stopy").visible:
		await pop("Stopy")
		await C.Hanka.say("Tam u vody je bláto. A v něm něco je!")
#endregion


#region Day 2 #####################################################################################
func _stones_click() -> void:
	await C.player.walk(Vector2(1000, 850))
	match _level():
		0:
			await C.Alica.say("Přes potok vedou kameny. Za ním je studánka.")
			await C.Alica.say("Pojď, Joey! Je to jen voda!")
			await C.Joey.say("Kňuk.")
			await C.Hanka.say("Joeymu se do vody nechce.")
		1: await C.player.say("Kameny jsou napůl pod vodou! Včera byly suché.")
		_: await C.player.say("Kameny jsou skoro celé pod vodou.")


func _water() -> void:
	await C.player.walk_to_clicked()
	if _night():
		await _eyes()
	elif Globals.b_night2:
		await C.player.say("Voda je zase o kousek výš.")
	else:
		await C.player.say("Potok. Studená a čistá voda.")


func _franta() -> void:
	if Globals.b_franta:
		await C.Rybar.say("Ryby pořád neberou. Ta vydra!")
		return
	await C.Alica.say("Dobrý den, pane Franto! Chytá to?")
	await C.Rybar.say("Nic. Ryby mi asi žere vydra.")
	await C.Rybar.say("Ukážu vám, jakou má stopu.")
	await pop("Vydra")
	await C.Alica.say("Vydra má malou kulatou stopu. Pět prstů.")
	Globals.b_franta = true
	await _tracks_appear()


func _tracks() -> void:
	await C.player.walk(get_prop("Stopy").position + Vector2(-300, 60))
	if Globals.b_tracks:
		await C.player.say("Obrovské stopy s blánou. A mezi nimi šmouha.")
		return
	await C.Alica.say("Stopy! A obrovské!")
	await C.Tonda.say("Vlkodlak!!!")
	C.Alica.pose("lens")
	await C.Alica.say("Prsty mají spojené blánou. Jako kachna. A mezi stopami je šmouha, jako by se něco táhlo.")
	C.Alica.pose()
	await C.Alica.say("To není vydra! Vydra má malé tlapky.")
	await C.Alica.say("Je to něco velkého. A plave to.")
	await C.Alica.say("Dnes v noci budeme u potoka hlídat!")
	Globals.b_tracks = true
	await fade(_night_set, "Noc…")
	await C.Tonda.say("Nikdo neusne!")
	await hand_over(C.Hanka, "Hani, ty hlídáš s baterkou. Posviť na vodu.")
	await C.Hanka.say("Já svítím!")


func _night_set() -> void:
	remove("Betka"); remove("Rybar")
	get_prop("Oci").show()
	dark(NIGHT)
	Globals.show_exit(self, "Louka", false)


func _eyes() -> void:
	if C.player != C.Hanka:
		await hand_over(C.Hanka, "Hani, posviť tam baterkou.")
	await C.Hanka.walk(Vector2(get_prop("Oci").position.x - 120, 880))
	await C.Hanka.say("Oči! Tam ve vodě!")
	await C.Tonda.say("Co? Kde? Vlkodlak?")
	sfx("PLESK!", get_prop("Oci").position + Vector2(0, -60))
	get_prop("Oci").hide()
	await C.Alica.say("Psst! Už je pryč. Uplaval.")
	Globals.b_night2 = true
	Globals.b_day = 3
	await fade(_morning, "Ráno…")
	await C.Hanka.say("Alico! U potoka je další pahýl!")


func _morning() -> void:
	light_up(0.1)
	place("Betka", get_marker_position("Betka"))
	get_prop("Pahyl").show()
	_stones()
	Globals.show_exit(self, "Louka", true)
#endregion


#region Day 3 #####################################################################################
func _stump() -> void:
	await C.player.walk(get_prop("Pahyl").position + Vector2(220, 60))
	if Globals.b_stump2:
		await C.player.say("Další pahýl jako tužka. Zuby jsou vidět i bez lupy.")
		await _who()
		return
	await C.Alica.say("Zase! Další vrba.")
	C.Alica.pose("lens")
	await C.Alica.say("Podívám se lupou. Zase dva velké zuby vedle sebe!")
	C.Alica.pose()
	await C.Alica.say("A od pahýlu vede k vodě hladká klouzačka z bláta. Tudy se táhla vrba.")
	Globals.b_stump2 = true
	if Globals.b_rock:
		await _who()
	else:
		await C.Hanka.say("Bětka kreslí třetí obrázek. Pojď se podívat!")


func _who() -> void:
	if not (Globals.b_rock and Globals.b_stump2) or Globals.b_who:
		return
	await C.Alica.say("STOP, detektive! Máme všechny stopy. Kdo to byl?")
	var mg: CanvasLayer = WhoGame.new()
	add_child(mg)
	await mg.finished
	Globals.b_who = true
	await C.Alica.say("Čmuchej, Joey! Kam ty stopy vedou?")
	await C.Joey.say("Čmuch čmuch!")
	await C.Joey.walk(get_hotspot("Hraz").walk_to_point)
	await C.Hanka.say("Proti proudu! Pojďte za Joeyem!")
	Globals.show_exit(self, "Hraz", true)
#endregion
