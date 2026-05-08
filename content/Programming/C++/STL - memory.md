---
title: STL_memory
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
>  STL std::memory 에 대한 내용 정리

---
<strong><font color="#9fffa3">Table of Contents</font></strong>

1. [1. pointer_traits](#1.%20pointer_traits)
	1. [1. 구성 요소](#1.%20%EA%B5%AC%EC%84%B1%20%EC%9A%94%EC%86%8C)
	2. [2. 예제 코드](#2.%20%EC%98%88%EC%A0%9C%20%EC%BD%94%EB%93%9C)
	3. [3. 실제 코드](#3.%20%EC%8B%A4%EC%A0%9C%20%EC%BD%94%EB%93%9C)
2. [2. allocator](#2.%20allocator)
	1. [1. 구성 요소](#1.%20%EA%B5%AC%EC%84%B1%20%EC%9A%94%EC%86%8C)
	2. [2. 예제 코드](#2.%20%EC%98%88%EC%A0%9C%20%EC%BD%94%EB%93%9C)
	3. [3. 실제 코드](#3.%20%EC%8B%A4%EC%A0%9C%20%EC%BD%94%EB%93%9C)
3. [3. unique_ptr](#3.%20unique_ptr)
	1. [1. 구성 요소](#1.%20%EA%B5%AC%EC%84%B1%20%EC%9A%94%EC%86%8C)
	2. [2. 예제 코드](#2.%20%EC%98%88%EC%A0%9C%20%EC%BD%94%EB%93%9C)
	3. [3. 실제 코드](#3.%20%EC%8B%A4%EC%A0%9C%20%EC%BD%94%EB%93%9C)
4. [4. make_unique](#4.%20make_unique)
	1. [1. 예제 코드](#1.%20%EC%98%88%EC%A0%9C%20%EC%BD%94%EB%93%9C)
	2. [2. 실제 코드](#2.%20%EC%8B%A4%EC%A0%9C%20%EC%BD%94%EB%93%9C)



---
# 1. pointer_traits

포인터 타입들(raw/smatrt pointer)에 대해 공통된 인터페이스 제공하는 유틸리티 템플릿
주로 라이브러리 제작자들이 "이 타입이 정확히 무엇을 가르키는지", 
"다른 타입을 가르키는 동일한 종류의 포인터로 어떻게 바꾸는지"  등을 알기 위해 사용

- `unique_ptr<T>`, `T*` 등 서로 구조가 다르지만 공통적으로 필요한 정보가 있다
- `pointer_traits` 는 이를 표준화된 이름으로 뽑아 낸다
<br>
## 1. 구성 요소

`element_type`
- 포인터가 가리키는 실제 데이터 타입(예 : `int*` 라면 `int` )

`pointer_to(r)`
- 참조값 r을 받아서 해당 pointer 타입으로 변환해주는 함수

`rebind<U>`
- 현재 포인터와 같은 방식을 사용하면서 가리키는 대상만 U 타입으로 바꾸는 포인터를 생성  
-  (예 : `MyPtr<int>` 를 `MyPtr<double>` 로 변환)

`diffente_type`
- 두 pointer 사이의 거리를 측정할 때 사용하는 숫자 타입
- 배열의 한 요소와 다른 요소에 얼마나 떨어져 있는지 계산

<br>

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

<br>

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
<br>

# 2. allocator
<br>

`std::allocator` 는 컨테이너(`vector` , `list` ) 가 메모리를 관리하는 방식을 정의하는 객체

<font color="#b3f594">1. 역할 분리</font>

메모리의 할당(allocate) / 해제(deallocate)와 객체의 생성 (construct/destroy)
과정을 분리하여 제어 할 수 있게 된다


<font color="#b3f594">2. 성능 최적화</font>

`new/delete` 대신 메모리 정렬(alignment)이나 pool 방식을 사용하여 데이터 처리 속도를 높인다.


<font color="#b3f594">3. 표준 규격</font>

`value_type` , `pointer`, `rebind ` 등의 인터페이스 표준에 맞춰 구현해야 
STL 컨테이너와 호환된다
              
<br>

## 1. 구성 요소

`vlaue_type`
- 할당자가 다루는 실제 데이터 타입 (`T` )

`rebind<U>`
- 할당자 대상 타입을 `T` 에서 `U` 로 변경하는 구조체

	 (예 : `list` 내부 노드 할당시 필수)


`allocate(n)`
- `n * sizeof(T)` 크리만큼의 메모리 공간만 확보


`deallocate(p, n)`
- 확보했던 메모리 공간을 해제


`construct(p, args)`
- 할당된 공간에 `placement new` 를 사용하여 객체를 생성

`destroy(p)`
- 객체의 소멸자 (`~U()`) 를 직접 호출하여 객체만 파괴

<br>

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
<br>

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

---
<br>

# 3. unique_ptr
<br>

`std::unique_ptr`은 힙에 할당된 객체를 자동으로 해제해주는 <font color="#ffa500">스마트 포인터</font>


<font color="#b3f594">1. 핵심 정의</font>

객체의 생명 주기를 자도응로 관리하는 wrapper 클래스이며 
RAII (resource acquisition is initialization) 패턴을 기반으로 설계


<font color="#b3f594">2. 자원 해제 보장</font>

스마트 포인터 객체가 스코프를 벗어나 소멸될때 가리키던 메모리를
자동으로 delete하게 된다

<font color="#b3f594">3. 예외 안정성</font>

함수 실행 중 예외가 발생하여 중단되더라도, 스택에 쌓인 스마트 포인터의
소멸자가 호출되므로 메모리 누수 (memory leak)가 발생하지 않는다

<font color="#b3f594">4. 소유권 명시</font>

`std::unique_ptr` 은 나만 가질수 있음 `std::shared_ptr` 공유

<font color="#b3f594">5. 사용 이유</font>
```cpp
//문제 상황 - 수동 관리
float* p = new float (1.0f);

// 만약 중간에 문제가 발생하면?

delete p; //여기 도달하기 전에 끝난다 -> 메모리 누수
```

```cpp
//unique_ptr 사용
std::unique_ptr<float>p = std::make_unique<float>(1.0f);
// 스코프를 벗어나면 자동으로 delete 호출 따라서 예외가 발생해도 안전
```
<br>

## 1. 구성 요소

`std::unique_ptr<T, Deleter>`
- T : 관리할 객체 타입
- Deleter : 소멸 시 호출할 객체 - 기본값 : `std::default_deleter<T>`

특징
- 소유권 이전 : std::move로만 가능
- 복사 불가 : 소유권 명시
- 소멸 시 : Deleter::operator() 자동 호출

<br>

## 2. 예제 코드

```cpp

//단일 객체
std::unique_ptr<float> p1 = std::make_unique<float>(1.0f);
*p1 = 2.0f;
//스코프 끝 -> Deleter 자동 호출

//배열
std::uique_ptr<float[]> p2 = std::make_unique<float[]>(4);
p2[0] = 1.0f;
//스코프 끝 -> Deleter 자동 호출

//소유권 이전
std::unique_ptr<float> p3 = std::move(p1);
//이후 p1 = nullptr / p3 = p1이 가리키던 값


/*== Deleter ===*/
strcut MyDeleter
{
	void operator() (float* p)
	{
	    print("MyDeleter called \n");
	    delete p;
	}
}

std::unique_ptr<float, MyDeleter> p (new float (1.0f));
//소멸시 -> MyDeleter:operator() 호출

```
<br>


## 3. 실제 코드

```cpp

// step 1 : std::unique_ptr에 ipl::deleter 주입
template <typename T>
using unique_ptr = std::make_unique<T, deleter<T>>;
// ipl::deleter 사용

// step 2 : ipl::deleter 
template <typenamm T>
strcut deleter
{
	void operator()(T* p)
	{
	    P->~T();             //소멸자 직접 호출
	    gMemory().free(p);   //ipl 할당자로 해제
	}
};

// step 3 : 사용
ipl::unique_ptr<float> p = ipl::make_unique<float>(1.0f);

```

---
<br>

# 4. make_unique

- `std::unique_ptr` 을 안전하게 생성하는 헬퍼 함수


## 1. 예제 코드

```cpp

// 단일 객체
auto p1 = std::make_uqniue<float>(1.0f);
// new float (1.0f) + unique_ptr 래핑

// 배열
auto p2 = std::make_unique<float[]>(4);
// new float[4] + unique_tpr 래핑

// custom class
auto p3 = std::make_unique<Foo>(1,2,3);
// new Foo (1,2,3) + unique_tpr 래핑
```


## 2. 실제 코드
```cpp

//단일 객체
template <typename T, typename... Args>
typename std::enable_if<!std::is_array<T>::value,  //T 배열이 아닐때만 활성화
					    ipl::unique_ptr<T>>::type  // 반환 타입
make_unique(Arggs&&... args)
{
	//step 1 : gMemory로 메모리 할당
	auto p = reinterpret_cast<T*>
	(
	    gMemory().allocate(sizeof(T), DefaultAlignement);
	);

	//step 2 : placement new로 생성자 호출
	new (p) T(std::forward<Args>(args)...);
	
	//step 3 : deleter와 함께 unique_ptr 반환
	return ipl::unique_ptr<T>(p, deleter<T>());
}


//배열 
template <typename T>
typename std::enable_if<std::is_array<T>::value && 
					std::extent<T>::value == 0, // float[0] ok / float[4] fail
					ipl::unique_ptr<T>::type
make_unique(size_t Size)
{
    //float[] -> float으로 벗겨냄
    typedef typename std::remove_extent<T>::tyupe E;
    
    // Step 1: 전체 배열 한번에 할당
    auto P = reinterpret_cast<E*> (gMemory().alocate(size * sizeof(E), DefaultAlignement));
	
	// Step 2 : 각 원소마다 생성자 호출
	for (auto i = 0u; i < Size; ++i)
	{
	    new (&p[i]) E();
	}

	// Step 3 : size를 deleter에 전달
	return ipl::unique_ptr<T>(p, deleter<T>(size));
}						
```


---

# 5. shared_ptr
<br>

<font color="#b3f594">1. 핵심 정의</font>

하나의 자원을 여러 포인트가 공동으로 소유할 수 있게 해주는 스마트 포인터

<font color="#b3f594">2. 참조 횟수</font>

자원을 가리키는 `shared_ptr`가 몇개인지 내부적으로 기록한다 (0이 되면 소멸)

<font color="#b3f594">3. 중요</font>

`std::make_shared` 사용하면 메모리 할당 횟수를 줄여 성능과 예외 안전성 증가

<br>

## 1. 파라미터

- `T`  : 관리할 객체의 타입
- `use_count()` : 현재 해당 자원을 공유하고 있는 `shared_ptr` 의 개수를 반환
- `get()` : 내부의 실제 포인터 주소를 반환

<br>

## 2. 예제 코드

``` cpp
// shared_ptr - 소유자가 여러 명
std::shared_ptr<Foo> p1 = std::make_shared<Foo>();
std::shared_ptr<Foo> p2 = 1; // OK
// p1, p2 둘 다 소멸해야 Foo 해제
```

<br>

## 3. 실제 코드

``` cpp
template <typename T>
using shared_ptr = std::shared_ptr<T>;

template <typename T, typename... Args>
std::shared_ptr<T> make_shared<Args&&.... args)
{
    //allocate_shared = 커스덤 allocator로 shared_ptr 생성
    //allocator 는 gMemory()가 사용하는 allocator
    return std::allocate_shared<T>(allocator<T>(), args...); 
}

```

---

# 6. weak_ptr
<br>
<font color="#b3f594">1. 핵심 정의</font>

`shared_ptr` 가 관리하는 자원을 가리키지만 소유권은 갖지 않는 포인터

<font color="#b3f594">2. 참조횟수 영향 없음</font>
`weak_ptr` 이 아무리 많아도 `use_count` 는 올라가지 않음

<font color="#b3f594">3. 순환 참조 방지</font>

두 객체가 서로를 가리키는 `shared_ptr` 은 메모리가 영원히 해제되지 않는
문제점이 발생하는데 이를 해결하는 핵심 도구

<font color="#b3f594">4. 중요</font>

자원이 이미 해제되어 있을 수 있으므로 `lock()` 함수를 통해 `shared_ptr` 로 
변환해서 안전한지 확인 후 사용

<br>

## 1. 파라미터

- `expired()` : 가리키는 자원이 이미 해제되었는지 확인
- `lock()` : 자원이 살아있다면 `shared_ptr` 를 반환하고 죽었다면 `nullptr`  반환

<br>

## 2. 예제 코드

``` cpp
#include <memory>

int main()
{
	std::shared_ptr<int> s_ptr = std::make_shqred<int>(100);
	std::weak_ptr<int> w_ptr = s_ptr; //소유권 없이 관찰만 시작
	
	//사용전 확인 (lock())
	if (std::shared_ptr<int> locked_ptr = w_ptr.lock())
	{
	    std::cout << "resource 살아있음" << "\n";
	}
	
	//원본 해제
	s_ptr.reset();
	
	if (w_ptr.expired())
	{
	    std::cout << "resource 이미 해제됨 \n";
	} 
	
	/*
	 * w_ptr.lock()을 통해 안전하게 자원에 접근
	 * 원본이 reset 된 후 expired()는 true를 반환하여 안정성을 보장한다
     */
}

```

<br>

## 3. 실제 코드

``` cpp

struct Boss;

struct Minion
{
	//shared_ptr<Boss>라면 Minion / Boss 가 서로를 가르쳐 영원이 해제 안됨
	~Minion() { std::cout << "미니언 소멸 \n"; }
	std::weak_ptr<Boss> boss;
};

struct Boss
{
	~Boss() {std::cout << "보스 소멸 \n";}
	std::shared_ptr<Minion> minion;
};

void Battle()
{
	auto b = std::make_shared<Boss>();
	auto m = std::make_shared<Minion>();
	
	b->minion = m;
	m->boss = b;    //weak_ptr 이므로 참조 카운트가 올라가지 않음
}

```

---


