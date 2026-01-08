from typing import AsyncIterator, List, Optional
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage, BaseMessage
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from app.core.config import settings
from app.constants.models import DEFAULT_MODEL, is_valid_model, AVAILABLE_MODELS
from app.services.search_service import search_service
import json

# Langchain 0.3.0에서 Agent import
try:
    from langchain.agents import create_openai_tools_agent, AgentExecutor
except ImportError:
    # 대체 경로 시도
    try:
        from langchain_core.agents import AgentExecutor
        from langchain.agents.openai_tools import create_openai_tools_agent
    except ImportError:
        # Agent 기능이 없으면 None으로 설정 (검색 기능 비활성화)
        create_openai_tools_agent = None
        AgentExecutor = None


class OpenAIService:
    """Langchain을 사용한 OpenAI 서비스"""
    
    def __init__(self):
        if not settings.OPENAI_API_KEY:
            raise ValueError("OPENAI_API_KEY가 설정되지 않았습니다.")
        self.api_key = settings.OPENAI_API_KEY
    
    def _create_llm(
        self,
        model: str = None,
        temperature: float = 0.7,
        max_tokens: int = 1000,
        streaming: bool = False
    ) -> ChatOpenAI:
        """Langchain ChatOpenAI 인스턴스 생성"""
        # 모델이 제공되지 않으면 기본 모델 사용
        if model is None:
            model = DEFAULT_MODEL
        
        # 모델 검증
        if not is_valid_model(model):
            raise ValueError(f"지원하지 않는 모델입니다: {model}. 사용 가능한 모델: {', '.join(AVAILABLE_MODELS)}")
        
        # o1, o3 시리즈는 max_completion_tokens 사용, 다른 모델은 max_tokens 사용
        # Reasoning 모델(o1, o3)은 temperature를 지원하지 않음
        is_reasoning_model = model.startswith("o1") or model.startswith("o3") or model.startswith("gpt-5")
        
        llm_kwargs = {
            "model": model,
            "streaming": streaming,
            "openai_api_key": self.api_key,
        }
        
        # Reasoning 모델은 temperature를 지원하지 않음
        if not is_reasoning_model:
            llm_kwargs["temperature"] = temperature
        
        # Reasoning 모델(o1, o3)은 max_completion_tokens 사용
        if is_reasoning_model:
            llm_kwargs["max_completion_tokens"] = max_tokens
        else:
            llm_kwargs["max_tokens"] = max_tokens
        
        return ChatOpenAI(**llm_kwargs)
    
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
        model: str = None,
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
        model: str = None,
        temperature: float = 0.7,
        max_tokens: int = 1000,
        use_search: bool = False
    ) -> dict:
        """대화 히스토리를 포함한 채팅 완성 응답 반환"""
        # 검색 기능이 활성화되어 있고, 검색 툴이 사용 가능한 경우 Agent 사용
        if use_search and search_service.is_enabled:
            return await self._get_chat_completion_with_agent(
                messages=messages,
                model=model,
                temperature=temperature,
                max_tokens=max_tokens
            )
        
        # 기본 채팅 완성 (검색 없음)
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
    
    async def _get_chat_completion_with_agent(
        self,
        messages: List[dict],
        model: str = None,
        temperature: float = 0.7,
        max_tokens: int = 1000
    ) -> dict:
        """Agent를 사용한 채팅 완성 (검색 툴 포함)"""
        # Agent 기능이 사용 불가능한 경우
        if create_openai_tools_agent is None or AgentExecutor is None:
            # 검색을 직접 수행하고 결과를 포함하여 일반 채팅으로 처리
            return await self._get_chat_completion_with_manual_search(
                messages=messages,
                model=model,
                temperature=temperature,
                max_tokens=max_tokens
            )
        
        llm = self._create_llm(
            model=model,
            temperature=temperature,
            max_tokens=max_tokens,
            streaming=False
        )
        
        # 검색 툴 가져오기
        tools = search_service.get_tools()
        if not tools:
            # 검색 툴이 없으면 일반 채팅으로 폴백
            return await self.get_chat_completion(
                messages=messages,
                model=model,
                temperature=temperature,
                max_tokens=max_tokens,
                use_search=False
            )
        
        # Agent 프롬프트 생성
        prompt = ChatPromptTemplate.from_messages([
            ("system", """당신은 도움이 되는 AI 어시스턴트입니다. 
사용자의 질문에 답변할 때, 최신 정보나 실시간 데이터가 필요한 경우 검색 툴을 사용하세요.
검색 결과를 바탕으로 정확하고 유용한 답변을 제공하세요."""),
            MessagesPlaceholder(variable_name="chat_history"),
            ("human", "{input}"),
            MessagesPlaceholder(variable_name="agent_scratchpad"),
        ])
        
        # Agent 생성
        agent = create_openai_tools_agent(llm, tools, prompt)
        agent_executor = AgentExecutor(agent=agent, tools=tools, verbose=False)
        
        # 마지막 사용자 메시지 추출
        last_user_message = None
        chat_history = []
        for msg in messages:
            if msg.get("role") == "user":
                last_user_message = msg.get("content", "")
            elif msg.get("role") == "assistant":
                chat_history.append(("assistant", msg.get("content", "")))
            elif msg.get("role") == "system":
                chat_history.append(("system", msg.get("content", "")))
        
        if not last_user_message:
            raise ValueError("사용자 메시지를 찾을 수 없습니다.")
        
        try:
            # Agent 실행
            result = await agent_executor.ainvoke({
                "input": last_user_message,
                "chat_history": chat_history
            })
            
            return {
                "response": result.get("output", ""),
                "model": model,
                "usage": None  # Agent 사용 시 토큰 사용량은 복잡하므로 None
            }
        except Exception as e:
            raise Exception(f"Agent 실행 중 오류 발생: {str(e)}")
    
    async def _get_chat_completion_with_manual_search(
        self,
        messages: List[dict],
        model: str = None,
        temperature: float = 0.7,
        max_tokens: int = 1000
    ) -> dict:
        """수동 검색을 포함한 채팅 완성 (Agent가 없는 경우)"""
        # 마지막 사용자 메시지 추출
        last_user_message = None
        for msg in reversed(messages):
            if msg.get("role") == "user":
                last_user_message = msg.get("content", "")
                break
        
        if not last_user_message:
            raise ValueError("사용자 메시지를 찾을 수 없습니다.")
        
        # 검색 수행 (간단한 키워드 추출)
        search_results = await search_service.search(last_user_message)
        
        # 검색 결과를 시스템 메시지에 추가
        search_context = ""
        if search_results:
            search_context = "\n\n[검색 결과]\n"
            for i, result in enumerate(search_results[:3], 1):  # 상위 3개만 사용
                content = result.get("content", "") or result.get("snippet", "")
                url = result.get("url", "")
                search_context += f"{i}. {content}\n출처: {url}\n\n"
        
        # 메시지에 검색 결과 추가
        enhanced_messages = messages.copy()
        if search_context:
            # 시스템 메시지가 있으면 업데이트, 없으면 추가
            system_msg_index = next(
                (i for i, msg in enumerate(enhanced_messages) if msg.get("role") == "system"),
                None
            )
            if system_msg_index is not None:
                enhanced_messages[system_msg_index]["content"] += search_context
            else:
                enhanced_messages.insert(0, {
                    "role": "system",
                    "content": f"다음 검색 결과를 참고하여 답변하세요.{search_context}"
                })
        
        # 일반 채팅 완성으로 처리
        return await self.get_chat_completion(
            messages=enhanced_messages,
            model=model,
            temperature=temperature,
            max_tokens=max_tokens,
            use_search=False
        )
    
    async def stream_completion(
        self,
        message: str,
        model: str = None,
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
        model: str = None,
        temperature: float = 0.7,
        max_tokens: int = 1000,
        use_search: bool = False
    ) -> AsyncIterator[str]:
        """대화 히스토리를 포함한 채팅 스트리밍 응답 반환"""
        # 검색 기능이 활성화되어 있고, 검색 툴이 사용 가능한 경우
        # Agent는 스트리밍을 완전히 지원하지 않으므로, 검색 후 일반 스트리밍으로 처리
        if use_search and search_service.is_enabled:
            # Agent로 검색 수행 후 결과를 포함하여 스트리밍
            try:
                # 먼저 Agent로 검색 포함 응답 생성
                agent_result = await self._get_chat_completion_with_agent(
                    messages=messages,
                    model=model,
                    temperature=temperature,
                    max_tokens=max_tokens
                )
                # 결과를 스트리밍 형태로 반환
                response_text = agent_result.get("response", "")
                for char in response_text:
                    yield char
                return
            except Exception as e:
                # Agent 실패 시 일반 스트리밍으로 폴백
                pass
        
        # 기본 스트리밍 (검색 없음)
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
