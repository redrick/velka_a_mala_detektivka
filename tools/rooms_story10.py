#!/usr/bin/env python3
"""Story 10 "Záhada ve škole": rooms and characters (see popochiu_gen.py).

  python3 tools/rooms_story10.py
"""
from popochiu_gen import make_room, make_character, _rect

PROPS = "res://assets/props/"

make_character("Mama", "mama", "Máma", 580, "0.55, 0.25, 0.45")
make_character("Tata", "tata", "Táta", 640, "0.2, 0.3, 0.55")
make_character("Lucie", "lucie", "Paní učitelka Lucie", 580, "0.45, 0.2, 0.5")
make_character("Skolnik", "skolnik", "Pan Karel, školník", 660, "0.2, 0.4, 0.25")
make_character("MalyKarel", "malykarel", "Malý Karel", 480, "0.25, 0.35, 0.6")

make_room(
    "Skola10", "school10",
    walk=[(40, 790), (1880, 790), (1900, 1060), (20, 1060)],
    props=[
        dict(name="Kotec", tex=PROPS + "hutch_empty.png", pos=(1500, 740), desc="Prázdný kotec", size=(560, 420),
             baseline=200, poly=_rect(0, 40, 560, 380)),
        dict(name="NovyKotec", tex=PROPS + "hutch_new.png", pos=(1500, 730), desc="Nový kotec", size=(600, 460),
             visible=False, baseline=200, poly=_rect(0, 40, 600, 420)),
        dict(name="Seno", tex=PROPS + "hay_trail10.png", pos=(820, 880), desc="Stopa ze sena", size=(840, 120), baseline=-300),
        dict(name="Stopy", tex=PROPS + "prints_mud10.png", pos=(1240, 970), desc="Stopy v blátě", size=(600, 140), baseline=-300),
        dict(name="Spoluzaci", tex=PROPS + "classmates.png", pos=(250, 820), desc="Spolužáci", size=(600, 500),
             baseline=180, poly=_rect(0, 0, 560, 480)),
        dict(name="Jezek", tex=PROPS + "hedgehog.png", pos=(260, 680), desc="Ježek", size=(180, 120), visible=False, baseline=-100),
    ],
    hotspots=[
        dict(name="Hromada", desc="Hromada klestí", poly=[(20, 380), (420, 380), (420, 700), (20, 700)], walk_to=(420, 880)),
        dict(name="Srub", desc="Dveře do kumbálu", poly=[(900, 420), (1030, 420), (1030, 690), (900, 690)], walk_to=(960, 860)),
        dict(name="Hacek", desc="Háček na čepici", poly=[(1040, 440), (1110, 440), (1110, 520), (1040, 520)], walk_to=(1060, 860)),
    ],
    markers={"Start": (600, 950), "Tata": (1750, 930), "Lucie": (1220, 950), "Karel": (640, 1000), "Srub": (960, 880)},
)

make_room(
    "Kumbal10", "kumbal10",
    walk=[(40, 800), (1880, 800), (1900, 1060), (20, 1060)],
    props=[
        dict(name="Cepice", tex=PROPS + "hat_nest.png", pos=(1520, 880), desc="Čepice pana Karla", size=(600, 320), baseline=100),
    ],
    hotspots=[
        dict(name="Ven", desc="Ven", poly=[(0, 560), (90, 560), (90, 1060), (0, 1060)], walk_to=(110, 950)),
    ],
    markers={"Start": (300, 950), "Karel": (1150, 920)},
)

make_room(
    "Domov10", "home10",
    walk=[(40, 800), (1880, 800), (1900, 1060), (20, 1060)],
    props=[
        dict(name="Krabice", tex=PROPS + "box10.png", pos=(1500, 880), desc="Krabice s dírkami", size=(240, 200), baseline=-100),
    ],
    hotspots=[
        dict(name="Okno", desc="Okno", poly=[(1150, 100), (1770, 100), (1770, 640), (1150, 640)], walk_to=(1400, 880)),
    ],
    markers={"Start": (500, 950), "Mama": (900, 920), "Tata": (1250, 920)},
)
