---
title: "[lgorithm] BVH, Octree 분석"
author: KurtJang
tags:
  - Blog
  - "#Programming"
  - "#Graphics"
  - "#CPP"
date: 2026-05-19
draft: "True"
description: BVH (Bounding volume Hierarchy), Octree 분석
---

---

# 1. BVH

- 레이 트레이싱을 빠르게 만드는 tree 자료 구조

![[algo_BVH_concept.webp]]


> [!info] 왜 필요한가?
> 예 : 씬에 삼각형 10만개 있을때 레이를 쏜다면
> - BVH 없음 -> 10만개 전부 교차 검사 -  `O(n)`
> - BVH 있음 -> log(10만) = 17번만 검사 - `O(log n)`

---
# 1.1 구성요소

루트 노드 (전체 씬 AABB)
    ├── 내부 노드 (왼쪽 절반 AABB)
    │       ├── 리프 (삼각형 1~2)
    │       └── 리프 (삼각형 3~4)
    └── 내부 노드 (오른쪽 절반 AABB)
            ├── 리프 (삼각형 5~6)
            └── 리프 (삼각형 7~8)

---

## 1.2 핵심 개념

### AABB
- AABB (Axis-Aligned Bounding Box)
- 삼각형을 감싸는 가장 작은 박스

``` 
삼각형 비교 검사 -> 수학적 계산, 복잡 느림
AABB 교차 검사 -> 범위 비교 6번, 매우 빠름
```

### SAH
- SAH (Surface Area Heuristic)
- BVH를 어떻게 분할할지 결정하는 기준
- 단순히 반으로 나누는게 아니라 레이 교차 확률을 기반으로 최적 분할점 도출

``` 
비용 = (왼쪽 표면적 / 부모 표먼적) * 왼쪽 삼각형수 +
       (오른쪽 표면적 / 부모 표면적) * 오른쪽 삼각형 수
```

---

# 2. Octree

![[algo_Octree_concept.webp]]

- 공간을 8등분한 자료 구조
- 3D 공간을 x,y,z 축으로 각각 반으로 나눠서 8개의 child cell을 만든다

## 2.1 구성 요소

OctreeNode 예제
``` cpp
strcut OctreeNode{
	AABB bounds,                //해당 셀의 공간 범위
	OctreeNode* children[8];    //8개의 자식 (null = 리프)
	std::vector<int> objets;    //이 셀에 속한 오브젝트들
}
```


> [!info] 분할 조건
> 1. 셀안의 오브젝트 수 (최대 허용 8개)
> 2. 이 셀을 8등분으로 분할
> 3. 자식셀로 이동
> 4. 자식셀에서 8등분으로 분할
> 5. 재귀 반복

# 3. 비교

Octree / BVH 비교
![[algo_compare_BVH_octree.webp]]

|         | Octree       | BVH        |
| ------- | ------------ | ---------- |
| 분할 기준   | 공간 균등 분할     | 오브젝트 기준 분할 |
| 박스 크기   | 균등           | 제각각        |
| 오브젝트 중복 | 있음           | 없음         |
| 빈 공간    | 있음           | 없음         |
| 주 용도    | 렌더링 컬링, 충동감지 | 레이 트레이싱    |
| 동적 오브젝트 | 업데이트 쉬움      | 재빌드 필요     |

> [!info] 게임 사용 예제
> 1. 렌더링 -> Octree / BVH (카메라 밖 오브젝트 컬링)
> 2. 물리 충돌 -> Octree (동적 오브젝트 많음)
> 3. 레이 캐스트 -> BVH (정밀도 중요)
> 4. 음향 시뮬 -> BVH (Steam Audio)
> <br>
><strong><font color="#b3f594">Unreal Engine 5</font></strong>
>- Lumen (전역 조명) -> BVH (Mesh Distance Field) 
>- 물리 충돌 -> PhysX BVH (Chaos)
>- 렌더링 컬링 -> BVH + Octree 
><br>
><strong><font color="#b3f594">Unity DOTS</font></strong>
>- 정적 collider -> BVH
>- 동적 collider -> 매 피프레임 BVH 부분 재빌드


---










---

<font color="#b3f594">1. 역할 분리</font>
<font color="#b3f594">1. 역할 분리</font>
<font color="#b3f594">1. 역할 분리</font>
<font color="#b3f594">1. 역할 분리</font>


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


<font color="#2ecc71">초록색 텍스트</font>
<font color="#3498db">파란색 텍스트</font>
<font color="#ff4d4d">빨간색 텍스트</font>
<font color="#ffa500">주황색 텍스트</font>
<font color="#f1c40f">노란색 텍스트</font>

<font color="#b3f594">■ 이미지의 그 초록색 (연두)</font>
<font color="#80dfff">■ 시원한 밝은 파란색</font>
<font color="#ff6b6b">■ 예쁜 다홍빛 빨간색</font>
<font color="#ffb15b">■ 질문하신 주황색</font>
<font color="#ffff80">■ 눈 안 아픈 부드러운 노란색</font>

<strong style="color:#b3f594">연두색 (이미지 속 그 색상)</strong>
<strong style="color:#80dfff">밝은 하늘색 (정보/참고)</strong>
<strong style="color:#ff6b6b">다홍색 (주의/경고)</strong>
<strong style="color:#ffb15b">주황색 (핵심 키워드)</strong>
<strong style="color:#ffff80">부드러운 노란색 (강조)</strong>

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

> [!tip] 팁 (보통 민트/연초록)
> 내용을 입력하세요.

> [!success] 성공 (보통 초록/민트)
> 완료된 항목이나 긍정적인 내용을 넣기 좋습니다.

> [!check] 체크 (success와 비슷함)
> 확인이 필요한 내용에 사용하세요.