#!/usr/bin/env python3
"""Story 11 "Kam mizí vajíčka?": rooms (see popochiu_gen.py).

  python3 tools/rooms_story11.py
"""
from popochiu_gen import make_room, _rect

PROPS = "res://assets/props/"

make_room(
    "Dvur11", "yard11",
    walk=[(40, 790), (1880, 790), (1900, 1060), (20, 1060)],
    props=[
        dict(name="Slepice", tex=PROPS + "hens11.png", pos=(860, 820), desc="Slepičky", size=(760, 240), baseline=-60),
        dict(name="Kropenatka", tex=PROPS + "kropenatka_puff.png", pos=(1240, 880), desc="Kropenatka", size=(240, 200), baseline=-60),
        dict(name="PsiStopy", tex=PROPS + "dog_prints11.png", pos=(880, 1010), desc="Stopy u plotu", size=(440, 120), baseline=-300),
        dict(name="Pirko", tex=PROPS + "feather_prints.png", pos=(1180, 760), desc="Pírko a stopičky", size=(480, 140),
             visible=False, baseline=-300),
        dict(name="Straka", tex="res://assets/characters/magpie.png", pos=(1200, 300), desc="Straka na stromě", size=(220, 160),
             baseline=600),
    ],
    hotspots=[
        dict(name="Kurnik", desc="Kurník", poly=[(620, 430), (1000, 430), (1000, 690), (620, 690)], walk_to=(800, 860)),
        dict(name="Stodola", desc="Stodola", poly=[(1320, 300), (1900, 300), (1900, 690), (1320, 690)], walk_to=(1500, 860)),
        dict(name="Mezera", desc="Dírka pod pletivem", poly=[(1030, 640), (1130, 640), (1130, 750), (1030, 750)], walk_to=(1080, 840)),
        dict(name="Dum", desc="Domů", poly=[(120, 470), (330, 470), (330, 690), (120, 690)], walk_to=(240, 840)),
    ],
    markers={"Start": (330, 940), "Babicka": (1580, 1000), "Tonda": (1800, 990)},
)

make_room(
    "Kurnik11", "henhouse11",
    walk=[(40, 800), (1880, 800), (1900, 1060), (20, 1060)],
    props=[
        dict(name="Vajicka", tex=PROPS + "eggs7.png", pos=(1540, 640), desc="Vajíčka", size=(600, 120), baseline=600),
    ],
    hotspots=[
        dict(name="Hnizda", desc="Hnízda s hoblinami", poly=[(1300, 520), (1810, 520), (1810, 730), (1300, 730)], walk_to=(1500, 880)),
        dict(name="Ven", desc="Ven", poly=[(0, 560), (90, 560), (90, 1060), (0, 1060)], walk_to=(110, 950)),
    ],
    markers={"Start": (300, 950)},
)

make_room(
    "Stodola11", "barn11",
    walk=[(40, 800), (1880, 800), (1900, 1060), (20, 1060)],
    props=[
        dict(name="Hnizdo", tex=PROPS + "nest11.png", pos=(1270, 830), desc="Tajné hnízdo", size=(400, 240), visible=False, baseline=100),
    ],
    hotspots=[
        dict(name="Baliky", desc="Balíky slámy", poly=[(1150, 100), (1920, 100), (1920, 680), (1150, 680)], walk_to=(1100, 880)),
        dict(name="Skvira", desc="Tmavá škvíra mezi balíky", poly=[(1180, 690), (1360, 690), (1360, 800), (1180, 800)], walk_to=(1150, 880)),
        dict(name="Ven", desc="Ven", poly=[(0, 560), (90, 560), (90, 1060), (0, 1060)], walk_to=(110, 950)),
    ],
    markers={"Start": (300, 950), "Babicka": (600, 940), "Verka": (900, 940)},
)

make_room(
    "Kuchyne11", "kitchen",
    walk=[(40, 790), (1880, 790), (1900, 1060), (20, 1060)],
    props=[
        dict(name="Kraslice", tex=PROPS + "kraslice_row.png", pos=(520, 590), desc="Kraslice", size=(600, 140), baseline=600),
    ],
    hotspots=[
        dict(name="Dvere", desc="Dveře na dvůr", poly=[(1690, 230), (1880, 230), (1880, 756), (1690, 756)], walk_to=(1700, 830)),
    ],
    markers={"Start": (760, 900), "ZeDvora": (1620, 880)},
)
