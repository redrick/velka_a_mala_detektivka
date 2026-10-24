@tool
extends "res://game/shared/story_room.gd"
## Story 7, the snowy garden, told by Joey. Morning (Joey's slides): babička's cold hands at the feeder,
## the glove on the post (Joey takes it), děda shovels the snow onto a pile, the kids build a fort from it.
## Evening: the ring is gone; the feeder (shovelled), the glove gone too, Joey suspected, his stash dug up;
## Tonda's magpie. Next day: "Kde je prstýnek?", Joey tells them with a paw and a stare, and sniffs the ring
## out of the fort wall (minigame).

const Data := preload('room_zahrada7_state.gd')
const WhereGame := preload("res://game/minigames/who_7.gd")
const SniffGame := preload("res://game/minigames/sniff.gd")
const EVENING := Color(0.45, 0.47, 0.68)

var state: Data = load("res://game/rooms/zahrada7/room_zahrada7.tres")


func _on_room_entered() -> void:
	match C.player.last_room:
		"Les7": C.player.position = get_marker_position("ZLesa")
		_: C.player.position = get_marker_position("Start")
	Globals.bring_sister(self, Vector2(170, 10))
	place("Joey", joey_spot()).pose("sad" if Globals.j_stash and not Globals.j_ring else "")
	if Globals.j_case and not Globals.j_straka:
		place("Babicka", Vector2(820, 940))
	elif Globals.j_straka:
		place("Babicka", Vector2(780, 950))
		place("Betka", Vector2(1150, 990))
	else:
		remove("Babicka")
	if Globals.j_stash and not Globals.j_tonda:
		place("Tonda", Vector2(1500, 940))
	else:
		remove("Tonda")
	if not Globals.j_straka:
		remove("Betka")
	get_prop("Skrys").visible = Globals.j_stash
	get_prop("Prstynek").visible = false
	if Globals.j_case and not Globals.j_straka and C.player.last_room != "Les7":
		dark(EVENING)
	Globals.exit_arrow(self, "KLesu", false, Globals.j_tonda)
	get_hotspot("KLesu").clickable = Globals.j_tonda


func _on_room_transition_finished() -> void:
	if not Globals.j_morning:
		await _morning()


func joey_goal() -> Vector2:
	if not Globals.j_case: return get_hotspot("Dum").walk_to_point
	if not Globals.j_feeder: return get_hotspot("Krmitko").walk_to_point
	if not Globals.j_stash: return get_hotspot("Kulna").walk_to_point
	if not Globals.j_tonda: return C.Tonda.position + Vector2(-240, 40)
	if not Globals.j_straka: return Vector2(1760, 960)
	return get_marker_position("Pevnost") + Vector2(160, 20)


func _morning() -> void:
	_card(["Ahoj. Já jsem Joey.", "Dneska vám vyprávím já."], 3.0)
	await get_tree().create_timer(3.4).timeout
	await slideshow([
		["j_feeder", "Joey", "Ráno babička krmila ptáčky. Říkala: Mám studené ruce, prstýnek mi padá."],
		["", "Joey", "Rukavici si položila na sloupek. Voněla babičkou…"],
		["j_glove", "Joey", "Tak jsem si ji vzal. A zakopal do své skrýše u kůlny. Pssst!"],
		["j_shovel", "Joey", "Pak děda odházel sníh od krmítka na velkou hromadu."],
		["j_fort", "Joey", "A odpoledne holky, Bětka a Tonda postavili z hromady sněhovou pevnost."],
		["", "Joey", "A večer… Večer se stalo něco hrozného. Pojďte domů!"],
	])
	Globals.j_morning = true


func on_click(node: Node) -> void:
	match node.script_name:
		"Krmitko": await _feeder()
		"Kulna", "Skrys": await _stash()
		"Pevnost": await _fort()
		"Dum":
			await C.player.walk_to_clicked()
			R.goto_room("Kuchyne7")
		"KLesu":
			await C.player.walk_to_clicked()
			R.goto_room("Les7")
		_: await super(node)


func on_character(chr: PopochiuCharacter, action: String, _item: PopochiuInventoryItem = null) -> bool:
	if action == "look" or chr == C.Alica or chr == C.Hanka:
		return false
	match chr.script_name:
		"Joey":
			if Globals.j_straka and not Globals.j_ring:
				await _fort()
				return true
			return false
		"Tonda":
			await C.player.walk(chr.position + Vector2(-240, 20))
			await _tonda()
		"Babicka":
			await C.player.walk(chr.position + Vector2(240, 20))
			await C.Babicka.say("Prstýnek od dědy, s hvězdičkou. Ráno jsem ho ještě měla…" if not Globals.j_ring else "Joey má nejlepší nos ze všech!")
		"Betka":
			await C.player.walk(chr.position + Vector2(-240, 20))
			await C.Betka.say("Bloky do pevnosti jsme řezali z té velké hromady.")
		_:
			return false
	return true


