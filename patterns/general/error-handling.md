---
id: "gen-pattern-002"
title: "Error Handling Patterns"
category: "pattern"
language: "all"
version: "1.0.0"
created_at: "2026-02-24"
tags:
  - error-handling
  - exceptions
  - retry
  - circuit-breaker
  - logging
---

# Error Handling Patterns

## Problem

Silent failures that corrupt state, swallowed exceptions that hide bugs, inconsistent error reporting, and missing retry logic that causes transient failures to become user-facing errors.

## Solution: Never Swallow Exceptions

Catching an exception without handling it or re-raising it destroys diagnostic information and causes silent data corruption or undefined state.

**Python:**
```python
# Bad: swallowing the exception loses all context
try:
    result = risky_operation()
except Exception:
    pass  # NEVER do this

# Bad: bare except catches KeyboardInterrupt, SystemExit too
try:
    result = risky_operation()
except:
    pass

# Good: catch specific exceptions and handle or re-raise with context
try:
    result = risky_operation()
except ValueError as e:
    logger.warning("Invalid input for risky_operation: %s", e)
    return default_value
except IOError as e:
    logger.error("IO failure in risky_operation", exc_info=True)
    raise RuntimeError("Storage unavailable") from e
```

**JavaScript:**
```javascript
// Bad: swallowing in async code
async function fetchUser(id) {
  try {
    return await api.getUser(id);
  } catch (err) {
    // nothing — caller gets undefined, thinks everything is fine
  }
}

// Good: propagate or handle with intent
async function fetchUser(id) {
  try {
    return await api.getUser(id);
  } catch (err) {
    if (err.status === 404) return null;  // intentional: not found is valid
    logger.error({ err, userId: id }, 'Failed to fetch user');
    throw err;  // propagate unexpected errors
  }
}
```

## Solution: Log with Context

Log messages should include enough context to diagnose the problem without access to the machine or session.

**Python:**
```python
import logging

logger = logging.getLogger(__name__)

# Bad: no context
logger.error("Failed to process order")

# Good: include IDs, operation, and exception info
logger.error(
    "Failed to process order %s for user %s: %s",
    order_id,
    user_id,
    str(e),
    exc_info=True,  # includes full stack trace in log
)
```

**JavaScript (structured logging with pino/winston):**
```javascript
// Bad
console.error('Request failed');

// Good: structured log with context
logger.error({
  err,
  userId: req.user?.id,
  path: req.path,
  requestId: req.id,
}, 'Request processing failed');
```

## Solution: Fail Fast Principle

Validate inputs at the entry point of functions and fail early with clear messages. This prevents errors from propagating deep into the call stack where the root cause is obscured.

**Python:**
```python
def calculate_tax(amount: float, rate: float) -> float:
    # Fail fast: validate before any computation
    if amount < 0:
        raise ValueError(f"Amount must be non-negative, got {amount}")
    if not 0 <= rate <= 1:
        raise ValueError(f"Rate must be between 0 and 1, got {rate}")

    return amount * rate
```

## Solution: Retry with Exponential Backoff

For transient failures (network timeouts, rate limits), retry with increasing delays to avoid overwhelming the failing service.

**Python:**
```python
import time
import logging

logger = logging.getLogger(__name__)

def retry_with_backoff(func, max_attempts: int = 3, base_delay: float = 1.0):
    """Retry func up to max_attempts times with exponential backoff."""
    for attempt in range(1, max_attempts + 1):
        try:
            return func()
        except (IOError, TimeoutError) as e:
            if attempt == max_attempts:
                raise
            delay = base_delay * (2 ** (attempt - 1))
            logger.warning(
                "Attempt %d/%d failed: %s. Retrying in %.1fs",
                attempt, max_attempts, e, delay
            )
            time.sleep(delay)
```

**JavaScript:**
```javascript
async function retryWithBackoff(fn, maxAttempts = 3, baseDelay = 1000) {
  for (let attempt = 1; attempt <= maxAttempts; attempt++) {
    try {
      return await fn();
    } catch (err) {
      if (attempt === maxAttempts) throw err;
      const delay = baseDelay * Math.pow(2, attempt - 1);
      logger.warn({ err, attempt, delay }, 'Retrying after failure');
      await new Promise(resolve => setTimeout(resolve, delay));
    }
  }
}
```

## Solution: Circuit Breaker Pattern

Prevent cascading failures by temporarily stopping calls to a failing service. After a threshold of failures, "open" the circuit; after a cooldown, allow trial calls to test recovery.

**Python (conceptual implementation):**
```python
import time
from enum import Enum

class CircuitState(Enum):
    CLOSED = "closed"      # normal operation
    OPEN = "open"          # blocking all calls
    HALF_OPEN = "half_open"  # testing recovery

class CircuitBreaker:
    def __init__(self, failure_threshold: int = 5, recovery_timeout: float = 30.0):
        self.failure_threshold = failure_threshold
        self.recovery_timeout = recovery_timeout
        self.failure_count = 0
        self.last_failure_time = None
        self.state = CircuitState.CLOSED

    def call(self, func, *args, **kwargs):
        if self.state == CircuitState.OPEN:
            if time.time() - self.last_failure_time > self.recovery_timeout:
                self.state = CircuitState.HALF_OPEN
            else:
                raise RuntimeError("Circuit breaker is OPEN — service unavailable")

        try:
            result = func(*args, **kwargs)
            self._on_success()
            return result
        except Exception as e:
            self._on_failure()
            raise

    def _on_success(self):
        self.failure_count = 0
        self.state = CircuitState.CLOSED

    def _on_failure(self):
        self.failure_count += 1
        self.last_failure_time = time.time()
        if self.failure_count >= self.failure_threshold:
            self.state = CircuitState.OPEN
```

## When to Use

- In every function that calls external services, file system, network, or database.
- At API boundaries: validate inputs with clear error messages before processing.
- For idempotent operations that may transiently fail: retry with backoff.
- For critical downstream dependencies: circuit breaker to prevent cascade failures.

## When NOT to Use

- Do not retry non-idempotent operations (e.g., creating a payment charge) without deduplication.
- Do not add circuit breakers for operations that are trivially fast and local.
- Do not retry on non-transient errors (e.g., validation errors, auth failures): retrying won't help.

## Related Patterns

- `gen-pattern-001` — Clean Code Principles
- `gen-pattern-003` — Async Patterns
- `beh-002` — Error Analysis Instructions
