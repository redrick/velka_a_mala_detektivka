extends "res://game/minigames/minigame_base.gd"
## Put everyone in the right place by the picture rules (a small logic grid). A story's puzzle extends this
## and returns its data from _puzzle(). Rule cards sit on top, the places in the middle, the things to place
## in a tray at the bottom. Click a thing, then a place (a taken place sends its thing back to the tray);
## click a placed thing to take it back. A rule card turns green when it holds and red when it is broken;
## clicking a card reads the rule out. Arrows + Enter: pick the next thing / place.
##
## _puzzle() keys: title, task, mode ("row": the places stand in a line, so "next to" and "before" make
## sense; "pairs": each thing belongs to one owner), levels. A level: slots [[id, picture, label]],
## items [[id, picture, name]], rules [[kind, a, b, text]], win (the cheer).
## Rule kinds: is (item a in slot b), not, next (items a and b side by side), apart (not side by side),
## before (a somewhere left of b), end (a at either end of the row; b unused).
## tools/check_levels.py checks every level has exactly one answer.

const SYMBOL := {"is": "rule_is", "not": "rule_not", "next": "rule_next", "apart": "rule_apart",
	"before": "rule_before", "end": "rule_end"}
const COLS := 15
const OK := Color(0.45, 0.85, 0.45, 0.35)
const BAD := Color(0.95, 0.3, 0.3, 0.35)

var _lv: Dictionary
var _at := {}            # item id -> slot index (-1 = in the tray)
var _item_nodes := {}    # item id -> TextureRect
var _cards: Array = []   # [ColorRect, rule]
var _card_cells := {}    # Vector2i -> rule index
var _slot_cells := {}    # Vector2i -> slot index
var _tray_cells := {}    # Vector2i -> item id
var _tray_pos := {}      # item id -> Vector2i
var _slot_pos: Array = []
var _sel := ""
var _sel_frame: Panel
var _hint_frame: Panel
var _history: Array = []
var _won := false


func _puzzle() -> Dictionary: return {}
func _title() -> String: return tr(_puzzle().get("title", ""))
func _task_text() -> String: return tr(_puzzle().get("task", ""))
func _levels() -> int: return _puzzle().levels.size()


func _build(i: int) -> void:
	tile = 100.0
	_lv = _puzzle().levels[i]
	_at.clear(); _item_nodes.clear(); _cards.clear(); _card_cells.clear(); _slot_cells.clear()
	_tray_cells.clear(); _tray_pos.clear(); _slot_pos.clear(); _history.clear()
	_sel = ""
	_won = false
	var rules: Array = _lv.rules
	var rule_rows := int(ceil(rules.size() / 4.0))
	set_board_size(COLS, rule_rows + 5)
	for k in rules.size():
		var r: Array = rules[k]
		var at := Vector2i((k % 4) * 4, k / 4)
		var card := ColorRect.new()
		card.color = Color(1, 1, 1, 0.0)
		card.position = cell_pos(at) + Vector2(-4, 4)
		card.size = Vector2(tile * 3 + 8, tile - 8)
		card.mouse_filter = Control.MOUSE_FILTER_IGNORE
		board.add_child(card)
		_cards.append([card, r])
		piece(_tex_of(r[1]), at, 1)
		piece(SYMBOL[r[0]], at + Vector2i(1, 0), 1)
		if r[0] != "end":
			piece(_tex_of(r[2]), at + Vector2i(2, 0), 1)
		for dx in 3:
			_card_cells[at + Vector2i(dx, 0)] = k
	var slots: Array = _lv.slots
	var sy := rule_rows + 1
	var x0 := int((COLS - (slots.size() * 2 - 1)) / 2)
	for k in slots.size():
		var c := Vector2i(x0 + k * 2, sy)
		_slot_pos.append(c)
		var s: Array = slots[k]
		if s[1] != "":
			piece(s[1], c, 1)
		else:
			var l := Kit.title(tr(s[2]), 64)
			l.position = cell_pos(c)
			l.size = Vector2(tile, tile)
			board.add_child(l)
		piece("rule_slot", c + Vector2i(0, 1), 0)
		_slot_cells[c] = k
		_slot_cells[c + Vector2i(0, 1)] = k
	var items: Array = _lv.items
	var ix := int((COLS - (items.size() * 2 - 1)) / 2)
	for k in items.size():
		var it: Array = items[k]
		var c := Vector2i(ix + k * 2, sy + 3)
		_tray_pos[it[0]] = c
		_at[it[0]] = -1
		_item_nodes[it[0]] = piece(it[1], c, 3)
	_sel_frame = frame()
	_sel_frame.hide()
	_hint_frame = frame(Color("4dabf7"))
	_hint_frame.hide()
	_update()


func _tex_of(id: String) -> String:
	for it in _lv.items:
		if it[0] == id:
			return it[1]
	for s in _lv.slots:
		if s[0] == id:
			return s[1]
	return id


func _name_of(id: String) -> String:
	for it in _lv.items:
		if it[0] == id:
			return it[2]
	return id


