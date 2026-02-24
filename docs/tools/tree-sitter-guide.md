---
id: "doc-001"
title: "Tree-sitter Guide for AgentChanti"
category: "doc"
language: "python"
version: "1.0.0"
created_at: "2026-02-24"
tags:
  - tree-sitter
  - parsing
  - ast
  - code-analysis
  - py-tree-sitter
---

# Tree-sitter Guide for AgentChanti

## Installation

```bash
pip install tree-sitter tree-sitter-python tree-sitter-javascript tree-sitter-typescript
# Add additional languages as needed:
# pip install tree-sitter-java tree-sitter-go tree-sitter-rust
```

## Loading Grammars

```python
from tree_sitter import Language, Parser
import tree_sitter_python as tspython
import tree_sitter_javascript as tsjavascript
import tree_sitter_typescript as tstypescript

# Build Language objects from the compiled grammar
PY_LANGUAGE = Language(tspython.language())
JS_LANGUAGE = Language(tsjavascript.language())
TS_LANGUAGE = Language(tstypescript.language_typescript())
TSX_LANGUAGE = Language(tstypescript.language_tsx())

# Convenience map
LANGUAGE_MAP = {
    'python': PY_LANGUAGE,
    'javascript': JS_LANGUAGE,
    'typescript': TS_LANGUAGE,
    'tsx': TSX_LANGUAGE,
}

def get_parser(language: str) -> Parser:
    lang = LANGUAGE_MAP.get(language)
    if not lang:
        raise ValueError(f"Unsupported language: {language}")
    return Parser(lang)
```

## Parsing Code

```python
from tree_sitter import Parser
import tree_sitter_python as tspython

parser = Parser(Language(tspython.language()))

# Parse from bytes (preferred — avoids encoding issues)
source_bytes = b"""
def calculate_tax(amount: float, rate: float) -> float:
    if amount < 0:
        raise ValueError(f"Amount must be non-negative, got {amount}")
    return amount * rate
"""

tree = parser.parse(source_bytes)
root = tree.root_node

print(root.type)               # 'module'
print(root.start_point)        # (0, 0)
print(root.end_point)          # (row, col)
print(root.has_error)          # True if parse had errors

# Parse from string (encode to bytes first)
source = "def hello(): return 42"
tree = parser.parse(source.encode('utf-8'))
```

## Walking the AST

```python
def walk_ast(node, depth=0):
    """Recursively walk the AST and print node types."""
    indent = '  ' * depth
    text = node.text.decode('utf-8') if node.is_named else node.type
    print(f"{indent}{node.type}: {repr(text[:50])}")
    for child in node.children:
        walk_ast(child, depth + 1)

# Using a cursor for efficient traversal (no recursion overhead)
cursor = root.walk()
cursor.goto_first_child()
while True:
    node = cursor.node
    # process node
    if not cursor.goto_first_child():
        if not cursor.goto_next_sibling():
            cursor.goto_parent()
            if not cursor.goto_next_sibling():
                break
```

## Extracting Functions and Classes

```python
def extract_definitions(source: bytes, language: str) -> list[dict]:
    """Extract function and class definitions from source code."""
    parser = get_parser(language)
    tree = parser.parse(source)

    definitions = []
    _extract_recursive(tree.root_node, source, definitions)
    return definitions

def _extract_recursive(node, source: bytes, results: list):
    if node.type in ('function_definition', 'async_function_definition'):
        name_node = node.child_by_field_name('name')
        params_node = node.child_by_field_name('parameters')
        if name_node:
            results.append({
                'type': 'function',
                'name': name_node.text.decode('utf-8'),
                'start_line': node.start_point[0] + 1,
                'end_line': node.end_point[0] + 1,
                'is_async': node.type == 'async_function_definition',
            })

    elif node.type == 'class_definition':
        name_node = node.child_by_field_name('name')
        if name_node:
            results.append({
                'type': 'class',
                'name': name_node.text.decode('utf-8'),
                'start_line': node.start_point[0] + 1,
            })

    for child in node.children:
        _extract_recursive(child, source, results)
```

## Querying with S-expressions

Tree-sitter's query language is much faster than manual traversal for pattern matching.

```python
from tree_sitter import Language, Parser, Query
import tree_sitter_python as tspython

PY_LANGUAGE = Language(tspython.language())

# S-expression query: find all function calls
call_query = PY_LANGUAGE.query("""
(call
  function: (attribute
    object: (identifier) @object
    attribute: (identifier) @method)
  arguments: (argument_list) @args)
""")

# Find all function definitions with type hints
function_query = PY_LANGUAGE.query("""
(function_definition
  name: (identifier) @name
  parameters: (parameters) @params
  return_type: (type) @return_type)
""")

source = b"""
def greet(name: str) -> str:
    return f"Hello, {name}"

class Greeter:
    def wave(self) -> None:
        pass
"""

parser = Parser(PY_LANGUAGE)
tree = parser.parse(source)

# Run the query
matches = function_query.matches(tree.root_node)
for pattern_index, capture_dict in matches:
    name = capture_dict['name'][0].text.decode('utf-8')
    print(f"Function: {name}")

# captures() is simpler for flat results
for node, capture_name in function_query.captures(tree.root_node):
    if capture_name == 'name':
        print(f"Function name: {node.text.decode('utf-8')}")
```

## Handling Parse Errors

```python
def parse_with_error_handling(source: bytes, language: str) -> tuple:
    """Returns (tree, errors) where errors is a list of error positions."""
    parser = get_parser(language)
    tree = parser.parse(source)
    errors = []

    if tree.root_node.has_error:
        # Find all ERROR and MISSING nodes
        def find_errors(node):
            if node.type in ('ERROR', 'MISSING'):
                errors.append({
                    'type': node.type,
                    'start': node.start_point,
                    'end': node.end_point,
                    'text': node.text.decode('utf-8', errors='replace'),
                })
            for child in node.children:
                find_errors(child)

        find_errors(tree.root_node)

    return tree, errors

tree, errors = parse_with_error_handling(b"def foo(: pass", 'python')
if errors:
    for error in errors:
        print(f"Parse error at {error['start']}: {error['text']}")
```

## Incremental Parsing for File Changes

```python
def update_parse(old_tree, old_source: bytes, new_source: bytes, language: str):
    """
    Incrementally re-parse changed regions only.
    Much faster than a full re-parse for small edits.
    """
    parser = get_parser(language)

    # Compute the diff to create edit records
    # For simplicity, this example replaces entire content
    # In production: compute precise byte ranges of changes
    edit_start_byte = 0
    old_end_byte = len(old_source)
    new_end_byte = len(new_source)

    old_start_point = (0, 0)
    old_end_point = old_tree.root_node.end_point
    new_end_point = (new_source.count(b'\n'), len(new_source.split(b'\n')[-1]))

    old_tree.edit(
        start_byte=edit_start_byte,
        old_end_byte=old_end_byte,
        new_end_byte=new_end_byte,
        start_point=old_start_point,
        old_end_point=old_end_point,
        new_end_point=new_end_point,
    )

    # Re-parse using the invalidated tree as a hint
    new_tree = parser.parse(new_source, old_tree)
    return new_tree
```

## Performance Tips

- Parse files to bytes (not str) — avoids UTF-8 decoding overhead.
- Use queries (`Language.query()`) instead of manual recursion for pattern matching — they are compiled to optimized C code.
- Use `tree.walk()` cursor for large AST traversals — avoids Python recursion limits and stack overhead.
- Cache `Parser` instances — creating a Parser per call is wasteful.
- Use incremental parsing for frequently-updated files (e.g., files being edited in real-time).
