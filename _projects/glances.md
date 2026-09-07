---
layout: page
title: Glances AR Glasses
description: High-precision eye tracking on low-cost hardware, powered by our custom GlanceNet model
permalink: /projects/glances/
importance: 2
category: work
---

What if interacting with a screen started with simply looking at it? **Glances (览司)** brings a large virtual display and binocular eye tracking together in AR glasses, making your gaze part of the interface. Look to move the cursor or highlight a target, then use gestures, touch, or voice to take action.

We're building toward an experience where looking, choosing, and acting flow naturally together—from playing a game to working with an AI assistant. Glances starts with a simple idea: the screen in front of your eyes should understand where your attention goes.

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

## Core Technology

At the heart of Glances is **GlanceNet**, our custom multimodal eye-tracking model. Inspired by advances in autonomous driving, it brings **high-precision gaze estimation to low-cost hardware**. We develop the model and hardware together, using advances in algorithms to get more out of a compact, accessible sensing setup.

Our dedicated eye-tracking dataset spans different scenarios and contains approximately **8 million samples**, giving us a foundation for developing and refining GlanceNet. Rapid calibration connects gaze estimates to on-screen interaction, while the integrated sensing and inference pipeline brings the whole experience to life.

## From Model to Working Prototype

Our prototype achieves an eye-tracking error of approximately **0.5° on low-cost hardware** using GlanceNet. It's an exciting step toward bringing precise gaze interaction into everyday AR glasses—and the foundation for the hands-on demos above.

## Applications

Eye tracking opens up new ways to play, communicate intent, and get things done. Our prototype demos bring three of those possibilities to life:

- **Gaze-controlled games:** make looking part of the action, with eye movements adding a new dimension to gameplay.
- **Gaze-aware agents:** give an AI assistant a clue to what you mean by showing it where you're looking.
- **Gaze-assisted productivity:** pair the directness of gaze with the expressiveness of voice to interact with on-screen content.

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
