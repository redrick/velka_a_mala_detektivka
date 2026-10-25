@tool
extends "res://game/shared/story_room.gd"
## Story 6, babička's kitchen in Advent: the window with the cooling tray on the sill, the pantry shelf with
## the tin. Two thieves on two trails: outside the tits peck the broken pieces (the dawn watch, the feeder in
## the garden), inside whole stars vanish from the tin at night: 7, then 2 more. Suspects: mice, Joey,
## Hanka, Tonda. Hanka finds děda's boots with spruce needles and a red ribbon; "Kdo bere hvězdičky?".

const Data := preload('room_kuchyne6_state.gd')
const WhoGame := preload("res://game/minigames/who_6.gd")
const DAWN := Color(0.55, 0.55, 0.72)
const EVENING := Color(0.75, 0.68, 0.62)

var state: Data = load("res://game/rooms/kuchyne6/room_kuchyne6.tres")


func _on_room_entered() -> void:
	C.player.position = get_marker_position("ZeZahrady") if C.player.last_room == "Zahrada6" else get_marker_position("Start")
	Globals.bring_sister(self, Vector2(-170, 10))
	place("Babicka", Vector2(1100, 900))
	place("Joey", Vector2(900, 1010))
	if not Globals.p_who:
		place("Deda", Vector2(200, 960))
	else:
		remove("Deda")
	if Globals.p_day == 2 and not Globals.p_who:
		place("Tonda", Vector2(1000, 940))
	else:
		remove("Tonda")
	var tray := get_prop("Tac")
	var tex: Texture2D = load("res://assets/props/%s.png" % ("tray_whole" if Globals.p_day >= 2 else "tray_pecked"))
	tray.texture = tex
	tray.get_node("Sprite2D").texture = tex
	tray.visible = Globals.p_day >= 1
	get_prop("Stopicky").visible = Globals.p_day == 1
	get_prop("Sykorky").visible = Globals.phase == "p_dawn"
	get_prop("Tlapky").visible = Globals.p_day == 1
	get_prop("Past").visible = Globals.p_tin1
	get_prop("Sacek").visible = Globals.p_day == 2 and Globals.p_boots
	if not Globals.p_intro:
		dark(EVENING, false)
	elif Globals.phase == "p_dawn":
		dark(DAWN, false)
	Globals.exit_arrow(self, "Dvere", false, Globals.p_intro)


func _on_room_transition_finished() -> void:
	if not Globals.p_intro:
		await _baking()
	elif Globals.phase == "p_dawn":
		await _dawn()
	elif Globals.phase == "p_morning":
		Globals.phase = ""
		_card(["Druhé ráno…"], 1.6)
		await get_tree().create_timer(2.0).timeout
		await C.Hanka.say("Na parapetu nikdo nebyl! Ptáčci jsou na krmítku.")
		await C.Alica.say("Případ vyřešen. Ještě se podívám do plechovky…")
	else:
		# resumed from a save made between the last clue of a day and what it starts
		await _day1()
		await _day2()


func joey_goal() -> Vector2:
	if Globals.p_day == 1:
		if not Globals.p_sill: return get_marker_position("Okno") + Vector2(-160, 40)
		if not Globals.p_tin1: return get_marker_position("Spiz") + Vector2(-160, 40)
		if not Globals.p_joey: return get_prop("Tlapky").position + Vector2(-260, 40)
		if Globals.p_birds and not Globals.p_feeder: return get_hotspot("Dvere").walk_to_point
	if Globals.p_day == 2:
		if not Globals.p_tin2: return get_marker_position("Spiz") + Vector2(-160, 40)
		if not Globals.p_trap: return get_prop("Past").position + Vector2(-200, 60)
		if not Globals.p_boots: return get_prop("Boty").position + Vector2(-220, 40)
		if not Globals.p_tonda: return C.Tonda.position + Vector2(-240, 0)
		if not Globals.p_hanka: return Globals.sister().position + Vector2(-220, 0)
	return Vector2.ZERO


#region The baking, the first morning ################################################################
func _baking() -> void:
	await C.Babicka.say("Upekly jsme dvanáct hvězdiček, dvanáct srdíček a dvanáct měsíčků.")
	await C.Hanka.say("Srdíčka mají čokoládu!")
	await C.Babicka.say("Ty křivé a zlomené dám vychladnout na plech za okno.")
	await C.Deda.say("Mňam. A kolik je těch hvězdiček? …Jen se ptám.")
	await C.Babicka.say("Hanka dostane jedno srdíčko na dobrou noc. A teď spát!")
	Globals.p_intro = true
	Globals.p_day = 1
	_card(["Ráno…"], 1.6)
	light_up(1.0)
	await get_tree().create_timer(2.0).timeout
	await C.Alica.say("Babi! Plech na parapetu je celý ozobaný!")


