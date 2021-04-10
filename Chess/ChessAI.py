import main
import ChessEngine
import ChessAIML
import os
import numpy as np
from numpy import random
import chess.polyglot
import chess.engine

root = os.path.join(os.getcwd(), 'Chess')
gs = ChessEngine.GameState()
pieces = ['P', 'R', 'N', 'B', 'Q', 'K']
values = [100, 500, 350, 350, 900, 2000]
piece_value = dict(zip(pieces, values))
polyboard = chess.Board()


class Calculations:

    vs_ai = False
    vs_ml = False
    stockfish = True

    best_move = 0
    opening_move = 0

    pawnstable = np.array([
        [0, 0, 0, 0, 0, 0, 0, 0],
        [5, 10, 10, -20, -20, 10, 10, 5],
        [5, -5, -10, 0, 0, -10, -5, 5],
        [0, 0, 0, 20, 20, 0, 0, 0],
        [5, 5, 10, 25, 25, 10, 5, 5],
        [10, 10, 20, 30, 30, 20, 10, 10],
        [50, 50, 50, 50, 50, 50, 50, 50],
        [0, 0, 0, 0, 0, 0, 0, 0]])

    pawnstable_black = np.array([
        [0, 0, 0, 0, 0, 0, 0, 0],
        [50, 50, 50, 50, 50, 50, 50, 50],
        [10, 10, 20, 30, 30, 20, 10, 10],
        [5, 5, 10, 25, 25, 10, 5, 5],
        [0, 0, 0, 20, 20, 0, 0, 0],
        [5, -5, -10, 0, 0, -10, -5, 5],
        [5, 10, 10, -20, -20, 10, 10, 5],
        [0, 0, 0, 0, 0, 0, 0, 0]])

    knightstable = np.array([
        [-50, -40, -30, -30, -30, -30, -40, -50],
        [-40, -20, 0, 5, 5, 0, -20, -40],
        [-30, 5, 10, 15, 15, 10, 5, -30],
        [-30, 0, 15, 20, 20, 15, 0, -30],
        [-30, 5, 15, 20, 20, 15, 0, -30],
        [-30, 0, 10, 15, 15, 10, 0, -30],
        [-40, -20, 0, 0, 0, 0, -20, -40],
        [-50, -40, -30, -30, -30, -30, -40, -50]
    ])

    bishopstable = np.array([
        [-20, -10, -10, -10, -10, -10, -10, -20],
        [-10, 5, 0, 0, 0, 0, 5, -10],
        [-10, 10, 10, 10, 10, 10, 10, -10],
        [-10, 0, 10, 10, 10, 10, 0, -10],
        [-10, 5, 5, 10, 10, 5, 5, -10],
        [-10, 0, 5, 10, 10, 5, 0, -10],
        [-10, 0, 0, 0, 0, 0, 0, -10],
        [-20, -10, -10, -10, -10, -10, -10, -20]
    ])

    rookstable = np.array([
        [0, 0, 0, 5, 5, 0, 0, 0],
        [-5, 0, 0, 0, 0, 0, 0, -5],
        [-5, 0, 0, 0, 0, 0, 0, -5],
        [-5, 0, 0, 0, 0, 0, 0, -5],
        [-5, 0, 0, 0, 0, 0, 0, -5],
        [-5, 0, 0, 0, 0, 0, 0, -5],
        [5, 10, 10, 10, 10, 10, 10, 5],
        [0, 0, 0, 0, 0, 0, 0, 0]
    ])

    queenstable = np.array([
        [-20, -10, -10, -5, -5, -10, -10, -20],
        [-10, 0, 5, 0, 0, 0, 0, -10],
        [-10, 5, 5, 5, 5, 5, 0, -10],
        [0, 0, 5, 5, 5, 5, 0, -5],
        [-5, 0, 5, 5, 5, 5, 0, -5],
        [-10, 0, 5, 5, 5, 5, 0, -10],
        [-10, 0, 0, 0, 0, 0, 0, -10],
        [-20, -10, -10, -5, -5, -10, -10, -20]
    ])

    kingstable = np.array([
        [20, 30, 10, 0, 0, 10, 30, 20],
        [20, 20, 0, 0, 0, 0, 20, 20],
        [-10, -20, -20, -20, -20, -20, -20, -10],
        [-20, -30, -30, -40, -40, -30, -30, -20],
        [-30, -40, -40, -50, -50, -40, -40, -30],
        [-30, -40, -40, -50, -50, -40, -40, -30],
        [-30, -40, -40, -50, -50, -40, -40, -30],
        [-30, -40, -40, -50, -50, -40, -40, -30]])

    @staticmethod
    def get_board_score(board):
        material = Calculations.get_material_scores(board)

        if gs.whiteToMove:
            pawns = Calculations.get_position_scores(board, Calculations.pawnstable, piece_in='P')
            knights = Calculations.get_position_scores(board, Calculations.knightstable, piece_in='N')
            bishops = Calculations.get_position_scores(board, Calculations.bishopstable, piece_in='B')
            rooks = Calculations.get_position_scores(board, Calculations.rookstable, piece_in='R')
            queens = Calculations.get_position_scores(board, Calculations.queenstable, piece_in='Q')
            kings = Calculations.get_position_scores(board, Calculations.kingstable, piece_in='K')
        elif not gs.whiteToMove:
            pawns = Calculations.get_position_scores(board, Calculations.pawnstable[::-1], piece_in='P')
            knights = Calculations.get_position_scores(board, Calculations.knightstable[::-1], piece_in='N')
            bishops = Calculations.get_position_scores(board, Calculations.bishopstable[::-1], piece_in='B')
            rooks = Calculations.get_position_scores(board, Calculations.rookstable[::-1], piece_in='R')
            queens = Calculations.get_position_scores(board, Calculations.queenstable[::-1], piece_in='Q')
            kings = Calculations.get_position_scores(board, Calculations.kingstable[::-1], piece_in='K')

        score = material + pawns + knights + bishops + rooks + queens + kings
        return score

    @staticmethod
    def get_position_scores(board, table, piece_in):
        white = 0
        black = 0
        for r in range(main.DIMENSION):
            for c in range(main.DIMENSION):
                piece = board[r][c]
                if piece != '--':
                    if piece[1] == piece_in:
                        if piece[0] == gs.whiteToMove:
                            white += table[r][c]
                        else:
                            black += table[r][c]
        position_score = white - black
        return position_score

    @staticmethod
    def get_material_scores(board):
        white = 0
        black = 0
        for r in range(main.DIMENSION):
            for c in range(main.DIMENSION):
                piece = board[r][c]
                if piece != '--':
                    if piece[0] == gs.whiteToMove:
                        white += piece_value[piece[1]]
                    else:
                        black += piece_value[piece[1]]
        material_score = white - black
        return material_score

    @staticmethod
    def stock_score(board, depth):
        with chess.engine.SimpleEngine.popen_uci(root + '/books/stockfish.exe') as sf:
            result = sf.analyse(board, chess.engine.Limit(depth=depth))
            score = result['score'].white().score()
            move = result['pv'][0]
            return score, move


