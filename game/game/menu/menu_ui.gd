extends CanvasLayer
## Main menu: pick a series, then a story. Series and stories come from series.json; a story with
## a "start_room" is playable, the rest show as "Brzy" (coming soon). Every screen has Nastavení and
## Ukončit hru bottom-left and the language switch bottom-right.

const Kit := preload("res://game/menu/ui_kit.gd")
const SettingsPage := preload("res://game/menu/settings_page.gd")
const CATALOG := "res://game/menu/series.json"
const CARD_SIZE := Vector2(170, 204)

var _catalog: Array = []
var _screen: Control
## The screen shown now (rebuilt on a language or settings change), and where "← Zpět" on the
## settings and quit screens returns to.
var _current: Callable
var _back: Callable


func _ready() -> void:
	var parsed = JSON.parse_string(FileAccess.get_file_as_string(CATALOG))
	_catalog = parsed.series if parsed is Dictionary else []
	Lang.changed.connect(_rebuild)
	Prefs.changed.connect(_rebuild)
	show_series()


func _rebuild() -> void:
	_current.call()


func show_series() -> void:
	_back = show_series
	_current = show_series
	var screen := _new_screen()
	var col := VBoxContainer.new()
	col.position = Vector2(640, 70)
	col.size = Vector2(1220, 940)
	col.alignment = BoxContainer.ALIGNMENT_CENTER
	col.add_theme_constant_override("separation", 40)
	screen.add_child(col)
	col.add_child(Kit.title(tr("Vyber si příběh"), 76))
	var row := HBoxContainer.new()
	row.alignment = BoxContainer.ALIGNMENT_CENTER
	row.add_theme_constant_override("separation", 60)
	col.add_child(row)
	for series in _catalog:
		row.add_child(_series_card(series))
	row.add_child(_coming_series_card())
	_add_footer(screen)


func show_episodes(series: Dictionary) -> void:
	_back = show_episodes.bind(series)
	_current = _back
	var screen := _new_screen()
	var sheet := Kit.panel()
	sheet.position = Vector2(60, 20)
	sheet.size = Vector2(1800, 920)
	screen.add_child(sheet)
	var col := VBoxContainer.new()
	col.add_theme_constant_override("separation", 12)
	sheet.add_child(col)

	var top := HBoxContainer.new()
	top.add_theme_constant_override("separation", 30)
	col.add_child(top)
	top.add_child(Kit.button(tr("← Zpět"), show_series))
	var heading := Kit.title(tr(series.title), 54)
	heading.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	top.add_child(heading)

	var sub := Kit.label(tr(series.get("subtitle", "")), 30)
	col.add_child(sub)

	var grid := GridContainer.new()
	grid.columns = 8
	grid.add_theme_constant_override("h_separation", 22)
	grid.add_theme_constant_override("v_separation", 10)
	grid.size_flags_horizontal = Control.SIZE_SHRINK_CENTER
	col.add_child(grid)
	for ep in series.episodes:
		grid.add_child(_episode_card(ep))
	_add_footer(screen)


func show_settings() -> void:
	_current = show_settings
	var col := _dialog(1200.0, 200.0)
	col.add_child(_header(tr("Nastavení")))
	col.add_child(SettingsPage.new())


func show_quit() -> void:
	_current = show_quit
	var col := _dialog(720.0, 300.0)
	col.add_child(Kit.title(tr("Ukončit hru"), 60))
	col.add_child(Kit.label(tr("Opravdu ukončit hru?"), 34))
	var row := HBoxContainer.new()
	row.alignment = BoxContainer.ALIGNMENT_CENTER
	row.add_theme_constant_override("separation", 40)
	row.add_child(_wide(Kit.button(tr("Ano"), Kit.quit_game), 200))
	row.add_child(_wide(Kit.button(tr("Ne"), _back), 200))
	col.add_child(row)


## A paper sheet of the given width, centred horizontally; returns its column.
func _dialog(width: float, top: float) -> VBoxContainer:
	var screen := _new_screen()
	var sheet := Kit.panel()
	sheet.custom_minimum_size.x = width
	sheet.position = Vector2((1920 - width) / 2.0, top)
	screen.add_child(sheet)
	var col := VBoxContainer.new()
	col.alignment = BoxContainer.ALIGNMENT_CENTER
	col.add_theme_constant_override("separation", 26)
	sheet.add_child(col)
	return col


## "← Zpět" on the left, the title centred.
func _header(text: String) -> HBoxContainer:
	var top := HBoxContainer.new()
	top.add_theme_constant_override("separation", 30)
	top.add_child(Kit.button(tr("← Zpět"), _back))
	var heading := Kit.title(text, 60)
	heading.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	top.add_child(heading)
	top.add_child(Control.new())
	return top


