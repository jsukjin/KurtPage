---
title: how to run python in GCP
author: KurtJang
tags:
  - Blog
  - Python
  - Cloud
date: 2026-03-16
draft: "False"
---

> [!NOTE] 
> Goole Cloud Run을 활용한 python 실행

---
<br>
<strong><font color="#9fffa3">Table of Contents</font></strong>

1. [1. Google Cloud setup](#1-google-cloud-setup)
2. [2. Python setup](#2-python-setup)
3. [3. n8n](#3-n8n)
	1. [1. Authorization](#1-authorization)
4. [4. Test](#4-test)
	1. [1. GET](#1-get)
	2. [2. POST](#2-post)

<br>

---
# 1. Google Cloud setup


1. Colud Run 클릭 (검색창에서 clolud run 검색)

![[CloudRun_Search_CloudRun.webp|500]]


2.  create 실행
	- Execution envrionment
		- Default로 설정

![[CloudRun_Setup_01.webp|500]]


3. Enable required APIs
- 설정을 진행하다 보면 require API를 모두 enable 한다
`
![[CloudRun_Enable_CloudBuildAPI.webp|300]]
![[CloudRun_Enable_Required API.webp|300]]


4. Result  ^CloudUrl
- 등록이 완료되고 나면 URL 에 해당 코드를 실행할 수 있는 주소를 부여한다

![[ColudRun_Result.webp]]


---
# 2. Python setup

- GET / POST를 테스트하는 간단한 python 코드
- <font color="#f79646">VALID_AUTH_TOKEN 의 경우 header auth를 사용하기 위함</font>

``` python
import functions_framework
from flask import abort

  
# 실제 운영 시에는 이 값을 환경 변수 등으로 관리하는 것이 좋습니다.
VALID_AUTH_TOKEN = "your-secret-token-here"

  
@functions_framework.http
def hello_http(request):

    # 1. 인증 확인 (Header에서 Authorization 값을 가져옴)
    auth_header = request.headers.get('Authorization')
    
    # "Bearer your-secret-token-here" 형식인지 확인
    if not auth_header or auth_header != f"Bearer {VALID_AUTH_TOKEN}":

        # 인증 실패 시 401 Unauthorized 반환
        return abort(401, description="Unauthorized: Invalid or missing token.")


    # 2. 기존 로직 실행
    if request.method == 'GET':
        name = request.args.get('name', 'World')
        return f"Hello {name}! Auth Successful."

    elif request.method == 'POST':
        request_json = request.get_json(silent=True)
        name = request_json.get('name', 'Anonymous') if request_json else 'Anonymous'
        return {"message": f"Hello {name}! This was a secure POST request."}

    return abort(405)
```

---
# 3. n8n

## 1. Authorization

- 사용 목적 : 보안
- 사용 방법
	- Header Auth 및 TOKEN 설정
		(예 : name : Authorization , value : Bearer your-secret-token-here)
- n8n에 credential 설정으로 사전에 저장해두고 활용 가능

사진 : Header Auth 
![[CloudRun_HeaderAuth_Example.webp|700]]

---

# 4. Test

위의 python 파일을 실행시키기 위한 n8n GET/POST example

## 1. GET

- url : myURL [[#^CloudUrl]]
- Generic Auth Type : Header Auth
	- my header auth
- Send Query Parameters : true
	- JASON / Using Fields Below
		- name : name
		- value : your desired Value

## 2. POST

- url : myURL [[#^CloudUrl]]
- Generic Auth Type : Header Auth
	- my header auth
- Send Query Parameters : true
	- JASON / Using Fields Below
		- name : name
		- value : kurt (any test value)

---



