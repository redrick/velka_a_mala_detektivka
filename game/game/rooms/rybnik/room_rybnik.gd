@tool
extends "res://game/shared/story_room.gd"
## Story 3, the old pond. Which willow? (děda knows the stump) → děda's big steps land in the pond →
## the children's steps (minigame) → Hanka finds the star stone → Joey digs: empty! → clues and
## suspects (boot prints, round dots, Tonda runs off, the badger's burrow, the fisherman) → evening at
## home → dawn: Hanka's torch catches Tonda, who joins → whose print is it? (minigame) → Joey's nose
## leads to the mill.

const Data := preload('room_rybnik_state.gd')
const StepsGame := preload("res://game/minigames/steps.gd")
const PrintsGame := preload("res://game/minigames/prints.gd")
const DAWN := Color(0.42, 0.44, 0.62)

var state: Data = load("res://game/rooms/rybnik/room_rybnik.tres")


func _on_room_entered() -> void:
	match C.player.last_room:
		"Mlyn": C.player.position = get_marker_position("ZMlyna")
		_: C.player.position = get_marker_position("Start")
	Globals.bring_sister(self, Vector2(170, 10))
	place("Deda", Vector2(620, 900))
	place("Joey", Vector2(470, 990))
	place("Rybar", Vector2(1720, 790))
	get_prop("Kamen").visible = Globals.r_steps
	get_prop("Dira").visible = Globals.r_hole
	get_prop("Stopy").visible = Globals.r_hole
	if Globals.r_hole and not Globals.r_tonda_ran:
		place("Tonda", Vector2(900, 800)).pose("spade")
	elif Globals.phase == "r_dawn" or (Globals.r_evening and not Globals.r_tonda_ok):
		place("Tonda", Vector2(900, 800)).pose("spade")
		remove("Rybar")
		dark(DAWN)
	elif Globals.r_tonda_ok:
		place("Tonda", Vector2(1000, 960))
	else:
		remove("Tonda")
	get_hotspot("KMlynu").clickable = Globals.r_trail
	Globals.exit_arrow(self, "Domu", true)
	Globals.exit_arrow(self, "KMlynu", false, Globals.r_trail)


func _on_room_transition_finished() -> void:
	if Globals.phase == "r_dawn":
		Globals.phase = ""
		_card(["Druhý den za svítání…"], 1.6)
		await get_tree().create_timer(2.0).timeout
		await C.Hanka.say("Mám baterku.")
		await C.Alica.say("Psst! Tamhle u vrby… Někdo kope!")
		await C.Alica.say("Hanko, posviť na něj!")
	elif not Globals.r_stump and C.player.last_room != "Mlyn":
		await C.Deda.say("Jé… Rybník je mnohem menší, než byl. A lávka tu už dávno není.")
		await C.Alica.say("Na mapě je jedna velká vrba. Ale tady jsou tři!")


func joey_goal() -> Vector2:
	if not Globals.r_stump:
		return C.Deda.position + Vector2(160, 60)
	if not Globals.r_steps:
		return get_marker_position("Parez") + Vector2(-150, 40)
	if not Globals.r_boots or not Globals.r_dots:
		return get_prop("Stopy").position + Vector2(-190, 20)
	if not Globals.r_tonda_ran:
		return Vector2(760, 900)
	if not Globals.r_burrow:
		return get_prop("Nora").position + Vector2(180, 140)
	if not Globals.r_rybar:
		return C.Rybar.position + Vector2(-200, 180)
	return Vector2.ZERO


#region Clicks ####################################################################################
func on_click(node: Node) -> void:
	match node.script_name:
		"Vrba1", "Vrba2", "Vrba3":
			await C.player.walk_to_clicked()
			await C.player.say("Tahle vrba je moc malá." if Globals.r_stump else "Která vrba je ta velká? Zeptáme se dědy!")
		"Parez": await _stump()
		"Kamen": await C.player.say("Kámen s hvězdičkou. Tady to je!")
		"Dira": await C.player.say("Prázdná díra. Poklad je pryč.")
		"Stopy": await _prints_click()
		"Nora": await _burrow()
		"Domu":
			await C.player.walk_to_clicked()
			R.goto_room("Kuchyne3")
		"KMlynu":
			await C.player.walk_to_clicked()
			R.goto_room("Mlyn")
		_: await super(node)


func on_look(node: Node) -> void:
	match node.script_name:
		"Parez": await C.player.say("Starý pařez.")
		"Nora": await C.player.say("Díra ve svahu.")
		"Stopy": await C.player.say("Stopy v bahně.")
		_: await super(node)


