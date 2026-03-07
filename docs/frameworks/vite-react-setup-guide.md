---
id: "doc-009"
title: "Vite React Setup Guide"
category: "doc"
language: "javascript"
version: "1.0.0"
created_at: "2026-03-07"
tags:
  - vite
  - react
  - testing
  - setup
  - guide
---

## Overview

Setting up Vite in a React project requires specific packages and configuration
to ensure components render correctly and DOM assertions work.

*** Do not create TS or TSX files if JS or JSX already exists, Update those files insetead ***

## 1. Required Packages

Install the following React vite packages initialization:
*** This step is very important to create necessary files and folders example, src/App.jsx, src/index.jsx, src/main.jsx, src/App.css, src/index.css, vite.config.js, package.json ***

```bash
npm create vite@latest my-react-app -- --template react --no-interactive
```

## 2. Install react dependencies

```bash
npm install react-router-dom
```

## 3. install NPM packages

```bash
npm install 
```
### Execute these installations for first time.
