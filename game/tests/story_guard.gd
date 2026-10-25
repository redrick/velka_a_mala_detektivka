extends "res://tests/story_test.gd"
## A second click while the first click's scene still runs is ignored (Globals.click_busy), the running scene
## goes on, and a mark left by a cancelled scene wears off.


func run() -> void:
	await start("Louka13", 13)
	var tent: Node = R.current.get_hotspot("Stan")
	var deda := C.get_character("Deda")
	InGameMenu.history.clear()
	E.clicked = tent
	tent.handle_command(MOUSE_BUTTON_LEFT)
	await get_tree().create_timer(0.3).timeout
	tent.handle_command(MOUSE_BUTTON_LEFT)
	E.clicked = deda
	deda.handle_command(MOUSE_BUTTON_LEFT)
	E.clicked = null
	await idle()
	check(InGameMenu.history.size() == 1, "three quick clicks, one scene (%d lines)" % InGameMenu.history.size())
	E.clicked = deda
	await deda.handle_command(MOUSE_BUTTON_LEFT)
	await idle()
	check(InGameMenu.history.size() == 2, "the next click after the scene works")
	R.current.set_meta("click_busy", true)
	await get_tree().create_timer(3.0 * Engine.time_scale).timeout
	check(not Globals.click_busy(), "a stale mark wears off")
