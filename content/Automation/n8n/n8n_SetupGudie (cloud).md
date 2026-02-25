---
title: n8n setup (cloud)
author: KurtJang
tags:
  - Blog
date: 2026-02-06
draft: "False"
---

> [!NOTE] Summary
> setup guide for n8n in google cloud

---
<font color="#68ff6e">Table of Contents</font>

1. [1. Google Cloud Setup](#1.%20Google%20Cloud%20Setup)
	1. [A. Project / Virtual Machine Setup](#A.%20Project%20/%20Virtual%20Machine%20Setup)
	2. [B. Configuration](#B.%20Configuration)
		1. [Machine Configuration](#Machine%20Configuration)
		2. [OS and Storage](#OS%20and%20Storage)
		3. [Networking](#Networking)
		4. [FireWall](#FireWall)
2. [2. Docker / n8n setup](#2.%20Docker%20/%20n8n%20setup)
3. [3. Config](#3.%20Config)

---
# 1. Google Cloud Setup

## A. Project / Virtual Machine Setup

1. https://cloud.google.com/
2. Console 클릭

![[n8n_cloud_GoogleCloud.png|450]]

3. 'My Project' 클릭해서 project 생성 (1번)
4. Virtual machine 생성 (2번)

![[n8n_cloud_setup_01.png|450]]

5. "Compute Engine API" 에서 Enable 클릭

![[n8n_cloud_setup_02.png|450]]

---
## B. Configuration

Free Tier 조건에 맞추기 위하여 다음과 같이 설정한다
	- https://docs.cloud.google.com/free/docs/free-cloud-features?hl=ko

### Machine Configuration

- **Region : US West**
- **Zone : Any**
- **Series : E2**

![[n8n_cloud_machine_configuration.png|450]]

### OS and Storage

- **Operation System : Ubuntu**
- **HDD : 30 GB**

![[n8n_cloud_setup_OsAndStorage.png|450]]

### Networking

- Allow HTTP traffic - tick
- Allow HTTPS traffic - tick
- Allow Load Balancer Health Checks - tick

![[n8n_cloud_setup_Networking.png|450]]

### FireWall
1. Firewall rule 생성
	- http 접속을 가능하게 하기 위하여 rule 생성
	- 추후에는 https로 접속 가능해지면 제거

![[n8n_cloud_setup_NetworkDetails.png|450]]
- view network details / 네트워크 세부정보 보기 클릭

![[n8n_cloud_setup_CreateVPCFireWall.png|450]]
- 'Create VPC firewall rule' 클릭

![[n8n_cloud_setup_FireWallSetup_Detail.png|450]]
- **Source ranges : 0.0.0.0/0**
- **Speicifed protocols and ports**
	- **TCP  :allow**
	- **Ports : 5678**


---
# 2. Docker / n8n setup

1. SSH 접속
- open in broswer window 또는 SSH 클릭

![[n8n_cloud_setup_SSH.png|500]]

2. Docker 설치
- 가이드 참고
- https://docs.docker.com/engine/install/ubuntu/

3. n8n 설치
- 커멘드를 잘 복사/붙여넣기 하자 (여기서 많이 시간 소비함)
- https://docs.n8n.io/hosting/installation/docker/#using-with-postgresql

---
# 3. Config

모든 설치가 진행되고 실행하면 다음과 같은 에러 메세지가 나오는데
이는 'http'를 활용하기 때문에 발생되는 문제이다

![[n8n_cloud_setup_HTTPError.png|400]]

- Seure 옵션을 강제로 false 함으로써 http에서 로딩이 가능하다 (아래 cmd 실행)
	- '**-e N8N_SECURE_COOKIE=false**'
``` 
sudo docker run -it --rm --name n8n -p 5678:5678 -v n8n_data:/home/node/.n8n -e N8N_SECURE_COOKIE=false docker.n8n.io/n8nio/n8n
```

하지만 webhook 사용을 위하여 https로 로그인이 필요하기에 
도메인 등록 및 https 인증작업을 진행이 필요하다
추후 https 문제가 해결되는 대로 내용 업로드 예정

---
