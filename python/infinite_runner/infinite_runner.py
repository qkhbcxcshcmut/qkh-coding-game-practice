import pygame
import random
import math
import asyncio
import platform

# Initialize Pygame
pygame.init()

# Set up the display
WIDTH, HEIGHT = 800, 400
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Infinite Runner")

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
YELLOW = (255, 255, 0)
GREEN = (0, 255, 0)

# Game constants
GROUND_HEIGHT = HEIGHT - 50
FPS = 60
INITIAL_SPEED = 5
SPEED_INCREMENT = 0.01

# Player class
class Player:
    def __init__(self):
        self.width = 40
        self.height = 60
        self.x = 100
        self.y = GROUND_HEIGHT - self.height
        self.jump_velocity = -15
        self.velocity_y = 0
        self.gravity = 0.8
        self.is_jumping = False
        self.is_sliding = False
        self.rect = pygame.Rect(self.x, self.y, self.width, self.height)

    def jump(self):
        # Start jumping if not already jumping or sliding
        if not self.is_jumping and not self.is_sliding:
            self.velocity_y = self.jump_velocity
            self.is_jumping = True

    def slide(self):
        # Start sliding if not jumping or already sliding
        if not self.is_jumping and not self.is_sliding:
            self.is_sliding = True
            self.height = 30  # Reduce height when sliding
            self.y = GROUND_HEIGHT - self.height
            self.rect = pygame.Rect(self.x, self.y, self.width, self.height)

    def stop_slide(self):
        # Stop sliding and restore normal height
        if self.is_sliding:
            self.is_sliding = False
            self.height = 60
            self.y = GROUND_HEIGHT - self.height
            self.rect = pygame.Rect(self.x, self.y, self.width, self.height)

    def update(self):
        # Update player position during jump
        if self.is_jumping:
            self.y += self.velocity_y
            self.velocity_y += self.gravity
            if self.y >= GROUND_HEIGHT - self.height:
                self.y = GROUND_HEIGHT - self.height
                self.is_jumping = False
                self.velocity_y = 0
        self.rect = pygame.Rect(self.x, self.y, self.width, self.height)

    def draw(self):
        # Draw player (green when sliding, white otherwise)
        color = GREEN if self.is_sliding else WHITE
        pygame.draw.rect(screen, color, (self.x, self.y, self.width, self.height))

# Obstacle class
class Obstacle:
    def __init__(self, x):
        self.width = 30
        self.height = random.randint(30, 60)
        self.x = x
        self.y = GROUND_HEIGHT - self.height
        self.rect = pygame.Rect(self.x, self.y, self.width, self.height)

    def update(self, speed):
        # Move obstacle left
        self.x -= speed
        self.rect = pygame.Rect(self.x, self.y, self.width, self.height)

    def draw(self):
        # Draw obstacle as a black rectangle
        pygame.draw.rect(screen, BLACK, (self.x, self.y, self.width, self.height))

# Coin class
class Coin:
    def __init__(self, x):
        self.radius = 15
        self.x = x
        self.base_y = GROUND_HEIGHT - 100
        self.y = self.base_y
        self.phase = random.uniform(0, 2 * math.pi)
        self.rect = pygame.Rect(self.x - self.radius, self.y - self.radius, self.radius * 2, self.radius * 2)

    def update(self, speed, time):
        # Move coin left and apply floating effect
        self.x -= speed
        self.y = self.base_y + math.sin(time * 2 + self.phase) * 30
        self.rect = pygame.Rect(self.x - self.radius, self.y - self.radius, self.radius * 2, self.radius * 2)

    def draw(self):
        # Draw coin as a yellow circle
        pygame.draw.circle(screen, YELLOW, (int(self.x), int(self.y)), self.radius)

