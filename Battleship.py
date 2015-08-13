# Image source - pexels.com

import pygame, random, sys
from pygame.locals import *

FPS = 30
WINDOWWIDTH = 1200
WINDOWHEIGHT = 800
GRIDSIZE = 500
BOARDWIDTH = 10
BOARDHEIGHT = 10
CELLSIZE = 48
INNER_CELLSIZE = int(CELLSIZE * .75)
X_MARGIN = int((WINDOWWIDTH - (GRIDSIZE*2)) / 3)
Y_MARGIN = int((WINDOWHEIGHT - GRIDSIZE) / 2)
LINEWIDTH = 2

BLANK = "."
SHIP = "O"
HIT = "H"
MISS = "M"
SUNK = "S"

BLACK = (0, 0, 0)
GRAY = (135, 135, 135)
WHITE = (255, 255, 255)
BROWN = (128, 71, 52)
LIGHTBROWN = (168, 91, 66)
RED = (176, 21, 21)
LIGHTRED = (214, 32, 32)
GREEN = (35, 94, 37)
LIGHTGREEN = (58, 140, 60)
BLUE = (0, 255, 255)
ORANGE = (235, 127, 33)

HIGHLIGHTCOLOR = BLUE
BOARDCOLOR = GRAY
SHIPCOLOR = (BROWN, LIGHTBROWN)
COLLIDESHIPCOLOR = (RED, LIGHTRED)
NONCOLLIDESHIPCOLOR = (GREEN, LIGHTGREEN)
LINECOLOR = BLACK
HITCOLOR = RED
MISSCOLOR = WHITE
FONTCOLOR = WHITE
FONTRECTCOLOR = ORANGE

TEMPLATEWIDTH = 5
TEMPLATEHEIGHT = 5

AIRCRAFTCARRIER_TEMPLATE =[["..O..",
                            "..O..",
                            "..O..",
                            "..O..",
                            "..O.."],
                           [".....",
                            ".....",
                            "OOOOO",
                            ".....",
                            "....."]]

BATTLESHIP_TEMPLATE =[["..O..",
                       "..O..",
                       "..O..",
                       "..O..",
                       "....."],
                      [".....",
                       ".....",
                       "OOOO.",
                       ".....",
                       "....."]]

SUBMARINE_TEMPLATE =[[".....",
                      "..O..",
                      "..O..",
                      "..O..",
                      "....."],
                     [".....",
                      ".....",
                      ".OOO.",
                      ".....",
                      "....."]]

DESTROYER_TEMPLATE =[[".....",
                      "..O..",
                      "..O..",
                      "..O..",
                      "....."],
                     [".....",
                      ".....",
                      ".OOO.",
                      ".....",
                      "....."]]

PATROLBOAT_TEMPLATE =[[".....",
                       "..O..",
                       "..O..",
                       ".....",
                       "....."],
                      [".....",
                       ".....",
                       ".OO..",
                       ".....",
                       "....."]]

YCOORDS_VERTICAL = {"Patrol Boat":(1, 2),
                    "Destroyer":(1, 1),
                    "Submarine":(1, 1),
                    "Battleship":(0, 1),
                    "Aircraft Carrier":(0, 0)}
XCOORDS_HORIZONTAL = {"Patrol Boat":(1, 2),
                      "Destroyer":(1, 1),
                      "Submarine":(1, 1),
                      "Battleship":(0, 1),
                      "Aircraft Carrier":(0, 0)}

BOATS = {"Patrol Boat":PATROLBOAT_TEMPLATE,
         "Destroyer":DESTROYER_TEMPLATE,
         "Submarine":SUBMARINE_TEMPLATE,
         "Battleship":BATTLESHIP_TEMPLATE,
         "Aircraft Carrier":AIRCRAFTCARRIER_TEMPLATE}

