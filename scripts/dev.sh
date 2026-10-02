#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."
if [ -f backend/.env ]; then
  set -a
  source backend/.env
  set +a
fi
export DEBUG=true
if [ ! -x .venv/bin/python ]; then python3 -m venv .venv; fi
.venv/bin/pip install -r backend/requirements.txt
npm ci --prefix frontend
.venv/bin/python backend/manage.py migrate
.venv/bin/python backend/manage.py seed_demo
.venv/bin/python backend/manage.py runserver 127.0.0.1:8000 --noreload &
backend_pid=$!
trap 'kill "$backend_pid" 2>/dev/null || true' EXIT INT TERM
npm run dev --prefix frontend
