#!/usr/bin/env bash
# SakthiDev Studio - App Window Launcher
# Opens as standalone native window using Chrome/Chromium app mode or default browser.

APP_URL="http://localhost:8000"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

is_up() {
    [ "$(curl -s -o /dev/null -w "%{http_code}" "$APP_URL" 2>/dev/null)" = "200" ]
}

# Check if server is running; if not, trigger systemd service or start background process
if ! is_up; then
    # Try starting user systemd service if active
    systemctl --user start sakthidev-studio 2>/dev/null || true
    sleep 1
    # If still not running, run via venv in background
    if ! is_up; then
        nohup "$SCRIPT_DIR/venv/bin/python3" -m uvicorn server:app --host 0.0.0.0 --port 8000 --reload > "$SCRIPT_DIR/server.log" 2>&1 &
        sleep 2
    fi
fi

# Open in Native App Window (Chrome/Chromium app mode)
if which google-chrome >/dev/null 2>&1; then
    google-chrome --app="$APP_URL" --user-data-dir="/tmp/sakthidev_chrome_profile" &
elif which chromium >/dev/null 2>&1; then
    chromium --app="$APP_URL" &
elif which brave-browser >/dev/null 2>&1; then
    brave-browser --app="$APP_URL" &
else
    xdg-open "$APP_URL" &
fi
