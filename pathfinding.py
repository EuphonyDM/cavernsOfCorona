# Contains the pathfinding algorithim used by the enemies and to confirm that a generated level is valid
# The algorithim used is a greedy best first search, which prioritizes spaces closer to the goal

def pathfind(avail, sr, sc, gr, gc):
    openList = []
    closedList = []
    openList.append((sr, sc))
    while len(openList) > 0:
        node = openList.pop()
        closedList.append(node)
        if node == (gr, gc):
            return closedList
        for n in getNeighbors(avail, node):
            if n not in openList and n not in closedList:
                openList.append(n)
        openList = bestSorted(openList, (gr, gc))
    return None

def getNeighbors(avail, node):
    result = []
    dirs = [(0,1), (1, 0), (0, -1), (-1, 0)]
    for r, c in dirs: 
        newR = node[0] + r
        newC = node[1] + c
        newNode = (newR, newC)
        if avail(newNode):
            result.append(newNode)
    return result

def bestSorted(nodes, gNode):
    valDict = dict()
    for node in nodes:
        val = h(node, gNode)
        l = valDict.get(val, [])
        l.append(node)
        valDict[val] = l
    result = []
    i = 0
    while len(valDict) > 0:
        if i in valDict:
            for node in valDict[i]:
                result.insert(0,node)
            del valDict[i]
        i += 1
    return result
    
def h(sNode, gNode):
    return abs(gNode[0]-sNode[0]) + abs(gNode[1]-sNode[1])

