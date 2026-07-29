---
title: "[Core] MemoryAllocator"
author: KurtJang
tags:
  - Blog
  - "#Programming"
  - "#CPP"
  - "#SteamAudio"
date: 2026-06-15
draft: "False"
description: "[SteamAudio] memory_allocator"
---

---

# 1. Introduction

- steam audio의 custom memory system 
- C++ 표준 라이브러리 `std::vector`, `std::unique_ptr`, `std::shar_ptr`  가 내부적으로
  사용하는 <strong style="color:#b3f594">메모리 할당/해제 경로를 전부 제어</strong>
- 왜 필요한가?
	- 메모리 추적 - 프로파일 등에 활용
	- 정렬보장 - 64B 정렬이 되어 SIMD AVX 512 가능
	- 커스덤 풀 - 게임 , 오디오 엔진에서 한 단편화 방지용 풀 교체 가능
	- 플랫폼 대응 - 콘솔 등 malloc를 직접 못쓴느 환경에서 콜백으로 교체


---
# 2. 구성요소

### 2.1 Memory class

- IPL_CALLBACK - 플랫폼별 calling convention (__cdecl, __stdcall)
- init() - 콜백을 넘기지 않을 경우 `_aligned_malloc / _aligned_free` 사용
- `gMemory()` : 전역 변수 (메모리 클래스) / 싱글턴 패턴


## 2.2 STL allocator

- C+++ named requirement **Allocator** 를 완전히 구현한 템플릿 클래스
- STL이 내부적으로 메모리가 필요할 때 호출하는 인터페이스 모두 구현

- 타입 정의 블록
``` cpp
using pointer = value_type*;
using const_pointer = std::pointer_traits<pointer>::reinbd<value_type const>;
using void_pointer = std::pointet_traits<pointer>::rebind<void>;

```

### rebind struct 

- `std::pointer_traits::rebind` 를 써서 `void*` 를 직접 안쓰고 유도 fancy pointer
  (스마트 포인터 기반 allocator) 와 호환성이 생기지만 raw_pointer 환경에서는
  사실상 `void*` 와 동일

``` cpp
template <class U>
struct rebind {typedef allocator<U> other};

//내부적으로 allocator<Node<T>> 필요
std::list<T> 

//내부적으로 allocator<pair<const k,V> 필요
std::map<K,V>
```


### allocate / deallocate

``` cpp
T* allocate(size_t n)
{
    return reinterpret_cast<T*>(
        gMemory().allocate(n * sizeof(T), Memory::kDefaultAlignment);
    )
}

void deallocate(T* p, size_t num)
{
    gMemory().free(p); //num 무시
}
```

### construct / destroy

- construct -  `new` 이미 할당된 메모리에 생성자만 호출
- `void* p` 캐스팅 -  `T*`  그대로 쓰면 의도치 않은 `new`  오버로드 선택 가능 
- destroy - 소멸자만 호출, 메모리 해제 X 
  (deallocate에서 따로 처리)

``` cpp
template <class U, class... Args>
void construct (U* p , Args&&... args)
{
    new ((void*) p) U (std::forward<Args>(args)...);
}

template <class U>
void destroy(U* p) noexcept
{
    p->~U();
}
```

### propagate policy

- `propagate_on_copy` - 컨테이너 복사시 allocator 복사 안함
- `propgate_on_move` - 컨테이너 이동시 allocator 이동 안함
- `propagate_on_swap` - swap시 allocator 교환 안됨
- `is_always_equal` - 모든 인스턴스가 동일 -> STL 비교 최적화
  allocator에 멤버 변수가 없으면 `is_empty = true_type` STL이 불필요한
  allocator 비교를 건너뜀 -> 컨테이너 이동 / 스왑 최적화

``` cpp
using propagate_on_container_copy_assignment = std::false_type;
using propagate_on_container_move_assignmnet = std::false_type;
using propagate_on_container_swap            = std::false_type;
using is_always_equal                        = std::is_empty<allocator>;

```


### operator == / !=

- 타입이 달라도`T1 != T2` 동일 풀 -> 항상 `true`
- STL은 두 컨테이너가 같은 `allocator`를 쓰는지 확인해 
  원소를 재할당 없이 이동할 수 있는지 판단함


## 2.3 Deleter 

