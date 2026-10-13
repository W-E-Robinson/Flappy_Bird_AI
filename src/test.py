import gymnasium as gym
from os import listdir
from statistics import mean, median
from agent import Agent
from env import ENV_ID
from tqdm import tqdm
from constants import NUM_TEST_EPISODES, TEST_SEED_START

TEST_SCORES_FILE = "./src/scores_last_test_run.txt"
LATEST_BEST_RUN_FILE = "./src/latest_best_run.txt"
BEST_BOT_RUN_FILE = "./src/best_bot_run.txt"


def run_attempt(env, agent, seed: int):
    obs, info = env.reset(seed=seed)

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


# Median is what to compare models by, the max being an order statistic that
# mostly reflects how many courses were run
def report_scores(scores: list[int]):
    ranked = sorted(scores)
    n = len(ranked)

    def percentile(fraction):
        return ranked[min(n - 1, int(fraction * n))]

    print(f"  median {median(scores):.1f}   mean {mean(scores):.2f}")
    print(
        f"  p10 {percentile(0.10)}   p25 {percentile(0.25)}   "
        f"p75 {percentile(0.75)}   p90 {percentile(0.90)}"
    )
    print(f"  min {ranked[0]}   max {ranked[-1]}   zeros {scores.count(0)}/{n}")


def write_run(file_path: str, score: int, seed: int, moves: list[bool]):
    with open(file_path, "w") as f:
        f.write(str(score))
        f.write("\n")
        f.write(str(seed))
        for move in moves:
            f.write("\n")
            f.write(str(move))


def read_best_score(file_path: str) -> int:
    with open(file_path, "r") as f:
        return int(f.read().splitlines()[0])


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

    best_info = {"score": -1, "moves": []}
    best_seed = TEST_SEED_START
    scores = []

    seeds = range(TEST_SEED_START, TEST_SEED_START + NUM_TEST_EPISODES)
    for seed in tqdm(seeds):
        info = run_attempt(env, agent, seed)
        scores.append(info["score"])
        if info["score"] > best_info["score"]:
            best_info = info
            best_seed = seed

    print("Running finished")
    print(f"Total number of courses: {NUM_TEST_EPISODES}")
    report_scores(scores)
    print(f"Best run score: {best_info['score']} (seed {best_seed})")

    with open(TEST_SCORES_FILE, "w") as f:
        print(f"Writing scores to {TEST_SCORES_FILE}")
        for score in scores:
            f.write(str(score))
            f.write("\n")

    write_run(LATEST_BEST_RUN_FILE, best_info["score"], best_seed, best_info["moves"])

    if best_info["score"] >= read_best_score(BEST_BOT_RUN_FILE):
        print(f"New best ever bot run, writing to {BEST_BOT_RUN_FILE}")
        write_run(BEST_BOT_RUN_FILE, best_info["score"], best_seed, best_info["moves"])


if __name__ == "__main__":
    main()
