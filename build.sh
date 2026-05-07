#!/bin/bash
set -e

echo "=== [1/5] Python 가상환경 생성 ==="
uv venv .venv

echo "=== [2/5] Python 패키지 설치 ==="
uv pip install -r backend/requirements.txt

PYTHON=.venv/bin/python
echo "Python: $($PYTHON --version)"

echo "=== [3/5] DB 초기화 & 데이터 적재 ==="
$PYTHON -m backend.db.init_db
$PYTHON -m backend.services.seed_demo
$PYTHON -m backend.services.recompute_tiers

echo "=== [4/5] 정적 JSON 생성 (~3,000개) ==="
$PYTHON -m backend.scripts.build_static_api

echo "=== [5/5] Vite 빌드 ==="
cd frontend && npx vite build

echo "=== 빌드 완료 ==="
