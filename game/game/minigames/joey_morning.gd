extends "res://game/minigames/rules.gd"
## Story 7 "Co se ráno dělo?": the ring is gone, so the detectives put the day in order from what everyone
## remembers (1 = first). The same true morning both times, the second time with děda's shovel too.

const LEVELS := [
	{
		"slots": [["n1", "num1", "1"], ["n2", "num2", "2"], ["n3", "num3", "3"]],
		"items": [["feeder", "where_feeder", "babička u krmítka"], ["stash", "where_stash", "Joeyho skrýš"],
			["fort", "where_fort", "sněhová pevnost"]],
		"rules": [
			["before", "feeder", "stash", "Babička krmila ptáčky dřív, než Joey schoval rukavici."],
			["before", "stash", "fort", "Pevnost jsme stavěli až odpoledne. To už byla rukavice ve skrýši."],
		],
		"win": "Haf! Přesně tak to bylo!",
	},
	{
		"slots": [["n1", "num1", "1"], ["n2", "num2", "2"], ["n3", "num3", "3"], ["n4", "num4", "4"]],
		"items": [["feeder", "where_feeder", "babička u krmítka"], ["stash", "where_stash", "Joeyho skrýš"],
			["shovel", "clue_shovel", "děda s lopatou"], ["fort", "where_fort", "sněhová pevnost"]],
		"rules": [
			["before", "shovel", "fort", "Pevnost je z hromady, kterou nahrnul děda."],
			["before", "feeder", "shovel", "Děda házel sníh až po krmení ptáčků."],
			["before", "feeder", "stash", "Joey sebral rukavici, kterou babička odložila u krmítka."],
			["next", "stash", "feeder", "Joey ji sebral hned. Nic jiného mezi tím nebylo."],
		],
		"win": "Haf! Teď víme, jak šel celý den po sobě.",
	},
]


func _puzzle() -> Dictionary:
	return {
		"title": "Co se ráno dělo?",
		"task": "Seřaď, co se dnes dělo, jak to šlo po sobě (1 bylo první). Klikni na obrázek a pak na číslo.",
		"mode": "row",
		"levels": LEVELS,
	}
