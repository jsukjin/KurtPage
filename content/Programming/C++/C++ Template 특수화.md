---
title: C++ Template 부분특수화
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
<font color="#b3f594"><strong>Table of Contents</strong> </font>

%% create table of contents (옵션 없는거) 를 마지막에 사용해 주세요 %%

- [Code Example](#code-example)
- [Callout Example](#callout-example)

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