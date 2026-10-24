@tool
extends "res://game/shared/story_room.gd"
## Story 5, the snowy garden at the chalupa. Every morning a new snowman stands here: one waving, one with
## a snow dog, one holding Hanka's lost mitten. The small star prints lead through the gap in the fence.
## Morning 3: Alica reads the three snowmen like Franta's picture letter, "Kdo staví sněhuláky?", and the
## girls answer with snowmen of their own (minigame). Morning 4: a tiny snowman with a red pompom, and Bětka.

const Data := preload('room_zahrada5_state.gd')
const WhoGame := preload("res://game/minigames/who_5.gd")
const SnowGame := preload("res://game/minigames/snowman.gd")
const SNOWMEN := ["snowman1", "snowman1", "snowman2", "snowman3", "snowman3"]

var state: Data = load("res://game/rooms/zahrada5/room_zahrada5.tres")


func _on_room_entered() -> void:
	match C.player.last_room:
		"Ves5": C.player.position = get_marker_position("ZeSilnice")
		_: C.player.position = get_marker_position("Start")
	Globals.bring_sister(self, Vector2(170, 10))
	place("Joey", joey_spot())
	var tex: Texture2D = load("res://assets/props/%s.png" % SNOWMEN[clampi(Globals.s_day, 0, 4)])
	var sm := get_prop("Snehulak")
	sm.texture = tex
	sm.get_node("Sprite2D").texture = tex
	sm.visible = Globals.s_day > 0
	get_prop("Nit").visible = Globals.s_day >= 2
	get_prop("Rukavice").visible = Globals.s_road and Globals.s_day < 2
	get_prop("Odpoved").visible = Globals.s_answer
	get_prop("Hvezda").visible = Globals.s_answer
	get_prop("Malicky").visible = Globals.s_day >= 4
	if Globals.s_day >= 4 and not Globals.s_betka:
		place("Betka", Vector2(1540, 790)).pose("whisper")
	else:
		remove("Betka")
	remove("Rybar")
	Globals.exit_arrow(self, "NaSilnici", false)


func _on_room_transition_finished() -> void:
	if Globals.phase != "s_morning":
		return
	Globals.phase = ""
	_card([["", "Ráno…", "Druhé ráno…", "Třetí ráno…", "Čtvrté ráno…"][clampi(Globals.s_day, 0, 4)]], 1.6)
	await get_tree().create_timer(2.0).timeout
	match Globals.s_day:
		1:
			C.Hanka.pose("point")
			await C.Hanka.say("Sněhulák! Někdo ho postavil v noci!")
			C.Hanka.pose()
			await C.Alica.say("Byl rychlejší než my. Kdo to byl?")
		2:
			await C.Hanka.say("Další sněhulák! A má pejska!")
			await C.Joey.say("Haf?")
			await C.Alica.say("A zase jsme ho nechytily…")
		3:
			C.Hanka.pose("point")
			await C.Hanka.say("Třetí sněhulák! A drží… moji rukavičku!")
			C.Hanka.pose()
		4:
			await C.Alica.say("Hani, koukej! Vedle naší odpovědi stojí malinký sněhulák. S bambulí!")
			await C.Hanka.say("A ty stopy vedou k nám. Ne pryč!")
			await C.Hanka.say("Za plotem někdo kouká…")


func joey_goal() -> Vector2:
	match Globals.s_day:
		1:
			if not Globals.s_nose: return get_prop("Snehulak").position + Vector2(-200, 120)
			if not Globals.s_stars: return get_prop("Stopy").position + Vector2(-180, 40)
			if not Globals.s_road: return get_hotspot("Diera").walk_to_point + Vector2(-100, 60)
			if not Globals.s_tonda: return get_hotspot("NaSilnici").walk_to_point
		2:
			if not Globals.s_dog: return get_prop("Snehulak").position + Vector2(-200, 120)
			if not Globals.s_thread: return get_prop("Nit").position + Vector2(-120, 200)
			if Globals.s_babicka and not (Globals.s_tonda_ok and Globals.s_parsnip and Globals.s_boots and Globals.s_curtain):
				return get_hotspot("NaSilnici").walk_to_point
		3:
			if not Globals.s_mitten or not Globals.s_answer: return get_prop("Snehulak").position + Vector2(-200, 120)
		4:
			return C.Betka.position + Vector2(-260, 120) if has_character("Betka") else Vector2.ZERO
	return get_hotspot("Dum").walk_to_point


