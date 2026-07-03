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

# 1. Intorduction

대표적인 Ray algorithm은 다음과 같다

<strong style="color:#b3f594">1. Moller-Trumbore</strong>
- <font color="#ffb15b">대상 : Ray - Triangle</font>
- 저장소 불필요, 행렬식 없음
- barycentric(u,v) 동시 산출
- 외적 2회  + 내적 3회
- 삼각형 1개씩 순차검사

<strong style="color:#b3f594">2. William slab test</strong>
- <font color="#ffb15b">대상 : Ray - AABB</font>
- branchless, 나눗셈 없음
- 부호 배열로 near/far 선택
- BVH Treversal  hot pass 최적

<strong style="color:#b3f594">3. Quadratic(구)</strong>
- <font color="#ffb15b">대상 : Ray - Sphere</font>
- 수식 단순, 구현 5종
- 판별식 D로 miss 조기 탈출
- sqrt() 비용발생

<strong style="color:#b3f594">4. Woop (precomp)</strong>
- <font color="#ffb15b">대상 : Ray - Triangle</font>
- 삼각형당 행렬 사전 계산
- runtime 내적3회
- SIMD 패킹 최적화
- 삼각형당 48 bytes 추가 저장
- EMbree 내부 사용
 
<strong style="color:#b3f594">5. Piucker coord</strong>
- <font color="#ffb15b">대상 : Ray - Triangle</font>
- winding order 동시 판별
- 일관된 부호로 분기 제거
- 삼각형당 6-coord 사전 계산
- **현재 거의 사용 안함**

<strong style="color:#b3f594">6. Badouel(bary)</strong>
- <font color="#ffb15b">대상 : Ray - Triangle</font>
- 평면 교점 후 2D projection
- 구현 직관적
- 나눗셈 포함, 수치 불안정
- **Moller 보다 연산 많음 (old version)**


---
# 2. Ray - Triangle

## A.  Möller–Trumbore


![[algo_collision_triangle.webp]]

### 1. 구성

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
### 2. 예제 코드

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
    
    //3. determinant = E1 · h (내적)
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

    //6. u = (s * h) · invDet (내적)
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
        
    //9. t = (E2 · q) * invDet (레이 위의 거리) (dot)
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

# 3. Ray - Box

## A. Slab method

- <strong style="color:#b3f594">Ray가 AABB 박스에 닿는지 확인하는 알고리즘</strong>
- 슬랩(Slab)은 두 평행 평면 사이의 공간이며 X,Y,Z 3쌍의 슬랩으루 구성됨


![[algo_collision_AABB.webp]]

- `tMin < tMax` 이면 교차
- `tMin`(노란점) = 박스 진입, `tMax`(초록점) = 박스 탈출
- <strong style="color:#ffb15b">Ray (파란색) 은 아래의 조건일때 구간 겹침 없음</strong>
	-  `tMin` > `tMax` 

### 1. 구성

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


### 2. 예제 코드

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

## B. Ray - OBB

- `slap test` 는 SAT(separating Axis Theorem)를 축이 고정된 케이스에 특화
- `Ray-OBB` 는 그것을 OBB로 바꾼 형태 (구조가 거의 동일)

