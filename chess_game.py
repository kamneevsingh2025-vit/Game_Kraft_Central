
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
