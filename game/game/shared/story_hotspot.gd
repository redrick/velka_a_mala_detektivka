@tool
extends PopochiuHotspot
## A hotspot whose clicks are handled by its room script (see story_prop.gd).


func _on_click() -> void:
	await R.current.on_click(self)


func _on_right_click() -> void:
	await R.current.on_look(self)


func _on_item_used(item: PopochiuInventoryItem) -> void:
	await R.current.on_item(self, item)


## Ignored while a scene runs (Globals.click_busy).
func handle_command(button_idx: int) -> void:
	var room: Node = Globals.click_begin()
	if room:
		await super(button_idx)
		Globals.click_end(room)


func on_item_used(item: PopochiuInventoryItem) -> void:
	var room: Node = Globals.click_begin()
	if room:
		await super(item)
		Globals.click_end(room)
