extends RefCounted
## Shared look for the main menu and the in-game menu: hand-inked paper panels and yellow buttons
## drawn in art/menu.py, táta's handwriting (TataHand), dark ink text, yellow outlined titles.

const ART := "res://assets/menu/"
const FONT := preload("res://assets/fonts/TataHand.ttf")
const INK := Color("2b2118")
const TITLE_YELLOW := Color("ffd43b")
const LOCALES := {"cs": "Čeština", "en": "English"}


static func theme(size := 30) -> Theme:
	var t := Theme.new()
	t.default_font = FONT
	t.default_font_size = size
	return t


static func skin(skin_name: String, margin: float) -> StyleBoxTexture:
	var sb := StyleBoxTexture.new()
	sb.texture = load(ART + skin_name + ".png")
	sb.set_texture_margin_all(margin)
	sb.set_content_margin_all(margin * 0.9)
	return sb


static func panel() -> PanelContainer:
	var p := PanelContainer.new()
	p.add_theme_stylebox_override("panel", skin("panel", 36))
	return p


static func title(text: String, size: int) -> Label:
	var l := label(text, size, TITLE_YELLOW)
	l.add_theme_color_override("font_outline_color", INK)
	l.add_theme_constant_override("outline_size", maxi(10, size / 5))
	return l


static func label(text: String, size: int, color := INK, outlined := false) -> Label:
	var l := Label.new()
	l.text = text
	l.auto_translate_mode = Node.AUTO_TRANSLATE_MODE_DISABLED
	l.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
	l.add_theme_font_size_override("font_size", size)
	l.add_theme_color_override("font_color", color)
	if outlined:
		l.add_theme_color_override("font_outline_color", INK)
		l.add_theme_constant_override("outline_size", 10)
	return l


static func button(text: String, on_press: Callable, size := 34, lit := true) -> Button:
	var b := Button.new()
	b.text = text
	b.auto_translate_mode = Node.AUTO_TRANSLATE_MODE_DISABLED
	b.add_theme_font_size_override("font_size", size)
	for c in ["font_color", "font_hover_color", "font_pressed_color", "font_focus_color"]:
		b.add_theme_color_override(c, INK)
	var normal := "button" if lit else "button_off"
	b.add_theme_stylebox_override("normal", skin(normal, 26))
	b.add_theme_stylebox_override("hover", skin("button_hover", 26))
	b.add_theme_stylebox_override("pressed", skin("button_hover", 26))
	b.add_theme_stylebox_override("focus", StyleBoxEmpty.new())
	b.pressed.connect(on_press)
	return b


## A caption followed by buttons; the button whose value equals `current` is lit.
## `options` is an Array of [text, value] pairs, `on_pick` receives the chosen value.
static func option_row(caption: String, options: Array, current: Variant, on_pick: Callable, size := 28) -> HBoxContainer:
	var row := HBoxContainer.new()
	row.alignment = BoxContainer.ALIGNMENT_CENTER
	row.add_theme_constant_override("separation", 10)
	var l := label(caption, size)
	l.custom_minimum_size.x = 250
	l.horizontal_alignment = HORIZONTAL_ALIGNMENT_RIGHT
	row.add_child(l)
	for opt in options:
		row.add_child(button(opt[0], on_pick.bind(opt[1]), size, opt[1] == current))
	return row


static func quit_game() -> void:
	Globals.save_now()
	(Engine.get_main_loop() as SceneTree).quit()


## Two buttons, "Čeština" and "English"; the current language is the lit one.
static func language_switch(size := 28) -> HBoxContainer:
	var row := HBoxContainer.new()
	row.add_theme_constant_override("separation", 10)
	for loc in LOCALES:
		row.add_child(button(LOCALES[loc], Lang.set_locale.bind(loc), size, Lang.current() == loc))
	return row
