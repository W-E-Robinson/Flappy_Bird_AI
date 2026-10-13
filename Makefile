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

# Best ever bot run, replayed on the seed it was actually scored on. The seed
# stored with the run rebuilds that course, so RUN_MODE does not apply.
replay-best-ever:
	REPLAY_MODE=BOT $(PYTHON) ./src/replay.py

replay-latest-model:
	REPLAY_MODE=LATEST_BOT RUN_MODE=TEST $(PYTHON) ./src/replay.py

replay-human:
	REPLAY_MODE=HUMAN RUN_MODE=TEST $(PYTHON) ./src/replay.py

replay-both:
	REPLAY_MODE=BOTH RUN_MODE=TEST $(PYTHON) ./src/replay.py

graph-session:
	GRAPH_MODE=SESSION $(PYTHON) ./src/graph.py

graph-test-run:
	GRAPH_MODE=TEST_RUN $(PYTHON) ./src/graph.py

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
