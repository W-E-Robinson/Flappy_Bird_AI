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
)

ENV_ID = "Flappy-v2"


class Env(gym.Env):
    def __init__(self):
        self.game = Game()
        self.moves = []

        obs_space_ranges = [
            # current row of top of bird
            [0, SCREEN_SIDE_LENGTH - BIRD_SIZE],
            # top gap row
            [
                MIN_DISTANCE_BOUNDARY_TO_GAP,
                SCREEN_SIDE_LENGTH
                - MIN_DISTANCE_BOUNDARY_TO_GAP
                - FINAL_OBSTACLE_GAP_SIZE
                + 1,
            ],
            # bottom gap row
            [
                MIN_DISTANCE_BOUNDARY_TO_GAP + FINAL_OBSTACLE_GAP_SIZE,
                SCREEN_SIDE_LENGTH - MIN_DISTANCE_BOUNDARY_TO_GAP,
            ],
            # distance from right col of bird to col of next obstacle
            [1, SCREEN_SIDE_LENGTH - BIRD_LEFT_COL_COORD],
        ]
        self.observation_space = gym.spaces.Box(
            low=np.array(
                [
                    obs_space_ranges[0][0],
                    obs_space_ranges[1][0],
                    obs_space_ranges[2][0],
                    obs_space_ranges[3][0],
                ],
                dtype=np.float32,
            ),
            high=np.array(
                [
                    obs_space_ranges[0][1],
                    obs_space_ranges[1][1],
                    obs_space_ranges[2][1],
                    obs_space_ranges[3][1],
                ],
                dtype=np.float32,
            ),
            dtype=np.float32,
        )

        self.action_space = gym.spaces.Discrete(OUTPUT_SIZE)

        self._action_to_input = {
            0: True,
            1: False,
        }

    def _get_obs(self) -> np.ndarray:
        return np.array(self.game.get_state(), dtype=np.float32)

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
        reward = -1
        # Weakly encouraging to stay centre
        if state[0] == 20:
            reward += 5
        # Strongly encouraging to go through gap
        if state[3] == 19:  # Just went past gap
            reward += 25

        truncated = self.game.detect_game_over() and self.game.score != MAX_SCORE
        if truncated:
            reward -= 100

        terminated = self.game.score == MAX_SCORE

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

        observation = self._get_obs()
        info = self._get_info()

        return observation, info


gym.register(
    id=ENV_ID,
    entry_point="env:Env",
    max_episode_steps=MAX_EPISODE_STEPS,
)
