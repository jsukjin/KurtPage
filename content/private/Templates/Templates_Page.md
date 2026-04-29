---
title: <% tp.file.title %>
author: KurtJang
tags:
  - Blog
date: <% tp.date.now("YYYY-MM-DD")%>
draft: "False"
---

> [!NOTE] 
> 요약

---
<font color="#68ff6e">Table of Contents</font>

%% create table of contents (옵션 없는거) 를 마지막에 사용해 주세요 %%

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


%% 옵시디언에서만 보이는 주석 %%


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

