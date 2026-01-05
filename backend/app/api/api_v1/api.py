from fastapi import APIRouter
from app.api.api_v1.endpoints import auth, prompt, models, conversation

api_router = APIRouter()
api_router.include_router(auth.router, prefix="/auth", tags=["인증"])
api_router.include_router(prompt.router, prefix="/prompt", tags=["프롬프트"])
api_router.include_router(models.router, prefix="/models", tags=["모델"])
api_router.include_router(conversation.router, prefix="/conversations", tags=["대화"])
