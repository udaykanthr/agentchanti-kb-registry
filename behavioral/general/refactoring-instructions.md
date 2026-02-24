---
id: "beh-003"
title: "Refactoring Instructions"
category: "behavioral"
language: "all"
version: "1.0.0"
created_at: "2026-02-24"
tags:
  - refactoring
  - behavioral
  - code-quality
  - clean-code
---

# Refactoring Instructions

When refactoring code, follow these instructions exactly.

## Always

- **Understand intent before changing implementation.** Read the function or module completely. Understand what it does and why before proposing any change. Ask clarifying questions if the intent is unclear.
- **Preserve existing behavior.** Refactoring means improving structure without changing behavior. If behavior MUST change as part of the refactoring, call this out explicitly as a separate concern.
- **Make one logical change at a time.** Do not combine: remove duplication AND rename variables AND restructure control flow in one step. Each change should be independently reviewable.

## Always Check After Each Change

- **Existing tests still pass.** Confirm by running the test suite. If tests cannot be run, state this explicitly and flag it as a risk.
- **Public API signatures unchanged** unless explicitly requested. If a signature must change, note every call site that will break.
- **No new external dependencies introduced silently.** Any new import or library must be explicitly called out.

## Refactoring Priorities (Apply in This Order)

1. **Remove duplication.** Identical or near-identical code blocks should be extracted into a shared function. Duplication is the highest priority because it creates the most future maintenance cost.
2. **Improve naming clarity.** Rename variables, functions, and classes to reveal intent. A name that requires a comment to explain it needs to be renamed.
3. **Reduce function length and complexity.** Functions over 30 lines or with cyclomatic complexity > 5 should be decomposed. Extract logical sub-steps into named functions.
4. **Improve error handling.** Replace bare except/catch blocks. Replace swallowed exceptions with appropriate logging and propagation. Add missing error handling at external call sites.
5. **Add type hints and documentation.** Add type annotations to function signatures. Add docstrings to public functions and classes only after the logic is clean.

## Never

- **Never refactor and add features in the same change.** Refactoring changes the structure; feature additions change the behavior. Mixing both makes reviewing impossible and bugs untraceable.
- **Never "improve" working code speculatively** — only refactor code that will be changed, tested, or reviewed. Speculative refactoring in untouched files creates churn without benefit.
- **Never reorder steps inside a function** unless you have proven the steps are independent. Silently reordering steps can introduce timing or state bugs.

## Refactoring Output Format

Present each refactoring step separately:

```
## Refactoring Plan for `process_order()`

### Step 1: Remove Duplication
Lines 45-55 and lines 78-88 contain identical validation logic.
Extract to `validate_order_items(items: list[OrderItem]) -> None`.

### Step 2: Improve Naming
- `d` → `discount_rate` (line 23)
- `calc()` → `calculate_line_item_total()` (line 31)
- `res` → `processed_orders` (line 67)

### Step 3: Reduce Function Length
`process_order()` is 120 lines. Decompose:
- `validate_order(order)` — lines 10-40
- `apply_discounts(order)` — lines 41-65
- `persist_order(order)` — lines 66-90
- `notify_fulfillment(order)` — lines 91-120

### No Behavior Changes
All changes are structural. The public signature `process_order(order: Order) -> ProcessingResult`
is unchanged. All existing tests should pass without modification.
```
