---
title: Collision algorithm
author: KurtJang
tags:
  - Blog
  - "#Programming"
  - CPP
  - "#Algorithm"
date: 2026-05-19
draft: "True"
description: collision 관련 algorithm 분석
---

---

# 1. AABB

- ray가 AABB 박스에 닿는지 확인하는 알고리즘
- 슬랩(Slab)은 두 평행 평면 사이의 공간이며 X,Y,Z 3쌍의 슬랩으루 구성됨


![[algo_collision_AABB.webp]]

- `tMin < tMax` 이면 교차
- `tMin`(노란점) = 박스 진입, `tMax`(초록점) = 박스 탈출
- ray(파란색)은 `tMin` > `tMax` 이므로 구간 겹침 없음 

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

# 2. Triangle

- Ray Triangle 교차 테스트 (Möller–Trumbore 알고리즘)

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