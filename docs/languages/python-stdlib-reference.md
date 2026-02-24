---
id: "doc-004"
title: "Python Stdlib Reference for Agentic Code"
category: "doc"
language: "python"
version: "1.0.0"
created_at: "2026-02-24"
tags:
  - python
  - stdlib
  - pathlib
  - subprocess
  - logging
  - dataclasses
  - typing
---

# Python Stdlib Reference for Agentic Code

Key stdlib modules for agent-style code generation, file operations, process execution, and structured data handling.

## pathlib — Modern File Paths

Always use `pathlib.Path` over `os.path`. It is object-oriented, more readable, and cross-platform.

```python
from pathlib import Path

# Creating paths
p = Path('/home/user/project')
config = p / 'config' / 'settings.json'  # clean path joining

# Inspection
print(config.exists())         # True/False
print(config.is_file())        # True if file
print(config.is_dir())         # True if directory
print(config.suffix)           # '.json'
print(config.stem)             # 'settings'
print(config.name)             # 'settings.json'
print(config.parent)           # Path('/home/user/project/config')

# Reading and writing
text = config.read_text(encoding='utf-8')
config.write_text(json.dumps(data, indent=2), encoding='utf-8')
data = config.read_bytes()

# Glob
py_files = list(p.rglob('*.py'))  # recursive
yml_files = list(p.glob('errors/**/*.yml'))

# Create directories
output_dir = Path('output/reports')
output_dir.mkdir(parents=True, exist_ok=True)

# Resolve (make absolute)
abs_path = Path('relative/path').resolve()
```

## subprocess — Running Shell Commands

```python
import subprocess

# Run command and capture output (recommended: use run() not Popen for simple cases)
result = subprocess.run(
    ['git', 'log', '--oneline', '-10'],
    capture_output=True,
    text=True,               # decode stdout/stderr as str
    cwd='/path/to/repo',     # working directory
    timeout=30,              # seconds before TimeoutExpired
    check=False,             # don't raise on non-zero exit code
)

if result.returncode == 0:
    print(result.stdout)
else:
    print(f"Error: {result.stderr}")

# check=True: raises CalledProcessError on non-zero exit
try:
    result = subprocess.run(['mypy', 'src/'], check=True, capture_output=True, text=True)
except subprocess.CalledProcessError as e:
    print(f"mypy failed (exit {e.returncode}):\n{e.stdout}\n{e.stderr}")

# Shell=True (avoid when possible — security risk with user input)
result = subprocess.run('echo hello | grep h', shell=True, capture_output=True, text=True)
```

## shutil — High-level File Operations

```python
import shutil

# Copy files and directories
shutil.copy2('src/file.py', 'dst/file.py')         # copy with metadata
shutil.copytree('src/', 'dst/', dirs_exist_ok=True) # recursive copy

# Move
shutil.move('old_path/', 'new_path/')

# Delete
shutil.rmtree('directory_to_delete/')  # recursive delete (no recycle bin!)

# Create archive
shutil.make_archive('output_name', 'zip', root_dir='content_dir/')

# Get disk usage
total, used, free = shutil.disk_usage('/')
print(f"Free: {free // (2**30)} GiB")
```

## tempfile — Temporary Files

```python
import tempfile
from pathlib import Path

# Temporary file that auto-deletes
with tempfile.NamedTemporaryFile(suffix='.py', mode='w', delete=True) as f:
    f.write("x = 1")
    f.flush()
    # file exists at f.name during the with block

# Temporary directory
with tempfile.TemporaryDirectory() as tmpdir:
    workspace = Path(tmpdir)
    (workspace / 'script.py').write_text("print('hello')")
    subprocess.run(['python', str(workspace / 'script.py')], check=True)
# tmpdir and all contents deleted automatically

# Persistent temp file (you manage deletion)
fd, path = tempfile.mkstemp(suffix='.json')
import os
os.close(fd)
Path(path).write_text('{}')
# ... use the file ...
os.unlink(path)  # delete when done
```

## logging — Structured Logging

```python
import logging

# Configure once at application entry point
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s %(name)s %(levelname)s %(message)s',
)

# Use named loggers per module (NOT root logger)
logger = logging.getLogger(__name__)

# Log with context
logger.debug("Processing %d items", len(items))
logger.info("User %s created order %s", user_id, order_id)
logger.warning("Retry attempt %d of %d for %s", attempt, max_retries, url)
logger.error("Failed to process order %s: %s", order_id, error, exc_info=True)
logger.critical("Database unreachable: %s", error)

# Structured logging with extra fields (for log aggregation tools)
logger.info("Request processed", extra={
    'user_id': user_id,
    'duration_ms': duration,
    'status': 'success',
})
```

## dataclasses — Structured Data

```python
from dataclasses import dataclass, field, asdict, astuple
from typing import Optional

@dataclass
class Config:
    host: str
    port: int = 8080
    debug: bool = False
    tags: list[str] = field(default_factory=list)  # mutable default
    metadata: dict = field(default_factory=dict)

config = Config(host='localhost')
print(config.port)       # 8080
print(asdict(config))    # {'host': 'localhost', 'port': 8080, ...}

# Frozen (immutable) — hashable
@dataclass(frozen=True)
class CacheKey:
    language: str
    error_type: str

key = CacheKey(language='python', error_type='AttributeError')
cache = {key: 'result'}  # hashable — can be dict key
```

## typing — Type System

```python
from typing import (
    Optional, Union, Any, Callable, TypeVar, Generic,
    Sequence, Mapping, Iterator, Generator
)
from collections.abc import Callable

# Common patterns
def process(items: Sequence[str]) -> list[str]:
    return [item.upper() for item in items]

def transform(data: dict[str, Any]) -> dict[str, str]:
    return {k: str(v) for k, v in data.items()}

# Callable with signature
Handler = Callable[[str, int], bool]

def register(name: str, handler: Handler) -> None:
    handlers[name] = handler

# TypeVar for generic functions
T = TypeVar('T')
def first(items: list[T]) -> T | None:
    return items[0] if items else None
```

## functools — Function Tools

```python
from functools import lru_cache, cache, partial, reduce

# LRU cache: memoize function results
@lru_cache(maxsize=128)
def expensive_computation(n: int) -> int:
    return sum(i**2 for i in range(n))

# cache (Python 3.9+): unbounded cache
@cache
def fibonacci(n: int) -> int:
    if n < 2:
        return n
    return fibonacci(n - 1) + fibonacci(n - 2)

# Partial: create specialized function from generic one
from functools import partial

def power(base, exponent):
    return base ** exponent

square = partial(power, exponent=2)
cube = partial(power, exponent=3)
print(square(4))  # 16
print(cube(3))    # 27
```

## itertools — Iteration Utilities

```python
import itertools

# Chain: flatten iterables
all_items = list(itertools.chain(list1, list2, list3))

# Batched (Python 3.12+): split into fixed-size chunks
for batch in itertools.batched(range(100), 10):
    process_batch(list(batch))

# Groupby: group consecutive items by key
from itertools import groupby
data = sorted(errors, key=lambda e: e.language)  # must sort first
for language, group in groupby(data, key=lambda e: e.language):
    print(f"{language}: {list(group)}")

# Product: Cartesian product (nested loops)
for lang, severity in itertools.product(['python', 'go'], ['warning', 'critical']):
    print(f"{lang}/{severity}")
```
