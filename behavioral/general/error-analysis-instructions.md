---
id: "beh-002"
title: "Error Analysis Instructions"
category: "behavioral"
language: "all"
version: "1.0.0"
created_at: "2026-02-24"
tags:
  - error-analysis
  - behavioral
  - debugging
  - stack-trace
---

# Error Analysis Instructions

When analyzing errors and stack traces, follow these instructions exactly.

## Always

- **Read the full stack trace top to bottom before responding.** The first line is the exception type and message. The stack frames show the call chain. The bottom-most frame in user code is usually closest to the root cause.
- **Identify the root cause**, not just the surface error. "AttributeError: 'NoneType' has no attribute 'name'" is not the root cause — the root cause is why the variable is None. Trace back to find where it became None.
- **Check if the error is in user code vs library code.** If the top frames are in third-party libraries and the bottom frames are in user code, look at the user code frames — that is where the mistake is. If all frames are in user code, the bug is directly visible.

## Always Provide

- **Exact file and line number** of the most relevant frame (the highest frame in user code that precedes the error).
- **Root cause explanation**: a 1-3 sentence plain-English explanation of WHY the error occurred, not just WHAT the error says.
- **Minimal fix code snippet**: show the specific change needed, not a complete rewrite. The fix should be as small as possible while still being correct.
- **How to verify the fix works**: specify a test input, assertion, or command that confirms the fix resolved the issue.

## Never

- **Never guess without evidence from the stack trace.** If the stack trace does not provide enough information, say what additional information is needed (e.g., print the value of X at line Y) rather than speculating.
- **Never provide a fix without explaining why it works.** Each fix must be accompanied by a one-sentence explanation connecting the cause to the solution.
- **Never ignore related warnings above the error line.** Warnings that appear before the exception in logs often indicate the root cause. Always mention them if present.

## When Error is in a Library

- First check if this is a known issue: look for the error message pattern in the KB. If found, apply the KB fix directly.
- If the library version is relevant, suggest checking and potentially pinning it: "Consider verifying you're on version X.Y.Z, as this was a known bug in earlier versions."
- Always check library documentation first before suggesting a workaround. Workarounds should note that they are workarounds.

## Analysis Output Format

```
## Error Analysis

**Error:** `AttributeError: 'NoneType' object has no attribute 'email'`
**Location:** `src/services/user.py:142` in `send_notification()`

**Root Cause:**
`find_user_by_id()` returns `None` when the user ID does not exist in the database,
but `send_notification()` does not check for this before accessing `user.email`.

**Fix:**
```python
# Before (line 140-143):
user = find_user_by_id(user_id)
send_email(user.email, template)

# After:
user = find_user_by_id(user_id)
if user is None:
    logger.warning("Cannot notify: user %s not found", user_id)
    return
send_email(user.email, template)
```

**Why this works:** The guard clause exits early when `user` is `None`,
preventing the attribute access that causes the error.

**Verify:** Call `send_notification(user_id=999999)` with a non-existent ID
and confirm it logs the warning and returns without raising.
```