class AI:
    INFINITE = 1000000

    @staticmethod
    def get_ai_move():
        depth = 1
        if Calculations.vs_ml:
            try:
                ml_move = AI.openings()
                engine_move, ai_clicks = AI.convert_book_to_engine(ml_move)
                Calculations.best_move, Calculations.opening_move = engine_move, ml_move
            except:
                ml_move = ChessAIML.against_player(polyboard, depth)
                if ml_move not in polyboard.legal_moves:
                    ml_move = ChessAIML.against_player(polyboard, depth)
                engine_move, ai_clicks = AI.convert_book_to_engine(ml_move)
                Calculations.best_move, Calculations.opening_move = engine_move, ml_move
            return engine_move, ml_move

        elif Calculations.vs_ai:
            try:
                ml_move = AI.openings()
                engine_move, ai_clicks = AI.convert_book_to_engine(ml_move)
                Calculations.best_move, Calculations.opening_move = engine_move, ml_move
            except:
                if Calculations.stockfish:
                    score, sf_move = Calculations.stock_score(polyboard, depth)
                    engine_move, ai_clicks = AI.convert_book_to_engine(sf_move)
                    Calculations.best_move, Calculations.opening_move = engine_move, sf_move
                else:
                    best_move = 0
                    best_score = -AI.INFINITE
                    a = -AI.INFINITE
                    b = AI.INFINITE
                    for move in polyboard.legal_moves:
                        polyboard.push(move)
                        score = AI.alphabeta(polyboard, depth - 1, a, b, True)
                        if score > best_score:
                            best_score = score
                            best_move = move
                        if score > a:
                            a = score
                        polyboard.pop()
                    engine_move, ai_clicks = AI.convert_book_to_engine(str(best_move))
                    ml_move = best_move
                    Calculations.best_move, Calculations.opening_move = engine_move, ml_move
                return engine_move, ml_move


    @staticmethod
    def alphabeta(polyboard, depth, a, b, maximizing):
        if depth == 0 or polyboard.is_game_over():
            return AI.quiesce(polyboard, depth, a, b)

        if maximizing:
            best_score = -np.inf
            for move in polyboard.legal_moves:
                polyboard.push(move)
                best_score = max(best_score, AI.alphabeta(polyboard, depth - 1, a, b, False))
                polyboard.pop()
                a = max(a, best_score)
                if b <= a:
                    break
            return best_score
        elif not maximizing:
            best_score = np.inf
            for move in polyboard.legal_moves:
                polyboard.push(move)
                best_score = min(best_score, AI.alphabeta(polyboard, depth - 1, a, b, True))
                polyboard.pop()
                b = min(b, best_score)
                if b <= a:
                    break
            return best_score

    @staticmethod
    def quiesce(polyboard, depth, a, b):
        stand_pat = Calculations.stock_score(polyboard, depth)
        if stand_pat >= b:
            return b
        if a < stand_pat:
            a = stand_pat

        for move in polyboard.legal_moves:
            if polyboard.is_capture(move):
                polyboard.push(move)
                score = -AI.quiesce(polyboard, depth, -b, -a)
                polyboard.pop()

                if score >= b:
                    return b
                if score > a:
                    a = score
        return a

    @staticmethod
    def openings():
        books = ['bookfish.bin', 'Perfect2019.bin']
        selection = random.randint(2)
        with chess.polyglot.open_reader(root + "/books/" + books[selection]) as reader:
            for entry in reader.find_all(polyboard):
                return entry.move

    @staticmethod
    def convert_book_to_engine(book_move):
        ranks_to_rows = {"1": 7, "2": 6, "3": 5, "4": 4,
                         "5": 3, "6": 2, "7": 1, "8": 0}
        files_to_cols = {"a": 0, "b": 1, "c": 2, "d": 3,
                         "e": 4, "f": 5, "g": 6, "h": 7}

        best_move = ""
        engine_move, ai_clicks = "N", "N"
        ranks = ["1", "2", "3", "4", "5", "6", "7", "8"]
        files = ["a", "b", "c", "d", "e", "f", "g", "h"]

        try:
            for letter in str(book_move):
                if letter in ranks:
                    best_move += str(abs(ranks_to_rows[str(letter)]))
                elif letter in files:
                    best_move += str(abs(files_to_cols[str(letter)]))
        except:
            best_move = "N"

        if best_move != "N":
            ai_clicks = [(int(best_move[1]), int(best_move[0])), (int(best_move[3]), int(best_move[2]))]
            engine_move = ChessEngine.Move(ai_clicks[0], ai_clicks[1], gs.board)

        return engine_move, ai_clicks

    @staticmethod
    def make_polymove(book_move):
        if chess.Move.from_uci(str(book_move)) in polyboard.legal_moves:
            polyboard.push(chess.Move.from_uci(str(book_move)))


def print_boards():
    print(gs.board)
    print(polyboard)

