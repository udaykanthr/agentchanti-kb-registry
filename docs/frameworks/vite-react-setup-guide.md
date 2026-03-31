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

## 4. Actual scaffold output — IMPORTANT for inline edits

`npm create vite@latest --template react` (current version) generates these files.
**Always use this exact content in <<<FIND>>> blocks when editing scaffold files.**

### src/main.jsx (actual scaffold output)

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

### src/App.jsx (actual scaffold output)

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

**Key differences from older templates:**
- Uses `import { useState }` without `import React` (React 17+ JSX transform)
- `viteLogo` imported from `/vite.svg` (absolute path)
- vite.dev link (not vitejs.dev)
- Returns a fragment `<>...</>` not `<div className="App">`
