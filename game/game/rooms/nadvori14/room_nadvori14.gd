@tool
extends "res://game/shared/story_room.gd"
## Story 14, the courtyard: the palace front, the square tower with three rows of putlog holes, the bench, jackdaws
## on the wall. Day 1: hunting for "14", Tonda's rohlík vanishes from the bench (Joey asleep with a jackdaw at his
## chest, never mentioned). Day 2: twigs and Joey's fur under the tower, putlog holes, Bětka draws the wall. Dawn:
## Hanka's torch, two pale eyes and the red ribbon; "Kdo krade na hradě?", the kastelánka about jackdaws, "Čtrnáctá
## díra", the ladder, Hanka's small hand, "Jméno pro kavku", the second Klub tin.

const Data := preload('room_nadvori14_state.gd')
const WhoGame := preload("res://game/minigames/who_14.gd")
const QuizGame := preload("res://game/minigames/quiz_14.gd")
const HolesGame := preload("res://game/minigames/holes.gd")
const SpellGame := preload("res://game/minigames/spell_14.gd")
const DAWN := Color(0.32, 0.3, 0.5)

var state: Data = load("res://game/rooms/nadvori14/room_nadvori14.tres")


func _dawn() -> bool:
	return Globals.h_twigs and Globals.h_drawing and not Globals.h_dawn


func _day2() -> bool:
	return Globals.h_kastel


func _on_room_entered() -> void:
	match C.player.last_room:
		"Sal14": C.player.position = get_hotspot("Sal").walk_to_point + Vector2(-100, 30)
		_: C.player.position = get_marker_position("Start")
	Globals.bring_sister(self, Vector2(170, 10))
	for who in ["Deda", "Verka", "Tonda", "Betka", "Rybar"]:
		place(who, get_marker_position(who))
	var joey := place("Joey", get_marker_position("Joey") if not _day2() else joey_spot())
	joey.pose("lie" if not Globals.h_bears else "")
	if _day2() or not Globals.h_rohlik:
		place("Kastelanka", get_marker_position("Kastelanka"))
	else:
		remove("Kastelanka")
	if not Globals.h_rohlik:
		C.Tonda.pose("rohlik" if not Globals.h_court else "")
	get_prop("Rohlik").visible = Globals.h_court and not Globals.h_rohlik
	get_prop("KavkaDole").visible = not Globals.h_bears
	get_prop("Vetvicky").visible = _day2()
	get_prop("Oci").visible = _dawn()
	get_prop("Zebrik").visible = Globals.h_count and not Globals.h_hole
	get_prop("Plechovka").visible = Globals.h_hole and not Globals.h_tin
	hidden_thing(null, "Klicek", "h_found", 10, "")
	Globals.exit_arrow(self, "Brana", true, not _dawn())
	Globals.exit_arrow(self, "Sal", false, not _dawn())
	if _dawn():
		dark(DAWN)


func _on_room_transition_finished() -> void:
	if not Globals.h_court:
		await C.Tonda.say("Rohlík si nechám na potom.")
		C.Tonda.pose()
		get_prop("Rohlik").show()
		Globals.h_court = true
		await C.Alica.say("Čtrnáct… Co je tady čtrnáct? Podívám se všude.")
	elif _dawn() and C.player != C.Hanka:
		await hand_over(C.Hanka, "Hani, posviť na věž.")
	elif Globals.h_dawn and not Globals.h_who:
		await _who()
	elif Globals.h_hole and not Globals.h_name:
		await _name()
	else:
		await _hunt_done()


func joey_goal() -> Vector2:
	if not Globals.h_windows: return get_hotspot("Okna").walk_to_point
	if not Globals.h_steps: return get_hotspot("Lavicka").walk_to_point
	if not Globals.h_tower: return get_hotspot("Vez").walk_to_point
	if not Globals.h_bears: return get_hotspot("Brana").walk_to_point
	if not Globals.h_kastel: return get_hotspot("Sal").walk_to_point
	if not Globals.h_twigs: return get_prop("Vetvicky").position + Vector2(-260, 120)
	if not Globals.h_drawing: return get_marker_position("Betka") + Vector2(-240, 20)
	if _dawn(): return get_hotspot("Vez").walk_to_point
	if not Globals.h_quiz: return get_marker_position("Kastelanka") + Vector2(-240, 20)
	if not Globals.h_count: return get_marker_position("Betka") + Vector2(-240, 20)
	if not Globals.h_hole: return get_prop("Zebrik").position + Vector2(-200, 160)
	if not Globals.h_tin: return get_prop("Plechovka").position + Vector2(-220, 20)
	return Vector2.ZERO


