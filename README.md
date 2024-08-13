AI-MANAGER
==========

개요
----
AI-MANAGER는 특정 마이너 갤러리의 게시물을 모니터링하고, 부적절하다고 판단되는 게시물 발견 시 알림을 보내는 프로젝트입니다.

주요 기능
---------
- Selenium을 이용한 웹 스크래핑
- 머신러닝 모델을 활용한 게시물 예측
- Discord를 통한 실시간 알림 전송

핵심 특징
---------
1. 웹 스크래핑: Selenium으로 게시판 글 자동 탐색 및 수집
2. 예측 분석: 머신 러닝 모델로 주의 필요 게시글 식별
3. 알림 시스템: 문제성 게시물 감지 시 Discord로 즉시 경고
4. 유연한 설정: 사용자 지정 가능한 구성 파일 제공

시스템 요구사항
---------------
- Python 3.x
- Selenium
- BeautifulSoup4
- TensorFlow (또는 Keras)
- Requests
- WebDriver Manager
- Discord 웹훅 (선택사항)

설정 가이드
------------

3. Dcinside 계정 설정 (config/account.txt):
   YOUR_ACCOUNT_ID
   YOUR_ACCOUNT_PASSWD

4. Discord 웹훅 설정 (config/discord.txt):
   DISCORD_WEBHOOK_URL=YOUR_DISCORD_WEBHOOK_URL

빠른 시작 가이드
----------------
1. 프로젝트 복제:
   git clone https://github.com/dcinside-ssibal/ai-manager.git
   cd ai-Manager

2. 실행 권한 부여:
   chmod +x start.sh

3. 프로그램 실행:
   ./start.sh

커스터마이징 옵션
-----------------
- 모니터링 주기: monitor_new_posts 함수에서 시간 간격 조정 (기본 5분)
- 예측 정확도: 모델 업데이트 또는 재학습으로 성능 개선

트러블슈팅
----------
- 알림 문제: 모델 학습 상태와 예측 기능 점검
- 설정 오류: 구성 파일 내용 재확인
- 스크래핑 이슈: WebDriver와 스크래핑 로직 업데이트 확인

라이선스
--------
MIT 라이선스 적용. 상세 내용은 LICENSE 파일 참조.

문의 및 지원
------------
기술 지원 및 문의: https://dcinside-ssibal.github.io/dcinside-ssibal-online-profile/