def main():
    global DISPLAYSURF, FPSCLOCK, FONTOBJ
    pygame.init()
    FPSCLOCK = pygame.time.Clock()
    DISPLAYSURF = pygame.display.set_mode((WINDOWWIDTH, WINDOWHEIGHT))
    FONTOBJ = pygame.font.Font("freesansbold.ttf", 32)
    
    pygame.display.set_caption("Battleship!")
    pygame.display.set_icon(pygame.image.load("gameicon.png"))
    
    while True:
        if runGame() == False:
            pygame.quit()
            sys.exit()

def runGame():
    board1 = createBoard()
    board2 = createBoard()
    msg = ""
    pieces = []
    for i in BOATS:
        pieces.append(getNewBoat(i))
        
    boatsOnGrid1, squaresOnBoats = getHumanShipPlacement(board1, board2, pieces)
    boatsOnGrid2 = getComputerShipPlacement(pieces, board2)

    playerShipsSunk = []
    computerShipsSunk = []
    
    if random.randint(0, 1) == 0:
        turn = "player"
    else:
        turn = "computer"

    shipFound = False
    orientationGuess = None
    shipCoords = None
    directionList = None
    
    while True:
        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit()
                sys.exit()

        if turn == "player":
            playerMissileLaunch(board1, board2)
            for boat in boatsOnGrid2:
                if isShipSunk(boat, board2):
                    if boat not in playerShipsSunk:
                        playerShipsSunk.append(boat)
                        for x in range(TEMPLATEWIDTH):
                            for y in range(TEMPLATEHEIGHT):
                                xcoord = boat["x"] + x
                                ycoord = boat["y"] + y
                                if boat["rotation"][x][y] == SHIP and board2[xcoord][ycoord] == HIT:
                                    board2[xcoord][ycoord] = SUNK

                        drawSurface(board1, board2)
                        drawCoords()
                        msg = "You sunk my " + boat["name"] + "!"
                        drawMessage(msg)
                        pygame.display.update()
                        FPSCLOCK.tick(FPS)
                        pygame.time.wait(1000)
                        msg = ""
            if len(playerShipsSunk) == 5:
                return endGameScreen("PLAYER")
            turn = "computer"
            
        elif turn == "computer":
            shipFound, orientationGuess, shipCoords, directionList, result, location = getComputerMove(board1, shipFound, orientationGuess, shipCoords, directionList)
            
            drawSurface(board1, board2)
            drawCoords()
            msg = "Launching missile . . ."
            drawMessage(msg)
            pygame.display.update()
            FPSCLOCK.tick(FPS)
            pygame.time.wait(500)
            msg = ""
            board1[location[0]][location[1]] = result
            sunkenShips = getSunkenShips(board1, boatsOnGrid1, squaresOnBoats)
            for boat in sunkenShips:
                if boat not in computerShipsSunk:
                    computerShipsSunk.append(boat)
                    shipFound = False
                    orientationGuess = None
                    shipCoords = None
                    directionList = None

                    for x in range(BOARDWIDTH):
                        for y in range(BOARDHEIGHT):
                            if [x, y] in squaresOnBoats[boat["name"]]:
                                board1[x][y] = SUNK
                        
                    drawSurface(board1, board2)
                    drawCoords()
                    msg = "I sunk your " + boat["name"] + "!"
                    drawMessage(msg)
                    pygame.display.update()
                    FPSCLOCK.tick(FPS)
                    pygame.time.wait(1000)
                    msg = ""
            if len(computerShipsSunk) == 5:
                return endGameScreen("COMPUTER")
            turn = "player"

        drawSurface(board1, board2)
        drawCoords()
        drawMessage(msg)
        pygame.display.update()
        FPSCLOCK.tick(FPS)