func on_click(node: Node) -> void:
	match node.script_name:
		"Okno", "Tac", "Stopicky": await _window()
		"Sykorky": await C.player.say("Sýkorky! Ptáčci mají hlad.")
		"Plechovka": await _tin()
		"Tlapky": await _paws()
		"Past": await _trap()
		"Boty": await _boots()
		"Sacek":
			await C.player.walk_to_clicked()
			await C.player.say("Sáček na polevu. Je v něm bílá poleva. Někdo jím psal?")
		"Fotka":
			await C.player.walk_to_clicked()
			await C.player.say("Fotka Klubu Hvězdička. Jedna, dva, tři… sedm!")
		"Kamna":
			await C.player.walk_to_clicked()
			await C.player.say("Kamna hřejí. Voní to tu perníkem.")
		"Dvere":
			await C.player.walk_to_clicked()
			R.goto_room("Zahrada6")
		_: await super(node)


func _window() -> void:
	await C.player.walk(get_marker_position("Okno"))
	if Globals.p_day >= 2:
		await C.player.say("Plech je celý. Ptáčci teď chodí na krmítko.")
		return
	if Globals.p_sill:
		await C.player.say("Ozobané kousky a malé stopičky.")
		return
	if C.player == C.Alica:
		C.Alica.pose("lens")
	await C.player.say("Kousíčky jsou ozobané. Samé drobečky.")
	C.player.pose()
	C.Hanka.pose("point")
	await C.Hanka.say("A na parapetu jsou malé stopičky. Jako vidlička!")
	C.Hanka.pose()
	Globals.p_sill = true
	await _day1()


func _tin() -> void:
	await C.player.walk(get_marker_position("Spiz"))
	if Globals.p_day == 1 and not Globals.p_tin1:
		await picture("res://assets/slides/tin5.png", "Plechovka ve spíži")
		await C.Alica.say("Hvězdiček je jen pět! Sedm chybí!")
		await C.Babicka.say("Srdíček je jedenáct. To jedno snědla Hanka na dobrou noc.")
		await C.Alica.say("Ale venku jsou drobečky. A tady chybí celé hvězdy. Nic rozbitého.")
		C.Alica.pose("think")
		await C.Alica.say("To nejsou stejní zloději!")
		C.Alica.pose()
		await C.Deda.say("To budou myši. Dám do spíže past.")
		await pop("Past")
		Globals.p_tin1 = true
		await _day1()
	elif Globals.p_day == 2 and not Globals.p_tin2:
		await picture("res://assets/slides/tin3.png", "Plechovka ve spíži")
		await C.Alica.say("Zase chybí dvě hvězdičky! Jsou jenom tři.")
		await C.Alica.say("Případ NENÍ vyřešen!")
		Globals.p_tin2 = true
		await _day2()
	else:
		await C.player.say("Plechovka s perníčky.")


func _paws() -> void:
	await C.player.walk_to_clicked(Vector2(-260, 20))
	if Globals.p_joey:
		await C.player.say("Moučné tlapky. Končí u spíže.")
		return
	await C.Alica.say("Moučné tlapky! A vedou ke spíži. Joey, mám tě!")
	await C.Joey.say("Haf?")
	await C.Hanka.say("Tlapky končí u plechovky. Joey si tam jen sedl a škemral.")
	await C.Hanka.say("A Joey neumí otevřít plechovku!")
	Globals.p_joey = true
	await _day1()


func _day1() -> void:
	if Globals.p_day == 1 and Globals.p_sill and Globals.p_tin1 and Globals.p_joey and not Globals.p_birds:
		await C.Alica.say("Zítra za svítání budeme hlídat okno. Uvidíme, kdo zobe!")
		await fade(func(): pass, "Za svítání…")
		Globals.phase = "p_dawn"
		R.goto_room("Kuchyne6")


func _dawn() -> void:
	Globals.phase = ""
	await pop("Sykorky")
	sfx("ŤUK ŤUK!", Vector2(900, 380), 70)
	C.Hanka.pose("point")
	await C.Hanka.say("Sýkorky! Ptáčci mají hlad!")
	C.Hanka.pose()
	await C.Alica.say("Takže venku zobou sýkorky.")
	await C.Hanka.say("A venku přes zahradu jde někdo s lucernou…")
	await C.Babicka.say("Perníček ptáčkům škodí. Je v něm cukr a koření.")
	await C.Babicka.say("Postavíme jim krmítko. Se semínky a lojem.")
	await C.Deda.say("Pomůžu vám! Hned!")
	Globals.p_birds = true
	await light_up(1.0)
	get_prop("Sykorky").hide()
	await C.Alica.say("Krmítko postavíme na zahradě. Pod oknem!")
