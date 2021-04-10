

class GameState:
    def __init__(self):
        # Board is 8x8 2D list with each element having two characters
        # (representing colour and type of piece) with "--" representing
        # an empty space
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
        self.chessboard = self.board[:]
        self.moveFunction = {'P': self.getPawnMoves, 'R': self.getRookMoves,
                             'B': self.getBishopMoves, 'N': self.getKnightMoves,
                             'Q': self.getQueenMoves, 'K': self.getKingMoves}
        self.whiteToMove = True
        self.moveLog = []
        self.whiteKingLocation = (7, 4)
        self.blackKingLocation = (0, 4)
        self.checkmate = False
        self.stalemate = False
        self.enpassantPossible = ()  # square where enpassant capture is possible
        self.currentCastlingRight = CastleRights(True, True, True, True)  # updates for if the rights change
        self.castleRightsLog = [CastleRights(self.currentCastlingRight.wks, self.currentCastlingRight.bks, self.currentCastlingRight.wqs,self.currentCastlingRight.bqs)]  # checks if the pieces have moved and whether we need to remove rights

    def makeMove(self, move, board='gs'):
        if board == 'gs':
            board = self.board
        elif board == 'chessboard':
            board = self.chessboard
        board[move.endRow][move.endCol] = board[move.startRow][move.startCol]
        board[move.startRow][move.startCol] = "--"
        self.moveLog.append(move)  # Logs the moves
        self.whiteToMove = not self.whiteToMove   # Switches the turn

        # Updating the Kings location
        if move.pieceMoved == "wK":
            self.whiteKingLocation = (move.endRow, move.endCol)
        elif move.pieceMoved == "bK":
            self.blackKingLocation = (move.endRow, move.endCol)

        # Pawn Promotion
        if move.isPawnPromotion:
            board[move.endRow][move.endCol] = move.pieceMoved[0] + 'Q'

        # Enpassant Move
        if move.isEnpassantMove:
            board[move.startRow][move.endCol] = '--'  # This captures the pawn

        # Update our enpassantPossible variable after every move to see if an enpassant move
        # possible. Need to check if it's a pawn and if it's moving twice
        if move.pieceMoved[1] == 'P' and abs(move.startRow - move.endRow) == 2:  #only for two square pawn moves
            self.enpassantPossible = ((move.startRow + move.endRow)//2, move.startCol) # takes the average of the two move and updates that to be an enpassantPossible
        else:
            self.enpassantPossible = ()

        # Castling
        if move.isCastleMove:
            if move.endCol - move.startCol == 2:   # King side castle
                board[move.endRow][move.endCol - 1] = board[move.endRow][move.endCol+1] # Copies Rook to new square
                board[move.endRow][move.endCol + 1] = '--'   # removes the old Rook
            else:    # Queen side castle
                board[move.endRow][move.endCol + 1] = board[move.endRow][move.endCol - 2]  # Copies Rook to new square
                board[move.endRow][move.endCol - 2] = '--'  # removes the old Rook

        # Updating currentCastlingRight:
        # updates if there is a rook or a king move
        self.updateCastleRights(move)
        self.castleRightsLog.append(CastleRights(self.currentCastlingRight.wks, self.currentCastlingRight.bks, self.currentCastlingRight.wqs, self.currentCastlingRight.bqs))

    '''
    Undo Move using z button
    '''

    def undoMove(self):
        if len(self.moveLog) != 0:
            move = self.moveLog.pop()
            self.board[move.startRow][move.startCol] = move.pieceMoved
            self.board[move.endRow][move.endCol] = move.pieceCaptured
            self.whiteToMove = not self.whiteToMove

        # Updating the Kings location
        if move.pieceMoved == "wK":
            self.whiteKingLocation = (move.startRow, move.startCol)
        elif move.pieceMoved == "bK":
            self.blackKingLocation = (move.startRow, move.startCol)

        # Undo enpassant move
        if move.isEnpassantMove:
            self.board[move.endRow][move.endCol] = '--'    # leave landed square blank
            self.board[move.startRow][move.endCol] = move.pieceCaptured
            self.enpassantPossible = (move.endRow, move.endCol)

        # Undo on two square pawn advance to set the possible back to nothing
        if move.pieceMoved[1] == 'P' and abs(move.startRow - move.endRow) == 2:
            self.enpassantPossible = ()

        # Undo Castle Move
        if move.isCastleMove:
            if move.endCol - move.startCol == 2:   # King Side
                self.board[move.endRow][move.endCol+1] = self.board[move.endRow][move.endCol-1]
                self.board[move.endRow][move.endCol-1] = '--'
            else:
                self.board[move.endRow][move.endCol-2] = self.board[move.endRow][move.endCol+1]
                self.board[move.endRow][move.endCol + 1] = '--'

        # Undo Castling Rights
        self.castleRightsLog.pop()    # get rid of the new castle rights
        newRights = self.castleRightsLog[-1]
        self.currentCastlingRight = CastleRights(newRights.wks,newRights.bks,newRights.wqs,newRights.bqs)

    def updateCastleRights(self, move):
        if move.pieceMoved == 'wK':
            self.currentCastlingRight.wks = False
            self.currentCastlingRight.wqs = False
        elif move.pieceMoved == 'bK':
            self.currentCastlingRight.bks = False
            self.currentCastlingRight.bqs = False
        elif move.pieceMoved == 'wR':   # need to check which white rook moved
            if move.startRow == 7:
                if move.startCol == 0:     # LEFT ROOK
                    self.currentCastlingRight.wqs = False
                if move.startCol == 7:    # RIGHT ROOK
                    self.currentCastlingRight.wks = False
        elif move.pieceMoved == 'bR':   # need to check which black rook moved
            if move.startRow == 0:
                if move.startCol == 0:     # LEFT ROOK
                    self.currentCastlingRight.bqs = False
                if move.startCol == 7:    # RIGHT ROOK
                    self.currentCastlingRight.bks = False

    '''
    All moves considering checks. So cannot move a pawn out of the way of 
    defending the king. Need to check the opponents possible moves after you
    move to validate your move.
    So:
        make move, 
        generate all possible moves for opponent, 
        see if any moves can attack king,
        if king is safe then make it a valid move and add to valid move list
    '''
    def getValidMoves(self, board='gs'):
        if board == 'gs':
            board = self.board
        elif board == 'chessboard':
            board = self.chessboard
        tempEnpassantPossible = self.enpassantPossible
        tempCastleRights = CastleRights(self.currentCastlingRight.wks, self.currentCastlingRight.bks,
                                        self.currentCastlingRight.wqs, self.currentCastlingRight.bqs)
        # make move,
        moves = self.getAllPossibleMoves()
        # generate castling moves
        if self.whiteToMove:
            self.getCastleMoves(self.whiteKingLocation[0], self.whiteKingLocation[1], moves)
        else:
            self.getCastleMoves(self.blackKingLocation[0], self.blackKingLocation[1], moves)
        # generate all possible moves for opponent,
        for i in range(len(moves)-1, -1, -1):
            self.makeMove(moves[i])
            # see if any moves can attack king
            self.whiteToMove = not self.whiteToMove
            # if in check then not a valid move
            if self.inCheck():
                moves.remove(moves[i])
            # if king is safe then make it a valid move and add to valid move list
            self.whiteToMove = not self.whiteToMove
            self.undoMove()

        if len(moves) == 0:  # neither checkmate or stalemate
            if self.inCheck():
                self.checkmate = True
            else:
                self.stalemate = True

        self.enpassantPossible = tempEnpassantPossible
        self.currentCastlingRight = tempCastleRights
        return moves


    '''
    See if each sides king is in check
    '''
    def inCheck(self):   # Determines if the current player is in check
        if self.whiteToMove:
            # print(self.squareUnderAttack(self.whiteKingLocation[0], self.whiteKingLocation[1]))
            return self.squareUnderAttack(self.whiteKingLocation[0], self.whiteKingLocation[1])
        else:
            # print(self.squareUnderAttack(self.blackKingLocation[0], self.blackKingLocation[1]))
            return self.squareUnderAttack(self.blackKingLocation[0], self.blackKingLocation[1])

    '''
    Determines if the enemy can attack the square r, c
    '''
    def squareUnderAttack(self, r, c):
        self.whiteToMove = not self.whiteToMove  # switches to opponents turn
        oppMoves = self.getAllPossibleMoves()
        self.whiteToMove = not self.whiteToMove
        for move in oppMoves:
            if move.endRow == r and move.endCol == c:
                return True
        return False

    '''
    All moves without checks. Considers moves that do not step into or 
    past other pieces.
    '''
    def getAllPossibleMoves(self, board='gs'):
        if board == 'gs':
            board = self.board
        elif board == 'chessboard':
            board = self.chessboard
        moves = []
        for r in range(len(board)):
            for c in range(len(board[r])):   # length of current row we are looking at for cols
                turn = board[r][c][0]
                if (turn == 'w' and self.whiteToMove) or (turn == 'b' and not self.whiteToMove):
                    piece = board[r][c][1]
                    self.moveFunction[piece](r, c, moves)   # calls the function without lots of if functions
        return moves
    '''
    Gets all the piece moves for the piece at r, c and add these moves to the list
    '''
    def getPawnMoves(self, r, c, moves, board='gs'):
        if board == 'gs':
            board = self.board
        elif board == 'chessboard':
            board = self.chessboard
        if self.whiteToMove:            # white to move
            if board[r-1][c] == "--":
                moves.append(Move((r, c), (r-1, c), board))
                if r == 6 and board[r-2][c] == "--":
                    moves.append(Move((r, c), (r-2, c), board))
            if c-1 >= 0:   # captures to the left
                if board[r-1][c-1][0] == 'b':  # checks for enemy piece to capture
                    moves.append(Move((r, c), (r-1, c-1), board))
                elif ((r-1), (c-1)) == self.enpassantPossible:
                    moves.append(Move((r, c), (r-1, c-1), board, isEnpassantMove=True))
            if c+1 <= 7:  # captures to the right
                if board[r-1][c+1][0] == 'b':
                    moves.append(Move((r, c), (r - 1, c + 1), board))
                elif ((r-1), (c+1)) == self.enpassantPossible:
                    moves.append(Move((r, c), (r-1, c+1), board, isEnpassantMove=True))

        else:   # black pawn moves
            if board[r+1][c] == "--":
                moves.append(Move((r, c), (r + 1, c), board))
                if r == 1 and board[r+2][c] == "--":
                    moves.append(Move((r, c), (r + 2, c), board))
            if c - 1 >= 0:  # captures to the left
                if board[r + 1][c - 1][0] == 'w':  # checks for enemy piece to capture
                    moves.append(Move((r, c), (r + 1, c - 1), board))
                elif ((r+1), (c-1)) == self.enpassantPossible:
                    moves.append(Move((r, c), (r+1, c-1), board, isEnpassantMove=True))
            if c + 1 <= 7:  # captures to the right
                if board[r + 1][c + 1][0] == 'w':
                    moves.append(Move((r, c), (r + 1, c + 1), board))
                elif ((r+1), (c+1)) == self.enpassantPossible:
                    moves.append(Move((r, c), (r+1, c+1), board, isEnpassantMove=True))

    def getRookMoves(self, r, c, moves, board='gs'):
        if board == 'gs':
            board = self.board
        elif board == 'chessboard':
            board = self.chessboard
        directions = ((-1, 0), (0, -1), (1, 0), (0, 1))  # Direction of Up Left Down Right
        enemyColor = "b" if self.whiteToMove else "w"
        for d in directions:
            for i in range(1, 8):
                endRow = r + d[0] * i
                endCol = c + d[1] * i
                if 0 <= endRow < 8 and 0 <= endCol < 8:
                    endPiece = board[endRow][endCol]
                    if endPiece == "--":
                        moves.append(Move((r, c), (endRow, endCol), board))
                    elif endPiece[0] == enemyColor:
                        moves.append(Move((r, c), (endRow, endCol), board))
                        break
                    else:
                        break
                else:
                    break

    def getBishopMoves(self, r, c, moves, board='gs'):
        if board == 'gs':
            board = self.board
        elif board == 'chessboard':
            board = self.chessboard
        directions = ((-1, -1), (-1, 1), (1, -1), (1, 1))  # Direction of TopLeft TopRight BotLeft BotRight
        enemyColor = "b" if self.whiteToMove else "w"
        for d in directions:
            for i in range(1, 8):
                endRow = r + d[0] * i
                endCol = c + d[1] * i
                if 0 <= endRow < 8 and 0 <= endCol < 8:
                    endPiece = board[endRow][endCol]
                    if endPiece == "--":
                        moves.append(Move((r, c), (endRow, endCol), board))
                    elif endPiece[0] == enemyColor:
                        moves.append(Move((r, c), (endRow, endCol), board))
                        break
                    else:
                        break
                else:
                    break

    def getKnightMoves(self, r, c, moves, board='gs'):
        if board == 'gs':
            board = self.board
        elif board == 'chessboard':
            board = self.chessboard
        knightMoves = ((-2, -1), (-2, 1), (-1, -2), (-1, 2), (1, -2), (1, 2), (2, -1), (2, 1))
        allyColor = "w" if self.whiteToMove else "b"
        for m in knightMoves:
            endRow = r + m[0]
            endCol = c + m[1]
            if 0 <= endRow < 8 and 0 <= endCol < 8:
                endPiece = board[endRow][endCol]
                if endPiece[0] != allyColor:
                    moves.append(Move((r, c), (endRow, endCol), board))

    def getQueenMoves(self, r, c, moves):
        self.getRookMoves(r, c, moves)
        self.getBishopMoves(r, c, moves)

    def getKingMoves(self, r, c, moves, board='gs'):
        if board == 'gs':
            board = self.board
        elif board == 'chessboard':
            board = self.chessboard
        kingMoves = ((-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 1), (1, -1), (1, 0), (1, 1))
        allyColor = "w" if self.whiteToMove else "b"
        for i in range(8):
            endRow = r + kingMoves[i][0]
            endCol = c + kingMoves[i][1]
            if 0 <= endRow < 8 and 0 <= endCol < 8:
                endPiece = board[endRow][endCol]
                if endPiece[0] != allyColor:
                    # print(Move((r, c), (endRow, endCol), board))
                    moves.append(Move((r, c), (endRow, endCol), board))

    '''
    Generate all valid castle moves for the king and add them to the list of allowed moves
    '''
    def getCastleMoves(self, r, c, moves):
        if self.squareUnderAttack(r, c):
            return   # Can't castle while in check
        if (self.whiteToMove and self.currentCastlingRight.wks) or (not self.whiteToMove and self.currentCastlingRight.bks):
            self.getKingSideCastleMoves(r, c, moves)
        if (self.whiteToMove and self.currentCastlingRight.wqs) or (not self.whiteToMove and self.currentCastlingRight.bqs):
            self.getQueenSideCastleMoves(r, c, moves)

    def getKingSideCastleMoves(self, r, c, moves, board='gs'):
        if board == 'gs':
            board = self.board
        elif board == 'chessboard':
            board = self.chessboard
        if board[r][c+1] == '--' and board[r][c+2] == '--':
            if not self.squareUnderAttack(r, c+1) and not self.squareUnderAttack(r,c+2):
                moves.append(Move((r, c), (r, c+2), board, isCastleMove=True))

    def getQueenSideCastleMoves(self, r, c, moves, board='gs'):
        if board == 'gs':
            board = self.board
        elif board == 'chessboard':
            board = self.chessboard
        if board[r][c-1] == '--' and board[r][c-2] == '--' and board[r][c-3] == '--':
            if not self.squareUnderAttack(r, c-1) and not self.squareUnderAttack(r, c-2):
                moves.append(Move((r,c), (r,c-2), board, isCastleMove=True))


class CastleRights:
    def __init__(self, wks, bks, wqs, bqs):
        self.wks = wks
        self.bks = bks
        self.wqs = wqs
        self.bqs = bqs


class Move:
    # We are flipping our top left representing (0,0) to proper chess
    # notation where instead the bottom left represents (0,0). Further
    # changing our columns from numbers to letters so bottom left is now
    # (0, a) and top left is (8,a)
    ranksToRows = {"1": 7, "2": 6, "3": 5, "4": 4,
                   "5": 3, "6": 2, "7": 1, "8": 0}
    rowsToRanks = {v: k for k, v in ranksToRows.items()}

    filesToCols = {"a": 0, "b": 1, "c": 2, "d": 3,
                   "e": 4, "f": 5, "g": 6, "h": 7}
    colsToFiles = {v: k for k, v in filesToCols.items()}

    def __init__(self, startSq, endSq, board, isEnpassantMove=False, isCastleMove=False):
        self.startRow = startSq[0]
        self.startCol = startSq[1]
        self.endRow = endSq[0]
        self.endCol = endSq[1]

        self.pieceMoved = board[self.startRow][self.startCol]
        self.pieceCaptured = board[self.endRow][self.endCol]

        # Pawn Promotion
        self.isPawnPromotion = (self.pieceMoved == 'wP' and self.endRow == 0) or (self.pieceMoved == 'bP' and self.endRow == 7)

        # Enpassant
        self.isEnpassantMove = isEnpassantMove

        if self.isEnpassantMove:
            self.pieceCaptured = 'wP' if self.pieceMoved == 'bP' else 'bP'

        # Castling
        self.isCastleMove = isCastleMove

        self.moveID = self.startRow * 1000 + self.startCol * 100 + self.endRow * 10 + self.endCol

        self.stored = (startSq, endSq, board, False, False)
    '''
    Overriding the eq method
    '''
    def __eq__(self, other):
        if isinstance(other, Move):
            return self.moveID == other.moveID
        return False

    def getChessNotation(self):
        return self.getRankFile(self.startRow, self.startCol) + self.getRankFile(self.endRow, self.endCol)

    def getRankFile(self, r, c):
        return self.colsToFiles[c] + self.rowsToRanks[r]



