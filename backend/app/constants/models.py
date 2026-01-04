"""OpenAI 모델 상수 정의"""

from typing import List, Dict

# 사용 가능한 OpenAI 모델 목록 (OpenAI 공식 문서 기준)
AVAILABLE_MODELS: List[str] = [
    # GPT-5 시리즈
    "gpt-5",
    "gpt-5.1",
    "gpt-5.2",
    "gpt-5-mini",
    "gpt-5-nano",
    # GPT-4o 시리즈
    "gpt-4o",
    "gpt-4o-mini",
    "gpt-4o-2024-05-13",
    "gpt-4o-2024-08-06",
    "gpt-4o-2024-11-20",
    # GPT-4 시리즈
    "gpt-4-turbo",
    "gpt-4-turbo-2024-04-09",
    "gpt-4-turbo-preview",
    "gpt-4-0125-preview",
    "gpt-4-1106-preview",
    "gpt-4",
    "gpt-4-32k",
    "gpt-4-0613",
    "gpt-4-32k-0613",
    # GPT-3.5 시리즈
    "gpt-3.5-turbo",
    "gpt-3.5-turbo-0125",
    "gpt-3.5-turbo-1106",
    "gpt-3.5-turbo-16k",
    "gpt-3.5-turbo-0613",
    "gpt-3.5-turbo-16k-0613",
    # o1/o3 시리즈 (Reasoning 모델)
    "o1-preview",
    "o1-mini",
    "o1",
    "o3",
    "o3-mini",
    "o3-pro",
    "o1-2024-12-17",
    "o1-mini-2024-09-12",
]

# 기본 모델
DEFAULT_MODEL: str = "gpt-4o-mini"

