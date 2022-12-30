"""
chess_computer.py

chess bot to play against
based off https://www.youtube.com/watch?v=-QHAPDk5tgs&ab_channel=EddieSharick
"""

__date__ = "2022-12-30"
__author__ = "WilliamGasson"
__version__ = "0.1"


# %% --------------------------------------------------------------------------
# Imports
# -----------------------------------------------------------------------------
import random

# %% --------------------------------------------------------------------------
# Set piece values
# -----------------------------------------------------------------------------

pieceScore = {"K":0, "Q":9, "R": 5, "B": 3, "N": 3, "P":1}
CHECKMATE = 1000
STALEMATE = 0


# %% --------------------------------------------------------------------------
# Random move computer
# -----------------------------------------------------------------------------

def findRandomMove(validMoves):
    return validMoves[random.randint(0, len(validMoves)-1)]


# %% --------------------------------------------------------------------------
#  Best move computer
# -----------------------------------------------------------------------------

def findBestMove(gs, validMoves):
    
    turnMultiplier = 1 if gs.whiteToMove else -1 # so you are always maximising
    
    maxScore = -CHECKMATE
    bestMove = None
    for playerMove in validMoves:
        
        gs.makeMove(playerMove)
        
        if gs.checkmate:
            score = CHECKMATE
        elif gs.stalemate:
            score = STALEMATE
        else:
            score =  turnMultiplier * scoreMaterial(gs.board)
        
        if score > maxScore :
            maxScore = score
            bestMove = playerMove
        print(score)
        gs.undoMove()
            
    return bestMove
# %% --------------------------------------------------------------------------
#  Score the value of piece
# -----------------------------------------------------------------------------
## TODO improve scoring method - position
## TODO move checkmate and stale mate into score
def scoreMaterial(board):
    score = 0
    for row in board:
        for square in row:
            if square[0] == "w":
                score += pieceScore[square[1]]
            elif square[0] == "b":
                score -= pieceScore[square[1]]
                
    return score