@echo off
REM 构建 Windows 的 VidsDownloadTool.exe（单文件）
cd /d "%~dp0"
if not exist .venv python -m venv .venv
.venv\Scripts\pip install -q -U -r requirements.txt
.venv\Scripts\pyinstaller --noconfirm --onefile --windowed --name VidsDownloadTool ^
  --collect-all imageio_ffmpeg --collect-all yt_dlp --collect-all yt_dlp_ejs ^
  app.py
echo 完成：dist\VidsDownloadTool.exe
pause
