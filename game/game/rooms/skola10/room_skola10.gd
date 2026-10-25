@tool
extends "res://game/shared/story_room.gd"
## Story 10, the forest school meadow. Monday (Alica with her class, Hanka is at školka): the hutch is open,
## Míša and Šiša are gone; the broken latch and wood shavings; big holínky prints to the log building; the
## hay trail to the hedgehog's nest with a torn note "…V TEPLE. K."; malý Karel; the locked kumbál and the
## empty hat hook; táta comes with a box with air holes. Tuesday's field day: Hanka's rustling bag makes the
## guinea pigs wheek behind the kumbál door; pan Karel; the new hutch (minigame); pens on the meadow for the
## pupils' own guinea pigs (minigame).

const Data := preload('room_skola10_state.gd')
const HutchGame := preload("res://game/minigames/hutch.gd")
const PensGame := preload("res://game/minigames/pens.gd")

var state: Data = load("res://game/rooms/skola10/room_skola10.tres")


func _on_room_entered() -> void:
	C.player.position = get_marker_position("Srub") + Vector2(-200, 60) if C.player.last_room == "Kumbal10" else get_marker_position("Start")
	if Globals.q_day == 2:
		Globals.bring_sister(self, Vector2(170, 10))
		place("Mama", Vector2(400, 940))
		place("Tata", get_marker_position("Tata"))
		remove("MalyKarel")
	else:
		remove("Hanka")
		place("MalyKarel", get_marker_position("Karel"))
		remove("Mama")
		remove("Tata")
	place("Lucie", get_marker_position("Lucie"))
	if Globals.q_found:
		place("Skolnik", Vector2(950, 960))
	else:
		remove("Skolnik")
	if Globals.q_box or Globals.q_day == 2:
		place("Joey", Vector2(1650, 1000))
	else:
		remove("Joey")
	get_prop("Kotec").visible = not Globals.q_new
	get_prop("NovyKotec").visible = Globals.q_new
	get_prop("Jezek").visible = Globals.q_nest


func _on_room_transition_finished() -> void:
	if not Globals.q_intro:
		await _intro()
	elif Globals.q_new and not Globals.game_finished:
		await _finish()
	elif Globals.q_wheek and not Globals.q_found:
		await _karel_comes()
	elif Globals.q_day == 1 and not Globals.q_box:
		await _monday_done()
	elif Globals.phase == "q_fieldday":
		Globals.phase = ""
		_card(["Úterý. Brigáda!"], 1.6)
		await get_tree().create_timer(2.0).timeout
		await C.Lucie.say("Dneska stavíme nový kotec. Ale pana Karla pořád nikdo neviděl.")
		await C.Hanka.say("Já mám v sáčku mrkvičky. Pro Míšu a Šišu, až se najdou.")


func joey_goal() -> Vector2:
	if Globals.q_day == 2 and not Globals.q_wheek:
		return get_marker_position("Srub")
	if Globals.q_found and not Globals.q_new:
		return get_prop("Kotec").position + Vector2(-300, 200)
	return get_marker_position("Srub")


func _intro() -> void:
	_card(["Pondělí ráno v lesní škole."], 1.8)
	await get_tree().create_timer(2.2).timeout
	await C.Lucie.say("Děti, stalo se něco smutného. Kotec je otevřený. Míša a Šiša jsou pryč.")
	await C.MalyKarel.say("Stella pláče…")
	await C.Lucie.say("Ale máme ve třídě detektivku! Alico, povedeš pátrání?")
	C.Alica.pose("lens")
	await C.Alica.say("Ano! Hledáme stopy!")
	C.Alica.pose()
	Globals.q_intro = true


func on_click(node: Node) -> void:
	match node.script_name:
		"Kotec": await _hutch()
		"NovyKotec":
			await C.player.walk_to_clicked(Vector2(-300, 200))
			await C.player.say("Nový kotec! MÍŠA a ŠIŠA. A západka, kterou ježek neotevře.")
		"Stopy": await _prints()
		"Seno", "Hromada", "Jezek": await _nest()
		"Srub": await _door()
		"Hacek": await _hook()
		"Spoluzaci":
			await C.player.walk_to_clicked(Vector2(200, 160))
			await C.player.say("Julča má lupu, Beatka kreslí a Stella se bojí o morčátka.")
		_: await super(node)


