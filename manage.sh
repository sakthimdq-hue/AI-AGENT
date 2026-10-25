#!/usr/bin/env bash
# ==============================================================================
# SakthiDev Studio - Master Controller & Dynamic Lifecycle Manager
# ==============================================================================

PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SERVICE_NAME="sakthidev-studio"
USER_SYSTEMD_DIR="$HOME/.config/systemd/user"
USER_APPS_DIR="$HOME/.local/share/applications"
USER_ICONS_DIR="$HOME/.local/share/icons/hicolor/scalable/apps"
PORT=8000
URL="http://localhost:$PORT"

print_header() {
    echo "=========================================================="
    echo "⚡ SakthiDev Studio - Autonomous AI Software Engineer"
    echo "=========================================================="
}

is_running() {
    local code
    code="$(curl -s -o /dev/null -w "%{http_code}" "$URL" 2>/dev/null)"
    [ "$code" = "200" ]
}


case "$1" in
    start)
        print_header
        echo "🚀 Starting SakthiDev Studio..."
        if [ -f "$USER_SYSTEMD_DIR/$SERVICE_NAME.service" ]; then
            systemctl --user start $SERVICE_NAME
        else
            nohup "$PROJECT_DIR/venv/bin/python3" -m uvicorn server:app --host 0.0.0.0 --port $PORT --reload > "$PROJECT_DIR/server.log" 2>&1 &
        fi
        sleep 1
        if is_running; then
            echo "✅ Online at $URL (Hot-Reload Active)"
        else
            echo "⏳ Service starting up... check './manage.sh status' or './manage.sh logs'"
        fi
        ;;

    stop)
        print_header
        echo "🛑 Stopping SakthiDev Studio..."
        systemctl --user stop $SERVICE_NAME 2>/dev/null || true
        pkill -f "uvicorn server:app" 2>/dev/null || true
        echo "✅ Stopped."
        ;;

    restart)
        print_header
        echo "🔄 Restarting SakthiDev Studio..."
        if [ -f "$USER_SYSTEMD_DIR/$SERVICE_NAME.service" ]; then
            systemctl --user restart $SERVICE_NAME
        else
            pkill -f "uvicorn server:app" 2>/dev/null || true
            sleep 1
            nohup "$PROJECT_DIR/venv/bin/python3" -m uvicorn server:app --host 0.0.0.0 --port $PORT --reload > "$PROJECT_DIR/server.log" 2>&1 &
        fi
        sleep 1
        echo "✅ Restarted with latest changes!"
        ;;

    status)
        print_header
        if is_running; then
            echo "🟢 STATUS: RUNNING & HEALTHY"
            echo "🌐 Address: $URL"
            echo "⚙️ Mode: Live Hot-Reload (Edits to python or static files load instantly)"
            echo "PID(s): $(pgrep -f "uvicorn server:app" | tr '\n' ' ')"
        else
            echo "🔴 STATUS: STOPPED"
            echo "👉 Run './manage.sh start' or './manage.sh install-service' to run in background."
        fi
        ;;

    logs)
        print_header
        echo "📜 Showing live logs (Press Ctrl+C to exit)..."
        if systemctl --user is-active --quiet $SERVICE_NAME 2>/dev/null; then
            journalctl --user -u $SERVICE_NAME -f
        elif [ -f "$PROJECT_DIR/server.log" ]; then
            tail -f "$PROJECT_DIR/server.log"
        else
            echo "⚠️ No log file found yet. Start the service first."
        fi
        ;;

    open)
        "$PROJECT_DIR/open_app.sh"
        ;;

    install-service)
        print_header
        echo "⚙️ Installing Permanent Background Service & Desktop Launcher..."
        mkdir -p "$USER_SYSTEMD_DIR"
        mkdir -p "$USER_APPS_DIR"
        mkdir -p "$USER_ICONS_DIR"

        # Copy service and desktop entry
        cp "$PROJECT_DIR/$SERVICE_NAME.service" "$USER_SYSTEMD_DIR/"
        cp "$PROJECT_DIR/$SERVICE_NAME.desktop" "$USER_APPS_DIR/"
        if [ -f "$PROJECT_DIR/static/icon.svg" ]; then
            cp "$PROJECT_DIR/static/icon.svg" "$USER_ICONS_DIR/$SERVICE_NAME.svg"
        fi

        # Reload systemd and enable service
        systemctl --user daemon-reload
        systemctl --user enable $SERVICE_NAME
        systemctl --user restart $SERVICE_NAME

        # Enable linger so service starts on boot
        loginctl enable-linger "$USER" 2>/dev/null || true

        update-desktop-database "$USER_APPS_DIR" 2>/dev/null || true
        gtk-update-icon-cache -f -t "$HOME/.local/share/icons/hicolor" 2>/dev/null || true

        echo "✅ Installed successfully!"
        echo "✨ It will now run automatically whenever your PC boots!"
        echo "✨ 'SakthiDev Studio' is now available in your Ubuntu Application Menu!"
        echo "✨ Edits you make to the code will auto-reload immediately."
        ;;

    remove-service)
        print_header
        echo "🗑️ Removing User Service and Desktop Shortcut..."
        systemctl --user stop $SERVICE_NAME 2>/dev/null || true
        systemctl --user disable $SERVICE_NAME 2>/dev/null || true
        rm -f "$USER_SYSTEMD_DIR/$SERVICE_NAME.service"
        rm -f "$USER_APPS_DIR/$SERVICE_NAME.desktop"
        systemctl --user daemon-reload
        echo "✅ Removed."
        ;;

    build-deb)
        "$PROJECT_DIR/build_deb.sh"
        ;;

    build-exe)
        "$PROJECT_DIR/build_exe.sh"
        ;;

    build-apk)
        "$PROJECT_DIR/build_apk.sh" "$2"
        ;;

    build-all)
        print_header
        echo "🚀 Running Complete Multi-Platform Dynamic Build (.deb, .exe, .apk)..."
        "$PROJECT_DIR/build_deb.sh"
        echo ""
        "$PROJECT_DIR/build_exe.sh"
        echo ""
        "$PROJECT_DIR/build_apk.sh" "$2"
        echo ""
        echo "=========================================================="
        echo "🎉 ALL PACKAGES BUILT & TESTED SUCCESSFULLY!"
        echo "📁 Check the 'dist/' folder for your deliverables:"
        ls -lh "$PROJECT_DIR/dist"
        echo "=========================================================="
        ;;

    *)
        print_header
        echo "Usage: ./manage.sh [command]"
        echo ""
        echo "Commands:"
        echo "  start            - Start agent in background"
        echo "  stop             - Stop agent"
        echo "  restart          - Restart agent (applies code changes)"
        echo "  status           - Check if agent is currently running"
        echo "  logs             - Watch live server output logs"
        echo "  open             - Open agent in native desktop window"
        echo "  install-service  - Make it run 24/7 on system boot & add to App Menu"
        echo "  remove-service   - Remove the background service & desktop entry"
        echo "  build-deb        - Build dynamic Debian package (.deb)"
        echo "  build-exe        - Build standalone Windows executable package (.exe)"
        echo "  build-apk [IP]   - Build signed Android APK (.apk)"
        echo "  build-all        - Build and test all 3 platforms together (.deb, .exe, .apk)"
        ;;
esac
