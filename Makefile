.PHONY: all bear wax readme robby tests arxivstatsbot arxivstatsbot-linux sb jboptim

SOURCES := $(shell git ls-files '*.py')

all: bear wax readme tests sb jboptim
bear:
	poetry run python -m nuitka --follow-imports --show-progress bear.py
	sudo mv bear.bin /usr/local/bin/bear
bear-linux:
	docker run -it -v $(shell pwd):/project -w /project ruivieira/python-experiments:latest python3 -m nuitka --follow-imports --show-progress bear.py
wax:
	poetry run python -m nuitka --follow-imports --show-progress wax.py
readme:
	python -m nuitka --follow-imports --show-progress readme.py -o readme
robby:
	python -m nuitka --follow-imports --show-progress robby.py -o robby
sb:
	poetry run python -m nuitka --follow-imports --show-progress sb.py
	sudo mv sb.bin /usr/local/bin/sb
arxivstatsbot:
	poetry run python -m nuitka --follow-imports --show-progress arxivstatsbot.py
arxivstatsbot-linux:
	docker run -it -v $(shell pwd):/project -w /project ruivieira/python-experiments:latest python3 -m nuitka --follow-imports --show-progress arxivstatsbot.py
jboptim:
	poetry run python -m nuitka --follow-imports --show-progress jboptim.py
	sudo mv jboptim.bin /usr/local/bin/jboptim

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