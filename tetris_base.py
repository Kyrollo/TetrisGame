import random, time, pygame, sys
from pygame.locals import *
random.seed(41)
##############################################################################
# SETTING UP GENERAL CONSTANTS
##############################################################################

# Board config
#FPS          = 25
FPS          = 90000000000
WINDOWWIDTH  = 650
WINDOWHEIGHT = 690
BOXSIZE      = 25
BOARDWIDTH   = 10
BOARDHEIGHT  = 25
BLANK        = '.'
XMARGIN      = int((WINDOWWIDTH - BOARDWIDTH * BOXSIZE) / 2)
TOPMARGIN    = WINDOWHEIGHT - (BOARDHEIGHT * BOXSIZE) - 5

# Timing config
# Every time the player pushes the left or right arrow key down, the falling
# piece should move one box over to the left or right, respectively. However,
# the player can also hold down the left or right arrow key to keep moving the
# falling piece. The MOVESIDEWAYSFREQ constant will set it so that every 0.15
# seconds that passes with the left or right arrow key held down, the piece
# will move another space over.
MOVESIDEWAYSFREQ = 0.15
MOVEDOWNFREQ     = 0.1

# Colors
#               R    G    B
WHITE       = (255, 255, 255)
GRAY        = (185, 185, 185)
BLACK       = (  0,   0,   0)
RED         = (155,   0,   0)
LIGHTRED    = (175,  20,  20)
GREEN       = (  0, 155,   0)
LIGHTGREEN  = ( 20, 175,  20)
BLUE        = (  0,   0, 155)
LIGHTBLUE   = ( 20,  20, 175)
YELLOW      = (155, 155,   0)
LIGHTYELLOW = (175, 175,  20)

BORDERCOLOR     = BLUE
BGCOLOR         = BLACK
TEXTCOLOR       = WHITE
TEXTSHADOWCOLOR = GRAY
COLORS          = (     BLUE,      GREEN,      RED,      YELLOW)
LIGHTCOLORS     = (LIGHTBLUE, LIGHTGREEN, LIGHTRED, LIGHTYELLOW)

# Each color must have light color
assert len(COLORS) == len(LIGHTCOLORS)

# Piece Templates
# The TEMPLATEWIDTH and TEMPLATEHEIGHT constants simply set how large each row
# and column for each shape’s rotation should be
TEMPLATEWIDTH  = 5
TEMPLATEHEIGHT = 5

S_SHAPE_TEMPLATE = [['.....',
                     '.....',
                     '..OO.',
                     '.OO..',
                     '.....'],
                    ['.....',
                     '..O..',
                     '..OO.',
                     '...O.',
                     '.....']]

Z_SHAPE_TEMPLATE = [['.....',
                     '.....',
                     '.OO..',
                     '..OO.',
                     '.....'],
                    ['.....',
                     '..O..',
                     '.OO..',
                     '.O...',
                     '.....']]

I_SHAPE_TEMPLATE = [['..O..',
                     '..O..',
                     '..O..',
                     '..O..',
                     '.....'],
                    ['.....',
                     '.....',
                     'OOOO.',
                     '.....',
                     '.....']]

O_SHAPE_TEMPLATE = [['.....',
                     '.....',
                     '.OO..',
                     '.OO..',
                     '.....']]

J_SHAPE_TEMPLATE = [['.....',
                     '.O...',
                     '.OOO.',
                     '.....',
                     '.....'],
                    ['.....',
                     '..OO.',
                     '..O..',
                     '..O..',
                     '.....'],
                    ['.....',
                     '.....',
                     '.OOO.',
                     '...O.',
                     '.....'],
                    ['.....',
                     '..O..',
                     '..O..',
                     '.OO..',
                     '.....']]

L_SHAPE_TEMPLATE = [['.....',
                     '...O.',
                     '.OOO.',
                     '.....',
                     '.....'],
                    ['.....',
                     '..O..',
                     '..O..',
                     '..OO.',
                     '.....'],
                    ['.....',
                     '.....',
                     '.OOO.',
                     '.O...',
                     '.....'],
                    ['.....',
                     '.OO..',
                     '..O..',
                     '..O..',
                     '.....']]

T_SHAPE_TEMPLATE = [['.....',
                     '..O..',
                     '.OOO.',
                     '.....',
                     '.....'],
                    ['.....',
                     '..O..',
                     '..OO.',
                     '..O..',
                     '.....'],
                    ['.....',
                     '.....',
                     '.OOO.',
                     '..O..',
                     '.....'],
                    ['.....',
                     '..O..',
                     '.OO..',
                     '..O..',
                     '.....']]

