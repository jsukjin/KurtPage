---
title: ReadMe
author: KurtJang
tags:
  - "#Blog"
date: 2025-12-31
draft: "true"
description: "요약"
---
<font color="#92d050">Table Of Contents</font>

- [Table of Contents](#table-of-contents)
- [ETC](#etc)
	- [Installed plugin list](#installed-plugin-list)

---

# How To Setup

1. Git clone
``` cpp fold title:Cmd
// git clone (kurtPage)
git congit@github.com:jsukjin/KurtPage.git
```

2. Node.js Install (없을 경우)
- https://nodejs.org/en/download

2. Create Quartz
- https://quartz.jzhao.xyz
``` cpp fold title:Cmd
// git clone
git clone (mygit)

// npm install
npm i

//create quartz
npx quartz create

```

4. Git Setup
- https://quartz.jzhao.xyz/setting-up-your-GitHub-repository
``` cpp fold title:Cmd
//list all the repositories that are trackedgit 
git remote -v

//if the origin doesn't match your own repository, 
//set your repository as the origin
git remote set-url origin REMOTE-URL

//if you don't have upstream as a remote, add it so updates work
git remote add upstream https://github.com/jackyzha0/quartz.git

```

- 셋업 이후 git remote -v를 통해 아래와 같이 origin / upstream 이 셋업됨을 확인
![[quartz_setup_git_result.png|300]]
---

# Trouble Shooting

## quartz sync 가 안될때 (ssh로 인한 문제)

### 1단계: 기존의 꼬인 키 정리 (선택 사항)

`.ssh` 폴더에 이미 만든 파일들이 있다면, 헷갈리지 않게 삭제하거나 다른 폴더로 옮겨두는 것이 좋습니다.

### 2단계: Quartz용 SSH 키 생성

1. **터미널(PowerShell 또는 CMD)**을 엽니다.
    
2. 아래 명령어를 복사해서 붙여넣고 엔터를 치세요: 

```
ssh-keygen -t ed25519 -C "본인의_깃허브_이메일@example.com"
```


3. **중요:** 질문이 세 번 나오는데, **아무것도 입력하지 말고 엔터만 세 번** 치세요.
    - `Enter file in which to save the key`: 엔터 (기본 경로 저장)
    - `Enter passphrase`: 엔터 (비밀번호 생략)
    - `Enter same passphrase again`: 엔터
        
### 3단계: 생성된 키 확인 및 복사

이제 터미널이 인식할 수 있는 표준 이름(`id_ed25519`)으로 키가 만들어졌습니다.

1. 터미널에 아래 명령어를 입력해 **공개키** 내용을 출력합니다: `cat ~/.ssh/id_ed25519.pub` _(만약 `cat` 명령어가 안 되면 메모장으로 `C:\Users\jsukjin\.ssh\id_ed25519.pub` 파일을 여세요.)_
    
2. `ssh-ed25519 AAAAC3...`으로 시작하는 **전체 문장을 복사**합니다.
    
### 4단계: GitHub에 새 키 등록

1. **GitHub 접속** → 우측 상단 프로필 클릭 → **Settings**.
2. 왼쪽 메뉴에서 **SSH and GPG keys** 클릭.
3. **New SSH Key** 버튼 클릭.
4. **Title**에는 `Quartz Key`라고 적고, **Key** 칸에 복사한 내용을 붙여넣은 뒤 **Add SSH Key**를 누릅니다.
    
### 5단계: 최종 연결 테스트

Quartz를 실행하기 전에 터미널에서 연결이 잘 되는지 확인합니다.

1. 터미널에 입력: `ssh -T git@github.com`
```
`ssh -T git@github.com`
```

2. `Are you sure you want to continue connecting (yes/no/[fingerprint])?` 
   라고 나오면 **`yes`**라고 입력하고 엔터를 칩니다.
    
3. **"Hi [본인아이디]! You've successfully authenticated..."** 메시지가 나오면 성공입니다!

---

# ETC
## Installed plugin list

- Excalidraw
- DataView
- Templater
- Advanced Tables
- Editing Toolbar
- Recent Files
- Table of Contents
- Automatic Table of Contents
- Code Styler
- Image Converter

---