VENV := .venv
PYTHON := $(VENV)/bin/python
PIP := $(VENV)/bin/pip
BLACK := $(VENV)/bin/black
PYRIGHT := $(VENV)/bin/pyright

play:
	RUN_MODE=RANDOM $(PYTHON) ./src/play.py

play-test:
	RUN_MODE=TEST $(PYTHON) ./src/play.py

venv:
	python3 -m venv $(VENV)

requirements: venv
	$(PIP) install -r requirements.txt

format: requirements
	$(BLACK) .

check: requirements
	$(PYRIGHT) .

style: format check
	
test-model:
	RUN_MODE=TEST $(PYTHON) ./src/test.py

train-model:
	RUN_MODE=RANDOM $(PYTHON) ./src/train.py

replay-model:
	REPLAY_MODEL=BOT RUN_MODE=TEST $(PYTHON) ./src/replay.py

clear-models:
	$(PYTHON) ./src/__models__/clear_models.py
