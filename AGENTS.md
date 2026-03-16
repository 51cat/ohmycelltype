# AGENTS.md

Guidelines for agentic coding agents working on the ohmycelltype codebase.

## Project Overview

ohmycelltype is a multi-agent cell type annotation system for single-cell RNA-seq data. It uses multiple LLM models in parallel for annotation, with consensus mechanisms, automatic auditing, and self-reflection capabilities.

## Build/Lint/Test Commands

### Installation

```bash
# Install in development mode
pip install -e .

# Or install dependencies directly
pip install openai pandas requests rich click markdown
```

### Running the CLI

```bash
# Initialize configuration
ohmycelltype init-config

# Set API key
ohmycelltype set-api

# Run annotation
ohmycelltype annotate input.csv -o ./results

# View configuration
ohmycelltype show

# View version
ohmycelltype version
```

### Testing

```bash
# No test suite exists yet. When adding tests, use pytest:
pytest tests/

# Run a single test file
pytest tests/test_workflow.py

# Run a single test function
pytest tests/test_workflow.py::test_celltype_annotation -v
```

### Linting and Type Checking

```bash
# Recommended linting (when tools are set up)
ruff check ohmycelltype/

# Type checking (when mypy is configured)
mypy ohmycelltype/

# Format code
ruff format ohmycelltype/
```

## Project Structure

```
ohmycelltype/
├── ohmycelltype/           # Main package
│   ├── __init__.py         # Package init, JSON utilities
│   ├── cli.py              # CLI entry point (click)
│   ├── config.py           # Configuration management
│   ├── workflow.py         # Main annotation workflow
│   ├── llm/                # LLM provider implementations
│   │   ├── base.py         # Abstract base class
│   │   ├── message.py      # Message handling
│   │   ├── n1n.py          # N1N provider
│   │   └── openrouter.py   # OpenRouter provider
│   ├── nodes/              # Workflow nodes
│   │   ├── paramcollector_node.py
│   │   ├── anno_cluster_node.py
│   │   ├── audit_ann_node.py
│   │   ├── consensus_node.py
│   │   └── report_node.py
│   ├── state/              # State management (dataclasses)
│   │   └── state.py
│   ├── prompt/             # Prompt templates
│   │   └── prompt.py
│   └── tools/              # Utility functions
│       ├── logger.py       # Rich-based logging
│       └── utils.py        # Helper functions
├── setup.py                # Package setup
└── README.md               # Documentation (Chinese)
```

## Code Style Guidelines

### Imports

```python
# 1. Standard library (alphabetical)
import json
import os
import time
from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any

# 2. Third-party packages (alphabetical)
import pandas as pd
from openai import OpenAI
from rich.console import Console

# 3. Local imports (alphabetical)
from ohmycelltype.llm.base import BaseLLM
from ohmycelltype.llm.message import Message
from ohmycelltype.state.state import SingleCluster, MetaData
```

### Naming Conventions

- **Classes**: PascalCase (e.g., `CelltypeWorkflow`, `SingleCluster`, `N1N_LLM`)
- **Functions/Methods**: snake_case (e.g., `get_celltype`, `update_metadata`, `extract_and_validate_json`)
- **Private Methods**: Prefix with underscore (e.g., `_initialize_nodes`, `_ann_single_cluster`)
- **Constants**: UPPER_SNAKE_CASE (e.g., `BASE_CONFIG`, `INIT_CELLTYPE`)
- **Module-level variables**: snake_case (e.g., `custom_theme`, `console`)

### Type Hints

Use type hints for function signatures. Prefer modern Python syntax:

```python
# Good
def invoke(self, message_input: Message, **kwargs) -> str:
    ...

def get_metadata_val(self, key: str) -> Any:
    return self.metadata[key]

# Union types (Python 3.10+)
def validate_response(self, response: str | None) -> str:
    ...

# Generic types
from typing import Dict, List, Optional, Any

def update_ann_results(self, model_name: str, res: dict) -> None:
    self.ann_results[model_name] = res
```

### Dataclasses for State Management

Use `@dataclass` for state and data containers:

```python
from dataclasses import dataclass, field
from typing import Dict, List

@dataclass
class SingleCluster:
    cluster_id: str = ''
    cluster_genes: List[str] = field(default_factory=list)
    ann_results: Dict = field(default_factory=dict)
    
    def get_celltype(self, model_name: str) -> str:
        return self.ann_results[model_name]['cell_type']
```

### Error Handling

- Raise specific exceptions with clear messages
- Use try/except for external API calls
- Log errors using the rich-based logger

```python
from ohmycelltype.tools.logger import log_error, log_warning

# API retry pattern with exponential backoff
for attempt in range(1, self.max_retry + 1):
    try:
        response = self.client.chat.completions.create(...)
        return response
    except Exception as e:
        if attempt < self.max_retry:
            delay = 2 ** (attempt - 1)
            time.sleep(delay)
        else:
            log_error(f"重试 {self.max_retry} 次后仍失败")
            raise

# Validation with clear errors
if provider not in self.config:
    raise ValueError(f"Unsupported provider: {provider}")
```

### Decorators

Use `@property` for getters, `functools.wraps` for decorators:

```python
from functools import wraps

def rich_log(func: Callable) -> Callable:
    @wraps(func)
    def wrapper(*args, **kwargs) -> Any:
        log_start(func.__name__)
        result = func(*args, **kwargs)
        return result
    return wrapper

class Message:
    @property
    def message(self):
        return self._message
```

### Logging

Use the rich-based logger from `tools/logger.py`:

```python
from ohmycelltype.tools.logger import (
    log_info, log_warning, log_error, log_success,
    display_annotation_table, display_section_header
)

log_info("Processing cluster", highlight=True)
log_success("Annotation complete")
log_warning("Low reliability score detected")
log_error("API call failed")
```

### JSON Handling

Use utilities from `__init__.py`:

```python
from ohmycelltype import load_json, write_json

# Write with UTF-8 encoding and indentation
write_json(data, "output.json")

# Load with UTF-8 encoding
data = load_json("input.json")
```

### Prompt Templates

Store prompts as module-level constants in `prompt/prompt.py`. Use `.format()` for variable substitution:

```python
INIT_CELLTYPE = """
你是一位资深的单细胞生物信息学专家...
物种: {species}
组织: {tissue}
Cluster: {cluster_id}
基因: {gene_list}
"""

# Usage
system_prompt = INIT_CELLTYPE.format(
    species="human",
    tissue="blood",
    cluster_id="0",
    gene_list="CD3D,CD3E,CD4"
)
```

### Node Classes Pattern

Follow the standard node pattern:

```python
class SomeNode:
    def __init__(self, llm, metadata_state: MetaData, state: SingleCluster) -> None:
        self.llm = llm
        self.state = state
        self.metadata_state = metadata_state
    
    def prep(self):
        """Prepare inputs (prompts, messages)."""
        self.system_prompt = PROMPT_TEMPLATE.format(...)
        self.message_input = Message(system_prompt=self.system_prompt)
    
    def run(self) -> dict:
        """Execute the node's main logic."""
        self.message_input.add_user_message("Task instruction")
        response = self.llm.invoke(self.message_input)
        return extract_and_validate_json(response)
```

## Notes

- The project uses Chinese for prompts and user-facing messages, but code comments and docstrings can be in either language
- LLM responses are expected in JSON format; use `extract_and_validate_json()` for parsing
- Multi-model parallel annotation is handled via `ThreadPoolExecutor`
- Configuration is stored in `~/ohmycelltype.json`
