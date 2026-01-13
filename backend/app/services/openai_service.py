"""
OpenAI 서비스

Langchain을 사용하여 OpenAI API와 상호작용하는 서비스입니다.
단일 프롬프트 완성, 채팅 완성, 스트리밍 응답을 지원합니다.
"""

from typing import AsyncIterator, List, Optional
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage, BaseMessage
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder

from app.core.config import settings
from app.constants.models import DEFAULT_MODEL, is_valid_model, AVAILABLE_MODELS
from app.services.search_service import search_service


# =============================================================================
# Agent 모듈 동적 임포트
# =============================================================================

try:
    from langchain.agents import create_openai_tools_agent, AgentExecutor
except ImportError:
    try:
        from langchain_core.agents import AgentExecutor
        from langchain.agents.openai_tools import create_openai_tools_agent
    except ImportError:
        create_openai_tools_agent = None
        AgentExecutor = None


# =============================================================================
# 상수 정의
# =============================================================================

REASONING_MODEL_PREFIXES = ("o1", "o3", "gpt-5")
MAX_SEARCH_RESULTS = 3

AGENT_SYSTEM_PROMPT = """당신은 도움이 되는 AI 어시스턴트입니다.
사용자의 질문에 답변할 때, 최신 정보나 실시간 데이터가 필요한 경우 검색 툴을 사용하세요.
검색 결과를 바탕으로 정확하고 유용한 답변을 제공하세요."""


# =============================================================================
# 헬퍼 함수
# =============================================================================

def is_reasoning_model(model: str) -> bool:
    """Reasoning 모델 여부를 확인합니다. (o1, o3, gpt-5 시리즈)"""
    return model.startswith(REASONING_MODEL_PREFIXES)


def extract_token_usage(response) -> Optional[dict]:
    """응답 객체에서 토큰 사용량 정보를 추출합니다."""
    if not hasattr(response, "response_metadata"):
        return None

    token_usage = getattr(response.response_metadata, "token_usage", {})
    if not token_usage:
        return None

    return {
        "prompt_tokens": token_usage.get("prompt_tokens", 0),
        "completion_tokens": token_usage.get("completion_tokens", 0),
        "total_tokens": token_usage.get("total_tokens", 0),
    }


def find_last_user_message_content(messages: List[dict]) -> Optional[str]:
    """메시지 리스트에서 마지막 사용자 메시지 내용을 찾습니다."""
    for msg in reversed(messages):
        if msg.get("role") == "user":
            return msg.get("content", "")
    return None


def build_chat_history(messages: List[dict]) -> List[tuple]:
    """메시지 리스트를 Agent용 chat_history 형식으로 변환합니다."""
    chat_history = []
    for msg in messages:
        role = msg.get("role")
        content = msg.get("content", "")
        if role in ("assistant", "system"):
            chat_history.append((role, content))
    return chat_history


def format_search_results(search_results: List[dict]) -> str:
    """검색 결과를 문자열 형식으로 포맷합니다."""
    if not search_results:
        return ""

    formatted = "\n\n[검색 결과]\n"
    for i, result in enumerate(search_results[:MAX_SEARCH_RESULTS], 1):
        content = result.get("content", "") or result.get("snippet", "")
        url = result.get("url", "")
        formatted += f"{i}. {content}\n출처: {url}\n\n"

    return formatted


# =============================================================================
# OpenAI 서비스 클래스
# =============================================================================

