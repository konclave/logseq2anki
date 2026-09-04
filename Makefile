.PHONY: help sync install test clean

# Default goal: display help
help:
	@echo "Available tasks:"
	@echo "  make sync      - Run the Logseq to Anki synchronization"
	@echo "  make install   - Install Python dependencies using uv"
	@echo "  make test      - Run all tests"
	@echo "  make clean     - Remove the virtual environment"
	@echo "  make help      - Show this help message"

# Run the synchronization
sync:
	@export PYTHONPATH=$${PYTHONPATH}:. && ./.venv/bin/python src/main.py

# Install dependencies
install:
	@uv venv
	@uv sync

# Run all tests
test:
	@echo "Running tests..."
	@export PYTHONPATH=$${PYTHONPATH}:. && ./.venv/bin/python tests/test_parser.py
	@export PYTHONPATH=$${PYTHONPATH}:. && ./.venv/bin/python tests/test_dynamic_decks.py
	@export PYTHONPATH=$${PYTHONPATH}:. && ./.venv/bin/python tests/test_llm_fallback.py
	@export PYTHONPATH=$${PYTHONPATH}:. && ./.venv/bin/python tests/test_anki_client.py

# Clean up the virtual environment
clean:
	@rm -rf ./.venv