def isValidOrientation(board, shipCoords, orientation, directionList):
    if orientation == "vertical":
        if directionList["up"] != None:
            if isOnBoard(shipCoords[0], shipCoords[1] + directionList["up"]):
                if board[shipCoords[0]][shipCoords[1] + directionList["up"]] in (BLANK, SHIP):
                    return True
        if directionList["down"] != None:
            if isOnBoard(shipCoords[0], shipCoords[1] + directionList["down"]):
                if board[shipCoords[0]][shipCoords[1] + directionList["down"]] in (BLANK, SHIP):
                    return True
                                                                                  
    elif orientation == "horizontal":
        if directionList["left"] != None:
            if isOnBoard(shipCoords[0] + directionList["left"], shipCoords[1]):
                if board[shipCoords[0] + directionList["left"]][shipCoords[1]] in (BLANK, SHIP):
                    return True
        if directionList["right"] != None:
            if isOnBoard(shipCoords[0] + directionList["right"], shipCoords[1]):
                if board[shipCoords[0] + directionList["right"]][shipCoords[1]] in (BLANK, SHIP):
                    return True

    return False

def getComputerMove(board1, shipFound, orientationGuess, shipCoords, directionList):
    if shipFound == True:
        if orientationGuess != None:
            if not isValidOrientation(board1, shipCoords, orientationGuess, directionList):
                if orientationGuess == "vertical":
                    orientationGuess = "horizontal"
                    directionList = {"left": -1,
                                     "right": 1}
                elif orientationGuess == "horizontal":
                    orientationGuess = "vertical"
                    directionList = {"up": -1,
                                     "down": 1}
        else:
            if isValidOrientation(board1, shipCoords, "vertical", {"up":-1, "down":1}):
                orientationGuess = "vertical"
                directionList = {"up": -1,
                                 "down": 1}
            else:
                orientationGuess = "horizontal"
                directionList = {"left": -1,
                                 "right": 1}

        directionList = getEdgeOfShip(board1, shipCoords, orientationGuess, directionList)
        
        if orientationGuess == "vertical":
            direction = random.choice(("up", "down"))
            while directionList[direction] == None:
                direction = random.choice(("up", "down"))
            location = [shipCoords[0], shipCoords[1] + directionList[direction]]
                
        elif orientationGuess == "horizontal":
            direction = random.choice(("left", "right"))
            while directionList[direction] == None:
                direction = random.choice(("left", "right"))
            location = [shipCoords[0] + directionList[direction], shipCoords[1]]

    else:
        validPositions = []
        unsunkHits = []
        for x in range(BOARDWIDTH):
            for y in range(BOARDHEIGHT):
                if board1[x][y] == HIT:
                    unsunkHits.append([x, y])
                elif board1[x][y] in (BLANK, SHIP):
                    validPositions.append([x, y])

        if len(unsunkHits) > 0:
            shipCoords = random.choice(unsunkHits)
            shipFound = True
            if isValidOrientation(board1, shipCoords, "vertical", {"up":-1, "down":1}):
                orientationGuess = "vertical"
                directionList = {"up": -1,
                                 "down": 1}
            else:
                orientationGuess = "horizontal"
                directionList = {"left": -1,
                                 "right": 1}

            directionList = getEdgeOfShip(board1, shipCoords, orientationGuess, directionList)

            if orientationGuess == "vertical":
                direction = random.choice(("up", "down"))
                while directionList[direction] == None:
                    direction = random.choice(("up", "down"))
                location = [shipCoords[0], shipCoords[1] + directionList[direction]]
                
            elif orientationGuess == "horizontal":
                direction = random.choice(("left", "right"))
                while directionList[direction] == None:
                    direction = random.choice(("left", "right"))
                location = [shipCoords[0] + directionList[direction], shipCoords[1]]

        else:
            location = random.choice(validPositions)
    
    if shipFound:
        if board1[location[0]][location[1]] == SHIP:
            result = HIT
            if direction == "up" or direction == "left":
                directionList[direction] -= 1
            else:
                directionList[direction] += 1
        else:
            result = MISS
            directionList[direction] = None

    else:
        if board1[location[0]][location[1]] == SHIP:
            result = HIT
            shipFound = True
            shipCoords = location
        else:
            result = MISS

    return shipFound, orientationGuess, shipCoords, directionList, result, location

