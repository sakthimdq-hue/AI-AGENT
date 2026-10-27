#!/usr/bin/env bash
# ==============================================================================
# SakthiDev Studio - Automated Windows (.EXE) Builder
# Packages the agent into a standalone Windows x64 executable & zip archive
# ==============================================================================

set -e

PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
DIST_DIR="$PROJECT_DIR/dist"
WINDOWS_BUILD_DIR="$DIST_DIR/windows_exe"
APP_NAME="SakthiDev Studio"
PORT=8000
LOCAL_IP="${1:-$(hostname -I | awk '{print $1}')}"
URL="http://${LOCAL_IP}:$PORT"

echo "=================================================================="
echo "🪟 Building & Packaging Windows (.EXE) for $APP_NAME"
echo "🌐 Configured Target URL: $URL"
echo "=================================================================="

# Ensure wine64 compatibility symlink
mkdir -p "$HOME/.local/bin"
if [ ! -f "$HOME/.local/bin/wine64" ] && which wine >/dev/null 2>&1; then
    ln -sf "$(which wine)" "$HOME/.local/bin/wine64"
fi
export PATH="$HOME/.local/bin:$PATH"

mkdir -p "$DIST_DIR"

ZIP_NAME="sakthidev-studio-windows.zip"
ZIP_PATH="$DIST_DIR/$ZIP_NAME"

if [ -f "$ZIP_PATH" ]; then
    echo "⚡ Existing Windows Electron runtime found. Updating and applying connection patch..."
    "$PROJECT_DIR/venv/bin/python3" "$PROJECT_DIR/patch_windows.py" "$LOCAL_IP"
else
    rm -rf "$WINDOWS_BUILD_DIR"
    echo "⚙️ Packaging with Electron native engine..."
    npx -y nativefier \
        --platform windows \
        --arch x64 \
        --name "$APP_NAME" \
        "$URL" \
        "$WINDOWS_BUILD_DIR" \
        --no-overwrite

    EXE_PATH="$(find "$WINDOWS_BUILD_DIR" -name "*.exe" | head -n 1)"
    if [ -f "$EXE_PATH" ]; then
        cd "$WINDOWS_BUILD_DIR"
        zip -q -r "$ZIP_PATH" .
        cd "$PROJECT_DIR"
        rm -rf "$WINDOWS_BUILD_DIR"
        "$PROJECT_DIR/venv/bin/python3" "$PROJECT_DIR/patch_windows.py" "$LOCAL_IP"
    else
        echo "❌ Error: Windows .exe was not generated."
        exit 1
    fi
fi

echo "=================================================================="
echo "🎉 SUCCESS! Windows Executable Package ready at:"
echo "   $ZIP_PATH"
echo "=================================================================="

