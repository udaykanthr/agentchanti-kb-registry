---
id: "doc-013"
title: "Responsive TailwindCSS Hero Component (Generic)"
category: "doc"
language: "all"
version: "1.0.1"
created_at: "2026-03-24"
tags:
  - tailwindcss
  - html
  - ui
  - component
  - hero
  - generic
  - animation
---

# Generic Responsive TailwindCSS Hero Component

This document provides a highly polished, responsive hero component using purely HTML and Tailwind CSS. It features a modern layout with a beautiful, animated gradient circle on the right side and left-aligned text content. By keeping it framework-agnostic, you can easily copy and paste this structure into React, Angular, Vue, Svelte, or vanilla HTML projects.

## Overview

The responsive hero component includes the following features:
- **Clean Typography:** Bold, imposing headline emphasizing "Run successful remote and Hybrid teams." with left-aligned supporting text.
- **Modern Animated Gradient:** A custom animated blob/circle gradient effect using overlapping blurred radial shapes that breathe and shift on the right side of the layout.
- **Glassmorphism Elements:** Subtle semi-transparent borders and backdrops to ensure the text remains legible over the glowing elements.
- **Framework Agnostic:** Pure HTML with a self-contained `<style>` block for the custom animation keyframes, ensuring zero configuration is needed in your Tailwind setup.

## Implementation

