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
DEPTH = 2

# %% --------------------------------------------------------------------------
# Random move computer
# -----------------------------------------------------------------------------

def findRandomMove(validMoves):
    return validMoves[random.randint(0, len(validMoves)-1)]


# %% --------------------------------------------------------------------------
#  Best move computer old
# -----------------------------------------------------------------------------

def findBestMoveGreedy(gs, validMoves):
    
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

def findMoveMinMaxDepthTwo(gs, validMoves):
    
    turnMultiplier = 1 if gs.whiteToMove else -1 # so you are always maximising
    opponentMinMaxScore = CHECKMATE
    bestPlayerMove = None
    random.shuffle(validMoves)
    for playerMove in validMoves:
        
        gs.makeMove(playerMove)
        opponentsMoves = gs.getValidMoves()
        
        if gs.stalemate:
            opponentMaxScore = -turnMultiplier * STALEMATE
        elif gs.checkmate:
            opponentMaxScore = CHECKMATE
        else:
            opponentMaxScore = - CHECKMATE

            for opponentMove in opponentsMoves:
                gs.makeMove(opponentMove)
                gs.getValidMoves()
                if gs.checkmate:
                    score = CHECKMATE
                elif gs.stalemate:
                    score = STALEMATE
                else:
                    score =  -turnMultiplier * scoreMaterial(gs.board)
                if score > opponentMaxScore:
                    opponentMaxScore = score
                gs.undoMove()

            if opponentMaxScore < opponentMinMaxScore:
                opponentMinMaxScore = opponentMaxScore
                bestPlayerMove = playerMove
            gs.undoMove()
    print(opponentMinMaxScore)
    return bestPlayerMove


# %% --------------------------------------------------------------------------
# Recursive method
# -----------------------------------------------------------------------------


def findBestMoveMinMax(gs, validMoves):
    global nextMove
    findMoveMinMax(gs, validMoves, DEPTH, gs.whiteToMove)
    return nextMove


def findMoveMinMax(gs, validMoves, depth, whiteToMove):
    global nextMove
    if depth == 0:
        return scoreMaterial(gs.board)
    
    if whiteToMove:
        maxScore = -CHECKMATE
        for move in validMoves:
            gs.makeMove(move)
            nextMoves = gs.getValidMoves()
            score = findMoveMinMax(gs, nextMoves, depth -1, False)
            if score > maxScore:
                maxScore = score
                if depth == DEPTH:
                    nextMove = move
            gs.undoMove()
        return maxScore    
                
    else:
        minScore = CHECKMATE
        for move in validMoves:
            gs.makeMove(move)
            nextMoves = gs.getValidMoves()
            score = findMoveMinMax(gs, nextMoves, depth -1, True)
            if score < minScore:
                minScore = score
                if depth == DEPTH:
                    nextMove = move
            gs.undoMove()
        return minScore   

# %% --------------------------------------------------------------------------
#  Score the value of piece
# -----------------------------------------------------------------------------
## TODO improve scoring method - position
## TODO - position: how many pieces it is attacking, protecting, squares it can move to
## TODO checks have more value - evaluate that first

def scoreMaterial(board):
    score = 0
    for row in board:
        for square in row:
            if square[0] == "w":
                score += pieceScore[square[1]]
            elif square[0] == "b":
                score -= pieceScore[square[1]]
                
    return score

def scoreBoard(gs):
    # positive score is good for white
    if gs.checkmate:
        if gs.whiteToMove:
            return - CHECKMATE # Black wins
        else:
            return CHECKMATE # White wins
    elif gs.stalemate:
        return STALEMATE
    
    score = 0
    for row in gs.board:
        for square in row:
            if square[0] == "w":
                score += pieceScore[square[1]]
            elif square[0] == "b":
                score -= pieceScore[square[1]]
                
    return score