"""
chess_main.py

driver file :  handles user inputs, displays board
needs to be replaced if an online version - engine the same
"""

__date__ = "2022-12-28"
__author__ = "WilliamGasson"
__version__ = "0.1"


# %% --------------------------------------------------------------------------
# Imports
# -----------------------------------------------------------------------------

import pygame as p
import chess_engine as ce


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
        IMAGES[piece] = p.image.load("images/{}.png".format(piece))
        # scale to correct size for board
        IMAGES[piece] = p.transform.scale(IMAGES[piece], (SQ_SIZE, SQ_SIZE))


# %% --------------------------------------------------------------------------
# Draw the current state
# -----------------------------------------------------------------------------


def drawGameSate(screen, gs):
    # Set the colours of the board
    colours = [p.Color("white"), p.Color("gray")]
    # Loop through the squares
    for r in range(DIMENSION):
        for c in range(DIMENSION):
            # draw squares
            colour = colours[((r + c) % 2)]
            p.draw.rect(
                screen, colour, p.Rect(c * SQ_SIZE, r * SQ_SIZE, SQ_SIZE, SQ_SIZE)
            )
            # draw pieces
            piece = gs.board[r][c]
            if piece != "--":
                screen.blit(
                    IMAGES[piece], p.Rect(c * SQ_SIZE, r * SQ_SIZE, SQ_SIZE, SQ_SIZE)
                )


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

    sqSelected = ()  # keep track of last click - tuple
    playerClicks = []  # keeps tack of player clicks - 2 tuples

    running = True
    while running:
        for e in p.event.get():
            if e.type == p.QUIT:
                running = False

            # tracking mouse
            elif e.type == p.MOUSEBUTTONDOWN:
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
                            sqSelected = ()  # deselect
                            playerClicks = []  # clear
                    if not moveMade:
                        playerClicks = [sqSelected]

            # tracking keyboard
            elif e.type == p.KEYDOWN:
                # Z undos move
                if e.key == p.K_z:
                    gs.undoMove()
                    moveMade = True

        if moveMade:
            validMoves = gs.getValidMoves()
            moveMade = False

        drawGameSate(screen, gs)
        clock.tick(MAX_FPS)
        p.display.flip()


if __name__ == "__main__":
    main()
