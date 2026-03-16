---
title: how to run python in docker
author: KurtJang
tags:
  - Blog
  - Python
  - n8n
date: 2026-02-24
draft: "False"
---

> [!info]  요약
> python을 docker에 올리고 이를 n8n(self-hosted) 에서 Http request로 실행하는 방법
> 

---
<font color="#68ff6e">Table of Contents</font>

1. [1. Docker setup](#1.%20Docker%20setup)
	1. [DockerFile](#DockerFile)
	2. [docker-compose.yml](#docker-compose.yml)
2. [2. Python setup](#2.%20Python%20setup)
	1. [main.py](#main.py)
	2. [test.py](#test.py)
3. [3. Test](#3.%20Test)

---
# 1. Docker setup

## DockerFile

- docker image를 생성을 위한 config

![[docker_python_DockerFile.png|700]]

**예제 코드**
```
# 1. 파이썬 경량 버전 사용
FROM python:3.9-slim

# 2. 작업 디렉토리 생성
WORKDIR /app

# 3. 라이브러리 목록 복사 및 설치
COPY requirements.txt .

# 이미지 빌드 시점에 설치하므로 속도가 매우 빠릅니다.
RUN pip install --no-cache-dir -r requirements.txt

# 4. 소스 코드 복사
COPY . .

# 5. 실행 환경 설정 (PATH 명시)
ENV PATH="/usr/local/bin:$PATH"

# 6. 기본 실행 명령
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

## docker-compose.yml

- docker 내의 container 를 정의하고 실행하기  config

![[docker_python_docker-compose.png|700]]

**예제 코드**
```
name: kurt-n8n  # folder Name

services:
  python-api: # 추후 http request 주소 eg : http://python-api:8000/user-register
    build: .
    image: python_n8n_automation_app:latest #image name
    container_name: python_n8n_automation   #container_name
    volumes:
      - .:/app

    ports:
      - "8000:8000"  # 호스트의 8000 포트를 컨테이너의 8000 포트로 매핑

    # 'python -m' 방식을 사용하면 모듈 인식 에러가 거의 발생하지 않습니다.
    command: python -m uvicorn main:app --host 0.0.0.0 --port 8000 --reload
    networks:
      - n8n_network

networks:
  n8n_network:
    external: true
    name: n8n_demo  # 'docker network ls'에서 확인하신 이름 그대로 사용하세요.
```


> [!NOTE] NOTE
> 같은 네트워크에 들어가야 http request가 가능하므로
> networks는 반드시 n8n과 실행한 container의 같은 네트워크 이름으로 구성해야 된다

---

# 2. Python setup

## main.py

![[docker_python_main.py.png|700]]

- FAST API를 활용하여 get/post 를 설정하고 그에 맞는 함수를 호출
- 함수는 별도의 python 파일로 관리하여 모듈성 강화


**예제 코드**
```
from fastapi import FastAPI
from pydantic import BaseModel
from test import test_post_handler, calculate_handler, user_info_handler

app = FastAPI()

# n8n에서 데이터를 보낼 때 받을 데이터 구조 정의
class Item(BaseModel):
    name: str
    message: str

class CalculateItem(BaseModel):
    num1: float
    num2: float
    operation: str  # "add", "subtract", "multiply", "divide"

class UserItem(BaseModel):
    name: str
    email: str
    age: int

@app.get("/") #http reuqest get
def read_root():
    return {"status": "ok", "info": "Python API is running inside Docker"}

@app.post("/n8n-test") #http request post
def test_post(item: Item):
    return test_post_handler(item)

@app.post("/calculate") #계산 API
def calculate(item: CalculateItem):
    return calculate_handler(item)

@app.post("/user-register") #사용자 등록 API
def register_user(item: UserItem):
    return user_info_handler(item)

```

## test.py

![[docker_python_test.py.png|700]]
- Test.py 에는 함수의 구현부가 들어가 있다
- main.py 가 일종의 header / test.py가 cpp 역할을 하게 된다

**에제 코드**
```
def test_post_handler(item) -> dict:
    return {
        "received_name": item.name,
        "processed_message": f"Hello! Your message '{item.message}' was received successfully."
    }

def calculate_handler(item) -> dict:
    """덧셈, 뺄셈 등 계산을 수행하는 함수"""
    num1 = item.num1
    num2 = item.num2
    operation = item.operation

    if operation == "add":
        result = num1 + num2
    elif operation == "subtract":
        result = num1 - num2
    elif operation == "multiply":
        result = num1 * num2
    elif operation == "divide":
        result = num1 / num2 if num2 != 0 else "Error: Division by zero"
    else:
        result = "Error: Unknown operation"

    return {
        "num1": num1,
        "num2": num2,
        "operation": operation,
        "result": result
    }

def user_info_handler(item) -> dict:
    """사용자 정보를 처리하는 함수"""
    return {
        "status": "success",
        "user_name": item.name,
        "user_email": item.email,
        "user_age": item.age,
        "message": f"User {item.name} registered successfully!"
    }

```

---

# 3. Test

- HTTP Request 호출
	- URL의 경우 docker-compose에서 services에서 이름 확인
	- 예시 (http://python-api:8000/user-register)
		- http://python-api:8000 : docker-compose 에서 적용된 service 이름/포트 적용
		- user-register : main.py에서 @aspp.post로 지정한 부분 적용


![[docker_python_n8n.png|700]]

예 : docker-compose.yml 예제
```

services:
  python-api: # 추후 http request 주소 eg : http://python-api:8000/user-register
    build: .
    image: python_n8n_automation_app:latest #image name
    container_name: python_n8n_automation   #container_name
    volumes:
      - .:/app

    ports:
      - "8000:8000"  # 호스트의 8000 포트를 컨테이너의 8000 포트로 매핑

```

- body parameter에 알맞은 파라미터를 작성해서 보내면 
  python으로  실행된 결과물을  output으로 받을 수 있다
---