func on_click(node: Node) -> void:
	if await hidden_thing(node, "Klicek", "h_found", 10, "Klíček"):
		return
	match node.script_name:
		"Okna": await _windows()
		"Lavicka", "Rohlik": await _bench()
		"Vez", "Oci", "Zebrik": await _tower()
		"Kavka", "KavkaDole":
			await C.player.walk_to_clicked()
			await C.player.say("Černý ptáček. Má šedou hlavu a světlé oči.")
		"Vetvicky": await _twigs()
		"Plechovka": await _tin()
		"Brana":
			await C.player.walk_to_clicked()
			if _dawn():
				await C.player.say("Teď hlídáme. Nikam nejdu.")
				return
			R.goto_room("Brana14")
		"Sal":
			await C.player.walk_to_clicked()
			if _dawn():
				await C.player.say("Teď hlídáme. Nikam nejdu.")
				return
			if not Globals.h_bears:
				await C.player.say("Sál na spaní. Ještě je den, ještě budeme pátrat.")
				return
			R.goto_room("Sal14")
		_: await super(node)


func on_character(chr: PopochiuCharacter, action: String, _item: PopochiuInventoryItem = null) -> bool:
	if action == "look" or chr == C.Alica or chr == C.Hanka or chr == C.Joey:
		return false
	if _dawn():
		await C.player.say("Psst. Ostatní ještě spí.")
		return true
	await C.player.walk(chr.position + Vector2(-240, 20))
	match chr.script_name:
		"Kastelanka": await _kastelanka()
		"Betka": await _betka()
		"Tonda":
			if Globals.h_tin:
				await C.Tonda.say("Příště si rohlík schovám do kapsy!")
			elif Globals.h_who:
				await C.Tonda.say("Takže můj rohlík snědly kavky?")
				await C.Kastelanka.say("Ano. A ještě se o něj podělily.")
			elif Globals.h_rohlik:
				await C.Tonda.say("To byli medvědi! Mají hlad!")
				await C.Alica.say("Pojďme se podívat k příkopu.")
			else:
				await C.Tonda.say("Čtrnáct… Kroků? Oken? Schodů?")
		"Deda": await C.Deda.say("Na hradě jsme s Klubem byli na výletě. Ale kam jsme schovali plechovku?")
		"Verka":
			if Globals.h_hole and not Globals.h_tin:
				await _tin()
			else:
				await C.Verka.say("XIV… Ta věž mi něco připomíná.")
		"Rybar":
			if Globals.h_count and not Globals.h_hole:
				await C.Rybar.say("Žebřík podržíme s dědou. Neboj.")
			else:
				await C.Rybar.say("Tady je krásně. Ale ryby tu nejsou.")
		_: return false
	return true


#region Day 1: hunting 14 ##########################################################################
func _windows() -> void:
	await C.player.walk(get_hotspot("Okna").walk_to_point)
	if Globals.h_windows:
		await C.player.say("Tři okna. Ne čtrnáct.")
		return
	await C.Alica.say("Čtrnáct oken? Jedno, dvě, tři… Tady jsou jen tři.")
	Globals.h_windows = true
	await _hunt_done()


func _bench() -> void:
	await C.player.walk(get_hotspot("Lavicka").walk_to_point)
	if Globals.h_rohlik:
		await C.player.say("Na lavičce zbyly jen drobky.")
		return
	if Globals.h_steps:
		await C.player.say("Tondův rohlík na lavičce.")
		return
	await C.Alica.say("Od lavičky k věži. Kroky! Raz, dva, tři…")
	await C.Hanka.say("…dvanáct, třináct, čtrnáct! Nic tu není.")
	Globals.h_steps = true
	await _hunt_done()


func _tower() -> void:
	await C.player.walk(get_hotspot("Vez").walk_to_point)
	if _dawn():
		await _dawn_eyes()
		return
	if Globals.h_count and not Globals.h_hole:
		await _ladder()
		return
	if Globals.h_dawn and not Globals.h_who:
		await _who()
		return
	if Globals.h_hole and not Globals.h_name:
		await _name()
		return
	if Globals.h_hole:
		await C.player.say("Kavčí hnízdo zůstane ve čtrnácté díře. Na jaře se kavky vrátí.")
		return
	if Globals.h_who and not Globals.h_quiz:
		await C.player.say("Kavky bydlí v díře ve zdi. Paní kastelánka o nich ví všechno.")
		return
	if Globals.h_who and not Globals.h_count:
		await C.player.say("Která díra to je? Bětka má obrázek věže.")
		return
	if Globals.h_kastel and not Globals.h_twigs:
		await _twigs()
		return
	if Globals.h_twigs and not Globals.h_drawing:
		await C.player.say("Spousta děr. Bětka by je mohla nakreslit.")
		return
	if Globals.h_tower:
		await C.player.say("Tři řady děr ve zdi.")
		return
	await C.Alica.say("Ta věž má spoustu děr. Jsou ve třech řadách.")
	Globals.h_tower = true
	await _hunt_done()


