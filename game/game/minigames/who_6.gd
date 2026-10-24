extends "res://game/minigames/whodunit.gd"
## Story 6: who takes the stars from the tin?


func _case() -> Dictionary:
	return {
		"title": "Kdo bere hvězdičky?",
		"task": "Z plechovky mizí jen celé hvězdičky s bílou polevou, v noci, v zamčeném domě. Nejdřív 7, potom 2. Kdo to je?",
		"hint": "Čmuch čmuch! Na válenkách bylo jehličí a červená stužka.",
		"win": "Děda! Mokré válenky, jehličí, stužka… a past bez návnady.",
		"culprit": "deda",
		"clues": ["clue_trap", "clue_crumbs", "clue_needles", "clue_photo7"],
		"suspects": [
			["mice", "Myši", "who_mice", "Past nemá návnadu. A myši by okusovaly všechno, ne celé hvězdičky."],
			["joey", "Joey", "who_joey5", "Joey plechovku neotevře. Jen u ní sedí a škemrá."],
			["hanka", "Hanka", "who_hanka6", "Hančiny drobečky jsou čokoládové, ze srdíčka. Chybí hvězdičky."],
			["tonda", "Tonda", "who_tonda5", "Tonda má rád měsíčky a těch je pořád dvanáct. A v noci byl doma."],
			["birds", "Sýkorky", "who_birds", "Sýkorky zobou venku na plechu. Plechovku v zamčené spíži neotevřou."],
			["deda", "Děda", "who_deda6", ""],
		],
	}
