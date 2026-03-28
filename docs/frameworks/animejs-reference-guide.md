---
id: "doc-012"
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

You can install Anime.js via npm or include it directly in your HTML.

### Via npm
```bash
npm install animejs
```
Then import it in your JavaScript/TypeScript files:
```javascript
import anime from 'animejs/lib/anime.es.js';
// or
const anime = require('animejs');
```

### Via CDN (HTML)
```html
<script src="https://cdnjs.cloudflare.com/ajax/libs/animejs/3.2.1/anime.min.js"></script>
```

## Usage Guidelines

Anime.js is a lightweight JavaScript animation library with a simple, yet powerful API. It works with CSS properties, SVG, DOM attributes, and JavaScript Objects.

### Basic Animation
```javascript
anime({
  targets: '.css-selector',
  translateX: 250,
  duration: 800,
  easing: 'easeInOutQuad'
});
```

### Timeline
To sequence multiple animations, use `anime.timeline()`:
```javascript
const timeline = anime.timeline({
  easing: 'easeOutExpo',
  duration: 750
});

timeline
.add({
  targets: '.box1',
  translateX: 250,
})
.add({
  targets: '.box2',
  translateX: 250,
  offset: '-=500' // Starts 500ms before previous animation ends
});
```

### React/Vue Integration
When using Anime.js in UI frameworks like React or Vue, it's best to use `useRef` or template refs instead of CSS selectors to ensure you target the correct DOM element.

**React Example:**
```javascript
import { useEffect, useRef } from 'react';
import anime from 'animejs';

function AnimatedBox() {
  const boxRef = useRef(null);

  useEffect(() => {
    anime({
      targets: boxRef.current,
      translateX: 100,
      duration: 1000
    });
  }, []);

  return <div ref={boxRef} className="box"></div>;
}
```

## Error Troubleshooting

### `targets is undefined or cannot be found`
**Cause:** Anime.js cannot find the specified target elements in the DOM. This often happens if the animation code runs before the DOM is fully loaded or if framework components (React/Vue) haven't mounted yet.
**Fix:**
- Ensure your script runs after the DOM is ready, or place the `<script>` tag at the end of the `<body>`.
- In React/Vue, execute animations inside `useEffect` (React) or `onMounted` (Vue) using references or refs.

### `anime is not a function`
**Cause:** The Anime.js library was not imported correctly or the ES6 module path is wrong.
**Fix:**
Make sure you are importing from the correct path. For ES modules, use `import anime from 'animejs/lib/anime.es.js';`.

### `TypeError: Cannot read properties of undefined (reading 'style')`
**Cause:** One of the targets passed to Anime.js is not a valid DOM node, or it was removed from the DOM before or during the animation.
**Fix:**
Check that you are passing valid DOM nodes or valid query selectors. If using an array of targets, ensure there are no `null` or `undefined` elements.