#endregion


#region The second morning ############################################################################
func _trap() -> void:
	await C.player.walk_to_clicked(Vector2(-200, 40))
	if Globals.p_day < 2:
		await C.player.say("Dědova past na myši.")
		return
	if C.player == C.Alica:
		C.Alica.pose("lens")
	await C.player.say("Past je prázdná. A nemá žádnou návnadu!")
	C.player.pose()
	await C.Alica.say("Děda v myši nevěří. A myši by okusovaly všechno, ne jen celé hvězdičky.")
	Globals.p_trap = true
	await _day2()


func _boots() -> void:
	await C.player.walk_to_clicked(Vector2(-220, 20))
	if Globals.p_day < 2:
		await C.player.say("Dědovy válenky.")
		return
	await hand_over(C.Hanka, "Dědovy válenky. Hani, ty jsi malá, podívej se zblízka!")
	if Globals.p_boots:
		await C.Hanka.say("Jehličí a červená stužka.")
		return
	C.Hanka.pose("point")
	await C.Hanka.say("Dědovy boty jsou mokré. A je na nich jehličí! A červená stužka!")
	C.Hanka.pose()
	C.Babicka.pose("ribbon")
	await C.Babicka.say("Moje červená stužka! Na cívce už skoro žádná není.")
	C.Babicka.pose()
	get_prop("Sacek").show()
	await C.Alica.say("A v dřezu je sáček s bílou polevou. Někdo psal polevou…")
	Globals.p_boots = true
	await _day2()


func on_character(chr: PopochiuCharacter, action: String, _item: PopochiuInventoryItem = null) -> bool:
	if action == "look" or chr == C.Joey:
		return false
	match chr.script_name:
		"Hanka", "Alica":
			if chr == C.player or Globals.p_day != 2 or Globals.p_hanka:
				return false
			await C.player.walk(chr.position + Vector2(-220, 0))
			await _hanka_crumbs()
		"Deda":
			await C.player.walk(chr.position + Vector2(240, 0))
			if Globals.p_day == 2:
				await C.Deda.say("Myši, holky. Určitě myši. …Kde jsou moje noviny?")
			else:
				await C.Deda.say("Mňam, perníčky. Jen jeden na zkoušku.")
		"Babicka":
			await C.player.walk(chr.position + Vector2(240, 0))
			await C.Babicka.say("Perníčky jsou na Vánoce. Hlídejte mi je, detektivky!")
		"Tonda":
			await C.player.walk(chr.position + Vector2(-240, 0))
			await C.Tonda.say("Já bych jich snědl sto! Hlavně měsíčky. Ty jsou nejlepší.")
			await C.Alica.say("Měsíčků je pořád dvanáct. A v noci jsi byl doma. Zamčený dům… Škrtám!")
			Globals.p_tonda = true
			await _day2()
		_:
			return false
	return true


func _hanka_crumbs() -> void:
	await C.Alica.say("Hani… máš drobečky. Na svetru i na polštáři.")
	C.Hanka.pose("cry")
	await C.Hanka.say("Já ne! Já to nebyla!")
	await C.Babicka.say("Jedno srdíčko jsem jí dala já. Na dobrou noc.")
	C.Alica.pose("lens")
	await C.Alica.say("Drobečky jsou tmavé. Čokoládové. Ze srdíčka!")
	await C.Alica.say("Ale chybí hvězdičky s bílou polevou. Hani, promiň.")
	C.Alica.pose()
	C.Hanka.pose()
	await C.Hanka.say("…Dobře. Moje tajemství je obrázek pro Bětku.")
	Globals.p_hanka = true
	await _day2()


func _day2() -> void:
	if Globals.p_day != 2 or Globals.p_who:
		return
	if not (Globals.p_tin2 and Globals.p_trap and Globals.p_hanka and Globals.p_tonda and Globals.p_boots):
		return
	C.Hanka.pose("photo")
	await C.Hanka.say("Jedna, dva, tři… sedm! Na fotce Klubu je sedm lidí!")
	C.Hanka.pose()
	await C.Alica.say("Sedm hvězdiček pro sedm členů. Ale proč pak ještě dvě?")
	var mg: CanvasLayer = WhoGame.new()
	add_child(mg)
	await mg.finished
	Globals.p_who = true
	await C.Alica.say("Jehličí! Velký smrk je jenom u mlýna. Za svítání půjdeme po dědových stopách!")
	await fade(func(): pass, "První adventní neděle, za svítání…")
	Globals.phase = "p_spruce"
	R.goto_room("Mlyn6")
#endregion
