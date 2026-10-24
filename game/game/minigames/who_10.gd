extends "res://game/minigames/whodunit.gd"
## Story 10: who took Míša and Šiša?


func _case() -> Dictionary:
	return {
		"title": "Kdo vzal Míšu a Šišu?",
		"task": "Velké holínky s vroubky vedou ke srubu. V kotci jsou hobliny. Na papírku je K. A háček na čepici je prázdný.",
		"hint": "Čmuch čmuch! Kdo nosí holínky, má klíč od kumbálu a jmenuje se na K?",
		"win": "Velký Karel, pan školník! Holínky, hobliny z jeho ponku, čepice pryč. A podpis K.",
		"culprit": "skolnik",
		"clues": ["clue_holinka", "clue_shavings", "clue_note10", "clue_hook"],
		"suspects": [
			["jezek", "Ježek", "who_jezek", "Ježek je moc malý. Morče by neodnesl. Nosil jen seno."],
			["karel", "Malý Karel", "who_malykarel", "Malý Karel byl v neděli u babičky. A seno má od králíka."],
			["tata", "Táta", "who_tata10", "Táta nosí boty se čtverečky, ne holínky. A nejmenuje se na K."],
			["liska", "Liška", "who_liska10", "U kotce nejsou žádné liščí stopy. A papírek by liška nenapsala."],
			["skolnik", "Velký Karel", "who_skolnik", ""],
		],
	}
