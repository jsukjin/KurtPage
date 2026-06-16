---
title: BVH, Octree 분석
author: KurtJang
tags:
  - Blog
  - "#Programming"
  - "#Graphics"
  - "#CPP"
date: 2026-05-19
draft: "False"
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
## 1.1 구성요소

- 루트 노드 (전체 씬 AABB)
	- 내부노드(왼쪽 절반 AABB)
		- 리프 (삼각형 1~2)
		- 리프 (삼각형 3~4)
	- 내부노드(오른쪽 절반 AABB)
		- 리프 (삼각형 5~6)
		- 리프 (삼각형7~8)
		
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

OctreeNode 구조 (예)
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

---

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

# 4. 예제 코드

``` cpp
#include <vector>
#include <algorithm>

// -----------------------------------------------
// AABB — 축 정렬 바운딩 박스
// min/max 로 박스 범위 표현
// -----------------------------------------------
struct AABB {
    float minX, minY, minZ;
    float maxX, maxY, maxZ;

    // 레이가 이 박스에 닿는가?
    bool intersect(float rayOx, float rayOy, float rayOz,
                   float rayDx, float rayDy, float rayDz) const
    {
        // 각 축별로 레이가 박스 범위 안에 들어오는 t 구간 계산
        float tMin = (minX - rayOx) / rayDx;
        float tMax = (maxX - rayOx) / rayDx;
        if (tMin > tMax) std::swap(tMin, tMax);

        float tyMin = (minY - rayOy) / rayDy;
        float tyMax = (maxY - rayOy) / rayDy;
        if (tyMin > tyMax) std::swap(tyMin, tyMax);

        if (tMin > tyMax || tyMin > tMax) return false;
        tMin = std::max(tMin, tyMin);
        tMax = std::min(tMax, tyMax);

        float tzMin = (minZ - rayOz) / rayDz;
        float tzMax = (maxZ - rayOz) / rayDz;
        if (tzMin > tzMax) std::swap(tzMin, tzMax);

        if (tMin > tzMax || tzMin > tMax) return false;
        return true;
    }
};

// -----------------------------------------------
// Triangle — 인덱스 3개짜리 삼각형
// -----------------------------------------------
struct Triangle {
    int indices[3];  // 버텍스 배열의 인덱스
};

// -----------------------------------------------
// BVHNode — BVH 트리의 노드 하나
// -----------------------------------------------
struct BVHNode {
    AABB bounds;            // 이 노드를 감싸는 박스

    int leftChild  = -1;   // 왼쪽 자식 인덱스 (-1 = 없음)
    int rightChild = -1;   // 오른쪽 자식 인덱스 (-1 = 없음)

    int triangleStart = -1; // 리프 노드: 담당 삼각형 시작 인덱스
    int triangleCount = 0;  // 리프 노드: 담당 삼각형 수

    bool isLeaf() const { return leftChild == -1; }
};

// -----------------------------------------------
// BVH — 빌드 + 쿼리
// -----------------------------------------------
struct BVH {
    std::vector<BVHNode> nodes;

    // 삼각형들로 BVH 빌드
    void build(const std::vector<Triangle>& triangles)
    {
        nodes.clear();

        // 루트 노드 생성 → 모든 삼각형 포함
        BVHNode root;
        root.triangleStart = 0;
        root.triangleCount = static_cast<int>(triangles.size());
        root.bounds = calcAABB(triangles, 0, root.triangleCount);
        nodes.push_back(root);

        // 재귀적으로 분할
        subdivide(0, triangles);
    }

    // 레이 쏘기 — 충돌 여부 반환
    bool anyHit(float ox, float oy, float oz,
                float dx, float dy, float dz) const
    {
        return traverse(0, ox, oy, oz, dx, dy, dz);
    }

private:
    // 노드를 둘로 분할
    void subdivide(int nodeIdx, const std::vector<Triangle>& triangles)
    {
        BVHNode& node = nodes[nodeIdx];

        // 삼각형이 2개 이하면 리프 노드로 확정
        if (node.triangleCount <= 2)
            return;

        // 중앙값 기준으로 X축 분할 (단순 버전)
        // 실제 BVH는 SAH 기준으로 최적 축/위치를 찾음
        float midX = (node.bounds.minX + node.bounds.maxX) / 2.0f;

        int mid = node.triangleStart + node.triangleCount / 2;

        // 왼쪽 자식
        BVHNode leftNode;
        leftNode.triangleStart = node.triangleStart;
        leftNode.triangleCount = mid - node.triangleStart;
        leftNode.bounds = calcAABB(triangles, 
                        leftNode.triangleStart, 
                        leftNode.triangleCount);
                        
        nodes.push_back(leftNode);
        nodes[nodeIdx].leftChild = static_cast<int>(nodes.size()) - 1;

        // 오른쪽 자식
        BVHNode rightNode;
        rightNode.triangleStart = mid;
        rightNode.triangleCount = node.triangleStart + 
                                  node.triangleCount - mid;
        rightNode.bounds = calcAABB(triangles, 
                                    rightNode.triangleStart,
                                    rightNode.triangleCount);
        nodes.push_back(rightNode);
        nodes[nodeIdx].rightChild = static_cast<int>(nodes.size()) - 1;

        // 재귀 분할
        subdivide(nodes[nodeIdx].leftChild, triangles);
        subdivide(nodes[nodeIdx].rightChild, triangles);
    }

    // 레이 순회
    bool traverse(int nodeIdx,
                  float ox, float oy, float oz,
                  float dx, float dy, float dz) const
    {
        const BVHNode& node = nodes[nodeIdx];

        // 이 노드의 AABB 와 레이 교차 검사
        if (!node.bounds.intersect(ox, oy, oz, dx, dy, dz))
            return false;  // 박스 miss → 스킵

        if (node.isLeaf())
        {
            // 리프 도달 → 실제 삼각형 교차 검사
            // 예시: node.triangleStart ~ triangleStart+triangleCount 범위
            // 실제 구현에서는 여기서 Möller–Trumbore 알고리즘 사용
            return true;  // 간단히 hit 반환
        }

        // 자식 노드 재귀 탐색
        bool hitLeft  = traverse(node.leftChild,  ox, oy, oz, dx, dy, dz);
        bool hitRight = traverse(node.rightChild, ox, oy, oz, dx, dy, dz);

        return hitLeft || hitRight;
    }

    // 삼각형 범위의 AABB 계산
    AABB calcAABB(const std::vector<Triangle>& triangles,
                  int start, int count)
    {
        // 간단히 전체 씬 범위 반환 (실제로는 버텍스 좌표로 계산)
        return AABB{ 0, 0, 0, 10, 10, 10 };
    }
};
```

