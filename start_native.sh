#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")"
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
pip install -r requirements-dev.txt
mkdir -p .runtime
uvicorn virtual_robot.main:app --host 0.0.0.0 --port 8001 >.runtime/robot.log 2>&1 &
ROBOT_PID=$!
trap 'kill $ROBOT_PID 2>/dev/null || true' EXIT
export ROBOT_API_URL=http://127.0.0.1:8001
export DATABASE_URL=sqlite:///./rms.db
uvicorn app.main:app --app-dir dashboard --host 0.0.0.0 --port 8000
