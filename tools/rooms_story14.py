#!/usr/bin/env python3
"""Story 14 "Poklad na hradě": rooms and the kastelánka (see popochiu_gen.py).

  python3 tools/rooms_story14.py
"""
from popochiu_gen import make_room, make_character

PROPS = "res://assets/props/"
HOLE14 = (1392, 401)   # putlog hole 14 on the courtyard tower (art/story14.py hole_xy(14))


def key(n, pos):
    return dict(name=f"Klicek{n}", tex=PROPS + "hidkey14.png", pos=pos, desc="Klíček", size=(80, 120), baseline=-300)


make_character("Kastelanka", "kastelanka", "Paní kastelánka", 580, "0.35, 0.55, 0.85")

make_room(
    "Brana14", "gate14",
    walk=[(40, 772), (1480, 772), (1480, 840), (40, 840)],
    props=[key(1, (210, 905)), key(2, (1650, 990)), key(3, (880, 560))],
    hotspots=[
        dict(name="Brana", desc="Brána do hradu", poly=[(1215, 560), (1475, 560), (1475, 842), (1215, 842)],
             walk_to=(1300, 810)),
        dict(name="Prikop", desc="Příkop s medvědy", poly=[(0, 860), (1920, 860), (1920, 1080), (0, 1080)],
             walk_to=(700, 820)),
        dict(name="Kopec", desc="Kopec pod hradem", poly=[(60, 480), (780, 380), (780, 740), (60, 740)],
             walk_to=(400, 810)),
    ],
    markers={"Start": (300, 815), "Kastelanka": (1100, 815), "Deda": (560, 815), "Verka": (700, 815),
             "Tonda": (850, 815), "Betka": (980, 815), "Joey": (430, 830)},
)

make_room(
    "Nadvori14", "court14",
    walk=[(40, 790), (1880, 790), (1900, 1060), (20, 1060)],
    props=[
        dict(name="Rohlik", tex=PROPS + "rohlik14.png", pos=(690, 690), desc="Tondův rohlík", size=(140, 80),
             baseline=-300),
        dict(name="Kavka", tex=PROPS + "kavka14.png", pos=(1880, 420), desc="Černý ptáček", size=(180, 160),
             baseline=-400),
        dict(name="KavkaDole", tex=PROPS + "kavka14_walk.png", pos=(560, 1010), desc="Černý ptáček", size=(220, 140),
             visible=False, baseline=-400),
        dict(name="Vetvicky", tex=PROPS + "twigs14.png", pos=(1480, 790), desc="Větvičky pod věží", size=(320, 140),
             visible=False, baseline=-400),
        dict(name="Oci", tex=PROPS + "eyes14.png", pos=(HOLE14[0], HOLE14[1] + 14), desc="Díra ve zdi", size=(110, 150),
             visible=False, baseline=-400),
        dict(name="Zebrik", tex=PROPS + "ladder14.png", pos=(HOLE14[0] + 20, 760), desc="Žebřík", size=(240, 840),
             scale=0.8, visible=False, baseline=-300),
        dict(name="Plechovka", tex=PROPS + "tin14.png", pos=(1180, 960), desc="Plechovka z Klubu", size=(160, 140),
             visible=False, baseline=-300),
        key(4, (60, 840)), key(5, (1010, 560)), key(6, (1880, 1000)), key(7, (1660, 730)),
    ],
    hotspots=[
        dict(name="Okna", desc="Okna paláce", poly=[(120, 430), (660, 430), (660, 620), (120, 620)], walk_to=(400, 860)),
        dict(name="Lavicka", desc="Lavička", poly=[(560, 620), (830, 620), (830, 760), (560, 760)], walk_to=(700, 860)),
        dict(name="Vez", desc="Věž", poly=[(1250, 120), (1820, 120), (1820, 760), (1250, 760)], walk_to=(1350, 860)),
        dict(name="Brana", desc="K bráně", poly=[(0, 800), (80, 800), (80, 1060), (0, 1060)], walk_to=(110, 950)),
        dict(name="Sal", desc="Do sálu", poly=[(1840, 800), (1920, 800), (1920, 1060), (1840, 1060)], walk_to=(1800, 950)),
    ],
    markers={"Start": (330, 950), "Kastelanka": (1050, 900), "Deda": (820, 940), "Verka": (980, 960), "Tonda": (620, 880),
             "Betka": (1180, 930), "Joey": (380, 1020), "Rybar": (1640, 900)},
)

make_room(
    "Sal14", "hall14",
    walk=[(40, 800), (1880, 800), (1900, 1060), (20, 1060)],
    props=[
        dict(name="Stuzka", tex=PROPS + "sill14.png", pos=(1390, 600), desc="Stužka a sponka", size=(220, 100),
             visible=False, baseline=-300),
        dict(name="Stopicky", tex=PROPS + "prints14.png", pos=(1390, 604), desc="Stopičky v prachu", size=(240, 100),
             visible=False, baseline=-300),
        key(8, (130, 760)), key(9, (1700, 1010)), key(10, (980, 700)),
    ],
    hotspots=[
        dict(name="Okno", desc="Okno ve zdi", poly=[(1230, 260), (1540, 260), (1540, 640), (1230, 640)], walk_to=(1380, 860)),
        dict(name="Spacaky", desc="Spacáky", poly=[(180, 780), (1180, 780), (1180, 900), (180, 900)], walk_to=(700, 950)),
        dict(name="Dvere", desc="Na nádvoří", poly=[(0, 800), (80, 800), (80, 1060), (0, 1060)], walk_to=(110, 950)),
    ],
    markers={"Start": (330, 960), "Kastelanka": (1700, 920), "Deda": (520, 930), "Verka": (300, 900), "Tonda": (900, 960),
             "Betka": (1100, 930), "Joey": (760, 1010), "Rybar": (160, 920)},
)
