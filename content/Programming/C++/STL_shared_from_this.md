---
title: STD_shared_from_this
author: KurtJang
tags:
  - Blog
  - "#Programming"
  - "#CPP"
  - "#STL"
date: 2026-05-16
draft: "False"
description: std::memory 정리
---

---

# 1. 개념
- `shared_ptr` 로 관리되는 객체가 자기 자신에 대한 `shraed_ptr` 을 안전하게
  반환해야 할때 상속하는 기반 class
- `this` 로 직접 `shareD_ptr` 을 만들면 referecne count가 분리되어 
  이중해제 (doucle free)가 발생한다

``` cpp
// count가 분리됨
struct foo 
{
    shared_ptr<Foo>getThis()
    {
        //기존 카운터와 별개 생성 -> crash
        reutnr shared_ptr<Foo>(this);
    }
}
```

---

# 2. 구성 요소
- `sahred_from_this`
	- `this` 를 기존 `shared_ptr` 과 같은 카운터를 공유하는 `shared_ptr` 로 반환
- `weak_from_this()` (C++17)
	- 같은 카운터를 공유하는 `weak_ptr` 반환
- 특이사항
	- 반드시 `shared_ptr` 로 먼저 생성된 객체에서만 호출 가능
	
``` cpp
auto obj = make_shared<MyObj>();  //이후에만 shared_from_this() 호출 가능
MyObj raw;
raw.shared_from_this();           //std::bad_weak_ptr 예외 발생
```

---
# 3. 예제 코드

``` cpp
strcut Node : public std::enable_shared_from_this<Node>
{
    shared_ptr<Node> getSelf()
    {
        return shared_from_this(); //기존 카운터 공유
    }
};

auto node = make_shared<Node>();
auto a = node->getSelf();
auto b = node->getSelf();
//셋 다 카운터 공유 - use_count == 3
```

---
# 4. 실전 코드
``` cpp
#include <memory

//context.h (Steam Audio)
class Context : public std::enable_shared_fromth
{
public:
    void scheduleWork();
    void registerCallback(std::function<void(shared_ptr<Context>)> cb);
};

//context.cpp 
void Context::registerCallback(std::vector<void>(shared_tpr<Context>)> cb)
{
    //this를 직접 넘기면 카운터 분리 -> double free 위험
    //shared_from_this()로 안전하게 카운터 공유
    cb(shared_from_this());
}

void Context:::scheduleWork()
{
    //weak_from_this() -> 객체가 소멸했을 때 안전하게 무시 가능
    //eg) thread가 Context 보다 오래 살아있을 경우
    auto weak = weak_from_this();
    
    threadpool.enqueue([weak]()
    {
        //lock() -> 아직 살아 있으면 shared_ptr 반환
        //소멸했으면 nullptr
        if (auto ctx = weak.lock())
        {
            ctx->doWork();
            //Context 살아있음 -> 작업 수행
        }
        //Context 이미 소멸 -> 아무것도 안함(no crash)
    });
}

```

> [!info] 사용 예제
> <strong><font color="#3498db">1. 비동기 callback 및 event handler</font></strong>
> - 비동기 작업 (네트워크, 타이머) 등을 수행할때 작업이 완료될 시점에 객체가 여전히
>   살아있음을 보장해야 합니다. `this` 를 lamda 캡쳐로 보내면 작업 실행전 객체가
>   파괴될 위험이 있지만 `shared_from_this` 를 넘기면 참조횟수가 증가하여 안전하게
>   수명을 연잘 할 수 있다
> - eg) `asio` 같은 네트워크 라이브러리에서 핸들러를 등록할 때 자주 사용 
>   <br>
> <strong><font color="#3498db">2. 관찰자(observer) 패턴 및 listener 등록</font></strong>
> - 객체가 자신을 다른 관리자나 컨테이너에 등록해야 할 때 사용 합니다.
> - 상황 : "내가 이 이벤트를 듣고 싶으니 나를 리스트에 추가해줘" 라고 요청할때
>   관리자가 나를 `shared_ptr` 로 들고 있게 하려면 `shared_from_this` 가 필요
>   <br>
> <strong><font color="#3498db">3. 연쇄적인 함수 호출 (Chaining)</font></strong>
> - 함수 반환값으로 자기 자신의 `shared_ptr` 을 돌려워, 호출부에서 계속해서
>   소유권을 유지하며 다음 동작을 이어가게 하고 싶을 때 유용
