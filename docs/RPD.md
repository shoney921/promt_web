# Dean Prompt Web - RPD (Requirements & Planning Document)

## 1. 프로젝트 개요

### 프로젝트명
**Dean Prompt Web** - 개인화된 AI 프롬프트 관리 플랫폼

### 프로젝트 목적
일반 ChatGPT 클론을 넘어, 사용자가 자신만의 프롬프트를 체계적으로 저장, 관리, 재사용할 수 있는 **"나만의 프롬프트 라이브러리"**를 제공하는 것

### 핵심 가치 제안
| 가치 | 설명 |
|------|------|
| **재사용성** | 자주 쓰는 프롬프트를 저장하고 언제든 재활용 |
| **효율성** | 템플릿 변수로 반복 입력 최소화 |
| **조직화** | 폴더와 태그로 체계적인 프롬프트 관리 |
| **즉시성** | 프롬프트 선택 → 변수 입력 → 바로 채팅 |

### 타겟 사용자

| 사용자 유형 | 주요 사용 목적 | 예상 사용 빈도 |
|------------|---------------|---------------|
| 개인 사용자 | 일상적인 AI 활용, 개인 프롬프트 라이브러리 구축 | 매일 |
| 학생/연구자 | 논문 작성, 학습 보조, 연구 분석 | 주 3-5회 |
| 개발자/기술직 | 코드 리뷰, 문서화, 디버깅, API 설계 | 매일 |

---

## 2. 핵심 기능 목록

### MVP (Phase 1) - 필수 기능

| ID | 기능명 | 설명 | 우선순위 |
|----|--------|------|----------|
| F1 | **프롬프트 CRUD** | 프롬프트 생성, 조회, 수정, 삭제 | 필수 |
| F2 | **폴더 관리** | 프롬프트를 폴더로 분류, 중첩 폴더 지원 | 필수 |
| F3 | **태그 시스템** | 프롬프트에 태그 추가, 태그로 필터링 | 필수 |
| F4 | **템플릿 변수** | `{{변수명}}` 문법으로 동적 프롬프트 | 필수 |
| F5 | **변수 입력 폼** | 프롬프트 실행 시 변수 입력 UI 자동 생성 | 필수 |
| F6 | **프롬프트 검색** | 제목, 내용, 태그로 프롬프트 검색 | 필수 |
| F7 | **채팅 시작** | 프롬프트 선택 → 변수 입력 → 새 채팅 생성 | 필수 |
| F8 | **채팅 중 불러오기** | 기존 대화에서 프롬프트 삽입 | 권장 |
| F9 | **즐겨찾기** | 자주 쓰는 프롬프트 즐겨찾기 | 선택 |
| F10 | **사용 통계** | 프롬프트별 사용 횟수 추적 | 선택 |

### Phase 2 - 확장 기능

| ID | 기능명 | 설명 |
|----|--------|------|
| F11 | 공개 링크 공유 | URL로 프롬프트 공유 |
| F12 | 프롬프트 복제 | 다른 사용자 프롬프트 가져오기 |
| F13 | 팀 워크스페이스 | 팀 단위 프롬프트 관리 |

### Phase 3 - 고급 기능

| ID | 기능명 | 설명 |
|----|--------|------|
| F14 | 워크플로우 빌더 | 여러 프롬프트 순차 실행 |
| F15 | API 연동 | 외부 앱에서 프롬프트 호출 |
| F16 | 커뮤니티 마켓 | 인기 프롬프트 탐색/공유 |

---

## 3. 사용자 시나리오

### 시나리오 1: 프롬프트 생성 및 사용

**페르소나**: 개발자 김철수 - 코드 리뷰 프롬프트 생성

1. 김철수는 "프롬프트" 메뉴로 이동한다
2. "새 프롬프트" 버튼을 클릭한다
3. 다음 정보를 입력한다:
   - 제목: "Python 코드 리뷰"
   - 폴더: "개발 도구"
   - 태그: #코드리뷰, #Python
   - 내용:
     ```
     다음 Python 코드를 리뷰해주세요.

     코드:
     ```python
     {{code}}
     ```

     리뷰 관점:
     {{focus_areas}}
     ```
4. 저장 버튼을 클릭한다
5. 나중에 이 프롬프트를 사용할 때:
   - 프롬프트 카드에서 "실행" 버튼 클릭
   - 변수 입력 폼이 나타남:
     - code: [텍스트 영역]
     - focus_areas: [텍스트 필드]
   - 값 입력 후 "채팅 시작" 클릭
   - 새 채팅이 생성되고 AI가 응답 시작

### 시나리오 2: 기존 채팅에서 프롬프트 사용

**페르소나**: 학생 이영희 - 논문 작성 중 프롬프트 사용

