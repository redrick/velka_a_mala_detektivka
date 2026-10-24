extends "res://game/minigames/rules.gd"
## Story 12 "Kdo kde sedí?": the party table, seats numbered from the left. Seat everyone by the wishes.

const LEVELS := [
	{
		"slots": [["n1", "num1", "1"], ["n2", "num2", "2"], ["n3", "num3", "3"]],
		"items": [["alica", "who_alica12", "Alica"], ["hanka", "who_hanka12", "Hanka"], ["joey", "who_joey5", "Joey"]],
		"rules": [
			["is", "alica", "n2", "Oslavenkyně sedí uprostřed."],
			["before", "joey", "hanka", "Joey sedí někde vlevo od Hanky."],
		],
		"win": "Všichni sedí, může se krájet dort!",
	},
	{
		"slots": [["n1", "num1", "1"], ["n2", "num2", "2"], ["n3", "num3", "3"], ["n4", "num4", "4"]],
		"items": [["alica", "who_alica12", "Alica"], ["hanka", "who_hanka12", "Hanka"], ["tonda", "who_tonda12", "Tonda"],
			["joey", "who_joey5", "Joey"]],
		"rules": [
			["next", "hanka", "alica", "Hanka chce sedět vedle Alice."],
			["end", "joey", "", "Joey sedí na kraji, u své misky."],
			["apart", "joey", "hanka", "Joey nesmí sedět vedle Hanky. Ujídá jí dort!"],
			["before", "tonda", "alica", "Tonda sedí někde vlevo od Alice."],
			["apart", "tonda", "hanka", "Tonda nesedí vedle Hanky."],
		],
		"win": "Všichni sedí, může se krájet dort!",
	},
	{
		"slots": [["n1", "num1", "1"], ["n2", "num2", "2"], ["n3", "num3", "3"], ["n4", "num4", "4"], ["n5", "num5", "5"]],
		"items": [["alica", "who_alica12", "Alica"], ["hanka", "who_hanka12", "Hanka"], ["tonda", "who_tonda12", "Tonda"],
			["betka", "who_betka12", "Bětka"], ["joey", "who_joey5", "Joey"]],
		"rules": [
			["is", "alica", "n3", "Oslavenkyně sedí uprostřed."],
			["next", "hanka", "alica", "Hanka chce sedět vedle Alice."],
			["end", "joey", "", "Joey sedí na kraji, u své misky."],
			["apart", "joey", "hanka", "Joey nesmí sedět vedle Hanky. Ujídá jí dort!"],
			["apart", "tonda", "betka", "Tonda a Bětka se pořád chichotají. Nesmí sedět vedle sebe."],
			["before", "betka", "alica", "Bětka sedí někde vlevo od Alice."],
			["before", "joey", "tonda", "Joey sedí někde vlevo od Tondy."],
		],
		"win": "Všichni sedí. Všechno nejlepší, Alico!",
	},
]


func _puzzle() -> Dictionary:
	return {
		"title": "Kdo kde sedí?",
		"task": "Posaď hosty ke stolu podle přání. Židle se počítají zleva. Klikni na hosta a pak na židli.",
		"mode": "row",
		"levels": LEVELS,
	}
