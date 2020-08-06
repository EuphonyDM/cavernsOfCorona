from cmu_112_graphics import * # taken from https://www.diderot.one/course/34/chapters/2847/

class Item:
    def __init__(self, app, name, spritePath):
        self.app = app
        self.name = name
        self.sprite = app.app.loadImage(spritePath)

    def scaleSprite(self, squareLen):
        if self.sprite.size[0] != squareLen:
            self.sprite = self.app.app.scaleImage(self.sprite, squareLen / self.sprite.size[0])
    
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

class Consumable(Item):
    def __init__(self, app, name, spritePath, effects):
        super().__init__(app, name, spritePath)
        self.effects = effects.split(",")
    
    def use(self, player):
        for effect in self.effects:
            e0 = effect[0]
            if e0 == "h":
                hp, mhp = player.hp
                hp += int(effect[1:])
                if hp > mhp: hp = mhp
                player.hp = (hp, mhp)
            if e0 == "d":
                self.app.player.effects.append((effect[:3], int(effect[3:])))
                self.app.player.updateStats
                


def genItem(app, name):
    if name == "Crown":
        return Item(app, "Crystal Crown", f"assets{os.sep}1BitPack{os.sep}crown.png")
    if name == "Sword":
        return Equip(app, "Sword", f"assets{os.sep}1BitPack{os.sep}sword.png", "d3", "main")
    if name == "Helmet":
        return Equip(app, "Helmet", f"assets{os.sep}1BitPack{os.sep}helmet.png", "a2", "head")
    if name == "Health Ring":
        return Equip(app, "Ring of Health", f"assets{os.sep}1BitPack{os.sep}ring.png", "h5", "ring")
    if name == "Health Pot":
        return Consumable(app, "Health Potion", f"assets{os.sep}1BitPack{os.sep}potion.png", "h5")
    if name == "Sharpening Kit":
        return Consumable(app, "Sharpening Kit", f"assets{os.sep}1BitPack{os.sep}kit.png", "d0210")
