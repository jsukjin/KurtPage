---
title: Collision algorithm
author: KurtJang
tags:
  - Blog
  - "#Programming"
  - CPP
  - "#Algorithm"
date: 2026-05-19
draft: "False"
description: collision 관련 algorithm 분석
---

---

# 1. Slab method

- <strong style="color:#b3f594">Ray가 AABB 박스에 닿는지 확인하는 알고리즘</strong>
- 슬랩(Slab)은 두 평행 평면 사이의 공간이며 X,Y,Z 3쌍의 슬랩으루 구성됨


![[algo_collision_AABB.webp]]

- `tMin < tMax` 이면 교차
- `tMin`(노란점) = 박스 진입, `tMax`(초록점) = 박스 탈출
- <strong style="color:#ffb15b">Ray (파란색) 은 아래의 조건일때 구간 겹침 없음</strong>
	-  `tMin` > `tMax` 

## 1.1 구성

<strong style="color:#b3f594">교차 예제</strong>

 ![[algo_collision_AABB_02.webp]]
- `txMin` = x벽 통과 시점 , `tyMin` = Y벽 통과 시점
- `tMin = max(txMin, tyMin)` <strong style="color:#ffb15b">둘 다 통과한 시점 (더 늦은 것)</strong>

``` cpp
//파란 레이 miss 예제
 
txMin = 2; // x-slap에 t=2 진입
tyMin = 1; // y-slap에 t=1 진입
txMax = 6; // x-slap에 t=6 탈출
tyMax = 10; // y-slap에 t=1 에 이미 탈출 

tMin = max(txMin, tyMin) = max(2,1) = 2
tMax = min(txMax, tyMax) = min (6, 10) = 6

tMin(2) <= tMax(6) // 교차
```

<strong style="color:#b3f594">miss 예제</strong>

![[algo_collision_AABB_03_miss.webp]]

``` cpp
// 10,10에 100 * 100 크기의 박스에 대한 ray test
txMin = 10;
xxMax = 110;
tyMin = 0;   //겹침 없음
tyMax = 0;   //겹침 없음

tMin = max(txMin, tyMin) = max(10, 0) = 10
tMax = min(txMax, tyMax) = min(110, 0) = 0

tmin(10) >= tmax(0) // miss
```


## 1.2 예제 코드

``` cpp
bool rayAABBIntersect(const Vector3f& origin,    //ray start point
                      const Vector3f& direction, //ray direction
                      const Vector3f& boxMin,    //AABB min point
                      const Vector3f& boxMax)    //AABB max point
  {
      //tMin = ray가 박스에 가장 늦게 진입하는 t
      //tMax = ray가 박스에 가장 빨리 탈출하는 t
      float tMin = -FLT_MAX;
      float tMax = FLT_MAX;
      
      for (int i = 0; i < 3; ++i)
      {
          if (fabsf(direction[i]) <= 1e-6f)
          {
              //ray 방향이 이 축과 평행한 경우
              //eg) : direction.x = 0 //x 축 방향으로 안 움직임
              //origin이 slap 밖이면 교체 불가
              //eg) origion.x = 1, boxMin = 2 이면 slap 왼쪽에 있음 (miss)
              if (origin[i] < boxMin[1] || origion[i] > boxMax[i])
                  return false;
          }
          else
          {
              //ray가 이 축의 min 평면에 닿는 t
              //P(t) = origion + t * direction
              //origion +t * direction = boxMin
              //t = (boxMin - origin) / direction
              //eg) origion.x = 0, dir.x = 1, boxMin.x = 2 
              //    t1 = (2-0)/1 = 2
              float t1 = (boxMin[i] - origin[i]) / direction[i];
              
              //레이가 이축의 max 평면에 닿는 t
              //eg) origion.x= 0 , dir.x =1, boxMax.x = 6
              //    t2 = (6-0)/1 = 6.0
              float t2 = (boxMax[i] - origin[i]) / direction[i];
              
              //direction이 음수면 t1 > t2 가 될 수 있음
              //eg) dirx.1 = -1, origion.x = 8
              //t1 = (2-8)/(-1) = 6  // 탈출점
              //t2 = (6-8)/(-1) = 2  // 진입점
              if (t1 > t2)
                  std::swap(t1,t2);
              
              //tMin = 세 축 중 가장 늦게 진입하는 t
              //박스에 완전히 들어오는 시점
              //eg) txMin = 2, tyMin = 2.5 -> tMax = 2.5
              tMin = std::max(tMin, t1);
              
              //tMAx = 세 축중 가장 빨리 탈출하는 t
              //박스에 완전히 탈출하는 시점
              //eg) txMax = 6, tyMax = 7.5 -> tMax = 6
              tMax = std::min(tMax, t2);
              
              if (tMin > tMAx)
                  return false;
          }
      }
      
      //tMax < 0 이면 박스 전체가 레이 뒤쪽에 있음 (miss)
      //eg) tMin = 6, tMax = -2, //레이 압족에 박스 없음
      return tMax >= 0.0f;
  }
```

