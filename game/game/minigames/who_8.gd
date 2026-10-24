extends "res://game/minigames/whodunit.gd"
## Story 8: who eats the snowmen's noses?


func _case() -> Dictionary:
	return {
		"title": "Kdo okusuje nosy?",
		"task": "Nosy zmizely i u nejvyššího sněhuláka. Kousek nosu je roztřepený. Na čistém sněhu je stopa jako dvě špičaté kapky, vzadu bez teček.",
		"hint": "Čmuch čmuch! Kdo nemá nahoře přední zuby a dosáhne vysoko?",
		"win": "Srnka! Dosáhne vysoko, nemá nahoře zuby, tak trhá. A stopa je bez teček.",
		"culprit": "deer",
		"clues": ["clue_high", "clue_stub", "clue_deerprint", "clue_alibi"],
		"suspects": [
			["joey", "Joey", "who_joey5", "Joey spal celou noc v chodbě. Jeho stopy přibyly až ráno."],
			["hare", "Zajíc", "who_hare", "Zajíc je malý, tak vysoko nedosáhne. A kouše rovně jako nůžky."],
			["fox", "Liška", "who_fox", "Liška nejí mrkev, loví myši. A její stopy jdou v řadě k myší díře."],
			["boar", "Divočák", "who_boar", "Divočák má vzadu dvě tečky. Na čistém sněhu žádné nejsou."],
			["deer", "Srnka", "who_deer", ""],
		],
	}
