from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from sqlalchemy import func, desc
from typing import List
from app.api.deps import get_current_user, get_db
from app.models.user import User
from app.models.conversation import Conversation, Message
from app.schemas.conversation import (
    ConversationCreate,
    ConversationResponse,
    ConversationListResponse,
    MessageCreate,
    MessageResponse
)

router = APIRouter()


@router.post("/", response_model=ConversationResponse, status_code=status.HTTP_201_CREATED)
def create_conversation(
    conversation: ConversationCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """새 대화 세션 생성"""
    db_conversation = Conversation(
        user_id=current_user.id,
        title=conversation.title,
        model=conversation.model,
        temperature=conversation.temperature,
        max_tokens=conversation.max_tokens
    )
    db.add(db_conversation)
    db.commit()
    db.refresh(db_conversation)
    return db_conversation


@router.get("/", response_model=List[ConversationListResponse])
def get_conversations(
    skip: int = 0,
    limit: int = 50,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """사용자의 대화 세션 목록 조회"""
    conversations = db.query(Conversation).filter(
        Conversation.user_id == current_user.id
    ).order_by(desc(Conversation.updated_at)).offset(skip).limit(limit).all()
    
    result = []
    for conv in conversations:
        message_count = db.query(func.count(Message.id)).filter(
            Message.conversation_id == conv.id
        ).scalar()
        
        result.append({
            "id": conv.id,
            "user_id": conv.user_id,
            "title": conv.title,
            "model": conv.model,
            "created_at": conv.created_at,
            "updated_at": conv.updated_at,
            "message_count": message_count or 0
        })
    
    return result


@router.get("/{conversation_id}", response_model=ConversationResponse)
def get_conversation(
    conversation_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """특정 대화 세션 조회 (메시지 포함)"""
    conversation = db.query(Conversation).filter(
        Conversation.id == conversation_id,
        Conversation.user_id == current_user.id
    ).first()
    
    if not conversation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="대화 세션을 찾을 수 없습니다."
        )
    
    return conversation


@router.delete("/{conversation_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_conversation(
    conversation_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """대화 세션 삭제"""
    conversation = db.query(Conversation).filter(
        Conversation.id == conversation_id,
        Conversation.user_id == current_user.id
    ).first()
    
    if not conversation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="대화 세션을 찾을 수 없습니다."
        )
    
    db.delete(conversation)
    db.commit()
    return None


@router.patch("/{conversation_id}/title", response_model=ConversationResponse)
def update_conversation_title(
    conversation_id: int,
    title: str = Query(..., description="새 제목"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """대화 세션 제목 업데이트"""
    conversation = db.query(Conversation).filter(
        Conversation.id == conversation_id,
        Conversation.user_id == current_user.id
    ).first()
    
    if not conversation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="대화 세션을 찾을 수 없습니다."
        )
    
    conversation.title = title
    db.commit()
    db.refresh(conversation)
    return conversation

