import chess
import chess.engine
import random
import numpy as np
from tensorflow import keras
import tensorflow.keras.models as models
import tensorflow.keras.layers as layers
import tensorflow.keras.optimizers as optimizers
import tensorflow.keras.callbacks as callbacks
from numpy import savez_compressed, asarray


root = 'C:/Users/micha/Documents/PycharmProjects/Chess/Chess'


def random_board(max_depth=200):
    board = chess.Board()
    depth = random.randrange(0, max_depth)

    for _ in range(depth):
        all_moves = list(board.legal_moves)
        random_move = random.choice(all_moves)
        board.push(random_move)
        if board.is_game_over():
            break

    return board


def stockfish(board, depth):
    with chess.engine.SimpleEngine.popen_uci(root + '/books/stockfish.exe') as sf:
        result = sf.analyse(board, chess.engine.Limit(depth=depth))
        score = result['score'].white().score()
        return score


board = random_board()

'''
Converting the board
'''
squares_index = {
  'a': 0,
  'b': 1,
  'c': 2,
  'd': 3,
  'e': 4,
  'f': 5,
  'g': 6,
  'h': 7
}


# example: h3 -> 17
def square_to_index(square):
    letter = chess.square_name(square)
    return 8 - int(letter[1]), squares_index[letter[0]]


def split_dims(board):
    # this is the 3d matrix
    board3d = np.zeros((14, 8, 8), dtype=np.int8)

    # here we add the pieces's view on the matrix
    for piece in chess.PIECE_TYPES:
        for square in board.pieces(piece, chess.WHITE):
            idx = np.unravel_index(square, (8, 8))
            board3d[piece - 1][7 - idx[0]][idx[1]] = 1
        for square in board.pieces(piece, chess.BLACK):
            idx = np.unravel_index(square, (8, 8))
            board3d[piece + 5][7 - idx[0]][idx[1]] = 1

    # add attacks and valid moves too
    # so the network knows what is being attacked
    aux = board.turn
    board.turn = chess.WHITE
    for move in board.legal_moves:
        i, j = square_to_index(move.to_square)
        board3d[12][i][j] = 1
    board.turn = chess.BLACK
    for move in board.legal_moves:
        i, j = square_to_index(move.to_square)
        board3d[13][i][j] = 1
    board.turn = aux

    return board3d


# print(split_dims(board))

'''
TF MODEL
'''


def build_model(conv_size, conv_depth):
    board3d = layers.Input(shape=(14, 8, 8))

    # adding the convolutional layers
    x = board3d
    for _ in range(conv_depth):
        x = layers.Conv2D(filters=conv_size, kernel_size=3, padding='same', activation='relu', data_format='channels_first')(x)
    x = layers.Flatten()(x)
    x = layers.Dense(64, 'relu')(x)
    x = layers.Dense(1, 'sigmoid')(x)

    return models.Model(inputs=board3d, outputs=x)


def build_model_residual(conv_size, conv_depth):
    board3d = layers.Input(shape=(14, 8, 8))

    # adding the convolutional layers
    x = layers.Conv2D(filters=conv_size, kernel_size=3, padding='same', data_format='channels_first')(board3d)
    for _ in range(conv_depth):
        previous = x
        x = layers.Conv2D(filters=conv_size, kernel_size=3, padding='same', data_format='channels_first')(x)
        x = layers.BatchNormalization()(x)
        x = layers.Activation('relu')(x)
        x = layers.Conv2D(filters=conv_size, kernel_size=3, padding='same', data_format='channels_first')(x)
        x = layers.BatchNormalization()(x)
        x = layers.Add()([x, previous])
        x = layers.Activation('relu')(x)
    x = layers.Flatten()(x)
    x = layers.Dense(1, 'sigmoid')(x)

    return models.Model(inputs=board3d, outputs=x)


model = build_model_residual(32, 4)
'''
Training
'''


