from constants import (
    SCREEN_SIDE_LENGTH,
    REDUCTION_PER_GAP_SHRINK,
    MAX_SCORE,
    BACKGROUND_COLOUR,
    RGB,
    ESCAPE,
    BCG,
    RGB_MODE,
    RESET,
    BIRD_COLOUR,
    MS_PER_GAME_TICK,
    BIRD_STARTING_TOP_ROW_COORD,
    BIRD_LEFT_COL_COORD,
    GRAV_ACCELERATION_ROWS_PER_TICK_SQUARED,
    VERTITCAL_VELOCITY_CLAMP_ROWS_PER_TICK,
    SCORE_COLOUR,
    SCORE_NUM_DIGITS,
    SCORE_DIGIT_NUM_ROWS,
    SCORE_DIGIT_NUM_COLS,
    SCORE_DIGIT_COL_GAP,
    STARTING_OBSTACLE_GAP_SIZE,
    FINAL_OBSTACLE_GAP_SIZE,
    NUM_POINTS_PER_GAP_SHRINK,
    MIN_DISTANCE_BOUNDARY_TO_GAP,
    DISTANCE_BETWEEN_OBSTACLES,
    OBSTACLE_COLOUR,
    DIGIT_GLYPHS,
    BIRD_SIZE,
    BIRD_FLAP_RISE_ROWS,
)
import random
import math
import time
import os
import sys
import termios
import tty
import select


