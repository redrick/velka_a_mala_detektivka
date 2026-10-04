extends Node
## Options chosen in the settings menu, remembered in user://settings.cfg: whether dialog lines
## wait for a click (default) or continue on their own, the typing speed, fullscreen (default)
## or a window, and the background music volume.

signal changed

const SETTINGS := "user://settings.cfg"
const SPEEDS := {"slow": 0.06, "normal": 0.03, "fast": 0.01}

var auto_continue := false
var speed := "normal"
var fullscreen := true
## Background music: "off", "quiet" (default) or "normal".
var music := "quiet"


func _ready() -> void:
	var cfg := ConfigFile.new()
	cfg.load(SETTINGS)
	auto_continue = cfg.get_value("text", "auto_continue", false)
	speed = cfg.get_value("text", "speed", "normal")
	fullscreen = cfg.get_value("display", "fullscreen", true)
	music = cfg.get_value("sound", "music", "quiet")
	_apply()
	_apply_window()


func set_auto_continue(value: bool) -> void:
	auto_continue = value
	_apply()
	_save()


func set_speed(value: String) -> void:
	speed = value
	_apply()
	_save()


func set_music(value: String) -> void:
	music = value
	_save()
	changed.emit()


func set_fullscreen(value: bool) -> void:
	fullscreen = value
	_apply_window()
	_save()
	changed.emit()


func _apply_window() -> void:
	if DisplayServer.get_name() == "headless":
		return
	if fullscreen:
		DisplayServer.window_set_mode(DisplayServer.WINDOW_MODE_FULLSCREEN)
		return
	DisplayServer.window_set_mode(DisplayServer.WINDOW_MODE_WINDOWED)
	var screen := DisplayServer.window_get_current_screen()
	var size := Vector2i(1280, 720)
	DisplayServer.window_set_size(size)
	DisplayServer.window_set_position(
			DisplayServer.screen_get_position(screen) + (DisplayServer.screen_get_size(screen) - size) / 2)


func _apply() -> void:
	E.settings.auto_continue_text = auto_continue
	E.text_speed = SPEEDS.get(speed, SPEEDS.normal)
	changed.emit()


func _save() -> void:
	var cfg := ConfigFile.new()
	cfg.load(SETTINGS)
	cfg.set_value("text", "auto_continue", auto_continue)
	cfg.set_value("text", "speed", speed)
	cfg.set_value("display", "fullscreen", fullscreen)
	cfg.set_value("sound", "music", music)
	cfg.save(SETTINGS)
