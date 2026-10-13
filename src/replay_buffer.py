from collections import deque
import random
import numpy as np
import torch


class ReplayBuffer:
    """Fixed-size FIFO store of past transitions, sampled at random.

    Breaks the correlation between consecutive game ticks (which are nearly
    identical and distance of 20 between obstacles) and lets rare informative
    transitions, deaths + gap passes, be learned from many times instead of once

    Attributes:
        buffer: deque of (obs, action, reward, next_obs, done), oldest evicted
            once capacity is reached
    """

    def __init__(self, capacity: int):
        self.buffer = deque(maxlen=capacity)

    def push(
        self,
        obs: np.ndarray,
        action: int,
        reward: float,
        next_obs: np.ndarray,
        done: bool,
    ):
        self.buffer.append(
            (
                np.array(obs, dtype=np.float32),
                action,
                reward,
                np.array(next_obs, dtype=np.float32),
                done,
            )
        )

    def sample(self, batch_size: int):
        batch = random.sample(self.buffer, batch_size)
        obs, actions, rewards, next_obs, dones = zip(*batch)

        return (
            torch.tensor(np.array(obs), dtype=torch.float32),
            torch.tensor(actions, dtype=torch.int64),
            torch.tensor(rewards, dtype=torch.float32),
            torch.tensor(np.array(next_obs), dtype=torch.float32),
            torch.tensor(dones, dtype=torch.float32),
        )

    def __len__(self):
        return len(self.buffer)
