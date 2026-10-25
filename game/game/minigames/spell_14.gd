extends "res://game/minigames/spell.gd"
## Story 14 "Jméno pro kavku": Alica writes the jackdaw's name on Bětka's drawing. Á is not A!


func _data() -> Dictionary:
	return {
		"title": "Jméno pro kavku",
		"task": "Napiš jméno pod Bětčin obrázek. Pozor: Á s čárkou je jiné písmeno než A!",
		"levels": [
			{"word": "KÁJA", "extra": "AŽ", "picture": "who_kavka14", "win": "Kavka Kája!"},
			{"word": "KAVKA", "extra": "ÁH", "picture": "who_kavka14", "win": "Kája je kavka. KAVKA!"},
		],
	}
