import pygame as p
import ChessEngine
import ChessAI
import chess.polyglot
import time
import threading
from threading import Thread
import os

'''
Variables and Logic
'''
# Menu Screen Logic
menu_screen = True
style_screen = False
game_screen = False

# Gamemode Logic
vs_ai = False
vs_player = False
vs_ml = False

# Toggle Logic
drag_move = True
highlight_moves = False
sound = False

# Variables
root = os.path.join(os.getcwd(), 'Chess')
WIDTH = HEIGHT = 812   # can use 400 and 512 as dimensions instead too
DIMENSION = 8     # Dimensions of a board are 8x8
SQ_SIZE = HEIGHT // DIMENSION
MAX_FPS = 60
IMAGES = {}   # Only call to load images once as it's expensive to do
ICON = {}
mouse_pos = ()
pieces = ['wP', 'wR', 'wN', 'wB', 'wQ', 'wK', 'bP', 'bR', 'bN', 'bB', 'bQ', 'bK']

# Board and Colours
style1 = True
style2 = False
cream = '#F0D9B5'
brown = '#B58863'
yellow = '#DAC432'
white = (255, 255, 255, 255)
black = (0, 0, 0, 255)
style1_colors = [cream, brown, yellow, 'blue']
style2_colors = ['white', 'grey', 'blue', yellow]

chosen_style = style1
chosen_colors = style1_colors

background_color = white
'''
Initialise our png piece images
'''


def load_image(chosen_images='high_res_style_1'):
    chosen_images = str(chosen_images + '\\')

    icons = ['toggle_on', 'toggle_off', 'toggle_trans_on', 'toggle_trans_off', 'black_circle', 'transparent', 'white_border']
    for piece in pieces:
        resize = (SQ_SIZE, SQ_SIZE)
        IMAGES[piece] = p.transform.scale(p.image.load(os.path.join(root, "images\\pieces\\") + chosen_images + piece + ".png"), resize)
    for icon in icons:
        resize = (SQ_SIZE, SQ_SIZE)
        if icon == 'black_circle' or icon == 'transparent':
            resize = (int(SQ_SIZE / 4), int(SQ_SIZE / 4))
        ICON[icon] = p.transform.scale(p.image.load(os.path.join(root, "images\\icons\\") + icon + ".png"), resize)
'''

Main code driver which also handles input and output

'''


def menu():
    global style1, style2, chosen_style, chosen_colors, drag_move, highlight_moves, vs_ai, vs_ml
    p.init()
    screen = p.display.set_mode((WIDTH, HEIGHT))
    clock = p.time.Clock()
    screen.fill(p.Color("white"))

    running = True
    menu_close = False

    draw_menu(screen)

    while running:
        for e in p.event.get():
            if e.type == p.QUIT:
                running = False

            # Mouse Presses
            elif e.type == p.MOUSEBUTTONUP:
                if not menu_close:
                    location = p.mouse.get_pos()  # is the x y location of the mouse
                    col = location[0]//SQ_SIZE
                    row = location[1]//SQ_SIZE
                    sq_selected = (row, col)

                    # Checking what game mode is pressed
                    if sq_selected == (2, 1) or sq_selected == (2, 2):
                        sq_selected = ()
                        vs_ai = False
                        vs_ml = False
                        ChessAI.Calculations.vs_ai = False
                        ChessAI.Calculations.vs_ml = False
                        game()
                    if sq_selected == (2, 3) or sq_selected == (2, 4):
                        sq_selected = ()
                        vs_ai = True
                        vs_ml = False
                        ChessAI.Calculations.vs_ai = True
                        ChessAI.Calculations.vs_ml = False
                        game()
                    if sq_selected == (2, 5) or sq_selected == (2, 6):
                        sq_selected = ()
                        vs_ml = True
                        vs_ai = False
                        ChessAI.Calculations.vs_ml = True
                        ChessAI.Calculations.vs_ai = False
                        game()

                    # Checking which style is selected
                    style1_locations = [(4, 1), (4, 2), (4, 3), (5, 1), (5, 3), (5, 3)]
                    style2_locations = [(4, 4), (4, 5), (4, 6), (5, 4), (5, 5), (5, 6)]
                    for location in style1_locations:
                        if sq_selected == location:
                            sq_selected = ()
                            style1 = True
                            style2 = False
                            chosen_style = style1
                            chosen_colors = style1_colors
                            draw_text(screen, text='', text_location='')
                    for location in style2_locations:
                        if sq_selected == location:
                            sq_selected = ()
                            style2 = True
                            style1 = False
                            chosen_style = style2
                            chosen_colors = style2_colors
                            draw_text(screen, text='', text_location='')

                    # Toggle Switches
                    if sq_selected == (7, 2) or sq_selected == (7, 3):
                        sq_selected = ()
                        drag_move = not drag_move
                        draw_text(screen, text='', text_location='')
                    if sq_selected == (7, 4) or sq_selected == (7, 5):
                        sq_selected = ()
                        highlight_moves = not highlight_moves
                        draw_text(screen, text='', text_location='')

        clock.tick(MAX_FPS)
        p.display.flip()


