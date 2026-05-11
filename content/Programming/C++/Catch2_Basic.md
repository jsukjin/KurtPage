---
title: Catch2 basic
author: KurtJang
tags:
  - Blog
  - "#Programming"
  - "#CPP"
  - "#Debug"
date: 2026-05-08
draft: "False"
description: Catch2에 대한 기초 개념/사용법에 대한 내용
---

---

# 1. Catch2

- Catch2 는 C++ 개발자들 사이에서 매우 인기있는 **유닛 테스트(Unit Test) 프레임 워크** 입니다.
- 기존의 Google Test(gtest)나 cppunit에 비해 문법이 훨씬 직관적이다
- 설정이 간단하다는 강력한 장점이 있어 현대적인 C++ 프로젝트에서 자주 사용 됩니다.

<br>

<strong><font color="#b3f594">1. 자연스러운 문법</font></strong>

- 테스트 이름에 일반 문장을 쓸수 있고 `REQUIRE(a==b)` 와 같이 표준 C++ 비교 연산자를
  그대로 사용 합니다.

<strong><font color="#b3f594">2. 섹션 구조</font></strong>

하나의 텍스트 케이스 안에서 `SECTION`을 나눠 실행할 수 있습니다.
각 섹션은 독립적인 환경에서 실행되므로 설정(Setup)과 해지(Teardown) 코드를 중복해서 
작성할 필요가 없습니다.


<font color="#b3f594">3. 태그 시스템</font>

테스트 케이스마다 `[vector]` `[fast]` 같은 태그를 달아 특정 그룹의 테스트만 골라 실행하기
편리 합니다.

<font color="#b3f594">4. 마이크로 벤치마킹</font>

테스트 뿐만 아니라 코드의 성능을 측정하는 벤치마크 기능도 내장되어 있습니다.


<font color="#b3f594">5.버전별 특징 </font>

V2 : 헤더 파일 하나만 포함하면 끝나는 방식이라 도입이 매우 쉬움
V3 : 컴파일 속도 향상을 위해 일반적인 라이브러리 형태로 구조가 변경 됨


## 1. 구성 요소


`TEST_CASE("이름", "[태그")`

- 테스트 하나의 단위
- 이름 : 실패시 출력 되는 식별자, 전체 파일에서 유일해야 함
- 태그 : 실행 필터링 분류 (예 : `[Array]` `[memory]` 등)

`SECTION("이름")`

- `TEST_CASE` 안에서 독립적인 분기
- 각 SECTION 진입 전 `TEST_CASE` 코드가 새로 실행됨
- 초기화 코드를 여러 케이스가 공유할 때 사용


`REQUIRE(조건)`

- 조건이 거짓이면 테스트 즉시 중단

`CHECK(조건)`

- 조건이 거짓 이여도 계속 진행 - 여러 항목을 한꺼번에 확인할때


`REQUIRE_FALSE(조건)` / `CHECK_FALSE(조건)`

- 거짓이어야 통과

`Approx(값)`

- `float / dobule` 비교시 사용 (부동 소수점 비교 시)

<br>

## 2. 설치 방법

### A. 직접 설치

1. **[Catch 소스 저장소](https://github.com/catchorg/Catch2)**에서 파일을 다운로드 받는다 
2. 프로젝트 폴더에 넣고 소스 코드에서 `#include "catch.hpp"` 

<br>
### B. Cmake 활용

별도의 설치 과정 없이, Cmake가 빌드 시점에 Catch2 소스 코드를 알아서
내려받아 프로젝트에 포함 시키는 방식 (Featch)
인터넷만 연결되어 있다면 바로 실행 가능 합니다.

``` python
#=== CmakeLists.txt ===

cmake_minimum_required(VERSION 3.14)
project(MyTestProject)

# 1. FetchContent 모듈 로드
include(FetchContent)

# 2. Catch2 다운로드 정의
FetchContent_Declare(
  Catch2
  GIT_REPOSITORY https://github.com/catchorg/Catch2.git
  GIT_TAG        v3.4.0 # 사용하고자 하는 버전 태그
)

# 3. 프로젝트에 Catch2 사용 가능하게 설정
FetchContent_MakeAvailable(Catch2)

# 4. 내 테스트 실행 파일 생성
add_executable(run_tests test_main.cpp)

# 5. Catch2 라이브러리 링크
# Catch2::Catch2WithMain을 링크하면 별도의 main() 함수를 작성할 필요가 없습니다.
target_link_libraries(run_tests PRIVATE Catch2::Catch2WithMain)
```



## 3. 예제 코드

``` cpp

//V3 기준
#include <catch2/catch_test_macros.hpp>


// 테스트할 함수
int Add(int a, int b) 
{
    return a + b;
}

TEST_CASE("Addition Test", "[math]")
{
    //REQUIRE : 조건이 거짓이면 여기서 즉시 중단
    //Add (1,2) 가 3 이 아니면 아래 줄은 실행이 안됨
    REQUIRE(Add(1,2) == 3);
    
    //REQUIRE
    // 첫번째가 통과 했을 때만 여기까지 옴
    REQUIRE(Add(10,-2) == 8);
}

//--------------------------------------------

// V2 기준
#define CATCH_CONFIG_MAIN
#include "catch.hpp"

TEST_CASE("Basic Test")
{
    //CHECK - REQUIRE.와 달리 실패해도 계속 진행
    //여러 항목을 한꺼번에 확인할 때 사용
    //여기서 실패해도 다음 CHECK로 넘어감
    CHECK(1 + 1 == 2);
}

```

- 성공적으로 실행하면 "All test passed" 라는 초록색 메세지 출력

## 4. 실제 코드

```cpp
// Catch2 v2
// SteamAudio - Array.test.cpp

#include <catch2/catch_all.hpp>
#include <array.h>

TEST_CASE("Array is created with the specified size", "[Array]")
{
    ipl::Array<int> a (10);
    REQUIRE(a.size(0) == 10);
}

TEST_CASE("Array elements cna be accessed correctly", "[Array]")
{
    ipl::Array<int> a (10);
    a[0] = 12;
    a[1] = 157;
    
    REQUIRE(a[0]= == 12);
    REQUIRE(a[1] == 157);
    REQUIRE(a.data()[0] == a[0]);
    REQUIRE(a.data()[1] == a[1]) 
}

```


<strong><font color="#b3f594">Catch2 v2/v3 차이점</font></strong>

| v2                                     | v3                                |
| -------------------------------------- | --------------------------------- |
| `#include <catch.hpp>`                 | `#include <catch2/catch_all.hpp>` |
| `#define CATCH_CONFIG_MAIN` (test.cpp) | 없음                                |
| `Catch::Catch` (Cmake)                 | `Catch2::Catch2WithMain` (Cmake)  |
| `REQUIRE` / `CHECK` / `Approx`         |  동일                               |


## 5. 유용한 링크

- [Catch2.org](https://catch2.org/)
- [Catch2(Git)](https://github.com/catchorg/Catch2)

---
