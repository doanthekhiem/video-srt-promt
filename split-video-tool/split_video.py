#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Cắt video thành N phần theo thời gian; các phần đầu làm tròn 5 phút."""

from __future__ import annotations

import argparse
import json
import os
import shutil
import subprocess
import sys
import webbrowser
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import parse_qs, urlparse

ROOT = Path(__file__).resolve().parent
VIDEOS_DIR = ROOT / "videos"
OUTPUT_DIR = ROOT / "videos-cut"
PORT = 8765
FIVE_MIN = 5 * 60


def sec_to_ffmpeg(t: float) -> str:
    h = int(t // 3600)
    m = int((t % 3600) // 60)
    s = t % 60
    return f"{h:02d}:{m:02d}:{s:06.3f}"


def sec_to_hms(t: float) -> str:
    t = int(round(t))
    h, rem = divmod(t, 3600)
    m, s = divmod(rem, 60)
    if h:
        return f"{h}:{m:02d}:{s:02d}"
    return f"{m}:{s:02d}"


def find_tool(name: str) -> str:
    p = shutil.which(name)
    if not p:
        raise RuntimeError(
            f"Không tìm thấy {name}. Cài ffmpeg (winget install Gyan.FFmpeg) và thêm vào PATH."
        )
    return p


def probe_duration(video: Path, ffprobe: str) -> float:
    cmd = [
        ffprobe,
        "-v",
        "error",
        "-show_entries",
        "format=duration",
        "-of",
        "default=noprint_wrappers=1:nokey=1",
        str(video),
    ]
    out = subprocess.run(cmd, capture_output=True, text=True, check=True)
    return float(out.stdout.strip())


def round_part_seconds(seconds: float) -> int:
    """Làm tròn thời lượng phần về bội 5 phút (5, 10, 15, ...)."""
    minutes = seconds / 60
    rounded_min = max(5, round(minutes / 5) * 5)
    return int(rounded_min * 60)


def compute_segments(total_sec: float, n: int) -> list[tuple[float, float]]:
    if n < 2:
        raise ValueError("Số phần phải >= 2")
    if total_sec <= 0:
        raise ValueError("Video không có thời lượng hợp lệ")

    segments: list[tuple[float, float]] = []
    start = 0.0
    remaining = total_sec
    parts_left = n

    for _ in range(n - 1):
        avg = remaining / parts_left
        part_len = round_part_seconds(avg)
        if part_len >= remaining:
            part_len = max(int(remaining * 0.5), FIVE_MIN)
        end = start + part_len
        if end >= total_sec:
            end = total_sec - 1
        segments.append((start, end))
        start = end
        remaining = total_sec - start
        parts_left -= 1

    segments.append((start, total_sec))
    return segments


def ensure_dirs() -> None:
    VIDEOS_DIR.mkdir(parents=True, exist_ok=True)
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)


def list_videos() -> list[str]:
    ensure_dirs()
    if not VIDEOS_DIR.is_dir():
        return []
    exts = {".mp4", ".mkv", ".webm", ".mov", ".avi", ".m4v"}
    files = [
        p.name
        for p in sorted(VIDEOS_DIR.iterdir())
        if p.is_file() and p.suffix.lower() in exts
    ]
    return files


def resolve_video(name: str) -> Path:
    name = name.strip()
    if not name:
        raise ValueError("Chưa chọn video")
    p = Path(name)
    if p.is_file():
        return p.resolve()
    candidate = VIDEOS_DIR / name
    if candidate.is_file():
        return candidate.resolve()
    raise FileNotFoundError(f"Không tìm thấy video: {name}")


def split_video_file(
    video: Path,
    n: int,
    overwrite: bool = False,
) -> dict:
    ffmpeg = find_tool("ffmpeg")
    ffprobe = find_tool("ffprobe")
    duration = probe_duration(video, ffprobe)
    segments = compute_segments(duration, n)

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    stem = video.stem
    ext = video.suffix

    plan = []
    created: list[Path] = []

    try:
        for i, (start, end) in enumerate(segments, start=1):
            out = OUTPUT_DIR / f"{stem}_p{i}{ext}"
            if out.exists() and not overwrite:
                raise FileExistsError(f"File đã tồn tại: {out.name}. Bật ghi đè hoặc xóa file cũ.")
            plan.append(
                {
                    "part": i,
                    "start_sec": start,
                    "end_sec": end,
                    "duration_sec": end - start,
                    "start": sec_to_hms(start),
                    "end": sec_to_hms(end),
                    "duration": sec_to_hms(end - start),
                    "output": str(out),
                }
            )

            ff_args = [
                ffmpeg,
                "-hide_banner",
                "-loglevel",
                "warning",
                "-stats",
                "-i",
                str(video),
                "-ss",
                sec_to_ffmpeg(start),
            ]
            if i < len(segments):
                ff_args.extend(["-to", sec_to_ffmpeg(end)])
            ff_args.extend(
                ["-c", "copy", "-map", "0", "-avoid_negative_ts", "make_zero", str(out)]
            )
            if overwrite:
                ff_args.insert(4, "-y")

            r = subprocess.run(ff_args, capture_output=True, text=True)
            if r.returncode != 0:
                err = (r.stderr or r.stdout or "").strip()[-2000:]
                raise RuntimeError(f"ffmpeg lỗi phần {i}: {err}")
            created.append(out)

        return {
            "ok": True,
            "input": str(video),
            "input_duration": sec_to_hms(duration),
            "input_duration_sec": duration,
            "parts": n,
            "output_dir": str(OUTPUT_DIR),
            "segments": plan,
        }
    except Exception:
        for p in created:
            try:
                p.unlink(missing_ok=True)
            except OSError:
                pass
        raise


class Handler(BaseHTTPRequestHandler):
    def log_message(self, fmt, *args):
        pass

    def _send_json(self, code: int, data: dict):
        body = json.dumps(data, ensure_ascii=False).encode("utf-8")
        self.send_response(code)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Access-Control-Allow-Origin", "*")
        self.end_headers()
        self.wfile.write(body)

    def _read_json(self) -> dict:
        length = int(self.headers.get("Content-Length", 0))
        raw = self.rfile.read(length) if length else b"{}"
        return json.loads(raw.decode("utf-8"))

    def do_OPTIONS(self):
        self.send_response(204)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.end_headers()

    def do_GET(self):
        path = urlparse(self.path).path
        if path in ("/", "/index.html"):
            html = (ROOT / "index.html").read_bytes()
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.send_header("Content-Length", str(len(html)))
            self.end_headers()
            self.wfile.write(html)
            return
        if path == "/api/videos":
            self._send_json(200, {"videos": list_videos(), "videos_dir": str(VIDEOS_DIR)})
            return
        self.send_error(404)

    def do_POST(self):
        path = urlparse(self.path).path
        if path != "/api/split":
            self.send_error(404)
            return
        try:
            data = self._read_json()
            video = resolve_video(data.get("video", ""))
            n = int(data.get("parts", 0))
            overwrite = bool(data.get("overwrite", False))
            if n < 2 or n > 50:
                raise ValueError("Số phần phải từ 2 đến 50")
            result = split_video_file(video, n, overwrite=overwrite)
            self._send_json(200, result)
        except FileExistsError as e:
            self._send_json(409, {"ok": False, "error": str(e)})
        except Exception as e:
            self._send_json(400, {"ok": False, "error": str(e)})


def serve(open_browser: bool = True):
    ensure_dirs()
    os.chdir(ROOT)
    url = f"http://127.0.0.1:{PORT}/"
    print(f"Split video tool: {url}")
    print(f"Video input:  {VIDEOS_DIR}")
    print(f"Video output: {OUTPUT_DIR}")
    if open_browser:
        webbrowser.open(url)
    server = ThreadingHTTPServer(("127.0.0.1", PORT), Handler)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nĐã dừng.")


def main_cli():
    ap = argparse.ArgumentParser(description="Cắt video thành N phần (thời gian, làm tròn 5 phút)")
    ap.add_argument("video", help="Tên file trong videos/ hoặc đường dẫn đầy đủ")
    ap.add_argument("-n", "--parts", type=int, required=True, help="Số phần")
    ap.add_argument("--overwrite", action="store_true")
    ap.add_argument("--serve", action="store_true", help="Chạy giao diện web")
    ap.add_argument("--no-browser", action="store_true")
    args = ap.parse_args()

    if args.serve:
        serve(open_browser=not args.no_browser)
        return

    video = resolve_video(args.video)
    result = split_video_file(video, args.parts, overwrite=args.overwrite)
    print(json.dumps(result, ensure_ascii=False, indent=2))


def _is_serve_mode() -> bool:
    flags = set(sys.argv[1:])
    if not flags:
        return True
    return flags.issubset({"--serve", "--no-browser"})


if __name__ == "__main__":
    if _is_serve_mode():
        serve(open_browser="--no-browser" not in sys.argv)
    else:
        main_cli()
