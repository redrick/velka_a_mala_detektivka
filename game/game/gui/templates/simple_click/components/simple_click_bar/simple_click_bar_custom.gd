extends "simple_click_bar.gd"

const Kit := preload("res://game/menu/ui_kit.gd")


func _ready() -> void:
	super()
	var strip: PanelContainer = %PanelContainer
	strip.self_modulate = Color.WHITE
	strip.add_theme_stylebox_override("panel", Kit.skin("panel", 30))
	var house: Texture2D = load(Kit.ART + "home.png")
	settings_btn.texture_normal = house
	settings_btn.texture_hover = house
	settings_btn.texture_pressed = house
	settings_btn.ignore_texture_size = true
	settings_btn.stretch_mode = TextureButton.STRETCH_KEEP_ASPECT_CENTERED
	settings_btn.custom_minimum_size = Vector2(90, 0)


# The bar belongs to a story: hidden (and deaf to the mouse) in the main menu.
func _process(_delta: float) -> void:
	visible = InGameMenu.in_story()
	set_process_input(visible and not always_visible)


func _on_settings_pressed() -> void:
	InGameMenu.open()
