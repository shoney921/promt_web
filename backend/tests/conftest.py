import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
from app.main import app
from app.core.database import get_db, Base
from app.core.security import create_access_token
from app.models.user import User
from app.core.config import settings

# 모든 모델을 import하여 Base에 등록
from app.models import user

# 테스트용 인메모리 SQLite 데이터베이스
SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture(scope="function")
def db():
    """테스트용 데이터베이스 세션"""
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()
        Base.metadata.drop_all(bind=engine)


@pytest.fixture(scope="function")
def client(db):
    """테스트 클라이언트"""
    def override_get_db():
        try:
            yield db
        finally:
            pass
    
    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()


@pytest.fixture
def test_user(db):
    """테스트용 사용자 생성"""
    from app.services.auth_service import AuthService
    from app.schemas.user import UserCreate
    
    auth_service = AuthService()
    user_data = UserCreate(
        email="test@example.com",
        password="testpassword123",
        full_name="Test User"
    )
    user = auth_service.create_user(db, user_data)
    return user


@pytest.fixture
def auth_token(test_user):
    """테스트용 인증 토큰"""
    return create_access_token(data={"sub": test_user.email})


@pytest.fixture
def auth_headers(auth_token):
    """인증 헤더"""
    return {"Authorization": f"Bearer {auth_token}"}
