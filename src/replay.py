from typing import NamedTuple
from constants import (
    REPLAY_MODE,
    BOT_BIRD_COLOUR,
    BIRD_COLOUR,
    RGB,
)
from game import Game

LATEST_BOT = ("src/latest_best_run.txt", BOT_BIRD_COLOUR)
BOT_RUN = ("src/best_bot_run.txt", BOT_BIRD_COLOUR)
HUMAN_RUN = ("src/best_human_run.txt", BIRD_COLOUR)
RUNS_PER_REPLAY_MODE = {
    "LATEST_BOT": [LATEST_BOT],
    "BOT": [BOT_RUN],
    "HUMAN": [HUMAN_RUN],
    "BOTH": [BOT_RUN, HUMAN_RUN],
}


class Run(NamedTuple):
    file: str
    game: Game
    moves: list[bool]
    recorded_score: int


def str_to_bool(value):
    return value.strip().lower() == "true"


def load_run(file: str, colour: RGB) -> Run:
    with open(file, "r") as f:
        lines = f.read().splitlines()
    recorded_score = int(lines.pop(0))

    seed = None
    if lines and lines[0].strip().lower() not in ("true", "false"):
        seed = int(lines.pop(0))

    game = Game(seed=seed)
    game.bird_colour = colour
    return Run(file, game, [str_to_bool(line) for line in lines], recorded_score)


def main():
    runs = [
        load_run(file, colour) for file, colour in RUNS_PER_REPLAY_MODE[REPLAY_MODE]
    ]
    Game.race_loop([(run.game, run.moves) for run in runs])


if __name__ == "__main__":
    main()
