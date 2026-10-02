from gymnasium.wrappers import TimeLimit
from os import listdir
from agent import Agent
from env import Env
from tqdm import tqdm
from constants import NUM_TET_EPISODES


def run_attempt(env, agent):
    obs, _info = env.reset()

    done = False

    while not done:
        action = agent.get_action(obs)

        (
            next_obs,
            _reward,
            terminated,
            truncated,
            _info,
        ) = env.step(action)

        done = terminated or truncated
        obs = next_obs

    return agent.get_score()


def main():
    print("Running trained model")

    env = TimeLimit(Env(), max_episode_steps=10)

    agent = Agent(
        env=env,
        learning_rate=0.01,  # Constructor requires but redundant for running model
        initial_epsilon=0.0,  # Always best known when running model
        epsilon_decay=0.0,  # Constructor requires but redundant for running
        final_epsilon=0.0,  # Always best known when running model
        discount_factor=0.95,  # Constructor requires but redundant for running
    )

    models_list = sorted(
        file for file in listdir("./src/__models__/") if file.endswith(".pt")
    )
    latest_model = models_list[-1]
    model_path = f"./src/__models__/{latest_model}"

    print(f"Loading model: {model_path}")
    # Loads relative to where script run from
    agent.load(model_path)

    scores = []
    for range_idx in tqdm(range(NUM_TET_EPISODES)):
        scores.append(run_attempt(env, agent))

    num_attempts = NUM_TET_EPISODES
    print("Running finished")
    print(f"Total number of runs: {num_attempts}")
    print(f"Scores: {scores}")


if __name__ == "__main__":
    main()
