import sys
import pygame
import random
import math

# Loading high score from file
def load_high_score():
    try:
        with open('high_score.txt', 'r') as f:
            return int(f.read())
    except:
        return 0

# Initialize high_score
high_score = load_high_score()

# Initialize current_score
current_score = 0

# Initialize Pygame
pygame.init()

# Set up the display
WIDTH, HEIGHT = 690, 800
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Piggy Painter")
pygame.display.set_icon(pygame.image.load("pig_r.png"))
pygame.font.init()

# Colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
BLUE = (0, 0, 255)
ORANGE = (255, 165, 0)
YELLOW = (255, 255, 0)
PINK = (200, 160, 170)
BROWN = (139, 69, 19)
GREEN = (0, 255, 0)
PURPLE = (128, 0, 128)
CYAN = (0, 255, 255)
MAGENTA = (255, 0, 255)
GRAY = (128, 128, 128)
# make a list of all the colors above
colors = [BLUE, ORANGE, YELLOW, PINK, BROWN, GREEN, PURPLE, CYAN, MAGENTA, GRAY]

def get_random_color():
    return random.choice(colors)

random_color = get_random_color()

# UI settings
UI_HEIGHT = 50  # Space for UI elements at top

# Grid settings
GRID_SIZE = 16 # grid settings
PLAYABLE_HEIGHT = HEIGHT - UI_HEIGHT
CELL_SIZE = min(WIDTH // GRID_SIZE, PLAYABLE_HEIGHT // GRID_SIZE)

# At the top with other globals
round_number = 1

# Player settings
player_pos = [random.randint(0, GRID_SIZE - 1), random.randint(0, GRID_SIZE - 1)]
player_speed = 1

# Load images
player_img = pygame.image.load("pig_r.png")
enemy_img = pygame.image.load("farmer.png")
player_img = pygame.transform.scale(player_img, (CELL_SIZE, CELL_SIZE))
enemy_img = pygame.transform.scale(enemy_img, (CELL_SIZE, CELL_SIZE))

# Grid initialization
grid = [[0 for _ in range(GRID_SIZE)] for _ in range(GRID_SIZE)]

# custom font
title_font = pygame.font.Font("RubikWetPaint-Regular.ttf", 70)
small_font = pygame.font.Font("RubikWetPaint-Regular.ttf", 28)

# Game state variables
LEVEL_TEXT_DURATION = 40
ENEMY_MOVE_DELAY = 5
IMMUNITY_DURATION = 60
ROTATION_SPEED = 10  # colission degrees per frame
TOTAL_ROTATION = 720  # 360 * 2 degrees

# Game variables
show_level_text = False
level_text_timer = 0
immunity_timer = 0
music_playing = True
music_toggle_pressed = False
enemy_move_counter = 0
num_enemies = round_number
enemies = []
rotation_angle = 0 # starting rotation angle for collision animation
is_rotating = False # flag to indicate collision animation
round_number = 1
current_score = 0
high_score = load_high_score()
squeal_sound = "squeal.mp3"
title_music = "background1.mp3"
game_music = "background2.mp3"

def save_high_score(score):
    with open('high_score.txt', 'w') as f:
        f.write(str(score))

def update_scores():
    global current_score, high_score
    current_score += 1
    if current_score > high_score:
        high_score = current_score
        save_high_score(high_score)

def reset_current_score():
    global current_score, round_number
    current_score = 0
    round_number = 1

def play_game_music():
    global music_playing, music_toggle_pressed
    
    keys = pygame.key.get_pressed()
    if keys[pygame.K_m]:
        if not music_toggle_pressed:  # Only toggle once per key press
            music_playing = not music_playing
            if music_playing:
                pygame.mixer.music.unpause()
            else:
                pygame.mixer.music.pause()
        music_toggle_pressed = True
    else:
        music_toggle_pressed = False  # Reset when key is released

def draw_grid():
    for y in range(GRID_SIZE):
        for x in range(GRID_SIZE):
            rect = (x * CELL_SIZE, y * CELL_SIZE + UI_HEIGHT, CELL_SIZE, CELL_SIZE)
            if grid[y][x] == 1:
                pygame.draw.rect(screen, random_color, rect)  # Fill visited squares with color
            pygame.draw.rect(screen, WHITE, rect, 1)  # Draw grid lines

def move_player(dx, dy):
    global current_score
    new_x = player_pos[0] + dx
    new_y = player_pos[1] + dy
    
    # Ensure grid alignment
    new_x = max(0, min(new_x, GRID_SIZE - 1))
    new_y = max(0, min(new_y, GRID_SIZE - 1))
    
    if grid[new_y][new_x] == 0:  # Check if the block is not already filled
        current_score += 1  # Increment score for filling a new block
        update_scores()  # Update scores if necessary
    
    player_pos[0], player_pos[1] = new_x, new_y
    grid[new_y][new_x] = 1

def move_enemy(enemy):
    dx = player_pos[0] - enemy[0]
    dy = player_pos[1] - enemy[1]
    
    # Move in direction of larger difference
    if abs(dx) > abs(dy):
        enemy[0] += 1 if dx > 0 else -1
    else:
        enemy[1] += 1 if dy > 0 else -1
        
    # Ensure grid alignment
    enemy[0] = max(0, min(enemy[0], GRID_SIZE - 1))
    enemy[1] = max(0, min(enemy[1], GRID_SIZE - 1))

def init_enemies():
    for _ in range(num_enemies):
        x = random.randint(0, GRID_SIZE - 1)
        y = random.randint(0, GRID_SIZE - 1)
        enemies.append([x, y])

def move_enemies():
    global enemy_move_counter
    
    enemy_move_counter += 1
    if enemy_move_counter < ENEMY_MOVE_DELAY:
        return
        
    enemy_move_counter = 0
    
    for enemy in enemies:
        # Get direction towards player
        dx = player_pos[0] - enemy[0]
        dy = player_pos[1] - enemy[1]
        
        # Calculate base randomization for current level group
        base_random = 0.3  # 30% base random movement
        level_group = (round_number - 1) // 3  # Group levels in sets of 3
        level_in_group = (round_number - 1) % 3  # Position within group (0,1,2)
        random_chance = min(0.9, base_random + (level_in_group * 0.1))  # Increases by 10% each level, max 90%
        
        # Use calculated random chance for movement decision
        if random.random() < random_chance:
            # Move in direction of larger difference
            if abs(dx) > abs(dy):
                enemy[0] += 1 if dx > 0 else -1
            else:
                enemy[1] += 1 if dy > 0 else -1
        else:
            # Random movement
            enemy[0] += random.choice([-1, 0, 1])
            enemy[1] += random.choice([-1, 0, 1])
            
        # Keep within bounds
        enemy[0] = max(0, min(enemy[0], GRID_SIZE - 1))
        enemy[1] = max(0, min(enemy[1], GRID_SIZE - 1))

def handle_collision():
    global is_rotating, rotation_angle
    is_rotating = True
    rotation_angle = 0
    pygame.mixer.music.load(squeal_sound)
    pygame.mixer.music.play()

def check_collision():
    for enemy in enemies:
        if (player_pos[0] == enemy[0] and 
            player_pos[1] == enemy[1] and 
            not is_rotating):  # Only detect collision when not already rotating
            handle_collision()
            return True
    return False

def is_level_complete(grid):
    # Check if all cells are filled with boxes
    for row in grid:
        for cell in row:
            if cell == 0:  # 0 represents empty cell
                return False
    return True

def reset_level(grid, enemies):
    global round_number, show_level_text, level_text_timer, random_color, immunity_timer
    
    immunity_timer = IMMUNITY_DURATION
    # Clear the grid
    for i in range(len(grid)):
        for j in range(len(grid[i])):
            grid[i][j] = 0
    
    random_color = get_random_color()
    round_number += 1
    
    # Reset positions safely
    player_pos[0] = random.randint(0, GRID_SIZE - 1)
    player_pos[1] = random.randint(0, GRID_SIZE - 1)
    
    new_enemy_pos = [random.randint(0, GRID_SIZE - 1), random.randint(0, GRID_SIZE - 1)]
    while abs(new_enemy_pos[0] - player_pos[0]) < 3 or abs(new_enemy_pos[1] - player_pos[1]) < 3:
        new_enemy_pos = [random.randint(0, GRID_SIZE - 1), random.randint(0, GRID_SIZE - 1)]
    enemies.append(new_enemy_pos)
    
    show_level_text = True
    level_text_timer = 0

def game_over():
    font = pygame.font.Font(None, 74)
    pygame.mixer.music.stop()
    game_over_text = title_font.render("GAME OVER!", True, MAGENTA)
    play_again_text = small_font.render("Play Again? (Y/N)", True, BROWN)
    screen.blit(game_over_text, (WIDTH // 2 - game_over_text.get_width() // 2, HEIGHT // 2 - 100))
    screen.blit(play_again_text, (WIDTH // 2 - play_again_text.get_width() // 2, HEIGHT // 2 + 50))
    pygame.display.flip()
    
    waiting_for_input = True
    while waiting_for_input:
        for event in pygame.event.get():
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_y:
                    # Reset game state
                    pygame.mixer.music.load("background2.mp3")
                    pygame.mixer.music.play(-1)
                    player_pos[:] = [GRID_SIZE // 2, GRID_SIZE // 2]
                    enemies.clear()
                    current_score = 0
                    init_enemies()
                    grid[:] = [[0 for _ in range(GRID_SIZE)] for _ in range(GRID_SIZE)]
                    grid[player_pos[1]][player_pos[0]] = 1
                    waiting_for_input = False
                elif event.key == pygame.K_n:
                    pygame.quit()
                    sys.exit()

def draw_scores():
    score_text = small_font.render(f'Score: {current_score}', True, ORANGE)
    high_score_text = small_font.render(f'High Score: {high_score}', True, ORANGE)
    level_text = small_font.render(f'Level: {round_number}', True, GREEN)
    high_score_width = high_score_text.get_width() / 2 # Get the half width position of the high score text
    level_text_width = level_text.get_width() # Get the width of the level text
    screen.blit(score_text, (10, 10)) # Left position of the score text
    screen.blit(high_score_text, ((WIDTH / 2)-high_score_width, 10)) # Center the high score text
    screen.blit(level_text, (WIDTH - (level_text_width+40), 10)) # Right position of the level text

def show_level_message():
    global show_level_text, level_text_timer
    if show_level_text:
        text = title_font.render(f"Level {round_number}", True, YELLOW)
        text_rect = text.get_rect(center=(WIDTH/2, HEIGHT/2))
        # Fade out effect
        alpha = min(255, (LEVEL_TEXT_DURATION - level_text_timer) * 4)
        text.set_alpha(alpha)
        screen.blit(text, text_rect)
        level_text_timer += 1
        if level_text_timer >= LEVEL_TEXT_DURATION:
            show_level_text = False
            level_text_timer = 0

def draw_player():
    global is_rotating, rotation_angle
    
    if is_rotating:
        rotation_angle += ROTATION_SPEED
        if rotation_angle >= TOTAL_ROTATION:
            is_rotating = False
            rotation_angle = 0
            game_over()  # Call game over after rotation completes
        rotated_img = pygame.transform.rotate(player_img, rotation_angle)
    else:
        rotated_img = player_img
        
    rect = rotated_img.get_rect(center=(
        player_pos[0] * CELL_SIZE + CELL_SIZE//2,
        player_pos[1] * CELL_SIZE + UI_HEIGHT + CELL_SIZE//2
    ))
    screen.blit(rotated_img, rect)

def draw_enemies():
    enemy_surface = enemy_img.copy()
    enemy_surface.set_alpha(255 if immunity_timer == 0 else 
                          int((IMMUNITY_DURATION - immunity_timer) * (255 / IMMUNITY_DURATION)))
    
    for enemy in enemies:
        screen.blit(enemy_surface,
                   (enemy[0] * CELL_SIZE,
                    enemy[1] * CELL_SIZE + UI_HEIGHT))

def get_rainbow_color(offset=0):
    # Use time and sine waves to create smooth color transitions
    t = pygame.time.get_ticks() / 1000  # Convert to seconds
    
    # Calculate RGB values using offset sine waves
    r = (math.sin(t + offset) * 127 + 128)
    g = (math.sin(t + offset + 2) * 127 + 128)
    b = (math.sin(t + offset + 4) * 127 + 128)
    
    return (int(r), int(g), int(b))

def get_jiggle_offset(speed=5, amplitude=8, letter_index=0):
    t = pygame.time.get_ticks() / 1000
    x_offset = math.sin((t * speed) + letter_index) * amplitude
    y_offset = math.cos((t * speed * 1.5) + letter_index) * amplitude
    return x_offset, y_offset

def show_splash_screen():
    waiting = True
    clock = pygame.time.Clock()
    title = "Piggy Painter"
    pygame.mixer.init()
    pygame.mixer.music.load(title_music)  # Load initial music
    pygame.mixer.music.play(-1)  # Play indefinitely 
    
    while waiting:
        clock.tick(60)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.KEYDOWN:
                pygame.event.clear()  # Clear any pending events
                pygame.mixer.music.stop() # Stop music once the key is pressed
                return  # Exit splash screen immediately
        screen.fill(BLACK)
        
        # Images
        splash_size = HEIGHT // 5
        splash_pig = pygame.transform.scale(player_img, (splash_size, splash_size))
        splash_enemy = pygame.transform.scale(enemy_img, (splash_size, splash_size))
        screen.blit(splash_pig, (WIDTH//4 - splash_size//2, HEIGHT//2 - splash_size//2))
        screen.blit(splash_enemy, (3*WIDTH//4 - splash_size//2, HEIGHT//2 - splash_size//2))
        
        # Title letters
        letter_widths = [title_font.render(letter, True, WHITE).get_width() for letter in title]
        total_width = sum(letter_widths) + (len(title) - 1) * 5
        start_x = (WIDTH - total_width) // 2
        
        x = start_x
        for i, letter in enumerate(title):
            color = get_rainbow_color(i * 0.5)
            x_off, y_off = get_jiggle_offset(letter_index=i*0.5)
            letter_surface = title_font.render(letter, True, color)
            screen.blit(letter_surface, (x + x_off, HEIGHT//4 + y_off))
            x += letter_surface.get_width() + 5

        press_text = small_font.render("Press any key to start", True, get_rainbow_color(2))
        press_rect = press_text.get_rect(center=(WIDTH//2, HEIGHT*3//4))
        screen.blit(press_text, press_rect)
        
        pygame.display.flip()

show_splash_screen()
pygame.event.clear()  # Clear any pending events after splash screen

def is_grid_complete():
    """Check if all grid cells are filled"""
    for row in grid:
        for cell in row:
            if cell == 0:
                return False
    return True

def reset_level():
    global round_number, show_level_text, level_text_timer, random_color, immunity_timer
    
    immunity_timer = IMMUNITY_DURATION
    # Clear the grid
    for i in range(len(grid)):
        for j in range(len(grid[i])):
            grid[i][j] = 0
    
    random_color = get_random_color()
    round_number += 1
    
    # Reset positions safely
    player_pos[0] = random.randint(0, GRID_SIZE - 1)
    player_pos[1] = random.randint(0, GRID_SIZE - 1)
    
    new_enemy_pos = [random.randint(0, GRID_SIZE - 1), random.randint(0, GRID_SIZE - 1)]
    while abs(new_enemy_pos[0] - player_pos[0]) < 3 or abs(new_enemy_pos[1] - player_pos[1]) < 3:
        new_enemy_pos = [random.randint(0, GRID_SIZE - 1), random.randint(0, GRID_SIZE - 1)]
    enemies.append(new_enemy_pos)
    
    show_level_text = True
    level_text_timer = 0

def update_game_state():
    global show_level_text, level_text_timer
    # Check for level completion
    if is_grid_complete():
        show_level_text = True
        level_text_timer = LEVEL_TEXT_DURATION
        reset_level()
        update_scores()

def main():
    clock = pygame.time.Clock()
    init_enemies()
    running = True
    high_score = load_high_score()
    pygame.mixer.music.load("background2.mp3")
    pygame.mixer.music.play(-1)  # Play indefinitely

    global immunity_timer, current_score
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT] or keys[pygame.K_o] or keys[pygame.K_a]:
            move_player(-player_speed, 0)
        if keys[pygame.K_RIGHT] or keys[pygame.K_p] or keys[pygame.K_d]:
            move_player(player_speed, 0)
        if keys[pygame.K_UP] or keys[pygame.K_q] or keys[pygame.K_w]:
            move_player(0, -player_speed)
        if keys[pygame.K_DOWN] or keys[pygame.K_z] or keys[pygame.K_s]:
            move_player(0, player_speed)
        if keys[pygame.K_ESCAPE]:
            running = False # Quit game
            
        move_enemies()

        if check_collision():
            if not is_rotating:  # Start rotation
                handle_collision()
        elif is_rotating:  # Check if rotation is done
            draw_player()  # Ensure player is drawn with rotation
        else:
            # Normal game drawing
            draw_player()
            draw_enemies()
            draw_grid()
            draw_scores()

        if is_level_complete(grid):
            reset_level()

        screen.fill(BLACK)
        draw_grid()
        draw_player()
        draw_enemies()
        play_game_music()
        draw_scores()
        show_level_message()

        # In main game loop
        if immunity_timer > 0:
            immunity_timer -= 1

        # Add this call in your main game loop
        update_game_state()

        pygame.display.flip()
        clock.tick(10)  # 10 FPS for a retro feel

    pygame.quit()

if __name__ == "__main__":
    main()