``` cpp
template <typename T>
strcut Deleter
{
    template<typename U, std::enable_if<std::is_convertible<U*, T*>::value, int> =0>
    Deleter (const Deleter<U>&) {}
    
    void operator()(T* p) const
    {
        p->~T();
        gMemory().free(p);
    }
}
```

- `delete p` 를 쓰면 안되는 이유?
``` cpp
delete p = p->~T(); // OK
::operator delete (p) // system에서 heap으로 해체-> memory pool 오염
```

``` cpp
template <typename U, enable_if<is_convertible<U*,T*>::vlaue, int >= 0->
Deleter (const Deleter<U>&) {}

//is_convertible<U*,T*> : U*가 T*로 암시적 변환 가능한 경우만 활성화
//int = 0  : default 파라미터, 호출 시 명시 불필요 (SFINAE 관용구)
//결과 : unique_ptr<Base>가 unique_ptr<Derived>를 받을 수 있게 된다
```


### 2.4 Deleter<T[]>

- `new T[N]` - 컴파일러가 숨겨진 헤더에 N 저장
- 왜 `(&p[i])->~U()` 인가 ?
	- `p[i].~U()` - 는 문법오류 (임시값에 소멸자 호출)
	- `(&p[i])` - 로 주소를 취한 후 포인터 소멸자 호출 구문 사용

---

# 3. 예제 코드

``` cpp
// vectdor 에 allocator 적용
//push_back, resize 등 내부 할당이 모두 gMemory()로 라우팅
ipl::Vector<float> samples 
// std::vector<float, ipl::allocator<float>>
//samples.resize(1024);
//samples.push_back(0.5f)

//map에도 동일하게 적용
ipl::map<std::string ,int> index;
index["kick"] = 0;
index["snare"] = 1;

// make_uqniue - 단일 객체
//ipl::unique_ptr<AudioEffect> 반환
//스코프 종료 시 : p->~AudioEffect() + gMemory().free(p)
auto effect = ipl::make_unique<AudioEffect>(44100, 512);
effect->process(inputBuf, outputBuf);
//여기서 자동 해제

// make_unique - 배열
//float 1024 배열 생성
auto buf = ipl:::make_unique<float[]>()1024);
buf[0] = 0.0f; // 접근

// audio effect - 배열
auto effects = ipl::make_unique<AudioEffect[]>(8);
for(int i = 0; i < 8; ++i)
{
    effects[i].process(inputBuf, outputBuf);
    //소멸 시 for i = 0..7 
}

// make_shared - 공유 소유권
//[제어블록 + IRBuffer] 단일 할당
auto ir1 = ipl::make_shared<IRBuffer>(2, 1024);
auto ir2 = ir1; //ref_count = 2;
//ir1, ir2 둘다 소멸 후 gMemory()로 해제

```


---

# 4. 실전 코드