``` cpp

// OBB 정의 
struct OBB { Vec3 center; 
Vec3 axes[3]; // 단위벡터, 서로 직교 
float halfExtents[3]; }; 

bool rayOBB(const Ray& r, const OBB& obb, float& tOut) 
{ 
    Vec3 d = r.origin - obb.center; 
    float tmin = -INF, tmax = +INF; 
    for (int i = 0; i < 3; i++) 
    { 
        float e = dot(obb.axes[i], d); // origin을 축에 투영 
        float f = dot(obb.axes[i], r.dir); // dir을 축에 투영 
        if (fabsf(f) > EPS) 
        { 
            float t1 = (e + obb.halfExtents[i]) / f; // near slab 
            float t2 = (e - obb.halfExtents[i]) / f; // far slab 
            
            if (t1 > t2) swap(t1, t2); 
            tmin = max(tmin, t1); 
            tmax = min(tmax, t2); 
            
            if (tmin > tmax) return false; // 조기 탈출 
		} 
		else if (-e - obb.halfExtents[i] > 0 || -e + obb.halfExtents[i] < 0) 
		    return false; // 레이가 이 슬랩에 평행 + 밖에 있음
		}
	}
	
	tOut = (tmin > 0) ? tmin : tmax; 
	return tmax >= 0;
}

// 한 축에 대해 레이의 투영 구간과 OBB 투영 구간 겹침 검사 
auto slabOnAxis = [&](Vec3 axis) -> bool 
{ 
    float e = dot(axis, obb.center - r.origin); 
    float f = dot(axis, r.dir); 
    float h = dot(axis, obb.axes[0]) * obb.he[0] // OBB를 축에 투영 
            + dot(axis, obb.axes[1]) * obb.he[1] 
            + dot(axis, obb.axes[2]) * obb.he[2]; 
    return fabsf(e) <= h + fabsf(f) * tmax; }; 
    
// OBB의 3 face 축 검사 (= 방법1과 동일 결과) 
for (int i=0;i<3;i++)
{
    if (!slabOnAxis(obb.axes[i])) return false;  
} 

// 레이 dir × OBB 축 cross 3개 추가 검사 (얇은 슬랩 감지) 
for (int i=0;i<3;i++) 
{
    if (!slabOnAxis(cross(r.dir, obb.axes[i])))
    {
        return false;
    }  
}

return true;


```


---


# 4. Ray - Sphere

## A. Quadratic Equation

### 1. 구성

광선과 구가 만나는 점을 찾으려면, **광선의 방정식**과 **구의 방정식**을 연립해야 합니다. 
이 연립하는 과정에서 자연스럽게 2차 방정식이 만들어집니다.


<strong style="color:#b3f594">1. Ray Equation</strong>

- 시작점($P_0$), 벡터($D$), 시간(t)

$$P(t) = P_0 + tD \quad (t \ge 0)$$


<strong style="color:#b3f594">2. Sphere Equation</strong>

- 중심(C), 반지름(r)인 구 표면에 임의의 점 P는 다음 조건을 만족한다

$$(P - C) \cdot (P - C) = r^2$$


<strong style="color:#b3f594">3. 연립하여 2차 방정식 만들기</strong>

- 광선이 구와 만나는 점의 위치  $P(t)$가 구의 방정식도 만족하는 순간
- 구의 방정식에 $P(t)$ 대입
$$((P_0 + tD) - C) \cdot ((P_0 + tD) - C) = r^2$$

- 광선의 시작점에서 구의 중심을 뺀 변위 벡터를 $V = P_0 - C$라고 정의

$$(tD + V) \cdot (tD + V) = r^2$$
$$t^2(D \cdot D) + 2t(D \cdot V) + (V \cdot V) - r^2 = 0$$

- 이 식은 우리가 잘 아는 $at^2 + bt + c = 0$ 형태의 **$t$에 대한 2차 방정식**입니다!
 
$$at^2 + bt + c = 0$$

- $a = D \cdot D$ (만약 방향 벡터 $D$가 정규화(내적값이 1)되어 있다면 $a = 1$이 됩니다.)
    
- $b = 2(D \cdot V)$
    
- $c = (V \cdot V) - r^2$



<strong style="color:#b3f594">4. 교차여부 판단</strong>

이제 근의 공식에 쓰이는 판별식 $B^2 - 4ac$ (여기서는 $b^2 - 4ac$)를 사용해 구와 광선의 관계를 
알 수 있습니다.

- **판별식 < 0**: 실근이 없음 $\rightarrow$ 광선이 구를 **비껴감** (교점 0개)
    
