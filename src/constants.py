# Game Screen
SCREEN_SIDE_LENGTH = 25
BIRD_STARTING_ROW_COORD = 10
BIRD_COL_COORD = 10

# Game Mechanics
MS_PER_GAME_TICK = 100

# Colours
RGB = tuple[int, int, int]
BACKGROUND_COLOUR: RGB = (255, 255, 255)  # White
BIRD_COLOUR: RGB = (255, 0, 0)  # Red

# ANSI terminal codes
ESCAPE: str = "\033"
BCG: str = "48"  # Background
RGB_MODE: str = "2"
RESET: str = f"{ESCAPE}[0m"
