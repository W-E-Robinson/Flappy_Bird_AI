from constants import (
    SCREEN_SIDE_LENGTH,
    BACKGROUND_COLOUR,
    ESCAPE,
    BCG,
    RGB_MODE,
    RESET,
    BIRD_COLOUR,
    MS_PER_GAME_TICK,
    BIRD_STARTING_ROW_COORD,
    BIRD_COL_COORD,
)
import random
import time
import os
from typing import Literal


class Game:
    def __init__(self):
        self.screen = [
            [BACKGROUND_COLOUR for x in range(SCREEN_SIDE_LENGTH)]
            for y in range(SCREEN_SIDE_LENGTH)
        ]
        self.bird_row_coord = BIRD_STARTING_ROW_COORD
        self.screen[self.bird_row_coord][BIRD_COL_COORD] = BIRD_COLOUR

    def move_bird(self, direction: Literal["UP", "DOWN"]):
        self.screen[self.bird_row_coord][BIRD_COL_COORD] = BACKGROUND_COLOUR
        self.bird_row_coord = (
            self.bird_row_coord - 1 if direction == "UP" else self.bird_row_coord + 1
        )
        self.screen[self.bird_row_coord][BIRD_COL_COORD] = BIRD_COLOUR

    def on_tick(self):
        rand = random.uniform(0, 1)
        self.move_bird("DOWN" if rand >= 0.5 else "UP")

    def detect_game_over(self):
        if self.bird_row_coord == 0:  # Hit top of screen
            return True
        if self.bird_row_coord == SCREEN_SIDE_LENGTH - 1:  # Hit bottom of screen
            return True
        return False

    def game_loop(self):
        gameRunning = True

        while gameRunning:
            os.system("clear")

            self.on_tick()
            if self.detect_game_over() is True:
                gameRunning = False
            self.print_screen()

            time.sleep(MS_PER_GAME_TICK / 1000)

    def print_screen(self):
        for row in self.screen:
            for cell in row:
                [red, green, blue] = cell

                print(
                    f"{ESCAPE}[{BCG};{RGB_MODE};{red};{green};{blue}m  {RESET}", end=""
                )

            print()
