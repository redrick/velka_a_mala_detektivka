@tool
extends PopochiuCharacter
## Base for every character: swaps between the exported PNG frames
## (assets/characters/<sprite_prefix>_<mood>.png) to walk, talk and hold poses, and adds a small bob.

const CHAR_DIR := "res://assets/characters/"
const WALK_FPS := 6.0
const TALK_FPS := 7.0

@export var sprite_prefix := ""
@export var default_mood := "happy"

var _mood := ""
var _state := "idle"
var _t := 0.0
var _frames := {}


class _Ticker extends Node:
	var target: Node

	func _process(delta: float) -> void:
		target._tick(delta)


func _ready() -> void:
	super()
	if Engine.is_editor_hint() or sprite_prefix.is_empty():
		return
	_mood = default_mood
	_show(_mood)
	var ticker := _Ticker.new()
	ticker.target = self
	add_child(ticker)


func _tick(delta: float) -> void:
	_t += delta
	var sprite: Sprite2D = $Sprite2D
	match _state:
		"walk":
			var step := int(_t * WALK_FPS) % 2 == 0
			_show("walk" if step and _has("walk") else _mood)
			sprite.position.y = -absf(sin(_t * WALK_FPS * PI)) * 10.0
			sprite.scale.y = 1.0
		"talk":
			var open := int(_t * TALK_FPS) % 2 == 0
			_show("talk" if open and _mood == default_mood and _has("talk") else _mood)
			sprite.position.y = 0.0
			sprite.scale.y = 1.0 + sin(_t * 18.0) * 0.012
		_:
			sprite.position.y = 0.0
			sprite.scale.y = 1.0 + sin(_t * 2.4) * 0.008


## Lines are written in Czech in the scripts; this shows them in the current language.
func say(dialog: String, emo := EMPTY_STRING) -> void:
	InGameMenu.remember(self, dialog)
	await super(tr(dialog), emo)


## Holds a pose (a mood/arm variant such as "lens", "point", "sleepy"); no argument = default.
func pose(mood := "") -> void:
	_mood = default_mood if mood.is_empty() else mood
	_show(_mood)


func _play_idle() -> void:
	_state = "idle"
	_show(_mood)


func _play_walk(_target_pos: Vector2) -> void:
	if _state != "walk":
		_t = 0.0
	_state = "walk"


func _play_talk() -> void:
	if _state != "talk":
		_t = 0.0
	_state = "talk"


func _has(mood: String) -> bool:
	return _texture(mood) != null


func _show(mood: String) -> void:
	var tex := _texture(mood)
	if tex and $Sprite2D.texture != tex:
		$Sprite2D.texture = tex


func _texture(mood: String) -> Texture2D:
	if sprite_prefix.is_empty():
		return null
	if not _frames.has(mood):
		var path := CHAR_DIR + "%s_%s.png" % [sprite_prefix, mood]
		_frames[mood] = load(path) if ResourceLoader.exists(path) else null
	return _frames[mood]