class Game:
    def __init__(self):
        self.screen = [
            [BACKGROUND_COLOUR for x in range(SCREEN_SIDE_LENGTH)]
            for y in range(SCREEN_SIDE_LENGTH)
        ]
        # Bird is BIRD_SIZExBIRD_SIZE square, tracked in row plane by top row
        self.bird_top_row_coord = BIRD_STARTING_TOP_ROW_COORD
        self.game_over_screen = [
            [BACKGROUND_COLOUR for x in range(SCREEN_SIDE_LENGTH)]
            for y in range(SCREEN_SIDE_LENGTH)
        ]
        self.num_ticks_rising_without_further_input = 0
        self.last_direction = "DOWN"
        self.current_velocity = 0
        self.score = 0
        self.gaps = (
            []
        )  # [col, gap_top_idx, gap_bottom_idx] # LIME: I don't like this, dict?
        self.game_ticks_elapsed = 0
        self.input_this_tick = False

        self.draw_current_bird_position(BIRD_COLOUR)

    def move_bird_vertically(self):
        bird_velocity, direction = self.bird_velocity_rows_per_tick_rounded()

        self.draw_current_bird_position(BACKGROUND_COLOUR)
        self.bird_top_row_coord = (
            self.bird_top_row_coord - bird_velocity
            if direction == "UP"
            else self.bird_top_row_coord + bird_velocity
        )

        # Stops 'list index out of range' error on game over detection whn overshoot
        if self.bird_top_row_coord <= 0:
            self.bird_top_row_coord = 0
        if self.bird_top_row_coord >= SCREEN_SIDE_LENGTH - BIRD_SIZE:
            self.bird_top_row_coord = SCREEN_SIDE_LENGTH - BIRD_SIZE

        self.draw_current_bird_position(BIRD_COLOUR)

    def get_all_bird_coords(self):
        coords = []
        for i in range(BIRD_SIZE):
            for j in range(BIRD_SIZE):
                coords.append([self.bird_top_row_coord + i, BIRD_LEFT_COL_COORD + j])
        return coords

    # Used to clear up current bird position or draw new position
    def draw_current_bird_position(self, colour: RGB):
        for coord in self.get_all_bird_coords():
            row, col = coord
            self.screen[row][col] = colour

    def bird_velocity_rows_per_tick_rounded(self):
        if self.input_this_tick:
            self.last_direction = "UP"
            self.current_velocity = BIRD_FLAP_RISE_ROWS
            return BIRD_FLAP_RISE_ROWS, "UP"
        else:
            # Motion with constant acceleration (including hard cap falling), source:
            # https://openstax.org/books/university-physics-volume-1/pages/3-4-motion-with-constant-acceleration
            # With constant acceleration and per tick calculating, just becomes:
            # new velocity = current veloicity +/- grav constant
            if self.last_direction == "UP":
                new_velocity = (
                    self.current_velocity - GRAV_ACCELERATION_ROWS_PER_TICK_SQUARED
                )

                # Can't see this ever guard coming into place given the grav
                # constants I'm experimenting with are so low
                if new_velocity <= 0:
                    self.current_velocity = 0
                    self.last_direction = "DOWN"
                    return 0, "DOWN"

                self.current_velocity = new_velocity
                return int(round(new_velocity)), "UP"
            else:
                new_velocity = (
                    self.current_velocity + GRAV_ACCELERATION_ROWS_PER_TICK_SQUARED
                )
                actual_velocity = min(
                    new_velocity, VERTITCAL_VELOCITY_CLAMP_ROWS_PER_TICK
                )
                self.current_velocity = actual_velocity
                return int(round(actual_velocity)), "DOWN"

    def on_tick(self):
        self.move_bird_vertically()
        self.move_obstacles()
        if self.game_ticks_elapsed % DISTANCE_BETWEEN_OBSTACLES == 0:
            self.generate_new_obstacle()
        for idx in range(len(self.gaps)):
            col_idx, top_gap_row_idx, bottom_gap_row_idx = self.gaps[idx]
            if col_idx == BIRD_LEFT_COL_COORD - 1:
                self.score += 1
        self.game_ticks_elapsed += 1

    def move_obstacles(self):
        for idx in range(len(self.gaps)):
            col_idx, top_gap_row_idx, bottom_gap_row_idx = self.gaps[idx]
            for row_idx in range(top_gap_row_idx + 1):
                self.screen[row_idx][col_idx] = BACKGROUND_COLOUR
            for row_idx in range(bottom_gap_row_idx, SCREEN_SIDE_LENGTH):
                self.screen[row_idx][col_idx] = BACKGROUND_COLOUR
            self.gaps[idx] = (col_idx - 1, top_gap_row_idx, bottom_gap_row_idx)

        def my_func(x):
            col_idx, top_gap_row_idx, bottom_gap_row_idx = x
            if col_idx >= 0:
                return True
            else:
                return False

        self.gaps = list(filter(my_func, self.gaps))

        for idx in range(len(self.gaps)):
            col_idx, top_gap_row_idx, bottom_gap_row_idx = self.gaps[idx]
            for row_idx in range(top_gap_row_idx + 1):
                self.screen[row_idx][col_idx] = OBSTACLE_COLOUR
            for row_idx in range(bottom_gap_row_idx, SCREEN_SIDE_LENGTH):
                self.screen[row_idx][col_idx] = OBSTACLE_COLOUR

    def detect_game_over(self):
        if self.bird_top_row_coord == 0:  # Hit top of screen
            return True

        if (
            self.bird_top_row_coord == SCREEN_SIDE_LENGTH - BIRD_SIZE
        ):  # Hit bottom of screen
            return True

        for idx in range(len(self.gaps)):
            col_idx, top_gap_row_idx, bottom_gap_row_idx = self.gaps[idx]
            if col_idx == BIRD_LEFT_COL_COORD:
                if (
                    self.bird_top_row_coord < top_gap_row_idx
                    or self.bird_top_row_coord > bottom_gap_row_idx
                ):
                    return True

        if self.score == MAX_SCORE:
            return True

        return False

    def generate_new_obstacle(self):
        num_reductions = math.floor(self.score / NUM_POINTS_PER_GAP_SHRINK)
        gap_size = (
            STARTING_OBSTACLE_GAP_SIZE - num_reductions * REDUCTION_PER_GAP_SHRINK
        )
        gap_size = max(gap_size, FINAL_OBSTACLE_GAP_SIZE)

        # Both bounds included on randint
        top_gap_row_idx = random.randint(
            MIN_DISTANCE_BOUNDARY_TO_GAP,
            SCREEN_SIDE_LENGTH - MIN_DISTANCE_BOUNDARY_TO_GAP - gap_size,
        )
        obstacle_starting_col_idx = SCREEN_SIDE_LENGTH - 1
        self.gaps.append(
            (obstacle_starting_col_idx, top_gap_row_idx, top_gap_row_idx + gap_size)
        )

    def game_loop(self):
        fd = sys.stdin.fileno()
        old_settings = termios.tcgetattr(fd)
        # LIME: only posix this works for? = make note if so

        try:
            tty.setcbreak(fd)

            gameRunning = True

            while gameRunning:
                self.input_this_tick = False

                readable, _, _ = select.select([sys.stdin], [], [], 0)

                if readable:
                    while select.select([sys.stdin], [], [], 0)[0]:
                        key = sys.stdin.read(1)
                        if key == " ":
                            self.input_this_tick = True

                os.system("clear")

                self.on_tick()
                if self.detect_game_over() is True:
                    gameRunning = False
                self.print_screen(self.screen)

                time.sleep(MS_PER_GAME_TICK / 1000)
        finally:
            termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)

        os.system("clear")
        self.write_score_game_over_screen()
        self.print_screen(self.game_over_screen)

    def print_screen(self, screen):
        for row in screen:
            for cell in row:
                [red, green, blue] = cell

                print(
                    f"{ESCAPE}[{BCG};{RGB_MODE};{red};{green};{blue}m  {RESET}", end=""
                )

            print()

    def write_score_game_over_screen(self):
        score = str(min(self.score, MAX_SCORE)).zfill(SCORE_NUM_DIGITS)

        score_num_cols = (
            SCORE_NUM_DIGITS * SCORE_DIGIT_NUM_COLS
            + (SCORE_NUM_DIGITS - 1) * SCORE_DIGIT_COL_GAP
        )
        starting_starter_row = (SCREEN_SIDE_LENGTH - SCORE_DIGIT_NUM_ROWS) // 2
        starting_starter_col = (SCREEN_SIDE_LENGTH - score_num_cols) // 2

        for idx, digit in enumerate(score):
            digit_col = starting_starter_col + idx * (
                SCORE_DIGIT_NUM_COLS + SCORE_DIGIT_COL_GAP
            )

            for row_offset, glyph_row in enumerate(DIGIT_GLYPHS[digit]):
                for col_offset, cell in enumerate(glyph_row):
                    if cell == "#":
                        self.game_over_screen[starting_starter_row + row_offset][
                            digit_col + col_offset
                        ] = SCORE_COLOUR
