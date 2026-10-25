extends "res://tests/story_test.gd"
## Blind play: an explorer that doesn't know the solution. In every room it tries what a child could
## do (click props and hotspots, click people and the sister, use every item on everything, pick
## every answer on a choose() card), prefers what it hasn't tried yet in this state, and walks back
## to states with untried actions. Fails with ROADBLOCK when nothing untried is reachable before the
## story ends. Also checks what it sees: clickables off screen, covered, unreachable or nameless.
## Run through tools/blind_play.sh (own copy of the project, own user data).
##   -- --test=res://tests/blind.gd --story=4 --seed=1 [--tries=2] [--max=4000] [--right] [--crash=3 | --resume]

const LAST_STORY := 16

var story := 0
var rng := RandomNumberGenerator.new()
var tries_per := 2
var max_actions := 4000
var right_clicks := false
var tries := {}        # fp -> {action: count}
var actions_of := {}   # fp -> [action, ...]
var trans := {}        # fp -> {action: fp}
var seen := {}
var progress_by := {}  # action kind -> times it led to a new state
var notes := {}        # message -> room/target it is about
var needed := {}       # room/target whose action changed the story state
var choice_tries := {}
var resumes_at := []
var n_actions := 0
var wander := 0
var hot_family := ""
var hot_next := ""
var crash_at := 0      # quit (after a save, like closing the window) at the n-th chance in a running chain
var chances := 0       # chains that changed the state and were still running
var resume := false
var n_progress := 0
var cur_fp := ""
var _choosing := false


func run() -> void:
	for a in OS.get_cmdline_user_args():
		if a.begins_with("--story="): story = int(a.substr(8))
		elif a.begins_with("--seed="): rng.seed = int(a.substr(7))
		elif a.begins_with("--tries="): tries_per = int(a.substr(8))
		elif a.begins_with("--max="): max_actions = int(a.substr(6))
		elif a == "--right": right_clicks = true
		elif a.begins_with("--crash="): crash_at = int(a.substr(8))
		elif a == "--resume": resume = true
	Engine.time_scale = 8.0
	var start_room := _start_room(story)
	if start_room == "":
		check(false, "story %d has no start_room" % story)
		return
	resumes_at = [] if crash_at > 0 or resume else [rng.randi_range(3, 15), rng.randi_range(16, 40)]
	var t0 := Time.get_ticks_msec()
	if resume:
		check(Globals.has_save(story), "a save to continue")
		Globals.continue_episode(story)
		while not (E.in_room and is_instance_valid(R.current) and R.current.script_name != "Menu"):
			await get_tree().process_frame
		print("  > continued in ", R.current.script_name)
		await _current_check()
	else:
		await start(start_room, story)
	var stall := 0
	while n_actions < max_actions:
		await _settle()
		if Globals.is_finished(story) or (is_instance_valid(R.current) and R.current.script_name == "Menu"):
			break
		var fp := _fingerprint()
		cur_fp = fp
		var acts := _actions()
		actions_of[fp] = acts.map(func(a): return a.key)
		if not seen.has(fp):
			seen[fp] = true
			n_progress += 1
			_geometry()
			if not resumes_at.is_empty() and n_progress >= resumes_at[0]:
				resumes_at.pop_front()
				await _resume_check()
				continue
		if acts.is_empty():
			check(false, "SOFTLOCK nothing to click in %s | %s" % [R.current.script_name, fp])
			break
		var act: Dictionary = _pick(fp, acts)
		if act.is_empty():
			_roadblock(fp, acts)
			break
		tries[fp][act.key] = tries[fp].get(act.key, 0) + 1
		n_actions += 1
		print("  > %s: %s" % [R.current.script_name, act.key])
		var flags_before := str(_state_dict())
		var where: String = R.current.script_name + "/" + (act.node.script_name if act.has("node") else "")
		await _do(act, flags_before)
		await _settle()
		if str(_state_dict()) != flags_before:
			needed[where] = true
		if Globals.is_finished(story) or (is_instance_valid(R.current) and R.current.script_name == "Menu"):
			break
		var after := _fingerprint()
		if not trans.has(fp): trans[fp] = {}
		trans[fp].get_or_add(act.key, {})[after] = true
		if after != fp:
			var a_parts := fp.split("|")
			var changed := Array(after.split("|")).filter(func(x): return not x in a_parts)
			print("    = ", " ".join(changed).left(300))
		if after != fp and not seen.has(after):
			hot_family = _family(act.key)
			hot_next = hot_family + str(int(act.key.substr(hot_family.length())) + 1) if hot_family != "" else ""
			progress_by[act.kind] = progress_by.get(act.kind, 0) + 1
			stall = 0
			wander = 0
		else:
			stall += 1
		if stall > 600:
			_roadblock(fp, acts)
			break
	var secs := (Time.get_ticks_msec() - t0) / 1000.0
	check(Globals.is_finished(story), "story %d finished blind" % story)
	print("BLIND story=%d seed=%d finished=%s actions=%d states=%d secs=%.0f progress_by=%s chances=%d%s" % [
		story, rng.seed, Globals.is_finished(story), n_actions, seen.size(), secs, progress_by, chances, " resumed" if resume else ""])
	for n in notes:
		var target: String = notes[n]
		print("BLIND %s %s" % ["NEEDED" if needed.has(target) else "note", n])


