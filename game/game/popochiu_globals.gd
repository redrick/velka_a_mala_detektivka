extends Node

var case_started := false
var footprints_found := false
var joey_cleared := false
var trap_planned := false
var got_flour := false
var trap_set := false
var night_done := false
var thread_found := false
var bush_found := false
var stream_crossed := false
var hanka_behind_fence := false
var shed_done := false
var nails_done := 0
var game_finished := false
# "", "evening", "night", "ending": which cutscene the next room entry should play
var phase := ""
## Which story (episode number) is being played; also its save slot. 0 = in the menu.
var story := 0

# story 2 "Tajemství starého klíče" --------------------------------------------------------------
var k_noises := 0          # noises heard from the attic at night (3 = all)
var k_breakfast := false   # děda said "na půdu se nechodí"
var k_feather := false
var k_pellets := false
var k_window := false      # the star on the attic window = the star on the key
var k_ladder := false      # děda agreed and put up the ladder
var k_chest := false       # chest opened, flashback and riddle seen
var k_owls := false        # the owls found; next morning in the attic
var k_sunbeam := false     # mirrors minigame done, the star of light is on the floor
var k_planks := 0          # planks counted from the star
var k_map := false         # both halves of the map
var k_nails := 0           # nails in the owl box

# story 3 "Mapa ke starému rybníku" ----------------------------------------------------------------
var r_intro := false       # the map scene in the kitchen
var r_stump := false       # děda recognised the stump of the big willow
var r_steps := false       # the 20 children's steps done, star stone found
var r_hole := false        # Joey dug: someone was here first
var r_boots := false
var r_dots := false
var r_tonda_ran := false
var r_burrow := false
var r_rybar := false
var r_evening := false     # the quarrel at home and making up
var r_tonda_ok := false    # dawn: Tonda's secret, he joins
var r_prints := false      # whose print is it? minigame
var r_trail := false       # Joey's nose leads to the mill
var r_verka := false       # the lady at the bench gave Joey a biscuit
var r_end := false

# story 4 "Hanka to vyřeší!" (Alica is ill; Hanka plays) ------------------------------------------
var f_intro := false       # the letter at Alica's bed, Hanka got the walkie-talkie
var f_kurnik := false      # babička's new henhouse: not the hen from the letter
var f_inside := false      # inside the old henhouse: the hen, the star and the F
var f_prints := false      # the big zigzag print reported to HQ
var f_three := false       # three o'clock at the church: the hand points TAM
var f_rocks := 0           # rocks tried on the field before anyone knew which
var f_magpie := false      # the magpie flew off with something shiny
var f_boot := false        # Tonda fished an old boot out of the brook
var f_evening := false     # the suspects at Alica's bed
var f_tower := false       # the sexton cleared, the view from the tower: the Bota rock
var f_bota := false        # at the Bota: the wrapper, the prints, the float; dusk
var f_tin := false         # Hanka's torch found the tin in the crack
var f_opened := false      # the tin opened at Alica's bed
var f_who := false         # who walked the trail ahead of us? (minigame)
var f_read := false        # the new letter read: the jetty at three
var f_franta := false      # the fisherman is Franta
var f_clock := false       # the clock runs again
var f_radio := false       # Alica radios Hanka across the rock field to the Bota rock (minigame)

# story 5 "Kdo staví sněhuláky?" --------------------------------------------------------------------
var s_intro := false       # the first snow, "ráno postavíme sněhuláka"
var s_day := 0             # which morning it is (1-4)
var s_nose := false        # Alica: walnut eyes, pinecone buttons, the nose isn't a carrot
var s_stars := false       # the small prints with stars on the soles
var s_road := false        # the prints vanish where the tractor went
var s_tonda := false       # Tonda: "já stavím jenom obry"
var s_dog := false         # snowman 2 with a snow dog
var s_thread := false      # a red woollen thread on the fence
var s_babicka := false     # babička cleared: dough on her gloves, baking for Advent
var s_tonda_ok := false    # Tonda cleared: big boots, no pompom; "pastinák má jenom Franta"
var s_parsnip := false     # at Franta's: crates of parsnips
var s_boots := false       # small star-soled boots by Franta's stove
var s_curtain := false     # the curtain to the stairs moved
var s_mitten := false      # snowman 3 holds Hanka's lost mitten
var s_who := false         # who builds the snowmen? (minigame)
var s_answer := false      # the girls' answer, built from snowballs (minigame)
var s_betka := false       # met Bětka
var s_mittens := false     # the wet mittens mixed up by the stove, sorted back (minigame)