func on_character(chr: PopochiuCharacter, action: String, _item: PopochiuInventoryItem = null) -> bool:
	if action == "look" or chr == C.Alica or chr == C.Hanka:
		return false
	match chr.script_name:
		"MalyKarel": await _karel()
		"Lucie":
			await C.player.walk(chr.position + Vector2(-240, 20))
			if Globals.q_day == 1 and not Globals.q_hutch:
				await C.Lucie.say("Podívej se nejdřív na kotec, Alico.")
			elif Globals.q_day == 1 and not Globals.q_prints:
				await C.Lucie.say("Na zemi bývají stopy. Kam vedou?")
			elif Globals.q_day == 1 and not Globals.q_nest:
				await C.Lucie.say("Co je v té hromadě klestí? Něco tam šustí.")
			elif Globals.q_day == 1 and not Globals.q_karel:
				await C.Lucie.say("Zeptej se spolužáků. Třeba malého Karla.")
			else:
				await C.Lucie.say("Klíč od kumbálu má jen pan Karel. A nebere telefon. Asi je v lese na dříví.")
		"Tata":
			await C.player.walk(chr.position + Vector2(-260, 20))
			await C.Tata.say("Krabice? To je překvapení. Na brigádu!" if not Globals.q_new else "Dobrá práce, stavitelky!")
		"Mama":
			await C.player.walk(chr.position + Vector2(240, 20))
			await C.Mama.say("Hani, ukaž mrkvičky. Šustí to!")
		"Skolnik":
			await C.player.walk(chr.position + Vector2(-260, 20))
			if Globals.q_found and not Globals.q_new:
				await _build()
			else:
				await C.Skolnik.say("Teď už se v novém kotci nebudou bát mrazu.")
		"Joey":
			if Globals.q_box and Globals.q_day == 1:
				await C.Joey.walk(get_marker_position("Srub") + Vector2(80, 30))
				await C.Joey.say("Haf! Haf!")
				await C.Tata.say("Joey, k ježkovi! Tam je seno. Ty ses spletl.")
				return true
			return false
		_: return false
	return true


#region Monday ######################################################################################
func _hutch() -> void:
	await C.player.walk(get_prop("Kotec").position + Vector2(-320, 200))
	if Globals.q_found:
		await _build()
		return
	if Globals.q_hutch:
		await C.player.say("Prázdný kotec. Rozbitá západka a hobliny.")
		return
	C.Alica.pose("lens")
	await C.Alica.say("Západka je rozbitá. Dvířka se nedají zavřít.")
	await C.Alica.say("A uvnitř jsou hobliny. Kudrnaté hobliny… jako u táty v dílně!")
	C.Alica.pose()
	Globals.q_hutch = true
	await _monday_done()


func _prints() -> void:
	await C.player.walk_to_clicked(Vector2(-260, -20))
	if Globals.q_prints:
		await C.player.say("Velké holínky s vroubky. Vedou ke srubu.")
		return
	C.Alica.pose("lens")
	await C.Alica.say("Velké stopy od holínek. Podrážka má vroubky jako rybí kostička.")
	await C.Alica.say("Moje jsou malé. Tátovy boty mají čtverečky. Tyhle jsou jiné.")
	await C.Alica.say("A nevedou po seně. Vedou ke srubu!")
	C.Alica.pose()
	Globals.q_prints = true
	await _monday_done()


func _nest() -> void:
	await C.player.walk(get_hotspot("Hromada").walk_to_point)
	if Globals.q_nest:
		await C.player.say("Ježkův pelíšek. Seno a papírek.")
		return
	await C.Alica.say("Stopa ze sena vede až sem, do hromady klestí.")
	await pop("Jezek")
	await C.MalyKarel.say("Ježek! Má v puse seno!")
	await C.Lucie.say("Ježci se teď na jaře budí. A staví si pelíšek z měkkého sena.")
	await C.Alica.say("V pelíšku je papírek! Roztržený.")
	await picture("res://assets/slides/torn_note10.png", "Roztržený papírek")
	await C.Alica.say("…jsou u mě v teple. K.")
	await C.Alica.say("Ježek je moc malý, morče by neodnesl. Ale někdo napsal: v teple! A podepsal se K.")
	Globals.q_nest = true
	await _monday_done()


func _karel() -> void:
	await C.player.walk(C.MalyKarel.position + Vector2(240, 20))
	if not Globals.q_nest:
		await C.MalyKarel.say("Já bych si Míšu a Šišu vzal domů. Kdyby to šlo.")
		return
	if Globals.q_karel:
		await C.MalyKarel.say("Já to nebyl! Fakt!")
		return
	await C.Alica.say("Karle… Na papírku je K. A ty máš v kapse seno!")
	await C.MalyKarel.say("Seno je od mého králíka! A v neděli jsem byl celý den u babičky.")
	await C.MalyKarel.say("A já píšu K. úplně jinak. Koukej.")
	await C.Alica.say("Máš pravdu. Promiň. Škrtám.")
	await C.Alica.say("Ale kdo je ještě K.?")
	Globals.q_karel = true
	await _monday_done()


