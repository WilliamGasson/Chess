"""
chess_engine.py

Stores state data for the game, calcuates valid moves and move log
"""

__date__ = "2022-12-28"
__author__ = "WilliamGasson"
__version__ = "0.1"


## TODO fix check and checkmate
## TODO add a bot
## TODO reinforcement learning bot
## TODO add to website

# %% --------------------------------------------------------------------------
# GameState class
# -----------------------------------------------------------------------------


class GameState:
    def __init__(self):
        # board is an 8x8 2d list where each peice has the first char as the colour and second as the type, -- is empty
        self.board = [
            ["bR", "bN", "bB", "bQ", "bK", "bB", "bN", "bR"],
            ["bP", "bP", "bP", "bP", "bP", "bP", "bP", "bP"],
            ["--", "--", "--", "--", "--", "--", "--", "--"],
            ["--", "--", "--", "--", "--", "--", "--", "--"],
            ["--", "--", "--", "--", "--", "--", "--", "--"],
            ["--", "--", "--", "--", "--", "--", "--", "--"],
            ["wP", "wP", "wP", "wP", "wP", "wP", "wP", "wP"],
            ["wR", "wN", "wB", "wQ", "wK", "wB", "wN", "wR"],
        ]
        self.moveFunctions = {
            "K": self.getKingMoves,
            "Q": self.getQueenMoves,
            "R": self.getRookMoves,
            "N": self.getKnightMoves,
            "B": self.getBishopMoves,
            "P": self.getPawnMoves,
        }
        self.whiteToMove = True
        # TODO self.allyColour 
        # TODO self.enemyColour
        self.moveLog = []
        self.whiteKingLocation = (7, 4)
        self.blackKingLocation = (0, 4)
        
        self.inCheck = False
        self.pins = []
        self.checks = []
        self.checkmate = False
        self.stalemate = False
        
        self.enpassantPossible = () # coordinates for the square where an enpassant is possible
        
        self.currentCastleRights = CastleRights(True,True,True,True)
        self.castleRightsLog = [CastleRights(self.currentCastleRights.wks, self.currentCastleRights.bks, 
                                             self.currentCastleRights.wqs, self.currentCastleRights.bqs)]

    def makeMove(self, move):

        self.board[move.endRow][move.endCol] = move.pieceMoved
        self.board[move.startRow][move.startCol] = "--"  # replace piece with empty square

        self.moveLog.append(move)  # log move
        self.whiteToMove = not self.whiteToMove  # swap player
        # track king
        if move.pieceMoved == "wK":
            self.whiteKingLocation = (move.endRow, move.endCol)
        elif move.pieceMoved == "bK":
            self.blackKingLocation = (move.endRow, move.endCol)
            
        # If pawn move 2 squares next move can be an en passant
        if move.pieceMoved[1] == "P" and abs(move.startRow - move.endRow) == 2:
            self.enpassantPossible = ((move.startRow + move.endRow)//2, move.startCol)
        else:
            self.enpassantPossible = ()
            
        # enpassant move
        if move.isEnpassantMove:
            self.board[move.startRow][move.endCol] = "--"    
            
        # pawn promotion
        if move.isPawnPromotion:
            promotedPiece = input("Promote to Q, R, B or N:") # can add UI to make it better
            self.board[move.endRow][move.endCol] = move.pieceMoved[0] + promotedPiece # modify if you want to give option of other pieces
        
        # Castle move
        if move.isCastleMove:
            if move.endCol - move.startCol == 2: # King side
                self.board[move.endRow][move.endCol-1] = self.board[move.endRow][move.endCol+1] # move rook
                self.board[move.endRow][move.endCol+1] = "--" # move rook
            else:
                self.board[move.endRow][move.endCol+1] = self.board[move.endRow][move.endCol-2] # move rook
                self.board[move.endRow][move.endCol-2] = "--" # move rook                
        
        # Castling rights
        self.updateCastleRights(move)
        self.castleRightsLog.append(CastleRights(self.currentCastleRights.wks, self.currentCastleRights.bks, 
                                             self.currentCastleRights.wqs, self.currentCastleRights.bqs))

        

    def undoMove(self):

        if len(self.moveLog) != 0:  # not the first move
            move = self.moveLog.pop()
            self.board[move.startRow][move.startCol] = move.pieceMoved  # move piece back
            self.board[move.endRow][move.endCol] = move.pieceCaptured  # replace captured piece
            self.whiteToMove = not self.whiteToMove  # swap player
            
            # track king
            if move.pieceMoved == "wK":
                self.whiteKingLocation = (move.endRow, move.endCol)
            elif move.pieceMoved == "bK":
                self.blackKingLocation = (move.endRow, move.endCol)
                
            # undo enpassant move
            if move.isEnpassantMove:
                self.board[move.endRow][move.endCol] = "--" # leave the landing square blank
                self.board[move.startRow][move.endCol] = move.pieceCaptured
                self.enpassantPossible = (move.endRow, move.endCol)
                
            # undo a 2 square pawn advance
            if move.pieceMoved[1] == "P" and abs(move.startRow - move.endRow)==2:
                self.enpassantPossible = ()
            
            # give back castle rights
            self.castleRightsLog.pop() # remove castling rights from log
            self.currentCastleRights = self.castleRightsLog[-1] # set rights to the new last entry of log
            
            if move.isCastleMove:
                if move.endCol - move.startCol == 2: # King side
                    self.board[move.endRow][move.endCol+1] = self.board[move.endRow][move.endCol-1] # move rook
                    self.board[move.endRow][move.endCol-1] = "--" # move rook
                else:
                    self.board[move.endRow][move.endCol-2] = self.board[move.endRow][move.endCol+1] # move rook
                    self.board[move.endRow][move.endCol+1] = "--" # move rook   

    def getValidMoves(self):
    # Checking move is legal

        moves = []
        self.inCheck, self.pins, self.checks = self.checkForPinsAndChecks()
        print(self.inCheck, self.pins, self.checks)
        if self.whiteToMove:
            kingRow = self.whiteKingLocation[0]
            kingCol = self.whiteKingLocation[1]
        else:
            kingRow = self.blackKingLocation[0]
            kingCol = self.blackKingLocation[1] 
        if self.inCheck:
            if len(self.checks) == 1: # only 1 check, so block check or move king
                moves = self.getAllPossibleMoves()  
                   
                # to block check you must move a piece between king and enemy piece
                check = self.checks[0]
                checkRow = check[0]
                checkCol = check[1]
                pieceChecking = self.board[checkRow][checkCol]
                validSquares = [] # squares that miece can move to
                # if knight must capture knight or move king
                if pieceChecking[1] == "N":
                    validSquares = [(checkRow, checkCol)]
                else:
                    for i in range(1,8):
                        validSquare = (kingRow + check[2] * i, kingCol + check[3] * i) # check[2]a dn check[3]are the directions
                        validSquares.append(validSquare)
                        if validSquare[0]== checkRow and validSquare[1] == checkCol:
                            break 
                for i in range(len(moves) - 1, -1, -1): # go through list backward as removing items from list
                    if moves[i].pieceMoved[1] != "K":
                        if not (moves[i].endRow,moves[i].endCol) in validSquares:
                            moves.remove(moves[i])                  
            else: # double check
                self.getKingMoves(kingRow, kingCol, moves)
        else: # not in check
            # Generate possible moves
            moves = self.getAllPossibleMoves()
            
            self.getCastleMoves(kingRow,kingCol,moves)                                

        
        if len(moves) == 0:
            if self.incheck():
                self.checkmate = True
                print("checkmate")
            else:
                self.stalemate = True
                print("stalemate")

        else:
            self.checkmate = False
            self.stalemate = False
            

        return moves
        
    def getAllPossibleMoves(self):
    # Create moves each piece can play

        moves = []
        for r in range(len(self.board)):
            for c in range(len(self.board[r])):
                turn = self.board[r][c][0]  # Which colour piece you are looking at
                if (turn == "w" and self.whiteToMove) or (
                    turn == "b" and not self.whiteToMove
                ):
                    piece = self.board[r][c][1]  # What the piece is
                    self.moveFunctions[piece](r, c, moves)  # Calls move functions

        return moves

    def checkForPinsAndChecks(self):
        pins = [] # Squares where a piece is pinned and direction it is pinned from
        checks = [] # Squares where there is a check from
        inCheck = False
        
        if self.whiteToMove:
            enemyColour = "b"
            allyColour = "w"
            startRow = self.whiteKingLocation[0] # TODO compress into one row
            startCol = self.whiteKingLocation[1]
        else:
            enemyColour = "w"
            allyColour = "b"
            startRow = self.blackKingLocation[0]
            startCol = self.blackKingLocation[1]
        # Check outwards from the king for pins and checks
        directions = ((-1,0), (0,-1), (1,0), (0,1),
                      (-1,-1), (-1,1), (1,-1), (1,1))
        
        for j in range(len(directions)):
            d= directions[j]
            possiblePin = () 
            for i in range(1,8): 
                endRow = startRow +d[0] * i
                endCol = startCol + d[1] * i
                if 0 <= endRow < 8 and 0 <= endCol < 8:
                    endPiece = self.board[endRow][endCol]
                    if endPiece[0] == allyColour and endPiece[1] != "K":
                        if possiblePin == (): # 1st allied pin so could be pinned
                            possiblePin = (endRow, endCol, d[0], d[1])
                        else: # 2nd allied peice so not a pin or check
                            break     
                    elif endPiece[0] == enemyColour:
                        type = endPiece[1]
                        # 5 possibilities here
                        # 1) orthoganally away from king and piece is a rook
                        # 2) diagonally away from king and piece is a bishop
                        # 3) 1 square away diagonally from king and piece is a pawn
                        # 4) any direction away is a queen
                        # 5) any direction 1 square away and piece is a king
                        if (0<=j <=3 and type =="R") or \
                            (4<=j<=7 and type =="B") or \
                            (i == 1 and type =="P" and ((enemyColour == "w" and 6<=j<=7) or enemyColour == "b" and 4<=j <=5)) or \
                            (type == "Q") or (i == 1 and type =="K"):
                            if possiblePin == (): # no blocking piece
                                inCheck = True
                                checks.append((endRow, endCol, d[0], d[1]))
                                break
                            else: # piece blocking so pin
                                pins.append(possiblePin)
                                break
                        else: # enemy piece not applying check
                            break
        knightMoves = ((-2,-1),
                      (-2,1),
                      (-1,-2),
                      (-1,2),
                      (1,-2),
                      (1,2),
                      (2,-1),
                      (2,1))
        for m in knightMoves:
            endRow = startRow +m[0]
            endCol = startCol + m[1]
            if 0<= endRow<8 and 0<=endCol<8:
                endPiece = self.board[endRow][endCol]
                endPiece = self.board[endRow][endCol]
                if endPiece[0] == enemyColour and endPiece[1] =="N":
                    inCheck = True
                    checks.append((endRow,endCol, m[0], m[1]))
        return inCheck, pins, checks
                                       
    def incheck(self):
        if self.whiteToMove:
            return self.squareUnderAttack(
                self.whiteKingLocation[0], self.whiteKingLocation[1]
            )
        else:
            return self.squareUnderAttack(
                self.blackKingLocation[0], self.blackKingLocation[1]
            )

    def squareUnderAttack(self, r, c):
        self.whiteToMove = not self.whiteToMove  # switch to get opponents moves
        oppMoves = self.getAllPossibleMoves()
        self.whiteToMove = not self.whiteToMove  # switch back
        for move in oppMoves:
            if move.endRow == r and move.endCol == c:  # square is being attacked
                return True
        return False        
    
    def getKingMoves(self, r, c, moves):
        rowMoves = (-1,-1,-1,0,0,1,1,1)
        colMoves = (-1,0,1,-1,1,-1,0,1)
        allyColour = "w" if self.whiteToMove else "b"

        for i in range(len(rowMoves)):
            endRow = r + rowMoves[i]
            endCol = c + colMoves[i]            
            if 0 <= endRow < 8 and 0 <= endCol < 8:  # only check the board
                endPiece = self.board[endRow][endCol]
                if endPiece[0] != allyColour:
                    if allyColour == "w":
                        self.whiteKingLocation = (endRow,endCol)
                    else:
                        self.blackKingLocation = (endRow, endCol)
                    inCheck, pins, checks = self.checkForPinsAndChecks()
                    if not inCheck:
                        moves.append(Move((r,c),(endRow,endCol), self.board))
                    # place king back on orignal location
                    if allyColour == "w":
                        self.whiteKingLocation = (r,c)
                    else:
                        self.blackKingLocation = (r,c)
    
    def getCastleMoves(self, r, c, moves):
        if self.squareUnderAttack(r, c):
            return # Can't castle in check
        if (self.whiteToMove and self.currentCastleRights.wks) or (not self.whiteToMove and self.currentCastleRights.bks):
            self.getKingSideCastleMoves(r, c, moves)
            
        if (self.whiteToMove and self.currentCastleRights.wqs) or (not self.whiteToMove and self.currentCastleRights.bqs):
            self.getQueenSideCastleMoves(r, c, moves)
    
    def getKingSideCastleMoves(self, r, c, moves): 
        if self.board[r][c+1] == "--" and self.board[r][c+2] == "--":
            if not self.squareUnderAttack(r, c+1) and not self.squareUnderAttack(r, c + 2):
                moves.append(Move((r,c), (r, c+2),self.board, isCastleMove = True))
            
    def getQueenSideCastleMoves(self, r, c, moves):
        if self.board[r][c-1] == "--" and self.board[r][c-2] == "--" and self.board[r][c-3] == "--":
            if not self.squareUnderAttack(r, c - 1) and not self.squareUnderAttack(r, c - 2):
                moves.append(Move((r,c), (r, c - 2),self.board, isCastleMove = True))
                      
    def updateCastleRights(self, move):
        if move.pieceMoved == "wK":
            self.currentCastleRights.wks = False
            self.currentCastleRights.wqs = False
        elif move.pieceMoved == "bK":
            self.currentCastleRights.bks = False
            self.currentCastleRights.bqs = False        
        elif move.pieceMoved == "wR":
            if move.startRow == 7:
                if move.startCol == 7: 
                    self.currentCastleRights.wks = False
                elif move.startCol == 0:
                    self.currentCastleRights.wqs = False        
        elif move.pieceMoved == "bR":
                if move.startCol == 7: 
                    self.currentCastleRights.bks = False
                elif move.startCol == 0:
                    self.currentCastleRights.bqs = False    
    
    ## TODO add pins for queen                            
    def getQueenMoves(self, r, c, moves):
        
        piecePinned = False
        pinDirection = ()
        for i in range(len(self.pins)-1,-1,-1):
            if self.pins[i][0] == r and self.pins[i][1] == c:
                piecePinned = True
                pinDirection = (self.pins[i][2], self.pins[i][3])
                self.pins.remove(self.pins[i])
                break


        directions = ((-1, -1),(1, -1),(1, 1),(-1, 1),
                      (-1, 0),(0, -1),(1, 0),(0, 1),)  # up left down right
        
        enemyColour = "b" if self.whiteToMove else "w"
        for d in directions:
            for i in range(1, 8):  # loop through directions
                endRow = r + d[0] * i
                endCol = c + d[1] * i
                if 0 <= endRow < 8 and 0 <= endCol < 8:  # only check the board
                    if not piecePinned or pinDirection == d or pinDirection == (-d[0],-d[1]):
                        endPiece = self.board[endRow][endCol]
                        if endPiece == "--":  # no piece so keep searching
                            moves.append(Move((r, c), (endRow, endCol), self.board))
                        elif endPiece[0] == enemyColour:  # a piece you can capture
                            moves.append(Move((r, c), (endRow, endCol), self.board))
                            break
                        else:  # piece you can't take
                            break
                    else:  # piece pinned
                        break
                else:  #  off the board
                    break

    def getRookMoves(self, r, c, moves):
        piecePinned = False
        pinDirection = ()
        for i in range(len(self.pins)-1,-1,-1):
            if self.pins[i][0] == r and self.pins[i][1] == c:
                piecePinned = True
                pinDirection = (self.pins[i][2], self.pins[i][3])
                if self.board[r][c][1] != "Q": # can't remove queen from pin on rook move only bishop moves
                    self.pins.remove(self.pins[i])
                break
        
        directions = ((-1, 0), (0, -1), (1, 0), (0, 1))  # up left down right
        enemyColour = "b" if self.whiteToMove else "w"
        for d in directions:
            for i in range(1, 8):  # loop through directions
                endRow = r + d[0] * i
                endCol = c + d[1] * i
                if 0 <= endRow < 8 and 0 <= endCol < 8:  # only check the board
                    if not piecePinned or pinDirection == d or pinDirection == (-d[0],-d[1]):
                        endPiece = self.board[endRow][endCol]
                        if endPiece == "--":  # no piece so keep searching
                            moves.append(Move((r, c), (endRow, endCol), self.board))
                        elif endPiece[0] == enemyColour:  # a piece you can capture
                            moves.append(Move((r, c), (endRow, endCol), self.board))
                            break
                        else:  # piece you can't take
                            break
                    else:  # piece pinned
                        break
                else:  #  off the board
                    break

    def getKnightMoves(self, r, c, moves):
        
        piecePinned = False
        for i in range(len(self.pins)-1,-1,-1):
            if self.pins[i][0] == r and self.pins[i][1] == c:
                piecePinned = True
                self.pins.remove(self.pins[i])
                break
        
        directions = (
            (1, 2),
            (-1, 2),
            (1, -2),
            (-1, -2),
            (2, 1),
            (-2, 1),
            (2, -1),
            (-2, -1),
        )  # up left down right
        enemyColour = "b" if self.whiteToMove else "w"
        for d in directions:
            endRow = r + d[0]
            endCol = c + d[1]
            if 0 <= endRow < 8 and 0 <= endCol < 8:  # only check the board
                if not piecePinned:
            
                    endPiece = self.board[endRow][endCol]
                    if (endPiece[0] == enemyColour or endPiece == "--"):  # a piece you can capture
                        moves.append(Move((r, c), (endRow, endCol), self.board))

    def getBishopMoves(self, r, c, moves):
        piecePinned = False
        pinDirection = ()
        for i in range(len(self.pins)-1,-1,-1):
            if self.pins[i][0] == r and self.pins[i][1] == c:
                piecePinned = True
                pinDirection = (self.pins[i][2], self.pins[i][3])
                self.pins.remove(self.pins[i])
                break
        
        directions = ((-1, -1), (1, -1), (1, 1), (-1, 1))  # up left down right
        enemyColour = "b" if self.whiteToMove else "w"
        for d in directions:
            for i in range(1, 8):  # loop through directions
                endRow = r + d[0] * i
                endCol = c + d[1] * i
                if 0 <= endRow < 8 and 0 <= endCol < 8:  # only check the board
                    if not piecePinned or pinDirection ==d or pinDirection == (-d[0], -d[1]):
                        endPiece = self.board[endRow][endCol]
                        if endPiece == "--":  # no piece so keep searching
                            moves.append(Move((r, c), (endRow, endCol), self.board))
                        elif endPiece[0] == enemyColour:  # a piece you can capture
                            moves.append(Move((r, c), (endRow, endCol), self.board))
                            break
                        else:  # piece you can't take
                            break
                    else:  #  off the board
                        break

    def getPawnMoves(self, r, c, moves):
        
        piecePinned = False
        pinDirection = ()
        for i in range(len(self.pins)-1,-1,-1):
            if self.pins[i][0] == r and self.pins[i][1] == c:
                piecePinned = True
                pinDirection = (self.pins[i][2], self.pins[i][3])
                self.pins.remove(self.pins[i])
                break
         
        if self.whiteToMove:  # white pawns
            
            moveAmount = -1
            startRow = 6
            backRow = 0
            enemyColour = "b"
        else:
            moveAmount = 1
            startRow = 1
            backRow = 7
            enemyColour = "w"
        pawnPromotion = False
            
            
        if self.board[r + moveAmount][c] == "--":  # nothing blocking the move
            if not piecePinned or pinDirection == (moveAmount,0):
                if r + moveAmount == backRow: # if pawn gets to back row it will promote
                    pawnPromotion = True
                moves.append(Move((r, c), (r + moveAmount, c), self.board, isPawnPromotion = pawnPromotion))
                
                if r == startRow and self.board[r + 2 * moveAmount][c] == "--": # 2 square move
                    moves.append(Move((r, c), (r + 2 * moveAmount, c), self.board))
                    
        # capture to left
        if c - 1 >= 0:  # not at the edge of the board
            if not piecePinned or pinDirection == (moveAmount, -1):
                if (self.board[r + moveAmount][c - 1][0] == enemyColour):  # there is a black piece that can be captured
                    if r + moveAmount == backRow: # if pawn gets to back row it will promote
                        pawnPromotion = True
                    moves.append(Move((r, c), (r + moveAmount, c -1), self.board, isPawnPromotion = pawnPromotion))
                    
                if (r + moveAmount, c - 1) == self.enpassantPossible:
                    moves.append(Move((r, c), (r + moveAmount, c - 1), self.board, isEnpassantMove = True))

        # capture to right
        if c + 1 <= 7:  # not at the edge of the board
            if not piecePinned or pinDirection == (moveAmount, 1):
                if (self.board[r + moveAmount][c + 1][0] == enemyColour):  # there is a black piece that can be captured
                    if r + moveAmount == backRow: # if pawn gets to back row it will promote
                        pawnPromotion = True
                    moves.append(Move((r, c), (r + moveAmount, c + 1), self.board, isPawnPromotion = pawnPromotion))
                if (r + moveAmount, c + 1) == self.enpassantPossible:
                    moves.append(Move((r, c), (r + moveAmount, c + 1), self.board, isEnpassantMove = True))

            
# %% --------------------------------------------------------------------------
# CastleRights class
# -----------------------------------------------------------------------------

class CastleRights():
    def __init__(self, wks, bks, wqs, bqs):
        self.wks = wks
        self.bks = bks
        self.wqs = wqs
        self.bqs = bqs


# %% --------------------------------------------------------------------------
# Move class
# -----------------------------------------------------------------------------


class Move:
    # maps keys to vales
    ranksToRows = {"1": 7, "2": 6, "3": 5, "4": 4,
                   "5": 3, "6": 2, "7": 1, "8": 0}
    rowsToRanks = {v: k for k, v in ranksToRows.items()}

    filesToCols = {"a": 0, "b": 1, "c": 2, "d": 3,
                   "e": 4, "f": 5, "g": 6, "h": 7}
    colsToFiles = {v: k for k, v in filesToCols.items()}

    def __init__(self, startSq, endSq, board, isPawnPromotion = False, isEnpassantMove=False, isCastleMove=False):
        self.startRow = startSq[0]
        self.startCol = startSq[1]
        self.endRow = endSq[0]
        self.endCol = endSq[1]
        self.pieceMoved = board[self.startRow][self.startCol]
        self.pieceCaptured = board[self.endRow][self.endCol]  # piece captured can be blank
        
        self.isPawnPromotion = isPawnPromotion
        
        self.isEnpassantMove = isEnpassantMove
        if self.isEnpassantMove:
            self.pieceCaptured = "wP" if self.pieceMoved == "bP" else "bP"
        
        self.isCastleMove = isCastleMove
        
        self.moveID = self.startRow * 1000 + self.startCol * 100 + self.endRow * 10 + self.endCol

    def __eq__(self, other):
        if isinstance(other, Move):
            return self.moveID == other.moveID
        return False

    def getChessNotation(self):
        return self.getRankFile(self.startRow, self.startCol) + self.getRankFile(
            self.endRow, self.endCol
        )

    def getRankFile(self, r, c):
        return self.colsToFiles[c] + self.rowsToRanks[r]