# story 6 "Kam mizí perníčky?" --------------------------------------------------------------------
var p_intro := false       # baking: 12 stars, 12 hearts, 12 moons; crooked pieces on the sill
var p_day := 0             # 1 = first morning, 2 = second morning
var p_sill := false        # pecked pieces and fork-like prints on the sill
var p_tin1 := false        # 7 stars gone from the tin
var p_joey := false        # floury paw prints end at the tin (he only begged)
var p_birds := false       # dawn watch: the tits on the sill
var p_feeder := false      # the bird feeder built
var p_tin2 := false        # 2 more stars gone
var p_trap := false        # děda's mousetrap has no bait
var p_hanka := false       # chocolate crumbs on Hanka: from her heart, not a star
var p_tonda := false       # Tonda likes moons, and wasn't in the house at night
var p_boots := false       # děda's boots: spruce needles and a red ribbon
var p_who := false         # who takes the stars? (minigame)
var p_spruce := false      # caught at the spruce by the mill
var p_stars := false       # the stars hung by the club rule (minigame)
var p_food := false        # every bird at the feeder gets its own food (minigame)

# story 7 "Joeyho velký den" -------------------------------------------------------------------------
var j_morning := false     # Joey told the morning (slides): cold hands, the glove, the shovel, the fort
var j_case := false        # evening: babička's ring is gone
var j_feeder := false      # searched at the feeder: the snow is shovelled away
var j_glove := false       # the glove is gone too: Joey suspected
var j_stash := false       # Joey's stash dug up: glove, bone, sock, no ring
var j_tonda := false       # Tonda saw the magpie carry something shiny to the forest
var j_straka := false      # the hajný: only foil, and magpies are wary of shiny things
var j_where := false       # where can the ring be? (minigame)
var j_ring := false        # Joey sniffed out the ring in the fort (minigame)
var j_order := false       # Joey tells his morning in the right order (minigame)

# story 8 "Stopy ve sněhu" ---------------------------------------------------------------------------
var n_day := 1             # 1 = the first morning, 2 = after the clean-page night
var n_high := false        # even the tallest snowman lost its nose
var n_stub := false        # Hanka found a bitten stub: frayed
var n_trampled := false    # the prints are trampled by Joey
var n_hajny := false       # the hajný: "first learn the tracks"
var n_hare := false        # hare: Y prints, clean cut, small
var n_fox := false         # fox: a straight line to the mousehole
var n_boar := false        # boar: wider, two dots behind
var n_guide := false       # the track guide, "make a clean page"
var n_clean := false       # one kind of print on the clean snow
var n_who := false         # who eats the noses? (minigame)
var n_trail := false       # followed the deer trail (minigame)
var n_bed := false         # Hanka found the deer's bed under the low spruce
var n_scale := false       # the same hay in both racks of the krmelec (minigame)

# story 9 "Tajná zpráva v knihovně" -------------------------------------------------------------------
var z_slip := false        # the slip falls out of the library book
var z_zig := false         # Hanka: the slip has a zigzag edge
var z_lav := false         # Joey smells lavender on it
var z_msg1 := false        # HLEDEJ HVEZDU NA MASOPUSTU (minigame)
var z_db := false          # babička: "To je D, ne B" without the key
var z_card := false        # the borrowing card: H. and J. in 1966, Tonda in December
var z_tonda := false       # Tonda can't read the code
var z_verka := false       # Věrka hides a star: her kominík hat; flour, not lavender
var z_msg2 := false        # PRIJD V MASCE, in Alica's boot inside the house (minigame)
var z_star := false        # děda's star has 5 strokes; the message's stars are one stroke, like babička's list
var z_shears := false      # babička's pinking shears cut zigzags
var z_who := false         # who wrote the message? (parade, minigame)
var z_end := false
var z_parade := false      # the masks lined up for the parade (minigame)

