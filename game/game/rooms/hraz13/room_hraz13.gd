@tool
extends "res://game/shared/story_room.gd"
## Story 13, upstream: the creek widens into a little pond behind a dam of branches and mud, with děda's stick
## woven in. The hajný: a young beaver (facts, "Pravda, nebo ne?", "Hráz pro bobra"). Dusk: Hryzálek swims up,
## Joey gets splashed, Hanka names him and gives him her stick. Morning: the water below the dam is lower and
## the old Klub tin shows under the footbridge; Věrka comes with buchty. XIV.

const Data := preload('room_hraz13_state.gd')
const QuizGame := preload("res://game/minigames/quiz_13.gd")
const DamGame := preload("res://game/minigames/dam.gd")
const DUSK := Color(0.42, 0.38, 0.6)

var state: Data = load("res://game/rooms/hraz13/room_hraz13.tres")


func _dusk() -> bool:
	return Globals.b_damgame and not Globals.b_gift


func _on_room_entered() -> void:
	C.player.position = get_marker_position("Start")
	Globals.bring_sister(self, Vector2(170, 10))
	place("Joey", get_marker_position("Joey"))
	place("Deda", get_marker_position("Deda"))
	place("Tonda", get_marker_position("Tonda"))
	if Globals.b_dam:
		place("Hajny", get_marker_position("Hajny"))
	else:
		remove("Hajny")
	if Globals.b_gift:
		place("Verka", get_marker_position("Verka"))
	else:
		remove("Verka")
	get_prop("Plave").visible = _dusk() and not Globals.b_beaver
	get_prop("Bobr").visible = _dusk() and Globals.b_beaver
	get_prop("Plechovka").visible = Globals.b_gift and not Globals.b_tin
	hidden_thing(null, "Zaba", "b_frogs", 10, "")
	Globals.exit_arrow(self, "Potok", true, not _dusk())
	if _dusk():
		dark(DUSK)


func _on_room_transition_finished() -> void:
	if not Globals.b_dam:
		await _arrive()
	elif _dusk() and C.player != C.Hanka:
		await hand_over(C.Hanka, "Teď ty, Hanko. Jen trošku posviť.")


func joey_goal() -> Vector2:
	if not Globals.b_hajny or not Globals.b_damgame: return get_marker_position("Hajny") + Vector2(-260, 30)
	if _dusk(): return Vector2(1300, 860)
	if not Globals.b_tin: return get_hotspot("Lavka").walk_to_point
	return Vector2.ZERO


func _arrive() -> void:
	await C.Alica.say("Tady je z potoka najednou rybníček!")
	await C.Hanka.say("Hráz! Z větví a z bláta!")
	await C.Deda.say("Moje hůl! Pořád má hvězdu z Klubu.")
	await C.Alica.say("Je oloupaná. Někdo z ní okousal kůru.")
	Globals.b_dam = true
	place("Hajny", Vector2(1860, 900))
	await C.Hajny.walk(get_marker_position("Hajny"))
	await C.Alica.say("Pan hajný!")
	await C.Hajny.say("Dobrý den, detektivové. Vidím, že jste našli hráz.")


func on_click(node: Node) -> void:
	if await hidden_thing(node, "Zaba", "b_frogs", 10, "Žabka"):
		return
	match node.script_name:
		"Hraz":
			if _dusk():
				await _beaver()
				return
			await C.player.walk(Vector2(1040, 860))
			await C.player.say("Hráz z větví, bláta a kamenů. A v ní dědova hůl.")
		"Hrad":
			await C.player.walk_to_clicked()
			await C.player.say("Hromada větví a bláta ve vodě. To je bobří hrad.")
		"Plave", "Bobr": await _beaver()
		"Plechovka", "Lavka": await _tin()
		"Potok":
			await C.player.walk_to_clicked()
			if _dusk():
				await C.player.say("Teď ne! Čekáme potichu na bobra.")
				return
			R.goto_room("Potok13")
		_: await super(node)


func on_item(node: Node, item: PopochiuInventoryItem) -> void:
	if item == I.Klacik and node.script_name in ["Bobr", "Plave", "Hraz"] and Globals.b_beaver:
		I.deselect_active()
		await _gift()
		return
	await super(node, item)


func on_character(chr: PopochiuCharacter, action: String, _item: PopochiuInventoryItem = null) -> bool:
	if action == "look" or chr == C.Alica or chr == C.Hanka or chr == C.Joey:
		return false
	await C.player.walk(chr.position + Vector2(-240, 20))
	match chr.script_name:
		"Hajny": await _hajny()
		"Deda": await C.Deda.say("Moji hůl si nech, Hryzálku. Udělám si novou.")
		"Tonda":
			if Globals.b_beaver:
				await C.Tonda.say("Bobr! Lepší než vlkodlak!")
			else:
				await C.Tonda.say("Takže žádný vlkodlak…")
		"Verka": await _tin()
		_: return false
	return true


