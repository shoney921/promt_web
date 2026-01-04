#!/bin/bash

# 테스트 실행 스크립트

echo "🧪 테스트 실행 중..."

# 가상환경 활성화 (선택사항)
# source venv/bin/activate

# pytest 실행
pytest tests/ -v --tb=short

echo "✅ 테스트 완료!"
