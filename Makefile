PYTHON = python3
MAIN = main.py
MAP = MapName.txt

install:
	$(PYTHON) -m pip install flake8 mypy

run:
	$(PYTHON) $(MAIN) "$(MAP)"

debug:
	$(PYTHON) -m pdb $(MAIN) "$(MAP)"

clean:
	rm -rf __pycache__ .mypy_cache

lint:
	flake8 .
	mypy . --warn-return-any --warn-unused-ignores --ignore-missing-imports --disallow-untyped-defs --check-untyped-defs