func on_click(node: Node) -> void:
	match node.script_name:
		"Snehulak": await _snowman()
		"Stopy": await _prints()
		"Nit": await _thread()
		"Rukavice":
			await C.player.walk_to_clicked()
			await C.player.say("Něco tu leží ve sněhu.")
		"Diera": await _gap()
		"Plot":
			await C.player.walk_to_clicked()
			await C.player.say("Plot. Za ním je silnice.")
		"Odpoved", "Hvezda":
			await C.player.walk_to_clicked()
			await C.player.say("Naše odpověď: Ahoj! Pojď si s námi hrát!")
		"Malicky":
			await C.player.walk_to_clicked()
			await C.player.say("Malinký sněhulák s červenou bambulí. To je odpověď na odpověď!")
		"Dum": await _home()
		"NaSilnici":
			await C.player.walk_to_clicked()
			R.goto_room("Ves5")
		_: await super(node)


func on_character(chr: PopochiuCharacter, action: String, _item: PopochiuInventoryItem = null) -> bool:
	if chr.script_name != "Betka" or action == "look":
		return false
	await _betka()
	return true


#region Day 1 #########################################################################################
func _snowman() -> void:
	await C.player.walk(get_marker_position("Snehulak"))
	await C.player.face_clicked()
	match Globals.s_day:
		1:
			if not Globals.s_nose:
				await hand_over(C.Alica, "Je malý jako já! Alico, prohlédni si ho lupou.")
			C.Alica.pose("lens")
			await C.Alica.say("Oči z ořechů. Knoflíky ze šišek. A nos…")
			await C.Alica.say("To není mrkev! Je bílý!")
			C.Alica.pose()
			Globals.s_nose = true
			await _check_day()
		2:
			await C.player.say("Sněhulák a vedle něj pejsek ze sněhu. S ušima z listí!")
			await C.Joey.say("Haf haf?")
			await C.Hanka.say("Joey, to jsi ty! Ze sněhu!")
			Globals.s_dog = true
			await _check_day()
		3:
			await _mitten_morning()
		_:
			await C.player.say("Naši sněhuláci a Bětčin malý.")


func _prints() -> void:
	await C.player.walk_to_clicked(Vector2(-200, 20))
	if Globals.s_stars:
		await C.player.say("Malé stopy s hvězdičkami. Vedou k plotu.")
		return
	C.Hanka.pose("point")
	await C.Hanka.say("Malé stopičky! Malé jako moje.")
	C.Hanka.pose()
	C.Alica.pose("lens")
	await C.Alica.say("A na podrážce mají hvězdičky! Zapisuju: STOPY S HVĚZDIČKAMI.")
	C.Alica.pose()
	Globals.s_stars = true
	await _check_day()


func _gap() -> void:
	await C.player.walk_to_clicked()
	if not Globals.s_stars:
		await C.player.say("Díra v plotě. Malá.")
		return
	await hand_over(C.Hanka, "Stopy vedou dírou v plotě. Tudy se neprotáhnu. Hani, ty jo!")
	await C.Hanka.say("Stopy vedou dírou v plotě. Já se vejdu!")
	await C.Alica.say("A já to oběhnu po silnici. Počkej na mě!")
	if not Globals.s_road:
		get_prop("Rukavice").show()
	R.goto_room("Ves5")


func _check_day() -> void:
	if Globals.s_day == 1 and Globals.s_nose and Globals.s_stars and not Globals.s_road:
		await C.Alica.say("Stopy vedou k plotu. Půjdeme po nich!")
	elif Globals.s_day == 2 and Globals.s_dog and Globals.s_thread and not Globals.s_babicka:
		await C.Alica.say("Mám nápad. Uděláme tabuli podezřelých. Doma v kuchyni!")
