@tool
extends "res://game/shared/story_room.gd"
## Story 2 starts here: the girls' bedroom at night. Something above the ceiling taps, hisses
## and snores. Clicking the ceiling three times collects the three noises; then it's morning.

const Data := preload('room_loznice_state.gd')
const NIGHT := Color(0.28, 0.32, 0.58)
const NOISES := [["ŤUK! ŤUK!", Vector2(700, 60)], ["ŠŠŠŠ…", Vector2(1150, 70)], ["CHRRR…", Vector2(420, 70)]]

var state: Data = load("res://game/rooms/loznice/room_loznice.tres")


func _on_room_entered() -> void:
	C.player.position = get_marker_position("Start")
	Globals.bring_sister(self, Vector2(-170, 10))
	dark(NIGHT, false)
	glow(Vector2(240, 410), Color(0.7, 0.8, 1.0), 1.0, 3.0)
	glow(Vector2(960, 700), Color(1.0, 0.85, 0.6), 0.5, 3.5)


func _on_room_transition_finished() -> void:
	if Globals.k_noises > 0:
		return
	await get_tree().create_timer(0.6).timeout
	sfx("ŤUK…", Vector2(760, 60), 70)
	C.Hanka.pose("worried")
	await C.Hanka.say("Alico… slyšíš to? Co to je?")
	C.Hanka.pose()
	await C.Alica.say("Něco je nad námi na půdě. Poslechneme si to!")


func on_click(node: Node) -> void:
	match node.script_name:
		"Strop":
			await _noise()
		"Dvere":
			if Globals.k_noises < 3:
				await C.player.say("Je noc. Nejdřív zjistíme, co dělá ty zvuky.")
			else:
				await _morning()
		_:
			await super(node)


func on_look(node: Node) -> void:
	match node.script_name:
		"Strop": await C.player.say("Nad stropem je půda.")
		"Okno": await C.player.say("Venku je tma. Svítí měsíc.")
		"Postele": await C.player.say("Naše postýlky.")
		"Dvere": await C.player.say("Dveře do kuchyně.")
		_: await super(node)


func _noise() -> void:
	if Globals.k_noises >= 3:
		await C.player.say("Teď je ticho. Ráno to prozkoumáme!")
		return
	var n: Array = NOISES[Globals.k_noises]
	sfx(n[0], n[1])
	Globals.k_noises += 1
	match Globals.k_noises:
		1:
			C.Hanka.pose("surprised")
			await C.Hanka.say("Něco tam ťuká!")
			C.Hanka.pose()
			await C.Alica.say("Zapíšu si to. Zvuk číslo jedna: ťuk ťuk.")
		2:
			C.Hanka.pose("worried")
			await C.Hanka.say("A teď to syčí!")
			C.Hanka.pose()
			await C.Alica.say("Zvuk číslo dvě: šššš.")
		3:
			await C.Hanka.say("A chrápe to! Jako děda!")
			await C.Alica.say("Zvuk číslo tři: chrrr.")
			C.Alica.pose("grin")
			await C.Alica.say("Detektivky se nebojí. Ráno to prozkoumáme!")
			C.Alica.pose()
			await _morning()


func _morning() -> void:
	# the kitchen plays the breakfast scene (a script stops when its room is freed)
	Globals.phase = "k_breakfast"
	R.goto_room("Snidane")
