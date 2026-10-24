@tool
extends "res://game/shared/story_room.gd"
## Story 10, the family kitchen at home on Monday evening: máma ("v noci mrzlo"), táta's box, the video
## call with babička and děda (hedgehogs wake up now; "a kdo podepisuje K.?"), "Kdo vzal Míšu a Šišu?"
## Hanka wants to be there tomorrow.

const Data := preload('room_domov10_state.gd')
const WhoGame := preload("res://game/minigames/who_10.gd")
const EVENING := Color(0.78, 0.74, 0.7)

var state: Data = load("res://game/rooms/domov10/room_domov10.tres")


func _on_room_entered() -> void:
	C.player.position = get_marker_position("Start")
	place("Hanka", get_marker_position("Start") + Vector2(-200, 20))
	place("Mama", get_marker_position("Mama")).pose("home")
	place("Tata", get_marker_position("Tata"))
	place("Joey", Vector2(1100, 1000))
	dark(EVENING, false)


func _on_room_transition_finished() -> void:
	if not Globals.q_box or Globals.q_day == 2:
		return
	Globals.phase = ""
	await C.Hanka.say("Alico! Co bylo ve škole?")
	await C.Alica.say("Míša a Šiša zmizeli! A já vedu pátrání.")
	await C.Hanka.say("Já taky chci být u toho!")
	await C.Mama.say("V noci mrzlo. Kdo by je nechal venku? Doufám, že jsou někde v teple.")
	await picture("res://assets/slides/video_call10.png", "Volají babička a děda")
	await radio("Ježci se teď na jaře budí a staví si pelíšky. Proto to seno.", "Deda", "res://assets/slides/video_call10.png")
	await radio("A kdo se podepisuje K.? Nejen malý Karel, ne?", "Babicka", "res://assets/slides/video_call10.png")
	Globals.q_home = true
	await C.Alica.say("Velké holínky, hobliny, prázdný háček, K. … Hani, pomůžeš mi?")
	if not Globals.q_who:
		var mg: CanvasLayer = WhoGame.new()
		add_child(mg)
		await mg.finished
		Globals.q_who = true
	await C.Alica.say("Velký Karel! Pan školník. Ale proč?")
	await C.Tata.say("Zítra je brigáda. Pojedeme všichni. I Hanka.")
	await C.Hanka.say("Hurá! Vezmu si mrkvičky v sáčku!")
	Globals.q_day = 2
	Globals.phase = "q_fieldday"
	R.goto_room("Skola10")


func on_click(node: Node) -> void:
	match node.script_name:
		"Krabice":
			await C.player.walk_to_clicked(Vector2(-240, 40))
			await C.player.say("Tátova krabice s dírkami. Co v ní je?")
		"Okno":
			await C.player.walk_to_clicked()
			await C.player.say("Venku je tma a mráz.")
		_: await super(node)
