---
id: "react-pattern-002"
title: "React State Management Patterns"
category: "pattern"
language: "javascript"
version: "1.0.0"
created_at: "2026-02-24"
tags:
  - react
  - state
  - useState
  - useReducer
  - context
  - derived-state
---

# React State Management Patterns

## Problem

Overuse of global state managers for local data, context that causes excessive re-renders, derived state stored redundantly in state (leading to sync bugs), and anti-patterns like copying props to state.

## Solution: useState vs useReducer Decision Guide

```jsx
// Use useState for: simple, independent values
const [isOpen, setIsOpen] = useState(false);
const [count, setCount] = useState(0);

// Use useReducer for: complex state with multiple sub-values, or
// when next state depends on previous state in non-trivial ways
const initialState = { status: 'idle', data: null, error: null };

function reducer(state, action) {
  switch (action.type) {
    case 'fetch_start':
      return { status: 'loading', data: null, error: null };
    case 'fetch_success':
      return { status: 'success', data: action.payload, error: null };
    case 'fetch_error':
      return { status: 'error', data: null, error: action.error };
    default:
      throw new Error(`Unknown action: ${action.type}`);
  }
}

function DataComponent({ id }) {
  const [state, dispatch] = useReducer(reducer, initialState);

  useEffect(() => {
    dispatch({ type: 'fetch_start' });
    fetchData(id)
      .then(data => dispatch({ type: 'fetch_success', payload: data }))
      .catch(error => dispatch({ type: 'fetch_error', error }));
  }, [id]);

  if (state.status === 'loading') return <Spinner />;
  if (state.status === 'error') return <Error message={state.error.message} />;
  return <Display data={state.data} />;
}
```

## Solution: Context Pitfalls

Context re-renders all consumers when the value changes. Split context by update frequency to minimize re-renders.

```jsx
// Bad: single context causes all consumers to re-render on any change
const AppContext = createContext();
function AppProvider({ children }) {
  const [user, setUser] = useState(null);
  const [theme, setTheme] = useState('light');
  const [cart, setCart] = useState([]);
  return (
    <AppContext.Provider value={{ user, setUser, theme, setTheme, cart, setCart }}>
      {children}
    </AppContext.Provider>
  );
}

// Good: separate contexts by change frequency
const UserContext = createContext();    // changes rarely (login/logout)
const ThemeContext = createContext();   // changes occasionally
const CartContext = createContext();    // changes frequently

// Split the provider into focused providers
function Providers({ children }) {
  return (
    <UserProvider>
      <ThemeProvider>
        <CartProvider>
          {children}
        </CartProvider>
      </ThemeProvider>
    </UserProvider>
  );
}
```

## Solution: Lifting State Up

When two sibling components need to share state, lift the state to their common ancestor.

```jsx
// Bad: duplicate state in siblings that get out of sync
function SearchBox() {
  const [query, setQuery] = useState('');
  // ...
}

function ResultsList() {
  const [query, setQuery] = useState('');  // separate state, gets out of sync!
  // ...
}

// Good: lift to common parent
function SearchPage() {
  const [query, setQuery] = useState('');
  return (
    <>
      <SearchBox query={query} onQueryChange={setQuery} />
      <ResultsList query={query} />
    </>
  );
}
```

## Solution: Derived State Anti-Patterns

Do not store in state values that can be computed from other state or props. This creates sync bugs.

```jsx
// Anti-pattern: derived state stored in useState
function ItemList({ items }) {
  const [filteredItems, setFilteredItems] = useState(items);  // copies props!
  const [search, setSearch] = useState('');

  // Bug: if `items` prop changes, filteredItems is stale
  useEffect(() => {
    setFilteredItems(items.filter(i => i.name.includes(search)));
  }, [items, search]);

  return <ul>{filteredItems.map(...)}</ul>;
}

// Correct: compute during render (no state needed)
function ItemList({ items }) {
  const [search, setSearch] = useState('');
  const filteredItems = items.filter(i => i.name.includes(search));  // derived, not stored

  return (
    <>
      <input value={search} onChange={e => setSearch(e.target.value)} />
      <ul>{filteredItems.map(...)}</ul>
    </>
  );
}

// If computation is expensive, memoize instead of storing in state
const filteredItems = useMemo(
  () => items.filter(i => i.name.includes(search)),
  [items, search]
);
```

## Solution: External Store Basics (Zustand, Redux Toolkit)

For genuinely global state (user auth, feature flags, shopping cart accessible from anywhere), use an external store.

```javascript
// Zustand (simpler, recommended for most cases)
import { create } from 'zustand';

const useCartStore = create((set, get) => ({
  items: [],
  addItem: (item) => set(state => ({
    items: [...state.items, item]
  })),
  removeItem: (id) => set(state => ({
    items: state.items.filter(i => i.id !== id)
  })),
  total: () => get().items.reduce((sum, item) => sum + item.price, 0),
}));

// Usage anywhere in the tree (no Provider needed)
function CartSummary() {
  const { items, total } = useCartStore();
  return <div>{items.length} items, ${total()}</div>;
}
```

## When to Use

- `useState`: simple, local, independent values.
- `useReducer`: complex state machines, multiple related values, testable update logic.
- Context: truly global values (auth, theme) that don't change frequently.
- External store: when multiple disconnected parts of the app need the same mutable state.

## When NOT to Use

- Do not store derived values in state — compute them.
- Do not put server data in global state when a query cache (React Query, SWR) would work better.
- Do not use context for high-frequency updates (every keypress, animation frames) — use external store with subscriptions instead.

## Related Patterns

- `react-pattern-001` — Component Patterns
