---
id: "doc-012"
title: "React TailwindCSS Responsive Header"
category: "doc"
language: "javascript"
version: "1.0.0"
created_at: "2026-03-24"
tags:
  - react
  - tailwindcss
  - ui
  - component
---

# React TailwindCSS Responsive Header Component

This document provides a robust, reusable, and accessible pattern for implementing a responsive header using React and TailwindCSS. 

## Overview

The responsive header component includes the following features:
- **Sticky & Glassmorphism Design:** A sticky top navigation bar with a subtle blur effect (`backdrop-blur-md`).
- **React Router Navigation:** Utilizes `<Link>` from `react-router-dom` for client-side routing.
- **Mobile Navigation:** A hamburger menu button that reveals a sliding side panel on smaller screens.
- **Accessibility:** Includes semantic HTML (`<header>`, `<nav>`), screen reader text (`sr-only`), and focus states (`focus:ring-2`).

## Implementation

```javascript
import React, { useState } from 'react';
import { Link } from 'react-router-dom';
import PropTypes from 'prop-types';

/**
 * Header component
 *
 * A responsive header that uses Tailwind CSS for styling.
 * It displays a brand name, navigation links, and a mobile menu toggle
 * with an overlay panel. The component is fully responsive and
 * follows accessibility best practices.
 *
 * @param {Object} props
 * @param {string} props.title - Brand name or logo text.
 * @param {Array<{ name: string, to: string }>} props.navLinks - Navigation links.
 */
const Header = ({ title, navLinks }) => {
  const [isMobileMenuOpen, setIsMobileMenuOpen] = useState(false);

  const links =
    Array.isArray(navLinks) && navLinks.length
      ? navLinks
      : [
          { name: 'Home', to: '/' },
          { name: 'Features', to: '/features' },
          { name: 'Pricing', to: '/pricing' },
          { name: 'Contact', to: '/contact' },
        ];

  return (
    <>
      <header className="fixed w-full top-0 z-40 bg-white/80 backdrop-blur-md shadow-sm border-b border-gray-100">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center h-16">
            {/* Logo */}
            <div className="flex-shrink-0 flex items-center">
              <Link to="/" className="text-2xl font-bold bg-gradient-to-r from-blue-600 to-indigo-600 bg-clip-text text-transparent">
                {title || 'BrandLogo'}
              </Link>
            </div>

            {/* Desktop Navigation */}
            <nav className="hidden md:flex space-x-8">
              {links.map((link) => (
                <Link
                  key={link.name}
                  to={link.to}
                  className="text-gray-600 hover:text-indigo-600 text-sm font-medium transition-colors duration-200"
                >
                  {link.name}
                </Link>
              ))}
            </nav>

            {/* Desktop Call to Action */}
            <div className="hidden md:flex items-center space-x-4">
              <Link to="/login" className="text-gray-600 hover:text-indigo-600 text-sm font-medium transition-colors duration-200">
                Log in
              </Link>
              <Link to="/signup" className="bg-indigo-600 hover:bg-indigo-700 text-white px-5 py-2 rounded-full text-sm font-medium transition-all duration-200 shadow-md hover:shadow-lg transform hover:-translate-y-0.5">
                Sign up
              </Link>
            </div>

            {/* Mobile menu button */}
            <div className="flex items-center md:hidden">
              <button
                onClick={() => setIsMobileMenuOpen(true)}
                className="text-gray-600 hover:text-indigo-600 focus:outline-none focus:ring-2 focus:ring-inset focus:ring-indigo-500 rounded-md p-2 transition-colors"
                aria-label="Open main menu"
              >
                <svg className="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 6h16M4 12h16M4 18h16" />
                </svg>
              </button>
            </div>
          </div>
        </div>
      </header>

      {/* Mobile Menu Side Panel Overlay */}
      {isMobileMenuOpen && (
        <div className="fixed inset-0 z-50 md:hidden">
          {/* Backdrop Overlay */}
          <div 
            className="fixed inset-0 bg-black/50 backdrop-blur-sm transition-opacity"
            onClick={() => setIsMobileMenuOpen(false)}
            aria-hidden="true"
          ></div>

          {/* Sliding Side Panel */}
          <div className="fixed inset-y-0 right-0 w-64 bg-white shadow-2xl transform transition-transform duration-300 ease-in-out flex flex-col">
            <div className="flex items-center justify-between p-4 border-b border-gray-100">
              <span className="text-xl font-bold text-gray-900">Menu</span>
              <button
                onClick={() => setIsMobileMenuOpen(false)}
                className="text-gray-500 hover:text-gray-900 focus:outline-none focus:ring-2 ring-indigo-500 p-2 rounded-md"
                aria-label="Close menu"
              >
                <svg className="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                </svg>
              </button>
            </div>

            {/* Panel Links */}
            <div className="flex-1 overflow-y-auto px-4 py-6">
              <nav className="flex flex-col space-y-4">
                {links.map((link) => (
                  <Link
                    key={link.name}
                    to={link.to}
                    onClick={() => setIsMobileMenuOpen(false)}
                    className="block text-gray-700 hover:bg-indigo-50 hover:text-indigo-600 px-3 py-2 rounded-lg text-base font-medium transition-colors"
                  >
                    {link.name}
                  </Link>
                ))}
              </nav>

              <div className="mt-8 pt-8 border-t border-gray-100 flex flex-col space-y-4">
                <Link to="/login" className="block w-full text-center text-gray-700 hover:bg-indigo-50 hover:text-indigo-600 px-4 py-2 rounded-lg font-medium transition-colors">
                  Log in
                </Link>
                <Link to="/signup" className="block w-full text-center bg-indigo-600 hover:bg-indigo-700 text-white px-4 py-2 rounded-lg font-medium shadow-md transition-colors">
                  Sign up
                </Link>
              </div>
            </div>
          </div>
        </div>
      )}
    </>
  );
};

Header.propTypes = {
  title: PropTypes.string,
  navLinks: PropTypes.arrayOf(
    PropTypes.shape({
      name: PropTypes.string.isRequired,
      to: PropTypes.string.isRequired,
    })
  ),
};

export default Header;
```