def getHumanShipPlacement(board1, board2, pieces):
    boatsOnGrid1 = []
    boatIndex = 0
    boat = pieces[boatIndex]
    coordX = 5
    coordY = 5
    boatName = boat["name"].lower()
    seq = ("Place your " , " with the arrow keys. Space to set and W to rotate")
    msg = boatName.join(seq)
    if not isOverlapping(board1, boat):
        canPlacePiece = True
        color = NONCOLLIDESHIPCOLOR
    else:
        canPlacePiece = False
        color = COLLIDESHIPCOLOR
    while True:
        if isOverlapping(board1, boat):
            canPlacePiece = False
            color = COLLIDESHIPCOLOR
        else:
            canPlacePiece = True
            color = NONCOLLIDESHIPCOLOR
            
        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit()
                sys.exit()
                
            elif event.type == KEYUP:
                if event.key == K_UP and not isGoingOffBoard(boat, adjY=-1):
                    boat["y"] -= 1
                elif event.key == K_DOWN and not isGoingOffBoard(boat, adjY=1):
                    boat["y"] += 1
                elif event.key == K_LEFT and not isGoingOffBoard(boat, adjX=-1):
                    boat["x"] -= 1
                elif event.key == K_RIGHT and not isGoingOffBoard(boat, adjX=1):
                    boat["x"] += 1

                elif event.key == K_SPACE:
                    if canPlacePiece:
                        boatsOnGrid1 = addToBoard(board1, boat, boatsOnGrid1)
                        boatIndex += 1
                        if boatIndex > 4:
                            squaresOnBoats = {}
                            for boat in boatsOnGrid1:
                                squaresOnBoats[boat["name"]] = getSquaresInBoat(boat)
                            return boatsOnGrid1, squaresOnBoats
                        boat = pieces[boatIndex]
                        boatName = boat["name"].lower()
                        msg = boatName.join(seq)
                    
                elif event.key == K_w:
                    boat = rotatePiece(boat)
                    if isGoingOffBoard(boat):
                        boat = rotatePiece(boat)

        drawSurface(board1, board2)
        drawCoords()
        drawPiece(boat, color)
        drawMessage(msg)
        pygame.display.update()
        FPSCLOCK.tick()

def getSquaresInBoat(boat):
    squaresInBoat = []
    breakLoop = False
    for x in range(TEMPLATEWIDTH):
        for y in range(TEMPLATEHEIGHT):
            if boat["rotation"][x][y] == SHIP:
                xcoord = boat["x"] + x
                ycoord = boat["y"] + y
                squaresInBoat.append([xcoord, ycoord])
                breakLoop = True
            if breakLoop:
                break
        if breakLoop:
            break

    for i in range(boat["size"]-1):
        if boat["orientation"] == "h":
            xcoord += 1
        elif boat["orientation"] == "v":
            ycoord += 1
        squaresInBoat.append([xcoord, ycoord])

    return squaresInBoat

def getSunkenShips(board, boatsOnGrid, squaresOnBoats):
    hits = getHitsOnBoard(board)
    sunkenShips = []
    for boat in boatsOnGrid:
        hitsOnBoat = 0
        squaresInBoat = squaresOnBoats[boat["name"]]
        for coords in squaresInBoat:
            if coords in hits:
                hitsOnBoat += 1
        if hitsOnBoat == boat["size"]:
            sunkenShips.append(boat)

    return sunkenShips

def getHitsOnBoard(board):
    hits = []
    for x in range(BOARDWIDTH):
        for y in range(BOARDHEIGHT):
            if board[x][y] in (HIT, SUNK):
                hits.append([x,y])

    return hits

def isShipSunk(piece, board):
    for x in range(TEMPLATEWIDTH):
        for y in range(TEMPLATEHEIGHT):
            xcoord = piece["x"] + x
            ycoord = piece["y"] + y
            if piece["rotation"][x][y] == SHIP and board[xcoord][ycoord] != HIT:
                return False

    return True

