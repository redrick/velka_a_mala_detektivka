@tool
extends "res://game/shared/story_room.gd"
## Story 11, the chalupa yard at Easter. Thursday: eight hens, one egg short every day. False leads: round
## prints by the run (Joey, not a fox), no shells anywhere, the magpie's nest (foil, ribbon, a spoon), Tonda
## (he brings eggs). Kropenatka puffed up with straw in her feathers. Saturday evening she's missing: the gap
## under the wire, a speckled feather, hen prints to the barn.

const Data := preload('room_dvur11_state.gd')
const EVENING := Color(0.5, 0.5, 0.7)

var state: Data = load("res://game/rooms/dvur11/room_dvur11.tres")


func _on_room_entered() -> void:
	match C.player.last_room:
		"Kurnik11": C.player.position = get_hotspot("Kurnik").walk_to_point
		"Stodola11": C.player.position = get_hotspot("Stodola").walk_to_point
		_: C.player.position = get_marker_position("Start")
	Globals.bring_sister(self, Vector2(170, 10))
	place("Joey", joey_spot())
	place("Babicka", get_marker_position("Babicka")).pose("basket" if not Globals.v_count else "")
	if Globals.v_count and not Globals.v_tonda:
		place("Tonda", get_marker_position("Tonda")).pose("eggs")
	else:
		remove("Tonda")
	if Globals.v_missing and not Globals.v_gap:
		place("Deda", Vector2(1450, 930))
	else:
		remove("Deda")
	get_prop("Kropenatka").visible = not Globals.v_missing or Globals.v_bales
	get_prop("Pirko").visible = Globals.v_gap
	get_prop("Straka").visible = not Globals.v_magpie
	if Globals.v_missing and not Globals.v_gap:
		dark(EVENING)


func _on_room_transition_finished() -> void:
	if not Globals.v_intro:
		await _intro()
	elif Globals.phase == "v_evening":
		Globals.phase = ""
		await C.Babicka.say("Pět, šest, sedm… Kde je Kropenatka? Nepřišla spát!")
		await C.Hanka.say("Kropenatka se ztratila!")
		await C.Deda.say("Vezměte baterky. Hledáme!")


func joey_goal() -> Vector2:
	if not Globals.v_count: return get_hotspot("Kurnik").walk_to_point
	if not Globals.v_fox: return get_prop("PsiStopy").position + Vector2(-240, -40)
	if not Globals.v_shells: return get_prop("Slepice").position + Vector2(-300, 160)
	if not Globals.v_magpie: return Vector2(1200, 900)
	if not Globals.v_tonda: return get_marker_position("Tonda") + Vector2(-240, 20)
	if not Globals.v_straw: return get_prop("Kropenatka").position + Vector2(-220, 40)
	if not Globals.v_missing: return get_hotspot("Dum").walk_to_point
	if not Globals.v_gap: return get_hotspot("Mezera").walk_to_point
	return get_hotspot("Stodola").walk_to_point


func _intro() -> void:
	_card(["Zelený čtvrtek. Velikonoce na chalupě!"], 2.0)
	await get_tree().create_timer(2.4).timeout
	await C.Babicka.say("Vítejte, holčičky! V sobotu budeme barvit vajíčka. Sbírám je celý týden.")
	await C.Alica.say("Babi, proč máš v košíku tak málo vajíček?")
	await C.Babicka.say("No právě. Mám osm slepiček. Ale každý den jedno vajíčko chybí.")
	C.Alica.pose("lens")
	await C.Alica.say("To je případ pro nás! Velká a malá detektivka!")
	C.Alica.pose()
	Globals.v_intro = true


func on_click(node: Node) -> void:
	match node.script_name:
		"Kurnik":
			await C.player.walk_to_clicked()
			R.goto_room("Kurnik11")
		"PsiStopy": await _prints()
		"Slepice": await _shells()
		"Straka": await _magpie()
		"Kropenatka": await _kropenatka()
		"Mezera", "Pirko": await _gap()
		"Stodola": await _barn()
		"Dum":
			await C.player.walk_to_clicked()
			R.goto_room("Kuchyne11")
		_: await super(node)


func on_character(chr: PopochiuCharacter, action: String, _item: PopochiuInventoryItem = null) -> bool:
	if action == "look" or chr == C.Alica or chr == C.Hanka or chr == C.Joey:
		return false
	await C.player.walk(chr.position + Vector2(-240, 20))
	match chr.script_name:
		"Tonda": await _tonda()
		"Babicka": await C.Babicka.say("Osm slepiček. Kropenatka je ta s tečkami." if not Globals.v_missing else "Kropenatko, kde jsi?")
		"Deda": await C.Deda.say("Stodola je zamčená. Klíč mám já.")
		_: return false
	return true