1. 이영희는 AI와 논문 관련 대화 중이다
2. 채팅 입력창 옆의 "프롬프트 불러오기" 버튼 클릭
3. 프롬프트 검색창에서 "논문 요약" 검색
4. "학술 논문 요약 요청" 프롬프트 선택
5. 변수 입력 팝업:
   - paper_title: "딥러닝 기반 자연어 처리"
   - key_points: "모델 구조, 실험 결과"
6. "삽입" 버튼 클릭
7. 완성된 프롬프트가 채팅 입력창에 삽입됨
8. 전송하여 대화 계속

### 시나리오 3: 프롬프트 정리 및 검색

**페르소나**: 일반 사용자 박지민 - 프롬프트 정리

1. 박지민은 20개의 프롬프트를 보유 중
2. 사이드바에서 폴더 구조 확인:
   - 업무
   - 학습
   - 일상
3. "이메일 작성" 프롬프트를 드래그하여 "업무" 폴더로 이동
4. 검색창에 "번역" 입력
5. 관련 프롬프트 2개가 필터링됨
6. 태그 필터에서 "#영어" 선택
7. 결과가 1개로 좁혀짐

---

## 4. 기술 스택

### 현재 스택 (유지)

| 레이어 | 기술 | 버전 | 용도 |
|--------|------|------|------|
| **Backend** | FastAPI | 0.104.1 | REST API 서버 |
| | SQLAlchemy | 2.0.23 | ORM |
| | PostgreSQL | 15 | 데이터베이스 |
| | Alembic | 1.12.1 | DB 마이그레이션 |
| | LangChain | 0.3.0 | LLM 통합 |
| **Frontend** | React | 18.2.0 | UI 프레임워크 |
| | TypeScript | 5.2.2 | 타입 안정성 |
| | Vite | 5.0.0 | 빌드 도구 |
| | Tailwind CSS | 3.3.5 | 스타일링 |
| | Zustand | 4.4.7 | 상태 관리 |
| | TanStack Query | 5.12.2 | 서버 상태 관리 |
| **Infra** | Docker | - | 컨테이너화 |

### 추가 예정

| 기술 | 용도 |
|------|------|
| React DnD | 드래그 앤 드롭 (폴더 정리) |
| Fuse.js | 프론트엔드 검색 (선택적) |

---

## 5. 마일스톤 및 일정

### Phase 1: MVP (핵심 기능)

| 마일스톤 | 작업 내용 | 산출물 |
|----------|----------|--------|
| **M1: DB 설계** | Prompt, Folder, PromptUsage 테이블 설계 및 마이그레이션 | Alembic 마이그레이션 파일 |
| **M2: Backend API** | 프롬프트 CRUD, 폴더 CRUD, 검색 API | `/api/v1/prompts`, `/api/v1/folders` |
| **M3: 프롬프트 목록 UI** | 프롬프트 라이브러리 페이지, 카드 뷰, 폴더 사이드바 | `/prompts` 페이지 |
| **M4: 프롬프트 편집 UI** | 생성/수정 폼, 변수 입력, Markdown 에디터 | `/prompts/new`, `/prompts/:id` |
| **M5: 채팅 연동** | 변수 입력 폼, 프롬프트 실행, 채팅 페이지 통합 | 수정된 `ChatPage.tsx` |
| **M6: 검색 & 필터** | 제목/내용/태그 검색, 폴더/태그 필터 | 검색 컴포넌트 |

### Phase 2: 공유 & 협업

| 마일스톤 | 작업 내용 |
|----------|----------|
| M7 | 공개 링크 생성 및 공유 페이지 |
| M8 | 프롬프트 복제 기능 |
| M9 | 팀 워크스페이스 (선택) |

### Phase 3: 고급 기능

| 마일스톤 | 작업 내용 |
|----------|----------|
| M10 | 워크플로우 빌더 |
| M11 | 외부 API 연동 |
| M12 | 커뮤니티 마켓플레이스 |

---

## 6. 데이터 모델

### ERD 개요

```
┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│    User     │────<│   Prompt    │────<│PromptUsage │
└─────────────┘     └─────────────┘     └─────────────┘
                           │
                           │
                    ┌─────────────┐
                    │   Folder    │
                    └─────────────┘
```

### 테이블 스키마

#### Prompt 테이블
```sql
CREATE TABLE prompts (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id),
    folder_id UUID REFERENCES folders(id),
    title VARCHAR(200) NOT NULL,
    content TEXT NOT NULL,
    description TEXT,
    variables JSONB DEFAULT '[]',  -- [{name, description, default}]
    tags JSONB DEFAULT '[]',       -- ["tag1", "tag2"]
    is_favorite BOOLEAN DEFAULT FALSE,
    is_public BOOLEAN DEFAULT FALSE,
    share_token VARCHAR(50) UNIQUE,
    use_count INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);
```

