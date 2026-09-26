@tool
extends "res://addons/popochiu/engine/interfaces/i_room.gd"

# classes ----
const PRZahrada := preload("res://game/rooms/zahrada/room_zahrada.gd")
const PRKuchyne := preload("res://game/rooms/kuchyne/room_kuchyne.gd")
const PRZahumenek := preload("res://game/rooms/zahumenek/room_zahumenek.gd")
const PRKulna := preload("res://game/rooms/kulna/room_kulna.gd")
const PRMenu := preload("res://game/rooms/menu/room_menu.gd")
# ---- classes

# nodes ----
var Zahrada: PRZahrada : get = get_Zahrada
var Kuchyne: PRKuchyne : get = get_Kuchyne
var Zahumenek: PRZahumenek : get = get_Zahumenek
var Kulna: PRKulna : get = get_Kulna
var Menu: PRMenu : get = get_Menu
# ---- nodes

# functions ----
func get_Zahrada() -> PRZahrada: return get_runtime_room("Zahrada")
func get_Kuchyne() -> PRKuchyne: return get_runtime_room("Kuchyne")
func get_Zahumenek() -> PRZahumenek: return get_runtime_room("Zahumenek")
func get_Kulna() -> PRKulna: return get_runtime_room("Kulna")
func get_Menu() -> PRMenu: return get_runtime_room("Menu")
# ---- functions

