.PHONY: all bear wax

all: bear wax
bear:
	@python -m nuitka --follow-imports --show-progress bear.py
	@sudo mv bear.bin /usr/local/bin/bear
wax:
	@python -m nuitka --follow-imports --show-progress wax.py
