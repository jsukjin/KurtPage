---
title: std::condition_variable 정리
author: KurtJang
tags:
  - Blog
date: 2026-05-22
draft: "False"
description: std::condition_variable 정리
---

---

# 1. 핵심 요약

`std::condition_variable` 은 멀티 스레딩 환경에서 특정조건이 만족될때 까지
thread 수면(sleep) 상태로 대기 시키고 다른 스레드가 조건을 만족시키면 깨워주는
역할을 하는 <font color="#b3f594">동기화 객체</font>

<strong style="color:#b3f594">1. 효율성</strong>
- 조건이 충죽될때까지 CPU를 점유하며 무한반복 하는 대신 
  스레드를 잠재워 CPU 지원 낭비를 막는다

<strong style="color:#b3f594">2. 필수 요소</strong>
- 공유 데이터 보호를 위해 반드시 `std::mutex` 및 `std::unique_lockstd::mutex` 
  함께 사용 된다

<strong style="color:#b3f594">3.가짜 기상(wakeup)</strong>
- 운영체제 특성상 신호 없이도 thread가 깨어날 수 있으므로 대기할때 반드시
  조건검사 (Predicate)를 함께 전달해야 한다


---

# 2. 구성 요소

- `wait(lock, pred)
	- pred(조건 람다 함수)가 true 될때 스thread를 대기 시킨다
	- 깨어나면 lock을 해제하고 깨어날 때 다시 lock을 획득한다

- `notify_one`
	- 대기 중인 thread 중 하나의 thread만 깨워 작업을 재개한다

- `notify_all`
	- 대기 중인 모든 thread를 동시에 깨운다 (방송형 신호)

- `wait_for(lokc, time, pred)`
	- 조건이 만족되거나 특정 시간 간격이 이 경과 댈때까지 대기한다

- `wait_until(lock, time, pred)`
	- 조건이 만족 되거나 특정 시점이 될때까지 대기 한다


---

# 3. 예제 코드

``` cpp
#include <iostream>
#include <thread>
#include <mutex>
#include <condition_variable>
#include <string>
#include <chrono>

std::mutex mtx;               //공유 데이터 보호를 위함 mutex
std::condition_variable cv;   //thread 동기화를 위한 조건 변수
std::string shread_data;     //공유 데이터
bool isReady = false;        //데이터 준비 완료 여부를 나타내는 플래그

void consumer()
{
    std::unique_lock<std::mutex> lock(mtx);
    
    std::cout <"[consumer] data waiting\n";
    
    //isReady가 true가 될때까지 (가짜 가상 방지를 위해 람다식 적용)
    //wait 호출시 lock이 자동으로 해제되고, thread는 수면 상태에 들어감
    cv.wait (lock, []{return isReady;})
    
    //cv가 깨어나고 isReady가 treu면 자동으로 lock을 다시 획득
    //그리고 해당 아래 코드를 실행
    std::cout <<"[comsumer] data processed" << shared_data << std::endl;
}

//데이터를 생성하는 생산자 thread
void producer()
{
	//데이터 준비 시간 시뮬레이션
    std::this_thread::sleep_for(std::chorono::seconds(2));
    
    {
        std::lock_guard<std::mutex> lock(mtx);
        shared_data = "hello contion variable!";
        isReady = true;
        std::cout <<"[producer] data is ready \n";
    }
    
    //대기 중인 스레드 하나를 채움
    cv_notify_one();
}

int main()
{
    std::thread t1(consumer);
    std::thread t2(producer);
    
    t1.join();
    t2.join();
    
    //1. 2개의 thread 실행
    //2. producer thread에는 2초 sleep 이 있어서 consumer 실행
    //3. condition_variable로 인해 wait
    //4. producer에서 isReady 변경
    //5. isRady가 변경됨에 따라 consumer에서 작업 진행
    //6. 종료
    
    //[consumer] data waiting
	//[producer] data is ready
	//[comsumer] data processed hello contion variable!
    
    return 0;
}



```


