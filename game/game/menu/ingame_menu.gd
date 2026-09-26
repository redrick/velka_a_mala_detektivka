extends CanvasLayer
## In-game menu, styled like the main menu. Opened by the house button in the corner (or the top
## bar's house icon): continue, settings, the history of spoken lines, main menu, quit.

const Kit := preload("res://game/menu/ui_kit.gd")
const SettingsPage := preload("res://game/menu/settings_page.gd")
const HISTORY_SIZE := 150

## Spoken lines of the current story: {name, text, color}; name and text are Czech keys, translated
## when shown so a language switch also switches older lines.
var history: Array[Dictionary] = []

var _house := TextureButton.new()
var _overlay: Control
var _page := "main"


func _ready() -> void:
	layer = 40
	process_mode = Node.PROCESS_MODE_ALWAYS
	_house.texture_normal = load(Kit.ART + "home.png")
	_house.ignore_texture_size = true
	_house.stretch_mode = TextureButton.STRETCH_KEEP_ASPECT
	_house.custom_minimum_size = Vector2(84, 84)
	_house.position = Vector2(18, 978)
	_house.pressed.connect(open)
	add_child(_house)
	Lang.changed.connect(func(): if is_open(): _build())
	Prefs.changed.connect(func(): if is_open(): _build())


func _process(_delta: float) -> void:
	# Hidden while a subtitle is up: the band runs along the bottom where the house sits.
	_house.visible = in_story() and not is_open() and not G.gui.is_showing_dialog_line
	_house.position.y = get_viewport().get_visible_rect().size.y - 102.0


func in_story() -> bool:
	return R.current != null and R.current.script_name != "Menu" and E.in_room


func is_open() -> bool:
	return is_instance_valid(_overlay)


func remember(chr: PopochiuCharacter, text: String) -> void:
	history.append({name = chr.description, text = text, color = chr.text_color})
	if history.size() > HISTORY_SIZE:
		history.pop_front()


func open() -> void:
	if is_open() or not in_story():
		return
	_show("main")


func close() -> void:
	if is_open():
		_overlay.queue_free()


func _show(page: String) -> void:
	_page = page
	_build()


func _build() -> void:
	if is_open():
		_overlay.queue_free()
	_overlay = ColorRect.new()
	_overlay.color = Color(0.1, 0.08, 0.05, 0.45)
	_overlay.set_anchors_preset(Control.PRESET_FULL_RECT)
	_overlay.mouse_filter = Control.MOUSE_FILTER_STOP
	_overlay.theme = Kit.theme(34)
	add_child(_overlay)

	var sheet := Kit.panel()
	_overlay.add_child(sheet)
	var col := VBoxContainer.new()
	col.alignment = BoxContainer.ALIGNMENT_CENTER
	col.add_theme_constant_override("separation", 26)
	sheet.add_child(col)
	var width := 900.0
	var top := 170.0
	match _page:
		"confirm":
			width = 820.0
			top = 240.0
			_confirm_page(col, tr("Hlavní menu"), tr("Opravdu skončit a jít do hlavního menu?"), _leave)
		"quit":
			width = 720.0
			top = 240.0
			_confirm_page(col, tr("Ukončit hru"), tr("Opravdu ukončit hru?"), Kit.quit_game)
		"settings":
			width = 1200.0
			top = 200.0
			_settings_page(col)
		"history":
			width = 1300.0
			top = 60.0
			_history_page(col)
		_:
			_main_page(col)
	sheet.custom_minimum_size.x = width
	sheet.position = Vector2((1920 - width) / 2.0, top)


func _main_page(col: VBoxContainer) -> void:
	col.add_child(Kit.title(tr("Menu"), 70))
	col.add_child(_wide(Kit.button(tr("Pokračovat"), close, 40), 420))
	col.add_child(_wide(Kit.button(tr("Nastavení"), _show.bind("settings"), 40), 420))
	col.add_child(_wide(Kit.button(tr("Historie"), _show.bind("history"), 40), 420))
	col.add_child(_wide(Kit.button(tr("Hlavní menu"), _show.bind("confirm"), 40), 420))
	col.add_child(_wide(Kit.button(tr("Ukončit hru"), _show.bind("quit"), 40), 420))


func _settings_page(col: VBoxContainer) -> void:
	col.add_child(_page_header(tr("Nastavení")))
	col.add_child(SettingsPage.new())


func _confirm_page(col: VBoxContainer, heading: String, question: String, on_yes: Callable) -> void:
	col.add_child(Kit.title(heading, 60))
	col.add_child(Kit.label(question, 34))
	var row := HBoxContainer.new()
	row.alignment = BoxContainer.ALIGNMENT_CENTER
	row.add_theme_constant_override("separation", 40)
	row.add_child(_wide(Kit.button(tr("Ano"), on_yes), 200))
	row.add_child(_wide(Kit.button(tr("Ne"), _show.bind("main")), 200))
	col.add_child(row)


## "← Zpět" on the left, the page title centred.
func _page_header(heading_text: String) -> HBoxContainer:
	var top := HBoxContainer.new()
	top.add_theme_constant_override("separation", 30)
	top.add_child(Kit.button(tr("← Zpět"), _show.bind("main")))
	var heading := Kit.title(heading_text, 60)
	heading.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	top.add_child(heading)
	top.add_child(Control.new())
	return top


func _history_page(col: VBoxContainer) -> void:
	col.add_child(_page_header(tr("Historie")))

	var scroll := ScrollContainer.new()
	scroll.custom_minimum_size = Vector2(1200, 760)
	scroll.horizontal_scroll_mode = ScrollContainer.SCROLL_MODE_DISABLED
	col.add_child(scroll)
	var lines := VBoxContainer.new()
	lines.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	lines.add_theme_constant_override("separation", 14)
	scroll.add_child(lines)
	if history.is_empty():
		lines.add_child(Kit.label(tr("Zatím tu nic není."), 32))
	for entry in history:
		var row := HBoxContainer.new()
		row.add_theme_constant_override("separation", 16)
		var who := Kit.label(tr(entry.name) + ":", 30, entry.color, true)
		who.custom_minimum_size.x = 190
		who.horizontal_alignment = HORIZONTAL_ALIGNMENT_RIGHT
		who.vertical_alignment = VERTICAL_ALIGNMENT_TOP
		who.add_theme_color_override("font_outline_color", Color.WHITE)
		row.add_child(who)
		var what := Kit.label(tr(entry.text), 30)
		what.horizontal_alignment = HORIZONTAL_ALIGNMENT_LEFT
		what.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART
		what.size_flags_horizontal = Control.SIZE_EXPAND_FILL
		row.add_child(what)
		lines.add_child(row)
	_scroll_to_end.call_deferred(scroll)


func _scroll_to_end(scroll: ScrollContainer) -> void:
	await get_tree().process_frame
	if is_instance_valid(scroll):
		scroll.scroll_vertical = int(scroll.get_v_scroll_bar().max_value)


func _leave() -> void:
	close()
	Globals.go_to_menu()


func _wide(c: Control, width: float) -> Control:
	c.custom_minimum_size.x = width
	c.size_flags_horizontal = Control.SIZE_SHRINK_CENTER
	return c
