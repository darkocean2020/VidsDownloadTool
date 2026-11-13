"""VidsDownloadTool - 基于 yt-dlp 的批量视频下载工具（Tkinter 图形界面）。"""

import os
import platform
import queue
import re
import subprocess
import sys
import threading
import tkinter as tk
from pathlib import Path
from tkinter import filedialog, messagebox, ttk

import yt_dlp

APP_NAME = "VidsDownloadTool"


def default_download_dir() -> Path:
    """开发时用项目内 downloads/；打包后 Windows 用 exe 同级 downloads/，macOS 用 ~/Downloads/VidsDownloadTool。"""
    if getattr(sys, "frozen", False):
        if platform.system() == "Windows":
            candidate = Path(sys.executable).resolve().parent / "downloads"
            try:
                candidate.mkdir(parents=True, exist_ok=True)
                return candidate
            except OSError:
                pass
        return Path.home() / "Downloads" / APP_NAME
    return Path(__file__).resolve().parent / "downloads"


def find_ffmpeg() -> str | None:
    """优先使用打包进来的 ffmpeg（imageio-ffmpeg），用于合并音视频流。"""
    try:
        import imageio_ffmpeg

        path = imageio_ffmpeg.get_ffmpeg_exe()
        if path and os.path.exists(path):
            return path
    except Exception:
        pass
    return None


def parse_links(text: str) -> list[str]:
    links, seen = [], set()
    for token in re.split(r"[\s,，；;]+", text):
        token = token.strip()
        if token.startswith(("http://", "https://")) and token not in seen:
            seen.add(token)
            links.append(token)
    return links


class StopRequested(Exception):
    pass


class QueueLogger:
    def __init__(self, q: queue.Queue):
        self.q = q

    def debug(self, msg):
        if not msg.startswith("[debug]"):
            self.info(msg)

    def info(self, msg):
        if msg.startswith("[download]") and "%" in msg:
            return  # 进度由进度条显示，不刷屏
        self.q.put(("log", msg))

    def warning(self, msg):
        self.q.put(("log", f"⚠️ {msg}"))

    def error(self, msg):
        self.q.put(("log", f"❌ {msg}"))


