from game import Game


def str_to_bool(value):
    return value.strip().lower() == "true"


def main():
    game = Game()
    with open("./src/latest_best_run.txt", "r") as f:
        lines = f.read().splitlines()
    score = lines.pop(0)
    game.repeat_loop(int(score), list(map(lambda x: str_to_bool(x), lines)))


if __name__ == "__main__":
    main()
