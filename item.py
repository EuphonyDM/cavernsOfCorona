from cmu_112_graphics import * # taken from https://www.diderot.one/course/34/chapters/2847/

class Item:
    def __init__(self, app, name, spritePath):
        self.app = app
        self.name = name
        self.sprite = app.loadImage(spritePath)

    def scaleSprite(self, squareLen):
        if self.sprite.size[0] != squareLen:
            self.sprite = self.app.scaleImage(self.sprite, squareLen / self.sprite.size[0])
    
    def render(self, row, col, squareLen, canvas):
        self.scaleSprite(squareLen)
        x = col * squareLen + squareLen / 2
        y = row * squareLen + squareLen / 2
        canvas.create_image(x, y, image=ImageTk.PhotoImage(self.sprite))

class Equip(Item):
    def __init__(self, app, name, spritePath, effects, slot):
        super().__init__(app, name, spritePath)
        self.slot = slot
        self.dmg = 0
        self.ac = 0
        self.hp = 0
        for effect in effects.split(","):
            effectType = effect[0]
            power = int(effect[1:])
            if effectType == "d":
                self.dmg += power
            if effectType == "a":
                self.ac += power
            if effectType == "h":
                self.hp += power