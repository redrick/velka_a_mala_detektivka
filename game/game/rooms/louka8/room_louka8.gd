@tool
extends "res://game/shared/story_room.gd"
## Story 8, the meadow behind the chalupa with the hajný: hare prints (Y) and the hare in its form, the
## clean cut of a hare's bite against the frayed one of a deer (twigs); a straight line of fox prints to a
## mousehole (the mousing jump); boars rooting at the old oak (wider prints, two dots behind).

const Data := preload('room_louka8_state.gd')

var state: Data = load("res://game/rooms/louka8/room_louka8.tres")


func _on_room_entered() -> void:
	match C.player.last_room:
		"Les8": C.player.position = get_marker_position("ZLesa")
		_: C.player.position = get_marker_position("Start")
	Globals.bring_sister(self, Vector2(170, 10))
	place("Joey", joey_spot())
	if Globals.n_day == 1 and not Globals.n_guide:
		place("Hajny", get_marker_position("Hajny"))
		place("Tonda", Vector2(1620, 990))
	else:
		remove("Hajny")
		remove("Tonda")
	get_prop("Zajic").visible = not Globals.n_hare
	get_prop("Divocak").visible = not Globals.n_boar
	Globals.exit_arrow(self, "Zpet", true)
	Globals.exit_arrow(self, "DoLesa", false, _learned())
	get_hotspot("DoLesa").clickable = _learned() or Globals.n_trail


func _learned() -> bool:
	return Globals.n_hare and Globals.n_fox and Globals.n_boar


func joey_goal() -> Vector2:
	if not Globals.n_hare: return get_hotspot("ZajiciStopy").walk_to_point
	if not Globals.n_fox: return get_hotspot("LisciStopy").walk_to_point
	if not Globals.n_boar: return get_hotspot("Dub").walk_to_point
	return Vector2(1760, 960)


func on_click(node: Node) -> void:
	match node.script_name:
		"Zajic", "ZajiciStopy": await _hare()
		"LisciStopy", "Liska": await _fox()
		"Divocak", "Dub": await _boar()
		"Zpet":
			await C.player.walk_to_clicked()
			R.goto_room("Zahrada8")
		"DoLesa":
			await C.player.walk_to_clicked()
			R.goto_room("Les8")
		_: await super(node)


func on_character(chr: PopochiuCharacter, action: String, _item: PopochiuInventoryItem = null) -> bool:
	if action == "look" or chr == C.Alica or chr == C.Hanka or chr == C.Joey:
		return false
	await C.player.walk(chr.position + Vector2(-240, 20))
	match chr.script_name:
		"Hajny": await C.Hajny.say("Podívejte se na stopy. Každé zvíře má jinou." if not _learned() else "A teď do lesa. Tam vám ukážu ještě víc.")
		"Tonda": await C.Tonda.say("Já říkám zajíc! Nebo divočák!")
		_: return false
	return true


func _hare() -> void:
	await C.player.walk(get_hotspot("ZajiciStopy").walk_to_point)
	if Globals.n_hare:
		await C.player.say("Zajíčí stopy jako Y. Vedou podél křoví.")
		return
	await C.Tonda.say("Zajíc! Já to říkal!")
	var z := get_prop("Zajic")
	var tw := create_tween()
	tw.tween_property(z, "position", z.position + Vector2(-900, 40), 0.8)
	await tw.finished
	z.hide()
	await C.Hajny.say("Zajíčí stopy vypadají jako Y. Velké zadní nohy dopadnou až před ty přední.")
	await picture("res://assets/slides/twigs.png", "Kdo kousal?")
	await C.Hajny.say("Zajíc ukousne rovně, jako nůžky.")
	await C.Hajny.say("Srnka nemá nahoře přední zuby. Utrhne to a konec je roztřepený.")
	C.Hanka.pose("point")
	await C.Hanka.say("A zajíček je malý jako já. Na dědova sněhuláka by nedosáhl!")
	C.Hanka.pose()
	await C.Alica.say("A jeho stopy jdou podél křoví. Ke sněhulákům nevedou.")
	Globals.n_hare = true
	await _done()


func _fox() -> void:
	await C.player.walk(get_hotspot("LisciStopy").walk_to_point)
	if Globals.n_fox:
		await C.player.say("Liščí stopy v jedné řadě. K myší díře.")
		return
	await C.Alica.say("Tady jde stopa v rovné řadě. Jako po provázku.")
	await C.Hajny.say("To je liška. Ta nejí mrkev. Loví myši.")
	await pop("Liska")
	sfx("HOP!", Vector2(1000, 500), 70)
	await C.Hajny.say("Uslyší myš pod sněhem a skočí. Hop!")
	get_prop("Liska").hide()
	Globals.n_fox = true
	await _done()


func _boar() -> void:
	await C.player.walk(get_hotspot("Dub").walk_to_point)
	if Globals.n_boar:
		await C.player.say("Pod dubem je rozrytý sníh. Tady hledali žaludy divočáci.")
		return
	await C.Tonda.say("Divočák! Divočák sní všechno!")
	await C.Hajny.say("Divočáci tu ryli pod sněhem žaludy. Podívejte na jejich stopu.")
	C.Alica.pose("lens")
	await C.Alica.say("Je širší než srnčí. A vzadu má dvě tečky!")
	C.Alica.pose()
	await C.Hajny.say("Výborně. To jsou paspárky. Srnka je ve sněhu skoro nenechá.")
	var d := get_prop("Divocak")
	var tw := create_tween()
	tw.tween_property(d, "position", d.position + Vector2(800, 0), 1.0)
	await tw.finished
	d.hide()
	Globals.n_boar = true
	await _done()


func _done() -> void:
	if _learned():
		await C.Hajny.say("A teď pojďte do lesa. Ukážu vám všechny stopy pohromadě.")
		Globals.show_exit(self, "DoLesa")
		get_hotspot("DoLesa").clickable = true