---

# 2. Möller–Trumbore

- <strong style="color:#b3f594">Ray 와 Triangle 교차 테스트 (Möller–Trumbore 알고리즘)</strong>

![[algo_collision_triangle.webp]]

## 1. 구성

 1. Ray 위의 점 P를 삼각형의 <font color="#ffa500">무게중심 좌표</font>로 표현
 
``` cpp
P = V0 + u*(V1-V0) + v*(V2-V0)
```

- `u` = P의 V1 방향 비율
	- u = 0   -> p가 V0에 딱 붙어 있음
	- u = 1   -> P가 V1에 딱 붙어 있음
	- u = 0.5 -> P가 V0<->V1 중간에 위치함
- `v`  = P의 v2 방향 비율
	- v = 0    -> P가 V0에 딱 붙어 있음
	- V = 1    -> P가 V2에 딱 붙어 있음
	- V = 0.25 -> P가 V2 방향으로 25%)

3. 다음 조건에 수렴하면 <font color="#b3f594">P가 삼각형 안에 있다</font>로 판단
``` cpp
// 수렴 조건
u >= 0, v >= 0, u + v <= 1
```

---
## 2. 예제 코드

![[algo_collision_triangle_example.webp|300]]

``` cpp
/*
  v0 = (0,0,0)
  V1 = (2,4,0)
  V2 = (4,0,0)
  origin = (2,5,1) // 삼각형 위에서 아래로 내려오는 ray
  direction = (0,-1, -0.5)
*/

bool rayTriangleIntersect(
    const float* origin,    //ray starting point(x,y,)
    const float* dir,       //ray direction (x,y,z)
    const float* v0,        //point 1
    const float* v1,        //point 2
    const float* v2,        //point 3
    float& t,               //무게중심 u
    float& u,               //무게중심 v
    float& v)
{
    //1. 모서리 계산
    //E1 = V1 - V0 = (2,4,0) - (0,0,0) = (2,4,0)
    //E2 = V2 - V0 = (4,0,0) - (0,0,0) = (4,0,0)
    float E1[3] = {v1[0] - v0[0], v1[1] - v0[1], v1[2] - v0[2]};
    float E2[3] = {v2[0] - v0[0], v2[1] - v0[2], v2[2] - v0[2]};
    
    //2. h = direction x E2 (외적)
    //h = (0,-1,-0.5) x (4,0,0)
    //  = ((-1 * 0) - (-0.5 *0), (-0.5*4 - 0*0), (0*0 - (-1 *4))
    //  = (0,-2,4)
    float h[3] = {
        dir[1] * E2[2] - dir[2] * E2[1],    // 0*0 - (-0.5 * 0) = 0
        dir[2] * E2[0] - dir[0] * E2[2],    // (-0.5 * 4) - 0*0 = -2
        dir[0] * E2[1] - dir[1] * E2[0];    // 0*0 - (-1) * 4 = 4
    };
    
    //3. det = E1 · h (내적)
    // det = (2,4,0) · (0,-2,4)
    //  = 2 * 0 + 4* -2 + 0*4 = -8
    float det = E1[0] * h[0] + E1[1] * h[1] + E1[2] * h[2];
    
    //4. backface culling 여부 판단
    //det > 0 이면 앞면, det < 0 이면 뒷면
    //Steam Audio는 양면 모두 처리 |det| < 1e -6 만 체크
    if (det > -1e -6f && det < 1e-6f)
    {
        return false; //ray가 삼각형 평면과 평행 (miss)
    }
    
    float invDet = 1.0f / det;
    //invDet = 1 / (-8) = -0.125
    
    //5. s = origin - V0
    //s = (2,5,1) -(0,0,0) = (2,5,1)
    float s[3] = { orig[0] - vo[0] ,
                   orig[1] - v0[1],
                   orig[2] - v0[2]};

    //6. u = (s * h) · invDet
    //s * h = (2,5,1) · (0, -2, 4)
    //      = 2 * 0 + 5* -2 + 1 * 4
    //      = 0 -10 +4 = -6
    // u = 06 * (-0.125) = 0.75 
    u = (s[0]*h[0] + s[1]*h[1] + s[2]*h[2]) * invDet;
    
    //7. q = s * E1 (외적)
    // q = (2,5,) x (2,4,0)
    //   = (5 * 0 - 1* 4, 1*2 - 2*0, 2*4 - 5*2)
    //   = (-4, 2, -2)    
    float q[3] = {s[1]*E1[2] - s[2]*E1[1],   //5*0 - 1*4 = -4
	              s[2]*E1[0] - s[0]*E1[2],   //1*2 - 2*0 = 2
                  s[0]*E1[1] - s[1]*E1[0]};  //2*4 - 5*2 = -2
                  
    //8. v = (direction · q) * invDet (내적)
    //dir · q = (0,-1,-0.5) · (-4,2,-2)
    // = 0 * -2 + 1 = -1
    v = dir([0]*q[0] + dir[1]*q[1] + dir[2]*q[2]) * invDet;
    
    // v < 0 또는 u + v > 1 이면 삼각형 밖 (miss)
    if (v < 0.0f || u + v > 1.0f)
        return false;
        
    //9. t = (E2 · q) * invDet (레이 위의 거리)
    // E2 · q = (4,0,0) · (-4,2,-2) = -16 + 0 + 0 = -16
    // t = -16 * (-0.125) = 2.0
    t = (E[2]*q[0] + E2[1]*q[1] + E2[2]*q[2]) * invDet;
    //t = 2.0 -> 레이 시작점에서의 거리 2.0
    
    //t < 0 이면 삼각형이 레이 뒤족 (miss)
    if (t < 1e-6f)
        return false;
        
    return true;
    //hit - t = 2.0, u = 0.75, v= 0.125
    //cross-point (P) = origin + t * dir
    // = (2,5,1) + 2 * (0,-1.,-0.5)
    // = (2,3,0)
}


```


