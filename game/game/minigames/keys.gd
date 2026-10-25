extends "res://game/minigames/match.gd"
## Story 14 "Klíče od hradu": the kastelánka's keys have Roman numbers, the doors have dots. Put each key to its
## door. The last level ends with XIV.

const WHY := {
	"1": "I je jedna čárka. Jedna tečka.",
	"2": "II jsou dvě čárky. Dvě tečky.",
	"3": "III jsou tři čárky. Tři tečky.",
	"4": "IV: jednička před pětkou. O jednu míň než pět.",
	"5": "V je jako ruka. Pět prstů.",
	"6": "VI: jednička za pětkou. O jednu víc než pět.",
	"9": "IX: jednička před desítkou. O jednu míň než deset.",
	"10": "X jsou jako dvě ruce. Deset prstů.",
	"11": "XI: jednička za desítkou. Deset a jedna.",
	"14": "XIV: deset a čtyři. Čtrnáct!",
}


func _data() -> Dictionary:
	return {
		"title": "Klíče od hradu",
		"task": "I = 1, V = 5, X = 10. Jednička před větším znakem jednu ubere, za ním jednu přidá. Dej každý klíč ke dveřím se stejným počtem teček.",
		"levels": [
			{
				"left": [["1", "key14", "I"], ["2", "key14", "II"], ["3", "key14", "III"]],
				"right": [["3", "dots_3", ""], ["1", "dots_1", ""], ["2", "dots_2", ""]],
				"why": WHY,
				"win": "Čárky se počítají jako prstíky!",
			},
			{
				"left": [["5", "key14", "V"], ["4", "key14", "IV"], ["6", "key14", "VI"]],
				"right": [["4", "dots_4", ""], ["6", "dots_6", ""], ["5", "dots_5", ""]],
				"why": WHY,
				"win": "IV je čtyři a VI je šest!",
			},
			{
				"left": [["10", "key14", "X"], ["9", "key14", "IX"], ["14", "key14", "XIV"], ["11", "key14", "XI"]],
				"right": [["11", "dots_11", ""], ["14", "dots_14", ""], ["10", "dots_10", ""], ["9", "dots_9", ""]],
				"why": WHY,
				"win": "XIV je čtrnáct! Jako na Věrčině kresbě!",
			},
		],
	}
