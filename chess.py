# Importing Modules
import pygame  # pip install pygame
import requests  # pip install requests
import random
from io import BytesIO

# Initialising pygame module
pygame.init()

# Setting Width and height of the Chess Game screen
WIDTH = 1000
HEIGHT = 900

screen = pygame.display.set_mode([WIDTH, HEIGHT])
pygame.display.set_caption('Chess Game')

font = pygame.font.Font('freesansbold.ttf', 20)
medium_font = pygame.font.Font('freesansbold.ttf', 30)
big_font = pygame.font.Font('freesansbold.ttf', 50)

timer = pygame.time.Clock()
fps = 60

# variables for block placement
block_action_pending = False
selecting_block = False
block_actor = None
block_selection_popup = False  # NEW: popup state

# game variables and images
white_pieces = ['rook', 'knight', 'bishop', 'king', 'queen', 'bishop', 'knight', 'rook',
                'pawn', 'pawn', 'pawn', 'pawn', 'pawn', 'pawn', 'pawn', 'pawn']
white_locations = [(0, 0), (1, 0), (2, 0), (3, 0), (4, 0), (5, 0), (6, 0), (7, 0),
                   (0, 1), (1, 1), (2, 1), (3, 1), (4, 1), (5, 1), (6, 1), (7, 1)]
black_pieces = ['rook', 'knight', 'bishop', 'king', 'queen', 'bishop', 'knight', 'rook',
                'pawn', 'pawn', 'pawn', 'pawn', 'pawn', 'pawn', 'pawn', 'pawn']
black_locations = [(0, 7), (1, 7), (2, 7), (3, 7), (4, 7), (5, 7), (6, 7), (7, 7),
                   (0, 6), (1, 6), (2, 6), (3, 6), (4, 6), (5, 6), (6, 6), (7, 6)]

captured_pieces_white = []
captured_pieces_black = []

turn_step = 0
selection = 100
valid_moves = []

# url for chess pieces images
image_urls = ['https://media.geeksforgeeks.org/wp-content/uploads/20240302025946/black_queen.png',
              'https://media.geeksforgeeks.org/wp-content/uploads/20240302025948/black_king.png',
              'https://media.geeksforgeeks.org/wp-content/uploads/20240302025345/black_rook.png',
              'https://media.geeksforgeeks.org/wp-content/uploads/20240302025951/black_bishop.png',
              'https://media.geeksforgeeks.org/wp-content/uploads/20240302025947/black_knight.png',
              'https://media.geeksforgeeks.org/wp-content/uploads/20240302025945/black_pawn.png',
              'https://media.geeksforgeeks.org/wp-content/uploads/20240302025952/white_queen.png',
              'https://media.geeksforgeeks.org/wp-content/uploads/20240302025943/white_king.png',
              'https://media.geeksforgeeks.org/wp-content/uploads/20240302025949/white_rook.png',
              'https://media.geeksforgeeks.org/wp-content/uploads/20240302025944/white_bishop.png',
              'https://media.geeksforgeeks.org/wp-content/uploads/20240302025325/white_knight.png',
              'https://media.geeksforgeeks.org/wp-content/uploads/20240302025953/white_pawn.png']

# load in game piece images
def load_image_from_url(url, size, small_size):
    response = requests.get(url)
    image = pygame.image.load(BytesIO(response.content))
    image = pygame.transform.scale(image, size)
    small_image = pygame.transform.scale(image, small_size)
    return image, small_image

# Black pieces
black_queen, black_queen_small = load_image_from_url(image_urls[0], (80, 80), (45, 45))
black_king, black_king_small   = load_image_from_url(image_urls[1], (80, 80), (45, 45))
black_rook, black_rook_small   = load_image_from_url(image_urls[2], (80, 80), (45, 45))
black_bishop, black_bishop_small = load_image_from_url(image_urls[3], (80, 80), (45, 45))
black_knight, black_knight_small = load_image_from_url(image_urls[4], (80, 80), (45, 45))
black_pawn, black_pawn_small   = load_image_from_url(image_urls[5], (65, 65), (45, 45))

