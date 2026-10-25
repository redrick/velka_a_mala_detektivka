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
const PRPokoj4 := preload("res://game/rooms/pokoj4/room_pokoj4.gd")
const PRVes4 := preload("res://game/rooms/ves4/room_ves4.gd")
const PRPole4 := preload("res://game/rooms/pole4/room_pole4.gd")
const PRMolo4 := preload("res://game/rooms/molo4/room_molo4.gd")
const PRZahrada5 := preload("res://game/rooms/zahrada5/room_zahrada5.gd")
const PRVes5 := preload("res://game/rooms/ves5/room_ves5.gd")
const PRFranta5 := preload("res://game/rooms/franta5/room_franta5.gd")
const PRKuchyne5 := preload("res://game/rooms/kuchyne5/room_kuchyne5.gd")
const PRKuchyne6 := preload("res://game/rooms/kuchyne6/room_kuchyne6.gd")
const PRZahrada6 := preload("res://game/rooms/zahrada6/room_zahrada6.gd")
const PRMlyn6 := preload("res://game/rooms/mlyn6/room_mlyn6.gd")
const PRZahrada7 := preload("res://game/rooms/zahrada7/room_zahrada7.gd")
const PRKuchyne7 := preload("res://game/rooms/kuchyne7/room_kuchyne7.gd")
const PRLes7 := preload("res://game/rooms/les7/room_les7.gd")
const PRZahrada8 := preload("res://game/rooms/zahrada8/room_zahrada8.gd")
const PRLouka8 := preload("res://game/rooms/louka8/room_louka8.gd")
const PRLes8 := preload("res://game/rooms/les8/room_les8.gd")
const PRKuchyne8 := preload("res://game/rooms/kuchyne8/room_kuchyne8.gd")
const PRKuchyne9 := preload("res://game/rooms/kuchyne9/room_kuchyne9.gd")
const PRKnihovna9 := preload("res://game/rooms/knihovna9/room_knihovna9.gd")
const PRMlyn9 := preload("res://game/rooms/mlyn9/room_mlyn9.gd")
const PRMasopust9 := preload("res://game/rooms/masopust9/room_masopust9.gd")
const PRSkola10 := preload("res://game/rooms/skola10/room_skola10.gd")
const PRKumbal10 := preload("res://game/rooms/kumbal10/room_kumbal10.gd")
const PRDomov10 := preload("res://game/rooms/domov10/room_domov10.gd")
const PRDvur11 := preload("res://game/rooms/dvur11/room_dvur11.gd")
const PRKurnik11 := preload("res://game/rooms/kurnik11/room_kurnik11.gd")
const PRStodola11 := preload("res://game/rooms/stodola11/room_stodola11.gd")
const PRKuchyne11 := preload("res://game/rooms/kuchyne11/room_kuchyne11.gd")
const PRChalupa12 := preload("res://game/rooms/chalupa12/room_chalupa12.gd")
const PRVes12 := preload("res://game/rooms/ves12/room_ves12.gd")
const PRChodba12 := preload("res://game/rooms/chodba12/room_chodba12.gd")
const PRZahrada12 := preload("res://game/rooms/zahrada12/room_zahrada12.gd")
const PRLouka13 := preload("res://game/rooms/louka13/room_louka13.gd")
const PRPotok13 := preload("res://game/rooms/potok13/room_potok13.gd")
const PRHraz13 := preload("res://game/rooms/hraz13/room_hraz13.gd")
const PRBrana14 := preload("res://game/rooms/brana14/room_brana14.gd")
const PRNadvori14 := preload("res://game/rooms/nadvori14/room_nadvori14.gd")
const PRSal14 := preload("res://game/rooms/sal14/room_sal14.gd")
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
var Pokoj4: PRPokoj4 : get = get_Pokoj4
var Ves4: PRVes4 : get = get_Ves4
var Pole4: PRPole4 : get = get_Pole4
var Molo4: PRMolo4 : get = get_Molo4
var Zahrada5: PRZahrada5 : get = get_Zahrada5
var Ves5: PRVes5 : get = get_Ves5
var Franta5: PRFranta5 : get = get_Franta5
var Kuchyne5: PRKuchyne5 : get = get_Kuchyne5
var Kuchyne6: PRKuchyne6 : get = get_Kuchyne6
var Zahrada6: PRZahrada6 : get = get_Zahrada6
var Mlyn6: PRMlyn6 : get = get_Mlyn6
var Zahrada7: PRZahrada7 : get = get_Zahrada7
var Kuchyne7: PRKuchyne7 : get = get_Kuchyne7
var Les7: PRLes7 : get = get_Les7
var Zahrada8: PRZahrada8 : get = get_Zahrada8
var Louka8: PRLouka8 : get = get_Louka8
var Les8: PRLes8 : get = get_Les8
var Kuchyne8: PRKuchyne8 : get = get_Kuchyne8
var Kuchyne9: PRKuchyne9 : get = get_Kuchyne9
var Knihovna9: PRKnihovna9 : get = get_Knihovna9
var Mlyn9: PRMlyn9 : get = get_Mlyn9
var Masopust9: PRMasopust9 : get = get_Masopust9
var Skola10: PRSkola10 : get = get_Skola10
var Kumbal10: PRKumbal10 : get = get_Kumbal10
var Domov10: PRDomov10 : get = get_Domov10
var Dvur11: PRDvur11 : get = get_Dvur11
var Kurnik11: PRKurnik11 : get = get_Kurnik11
var Stodola11: PRStodola11 : get = get_Stodola11
var Kuchyne11: PRKuchyne11 : get = get_Kuchyne11
var Chalupa12: PRChalupa12 : get = get_Chalupa12
var Ves12: PRVes12 : get = get_Ves12
var Chodba12: PRChodba12 : get = get_Chodba12
var Zahrada12: PRZahrada12 : get = get_Zahrada12
var Louka13: PRLouka13 : get = get_Louka13
var Potok13: PRPotok13 : get = get_Potok13
var Hraz13: PRHraz13 : get = get_Hraz13
var Brana14: PRBrana14 : get = get_Brana14
var Nadvori14: PRNadvori14 : get = get_Nadvori14
var Sal14: PRSal14 : get = get_Sal14
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
func get_Pokoj4() -> PRPokoj4: return get_runtime_room("Pokoj4")
func get_Ves4() -> PRVes4: return get_runtime_room("Ves4")
func get_Pole4() -> PRPole4: return get_runtime_room("Pole4")
func get_Molo4() -> PRMolo4: return get_runtime_room("Molo4")
func get_Zahrada5() -> PRZahrada5: return get_runtime_room("Zahrada5")
func get_Ves5() -> PRVes5: return get_runtime_room("Ves5")
func get_Franta5() -> PRFranta5: return get_runtime_room("Franta5")
func get_Kuchyne5() -> PRKuchyne5: return get_runtime_room("Kuchyne5")
func get_Kuchyne6() -> PRKuchyne6: return get_runtime_room("Kuchyne6")
func get_Zahrada6() -> PRZahrada6: return get_runtime_room("Zahrada6")
func get_Mlyn6() -> PRMlyn6: return get_runtime_room("Mlyn6")
func get_Zahrada7() -> PRZahrada7: return get_runtime_room("Zahrada7")
func get_Kuchyne7() -> PRKuchyne7: return get_runtime_room("Kuchyne7")
func get_Les7() -> PRLes7: return get_runtime_room("Les7")
func get_Zahrada8() -> PRZahrada8: return get_runtime_room("Zahrada8")
func get_Louka8() -> PRLouka8: return get_runtime_room("Louka8")
func get_Les8() -> PRLes8: return get_runtime_room("Les8")
func get_Kuchyne8() -> PRKuchyne8: return get_runtime_room("Kuchyne8")
func get_Kuchyne9() -> PRKuchyne9: return get_runtime_room("Kuchyne9")
func get_Knihovna9() -> PRKnihovna9: return get_runtime_room("Knihovna9")
func get_Mlyn9() -> PRMlyn9: return get_runtime_room("Mlyn9")
func get_Masopust9() -> PRMasopust9: return get_runtime_room("Masopust9")
func get_Skola10() -> PRSkola10: return get_runtime_room("Skola10")
func get_Kumbal10() -> PRKumbal10: return get_runtime_room("Kumbal10")
func get_Domov10() -> PRDomov10: return get_runtime_room("Domov10")
func get_Dvur11() -> PRDvur11: return get_runtime_room("Dvur11")
func get_Kurnik11() -> PRKurnik11: return get_runtime_room("Kurnik11")
func get_Stodola11() -> PRStodola11: return get_runtime_room("Stodola11")
func get_Kuchyne11() -> PRKuchyne11: return get_runtime_room("Kuchyne11")
func get_Chalupa12() -> PRChalupa12: return get_runtime_room("Chalupa12")
func get_Ves12() -> PRVes12: return get_runtime_room("Ves12")
func get_Chodba12() -> PRChodba12: return get_runtime_room("Chodba12")
func get_Zahrada12() -> PRZahrada12: return get_runtime_room("Zahrada12")
func get_Louka13() -> PRLouka13: return get_runtime_room("Louka13")
func get_Potok13() -> PRPotok13: return get_runtime_room("Potok13")
func get_Hraz13() -> PRHraz13: return get_runtime_room("Hraz13")
func get_Brana14() -> PRBrana14: return get_runtime_room("Brana14")
func get_Nadvori14() -> PRNadvori14: return get_runtime_room("Nadvori14")
func get_Sal14() -> PRSal14: return get_runtime_room("Sal14")
# ---- functions

