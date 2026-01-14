"""
프롬프트 API 엔드포인트

단일 프롬프트 완성 및 대화 히스토리 기반 채팅 완성 기능을 제공합니다.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import List, Optional
import json

from app.api.deps import get_current_user, get_db
from app.models.user import User
from app.models.conversation import Conversation, Message
from app.schemas.prompt import PromptRequest, PromptResponse, ChatRequest, ChatMessage
from app.services.openai_service import openai_service


router = APIRouter()


# =============================================================================
# 헬퍼 함수
# =============================================================================

def find_last_user_message(messages: List[ChatMessage]) -> Optional[ChatMessage]:
    """메시지 리스트에서 마지막 사용자 메시지를 찾습니다."""
    for msg in reversed(messages):
        if msg.role == "user":
            return msg
    return None


def get_or_create_conversation(
    db: Session,
    user: User,
    request: ChatRequest
) -> Conversation:
    """
    기존 대화 세션을 조회하거나 새로운 대화 세션을 생성합니다.

    Args:
        db: 데이터베이스 세션
        user: 현재 사용자
        request: 채팅 요청 데이터

    Returns:
        Conversation 객체

    Raises:
        HTTPException: 대화 세션을 찾을 수 없는 경우
    """
    if request.conversation_id:
        conversation = db.query(Conversation).filter(
            Conversation.id == request.conversation_id,
            Conversation.user_id == user.id
        ).first()

        if not conversation:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="대화 세션을 찾을 수 없습니다."
            )
        return conversation

    # 새 대화 세션 생성
    first_user_message = next(
        (msg for msg in request.messages if msg.role == "user"),
        None
    )
    title = first_user_message.content[:50] if first_user_message else "새 대화"

    conversation = Conversation(
        user_id=user.id,
        title=title,
        model=request.model,
        temperature=request.temperature,
        max_tokens=request.max_tokens
    )
    db.add(conversation)
    db.commit()
    db.refresh(conversation)

    return conversation


def save_user_message(
    db: Session,
    conversation_id: int,
    messages: List[ChatMessage]
) -> None:
    """마지막 사용자 메시지를 데이터베이스에 저장합니다."""
    last_user_message = find_last_user_message(messages)

    if last_user_message:
        user_msg = Message(
            conversation_id=conversation_id,
            role=last_user_message.role,
            content=last_user_message.content
        )
        db.add(user_msg)
        db.commit()


def save_assistant_message(
    db: Session,
    conversation: Conversation,
    content: str,
    usage: Optional[dict] = None
) -> None:
    """AI 응답 메시지를 데이터베이스에 저장합니다."""
    assistant_msg = Message(
        conversation_id=conversation.id,
        role="assistant",
        content=content,
        usage=usage
    )
    db.add(assistant_msg)
    conversation.updated_at = func.now()
    db.commit()


def convert_messages_to_dict(messages: List[ChatMessage]) -> List[dict]:
    """ChatMessage 리스트를 딕셔너리 리스트로 변환합니다."""
    return [
        {"role": msg.role, "content": msg.content}
        for msg in messages
    ]


def create_streaming_headers() -> dict:
    """SSE 스트리밍에 필요한 HTTP 헤더를 생성합니다."""
    return {
        "Cache-Control": "no-cache",
        "Connection": "keep-alive",
    }


# =============================================================================
# API 엔드포인트
# =============================================================================

@router.post("/completion", response_model=PromptResponse)
async def get_completion(
    request: PromptRequest,
    current_user: User = Depends(get_current_user)
):
    """
    단일 프롬프트에 대한 AI 완성 응답을 반환합니다.

    - 스트리밍 모드: SSE(Server-Sent Events) 형식으로 실시간 응답
    - 일반 모드: 완성된 응답을 한 번에 반환
    """
    try:
        if request.stream:
            return await _handle_streaming_completion(request)
        else:
            return await _handle_normal_completion(request)

    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"AI 응답 생성 중 오류 발생: {str(e)}"
        )


async def _handle_streaming_completion(request: PromptRequest) -> StreamingResponse:
    """단일 프롬프트에 대한 스트리밍 응답을 처리합니다."""
    async def generate_stream():
        async for chunk in openai_service.stream_completion(
            message=request.message,
            model=request.model,
            temperature=request.temperature,
            max_tokens=request.max_tokens
        ):
            yield f"data: {json.dumps({'chunk': chunk}, ensure_ascii=False)}\n\n"
        yield "data: [DONE]\n\n"

    return StreamingResponse(
        generate_stream(),
        media_type="text/event-stream",
        headers=create_streaming_headers()
    )


async def _handle_normal_completion(request: PromptRequest) -> PromptResponse:
    """단일 프롬프트에 대한 일반 응답을 처리합니다."""
    result = await openai_service.get_completion(
        message=request.message,
        model=request.model,
        temperature=request.temperature,
        max_tokens=request.max_tokens
    )
    return PromptResponse(**result)


@router.post("/chat", response_model=PromptResponse)
async def get_chat_completion(
    request: ChatRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    대화 히스토리를 포함한 AI 채팅 완성 응답을 반환합니다.

    - conversation_id가 제공되면 기존 대화를 이어갑니다.
    - conversation_id가 없으면 새 대화 세션을 생성합니다.
    - 스트리밍 모드: SSE 형식으로 실시간 응답
    - 일반 모드: 완성된 응답을 한 번에 반환
    """
    try:
        # 1. 대화 세션 조회 또는 생성
        conversation = get_or_create_conversation(db, current_user, request)

        # 2. 사용자 메시지 저장
        save_user_message(db, conversation.id, request.messages)

        # 3. 메시지 형식 변환
        messages = convert_messages_to_dict(request.messages)

        # 4. AI 응답 생성
        if request.stream:
            return await _handle_streaming_chat(
                db=db,
                conversation=conversation,
                messages=messages,
                request=request
            )
        else:
            return await _handle_normal_chat(
                db=db,
                conversation=conversation,
                messages=messages,
                request=request
            )

    except HTTPException:
        raise
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"AI 응답 생성 중 오류 발생: {str(e)}"
        )


