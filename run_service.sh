#!/usr/bin/env bash
# Runner for SakthiDev Studio Background Service
DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$DIR"

exec "$DIR/venv/bin/python3" -m uvicorn server:app --host 0.0.0.0 --port 8000 --reload
