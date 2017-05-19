.PHONY: clean install test

# Project settings
PROJECT = cljs-loader

# Virtual environment settings
ENV ?= venv
REPOSITORY ?= test-pypi

requirements = -r requirements.txt

all: help

clean:  ## Clean
	@echo "Cleaning..."
	@find drf_hal_json/ -name '*.pyc' -delete
	@rm -rf ./build ./*egg* ./dist

install:  ## Install build dependencies (prerequisite for build)
	@echo "Installing build dependencies"
	@[ ! -d $(ENV)/ ] && virtualenv -p python3 $(ENV)/ || :
	@$(ENV)/bin/pip install $(requirements)

test: install  ## Run tests
	@cd tests && python manage.py test

help:
	@grep -E '^[a-zA-Z0-9_-]+:.*?## .*$$' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-25s\033[0m %s\n", $$1, $$2}'
