---
title: memory.test 분석
author: KurtJang
tags:
  - Blog
date: 2026-05-08
draft: "False"
---

> [!NOTE] 
> Memory.test.cpp 분석
> 

---
<br>
<font color="#b3f594"><strong>Table of Contents</strong> </font>

- [Code Example](#code-example)
- [Callout Example](#callout-example)

%% create table of contents (옵션 없는거) 를 마지막에 사용해 주세요 %%

<br>

---

``` cpp
#include <catch.hpp> // catch2

#include <memory_allocaltor.h>
#include <context.h>
#include <types.h>
#include <containers.h>
#include <array.h>


#if defined(IPL_OS_WINDOWS) && !defined(_DEBUG)

// 커스덤 할당자가 몇바이트를 할당했는지 기록하눈 카운터
// TEST_CASE 시작시 0 으로 초기화
gByteAllocated = 0;

void* IPL_CALLBACK allocateMemory(const size_t size, const size_t alignment)
{
    gByteAllocated += size;  //요청 크기 누적
    return malloc(size);     //실제 할당
}

void IPL_CALLBACK freeMemory(void* memoryBlock)
{
    free(memoryBlock);
}

// 힙에서 현재 사용중인 메모리 총량을 바이트로 반환
init measureHeap()
{
    //1. 이 프로세스의 heap handle 획득
    auto heap = GetProcessorHeap(); 
    //2. 다른 스레드가 heap을 건드리지 못하게 잠금
    HeapLock(heap);
    
    //3. 순회 시작점을 초기화
    PROCESS_HEAP_ENTRY heapEntry;
    heapEntry.lpData = nullptr;
    
    auto size = 0;
    
    //4. 블록을 하나씩 순회
    while(HeapWalk(heap, &heapEntry))
    {
        //5. 사용중인 블록만 크기 누적
        if(heapEntry.wFlags & 
        (PROCESS_HEAP_ENTRY_BUSY | PROCESS_HEAP_ENTRY_MOVABLE))
        {
            //6. 여기서 크기 누적
            size += heapEntry.cbData;
        }
    }
    
    //7. 잠금 해제
    HeapUnLock(heap);
    
    //8. 사용중인 총 바이트 반환
    return size;
}

//TEST 용 obj
struct BigObject
{
    ipl::vector<float> data;
    
    BigObject(const size_t numElements)
        : data(numElements)
    {}
}

//TEST 1
TEST_CASE("Memory::allocate allocation are routed correctly", "[memory]")
{
    //1. 카운터 초기화
    // 이전 테스트에서 남은 값을 지운다
    gBytesAllocated = 0; 
    
    //2. 커스덤 할당자 지원
    //이제부터 gMemory().allocate() ->allocateMemory() callback 경유
    ipl::gMemory().init(allocateMemory, freeMemory);
    
    //3. 할당 전 heap snaptshot
    //예 : 현재 heap 사용량 = 50,000 바이트
    auto baseline = measureHeap();
    //baseline = 50,000
    
    //4. 실제 할당
    //allocateMemory(1024, 64) 콜백 실행
    //예 : gBytesAllocated += 1024 -> gBytesAllocated = 1024
    //     malloc(1024) -> heap : 50,000 + 1024 = 51,024
    auto memoryBlock = ipl::gMemory().allocate(1024,
										   ipl::Memory::kDefaultAlignment);
    
    //5. Heap 증가량 측정
    auto bytesAllocated = measureHeap() - baseline;
    //measureHeap() = 51.024
    //51,024 - 50,000 = 1024
    //bytesAllocated = 1024
    
    //6. 메모리 해제
    //freeMemory(memBlock) + free()
    //heap : 51,024 -> 50,000 (원복)
    ipl:gMemory().free(memoryBlock);
    
    //7. 할당자 원복
    //다음 테스트가 기본 malloc/free로 시작하도록 정리
    ipl::gMemory().init(nullptr, nullptr);
    
    //8. 검증
    REQUIRE(bytesAllocated == gBytesAllocated);
    
    //bytesAllocated = 1024 (힙에서 실제로 늘어난 양)
    //gBytesAllocated = 024 (콜백이 기록한 양)
    //결과가 같으면 PASS    
}


//TEST 2
TEST_CASE("STL container allocations are routed correctly", "[memory]")
{
    gBytesAllocated = 0;
    ipl::gMemory().init(allocateMemory, freeMemory);
    
    auto bytesAllocated = 0;
    
    {
        auto baseline = measureHeap();
        auto bigObject = ipl:make_unique_<BigObject>(32);
        bytesAllocated = measureHeap() - baseline;
    }
    
    ipl::gMemory().init(nullptr, nullptr);
    REQUIRE(bytesAllocated == gBytesAllocated);
}




#endif

```



## WIndows Heap

``` cpp

// 윈도우 힙 블록하나의 구조체
PROCESS_HEAP_ENTRY heapEntry;

// 이 블록의 시작 주소
heapEntry.lpData;

// 이 블록의 크기 (Byte)
heapEntry.cbData;

//이 블록의 상태
heapEntry.wFlags;

//사용중인 블록 (malloc으로 할당됨)
heapEntry.wFlags & PROCESS_HEAP_ENTRY_BUSY

//이동 가능한 블록
heapEntry.wFlags & PROCESS_HEAP_ENTRY_MOVABLE



// HeapWalk (전체순회)
while (HeapWalk(heap, &heapEntry))
{
    //heap entry에 다른 블록 정보가 채워짐
}



```


테스트 예제
``
``` cpp
 //== TEST 예제 ==
 
 
 //할당 전 총 용량
 auto baseline = measureHeap();
 
 //1024 바이트 할당
 auto ptr = gMemory().allocate(1024);
 
 //늘어난 양 = 1024
 auto after = measureHeap() - baseline;
 
 // 콜백도 1024를 기족했는지 확인
 REQUIRE(after == gBytesAllocated);
 
```








---


<font color="#b3f594">1. 역할 분리</font>
<font color="#b3f594">1. 역할 분리</font>
<font color="#b3f594">1. 역할 분리</font>
<font color="#b3f594">1. 역할 분리</font>


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