#!/bin/bash

# 변수 설정
VENV_DIR="ai-manager"
REQUIREMENTS_FILE="requirements.txt"

# 가상환경 생성
if [ ! -d "$VENV_DIR" ]; then
    python3 -m venv $VENV_DIR
fi

# 가상환경 활성화
source $VENV_DIR/bin/activate

# 패키지 설치
if [ -f "$REQUIREMENTS_FILE" ]; then
    pip install --upgrade pip -q
    pip install -r $REQUIREMENTS_FILE -q
else
    echo "Requirements file not found."
    exit 1
fi

# WebDriver Manager 설치
pip install webdriver-manager -q

# ChromeDriver 설치 및 경로 확인
python3 -c "from webdriver_manager.chrome import ChromeDriverManager; ChromeDriverManager().install()"

# main.py 실행
echo "Starting program..."
python3 main.py

echo "Setup complete."
