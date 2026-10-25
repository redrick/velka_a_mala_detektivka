extends "res://game/minigames/whodunit.gd"
## Story 14: who takes the things at the castle?


func _case() -> Dictionary:
	return {
		"title": "Kdo krade na hradě?",
		"task": "Zmizel rohlík, stužka a sponka. Na okně jsou ptačí stopičky a černé pírko. Pod věží větvičky a Joeyho chlupy. Ve zdi svítí dvě světlé oči.",
		"hint": "Čmuch čmuch! Kdo má černé peří a bydlí v díře ve zdi?",
		"win": "Černý ptáček z díry ve zdi! Nosí si do hnízda měkké věci.",
		"culprit": "kavka",
		"clues": ["clue_prints14", "clue_feather14", "clue_twigs14", "clue_wall14", "clue_ribbon14"],
		"suspects": [
			["medved", "Medvědi", "who_medved14", "Medvědi z příkopu ven nemůžou. A po okně by nechodili."],
			["strasidlo", "Strašidlo", "who_strasidlo14", "Strašidla nejsou. A strašidlo nenechává pírka ani větvičky."],
			["holub", "Holub", "who_holub14", "Holubí pírko je šedé. Tohle je černé."],
			["joey", "Joey", "who_joey5", "Joey celou dobu spal. A k oknu by nevyskočil."],
			["kastelanka", "Kastelánka", "who_kastelanka14", "Paní kastelánka jen otvírala okenice. Stužku neviděla."],
			["kavka", "Černý pták", "who_kavka14", ""],
		],
	}
