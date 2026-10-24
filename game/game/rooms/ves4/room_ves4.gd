@tool
extends "res://game/shared/story_room.gd"
## Story 4, the village: babička's henhouse, the tiny old henhouse behind the barn (only Hanka fits in),
## the church with the clock stopped at three. Day 1: the hen + star + F, the zigzag print, three o'clock
## ("the hand doesn't show the time, it points THERE"). Day 2: the sexton is cleared, the view from the
## tower shows the Bota rock. At the end Franta brings the winding key: the gears minigame, BIM BAM.

const Data := preload('room_ves4_state.gd')
const GearsGame := preload("res://game/minigames/gears.gd")

var state: Data = load("res://game/rooms/ves4/room_ves4.tres")


func _on_room_entered() -> void:
	match C.player.last_room:
		"Pole4": C.player.position = get_marker_position("ZPole")
		_: C.player.position = get_marker_position("Start")
	place("Babicka", get_marker_position("Babicka"))
	place("Joey", joey_spot())
	place("Kostelnik", get_marker_position("Kostelnik"))
	if Globals.f_franta and not Globals.f_clock:
		place("Deda", get_marker_position("Deda"))
		place("Rybar", Vector2(1460, 880)).pose()
		place("Verka", Vector2(560, 990))
	else:
		remove("Rybar")
		remove("Verka")
		place("Deda", get_marker_position("Deda"))
	if Globals.f_three and not Globals.f_franta:
		place("Tonda", Vector2(600, 990))
	else:
		remove("Tonda")
	get_prop("Stopy").visible = Globals.f_inside
	Globals.exit_arrow(self, "Domu", true)
	Globals.exit_arrow(self, "KPoli", false, Globals.f_three)


func _on_room_transition_finished() -> void:
	if Globals.phase == "f_morning":
		Globals.phase = ""
		_card(["Druhý den ráno…"], 1.6)
		await get_tree().create_timer(2.0).timeout
		await C.Babicka.say("Alice je líp. Ale ještě musí ležet.")
		await C.Hanka.say("Pan kostelník! Zeptám se ho na hodiny.")
	elif Globals.f_franta and not Globals.f_clock:
		await C.Rybar.say("Hanko, klíč patří do věže. Dej ho panu kostelníkovi.")
	elif not Globals.f_kurnik and Globals.f_intro:
		await C.Deda.say("Slepička v dopise? To bude přece náš kurník!")


func joey_goal() -> Vector2:
	if not Globals.f_kurnik:
		return get_hotspot("Kurnik").walk_to_point + Vector2(60, 40)
	if not Globals.f_inside:
		return get_hotspot("StaryKurnik").walk_to_point + Vector2(-120, 60)
	if not Globals.f_prints:
		return get_prop("Stopy").position + Vector2(-160, 40)
	if not Globals.f_three:
		return get_hotspot("Hodiny").walk_to_point + Vector2(-120, 40)
	if Globals.f_evening and not Globals.f_tower:
		return C.Kostelnik.position + Vector2(-220, 60)
	if not Globals.f_tower:
		return Vector2(1760, 960)
	if Globals.f_franta and not Globals.f_clock:
		return C.Kostelnik.position + Vector2(-220, 60)
	if Globals.f_tin and not Globals.f_read:
		return get_hotspot("Domu").walk_to_point
	if not Globals.f_franta:
		return Vector2(1760, 960)
	return Vector2.ZERO


func on_click(node: Node) -> void:
	match node.script_name:
		"Kurnik": await _new_henhouse()
		"StaryKurnik": await _old_henhouse()
		"Stopy": await _report_prints()
		"Hodiny", "Kostel": await _church()
		"Lavicka":
			await C.player.walk_to_clicked()
			await C.player.say("Lavička u kostela.")
		"Domu":
			await C.player.walk_to_clicked()
			R.goto_room("Pokoj4")
		"KPoli":
			await C.player.walk_to_clicked()
			R.goto_room("Pole4")
		_: await super(node)


func on_item(node: Node, item: PopochiuInventoryItem) -> void:
	I.deselect_active()
	if item == I.KlicHodin and node.script_name in ["Hodiny", "Kostel"]:
		await _church()
	elif item == I.Vysilacka:
		await _radio_now()
	else:
		await on_click(node)


