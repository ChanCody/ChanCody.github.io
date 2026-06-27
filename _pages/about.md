---
layout: about
title: about
permalink: /
subtitle: 

profile:
  align: right
  image: chan_pic.jpg
  image_circular: false # crops the image to make it circular
  # more_info: >
  #   # <p>Huawei, Shanghai, China</p>

selected_papers: false # includes a list of papers marked as "selected={true}"
social: false # includes social icons at the bottom of the page

announcements:
  enabled: true # includes a list of news items
  scrollable: true # adds a vertical scroll bar if there are more than 3 news items
  limit: 5 # leave blank to include all the news in the `_news` folder

latest_posts:
  enabled: false
  scrollable: true # adds a vertical scroll bar if there are more than 3 new posts items
  limit: 3 # leave blank to include all the blog posts
---

Hello world!👋

I'm a software engineer in [Huawei ADS](https://auto.huawei.com/cn/), Shanghai, China. Our team is focused on sensor fusion and localization for autonomous driving system (ADS).

In 2022, I graduated from Xi'an Jiaotong University and got my master's degree in Machinical Engineer. Under the guidance of Prof. [Xuesong Mei](https://ieeexplore.ieee.org/author/37544593200), my research focused on Machine Vision and optical 3D measurement.

Currently, I'm interested in all kinds of deep-learning related technologies, especially in autonomous driving, SLAM and 3D reconstruction. I hope that L4 autonomous driving comes true in the next decade.

<style>
  h2 a[href$="/news/"] {
    pointer-events: none;
    cursor: default;
    text-decoration: none;
  }
</style>

<script>
  document.addEventListener("DOMContentLoaded", () => {
    document.querySelectorAll('h2 a[href$="/news/"]').forEach((link) => {
      const text = document.createElement("span");
      text.style.color = "inherit";
      text.textContent = link.textContent;
      link.replaceWith(text);
    });
  });
</script>

<!-- # TODO
- add my two articles to publication page
- choose between projects and repositories to show my github repos(projects) -->
