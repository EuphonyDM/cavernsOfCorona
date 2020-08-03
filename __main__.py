
# taken from https://www.diderot.one/course/34/chapters/2847/
from cmu_112_graphics import *
import level
import creature

class Caverns(ModalApp):
    def appStarted(self):
        self.setSize(640, 480)
        self.player = creature.Player(self, 10, 2, 2)
        self.addMode(GameMode(name="game"))
        self.addMode(Inventory(name="inv"))
        self.setActiveMode('game')

class GameMode(Mode):
    def appStarted(self):
        self.player = self.app.player
        self.levels = []
        self.levels.append(level.Level(self, self.player))
        self.currentLevel = 0
    
    def keyPressed(self, event):
        if event.key == "i":
            self.setActiveMode("inv")
        self.levels[self.currentLevel].keyPressed(event)
    
    def timerFired(self):
        self.levels[self.currentLevel].timerFired()
    
    def redrawAll(self, canvas):
            canvas.create_rectangle(self.height, 0, self.width, self.height, fill="black")
            textX = (self.height + self.width) / 2
            canvas.create_text(textX, 40, text=f"HP: {self.player.hp[0]}/{self.player.hp[1]}", fill="white", font="Mono 14")
            canvas.create_text(textX, 80, text=f"Damage: {self.player.damage}", fill="white", font="Mono 14")
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
                item = self.inv[self.startIndex+i]
                canvas.create_text(20, (y0 + y1) / 2, text=f"{self.startIndex+i}.", font="Mono 14")
                canvas.create_text(80, (y0 + y1) / 2, text=item.name, font="Mono 14")
            height += self.height / 8
            if self.color == "gray45": self.color = "gray65"
            else: self.color = "gray45"
            i += 1


if __name__ == "__main__":
    Caverns()