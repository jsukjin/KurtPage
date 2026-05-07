---
title: Visualizer Test2
author: KurtJang
tags:
  - Blog
date: 2026-03-27
draft: "false"
---

> [!NOTE] 
> 요약

---
<font color="#68ff6e">Table of Contents</font>

- [Code Example](#code-example)
- [Callout Example](#callout-example)

---

들여쓰기

<details>
  <summary>여기를 클릭해서 내용을 확인하세요 (제목)</summary>
  <div markdown="1">
    
    이곳에 펼쳐질 내용을 작성합니다.
    - 리스트도 가능하고
    - **굵은 글씨**도 가능합니다.

  </div>
</details>






---
100%

<iframe 
  src="/static/floodfill_interactive.html" 
  width="100%" 
  height="750"
  style="border:none; border-radius:8px;"
></iframe>

---

90 % center

<div style="display:flex; justify-content:center;">
  <iframe 
    src="/static/floodfill_interactive.html" 
    width="90%" 
    height="750"
    style="border:none; border-radius:8px;"
  ></iframe>
</div>

---

클릭해서 열기


<details style="border-left: 3px solid #4fc3f7; padding-left:16px; margin:16px 0;">
<summary style="cursor:pointer; color:#4fc3f7; font-weight:bold;">
  🔍 FloodFill 시각화 — 클릭해서 열기
</summary>

<div style="display:flex; justify-content:center; margin-top:12px;">
  <iframe 
    src="/static/floodfill_interactive.html" 
    width="100%" 
    height="750"
    style="border:none; border-radius:8px;"
  ></iframe>
</div>

</details>




---

<details style="border-left: 3px solid #4fc3f7; padding-left:16px; margin:16px 0;">
<summary style="cursor:pointer; color:#4fc3f7; font-weight:bold;">
  🔍 FloodFill 시각화 — 클릭해서 열기
</summary>

<div style="display:flex; justify-content:center; margin-top:12px;">
  <iframe 
    src="/static/floodfill_interactive.html" 
    width="80%" 
    height="750"
    style="border:none; border-radius:8px;"
  ></iframe>
</div>

</details>



---
# Code Example
``` cpp fold title:Cmd
au.3dVisualize.Listeners 1
```

``` cpp fold title:subject
int a = 1;
int b = 2;
a + b 3;
```

# Callout Example
> [!info] info
> Contents

> [!todo] todo
> Contents

> [!error] Title
> Contents

> [!question] Title
> Contents

> [!example] Title
> Contents

