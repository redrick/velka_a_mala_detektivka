@tool
extends "res://game/shared/story_room.gd"
## Story 14, Točník's gate: the stone bridge over the rock-cut moat where the bears Martin and Agáta live, the
## gate tower. The Klub arrives (Věrka's drawing, XIV forgotten, the legend of turning round the hill), the
## kastelánka and her keys ("Klíče od hradu": XIV = 14). Later the bears are cleared of the rohlík.

const Data := preload('room_brana14_state.gd')
const KeysGame := preload("res://game/minigames/keys.gd")

var state: Data = load("res://game/rooms/brana14/room_brana14.tres")


func _on_room_entered() -> void:
	match C.player.last_room:
		"Nadvori14": C.player.position = get_hotspot("Brana").walk_to_point + Vector2(-120, 0)
		_: C.player.position = get_marker_position("Start")
	Globals.bring_sister(self, Vector2(-150, 8))
	place("Joey", get_marker_position("Joey"))
	if not Globals.h_keys or (Globals.h_rohlik and not Globals.h_bears):
		place("Kastelanka", get_marker_position("Kastelanka"))
	else:
		remove("Kastelanka")
	if not Globals.h_keys:
		for who in ["Deda", "Verka", "Tonda", "Betka"]:
			place(who, get_marker_position(who))
	else:
		for who in ["Deda", "Verka", "Tonda", "Betka"]:
			remove(who)
	if Globals.h_rohlik and not Globals.h_bears:
		place("Tonda", get_marker_position("Tonda"))
	hidden_thing(null, "Klicek", "h_found", 10, "")


func _on_room_transition_finished() -> void:
	if not Globals.h_intro:
		await _intro()


func joey_goal() -> Vector2:
	if not Globals.h_keys: return get_marker_position("Kastelanka") + Vector2(-200, 0)
	if Globals.h_rohlik and not Globals.h_bears: return get_hotspot("Prikop").walk_to_point
	return get_hotspot("Brana").walk_to_point


func _intro() -> void:
	C.Verka.pose("happy")
	await C.Deda.say("Tuhle věž znám. To je hrad Točník!")
	await C.Hanka.say("Tam jsme už byly!")
	await picture("res://assets/slides/b_tin.png")
	await C.Verka.say("Tu kresbu jsem kreslila já. Když jsme byli malí.")
	await C.Verka.say("Ale co je XIV… to už nevím.")
	await C.Deda.say("Já taky ne.")
	await C.Tonda.say("Pověst říká: kdo chtěl na hrad, musel se třikrát otočit kolem hory.")
	await C.Hanka.say("Raz, dva, tři! Točí se mi hlava!")
	await C.Alica.say("Proto se ten hrad jmenuje Točník!")
	Globals.h_intro = true


func on_click(node: Node) -> void:
	if await hidden_thing(node, "Klicek", "h_found", 10, "Klíček"):
		return
	match node.script_name:
		"Brana":
			await C.player.walk_to_clicked()
			if not Globals.h_keys:
				await C.player.say("Brána je zamčená. Klíče má paní kastelánka.")
				return
			R.goto_room("Nadvori14")
		"Prikop": await _moat()
		"Kopec":
			await C.player.walk_to_clicked()
			await C.player.say("Dole pod Točníkem stojí starý hrad Žebrák. Točník stojí nad ním.")
		_: await super(node)


func on_character(chr: PopochiuCharacter, action: String, _item: PopochiuInventoryItem = null) -> bool:
	if action == "look" or chr == C.Alica or chr == C.Hanka or chr == C.Joey:
		return false
	await C.player.walk(chr.position + Vector2(-220, 0))
	match chr.script_name:
		"Kastelanka":
			if not Globals.h_keys:
				await _keys()
			elif Globals.h_rohlik and not Globals.h_bears:
				await _moat()
			else:
				await C.Kastelanka.say("Vítejte na Točníku, Klube Hvězdičko!")
		"Deda": await C.Deda.say("Na Točníku jsme byli s Klubem jednou na výletě. Před šedesáti lety.")
		"Verka": await C.Verka.say("XIV… Ta čísla mi něco připomínají. Ale co?")
		"Tonda":
			if Globals.h_rohlik:
				await C.Tonda.say("Medvědi mají rádi rohlíky!")
			else:
				await C.Tonda.say("Na hradě prý straší!")
		"Betka": await C.Betka.say("Já si budu všechno kreslit.")
		_: return false
	return true


func _keys() -> void:
	await C.Alica.say("Dobrý den, paní kastelánko!")
	C.Kastelanka.pose("keys")
	await C.Kastelanka.say("Vítejte na Točníku, Klube Hvězdičko! Tady mám klíče od celého hradu.")
	await C.Kastelanka.say("Na klíčích jsou římská čísla. Jako za krále Václava IV., který hrad postavil.")
	await C.Kastelanka.say("Pomůžete mi dát každý klíč ke správným dveřím?")
	var mg: CanvasLayer = KeysGame.new()
	add_child(mg)
	await mg.finished
	C.Kastelanka.pose()
	Globals.h_keys = true
	await C.Alica.say("Jednička před pětkou je čtyřka. Takže XIV je čtrnáct!")
	await C.Hanka.say("Čtrnáct čeho?")
	await C.Alica.say("To zjistíme!")
	await C.Kastelanka.say("Tak pojďte dál.")
	R.goto_room("Nadvori14")


func _moat() -> void:
	await C.player.walk(get_hotspot("Prikop").walk_to_point)
	if not Globals.h_rohlik or Globals.h_bears:
		await picture("res://assets/slides/k_bears.png", "Medvědi Martin a Agáta")
		await C.Hanka.say("Ahoj, medvídci!")
		return
	await C.Tonda.say("To byli medvědi! Mají hlad!")
	await picture("res://assets/slides/k_bears.png", "Medvědi Martin a Agáta")
	await C.Kastelanka.say("Medvědi z příkopu ven nemůžou. Dostávají jablka a mrkev.")
	await C.Alica.say("Takže medvědi to nebyli.")
	await C.Tonda.say("A co Joey? Ten sní všechno!")
	await C.Alica.say("Joey celou dobu spal. Viděla jsem ho.")
	Globals.h_bears = true
	await C.Kastelanka.say("Už se stmívá. Pojďte do sálu, tam budete spát.")
	await C.Alica.say("Do sálu se jde přes nádvoří.")
