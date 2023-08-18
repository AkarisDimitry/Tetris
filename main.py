'''
Here's a general outline of what you need to do:

Initialize the game grid: This is typically a 10x20 grid, but it can be any size you want. Each cell in the grid can be empty or filled with a block.

Tetrominoes: There are seven different Tetris pieces, each made up of four squares. These are typically represented as 4x4 matrices.

Piece rotation: Implement the SRS rotation rules. When a player tries to rotate a piece, check the rotation matrix for that piece and apply it. If the rotation would cause the piece to overlap with another block or go out of bounds, you need to perform a wall kick.

Wall kicks: The SRS has specific rules for how pieces should move when they are rotated near walls or other blocks. These rules depend on the current orientation of the piece and the direction of rotation.

Collision detection: Check if a piece can move or rotate without overlapping with other blocks or going out of bounds.

Clearing lines: When a horizontal line of the grid is completely filled with blocks, remove that line and move all the lines above it down by one.

Game loop: Handle user input to move and rotate pieces, update the position of the falling piece, check for collisions, and clear lines.

Scoring: Assign points to the player based on the number of lines they clear.

Game Over: The game is over when a new piece cannot enter the playfield because the top row is blocked.

Display: Update the display to show the current state of the game grid, the score, and the next piece.

Controls: Implement controls for moving the piece left, right, down, rotating, and hard dropping.
'''

import numpy as np
import pygame
import random

# Initialize pygame
pygame.init()

# Set the window dimensions
window_width = 600
window_height = 900

# Create the window
window = pygame.display.set_mode((window_width, window_height))
pygame.display.set_caption("Tetris")

# Create a font
font = pygame.font.SysFont("Arial", 24)


# Define DAS variables
initial_delay = 100  # 500 milliseconds
auto_repeat_rate = 50

last_left_movement = 0
last_right_movement = 0
last_down_movement = 0

das_left_start_time = 0
das_right_start_time = 0
das_down_start_time = 0

das_left_active = False
das_right_active = False
das_down_active = False

# Define a dictionary to keep track of the statistics:
statistics = {
    "total_tetrominoes": 0,
    "tetromino_counts": {"I": 0, "O": 0, "T": 0, "S": 0, "Z": 0, "J": 0, "L": 0},
    "line_clears": {"single": 0, "double": 0, "triple": 0, "quadruple": 0}
}

# Define the colors
colors = {
    "cyan": (0, 255, 255),
    "yellow": (255, 255, 0),
    "purple": (128, 0, 128),
    "green": (0, 128, 0 ),
    "red": (255, 0, 0),
    "blue": (0, 0, 255),
    "orange": (255, 165, 0),
    "black": (0, 0, 0),
    "grey": (100, 100, 100),
    "white": (255, 255, 255)
}

# Define the colors
colors_list = [n for n in colors]

# Define the tetrominoes as 4x4 matrices
tetrominoes = {
    "I": {
        "shape": np.array([
            [0, 0, 0, 0],
            [1, 1, 1, 1],
            [0, 0, 0, 0],
            [0, 0, 0, 0]
        ]),
        "color": "cyan" , 'ID': 1
    },
    "O": {
        "shape": np.array([
            [0, 0, 0, 0],
            [0, 1, 1, 0],
            [0, 1, 1, 0],
            [0, 0, 0, 0]
        ]),
        "color": "yellow", 'ID': 2
    },
    "T": {
        "shape": np.array([
            [0, 0, 0, 0],
            [0, 1, 1, 1],
            [0, 0, 1, 0],
            [0, 0, 0, 0]
        ]),
        "color": "purple", 'ID': 3
    },
    "S": {
        "shape": np.array([
            [0, 0, 0, 0],
            [0, 0, 1, 1],
            [0, 1, 1, 0],
            [0, 0, 0, 0]
        ]),
        "color": "green", 'ID': 4
    },
    "Z": {
        "shape": np.array([
            [0, 0, 0, 0],
            [0, 1, 1, 0],
            [0, 0, 1, 1],
            [0, 0, 0, 0]
        ]),
        "color": "red", 'ID': 5
    },
    "J": {
        "shape": np.array([
            [0, 0, 0, 0],
            [0, 1, 1, 1],
            [0, 0, 0, 1],
            [0, 0, 0, 0]
        ]),
        "color": "blue", 'ID': 6
    },
    "L": {
	    "shape": np.array([
	        [0, 0, 0, 0],
	        [0, 1, 1, 1],
	        [0, 1, 0, 0],
	        [0, 0, 0, 0]
	    ]),
	    "color": "orange", 'ID': 7
}}