- **판별식 = 0**: 중근 $\rightarrow$ 광선이 구의 표면에 **접함** (교점 1개)
    
- **판별식 > 0**: 서로 다른 두 실근 $\rightarrow$ 광선이 구를 **뚫고 지나감** (교점 2개)
    

교점이 있을 때, 근의 공식으로 구한 $t$ 값 중  <font color="#ffa500">더 작고 0보다 큰 값 </font> 이 광선이 
구와 처음 부딪히는 실제 지점이 됩니다.

    
---

### 2. 예제 코드

``` cpp
#include <iostream>
#include <cmath>

// 3차원 벡터 구조체
struct Vector3 {
    float x, y, z;

    Vector3 operator+(const Vector3& v) const 
    { 
        return {x + v.x, y + v.y, z + v.z}; 
    }
    Vector3 operator-(const Vector3& v) const 
    { 
        return 
	{x - v.x, y - v.y, z - v.z}; }
	
    Vector3 operator*(float s) const 
    { 
        return {x * s, y * s, z * s}; 
    }
    
    // 내적 (Dot Product)
    float dot(const Vector3& v) const 
    {
        return x * v.x + y * v.y + z * v.z;
    }
};

// 광선 구조체
struct Ray {
    Vector3 origin;    // 시작점 (P0)
    Vector3 direction; // 방향 벡터 (D) - 정규화되었다고 가정
};

// 구 구조체
struct Sphere {
    Vector3 center;    // 중심 (C)
    float radius;      // 반지름 (r)
};

// 교차 검사 함수
bool intersectRaySphere(const Ray& ray, const Sphere& sphere, float& t_hit) 
{
    Vector3 V = ray.origin - sphere.center; // P0 - C

    // 2차 방정식의 계수들 (방향 벡터 ray.direction이 정규화되어 있어 a = 1)
    float a = ray.direction.dot(ray.direction); 
    float b = 2.0f * ray.direction.dot(V);
    float c = V.dot(V) - (sphere.radius * sphere.radius);

    // 판별식 계산
    // 근의 공식 b^2 - 4ac
    float discriminant = b * b - 4.0f * a * c;

    // 판별식이 0보다 작으면 만나지 않음
    if (discriminant < 0.0f) 
    {
        return false;
    }

    // 근의 공식을 사용하여 t 구하기
    // 광선이 나아가는 방향이므로, 둘 중 더 가까운(작은) 앞쪽 교점을 찾음
    // 근의 공식
    // t = (-b +- sqrt(b^2 -4ac)) / 2a
    float t1 = (-b - std::sqrt(discriminant)) / (2.0f * a);
    float t2 = (-b + std::sqrt(discriminant)) / (2.0f * a);

    // t는 무조건 0 이상이어야 함 (광선 진행 방향의 앞쪽만 유효)
    if (t1 >= 0.0f) 
    {
        t_hit = t1;
        return true;
    }
    if (t2 >= 0.0f) 
    {
        t_hit = t2;
        return true;
    }

    // 구가 광선 뒤쪽에 있는 경우
    return false;
}

int main() {
    // 원점에 위치하고 반지름이 2인 구
    Sphere sphere = { {0.0f, 0.0f, 0.0f}, 2.0f };

    // (0, 0, 5)에서 시작해 구 중심 방향(0, 0, -1)으로 쏘는 광선
    Ray ray = { {0.0f, 0.0f, 5.0f}, {0.0f, 0.0f, -1.0f} };

    float t;
    if (intersectRaySphere(ray, sphere, t)) 
    {
        std::cout << "구체와 충돌했습니다! 충돌 거리(t): " << t << std::endl;
        Vector3 hitPoint = ray.origin + ray.direction * t;
        std::cout << "충돌 좌표: (" << hitPoint.x << ", " << hitPoint.y << ",
        " << hitPoint.z << ")" << std::endl;
    } 
    else 
    {
        std::cout << "충돌하지 않았습니다." << std::endl;
    }

    return 0;
}
```


