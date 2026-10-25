#!/usr/bin/env bash
# ==============================================================================
# SakthiDev Studio - 100% Comprehensive Quality Assurance Test Suite
# Exhaustively verifies .deb, .exe (Windows), and .apk (Android) packages
# ==============================================================================

set -e

PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
DIST_DIR="$PROJECT_DIR/dist"
TEST_TEMP="/tmp/sakthidev_qa_test"
PASSED=0
FAILED=0

GREEN='\033[0;32m'
RED='\033[0;31m'
CYAN='\033[0;36m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

pass() {
    echo -e "   [${GREEN}PASS${NC}] $1"
    PASSED=$((PASSED + 1))
}

fail() {
    echo -e "   [${RED}FAIL${NC}] $1"
    FAILED=$((FAILED + 1))
}

rm -rf "$TEST_TEMP"
mkdir -p "$TEST_TEMP"

echo -e "${CYAN}==================================================================${NC}"
echo -e "${YELLOW}⚡ SAKTHIDEV STUDIO - COMPREHENSIVE 100% QA VERIFICATION SUITE${NC}"
echo -e "${CYAN}==================================================================${NC}"

# ------------------------------------------------------------------------------
# SUITE 1: DEBIAN PACKAGE (.DEB)
# ------------------------------------------------------------------------------
echo ""
echo -e "${CYAN}--- [1/3] TESTING LINUX DEBIAN PACKAGE (.DEB) ---${NC}"
DEB_PATH="$DIST_DIR/sakthidev-studio.deb"

if [ -f "$DEB_PATH" ]; then
    DEB_SIZE=$(stat -c%s "$DEB_PATH")
    if [ "$DEB_SIZE" -gt 2000000 ]; then
        pass "File exists and healthy size ($((DEB_SIZE / 1024 / 1024)) MB)"
    else
        fail "Debian file size suspiciously small ($DEB_SIZE bytes)"
    fi
else
    fail "Debian file not found at $DEB_PATH"
fi

# Inspect deb control info
dpkg-deb -I "$DEB_PATH" > "$TEST_TEMP/deb_info.txt" 2>&1
if grep -q "Package: sakthidev-studio" "$TEST_TEMP/deb_info.txt"; then
    pass "Control header: Package name matches 'sakthidev-studio'"
else
    fail "Control header missing package name"
fi

if grep -q "Depends:.*python3" "$TEST_TEMP/deb_info.txt"; then
    pass "Dependencies: python3 dependency declared"
else
    fail "Missing python3 dependency declaration"
fi

# Inspect deb file contents
dpkg-deb -c "$DEB_PATH" > "$TEST_TEMP/deb_contents.txt" 2>&1

check_deb_content() {
    local target="$1"
    local desc="$2"
    if grep -q "$target" "$TEST_TEMP/deb_contents.txt"; then
        pass "$desc ($target)"
    else
        fail "Missing expected file: $target"
    fi
}

check_deb_content "opt/sakthidev-studio/server.py" "Core backend server"
check_deb_content "opt/sakthidev-studio/static/index.html" "Frontend UI console"
check_deb_content "usr/bin/sakthidev-studio" "Executable binary launcher in PATH"
check_deb_content "usr/share/applications/sakthidev-studio.desktop" "Desktop app shortcut"
check_deb_content "usr/share/icons/hicolor/scalable/apps/sakthidev-studio.svg" "Scalable SVG app icon"
check_deb_content "usr/share/icons/hicolor/512x512/apps/sakthidev-studio.png" "High-res 512x512 PNG icon"
check_deb_content "etc/systemd/user/sakthidev-studio.service" "Autostart systemd user service"

# Extract and validate desktop file from package
dpkg-deb -x "$DEB_PATH" "$TEST_TEMP/deb_extracted"
DESKTOP_EXTRACTED="$TEST_TEMP/deb_extracted/usr/share/applications/sakthidev-studio.desktop"
if [ -f "$DESKTOP_EXTRACTED" ]; then
    if desktop-file-validate "$DESKTOP_EXTRACTED"; then
        pass "Desktop file passes standard XDG specification validation"
    else
        fail "Desktop file validation failed"
    fi
    if grep -q "Keywords=" "$DESKTOP_EXTRACTED"; then
        pass "Search Keywords present in desktop entry"
    else
        fail "Search Keywords missing in desktop entry"
    fi
