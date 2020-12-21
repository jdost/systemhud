.PHONY: DEFAULT clean test lint mypy format isort black shell install
PYTHON=venv/bin/python

DEFAULT: test
src/setup.py:
venv: src/setup.py
	@python3 -m venv --system-site-packages --prompt sysHUD venv
	${PYTHON} -m pip install -U -e src/[dev]
	@touch venv

clean:
	rm -f src/*/*.pyc
	rm -f src/*/*/*.pyc
	rm -rf *.egg-info
	rm -rf dist/
	rm -rf .mypy_cache
	rm -rf .pytest_cache

test: format lint

lint: mypy

mypy: venv
	@echo " >> Type-checking codebase with mypy"
	@${PYTHON} -m mypy --ignore-missing-import src
	@echo ""

format: isort black

isort: venv
	@echo " >> Formatting imports in codebase with isort"
	@${PYTHON} -m isort src
	@${PYTHON} -m isort bin
	@echo ""

black: venv
	@echo " >> Formatting codebase with black"
	@${PYTHON} -m black src
	@${PYTHON} -m black bin
	@echo ""

shell:
	${PYTHON}
