# Contains the main Caverns app and all of its modes

from cmu_112_graphics import * # taken from https://www.diderot.one/course/34/chapters/2847/
import level
import creature
import item

class Caverns(ModalApp):
    def appStarted(self):
        self.setSize(640, 480)
        self.player = creature.Player(self, 10, 2, 2)
        self.levels = []
        self.levels.append(level.Level(self, self.player))
        self.currentLevel = 0
        self.turns = 0
        self.addMode(StartMode(name="start"))
        self.addMode(GameMode(name="game"))
        self.addMode(Inventory(name="inv"))
        self.addMode(Win(name="win"))
        self.addMode(Lose(name="lose"))
        self.setActiveMode('start')

class StartMode(Mode):
    def start(self):
        self.setActiveMode("game")
    
    def redrawAll(self, canvas):
        canvas.create_rectangle(0, 0, self.width, self.height, fill="#220000")
        canvas.create_text(self.width / 2, self.height/2 - 60, text="Caverns of Corona", font="Mono 32", fill="white")
        canvas.create_rectangle(self.width / 2 - 100, self.height / 2, self.width / 2 + 100, self.height / 2 + 60, 
                                fill="white", width=0, onClick=self.start)
        canvas.create_text(self.width/2, self.height/2 + 30, text="New Game", font="Mono 20", fill="black")

class GameMode(Mode):
    def appStarted(self):
        self.player = self.app.player
        self.levels = self.app.levels
        self.currentLevel = self.app.currentLevel
    
    def keyPressed(self, event):
        if event.key == "i":
            self.setActiveMode("inv")
        self.levels[self.currentLevel].keyPressed(event)
    
    def timerFired(self):
        self.levels[self.currentLevel].timerFired()
    
    def redrawAll(self, canvas):
            canvas.create_rectangle(self.height, 0, self.width, self.height, fill="gray16")
            textX = (self.height + self.width) / 2
            canvas.create_text(textX, 40, text=f"HP: {self.player.hp[0]}/{self.player.hp[1]}", fill="white", font="Mono 14")
            canvas.create_text(textX, 80, text=f"Damage: {self.player.dmg}", fill="white", font="Mono 14")
            canvas.create_text(textX, 120, text=f"AC: {self.player.ac}", fill="white", font="Mono 14")
            canvas.create_text(textX, self.height - 40, text=f"Row: {self.player.row} Col: {self.player.col}", fill="white", font="Mono 12")
            self.levels[self.currentLevel].render(self.height, canvas)

class Inventory(Mode):
    def modeActivated(self):
        self.selected = 0
        self.color = "gray45"
        self.startIndex = 0
        self.inv = self.app.player.inventory
    
    def keyPressed(self, event):
        if event.key == "Escape" or event.key == "i":
            self.setActiveMode("game")
        if event.key == "Up":
            if self.selected > 0: self.selected -= 1
            elif self.startIndex > 0: self.startIndex -= 1
        if event.key == "Down":
            if self.selected < 7: self.selected += 1
            elif self.startIndex + 8 < len(self.inv): self.startIndex += 1
        if event.key == "e":
            if self.startIndex + self.selected < len(self.inv):
                chosen = self.inv[self.startIndex + self.selected]
                if not isinstance(chosen, item.Equip): return
                equips = self.app.player.equips
                if equips.get(chosen.slot) != None:
                    self.inv.append(equips[chosen.slot])
                equips[chosen.slot] = chosen
                self.inv.pop(self.startIndex + self.selected)
            self.app.player.updateStats()
        if event.key == "u":
            if self.startIndex + self.selected < len(self.inv):
                chosen = self.inv[self.startIndex + self.selected]
                if not isinstance(chosen, item.Consumable): return
                chosen.use(self.app.player)
                self.inv.pop(self.startIndex + self.selected)
        if event.key == "d":
            if self.startIndex + self.selected < len(self.inv):
                chosen = self.inv[self.startIndex + self.selected]
                level = self.app.levels[self.app.currentLevel]
                level.items[(self.app.player.row, self.app.player.col)] = level.items.get((self.app.player.row, self.app.player.col), []) + [chosen]
                self.inv.pop(self.startIndex + self.selected)
    
    def redrawAll(self, canvas):
        height = self.height / 8
        i = 0
        while height <= self.height:
            x0 = 0
            y0 = height - self.height / 8
            x1 = self.width
            y1 = height
            if i == self.selected:
                canvas.create_rectangle(x0, y0, x1, y1, fill=self.color, width=10, outline="black")
            else:
                canvas.create_rectangle(x0, y0, x1, y1, fill=self.color, width=0)
            if self.startIndex + i < len(self.inv):
                aItem = self.inv[self.startIndex+i]
                canvas.create_text(20, (y0 + y1) / 2, text=f"{self.startIndex+i}.", font="Mono 14")
                canvas.create_text(120, (y0 + y1) / 2, text=aItem.name, font="Mono 14")
            height += self.height / 8
            if self.color == "gray45": self.color = "gray65"
            else: self.color = "gray45"
            i += 1

class Win(Mode):
    def redrawAll(self, canvas):
        canvas.create_rectangle(0, 0, self.width, self.height, fill="black")
        canvas.create_text(self.width / 2, self.height/2 - 20, text="You win!", font="Mono 32", fill="white")
        canvas.create_text(self.width / 2, self.height/2 + 20, text=f"Turns taken: {self.app.turns}", font="Mono 32", fill="white")

class Lose(Mode):
    def redrawAll(self, canvas):
        canvas.create_rectangle(0, 0, self.width, self.height, fill="black")
        canvas.create_text(self.width / 2, self.height/2 - 20, text="You lose :(", font="Mono 32", fill="white")
        canvas.create_text(self.width / 2, self.height/2 + 20, text=f"Turns taken: {self.app.turns}", font="Mono 32", fill="white")
