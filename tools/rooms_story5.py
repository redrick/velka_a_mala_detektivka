#!/usr/bin/env python3
"""Story 5 "Kdo staví sněhuláky?": rooms, characters and items (see popochiu_gen.py).

  python3 tools/rooms_story5.py
"""
from popochiu_gen import make_room, make_item, make_character, _rect

PROPS = "res://assets/props/"

make_character("Betka", "betka", "Holčička s bambulí", 460, "0.75, 0.2, 0.2")

make_room(
    "Zahrada5", "garden5",
    walk=[(40, 780), (1880, 780), (1900, 1060), (20, 1060)],
    props=[
        dict(name="Snehulak", tex=PROPS + "snowman1.png", pos=(1060, 820), desc="Sněhulák", size=(300, 420),
             baseline=180, poly=[(-150, -200), (150, -200), (150, 200), (-150, 200)]),
        dict(name="Stopy", tex=PROPS + "star_prints.png", pos=(1180, 900), desc="Malé stopy", size=(440, 140), baseline=-300),
        dict(name="Nit", tex=PROPS + "red_thread.png", pos=(1360, 650), desc="Červená nitka", size=(120, 120),
             visible=False, baseline=-300),
        dict(name="Rukavice", tex=PROPS + "mitten_lost.png", pos=(1290, 770), desc="Rukavička", size=(100, 100),
             visible=False, baseline=-300),
        dict(name="Odpoved", tex=PROPS + "answer.png", pos=(560, 870), desc="Naše odpověď", size=(600, 380),
             visible=False, baseline=180, poly=[(-200, -190), (290, -190), (290, 40), (-200, 40)]),
        dict(name="Hvezda", tex=PROPS + "twig_star.png", pos=(860, 720), desc="Hvězda z větviček", size=(160, 160),
             visible=False, baseline=-200),
        dict(name="Malicky", tex=PROPS + "tiny_snowman.png", pos=(900, 880), desc="Malinký sněhulák s bambulí",
             size=(160, 220), visible=False, baseline=100),
    ],
    hotspots=[
        dict(name="Dum", desc="Domů do kuchyně", poly=[(240, 520), (420, 520), (420, 740), (240, 740)], walk_to=(330, 840)),
        dict(name="Diera", desc="Díra v plotě", poly=[(1255, 560), (1360, 560), (1360, 760), (1255, 760)], walk_to=(1300, 820)),
        dict(name="Plot", desc="Plot", poly=[(700, 540), (1250, 540), (1250, 720), (700, 720)], walk_to=(980, 800)),
        dict(name="NaSilnici", desc="Na silnici", poly=[(1830, 560), (1920, 560), (1920, 1060), (1830, 1060)], walk_to=(1810, 950)),
    ],
    markers={"Start": (420, 900), "ZeSilnice": (1700, 950), "Snehulak": (880, 900), "ZaPlotem": (1500, 700)},
)

make_room(
    "Ves5", "village5",
    walk=[(40, 780), (1880, 780), (1900, 1060), (20, 1060)],
    props=[
        dict(name="Sane", tex=PROPS + "sled_tracks.png", pos=(760, 1000), desc="Stopy od saní", size=(520, 120), baseline=-300),
        dict(name="VelkeStopy", tex=PROPS + "big_prints.png", pos=(420, 930), desc="Velké stopy", size=(400, 120), baseline=-300),
    ],
    hotspots=[
        dict(name="Koleje", desc="Koleje od traktoru", poly=[(900, 930), (1700, 930), (1700, 1010), (900, 1010)], walk_to=(1100, 900)),
        dict(name="DumTonda", desc="Tondův dům", poly=[(260, 480), (720, 480), (720, 720), (260, 720)], walk_to=(480, 840)),
        dict(name="DumFranta", desc="Frantův dům", poly=[(1430, 480), (1560, 480), (1560, 730), (1430, 730)], walk_to=(1490, 840)),
        dict(name="Zpet", desc="Zpátky na zahradu", poly=[(0, 560), (90, 560), (90, 1060), (0, 1060)], walk_to=(110, 950)),
    ],
    markers={"Start": (260, 950), "ZFranty": (1490, 880), "Tonda": (640, 900)},
)

make_room(
    "Franta5", "hallway5",
    walk=[(40, 800), (1880, 800), (1900, 1060), (20, 1060)],
    props=[
        dict(name="Boticky", tex=PROPS + "small_boots.png", pos=(1100, 850), desc="Malé botičky", size=(240, 140), baseline=-100),
    ],
    hotspots=[
        dict(name="Ven", desc="Ven", poly=[(58, 170), (270, 170), (270, 790), (58, 790)], walk_to=(260, 900)),
        dict(name="Pastinak", desc="Bedýnky s pastinákem", poly=[(380, 600), (860, 600), (860, 800), (380, 800)], walk_to=(620, 880)),
        dict(name="Kamna", desc="Kamna", poly=[(920, 400), (1270, 400), (1270, 790), (920, 790)], walk_to=(1000, 900)),
        dict(name="Zaves", desc="Závěs ke schodům", poly=[(1536, 170), (1824, 170), (1824, 790), (1536, 790)], walk_to=(1500, 900)),
    ],
    markers={"Start": (300, 930), "Franta": (1380, 900)},
)

make_room(
    "Kuchyne5", "kitchen",
    walk=[(40, 790), (1880, 790), (1900, 1060), (20, 1060)],
    hotspots=[
        dict(name="Dvere", desc="Dveře ven", poly=[(1690, 230), (1880, 230), (1880, 756), (1690, 756)], walk_to=(1700, 830)),
        dict(name="Okno", desc="Okno", poly=[(690, 150), (1115, 150), (1115, 440), (690, 440)], walk_to=(900, 820)),
        dict(name="Kamna", desc="Kamna", poly=[(58, 360), (328, 360), (328, 756), (58, 756)], walk_to=(380, 850)),
    ],
    markers={"Start": (760, 900), "ZeZahrady": (1620, 880), "Okno": (900, 860)},
)

make_item("Rukavicka", PROPS + "mitten_icon.png", "Hančina rukavička")