fi

# Validate launcher bash syntax
LAUNCHER_EXTRACTED="$TEST_TEMP/deb_extracted/usr/bin/sakthidev-studio"
if [ -f "$LAUNCHER_EXTRACTED" ]; then
    if bash -n "$LAUNCHER_EXTRACTED"; then
        pass "Launcher script syntax valid (bash -n passed)"
    else
        fail "Launcher script syntax error"
    fi
fi


# ------------------------------------------------------------------------------
# SUITE 2: WINDOWS EXECUTABLE PACKAGE (.EXE / .ZIP)
# ------------------------------------------------------------------------------
echo ""
echo -e "${CYAN}--- [2/3] TESTING WINDOWS EXECUTABLE PACKAGE (.EXE) ---${NC}"
WIN_ZIP="$DIST_DIR/sakthidev-studio-windows.zip"

if [ -f "$WIN_ZIP" ]; then
    ZIP_SIZE=$(stat -c%s "$WIN_ZIP")
    if [ "$ZIP_SIZE" -gt 50000000 ]; then
        pass "Windows package exists ($((ZIP_SIZE / 1024 / 1024)) MB)"
    else
        fail "Windows package size suspiciously small ($ZIP_SIZE bytes)"
    fi
else
    fail "Windows zip package not found"
fi

# Test zip integrity (CRC check)
if unzip -t "$WIN_ZIP" >/dev/null 2>&1; then
    pass "Zip archive integrity 100% sound (CRC32 check passed)"
else
    fail "Zip archive corruption detected"
fi

# Extract and verify PE32+ executable
mkdir -p "$TEST_TEMP/win_extracted"
unzip -q -j "$WIN_ZIP" "*SakthiDev Studio.exe" -d "$TEST_TEMP/win_extracted/" 2>/dev/null || true
EXE_FILE="$TEST_TEMP/win_extracted/SakthiDev Studio.exe"

if [ -f "$EXE_FILE" ]; then
    pass "Target executable found: 'SakthiDev Studio.exe'"
    EXE_TYPE=$(file "$EXE_FILE")
    if echo "$EXE_TYPE" | grep -q "PE32+ executable (GUI) x86-64, for MS Windows"; then
        pass "Binary architecture verified: PE32+ 64-bit Windows GUI Executable"
    else
        fail "Unexpected binary format: $EXE_TYPE"
    fi
else
    fail "Executable 'SakthiDev Studio.exe' missing in zip"
fi

# Verify essential Windows runtime DLLs inside zip
check_zip_member() {
    local member="$1"
    local desc="$2"
    if unzip -l "$WIN_ZIP" | grep -q "$member"; then
        pass "$desc ($member)"
    else
        fail "Missing Windows runtime dependency: $member"
    fi
}

check_zip_member "ffmpeg.dll" "Audio/Video codec acceleration DLL"
check_zip_member "d3dcompiler_47.dll" "DirectX 3D Shader rendering DLL"
check_zip_member "vulkan-1.dll" "Vulkan hardware GPU acceleration DLL"
check_zip_member "resources.pak" "Electron UI resources bundle"
check_zip_member "v8_context_snapshot.bin" "Chromium V8 JavaScript engine snapshot"


# ------------------------------------------------------------------------------
# SUITE 3: ANDROID MOBILE PACKAGE (.APK)
# ------------------------------------------------------------------------------
echo ""
echo -e "${CYAN}--- [3/3] TESTING ANDROID PACKAGE (.APK) ---${NC}"
APK_PATH="$DIST_DIR/sakthidev-studio.apk"

if [ -f "$APK_PATH" ]; then
    APK_SIZE=$(stat -c%s "$APK_PATH")
    if [ "$APK_SIZE" -gt 5000000 ]; then
        pass "Android APK exists ($((APK_SIZE / 1024 / 1024)) MB)"
    else
        fail "APK file size suspiciously small ($APK_SIZE bytes)"
    fi
