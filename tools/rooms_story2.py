#!/usr/bin/env python3
"""Story 2 "Tajemství starého klíče": writes its four rooms and two items with popochiu_gen.

  python3 tools/rooms_story2.py

Safe to re-run: scenes are rewritten, the hand-written room scripts are kept.
Positions follow the art in art/story2.py (rooms are 960 x 540 pt drawn at 2x, y flipped).
"""
from popochiu_gen import make_room, make_item, _rect

PROPS = "res://assets/props/"

make_room(
    "Loznice", "bedroom",
    walk=[(40, 880), (1880, 880), (1900, 1060), (20, 1060)],
    hotspots=[
        dict(name="Strop", desc="Strop", poly=[(0, 0), (1920, 0), (1920, 125), (0, 125)], walk_to=(960, 940)),
        dict(name="Okno", desc="Okno", poly=_rect(240, 410, 290, 345), walk_to=(300, 940)),
        dict(name="Postele", desc="Postýlky", poly=[(470, 650), (1510, 650), (1510, 780), (470, 780)], walk_to=(960, 920)),
        dict(name="Dvere", desc="Dveře do kuchyně", poly=[(1651, 324), (1843, 324), (1843, 864), (1651, 864)], walk_to=(1700, 930)),
    ],
    markers={"Start": (700, 960)},
)

make_room(
    "Snidane", "kitchen",
    walk=[(40, 790), (1880, 790), (1900, 1060), (20, 1060)],
    props=[
        dict(name="Hrnek1", tex=PROPS + "mug.png", pos=(790, 500), desc="Kakao", size=(90, 90)),
        dict(name="Hrnek2", tex=PROPS + "mug.png", pos=(1030, 500), desc="Kakao", size=(90, 90)),
        dict(name="Micka", tex="res://assets/characters/cat_micka.png", pos=(430, 800), desc="Kočka Micka",
             size=(200, 200), baseline=100, scale=0.8),
    ],
    hotspots=[
        dict(name="Dvere", desc="Dveře na zahradu", poly=[(1690, 230), (1880, 230), (1880, 756), (1690, 756)], walk_to=(1700, 830)),
        dict(name="Okno", desc="Okno", poly=[(690, 150), (1115, 150), (1115, 540), (690, 540)], walk_to=(900, 820)),
        dict(name="Kamna", desc="Kamna", poly=[(58, 360), (328, 360), (328, 756), (58, 756)], walk_to=(380, 850)),
    ],
    markers={"Start": (900, 880), "ZeZahrady": (1620, 880)},
)

make_room(
    "Stit", "gable",
    walk=[(40, 800), (1880, 800), (1900, 1060), (20, 1060)],
    props=[
        dict(name="Pirko", tex=PROPS + "feather.png", pos=(1180, 930), desc="Bílé pírko", scale=0.8,
             size=(110, 150), baseline=60),
        dict(name="Vyvrzky", tex=PROPS + "pellets.png", pos=(1420, 960), desc="Šedé kuličky", size=(190, 100), baseline=40),
        dict(name="Zebrik", tex=PROPS + "ladder_tall.png", pos=(1269, 560), desc="Žebřík na půdu", size=(140, 660),
             baseline=320, visible=False),
        dict(name="Budka", tex=PROPS + "owl_box.png", pos=(1560, 540), desc="Budka pro sovy", size=(180, 220),
             baseline=600, visible=False),
    ] + [dict(name=f"Hrebik{i}", tex=PROPS + "nail.png", pos=(1500 + 60*i, 460), desc="Hřebík", size=(60, 80),
              baseline=700, visible=False) for i in range(1, 4)],
    hotspots=[
        dict(name="Okynko", desc="Okýnko s hvězdičkou", poly=_rect(1269, 219, 180, 180), walk_to=(1269, 880)),
        dict(name="Domu", desc="Do kuchyně", poly=[(0, 560), (110, 560), (110, 1060), (0, 1060)], walk_to=(120, 940)),
    ],
    markers={"Start": (500, 940), "ZeKuchyne": (220, 940), "ZPudy": (1120, 940), "Konec": (1150, 960)},
)

BOARD = 154      # one floor board, px (art/story2.py BOARD_W * 1920)
FIRST = 538      # centre of the board the sunlight star lands on


make_room(
    "Puda", "attic",
    walk=[(60, 880), (1500, 880), (1520, 1060), (40, 1060)],
    props=[
        dict(name="Truhla", tex=PROPS + "chest_closed.png", pos=(250, 840), desc="Truhla se hvězdičkou",
             size=(300, 200), baseline=90),
        dict(name="Sovy", tex=PROPS + "owls_beam.png", pos=(1150, 128), desc="Sovy na trámu", size=(600, 200),
             visible=False, baseline=-300),
        dict(name="Svetlo", tex=PROPS + "star_light.png", pos=(FIRST, 960), desc="Hvězdička ze sluníčka",
             size=(300, 90), visible=False, baseline=-300),
        dict(name="Plechovka", tex=PROPS + "tin_star.png", pos=(FIRST + 7*BOARD, 990), desc="Plechovka se hvězdičkou",
             size=(160, 100), visible=False, baseline=-200),
    ],
    hotspots=[
        dict(name="Okynko", desc="Okýnko s hvězdičkou", poly=_rect(384, 410, 190, 190), walk_to=(400, 940)),
        dict(name="Tram", desc="Trám pod střechou", poly=[(700, 30), (1600, 30), (1600, 250), (700, 250)], walk_to=(1100, 940)),
        dict(name="Dolu", desc="Dolů po žebříku", poly=[(0, 600), (90, 600), (90, 1060), (0, 1060)], walk_to=(120, 960)),
    ] + [dict(name=f"Prkno{i}", desc="Prkno", poly=[(FIRST - BOARD/2 + BOARD*i, 870), (FIRST + BOARD/2 + BOARD*i, 870),
                                                   (FIRST + BOARD/2 + BOARD*i, 1075), (FIRST - BOARD/2 + BOARD*i, 1075)],
              walk_to=(min(FIRST + BOARD*i, 1480), 960)) for i in range(1, 8)],
    markers={"Vstup": (560, 1000)},
)

make_item("Pulmapa", "res://assets/props/map_half.png", "Půlka staré mapy")
make_item("Mapa", "res://assets/props/map_full.png", "Celá mapa ke starému rybníku")
