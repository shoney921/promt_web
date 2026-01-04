import pytest
from fastapi import status
from unittest.mock import AsyncMock, patch, MagicMock


class TestPromptEndpoints:
    """프롬프트 엔드포인트 테스트"""
    
    def test_completion_without_auth(self, client):
        """인증 없이 completion 엔드포인트 접근 시 401 에러"""
        response = client.post(
            "/api/v1/prompt/completion",
            json={
                "message": "안녕하세요",
                "stream": False
            }
        )
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
    
    @patch('app.api.api_v1.endpoints.prompt.openai_service')
    def test_completion_success(self, mock_service, client, auth_headers):
        """completion 엔드포인트 성공 테스트"""
        # Mock 응답 설정
        mock_response = {
            "response": "안녕하세요! 무엇을 도와드릴까요?",
            "model": "gpt-4o-mini",
            "usage": {
                "prompt_tokens": 10,
                "completion_tokens": 20,
                "total_tokens": 30
            }
        }
        mock_service.get_completion = AsyncMock(return_value=mock_response)
        
        response = client.post(
            "/api/v1/prompt/completion",
            headers=auth_headers,
            json={
                "message": "안녕하세요",
                "model": "gpt-4o-mini",
                "temperature": 0.7,
                "max_tokens": 1000,
                "stream": False
            }
        )
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "response" in data
        assert "model" in data
        assert data["response"] == "안녕하세요! 무엇을 도와드릴까요?"
        assert data["model"] == "gpt-4o-mini"
        mock_service.get_completion.assert_called_once()
    
    @patch('app.api.api_v1.endpoints.prompt.openai_service')
    def test_completion_stream(self, mock_service, client, auth_headers):
        """completion 스트리밍 테스트"""
        # Mock 스트리밍 응답
        async def mock_stream(message, model=None, temperature=None, max_tokens=None):
            chunks = ["안녕", "하세요", "!"]
            for chunk in chunks:
                yield chunk
        
        mock_service.stream_completion = mock_stream
        
        response = client.post(
            "/api/v1/prompt/completion",
            headers=auth_headers,
            json={
                "message": "안녕하세요",
                "stream": True
            }
        )
        
        assert response.status_code == status.HTTP_200_OK
        assert response.headers["content-type"] == "text/event-stream; charset=utf-8"
    
    def test_chat_without_auth(self, client):
        """인증 없이 chat 엔드포인트 접근 시 401 에러"""
        response = client.post(
            "/api/v1/prompt/chat",
            json={
                "messages": [
                    {"role": "user", "content": "안녕하세요"}
                ],
                "stream": False
            }
        )
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
    
    @patch('app.api.api_v1.endpoints.prompt.openai_service')
    def test_chat_success(self, mock_service, client, auth_headers):
        """chat 엔드포인트 성공 테스트"""
        # Mock 응답 설정
        mock_response = {
            "response": "안녕하세요! 무엇을 도와드릴까요?",
            "model": "gpt-4o-mini",
            "usage": {
                "prompt_tokens": 15,
                "completion_tokens": 25,
                "total_tokens": 40
            }
        }
        mock_service.get_chat_completion = AsyncMock(return_value=mock_response)
        
        response = client.post(
            "/api/v1/prompt/chat",
            headers=auth_headers,
            json={
                "messages": [
                    {"role": "user", "content": "안녕하세요"},
                    {"role": "assistant", "content": "안녕하세요! 무엇을 도와드릴까요?"},
                    {"role": "user", "content": "Python에 대해 알려주세요"}
                ],
                "model": "gpt-4o-mini",
                "temperature": 0.7,
                "max_tokens": 1000,
                "stream": False
            }
        )
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "response" in data
        assert "model" in data
        assert data["response"] == "안녕하세요! 무엇을 도와드릴까요?"
        mock_service.get_chat_completion.assert_called_once()
    
    @patch('app.api.api_v1.endpoints.prompt.openai_service')
    def test_chat_stream(self, mock_service, client, auth_headers):
        """chat 스트리밍 테스트"""
        # Mock 스트리밍 응답
        async def mock_stream(messages, model=None, temperature=None, max_tokens=None):
            chunks = ["Python은", " 프로그래밍", " 언어입니다."]
            for chunk in chunks:
                yield chunk
        
        mock_service.stream_chat_completion = mock_stream
        
        response = client.post(
            "/api/v1/prompt/chat",
            headers=auth_headers,
            json={
                "messages": [
                    {"role": "user", "content": "Python에 대해 알려주세요"}
                ],
                "stream": True
            }
        )
        
        assert response.status_code == status.HTTP_200_OK
        assert response.headers["content-type"] == "text/event-stream; charset=utf-8"
    
    @patch('app.api.api_v1.endpoints.prompt.openai_service')
    def test_completion_invalid_request(self, mock_service, client, auth_headers):
        """잘못된 요청 파라미터 테스트"""
        mock_service.get_completion = AsyncMock(side_effect=ValueError("잘못된 요청입니다."))
        
        response = client.post(
            "/api/v1/prompt/completion",
            headers=auth_headers,
            json={
                "message": "",
                "temperature": 3.0,  # 범위를 벗어남
                "stream": False
            }
        )
        
        # Pydantic validation이 먼저 발생할 수 있지만, 서비스 레벨 에러도 처리
        assert response.status_code in [status.HTTP_400_BAD_REQUEST, status.HTTP_422_UNPROCESSABLE_ENTITY]
    
    @patch('app.api.api_v1.endpoints.prompt.openai_service')
    def test_completion_openai_error(self, mock_service, client, auth_headers):
        """OpenAI API 에러 처리 테스트"""
        mock_service.get_completion = AsyncMock(side_effect=Exception("OpenAI API 오류"))
        
        response = client.post(
            "/api/v1/prompt/completion",
            headers=auth_headers,
            json={
                "message": "테스트 메시지",
                "stream": False
            }
        )
        
        assert response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
        assert "오류 발생" in response.json()["detail"]
