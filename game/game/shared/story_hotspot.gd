@tool
extends PopochiuHotspot
## A hotspot whose clicks are handled by its room script (see story_prop.gd).


func _on_click() -> void:
	await R.current.on_click(self)


func _on_right_click() -> void:
	await R.current.on_look(self)


func _on_item_used(item: PopochiuInventoryItem) -> void:
	await R.current.on_item(self, item)