# 모델 정보
MODEL_INFO: Dict[str, Dict[str, str]] = {
    # GPT-5 시리즈
    "gpt-5": {
        "label": "GPT-5",
        "description": "최신 고성능 GPT-5 모델",
        "category": "gpt-5",
    },
    "gpt-5.1": {
        "label": "GPT-5.1",
        "description": "GPT-5.1 버전 모델",
        "category": "gpt-5",
    },
    "gpt-5.2": {
        "label": "GPT-5.2",
        "description": "코딩 및 에이전트 작업에 최적화된 최신 모델",
        "category": "gpt-5",
    },
    "gpt-5-mini": {
        "label": "GPT-5 Mini",
        "description": "경량화된 GPT-5 모델",
        "category": "gpt-5",
    },
    "gpt-5-nano": {
        "label": "GPT-5 Nano",
        "description": "가장 작은 GPT-5 모델",
        "category": "gpt-5",
    },
    # GPT-4o 시리즈
    "gpt-4o": {
        "label": "GPT-4o",
        "description": "최신 고성능 멀티모달 모델 (2024년 5월)",
        "category": "gpt-4o",
    },
    "gpt-4o-mini": {
        "label": "GPT-4o Mini",
        "description": "빠르고 저렴한 GPT-4o 모델",
        "category": "gpt-4o",
    },
    "gpt-4o-2024-05-13": {
        "label": "GPT-4o (2024-05-13)",
        "description": "GPT-4o 특정 버전",
        "category": "gpt-4o",
    },
    "gpt-4o-2024-08-06": {
        "label": "GPT-4o (2024-08-06)",
        "description": "GPT-4o 특정 버전",
        "category": "gpt-4o",
    },
    "gpt-4o-2024-11-20": {
        "label": "GPT-4o (2024-11-20)",
        "description": "GPT-4o 최신 버전",
        "category": "gpt-4o",
    },
    # GPT-4 시리즈
    "gpt-4-turbo": {
        "label": "GPT-4 Turbo",
        "description": "고성능 GPT-4 Turbo 모델",
        "category": "gpt-4",
    },
    "gpt-4-turbo-2024-04-09": {
        "label": "GPT-4 Turbo (2024-04-09)",
        "description": "GPT-4 Turbo 특정 버전",
        "category": "gpt-4",
    },
    "gpt-4-turbo-preview": {
        "label": "GPT-4 Turbo Preview",
        "description": "GPT-4 Turbo 미리보기 버전",
        "category": "gpt-4",
    },
    "gpt-4-0125-preview": {
        "label": "GPT-4 (2024-01-25 Preview)",
        "description": "GPT-4 미리보기 버전",
        "category": "gpt-4",
    },
    "gpt-4-1106-preview": {
        "label": "GPT-4 (2023-11-06 Preview)",
        "description": "GPT-4 미리보기 버전",
        "category": "gpt-4",
    },
    "gpt-4": {
        "label": "GPT-4",
        "description": "표준 GPT-4 모델",
        "category": "gpt-4",
    },
    "gpt-4-32k": {
        "label": "GPT-4 32k",
        "description": "긴 컨텍스트를 지원하는 GPT-4 모델",
        "category": "gpt-4",
    },
    "gpt-4-0613": {
        "label": "GPT-4 (2023-06-13)",
        "description": "GPT-4 특정 버전",
        "category": "gpt-4",
    },
    "gpt-4-32k-0613": {
        "label": "GPT-4 32k (2023-06-13)",
        "description": "GPT-4 32k 특정 버전",
        "category": "gpt-4",
    },
    # GPT-3.5 시리즈
    "gpt-3.5-turbo": {
        "label": "GPT-3.5 Turbo",
        "description": "빠른 응답 모델",
        "category": "gpt-3.5",
    },
    "gpt-3.5-turbo-0125": {
        "label": "GPT-3.5 Turbo (2024-01-25)",
        "description": "GPT-3.5 Turbo 최신 버전",
        "category": "gpt-3.5",
    },
    "gpt-3.5-turbo-1106": {
        "label": "GPT-3.5 Turbo (2023-11-06)",
        "description": "GPT-3.5 Turbo 특정 버전",
        "category": "gpt-3.5",
    },
    "gpt-3.5-turbo-16k": {
        "label": "GPT-3.5 Turbo 16k",
        "description": "긴 컨텍스트를 지원하는 GPT-3.5 Turbo",
        "category": "gpt-3.5",
    },
    "gpt-3.5-turbo-0613": {
        "label": "GPT-3.5 Turbo (2023-06-13)",
        "description": "GPT-3.5 Turbo 특정 버전",
        "category": "gpt-3.5",
    },
    "gpt-3.5-turbo-16k-0613": {
        "label": "GPT-3.5 Turbo 16k (2023-06-13)",
        "description": "GPT-3.5 Turbo 16k 특정 버전",
        "category": "gpt-3.5",
    },
    # o1/o3 시리즈 (Reasoning 모델)
    "o1-preview": {
        "label": "O1 Preview",
        "description": "추론 능력이 향상된 모델 (미리보기)",
        "category": "o1",
    },
    "o1-mini": {
        "label": "O1 Mini",
        "description": "빠른 추론 모델",
        "category": "o1",
    },
    "o1": {
        "label": "O1",
        "description": "추론 능력이 향상된 모델",
        "category": "o1",
    },
    "o3": {
        "label": "O3",
        "description": "최신 추론 모델",
        "category": "o1",
    },
    "o3-mini": {
        "label": "O3 Mini",
        "description": "최신 추론 모델 (미니)",
        "category": "o1",
    },
    "o3-pro": {
        "label": "O3 Pro",
        "description": "최신 추론 모델 (프로)",
        "category": "o1",
    },
    "o1-2024-12-17": {
        "label": "O1 (2024-12-17)",
        "description": "O1 특정 버전",
        "category": "o1",
    },
    "o1-mini-2024-09-12": {
        "label": "O1 Mini (2024-09-12)",
        "description": "O1 Mini 특정 버전",
        "category": "o1",
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
