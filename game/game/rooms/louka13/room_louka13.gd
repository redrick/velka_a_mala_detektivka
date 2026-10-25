@tool
extends "res://game/shared/story_room.gd"
## Story 13, the camp on Hvězdná louka: the family's dome tent, děda's old Klub tent, Tonda and Bětka's small one,
## the campfire, the willows by the creek. Day 1: the camp, the evening at the fire, Hanka's night walk (PLESK).
## Day 2: the willow is down, děda's stick is gone; the saw, the knife and Joey are checked, then "Čím to bylo?".

const Data := preload('room_louka13_state.gd')
const CutsGame := preload("res://game/minigames/cuts.gd")
const EVENING := Color(0.85, 0.7, 0.6)
const NIGHT := Color(0.22, 0.24, 0.42)

var state: Data = load("res://game/rooms/louka13/room_louka13.tres")


func _night() -> bool:
	return Globals.b_evening and not Globals.b_night1


func _on_room_entered() -> void:
	match C.player.last_room:
		"Potok13": C.player.position = get_hotspot("Potok").walk_to_point + Vector2(-80, 40)
		_: C.player.position = get_marker_position("Start")
	Globals.bring_sister(self)
	place("Joey", joey_spot())
	place("Tata", get_marker_position("Tata"))
	if _night():
		remove("Deda"); remove("Mama"); remove("Tonda")
	else:
		place("Deda", get_marker_position("Deda"))
		place("Mama", get_marker_position("Mama"))
		place("Tonda", get_marker_position("Tonda"))
	get_prop("Vrba").visible = Globals.b_night1
	get_prop("Pletivo").visible = Globals.b_tin
	hidden_thing(null, "Zaba", "b_frogs", 10, "")
	Globals.exit_arrow(self, "Potok", false, not _night())
	if _night():
		dark(NIGHT)


func _on_room_transition_finished() -> void:
	if not Globals.b_intro:
		await _intro()
	elif _night() and C.player != C.Hanka:
		await hand_over(C.Hanka, "Hani, ty máš baterku. Posviť ven.")
	else:
		await _maybe_cuts()


func joey_goal() -> Vector2:
	if not Globals.b_rock1: return get_hotspot("Potok").walk_to_point
	if not Globals.b_evening: return get_prop("Ohen").position + Vector2(-260, 60)
	if _night(): return get_hotspot("Vrby").walk_to_point
	if not Globals.b_stump: return get_prop("Vrba").position + Vector2(-300, 40)
	if not Globals.b_stick: return get_marker_position("Deda") + Vector2(-240, 30)
	if not Globals.b_saw: return get_prop("Polena").position + Vector2(-180, 0)
	if not Globals.b_knife: return Globals.sister().position + Vector2(-200, 20)
	if not Globals.b_joey: return Vector2.ZERO
	return get_hotspot("Potok").walk_to_point


func _intro() -> void:
	await C.Deda.say("Tady jsme kdysi stanovali s Klubem. Před padesáti lety!")
	await C.Alica.say("Dědo, ty jsi tu byl jako kluk?")
	await C.Deda.say("Byl. A můj stan stojí. Za minutu!")
	await C.Tata.say("Kde má ta tyčka začátek?!")
	await C.Tonda.say("Bětka už je u potoka. Kreslí.")
	Globals.b_intro = true


func on_click(node: Node) -> void:
	if await hidden_thing(node, "Zaba", "b_frogs", 10, "Žabka"):
		return
	match node.script_name:
		"Ohen": await _fire()
		"Polena": await _logs()
		"Stan": await _tent()
		"Vrby": await _willows()
		"Vrba": await _stump()
		"Pletivo":
			await C.player.walk_to_clicked()
			await C.player.say("Pletivo ochrání naše vrby. Ty u hráze nechte Hryzálkovi.")
		"Potok":
			await C.player.walk_to_clicked()
			if _night():
				await C.player.say("V noci k potoku sama nepůjdu.")
				return
			R.goto_room("Potok13")
		_: await super(node)