# story 10 "Záhada ve škole" --------------------------------------------------------------------------
var q_day := 1             # 1 = Monday at school, 2 = Tuesday's field day
var q_intro := false       # the hutch is open, Míša and Šiša are gone
var q_hutch := false       # the latch is broken; wood shavings inside
var q_prints := false      # big herringbone holínky prints go to the log building
var q_nest := false        # the hay trail leads to the hedgehog's nest; a torn note "…V TEPLE. K."
var q_karel := false       # malý Karel: hay from his rabbit, at grandma's on Sunday
var q_door := false        # the kumbál is locked, only pan Karel has the key; his hat hook is empty
var q_box := false         # táta picks Alica up: a big box with air holes
var q_home := false        # evening at home: the frost, the video call
var q_who := false         # who took Míša and Šiša? (minigame)
var q_wheek := false       # Hanka rustles her bag: UÍÍÍK from the kumbál
var q_found := false       # in the kumbál, in pan Karel's hat
var q_new := false         # the new hutch built (minigame)
var q_pens := false        # a pen for every guinea pig on the meadow (minigame)

# story 11 "Kam mizí vajíčka?" ------------------------------------------------------------------------
var v_intro := false       # Maundy Thursday at the chalupa: eight hens, one egg short every day
var v_count := false       # Hanka counts seven eggs
var v_fox := false         # the prints by the run are round: Joey's, not a fox's
var v_shells := false      # no eggshells anywhere: nobody ate them
var v_magpie := false      # the magpie's nest: foil, ribbon, the old spoon, no egg
var v_tonda := false       # Tonda brings eggs, he doesn't take them
var v_straw := false       # Kropenatka puffed up, straw in her feathers
var v_missing := false     # Saturday evening: Kropenatka is missing
var v_gap := false         # the gap under the wire, a speckled feather, hen prints to the barn
var v_who := false         # where are the eggs? who? (minigame)
var v_bales := false       # Hanka crawls through the bales (minigame): the nest
var v_swap := false        # Věrka's eggs from under her rooster for Kropenatka
var v_pattern := false     # the kraslice laid out in repeating rows (minigame)

# story 12 "Tajemné šipky" ----------------------------------------------------------------------------
var a_intro := false       # three weeks later at the chalupa: the chicks, máma's lunchbox note with a heart
var a_arrow := false       # the first chalk arrow on the path: dashed, a heart at the end
var a_shed := false        # děda's shed is locked; "mňau" from inside; "To byla… straka!"
var a_flour := false       # babička, all floury: "Nesmíš sem!"
var a_home := false        # back home in the village: arrows everywhere
var a_high := false        # the long solid arrow high on the garage, an oil smudge next to it
var a_dashed := false      # the dashed arrow with a heart on the pavement
var a_dotted := false      # the tiny dotted arrow right down by the fence
var a_tonda := false       # Tonda: chalky hands, a real hopscotch, a white card falls out of his pocket
var a_tracks := false      # wide knobbly tyre tracks to the locked garage; táta, oily: "Opravuju… sekačku."
var a_phone := false       # máma whispering on the phone, the torn list "balónky, limo, 8…"
var a_shavings := false    # Hanka guards the space under the stairs: "To je tajemství!", shavings in her pocket
var a_hurt := false        # the garden gate is locked, whispers "…Klub…": a meeting without Alica
var a_morning := false     # the night (Hanka nearly tells opička), then the birthday morning: nobody says anything
var a_who := false         # who drew which arrow? (three rounds)
var a_tam := false         # Hanka's torch finds the star under the stairs: TAM
var a_skoc := false        # the hopscotch star: SKOČ
var a_joey := false        # Joey sits on the next arrow until Alica says "hodný"
var a_arrows := false      # the rain-smudged arrows put right (minigame): door -> stars -> gate
var a_hanka := false       # Hanka's present: the cat drawing and the peeled stick
var a_kitten := false      # děda's present: the kitten Micka (the "magpie" in the shed)
var a_bike := false        # the parents' present: the pink bike with a front fork (the tyre tracks)
var a_seating := false     # everyone seated at the party table (minigame)

