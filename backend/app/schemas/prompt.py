from typing import Optional, List
from pydantic import BaseModel, Field, field_validator
from app.constants.models import DEFAULT_MODEL, is_valid_model


class PromptRequest(BaseModel):
    """프롬프트 요청 스키마"""
    message: str = Field(..., description="사용자 메시지/프롬프트")
    model: Optional[str] = Field(default=DEFAULT_MODEL, description="사용할 OpenAI 모델")
    temperature: Optional[float] = Field(default=0.7, ge=0.0, le=2.0, description="온도 설정 (0.0-2.0)")
    max_tokens: Optional[int] = Field(default=1000, ge=1, description="최대 토큰 수")
    stream: Optional[bool] = Field(default=False, description="스트리밍 응답 여부")
    use_search: Optional[bool] = Field(default=False, description="웹 검색 기능 사용 여부")
    
    @field_validator('model')
    @classmethod
    def validate_model(cls, v: Optional[str]) -> str:
        """모델 검증"""
        if v is None:
            return DEFAULT_MODEL
        if not is_valid_model(v):
            from app.constants.models import AVAILABLE_MODELS
            raise ValueError(f"지원하지 않는 모델입니다: {v}. 사용 가능한 모델: {', '.join(AVAILABLE_MODELS)}")
        return v


class PromptResponse(BaseModel):
    """프롬프트 응답 스키마"""
    response: str = Field(..., description="AI 응답")
    model: str = Field(..., description="사용된 모델")
    usage: Optional[dict] = Field(default=None, description="토큰 사용량 정보")
    conversation_id: Optional[int] = Field(default=None, description="대화 세션 ID")


class ChatMessage(BaseModel):
    """채팅 메시지 스키마"""
    role: str = Field(..., description="메시지 역할 (user, assistant, system)")
    content: str = Field(..., description="메시지 내용")


class ChatRequest(BaseModel):
    """채팅 요청 스키마 (대화 히스토리 포함)"""
    messages: List[ChatMessage] = Field(..., description="대화 메시지 목록")
    model: Optional[str] = Field(default=DEFAULT_MODEL, description="사용할 OpenAI 모델")
    temperature: Optional[float] = Field(default=0.7, ge=0.0, le=2.0, description="온도 설정 (0.0-2.0)")
    max_tokens: Optional[int] = Field(default=1000, ge=1, description="최대 토큰 수")
    stream: Optional[bool] = Field(default=False, description="스트리밍 응답 여부")
    conversation_id: Optional[int] = Field(default=None, description="대화 세션 ID (기존 대화 이어가기)")
    use_search: Optional[bool] = Field(default=False, description="웹 검색 기능 사용 여부")
    
    @field_validator('model')
    @classmethod
    def validate_model(cls, v: Optional[str]) -> str:
        """모델 검증"""
        if v is None:
            return DEFAULT_MODEL
        if not is_valid_model(v):
            from app.constants.models import AVAILABLE_MODELS
            raise ValueError(f"지원하지 않는 모델입니다: {v}. 사용 가능한 모델: {', '.join(AVAILABLE_MODELS)}")
        return v