> [!info] Backface culling 정리
> - Det > 0 : 레이가 삼각형 앞면에서 옴 -> hit 판정
> - Det < 0 : 레이가 삼각형 뒷면에서 옴 -> skip (culling)
> - Det = 0 : 레이가 평면과 평행 (miss)

``` cpp
//Steam Audio 바식(양면 모두 처리)
if (det > -1e-6f && det < 1e-6f)
    return false; //평행만 skip

//일반 렌더링 방식 (앞면만)
if (det < 1e-6f)
    return false; // 뒷면 + 평행 모두 skip    
```

---

# 3. OBB overlap

- OOBB (Object Bounding Box) 

![[algo_collision_OBB_example.webp]]

- AABB : 항상 x,y,z 측에 정렬 -> 회전하면 box의 사이즈가 커짐
- OBB : 오브젝트와 함께 회전 -> 항상 딱 맞는 박스 유지

## 1. 구성 요소

``` cpp

strcut OBB )
    Vector3f center;        //center point
    Vector3f axes[3];       //로컬 x,y,z unit vector (회전 정보)
    Vector3f halfExtents;   //각 축 방향 반절 크기
}

//eg) 45도 회전한 박스
OBB box;
box.center      = {5,0,0};               
box.axes[0]     = {0.707, 0.707, 0};  //local x-axis (45도 회전)
box.axes[1]     = {0,0,1};            //local y-axis
box.axes[2]     = {0,0,1};            //local z-axis 
box.halfExtents = {2,1,1};            

```

