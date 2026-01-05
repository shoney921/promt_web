from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from sqlalchemy import func
from app.api.deps import get_current_user, get_db
from app.models.user import User
from app.models.conversation import Conversation, Message
from app.schemas.prompt import PromptRequest, PromptResponse, ChatRequest, ChatMessage
from app.services.openai_service import openai_service
import json

router = APIRouter()


@router.post("/completion", response_model=PromptResponse)
async def get_completion(
    request: PromptRequest,
    current_user: User = Depends(get_current_user)
):
    """
    단일 프롬프트에 대한 AI 완성 응답 반환
    """
    try:
        if request.stream:
            # 스트리밍 응답
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
                headers={
                    "Cache-Control": "no-cache",
                    "Connection": "keep-alive",
                }
            )
        else:
            # 일반 응답
            result = await openai_service.get_completion(
                message=request.message,
                model=request.model,
                temperature=request.temperature,
                max_tokens=request.max_tokens
            )
            return PromptResponse(**result)
    
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


@router.post("/chat", response_model=PromptResponse)
async def get_chat_completion(
    request: ChatRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    대화 히스토리를 포함한 AI 채팅 완성 응답 반환
    대화 세션 ID가 제공되면 기존 대화를 이어가고, 없으면 새 대화를 생성합니다.
    """
    try:
        # 대화 세션 처리
        conversation = None
        if request.conversation_id:
            # 기존 대화 세션 조회
            conversation = db.query(Conversation).filter(
                Conversation.id == request.conversation_id,
                Conversation.user_id == current_user.id
            ).first()
            if not conversation:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="대화 세션을 찾을 수 없습니다."
                )
        else:
            # 새 대화 세션 생성
            first_user_message = next((msg for msg in request.messages if msg.role == "user"), None)
            title = first_user_message.content[:50] if first_user_message else "새 대화"
            
            conversation = Conversation(
                user_id=current_user.id,
                title=title,
                model=request.model,
                temperature=request.temperature,
                max_tokens=request.max_tokens
            )
            db.add(conversation)
            db.commit()
            db.refresh(conversation)
        
        # 마지막 사용자 메시지 저장
        last_user_message = None
        for msg in reversed(request.messages):
            if msg.role == "user":
                last_user_message = msg
                break
        
        if last_user_message:
            user_msg = Message(
                conversation_id=conversation.id,
                role=last_user_message.role,
                content=last_user_message.content
            )
            db.add(user_msg)
            db.commit()
        
        # 메시지 리스트를 딕셔너리로 변환
        messages = [
            {"role": msg.role, "content": msg.content}
            for msg in request.messages
        ]
        
        if request.stream:
            # 스트리밍 응답
            full_response = ""
            async def generate_stream():
                nonlocal full_response
                async for chunk in openai_service.stream_chat_completion(
                    messages=messages,
                    model=request.model,
                    temperature=request.temperature,
                    max_tokens=request.max_tokens
                ):
                    full_response += chunk
                    yield f"data: {json.dumps({'chunk': chunk}, ensure_ascii=False)}\n\n"
                
                # 스트리밍 완료 후 메시지 저장
                assistant_msg = Message(
                    conversation_id=conversation.id,
                    role="assistant",
                    content=full_response
                )
                db.add(assistant_msg)
                conversation.updated_at = func.now()
                db.commit()
                
                # conversation_id를 포함한 완료 메시지 전송
                yield f"data: {json.dumps({'conversation_id': conversation.id}, ensure_ascii=False)}\n\n"
                yield "data: [DONE]\n\n"
            
            return StreamingResponse(
                generate_stream(),
                media_type="text/event-stream",
                headers={
                    "Cache-Control": "no-cache",
                    "Connection": "keep-alive",
                }
            )
        else:
            # 일반 응답
            result = await openai_service.get_chat_completion(
                messages=messages,
                model=request.model,
                temperature=request.temperature,
                max_tokens=request.max_tokens
            )
            
            # AI 응답 메시지 저장
            assistant_msg = Message(
                conversation_id=conversation.id,
                role="assistant",
                content=result["response"],
                usage=result.get("usage")
            )
            db.add(assistant_msg)
            conversation.updated_at = func.now()
            db.commit()
            
            result["conversation_id"] = conversation.id
            return PromptResponse(**result)
    
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"AI 응답 생성 중 오류 발생: {str(e)}"
        )