# Define the game grid as a 10x20 2D list
grid_width = 10
grid_height = 20
grid = np.zeros((grid_height, grid_width), dtype=int)

# Test 
tetrominoes, grid

def rotate_tetromino(tetromino, direction):
    # Transpose the tetromino
    rotated = np.transpose(tetromino)
    
    # Reverse each row for clockwise rotation, or reverse each column for counter-clockwise rotation
    if direction == "clockwise":
        rotated = np.array([row[::-1] for row in rotated])
    else:
        rotated = rotated[::-1]
    
    return rotated

# Test rotation function
tetromino = tetrominoes["T"]["shape"]
rotated_clockwise = rotate_tetromino(tetromino, "clockwise")
rotated_counter_clockwise = rotate_tetromino(tetromino, "counter-clockwise")

tetromino, rotated_clockwise, rotated_counter_clockwise

# Define the wall kick offsets for each tetromino and rotation direction
wall_kick_offsets = {
    "I": {
        "0->R": [(0, 0), (-2, 0), (1, 0), (-2, -1), (1, 2)],
        "R->0": [(0, 0), (2, 0), (-1, 0), (2, 1), (-1, -2)],
        "R->2": [(0, 0), (-1, 0), (2, 0), (-1, 2), (2, -1)],
        "2->R": [(0, 0), (1, 0), (-2, 0), (1, -2), (-2, 1)],
        "2->L": [(0, 0), (2, 0), (-1, 0), (2, 1), (-1, -2)],
        "L->2": [(0, 0), (-2, 0), (1, 0), (-2, -1), (1, 2)],
        "L->0": [(0, 0), (1, 0), (-2, 0), (1, -2), (-2, 1)],
        "0->L": [(0, 0), (-1, 0), (2, 0), (-1, 2), (2, -1)]
    },
    "others": {
        "0->R": [(0, 0), (-1, 0), (-1, 1), (0, -2), (-1, -2)],
        "R->0": [(0, 0), (1, 0), (1, -1), (0, 2), (1, 2)],
        "R->2": [(0, 0), (1, 0), (1, -1), (0, 2), (1, 2)],
        "2->R": [(0, 0), (-1, 0), (-1, 1), (0, -2), (-1, -2)],
        "2->L": [(0, 0), (-1, 0), (-1, 1), (0, -2), (-1, -2)],
        "L->2": [(0, 0), (1, 0), (1, -1), (0, 2), (1, 2)],
        "L->0": [(0, 0), (1, 0), (1, -1), (0, 2), (1, 2)],
        "0->L": [(0, 0), (-1, 0), (-1, 1), (0, -2), (-1, -2)]
    }
}

# Define a function to check for full lines and clear them
def clear_lines(grid):
    cleared_lines = 0
    for i in range(grid_height):
        if all(grid[i]):
            cleared_lines += 1
            for j in range(i, 0, -1):
                grid[j] = grid[j - 1]
            grid[0] = [0] * grid_width

    # Update statistics
    if cleared_lines == 1:
        statistics["line_clears"]["single"] += 1
    elif cleared_lines == 2:
        statistics["line_clears"]["double"] += 1
    elif cleared_lines == 3:
        statistics["line_clears"]["triple"] += 1
    elif cleared_lines == 4:
        statistics["line_clears"]["quadruple"] += 1

    return grid, cleared_lines

# Define a function to add the current tetromino to the game grid
def add_to_grid(tetromino, current_tetromino_key, grid, position):
    new_grid = grid.copy()
    for i in range(4):
        for j in range(4):
            if tetromino[i, j] == 1:
                new_grid[position[0] + i, position[1] + j] = tetrominoes[current_tetromino_key]['ID']
    return new_grid

def apply_wall_kick(tetromino, current_tetromino_key, direction, rotation_key, grid, position):
    offsets = wall_kick_offsets["I" if tetromino == "I" else "others"][rotation_key]
    for offset in offsets:
        new_position = (position[0] + offset[0], position[1] + offset[1])
        
        # Check if the new position is within the grid boundaries
        if 0 <= new_position[0] < grid_height and 0 <= new_position[1] < grid_width:
            # Check if the new position is valid
            if is_valid_position(tetromino, grid, new_position):
                return new_position
    return None

