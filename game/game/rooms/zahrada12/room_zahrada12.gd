@tool
extends "res://game/shared/story_room.gd"
## Story 12, our garden: PŘEKVAPENÍ! Everybody is here. Each suspect explains (Tonda's invitations, babička's
## cake, máma's list, Hanka's dotted arrows), everyone gets seated ("Kdo kde sedí?"), the cake with eight
## candles, the presents: Hanka's cat drawing and the stick she peeled herself, děda's basket ("mňau": the
## kitten Micka, daughter of the old Micka), the pink bike with a front fork (the wide tyre tracks). Joey
## shakes off the party hat.

const Data := preload('room_zahrada12_state.gd')
const SeatingGame := preload("res://game/minigames/seating.gd")

var state: Data = load("res://game/rooms/zahrada12/room_zahrada12.tres")


func _on_room_entered() -> void:
	if C.player != C.Alica:
		Globals.switch_to(C.Alica)
	C.player.position = get_marker_position("Start")
	Globals.bring_sister(self, Vector2(-170, 10))
	for who in ["Mama", "Tata", "Babicka", "Deda", "Tonda", "Betka", "Verka", "Joey"]:
		place(who, get_marker_position(who))
	C.Deda.pose("basket" if not Globals.a_kitten else "")
	get_prop("Kresba").visible = Globals.a_hanka
	get_prop("Kolo").visible = Globals.a_bike
	get_prop("Klobouk").visible = false


func _on_room_transition_finished() -> void:
	if get_meta("in", false):
		return
	set_meta("in", true)
	if Globals.a_hanka and Globals.a_kitten and Globals.a_bike:
		await _all_presents()
		return
	if Globals.a_hanka or Globals.a_kitten or Globals.a_bike:
		return
	sfx("PŘEKVAPENÍ!", Vector2(960, 420), 120)
	await C.Mama.say("Všechno nejlepší, Alico!")
	await C.Alica.say("To… to je všechno pro mě?")
	await C.Tata.say("Osm let! To se musí oslavit.")
	await C.Tonda.say("Ta kartička byla pozvánka. Roznášel jsem je!")
	await C.Babicka.say("A dort jsem pekla já. Proto ta mouka.")
	await C.Mama.say("Balónky, limo, osm svíček. To byl ten seznam.")
	await C.Alica.say("A šipky jste kreslili vy tři. Táta, máma a Hanka!")
	await C.Hanka.say("A já jsem to skoro neřekla! Skoro…")
	await C.Alica.say("Velká a malá detektivka vyšetřila vlastní narozeniny!")
	await C.Mama.say("A teď ke stolu! Kdo bude sedět kde? Každý má svoje přání.")
	var mg: CanvasLayer = SeatingGame.new()
	add_child(mg)
	await mg.finished
	Globals.a_seating = true
	await C.Mama.say("A teď dárky! Kdo začne?")


func joey_goal() -> Vector2:
	if not Globals.a_hanka: return C.Hanka.position + Vector2(-200, 20)
	if not Globals.a_kitten: return C.Deda.position + Vector2(-240, 20)
	return C.Tata.position + Vector2(-240, 20)


func on_click(node: Node) -> void:
	match node.script_name:
		"Dort":
			await C.player.walk(get_prop("Dort").position + Vector2(-240, 300))
			await C.Alica.say("Osm svíček. Fffffuu!")
			await C.Hanka.say("Všechny zhasly! Přání se splní!")
		"Darky":
			await C.player.walk_to_clicked()
			await C.player.say("Dárečky od hostů. Ty rozbalíme potom.")
		"Kresba":
			await C.player.walk_to_clicked()
			await C.player.say("Kočička od Hanky a hůlka, co si sama oloupala.")
		"Kolo":
			await C.player.walk_to_clicked()
			await C.player.say("Moje růžové kolo s odpruženou vidlicí!")
		_: await super(node)


func on_character(chr: PopochiuCharacter, action: String, _item: PopochiuInventoryItem = null) -> bool:
	if action == "look" or chr == C.Alica:
		return false
	if chr == C.Hanka:
		if Globals.a_hanka:
			return false
		await _hanka()
		return true
	if chr == C.Joey:
		return false
	await C.player.walk(chr.position + Vector2(-240, 20))
	match chr.script_name:
		"Deda": await _kitten()
		"Tata", "Mama": await _bike()
		"Babicka": await C.Babicka.say("Kousek dortu, Alico?")
		"Tonda": await C.Tonda.say("Pojďte hrát na schovávanou!")
		"Betka": await C.Betka.say("Ty balónky jsme malovaly my!")
		"Verka": await C.Verka.say("Tak co? Máš ráda kočičky?")
		_: return false
	return true


func _hanka() -> void:
	await C.Hanka.say("Alico, tohle je ode mě! Kočička. Nakreslila jsem ji ve školce.")
	await pop("Kresba")
	await C.Hanka.say("A hůlka. Sama jsem ji oloupala! Nožíkem!")
	await C.Alica.say("Proto ty hobliny v kapse! Děkuju, Hani!")
	Globals.a_hanka = true
	await _all_presents()


func _kitten() -> void:
	if Globals.a_kitten:
		await C.Deda.say("Dávej na ni pozor. Je ještě malinká.")
		return
	await C.Deda.say("A tohle je ode mě.")
	sfx("Mňau!", C.Deda.position + Vector2(60, -320), 60)
	await C.Alica.say("Ta straka z kůlny!")
	C.Deda.pose()
	C.Alica.pose("kitten")
	await C.Deda.say("Koťátko. Je to dcera naší staré Micky.")
	await C.Alica.say("Takže je to malá Micka! Micka, malá Micka!")
	C.Alica.pose()
	Globals.a_kitten = true
	await _all_presents()


func _bike() -> void:
	if Globals.a_bike:
		await C.Tata.say("Pojedeme spolu do lesa. Po pěšinkách!")
		return
	await C.Tata.say("A teď od nás. Zavři oči!")
	await pop("Kolo")
	await C.Alica.say("Nové kolo! Růžové!")
	await C.Tata.say("S odpruženou vidlicí. Pojedeme spolu do lesa.")
	C.Alica.pose("lens")
	await C.Alica.say("Proto ty široké stopy u garáže! A ten olej!")
	C.Alica.pose()
	await C.Tata.say("Žádná sekačka. Kolo jsem chystal.")
	Globals.a_bike = true
	await _all_presents()


func _all_presents() -> void:
	if not (Globals.a_hanka and Globals.a_kitten and Globals.a_bike):
		return
	await C.Babicka.say("A Joey taky dostane čepičku!")
	sfx("VRRR!", C.Joey.position + Vector2(0, -300), 70)
	get_prop("Klobouk").position = C.Joey.position + Vector2(80, 10)
	await pop("Klobouk")
	await C.Hanka.say("Joey čepičky nesnáší!")
	await C.Alica.say("Vždyť to celé bylo pro mě. A já myslela, že na mě všichni zapomněli.")
	await C.Mama.say("Na tebe nikdo nezapomene, Alico.")
	await the_end("Konec 12. dílu")
