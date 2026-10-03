from constants import (
    REPLAY_MODE,
    BOT_BIRD_COLOUR,
    BIRD_COLOUR,
)
from game import Game


def str_to_bool(value):
    return value.strip().lower() == "true"


def main():
    game = Game()
    if REPLAY_MODE == "BOT":
        file = "src/latest_best_run.txt"
        colour = BOT_BIRD_COLOUR
    elif REPLAY_MODE == "HUMAN":
        file = "src/best_human_run.txt"
        colour = BIRD_COLOUR
    else:
        file = "bob"

    with open(file, "r") as f:
        lines = f.read().splitlines()
    score = lines.pop(0)
    game.repeat_loop(int(score), list(map(lambda x: str_to_bool(x), lines)), colour)


if __name__ == "__main__":
    main()
