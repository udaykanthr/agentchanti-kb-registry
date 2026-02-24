---
id: "beh-007"
title: "Python-Specific Instructions"
category: "behavioral"
language: "python"
version: "1.0.0"
created_at: "2026-02-24"
tags:
  - python
  - behavioral
  - pythonic
  - best-practices
  - async
---

# Python-Specific Instructions

When writing or reviewing Python code, follow these instructions exactly.

## Always Use

- **`pathlib.Path` over `os.path`**: Use `Path('dir') / 'file.txt'` not `os.path.join('dir', 'file.txt')`. Use `path.read_text()` not `open(path).read()`.
- **f-strings over `.format()` or `%`**: Use `f"Hello, {name}"` not `"Hello, %s" % name` or `"Hello, {}".format(name)`. Exception: logging — use `logger.info("User %s", user_id)` (lazy formatting).
- **Dataclasses or Pydantic over raw dicts for structured data**: Use `@dataclass class Config:` not `config = {'host': ..., 'port': ...}`. Raw dicts have no type safety or IDE support.
- **Context managers for resource management**: Use `with open(path) as f:` not `f = open(path); ... ; f.close()`. Apply to all resources: files, DB connections, locks, HTTP sessions.
- **`logging` module over `print` statements**: Use `logger.info(...)` not `print(...)` in any non-script code. Print is for scripts and REPL only.

## Always Add

- **Type hints on all function signatures**: Every function parameter and return type must be annotated. `def process(items: list[str]) -> list[str]:` not `def process(items):`.
- **`__all__` in module files**: Define `__all__ = ['PublicClass', 'public_function']` in modules with public APIs. This controls what `from module import *` exports.
- **`if __name__ == "__main__":` guard**: Every script with top-level executable code must be wrapped in this guard to prevent execution on import.

## Never

- **Never use mutable default arguments**: `def f(x=[]):` creates ONE list shared across all calls. Use `def f(x=None): x = x or []` or `def f(x: list | None = None): x = x if x is not None else []`.
- **Never use bare `except:`**: `except:` catches `KeyboardInterrupt`, `SystemExit`, and `GeneratorExit` — system signals that should propagate. Always use `except Exception:` at minimum, and prefer specific exception types.
- **Never use wildcard imports `from x import *`**: They pollute the namespace, hide what symbols are available, and make refactoring dangerous. Always use explicit imports.
- **Never use `global` variables for state**: Global mutable state causes unpredictable behavior in tests and concurrent code. Use class attributes, function parameters, or dependency injection instead.

## Async-Specific

- **Always await coroutines**: `result = await my_coroutine()` not `result = my_coroutine()`. An unawaited coroutine returns a coroutine object and never executes.
- **Never mix sync/async I/O**: Never use `requests`, `open()`, `time.sleep()`, or other blocking calls inside an `async def` function. Use `aiohttp`, `aiofiles`, `asyncio.sleep()` instead.
- **Use `asyncio.gather()` for parallel tasks**: When multiple async operations are independent, run them concurrently: `results = await asyncio.gather(task1(), task2())` instead of `await task1(); await task2()`.

## Code Quality Specifics

When writing Python:
1. Import order: stdlib → third-party → local, with a blank line between groups.
2. Class order: `__init__`, class methods, properties, instance methods, private methods.
3. Prefer `is None` and `is not None` over `== None` — the latter calls `__eq__` and can be overridden.
4. Use `enumerate()` instead of `range(len(x))` when you need both index and value.
5. Use `zip()` to iterate two sequences in parallel. Use `zip(..., strict=True)` (Python 3.10+) to raise if lengths differ.
