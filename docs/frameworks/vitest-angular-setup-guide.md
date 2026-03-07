---
id: "doc-011"
title: "Vitest Angular Setup Guide"
category: "doc"
language: "typescript"
version: "1.0.0"
created_at: "2026-03-07"
tags:
  - vitest
  - angular
  - vite
  - testing
  - setup
  - guide
---

## Overview

Setting up Vitest in an Angular project (v16+) is typically done using the
`@analogjs/vite-plugin-angular` plugin to compile Angular components for Vite.

> [!IMPORTANT]
> **Development Constraint:** Never generate Angular component files from scratch. Always execute `ng generate` first. Once the files are created, read the file content and apply surgical updates to the class logic and template. When updating `.spec.ts` files, strictly follow the vitest-angular-setup-guide.md pattern, replacing default Jasmine/Karma code with Vitest and Testing Library syntax.

## 1. Required Packages

Install the following development dependencies:

```bash
npm install -D vitest @analogjs/vite-plugin-angular @angular/build @angular/platform-browser-dynamic jsdom @testing-library/angular @testing-library/jest-dom @testing-library/dom
```

- `vitest`: The testing framework.
- `@analogjs/vite-plugin-angular`: Vite plugin for Angular compatibility.
- `@angular/build`: Required peer dependency for the analogjs plugin to access Angular's internal build modules.
- `@angular/platform-browser-dynamic`: Required for initializing the Angular test environment.
- `jsdom`: Browser environment simulation for Node.js.
- `@testing-library/angular`: For rendering Angular components in tests (optional but recommended).

## 2. Vite Configuration (`vite.config.ts` and `vitest.config.ts`)

Create a `vite.config.ts` for build/dev and a separate `vitest.config.ts` for testing.

```typescript
// vite.config.ts
import { defineConfig } from 'vite';
import angular from '@analogjs/vite-plugin-angular';

export default defineConfig({
  plugins: [angular()],
});
```

```typescript
// vitest.config.ts
import { defineConfig } from 'vitest/config';

export default defineConfig({
  test: {
    environment: 'jsdom',
    include: ['src/**/*.spec.ts', 'src/**/*.test.ts'],
    exclude: ['node_modules', 'dist'],
    setupFiles: ['./src/test-setup.ts'],
    globals: true,
  },
});
```

## 3. Test Setup File (`src/test-setup.ts`)

Create a test setup file to initialize the Angular testing environment and import DOM matchers.

```typescript
import '@testing-library/jest-dom';
import { TestBed } from '@angular/core/testing';
import {
  BrowserDynamicTestingModule,
  platformBrowserDynamicTesting,
} from '@angular/platform-browser-dynamic/testing';

TestBed.initTestEnvironment(
  BrowserDynamicTestingModule,
  platformBrowserDynamicTesting()
);
```

## 4. TypeScript Configuration (`tsconfig.spec.json`)

Ensure `vitest/globals` and `@testing-library/jest-dom` are included in your `compilerOptions.types`.
Also include your test setup file in `files` to ensure it is compiled.

```json
{
  "extends": "./tsconfig.json",
  "compilerOptions": {
    "outDir": "./out-tsc/spec",
    "types": ["vitest/globals", "@testing-library/jest-dom", "node"]
  },
  "files": ["src/test-setup.ts"],
  "include": ["src/**/*.spec.ts", "src/**/*.d.ts"]
}
```

## 5. Add Scripts to `package.json`

Add test scripts to your `package.json` using `npm pkg set`:

```bash
npm pkg set scripts.test="vitest run"
npm pkg set scripts.test:ui="vitest --ui"
npm pkg set scripts.test:coverage="vitest run --coverage"
```

## Troubleshooting

- **ReferenceError: describe is not defined**: Ensure `globals: true` is in your `vite.config.ts` and `vitest/globals` is in your `tsconfig.spec.json` types.
- **ReferenceError: jest is not defined**:  Ensure `import { describe, test, expect } from 'vitest'` is in .test files and remove and never use jest related imports and functions.
- **Error: Failed to resolve import**: Ensure `import <component-name> from '<component-path>'` is in .test files and component-path is correct.
- **Can't bind to 'x' since it isn't a known property of 'y'**: The component is not properly configured in your test module. Ensure proper imports when using `@testing-library/angular` `render()` or `TestBed.configureTestingModule()`.