## Per-story progress next to Popochiu's save files: saved?, finished?, and the last story played.
const PROGRESS := "user://progress.cfg"


func _ready() -> void:
	# E is the next autoload: connect once everything is in the tree
	(func(): E.game_loaded.connect(_on_game_loaded)).call_deferred()


## Autosave: whenever a story room has been entered (after its setup, before its cutscene).
func _process(_delta: float) -> void:
	if story <= 0 or not E.in_room or not is_instance_valid(R.current) or R.current.script_name == "Menu":
		return
	if get_meta("saved_room", 0) != R.current.get_instance_id():
		set_meta("saved_room", R.current.get_instance_id())
		save_now()


func _notification(what: int) -> void:
	if what == NOTIFICATION_WM_CLOSE_REQUEST:
		save_now()


func save_now() -> void:
	if story <= 0 or not is_instance_valid(R.current) or R.current.script_name == "Menu":
		return
	if not get_tree().get_nodes_in_group("minigame").is_empty():
		return
	E.save_game(story, "story %d" % story)
	var cfg := _progress()
	cfg.set_value("story_%d" % story, "saved", true)
	cfg.set_value("story_%d" % story, "finished", game_finished)
	cfg.set_value("general", "last_story", story)
	cfg.save(PROGRESS)


func has_save(n: int) -> bool:
	return FileAccess.file_exists("user://save_%d.json" % n) and _progress().get_value("story_%d" % n, "saved", false)


func is_finished(n: int) -> bool:
	return _progress().get_value("story_%d" % n, "finished", false)


## The story to offer under "Pokračovat" on the first menu screen, or 0.
func last_story() -> int:
	var n: int = _progress().get_value("general", "last_story", 0)
	return n if has_save(n) and not is_finished(n) else 0


## An exit at the edge of a room: a wider click area and a pulsing yellow arrow, so the way on is
## visible. `left` = the exit is at the left edge. Show or hide it later with show_exit().
func exit_arrow(room: Node, hotspot: String, left: bool, on := true) -> void:
	var h: PopochiuHotspot = room.get_hotspot(hotspot)
	var x0 := 0.0 if left else 1690.0
	h.interaction_polygon = PackedVector2Array([Vector2(x0, 600), Vector2(x0 + 230, 600), Vector2(x0 + 230, 1060), Vector2(x0, 1060)])
	var a := Sprite2D.new()
	a.name = "Arrow" + hotspot
	a.texture = load("res://assets/minigames/%s.png" % ("arrow_left" if left else "arrow"))
	a.position = Vector2(130.0 if left else 1790.0, 820.0)
	a.z_index = 50
	room.add_child(a)
	var tw := a.create_tween().set_loops()
	tw.tween_property(a, "position:x", a.position.x + (-20.0 if left else 20.0), 0.6)
	tw.tween_property(a, "position:x", a.position.x, 0.6)
	show_exit(room, hotspot, on)


func show_exit(room: Node, hotspot: String, on := true) -> void:
	var a := room.get_node_or_null("Arrow" + hotspot)
	if a:
		a.visible = on


func _progress() -> ConfigFile:
	var cfg := ConfigFile.new()
	cfg.load(PROGRESS)
	return cfg


func sister() -> PopochiuCharacter:
	return C.get_character("Hanka" if C.player.script_name == "Alica" else "Alica")