func on_character(chr: PopochiuCharacter, action: String, _item: PopochiuInventoryItem = null) -> bool:
	if action == "look":
		return false
	if chr == C.Alica or chr == C.Hanka:
		if Globals.b_stump and not Globals.b_knife:
			await _knife()
			return true
		return false
	if chr == C.Joey:
		if Globals.b_stump and not Globals.b_joey:
			await _joey()
			return true
		return false
	if _night():
		await C.player.say("Psst. Všichni spí.")
		return true
	await C.player.walk(chr.position + Vector2(-240, 20))
	match chr.script_name:
		"Deda":
			if Globals.b_stump and not Globals.b_stick:
				await _stick()
			elif not Globals.b_stump:
				await C.Deda.say("Ten starý stan má na sobě hvězdu. Ušili jsme ji v Klubu Hvězdička.")
			else:
				await C.Deda.say("Bez hole se mi chodí špatně. Najdete ji, detektivové?")
		"Tata":
			if Globals.b_stump and not Globals.b_saw:
				await _logs()
			elif not Globals.b_evening:
				await C.Tata.say("Mám novou pilku. Večer nařežu suché větve na oheň.")
			else:
				await C.Tata.say("Suché spadlé větve. Živé stromy se neřežou.")
		"Mama":
			if not Globals.b_evening:
				await C.Mama.say("Až Bětka dokreslí, uděláme oheň a opečeme buřty.")
			else:
				await C.Mama.say("Nejdřív stopy, pak snídaně. Detektivky!")
		"Tonda":
			if Globals.b_stump:
				await C.Tonda.say("Byl to vlkodlak! Určitě!")
				await C.Alica.say("Vlkodlaci nejsou. Nejdřív stopy. Kdo to byl, zjistí lupa!")
			else:
				await C.Tonda.say("Večer vám povím strašidelný příběh!")
		_: return false
	return true


#region Day 1 ######################################################################################
func _fire() -> void:
	await C.player.walk(get_prop("Ohen").position + Vector2(-260, 60))
	if _night():
		await C.player.say("Oheň dohořel. Všichni spí.")
		return
	if Globals.b_evening:
		await C.player.say("Ohniště. Ještě je teplé.")
		return
	if not Globals.b_rock1:
		await C.player.say("Ohniště. Večer si opečeme buřty! Ale kde je Bětka?")
		return
	await fade(_evening_set, "Večer…")
	await _evening()


func _evening_set() -> void:
	dark(EVENING, false)
	get_prop("Ohen").texture = load("res://assets/props/fire13.png")
	get_prop("Ohen").get_node("Sprite2D").texture = get_prop("Ohen").texture
	glow(get_prop("Ohen").position + Vector2(0, -60), Color(1.0, 0.6, 0.3), 1.4, 3.0)


func _evening() -> void:
	C.Tata.pose("saw")
	await C.Tata.say("Jen suché spadlé větve. Řez je rovný a hladký.")
	C.Tata.pose()
	C.Hanka.pose("stick")
	await C.Hanka.say("A já loupu klacík. Nožem!")
	await C.Mama.say("Opatrně, Hani.")
	await C.Tonda.say("…a v lese žije VLKODLAK!")
	await C.Deda.say("Vlkodlaci nejsou. Dost strašení. Buřty jsou hotové!")
	C.Hanka.pose()
	I.Klacik.add()
	await C.Hanka.say("Můj klacík si dám do kapsy.")
	Globals.b_evening = true
	await fade(_night_set, "Noc…")
	await hand_over(C.Hanka, "Hani, ty máš baterku. Posviť ven.")
	await C.Hanka.say("Musím čůrat… Posvítím si baterkou.")
	sfx("ŠPLOUCH…", Vector2(1720, 520), 60)
	await C.Hanka.say("U vrb něco šplouchá!")


func _night_set() -> void:
	for n in get_children():
		if n is CanvasModulate or n is PointLight2D:
			n.queue_free()
	remove("Deda"); remove("Mama"); remove("Tonda")
	dark(NIGHT)
	Globals.show_exit(self, "Potok", false)


func _willows() -> void:
	await C.player.walk_to_clicked()
	if _night():
		if C.player != C.Hanka:
			await hand_over(C.Hanka, "Hani, posviť tam baterkou.")
		await C.Hanka.say("Kdo je tam?")
		sfx("PLESK!", Vector2(1680, 560))
		await C.Hanka.say("Tati! V potoce je drak! Viděla jsem dvě svítící oči!")
		await C.Tata.say("To byla ryba. Spinkej.")
		await C.Hanka.say("Ryba se svítícíma očima?")
		Globals.b_night1 = true
		Globals.b_day = 2
		await fade(_morning, "Ráno…")
		await C.Hanka.say("Alico! Vstávej! U vrb se něco stalo!")
		return
	if Globals.b_night1:
		await C.player.say("U potoka chybí jedna vrba!")
	else:
		await C.player.say("Mladé vrby u potoka.")


