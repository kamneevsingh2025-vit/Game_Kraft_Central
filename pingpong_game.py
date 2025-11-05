
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
