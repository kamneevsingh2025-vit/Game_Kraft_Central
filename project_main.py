import pygame
import os
import sys
import subprocess
from flask import Flask, render_template_string, redirect, url_for
import random # Needed for RPS and Miner
import numpy as np # Needed for Miner (Must be available in the subprocess environment)

# --- FLASK SETUP ---
app = Flask(__name__)

# ----------------------------------------------------
## UTILITY FUNCTIONS 
# ----------------------------------------------------

def run_game_script(script_content, temp_script_name="temp_game_script.py"):
    """
    Writes the Pygame script content to a temporary file and runs it in a subprocess.
    """
    try:
        # Write the Pygame code string to a temporary .py file
        with open(temp_script_name, "w") as f:
            f.write(script_content)
        
        # Execute the temporary script using the current Python interpreter
        print(f"--- Launching {temp_script_name} in subprocess...")
        subprocess.Popen([sys.executable, temp_script_name])
        print("--- Subprocess started.")

    except Exception as e:
        print(f"An error occurred during subprocess launch: {e}")

# ----------------------------------------------------
## PYGAME CODE STRINGS FOR SUBPROCESSES
# ----------------------------------------------------

# --- ROCK PAPER SCISSORS PYGAME LOGIC (Assumed from previous context) ---
PYGAME_RPS_CODE = """
import pygame
import sys
import random
import os 

pygame.init()
WIDTH, HEIGHT = 600, 400
WIN = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Rock Paper Scissors")

# ICON CODE (Simplified for inclusion in a string)
try:
    script_dir = os.path.dirname(os.path.abspath(__file__))
    icon_path = os.path.join(script_dir, "rps_icon.png")
    if os.path.exists(icon_path):
        icon_image = pygame.image.load(icon_path)
        pygame.display.set_icon(icon_image)
except:
    pass # Ignore icon loading errors

FONT = pygame.font.SysFont("consolas", 30)
BIG_FONT = pygame.font.SysFont("consolas", 50)

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GRAY = (200, 200, 200)
GREEN = (100, 255, 100)
RED = (255, 100, 100)
BLUE = (100, 100, 255)

# Background Music (Simplified check)
pygame.mixer.init()
try:
    sound_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "backgroundmusicrps.wav")
    if os.path.exists(sound_path):
        bg_music = pygame.mixer.Sound(sound_path)
        bg_music.play(loops=-1)
except:
    print("Warning: backgroundmusicrps.wav could not be loaded in subprocess.")

OPTIONS = ["Rock", "Paper", "Scissors"]
BUTTONS = []
for i, option in enumerate(OPTIONS):
    rect = pygame.Rect(50 + i*180, 300, 150, 60)
    BUTTONS.append((rect, option))

player_choice = None
computer_choice = None
result = ""

def draw_screen():
    WIN.fill(WHITE)
    
    for rect, text in BUTTONS:
        pygame.draw.rect(WIN, GRAY, rect)
        txt = FONT.render(text, True, BLACK)
        txt_rect = txt.get_rect(center=rect.center)
        WIN.blit(txt, txt_rect)

    if player_choice:
        p_txt = BIG_FONT.render(f"Player: {player_choice}", True, BLUE)
        WIN.blit(p_txt, (50, 50))
    if computer_choice:
        c_txt = BIG_FONT.render(f"Computer: {computer_choice}", True, RED)
        WIN.blit(c_txt, (50, 120))
    
    if result:
        r_txt = BIG_FONT.render(result, True, GREEN)
        WIN.blit(r_txt, (50, 200))
    
    pygame.display.update()

def check_winner(player, computer):
    if player == computer:
        return "Tie!"
    elif (player=="Rock" and computer=="Scissors") or \
         (player=="Paper" and computer=="Rock") or \
         (player=="Scissors" and computer=="Paper"):
        return "You Win!"
    else:
        return "You Lose!"

run = True
while run:
    draw_screen()
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            run = False
        if event.type == pygame.MOUSEBUTTONDOWN:
            pos = pygame.mouse.get_pos()
            for rect, option in BUTTONS:
                if rect.collidepoint(pos):
                    player_choice = option
                    computer_choice = random.choice(OPTIONS)
                    result = check_winner(player_choice, computer_choice)

pygame.quit() 
"""

