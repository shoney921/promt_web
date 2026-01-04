from fastapi import APIRouter
from app.api.api_v1.endpoints import auth, prompt

api_router = APIRouter()
api_router.include_router(auth.router, prefix="/auth", tags=["인증"])
api_router.include_router(prompt.router, prefix="/prompt", tags=["프롬프트"])
