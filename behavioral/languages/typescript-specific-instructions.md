---
id: "beh-008"
title: "TypeScript-Specific Instructions"
category: "behavioral"
language: "typescript"
version: "1.0.0"
created_at: "2026-02-24"
tags:
  - typescript
  - behavioral
  - strict
  - type-safety
  - best-practices
---

# TypeScript-Specific Instructions

When writing or reviewing TypeScript code, follow these instructions exactly.

## Always Use

- **Strict mode**: `tsconfig.json` must have `"strict": true`. If it's missing, flag it as [WARNING] and suggest adding it. Strict mode enables: `strictNullChecks`, `noImplicitAny`, `strictFunctionTypes`, and more.
- **Explicit return types on functions**: `function greet(name: string): string { ... }` not `function greet(name: string) { ... }`. Return type inference can be wrong when a function grows, and explicit types serve as documentation.
- **`unknown` over `any` for external data**: API responses, parsed JSON, and user input should be typed as `unknown`, then narrowed with type guards before use. `any` bypasses all type checking.
- **`const` over `let` where possible**: Use `const` for all variables that are not reassigned. Reserve `let` for values that change.
- **Optional chaining (`?.`) over manual null checks**: `user?.profile?.name` not `user && user.profile && user.profile.name`.

## Always Prefer

- **`type` over `interface` for unions and intersections**: `type Result = Success | Error` must use `type`. For simple object shapes, either works — be consistent within a codebase.
- **`interface` for object shapes that may be extended**: If other code will `extends` or `implements` the shape, use `interface`. Otherwise, `type` is fine.
- **Discriminated unions over optional fields**: `type Shape = { kind: 'circle'; radius: number } | { kind: 'rect'; width: number }` is safer than `type Shape = { kind: string; radius?: number; width?: number }`.

## Never

- **Never use `any` without a comment explaining why**: If `any` is genuinely necessary, add a comment: `// any: required because third-party library has no types`. Every `any` without a comment is flagged as [WARNING].
- **Never use non-null assertion (`!`) without a guard**: `element!.focus()` will throw at runtime if element is null. Either check with `if (element)` first, or explain why null is impossible.
- **Never ignore TypeScript errors with `@ts-ignore`** without an explanation comment. Use `@ts-expect-error` instead (errors if the next line is valid — tells you when the suppression is no longer needed), and always add a comment explaining why.

## When Handling API Responses

Always validate external data with a type guard or schema library before using it as a typed value.

```typescript
// Bad: assuming the shape without validation
const user: User = await response.json();  // could be anything
console.log(user.name.toUpperCase());      // runtime crash if name is missing

// Good: validate with zod
import { z } from 'zod';

const UserSchema = z.object({
  id: z.number(),
  name: z.string(),
  email: z.string().email(),
});

const raw = await response.json();
const user = UserSchema.parse(raw);     // throws ZodError if invalid
// or:
const result = UserSchema.safeParse(raw);
if (!result.success) {
  logger.error('Invalid user response:', result.error);
  throw new Error('API returned unexpected data shape');
}
const user = result.data;  // fully typed User
```

## TypeScript-Specific Code Quality

1. **Enums vs `as const` objects**: Prefer `const Direction = { Up: 'Up', Down: 'Down' } as const` over `enum Direction { Up, Down }`. Const objects are simpler, tree-shakeable, and interoperate better with JSON.
2. **Type narrowing**: Use `typeof`, `instanceof`, `in`, or discriminant checks to narrow union types before accessing their members.
3. **Avoid type assertions (`as`)**: Type assertions bypass type checking. Prefer type guards. Use `as` only when you have information TypeScript doesn't (e.g., after a runtime check).
4. **`satisfies` operator (TS 4.9+)**: Use `satisfies` to validate an expression against a type without widening the inferred type.
5. **Template literal types**: Use for string validation and APIs where string shape matters: `type EventName = `on${Capitalize<string>}``; `.
