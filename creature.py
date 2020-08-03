from cmu_112_graphics import *
import os
import item

class Creature():
    def __init__(self, app, name, spritePath, hp, row, col):
        self.name = name
        self.app = app
        self.sprite = app.loadImage(spritePath)
        self.hp = (hp, hp) # current, maximum
        self.row = row
        self.col = col
    
    def scaleSprite(self, squareLen):
        if self.sprite.size[0] != squareLen:
            self.sprite = self.app.scaleImage(self.sprite, squareLen // self.sprite.size[0])

    def move(self, row, col):
        self.row = row
        self.col = col
    
    def render(self, size, rcs, canvas):
        squareLen = size / rcs
        self.scaleSprite(squareLen)
        x = self.col * squareLen + squareLen / 2
        y = self.row * squareLen + squareLen / 2
        canvas.create_image(x, y, image=ImageTk.PhotoImage(self.sprite))
    
class Player(Creature):
    def __init__(self, app, hp, row, col):
        super().__init__(app, "Player", f"assets{os.sep}1BitPack{os.sep}player.png", hp, row, col)
        self.baseDamage = 3
        self.damage = 3
        self.ac = 0
        self.inventory = []
        self.equips = dict()
    
    def updateStats(self):
        self.damage = self.baseDamage
        self.ac = 0
        for slot in self.equips:
            item = self.equips[slot]
            if isInstance(item, item.Equip):
                self.damage += item.dmg
                self.ac += item.ac

class Enemy(Creature):
    def __init__(self, app, name, spritePath, hp, row, col):
        super().__init__(app, name, spritePath, hp, row, col)