func on_character(chr: PopochiuCharacter, action: String, _item: PopochiuInventoryItem = null) -> bool:
	if action == "look" or chr == C.Joey:
		return false
	await C.player.walk_to_clicked(Vector2(-200, 0))
	await C.player.face_clicked()
	if chr == C.Deda:
		await _talk_deda()
	elif chr == C.Tonda:
		await _talk_tonda()
	elif chr == C.Rybar:
		await _talk_rybar()
	else:
		return false
	return true
#endregion


#region The willow, the steps and the hole #########################################################
func _talk_deda() -> void:
	if not Globals.r_stump:
		await C.Alica.say("Dědo, pamatuješ si, která vrba to byla?")
		await C.Deda.say("Hm… Velká vrba byla nejtlustší ze všech. Tlustší než já!")
		await C.Deda.walk(get_marker_position("Parez") + Vector2(-160, 0))
		await C.Deda.say("Tady! Velká vrba spadla. Zbyl z ní jen pařez.")
		Globals.r_stump = true
	elif not Globals.r_steps:
		await C.Deda.say("Od pařezu dvacet kroků. Klikni na pařez!")
	elif not Globals.r_hole:
		await C.Deda.say("Joey, hrabej!")
		await _dig()
	elif not Globals.r_evening:
		await C.Deda.say("Kdo mohl vědět, kde poklad je? Mapa byla přece roztržená…")
	else:
		await C.Deda.say("Klub Hvězdička drží spolu!")


func _stump() -> void:
	await C.player.walk_to_clicked()
	if not Globals.r_stump:
		await C.player.say("Starý pařez. Zeptáme se dědy, kde byla velká vrba.")
		return
	if Globals.r_steps:
		await C.player.say("Tady stála velká vrba.")
		return
	await C.Deda.say("Tak… Od pařezu dvacet kroků. Jedna… dva… tři…")
	C.Deda.ignore_walkable_areas = true
	await C.Deda.walk(Vector2(1180, 700))
	sfx("ŠPLOUCH!", Vector2(1080, 560))
	await C.Deda.say("Jejda! To asi nebude ono.")
	await C.Deda.walk(get_marker_position("Parez") + Vector2(-160, 0))
	C.Deda.ignore_walkable_areas = false
	C.Alica.pose("point")
	await C.Alica.say("Dědo! Na mapě jsou malinké šlápoty. Tys byl malý kluk. Musí to být dětské kroky!")
	C.Alica.pose()
	await C.Deda.say("Máš pravdu. Tak naplánujte dvacet dětských kroků!")
	var mg: CanvasLayer = StepsGame.new()
	add_child(mg)
	await mg.finished
	Globals.r_steps = true
	await C.player.walk(get_marker_position("Kamen"))
	await pop("Kamen")
	C.Hanka.pose("point")
	await C.Hanka.say("Tady v trávě je kámen! A má hvězdičku!")
	C.Hanka.pose()
	await C.Deda.say("Joey, hrabej!")
	await _dig()


func _dig() -> void:
	await C.Joey.walk(get_prop("Kamen").position + Vector2(120, 0))
	sfx("HRAB HRAB", Vector2(1600, 800), 60)
	await get_tree().create_timer(1.0).timeout
	await pop("Dira")
	get_prop("Stopy").show()
	await C.Alica.say("Ta hlína je nějaká měkká…")
	await C.Deda.say("Jako by ji někdo nedávno kopal.")
	C.Hanka.pose("surprised")
	await C.Hanka.say("Poklad je pryč!")
	C.Hanka.pose()
	C.Alica.pose("surprised")
	await C.Alica.say("Někdo tu byl před námi! Hledejte stopy!")
	C.Alica.pose()
	Globals.r_hole = true
	place("Tonda", Vector2(900, 800)).pose("spade")
#endregion


#region Clues and suspects #########################################################################
func _prints_click() -> void:
	await C.player.walk_to_clicked(Vector2(-200, 20))
	await C.player.face_clicked()
	if Globals.r_tonda_ok and not Globals.r_prints:
		await _compare_prints()
		return
	if C.player == C.Alica:
		if not Globals.r_boots:
			C.Alica.pose("lens")
			await C.Alica.say("Stopy od velkých bot!")
			C.Alica.pose()
			Globals.r_boots = true
		else:
			await C.Alica.say("Velké boty. A vedle nich malé dírky… Hanka je vidí líp.")
	else:
		if not Globals.r_dots:
			C.Hanka.pose("point")
			await C.Hanka.say("A tady jsou malé dírky. Jako když zobe ptáček.")
			C.Hanka.pose()
			Globals.r_dots = true
		else:
			await C.Hanka.say("Dírky jsou kulaté. Alica má lupu na velké stopy.")
	await _check_day_done()


