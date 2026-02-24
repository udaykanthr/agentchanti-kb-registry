---
id: "py-pattern-002"
title: "Python Type Hints Guide"
category: "pattern"
language: "python"
version: "1.0.0"
created_at: "2026-02-24"
tags:
  - python
  - type-hints
  - typing
  - mypy
  - pydantic
---

# Python Type Hints Guide

## Problem

Untyped Python code that relies on implicit contracts, causes runtime AttributeErrors and TypeErrors that could be caught at development time, and prevents IDEs from providing meaningful autocomplete and refactoring support.

## Solution: Basic Type Annotations

Annotate all function parameters and return types. Annotate important local variables where the type is not obvious from context.

```python
# Unannotated — hard to use safely
def process(data, limit):
    results = []
    for item in data:
        if item > limit:
            results.append(str(item))
    return results

# Annotated — clear contract
def process(data: list[int], limit: int) -> list[str]:
    return [str(item) for item in data if item > limit]
```

## Solution: Optional and Union Types

```python
from typing import Optional, Union

# Optional[T] is equivalent to T | None (Python 3.10+)
def find_user(user_id: int) -> Optional[str]:
    return users.get(user_id)

# Python 3.10+ shorthand (preferred when your codebase targets 3.10+)
def find_user(user_id: int) -> str | None:
    return users.get(user_id)

# Union for multiple valid types
def parse_id(value: Union[str, int]) -> int:
    if isinstance(value, str):
        return int(value)
    return value

# Python 3.10+:
def parse_id(value: str | int) -> int:
    return int(value) if isinstance(value, str) else value
```

## Solution: TypeVar for Generic Functions

Use TypeVar when a function can work with multiple types but the output type matches the input type.

```python
from typing import TypeVar, Sequence

T = TypeVar('T')

def first(items: Sequence[T]) -> T | None:
    return items[0] if items else None

# TypeScript-style: first([1, 2, 3]) returns int | None
# first(['a', 'b']) returns str | None
```

## Solution: Protocol for Duck Typing

Use Protocol to define structural subtypes — any class with the right methods satisfies the Protocol, without inheriting from it.

```python
from typing import Protocol, runtime_checkable

@runtime_checkable
class Closeable(Protocol):
    def close(self) -> None: ...

@runtime_checkable
class Saveable(Protocol):
    def save(self) -> bool: ...

# Any class with a .close() method satisfies Closeable
def safe_close(resource: Closeable) -> None:
    try:
        resource.close()
    except Exception as e:
        logger.warning("Failed to close %s: %s", resource, e)

# Works with any object that has .close() — no inheritance needed:
safe_close(open('file.txt'))
safe_close(db_connection)
safe_close(socket_connection)
```

## Solution: TypedDict

Define dict shapes precisely when you can't use dataclasses (e.g., JSON payloads, API responses).

```python
from typing import TypedDict, NotRequired

class UserPayload(TypedDict):
    id: int
    name: str
    email: str
    role: NotRequired[str]  # optional field (Python 3.11+)

def process_user(payload: UserPayload) -> None:
    print(payload['name'])  # IDE knows this is a str
    role = payload.get('role', 'user')  # safe access for optional field
```

## Solution: Runtime Checking with isinstance

Type hints are not enforced at runtime by Python. Use isinstance() for runtime validation, especially at API boundaries.

```python
def process(data: list[int]) -> list[str]:
    # At the boundary of untrusted input, validate:
    if not isinstance(data, list):
        raise TypeError(f"Expected list, got {type(data).__name__}")
    if not all(isinstance(x, int) for x in data):
        raise TypeError("All items must be integers")

    return [str(x) for x in data]
```

For complex validation at API boundaries, use Pydantic:

```python
from pydantic import BaseModel, Field, EmailStr

class CreateUserRequest(BaseModel):
    name: str = Field(min_length=1, max_length=100)
    email: EmailStr
    age: int = Field(ge=0, le=150)

# Pydantic validates at runtime and raises ValidationError with details
request = CreateUserRequest(name="Alice", email="alice@example.com", age=30)
```

## Solution: Mypy Usage

Run mypy in CI to catch type errors before deployment.

```bash
# Install
pip install mypy

# Run on your package
mypy src/

# Strict mode (recommended for new projects)
mypy --strict src/

# Key mypy config in pyproject.toml or mypy.ini:
# [mypy]
# strict = true
# ignore_missing_imports = true  # for untyped third-party libs
```

Common mypy flags:
- `--disallow-untyped-defs`: error if any function lacks annotations
- `--no-implicit-optional`: `x: str = None` is an error (must be `Optional[str]`)
- `--warn-return-any`: warn when a function returns Any

## When to Use

- Annotate all function signatures in application code.
- Use TypedDict for JSON/dict structures that cross module boundaries.
- Use Protocol for dependency injection and testability.
- Use runtime validation (Pydantic or isinstance) at system boundaries.

## When NOT to Use

- Do not annotate trivial local variables where the type is obvious from context.
- Do not over-engineer generic types for one-off functions.
- Do not use `Any` as a shortcut — use `object` or `Unknown` (with casting where needed).

## Related Patterns

- `py-pattern-001` — Pythonic Patterns
- `beh-007` — Python-Specific Instructions
