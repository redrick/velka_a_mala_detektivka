#!/usr/bin/env python3
"""Story 3 "Mapa ke starému rybníku": rooms, characters and items (see popochiu_gen.py).

  python3 tools/rooms_story3.py
"""
from popochiu_gen import make_room, make_item, make_character, _rect

PROPS = "res://assets/props/"

make_character("Verka", "verka", "Paní s kloboukem", 580, "0.18, 0.45, 0.43")
make_character("Rybar", "rybar", "Rybář", 620, "0.25, 0.32, 0.18")

make_room(
    "Kuchyne3", "kitchen",
    walk=[(40, 790), (1880, 790), (1900, 1060), (20, 1060)],
    props=[dict(name="MapaStul", tex=PROPS + "map_full.png", pos=(960, 560), desc="Mapa na stole", size=(260, 180))],
    hotspots=[
        dict(name="Dvere", desc="Dveře ven", poly=[(1690, 230), (1880, 230), (1880, 756), (1690, 756)], walk_to=(1700, 830)),
        dict(name="Okno", desc="Okno", poly=[(690, 150), (1115, 150), (1115, 440), (690, 440)], walk_to=(900, 820)),
        dict(name="Kamna", desc="Kamna", poly=[(58, 360), (328, 360), (328, 756), (58, 756)], walk_to=(380, 850)),
    ],
    markers={"Start": (760, 900), "ZRybnika": (1620, 880)},
)

make_room(
    "Rybnik", "pond",
    walk=[(40, 770), (1880, 770), (1900, 1060), (20, 1060)],
    props=[
        dict(name="Kamen", tex=PROPS + "star_stone.png", pos=(1500, 1000), desc="Kámen s hvězdičkou", size=(200, 100),
             visible=False, baseline=-100),
        dict(name="Dira", tex=PROPS + "hole_empty.png", pos=(1700, 985), desc="Díra v zemi", size=(300, 130),
             visible=False, baseline=-100),
        dict(name="Stopy", tex=PROPS + "prints_mud.png", pos=(1290, 990), desc="Stopy v bahně", size=(320, 180),
             visible=False, baseline=-100),
        dict(name="Nora", tex=PROPS + "burrow.png", pos=(420, 800), desc="Díra ve svahu", size=(240, 110), baseline=-50),
    ],
    hotspots=[
        dict(name="Vrba1", desc="Vrba", poly=_rect(230, 520, 330, 420), walk_to=(300, 900)),
        dict(name="Vrba2", desc="Vrba", poly=_rect(691, 540, 240, 330), walk_to=(700, 880)),
        dict(name="Vrba3", desc="Vrba", poly=_rect(1536, 520, 320, 420), walk_to=(1500, 900)),
        dict(name="Parez", desc="Pařez", poly=_rect(1075, 830, 190, 120), walk_to=(1075, 930)),
        dict(name="Domu", desc="Domů", poly=[(0, 560), (90, 560), (90, 1060), (0, 1060)], walk_to=(110, 950)),
        dict(name="KMlynu", desc="Ke mlýnu", poly=[(1830, 560), (1920, 560), (1920, 1060), (1830, 1060)], walk_to=(1810, 950)),
    ],
    markers={"Start": (260, 950), "ZMlyna": (1720, 950), "Parez": (1075, 940), "Kamen": (1400, 960)},
)

make_room(
    "Mlyn", "mill_yard",
    walk=[(40, 800), (1880, 800), (1900, 1060), (20, 1060)],
    props=[
        dict(name="Lucerna", tex=PROPS + "lantern_lit.png", pos=(1280, 630), desc="Lucerna na okně", size=(100, 130), scale=0.8),
        dict(name="Hul", tex=PROPS + "stick_lean.png", pos=(700, 810), desc="Hůlka", size=(90, 300), baseline=150),
        dict(name="Plechovka", tex=PROPS + "tin_open.png", pos=(600, 830), desc="Plechovka se hvězdičkou",
             size=(320, 220), visible=False, baseline=300),
        dict(name="Tolar", tex=PROPS + "coin_shine.png", pos=(700, 330), desc="Stříbrný tolar", size=(220, 220), visible=False, baseline=400),
        dict(name="Dalekohled", tex=PROPS + "spyglass.png", pos=(1240, 330), desc="Dalekohled", size=(260, 80), visible=False, baseline=400),
        dict(name="Fotka", tex=PROPS + "club_photo.png", pos=(960, 330), desc="Stará fotka", size=(260, 200), visible=False, baseline=400),
        dict(name="Odznak", tex=PROPS + "badge.png", pos=(830, 480), desc="Odznak se hvězdičkou", size=(80, 80), visible=False, baseline=400),
        dict(name="Dopis", tex=PROPS + "picture_letter.png", pos=(1100, 500), desc="Obrázkový dopis", size=(300, 220), visible=False, baseline=400),
    ],
    hotspots=[
        dict(name="Lavicka", desc="Lavička", poly=_rect(576, 890, 270, 130), walk_to=(760, 970)),
        dict(name="Dvere", desc="Dveře mlýnku", poly=[(1086, 594), (1142, 594), (1142, 756), (1086, 756)], walk_to=(1110, 880)),
        dict(name="Zpet", desc="K rybníku", poly=[(0, 560), (90, 560), (90, 1060), (0, 1060)], walk_to=(110, 950)),
    ],
    markers={"Start": (900, 970), "Verka": (300, 960)},
)

make_item("Dopis", "res://assets/props/letter_icon.png", "Frantův obrázkový dopis")