PIECES = {'S': S_SHAPE_TEMPLATE,
          'Z': Z_SHAPE_TEMPLATE,
          'J': J_SHAPE_TEMPLATE,
          'L': L_SHAPE_TEMPLATE,
          'I': I_SHAPE_TEMPLATE,
          'O': O_SHAPE_TEMPLATE,
          'T': T_SHAPE_TEMPLATE}

# Define if the game is manual or not
MANUAL_GAME = False

##############################################################################
# MAIN GAME
##############################################################################
def main():
    global FPSCLOCK, DISPLAYSURF, BASICFONT, BIGFONT

    pygame.init()
    falling_piece      = get_new_piece()
    next_piece         = get_new_piece()
    board = get_blank_board()
    FPSCLOCK    = pygame.time.Clock()
    DISPLAYSURF = pygame.display.set_mode((WINDOWWIDTH, WINDOWHEIGHT))
    BASICFONT   = pygame.font.Font('freesansbold.ttf', 18)
    BIGFONT     = pygame.font.Font('freesansbold.ttf', 100)
    pygame.display.set_caption('Tetris AI')
    population=[]
    for i in range(1000):
        print("game number:- ",i+1)
        if (MANUAL_GAME):
            run_game()
        if not MANUAL_GAME:
            population,score=AI_game(population)
            for j in range(1):
                print("it's score:- ",score)
                print("the factorials:- ",population[i])
                print("")

def evaluate_move(board_state, current_piece, next_piece, column, factors):
    # Calculate initial move information for the board
    total_holes_bef, total_blocking_bloks_bef = calc_initial_move_info(board_state)

    # Calculate information for the potential move
    move_info = calc_move_info(board_state, current_piece, column, current_piece['rotation'],
                               total_holes_bef, total_blocking_bloks_bef)

    # Check if the move is valid
    if not move_info[0]:
        return float('-inf')  # Invalid move has the lowest score

    # Extract move information
    max_height, num_removed_lines, new_holes, new_blocking_blocks, piece_sides, floor_sides, wall_sides = move_info[1:]

    # Calculate the rating using the provided factors
    rating = 0
    if factors is None:
        return 0.0
    for i in range(len(factors)):
        if i == 0:
            rating += factors[i] * max_height  # Factor for maximum height
        elif i == 1:
            rating += -factors[i] * num_removed_lines  # Factor for removed lines
        elif i == 2:
            rating += factors[i] * new_holes  # Factor for new holes
        elif i == 3:
            rating += factors[i] * new_blocking_blocks  # Factor for new blocking blocks
        elif i == 4:
            rating += factors[i] * piece_sides  # Factor for sides in contact with other pieces
        elif i == 5:
            rating += -factors[i] * floor_sides  # Factor for sides in contact with the floor
        elif i == 6:
            rating += -factors[i] * wall_sides  # Factor for sides in contact with walls
        # Add more factors as needed

    return rating

def simulate_action(board_state, piece_copy, action):
    # Create a copy of the piece to avoid modifying the original
    simulated_piece = piece_copy.copy()
    #print(action)
    # Create a copy of the board state to simulate the action
    simulated_board_state = [row[:] for row in board_state]

    # Apply the action to the simulated piece
    if action == 'left' and is_valid_position(simulated_board_state, simulated_piece, adj_X=-1):
        simulated_piece['x'] -= 1

    elif action == 'right' and is_valid_position(simulated_board_state, simulated_piece, adj_X=1):

        simulated_piece['x'] += 1
    elif action == 'rotate':
        # Rotate the piece
        simulated_piece['rotation'] = (simulated_piece['rotation'] + 1) % len(PIECES[simulated_piece['shape']])
        if not is_valid_position(simulated_board_state, simulated_piece):
            # Undo rotation if it results in an invalid position
            simulated_piece['rotation'] = (simulated_piece['rotation'] - 1) % len(PIECES[simulated_piece['shape']])
    elif action == 'down' and is_valid_position(simulated_board_state, simulated_piece, adj_Y=1):
        # Move the piece down
        simulated_piece['y'] += 1
    i=0
    #print(action)
    #print(simulated_piece)
    # Simulate letting the piece fall down until it can't move down anymore
    while is_valid_position(simulated_board_state, simulated_piece, adj_Y=1):
        simulated_piece['y'] += 1
        i+=1
        #print(i)

    # Add the simulated piece to the board if it can't move down anymore
    if action == 'down' and not is_valid_position(simulated_board_state, simulated_piece, adj_Y=1):
        add_to_board(simulated_board_state, simulated_piece)

    return simulated_board_state,simulated_piece

