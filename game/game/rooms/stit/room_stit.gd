@tool
extends "res://game/shared/story_room.gd"
## Story 2, the garden under the attic window. Hanka finds the white feather low in the grass,
## Alica looks at the grey pellets with the magnifier, the attic window has the same star as the
## key. Showing děda the key makes him put up the ladder. At the end the owl box goes up here.

const Data := preload('room_stit_state.gd')

var state: Data = load("res://game/rooms/stit/room_stit.tres")


func _on_room_entered() -> void:
	match C.player.last_room:
		"Puda": C.player.position = get_marker_position("ZPudy")
		_: C.player.position = get_marker_position("ZeKuchyne")
	if Globals.phase == "k_ending":
		C.player.position = get_marker_position("Konec")
	Globals.bring_sister(self, Vector2(-170, 10))
	place("Joey", Vector2(380, 990))
	if Globals.k_breakfast:
		place("Deda", Vector2(760, 880))
	Globals.exit_arrow(self, "Domu", true)
	get_prop("Pirko").visible = not Globals.k_feather
	get_prop("Zebrik").visible = Globals.k_ladder and not Globals.k_map
	_show_box()


func _on_room_transition_finished() -> void:
	if Globals.phase == "k_ending":
		await _ending()
	elif C.player.last_room == "Snidane" and not Globals.k_feather:
		await C.Alica.say("Tady nahoře je okýnko na půdu. Hledejte stopy!")


func joey_goal() -> Vector2:
	if not Globals.k_feather:
		return get_prop("Pirko").position + Vector2(-140, 40)
	if not Globals.k_pellets:
		return get_prop("Vyvrzky").position + Vector2(-160, 20)
	if not Globals.k_window:
		return get_hotspot("Okynko").walk_to_point + Vector2(-120, 60)
	if not Globals.k_ladder:
		return C.Deda.position + Vector2(160, 60)
	return get_marker_position("ZPudy") + Vector2(-160, 40)


func on_click(node: Node) -> void:
	match node.script_name:
		"Pirko":
			await _feather()
		"Vyvrzky":
			await _pellets()
		"Okynko":
			await C.player.walk_to_clicked()
			await C.player.face_clicked()
			await _window()
		"Domu":
			await C.player.walk_to_clicked()
			R.goto_room("Snidane")
		"Zebrik":
			await C.player.walk_to_clicked()
			Globals.phase = "k_attic" if not Globals.k_chest else ""
			R.goto_room("Puda")
		"Hrebik1", "Hrebik2", "Hrebik3":
			await _nail(node)
		"Budka":
			await C.player.say("Budka pro sovičky.")
		_:
			await super(node)


func on_look(node: Node) -> void:
	match node.script_name:
		"Okynko": await C.player.say("Kulaté okýnko na půdu. Má hvězdičku!" if Globals.k_window else "Kulaté okýnko na půdu.")
		"Pirko": await C.player.say("Něco bílého v trávě.")
		"Vyvrzky": await C.player.say("Divné šedé kuličky.")
		"Zebrik": await C.player.say("Žebřík na půdu.")
		_: await super(node)


func on_item(node: Node, item: PopochiuInventoryItem) -> void:
	if node.script_name == "Vyvrzky" and item == I.Lupa:
		await _pellets()
	elif node.script_name == "Okynko" and item == I.Klic:
		await _window()
	else:
		await super(node, item)


func on_character(chr: PopochiuCharacter, action: String, item: PopochiuInventoryItem = null) -> bool:
	if chr != C.Deda:
		return false
	if action == "look":
		await C.player.say("To je náš děda.")
		return true
	await C.player.walk_to_clicked(Vector2(-220, 0))
	await C.player.face_clicked()
	if action == "item" and item == I.Klic:
		await _show_key()
	elif Globals.phase == "k_nails":
		await C.Deda.say("Zatlučte tři hřebíky. Ťuk, ťuk, ťuk!")
	elif Globals.k_ladder:
		await C.Deda.say("Žebřík stojí. Tak nahoru, ale potichu!")
	elif Globals.k_window:
		await C.Deda.say("Copak to máte, detektivky?")
		await C.Alica.say("Ukážeme dědovi klíč s hvězdičkou!")
	else:
		await C.Deda.say("Na půdu se nechodí. Jsou tam jen staré krámy…")
	return true


