extends "res://game/minigames/rules.gd"
## Story 9 "Masopustní průvod": line up the masks for the parade (1 = in front) by the old rules.

const LEVELS := [
	{
		"slots": [["n1", "num1", "1"], ["n2", "num2", "2"], ["n3", "num3", "3"]],
		"items": [["kobyla", "who_kobyla", "kobyla"], ["franta", "who_franta9", "medvědář"], ["medved", "who_medved", "medvěd"]],
		"rules": [
			["is", "kobyla", "n1", "Kobyla jde v průvodu první."],
			["before", "franta", "medved", "Medvědář jde před medvědem."],
		],
		"win": "Průvod může vyrazit!",
	},
	{
		"slots": [["n1", "num1", "1"], ["n2", "num2", "2"], ["n3", "num3", "3"], ["n4", "num4", "4"]],
		"items": [["kobyla", "who_kobyla", "kobyla"], ["franta", "who_franta9", "medvědář"], ["medved", "who_medved", "medvěd"],
			["kominik", "who_kominik", "kominík"]],
		"rules": [
			["is", "kobyla", "n1", "Kobyla jde v průvodu první."],
			["next", "franta", "medved", "Medvědář vede medvěda: jdou hned za sebou."],
			["before", "franta", "medved", "Medvědář jde před medvědem."],
			["end", "kominik", "", "Kominík jde na kraji průvodu."],
		],
		"win": "Průvod může vyrazit!",
	},
	{
		"slots": [["n1", "num1", "1"], ["n2", "num2", "2"], ["n3", "num3", "3"], ["n4", "num4", "4"], ["n5", "num5", "5"]],
		"items": [["kobyla", "who_kobyla", "kobyla"], ["franta", "who_franta9", "medvědář"], ["medved", "who_medved", "medvěd"],
			["kominik", "who_kominik", "kominík"], ["baba", "who_baba", "bába s nůší"]],
		"rules": [
			["end", "kobyla", "", "Kobyla jde na kraji průvodu."],
			["end", "baba", "", "Bába s nůší jde na kraji průvodu."],
			["before", "kobyla", "baba", "Kobyla jde před bábou."],
			["next", "franta", "medved", "Medvědář vede medvěda: jdou hned za sebou."],
			["before", "franta", "medved", "Medvědář jde před medvědem."],
			["next", "kominik", "kobyla", "Kominík jde hned u kobyly."],
		],
		"win": "Masopust! Průvod vyráží vesnicí!",
	},
]


func _puzzle() -> Dictionary:
	return {
		"title": "Masopustní průvod",
		"task": "Seřaď masky do průvodu podle pravidel (1 jde první). Klikni na masku a pak na číslo.",
		"mode": "row",
		"levels": LEVELS,
	}