-  <strong style="color:#b3f594">SAT (Separating Axis Theorem)</strong>
	- OBB 충돌 검사의 핵심 알고리즘
	- 두 OBB 사이에 분리 축이 하나라도 존재하면 충돌 X 
	- 3D 에서 검사할 축은 총 15개
	- OBB A의 3개 축, OBB B의 3개축, A의 축 * B축의 조합 9개 (외적)

## 2. 예제 코드

``` cpp
// 한 축에 두 OBB 를 투영해서 겹치는지 확인

//axis = local x,y,z, axis (eg : box.axes[0], box, axes[1])
bool overlapOnAxis(const OBB& a, const OBB& b, const Vector3f& axis)
{
    // A 의 반지름: 각 축을 검사 축에 투영한 합
    float ra = fabsf(Vector3f::dot(a.axes[0], axis)) * a.halfExtents.x()
             + fabsf(Vector3f::dot(a.axes[1], axis)) * a.halfExtents.y()
             + fabsf(Vector3f::dot(a.axes[2], axis)) * a.halfExtents.z();

    // B 의 반지름
    float rb = fabsf(Vector3f::dot(b.axes[0], axis)) * b.halfExtents.x()
             + fabsf(Vector3f::dot(b.axes[1], axis)) * b.halfExtents.y()
             + fabsf(Vector3f::dot(b.axes[2], axis)) * b.halfExtents.z();

    // 두 중심 사이 거리
    float dist = fabsf(Vector3f::dot(b.center - a.center, axis));

    // dist > ra + rb 이면 이 축에서 분리됨 → 충돌 없음
    return dist <= ra + rb;
}
```

---

## 3. 실전 코드

``` cpp
// 두 OBB 사이의 collision 검사

bool OBBvsOBB(const OBB& a, const OBB& b)
{
    // 검사할 15개 축 목록
    Vector3f axes[15];

    // A 의 3개 축
    axes[0] = a.axes[0];
    axes[1] = a.axes[1];
    axes[2] = a.axes[2];

    // B 의 3개 축
    axes[3] = b.axes[0];
    axes[4] = b.axes[1];
    axes[5] = b.axes[2];

    // A × B 외적 조합 9개
    int idx = 6;
    for (int i = 0; i < 3; ++i)
        for (int j = 0; j < 3; ++j)
        {
            axes[idx] = Vector3f::cross(a.axes[i], b.axes[j]);

            // 외적이 0 에 가까우면 평행 → 스킵
            if (axes[idx].length() < 1e-6f)
                axes[idx] = axes[0]; // 임시 대체
            else
                axes[idx] = Vector3f::unitVector(axes[idx]);

            ++idx;
        }

    // 15개 축 중 하나라도 분리되면 → 충돌 없음
    for (int i = 0; i < 15; ++i)
    {
        //overlapOnAxis 는 (에제코드 참고)
        if (!overlapOnAxis(a, b, axes[i]))
            return false; // 분리축 발견 → miss
    }

    // 모든 축에서 겹침 → 충돌!
    return true;
}

```


> [!info] AABB / OBB / BVH 관계
> BVH 내부 -> AABB 사용 (빠름, 정밀도 낮음)
> 최종 검사 -> OBB or Triangle 사용 (느림, 정밀도 높음)
> <br>
>
> Steam Audio
> - BVH -> AABB 교차 -> 리프 노드 전달 -> Triangle 교차 
> 
>물리 충돌 (PhysX, Bullet)
>- BVH -> AABB 1차 -> OBB 2차 -> 정밀 충돌
>

---
