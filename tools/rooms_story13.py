#!/usr/bin/env python3
"""Story 13 "Stopy u potoka": rooms, the stick item, Bětka in summer clothes (see popochiu_gen.py).

  python3 tools/rooms_story13.py
"""
from popochiu_gen import make_room, make_item

PROPS = "res://assets/props/"


def frog(n, pos):
    return dict(name=f"Zaba{n}", tex=PROPS + "frog13.png", pos=pos, desc="Žabka", size=(90, 90), baseline=-300)


make_room(
    "Louka13", "camp13",
    walk=[(40, 790), (1880, 790), (1900, 1060), (20, 1060)],
    props=[
        dict(name="Ohen", tex=PROPS + "fire13_out.png", pos=(960, 900), desc="Ohniště", size=(400, 260), scale=0.8,
             baseline=-100),
        dict(name="Polena", tex=PROPS + "logs13.png", pos=(520, 990), desc="Polena a pilka", size=(300, 140), scale=0.8,
             baseline=-300),
        dict(name="Vrba", tex=PROPS + "willow13.png", pos=(1520, 860), desc="Spadlá vrba", size=(800, 260), scale=0.8,
             visible=False, baseline=-300),
        dict(name="Pletivo", tex=PROPS + "mesh13.png", pos=(1780, 690), desc="Vrba v pletivu", size=(220, 500),
             scale=0.9, visible=False, baseline=-300),
        frog(1, (130, 1010)), frog(2, (700, 760)), frog(3, (1210, 1040)), frog(4, (1830, 900)),
    ],
    hotspots=[
        dict(name="Stan", desc="Dědův starý stan", poly=[(800, 400), (1290, 400), (1300, 760), (790, 760)],
             walk_to=(900, 860)),
        dict(name="Vrby", desc="Vrby u potoka", poly=[(1620, 120), (1900, 120), (1900, 760), (1620, 760)],
             walk_to=(1600, 860)),
        dict(name="Potok", desc="K potoku", poly=[(1840, 800), (1920, 800), (1920, 1060), (1840, 1060)],
             walk_to=(1800, 950)),
    ],
    markers={"Start": (760, 960), "Deda": (1130, 880), "Tata": (330, 930), "Mama": (150, 900), "Tonda": (1360, 930),
             "Joey": (600, 1000)},
)

make_room(
    "Potok13", "creek13",
    walk=[(40, 800), (1880, 800), (1900, 1060), (20, 1060)],
    props=[
        dict(name="Kameny", tex=PROPS + "stones13_0.png", pos=(1000, 640), desc="Kameny přes potok", size=(760, 260),
             baseline=-400),
        dict(name="Stopy", tex=PROPS + "tracks13.png", pos=(760, 880), desc="Stopy v blátě", size=(900, 280), scale=0.8,
             visible=False, baseline=-400),
        dict(name="Vydra", tex=PROPS + "otter13.png", pos=(1480, 1000), desc="Franta nakreslil stopu", size=(180, 180),
             scale=0.8, visible=False, baseline=-400),
        dict(name="Pahyl", tex=PROPS + "stump13.png", pos=(250, 820), desc="Další pahýl", size=(240, 160),
             visible=False, baseline=-300),
        dict(name="Oci", tex=PROPS + "eyes13.png", pos=(1240, 690), desc="Něco ve vodě", size=(240, 120),
             visible=False, baseline=-400),
        frog(5, (430, 640)), frog(6, (1660, 700)), frog(7, (1110, 1030)),
    ],
    hotspots=[
        dict(name="Voda", desc="Potok", poly=[(0, 600), (1920, 600), (1920, 760), (0, 760)], walk_to=(1100, 850)),
        dict(name="Louka", desc="Zpátky do tábora", poly=[(0, 800), (80, 800), (80, 1060), (0, 1060)],
             walk_to=(110, 950)),
        dict(name="Hraz", desc="Proti proudu", poly=[(1840, 800), (1920, 800), (1920, 1060), (1840, 1060)],
             walk_to=(1800, 950)),
    ],
    markers={"Start": (300, 950), "Betka": (620, 900), "Franta": (1680, 900), "Tonda": (900, 1000), "Joey": (420, 1000)},
)

make_room(
    "Hraz13", "dam13",
    walk=[(40, 800), (1880, 800), (1900, 1060), (20, 1060)],
    props=[
        dict(name="Hraz", tex=PROPS + "dam13p.png", pos=(1040, 640), desc="Hráz z větví a bláta", size=(880, 240),
             baseline=-400),
        dict(name="Bobr", tex=PROPS + "beaver13_sit.png", pos=(1000, 520), desc="Hryzálek", size=(340, 300),
             scale=0.9, visible=False, baseline=-400),
        dict(name="Plave", tex=PROPS + "beaver13_swim.png", pos=(1400, 600), desc="Někdo plave", size=(400, 160),
             visible=False, baseline=-400),
        dict(name="Plechovka", tex=PROPS + "tin13.png", pos=(1560, 780), desc="Stará plechovka", size=(180, 140),
             visible=False, baseline=-300),
        frog(8, (560, 620)), frog(9, (1830, 640)), frog(10, (300, 1030)),
    ],
    hotspots=[
        dict(name="Hrad", desc="Bobří hrad", poly=[(220, 470), (560, 470), (560, 640), (220, 640)], walk_to=(400, 860)),
        dict(name="Lavka", desc="Stará lávka", poly=[(1300, 680), (1900, 680), (1900, 770), (1300, 770)],
             walk_to=(1500, 860)),
        dict(name="Potok", desc="Zpátky po proudu", poly=[(0, 800), (80, 800), (80, 1060), (0, 1060)],
             walk_to=(110, 950)),
    ],
    markers={"Start": (330, 950), "Hajny": (1500, 900), "Deda": (700, 930), "Verka": (1760, 920), "Tonda": (1200, 980),
             "Joey": (520, 1000), "Tata": (1780, 900)},
)

make_item("Klacik", "res://assets/props/klacik13.png", "Hančin loupaný klacík")
