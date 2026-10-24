extends Node
## Headless story test runner. Not an autoload in the project: tools/test_story.sh adds it to
## project.godot for one run and removes it again. Plays a story by calling the room scripts' click
## handlers directly (synthetic clicks don't move Popochiu's hover), and solves every minigame that
## opens. A test script (tests/story_N.gd) extends tests/story_test.gd and implements run().
##
##   godot --headless --path game -- --test=res://tests/story_4.gd

var fails := 0
var checks := 0


func _ready() -> void:
	var path := ""
	for a in OS.get_cmdline_user_args():
		if a.begins_with("--test="):
			path = a.substr(7)
	if path.is_empty():
		return
	var was_auto: bool = Prefs.auto_continue
	var was_speed: String = Prefs.speed
	Prefs.set_auto_continue(true)
	Prefs.set_speed("fast")
	Engine.time_scale = 4.0
	while not (E.in_room and is_instance_valid(R.current) and R.current.script_name == "Menu"):
		await get_tree().process_frame
	var t: Node = load(path).new()
	t.runner = self
	add_child(t)
	await t.run()
	print("TEST %s: %d/%d checks passed" % [path.get_file(), checks - fails, checks])
	Prefs.set_auto_continue(was_auto)
	Prefs.set_speed(was_speed)
	get_tree().quit(1 if fails > 0 else 0)
