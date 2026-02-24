---
id: "gen-pattern-003"
title: "Async/Await Patterns"
category: "pattern"
language: "all"
version: "1.0.0"
created_at: "2026-02-24"
tags:
  - async
  - await
  - concurrency
  - timeout
  - cancellation
---

# Async/Await Patterns

## Problem

Async code that blocks the event loop, callback hell that is hard to read, parallel operations executed sequentially (wasting time), missing timeout handling, and uncancellable long-running operations.

## Solution: Async/Await over Callbacks

Async/await transforms asynchronous code into a synchronous-looking style that is easier to read, debug, and handle errors in.

**JavaScript (callbacks → promises → async/await):**
```javascript
// Bad: callback hell
readFile('data.txt', (err, data) => {
  if (err) return handleError(err);
  parseJSON(data, (err, parsed) => {
    if (err) return handleError(err);
    saveToDb(parsed, (err, result) => {
      if (err) return handleError(err);
      console.log('Done', result);
    });
  });
});

// Good: async/await — flat, readable, proper error handling
async function processFile() {
  const data = await readFile('data.txt', 'utf8');
  const parsed = JSON.parse(data);
  const result = await saveToDb(parsed);
  console.log('Done', result);
}
```

**Python:**
```python
import asyncio
import aiofiles
import aiohttp

# Bad: blocking I/O in async context (blocks the event loop)
async def bad_fetch():
    import requests  # synchronous library
    response = requests.get('https://api.example.com/data')  # BLOCKS the event loop!
    return response.json()

# Good: use async-native libraries
async def good_fetch():
    async with aiohttp.ClientSession() as session:
        async with session.get('https://api.example.com/data') as response:
            return await response.json()
```

## Solution: Parallel vs Sequential Execution

Sequential execution (one await after another) is correct when operations depend on each other. Parallel execution (concurrent awaits) is correct when operations are independent.

**JavaScript:**
```javascript
// Sequential — correct when step2 needs step1's result
const user = await fetchUser(id);
const orders = await fetchOrders(user.accountId);  // needs user.accountId

// Sequential (wasteful) — step1 and step2 are independent
const userProfile = await fetchProfile(userId);     // 200ms
const settings = await fetchSettings(userId);       // 150ms
// Total: 350ms

// Parallel — correct when operations are independent
const [userProfile, settings] = await Promise.all([
  fetchProfile(userId),   // 200ms ]
  fetchSettings(userId),  // 150ms } run concurrently
]);
// Total: ~200ms (longest)

// Parallel with partial failure handling
const results = await Promise.allSettled([
  fetchProfile(userId),
  fetchSettings(userId),
  fetchNotifications(userId),
]);
results.forEach(result => {
  if (result.status === 'rejected') {
    logger.warn('Partial fetch failed:', result.reason);
  }
});
```

**Python:**
```python
import asyncio

# Sequential (wasteful if independent):
user = await fetch_user(id)       # 100ms
settings = await fetch_settings(id)  # 80ms — could run concurrently!

# Parallel — run concurrently with asyncio.gather
user, settings = await asyncio.gather(
    fetch_user(id),
    fetch_settings(id),
)

# Parallel with individual error handling
results = await asyncio.gather(
    fetch_user(id),
    fetch_settings(id),
    return_exceptions=True,  # don't raise on first failure
)
for result in results:
    if isinstance(result, Exception):
        logger.warning("Partial failure: %s", result)
```

## Solution: Timeout Handling

Never let async operations wait indefinitely. Always set a timeout and handle the timeout case explicitly.

**Python:**
```python
import asyncio

async def fetch_with_timeout(url: str, timeout: float = 5.0):
    try:
        async with asyncio.timeout(timeout):  # Python 3.11+
            return await fetch(url)
    except TimeoutError:
        logger.error("Request to %s timed out after %ss", url, timeout)
        raise  # or return a default value

# Python 3.10 and earlier:
async def fetch_with_timeout_legacy(url: str, timeout: float = 5.0):
    try:
        return await asyncio.wait_for(fetch(url), timeout=timeout)
    except asyncio.TimeoutError:
        raise
```

**JavaScript:**
```javascript
async function fetchWithTimeout(url, timeoutMs = 5000) {
  const controller = new AbortController();
  const timeoutId = setTimeout(() => controller.abort(), timeoutMs);

  try {
    const response = await fetch(url, { signal: controller.signal });
    return await response.json();
  } catch (err) {
    if (err.name === 'AbortError') {
      throw new Error(`Request to ${url} timed out after ${timeoutMs}ms`);
    }
    throw err;
  } finally {
    clearTimeout(timeoutId);  // always clear the timer
  }
}
```

## Solution: Cancellation Patterns

Long-running async operations should be cancellable to enable clean shutdown and resource release.

**Python:**
```python
import asyncio

async def long_running_job(cancel_event: asyncio.Event):
    while not cancel_event.is_set():
        await process_batch()
        await asyncio.sleep(0.1)  # yield to event loop — allows cancellation check
    logger.info("Job cancelled cleanly")

# Cancel from outside:
cancel_event = asyncio.Event()
task = asyncio.create_task(long_running_job(cancel_event))

# Signal cancellation:
cancel_event.set()
await task  # wait for clean shutdown
```

**JavaScript (with AbortController):**
```javascript
async function longRunningJob(signal) {
  while (!signal.aborted) {
    await processBatch();
    // Check between batches
    if (signal.aborted) break;
  }
  console.log('Job cancelled cleanly');
}

const controller = new AbortController();
const jobPromise = longRunningJob(controller.signal);

// Cancel later:
controller.abort();
await jobPromise;
```

## When to Use

- Parallel execution: whenever two or more async operations are independent of each other.
- Timeouts: always on network calls, external service calls, and DB queries.
- Cancellation: long-running jobs, background tasks, and any user-initiated operations.

## When NOT to Use

- Do not use `Promise.all` when the operations must run in a specific order.
- Do not use `asyncio.gather` with `return_exceptions=False` (default) when you need to handle partial failures without aborting.
- Do not add cancellation to operations that are already atomic and fast.

## Related Patterns

- `gen-pattern-002` — Error Handling Patterns
- `py-pattern-001` — Pythonic Patterns
- `js-pattern-001` — Modern JS Patterns
