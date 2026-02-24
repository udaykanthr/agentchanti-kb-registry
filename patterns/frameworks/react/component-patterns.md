---
id: "react-pattern-001"
title: "React Component Patterns"
category: "pattern"
language: "javascript"
version: "1.0.0"
created_at: "2026-02-24"
tags:
  - react
  - components
  - hooks
  - composition
  - performance
---

# React Component Patterns

## Problem

React components that are monolithic, tightly coupled, hard to test, and mix presentation with logic — leading to components that are difficult to reuse and that re-render unnecessarily.

## Solution: Compound Components

Compound components share state implicitly through context, enabling flexible composition without prop drilling.

```jsx
import { createContext, useContext, useState } from 'react';

// Context for shared state
const TabsContext = createContext(null);

// Parent provides state
function Tabs({ defaultTab, children }) {
  const [activeTab, setActiveTab] = useState(defaultTab);
  return (
    <TabsContext.Provider value={{ activeTab, setActiveTab }}>
      <div className="tabs">{children}</div>
    </TabsContext.Provider>
  );
}

// Children consume context, no props needed
function TabList({ children }) {
  return <div role="tablist">{children}</div>;
}

function Tab({ id, children }) {
  const { activeTab, setActiveTab } = useContext(TabsContext);
  return (
    <button
      role="tab"
      aria-selected={activeTab === id}
      onClick={() => setActiveTab(id)}
    >
      {children}
    </button>
  );
}

function TabPanel({ id, children }) {
  const { activeTab } = useContext(TabsContext);
  if (activeTab !== id) return null;
  return <div role="tabpanel">{children}</div>;
}

// Attach to parent for discoverability
Tabs.List = TabList;
Tabs.Tab = Tab;
Tabs.Panel = TabPanel;

// Usage: clean, flexible composition
<Tabs defaultTab="overview">
  <Tabs.List>
    <Tabs.Tab id="overview">Overview</Tabs.Tab>
    <Tabs.Tab id="details">Details</Tabs.Tab>
  </Tabs.List>
  <Tabs.Panel id="overview"><Overview /></Tabs.Panel>
  <Tabs.Panel id="details"><Details /></Tabs.Panel>
</Tabs>
```

## Solution: Custom Hooks

Extract stateful logic from components into custom hooks. Custom hooks start with `use` and can call other hooks.

```jsx
// Extract data fetching into a reusable hook
function useUser(userId) {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    let cancelled = false;  // prevent state update if component unmounts
    setLoading(true);
    fetchUser(userId)
      .then(data => { if (!cancelled) setUser(data); })
      .catch(err => { if (!cancelled) setError(err); })
      .finally(() => { if (!cancelled) setLoading(false); });
    return () => { cancelled = true; };
  }, [userId]);

  return { user, loading, error };
}

// Components stay clean
function UserProfile({ userId }) {
  const { user, loading, error } = useUser(userId);
  if (loading) return <Spinner />;
  if (error) return <ErrorMessage error={error} />;
  return <div>{user.name}</div>;
}
```

## Solution: Composition over Inheritance

React doesn't use class inheritance. Use composition — pass components as props or children — to build complex UI from simple parts.

```jsx
// Bad: trying to share logic via class inheritance
class SpecialButton extends Button { }  // anti-pattern in React

// Good: wrap/compose
function PrimaryButton({ children, ...props }) {
  return <Button className="btn-primary" {...props}>{children}</Button>;
}

function LoadingButton({ loading, children, ...props }) {
  return (
    <Button disabled={loading} {...props}>
      {loading ? <Spinner size="sm" /> : children}
    </Button>
  );
}
```

## Solution: memo and useMemo — When to Use/Avoid

Memoization prevents unnecessary re-renders and expensive recalculations, but it has overhead. Use it only when you have a measured performance problem.

```jsx
// React.memo: prevents re-render when props haven't changed
// Use when: component renders frequently, parent re-renders often, props rarely change
const UserRow = React.memo(function UserRow({ user, onSelect }) {
  return (
    <tr onClick={() => onSelect(user.id)}>
      <td>{user.name}</td>
      <td>{user.email}</td>
    </tr>
  );
});
// Note: onSelect must be stable (useCallback) or memo won't help

// useMemo: memoize expensive computation
function UserTable({ users, searchTerm }) {
  // Only recompute when users or searchTerm changes
  const filteredUsers = useMemo(() =>
    users.filter(u => u.name.toLowerCase().includes(searchTerm.toLowerCase())),
    [users, searchTerm]
  );
  return <table>{filteredUsers.map(u => <UserRow key={u.id} user={u} />)}</table>;
}

// useCallback: stable function reference (needed when passing callbacks to memoized children)
function Parent({ userId }) {
  const handleSelect = useCallback((id) => {
    navigate(`/users/${id}`);
  }, [navigate]);  // stable reference — navigate from react-router is stable

  return <UserTable onSelect={handleSelect} />;
}
```

## When to Use

- Compound components: when multiple related components share state and you want clean composition.
- Custom hooks: when the same stateful logic appears in 2+ components, or when a component's `useEffect` logic is complex.
- Composition: always, instead of inheritance.
- memo/useMemo: only after profiling shows a real performance issue. Premature memoization adds complexity.

## When NOT to Use

- Do not use compound components for simple parent-child relationships — regular props are clearer.
- Do not extract every small piece of logic into a custom hook — only extract when there's actual reuse or complexity.
- Do not wrap every component in `React.memo` — it adds overhead and may hide bugs.

## Related Patterns

- `react-pattern-002` — State Management Patterns
- `beh-001` — Code Review Instructions