func on_character(chr: PopochiuCharacter, action: String, item: PopochiuInventoryItem = null) -> bool:
	if action == "look" or chr == C.Joey:
		return false
	if item:
		I.deselect_active()
	await C.player.walk_to_clicked(Vector2(-220, 0))
	await C.player.face_clicked()
	match chr.script_name:
		"Kostelnik": await _sexton(item)
		"Deda":
			if not Globals.f_kurnik: await C.Deda.say("Slepička? Podívej se do kurníku!")
			elif not Globals.f_three: await C.Deda.say("Hodiny v dopise ukazují tři. Tak přijdeme ve tři!")
			else: await C.Deda.say("Kam ta ručička ukazuje… Vidíš to, Hanko?")
		"Babicka": await C.Babicka.say("Vedeš ty, Hanko. Já jdu za tebou.")
		"Tonda": await C.Tonda.say("Já jdu s vámi! Kdo najde poklad?")
		"Rybar": await C.Rybar.say("Klíč patří do věže. Zkus to s panem kostelníkem.")
		"Verka": await C.Verka.say("Klub Hvězdička je zase spolu. To jsem ráda!")
		_: return false
	return true


#region Day 1: the henhouses, the print, three o'clock ##############################################
func _new_henhouse() -> void:
	await C.player.walk_to_clicked()
	if Globals.f_kurnik:
		await C.player.say("Babiččin kurník. Tady to nebylo.")
		return
	await C.Hanka.say("Tady jsou babiččiny slepičky. Ale ta v dopise vypadá jinak.")
	await C.Babicka.say("Tenhle kurník je nový. Postavil ho děda loni.")
	C.Hanka.pose("think")
	await C.Hanka.say("Franta byl malý kluk. To je dávno. Musí to být starý kurník!")
	C.Hanka.pose()
	await C.Babicka.say("Starý kurník je za stodolou. Ten je malinký.")
	Globals.f_kurnik = true


func _old_henhouse() -> void:
	await C.player.walk_to_clicked()
	if not Globals.f_kurnik:
		await C.player.say("Malinký starý kurník. Zarostlý.")
		return
	if Globals.f_inside:
		await C.player.say("Uvnitř je vyrytá slepička, hvězdička a F.")
		return
	await C.Babicka.say("Dvířka jsou malinká. Tam se nevejdu.")
	await C.Hanka.say("Já jo! Já jsem malá. A mám baterku.")
	await slideshow([
		["henhouse_inside", "Hanka", "Slepička! Úplně stejná jako v dopise!"],
		["", "Hanka", "A hvězdička. A písmenko F."],
	])
	await C.Babicka.say("F jako Franta!")
	Globals.f_inside = true
	await pop("Stopy")
	C.Hanka.pose("point")
	await C.Hanka.say("A tady u dvířek… obří bota!")
	C.Hanka.pose()


func _report_prints() -> void:
	await C.player.walk_to_clicked(Vector2(-180, 20))
	if Globals.f_prints:
		await C.player.say("Obří stopy s cikcak podrážkou.")
		return
	C.Hanka.pose("radio")
	await C.Hanka.say("Velitelství! Slyšíš? Tady jsou obří stopy. Mají cikcak!")
	await radio("Jsou ještě mokré? Hani, to je čerstvé!")
	await radio("Někdo jde po Frantově stopě před námi! Zapisuju: STOPY.")
	await radio("Další obrázek v dopise jsou hodiny.")
	C.Hanka.pose()
	Globals.f_prints = true


func _radio_now() -> void:
	C.Hanka.pose("radio")
	await C.Hanka.say("Velitelství, slyšíš mě?")
	if not Globals.f_inside:
		await radio("Slyším! Hledej slepičku z dopisu.")
	elif not Globals.f_prints:
		await radio("Co je u dvířek kurníku, Hani? Podívej se na zem.")
	elif not Globals.f_three:
		await radio("Slyším! Teď hodiny. Na věži jsou hodiny.")
	elif not Globals.f_tower:
		await radio("Kam ukazuje ručička, Hani? Zkus se podívat shora.")
	else:
		await radio("Slyším tě, Hani! Jsi skvělý detektiv.")
	C.Hanka.pose()


