#!/bin/bash

# 가상환경이 설치된 경로로 이동
cd /home/ubuntu/ai-manager || exit

# 가상환경 활성화
source ai-manager/bin/activate

# Python 스크립트 실행
python main.py

# 가상환경 비활성화
deactivate