def game():
    global drag_move, vs_ai, vs_ml
    p.init()
    screen = p.display.set_mode((WIDTH, HEIGHT))
    clock = p.time.Clock()
    screen.fill(p.Color("white"))
    gs = ChessEngine.GameState()
    valid_moves = gs.getValidMoves()
    move_made = False  # flag variable for when a move is made
    undo_made = False

    playing = True
    sq_selected = ()   # initially no square is selected, keeps track of last selected click (6, 4)
    player_clicks = []  # keeps track of the players clicks [(6, 4) , (4, 4)]
    game_over = False

    drag = False
    selected = None
    piece_selected_rect = []
    for piece in pieces:
        piece_selected_rect.append(IMAGES[piece].get_rect())

    draw_gamestate(screen, gs, valid_moves, sq_selected, player_clicks, move_made, undo_made, drag, mouse_pos)  # initial draw of gamestate as it only updates on player clicks

    while playing:
        for e in p.event.get():
            if e.type == p.QUIT:
                playing = False

            # Mouse Presses
            # elif drag_move:
            if e.type == p.MOUSEBUTTONDOWN:
                if e.button == 1:
                    col, row = e.pos[0] // SQ_SIZE, e.pos[1] // SQ_SIZE
                    sq_selected = (row, col)
                    piece_selected = gs.board[row][col]
                    if gs.whiteToMove and piece_selected[0] == 'w' or not gs.whiteToMove and piece_selected[0] == 'b':
                        if piece_selected != '--':
                            piece_rect = IMAGES[piece_selected].get_rect()
                            gs.board[row][col] = "--"   # removes piece from current pos
                            draw_gamestate(screen, gs, valid_moves, sq_selected, player_clicks, move_made, undo_made, drag, mouse_pos)
                            drag = True                         # time to drag
                            offset_x = piece_rect.x - e.pos[0]    # offset between mouse and center of item
                            offset_y = piece_rect.y - e.pos[1]
                            piece_rect.x = col * SQ_SIZE + e.pos[0] + offset_x
                            piece_rect.y = row * SQ_SIZE + e.pos[1] + offset_y
                            screen.blit(IMAGES[piece_selected], piece_rect)

            elif e.type == p.MOUSEBUTTONUP:
                if e.button == 1:
                    drag = False
                    sq_released = (int(e.pos[1]/SQ_SIZE), int(e.pos[0]/SQ_SIZE))
                    if sq_released == sq_selected:
                        gs.board[sq_selected[0]][sq_selected[1]] = piece_selected
                        sq_selected = ()
                        player_clicks = []
                        draw_gamestate(screen, gs, valid_moves, sq_selected, player_clicks, move_made, undo_made, drag, mouse_pos)
                    else:
                        player_clicks = [sq_selected, sq_released]
                        draw_gamestate(screen, gs, valid_moves, sq_selected, player_clicks, move_made, undo_made, drag, mouse_pos)
                    if len(player_clicks) == 2:
                        move = ChessEngine.Move(player_clicks[0], player_clicks[1], gs.board)
                        poly_move = str(chess.Move.from_uci(ChessEngine.Move.getChessNotation(move)))
                        for i in range(len(valid_moves)):
                            if move == valid_moves[i]:
                                gs.board[player_clicks[0][0]][player_clicks[0][1]] = piece_selected
                                gs.makeMove(valid_moves[i])
                                ChessAI.polyboard.push(chess.Move.from_uci(poly_move))
                                move_made = True
                                ChessAI.Calculations.best_move = 0
                                ChessAI.Calculations.opening_move = 0
                                draw_gamestate(screen, gs, valid_moves, sq_selected, player_clicks, move_made,
                                               undo_made, drag, mouse_pos)

                        if not move_made:
                            gs.board[sq_selected[0]][sq_selected[1]] = piece_selected
                            sq_selected = ()
                            player_clicks = []
                            draw_gamestate(screen, gs, valid_moves, sq_selected, player_clicks, move_made,
                                           undo_made, drag, mouse_pos)

            elif e.type == p.MOUSEMOTION:
                if drag:                                    # if item is clicked on
                    piece_rect.x = col * SQ_SIZE + e.pos[0] + offset_x     # update the pos of the item to mouse pos
                    piece_rect.y = row * SQ_SIZE + e.pos[1] + offset_y
                    draw_gamestate(screen, gs, valid_moves, sq_selected, player_clicks, move_made, undo_made, drag, mouse_pos=(e.pos[0], e.pos[1]))
                    screen.blit(IMAGES[piece_selected], piece_rect)

            elif e.type == p.KEYDOWN:
                if e.key == p.K_ESCAPE:
                    main()

        if move_made:
            if not vs_ml and not vs_ai:
                valid_moves = gs.getValidMoves()
                sq_selected = ()
                draw_gamestate(screen, gs, valid_moves, sq_selected, player_clicks, undo_made, move_made, drag, mouse_pos)
                draw_gamestate(screen, gs, valid_moves, sq_selected, player_clicks, move_made, undo_made, drag, mouse_pos)
                player_clicks = []
                move_made = False

            if vs_ml or vs_ai:
                move_made = False

                if vs_ml:
                    ml_thread = threading.Thread(target=ChessAI.AI.get_ai_move)
                    ml_thread.daemon = True
                    ml_thread.start()
                    while ml_thread.is_alive:
                        if ChessAI.Calculations.best_move != 0:
                            ml_thread.is_alive = False
                        else:
                            p.display.update()
                        time.sleep(1)
                    best_move, poly_move = ChessAI.Calculations.best_move, ChessAI.Calculations.opening_move

                elif vs_ai:
                    ai_thread = threading.Thread(target=ChessAI.AI.get_ai_move)
                    ai_thread.daemon = True
                    ai_thread.start()
                    while ai_thread.is_alive:
                        if ChessAI.Calculations.best_move != 0:
                            ai_thread.is_alive = False
                        else:
                            p.display.update()
                        time.sleep(1)
                    best_move, poly_move = ChessAI.Calculations.best_move, ChessAI.Calculations.opening_move

                if best_move == poly_move == "N":
                    if gs.inCheck():
                        gs.checkmate = True
                        break
                    else:
                        gs.stalemate = True
                        break

                gs.makeMove(best_move)
                ChessAI.polyboard.push(poly_move)
                valid_moves = gs.getValidMoves()
                draw_gamestate(screen, gs, valid_moves, sq_selected, player_clicks, move_made, undo_made, drag,
                               mouse_pos)
                draw_gamestate(screen, gs, valid_moves, sq_selected, player_clicks, move_made, undo_made, drag,
                               mouse_pos)

        if gs.checkmate:
            game_over = True
            if gs.whiteToMove:
                draw_text(screen, text_location='center', text='Black wins by Checkmate')
            else:
                draw_text(screen, text_location='center', text='White wins by Checkmate')
        elif gs.stalemate:
            game_over = True
            draw_text(screen, text_location='center', text='Stalemate')

        clock.tick(MAX_FPS)
        p.display.flip()


