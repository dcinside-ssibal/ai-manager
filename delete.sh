#!/bin/bash

# 파일을 삭제할 디렉토리 설정
TARGET_DIR="."

# 제외할 파일 확장자 및 디렉토리 설정
EXCLUDE_PATTERNS=("*.py" "*.txt" ".git" ".gitignore" "*.sh")

# 삭제할 파일 및 디렉토리 리스트
delete_files() {
    find "$TARGET_DIR" -type f | while read -r file; do
        # 제외할 패턴과 일치하지 않는 파일 삭제
        skip=false
        for pattern in "${EXCLUDE_PATTERNS[@]}"; do
            if [[ "$file" == *$pattern ]]; then
                skip=true
                break
            fi
        done
        if [ "$skip" = false ]; then
            rm "$file"
        fi
    done
}

delete_directories() {
    find "$TARGET_DIR" -type d | while read -r dir; do
        # 제외할 패턴과 일치하지 않는 디렉토리 삭제
        skip=false
        for pattern in "${EXCLUDE_PATTERNS[@]}"; do
            if [[ "$dir" == *$pattern ]]; then
                skip=true
                break
            fi
        done
        if [ "$skip" = false ] && [ "$dir" != "$TARGET_DIR" ]; then
            rm -r "$dir"
        fi
    done
}

# 삭제 실행
delete_files
delete_directories

echo "Cleanup complete."
