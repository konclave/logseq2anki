# AGENTS.md - Logseq to Anki Project Guide

This document provides essential information for agentic coding agents working on this Python project that converts Logseq journal notes to Anki flashcards.

## Project Overview

A Python CLI tool that:
- Scans Logseq journal files (`~/Sync/logseq/journals/*.md`) for notes tagged with `#card #deutsch`
- Extracts German vocabulary with cloze deletions using `{{cloze translation}}` syntax
- Supports AI-powered example sentence generation via Gemini or OpenRouter APIs
- Syncs to Anki via AnkiConnect add-on
- Organizes cards into dynamic decks based on tags

## Build/Test/Lint Commands

### Essential Commands
```bash
# Install dependencies
make install
# or: pip3 install -r requirements.txt

# Run the main sync application
make sync
# or: PYTHONPATH=$PYTHONPATH:. python3 src/main.py

# Run all tests
make test
# or run individual tests:
PYTHONPATH=$PYTHONPATH:. python3 tests/test_parser.py
PYTHONPATH=$PYTHONPATH:. python3 tests/test_dynamic_decks.py
PYTHONPATH=$PYTHONPATH:. python3 tests/test_llm_fallback.py

# Check Python version (requires 3.11+)
python3 --version
```

### Testing Notes
- Tests are simple executable Python files, not pytest-based
- Use `unittest` framework for complex tests (see `test_llm_fallback.py`)
- Always set `PYTHONPATH=$PYTHONPATH:.` when running tests directly
- Test files create temporary artifacts and clean them up

## Code Style Guidelines

### Import Organization
```python
# Standard library imports first
import os
import re
from typing import List, Dict, Any, Optional

# Third-party imports second
import requests
from dotenv import load_dotenv
from rich.console import Console

# Local imports last
from src.anki import AnkiClient
from src.parser import LogseqNote
```

### Type Hints and Data Structures
- **Always** use type hints for function parameters and return values
- Use `dataclass` for data structures with `@dataclass` decorator
- Use `field(default_factory=list)` for mutable default arguments
- Import from `typing` extensively: `List`, `Dict`, `Any`, `Optional`

```python
from dataclasses import dataclass, field
from typing import List

@dataclass
class LogseqNote:
    front: str
    cloze: str
    tags: List[str]
    examples: List[str] = field(default_factory=list)
    file_path: str = ""
```

### Naming Conventions
- **Classes**: `PascalCase` (e.g., `AnkiClient`, `LLMClient`)
- **Functions/Variables**: `snake_case` (e.g., `parse_logseq_file`, `current_note`)
- **Constants**: `UPPER_SNAKE_CASE` (rare, but use for module-level constants)
- **Private methods**: prefix with underscore (`_generate_with_openrouter`)

### Error Handling Patterns
```python
# Network/API operations - use try/catch and check response structure
def invoke(self, action: str, **params) -> Any:
    response = requests.post(self.url, json={...})
    result = response.json()
    if len(result) != 2:
        raise Exception("response has an unexpected number of fields")
    if "error" not in result:
        raise Exception("response is missing required error field")
    if result["error"] is not None:
        raise Exception(result["error"])
    return result["result"]

# File operations - check existence first
def scan_journals(directory: str) -> List[LogseqNote]:
    expanded_path = os.path.expanduser(directory)
    if not os.path.exists(expanded_path):
        return []

# Graceful degradation for optional features
@property
def is_configured(self) -> bool:
    return bool(self.api_key or self.openrouter_api_key)
```

### String Processing and Regex
- Use raw strings for regex patterns: `r"^\s*-\s+(.*?)\{\{cloze\s+(.*?)\}\}(.*)"`
- Always handle encoding for file operations: `open(file_path, "r", encoding="utf-8")`
- Use `strip()` liberally to clean input data
- Escape strings properly for API queries: `escaped_text = front_text.replace('"', '\\"')`

### Function Structure
```python
def function_name(param1: str, param2: Optional[int] = None) -> ReturnType:
    """
    Brief description of what the function does.
    
    Args:
        param1: Description of first parameter
        param2: Description of optional parameter
    
    Returns:
        Description of return value
    """
    # Early returns for validation
    if not param1:
        return []
    
    # Main logic
    result = []
    for item in collection:
        # Process item
        result.append(processed_item)
    
    return result
```

### Environment and Configuration
- Use `python-dotenv` for environment variables
- Always call `load_dotenv()` at module import time
- Check for API keys with `os.getenv()` and provide fallbacks
- Use environment variables for external service configuration

### CLI and User Interface
- Use `rich` library for beautiful CLI output
- Use `Panel.fit()` for headers and `Progress()` for long operations
- Use color codes: `[green]`, `[red]`, `[yellow]`, `[blue]`, `[cyan]`, `[magenta]`
- Provide clear error messages and status updates

### API Client Patterns
- Initialize clients lazily (only if API keys available)
- Implement fallback mechanisms (Gemini → OpenRouter)
- Use structured JSON payloads for API requests
- Handle HTTP status codes with `raise_for_status()`

## Project Structure Notes

```
src/
├── main.py          # CLI entry point and orchestration
├── parser.py        # Logseq markdown parsing logic
├── anki.py          # AnkiConnect API client
└── llm.py           # LLM integration (Gemini/OpenRouter)

tests/
├── test_parser.py           # Simple parsing tests
├── test_dynamic_decks.py    # Deck selection logic
└── test_llm_fallback.py     # LLM fallback with unittest
```

## Dependencies
- `requests` - HTTP client for API calls
- `google-genai` - Gemini AI SDK
- `rich` - CLI formatting and progress
- `python-dotenv` - Environment variable management

## Important Notes
- This project requires Anki to be running with AnkiConnect add-on installed
- Logseq journals are expected at `~/Sync/logseq/journals/`
- Uses standard Anki Cloze model format
- Supports both Gemini and OpenRouter API keys
- German language focused, but extensible to other languages