def getEdgeOfShip(board, shipCoords, orientation, directionList):
    if orientation == "vertical":
        edgeUp = 0
        edgeDown = 0
        if directionList["up"] != None:
            while True:
                edgeUp -= 1
                xCoord = shipCoords[0]
                yCoord = shipCoords[1] + edgeUp
                if not isOnBoard(xCoord, yCoord):
                    edgeUp += 1
                    break
                elif board[xCoord][yCoord] != HIT:
                    if board[xCoord][yCoord] not in (BLANK, SHIP):
                        edgeUp += 1
                    break
            directionList["up"] = edgeUp
            if directionList["up"] == 0:
                directionList["up"] = None
        if directionList["down"] != None:
            while True:
                edgeDown += 1
                xCoord = shipCoords[0]
                yCoord = shipCoords[1] + edgeDown
                if not isOnBoard(xCoord, yCoord):
                    edgeDown -= 1
                    break
                elif board[xCoord][yCoord] != HIT:
                    if board[xCoord][yCoord] not in (BLANK, SHIP):
                        edgeDown -= 1
                    break
            directionList["down"] = edgeDown
            if directionList["down"] == 0:
                directionList["down"] = None
                
    elif orientation == "horizontal":
        edgeLeft = 0
        edgeRight = 0
        if directionList["left"] != None:
            while True:
                edgeLeft -= 1
                xCoord = shipCoords[0] + edgeLeft
                yCoord = shipCoords[1]
                if not isOnBoard(xCoord, yCoord):
                    edgeLeft += 1
                    break
                elif board[xCoord][yCoord] != HIT:
                    if board[xCoord][yCoord] not in (BLANK, SHIP):
                        edgeLeft += 1
                    break
            directionList["left"] = edgeLeft
            if directionList["left"] == 0:
                directionList["left"] = None
        if directionList["right"] != None:
            while True:
                edgeRight += 1
                xCoord = shipCoords[0] + edgeRight
                yCoord = shipCoords[1]
                if not isOnBoard(xCoord, yCoord):
                    edgeRight -= 1
                    break
                elif board[xCoord][yCoord] != HIT:
                    if board[xCoord][yCoord] not in (BLANK, SHIP):
                        edgeRight -= 1
                    break
            directionList["right"] = edgeRight
            if directionList["right"] == 0:
                directionList["right"] = None

    return directionList

def endGameScreen(winner):
    WINNEROBJ = pygame.font.Font("freesansbold.ttf", 50)
    msg = "All ships sunk! " + winner + " is the winner!"
    msg2 = "Want to play again?"
    msgSurface = WINNEROBJ.render(msg, True, FONTCOLOR, FONTRECTCOLOR)
    msg2Surface = WINNEROBJ.render(msg2, True, FONTCOLOR, FONTRECTCOLOR)
    msgRect = msgSurface.get_rect()
    msg2Rect = msg2Surface.get_rect()
    msgRect.center = (int(WINDOWWIDTH/2), int(WINDOWHEIGHT/2 - 60))
    msg2Rect.center = (int(WINDOWWIDTH/2), int(WINDOWHEIGHT/2 - 7.5))
    FONTOBJ2 = pygame.font.Font("freesansbold.ttf", 35)
    yesSurface = FONTOBJ2.render("Yes", True, FONTCOLOR, FONTRECTCOLOR)
    yesRect = yesSurface.get_rect()
    yesRect.center = (int(WINDOWWIDTH/2-yesRect.width), int(WINDOWHEIGHT/2 + 50))
    noSurface = FONTOBJ2.render("No", True, FONTCOLOR, FONTRECTCOLOR)
    noRect = noSurface.get_rect()
    noRect.center = (int(WINDOWWIDTH/2+noRect.width), int(WINDOWHEIGHT/2 + 50))
    while True:
        mouseClicked = False
        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == MOUSEMOTION:
                mousex, mousey = event.pos
            elif event.type == MOUSEBUTTONUP:
                mousex, mousey = event.pos
                mouseClicked = True
        if mouseClicked and yesRect.collidepoint(mousex, mousey):
            return True
        elif mouseClicked and noRect.collidepoint(mousex, mousey):
            return False
        DISPLAYSURF.blit(msgSurface, msgRect)
        DISPLAYSURF.blit(msg2Surface, msg2Rect)
        DISPLAYSURF.blit(yesSurface, yesRect)
        DISPLAYSURF.blit(noSurface, noRect)
        pygame.display.update()
        FPSCLOCK.tick(FPS)

