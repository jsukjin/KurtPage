---
title: Custom Acoust System
author: KurtJang
tags:
  - Blog
date: 2026-03-27
draft: "true"
description: "요약"
---

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


**그래프 탐색 기반**

- **BFS (너비 우선 탐색)** — FloodFill의 기반이 되는 알고리즘. 최단 경로 보장 (가중치 없는 그래프)
- **DFS (깊이 우선 탐색)** — 미로 생성, 연결 요소 탐색에 자주 사용
- **Dijkstra** — 가중치 있는 그래프에서 단일 출발점 최단 경로
- **A* (A-Star)** — Dijkstra + 휴리스틱. 게임 AI 길찾기의 사실상 표준
- **Bellman-Ford** — 음수 가중치 간선도 처리 가능


**계층/계획 기반**

- **Jump Point Search (JPS)** — 격자 맵에서 A*보다 훨씬 빠름. 게임 엔진에서 많이 씀
- **HPA* (Hierarchical Pathfinding A*)** — 맵을 구역 단위로 나눠 대규모 월드에 적합. Wwise/게임 AI에서 활용
- **NavMesh Pathfinding** — 폴리곤 기반 내비게이션 메쉬 위에서 A* 적용. Unreal/Unity 표준

**특수 목적**

- **D* Lite** — 동적 환경(장애물이 바뀌는 경우)에 최적. 로보틱스에서 사용
- **Theta*** — A*의 변형, 격자 제약 없이 어느 각도로든 이동 가능 (Any-angle pathfinding)
- **Flow Field Pathfinding** — 다수의 유닛이 같은 목적지로 이동할 때 효율적. RTS 게임에서 사용



## 도달 가능 영역 판별 알고리즘

### 1. FloodFill (BFS/DFS 기반)

**동작:** 시작점에서 인접 셀을 재귀/큐로 퍼져나가며 연결 영역 전체를 마킹

|장점|단점|
|---|---|
|구현 간단|맵 전체를 탐색해서 느릴 수 있음|
|직관적|동적 환경(장애물 변화)마다 재계산 필요|
|메모리 예측 쉬움|대규모 맵에서 메모리 부담|

---

### 2. Union-Find (Disjoint Set)

**동작:** 맵의 각 셀을 노드로 보고, 인접한 빈 셀끼리 같은 집합으로 묶음. `find(A) == find(B)` 이면 연결됨

|장점|단점|
|---|---|
|연결 여부 쿼리가 **O(α)** (사실상 O(1))|초기 구축 비용 있음|
|장애물 **추가**에 대한 업데이트 빠름|장애물 **제거**는 재구축 필요|
|대규모 정적 맵에 강함|구현이 FloodFill보다 복잡|

---

### 3. BFS (너비 우선 탐색) 단독

**동작:** FloodFill과 유사하지만 목적지까지의 **거리도 같이 계산**

|장점|단점|
|---|---|
|최단 거리도 동시에 파악|FloodFill보다 무거움|
|레이어별(거리별) 도달 가능 영역 파악|역시 동적 환경에 약함|

---

### 4. Bitmasked Connectivity

**동작:** 맵을 비트 배열로 표현하고 비트 연산으로 연결 영역 계산

|장점|단점|
|---|---|
|매우 빠름 (비트 연산)|구현 복잡|
|메모리 효율 최고|맵 크기 제한 있음|
|임베디드/모바일에 유리|가중치/복잡한 지형 표현 어려움|

---

### 5. Hierarchical Connectivity (계층적 연결성)

**동작:** 맵을 청크/구역으로 나누고, 구역 간 연결성만 먼저 확인. HPA*의 전처리 단계와 동일

|장점|단점|
|---|---|
|대규모 맵에서 압도적으로 빠름|구현 난이도 높음|
|부분 업데이트 가능|청크 경계 처리 까다로움|
|Unreal NavMesh가 이 방식|정밀도가 청크 크기에 의존|

---

## 상황별 추천

```
소규모 맵 / 단순 구현    → FloodFill
정적 맵 + 빠른 쿼리      → Union-Find
거리 정보도 필요          → BFS
대규모 맵 / 실시간 게임  → Hierarchical Connectivity
메모리 극도로 아껴야 함  → Bitmasked
```