# White pieces
white_queen, white_queen_small = load_image_from_url(image_urls[6], (80, 80), (45, 45))
white_king, white_king_small   = load_image_from_url(image_urls[7], (80, 80), (45, 45))
white_rook, white_rook_small   = load_image_from_url(image_urls[8], (80, 80), (45, 45))
white_bishop, white_bishop_small = load_image_from_url(image_urls[9], (80, 80), (45, 45))
white_knight, white_knight_small = load_image_from_url(image_urls[10], (80, 80), (45, 45))
white_pawn, white_pawn_small   = load_image_from_url(image_urls[11], (65, 65), (45, 45))

white_images = [white_pawn, white_queen, white_king,
                white_knight, white_rook, white_bishop]
small_white_images = [white_pawn_small, white_queen_small, white_king_small, white_knight_small,
                      white_rook_small, white_bishop_small]

black_images = [black_pawn, black_queen, black_king,
                black_knight, black_rook, black_bishop]
small_black_images = [black_pawn_small, black_queen_small, black_king_small,
                      black_knight_small, black_rook_small, black_bishop_small]

piece_list = ['pawn', 'queen', 'king', 'knight', 'rook', 'bishop']

blocks = set()

counter = 0
winner = ''
game_over = False

# -------- BLOCK FUNCTIONS --------
def generate_blocks(num_blocks=2):
    new_blocks = set()
    while len(new_blocks)//2 < num_blocks:
        x = random.randint(0, 7)
        y = random.randint(0, 7)
        if (x,y) in white_locations or (x,y) in black_locations:
            continue
        directions = [(0,1),(0,-1),(1,0),(-1,0)]
        dx, dy = random.choice(directions)
        nx, ny = x+dx, y+dy
        if 0 <= nx <= 7 and 0 <= ny <= 7:
            if (nx,ny) not in white_locations and (nx,ny) not in black_locations:
                new_blocks.add(((x,y),(nx,ny)))
                new_blocks.add(((nx,ny),(x,y)))
    return new_blocks

def draw_blocks():
    seen = set()
    for (a,b) in blocks:
        key = tuple(sorted([a,b]))
        if key in seen: continue
        seen.add(key)
        x1,y1=a; x2,y2=b
        if x1==x2:
            y_line=max(y1,y2)*100
            pygame.draw.line(screen,"red",(x1*100,y_line),(x1*100+100,y_line),6)
        elif y1==y2:
            x_line=max(x1,x2)*100
            pygame.draw.line(screen,"red",(x_line,y1*100),(x_line,y1*100+100),6)

# Popup overlay for block choice
def draw_block_popup():
    pygame.draw.rect(screen, "black", [150, 150, 700, 500])
    pygame.draw.rect(screen, "gold", [150, 150, 700, 500], 4)
    screen.blit(big_font.render("Captured a piece!", True, "white"), (200, 170))
    screen.blit(medium_font.render("Remove a block? (Press # or N to skip)", True, "white"), (200, 220))
    seen = set()
    idx = 1
    for (a, b) in blocks:
        key = tuple(sorted([a, b]))
        if key in seen: continue
        seen.add(key)
        text = f"{idx}. {a} - {b}"
        screen.blit(font.render(text, True, "white"), (200, 260 + idx*30))
        idx += 1

