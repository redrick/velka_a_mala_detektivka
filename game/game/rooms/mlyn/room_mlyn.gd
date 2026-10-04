@tool
extends "res://game/shared/story_room.gd"
## Story 3, the little mill. Joey's trail ends at the lady's bench (she gives him a biscuit; the stick
## and the lantern are there to be noticed). Then "Kdo to byl?" (minigame), Hanka invites the lady to
## the club, she finishes Věrka's riddle… it's Věrka! Tonda fetches děda, the club opens the tin
## together, Tonda gets the spare badge and Hanka keeps Franta's picture letter.

const Data := preload('room_mlyn_state.gd')
const CulpritGame := preload("res://game/minigames/culprit.gd")

var state: Data = load("res://game/rooms/mlyn/room_mlyn.tres")


func _on_room_entered() -> void:
	C.player.position = get_marker_position("Start")
	Globals.bring_sister(self, Vector2(170, 10))
	Globals.exit_arrow(self, "Zpet", true)
	place("Verka", get_marker_position("Verka"))
	place("Tonda", C.player.position + Vector2(330, 20))
	place("Joey", C.player.position + Vector2(500, 30))
	for p in ["Plechovka", "Tolar", "Dalekohled", "Fotka", "Odznak", "Dopis"]:
		get_prop(p).visible = Globals.r_end and p in ["Plechovka"]
	if Globals.r_end:
		place("Deda", Vector2(1000, 960))


func _on_room_transition_finished() -> void:
	if not Globals.r_verka:
		await _bench()


func on_click(node: Node) -> void:
	match node.script_name:
		"Zpet":
			await C.player.walk_to_clicked()
			R.goto_room("Rybnik")
		"Hul": await C.player.say("Hůlka opřená o lavičku.")
		"Lucerna": await C.player.say("Na okně stojí lucerna.")
		"Lavicka": await C.player.say("Lavička u mlýnku.")
		"Dvere": await C.player.say("Dveře do mlýnku.")
		_: await super(node)


func on_character(chr: PopochiuCharacter, action: String, _item: PopochiuInventoryItem = null) -> bool:
	if action == "look" or chr == C.Joey:
		return false
	if chr == C.Verka:
		if Globals.r_end:
			await C.Verka.say("Klub Hvězdička je zase celý. Skoro celý… ještě Franta!")
		elif Globals.r_verka:
			await _whodunit()
		else:
			await C.Verka.say("Dobrý den, děti!")
		return true
	if chr == C.Tonda:
		await C.Tonda.say("Já jsem v klubu!" if Globals.r_end else "Joey nás přivedl sem. Proč asi?")
		return true
	if chr == C.Deda:
		await C.Deda.say("Tolik let… Věrka je zpátky!")
		return true
	return false


func _bench() -> void:
	await C.Joey.walk(get_marker_position("Verka") + Vector2(160, 20))
	await C.Verka.say("Ty jsi ale krásný pejsek! Na, máš piškot.")
	await C.Joey.say("Haf!")
	await C.Alica.say("Joey nic nenašel. Jen chtěl dobrotu.")
	await C.Tonda.say("Tak to je typický Joey.")
	await C.Tonda.say("Kdo vůbec věděl, kde poklad je?")
	await C.Alica.say("Jen Klub Hvězdička. Děda, Franta a Věrka.")
	C.Hanka.pose("grin")
	await C.Hanka.say("Tak to byla Věrka!")
	C.Hanka.pose()
	await C.Alica.say("Věrka bydlí daleko ve městě, Hanko.")
	Globals.r_verka = true
	await _whodunit()


func _whodunit() -> void:
	await C.Alica.say("Máme všechny stopy. Tak kdo vykopal poklad?")
	var mg: CanvasLayer = CulpritGame.new()
	add_child(mg)
	await mg.finished
	await _reveal()


func _reveal() -> void:
	await C.Alica.say("Paní od mlýna? Ale proč by kopala náš poklad?")
	C.Hanka.pose("grin")
	await C.Hanka.say("Zeptám se jí. Je hodná!")
	C.Hanka.pose()
	await C.Hanka.walk(C.Verka.position + Vector2(220, 0))
	await C.Hanka.say("Paní, nechcete s námi hledat poklad? Jsme Klub Hvězdička!")
	C.Verka.pose("surprised")
	await C.Verka.say("Klub… Hvězdička?")
	C.Verka.pose()
	await C.Verka.say("„Od hvězdičky sedm prken, pod prknem, které zpívá…“")
	C.Alica.pose("surprised")
	await C.Alica.say("Tu hádanku zná jen… Věrka!")
	C.Alica.pose()
	await C.Tonda.say("Běžím pro dědu!")
	C.Tonda.ignore_walkable_areas = true
	await C.Tonda.walk(Vector2(-150, 960))
	var deda := place("Deda", Vector2(-150, 960))
	deda.ignore_walkable_areas = true
	C.Tonda.walk(Vector2(1150, 980))
	await deda.walk(Vector2(760, 970))
	deda.ignore_walkable_areas = false
	C.Tonda.ignore_walkable_areas = false
	C.Verka.pose("surprised")
	await C.Verka.say("Honzo?!")
	await C.Deda.say("Věrko?!")
	C.Verka.pose("grin")
	await C.Deda.say("Tolik let!")
	await C.Verka.say("Letos jsem se vrátila. Bydlím tady ve mlýnku.")
	C.Verka.pose()
	await C.Alica.say("Tak vy jste vykopala poklad?")
	await C.Verka.say("Viděla jsem ceduli: Bagry od pondělí. Bála jsem se, že bagr poklad rozbije.")
	await C.Verka.say("Tak jsem ho minulou neděli za svítání vykopala. S lucernou a s hůlkou.")
	await C.Alica.say("A proč jste plechovku neotevřela?")
	await C.Verka.say("Poklad smí otevřít jen celý klub. Tak jsem čekala.")
	await _treasure()


func _treasure() -> void:
	await pop("Plechovka")
	await C.Deda.say("Tak… raz, dva, tři!")
	sfx("SKŘÍP!", Vector2(470, 560), 60)
	await pop("Tolar")
	C.Alica.pose("surprised")
	await C.Alica.say("Pravá stříbrná mince!")
	C.Alica.pose()
	await C.Deda.say("Stříbrný tolar. Našli jsme ho v bahně, když vypustili rybník. Je moc vzácný. Ale poklad klubu se neprodává.")
	await pop("Dalekohled")
	await C.Verka.say("Dalekohled po mém tátovi. Koukali jsme s ním na hvězdy.")
	await pop("Fotka")
	await C.Hanka.say("To jste vy?")
	await C.Verka.say("Honza, Franta a já.")
	await pop("Odznak")
	await C.Verka.say("A tenhle odznak je pro nového člena. Čekal tu na tebe, Tondo.")
	await C.Tonda.say("Já jsem v klubu!")
	get_prop("Odznak").hide()
	await pop("Dopis")
	C.Hanka.pose("point")
	await C.Hanka.say("A tady je obrázek! To je slepička!")
	C.Hanka.pose()
	await C.Verka.say("To nakreslil Franta. Byl nejmenší. Psát ještě neuměl.")
	await C.Deda.say("Franta říkal, že má svůj vlastní poklad. Nikdy neprozradil kde.")
	await I.Dopis.add()
	for p in ["Tolar", "Dalekohled", "Fotka", "Dopis"]:
		get_prop(p).hide()
	Globals.r_end = true
	await C.Alica.say("Klub Hvězdička drží spolu!")
	await the_end("Konec 3. dílu")
