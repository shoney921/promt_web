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
TAVILY_API_KEY=your-tavily-api-key-here  # 선택적: 웹 검색 기능 사용 시 필요
```

**Tavily API Key 발급 방법:**

1. [Tavily 웹사이트](https://tavily.com)에 가입
2. 무료 티어로 시작 가능 (월 1,000회 검색)
3. API Key를 발급받아 `.env` 파일에 추가
4. API Key가 없어도 기본 AI 기능은 정상 작동 (검색 기능만 비활성화)

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
- ✅ AI 프롬프트 대화 (스트리밍 지원)
- ✅ 대화 기록 관리
- ✅ 웹 검색 기능 (Tavily Search 통합)
  - LLM이 필요할 때 자동으로 웹 검색 수행
  - 최신 정보 및 실시간 데이터 검색 지원

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
- Langchain (OpenAI 통합, Agent)
- Tavily Search (웹 검색)

### Frontend

- React 18
- TypeScript
- Vite
- Tailwind CSS
- Zustand
- TanStack Query
- React Router

---

## 프로덕션 인프라

### 아키텍처 개요

로컬 PC에서 Docker로 서비스를 실행하고, Cloudflare Tunnel을 통해 외부에서 접속할 수 있습니다.

```
┌─────────────────────────────────────────────────────────────────────────┐
│                              인터넷                                      │
└────────────────────────────────┬────────────────────────────────────────┘
                                 │
                                 ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                     Cloudflare Edge Network                              │
│  ┌─────────────────────────────────────────────────────────────────┐    │
│  │  prompt.shoneylife.com                                           │    │
│  │  • SSL/TLS 종료 (자동 인증서)                                     │    │
│  │  • DDoS 보호                                                      │    │
│  │  • CDN 캐싱                                                       │    │
│  └─────────────────────────────────────────────────────────────────┘    │
└────────────────────────────────┬────────────────────────────────────────┘
                                 │ Cloudflare Tunnel (암호화)
                                 ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                        로컬 PC (Docker)                                  │
│  ┌──────────────────────────────────────────────────────────────────┐   │
│  │                    Docker Network: internal                       │   │
│  │                                                                   │   │
│  │   ┌─────────────┐     ┌─────────────┐     ┌─────────────┐        │   │
│  │   │ cloudflared │────►│   nginx     │────►│  backend    │        │   │
│  │   │             │     │   :80       │     │   :8000     │        │   │
│  │   └─────────────┘     └──────┬──────┘     └──────┬──────┘        │   │
│  │                              │                    │               │   │
│  │                              │                    ▼               │   │
│  │                              │            ┌─────────────┐        │   │
│  │                              │            │  postgres   │        │   │
│  │                              │            │   :5432     │        │   │
│  │                              │            └─────────────┘        │   │
│  │                              │                                   │   │
│  │                              ▼                                   │   │
│  │                       정적 파일 서빙                              │   │
│  │                    (React 빌드 결과물)                            │   │
│  │                                                                   │   │
│  └──────────────────────────────────────────────────────────────────┘   │
│                                                                          │
│  호스트 노출 포트: 80 (nginx)                                            │
│  외부 미노출: postgres (5432), backend (8000)                            │
└─────────────────────────────────────────────────────────────────────────┘
```

### 네트워크 흐름 상세

```
요청 흐름 (외부 → 내부)
═══════════════════════════════════════════════════════════════════════════

1. 사용자 브라우저
   │
   │  HTTPS 요청: https://prompt.shoneylife.com/api/v1/chat
   ▼
2. Cloudflare Edge (서울 PoP)
   │  • SSL 종료
   │  • 보안 검사
   │  • 요청을 Tunnel로 전달
   ▼
3. cloudflared 컨테이너
   │  • Cloudflare와 암호화된 연결 유지
   │  • 요청을 nginx:80으로 프록시
   ▼
4. nginx 컨테이너 (:80)
   │  • 경로 기반 라우팅:
   │    - /api/*  → backend:8000
   │    - /health → backend:8000/health
   │    - /*      → 정적 파일 (React)
   ▼
5. backend 컨테이너 (:8000)
   │  • FastAPI 처리
   │  • OpenAI API 호출
   ▼
6. postgres 컨테이너 (:5432)
      • 데이터 저장/조회
```

### 컨테이너별 역할

| 컨테이너 | 이미지 | 내부 포트 | 호스트 포트 | 역할 |
|---------|--------|----------|------------|------|
| **postgres** | postgres:15-alpine | 5432 | - (미노출) | PostgreSQL 데이터베이스 |
| **backend** | Dockerfile.prod | 8000 | - (미노출) | FastAPI 서버 (4 workers) |
| **nginx** | Dockerfile.prod | 80 | 80 | 리버스 프록시 + 정적 파일 |
| **cloudflared** | cloudflare/cloudflared | - | - | Cloudflare Tunnel 클라이언트 |

### Nginx 라우팅 규칙

```
location /api/         → proxy_pass http://backend:8000
location /health       → proxy_pass http://backend:8000/health
location /docs         → proxy_pass http://backend:8000/docs
location /openapi.json → proxy_pass http://backend:8000/openapi.json
location /             → React 정적 파일 (SPA 라우팅)
```

### 프로덕션 실행

```bash
# 1. 환경변수 설정
cp .env.example .env.production
# .env.production 파일에서 API 키와 토큰 설정

# 2. 프로덕션 실행
docker-compose -f docker-compose.prod.yml --env-file .env.production up --build -d

# 3. 상태 확인
docker-compose -f docker-compose.prod.yml --env-file .env.production ps

# 4. 로그 확인
docker-compose -f docker-compose.prod.yml --env-file .env.production logs -f

# 5. 중지
docker-compose -f docker-compose.prod.yml --env-file .env.production down
```

### 접속 URL

| 환경 | URL |
|------|-----|
| 프로덕션 (외부) | https://prompt.shoneylife.com |
| 로컬 테스트 | http://localhost |
| API 문서 | https://prompt.shoneylife.com/docs |
| 헬스체크 | https://prompt.shoneylife.com/health |

### Cloudflare Tunnel 설정 요약

1. **Cloudflare Zero Trust** 접속: https://one.dash.cloudflare.com
2. **Networks > Tunnels** 에서 Tunnel 생성
3. 생성된 **토큰**을 `.env.production`의 `CLOUDFLARE_TUNNEL_TOKEN`에 설정
4. **Public Hostname** 설정:
   - Subdomain: `prompt`
   - Domain: `shoneylife.com`
   - Service: `http://nginx:80`

### 보안 고려사항

- ✅ PostgreSQL 외부 미노출 (Docker 내부 네트워크만)
- ✅ Backend 직접 접근 불가 (nginx 프록시 경유)
- ✅ SSL/TLS Cloudflare에서 자동 관리
- ✅ DDoS 보호 기본 제공
- ✅ 로컬 PC IP 주소 미노출
- ⚠️ `.env.production`은 반드시 `.gitignore`에 포함

상세 설정 가이드: [docs/INFRASTRUCTURE.md](docs/INFRASTRUCTURE.md)
