"""
chess_engine.py

stores state data for the game, calcuates valid moves and move log
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
        self.checkmate = False
        self.stalemate = False

    """
    Executes normal moves
    """

    def makeMove(self, move):
        self.board[move.startRow][
            move.startCol
        ] = "--"  # replace piece with empty square
        self.board[move.endRow][move.endCol] = move.pieceMoved
        self.moveLog.append(move)  # log move
        self.whiteToMove = not self.whiteToMove  # swap player
        # track king
        if move.pieceMoved == "wK":
            self.whiteKingLocation = (move.endRow, move.endCol)
        elif move.pieceMoved == "bK":
            self.blackKingLocation = (move.endRow, move.endCol)

    """
    Undoes moves
    """

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

    """
    Get king moves
    """

    def getKingMoves(self, r, c, moves):
        directions = (
            (1, 0),
            (1, 1),
            (0, 1),
            (-1, 1),
            (-1, 0),
            (-1, -1),
            (0, -1),
            (1, -1),
        )  # up left down right
        enemyColour = "b" if self.whiteToMove else "w"
        for i in range(len(directions)):
            endRow = r + directions[i][0]
            endCol = c + directions[i][1]
            if 0 <= endRow < 8 and 0 <= endCol < 8:  # only check the board
                endPiece = self.board[endRow][endCol]
                if (
                    endPiece[0] == enemyColour or endPiece == "--"
                ):  # a piece you can capture
                    moves.append(Move((r, c), (endRow, endCol), self.board))

    """
    Get queen moves
    """

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

    """
    Get rook moves
    """

    def getRookMoves(self, r, c, moves):
        directions = ((-1, 0), (0, -1), (1, 0), (0, 1))  # up left down right
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

    """
    Get knight moves
    """

    def getKnightMoves(self, r, c, moves):
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
                endPiece = self.board[endRow][endCol]
                if (
                    endPiece[0] == enemyColour or endPiece == "--"
                ):  # a piece you can capture
                    moves.append(Move((r, c), (endRow, endCol), self.board))

    """
    Get bishop moves
    """

    def getBishopMoves(self, r, c, moves):
        directions = ((-1, -1), (1, -1), (1, 1), (-1, 1))  # up left down right
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

    """
    Get pawn moves
    """

    def getPawnMoves(self, r, c, moves):
        if self.whiteToMove:  # white pawns
            if self.board[r - 1][c] == "--":  # nothing blocking the move
                moves.append(Move((r, c), (r - 1, c), self.board))
                if r == 6 and self.board[r - 2][c] == "--":  # 2 square pawn move
                    moves.append(Move((r, c), (r - 2, c), self.board))
            # capture to left
            if c - 1 >= 0:  # not at the edge of the board
                if (
                    self.board[r - 1][c - 1][0] == "b"
                ):  # there is a black piece that can be captured
                    moves.append(Move((r, c), (r - 1, c - 1), self.board))
            # capture to right
            if c + 1 <= 7:  # not at the edge of the board
                if (
                    self.board[r - 1][c + 1][0] == "b"
                ):  # there is a black piece that can be captured
                    moves.append(Move((r, c), (r - 1, c + 1), self.board))

        else:  # black pawn moves
            if self.board[r + 1][c] == "--":  # nothing blocking the move
                moves.append(Move((r, c), (r + 1, c), self.board))
                if r == 1 and self.board[r + 2][c] == "--":  # 2 square pawn move
                    moves.append(Move((r, c), (r + 2, c), self.board))
            # capture to left
            if c - 1 >= 0:  # not at the edge of the board
                if (
                    self.board[r + 1][c - 1][0] == "w"
                ):  # there is a black piece that can be captured
                    moves.append(Move((r, c), (r + 1, c - 1), self.board))
            # capture to right
            if c + 1 <= 7:  # not at the edge of the board
                if (
                    self.board[r + 1][c + 1][0] == "w"
                ):  # there is a black piece that can be captured
                    moves.append(Move((r, c), (r + 1, c + 1), self.board))

        # add pawn promotion or enpassen

    """
    Create moves each piece can play
    """

    def getAllPossibleMoves(self):
        moves = []
        for r in range(len(self.board)):
            for c in range(len(self.board[r])):
                turn = self.board[r][c][0]  # which colour piece you are looking at
                if (turn == "w" and self.whiteToMove) or (
                    turn == "b" and not self.whiteToMove
                ):
                    piece = self.board[r][c][1]  # what the piece is
                    self.moveFunctions[piece](r, c, moves)  # calls move functions

        return moves

    """
    Checking move is legal
    """

    def getValidMoves(self):
        # generate possible moves
        moves = self.getAllPossibleMoves()
        # make the moves
        for i in range(len(moves) - 1, -1, -1):  # loop from end of list to start
            self.makeMove(moves[i])
            self.whiteToMove = not self.whiteToMove
            # see opponent moves checks
            if self.incheck():
                moves.remove(moves[i])
            self.whiteToMove = not self.whiteToMove
            self.undoMove()
        print(len(moves))
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

    def __init__(self, startSq, endSq, board):
        self.startRow = startSq[0]
        self.startCol = startSq[1]
        self.endRow = endSq[0]
        self.endCol = endSq[1]
        self.pieceMoved = board[self.startRow][self.startCol]
        self.pieceCaptured = board[self.endRow][
            self.endCol
        ]  # piece captured can be blank
        self.moveID = (
            self.startRow * 1000 + self.startCol * 100 + self.endRow * 10 + self.endCol
        )

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
