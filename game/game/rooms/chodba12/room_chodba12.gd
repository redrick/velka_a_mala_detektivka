@tool
extends "res://game/shared/story_room.gd"
## Story 12, the hallway at home. The day before: máma whispering on the phone (the torn list "balónky, limo,
## 8…"), the circled day on the calendar, Hanka guarding the space under the stairs ("To je tajemství!",
## shavings in her pocket). The night: Hanka nearly tells opička. The birthday morning: nobody says anything,
## an arrow on Alica's door; the arrow guide and "who drew which arrow?" (three rounds); Hanka's torch finds
## the star under the stairs: TAM.

const Data := preload('room_chodba12_state.gd')
const WhoGame := preload("res://game/minigames/who_12.gd")
const NIGHT := Color(0.3, 0.32, 0.5)
const DIM := Color(0.35, 0.33, 0.4)

var state: Data = load("res://game/rooms/chodba12/room_chodba12.tres")


func _on_room_entered() -> void:
	if Globals.a_hurt and not Globals.a_morning:
		C.player.position = get_marker_position("Rano")
	else:
		C.player.position = get_marker_position("Start")
	Globals.bring_sister(self, Vector2(-170, 10))
	place("Joey", joey_spot())
	if not Globals.a_phone:
		place("Mama", get_marker_position("Mama")).pose("phone")
	elif Globals.a_morning:
		place("Mama", get_marker_position("Mama")).pose("home")
	else:
		remove("Mama")
	get_prop("SipkaDvere").visible = Globals.a_morning
	get_prop("Hvezda").visible = Globals.a_tam
	if Globals.a_hurt and not Globals.a_morning:
		dark(NIGHT, false)
	Globals.exit_arrow(self, "Ven", false)


func _on_room_transition_finished() -> void:
	if Globals.a_hurt and not Globals.a_morning:
		Globals.phase = ""
		await _night()


func joey_goal() -> Vector2:
	if not Globals.a_phone: return get_marker_position("Mama") + Vector2(-240, 20)
	if not Globals.a_shavings: return get_hotspot("Schody").walk_to_point
	if not Globals.a_morning: return get_hotspot("Ven").walk_to_point
	if not Globals.a_who: return get_hotspot("Pokoj").walk_to_point
	if not Globals.a_tam: return get_hotspot("Schody").walk_to_point
	return get_hotspot("Ven").walk_to_point


func on_click(node: Node) -> void:
	match node.script_name:
		"Kalendar":
			await C.player.walk_to_clicked()
			if Globals.a_morning:
				await C.Alica.say("Jeden den je zakroužkovaný. Dnešek!")
			else:
				await C.Alica.say("Jeden den je zakroužkovaný. Zítřek!")
			await C.Hanka.say("Hihi. To nic není!")
		"Pokoj", "SipkaDvere": await _door()
		"Schody", "Hvezda": await _stairs()
		"Ven": await _out()
		_: await super(node)


func on_character(chr: PopochiuCharacter, action: String, _item: PopochiuInventoryItem = null) -> bool:
	if action == "look" or chr == C.Alica or chr == C.Hanka or chr == C.Joey:
		return false
	await C.player.walk(chr.position + Vector2(-240, 20))
	match chr.script_name:
		"Mama":
			if Globals.a_phone:
				await C.Mama.say("Já? Nic. Vůbec nic se neděje.")
			else:
				await _phone()
		_: return false
	return true


#region The day before ###############################################################################
func _phone() -> void:
	await C.Mama.say("…balónky, limo, osm… psst, ona je tady! Pa pa!")
	C.Mama.pose("home")
	await C.Alica.say("Mami, s kým to mluvíš?")
	await C.Mama.say("S nikým! S babičkou. Nákupy.")
	await C.Alica.say("Mami, něco ti vypadlo. Roztržený papírek!")
	await picture("res://assets/slides/list12.png", "Balónky, limo, 8…")
	await C.Alica.say("Balónky? Limo? A proč osm?")
	Globals.a_phone = true
	await _suspects()


