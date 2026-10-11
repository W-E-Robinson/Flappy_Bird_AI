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
)

ENV_ID = "Flappy-v2"


class Env(gym.Env):
    def __init__(self):
        self.game = Game()
        self.moves = []
        self.prev_score = 0

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
            # offset from centre of upcoming gap
            [-(SCREEN_SIDE_LENGTH / 2), SCREEN_SIDE_LENGTH / 2],
            # bird velocity
            [0, VERTITCAL_VELOCITY_CLAMP_ROWS_PER_TICK],
        ]
        self.observation_space = gym.spaces.Box(
            low=np.array(
                [
                    obs_space_ranges[0][0],
                    obs_space_ranges[1][0],
                    obs_space_ranges[2][0],
                    obs_space_ranges[3][0],
                    obs_space_ranges[4][0],
                    obs_space_ranges[5][0],
                ],
                dtype=np.float32,
            ),
            high=np.array(
                [
                    obs_space_ranges[0][1],
                    obs_space_ranges[1][1],
                    obs_space_ranges[2][1],
                    obs_space_ranges[3][1],
                    obs_space_ranges[4][1],
                    obs_space_ranges[5][1],
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

        reward = 0

        # Encourage alignment with the centre of the gap
        if abs(state[4]) == 0:  # LIME: refactor into dict, I change to abs too
            reward += 5
        elif abs(state[4]) == 1:
            # LIME: what if clipping bottom because starts to see next one?
            # make it hug the top end more?
            reward += 3
        elif abs(state[4]) == 2:
            reward += 1
        else:
            reward -= 2
            # LIME: need test reward and get state from now on

        # Reward successfully passing the gap
        scored = self.game.score > self.prev_score
        self.prev_score = self.game.score
        if scored:
            reward += 20

        # Death and reaching MAX_SCORE both end the MDP, so both are
        # terminated. Truncation is reserved for the TimeLimit wrapper's step
        # cap, which is a cutoff rather than a real end state - the agent must
        # keep bootstrapping through those, but never through a death.
        won = self.game.score == MAX_SCORE
        game_over = self.game.detect_game_over() and not won

        # Penalise game over
        if game_over:
            reward -= 100

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
