@tool
extends "res://game/shared/story_room.gd"
## Story 12, our street at home in the village. The day before: chalk arrows everywhere (a long solid one high
## up on the garage with an oil smudge, a dashed one with a heart, a tiny dotted one right by the ground), Tonda
## with chalky hands and a real hopscotch (and a white card in his pocket), wide knobbly tyre tracks to the
## locked garage, táta "fixing the mower" that stands outside. The garden gate is locked, whispers "…Klub…":
## the hurt beat. The birthday morning: the trail. SKOČ on the hopscotch, Joey sitting on an arrow, the
## rain-smudged arrows put right ("Otoč šipky"), the gate.

const Data := preload('room_ves12_state.gd')
const ArrowsGame := preload("res://game/minigames/arrows.gd")
const EVENING := Color(0.75, 0.7, 0.85)

var state: Data = load("res://game/rooms/ves12/room_ves12.tres")


func _on_room_entered() -> void:
	match C.player.last_room:
		"Chodba12": C.player.position = get_hotspot("Dum").walk_to_point + Vector2(80, 60)
		_: C.player.position = get_marker_position("Start")
	Globals.bring_sister(self, Vector2(170, 10))
	if Globals.a_tam and not Globals.a_joey:
		place("Joey", get_marker_position("Joey"))
	else:
		place("Joey", joey_spot())
	if Globals.a_home and not Globals.a_tonda:
		place("Tonda", get_marker_position("Tonda")).pose("chalk")
	else:
		remove("Tonda")
	if Globals.a_home and not Globals.a_tracks:
		place("Tata", get_marker_position("Tata")).pose("oil")
	else:
		remove("Tata")
	if Globals.a_home and not Globals.a_morning:
		place("Verka", get_marker_position("Verka"))
		place("Betka", get_marker_position("Betka"))
	else:
		remove("Verka")
		remove("Betka")
	get_prop("Karticka").visible = false
	get_prop("Hvezda").visible = Globals.a_skoc
	if Globals.a_morning:
		for arrow in ["SipkaVysoko", "SipkaCarkovana", "SipkaTeckovana"]:
			get_prop(arrow).modulate = Color(1, 1, 1, 0.35)
	if Globals.a_hurt and not Globals.a_morning:
		dark(EVENING, false)
	Globals.exit_arrow(self, "Dum", true)


func _on_room_transition_finished() -> void:
	if not Globals.a_home:
		await _home()
	elif Globals.phase == "a_trail":
		Globals.phase = ""
		await C.Alica.say("V noci pršelo. Šipky jsou rozmazané!")
		C.Hanka.pose("chalk")
		await C.Hanka.say("Já mám křídu! Ale kudy se jde, ti neřeknu. To je tajemství!")
		C.Hanka.pose()


func joey_goal() -> Vector2:
	if Globals.a_tam:
		if not Globals.a_skoc: return get_prop("Panak").position + Vector2(-240, 0)
		if not Globals.a_joey: return get_marker_position("Joey") + Vector2(-240, 40)
		return get_hotspot("Branka").walk_to_point
	if not Globals.a_high: return Vector2(860, 860)
	if not Globals.a_dashed: return get_prop("SipkaCarkovana").position + Vector2(-260, 0)
	if not Globals.a_dotted: return get_prop("SipkaTeckovana").position + Vector2(-200, 130)
	if not Globals.a_tonda: return get_marker_position("Tonda") + Vector2(-240, 20)
	if not Globals.a_tracks: return get_hotspot("Garaz").walk_to_point
	if not (Globals.a_phone and Globals.a_shavings): return get_hotspot("Dum").walk_to_point
	if not Globals.a_hurt: return get_hotspot("Branka").walk_to_point
	return get_hotspot("Dum").walk_to_point


func _home() -> void:
	await C.Alica.say("Doma! A tady taky šipky! Na garáži, na chodníku, u plotu…")
	await C.Hanka.say("Hihi.")
	C.Alica.pose("lens")
	await C.Alica.say("Každá je jiná. Někdo je tu kreslí. Velká a malá detektivka to vyšetří!")
	C.Alica.pose()
	Globals.a_home = true
	place("Tonda", get_marker_position("Tonda")).pose("chalk")
	place("Tata", get_marker_position("Tata")).pose("oil")
	place("Verka", get_marker_position("Verka"))
	place("Betka", get_marker_position("Betka"))


