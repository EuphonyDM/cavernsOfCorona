
# taken from https://www.diderot.one/course/34/chapters/2847/
from cmu_112_graphics import *
import level
import creature

class Caverns(ModalApp):
    def appStarted(self):
        self.setSize(640, 480)
        self.addMode(GameMode(name='game'))
        self.setActiveMode('game')

class GameMode(Mode):
    def appStarted(self):
        self.player = creature.Player(self, 10, 2, 2)
        self.levels = []
        self.levels.append(level.Level(self, self.player))
        self.currentLevel = 0
    
    def keyPressed(self, event):
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

if __name__ == "__main__":
    Caverns()