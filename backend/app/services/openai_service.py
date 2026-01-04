from typing import AsyncIterator, List, Optional
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage, BaseMessage
from app.core.config import settings
import json


class OpenAIService:
    """Langchain을 사용한 OpenAI 서비스"""
    
    def __init__(self):
        if not settings.OPENAI_API_KEY:
            raise ValueError("OPENAI_API_KEY가 설정되지 않았습니다.")
        self.api_key = settings.OPENAI_API_KEY
    
    def _create_llm(
        self,
        model: str = "gpt-4o-mini",
        temperature: float = 0.7,
        max_tokens: int = 1000,
        streaming: bool = False
    ) -> ChatOpenAI:
        """Langchain ChatOpenAI 인스턴스 생성"""
        return ChatOpenAI(
            model=model,
            temperature=temperature,
            max_tokens=max_tokens,
            streaming=streaming,
            openai_api_key=self.api_key,
        )
    
    def _convert_messages(self, messages: List[dict]) -> List[BaseMessage]:
        """메시지 딕셔너리를 Langchain 메시지 객체로 변환"""
        langchain_messages = []
        for msg in messages:
            role = msg.get("role", "user")
            content = msg.get("content", "")
            
            if role == "user":
                langchain_messages.append(HumanMessage(content=content))
            elif role == "assistant":
                langchain_messages.append(AIMessage(content=content))
            elif role == "system":
                langchain_messages.append(SystemMessage(content=content))
        
        return langchain_messages
    
    async def get_completion(
        self,
        message: str,
        model: str = "gpt-4o-mini",
        temperature: float = 0.7,
        max_tokens: int = 1000
    ) -> dict:
        """단일 프롬프트에 대한 완성 응답 반환"""
        llm = self._create_llm(
            model=model,
            temperature=temperature,
            max_tokens=max_tokens,
            streaming=False
        )
        
        try:
            response = await llm.ainvoke(message)
            
            return {
                "response": response.content,
                "model": model,
                "usage": {
                    "prompt_tokens": getattr(response.response_metadata, "token_usage", {}).get("prompt_tokens", 0),
                    "completion_tokens": getattr(response.response_metadata, "token_usage", {}).get("completion_tokens", 0),
                    "total_tokens": getattr(response.response_metadata, "token_usage", {}).get("total_tokens", 0),
                } if hasattr(response, "response_metadata") else None
            }
        except Exception as e:
            raise Exception(f"OpenAI API 호출 중 오류 발생: {str(e)}")
    
    async def get_chat_completion(
        self,
        messages: List[dict],
        model: str = "gpt-4o-mini",
        temperature: float = 0.7,
        max_tokens: int = 1000
    ) -> dict:
        """대화 히스토리를 포함한 채팅 완성 응답 반환"""
        llm = self._create_llm(
            model=model,
            temperature=temperature,
            max_tokens=max_tokens,
            streaming=False
        )
        
        langchain_messages = self._convert_messages(messages)
        
        try:
            response = await llm.ainvoke(langchain_messages)
            
            return {
                "response": response.content,
                "model": model,
                "usage": {
                    "prompt_tokens": getattr(response.response_metadata, "token_usage", {}).get("prompt_tokens", 0),
                    "completion_tokens": getattr(response.response_metadata, "token_usage", {}).get("completion_tokens", 0),
                    "total_tokens": getattr(response.response_metadata, "token_usage", {}).get("total_tokens", 0),
                } if hasattr(response, "response_metadata") else None
            }
        except Exception as e:
            raise Exception(f"OpenAI API 호출 중 오류 발생: {str(e)}")
    
    async def stream_completion(
        self,
        message: str,
        model: str = "gpt-4o-mini",
        temperature: float = 0.7,
        max_tokens: int = 1000
    ) -> AsyncIterator[str]:
        """단일 프롬프트에 대한 스트리밍 응답 반환"""
        llm = self._create_llm(
            model=model,
            temperature=temperature,
            max_tokens=max_tokens,
            streaming=True
        )
        
        try:
            async for chunk in llm.astream(message):
                if chunk.content:
                    yield chunk.content
        except Exception as e:
            raise Exception(f"OpenAI API 스트리밍 중 오류 발생: {str(e)}")
    
    async def stream_chat_completion(
        self,
        messages: List[dict],
        model: str = "gpt-4o-mini",
        temperature: float = 0.7,
        max_tokens: int = 1000
    ) -> AsyncIterator[str]:
        """대화 히스토리를 포함한 채팅 스트리밍 응답 반환"""
        llm = self._create_llm(
            model=model,
            temperature=temperature,
            max_tokens=max_tokens,
            streaming=True
        )
        
        langchain_messages = self._convert_messages(messages)
        
        try:
            async for chunk in llm.astream(langchain_messages):
                if chunk.content:
                    yield chunk.content
        except Exception as e:
            raise Exception(f"OpenAI API 스트리밍 중 오류 발생: {str(e)}")


# 싱글톤 인스턴스
openai_service = OpenAIService()
