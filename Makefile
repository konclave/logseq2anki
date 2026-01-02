.PHONY: help sync install test

# Default goal: display help
help:
	@echo "Available tasks:"
	@echo "  make sync      - Run the Logseq to Anki synchronization"
	@echo "  make install   - Install Python dependencies"
	@echo "  make test      - Run all tests"
	@echo "  make help      - Show this help message"

# Run the synchronization
sync:
	@export PYTHONPATH=$${PYTHONPATH}:. && python3 src/main.py

# Install dependencies
install:
	@pip3 install -r requirements.txt

# Run all tests
test:
	@echo "Running tests..."
	@export PYTHONPATH=$${PYTHONPATH}:. && python3 tests/test_parser.py
	@export PYTHONPATH=$${PYTHONPATH}:. && python3 tests/test_dynamic_decks.py
