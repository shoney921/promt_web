#!/bin/bash

# 도커 컨테이너 내에서 테스트 실행 스크립트

echo "🧪 도커 컨테이너 내에서 테스트 실행 중..."

# 옵션 파라미터 처리
TEST_FILE=""
TEST_FUNCTION=""
VERBOSE="-v"
USE_EXISTING=false

while [[ $# -gt 0 ]]; do
    case $1 in
        -f|--file)
            TEST_FILE="$2"
            shift 2
            ;;
        -k|--keyword)
            TEST_FUNCTION="$2"
            shift 2
            ;;
        -v|--verbose)
            VERBOSE="-v"
            shift
            ;;
        -q|--quiet)
            VERBOSE=""
            shift
            ;;
        -e|--existing)
            USE_EXISTING=true
            shift
            ;;
        -h|--help)
            echo "사용법: $0 [옵션]"
            echo ""
            echo "옵션:"
            echo "  -f, --file FILE        특정 테스트 파일 실행 (예: test_prompt.py)"
            echo "  -k, --keyword KEYWORD   키워드로 테스트 필터링"
            echo "  -v, --verbose          상세 출력 (기본값)"
            echo "  -q, --quiet            간단한 출력"
            echo "  -e, --existing         실행 중인 컨테이너 사용 (없으면 새로 생성)"
            echo "  -h, --help            도움말 표시"
            echo ""
            echo "예제:"
            echo "  $0                                    # 전체 테스트"
            echo "  $0 -f test_prompt.py                 # 특정 파일 테스트"
            echo "  $0 -k test_completion                # 키워드로 필터링"
            echo "  $0 -f test_prompt.py -k success       # 파일과 키워드 조합"
            echo "  $0 -e                                 # 실행 중인 컨테이너 사용"
            exit 0
            ;;
        *)
            echo "알 수 없는 옵션: $1"
            echo "도움말: $0 --help"
            exit 1
            ;;
    esac
done

# 테스트 명령어 구성
TEST_CMD="pytest tests/"

if [ -n "$TEST_FILE" ]; then
    # 파일명에 .py 확장자가 없으면 추가
    if [[ ! "$TEST_FILE" == *.py ]]; then
        TEST_FILE="${TEST_FILE}.py"
    fi
    TEST_CMD="pytest tests/$TEST_FILE"
fi

if [ -n "$TEST_FUNCTION" ]; then
    TEST_CMD="$TEST_CMD -k $TEST_FUNCTION"
fi

if [ -n "$VERBOSE" ]; then
    TEST_CMD="$TEST_CMD $VERBOSE"
fi

TEST_CMD="$TEST_CMD --tb=short"

echo "실행 명령: $TEST_CMD"
echo ""

# 프로젝트 루트로 이동
cd "$(dirname "$0")/.." || exit 1

# 백엔드 컨테이너가 실행 중인지 확인
if [ "$USE_EXISTING" = true ] && docker ps | grep -q ai_prompt_backend; then
    echo "✅ 기존 백엔드 컨테이너에서 테스트 실행..."
    docker exec ai_prompt_backend $TEST_CMD
elif docker ps | grep -q ai_prompt_backend && [ "$USE_EXISTING" != false ]; then
    echo "✅ 기존 백엔드 컨테이너에서 테스트 실행..."
    docker exec ai_prompt_backend $TEST_CMD
else
    echo "🚀 테스트 전용 컨테이너 실행..."
    docker-compose --profile test run --rm backend-test $TEST_CMD
fi

echo ""
echo "✅ 테스트 완료!"
