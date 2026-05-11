---
title: Managed Ak System
author: KurtJang
tags:
  - Blog
  - UE
  - Wwise
date: 2026-03-17
draft: "true"
description: "AkComponent optimization"
---
<font color="#68ff6e">Table of Contents</font>

- [Code Example](#code-example)
- [Callout Example](#callout-example)

1. [1. Introduction](#1.%20Introduction)
		1. [목적](#%EB%AA%A9%EC%A0%81)
2. [2. Problem Statement](#2.%20Problem%20Statement)
	1. [3. 시스템 아키텍처 (System Architecture)](#3.%20%EC%8B%9C%EC%8A%A4%ED%85%9C%20%EC%95%84%ED%82%A4%ED%85%8D%EC%B2%98%20(System%20Architecture))
	2. [3.1 설계 원칙](#3.1%20%EC%84%A4%EA%B3%84%20%EC%9B%90%EC%B9%99)
	3. [3.2 주요 기능 (Key features)](#3.2%20%EC%A3%BC%EC%9A%94%20%EA%B8%B0%EB%8A%A5%20(Key%20features))
	4. [1.2 멀티 플레이 환경에서의 성능 병목](#1.2%20%EB%A9%80%ED%8B%B0%20%ED%94%8C%EB%A0%88%EC%9D%B4%20%ED%99%98%EA%B2%BD%EC%97%90%EC%84%9C%EC%9D%98%20%EC%84%B1%EB%8A%A5%20%EB%B3%91%EB%AA%A9)
3. [3. System Architecture](#3.%20System%20Architecture)
4. [4. Implementation Details](#4.%20Implementation%20Details)
5. [5. Testing & Validation](#5.%20Testing%20&%20Validation)
6. [2. Ak system optimizaion plan](#2.%20Ak%20system%20optimizaion%20plan)
	1. [1. Modular Audio Service](#1.%20Modular%20Audio%20Service)
	2. [As-Is](#As-Is)
	3. [To-Be](#To-Be)
	4. [1. Shared RTPC Parameters](#1.%20Shared%20RTPC%20Parameters)
	5. [As-Is](#As-Is)
	6. [To-Be](#To-Be)
7. [Code Example](#Code%20Example)
8. [Callout Example](#Callout%20Example)
	1. [Gemini said](#Gemini%20said)
9. [📑 Managed AkComponent 기술 상세 설계서 (Draft)](#%F0%9F%93%91%20Managed%20AkComponent%20%EA%B8%B0%EC%88%A0%20%EC%83%81%EC%84%B8%20%EC%84%A4%EA%B3%84%EC%84%9C%20(Draft))
	1. [1. 개요 (Introduction)](#1.%20%EA%B0%9C%EC%9A%94%20(Introduction))
	2. [2. 현황 및 문제점 (Problem Statement)](#2.%20%ED%98%84%ED%99%A9%20%EB%B0%8F%20%EB%AC%B8%EC%A0%9C%EC%A0%90%20(Problem%20Statement))
	3. [3. 시스템 아키텍처 (System Architecture)](#3.%20%EC%8B%9C%EC%8A%A4%ED%85%9C%20%EC%95%84%ED%82%A4%ED%85%8D%EC%B2%98%20(System%20Architecture))
	4. [4. 구현 상세 (Implementation Details)](#4.%20%EA%B5%AC%ED%98%84%20%EC%83%81%EC%84%B8%20(Implementation%20Details))
		1. [**4.1. 모듈별 오디오 서비스 설정 (To-Be)**](#**4.1.%20%EB%AA%A8%EB%93%88%EB%B3%84%20%EC%98%A4%EB%94%94%EC%98%A4%20%EC%84%9C%EB%B9%84%EC%8A%A4%20%EC%84%A4%EC%A0%95%20(To-Be)**)
		2. [**4.2. 중앙 집중형 데이터 흐름 (Centralization)**](#**4.2.%20%EC%A4%91%EC%95%99%20%EC%A7%91%EC%A4%91%ED%98%95%20%EB%8D%B0%EC%9D%B4%ED%84%B0%20%ED%9D%90%EB%A6%84%20(Centralization)**)
	5. [5. 테스트 및 검증 (Testing & Validation)](#5.%20%ED%85%8C%EC%8A%A4%ED%8A%B8%20%EB%B0%8F%20%EA%B2%80%EC%A6%9D%20(Testing%20&%20Validation))


---

# 1. Introduction

## 목적

wwise의 Ak Component를 사용함에 환경에 따른 시스템적 문제가 따르고 있습니다.
예를 들어 
는 독립적인 연산 유닛으로 작동하여 객체가 많아 ㅈ

사용시에 발생하는 시스템적인 문제점을 가지고 있습니다.



RTPC 계산과 Component management를 통해 퍼포먼스 향상을 위한 시스템 구축

기존 Wwise AkComponent 시스템은 각 컴포넌트가 독립적인 연산 유닛으로 동작하여, 
객체가 많아질수록 CPU 부하가 선형적으로 증가하는 구조적 한계를 가지고 있습니다.

## 기대 효과

중앙 집중형 데이터 공유 및 컴포넌트 재활용을 통하여 멀티 플레이 환경에서도
안정적인 시스템 구축

---

# 2. Problem Statement

- **개별 독립 연산**
	- 모든 AkComponent가 개별 Audio Service를 보유하며 파라미터를 독립적으로 
	  계산합니다. 이로 인해 동일한 위치의 사운드들도 중복된 연산을 수행하게 됩니다

- **비효율적인 리소스 할당**
	- 3D 앰비언스처럼 Spatialization 계산이 불필요한 사운드도 모든 파라미터를 계산하는 
	  정적 서비스 설정을 공유합니다.
	
- **제한 없는 컴포넌트 생성**
	- 총기 발사(Gunfire) 시마다 컴포넌트를 생성하고 재생 직후 파괴하는 과정이 반복되며, 
	  생성 개수에 제한이 없어 메모리와 CPU에 과부하를 줍니다.

- **운영 영향**
	- 다수의 Line Trace(컴포넌트당 10~30개)가 매 틱(0.2f)마다 발생하여 멀티플레이어 
	  환경에서 심각한 성능 저하를 일으킵니다.


## 3. 시스템 아키텍처 (System Architecture)

## 3.1 설계 원칙

다음 3가지 원칙을 기준으로 하여 시스템이 설계 되었다

- 불필요한 연산 제거(Elimination),
- 연산 결과의 재사용(Sharing)
- 객체의 수명 주기 관리(Lifecycle Control).

## 3.2 주요 기능 (Key features)

1. **Modular Audio Service**

사운드 사용 용도에 따라 계산할 파라미터와 tick 간격을 커스터마이징 한다


2. **Shared RTPC Parameters**

계산이 필요한 컴포넌트들을 그룹화하고 이중 하나의 Ak Compoent (Primary Ak)만
 해당 계산을 집중수행하고 나머지는 해당 배포받는 결과값을 참조하여 사운드를 적용한다


3. Managed Ak Component

Obejct 의 종류/목적 등을 고려하여 Spawn 가능한 컴포넌트 수를 제한하고 이미 생성된 객체를
최대한 효율적으로 활용한다


---





| **Usage (용도)**     | **연산 항목 (Target Params)**           | **Tick Interval** | **Line Trace 수** | **비고**                     |
| ------------------ | ----------------------------------- | ----------------- | ---------------- | -------------------------- |
| **3D Ambience**    | Obs / Occ                           | 0.2f              | 5 ~ 10           | Spatialization 등 불필요 항목 제외 |
| **Local Gunfire**  | Obs/Occ, Spatial, Indoor, Elevation | 0.2f              | 10 ~ 30          | 최우선순위 연산 수행                |
| **Remote Gunfire** | 위와 동일                               | **0.5f**          | **10 ~ 20**      | 원거리/타사 노출 시 연산량 절감         |





- **기존 시스템의 한계 (As-Is)**:
    
    - **개별 독립 연산**: 모든 AkComponent가 개별 Audio Service를 보유하며 파라미터를 독립적으로 계산합니다. 이로 인해 동일한 위치의 사운드들도 중복된 연산을 수행하게 됩니다.
        
    - **비효율적인 리소스 할당**: 3D 앰비언스처럼 Spatialization 계산이 불필요한 사운드도 모든 파라미터를 계산하는 정적 서비스 설정을 공유합니다.
        
    - **제한 없는 컴포넌트 생성**: 총기 발사(Gunfire) 시마다 컴포넌트를 생성하고 재생 직후 파괴하는 과정이 반복되며, 생성 개수에 제한이 없어 메모리와 CPU에 과부하를 줍니다.
        
- **운영 영향**: 다수의 Line Trace(컴포넌트당 10~30개)가 매 틱(0.2f)마다 발생하여 멀티플레이어 환경에서 심각한 성능 저하를 일으킵니다.



현재 wwise의 Ak Component 시스템은 각 Component가 자율적인 연산을 수행하도록
설계 되어 있습니다. (예 : 개별적인 Obs/Occ servcie)
개별 AK Component는 자신만의 RTPC 계산 시스템을 가지고 있으며 이를 통해 
obstruction / occlusion 과 같은 rtpc value를 계산한다.

1. 독립적 Parameter 계산
	- Obs/Occ 및 개별 rtpc parameter 들이 Component 의 매 tick 마다 고비용의 line trace를
	  수행하고 있다

2. 종적 서비스 구조(Static setup) 
	- 사운드 종류/중요도에 상관 없이 모든 컴포넌트가 동일한 서비스 설정을 공유합니다.
	  (예 : 3d ambinece 사운드용 Ak Component에서 spatialization 관련 rtpc 계산)


## 1.2 멀티 플레이 환경에서의 성능 병목

이러한 "개별 독립 연산" 방식은 단일 플레이어 환경에서는 큰 문제가 되지 않으나
대규모 멀티플레이 환경에서는 다음과 같은 치명적인 성능 저하를 발생 시킨다

1. 연산량의 기하 급수적 증가
	- 플레이어 한명당 발생하는 사운드 객체가 늘어날수록 시스템 전체의
	  line trace 횟수가 중복되어서 증가한다
	  (예 : 동일/비슷한 위치에서 생성되는 footstp , rustle 용 Ak Component는 
	  각자 개별적인 RTPC 계산을 수행하게 된다)

2. 시스템 오버헤드

	- 멀티환경에서 빈번하게 발생하는 fire and forget (eg : 총 격발) 사운드의 경우 
	  Component 생성과 동시에 파라미터를 동기적(synchronous) 계산하여 업데이트 하고
	  사운드가 재생되면 이후 바로 파괴된다
	- 이때 발생하는 무분별한 spawn/destroy는 메모리 단편화 및 CPU 피크의 주범이다


3. 네트워크 기반의 우선순위 부재

	- 사운드 자체의 중요도 없이 나/ 나외의 모든 사운드를 동일한 방식으로 계산하고 업데이트 하게된다
	- 이는 유동적으로 시스템 조절이 불가능하고 이로 인해 속도저하를 일으키게 된다


---




현재

AkComponent 시스템은 각 Component가 독립적으로 작동하는 구조를 가지고 있습니다.
이러한 구조는 소규모 프로젝트에서는 무제가 되지 않으나 다수의 인원이 투입되는 멀티플레이 
환경에서는 심각한 성능저하를 일으킵니다.

- **과도한 연산 부하:** 모든 AkComponent가 개별적으로 파라미터를 계산하므로,  중복 연산이 기하급수적으로 증가합니다.
 
- **리소스 낭비:** 특히 `Obstruction/Occlusion (Obs/Occ)` 연산을 위한 Line Trace가 모든 컴포넌트에서 매 틱(Tick)마다 발생하여 CPU 성능의 상당 부분을 점유합니다.
    
- **관리의 부재:** 총기 발사(Gunfire)와 같은 'Fire-and-forget' 사운드 생성 시 컴포넌트가 무제한으로 스폰되고 즉시 파괴되는 과정에서 불필요한 할당/해제(overhead) 부하가 발생합니다.
    
따라서 시스템 리소스를 효율적으로 분배하고, 실시간 연산량을 제어하기 위한 새로운 최적화 아키텍처 도입이 필수적입니다.

---







# 3. System Architecture



# 4. Implementation Details

# 5. Testing & Validation



# 2. Ak system optimizaion plan

optimizaion plan의 경우 다음과 같은 큰 카테고리 3가지로 진행 하였습니다.

1. **Modular Audio Service**
2. **Shared RTPC parameters**
3. **Manage AK Component**


## 1. Modular Audio Service

- 사운드의 용도에 맞게 RTPC 계산하는 시스템을 모듈식으로 자유롭게 구성할 수 있는 시스템

## As-Is

![[Pasted image 20260317183844.png]]

- 사운드의 종류나 타입에 관계없이 동일하게 RTPC parameters를 위한 계산을 수행한다
- 예 : 3d ambience / gun fire 모두 동일한 rtpc 계산을 위한 line trace를 사용한다


## To-Be

![[Pasted image 20260317184022.png]]

- 사운드의 용도에 따라 사용할 RTPC를 파악하고 이를 계산한다
- 또한 중요성 (local / remote player 여부) 에 따라 tick interval, num of line traces 변한다
- 예 : 3d ambience의 경우 elevation rtpc만을 계산한다
     gun fire 의 경우 local / remote 여부에 따라 셋팅이 바뀐다

---

## 1. Shared RTPC Parameters

- 이미터의 위치 / 사운드 특성 등에 따라 비슷한 RTPC 값이 필요한 RTPC 를 합쳐
  하나의 Priamry Ak Component에서 RTPC calcuation을 수행 이후 이를 전파하여
  RTPC parameter 자체를 쉐어하는 방식식

## As-Is

- Ak Component 개별로 필요한 rtpc 계산을 수행한다
- 따라서 VO, Movement, Weapon 모두 동일한 RTPC 계산을 수행한다

![[Pasted image 20260317185308.png]]


## To-Be

- 만약 Character용 사운드라면 RTPC parameter 자체가 Ak Component 위치,특성 등에 따라
  크게 변하지 않게 된다
- 따라서 하나의 primary Ak Component (예 : Ak for VO) 에서 기존의 RTPC 계산을 수행하여
  이를 전파 시킨다
- 다른 Ak Component의 경우 Priamry 에서 RTPC 값을 가져와서 바로 적용한다


![[Pasted image 20260317185814.png]]


> [!NOTE] Info
> 대부분의 Fire and forget sound (예 : gun fire) 의 경우 obs/occ 와 같은 rtpc value를 동기화
> 작업을 통해 계산하고 업데이트 하게 된다
> 현재 Ak Component Obtruction/Occlusion Service의 경우에도 초기 시작시 대략 24ea 정도의 
> line trace를 Game Thread에서 쏘게 된다
> 이러한 부분을 고려할때 불필요한 RTPC 계산은 그 이상의 효과를 발휘하게 된다







들여쓰기

<details>
  <summary>여기를 클릭해서 내용을 확인하세요 (제목)</summary>
  <div markdown="1">
    
    이곳에 펼쳐질 내용을 작성합니다.
    - 리스트도 가능하고
    - **굵은 글씨**도 가능합니다.

  </div>
</details>



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



## Gemini said

작성하신 목차와 제공해주신 프레젠테이션의 세부 데이터를 결합하여, **Managed AkComponent 시스템**의 각 항목을 구체적으로 상세화한 기술 설계서입니다.

---

# 📑 Managed AkComponent 기술 상세 설계서 (Draft)

## 1. 개요 (Introduction)

- **문서의 목적**: 본 문서는 대규모 멀티플레이어 환경에서 발생하는 오디오 연산 병목 현상을 해결하기 위해 설계된 'Managed AkComponent' 시스템의 구조와 구현 세부 사항을 정의합니다.
    
    +1
    
- **도입 배경**: 기존 Wwise AkComponent 시스템은 각 컴포넌트가 독립적인 연산 유닛으로 동작하여, 객체가 많아질수록 CPU 부하가 선형적으로 증가하는 구조적 한계를 가지고 있습니다.
    
    +2
    
- **기대 효과**: 중앙 집중형 데이터 공유 및 컴포넌트 풀링을 통해 10 vs 10 이상의 전투 상황에서도 안정적인 프레임워크와 오디오 품질을 보장합니다.
    
    +3
    

---

## 2. 현황 및 문제점 (Problem Statement)

- **기존 시스템의 한계 (As-Is)**:
    
    - **개별 독립 연산**: 모든 AkComponent가 개별 Audio Service를 보유하며 파라미터를 독립적으로 계산합니다. 이로 인해 동일한 위치의 사운드들도 중복된 연산을 수행하게 됩니다.
        
        +2
        
    - **비효율적인 리소스 할당**: 3D 앰비언스처럼 Spatialization 계산이 불필요한 사운드도 모든 파라미터를 계산하는 정적 서비스 설정을 공유합니다.
        
    - **제한 없는 컴포넌트 생성**: 총기 발사(Gunfire) 시마다 컴포넌트를 생성하고 재생 직후 파괴하는 과정이 반복되며, 생성 개수에 제한이 없어 메모리와 CPU에 과부하를 줍니다.
        
        +2
        
- **운영 영향**: 다수의 Line Trace(컴포넌트당 10~30개)가 매 틱(0.2f)마다 발생하여 멀티플레이어 환경에서 심각한 성능 저하를 일으킵니다.
    
    +1
    

---

## 3. 시스템 아키텍처 (System Architecture)

- **설계 원칙**: 불필요한 연산 제거(Elimination), 연산 결과의 재사용(Sharing), 객체의 수명 주기 관리(Lifecycle Control).
    
    +4
    
- **주요 기능 (Key Features)**:
    
    1. **Modular AudioService**: 사운드 사용처(Usage)에 따라 계산할 파라미터와 틱 간격을 커스터마이징합니다.
        
        +1
        
    2. **Shared RTPC Parameters**: 계산이 필요한 로직은 단 하나의 **Primary AkComponent**에서 집중 수행하고, 나머지 컴포넌트는 해당 결과값을 배포받아 사용합니다.
        
        +2
        
    3. **Managed Ak Component**: 캐릭터당 최대 스폰 가능한 컴포넌트 수를 제한(Max 3)하고, 생성된 객체를 효율적으로 재활용합니다.
        
        +2
        

---

## 4. 구현 상세 (Implementation Details)

### **4.1. 모듈별 오디오 서비스 설정 (To-Be)**

사운드의 우선순위와 용도에 따라 연산 셋업을 차별화합니다.

+2

|Usage (용도)|연산 항목 (Target Params)|Tick Interval|Line Trace 수|비고|
|---|---|---|---|---|
|**3D Ambience**|Obs / Occ <br><br>+1|0.2f|5 ~ 10|Spatialization 등 불필요 항목 제외|
|**Local Gunfire**|Obs/Occ, Spatial, Indoor, Elevation|0.2f <br><br>+1|10 ~ 30 <br><br>+1|최우선순위 연산 수행|
|**Remote Gunfire**|위와 동일|**0.5f**|**10 ~ 20**|원거리/타사 노출 시 연산량 절감|

### **4.2. 중앙 집중형 데이터 흐름 (Centralization)**

- **Primary AkComponent**: 실시간 Line Trace(Obs/Occ, Indoor, Elevation 등)를 수행하여 RTPC 파라미터를 갱신합니다.
    
- **Secondary Components**: 자체적인 Tick 연산을 중단하고(No Tick, Trace 0), Primary가 갱신한 값을 직접 가져와(Get Parameters) 이벤트에 적용합니다 .
    
    +1
    

---

## 5. 테스트 및 검증 (Testing & Validation)

- **테스트 시나리오**: 10 vs 10 대규모 교전 상황에서 총기 발사 및 발소리 사운드에 Managed 시스템 적용.
    
- **비교 분석 결과**:
    

|비교 항목|AS-IS (전통적 방식)|TO-BE (Managed 방식)|
|---|---|---|
|**컴포넌트 관리**|무제한 생성 및 즉시 파괴 <br><br>+2|캐릭터당 최대 3개로 제한 및 재사용 <br><br>+1|
|**연산 중복도**|컴포넌트마다 개별 동기 연산 수행 <br><br>+1|Primary에서 계산 후 데이터 분배 <br><br>+1|
|**Line Trace 부하**|모든 컴포넌트가 10~30개 소모 <br><br>+1|Secondary는 0개 소모 (Primary 공유)|
|**리소스 효율**|정적이고 경직된 서비스 구조|Usage별 맞춤형 모듈 서비스 제공 <br><br>+1|