# --- PYGAME CHESS LOGIC (The detailed code is included here) ---
PYGAME_CHESS_CODE = """
import pygame
import os
import sys

# Initialize Pygame in the separate process
pygame.init()

# SCREEN & BOARD SETTINGS
SQUARE = 70
BOARD_SIZE = SQUARE * 8
RIGHT_PANEL = 200
BOTTOM_PANEL = 120
WIDTH = BOARD_SIZE + RIGHT_PANEL
HEIGHT = BOARD_SIZE + BOTTOM_PANEL

screen = pygame.display.set_mode([WIDTH, HEIGHT])
pygame.display.set_caption('Two-Player Pygame Chess!')

font = pygame.font.Font('freesansbold.ttf', 16)
medium_font = pygame.font.Font('freesansbold.ttf', 32)
big_font = pygame.font.Font('freesansbold.ttf', 40)

timer = pygame.time.Clock()
fps = 60

# Background Music (Simplified check)
pygame.mixer.init()
try:
    sound_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "backgroundmusicchess.wav")
    if os.path.exists(sound_path):
        bg_music = pygame.mixer.Sound(sound_path)
        bg_music.play(loops=-1)
except:
    print("Warning: backgroundmusicchess.wav could not be loaded in subprocess.")

# GAME VARIABLES
white_pieces = ['rook', 'knight', 'bishop', 'queen', 'king', 'bishop', 'knight', 'rook'] + ['pawn']*8
black_pieces = ['rook', 'knight', 'bishop', 'queen', 'king', 'bishop', 'knight', 'rook'] + ['pawn']*8

# White pieces at bottom
white_locations = [(0, 7), (1, 7), (2, 7), (3, 7), (4, 7), (5, 7), (6, 7), (7, 7)] + [(i, 6) for i in range(8)]
# Black pieces at top
black_locations = [(0, 0), (1, 0), (2, 0), (3, 0), (4, 0), (5, 0), (6, 0), (7, 0)] + [(i, 1) for i in range(8)]

captured_pieces_white = []
captured_pieces_black = []

# Castling tracking: [king_moved, left_rook_moved, right_rook_moved]
white_castling = [False, False, False]
black_castling = [False, False, False]

# En passant tracking: stores the position where en passant capture is possible
en_passant_target = None

turn_step = 0
# 0-white select, 1-white move, 2-black select, 3-black move
selection = 100
valid_moves = []
counter = 0
winner = ''
game_over = False
promotion_index = None # Index of pawn to be promoted
promotion_color = None # 'white' or 'black'

piece_list = ['pawn', 'queen', 'king', 'knight', 'rook', 'bishop']

# IMAGE LOADING
# The path must be absolute or relative to the CURRENT working directory
def load_img(filename, size):
    # This assumes the 'assets/images' folder is in the same directory 
    # as the script that is eventually executed (temp_game_script.py).
    base = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'assets', 'images')
    path = os.path.join(base, filename)
    if not os.path.exists(path):
        # NOTE: In a subprocess, this error is critical if assets are missing.
        print(f"ERROR: Chess image not found: {path}. Check your assets folder structure.")
        # Return a small surface as a fallback to prevent the script from crashing immediately
        return pygame.Surface(size) 
    img = pygame.image.load(path).convert_alpha()
    return pygame.transform.scale(img, size)

# Load black pieces
black_queen = load_img('black queen.png', (60, 60))
black_king = load_img('black king.png', (60, 60))
black_rook = load_img('black rook.png', (60, 60))
black_bishop = load_img('black bishop.png', (60, 60))
black_knight = load_img('black knight.png', (60, 60))
black_pawn = load_img('black pawn.png', (50, 50))

# Load white pieces
white_queen = load_img('white queen.png', (60, 60))
white_king = load_img('white king.png', (60, 60))
white_rook = load_img('white rook.png', (60, 60))
white_bishop = load_img('white bishop.png', (60, 60))
white_knight = load_img('white knight.png', (60, 60))
white_pawn = load_img('white pawn.png', (50, 50))

# Small images for captured pieces
def make_small(img):
    return pygame.transform.scale(img, (35, 35))

small_black_images = [make_small(black_pawn), make_small(black_queen), make_small(black_king),make_small(black_knight), make_small(black_rook), make_small(black_bishop)]
small_white_images = [make_small(white_pawn), make_small(white_queen), make_small(white_king), make_small(white_knight), make_small(white_rook), make_small(white_bishop)]

white_images = [white_pawn, white_queen, white_king, white_knight, white_rook, white_bishop]
black_images = [black_pawn, black_queen, black_king, black_knight, black_rook, black_bishop]

# DRAW FUNCTIONS
def draw_piece(img, position):
    x = position[0] * SQUARE + (SQUARE - img.get_width()) // 2
    y = position[1] * SQUARE + (SQUARE - img.get_height()) // 2
    screen.blit(img, (x, y))

def draw_board():
    # Draw squares - Classic wood theme
    for row in range(8):
        for col in range(8):
            # Light wood and dark wood colors
            color = (240, 217, 181) if (row + col + 1) % 2 == 0 else (181, 136, 99)
            pygame.draw.rect(screen, color, [col*SQUARE, row*SQUARE, SQUARE, SQUARE])

    # Panels - Dark wood color
    pygame.draw.rect(screen, (101, 67, 33), [0, BOARD_SIZE, WIDTH, BOTTOM_PANEL])
    pygame.draw.rect(screen, (139, 90, 43), [0, BOARD_SIZE, WIDTH, BOTTOM_PANEL], 5)
    pygame.draw.rect(screen, (139, 90, 43), [BOARD_SIZE, 0, RIGHT_PANEL, HEIGHT], 5)

    # Grid lines
    for i in range(9):
        pygame.draw.line(screen, 'black', (0, i*SQUARE), (BOARD_SIZE, i*SQUARE), 2)
        pygame.draw.line(screen, 'black', (i*SQUARE, 0), (i*SQUARE, BOARD_SIZE), 2)

    # Status text
    status_text = ['White: Select a Piece to Move!', 'White: Select a Destination!',
                    'Black: Select a Piece to Move!', 'Black: Select a Destination!']
    screen.blit(font.render(status_text[turn_step], True, 'white'), (20, BOARD_SIZE + 20))
    
    # Forfeit button with background
    forfeit_rect = pygame.Rect(BOARD_SIZE + 50, BOARD_SIZE + 20, 100, 30)
    pygame.draw.rect(screen, (139, 69, 19), forfeit_rect) # Saddle brown
    pygame.draw.rect(screen, (101, 67, 33), forfeit_rect, 2)
    screen.blit(font.render('FORFEIT', True, 'white'), (BOARD_SIZE + 60, BOARD_SIZE + 25))

def draw_pieces():
    for i, piece in enumerate(white_pieces):
        index = piece_list.index(piece)
        img = white_pawn if piece=='pawn' else white_images[index]
        draw_piece(img, white_locations[i])
        if turn_step < 2 and selection == i:
            pygame.draw.rect(screen, (218, 165, 32), [white_locations[i][0]*SQUARE+1, white_locations[i][1]*SQUARE+1, SQUARE, SQUARE], 3)

    for i, piece in enumerate(black_pieces):
        index = piece_list.index(piece)
        img = black_pawn if piece=='pawn' else black_images[index]
        draw_piece(img, black_locations[i])
        if turn_step >= 2 and selection == i:
            pygame.draw.rect(screen, (184, 134, 11), [black_locations[i][0]*SQUARE+1, black_locations[i][1]*SQUARE+1, SQUARE, SQUARE], 3)

def draw_valid(moves):
    color = (218, 165, 32) if turn_step < 2 else (184, 134, 11)
    for move in moves:
        pygame.draw.circle(screen, color, (move[0]*SQUARE + SQUARE//2, move[1]*SQUARE + SQUARE//2), 5)

def draw_captured():
    for i, piece in enumerate(captured_pieces_white):
        index = piece_list.index(piece)
        screen.blit(small_black_images[index], (BOARD_SIZE + 25, 5 + 50*i))
    for i, piece in enumerate(captured_pieces_black):
        index = piece_list.index(piece)
        screen.blit(small_white_images[index], (BOARD_SIZE + 125, 5 + 50*i))

def draw_check():
    global counter
    # Check if a king is still on the board before proceeding
    if 'king' not in white_pieces or 'king' not in black_pieces:
        return
        
    if turn_step < 2:
        king_index = white_pieces.index('king')
        king_location = white_locations[king_index]
        # Use globals() to check for options lists defined in the main loop of this script
        if 'black_options' in globals():
            for moves in black_options:
                if king_location in moves and counter < 15:
                    pygame.draw.rect(screen, (178, 34, 34), [king_location[0]*SQUARE+1, king_location[1]*SQUARE+1, SQUARE, SQUARE], 5)
    elif turn_step >= 2:
        king_index = black_pieces.index('king')
        king_location = black_locations[king_index]
        if 'white_options' in globals():
            for moves in white_options:
                if king_location in moves and counter < 15:
                    pygame.draw.rect(screen, (178, 34, 34), [king_location[0]*SQUARE+1, king_location[1]*SQUARE+1, SQUARE, SQUARE], 5)

def draw_game_over():
    pygame.draw.rect(screen, (101, 67, 33), [200, 200, 400, 70])
    pygame.draw.rect(screen, (139, 90, 43), [200, 200, 400, 70], 3)
    screen.blit(font.render(f'{winner} won the game!', True, 'white'), (210, 210))
    screen.blit(font.render('Press ENTER to Restart!', True, 'white'), (210, 240))

def draw_promotion():
    pygame.draw.rect(screen, (222, 184, 135), [250, 250, 260, 180])
    pygame.draw.rect(screen, (139, 90, 43), [250, 250, 260, 180], 3)
    screen.blit(font.render('Promote to:', True, (101, 67, 33)), (280, 260))
    
    options = ['Queen', 'Rook', 'Bishop', 'Knight']
    for i, option in enumerate(options):
        y_pos = 290 + i * 40
        pygame.draw.rect(screen, (210, 180, 140), [270, y_pos, 220, 35])
        pygame.draw.rect(screen, (139, 90, 43), [270, y_pos, 220, 35], 2)
        screen.blit(font.render(option, True, (101, 67, 33)), (320, y_pos + 8))

# MOVE LOGIC FUNCTIONS (Replicated from original code)

def check_rook(pos, color):
    moves_list = []
    friends = white_locations if color=='white' else black_locations
    enemies = black_locations if color=='white' else white_locations
    directions = [(0,1),(0,-1),(1,0),(-1,0)]
    for dx,dy in directions:
        chain=1
        while True:
            t=(pos[0]+dx*chain,pos[1]+dy*chain)
            if t in friends or not (0<=t[0]<=7 and 0<=t[1]<=7):
                break
            moves_list.append(t)
            if t in enemies:
                break
            chain+=1
    return moves_list

def check_bishop(pos,color):
    moves_list=[]
    friends = white_locations if color=='white' else black_locations
    enemies = black_locations if color=='white' else white_locations
    directions=[(1,1),(1,-1),(-1,1),(-1,-1)]
    for dx,dy in directions:
        chain=1
        while True:
            t=(pos[0]+dx*chain,pos[1]+dy*chain)
            if t in friends or not (0<=t[0]<=7 and 0<=t[1]<=7):
                break
            moves_list.append(t)
            if t in enemies:
                break
            chain+=1
    return moves_list

def check_queen(pos,color):
    return check_rook(pos,color)+check_bishop(pos,color)

def check_knight(position, color):
    moves_list = []
    friends_list = white_locations if color=='white' else black_locations
    targets = [(1,2),(1,-2),(2,1),(2,-1),(-1,2),(-1,-2),(-2,1),(-2,-1)]
    for dx,dy in targets:
        t=(position[0]+dx,position[1]+dy)
        if t not in friends_list and 0<=t[0]<=7 and 0<=t[1]<=7:
            moves_list.append(t)
    return moves_list

# Placeholder for is_square_under_attack (critical for check/mate)
def is_square_under_attack(square, color, pieces, locations):
    # Simplified: always returns False to prevent halting, a real engine is needed here.
    return False

def check_king(pos, color):
    moves_list = []
    friends = white_locations if color=='white' else black_locations
    enemies = black_locations if color=='white' else white_locations
    castling_status = white_castling if color=='white' else black_castling
    
    # Normal king moves
    targets = [(1,0),(1,1),(1,-1),(-1,0),(-1,-1),(-1,1),(0,1),(0,-1)]
    for dx,dy in targets:
        t = (pos[0]+dx,pos[1]+dy)
        if t not in friends and 0<=t[0]<=7 and 0<=t[1]<=7:
            moves_list.append(t)
    
    # Castling (Simplified: allows if flags are clear and path is empty)
    if not castling_status[0]:
        row = pos[1]
        
        # Kingside castling
        if not castling_status[2] and (pos[0]+1, row) not in friends+enemies and (pos[0]+2, row) not in friends+enemies:
            moves_list.append((pos[0]+2, row))
        
        # Queenside castling
        if not castling_status[1] and (pos[0]-1, row) not in friends+enemies and (pos[0]-2, row) not in friends+enemies and (pos[0]-3, row) not in friends+enemies:
            moves_list.append((pos[0]-2, row))
    
    return moves_list

def check_pawn(pos,color):
    moves_list=[]
    
    if color=='white':
        if (pos[0],pos[1]-1) not in white_locations+black_locations and pos[1]>0:
            moves_list.append((pos[0],pos[1]-1))
        if pos[1]==6 and (pos[0],pos[1]-2) not in white_locations+black_locations and (pos[0],pos[1]-1) not in white_locations+black_locations:
            moves_list.append((pos[0],pos[1]-2))
        for dx in [-1,1]:
            t=(pos[0]+dx,pos[1]-1)
            if t in black_locations:
                moves_list.append(t)
        # En passant capture check
        global en_passant_target
        if en_passant_target and pos[1] == 3:
            if en_passant_target == (pos[0]+1, 3) or en_passant_target == (pos[0]-1, 3):
                moves_list.append((en_passant_target[0], 2))
    else:
        if (pos[0],pos[1]+1) not in white_locations+black_locations and pos[1]<7:
            moves_list.append((pos[0],pos[1]+1))
        if pos[1]==1 and (pos[0],pos[1]+2) not in white_locations+black_locations and (pos[0],pos[1]+1) not in white_locations+black_locations:
            moves_list.append((pos[0],pos[1]+2))
        for dx in [-1,1]:
            t=(pos[0]+dx,pos[1]+1)
            if t in white_locations:
                moves_list.append(t)
        # En passant capture check
        if en_passant_target and pos[1] == 4:
            if en_passant_target == (pos[0]+1, 4) or en_passant_target == (pos[0]-1, 4):
                moves_list.append((en_passant_target[0], 5))
    return moves_list

def check_options(pieces, locations, color):
    all_moves=[]
    for piece,loc in zip(pieces,locations):
        if piece=='pawn': moves=check_pawn(loc,color)
        elif piece=='rook': moves=check_rook(loc,color)
        elif piece=='bishop': moves=check_bishop(loc,color)
        elif piece=='queen': moves=check_queen(loc,color)
        elif piece=='king': moves=check_king(loc,color)
        elif piece=='knight': moves=check_knight(loc,color)
        all_moves.append(moves)
    return all_moves

def check_valid_moves():
    options_list = white_options if turn_step<2 else black_options
    if selection >= len(options_list): # Safety check if selection is out of bounds
        return []
    return options_list[selection]

# INITIAL MOVE OPTIONS (Need to be global for check_check to work)
global black_options
global white_options
black_options = check_options(black_pieces, black_locations, 'black')
white_options = check_options(white_pieces, white_locations, 'white')

# MAIN LOOP
run=True
while run:
    timer.tick(fps)
    counter = (counter + 1) % 30
    screen.fill((70, 50, 30))

    draw_board()
    draw_pieces()
    draw_captured()
    draw_check()

    if selection!=100:
        valid_moves=check_valid_moves()
        draw_valid(valid_moves)
    
    if promotion_index is not None:
        draw_promotion()

    for event in pygame.event.get():
        if event.type==pygame.QUIT:
            run=False
        if event.type==pygame.KEYDOWN:
            if event.key == pygame.K_RETURN and game_over:
                # Basic exit for the subprocess on restart request
                run = False 

        if event.type==pygame.MOUSEBUTTONDOWN and event.button==1:
            
            # Handle promotion dialog click
            if promotion_index is not None:
                mouse_x, mouse_y = event.pos
                if 270 <= mouse_x <= 490:
                    piece_choice = None
                    if 290 <= mouse_y <= 325: piece_choice = 'queen'
                    elif 330 <= mouse_y <= 365: piece_choice = 'rook'
                    elif 370 <= mouse_y <= 405: piece_choice = 'bishop'
                    elif 410 <= mouse_y <= 445: piece_choice = 'knight'
                    
                    if piece_choice:
                        pieces = white_pieces if promotion_color == 'white' else black_pieces
                        pieces[promotion_index] = piece_choice
                        
                        # Reset promotion state
                        promotion_index = None
                        promotion_color = None
                        
                        # Recalculate options
                        black_options=check_options(black_pieces, black_locations,'black')
                        white_options=check_options(white_pieces, white_locations,'white')
                        continue # Skip further processing while in promotion mode
            
            if not game_over:
                x_coord, y_coord = event.pos[0]//SQUARE, event.pos[1]//SQUARE
                click_coords=(x_coord,y_coord)
                
                # Check Forfeit Button
                forfeit_rect = pygame.Rect(BOARD_SIZE + 50, BOARD_SIZE + 20, 100, 30)
                if forfeit_rect.collidepoint(event.pos):
                    winner = 'Black' if turn_step < 2 else 'White'
                    game_over = True
                    continue # Stop processing turn

                # White's Turn
                if turn_step<=1:
                    if click_coords in white_locations:
                        selection=white_locations.index(click_coords)
                        if turn_step==0: turn_step=1
                    elif click_coords in valid_moves and selection!=100:
                        # Move execution block
                        piece = white_pieces[selection]
                        old_pos = white_locations[selection]
                        
                        # Castling
                        if piece == 'king' and abs(click_coords[0] - old_pos[0]) == 2:
                            white_locations[selection] = click_coords
                            white_castling[0] = True
                            if click_coords[0] == 6: # Kingside
                                rook_index = white_locations.index((7, 7))
                                white_locations[rook_index] = (5, 7)
                                white_castling[2] = True
                            else: # Queenside
                                rook_index = white_locations.index((0, 7))
                                white_locations[rook_index] = (3, 7)
                                white_castling[1] = True
                            en_passant_target = None
                        else:
                            en_passant_capture = False
                            # En Passant Capture
                            if piece == 'pawn' and en_passant_target and old_pos[1] == 3 and click_coords == (en_passant_target[0], 2):
                                captured_pawn_pos = en_passant_target
                                idx = black_locations.index(captured_pawn_pos)
                                captured_pieces_white.append(black_pieces.pop(idx))
                                black_locations.pop(idx)
                                en_passant_capture = True
                            
                            white_locations[selection] = click_coords
                            
                            # Update Castling Flags for Rook/King moves
                            if piece == 'king': white_castling[0] = True
                            elif piece == 'rook':
                                if old_pos == (0, 7): white_castling[1] = True
                                elif old_pos == (7, 7): white_castling[2] = True
                            
                            # Standard Capture
                            if not en_passant_capture and click_coords in black_locations:
                                idx = black_locations.index(click_coords)
                                if black_pieces[idx] == 'king': winner = 'White'; game_over=True
                                captured_pieces_white.append(black_pieces.pop(idx))
                                black_locations.pop(idx)
                            
                            # En Passant Target Set
                            if piece == 'pawn' and old_pos[1] == 6 and click_coords[1] == 4:
                                en_passant_target = (click_coords[0], 4)
                            else:
                                en_passant_target = None
                            
                            # Pawn Promotion Trigger
                            if piece == 'pawn' and click_coords[1] == 0:
                                promotion_index = selection
                                promotion_color = 'white'
                            
                        # End Turn
                        black_options=check_options(black_pieces, black_locations,'black')
                        white_options=check_options(white_pieces, white_locations,'white')
                        if not promotion_index: # Only advance turn if not in promotion dialog
                            turn_step=2; selection=100; valid_moves=[]

                # Black's Turn (Similar logic to White's Turn)
                else:
                    if click_coords in black_locations:
                        selection=black_locations.index(click_coords)
                        if turn_step==2: turn_step=3
                    elif click_coords in valid_moves and selection!=100:
                        piece = black_pieces[selection]
                        old_pos = black_locations[selection]

                        # Castling
                        if piece == 'king' and abs(click_coords[0] - old_pos[0]) == 2:
                            black_locations[selection] = click_coords
                            black_castling[0] = True
                            if click_coords[0] == 6: # Kingside
                                rook_index = black_locations.index((7, 0))
                                black_locations[rook_index] = (5, 0)
                                black_castling[2] = True
                            else: # Queenside
                                rook_index = black_locations.index((0, 0))
                                black_locations[rook_index] = (3, 0)
                                black_castling[1] = True
                            en_passant_target = None
                        else:
                            en_passant_capture = False
                            # En Passant Capture
                            if piece == 'pawn' and en_passant_target and old_pos[1] == 4 and click_coords == (en_passant_target[0], 5):
                                captured_pawn_pos = en_passant_target
                                idx = white_locations.index(captured_pawn_pos)
                                captured_pieces_black.append(white_pieces.pop(idx))
                                white_locations.pop(idx)
                                en_passant_capture = True
                            
                            black_locations[selection] = click_coords
                            
                            # Update Castling Flags for Rook/King moves
                            if piece == 'king': black_castling[0] = True
                            elif piece == 'rook':
                                if old_pos == (0, 0): black_castling[1] = True
                                elif old_pos == (7, 0): black_castling[2] = True
                            
                            # Standard Capture
                            if not en_passant_capture and click_coords in white_locations:
                                idx = white_locations.index(click_coords)
                                if white_pieces[idx] == 'king': winner = 'Black'; game_over=True
                                captured_pieces_black.append(white_pieces.pop(idx))
                                white_locations.pop(idx)
                            
                            # En Passant Target Set
                            if piece == 'pawn' and old_pos[1] == 1 and click_coords[1] == 3:
                                en_passant_target = (click_coords[0], 3)
                            else:
                                en_passant_target = None
                            
                            # Pawn Promotion Trigger
                            if piece == 'pawn' and click_coords[1] == 7:
                                promotion_index = selection
                                promotion_color = 'black'
                                
                        # End Turn
                        black_options=check_options(black_pieces, black_locations,'black')
                        white_options=check_options(white_pieces, white_locations,'white')
                        if not promotion_index: # Only advance turn if not in promotion dialog
                            turn_step=0; selection=100; valid_moves=[]
                            
    if game_over:
        draw_game_over()
        
    pygame.display.flip()

# Exiting Pygame is important for the subprocess
pygame.quit()
"""

