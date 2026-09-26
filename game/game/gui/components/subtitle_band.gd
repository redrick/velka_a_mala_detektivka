extends RefCounted
## The look shared by spoken lines and hover names: a translucent paper band across the bottom of
## the screen, over the picture. The label grows upwards with its text (fit_content) and is hidden
## by its component when there is nothing to say.

const SIDE_MARGIN := 140.0


static func apply(label: RichTextLabel, pad := 16.0, alpha := 0.82) -> void:
	var sb := StyleBoxFlat.new()
	sb.bg_color = Color(0.96, 0.94, 0.89, alpha)
	sb.border_color = Color(0.17, 0.13, 0.09, 0.5)
	sb.border_width_top = 3
	sb.content_margin_left = SIDE_MARGIN
	sb.content_margin_right = SIDE_MARGIN
	sb.content_margin_top = pad
	sb.content_margin_bottom = pad
	label.add_theme_stylebox_override("normal", sb)
	label.fit_content = true
	label.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART
	label.set_anchors_preset(Control.PRESET_BOTTOM_WIDE)
	label.grow_horizontal = Control.GROW_DIRECTION_BOTH
	label.grow_vertical = Control.GROW_DIRECTION_BEGIN
	label.offset_left = 0.0
	label.offset_right = 0.0
	label.offset_top = 0.0
	label.offset_bottom = 0.0
