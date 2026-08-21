---
title: "[Core] Overview"
author: KurtJang
tags:
  - Blog
  - "#Programming"
  - SteamAudio
  - CPP
date: 2026-08-11
draft: "false"
description: Core Overview
---

---

# 1. 전체 개요

<strong style="color:#b3f594">Steam Audio Core</strong>는 "소리가 공간을 어떻게 통과하는지"를 실제 지오메트리 기반으로 계산해주는 C++ 라이브러리다. 파일이 200개가 넘어서 처음 보면 막막하지만, 실제로 하는 일은 딱 4단계로 나눌 수 있다.

![[core_overview_flow.svg|700]]

1. **Scene / Geometry** - 레벨의 벽, 바닥 같은 지오메트리를 삼각형 메시로 등록하고, 빠른 충돌 검사를 위해 BVH(경계볼륨계층구조)로 정리한다.
2. **Probe / Baking** - 레벨이 로딩되기 전에, 비싼 계산(경로 탐색, 반사 시뮬레이션)을 미리 해서 저장해둔다.
3. **Simulation** - 게임이 실행되는 동안, 매 프레임 소스와 리스너의 위치를 반영해서 직접음/반사음/회절음을 계산한다.
4. **DSP Effect** - 시뮬레이션 결과를 실제 오디오 신호에 적용해서 최종 사운드를 만든다.

> [!success] 핵심 아이디어
> 이 라이브러리 전체를 관통하는 단 하나의 설계 철학은 **"비싼 건 미리 하고, 실시간에는 최소한만 한다"** 이다.
> 벽의 위치 같은 정적인 정보는 로딩 전에 다 계산해두고(Bake), 소스/리스너처럼 계속 움직이는 값만 매 프레임 반영한다.
> [[core_path_finder|PathFinder]]에서 본 Bake(Dijkstra) vs Runtime(A*)의 구분도 이 철학의 한 예시일 뿐이다.


---

# 2. 카테고리별 파일

`core/src/core/` 안의 200개가 넘는 파일을 역할별로 묶으면 다음과 같다. 이미 정리한 파일은 링크로 연결했다.

## 2.1 기반 - 수학 / 자료구조 / 플랫폼

프로그램 전체가 공통으로 쓰는 가장 아래 계층이다.

- **수학 타입**: `vector.h`, `matrix.h`, `quaternion.h`, `coordinate_space.h`, `polar_vector.h`, `box.h`, `sphere.h`, `triangle.h`
- **구면 조화 함수(SH)**: `sh.h/.cpp`, `sh/` (반사음을 방향별로 압축 표현할 때 사용)
- **자료구조**: [[core_Array|array.h]], `containers.h`, `stack.h`, `triple_buffer.h`
- **SIMD 최적화**: `float4.h`, `float8.h`, `sse_float4.h`, `avx_float8.h`, `neon_float4.h` ([[core_simd|SIMD 정리글]] 참고)
- **플랫폼/유틸**: `platform.h`, `util.h`, `types.h`, [[core_memory_allocator|memory_allocator]], `log.h`, `error.h`, `profiler.h`

## 2.2 Scene & Geometry - 지오메트리

레벨의 벽, 바닥, 오브젝트를 "충돌 검사가 가능한 형태"로 등록하는 계층이다.

- **핵심**: [[core_scene|scene.h/.cpp]], [[core_mesh|mesh.h/.cpp]], [[core_instanced_mesh|instanced_mesh]], `static_mesh.h/.cpp`, `custom_scene.h/.cpp`
- **가속 구조**: [[core_bvh|bvh.h/.cpp]], `ray.h/.cpp`, `hit.h`
- **재질**: `material.h` (재질별 흡음/산란 계수)
- **하드웨어 백엔드별 구현체**: `embree_scene/static_mesh/instanced_mesh.*`, `radeonrays_scene/static_mesh.*`

## 2.3 Probe & Baking - 사전 계산

레벨에 가상의 관측 지점(probe)을 뿌리고, 그 지점들 사이의 정보를 미리 구워두는 계층이다.

- **Probe 자체**: `probe.h`, `probe_data.h`, `probe_batch.h/.cpp`, `probe_generator.h/.cpp`, `probe_manager.h/.cpp`, `probe_tree.h/.cpp`, `octree_probes.h/.cpp`
- **경로 탐색(Bake)**: [[core_path_finder|path_finder]], `path_visibility.h/.cpp`
- **반사음 Bake**: `reflection_baker.h/.cpp`, `baked_reflection_data.h/.cpp`, `baked_reflection_simulator.h/.cpp`

## 2.4 Simulation - 실시간 시뮬레이션

매 프레임 소스/리스너 위치를 반영해서 소리의 물리적 특성을 계산하는 계층이다.

- **직접음(Direct)**: `direct_simulator.h/.cpp` - 거리 감쇠, 지향성, 공기 흡수, occlusion 계산
  - 관련 계산: `distance_attenuation.h/.cpp`, `directivity.h/.cpp`, `air_absorption.h/.cpp`, `deviation.h/.cpp`
