---
id: "beh-001"
title: "Code Review Instructions"
category: "behavioral"
language: "all"
version: "1.0.0"
created_at: "2026-02-24"
tags:
  - code-review
  - behavioral
  - null-handling
  - error-handling
  - validation
---

# Code Review Instructions

When reviewing code, follow these instructions exactly.

## Always Check

- **Null/None handling**: Verify every variable that can be null/None is checked before use. Flag unguarded dereferences.
- **Error handling completeness**: Verify all calls to external services, file system, network, and databases have error handling. Bare except/catch with no action is always flagged.
- **Input validation**: Verify all inputs from external sources (HTTP requests, file reads, env vars, CLI args) are validated before use. Check for type, range, and format validation at system boundaries.
- **Resource cleanup**: Verify files, database connections, locks, sockets, and threads are closed/released in all code paths, including error paths. Context managers and using/with blocks should be used wherever available.

## Always Flag

Format all findings as: `[CRITICAL|WARNING|SUGGESTION] description → fix`

- **Magic numbers**: Any unexplained numeric constant in logic (not 0, 1, or -1 for simple indexing). Flag with [SUGGESTION] → extract to named constant.
- **Deeply nested logic**: More than 3 levels of nesting. Flag with [WARNING] → suggest guard clauses, early returns, or extraction to functions.
- **Functions over 50 lines**: Flag with [WARNING] → suggest decomposition into smaller named functions.
- **Duplicate code blocks**: Code copied more than once. Flag with [WARNING] → suggest extraction to a shared function.

## Always Suggest

- **Type hints/annotations**: Where function signatures or critical variables lack type information. Add as [SUGGESTION].
- **Docstrings for public APIs**: Public functions and classes without documentation. Add as [SUGGESTION].
- **Unit test coverage for edge cases**: Note missing coverage for: empty input, None/null input, maximum boundaries, concurrent access, and error paths. Add as [SUGGESTION].

## Never Do

- **Never rewrite working code** without an explicit request to refactor. A code review comments on existing code, it does not replace it.
- **Never change function signatures** without explicitly noting it as a breaking change. Always mention: "This changes the public API — callers must be updated."
- **Never introduce new dependencies** without noting them: "This adds a dependency on [library]. Ensure it is approved and pinned in requirements/package.json."

## Review Output Format

Structure findings by severity, most critical first:

```
## Code Review: [filename or function]

### CRITICAL
[CRITICAL] Unguarded null dereference on line 42: `user.profile.name` — user may be null here
→ Fix: Check `if user and user.profile` before accessing, or use optional chaining

### WARNING
[WARNING] Exception caught but not handled on line 78: `except Exception: pass`
→ Fix: At minimum, log the exception with exc_info=True, then decide: re-raise, return default, or alert

[WARNING] Function `process_data` is 87 lines (line 12–99)
→ Fix: Extract validation (lines 12–35) and transformation (lines 36–70) into separate functions

### SUGGESTION
[SUGGESTION] Missing type hints on `calculate_discount(price, rate)`
→ Fix: `def calculate_discount(price: float, rate: float) -> float:`
```