def getMinMaxCoords(piece):
    if piece["orientation"] == "v":
        minX = -2
        maxX = BOARDWIDTH-TEMPLATEWIDTH+2
        minY = -YCOORDS_VERTICAL[piece["name"]][0]
        maxY = BOARDHEIGHT-TEMPLATEHEIGHT+YCOORDS_VERTICAL[piece["name"]][1]
    elif piece["orientation"] == "h":
        minY = -2
        maxY = BOARDHEIGHT-TEMPLATEHEIGHT+2
        minX = -XCOORDS_HORIZONTAL[piece["name"]][0]
        maxX = BOARDWIDTH-TEMPLATEWIDTH+XCOORDS_HORIZONTAL[piece["name"]][1]
        
    return (minX, minY), (maxX, maxY)

def getComputerShipPlacement(pieces, board2):
    boatsOnGrid2 = []
    for piece in pieces:
        if random.randint(0,1) == 1:
            piece = rotatePiece(piece)
        piece["x"] = random.randint(getMinMaxCoords(piece)[0][0], getMinMaxCoords(piece)[1][0])
        piece["y"] = random.randint(getMinMaxCoords(piece)[0][1], getMinMaxCoords(piece)[1][1])
        while isGoingOffBoard(piece) or isOverlapping(board2, piece):
            if random.randint(0,1) == 1:
                piece = rotatePiece(piece)
            piece["x"] = random.randint(0, BOARDWIDTH)
            piece["y"] = random.randint(0, BOARDHEIGHT)
        boatsOnGrid2 = addToBoard(board2, piece, boatsOnGrid2)

    return boatsOnGrid2

def isOverlapping(board, piece, adjX=0, adjY=0):
    for x in range(TEMPLATEWIDTH):
        for y in range(TEMPLATEHEIGHT):
            if piece["rotation"][x][y] == SHIP:
                xcoord = x + piece["x"] + adjX
                ycoord = y + piece["y"] + adjY
                if board[xcoord][ycoord] != BLANK:
                    return True

    return False

def isGoingOffBoard(piece, adjX=0, adjY=0):
    for x in range(TEMPLATEWIDTH):
        for y in range(TEMPLATEHEIGHT):
            if piece["rotation"][x][y] == SHIP:
                xcoord = x + piece["x"] + adjX
                ycoord = y + piece["y"] + adjY
                if not isOnBoard(xcoord, ycoord):
                    return True

    return False

def drawPiece(piece, color):
    board = createBoard()
    addToBoard(board, piece, [])
    for x in range(BOARDWIDTH):
        for y in range(BOARDHEIGHT):
            if board[x][y] == SHIP:
                pixelx, pixely = convertToPixelCoords(x, y, "1")
                cell = pygame.Rect(pixelx, pixely, CELLSIZE, CELLSIZE)
                innercell = pygame.Rect(0, 0, INNER_CELLSIZE, INNER_CELLSIZE)
                innercell.centerx, innercell.centery = cell.centerx, cell.centery
                pygame.draw.rect(DISPLAYSURF, color[0], cell)
                pygame.draw.rect(DISPLAYSURF, color[1], innercell)

