# @popochiu-docs-ignore-class
@tool
extends PopochiuRoom

const Data := preload('room_menu_state.gd')
const MenuUI := preload("res://game/menu/menu_ui.gd")

var state: Data = load("res://game/rooms/menu/room_menu.tres")


#region Virtual ####################################################################################
func _on_room_entered() -> void:
	G.hide_interface()
	for chr in get_characters():
		remove_character(chr)
	add_child(MenuUI.new())


func _on_room_transition_finished() -> void:
	pass


func _on_room_exited() -> void:
	pass


#endregion