'''
Highlights the selected square and available moves
'''


def highlight_square(screen, gs, valid_moves, sq_selected):
    if sq_selected != ():
        r, c = sq_selected
        if gs.board[r][c][0] == ("w" if gs.whiteToMove else "b"):
            s = p.Surface((SQ_SIZE, SQ_SIZE))
            s.set_alpha(100)    # Transparency Value ( 0 is transparent and 255 is opaque)

            s.fill(p.Color(chosen_colors[3]))
            for move in valid_moves:
                if move.startRow == r and move.startCol == c:
                    screen.blit(s, (move.endCol*SQ_SIZE, move.endRow*SQ_SIZE))
            draw_pieces(screen, gs.board)


def highlight_pieces(screen, gs, sq_selected, player_clicks, move_made):
    if sq_selected != ():
        r, c = sq_selected
        s = p.Surface((SQ_SIZE, SQ_SIZE))
        s.set_alpha(255)    # Transparency Value ( 0 is transparent and 255 is opaque)
        s.fill(p.Color(chosen_colors[2]))
        screen.blit(s, (c*SQ_SIZE, r*SQ_SIZE,))

    if move_made:
        r1, c1 = player_clicks[0]
        r2, c2 = player_clicks[1]
        s = p.Surface((SQ_SIZE, SQ_SIZE))
        s.set_alpha(255)    # Transparency Value ( 0 is transparent and 255 is opaque)
        s.fill(p.Color(chosen_colors[2]))
        screen.blit(s, (c1 * SQ_SIZE, r1 * SQ_SIZE))
        screen.blit(s, (c2 * SQ_SIZE, r2 * SQ_SIZE))


