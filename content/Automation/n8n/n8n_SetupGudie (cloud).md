---
title: n8n setup (cloud)
author: KurtJang
tags:
  - Blog
  - n8n
date: 2026-02-06
draft: "False"
description: setup guide for n8n in google cloud
---

---
# 1. Google Cloud Setup

## A. Project / Virtual Machine Setup

1. https://cloud.google.com/
2. Console 클릭

![[n8n_cloud_GoogleCloud.webp|450]]

3. 'My Project' 클릭해서 project 생성 (1번)
4. Virtual machine 생성 (2번)

![[n8n_cloud_setup_01.webp|450]]

5. "Compute Engine API" 에서 Enable 클릭

![[n8n_cloud_setup_02.webp|450]]

---
## B. Configuration

Free Tier 조건에 맞추기 위하여 다음과 같이 설정한다
	- https://docs.cloud.google.com/free/docs/free-cloud-features?hl=ko

### Machine Configuration

- **Region : US West**
- **Zone : Any**
- **Series : E2**

![[n8n_cloud_machine_configuration.webp|450]]

### OS and Storage

- **Operation System : Ubuntu**
- **HDD : 30 GB**

![[n8n_cloud_setup_OsAndStorage.webp|450]]

### Networking

- Allow HTTP traffic - tick
- Allow HTTPS traffic - tick
- Allow Load Balancer Health Checks - tick

![[n8n_cloud_setup_Networking.webp|450]]

### FireWall
1. Firewall rule 생성
	- http 접속을 가능하게 하기 위하여 rule 생성
	- 추후에는 https로 접속 가능해지면 제거

![[n8n_cloud_setup_NetworkDetails.webp|450]]
- view network details / 네트워크 세부정보 보기 클릭

![[n8n_cloud_setup_CreateVPCFireWall.webp|450]]
- 'Create VPC firewall rule' 클릭

![[n8n_cloud_setup_FireWallSetup_Detail.webp|450]]
- **Source ranges : 0.0.0.0/0**
- **Speicifed protocols and ports**
	- **TCP  :allow**
	- **Ports : 5678**


---
# 2. Docker setup

1. SSH 접속
- open in broswer window 또는 SSH 클릭

![[n8n_cloud_setup_SSH.webp|500]]

2. 폴더 생성/권한
```
# 폴더생성 및 이동
mk dir -p /n8n/data
cd ~/n8n

# 권한 
# 1000:1000 - [사용자ID]:[그룹ID] 
sudo chown -R 1000:1000 ~/n8n/data

```

3. compose 파일 생성
```
# nano 설치 (text editor)
sudo apt install -y nano

# compose 파일 생성
nano docker-compose.yml #파일 생성
```

4. docker-compose.yml 예제
	- YOUR_NGROK_DOMAIN에 발급받은 도메인 넣기
```
version: "3.8" 
services: 
	n8n: 
		image: n8nio/n8n:latest 
		container_name: n8n 
		restart: unless-stopped 
		ports: - "127.0.0.1:5678:5678" # 외부 IP로 직접 접근 차단 
		environment: 
			- N8N_HOST=YOUR_NGROK_DOMAIN 
			- N8N_PORT=5678 - N8N_PROTOCOL=https 
			- WEBHOOK_URL=https://YOUR_NGROK_DOMAIN 
			- GENERIC_TIMEZONE=Asia/Seoul 
			- N8N_EDITOR_BASE_URL=https://YOUR_NGROK_DOMAIN 
			- N8N_SECURE_COOKIE=false #세션/쿠키 문제 해결 
			- N8N_PROXY_HOPS=1 #ngrok 프록시 경유 시 rate-limit 오작동 방지 
			- N8N_ENCRYPTION_KEY=YOUR_OPENSSL_RAND_HEX_32 #암호화키 고정
			  
		 volumes: - ./data:/home/node/.n8n
```


참고 자료
- https://docs.docker.com/engine/install/ubuntu/
- https://docs.n8n.io/hosting/installation/docker/#using-with-postgresql


---
# 3. Ngrok setup

1. Auth Token 등록

```
# auth-token 등록
ngrok config add-authtoken [YOUR_AUTH_TOKEN]
```

2.  ngrok 실행
	- YOUR_NGROK_DOMAIN에 받은 domain 등록
```
nohup ngrok http --domain=YOUR_NGROK_DOMAIN 5678 > /dev/null 2>&1 &
```



---
# 4. Result
- setup owner가 뜨며 성공됨을 알 수 있다

![[n8n_setup_login.webp|300]]


```
# docker에 n8n 실행
docker compose up -d

# docker에 n8n 실행 (리빌드이후)
docker compose up --build -d

# ngrok 설정
nohup ngrok http --domain=YOUR_NGROK_DOMAIN 5678 > /dev/null 2>&1 &

# ngrok 설정 해제
pkill ngrok

# docker에 n8n 내림
docker compose down
```


---
