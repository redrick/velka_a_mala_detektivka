@tool
extends "res://game/shared/story_room.gd"
## Story 2, the attic. Dark: Hanka's torch finds the chest, děda's key opens it (the club
## flashback, half a map, Věrka's riddle), then the torch finds the owls on the beam. Next
## morning the club mirrors throw the sun's star on the floor (minigame), Hanka counts seven
## planks, and only she fits under the low roof where the seventh plank sings.

const Data := preload('room_puda_state.gd')
const DARK := Color(0.12, 0.12, 0.2)
const COUNT := ["Jedna!", "Dvě!", "Tři!", "Čtyři!", "Pět!", "Šest!", "Sedm!"]
const SunbeamGame := preload("res://game/minigames/sunbeam.gd")

var state: Data = load("res://game/rooms/puda/room_puda.tres")
var _beam: Polygon2D


func _on_room_entered() -> void:
	C.player.position = get_marker_position("Vstup")
	Globals.bring_sister(self, Vector2(170, 10))
	place("Deda", Vector2(1040, 930))
	if Globals.k_chest:
		get_prop("Truhla").texture = load("res://assets/props/chest_open.png")
	get_prop("Sovy").visible = Globals.k_owls
	get_prop("Svetlo").visible = Globals.k_sunbeam
	get_prop("Plechovka").hide()
	Globals.exit_arrow(self, "Dolu", true)
	_planks_active(Globals.k_sunbeam and not Globals.k_map)
	if Globals.k_owls:
		_morning_light()
	else:
		dark(DARK)
		glow(Vector2(384, 410), Color(1.0, 0.9, 0.6), 0.7, 1.5)


func _on_room_transition_finished() -> void:
	if Globals.phase == "k_attic":
		Globals.phase = ""
		await C.Alica.say("Tady je tma jako v pytli!")
		if C.player == C.Hanka:
			await C.Hanka.say("Posvítím baterkou!")
		else:
			await C.Hanka.say("Klikni na mě, já mám baterku!")
	elif Globals.k_owls and not Globals.k_sunbeam:
		await C.Alica.say("Sluníčko svítí okýnkem! Klikni na okýnko.")


func on_click(node: Node) -> void:
	var n: String = node.script_name
	if n.begins_with("Prkno"):
		await _plank(int(n.substr(5)))
		return
	match n:
		"Truhla": await _chest_click()
		"Tram": await _beam_click()
		"Okynko":
			await C.player.walk_to_clicked()
			await C.player.face_clicked()
			if Globals.k_owls and not Globals.k_sunbeam:
				await _mirrors()
			else:
				await on_look(node)
		"Sovy": await C.player.say("Pst, sovičky spinkají.")
		"Svetlo": await C.player.say("Hvězdička ze sluníčka!")
		"Dolu":
			await C.player.walk_to_clicked()
			R.goto_room("Stit")
		_: await super(node)


func on_look(node: Node) -> void:
	match node.script_name:
		"Okynko": await C.player.say("Okýnko s hvězdičkou.")
		"Tram": await C.player.say("Starý trám pod střechou.")
		"Truhla": await C.player.say("Stará truhla se hvězdičkou na zámku.")
		_: await super(node)


func on_item(node: Node, item: PopochiuInventoryItem) -> void:
	if node.script_name == "Truhla" and item == I.Klic:
		await _open_chest()
	else:
		await super(node, item)


func on_character(chr: PopochiuCharacter, action: String, _item: PopochiuInventoryItem = null) -> bool:
	if chr != C.Deda or action == "look":
		return false
	if not Globals.k_chest:
		await C.Deda.say("Tady někde byla moje truhla…")
	elif not Globals.k_owls:
		await C.Deda.say("Slyšíte? Nahoře na trámu něco je.")
	elif not Globals.k_sunbeam:
		await C.Deda.say("Kam ráno svítí hvězdička… Podívejte se k okýnku.")
	else:
		await C.Deda.say("Od hvězdičky sedm prken. Počítejte!")
	return true


