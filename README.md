# VidsDownloadTool

基于 [yt-dlp](https://github.com/yt-dlp/yt-dlp) 的批量视频下载工具，带图形界面，下载即用，无需安装 Python 或 ffmpeg。

A simple GUI batch video downloader powered by yt-dlp. Download, open, paste links, done. ([English guide below](#english))

## 下载

| 系统 | 下载 |
|---|---|
| **Windows** 10/11 (64 位) | [VidsDownloadTool.exe](https://github.com/darkocean2020/VidsDownloadTool/releases/latest/download/VidsDownloadTool.exe) |
| **macOS** (Apple Silicon：M1/M2/M3/M4…) | [VidsDownloadTool.dmg](https://github.com/darkocean2020/VidsDownloadTool/releases/latest/download/VidsDownloadTool.dmg) |

所有版本见 [Releases 页面](https://github.com/darkocean2020/VidsDownloadTool/releases)。

> 本软件未经过 Apple / Microsoft 付费签名，首次打开时系统会拦截，按下面步骤放行一次即可。

### Windows 使用方法
1. 下载 `VidsDownloadTool.exe`，建议放到一个单独的文件夹（例如桌面上新建的 `视频下载`）。
2. 双击运行。若出现蓝色的「Windows 已保护你的电脑」：点 **更多信息** → **仍要运行**。
3. 首次启动需要几秒钟解压，请耐心等待窗口出现。
4. 下载的视频保存在 **exe 同目录下的 `downloads` 文件夹**。

### macOS 使用方法
1. 下载 `VidsDownloadTool.dmg` 并双击打开，把 **VidsDownloadTool** 拖到 **Applications（应用程序）** 文件夹。
2. 打开「终端」(Terminal)，粘贴并回车执行下面这行（去掉系统对未签名应用的拦截标记）：
   ```bash
   xattr -cr /Applications/VidsDownloadTool.app
   ```
3. 在「应用程序」里双击打开 VidsDownloadTool。
   - 如果仍提示「无法打开」：打开 **系统设置 → 隐私与安全性**，在页面下方点 **仍要打开**。
4. 下载的视频保存在 **`~/Downloads/VidsDownloadTool`**（「下载」文件夹里的 VidsDownloadTool）。

> 目前只提供 Apple Silicon 版本。Intel Mac 用户请参考下方「从源码运行」。

### 使用说明
1. 在输入框粘贴视频链接，**每行一个**（也可以用空格或逗号分隔）。
2. 点击 **爬取**，程序会依次下载；某个链接出错会自动跳过，最后列出失败的链接。
3. 其他功能：
   - **仅下载音频**：勾选后保存为 mp3
   - **停止**：中断当前任务
   - **更改…**：选择其他保存目录
   - **打开文件夹**：直接打开下载目录

支持的网站与 yt-dlp 相同（YouTube、Bilibili、Twitter/X、Vimeo 等上千个站点），完整列表见 [supported sites](https://github.com/yt-dlp/yt-dlp/blob/master/supportedsites.md)。

### 常见问题
- **YouTube 下载失败或画质较低**：YouTube 需要 JS 运行环境，安装 [Deno](https://deno.com) 后效果最好。另外网站改版时 yt-dlp 需要更新，请下载本工具的最新版本。
- **某个视频一直失败**：可能是会员/地区限制/私密视频，本工具不支持登录账号下载。

---

## English

### Download
- **Windows** 10/11 (64-bit): [VidsDownloadTool.exe](https://github.com/darkocean2020/VidsDownloadTool/releases/latest/download/VidsDownloadTool.exe)
- **macOS** (Apple Silicon): [VidsDownloadTool.dmg](https://github.com/darkocean2020/VidsDownloadTool/releases/latest/download/VidsDownloadTool.dmg)

The app is not code-signed, so the OS will warn you the first time.

**Windows:** put the exe in its own folder and double-click it. If SmartScreen shows "Windows protected your PC", click **More info → Run anyway**. Videos are saved to the `downloads` folder next to the exe.

**macOS:** open the dmg and drag the app into Applications, then run this once in Terminal:
```bash
xattr -cr /Applications/VidsDownloadTool.app
```
Then open it from Applications. If macOS still blocks it, go to **System Settings → Privacy & Security** and click **Open Anyway**. Videos are saved to `~/Downloads/VidsDownloadTool`.

**Usage:** paste links (one per line), click **爬取** (Download). Failed links are skipped and listed at the end. Options: audio-only (mp3), stop, change folder, open folder.

---

## 开发者 / For developers

### 从源码运行
```bash
python3 -m venv .venv && .venv/bin/pip install -r requirements.txt
.venv/bin/python app.py
```
需要带 Tkinter 的 Python（macOS：`brew install python-tk@3.14`）。源码运行时视频保存在项目内 `downloads/`。

### 打包
- macOS：`./build_mac.sh` → `dist/VidsDownloadTool.dmg`
- Windows：运行 `build_windows.bat` → `dist\VidsDownloadTool.exe`
- 自动发布：推送 `v*` 标签（如 `git tag v1.0.1 && git push origin v1.0.1`），GitHub Actions 会构建 exe 和 dmg 并发布到 Releases。

## 免责声明 / Disclaimer
请仅下载你有权下载的内容，并遵守相关网站的服务条款与当地法律。Only download content you have the right to download.

## License
[MIT](LICENSE)