func _start_room(n: int) -> String:
	var data = JSON.parse_string(FileAccess.get_file_as_string("res://game/menu/series.json"))
	for s in data.series:
		for e in s.episodes:
			if int(e.number) == n:
				return e.get("start_room", "")
	return ""


#region State #######################################################################################
func _fingerprint() -> String:
	var parts := []
	for p in Globals.get_script().get_script_property_list():
		if p.usage & PROPERTY_USAGE_SCRIPT_VARIABLE:
			parts.append("%s=%s" % [p.name, Globals.get(p.name)])
	if is_instance_valid(R.current):
		parts.append("room=" + R.current.script_name)
		for p in R.current.get_script().get_script_property_list():
			if p.usage & PROPERTY_USAGE_SCRIPT_VARIABLE and p.type in [TYPE_BOOL, TYPE_INT, TYPE_STRING]:
				parts.append("r.%s=%s" % [p.name, R.current.get(p.name)])
		var vis := []
		for n in _clickables():
			vis.append(n.script_name)
		vis.sort()
		parts.append("vis=" + ",".join(vis))
	var inv: Array = I.items.duplicate()
	inv.sort()
	parts.append("inv=" + ",".join(inv))
	parts.append("player=" + C.player.script_name)
	return "|".join(parts)


func _state_dict() -> Dictionary:
	var d := {}
	for p in Globals.get_script().get_script_property_list():
		if p.usage & PROPERTY_USAGE_SCRIPT_VARIABLE:
			d[p.name] = Globals.get(p.name)
	d["inv"] = I.items.duplicate()
	return d


## What the real mouse can reach: shown, clickable, and listening (a clickable that started with
## clickable = false never connected its mouse signals, so it can't be hovered later).
func _clickables() -> Array:
	var out := []
	if not is_instance_valid(R.current):
		return out
	for n in R.current.get_props() + R.current.get_hotspots() + R.current.get_characters():
		if not is_instance_valid(n) or not n.is_visible_in_tree() or not n.clickable:
			continue
		if n is PopochiuCharacter and n == C.player:
			continue
		if not n.mouse_entered.is_connected(n._on_mouse_entered):
			_note("clickable but deaf (started unclickable): %s/%s" % [R.current.script_name, n.script_name])
			continue
		out.append(n)
	return out


func _actions() -> Array:
	var out := []
	var targets := _clickables()
	for n in targets:
		out.append({key = "click " + n.script_name, kind = "click", node = n})
		if right_clicks:
			out.append({key = "look " + n.script_name, kind = "look", node = n})
	for item_name in I.items:
		var item: PopochiuInventoryItem = I.get_item_instance(item_name)
		for n in targets:
			out.append({key = "use %s on %s" % [item_name, n.script_name], kind = "item", node = n, item = item})
		out.append({key = "click item " + item_name, kind = "item_click", item = item})
	return out