func _slot_index(id: String) -> int:
	for k in _lv.slots.size():
		if _lv.slots[k][0] == id:
			return k
	return -1


## "ok", "bad" or "" (not everyone in the rule is placed yet).
func _state(r: Array, at: Dictionary) -> String:
	var a: int = at.get(r[1], -1)
	if a < 0:
		return ""
	var n: int = _lv.slots.size()
	match r[0]:
		"is": return "ok" if a == _slot_index(r[2]) else "bad"
		"not": return "bad" if a == _slot_index(r[2]) else "ok"
		"end": return "ok" if a == 0 or a == n - 1 else "bad"
	var b: int = at.get(r[2], -1)
	if b < 0:
		return ""
	match r[0]:
		"next": return "ok" if absi(a - b) == 1 else "bad"
		"apart": return "ok" if absi(a - b) != 1 else "bad"
		"before": return "ok" if a < b else "bad"
	return ""


func _update() -> void:
	_tray_cells.clear()
	for id in _at:
		var c: Vector2i = _tray_pos[id] if _at[id] < 0 else _slot_pos[_at[id]] + Vector2i(0, 1)
		_item_nodes[id].position = cell_pos(c)
		if _at[id] < 0:
			_tray_cells[c] = id
	var all_ok := true
	for card in _cards:
		var st := _state(card[1], _at)
		(card[0] as ColorRect).color = OK if st == "ok" else BAD if st == "bad" else Color(1, 1, 1, 0)
		all_ok = all_ok and st == "ok"
	if _sel != "":
		_sel_frame.position = _item_nodes[_sel].position
		_sel_frame.show()
	else:
		_sel_frame.hide()
	var placed := true
	for id in _at:
		placed = placed and _at[id] >= 0
	if placed and all_ok and not _won:
		_won = true
		_sel_frame.hide()
		level_done(_lv.win)


func _occupant(slot: int) -> String:
	for id in _at:
		if _at[id] == slot:
			return id
	return ""


func _cell(c: Vector2i) -> void:
	if _won:
		return
	_hint_frame.hide()
	if _card_cells.has(c):
		say(_cards[_card_cells[c]][1][3])
		return
	if _tray_cells.has(c):
		_sel = _tray_cells[c]
		say(_name_of(_sel))
		_update()
		return
	if _slot_cells.has(c):
		var slot: int = _slot_cells[c]
		var there := _occupant(slot)
		if _sel == "":
			if there != "":
				_move(there, -1)
			return
		if there != "" and there != _sel:
			_history.append([there, _at[there]])
			_at[there] = -1
		_move(_sel, slot)
		_sel = ""
		_update()


func _move(id: String, slot: int) -> void:
	_history.append([id, _at[id]])
	_at[id] = slot
	say("")
	_update()


func _targets() -> Array:
	var out := []
	for id in _at:
		if _at[id] < 0:
			out.append(_tray_pos[id])
	for p in _slot_pos:
		out.append(p + Vector2i(0, 1))
	return out


func _dir(d: Vector2i) -> void:
	var t := _targets()
	var cur := Vector2i(-1, -1)
	if _sel != "" and _at[_sel] < 0:
		cur = _tray_pos[_sel]
	var k := t.find(cur)
	k = posmod(k + (1 if d.x >= 0 and d.y >= 0 else -1), t.size())
	var c: Vector2i = t[k]
	if _tray_cells.has(c):
		_cell(c)
	else:
		_hint_frame.position = cell_pos(c)
		_hint_frame.show()


func _action() -> void:
	if _hint_frame.visible:
		_cell(Vector2i(_hint_frame.position / tile))


func _undo() -> void:
	if _history.is_empty() or _won:
		return
	var h: Array = _history.pop_back()
	_at[h[0]] = h[1]
	_sel = ""
	_update()


## The one answer: item id -> slot index (the levels are small, so try every order).
func _solve() -> Dictionary:
	var ids: Array = []
	for it in _lv.items:
		ids.append(it[0])
	var found := {}
	_search(ids, 0, {}, found)
	return found


func _search(ids: Array, k: int, at: Dictionary, found: Dictionary) -> bool:
	for r in _lv.rules:
		if _state(r, at) == "bad":
			return false
	if k == ids.size():
		found.merge(at)
		return true
	var used := at.values()
	for s in _lv.slots.size():
		if s in used:
			continue
		at[ids[k]] = s
		if _search(ids, k + 1, at, found):
			return true
		at.erase(ids[k])
	return false


func _hint() -> void:
	var sol := _solve()
	for id in sol:
		if _at[id] != sol[id]:
			if _at[id] >= 0:
				_move(id, -1)
			_sel = id
			_update()
			_hint_frame.position = cell_pos(_slot_pos[sol[id]] + Vector2i(0, 1))
			_hint_frame.show()
			say("Čmuch! Tohle patří sem.")
			return


func solve_for_test() -> void:
	var sol := _solve()
	for id in _at.keys():
		_at[id] = -1
	for id in sol:
		_at[id] = sol[id]
	_update()
	await get_tree().process_frame
