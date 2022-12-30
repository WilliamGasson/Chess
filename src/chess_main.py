"""
chess_main.py

Driver file :  handles user inputs, displays board

Based off : https://www.youtube.com/watch?v=EnYui0e73Rs&t=9s&ab_channel=EddieSharick

Inputs : clicks to move pieces
         z undo move
         r reset move
         QRBN select piece for pawn promotion
"""

## TODO fix printing checkmate or stalemate


__date__ = "2022-12-28"
__author__ = "WilliamGasson"
__version__ = "0.1"


# %% --------------------------------------------------------------------------
# Imports
# -----------------------------------------------------------------------------

import pygame as p
import chess_engine as ce
import chess_computer as cc

# %% --------------------------------------------------------------------------
#  Constants
# -----------------------------------------------------------------------------

WIDTH = HEIGHT = 512  # could go 400
DIMENSION = 8  # dimension of chess board are 8 by 8
SQ_SIZE = HEIGHT // DIMENSION
MAX_FPS = 15  # for animation
IMAGES = {}


# %% --------------------------------------------------------------------------
# Load images to create a global dictionary of images, only called once
# -----------------------------------------------------------------------------


def loadImage():
    pieces = ["bR", "bN", "bB", "bQ", "bK", "bP", "wR", "wN", "wB", "wQ", "wK", "wP"]
    for piece in pieces:
        # can call an image by saying IMAGES['wP']
        IMAGES[piece] = p.image.load("../images/{}.png".format(piece))
        # scale to correct size for board
        IMAGES[piece] = p.transform.scale(IMAGES[piece], (SQ_SIZE, SQ_SIZE))


# %% --------------------------------------------------------------------------
# Main driver, user inputs and graphics
# -----------------------------------------------------------------------------


def main():
    p.init()
    screen = p.display.set_mode((WIDTH, HEIGHT))
    # screen.fill(p.Color("white"))
    loadImage()
    clock = p.time.Clock()
    gs = ce.GameState()

    validMoves = gs.getValidMoves()  # get a list of possible moves
    moveMade = False  # track when a move is made

    animate = False # flag variable for when variable should be annimated
    sqSelected = ()  # keep track of last click - tuple
    playerClicks = []  # keeps tack of player clicks - 2 tuples
    gameOver = False

    # 
    playerOne = True # if human play white, this will be true, if ai it will be false
    playerTwo = False # if human is plying black this will be true

    running = True
    while running:
        humanTurn = (gs.whiteToMove and playerOne) or (not gs.whiteToMove and playerTwo)

        for e in p.event.get():
            if e.type == p.QUIT:
                running = False

            # tracking mouse
            elif e.type == p.MOUSEBUTTONDOWN:
                if not gameOver and humanTurn:
                    location = p.mouse.get_pos()  # x,y location of mouse
                    col = location[0] // SQ_SIZE
                    row = location[1] // SQ_SIZE
                    if sqSelected == (row, col):  # select same box twice
                        sqSelected = ()  # deselect
                        playerClicks = []  # clear
                    else:
                        sqSelected = (row, col)
                        playerClicks.append(sqSelected)  # append first and second click
                    if len(playerClicks) == 2:  # selected piece and move
                        move = ce.Move(playerClicks[0], playerClicks[1], gs.board)
                        print(move.getChessNotation())
                        for i in range(len(validMoves)):
                            if move == validMoves[i]:
                                gs.makeMove(validMoves[i])
                                moveMade = True
                                animate = True
                                sqSelected = ()  # deselect
                                playerClicks = []  # clear
                        if not moveMade:
                            playerClicks = [sqSelected]

            # tracking keyboard
            elif e.type == p.KEYDOWN:
                if e.key == p.K_z:    # Z undos move
                    gs.undoMove()
                    moveMade = True
                    animate = False
            
                if e.key == p.K_r:    # R resets board
                    gs = ce.GameState()
                    validMoves = gs.getValidMoves()  # get a list of possible moves
                    moveMade = False  # track when a move is made
                    animate = False # flag variable for when variable should be annimated
                    sqSelected = ()  # keep track of last click - tuple
                    playerClicks = []
                    

        ## AI move finder
        if not gameOver and not humanTurn:
            AIMove = cc.findBestMoveMinMax(gs, validMoves)
            if AIMove is None:
                AIMove = cc.findRandomMove(validMoves)
                
            gs.makeMove(AIMove)
            moveMade = True
            animate = True        
        
        if moveMade:
            if animate:
                animateMove(gs.moveLog[-1], screen, gs.board, clock)
            validMoves = gs.getValidMoves()
            moveMade = False
            animate = False
        
        # TODO more efficient to draw when it changes instead of every frame
        drawGameSate(screen, gs,validMoves, sqSelected)
        
        if gs.checkmate:
            gameOver = True
            if gs.whiteToMove:
                drawText(screen, "Black wins by checkmate")
            else:
                drawText(screen, "White wins by checkmate")
        elif gs.stalemate:
            gameOver = True
            drawText(screen, "Stalemate")

        drawGameSate(screen, gs, validMoves, sqSelected)
        clock.tick(MAX_FPS)
        p.display.flip()