- **경로(Pathing)**: `path_simulator.h/.cpp` (앞서 [[core_path_finder|PathFinder]]가 찾은 경로를 실제 시뮬레이션에 적용)
- **반사(Reflection)**: `reflection_simulator.h/.cpp` + 하드웨어 백엔드(`embree_reflection_simulator.*`, `radeonrays_reflection_simulator.*`), `reflection_simulator_factory.h/.cpp`
- **결과물 표현**: `energy_field.h/.cpp` (방향별/대역별 에너지), `impulse_response.h/.cpp`, `reconstructor.h/.cpp`
- **오케스트레이션**: `simulation_manager.h/.cpp`, `simulation_data.h/.cpp`, `job.h`, `job_graph.h/.cpp`, `thread_pool.h/.cpp`


## 2.5 DSP Effect - 실제 오디오 처리

시뮬레이션 결과를 실제 PCM 오디오 버퍼에 적용하는 계층이다. 대부분 "Effect"로 끝난다.

- **오디오 버퍼 자체**: [[core_audiobuffer|audio_buffer.h/.cpp]]
- **직접음 적용**: [[core_direct_effect|direct_effect.h/.cpp]], `gain_effect.h/.cpp`, [[core_eqeffect|eq_effect.h/.cpp]], `delay.h/.cpp`, [[core_delay_effect|delay_effect.h/.cpp]]
- **공간감(Panning/Binaural)**: [[core_panning_effect|panning_effect.h/.cpp]], `binaural_effect.h/.cpp`, `virtual_surround_effect.h/.cpp`
- **Ambisonics(구면 오디오)**: `ambisonics_encode/decode/rotate/panning/binaural_effect.*`
- **반사/잔향**: `reverb_effect.h/.cpp`, `reverb_estimator.h/.cpp`, `hybrid_reverb_effect.h/.cpp`, `hybrid_reverb_estimator.h/.cpp`
- **컨볼루션(반사음 렌더링용)**: `overlap_add_convolution_effect.*`, `overlap_save_convolution_effect.*`, `tan_convolution_effect.*`
- **FFT 백엔드**: `fft.h` + `pffft_fft.cpp` / `ipp_fft.cpp` / `vdsp_fft.cpp` (플랫폼별 구현체)
- **HRTF(머리전달함수, 바이노럴의 핵심 데이터)**: `hrtf.cpp`, `hrtf_database.*`, `hrtf_map*.*`, `sofa_hrtf_map.*`, `hrtf2sh.cpp`, `cipic_124.inl`, `speaker_layout.*`

## 2.6 하드웨어 가속 백엔드

같은 역할(레이캐스트, GPU 연산 등)을 여러 하드웨어로 수행할 수 있게 만든 계층이다. 이름에 백엔드 이름이 그대로 들어간다.

- **Embree** (Intel CPU 레이트레이싱): `embree_device/scene/static_mesh/instanced_mesh/reflection_simulator.*`
- **RadeonRays** (AMD GPU 레이트레이싱): `radeonrays_device/scene/static_mesh/reflection_simulator.*`
- **OpenCL** (범용 GPU 연산): `opencl_device/buffer/kernel/energy_field/impulse_response/reconstructor.*`
- **TrueAudio Next**: `tan_device.*`, `tan_convolution_effect.*`

## 2.7 API / 직렬화 / 기타

- **공개 C API 헤더**: `phonon.h`, `phonon_interfaces.h`, `docs.h`
- **API 래퍼 구현**: `api_*.cpp/.h` (약 40개 - 내부 C++ 클래스를 C API로 감싸는 얇은 레이어)
- **직렬화**: `serialized_object.h/.cpp` + `*.fbs` (FlatBuffers 스키마: `mesh.fbs`, `probe_batch.fbs`, `energy_field.fbs`, `path_data.fbs` 등)
- **컨텍스트/수명 관리**: `context.h/.cpp`, `library.h/.cpp`


---

# 3. 특이사항

## 3.1 왜 이렇게 파일이 많고, 비슷한 이름이 반복될까?

> [!info] 패턴 - 인터페이스 + 백엔드별 구현체 + Factory
> `reflection_simulator.h`(인터페이스) 옆에 `embree_reflection_simulator.*`, `radeonrays_reflection_simulator.*`가 나란히 있는 이유는,
> **어떤 하드웨어(CPU/GPU, 어떤 GPU 벤더)를 쓸지 실행 중에 정해지기 때문**이다.
> `reflection_simulator_factory.h/.cpp`, `scene_factory.h/.cpp`, `energy_field_factory.h/.cpp`처럼 이름에 `_factory`가 붙은 파일들이
> "지금 이 환경에서는 어떤 구현체를 만들어야 하는지" 판단해서 실제 객체를 생성해준다.
> 즉 <strong style="color:#b3f594">Scene</strong>, <strong style="color:#b3f594">Reflection Simulator</strong> 같은 핵심 개념은 하나인데, 그걸 구현하는 방법(Embree/RadeonRays/OpenCL)만 여러 개인 셈이다.

## 3.2 왜 `api_*.cpp`가 따로 존재할까?

