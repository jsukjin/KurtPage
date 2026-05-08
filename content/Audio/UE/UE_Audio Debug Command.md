---
title: Audio Debug Command
author: KurtJang
date: 2025-12-23
tags:
  - "#Blog"
  - "#UE"
  - "#UEAudio"
draft: "False"
---

>[!Info] Summary
>자주쓰는 UE Audio debug Command 정리

---
<br>

<strong><font color="#9fffa3">Table of Contents</font></strong>

1. [1. InGame](#1-ingame)
	1. [1. 3D Audio Debug](#1-3d-audio-debug)
	2. [2. Listener Debug](#2-listener-debug)
	3. [3. 3D Active sounds Debug](#3-3d-active-sounds-debug)
	4. [4. Active Sounds Debug](#4-active-sounds-debug)
	5. [5. Active Sounds Debug (log)](#5-active-sounds-debug-log)
2. [2. Mix](#2-mix)
	1. [1. SoundModulation](#1-soundmodulation)
3. [3. Profiling](#3-profiling)
4. [4. Links](#4-links)

<br>

---

# 1. InGame

## 1. 3D Audio Debug

월드에서 audio 플레이 상태 확인
``` cpp fold title:Cmd
au.3dVisualize.Enabled 1
```

## 2. Listener Debug

World에 Listener Transform 표시
``` cpp fold title:Cmd
au.3dVisualize.Listeners 1
```
- <font color="#ffb15b"> au.3dVisualize.Enabled 1</font> 이후 사용 필요

---

## 3. 3D Active sounds Debug

현재 active 상태 사운드의 3d 좌표 visualize
``` cpp fold title:Cmd
au.3dVisualize.ActiveSounds 1
```
- 0: Disable, 1: Volume (Lin), 2: Volume (dB), 3: Distance, 4: Random color

![[UE_AudioDebug_3D_ActiveSounds.webp|300]]

## 4. Active Sounds Debug

현재 Actvie 상태에 있는 모든 사운드 관련 정보를 screen에 표시함
``` cpp fold title:Cmd
au.Debug.Sounds 1
```

![[UE_AudioDebug_ActiveSounds.webp|500]]

## 5. Active Sounds Debug (log)

현재 Actvie 상태에 있는 모든 사운드 관련 정보를 표시 (log)
``` cpp fold title:Cmd
au.Debug.Sounds 1
```

![[UE_AudioDebug_ActiveSounds_Log.webp]]

---

# 2. Mix

## 1. SoundModulation

Modulation Matrix 표시
``` cpp fold title:Cmd
au.Debug.Modulation.Enable.Matrix 1
```

만약 특정 CB 만 보고 싶다면
``` cpp fold title:Cmd
au.Debug.Modulation.Filter.Buses [BUS_NAME] 
```
- eg : au.Debug.Modulation.Filter.Buses CB_Music

![[UE_AudioDebug_Mix_ModulationMatrix.webp]]

---

# 3. Profiling

메모리 관련 리포트 출력
``` cpp fold title:Cmd
au.Debug.AduioMemReport
```
- 아래 사진과 같이 saved/profiling 경로 안에 로그 파일 생성

사진 : 로그 메세지
![[UE_AudioDebug_Profiling_Log.webp]]

![[UE_AudioDebug_ActiveSoundLists.webp]]
- 이와 같이 로그 파일을 통해 active 되었었던 모든 사운드를 확인할 수 있다

Audio cache overflow시 report에 에러 송출
``` cpp fold title:Cmd
au.streamcaching.SaveAudiomemReportOnCacheOverflow 1
```
- Audio Memreport에 추가됨

Stream cahcing profiling
``` cpp fold title:Cmd
au.Debug.AduioMemReport
```
- Audio Memreport에 추가됨

---

# 4. Links

더 자세한 정보는 링크 참고 - [UE Audio Console Commands](https://dev.epicgames.com/documentation/en-us/unreal-engine/audio-console-commands-in-unreal-engine)

---
