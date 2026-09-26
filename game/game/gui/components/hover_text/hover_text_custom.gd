extends "hover_text.gd"
## The name of whatever is under the mouse, in a band along the bottom of the screen that shows
## only while there is a name to show.

const Band := preload("res://game/gui/components/subtitle_band.gd")

## Popochiu builds "Use <item> with <target>" in English while an item is active.
var _use := RegEx.create_from_string("^Use (.+) with (.+)$")


func _ready() -> void:
	super()
	# The component itself is a thin strip anchored to the bottom; let the band fill the width.
	set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	Band.apply(label, 10.0, 0.7)
	label.add_theme_color_override("default_color", Color("2b2118"))
	label.add_theme_color_override("font_outline_color", Color.WHITE)
	label.hide()


func _show_text(txt := "") -> void:
	label.visible = not txt.is_empty()
	var m := _use.search(txt)
	if m:
		super(tr("Použít %s na: %s") % [tr(m.get_string(1)), tr(m.get_string(2))])
	else:
		super(tr(txt))
