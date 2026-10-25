@tool
extends PopochiuProp
## A prop whose clicks are handled by its room script: on_click(node), on_look(node), on_item(node, item).
## Rooms made by tools/popochiu_gen.py use it, so a story's logic lives in one file per room.


func _ready() -> void:
	super()
	# in a scene written inline the Sprite2D doesn't exist yet when `texture` is set
	if has_node("Sprite2D"):
		$Sprite2D.texture = texture


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
