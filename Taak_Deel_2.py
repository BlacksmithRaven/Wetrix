from visual import *
from numpy import *
import random as rand
from Taak_Deel_1 import *
from helpers import *


class Wetrix:
    def __init__(self):
        self.view = WetrixView(self)
        self.afgevloeid = 0
        self.aard = 0
        self.score = 0
        self.items = [Bodem(self), Scorebord(self), UpperBlok(self), Pluviometer(self), Seismograaf(self)]

    def incr_afgevloeid(self, aantal):
        self.afgevloeid += aantal

    def activate(self, item):
        self.items.append(item)

    def deactivate(self, item):
        self.items.remove(item)

    def play(self):
        dt = 0.01
        while self.afgevloeid < 100:
            sleep(dt)
            for itm in self.items[2:]:  # de bodem en het scorebord moeten nooit worden aangepast, behalve bij een botsing (zie verder)
                itm.update(dt)
            if self.aard > 200:
                for i in range(20):
                    if self.items[0].bodemhoogtes[i] > 2:
                        self.items[0].bodemhoogtes[i] -= 2
                for i in range(21, 60):
                    if self.items[0].bodemhoogtes[i] > 1:
                        self.items[0].bodemhoogtes[i] -= 1
                for i in range(61, 80):
                    if self.items[0].bodemhoogtes[i] > 2:
                        self.items[0].bodemhoogtes[i] -= 2
                self.aard = 0
                self.afgevloeid += nivelleer(self.items[0].bodemhoogtes, self.items[0].waterniveaus)
                self.items[0].update()
        print " Game Over, je score bedroeg " + str(self.score) + "!"


class GameItem:
    def __init__(self, game):
        self.game = game
        self.x = 0
        self.y = 0
        self.vakgrootte = 10


class Bodem(GameItem):
    def __init__(self, game):
        GameItem.__init__(self, game)
        self.bodemhoogtes = [1 for _ in range(0, 80)]  # de onderscore omdat we de waarde hier verder toch niet gebruiken
        self.waterniveaus = [0 for _ in range(0, 80)]
        self.view = BodemView(self)

    def update(self):  # geen dt aangezien we die toch nergens voor nodig hebben om de Bodem te updaten
        self.view.update()


class Pluviometer(GameItem):
    def __init__(self, game):
        GameItem.__init__(self, game)
        self.pluvio = self.game.afgevloeid
        self.view = PluvioView(self)

    def update(self, dt):
        self.pluvio = self.game.afgevloeid
        self.view.update()


class Seismograaf(GameItem):
    def __init__(self, game):
        GameItem.__init__(self, game)
        self.seismo = self.game.aard
        self.view = SeismoView(self)

    def update(self, dt):
        self.seismo = self.game.aard
        self.view.update()


class Scorebord(GameItem):
    def __init__(self, game):
        GameItem.__init__(self, game)
        self.score = self.game.score
        self.view = ScoreView(self)

    def update(self):
        self.score = self.game.score
        self.view.update()


class MovingItem(GameItem):
    def __init__(self, game):
        GameItem.__init__(self, game)
        self.snely = 500

    def update(self, dt):
        self.x = self.game.view.venster.mouse.pos[0]
        self.y -= self.snely * dt
        rechtse_blok_pos = self.x + self.vakgrootte * (
                    len(self.vorm) - 1)  # de pos van de meest rechtse blok van een blokkencomplex wordt gedfinieerd als
        if self.game.view.venster.kb.keys:  # de pos van de eerste blok plus (het aantal overige blokken * de vakgrootte)
            toets = self.game.view.venster.kb.getkey()
            if toets == " ":
                self.y -= 40
        if self.x < 5:  # self.x wordt verderop als de meest linkse blok van een blokkencomplex gevormd
            self.x = 5
        if rechtse_blok_pos > 795:
            self.x = 795 - self.vakgrootte * (len(self.vorm) - 1)
        self.view.update()


