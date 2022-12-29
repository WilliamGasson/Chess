"""
chess_engine.py

Stores state data for the game, calcuates valid moves and move log
"""

__date__ = "2022-12-28"
__author__ = "WilliamGasson"
__version__ = "0.1"


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
        self.moveLog = []
        self.whiteKingLocation = (7, 4)
        self.blackKingLocation = (0, 4)
        self.inCheck = False
        self.pins = []
        self.checks = []
        self.checkmate = False
        self.stalemate = False
        self.enpassantPossible = () # coordinates for the square where an enpassant is possible


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
            
        # pawn promotion
        if move.isPawnPromotion:
            self.board[move.endRow][move.endCol] = move.pieceMoved[0]+"Q" # modify if you want to give option of other pieces

        # enpassant move
        if move.isEnpassantMove:
            self.board[move.startRow][move.endCol] = "--"

        #update enpassantPossible variable
        if move.pieceMoved[1] == "P" and abs(move.startRow - move.endRow) == 2:
            self.enpassantPossible = ((move.startRow + move.endRow)//2, move.startCol)
        else:
            self.enpassantPossible = ()

    def undoMove(self):

        if len(self.moveLog) != 0:  # not the first move
            move = self.moveLog.pop()
            self.board[move.startRow][
                move.startCol
            ] = move.pieceMoved  # move piece back
            self.board[move.endRow][
                move.endCol
            ] = move.pieceCaptured  # replace captured piece
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
            # undo a 2 square paun advance
            if move.pieceMoved[1] == "P" and abs(move.startRow - move.endRow)==2:
                self.enpassantPossible = ()
            
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
                                

    def getQueenMoves(self, r, c, moves):

        directions = (
            (-1, -1),
            (1, -1),
            (1, 1),
            (-1, 1),
            (-1, 0),
            (0, -1),
            (1, 0),
            (0, 1),
        )  # up left down right
        enemyColour = "b" if self.whiteToMove else "w"
        for d in directions:
            for i in range(1, 8):  # loop through directions
                endRow = r + d[0] * i
                endCol = c + d[1] * i
                if 0 <= endRow < 8 and 0 <= endCol < 8:  # only check the board
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

    def getRookMoves(self, r, c, moves):
        piecePinned = False
        pinDirection = ()
        for i in range(len(self.pins)-1,-1,-1):
            if self.pins[i][0] == r and self.pins[i][1] == c:
                piecePinned = True
                pinDirection = (self.pins[i][2], self.pins[1][3])
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
                pinDirection = (self.pins[i][2], self.pins[1][3])
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
                pinDirection = (self.pins[i][2], self.pins[1][3])
                self.pins.remove(self.pins[i])
                break
         
        if self.whiteToMove:  # white pawns
            if self.board[r - 1][c] == "--":  # nothing blocking the move
                if not piecePinned or pinDirection == (-1,0):
                    moves.append(Move((r, c), (r - 1, c), self.board))
                    if r == 6 and self.board[r - 2][c] == "--":  # 2 square pawn move
                        moves.append(Move((r, c), (r - 2, c), self.board))
            # capture to left
            if c - 1 >= 0:  # not at the edge of the board
                if (self.board[r - 1][c - 1][0] == "b"):  # there is a black piece that can be captured
                    if not piecePinned or pinDirection == (-1,-1):
                        moves.append(Move((r, c), (r - 1, c - 1), self.board))
                elif (r-1,c-1) == self.enpassantPossible:
                    moves.append(Move((r, c), (r - 1, c - 1), self.board, isEnpassantMove = True))

            # capture to right
            if c + 1 <= 7:  # not at the edge of the board
                if (self.board[r - 1][c + 1][0] == "b"):  # there is a black piece that can be captured
                    if not piecePinned or pinDirection == (-1,1):
                        moves.append(Move((r, c), (r - 1, c + 1), self.board))
                elif (r-1,c+1) == self.enpassantPossible:
                    moves.append(Move((r, c), (r - 1, c + 1), self.board, isEnpassantMove = True))

        else:  # black pawn moves
            if self.board[r + 1][c] == "--":  # nothing blocking the move
                if not piecePinned or pinDirection == (1,0):
                    moves.append(Move((r, c), (r + 1, c), self.board))
                    if r == 1 and self.board[r + 2][c] == "--":  # 2 square pawn move
                        moves.append(Move((r, c), (r + 2, c), self.board))
            # capture to left
            if c - 1 >= 0:  # not at the edge of the board
                if (self.board[r + 1][c - 1][0] == "w"):  # there is a black piece that can be captured
                    if not piecePinned or pinDirection == (1,-1):
                        moves.append(Move((r, c), (r + 1, c - 1), self.board))
                elif (r+1,c-1) == self.enpassantPossible:
                    moves.append(Move((r, c), (r + 1, c - 1), self.board), isEnpassantMove = True)
            # capture to right
            if c + 1 <= 7:  # not at the edge of the board
                if (self.board[r + 1][c + 1][0] == "w"):  # there is a black piece that can be captured
                    if not piecePinned or pinDirection == (1,1):
                        moves.append(Move((r, c), (r + 1, c + 1), self.board))
                elif (r+1,c+1) == self.enpassantPossible:
                    moves.append(Move((r, c), (r + 1, c + 1), self.board), isEnpassantMove = True)
        # Add enpassen and promotion of non queen

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

    def getValidMoves(self):
    # Checking move is legal
        self.inCheck, self.pins, self.checks = self.checkForPinsAndChecks()
        if self.whiteToMove:
            kingRow = self.whiteKingLocation[0]
            kingCol = self.whiteKingLocation[1]
        else:
            kingRow = self.blackKingLocation[0]
            kingCol = self.blackKingLocation[1] 
        if self.inCheck:
            if len(self.checks)==1: # only 1 check, so block check or move king
                moves = self.getAllPossibleMoves()     
                # to block check you must move a piece between king and enemy piece
                check = self.checks[0]
                checkRow = check[0]
                checkCol = check[1]
                pieceChecking = self.board[checkRow][checkCol]
                validSquares = [] # squares that miece can move to
                # if knight must capture knight or move king
                if pieceChecking[1] -- "N":
                    validSquares = [(checkRow, checkCol)]
                else:
                    for i in range(1,8):
                        validSquare = (kingRow+check[2]*i, kingCol+check[3]*i)# check[2]a dn check[3]are the directions
                        validSquares.append(validSquare)
                        if validSquare[0]== checkRow and validSquare[1] == checkCol:
                            break 
                for i in range(len(moves)-1,-1,-1): # go through list backward as removing items from list
                    if moves[i].pieceMoved[1] != "K":
                        if not (moves[i].endrow,moves[i].endCol) in validSquares:
                            moves.remove(moves[i])                  
            else: # double check
                self.getKingMoves(kingRow,kingCol,moves)
        else: # not in check
            # Generate possible moves
            moves = self.getAllPossibleMoves()
                
        return moves

            
        # # Make the moves
        # for i in range(len(moves) - 1, -1, -1):  # loop from end of list to start
        #     self.makeMove(moves[i])
        #     self.whiteToMove = not self.whiteToMove
        #     # See opponent moves checks
        #     if self.incheck():
        #         moves.remove(moves[i])
        #     self.whiteToMove = not self.whiteToMove
        #     self.undoMove()
        # print(len(moves))
        # if len(moves) == 0:
        #     if self.incheck():
        #         self.checkmate = True
        #         print("checkmate")
        #     else:
        #         self.stalemate = True
        #         print("stalemate")

        # else:
        #     self.checkmate = False
        #     self.stalemate = False

    def checkForPinsAndChecks(self):
        pins = [] # Squares where a piece is pinned and direction it is pinned from
        checks = [] # Squares where there is a check from
        inCheck = False
        
        if self.whiteToMove:
            enemyColour = "b"
            allyColour = "w"
            startRow = self.whiteKingLocation[0]
            startCol = self.whiteKingLocation[1]
        else:
            enemyColour = "w"
            allyColour = "b"
            startRow = self.blackKingLocation[0]
            startCol = self.blackKingLocation[1]
        # Check outwards from the king for pins and checks
        directions = ((-1,0),
                      (0,-1),
                      (1,0),
                      (0,1),
                      (-1,-1),
                      (-1,1),
                      (1,-1),
                      (1,1))
        
        for j in range(len(directions)):
            d= directions[j]
            possiblePin = () 
            for i in range(1,8): 
                endRow = startRow +d[0]*i
                endCol = startRow + d[1]*i
                if 0 <= endRow < 8 and 0 <= endCol <8:
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
            if 0<= endRow<8 and 0<=endRow<8:
                endPiece = self.board[endRow][endCol]
                endPiece = self.board[endRow][endCol]
                if endPiece[0] == enemyColour and endPiece[1] =="N":
                    inCheck = True
                    checks.append((endRow,endCol, m[0], m[1]))
        return inCheck, pins,checks
                                       
            
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


# %% --------------------------------------------------------------------------
# Move class
# -----------------------------------------------------------------------------


class Move:
    # maps keys to vales
    ranksToRows = {"1": 7, "2": 6, "3": 5, "4": 4, "5": 3, "6": 2, "7": 1, "8": 0}
    filesToCols = {"a": 0, "b": 1, "c": 2, "d": 3, "e": 4, "f": 5, "g": 6, "h": 7}
    rowsToRanks = {v: k for k, v in ranksToRows.items()}
    colsToFiles = {v: k for k, v in filesToCols.items()}

    def __init__(self, startSq, endSq, board, isEnpassantMove = False):
        self.startRow = startSq[0]
        self.startCol = startSq[1]
        self.endRow = endSq[0]
        self.endCol = endSq[1]
        self.pieceMoved = board[self.startRow][self.startCol]
        self.pieceCaptured = board[self.endRow][self.endCol]  # piece captured can be blank
        self.isPawnPromotion = (self.pieceMoved == "wP" and self.endRow == 0) or (self.pieceMoved == "bP" and self.endRow ==7)
        self.isEnpassantMove = isEnpassantMove
        if self.isEnpassantMove:
            self.pieceCaptured = "wP" if self.pieceMoved == "bP" else "bP"
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