# --- SPACE MINER PYGAME  ---
PYGAME_MINER_CODE = """

import pygame
import numpy as np
import random
import sys

# --- Initialize pygame ---
pygame.init()

# --- Game Settings ---
GRID_SIZE = 8
CELL_SIZE = 60
WIDTH = HEIGHT = GRID_SIZE * CELL_SIZE
FPS = 10

# Colors
BLACK = (10, 10, 20)
GRAY = (80, 80, 100)
ORE_COLOR = (255, 223, 0)
ASTEROID_COLOR = (200, 60, 60)
PLAYER_COLOR = (0, 200, 255)
POWERUP_COLOR = (50, 205, 50)
TEXT_COLOR = (255, 255, 255)

# Initialize screen
screen = pygame.display.set_mode((WIDTH, HEIGHT + 100))
pygame.display.set_caption("SPACE MINER")

font = pygame.font.SysFont("consolas", 24)
clock = pygame.time.Clock()

# --- Background Music ---
pygame.mixer.init()
try:
    bg_music = pygame.mixer.Sound("backgroundmusicspaceminer.wav")
    bg_music.play(loops=-1)
except pygame.error as e:
    print(f" Cannot load background music: {e}")

grid = np.zeros((GRID_SIZE, GRID_SIZE), dtype=int)
player_pos = [GRID_SIZE // 2, GRID_SIZE // 2]
grid[player_pos[0], player_pos[1]] = 9
score = 0
health = 100
moves = 0
running = True

# Spawn initial objects
def spawn_objects():
    for _ in range(8):
        while True:
            x, y = random.randint(0, GRID_SIZE - 1), random.randint(0, GRID_SIZE - 1)
            if grid[x, y] == 0:  # empty
                grid[x, y] = 1
                break
    for _ in range(6):
        while True:
            x, y = random.randint(0, GRID_SIZE - 1), random.randint(0, GRID_SIZE - 1)
            if grid[x, y] == 0:
                grid[x, y] = -1
                break
    for _ in range(3):
        while True:
            x, y = random.randint(0, GRID_SIZE - 1), random.randint(0, GRID_SIZE - 1)
            if grid[x, y] == 0:
                grid[x, y] = 2
                break

spawn_objects()

#Helper functions 
def draw_grid():
    for x in range(GRID_SIZE):
        for y in range(GRID_SIZE):
            rect = pygame.Rect(y * CELL_SIZE, x * CELL_SIZE, CELL_SIZE, CELL_SIZE)
            cell_value = grid[x, y]
            if cell_value == 9:
                color = PLAYER_COLOR
            elif cell_value == 1:
                color = ORE_COLOR
            elif cell_value == -1:
                color = ASTEROID_COLOR
            elif cell_value == 2:
                color = POWERUP_COLOR
            else:
                color = GRAY
            pygame.draw.rect(screen, color, rect)
            pygame.draw.rect(screen, BLACK, rect, 2)

def draw_ui():
    ui_y = HEIGHT + 20
    text = font.render(f"Score: {score}   Health: {health}   Moves: {moves}", True, TEXT_COLOR)
    screen.blit(text, (20, ui_y))

def move_player(dx, dy):
    global player_pos, score, health, moves, running

    x, y = player_pos
    new_x, new_y = x + dx, y + dy

    if 0 <= new_x < GRID_SIZE and 0 <= new_y < GRID_SIZE:
        grid[x, y] = 0
        moves += 1

        if grid[new_x, new_y] == 1:
            score += 10
        elif grid[new_x, new_y] == -1:
            health -= 10
        elif grid[new_x, new_y] == 2:
            health = min(100, health + 20)

        grid[new_x, new_y] = 9
        player_pos = [new_x, new_y]

        # Randomly spawn objects
        # Randomly spawn objects
        if random.random() < 0.3:
            while True:
                rx, ry = random.randint(0, GRID_SIZE - 1), random.randint(0, GRID_SIZE - 1)
                if grid[rx, ry] == 0:
                    choice = random.choices([1, -1, 2], weights=[50, 40, 10], k=1)[0]
                    grid[rx, ry] = choice
                    break


        # Increase asteroid count with moves
        if moves % 5 == 0:  # every 5 moves
            while True:
                rx, ry = random.randint(0, GRID_SIZE - 1), random.randint(0, GRID_SIZE - 1)
                if grid[rx, ry] == 0:
                    grid[rx, ry] = -1
                    break

        if health <= 0:
            running = False

def show_game_over():
    screen.fill(BLACK)
    over_text = font.render("GAME OVER ", True, (255, 80, 80))
    score_text = font.render(f"Final Score: {score}", True, TEXT_COLOR)
    moves_text = font.render(f"Total Moves: {moves}", True, TEXT_COLOR)
    tip_text = font.render("Press any key to exit", True, TEXT_COLOR)

    screen.blit(over_text, (WIDTH // 2 - 100, HEIGHT // 2 - 70))
    screen.blit(score_text, (WIDTH // 2 - 100, HEIGHT // 2 - 30))
    screen.blit(moves_text, (WIDTH // 2 - 100, HEIGHT // 2 + 10))
    screen.blit(tip_text, (WIDTH // 2 - 100, HEIGHT // 2 + 50))
    pygame.display.flip()

    try:
        bg_music.stop()
    except:
        pass

    waiting = True
    while waiting:
        for event in pygame.event.get():
            if event.type == pygame.KEYDOWN or event.type == pygame.QUIT:
                waiting = False
    pygame.quit()
    sys.exit()

#Main Game Loop
while running:
    screen.fill(BLACK)
    draw_grid()
    draw_ui()
    pygame.display.flip()
    clock.tick(FPS)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
            break
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_UP:
                move_player(-1, 0)
            elif event.key == pygame.K_DOWN: 
                move_player(1, 0)
            elif event.key == pygame.K_LEFT: 
                move_player(0, -1)
            elif event.key == pygame.K_RIGHT: 
                move_player(0, 1)

show_game_over()
"""

