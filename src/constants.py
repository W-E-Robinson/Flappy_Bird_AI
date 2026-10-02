import os
import random

# Game Screen
SCREEN_SIDE_LENGTH = 40
BIRD_STARTING_TOP_ROW_COORD = 13
BIRD_LEFT_COL_COORD = 9

# Game Mechanics - to be tinkered with until game feels right
MS_PER_GAME_TICK = 1000
GRAV_ACCELERATION_ROWS_PER_TICK_SQUARED = 1.2
VERTITCAL_VELOCITY_CLAMP_ROWS_PER_TICK = 4.0
BIRD_SIZE = 3  # BIRD_SIZExBIRD_SIZE pixels
BIRD_FLAP_RISE_ROWS = 2

# Game Rules
STARTING_OBSTACLE_GAP_SIZE = 15
FINAL_OBSTACLE_GAP_SIZE = 5
NUM_POINTS_PER_GAP_SHRINK = 10
REDUCTION_PER_GAP_SHRINK = 2
MIN_DISTANCE_BOUNDARY_TO_GAP = 2
DISTANCE_BETWEEN_OBSTACLES = 20

# Max Score
MAX_SCORE = 9_999

# Score Display - each digit is drawn as a 7 row x 5 col block
SCORE_NUM_DIGITS = 4
SCORE_DIGIT_NUM_ROWS = 7
SCORE_DIGIT_NUM_COLS = 5
SCORE_DIGIT_COL_GAP = 1
DIGIT_GLYPHS: dict[str, list[str]] = {
    # Each digit is drawn as a basic bitmap, # is a filled cell
    "0": [" ### ", "#   #", "#  ##", "# # #", "##  #", "#   #", " ### "],
    "1": ["  #  ", " ##  ", "  #  ", "  #  ", "  #  ", "  #  ", " ### "],
    "2": [" ### ", "#   #", "    #", "   # ", "  #  ", " #   ", "#####"],
    "3": [" ### ", "#   #", "    #", "  ## ", "    #", "#   #", " ### "],
    "4": ["   # ", "  ## ", " # # ", "#  # ", "#####", "   # ", "   # "],
    "5": ["#####", "#    ", "#### ", "    #", "    #", "#   #", " ### "],
    "6": ["  ## ", " #   ", "#    ", "#### ", "#   #", "#   #", " ### "],
    "7": ["#####", "    #", "   # ", "  #  ", " #   ", " #   ", " #   "],
    "8": [" ### ", "#   #", "#   #", " ### ", "#   #", "#   #", " ### "],
    "9": [" ### ", "#   #", "#   #", " ####", "    #", "   # ", " ##  "],
}

# Colours
RGB = tuple[int, int, int]
BACKGROUND_COLOUR: RGB = (255, 255, 255)  # White
BIRD_COLOUR: RGB = (255, 0, 0)  # Red
SCORE_COLOUR: RGB = (0, 0, 0)  # Black
OBSTACLE_COLOUR: RGB = (0, 0, 0)  # Black

# ANSI terminal codes
ESCAPE: str = "\033"
BCG: str = "48"  # Background
RGB_MODE: str = "2"
RESET: str = f"{ESCAPE}[0m"

# Network architecture
HIDDEN_LAYER_SIZE = 32
# Actions: input (bird moves up) or no input
OUTPUT_SIZE = 2
# Observables: bird top row, upcoming top gap row, upcoming botton gap row, upcoming gap col
INPUT_FEATURES = 4

# Training + Testing
NUM_TRAINING_EPISODES = 100
NUM_TEST_EPISODES = 100
NUM_STEPS_TARGET_NETWORK_RESET = 100
LEARNING_RATE = 0.001
START_EPSILON = 1.0
FINAL_EPSILON = 0.1
DISCOUNT_FACTOR = 0.95
RUN_MODE = os.getenv("RUN_MODE", "RANDOM")  # RANDOM or TEST
random.seed(666)
TEST_OBSTACLE_DECIMALS = [random.uniform(0.0, 1.0) for _ in range(1005)]
# Enough to clear max score possible (100 is plenty of buffer)
MAX_EPISODE_STEPS = MAX_SCORE * DISTANCE_BETWEEN_OBSTACLES + 100

# Replaying
REPLAY_MODE = os.getenv("REPLAY", "BOT")  # options: BOT, HUMAN, BOTH
