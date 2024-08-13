# AI-MANAGER

## 프로젝트 개요

**AI-MANAGER**는 특정 갤러리의 게시물을 모니터링하고 부적절한 게시물이 있을 경우 디스코드 메세지를 보내는 프로젝트입니다. 

이 프로젝트는 Selenium을 이용한 웹 스크래핑, 머신러닝 모델을 이용한 예측, 그리고 Discord를 통한 알림 전송 기능을 포함하고 있습니다.

## 주요 기능

- **웹 스크래핑**: Selenium을 사용하여 보드에서 게시물을 탐색하고 스크랩합니다.
- **예측**: 머신 러닝 모델을 활용하여 주의가 필요한 게시글을 식별합니다.
- **알림**: 문제가 있는 게시물이 감지되면 Discord 채널로 경고를 보냅니다.
- **구성**: 구성 파일을 통해 사용자 지정할 수 있습니다.

## 설치 및 실행 방법

### 요구 사항

- Python 3.x
- Selenium
- BeautifulSoup4
- TensorFlow(또는 Keras)
- Requests
- WebDriver Manager

### 설치 및 실행

1. 저장소를 클론합니다.

   ```bash
   git clone https://github.com/yourusername/ai-manager.git
   cd ai-manager
   ```

2. ./start.sh에 실행 권한을 부여합니다.

   ```bash
   chmod +x shart.sh
   ```

3. 애플리케이션을 실행합니다.

   ```bash
   ./start.sh
   ```

## 개선할 점

현재 AI-MANAGER는 게시물 모니터링과 예측 기능만을 지원합니다. 추가적인 기능을 고려할 수 있습니다:

1. **모델 성능 개선**:
   - 머신러닝 모델을 업데이트하거나 재학습하여 예측 성능을 향상시킵니다.
   - 다양한 데이터로 모델을 테스트하고 튜닝합니다.

2. **알림 기능 개선**:
   - 알림 메시지를 더 정교하게 설정하여 사용자에게 더 유용한 정보를 제공합니다.
   - 예를 들어, 문제의 심각도에 따라 알림의 우선순위를 조정합니다.

## 문의

프로젝트와 관련된 문의는 [씨발님의 온라인 프로필](https://dcinside-ssibal.github.io/dcinside-ssibal-online-profile/)를 참고해주세요.


## 라이선스

이 프로젝트는 MIT 라이선스에 따라 배포됩니다. 자세한 내용은 LICENSE 파일을 참조하세요.
