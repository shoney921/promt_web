import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from app.services.openai_service import OpenAIService
from app.core.config import settings


class TestOpenAIService:
    """OpenAI 서비스 테스트"""
    
    @pytest.fixture
    def mock_openai_key(self, monkeypatch):
        """OpenAI API 키 모킹"""
        monkeypatch.setenv("OPENAI_API_KEY", "test-api-key")
        monkeypatch.setattr(settings, "OPENAI_API_KEY", "test-api-key")
    
    @pytest.fixture
    def service(self, mock_openai_key):
        """OpenAI 서비스 인스턴스"""
        return OpenAIService()
    
    def test_init_without_api_key(self, monkeypatch):
        """API 키 없이 초기화 시 에러"""
        monkeypatch.setattr(settings, "OPENAI_API_KEY", "")
        with pytest.raises(ValueError, match="OPENAI_API_KEY가 설정되지 않았습니다"):
            OpenAIService()
    
    @patch('app.services.openai_service.ChatOpenAI')
    def test_get_completion(self, mock_chat_openai, service):
        """get_completion 메서드 테스트"""
        # Mock ChatOpenAI 인스턴스
        mock_llm = MagicMock()
        mock_response = MagicMock()
        mock_response.content = "테스트 응답"
        mock_response.response_metadata = MagicMock()
        mock_response.response_metadata.token_usage = {
            "prompt_tokens": 10,
            "completion_tokens": 20,
            "total_tokens": 30
        }
        mock_llm.ainvoke = AsyncMock(return_value=mock_response)
        mock_chat_openai.return_value = mock_llm
        
        import asyncio
        result = asyncio.run(service.get_completion("테스트 메시지"))
        
        assert result["response"] == "테스트 응답"
        assert result["model"] == "gpt-4o-mini"
        assert result["usage"]["total_tokens"] == 30
        mock_llm.ainvoke.assert_called_once()
    
    @patch('app.services.openai_service.ChatOpenAI')
    def test_get_chat_completion(self, mock_chat_openai, service):
        """get_chat_completion 메서드 테스트"""
        # Mock ChatOpenAI 인스턴스
        mock_llm = MagicMock()
        mock_response = MagicMock()
        mock_response.content = "채팅 응답"
        mock_response.response_metadata = MagicMock()
        mock_response.response_metadata.token_usage = {
            "prompt_tokens": 15,
            "completion_tokens": 25,
            "total_tokens": 40
        }
        mock_llm.ainvoke = AsyncMock(return_value=mock_response)
        mock_chat_openai.return_value = mock_llm
        
        import asyncio
        messages = [
            {"role": "user", "content": "안녕하세요"},
            {"role": "assistant", "content": "안녕하세요!"}
        ]
        result = asyncio.run(service.get_chat_completion(messages))
        
        assert result["response"] == "채팅 응답"
        assert result["model"] == "gpt-4o-mini"
        mock_llm.ainvoke.assert_called_once()
    
    def test_convert_messages(self, service):
        """메시지 변환 테스트"""
        messages = [
            {"role": "user", "content": "사용자 메시지"},
            {"role": "assistant", "content": "어시스턴트 메시지"},
            {"role": "system", "content": "시스템 메시지"}
        ]
        
        from langchain_core.messages import HumanMessage, AIMessage, SystemMessage
        
        result = service._convert_messages(messages)
        
        assert len(result) == 3
        assert isinstance(result[0], HumanMessage)
        assert isinstance(result[1], AIMessage)
        assert isinstance(result[2], SystemMessage)
        assert result[0].content == "사용자 메시지"
        assert result[1].content == "어시스턴트 메시지"
        assert result[2].content == "시스템 메시지"
