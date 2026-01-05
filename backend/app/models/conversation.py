from sqlalchemy import Column, Integer, String, Float, ForeignKey, DateTime, Text, JSON
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.core.database import Base


class Conversation(Base):
    """대화 세션 모델"""
    __tablename__ = "conversations"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    title = Column(String, nullable=True)  # 대화 제목 (첫 메시지 기반)
    model = Column(String, nullable=True)  # 사용된 모델
    temperature = Column(Float, nullable=True)  # 사용된 temperature
    max_tokens = Column(Integer, nullable=True)  # 사용된 max_tokens
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # 관계
    messages = relationship("Message", back_populates="conversation", cascade="all, delete-orphan")


class Message(Base):
    """대화 메시지 모델"""
    __tablename__ = "messages"

    id = Column(Integer, primary_key=True, index=True)
    conversation_id = Column(Integer, ForeignKey("conversations.id"), nullable=False, index=True)
    role = Column(String, nullable=False)  # user, assistant, system
    content = Column(Text, nullable=False)  # 메시지 내용
    usage = Column(JSON, nullable=True)  # 토큰 사용량 정보
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # 관계
    conversation = relationship("Conversation", back_populates="messages")