func _pick(fp: String, acts: Array) -> Dictionary:
	if not tries.has(fp): tries[fp] = {}
	var open := acts.filter(func(a): return tries[fp].get(a.key, 0) < _limit(a.key))
	if not open.is_empty():
		# clicks before item uses: a child clicks first
		var plain := open.filter(func(a): return a.kind == "click")
		if not plain.is_empty() and rng.randf() < 0.85:
			open = plain
		# what just worked: try its siblings next (Prkno1 -> Prkno2, Kamen1 -> Kamen2)
		var kin := open.filter(func(a): return _family(a.key) == hot_family)
		if hot_family != "" and not kin.is_empty() and rng.randf() < 0.9:
			open = kin
			var next := open.filter(func(a): return a.key == hot_next)
			if not next.is_empty() and rng.randf() < 0.8:
				return next[0]
		var low := 1 << 30
		for a in open:
			low = mini(low, tries[fp].get(a.key, 0))
		open = open.filter(func(a): return tries[fp].get(a.key, 0) == low)
		return open[rng.randi() % open.size()]
	var key := _path_to_untried(fp)
	for a in acts:
		if a.key == key:
			return a
	# outcomes can depend on things the fingerprint doesn't see: wander a while before giving up
	wander += 1
	if wander < 300:
		return acts[rng.randi() % acts.size()]
	return {}


func _family(key: String) -> String:
	var re := RegEx.create_from_string("\\d+$")
	return re.sub(key, "") if re.search(key) else ""


## Using an item mostly does what a click does: one try per state is enough.
func _limit(key: String) -> int:
	return 1 if key.begins_with("use ") or key.begins_with("click item ") else tries_per


## BFS over seen transitions to a state that still has untried actions; returns the first action.
func _path_to_untried(from: String) -> String:
	var first := {from: ""}
	var queue := [from]
	while not queue.is_empty():
		var fp: String = queue.pop_front()
		if fp != from:
			for k in actions_of.get(fp, []):
				if tries.get(fp, {}).get(k, 0) < _limit(k):
					return first[fp]
		for k in trans.get(fp, {}):
			for nxt in trans[fp][k]:
				if not first.has(nxt):
					first[nxt] = k if fp == from else first[fp]
					queue.append(nxt)
	return ""


func _roadblock(fp: String, acts: Array) -> void:
	check(false, "ROADBLOCK in %s after %d actions" % [R.current.script_name, n_actions])
	print("BLIND ROADBLOCK story=%d room=%s" % [story, R.current.script_name])
	print("  state: ", fp)
	print("  actions: ", acts.map(func(a): return a.key))


func _note(msg: String, target := "") -> void:
	if not notes.has(msg):
		notes[msg] = target
		print("  note: ", msg)
#endregion


#region Acting ######################################################################################
func _do(act: Dictionary, flags_before := "") -> void:
	var done := [false]
	var f := func():
		match act.kind:
			"click":
				E.clicked = act.node
				act.node.last_click_button = MOUSE_BUTTON_LEFT
				await act.node._on_click()
			"look":
				E.clicked = act.node
				act.node.last_click_button = MOUSE_BUTTON_RIGHT
				await act.node._on_right_click()
			"item":
				I.active = act.item
				E.clicked = act.node
				act.node.last_click_button = MOUSE_BUTTON_LEFT
				await act.node._on_item_used(act.item)
				if is_instance_valid(act.item): I.active = null
			"item_click":
				I.clicked = act.item
				act.item.last_click_button = MOUSE_BUTTON_LEFT
				await act.item._on_click()
				I.clicked = null
				I.active = null
		done[0] = true
	var room_id := R.current.get_instance_id()
	f.call()
	var counted := false
	var moved := false
	var t := 0.0
	while not done[0] and t < 240.0:
		await get_tree().process_frame
		_answer_cards()
		_talk_check(act.key)
		t += get_process_delta_time()
		if is_instance_valid(R.current) and R.current.get_instance_id() != room_id and E.in_room and not _busy():
			moved = true
			break
		if crash_at > 0 and not counted and str(_state_dict()) != flags_before:
			counted = true
			chances += 1
			if chances == crash_at:
				await get_tree().create_timer(rng.randf_range(0.0, 0.4)).timeout
				if not done[0]:
					Globals.save_now()
					print("BLIND CRASH story=%d chance=%d during '%s' in %s" % [story, chances, act.key, R.current.script_name])
					get_tree().quit(3)
					await get_tree().create_timer(60.0).timeout
	if not done[0] and not moved:
		check(false, "HANG %s in %s (%s)" % [act.key, R.current.script_name if is_instance_valid(R.current) else "?", _why()])


