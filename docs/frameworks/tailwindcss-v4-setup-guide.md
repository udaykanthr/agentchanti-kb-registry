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


## Correct Installation (PostCSS)

Installing Tailwind CSS as a PostCSS plugin is the most seamless way to integrate it with frameworks like Next.js and Angular.

### Step 1: Install Tailwind CSS

Install `tailwindcss`, `@tailwindcss/postcss`, and `postcss` via npm.

```bash
npm install tailwindcss @tailwindcss/postcss postcss
```

### Step 2: Add Tailwind to your PostCSS configuration

Add `@tailwindcss/postcss` to your `postcss.config.mjs` file, or wherever PostCSS is configured in your project.

```javascript
export default {
  plugins: {
    "@tailwindcss/postcss": {},
  }
}
```

### Step 3: Import Tailwind CSS

Add an `@import` to your CSS file that imports Tailwind CSS.

```css
@import "tailwindcss";
```

### Step 4: Start using Tailwind in your HTML

Link your compiled CSS file and start using Tailwind's utility classes.

```html
<!doctype html>
<html>
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <link href="/dist/styles.css" rel="stylesheet">
</head>
<body>
  <h1 class="text-3xl font-bold underline">
    Hello world!
  </h1>
</body>
</html>
```

## Key Differences from v3

| Feature | v3 (old) | v4 (current) |
|---------|----------|--------------|
| Install | `npm install tailwindcss postcss autoprefixer` | `npm install tailwindcss @tailwindcss/postcss postcss` |
| Init | `npx tailwindcss init -p` | Not needed |
| Config | `tailwind.config.js` | Now configured directly in CSS or PostCSS config |
| CSS import | `@tailwind base/components/utilities` | `@import "tailwindcss"` |
| Build Directives | Uses `tailwind.config.js` for content paths | Automatically detects files or uses `@source` in CSS |
