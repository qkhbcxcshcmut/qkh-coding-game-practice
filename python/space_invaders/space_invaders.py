import pygame
import random
import sys
import asyncio
import platform

# Initialize Pygame
pygame.init()
pygame.mixer.init()

# Screen configuration
WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Space Invaders")

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
BLUE = (50, 50, 255)
GREEN = (50, 255, 50)

# Fonts
font = pygame.font.SysFont("Arial", 36)
title_font = pygame.font.SysFont("Arial", 48, bold=True)

# Load sounds
try:
    shoot_sound = pygame.mixer.Sound("shoot.wav")
    explosion_sound = pygame.mixer.Sound("explosion.wav")
except FileNotFoundError:
    print("Sound files not found. Running without sound.")
    shoot_sound = explosion_sound = None

# Player class
class Player(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = pygame.Surface((50, 50))
        self.image.fill(GREEN)
        self.rect = self.image.get_rect(center=(WIDTH // 2, HEIGHT - 50))
        self.speed = 5
        self.health = 3

    def update(self):
        keys = pygame.key.get_pressed()
        if (keys[pygame.K_LEFT] or keys[pygame.K_a]) and self.rect.left > 0:
            self.rect.x -= self.speed
        if (keys[pygame.K_RIGHT] or keys[pygame.K_d]) and self.rect.right < WIDTH:
            self.rect.x += self.speed

# Enemy class
class Enemy(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = pygame.Surface((40, 40))
        self.image.fill(RED)
        self.rect = self.image.get_rect(topleft=(x, y))
        self.speed = 2
        self.direction = 1

    def update(self):
        self.rect.x += self.speed * self.direction
        if random.random() < 0.01:  # Chance to shoot
            bullet = Bullet(self.rect.centerx, self.rect.bottom, 5)
            enemy_bullets.add(bullet)
            all_sprites.add(bullet)

# Bullet class
class Bullet(pygame.sprite.Sprite):
    def __init__(self, x, y, speed):
        super().__init__()
        self.image = pygame.Surface((5, 10))
        self.image.fill(WHITE if speed < 0 else RED)
        self.rect = self.image.get_rect(center=(x, y))
        self.speed = speed

    def update(self):
        self.rect.y += self.speed
        if self.rect.bottom < 0 or self.rect.top > HEIGHT:
            self.kill()

# Sprite groups
all_sprites = pygame.sprite.Group()
enemies = pygame.sprite.Group()
player_bullets = pygame.sprite.Group()
enemy_bullets = pygame.sprite.Group()

# Initialize game variables
player = None
score = 0
game_state = "start"
clock = pygame.time.Clock()
FPS = 60

# Draw text function
def draw_text(text, x, y, color=WHITE, use_title_font=False):
    selected_font = title_font if use_title_font else font
    img = selected_font.render(text, True, color)
    screen.blit(img, (x, y))

# Draw button function
def draw_button(text, x, y, width, height, inactive_color, active_color):
    mouse = pygame.mouse.get_pos()
    click = pygame.mouse.get_pressed()
    
    button_rect = pygame.Rect(x, y, width, height)
    color = active_color if button_rect.collidepoint(mouse) else inactive_color
    
    pygame.draw.rect(screen, color, button_rect, border_radius=10)
    text_surface = font.render(text, True, WHITE)
    text_rect = text_surface.get_rect(center=button_rect.center)
    screen.blit(text_surface, text_rect)
    
    return button_rect.collidepoint(mouse) and click[0] == 1

# Initialize game
def setup():
    global player, all_sprites, enemies, player_bullets, enemy_bullets, score
    all_sprites.empty()
    enemies.empty()
    player_bullets.empty()
    enemy_bullets.empty()
    
    player = Player()
    all_sprites.add(player)
    
    for row in range(3):
        for col in range(10):
            enemy = Enemy(col * 60 + 50, row * 60 + 50)
            enemies.add(enemy)
            all_sprites.add(enemy)
    
    score = 0

# Game loop
async def main():
    global game_state, score
    setup()
    running = True
    
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if game_state == "playing" and event.key == pygame.K_SPACE:
                    bullet = Bullet(player.rect.centerx, player.rect.top, -7)
                    player_bullets.add(bullet)
                    all_sprites.add(bullet)
                    if shoot_sound:
                        shoot_sound.play()

        screen.fill(BLACK)

        if game_state == "start":
            draw_text("Space Invaders", WIDTH // 2 - 140, HEIGHT // 3, WHITE, True)
            if draw_button("Play Game", WIDTH // 2 - 100, HEIGHT // 2, 200, 60, BLUE, GREEN):
                game_state = "playing"
        
        elif game_state == "game_over":
            draw_text("Game Over", WIDTH // 2 - 100, HEIGHT // 3, WHITE, True)
            draw_text(f"Score: {score}", WIDTH // 2 - 60, HEIGHT // 2 - 30)
            if draw_button("Play Again", WIDTH // 2 - 100, HEIGHT // 2 + 30, 200, 60, BLUE, GREEN):
                setup()
                game_state = "playing"
        
        else:
            # Update
            all_sprites.update()

            # Enemy movement
            if enemies:
                leftmost = min(enemy.rect.left for enemy in enemies)
                rightmost = max(enemy.rect.right for enemy in enemies)
                if rightmost >= WIDTH or leftmost <= 0:
                    for enemy in enemies:
                        enemy.direction *= -1
                        enemy.rect.y += 20

            # Handle collisions
            for bullet in player_bullets:
                hits = pygame.sprite.spritecollide(bullet, enemies, True)
                if hits:
                    bullet.kill()
                    score += 10
                    if explosion_sound:
                        explosion_sound.play()

            for bullet in enemy_bullets:
                if pygame.sprite.collide_rect(bullet, player):
                    bullet.kill()
                    player.health -= 1
                    if player.health <= 0:
                        game_state = "game_over"

            # Check if enemies reach bottom
            for enemy in enemies:
                if enemy.rect.bottom >= HEIGHT:
                    game_state = "game_over"

            # Draw
            all_sprites.draw(screen)
            draw_text(f"Score: {score}", 20, 20)
            draw_text(f"Health: {player.health}", 20, 60)

        pygame.display.flip()
        clock.tick(FPS)
        await asyncio.sleep(1.0 / FPS)

    pygame.quit()
    sys.exit()

# Run game
if platform.system() == "Emscripten":
    asyncio.ensure_future(main())
else:
    if __name__ == "__main__":
        asyncio.run(main())