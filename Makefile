.PHONY: install lint test run

install:
	python -m pip install -r requirements.txt

lint:
	ruff check .

test:
	pytest -q

run:
	python -m src.cli --help
