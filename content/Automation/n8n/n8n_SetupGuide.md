---
title: n8n Setup Guide
author: KurtJang
tags:
  - "#Books"
date: 2026-01-02
draft: "False"
---

> [!NOTE] 
> self hosted n8n setup guide

---
<font color="#68ff6e">Table of Contents</font>

- [1. Docker desktop 설치](#1-docker-desktop-%EC%84%A4%EC%B9%98)
- [2. Git repo 받기](#2-git-repo-%EB%B0%9B%EA%B8%B0)
- [3. ngrok 설치](#3-ngrok-%EC%84%A4%EC%B9%98)
	- [1. chocolatey](#1-chocolatey)
	- [2.ngrok 설치](#2ngrok-%EC%84%A4%EC%B9%98)
	- [3. config 설정](#3-config-%EC%84%A4%EC%A0%95)
- [3. n8n config 설정](#3-n8n-config-%EC%84%A4%EC%A0%95)
	- [1. config 파일 수정](#1-config-%ED%8C%8C%EC%9D%BC-%EC%88%98%EC%A0%95)
	- [2. env 파일 수정](#2-env-%ED%8C%8C%EC%9D%BC-%EC%88%98%EC%A0%95)
- [5. n8n 실행](#5-n8n-%EC%8B%A4%ED%96%89)
- [6. 결과](#6-%EA%B2%B0%EA%B3%BC)
- [6. Cmd](#6-cmd)


---
# 1. Docker desktop 설치

https://docs.docker.com/desktop/

---
#  2. Git repo 받기

self hosted n8n을 위한 kit 받기
- https://github.com/n8n-io/self-hosted-ai-starter-kit

---
# 3. ngrok 설치

## 1. chocolatey 설치

- 추후 web hook 사용을 위해 ngrok 설치가 필요
	- https://chocolatey.org/install

## 2.ngrok 설치

cmd 입력

``` cpp fold title:Cmd
choco install ngrok
```

## 3. config 설정

해당 url을 참고해서 config 설정
https://dashboard.ngrok.com/get-started/setup/windows

---
# 3. n8n config 설정

## 1. config 파일 수정
아래 cmd 내용을 x-n8n, services, n8n-import에 넣어준다 (git의 docker-compose.yaml)

``` cpp fold title:Cmd
 - WEBHOOK_TUNNEL_URL=${WEBHOOOK_TUNNEL_URL}
 - WEBHOOK_URL=${WEBHOOK_URL}
```

x-n8n
![[n8n_setup_kn8n.png|400]]

services
![[n8n_setup_services.png|400]]

n8n-import
![[n8n_setup_n8nimport.png|400]]

## 2. env 파일 수정
ngrok에서 받은 주소를 넣어준다 (.env 파일)
![[n8n_setup_subdomain.png]]

---
# 5. n8n 실행

1. docker에 실행
2. compose 실행 
- 예 : 아래 cmd 입력
``` cpp fold title:Cmd
docker compose up
```

3. ngrok 실행
- 예 : 아래 CMD 입력 (localhost 5678을 ngork 주소로 연결)
``` cpp fold title:Cmd
ngrok http 5678
```

---
# 6. 결과

 n8n이 실행된 결과를 확인할 수 있다
 ngrok 주소를 통해서 외부에서 접속 가능하다
![[n8n_setup_login.png]]

---
# 6. Cmd

docker 관련 cmd
``` cpp fold title:Cmd
// docker에 image 올리기
docker compose --profile cpu up

//docker에 image 올리기 (without log)
docker compose --profile cpu up -d

//docker에 image 내리기
docker compose down

//docker 재시작 (image 있는 상태에서 재식작)
docker compose restart

//docker에 실행중인 image 확인
docker ps

//compose 관련 로그
docker compose logs

//n8n server log를 실시간 확인
docker compose -f n8n
```


> [!info] Tip
> 개별 노드에 대한 정보는 youtube에 방대하게 있으니 참고

---


