# Game Screen
SCREEN_SIDE_LENGTH = 40
BIRD_STARTING_ROW_COORD = 20
BIRD_COL_COORD = 10

# Game Mechanics - to be tinkered with until game feels right
MS_PER_GAME_TICK = 1
GRAV_ACCELERATION_ROWS_PER_TICK_SQUARED = 2.0
VERTITCAL_VELOCITY_CLAMP_ROWS_PER_TICK = 4.0

# Max Score
MAX_SCORE = 9999

# Score Display - each digit is drawn as a 7 row x 5 col block
SCORE_NUM_DIGITS = 4
SCORE_DIGIT_NUM_ROWS = 7
SCORE_DIGIT_NUM_COLS = 5
SCORE_DIGIT_COL_GAP = 1

# Colours
RGB = tuple[int, int, int]
BACKGROUND_COLOUR: RGB = (255, 255, 255)  # White
BIRD_COLOUR: RGB = (255, 0, 0)  # Red
SCORE_COLOUR: RGB = (0, 0, 0)  # Black

# ANSI terminal codes
ESCAPE: str = "\033"
BCG: str = "48"  # Background
RGB_MODE: str = "2"
RESET: str = f"{ESCAPE}[0m"
