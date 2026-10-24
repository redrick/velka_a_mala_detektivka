@tool
extends "res://game/shared/story_room.gd"
## Story 8, the garden with the snowman family. Morning 1: the parsnip noses are gone, even from děda's
## tall snowman; Hanka finds a frayed stub; the prints are trampled by Joey; Tonda says "zajíc!"; the hajný
## sends them to learn the tracks. Morning 2 (after the clean-page night): the noses are gone again and the
## smooth snow has one kind of print → "Kdo okusuje nosy?" → follow the deer (minigame).

const Data := preload('room_zahrada8_state.gd')
const WhoGame := preload("res://game/minigames/who_8.gd")
const TrailGame := preload("res://game/minigames/trail.gd")

var state: Data = load("res://game/rooms/zahrada8/room_zahrada8.tres")


func _on_room_entered() -> void:
	match C.player.last_room:
		"Louka8": C.player.position = get_marker_position("ZLouky")
		_: C.player.position = get_marker_position("Start")
	Globals.bring_sister(self, Vector2(170, 10))
	place("Joey", joey_spot())
	if Globals.n_day == 1 and not Globals.n_hajny:
		place("Tonda", get_marker_position("Tonda"))
	else:
		remove("Tonda")
	if Globals.n_trampled and Globals.n_stub and Globals.n_high and not Globals.n_hajny:
		place("Hajny", get_marker_position("Hajny"))
	else:
		remove("Hajny")
	get_prop("Pahyl").visible = Globals.n_day == 1 and not Globals.n_stub
	get_prop("Stopy").visible = Globals.n_day == 1
	get_prop("CisteStopy").visible = Globals.n_day == 2
	Globals.exit_arrow(self, "NaLouku", false, Globals.n_hajny)
	get_hotspot("NaLouku").clickable = Globals.n_hajny


func _on_room_transition_finished() -> void:
	if Globals.phase == "n_morning":
		Globals.phase = ""
		_card(["Ráno…" if Globals.n_day == 1 else "Druhé ráno…"], 1.6)
		await get_tree().create_timer(2.0).timeout
		if Globals.n_day == 1:
			C.Hanka.pose("point")
			await C.Hanka.say("Sněhuláci nemají nosy! Někdo je v noci snědl!")
			C.Hanka.pose()
			await C.Alica.say("A Joey tu všechno pošlapal. Joey!")
		else:
			await C.Alica.say("Zase nemají nosy! Ale sníh byl hladký. Jako čistý papír!")


func joey_goal() -> Vector2:
	if Globals.n_day == 1:
		if not Globals.n_stub: return get_prop("Pahyl").position + Vector2(-200, -40)
		if not Globals.n_high: return Vector2(900, 960)
		if not Globals.n_trampled: return get_prop("Stopy").position + Vector2(-260, -40)
		return Vector2(1760, 960)
	if not Globals.n_clean: return get_prop("CisteStopy").position + Vector2(-260, -40)
	return get_hotspot("NaLouku").walk_to_point


func on_click(node: Node) -> void:
	match node.script_name:
		"Snehulaci":
			await C.player.walk(Vector2(900, 960))
			if Globals.n_day == 2:
				await C.player.say("Nosy jsou zase pryč.")
			elif C.player == C.Alica:
				C.Alica.pose("lens")
				await C.Alica.say("Nosy jsou pryč. I u dědova sněhuláka. A ten je vyšší než já!")
				C.Alica.pose()
				Globals.n_high = true
				await _check()
			else:
				await C.Hanka.say("Dědův sněhulák je hrozně vysoký. Alico, podívej se lupou!")
		"Pahyl":
			await C.player.walk_to_clicked(Vector2(-200, -40))
			await hand_over(C.Hanka, "Něco tam leží u země. Hani, ty jsi blíž!")
			C.Hanka.pose("stub")
			await C.Hanka.say("Kousek nosu! Je celý roztřepený.")
			C.Hanka.pose()
			get_prop("Pahyl").hide()
			I.Pahyl.add()
			Globals.n_stub = true
			await _check()
		"Stopy":
			await C.player.walk_to_clicked(Vector2(-260, -40))
			await C.player.say("Samé tlapky od Joeyho. Všechno je pošlapané!")
			await C.Joey.say("Haf?")
			Globals.n_trampled = true
			await _check()
		"CisteStopy": await _clean()
		"Dum":
			await C.player.walk_to_clicked()
			R.goto_room("Kuchyne8")
		"NaLouku":
			await C.player.walk_to_clicked()
			R.goto_room("Louka8")
		_: await super(node)


