from os import listdir, remove


def main():
    print("Clearing trained models")

    models_list = sorted(
        file for file in listdir("./src/__models__/") if file.endswith(".pt")
    )

    for model in models_list:
        print(f"Clearing model: {model}")
        remove(f"./src/__models__/{model}")

    print("Clearing finished")
    print(f"Total number of models cleared: {len(models_list)}")


if __name__ == "__main__":
    main()
