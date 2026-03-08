---
id: "doc-010"
title: "Vitest React Setup Guide"
category: "doc"
language: "javascript"
version: "1.0.0"
created_at: "2026-03-07"
tags:
  - vitest
  - react
  - vite
  - testing
  - setup
  - guide
---

## Overview

Setting up Vitest in a React + Vite project requires specific packages and configuration
to ensure components render correctly and DOM assertions work.

*** Do not create TS or TSX files if JS or JSX already exists, Update those files insetead ***

## 1. Required Packages *** Important ***

Install the following development dependencies:

```bash
npm install -D vitest @testing-library/react @testing-library/jest-dom jsdom @vitest/ui
```

- `vitest`: The testing framework.
- `@testing-library/react`: For rendering React components in tests.
- `@testing-library/jest-dom`: For custom DOM matchers (e.g., `toBeInTheDocument`).
- `jsdom`: Browser environment simulation for Node.js.
- `@vitest/ui`: Optional UI for viewing test results.

## 2. Vite Configuration (`vite.config.ts` or `vite.config.js`)

Update your Vite config to include the test environment setup. Note the
`/// <reference types="vitest" />` comment is required for TypeScript to recognize
the test configuration.

```typescript
/// <reference types="vitest" />
import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

export default defineConfig({
  plugins: [react()],
  test: {
    environment: 'jsdom',
    globals: true,
    setupFiles: './src/setupTests.ts', // or .js
  },
})
```
- `environment: 'jsdom'`: Simulates a browser environment.
- `globals: true`: Allows using `describe`, `it`, `expect` without importing them.
- `setupFiles`: Runs before each test file, used to inject global matchers.

## 3. Test Setup File (`src/setupTests.ts` or `src/setupTests.js`)

Create a setup file to import `@testing-library/jest-dom`. This gives you access
to custom matchers like `.toBeInTheDocument()`. Depending on your project type, this may be a `.js` or `.ts` file.

```typescript
import '@testing-library/jest-dom'
```

## 4. TypeScript Configuration (`tsconfig.json` or `tsconfig.app.json`)

If using TypeScript, ensure `vitest/globals` and `@testing-library/jest-dom` are
included in your `compilerOptions.types`.

```json
{
  "compilerOptions": {
    "types": ["vitest/globals", "@testing-library/jest-dom"]
  }
}
```
This resolves errors like `ReferenceError: describe is not defined` or
`Property 'toBeInTheDocument' does not exist on type 'Matchers<any>'`.

## 5. Add Scripts to `package.json`

Add test scripts to your `package.json` using `npm pkg set`:

```bash
npm pkg set scripts.test="vitest"
npm pkg set scripts.test:ui="vitest --ui"
npm pkg set scripts.test:coverage="vitest run --coverage"
```

## Troubleshooting

- **ReferenceError: describe is not defined**: Ensure `globals: true` is in
  `vite.config.ts`, and `vitest/globals` is in `tsconfig.json` types.
- **ReferenceError: jest is not defined**:  Ensure `import { describe, test, expect } from 'vitest'` is in .test files and remove and never use jest related imports and functions.
- **Error: Failed to resolve import**: Ensure `import <component-name> from '<component-path>'` is in .test files and component-path is correct.  
- **document/window is not defined**: Ensure `environment: 'jsdom'` is set in
  your test config and `jsdom` is installed.
