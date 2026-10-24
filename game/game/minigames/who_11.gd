extends "res://game/minigames/whodunit.gd"
## Story 11: where do the eggs go?


func _case() -> Dictionary:
	return {
		"title": "Kam mizí vajíčka?",
		"task": "Každý den chybí jedno vajíčko. Skořápky nikde. Kropenatka má v peří slámu a kvoká. Pod pletivem je dírka a pírko.",
		"hint": "Čmuch čmuch! Kdo má v peří slámu, když v kurníku jsou hobliny?",
		"win": "Kropenatka! Chodí dírkou do stodoly a vajíčka schovává mezi balíky. Chce mít kuřátka!",
		"culprit": "kropenatka",
		"clues": ["clue_noshells", "clue_straw", "clue_feather", "clue_kvok"],
		"suspects": [
			["fox", "Liška", "who_fox11", "Stopy u plotu jsou kulaté. Joeyho. A liška by nechala skořápky."],
			["magpie", "Straka", "who_magpie11", "Ve strakatém hnízdě je jen alobal, mašle a lžička. Vajíčka nejsou lesklá."],
			["tonda", "Tonda", "who_tonda11", "Tonda vajíčka nosí, nebere. Má je od maminky."],
			["jezek", "Ježek", "who_jezek11", "Ježek by vajíčko snědl. A skořápky by tu zůstaly."],
			["kropenatka", "Kropenatka", "who_kropenatka", ""],
		],
	}