class App:
    def __init__(self, root: tk.Tk):
        self.root = root
        self.q: queue.Queue = queue.Queue()
        self.worker: threading.Thread | None = None
        self.stop_flag = threading.Event()
        self.download_dir = default_download_dir()
        try:
            self.download_dir.mkdir(parents=True, exist_ok=True)
        except OSError:
            pass
        self.ffmpeg = find_ffmpeg()

        root.title("视频批量下载工具")
        root.geometry("760x620")
        root.minsize(560, 480)

        main = ttk.Frame(root, padding=12)
        main.pack(fill=tk.BOTH, expand=True)

        ttk.Label(main, text="视频链接（每行一个，也可用空格/逗号分隔）：").pack(anchor=tk.W)
        self.links_text = tk.Text(main, height=9, wrap=tk.NONE, undo=True)
        self.links_text.pack(fill=tk.BOTH, expand=False, pady=(4, 8))

        dir_row = ttk.Frame(main)
        dir_row.pack(fill=tk.X, pady=(0, 8))
        ttk.Label(dir_row, text="保存到：").pack(side=tk.LEFT)
        self.dir_var = tk.StringVar(value=str(self.download_dir))
        ttk.Entry(dir_row, textvariable=self.dir_var, state="readonly").pack(
            side=tk.LEFT, fill=tk.X, expand=True, padx=4
        )
        ttk.Button(dir_row, text="更改…", command=self.choose_dir).pack(side=tk.LEFT)
        ttk.Button(dir_row, text="打开文件夹", command=self.open_dir).pack(side=tk.LEFT, padx=(4, 0))

        btn_row = ttk.Frame(main)
        btn_row.pack(fill=tk.X, pady=(0, 8))
        self.start_btn = ttk.Button(btn_row, text="爬取", command=self.start)
        self.start_btn.pack(side=tk.LEFT)
        self.stop_btn = ttk.Button(btn_row, text="停止", command=self.stop, state=tk.DISABLED)
        self.stop_btn.pack(side=tk.LEFT, padx=6)
        ttk.Button(btn_row, text="清空日志", command=self.clear_log).pack(side=tk.LEFT)
        self.audio_only = tk.BooleanVar(value=False)
        ttk.Checkbutton(btn_row, text="仅下载音频", variable=self.audio_only).pack(side=tk.LEFT, padx=12)

        self.status_var = tk.StringVar(value="就绪")
        ttk.Label(main, textvariable=self.status_var).pack(anchor=tk.W)
        self.item_progress = ttk.Progressbar(main, maximum=100)
        self.item_progress.pack(fill=tk.X, pady=(4, 2))
        self.total_var = tk.StringVar(value="")
        ttk.Label(main, textvariable=self.total_var).pack(anchor=tk.W, pady=(0, 6))

        log_frame = ttk.Frame(main)
        log_frame.pack(fill=tk.BOTH, expand=True)
        self.log_text = tk.Text(log_frame, height=12, state=tk.DISABLED, wrap=tk.WORD)
        scroll = ttk.Scrollbar(log_frame, command=self.log_text.yview)
        self.log_text.configure(yscrollcommand=scroll.set)
        self.log_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scroll.pack(side=tk.RIGHT, fill=tk.Y)

        if not self.ffmpeg:
            self.log("⚠️ 未找到 ffmpeg，将只下载单文件格式（画质可能较低）。")

        root.protocol("WM_DELETE_WINDOW", self.on_close)
        self.root.after(100, self.poll_queue)

    # ---------- UI helpers ----------
    def log(self, msg: str):
        self.log_text.configure(state=tk.NORMAL)
        self.log_text.insert(tk.END, msg + "\n")
        self.log_text.see(tk.END)
        self.log_text.configure(state=tk.DISABLED)

    def clear_log(self):
        self.log_text.configure(state=tk.NORMAL)
        self.log_text.delete("1.0", tk.END)
        self.log_text.configure(state=tk.DISABLED)

    def choose_dir(self):
        d = filedialog.askdirectory(initialdir=str(self.download_dir))
        if d:
            self.download_dir = Path(d)
            self.dir_var.set(d)

    def open_dir(self):
        self.download_dir.mkdir(parents=True, exist_ok=True)
        path = str(self.download_dir)
        if platform.system() == "Windows":
            os.startfile(path)  # noqa: S606
        elif platform.system() == "Darwin":
            subprocess.Popen(["open", path])
        else:
            subprocess.Popen(["xdg-open", path])

    def set_running(self, running: bool):
        self.start_btn.configure(state=tk.DISABLED if running else tk.NORMAL)
        self.stop_btn.configure(state=tk.NORMAL if running else tk.DISABLED)
        self.links_text.configure(state=tk.DISABLED if running else tk.NORMAL)

    # ---------- actions ----------
    def start(self):
        links = parse_links(self.links_text.get("1.0", tk.END))
        if not links:
            messagebox.showinfo("提示", "请先输入至少一个以 http:// 或 https:// 开头的链接。")
            return
        try:
            self.download_dir.mkdir(parents=True, exist_ok=True)
        except OSError as e:
            messagebox.showerror("错误", f"无法创建下载文件夹：\n{e}")
            return
        self.stop_flag.clear()
        self.set_running(True)
        self.item_progress["value"] = 0
        self.worker = threading.Thread(
            target=self.run_downloads, args=(links, self.download_dir, self.audio_only.get()), daemon=True
        )
        self.worker.start()

    def stop(self):
        self.stop_flag.set()
        self.status_var.set("正在停止…")

    def on_close(self):
        if self.worker and self.worker.is_alive():
            if not messagebox.askyesno("退出", "下载仍在进行，确定要退出吗？"):
                return
            self.stop_flag.set()
        self.root.destroy()

    # ---------- worker ----------
    def build_opts(self, out_dir: Path, audio_only: bool) -> dict:
        def hook(d):
            if self.stop_flag.is_set():
                raise StopRequested()
            if d["status"] == "downloading":
                total = d.get("total_bytes") or d.get("total_bytes_estimate")
                pct = d["downloaded_bytes"] / total * 100 if total else 0
                speed = d.get("_speed_str", "").strip()
                eta = d.get("_eta_str", "").strip()
                self.q.put(("progress", pct, f"下载中 {pct:5.1f}%  {speed}  剩余 {eta}"))
            elif d["status"] == "finished":
                self.q.put(("progress", 100, "下载完成，处理中…"))

        opts = {
            "outtmpl": str(out_dir / "%(title).150B [%(id)s].%(ext)s"),
            "logger": QueueLogger(self.q),
            "progress_hooks": [hook],
            "ignoreerrors": "only_download",  # 播放列表中个别失败时跳过
            "noprogress": True,
            "windowsfilenames": True,
            "retries": 3,
            "fragment_retries": 3,
            "concurrent_fragment_downloads": 4,
        }
        if self.ffmpeg:
            opts["ffmpeg_location"] = self.ffmpeg
            if audio_only:
                opts["format"] = "ba/b"
                opts["postprocessors"] = [
                    {"key": "FFmpegExtractAudio", "preferredcodec": "mp3", "preferredquality": "192"}
                ]
            else:
                opts["format"] = "bv*+ba/b"
                opts["merge_output_format"] = "mp4"
        else:
            opts["format"] = "ba/b" if audio_only else "b"
        return opts

    def run_downloads(self, links: list[str], out_dir: Path, audio_only: bool):
        ok, failed = 0, []
        total = len(links)
        opts = self.build_opts(out_dir, audio_only)
        for i, url in enumerate(links, 1):
            if self.stop_flag.is_set():
                break
            self.q.put(("total", f"总进度：{i}/{total}    成功 {ok}  失败 {len(failed)}"))
            self.q.put(("progress", 0, f"正在解析：{url}"))
            self.q.put(("log", f"\n▶ [{i}/{total}] {url}"))
            try:
                with yt_dlp.YoutubeDL(opts) as ydl:
                    code = ydl.download([url])
                if code:
                    raise RuntimeError("yt-dlp 返回错误")
                ok += 1
                self.q.put(("log", "✅ 完成"))
            except StopRequested:
                self.q.put(("log", "⏹ 已停止"))
                break
            except Exception as e:  # 出错则跳过
                failed.append(url)
                self.q.put(("log", f"⏭ 跳过（出错）：{e}"))
        self.q.put(("done", ok, failed, total))

    def poll_queue(self):
        try:
            while True:
                item = self.q.get_nowait()
                kind = item[0]
                if kind == "log":
                    self.log(item[1])
                elif kind == "progress":
                    self.item_progress["value"] = item[1]
                    self.status_var.set(item[2])
                elif kind == "total":
                    self.total_var.set(item[1])
                elif kind == "done":
                    _, ok, failed, total = item
                    self.set_running(False)
                    stopped = self.stop_flag.is_set()
                    self.status_var.set("已停止" if stopped else "全部完成")
                    self.total_var.set(f"共 {total} 个：成功 {ok}，失败 {len(failed)}")
                    if failed:
                        self.log("\n以下链接下载失败，已跳过：")
                        for u in failed:
                            self.log(f"  {u}")
                    self.log(f"\n文件保存在：{self.download_dir}")
        except queue.Empty:
            pass
        self.root.after(100, self.poll_queue)


def main():
    root = tk.Tk()
    try:
        ttk.Style().theme_use("aqua" if platform.system() == "Darwin" else "vista")
    except tk.TclError:
        pass
    App(root)
    root.mainloop()


if __name__ == "__main__":
    main()