def hover_square(screen, gs, mouse_pos):
    c, r = mouse_pos[0] // SQ_SIZE, mouse_pos[1] // SQ_SIZE
    s = p.Surface((SQ_SIZE, SQ_SIZE))
    s.set_alpha(255)
    s.fill(p.Color('white'))
    colors = [p.Color(chosen_colors[0]), p.Color(chosen_colors[1])]
    color = colors[((r + c) % 2)]
    screen.blit(s, (c * SQ_SIZE, r * SQ_SIZE))
    p.draw.rect(screen, color, p.Rect(c * SQ_SIZE + 5, r * SQ_SIZE + 5, SQ_SIZE - 10, SQ_SIZE + - 10))

'''
Draws the graphics of the board and pieces and draws and updates the current gamestate
'''


def draw_gamestate(screen, gs, valid_moves, sq_selected, player_clicks, move_made, undo_made, drag, mouse_pos):
    draw_board(screen)    # draws the squares first
    highlight_pieces(screen, gs, sq_selected, player_clicks, move_made)    # Highlights piece to move and moved to
    if drag:
        hover_square(screen, gs, mouse_pos)
    draw_pieces(screen, gs.board)    # draws the pieces on top of the board

    if highlight_moves:
        highlight_square(screen, gs, valid_moves, sq_selected)   # Highlights Valid Moves


def draw_board(screen):
    colors = [p.Color(chosen_colors[0]), p.Color(chosen_colors[1])]
    for r in range(DIMENSION):
        for c in range(DIMENSION):
            color = colors[((r+c) % 2)]
            p.draw.rect(screen, color, p.Rect(c*SQ_SIZE, r*SQ_SIZE, SQ_SIZE, SQ_SIZE))


def draw_pieces(screen, board):
    for r in range(DIMENSION):
        for c in range(DIMENSION):
            piece = board[r][c]
            if piece != "--":
                screen.blit(IMAGES[piece], p.Rect(c*SQ_SIZE, r*SQ_SIZE, SQ_SIZE, SQ_SIZE))


