---
id: "doc-014"
title: "Anime.js Installation and Usage Guide"
category: "doc"
language: "javascript"
version: "1.0.0"
created_at: "2026-03-28"
tags:
  - animejs
  - ui
  - animation
---

# Anime.js Reference Guide

## Installation

Install Anime.js via npm:
```bash
npm install animejs
```

Anime.js has a very flexible modules-first API and excellent tree shaking support, making it one of the most lightweight JavaScript animation libraries.

## Module Imports

Anime.js modules can be imported straight from the main `animejs` module, or more granularly from specific subpaths (either by using a bundler like Vite/esbuild or natively without a build step using `importmap`).

### Importing from the main module

Every Anime.js module can be directly imported from the main module:

```javascript
import { animate, splitText, stagger, random } from 'animejs';

const split = splitText('p');

animate(split.words, {
  opacity: () => random(0, 1, 2),
  delay: stagger(50),
});
```

### Importing from subpaths

When not using a bundler, or when tree shaking cannot be activated in a project, the entire library logic might unintentionally be loaded. To solve this, Anime.js allows importing specific functionality from a subpath.

```javascript
import { animate } from 'animejs/animation';
import { splitText } from 'animejs/text';
import { stagger, random } from 'animejs/utils';

const split = splitText('p');

animate(split.words, {
  opacity: () => random(0, 1, 2),
  delay: stagger(50),
});
```

This approach ensures that only the code required for the specified functionality is loaded.

**List of available subpaths:**
```javascript
import { animate } from 'animejs/animation';
import { createTimer } from 'animejs/timer';
import { createTimeline } from 'animejs/timeline';
import { createAnimatable } from 'animejs/animatable';
import { createDraggable } from 'animejs/draggable';
import { createLayout } from 'animejs/layout';
import { createScope } from 'animejs/scope';
import { engine } from 'animejs/engine';
import * as events from 'animejs/events';
import * as easings from 'animejs/easings';
import * as utils from 'animejs/utils';
import * as svg from 'animejs/svg';
import * as text from 'animejs/text';
import * as waapi from 'animejs/waapi';
```

### Importing ES modules without a bundler

With `importmap`, the main module and any of the subpath modules can be imported just like with a bundler, but without a build step in the browser:

```html
<script type="importmap">
{
  "imports": {
    "animejs": "/node_modules/animejs/dist/modules/index.js",
    "animejs/animation": "/node_modules/animejs/dist/modules/animation/index.js",
    "animejs/timer": "/node_modules/animejs/dist/modules/timer/index.js",
    "animejs/timeline": "/node_modules/animejs/dist/modules/timeline/index.js",
    "animejs/animatable": "/node_modules/animejs/dist/modules/animatable/index.js",
    "animejs/draggable": "/node_modules/animejs/dist/modules/draggable/index.js",
    "animejs/layout": "/node_modules/animejs/dist/modules/layout/index.js",
    "animejs/scope": "/node_modules/animejs/dist/modules/scope/index.js",
    "animejs/engine": "/node_modules/animejs/dist/modules/engine/index.js",
    "animejs/events": "/node_modules/animejs/dist/modules/events/index.js",
    "animejs/easings": "/node_modules/animejs/dist/modules/easings/index.js",
    "animejs/utils": "/node_modules/animejs/dist/modules/utils/index.js",
    "animejs/svg": "/node_modules/animejs/dist/modules/svg/index.js",
    "animejs/text": "/node_modules/animejs/dist/modules/text/index.js",
    "animejs/waapi": "/node_modules/animejs/dist/modules/waapi/index.js"
  }
}
</script>

<script type="module">
  import { animate } from 'animejs/animation';
  import { splitText } from 'animejs/text';
  import { stagger, random } from 'animejs/utils';

  const split = splitText('p');

  animate(split.words, {
    opacity: () => random(0, 1, 2),
    delay: stagger(50),
  });
</script>
```

## Error Troubleshooting

### `SyntaxError: Cannot use import statement outside a module`
**Cause:** Attempting to use Anime.js ES modules in a standard `<script>` tag without `type="module"`, or in a Node.js environment without ES module support configured.
**Fix:**
- In the browser, ensure your script tag uses `type="module"`: `<script type="module" src="app.js"></script>`.
- Or, if you use Node.js to bundle, ensure your `package.json` contains `"type": "module"`.

### `Uncaught TypeError: Failed to resolve module specifier "animejs".`
**Cause:** The browser does not know how to resolve bare imports like `'animejs'` dynamically without an import map or a build step.
**Fix:**
Provide an `<script type="importmap">` mapping the bare specifier to a valid local or CDN URL, or run your code through a bundler like Vite.

### `animate is not exported from 'animejs'`
**Cause:** Trying to use `import { animate } from 'animejs';` on an older version of Anime.js (v3 or below).
**Fix:**
Ensure you have installed the latest version of Anime.js that supports the modules-first API (`npm i animejs@next` or similar, depending on the release branch).
