#!/usr/bin/env python3
import zipfile, os, shutil, sys

def patch_windows_package(target_ip="192.168.0.115"):
    project_dir = os.path.abspath(os.path.dirname(__file__))
    zip_path = os.path.join(project_dir, 'dist', 'sakthidev-studio-windows.zip')
    extract_dir = '/tmp/sakthi_win_build'

    if not os.path.exists(zip_path):
        print(f"Error: {zip_path} not found.")
        sys.exit(1)

    if os.path.exists(extract_dir):
        shutil.rmtree(extract_dir)
    os.makedirs(extract_dir, exist_ok=True)

    print(f"📦 Extracting {zip_path}...")
    with zipfile.ZipFile(zip_path, 'r') as z:
        z.extractall(extract_dir)

    app_dir = os.path.join(extract_dir, 'SakthiDev Studio-win32-x64')
    nativefier_json_path = os.path.join(app_dir, 'resources', 'app', 'nativefier.json')
    main_js_path = os.path.join(app_dir, 'resources', 'app', 'lib', 'main.js')
    static_dir = os.path.join(app_dir, 'resources', 'app', 'lib', 'static')
    os.makedirs(static_dir, exist_ok=True)

    target_url = f"http://{target_ip}:8000/"

    # 1. Update nativefier.json
    if os.path.exists(nativefier_json_path):
        with open(nativefier_json_path, 'r', encoding='utf-8') as f:
            nf = f.read()
        import re
        nf = re.sub(r'"targetUrl":\s*"[^"]+"', f'"targetUrl":"{target_url}"', nf)
        with open(nativefier_json_path, 'w', encoding='utf-8') as f:
            f.write(nf)
        print(f"✅ Updated nativefier.json targetUrl to {target_url}")

    # 2. Copy connect.html
    src_connect = os.path.join(project_dir, 'static', 'connect.html')
    dest_connect = os.path.join(static_dir, 'connect.html')
    if os.path.exists(src_connect):
        shutil.copy(src_connect, dest_connect)
        print("✅ Copied connect.html to resources/app/lib/static/connect.html")

    # 3. Patch main.js for graceful connection fallback (No more blank white screen!)
    if os.path.exists(main_js_path):
        with open(main_js_path, 'r', encoding='utf-8') as f:
            mjs = f.read()

        # Robust replace for loadURL fallback
        import re
        # Replace previous patched or original loadURL block
        load_pattern = r'if \(appArgs\.targetUrl\) \{[\s\S]*?(?:await mainWindow\.loadURL\([^\)]*\);[\s\S]*?\}|await mainWindow\.loadURL\(appArgs\.targetUrl\);\s*\})'
        robust_load = """if (appArgs.targetUrl) {
        try {
            await mainWindow.loadURL(appArgs.targetUrl);
        } catch (e) {
            log.error('Failed to load targetUrl', e);
            await mainWindow.loadFile(path.join(__dirname, 'static', 'connect.html'));
        }
    }"""
        mjs = re.sub(r'if \(appArgs\.targetUrl\) \{\s*(?:try \{[\s\S]*?\}\s*catch[^{]*\{[\s\S]*?\}\s*\}|await mainWindow\.loadURL\(appArgs\.targetUrl\);\s*\})', robust_load, mjs)

        # Robust replace for did-fail-load hook
        robust_hook = """(0, windowEvents_1.setupNativefierWindow)(windowOptions, mainWindow);
    mainWindow.webContents.on('did-fail-load', (event, errorCode, errorDesc, validatedUrl) => {
        log.warn('did-fail-load triggered:', errorCode, errorDesc, validatedUrl);
        if (errorCode !== -3 && !(validatedUrl && validatedUrl.includes('connect.html'))) {
            mainWindow.loadFile(path.join(__dirname, 'static', 'connect.html')).catch((err) => log.error('Fallback error', err));
        }
    });"""

        hook_target = "(0, windowEvents_1.setupNativefierWindow)(windowOptions, mainWindow);"
        if "did-fail-load triggered:" in mjs:
            # Replace existing did-fail-load hook
            mjs = re.sub(r'\(0, windowEvents_1\.setupNativefierWindow\)\(windowOptions, mainWindow\);[\s\S]*?mainWindow\.webContents\.on\(\'did-fail-load\'[\s\S]*?\}\);', robust_hook, mjs)
            print("✅ Re-patched main.js did-fail-load listener with safe loadFile")
        elif hook_target in mjs:
            mjs = mjs.replace(hook_target, robust_hook)
            print("✅ Added did-fail-load listener in main.js with safe loadFile")

        with open(main_js_path, 'w', encoding='utf-8') as f:
            f.write(mjs)

    # 4. Add Start-Local-Server.bat for Windows users wanting to run locally
    bat_content = """@echo off
title SakthiDev Studio - Local Server
color 0b
echo ==========================================================
echo ⚡ SakthiDev Studio - Windows Local Backend Runner
echo ==========================================================
echo.
where python >nul 2>nul
if %errorlevel% neq 0 (
    echo [ERROR] Python was not found in your Windows PATH.
    echo Please install Python 3.10+ from python.org and tick "Add to PATH".
    pause
    exit /b 1
)
cd /d "%~dp0backend"
echo [1/2] Checking requirements...
python -m pip install -r requirements.txt
echo.
echo [2/2] Launching backend on http://localhost:8000...
echo 🌐 You can now launch "SakthiDev Studio.exe"!
echo ==========================================================
python -m uvicorn server:app --host 0.0.0.0 --port 8000 --reload
pause
"""
    with open(os.path.join(app_dir, 'Start-Local-Server.bat'), 'w', encoding='utf-8') as f:
        f.write(bat_content)
    print("✅ Created Start-Local-Server.bat")

    # 5. Add backend files so the zip is completely self-contained for Windows
    backend_dir = os.path.join(app_dir, 'backend')
    os.makedirs(backend_dir, exist_ok=True)
    for item in ['server.py', 'requirements.txt', 'config.example.json', 'config.json']:
        src = os.path.join(project_dir, item)
        if os.path.exists(src):
            shutil.copy(src, os.path.join(backend_dir, item))
    for d in ['core', 'static']:
        src_d = os.path.join(project_dir, d)
        dest_d = os.path.join(backend_dir, d)
        if os.path.exists(dest_d):
            shutil.rmtree(dest_d)
        shutil.copytree(src_d, dest_d)
    print("✅ Bundled complete backend runtime into backend/ folder")

    # 6. Re-zip the package
    print("🗜️ Re-compressing into dist/sakthidev-studio-windows.zip...")
    os.remove(zip_path)
    shutil.make_archive(os.path.join(project_dir, 'dist', 'sakthidev-studio-windows'), 'zip', extract_dir)
    shutil.rmtree(extract_dir)
    print(f"🎉 SUCCESS! Final Windows package size: {os.path.getsize(zip_path) / (1024*1024):.1f} MB")

if __name__ == '__main__':
    ip = sys.argv[1] if len(sys.argv) > 1 else "192.168.0.115"
    patch_windows_package(ip)
