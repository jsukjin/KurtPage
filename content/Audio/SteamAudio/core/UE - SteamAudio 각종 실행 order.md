---
title: Untitled
author: KurtJang
tags:
  - Blog
date: 2026-07-14
draft: "False"
description: "요약"
---

---

# 1. Export Static Geometry 실행


**FSteamAudioEditorModule::OnExportStaticGeometry**

**FSteamAudioEditorModule:: ExportAllLevels**
- Async (wokerthread)
- eiditng level이 instanced level이면 
	- **FSteamAudioEditorModule::ExportSingleLevel**
- 아니면
	- **FSteamAudioEditorModule::ExportStaticGeometryForLevel** 호출 (async)

**SteamAudio::ExportStaticGeometryForLevel (in SteamAudioScene.cpp)**
- Async (worker thread) - workter thread에서 다른 worker thread 호출
- GetActorsForStaticGeometryExport (game thread)

**GetActorsForStaticGeometryExport (in SteamAudiosCene)**
- Async(worker thread) 
- TActorIteractor를 활용해서 StaticMeshComponent가 있다면 add
- 만약 USteamAudioSetting에서 bExportLandScapeGemoetry가 true이면 
	- ALandScape를 서치하고 이를 add

**ExportActors (in SteamAudioScene.cpp)**
- async (woker thread)
- StaticMeshActor 일경우
	- **ExportStaticMeshComponentsForActor** 실행
- Level (ALandScape) 일경우
	-  **ExportLandscapeActor** 실행

**ExportStaticMeshComponentsForActor (in SteamAudioScene)**
- Actor에서UStaticMesComponent를 모두 찾는다
- loop를 돌면서 Component마다 UStaticMesh를 찾는다
- Valid RenderData가 있다면 **ExportStaticMeshComponent** 실행

**ExportStaticMeshComponent (in SteamAudioScene)**
- Vertex
	- MinLODExport Idx 찾는다
	- FStaticMeshLODResources에 접근하여 FPositionVertexBuffer에 접근
	- static의 경우 좌표를 반영한 vertex를 저장 
		- static mesh의 경우 relative location만 알고 있어서 이를 world로 변환해서 저장
	- dynamic의 경우 그냥 저장하고 나중에 transform을 조정

- Index
	- FIndexArrayView에서 Index 정보 가져옴
	- Index정보를 토대로 IPLTriangle을 만들고 이를 저장

- Material
	- GetMaterialAssetForActor 을 호출
		- FBodyInstance를 찾아서 Setting에 있는 phys랑 대조하고 정보를 저장
		- ExportMaterial 호출
			- String가지고 기존에 집행했던 data에서 매치되는 USteamAudioMaterial 찾는다
			- 여기의 정보를 그대로 등록

 **ExportBSPGeometry (in SteamAudioScene.cpp)**
 - **ExportStaticMeshComponent 와 동일 (index, triangles)
	 - 다만 구조가 조금 다름

**FSteamAudioManagerInitializeSteamAudio**
- game thread
	- vertexes, indices가 다 준비되면 IPLScene 생성

- Scene 생성
	- 다만 Embree나 OpenCL등 맞게 scene이 생성될수 있음
		
	- HRTF initialization - **FSteamAudioManager::InitHRTF**
		- iplHRTFCreate

	- 생성된 IPLScene, IPLContext를 활용해서 수거한 index, vertex, triangles등을 저장
		- 저장때 IPLSerializedObject를 생성해서 저장

- **iplStaticMeshSave** (만약 obj export 할것이 아니면)

	- StaticMesh의 serializeAsRoot (core)
	- StaticMesh안에서 serailze 한이후 commit

- **USteamAudioSerializedObject::SerializeObjectToPackage**
- **ASteamAudioStaticMeshActor** 스폰 (정보를 가지고 있는 Actor)



# 2. Probe Volume (Generate Probe)





- IPLStaticMeshSettings 생성
- **iplStaticMeshCreate** 실행
- staticmesh를 serialize 하기 위해 **iplSerializedObjectCreate**
	- serializeObject 생성이후 잘 생성되면 **iplStaticMeshSave**
- **iplStaticMeshSave**
	- StaticMesh의 serializeAsRoot (core)
	- StaticMesh안에서 serailze 한이후 commit

- USteamAudioSerializedObject 에셋생성 (serailzed object랑 fileName 가지고)
- 이후 ASteamAudioStaticMeshActor 생성
	- IPLScene, IPLStaticMesh 보관용 Actor
- 이후 **iplSerializedObjectRelease** 실행
- **iplStaticMeshRelease** 실행








# 1. 제목









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