def playerMissileLaunch(board1, board2):
    msg = "Arrow keys to select target, space to fire"
    coordX = 5
    coordY = 5
    if board2[coordX][coordY] not in (BLANK, SHIP):
        canLaunch = False
    else:
        canLaunch = True
    while True:
        if board2[coordX][coordY] not in (BLANK, SHIP):
            canLaunch = False
        else:
            canLaunch = True

        for event in pygame.event.get():
            if event.type == KEYUP:
                if event.key == K_UP and isOnBoard(coordX, coordY-1):
                    coordY -= 1
                elif event.key == K_DOWN and isOnBoard(coordX, coordY+1):
                    coordY += 1
                elif event.key == K_LEFT and isOnBoard(coordX-1, coordY):
                    coordX -= 1
                elif event.key == K_RIGHT and isOnBoard(coordX+1, coordY):
                    coordX += 1

                elif event.key == K_SPACE:
                    if canLaunch:
                        if board2[coordX][coordY] == SHIP:
                            board2[coordX][coordY] = HIT
                            return
                        else:
                            board2[coordX][coordY] = MISS
                            return

        drawSurface(board1, board2)
        drawCoords()
        drawMessage(msg)
        drawHighlightBox("2", coordX, coordY)
        pygame.display.update()
        FPSCLOCK.tick()

def addToBoard(board, piece, boatsOnGrid):
    for x in range(TEMPLATEWIDTH):
        for y in range(TEMPLATEHEIGHT):
            if piece["rotation"][x][y] != BLANK:
                board[x + piece["x"]][y + piece["y"]] = SHIP

    boatsOnGrid.append(piece)
    return boatsOnGrid

def drawHighlightBox(boardnum, boxx, boxy):
    pixelx, pixely = convertToPixelCoords(boxx, boxy, boardnum)
    pygame.draw.rect(DISPLAYSURF, HIGHLIGHTCOLOR, (pixelx-2, pixely-2, CELLSIZE+4, CELLSIZE+4), 4)

def drawSurface(board1, board2):
    BGIMAGE = pygame.image.load("bgimage.png")
    BGIMAGE = pygame.transform.smoothscale(BGIMAGE, (WINDOWWIDTH, WINDOWHEIGHT))
    bgRect = BGIMAGE.get_rect()
    DISPLAYSURF.blit(BGIMAGE, bgRect)
    boardRect1 = pygame.Rect(X_MARGIN, Y_MARGIN, GRIDSIZE, GRIDSIZE)
    boardRect2 = pygame.Rect(X_MARGIN + X_MARGIN + GRIDSIZE, Y_MARGIN, GRIDSIZE, GRIDSIZE)
    pygame.draw.rect(DISPLAYSURF, LINECOLOR, boardRect1)
    pygame.draw.rect(DISPLAYSURF, LINECOLOR, boardRect2)

    for board in ("1", "2"):
        for x in range(BOARDWIDTH):
            for y in range(BOARDHEIGHT):
                if board == "1":
                    boardnum = board1
                else:
                    boardnum = board2
                pixelx, pixely = convertToPixelCoords(x, y, board)
                cell = pygame.Rect(pixelx, pixely, CELLSIZE, CELLSIZE)
                innercell = pygame.Rect(0, 0, INNER_CELLSIZE, INNER_CELLSIZE)
                innercell.centerx, innercell.centery = cell.centerx, cell.centery
                if boardnum[x][y] in (BLANK, MISS) or (board == "2" and boardnum[x][y] == SHIP):
                    pygame.draw.rect(DISPLAYSURF, BOARDCOLOR, cell)
                elif boardnum[x][y] in (SHIP, SUNK):
                    if board == "1":
                        pygame.draw.rect(DISPLAYSURF, SHIPCOLOR[0], cell)
                        pygame.draw.rect(DISPLAYSURF, SHIPCOLOR[1], innercell)
                    elif board == "2" and boardnum[x][y] == SUNK:
                        pygame.draw.rect(DISPLAYSURF, SHIPCOLOR[0], cell)
                        pygame.draw.rect(DISPLAYSURF, SHIPCOLOR[1], innercell)
                if boardnum[x][y] in (HIT, SUNK):
                    pygame.draw.rect(DISPLAYSURF, SHIPCOLOR[0], cell)
                    pygame.draw.rect(DISPLAYSURF, SHIPCOLOR[1], innercell)
                    pygame.draw.circle(DISPLAYSURF, HITCOLOR, (cell.centerx, cell.centery), int(CELLSIZE/2))
                elif boardnum[x][y] == MISS:
                    pygame.draw.circle(DISPLAYSURF, MISSCOLOR, (cell.centerx, cell.centery), int(CELLSIZE/2))
                if boardnum[x][y] == SUNK:
                    pygame.draw.line(DISPLAYSURF, LINECOLOR, (cell.left + 5, cell.top + 5), (cell.right - 5, cell.bottom - 5), 8)
                    pygame.draw.line(DISPLAYSURF, LINECOLOR, (cell.left + 5, cell.bottom - 5), (cell.right - 5, cell.top + 5), 8)

