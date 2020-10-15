.PHONY: all bear wax readme tests arxivstatsbot arxivstatsbot-linux

SOURCES := $(shell git ls-files '*.py')

all: bear wax readme tests
bear:
	poetry run python -m nuitka --follow-imports --show-progress bear.py
	sudo mv bear.bin /usr/local/bin/bear
bear-linux:
	docker run -it -v $(shell pwd):/project -w /project ruivieira/python-experiments:latest python3 -m nuitka --follow-imports --show-progress bear.py
wax:
	poetry run python -m nuitka --follow-imports --show-progress wax.py
readme:
	poetry run python -m nuitka --follow-imports --show-progress readme.py
arxivstatsbot:
	poetry run python -m nuitka --follow-imports --show-progress arxivstatsbot.py
arxivstatsbot-linux:
	docker run -it -v $(shell pwd):/project -w /project ruivieira/python-experiments:latest python3 -m nuitka --follow-imports --show-progress arxivstatsbot.py
build-container:
	docker build -t ruivieira/python-experiments:latest .
clean:
	rm -f *.bin
	rm -Rf bear.build
	rm -Rf wax.build
	rm -Rf readme.build
	rm -Rf arxivstatsbot.build
tests:
	poetry run pylint $(SOURCES)
	poetry run mypy $(SOURCES)
	poetry run black --check $(SOURCES)