---
layout: page
title: Line-Laser 3D Measurement
description: A self-developed hardware–software system for high-precision 3D reconstruction
img: assets/img/publication_preview/voronoi_preview.png
importance: 1
category: work
related_publications: true
---

This project is a complete line-laser 3D measurement system built from the ground up. I independently designed and developed both the hardware and software, integrating image acquisition, system calibration, laser-stripe centerline extraction, 3D reconstruction, and point-cloud generation into a single measurement pipeline.

The reconstruction algorithm builds geometric models of the camera and laser plane. For each captured line-laser image, it extracts the laser-stripe centerline and triangulates the corresponding rays against the calibrated laser plane, recovering a high-precision 3D point cloud of the measured surface.

At the core of the system is my Voronoi-diagram-based centerline extraction method {% cite chen2022voronoi %}. Its graph-centrality-based pruning strategy remains robust under severe image noise: experiments achieved an average centerline extraction accuracy of **0.35 pixels**, while reconstruction of a Φ20 mm standard sphere achieved an average 3D accuracy of **0.0282 mm**.

## Demo

<iframe
  src="https://player.cloudinary.com/embed/?cloud_name=p6fghypy&public_id=videos%2Fline_laser_3d"
  width="640"
  height="360"
  style="height: auto; width: 100%; aspect-ratio: 640 / 360;"
  allow="autoplay; fullscreen; encrypted-media; picture-in-picture"
  allowfullscreen
  frameborder="0"
></iframe>
