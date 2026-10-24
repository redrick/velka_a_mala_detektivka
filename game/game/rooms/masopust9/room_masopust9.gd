@tool
extends "res://game/shared/story_room.gd"
## Story 9, Masopust on the village green. First the masks get lined up ("Masopustní průvod"). Three masks
## wear a star: the kobyla, the kominík and the bába s nůší. "Kdo napsal zprávu?" (minigame); Hanka sees the
## zigzag shawl; the bába is babička. Sixty years ago a boy left her a coded slip: PRIJD NA MASOPUST, BUDU
## MEDVED (decoded together); the bear is děda.

const Data := preload('room_masopust9_state.gd')
const WhoGame := preload("res://game/minigames/who_9.gd")
const CipherGame := preload("res://game/minigames/cipher.gd")
const ParadeGame := preload("res://game/minigames/parade.gd")

var state: Data = load("res://game/rooms/masopust9/room_masopust9.tres")


func _on_room_entered() -> void:
	C.player.position = get_marker_position("Start")
	Globals.bring_sister(self, Vector2(170, 10))
	C.Alica.set_outfit("alicao")
	C.Hanka.set_outfit("hankab")
	place("Joey", joey_spot())
	place("Tonda", get_marker_position("Kobyla")).pose("kobyla")
	place("Verka", get_marker_position("Kominik")).pose("kominik")
	place("Babicka", get_marker_position("Baba")).pose("baba")
	place("Deda", get_marker_position("Medved")).pose("bear")
	place("Rybar", get_marker_position("Franta"))
	# under the masks nobody knows who is who (Globals.dress() puts the names back on the way out)
	for mask in [["Tonda", "Kobyla"], ["Verka", "Kominík"], ["Babicka", "Bába s nůší"], ["Deda", "Medvěd"], ["Rybar", "Medvědář"]]:
		C.get_character(mask[0]).description = mask[1]


func _on_room_exited() -> void:
	super()
	Globals.dress()


func _on_room_transition_finished() -> void:
	if not Globals.z_parade:
		await C.Rybar.say("Holky, průvod se řadí a všichni se pletou. Pomůžete nám?")
		var mg: CanvasLayer = ParadeGame.new()
		add_child(mg)
		await mg.finished
		Globals.z_parade = true
	if not Globals.z_who:
		sfx("TRA-TA-TÁ!", Vector2(1200, 260), 90)
		await C.Alica.say("Masopustní průvod! Tři masky mají hvězdičku: kobyla, kominík a bába s nůší.")
		await C.Hanka.say("Kdo z nich napsal zprávu?")


func joey_goal() -> Vector2:
	return C.Babicka.position + Vector2(-240, 60)


func on_click(node: Node) -> void:
	if node.script_name == "Pruvod":
		await _who()
	else:
		await super(node)


func on_character(chr: PopochiuCharacter, action: String, _item: PopochiuInventoryItem = null) -> bool:
	if action == "look" or chr == C.Alica or chr == C.Hanka:
		return false
	match chr.script_name:
		"Joey": return false
		"Tonda":
			await C.player.walk(chr.position + Vector2(0, 130))
			await C.Tonda.say("Íhahá! Jsem kobyla! A mám tenisky.")
		"Verka":
			await C.player.walk(chr.position + Vector2(0, 130))
			await C.Verka.say("Kominík nosí štěstí! Hvězdička na klobouku taky.")
		"Rybar":
			await C.player.walk(chr.position + Vector2(0, 130))
			await C.Rybar.say("Já vodím medvěda. Písmo jsme vymysleli s Honzou, ale hvězdičku nemám.")
		"Deda":
			await C.player.walk(chr.position + Vector2(0, 130))
			await C.Deda.say("Brum brum! Medvěd hvězdičku nemá.")
		"Babicka":
			await _who()
		_:
			return false
	return true


func _who() -> void:
	await C.player.walk(get_marker_position("Baba") + Vector2(0, 130))
	if Globals.z_who:
		await C.Babicka.say("Zatancujeme si, medvěde?")
		return
	await C.Alica.say("STOP, detektive! Kdo napsal zprávu?")
	var mg: CanvasLayer = WhoGame.new()
	add_child(mg)
	await mg.finished
	Globals.z_who = true
	C.Hanka.pose("point")
	await C.Hanka.say("Bába má na šátku zoubky! A voní levandulí!")
	C.Hanka.pose()
	await C.Joey.walk(C.Babicka.position + Vector2(-180, 60))
	await C.Joey.say("Haf haf!")
	C.Babicka.pose("unmask")
	await C.Babicka.say("Vy jste mě poznaly, detektivky!")
	await C.Babicka.say("Před šedesáti lety mi jeden kluk dal do téhle knížky zprávu.")
	await C.Babicka.say("A já ji rozluštila sama. Bez klíče.")
	await picture("res://assets/slides/slip_old.png", "Zpráva z roku 1966")
	var mg2: CanvasLayer = CipherGame.new()
	mg2.messages = ["PRIJD NA|MASOPUST|BUDU MEDVED"]
	add_child(mg2)
	await mg2.finished
	await C.Alica.say("Přijď na masopust. Budu medvěd!")
	C.Deda.pose("bearface")
	await C.Deda.say("Ten kluk jsem byl já. A medvěd jsem každý rok.")
	await C.Babicka.say("Chtěla jsem, abyste to dobrodružství zažily taky.")
	sfx("TRA-LA-LA!", Vector2(1300, 240), 80)
	await C.Hanka.say("Medvěd tancuje s bábou!")
	await C.Alica.say("Babička byla první detektivka v rodině!")
	Globals.z_end = true
	await the_end("Konec 9. dílu")
