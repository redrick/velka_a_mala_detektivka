@tool
extends "res://game/shared/story_room.gd"
## Story 9, the village library: the librarian shows the borrowing card in the book (A. and J. in February
## 1966, Tonda in December); Tonda, a suspect, can't read the star code and wants to learn it.

const Data := preload('room_knihovna9_state.gd')

var state: Data = load("res://game/rooms/knihovna9/room_knihovna9.tres")


func _on_room_entered() -> void:
	C.player.position = get_marker_position("Start")
	Globals.bring_sister(self, Vector2(170, 10))
	place("Joey", joey_spot())
	place("Knihovnice", get_marker_position("Knihovnice"))
	place("Tonda", get_marker_position("Tonda"))
	Globals.exit_arrow(self, "Ven", true)


func joey_goal() -> Vector2:
	if not Globals.z_card: return C.Knihovnice.position + Vector2(-240, 40)
	if not Globals.z_tonda: return C.Tonda.position + Vector2(-240, 40)
	return get_hotspot("Ven").walk_to_point


func on_click(node: Node) -> void:
	match node.script_name:
		"Pult": await _borrowing_card()
		"Police":
			await C.player.walk_to_clicked()
			await C.player.say("Tolik knížek! Pohádky, zvířata, hvězdy…")
		"Ven":
			await C.player.walk_to_clicked()
			R.goto_room("Kuchyne9")
		_: await super(node)


func on_character(chr: PopochiuCharacter, action: String, _item: PopochiuInventoryItem = null) -> bool:
	if action == "look" or chr == C.Alica or chr == C.Hanka or chr == C.Joey:
		return false
	await C.player.walk(chr.position + Vector2(-240, 20))
	match chr.script_name:
		"Knihovnice": await _borrowing_card()
		"Tonda": await _tonda()
		_: return false
	return true


func _borrowing_card() -> void:
	if Globals.z_card:
		await C.Knihovnice.say("Tahle knížka je skoro starší než vaše babička.")
		return
	await C.Alica.say("Dobrý den. Kdo si půjčoval tuhle knížku?")
	await C.Knihovnice.say("Podívejte se na lístek vzadu v knížce. Tam se píše každý, kdo si ji půjčil.")
	await picture("res://assets/slides/library_card9.png", "Lístek s výpůjčkami")
	await C.Alica.say("H. a J. v únoru 1966. A Tonda v prosinci!")
	await C.Hanka.say("H. jako Honza? To je náš děda!")
	await C.Knihovnice.say("Tahle knížka je skoro starší než vaše babička.")
	await C.Knihovnice.say("A minulý týden si ji půjčila zase vaše babička. Odnesla ji v tašce.")
	Globals.z_card = true
	await C.Hanka.say("Tonda je tady!")


func _tonda() -> void:
	if Globals.z_tonda:
		await C.Tonda.say("Naučíte mě to tajné písmo? Prosím!")
		return
	await C.Alica.say("Tondo! Tys měl tuhle knížku v prosinci. Nepsal jsi tajnou zprávu?")
	await C.Tonda.say("Jakou zprávu? Ukaž… To jsou samé hvězdičky a tečky. To neumím přečíst!")
	await C.Tonda.say("Naučíte mě to? Prosím!")
	await C.Alica.say("Tonda by to přečetl jen s klíčem. A klíč nemá. Škrtám.")
	Globals.z_tonda = true
	await C.Hanka.say("Paní Věrka je taky z Klubu. Půjdeme ke mlýnu!")
