import pygame
import random
import sys
import math

# Initialize Pygame
pygame.init()

# Game settings
ROWS = 20
COLS = 10
BLOCK_SIZE = 30
NEXT_BLOCK_SIZE = 25
WINDOW_WIDTH = 800
WINDOW_HEIGHT = 600
BOARD_WIDTH = COLS * BLOCK_SIZE
BOARD_HEIGHT = ROWS * BLOCK_SIZE
BOARD_X = (WINDOW_WIDTH - BOARD_WIDTH) // 2
BOARD_Y = (WINDOW_HEIGHT - BOARD_HEIGHT) // 2

# Colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GRAY = (128, 128, 128)
DARK_GRAY = (50, 50, 50)
CYAN = (0, 255, 255)
BLUE = (0, 0, 255)
ORANGE = (255, 127, 0)
YELLOW = (255, 255, 0)
GREEN = (0, 255, 0)
PURPLE = (128, 0, 128)
RED = (255, 0, 0)
DARK_BLUE = (0, 0, 50)

COLORS = [
    None,
    CYAN,    # I
    BLUE,    # J
    ORANGE,  # L
    YELLOW,  # O
    GREEN,   # S
    PURPLE,  # T
    RED      # Z
]

# Piece shapes
SHAPES = [
    None,
    [[0, 0, 0, 0], [1, 1, 1, 1], [0, 0, 0, 0], [0, 0, 0, 0]],  # I
    [[2, 0, 0], [2, 2, 2], [0, 0, 0]],                          # J
    [[0, 0, 3], [3, 3, 3], [0, 0, 0]],                          # L
    [[0, 4, 4], [0, 4, 4], [0, 0, 0]],                          # O
    [[0, 5, 5], [5, 5, 0], [0, 0, 0]],                          # S
    [[0, 6, 0], [6, 6, 6], [0, 0, 0]],                          # T
    [[7, 7, 0], [0, 7, 7], [0, 0, 0]]                           # Z
]

# Fonts (try to download "Press Start 2P" or replace with "monospace")
try:
    FONT = pygame.font.Font("pressstart2p.ttf", 36)
    SMALL_FONT = pygame.font.Font("pressstart2p.ttf", 20)
except:
    FONT = pygame.font.SysFont("monospace", 36)
    SMALL_FONT = pygame.font.SysFont("monospace", 20)

# Particle system for explosion effect
particles = []

class Particle:
    def __init__(self, x, y, color):
        self.x = x
        self.y = y
        self.color = color
        self.vx = random.uniform(-3, 3)
        self.vy = random.uniform(-3, 3)
        self.lifetime = random.randint(20, 40)
        self.size = random.randint(5, 10)

    def update(self):
        self.x += self.vx
        self.y += self.vy
        self.lifetime -= 1
        self.size = max(2, self.size - 0.2)

    def draw(self, surface):
        if self.lifetime > 0:
            alpha = int(255 * (self.lifetime / 40))
            color = (*self.color[:3], alpha)
            surf = pygame.Surface((self.size, self.size), pygame.SRCALPHA)
            pygame.draw.circle(surf, color, (self.size / 2, self.size / 2), self.size / 2)
            surface.blit(surf, (self.x - self.size / 2, self.y - self.size / 2))

# Game state
board = [[0] * COLS for _ in range(ROWS)]
score = 0
level = 1
game_over = False
is_paused = False
current_piece = None
next_piece = None
drop_time = 0
title_scale = 1.0
title_pulse = 0.02  # For title animation

# Screen setup
screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
pygame.display.set_caption("Tetris")
clock = pygame.time.Clock()

def create_board():
    return [[0] * COLS for _ in range(ROWS)]