func on_click(node: Node) -> void:
	match node.script_name:
		"SipkaVysoko": await _arrow_high()
		"SipkaCarkovana": await _arrow_dashed()
		"SipkaTeckovana": await _arrow_dotted()
		"Panak", "Hvezda": await _hopscotch()
		"Stopy", "Garaz", "Sekacka": await _garage()
		"Karticka": await C.player.say("Bílá kartička. Tonda ji hned schoval.")
		"Branka": await _gate()
		"Dum":
			await C.player.walk_to_clicked()
			R.goto_room("Chodba12")
		_: await super(node)


func on_character(chr: PopochiuCharacter, action: String, _item: PopochiuInventoryItem = null) -> bool:
	if action == "look" or chr == C.Alica or chr == C.Hanka:
		return false
	if chr == C.Joey:
		if not Globals.a_skoc or Globals.a_joey:
			return false
		await _joey()
		return true
	await C.player.walk(chr.position + Vector2(-240, 20))
	match chr.script_name:
		"Tonda": await _tonda()
		"Tata": await _garage()
		"Verka":
			await C.Verka.say("Alico, máš ráda kočičky?")
			await C.Alica.say("Moc! Proč?")
			await C.Verka.say("Jen tak. Jen tak se ptám!")
		"Betka":
			await C.Alica.say("Bětko, proč máš ruce od barvy?")
			await C.Betka.say("Malujeme… nic! Nic nemalujeme!")
		_: return false
	return true


#region The day before ###############################################################################
func _arrow_high() -> void:
	await C.player.walk(Vector2(860, 860))
	if Globals.a_morning:
		await C.player.say("Déšť šipky skoro smyl.")
		return
	if Globals.a_high:
		await C.player.say("Dlouhá rovná šipka. Vysoko. Vedle černá šmouha.")
		return
	C.Alica.pose("lens")
	await C.Alica.say("Dlouhá rovná šipka. Je hodně vysoko. Tam nedosáhnu ani já!")
	await C.Alica.say("A vedle je černá šmouha. Jako od oleje.")
	C.Alica.pose()
	Globals.a_high = true


func _arrow_dashed() -> void:
	await C.player.walk(get_prop("SipkaCarkovana").position + Vector2(-260, 0))
	if Globals.a_morning:
		await C.player.say("Déšť šipky skoro smyl.")
		return
	if Globals.a_dashed:
		await C.player.say("Čárkovaná šipka se srdíčkem. Jako na chalupě.")
		return
	C.Alica.pose("lens")
	await C.Alica.say("Čárkovaná šipka. Na konci srdíčko. Stejná jako na chalupě!")
	C.Alica.pose()
	Globals.a_dashed = true


func _arrow_dotted() -> void:
	await C.player.walk(get_prop("SipkaTeckovana").position + Vector2(-200, 130))
	if Globals.a_morning:
		await C.player.say("Déšť šipky skoro smyl.")
		return
	if Globals.a_dotted:
		await C.player.say("Malá šipka z teček. Úplně dole u země.")
		return
	C.Alica.pose("lens")
	await C.Alica.say("Malinká šipka z teček. Celá křivá. A úplně dole u země.")
	C.Alica.pose()
	await C.Alica.say("Tu kreslil někdo malý.")
	await C.Hanka.say("Malý? Já ne! Hihi.")
	Globals.a_dotted = true


func _tonda() -> void:
	if Globals.a_tonda:
		return
	await C.Alica.say("Tondo! Máš ruce celé od křídy. Ty kreslíš ty šipky?")
	await C.Tonda.say("Ne! Kreslím panáka! Podívej!")
	await C.Alica.say("Opravdu. Panák. Tonda mluví pravdu.")
	await pop("Karticka")
	await C.Alica.say("Tondo, vypadla ti kartička!")
	await C.Tonda.say("To nic! To nic není! Ahoj!")
	get_prop("Karticka").hide()
	Globals.a_tonda = true
	remove("Tonda")