def draw_text(screen, text, text_location, color='black'):
    montserrat_font_dir = root + '/fonts/Montserrat/Montserrat-SemiBold.ttf'
    font = p.font.Font(montserrat_font_dir, 32)
    text_object = font.render(text, True, p.Color(color))

    adjust_for_text_width = text_object.get_width()/2
    adjust_for_text_height = text_object.get_height() / 2

    if text_location != '':
        # Reference Positions
        if text_location == 'center':
            text_location = p.Rect(0, 0, WIDTH, HEIGHT).move(WIDTH/2 - adjust_for_text_width,
                                                             HEIGHT/2 - adjust_for_text_height)
        elif text_location == 'top':
            text_location = p.Rect(0, 0, WIDTH, HEIGHT).move(WIDTH/2 - adjust_for_text_width,
                                                             2 * adjust_for_text_height)
        elif text_location == 'bottom':
            text_location = p.Rect(0, 0, WIDTH, HEIGHT).move(WIDTH/2 - adjust_for_text_width,
                                                             HEIGHT - 3 * adjust_for_text_height)
        elif text_location == 'left':
            text_location = p.Rect(0, 0, WIDTH, HEIGHT).move(adjust_for_text_width,
                                                             HEIGHT/2 - adjust_for_text_height)
        elif text_location == 'right':
            text_location = p.Rect(0, 0, WIDTH, HEIGHT).move(WIDTH - 4 * adjust_for_text_width,
                                                             HEIGHT/2 - adjust_for_text_height)
        # Custom Positions
        elif text_location == 'play_vs':
            text_location = p.Rect(0, 0, WIDTH, HEIGHT).move(WIDTH / 2 - adjust_for_text_width,
                                                             HEIGHT / 5 - adjust_for_text_height)
        elif text_location == 'p2':
            text_location = p.Rect(0, 0, WIDTH, HEIGHT).move(2 * WIDTH / 8 - adjust_for_text_width,
                                                             HEIGHT / 4 + adjust_for_text_height)
        elif text_location == 'ai':
            text_location = p.Rect(0, 0, WIDTH, HEIGHT).move(4 * WIDTH / 8 - adjust_for_text_width,
                                                             HEIGHT / 4 + adjust_for_text_height)
        elif text_location == 'ml':
            text_location = p.Rect(0, 0, WIDTH, HEIGHT).move(6 * WIDTH / 8 - adjust_for_text_width,
                                                             HEIGHT / 4 + adjust_for_text_height)

        elif text_location == 'board':
            text_location = p.Rect(0, 0, WIDTH, HEIGHT).move(WIDTH / 2 - adjust_for_text_width,
                                                             HEIGHT/2 - adjust_for_text_height)
        elif text_location == 'style1':
            text_location = p.Rect(0, 0, WIDTH, HEIGHT).move(2 * WIDTH / 8,
                                                             HEIGHT/2 + 3 * adjust_for_text_height)
        elif text_location == 'style2':
            text_location = p.Rect(0, 0, WIDTH, HEIGHT).move(6 * WIDTH / 8 - 2 * adjust_for_text_width,
                                                             HEIGHT/2 + 3 * adjust_for_text_height)

        elif text_location == 'settings':
            text_location = p.Rect(0, 0, WIDTH, HEIGHT).move(WIDTH / 2 - adjust_for_text_width,
                                                             3 * HEIGHT / 4 - adjust_for_text_height)
        elif text_location == 'drag':
            text_location = p.Rect(0, 0, WIDTH, HEIGHT).move(3 * WIDTH / 9,
                                                             3 * HEIGHT / 4 + 2 * adjust_for_text_height)
            screen.blit(ICON['toggle_trans_on'],
                        p.Rect(0, 0, WIDTH, HEIGHT).move(3 * WIDTH / 9,
                                                         3 * HEIGHT / 4 + 4 * adjust_for_text_height))
        elif text_location == 'highlight':
            text_location = p.Rect(0, 0, WIDTH, HEIGHT).move(5 * WIDTH / 9 - adjust_for_text_width / 3,
                                                             3 * HEIGHT / 4 + 2 * adjust_for_text_height)
            screen.blit(ICON['toggle_trans_off'],
                        p.Rect(0, 0, WIDTH, HEIGHT).move(5 * WIDTH / 9,
                                                         3 * HEIGHT / 4 + 4 * adjust_for_text_height))

        screen.blit(text_object, text_location)

    elif text_location == '':
        if style1:
            screen.blit(ICON['black_circle'], (WIDTH/5, 7 * HEIGHT / 12))
            s = p.Surface((int(SQ_SIZE / 4), int(SQ_SIZE / 4)), p.SRCALPHA)  # per-pixel alpha
            s.fill(background_color)  # notice the alpha value in the color
            screen.blit(s, (6 * WIDTH / 11, 7 * HEIGHT / 12))
        elif style2:
            screen.blit(ICON['black_circle'], (6 * WIDTH / 11, 7 * HEIGHT / 12))
            s = p.Surface((int(SQ_SIZE / 4), int(SQ_SIZE / 4)), p.SRCALPHA)  # per-pixel alpha
            s.fill(background_color)  # notice the alpha value in the color
            screen.blit(s, (WIDTH/5, 7 * HEIGHT / 12))

        if drag_move:
            screen.blit(ICON['toggle_trans_on'],
                        p.Rect(0, 0, WIDTH, HEIGHT).move(3 * WIDTH / 9,
                                                         3 * HEIGHT / 4 + 4 * adjust_for_text_height))
        elif not drag_move:
            screen.blit(ICON['toggle_trans_off'],
                        p.Rect(0, 0, WIDTH, HEIGHT).move(3 * WIDTH / 9,
                                                         3 * HEIGHT / 4 + 4 * adjust_for_text_height))
        if highlight_moves:
            screen.blit(ICON['toggle_trans_on'],
                        p.Rect(0, 0, WIDTH, HEIGHT).move(5 * WIDTH / 9,
                                                         3 * HEIGHT / 4 + 4 * adjust_for_text_height))
        elif not highlight_moves:
            screen.blit(ICON['toggle_trans_off'],
                        p.Rect(0, 0, WIDTH, HEIGHT).move(5 * WIDTH / 9,
                                                         3 * HEIGHT / 4 + 4 * adjust_for_text_height))


