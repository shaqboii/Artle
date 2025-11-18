import pygame
import random
import math
import sys
import os

def resource_path(relative_path):
    """ Get absolute path to resource, works for dev and for PyInstaller """
    if hasattr(sys, '_MEIPASS'):
        return os.path.join(sys._MEIPASS, relative_path)
    return os.path.join(os.path.abspath("."), relative_path)

word_bank_path = resource_path("wordleWords.txt")
font_path = resource_path("SF-Pro-Display-Black.otf")

# --- Load Word Bank ---
with open("wordleWords.txt", "r", encoding="utf-8") as f:
    WORDS = [w.strip().lower() for w in f.readlines() if len(w.strip()) == 5]
WORD_SET = set(WORDS)

# --- Game Logic ---
def get_feedback(guess, solution):
    result = ["grey"] * 5
    solution_chars = list(solution)
    for i in range(5):
        if guess[i] == solution[i]:
            result[i] = "green"
            solution_chars[i] = None
    for i in range(5):
        if result[i] == "grey" and guess[i] in solution_chars:
            result[i] = "yellow"
            solution_chars[solution_chars.index(guess[i])] = None
    return result

def generate_target_art(word_list):
    solution = random.choice(word_list)
    guesses = random.sample(word_list, 6)
    art = [get_feedback(guess, solution) for guess in guesses]
    return {"solution": solution, "art": art, "guesses": guesses}

# --- Pygame Setup ---
pygame.init()
screen = pygame.display.set_mode((1920, 1080))
#emojis = pygame_emojis.emojis(screen)
pygame.display.set_caption("Wordle Art GUI")
clock = pygame.time.Clock()
font = pygame.font.Font("SF-Pro-Display-Black.otf", 32)
big_font = pygame.font.Font("SF-Pro-Display-Black.otf", 48)
label_font = pygame.font.Font("SF-Pro-Display-Black.otf", 28)

# --- Colors ---
COLOR_MAP = {
    "green": (0, 200, 0),
    "yellow": (200, 200, 0),
    "grey": (50, 50, 50)
}

# --- Game State ---
game_state = "title"
solution_word = ""
target_art = []
player_art = []
player_guesses = []
current_guess = ""
current_row = 0

# --- Drawing Functions ---
def proportional_rect(x_ratio, y_ratio, width, height):
    x = screen.get_width() * x_ratio - width / 2
    y = screen.get_height() * y_ratio - height / 2
    return pygame.Rect(x, y, width, height)

def draw_title_screen():
    screen.fill("#222222")
    title = big_font.render("Welcome to Wordle Art!", True, (255, 255, 255))
    screen.blit(title, title.get_rect(center=(screen.get_width() * 0.5, screen.get_height() * 0.28)))

    subtitle = font.render("Recreate the target artwork using Wordle-style guesses", True, (200, 200, 200))
    screen.blit(subtitle, subtitle.get_rect(center=(screen.get_width() * 0.5, screen.get_height() * 0.36)))

    start_rect = proportional_rect(0.5, 0.55, 200, 60)
    pygame.draw.rect(screen, (70, 130, 180), start_rect)
    start_text = font.render("Start Game", True, (255, 255, 255))
    screen.blit(start_text, start_text.get_rect(center=start_rect.center))
    return start_rect

def draw_win_screen():
    screen.fill("#222222")
    win_text = big_font.render("/e🎉 You recreated the artwork perfectly!", True, (0, 255, 0))
    screen.blit(win_text, win_text.get_rect(center=(screen.get_width() * 0.5, screen.get_height() * 0.42)))

    solution_text = font.render(f"The solution was: {solution_word.upper()}", True, (255, 255, 255))
    screen.blit(solution_text, solution_text.get_rect(center=(screen.get_width() * 0.5, screen.get_height() * 0.5)))

    play_again_rect = proportional_rect(0.5, 0.6, 200, 60)
    pygame.draw.rect(screen, (70, 130, 180), play_again_rect)
    play_again_text = font.render("Play Again", True, (255, 255, 255))
    screen.blit(play_again_text, play_again_text.get_rect(center=play_again_rect.center))

    return play_again_rect

