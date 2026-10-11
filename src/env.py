import gymnasium as gym
from game import Game
from typing import Optional
import numpy as np
from constants import (
    MIN_DISTANCE_BOUNDARY_TO_GAP,
    FINAL_OBSTACLE_GAP_SIZE,
    BIRD_SIZE,
    MAX_SCORE,
    MAX_EPISODE_STEPS,
    INPUT_FEATURES,
    OUTPUT_SIZE,
    SCREEN_SIDE_LENGTH,
    BIRD_LEFT_COL_COORD,
    VERTITCAL_VELOCITY_CLAMP_ROWS_PER_TICK,
    BIRD_FLAP_RISE_ROWS,
)

ENV_ID = "Flappy-v2"


class Env(gym.Env):
    def __init__(self):
        self.game = Game()
        self.moves = []
        self.prev_score = 0

        bird_mid_row_min = 0
        bird_mid_row_max = SCREEN_SIDE_LENGTH - BIRD_SIZE + 1
        gap_top_min = MIN_DISTANCE_BOUNDARY_TO_GAP
        gap_bottom_max = SCREEN_SIDE_LENGTH - MIN_DISTANCE_BOUNDARY_TO_GAP

        obs_space_ranges = [
            # current row of middle of bird
            [bird_mid_row_min, bird_mid_row_max],
            # top gap row
            [
                gap_top_min,
                SCREEN_SIDE_LENGTH
                - MIN_DISTANCE_BOUNDARY_TO_GAP
                - FINAL_OBSTACLE_GAP_SIZE,
            ],
            # bottom gap row, gap_size - 1 rows below the top gap row
            [
                MIN_DISTANCE_BOUNDARY_TO_GAP + FINAL_OBSTACLE_GAP_SIZE - 1,
                gap_bottom_max,
            ],
            # distance from right col of bird to col of next obstacle
            [-2, SCREEN_SIDE_LENGTH - BIRD_LEFT_COL_COORD],  # -2 when in gap
            # offset from centre of upcoming gap. The gap centre always sits
            # between the top and bottom gap rows, so those bound the offset.
            [bird_mid_row_min - gap_bottom_max, bird_mid_row_max - gap_top_min],
            # bird velocity, negative while rising
            [-BIRD_FLAP_RISE_ROWS, VERTITCAL_VELOCITY_CLAMP_ROWS_PER_TICK],
        ]

        self._obs_low = np.array([r[0] for r in obs_space_ranges], dtype=np.float32)
        self._obs_high = np.array([r[1] for r in obs_space_ranges], dtype=np.float32)
        self._obs_range = self._obs_high - self._obs_low

        self.observation_space = gym.spaces.Box(
            low=-1.0,
            high=1.0,
            shape=(INPUT_FEATURES,),
            dtype=np.float32,
        )

        self.action_space = gym.spaces.Discrete(OUTPUT_SIZE)

        self._action_to_input = {
            0: True,
            1: False,
        }

    def _get_obs(self) -> np.ndarray:
        # Scale every feature to [-1, 1] so none dominates the networks input
        # layer, this stopped velocity of max 4 getting made invisible out by rows spans
        # in other observables.
        raw = np.array(self.game.get_state(), dtype=np.float32)
        scaled = 2.0 * (raw - self._obs_low) / self._obs_range - 1.0
        return np.clip(scaled, -1.0, 1.0).astype(np.float32)

    # Returns current score and cumulation of action per tick
    def _get_info(self):
        return {
            "score": self.game.score,
            "moves": self.moves,
        }

    def step(self, action):
        move = self._action_to_input[action]
        self.moves.append(move)
        self.game.on_tick(move)

        state = self.game.get_state()

        reward = 0

        # Encourage alignment with the centre of the gap
        if abs(state[4]) == 0:  # LIME: refactor into dict, I change to abs too
            reward += 0.2
        elif abs(state[4]) == 1:
            # LIME: what if clipping bottom because starts to see next one?
            # make it hug the top end more?
            reward += 0.15
        elif abs(state[4]) == 2:
            reward += 0.05
        else:
            reward -= 0.1
            # LIME: need test reward and get state from now on

        # Reward successfully passing the gap
        scored = self.game.score > self.prev_score
        self.prev_score = self.game.score
        if scored:
            reward += 1

        won = self.game.score == MAX_SCORE
        game_over = self.game.detect_game_over() and not won

        # After realignment of rewards a fast death must still be worse than an accrued
        # negative rewards from misalignment relative to centre
        if game_over:
            reward -= 5

        terminated = game_over or won
        truncated = False

        observation = self._get_obs()
        info = self._get_info()

        return observation, reward, terminated, truncated, info

    def reset(
        self,
        *,
        seed: Optional[int] = None,
        options: Optional[dict] = None,
    ):
        super().reset(seed=seed)

        self.game = Game()
        self.moves = []
        self.prev_score = 0

        # Built after the new game, so info describes the episode being
        # started rather than the one just finished.
        info = self._get_info()
        observation = self._get_obs()

        return observation, info


gym.register(
    id=ENV_ID,
    entry_point="env:Env",
    max_episode_steps=MAX_EPISODE_STEPS,
)
