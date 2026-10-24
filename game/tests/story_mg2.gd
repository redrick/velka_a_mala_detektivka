extends "res://tests/story_test.gd"
## The second puzzles of stories 4-12, on their own: each level gets a few clicks, a hint and an undo,
## then is solved; the puzzle must close after its last level.

const GAMES := ["radio", "mittens", "birds", "joey_morning", "scale", "parade", "pens", "pattern", "seating"]


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
			for c in [Vector2i(0, 0), Vector2i(1, 0), Vector2i(2, 1), Vector2i(1, 1), Vector2i(3, 4), Vector2i(0, 5)]:
				mg._cell(c)
				await get_tree().create_timer(0.1).timeout
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