---

Unreal + Wwise 환경이시면 NavMesh가 Hierarchical Connectivity를 내부적으로 쓰고 있어서, 사운드 오브젝트 도달 가능 여부는 NavMesh 쿼리(`UNavigationSystemV1::IsLocationReachable`) 로 처리하면 별도 구현 없이 바로 쓸 수 있어요.


FloodFill → 도달 가능 영역 확인 

A* / Dijkstra → 그 안에서 최적 경로 계산 

Bresenham / Raycast → 경로 스무딩 or LoS 체크


![[Custom Acoustic System-1774588571917.webp]]


![[Custom Acoustic System-1774588599776.webp]]




![[Steam Audio-1774540276334.webp]]


![[Custom Acoustic System-1774920097702.webp]]



![[Custom Acoustic System-1774920163812.webp]]




---

![[Custom Acoustic System-1775467389535.webp]]
voxelsize 10



![[Custom Acoustic System-1775467611953.webp]]
voxelsize = 20



![[Custom Acoustic System-1775467551233.webp]]
voxlesize = 30






---


## 원인 분석

```
현재 코드:
    Primitive->Bounds.GetBox()
    → 이건 월드 공간 AABB (Axis-Aligned)
    → 회전된 메시의 경우 실제 형태보다 훨씬 큰 박스가 나옴

사진의 상황:
    주황색 직육면체가 비스듬히 회전되어 있음
    → AABB는 회전을 감싸는 더 큰 정렬 박스
    → 실제 메시보다 훨씬 넓은 영역에 Density 세팅됨
    → 파란 점선 영역이 실제 메시보다 크게 표시되는 이유
```

---

## 근본적인 해결 방향

|방법|정확도|비용|Physics 독립|
|---|---|---|---|
|A. World AABB (현재)|낮음 (회전 오차)|최저|✅|
|B. OBB (Object Aligned Box)|높음|낮음|✅|
|C. Convex Hull 복셀화|매우 높음|높음|✅|
|D. OverlapTest per Cell|정확|게임스레드 비용|❌|

**CAS 설계에 맞는 선택 = B. OBB**

```
Primitive의 로컬 공간 Box Extent를 읽고
Actor Transform을 적용해서
회전이 반영된 실제 형태로 셀 점유 판별
```

---

## OBB 복셀화 원리

```
로컬 공간에서:
    Box Extent = (HalfX, HalfY, HalfZ) 읽기

각 셀에 대해:
    셀 중심을 Primitive의 로컬 공간으로 역변환
    → 로컬 공간에서 |LocalPos| <= Extent 인지 확인
    → 맞으면 Density 세팅
```

핵심은 **셀을 월드로 변환하는 게 아니라, 셀을 Primitive 로컬로 역변환**하는 거예요.

---

확인 하나만 할게요:

완벽해요. **StaticMesh OBB + Transform 전체 반영**으로 갈게요.

---

## 핵심 개념

```
기존 (AABB):
    월드 공간에서 Min/Max 박스 → 회전 무시

수정 (OBB):
    각 셀 중심을 Primitive의 InverseTransform으로
    로컬 공간으로 변환 → 로컬에서 BoxExtent와 비교

    셀이 OBB 안에 있다 =
        |LocalPos.X| <= HalfExtent.X &&
        |LocalPos.Y| <= HalfExtent.Y &&
        |LocalPos.Z| <= HalfExtent.Z
```

AABB는 1차 컬링에만 사용하고, 실제 점유 판별은 OBB로 해요.

## 변경 요약 ``` 
기존 ApplyPrimitiveAABB: PrimBox.Intersect(CellBox) 
→ 월드 공간 AABB vs 셀 AABB 
→ 회전 무시 새 ApplyPrimitiveOBB: 

WorldTransform.InverseTransformPosition(CellCenter) 
→ 셀 중심을 Primitive 로컬 공간으로 변환 
→ 로컬에서 |Pos| <= Extent 비교


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
    width="90%" 
    height="750"
    style="border:none; border-radius:8px;"
  ></iframe>
</div>

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