func _stairs() -> void:
	await C.player.walk(get_hotspot("Schody").walk_to_point)
	if Globals.a_tam:
		await C.player.say("TAM. Šipka pod schody ukazuje ven.")
		return
	if Globals.a_who:
		await _find_star()
		return
	if Globals.a_shavings:
		await C.Hanka.say("Tam nesmíš! To je tajemství!")
		return
	await hand_over(C.Alica, "Hihi. Pod schody nikoho nepustím!")
	await C.Hanka.say("Stůj! Pod schody nesmíš!")
	await C.Alica.say("Proč ne?")
	C.Hanka.pose("secret")
	await C.Hanka.say("Neřeknu! Je to tajemství!")
	C.Hanka.pose()
	C.Alica.pose("lens")
	await C.Alica.say("Hani, ty máš v kapse hobliny. Co jsi dělala?")
	C.Alica.pose()
	await C.Hanka.say("Nic! Ve školce. Hihi.")
	Globals.a_shavings = true
	await _suspects()


func _suspects() -> void:
	if not (Globals.a_phone and Globals.a_shavings and Globals.a_tonda and Globals.a_tracks):
		return
	await C.Alica.say("Máma šeptá, táta je od oleje, Tonda schovává kartičky, Hanka má tajemství…")
	await C.Alica.say("Všichni jsou podezřelí!")
#endregion


#region The night and the birthday morning ##########################################################
func _night() -> void:
	await C.Hanka.say("Opičko, zítra má Alica naroz… psst!")
	await C.Alica.say("Hm? Co říkáš, Hani?")
	await C.Hanka.say("Nic! Dobrou noc!")
	await fade(_morning_room, "Ráno…")
	Globals.a_morning = true
	C.Alica.pose("glum")
	await C.Alica.say("Nikdo mi nic neřekl. Ani máma, ani táta.")
	await C.Mama.say("Dobré ráno. Snídaně je na stole.")
	await C.Alica.say("Jen dobré ráno…")
	C.Alica.pose()
	await C.Hanka.say("Alico! Na tvých dveřích je šipka!")


func _morning_room() -> void:
	light_up(0.1)
	get_prop("SipkaDvere").show()
	place("Mama", get_marker_position("Mama")).pose("home")


func _door() -> void:
	await C.player.walk(get_hotspot("Pokoj").walk_to_point)
	if not Globals.a_morning:
		await C.player.say("Můj pokojíček.")
		return
	if Globals.a_who:
		await C.player.say("Čárkovaná šipka ukazuje pod schody.")
		return
	C.Alica.pose("lens")
	await C.Alica.say("Šipka na mých dveřích! Ukazuje pod schody.")
	C.Alica.pose()
	await C.Alica.say("Teď to vyřeším. Kdo kreslí jaké šipky?")
	await picture("res://assets/slides/arrows_guide12.png", "Tři různé šipky")
	for kind in ["tata", "mama", "hanka"]:
		var mg: CanvasLayer = WhoGame.new()
		mg.kind = kind
		add_child(mg)
		await mg.finished
	Globals.a_who = true
	await C.Alica.say("Táta, máma… a Hanka?! Ty malinké šipky jsi kreslila ty?")
	C.Hanka.pose("secret")
	await C.Hanka.say("Hihi. Pojď! Já vím kudy!")
	C.Hanka.pose()


func _find_star() -> void:
	await hand_over(C.Hanka, "Pod schody je tma. Baterku má Hanka!")
	dark(DIM)
	await C.Hanka.say("Rozsvítím baterku!")
	await pop("Hvezda")
	await C.Hanka.say("Hvězda! Co je na ní napsané?")
	await C.Alica.say("T… A… M. TAM!")
	await C.Alica.say("A šipka pod ní ukazuje ven!")
	await C.Hanka.say("Venku hledej další hvězdu!")
	await light_up(0.8)
	Globals.a_tam = true


func _out() -> void:
	await C.player.walk_to_clicked()
	if Globals.a_morning and not Globals.a_who:
		await C.player.say("Nejdřív šipka na dveřích.")
		return
	if Globals.a_who and not Globals.a_tam:
		await C.player.say("Šipka ukazuje pod schody.")
		return
	if Globals.a_tam:
		Globals.phase = "a_trail"
	R.goto_room("Ves12")
#endregion
