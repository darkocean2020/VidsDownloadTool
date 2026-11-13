# VidsDownloadTool

基于 [yt-dlp](https://github.com/yt-dlp/yt-dlp) 的批量视频下载工具，带图形界面。

## 功能
- 输入框粘贴多个链接（每行一个，或用空格/逗号分隔），点击 **爬取** 依次下载
- 某个链接出错会自动跳过，结束后列出失败的链接
- 自带 ffmpeg，自动合并最佳画质视频+音频为 mp4；可勾选「仅下载音频」(mp3)
- 支持停止、更改保存目录、一键打开下载文件夹

## 下载保存位置
| 运行方式 | 默认目录 |
|---|---|
| 源码运行 | 项目内 `downloads/` |
| Windows exe | exe 同目录下的 `downloads/` |
| macOS app | `~/Downloads/VidsDownloadTool/` |

## 直接从源码运行
```bash
python3 -m venv .venv && .venv/bin/pip install -r requirements.txt
.venv/bin/python app.py
```
（macOS 需要带 Tkinter 的 Python，例如 `brew install python-tk@3.14`）

## 打包
- **macOS (.app + .dmg)**：`./build_mac.sh` → `dist/VidsDownloadTool.dmg`
- **Windows (.exe)**：在 Windows 上双击 `build_windows.bat` → `dist\VidsDownloadTool.exe`
- **GitHub Actions**：推送 `v*` 标签（如 `v1.0.0`）或手动触发 `Build` 工作流，自动产出 exe 和 dmg 并附到 Release。

## 注意
- 应用未签名：macOS 首次打开如提示「无法验证开发者/已损坏」，右键 → 打开，或执行 `xattr -cr /Applications/VidsDownloadTool.app`；Windows SmartScreen 提示时点「更多信息 → 仍要运行」。
- YouTube 需要 JS 运行环境才能获得全部格式：电脑装有 [Deno](https://deno.com) 时效果最好，没有也能下载但可选格式可能变少。
- 请仅下载你有权下载的内容。
