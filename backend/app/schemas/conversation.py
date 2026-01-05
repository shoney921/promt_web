from typing import Optional, List
from pydantic import BaseModel, Field
from datetime import datetime


class MessageBase(BaseModel):
    """메시지 기본 스키마"""
    role: str = Field(..., description="메시지 역할 (user, assistant, system)")
    content: str = Field(..., description="메시지 내용")
    usage: Optional[dict] = Field(default=None, description="토큰 사용량 정보")


class MessageCreate(MessageBase):
    """메시지 생성 스키마"""
    pass


class MessageResponse(MessageBase):
    """메시지 응답 스키마"""
    id: int
    conversation_id: int
    created_at: datetime

    class Config:
        from_attributes = True


class ConversationBase(BaseModel):
    """대화 세션 기본 스키마"""
    title: Optional[str] = Field(default=None, description="대화 제목")
    model: Optional[str] = Field(default=None, description="사용된 모델")
    temperature: Optional[float] = Field(default=None, description="사용된 temperature")
    max_tokens: Optional[int] = Field(default=None, description="사용된 max_tokens")


class ConversationCreate(ConversationBase):
    """대화 세션 생성 스키마"""
    pass


class ConversationResponse(ConversationBase):
    """대화 세션 응답 스키마"""
    id: int
    user_id: int
    created_at: datetime
    updated_at: Optional[datetime]
    messages: List[MessageResponse] = []

    class Config:
        from_attributes = True


class ConversationListResponse(BaseModel):
    """대화 세션 목록 응답 스키마"""
    id: int
    user_id: int
    title: Optional[str]
    model: Optional[str]
    created_at: datetime
    updated_at: Optional[datetime]
    message_count: int = Field(default=0, description="메시지 개수")

    class Config:
        from_attributes = True

