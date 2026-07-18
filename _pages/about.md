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

Hello world! 👋

I'm an AI engineer at [Shanghai Ancient Books Publishing House](https://guji.com.cn/), specializing in OCR, LLMs, and agent orchestration. Our main product is [Huidian](https://www.gujidh.com/), an AI-powered platform for searching and studying ancient Chinese texts.

From 2022 to 2024, I worked as a software engineer on the [Huawei ADS](https://auto.huawei.com/cn/) team, focusing on SLAM for autonomous driving.

In 2022, I earned my master's degree in Mechanical Engineering from Xi'an Jiaotong University. Under the guidance of Prof. [Xuesong Mei](https://ieeexplore.ieee.org/author/37544593200), my research focused on machine vision and optical 3D measurement.

In my spare time, I'm interested in AI and AR glasses, particularly eye-tracking technologies. I hope to see the kind of AR glasses depicted in science fiction become a reality in the future.

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