class UpperBlok(MovingItem):
    def __init__(self, game):
        MovingItem.__init__(self, game)
        self.x = 400
        self.y = 600
        self.vorm = rand.choice(([4, 4, 4], [2, 2, 2], [1, 1, 4, 1, 1], [2, 2, 3, 4, 3, 2, 2], [2, 2, 3, 2, 2],
                                 [3, 1, 1, 1, 1], [5, 5], [1, 1, 1, 1, 1], [5, 1, 1]))
        self.view = BlokView(self, (0.15, 0.50, 0))

    def update(self, dt):
        MovingItem.update(self, dt)
        self.handle_collisions()

    def handle_collisions(self):
        for idx, bodemblok in enumerate(self.game.items[0].view.grondblokjes):
            val_blok = self.view.grote_blok[0]  # de meest linkse blok
            if abs(val_blok.pos[0] - bodemblok.pos[0]) < self.vakgrootte / 2 and (val_blok.pos[1] - bodemblok.height) < 0.1:
                a = 0
                for i in range(idx, idx + len(self.vorm)):
                    self.game.items[0].bodemhoogtes[i] += self.vorm[a]  # de lijst met bodemhoogtes aanpassen
                    a += 1
                self.game.aard += sum(self.vorm)
                self.game.afgevloeid += nivelleer(self.game.items[0].bodemhoogtes, self.game.items[0].waterniveaus)
                self.game.items[0].update()
                self.view.erase()
                self.game.deactivate(self)
                getal = rand.randint(1, 10)  # deze implementatie heeft geen last van vervelende blokken bovenaan
                if getal == 1 or getal == 2:
                    self.game.activate(UpperBlok(self.game))
                elif getal == 3 or getal == 4:
                    self.game.activate(DownerBlok(self.game))
                elif getal == 6 or getal == 7 or getal == 8 or getal == 9:
                    self.game.activate(WaterBlok(self.game))
                else:
                    getal2 = rand.randint(1, 3)
                    if getal2 == 1 or getal2 == 2:
                        self.game.activate(VuurBlok(self.game))
                    else:
                        self.game.activate(BomBlok(self.game))


class WaterBlok(MovingItem):
    def __init__(self, game):
        MovingItem.__init__(self, game)
        self.x = 400
        self.y = 600
        self.vorm = rand.choice(([3, 4, 5, 6, 5, 4, 3], [3, 4, 5, 6, 7, 8, 9, 8, 7, 6, 5, 4, 3], [1, 2, 3, 2, 1], [1, 2, 3, 2, 1], [1, 2, 3, 2, 1], [1, 2, 3, 2, 1]))
        self.view = BlokView(self, (0, 0.1, 0.5))

    def update(self, dt):
        MovingItem.update(self, dt)
        self.handle_colissions()

    def handle_colissions(self):
        for idx, bodemblok in enumerate(self.game.items[0].view.grondblokjes):
            val_blok = self.view.grote_blok[0]
            if abs(val_blok.pos[0] - bodemblok.pos[0]) < self.vakgrootte / 2 and (val_blok.pos[1] - bodemblok.height) < 0.1:
                a = 0
                for i in range(idx, idx + len(self.vorm)):
                    self.game.items[0].waterniveaus[i] += self.vorm[a]
                    a += 1
                self.game.afgevloeid += nivelleer(self.game.items[0].bodemhoogtes, self.game.items[0].waterniveaus)
                self.game.items[0].update()
                self.view.erase()
                self.game.deactivate(self)
                self.game.activate(UpperBlok(self.game))  # na een waterblok komt steeds een grondblok


class DownerBlok(MovingItem):
    def __init__(self, game):
        MovingItem.__init__(self, game)
        self.x = 400
        self.y = 600
        self.vorm = rand.choice(([1, 1, 1, 2], [4, 4, 4], [2, 2, 1], [1, 2, 2, 1], [1, 1, 2, 1, 1]))
        self.view = BlokView(self, color.red)

    def update(self, dt):
        MovingItem.update(self, dt)
        self.handle_colissions()

    def handle_colissions(self):
        for idx, bodemblok in enumerate(self.game.items[0].view.grondblokjes):
            val_blok = self.view.grote_blok[0]
            if abs(val_blok.pos[0] - bodemblok.pos[0]) < self.vakgrootte / 2 and (val_blok.pos[1] - bodemblok.height) < 0.1:
                for i in range(idx, idx + len(self.vorm)):
                    self.game.items[0].bodemhoogtes[i] = 1
                self.game.afgevloeid += nivelleer(self.game.items[0].bodemhoogtes, self.game.items[0].waterniveaus)
                self.game.items[0].update()
                self.view.erase()
                self.game.deactivate(self)
                self.game.activate(UpperBlok(self.game))


