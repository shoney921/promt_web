"""OpenAI 모델 상수 정의"""

from typing import List, Dict

# 사용 가능한 OpenAI 모델 목록
AVAILABLE_MODELS: List[str] = [
    "gpt-4o-mini",
    "gpt-4o",
    "gpt-4-turbo",
    "gpt-4",
    "gpt-3.5-turbo",
]

# 기본 모델
DEFAULT_MODEL: str = "gpt-4o-mini"

# 모델 정보
MODEL_INFO: Dict[str, Dict[str, str]] = {
    "gpt-4o-mini": {
        "label": "GPT-4o Mini",
        "description": "빠르고 저렴한 모델",
        "category": "gpt-4",
    },
    "gpt-4o": {
        "label": "GPT-4o",
        "description": "최신 고성능 모델",
        "category": "gpt-4",
    },
    "gpt-4-turbo": {
        "label": "GPT-4 Turbo",
        "description": "고성능 모델",
        "category": "gpt-4",
    },
    "gpt-4": {
        "label": "GPT-4",
        "description": "표준 고성능 모델",
        "category": "gpt-4",
    },
    "gpt-3.5-turbo": {
        "label": "GPT-3.5 Turbo",
        "description": "빠른 응답 모델",
        "category": "gpt-3.5",
    },
}


def is_valid_model(model: str) -> bool:
    """모델이 유효한지 확인"""
    return model in AVAILABLE_MODELS


def get_model_info(model: str) -> Dict[str, str]:
    """모델 정보 반환"""
    return MODEL_INFO.get(model, {
        "label": model,
        "description": "알 수 없는 모델",
        "category": "unknown",
    })
