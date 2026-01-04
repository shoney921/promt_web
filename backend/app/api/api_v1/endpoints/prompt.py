from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import StreamingResponse
from app.api.deps import get_current_user
from app.models.user import User
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
    current_user: User = Depends(get_current_user)
):
    """
    대화 히스토리를 포함한 AI 채팅 완성 응답 반환
    """
    try:
        # 메시지 리스트를 딕셔너리로 변환
        messages = [
            {"role": msg.role, "content": msg.content}
            for msg in request.messages
        ]
        
        if request.stream:
            # 스트리밍 응답
            async def generate_stream():
                async for chunk in openai_service.stream_chat_completion(
                    messages=messages,
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
            result = await openai_service.get_chat_completion(
                messages=messages,
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
