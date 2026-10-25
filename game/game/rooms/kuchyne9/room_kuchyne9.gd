@tool
extends "res://game/shared/story_room.gd"
## Story 9, babička's kitchen in February. A coded slip falls out of the library book (zigzag edge,
## lavender); děda knows the club's star code and fetches the key; babička gives herself away ("To je D, ne B").
## Later a second slip turns up in Alica's boot, inside the house; děda's star has five strokes, babička's
## list has a one-stroke star; the pinking shears in her sewing corner. Then off to Masopust.

const Data := preload('room_kuchyne9_state.gd')
const CipherGame := preload("res://game/minigames/cipher.gd")
const PLACES := [
	"Do knihovny",
	"Ke mlýnu",
	"Zůstat doma",
]

var state: Data = load("res://game/rooms/kuchyne9/room_kuchyne9.tres")


func _on_room_entered() -> void:
	C.player.position = get_marker_position("Venku") if C.player.last_room != "" and C.player.last_room != "Menu" else get_marker_position("Start")
	Globals.bring_sister(self, Vector2(-170, 10))
	place("Joey", Vector2(1200, 990))
	if Globals.z_msg2 and not Globals.z_who:
		place("Babicka", Vector2(1100, 940))
	else:
		place("Babicka", Vector2(260, 900))
	place("Deda", Vector2(1000, 920))
	get_prop("Listek").visible = Globals.z_slip and not Globals.z_msg1
	get_prop("Bota").visible = _boot_time() and not Globals.z_msg2
	Globals.exit_arrow(self, "Dvere", false, Globals.z_db)


func _on_room_transition_finished() -> void:
	if not Globals.z_slip:
		await _start()
	elif Globals.z_msg1 and not Globals.z_db:
		await _d_not_b()
	elif Globals.z_star and Globals.z_shears and Globals.z_msg2 and not Globals.z_parade:
		await _ready_for_masopust()
	elif _boot_time() and not Globals.z_msg2:
		await C.Hanka.say("Alico! V tvé botě je papírek!")


func _boot_time() -> bool:
	return Globals.z_card and Globals.z_tonda and Globals.z_verka


func joey_goal() -> Vector2:
	if Globals.z_zig and Globals.z_lav and not Globals.z_msg1: return C.Deda.position + Vector2(-240, 40)
	if not Globals.z_msg1: return get_marker_position("Stul")
	if _boot_time() and not Globals.z_msg2: return get_prop("Bota").position + Vector2(-200, 60)
	if Globals.z_msg2 and not Globals.z_star: return C.Deda.position + Vector2(-240, 40)
	if Globals.z_msg2 and not Globals.z_shears: return get_prop("Sici").position + Vector2(-200, 220)
	return get_hotspot("Dvere").walk_to_point


func _start() -> void:
	await C.Alica.say("Knížka z knihovny. Pohádky o hvězdách.")
	sfx("ŠUP!", Vector2(580, 520), 60)
	await pop("Listek")
	Globals.z_slip = true
	C.Hanka.pose("point")
	await C.Hanka.say("Něco z ní vypadlo! Papírek!")
	C.Hanka.pose()


func on_click(node: Node) -> void:
	match node.script_name:
		"Listek": await _slip()
		"Kniha":
			await C.player.walk(get_marker_position("Stul"))
			await C.player.say("Knížka z knihovny. Babička ji minulý týden přinesla domů.")
		"Bota": await _boot()
		"Seznam": await _list()
		"Sici": await _sewing()
		"Kamna":
			await C.player.walk_to_clicked()
			await C.player.say("Kamna hřejí. Venku mrzne.")
		"Dvere":
			await C.player.walk_to_clicked()
			await _out()
		_: await super(node)


func on_character(chr: PopochiuCharacter, action: String, _item: PopochiuInventoryItem = null) -> bool:
	if action == "look" or chr == C.Alica or chr == C.Hanka:
		return false
	match chr.script_name:
		"Deda":
			await C.player.walk(chr.position + Vector2(-240, 20))
			if Globals.z_slip and not Globals.z_msg1:
				await _decode1()
			elif Globals.z_msg1 and not Globals.z_db:
				await _d_not_b()
			elif Globals.z_msg2 and not Globals.z_star:
				await _deda_star()
			else:
				await C.Deda.say("Hvězdičkové písmo… To jsem nepsal, holky. Na mou duši.")
		"Babicka":
			await C.player.walk(chr.position + Vector2(240, 20))
			await C.Babicka.say("Zítra je masopust. Šiju vám masky!" if Globals.z_msg2 else "Co luštíte, detektivky?")
		"Joey":
			if Globals.z_slip and not Globals.z_lav:
				await _sniff()
			else:
				return false
		_:
			return false
	return true


#region The first slip ##############################################################################
func _slip() -> void:
	await C.player.walk(get_marker_position("Stul"))
	await picture("res://assets/slides/slip1.png", "Tajná zpráva")
	await C.Alica.say("Hvězdičky, měsíčky, srdíčka a kolečka. A pod nimi tečky jako na kostce!")
	if not Globals.z_zig:
		C.Hanka.pose("point")
		await C.Hanka.say("Papírek má zoubky! Na kraji. Jako pilka.")
		C.Hanka.pose()
		Globals.z_zig = true
	if not Globals.z_lav:
		await _sniff()
	if not Globals.z_msg1:
		await C.Alica.say("Dědo! Neznáš tohle písmo?")


