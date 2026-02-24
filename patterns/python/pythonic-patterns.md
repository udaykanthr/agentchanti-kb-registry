---
id: "py-pattern-001"
title: "Pythonic Patterns"
category: "pattern"
language: "python"
version: "1.0.0"
created_at: "2026-02-24"
tags:
  - python
  - pythonic
  - comprehensions
  - generators
  - dataclasses
  - walrus-operator
---

# Pythonic Patterns

## Problem

Python code written in a style that ignores language idioms — verbose loops where comprehensions apply, manual resource management instead of context managers, raw dicts where dataclasses give structure, and repetitive string formatting.

## Solution: List and Dict Comprehensions

Comprehensions are more readable and often faster than equivalent for-loops for simple transformations.

```python
# Bad: verbose loop
squares = []
for x in range(10):
    if x % 2 == 0:
        squares.append(x ** 2)

# Good: list comprehension
squares = [x ** 2 for x in range(10) if x % 2 == 0]

# Dict comprehension
word_lengths = {word: len(word) for word in words}

# Set comprehension
unique_domains = {email.split('@')[1] for email in emails}

# Nested comprehension (use sparingly — readability drops fast)
matrix = [[row[i] for row in matrix] for i in range(len(matrix[0]))]
```

## Solution: Context Managers

Use `with` statements for resources that need cleanup — files, connections, locks. Implement `__enter__`/`__exit__` or use `contextlib` for custom context managers.

```python
# Bad: manual resource management
f = open('data.txt')
try:
    content = f.read()
finally:
    f.close()  # easy to forget or miss in error paths

# Good: context manager
with open('data.txt', 'r', encoding='utf-8') as f:
    content = f.read()

# Multiple context managers (Python 3.10+ cleaner syntax)
with (
    open('input.txt') as infile,
    open('output.txt', 'w') as outfile,
):
    outfile.write(infile.read())

# Custom context manager with contextlib
from contextlib import contextmanager

@contextmanager
def db_transaction(connection):
    cursor = connection.cursor()
    try:
        yield cursor
        connection.commit()
    except Exception:
        connection.rollback()
        raise
    finally:
        cursor.close()

with db_transaction(conn) as cursor:
    cursor.execute("INSERT INTO users (name) VALUES (?)", (name,))
```

## Solution: Generators

Generators produce values lazily — they are memory-efficient for large datasets and pipelines.

```python
# Bad: loads everything into memory
def read_large_file(path):
    with open(path) as f:
        return f.readlines()  # entire file in memory

lines = read_large_file('huge.log')
for line in lines:
    process(line)

# Good: generator — one line in memory at a time
def read_large_file(path):
    with open(path) as f:
        for line in f:
            yield line.rstrip('\n')

for line in read_large_file('huge.log'):
    process(line)

# Generator expression (like list comprehension but lazy)
total = sum(len(line) for line in read_large_file('huge.log'))
```

## Solution: Dataclasses

Use `@dataclass` for structured data instead of raw dicts or verbose `__init__` boilerplate.

```python
from dataclasses import dataclass, field
from typing import Optional

# Bad: raw dict — no type safety, no IDE support
user = {'id': 1, 'name': 'Alice', 'email': 'alice@example.com'}

# Good: dataclass
@dataclass
class User:
    id: int
    name: str
    email: str
    is_active: bool = True
    tags: list[str] = field(default_factory=list)

user = User(id=1, name='Alice', email='alice@example.com')
print(user.name)    # IDE knows this is a str
print(repr(user))   # User(id=1, name='Alice', ...)

# Frozen dataclass (immutable — great for cache keys)
@dataclass(frozen=True)
class Point:
    x: float
    y: float

p = Point(1.0, 2.0)
hash(p)  # hashable because frozen
```

## Solution: F-Strings

F-strings are the most readable, fastest string interpolation method in Python 3.6+.

```python
name = "Alice"
score = 98.765

# Older styles — avoid
msg = "Hello, %s! Score: %.1f" % (name, score)
msg = "Hello, {}! Score: {:.1f}".format(name, score)

# Good: f-string
msg = f"Hello, {name}! Score: {score:.1f}"

# Expressions inside f-strings
items = [1, 2, 3]
summary = f"Items: {len(items)}, Total: {sum(items)}"

# Multi-line f-strings
query = (
    f"SELECT * FROM users "
    f"WHERE id = {user_id} "
    f"AND is_active = true"
)
```

## Solution: Walrus Operator

The walrus operator `:=` assigns a value and uses it in the same expression, avoiding repeated calls.

```python
import re

# Without walrus: call match() twice or use a temp variable awkwardly
if re.search(r'\d+', text):
    m = re.search(r'\d+', text)  # called twice
    print(m.group())

# With walrus:
if m := re.search(r'\d+', text):
    print(m.group())

# In while loop:
while chunk := f.read(8192):
    process(chunk)

# In list comprehension (filter with computation):
results = [processed for item in items if (processed := transform(item)) is not None]
```

## Solution: Structural Pattern Matching (Python 3.10+)

Pattern matching (`match`/`case`) handles complex conditional dispatch more cleanly than chained if/elif.

```python
# Instead of cascading isinstance checks:
def process_event(event: dict):
    match event:
        case {"type": "click", "x": x, "y": y}:
            handle_click(x, y)
        case {"type": "keypress", "key": key} if key.isalpha():
            handle_keypress(key)
        case {"type": "resize", "width": w, "height": h}:
            handle_resize(w, h)
        case _:
            logger.warning("Unknown event: %s", event)
```

## When to Use

Always prefer these Python-native patterns over generic approaches. These are not style preferences — they affect readability, performance, and maintainability.

## When NOT to Use

- Do not use comprehensions for complex multi-step logic — a for loop with readable variable names may be clearer.
- Do not use walrus operator where it reduces clarity.
- Avoid deeply nested generators/comprehensions — extract into named functions.

## Related Patterns

- `py-pattern-002` — Type Hints Guide
- `beh-007` — Python-Specific Instructions
