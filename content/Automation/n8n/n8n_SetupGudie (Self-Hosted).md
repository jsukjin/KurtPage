---
title: n8n setup guide (self-hosted)
author: KurtJang
tags:
  - "#Blog"
date: 2026-01-02
draft: "False"
---

> [!NOTE] Summary
> setup guide for self-hosted n8n

---
<font color="#68ff6e">Table of Contents</font>

1. [1. Docker desktop 설치](#1.%20Docker%20desktop%20%EC%84%A4%EC%B9%98)
2. [2. Git repo 받기](#2.%20Git%20repo%20%EB%B0%9B%EA%B8%B0)
3. [3. ngrok 설치](#3.%20ngrok%20%EC%84%A4%EC%B9%98)
	1. [1. chocolatey](#1.%20chocolatey)
	2. [2.ngrok](#2.ngrok)
	3. [3. env 파일 설정](#3.%20env%20%ED%8C%8C%EC%9D%BC%20%EC%84%A4%EC%A0%95)
4. [3. n8n config 설정](#3.%20n8n%20config%20%EC%84%A4%EC%A0%95)
	1. [1. config 파일 수정](#1.%20config%20%ED%8C%8C%EC%9D%BC%20%EC%88%98%EC%A0%95)
	2. [2. env 파일 수정](#2.%20env%20%ED%8C%8C%EC%9D%BC%20%EC%88%98%EC%A0%95)
5. [5. n8n 실행](#5.%20n8n%20%EC%8B%A4%ED%96%89)
6. [6. 결과](#6.%20%EA%B2%B0%EA%B3%BC)
7. [6. docker cmd](#6.%20docker%20cmd)



---
# 1. Docker desktop 설치

1. 다운로드 및 설치
- https://docs.docker.com/desktop/

---
#  2. Git repo 받기

1. git clone (self hosted kit)
- https://github.com/n8n-io/self-hosted-ai-starter-kit

---
# 3. ngrok 설치

## 1. chocolatey

1. 추후 web hook 사용을 위해 ngrok 설치가 필요
	- https://chocolatey.org/install
	- Powershell 실행을 '관리자 권한'으로

## 2.ngrok

1. ngrok 설치
	- cmd에 아래 입력 (ngrok 설치)

``` cpp fold title:Cmd
choco install ngrok
```

2. token 발급 및 적용
	- https://dashboard.ngrok.com/get-started/your-authtoken

![[n8n_ngrok_token.png|450]]

## 3. env 파일 설정

1. env.exmaple -> env로 이름을 수정하고 안에 id/pw 수정해준다

![[n8n_내부.png|450]]


---
# 3. n8n config 설정

## 1. config 파일 수정

- 아래 cmd 내용을 x-n8n, services, n8n-import에 넣어준다
- 파일 : docker-compose.yaml


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
- ngrok에서 받은 주소를 넣어준다 
- 파일 : .evn 파일

![[n8n_setup_subdomain.png|450]]

---
# 5. n8n 실행

1. docker에 실행
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

![[n8n_setup_login.png|400]]

- ngrok에서 제공하는 주소를 통해 n8n에 접속이 가능하다


![[n8n_actvation.png|400]]
- 이후 settings에서 activation을 진행

---
# 6. docker cmd

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