## Waits until nothing talks, walks or blocks; answers choose() cards on the way.
func _settle() -> void:
	var calm := 0.0
	var t := 0.0
	var blocked := 0.0
	while calm < 0.8 and t < 400.0:
		await get_tree().process_frame
		var dt := get_process_delta_time()
		t += dt
		_answer_cards()
		var busy := _busy()
		if not busy and G.is_blocked:
			blocked += dt
			if blocked > 60.0:
				check(false, "SOFTLOCK gui blocked with nothing happening in " + R.current.script_name)
				G.unblock()
				blocked = 0.0
		else:
			blocked = 0.0
		calm = 0.0 if busy or G.is_blocked else calm + dt
	if t >= 400.0:
		check(false, "idle timeout: " + _why())


func _answer_cards() -> void:
	if _choosing or not is_instance_valid(R.current):
		return
	for layer in R.current.get_children():
		if not (layer is CanvasLayer and layer.layer == 40):
			continue
		var buttons := layer.find_children("*", "Button", true, false)
		if buttons.is_empty():
			continue
		_choosing = true
		var title := ""
		for l in layer.find_children("*", "Label", true, false):
			title = l.text
			break
		var key := cur_fp + "#" + title
		var counts: Dictionary = choice_tries.get_or_add(key, {})
		var low := 1 << 30
		for i in buttons.size():
			low = mini(low, counts.get(i, 0))
		var pick := []
		for i in buttons.size():
			if counts.get(i, 0) == low: pick.append(i)
		var i: int = pick[rng.randi() % pick.size()]
		counts[i] = counts.get(i, 0) + 1
		print("  > choose '%s': %s" % [title, buttons[i].text])
		_press.call_deferred(buttons[i])
		return


func _press(b: Button) -> void:
	await get_tree().create_timer(0.2).timeout
	if is_instance_valid(b):
		b.pressed.emit()
	_choosing = false


## A line said by someone who isn't in the room: when it ends, Popochiu's idle() has no tree, the
## say() coroutine dies with an error and whatever awaited it never goes on.
func _talk_check(during: String) -> void:
	for chr in C._characters.values():
		if is_instance_valid(chr) and chr.is_talking and not chr.is_inside_tree():
			_note("%s talks outside the room (%s, during '%s')" % [chr.script_name, R.current.script_name, during])


## After loading, Popochiu makes the room current (floor clicks walk, its cutscene plays) only once the
## GUI has sent load_feedback_finished.
func _current_check() -> void:
	var t := 0.0
	while not R.current.is_current and t < 20.0:
		await get_tree().process_frame
		t += get_process_delta_time()
	check(R.current.is_current, "continued room %s is current" % R.current.script_name)


func _resume_check() -> void:
	var room: String = R.current.script_name
	var before := _state_dict()
	print("  > save + continue in ", room)
	await save_and_continue(story, room)
	await _current_check()
	await _settle()
	var after := _state_dict()
	for k in before:
		var a = before[k]
		var b = after.get(k)
		if k == "inv":
			for it in a:
				if not it in b: check(false, "resume lost item " + it)
		elif typeof(a) == TYPE_BOOL and a and not b:
			check(false, "resume lost flag " + k)
		elif typeof(a) == TYPE_INT and int(b) < a:
			check(false, "resume lowered %s %d -> %d" % [k, a, b])
