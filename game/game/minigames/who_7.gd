extends "res://game/minigames/whodunit.gd"
## Story 7: where can babička's ring be? (places instead of people)


func _case() -> Dictionary:
	return {
		"title": "Kde je prstýnek?",
		"task": "Ráno měla babička studené ruce a prstýnek jí padal. Kdo potom hýbal se sněhem od krmítka? Kde prstýnek je?",
		"hint": "Čmuch čmuch! Děda odházel sníh od krmítka na hromadu. A co se pak stalo s hromadou?",
		"win": "V pevnosti! Sníh od krmítka děda odházel na hromadu. A z hromady jsme stavěli pevnost!",
		"culprit": "fort",
		"clues": ["clue_glove7", "clue_shovel", "clue_pile", "clue_foil"],
		"suspects": [
			["feeder", "U krmítka", "where_feeder", "U krmítka nic není. Sníh je odházený až na zem."],
			["stash", "Joeyho skrýš", "where_stash", "V Joeyho skrýši je jen rukavice, kost a ponožka."],
			["magpie", "Straka", "where_magpie", "Straka měla jen alobal. A lesklých věcí se bojí."],
			["fort", "Sněhová pevnost", "where_fort", ""],
		],
	}
