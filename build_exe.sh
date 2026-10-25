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
URL="http://localhost:$PORT"

echo "=================================================================="
echo "🪟 Building Windows (.EXE) Package for $APP_NAME"
echo "=================================================================="

# Ensure wine64 compatibility symlink
mkdir -p "$HOME/.local/bin"
if [ ! -f "$HOME/.local/bin/wine64" ] && which wine >/dev/null 2>&1; then
    ln -sf "$(which wine)" "$HOME/.local/bin/wine64"
fi
export PATH="$HOME/.local/bin:$PATH"

mkdir -p "$DIST_DIR"
rm -rf "$WINDOWS_BUILD_DIR"

echo "⚙️ Packaging with Electron native engine..."
npx nativefier \
    --platform windows \
    --arch x64 \
    --name "$APP_NAME" \
    "$URL" \
    "$WINDOWS_BUILD_DIR" \
    --no-overwrite

EXE_PATH="$(find "$WINDOWS_BUILD_DIR" -name "*.exe" | head -n 1)"

if [ -f "$EXE_PATH" ]; then
    echo "✅ Windows Executable generated successfully:"
    echo "   $EXE_PATH"
    
    echo "🧪 Testing binary format..."
    file "$EXE_PATH"

    echo "📦 Creating portable zip distribution..."
    ZIP_NAME="sakthidev-studio-windows.zip"
    cd "$WINDOWS_BUILD_DIR"
    zip -q -r "../$ZIP_NAME" .
    cd "$PROJECT_DIR"
    rm -rf "$WINDOWS_BUILD_DIR"
    
    echo "=================================================================="
    echo "🎉 SUCCESS! Windows Executable Package ready at:"
    echo "   $DIST_DIR/$ZIP_NAME"
    echo "=================================================================="
else
    echo "❌ Error: Windows .exe was not generated."
    exit 1
fi
