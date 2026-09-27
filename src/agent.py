import torch
from network import Network
import numpy as np
import gymnasium as gym


class Agent:
    """An agent that interacts with the cube environment, uses a Q-network to estimate action values and develop an action policy

    Attributes:
        env: Training environment to take actions, update cube state and return reward
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

    def get_action(self, obs: list[int]) -> int:
        if np.random.random() < self.epsilon:
            return self.env.action_space.sample()
        else:
            state = torch.tensor(obs, dtype=torch.float32)
            with torch.no_grad():
                q_values = self.network(state)

            return int(torch.argmax(q_values))

    def update(
        self,
        obs: list[int],
        action: int,
        reward: float,
        terminated: bool,
        next_obs: list[int],
    ):
        state = torch.tensor(obs, dtype=torch.float32)
        next_state = torch.tensor(next_obs, dtype=torch.float32)

        q_values = self.network(state)

        current_q = q_values[action]

        with torch.no_grad():
            next_q_values = self.target_network(next_state)
            # LIME: look into overestimation bias
            best_future_q = torch.max(next_q_values)

            target = reward + self.discount_factor * best_future_q * (not terminated)

        loss = (current_q - target) ** 2

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
