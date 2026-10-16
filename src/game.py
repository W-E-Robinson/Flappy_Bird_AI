from constants import (
    RUN_MODE,
    TEST_OBSTACLE_DECIMALS,
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
    MS_PER_REPLAY_TICK,
    BIRD_STARTING_TOP_ROW_COORD,
    BIRD_LEFT_COL_COORD,
    GRAV_ACCELERATION_ROWS_PER_TICK_SQUARED,
    VERTITCAL_VELOCITY_CLAMP_ROWS_PER_TICK,
    SCORE_COLOUR,
    SCORE_NUM_DIGITS,
    SCORE_DIGIT_NUM_ROWS,
    SCORE_DIGIT_NUM_COLS,
    SCORE_DIGIT_COL_GAP,
    SCORE_DIGIT_ROW_GAP,
    STARTING_OBSTACLE_GAP_SIZE,
    FINAL_OBSTACLE_GAP_SIZE,
    NUM_POINTS_PER_GAP_SHRINK,
    MIN_DISTANCE_BOUNDARY_TO_GAP,
    DISTANCE_BETWEEN_OBSTACLES,
    OBSTACLE_COLOUR,
    DIGIT_GLYPHS,
    BIRD_SIZE,
    BIRD_FLAP_RISE_ROWS,
    OVERLAP_BIRD_COLOUR,
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
    def __init__(self, seed: int | None = None):
        # A seeded course is reproducible, so a run can be stored as its seed
        # plus its moves and rebuilt exactly for replay. No seed = the
        # course comes from RUN_MODE as before.
        self.seed = seed
        self.rng = random.Random(seed)
        self.screen = [
            [BACKGROUND_COLOUR for x in range(SCREEN_SIDE_LENGTH)]
            for y in range(SCREEN_SIDE_LENGTH)
        ]
        # Bird is BIRD_SIZExBIRD_SIZE square, tracked in row plane by top row
        self.bird_top_row_coord = BIRD_STARTING_TOP_ROW_COORD
        self.last_direction = "DOWN"
        self.current_velocity = 0
        self.score = 0
        # {col_idx, gap_top_idx, gap_bottom_idx}[] gap_top_idx and gap_bottom_idx
        # are the first and last open rows of the gap, inclusively.
        self.gaps = []
        self.game_ticks_elapsed = 0
        self.obstacles_generated = 0
        self.moves_thus_far = []
        self.bird_colour = BIRD_COLOUR
        # Purely for observation benefit. And signed to match the row
        # coordinate system: positive is falling, negative is rising.
        self.rounded_bird_velocity = 0

    def move_bird_vertically(self, input_this_tick: bool):
        bird_velocity, direction = self.bird_velocity_rows_per_tick_rounded(
            input_this_tick
        )
        # bird_velocity is an unsigned magnitude, so carry the direction into
        # the observation, else rising and falling look identical.
        self.rounded_bird_velocity = (
            -bird_velocity if direction == "UP" else bird_velocity
        )

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

        self.draw_current_bird_position(self.bird_colour)

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

    def bird_velocity_rows_per_tick_rounded(self, input_this_tick: bool):
        if input_this_tick:
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

    def on_tick(self, input_this_tick: bool):
        self.move_bird_vertically(input_this_tick)
        self.move_obstacles()
        if self.game_ticks_elapsed % DISTANCE_BETWEEN_OBSTACLES == 0:
            self.generate_new_obstacle()
        for gap in self.gaps:
            if gap["col_idx"] == BIRD_LEFT_COL_COORD - 1:
                self.score += 1
                break
        self.game_ticks_elapsed += 1

    def move_obstacles(self):
        for idx, gap in enumerate(self.gaps):
            col_idx = gap["col_idx"]
            for row_idx in range(gap["gap_top_idx"]):
                self.screen[row_idx][col_idx] = BACKGROUND_COLOUR
            for row_idx in range(gap["gap_bottom_idx"] + 1, SCREEN_SIDE_LENGTH):
                self.screen[row_idx][col_idx] = BACKGROUND_COLOUR
            self.gaps[idx]["col_idx"] -= 1

        def is_col_still_on_page(gap):
            return True if gap["col_idx"] >= 0 else False

        self.gaps = list(filter(is_col_still_on_page, self.gaps))

        for idx, gap in enumerate(self.gaps):
            col_idx = gap["col_idx"]
            for row_idx in range(gap["gap_top_idx"]):
                self.screen[row_idx][col_idx] = OBSTACLE_COLOUR
            for row_idx in range(gap["gap_bottom_idx"] + 1, SCREEN_SIDE_LENGTH):
                self.screen[row_idx][col_idx] = OBSTACLE_COLOUR

    def detect_game_over(self):
        if self.bird_top_row_coord == 0:  # Hit top of screen
            return True

        if (
            self.bird_top_row_coord == SCREEN_SIDE_LENGTH - BIRD_SIZE
        ):  # Hit bottom of screen
            return True

        #  Obstacle collision
        bird_col_coords = []
        for i in range(BIRD_SIZE):
            bird_col_coords.append(BIRD_LEFT_COL_COORD + i)

        potential_obstacle = None
        for idx, gap in enumerate(self.gaps):
            col_idx = gap["col_idx"]
            if col_idx in bird_col_coords:
                potential_obstacle = gap
                break

        if potential_obstacle is not None:
            bird_row_coords = []
            for i in range(BIRD_SIZE):
                bird_row_coords.append(self.bird_top_row_coord + i)

            for row_coord in bird_row_coords:
                if (
                    row_coord < potential_obstacle["gap_top_idx"]
                    or row_coord > potential_obstacle["gap_bottom_idx"]
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
        top_gap_row_idx_options = list(
            range(
                MIN_DISTANCE_BOUNDARY_TO_GAP,
                SCREEN_SIDE_LENGTH - MIN_DISTANCE_BOUNDARY_TO_GAP - gap_size + 1,
            )
        )

        if self.seed is not None:
            top_gap_row_idx = self.rng.choice(top_gap_row_idx_options)
        elif RUN_MODE == "RANDOM":
            top_gap_row_idx = random.choice(top_gap_row_idx_options)
        else:
            top_gap_row_idx = top_gap_row_idx_options[
                round(
                    TEST_OBSTACLE_DECIMALS[self.obstacles_generated]
                    * (len(top_gap_row_idx_options) - 1)
                )
            ]

        self.gaps.append(
            {
                "col_idx": SCREEN_SIDE_LENGTH - 1,
                "gap_top_idx": top_gap_row_idx,
                "gap_bottom_idx": top_gap_row_idx + gap_size - 1,
            }
        )
        self.obstacles_generated += 1

    # Environment will trigger game looping via direct game function calls
    def human_game_loop(self):
        # Current input listening only works on POSIX
        fd = sys.stdin.fileno()
        old_settings = termios.tcgetattr(fd)

        try:
            tty.setcbreak(fd)

            gameRunning = True

            self.draw_current_bird_position(self.bird_colour)
            while gameRunning:
                readable, _, _ = select.select([sys.stdin], [], [], 0)

                input_this_tick = False
                if readable:
                    while select.select([sys.stdin], [], [], 0)[0]:
                        key = sys.stdin.read(1)
                        if key == " ":
                            input_this_tick = True

                os.system("clear")

                self.moves_thus_far.append(input_this_tick)
                print(self.get_state())
                self.on_tick(input_this_tick)
                if self.detect_game_over() is True:
                    gameRunning = False
                self.print_screen(self.screen)

                time.sleep(MS_PER_GAME_TICK / 1000)
        finally:
            termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)

        os.system("clear")
        game_over_screen = self.create_game_over_screen([self])
        self.print_screen(game_over_screen)

        if RUN_MODE == "TEST":
            best_human_run_file = "./src/best_human_run.txt"
            with open(best_human_run_file, "r") as f:
                lines = f.read().splitlines()
            best_score = lines.pop(0)

            if self.score >= int(best_score):
                with open(best_human_run_file, "a") as f:
                    f.truncate(0)
                    f.write(str(self.score))
                    for move in self.moves_thus_far:
                        f.write("\n")
                        f.write(str(move))

    @classmethod
    def race_loop(cls, runs: list[tuple["Game", list[bool]]]):
        racing = list(runs)
        for game, _ in racing:
            game.draw_current_bird_position(game.bird_colour)

        while racing:
            for game, moves in racing:
                game.on_tick(moves[game.game_ticks_elapsed])
            racing = [
                (game, moves)
                for game, moves in racing
                if not game.detect_game_over() and game.game_ticks_elapsed < len(moves)
            ]

            # Only the survivor is drawn, so a bird vanishes as it fails
            if racing:
                os.system("clear")
                cls.print_screen(cls.compose_screens([game for game, _ in racing]))

            time.sleep(MS_PER_REPLAY_TICK / 1000)

        os.system("clear")
        cls.print_screen(cls.create_game_over_screen([game for game, _ in runs]))

    @staticmethod
    def compose_screens(games: list["Game"]) -> list[list[RGB]]:
        stage = max(games, key=lambda game: game.game_ticks_elapsed)
        screen = [row.copy() for row in stage.screen]

        for game in games:
            if game is stage:
                continue
            for row, col in game.get_all_bird_coords():
                screen[row][col] = (
                    OVERLAP_BIRD_COLOUR
                    if screen[row][col] == stage.bird_colour
                    else game.bird_colour
                )

        return screen

    @staticmethod
    def print_screen(screen):
        for row in screen:
            for cell in row:
                [red, green, blue] = cell

                print(
                    f"{ESCAPE}[{BCG};{RGB_MODE};{red};{green};{blue}m  {RESET}", end=""
                )

            print()

    @staticmethod
    def create_game_over_screen(games: list["Game"]) -> list[list[RGB]]:
        game_over_screen = [
            [BACKGROUND_COLOUR for x in range(SCREEN_SIDE_LENGTH)]
            for y in range(SCREEN_SIDE_LENGTH)
        ]

        score_num_cols = (
            SCORE_NUM_DIGITS * SCORE_DIGIT_NUM_COLS
            + (SCORE_NUM_DIGITS - 1) * SCORE_DIGIT_COL_GAP
        )
        score_num_rows = (
            len(games) * SCORE_DIGIT_NUM_ROWS + (len(games) - 1) * SCORE_DIGIT_ROW_GAP
        )
        starting_starter_row = (SCREEN_SIDE_LENGTH - score_num_rows) // 2
        starting_starter_col = (SCREEN_SIDE_LENGTH - score_num_cols) // 2

        for game_idx, game in enumerate(games):
            score = str(min(game.score, MAX_SCORE)).zfill(SCORE_NUM_DIGITS)
            score_row = starting_starter_row + game_idx * (
                SCORE_DIGIT_NUM_ROWS + SCORE_DIGIT_ROW_GAP
            )
            colour = game.bird_colour if len(games) > 1 else SCORE_COLOUR

            for idx, digit in enumerate(score):
                digit_col = starting_starter_col + idx * (
                    SCORE_DIGIT_NUM_COLS + SCORE_DIGIT_COL_GAP
                )

                for row_offset, glyph_row in enumerate(DIGIT_GLYPHS[digit]):
                    for col_offset, cell in enumerate(glyph_row):
                        if cell == "#":
                            game_over_screen[score_row + row_offset][
                                digit_col + col_offset
                            ] = colour

        return game_over_screen

    # Purely for benefit of Environment
    def get_state(self) -> list[int]:
        # State is list of:
        # 1) current row of middle of bird (asumming 3x3 at the moment)
        # 2) top gap row
        # 3) bottom gap row
        # 4) distance from right col of bird to col of next obstacle
        # 5) offset from centre of upcoming gap (minus if above, positive below)
        # measuring from middle of bird working with 3x3 at the moment
        # 6) bird velocity (should help bird to gauge how far fall next tick if free falling)
        # 7) offset from centre of the gap AFTER the upcoming one, 0 when there
        # isn't one on screen yet
        # 8) whether that gap after next is actually on screen, 1 or 0. Gaps
        # spawn every DISTANCE_BETWEEN_OBSTACLES ticks but stay ahead of the
        # bird for longer than that, so roughly half the time there is no gap
        # after next and 0 in 7) would otherwise read as "perfectly aligned"
        bird_middle_row = self.bird_top_row_coord + 1  # LIME: magic number? 3x3

        def offset_from_gap_centre(gap):
            return bird_middle_row - round(
                (gap["gap_top_idx"] + gap["gap_bottom_idx"]) / 2
            )

        # Gaps appended in order, so the upcoming ones stay in order too
        upcoming = [gap for gap in self.gaps if gap["col_idx"] > BIRD_LEFT_COL_COORD]

        if upcoming:
            gap = upcoming[0]
            gap_after_next_known = len(upcoming) > 1
            return [
                bird_middle_row,
                gap["gap_top_idx"],
                gap["gap_bottom_idx"],
                gap["col_idx"] - BIRD_LEFT_COL_COORD - BIRD_SIZE,
                offset_from_gap_centre(gap),
                self.rounded_bird_velocity,
                offset_from_gap_centre(upcoming[1]) if gap_after_next_known else 0,
                1 if gap_after_next_known else 0,
            ]

        # First observation on a given game
        return [
            self.bird_top_row_coord,
            MIN_DISTANCE_BOUNDARY_TO_GAP,
            SCREEN_SIDE_LENGTH - MIN_DISTANCE_BOUNDARY_TO_GAP,
            SCREEN_SIDE_LENGTH - BIRD_LEFT_COL_COORD,
            # Can't know as spawned after first observation, centre seems a
            # good a place as any for a single first obs
            0,
            0,
            0,
            0,
        ]
