---
id: "doc-006"
title: "React Hooks Reference"
category: "doc"
language: "javascript"
version: "1.0.0"
created_at: "2026-02-24"
tags:
  - react
  - hooks
  - useState
  - useEffect
  - useRef
  - useMemo
  - useCallback
---

# React Hooks Reference

## useState

```jsx
const [value, setValue] = useState(initialValue);
const [count, setCount] = useState(0);

// Functional update (safe when next state depends on current)
setCount(prev => prev + 1);

// Lazy initialization (initializer only runs once)
const [data, setData] = useState(() => expensiveComputation());

// Common mistake: mutating state directly
const [items, setItems] = useState([]);
items.push(newItem);       // WRONG — mutates state directly
setItems([...items, newItem]);  // RIGHT — new array
```

## useEffect

```jsx
// Run on every render (no dependency array)
useEffect(() => { document.title = title; });

// Run once on mount (empty array)
useEffect(() => {
  const subscription = subscribe();
  return () => subscription.unsubscribe();  // cleanup on unmount
}, []);

// Run when specific values change
useEffect(() => {
  fetchUser(userId).then(setUser);
}, [userId]);  // re-runs when userId changes

// Common mistake: missing dependencies
useEffect(() => {
  // eslint-disable-next-line — BAD: lying to the linter
  fetchUser(userId);  // userId is used but not in deps
}, []);

// Async inside useEffect: define async function inside
useEffect(() => {
  let cancelled = false;
  async function load() {
    const data = await fetchUser(userId);
    if (!cancelled) setUser(data);
  }
  load();
  return () => { cancelled = true; };
}, [userId]);
```

## useContext

```jsx
const ThemeContext = createContext('light');

function App() {
  return (
    <ThemeContext.Provider value="dark">
      <Button />
    </ThemeContext.Provider>
  );
}

function Button() {
  const theme = useContext(ThemeContext);  // 'dark'
  return <button className={`btn-${theme}`}>Click</button>;
}
```

## useReducer

```jsx
function reducer(state, action) {
  switch (action.type) {
    case 'increment': return { count: state.count + 1 };
    case 'decrement': return { count: state.count - 1 };
    case 'reset':     return { count: action.payload ?? 0 };
    default: throw new Error(`Unknown action: ${action.type}`);
  }
}

function Counter() {
  const [state, dispatch] = useReducer(reducer, { count: 0 });
  return (
    <>
      <span>{state.count}</span>
      <button onClick={() => dispatch({ type: 'increment' })}>+</button>
      <button onClick={() => dispatch({ type: 'reset', payload: 10 })}>Reset to 10</button>
    </>
  );
}
```

## useCallback

Memoizes a function — returns the same function reference unless dependencies change. Use when passing callbacks to memoized children or as effect dependencies.

```jsx
function Parent({ userId }) {
  // Without useCallback: new function on every render → child always re-renders
  const handleSelect = useCallback((itemId) => {
    navigate(`/users/${userId}/items/${itemId}`);
  }, [userId, navigate]);  // stable: only changes when userId changes

  return <MemoizedChild onSelect={handleSelect} />;
}

// Common mistake: empty dependency array when callback uses values
const handleClick = useCallback(() => {
  sendData(value);  // value is stale if not in deps!
}, []);             // BUG: stale closure

// Right:
const handleClick = useCallback(() => {
  sendData(value);
}, [value]);
```

## useMemo

Memoizes a computed value. Only recomputes when dependencies change.

```jsx
function UserTable({ users, searchTerm }) {
  // Without useMemo: filter runs on every render
  const filtered = useMemo(
    () => users.filter(u => u.name.toLowerCase().includes(searchTerm.toLowerCase())),
    [users, searchTerm]
  );

  return <table>{filtered.map(u => <UserRow key={u.id} user={u} />)}</table>;
}

// Do NOT use useMemo for:
// - Simple operations (array access, arithmetic, short conditions)
// - Non-deterministic values (random numbers, dates)
// Rule: profile first, memoize second
```

## useRef

Creates a mutable ref that persists across renders without causing re-renders.

```jsx
// DOM reference
function TextInput() {
  const inputRef = useRef(null);

  useEffect(() => {
    inputRef.current?.focus();  // focus on mount
  }, []);

  return <input ref={inputRef} />;
}

// Storing mutable values without re-renders (timer IDs, previous values)
function Timer() {
  const timerRef = useRef(null);

  const start = () => {
    timerRef.current = setInterval(tick, 1000);
  };

  const stop = () => {
    clearInterval(timerRef.current);
    timerRef.current = null;
  };

  useEffect(() => () => clearInterval(timerRef.current), []);  // cleanup
}

// Previous value pattern
function usePrevious(value) {
  const ref = useRef();
  useEffect(() => { ref.current = value; });
  return ref.current;  // returns previous render's value
}
```

## useLayoutEffect

Same as useEffect but fires synchronously after DOM mutations, before the browser paints. Use only when you need to measure the DOM.

```jsx
function Tooltip({ children, target }) {
  const tooltipRef = useRef(null);
  const [position, setPosition] = useState({ top: 0, left: 0 });

  useLayoutEffect(() => {
    // Measure tooltip BEFORE browser paints to prevent flicker
    const rect = tooltipRef.current.getBoundingClientRect();
    const targetRect = target.current.getBoundingClientRect();
    setPosition({
      top: targetRect.bottom,
      left: targetRect.left - rect.width / 2,
    });
  }, [target]);

  return <div ref={tooltipRef} style={position}>{children}</div>;
}
```

## useId

Generates a stable unique ID across server and client renders. Required for accessible HTML (label + input association).

```jsx
function EmailField() {
  const id = useId();  // e.g., ':r0:'

  return (
    <>
      <label htmlFor={id}>Email</label>
      <input id={id} type="email" />
    </>
  );
}

// Do NOT use as array keys — useId is for HTML IDs only
```

## Rules of Hooks (Must Follow)

1. **Only call hooks at the top level** — never inside if/for/while or nested functions
2. **Only call hooks from React functions** — function components or custom hooks (starting with `use`)
3. **Never conditionally call hooks** — React relies on hook call order being consistent

```jsx
// WRONG:
function Component({ show }) {
  if (show) {
    const [value, setValue] = useState(0);  // conditional hook!
  }
}

// RIGHT:
function Component({ show }) {
  const [value, setValue] = useState(0);  // always called
  if (!show) return null;
  return <div>{value}</div>;
}
```
