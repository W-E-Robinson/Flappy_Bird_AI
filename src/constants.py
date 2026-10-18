import os
import random

# Game Screen
SCREEN_SIDE_LENGTH = 40
BIRD_STARTING_TOP_ROW_COORD = 13
BIRD_LEFT_COL_COORD = 9

# Game Mechanics - to be tinkered with until game feels right
MS_PER_GAME_TICK = 100
MS_PER_REPLAY_TICK = 100
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
MAX_SCORE = 999

# Score Display - each digit is drawn as a 7 row x 5 col block
SCORE_NUM_DIGITS = 3
SCORE_DIGIT_NUM_ROWS = 7
SCORE_DIGIT_NUM_COLS = 5
SCORE_DIGIT_COL_GAP = 1
SCORE_DIGIT_ROW_GAP = 2  # Between 2 scores on a replay comparison run
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
BOT_BIRD_COLOUR: RGB = (0, 0, 255)  # Blue
OVERLAP_BIRD_COLOUR: RGB = (255, 0, 255)  # Magenta

# ANSI terminal codes
ESCAPE: str = "\033"
BCG: str = "48"  # Background
RGB_MODE: str = "2"
RESET: str = f"{ESCAPE}[0m"

# Network architecture
HIDDEN_LAYER_SIZE = 64
# Actions: input (bird moves up) or no input
OUTPUT_SIZE = 2
# Observables: bird top row, upcoming top gap row, upcoming botton gap row,
# distance to upcoming gap col, offset from gap centre, bird velocity,
# offset from the centre of the gap after next, whether that gap is on screen
INPUT_FEATURES = 8

# Training + Testing
NUM_TRAINING_EPISODES = 25_000
NUM_TEST_EPISODES = 1000
# Test runs use seeds TEST_SEED_START..+NUM_TEST_EPISODES, so every model faces
# the identical set of courses and the scores are comparable between runs
TEST_SEED_START = 0
NUM_STEPS_TARGET_NETWORK_RESET = 1000
LEARNING_RATE = 0.001
START_EPSILON = 1.0
FINAL_EPSILON = 0.005
# Fraction of the run spent decaying epsilon, so the remainder trains at the
# floor. Decoupled from the episode count: a longer run buys more exploitation
# episodes rather than a proportionally longer exploration phase.
EPSILON_DECAY_FRACTION = 0.8
DISCOUNT_FACTOR = 0.98
RUN_MODE = os.getenv("RUN_MODE", "RANDOM")  # RANDOM or TEST
random.seed(666)
TEST_OBSTACLE_DECIMALS = [random.uniform(0.0, 1.0) for _ in range(1005)]
# Enough to clear max score possible (100 is plenty of buffer)
MAX_EPISODE_STEPS = MAX_SCORE * DISTANCE_BETWEEN_OBSTACLES + 100

# Replay buffer
REPLAY_BUFFER_CAPACITY = 100_000
REPLAY_BATCH_SIZE = 64
MIN_REPLAY_BUFFER_SIZE = 1_000

# Replaying - options: BOT, HUMAN, BOTH, LATEST_BOT
REPLAY_MODE = os.getenv("REPLAY_MODE", "BOT")

# Graphing
GRAPH_MODE = os.getenv("GRAPH_MODE", "SESSION")  # options: SESSION, TEST_RUN
