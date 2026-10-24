#!/usr/bin/env python3
"""Story 9 "Tajná zpráva v knihovně": rooms and characters (see popochiu_gen.py).

  python3 tools/rooms_story9.py
"""
from popochiu_gen import make_room, make_character, _rect

PROPS = "res://assets/props/"

make_character("Knihovnice", "knihovnice", "Paní knihovnice", 560, "0.2, 0.45, 0.45")

make_room(
    "Kuchyne9", "kitchen",
    walk=[(40, 790), (1880, 790), (1900, 1060), (20, 1060)],
    props=[
        dict(name="Kniha", tex=PROPS + "book9.png", pos=(470, 600), desc="Knížka z knihovny", size=(140, 100), baseline=600),
        dict(name="Listek", tex=PROPS + "slip_small.png", pos=(580, 600), desc="Papírek", size=(140, 80), visible=False, baseline=600),
        dict(name="Bota", tex=PROPS + "boot9.png", pos=(1560, 1000), desc="Alicina bota", size=(140, 160), visible=False, baseline=-100),
        dict(name="Seznam", tex=PROPS + "list9.png", pos=(1290, 230), desc="Babiččin seznam", size=(160, 200), baseline=600),
        dict(name="Sici", tex=PROPS + "sewing9.png", pos=(1420, 660), desc="Šicí stroj a nůžky", size=(320, 240), baseline=-100),
    ],
    hotspots=[
        dict(name="Dvere", desc="Dveře ven", poly=[(1690, 230), (1880, 230), (1880, 756), (1690, 756)], walk_to=(1700, 830)),
        dict(name="Kamna", desc="Kamna", poly=[(58, 360), (328, 360), (328, 756), (58, 756)], walk_to=(380, 850)),
    ],
    markers={"Start": (760, 900), "Venku": (1620, 880), "Stul": (520, 860)},
)

make_room(
    "Knihovna9", "library9",
    walk=[(40, 800), (1880, 800), (1900, 1060), (20, 1060)],
    hotspots=[
        dict(name="Pult", desc="Pult paní knihovnice", poly=[(1150, 610), (1760, 610), (1760, 800), (1150, 800)], walk_to=(1100, 880)),
        dict(name="Police", desc="Police s knížkami", poly=[(380, 150), (1100, 150), (1100, 780), (380, 780)], walk_to=(700, 880)),
        dict(name="Ven", desc="Ven", poly=[(0, 560), (90, 560), (90, 1060), (0, 1060)], walk_to=(110, 950)),
    ],
    markers={"Start": (260, 950), "Knihovnice": (1450, 880), "Tonda": (960, 950)},
)

make_room(
    "Mlyn9", "mill6",
    walk=[(40, 790), (1880, 790), (1900, 1060), (20, 1060)],
    hotspots=[
        dict(name="Mlyn", desc="Mlýn", poly=[(120, 300), (560, 300), (560, 740), (120, 740)], walk_to=(400, 870)),
        dict(name="Zpet", desc="Zpátky", poly=[(0, 560), (90, 560), (90, 1060), (0, 1060)], walk_to=(110, 950)),
    ],
    markers={"Start": (260, 950), "Verka": (900, 920)},
)

make_room(
    "Masopust9", "street9",
    walk=[(40, 790), (1880, 790), (1900, 1060), (20, 1060)],
    hotspots=[
        dict(name="Pruvod", desc="Masopustní průvod", poly=[(700, 250), (1880, 250), (1880, 780), (700, 780)], walk_to=(800, 900)),
    ],
    markers={"Start": (300, 950), "Kobyla": (860, 900), "Kominik": (1110, 890), "Baba": (1380, 900), "Medved": (1640, 900),
             "Franta": (1820, 900)},
)