class OpenAIService:
    """Langchain을 사용한 OpenAI 서비스"""

    def __init__(self):
        if not settings.OPENAI_API_KEY:
            raise ValueError("OPENAI_API_KEY가 설정되지 않았습니다.")
        self._api_key = settings.OPENAI_API_KEY

    # -------------------------------------------------------------------------
    # LLM 생성
    # -------------------------------------------------------------------------

    def _create_llm(
        self,
        model: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: int = 1000,
        streaming: bool = False
    ) -> ChatOpenAI:
        """
        Langchain ChatOpenAI 인스턴스를 생성합니다.

        Args:
            model: 사용할 모델명 (None이면 기본 모델 사용)
            temperature: 응답의 창의성 조절 (0.0~2.0)
            max_tokens: 최대 토큰 수
            streaming: 스트리밍 모드 활성화 여부

        Returns:
            ChatOpenAI 인스턴스

        Raises:
            ValueError: 지원하지 않는 모델인 경우
        """
        model = model or DEFAULT_MODEL

        if not is_valid_model(model):
            raise ValueError(
                f"지원하지 않는 모델입니다: {model}. "
                f"사용 가능한 모델: {', '.join(AVAILABLE_MODELS)}"
            )

        llm_kwargs = {
            "model": model,
            "streaming": streaming,
            "openai_api_key": self._api_key,
        }

        # Reasoning 모델은 temperature를 지원하지 않음
        if not is_reasoning_model(model):
            llm_kwargs["temperature"] = temperature

        # Reasoning 모델은 max_completion_tokens 사용, 그 외는 max_tokens 사용
        token_param = "max_completion_tokens" if is_reasoning_model(model) else "max_tokens"
        llm_kwargs[token_param] = max_tokens

        return ChatOpenAI(**llm_kwargs)

    # -------------------------------------------------------------------------
    # 메시지 변환
    # -------------------------------------------------------------------------

    def _convert_messages(self, messages: List[dict]) -> List[BaseMessage]:
        """
        딕셔너리 형식의 메시지를 Langchain 메시지 객체로 변환합니다.

        Args:
            messages: role과 content를 포함한 딕셔너리 리스트

        Returns:
            Langchain BaseMessage 객체 리스트
        """
        message_map = {
            "user": HumanMessage,
            "assistant": AIMessage,
            "system": SystemMessage,
        }

        langchain_messages = []
        for msg in messages:
            role = msg.get("role", "user")
            content = msg.get("content", "")
            message_class = message_map.get(role, HumanMessage)
            langchain_messages.append(message_class(content=content))

        return langchain_messages

    # -------------------------------------------------------------------------
    # 단일 프롬프트 완성
    # -------------------------------------------------------------------------

    async def get_completion(
        self,
        message: str,
        model: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: int = 1000
    ) -> dict:
        """
        단일 프롬프트에 대한 완성 응답을 반환합니다.

        Args:
            message: 프롬프트 메시지
            model: 사용할 모델명
            temperature: 응답의 창의성 조절
            max_tokens: 최대 토큰 수

        Returns:
            response, model, usage를 포함한 딕셔너리
        """
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
                "usage": extract_token_usage(response)
            }
        except Exception as e:
            raise Exception(f"OpenAI API 호출 중 오류 발생: {str(e)}")

    async def stream_completion(
        self,
        message: str,
        model: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: int = 1000
    ) -> AsyncIterator[str]:
        """
        단일 프롬프트에 대한 스트리밍 응답을 반환합니다.

        Args:
            message: 프롬프트 메시지
            model: 사용할 모델명
            temperature: 응답의 창의성 조절
            max_tokens: 최대 토큰 수

        Yields:
            응답 텍스트 청크
        """
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

    # -------------------------------------------------------------------------
    # 채팅 완성 (대화 히스토리 포함)
    # -------------------------------------------------------------------------

    async def get_chat_completion(
        self,
        messages: List[dict],
        model: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: int = 1000,
        use_search: bool = False
    ) -> dict:
        """
        대화 히스토리를 포함한 채팅 완성 응답을 반환합니다.

        Args:
            messages: 대화 히스토리 (role, content 딕셔너리 리스트)
            model: 사용할 모델명
            temperature: 응답의 창의성 조절
            max_tokens: 최대 토큰 수
            use_search: 검색 기능 사용 여부

        Returns:
            response, model, usage를 포함한 딕셔너리
        """
        # 검색 기능이 활성화된 경우 Agent 사용
        if use_search and search_service.is_enabled:
            return await self._get_chat_with_agent(
                messages=messages,
                model=model,
                temperature=temperature,
                max_tokens=max_tokens
            )

        return await self._get_chat_basic(
            messages=messages,
            model=model,
            temperature=temperature,
            max_tokens=max_tokens
        )

    async def _get_chat_basic(
        self,
        messages: List[dict],
        model: Optional[str],
        temperature: float,
        max_tokens: int
    ) -> dict:
        """기본 채팅 완성 (검색 없음)"""
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
                "usage": extract_token_usage(response)
            }
        except Exception as e:
            raise Exception(f"OpenAI API 호출 중 오류 발생: {str(e)}")

    async def stream_chat_completion(
        self,
        messages: List[dict],
        model: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: int = 1000,
        use_search: bool = False
    ) -> AsyncIterator[str]:
        """
        대화 히스토리를 포함한 채팅 스트리밍 응답을 반환합니다.

        Args:
            messages: 대화 히스토리
            model: 사용할 모델명
            temperature: 응답의 창의성 조절
            max_tokens: 최대 토큰 수
            use_search: 검색 기능 사용 여부

        Yields:
            응답 텍스트 청크
        """
        # 검색 기능이 활성화된 경우 Agent로 처리 후 결과를 스트리밍
        if use_search and search_service.is_enabled:
            async for chunk in self._stream_chat_with_agent(
                messages=messages,
                model=model,
                temperature=temperature,
                max_tokens=max_tokens
            ):
                yield chunk
            return

        # 기본 스트리밍
        async for chunk in self._stream_chat_basic(
            messages=messages,
            model=model,
            temperature=temperature,
            max_tokens=max_tokens
        ):
            yield chunk

    async def _stream_chat_basic(
        self,
        messages: List[dict],
        model: Optional[str],
        temperature: float,
        max_tokens: int
    ) -> AsyncIterator[str]:
        """기본 채팅 스트리밍 (검색 없음)"""
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

    async def _stream_chat_with_agent(
        self,
        messages: List[dict],
        model: Optional[str],
        temperature: float,
        max_tokens: int
    ) -> AsyncIterator[str]:
        """Agent를 사용한 채팅 스트리밍 (검색 포함)"""
        try:
            # Agent는 완전한 스트리밍을 지원하지 않으므로
            # 먼저 응답을 생성한 후 문자 단위로 스트리밍
            result = await self._get_chat_with_agent(
                messages=messages,
                model=model,
                temperature=temperature,
                max_tokens=max_tokens
            )
            response_text = result.get("response", "")
            for char in response_text:
                yield char
        except Exception:
            # Agent 실패 시 기본 스트리밍으로 폴백
            async for chunk in self._stream_chat_basic(
                messages=messages,
                model=model,
                temperature=temperature,
                max_tokens=max_tokens
            ):
                yield chunk

    # -------------------------------------------------------------------------
    # Agent 기반 채팅 (검색 기능 포함)
    # -------------------------------------------------------------------------

    async def _get_chat_with_agent(
        self,
        messages: List[dict],
        model: Optional[str],
        temperature: float,
        max_tokens: int
    ) -> dict:
        """Agent를 사용한 채팅 완성 (검색 툴 포함)"""
        # Agent 기능이 없으면 수동 검색으로 폴백
        if create_openai_tools_agent is None or AgentExecutor is None:
            return await self._get_chat_with_manual_search(
                messages=messages,
                model=model,
                temperature=temperature,
                max_tokens=max_tokens
            )

        tools = search_service.get_tools()
        if not tools:
            # 검색 툴이 없으면 기본 채팅으로 폴백
            return await self._get_chat_basic(
                messages=messages,
                model=model,
                temperature=temperature,
                max_tokens=max_tokens
            )

        return await self._execute_agent(
            messages=messages,
            model=model,
            temperature=temperature,
            max_tokens=max_tokens,
            tools=tools
        )

    async def _execute_agent(
        self,
        messages: List[dict],
        model: Optional[str],
        temperature: float,
        max_tokens: int,
        tools: list
    ) -> dict:
        """Agent를 실행하여 응답을 생성합니다."""
        llm = self._create_llm(
            model=model,
            temperature=temperature,
            max_tokens=max_tokens,
            streaming=False
        )

        # Agent 프롬프트 생성
        prompt = ChatPromptTemplate.from_messages([
            ("system", AGENT_SYSTEM_PROMPT),
            MessagesPlaceholder(variable_name="chat_history"),
            ("human", "{input}"),
            MessagesPlaceholder(variable_name="agent_scratchpad"),
        ])

        agent = create_openai_tools_agent(llm, tools, prompt)
        agent_executor = AgentExecutor(agent=agent, tools=tools, verbose=False)

        last_user_message = find_last_user_message_content(messages)
        if not last_user_message:
            raise ValueError("사용자 메시지를 찾을 수 없습니다.")

        chat_history = build_chat_history(messages)

        try:
            result = await agent_executor.ainvoke({
                "input": last_user_message,
                "chat_history": chat_history
            })
            return {
                "response": result.get("output", ""),
                "model": model,
                "usage": None  # Agent 사용 시 토큰 사용량 추적이 복잡하므로 None
            }
        except Exception as e:
            raise Exception(f"Agent 실행 중 오류 발생: {str(e)}")

    async def _get_chat_with_manual_search(
        self,
        messages: List[dict],
        model: Optional[str],
        temperature: float,
        max_tokens: int
    ) -> dict:
        """수동 검색을 포함한 채팅 완성 (Agent가 없는 경우 폴백)"""
        last_user_message = find_last_user_message_content(messages)
        if not last_user_message:
            raise ValueError("사용자 메시지를 찾을 수 없습니다.")

        # 검색 수행
        search_results = await search_service.search(last_user_message)
        search_context = format_search_results(search_results)

        # 검색 결과를 메시지에 추가
        enhanced_messages = self._inject_search_context(messages, search_context)

        return await self._get_chat_basic(
            messages=enhanced_messages,
            model=model,
            temperature=temperature,
            max_tokens=max_tokens
        )

    def _inject_search_context(
        self,
        messages: List[dict],
        search_context: str
    ) -> List[dict]:
        """검색 결과를 시스템 메시지에 주입합니다."""
        if not search_context:
            return messages

        enhanced_messages = [msg.copy() for msg in messages]

        # 기존 시스템 메시지 찾기
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

        return enhanced_messages


# =============================================================================
# 싱글톤 인스턴스
# =============================================================================

openai_service = OpenAIService()