def good_action(board_state, piece_copy, next_piece, column, factors):
    best_action = None
    best_score = float('-inf')

    # Iterate over possible actions
    for action in ["left", "right", "rotate", "down"]:
        #print(action)
        # Simulate the action
        simulated_board_state,simulated_piece = simulate_action(board_state, piece_copy, action)

        # Calculate the score for the action
        #print(simulated_board_state)
        score = evaluate_move(simulated_board_state, simulated_piece, next_piece, simulated_piece['x'], factors)
        #print(score)
        if score > best_score:
            best_score = score
            best_action = action

    return best_action

def initialize_population(num_chromosomes, num_factors):
    population = []
    for _ in range(num_chromosomes):
        chromosome = [random.uniform(-100, 100) for _ in range(num_factors)]  # Initialize factors randomly between -1 and 1
        population.append(chromosome)
    return population

def select_best_chromosomes(population, board_state, current_piece, next_piece, column):
    scores = [evaluate_move(board_state, current_piece, next_piece, column, chromosome) for chromosome in population]
    sorted_population = [chromosome for _, chromosome in sorted(zip(scores, population), reverse=False)]
    return sorted_population[:int(len(population) / 2)]

def crossover(parent1, parent2):
    crossover_point = random.randint(1, len(parent1) - 1)
    child1 = parent1[:crossover_point] + parent2[crossover_point:]
    child2 = parent2[:crossover_point] + parent1[crossover_point:]
    return child1, child2

def mutate(chromosome, mutation_rate):
    mutated_chromosome = []
    for gene in chromosome:
        if random.random() < mutation_rate:
            mutated_gene = gene + random.uniform(-10, 10)   # Mutate gene with a small random value
            # Ensure the mutated gene stays within the desired range [-1, 1]
            mutated_gene = max(min(mutated_gene, 100), -100)
            mutated_chromosome.append(mutated_gene)
        else:
            mutated_chromosome.append(gene)
    return mutated_chromosome

