#!/usr/bin/env python3
"""Story 12 "Tajemné šipky": rooms (see popochiu_gen.py).

  python3 tools/rooms_story12.py
"""
from popochiu_gen import make_room

PROPS = "res://assets/props/"

make_room(
    "Chalupa12", "yard11",
    walk=[(40, 790), (1880, 790), (1900, 1060), (20, 1060)],
    props=[
        dict(name="Sipka", tex=PROPS + "arrow_dashed.png", pos=(900, 900), desc="Šipka z křídy", size=(360, 140),
             scale=0.8, baseline=-400),
        dict(name="Mouka", tex=PROPS + "flour_patch.png", pos=(260, 810), desc="Mouka na prahu", size=(360, 100),
             scale=0.8, visible=False, baseline=-400),
    ],
    hotspots=[
        dict(name="Kulna", desc="Dědova kůlna", poly=[(1320, 300), (1900, 300), (1900, 690), (1320, 690)], walk_to=(1500, 860)),
        dict(name="Kurnik", desc="Kurník", poly=[(620, 430), (1000, 430), (1000, 690), (620, 690)], walk_to=(800, 860)),
        dict(name="Dum", desc="Babiččina kuchyně", poly=[(120, 470), (330, 470), (330, 690), (120, 690)], walk_to=(260, 860)),
        dict(name="Auto", desc="Domů", poly=[(0, 560), (90, 560), (90, 1060), (0, 1060)], walk_to=(110, 950)),
    ],
    markers={"Start": (560, 940), "Babicka": (420, 900), "Deda": (1300, 920), "Mama": (1140, 1000)},
)

make_room(
    "Ves12", "street12",
    walk=[(40, 770), (1880, 770), (1900, 1060), (20, 1060)],
    props=[
        dict(name="SipkaVysoko", tex=PROPS + "arrow_high.png", pos=(1000, 425), desc="Šipka vysoko na garáži", size=(400, 160),
             scale=0.6, baseline=-200),
        dict(name="SipkaCarkovana", tex=PROPS + "arrow_dashed.png", pos=(640, 1010), desc="Čárkovaná šipka", size=(360, 140),
             scale=0.7, baseline=-400),
        dict(name="SipkaTeckovana", tex=PROPS + "arrow_dotted.png", pos=(1450, 745), desc="Malá tečkovaná šipka", size=(240, 120),
             baseline=-300),
        dict(name="Panak", tex=PROPS + "hopscotch12.png", pos=(1150, 950), desc="Panák z křídy", size=(240, 440),
             scale=0.5, baseline=-400),
        dict(name="Stopy", tex=PROPS + "tracks12.png", pos=(960, 800), desc="Stopy pneumatik", size=(600, 180),
             scale=0.6, baseline=-400),
        dict(name="Sekacka", tex=PROPS + "mower12.png", pos=(1250, 770), desc="Sekačka", size=(220, 200), scale=0.8),
        dict(name="Karticka", tex=PROPS + "card12.png", pos=(1330, 1010), desc="Kartička", size=(140, 100),
             visible=False, baseline=-400),
        dict(name="Hvezda", tex=PROPS + "star_skoc.png", pos=(1150, 880), desc="Papírová hvězda", size=(180, 180),
             scale=0.6, visible=False, baseline=-300),
    ],
    hotspots=[
        dict(name="Garaz", desc="Garáž", poly=[(820, 460), (1170, 460), (1170, 700), (820, 700)], walk_to=(900, 860)),
        dict(name="Branka", desc="Branka do zahrady", poly=[(1500, 600), (1640, 600), (1640, 730), (1500, 730)], walk_to=(1570, 850)),
        dict(name="Dum", desc="Domů", poly=[(270, 430), (380, 430), (380, 650), (270, 650)], walk_to=(330, 820)),
    ],
    markers={"Start": (380, 920), "Tonda": (1000, 1045), "Tata": (720, 880), "Verka": (1700, 1000), "Betka": (1860, 990),
             "Joey": (1440, 860)},
)

make_room(
    "Chodba12", "hall12",
    walk=[(40, 800), (1880, 800), (1900, 1060), (20, 1060)],
    props=[
        dict(name="Kalendar", tex=PROPS + "calendar12.png", pos=(620, 420), desc="Kalendář", size=(240, 280),
             scale=0.8, baseline=-300),
        dict(name="SipkaDvere", tex=PROPS + "arrow_dashed.png", pos=(240, 520), desc="Šipka na dveřích", size=(360, 140),
             scale=0.6, visible=False, baseline=-300),
        dict(name="Hvezda", tex=PROPS + "star_tam.png", pos=(1360, 700), desc="Papírová hvězda", size=(180, 180),
             scale=0.7, visible=False, baseline=-300),
    ],
    hotspots=[
        dict(name="Pokoj", desc="Dveře do pokojíčku", poly=[(90, 195), (390, 195), (390, 790), (90, 790)], walk_to=(300, 880)),
        dict(name="Schody", desc="Pod schody", poly=[(1190, 525), (1520, 525), (1520, 790), (1190, 790)], walk_to=(1200, 880)),
        dict(name="Ven", desc="Ven", poly=[(1840, 800), (1920, 800), (1920, 1060), (1840, 1060)], walk_to=(1800, 950)),
    ],
    markers={"Start": (1650, 940), "Mama": (900, 920), "Rano": (520, 920)},
)

make_room(
    "Zahrada12", "party12",
    walk=[(40, 810), (1880, 810), (1900, 1060), (20, 1060)],
    props=[
        dict(name="Dort", tex=PROPS + "cake12.png", pos=(960, 630), desc="Dort s osmi svíčkami", size=(280, 220),
             scale=0.7, baseline=200),
        dict(name="Darky", tex=PROPS + "presents12.png", pos=(1480, 790), desc="Dárky", size=(400, 160), scale=0.8,
             baseline=-100),
        dict(name="Kresba", tex=PROPS + "gifts12.png", pos=(560, 1030), desc="Hančiny dárky", size=(520, 240),
             scale=0.6, visible=False, baseline=-300),
        dict(name="Kolo", tex=PROPS + "bike12.png", pos=(1450, 1030), desc="Růžové kolo", size=(440, 240),
             visible=False, baseline=-40),
        dict(name="Klobouk", tex=PROPS + "party_hat12.png", pos=(300, 1010), desc="Čepička", size=(100, 120),
             visible=False, baseline=-300),
    ],
    hotspots=[],
    markers={"Start": (960, 1000), "Mama": (1350, 900), "Tata": (1530, 920), "Babicka": (560, 900), "Deda": (360, 920),
             "Tonda": (1720, 900), "Betka": (1870, 930), "Verka": (170, 900), "Joey": (240, 1030)},
)
