extends "res://game/minigames/whodunit.gd"
## Story 9: who wrote the coded message? (the Masopust parade)


func _case() -> Dictionary:
	return {
		"title": "Kdo napsal zprávu?",
		"task": "Papírek má zoubky a voní levandulí. Hvězdičky jsou jedním tahem. A kdo umí písmo bez klíče? Ukaž na masku!",
		"hint": "Čmuch čmuch! Babiččiny nůžky stříhají zoubky. Kdo má zoubky na šátku?",
		"win": "Bába s nůší! Na šátku má zoubky, voní levandulí a pod šátkem je drdol.",
		"culprit": "baba",
		"clues": ["clue_zig9", "clue_lavender", "clue_onestar", "clue_db"],
		"suspects": [
			["kobyla", "Kobyla", "who_kobyla", "Kobyla má tenisky a je to Tonda. Tonda písmo neumí přečíst."],
			["kominik", "Kominík", "who_kominik", "Kominík je paní Věrka. Voní moukou a klobouk má rovný kraj."],
			["franta", "Medvědář", "who_franta9", "Pan Franta je medvědář. Hvězdičku na masce nemá."],
			["medved", "Medvěd", "who_medved", "Medvěd je děda. Kreslí hvězdu pěti čarami."],
			["baba", "Bába s nůší", "who_baba", ""],
		],
	}
