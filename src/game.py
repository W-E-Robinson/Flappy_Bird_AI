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
    GRAV_ACCELERATION_ROWS_PER_TICK_SQUARED,
    VERTITCAL_VELOCITY_CLAMP_ROWS_PER_TICK,
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
        self.num_ticks_in_free_fall = 0
        self.current_free_fall_velocity = 0

    def move_bird(self, direction: Literal["UP", "DOWN"]):
        self.screen[self.bird_row_coord][BIRD_COL_COORD] = BACKGROUND_COLOUR
        bird_velocity = self.bird_velocity_rows_per_tick(direction)

        self.bird_row_coord = (
            int(round(self.bird_row_coord - bird_velocity, 0))
            if direction == "UP"
            else int(round(self.bird_row_coord + bird_velocity, 0))
        )
        if self.bird_row_coord >= SCREEN_SIDE_LENGTH:
            self.bird_row_coord = SCREEN_SIDE_LENGTH - 1
        self.screen[self.bird_row_coord][BIRD_COL_COORD] = BIRD_COLOUR

    def bird_velocity_rows_per_tick(self, direction: Literal["UP", "DOWN"]):
        if direction == "UP":
            self.num_ticks_in_free_fall = 0
            self.current_free_fall_velocity = 0
            return 1
        elif (
            direction == "DOWN" and self.num_ticks_in_free_fall == 0
        ):  # LIME: do I like this? is it needed?
            self.num_ticks_in_free_fall = 1
            self.current_free_fall_velocity = GRAV_ACCELERATION_ROWS_PER_TICK_SQUARED
            return 1
        else:
            # https://en.wikipedia.org/wiki/Equations_for_a_falling_body
            # LIME: umm using above correctly?
            calced_velocity = (
                self.current_free_fall_velocity
                + GRAV_ACCELERATION_ROWS_PER_TICK_SQUARED * self.num_ticks_in_free_fall
            )
            self.num_ticks_in_free_fall += 1
            final_velocity = min(
                calced_velocity, VERTITCAL_VELOCITY_CLAMP_ROWS_PER_TICK
            )
            self.current_free_fall_velocity = final_velocity
            return final_velocity

    def on_tick(self):
        input = random.uniform(0, 1)
        self.move_bird("DOWN" if input >= 0.5 else "UP")

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

        print("Game Over")

    def print_screen(self):
        for row in self.screen:
            for cell in row:
                [red, green, blue] = cell

                print(
                    f"{ESCAPE}[{BCG};{RGB_MODE};{red};{green};{blue}m  {RESET}", end=""
                )

            print()
