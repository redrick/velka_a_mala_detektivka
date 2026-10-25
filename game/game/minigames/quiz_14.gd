extends "res://game/minigames/quiz.gd"
## Story 14: what the kastelánka told about jackdaws and the castle.


func _data() -> Dictionary:
	return {
		"title": "Pravda, nebo ne?",
		"task": "Co víš o kavkách? Přečti větu a řekni, jestli je to pravda.",
		"questions": [
			["res://assets/slides/k_kavka.png", "Kavka je bílá s černou hlavou.", false,
				"Kavka je černá. Jen zátylek má stříbrně šedý a oči světlé."],
			["res://assets/slides/k_nest.png", "Kavka si dělá hnízdo v díře ve zdi.", true,
				"Ve stromech, ve skalách, v komínech i v děrách hradních zdí."],
			["res://assets/props/twigs14.png", "Pod kavčí dírou leží spadané větvičky.", true,
				"Větvičky, které se do díry nevešly, spadnou dolů. Podle nich se hnízdo pozná."],
			["res://assets/props/sill14.png", "Kavka si do hnízda nosí měkké věci.", true,
				"Trávu, mech, chlupy, peří, hadříky… i stužku a sponku!"],
			["res://assets/slides/k_share.png", "Kavky se o jídlo nikdy nedělí.", false,
				"Kavky se o jídlo dělí. Tondův rohlík snědly spolu."],
			["res://assets/slides/k_bears.png", "Medvědi Martin a Agáta můžou vylézt z příkopu.", false,
				"Z příkopu ven nemůžou. Kastelánka jim nosí jablka a mrkev."],
		],
		"win": "Teď víš o kavkách skoro všechno!",
	}