def main_AI(num_iterations, board_state, current_piece, next_piece, column,population):
    num_chromosomes = 30
    num_factors = 7  # Number of factors to optimize
    mutation_rate = 0.1
    best_score = float('inf')
    best_factors = None
    if len(population)==0:
        population = initialize_population(num_chromosomes, num_factors)

    for _ in range(num_iterations):
        selected_population = select_best_chromosomes(population, board_state, current_piece, next_piece, column)

        new_generation = []
        for _ in range(num_chromosomes // 2):
            parent1, parent2 = random.choices(selected_population, k=2)
            child1, child2 = crossover(parent1, parent2)
            child1 = mutate(child1, mutation_rate)
            child2 = mutate(child2, mutation_rate)
            new_generation.extend([child1, child2])

        population = new_generation

        # Evaluate the best chromosome in the current generation
        max_score = max([evaluate_move(board_state, current_piece, next_piece, column, chromosome) for chromosome in population])
        if max_score < best_score:
            best_score = max_score
            best_factors = population[0]

    return best_factors, best_score,population

def minimize_horizontal_movement(board_state, current_piece, next_piece, factors):
    current_column = current_piece['x']
    best_column = current_column
    best_score = evaluate_move(board_state, current_piece, next_piece, current_column, factors)

    # Try moving left
    if current_column > 0:
        left_score = evaluate_move(board_state, current_piece, next_piece, current_column - 1, factors)
        if left_score >= best_score:
            best_column = current_column - 1
            best_score = left_score

    # Try moving right
    if current_column < len(board_state[0]) - len(current_piece['shape'][0]):
        right_score = evaluate_move(board_state, current_piece, next_piece, current_column + 1, factors)
        if right_score >= best_score:
            best_column = current_column + 1
            best_score = right_score

    # Try rotating
    rotated_piece = current_piece.copy()
    rotated_piece['rotation'] = (rotated_piece['rotation'] + 1) % len(PIECES[rotated_piece['shape']])
    rotation_score = evaluate_move(board_state, rotated_piece, next_piece, current_column, factors)
    if rotation_score >= best_score:
        # If rotation yields a better score, update the best column and score
        best_column = current_column
        best_score = rotation_score

    return best_column

# Assuming you have defined all necessary functions and variables like get_blank_board, calc_level_and_fall_freq, etc.
factorials = []

def AI_game(population):
    global DISPLAYSURF, FPSCLOCK

    # Setup variables
    board = get_blank_board()
    last_fall_time = time.time()
    score = 0
    level, fall_freq = calc_level_and_fall_freq(score)

    falling_piece = None  # Define falling_piece here
    next_piece = get_new_piece()
    factors = [1, 1, 1, 1,1]
    while True:
        # Game Loop
        if falling_piece is None:
            # No falling piece in play, so start a new piece at the top
            falling_piece = next_piece
            next_piece = get_new_piece()
            score += 1

            # Reset last_fall_time
            last_fall_time = time.time()

            if not is_valid_position(board, falling_piece):
                # GAME-OVER
                # Can't fit a new piece on the board, so game over.
                return population,score

        # Evaluate the move using the provided factors
        best_rating = float('-inf')
        best_action = None
        temp_piece = falling_piece.copy()  # Create a copy to avoid modifying the original piece
        #best_column = minimize_horizontal_movement(board, temp_piece, next_piece, factors)
        #temp_piece['x'] = best_column

        best_factors, rating,population = main_AI(10, board, temp_piece, next_piece, temp_piece["x"],population)
        best_action = good_action(board, temp_piece, next_piece, temp_piece["x"], best_factors)
        factorials.append(best_factors)
        factors=best_factors
        #print(factors)
        if best_action == "left" and is_valid_position(board, falling_piece, adj_X=-1):
            #print("left")
            falling_piece['x'] -= 1
        elif best_action == "right" and is_valid_position(board, falling_piece, adj_X=1):
            #print("right")
            falling_piece['x'] += 1
        elif best_action == "rotate":
            #print("a77a")
            falling_piece['rotation'] = (falling_piece['rotation'] + 1) % len(PIECES[falling_piece['shape']])
            if not is_valid_position(board, falling_piece):
                falling_piece['rotation'] = (falling_piece['rotation'] - 1) % len(PIECES[falling_piece['shape']])
        elif best_action == "down" and is_valid_position(board, falling_piece, adj_Y=1):
            #print("down")
            falling_piece['y'] += 1
        # Check for quit
        check_quit()

        # Let the piece fall if it is time to fall
        if time.time() - last_fall_time > fall_freq:
            # See if the piece has landed
            if not is_valid_position(board, falling_piece, adj_Y=1):
                # Falling piece has landed, set it on the board
                add_to_board(board, falling_piece)
                num_removed_lines = remove_complete_lines(board)

                # Bonus score for complete lines at once
                # 40   pts for 1 line
                # 120  pts for 2 lines
                # 300  pts for 3 lines
                # 1200 pts for 4 lines
                if num_removed_lines == 1:
                    score += 40
                elif num_removed_lines == 2:
                    score += 120
                elif num_removed_lines == 3:
                    score += 300
                elif num_removed_lines == 4:
                    score += 1200

                level, fall_freq = calc_level_and_fall_freq(score)
                falling_piece = None
            else:
                # Piece did not land, just move the piece down
                falling_piece['y'] += 1
                last_fall_time = time.time()

        # Drawing everything on the screen
        DISPLAYSURF.fill(BGCOLOR)
        draw_board(board)
        draw_status(score, level)
        draw_next_piece(next_piece)

        if falling_piece is not None:
            draw_piece(falling_piece)

        pygame.display.update()
        FPSCLOCK.tick(FPS)

def run_game():
    # Setup variables
    board              = get_blank_board()
    last_movedown_time = time.time()
    last_moveside_time = time.time()
    last_fall_time     = time.time()
    moving_down        = False # note: there is no movingUp variable
    moving_left        = False
    moving_right       = False
    score              = 0
    level, fall_freq   = calc_level_and_fall_freq(score)

    falling_piece      = get_new_piece()
    next_piece         = get_new_piece()

    while True:
        # Game Loop
        if (falling_piece == None):
            # No falling piece in play, so start a new piece at the top
            falling_piece = next_piece
            next_piece    = get_new_piece()
            score += 1

            # Reset last_fall_time
            last_fall_time = time.time()

            if (not is_valid_position(board, falling_piece)):
                # GAME-OVER
                # Can't fit a new piece on the board, so game over.
                return

        # Check for quit
        check_quit()

        for event in pygame.event.get():
            # Event handling loop
            if (event.type == KEYUP):
                if (event.key == K_p):
                    # PAUSE the game
                    DISPLAYSURF.fill(BGCOLOR)
                    # Pause until a key press
                    show_text_screen('Paused')

                    # Update times
                    last_fall_time     = time.time()
                    last_movedown_time = time.time()
                    last_moveside_time = time.time()

                elif (event.key == K_LEFT or event.key == K_a):
                    moving_left = False
                elif (event.key == K_RIGHT or event.key == K_d):
                    moving_right = False
                elif (event.key == K_DOWN or event.key == K_s):
                    moving_down = False

            elif event.type == KEYDOWN:
                # Moving the piece sideways
                if (event.key == K_LEFT or event.key == K_a) and \
                    is_valid_position(board, falling_piece, adj_X=-1):

                    falling_piece['x'] -= 1
                    moving_left         = True
                    moving_right        = False
                    last_moveside_time  = time.time()

                elif (event.key == K_RIGHT or event.key == K_d) and \
                    is_valid_position(board, falling_piece, adj_X=1):

                    falling_piece['x'] += 1
                    moving_right        = True
                    moving_left         = False
                    last_moveside_time  = time.time()

                # Rotating the piece (if there is room to rotate)
                elif (event.key == K_UP or event.key == K_w):
                    falling_piece['rotation'] = (falling_piece['rotation'] + 1) % len(PIECES[falling_piece['shape']])

                    if (not is_valid_position(board, falling_piece)):
                        falling_piece['rotation'] = (falling_piece['rotation'] - 1) % len(PIECES[falling_piece['shape']])

                elif (event.key == K_q):
                    falling_piece['rotation'] = (falling_piece['rotation'] - 1) % len(PIECES[falling_piece['shape']])

                    if (not is_valid_position(board, falling_piece)):
                        falling_piece['rotation'] = (falling_piece['rotation'] + 1) % len(PIECES[falling_piece['shape']])

                # Making the piece fall faster with the down key
                elif (event.key == K_DOWN or event.key == K_s):
                    moving_down = True

                    if (is_valid_position(board, falling_piece, adj_Y=1)):
                        falling_piece['y'] += 1

                    last_movedown_time = time.time()

                # Move the current piece all the way down
                elif event.key == K_SPACE:
                    moving_down  = False
                    moving_left  = False
                    moving_right = False

                    for i in range(1, BOARDHEIGHT):
                        if (not is_valid_position(board, falling_piece, adj_Y=i)):
                            break

                    falling_piece['y'] += i - 1

        # Handle moving the piece because of user input
        if (moving_left or moving_right) and time.time() - last_moveside_time > MOVESIDEWAYSFREQ:
            if moving_left and is_valid_position(board, falling_piece, adj_X=-1):
                falling_piece['x'] -= 1
            elif moving_right and is_valid_position(board, falling_piece, adj_X=1):
                falling_piece['x'] += 1

            last_moveside_time = time.time()

        if moving_down and time.time() - last_movedown_time > MOVEDOWNFREQ and is_valid_position(board, falling_piece, adj_Y=1):
            falling_piece['y'] += 1
            last_movedown_time = time.time()

        # Let the piece fall if it is time to fall
        if time.time() - last_fall_time > fall_freq:
            # See if the piece has landed
            if (not is_valid_position(board, falling_piece, adj_Y=1)):
                # Falling piece has landed, set it on the board
                add_to_board(board, falling_piece)
                num_removed_lines = remove_complete_lines(board)

                # Bonus score for complete lines at once
                # 40   pts for 1 line
                # 120  pts for 2 lines
                # 300  pts for 3 lines
                # 1200 pts for 4 lines

                if(num_removed_lines == 1):
                    score += 40
                elif (num_removed_lines == 2):
                    score += 120
                elif (num_removed_lines == 3):
                    score += 300
                elif (num_removed_lines == 4):
                    score += 1200

                level, fall_freq = calc_level_and_fall_freq(score)
                falling_piece    = None

            else:
                # Piece did not land, just move the piece down
                falling_piece['y'] += 1
                last_fall_time      = time.time()

        # Drawing everything on the screen
        DISPLAYSURF.fill(BGCOLOR)
        draw_board(board)
        draw_status(score, level)
        draw_next_piece(next_piece)

        if falling_piece != None:
            draw_piece(falling_piece)

        pygame.display.update()
        FPSCLOCK.tick(FPS)

##############################################################################
# GAME FUNCTIONS
##############################################################################

def make_text_objs(text, font, color):
    surf = font.render(text, True, color)

    return surf, surf.get_rect()


def terminate():
    """Terminate the game"""
    pygame.quit()
    sys.exit()


def check_key_press():
    # Go through event queue looking for a KEYUP event.
    # Grab KEYDOWN events to remove them from the event queue.
    check_quit()

    for event in pygame.event.get([KEYDOWN, KEYUP]):
        if event.type == KEYDOWN:
            continue
        return event.key
    return None


def show_text_screen(text):
    # This function displays large text in the
    # center of the screen until a key is pressed.

    # Draw the text drop shadow
    title_surf, title_rect = make_text_objs(text, BIGFONT, TEXTSHADOWCOLOR)
    title_rect.center      = (int(WINDOWWIDTH / 2), int(WINDOWHEIGHT / 2))
    DISPLAYSURF.blit(title_surf, title_rect)

    # Draw the text
    title_surf, title_rect = make_text_objs(text, BIGFONT, TEXTCOLOR)
    title_rect.center      = (int(WINDOWWIDTH / 2) - 3, int(WINDOWHEIGHT / 2) - 3)
    DISPLAYSURF.blit(title_surf, title_rect)

    # Draw the additional "Press a key to play." text.
    press_key_surf, press_key_rect = make_text_objs('Press a key to play.', BASICFONT, TEXTCOLOR)
    press_key_rect.center = (int(WINDOWWIDTH / 2), int(WINDOWHEIGHT / 2) + 100)
    DISPLAYSURF.blit(press_key_surf, press_key_rect)

    while check_key_press() == None:
        pygame.display.update()
        FPSCLOCK.tick()


def check_quit():
    for event in pygame.event.get(QUIT): # get all the QUIT events
        terminate() # terminate if any QUIT events are present

    for event in pygame.event.get(KEYUP): # get all the KEYUP events
        if event.key == K_ESCAPE:
            terminate() # terminate if the KEYUP event was for the Esc key
        pygame.event.post(event) # put the other KEYUP event objects back


def calc_level_and_fall_freq(score):
    """ Calculate level and fall frequency
        Based on the score, return the level the player is on and
        how many seconds pass until a falling piece falls one space.

    Args:
        score: game score

    """
    level     = int(score / 400) + 1
    fall_freq = 0.27 - (level * 0.02)

    if (not MANUAL_GAME):
        fall_freq = 0.00

    return level, fall_freq


def get_new_piece():
    """Return a random new piece in a random rotation and color"""

    shape     = random.choice(list(PIECES.keys()))
    new_piece = {'shape': shape,
                'rotation': random.randint(0, len(PIECES[shape]) - 1),
                'x': int(BOARDWIDTH / 2) - int(TEMPLATEWIDTH / 2),
                'y': -2, # start it above the board (i.e. less than 0)
                'color': random.randint(0, len(COLORS)-1)}

    return new_piece


def add_to_board(board, piece):
    """Fill in the board based on piece's location, shape, and rotation"""

    for x in range(TEMPLATEWIDTH):
        for y in range(TEMPLATEHEIGHT):
            if PIECES[piece['shape']][piece['rotation']][y][x] != BLANK:
                board[x + piece['x']][y + piece['y']] = piece['color']


def get_blank_board():
    """Create and return a new blank board data structure"""

    board = []
    for i in range(BOARDWIDTH):
        board.append([BLANK] * BOARDHEIGHT)

    return board


def is_on_board(x, y):
    """Check if the piece is on the board"""

    return x >= 0 and x < BOARDWIDTH and y < BOARDHEIGHT


def is_valid_position(board, piece, adj_X=0, adj_Y=0):
    """Return True if the piece is within the board and not colliding"""

    for x in range(TEMPLATEWIDTH):
        for y in range(TEMPLATEHEIGHT):
            is_above_board = y + piece['y'] + adj_Y < 0

            if is_above_board or PIECES[piece['shape']][piece['rotation']][y][x] == BLANK:
                continue

            if not is_on_board(x + piece['x'] + adj_X, y + piece['y'] + adj_Y):
                return False

            if board[x + piece['x'] + adj_X][y + piece['y'] + adj_Y] != BLANK:
                return False

    return True


def is_complete_line(board, y):
    """Return True if the line filled with boxes with no gaps"""

    for x in range(BOARDWIDTH):
        if board[x][y] == BLANK:
            return False

    return True


def remove_complete_lines(board):
    """Remove any completed lines on the board.

    After remove any completed lines, move everything above them dowm and
    return the number of complete lines.

    """
    num_removed_lines = 0
    y = BOARDHEIGHT - 1     # Start y at the bottom of the board

    while y >= 0:
        if is_complete_line(board, y):
            # Remove the line and pull boxes down by one line.
            for pullDownY in range(y, 0, -1):
                for x in range(BOARDWIDTH):
                    board[x][pullDownY] = board[x][pullDownY-1]

            # Set very top line to blank.
            for x in range(BOARDWIDTH):
                board[x][0] = BLANK

            num_removed_lines += 1

            # Note on the next iteration of the loop, y is the same.
            # This is so that if the line that was pulled down is also
            # complete, it will be removed.
        else:
            y -= 1  # Move on to check next row up

    return num_removed_lines


def conv_to_pixels_coords(boxx, boxy):
    """Convert the given xy coordinates to the screen coordinates

    Convert the given xy coordinates of the board to xy coordinates of the
    location on the screen.

    """
    return (XMARGIN + (boxx * BOXSIZE)), (TOPMARGIN + (boxy * BOXSIZE))


def draw_box(boxx, boxy, color, pixelx=None, pixely=None):
    """Draw box

    Draw a single box (each tetromino piece has four boxes) at xy coordinates
    on the board. Or, if pixelx and pixely are specified, draw to the pixel
    coordinates stored in pixelx and pixely (this is used for the "Next" piece).

    """
    if color == BLANK:
        return

    if pixelx == None and pixely == None:
        pixelx, pixely = conv_to_pixels_coords(boxx, boxy)

    pygame.draw.rect(DISPLAYSURF, COLORS[color], (pixelx + 1, pixely + 1, BOXSIZE - 1, BOXSIZE - 1))
    pygame.draw.rect(DISPLAYSURF, LIGHTCOLORS[color], (pixelx + 1, pixely + 1, BOXSIZE - 4, BOXSIZE - 4))


def draw_board(board):
    """Draw board"""

    # Draw the border around the board
    pygame.draw.rect(DISPLAYSURF, BORDERCOLOR, (XMARGIN - 3, TOPMARGIN - 7, (BOARDWIDTH * BOXSIZE) + 8, (BOARDHEIGHT * BOXSIZE) + 8), 5)

    # Fill the background of the board
    pygame.draw.rect(DISPLAYSURF, BGCOLOR, (XMARGIN, TOPMARGIN, BOXSIZE * BOARDWIDTH, BOXSIZE * BOARDHEIGHT))

    # Draw the individual boxes on the board
    for x in range(BOARDWIDTH):
        for y in range(BOARDHEIGHT):
            draw_box(x, y, board[x][y])


def draw_status(score, level):
    """Draw status"""

    # Draw the score text
    score_surf = BASICFONT.render('Score: %s' % score, True, TEXTCOLOR)
    score_rect = score_surf.get_rect()
    score_rect.topleft = (WINDOWWIDTH - 150, 80)
    DISPLAYSURF.blit(score_surf, score_rect)

    # draw the level text
    levelSurf = BASICFONT.render('Level: %s' % level, True, TEXTCOLOR)
    levelRect = levelSurf.get_rect()
    levelRect.topleft = (WINDOWWIDTH - 150, 110)
    DISPLAYSURF.blit(levelSurf, levelRect)


def draw_piece(piece, pixelx=None, pixely=None):
    """Draw piece"""

    shape_to_draw = PIECES[piece['shape']][piece['rotation']]

    if pixelx == None and pixely == None:
        # If pixelx and pixely hasn't been specified, use the location stored
        # in the piece data structure
        pixelx, pixely = conv_to_pixels_coords(piece['x'], piece['y'])

    # Draw each of the boxes that make up the piece
    for x in range(TEMPLATEWIDTH):
        for y in range(TEMPLATEHEIGHT):
            if shape_to_draw[y][x] != BLANK:
                draw_box(None, None, piece['color'], pixelx + (x * BOXSIZE), pixely + (y * BOXSIZE))


def draw_next_piece(piece):
    """Draw next piece"""

    # draw the "next" text
    next_surf = BASICFONT.render('Next:', True, TEXTCOLOR)
    next_rect = next_surf.get_rect()
    next_rect.topleft = (WINDOWWIDTH - 150, 160)
    DISPLAYSURF.blit(next_surf, next_rect)

    # draw the "next" piece
    draw_piece(piece, pixelx=WINDOWWIDTH-150, pixely=160)


##############################################################################
# GAME STATISTICS FUNCTIONS
##############################################################################

def calc_move_info(board, piece, x, r, total_holes_bef, total_blocking_bloks_bef):
    """Calculate informations based on the current play"""

    piece['rotation'] = r
    piece['y']        = 0
    piece['x']        = x

    # Check if it's a valid position
    if (not is_valid_position(board, piece)):
        return [False]

    # Goes down the piece while it's a valid position
    while is_valid_position(board, piece, adj_X=0, adj_Y=1):
        piece['y']+=1

    # Create a hypothetical board
    new_board = get_blank_board()
    for x2 in range(BOARDWIDTH):
        for y in range(BOARDHEIGHT):
            new_board[x2][y] = board[x2][y]

    # Add the piece to the new_board
    add_to_board(new_board, piece)

    # Calculate the sides in contact
    piece_sides, floor_sides, wall_sides = calc_sides_in_contact(board, piece)

    # Calculate removed lines
    num_removed_lines = remove_complete_lines(new_board)

    total_blocking_block = 0
    total_holes          = 0
    max_height           = 0

    for x2 in range(0, BOARDWIDTH):
        b = calc_heuristics(new_board, x2)
        total_holes += b[0]
        total_blocking_block += b[1]
        max_height += b[2]

    new_holes           = total_holes - total_holes_bef
    new_blocking_blocks = total_blocking_block - total_blocking_bloks_bef

    return [True, max_height, num_removed_lines, new_holes, new_blocking_blocks, piece_sides, floor_sides, wall_sides]

def calc_initial_move_info(board):
    total_holes          = 0
    total_blocking_bocks = 0

    for x2 in range(0, BOARDWIDTH):
        b = calc_heuristics(board, x2)

        total_holes          += b[0]
        total_blocking_bocks += b[1]

    return total_holes, total_blocking_bocks

def calc_heuristics(board, x):
    """Calculate heuristics

    The heuristics are composed by: number of holes, number of blocks above
    hole and maximum height.

    """
    total_holes        = 0
    locals_holes       = 0
    blocks_above_holes = 0
    is_hole_exist      = False
    sum_heights        = 0

    for y in range(BOARDHEIGHT-1, -1,-1):
        if board[x][y] == BLANK:
            locals_holes += 1
        else:
            sum_heights += BOARDHEIGHT-y

            if locals_holes > 0:
                total_holes += locals_holes
                locals_holes = 0

            if total_holes > 0:
                blocks_above_holes += 1

    return total_holes, blocks_above_holes, sum_heights

def calc_sides_in_contact(board, piece):
    """Calculate sides in contacts"""

    piece_sides = 0
    floor_sides = 0
    wall_sides  = 0

    for Px in range(TEMPLATEWIDTH):
        for Py in range(TEMPLATEHEIGHT):

            # Wall
            if not PIECES[piece['shape']][piece['rotation']][Py][Px] == BLANK: # Quadrante faz parte da peça
                if piece['x']+Px == 0 or piece['x']+Px == BOARDWIDTH-1:
                    wall_sides += 1

                if piece['y']+Py == BOARDHEIGHT-1:
                    floor_sides += 1
                else:
                # Para outras opecas no contorno do template:
                    if Py == TEMPLATEHEIGHT-1 and not board[piece['x']+Px][piece['y']+Py+1] == BLANK:
                        piece_sides += 1

                #os extremos do template sao colorido: confere se ha pecas do lado deles
                if Px == 0 and piece['x']+Px > 0 and not board[piece['x']+Px-1][piece['y']+Py] == BLANK:
                        piece_sides += 1

                if Px == TEMPLATEWIDTH-1 and piece['x']+Px < BOARDWIDTH -1 and not board[piece['x']+Px+1][piece['y']+Py] == BLANK:
                        piece_sides += 1

            # Other pieces in general
            elif piece['x']+Px < BOARDWIDTH and piece['x']+Px >= 0 and piece['y']+Py < BOARDHEIGHT and not board[piece['x']+Px][piece['y']+Py] == BLANK:  #quadrante do tabuleiro colorido mas nao do template

                # O quadrante vazio do template esta colorido no tabuleiro
                if not PIECES[piece['shape']][piece['rotation']][Py-1][Px] == BLANK:
                    piece_sides += 1

                if Px > 0 and not PIECES[piece['shape']][piece['rotation']][Py][Px-1] == BLANK:
                    piece_sides += 1

                if Px < TEMPLATEWIDTH-1 and not PIECES[piece['shape']][piece['rotation']][Py][Px+1] == BLANK:
                    piece_sides += 1

                    #(nao pode haver pecas em cima)

    return  piece_sides, floor_sides, wall_sides


main()
