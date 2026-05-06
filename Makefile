.PHONY: dev migrate test worker install clean

# Variables
PYTHON = venv/Scripts/python
PIP = venv/Scripts/pip
ALEMBIC = venv/Scripts/alembic
CELERY = venv/Scripts/celery
UVICORN = venv/Scripts/uvicorn
PYTEST = venv/Scripts/pytest

# Development
dev:
	set PYTHONPATH=. && $(UVICORN) app.main:app --reload

# Database
migrate:
	set PYTHONPATH=. && $(ALEMBIC) upgrade head

# Worker
worker:
	set PYTHONPATH=. && $(CELERY) -A app.tasks.celery_app worker --loglevel=info

# Testing
test:
	set PYTHONPATH=. && $(PYTEST)

# Installation
install:
	python -m venv venv
	$(PIP) install -r requirements.txt

# Clean up
clean:
	rmdir /s /q __pycache__
	rmdir /s /q .pytest_cache
	rmdir /s /q .mypy_cache
