.DEFAULT_GOAL := lint
sources = list_dependencies.py

.PHONY: install
install:
	python -m pip install -U pip
	pip install -r requirements-linting.txt
	pip install -e .

.PHONY: format
format:
	isort $(sources)
	black $(sources)

.PHONY: lint
lint:
	ruff $(sources)
	isort $(sources) --check-only --df
	black $(sources) --check --diff

.PHONY: pyupgrade
pyupgrade:
	pyupgrade --py37-plus $(sources)