# %% --------------------------------------------------------------------------
# Draw board
# -----------------------------------------------------------------------------

def drawBoard(screen):
    # Set the colours of the board
    global colours 
    colours = [p.Color("white"), p.Color("gray")]
    # Loop through the squares
    for r in range(DIMENSION):
        for c in range(DIMENSION):
            # draw squares
            colour = colours[((r + c) % 2)]
            p.draw.rect(
                screen, colour, p.Rect(c * SQ_SIZE, r * SQ_SIZE, SQ_SIZE, SQ_SIZE)
            )
           

# %% --------------------------------------------------------------------------
# Highlight square selected and move for pieces selected
# -----------------------------------------------------------------------------

def highlightSquares(screen, gs, validMoves, sqSelected):
    if sqSelected != ():
        r,c =sqSelected
        if gs.board[r][c][0] == ("w" if gs.whiteToMove else "b"): # sqSelected is a piece you can move
            # highlight selected square
            s = p.Surface((SQ_SIZE,SQ_SIZE))
            s.set_alpha(100) # 0 transparent, 255 opaque
            s.fill(p.Color("blue"))
            screen.blit(s, (c*SQ_SIZE, r*SQ_SIZE))
            # highlight valid squares
            for move in validMoves:
                
                if move.startRow == r and move.startCol == c:
                    if gs.board[move.endRow][move.endCol] == "--":
                        s.fill(p.Color("green"))
                        screen.blit(s, (move.endCol*SQ_SIZE, move.endRow*SQ_SIZE))
                    else:
                        s.fill(p.Color("red"))
                        screen.blit(s, (move.endCol*SQ_SIZE, move.endRow*SQ_SIZE))


                

# %% --------------------------------------------------------------------------
# Draw the pieces
# -----------------------------------------------------------------------------

def drawPieces(screen, board):
    # Loop through the squares
    for r in range(DIMENSION):
        for c in range(DIMENSION):
            # draw pieces
            piece = board[r][c]
            if piece != "--":
                screen.blit(
                    IMAGES[piece], p.Rect(c * SQ_SIZE, r * SQ_SIZE, SQ_SIZE, SQ_SIZE)
                )


# %% --------------------------------------------------------------------------
# Animate moves
# -----------------------------------------------------------------------------
def animateMove(move, screen, board, clock):
    global colours
    dR = move.endRow - move.startRow
    dC = move.endCol - move.startCol
    framesPerSqare = 5
    frameCount = (abs(dR)+abs(dC)) * framesPerSqare
    for frame in range(frameCount + 1):
        r, c = (move.startRow + dR*frame/frameCount, move.startCol + dC*frame/frameCount)
        drawBoard(screen)
        drawPieces(screen, board)
        # erase from end square
        colour = colours[(move.endRow + move.endCol)%2]
        endSquare = p.Rect(move.endCol*SQ_SIZE, move.endRow*SQ_SIZE,SQ_SIZE,SQ_SIZE)
        p.draw.rect(screen,colour, endSquare)
        # draw captured piece until the other piece reaches it
        if move.pieceCaptured != "--":
            screen.blit(IMAGES[move.pieceCaptured], endSquare)
        #draw moving piece
        screen.blit(IMAGES[move.pieceMoved], p.Rect(c*SQ_SIZE,r*SQ_SIZE, SQ_SIZE,SQ_SIZE))
        p.display.flip()
        clock.tick(60)



# %% --------------------------------------------------------------------------
# Draw text
# -----------------------------------------------------------------------------

def drawText(screen, text):
    font = p.font.SysFont("Helvitca", 32, True, False)
    textOject = font.render(text, 0, p.Color("Gray"))
    textLocation = p.Rect(0,0, WIDTH, HEIGHT).move(WIDTH/2 - textOject.get_width()/2, HEIGHT/2 - textOject.get_height()/2)
    screen.blit(textOject, textLocation)
    textOject = font.render(text, 0, p.Color("Black"))
    screen.blit(textOject, textLocation.move(2,2))


# %% --------------------------------------------------------------------------
# Draw the current state
# -----------------------------------------------------------------------------

def drawGameSate(screen, gs, validMoves, sqSelected):
    # Set the colours of the board
    drawBoard(screen)
    highlightSquares(screen, gs, validMoves, sqSelected)
    drawPieces(screen, gs.board)


if __name__ == "__main__":
    main()