#region Evening: the feeder, the glove, the stash ####################################################
func _feeder() -> void:
	await C.player.walk(get_hotspot("Krmitko").walk_to_point)
	if not Globals.j_case:
		await C.player.say("Krmítko. Sýkorky zobou semínka.")
		return
	if Globals.j_feeder:
		await C.player.say("U krmítka nic. Sníh je odházený.")
		return
	if C.player == C.Hanka:
		C.Hanka.pose("torch")
		await C.Hanka.say("Svítím… Nic. Jenom udusaný sníh.")
	else:
		C.Alica.pose("lens")
		await C.Alica.say("Nic. Sníh je odházený až na zem.")
	C.player.pose()
	await C.Babicka.say("A moje rukavice je taky pryč! Nechala jsem ji tady na sloupku.")
	await C.Alica.say("Rukavice zmizela… A prstýnek byl možná v ní! Kdo bere rukavice?")
	await C.Alica.say("Joey!")
	C.Joey.pose("sad")
	await C.Joey.say("Kňuk.")
	Globals.j_feeder = true
	Globals.j_glove = true
	await C.Hanka.say("Joey má skrýš u kůlny!")


func _stash() -> void:
	await C.player.walk(get_hotspot("Kulna").walk_to_point)
	if not Globals.j_glove:
		await C.player.say("Kůlna na dříví.")
		return
	if Globals.j_stash:
		await C.player.say("Joeyho skrýš: rukavice, kost a Hančina stará ponožka. Prstýnek ne.")
		return
	await C.Hanka.say("Joey vždycky něco schovává pod kůlnou. Tady!")
	sfx("HRAB HRAB", Vector2(1580, 600), 60)
	await pop("Skrys")
	await C.Alica.say("Babiččina rukavice! A kost. A… Hančina ponožka z podzimu!")
	C.Alica.pose("lens")
	await C.Alica.say("Ale v rukavici žádný prstýnek není.")
	C.Alica.pose()
	await C.Hanka.say("Joey to nebyl. Je smutný.")
	await C.Joey.say("Kňuk…")
	Globals.j_stash = true
	place("Tonda", Vector2(2050, 940))
	C.Tonda.ignore_walkable_areas = true
	await C.Tonda.walk(Vector2(1500, 940))
	C.Tonda.ignore_walkable_areas = false
	await _tonda()


func _tonda() -> void:
	if Globals.j_tonda:
		await C.Tonda.say("Straka letěla k lesu. K hájovně!")
		return
	await C.Tonda.say("Co hledáte? Prstýnek? Odpoledne jsem viděl straku! Nesla něco lesklého k lesu!")
	await C.Alica.say("Straky kradou lesklé věci! Zítra ráno půjdeme za panem hajným.")
	Globals.j_tonda = true
	Globals.show_exit(self, "KLesu")
	get_hotspot("KLesu").clickable = true
#endregion


#region Next day: where is it, the fort ##############################################################
func _fort() -> void:
	await C.player.walk(get_marker_position("Pevnost"))
	if not Globals.j_straka:
		await C.player.say("Naše sněhová pevnost! Má i vlajku.")
		return
	if Globals.j_ring:
		await C.player.say("Rozebraná pevnost. Postavíme ji znovu!")
		return
	if not Globals.j_where:
		await C.Alica.say("Udělám si časovou osu. Ráno měla babička prstýnek u krmítka.")
		await C.Alica.say("Kdo potom hýbal se sněhem od krmítka?")
		var mg: CanvasLayer = WhereGame.new()
		add_child(mg)
		await mg.finished
		Globals.j_where = true
	await C.Joey.walk(get_marker_position("Pevnost") + Vector2(150, 0))
	await C.Joey.say("Haf!")
	await C.Alica.say("Joey, ne! Pevnost nerozbíjej!")
	C.Joey.pose()
	await C.Joey.say("…")
	await C.Hanka.say("Počkej. Joey dává tlapku na koleno. A kouká. On nám to chce říct!")
	await C.Betka.say("Bloky jsme řezali z té hromady. Rozebereme je opatrně, jeden po druhém.")
	await C.Hanka.say("Joey, čmuchej! Ukaž, který blok!")
	var mg2: CanvasLayer = SniffGame.new()
	add_child(mg2)
	await mg2.finished
	Globals.j_ring = true
	await pop("Prstynek")
	await C.Alica.say("Prstýnek! Byl zamrzlý ve sněhovém bloku!")
	C.Babicka.pose("ring")
	await C.Babicka.say("Můj prstýnek s hvězdičkou! Joey má nejlepší nos ze všech.")
	C.Babicka.pose()
	await C.Alica.say("Promiň, Joey. Byl jsi lepší detektiv než my.")
	await C.Joey.say("HAF!")
	_card(["A já dostal buřta.", "Tohle byl můj velký den."], 4.0)
	await get_tree().create_timer(4.5).timeout
	await the_end("Konec 7. dílu")
#endregion
