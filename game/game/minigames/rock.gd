extends "res://game/minigames/seriate.gd"
## Story 13 "Kámen v potoce": Bětka's three drawings of the measuring rock fell out of her sketchbook. Put them
## in order (the water rises), put the day words under them, then pick what the rock will look like tomorrow.


func _data() -> Dictionary:
	return {
		"title": "Kámen v potoce",
		"task": "Bětčiny obrázky vypadly ze skicáku. Seřaď je: první den byl kámen vidět nejvíc.",
		"levels": [
			{
				"slots": [["", "1."], ["", "2."], ["", "3."]],
				"items": [["r2", "rock_2", ""], ["r0", "rock_0", ""], ["r1", "rock_1", ""]],
				"answer": ["r0", "r1", "r2"],
				"wrong": "Podívej se na vodu. Každý den je jí víc a kámen je menší.",
				"win": "Voda každý den stoupá!",
			},
			{
				"task": "Bětka kreslila v pátek, v sobotu a v neděli. Přečti slova a dej je pod obrázky.",
				"slots": [["rock_0", ""], ["rock_1", ""], ["rock_2", ""]],
				"items": [["ne", "", "NEDĚLE"], ["pa", "", "PÁTEK"], ["so", "", "SOBOTA"]],
				"answer": ["pa", "so", "ne"],
				"wrong": "Po pátku je sobota a po sobotě neděle.",
				"win": "Pátek, sobota, neděle!",
			},
			{
				"task": "Nahoře je kámen v neděli. Voda pořád stoupá. Jak bude vypadat zítra? Dej obrázek do rámečku.",
				"slots": [["rock_2", "ZÍTRA?"]],
				"items": [["low", "rock_low", ""], ["same", "rock_1", ""], ["gone", "rock_3", ""]],
				"answer": ["gone"],
				"wrong": "Voda každý den stoupá. Bude jí víc, nebo míň?",
				"win": "Kámen zmizí pod vodou! Něco ten potok hradí.",
			},
		],
	}
