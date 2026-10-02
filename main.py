import pygame
import random
import sys

pygame.init()

# ==================================================
# SCREEN (FIXED INITIALIZATION BUG)
# ==================================================
# সরাসরি (0,0) এবং FULLSCREEN দিলে পাইগেম নিজেই ডিভাইসের নেটিভ রেজোলিউশন নেয়
try:
    screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
    WIDTH, HEIGHT = screen.get_size()
except:
    WIDTH, HEIGHT = 600, 900
    screen = pygame.display.set_mode((WIDTH, HEIGHT))

pygame.display.set_caption("SHAHADAT RACING")

clock = pygame.time.Clock()
FPS = 60

# ==================================================
# COLORS
# ==================================================
GREEN = (35, 135, 55)
ROAD = (48, 48, 55)
WHITE = (255, 255, 255)
BLACK = (15, 15, 18)
RED = (225, 55, 55)
BLUE = (40, 105, 235)
YELLOW = (250, 205, 45)
ORANGE = (245, 125, 35)
PURPLE = (175, 65, 200)
CYAN = (50, 210, 220)
GRAY = (90, 90, 95)
DARK_GRAY = (35, 35, 40)

# ==================================================
# FONTS
# ==================================================
title_font = pygame.font.SysFont("Arial", 58, True)
big_font = pygame.font.SysFont("Arial", 52, True)
font = pygame.font.SysFont("Arial", 28, True)
small_font = pygame.font.SysFont("Arial", 22, True)
button_font = pygame.font.SysFont("Arial", 48, True)

# ==================================================
# ROAD
# ==================================================
ROAD_WIDTH = int(WIDTH * 0.7)
ROAD_LEFT = (WIDTH - ROAD_WIDTH) // 2
ROAD_RIGHT = ROAD_LEFT + ROAD_WIDTH

LANES = 4
LANE_WIDTH = ROAD_WIDTH // LANES

# ==================================================
# PLAYER
# ==================================================
CAR_WIDTH = 50
CAR_HEIGHT = 85

player = pygame.Rect(
    ROAD_LEFT + LANE_WIDTH * 2 + (LANE_WIDTH - CAR_WIDTH) // 2,
    HEIGHT - 300,
    CAR_WIDTH,
    CAR_HEIGHT
)

PLAYER_SPEED = 8

# ==================================================
# ENEMIES
# ==================================================
enemies = []
enemy_colors = [RED, BLUE, YELLOW, ORANGE, PURPLE]

# ==================================================
# GAME VARIABLES
# ==================================================
score = 0
best_score = 0
game_speed = 7.0
spawn_timer = 0
road_line_offset = 0

game_over = False
game_started = False
paused = False

left_pressed = False
right_pressed = False

# ==================================================
# BUTTONS
# ==================================================
BTN_WIDTH = int((WIDTH - 60) / 2)
BTN_HEIGHT = 110
BTN_Y = HEIGHT - 160

left_button = pygame.Rect(20, BTN_Y, BTN_WIDTH, BTN_HEIGHT)
right_button = pygame.Rect(WIDTH - BTN_WIDTH - 20, BTN_Y, BTN_WIDTH, BTN_HEIGHT)

