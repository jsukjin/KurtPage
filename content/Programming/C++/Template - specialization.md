---
title: Template_Specialization
author: KurtJang
tags:
  - Blog
  - "#Programming"
  - "#CPP"
  - "#CPP_Template"
date: 2026-05-07
draft: "False"
---

> [!NOTE] 
> C++ Template 특수화 (Template specialization) / 부분특수화 (Partial Specialization) 개념 정리

---
<strong><font color="#9fffa3">Table of Contents</font></strong>

1. [템플릿 특수화](#%ED%85%9C%ED%94%8C%EB%A6%BF%20%ED%8A%B9%EC%88%98%ED%99%94)
	1. [1. 사용이유](#1.%20%EC%82%AC%EC%9A%A9%EC%9D%B4%EC%9C%A0)
	2. [2. 예제 코드](#2.%20%EC%98%88%EC%A0%9C%20%EC%BD%94%EB%93%9C)
	3. [2. 실제 코드](#2.%20%EC%8B%A4%EC%A0%9C%20%EC%BD%94%EB%93%9C)

%% create table of contents (옵션 없는거) 를 마지막에 사용해 주세요 %%

---

# 템플릿 특수화

## 1. 사용이유

왜 사용하는가? - 같은 템플릿인데 특정 타입일때는 다르게 동작하기 위해서

예제 코드
```cpp
template <typename T>
strcut deleter
{
	void operator()(T* p) 
	{
	    p->~T();    //단일객체 -> 소멸자 1번
	    free(p);
	}
}

```
- 단일객체에서는 소멸자 1번으로 가능하지만 만약 배열이라면?
	- 소멸자를 N 번 호출해야 함
	- 같은 코드로 처리 불가 따라서 <font color="#ffa500">템플릿 특수화</font> 필요

> [!info] info
> 일반 템플릿 : 모든 타입에 대한 기본 구현
> 완전 특수화 : 특정 타입 하나만 다르게
> 부분 특수화 : 특정 패턴 (포인터, 배열 등) 다르게
> <font color="#80dfff">우선 순위 : 완전 특수화 > 부분 특수화 > 일반 특수화</font>
> 


## 2. 예제 코드


<font color="#b3f594">예제코드 - 일반 템플릿</font>
```cpp
template <typename T>
struct Printer
{
	void print(T Value)
	{
	    printf("일반 %d\n", value);
	}
};
```


<font color="#b3f594">예제코드 - 완전 특수화(Template specialization)</font>
```cpp
template <>
struct Printer<float>
{
	void print(float value)
	{
	    printf("float 전용 : %f\n", value);
	}
};

//float 만 처리한다

```


<font color="#b3f594">예제코드 - 부분 특수화(Partial Specialization)</font>
``` cpp
// T는 자유이나 포인터여야 함
template <typename T>
struct Printer<T*>
{
	void print(T* value)
	{
	    printf("포인터 전용\n");
	}
};

//T는 자유이나 배열이여 함
template <typename T>
struct Printer<T[]>    
{
	void print(T* value)
	{
	    print("배열 전용\n");
	}
};
```

<font color="#b3f594">Result</font>
```cpp
//일반
Printer<int> p;
p.print(1);

//float 전용 - 완전 특수화
Printer<float> p;
p.print(1.0f);

//pointer 전용 - 부분 특수화
Printer<int*> p;
p.printer(ptr);

//배열 전용 - 부분 특수화
Printer<int[]> p;
p.print(arr);
```

## 2. 실제 코드

```cpp
//일반 - 단일 객체
template <typename T>
struct deleter
{
	void operator()(T* p)
	{
	    //소멸자 1번
	    p->~T();
	    gMemory().free(p);
	}
};

 //부분특수화 - 배열
 template <typename T>
 strcut delter<T[]>
 {
	 size_t N;    //원수개수 기억
	 
	 void operator() (T* p)
	 {
	     for (size_t i = 0; i < N; ++i)
	     {
	         (&p[i])->~T();    //소멸자 N번
	     }
		 
	     gMemory.free(p);
	 }
 };

```

<font color="#b3f594">실제코드(Steam Audio)</font>
```cpp
  template <typename U, std::enable_if_t<std::is_convertible<U(*)[], T(*)[]>::value, int> = 0>
  deleter(const deleter<U[]>&) {}

/*
* U(*)[] : U 배열을 가리키는 포인터 배열
* T(*)[] = T 배열을 가리키는 포인터 배열
* is_convertible<A,B> : A가 B로 변환 가능한지 검사
* ::value : 결과를 bool로 반환
* enable_if<조건, int> : 조건이 true 일때만 타입 생성
* = 0 : 기본값, 호출 시 명시 불필요
*/  
  
```


---

