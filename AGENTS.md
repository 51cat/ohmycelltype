# AGENTS.md

Guide for AI coding agents working in the ohmycelltype repository.

## Project Overview

ohmycelltype is a multi-agent cell type annotation system for single-cell RNA sequencing data. It uses multiple LLM models in parallel to annotate cell types and reaches consensus through expert review.

**Tech Stack**: Python 3.10+, OpenAI SDK, Click (CLI), Rich (console), pandas

## Build & Installation

```bash
# Install in editable mode
pip install -e .

# Run the CLI
ohmycelltype annotate <input_file> -o <output_dir>
ohmycelltype version
```

## Testing

No test framework is currently configured. When tests are added:

```bash
# Run all tests
pytest

# Run a single test file
pytest tests/test_module.py

# Run a single test function
pytest tests/test_module.py::test_function_name -v

# Run with coverage
pytest --cov=ohmycelltype
```

## Linting & Type Checking

No linter is currently configured. Recommended setup:

```bash
# Install dev dependencies
pip install ruff mypy

# Run ruff linter
ruff check .

# Run ruff formatter
ruff format .

# Run type checker
mypy ohmycelltype/
```

## Code Style Guidelines

### Imports

Group imports in this order, separated by blank lines:

1. Standard library (alphabetical)
2. Third-party packages (alphabetical)
3. Local imports (alphabetical)

```python
import json
import os
from typing import Dict, List, Optional

from openai import OpenAI
from rich.console import Console

from ohmycelltype.llm.base import BaseLLM
from ohmycelltype.tools.logger import log_error, log_success
```

### Naming Conventions

| Type | Convention | Example |
|------|------------|---------|
| Classes | PascalCase | `CelltypeAnnoNode`, `N1N_LLM` |
| Functions/Methods | snake_case | `collect_parms`, `get_celltype` |
| Variables | snake_case | `cluster_id`, `model_name` |
| Constants | UPPER_SNAKE_CASE | `MAX_RETRIES`, `INIT_CELLTYPE` |
| Private methods | _leading_underscore | `_initialize_client` |
| Module-level dunder | __dunder__ | `__init__.py` |

### Type Hints

Use type hints for function signatures. Use `Optional` for optional parameters.

```python
def invoke(self, message_input: Message, **kwargs) -> str:
    ...

def __init__(self, api_key: str, model_name: Optional[str] = None):
    ...
```

For Python 3.10+, prefer union syntax:

```python
def validate(self, data: dict | None) -> bool:
    ...
```

### Dataclasses

Use `@dataclass` for state management classes:

```python
from dataclasses import dataclass, field
from typing import List, Dict

@dataclass
class SingleCluster:
    cluster_id: str = ''
    cluster_genes: List[str] = field(default_factory=list)
    ann_results: dict = field(default_factory=dict)
```

### Abstract Base Classes

Use `ABC` and `@abstractmethod` for interfaces:

```python
from abc import ABC, abstractmethod

class BaseLLM(ABC):
    @abstractmethod
    def invoke(self, system_prompt: str, user_prompt: str, **kwargs) -> str:
        pass
```

### Error Handling

Use specific exception types. Log errors with the logger module:

```python
from ohmycelltype.tools.logger import log_error

try:
    result = func(**params)
except Exception as e:
    log_error(f"执行失败: {str(e)}")
    raise
```

### Logging & Output

Use the `logger.py` module for console output. Do NOT use `print()` directly.

```python
from ohmycelltype.tools.logger import (
    log_info, log_warning, log_error, log_success
)

log_info("Processing cluster...")
log_warning("Low reliability score")
log_error("API call failed")
log_success("Annotation complete")
```

Use the `@add_log` decorator for automatic function timing:

```python
from ohmycelltype.tools.utils import add_log

@add_log
def process_cluster(self, cluster_id: int):
    ...
```

### CLI Commands

Use Click decorators for CLI:

```python
import click

@click.group()
def cli():
    """Description"""
    pass

@cli.command()
@click.argument('input_file', type=click.Path(exists=True))
@click.option('-o', '--output', required=True, help='Output directory')
def annotate(input_file, output):
    """Command description"""
    ...
```

### Project Structure

```
ohmycelltype/
├── llm/           # LLM provider implementations (inherit from BaseLLM)
├── nodes/         # Workflow nodes (each node is a processing step)
├── state/         # Dataclass state management
├── tools/         # Utility functions and tools
├── prompt/        # Prompt templates (uppercase constants)
├── cli.py         # CLI entry point
└── workflow.py    # Main workflow orchestration
```

### Adding a New LLM Provider

1. Create new file in `llm/` directory
2. Inherit from `BaseLLM`
3. Implement `invoke()` and `get_default_model()`
4. Add configuration to `config.json`

### JSON Handling

Use the helper functions from `__init__.py`:

```python
from ohmycelltype import load_json, write_json

data = load_json('config.json')
write_json(data, 'output.json')
```

Always use `ensure_ascii=False` for Chinese text support.

### Prompts

Store all prompts as uppercase module-level constants in `prompt/prompt.py`. Use `.format()` for variable substitution:

```python
INIT_CELLTYPE = """
You are an expert...
Species: {species}
Tissue: {tissue}
"""

formatted = INIT_CELLTYPE.format(species="Human", tissue="Liver")
```

## Key Files

| File | Purpose |
|------|---------|
| `workflow.py` | Main orchestration, entry point for annotation pipeline |
| `cli.py` | Command-line interface definitions |
| `llm/base.py` | Abstract base class for LLM implementations |
| `state/state.py` | Dataclasses for state management |
| `tools/logger.py` | Rich-based logging and console output |
| `prompt/prompt.py` | All prompt templates |

## Configuration

API credentials are stored in `~/.ohmycelltype.json`. Do NOT commit real API keys.
