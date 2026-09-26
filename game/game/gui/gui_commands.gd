# @popochiu-docs-ignore-class
extends SimpleClickCommands
## Fallbacks for clicks the game has no reaction for: instead of Popochiu's English system text,
## whoever is playing says a short line (translated by the character base).


# Called when `E.command_fallback()` is triggered.
# By default this checks whether the clicked object is a `PopochiuClickable` or
# a `PopochiuInventoryItem` and invokes the corresponding method based on the
# object type and mouse button.
func fallback() -> void:
	super()


# Called when the player left-clicks a `PopochiuClickable`.
func click_clickable() -> void:
	if I.active:
		await _cannot_combine()
	else:
		await C.player.say("S tím nic neudělám.")


# Called when the player right-clicks a `PopochiuClickable`.
func right_click_clickable() -> void:
	await C.player.say("Nic zvláštního tu nevidím.")


# Called when the player left-clicks a `PopochiuInventoryItem`.
func click_inventory_item() -> void:
	if I.active and I.active != I.clicked:
		await _cannot_combine()
	else:
		I.clicked.set_active()


# Called when the player right-clicks a `PopochiuInventoryItem`.
func right_click_inventory_item() -> void:
	await C.player.say("Nic zvláštního na tom nevidím.")


func _cannot_combine() -> void:
	match randi() % 3:
		0: await C.player.say("Hm, to nepůjde.")
		1: await C.player.say("To k sobě nepasuje.")
		_: await C.player.say("Ne, takhle to nefunguje.")
