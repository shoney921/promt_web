from fastapi import APIRouter, Depends
from app.api.deps import get_current_user
from app.models.user import User
from app.constants.models import AVAILABLE_MODELS, DEFAULT_MODEL, MODEL_INFO

router = APIRouter()


@router.get("/models")
async def get_available_models(
    current_user: User = Depends(get_current_user)
):
    """
    사용 가능한 OpenAI 모델 목록 반환
    """
    models = []
    for model_id in AVAILABLE_MODELS:
        info = MODEL_INFO.get(model_id, {})
        models.append({
            "value": model_id,
            "label": info.get("label", model_id),
            "description": info.get("description", ""),
            "category": info.get("category", "unknown"),
            "is_default": model_id == DEFAULT_MODEL,
        })
    
    return {
        "models": models,
        "default_model": DEFAULT_MODEL,
    }
