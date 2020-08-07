# Contains the Level class which most of the game is played in

from cmu_112_graphics import * # taken from https://www.diderot.one/course/34/chapters/2847/
import creature
import os
import item
import random
import copy
import pathfinding

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
        self.static, pr, pc, cr, cc = genLevel()
        while pathfinding.pathfind(self.notWall, pr, pc, cr, cc) == None:
            print("generation failed")
            self.static, pr, pc, cr, cc = genLevel()
        print(self.static)
        self.wall = app.loadImage(f"assets{os.sep}1BitPack{os.sep}wall.png")
        self.trap = app.loadImage(f"assets{os.sep}1BitPack{os.sep}trap.png")
        self.items = dict()
        self.items[(cr, cc)] = [item.genItem(self,"Crown")]
        self.enemies = set()
        self.toKill = []
        self.traps = set()
        self.genTraps(50)
        self.genEnemies(20)
        self.genItems("Sword", 5)
        self.genItems("Helmet", 5)
        self.genItems("Health Ring", 5)
        self.genItems("Health Pot", 10)
        self.genItems("Sharpening Kit", 10)
        self.player = player
        self.player.move(pr, pc)
        self.pTurn = True
    
    def genTraps(self, num):
        spawned = 0
        while spawned < num:
            r = random.randrange(100)
            c = random.randrange(100)
            if self.freeSpace((r,c)) and (r,c) not in self.traps:
                spawned += 1
                self.traps.add((r,c))

    def genEnemies(self, num):
        spawned = 0
        while spawned < num:
            r = random.randrange(100)
            c = random.randrange(100)
            if self.freeSpace((r,c)) and (r,c) not in self.traps:
                spawned += 1
                self.enemies.add(creature.Enemy(self.app, "e", f"assets{os.sep}1BitPack{os.sep}enemy.png", 8, r, c, 2, 0))
    
    def genItems(self, name, num):
        spawned = 0
        while spawned < num:
            r = random.randrange(100)
            c = random.randrange(100)
            if self.freeSpace((r,c)) and (r,c) not in self.traps:
                spawned += 1
                locList = self.items.get((r, c), [])
                locList.append(item.genItem(self, name))
                self.items[(r, c)] = locList

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
            for e in self.enemies:
                if e.row == newR and e.col == newC:
                    e.damaged(self.player.dmg)
                    return True
            self.player.move(newR, newC)
            if (newR, newC) in self.traps:
                self.player.damaged(2)
            return True
        return False
    
    def notWall(self, node):
        r = node[0]
        c = node[1]
        return self.static.splitlines()[r][c] == "."

    def freeSpace(self, node):
        r = node[0]
        c = node[1]
        return self.notWall(node) and self.noEnemies(r, c)

    def noEnemies(self, r, c):
        for e in self.enemies:
            if e.row == r and e.col == c:
                return False
        return True

    def timerFired(self):
        if self.pTurn: 
            self.player.updateStats
            for i in self.player.inventory:
                if i.name == "Crystal Crown":
                    self.app.setActiveMode("win")
            return
        for e in self.toKill:
            self.enemies.remove(e)
        self.toKill = []
        for e in self.enemies:
            if self.nearPlayer(e):
                e.turn(self.static.splitlines(), self.enemies, self.freeSpace)
                if (e.row, e.col) in self.traps:
                    e.damaged(2)
        for e in self.toKill:
            self.enemies.remove(e)
        self.toKill = []
        self.app.turns += 1
        newEffects = []
        for e0, e1 in self.player.effects:
            e1 -= 1
            if e1 != 0:
                newEffects.append((e0, e1))
        self.player.effects = newEffects
        self.player.updateStats()
        self.pTurn = True
    
    def nearPlayer(self, e):
        r1 = self.player.row
        c1 = self.player.col
        r2 = e.row
        c2 = e.col
        dist = ((r2-r1)**2 + (c2-c1)**2) ** 0.5
        return dist < 10

    def scaleSprites(self, squareLen):
        if self.wall.size[0] != squareLen:
            self.wall = self.app.scaleImage(self.wall, squareLen / self.wall.size[0])
        if self.trap.size[0] != squareLen:
            self.trap = self.app.scaleImage(self.trap, squareLen / self.trap.size[0])

    def getView(self, scrollR, scrollC):
        lines = self.static.splitlines()
        rows = len(lines)
        cols = len(lines[self.player.row])
        # for i in range(self.player.row - 3, self.player.row + 3):
        #     if 0 <= i < len(lines):
        #         newCols = len(lines[i])
        #         if newCols > cols:
        #             cols = newCols
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
                for i in self.items.get((row, col), []):
                    newR = row - scrollR
                    newC = col - scrollC
                    if 0 <= newR < 7 and 0 <= newC < 7:
                        i.render(newR, newC, squareLen, canvas)

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
        
        for row, col in self.traps:
            if not row == self.player.row or not col == self.player.col:
                newR = row - scrollR
                newC = col - scrollC
                if 0 <= newR < 7 and 0 <= newC < 7:
                    x0 = newC * squareLen
                    y0 = newR * squareLen
                    x1 = x0 + squareLen
                    y1 = y0 + squareLen
                    x = (x0 + x1) / 2
                    y = (y0 + y1) / 2
                    canvas.create_image(x, y, image=ImageTk.PhotoImage(self.trap))

        self.player.render(size, rcs, 3, 3, canvas)

        for enemy in self.enemies:
            relR = enemy.row - scrollR
            relC = enemy.col - scrollC
            if 0 <= relR < 7 and 0 <= relC < 7:
                enemy.render(size, rcs, relR, relC, canvas)

