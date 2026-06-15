---
title: keywords_new
author: KurtJang
tags:
  - Blog
date: 2026-05-07
draft: "False"
description: "operator new , new[] 에 대한 내용 정리"
---

---

# new 

런타임에 힙에서 메모리를 동적으로 할당 받는다 


<font color="#b3f594">1. 핵심 정의</font>

단순히 메모리 공간을 할당(allocate) 하는 역할만 하는 함수
(생성자를 호출하지 않는다)

<font color="#b3f594">2. new 연산자의 차이 </font>

new 연산자 : `operator new` 를 호출해 메모리 할당-> 생성자 호출-> 포인터 반환
operator new : 순수하게 `malloc` 처럼 바이트 단위로 메모리 덩어리를 가져옴

``` cpp
//스택 할당 - 크기 컴파일 타임 고정 
//함수가 끝나면 자동해제되며 크기 변경이 안된다
int arr[4];

//힙 할당 - 크기 런타임 결정
// 직접 해제해야 하며 런타임에 크리 결정 가능
int* arr = new int[size];
```
<br>

## 1. 구성요소

<font color="#b3f594">new (일반) </font>
- `operator new()` : 메모리 할당
- 생성자 호출

<font color="#b3f594">delete  </font>

- 소멸자 호출 -> 객체 정리
- `operator delete()`  : 메모리 해제

<br>

## 2. 예제 코드

``` cpp

float* p = new float (1.0f);
delete p;

float *arr = new float[4];
delete[] arr;

//placement new - 이미 있는 메모리에 생성자만 호출

// 메모리 할당 없음
// buffer 위치에 생성자만 호출
alignas(float) char buffer [sizeof(float)];
float* p = new (buffer) float(1.0f);

// 소멸자 직접 호출
// delete를 쓰면 안됨 (buffer는 내가 관리하는 메모리)
p->float();

```
<br>

## 3. 실제 코드

``` cpp
//operator new 역할
auto p = reinterpret_cast<T*>(gMemory().allocate(sizeof(T), kDefaultAlignment)); 

//생성자만 호출 한 형태 (메모리는 p 사용)
new (p) T(std::forwared<Args>(args) ...);

auto p = reinterpret_cast<E*>(gMemory().allocate(sizeof(E), kDefaultAlignment);

for (auto i = 0u; i < size; ++i)
{
	new (&p[i]) E();
}

p->~T();            //deleter에서 소멸 (소멸자만 호출)
gMemory().free(p);  //deleter에서 소멸 (메모리만 해제)

```
<br>

## 4. 비교

|        | 일반 new                  | 배열 new[]                  | placement new            |
| ------ | ----------------------- | ------------------------- | ------------------------ |
| 메모리 할당 | <center>0</center>      | <center>0</center>        | <center>X</center>       |
| 생성자 호출 | <center>0</center>      | <center>0 (N 번)</center>  | <center>0</center>       |
| 해제 방법  | <center>delete</center> | <center>delete[]</center> | <center>직접 ~T()</center> |
| 메모리 해제 | <center>자동</center>     | <center>자동</center>       | <center>직접</center>      |

---

