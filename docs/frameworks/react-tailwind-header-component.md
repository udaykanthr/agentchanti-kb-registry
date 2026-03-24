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
- **Desktop Navigation:** Horizontal links with hover states and micro-animations for calls-to-action (CTA).
- **Mobile Navigation:** A hamburger menu button that reveals a sliding side panel on smaller screens.
- **Accessibility:** Includes semantic HTML (`<header>`, `<nav>`), screen reader text (`sr-only`), and focus states (`focus:ring-2`).

## Implementation

```javascript
import React, { useState } from 'react';

const Header = () => {
  const [isMobileMenuOpen, setIsMobileMenuOpen] = useState(false);

  return (
    <header className="fixed w-full top-0 z-50 bg-white/80 backdrop-blur-md shadow-sm border-b border-gray-100">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex justify-between items-center h-16">
          {/* Logo */}
          <div className="flex-shrink-0 flex items-center">
            <a href="#" className="text-2xl font-bold bg-gradient-to-r from-blue-600 to-indigo-600 bg-clip-text text-transparent">
              BrandLogo
            </a>
          </div>

          {/* Desktop Navigation */}
          <nav className="hidden md:flex space-x-8">
            {['Home', 'Features', 'Pricing', 'Contact'].map((item) => (
              <a
                key={item}
                href={`#${item.toLowerCase()}`}
                className="text-gray-600 hover:text-indigo-600 text-sm font-medium transition-colors duration-200"
              >
                {item}
              </a>
            ))}
          </nav>

          {/* Desktop Call to Action */}
          <div className="hidden md:flex items-center space-x-4">
            <button className="text-gray-600 hover:text-indigo-600 text-sm font-medium transition-colors duration-200">
              Log in
            </button>
            <button className="bg-indigo-600 hover:bg-indigo-700 text-white px-5 py-2 rounded-full text-sm font-medium transition-all duration-200 shadow-md hover:shadow-lg transform hover:-translate-y-0.5">
              Sign up
            </button>
          </div>

          {/* Mobile menu button */}
          <div className="flex items-center md:hidden">
            <button
              onClick={() => setIsMobileMenuOpen(true)}
              className="text-gray-600 hover:text-indigo-600 focus:outline-none focus:ring-2 focus:ring-inset focus:ring-indigo-500 rounded-md p-2 transition-colors"
            >
              <span className="sr-only">Open main menu</span>
              <svg className="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 6h16M4 12h16M4 18h16" />
              </svg>
            </button>
          </div>
        </div>
      </div>

      {/* Mobile Menu Side Panel Overlay */}
      {isMobileMenuOpen && (
        <div className="fixed inset-0 z-50 md:hidden">
          {/* Backdrop Overlay */}
          <div 
            className="fixed inset-0 bg-black/50 backdrop-blur-sm transition-opacity"
            onClick={() => setIsMobileMenuOpen(false)}
          ></div>

          {/* Sliding Side Panel */}
          <div className="fixed inset-y-0 right-0 w-64 bg-white shadow-2xl transform transition-transform duration-300 ease-in-out flex flex-col">
            <div className="flex items-center justify-between p-4 border-b border-gray-100">
              <span className="text-xl font-bold text-gray-900">Menu</span>
              <button
                onClick={() => setIsMobileMenuOpen(false)}
                className="text-gray-500 hover:text-gray-900 focus:outline-none focus:ring-2 ring-indigo-500 p-2 rounded-md"
              >
                <span className="sr-only">Close menu</span>
                <svg className="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                </svg>
              </button>
            </div>

            {/* Panel Links */}
            <div className="flex-1 overflow-y-auto px-4 py-6">
              <nav className="flex flex-col space-y-4">
                {['Home', 'Features', 'Pricing', 'Contact'].map((item) => (
                  <a
                    key={item}
                    href={`#${item.toLowerCase()}`}
                    onClick={() => setIsMobileMenuOpen(false)}
                    className="text-gray-700 hover:bg-indigo-50 hover:text-indigo-600 px-3 py-2 rounded-lg text-base font-medium transition-colors"
                  >
                    {item}
                  </a>
                ))}
              </nav>

              <div className="mt-8 pt-8 border-t border-gray-100 flex flex-col space-y-4">
                <button className="w-full text-center text-gray-700 hover:bg-indigo-50 hover:text-indigo-600 px-4 py-2 rounded-lg font-medium transition-colors">
                  Log in
                </button>
                <button className="w-full text-center bg-indigo-600 hover:bg-indigo-700 text-white px-4 py-2 rounded-lg font-medium shadow-md transition-colors">
                  Sign up
                </button>
              </div>
            </div>
          </div>
        </div>
      )}
    </header>
  );
};

export default Header;
```

## Key Considerations
- Ensure that the parent container of `<Header />` has adequate `pt-16` padding (or responsive equivalent) to account for the fixed header so content isn't obscured.
- The component relies on the heroicons SVG patterns for the menu/close buttons, keeping the dependency lightweight without requiring an external package.
- The `.backdrop-blur-sm` helps separate the mobile panel from the background content cleanly.