def genLevel():
    failed = 0
    levelStr = ((" " * 100) + "\n") * 100
    levelLines = levelStr.splitlines()
    while failed < 10000: # place rooms
        n = random.randrange(7) # if I add more rooms, change these two lines
        room = readFile("rooms"+os.sep+"00"+str(n)+".txt")
        lines = room.splitlines()
        row = random.randrange(100-len(lines))
        col = random.randrange(100-len(lines[0]))
        copyLines = copy.deepcopy(levelLines)
        toBreak = False
        for r in range(len(lines)):
            for c in range(len(lines[1])):
                newR = r + row
                newC = c + col
                if not copyLines[newR][newC] == " ":
                    failed += 1
                    toBreak = True
                    break
                copyLines[newR] = copyLines[newR][:newC]+lines[r][c]+copyLines[newR][newC+1:]
            if toBreak:
                break
        if not toBreak:
            levelLines = copyLines
    failed = 0
    while failed < 100:
        room = readFile("rooms"+os.sep+"small.txt")
        lines = room.splitlines()
        row = random.randrange(100-len(lines))
        col = random.randrange(100-len(lines[0]))
        copyLines = copy.deepcopy(levelLines)
        toBreak = False
        for r in range(len(lines)):
            for c in range(len(lines[1])):
                newR = r + row
                newC = c + col
                if not copyLines[newR][newC] == " ":
                    failed += 1
                    toBreak = True
                    break
                copyLines[newR] = copyLines[newR][:newC]+lines[r][c]+copyLines[newR][newC+1:]
            if toBreak:
                break
        if not toBreak:
            levelLines = copyLines
    levelLines = makeTunnels(levelLines)
    pr, pc = getPlayerLoc(levelLines)
    cr, cc = getCrownLoc(levelLines)
    levelStr = ""
    for l in levelLines:
        levelStr += l
        levelStr += "\n"
    return (levelStr, pr, pc, cr, cc)

