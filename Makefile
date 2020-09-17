.PHONY: bear

all: bear
bear:
	@python -m nuitka --follow-imports --show-progress bear.py
	@sudo mv bear.bin /usr/local/bin/bear