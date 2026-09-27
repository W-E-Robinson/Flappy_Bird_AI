import gymnasium as gym
from game import Game
import numpy as np
from constants import (
    INPUT_FEATURES,
    NUM_POSSIBLE_MOVES,
)


class Env(gym.Env):
    def __init__(self):
        self.game = Game()

        self.observation_space = gym.spaces.Box(
            0.0,
            1.0,
            shape=(INPUT_FEATURES,),
            dtype=np.float32,
        )

        self.action_space = gym.spaces.Discrete(NUM_POSSIBLE_MOVES)

        self._action_to_input = {
            0: True,
            1: False,
        }
