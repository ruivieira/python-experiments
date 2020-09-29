.PHONY: all bear wax readme tests

SOURCES := $(shell git ls-files '*.py')

all: bear wax readme tests
bear:
	@python -m nuitka --follow-imports --show-progress bear.py
	@sudo mv bear.bin /usr/local/bin/bear
wax:
	@python -m nuitka --follow-imports --show-progress wax.py
readme:
	@python -m nuitka --follow-imports --show-progress readme.py

tests:
	pylint $(SOURCES)
	mypy $(SOURCES)