func _church() -> void:
	await C.player.walk(get_hotspot("Hodiny").walk_to_point)
	if Globals.f_franta and not Globals.f_clock:
		await _clock_runs()
		return
	if not Globals.f_prints:
		await C.player.say("Kostel. Hodiny na věži ukazují tři.")
		return
	if Globals.f_three:
		await C.player.say("Ručička ukazuje tam, k poli.")
		return
	await C.Hanka.say("Hodiny! Jako v dopise. A ukazují tři.")
	await C.Babicka.say("Ty hodiny stojí, co pamatuju.")
	await C.Deda.say("V dopise jsou hodiny ve tři. Tak sem přijdeme ve tři!")
	await C.Kostelnik.say("Holčičko, na věž nesmíte. Je tam zamčeno.")
	C.Hanka.pose("radio")
	await radio("Kostelník má velké boty! A nechce nás pustit nahoru. Podezřelý číslo jedna!")
	C.Hanka.pose()
	var to_bench := func():
		C.Babicka.position = get_marker_position("Lavicka") + Vector2(-80, 40)
		C.Deda.position = get_marker_position("Lavicka") + Vector2(120, 40)
		C.player.position = get_marker_position("Lavicka") + Vector2(-260, 60)
	await fade(to_bench, "Ve tři hodiny…")
	await C.Deda.say("Tři hodiny. Teď!")
	await get_tree().create_timer(1.0).timeout
	await C.Babicka.say("…Nic se neděje.")
	var f := place("Rybar", Vector2(-120, 880))
	f.ignore_walkable_areas = true
	await f.walk(Vector2(1560, 880))
	f.pose("grin")
	await C.Hanka.say("Pan rybář! Podíval se na hodiny a usmál se.")
	f.pose()
	await f.walk(Vector2(2100, 880))
	f.ignore_walkable_areas = false
	remove("Rybar")
	place("Tonda", Vector2(2000, 950))
	await C.Tonda.walk(Vector2(1180, 950))
	await C.Tonda.say("Ahoj! Na co čekáte?")
	await C.Deda.say("Že se něco stane ve tři. Ale nestalo se nic.")
	C.Hanka.pose("think")
	await C.Hanka.say("Hm… Ručička je dlouhá. Jako prst.")
	C.Hanka.pose("point")
	await C.Hanka.say("Ručička neukazuje čas. Ukazuje TAM!")
	C.Hanka.pose()
	await C.Tonda.say("K poli? Jdu s vámi!")
	Globals.f_three = true
	Globals.show_exit(self, "KPoli")
#endregion


#region Day 2: the sexton, the tower ################################################################
func _sexton(item: PopochiuInventoryItem) -> void:
	if Globals.f_franta and not Globals.f_clock:
		await _clock_runs()
		return
	if not Globals.f_evening:
		await C.Kostelnik.say("Na věž nesmíte, holčičko. Je to nebezpečné.")
		return
	if Globals.f_tower:
		await C.Kostelnik.say("Bota je za potokem. Kluci tam kdysi lezli.")
		return
	await C.Hanka.say("Pane kostelníku, proč ty hodiny stojí?")
	await C.Kostelnik.say("Stojí šedesát let. Když jsem byl kluk, ztratil se klíč na natahování.")
	await C.Babicka.say("A nechodil jste včera ráno za stodolou? Ve velkých botách?")
	C.Kostelnik.pose("galoshes")
	await C.Kostelnik.say("Já? Já nosím jen tyhle malé galoše. Koukejte.")
	C.Kostelnik.pose()
	C.Hanka.pose("radio")
	await C.Hanka.say("Velitelství! Pan kostelník má malé galoše. Bez cikcaku.")
	await radio("Tak to nebyl on. Škrtám!")
	C.Hanka.pose()
	await C.Kostelnik.say("Na věž lezl jen jeden kluk. Malý Franta. Pak se odstěhoval.")
	await C.Hanka.say("Ručička ukazuje k poli. Ale tam je kamenů! Který?")
	await C.Kostelnik.say("Tak se podívej shora. Pojď, podržím tě.")
	await picture("res://assets/slides/tower_view4.png", "Z věže")
	C.Hanka.pose("point")
	await C.Hanka.say("Ručička ukazuje na kámen. A ten kámen vypadá jako bota!")
	C.Hanka.pose()
	await C.Kostelnik.say("Tomu kameni říkáme Bota odjakživa.")
	Globals.f_tower = true


func _clock_runs() -> void:
	if not I.KlicHodin.in_inventory:
		await C.Kostelnik.say("Bez klíče hodiny nenatáhnu.")
		return
	I.KlicHodin.remove()
	await C.Kostelnik.say("Klíč! Ten ztracený klíč! Po šedesáti letech!")
	await C.Rybar.say("Promiňte. To já. Jako kluk jsem ho schoval do pokladu.")
	await C.Kostelnik.say("Jenže strojek je rozebraný. Kolečka jsou rozházená po podlaze.")
	await C.Kostelnik.say("Hanko, ty máš šikovné oči. Pomůžeš?")
	var mg: CanvasLayer = GearsGame.new()
	add_child(mg)
	await mg.finished
	Globals.f_clock = true
	sfx("BIM BAM!", Vector2(1260, 160), 110)
	await get_tree().create_timer(1.2).timeout
	sfx("BIM BAM!", Vector2(1360, 220), 110)
	await C.Babicka.say("Hodiny jdou! Po šedesáti letech!")
	C.Hanka.pose("radio")
	await radio("Slyším je až sem! BIM BAM! Hani, tys to vyřešila!")
	C.Hanka.pose("grin")
	await C.Deda.say("Klub Hvězdička je zase celý.")
	await C.Hanka.say("Hanka to vyřešila!")
	C.Hanka.pose()
	await the_end("Konec 4. dílu")
#endregion
