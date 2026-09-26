@tool
extends "res://addons/popochiu/engine/interfaces/i_inventory.gd"

# classes ----
const PIILupa := preload("res://game/inventory_items/lupa/inventory_item_lupa.gd")
const PIIZapisnik := preload("res://game/inventory_items/zapisnik/inventory_item_zapisnik.gd")
const PIIStaraPonozka := preload("res://game/inventory_items/stara_ponozka/inventory_item_stara_ponozka.gd")
const PIIMouka := preload("res://game/inventory_items/mouka/inventory_item_mouka.gd")
const PIINovaPonozka := preload("res://game/inventory_items/nova_ponozka/inventory_item_nova_ponozka.gd")
const PIINitka := preload("res://game/inventory_items/nitka/inventory_item_nitka.gd")
const PIIKlic := preload("res://game/inventory_items/klic/inventory_item_klic.gd")
# ---- classes

# nodes ----
var Lupa: PIILupa : get = get_Lupa
var Zapisnik: PIIZapisnik : get = get_Zapisnik
var StaraPonozka: PIIStaraPonozka : get = get_StaraPonozka
var Mouka: PIIMouka : get = get_Mouka
var NovaPonozka: PIINovaPonozka : get = get_NovaPonozka
var Nitka: PIINitka : get = get_Nitka
var Klic: PIIKlic : get = get_Klic
# ---- nodes

# functions ----
func get_Lupa() -> PIILupa: return get_item_instance("Lupa")
func get_Zapisnik() -> PIIZapisnik: return get_item_instance("Zapisnik")
func get_StaraPonozka() -> PIIStaraPonozka: return get_item_instance("StaraPonozka")
func get_Mouka() -> PIIMouka: return get_item_instance("Mouka")
func get_NovaPonozka() -> PIINovaPonozka: return get_item_instance("NovaPonozka")
func get_Nitka() -> PIINitka: return get_item_instance("Nitka")
func get_Klic() -> PIIKlic: return get_item_instance("Klic")
# ---- functions

