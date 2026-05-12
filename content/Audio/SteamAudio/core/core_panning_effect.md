---
title: "[Core] Panning Effect 분석"
author: KurtJang
tags:
  - Blog
  - "#Programming"
  - CPP
  - SteamAudio
date: 2026-05-12
draft: "False"
description: "[SteamAudio] Panning Effect 분석 (core module)"
---

---

# 1. Introduction

- mono 입력 -> multi-channel 출력으로 변환 (spatialization 효과)
- 소리방향 (`Vector3f direction`) 을 받아 각 스피커에 배분할 가중치(weight)를 계산
- FFT / convolution 없이 순수 Gain 만으로 작동 (panning 기본요소)

# 2. 구성요소

``` cpp
struct PanningEffectSetttings
{
    //Stereo / 5.1 / 7.1 등
    const SpeakerLayout* spekaerLaytout;
}

//매 프레임 소리 방향 입력
strcut PanningEffectParam
{
    const Vector3f* direction //소리가 오는 방향
}

```

| Layout           | algorithm                 | note                    |
| ---------------- | ------------------------- | ----------------------- |
| Mono             | 항상 1.0f                   | 계산 X                    |
| Stereo           | `stereoPaningWeight`      | con/sin constant- power |
| Qaud / 5.1 / 7.1 | `PairwisePanningWeight`   | 인접 스피커 2개에만 배분          |
| Custom           | `firstOrderPanningWeight` | 내적(dot-product)기반       |

## 특이사항

- Crossfade - 방향이 갑자기 바뀔 때 튀는 소리 방지

``` cpp
// 이전 프레임 가충치 -> 현재 프레임 가중치로 선형 보정
auto alpha = (float) j / (float) in.numSamples();
auto blendedWeight = alpha * weight + (1.0f - alpha) * weightPrev;
```

- pairwise - 5.1/7.1에서 인접한 2개 스피커만 활성화 / 나머지는 0

``` cpp
//azimuth 각도로 스피커 pair 결정
if (index == speakerIndices[0]) return consf();
els if (index == speakerIndices[1]) return sinf;
else return 0.0f;                            
```


---
# 3. 예제 코드

``` cpp
//stereo constant power panning method
// direction.x : -1 (left)  ~ +1 (right)
float p = direction.x();
float q = (p + 1) * (pi / 4); // 0 ~ 2_PI mapping

float weightL = cosf(q);    //left speaker
float weightR = sinf(q);    //right speaker
//cos^2 (q) + sin^2(q) = 1 에너지의 합은 항상 일정

```

---

# 4. 실전 코드

``` cpp
AudioEffectState PanningEffect::apply (const PanningEffectParam& params,      
                                       const AudioBuffer& in,
                                       AudioBuffer& out)
{
    
}


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