def build_dataset():
    print("Building Dataset")
    num_boards = 1000
    num_boards += -1
    depth = 1

    # Initialise the np data arrays
    board = random_board()
    score = stockfish(board, depth)
    board = split_dims(board)

    board = np.array(board)
    score = np.array(score)

    ml_input = np.array([board])
    ml_output = np.array([score])

    for i in range(num_boards):
        if i == int(num_boards/10):
            print("10% Done")
        elif i == int(num_boards/5):
            print("20% Done")
        elif i == int(4*num_boards/5):
            print("80% Done")
        elif i == int(9*num_boards/10):
            print("90% Done")
        board = random_board()
        score = stockfish(board, depth)

        while score is None:
            board = random_board()
            score = stockfish(board, depth)

        board = split_dims(board)

        ml_input = np.append(ml_input, np.array([board]), axis=0)
        ml_output = np.append(ml_output, np.array([score]), axis=0)

    print("BUILT DATASET")
    print(ml_input.shape)  #(num_boards, 14, 8, 8)
    print(ml_output.shape)  #(num_boards
    np.savez(root + '\\datasets\\my-dataset-{num}-{depth}.npz'.format(num=num_boards+1, depth=depth), b=ml_input, v=ml_output)


# build_dataset()


def get_dataset():
    np_load_old = np.load
    np.load = lambda *a, **k: np_load_old(*a, allow_pickle=True, **k)

    container = np.load(root + '\\datasets\\ml-dataset.npz')
    np.load = np_load_old

    b, v = container['b'], container['v']
    v = np.asarray(v / abs(v).max() / 2 + 0.5, dtype=np.float32) # normalization (0 - 1)
    # print("container")
    # print(b.shape)
    # print(v.shape)
    return b, v

get_dataset()


def train():
    x_train, y_train = get_dataset()
    print(x_train.shape)
    print(y_train.shape)

    model.compile(optimizer=optimizers.Adam(5e-5), loss='mean_squared_error')
    model.summary()
    model.fit(x_train, y_train,
              batch_size=2048,
              epochs=1000,
              verbose=1,
              validation_split=0.1,
              callbacks=[callbacks.ReduceLROnPlateau(monitor='loss', patience=10),
                         callbacks.EarlyStopping(monitor='loss', patience=15, min_delta=1e-4)])

    model.save(root + '/models/model.h5')


def load_model():
    model = keras.models.load_model(root + '/models/model.h5')
    return model


#train()
model = load_model()


'''
Using minimax alg
'''


# used for the minimax algorithm
def minimax_eval(board):
    board3d = split_dims(board)
    board3d = np.expand_dims(board3d, 0)
    return model.predict(board3d)[0][0]


def alphabeta(board, depth, alpha, beta, maximizing):
    if depth == 0 or board.is_game_over():
        return minimax_eval(board)

    if maximizing:
        best_score = -np.inf
        for move in board.legal_moves:
            board.push(move)
            best_score = max(best_score, alphabeta(board, depth - 1, alpha, beta, False))
            board.pop()
            alpha = max(alpha, best_score)
            if beta <= alpha:
                break
        return best_score
    elif not maximizing:
        best_score = np.inf
        for move in board.legal_moves:
            board.push(move)
            best_score = min(best_score, alphabeta(board, depth - 1, alpha, beta, True))
            board.pop()
            beta = min(beta, best_score)
            if beta <= alpha:
                break
        return best_score


# this is the actual function that gets the move from the neural network
def get_ai_move(board, depth):
    max_move = None
    max_eval = -np.inf

    for move in board.legal_moves:
        board.push(move)
        eval = alphabeta(board, depth - 1, -np.inf, np.inf, True)
        board.pop()
        if eval > max_eval:
            max_eval = eval
            max_move = move

    return max_move


board = chess.Board()


def against_stockfish():
    with chess.engine.SimpleEngine.popen_uci(root + '/books/stockfish') as engine:
        while True:
            move = get_ai_move(board, 2)
            board.push(move)
            print("STOCKFISH")
            print(board)
            print("ML \n")
            if board.is_game_over():
                break
            move = engine.analyse(board, chess.engine.Limit(time=1), info=chess.engine.INFO_PV)['pv'][0]
            board.push(move)
            print("STOCKFISH")
            print(board)
            print("ML \n")
            if board.is_game_over():
                break


def against_player(polyboard, depth):
    move = get_ai_move(polyboard, depth)
    return move


#against_stockfish()