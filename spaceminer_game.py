

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