## Key Considerations

> [!IMPORTANT]
> **React Router Context Required**: Because this component uses `<Link>` tags from `react-router-dom`, you **must** ensure the entire application tree is wrapped in a `<BrowserRouter>` (e.g., in your `main.jsx` or `index.js`). Missing this wrapper will trigger a `Cannot destructure property 'basename' of 'useContext(...)' as it is null` runtime error.

- **Stacking Context**: The mobile menu overlay is intentionally placed completely outside the `<header>` container as a sibling inside a React Fragment (`<>`). This structure prevents the `<header>`'s CSS `backdrop-blur` filter from stripping the overlay child's global `fixed` positioning dimensions.
- **Padding Adjustment**: Make sure the parent container rendering `<Header />` has adequate top padding (e.g., `pt-16`) to account for the fixed header so background content isn't chopped off at the top. 
- **Icons**: The component utilizes lightweight inline SVG paths (from Heroicons) to maintain a zero-dependency footprint apart from standard React and Tailwind classes.

## Troubleshooting

### Error: `Cannot destructure property 'basename' of 'useContext(...)' as it is null`

**Cause:** You are using the `Header` component (which contains `<Link>` components from `react-router-dom`) outside of a Router context.

**Solution:** Ensure that the root component or the component containing the `Header` is wrapped in a `<BrowserRouter>`.

**Example Fix (in `main.jsx` or `App.jsx`):**
```javascript
import React from 'react'
import ReactDOM from 'react-dom/client'
import { BrowserRouter } from 'react-router-dom'
import App from './App.jsx'
import './index.css'

ReactDOM.createRoot(document.getElementById('root')).render(
  <React.StrictMode>
    <BrowserRouter>
      <App />
    </BrowserRouter>
  </React.StrictMode>,
)
```
