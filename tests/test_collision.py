"""Collision rules.

Two gama over rules are being tested here:
1) The ceiling and the floor kill on contact. The bird does not have to
   overshoot them, occupying the outermost row is already fatal.
2) A pillar only kills when the bird actually overlaps it. Sharing rows with a
   pillar that is not in the bird's columns is safe, and so is sharing columns
   with a pillar whose gap the bird fits inside.
"""

import pytest
from game import Game
from constants import (
    SCREEN_SIDE_LENGTH,
    BIRD_SIZE,
    BIRD_LEFT_COL_COORD,
    BIRD_STARTING_TOP_ROW_COORD,
)

CEILING_ROW = 0
# Bird top row when it sits on the floor
FLOOR_TOP_ROW = SCREEN_SIDE_LENGTH - BIRD_SIZE

# A gap the bird (assuming size of 3) fits inside with one row of slack either side
GAP_TOP = 10
GAP_BOTTOM = 14

# Columns the bird occupies, so the columns a pillar can collide in
BIRD_COLS = list(range(BIRD_LEFT_COL_COORD, BIRD_LEFT_COL_COORD + BIRD_SIZE))


def game_with_pillar(
    bird_top_row: int,
    col_idx: int = BIRD_LEFT_COL_COORD,
    gap_top: int = GAP_TOP,
    gap_bottom: int = GAP_BOTTOM,
) -> Game:
    """A game with the bird parked at a row and exactly one pillar on screen."""
    game = Game()
    game.bird_top_row_coord = bird_top_row
    game.gaps = [
        {"col_idx": col_idx, "gap_top_idx": gap_top, "gap_bottom_idx": gap_bottom}
    ]
    return game


def game_with_no_pillars(bird_top_row: int) -> Game:
    game = Game()
    game.bird_top_row_coord = bird_top_row
    game.gaps = []
    return game


class TestCeilingAndFloor:
    """Touching is failing - no overshoot required."""

    def test_touching_the_ceiling_row_is_game_over(self):
        assert game_with_no_pillars(CEILING_ROW).detect_game_over() is True

    def test_touching_the_floor_row_is_game_over(self):
        assert game_with_no_pillars(FLOOR_TOP_ROW).detect_game_over() is True

    def test_one_row_clear_of_the_ceiling_survives(self):
        assert game_with_no_pillars(CEILING_ROW + 1).detect_game_over() is False

    def test_one_row_clear_of_the_floor_survives(self):
        assert game_with_no_pillars(FLOOR_TOP_ROW - 1).detect_game_over() is False

    @pytest.mark.parametrize("bird_top_row", range(CEILING_ROW + 1, FLOOR_TOP_ROW))
    def test_every_row_between_the_two_survives(self, bird_top_row: int):
        assert game_with_no_pillars(bird_top_row).detect_game_over() is False

    def test_falling_lands_exactly_on_the_floor_row_and_dies(self):
        """Gravity overshoots the floor, so prove the clamp lands on the fatal
        row rather than past it. This is the rule reached through real play
        rather than by assigning a coordinate."""
        game = game_with_no_pillars(BIRD_STARTING_TOP_ROW_COORD)

        ticks = 0
        while not game.detect_game_over():
            game.on_tick(False)  # No flap, so free fall
            # on_tick spawns obstacles, so keep the screen clear and leave the
            # floor as the only thing that can end this run
            game.gaps = []
            ticks += 1
            assert ticks < SCREEN_SIDE_LENGTH, "Bird never reached the floor"

        assert game.bird_top_row_coord == FLOOR_TOP_ROW

    def test_flapping_lands_exactly_on_the_ceiling_row_and_dies(self):
        game = game_with_no_pillars(BIRD_STARTING_TOP_ROW_COORD)

        ticks = 0
        while not game.detect_game_over():
            game.on_tick(True)  # Flap every tick, so climb
            game.gaps = []  # Leave the ceiling as the only thing that can end this run
            ticks += 1
            assert ticks < SCREEN_SIDE_LENGTH, "Bird never reached the ceiling"

        assert game.bird_top_row_coord == CEILING_ROW


class TestPillarCollision:
    """Overlap is failing, sharing rows or columns alone is not."""

    @pytest.mark.parametrize(
        "bird_top_row", [GAP_TOP, GAP_TOP + 1, GAP_BOTTOM - BIRD_SIZE + 1]
    )
    def test_bird_fully_inside_the_gap_survives(self, bird_top_row: int):
        assert game_with_pillar(bird_top_row).detect_game_over() is False

    def test_clipping_the_gap_by_one_row_from_above_is_game_over(self):
        """Bird's top row sits one row above the gap, the other two are inside."""
        assert game_with_pillar(GAP_TOP - 1).detect_game_over() is True

    def test_clipping_the_gap_by_one_row_from_below_is_game_over(self):
        """Bird's bottom row sits one row below the gap, the other two are inside."""
        assert game_with_pillar(GAP_BOTTOM - BIRD_SIZE + 2).detect_game_over() is True

    def test_bird_entirely_above_the_gap_is_game_over(self):
        assert game_with_pillar(GAP_TOP - BIRD_SIZE - 2).detect_game_over() is True

    def test_bird_entirely_below_the_gap_is_game_over(self):
        assert game_with_pillar(GAP_BOTTOM + 2).detect_game_over() is True

    @pytest.mark.parametrize("col_idx", BIRD_COLS)
    def test_collision_detected_in_every_column_the_bird_occupies(self, col_idx: int):
        game = game_with_pillar(GAP_BOTTOM + 2, col_idx=col_idx)
        assert game.detect_game_over() is True

    @pytest.mark.parametrize("col_idx", [BIRD_LEFT_COL_COORD - 1, BIRD_COLS[-1] + 1])
    def test_misaligned_bird_survives_a_pillar_outside_its_columns(self, col_idx: int):
        """Badly misaligned on rows, but the pillar is one column shy of the bird
        on either side, so there is no overlap and no collision."""
        game = game_with_pillar(GAP_BOTTOM + 2, col_idx=col_idx)
        assert game.detect_game_over() is False

    def test_pillar_scrolling_into_the_bird_turns_safe_into_game_over(self):
        """The moment of collision: one tick of scrolling moves the pillar from
        just clear of the bird's columns into them."""
        game = game_with_pillar(GAP_BOTTOM + 2, col_idx=BIRD_COLS[-1] + 1)
        assert game.detect_game_over() is False

        game.move_obstacles()

        assert game.gaps[0]["col_idx"] == BIRD_COLS[-1]
        assert game.detect_game_over() is True
