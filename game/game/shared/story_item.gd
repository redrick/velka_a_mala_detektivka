extends PopochiuInventoryItem
## Inventory item for the later stories: right click describes it, the room decides the rest.


func _on_click() -> void:
	E.command_fallback()


func _on_right_click() -> void:
	await C.player.say(description)


func _on_item_used(_item: PopochiuInventoryItem) -> void:
	E.command_fallback()