func _morning() -> void:
	light_up(0.1)
	place("Deda", get_marker_position("Deda"))
	place("Mama", get_marker_position("Mama"))
	place("Tonda", get_marker_position("Tonda"))
	get_prop("Ohen").texture = load("res://assets/props/fire13_out.png")
	get_prop("Ohen").get_node("Sprite2D").texture = get_prop("Ohen").texture
	get_prop("Vrba").show()
	Globals.show_exit(self, "Potok", true)


func _tent() -> void:
	await C.player.walk_to_clicked()
	if _night():
		await C.player.say("Děda chrápe. Chrrr…")
	elif Globals.b_stump and not Globals.b_stick:
		await C.player.walk(get_marker_position("Deda") + Vector2(-240, 30))
		await _stick()
	else:
		await C.player.say("Dědův starý stan z Klubu. Na štítu má hvězdu.")
#endregion


#region Day 2: the case ###########################################################################
func _stump() -> void:
	await C.player.walk(get_prop("Vrba").position + Vector2(-300, 40))
	if Globals.b_stump:
		await C.player.say("Pahýl jako ořezaná tužka. A kolem třísky.")
		return
	await C.Alica.say("Vrba spadla! Někdo ji v noci pokácel!")
	await C.Alica.say("Pahýl je špičatý jako tužka. A kolem jsou třísky.")
	C.Alica.pose("lens")
	await C.Alica.say("Podívám se lupou… Dva velké zuby vedle sebe! A ostré jako dláto!")
	C.Alica.pose()
	Globals.b_stump = true
	if not Globals.b_stick:
		await C.player.walk(get_marker_position("Deda") + Vector2(-240, 30))
		await _stick()
	else:
		await _case()


func _stick() -> void:
	await C.Deda.say("Kde je moje hůl? Večer stála u stanu!")
	await C.Alica.say("Taky zmizela? To je divné.")
	Globals.b_stick = true
	await _case()


func _case() -> void:
	if not (Globals.b_stump and Globals.b_stick):
		return
	await C.Alica.say("Zakládám případ číslo třináct: Stopy u potoka!")
	await C.Hanka.say("A já svítím baterkou!")
	await C.Alica.say("Kdo mohl strom pokácet? Táta má pilku, Hanka nožík a Joey rád kouše klacky.")


func _logs() -> void:
	await C.player.walk(get_prop("Polena").position + Vector2(-180, 0))
	if not Globals.b_stump or Globals.b_saw:
		await C.player.say("Polena z večera. Řez je rovný a hladký.")
		return
	C.Alica.pose("lens")
	await C.Alica.say("Pilka řeže rovně. Ale pahýl je špičatý jako tužka!")
	C.Alica.pose()
	await C.Tata.say("Vidíš? Já to nebyl.")
	Globals.b_saw = true
	await _maybe_cuts()


func _knife() -> void:
	await C.Alica.say("Hani, ty máš nožík. Neloupala jsi v noci vrbu?")
	await C.Hanka.say("Já bych strom neuměla pokácet!")
	C.Alica.pose("lens")
	await C.Alica.say("Máš v kapse dlouhé tenké kudrlinky. U pahýlu jsou krátké tlusté třísky.")
	C.Alica.pose()
	await C.Alica.say("Já vím, Hani. Promiň.")
	await C.Hanka.say("Tak jo. Opička ti odpouští taky.")
	Globals.b_knife = true
	await _maybe_cuts()


func _joey() -> void:
	await C.player.walk(C.Joey.position + Vector2(-220, 20))
	await C.Alica.say("Joey, to jsi byl ty? Ten klacek máš celý okousaný.")
	await C.Joey.say("Haf?")
	C.Alica.pose("lens")
	await C.Alica.say("Pejsek dělá zoubky malé dírky. Ne velké rýhy.")
	C.Alica.pose()
	await C.Hanka.say("Joey je hodný. A do vody se mu nechce!")
	Globals.b_joey = true
	await _maybe_cuts()


func _maybe_cuts() -> void:
	if not (Globals.b_saw and Globals.b_knife and Globals.b_joey) or Globals.b_cuts:
		return
	await C.Alica.say("Porovnám všechny stopy na dřevě. Čím to bylo?")
	var mg: CanvasLayer = CutsGame.new()
	add_child(mg)
	await mg.finished
	Globals.b_cuts = true
	await C.Alica.say("Pilka ne, nožík ne, Joey ne. Někdo s velkými zuby!")
	await C.Tata.say("Projedeme se na kole podél potoka. Třeba někoho potkáme.")
#endregion
