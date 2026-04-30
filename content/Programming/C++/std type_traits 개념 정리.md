---
title: std::type_traits 개념 정리
author: KurtJang
tags:
  - Blog
  - "#Programming"
  - "#CPP"
  - "#STL"
date: 2026-05-01
draft: "False"
---

> [!NOTE] 
> C++ STL type_traits 개념 정리 (C++ 11)

---
<font color="#b3f594"><strong>Table of Contents</strong> </font>

- [Code Example](#code-example)
- [Callout Example](#callout-example)


- [is_convertible](#is_convertible)
	- [1. 파라미터](#1-%ED%8C%8C%EB%9D%BC%EB%AF%B8%ED%84%B0)
	- [2. 예제 코드](#2-%EC%98%88%EC%A0%9C-%EC%BD%94%EB%93%9C)
- [enable_if](#enable_if)
	- [1. 파라미터](#1-%ED%8C%8C%EB%9D%BC%EB%AF%B8%ED%84%B0)
	- [2. 예제 코드](#2-%EC%98%88%EC%A0%9C-%EC%BD%94%EB%93%9C)
	- [3. 실제 코드](#3-%EC%8B%A4%EC%A0%9C-%EC%BD%94%EB%93%9C)
	- [3. 실제 코드](#3-%EC%8B%A4%EC%A0%9C-%EC%BD%94%EB%93%9C)
- [Code Example](#code-example)
- [Callout Example](#callout-example)


---

# is_convertible

- <font color="#b3f594">핵심 정의 </font> : 탸입 `from` 에서 타입 `to` 로 암시적 변환(implicit conversion)이 가능한지
             컴파일 타임에 검사하는 type trait 입니다.
             
- <font color="#b3f594">작동 원리 </font> : `std::is_convertible<From, To>::value` 의 경우 변환이 가능하면 `true` , 
             불가능 하면 `false` 를 반환한다
             
- <font color="#b3f594">주요 용도 </font> : 상속 관계확인 "자식 포인터를 부모포인터로 바꿀수 있는가" 이나 함수 전달가능
             여부를 체크할 때 사용 합니다.

## 1. 파라미터

- `From` : 원본 타입
- `To` : 변환하고자 하는 대상 타입
- `value` : 변환 가능 여부를 담은 `static constexpr bool` 값

## 2. 예제 코드

``` cpp
#include<iostream>
#include <type_traits>

struct Base
{};

struct Derived : publid Base
{};

struct Random{};

int main
{
	//1. 상속 관계 변환 체크
	bool b1 = std::is_convertible_v<Derived*, Base*>;
	//결과 : true (자식 포인터는 부모 포인터로 암시적 변환 가능)
	
	//2. 상관 없는 타입 변환 체크
	bool b2 = std::is_convertible_v<Random*, Base*>;
	//결과 : false (아무 관계없는 타입끼리는 변환 불가)
	
	//3. 기본 자료형 변환 체크
	bool b3 = std::is_convertible_v<int, double>
	//결과 : true (int는 double로 암시적 형변환 가능)
}

```

---
# enable_if


- <font color="#b3f594">핵심 정의 </font> : 특정 조건이 `true` 일때만 해당 템플릿 함수나 클래스 컴파일 대상에 포함시키는 
             도구 입니다.

- <font color="#b3f594">SFINAE 원칙 </font> : 조건이 거짓이라 템플릿 치환에 실패해도 에러를 내지 않고 그냥 "이 함수는 
               후보가 아니네" 하고 조용히 넘어가는 성질을 이용 합니다.

- <font color="#b3f594">중요 포인트 </font> : 함수 오버로딩 시 특정 타입들에 대해서만 함수르 열여주고 싶을때만 필수적입니다.

## 1. 파라미터

- `condition` : `true` 혹은 `false` 로 결정되는 컴파일 타입 조건
- `Type` : 조건이 `true` 일때 `std::enable_if<...>::type` 이 가질 타입 (생략 시 `void` )
 
## 2. 예제 코드

``` cpp
#include<iostream>
#include <type_traits>

//T가 정수형 (int, long 등)일 때만 이 함수가 컴파일에 포함됨
template<typename T>
typename std::enable_if<std::is_integral<T>::value, void>::type
check_type(T val)
{
	std::cout << "정수 입니다." << val <<std::endl;
}

//T가 실수형(float, double)일 때만 이 함수가 컴파일에 포함됨
template<typename T>
std::enable_if<std::is_floating_point_v<T>>   //C++14 스타일 (더 간결함)
check_type(T val)
{
	std::cout << "실수입니다." << val << std::endl;
}

int main()
{
	check_type(10);
	//성공 : 첫 번째 check_type 선택
	
	check_type(3.14);
	//성공 : 두 번째 check_type 선택
	
	//check_type("hello");
	//실패 : 컴파일 에러
	/* 1. "Hello"는 문자열 (const char*) 입니다.
	 * 2. 정수도 아니고 실수도 아니므로 두 템플릿 모두 조건이 false
	 * 3. 결국 호출할 수 있는 함수가 하나도 없어서 컴파일 에러 발생
	*/
}
```


## 3. 실제 코드

- `deleter` 변환 생성자 (위의 2개념의 결합)

```cpp
template<typename T>
struct deleter
{

//1. template<typename U> : 변환할 원본 타입을 방출
//2. std::is_convertible<U*, T*>::value : U*를 T*로 바꿀수 있는가 (상속관계)
//3. std::enable_if<..., int> =0 : 위 조건이 참일때만 이 생성자를 활성화 함
template<typename U, std::enable_if<std::is_convertible_v<U*,T*>, int> = 0>
deleter(const deleter<U>&)
{
	//주석 : 성공적으로 변환함
}

};

/*
	[상세 설명 및 시나리오]
	
	시나리오
	class Parent {};
	class Child : public Parent {}
	
	1. deleter<Child> d_child;
	2. deleter<Parent> d_parent = d_child;
	   
	[작동 과정]
	- d_parent를 만들때 변환 생성자를 호출 (U=Child, T=Parent)
    - is_convertible_v<Child*, Parent*>는 'true' 이다 (상속관계이므로)
    - enable_if 의 조건이 true가 되어 이 생성자가 컴파일에 포함됨
    - 결과적으로 deleter<Child>에서 deleter<Parent>로의 안전한 복사 실행
    - 만약 2 클래스가 상속관계가 아니라면 enable_if에 의해 이 생섣자가 '증발'하여
      잘못된 복사를 컴파일 단계에서 완전 봉쇄 합니다.
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