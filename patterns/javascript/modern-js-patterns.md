---
id: "js-pattern-001"
title: "Modern JavaScript Patterns"
category: "pattern"
language: "javascript"
version: "1.0.0"
created_at: "2026-02-24"
tags:
  - javascript
  - es2020
  - destructuring
  - optional-chaining
  - modules
  - promises
---

# Modern JavaScript Patterns

## Problem

JavaScript code that relies on older idioms — manual null checks, verbose object access, unstructured callbacks, and CommonJS modules that prevent tree-shaking and static analysis.

## Solution: Destructuring

Extract values from objects and arrays concisely, with defaults for missing values.

```javascript
// Object destructuring
const { name, email, role = 'user' } = user;

// Rename during destructure
const { id: userId, name: userName } = user;

// Nested destructuring
const { address: { city, country = 'US' } } = user;

// Array destructuring
const [first, second, ...rest] = items;

// Function parameter destructuring
function renderUser({ name, email, role = 'user' }) {
  return `${name} <${email}> [${role}]`;
}

// Swap variables without temp
[a, b] = [b, a];
```

## Solution: Spread and Rest

```javascript
// Spread: create new array/object without mutating
const updated = { ...user, email: 'new@example.com' };  // shallow clone + override
const merged = { ...defaults, ...userConfig };            // merge objects

// Array spread
const combined = [...arrayA, ...arrayB];
const copy = [...original];

// Rest: collect remaining arguments
function log(level, ...messages) {
  console.log(`[${level}]`, ...messages);
}
```

## Solution: Optional Chaining and Nullish Coalescing

```javascript
// Optional chaining: safely traverse deep objects
const city = user?.address?.city;            // undefined if any step is null/undefined
const handler = config?.onSuccess?.bind(this); // method on possibly-null object

// Optional chaining with method calls
const len = str?.length;                      // undefined if str is null/undefined
const trimmed = value?.trim?.();              // call only if trim is a function

// Nullish coalescing: default only for null/undefined (not 0 or '')
const port = config.port ?? 3000;             // 0 is a valid port — don't use || here
const name = user.name ?? 'Anonymous';

// Combined
const displayName = user?.profile?.displayName ?? user?.name ?? 'Anonymous';
```

## Solution: Promise.all vs Promise.allSettled

```javascript
// Promise.all: resolves when ALL resolve, rejects on FIRST failure
const [profile, settings] = await Promise.all([
  fetchProfile(userId),
  fetchSettings(userId),
]);
// If either rejects, the whole Promise.all rejects immediately

// Promise.allSettled: waits for ALL, collects results AND rejections
const results = await Promise.allSettled([
  fetchProfile(userId),
  fetchSettings(userId),
  fetchNotifications(userId),
]);

results.forEach((result, i) => {
  if (result.status === 'fulfilled') {
    console.log(`Request ${i} succeeded:`, result.value);
  } else {
    console.warn(`Request ${i} failed:`, result.reason);
  }
});

// Promise.race: resolves/rejects with the FIRST to settle (good for timeouts)
const data = await Promise.race([
  fetchData(),
  new Promise((_, reject) => setTimeout(() => reject(new Error('Timeout')), 5000)),
]);
```

## Solution: Async Iterators

Process large asynchronous datasets one item at a time, without loading all into memory.

```javascript
// Async generator function
async function* fetchPages(baseUrl) {
  let page = 1;
  while (true) {
    const res = await fetch(`${baseUrl}?page=${page}`);
    const data = await res.json();
    if (!data.items.length) return;  // no more pages
    yield* data.items;
    page++;
  }
}

// Consume with for-await-of
for await (const item of fetchPages('https://api.example.com/items')) {
  await processItem(item);
}
```

## Solution: ESM vs CommonJS

Prefer ESM (ES Modules) for new code. It enables static analysis, tree-shaking, and top-level await.

```javascript
// CommonJS (older Node.js — avoid for new code)
const path = require('path');
const { readFile } = require('fs/promises');
module.exports = { myFunction };

// ESM (modern — use this)
import path from 'path';
import { readFile } from 'fs/promises';
export { myFunction };
export default class MyService { ... }

// package.json to enable ESM in Node.js:
// { "type": "module" }
// Or use .mjs extension for ESM files

// Top-level await (ESM only)
const config = await loadConfig();  // no wrapping async function needed
```

## When to Use

- Always use optional chaining (`?.`) and nullish coalescing (`??`) instead of manual null checks.
- Use `Promise.allSettled` when you need results from all operations even if some fail.
- Use destructuring in function parameters for objects with 2+ properties.
- Prefer ESM for new modules; use CommonJS only when targeting older Node.js or library compatibility.

## When NOT to Use

- Do not use `||` as a null check when `0`, `''`, or `false` are valid values — use `??` instead.
- Do not spread deeply nested objects expecting a deep clone — spread is shallow.
- Do not use `Promise.all` for fire-and-forget side effects — use `Promise.allSettled` or individual awaits.

## Related Patterns

- `ts-pattern-001` — Strict TypeScript Patterns
- `gen-pattern-003` — Async Patterns