def get_random_piece():
    piece_id = random.randint(1, 7)
    return {
        "shape": SHAPES[piece_id],
        "color": COLORS[piece_id],
        "pos": {"x": COLS // 2 - 1, "y": 0},
        "id": piece_id
    }

def draw_gradient_background():
    for y in range(WINDOW_HEIGHT):
        t = y / WINDOW_HEIGHT
        r = int(DARK_BLUE[0] * (1 - t) + BLACK[0] * t)
        g = int(DARK_BLUE[1] * (1 - t) + BLACK[1] * t)
        b = int(DARK_BLUE[2] * (1 - t) + BLACK[2] * t)
        pygame.draw.line(screen, (r, g, b), (0, y), (WINDOW_WIDTH, y))

def draw_block(surface, x, y, color, block_size, is_board=False):
    pygame.draw.rect(surface, color, (x * block_size, y * block_size, block_size, block_size))
    if is_board and not color:  # Draw grid for empty board cells
        pygame.draw.rect(surface, (255, 255, 255, 50), (x * block_size, y * block_size, block_size, block_size), 1)
    else:
        pygame.draw.rect(surface, BLACK, (x * block_size, y * block_size, block_size, block_size), 1)

def draw_board():
    draw_gradient_background()
    # Draw board with grid
    board_surface = pygame.Surface((BOARD_WIDTH, BOARD_HEIGHT), pygame.SRCALPHA)
    for y in range(ROWS):
        for x in range(COLS):
            if board[y][x]:
                draw_block(board_surface, x, y, board[y][x], BLOCK_SIZE, is_board=True)
            else:
                draw_block(board_surface, x, y, (0, 0, 0, 0), BLOCK_SIZE, is_board=True)
    
    # Draw current piece
    if current_piece:
        for y, row in enumerate(current_piece["shape"]):
            for x, value in enumerate(row):
                if value:
                    draw_block(board_surface, current_piece["pos"]["x"] + x,
                              current_piece["pos"]["y"] + y,
                              current_piece["color"], BLOCK_SIZE)
    screen.blit(board_surface, (BOARD_X, BOARD_Y))
    # Draw board border
    pygame.draw.rect(screen, GRAY, (BOARD_X - 2, BOARD_Y - 2, BOARD_WIDTH + 4, BOARD_HEIGHT + 4), 2)

def draw_next_piece():
    next_surface = pygame.Surface((120, 120), pygame.SRCALPHA)
    next_surface.fill((50, 50, 50, 200))
    if next_piece:
        for y, row in enumerate(next_piece["shape"]):
            for x, value in enumerate(row):
                if value:
                    draw_block(next_surface, x, y, next_piece["color"], NEXT_BLOCK_SIZE)
    pygame.draw.rect(next_surface, GRAY, (0, 0, 120, 120), 2)
    screen.blit(next_surface, (BOARD_X + BOARD_WIDTH + 50, BOARD_Y + 50))

def is_valid_position(piece, offset={"x": 0, "y": 0}):
    for y, row in enumerate(piece["shape"]):
        for x, value in enumerate(row):
            if value:
                new_x = piece["pos"]["x"] + x + offset["x"]
                new_y = piece["pos"]["y"] + y + offset["y"]
                if not (0 <= new_x < COLS and new_y < ROWS and (new_y < 0 or board[new_y][new_x] == 0)):
                    return False
    return True

def rotate():
    if not current_piece or game_over or is_paused:
        return
    original_shape = current_piece["shape"]
    original_pos = current_piece["pos"].copy()
    rows = len(current_piece["shape"])
    cols = len(current_piece["shape"][0])
    new_shape = [[0] * rows for _ in range(cols)]
    for y in range(rows):
        for x in range(cols):
            new_shape[x][rows - 1 - y] = current_piece["shape"][y][x]
    current_piece["shape"] = new_shape
    if not is_valid_position(current_piece):
        if current_piece["pos"]["x"] > COLS / 2:
            current_piece["pos"]["x"] -= 1
        else:
            current_piece["pos"]["x"] += 1
        if not is_valid_position(current_piece):
            current_piece["shape"] = original_shape
            current_piece["pos"] = original_pos

def move_left():
    if not current_piece or game_over or is_paused:
        return
    if is_valid_position(current_piece, {"x": -1, "y": 0}):
        current_piece["pos"]["x"] -= 1

def move_right():
    if not current_piece or game_over or is_paused:
        return
    if is_valid_position(current_piece, {"x": 1, "y": 0}):
        current_piece["pos"]["x"] += 1

def move_down():
    if not current_piece or game_over or is_paused:
        return False
    if is_valid_position(current_piece, {"x": 0, "y": 1}):
        current_piece["pos"]["y"] += 1
        return True
    return False

def hard_drop():
    if not current_piece or game_over or is_paused:
        return
    while move_down():
        pass
    lock_piece()

def spawn_explosion(y):
    # Spawn particles for each block in the cleared line
    for x in range(COLS):
        color = board[y][x] if board[y][x] else WHITE
        for _ in range(5):  # Number of particles per block
            px = BOARD_X + x * BLOCK_SIZE + BLOCK_SIZE / 2
            py = BOARD_Y + y * BLOCK_SIZE + BLOCK_SIZE / 2
            particles.append(Particle(px, py, color))

def lock_piece():
    global current_piece, next_piece
    for y, row in enumerate(current_piece["shape"]):
        for x, value in enumerate(row):
            if value:
                board_y = current_piece["pos"]["y"] + y
                if board_y >= 0:
                    board[board_y][current_piece["pos"]["x"] + x] = current_piece["color"]
    lines = check_lines()
    if lines > 0:
        add_score(lines)
    current_piece = next_piece
    next_piece = get_random_piece()
    if not is_valid_position(current_piece):
        global game_over
        game_over = True
    global drop_time
    drop_time = pygame.time.get_ticks()

def check_lines():
    lines = 0
    y = ROWS - 1
    while y >= 0:
        if all(board[y]):
            spawn_explosion(y)
            board.pop(y)
            board.insert(0, [0] * COLS)
            lines += 1
        else:
            y -= 1
    return lines

def add_score(lines):
    global score, level
    line_points = [0, 100, 300, 500, 800]
    score += line_points[lines] * level
    new_level = score // 1000 + 1
    if new_level > level:
        level = new_level

def draw_start_screen():
    global title_scale, title_pulse
    draw_gradient_background()
    # Title animation
    title_scale += title_pulse
    if title_scale > 1.1 or title_scale < 0.9:
        title_pulse = -title_pulse
    title = FONT.render("TETRIS", True, CYAN)
    scaled_title = pygame.transform.scale(title, (int(title.get_width() * title_scale), int(title.get_height() * title_scale)))
    screen.blit(scaled_title, (WINDOW_WIDTH // 2 - scaled_title.get_width() // 2, 100))
    # Draw block grid like HTML version
    block_grid = [
        [CYAN, CYAN, CYAN, CYAN],
        [BLUE, BLUE, BLUE, ORANGE],
        [ORANGE, ORANGE, YELLOW, YELLOW],
        [GREEN, GREEN, PURPLE, RED]
    ]
    for y, row in enumerate(block_grid):
        for x, color in enumerate(row):
            draw_block(screen, WINDOW_WIDTH // 2 // BLOCK_SIZE - 2 + x, 200 // BLOCK_SIZE + y, color, BLOCK_SIZE)
    play_text = SMALL_FONT.render("Press SPACE to PLAY", True, WHITE)
    screen.blit(play_text, (WINDOW_WIDTH // 2 - play_text.get_width() // 2, 300))
    controls = [
        "Controls:",
        "← → : Move",
        "↑ : Rotate",
        "↓ : Soft Drop",
        "Space : Hard Drop",
        "P : Pause/Resume"
    ]
    for i, line in enumerate(controls):
        text = SMALL_FONT.render(line, True, GRAY)
        screen.blit(text, (WINDOW_WIDTH // 2 - text.get_width() // 2, 400 + i * 25))

def draw_game_over():
    overlay = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, 180))
    screen.blit(overlay, (0, 0))
    game_over_text = FONT.render("GAME OVER", True, RED)
    score_text = SMALL_FONT.render(f"Score: {score}", True, WHITE)
    restart_text = SMALL_FONT.render("Press R to Restart", True, WHITE)
    screen.blit(game_over_text, (WINDOW_WIDTH // 2 - game_over_text.get_width() // 2, 200))
    screen.blit(score_text, (WINDOW_WIDTH // 2 - score_text.get_width() // 2, 300))
    screen.blit(restart_text, (WINDOW_WIDTH // 2 - restart_text.get_width() // 2, 350))

def draw_hud():
    # Score and level box
    hud_surface = pygame.Surface((200, 200), pygame.SRCALPHA)
    hud_surface.fill((50, 50, 50, 200))
    pygame.draw.rect(hud_surface, GRAY, (0, 0, 200, 200), 2)
    score_text = SMALL_FONT.render(f"SCORE: {score}", True, WHITE)
    level_text = SMALL_FONT.render(f"LEVEL: {level}", True, WHITE)
    hud_surface.blit(score_text, (10, 10))
    hud_surface.blit(level_text, (10, 100))
    screen.blit(hud_surface, (BOARD_X + BOARD_WIDTH + 50, BOARD_Y + 200))
    # Next piece label
    next_text = SMALL_FONT.render("NEXT", True, WHITE)
    screen.blit(next_text, (BOARD_X + BOARD_WIDTH + 50, BOARD_Y + 30))

def update_particles():
    for particle in particles[:]:
        particle.update()
        particle.draw(screen)
        if particle.lifetime <= 0:
            particles.remove(particle)

def init_game():
    global board, score, level, game_over, is_paused, current_piece, next_piece, drop_time, particles
    board = create_board()
    score = 0
    level = 1
    game_over = False
    is_paused = False
    particles = []
    next_piece = get_random_piece()
    current_piece = get_random_piece()
    drop_time = pygame.time.get_ticks()

# Game loop
state = "start"
while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
        if event.type == pygame.KEYDOWN:
            if state == "start":
                if event.key == pygame.K_SPACE:
                    state = "game"
                    init_game()
            elif state == "game":
                if event.key == pygame.K_LEFT:
                    move_left()
                elif event.key == pygame.K_RIGHT:
                    move_right()
                elif event.key == pygame.K_DOWN:
                    move_down()
                elif event.key == pygame.K_UP:
                    rotate()
                elif event.key == pygame.K_SPACE:
                    hard_drop()
                elif event.key == pygame.K_p:
                    is_paused = not is_paused
                    if not is_paused:
                        drop_time = pygame.time.get_ticks()
                elif event.key == pygame.K_r and game_over:
                    init_game()
                    game_over = False

    if state == "start":
        draw_start_screen()
    elif state == "game":
        if not game_over and not is_paused:
            current_time = pygame.time.get_ticks()
            drop_interval = 1000 - (level * 50)
            if current_time - drop_time > drop_interval:
                if not move_down():
                    lock_piece()
                drop_time = current_time
        draw_board()
        draw_next_piece()
        draw_hud()
        update_particles()
        if game_over:
            draw_game_over()
        if is_paused:
            pause_text = FONT.render("PAUSED", True, YELLOW)
            screen.blit(pause_text, (WINDOW_WIDTH // 2 - pause_text.get_width() // 2, WINDOW_HEIGHT // 2))

    pygame.display.flip()
    clock.tick(60)