func _door() -> void:
	await C.player.walk(get_marker_position("Srub"))
	if Globals.q_day == 2 and not Globals.q_wheek:
		await _wheek()
		return
	if Globals.q_wheek and not Globals.q_found:
		await _karel_comes()
		return
	if Globals.q_found:
		R.goto_room("Kumbal10")
		return
	await C.player.say("Dveře do kumbálu. Zamčeno.")
	if not Globals.q_door:
		await C.Lucie.say("Klíč od kumbálu má jen pan Karel. A nebere telefon. Asi je v lese na dříví.")
		Globals.q_door = true
		await _monday_done()


func _hook() -> void:
	await C.player.walk(get_marker_position("Srub") + Vector2(100, 0))
	await C.Alica.say("Háček na čepici pana Karla. Je prázdný.")
	if not Globals.q_door:
		Globals.q_door = true
		await _monday_done()


func _monday_done() -> void:
	if Globals.q_day != 1 or Globals.q_box:
		return
	if not (Globals.q_hutch and Globals.q_prints and Globals.q_nest and Globals.q_karel and Globals.q_door):
		return
	await C.Lucie.say("Je čas jít domů. Pro Alicu přijel táta.")
	place("Tata", Vector2(2050, 930))
	place("Joey", Vector2(2150, 1000))
	C.Tata.ignore_walkable_areas = true
	C.Joey.ignore_walkable_areas = true
	C.Joey.walk(get_marker_position("Srub") + Vector2(80, 30))
	await C.Tata.walk(get_marker_position("Tata"))
	C.Tata.ignore_walkable_areas = false
	C.Joey.ignore_walkable_areas = false
	await C.Joey.say("Haf! Haf!")
	await C.Tata.say("Joey, tam je zamčeno. Pojď, jedeme.")
	C.Tata.pose("box")
	await C.Alica.say("Tati, co je v té velké krabici? Má dírky!")
	await C.Tata.say("To je překvapení. Na zítřejší brigádu.")
	C.Tata.pose()
	await C.Alica.say("Hobliny… a krabice s dírkami na dýchání. Tati?!")
	Globals.q_box = true
	Globals.phase = "q_evening"
	R.goto_room("Domov10")
#endregion


#region Tuesday #####################################################################################
func _wheek() -> void:
	await hand_over(C.Hanka, "Zamčeno. Hani, nechceš to zkusit ty?")
	C.Hanka.pose("bag")
	sfx("ŠUST ŠUST", Vector2(900, 560), 70)
	await get_tree().create_timer(0.8).timeout
	sfx("UÍÍÍK! UÍÍÍK!", Vector2(960, 420), 90)
	await C.Hanka.say("Uííík! To jsou Míša a Šiša! Jsou v kumbálu!")
	C.Hanka.pose()
	await C.Alica.say("Morčata pískají, když šustí sáček s jídlem!")
	Globals.q_wheek = true
	await _karel_comes()


func _karel_comes() -> void:
	place("Skolnik", Vector2(2050, 930))
	C.Skolnik.ignore_walkable_areas = true
	await C.Skolnik.walk(Vector2(950, 960))
	C.Skolnik.ignore_walkable_areas = false
	await C.Skolnik.say("Dobré ráno! Co se tu děje? Proč jsou všichni u kumbálu?")
	await C.Alica.say("Pane Karle! Vy jste K.! Velký Karel!")
	await C.Skolnik.say("Velký Karel? No jasně. Pojďte, odemknu.")
	Globals.q_found = true
	R.goto_room("Kumbal10")


func _build() -> void:
	await C.Skolnik.say("Starý kotec má rozbitou západku. Postavíme nový. Táta přivezl dílky!")
	await C.Tata.say("V té krabici s dírkami byly díly nového kotce. Překvapení!")
	var mg: CanvasLayer = HutchGame.new()
	add_child(mg)
	await mg.finished
	Globals.q_new = true
	get_prop("Kotec").hide()
	await pop("NovyKotec")
	await C.Hanka.say("Napíšeme na něj MÍŠA a ŠIŠA!")
	await _finish()


## After the new hutch (also resumed here if the game was left in the middle of it).
func _finish() -> void:
	if not Globals.q_pens:
		await C.Lucie.say("Na brigádu si děti přinesly i svoje morčata z domova. Každé chce na louce svou ohrádku!")
		var pens: CanvasLayer = PensGame.new()
		add_child(pens)
		await pens.finished
		Globals.q_pens = true
	await C.Skolnik.say("A ježek dostane vlastní hromádku sena. Ať si pelíšek dostaví.")
	await C.Alica.say("Případ vyřešen. Velký Karel byl hodný Karel.")
	await the_end("Konec 10. dílu")
#endregion
