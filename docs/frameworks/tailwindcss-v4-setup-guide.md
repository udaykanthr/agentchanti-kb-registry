---
id: "doc-008"
title: "Tailwind CSS v4 Setup Guide"
category: "doc"
language: "all"
version: "1.4.0"
created_at: "2026-03-04"
updated_at: "2026-04-01"
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

**IMPORTANT**: Tailwind CSS v4 (released 2025) completely replaced the v3 setup.
`npx tailwindcss init`, `tailwind.config.js`, and `@tailwind` directives are **gone**.

Use this guide when setting up Tailwind CSS v4 with Vite, React, or any PostCSS-based
framework. Required packages: `tailwindcss`, `@tailwindcss/postcss`, `postcss`.
The PostCSS config file for Vite projects must be `postcss.config.mjs` (not `.js`).
The CSS entry point uses a single `@import "tailwindcss"` line — no `@tailwind` directives.

## Correct Installation (PostCSS + Vite)

Install and configure Tailwind CSS v4 as a PostCSS plugin. Works with Vite, React, Next.js, and Angular.

### Step 1: Install packages

```bash
npm install tailwindcss @tailwindcss/postcss postcss
```

> No `autoprefixer` needed — Lightning CSS handles vendor prefixing automatically.

### Step 2: Write PostCSS config — MUST be a [CODE] plan step

> **CRITICAL**: Write `postcss.config.mjs` as a **`[CODE]`** plan step with a `content:` block.
> **NEVER** use a `[CMD]` step with `touch`, `type nul >`, `echo >`, or any shell command
> to create this file — those produce an empty file with no plugin configuration, which
> silently breaks Tailwind processing (no styles are generated, no error is thrown).

Target file: `<project>/postcss.config.mjs` (use `.mjs`, not `.js`, for Vite projects)

```js
/* postcss.config.mjs */
export default {
  plugins: {
    '@tailwindcss/postcss': {},
  },
}
```

> For CommonJS projects only, use `postcss.config.cjs` with `module.exports = { ... }`.

### Step 3: Write CSS import — MUST be a [CODE] plan step

> **CRITICAL**: Write `src/index.css` as a **`[CODE]`** plan step. Do not use a shell
> command to create or truncate it.

In your main CSS file (e.g. `src/index.css`):

```css
@import "tailwindcss";
```

That single line replaces all three old `@tailwind base/components/utilities` directives.

**Do not run** `npx tailwindcss init` or add `tailwind.config.js` — these are removed in v4.
PostCSS runs automatically via `npm run dev` / `npm run build` — no CLI needed.

## Do NOT Use (v3 patterns that break v4)

```css
/* WRONG — causes build failure in v4 */
@tailwind base;
@tailwind components;
@tailwind utilities;
```

```bash
# WRONG — these commands no longer exist
npx tailwindcss init
npx tailwindcss init -p
```

```js
// WRONG — wrong plugin name
plugins: { tailwindcss: {} }

// CORRECT
plugins: { '@tailwindcss/postcss': {} }
```

## Key Differences from v3

| Feature | v3 (old) | v4 (current) |
|---------|----------|--------------|
| Install | `npm install tailwindcss postcss autoprefixer` | `npm install tailwindcss @tailwindcss/postcss postcss` |
| Config file | `tailwind.config.js` | Not used — configure in CSS |
| CSS import | `@tailwind base/components/utilities` | `@import "tailwindcss"` |
| PostCSS plugin | `tailwindcss` | `@tailwindcss/postcss` |
| Init command | `npx tailwindcss init -p` | Not needed |
