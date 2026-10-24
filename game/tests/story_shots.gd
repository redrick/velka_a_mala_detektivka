extends "res://tests/story_test.gd"
## Screenshots of the second puzzles (first and last level) into user://shots/. Run with a window.

const GAMES := ["radio", "mittens", "birds", "joey_morning", "scale", "parade", "pens", "pattern", "seating"]


func run() -> void:
	DirAccess.make_dir_recursive_absolute("user://shots")
	await get_tree().create_timer(0.5).timeout
	for g in GAMES:
		var mg: Node = load("res://game/minigames/%s.gd" % g).new()
		mg.set_meta("solving", true)
		add_child(mg)
		for i in [0, mg._levels() - 1]:
			mg.start_level(i)
			await get_tree().create_timer(0.8).timeout
			mg._cell(Vector2i(1, 1))
			mg._hint()
			await get_tree().create_timer(0.5).timeout
			get_viewport().get_texture().get_image().save_png("user://shots/%s_%d.png" % [g, i])
		mg.queue_free()
	check(true, "shots taken")
