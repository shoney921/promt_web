# 트러블슈팅 가이드

## 목차
1. [Docker BuildKit 캐시로 인한 프론트엔드 빌드 미반영 문제](#1-docker-buildkit-캐시로-인한-프론트엔드-빌드-미반영-문제)

---

## 1. Docker BuildKit 캐시로 인한 프론트엔드 빌드 미반영 문제

### 발생일
2026-01-16

### 증상
- 프론트엔드에서 백엔드 API 호출 시 CORS 에러 발생
- 브라우저 개발자 도구에서 확인 시:
  - Origin: `https://prompt.shoneylife.com`
  - Request URL: `https://shoneylife.com/api/v1/auth/register` (잘못된 URL)
- `docker-compose up --build`를 실행해도 변경사항이 반영되지 않음

### 원인

**Docker BuildKit의 공격적인 캐싱**

Docker 23.0+부터 기본 활성화된 BuildKit은 빌드 속도 향상을 위해 강력한 캐싱을 적용합니다. 문제는 다음과 같이 발생했습니다:

1. **`COPY . .` 레이어 캐싱**: BuildKit이 파일 변경을 감지하지 못하고 이전 캐시를 계속 사용
2. **node_modules/dist 폴더 포함**: 로컬에 존재하는 `node_modules`와 `dist` 폴더가 빌드 컨텍스트에 포함되어 캐시 무효화를 방해
3. **Vite 환경변수 주입 실패**: `VITE_API_BASE_URL` 환경변수가 빌드 시점에 제대로 주입되지 않음

### 디버깅 과정

```bash
# 1. 빌드된 JS 파일에서 API URL 확인
docker exec ai_prompt_nginx_prod sh -c "cat /usr/share/nginx/html/assets/*.js" | grep -o 'https://[^"]*api/v1'
# 결과: https://shoneylife.com/api/v1 (잘못된 URL이 계속 출력됨)

# 2. 로컬에서 직접 빌드하여 비교
cd frontend && npm run build
grep -o 'https://[^"]*api/v1' dist/assets/*.js
# 결과: https://prompt.shoneylife.com/api/v1 (정상)

# 3. docker-compose가 아닌 직접 빌드
docker build --no-cache -f frontend/Dockerfile.prod -t test-frontend ./frontend
# 결과: 새로운 파일명 생성 (index-C9PlCHdg.js)
```

### 해결 방법

#### 방법 1: .dockerignore 추가 (권장)

`frontend/.dockerignore` 파일 생성:

```
node_modules
dist
.git
*.log
```

#### 방법 2: 로컬 빌드 산출물 삭제 후 재빌드

```bash
# 1. 로컬 빌드 산출물 삭제
rm -rf frontend/node_modules frontend/dist

# 2. Docker 캐시 완전 삭제
docker stop ai_prompt_nginx_prod
docker rm ai_prompt_nginx_prod
docker rmi 01_ai_prompt_web-nginx
docker builder prune -af

# 3. 재빌드
docker-compose -f docker-compose.prod.yml --env-file .env.production up --build -d nginx
```

#### 방법 3: docker-compose 대신 직접 빌드

```bash
# 1. 직접 빌드
docker build --no-cache -f frontend/Dockerfile.prod -t 01_ai_prompt_web-nginx ./frontend

# 2. 컨테이너 재시작
docker-compose -f docker-compose.prod.yml --env-file .env.production up -d nginx
```

### 적용된 변경사항

| 파일 | 변경 내용 |
|------|----------|
| `frontend/.dockerignore` | `node_modules`, `dist` 제외 추가 |
| `frontend/.env.production` | `VITE_API_BASE_URL=https://prompt.shoneylife.com/api/v1` |
| `frontend/src/lib/api.ts` | 기본값을 프로덕션 URL로 변경 |

### 검증 방법

```bash
# 빌드된 JS에서 올바른 URL 확인
docker exec ai_prompt_nginx_prod sh -c "cat /usr/share/nginx/html/assets/*.js" | grep -o 'https://[^"]*api/v1' | head -1
# 예상 결과: https://prompt.shoneylife.com/api/v1

# API 요청 테스트
curl -s -X POST "https://prompt.shoneylife.com/api/v1/auth/register" \
  -H "Content-Type: application/json" \
  -d '{"email":"test@test.com","password":"password123"}'
```

### 교훈

1. **프론트엔드 빌드 시 항상 `.dockerignore` 설정 필수**
2. **BuildKit 캐시 문제 발생 시 `docker builder prune -af`로 캐시 삭제**
3. **Vite 환경변수는 빌드 시점에 주입되므로, 런타임이 아닌 빌드 단계에서 설정 필요**
4. **문제 발생 시 빌드된 파일의 내용을 직접 확인하여 디버깅**

---

## 추가 트러블슈팅 항목 템플릿

```markdown
## N. [문제 제목]

### 발생일
YYYY-MM-DD

### 증상
- 증상 1
- 증상 2

### 원인
원인 설명

### 해결 방법
해결 방법 설명

### 검증 방법
검증 명령어 또는 방법
```