#endregion


#region Geometry ####################################################################################
const SCREEN := Rect2(0, 0, 1920, 1080)


func _poly(n: Node) -> PackedVector2Array:
	var ip := n.get_node_or_null("InteractionPolygon")
	if ip == null or ip.polygon.is_empty():
		return PackedVector2Array()
	return ip.global_transform * ip.polygon


func _geometry() -> void:
	var room: String = R.current.script_name
	var targets := _clickables()
	var polys := {}
	for n in targets:
		polys[n] = _poly(n)
	for n in targets:
		var where := "%s/%s" % [room, n.script_name]
		if str(n.description).strip_edges() == "":
			_note("no hover name: " + where, where)
		var poly: PackedVector2Array = polys[n]
		if poly.is_empty():
			_note("no interaction polygon: " + where, where)
			continue
		var box := _bounds(poly)
		var pts := _samples(poly, box)
		if pts.is_empty():
			_note("polygon too thin to hit: " + where, where)
			continue
		var on := pts.filter(func(p): return SCREEN.has_point(p) and not _under_gui(p))
		if on.size() < maxi(1, pts.size() / 5):
			_note("mostly off screen / under GUI: %s %s" % [where, box], where)
		var free := 0
		var over := {}
		for p in on:
			var hit := false
			for o in targets:
				if o == n or (o is PopochiuCharacter and o.script_name in ["Joey", "Alica", "Hanka"]):
					continue
				if Geometry2D.is_point_in_polygon(p, polys[o]) and Globals.click_area(o) < Globals.click_area(n):
					hit = true
					over[o.script_name] = true
			if not hit: free += 1
		if not on.is_empty() and free == 0:
			_note("fully overlapped: %s by %s" % [where, over.keys()], where)
		if not n is PopochiuCharacter and n.walk_to_point != Vector2.ZERO:
			var w: Vector2 = n.to_global(n.walk_to_point)
			var d := _walk_distance(w)
			if d > 500.0:
				_note("walk_to %.0f px outside walkable: %s %s" % [d, where, w], where)


func _bounds(poly: PackedVector2Array) -> Rect2:
	var r := Rect2(poly[0], Vector2.ZERO)
	for p in poly: r = r.expand(p)
	return r


func _samples(poly: PackedVector2Array, box: Rect2) -> Array:
	var out := []
	for i in 12:
		for j in 12:
			var p := box.position + box.size * Vector2((i + 0.5) / 12.0, (j + 0.5) / 12.0)
			if Geometry2D.is_point_in_polygon(p, poly): out.append(p)
	return out


func _walk_distance(p: Vector2) -> float:
	var best := INF
	for wa in R.current.get_walkable_areas():
		var region: NavigationRegion2D = wa.get_node_or_null("Perimeter")
		if region == null or region.navigation_polygon == null:
			continue
		var np := region.navigation_polygon
		var outlines := []
		for i in np.get_outline_count():
			outlines.append(np.get_outline(i))
		var verts := np.get_vertices()
		for i in np.get_polygon_count():
			var pl := PackedVector2Array()
			for k in np.get_polygon(i): pl.append(verts[k])
			outlines.append(pl)
		for o in outlines:
			var outline: PackedVector2Array = region.global_transform * (o as PackedVector2Array)
			if Geometry2D.is_point_in_polygon(p, outline):
				return 0.0
			for k in outline.size():
				var c := Geometry2D.get_closest_point_to_segment(p, outline[k], outline[(k + 1) % outline.size()])
				best = minf(best, p.distance_to(c))
	return best


## The bottom-left house button and the top bar, laid out for a 1920x1080 screen (headless runs
## have a square viewport, so the GUI's own rects can't be trusted).
func _under_gui(p: Vector2) -> bool:
	return Rect2(10, 970, 100, 100).has_point(p) or Rect2(0, 0, 1920, 70).has_point(p)
#endregion
