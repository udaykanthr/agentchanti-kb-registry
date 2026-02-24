---
id: "adr-002"
title: "ADR-002: Use Tree-sitter for AST Parsing"
category: "adr"
language: "all"
version: "1.0.0"
created_at: "2026-02-24"
tags:
  - parsing
  - ast
  - tree-sitter
  - multi-language
---

# ADR-002: Use Tree-sitter for AST Parsing

## Status

Accepted

## Context

AgentChanti needs to parse source code into an Abstract Syntax Tree (AST) to:

1. Understand code structure (functions, classes, imports, call graphs)
2. Extract semantic features for indexing (function signatures, dependencies)
3. Build the code graph used for navigation and cross-reference
4. Support multiple languages (Python, JavaScript, TypeScript, Java, Go, Rust, C#)
5. Handle real-world code that may be syntactically incomplete or have errors

The parser must:
- Support all languages AgentChanti targets without separate parsing stacks
- Parse efficiently — ideally incrementally (only re-parse changed regions)
- Work with code that has syntax errors (graceful partial parsing)
- Be maintainable — we don't want to write grammars from scratch

## Decision

We will use **Tree-sitter** via the `py-tree-sitter` Python bindings for all AST parsing.

Each language requires its compiled grammar installed as a language-specific package (e.g., `tree-sitter-python`, `tree-sitter-javascript`).

```python
from tree_sitter import Language, Parser
import tree_sitter_python as tspython
import tree_sitter_javascript as tsjavascript

# Build language objects
PY_LANGUAGE = Language(tspython.language())
JS_LANGUAGE = Language(tsjavascript.language())

# Create and configure a parser
parser = Parser(PY_LANGUAGE)

# Parse source code
source = b"""
def greet(name: str) -> str:
    return f"Hello, {name}"
"""

tree = parser.parse(source)
root = tree.root_node

# Walk the AST
def extract_functions(node):
    functions = []
    if node.type == 'function_definition':
        name_node = node.child_by_field_name('name')
        functions.append(name_node.text.decode('utf-8'))
    for child in node.children:
        functions.extend(extract_functions(child))
    return functions

print(extract_functions(root))  # ['greet']

# Incremental parsing: only re-parse changed regions
new_source = b"""
def greet(name: str) -> str:
    return f"Hello, {name}!"  # added !
"""
new_tree = parser.parse(new_source, tree)  # reuses unchanged nodes
```

## Consequences

**Positive:**
- Single parsing stack for all supported languages — reduced maintenance burden
- Incremental parsing is built-in — re-parsing a changed file only processes the diff
- Error recovery: Tree-sitter produces a valid (partial) AST even for syntactically broken code
- Battle-tested: used in GitHub's code intelligence, Neovim, and many other production tools
- S-expression query language for pattern matching within ASTs (powerful for code analysis)
- Rust-based core — very fast parsing, even for large files

**Negative:**
- Grammar packages must be installed per language (`pip install tree-sitter-python`, etc.)
- The `py-tree-sitter` API is low-level — building higher-level abstractions requires effort
- Grammar support for newer language features may lag behind official language releases
- Binary wheel builds (C extension) may complicate deployment in restrictive environments

**Risks:**
- Grammar version mismatches between tree-sitter and tree-sitter-{language} packages could cause failures (mitigation: pin versions in requirements.txt, test matrix per version)

## Alternatives Considered

### Language-Specific Parsers (ast module, javalang, etc.)
- **Python**: `ast` module — excellent for Python-only, stdlib, no dependencies
- **JavaScript/TypeScript**: `acorn`, `@typescript-eslint/parser`
- **Java**: `javalang`
- **Pros**: Each is best-in-class for its own language
- **Cons**: Requires N separate parsing stacks, N maintenance paths, N different APIs. Cannot be abstracted cleanly
- **Why rejected**: Maintenance burden is unacceptable; building a unified abstraction over 7 different AST APIs would require significant engineering

### ctags / Universal Ctags
- **Pros**: Multi-language, battle-tested, simple setup, produces symbol index
- **Cons**: Produces symbol tables, not full ASTs. Cannot express structural queries. No type information. Not suitable for code graph construction
- **Why rejected**: Not an AST parser — only produces symbol indexes. Cannot answer structural questions like "what methods does class X call?"

### Pygments
- **Pros**: Multi-language, pure Python, used for syntax highlighting
- **Cons**: Tokenizer only — produces tokens, not a tree structure. No structural information at all
- **Why rejected**: Lexer, not a parser. Cannot determine code structure from tokens alone

### ANTLR Grammars
- **Pros**: Extremely powerful, used in professional compilers
- **Cons**: JVM dependency (or complex polyglot build), grammars are maintained separately and can be outdated, significantly more complex than Tree-sitter
- **Why rejected**: JVM dependency violates the local-first, lightweight design goal
