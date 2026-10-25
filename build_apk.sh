#!/usr/bin/env bash
# ==============================================================================
# SakthiDev Studio - Automated Android (.APK) Builder & Signer
# Generates a signed, standalone Android APK targeting your local AI Agent
# ==============================================================================

set -e

PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
DIST_DIR="$PROJECT_DIR/dist"
APK_WORK_DIR="$PROJECT_DIR/.apk_cache"
OUTPUT_APK="$DIST_DIR/sakthidev-studio.apk"
KEYSTORE="$APK_WORK_DIR/sakthidev.keystore"
ALIAS="sakthidev"
PASS="123456"

# Detect Local IP (or use passed argument)
LOCAL_IP="${1:-$(hostname -I | awk '{print $1}')}"
TARGET_URL="http://${LOCAL_IP}:8000"

echo "=================================================================="
echo "📱 Building & Signing Android APK for SakthiDev Studio"
echo "🌐 Configured Target URL: $TARGET_URL"
echo "=================================================================="

mkdir -p "$APK_WORK_DIR/assets"

# 1. Download Base Template if not cached
TEMPLATE_APK="$APK_WORK_DIR/base_template.apk"
if [ ! -f "$TEMPLATE_APK" ]; then
    echo "📥 Fetching mobile runtime engine..."
    curl -s -L -H "User-Agent: Mozilla/5.0" \
        "https://github.com/mgks/Android-SmartWebView/releases/download/v7.5/SmartWebView-v7.5.apk" \
        -o "$TEMPLATE_APK"
fi

cp "$TEMPLATE_APK" "$OUTPUT_APK"

# 2. Extract and customize configuration
unzip -p "$TEMPLATE_APK" assets/swv.properties > "$APK_WORK_DIR/assets/swv.properties"
sed -i "s|app\.url=.*|app.url=$TARGET_URL|g" "$APK_WORK_DIR/assets/swv.properties"

# 3. Update APK with modified properties
cd "$APK_WORK_DIR"
zip -q -u "$OUTPUT_APK" assets/swv.properties
# Remove old template signatures
zip -q -d "$OUTPUT_APK" "META-INF/*" || true

# 4. Generate Keystore if missing
if [ ! -f "$KEYSTORE" ]; then
    echo "🔑 Generating Android RSA 2048 signing certificate..."
    keytool -genkey -v -keystore "$KEYSTORE" -alias "$ALIAS" \
        -keyalg RSA -keysize 2048 -validity 10000 \
        -storepass "$PASS" -keypass "$PASS" \
        -dname "CN=Sakthi, OU=Dev, O=SakthiDev Studio, L=Chennai, ST=TN, C=IN"
fi

# 5. Sign the APK with Java jarsigner
echo "✍️ Signing APK with SHA-256 certificate..."
jarsigner -sigalg SHA256withRSA -digestalg SHA-256 \
    -keystore "$KEYSTORE" -storepass "$PASS" \
    "$OUTPUT_APK" "$ALIAS"

# 6. Verify signature
echo "🧪 Verifying Android APK signature..."
jarsigner -verify "$OUTPUT_APK" >/dev/null 2>&1
echo "✅ APK Signature Verified!"

cd "$PROJECT_DIR"

echo "=================================================================="
echo "🎉 SUCCESS! Signed Android APK ready at:"
echo "   $OUTPUT_APK"
echo "📲 Install on any Android phone (Settings > Install Unknown Apps > Allow)"
echo "=================================================================="
