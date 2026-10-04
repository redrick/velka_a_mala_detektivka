@tool
extends "res://game/characters/animated_character.gd"
## Made by tools/popochiu_gen.py: the room script decides what clicking this character does.

const Data := preload('character_verka_state.gd')

var state: Data = load("res://game/characters/verka/character_verka.tres")


func _on_click() -> void:
	if R.current.has_method("on_character") and await R.current.on_character(self, "click"):
		return
	await C.player.face_clicked()


func _on_right_click() -> void:
	if R.current.has_method("on_character") and await R.current.on_character(self, "look"):
		return
	await C.player.say(description)


func _on_item_used(item: PopochiuInventoryItem) -> void:
	if R.current.has_method("on_character") and await R.current.on_character(self, "item", item):
		return
	E.command_fallback()
