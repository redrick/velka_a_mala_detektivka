@tool
extends "res://addons/popochiu/engine/interfaces/i_character.gd"

# classes ----
const PCAlica := preload("res://game/characters/alica/character_alica.gd")
const PCHanka := preload("res://game/characters/hanka/character_hanka.gd")
const PCJoey := preload("res://game/characters/joey/character_joey.gd")
const PCBabicka := preload("res://game/characters/babicka/character_babicka.gd")
const PCTonda := preload("res://game/characters/tonda/character_tonda.gd")
const PCDeda := preload("res://game/characters/deda/character_deda.gd")
const PCVerka := preload("res://game/characters/verka/character_verka.gd")
const PCRybar := preload("res://game/characters/rybar/character_rybar.gd")
# ---- classes

# nodes ----
var Alica: PCAlica : get = get_Alica
var Hanka: PCHanka : get = get_Hanka
var Joey: PCJoey : get = get_Joey
var Babicka: PCBabicka : get = get_Babicka
var Tonda: PCTonda : get = get_Tonda
var Deda: PCDeda : get = get_Deda
var Verka: PCVerka : get = get_Verka
var Rybar: PCRybar : get = get_Rybar
# ---- nodes

# functions ----
func get_Alica() -> PCAlica: return get_runtime_character("Alica")
func get_Hanka() -> PCHanka: return get_runtime_character("Hanka")
func get_Joey() -> PCJoey: return get_runtime_character("Joey")
func get_Babicka() -> PCBabicka: return get_runtime_character("Babicka")
func get_Tonda() -> PCTonda: return get_runtime_character("Tonda")
func get_Deda() -> PCDeda: return get_runtime_character("Deda")
func get_Verka() -> PCVerka: return get_runtime_character("Verka")
func get_Rybar() -> PCRybar: return get_runtime_character("Rybar")
# ---- functions

