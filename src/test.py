import gymnasium as gym
from os import listdir
from agent import Agent
from env import ENV_ID
from tqdm import tqdm
from constants import NUM_TEST_EPISODES


def run_attempt(env, agent):
    obs, info = env.reset()

    done = False

    while not done:
        action = agent.get_action(obs)

        (
            next_obs,
            _reward,
            terminated,
            truncated,
            info,
        ) = env.step(action)

        done = terminated or truncated
        obs = next_obs

    return info


def main():
    print("Running trained model")

    env = gym.make(ENV_ID)

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

    best_info = {"score": 0, "moves": []}
    for range_idx in tqdm(range(NUM_TEST_EPISODES)):
        info = run_attempt(env, agent)
        if info["score"] >= best_info["score"]:
            best_info = info

    num_attempts = NUM_TEST_EPISODES
    print("Running finished")
    print(f"Total number of runs: {num_attempts}")
    print(f"Best run score: {best_info['score']}")
    print(f"Best run moves: {best_info['moves']}")
    with open("./src/latest_best_run.txt", "a") as f:
        f.truncate(0)
        f.write(str(best_info["score"]))
        for move in best_info["moves"]:
            f.write("\n")
            f.write(str(move))

    best_bot_run_file = "./src/best_bot_run.txt"
    with open(best_bot_run_file, "r") as f:
        lines = f.read().splitlines()
    best_score = lines.pop(0)

    if best_info["score"] >= int(best_score):
        with open(best_bot_run_file, "a") as f:
            f.truncate(0)
            f.write(str(best_info["score"]))
            for move in best_info["moves"]:
                f.write("\n")
                f.write(str(move))


if __name__ == "__main__":
    main()