def getNewBoat(boatType):
    size = 0
    shape = BOATS[boatType]
    for x in range(TEMPLATEWIDTH):
        for y in range(TEMPLATEHEIGHT):
            if shape[0][x][y] != BLANK:
                size += 1
    newBoat = {"shape": shape,
               "rotation": shape[0],
               "orientation": "h",
               "x": 3,
               "y": 3,
               "size": size,
               "name": boatType
               }
    
    return newBoat

def rotatePiece(piece):
    if piece["orientation"] == "h":
        piece["orientation"] = "v"
        piece["rotation"] = piece["shape"][1]
    elif piece["orientation"] == "v":
        piece["orientation"] = "h"
        piece["rotation"] = piece["shape"][0]

    return piece

def createBoard():
    board = []
    for i in range(BOARDWIDTH):
        board.append([BLANK] * BOARDHEIGHT)
        
    return board

def drawMessage(msg):
    msgSurface = FONTOBJ.render(msg, True, FONTCOLOR)
    msgRect = msgSurface.get_rect()
    msgRect.center = (int(WINDOWWIDTH/2), int(Y_MARGIN/2-20))
    DISPLAYSURF.blit(msgSurface, msgRect)

def drawCoords():
    grid1 = pygame.Rect(X_MARGIN, Y_MARGIN, GRIDSIZE, GRIDSIZE)
    grid2 = pygame.Rect(X_MARGIN + X_MARGIN + GRIDSIZE, Y_MARGIN, GRIDSIZE, GRIDSIZE)
    for board in ("1", "2"):
        xPos = 0
        yPos = 0
        for x in range(10):
            pixelx, pixely = convertToPixelCoords(xPos, yPos, board)
            numSurface = FONTOBJ.render(str(x), True, FONTCOLOR)
            numRect = numSurface.get_rect()
            numRect.center = (pixelx + CELLSIZE/2, pixely - CELLSIZE/2)
            DISPLAYSURF.blit(numSurface, numRect)
            xPos += 1
        for y in range(10):
            pixelx, pixely = convertToPixelCoords(xPos, yPos, board)
            numSurface = FONTOBJ.render(str(y), True, FONTCOLOR)
            numRect = numSurface.get_rect()
            numRect.center = (pixelx + CELLSIZE/2, pixely + CELLSIZE/2)
            DISPLAYSURF.blit(numSurface, numRect)
            yPos += 1

def convertToPixelCoords(boxx, boxy, boardnum):
    pixely = Y_MARGIN + (boxy * CELLSIZE) + (boxy*LINEWIDTH + 1)
    if boardnum == "1":
        pixelx = X_MARGIN + (boxx * CELLSIZE) + (boxx*LINEWIDTH + 1)
    else:
        pixelx = 2*X_MARGIN + GRIDSIZE + (boxx * CELLSIZE) + (boxx*LINEWIDTH + 1)

    return pixelx, pixely

def isOnBoard(x, y):
    return x >= 0 and x < BOARDWIDTH and y >= 0 and y < BOARDHEIGHT
    
if __name__ == "__main__":
    main()

