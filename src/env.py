import gymnasium as gym
from game import Game
import numpy as np
from constants import (
    INPUT_FEATURES,
    OUTPUT_SIZE,
)


class Env(gym.Env):
    def __init__(self):
        self.game = Game()

        self.observation_space = gym.spaces.Box(
            0.0,
            1.0,  # LIME: new upper bound should be?
            shape=(INPUT_FEATURES,),
            dtype=np.float32,
        )

        self.action_space = gym.spaces.Discrete(OUTPUT_SIZE)

        self._action_to_input = {
            0: True,
            1: False,
        }