func bring_sister(room: PopochiuRoom, offset := Vector2(-170, 10)) -> void:
	var other := sister()
	if not room.has_character(other.script_name):
		room.add_character(other)
	var x := C.player.position.x + offset.x
	if x < 240.0 or x > 1680.0:
		offset.x = -offset.x
	other.position = C.player.position + offset


func switch_to(chr: PopochiuCharacter) -> void:
	var old := C.player
	chr.stop_following_character()
	C.player = chr
	old.start_following_character(chr)


func start_episode(start_room: String, number: int) -> void:
	_reset_progress()
	story = number
	# what the girls already carry when a story starts
	if number == 2:
		I.Zapisnik.add(false)
		I.Klic.add(false)
	elif number == 3:
		I.Zapisnik.add(false)
		I.Mapa.add(false)
	elif number == 4:
		I.Dopis.add(false)
		C.player = C.get_character("Hanka")
	elif number in [5, 6, 7, 8, 9, 10, 11, 12]:
		I.Zapisnik.add(false)
	if number == 8:
		phase = "n_start"
	dress()
	G.show_interface()
	R.goto_room(start_room)


## Winter stories (December to February) put hats on the girls and Tonda; also the hover names below.
const WINTER := [5, 6, 7, 8, 9]


func dress() -> void:
	var w := story in WINTER
	for who in ["Alica", "Hanka", "Tonda"]:
		var chr := C.get_character(who)
		chr.set_outfit(who.to_lower() + ("w" if w else ""))
	# hover names that change with the stories: the fisherman is pan Franta (from story 4's jetty on), and the
	# girl with the pompom is Bětka once story 5 has introduced her
	C.get_character("Rybar").description = "Pan Franta" if story >= 5 or (story == 4 and f_franta) else "Rybář"
	C.get_character("Betka").description = "Holčička s bambulí" if story == 5 and not s_betka else "Bětka"
	C.get_character("Verka").description = "Paní Věrka" if story >= 4 else "Paní s kloboukem"
	for who in [["Tonda", "Tonda"], ["Babicka", "Babička"], ["Deda", "Děda"]]:
		C.get_character(who[0]).description = who[1]


func continue_episode(number: int) -> void:
	_reset_progress()
	G.show_interface()
	E.load_game(number)


func go_to_menu() -> void:
	if not G.is_blocked or game_finished:
		save_now()
	story = 0
	sister().stop_following_character()
	I.deselect_active()
	I.clean_inventory(true)
	R.goto_room("Menu")


func _reset_progress() -> void:
	var fresh: Node = get_script().new()
	for prop in get_script().get_script_property_list():
		if prop.usage & PROPERTY_USAGE_SCRIPT_VARIABLE:
			set(prop.name, fresh.get(prop.name))
	fresh.free()
	I.clean_inventory(true)
	InGameMenu.history.clear()
	for item_name in PopochiuConfig.get_inventory_items_on_start():
		I.get_item_instance(item_name).add(false)
	for room_path in PopochiuResources.get_section("rooms"):
		var room_state: PopochiuRoomData = load(room_path)
		if R.current and R.current.state == room_state:
			continue
		for children in PopochiuResources.ROOM_CHILDREN:
			(room_state.get(children) as Dictionary).clear()
		room_state.characters.clear()
		room_state.visited = false
		room_state.visited_times = 0
		room_state.visited_first_time = false
	R.store_states()
	for chr in C._characters.values():
		if is_instance_valid(chr) and not chr.is_inside_tree():
			chr.queue_free()
	C._characters.clear()
	C.player = C.get_character("Alica")


## After loading, put the sister next to the player (the room placed her by the entry door).
func _on_game_loaded(_data: Dictionary) -> void:
	# JSON loads every number as a float: put the int flags back
	for prop in get_script().get_script_property_list():
		if prop.usage & PROPERTY_USAGE_SCRIPT_VARIABLE and prop.type == TYPE_INT:
			set(prop.name, int(get(prop.name)))
	dress()
	var other := sister()
	if is_instance_valid(R.current) and R.current.has_character(other.script_name) and other.follow_character != "":
		other.position = C.player.position + Vector2(-170, 10)
