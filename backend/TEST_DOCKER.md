# 도커 컨테이너 내에서 테스트 실행 가이드

## 개요

이 문서는 도커 컨테이너 내에서 백엔드 테스트를 실행하는 다양한 방법을 설명합니다.

## 방법 1: 테스트 전용 컨테이너 사용 (권장)

가장 깔끔한 방법으로, 테스트만을 위한 별도 컨테이너를 실행합니다.

```bash
# 프로젝트 루트에서
docker-compose --profile test run --rm backend-test
```

**장점:**

- 기존 서비스에 영향을 주지 않음
- 깨끗한 환경에서 테스트 실행
- 테스트 후 자동으로 컨테이너 제거 (`--rm`)

## 방법 2: 실행 중인 백엔드 컨테이너에서 테스트

백엔드 서비스가 이미 실행 중인 경우, 해당 컨테이너에서 직접 테스트를 실행할 수 있습니다.

```bash
# 전체 테스트 실행
docker exec ai_prompt_backend pytest tests/ -v

# 특정 테스트 파일만 실행
docker exec ai_prompt_backend pytest tests/test_prompt.py -v

# 특정 테스트 함수만 실행
docker exec ai_prompt_backend pytest tests/test_prompt.py::TestPromptEndpoints::test_completion_success -v

# 키워드로 필터링
docker exec ai_prompt_backend pytest tests/ -k "test_completion" -v
```

**장점:**

- 빠른 실행 (컨테이너가 이미 실행 중)
- 코드 변경사항이 볼륨 마운트로 반영됨

## 방법 3: docker-compose exec 사용

docker-compose를 통해 실행 중인 서비스에서 테스트를 실행합니다.

```bash
# 프로젝트 루트에서
docker-compose exec backend pytest tests/ -v

# 특정 파일만
docker-compose exec backend pytest tests/test_prompt.py -v
```

**장점:**

- docker-compose 환경 변수 자동 적용
- 서비스 간 네트워크 연결 활용 가능

## 방법 4: 테스트 스크립트 사용

편리한 스크립트를 사용하여 테스트를 실행합니다.

```bash
# 프로젝트 루트에서
cd backend
./docker-test.sh

# 옵션 사용
./docker-test.sh -f test_prompt.py -v          # 특정 파일 테스트
./docker-test.sh -k test_completion -v         # 키워드로 테스트 필터링
./docker-test.sh -f test_prompt.py -k success   # 파일과 키워드 조합
./docker-test.sh -e                             # 실행 중인 컨테이너 사용
./docker-test.sh --help                         # 도움말 보기
```

## 테스트 옵션

pytest의 다양한 옵션을 사용할 수 있습니다:

```bash
# 상세 출력
docker exec ai_prompt_backend pytest tests/ -v

# 매우 상세한 출력
docker exec ai_prompt_backend pytest tests/ -vv

# 특정 패턴의 테스트만 실행
docker exec ai_prompt_backend pytest tests/ -k "test_completion"

# 특정 마커로 필터링
docker exec ai_prompt_backend pytest tests/ -m "not slow"

# 커버리지 리포트 생성
docker exec ai_prompt_backend pytest tests/ --cov=app --cov-report=html

# 실패한 테스트만 재실행
docker exec ai_prompt_backend pytest tests/ --lf
```

## 주의사항

1. **데이터베이스**: 테스트는 SQLite 인메모리 데이터베이스를 사용하므로 PostgreSQL이 실행 중이 아니어도 됩니다.

2. **환경 변수**: 테스트 전용 컨테이너는 `OPENAI_API_KEY`가 없어도 Mock을 사용하므로 정상 작동합니다.

3. **볼륨 마운트**: 코드 변경사항은 볼륨 마운트를 통해 자동으로 반영됩니다.

4. **컨테이너 재시작**: 코드 변경 후 컨테이너를 재시작할 필요는 없지만, 새로운 패키지 설치가 필요한 경우 이미지를 다시 빌드해야 합니다.

## 문제 해결

### 컨테이너를 찾을 수 없음

```bash
# 컨테이너 상태 확인
docker ps -a | grep ai_prompt

# 컨테이너 시작
docker-compose up -d backend
```

### 테스트가 실패함

```bash
# 상세한 에러 메시지 확인
docker exec ai_prompt_backend pytest tests/ -vv --tb=long

# 특정 테스트만 실행하여 디버깅
docker exec ai_prompt_backend pytest tests/test_prompt.py::TestPromptEndpoints::test_completion_success -vv
```

### 패키지가 설치되지 않음

```bash
# 이미지 재빌드
docker-compose build backend

# 또는 테스트 컨테이너만 재빌드
docker-compose build backend-test
```
