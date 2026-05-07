---
title: operator new 개념 정리
author: KurtJang
tags:
  - Blog
date: 2026-05-07
draft: "False"
---

> [!NOTE] 
> operator new , new[] 개념 정리

---
<font color="#b3f594"><strong>Table of Contents</strong> </font>

1. [new](#new)
	1. [1. 구성요소](#1.%20%EA%B5%AC%EC%84%B1%EC%9A%94%EC%86%8C)
	2. [2. 예제 코드](#2.%20%EC%98%88%EC%A0%9C%20%EC%BD%94%EB%93%9C)
	3. [3. 실제 코드](#3.%20%EC%8B%A4%EC%A0%9C%20%EC%BD%94%EB%93%9C)

---

# new 

- 런타임에 힙에서 메모리를 동적으로 


- <font color="#b3f594">핵심 정의</font> : 단순히 메모리 공간을 할당(allocate) 하는 역할만 하는 함수
             (생성자를 호출하지 않는다)
 - <font color="#b3f594">new 연산자의 차이</font>
	 - new 연산자 : `operator new` 를 호출해 메모리 할당-> 생성자 호출-> 포인터 반환
	 - operator new : 순수하게 `malloc` 처럼 바이트 단위로 메모리 덩어리를 가져옴

``` cpp
//스택 할당 - 크기 컴파일 타임 고정 
//함수가 끝나면 자동해제되며 크기 변경이 안된다
int arr[4];

//힙 할당 - 크기 런타임 결정
// 직접 해제해야 하며 런타임에 크리 결정 가능
int* arr = new int[size];
```

## 1. 구성요소

- 일반 new
	- `operator new()` : 메모리 할당
	-  생성자 호출

- delete
	- 소멸자 호출 -> 객체 정리
	- `operator delete()`  : 메모리 해제

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

## 3. 실제 코드

``` cpp
auto p = reinterpret_cast<T*>(gMemory().allocate(sizeof(T), kDefaultAlignment)); //operator new 역할

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


<font color="#ffa500">new 3가지 형태 비교</font>

|        | 일반 new                  | 배열 new[]                  | placement new            |
| ------ | ----------------------- | ------------------------- | ------------------------ |
| 메모리 할당 | <center>0</center>      | <center>0</center>        | <center>X</center>       |
| 생성자 호출 | <center>0</center>      | <center>0 (N 번)</center>  | <center>0</center>       |
| 해제 방법  | <center>delete</center> | <center>delete[]</center> | <center>직접 ~T()</center> |
| 메모리 해제 | <center>자동</center>     | <center>자동</center>       | <center>직접</center>      |
