# AI 프롬프트 웹

FastAPI + React + OpenAI를 사용한 AI 프롬프트 대화 웹 애플리케이션

## 프로젝트 구조

```
.
├── backend/          # FastAPI 백엔드
│   ├── app/
│   │   ├── api/      # API 엔드포인트
│   │   ├── core/     # 설정, 보안
│   │   ├── models/   # 데이터베이스 모델
│   │   ├── schemas/  # Pydantic 스키마
│   │   └── services/ # 비즈니스 로직
│   └── alembic/      # 데이터베이스 마이그레이션
├── frontend/         # React + Vite 프론트엔드
│   └── src/
│       ├── components/  # React 컴포넌트
│       ├── pages/       # 페이지 컴포넌트
│       ├── services/    # API 서비스
│       └── store/       # Zustand 상태 관리
└── docker-compose.yml   # Docker Compose 설정
```

## 시작하기

### 1. 환경 변수 설정

프로젝트 루트에 `.env` 파일을 생성하고 다음 내용을 추가하세요:

```env
SECRET_KEY=your-secret-key-change-in-production-use-a-secure-random-string
OPEN_AI_KEY=your-openai-api-key-here
```

### 2. Docker Compose로 실행

```bash
docker-compose up --build
```

이 명령은 다음을 실행합니다:

- PostgreSQL 데이터베이스 (포트 5432)
- FastAPI 백엔드 (포트 8000)
- React 프론트엔드 (포트 5173)

### 3. 접속

- 프론트엔드: http://localhost:5173
- 백엔드 API: http://localhost:8000
- API 문서: http://localhost:8000/docs

## 기능

### 구현된 기능

- ✅ 사용자 회원가입
- ✅ 사용자 로그인
- ✅ JWT 기반 인증
- ✅ 보호된 라우트

### 예정된 기능

- ⏳ AI 프롬프트 대화
- ⏳ 대화 기록 관리
- ⏳ 프롬프트 템플릿

## 개발

### 백엔드 개발

```bash
cd backend
pip install -r requirements.txt
uvicorn app.main:app --reload
```

### 프론트엔드 개발

```bash
cd frontend
npm install
npm run dev
```

### 테스트 실행

백엔드 테스트를 실행하려면:

```bash
cd backend
pip install -r requirements.txt  # pytest 등 테스트 의존성 설치
pytest tests/ -v
```

또는 테스트 스크립트 사용:

```bash
cd backend
./run_tests.sh
```

#### 테스트 구조

- `tests/test_auth.py`: 인증 엔드포인트 테스트 (회원가입, 로그인)
- `tests/test_prompt.py`: 프롬프트 엔드포인트 테스트 (completion, chat)
- `tests/test_openai_service.py`: OpenAI 서비스 단위 테스트
- `tests/conftest.py`: 테스트 픽스처 및 설정

#### 도커 컨테이너 내에서 테스트 실행

**방법 1: 테스트 전용 컨테이너 사용 (권장)**

```bash
# 프로젝트 루트에서
docker-compose --profile test run --rm backend-test
```

**방법 2: 실행 중인 백엔드 컨테이너에서 테스트**

```bash
# 백엔드 컨테이너가 실행 중인 경우
docker exec ai_prompt_backend pytest tests/ -v

# 특정 테스트 파일만 실행
docker exec ai_prompt_backend pytest tests/test_prompt.py -v

# 특정 테스트 함수만 실행
docker exec ai_prompt_backend pytest tests/test_prompt.py::TestPromptEndpoints::test_completion_success -v
```

**방법 3: 테스트 스크립트 사용**

```bash
# 프로젝트 루트에서
cd backend
./docker-test.sh

# 옵션 사용
./docker-test.sh -f test_prompt.py -v          # 특정 파일 테스트
./docker-test.sh -k test_completion -v         # 키워드로 테스트 필터링
./docker-test.sh -f test_prompt.py -k success  # 파일과 키워드 조합
```

**방법 4: docker-compose exec 사용**

```bash
# 백엔드 서비스가 실행 중일 때
docker-compose exec backend pytest tests/ -v
```

## 기술 스택

### Backend

- FastAPI
- SQLAlchemy
- PostgreSQL
- JWT (python-jose)
- Alembic (마이그레이션)

### Frontend

- React 18
- TypeScript
- Vite
- Tailwind CSS
- Zustand
- TanStack Query
- React Router
