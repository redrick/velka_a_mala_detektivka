extends "res://game/minigames/whodunit.gd"
## Story 12: who drew this arrow? Played three times, once for each kind of arrow (set `kind` before adding).

var kind := "tata"

const CASES := {
	"tata": {
		"task": "Dlouhá rovná šipka. Hodně vysoko. Vedle černá šmouha od oleje.",
		"hint": "Čmuch čmuch! Kdo je velký a má ruce od oleje?",
		"win": "Táta! Je vysoký a opravuje v garáži. Proto ta šmouha od oleje.",
		"why": {
			"mama": "Máma kreslí čárkovaně a se srdíčkem.",
			"hanka": "Hanka tak vysoko nedosáhne.",
			"tonda": "Tonda má ruce od křídy, ne od oleje.",
			"betka": "Bětka má ruce od barvy, ne od oleje.",
		},
	},
	"mama": {
		"task": "Čárkovaná šipka. Na konci srdíčko.",
		"hint": "Čmuch čmuch! Kdo se podepisuje srdíčkem?",
		"win": "Máma! Srdíčkem se podepisuje na lístečky ve svačině.",
		"why": {
			"tata": "Táta kreslí dlouhé rovné čáry. Bez srdíčka.",
			"hanka": "Hanka kreslí tečky.",
			"tonda": "Tonda kreslí panáka, ne srdíčka.",
			"betka": "Bětka maluje barvou, ne křídou.",
		},
	},
	"hanka": {
		"task": "Malinká šipka z teček. Celá křivá. Úplně dole u země.",
		"hint": "Čmuch čmuch! Kdo je nejmenší?",
		"win": "Hanka! Je malá, proto kreslí dole u země. A opička má tlapku od křídy!",
		"why": {
			"tata": "Táta kreslí vysoko. Tahle je úplně u země.",
			"mama": "Máma kreslí čárky a srdíčko. Tahle je z teček.",
			"tonda": "Tonda je velký. A jeho křída je na panákovi.",
			"betka": "Bětka maluje barvou, ne křídou.",
		},
	},
}


func _case() -> Dictionary:
	var c: Dictionary = CASES[kind]
	var why: Dictionary = c.why
	return {
		"title": "Kdo nakreslil tuhle šipku?",
		"task": c.task,
		"hint": c.hint,
		"win": c.win,
		"culprit": kind,
		"clues": ["clue_arrow_" + kind],
		"suspects": [
			["tata", "Táta", "who_tata12", why.get("tata", "")],
			["mama", "Máma", "who_mama12", why.get("mama", "")],
			["hanka", "Hanka", "who_hanka12", why.get("hanka", "")],
			["tonda", "Tonda", "who_tonda12", why.get("tonda", "")],
			["betka", "Bětka", "who_betka12", why.get("betka", "")],
		],
	}
