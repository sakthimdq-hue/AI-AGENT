#!/usr/bin/env bash
# SakthiDev Studio Launcher Script

cd "$(dirname "$0")"

# Activate virtual environment if present
if [ -d "venv" ]; then
    source venv/bin/activate
fi

echo "=========================================================="
echo "⚡ Starting SakthiDev Studio - Autonomous AI Software Engineer"
echo "=========================================================="
echo "🌐 Open your browser at: http://localhost:8000"
echo "⚙️ Model: Google Gemini Free Cloud / Local Ollama"
echo "💾 SQLite Memory: memory.db active"
echo "=========================================================="

./venv/bin/python3 -m uvicorn server:app --host 0.0.0.0 --port 8000
