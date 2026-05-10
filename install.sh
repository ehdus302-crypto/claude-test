#!/bin/sh
# claude-test 마켓플레이스 설치 스크립트
# 팀원은 이 파일 하나만 실행하면 됩니다.
#
# 사용법:
#   curl -fsSL https://raw.githubusercontent.com/ehdus302-crypto/claude-test/main/install.sh | sh
#   또는 저장소 클론 후: sh install.sh

set -e

MARKETPLACE="ehdus302-crypto/claude-test"
PLUGIN="moodboard-plugin@claude-test"

echo "▶ claude-test 마켓플레이스 등록 중..."
claude plugin marketplace add "$MARKETPLACE" --scope user

echo "▶ 마켓플레이스 최신화 중..."
claude plugin marketplace update claude-test

echo "▶ moodboard-plugin 설치 중..."
claude plugin install "$PLUGIN"

echo ""
echo "✓ 설치 완료!"
echo "  /moodboard  — Pinterest 레퍼런스 이미지 수집"
echo "  /sort-files — 폴더 파일 자동 정리"
