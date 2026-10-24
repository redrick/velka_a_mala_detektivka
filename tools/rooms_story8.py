#!/usr/bin/env python3
"""Story 8 "Stopy ve sněhu": rooms and items (see popochiu_gen.py).

  python3 tools/rooms_story8.py
"""
from popochiu_gen import make_room, make_item, _rect

PROPS = "res://assets/props/"
FAMILY_POLY = [(-520, -130), (520, -130), (520, 420), (-520, 420)]

make_room(
    "Zahrada8", "garden5",
    walk=[(40, 780), (1880, 780), (1900, 1060), (20, 1060)],
    props=[
        dict(name="Snehulaci", tex=PROPS + "family_none.png", pos=(1060, 640), desc="Sněhulácká rodina", size=(1120, 880),
             baseline=250, poly=FAMILY_POLY),
        dict(name="Pahyl", tex=PROPS + "stub_frayed.png", pos=(760, 1000), desc="Kousek nosu", size=(100, 80), baseline=-300),
        dict(name="Stopy", tex=PROPS + "prints_trampled.png", pos=(1300, 990), desc="Pošlapané stopy", size=(600, 160),
             baseline=-300),
        dict(name="CisteStopy", tex=PROPS + "prints_clean.png", pos=(1320, 980), desc="Stopy na čistém sněhu",
             size=(640, 140), visible=False, baseline=-300),
    ],
    hotspots=[
        dict(name="Dum", desc="Domů do kuchyně", poly=[(240, 520), (420, 520), (420, 740), (240, 740)], walk_to=(330, 840)),
        dict(name="NaLouku", desc="Na louku", poly=[(1830, 560), (1920, 560), (1920, 1060), (1830, 1060)], walk_to=(1810, 950)),
    ],
    markers={"Start": (420, 940), "ZLouky": (1700, 950), "Hajny": (1600, 920), "Tonda": (650, 960)},
)

make_room(
    "Louka8", "meadow8",
    walk=[(40, 800), (1880, 800), (1900, 1060), (20, 1060)],
    props=[
        dict(name="Zajic", tex=PROPS + "hare_sit.png", pos=(560, 760), desc="Zajíc", size=(180, 180), baseline=100),
        dict(name="Liska", tex=PROPS + "fox_pounce.png", pos=(1000, 740), desc="Liška", size=(400, 240), visible=False,
             baseline=100),
        dict(name="Divocak", tex=PROPS + "boar_root.png", pos=(1420, 740), desc="Divočák", size=(440, 260), baseline=100),
    ],
    hotspots=[
        dict(name="ZajiciStopy", desc="Stopy jako Y", poly=[(60, 660), (600, 660), (600, 760), (60, 760)], walk_to=(350, 860)),
        dict(name="LisciStopy", desc="Stopy v řadě", poly=[(660, 700), (1060, 700), (1060, 790), (660, 790)], walk_to=(860, 860)),
        dict(name="Dub", desc="Starý dub", poly=[(1200, 150), (1620, 150), (1620, 700), (1200, 700)], walk_to=(1380, 860)),
        dict(name="Zpet", desc="Zpátky na zahradu", poly=[(0, 560), (90, 560), (90, 1060), (0, 1060)], walk_to=(110, 950)),
        dict(name="DoLesa", desc="Do lesa", poly=[(1830, 560), (1920, 560), (1920, 1060), (1830, 1060)], walk_to=(1810, 950)),
    ],
    markers={"Start": (260, 950), "ZLesa": (1700, 950), "Hajny": (1050, 1040)},
)

make_room(
    "Les8", "forest8",
    walk=[(40, 800), (1880, 800), (1900, 1060), (20, 1060)],
    props=[
        dict(name="Loze", tex=PROPS + "deer_bed.png", pos=(1340, 790), desc="Ovál ve sněhu", size=(280, 100),
             visible=False, baseline=-100),
        dict(name="Srnka", tex=PROPS + "deer_stand.png", pos=(1560, 800), desc="Srnka", size=(480, 400),
             visible=False, baseline=200),
        dict(name="Jidlo", tex=PROPS + "krmelec_food.png", pos=(620, 760), desc="Mrkev, jablka a řepa", size=(320, 120),
             visible=False, baseline=100),
    ],
    hotspots=[
        dict(name="Krmelec", desc="Krmelec", poly=[(400, 380), (860, 380), (860, 720), (400, 720)], walk_to=(620, 870)),
        dict(name="Smrcek", desc="Nízký smrček", poly=[(1150, 420), (1560, 420), (1560, 760), (1150, 760)], walk_to=(1250, 880)),
        dict(name="Zpet", desc="Zpátky na louku", poly=[(0, 560), (90, 560), (90, 1060), (0, 1060)], walk_to=(110, 950)),
    ],
    markers={"Start": (260, 950), "Hajny": (900, 930)},
)

make_room(
    "Kuchyne8", "kitchen",
    walk=[(40, 790), (1880, 790), (1900, 1060), (20, 1060)],
    hotspots=[
        dict(name="Dvere", desc="Dveře na zahradu", poly=[(1690, 230), (1880, 230), (1880, 756), (1690, 756)], walk_to=(1700, 830)),
        dict(name="Okno", desc="Okno", poly=[(690, 150), (1115, 150), (1115, 440), (690, 440)], walk_to=(900, 820)),
    ],
    markers={"Start": (760, 900), "ZeZahrady": (1620, 880)},
)

make_item("Pahyl", PROPS + "stub_icon.png", "Kousek nosu")
