---
id: "doc-008"
title: "Tailwind CSS v4 Setup Guide"
category: "doc"
language: "all"
version: "1.0.0"
created_at: "2026-03-04"
tags:
  - tailwindcss
  - tailwind
  - css
  - frontend
  - setup
  - install
  - init
  - postcss
  - cli
---

## Overview

**IMPORTANT**: As of Tailwind CSS v4 (released 2025), the old `npx tailwindcss init`
command and `tailwind.config.js` configuration file are **no longer supported**.
Tailwind CSS v4 uses a completely new installation and configuration approach.

## DEPRECATED — Do NOT Use

### Deprecated CSS Directives (CRITICAL)

The following CSS directives are **REMOVED** in Tailwind CSS v4 and MUST NOT
be written to any CSS file. They will cause build failures:

```css
/* WRONG — NEVER write these: */
@tailwind base;
@tailwind components;
@tailwind utilities;
```

The ONLY correct CSS import for Tailwind CSS v4 is:

```css
/* CORRECT — use this single line instead: */
@import "tailwindcss";
```

Do NOT combine `@tailwind` directives with `@import "tailwindcss"`.
Do NOT add `@tailwind base;`, `@tailwind components;`, or `@tailwind utilities;`
anywhere in any CSS file. The single `@import "tailwindcss";` line replaces
ALL THREE of those old directives.

### Deprecated Commands

The following commands are **obsolete** and will fail with Tailwind CSS v4:

```bash
# WRONG — these no longer work:
npx tailwindcss init
npx tailwindcss init -p
npx tailwindcss init -p --yes
npx tailwindcss init --full
```

The `tailwind.config.js` / `tailwind.config.ts` configuration file is also
**no longer used** in Tailwind CSS v4. Configuration is now done via CSS.

`postcss.config.mjs` and `postcss.config.js` are also **no longer used** in Tailwind CSS v4.
**Use the filename `.postcssrc.json` instead. `postcss.config.mjs` and `postcss.config.js`**


## Correct Installation (Tailwind CSS v4)

IMPORTANT: In ALL commands below, replace `<project-name>` with the EXACT
project name derived from the user's task description. Use the SAME name
consistently in every step — do NOT invent a different name.

### Step 1: Create a new Vite project with react template

```bash
npm create vite@latest <project-name> -- --template react --no-interactive
```

### Step 2: Install packages, Install Tailwind CSS

```bash
npm install tailwindcss @tailwindcss/vite --save-dev
```

### Step 3: Install additional packages

```bash
npm install react-router-dom  --save
```

### Step 4: Install dependencies
```bash
npm install
```

### Step 5: Configure Vite: Add the plugin to your vite.config.ts or vite.config.js

```typescript
import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
import tailwindcss from '@tailwindcss/vite'

export default defineConfig({
  plugins: [
    react(),
    tailwindcss(),
  ],
})
```

### Step 6: Import Tailwind in CSS

Replace the ENTIRE contents of src/index.css with ONLY this single line:

```css
@import "tailwindcss";
```

WARNING: Do NOT write `@tailwind base;`, `@tailwind components;`, or
`@tailwind utilities;` — those directives are REMOVED in v4 and will break
the build. The single `@import "tailwindcss";` line replaces all of them.

## Key Differences from v3

| Feature | v3 (old) | v4 (current) |
|---------|----------|--------------|
| Install | `npm install tailwindcss postcss autoprefixer` | `npm create vite@latest <project-name>` then `npm install tailwindcss @tailwindcss/vite` |
| Init | `npx tailwindcss init -p` | Not needed |
| Config | `tailwind.config.js` | vite.config.ts |
| CSS import | `@tailwind base/components/utilities` | `@import "tailwindcss"` |
| Build | `npx tailwindcss -i input -o output` | `npm run dev` |
