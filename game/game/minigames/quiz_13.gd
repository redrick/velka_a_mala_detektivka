extends "res://game/minigames/quiz.gd"
## Story 13: what the hajný told about beavers.


func _data() -> Dictionary:
	return {
		"title": "Pravda, nebo ne?",
		"task": "Co víš o bobrech? Přečti větu a řekni, jestli je to pravda.",
		"questions": [
			["res://assets/props/beaver13_sit.png", "Bobr jí ryby.", false,
				"Bobr ryby nejí. Jí kůru, větvičky a listí."],
			["res://assets/slides/b_teeth.png", "Bobr má oranžové zuby.", true,
				"V zubech má železo. Proto jsou oranžové a tvrdé."],
			["res://assets/slides/b_lodge.png", "Vchod do bobřího hradu je pod vodou.", true,
				"Pod vodou se liška do hradu nedostane."],
			["res://assets/slides/b_tail.png", "Když bobr plácne ocasem, říká: Pozor, nebezpečí!", true,
				"PLESK! A všichni bobři se potopí."],
			["res://assets/props/willow13.png", "Bobr kácí stromy pilkou.", false,
				"Bobr nemá pilku. Okusuje strom dokola zuby, až je z něj tužka."],
			["res://assets/slides/b_young.png", "Mladý bobr si hledá vlastní potok.", true,
				"Když jsou bobrovi asi dva roky, odejde od rodičů a staví si vlastní hráz."],
		],
		"win": "Teď víš o bobrech skoro všechno!",
	}
