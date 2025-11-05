
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
    elif (player=="Rock" and computer=="Scissors") or          (player=="Paper" and computer=="Rock") or          (player=="Scissors" and computer=="Paper"):
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
