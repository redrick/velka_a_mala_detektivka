extends "res://game/minigames/match.gd"
## Story 13 "Čím to bylo?": each mark on the wood next to what made it. The last level adds the willow stump:
## not the saw, not the knife, not Joey.

const WHY := {
	"saw": "Pilka řeže rovně. Řez je hladký a placatý.",
	"knife": "Nožík dělá dlouhé tenké kudrlinky.",
	"joey": "Pejsek má malé špičaté zoubky. Dělají dírky.",
	"teeth": "Tady jsou velké široké rýhy. Dva velké zuby vedle sebe!",
}


func _data() -> Dictionary:
	return {
		"title": "Čím to bylo?",
		"task": "Klikni na stopu na dřevě vlevo a pak na to, co ji udělalo.",
		"levels": [
			{
				"left": [["saw", "mark_flat", ""], ["knife", "mark_curls", ""], ["joey", "mark_holes", ""]],
				"right": [["joey", "by_joey", ""], ["saw", "by_saw", ""], ["knife", "by_knife", ""]],
				"why": WHY,
				"win": "Pilka, nožík i Joey dělají jiné stopy než ten pahýl.",
			},
			{
				"left": [["knife", "mark_curls", ""], ["teeth", "mark_grooves", ""], ["saw", "mark_flat", ""],
					["joey", "mark_holes", ""]],
				"right": [["saw", "by_saw", ""], ["joey", "by_joey", ""], ["teeth", "by_teeth", ""], ["knife", "by_knife", ""]],
				"why": WHY,
				"win": "Vrbu pokácel někdo s dvěma velkými zuby!",
			},
		],
	}
