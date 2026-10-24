extends "res://game/minigames/rules.gd"
## Story 5 "Čí je rukavice?": the wet mittens (babička's too, wet from the dough) dry by the stove and got
## mixed up. Give everyone their mitten back by the rules (each says whose pattern is whose).

const LEVELS := [
	{
		"slots": [["alica", "who_alica5", "Alica"], ["hanka", "who_hanka5", "Hanka"], ["tonda", "who_tonda5", "Tonda"]],
		"items": [["star", "m_star", "hvězdičky"], ["stripe", "m_stripe", "proužky"], ["heart", "m_heart", "srdíčko"]],
		"rules": [
			["not", "star", "tonda", "Tonda nemá hvězdičky."],
			["not", "star", "alica", "Alica nemá hvězdičky."],
			["is", "stripe", "tonda", "Tonda má proužky."],
		],
		"win": "Každý má svou rukavici!",
	},
	{
		"slots": [["alica", "who_alica5", "Alica"], ["hanka", "who_hanka5", "Hanka"], ["tonda", "who_tonda5", "Tonda"],
			["babicka", "who_babicka5", "Babička"]],
		"items": [["star", "m_star", "hvězdičky"], ["stripe", "m_stripe", "proužky"], ["heart", "m_heart", "srdíčko"],
			["dots", "m_dots", "puntíky"]],
		"rules": [
			["is", "dots", "babicka", "Babička má puntíky."],
			["not", "star", "alica", "Alica nemá hvězdičky."],
			["not", "star", "tonda", "Tonda nemá hvězdičky."],
			["not", "heart", "tonda", "Tonda nemá srdíčko."],
		],
		"win": "Každý má svou rukavici!",
	},
	{
		"slots": [["alica", "who_alica5", "Alica"], ["hanka", "who_hanka5", "Hanka"], ["tonda", "who_tonda5", "Tonda"],
			["babicka", "who_babicka5", "Babička"]],
		"items": [["star", "m_star", "hvězdičky"], ["stripe", "m_stripe", "proužky"], ["heart", "m_heart", "srdíčko"],
			["dots", "m_dots", "puntíky"]],
		"rules": [
			["not", "star", "alica", "Alica nemá hvězdičky."],
			["not", "star", "hanka", "Hanka nemá hvězdičky."],
			["not", "star", "babicka", "Babička nemá hvězdičky."],
			["not", "stripe", "hanka", "Hanka nemá proužky."],
			["not", "stripe", "babicka", "Babička nemá proužky."],
			["not", "heart", "hanka", "Hanka nemá srdíčko."],
		],
		"win": "Všechny rukavice jsou zase doma!",
	},
]


func _puzzle() -> Dictionary:
	return {
		"title": "Čí je rukavice?",
		"task": "Rukavice se u kamen pomíchaly. Vrať každému tu jeho. Klikni na rukavici a pak na kamaráda. Na kartičky nahoře klikni a přečtou se.",
		"mode": "pairs",
		"levels": LEVELS,
	}
