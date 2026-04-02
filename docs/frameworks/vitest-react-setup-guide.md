---
id: "doc-010"
title: "Vitest React Setup Guide"
category: "doc"
language: "javascript"
version: "1.1.0"
created_at: "2026-03-07"
updated_at: "2026-04-02"
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

## Do NOT generate tests for scaffold config files

`postcss.config.mjs`, `vitest.config.js`, `vite.config.js`, and `vitest.setup.js` are
framework scaffolding — not application logic. Never auto-generate `.test.` files for them.

Two failures result when you do:
1. Auto-generators default to `node:test`/`assert` (incompatible with Vitest) — the
   baseline run fails before component tests even execute.
2. Tests call `require('../postcss.config.mjs')` on an ESM-only file — throws `ERR_REQUIRE_ESM`.
3. Tests that try to dynamically `import()` `vitest.config.js` inside a test run will fail
   because importing a Vitest config from within Vitest itself creates circular issues.

## Multi-file TEST step: always include file-path comment headers

When a plan step targets multiple test files (e.g., `Header.test.jsx`, `Hero.test.jsx`,
`App.test.jsx`) and provides all their content in one content block, each section MUST
start with a `// path/to/file.ext` comment so the parser can split them correctly:

```jsx
// src/components/Header.test.jsx
import { render, screen } from '@testing-library/react'
...Header tests...

// src/components/Hero.test.jsx
import { render, screen } from '@testing-library/react'
...Hero tests...

// src/App.test.jsx
import { render, screen } from '@testing-library/react'
...App tests...
```

Without these headers, ALL content gets written to the first target file, causing duplicate
`import` declarations and broken relative import paths.

## Testing components that use react-router-dom

Components that use `<Link>`, `<NavLink>`, or Router hooks MUST be wrapped in
`<MemoryRouter>` in tests. Never use `<BrowserRouter>` in tests.

```jsx
import { MemoryRouter } from 'react-router-dom'

it('renders nav links', () => {
  render(
    <MemoryRouter>
      <Header />
    </MemoryRouter>
  )
  expect(screen.getByRole('link', { name: /home/i })).toBeInTheDocument()
})
```

If the component under test is `App` and `App` already contains `<BrowserRouter>`,
do NOT add another `<MemoryRouter>` wrapper — that causes "You cannot render a
`<Router>` inside another `<Router>`". Instead render `<App />` directly, or mock
`BrowserRouter` to use `MemoryRouter`:

```jsx
vi.mock('react-router-dom', async () => {
  const actual = await vi.importActual('react-router-dom')
  return {
    ...actual,
    BrowserRouter: ({ children }) => (
      <actual.MemoryRouter initialEntries={['/']}>{children}</actual.MemoryRouter>
    ),
  }
})

render(<App />) // no extra MemoryRouter wrapper needed
```

## Testing Tailwind-styled components

Use `toHaveClass()`, never regex on `className`. Tailwind modifier classes (`md:flex`,
`hover:bg-cyan-300`, `-translate-x-full`) break regex word-boundary matching.

```js
// WRONG
expect(element.className).toMatch(/md:hidden/)

// CORRECT
expect(element).toHaveClass('md:hidden')
expect(element).not.toHaveClass('hidden')
```
