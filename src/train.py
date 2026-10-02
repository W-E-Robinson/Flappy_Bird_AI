from datetime import datetime
from tqdm import tqdm
from agent import Agent
from env import Env
import gymnasium as gym
from gymnasium.wrappers import TimeLimit
from constants import (
    MAX_EPISODE_STEPS,
    NUM_TRAINING_EPISODES,
    NUM_STEPS_TARGET_NETWORK_RESET,
    LEARNING_RATE,
    START_EPSILON,
    FINAL_EPSILON,
    DISCOUNT_FACTOR,
    MAX_SCORE,
    DISTANCE_BETWEEN_OBSTACLES,
)


def main():
    print("Initiating environment")
    n_episodes = NUM_TRAINING_EPISODES
    env = gym.wrappers.RecordEpisodeStatistics(
        # Enough to clear max score possible
        TimeLimit(Env(), max_episode_steps=MAX_EPISODE_STEPS),
        buffer_length=n_episodes,
    )

    print("Initiating agent")
    learning_rate = LEARNING_RATE
    start_epsilon = START_EPSILON
    epsilon_decay = start_epsilon / n_episodes
    final_epsilon = FINAL_EPSILON
    agent = Agent(
        env=env,
        learning_rate=learning_rate,
        initial_epsilon=start_epsilon,
        epsilon_decay=epsilon_decay,
        final_epsilon=final_epsilon,
        discount_factor=DISCOUNT_FACTOR,
    )

    num_steps = 0

    print(f"Beginning training, number of episodes: {n_episodes}")
    for episode in tqdm(range(n_episodes)):
        obs, _info = env.reset()
        done = False

        while not done:
            action = agent.get_action(obs)

            (
                next_obs,
                reward,
                terminated,
                truncated,
                _info,
            ) = env.step(action)

            agent.update(obs, action, float(reward), terminated, next_obs)

            done = terminated or truncated
            obs = next_obs

            num_steps += 1
            if num_steps % NUM_STEPS_TARGET_NETWORK_RESET == 0:
                agent.resync_target_network()

        agent.decay_epsilon()

    print("Training ended")

    timestamp = datetime.now().strftime("%Y_%m_%d_%H_%M_%S")
    # Saves relative to where script run from
    # model file name indicates: timestamp, scramble depth, number of training episodes
    model_path = f"./src/__models__/{timestamp}-{n_episodes}.pt"
    print(f"Saving model to: {model_path}")
    agent.save(model_path)


if __name__ == "__main__":
    main()
