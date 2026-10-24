@tool
extends "res://game/shared/story_room.gd"
## Story 11, the barn on Easter Sunday: děda unlocks it, Hanka plays hide-and-seek, something clucks behind
## the bales. "Kde jsou vajíčka?" (minigame); Hanka crawls through the bales (minigame) to Kropenatka's secret
## nest with nine eggs. No rooster, so no chicks: on Easter Monday Věrka brings eggs from under her rooster
## Pepík; three weeks later, chicks.

const Data := preload('room_stodola11_state.gd')
const WhoGame := preload("res://game/minigames/who_11.gd")
const BalesGame := preload("res://game/minigames/bales.gd")
const DIM := Color(0.6, 0.55, 0.5)

var state: Data = load("res://game/rooms/stodola11/room_stodola11.tres")


func _on_room_entered() -> void:
	C.player.position = get_marker_position("Start")
	Globals.bring_sister(self, Vector2(170, 10))
	place("Joey", joey_spot())
	place("Babicka", get_marker_position("Babicka"))
	place("Deda", Vector2(750, 950))
	remove("Verka")
	get_prop("Hnizdo").visible = Globals.v_bales
	if not Globals.v_bales:
		dark(DIM)
	Globals.exit_arrow(self, "Ven", true)


func _on_room_transition_finished() -> void:
	if Globals.v_bales and not Globals.game_finished:
		await _ending()
		return
	if not Globals.v_who and get_meta("in", false) == false:
		set_meta("in", true)
		await C.Deda.say("Odemknuto. Ale tady je jen sláma.")
		await C.Hanka.say("Můžu si tu hrát na schovávanou? S opičkou?")
		await C.Deda.say("Jasně, Hani. Ale nelez moc vysoko!")


func joey_goal() -> Vector2:
	return get_hotspot("Skvira").walk_to_point


func on_click(node: Node) -> void:
	match node.script_name:
		"Baliky", "Skvira", "Hnizdo": await _bales()
		"Ven":
			await C.player.walk_to_clicked()
			R.goto_room("Dvur11")
		_: await super(node)


func on_character(chr: PopochiuCharacter, action: String, _item: PopochiuInventoryItem = null) -> bool:
	if action == "look" or chr == C.Alica or chr == C.Hanka or chr == C.Joey:
		return false
	await C.player.walk(chr.position + Vector2(-240, 20))
	match chr.script_name:
		"Babicka": await C.Babicka.say("Kropenatko! Puťa puťa puťa!")
		"Deda": await C.Deda.say("Nelez moc vysoko, Hani!")
		"Verka": await C.Verka.say("Vajíčka od Pepíkových slepic. Pro Kropenatku!")
		_: return false
	return true


func _bales() -> void:
	await C.player.walk(get_hotspot("Skvira").walk_to_point)
	if Globals.v_bales:
		await C.player.say("Kropenatka sedí na vajíčkách.")
		return
	await hand_over(C.Hanka, "Mezi balíky je škvíra. Tam se vejde jen Hanka!")
	if not Globals.v_who:
		await C.Hanka.say("Opičko, schovej se tady. Raz, dva, tři…")
		sfx("KVOK… KVOK…", Vector2(1300, 620), 70)
		await C.Hanka.say("Kdo to tam kvoká?")
		await C.Alica.say("Počkej, Hani! Kde jsou vajíčka? A kde je Kropenatka?")
		var mg: CanvasLayer = WhoGame.new()
		add_child(mg)
		await mg.finished
		Globals.v_who = true
	await C.Hanka.say("Já se tam vejdu! Rozsvítím baterku.")
	var mg2: CanvasLayer = BalesGame.new()
	add_child(mg2)
	await mg2.finished
	Globals.v_bales = true
	await light_up(1.0)
	await pop("Hnizdo")
	await _ending()


## The nest found (also resumed here if the game was left in the middle of it).
func _ending() -> void:
	await C.Hanka.say("Kropenatko! Tady jsi! Sedíš na vajíčkách!")
	await C.Babicka.say("Devět vajíček! Kropenatka je kvočna.")
	await C.Alica.say("Kvočna?")
	await C.Babicka.say("Slepička, která chce mít kuřátka. Schovává vajíčka a sedí na nich.")
	await C.Hanka.say("Babi, budou kuřátka?")
	await C.Babicka.say("Ach, Hani. My ale nemáme kohouta. Bez kohouta kuřátka nebudou.")
	await C.Alica.say("Já vím! Paní Věrka má na mlýně kohouta. Pepíka!")
	await fade(func(): pass, "Velikonoční pondělí…")
	place("Verka", get_marker_position("Verka"))
	await C.Verka.say("Koledníci! Tady jsou vajíčka od Pepíkových slepic. Ta dáme Kropenatce.")
	await C.Babicka.say("A naše vajíčka si vezmu na kraslice.")
	await C.Alica.say("A Joey to věděl celou dobu. Pořád čmuchal u stodoly!")
	Globals.v_swap = true
	await picture("res://assets/slides/chicks11.png", "Kuřátka!")
	await C.Hanka.say("Jedno, dvě, tři… osm kuřátek!")
	await the_end("Konec 11. dílu")