class VuurBlok(MovingItem):
    def __init__(self, game):
        MovingItem.__init__(self, game)
        self.x = 400
        self.y = 600
        self.view = VuurView(self)
        self.vorm = [1]

    def update(self, dt):
        MovingItem.update(self, dt)
        self.handle_colissions()

    def handle_colissions(self):
        for idx, bodemblok in enumerate(self.game.items[0].view.grondblokjes):
            if abs(self.x - bodemblok.pos[0]) < self.vakgrootte / 2 and (self.y - bodemblok.height) < 0.1:
                if self.game.items[0].waterniveaus[idx] != 0:
                    am = aantal_meren(self.game.items[0].bodemhoogtes, self.game.items[0].waterniveaus)
                    wb = verdamp(idx, self.game.items[0].bodemhoogtes, self.game.items[0].waterniveaus)
                    self.game.score += (am * wb)
                else:
                    self.game.items[0].bodemhoogtes[idx] = 1
                    for i in range(10):
                        if self.game.items[0].bodemhoogtes[idx + i] >= i+1:
                            self.game.items[0].bodemhoogtes[idx + i] = i+1
                        if self.game.items[0].bodemhoogtes[idx - i] >= i+1:
                            self.game.items[0].bodemhoogtes[idx - i] = i+1
                    self.game.afgevloeid += nivelleer(self.game.items[0].bodemhoogtes, self.game.items[0].waterniveaus)
                self.game.items[0].update()
                self.game.items[1].update()
                self.view.erase()
                self.game.deactivate(self)
                self.game.activate(UpperBlok(self.game))


class BomBlok(MovingItem):
    def __init__(self, game):
        MovingItem.__init__(self, game)
        self.x = 400
        self.y = 600
        self.view = BomView(self)
        self.vorm = [1]

    def update(self, dt):
        MovingItem.update(self, dt)
        self.handle_colissions()

    def handle_colissions(self):
        for idx, bodemblok in enumerate(self.game.items[0].view.grondblokjes):
            if abs(self.x - bodemblok.pos[0]) < self.vakgrootte/2 and (self.y - bodemblok.height) < 0.1:
                self.game.items[0].bodemhoogtes[idx] = 0
                self.game.afgevloeid += nivelleer(self.game.items[0].bodemhoogtes, self.game.items[0].waterniveaus)
                self.game.items[0].update()
                self.view.erase()
                self.game.deactivate(self)
                self.game.activate(WaterBlok(self.game))
# ----------------------------------------------------------------------------------------------------------------------
# View module


class View:
    def __init__(self, owner):
        self.owner = owner
        self.vakgrootte = 10


# initieel is de view gewoon een statisch scherm zonder verandering
class WetrixView(View):
    def __init__(self, owner):
        View.__init__(self, owner)
        self.venster = open_display("Welcome To Wetrix -- This game was made by Lander Goes")
        box(pos=(-5, 5), color=color.red, length=self.vakgrootte, height=self.vakgrootte)  # eindblok links
        box(pos=(805, 5), color=color.red, length=self.vakgrootte, height=self.vakgrootte)  # eindblok rechts


# boxposities refereren naar het midden van de box
class BodemView(View):
    def __init__(self, owner):
        View.__init__(self, owner)
        self.bodemhoogtes = self.owner.bodemhoogtes
        self.waterniveaus = self.owner.waterniveaus
        self.grondblokjes = []
        self.waterblokjes = []
        for i, el in enumerate(self.bodemhoogtes):
            coordpos = rooster_naar_coord(self.vakgrootte, (i, 0))
            blok = box(pos=coordpos, color=(0.15, 0.50, 0), length=self.vakgrootte, height=self.vakgrootte * el)
            blok.pos[1] = blok.height / 2
            self.grondblokjes.append(blok)

    def erase(self):
        for (waterblok, grondblok) in zip(self.waterblokjes, self.grondblokjes):
            waterblok.visible = False
            grondblok.visible = False

    def update(self):
        self.erase()
        self.bodemhoogtes = self.owner.bodemhoogtes
        self.waterniveaus = self.owner.waterniveaus
        self.grondblokjes = []
        self.waterblokjes = []
        for i, el in enumerate(self.bodemhoogtes):
            if el != 0:
                coordpos = rooster_naar_coord(self.vakgrootte, (i, 0))
                blok = box(pos=coordpos, color=(0.15, 0.50, 0), length=self.vakgrootte, height=self.vakgrootte * el)
                blok.pos[1] = blok.height / 2  # height/2 om de y positie in het midden van de blok te krijgen
                self.grondblokjes.append(blok)
            else:
                coordpos = rooster_naar_coord(self.vakgrootte, (i, 0))
                blok = box(pos=coordpos, color=color.black, length=self.vakgrootte, height=self.vakgrootte)
                blok.pos[1] = blok.height/2
                self.grondblokjes.append(blok)
        for i, el in enumerate(self.waterniveaus):
            coordpos = rooster_naar_coord(self.vakgrootte, (i, self.bodemhoogtes[i]))
            blok = box(length=self.vakgrootte, height=self.vakgrootte * el, color=(0, 0.1, 0.5))
            blok.pos[0] = coordpos[0]
            blok.pos[1] = blok.height / 2 + self.bodemhoogtes[i] * self.vakgrootte
            self.waterblokjes.append(blok)


