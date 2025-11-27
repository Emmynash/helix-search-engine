.PHONY: build run test lint clean

# Default: Build and Run
all: build run

build:
	docker-compose build

run:
	docker-compose up

# Run the test suite inside the container
test:
	docker-compose run --rm api pytest tests/ -v

# Check for code style issues (Critical for Senior teams)
lint:
	docker-compose run --rm api flake8 app/

# Clean up artifacts
clean:
	docker-compose down -v
	find . -type d -name "__pycache__" -exec rm -rf {} +