# -------- DRAW BOARD --------
def draw_board():
    for i in range(32):
        column = i % 4
        row = i // 4
        if row % 2 == 0:
            pygame.draw.rect(screen, 'light gray', [600 - (column * 200), row * 100, 100, 100])
        else:
            pygame.draw.rect(screen, 'light gray', [700 - (column * 200), row * 100, 100, 100])
        pygame.draw.rect(screen, 'gray', [0, 800, WIDTH, 100])
        pygame.draw.rect(screen, 'gold', [0, 800, WIDTH, 100], 5)
        pygame.draw.rect(screen, 'gold', [800, 0, 200, HEIGHT], 5)
        status_text = ['White: Select a Piece to Move!', 'White: Select a Destination!',
                       'Black: Select a Piece to Move!', 'Black: Select a Destination!']
        screen.blit(big_font.render(status_text[turn_step], True, 'black'), (20, 820))
        for i in range(9):
            pygame.draw.line(screen, 'black', (0, 100 * i), (800, 100 * i), 2)
            pygame.draw.line(screen, 'black', (100 * i, 0), (100 * i, 800), 2)
        screen.blit(medium_font.render('FORFEIT', True, 'black'), (810, 830))

    if block_selection_popup:
        draw_block_popup()

# draw pieces onto board
def draw_pieces():
    for i in range(len(white_pieces)):
        index = piece_list.index(white_pieces[i])
        if white_pieces[i] == 'pawn':
            screen.blit(
                white_pawn, (white_locations[i][0] * 100 + 22, white_locations[i][1] * 100 + 30))
        else:
            screen.blit(white_images[index], (white_locations[i]
                                              [0] * 100 + 10, white_locations[i][1] * 100 + 10))
        if turn_step < 2:
            if selection == i:
                pygame.draw.rect(screen, 'red', [white_locations[i][0] * 100 + 1, white_locations[i][1] * 100 + 1,
                                                 100, 100], 2)

    for i in range(len(black_pieces)):
        index = piece_list.index(black_pieces[i])
        if black_pieces[i] == 'pawn':
            screen.blit(
                black_pawn, (black_locations[i][0] * 100 + 22, black_locations[i][1] * 100 + 30))
        else:
            screen.blit(black_images[index], (black_locations[i]
                                              [0] * 100 + 10, black_locations[i][1] * 100 + 10))
        if turn_step >= 2:
            if selection == i:
                pygame.draw.rect(screen, 'blue', [black_locations[i][0] * 100 + 1, black_locations[i][1] * 100 + 1,
                                                  100, 100], 2)

# function to check if movement is blocked by a block
def is_blocked(a, b):
    """Return True if movement from cell a -> b is blocked."""
    return ((a, b) in blocks)


# function to check all pieces valid options on board
def check_options(pieces, locations, turn):
    moves_list = []
    all_moves_list = []
    for i in range((len(pieces))):
        location = locations[i]
        piece = pieces[i]
        if piece == 'pawn':
            moves_list = check_pawn(location, turn)
        elif piece == 'rook':
            moves_list = check_rook(location, turn)
        elif piece == 'knight':
            moves_list = check_knight(location, turn)
        elif piece == 'bishop':
            moves_list = check_bishop(location, turn)
        elif piece == 'queen':
            moves_list = check_queen(location, turn)
        elif piece == 'king':
            moves_list = check_king(location, turn)
        all_moves_list.append(moves_list)
    return all_moves_list


# check king valid moves
def check_king(position, color):
    moves_list = []
    friends_list = white_locations if color == 'white' else black_locations
    targets = [(1, 0), (1, 1), (1, -1), (-1, 0),
               (-1, 1), (-1, -1), (0, 1), (0, -1)]
    for dx, dy in targets:
        target = (position[0] + dx, position[1] + dy)
        if target not in friends_list and 0 <= target[0] <= 7 and 0 <= target[1] <= 7:
            if not is_blocked(position, target):
                moves_list.append(target)
    return moves_list


# check queen valid moves
def check_queen(position, color):
    return check_bishop(position, color) + check_rook(position, color)


