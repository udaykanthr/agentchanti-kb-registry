---
id: "ts-pattern-001"
title: "Strict TypeScript Typing Patterns"
category: "pattern"
language: "typescript"
version: "1.0.0"
created_at: "2026-02-24"
tags:
  - typescript
  - strict
  - utility-types
  - discriminated-unions
  - type-guards
  - satisfies
---

# Strict TypeScript Typing Patterns

## Problem

TypeScript used with loose settings where `any` permeates the codebase, type guards are absent, and the full power of the type system is abandoned in favor of type assertions — resulting in runtime errors that TypeScript should have caught.

## Solution: Enable Strict Mode

In `tsconfig.json`, enable strict mode. This enables a suite of safety checks.

```json
{
  "compilerOptions": {
    "strict": true,
    "noImplicitAny": true,
    "strictNullChecks": true,
    "strictFunctionTypes": true,
    "noUncheckedIndexedAccess": true
  }
}
```

With `noUncheckedIndexedAccess`, array indexing returns `T | undefined` instead of `T`, forcing you to handle the missing case.

## Solution: Utility Types

```typescript
interface User {
  id: number;
  name: string;
  email: string;
  role: 'admin' | 'user';
  createdAt: Date;
}

// Partial: all fields optional (useful for update payloads)
type UserUpdate = Partial<User>;

// Required: all fields required (reverse of Partial)
type FullUser = Required<User>;

// Readonly: all fields immutable
type ReadonlyUser = Readonly<User>;

// Pick: select a subset of fields
type UserPreview = Pick<User, 'id' | 'name'>;

// Omit: exclude specific fields (for API responses that shouldn't expose everything)
type PublicUser = Omit<User, 'email' | 'createdAt'>;

// Record: dictionary type
type RolePermissions = Record<User['role'], string[]>;
const permissions: RolePermissions = {
  admin: ['read', 'write', 'delete'],
  user: ['read'],
};

// Exclude / Extract: filter union types
type NonAdminRoles = Exclude<User['role'], 'admin'>;  // 'user'
type AdminOnly = Extract<User['role'], 'admin'>;       // 'admin'

// ReturnType: extract the return type of a function
type ApiResponse = ReturnType<typeof fetchUser>;
```

## Solution: Discriminated Unions

Discriminated unions enable exhaustive type narrowing — TypeScript can verify that all cases are handled.

```typescript
type Shape =
  | { kind: 'circle'; radius: number }
  | { kind: 'rectangle'; width: number; height: number }
  | { kind: 'triangle'; base: number; height: number };

function area(shape: Shape): number {
  switch (shape.kind) {
    case 'circle':
      return Math.PI * shape.radius ** 2;
    case 'rectangle':
      return shape.width * shape.height;
    case 'triangle':
      return 0.5 * shape.base * shape.height;
    default:
      // This is never reached if all cases are handled
      // TypeScript will error here if you add a new Shape variant without handling it
      const _exhaustiveCheck: never = shape;
      throw new Error(`Unhandled shape: ${_exhaustiveCheck}`);
  }
}
```

## Solution: Type Guards

Type guards narrow a union type to a specific member within a conditional block.

```typescript
// User-defined type guard
interface Dog { kind: 'dog'; bark: () => void; }
interface Cat { kind: 'cat'; meow: () => void; }
type Pet = Dog | Cat;

function isDog(pet: Pet): pet is Dog {
  return pet.kind === 'dog';
}

function interact(pet: Pet) {
  if (isDog(pet)) {
    pet.bark();  // TypeScript knows it's Dog here
  } else {
    pet.meow();  // TypeScript knows it's Cat here
  }
}

// instanceof guard
function handleError(error: unknown) {
  if (error instanceof Error) {
    console.error(error.message);  // message exists on Error
  } else {
    console.error('Unknown error', error);
  }
}
```

## Solution: satisfies Operator (TypeScript 4.9+)

`satisfies` validates that an expression matches a type without widening the inferred type. Use it when you want type checking but also want to preserve the literal type.

```typescript
type Color = 'red' | 'green' | 'blue';
type Palette = Record<string, Color | [number, number, number]>;

// Without satisfies: type is widened to Palette
const myPalette: Palette = {
  red: [255, 0, 0],
  green: 'green',
  blue: [0, 0, 255],
};
myPalette.red;  // type: Color | [number, number, number] — not narrowed

// With satisfies: validates against Palette but preserves literal types
const myPalette = {
  red: [255, 0, 0],
  green: 'green',
  blue: [0, 0, 255],
} satisfies Palette;
myPalette.red;    // type: [number, number, number] — narrowed!
myPalette.green;  // type: 'green' — literal type preserved!
```

## Solution: Template Literal Types

```typescript
type EventName = 'click' | 'focus' | 'blur';
type Handler = `on${Capitalize<EventName>}`;  // 'onClick' | 'onFocus' | 'onBlur'

// Route parameter extraction
type ExtractRouteParams<T extends string> =
  T extends `${string}:${infer Param}/${infer Rest}`
    ? Param | ExtractRouteParams<Rest>
    : T extends `${string}:${infer Param}`
    ? Param
    : never;

type UserRouteParams = ExtractRouteParams<'/users/:userId/posts/:postId'>;
// type: 'userId' | 'postId'
```

## When to Use

- Strict mode: always, for all new TypeScript projects.
- Discriminated unions: for any value that can be in multiple distinct states.
- Type guards: at API boundaries and when narrowing union types.
- `satisfies`: when you need type validation but want to preserve literal inference.

## When NOT to Use

- Do not use complex mapped types or conditional types for simple cases where a plain interface suffices.
- Do not force TypeScript to model highly dynamic runtime data — use `unknown` and validate at runtime instead.

## Related Patterns

- `js-pattern-001` — Modern JavaScript Patterns
- `beh-008` — TypeScript-Specific Instructions
