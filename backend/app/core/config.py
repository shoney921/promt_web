from pydantic_settings import BaseSettings
from typing import List
import os


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
    
    # CORS
    CORS_ORIGINS: List[str] = [
        "http://localhost:5173",
        "http://localhost:3000",
        "http://127.0.0.1:5173",
        "http://127.0.0.1:3000",
    ]
    
    class Config:
        env_file = ".env"
        case_sensitive = True
        
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # OPEN_AI_KEY 환경 변수를 OPENAI_API_KEY로 매핑
        if os.getenv("OPEN_AI_KEY") and not self.OPENAI_API_KEY:
            self.OPENAI_API_KEY = os.getenv("OPEN_AI_KEY")


settings = Settings()