# check bishop moves
def check_bishop(position, color):
    moves_list = []
    friends_list = white_locations if color == 'white' else black_locations
    enemies_list = black_locations if color == 'white' else white_locations

    directions = [(1,-1), (-1,-1), (1,1), (-1,1)]
    for dx, dy in directions:
        chain = 1
        path = True
        while path:
            next_cell = (position[0] + chain*dx, position[1] + chain*dy)
            if 0 <= next_cell[0] <= 7 and 0 <= next_cell[1] <= 7:
                if next_cell not in friends_list:
                    prev_cell = (position[0] + (chain-1)*dx, position[1] + (chain-1)*dy)

                    # Special diagonal blocking: check BOTH orthogonal edges
                    inter1 = (prev_cell[0] + dx, prev_cell[1])   # horizontal step
                    inter2 = (prev_cell[0], prev_cell[1] + dy)   # vertical step

                    if is_blocked(prev_cell, inter1) or is_blocked(inter1, next_cell) \
                       or is_blocked(prev_cell, inter2) or is_blocked(inter2, next_cell):
                        path = False
                        continue

                    moves_list.append(next_cell)
                    if next_cell in enemies_list:
                        path = False
                    chain += 1
                else:
                    path = False
            else:
                path = False
    return moves_list



# check rook moves
def check_rook(position, color):
    moves_list = []
    friends_list = white_locations if color == 'white' else black_locations
    enemies_list = black_locations if color == 'white' else white_locations

    directions = [(0,1), (0,-1), (1,0), (-1,0)]
    for dx, dy in directions:
        chain = 1
        path = True
        while path:
            next_cell = (position[0] + chain*dx, position[1] + chain*dy)
            if 0 <= next_cell[0] <= 7 and 0 <= next_cell[1] <= 7:
                if next_cell not in friends_list:
                    prev_cell = (position[0] + (chain-1)*dx, position[1] + (chain-1)*dy)
                    if is_blocked(prev_cell, next_cell):
                        path = False
                        continue

                    moves_list.append(next_cell)
                    if next_cell in enemies_list:
                        path = False
                    chain += 1
                else:
                    path = False
            else:
                path = False
    return moves_list


# check valid pawn moves
def check_pawn(position, color):
    moves_list = []
    if color == 'white':
        forward1 = (position[0], position[1] + 1)
        forward2 = (position[0], position[1] + 2)

        if position[1] < 7 and forward1 not in white_locations+black_locations:
            if not is_blocked(position, forward1):
                moves_list.append(forward1)

                if position[1] == 1 and forward2 not in white_locations+black_locations:
                    if not is_blocked(forward1, forward2):
                        moves_list.append(forward2)

        # captures
        for dx in [-1, 1]:
            target = (position[0]+dx, position[1]+1)
            if target in black_locations and not is_blocked(position, target):
                moves_list.append(target)

    else:  # black pawns
        forward1 = (position[0], position[1] - 1)
        forward2 = (position[0], position[1] - 2)

        if position[1] > 0 and forward1 not in white_locations+black_locations:
            if not is_blocked(position, forward1):
                moves_list.append(forward1)

                if position[1] == 6 and forward2 not in white_locations+black_locations:
                    if not is_blocked(forward1, forward2):
                        moves_list.append(forward2)

        # captures
        for dx in [-1, 1]:
            target = (position[0]+dx, position[1]-1)
            if target in white_locations and not is_blocked(position, target):
                moves_list.append(target)

    return moves_list


# check valid knight moves
def check_knight(position, color):
    moves_list = []
    friends_list = white_locations if color == 'white' else black_locations

    x, y = position
    knight_moves = [(1, 2), (1, -2), (2, 1), (2, -1),
                    (-1, 2), (-1, -2), (-2, 1), (-2, -1)]

    for dx, dy in knight_moves:
        tx, ty = x + dx, y + dy
        # must land on-board and not on a friend
        if not (0 <= tx <= 7 and 0 <= ty <= 7):
            continue
        if (tx, ty) in friends_list:
            continue

        blocked = False

        if abs(dy) == 2:
            # Long axis is vertical: check THREE horizontal edges
            # toward the side of dx (right if dx>0, left if dx<0)
            side_x = x + (1 if dx > 0 else -1)
            if not (0 <= side_x <= 7):
                blocked = True
            else:
                step_y = 1 if dy > 0 else -1
                for k in range(0, 3):  # y, y±1, y±2
                    a = (x, y + k * step_y)
                    b = (side_x, y + k * step_y)
                    if is_blocked(a, b):
                        blocked = True
                        break

        else:  # abs(dx) == 2
            # Long axis is horizontal: check THREE vertical edges
            # toward the side of dy (top if dy>0, bottom if dy<0)
            side_y = y + (1 if dy > 0 else -1)
            if not (0 <= side_y <= 7):
                blocked = True
            else:
                step_x = 1 if dx > 0 else -1
                for k in range(0, 3):  # x, x±1, x±2
                    a = (x + k * step_x, y)
                    b = (x + k * step_x, side_y)
                    if is_blocked(a, b):
                        blocked = True
                        break

        if not blocked:
            moves_list.append((tx, ty))

    return moves_list



