extends "res://game/minigames/whodunit.gd"
## Story 4: who walked Franta's trail ahead of Hanka?


func _case() -> Dictionary:
	return {
		"title": "Kdo šel po stopě před Hankou?",
		"task": "U kurníku i u Boty byly obří stopy s cikcak podrážkou. A nový dopis. Kdo to byl?",
		"hint": "Čmuch čmuch! U Boty ležel splávek. Kdo chodí s udicí?",
		"win": "Pan rybář! Obří holinky, splávek… a ve tři se usmál na hodiny.",
		"culprit": "rybar",
		"clues": ["clue_zig", "clue_splavek", "clue_clock3", "clue_letter"],
		"suspects": [
			["kostelnik", "Kostelník", "who_kostelnik", "Kostelník nosí malé galoše. Ty nemají cikcak."],
			["straka", "Straka", "who_straka", "Straka nemá boty! A upustila jen obal od bonbonu."],
			["tonda", "Tonda", "who_tonda4", "Tonda má malé boty. A celou dobu byl s námi."],
			["rybar", "Pan rybář", "who_rybar4", ""],
		],
	}