func _sniff() -> void:
	await C.Joey.walk(get_marker_position("Stul") + Vector2(140, 60))
	await C.Joey.say("Čmuch čmuch!")
	await C.Hanka.say("Joey čmuchá. Papírek voní… levandulí!")
	Globals.z_lav = true


func _decode1() -> void:
	await C.Deda.say("To je hvězdičkové písmo! Písmo Klubu Hvězdička!")
	await C.Deda.say("Vymysleli jsme ho s Frantou a Věrkou. Klíč mám v klubovém zápisníku. Tady je!")
	await picture("res://assets/slides/cipher_key9.png", "Klíč")
	await C.Alica.say("Tvar je řádek a tečky jsou místo v řádku. Jdeme luštit!")
	var mg: CanvasLayer = CipherGame.new()
	mg.messages = ["HLEDEJ HVEZDU|NA MASOPUSTU"]
	add_child(mg)
	await mg.finished
	Globals.z_msg1 = true
	get_prop("Listek").hide()
	await C.Alica.say("Hledej hvězdu na masopustu! Ale kdo to napsal?")
	await _d_not_b()


func _d_not_b() -> void:
	await C.Alica.say("Napřed mi to vyšlo H… L… E… B? Nebo D?")
	await C.Babicka.say("To je D, ne B.")
	await C.Alica.say("Babi? Ty umíš hvězdičkové písmo? Vždyť ses ani nepodívala do klíče!")
	await C.Babicka.say("Já? Ale kdepak. To jen tak, od pohledu.")
	Globals.z_db = true
	Globals.show_exit(self, "Dvere")
	await C.Alica.say("Knížka je z knihovny. Zeptáme se paní knihovnice!")
#endregion


#region The second slip, the stars, the shears ######################################################
func _boot() -> void:
	await C.player.walk_to_clicked(Vector2(-200, 40))
	if Globals.z_msg2:
		await C.Alica.say("Moje bota.")
		return
	await C.Alica.say("V mojí botě je další papírek! Zase se zoubky!")
	await picture("res://assets/slides/slip2.png", "Další zpráva")
	var mg: CanvasLayer = CipherGame.new()
	mg.messages = ["PRIJD|V MASCE"]
	add_child(mg)
	await mg.finished
	Globals.z_msg2 = true
	get_prop("Bota").hide()
	await C.Alica.say("Přijď v masce! A tahle zpráva byla u nás doma. V mojí botě!")
	await C.Alica.say("Kdo může k nám do domu? Děda… nebo babička.")


func _deda_star() -> void:
	await C.Alica.say("Dědo, nakresli mi hvězdičku. Prosím.")
	await C.Deda.say("Hvězdičku? Jedna, dvě, tři, čtyři, pět čar. Hotovo.")
	await picture("res://assets/slides/stars9.png", "Děda kreslí pět čar. Ve zprávě je hvězdička jedním tahem.")
	await C.Alica.say("Děda kreslí hvězdu pěti čarami. Hvězdičky ve zprávě jsou jedním tahem!")
	Globals.z_star = true
	await _ready_for_masopust()


func _list() -> void:
	await C.player.walk(get_prop("Seznam").position + Vector2(0, 640))
	if not Globals.z_msg2:
		await C.player.say("Babiččin nákupní seznam. Mouka, vejce, povidla.")
		return
	C.Alica.pose("lens")
	await C.Alica.say("Babiččin seznam. A dole je hvězdička. Jedním tahem!")
	C.Alica.pose()
	if not Globals.z_star:
		await C.Alica.say("Jak kreslí hvězdu děda? Zeptám se ho.")
		return
	await _ready_for_masopust()


func _sewing() -> void:
	await C.player.walk(get_prop("Sici").position + Vector2(-200, 220))
	if not Globals.z_msg2:
		await C.player.say("Babiččin šicí koutek. Šije masky na masopust.")
		return
	if C.player == C.Hanka:
		C.Hanka.pose("point")
		await C.Hanka.say("Nůžky! A dělají zoubky! Na zemi jsou samé zubaté hadříky!")
		C.Hanka.pose()
	else:
		await C.Alica.say("Babiččiny krejčovské nůžky. Stříhají zoubky! Hani, koukni na hadříky.")
		await C.Hanka.say("Zoubky! Jako na papírku!")
	Globals.z_shears = true
	await _ready_for_masopust()


func _ready_for_masopust() -> void:
	if not (Globals.z_star and Globals.z_shears and Globals.z_msg2):
		return
	await C.Alica.say("Zoubky, levandule, hvězdička jedním tahem… Mám podezření. Ale musím to vidět na vlastní oči.")
	await C.Babicka.say("Zítra je masopust! Alica bude sova a Hanka medvídek. Šila jsem celý týden.")
	await fade(func(): pass, "Masopustní sobota…")
	R.goto_room("Masopust9")
#endregion


func _out() -> void:
	if not Globals.z_db:
		await C.player.say("Nejdřív rozluštíme papírek.")
		return
	var opts: Array = PLACES.slice(0, 2 if Globals.z_card else 1) + [PLACES[2]]
	var pick := await choose("Kam půjdeme?", opts)
	await go_place(opts[pick])


## Also called by the tests.
func go_place(where: String) -> void:
	match where:
		"Do knihovny": R.goto_room("Knihovna9")
		"Ke mlýnu": R.goto_room("Mlyn9")