start_button = pygame.Rect((WIDTH - 300) // 2, HEIGHT // 2, 300, 90)
restart_button = pygame.Rect((WIDTH - 300) // 2, HEIGHT // 2 + 100, 300, 90)
pause_button = pygame.Rect(WIDTH - 115, 50, 95, 50)

# ==================================================
# DRAW CAR
# ==================================================
def draw_car(rect, color):
    pygame.draw.rect(screen, color, rect, border_radius=10)
    pygame.draw.rect(screen, BLACK, (rect.x + 5, rect.bottom - 10, rect.width - 10, 8), border_radius=4)
    pygame.draw.rect(screen, (35, 70, 90), (rect.x + 8, rect.y + 10, rect.width - 16, 25), border_radius=5)
    pygame.draw.rect(screen, (30, 55, 70), (rect.x + 8, rect.y + 48, rect.width - 16, 20), border_radius=5)
    pygame.draw.rect(screen, WHITE, (rect.x + 5, rect.y + 5, 10, 7), border_radius=2)
    pygame.draw.rect(screen, WHITE, (rect.right - 15, rect.y + 5, 10, 7), border_radius=2)

    wheel_positions = [
        (rect.x - 5, rect.y + 15), (rect.right - 2, rect.y + 15),
        (rect.x - 5, rect.bottom - 37), (rect.right - 2, rect.bottom - 37)
    ]
    for wx, wy in wheel_positions:
        pygame.draw.rect(screen, BLACK, (wx, wy, 7, 22), border_radius=3)

# ==================================================
# SPAWN ENEMY (FIXED OVERLAP BUG)
# ==================================================
def spawn_enemy():
    available_lanes = []
    for lane in range(LANES):
        x = ROAD_LEFT + lane * LANE_WIDTH + (LANE_WIDTH - CAR_WIDTH) // 2
        # চেক করুন এই লেনের উপরের দিকে কোনো কার আছে কি না
        lane_clear = True
        for enemy in enemies:
            if abs(enemy["rect"].x - x) < 10 and enemy["rect"].y < 150:
                lane_clear = False
                break
        if lane_clear:
            available_lanes.append(lane)

    if not available_lanes:
        return # সব লেন ব্লক থাকলে স্পন করবেন না

    lane = random.choice(available_lanes)
    x = ROAD_LEFT + lane * LANE_WIDTH + (LANE_WIDTH - CAR_WIDTH) // 2
    y = -CAR_HEIGHT - random.randint(30, 180)

    enemy = {
        "rect": pygame.Rect(x, y, CAR_WIDTH, CAR_HEIGHT),
        "color": random.choice(enemy_colors)
    }
    enemies.append(enemy)

# ==================================================
# DRAW ROAD
# ==================================================
def draw_road():
    screen.fill(GREEN)
    pygame.draw.rect(screen, ROAD, (ROAD_LEFT, 0, ROAD_WIDTH, HEIGHT))
    pygame.draw.rect(screen, WHITE, (ROAD_LEFT, 0, 6, HEIGHT))
    pygame.draw.rect(screen, WHITE, (ROAD_RIGHT - 6, 0, 6, HEIGHT))

    dash_height = 45
    gap = 30
    distance = dash_height + gap

    for lane in range(1, LANES):
        x = ROAD_LEFT + lane * LANE_WIDTH
        y = -distance + (road_line_offset % distance)
        while y < HEIGHT:
            pygame.draw.rect(screen, WHITE, (x - 3, int(y), 6, dash_height))
            y += distance

# ==================================================
# UI DRAWING FUNCTIONS
# ==================================================
def draw_title():
    shadow = title_font.render("SHAHADAT RACING", True, BLACK)
    text = title_font.render("SHAHADAT RACING", True, CYAN)
    screen.blit(shadow, shadow.get_rect(center=(WIDTH // 2 + 3, 63)))
    screen.blit(text, text.get_rect(center=(WIDTH // 2, 60)))

def draw_buttons():
    pygame.draw.rect(screen, DARK_GRAY, left_button, border_radius=20)
    pygame.draw.rect(screen, GRAY, left_button, 3, border_radius=20)
    pygame.draw.rect(screen, DARK_GRAY, right_button, border_radius=20)
    pygame.draw.rect(screen, GRAY, right_button, 3, border_radius=20)

    left_text = button_font.render("◀", True, WHITE)
    right_text = button_font.render("▶", True, WHITE)
    screen.blit(left_text, left_text.get_rect(center=left_button.center))
    screen.blit(right_text, right_text.get_rect(center=right_button.center))

def draw_start_menu():
    screen.fill(DARK_GRAY)
    pygame.draw.rect(screen, ROAD, (WIDTH // 2 - 150, 0, 300, HEIGHT))
    for y in range(0, HEIGHT, 100):
        pygame.draw.rect(screen, WHITE, (WIDTH // 2 - 5, y, 10, 55))

    draw_title()
    subtitle = font.render("MOBILE CAR RACING", True, WHITE)
    screen.blit(subtitle, subtitle.get_rect(center=(WIDTH // 2, 150)))

    demo_car = pygame.Rect(WIDTH // 2 - 25, 230, 50, 85)
    draw_car(demo_car, BLUE)

    pygame.draw.rect(screen, BLUE, start_button, border_radius=20)
    start_text = font.render("START GAME", True, WHITE)
    screen.blit(start_text, start_text.get_rect(center=start_button.center))

    best_text = font.render(f"BEST SCORE: {best_score}", True, YELLOW)
    screen.blit(best_text, best_text.get_rect(center=(WIDTH // 2, HEIGHT // 2 + 150)))

    info = small_font.render("Use buttons or Arrow Keys", True, WHITE)
    screen.blit(info, info.get_rect(center=(WIDTH // 2, HEIGHT // 2 + 200)))

def draw_game_over():
    overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, 185))
    screen.blit(overlay, (0, 0))

    title = big_font.render("GAME OVER", True, RED)
    screen.blit(title, title.get_rect(center=(WIDTH // 2, HEIGHT // 2 - 100)))

    score_text = font.render(f"Score: {score}", True, WHITE)
    screen.blit(score_text, score_text.get_rect(center=(WIDTH // 2, HEIGHT // 2 - 30)))

    best_text = font.render(f"Best Score: {best_score}", True, YELLOW)
    screen.blit(best_text, best_text.get_rect(center=(WIDTH // 2, HEIGHT // 2 + 15)))

    pygame.draw.rect(screen, BLUE, restart_button, border_radius=20)
    restart_text = font.render("TAP TO RESTART", True, WHITE)
    screen.blit(restart_text, restart_text.get_rect(center=restart_button.center))

def draw_pause_button():
    pygame.draw.rect(screen, DARK_GRAY, pause_button, border_radius=12)
    pygame.draw.rect(screen, WHITE, pause_button, 2, border_radius=12)
    pause_text = small_font.render("II", True, WHITE)
    screen.blit(pause_text, pause_text.get_rect(center=pause_button.center))

def draw_pause_screen():
    overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, 150))
    screen.blit(overlay, (0, 0))

    pause_text = big_font.render("PAUSED", True, YELLOW)
    screen.blit(pause_text, pause_text.get_rect(center=(WIDTH // 2, HEIGHT // 2)))

    info = font.render("Tap II to continue", True, WHITE)
    screen.blit(info, info.get_rect(center=(WIDTH // 2, HEIGHT // 2 + 65)))

# ==================================================
# RESET GAME
# ==================================================
def reset_game():
    global score, game_speed, spawn_timer, road_line_offset
    global game_over, paused, left_pressed, right_pressed

    score = 0
    game_speed = 7.0
    spawn_timer = 0
    road_line_offset = 0
    game_over = False
    paused = False
    left_pressed = False
    right_pressed = False
    enemies.clear()

    player.x = ROAD_LEFT + LANE_WIDTH * 2 + (LANE_WIDTH - CAR_WIDTH) // 2
    player.y = HEIGHT - 400

# ==================================================
# MAIN LOOP
# ==================================================
running = True

while running:
    clock.tick(FPS)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        if event.type == pygame.MOUSEBUTTONDOWN:
            x, y = event.pos
            if not game_started:
                if start_button.collidepoint(x, y):
                    game_started = True
                    reset_game()
            elif game_over:
                if restart_button.collidepoint(x, y):
                    reset_game()
            else:
                if pause_button.collidepoint(x, y):
                    paused = not paused
                if not paused:
                    if left_button.collidepoint(x, y):
                        left_pressed = True
                    if right_button.collidepoint(x, y):
                        right_pressed = True

        if event.type == pygame.MOUSEBUTTONUP:
            left_pressed = False
            right_pressed = False

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_RETURN and not game_started:
                game_started = True
                reset_game()
            if event.key == pygame.K_r and game_over:
                reset_game()
            if event.key == pygame.K_p and game_started and not game_over:
                paused = not paused

    if game_started and not game_over and not paused:
        if left_pressed:
            player.x -= PLAYER_SPEED
        if right_pressed:
            player.x += PLAYER_SPEED

        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            player.x -= PLAYER_SPEED
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            player.x += PLAYER_SPEED

        # প্লেয়ারকে রাস্তার ভেতরে রাখা
        if player.left < ROAD_LEFT + 10:
            player.left = ROAD_LEFT + 10
        if player.right > ROAD_RIGHT - 10:
            player.right = ROAD_RIGHT - 10

        road_line_offset += game_speed
        spawn_timer += 1

        spawn_delay = max(25, int(65 - game_speed * 3))
        if spawn_timer >= spawn_delay:
            spawn_timer = 0
            spawn_enemy()

        for enemy in enemies[:]:
            # স্পিড ট্রাঙ্কেশন ফিক্স: round() ব্যবহার করা হয়েছে
            enemy["rect"].y += round(game_speed)

            if enemy["rect"].top > HEIGHT:
                enemies.remove(enemy)
                score += 1
                if score % 10 == 0:
                    game_speed += 0.7

            if player.colliderect(enemy["rect"].inflate(-8, -8)):
                game_over = True
                if score > best_score:
                    best_score = score

    # ==================================================
    # DRAW
    # ==================================================
    if not game_started:
        draw_start_menu()
    else:
        draw_road()
        for enemy in enemies:
            draw_car(enemy["rect"], enemy["color"])
        draw_car(player, BLUE)

        # HUD (উপরের লেখাগুলো)
        title_small = font.render("SHAHADAT RACING", True, CYAN)
        screen.blit(title_small, (20, 50))
        score_text = small_font.render(f"Score: {score}", True, WHITE)
        screen.blit(score_text, (20, 90))
        speed_text = small_font.render(f"Speed: {game_speed:.1f}", True, WHITE)
        screen.blit(speed_text, (20, 120))

        if not game_over:
            draw_pause_button()
        if not game_over and not paused:
            draw_buttons()
        if paused and not game_over:
            draw_pause_screen()
        if game_over:
            draw_game_over()

    pygame.display.update()

pygame.quit()
sys.exit()