def makeTunnels(lines):
    rows = len(lines)
    cols = len(lines[0])
    # .##.
    for row in range(rows):
        for col in range(cols):
            dirs = [(0,1), (1, 0), (0, -1), (-1, 0)]
            if lines[row][col] == ".":
                for r, c in dirs: 
                    newR = row + 3*r
                    newC = col + 3*c
                    if (0 <= newR < rows and 0 <= newC < cols and lines[newR][newC] == "."
                        and lines[row+r][col+c] == "#" and lines[row+2*r][col+2*c] == "#"):
                        lines[row+r] = lines[row+r][:col+c]+"."+lines[row+r][col+c+1:]
                        lines[row+2*r] = lines[row+2*r][:col+2*c]+"."+lines[row+2*r][col+2*c+1:]
    # .# #.
    for row in range(rows):
        for col in range(cols):
            dirs = [(0,1), (1, 0), (0, -1), (-1, 0)]
            if lines[row][col] == ".":
                for r, c in dirs: 
                    newR = row + 4*r
                    newC = col + 4*c
                    if (0 <= newR < rows and 0 <= newC < cols and lines[newR][newC] == "."
                        and lines[row+r][col+c] == "#" and lines[row+2*r][col+2*c] == " "
                        and lines[row+3*r][col+3*c] == "#"):
                        lines[row+r] = lines[row+r][:col+c]+"."+lines[row+r][col+c+1:]
                        lines[row+2*r] = lines[row+2*r][:col+2*c]+"."+lines[row+2*r][col+2*c+1:]
                        lines[row+3*r] = lines[row+3*r][:col+3*c]+"."+lines[row+3*r][col+3*c+1:]
    # .#  #.
    for row in range(rows):
        for col in range(cols):
            dirs = [(0,1), (1, 0), (0, -1), (-1, 0)]
            if lines[row][col] == ".":
                for r, c in dirs: 
                    newR = row + 5*r
                    newC = col + 5*c
                    if (0 <= newR < rows and 0 <= newC < cols and lines[newR][newC] == "."
                        and lines[row+r][col+c] == "#" and lines[row+2*r][col+2*c] == " "
                        and lines[row+3*r][col+3*c] == " " and lines[row+4*r][col+4*c] == "#"):
                        lines[row+r] = lines[row+r][:col+c]+"."+lines[row+r][col+c+1:]
                        lines[row+2*r] = lines[row+2*r][:col+2*c]+"."+lines[row+2*r][col+2*c+1:]
                        lines[row+3*r] = lines[row+3*r][:col+3*c]+"."+lines[row+3*r][col+3*c+1:]
                        lines[row+4*r] = lines[row+4*r][:col+4*c]+"."+lines[row+4*r][col+4*c+1:]
    # .##.
    for row in range(rows):
        for col in range(cols):
            dirs = [(0,1), (1, 0), (0, -1), (-1, 0)]
            if lines[row][col] == ".":
                for r, c in dirs: 
                    newR = row + 3*r
                    newC = col + 3*c
                    if (0 <= newR < rows and 0 <= newC < cols and lines[newR][newC] == "."
                        and lines[row+r][col+c] == "#" and lines[row+2*r][col+2*c] == "#"):
                        lines[row+r] = lines[row+r][:col+c]+"."+lines[row+r][col+c+1:]
                        lines[row+2*r] = lines[row+2*r][:col+2*c]+"."+lines[row+2*r][col+2*c+1:]
    return placeWalls(lines)
                    
def placeWalls(lines):
    rows = len(lines)
    cols = len(lines[0])
    dirs = [(0,1), (1, 0), (0, -1), (-1, 0)]
    for row in range(rows):
        for col in range(cols):
            if lines[row][col] == " ":
                for r, c in dirs: 
                    newR = row + r
                    newC = col + c
                    if 0 <= newR < rows and 0 <= newC < cols and lines[newR][newC] == ".":
                        lines[row] = lines[row][:col]+"#"+lines[row][col+1:]
    return lines

def getPlayerLoc(lines):
    r = 0
    c = 0
    val = lines[0][0]
    while val != ".":
        r+=1
        c+=1
        val = lines[r][c]
    return r, c

def getCrownLoc(lines):
    r = 99
    c = 99
    val = lines[0][0]
    while val != ".":
        r-=1
        c-=1
        val = lines[r][c]
    return r, c
