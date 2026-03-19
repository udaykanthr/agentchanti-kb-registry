---
id: "doc-008"
title: "Tailwind CSS v4 Setup Guide"
category: "doc"
language: "all"
version: "1.1.0"
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

> [!IMPORTANT]
> Tailwind CSS v4 is powered by Lightning CSS, which handles vendor prefixing automatically. You **no longer need** the `autoprefixer` package.

Install `tailwindcss` and `@tailwindcss/postcss` via npm.

```bash
npm install tailwindcss @tailwindcss/postcss postcss
```

### Step 2: Add Tailwind to your PostCSS configuration

Add `@tailwindcss/postcss` to your `postcss.config.js` file (ensure your project is set to `"type": "module"` in `package.json`).

```javascript
/* postcss.config.js */
export default {
  plugins: {
    "@tailwindcss/postcss": {},
  }
}
```

> [!IMPORTANT]
> Tailwind CSS v4 requires `@tailwindcss/postcss`. The legacy `tailwindcss` plugin name will NOT work and may lead to using v3 logic incorrectly.

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

## Troubleshooting

### Incorrect Plugin Names

If you see errors like `Unknown word` or if Tailwind classes aren't being applied despite having a PostCSS config, check your plugin names.

**WRONG (v3 style):**
```javascript
plugins: {
  tailwindcss: {}, // FAIL
  tailwind: {},    // FAIL
}
```

**CORRECT (v4 style):**
```javascript
plugins: {
  "@tailwindcss/postcss": {}, // SUCCESS
}
```

### CommonJS vs ESM

If your project uses CommonJS (`require`), you may need to name the file `postcss.config.cjs` and use `module.exports`:

```javascript
/* postcss.config.cjs */
module.exports = {
  plugins: {
    "@tailwindcss/postcss": {},
  }
}
```

### `.mjs` vs `.js` Config File Extension

When a Vite scaffold creates `postcss.config.mjs` (ESM module), commands and tools must
reference the **exact filename**. Never pass `--config postcss.config.js` when the file
on disk is `postcss.config.mjs`.

**WRONG — file extension mismatch:**
```bash
npx postcss src/index.css -o dist/styles.css --config postcss.config.js
```

**CORRECT — match the actual file on disk:**
```bash
npx postcss-cli src/index.css -o dist/styles.css --config postcss.config.mjs
```

Also note that `.mjs` files must use `export default`, not `require()`:

```javascript
/* postcss.config.mjs — CORRECT */
export default {
  plugins: {
    "@tailwindcss/postcss": {},
  }
}
```

```javascript
/* postcss.config.mjs — WRONG: require() is CommonJS, not valid in .mjs */
export default {
  plugins: [require("@tailwindcss/postcss")],
}
```

### `npx postcss` Fails — Use `postcss-cli` or Skip CLI Entirely

`postcss` is a **library**, not a CLI binary. Running `npx postcss ...` will fail with
`"npm error could not determine executable to run"` because there is no `postcss` binary.

**WRONG:**
```bash
npx postcss src/index.css -o dist/styles.css --config postcss.config.mjs
```

**CORRECT (if you need CLI):** install `postcss-cli` first:
```bash
npm install -D postcss-cli
npx postcss-cli src/index.css -o dist/styles.css --config postcss.config.mjs
```

**PREFERRED for Vite/CRA/Next.js projects:** Do NOT run postcss CLI at all.
PostCSS runs automatically during `npm run build` or `npm run dev` via the
framework's build pipeline. Just ensure `postcss.config.mjs` (or `.js`) exists
with `@tailwindcss/postcss` and add `@import "tailwindcss";` to your CSS file.
