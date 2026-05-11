---
title: How to run python in docker (cloud)
author: KurtJang
tags:
  - Blog
  - Python
  - n8n
  - Cloud
  - "#Docker"
date: 2026-03-16
draft: "False"
description: "Goole cloud docker에 python container를 생성하고 이를 n8n에서 실행하는 방법"
---
<br>
<strong><font color="#9fffa3">Table of Contents</font></strong>

1. [1. Cloud setup](#1-cloud-setup)
	1. [1.1 Docker setup](#11-docker-setup)
2. [2. Docker setup](#2-docker-setup)
	1. [1. Dockerfile](#1-dockerfile)
	2. [2. docker-compose.yml](#2-docker-composeyml)
	3. [3. requirements.txt](#3-requirementstxt)
	4. [4. main.py](#4-mainpy)
	5. [5. network setup](#5-network-setup)
	6. [6. cmd](#6-cmd)
3. [3. Test](#3-test)
	1. [1. GET](#1-get)
	2. [2. POST](#2-post)

<br>

---

# 1. Cloud setup

## 1.1 Docker setup

- 링크를 참고하여 docker setup
	- how to set up n8n (self-hosted) - [링크](https://jsukjin.github.io/Automation/n8n/n8n_SetupGudie-(Self-Hosted))
 
---
# 2. Docker setup

## 1. Dockerfile

- Docker setting 과 관련된 파일
```
FROM python:3.9-slim 

WORKDIR /app 

COPY requirements.txt . 
RUN pip install --no-cache-dir -r requirements.txt 

EXPOSE 5000 

CMD ["python", "main.py"]
```

## 2. docker-compose.yml

- compose setting 관련 파일
- **<font color="#f79646">networks 는 추후 설치된 n8n과 같은 네트워크에 있기 위하여 셋업한다</font>**
```                                
version: '3.8'

services:
  python_app:
    build: .
    container_name: hello-python-server
    ports:
      - "5000:5000"
    restart: always
    networks:
      - n8n_network

networks:
  n8n_network:
    external: true

```

## 3. requirements.txt

- 필요한 library 등록한다
```
# add more libraies 
flask
```

## 4. main.py

- GET/POST를 테스트할 수 있는 python 테스트 파일 올림
```
from flask import Flask, request, jsonify

app = Flask(__name__)

@app.route('/', methods=['GET', 'POST'])
def handle_requests():
    # 1. POST 요청 처리 (n8n 등에서 JSON 데이터를 보낼 때)
    if request.method == 'POST':
        data = request.get_json(silent=True) or {}
        
        # 'action'이라는 파라미터가 있는지 확인
        action = data.get('action')
        
        if action == 'search':
            return jsonify({
                "status": "success",
                "message": "검색 액션을 감지했습니다. search.py를 실행할 준비가 되었습니다!",
                "received_data": data
            }), 200
        elif action == 'test':
            return jsonify({"status": "success", "message": "테스트 모드입니다."}), 200
        else:
            return jsonify({"status": "error", "message": "알 수 없는 액션입니다.", "received_data": data}), 400

    # 2. GET 요청 처리 (브라우저 주소창 접속 등)
    else:
        # 주소창의 ?name=kurt 같은 파라미터 확인
        name = request.args.get('name')
        
        if name:
            return jsonify({
                "status": "success", 
                "message": f"안녕하세요 {name}님! 이름을 성공적으로 인식했습니다."
            }), 200
        else:
            return jsonify({
                "status": "waiting", 
                "message": "이름을 알려주세요. 주소 뒤에 ?name=이름 을 붙여보세요."
            }), 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
```


## 5. network setup

1. docker 정상작동 확인
	- 정상일 경우 status 에 up 확인 가능
```
docker ps # 현재 실행중인 docker 의 상태 확인
```

2. network 설정
```
# 불필요한 network 삭제
docker network prune -f

# n8n_network란 network 생성
docker network create n8n_network

# n8n_network 상태 보기
docker network inspect n8n_network

```

3. test code 실행
	- n8n 에 접속하기 전에 terminal에서 아래의 코드로 test 가능
```
curl -X POST http://localhost:5000/post \
     -H "Content-Type: application/json" \
     -d '{"name": "Kurt", "status": "success"}'
```

## 6. cmd

```
# 기존의 docker를 내려준다
dpocker compose down

# docker 를 새롭게 올린다
docker compose up -d

# 만약 python 코드가 변경되어 re-build 해야할 경우
docker compose up --build -d

# ngrok 기존연결 삭제
pkill ngrok

# ngrok 연결
nohup ngrok http --domain=[MY_NGROK_ADDRESS] 5678 > ngrok.log 2>&1 &
```


---

# 3. Test

다음과 같은 방식으로 테스트 진행
- URL의 경우 container name + port 로 지정됨
	- 예 : http://hello-python-server:5000/

## 1. GET

- URL : my_url 
	- Authentication : None
	- Send Query Parameters : true
		- Sepcify Query Parameters : Using Fields Below
			- name  : name 
			- value : my name

## 2. POST

- URL : my_url
- Authentication : None
- Send body : true
	- JSON / Using Fields Below
		- name : action
		- value : search

---