func on_character(chr: PopochiuCharacter, action: String, _item: PopochiuInventoryItem = null) -> bool:
	if action == "look" or chr == C.Alica or chr == C.Hanka or chr == C.Joey:
		return false
	await C.player.walk(chr.position + Vector2(-240, 20))
	match chr.script_name:
		"Tonda": await C.Tonda.say("To byl zajíc! Zajíci mají rádi mrkev. Každý to ví!")
		"Hajny": await _hajny()
		_: return false
	return true


func _check() -> void:
	if Globals.n_day != 1 or Globals.n_hajny or not (Globals.n_stub and Globals.n_high and Globals.n_trampled):
		return
	await C.Tonda.say("Zajíc! Určitě zajíc!")
	place("Hajny", Vector2(2050, 920))
	C.Hajny.ignore_walkable_areas = true
	await C.Hajny.walk(get_marker_position("Hajny"))
	C.Hajny.ignore_walkable_areas = false
	await _hajny()


func _hajny() -> void:
	if Globals.n_hajny:
		await C.Hajny.say("Na louce vám ukážu stopy.")
		return
	await C.Hajny.say("Dobré ráno! Co se stalo?")
	await C.Alica.say("Někdo snědl nosy sněhulákům. Tonda říká, že zajíc.")
	await C.Hajny.say("Zajíc? Možná. Možná ne. Nejdřív se naučíte stopy. Přečtete si to sami.")
	await C.Hajny.say("Pojďte za mnou na louku.")
	Globals.n_hajny = true
	Globals.show_exit(self, "NaLouku")
	get_hotspot("NaLouku").clickable = true
	C.Hajny.ignore_walkable_areas = true
	await C.Hajny.walk(Vector2(2050, 920))
	C.Hajny.ignore_walkable_areas = false
	remove("Hajny")
	if has_character("Tonda"):
		C.Tonda.ignore_walkable_areas = true
		await C.Tonda.walk(Vector2(-150, 960))
		C.Tonda.ignore_walkable_areas = false
	remove("Tonda")


#region Morning 2 ##################################################################################
func _clean() -> void:
	await C.player.walk_to_clicked(Vector2(-260, -40))
	if not Globals.n_clean:
		C.Alica.pose("lens")
		await C.Alica.say("Na čistém sněhu je jen jeden druh stopy!")
		await C.Alica.say("Dvě špičaté kapky. Úzké srdíčko. A vzadu žádné tečky.")
		C.Alica.pose()
		await C.Hanka.say("A Joey spal celou noc v chodbě. Tlapky tu nejsou.")
		Globals.n_clean = true
	if not Globals.n_who:
		var mg: CanvasLayer = WhoGame.new()
		add_child(mg)
		await mg.finished
		Globals.n_who = true
		await C.Alica.say("Srnka! Dosáhne vysoko, trhá a nemá tečky. Půjdeme po její stopě!")
	if not Globals.n_trail:
		var mg2: CanvasLayer = TrailGame.new()
		add_child(mg2)
		await mg2.finished
		Globals.n_trail = true
		await C.Hanka.say("Stopa vede dírou v plotě. Přes louku do lesa!")
		Globals.phase = "n_follow"
		R.goto_room("Les8")
#endregion