#endregion


#region Day 2 #########################################################################################
func _thread() -> void:
	await C.player.walk_to_clicked(Vector2(-100, 120))
	if C.player == C.Alica:
		C.Alica.pose("lens")
	else:
		C.Hanka.pose("point")
	await C.player.say("Červená vlnka na plotě. Jako z bambule!")
	C.player.pose()
	Globals.s_thread = true
	await _check_day()
#endregion


#region Day 3: the letter, who, the answer ##########################################################
func _mitten_morning() -> void:
	if not Globals.s_mitten:
		await C.Hanka.say("Moje rukavička! Ztratila jsem ji u plotu.")
		await C.Hanka.say("Kdo ji našel a vrátil, je hodný.")
		I.Rukavicka.add()
		Globals.s_mitten = true
		C.Alica.pose("think")
		await C.Alica.say("Počkej… Tři sněhuláci. Jeden mává. Jeden má pejska. Jeden drží rukavičku.")
		await C.Alica.say("To je jako Frantův dopis! Sněhuláci jsou dopis!")
		C.Alica.pose()
		await picture("res://assets/slides/snowmen_letter.png", "Ahoj – mám ráda pejska – našla jsem tohle")
		await C.Alica.say("Malé hvězdičky, bambule, pastinák, botičky u Franty… Někdo malý. A stydí se.")
	if not Globals.s_who:
		var mg: CanvasLayer = WhoGame.new()
		add_child(mg)
		await mg.finished
		Globals.s_who = true
		await C.Alica.say("Chytíme ho! Dáme na plot zvoneček!")
		await C.Hanka.say("Ne! Když ho chytíš, bude se bát.")
		await C.Hanka.say("Musíme mu odpovědět. Sněhuláky!")
		await C.Alica.say("…Máš pravdu, Hani. Postavíme odpověď.")
	if not Globals.s_answer:
		var mg: CanvasLayer = SnowGame.new()
		add_child(mg)
		await mg.finished
		Globals.s_answer = true
		await pop("Odpoved")
		await pop("Hvezda")
		await C.Hanka.say("Velký sněhulák mává. A tři malí se drží za ruce. Pojď si s námi hrát!")
		await C.Alica.say("A hvězda z větviček. A naši sněhuláci mají nos z mrkve!")
		await C.Alica.say("Teď počkáme do rána.")
#endregion


#region Day 4: Bětka ###################################################################################
func _betka() -> void:
	await hand_over(C.Hanka, "Hani, jdi ty. Tebe se nebude bát.")
	await C.Hanka.walk(C.Betka.position + Vector2(-230, 60))
	C.Hanka.pose("nomonkey")
	await C.Hanka.say("Ahoj. Chceš si pochovat opičku?")
	C.Betka.pose("monkey")
	await C.Betka.say("…Já jsem Bětka.")
	var f := place("Rybar", Vector2(2050, 900))
	f.ignore_walkable_areas = true
	await f.walk(Vector2(1750, 900))
	f.ignore_walkable_areas = false
	f.pose("home")
	await C.Rybar.say("Moje vnučka. Je u mě na zimu, než se maminka vrátí z práce.")
	await C.Rybar.say("Je stydlivá. Jako já, když jsem byl malý. Tak jsem ji naučil obrázkové dopisy.")
	await C.Betka.say("Sněhuláci jsou moje dopisy. Ráno nikdo nevidí, že se bojím.")
	await C.Betka.say("A rukavičku jsem chtěla vrátit.")
	await C.Hanka.say("Děkuju! Pojď si s námi hrát, Bětko!")
	await C.Alica.say("Klub Hvězdička má nového člena!")
	await C.Rybar.say("Zatím na zkoušku. Ale hvězdičky na botách už má.")
	C.Hanka.pose()
	C.Betka.pose("grin")
	Globals.s_betka = true
	Globals.dress()
	await the_end("Konec 5. dílu")
#endregion


## The garden door: home to the kitchen (the kitchen moves the story to the next morning when a day is done).
func _home() -> void:
	await C.player.walk_to_clicked()
	R.goto_room("Kuchyne5")