---


# 4. Overlap

## A. AABB vs Sphere

### 1. 원리

구의 중심 좌표를 Box의 min/max 범위 안으로 구겨 넣으면 (clamp) 
그 지점이 바로 <strong style="color:#ffb15b">Box 위에서 구체 줌심과 가장 가까운 점 </strong>


1. 구체의 중심(C)에서 가장 가까운점 P를 구한다

	- $P.x = \max(\text{Box.Min.x}, \min(C.x, \text{Box.Max.x}))$
	- $P.y = \max(\text{Box.Min.y}, \min(C.y, \text{Box.Max.y}))$
	- $P.z = \max(\text{Box.Min.z}, \min(C.z, \text{Box.Max.z}))$

2. 구체의 중심(C)와 찾은 점(P) 사이의 거리의 제곱을 구한다
3. 그 값이 반지름의 제곱(r^2)보다 작거나 같다면 Overlap


### 2. 예제 코드

``` cpp
struct AABB { Vector3 min; Vector3 max; }; 
struct Sphere { Vector3 center; float radius; }; bool 

bool checkOverlapAABBSphere(const AABB& box, const Sphere& sphere) 
{ 
    // 1. Box 위에서 구체 중심과 가장 가까운 점(Closest Point) 찾기 
    float closestX = std::max(box.min.x, 
                              std::min(sphere.center.x, box.max.x)); 
    float closestY = std::max(box.min.y, 
                              std::min(sphere.center.y, box.max.y)); 
    float closestZ = std::max(box.min.z, 
                              std::min(sphere.center.z, box.max.z)); 
    
    // 2. 구체 중심과 Closest Point 간의 거리 제곱 계산 
    float distanceSq = (closestX - sphere.center.x) * 
                       (closestX - sphere.center.x) + 
                       (closestY - sphere.center.y) * 
                       (closestY - sphere.center.y) + 
                       (closestZ - sphere.center.z) * 
                       (closestZ - sphere.center.z); 
                       
   // 3. 반지름 제곱과 비교 
   return distanceSq <= (sphere.radius * sphere.radius);
}
```

---


## B. OBB vs Sphere

### 1. 원리

회전된 상자(Oriented Bounding Box)와 Sphere의 Overlap 체크 역시 AABB와 동일하게
<strong style="color:#ffb15b">Box 위에서 구체 줌심과 가장 가까운 점 </strong>을 찾는것이 핵심


<strong style="color:#b3f594">1. Local Space 변환</strong>

OBB는 일반적으로 다음과 같은 정보로 정의
- Center : 상자의 월드 중심점
- Extents : 상자의 절반 크디 (중시->각 면까지의 거리)
- Axes : 상자가 바라보는 방향을 나타내는 vector (normalized)

<strong style="color:#b3f594">2. 구체 중심에서 상대 vector 구하기</strong>

먼저 구체의 월드 중심점 $C_{sphere}$에서 OBB의 중심점 $C_{box}$를 빼서 
상자 중심 기준의 상대 위치 벡터 $V$를 구합니다.

$$V = C_{sphere} - C_{box}$$

<strong style="color:#b3f594">3. Obb의 로컬 축으로 projection</strong>

상대 벡터 $V$를 OBB의 세 가지 로컬 방향 축($U_x, U_y, U_z$)에 각각 내적(Dot Product)합니다. 
이렇게 하면 구체의 중심이 상자의 로컬 좌표계 기준으로 어디에 와있는지 
좌표 값($L_x, L_y, L_z$)이 나옵니다.

$$L_x = V \cdot U_x, \quad L_y = V \cdot U_y, \quad L_z = V \cdot U_z$$


<strong style="color:#b3f594">3. Local Space에서 Clamping 및 거리 비교</strong>