#region The chest and the owls ###################################################################
func _chest_click() -> void:
	if Globals.k_chest:
		await C.player.say("Truhla je prázdná. Všechno máme.")
		return
	if is_dark() and C.player != C.Hanka:
		await C.Alica.say("Nic nevidím. Hanka má baterku!")
		return
	await C.player.walk_to_clicked(Vector2(160, 40))
	await C.player.face_clicked()
	C.Hanka.pose("point")
	await C.Hanka.say("Tam! Truhla se hvězdičkou!")
	C.Hanka.pose("torch")
	await C.Alica.say("Je zamčená. Ale my máme klíč!")


func _open_chest() -> void:
	await C.player.walk_to_clicked(Vector2(160, 40))
	sfx("CVAK!", get_prop("Truhla").position + Vector2(-60, -200))
	get_prop("Truhla").texture = load("res://assets/props/chest_open.png")
	I.Klic.remove()
	await C.Deda.say("Tohle je zápisník našeho klubu. Klub Hvězdička!")
	await C.Deda.say("Založili jsme ho tady na půdě, když jsem byl malý kluk…")
	await slideshow([
		["fb_club", "Deda", "Já a moji nejlepší kamarádi, Franta a Věrka."],
		["fb_attic", "Deda", "Každý večer jsme se tu scházeli. Naše znamení byla hvězdička."],
		["", "Deda", "A z trámu se na nás dívala sova."],
		["fb_pond", "Deda", "Jednou jsme u starého rybníka zakopali náš největší poklad."],
		["fb_map", "Deda", "Nakreslil jsem mapu a roztrhli jsme ji napůl. Poklad smí hledat jen celý klub!"],
		["fb_goodbye", "Deda", "Pak se Věrka odstěhovala daleko do města. Svou půlku schovala a nechala mi hádanku."],
		["fb_key", "Deda", "Nikdy jsem ji nenašel. Tak jsem truhlu zamkl a klíč schoval do staré boty."],
	])
	await I.Pulmapa.add()
	await C.Alica.say("V truhle je půlka mapy!")
	await C.Hanka.say("Dědo, nebuď smutný. My tu druhou půlku najdeme!")
	await C.Alica.say("Na poslední stránce zápisníku je hádanka.")
	await paper(["Moje půlka spí tam,", "kam ráno svítí hvězdička.", "Od hvězdičky sedm prken,",
			"pod prknem, které zpívá."], "Hádanka od Věrky:")
	await C.Deda.say("Tu hádanku jsem nikdy nerozluštil.")
	await C.Alica.say("Kam svítí hvězdička? Hvězdy přece svítí v noci…")
	Globals.k_chest = true
	sfx("ŠŠŠŠ!", Vector2(1150, 60))
	await get_tree().create_timer(0.6).timeout
	sfx("CHRRR!", Vector2(900, 90), 70)
	await C.Alica.say("Zase ty zvuky! Nahoře na trámu!")


func _beam_click() -> void:
	if not Globals.k_chest or Globals.k_owls:
		await C.player.say("Starý trám pod střechou." if not Globals.k_owls else "Pst, sovičky spinkají.")
		return
	if C.player != C.Hanka:
		await C.Alica.say("Hanko, posviť tam!")
		return
	C.Hanka.pose("torch")
	await pop("Sovy")
	await C.Alica.say("Na trámu sedí sova pálená. A v košíku má tři malé sovičky!")
	await C.Deda.say("Malé sovičky syčí a chrápou, když mají hlad.")
	C.Hanka.pose("grin")
	await C.Hanka.say("Tak to vy jste dělaly ty zvuky!")
	C.Hanka.pose()
	await C.Deda.say("Sova pálená loví v noci myši a létá úplně potichu.")
	await C.Deda.say("Sovy jsou vzácné. Necháme je tu v klidu bydlet.")
	await C.Alica.say("Kam ráno svítí hvězdička… Dědo, přijdeme se podívat ráno!")
	await fade(_to_morning, "Druhý den ráno…")
	await C.Alica.say("Sluníčko svítí okýnkem!")
	await C.Hanka.say("Ale světlo padá na stará zrcátka.")
	await C.Deda.say("To jsou zrcátka z našeho klubu! Natočte je.")
	await _mirrors()


