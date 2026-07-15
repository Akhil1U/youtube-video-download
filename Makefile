.PHONY: (
	      install test test-api-v1 \
          runserver-dev runserver \
		  deploy clear-expired-extracts
	)

PYTHON := uv run --active python
PIP := $(PYTHON) -m pip
HOST := 0.0.0.0

default: install test runserver

# Target to install dependencies
install:
	uv sync

# Target to run tests
test: test-api-v1

# Target to test RestAPI V1
test-api-v1:
	$(PYTHON) -m pytest tests/test_v1.py -xv

# Delete cached expired extracted info
clear-expired-extracts:
	$(PYTHON) -m app utils delete-expired-extracts

# Target to run development server
runserver-dev:
	$(PYTHON) -m fastapi dev app

# Target to run production server
runserver:
	$(PYTHON) -m fastapi run app

kill-uwsgi:
	pkill uwsgi

deploy: install test runserver
