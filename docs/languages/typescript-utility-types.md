---
id: "doc-005"
title: "TypeScript Utility Types Reference"
category: "doc"
language: "typescript"
version: "1.0.0"
created_at: "2026-02-24"
tags:
  - typescript
  - utility-types
  - generics
  - type-system
---

# TypeScript Utility Types Reference

Complete reference for all built-in TypeScript utility types with real examples.

## Base Type for Examples

```typescript
interface User {
  id: number;
  name: string;
  email: string;
  role: 'admin' | 'user' | 'moderator';
  createdAt: Date;
  address?: string;  // optional
}
```

## Partial\<T\>

Makes all properties optional.

```typescript
type UserUpdate = Partial<User>;
// { id?: number; name?: string; email?: string; ... }

function updateUser(id: number, changes: Partial<User>): User {
  const user = findUser(id);
  return { ...user, ...changes };
}

updateUser(1, { name: 'New Name' });  // only name needs to be provided
```

## Required\<T\>

Makes all properties required (reverse of Partial). Removes `?`.

```typescript
type FullUser = Required<User>;
// { id: number; name: string; email: string; address: string; ... }
// address is now required (no longer optional)
```

## Readonly\<T\>

Makes all properties immutable. TypeScript will error on assignment.

```typescript
type ImmutableUser = Readonly<User>;

const user: ImmutableUser = { id: 1, name: 'Alice', ... };
user.name = 'Bob';  // TS2540: Cannot assign to 'name' because it is a read-only property
```

## Record\<K, V\>

Creates a dictionary type with keys of type K and values of type V.

```typescript
type RolePermissions = Record<User['role'], string[]>;
const permissions: RolePermissions = {
  admin: ['read', 'write', 'delete'],
  user: ['read'],
  moderator: ['read', 'write'],
};

// Generic: map string keys to any value type
type StringToNumber = Record<string, number>;
const scores: StringToNumber = { Alice: 95, Bob: 87 };
```

## Pick\<T, K\>

Creates a type with only the specified properties from T.

```typescript
type UserPreview = Pick<User, 'id' | 'name'>;
// { id: number; name: string; }

type UserCard = Pick<User, 'name' | 'email' | 'role'>;
// Use for UI components that only need a subset

function renderUserCard(user: UserCard) { ... }
```

## Omit\<T, K\>

Creates a type with all properties EXCEPT the specified ones.

```typescript
// API response: don't expose createdAt timestamp
type PublicUser = Omit<User, 'createdAt'>;
// { id: number; name: string; email: string; role: ...; address?: string; }

// Remove sensitive fields from DTO
type CreateUserDto = Omit<User, 'id' | 'createdAt'>;
// Forces caller to provide everything except auto-generated fields
```

## Exclude\<T, U\>

Removes types from a union T that are assignable to U.

```typescript
type AllRoles = 'admin' | 'user' | 'moderator' | 'guest';
type UserFacingRoles = Exclude<AllRoles, 'admin'>;
// 'user' | 'moderator' | 'guest'

// Remove null from union
type NonNullableString = Exclude<string | null | undefined, null | undefined>;
// string
```

## Extract\<T, U\>

Keeps only the types in union T that are assignable to U (opposite of Exclude).

```typescript
type AdminRoles = Extract<AllRoles, 'admin' | 'moderator'>;
// 'admin' | 'moderator'

// Keep only function types from a union
type FunctionMembers = Extract<string | (() => void) | number, Function>;
// () => void
```

## NonNullable\<T\>

Removes `null` and `undefined` from a type.

```typescript
type MaybeUser = User | null | undefined;
type DefinitelyUser = NonNullable<MaybeUser>;
// User

// Useful in generic constraints
function process<T>(value: NonNullable<T>): void { ... }
```

## ReturnType\<T\>

Extracts the return type of a function type.

```typescript
function fetchUser(id: number): Promise<User> { ... }
type FetchResult = ReturnType<typeof fetchUser>;
// Promise<User>

// Useful for inferring types from factory functions
const createStore = () => ({
  users: [] as User[],
  addUser: (user: User) => { ... },
});

type Store = ReturnType<typeof createStore>;
// { users: User[]; addUser: (user: User) => void; }
```

## InstanceType\<T\>

Extracts the instance type from a constructor type.

```typescript
class UserService {
  constructor(private db: Database) {}
  getUser(id: number): User { ... }
}

type ServiceInstance = InstanceType<typeof UserService>;
// UserService — same as the class type itself, but useful in generics

// Generic factory pattern
function create<T extends new (...args: any[]) => any>(
  ctor: T
): InstanceType<T> {
  return new ctor();
}
```

## Parameters\<T\>

Extracts the parameter types of a function as a tuple.

```typescript
function createUser(name: string, email: string, role: User['role']): User { ... }

type CreateUserParams = Parameters<typeof createUser>;
// [name: string, email: string, role: 'admin' | 'user' | 'moderator']

// Useful for wrapping functions
function withLogging<T extends (...args: any[]) => any>(
  fn: T,
  fnName: string
): (...args: Parameters<T>) => ReturnType<T> {
  return (...args) => {
    console.log(`Calling ${fnName} with`, args);
    return fn(...args);
  };
}

const loggedCreate = withLogging(createUser, 'createUser');
loggedCreate('Alice', 'alice@example.com', 'user');  // fully typed
```

## Awaited\<T\>

Unwraps the resolved type from a Promise (useful for async return types).

```typescript
async function fetchUser(): Promise<User> { ... }

type FetchedUser = Awaited<ReturnType<typeof fetchUser>>;
// User (not Promise<User>)

// Deeply unwraps nested promises
type Deep = Awaited<Promise<Promise<string>>>;
// string
```

## Quick Reference

| Utility Type | Effect |
|---|---|
| `Partial<T>` | All properties optional |
| `Required<T>` | All properties required |
| `Readonly<T>` | All properties readonly |
| `Record<K, V>` | Dictionary with typed keys and values |
| `Pick<T, K>` | Keep only K from T |
| `Omit<T, K>` | Remove K from T |
| `Exclude<T, U>` | Remove from union T what matches U |
| `Extract<T, U>` | Keep in union T only what matches U |
| `NonNullable<T>` | Remove null and undefined |
| `ReturnType<T>` | Function return type |
| `InstanceType<T>` | Class instance type |
| `Parameters<T>` | Function parameter types as tuple |
| `Awaited<T>` | Unwrap Promise resolved type |