def draw_menu(screen):
    colors = [p.Color(style2_colors[0]), p.Color(style2_colors[1])]
    for r in range(DIMENSION):
        for c in range(DIMENSION):
            color = p.Color('white')
            if r == 0:
                p.draw.rect(screen, p.Color(cream), p.Rect(c * SQ_SIZE, r * SQ_SIZE, SQ_SIZE, SQ_SIZE))
    draw_text(screen, text='Chess', text_location='top', color='black')
    draw_text(screen, text='Play vs:', text_location='play_vs', color='black')

    draw_text(screen, text='P2', text_location='p2', color='black')     # 2 1 and 2 2
    draw_text(screen, text='AI', text_location='ai', color='black')     # 2 3 and 2 4
    draw_text(screen, text='ML', text_location='ml', color='black')     # 2 5 and 2 6

    draw_text(screen, text='Board Styles', text_location='board', color='black')
    draw_text(screen, text='Style 1', text_location='style1', color='black')    # 4 1, 4 2, 4 3, 5 1, 5 2, 5 3
    screen.blit(ICON['black_circle'], (WIDTH / 5, 7 * HEIGHT / 12))     # shows that style1 is selected
    draw_text(screen, text='Style 2', text_location='style2', color='black')    # 4 4, 4 5, 4 6, 5 4, 5 5, 5 6

    draw_text(screen, text='Settings', text_location='settings', color='black')
    draw_text(screen, text='Drag', text_location='drag', color='black')     # 7 2, 7 3
    draw_text(screen, text='Highlight', text_location='highlight', color='black')   # 7 4, 7 5

'''
Logic Switcher
'''


def main():
    load_image()
    menu()
    if game_screen:
        game()


class ThreadWithReturnValue(Thread):
    def __init__(self, group=None, target=None, name=None,
                 args=(), kwargs={}, Verbose=None):
        Thread.__init__(self, group, target, name, args, kwargs)
        self._return = None

    def run(self):
        if self._target is not None:
            self._return = self._target(*self._args,
                                        **self._kwargs)

    def join(self, *args):
        Thread.join(self, *args)
        return self._return


if __name__ == "__main__":
    main()

