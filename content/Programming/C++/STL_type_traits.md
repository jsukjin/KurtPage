---
title: STL_type_traits
author: KurtJang
tags:
  - Blog
  - "#Programming"
  - "#CPP"
  - "#STL"
date: 2026-05-01
draft: "False"
description: std::type_traits 에 대한 내용 정리 (C++ 11)
---

---

# is_convertible
<br>

<font color="#9fffa3">1. 핵심 정의</font>

타입 'from' 에서 타입 to로 암시적 변환 (implicit conversion) 이 가능한지
컴파일 타임에 검사하는 type trait 입니다.

<font color="#9fffa3">2. 작동 원리</font>

`std::is_convertible<From,To>::value`  의 경우 변환이 가능하면 `true`
변환이 불가능하면 `false` 를 반환 합니다.


<font color="#9fffa3">3. 주요 용도</font>

상속 관계확인이나 함수 전달 가능 여부를 체크할 때 사용 합니다.
<br>

## 1. 파라미터

- `From` : 원본 타입
- `To` : 변환하고자 하는 대상 타입
- `value` : 변환 가능 여부를 담은 `static constexpr bool` 값

<br>

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
<br>

# enable_if
<br>

<font color="#9fffa3">1. 핵심 정의</font>

특정 조건이 `true` 일때만 해당 템플릿 함수나 클래스 컴파일 대상에 포함시키는 도구


<font color="#9fffa3">2. SFINAE 원칙</font>

조건이 거짓이라 템플릿 치환에 실패해도 에러를 내지 않고 그냥 "이 함수는 후보가 아니네"
하고 조용히 넘어가는 성질을 이용 합니다.

<font color="#9fffa3">3. 중요 포인트</font>

함수 오버로딩 시 특정 타입들에 대해서만 함수로 열어주고 싶을 때 필수적 사용
<br>

## 1. 파라미터

- `condition` : `true` 혹은 `false` 로 결정되는 컴파일 타입 조건
- `Type` : 조건이 `true` 일때 `std::enable_if<...>::type` 이 가질 타입 (생략 시 `void` )

<br>

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
<br>

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

# 3. extent
<br>

<font color="#9fffa3">1. 핵심 정의</font>

타입 `T`  가 배열일때 , 지정한 차원의 요소 개수를 상수로 변환

<font color="#9fffa3">2. 작동 원리</font>

`int[10]` 이라면 `10` 을 `int[10][20]` 에서 1번째 차원을 물으면 `20` 반환

<font color="#9fffa3">3. 차원 지정</font>

2번째 템플릿 인자로 숫자를 넘겨 몇번째 대괄호의 크기를 측정할지 결정 한다

<font color="#9fffa3">4. 중요 포인트</font>

배열이 아니거나, 크기가 명시되지 않은 배열은 해당 차원의 크기를 물으면 `0` 반환

<br>

## 1. 파라미터

- `T` : 검사할 타입
- `N` : 몇번째 차원 (기본값 0 = 첫번째 차원)
- `::value` : 해당 차원의 크기 반환 (크기를 알수 없으면 0)

<br>

## 2. 예제 코드

``` cpp

std::extent<int[4]>::value;        //4
std::extent<int[4][3]>::value;     //4 (첫번째 차원)
std::extent<int[4][3],1>::value;   //3 (두번째 차원)

std::extent<int[]>::value;         //0 
std::extent<int>::vlaue;           //0 (배열 아님)
```
<br>

## 3. 실제 코드
``` cpp

template <typename T>
typename std::enable_if<std::is_array<T>::value &&
						std::extent<T>::value == 0, //here
						ipl::unique_ptr<T>::type
make_unique(size_t size)
{

}

// 왜 extent == 0을 체크할까요?

//크기 미지정 배열[] 은 0 이므로 make_unique가 가능
ipl::make_unique<float[]>(4);

// 크기 지정배열 float[4] 는 4이므로 make_uniuqe 막음
ipl::make_unique<float>[4]();
```

---
<br>

# 4. remove_extent

- 배열 타입에서 배열 껍데기를 벗겨내는 도구'

``` cpp
float[] -> float
int[4] -> int
float -> float (배열 아니면 그대로)
```

<br>

## 1. 구성 요소
- `T` : 변환할 타입
- `::type` : 배열 껍데기 벗긴 결과 타입

``` cpp
float[][] -> float[] // 한번만 벗김
float[] -> float     // 두번 벗김
```
<br>

## 2. 예제 코드

``` cpp

std::remove_extent<float[]>::type     //float
std::remove_extent<float[4]>::type    //float
std::remove_extent<float>[][]>::type  //float[] (한번만 벗김)
std::remove_extent<float>::type       //float 그대로
std::remove_extent<int[4]>::type      // int

```
<br>

## 3. 실제 코드

``` cpp

template <typename T>
make_unique(size_t size)
{
	//float[] -> float 으로 벗겨냄 (E = float)
	typedef typename std::remove_extent<T>::type E;	
	
	// E = float로 메모리 계산
	auto p = reinterpret_cast<E*>(gMemory().allocate (size * sizeof(E), ...));	
	
	//각 원소 생성
	for (auto i = 0; i < size; ++i)
	{
		/* (&p[i])는 배열의 시작 주소 
		*  *&p[0], &p[1] 등
		  
		  new (주소) 타입(인자)
		  float* p = reinterpret_cast<float*>(gMemory().allocate(...));
		
		  //생성자만 호출
		  new (p) float(1.0f);
		*/
		
		new (&p[i]) E(); //new float()
	}
	
	return ipl::unique_ptr<T>(p, deleter<T>(size));
}

```