func _hunt_done() -> void:
	if not (Globals.h_windows and Globals.h_steps and Globals.h_tower) or Globals.h_rohlik:
		return
	await C.Alica.say("Čtrnáct kroků, tři okna, hodně děr. Nic nesedí.")
	get_prop("Rohlik").hide()
	await C.Tonda.say("Můj rohlík! Je pryč!")
	await C.Tonda.say("To byli medvědi! Mají hlad!")
	await C.Alica.say("Pojďme se podívat k příkopu.")
	Globals.h_rohlik = true
	remove("Kastelanka")

#endregion


#region Day 2 ######################################################################################
func _twigs() -> void:
	await C.player.walk(get_prop("Vetvicky").position + Vector2(-260, 120))
	if Globals.h_twigs:
		await C.player.say("Větvičky a Joeyho chlupy.")
		return
	await C.Hanka.say("Joey něco našel!")
	await C.Joey.say("Čmuch čmuch!")
	await C.Hanka.say("Větvičky. A v nich Joeyho chlupy! Černé a bílé!")
	await C.Alica.say("Jak se Joeyho chlupy dostaly pod věž? Joey přece spal.")
	Globals.h_twigs = true
	await C.Kastelanka.say("Ty díry ve věži jsou po lešení. Stavitelé do nich kdysi strkali trámy.")
	await C.Alica.say("A kdo tam teď nosí větvičky?")
	await _maybe_dawn()


func _betka() -> void:
	if Globals.h_twigs and not Globals.h_drawing:
		await C.Betka.say("Nakreslím všechny díry. Tři řady po šesti.")
		Globals.h_drawing = true
		await _maybe_dawn()
		return
	if Globals.h_quiz and not Globals.h_count:
		await C.Alica.say("Bětko, ukaž ten obrázek věže. Která díra to je?")
		await C.Hanka.say("Tamta! Se stužkou!")
		var mg: CanvasLayer = HolesGame.new()
		add_child(mg)
		await mg.finished
		Globals.h_count = true
		await C.Alica.say("…třináct, čtrnáct! Čtrnáctá díra! XIV!")
		await C.Alica.say("A jejich díra je čtrnáctá. Tam bude poklad!")
		await C.Verka.say("Že by…?")
		await C.Kastelanka.say("Mladé kavky už vylétly. Můžeme se tam opatrně podívat. Přinesu žebřík.")
		await pop("Zebrik")
		return
	if Globals.h_who and not Globals.h_quiz:
		await C.Betka.say("Paní kastelánka ví o ptácích všechno. Zeptej se jí.")
		return
	await C.Betka.say("Nakreslím si všechno, co tu je.")


func _maybe_dawn() -> void:
	if not (Globals.h_twigs and Globals.h_drawing):
		return
	await C.Alica.say("Ráno budeme hlídat, kdo nosí větvičky do věže.")
	await fade(_dawn_set, "Svítání…")
	await hand_over(C.Hanka, "Hani, ty vstáváš první. Posviť na věž.")


func _dawn_set() -> void:
	dark(DAWN)
	get_prop("Oci").show()
	Globals.show_exit(self, "Brana", false)
	Globals.show_exit(self, "Sal", false)


func _dawn_eyes() -> void:
	if C.player != C.Hanka:
		await hand_over(C.Hanka, "Hani, posviť na věž.")
	await C.Hanka.say("Kdo to volá? Kja, kja!")
	await C.Hanka.say("Ali! Vstávej! Ve zdi je Bětčina stužka! A dvě světlé oči!")
	await C.Alica.say("Cože? Kde?")
	Globals.h_dawn = true
	await light_up(1.0)
	get_prop("Oci").hide()
	Globals.show_exit(self, "Brana", true)
	Globals.show_exit(self, "Sal", true)
	await _who()


