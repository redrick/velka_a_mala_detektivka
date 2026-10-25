extends "res://tests/story_test.gd"
## The puzzles of stories 13-14, on their own: each level gets a few clicks, a hint and an undo,
## then is solved; the puzzle must close after its last level.

const GAMES := ["cuts", "rock", "who_13", "quiz_13", "dam", "keys", "who_14", "quiz_14", "holes", "spell_14"]


func run() -> void:
	await get_tree().create_timer(0.5).timeout
	for g in GAMES:
		var mg: Node = load("res://game/minigames/%s.gd" % g).new()
		mg.set_meta("solving", true)
		var done := [false]
		mg.finished.connect(func(): done[0] = true)
		add_child(mg)
		var levels: int = mg._levels()
		for i in levels:
			await get_tree().process_frame
			for c in [Vector2i(0, 0), Vector2i(1, 0), Vector2i(2, 1), Vector2i(1, 1), Vector2i(3, 4), Vector2i(0, 5),
					Vector2i(4, 2), Vector2i(4, 0), Vector2i(2, 3), Vector2i(5, 3), Vector2i(-1, 2), Vector2i(40, 40)]:
				if mg.busy:
					break
				mg._cell(c)
				await get_tree().create_timer(0.1).timeout
			if g.begins_with("quiz"):
				mg._answer(false)
				mg._answer(true)
			mg._dir(Vector2i.RIGHT)
			mg._hint()
			mg._undo()
			await get_tree().create_timer(0.6).timeout
			await mg.solve_for_test()
			var t := 0.0
			while not done[0] and mg.level == i and t < 10.0:
				await get_tree().process_frame
				t += get_process_delta_time()
		check(done[0], "%s: all %d levels solved and closed" % [g, levels])