def draw_grid(grid_data, x_ratio, y_ratio, highlight_row=None, match_flags=None):
    x_offset = screen.get_width() * x_ratio
    y_start = screen.get_height() * y_ratio
    tile_size = 80
    spacing = 85

    for row in range(6):
        for col in range(5):
            color = COLOR_MAP["grey"]
            if row < len(grid_data):
                color = COLOR_MAP[grid_data[row][col]]
            pygame.draw.rect(screen, color, pygame.Rect(x_offset + col * spacing, y_start + row * spacing, tile_size, tile_size))

        if highlight_row is not None and row == highlight_row:
            arrow = label_font.render(">", True, (255, 255, 255))
            arrow_offset = int(10 * math.sin(pygame.time.get_ticks() / 200))
            screen.blit(arrow, (x_offset - 30 + arrow_offset, y_start + row * spacing + 25))


        if match_flags and row < len(match_flags) and match_flags[row]:
            center_x = x_offset + 5 * spacing + 35
            center_y = y_start + row * spacing + 40
            pygame.draw.circle(screen, (0, 255, 0), (center_x, center_y), 10)

def draw_guess_box(guess):
    x_start = screen.get_width() * 0.5 - 260
    y_pos = screen.get_height() * 0.75
    for i, letter in enumerate(guess.ljust(5)):
        pygame.draw.rect(screen, (100, 100, 100), pygame.Rect(x_start + i * 105, y_pos, 100, 100))
        if letter.strip():
            letter_text = font.render(letter.upper(), True, (255, 255, 255))
            screen.blit(letter_text, letter_text.get_rect(center=(x_start + i * 105 + 50, y_pos + 50)))

def draw_submit_button():
    submit_rect = proportional_rect(0.5, 0.88, 175, 60)
    pygame.draw.rect(screen, (70, 130, 180), submit_rect)
    submit_text = font.render("Submit", True, (255, 255, 255))
    screen.blit(submit_text, submit_text.get_rect(center=submit_rect.center))
    return submit_rect

def submit_guess():
    global current_guess, current_row, game_state
    if len(current_guess) != 5:
        return
    feedback = get_feedback(current_guess, solution_word)
    if feedback == target_art[current_row]:
        player_guesses.append(current_guess)
        player_art.append(feedback)
        current_guess = ""
        current_row += 1
        if current_row == 6:
            game_state = "won"
    else:
        current_guess = ""


# --- Main Loop ---
running = True
while running:
    screen.fill("#222222")

    if game_state == "title":
        start_button = draw_title_screen()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if start_button.collidepoint(event.pos):
                    game_state = "playing"
                    target_data = generate_target_art(WORDS)
                    solution_word = target_data["solution"]
                    target_art = target_data["art"]
                    player_art = []
                    player_guesses = []
                    current_guess = ""
                    current_row = 0
                    print("\n--- DEBUG: Target guesses used ---")
                    for i, guess in enumerate(target_data["guesses"]):
                        print(f"Row {i + 1}: {guess.upper()}")

    elif game_state == "playing":
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if submit_button.collidepoint(event.pos):
                    submit_guess()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN:
                    submit_guess()
                elif event.key == pygame.K_BACKSPACE:
                    current_guess = current_guess[:-1]
                elif event.unicode.isalpha() and len(current_guess) < 5:
                    current_guess += event.unicode.lower()

        match_flags = [player_art[i] == target_art[i] for i in range(len(player_art))]

        title = big_font.render(f"Solution: {solution_word.upper()}", True, (255, 255, 255))
        screen.blit(title, title.get_rect(center=(screen.get_width() * 0.5, screen.get_height() * 0.08)))

        screen.blit(label_font.render("Intended artwork:", True, (255, 255, 255)), (screen.get_width() * 0.15, screen.get_height() * 0.12))
        screen.blit(label_font.render("Player Art:", True, (255, 255, 255)), (screen.get_width() * 0.64, screen.get_height() * 0.12))

        draw_grid(target_art, 0.15, 0.18)
        draw_grid(player_art, 0.64, 0.18, highlight_row=current_row, match_flags=match_flags)
        draw_guess_box(current_guess)
        submit_button = draw_submit_button()
        


    elif game_state == "won":
        play_again_button = draw_win_screen()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if play_again_button.collidepoint(event.pos):
                    # Reset game state
                    game_state = "playing"
                    target_data = generate_target_art(WORDS)
                    solution_word = target_data["solution"]
                    target_art = target_data["art"]
                    player_art = []
                    player_guesses = []
                    current_guess = ""
                    current_row = 0
                    print("\n--- DEBUG: Target guesses used ---")
                    for i, guess in enumerate(target_data["guesses"]):
                        print(f"Row {i + 1}: {guess.upper()}")


    pygame.display.flip()
    clock.tick(165)

pygame.quit()
