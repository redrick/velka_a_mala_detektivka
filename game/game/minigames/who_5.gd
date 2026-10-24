extends "res://game/minigames/whodunit.gd"
## Story 5: who builds the snowmen?


func _case() -> Dictionary:
	return {
		"title": "Kdo staví sněhuláky?",
		"task": "Malé stopy s hvězdičkami, bílý nos z pastináku, červená vlnka z bambule a malé botičky u Franty. Kdo to je?",
		"hint": "Čmuch čmuch! Botičky s hvězdičkami schly u Franty na kamnech.",
		"win": "Někdo malý s červenou bambulí. Bydlí u Franty! A stydí se zaklepat.",
		"culprit": "pompom",
		"clues": ["clue_starprint", "clue_parsnip", "clue_thread", "clue_boots"],
		"suspects": [
			["tonda", "Tonda", "who_tonda5", "Tonda má velké boty bez hvězdiček. A modrou čepici bez bambule."],
			["babicka", "Babička", "who_babicka5", "Babička má mokré rukavice od těsta. A mrkve má všechny."],
			["joey", "Joey", "who_joey5", "Joey má tlapky, ne botičky. A sněhuláka by nepostavil!"],
			["pompom", "Někdo s bambulí", "who_pompom", ""],
		],
	}
