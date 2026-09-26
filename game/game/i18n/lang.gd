extends Node
## Current language (Czech or English), remembered between sessions in user://settings.cfg.

signal changed

const SETTINGS := "user://settings.cfg"


func _ready() -> void:
	var cfg := ConfigFile.new()
	cfg.load(SETTINGS)
	TranslationServer.set_locale(cfg.get_value("ui", "locale", "cs"))


func current() -> String:
	return TranslationServer.get_locale().substr(0, 2)


func set_locale(locale: String) -> void:
	if locale == current():
		return
	TranslationServer.set_locale(locale)
	var cfg := ConfigFile.new()
	cfg.load(SETTINGS)
	cfg.set_value("ui", "locale", locale)
	cfg.save(SETTINGS)
	changed.emit()