async def _handle_streaming_chat(
    db: Session,
    conversation: Conversation,
    messages: List[dict],
    request: ChatRequest
) -> StreamingResponse:
    """채팅 스트리밍 응답을 처리합니다."""
    full_response = ""

    async def generate_stream():
        nonlocal full_response

        # 검색 사용 여부 표시 (검색 기능이 활성화된 경우)
        if request.use_search:
            yield f"data: {json.dumps({'used_search': True}, ensure_ascii=False)}\n\n"

        # AI 응답 스트리밍
        async for chunk in openai_service.stream_chat_completion(
            messages=messages,
            model=request.model,
            temperature=request.temperature,
            max_tokens=request.max_tokens,
            use_search=request.use_search
        ):
            full_response += chunk
            yield f"data: {json.dumps({'chunk': chunk}, ensure_ascii=False)}\n\n"

        # 스트리밍 완료 후 메시지 저장
        save_assistant_message(db, conversation, full_response)

        # 대화 세션 ID 전송
        yield f"data: {json.dumps({'conversation_id': conversation.id}, ensure_ascii=False)}\n\n"
        yield "data: [DONE]\n\n"

    return StreamingResponse(
        generate_stream(),
        media_type="text/event-stream",
        headers=create_streaming_headers()
    )


async def _handle_normal_chat(
    db: Session,
    conversation: Conversation,
    messages: List[dict],
    request: ChatRequest
) -> PromptResponse:
    """채팅 일반 응답을 처리합니다."""
    # AI 응답 생성
    result = await openai_service.get_chat_completion(
        messages=messages,
        model=request.model,
        temperature=request.temperature,
        max_tokens=request.max_tokens,
        use_search=request.use_search
    )

    # AI 응답 저장
    save_assistant_message(
        db=db,
        conversation=conversation,
        content=result["response"],
        usage=result.get("usage")
    )

    result["conversation_id"] = conversation.id
    return PromptResponse(**result)
