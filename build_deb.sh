#!/usr/bin/env bash
# ==============================================================================
# SakthiDev Studio - Dynamic .DEB Package Builder
# Cleans old builds, captures latest code changes, and produces a fresh .deb
# ==============================================================================

set -e

PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BUILD_ROOT="$PROJECT_DIR/deb_build"
DIST_DIR="$PROJECT_DIR/dist"
APP_NAME="sakthidev-studio"

# 1. Version generation (Semantic + Timestamp for automatic upgrade detection)
VERSION="1.0.$(date +%Y%m%d%H%M)"
echo "------------------------------------------------------------------"
echo "📦 Building Dynamic Debian Package for $APP_NAME (Version: $VERSION)"
echo "------------------------------------------------------------------"

# 2. Clean up old builds (Delete old .deb and replace with new)
echo "🧹 Cleaning previous build artifacts..."
rm -rf "$BUILD_ROOT"
mkdir -p "$DIST_DIR"
rm -f "$DIST_DIR"/*.deb
mkdir -p "$BUILD_ROOT/DEBIAN"
mkdir -p "$BUILD_ROOT/opt/$APP_NAME"
mkdir -p "$BUILD_ROOT/usr/bin"
mkdir -p "$BUILD_ROOT/usr/share/applications"
mkdir -p "$BUILD_ROOT/usr/share/icons/hicolor/scalable/apps"
mkdir -p "$BUILD_ROOT/etc/systemd/user"

# 3. Copy project files (Excluding venv, git, temporary caches)
echo "📂 Packaging latest project codebase..."
rsync -av --progress "$PROJECT_DIR/" "$BUILD_ROOT/opt/$APP_NAME/" \
    --exclude="deb_build" \
    --exclude="dist" \
    --exclude="venv" \
    --exclude="__pycache__" \
    --exclude="*.pyc" \
    --exclude="*.deb" \
    --exclude=".git" \
    --exclude=".gemini" \
    --exclude="uploads/*" \
    --exclude="server.log" \
    --exclude="demo_project" \
    --exclude="demo_workspace"

# 4. Create Desktop Entry in package
cat << 'EOF' > "$BUILD_ROOT/usr/share/applications/sakthidev-studio.desktop"
[Desktop Entry]
Version=1.0
Type=Application
Name=SakthiDev Studio
GenericName=Autonomous AI Software Engineer
Comment=SakthiDev Cyber OS - Autonomous Software Engineer Operating System
Exec=/usr/bin/sakthidev-studio
Icon=sakthidev-studio
Terminal=false
Categories=Development;Utility;
Keywords=ai;agent;sakthi;sakthidev;studio;code;engineer;chat;gemini;s;
StartupNotify=true
StartupWMClass=google-chrome
Actions=RestartService;StopService;ViewLogs;

[Desktop Action RestartService]
Name=Restart AI Agent Service
Exec=systemctl --user restart sakthidev-studio

[Desktop Action StopService]
Name=Stop AI Agent Service
Exec=systemctl --user stop sakthidev-studio

[Desktop Action ViewLogs]
Name=View Service Logs
Exec=gnome-terminal -- journalctl --user -u sakthidev-studio -f
EOF

# 5. Copy Scalable and Multi-Resolution PNG Icons
if [ -f "$PROJECT_DIR/static/icon.svg" ]; then
    cp "$PROJECT_DIR/static/icon.svg" "$BUILD_ROOT/usr/share/icons/hicolor/scalable/apps/sakthidev-studio.svg"
    for size in 32 48 64 128 256 512; do
        mkdir -p "$BUILD_ROOT/usr/share/icons/hicolor/${size}x${size}/apps"
        convert -background none "$PROJECT_DIR/static/icon.svg" -resize ${size}x${size} "$BUILD_ROOT/usr/share/icons/hicolor/${size}x${size}/apps/sakthidev-studio.png" 2>/dev/null || true
    done
    mkdir -p "$BUILD_ROOT/usr/share/pixmaps"
    convert -background none "$PROJECT_DIR/static/icon.svg" -resize 512x512 "$BUILD_ROOT/usr/share/pixmaps/sakthidev-studio.png" 2>/dev/null || true
fi

# 6. Create binary launcher in /usr/bin/sakthidev-studio
cat << 'EOF' > "$BUILD_ROOT/usr/bin/sakthidev-studio"
#!/usr/bin/env bash
APP_DIR="/opt/sakthidev-studio"
APP_URL="http://localhost:8000"

# Check if server is running; if not, attempt to start user systemd service
if ! curl -s --head --request GET "$APP_URL" | grep -E "200|307|404" > /dev/null 2>&1; then
    systemctl --user start sakthidev-studio 2>/dev/null || true
    sleep 1
fi

# Open in Native Chrome/Chromium App Window or default browser
if which google-chrome >/dev/null 2>&1; then
    google-chrome --app="$APP_URL" --user-data-dir="/tmp/sakthidev_chrome_profile" &
elif which chromium >/dev/null 2>&1; then
    chromium --app="$APP_URL" &
elif which brave-browser >/dev/null 2>&1; then
    brave-browser --app="$APP_URL" &
else
    xdg-open "$APP_URL" &
fi
EOF
chmod +x "$BUILD_ROOT/usr/bin/sakthidev-studio"

# 7. Create Systemd Service template inside package
cat << 'EOF' > "$BUILD_ROOT/etc/systemd/user/sakthidev-studio.service"
[Unit]
Description=SakthiDev Studio - Autonomous AI Software Engineer
After=network.target

[Service]
Type=simple
WorkingDirectory=/opt/sakthidev-studio
ExecStart=/opt/sakthidev-studio/venv/bin/python3 -m uvicorn server:app --host 0.0.0.0 --port 8000
Restart=always
RestartSec=3
Environment=PYTHONUNBUFFERED=1

[Install]
WantedBy=default.target
EOF

# 8. Create DEBIAN/control file
cat << EOF > "$BUILD_ROOT/DEBIAN/control"
Package: $APP_NAME
Version: $VERSION
Section: devel
Priority: optional
Architecture: all
Maintainer: Sakthi <sakthi@localhost>
Depends: python3, python3-pip, python3-venv, curl
Description: SakthiDev Studio - Autonomous AI Software Engineer
 Dynamic AI agent running continuous local background assistance, SSE streaming, SQLite memory.
EOF

# 9. Create DEBIAN/postinst (Post-installation hook: sets up venv & activates service)
cat << 'EOF' > "$BUILD_ROOT/DEBIAN/postinst"
#!/usr/bin/env bash
set -e
APP_DIR="/opt/sakthidev-studio"

echo "⚡ Configuring SakthiDev Studio environment..."
if [ ! -d "$APP_DIR/venv" ]; then
    python3 -m venv "$APP_DIR/venv"
fi

if [ -f "$APP_DIR/requirements.txt" ]; then
    "$APP_DIR/venv/bin/pip" install --quiet --upgrade pip
    "$APP_DIR/venv/bin/pip" install --quiet -r "$APP_DIR/requirements.txt"
fi

# Fix permissions
chmod -R a+rX "$APP_DIR"
chmod +x "$APP_DIR/open_app.sh" 2>/dev/null || true

# Update desktop & icon caches
update-desktop-database 2>/dev/null || true
gtk-update-icon-cache -f -t /usr/share/icons/hicolor 2>/dev/null || true

echo "✅ SakthiDev Studio installed successfully!"
echo "👉 Launch from Application Menu or run 'sakthidev-studio' in terminal."
exit 0
EOF
chmod 755 "$BUILD_ROOT/DEBIAN/postinst"

# 10. Create DEBIAN/prerm (Pre-removal hook: stop running instance cleanly)
cat << 'EOF' > "$BUILD_ROOT/DEBIAN/prerm"
#!/usr/bin/env bash
set -e
echo "🛑 Stopping SakthiDev Studio services before update..."
systemctl --user stop sakthidev-studio 2>/dev/null || true
exit 0
EOF
chmod 755 "$BUILD_ROOT/DEBIAN/prerm"

# 11. Build the .deb file with dpkg-deb
FINAL_DEB="$DIST_DIR/sakthidev-studio.deb"

echo "🔨 Assembling Debian package..."
dpkg-deb --build "$BUILD_ROOT" "$FINAL_DEB"

# Clean temporary staging directory
rm -rf "$BUILD_ROOT"

echo "=================================================================="
echo "🎉 SUCCESS! Debian package ready at:"
echo "   $FINAL_DEB"
echo ""
echo "🚀 To install / update:"
echo "   sudo dpkg -i dist/sakthidev-studio.deb"
echo "=================================================================="
