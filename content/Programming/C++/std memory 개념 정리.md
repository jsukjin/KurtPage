---
title: std::memory 개념 정리
author: KurtJang
tags:
  - Blog
  - "#Programming"
  - "#CPP"
  - "#STL"
date: 2026-04-30
draft: "False"
---

> [!NOTE] 
> std::memory 개념 정리

---
<font color="#b3f594"><strong>Table of Contents</strong></font>

- [Code Example](#code-example)
- [Callout Example](#callout-example)

- [1. pointer_traits](#1-pointer_traits)
	- [1. 개념 설명](#1-%EA%B0%9C%EB%85%90-%EC%84%A4%EB%AA%85)
	- [2. 예제 코드](#2-%EC%98%88%EC%A0%9C-%EC%BD%94%EB%93%9C)
	- [3. 실제 예제](#3-%EC%8B%A4%EC%A0%9C-%EC%98%88%EC%A0%9C)
- [2. allocator](#2-allocator)



---

# 1. pointer_traits

포인터 타입들(raw/smatrt pointer)에 대해 공통된 인터페이스 제공하는 유틸리티 템플릿
주로 라이브러리 제작자들이 "이 티압이 정확히 무엇을 가르키는지", "다른 타입을 가르키는 동일한 종류의 포인터로 어떻게 바꾸는지" 등을 알기 위해 사용

- `unique_ptr<T>`, `T*` 등 서로 구조가 다르지만 공통적으로 필요한 정보가 있다
- `pointer_traits` 는 이를 표준화된 이름으로 뽑아 낸다

## 1. 구성 요소

- `elementer_type` : 포인터가 가리키는 실제 데이터 타입(예 : `int*` 라면 `int` )
- `pointer_to(r)` : 참조값 r을 받아서 해당 pointer 타입으로 변환해주는 함수
- `rebind<U>` : 현재 포인터와 같은 방식을 사용하면서 가리키는 대상만 U 타입으로
              바꾸는 포인터를 생성 (예 : `MyPtr<int>` 를 `MyPtr<double>` 로 변환)
- `diffente_type` : 두 pointer 사이의 거리를 측정할 때 사용하는 숫자 타입
				  (배열의 한 요소와 다른 요소에 얼마나 떨어져 있는지 계산)

## 2. 예제 코드

``` cpp
#include<iostream>
#include<memory>
#include<type_traits>

int main()
{
	int value = 42;
	int* ptr = &value;
	
	//1.pointer : 해당 포인터 타입 자체를 의미함
	using PtrType = std::pointer_traits<int*>::pointer;
	
	//2.element_type : 포인터가 가리키는 대상의 타입(int)
	using ElementType = std::pointer_traits<int*>::element_type;
	
	//3.difference_type : 포인터 간의 거리를 나타내는 타입(보통 ptrdiff_t)
	using DiffType = std::pointer_traits<int*>::difference_type;
	
	//4.rebind<U> : 포인터 종류는 유지하되 가리키는 대상만 변경 (int* -> dobule*)
	using doublePtr = std::pointer_traits<int*>::rebind<double>;
	
	//5.pointer_to : 참조를 받아서 해당 포인터 타입으로 변환
	PtrType convertedPtr = std::pointer<int*>::pointer_to(value);
	
	//========= 실제 테스트 ================
	
	std::cout << "1. 같은 타입인가? (PtrType == int*)" << 
	std:is_same_v<Ptrtype, int*>> << std::endl;
	// 결과 : true
	
	std::cout << "2. 가리키는 타입 크기" << sizeof(ElementType) << std::endl;
	//결과 : 4 
	
	std::cout <<"3.거리 타입 크기" << sizeof(DiffType) << std::endl
	//결과 : 8 (64비트 환경 기준 ptrdiff_t 크기)
	
	std::cout <<"4.Rebind 결과 double* 인가" 
	<< std::is_same_v<DoubleTpr, double*> << std::endl;
	//결과 :1 (true)
	
	std::cout << "5.pointer_to를 통해 얻은 값:" << *convertedPtr << std::endl;
	//결과 : 42 (위의 test value)
	
	return 0;
}
```

> [!info] info
> 1. `rebind<double>` : `int*` 를 `double*` 로 바꾸는 과정입니다. 만약 이게 스마트 포인터
>    `std::shared_ptr<int>` 였다면 결과는 `std::shared_ptr<double>` 이 됩니다.
> 2. `pointer_to` : 단순히 `&value` 를 하는것과 비슷해 보이지만 커스덤 포인터를 만들때는
>    이 함수가 해당 클래스에 맞게 변환 로직을 수행하게 됩니다.
> 3. `difference_type` : 두 포인터 사이의 메모리 간격(index 차이) 를 계산할때 사용하는
>    정수 타입 입니다.

## 3. 실제 코드

```cpp
// steam audio 예제 (memory_allocator.h)
using value_type = T;
using Reference = T&;
using const_reference = const T&;
using pointer = value_type*;

using const_pointer = typename std::pointer_traits<pointer>::template rebind<value_type const>;
using void_pointer = typename std::pointer_traits<pointer>::template rebind<void>;
using const_void_pointer = typename std::pointer_traits<pointer>::template rebind<const void>;
using difference_type = typename std::pointer_traits<pointer>::difference_type;
using size_type = std::make_unsigned_t<difference_type>;

```

> [!tip] 왜 `typename` 을 쓰나요?
> - `std::pointer_traits<pointer>::rebind<..>`  는 의존타입(dependent type) 
> - 컴파일러는 `pointer` 가 구체적으로 무엇인지 알기 전까지는 `rebind<...>` 가
>   타입(type) 인지 아니면 어떤값(static member) 인지 알 수 없다
> - C++ 규정상 템플릿 인자에 의존하는 이름이 "타입" 이라는 것을 명시하기 위해
>   `typename` 을 반드시 붙여야 한다 
>   (안붙이면 컴파일러는 이를 변수/함수 이름으로 오해하고 에러낼 수 있다)
>
  
> [!tip] 왜 `tempalte` 를 쓰나요?
> - `pointer_traits<pointer>` 내부에 있는 rebind는 그자체가 **"또다른 템플릿"**
> - 컴파일러가 코드를 읽을때 `<` 기호를 "작다(less than)"  라는 비교 연산자로 해석하지 않고
>   "아 이제부터 템플릿 인자가 시작되는구나!" 라고 올바르게 인식하게 하려면
>   `template` 키워드를 중간에 넣어줘야 한다
> - 이를 **"Template Disambiguator(템플릿 모호성 해소자)"** 라고 부른다

 
---
# 2. allocator

`std::allocator` 는 컨테이너(`vector` , `list` ) 가 메모리를 관리하는 방식을 정의하는 객체

- <font color="#b3f594">역할 분리</font>: 메모리의 할당(allocate) / 해제(deallocate)와 객체의 생성 (construct/destroy)
	         과정을 분리하여 제어 할 수 있게 된다
- <font color="#b3f594">성능 최적화 </font> : `new/delete` 대신 메모리 정렬(alignment)이나 pool 방식을 사용하여 데이터 
              처리 속도를 높인다.
- <font color="#b3f594">표준 규격</font> : `value_type` , `pointer`, `rebind ` 등의 인터페이스 표준에 맞춰 구현해야
              STL 컨테이너와 호환된다
              
## 1. 구성 요소

- `vlaue_type` : 할당자가 다루는 실제 데이터 타입 (`T` )
- `rebind<U>` : 할당자 대상 타입을 `T` 에서 `U` 로 변경하는 구조체
              (예 : `list` 내부 노드 할당시 필수)
- `allocate(n)` : `n * sizeof(T)` 크리만큼의 메모리 공간만 확보
- `deallocate(p, n)` : 확보했던 메모리 공간을 해제
- `construct(p, args)` : 할당된 공간에 `placement new` 를 사용하여 객체를 생성
- `destroy(p)` : 객체의 소멸자 (`~U()`) 를 직접 호출하여 객체만 파괴


## 2. 예제 코드


```cpp fold title:example

//1. 메모리만 할당 (땅 사기)
T* p = myAlloc.allocate(1);

//2. 해당 위치에 객체 생성 (건물 짓기)
myAlloc.construct(p, 42);

//3. 객체 소멸 (건물 부수기 - 메모리만 남음)
myAlloc.destroy(p);

//4. 메모리 해제 (땅 반납)
myAlloc.deallocate(p, 1);

```

## 3. 실제 코드

```cpp fold title:example

template<typename T>
class MyAudioAllocator 
{
public:
	using value_type = T;
	using pointer = T*;
	
	//pointer_traits를 이용한 타입변환 (const, void pointer)
	using const_pointer = typename std::pointer_traits<pointer>::template rebind<const, T>;
	using void_pointer = typename std::pointer_traits<pointer>::template rebind<void>;
	
	//컨테이너가 다른 타입(예 : node)를 할당할 수 있게 해주는 re-bind
	template<typename T>
	struct rebind 
	{
		using other = MyAudioAllocator<U>;
	}
	
	//메모리 할당 (정렬 기준 적용)
	T* allocate(std::size_t n)
	{
		//예 : 16 바이트 정렬 기준
		size_t size = n * sizeof(T) * 16;
		return reinterpret_cast<T*>(gMemory().allocate(size));
	}
	
	//객체 파괴 (명시적 소멸자 호출)
	template<class U>
	void destroy(U* p) noexcept
	{
		p->~U();
	}
	
	//메모리 해체
	void deallocate(T* p, std:size_t n)
	{
		gMemory().free(p);
	}
}

```



