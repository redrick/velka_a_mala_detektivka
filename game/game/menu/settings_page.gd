extends VBoxContainer
## Settings shared by the main menu and the in-game menu: language, fullscreen or window, and the
## text options. The menus rebuild it when Lang or Prefs change, so the lit buttons stay current.

const Kit := preload("res://game/menu/ui_kit.gd")


func _init() -> void:
	alignment = BoxContainer.ALIGNMENT_CENTER
	add_theme_constant_override("separation", 26)
	add_child(Kit.option_row(tr("Jazyk:"),
			[["Čeština", "cs"], ["English", "en"]], Lang.current(), Lang.set_locale))
	add_child(Kit.option_row(tr("Obrazovka:"),
			[[tr("Celá obrazovka"), true], [tr("Okno"), false]], Prefs.fullscreen, Prefs.set_fullscreen))
	add_child(Kit.option_row(tr("Text dál:"),
			[[tr("Kliknutím"), false], [tr("Automaticky"), true]],
			Prefs.auto_continue, Prefs.set_auto_continue))
	add_child(Kit.option_row(tr("Rychlost textu:"),
			[[tr("Pomalu"), "slow"], [tr("Normálně"), "normal"], [tr("Rychle"), "fast"]],
			Prefs.speed, Prefs.set_speed))
	add_child(Kit.option_row(tr("Hudba:"),
			[[tr("Vypnuto"), "off"], [tr("Potichu"), "quiet"], [tr("Nahlas"), "normal"]],
			Prefs.music, Prefs.set_music))
	add_child(Kit.label(tr("Hudba: Kevin MacLeod (incompetech.com), licence CC BY 4.0"), 20, Color("8a7f6a")))
