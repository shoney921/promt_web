# 로컬 PC 도커 외부 접속 인프라 구축 가이드

## 개요
로컬 PC에서 Docker를 사용하여 AI Prompt Web 서비스를 실행하고, Cloudflare Tunnel을 통해 `shoneylife.com` 도메인으로 외부 접속을 가능하게 하는 인프라 구축 가이드입니다.

---

## 선택된 옵션
- **외부 접속**: Cloudflare Tunnel (포트포워딩 불필요, 무료 SSL, DDoS 보호)
- **SSL**: Cloudflare에서 자동 관리
- **도메인**: shoneylife.com
- **모니터링**: 기본 Docker 로깅

---

## 프로덕션 아키텍처

```
[인터넷] ──► [Cloudflare Edge (shoneylife.com)]
                    │
                    │ (암호화된 터널)
                    ▼
            [cloudflared 컨테이너]
                    │
                    ▼
              [nginx:80] ─────────────────────┐
                    │                          │
                    ├── /api/* ──► [backend]   │ Docker
                    │                   │      │ Network
                    └── /*     ──► [정적파일]  │ (internal)
                                        │      │
                          [postgres:5432] ◄────┘
                              (외부 미노출)
```

### Cloudflare Tunnel 장점
- 공유기 포트포워딩 불필요
- SSL 인증서 Cloudflare에서 자동 관리
- DDoS 보호 기본 제공
- 로컬 PC IP 노출 없음

---

## 파일 구조

```
├── docker-compose.prod.yml          # 프로덕션 docker-compose
├── .env.example                      # 환경변수 템플릿
├── .env.production                   # 프로덕션 환경변수 (git 무시)
├── backend/
│   ├── Dockerfile                    # 개발용
│   └── Dockerfile.prod               # 프로덕션용
├── frontend/
│   ├── Dockerfile                    # 개발용
│   └── Dockerfile.prod               # 프로덕션용
└── nginx/
    ├── nginx.conf                    # nginx 메인 설정
    └── conf.d/
        └── default.conf              # 서버 블록 설정
```

---

## Cloudflare Tunnel 설정 가이드

### 1. Cloudflare Zero Trust 접속
1. https://one.dash.cloudflare.com 접속
2. 좌측 메뉴에서 `Networks` > `Tunnels` 클릭

### 2. Tunnel 생성
1. `Create a tunnel` 버튼 클릭
2. `Cloudflared` 선택 후 Next
3. Tunnel 이름 입력: `ai-prompt-tunnel`
4. Save tunnel

### 3. Tunnel 토큰 복사
1. 생성된 토큰을 복사
2. `.env.production` 파일의 `CLOUDFLARE_TUNNEL_TOKEN`에 붙여넣기

### 4. Public Hostname 설정
Tunnel 생성 후 Public Hostname 탭에서:

| Subdomain | Domain | Path | Service |
|-----------|--------|------|---------|
| (비워두기) | shoneylife.com | (비워두기) | http://nginx:80 |
| www | shoneylife.com | (비워두기) | http://nginx:80 |

또는 서브도메인 사용시:
| Subdomain | Domain | Path | Service |
|-----------|--------|------|---------|
| ai | shoneylife.com | (비워두기) | http://nginx:80 |

---

## 실행 방법

### 1. 환경변수 설정
```bash
# .env.production 파일 복사 및 수정
cp .env.example .env.production

# 필수 값 설정
# - OPENAI_API_KEY: OpenAI API 키
# - CLOUDFLARE_TUNNEL_TOKEN: Cloudflare Tunnel 토큰
# - SECRET_KEY: 새로운 시크릿 키 생성
```

### 2. 시크릿 키 생성
```bash
# Python으로 랜덤 시크릿 키 생성
python3 -c "import secrets; print(secrets.token_urlsafe(32))"
```

### 3. 프로덕션 실행
```bash
# 이미지 빌드 및 실행 (Cloudflare Tunnel 포함)
docker-compose -f docker-compose.prod.yml --env-file .env.production up --build -d

# Cloudflare Tunnel 없이 로컬에서만 테스트
docker-compose -f docker-compose.prod.yml --env-file .env.production up -d postgres backend nginx

# 로그 확인
docker-compose -f docker-compose.prod.yml --env-file .env.production logs -f

# 중지
docker-compose -f docker-compose.prod.yml --env-file .env.production down
```

### 4. 로컬 테스트
```bash
# 헬스체크
curl http://localhost/health

# API 테스트
curl http://localhost/api/v1/models/list
```

---

## 검증 방법

### 외부 접속 테스트
1. 모바일 데이터(Wi-Fi가 아닌)로 접속
2. 브라우저에서 `https://shoneylife.com` 접속
3. API 테스트: `https://shoneylife.com/api/v1/health`

### 로그 확인
```bash
# 전체 로그
docker-compose -f docker-compose.prod.yml logs -f

# 특정 서비스 로그
docker-compose -f docker-compose.prod.yml logs -f backend
docker-compose -f docker-compose.prod.yml logs -f nginx
docker-compose -f docker-compose.prod.yml logs -f cloudflared
```

---

## 주의사항

1. **PostgreSQL 외부 노출 금지** - docker-compose.prod.yml에서 ports 설정 없음
2. **API 키 보안** - `.env.production`은 반드시 `.gitignore`에 포함
3. **SECRET_KEY 변경** - 프로덕션에서는 반드시 새로운 키 사용
4. **CORS 도메인** - `https://shoneylife.com` 이미 추가됨

---

## 문제 해결

### Cloudflare Tunnel 연결 안됨
```bash
# cloudflared 컨테이너 상태 확인
docker-compose -f docker-compose.prod.yml logs cloudflared

# 토큰이 올바른지 확인
echo $CLOUDFLARE_TUNNEL_TOKEN
```

### 502 Bad Gateway
```bash
# backend가 정상 실행 중인지 확인
docker-compose -f docker-compose.prod.yml ps

# backend 로그 확인
docker-compose -f docker-compose.prod.yml logs backend
```

### CORS 에러
- 브라우저 개발자 도구에서 에러 확인
- `backend/app/core/config.py`의 CORS_ORIGINS 확인
- `.env.production`의 CORS_ORIGINS 환경변수 확인