class PluvioView(View):
    def __init__(self, owner):
        View.__init__(self, owner)
        self.grootte = self.owner.pluvio
        self.meter = cylinder(pos=(-5, 10), radius=5, color=vector(0, 0, 0.6))

    def update(self):
        self.grootte = self.owner.pluvio * 6  # de 6 komt van 600/100, schermhoogte/ max aantal blokken
        self.meter.axis = (0, self.grootte, 0)


class SeismoView(View):
    def __init__(self, owner):
        View.__init__(self, owner)
        self.grootte = self.owner.seismo
        self.meter = cylinder(pos=(805, 10), radius=5, color=(0.6, 0.4, 0))

    def update(self):
        self.grootte = self.owner.seismo * 3
        self.meter.axis = (0, self.grootte, 0)


class ScoreView(View):
    def __init__(self, owner):
        View.__init__(self, owner)
        self.score = self.owner.score
        self.bord = text(text="score:    " + str(self.score), pos=(705, 585), height=15, length=15, color=color.white)

    def update(self):
        self.score = self.owner.score
        self.bord.text = "score:    " + str(self.score)


class BlokView(View):
    def __init__(self, owner, kleur):
        View.__init__(self, owner)
        self.vorm = self.owner.vorm
        self.color = kleur
        self.grote_blok = []
        self.x = self.owner.x
        self.y = self.owner.y
        for h in self.vorm:
            positie = (self.x, self.y)
            blok = box(pos=positie, color=self.color, length=self.vakgrootte, height=self.vakgrootte * h)
            self.x += self.vakgrootte
            self.grote_blok.append(blok)
        eerste_blok_xpos = self.grote_blok[0].pos[0] - self.vakgrootte / 2  # vanaf hier constructie positioneringsblok
        laatse_blok_xpos = self.grote_blok[-1].pos[0] + self.vakgrootte / 2
        self.positioneringsblok = curve(pos=[(eerste_blok_xpos, 0), (laatse_blok_xpos, 0)], radius=2)

    def update(self):
        self.x = self.owner.x
        self.y = self.owner.y
        for i, el in enumerate(self.vorm):
            xpositie = self.x
            ypositie = self.y + (self.vakgrootte * el) / 2  # + om de mooie vorm te maken
            self.grote_blok[i].pos = (xpositie, ypositie)
            self.x += self.vakgrootte
        self.positioneringsblok.pos = [(self.grote_blok[0].pos[0] - self.vakgrootte / 2, -3, 0),
                                       (self.grote_blok[-1].pos[0] + self.vakgrootte / 2, -3, 0)]

    def erase(self):  # deze zal zorgen dat we geen rare vormen zien op het scherm eens het blokje zijn taak heeft uitgevoerd
        for blok in self.grote_blok:
            blok.visible = False
            del blok
        self.positioneringsblok.visible = False
        del self.positioneringsblok


class VuurView(View):
    def __init__(self, owner):
        View.__init__(self, owner)
        self.vuurblok = sphere(pos=(self.owner.x, self.owner.y), color=color.orange, radius=self.vakgrootte)

    def update(self):
        self.vuurblok.pos = (self.owner.x, self.owner.y)

    def erase(self):
        self.vuurblok.visible = False
        del self.vuurblok


class BomView(View):
    def __init__(self, owner):
        View.__init__(self, owner)
        self.bomblok = sphere(pos=(self.owner.x, self.owner.y), color=(0.2, 0.2, 0.2), radius=self.vakgrootte)

    def update(self):
        self.bomblok.pos = (self.owner.x, self.owner.y)

    def erase(self):
        self.bomblok.visible = False
        del self.bomblok


Game1 = Wetrix()
Game1.play()