# check for valid moves for just selected piece
def check_valid_moves():
    if turn_step < 2:
        options_list = white_options
    else:
        options_list = black_options
    valid_options = options_list[selection]
    return valid_options



# draw valid moves on screen
def draw_valid(moves):
    if turn_step < 2:
        color = 'red'
    else:
        color = 'blue'
    for i in range(len(moves)):
        pygame.draw.circle(
            screen, color, (moves[i][0] * 100 + 50, moves[i][1] * 100 + 50), 5)


# draw captured pieces on side of screen
def draw_captured():
    for i in range(len(captured_pieces_white)):
        captured_piece = captured_pieces_white[i]
        index = piece_list.index(captured_piece)
        screen.blit(small_black_images[index], (825, 5 + 50 * i))
    for i in range(len(captured_pieces_black)):
        captured_piece = captured_pieces_black[i]
        index = piece_list.index(captured_piece)
        screen.blit(small_white_images[index], (925, 5 + 50 * i))


# draw a flashing square around king if in check
def draw_check():
    if turn_step < 2:
        if 'king' in white_pieces:
            king_index = white_pieces.index('king')
            king_location = white_locations[king_index]
            for i in range(len(black_options)):
                if king_location in black_options[i]:
                    if counter < 15:
                        pygame.draw.rect(screen, 'dark red', [white_locations[king_index][0] * 100 + 1,
                                                              white_locations[king_index][1] * 100 + 1, 100, 100], 5)
    else:
        if 'king' in black_pieces:
            king_index = black_pieces.index('king')
            king_location = black_locations[king_index]
            for i in range(len(white_options)):
                if king_location in white_options[i]:
                    if counter < 15:
                        pygame.draw.rect(screen, 'dark blue', [black_locations[king_index][0] * 100 + 1,
                                                               black_locations[king_index][1] * 100 + 1, 100, 100], 5)


def draw_game_over():
    pygame.draw.rect(screen, 'black', [200, 200, 400, 70])
    screen.blit(font.render(
        f'{winner} won the game!', True, 'white'), (210, 210))
    screen.blit(font.render(f'Press ENTER to Restart!',
                            True, 'white'), (210, 240))
    



# main game loop
black_options = check_options(black_pieces, black_locations, 'black')
white_options = check_options(white_pieces, white_locations, 'white')
blocks = generate_blocks(3)

