---
id: "beh-009"
title: "React Router Setup Instructions"
category: "behavioral"
language: "javascript"
version: "1.0.0"
created_at: "2026-04-02"
tags:
  - react
  - react-router
  - BrowserRouter
  - HashRouter
  - MemoryRouter
  - main.jsx
  - App.jsx
  - entry-point
  - singleton
  - nested
  - router
  - behavioral
  - instructions
  - javascript
  - typescript
---

## CRITICAL: React Router Setup Rules

When generating or modifying React apps that use React Router, follow these rules to
prevent the "You cannot render a `<Router>` inside another `<Router>`" runtime error
and the `TypeError: Cannot destructure property 'basename' of useContext(...) as it is null`
crash caused by missing Router context.

## Rule 1: Only ONE BrowserRouter in the entire app — always in main.jsx

The `BrowserRouter` (or `HashRouter`) MUST be placed only at the app entry point:

```jsx
// main.jsx — CORRECT placement
import { StrictMode } from 'react'
import { createRoot } from 'react-dom/client'
import { BrowserRouter } from 'react-router-dom'
import './index.css'
import App from './App.jsx'

createRoot(document.getElementById('root')).render(
  <StrictMode>
    <BrowserRouter>
      <App />
    </BrowserRouter>
  </StrictMode>,
)
```

NEVER place `BrowserRouter` inside `App.jsx` or any child component:

```jsx
// App.jsx — WRONG: causes nested Router runtime error
export default function App() {
  return (
    <BrowserRouter>   {/* Remove this */}
      <div>...</div>
    </BrowserRouter>
  )
}
```

## Rule 2: When generating plan inline code for main.jsx — ALWAYS include BrowserRouter

This is the most commonly missed rule with concise LLMs.

If ANY component in the plan uses `<Link>`, `<NavLink>`, `<Route>`, `<Routes>`,
`useNavigate()`, `useLocation()`, or `useParams()` from `react-router-dom`, the
`main.jsx` inline code MUST wrap `<App />` in `<BrowserRouter>`.

**CHECKLIST before writing main.jsx inline code:**
- [ ] Is `react-router-dom` in the npm install step? → add BrowserRouter to main.jsx
- [ ] Does any component step use `<Link>` or `<NavLink>`? → add BrowserRouter to main.jsx
- [ ] BrowserRouter goes in main.jsx ONLY — never in App.jsx or children

## Rule 3: Use MemoryRouter in tests — never BrowserRouter

Tests that render components using Router hooks or `<Link>` MUST wrap in `<MemoryRouter>`:

```jsx
import { MemoryRouter } from 'react-router-dom'

render(
  <MemoryRouter>
    <Header />
  </MemoryRouter>
)
```

## Rule 4: NEVER nest two Routers

If the component under test is `App` and `App` already has `<BrowserRouter>` in `main.jsx`
(or inside itself), do NOT add another `<MemoryRouter>` in the test — it causes
"You cannot render a `<Router>` inside another `<Router>`".

**READ `App.jsx` before writing its test.** If `App` contains a Router, use one of:

**Option A** — Render App directly (only if no routing-dependent assertions needed):
```jsx
render(<App />)
```

**Option B (PREFERRED)** — Mock BrowserRouter to become MemoryRouter:
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

**Option C** — Test individual page components instead of App:
```jsx
render(
  <MemoryRouter initialEntries={['/about']}>
    <AboutPage />
  </MemoryRouter>
)
```

## Rule 5: Fix for the 'basename' null crash

```
TypeError: Cannot destructure property 'basename' of 'import_react.useContext(...)' as it is null
```

This error means a component using `<Link>`, `<NavLink>`, or a Router hook was rendered
without any Router ancestor. Fix: add `<BrowserRouter>` to `main.jsx` (see Rule 1 and 2).

## Rule 6: NEVER leave a JSX comment before the root JSX element in a return

`{/* comment */}` MUST be inside an open JSX element — placing it before the
opening root tag causes a syntax error:

```jsx
// WRONG — syntax error
return (
  {/* this causes a parse error */}
  <div>...</div>
)

// CORRECT
return (
  <div>
    {/* this is valid */}
    ...
  </div>
)
```