``` cpp
template <typename T>
class Allocator
{
public:
	using value_type = T;
	using reference = T&;
	using const_reference = const T&;
	using pointer = value_type*;
	
	//const_pointer : T const* 와 동일
	//std::pointer_traits<T*>::rebind<T const> -> T const*
	using const_pointer = typename std::pointer_traits<pointer>::template
	rebind<value_type const>;
	
	//void_pointer / const_void_pointer : void* / const vod* 동일
	//allocatoe의 hint인자 타입으로 사용됨
	using void_pointer = typename std::pointer_traits<pointer>::template 
	rebind<void>;
	using const_void_pointer = typename std::pointer_traits<pointer>::template
	rebind<const void>;
	
	//difference_type : 포인터 간 차이를 나타내는 signed 정수, 보통 ptrdiff_t
	//std::pionter_traits 에서 자동 유도
	using difference_type = typename std::pointer_traits<pointer>::
	difference_type;
	
	//size_type : 원소 개수를 나타내는 unsigned 정수, 보통 size_t
	//difference_type(signed) 을 unsigned로 변환해서 얻는다
	//std::make_unsigned<ptrdiff_t> ==size_t
	using size_type = std::make_unsigned_t<difference_type>;
	
/*
 rebind
 
 STL 컨테이너가 내부적으로 다른 타입의 allocator가 필요할 때 사용
 eg)
 std::list<T>는 내부적으로 Node<T>를 할당해야 함
 allocator<T>에서 allocator<Node<T>>로 변환이 필요
 rebind<Node<T>>::other == allocator<Node<T>>
*/
template <class U>
struct rebind
{
    typedef allocator<U> other;
}   

allocator() onexcept {}

/*
 rebind 생성자 (변환 생성자)
 
 allocator<U>에서 allocator<T>로 변환할때 호출
 STL : 내부에서 rebind와 함께 사용됨
 
 eg)
 std::list<int>가 내부적으로 allocator<Node<int>>를 만들 때
 allocator<int>로부터 이 생성자를 통해 allocator<Node<int>> 생성
*/
template <class U>
allocator<const allocator<U>&) onexcept {}


/* allocate(n)

STL이 n개의 T를 저장할 메모리를 요청할 때 호출
n * szeof(float) 바이트를 64b 정렬로 할당해 반환

reinterpret_cast<T*> : void* -> T* 강제 변환
gMemory().allocate : void* 반환
static_cast는 void* -> T* 변환에 사용 가능하지만
Steam Audio는 reinterpret_cast를 관통적으로 사용

NOTE - memroy::kDefaultAlignment - 64 (AVX 512)
NOTE - STL은 실패 시 std::bad_alloc를 기대하지만
여기선 nullptr반환 시 STL이 접근 오류로 크래쉬 - 수정 필요
*/
T* allocatoe(size_t n)
{
	const size_t size = n * sizeof(float) * Memory::kDefaultAlignment;
    return reinterpret_cast<T*>(gMemory().allocate(size));
}


/* deallocate(p, num)

STL이 allocate()로 받느 포인터를 해제할 때 사용
num : STL이 allocate시 전달했던 n 을 그대로 돌려줌
      gMemory()가 내부적으로 블록 크기를 추적하므로 num은 무시
*/
void deallocator(T* p, size_t num)
{
    gMemory().free(p);
}


/* allocate(n, hint)- - hint 버전

두번째 인자 hint는 "이 근처 메모리를 선호한다" 는 힌트
대부분 구현에서 무시, 여기서도 int를 버리고 allocate(n) 위임
STL 인터페이스 요건 상 구현이 필요해서 만들어 둔 것
*/
value_type* allocate(std::size_t n, const_void_pointer)
{
   return allocate(n);
}

/* constrcut (p, args...)

allocate()로 확보된 메모리 p에 객체를 생성
placement new 사용 - 메모리 할당 없이 생성자만 호출

new ((void*)p) U(args...)

(void*)p : T* -> void* 캐스팅
           컴파일러가 T*로 받으면 의도치 않은 operator new 오버로드
           선택 가능성이 있음 -> void*로 강제해 포준 placement new 호출
U(std::forward<Args>(args)...) : 완벽전달 (perefect forwarding)
                                lValue-> lvalue, rvalue-> rValue 보존
*/
template<class U, class... Args>
void construct(U* p, Args&&... args)
{
    new ((void*) p) U(std::forward<Args>(args)...);
}

/* destroy(p)
객체의 소멸자만 호출, 메모리 해제는 하지 않음
deallocate()가 별도로 메모리르 해제한다

P->~U() : 소멸자 직접 호출 구문
          일반 함수처럼 명시적으로 소멸자만 실행
          메모리는 건드리지 않음

noexcept : 소멸자는 예외를 던지면 안된다
*/
template<class U>
void destroy(U* p) noexcept
{
    p->~U();
}

std::size_t max_size() const noexcept
{
    return std::numeric_limits<size_type>::max();
}


/* select_on_container_copy_construction

컨테이너 복사/이동/swap 시 allocator를 함께 전파할지 결정
3가지 경우 모두 false_type

propagate_on_container_copy_assignment = false
vec1 = vec2 시 vec1의 allocator를 vec2의 것으로 교체하지 않음

propagate_on_container_move_assignment = false
vec1 = move(vec2) 시 allocator 이름 없음

propagate_on_container_swap = false
swap(vec1, vec2) 시 allocator 교환 없음
*/
allocator select_on_container_copy_construction() const
{
    return *this;
}

using propagate_on_container_copy_assignment = std::false_type;
using propagate_on_container_move_assignment = std::false_type;
using propagate_on_container_swap - std::false_type;
using is_always_equal = stD::is_empty<allocator>;

};


/* Deleter
std::unique_ptr<T, deleter<T>> 호출시 소멸되는 커스덤 해제 자

왜 delete를 쓰면 안되는가?
- make_unique는 gMemory().allocate + placement new로 객체 생성
  
delete p 내부 동작
- p->~T() // 소멸자 호출
- ::operator delete(p) //시스템 힙(malloc/free)으로 해제 -> pol 오염

올바른 해제
- p->~T() // 소멸자만 호출
- gMemory().free(p) // 커스덤 풀로 반환
*/
template <typename T>
struct deleter
{
public:

deleter() = default;

/* 변환 생성자 (SFINAE)

deleter<U>에서 deleter<T>로 변환 허용
U*가 T*로 임시적 변환 가능한 경움에만 활성화

std::enable_if<condition, int> = 0
 - condition이 true 일때만 이 생성자가 존재
 - int = 0 은 기본값 파라미터로, 호출 시 명시 불필요
   
eg)
 ipl::unique_ptr<Base> p = ipl::make_unique<Dervied>();
 Derived* 에서 Base*로 변환 가능 
*/
template<typename U, 
         std::enable_if_t<std::is_convertible<U*,T*>::value, int> = 0>
deleter(const deleter<U>&){}

/* ioperator()(p)

unique_ptr 소멸 또는 reset()시 자동 호출

p->~T()
 - 소멸자 직접 호출, 메모리 해제 없음
 - placement new 로 생성했으므로 반드시 이 방식으로 소멸자 호출
   
gMemory().free(p)
 - 커스덤 풀로 메모리 반환
 - p->~T() 이후에 호출해야 함(소멸자 실행 중엔 메모리 유효해야 함)
*/
void operator()(T* p) const
{
    p->~T();
    gMemory().free(p);
}
};

/* deleter<T[]> - unique_ptr 배열 특수화

std::unique_ptr<T[], deleterT[]>>소멸 시 호출

왜 N을 저장하는가?
 - new T[N]의 경우 컴파일러가 숨겨진 헤더에 N을 저장
 - placement new 배열은 N을 사용 안함(delete[] 는 사용)
 - deleter 안에 N를 직접 저장해 loop 소멸자 호출에 사용
*/
template <typename T>
struct deleter<T[]>
{
public:

/* 배열 원소, 개수 make_unique<T[]>(size) 가 생성 시 전달
 기본값 1 - 의도적으로 최소값으로 초기화 (0이면 루프 미실행)
*/
size_t N = 1;

deleter() = default;

//배열 크기를 받는 생성자. make_unique 배열 버전이 size를 전달
deleter(size_t N) : N(N) {}


/* 배열 변환 생성자 (SFINAE)

deleter<U[]> 에서 deleter<T[]>로 반환
U(*)[] 가 T(*)[]로 변환 가능한 경우에만 활성화
(배열 포인터 공변성 - Derived() -> BAse[]는 C++에서 허용)


NOTE
 - N을 복사하지 않는 버그 있음
 - other.N을 받아서 올바른 구
*/
template <typename U,
      std::enable_if_t<std::is_convertible<U(*), T(*)[]::value, int> =0>
deleter(const deleter<U[]>&) {}


/* operator()(p)

1. 각 원소의 소멸자 루프로 개별 호출
2. 전체 배열 메모리를 한번에 free

(&p[i])->~U()
- p[i].~U() 는 문법 오류(임시값에 호출 불가)
- &p[i]로 i번째 원소의 주소를 취한 후 포인터 소멸자 호출
  
trivial 타입 (float, int) 최적화
- 소멸자가 no-op -> 컴파일러가 루프 전체 제거
- non-trivial 타입 (string, audio buffer 등) 은 루프 반드시 필요
      
gMemory().free(p)
- 루프 완료 후 전체 블록 한번에 반환
- 원소별로 free 하지 않음 - 배열 전체가 단일 블록으로 할당되어서
*/
template <typename U,
     std::enable_if_t<std::is_convertible<U(*)[], T(*)[]::value, int> =0>
void operator() (U* p) const
{
    for (int i = 0; i < N; ++i)
    {
        (&p[i])->~U();
        //1번째 원소 소멸자 호출
    }
    gMemory().free(p):
    //전체 배열 메모리 반환
}
};

/* unique_ptr<T> alias

std::unique_ptr 의 2번째 템플릿 인자 (Deleter)에 ipl::deleter<T> 주입
ipl::unique_ptr<T>를 쓰면 자동으로 커스덤 deleter 사용

std::unique_ptr<T>     : deleter로 해제 (시스템 힙)
ipl::unique_ptr<T>     : dleeter<T>::operator() 로 해제
ipl::unique_ptr<T>의 크기 : sizeof(T*) * sizeof(deleter<T>)
                          포인터 +  empty 구조체 -> 포인터 크기와 동일
                          (EBO : empty base optimization 적용)
*/
template<typename T>
using unique_ptr = std::unique_ptr<T, deleter<T>>;


/* make_unique = 단일 객체 버전 (SFINAE : !is_Array)

!std::is_array<T?::value 조건
- T가 배열 타입이 아닐 때만 이 합수가 존재
- make_unique<float[]>(N) 처럼 배열로 호출하면 아래 벼일 버전이 선택 됨
  
*/
template<typename T, typename... Args>
typename std::enalbe_if<!std::is_array<T>::value, 
                         ipl::unique_ptr<T><::type
make_unique(Args&&... args)
{
   auto p = reinterpret_casT<T*>(
   gMemory().allocate(sizeof(T), Memory::kDefaultAlignment));
   
   new (P) T(std::forward<Args>(args)...);
   
   return ipl::unique_ptr<T>(p, deleter<T>());
}

/* make_uqniue = 배열 버전(SPINE : is_array && extent == 0)

std::is_array<T>::value && std::extent<T>::value == 0 조건
- T가 크기 미지정 배열일 때만 활성화

활성화
std::is_array<float[]> = true, std::enxtent<float[]> = 0

비활성화
std::is_array<float[5]> = true, std::extent<float[5]> = 5
std::is_array<float> = false

std::remove_extent<T>::type:
 - T = float[] -> E = float (배열 겉껍질 제거, 원소 타입 추축)
   
흐름
1. gMemory().allocate(size * sizeof(E), 64B) - 연속 메모리
2. for i : new (&p[i]) E{() - 각 원소 기본 생성
3. ipl::unique_ptr<T?(p, allocator<T>(size)) - N 저장 deleter
*/
template<typename T, typename ...Args>
typename std::enable_if<std::is_array<T>::value &&
                        std::extent<T>::value == 0,
                        ipl::unique_ptr<T>>::type
make_unique(size_t size)
{
    //E : 배열 원소 타입, float[] -> float
    typedef typename std::remove_extent<T>::type_t;
    
    //size 개 원소를 위한 연속 메모리 할당 (64B 정렬)
    size_t allocateSize = size * sizeof(float) * Memory::kDefaultAlignment;
    auto p = reinterpret_cast<E*>(allocateSize);
    
    //각 원소를 기본 생성자로 초기화
    //ou : unsigned 0 - i 와 size 타입 일치 (signed / unsigned 경고 방지)
    for (int i = 0u; i < size; ++i)
    {
        //i 번째 원소 위치에 placement new
        new(&p[i]) E();
    }
    
    //deleter<T>(sizse) : 소멸 시 루프 소멸자 호출에 size(=N) 필요
    return ipl::unique_ptr<T>(p, deleter<T>(size));
}

/* shared_ptr<T> alias

std::shared_ptr 는 그대로 사용
deleter를 커스덤할 피룡 없음 - allocate_shared가 allocator를 통해
제어블럭과 T 를 모두 커스덤 풀에서 할당하기 때문에
*/
template<typename T>
using shared_ptr = std::shared_ptr<T>;


/* make_shared

std::allocate_shared<T>(allocator, args...);
- 표준 라이브러리 함수 제공된 allocator로 [제어블록 + T]를 단일 할당
  
std::make_shqred 와 비교
- std::make_shqred<T>(args)
- new로 [제어블록 + T] 단일 할당 (시스템 힙)
  
ipl::make_shqred<T>(args)
- allocator<T>()로 [제어블록 + T] 단일 당 (gMemory())
  
둘 다 할당 1회 - 메모리 풀만 다름

shared_ptr<T>(new T(args)) 와 비교
- new T(args)   : T 할당 1회 (시스템 힙)
- 제어블록 내부 할당 : 제어블록 할당 1ㅠㅚ
- 총 2회 할당 - 캐시 비친화적

allocate_shared 장점
- 단일 할당, 캐시 친화적, 메모리 단편화 감소
*/
template<typename T, typename... Args>
std::shared_ptr<T> make_shared(Args&&... args)
{
   // allocator<T> : 임시 allocator 인스턴트 생성
   //allocate_shared 가 내부적으로 allocator.allocate() 를 호출해
   //[제어블록 + T]를 gMemory()에서 단일 할당
   return std::allocate_shared<T>(allocator<T>, std::forward<Args>(args)...);
}
```
