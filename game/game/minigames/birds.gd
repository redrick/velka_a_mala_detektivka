extends "res://game/minigames/rules.gd"
## Story 6 "Kdo co zobe?": babička fills the feeder, and every bird has its favourite food. Give each bird
## its own by the rules.

const LEVELS := [
	{
		"slots": [["sykorka", "bird_sykorka", "Sýkorka"], ["hyl", "bird_hyl", "Hýl"], ["kos", "bird_kos", "Kos"]],
		"items": [["lojova", "food_lojova", "lojová koule"], ["jerabiny", "food_jerabiny", "jeřabiny"],
			["jablko", "food_jablko", "jablíčko"]],
		"rules": [
			["is", "jablko", "kos", "Kos zobe jablíčko."],
			["not", "jerabiny", "sykorka", "Sýkorka jeřabiny nechce."],
		],
		"win": "Každý ptáček má svou dobrotu!",
	},
	{
		"slots": [["hyl", "bird_hyl", "Hýl"], ["kos", "bird_kos", "Kos"], ["vrabec", "bird_vrabec", "Vrabec"]],
		"items": [["jerabiny", "food_jerabiny", "jeřabiny"], ["jablko", "food_jablko", "jablíčko"], ["zrni", "food_zrni", "zrní"]],
		"rules": [
			["not", "jablko", "hyl", "Hýl jablíčko nechce."],
			["not", "jablko", "vrabec", "Vrabec jablíčko nechce."],
			["not", "zrni", "hyl", "Hýl zrní nechce."],
		],
		"win": "Každý ptáček má svou dobrotu!",
	},
	{
		"slots": [["sykorka", "bird_sykorka", "Sýkorka"], ["hyl", "bird_hyl", "Hýl"], ["kos", "bird_kos", "Kos"],
			["vrabec", "bird_vrabec", "Vrabec"]],
		"items": [["lojova", "food_lojova", "lojová koule"], ["jerabiny", "food_jerabiny", "jeřabiny"],
			["jablko", "food_jablko", "jablíčko"], ["zrni", "food_zrni", "zrní"]],
		"rules": [
			["not", "lojova", "kos", "Kos lojovou kouli nechce."],
			["not", "lojova", "hyl", "Hýl lojovou kouli nechce."],
			["not", "zrni", "sykorka", "Sýkorka zrní nechce."],
			["not", "zrni", "kos", "Kos zrní nechce."],
			["not", "jerabiny", "vrabec", "Vrabec jeřabiny nechce."],
			["not", "jablko", "hyl", "Hýl jablíčko nechce."],
			["not", "lojova", "vrabec", "Vrabec lojovou kouli nechce."],
			["not", "jerabiny", "kos", "Kos jeřabiny nechce."],
		],
		"win": "Krmítko je plné a všichni ptáčci zobou!",
	},
]


func _puzzle() -> Dictionary:
	return {
		"title": "Kdo co zobe?",
		"task": "Každý ptáček má rád něco jiného. Dej každému jeho dobrotu. Klikni na dobrotu a pak na ptáčka.",
		"mode": "pairs",
		"levels": LEVELS,
	}
