#!/usr/bin/env bash
# 构建 macOS 的 VidsDownloadTool.app 和 .dmg
# 需要带 Tkinter 的 Python（例如：brew install python-tk@3.14）
set -euo pipefail
cd "$(dirname "$0")"
PY="${PYTHON:-python3.14}"
[ -d .venv ] || "$PY" -m venv .venv
.venv/bin/pip install -q -U -r requirements.txt

rm -rf build dist
.venv/bin/pyinstaller --noconfirm --windowed --name VidsDownloadTool \
  --osx-bundle-identifier com.vidsdownloadtool.app \
  --collect-all imageio_ffmpeg --collect-all yt_dlp --collect-all yt_dlp_ejs \
  app.py

# 打包 dmg（包含 Applications 快捷方式，可拖拽安装）
STAGE=dist/dmg
mkdir -p "$STAGE"
cp -R dist/VidsDownloadTool.app "$STAGE/"
ln -s /Applications "$STAGE/Applications"
hdiutil create -volname VidsDownloadTool -srcfolder "$STAGE" -ov -format UDZO dist/VidsDownloadTool.dmg
rm -rf "$STAGE"
echo "完成：dist/VidsDownloadTool.app 和 dist/VidsDownloadTool.dmg"