이제 상자의 절반 크기(Extents)인 `[-Extent, +Extent]` 범위를 사용해 
AABB 때와 똑같이 값을 제한해 줍니다.

- $P_{local}.x = \max(-e_x, \min(L_x, e_x))$    
- $P_{local}.y = \max(-e_y, \min(L_y, e_y))$
- $P_{local}.z = \max(-e_z, \min(L_z, e_z))$
    
로컬 공간 상에서의 구체 중심 $L$과 가장 가까운 점 $P_{local}$ 사이의 
**거리 제곱**을 구해 반지름 제곱($r^2$)보다 작으면 충돌입니다!

### 2. 예제 코드

앞의 AABB vs Sphere코드와 비교해 보면 Dot 연산을 통해 로컬 좌표로 변환하는
과정만 추가된 것을 볼 수 있다

``` cpp
#include <iostream>
#include <cmath>
#include <algorithm>

struct Vector3 {
    float x, y, z;
    Vector3 operator-(const Vector3& v) const 
    { 
        return {x - v.x, y - v.y, z - v.z}; 
    }
    
    float dot(const Vector3& v) const
    { 
        return x * v.x + y * v.y + z * v.z; 
    }
};

// 회전된 상자 (OBB) 구조체
struct OBB {
    Vector3 center;       // 상자의 월드 중심점
    Vector3 extents;      // 상자의 절반 크기 (가로, 세로, 높이의 절반)
    Vector3 axes[3];      // 상자의 회전 방향을 나타내는 3개의 축 (정규화 필수)
};

struct Sphere {
    Vector3 center;
    float radius;
};

// OBB와 Sphere 간의 Overlap 체크 함수
bool checkOverlapOBBSphere(const OBB& box, const Sphere& sphere) 
{
    // 1. 구체 중심에서 OBB 중심을 향하는 상대 변위 벡터 계산
    Vector3 V = sphere.center - box.center;

    // 로컬 공간에서 가장 가까운 점을 저장할 벡터
    Vector3 closestPointLocal = {0.0f, 0.0f, 0.0f};
    // 로컬 공간에서의 구체 중심 좌표를 저장할 벡터
    Vector3 sphereProj = {0.0f, 0.0f, 0.0f};

    // 2. OBB의 3개 축(X, Y, Z)에 대해 각각 투영 및 Clamping 진행
    // X축
    sphereProj.x = V.dot(box.axes[0]);
    closestPointLocal.x = std::max(-box.extents.x, 
                                  std::min(sphereProj.x, box.extents.x));

    // Y축
    sphereProj.y = V.dot(box.axes[1]);
    closestPointLocal.y = std::max(-box.extents.y, 
                                   std::min(sphereProj.y, box.extents.y));

    // Z축
    sphereProj.z = V.dot(box.axes[2]);
    closestPointLocal.z = std::max(-box.extents.z, 
                                    std::min(sphereProj.z, box.extents.z));

    // 3. 로컬 공간에서의 거리 제곱 계산
    float distanceSq = (closestPointLocal.x - sphereProj.x) * 
                       (closestPointLocal.x - sphereProj.x) +
                       (closestPointLocal.y - sphereProj.y) *
                       (closestPointLocal.y - sphereProj.y) +
                       (closestPointLocal.z - sphereProj.z) *
                       (closestPointLocal.z - sphereProj.z);

    // 반지름 제곱과 비교하여 결과 반환
    return distanceSq <= (sphere.radius * sphere.radius);
}

int main() 
{
    // 45도 회전된 상자 정의 예시 (단순화를 위해 축만 수동 정의)
    OBB box;
    box.center = {0.0f, 0.0f, 0.0f};
    box.extents = {1.0f, 1.0f, 1.0f}; // 2x2x2 크기의 상자
    box.axes[0] = {0.707f, 0.707f, 0.0f};  // X축이 45도 회전됨
    box.axes[1] = {-0.707f, 0.707f, 0.0f}; // Y축
    box.axes[2] = {0.0f, 0.0f, 1.0f};       // Z축

    // 약간 비껴간 위치에 있는 구체
    Sphere sphere = { {1.2f, 1.2f, 0.0f}, 0.5f };

    if (checkOverlapOBBSphere(box, sphere)) 
    {
        std::cout << "OBB와 구체가 충돌(Overlap) 상태입니다." << std::endl;
    } 
    else 
    {
        std::cout << "충돌하지 않았습니다." << std::endl;
    }

    return 0;
}

```

