import pygame
import cv2
import random
import sys

# Initialize Pygame
pygame.init()

# Screen dimensions
WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Stickman Math Attack")

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
BLUE = (0, 0, 255)
GREEN = (0, 255, 0)

# Fonts
FONT = pygame.font.SysFont('arial', 32)
BIG_FONT = pygame.font.SysFont('arial', 48)

# Game variables
player_health = 100
npc_health = 100
question = ""
correct_answer = 0
time_limit = 20  # Time limit for each question (in seconds)
time_left = time_limit
user_input = ""
current_action = None  # Tracks the current action ("player" or "npc")
video_playing = False  # Indicates if a video is being played
game_over = False  # Indicates if the game is over
skip_intro = False  # Indicates if the intro video should be skipped

# Clock for timing
clock = pygame.time.Clock()

# Stickman positions and sizes
PLAYER_WIDTH, PLAYER_HEIGHT = 150, 175  # Adjusted stickman size based on sample
NPC_WIDTH, NPC_HEIGHT = 150, 175
player_pos = [100, HEIGHT - PLAYER_HEIGHT - 50]
npc_pos = [WIDTH - NPC_WIDTH - 100, HEIGHT - NPC_HEIGHT - 50]

# Load videos
story_video = "story.mp4"
player_punch_video = "pc_headSmash.mp4"
player_kick_video = "pc_kick.mp4"
player_special_attack_video = "pc_special.mp4"  # New special attack video
npc_punch_video = "npc_punch.mp4"
npc_kick_video = "npc_kick.mp4"
player_win_video = "BlueWins.mp4"
npc_win_video = "RedWins.mp4"

# Load idle background image
idle_background = pygame.image.load("bg1.jpg")
idle_background = pygame.transform.scale(idle_background, (WIDTH, HEIGHT))

# Generate a multiplication question
def generate_question():
    global question, correct_answer
    num1 = random.randint(1, 99)
    num2 = random.randint(1, 99)
    correct_answer = num1 * num2
    question = f"{num1} x {num2} = ?"

# Draw health bar
def draw_health_bar(x, y, health, max_health=100):
    health = max(0, health)
    bar_width = 200
    bar_height = 20
    fill_width = int((health / max_health) * bar_width)
    pygame.draw.rect(screen, RED, (x, y, bar_width, bar_height))
    pygame.draw.rect(screen, GREEN, (x, y, fill_width, bar_height))

# Play video
def play_video(video_path):
    global video_playing
    cap = cv2.VideoCapture(video_path)
    video_playing = True
    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break
        # Convert frame to Pygame surface
        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        frame = cv2.resize(frame, (WIDTH, HEIGHT))
        frame_surface = pygame.surfarray.make_surface(frame.swapaxes(0, 1))
        screen.blit(frame_surface, (0, 0))
        pygame.display.update()
        pygame.time.wait(int(1000 / cap.get(cv2.CAP_PROP_FPS)))
        # Check for events to skip video
        for event in pygame.event.get():
            if event.type == pygame.KEYDOWN and event.key == pygame.K_RETURN:
                cap.release()
                video_playing = False
                return
    cap.release()
    video_playing = False

# Restart the game
def restart_game():
    global player_health, npc_health, time_left, user_input, current_action, game_over
    player_health = 100
    npc_health = 100
    time_left = time_limit
    user_input = ""
    current_action = None
    game_over = False
    generate_question()

# Initialize game
generate_question()

# Play story video before starting the game
if not skip_intro:
    play_video(story_video)

# Main game loop
running = True
while running:
    if not video_playing:
        # Display idle background if no conditions are met
        screen.blit(idle_background, (0, 0))

        # Event handling
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if not game_over:
                    if event.key == pygame.K_BACKSPACE:
                        user_input = user_input[:-1]
                    elif event.key == pygame.K_RETURN:
                        if user_input.isdigit():
                            if int(user_input) == correct_answer:
                                npc_health -= 25
                                current_action = "player"
                                # Randomly choose player attack
                                attack_video = random.choice([player_punch_video, player_kick_video, player_special_attack_video])
                                play_video(attack_video)
                            else:
                                player_health -= 25
                                current_action = "npc"
                                # Randomly choose NPC attack
                                attack_video = random.choice([npc_punch_video, npc_kick_video,npc_punch_video, npc_kick_video,npc_punch_video, npc_kick_video])
                                play_video(attack_video)
                            generate_question()
                        user_input = ""
                        time_left = time_limit
                    elif event.unicode.isdigit():
                        user_input += event.unicode
                if event.key == pygame.K_r and game_over:
                    restart_game()

        # Update timer
        if not game_over:
            time_left -= 1 / 60
            if time_left <= 0:
                player_health -= 10
                current_action = "npc"
                attack_video = random.choice([npc_punch_video, npc_kick_video])
                play_video(attack_video)
                generate_question()
                time_left = time_limit

        # Check for game end
        if not game_over and (player_health <= 0 or npc_health <= 0):
            game_over = True
            if npc_health <= 0:
                play_video(player_win_video)
            else:
                play_video(npc_win_video)

        # Draw health bars
        draw_health_bar(50, 50, player_health)
        draw_health_bar(WIDTH - 250, 50, npc_health)

        # Display question
        if not game_over:
            question_text = FONT.render(question, True, BLACK)
            screen.blit(question_text, (WIDTH // 2 - question_text.get_width() // 2, 50))

            # Display user input
            input_text = FONT.render(user_input, True, BLACK)
            screen.blit(input_text, (WIDTH // 2 - input_text.get_width() // 2, 100))

            # Display timer
            timer_text = FONT.render(f"Time left: {int(time_left)}s", True, BLACK)
            screen.blit(timer_text, (WIDTH // 2 - timer_text.get_width() // 2, 150))
        else:
            winner = "Player" if npc_health <= 0 else "NPC"
            end_text = BIG_FONT.render(f"{winner} Wins! Press R to Restart", True, BLACK)
            screen.blit(end_text, (WIDTH // 2 - end_text.get_width() // 2, HEIGHT // 2))

        pygame.display.flip()
        clock.tick(60)

pygame.quit()
sys.exit()