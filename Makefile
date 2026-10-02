VENV := .venv
PYTHON := $(VENV)/bin/python
PIP := $(VENV)/bin/pip
BLACK := $(VENV)/bin/black
PYRIGHT := $(VENV)/bin/pyright

play:
	$(PYTHON) ./src/play.py

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
	$(PYTHON) ./src/test.py

train-model:
	$(PYTHON) ./src/train.py

clear-models:
	$(PYTHON) ./src/__models__/clear_models.py
