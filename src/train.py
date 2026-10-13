from datetime import datetime
from tqdm import tqdm
from agent import Agent
from env import ENV_ID
import gymnasium as gym
from constants import (
    NUM_TRAINING_EPISODES,
    NUM_STEPS_TARGET_NETWORK_RESET,
    LEARNING_RATE,
    START_EPSILON,
    FINAL_EPSILON,
    EPSILON_DECAY_FRACTION,
    DISCOUNT_FACTOR,
    MAX_SCORE,
    DISTANCE_BETWEEN_OBSTACLES,
)


def main():
    print("Initiating environment")
    n_episodes = NUM_TRAINING_EPISODES
    env = gym.wrappers.RecordEpisodeStatistics(
        gym.make(ENV_ID),
        buffer_length=n_episodes,
    )

    print("Initiating agent")
    learning_rate = LEARNING_RATE
    start_epsilon = START_EPSILON
    final_epsilon = FINAL_EPSILON
    # Paced over the distance epsilon actually travels, not the whole of
    # start_epsilon, so it lands on the floor exactly as the decay phase ends
    epsilon_decay = (start_epsilon - final_epsilon) / (
        n_episodes * EPSILON_DECAY_FRACTION
    )
    agent = Agent(
        env=env,
        learning_rate=learning_rate,
        initial_epsilon=start_epsilon,
        epsilon_decay=epsilon_decay,
        final_epsilon=final_epsilon,
        discount_factor=DISCOUNT_FACTOR,
    )

    num_steps = 0

    training_scores = []
    print(f"Beginning training, number of episodes: {n_episodes}")
    for episode in tqdm(range(n_episodes)):
        obs, info = env.reset()
        done = False

        while not done:
            action = agent.get_action(obs)

            (
                next_obs,
                reward,
                terminated,
                truncated,
                info,
            ) = env.step(action)

            agent.update(obs, action, float(reward), terminated, next_obs)

            done = terminated or truncated
            obs = next_obs

            num_steps += 1
            if num_steps % NUM_STEPS_TARGET_NETWORK_RESET == 0:
                agent.resync_target_network()

        agent.decay_epsilon()
        training_scores.append(info["score"])

    print("Training ended")

    with open("./src/scores_last_test_session.txt", "a") as f:
        print("Writing to scores_last_test_session.txt")
        f.truncate(0)
        for score in training_scores:
            f.write(str(score))
            f.write("\n")

    timestamp = datetime.now().strftime("%Y_%m_%d_%H_%M_%S")
    # Saves relative to where script run from
    # model file name indicates: timestamp, scramble depth, number of training episodes
    model_path = f"./src/__models__/{timestamp}-{n_episodes}.pt"
    print(f"Saving model to: {model_path}")
    agent.save(model_path)


if __name__ == "__main__":
    main()
