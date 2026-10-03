import gymnasium as gym
from game import Game
from typing import Optional
import numpy as np
from constants import (
    MAX_SCORE,
    INPUT_FEATURES,
    OUTPUT_SIZE,
    STARTING_OBSTACLE_GAP_SIZE,
)


class Env(gym.Env):
    def __init__(self):
        self.game = Game()
        self.moves = []

        # Observables are screen coordinates and a column distance, so the
        # screen bounds all of them
        self.observation_space = gym.spaces.Box(
            0.0,
            float(SCREEN_SIDE_LENGTH - 1),
            shape=(INPUT_FEATURES,),
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