func _who() -> void:
	await C.Alica.say("STOP, detektive! Kdo to byl?")
	var mg: CanvasLayer = WhoGame.new()
	add_child(mg)
	await mg.finished
	Globals.h_who = true
	sfx("KJA!", Vector2(1400, 300), 80)
	await C.Hanka.say("Černý ptáček! Vyletěl z té díry!")
	await C.Kastelanka.say("To je kavka. Bydlí v díře ve zdi věže.")
#endregion


#region The jackdaws, the hole, the tin ############################################################
func _kastelanka() -> void:
	if Globals.h_who and not Globals.h_quiz:
		await slideshow([
			["k_kavka", "Kastelanka", "Kavka je nejmenší z našich černých vran. Velká jako holub. Má šedý zátylek a světlé oči."],
			["k_nest", "Kastelanka", "Hnízdí v děrách. Větvičky, které se do díry nevejdou, spadnou dolů pod ni."],
			["k_nest", "Kastelanka", "Hnízdo si vystelou měkkými věcmi. Trávou, mechem, chlupy… a hadříky."],
			["k_share", "Kastelanka", "Kavky jsou chytré. A dělí se o jídlo. Pár spolu zůstane celý život."],
		])
		await C.Hanka.say("A ona nám vzala stužku?")
		await C.Kastelanka.say("Na vystlání hnízda. A Joeyho chlupy taky.")
		await C.Kastelanka.say("Tak, co jste si zapamatovali?")
		var mg: CanvasLayer = QuizGame.new()
		add_child(mg)
		await mg.finished
		Globals.h_quiz = true
		await C.Alica.say("A ve které díře kavky bydlí? Bětka má obrázek!")
		return
	if Globals.h_kastel and not Globals.h_twigs:
		await C.Kastelanka.say("Pod věží často něco leží. Podívejte se.")
		return
	if Globals.h_count and not Globals.h_hole:
		await C.Kastelanka.say("Žebřík stojí. Ale opatrně!")
		return
	await C.Kastelanka.say("Hrad postavil král Václav IV. Před víc než šesti sty lety!")


func _ladder() -> void:
	await C.Alica.say("Ale ta díra je hrozně malá.")
	await C.Deda.say("Velká ruka tam neprojde.")
	await C.Rybar.say("Moje taky ne.")
	await hand_over(C.Hanka, "Hani, ty máš nejmenší ruku!")
	await C.Hanka.say("Já mám nejmenší ruku!")
	await C.Alica.say("Opatrně, Hani!")
	await C.Hanka.walk(get_prop("Zebrik").position + Vector2(-200, 160))
	sfx("ŠUP!", Vector2(1392, 360), 60)
	await C.Betka.say("Moje stužka!")
	await C.Alica.say("Moje sponka!")
	await C.Tonda.say("A můj rohlík mají kavky v bříšku!")
	await C.Hanka.say("A tohle bylo úplně vzadu!")
	await pop("Plechovka")
	await C.Alica.say("Druhá plechovka Klubu Hvězdička!")
	await C.Kastelanka.say("Hnízdo necháme. Kavky se sem na jaře vrátí.")
	Globals.h_hole = true
	get_prop("Zebrik").hide()
	await _name()


func _name() -> void:
	await C.Hanka.say("Budeš se jmenovat Kája!")
	await C.Alica.say("Napíšu to pod Bětčin obrázek.")
	var mg: CanvasLayer = SpellGame.new()
	add_child(mg)
	await mg.finished
	Globals.h_name = true
	await C.Hanka.say("Kavka Kája!")


func _tin() -> void:
	if Globals.h_tin:
		return
	if not Globals.h_name:
		await _name()
	await C.player.walk(get_prop("Plechovka").position + Vector2(-220, 20))
	await C.Verka.say("Teď si vzpomínám! Čtrnáctá díra!")
	await C.Verka.say("Pod ní tenkrát ležela hromada kamení. Vylezli jsme na ni.")
	await C.Deda.say("Čtrnáctá díra. To nikdo neuhodne!")
	get_prop("Plechovka").hide()
	await slideshow([
		["k_tin", "Alica", "Mapa hvězd! A malý klíček s hvězdou."],
		["k_tin", "Alica", "A lísteček: „Poslední poklad čeká tam, kde jsou hvězdy nejblíž.“"],
		["k_tin", "Verka", "Ten klíček… ten patří k poslední plechovce."],
	])
	Globals.h_tin = true
	await C.Alica.say("Rohlík, stužka, sponka i poklad. Všechno vyřešeno!")
	await C.Hanka.say("Dobrou noc, Kájo!")
	await the_end("Konec 14. dílu")
#endregion