func _feather() -> void:
	if C.player != C.Hanka:
		await C.Alica.say("Něco tam leží v trávě… Hanka je blíž u země. Klikni na Hanku!")
		return
	await C.player.walk_to_clicked(Vector2(-120, 20))
	await C.player.face_clicked()
	C.Hanka.pose("point")
	await C.Hanka.say("Alico! Tady je bílé peříčko!")
	C.Hanka.pose()
	get_prop("Pirko").hide()
	Globals.k_feather = true
	await C.Alica.say("Stopa číslo jedna: bílé peříčko.")


func _pellets() -> void:
	if Globals.k_pellets:
		await C.player.say("Vývržky. Vyplivují je sovy.")
		return
	await C.player.walk_to_clicked(Vector2(-150, 20))
	await C.player.face_clicked()
	if C.player != C.Alica:
		await C.Hanka.say("Divné šedé kuličky. Alica má lupu, klikni na Alicu!")
		return
	C.Alica.pose("lens")
	await C.Alica.say("Jsou chlupaté… a jsou v nich malinké kostičky!")
	C.Alica.pose()
	await C.Alica.say("To jsou vývržky! Vyplivují je sovy. Učili jsme se to ve škole.")
	C.Hanka.pose("surprised")
	await C.Hanka.say("Sova? Na naší půdě?")
	C.Hanka.pose()
	Globals.k_pellets = true


func _window() -> void:
	if not (Globals.k_feather and Globals.k_pellets):
		await C.player.say("Kulaté okýnko na půdu. Nejdřív najdeme stopy.")
		return
	if not Globals.k_window:
		C.Alica.pose("point")
		await C.Alica.say("Okýnko má hvězdičku… a klíč taky!")
		C.Alica.pose()
		await C.Hanka.say("Ukážeme ho dědovi!")
		Globals.k_window = true
	else:
		await C.player.say("Stejná hvězdička jako na klíči.")


func _show_key() -> void:
	if Globals.k_ladder:
		await C.Deda.say("Klíč si nech, Alico. Bude se hodit.")
		return
	C.Alica.pose("grin")
	await C.Alica.say("Dědo! Tenhle klíč jsme našly ve staré botě v kůlně.")
	C.Alica.pose()
	await C.Deda.say("To je přece… můj starý klíč od truhly!")
	await C.Deda.say("Tak dobře. Půjdeme nahoru spolu. A potichu!")
	await C.Deda.walk(get_prop("Zebrik").position + Vector2(-180, 380))
	await pop("Zebrik")
	await C.Deda.say("Žebřík stojí. Hanka půjde první, má baterku.")
	Globals.k_ladder = true


func _show_box() -> void:
	var building := Globals.phase == "k_nails"
	get_prop("Budka").visible = building or Globals.game_finished
	for i in range(1, 4):
		get_prop("Hrebik%d" % i).visible = building and i > Globals.k_nails


func _ending() -> void:
	place("Babicka", Vector2(1480, 900))
	C.Deda.position = Vector2(1320, 880)
	await C.Deda.say("Odpoledne vyrobíme budku pro sovy, ať tu můžou bydlet napořád.")
	await pop("Budka")
	Globals.phase = "k_nails"
	Globals.k_nails = 0
	for i in range(1, 4):
		get_prop("Hrebik%d" % i).show()
	await C.Deda.say("Zatlučte tři hřebíky. Ťuk, ťuk, ťuk!")


func _nail(node: Node) -> void:
	if Globals.phase != "k_nails" or not node.visible:
		return
	await C.player.face_clicked()
	var tw := create_tween()
	tw.tween_property(node, "position:y", node.position.y + 20.0, 0.12)
	await tw.finished
	sfx("ŤUK!", node.position + Vector2(-40, -120), 60)
	node.hide()
	Globals.k_nails += 1
	if Globals.k_nails == 3:
		await C.Deda.say("Hotovo! Budka pro sovy.")
		await C.Babicka.say("Detektivky si zaslouží kakao!")
		await C.Hanka.say("Dobrou noc, sovičky.")
		C.Alica.pose("grin")
		await C.Alica.say("A ta mapa? Kam vede?")
		C.Alica.pose()
		await C.Deda.say("Ke starému rybníku. Ale to už je další případ!")
		await the_end("Konec 2. dílu")
