#!/usr/bin/env python3
"""Story 6 "Kam mizí perníčky?": rooms and items (see popochiu_gen.py).

  python3 tools/rooms_story6.py
"""
from popochiu_gen import make_room, make_item, _rect

PROPS = "res://assets/props/"

make_room(
    "Kuchyne6", "kitchen6",
    walk=[(40, 800), (1880, 800), (1900, 1060), (20, 1060)],
    props=[
        dict(name="Tac", tex=PROPS + "tray_pecked.png", pos=(800, 560), desc="Plech na parapetu", size=(320, 120), baseline=600),
        dict(name="Sykorky", tex=PROPS + "tits.png", pos=(900, 530), desc="Sýkorky", size=(400, 140), visible=False, baseline=600),
        dict(name="Stopicky", tex=PROPS + "bird_prints.png", pos=(1000, 580), desc="Stopičky na parapetu", size=(280, 60),
             visible=False, baseline=600),
        dict(name="Plechovka", tex=PROPS + "tin_shelf.png", pos=(1470, 470), desc="Plechovka s perníčky", size=(260, 140), baseline=600),
        dict(name="Tlapky", tex=PROPS + "paws_flour.png", pos=(1230, 900), desc="Moučné tlapky", size=(600, 140),
             visible=False, baseline=-300),
        dict(name="Past", tex=PROPS + "mousetrap.png", pos=(1300, 830), desc="Past na myši", size=(180, 80), visible=False,
             baseline=-200),
        dict(name="Boty", tex=PROPS + "deda_boots_needles.png", pos=(1540, 900), desc="Dědovy boty", size=(280, 220), baseline=-100),
        dict(name="Sacek", tex=PROPS + "piping_bag.png", pos=(700, 600), desc="Sáček na polevu", size=(160, 100),
             visible=False, baseline=600),
        dict(name="Fotka", tex=PROPS + "club_photo7.png", pos=(1480, 230), desc="Fotka Klubu Hvězdička", size=(340, 240), baseline=600),
    ],
    hotspots=[
        dict(name="Okno", desc="Okno", poly=[(580, 110), (1075, 110), (1075, 520), (580, 520)], walk_to=(830, 860)),
        dict(name="Kamna", desc="Kamna", poly=[(40, 410), (326, 410), (326, 790), (40, 790)], walk_to=(400, 880)),
        dict(name="Dvere", desc="Dveře na zahradu", poly=[(1690, 170), (1882, 170), (1882, 790), (1690, 790)], walk_to=(1700, 880)),
    ],
    markers={"Start": (760, 920), "ZeZahrady": (1720, 1000), "Okno": (830, 860), "Spiz": (1450, 880)},
)

make_room(
    "Zahrada6", "garden5",
    walk=[(40, 780), (1880, 780), (1900, 1060), (20, 1060)],
    props=[
        dict(name="Krmitko", tex=PROPS + "feeder.png", pos=(980, 790), desc="Krmítko", size=(280, 440), visible=False, baseline=200),
    ],
    hotspots=[
        dict(name="Misto", desc="Místo pod oknem", poly=[(860, 760), (1100, 760), (1100, 900), (860, 900)], walk_to=(800, 900)),
        dict(name="Dum", desc="Do kuchyně", poly=[(240, 520), (420, 520), (420, 740), (240, 740)], walk_to=(330, 840)),
        dict(name="KMlynu", desc="Ke mlýnu", poly=[(1830, 560), (1920, 560), (1920, 1060), (1830, 1060)], walk_to=(1810, 950)),
    ],
    markers={"Start": (420, 900), "ZMlyna": (1700, 950)},
)

make_room(
    "Mlyn6", "mill6",
    walk=[(40, 790), (1880, 790), (1900, 1060), (20, 1060)],
    props=[
        dict(name="Zebrik", tex=PROPS + "ladder6.png", pos=(1380, 560), desc="Žebřík", size=(120, 520), baseline=300),
        dict(name="NoveHvezdy", tex=PROPS + "new_stars.png", pos=(1120, 420), desc="Nové hvězdičky", size=(400, 280),
             visible=False, baseline=600),
        dict(name="Zrnicka", tex=PROPS + "seed_stars.png", pos=(1180, 620), desc="Zrníčkové hvězdy pro ptáčky", size=(440, 240),
             visible=False, baseline=600),
    ],
    hotspots=[
        dict(name="Smrk", desc="Velký smrk", poly=[(900, 60), (1400, 60), (1400, 740), (900, 740)], walk_to=(1000, 870)),
        dict(name="Mlyn", desc="Mlýn", poly=[(120, 300), (560, 300), (560, 740), (120, 740)], walk_to=(400, 870)),
        dict(name="Zpet", desc="Domů", poly=[(0, 560), (90, 560), (90, 1060), (0, 1060)], walk_to=(110, 950)),
    ],
    markers={"Start": (260, 950), "Deda": (1500, 900), "Franta": (1720, 920), "Verka": (820, 930), "Betka": (560, 960)},
)
