# @popochiu-docs-ignore-class
@tool
extends PopochiuHotspot
# You can use `E.queue([])` in any of the methods in this script to trigger a sequence of events.
# Use `await E.queue([])` to pause execution until the sequence completes.


#region Virtual ####################################################################################
# When the hotspot is clicked
func _on_click() -> void:
	await C.player.walk_to_clicked()
	await C.player.face_clicked()
	if Globals.night_done:
		await C.player.say("Návnada zmizela. Zloděj přišel!")
	elif Globals.got_flour and not Globals.trap_set:
		await _set_trap()
	elif Globals.trap_planned and not Globals.got_flour:
		await C.player.say("Na past potřebujeme mouku od babičky.")
	else:
		await C.player.say("Na šňůře visí jen jedna ponožka.")


# Called when the hotspot is double-clicked
func _on_double_click() -> void:
	# Replace the call to E.command_fallback() with your own logic.
	PopochiuUtils.e.command_fallback()
	# Example: on an exit hotspot you could instantly change rooms instead of waiting for the player
	# to walk there.
#	await R.current = R.NewRoom


# When the hotspot is right clicked
func _on_right_click() -> void:
	await C.player.face_clicked()
	await C.player.say("Babiččina šňůra na prádlo.")


# Called when the hotspot is middle clicked
func _on_middle_click() -> void:
	# Replace the call to E.command_fallback() with your own logic.
	PopochiuUtils.e.command_fallback()


# Called when the hotspot is clicked and there is an inventory item selected
func _on_item_used(_item: PopochiuInventoryItem) -> void:
	# Hanging the sock or pouring the flour here is the natural way to set the trap.
	if (_item == I.NovaPonozka or _item == I.Mouka) and Globals.got_flour and not Globals.trap_set:
		I.deselect_active()
		await C.player.walk_to_clicked()
		await C.player.face_clicked()
		await _set_trap()
	else:
		PopochiuUtils.e.command_fallback()


# Called when the hotspot starts moving
func _on_movement_started() -> void:
	pass


# Called when the hotspot stops moving
func _on_movement_ended() -> void:
	pass


#endregion

#region Public #####################################################################################
# Add functions here that are triggered by GUI commands.
#
# If you name the functions following the `on_<command_id>` pattern, they will be automatically
# called when the corresponding command is triggered in the GUI.
#
# For example, if your GUI provides a `look_at` command you could add:
#
#func on_look_at() -> void:
#	pass
#
# This function will be called whenever the `look_at` command is triggered in the GUI while this
# hotspot is the target.
# This keeps the code way more tidy and organized with GUIs with many different commands,
# as opposed to having a single `match` statement in the general-use methods.


#endregion


func _set_trap() -> void:
	await C.Alica.say("Pověsíme na šňůru novou ponožku…")
	R.current.get_prop("Navnada").show()
	C.Hanka.pose("grin")
	await C.Hanka.say("…a já pod ni nasypu mouku!")
	C.Hanka.pose()
	var trap: CanvasLayer = preload("res://game/minigames/trap.gd").new()
	R.current.add_child(trap)
	await trap.finished
	R.current.get_prop("Past").show()
	I.NovaPonozka.remove()
	I.Mouka.remove()
	C.Hanka.pose()
	await C.Alica.say("Past je hotová. Teď počkáme do večera.")
	Globals.trap_set = true
	Globals.phase = "evening"
	R.goto_room("Kuchyne")