func _add_footer(screen: Control) -> void:
	var left := HBoxContainer.new()
	left.add_theme_constant_override("separation", 16)
	left.add_child(Kit.button(tr("Nastavení"), show_settings, 28))
	left.add_child(Kit.button(tr("Ukončit hru"), show_quit, 28))
	_pin(screen, left, Control.PRESET_BOTTOM_LEFT)
	_pin(screen, Kit.language_switch(), Control.PRESET_BOTTOM_RIGHT)


## Puts `c` in a corner of the screen, growing away from the edges.
func _pin(screen: Control, c: Control, corner: Control.LayoutPreset) -> void:
	const MARGIN := 24.0
	screen.add_child(c)
	c.set_anchors_preset(corner)
	var right := corner == Control.PRESET_BOTTOM_RIGHT
	c.grow_horizontal = Control.GROW_DIRECTION_BEGIN if right else Control.GROW_DIRECTION_END
	c.grow_vertical = Control.GROW_DIRECTION_BEGIN
	c.offset_left = -MARGIN if right else MARGIN
	c.offset_right = c.offset_left
	c.offset_top = -MARGIN
	c.offset_bottom = -MARGIN


func _wide(c: Control, width: float) -> Control:
	c.custom_minimum_size.x = width
	c.size_flags_horizontal = Control.SIZE_SHRINK_CENTER
	return c


func _series_card(series: Dictionary) -> Control:
	var card := VBoxContainer.new()
	card.add_theme_constant_override("separation", 10)
	var cover := _cover_button(load(series.cover), Vector2(300, 400))
	cover.pressed.connect(show_episodes.bind(series))
	card.add_child(cover)
	var count: int = series.episodes.filter(func(e): return e.has("start_room")).size()
	card.add_child(Kit.label(tr("%d z %d příběhů") % [count, series.episodes.size()], 30, Color.WHITE, true))
	return card


func _coming_series_card() -> Control:
	var card := VBoxContainer.new()
	card.add_theme_constant_override("separation", 10)
	var cover := _cover_button(load(Kit.ART + "ep_locked.png"), Vector2(300, 400))
	cover.disabled = true
	cover.modulate = Color(1, 1, 1, 0.85)
	card.add_child(cover)
	card.add_child(Kit.label(tr("Další série brzy"), 30, Color.WHITE, true))
	return card


func _episode_card(ep: Dictionary) -> Control:
	var playable := ep.has("start_room")
	var card := VBoxContainer.new()
	card.add_theme_constant_override("separation", 6)
	var tex: Texture2D = load(ep.cover) if ep.has("cover") else load(Kit.ART + "ep_locked.png")
	var cover := _cover_button(tex, CARD_SIZE)
	card.add_child(cover)
	if playable:
		cover.pressed.connect(_start.bind(ep))
	else:
		cover.disabled = true
		cover.modulate = Color(1, 1, 1, 0.75)
		var num := Kit.title(str(int(ep.number)), 44)
		num.position = Vector2(12, 4)
		cover.add_child(num)
	# Stories not out yet keep their title secret: just the number and "???".
	var title: String = tr(ep.title) if playable else "???"
	var caption := Kit.label("%d. %s" % [ep.number, title], 22)
	caption.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART
	caption.custom_minimum_size = Vector2(CARD_SIZE.x, 58)
	card.add_child(caption)
	if playable:
		card.add_child(Kit.title(tr("▶ Hrát"), 30))
	else:
		card.add_child(Kit.label(tr("Brzy"), 20, Color("8a7f6a")))
	return card


func _cover_button(tex: Texture2D, size: Vector2) -> TextureButton:
	var b := TextureButton.new()
	b.texture_normal = tex
	b.ignore_texture_size = true
	b.stretch_mode = TextureButton.STRETCH_KEEP_ASPECT_CENTERED
	b.custom_minimum_size = size
	b.pivot_offset = size / 2.0
	b.mouse_entered.connect(func(): if not b.disabled: _zoom(b, 1.06))
	b.mouse_exited.connect(func(): _zoom(b, 1.0))
	return b


func _zoom(c: Control, to: float) -> void:
	create_tween().tween_property(c, "scale", Vector2(to, to), 0.12)


func _start(ep: Dictionary) -> void:
	_screen.mouse_filter = Control.MOUSE_FILTER_STOP
	Globals.start_episode(ep.start_room)


func _new_screen() -> Control:
	if is_instance_valid(_screen):
		_screen.queue_free()
	_screen = Control.new()
	_screen.set_anchors_preset(Control.PRESET_FULL_RECT)
	_screen.mouse_filter = Control.MOUSE_FILTER_IGNORE
	_screen.theme = Kit.theme()
	add_child(_screen)
	return _screen
