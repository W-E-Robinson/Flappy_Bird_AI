from constants import (
    SCREEN_SIDE_LENGTH,
    MAX_SCORE,
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
    SCORE_COLOUR,
    SCORE_NUM_DIGITS,
    SCORE_DIGIT_NUM_ROWS,
    SCORE_DIGIT_NUM_COLS,
    SCORE_DIGIT_COL_GAP,
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
        self.score = 0
        self.game_over_screen = [
            [BACKGROUND_COLOUR for x in range(SCREEN_SIDE_LENGTH)]
            for y in range(SCREEN_SIDE_LENGTH)
        ]

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
        # LIME: to test score changing for now, will be pillars past
        self.score += 1

    def detect_game_over(self):
        if self.bird_row_coord == 0:  # Hit top of screen
            return True
        if self.bird_row_coord == SCREEN_SIDE_LENGTH - 1:  # Hit bottom of screen
            return True
        if self.score == MAX_SCORE:
            return True
        return False

    def game_loop(self):
        gameRunning = True

        while gameRunning:
            os.system("clear")

            self.on_tick()
            if self.detect_game_over() is True:
                gameRunning = False
            self.print_play_screen()

            time.sleep(MS_PER_GAME_TICK / 1000)

        os.system("clear")
        self.write_score_game_over_screen()
        self.print_game_over_screen()

    def print_play_screen(self):
        for row in self.screen:
            for cell in row:
                [red, green, blue] = cell

                print(
                    f"{ESCAPE}[{BCG};{RGB_MODE};{red};{green};{blue}m  {RESET}", end=""
                )

            print()

    def print_game_over_screen(self):
        for row in self.game_over_screen:
            for cell in row:
                [red, green, blue] = cell

                print(
                    f"{ESCAPE}[{BCG};{RGB_MODE};{red};{green};{blue}m  {RESET}", end=""
                )

            print()

    def write_score_game_over_screen(self):
        score = str(self.score if self.score <= MAX_SCORE else MAX_SCORE).zfill(
            SCORE_NUM_DIGITS
        )

        score_num_cols = (
            SCORE_NUM_DIGITS * SCORE_DIGIT_NUM_COLS
            + (SCORE_NUM_DIGITS - 1) * SCORE_DIGIT_COL_GAP
        )
        starting_starter_row = (SCREEN_SIDE_LENGTH - SCORE_DIGIT_NUM_ROWS) // 2
        starting_starter_col = (SCREEN_SIDE_LENGTH - score_num_cols) // 2

        for idx, digit in enumerate(score):
            starting_grid_point = [
                starting_starter_row,
                starting_starter_col
                + idx * (SCORE_DIGIT_NUM_COLS + SCORE_DIGIT_COL_GAP),
            ]

            # Each number has 7 rows + 5 cols
            if digit == "0":
                self.game_over_screen[starting_grid_point[0] + 0][
                    starting_grid_point[1] + 1
                ] = SCORE_COLOUR
                self.game_over_screen[starting_grid_point[0] + 0][
                    starting_grid_point[1] + 2
                ] = SCORE_COLOUR
                self.game_over_screen[starting_grid_point[0] + 0][
                    starting_grid_point[1] + 3
                ] = SCORE_COLOUR
                self.game_over_screen[starting_grid_point[0] + 1][
                    starting_grid_point[1] + 0
                ] = SCORE_COLOUR
                self.game_over_screen[starting_grid_point[0] + 2][
                    starting_grid_point[1] + 0
                ] = SCORE_COLOUR
                self.game_over_screen[starting_grid_point[0] + 3][
                    starting_grid_point[1] + 0
                ] = SCORE_COLOUR
                self.game_over_screen[starting_grid_point[0] + 4][
                    starting_grid_point[1] + 0
                ] = SCORE_COLOUR
                self.game_over_screen[starting_grid_point[0] + 5][
                    starting_grid_point[1] + 0
                ] = SCORE_COLOUR
                self.game_over_screen[starting_grid_point[0] + 1][
                    starting_grid_point[1] + 4
                ] = SCORE_COLOUR
                self.game_over_screen[starting_grid_point[0] + 2][
                    starting_grid_point[1] + 4
                ] = SCORE_COLOUR
                self.game_over_screen[starting_grid_point[0] + 3][
                    starting_grid_point[1] + 4
                ] = SCORE_COLOUR
                self.game_over_screen[starting_grid_point[0] + 4][
                    starting_grid_point[1] + 4
                ] = SCORE_COLOUR
                self.game_over_screen[starting_grid_point[0] + 5][
                    starting_grid_point[1] + 4
                ] = SCORE_COLOUR
                self.game_over_screen[starting_grid_point[0] + 6][
                    starting_grid_point[1] + 1
                ] = SCORE_COLOUR
                self.game_over_screen[starting_grid_point[0] + 6][
                    starting_grid_point[1] + 2
                ] = SCORE_COLOUR
                self.game_over_screen[starting_grid_point[0] + 6][
                    starting_grid_point[1] + 3
                ] = SCORE_COLOUR
                self.game_over_screen[starting_grid_point[0] + 4][
                    starting_grid_point[1] + 1
                ] = SCORE_COLOUR
                self.game_over_screen[starting_grid_point[0] + 3][
                    starting_grid_point[1] + 2
                ] = SCORE_COLOUR
                self.game_over_screen[starting_grid_point[0] + 2][
                    starting_grid_point[1] + 3
                ] = SCORE_COLOUR
            elif digit == "1":
                self.game_over_screen[starting_grid_point[0] + 0][
                    starting_grid_point[1] + 2
                ] = SCORE_COLOUR
                self.game_over_screen[starting_grid_point[0] + 1][
                    starting_grid_point[1] + 1
                ] = SCORE_COLOUR
                self.game_over_screen[starting_grid_point[0] + 1][
                    starting_grid_point[1] + 2
                ] = SCORE_COLOUR
                self.game_over_screen[starting_grid_point[0] + 2][
                    starting_grid_point[1] + 2
                ] = SCORE_COLOUR
                self.game_over_screen[starting_grid_point[0] + 3][
                    starting_grid_point[1] + 2
                ] = SCORE_COLOUR
                self.game_over_screen[starting_grid_point[0] + 4][
                    starting_grid_point[1] + 2
                ] = SCORE_COLOUR
                self.game_over_screen[starting_grid_point[0] + 5][
                    starting_grid_point[1] + 2
                ] = SCORE_COLOUR
                self.game_over_screen[starting_grid_point[0] + 6][
                    starting_grid_point[1] + 1
                ] = SCORE_COLOUR
                self.game_over_screen[starting_grid_point[0] + 6][
                    starting_grid_point[1] + 2
                ] = SCORE_COLOUR
                self.game_over_screen[starting_grid_point[0] + 6][
                    starting_grid_point[1] + 3
                ] = SCORE_COLOUR
            elif digit == "2":
                self.game_over_screen[starting_grid_point[0] + 0][
                    starting_grid_point[1] + 1
                ] = SCORE_COLOUR
                self.game_over_screen[starting_grid_point[0] + 0][
                    starting_grid_point[1] + 2
                ] = SCORE_COLOUR
                self.game_over_screen[starting_grid_point[0] + 0][
                    starting_grid_point[1] + 3
                ] = SCORE_COLOUR
                self.game_over_screen[starting_grid_point[0] + 1][
                    starting_grid_point[1] + 0
                ] = SCORE_COLOUR
                self.game_over_screen[starting_grid_point[0] + 1][
                    starting_grid_point[1] + 4
                ] = SCORE_COLOUR
                self.game_over_screen[starting_grid_point[0] + 2][
                    starting_grid_point[1] + 4
                ] = SCORE_COLOUR
                self.game_over_screen[starting_grid_point[0] + 3][
                    starting_grid_point[1] + 3
                ] = SCORE_COLOUR
                self.game_over_screen[starting_grid_point[0] + 4][
                    starting_grid_point[1] + 2
                ] = SCORE_COLOUR
                self.game_over_screen[starting_grid_point[0] + 5][
                    starting_grid_point[1] + 1
                ] = SCORE_COLOUR
                self.game_over_screen[starting_grid_point[0] + 6][
                    starting_grid_point[1] + 0
                ] = SCORE_COLOUR
                self.game_over_screen[starting_grid_point[0] + 6][
                    starting_grid_point[1] + 1
                ] = SCORE_COLOUR
                self.game_over_screen[starting_grid_point[0] + 6][
                    starting_grid_point[1] + 2
                ] = SCORE_COLOUR
                self.game_over_screen[starting_grid_point[0] + 6][
                    starting_grid_point[1] + 3
                ] = SCORE_COLOUR
                self.game_over_screen[starting_grid_point[0] + 6][
                    starting_grid_point[1] + 4
                ] = SCORE_COLOUR
            elif digit == "3":
                self.game_over_screen[starting_grid_point[0] + 0][
                    starting_grid_point[1] + 1
                ] = SCORE_COLOUR
                self.game_over_screen[starting_grid_point[0] + 0][
                    starting_grid_point[1] + 2
                ] = SCORE_COLOUR
                self.game_over_screen[starting_grid_point[0] + 0][
                    starting_grid_point[1] + 3
                ] = SCORE_COLOUR
                self.game_over_screen[starting_grid_point[0] + 1][
                    starting_grid_point[1] + 0
                ] = SCORE_COLOUR
                self.game_over_screen[starting_grid_point[0] + 1][
                    starting_grid_point[1] + 4
                ] = SCORE_COLOUR
                self.game_over_screen[starting_grid_point[0] + 2][
                    starting_grid_point[1] + 4
                ] = SCORE_COLOUR
                self.game_over_screen[starting_grid_point[0] + 3][
                    starting_grid_point[1] + 2
                ] = SCORE_COLOUR
                self.game_over_screen[starting_grid_point[0] + 3][
                    starting_grid_point[1] + 3
                ] = SCORE_COLOUR
                self.game_over_screen[starting_grid_point[0] + 4][
                    starting_grid_point[1] + 4
                ] = SCORE_COLOUR
                self.game_over_screen[starting_grid_point[0] + 5][
                    starting_grid_point[1] + 0
                ] = SCORE_COLOUR
                self.game_over_screen[starting_grid_point[0] + 5][
                    starting_grid_point[1] + 4
                ] = SCORE_COLOUR
                self.game_over_screen[starting_grid_point[0] + 6][
                    starting_grid_point[1] + 1
                ] = SCORE_COLOUR
                self.game_over_screen[starting_grid_point[0] + 6][
                    starting_grid_point[1] + 2
                ] = SCORE_COLOUR
                self.game_over_screen[starting_grid_point[0] + 6][
                    starting_grid_point[1] + 3
                ] = SCORE_COLOUR
            elif digit == "4":
                self.game_over_screen[starting_grid_point[0] + 0][
                    starting_grid_point[1] + 3
                ] = SCORE_COLOUR
                self.game_over_screen[starting_grid_point[0] + 1][
                    starting_grid_point[1] + 2
                ] = SCORE_COLOUR
                self.game_over_screen[starting_grid_point[0] + 1][
                    starting_grid_point[1] + 3
                ] = SCORE_COLOUR
                self.game_over_screen[starting_grid_point[0] + 2][
                    starting_grid_point[1] + 1
                ] = SCORE_COLOUR
                self.game_over_screen[starting_grid_point[0] + 2][
                    starting_grid_point[1] + 3
                ] = SCORE_COLOUR
                self.game_over_screen[starting_grid_point[0] + 3][
                    starting_grid_point[1] + 0
                ] = SCORE_COLOUR
                self.game_over_screen[starting_grid_point[0] + 3][
                    starting_grid_point[1] + 3
                ] = SCORE_COLOUR
                self.game_over_screen[starting_grid_point[0] + 4][
                    starting_grid_point[1] + 0
                ] = SCORE_COLOUR
                self.game_over_screen[starting_grid_point[0] + 4][
                    starting_grid_point[1] + 1
                ] = SCORE_COLOUR
                self.game_over_screen[starting_grid_point[0] + 4][
                    starting_grid_point[1] + 2
                ] = SCORE_COLOUR
                self.game_over_screen[starting_grid_point[0] + 4][
                    starting_grid_point[1] + 3
                ] = SCORE_COLOUR
                self.game_over_screen[starting_grid_point[0] + 4][
                    starting_grid_point[1] + 4
                ] = SCORE_COLOUR
                self.game_over_screen[starting_grid_point[0] + 5][
                    starting_grid_point[1] + 3
                ] = SCORE_COLOUR
                self.game_over_screen[starting_grid_point[0] + 6][
                    starting_grid_point[1] + 3
                ] = SCORE_COLOUR
            elif digit == "5":
                self.game_over_screen[starting_grid_point[0] + 0][
                    starting_grid_point[1] + 0
                ] = SCORE_COLOUR
                self.game_over_screen[starting_grid_point[0] + 0][
                    starting_grid_point[1] + 1
                ] = SCORE_COLOUR
                self.game_over_screen[starting_grid_point[0] + 0][
                    starting_grid_point[1] + 2
                ] = SCORE_COLOUR
                self.game_over_screen[starting_grid_point[0] + 0][
                    starting_grid_point[1] + 3
                ] = SCORE_COLOUR
                self.game_over_screen[starting_grid_point[0] + 0][
                    starting_grid_point[1] + 4
                ] = SCORE_COLOUR
                self.game_over_screen[starting_grid_point[0] + 1][
                    starting_grid_point[1] + 0
                ] = SCORE_COLOUR
                self.game_over_screen[starting_grid_point[0] + 2][
                    starting_grid_point[1] + 0
                ] = SCORE_COLOUR
                self.game_over_screen[starting_grid_point[0] + 2][
                    starting_grid_point[1] + 1
                ] = SCORE_COLOUR
                self.game_over_screen[starting_grid_point[0] + 2][
                    starting_grid_point[1] + 2
                ] = SCORE_COLOUR
                self.game_over_screen[starting_grid_point[0] + 2][
                    starting_grid_point[1] + 3
                ] = SCORE_COLOUR
                self.game_over_screen[starting_grid_point[0] + 3][
                    starting_grid_point[1] + 4
                ] = SCORE_COLOUR
                self.game_over_screen[starting_grid_point[0] + 4][
                    starting_grid_point[1] + 4
                ] = SCORE_COLOUR
                self.game_over_screen[starting_grid_point[0] + 5][
                    starting_grid_point[1] + 0
                ] = SCORE_COLOUR
                self.game_over_screen[starting_grid_point[0] + 5][
                    starting_grid_point[1] + 4
                ] = SCORE_COLOUR
                self.game_over_screen[starting_grid_point[0] + 6][
                    starting_grid_point[1] + 1
                ] = SCORE_COLOUR
                self.game_over_screen[starting_grid_point[0] + 6][
                    starting_grid_point[1] + 2
                ] = SCORE_COLOUR
                self.game_over_screen[starting_grid_point[0] + 6][
                    starting_grid_point[1] + 3
                ] = SCORE_COLOUR
            elif digit == "6":
                self.game_over_screen[starting_grid_point[0] + 0][
                    starting_grid_point[1] + 2
                ] = SCORE_COLOUR
                self.game_over_screen[starting_grid_point[0] + 0][
                    starting_grid_point[1] + 3
                ] = SCORE_COLOUR
                self.game_over_screen[starting_grid_point[0] + 1][
                    starting_grid_point[1] + 1
                ] = SCORE_COLOUR
                self.game_over_screen[starting_grid_point[0] + 2][
                    starting_grid_point[1] + 0
                ] = SCORE_COLOUR
                self.game_over_screen[starting_grid_point[0] + 3][
                    starting_grid_point[1] + 0
                ] = SCORE_COLOUR
                self.game_over_screen[starting_grid_point[0] + 3][
                    starting_grid_point[1] + 1
                ] = SCORE_COLOUR
                self.game_over_screen[starting_grid_point[0] + 3][
                    starting_grid_point[1] + 2
                ] = SCORE_COLOUR
                self.game_over_screen[starting_grid_point[0] + 3][
                    starting_grid_point[1] + 3
                ] = SCORE_COLOUR
                self.game_over_screen[starting_grid_point[0] + 4][
                    starting_grid_point[1] + 0
                ] = SCORE_COLOUR
                self.game_over_screen[starting_grid_point[0] + 4][
                    starting_grid_point[1] + 4
                ] = SCORE_COLOUR
                self.game_over_screen[starting_grid_point[0] + 5][
                    starting_grid_point[1] + 0
                ] = SCORE_COLOUR
                self.game_over_screen[starting_grid_point[0] + 5][
                    starting_grid_point[1] + 4
                ] = SCORE_COLOUR
                self.game_over_screen[starting_grid_point[0] + 6][
                    starting_grid_point[1] + 1
                ] = SCORE_COLOUR
                self.game_over_screen[starting_grid_point[0] + 6][
                    starting_grid_point[1] + 2
                ] = SCORE_COLOUR
                self.game_over_screen[starting_grid_point[0] + 6][
                    starting_grid_point[1] + 3
                ] = SCORE_COLOUR
            elif digit == "7":
                self.game_over_screen[starting_grid_point[0] + 0][
                    starting_grid_point[1] + 0
                ] = SCORE_COLOUR
                self.game_over_screen[starting_grid_point[0] + 0][
                    starting_grid_point[1] + 1
                ] = SCORE_COLOUR
                self.game_over_screen[starting_grid_point[0] + 0][
                    starting_grid_point[1] + 2
                ] = SCORE_COLOUR
                self.game_over_screen[starting_grid_point[0] + 0][
                    starting_grid_point[1] + 3
                ] = SCORE_COLOUR
                self.game_over_screen[starting_grid_point[0] + 0][
                    starting_grid_point[1] + 4
                ] = SCORE_COLOUR
                self.game_over_screen[starting_grid_point[0] + 1][
                    starting_grid_point[1] + 4
                ] = SCORE_COLOUR
                self.game_over_screen[starting_grid_point[0] + 2][
                    starting_grid_point[1] + 3
                ] = SCORE_COLOUR
                self.game_over_screen[starting_grid_point[0] + 3][
                    starting_grid_point[1] + 2
                ] = SCORE_COLOUR
                self.game_over_screen[starting_grid_point[0] + 4][
                    starting_grid_point[1] + 1
                ] = SCORE_COLOUR
                self.game_over_screen[starting_grid_point[0] + 5][
                    starting_grid_point[1] + 1
                ] = SCORE_COLOUR
                self.game_over_screen[starting_grid_point[0] + 6][
                    starting_grid_point[1] + 1
                ] = SCORE_COLOUR
            elif digit == "8":
                self.game_over_screen[starting_grid_point[0] + 0][
                    starting_grid_point[1] + 1
                ] = SCORE_COLOUR
                self.game_over_screen[starting_grid_point[0] + 0][
                    starting_grid_point[1] + 2
                ] = SCORE_COLOUR
                self.game_over_screen[starting_grid_point[0] + 0][
                    starting_grid_point[1] + 3
                ] = SCORE_COLOUR
                self.game_over_screen[starting_grid_point[0] + 1][
                    starting_grid_point[1] + 0
                ] = SCORE_COLOUR
                self.game_over_screen[starting_grid_point[0] + 1][
                    starting_grid_point[1] + 4
                ] = SCORE_COLOUR
                self.game_over_screen[starting_grid_point[0] + 2][
                    starting_grid_point[1] + 0
                ] = SCORE_COLOUR
                self.game_over_screen[starting_grid_point[0] + 2][
                    starting_grid_point[1] + 4
                ] = SCORE_COLOUR
                self.game_over_screen[starting_grid_point[0] + 3][
                    starting_grid_point[1] + 1
                ] = SCORE_COLOUR
                self.game_over_screen[starting_grid_point[0] + 3][
                    starting_grid_point[1] + 2
                ] = SCORE_COLOUR
                self.game_over_screen[starting_grid_point[0] + 3][
                    starting_grid_point[1] + 3
                ] = SCORE_COLOUR
                self.game_over_screen[starting_grid_point[0] + 4][
                    starting_grid_point[1] + 0
                ] = SCORE_COLOUR
                self.game_over_screen[starting_grid_point[0] + 4][
                    starting_grid_point[1] + 4
                ] = SCORE_COLOUR
                self.game_over_screen[starting_grid_point[0] + 5][
                    starting_grid_point[1] + 0
                ] = SCORE_COLOUR
                self.game_over_screen[starting_grid_point[0] + 5][
                    starting_grid_point[1] + 4
                ] = SCORE_COLOUR
                self.game_over_screen[starting_grid_point[0] + 6][
                    starting_grid_point[1] + 1
                ] = SCORE_COLOUR
                self.game_over_screen[starting_grid_point[0] + 6][
                    starting_grid_point[1] + 2
                ] = SCORE_COLOUR
                self.game_over_screen[starting_grid_point[0] + 6][
                    starting_grid_point[1] + 3
                ] = SCORE_COLOUR
            elif digit == "9":
                self.game_over_screen[starting_grid_point[0] + 0][
                    starting_grid_point[1] + 1
                ] = SCORE_COLOUR
                self.game_over_screen[starting_grid_point[0] + 0][
                    starting_grid_point[1] + 2
                ] = SCORE_COLOUR
                self.game_over_screen[starting_grid_point[0] + 0][
                    starting_grid_point[1] + 3
                ] = SCORE_COLOUR
                self.game_over_screen[starting_grid_point[0] + 1][
                    starting_grid_point[1] + 0
                ] = SCORE_COLOUR
                self.game_over_screen[starting_grid_point[0] + 1][
                    starting_grid_point[1] + 4
                ] = SCORE_COLOUR
                self.game_over_screen[starting_grid_point[0] + 2][
                    starting_grid_point[1] + 0
                ] = SCORE_COLOUR
                self.game_over_screen[starting_grid_point[0] + 2][
                    starting_grid_point[1] + 4
                ] = SCORE_COLOUR
                self.game_over_screen[starting_grid_point[0] + 3][
                    starting_grid_point[1] + 1
                ] = SCORE_COLOUR
                self.game_over_screen[starting_grid_point[0] + 3][
                    starting_grid_point[1] + 2
                ] = SCORE_COLOUR
                self.game_over_screen[starting_grid_point[0] + 3][
                    starting_grid_point[1] + 3
                ] = SCORE_COLOUR
                self.game_over_screen[starting_grid_point[0] + 3][
                    starting_grid_point[1] + 4
                ] = SCORE_COLOUR
                self.game_over_screen[starting_grid_point[0] + 4][
                    starting_grid_point[1] + 4
                ] = SCORE_COLOUR
                self.game_over_screen[starting_grid_point[0] + 5][
                    starting_grid_point[1] + 3
                ] = SCORE_COLOUR
                self.game_over_screen[starting_grid_point[0] + 6][
                    starting_grid_point[1] + 1
                ] = SCORE_COLOUR
                self.game_over_screen[starting_grid_point[0] + 6][
                    starting_grid_point[1] + 2
                ] = SCORE_COLOUR
