---
title: std::default_random_engine
author: KurtJang
tags:
  - Blog
date: 2026-05-22
draft: "False"
description: std::default_random_engine 정리
---

---

# 1. 핵심 요약

- c++ 표준 난수 생성기 
- 엔진(분포 없는 raw 비트 생성) 과 분포(distruction)를 분리하는 구조

---

## 2. 구성 요소

- ` std::default_random_engine` / `std::mt19937`
	- 난수 비트를 생성하는 엔진 `mt19937` 이 품질이 더 좋아서 실무에서 선호

- `seed`
	- 엔진 초기 상태, 같은 seed->항상 같은 수열 (재현성)
	- `std::random_device{}()` 로 하드웨어 시드 사용 가능

- `std::uniform_real_distribution<float>(min,max)`
	- 균등 분포 `[min,max]` 범위 실수

- `std::uniform_int_distribution<int>(min,max)`
	- 균등 분포 `[min,max]` 범위 정수

- `std::normal_distribution<float>(mean,stddev)`
	- 정규 가우시안 분포

- `operator()(engine)`
	- 분포 객체에 엔진을 넘겨 샘플 하나를 뽑음

---

# 3. 예제 코드

``` cpp
#include <random>

std::mt19937 rng(42);    //seed=42 고정
std::uniform_real_distribution<float> dist(0.0f, 1.0f); //[0,1] 정규분포

float v = dist(rng); //난수 샘플 하나

//하드웨어 시드 (매 실행마다 다른 수열)
std::mt19937 rng2(std::random_device{}());
```

---

# 4. 실전 코드


``` cpp
//Steam Audio Reflection Simulator에서 레이 방향을 무작위로 샘플링하는 패턴

#include <raondom>

class ReflectionSimulator
{
public:
	ReflectionSimulator(int numRays, int numThreads)
	    : mRngEngine(numThreads)
	    , mDist(0.0f, 1.0f)
	{
	    for (int i = 0; i < numThreads; ++i)
	    {
	        //thread i 마다 다른 seed
	        mRngEngines[i].seed(i); 
	    }
	}
	
	void traceRays(int threadId, std::atomic<bool>& cancel)
	{
		std::mt19937& rng = mRngEngines[threadId];
	
	    if (cancel) break;
	    
	    //균등 샘플링 -> 방위각 고도각을 [0.1] radian으로 변환
	    float u = mDist(rng);  //0.73f 값은값
	    float v = mDist(rng); // 0.21 같은 값
	    
	    float theta = 2.0f * kPI * u;  //방위각[0,2PI]
	    float phi = std::acos(1.0f - 2.0f * v); //고도각[0, PI]
	    
	    Vector3f dir = {
	        std::sin(phi) * std::cos(theta), //x
	        std::sin(phi) * std::sin(theta), //y
	        std::cos(phi)
	    };
	    
	    castRay(dir)
	}

private:
    std::vector<std::mt19937> mRngEngines;   //[threadId] 인덱스 접근
    std::uniform_real_distribution<float> mDist; 
    int mNumRaysPerThread = 1024;

};

```