PYGAME_PINGPONG_CODE="""
import pygame
import sys
import math # Import math for absolute value (optional, but good practice)

# --- Initialization ---
pygame.init()

# --- Constants ---
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
SCREEN_SIZE = (SCREEN_WIDTH, SCREEN_HEIGHT)
CAPTION = "Pong with Lives and Increasing Speed"
FPS = 60

# Colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)

# --- Background Music ---
pygame.mixer.init()
try:
    bg_music = pygame.mixer.Sound("backgroundmusicpingpong.wav")
    bg_music.play(loops=-1)
except pygame.error as e:
    print(f" Cannot load background music: {e}")

# Paddle properties
PADDLE_WIDTH = 15
PADDLE_HEIGHT = 100
PADDLE_SPEED = 7

# Ball properties
BALL_SIZE = 15
# START with slower speed
INITIAL_BALL_SPEED_X = 4
INITIAL_BALL_SPEED_Y = 4
MAX_SPEED_INCREASE = 10 # Cap the speed increase slightly

# Game Setup
INITIAL_LIVES = 3
SPEED_INCREASE_FACTOR = 0.2 # How much to increase speed on each paddle hit

# --- Setup Screen and Clock ---
screen = pygame.display.set_mode(SCREEN_SIZE)
pygame.display.set_caption(CAPTION)
clock = pygame.time.Clock()

# --- Font Setup for Score and Game Over ---
font = pygame.font.Font(None, 74)
small_font = pygame.font.Font(None, 36)

# --- Game Objects (Rectangles) ---

# Paddles
player1_paddle = pygame.Rect(50, SCREEN_HEIGHT // 2 - PADDLE_HEIGHT // 2, PADDLE_WIDTH, PADDLE_HEIGHT)
player2_paddle = pygame.Rect(SCREEN_WIDTH - 50 - PADDLE_WIDTH, SCREEN_HEIGHT // 2 - PADDLE_HEIGHT // 2, PADDLE_WIDTH, PADDLE_HEIGHT)

# Ball
ball = pygame.Rect(SCREEN_WIDTH // 2 - BALL_SIZE // 2, SCREEN_HEIGHT // 2 - BALL_SIZE // 2, BALL_SIZE, BALL_SIZE)

# Initial ball direction/velocity
ball_speed_x = INITIAL_BALL_SPEED_X * (1 if pygame.time.get_ticks() % 2 == 0 else -1)
ball_speed_y = INITIAL_BALL_SPEED_Y * (1 if pygame.time.get_ticks() % 3 != 0 else -1)

# Game State Variables
lives1 = INITIAL_LIVES
lives2 = INITIAL_LIVES
game_active = True # New state variable

# --- Functions ---

def draw_text(text, font_size, color, x, y):
    text_surface = font_size.render(text, True, color)
    text_rect = text_surface.get_rect(center=(x, y))
    screen.blit(text_surface, text_rect)

def move_paddles():
    keys = pygame.key.get_pressed()
    
    # Player 1 controls (W/S)
    if keys[pygame.K_w] and player1_paddle.top > 0:
        player1_paddle.y -= PADDLE_SPEED
    if keys[pygame.K_s] and player1_paddle.bottom < SCREEN_HEIGHT:
        player1_paddle.y += PADDLE_SPEED

    # Player 2 controls (Up/Down Arrows)
    if keys[pygame.K_UP] and player2_paddle.top > 0:
        player2_paddle.y -= PADDLE_SPEED
    if keys[pygame.K_DOWN] and player2_paddle.bottom < SCREEN_HEIGHT:
        player2_paddle.y += PADDLE_SPEED

def move_ball():
   
    global ball_speed_x, ball_speed_y, lives1, lives2, game_active
    
    ball.x += ball_speed_x
    ball.y += ball_speed_y

    # Collision with top/bottom walls
    if ball.top <= 0 or ball.bottom >= SCREEN_HEIGHT:
        ball_speed_y *= -1

    # Collision with left/right boundaries (Scoring / Losing a life)
    if ball.left <= 0:
        # Player 1 loses a life
        lives1 -= 1
        if lives1 <= 0:
            game_active = False # Game Over
        reset_ball(start_right=True)
    
    if ball.right >= SCREEN_WIDTH:
        # Player 2 loses a life
        lives2 -= 1
        if lives2 <= 0:
            game_active = False # Game Over
        reset_ball(start_right=False)

def check_paddle_collision():
   
    global ball_speed_x, ball_speed_y
    
    # Increase speed and reverse direction on collision
    if ball.colliderect(player1_paddle) or ball.colliderect(player2_paddle):
        
        # Increase speed (up to a limit)
        current_speed = math.sqrt(ball_speed_x**2 + ball_speed_y**2)
        new_speed = min(current_speed + SPEED_INCREASE_FACTOR, MAX_SPEED_INCREASE)

        # Calculate factor to maintain direction ratio but scale to new speed
        scale_factor = new_speed / current_speed
        
        # Only reverse X-direction if moving towards the paddle it hit
        if ball_speed_x < 0 and ball.colliderect(player1_paddle):
            ball_speed_x *= -1 * scale_factor
            ball_speed_y *= scale_factor
        elif ball_speed_x > 0 and ball.colliderect(player2_paddle):
            ball_speed_x *= -1 * scale_factor
            ball_speed_y *= scale_factor
        
        # Note: A more complex collision logic could adjust ball_speed_y based on where the ball hits the paddle.

def reset_ball(start_right=None):

    global ball_speed_x, ball_speed_y
    
    ball.x = SCREEN_WIDTH // 2 - BALL_SIZE // 2
    ball.y = SCREEN_HEIGHT // 2 - BALL_SIZE // 2
    
    # Reset speed to initial slow speed
    ball_speed_y = INITIAL_BALL_SPEED_Y * (1 if pygame.time.get_ticks() % 3 != 0 else -1)
    
    # Determine horizontal start direction
    if start_right is not None:
        # Start moving away from the player who just lost the point
        ball_speed_x = INITIAL_BALL_SPEED_X if start_right else -INITIAL_BALL_SPEED_X
    else:
        # Initial random start
        ball_speed_x = INITIAL_BALL_SPEED_X * (1 if pygame.time.get_ticks() % 2 == 0 else -1)

def draw_elements():
    screen.fill(BLACK) # Clear screen

    # Draw Paddles and Ball
    pygame.draw.rect(screen, WHITE, player1_paddle)
    pygame.draw.rect(screen, WHITE, player2_paddle)
    pygame.draw.ellipse(screen, WHITE, ball)

    # Draw center line
    pygame.draw.aaline(screen, WHITE, (SCREEN_WIDTH // 2, 0), (SCREEN_WIDTH // 2, SCREEN_HEIGHT))

    # Draw Lives (Score)
    draw_text(f"Lives: {lives1}", small_font, WHITE, SCREEN_WIDTH // 4, 30)
    draw_text(f"Lives: {lives2}", small_font, WHITE, SCREEN_WIDTH * 3 // 4, 30)

def display_game_over():
    screen.fill(BLACK)
    
    winner = 1 if lives2 <= 0 else 2
    game_over_text = "GAME OVER"
    winner_text = f"Player {winner} Wins!"

    draw_text(game_over_text, font, WHITE, SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 50)
    draw_text(winner_text, small_font, WHITE, SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 50)
    draw_text("Press ESC to Quit", small_font, WHITE, SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 150)


# --- Main Game Loop ---
running = True
while running:
    # 1. Event Handling
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if not game_active and event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
            running = False

    if game_active:
        # 2. Game Logic Updates
        move_paddles()
        move_ball()
        check_paddle_collision()
        
        # 3. Drawing/Rendering
        draw_elements()

    else:
        # Game Over Screen
        display_game_over()
        
    # Update the display
    pygame.display.flip()

    # Control frame rate
    clock.tick(FPS)

# --- Cleanup ---
pygame.quit()
sys.exit()
"""



