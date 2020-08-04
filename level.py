from cmu_112_graphics import * # taken from https://www.diderot.one/course/34/chapters/2847/
import creature
import os
import item

# These two functions taken from https://www.diderot.one/course/34/chapters/2604/

def readFile(path):  
    with open(path, "rt") as f:  
        return f.read()  
  
def writeFile(path, contents):  
    with open(path, "wt") as f:  
        f.write(contents)  

class Level:
    def __init__(self, app, player):
        self.app = app
        self.static, pr, pc = genLevel()
        self.wall = app.loadImage(f"assets{os.sep}1BitPack{os.sep}wall.png")
        self.items = dict()
        self.items[(1, 3)] = [item.Equip(self.app, "Sword", f"assets{os.sep}1BitPack{os.sep}sword.png", "d5", "main")]
        self.enemies = set()
        self.player = player
        self.player.move(pr, pc)
        self.pTurn = True
    
    def keyPressed(self, event):
        if self.pTurn:
            if event.key == "Up": 
                if self.tryMove(-1, 0):
                    self.pTurn = False
            if event.key == "Down": 
                if self.tryMove(1, 0):
                    self.pTurn = False
            if event.key == "Left": 
                if self.tryMove(0, -1):
                    self.pTurn = False
            if event.key == "Right": 
                if self.tryMove(0, 1):
                    self.pTurn = False
            if event.key == ".":
                self.pTurn = False
            if event.key == "g":
                for item in self.items.get((self.player.row, self.player.col), []):
                    self.player.inventory.append(item)
                self.items[(self.player.row, self.player.col)] = []
                self.pTurn = False
    
    def tryMove(self, dRow, dCol):
        newR = self.player.row + dRow
        newC = self.player.col + dCol
        lines = self.static.splitlines()
        if lines[newR][newC] == ".":
            self.player.move(newR, newC)
            return True
        return False
    
    def timerFired(self):
        if self.pTurn: return
        for e in self.enemies:
            print("e")
        self.pTurn = True
    
    def scaleSprites(self, squareLen):
        if self.wall.size[0] != squareLen:
            self.wall = self.app.scaleImage(self.wall, squareLen / self.wall.size[0])

    def getView(self, scrollR, scrollC):
        lines = self.static.splitlines()
        rows = len(lines)
        cols = 0
        for i in range(self.player.row - 3, self.player.row + 3):
            if 0 <= i < len(lines):
                newCols = len(lines[i])
                if newCols > cols:
                    cols = newCols
        result = ""
        for r in range(7):
            for c in range(7):
                newR = r + scrollR
                newC = c + scrollC
                if 0 <= newR < rows and 0 <= newC < cols:
                    result += lines[newR][newC]
                else:
                    result += " "
            result += "\n"
        return result

    def render(self, size, canvas):
        scrollR = self.player.row - 3
        scrollC = self.player.col - 3
        view = self.getView(scrollR, scrollC)
        lines = view.splitlines()
        rcs = len(lines)
        squareLen = size / rcs
        self.scaleSprites(squareLen)
        canvas.create_rectangle(0, 0, size, size, fill="#220000", width=0)
        for row, col in self.items:
            if not row == self.player.row or not col == self.player.col:
                for item in self.items.get((row, col), []):
                    newR = row - scrollR
                    newC = col - scrollC
                    if 0 <= newR < 7 and 0 <= newC < 7:
                        item.render(newR, newC, squareLen, canvas)
        for row in range(rcs):
            for col in range(rcs):
                x0 = col * squareLen
                y0 = row * squareLen
                x1 = x0 + squareLen
                y1 = y0 + squareLen
                x = (x0 + x1) / 2
                y = (y0 + y1) / 2
                if lines[row][col] == "#":
                    canvas.create_image(x, y, image=ImageTk.PhotoImage(self.wall))
                if lines[row][col] == " ":
                    canvas.create_rectangle(x0, y0, x1, y1, fill="black")
        self.player.render(size, rcs, 3, 3, canvas)

def genLevel():
    return (readFile("level2.txt"), 2, 2)
