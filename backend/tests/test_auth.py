import pytest
from fastapi import status


class TestAuthEndpoints:
    """인증 엔드포인트 테스트"""
    
    def test_register_success(self, client):
        """회원가입 성공 테스트"""
        response = client.post(
            "/api/v1/auth/register",
            json={
                "email": "newuser@example.com",
                "password": "password123",
                "full_name": "New User"
            }
        )
        
        assert response.status_code == status.HTTP_201_CREATED
        data = response.json()
        assert "access_token" in data
        assert "token_type" in data
        assert data["token_type"] == "bearer"
    
    def test_register_duplicate_email(self, client, test_user):
        """중복 이메일 회원가입 테스트"""
        response = client.post(
            "/api/v1/auth/register",
            json={
                "email": "test@example.com",  # 이미 존재하는 이메일
                "password": "password123",
                "full_name": "Test User"
            }
        )
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST
    
    def test_login_success(self, client, test_user):
        """로그인 성공 테스트"""
        response = client.post(
            "/api/v1/auth/login",
            json={
                "email": "test@example.com",
                "password": "testpassword123"
            }
        )
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "access_token" in data
        assert "token_type" in data
        assert data["token_type"] == "bearer"
    
    def test_login_invalid_credentials(self, client, test_user):
        """잘못된 자격증명으로 로그인 테스트"""
        response = client.post(
            "/api/v1/auth/login",
            json={
                "email": "test@example.com",
                "password": "wrongpassword"
            }
        )
        
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
    
    def test_login_nonexistent_user(self, client):
        """존재하지 않는 사용자 로그인 테스트"""
        response = client.post(
            "/api/v1/auth/login",
            json={
                "email": "nonexistent@example.com",
                "password": "password123"
            }
        )
        
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
