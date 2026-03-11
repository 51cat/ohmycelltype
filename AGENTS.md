# AGENTS.md - Coding Guidelines for CelltypeAgent

This document provides coding guidelines for AI agents working on the CelltypeAgent codebase.

## Project Overview

CelltypeAgent is a multi-agent system for automatic cell type annotation in single-cell RNA sequencing data. It uses multiple LLM models (GPT, Claude, MiniMax, Qwen) to annotate cell types collaboratively without relying on frameworks like LangChain.

## Build/Lint/Test Commands

```bash
# Install the package in development mode
pip install -e .

# Run the main agent
python -m celltypeAgent.agent2

# No formal test suite exists. To test manually:
python -c "from celltypeAgent import load_json, write_json; print('Import OK')"

# No linting/type checking configured. If adding, consider:
# pip install ruff mypy
# ruff check celltypeAgent/
# mypy celltypeAgent/
```

## Project Structure

```
celltypeAgent/
├── celltypeAgent/           # Main package
│   ├── __init__.py          # Package init, JSON utilities, config loader
│   ├── agent2.py            # Main agent orchestration
│   ├── config.json          # API credentials (do not commit secrets)
│   ├── llm/                 # LLM interface implementations
│   │   ├── base.py          # Abstract base class for LLMs
│   │   ├── n1n.py           # N1N API implementation
│   │   ├── message.py       # Message history management
│   │   └── tool.py          # Tool documentation extraction
│   ├── nodes/               # Workflow nodes
│   │   ├── paramcollector_node.py   # Parameter collection
│   │   ├── anno_cluster_node.py     # Cell type annotation
│   │   ├── audit_ann_node.py        # Annotation auditing
│   │   └── consensus_node.py        # Multi-model consensus
│   ├── state/               # State management
│   │   └── state.py         # Dataclasses for state objects
│   ├── prompt/              # Prompt templates
│   │   └── prompt.py        # All prompt strings
│   └── tools/               # Utility functions
│       ├── utils.py         # General utilities
│       └── agent_tools.py   # Agent-specific tools
├── example_data/            # Test data files
├── work/                    # Output directory
└── setup.py                 # Package setup
```

## Code Style Guidelines

### Imports

Order imports in three groups, separated by blank lines:

1. Standard library imports
2. Third-party imports
3. Local package imports

```python
import os
import json
from typing import Dict, Any, Optional

import pandas as pd
from openai import OpenAI

from celltypeAgent.llm.base import BaseLLM
from celltypeAgent.state.state import MetaData
```

### Type Hints

- Use type hints for function parameters and return types
- Use `Optional[T]` for optional parameters
- Use `dict`, `list`, `str` (lowercase) for simple types
- Use `Dict[str, Any]`, `List[str]` for complex types from `typing`

```python
def invoke(self, message_input: Message, **kwargs) -> str:
    ...

def __init__(self, api_key: str, model_name: str | None = None):
    ...
```

### Naming Conventions

- **Classes**: PascalCase (e.g., `CelltypeAnnoNode`, `MetaData`)
- **Functions/Methods**: snake_case (e.g., `get_celltype`, `extract_and_validate_json`)
- **Constants**: UPPER_SNAKE_CASE (e.g., `PARM_COLLECT_MODEL`, `MAX_REFLECT_TIMES`)
- **Private methods**: Prefix with underscore (e.g., `_initialize_metadata_state`)
- **Properties**: Use `@property` decorator for computed attributes

### Class Structure

Follow this pattern for node classes:

```python
class ExampleNode:
    def __init__(self, LLM, metadata_state: MetaData, state: SingleCluster) -> None:
        self.llm = LLM
        self.metadata_state = metadata_state
        self.state = state
    
    def prep(self):
        """Prepare prompts and inputs before running."""
        ...
    
    def run(self) -> dict:
        """Execute the main logic."""
        ...
```

### State Classes

Use `@dataclass` for state objects:

```python
from dataclasses import dataclass, field
from typing import List, Dict

@dataclass
class SingleCluster:
    cluster_id: str = ''
    cluster_genes: List[str] = field(default_factory=list)
    ann_results: dict = field(default_factory=dict)
```

### Error Handling

- Use try-except for operations that may fail (file I/O, API calls, JSON parsing)
- Return tuples of `(success: bool, result: Any)` for task execution
- Raise `Exception` with descriptive messages for unrecoverable errors

```python
try:
    result = func(**params_dict)
    return True, result
except Exception as e:
    return False, e
```

### Logging and Decorators

Use the `@add_log` decorator for methods that need timing/logging:

```python
from celltypeAgent.tools.utils import add_log

@add_log
def _initialize_metadata_state(self):
    ...
```

### JSON Handling

- Use `json.dumps()` with `ensure_ascii=False` for Chinese text
- Use `extract_and_validate_json()` to parse LLM responses
- Use `load_json()` and `write_json()` from `__init__.py`

### Prompt Templates

Store all prompts in `celltypeAgent/prompt/prompt.py` as module-level constants:

```python
PROMPT_NAME = """
Template content with {placeholder}
"""
```

### LLM Integration

- Extend `BaseLLM` for new LLM providers
- Implement `invoke()` and `invoke_stream()` methods
- Use the `Message` class for conversation history management

## Dependencies

- `openai` - OpenAI API client
- `pandas` - Data manipulation
- `requests` - HTTP requests

## Important Notes

1. **Do not commit API keys** in `config.json` - use environment variables for production
2. **Chinese language support** is required - always use `ensure_ascii=False` for JSON
3. **No external frameworks** - keep implementations minimal and educational
4. **Reflection pattern** - agents can reflect on results up to `MAX_REFLECT_TIMES`
5. **Multi-model consensus** - final results combine multiple model predictions