def is_valid_position(tetromino, grid, position):
    for i in range(4):
        for j in range(4):
            if tetromino[i, j] == 1:
                x = position[1] + j
                y = position[0] + i

                if x < 0 or x >= grid_width or y < 0 or y >= grid_height:
                    return False
                if y >= 0 and grid[y, x] != 0:
                    return False

    return True

def calculate_shadow_position(tetromino, grid, position):
    shadow_position = position
    while is_valid_position(tetromino, grid, (shadow_position[0] + 1, shadow_position[1])):
        shadow_position = (shadow_position[0] + 1, shadow_position[1])
    return shadow_position

def get_tetromino_from_bag(bag):
    if not bag:
        # Refill the bag with all seven tetrominoes
        bag.extend(['I', 'O', 'T', 'S', 'Z', 'J', 'L'])
    # Draw a random tetromino from the bag
    tetromino = random.choice(bag)
    bag.remove(tetromino)
    # Update statistics
    statistics["total_tetrominoes"] += 1
    statistics["tetromino_counts"][tetromino] += 1

    return tetromino

# function to lock the tetromino
def lock_tetromino(current_tetromino, current_tetromino_key, current_position, grid, bag):
    # Lock the tetromino in place
    grid = add_to_grid(current_tetromino, current_tetromino_key, grid, current_position)
    # Clear completed lines
    grid, cleared_lines = clear_lines(grid)
    score += cleared_lines
    # Get the next tetromino from the bag
    next_tetromino_key = get_tetromino_from_bag(bag)
    next_tetromino = tetrominoes[next_tetromino_key]
    current_position = (0, grid_width // 2 - 2)
    if not is_valid_position(next_tetromino["shape"], grid, current_position):
        return None  # Game over
    hold_used = False  # Reset the hold action tracking for the next turn
    return next_tetromino_key, next_tetromino, current_position

# Test apply_wall_kick function
apply_wall_kick(tetrominoes['T']["shape"], "T", "clockwise", "0->R", grid, (0, 0))

# Test is_valid_position function
is_valid_position(tetrominoes['T']["shape"], grid, (0, 0)), is_valid_position(tetrominoes['T']["shape"], grid, (0, -1))

# Define the next tetromino
next_tetromino_key = random.choice(list(tetrominoes.keys()))
next_tetromino = tetrominoes[next_tetromino_key]

# Initialize the score
score = 0

# Define the current tetromino and its position
current_tetromino_key = random.choice(list(tetrominoes.keys()))
current_tetromino = tetrominoes[current_tetromino_key]["shape"]
current_position = (0, grid_width // 2 - 2)

# Define hold system variables
hold_tetromino_key = None
hold_tetromino = None
hold_used = False

# Main game loop
running = True

# Define the fall delay in milliseconds
fall_delay = 500

# Initialize the last fall time
last_fall_time = pygame.time.get_ticks()

# Initialize the rotation state
rotation_state = "0"

# Initialize an empty bag
bag = []

# Define a variable to store the start time:
start_time = pygame.time.get_ticks()


while running:

    # Handle user input
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN:

            if event.key == pygame.K_SPACE:
                # Hard drop the tetromino
                while is_valid_position(current_tetromino, grid, (current_position[0] + 1, current_position[1])):
                    current_position = (current_position[0] + 1, current_position[1])
                # Lock the tetromino in place
                grid = add_to_grid(current_tetromino, current_tetromino_key, grid, current_position)
                # Clear completed lines
                grid, cleared_lines = clear_lines(grid)
                score += cleared_lines
                # Spawn a new tetromino
                current_tetromino_key = next_tetromino_key
                current_tetromino = next_tetromino["shape"]
                next_tetromino_key = get_tetromino_from_bag(bag)
                next_tetromino = tetrominoes[next_tetromino_key]
                current_position = (0, grid_width // 2 - 2)
                if not is_valid_position(current_tetromino, grid, current_position):
                    running = False  # Game over
                hold_used = False  # Reset the hold action tracking for the next turn

            elif event.key == pygame.K_LSHIFT or event.key == pygame.K_RSHIFT:
                # Handle the hold action
                if not hold_used:
                    if hold_tetromino_key is None:
                        hold_tetromino_key = current_tetromino_key
                        current_tetromino_key = next_tetromino_key
                        next_tetromino_key = get_tetromino_from_bag(bag)
                    else:
                        hold_tetromino_key, current_tetromino_key = current_tetromino_key, hold_tetromino_key
                    current_tetromino = tetrominoes[current_tetromino_key]["shape"]
                    current_position = (0, grid_width // 2 - 2)
                    hold_used = True
                        
            elif event.key == pygame.K_z or event.key == pygame.K_UP:
                # Rotate the tetromino counter-clockwise
                new_rotation_state = "L" if rotation_state == "0" else "2" if rotation_state == "R" else "R" if rotation_state == "2" else "0"
                rotation_key = f"{rotation_state}->{new_rotation_state}"
                rotated = rotate_tetromino(current_tetromino, "counter-clockwise")
                if is_valid_position(rotated, grid, current_position):
                    current_tetromino = rotated
                    rotation_state = new_rotation_state
                else:
                    new_position = apply_wall_kick(rotated, current_tetromino_key, "counter-clockwise", rotation_key, grid, current_position)
                    if new_position is not None:
                        current_position = new_position
                        current_tetromino = rotated
                        rotation_state = new_rotation_state
            elif event.key == pygame.K_x:
                # Rotate the tetromino clockwise
                new_rotation_state = "R" if rotation_state == "0" else "2" if rotation_state == "L" else "L" if rotation_state == "2" else "0"
                rotation_key = f"{rotation_state}->{new_rotation_state}"
                rotated = rotate_tetromino(current_tetromino, "clockwise")
                if is_valid_position(rotated, grid, current_position):
                    current_tetromino = rotated
                    rotation_state = new_rotation_state
                else:
                    new_position = apply_wall_kick(rotated, current_tetromino_key, "clockwise", rotation_key, grid, current_position)
                    if new_position is not None:
                        current_position = new_position
                        current_tetromino = rotated
                rotation_state = new_rotation_state
    
    # Check the state of the movement keys
    keys = pygame.key.get_pressed()
    current_time = pygame.time.get_ticks()

    # Handle DAS for the left movement
    if keys[pygame.K_LEFT]:
        if not das_left_active:
            new_position = (current_position[0], current_position[1] - 1)
            if is_valid_position(current_tetromino, grid, new_position):
                current_position = new_position
                das_left_active = True
                das_left_start_time = current_time
        elif current_time - das_left_start_time >= initial_delay and current_time - last_left_movement >= auto_repeat_rate:
            new_position = (current_position[0], current_position[1] - 1)
            if is_valid_position(current_tetromino, grid, new_position):
                current_position = new_position
                last_left_movement = current_time
    else:
        das_left_active = False

    # Handle DAS for the right movement
    if keys[pygame.K_RIGHT]:
        if not das_right_active:
            new_position = (current_position[0], current_position[1] + 1)
            if is_valid_position(current_tetromino, grid, new_position):
                current_position = new_position
                das_right_active = True
                das_right_start_time = current_time
        elif current_time - das_right_start_time >= initial_delay and current_time - last_right_movement >= auto_repeat_rate:
            new_position = (current_position[0], current_position[1] + 1)
            if is_valid_position(current_tetromino, grid, new_position):
                current_position = new_position
                last_right_movement = current_time
    else:
        das_right_active = False

    # Handle DAS for the down movement
    if keys[pygame.K_DOWN]:
        if not das_down_active:
            new_position = (current_position[0] + 1, current_position[1])
            if is_valid_position(current_tetromino, grid, new_position):
                current_position = new_position
                das_down_active = True
                das_down_start_time = current_time
        elif current_time - das_down_start_time >= initial_delay and current_time - last_down_movement >= auto_repeat_rate:
            new_position = (current_position[0] + 1, current_position[1])
            if is_valid_position(current_tetromino, grid, new_position):
                current_position = new_position
                last_down_movement = current_time
    else:
        das_down_active = False

    # Update the game state
    current_time = pygame.time.get_ticks()
    if current_time - last_fall_time >= fall_delay:
        new_position = (current_position[0] + 1, current_position[1])
        if is_valid_position(current_tetromino, grid, new_position):
            current_position = new_position
        else:
            grid = add_to_grid(current_tetromino, current_tetromino_key, grid, current_position)
            grid, cleared_lines = clear_lines(grid)
            score += cleared_lines
            current_tetromino_key = next_tetromino_key
            current_tetromino = next_tetromino["shape"]
            next_tetromino_key = get_tetromino_from_bag(bag)
            next_tetromino = tetrominoes[next_tetromino_key]
            current_position = (0, grid_width // 2 - 2)
            if not is_valid_position(current_tetromino, grid, current_position):
                running = False  # Game over
            hold_used = False  # Reset the hold action tracking for the next turn
        
        last_fall_time = current_time

    grid_side = 30
    # Draw the game grid
    window.fill(colors["black"])
    for i in range(grid_height):
        for j in range(grid_width):
            color = colors[colors_list[grid[i][j]-1]] if grid[i][j] != 0 else colors["black"]
            pygame.draw.rect(window, color, (j*grid_side, i*grid_side, grid_side-1, grid_side-1), 8)

    # Calculate the shadow position
    shadow_position = calculate_shadow_position(current_tetromino, grid, current_position)

    # Draw the shadow
    for i in range(4):
        for j in range(4):
            if current_tetromino[i, j] == 1:
                x = (shadow_position[1] + j) * grid_side
                y = (shadow_position[0] + i) * grid_side
                pygame.draw.rect(window, colors["grey"], (x, y, grid_side, grid_side))
                pygame.draw.rect(window, colors["white"], (x, y, grid_side, grid_side), 1)

    # Display the current tetromino
    for i in range(4):
        for j in range(4):
            if current_tetromino[i, j] == 1:
                color = colors[tetrominoes[current_tetromino_key]["color"]]
                pygame.draw.rect(window, color, ((current_position[1]+j)*grid_side, (current_position[0]+i)*grid_side, grid_side, grid_side))
                pygame.draw.rect(window, colors["white"], ((current_position[1] + j)*grid_side, (current_position[0] + i)*grid_side, grid_side, grid_side), 1)

    # Display the next tetromino
    window.fill(colors["black"], (window_width, 0, 120, 120))
    pygame.draw.rect(window, colors["white"], (window_width-grid_side*7, 0, grid_side*6, grid_side*5), 2)
    for i in range(4):
        for j in range(4):
            if next_tetromino["shape"][i, j] == 1:
                color = colors[next_tetromino["color"]]
                pygame.draw.rect(window, color, (window_width-grid_side*6+j*grid_side, i*grid_side, grid_side, grid_side))
                pygame.draw.rect(window, colors["white"], (window_width-grid_side*6+j*grid_side, i*grid_side, grid_side, grid_side), 1)


    # Display the hold tetromino
    window.fill(colors["black"], (window_width-grid_side*7, grid_side*7, grid_side*6, grid_side*6))
    pygame.draw.rect(window, colors["red"], (window_width-grid_side*7, grid_side*7, grid_side*6, grid_side*6), 2)
    if hold_tetromino_key is not None:
        hold_tetromino = tetrominoes[hold_tetromino_key]["shape"]
        for i in range(4):
            for j in range(4):
                if hold_tetromino[i, j] == 1:
                    color = colors[tetrominoes[hold_tetromino_key]["color"]]
                    pygame.draw.rect(window, color, (window_width-grid_side*6+ j*grid_side, grid_side*7+i*grid_side, grid_side, grid_side))
                    pygame.draw.rect(window, colors["white"], (window_width-grid_side*6+j*grid_side, grid_side*7+i*grid_side, grid_side, grid_side), 1)


    # Display the score
    score_text = f"Score: {score}"
    score_surface = font.render(score_text, True, colors["white"])
    window.blit(score_surface, (window_width-grid_side*7, window_height - grid_side))

    # Display the statistics
    stats_text = f"Total Tetrominoes: {statistics['total_tetrominoes']}"
    stats_surface = font.render(stats_text, True, colors["white"])
    window.blit(stats_surface, (10, window_height - 60))

    for i, (tetromino, count) in enumerate(statistics["tetromino_counts"].items()):
        tetromino_text = f"{tetromino}: {count}"
        tetromino_surface = font.render(tetromino_text, True, colors["white"])
        window.blit(tetromino_surface, (10, window_height - 90 - i * 30))

    for i, (line_clear, count) in enumerate(statistics["line_clears"].items()):
        line_clear_text = f"{line_clear.capitalize()}: {count}"
        line_clear_surface = font.render(line_clear_text, True, colors["white"])
        window.blit(line_clear_surface, (window_width - 150, window_height - 90 - i * 30))

    # Calculate and display the TPS:
    elapsed_time = (pygame.time.get_ticks() - start_time) / 1000

    if elapsed_time > 0:
        tps = statistics["total_tetrominoes"] / elapsed_time
    else:
        tps = 0
    tps_text = f"TPS: {tps:.2f}"
    tps_surface = font.render(tps_text, True, colors["white"])
    window.blit(tps_surface, (window_width - 150, 10))

    pygame.display.flip()

# Quit pygame
pygame.quit()