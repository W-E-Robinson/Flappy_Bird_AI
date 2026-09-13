VENV := .venv
PYTHON := $(VENV)/bin/python
PIP := $(VENV)/bin/pip
BLACK := $(VENV)/bin/black
PYRIGHT := $(VENV)/bin/pyright

main:
	$(PYTHON) ./src/main.py

venv:
	python3 -m venv $(VENV)

requirements: venv
	$(PIP) install -r requirements.txt

format: requirements
	$(BLACK) .

check: requirements
	$(PYRIGHT) .