#region The hajný ##################################################################################
func _hajny() -> void:
	if not Globals.b_hajny:
		await C.Hajny.say("Tu hráz postavil bobr. Mladý bobr.")
		await C.Alica.say("Bobr?!")
		await C.Hanka.say("Jako v pohádce?")
		await slideshow([
			["b_young", "Hajny", "Bobří rodina bydlí dole u starého rybníka. Mladý bobr se letos vydal hledat vlastní potok."],
			["b_young", "Hajny", "A tady si staví první hráz a nový domov."],
			["b_teeth", "Hajny", "Má oranžové zuby. Jsou tvrdé, protože v nich je železo. Okusuje strom dokola, až je z něj tužka."],
			["b_lodge", "Hajny", "Jeho hrad má vchod pod vodou. Tam se liška nedostane. Proto bobr potřebuje vysokou vodu."],
			["b_tail", "Hajny", "A když se lekne, plácne ocasem o vodu. PLESK! To znamená: pozor, nebezpečí!"],
		])
		await C.Alica.say("A Franta myslel, že mu ryby žere vydra!")
		await C.Hajny.say("Bobr ryby nejí. Jen kůru, větvičky a listí.")
		Globals.b_hajny = true
	if not Globals.b_quiz:
		await C.Hajny.say("Tak, detektivové. Co jste si zapamatovali?")
		var quiz: CanvasLayer = QuizGame.new()
		add_child(quiz)
		await quiz.finished
		Globals.b_quiz = true
		await C.Hajny.say("Výborně! A víte, proč bobr postavil hráz zrovna tady?")
	if not Globals.b_damgame:
		await _dam_game()
		return
	if _dusk():
		await C.Hajny.say("Potichu… A nesvítit, dokud neřeknu.")
		return
	await C.Hajny.say("Pletivo ochrání vaše vrby u stanů. Ty u hráze nechte jemu.")


func _dam_game() -> void:
	await C.Hajny.say("Bobr staví hráz tam, kde je údolí úzké. Voda musí zakrýt vchod do jeho hradu. Ale vaše stany musí zůstat v suchu!")
	await C.Hajny.say("Zkuste to jako on. Tady mám mapu.")
	var mg: CanvasLayer = DamGame.new()
	add_child(mg)
	await mg.finished
	Globals.b_damgame = true
	await C.Hajny.say("Přesně tak by to udělal bobr. Počkáme do večera. Potichu.")
	await fade(_dusk_set, "Večer…")
	await hand_over(C.Hanka, "Teď ty, Hanko. Jen trošku posviť.")


func _dusk_set() -> void:
	dark(DUSK)
	get_prop("Plave").show()
	Globals.show_exit(self, "Potok", false)
#endregion


#region Dusk: Hryzálek #############################################################################
func _beaver() -> void:
	if not _dusk():
		return
	if C.player != C.Hanka:
		await hand_over(C.Hanka, "Teď ty, Hanko. Jen trošku posviť.")
	await C.Hanka.walk(Vector2(1150, 880))
	if not Globals.b_beaver:
		await C.Hanka.say("Někdo plave! S větví v puse!")
		get_prop("Plave").hide()
		await pop("Bobr")
		await C.Alica.say("Bobr si sedl na hráz. A okusuje kůru. Jako kukuřici!")
		await C.Hanka.say("On papá!")
		await C.Joey.walk(Vector2(900, 900))
		await C.Joey.say("Haf!")
		sfx("PLESK!", get_prop("Bobr").position + Vector2(0, 40))
		await C.Alica.say("Chudák Joey! Bobr ho postříkal!")
		await C.Hanka.say("Bude se jmenovat Hryzálek!")
		await C.Hajny.say("Hryzálek. To se mi líbí.")
		Globals.b_beaver = true
		await C.Hanka.say("Mám pro něj dárek. Můj loupaný klacík!")
		return
	await _gift()


func _gift() -> void:
	if Globals.b_gift:
		return
	if C.player != C.Hanka:
		await hand_over(C.Hanka, "Dej mu ho ty, Hani.")
	await C.Hanka.walk(Vector2(1150, 880))
	await C.Hanka.say("Tady máš dárek, Hryzálku. Ten je ode mě.")
	if I.Klacik.in_inventory:
		I.Klacik.remove()
	Globals.b_gift = true
	await fade(_morning, "Ráno…")
	await C.Alica.say("Pod hrází je voda nižší. A pod lávkou něco je!")


func _morning() -> void:
	light_up(0.1)
	get_prop("Bobr").hide()
	get_prop("Plave").hide()
	get_prop("Plechovka").show()
	place("Verka", get_marker_position("Verka")).pose("buchty")
	Globals.show_exit(self, "Potok", true)
#endregion


#region The tin ####################################################################################
func _tin() -> void:
	if not Globals.b_gift:
		await C.player.walk_to_clicked()
		await C.player.say("Stará lávka. Prkna jsou šedivá a ztrouchnivělá.")
		return
	if Globals.b_tin:
		return
	await C.player.walk(get_hotspot("Lavka").walk_to_point)
	await C.Alica.say("Plechovka! Celá rezavá.")
	await C.Verka.say("Nesu buchty! Co to máte?")
	await C.Deda.say("Věrko… to je naše plechovka z Klubu!")
	get_prop("Plechovka").hide()
	await slideshow([
		["b_tin", "Verka", "Klubová hvězda. A fotka. To jsme my, tady na louce!"],
		["b_tin", "Deda", "To jsme sem schovali před padesáti lety!"],
		["b_tin", "Alica", "Věž… hvězda… a čtrnáctka: XIV."],
		["b_tin", "Alica", "„Další poklad je na…“ Kde?! Je to utržené!"],
	])
	Globals.b_tin = true
	await C.Hanka.say("Hryzálek si vzal můj dárek. A my máme jeho poklad!")
	await C.Alica.say("Tohle byl náš nejmokřejší případ!")
	await the_end("Konec 13. dílu")
#endregion
