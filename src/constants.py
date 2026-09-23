# Game Screen
SCREEN_SIDE_LENGTH = 40
BIRD_STARTING_ROW_COORD = 20
BIRD_COL_COORD = 10

# Game Mechanics - to be tinkered with until game feels right
MS_PER_GAME_TICK = 500
GRAV_ACCELERATION_ROWS_PER_TICK_SQUARED = 2.0
VERTITCAL_VELOCITY_CLAMP_ROWS_PER_TICK = 4.0

# Colours
RGB = tuple[int, int, int]
BACKGROUND_COLOUR: RGB = (255, 255, 255)  # White
BIRD_COLOUR: RGB = (255, 0, 0)  # Red

# ANSI terminal codes
ESCAPE: str = "\033"
BCG: str = "48"  # Background
RGB_MODE: str = "2"
RESET: str = f"{ESCAPE}[0m"
