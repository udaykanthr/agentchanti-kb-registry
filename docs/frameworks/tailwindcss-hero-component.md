---
id: "doc-013"
title: "Responsive TailwindCSS Hero Component (Generic)"
category: "doc"
language: "all"
version: "1.0.0"
created_at: "2026-03-24"
tags:
  - tailwindcss
  - html
  - ui
  - component
  - hero
  - generic
---

# Generic Responsive TailwindCSS Hero Component

This document provides a highly polished, responsive hero component using purely HTML and Tailwind CSS. By keeping it framework-agnostic, you can easily copy and paste this structure into React, Angular, Vue, Svelte, or vanilla HTML projects.

## Overview

The responsive hero component includes the following features:
- **Clean Typography:** A bold headline with specialized accent coloring for specific words (e.g., "Hybrid teams.").
- **Soft Glow Effect:** Uses positioned radial gradients (`bg-gradient-radial` / blurred elements) to create a beautiful blue ambiance behind an illustration.
- **Integration Badges:** Simple pill-shaped badges with simple icons for services like Slack, Google Chat, and Zoom.
- **Responsive Layout:** Automatically stacks on smaller screens and forms a side-by-side layout on medium breakpoint (`md:flex-row`).
- **Framework Agnostic:** Pure HTML means you just need to convert `class` to `className` in React, or keep it as is for Angular/Vue.

## Implementation

```html
<!-- 
  Hero Component (Generic HTML + Tailwind CSS)

  A beautiful, responsive hero section designed to capture user attention.
  Features a large value proposition headline, a supportive paragraph,
  integration badges, and a right-side illustration with a soft glow effect.
-->
<section class="relative w-full min-h-screen bg-white overflow-hidden flex items-center justify-center pt-24 pb-12 sm:pt-32 sm:pb-16 lg:pb-24">
  <!-- Decorative Top Gradient/Blur -->
  <div class="absolute top-0 left-0 w-full h-full bg-gradient-to-b from-white via-white to-gray-50/50 -z-20"></div>

  <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 relative z-10 w-full">
    <div class="flex flex-col lg:flex-row items-center justify-between gap-12 lg:gap-8">
      
      <!-- Left Content Column -->
      <div class="flex-1 flex flex-col items-start text-left max-w-2xl">
        <h1 class="text-5xl sm:text-6xl lg:text-7xl font-extrabold tracking-tight text-[#223A70] leading-[1.1]">
          Run successful remote and <br class="hidden sm:block">
          <span class="text-[#00A3FF]">Hybrid teams.</span>
        </h1>
        
        <p class="mt-6 text-lg sm:text-xl text-gray-600 leading-relaxed max-w-xl">
          DailyBot takes chat and collaboration to the next level: daily standups, team check-ins, surveys, kudos, best companion bot for your virtual watercooler, 1:1 intros, motivation tracking and more.
        </p>

        <p class="mt-8 text-sm font-medium text-gray-500">
          The best companion bot for your chat app.
        </p>

        <!-- Integration Badges -->
        <div class="mt-4 flex flex-wrap items-center gap-4">
          <span class="inline-flex items-center gap-2 px-4 py-2 rounded-full border border-gray-200 bg-white shadow-sm text-sm font-semibold text-gray-700 hover:shadow-md transition-shadow cursor-pointer">
            <!-- Simulated Slack Icon -->
            <span class="w-5 h-5 bg-gradient-to-tr from-pink-500 via-red-500 to-yellow-500 rounded-sm"></span>
            Slack
          </span>
          
          <span class="inline-flex items-center gap-2 px-4 py-2 rounded-full border border-gray-200 bg-white shadow-sm text-sm font-semibold text-gray-700 hover:shadow-md transition-shadow cursor-pointer">
            <!-- Simulated Google Chat Icon -->
            <span class="w-5 h-5 bg-green-500 rounded-sm flex items-center justify-center text-white text-[10px] font-bold">G</span>
            Google Chat
          </span>
          
          <span class="inline-flex items-center gap-2 px-4 py-2 rounded-full border border-gray-200 bg-white shadow-sm text-sm font-semibold text-gray-700 hover:shadow-md transition-shadow cursor-pointer">
            <!-- Simulated Zoom Icon -->
            <span class="w-5 h-5 bg-blue-500 rounded-full flex items-center justify-center text-white text-[10px] font-bold">Z</span>
            Zoom
          </span>
        </div>

        <div class="mt-6 flex items-center gap-2 text-sm text-gray-600">
          <span>🔥</span>
          <span>🌟</span>
          <span class="font-medium">Other integrations: Discord, Telegram</span>
        </div>
      </div>

      <!-- Right Image/Illustration Column -->
      <div class="flex-1 w-full relative h-[400px] sm:h-[500px] lg:h-[600px] flex items-center justify-center mt-12 lg:mt-0">
        <!-- The beautiful cyan/blue soft glow effect behind the image -->
        <div class="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[300px] h-[300px] sm:w-[500px] sm:h-[500px] bg-[#00A3FF] opacity-30 blur-[100px] rounded-full mix-blend-multiply pointer-events-none -z-10"></div>
        
        <!-- Illustration Placeholder (can be replaced with actual SVG/Image) -->
        <div class="relative z-10 w-full h-full max-w-md mx-auto flex items-center justify-center p-8 bg-white/20 backdrop-blur-sm border border-white/40 rounded-3xl shadow-2xl xl:scale-110 transition-transform duration-500 hover:scale-[1.12]">
          <div class="text-gray-400 text-center font-medium">
            <p class="text-lg">Illustration / Dashboard Mockup</p>
            <p class="text-xs mt-2 uppercase tracking-widest">Image Placement</p>
          </div>
        </div>
      </div>

    </div>
  </div>
</section>
```

## Key Considerations

> [!TIP]
> **Performance**: The large blur effect `blur-[100px]` can be computationally expensive on some lower-end mobile devices. If performance stutters, consider using a pre-rendered webp image of a glow instead of dynamic CSS filters.

- **Layout Structure**: The hero section uses `flex-col` for mobile devices and shifts to `lg:flex-row` for larger screens, ensuring the text content is prioritized above the illustration vertically on smaller devices.
- **Color Palette**: The specific blues used are `#223A70` for the deep navy headline and `#00A3FF` for the vibrant cyan accent. In Tailwind v4, you can place these in your root CSS variables or keep them as arbitrary utilities `text-[#...]`.
- **Gloom / Glow Effect**: The glowing background utilizes a rounded div positioned behind the image with absolute positioning and a high blur. It uses `opacity-30` and `mix-blend-multiply` to blend smoothly with the white background.
- **Usage in Frameworks**: To use this in React, convert `class=` to `className=`. To use in Angular or Vue, no structural changes are needed aside from linking your generic component properties.