---

## C. AABB vs AABB

### 1. 원리

"두 상자가 겹치지 않는 경우"를 생각해보면 된다
<strong style="color:#ffb15b">x,y,z 축 단 하나라도 서로 공간이 떠 있다면(분리) 2 상자는 서로 만날수 없다</strong>

하나의 축(예: X축)에서 상자 A와 상자 B가 겹치려면 다음 두 조건이 **동시에** 만족해야 합니다.

1. A의 최소 좌표가 B의 최대 좌표보다 작거나 같아야 함 ($A.min \le B.max$)    
2. A의 최대 좌표가 B의 최소 좌표보다 크거나 같아야 함 ($A.max \ge B.min$)
    
이 조건이 X, Y, Z축 모두에서 만족하면 두 AABB는 Overlap 상태입니다.

### 2. 예제 코드

``` cpp
#include <iostream>

struct Vector3 {
    float x, y, z;
};

// AABB 구조체 (최솟값점과 최댓값점으로 정의)
struct AABB {
    Vector3 min;
    Vector3 max;
};

// AABB vs AABB Overlap 체크 함수
bool checkOverlapAABBAABB(const AABB& a, const AABB& b) {
    // X축 검사: 한 상자의 min이 다른 상자의 max보다 크면 절대 겹칠 수 없음
    if (a.min.x > b.max.x || a.max.x < b.min.x) return false;

    // Y축 검사
    if (a.min.y > b.max.y || a.max.y < b.min.y) return false;

    // Z축 검사
    if (a.min.z > b.max.z || a.max.z < b.min.z) return false;

    // 세 축 모두에서 겹쳤다면 충돌 상태임
    return true;
}

int main() {
    // 원점에 걸쳐 있는 상자 A (크기: 2x2x2)
    AABB boxA = { {-1.0f, -1.0f, -1.0f}, {1.0f, 1.0f, 1.0f} };

    // 살짝 겹쳐 있는 상자 B
    AABB boxB = { {0.5f, 0.5f, 0.5f}, {2.5f, 2.5f, 2.5f} };

    if (checkOverlapAABBAABB(boxA, boxB)) {
        std::cout << "두 AABB 상자가 오버랩(충돌)되었습니다." << std::endl;
    } else {
        std::cout << "충돌하지 않았습니다." << std::endl;
    }

    return 0;
}

```



> [!info] AABB vs AABB 활용
> AABB vs AABB는 연산이 가벼워 게임 엔진에서 "예선전" 개념으로 직접적인
> 충돌 검사를 하기 전에 이검사를 먼저 진행한다
> 
> 1. 캐릭터나 복잡한 물체들은 감싸는 커다란 공통 AABB ㄱ생성
> 2. 물체끼리 부딪혔는지 검사를 AABB vs AABB 활용
> 3. 여기서 false 가 나면 내부의 복잡한 폴리곤 연산을 통째로 skip (Early Out)


---
## D. OBB vs OBB

OOBB (Object Bounding Box) 

![[algo_collision_OBB_example.webp]]

- AABB : 항상 x,y,z 측에 정렬 -> 회전하면 box의 사이즈가 커짐
- OBB : 오브젝트와 함께 회전 -> 항상 딱 맞는 박스 유지

### 1. 구성 요소

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

### 2. 예제 코드

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


### 3. 실전 코드

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

