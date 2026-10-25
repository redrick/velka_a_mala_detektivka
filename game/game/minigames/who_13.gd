extends "res://game/minigames/whodunit.gd"
## Story 13: who fells the willows by the creek?


func _case() -> Dictionary:
	return {
		"title": "Kdo kácí vrby?",
		"task": "Pahýl jako tužka, široké rýhy od zubů, velké stopy s blánou, voda pořád stoupá, v noci PLESK. A dědova hůl zmizela.",
		"hint": "Čmuch čmuch! Kdo má dva velké zuby a plave?",
		"win": "Bobr! Okusuje vrby, plave v noci a staví z větví hráz. Proto voda stoupá!",
		"culprit": "bobr",
		"clues": ["clue_stump13", "clue_grooves13", "clue_webbed13", "clue_rock13", "clue_plesk13", "clue_stick13"],
		"suspects": [
			["tata", "Táta", "who_tata13", "Táta řezal pilkou suché větve. Pilka dělá rovný řez, ne tužku."],
			["hanka", "Hanka", "who_hanka13", "Hanka loupe klacík nožíkem. To jsou tenké kudrlinky. Strom by nepokácela!"],
			["joey", "Joey", "who_joey5", "Joey dělá zoubky malé dírky. A do vody se mu nechce."],
			["vydra", "Vydra", "who_vydra13", "Vydra má malou kulatou tlapku a jí ryby. Stopy u potoka jsou velké a s blánou."],
			["vlkodlak", "Vlkodlak", "who_vlkodlak13", "Vlkodlaci nejsou! Tonda to vymyslel, aby nás postrašil."],
			["bobr", "Bobr", "who_bobr13", ""],
		],
	}
