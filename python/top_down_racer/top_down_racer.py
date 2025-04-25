import pygame
import random
import asyncio
import platform
import numpy as np

# Initialize Pygame
pygame.init()

# Screen settings
WIDTH = 800
HEIGHT = 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Top-Down Racer")

# Colors
GRAY = (100, 100, 100)
WHITE = (255, 255, 255)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLACK = (0, 0, 0)

# Game settings
FPS = 60
PLAYER_SPEED = 5
ENEMY_SPEED = 3
ROAD_WIDTH = 400
ROAD_X = (WIDTH - ROAD_WIDTH) // 2

# Player car
player_size = (40, 60)
player = pygame.Surface(player_size)
player.fill(RED)
player_rect = player.get_rect(center=(WIDTH // 2, HEIGHT - 100))

# Enemy car
enemy_size = (40, 60)
enemy = pygame.Surface(enemy_size)
enemy.fill(GREEN)
enemy_rect = enemy.get_rect(center=(random.randint(ROAD_X + 20, ROAD_X + ROAD_WIDTH - 20), -enemy_size[1]))

# Sound (simple beep for collision)
def create_collision_sound():
    sample_rate = 44100
    duration = 0.1
    freq = 440
    t = np.linspace(0, duration, int(sample_rate * duration), False)
    sound_data = np.sin(2 * np.pi * freq * t) * 32767
    sound_array = np.column_stack((sound_data, sound_data)).astype(np.int16)
    return pygame.sndarray.make_sound(sound_array)

collision_sound = create_collision_sound()

# Game variables
score = 0
game_over = False
font = pygame.font.SysFont(None, 48)
clock = pygame.time.Clock()

def setup():
    global score, game_over, player_rect, enemy_rect
    score = 0
    game_over = False
    player_rect.center = (WIDTH // 2, HEIGHT - 100)
    enemy_rect.center = (random.randint(ROAD_X + 20, ROAD_X + ROAD_WIDTH - 20), -enemy_size[1])

def update_loop():
    global score, game_over, enemy_rect

    if not game_over:
        # Player movement
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT] and player_rect.left > ROAD_X:
            player_rect.x -= PLAYER_SPEED
        if keys[pygame.K_RIGHT] and player_rect.right < ROAD_X + ROAD_WIDTH:
            player_rect.x += PLAYER_SPEED
        if keys[pygame.K_UP] and player_rect.top > 0:
            player_rect.y -= PLAYER_SPEED
        if keys[pygame.K_DOWN] and player_rect.bottom < HEIGHT:
            player_rect.y += PLAYER_SPEED

        # Enemy movement
        enemy_rect.y += ENEMY_SPEED
        if enemy_rect.top > HEIGHT:
            enemy_rect.center = (random.randint(ROAD_X + 20, ROAD_X + ROAD_WIDTH - 20), -enemy_size[1])

        # Collision detection
        if player_rect.colliderect(enemy_rect) or player_rect.left <= ROAD_X or player_rect.right >= ROAD_X + ROAD_WIDTH:
            collision_sound.play()
            game_over = True

        # Update score
        score += 1 / FPS

    # Draw
    screen.fill(BLACK)
    # Draw road
    pygame.draw.rect(screen, GRAY, (ROAD_X, 0, ROAD_WIDTH, HEIGHT))
    pygame.draw.rect(screen, WHITE, (ROAD_X - 10, 0, 10, HEIGHT))
    pygame.draw.rect(screen, WHITE, (ROAD_X + ROAD_WIDTH, 0, 10, HEIGHT))
    # Draw cars
    screen.blit(player, player_rect)
    screen.blit(enemy, enemy_rect)
    # Draw score
    score_text = font.render(f"Score: {int(score)}", True, WHITE)
    screen.blit(score_text, (10, 10))
    # Draw game over
    if game_over:
        game_over_text = font.render(f"Game Over! Score: {int(score)}", True, WHITE)
        text_rect = game_over_text.get_rect(center=(WIDTH // 2, HEIGHT // 2))
        screen.blit(game_over_text, text_rect)

    pygame.display.flip()

async def main():
    setup()
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                return
            if event.type == pygame.KEYDOWN and game_over and event.key == pygame.K_SPACE:
                setup()  # Restart game
        update_loop()
        await asyncio.sleep(1.0 / FPS)

if platform.system() == "Emscripten":
    asyncio.ensure_future(main())
else:
    if __name__ == "__main__":
        asyncio.run(main())