#region Thursday and Friday ########################################################################
func _prints() -> void:
	await C.player.walk_to_clicked(Vector2(-240, -40))
	if Globals.v_fox:
		await C.player.say("Kulaté stopy. Joeyho.")
		return
	await C.Alica.say("Stopy u plotu! Že by liška?")
	C.Alica.pose("lens")
	await C.Alica.say("Ne. Liška má úzkou stopu. Tahle je kulatá. To je Joey! Pořád tady hrabe.")
	C.Alica.pose()
	await C.Joey.say("Haf!")
	Globals.v_fox = true
	await _friday()


func _shells() -> void:
	await C.player.walk(get_prop("Slepice").position + Vector2(-300, 160))
	if Globals.v_shells:
		await C.player.say("Slepičky zobou. Skořápky nikde.")
		return
	await C.Hanka.say("Hledám skořápky. Tady nic!")
	await C.Alica.say("Kdyby vajíčka někdo snědl, zůstaly by skořápky. Žádné tu nejsou.")
	await C.Alica.say("Nikdo je nesnědl. Někdo je SCHOVÁVÁ!")
	Globals.v_shells = true
	await _friday()


func _magpie() -> void:
	await C.player.walk(Vector2(1150, 900))
	if Globals.v_magpie:
		return
	await C.Alica.say("Straka! Straky kradou lesklé věci. A co vajíčka?")
	await picture("res://assets/slides/magpie_nest11.png", "Dalekohledem do strakatého hnízda")
	await C.Babicka.say("Alobal, mašle… a moje lžička, co mi straka vzala na podzim!")
	await C.Alica.say("Ale žádné vajíčko. Vajíčka nejsou lesklá. Straka to nebyla.")
	Globals.v_magpie = true
	get_prop("Straka").hide()
	await _friday()


func _tonda() -> void:
	if Globals.v_tonda:
		await C.Tonda.say("V pondělí přijdu na koledu!")
		return
	await C.Alica.say("Tondo! Kde jsi vzal ten košík vajíček?")
	await C.Tonda.say("Od nás! Mamka je posílá paní Janě. Prý jí chybí.")
	C.Babicka.pose()
	await C.Babicka.say("Děkuju, Tondo! Teď budeme mít na barvení dost.")
	Globals.v_tonda = true
	remove("Tonda")
	await _friday()


func _kropenatka() -> void:
	await C.player.walk(get_prop("Kropenatka").position + Vector2(-240, 40))
	if Globals.v_straw:
		await C.player.say("Kropenatka. Načepýřená a mrzutá.")
		return
	sfx("KVOK! KVOK!", get_prop("Kropenatka").position + Vector2(-80, -200), 70)
	await C.Babicka.say("Kropenatko, co je s tebou? Jsi celá načepýřená.")
	C.Alica.pose("lens")
	await C.Alica.say("Babi, ona má v peří stébla slámy! Ale v kurníku jsou hobliny…")
	C.Alica.pose()
	await C.Babicka.say("Slepice se hrabou všude, Alico.")
	Globals.v_straw = true
	await _friday()


func _friday() -> void:
	if Globals.v_missing or not (Globals.v_count and Globals.v_fox and Globals.v_shells and Globals.v_magpie and Globals.v_tonda
			and Globals.v_straw):
		return
	await C.Alica.say("Vajíčka jsou celá. Jsou někde schovaná! Ale kde?")
	await C.Babicka.say("Zítra je Bílá sobota. Budeme barvit. Pojďte domů!")
#endregion


#region Saturday evening ##############################################################################
func _gap() -> void:
	await C.player.walk(get_hotspot("Mezera").walk_to_point)
	if not Globals.v_missing:
		await C.player.say("Pletivo kolem výběhu. Dole je malá dírka.")
		return
	if Globals.v_gap:
		await C.player.say("Dírka pod pletivem. Stopičky vedou ke stodole.")
		return
	C.Alica.pose("lens")
	await C.Alica.say("Dírka pod pletivem! A pírko s tečkami!")
	C.Alica.pose()
	await pop("Pirko")
	await C.Hanka.say("A slepičí stopičky. Vedou ke stodole!")
	await C.Deda.say("Tudy chodí slepice na zahradu. Ale stodola je zamčená. Ráno odemknu.")
	await light_up(1.0)
	await fade(func(): pass, "Velikonoční neděle…")
	Globals.v_gap = true
	remove("Deda")


func _barn() -> void:
	await C.player.walk(get_hotspot("Stodola").walk_to_point)
	if not Globals.v_gap:
		await C.player.say("Stará stodola. Je zamčená.")
		return
	R.goto_room("Stodola11")
#endregion
