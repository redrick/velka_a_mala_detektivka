extends "dialog_overhead.gd"
## Spoken lines as subtitles: "Name: line" in a band along the bottom of the screen, over the
## picture. The band comes with the line and goes when it is dismissed (the component fades via
## modulate). Replaces the overhead placement, which could end up off screen.

const Band := preload("res://game/gui/components/subtitle_band.gd")

var _speaker: PopochiuCharacter


func _ready() -> void:
	super()
	set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	Band.apply(rich_text_label)
	# Keep the continue icon inside the band, at its right end.
	continue_icon.offset_left = -Band.SIDE_MARGIN + 30.0
	continue_icon.offset_right = continue_icon.offset_left + continue_icon_size.x


func _show_dialogue(chr: PopochiuCharacter, msg := "") -> void:
	_speaker = chr
	super(chr, msg)


func _modify_size(_msg: String, _target_position: Vector2) -> void:
	Band.apply(rich_text_label)
	await get_tree().process_frame


func _set_default_size() -> void:
	Band.apply(rich_text_label)


func _append_text(msg: String, _props: Dictionary) -> void:
	var who := ""
	if is_instance_valid(_speaker):
		who = "[color=%s]%s:[/color] " % [_speaker.text_color.to_html(), tr(_speaker.description)]
	rich_text_label.text = "[center]%s%s[/center]" % [who, msg]
