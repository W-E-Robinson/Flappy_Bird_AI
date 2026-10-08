VENV := .venv
PYTHON := $(VENV)/bin/python
PIP := $(VENV)/bin/pip
BLACK := $(VENV)/bin/black
PYRIGHT := $(VENV)/bin/pyright
PYTEST := $(VENV)/bin/pytest

play:
	RUN_MODE=RANDOM $(PYTHON) ./src/play.py

play-test:
	RUN_MODE=TEST $(PYTHON) ./src/play.py

train-model:
	RUN_MODE=RANDOM $(PYTHON) ./src/train.py

test-model:
	RUN_MODE=TEST $(PYTHON) ./src/test.py

train-test-model: train-model test-model

replay-model:
	REPLAY_MODE=BOT RUN_MODE=TEST $(PYTHON) ./src/replay.py

replay-human:
	REPLAY_MODE=HUMAN RUN_MODE=TEST $(PYTHON) ./src/replay.py

replay-both:
	REPLAY_MODE=BOTH RUN_MODE=TEST $(PYTHON) ./src/replay.py

clear-models:
	$(PYTHON) ./src/__models__/clear_models.py

venv:
	python3 -m venv $(VENV)

requirements: venv
	$(PIP) install -r requirements.txt

unit-test: requirements
	$(PYTEST) .

format: requirements
	$(BLACK) .

check: requirements
	$(PYRIGHT) .

style: format check
