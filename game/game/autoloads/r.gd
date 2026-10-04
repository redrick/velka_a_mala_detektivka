@tool
extends "res://addons/popochiu/engine/interfaces/i_room.gd"

# classes ----
const PRZahrada := preload("res://game/rooms/zahrada/room_zahrada.gd")
const PRKuchyne := preload("res://game/rooms/kuchyne/room_kuchyne.gd")
const PRZahumenek := preload("res://game/rooms/zahumenek/room_zahumenek.gd")
const PRKulna := preload("res://game/rooms/kulna/room_kulna.gd")
const PRMenu := preload("res://game/rooms/menu/room_menu.gd")
const PRLoznice := preload("res://game/rooms/loznice/room_loznice.gd")
const PRSnidane := preload("res://game/rooms/snidane/room_snidane.gd")
const PRStit := preload("res://game/rooms/stit/room_stit.gd")
const PRPuda := preload("res://game/rooms/puda/room_puda.gd")
const PRKuchyne3 := preload("res://game/rooms/kuchyne3/room_kuchyne3.gd")
const PRRybnik := preload("res://game/rooms/rybnik/room_rybnik.gd")
const PRMlyn := preload("res://game/rooms/mlyn/room_mlyn.gd")
# ---- classes

# nodes ----
var Zahrada: PRZahrada : get = get_Zahrada
var Kuchyne: PRKuchyne : get = get_Kuchyne
var Zahumenek: PRZahumenek : get = get_Zahumenek
var Kulna: PRKulna : get = get_Kulna
var Menu: PRMenu : get = get_Menu
var Loznice: PRLoznice : get = get_Loznice
var Snidane: PRSnidane : get = get_Snidane
var Stit: PRStit : get = get_Stit
var Puda: PRPuda : get = get_Puda
var Kuchyne3: PRKuchyne3 : get = get_Kuchyne3
var Rybnik: PRRybnik : get = get_Rybnik
var Mlyn: PRMlyn : get = get_Mlyn
# ---- nodes

# functions ----
func get_Zahrada() -> PRZahrada: return get_runtime_room("Zahrada")
func get_Kuchyne() -> PRKuchyne: return get_runtime_room("Kuchyne")
func get_Zahumenek() -> PRZahumenek: return get_runtime_room("Zahumenek")
func get_Kulna() -> PRKulna: return get_runtime_room("Kulna")
func get_Menu() -> PRMenu: return get_runtime_room("Menu")
func get_Loznice() -> PRLoznice: return get_runtime_room("Loznice")
func get_Snidane() -> PRSnidane: return get_runtime_room("Snidane")
func get_Stit() -> PRStit: return get_runtime_room("Stit")
func get_Puda() -> PRPuda: return get_runtime_room("Puda")
func get_Kuchyne3() -> PRKuchyne3: return get_runtime_room("Kuchyne3")
func get_Rybnik() -> PRRybnik: return get_runtime_room("Rybnik")
func get_Mlyn() -> PRMlyn: return get_runtime_room("Mlyn")
# ---- functions

