import torch
from network import Network
from replay_buffer import ReplayBuffer
import numpy as np
import gymnasium as gym
from constants import (
    REPLAY_BUFFER_CAPACITY,
    REPLAY_BATCH_SIZE,
    MIN_REPLAY_BUFFER_SIZE,
)


class Agent:
    """An agent that interacts with the game environment, uses a Q-network to estimate action values and develop an action policy

    Attributes:
        env: Training environment to take actions, update game state and return reward
        buffer: Replay buffer of past transitions, sampled in batches to train on
        network: Q-network to evaluate possible actions
        learning_rate (float): Controls Q-network adjustment based on new experience
        optimizer: Use Adam optimization alg to update network weights, using the learning_rate
        discount_factor (float): Relative value of future rewards compared with immediate reward
        epsilon (float): Establishes random action vs best known action (1 - epsilon = best known)
        epsilon_decay (float): How much to reduce epsilon each episode
        final_epsilon (float): Minimum exploration rate
    """

    def __init__(
        self,
        env: gym.Env,
        learning_rate: float,
        initial_epsilon: float,
        epsilon_decay: float,
        final_epsilon: float,
        discount_factor: float,
    ):
        self.env = env
        self.buffer = ReplayBuffer(REPLAY_BUFFER_CAPACITY)
        self.network = Network()
        self.target_network = Network()
        self.resync_target_network()
        self.learning_rate = learning_rate
        self.optimizer = torch.optim.Adam(
            self.network.parameters(), lr=self.learning_rate
        )
        self.discount_factor = discount_factor
        self.epsilon = initial_epsilon
        self.epsilon_decay = epsilon_decay
        self.final_epsilon = final_epsilon

    def get_action(self, obs: np.ndarray) -> int:
        if np.random.random() < self.epsilon:
            return self.env.action_space.sample()
        else:
            state = torch.tensor(obs, dtype=torch.float32)
            with torch.no_grad():
                q_values = self.network(state)

            return int(torch.argmax(q_values))

    def update(
        self,
        obs: np.ndarray,
        action: int,
        reward: float,
        terminated: bool,
        next_obs: np.ndarray,
    ):
        self.buffer.push(obs, action, reward, next_obs, terminated)

        if len(self.buffer) < MIN_REPLAY_BUFFER_SIZE:
            return

        (
            obs_batch,
            action_batch,
            reward_batch,
            next_obs_batch,
            done_batch,
        ) = self.buffer.sample(REPLAY_BATCH_SIZE)

        q_values = self.network(obs_batch)
        current_q = q_values.gather(1, action_batch.unsqueeze(1)).squeeze(1)

        with torch.no_grad():
            next_q_values = self.target_network(next_obs_batch)
            best_future_q = next_q_values.max(dim=1).values

            target = reward_batch + self.discount_factor * best_future_q * (
                1.0 - done_batch
            )

        loss = ((current_q - target) ** 2).mean()

        self.optimizer.zero_grad()
        loss.backward()
        self.optimizer.step()

    def decay_epsilon(self):
        self.epsilon = max(self.final_epsilon, self.epsilon - self.epsilon_decay)

    def save(self, model_path: str):
        torch.save(self.network.state_dict(), model_path)

    def load(self, model_path: str):
        self.network.load_state_dict(torch.load(model_path))
        self.network.eval()

    def resync_target_network(self):
        self.target_network.load_state_dict(self.network.state_dict())
        self.target_network.eval()
        self.target_network.requires_grad_(False)