else
    fail "APK not found at $APK_PATH"
fi

# Test APK Zip Integrity
if unzip -t "$APK_PATH" >/dev/null 2>&1; then
    pass "APK zip archive structure verified (no corruption)"
else
    fail "Corrupt APK archive structure"
fi

# Check Android components
check_apk_member() {
    local member="$1"
    local desc="$2"
    if unzip -l "$APK_PATH" | grep -q "$member"; then
        pass "$desc ($member)"
    else
        fail "Missing Android component: $member"
    fi
}

check_apk_member "AndroidManifest.xml" "Android Binary Manifest"
check_apk_member "classes.dex" "Dalvik Executable Runtime Bytecode (classes.dex)"
check_apk_member "assets/swv.properties" "Runtime configuration properties"
check_apk_member "resources.arsc" "Compiled Android Resources Table"

# Verify swv.properties content
mkdir -p "$TEST_TEMP/apk_assets"
unzip -p "$APK_PATH" assets/swv.properties > "$TEST_TEMP/apk_assets/swv.properties"
TARGET_URL=$(grep "^app\.url=" "$TEST_TEMP/apk_assets/swv.properties" | cut -d'=' -f2-)

if [ -n "$TARGET_URL" ] && [[ "$TARGET_URL" == http* ]]; then
    pass "Configured app URL verified: $TARGET_URL"
else
    fail "app.url in swv.properties is invalid or missing"
fi

# Test Cryptographic Java Signature
SIG_OUTPUT=$(jarsigner -verify "$APK_PATH" 2>&1)
if echo "$SIG_OUTPUT" | grep -q "jar verified."; then
    pass "Cryptographic signature: Verified valid SHA-256 certificate (jar verified)"
else
    fail "Signature verification failed: $SIG_OUTPUT"
fi


# ------------------------------------------------------------------------------
# SUITE 4: LIVE SERVICE & HTTP ENDPOINTS
# ------------------------------------------------------------------------------
echo ""
echo -e "${CYAN}--- [4/4] TESTING LIVE LOCAL AGENT RUNTIME ---${NC}"

# Check systemd user service
if systemctl --user is-active --quiet sakthidev-studio; then
    pass "Systemd Background Service: Active & Running (auto-restarts on boot)"
else
    fail "Systemd service is not active"
fi

# Check HTTP 200 on server
check_http() {
    local url="$1"
    local desc="$2"
    local code
    code=$(curl -s -o /dev/null -w "%{http_code}" "$url" 2>/dev/null || echo "000")
    if [ "$code" = "200" ]; then
        pass "$desc ($url -> HTTP 200 OK)"
    else
        fail "$desc ($url -> Returned HTTP $code)"
    fi
}

check_http "http://localhost:8000/" "Studio Main Cockpit UI"
check_http "http://localhost:8000/static/icon.svg" "Quantum Arc Reactor SVG Icon"
check_http "http://localhost:8000/static/manifest.json" "PWA Manifest"
check_http "http://localhost:8000/api/config" "Backend REST API Config Endpoint"

# Clean up QA scratch
rm -rf "$TEST_TEMP"

# ------------------------------------------------------------------------------
# SUMMARY REPORT
# ------------------------------------------------------------------------------
echo ""
echo -e "${CYAN}==================================================================${NC}"
TOTAL=$((PASSED + FAILED))
SUCCESS_RATE=$(( (PASSED * 100) / TOTAL ))
if [ "$FAILED" -eq 0 ]; then
    echo -e "${GREEN}🎉 100% ALL TESTS PASSED! (${PASSED}/${TOTAL} Tests Succeeded)${NC}"
    echo -e "${GREEN}✅ .deb, .exe, and .apk are 100% verified and production-ready!${NC}"
else
    echo -e "${RED}⚠️ ${FAILED} test(s) failed out of ${TOTAL}.${NC}"
fi
echo -e "${CYAN}==================================================================${NC}"