# --- HTML and CSS Template (Complete) ---
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Gamecraft Central - Animated</title>
    <style>
        body, html {
            margin: 0;
            padding: 0;
            height: 100%; 
            font-family: 'Arial', sans-serif;
            color: #ffffff;
            text-align: center;
        }

        .animated-background {
            background: linear-gradient(-45deg, #ee7752, #e73c7e, #23a6d5, #23d5ab);
            background-size: 400% 400%;
            height: 100vh;
            width: 100vw;
            animation: GradientAnimation 15s ease infinite;
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: flex-start;
            padding-top: 50px;
            position: relative; 
            overflow: hidden;
        }

        @keyframes GradientAnimation {
            0% { background-position: 0% 50%; }
            50% { background-position: 100% 50%; }
            100% { background-position: 0% 50%; }
        }

        .content-container {
            background: rgba(0, 0, 0, 0.5);
            padding: 25px 50px;
            border-radius: 12px;
            box-shadow: 0 5px 20px rgba(0, 0, 0, 0.7);
            animation: fadeInScale 1.5s ease-out;
            margin-bottom: 40px;
        }

        .content-container h1 {
            font-size: 2.5em;
            margin: 0;
            text-shadow: 0 0 10px rgba(255, 255, 255, 0.8);
        }

        .game-icon-grid {
            display: flex;
            justify-content: center;
            gap: 30px;
        }
        
        .game-icon-link {
            text-decoration: none;
            color: inherit;
        }

        .game-icon {
            background: rgba(255, 255, 255, 0.15);
            border: 2px solid rgba(255, 255, 255, 0.3);
            border-radius: 15px;
            padding: 20px;
            width: 120px;
            height: 120px;
            display: flex;
            flex-direction: column;
            justify-content: center;
            align-items: center;
            transition: transform 0.3s ease, background 0.3s ease;
            cursor: pointer;
        }
        
        .game-icon:hover {
            transform: scale(1.1);
            background: rgba(255, 255, 255, 0.3);
            box-shadow: 0 0 20px rgba(255, 255, 255, 0.6);
        }
        
        .game-icon .icon-symbol {
            font-size: 3em;
            margin-bottom: 5px;
        }
        
        .game-icon .icon-name {
            font-size: 0.9em;
            font-weight: bold;
            color: #fff;
        }
        
        @keyframes fadeInScale {
            0% { opacity: 0; transform: scale(0.9); }
            100% { opacity: 1; transform: scale(1); }
        }
    </style>
</head>
<body>

    <div class="animated-background">
        <div class="content-container">
            <h1>🎉Gamekraft Central🐍</h1>
        </div>
        <br>
        <br>
        <br>
        <br>
        <br>
        <br>
        <br>
        <br>
        
        
        <div class="game-icon-grid">
            
            <a href="/launch_chess" class="game-icon-link">
                <div class="game-icon">
                    <span class="icon-symbol">♞</span> <span class="icon-name">CHESS</span>
                </div>
            </a>
            
            <a href="/launch_rps" class="game-icon-link">
                <div class="game-icon">
                    <span class="icon-symbol">✂️</span> <span class="icon-name">ROCK PAPER SCISSORS</span>
                </div>
            </a>
            
            <a href="/launch_spaceminer_game" class="game-icon-link">
                <div class="game-icon">
                    <span class="icon-symbol">🚀</span> <span class="icon-name">SPACE MINER</span>
                </div>
            </a>
            <a href="/launch_pingpong" class="game-icon-link">
                <div class="game-icon">
                 <span class="icon-symbol">| • |</span> <span class="icon-name">PING PONG</span>
                </div>
            </a>

        </div>
    </div>

</body>
</html>
"""

# ----------------------------------------------------
## FLASK ROUTES
# ----------------------------------------------------

@app.route('/')
def home():
   
    return render_template_string(HTML_TEMPLATE)

@app.route('/launch_rps')
def launch_rps():
    
    run_game_script(PYGAME_RPS_CODE, "rps_game.py")
    return redirect(url_for('home'))

@app.route('/launch_chess')
def launch_chess():
    
    run_game_script(PYGAME_CHESS_CODE, "chess_game.py")
    return redirect(url_for('home'))

@app.route('/launch_spaceminer_game')
def launch_miner():
    run_game_script(PYGAME_MINER_CODE, "spaceminer_game.py")
    return redirect(url_for('home'))

@app.route('/launch_pingpong')
def launch_pingpong():
    run_game_script(PYGAME_PINGPONG_CODE, "pingpong_game.py")
    return redirect(url_for('home'))

# ----------------------------------------------------
## APPLICATION ENTRY POINT
# ----------------------------------------------------

if __name__ == '__main__':
    try:
        app.run(debug=True, use_reloader=False) 
    except OSError as e:
        print(f"ERROR: Could not start Flask server. Port may be in use: {e}")


