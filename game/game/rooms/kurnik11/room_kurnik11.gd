@tool
extends "res://game/shared/story_room.gd"
## Story 11, inside babička's henhouse: nest boxes with táta's wood shavings; Hanka counts seven eggs.

const Data := preload('room_kurnik11_state.gd')

var state: Data = load("res://game/rooms/kurnik11/room_kurnik11.tres")


func _on_room_entered() -> void:
	C.player.position = get_marker_position("Start")
	Globals.bring_sister(self, Vector2(170, 10))
	get_prop("Vajicka").visible = not Globals.v_count
	Globals.exit_arrow(self, "Ven", true)


func joey_goal() -> Vector2:
	return get_hotspot("Hnizda").walk_to_point if not Globals.v_count else get_hotspot("Ven").walk_to_point


func on_click(node: Node) -> void:
	match node.script_name:
		"Hnizda", "Vajicka":
			await C.player.walk(get_hotspot("Hnizda").walk_to_point)
			if Globals.v_count:
				await C.player.say("Hnízda s hoblinami od táty.")
				return
			C.Hanka.pose("point")
			await C.Hanka.say("Jedno, dvě, tři, čtyři, pět, šest… sedm!")
			C.Hanka.pose()
			await C.Alica.say("Osm slepiček a jen sedm vajíček. Zapisuju.")
			await C.Hanka.say("Já vím! Bere je zajíček. Na barvení!")
			await C.Alica.say("Hani, zajíček vajíčka nosí, nebere!")
			get_prop("Vajicka").hide()
			Globals.v_count = true
		"Ven":
			await C.player.walk_to_clicked()
			R.goto_room("Dvur11")
		_: await super(node)
