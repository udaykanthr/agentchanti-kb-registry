---
id: "doc-009"
title: "Vite React Setup Guide"
category: "doc"
language: "javascript"
version: "1.0.0"
created_at: "2026-03-07"
tags:
  - vite
  - react
  - testing
  - setup
  - guide
---

## Overview

Setting up Vite in a React project requires specific packages and configuration
to ensure components render correctly and DOM assertions work.

*** Do not create TS or TSX files if JS or JSX already exists, Update those files insetead ***

## 1. Required Packages

Install the following React vite packages initialization:
*** This step is very important to create necessary files and folders example, src/App.jsx, src/index.jsx, src/main.jsx, src/App.css, src/index.css, vite.config.js, package.json ***

IMPORTANT: In ALL commands below, replace `<project-name>` with the EXACT
project name derived from the user's task description. Use the SAME name
consistently in every step — do NOT invent a different name.

```bash
npm create vite@latest <project-name> -- --template react --no-interactive
```

## 2. Install react dependencies *** Important ***

```bash
npm install react-router-dom prop-types
```

## 3. install NPM packages

```bash
npm install
```
### Execute these installations for first time.

## 4. Actual scaffold output — READ before editing

`npm create vite@latest --template react` generates scaffold files whose exact content
**changes between `create-vite` package versions**.

> **CRITICAL**: NEVER hardcode scaffold file content in `<<<FIND>>>` blocks based on this
> KB doc. The doc may be out of date. Always **READ the actual generated file** immediately
> after the scaffold CMD step and use that content in any subsequent edit step.

### src/main.jsx (stable across versions)

`main.jsx` has been stable across recent versions:

```jsx
import { StrictMode } from 'react'
import { createRoot } from 'react-dom/client'
import './index.css'
import App from './App.jsx'

createRoot(document.getElementById('root')).render(
  <StrictMode>
    <App />
  </StrictMode>,
)
```

**Key differences from older Vite templates:**
- Uses named import `{ StrictMode }` — NOT `import React from 'react'`
- Uses named import `{ createRoot }` — NOT `import ReactDOM from 'react-dom/client'`
- CSS import comes BEFORE the App import
- App import uses explicit `.jsx` extension: `'./App.jsx'` NOT `'./App'`
- No `ReactDOM.createRoot(...)` — uses `createRoot(...)` directly

### src/App.jsx (version-dependent — always read the actual file)

> **WARNING**: `App.jsx` scaffold content differs by `create-vite` version. The example
> below is one known version. **Do not use it in a `<<<FIND>>>` block without first reading
> the actual file.** Mismatched FIND content silently falls through to the coder, producing
> conflicting diffs and broken imports.

One known version (older):

```jsx
import { useState } from 'react'
import reactLogo from './assets/react.svg'
import viteLogo from '/vite.svg'
import './App.css'

function App() {
  const [count, setCount] = useState(0)

  return (
    <>
      <div>
        <a href="https://vite.dev" target="_blank">
          <img src={viteLogo} className="logo" alt="Vite logo" />
        </a>
        <a href="https://react.dev" target="_blank">
          <img src={reactLogo} className="logo react" alt="React logo" />
        </a>
      </div>
      <h1>Vite + React</h1>
      <div className="card">
        <button onClick={() => setCount((count) => count + 1)}>
          count is {count}
        </button>
        <p>
          Edit <code>src/App.jsx</code> and save to test HMR
        </p>
      </div>
      <p className="read-the-docs">
        Click on the Vite and React logos to learn more
      </p>
    </>
  )
}

export default App
```

Newer versions may import from `./assets/vite.svg` (relative), add `heroImg`, or use
a completely different JSX structure. When in doubt, **write the App.jsx step as a full
`content:` replacement rather than an `edit:` with a FIND block**.

## 5. Do NOT generate tests for scaffold config files

`postcss.config.mjs`, `vitest.config.js`, `vite.config.js`, and `vitest.setup.js` are
framework scaffolding — not application logic. Never auto-generate `.test.` files for them.

Two failures result when you do:
1. Auto-generators default to `node:test`/`assert` (incompatible with Vitest) — the
   baseline run fails before component tests even execute.
2. Tests call `require('../postcss.config.mjs')` on an ESM-only file — throws `ERR_REQUIRE_ESM`.

## 6. Testing Tailwind-styled components with Vitest

Use `toHaveClass()`, never regex on `className`. Tailwind modifier classes (`md:flex`,
`hover:bg-cyan-300`, `-translate-x-full`) break regex word-boundary matching.

```js
// WRONG
expect(element.className).toMatch(/md:hidden/)

// CORRECT
expect(element).toHaveClass('md:hidden')
expect(element).not.toHaveClass('hidden')
```
