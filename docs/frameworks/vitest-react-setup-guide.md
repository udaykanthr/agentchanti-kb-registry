---
id: "doc-010"
title: "Vitest React Setup Guide"
category: "doc"
language: "javascript"
version: "1.0.0"
created_at: "2026-03-07"
tags:
  - vitest
  - react
  - vite
  - testing
  - setup
  - guide
---

## Overview

When setting up a React project with Vitest and @testing-library/react, the following
packages are ALL required. Missing any of these causes hard-to-debug import/runtime errors.

## Required Dev Packages (complete list)

```bash
npm install --save-dev vitest jsdom @testing-library/react @testing-library/dom @testing-library/jest-dom @testing-library/user-event @vitejs/plugin-react
```

### Package purposes:
| Package | Purpose | Error if missing |
|---------|---------|-----------------|
| `vitest` | Test runner | `vitest: command not found` |
| `jsdom` | DOM environment for tests | `Error: Failed to find a valid JSDOM implementation` or `ReferenceError: document is not defined` |
| `@testing-library/react` | `render()`, `screen` queries | `Cannot find module '@testing-library/react'` |
| `@testing-library/dom` | Core DOM queries (peer dep of @testing-library/react) | `Cannot find module '@testing-library/dom'` |
| `@testing-library/jest-dom` | Custom matchers: `toBeInTheDocument()`, `toHaveClass()` | `TypeError: expect(...).toBeInTheDocument is not a function` |
| `@testing-library/user-event` | Realistic user interactions: `userEvent.click()` | `Cannot find module '@testing-library/user-event'` |
| `@vitejs/plugin-react` | JSX transform for Vite | `[plugin:vite:esbuild] Failed to parse source for import analysis` |

## Required vitest.config.js

```js
import { defineConfig } from 'vitest/config'
import react from '@vitejs/plugin-react'

export default defineConfig({
  plugins: [react()],
  test: {
    environment: 'jsdom',
    globals: true,
    setupFiles: './vitest.setup.js',
  },
})
```

## Required vitest.setup.js

```js
import '@testing-library/jest-dom/vitest'
```

**CRITICAL**: Use `@testing-library/jest-dom/vitest` (NOT `@testing-library/jest-dom`).
The base import only works with Jest. The `/vitest` subpath registers matchers correctly
with Vitest's `expect`.

## Common mistakes

1. **Missing `jsdom`**: Vitest defaults to `node` environment. Without `jsdom`, there is
   no `document`, `window`, or DOM — all component renders fail silently or crash.
2. **Missing `@testing-library/dom`**: This is a peer dependency of `@testing-library/react`.
   npm v7+ auto-installs peer deps, but older versions or CI environments may not.
3. **Wrong jest-dom import**: `import '@testing-library/jest-dom'` in Vitest causes
   `expect.extend is not a function` or matchers not being registered.
4. **Missing `@vitejs/plugin-react`**: Without the React plugin, Vite cannot transform
   JSX in `.jsx`/`.tsx` files, causing parse errors in tests.
