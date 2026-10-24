#!/usr/bin/env python3
"""Story 7 "Joeyho velký den": rooms and characters (see popochiu_gen.py).

  python3 tools/rooms_story7.py
"""
from popochiu_gen import make_room, make_character, _rect

PROPS = "res://assets/props/"

make_character("Hajny", "hajny", "Pan hajný", 620, "0.2, 0.4, 0.2")

make_room(
    "Zahrada7", "garden7",
    walk=[(40, 790), (1880, 790), (1900, 1060), (20, 1060)],
    props=[
        dict(name="Skrys", tex=PROPS + "stash_open.png", pos=(1580, 800), desc="Joeyho skrýš", size=(400, 160),
             visible=False, baseline=-200),
        dict(name="Prstynek", tex=PROPS + "ring_glint.png", pos=(1230, 760), desc="Prstýnek", size=(160, 160),
             visible=False, baseline=600),
    ],
    hotspots=[
        dict(name="Krmitko", desc="Krmítko", poly=[(580, 430), (740, 430), (740, 860), (580, 860)], walk_to=(660, 900)),
        dict(name="Pevnost", desc="Sněhová pevnost", poly=[(880, 610), (1580, 610), (1580, 790), (880, 790)], walk_to=(1050, 880)),
        dict(name="Kulna", desc="Kůlna na dříví", poly=[(1530, 440), (1910, 440), (1910, 700), (1530, 700)], walk_to=(1560, 860)),
        dict(name="Dum", desc="Domů", poly=[(180, 480), (330, 480), (330, 690), (180, 690)], walk_to=(280, 840)),
        dict(name="KLesu", desc="K hájovně", poly=[(1830, 720), (1920, 720), (1920, 1060), (1830, 1060)], walk_to=(1810, 950)),
    ],
    markers={"Start": (360, 930), "ZLesa": (1700, 950), "Pevnost": (1050, 900)},
)

make_room(
    "Kuchyne7", "kitchen",
    walk=[(40, 790), (1880, 790), (1900, 1060), (20, 1060)],
    hotspots=[
        dict(name="Dvere", desc="Dveře na zahradu", poly=[(1690, 230), (1880, 230), (1880, 756), (1690, 756)], walk_to=(1700, 830)),
        dict(name="Kamna", desc="Kamna", poly=[(58, 360), (328, 360), (328, 756), (58, 756)], walk_to=(380, 850)),
    ],
    markers={"Start": (760, 900), "ZeZahrady": (1620, 880)},
)

make_room(
    "Les7", "forest7",
    walk=[(40, 800), (1880, 800), (1900, 1060), (20, 1060)],
    props=[
        dict(name="Straka", tex=PROPS + "magpie7.png", pos=(1560, 470), desc="Straka", size=(220, 160), baseline=600),
    ],
    hotspots=[
        dict(name="Hajovna", desc="Hájovna", poly=[(260, 420), (760, 420), (760, 710), (260, 710)], walk_to=(500, 860)),
        dict(name="Krmelec", desc="Krmelec", poly=[(1120, 420), (1580, 420), (1580, 720), (1120, 720)], walk_to=(1300, 870)),
        dict(name="Zpet", desc="Zpátky na zahradu", poly=[(0, 560), (90, 560), (90, 1060), (0, 1060)], walk_to=(110, 950)),
    ],
    markers={"Start": (260, 950), "Hajny": (1050, 920)},
)
