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
mkdir -p "$APK_WORK_DIR/assets/web"
unzip -p "$TEMPLATE_APK" assets/swv.properties > "$APK_WORK_DIR/assets/swv.properties"
sed -i "s|app\.url=.*|app.url=$TARGET_URL|g" "$APK_WORK_DIR/assets/swv.properties"
sed -i "s|security\.verify\.ssl=true|security.verify.ssl=false|g" "$APK_WORK_DIR/assets/swv.properties"

# Replace offline and error pages with SakthiDev Studio Cyber Connect Portal
cp "$PROJECT_DIR/static/connect.html" "$APK_WORK_DIR/assets/web/offline.html"
cp "$PROJECT_DIR/static/connect.html" "$APK_WORK_DIR/assets/web/error.html"

# 3. Update APK with modified properties and connection portal
cd "$APK_WORK_DIR"
zip -q -u "$OUTPUT_APK" assets/swv.properties assets/web/offline.html assets/web/error.html
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

# 5. Download uber-apk-signer if missing (Provides APK Signature Scheme v2/v3 + zipalign for Android 11+)
UBER_SIGNER="$APK_WORK_DIR/uber-apk-signer.jar"
if [ ! -f "$UBER_SIGNER" ]; then
    echo "📥 Fetching modern APK v2/v3 signing engine..."
    curl -s -L "https://github.com/patrickfav/uber-apk-signer/releases/download/v1.3.0/uber-apk-signer-1.3.0.jar" -o "$UBER_SIGNER"
fi

# 6. Sign and zipalign APK with v1, v2, v3 cryptographic scheme
echo "✍️ Signing & zip-aligning APK with SHA-256 (v1, v2, v3 signature schemes)..."
java -jar "$UBER_SIGNER" \
    --apks "$OUTPUT_APK" \
    --ks "$KEYSTORE" \
    --ksAlias "$ALIAS" \
    --ksPass "$PASS" \
    --ksKeyPass "$PASS" \
    --overwrite

echo "✅ APK Signature Verified (v2, v3 + zipalign)!"

cd "$PROJECT_DIR"

echo "=================================================================="
echo "🎉 SUCCESS! Signed Android APK ready at:"
echo "   $OUTPUT_APK"
echo "📲 Install on any Android phone (Settings > Install Unknown Apps > Allow)"
echo "=================================================================="