> [!info] C API와 내부 C++ 클래스의 분리
> Steam Audio는 Unity, Unreal, Wwise, FMOD 등 완전히 다른 언어/런타임에서 다 가져다 쓸 수 있어야 한다.
> 그래서 내부적으로는 평범한 C++ 클래스(`Scene`, `Simulator` 등)로 구현하고,
> `api_scene.cpp`, `api_simulator.cpp` 같은 파일들이 이를 **불투명 핸들(opaque handle) 기반의 순수 C 함수**로 한 번 더 감싼다.
> 이렇게 하면 C++ ABI(이름 맹글링, 예외 처리 등)에 종속되지 않고 어떤 언어에서든 안전하게 라이브러리를 호출할 수 있다.

## 3.3 왜 `.fbs` 파일이 곳곳에 있을까?

> [!info] FlatBuffers - 빠른 baked 데이터 로딩
> `probe_batch.fbs`, `energy_field.fbs`, `path_data.fbs` 같은 파일은 Google의 **FlatBuffers** 직렬화 스키마다.
> 베이킹 결과(경로, 반사음 에너지 필드 등)를 디스크에 저장했다가 로딩할 때, 일반 파싱 없이 **메모리에 매핑만 해도 바로 읽을 수 있는 바이너리 포맷**을 만들기 위해 사용한다.
> 레벨 로딩 속도가 중요한 게임에서, 수백 개의 probe 데이터를 빠르게 불러오려면 이런 "파싱 없는" 포맷이 필수적이다.

## 3.4 왜 SIMD 파일이 CPU 아키텍처별로 나뉘어 있을까?

> [!info] 벡터 연산 최적화
> `sse_float4.h`(x86), `avx_float8.h`(x86, 더 넓은 레지스터), `neon_float4.h`(ARM)는 모두 "4개 또는 8개의 float를 한 번에 계산한다"는 같은 목적을 갖지만,
> CPU마다 벡터 연산 명령어 집합이 다르기 때문에 각각 별도로 구현되어 있다. 반사음 시뮬레이션처럼 계산량이 많은 부분에서 이 최적화가 성능에 큰 영향을 준다.

## 3.5 왜 Bake와 Runtime이 계속 짝을 이룰까?

이미 [[core_path_finder|PathFinder 글]]에서 본 Dijkstra(Bake) / A*(Runtime) 패턴이 반사음 쪽에도 그대로 나타난다.

- `reflection_baker.cpp` (Bake) ↔ `reflection_simulator.cpp` (Runtime)
- `baked_reflection_data.h` (Bake 결과 저장) ↔ `energy_field.h` (Runtime 계산 결과)

**정적인 지오메트리 정보는 미리 계산해서 저장하고, 움직이는 소스/리스너 위치만 실시간으로 반영한다**는 설계 원칙이 코드베이스 전체에 일관되게 적용되어 있다는 걸 알 수 있다.


---

# 4. 더 공부하고 싶다면

## 4.1 이 블로그에서 이미 정리한 글

- 기반: [[core_Array]], [[core_matrix]], [[core_simd]], [[core_memory_allocator]], [[core_util]]
- 지오메트리: [[core_scene]], [[core_mesh]], [[core_instanced_mesh]], [[core_bvh]]
- 오디오 버퍼/이펙트: [[core_audiobuffer]], [[core_direct_effect]], [[core_delay_effect]], [[core_eqeffect]], [[core_panning_effect]]
- Probe/경로: [[core_path_finder]]

## 4.2 DeepWiki (외부, AI가 자동 생성한 코드 위키)

> [!tip] 전체 그림이 다시 헷갈릴 때
> https://deepwiki.com/ValveSoftware/steam-audio 여기서 특히 아래 항목들이 이 글의 카테고리와 대응된다.
> - **Core Architecture** → 2.7절(API/Context)과 대응
> - **Simulation Engine** → 2.4절(Direct/Path/Reflection Simulation)과 대응
> - **Audio Effects** → 2.5절(DSP Effect)과 대응
> - **Math & Optimization** → 2.1절(기반)과 대응

## 4.3 실제 소스코드 - GitHub

- 저장소: https://github.com/ValveSoftware/steam-audio
- Core 소스 경로: `core/src/core/`
- 공개 API 정의: `core/src/core/phonon.h` (전체 API의 시작점. 함수 하나가 궁금하면 여기서 검색)
- 빌드 구조: `core/CMakeLists.txt`

## 4.4 배경 이론이 더 궁금하다면

- **레이트레이싱/BVH**: PBR(Physically Based Rendering) 계열 자료 - 그래픽스의 BVH와 원리가 거의 동일하다.
- **구면 조화 함수(SH)**: 반사음의 방향 정보를 압축하는 이유를 이해하려면 "Spherical Harmonics lighting" 자료(3D 그래픽스 조명 쪽 자료)가 의외로 도움이 된다.
- **HRTF/바이노럴 오디오**: "Head-Related Transfer Function" 키워드로 검색하면 관련 논문/설명 자료가 많다.
- **길찾기(Dijkstra/A*)**: [[core_path_finder]] 글의 3장에서 기초부터 설명해뒀다.
