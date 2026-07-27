# ARG ?= "test.txt"
HIDE = PYGAME_HIDE_SUPPORT_PROMPT=1
FILES = main.py models.py parser.py display.py

VPATH = srcs/

.PHONY: install run debug clean lint lint-strict

install:
	uv sync

run:
	$(HIDE) uv run python main.py $(ARG)

debug:
	$(HIDE) uv run python -m pdb main.py $(ARG)

clean:
	find . -type d -name "__pycache__" -exec rm -rf {} +
	rm -rf .mypy_cache

lint:
	flake8 $(FILES)
	mypy $(FILES) --warn-return-any --warn-unused-ignores --ignore-missing-imports --disallow-untyped-defs --check-untyped-defs

lint-strict:
	flake8 $(FILES)
	mypy $(FILES) --strict
