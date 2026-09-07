---
layout: page
title: Glances are all you need.
description: High-precision eye tracking on low-cost hardware, powered by our custom GlanceNet model
img: assets/img/glances_hero_cover.jpg
permalink: /projects/glances/
importance: 2
category: work
---

Mixed reality devices such as Apple Vision Pro have demonstrated a new way to interact: **Gaze-and-Pinch**—look at what you want, then pinch to act. We believe this will become the primary mode of human–computer interaction. Yet limitations in eye-tracking algorithms keep the hardware costly and bulky, leaving almost all lightweight AR glasses on the market without eye-tracking interaction.

**Glances (览司)** addresses this with **GlanceNet**, our in-house eye-tracking model. It achieves **0.5° gaze accuracy on compact, low-cost hardware**, putting its performance among the industry's best and bringing precise eye-tracking interaction to lightweight AR glasses.

## Demos

<div class="glances-demos">
  <figure>
    <figcaption>Hero Demo</figcaption>
    <video controls playsinline preload="metadata" aria-label="Glances Hero Demo">
      <source src="https://res.cloudinary.com/p6fghypy/video/upload/v1788597565/demo_hero_h264_muted_u0cj7g.mp4" type="video/mp4">
      Your browser does not support embedded video.
    </video>
    <a href="https://res.cloudinary.com/p6fghypy/video/upload/v1788597565/demo_hero_h264_muted_u0cj7g.mp4">Open Hero Demo video</a>
  </figure>
  <figure>
    <figcaption>Eye Visual Demo</figcaption>
    <video controls playsinline preload="metadata" aria-label="Glances Eye Visual Demo">
      <source src="https://res.cloudinary.com/p6fghypy/video/upload/v1788597560/demo_eye_visual_cropped_with_title_w7zgci.mp4" type="video/mp4">
      Your browser does not support embedded video.
    </video>
    <a href="https://res.cloudinary.com/p6fghypy/video/upload/v1788597560/demo_eye_visual_cropped_with_title_w7zgci.mp4">Open Eye Visual Demo video</a>
  </figure>
</div>

## What's Next

We're building toward the first AR glasses equipped with eye-tracking interaction, with a roadmap toward **wireless glasses with waveguide optics**. Our goal is to make gaze-based interaction part of everyday life in a form you can comfortably wear throughout the day.

Ultimately, Glances will become **a single interface for the devices around you**. The same Gaze-and-Pinch interaction will let you control PCs, tablets, smart home devices, and more—one consistent way to interact across screens and environments.

<style>
  .glances-demos {
    display: grid;
    grid-template-columns: repeat(2, minmax(0, 1fr));
    gap: 1.5rem;
    margin-bottom: 2rem;
  }

  .glances-demos figure {
    min-width: 0;
    margin: 0;
  }

  .glances-demos figcaption {
    margin-bottom: 0.5rem;
    font-weight: 600;
  }

  .glances-demos video {
    display: block;
    width: 100%;
    aspect-ratio: 16 / 9;
    object-fit: contain;
    background: #000;
    margin-bottom: 0.5rem;
  }

  @media (max-width: 767px) {
    .glances-demos {
      grid-template-columns: minmax(0, 1fr);
    }
  }
</style>
