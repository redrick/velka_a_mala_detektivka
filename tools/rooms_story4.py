#!/usr/bin/env python3
"""Story 4 "Hanka to vyřeší!": rooms, characters and items (see popochiu_gen.py).

  python3 tools/rooms_story4.py
"""
from popochiu_gen import make_room, make_item, make_character, _rect

PROPS = "res://assets/props/"
FLOOR = [(40, 800), (1880, 800), (1900, 1060), (20, 1060)]

make_character("Kostelnik", "kostelnik", "Pan kostelník", 600, "0.2, 0.22, 0.3")

make_room(
    "Pokoj4", "sickroom4",
    walk=FLOOR,
    props=[
        dict(name="Plechovka", tex=PROPS + "tin_open4.png", pos=(760, 470), desc="Plechovka", size=(280, 200),
             visible=False, baseline=400),
        dict(name="Pistalka", tex=PROPS + "hen_whistle.png", pos=(560, 300), desc="Píšťalka slepička", size=(160, 100),
             visible=False, baseline=500),
        dict(name="Kulicky", tex=PROPS + "marbles.png", pos=(760, 260), desc="Kuličky", size=(120, 80),
             visible=False, baseline=500),
        dict(name="Klic", tex=PROPS + "clock_key.png", pos=(960, 300), desc="Velký železný klíč", size=(220, 100),
             visible=False, baseline=500),
        dict(name="Dopis", tex=PROPS + "new_letter.png", pos=(1180, 300), desc="Nový obrázkový dopis", size=(300, 220),
             visible=False, baseline=500),
    ],
    hotspots=[
        dict(name="Dvere", desc="Dveře ven", poly=[(1650, 170), (1862, 170), (1862, 790), (1650, 790)], walk_to=(1700, 880)),
        dict(name="Okno", desc="Okno", poly=[(115, 130), (500, 130), (500, 540), (115, 540)], walk_to=(320, 880)),
        dict(name="Stolek", desc="Čaj a kapesníky", poly=[(660, 480), (900, 480), (900, 800), (660, 800)], walk_to=(760, 880)),
    ],
    markers={"Start": (900, 950), "ZVsi": (1650, 930), "Postel": (1230, 935)},
)

make_room(
    "Ves4", "village4",
    walk=[(40, 780), (1880, 780), (1900, 1060), (20, 1060)],
    props=[
        dict(name="Stopy", tex=PROPS + "zig_prints.png", pos=(400, 900), desc="Obří stopy", size=(300, 160),
             visible=False, baseline=-200),
    ],
    hotspots=[
        dict(name="StaryKurnik", desc="Starý kurník", poly=[(420, 540), (700, 540), (700, 760), (420, 760)], walk_to=(560, 850)),
        dict(name="Kurnik", desc="Kurník", poly=[(730, 480), (1000, 480), (1000, 760), (730, 760)], walk_to=(860, 860)),
        dict(name="Hodiny", desc="Hodiny na věži", poly=[(1390, 110), (1530, 110), (1530, 245), (1390, 245)], walk_to=(1460, 850)),
        dict(name="Kostel", desc="Kostel", poly=[(1380, 255), (1900, 255), (1900, 740), (1380, 740)], walk_to=(1500, 850)),
        dict(name="Lavicka", desc="Lavička", poly=[(1030, 690), (1280, 690), (1280, 820), (1030, 820)], walk_to=(1150, 890)),
        dict(name="Domu", desc="Domů", poly=[(0, 560), (90, 560), (90, 1060), (0, 1060)], walk_to=(110, 950)),
        dict(name="KPoli", desc="Na pole", poly=[(1830, 560), (1920, 560), (1920, 1060), (1830, 1060)], walk_to=(1810, 950)),
    ],
    markers={"Start": (260, 950), "ZPole": (1700, 950), "Kostelnik": (1600, 830), "Deda": (1170, 1000),
             "Babicka": (1310, 950), "Lavicka": (1150, 870)},
)

make_room(
    "Pole4", "field4",
    walk=[(40, 810), (1880, 810), (1900, 1060), (20, 1060)],
    props=[
        dict(name="Straka", tex=PROPS + "magpie_fly.png", pos=(1220, 560), desc="Straka", size=(180, 120), baseline=600),
        dict(name="Obal", tex=PROPS + "wrapper.png", pos=(980, 900), desc="Obal od bonbonu", size=(80, 50),
             visible=False, baseline=-100),
        dict(name="Splavek", tex=PROPS + "splavek.png", pos=(1120, 880), desc="Splávek", size=(80, 100),
             visible=False, baseline=-100),
        dict(name="StopyB", tex=PROPS + "zig_prints.png", pos=(1300, 900), desc="Obří stopy", size=(300, 160),
             visible=False, baseline=-200),
        dict(name="Plechovka", tex=PROPS + "tin_closed.png", pos=(1420, 790), desc="Plechovka", size=(240, 160),
             visible=False, baseline=100),
    ],
    hotspots=[
        dict(name="Bota", desc="Velký kámen", poly=[(1040, 560), (1370, 560), (1370, 790), (1040, 790)], walk_to=(1200, 880)),
        dict(name="Skulina", desc="Škvíra u kamene", poly=[(1370, 700), (1480, 700), (1480, 800), (1370, 800)], walk_to=(1420, 880)),
        dict(name="Kamen1", desc="Kámen", poly=[(500, 690), (660, 690), (660, 790), (500, 790)], walk_to=(580, 880)),
        dict(name="Kamen2", desc="Kámen", poly=[(810, 640), (920, 640), (920, 720), (810, 720)], walk_to=(860, 860)),
        dict(name="Kamen3", desc="Kámen", poly=[(1560, 720), (1685, 720), (1685, 830), (1560, 830)], walk_to=(1620, 900)),
        dict(name="Potok", desc="Potok", poly=[(0, 600), (1035, 600), (1035, 690), (925, 690), (925, 636), (805, 636), (805, 690),
                                               (0, 690)], walk_to=(700, 860)),
        dict(name="DoVsi", desc="Do vsi", poly=[(0, 560), (90, 560), (90, 1060), (0, 1060)], walk_to=(110, 950)),
        dict(name="KRybniku", desc="K rybníku", poly=[(1830, 560), (1920, 560), (1920, 1060), (1830, 1060)], walk_to=(1810, 950)),
    ],
    markers={"Start": (260, 950), "ZMola": (1700, 950), "Bota": (1220, 900)},
)

make_room(
    "Molo4", "jetty4",
    walk=[(40, 790), (1880, 790), (1900, 1060), (20, 1060)],
    hotspots=[
        dict(name="Molo", desc="Molo", poly=[(960, 640), (1390, 640), (1390, 760), (960, 760)], walk_to=(1100, 860)),
        dict(name="Zpet", desc="Zpátky", poly=[(0, 560), (90, 560), (90, 1060), (0, 1060)], walk_to=(110, 950)),
    ],
    markers={"Start": (300, 950), "Rybar": (1200, 840), "Deda": (700, 940), "Verka": (520, 960)},
)

make_item("Vysilacka", PROPS + "radio_icon.png", "Vysílačka")
make_item("Plechovka", PROPS + "tin_icon.png", "Plechovka se hvězdičkou")
make_item("NovyDopis", PROPS + "newletter_icon.png", "Nový obrázkový dopis")
make_item("KlicHodin", PROPS + "clockkey_icon.png", "Velký železný klíč")