run = True
while run:
    timer.tick(fps)
    counter = (counter + 1) % 30

    # --- If popup is active, freeze board and only show popup ---
    if block_selection_popup:
        screen.fill('dark gray')
        draw_board()
        draw_blocks()
        draw_pieces()
        draw_captured()
        draw_check()
        draw_block_popup()
        pygame.display.flip()

        # Only handle popup keys / quit
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_n:
                    block_selection_popup = False
                elif pygame.K_1 <= event.key <= pygame.K_9:
                    choice = event.key - pygame.K_0
                    # build list of unique blocks
                    seen = []
                    for (a, b) in blocks:
                        key = tuple(sorted([a, b]))
                        if key not in seen:
                            seen.append(key)
                    if 1 <= choice <= len(seen):
                        (a, b) = seen[choice-1]
                        blocks.discard((a, b))
                        blocks.discard((b, a))
                        blocks.update(generate_blocks(1))
                    block_selection_popup = False
        continue  # skip normal gameplay loop until popup closes

    # --- Normal gameplay rendering ---
    screen.fill('dark gray')
    draw_board()
    draw_blocks()
    draw_pieces()
    draw_captured()
    draw_check()
    if selection != 100:
        valid_moves = check_valid_moves()
        draw_valid(valid_moves)

    # --- Normal event handling ---
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            run = False

        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1 and not game_over:
            x_coord = event.pos[0] // 100
            y_coord = event.pos[1] // 100
            click_coords = (x_coord, y_coord)

            if turn_step <= 1:
                if click_coords == (8, 8) or click_coords == (9, 8):
                    winner = 'black'
                if click_coords in white_locations:
                    selection = white_locations.index(click_coords)
                    if turn_step == 0:
                        turn_step = 1
                if click_coords in valid_moves and selection != 100:
                    white_locations[selection] = click_coords
                    if click_coords in black_locations:
                        black_piece = black_locations.index(click_coords)
                        captured_pieces_white.append(black_pieces[black_piece])
                        if black_pieces[black_piece] == 'king':
                            winner = 'white'
                        black_pieces.pop(black_piece)
                        black_locations.pop(black_piece)
                        # Trigger block popup after capture
                        block_selection_popup = True

                    black_options = check_options(black_pieces, black_locations, 'black')
                    white_options = check_options(white_pieces, white_locations, 'white')
                    turn_step = 2
                    selection = 100
                    valid_moves = []

            if turn_step > 1:
                if click_coords == (8, 8) or click_coords == (9, 8):
                    winner = 'white'
                if click_coords in black_locations:
                    selection = black_locations.index(click_coords)
                    if turn_step == 2:
                        turn_step = 3
                if click_coords in valid_moves and selection != 100:
                    black_locations[selection] = click_coords
                    if click_coords in white_locations:
                        white_piece = white_locations.index(click_coords)
                        captured_pieces_black.append(white_pieces[white_piece])
                        if white_pieces[white_piece] == 'king':
                            winner = 'black'
                        white_pieces.pop(white_piece)
                        white_locations.pop(white_piece)
                        # Trigger block popup after capture
                        block_selection_popup = True

                    black_options = check_options(black_pieces, black_locations, 'black')
                    white_options = check_options(white_pieces, white_locations, 'white')
                    turn_step = 0
                    selection = 100
                    valid_moves = []

        if event.type == pygame.KEYDOWN and game_over:
            if event.key == pygame.K_RETURN:
                game_over = False
                winner = ''
                white_pieces = ['rook', 'knight', 'bishop', 'king', 'queen', 'bishop', 'knight', 'rook',
                                'pawn', 'pawn', 'pawn', 'pawn', 'pawn', 'pawn', 'pawn', 'pawn']
                white_locations = [(0, 0), (1, 0), (2, 0), (3, 0), (4, 0), (5, 0), (6, 0), (7, 0),
                                   (0, 1), (1, 1), (2, 1), (3, 1), (4, 1), (5, 1), (6, 1), (7, 1)]
                black_pieces = ['rook', 'knight', 'bishop', 'king', 'queen', 'bishop', 'knight', 'rook',
                                'pawn', 'pawn', 'pawn', 'pawn', 'pawn', 'pawn', 'pawn', 'pawn']
                black_locations = [(0, 7), (1, 7), (2, 7), (3, 7), (4, 7), (5, 7), (6, 7), (7, 7),
                                   (0, 6), (1, 6), (2, 6), (3, 6), (4, 6), (5, 6), (6, 6), (7, 6)]
                captured_pieces_white = []
                captured_pieces_black = []
                turn_step = 0
                selection = 100
                valid_moves = []
                black_options = check_options(black_pieces, black_locations, 'black')
                white_options = check_options(white_pieces, white_locations, 'white')

    if winner != '':
        game_over = True
        draw_game_over()

    pygame.display.flip()


pygame.quit()