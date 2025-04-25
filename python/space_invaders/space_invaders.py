import pygame
import random
import sys
import asyncio
import platform
import os

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

# Asset folder
ASSET_PATH = "assets"

# Load images with fallback to surfaces
def load_image(filename, size, fallback_color):
    try:
        path = os.path.join(ASSET_PATH, filename)
        image = pygame.image.load(path).convert_alpha()
        image = pygame.transform.scale(image, size)
        return image
    except (FileNotFoundError, pygame.error) as e:
        print(f"Could not load {filename}: {e}. Using fallback surface.")
        surface = pygame.Surface(size)
        surface.fill(fallback_color)
        return surface

# Load sounds
try:
    shoot_sound = pygame.mixer.Sound(os.path.join(ASSET_PATH, "shoot.wav"))
    explosion_sound = pygame.mixer.Sound(os.path.join(ASSET_PATH, "explosion.wav"))
except FileNotFoundError:
    print("Sound files not found. Running without sound.")
    shoot_sound = explosion_sound = None

# Player class
class Player(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = load_image("player.png", (50, 50), GREEN)
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
        self.image = load_image("enemy.png", (40, 40), RED)
        self.rect = self.image.get_rect(topleft=(x, y))
        self.speed = 2
        self.direction = 1

    def update(self):
        self.rect.x += self.speed * self.direction
        if random.random() < 0.01:  # Chance to shoot
            bullet = Bullet(self.rect.centerx, self.rect.bottom, 5, is_player=False)
            enemy_bullets.add(bullet)
            all_sprites.add(bullet)

# Bullet class
class Bullet(pygame.sprite.Sprite):
    def __init__(self, x, y, speed, is_player=True):
        super().__init__()
        filename = "bullet_player.png" if is_player else "bullet_enemy.png"
        fallback_color = WHITE if is_player else RED
        self.image = load_image(filename, (5, 10), fallback_color)
        self.rect = self.image.get_rect(center=(x, y))
        self.speed = speed

    def update(self):
        self.rect.y += self.speed
        if self.rect.bottom < 0 or self.rect.top > HEIGHT:
            self.kill()

# Hit Effect class
class HitEffect(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = load_image("hit_effect.png", (40, 40), WHITE)
        self.rect = self.image.get_rect(center=(x, y))
        self.lifetime = 10  # Frames to display effect
        self.timer = 0

    def update(self):
        self.timer += 1
        if self.timer >= self.lifetime:
            self.kill()

# Sprite groups
all_sprites = pygame.sprite.Group()
enemies = pygame.sprite.Group()
player_bullets = pygame.sprite.Group()
enemy_bullets = pygame.sprite.Group()
hit_effects = pygame.sprite.Group()

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
    global player, all_sprites, enemies, player_bullets, enemy_bullets, hit_effects, score
    all_sprites.empty()
    enemies.empty()
    player_bullets.empty()
    enemy_bullets.empty()
    hit_effects.empty()
    
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
                    bullet = Bullet(player.rect.centerx, player.rect.top, -7, is_player=True)
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
            hit_effects.update()

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
                    # Add hit effect
                    for hit in hits:
                        effect = HitEffect(hit.rect.centerx, hit.rect.centery)
                        hit_effects.add(effect)
                        all_sprites.add(effect)

            for bullet in enemy_bullets:
                if pygame.sprite.collide_rect(bullet, player):
                    bullet.kill()
                    player.health -= 1
                    # Add hit effect
                    effect = HitEffect(player.rect.centerx, player.rect.centery)
                    hit_effects.add(effect)
                    all_sprites.add(effect)
                    if player.health <= 0:
                        game_state = "game_over"

            # Check if enemies reach bottom
            for enemy in enemies:
                if enemy.rect.bottom >= HEIGHT:
                    game_state = "game_over"

            # Draw
            all_sprites.draw(screen)
            hit_effects.draw(screen)
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