func _talk_tonda() -> void:
	if Globals.r_tonda_ok:
		await C.Tonda.say("Jsem v týmu! Kam půjdeme?")
		return
	if is_dark():
		if C.player != C.Hanka:
			await C.Alica.say("Hanko, posviť na něj!")
			return
		sfx("CVAK!", C.Tonda.position + Vector2(-80, -620), 70)
		await C.Alica.say("Máme tě!")
		await C.Tonda.say("Aaa!")
		await _tonda_secret()
		return
	if not Globals.r_tonda_ran:
		await C.Alica.say("Hele! Tonda! A má lopatku! Tondo, cos tu kopal?")
		await C.Tonda.say("Nic! Nic nevím!")
		C.Tonda.ignore_walkable_areas = true
		await C.Tonda.walk(Vector2(-150, 800))
		C.Tonda.ignore_walkable_areas = false
		remove("Tonda")
		await C.Alica.say("Utekl! A byl celý od bláta. Podezřelý číslo jedna: Tonda!")
		await C.Hanka.say("Hm…")
		Globals.r_tonda_ran = true
		await _check_day_done()


func _tonda_secret() -> void:
	C.Tonda.pose("box")
	await C.Tonda.say("Zakopávám svůj poklad. Slyšel jsem vás přes plot. O klubu a o pokladu.")
	await C.Tonda.say("Chtěl jsem mít taky klub. Jenže jsem sám.")
	C.Hanka.pose("grin")
	await C.Hanka.say("Já říkala, že Tonda je hodný!")
	C.Hanka.pose()
	await C.Alica.say("Promiň, Tondo. Myslela jsem, žes vzal náš poklad.")
	await C.Tonda.say("Váš poklad? Ten jsem nevzal.")
	await C.Tonda.say("Ale minulou neděli ráno jsem šel s tátou pro rohlíky. A u vrby svítilo světýlko!")
	await C.Alica.say("Stopa číslo čtyři!")
	await C.Hanka.say("Pomůžeš nám hledat?")
	C.Tonda.pose()
	await C.Tonda.say("Jasně!")
	Globals.r_tonda_ok = true
	await light_up()
	place("Rybar", Vector2(1720, 790))
	await C.Alica.say("Porovnáme stopy u díry! Kdo tu kopal?")


func _burrow() -> void:
	await C.player.walk_to_clicked(Vector2(200, 120))
	if Globals.r_burrow:
		await C.player.say("Jezevec v noci hrabe v zemi. Hledá žížaly a kořínky.")
		return
	sfx("HAF HAF!", get_prop("Nora").position + Vector2(-60, -180), 60)
	await C.Alica.say("Další díry!")
	await C.Deda.say("To je nora. Tady bydlí jezevec.")
	await C.Alica.say("Jezevec hrabe! Podezřelý číslo dvě!")
	Globals.r_burrow = true
	await _check_day_done()


func _talk_rybar() -> void:
	if Globals.r_prints:
		await C.Rybar.say("Tak co, detektivky? Našly jste toho, kdo tu straší ryby?")
		return
	if Globals.r_tonda_ok:
		await C.Alica.say("Pane rybáři, nebyl jste tu minulou neděli ráno?")
		await C.Rybar.say("Ráno spím. Na ryby chodím odpoledne. A moje holinky jsou obří!")
		return
	await C.Rybar.say("Samé díry! A ráno tu někdo svítí a straší ryby.")
	await C.Alica.say("Svítí? Kdo?")
	await C.Rybar.say("To já nevím. Ráno spím.")
	Globals.r_rybar = true
	await _check_day_done()


## All the first day's clues found: home for the evening.
func _check_day_done() -> void:
	if Globals.r_evening or not (Globals.r_boots and Globals.r_dots and Globals.r_tonda_ran and Globals.r_burrow and Globals.r_rybar):
		return
	await C.Alica.say("Máme hodně stop. Doma to promyslíme!")
	Globals.phase = "r_evening"
	R.goto_room("Kuchyne3")


func _compare_prints() -> void:
	var mg: CanvasLayer = PrintsGame.new()
	add_child(mg)
	await mg.finished
	Globals.r_prints = true
	await C.Alica.say("Ptáček to nebyl. Jezevec taky ne. Velká holinka… a hůlka!")
	await C.Tonda.say("Rybářovy holinky jsou obří. To nebyl on.")
	await C.Hanka.say("Joey něco čmuchá!")
	await C.Joey.say("Čmuch čmuch!")
	await C.Joey.walk(Vector2(1800, 960))
	Globals.r_trail = true
	get_hotspot("KMlynu").clickable = true
	Globals.show_exit(self, "KMlynu")
	await C.Alica.say("Stopa vede ke mlýnu! Za Joeym!")
#endregion
