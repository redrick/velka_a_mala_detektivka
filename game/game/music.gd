extends Node
## Quiet background music that crossfades by mood: "menu", "day" (cozy) and "night" (the dark attic,
## the shed, the night garden, dawn at the pond, the evening kitchen). A room's mood is its "mood"
## meta (the dark() / light_up() helpers set it); rooms without one play "day", the menu "menu".
## Each mood is a playlist that moves on to the next track when one ends.
## Tracks: Kevin MacLeod (incompetech.com), CC BY 4.0 — credited in the settings screen.

const DIR := "res://assets/music/"
const PLAYLISTS := {
	"menu": ["carefree"],
	"day": ["wallpaper", "somewhere_sunny", "easy_lemon"],
	"night": ["dreamer", "frost_waltz"],
}
const VOLUME_DB := {"off": -80.0, "quiet": -24.0, "normal": -15.0}
const FADE := 2.0

var _players: Array[AudioStreamPlayer] = []
var _now := 0
var _mood := ""
var _track := 0
var _room_id := 0


func _ready() -> void:
	process_mode = Node.PROCESS_MODE_ALWAYS
	for i in 2:
		var p := AudioStreamPlayer.new()
		p.volume_db = -80.0
		p.finished.connect(_next_track.bind(p))
		add_child(p)
		_players.append(p)
	Prefs.changed.connect(_apply_volume)


func _process(_delta: float) -> void:
	if not E.in_room or not is_instance_valid(R.current):
		return
	if R.current.get_instance_id() == _room_id:
		return
	_room_id = R.current.get_instance_id()
	var fallback := "menu" if R.current.script_name == "Menu" else "day"
	play(R.current.get_meta("mood", fallback))


## Switch to a mood (no change if it's already playing).
func play(mood: String) -> void:
	if mood == _mood or not PLAYLISTS.has(mood):
		return
	_mood = mood
	_track = 0
	_crossfade()


func _crossfade() -> void:
	var old := _players[_now]
	_now = 1 - _now
	var new := _players[_now]
	new.stream = load(DIR + PLAYLISTS[_mood][_track] + ".ogg")
	new.volume_db = -80.0
	new.play()
	var tw := create_tween().set_parallel()
	tw.tween_property(new, "volume_db", _target_db(), FADE)
	if old.playing:
		tw.tween_property(old, "volume_db", -80.0, FADE)
		tw.chain().tween_callback(old.stop)


func _next_track(p: AudioStreamPlayer) -> void:
	if p != _players[_now]:
		return
	_track = (_track + 1) % PLAYLISTS[_mood].size()
	_crossfade()


func _target_db() -> float:
	return VOLUME_DB.get(Prefs.music, VOLUME_DB.quiet)


func _apply_volume() -> void:
	var p := _players[_now]
	if p.playing:
		create_tween().tween_property(p, "volume_db", _target_db(), 0.5)
