# Taak Deel 1

## Conversie rooster - coordinatenstelsel

def rooster_naar_coord(vak_grootte, rooster_pos):
    x_positie = float(rooster_pos[0]*vak_grootte + 0.5*vak_grootte) # de 0.5 is bedoeld om in het midden van het vakje te raken
    y_positie = float(rooster_pos[1]*vak_grootte + 0.5*vak_grootte)
    coordinaten = (x_positie, y_positie)
    return coordinaten


def coord_naar_rooster(vak_grootte, coord_pos):
    x_positie = int(round((coord_pos[0] - 0.5*vak_grootte)/vak_grootte))
    y_positie = int(round((coord_pos[1] - 0.5*vak_grootte)/vak_grootte))
    roostercoordinaten = (x_positie, y_positie)
    return roostercoordinaten



## Meren - voorlopig doe ik  hier niets met het gegeven bodemhoogtes

def is_meer(i, bodemhoogtes, waterniveaus):
    if waterniveaus[i] > 0:
        return True
    else:
        return False

# hulpfunctie-werkt wel alleen als i zich effectief in het meer bevindt
def start_meer(i, bodemhoogtes, waterniveaus):
    if is_meer(i, bodemhoogtes, waterniveaus):
        return start_meer(i-1, bodemhoogtes, waterniveaus)
    else:
        return i+1                                  # tot en met het meer

# hulpfunctie-werkt wel alleen als i zicht effectief in het meer bevindt
def eind_meer(i, bodemhoogtes, waterniveaus):
    if is_meer(i, bodemhoogtes, waterniveaus):
        return eind_meer(i+1, bodemhoogtes, waterniveaus)
    else:
        return i-1                                  # tot en met het meer


def start_eind_meer(i, bodemhoogtes, waterniveaus):
    eindpositie = eind_meer(i, bodemhoogtes, waterniveaus)
    beginpositie = start_meer(i, bodemhoogtes, waterniveaus)
    return (beginpositie, eindpositie)


def aantal_meren(bodemhoogtes, waterniveaus):
    if len(waterniveaus) == 1:
        return 0
    if waterniveaus[0] != 0:
        i2 = eind_meer(0, bodemhoogtes, waterniveaus)
        return 1 + aantal_meren(bodemhoogtes, waterniveaus[i2+1:])
    else: 
        return 0 + aantal_meren(bodemhoogtes, waterniveaus[1:])


def verdamp(i, bodemhoogtes, waterniveaus):
    aantal_water = 0
    (b,e) = start_eind_meer(i, bodemhoogtes, waterniveaus)
    for i in range(b,e+1):                          # we gaan de lijst af van begin meer tot eind meer
        aantal_water += waterniveaus[i]
        waterniveaus[i] = 0
    return aantal_water
    
bodemhoogtes = [1, 1, 4, 1, 2, 5, 1, 1, 2, 1, 3, 1, 2, 1, 2, 1, 1]
waterniveaus = [0, 0, 0, 3, 2, 0, 2, 2, 1, 2, 0, 0, 0, 1, 0, 0, 0]



## Nivelleren van het waterniveau -

def hoogteverschil(i,j, bodemhoogtes, waterniveaus):
    Bi = bodemhoogtes[i]
    Bj = bodemhoogtes[j]
    Wi = waterniveaus[i]
    Wj = waterniveaus[j]
    return (Bi + Wi) - (Bj + Wj)

# op de eerste plaats uiteraard geen drukverschil --> gewoon kijken naar het aanwezige water
def drukverschil_links(i, bodemhoogtes, waterniveaus):
    Wi = waterniveaus[i]
    if i == 0:
        return -1 * Wi
    else:
        hv_l = hoogteverschil(i-1, i, bodemhoogtes, waterniveaus)
        return Wi * hv_l


# op de laatste plaats uiteraard geen drukverschil --> gewoon kijken naar het aanwezige water
def drukverschil_rechts(i, bodemhoogtes, waterniveaus):
    Wi = waterniveaus[i]
    if i == len(waterniveaus)-1:
        return -1 * Wi
    else:
        hv_r = hoogteverschil(i+1, i, bodemhoogtes, waterniveaus)
        return Wi * hv_r


# doorlopen van links naar rechts
def nivellering_links_mogelijk(bodemhoogtes, waterniveaus):
    som_drukverschillen = 0
    for i in range(0, len(waterniveaus)):                         # als de lijst begint op nul dan heeft het laatste element index len(lijst)-1
        delta_p = drukverschil_links(i, bodemhoogtes, waterniveaus)
        if delta_p < 0:
            som_drukverschillen += delta_p
    return bool(som_drukverschillen)




# doorlopen van rechts naar links
def nivellering_rechts_mogelijk(bodemhoogtes, waterniveaus):
    som_drukverschillen = 0
    for i in range(len(waterniveaus)-1,-1,-1):                    # van de laatste plaats tot en met de eerste
        delta_p = drukverschil_rechts(i, bodemhoogtes, waterniveaus)
        if delta_p < 0:
            som_drukverschillen += delta_p
    return bool(som_drukverschillen)



def nivelleer_naar_links(bodemhoogtes, waterniveaus):
    while nivellering_links_mogelijk(bodemhoogtes[1:], waterniveaus[1:]):
        for i, e in enumerate(waterniveaus[1:]):                                        # van het tweede tot en met het laatste element in de lijst
            if drukverschil_links(i, bodemhoogtes[1:], waterniveaus[1:]) < 0:
                waterniveaus[i+1] -= 1                                                  # i is bepaald op de lijst zonder het eerste element, op de oorspronkelijke lijst is dat dus i+1
                waterniveaus[i] += 1


def nivelleer_naar_rechts(bodemhoogtes, waterniveaus):
    while nivellering_rechts_mogelijk(bodemhoogtes[:-1], waterniveaus[:-1]):
        for i in range(len(waterniveaus)-2, -1, -1):                                     # van het voorlaatste tot en met het eerste element in de lijst
            if drukverschil_rechts(i, bodemhoogtes[:-1], waterniveaus[:-1]) < 0:         # de lijsten tot en zonder het laatste element
                waterniveaus[i] -= 1                                                     # het i-de element in de oorspronkelijke element
                waterniveaus[i+1] += 1

def nivelleer(bodemhoogtes, waterniveaus):
    pluviometer = 0
    nivelleer_naar_links(bodemhoogtes, waterniveaus)
    pluviometer += waterniveaus[0]
    waterniveaus[0] = 0
    nivelleer_naar_rechts(bodemhoogtes, waterniveaus)
    pluviometer += waterniveaus[-1]
    waterniveaus[-1] = 0
    for idx, h in enumerate(bodemhoogtes):                                               # dit deel van de functie zorgt voor de nivellering bij een gat in de bodem
        if h == 0:
            if is_meer(idx, bodemhoogtes, waterniveaus):
                pluviometer += verdamp(idx, bodemhoogtes, waterniveaus)
    return pluviometer




bodem = [1, 1, 4, 5, 1, 0, 1, 1, 2, 5, 1, 1, 1]
water = [0, 0, 0, 0, 2, 2, 2, 2, 2, 2, 0, 1, 0]
bodem2 = [1 for i in range(80)]
water2 = [1 for i in range(80)]