func _garage() -> void:
	await C.player.walk(get_hotspot("Garaz").walk_to_point)
	if Globals.a_tracks:
		await C.player.say("Garáž je zamčená. Stopy jsou široké a vroubkované.")
		return
	await C.Alica.say("Garáž je zamčená. A tady jsou stopy od kola.")
	C.Alica.pose("lens")
	await C.Alica.say("Moc široké na moje kolo. A vroubkované.")
	C.Alica.pose()
	await C.Alica.say("Tati, máš ruce od oleje. Co děláš v garáži?")
	await C.Tata.say("Opravuju… sekačku.")
	await C.Alica.say("Ale sekačka stojí tady venku!")
	await C.Tata.say("Ehm. Druhou sekačku.")
	Globals.a_tracks = true
	remove("Tata")


func _gate() -> void:
	await C.player.walk(get_hotspot("Branka").walk_to_point)
	if Globals.a_tam:
		await _trail_gate()
		return
	if Globals.a_hurt:
		await C.player.say("Branka do zahrady. Zamčená.")
		return
	if not (Globals.a_high and Globals.a_dashed and Globals.a_dotted and Globals.a_tonda and Globals.a_tracks
			and Globals.a_phone and Globals.a_shavings):
		await C.player.say("Branka do zahrady je zamčená. Všechny šipky vedou sem.")
		return
	await C.Alica.say("Všechny šipky vedou k nám do zahrady. A branka je zamčená.")
	sfx("…Klub… psst…", Vector2(1700, 520), 60)
	await C.Alica.say("Za plotem někdo šeptá. Klub Hvězdička má schůzku…")
	C.Alica.pose("glum")
	await C.Alica.say("…beze mě.")
	await C.Hanka.say("Alico… ono je to… ne, nic. Pojď domů.")
	C.Alica.pose()
	Globals.a_hurt = true
	await fade(func(): pass, "Večer…")
	Globals.phase = "a_night"
	R.goto_room("Chodba12")
#endregion


#region The birthday morning #########################################################################
func _hopscotch() -> void:
	await C.player.walk(get_prop("Panak").position + Vector2(-240, 0))
	if not Globals.a_tam:
		await C.player.say("Tondův panák. Jedna, dva, tři… až do nebe.")
		return
	if Globals.a_skoc:
		await C.player.say("SKOČ! Hop, hop, hop. Až na konec.")
		return
	await pop("Hvezda")
	await C.Hanka.say("Hvězda! Co je na ní?")
	await C.Alica.say("S… K… O… Č. SKOČ!")
	await C.Alica.say("Hop, hop, hop… až na konec!")
	await C.Alica.say("A na konci sedí Joey. Na šipce!")
	Globals.a_skoc = true


func _joey() -> void:
	await C.player.walk(get_marker_position("Joey") + Vector2(-240, 40))
	await C.Alica.say("Joey, uhni! Sedíš na šipce.")
	await C.Joey.say("Haf.")
	await C.Hanka.say("Nehne se. Musíš říct to kouzelné slovo!")
	await C.Alica.say("Hodný pejsek, Joey!")
	await C.Joey.say("Haf! Haf!")
	await C.Joey.walk(get_marker_position("Joey") + Vector2(-300, 120))
	Globals.a_joey = true
	await C.Alica.say("Pod ním je šipka. Ale déšť ty další rozmazal. Kam vedou?")
	await C.Hanka.say("Musíš je otočit správně! Od dveří, přes hvězdy, až k brance.")
	C.Hanka.pose("chalk")
	var mg: CanvasLayer = ArrowsGame.new()
	add_child(mg)
	await mg.finished
	C.Hanka.pose()
	Globals.a_arrows = true
	await C.Alica.say("Všechny šipky vedou k brance. Do naší zahrady!")


func _trail_gate() -> void:
	if not Globals.a_arrows:
		await C.player.say("Branka do zahrady. Ještě nevím, jestli vede sem cesta.")
		return
	await C.Hanka.say("Posvítím škvírou… Branka je odemčená! Otevři!")
	R.goto_room("Zahrada12")
#endregion