# Background class
class Background:
    def __init__(self):
        self.x1 = 0
        self.x2 = WIDTH
        self.speed = INITIAL_SPEED

    def update(self, speed):
        # Move background left to create scrolling effect
        self.speed = speed
        self.x1 -= self.speed
        self.x2 -= self.speed
        if self.x1 <= -WIDTH:
            self.x1 = self.x2 + WIDTH
        if self.x2 <= -WIDTH:
            self.x2 = self.x1 + WIDTH

    def draw(self):
        # Draw sky and ground
        screen.fill((134, 206, 250))  # Blue sky
        pygame.draw.rect(screen, (139, 69, 19), (0, GROUND_HEIGHT, WIDTH, HEIGHT))  # Brown ground
        # Draw scrolling ground lines
        pygame.draw.line(screen, WHITE, (self.x1, GROUND_HEIGHT), (self.x1 + WIDTH, GROUND_HEIGHT), 5)
        pygame.draw.line(screen, WHITE, (self.x2, GROUND_HEIGHT), (self.x2 + WIDTH, GROUND_HEIGHT), 5)

# Draw score
def draw_score(score):
    font = pygame.font.SysFont(None, 36)
    text = font.render(f"Score: {score}", True, BLACK)
    screen.blit(text, (10, 10))

# Draw game over screen
def draw_game_over(score):
    font = pygame.font.SysFont(None, 48)
    text = font.render(f"Game Over! Score: {score}", True, BLACK)
    text_rect = text.get_rect(center=(WIDTH // 2, HEIGHT // 2 - 20))
    screen.blit(text, text_rect)
    
    # Draw play again prompt
    font_small = pygame.font.SysFont(None, 36)
    play_again_text = font_small.render("Press R to Play Again", True, BLACK)
    play_again_rect = play_again_text.get_rect(center=(WIDTH // 2, HEIGHT // 2 + 20))
    screen.blit(play_again_text, play_again_rect)

# Initialize game state
def setup():
    global player, obstacles, coins, background, score, game_speed, time, game_over
    player = Player()
    obstacles = []
    coins = []
    background = Background()
    score = 0
    game_speed = INITIAL_SPEED
    time = 0
    game_over = False

# Update game state
def update_loop():
    global game_speed, time, score, game_over
    if not game_over:
        time += 1 / FPS
        game_speed += SPEED_INCREMENT / FPS

        # Handle events
        for event in pygame.event.get():
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    player.jump()
                elif event.key == pygame.K_DOWN:
                    player.slide()
            elif event.type == pygame.KEYUP:
                if event.key == pygame.K_DOWN:
                    player.stop_slide()

        # Update player
        player.update()

        # Spawn obstacles randomly
        if random.random() < 0.02:
            obstacles.append(Obstacle(WIDTH))
        # Spawn coins randomly
        if random.random() < 0.015:
            coins.append(Coin(WIDTH))

        # Update obstacles
        for obstacle in obstacles[:]:
            obstacle.update(game_speed)
            if obstacle.x < -obstacle.width:
                obstacles.remove(obstacle)
            if obstacle.rect.colliderect(player.rect):
                game_over = True

        # Update coins
        for coin in coins[:]:
            coin.update(game_speed, time)
            if coin.x < -coin.radius:
                coins.remove(coin)
            if coin.rect.colliderect(player.rect):
                coins.remove(coin)
                score += 1

        # Update background
        background.update(game_speed)

        # Draw game elements
        background.draw()
        player.draw()
        for obstacle in obstacles:
            obstacle.draw()
        for coin in coins:
            coin.draw()
        draw_score(score)
    else:
        # Draw game over screen
        background.draw()  # Keep background visible
        draw_game_over(score)
        
        # Check for play again input
        for event in pygame.event.get():
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_r:
                    setup()  # Reset game state

    pygame.display.flip()

# Main game loop
async def main():
    setup()
    while True:
        update_loop()
        await asyncio.sleep(1.0 / FPS)

# Run the game
if platform.system() == "Emscripten":
    asyncio.ensure_future(main())
else:
    if __name__ == "__main__":
        asyncio.run(main())