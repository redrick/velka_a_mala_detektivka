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
const PCKostelnik := preload("res://game/characters/kostelnik/character_kostelnik.gd")
const PCBetka := preload("res://game/characters/betka/character_betka.gd")
const PCHajny := preload("res://game/characters/hajny/character_hajny.gd")
const PCKnihovnice := preload("res://game/characters/knihovnice/character_knihovnice.gd")
const PCMama := preload("res://game/characters/mama/character_mama.gd")
const PCTata := preload("res://game/characters/tata/character_tata.gd")
const PCLucie := preload("res://game/characters/lucie/character_lucie.gd")
const PCSkolnik := preload("res://game/characters/skolnik/character_skolnik.gd")
const PCMalyKarel := preload("res://game/characters/maly_karel/character_maly_karel.gd")
const PCKastelanka := preload("res://game/characters/kastelanka/character_kastelanka.gd")
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
var Kostelnik: PCKostelnik : get = get_Kostelnik
var Betka: PCBetka : get = get_Betka
var Hajny: PCHajny : get = get_Hajny
var Knihovnice: PCKnihovnice : get = get_Knihovnice
var Mama: PCMama : get = get_Mama
var Tata: PCTata : get = get_Tata
var Lucie: PCLucie : get = get_Lucie
var Skolnik: PCSkolnik : get = get_Skolnik
var MalyKarel: PCMalyKarel : get = get_MalyKarel
var Kastelanka: PCKastelanka : get = get_Kastelanka
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
func get_Kostelnik() -> PCKostelnik: return get_runtime_character("Kostelnik")
func get_Betka() -> PCBetka: return get_runtime_character("Betka")
func get_Hajny() -> PCHajny: return get_runtime_character("Hajny")
func get_Knihovnice() -> PCKnihovnice: return get_runtime_character("Knihovnice")
func get_Mama() -> PCMama: return get_runtime_character("Mama")
func get_Tata() -> PCTata: return get_runtime_character("Tata")
func get_Lucie() -> PCLucie: return get_runtime_character("Lucie")
func get_Skolnik() -> PCSkolnik: return get_runtime_character("Skolnik")
func get_MalyKarel() -> PCMalyKarel: return get_runtime_character("MalyKarel")
func get_Kastelanka() -> PCKastelanka: return get_runtime_character("Kastelanka")
# ---- functions

