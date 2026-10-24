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
const PIIPulmapa := preload("res://game/inventory_items/pulmapa/inventory_item_pulmapa.gd")
const PIIMapa := preload("res://game/inventory_items/mapa/inventory_item_mapa.gd")
const PIIDopis := preload("res://game/inventory_items/dopis/inventory_item_dopis.gd")
const PIIVysilacka := preload("res://game/inventory_items/vysilacka/inventory_item_vysilacka.gd")
const PIIPlechovka := preload("res://game/inventory_items/plechovka/inventory_item_plechovka.gd")
const PIINovyDopis := preload("res://game/inventory_items/novy_dopis/inventory_item_novy_dopis.gd")
const PIIKlicHodin := preload("res://game/inventory_items/klic_hodin/inventory_item_klic_hodin.gd")
const PIIRukavicka := preload("res://game/inventory_items/rukavicka/inventory_item_rukavicka.gd")
const PIIPahyl := preload("res://game/inventory_items/pahyl/inventory_item_pahyl.gd")
# ---- classes

# nodes ----
var Lupa: PIILupa : get = get_Lupa
var Zapisnik: PIIZapisnik : get = get_Zapisnik
var StaraPonozka: PIIStaraPonozka : get = get_StaraPonozka
var Mouka: PIIMouka : get = get_Mouka
var NovaPonozka: PIINovaPonozka : get = get_NovaPonozka
var Nitka: PIINitka : get = get_Nitka
var Klic: PIIKlic : get = get_Klic
var Pulmapa: PIIPulmapa : get = get_Pulmapa
var Mapa: PIIMapa : get = get_Mapa
var Dopis: PIIDopis : get = get_Dopis
var Vysilacka: PIIVysilacka : get = get_Vysilacka
var Plechovka: PIIPlechovka : get = get_Plechovka
var NovyDopis: PIINovyDopis : get = get_NovyDopis
var KlicHodin: PIIKlicHodin : get = get_KlicHodin
var Rukavicka: PIIRukavicka : get = get_Rukavicka
var Pahyl: PIIPahyl : get = get_Pahyl
# ---- nodes

# functions ----
func get_Lupa() -> PIILupa: return get_item_instance("Lupa")
func get_Zapisnik() -> PIIZapisnik: return get_item_instance("Zapisnik")
func get_StaraPonozka() -> PIIStaraPonozka: return get_item_instance("StaraPonozka")
func get_Mouka() -> PIIMouka: return get_item_instance("Mouka")
func get_NovaPonozka() -> PIINovaPonozka: return get_item_instance("NovaPonozka")
func get_Nitka() -> PIINitka: return get_item_instance("Nitka")
func get_Klic() -> PIIKlic: return get_item_instance("Klic")
func get_Pulmapa() -> PIIPulmapa: return get_item_instance("Pulmapa")
func get_Mapa() -> PIIMapa: return get_item_instance("Mapa")
func get_Dopis() -> PIIDopis: return get_item_instance("Dopis")
func get_Vysilacka() -> PIIVysilacka: return get_item_instance("Vysilacka")
func get_Plechovka() -> PIIPlechovka: return get_item_instance("Plechovka")
func get_NovyDopis() -> PIINovyDopis: return get_item_instance("NovyDopis")
func get_KlicHodin() -> PIIKlicHodin: return get_item_instance("KlicHodin")
func get_Rukavicka() -> PIIRukavicka: return get_item_instance("Rukavicka")
func get_Pahyl() -> PIIPahyl: return get_item_instance("Pahyl")
# ---- functions

