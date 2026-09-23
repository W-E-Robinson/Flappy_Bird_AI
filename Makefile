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
