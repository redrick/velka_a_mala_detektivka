# @popochiu-docs-ignore-class
@tool
extends "res://game/characters/animated_character.gd"
# You can use `E.queue([])` in any of the methods in this script to trigger a sequence of events.
# Use `await E.queue([])` to pause execution until the sequence completes.

const Data := preload('character_babicka_state.gd')

var state: Data = load("res://game/characters/babicka/character_babicka.tres")


#region Virtual ####################################################################################
# Called when the room where this character is located has finished being added to the scene tree.
func _on_room_set() -> void:
	pass


# Called when the character is clicked
func _on_click() -> void:
	await C.player.walk_to_clicked(Vector2(-200, 0))
	await C.player.face_clicked()
	if R.current.script_name == "Kuchyne":
		await _talk_in_kitchen()
		return
	if Globals.game_finished:
		await say("Díky, detektivky! Ponožky už nikomu nezmizí.")
		return
	if Globals.shed_done:
		await say("Pomozte dědovi s domečkem.")
		return
	if not Globals.case_started:
		await say("To je divné… Včera zmizela jedna ponožka, dneska druhá!")
		await C.Alica.say("To je případ pro detektivky Alicu a Hanku!")
		Globals.case_started = true
		await I.Zapisnik.add()
	elif not Globals.footprints_found:
		await say("Podívejte se pořádně pod šňůru, děvčata.")
	elif not Globals.joey_cleared:
		await say("Stopy? A nebyl to náhodou Joey?")
	else:
		await say("Tonda za plotem prý něco viděl.")


# Called when the character is double-clicked
func _on_double_click() -> void:
	# Replace the call to E.command_fallback() with your code.
	E.command_fallback()
	# Example: teleport the player to the character.
#	C.player.teleport_to_character(self)


# Called when the character is right-clicked
func _on_right_click() -> void:
	await C.player.face_clicked()
	await C.player.say("To je naše babička. Věší prádlo.")


# Called when the character is middle clicked
func _on_middle_click() -> void:
	# Replace the call to E.command_fallback() to implement your code.
	E.command_fallback()
	# Example: make the player say something without facing the character.
#	await C.player.say("I don't want to talk to this guy")


# Called when the character is clicked while an inventory item is selected
func _on_item_used(_item: PopochiuInventoryItem) -> void:
	# Replace the call to E.command_fallback() with your own logic.
	E.command_fallback()
	# Example: if the player uses a Key on this character, make the player say something.
#	if _item == I.Key:
#		await C.player.say("I don't want to give my key away!")


# Override this to alter the idle animation or hook custom logic to it. 
# By default, it plays the "idle" animation from the character's Sprite.
func _play_idle() -> void:
	# If you want to preserve the default idle behavior, make sure to keep
	# the call to `super()` in your override.
	super()


# Override this to alter the walk animation or hook custom logic to it. 
# `target_pos` can be used to determine the movement direction.
# By default, it plays the "walk" animation from the character's Sprite.
func _play_walk(target_pos: Vector2) -> void:
	# If you want to preserve the default walking behavior, make sure to keep
	# the call to `super(target_pos)` in your override.
	super(target_pos)


# Override this to alter the talk animation or hook custom logic to it.
# By default, it plays the "talk" animation from the character's Sprite.
func _play_talk() -> void:
	# If you want to preserve the default talk behavior, make sure to keep
	# the call to `super()` in your override.
	super()


# Override this to alter the grab animation or hook custom logic to it.
# By default, it plays the "grab" animation from the character's Sprite.
func _play_grab() -> void:
	# If you want to preserve the default grab behavior, make sure to keep
	# the call to `super()` in your override.
	super()


# Called when the character starts moving.
# Implement any logic you want to trigger at the start of movement here.
# For example, you could play a sound effect or make something happen in the room.
func _on_movement_started() -> void:
	pass


# Called when the character stops moving
# Implement any logic you want to trigger at the start of movement here.
# For example, you could play a sound effect or make something happen in the room.
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
# character is the target.
# This keeps the code way more tidy and organized with GUIs with many different commands,
# as opposed to having a single `match` statement in the general-use methods.


#endregion


func _talk_in_kitchen() -> void:
	if Globals.night_done:
		await say("Tak co, chytily jste zloděje?")
		await C.Alica.say("Ještě ne. Ale máme stopu!")
	elif Globals.trap_set:
		await say("Kakao bude hned.")
	elif Globals.got_flour:
		await say("Hodně štěstí s pastí!")
	else:
		await C.Alica.say("Babičko, můžeme si půjčit mouku?")
		await say("Mouku? A na co vám bude?")
		await C.Alica.say("To je detektivní tajemství!")
		C.Hanka.pose("whisper")
		await C.Hanka.say("Pssst!")
		C.Hanka.pose()
		await say("Tak tady je. A vezměte si i novou ponožku, ať má zloděj co brát.")
		R.current.get_prop("Mouka").hide()
		await I.Mouka.add()
		await I.NovaPonozka.add()
		Globals.got_flour = true
		await C.Alica.say("Díky, babi! Teď past na šňůru.")
