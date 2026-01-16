from pydantic_settings import BaseSettings
from typing import List
import os


# 기본 CORS 출처 목록
DEFAULT_CORS_ORIGINS = [
    "http://localhost:5173",
    "http://localhost:3000",
    "http://127.0.0.1:5173",
    "http://127.0.0.1:3000",
    "https://shoneylife.com",
    "https://www.shoneylife.com",
    "https://prompt.shoneylife.com",
]


def get_cors_origins() -> List[str]:
    """환경변수에서 CORS 출처를 가져오거나 기본값 반환"""
    cors_env = os.getenv("CORS_ORIGINS")
    if cors_env:
        return [origin.strip() for origin in cors_env.split(",") if origin.strip()]
    return DEFAULT_CORS_ORIGINS


class Settings(BaseSettings):
    # 프로젝트 정보
    PROJECT_NAME: str = "AI Prompt Web"
    VERSION: str = "1.0.0"

    # 데이터베이스
    DATABASE_URL: str = "postgresql://postgres:postgres@postgres:5432/ai_prompt_db"

    # JWT 설정
    SECRET_KEY: str = "your-secret-key-change-in-production-use-env-variable"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 7  # 7일

    # OpenAI - OPEN_AI_KEY 환경 변수도 지원
    OPENAI_API_KEY: str = ""

    # Tavily Search API (선택적 - 없어도 검색 기능 비활성화)
    TAVILY_API_KEY: str = ""

    class Config:
        env_file = ".env"
        case_sensitive = True

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # OPEN_AI_KEY 환경 변수를 OPENAI_API_KEY로 매핑
        if os.getenv("OPEN_AI_KEY") and not self.OPENAI_API_KEY:
            self.OPENAI_API_KEY = os.getenv("OPEN_AI_KEY")

    @property
    def cors_origins(self) -> List[str]:
        """CORS 출처 목록 반환"""
        return get_cors_origins()


settings = Settings()
