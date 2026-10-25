extends "res://tests/story_test.gd"
## Every minigame from the main menu's list, every level: the paper sheet must stay 1780 x 1032 (content that
## doesn't fit makes it grow off the screen) and the board must lie inside it.

const Menu := preload("res://game/menu/menu_ui.gd")


func run() -> void:
	await get_tree().create_timer(0.5).timeout
	for entry in Menu.MINIGAMES:
		var mg: Node = entry[2].new()
		mg.set_meta("solving", true)
		add_child(mg)
		for i in mg._levels():
			if i > 0:
				mg.start_level(i)
			for k in 4:
				await get_tree().process_frame
			var sheet: Control = mg.get_child(1)
			var r: Rect2 = mg.board.get_global_rect()
			var ok: bool = sheet.size.y <= 1033 and sheet.size.x <= 1781 and r.position.x >= 70 and r.end.x <= 1850 \
				and r.position.y >= 24 and r.end.y <= 1056
			check(ok, "%s %d: sheet %s, board %s" % [entry[0], i + 1, sheet.size, r])
		mg.queue_free()
		await get_tree().process_frame