func _to_morning() -> void:
	Globals.k_owls = true
	light_up(0.1)
	_morning_light()
	get_prop("Sovy").show()
#endregion


#region Morning: the star of light and the planks ###############################################
func _morning_light() -> void:
	glow(Vector2(384, 410), Color(1.0, 0.9, 0.55), 1.4, 3.0)
	_beam = Polygon2D.new()
	_beam.polygon = PackedVector2Array([Vector2(350, 390), Vector2(420, 430), Vector2(640, 975), Vector2(440, 975)])
	_beam.color = Color(1.0, 0.93, 0.55, 0.32)
	_beam.z_index = 2
	_beam.visible = Globals.k_sunbeam
	add_child(_beam)


func _mirrors() -> void:
	var mg: CanvasLayer = SunbeamGame.new()
	add_child(mg)
	await mg.finished
	Globals.k_sunbeam = true
	_beam.show()
	await pop("Svetlo")
	C.Hanka.pose("point")
	await C.Hanka.say("Alico! Hvězdička svítí na zem!")
	C.Hanka.pose()
	C.Alica.pose("grin")
	await C.Alica.say("Kam ráno svítí hvězdička! To je z hádanky!")
	C.Alica.pose()
	await C.Alica.say("Od hvězdičky sedm prken. Klikej na prkna a počítej!")
	_planks_active(true)


func _planks_active(on: bool) -> void:
	for i in range(1, 8):
		get_hotspot("Prkno%d" % i).clickable = on


func _plank(i: int) -> void:
	if Globals.k_map:
		await C.player.say("Tady byla Věrčina půlka mapy.")
		return
	if i != Globals.k_planks + 1:
		Globals.k_planks = 0
		await C.Hanka.say("Hm… Počítá se od hvězdičky. Znovu!")
		return
	var spot := get_hotspot("Prkno%d" % i).walk_to_point
	sfx(tr(COUNT[i - 1]), Vector2(538 + 154 * i - 70, 780), 64)
	Globals.k_planks = i
	if i < 7:
		await C.Hanka.say(COUNT[i - 1])
		return
	await C.Alica.say("Sedmé prkno je až vzadu pod střechou.")
	await C.Deda.say("Tam se nevejdu.")
	await C.Alica.say("Já taky ne.")
	if C.player != C.Hanka:
		Globals.switch_to(C.Hanka)
	C.Hanka.pose("grin")
	await C.Hanka.say("Ale já jo! Jsem malá detektivka!")
	C.Hanka.pose()
	var home := C.Hanka.position
	C.Hanka.ignore_walkable_areas = true
	await C.Hanka.walk(Vector2(spot.x if spot.x > 1500 else 1616, 1000))
	sfx("VRZ!", Vector2(1540, 820), 70)
	await C.Hanka.say("Tohle prkno zpívá!")
	await pop("Plechovka")
	C.Hanka.pose("grin")
	await C.Hanka.say("Mám to! Plechovka se hvězdičkou!")
	C.Hanka.pose()
	get_prop("Plechovka").hide()
	await C.Hanka.walk(home)
	C.Hanka.ignore_walkable_areas = false
	I.Pulmapa.remove()
	await I.Mapa.add()
	await C.Deda.say("Věrčina půlka mapy! Po tolika letech!")
	await C.Hanka.say("Alica četla hádanku a já hledala!")
	await C.Alica.say("Obě půlky do sebe přesně zapadly. Je to mapa ke starému rybníku!")
	await C.Deda.say("Klub Hvězdička je zpátky! A vy dvě jste jeho nové členky.")
	Globals.k_map = true
	_planks_active(false)
	Globals.phase = "k_ending"
	R.goto_room("Stit")
#endregion