#### Folder 테이블
```sql
CREATE TABLE folders (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id),
    parent_id UUID REFERENCES folders(id),
    name VARCHAR(100) NOT NULL,
    order_index INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT NOW()
);
```

#### PromptUsage 테이블 (사용 기록)
```sql
CREATE TABLE prompt_usages (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    prompt_id UUID NOT NULL REFERENCES prompts(id),
    conversation_id UUID REFERENCES conversations(id),
    variables_used JSONB,  -- {name: value}
    created_at TIMESTAMP DEFAULT NOW()
);
```

---

## 7. API 설계

### 프롬프트 API

| Method | Endpoint | 설명 | Request Body | Response |
|--------|----------|------|-------------|----------|
| POST | `/api/v1/prompts` | 프롬프트 생성 | `{title, content, folder_id?, tags?, variables?}` | `Prompt` |
| GET | `/api/v1/prompts` | 목록 조회 | Query: `?search=&folder_id=&tag=` | `Prompt[]` |
| GET | `/api/v1/prompts/{id}` | 상세 조회 | - | `Prompt` |
| PUT | `/api/v1/prompts/{id}` | 수정 | `{title?, content?, ...}` | `Prompt` |
| DELETE | `/api/v1/prompts/{id}` | 삭제 | - | `{success: true}` |
| POST | `/api/v1/prompts/{id}/use` | 사용 (채팅 시작) | `{variables: {name: value}}` | `{conversation_id, message}` |
| POST | `/api/v1/prompts/{id}/favorite` | 즐겨찾기 토글 | - | `{is_favorite: boolean}` |

### 폴더 API

| Method | Endpoint | 설명 |
|--------|----------|------|
| POST | `/api/v1/folders` | 폴더 생성 |
| GET | `/api/v1/folders` | 폴더 트리 조회 |
| PUT | `/api/v1/folders/{id}` | 폴더 수정/이동 |
| DELETE | `/api/v1/folders/{id}` | 폴더 삭제 |

---

## 8. UI/UX 설계

### 메인 레이아웃

```
┌─────────────────────────────────────────────────────┐
│  로고    [채팅] [프롬프트] [설정]        [사용자]   │
├─────────┬───────────────────────────────────────────┤
│         │                                           │
│ 사이드바 │              메인 콘텐츠                  │
│         │                                           │
│ - 대화  │  (채팅 페이지 or 프롬프트 라이브러리)     │
│ - 폴더  │                                           │
│ - 태그  │                                           │
│         │                                           │
└─────────┴───────────────────────────────────────────┘
```

### 프롬프트 카드 디자인

```
┌────────────────────────────────────┐
│ ⭐ 코드 리뷰어                      │
│ #개발 #Python                       │
│                                    │
│ 코드를 분석하고 개선점을 찾아...    │
│                                    │
│ 📁 개발 도구  │  사용: 42회         │
│ [실행] [편집] [공유]               │
└────────────────────────────────────┘
```

### 프론트엔드 라우트

| 경로 | 설명 |
|------|------|
| `/prompts` | 프롬프트 라이브러리 (메인) |
| `/prompts/new` | 새 프롬프트 생성 |
| `/prompts/:id` | 프롬프트 상세/편집 |
| `/prompts/:id/use` | 변수 입력 후 실행 |
| `/shared/:token` | 공유된 프롬프트 보기 (Phase 2) |

---

## 9. 검증 방법

### 기능 테스트
- [ ] 프롬프트 생성/수정/삭제 동작 확인
- [ ] 변수 파싱 및 폼 자동 생성 확인
- [ ] 변수 치환 후 채팅 시작 확인
- [ ] 검색 및 필터링 동작 확인
- [ ] 폴더 구조 및 이동 확인

### 통합 테스트
- [ ] 프롬프트 → 변수 입력 → 채팅 생성 플로우
- [ ] 기존 채팅에서 프롬프트 불러오기 플로우

### 성능 테스트
- [ ] 100+ 프롬프트 목록 로딩 시간
- [ ] 검색 응답 시간

---

## 10. MVP 범위 요약

### 포함
- 프롬프트 CRUD (생성/조회/수정/삭제)
- 폴더 기반 분류 시스템
- 태그 지원
- 템플릿 변수 (`{{variable}}`) 지원
- 폼 기반 변수 입력 → 채팅 시작
- 프롬프트 검색 (제목/내용/태그)
- 채팅 중 프롬프트 불러오기

### 제외 (MVP 이후)
- 기본 예제 템플릿 (빈 상태로 시작)
- 공유/협업 기능
- 워크플로우/자동화
- 커뮤니티 마켓플레이스
