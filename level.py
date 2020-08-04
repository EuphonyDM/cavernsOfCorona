from cmu_112_graphics import * # taken from https://www.diderot.one/course/34/chapters/2847/
import creature
import os
import item
import random
import copy

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
        # self.items[(1, 3)] = [item.Equip(self.app, "Sword", f"assets{os.sep}1BitPack{os.sep}sword.png", "d5", "main")]
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
    for i in range(100):
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
                    toBreak = True
                    break
                copyLines[newR] = copyLines[newR][:newC]+lines[r][c]+copyLines[newR][newC+1:]
            if toBreak:
                break
        if not toBreak:
            levelLines = copyLines

    # tunnels = 0
    # tunnelLocs = set()
    # while tunnels < 300:
    #     r = random.randrange(100)
    #     c = random.randrange(100)
    #     val = levelLines[r][c]
    #     if val == "#" and isWall(levelLines, r, c):
    #         levelLines, b = makeTunnel(levelLines, r, c)
    #         if b:
    #             tunnels += 1
    pr, pc = getPlayerLoc(levelLines)
    levelStr = ""
    for l in levelLines:
        levelStr += l
        levelStr += "\n"
    print(levelStr)
    return (levelStr, pr, pc)

def isWall(lines, r, c):
    dirs = [(0,1), (1, 0), (0, -1), (-1, 0)]
    # wallCount = 0
    floorCount = 0
    for dc, dr in dirs:
        newr = r + dr
        newc = c + dc
        if 0 <= newr < len(lines) and 0 <= newc < len(lines[newr]):
            val = lines[newr][newc]
            # if val == "#":
            #     wallCount += 1
            if val == ".":
                floorCount += 1
    return floorCount == 1

# def makeTunnel(oldLines, r1, c1):
#     lines = copy.deepcopy(oldLines)
#     dirs = [(0,1), (1, 0), (0, -1), (-1, 0)]
#     tunnelDir = None
#     for dr, dc in dirs:
#         newr = r1 + dr
#         newc = c1 + dc
#         if 0 <= newr < len(lines) and 0 <= newc < len(lines[newr]) and lines[newr][newc] == ".":
#             tunnelDir = (-1*dr, -1*dc)
#     if tunnelDir == None:
#         return oldLines, False
#     r2 = r1
#     c2 = c1
#     while lines[r2][c2] != ".":
#         r2 += tunnelDir[0]
#         c2 += tunnelDir[1]
#         if not (0 <= r2 < len(lines)) or not (0 <= c2 < len(lines[r2])):
#             return oldLines, False
#     if abs(r2 - r1) > 5 or abs(c2 - c1) > 5:
#         return oldLines, False
#     if tunnelDir[0] != 0:
#         for r in range(min(r1, r2), max(r1, r2)):
#             lines[r] = lines[r][:c1]+"."+lines[r][c1+1:]
#             lines[r] = lines[r][:c1+1]+"#"+lines[r][c1+2:]
#             lines[r] = lines[r][:c1-1]+"#"+lines[r][c1:]
#     else: 
#         for c in range(min(c1, c2), max(c1, c2)):
#             lines[r1] = lines[r1][:c]+"."+lines[r1][c+1:]
#             lines[r1+1] = lines[r1+1][:c]+"#"+lines[r1+1][c+1:]
#             lines[r1-1] = lines[r1-1][:c]+"#"+lines[r1-1][c+1:]
#     if lines[r1-tunnelDir[0]][c1-tunnelDir[1]] == "#":
#         lines[r1-tunnelDir[0]] = lines[r1-tunnelDir[0]][:c1-tunnelDir[1]]+"."+lines[r1-tunnelDir[0]][c1-tunnelDir[1]+1:]
#     if lines[r2+tunnelDir[0]][c2+tunnelDir[1]] == "#":
#         lines[r2+tunnelDir[0]] = lines[r2+tunnelDir[0]][:c2+tunnelDir[1]]+"."+lines[r2+tunnelDir[0]][c2+tunnelDir[1]+1:]
#     return copy.deepcopy(lines), True

def getPlayerLoc(lines):
    r = 0
    c = 0
    val = lines[0][0]
    while val != ".":
        r+=1
        c+=1
        val = lines[r][c]
    return r, c