```html
<!-- 
  Modern Hero Component (Generic HTML + Tailwind CSS)
  
  Note: This wrapper includes a <style> block for the custom blob animation 
  to keep the component completely self-contained and configuration-free.
-->
<style>
  @keyframes blob {
    0% { transform: translate(0px, 0px) scale(1); }
    33% { transform: translate(30px, -50px) scale(1.1); }
    66% { transform: translate(-20px, 20px) scale(0.9); }
    100% { transform: translate(0px, 0px) scale(1); }
  }
  .animate-blob {
    animation: blob 7s infinite;
  }
  .animation-delay-2000 {
    animation-delay: 2s;
  }
  .animation-delay-4000 {
    animation-delay: 4s;
  }
</style>

<section class="relative w-full min-h-screen bg-[#FAFCFF] overflow-hidden flex items-center justify-center pt-24 pb-12 sm:pt-32 sm:pb-16 lg:pb-24 font-sans">
  
  <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 relative z-10 w-full flex flex-col lg:flex-row items-center justify-between gap-16 lg:gap-8">
    
    <!-- Left Content Column -->
    <div class="flex-1 flex flex-col items-start text-left max-w-2xl relative z-20">
      
      <!-- Optional Pill Badge -->
      <div class="mb-6 inline-flex items-center gap-2 px-3 py-1 rounded-full border border-blue-100 bg-blue-50/50 text-blue-700 text-sm font-semibold shadow-sm backdrop-blur-sm">
        <span class="relative flex h-2 w-2">
          <span class="animate-ping absolute inline-flex h-full w-full rounded-full bg-blue-400 opacity-75"></span>
          <span class="relative inline-flex rounded-full h-2 w-2 bg-blue-500"></span>
        </span>
        New integrations available
      </div>

      <h1 class="text-5xl sm:text-6xl lg:text-7xl font-extrabold tracking-tight text-[#162950] leading-[1.15]">
        Run successful remote and <br class="hidden sm:block">
        <span class="text-transparent bg-clip-text bg-gradient-to-r from-[#00A3FF] to-[#0052FF]">
          Hybrid teams.
        </span>
      </h1>
      
      <p class="mt-8 text-lg sm:text-xl text-gray-600 leading-relaxed max-w-xl">
        DailyBot takes chat and collaboration to the next level: daily standups, team check-ins, surveys, kudos, best companion bot for your virtual watercooler, 1:1 intros, motivation tracking and more.
      </p>

      <p class="mt-6 text-sm font-semibold text-gray-400 uppercase tracking-wide">
        The best companion bot for your chat app.
      </p>

      <!-- Chat Apps Row -->
      <div class="mt-6 flex flex-wrap items-center gap-6">
        <div class="flex items-center gap-2 group cursor-pointer">
          <div class="w-10 h-10 rounded-xl bg-white shadow-sm border border-gray-100 flex items-center justify-center group-hover:shadow-md group-hover:-translate-y-1 transition-all">
            <!-- Simulated Slack icon -->
            <div class="w-5 h-5 bg-gradient-to-br from-red-400 to-yellow-500 rounded-sm rounded-tr-xl rounded-bl-xl"></div>
          </div>
          <span class="font-medium text-gray-700">Slack</span>
        </div>

        <div class="flex items-center gap-2 group cursor-pointer">
          <div class="w-10 h-10 rounded-xl bg-white shadow-sm border border-gray-100 flex items-center justify-center group-hover:shadow-md group-hover:-translate-y-1 transition-all">
            <!-- Simulated Google Chat icon -->
            <div class="w-5 h-5 bg-green-500 rounded-full flex items-center justify-center text-white text-xs font-bold">G</div>
          </div>
          <span class="font-medium text-gray-700">Google Chat</span>
        </div>

        <div class="flex items-center gap-2 group cursor-pointer">
          <div class="w-10 h-10 rounded-xl bg-white shadow-sm border border-gray-100 flex items-center justify-center group-hover:shadow-md group-hover:-translate-y-1 transition-all">
            <!-- Simulated Zoom icon -->
            <div class="w-5 h-5 bg-blue-500 rounded-xl flex items-center justify-center text-white text-xs font-bold">Z</div>
          </div>
          <span class="font-medium text-gray-700">Zoom</span>
        </div>
      </div>

      <div class="mt-8 pt-6 border-t border-gray-100/60 w-full max-w-sm">
        <p class="text-sm text-gray-500 flex items-center gap-2">
          <span>🔥</span> 
          <span>🌟</span>
          <span class="font-medium">Other integrations: Discord, Telegram</span>
        </p>
      </div>
    </div>

    <!-- Right Image/Illustration Column (Animated Gradient) -->
    <div class="flex-1 w-full relative h-[400px] sm:h-[500px] lg:h-[600px] flex items-center justify-center mt-8 lg:mt-0">
      
      <!-- Animated Mesh Gradient Container -->
      <div class="relative w-full max-w-lg lg:max-w-xl aspect-square flex items-center justify-center">
        <!-- Center Blue Blob (Main Glow) -->
        <div class="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-64 h-64 sm:w-80 sm:h-80 bg-[#00A3FF] rounded-full mix-blend-multiply filter blur-[80px] opacity-70 animate-blob"></div>
        
        <!-- Top Right Cyan Blob -->
        <div class="absolute top-0 right-10 w-48 h-48 sm:w-72 sm:h-72 bg-[#00E5FF] rounded-full mix-blend-multiply filter blur-[80px] opacity-60 animate-blob animation-delay-2000"></div>
        
        <!-- Bottom Left Purple/Indigo Blob -->
        <div class="absolute bottom-10 left-10 w-56 h-56 sm:w-80 sm:h-80 bg-[#6C63FF] rounded-full mix-blend-multiply filter blur-[80px] opacity-60 animate-blob animation-delay-4000"></div>
        
        <!-- Foreground Floating Glassmorphism Element / Dashboard Mockup -->
        <div class="relative z-10 w-full max-w-sm aspect-[4/3] bg-white/40 backdrop-blur-2xl border border-white/60 rounded-3xl shadow-[0_8px_32px_0_rgba(31,38,135,0.07)] p-6 flex flex-col justify-between transform transition-transform duration-700 hover:scale-105">
          <!-- Fake Header for Mockup -->
          <div class="flex items-center justify-between border-b border-gray-200/50 pb-4">
            <div class="flex gap-2">
              <div class="w-3 h-3 rounded-full bg-red-400"></div>
              <div class="w-3 h-3 rounded-full bg-yellow-400"></div>
              <div class="w-3 h-3 rounded-full bg-green-400"></div>
            </div>
            <div class="w-1/2 h-4 bg-gray-200/50 rounded-full"></div>
          </div>
          <!-- Fake Content Lines -->
          <div class="space-y-4">
            <div class="w-full h-8 bg-white/50 rounded-lg"></div>
            <div class="w-3/4 h-8 bg-white/50 rounded-lg"></div>
            <div class="w-5/6 h-8 bg-white/50 rounded-lg"></div>
          </div>
          <!-- Fake Graph placeholder -->
          <div class="w-full h-1/3 bg-gradient-to-r from-[#00A3FF]/20 to-[#6C63FF]/20 rounded-xl mt-4"></div>
        </div>
      </div>

    </div>
  </div>
</section>
```

## Key Considerations

> [!TIP]
> **Performance**: The combination of `animate-blob` and `blur-[80px]` creates a beautiful organic glow, but is heavy on mobile browsers. For lower-end devices, you might consider replacing this with a static `.webp` image of a gradient in production.

- **Self-Contained Animation**: A `<style>` block is strategically placed inside the snippet. This approach ensures that developers copying this HTML don't have to alter their `tailwind.config.js` to define the custom blob keyframes or animation delay classes.
- **Glassmorphism**: The central card on the right uses `backdrop-blur-2xl` and a `bg-white/40` to let the glowing gradient shine through elegantly. This creates incredible depth.
- **Color Selection**: Using energetic colors like `#00A3FF` (Sky Blue) and `#6C63FF` (Indigo) matches the vibrant feel of modern SaaS marketing pages.
