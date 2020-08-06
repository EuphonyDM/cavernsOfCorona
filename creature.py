from cmu_112_graphics import * # taken from https://www.diderot.one/course/34/chapters/2847/
import os
import item
import random
import pathfinding
import level

class Creature():
    def __init__(self, app, name, spritePath, hp, dmg, ac, row, col):
        self.name = name
        self.app = app
        self.sprite = app.loadImage(spritePath)
        self.basehp = hp
        self.hp = (hp, hp) # current, maximum
        self.basedmg = dmg
        self.dmg = dmg
        self.baseac = ac
        self.ac = ac
        self.row = row
        self.col = col
    
    def damaged(self, damage):
        blocked = random.randint(0, self.ac)
        updatedDamage = damage - blocked
        if updatedDamage < 0: updatedDamage = 0
        self.hp = (self.hp[0] - (updatedDamage), self.hp[1])
        if self.hp[0] <= 0: 
            self.checkDead()
    
    def checkDead(self):
        return

    def scaleSprite(self, squareLen):
        if self.sprite.size[0] != squareLen:
            self.sprite = self.app.scaleImage(self.sprite, squareLen // self.sprite.size[0])

    def move(self, row, col):
        self.row = row
        self.col = col
    
    def render(self, size, rcs, relR, relC, canvas):
        squareLen = size / rcs
        self.scaleSprite(squareLen)
        x = relC * squareLen + squareLen / 2
        y = relR * squareLen + squareLen / 2
        canvas.create_image(x, y, image=ImageTk.PhotoImage(self.sprite))
    
class Player(Creature):
    def __init__(self, app, hp, row, col):
        super().__init__(app, "Player", f"assets{os.sep}1BitPack{os.sep}player.png", hp, 3, 0, row, col)
        self.inventory = []
        self.equips = dict()
        self.effects = []
    
    def checkDead(self):
        if self.hp[0] <= 0: 
            self.app.setActiveMode("lose")
    
    def updateStats(self):
        self.dmg = self.basedmg
        self.ac = self.baseac
        maxhp = self.basehp
        for slot in self.equips:
            wornItem = self.equips[slot]
            if isinstance(wornItem, item.Equip):
                self.dmg += wornItem.dmg
                self.ac += wornItem.ac
                maxhp += wornItem.hp
        self.hp = (self.hp[0] + (maxhp - self.hp[1]), maxhp)
        for effect in self.effects:
            if effect[0][0] == "d":
                self.dmg += int(effect[0][1:])


class Enemy(Creature):
    def __init__(self, app, name, spritePath, hp, row, col, dmg, ac):
        super().__init__(app, name, spritePath, hp, dmg, ac, row, col)
        self.damage = dmg
        self.path = []
    
    def turn(self, lines, enemies, avail):
        pr = self.app.player.row
        pc = self.app.player.col
        dirs = [(0,1), (1, 0), (0, -1), (-1, 0)]
        for r, c in dirs:
            newR = self.row + r
            newC = self.col + c
            if (0 <= newR < len(lines) and 0 <= newC < len(lines[newR]) and
                pr == newR and pc == newC):
                self.app.player.damaged(self.damage)
                return
        if self.path == None or len(self.path) == 0:
            self.path = pathfinding.pathfind(avail, self.row, self.col, pr, pc)
            if self.path != None:
                if len(self.path) > 4:
                    self.path = self.path[:4]
                self.path.pop(0)
        if self.path != None:
            node = self.path.pop(0)
            self.move(node[0], node[1])
    
    def noEnemies(enemies, r, c):
        for e in enemies:
            if e.row == r and e.col == c:
                return False
        return True
    
    def checkDead(self):
        if self.hp[0] <= 0: 
            self.app.levels[self.app.currentLevel].enemies.remove(self)
