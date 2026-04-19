# -*- coding: utf-8 -*-
"""
merge_srt_phrases.py
---------------------
Gộp các block SRT liên tiếp thành cụm câu hoàn chỉnh.
Mỗi block đầu ra kết thúc đúng tại một dấu câu: , . ? ! …

Cách dùng:
    python merge_srt_phrases.py <input.srt> [output.srt]

    Nếu không truyền output thì ghi đè lên file input.

Ví dụ:
    python merge_srt_phrases.py "video.srt"
    python merge_srt_phrases.py "video.srt" "video_merged.srt"
"""

import io
import re
import sys
from pathlib import Path

if sys.stdout.encoding and sys.stdout.encoding.lower() != "utf-8":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

# Dấu câu kết thúc một cụm — dừng gộp và xuất block
_END_PUNCT = re.compile(r"[.,?!…\u2026]+\s*$")

# Dấu câu "mạnh" — kết thúc câu, không nối tiếp câu mới vào block này
_STRONG_END = re.compile(r"[.?!…\u2026]+\s*$")


# ---------------------------------------------------------------------------
# SRT helpers
# ---------------------------------------------------------------------------

def ts_to_ms(t: str) -> int:
    m = re.match(r"(\d+):(\d+):(\d+)[,.](\d+)", t.strip())
    if not m:
        return 0
    h, mi, s, ms = map(int, m.groups())
    return ((h * 60 + mi) * 60 + s) * 1000 + ms


def ms_to_ts(ms: int) -> str:
    if ms < 0:
        ms = 0
    s, rem = divmod(ms, 1000)
    m, s = divmod(s, 60)
    h, m = divmod(m, 60)
    return f"{h:02d}:{m:02d}:{s:02d},{rem:03d}"


def parse_srt(raw: str) -> list[tuple[int, int, str]]:
    """Trả về list (start_ms, end_ms, text)."""
    raw = raw.replace("\r\n", "\n").replace("\r", "\n")
    blocks = re.split(r"\n\s*\n", raw.strip())
    cues: list[tuple[int, int, str]] = []
    for block in blocks:
        lines = [ln for ln in block.split("\n") if ln.strip()]
        if len(lines) < 3:
            continue
        time_line = lines[1].strip()
        if "-->" not in time_line:
            continue
        parts = time_line.split("-->")
        start = ts_to_ms(parts[0])
        end = ts_to_ms(parts[1])
        text = " ".join(ln.strip() for ln in lines[2:]).strip()
        if not text:
            continue
        cues.append((start, end, text))
    return cues


def write_srt(path: Path, merged: list[tuple[int, int, str]]) -> None:
    lines: list[str] = []
    for i, (start, end, text) in enumerate(merged, 1):
        lines.append(f"{i}")
        lines.append(f"{ms_to_ts(start)} --> {ms_to_ts(end)}")
        lines.append(text)
        lines.append("")
    path.write_text("\n".join(lines), encoding="utf-8")


# ---------------------------------------------------------------------------
# Core logic
# ---------------------------------------------------------------------------

def explode_cues(cues: list[tuple[int, int, str]]) -> list[tuple[int, int, str]]:
    """
    Tách từng cue tại các dấu câu bên trong text (không chỉ ở cuối).
    Timestamp của mỗi phần nhỏ được nội suy tuyến tính theo độ dài ký tự.
    Sau bước này mỗi phần nhỏ hoặc kết thúc bằng dấu câu, hoặc là đoạn cuối chưa có dấu.
    """
    result: list[tuple[int, int, str]] = []
    # Tách sau dấu câu, giữ dấu câu ở cuối phần trước
    _SPLIT_AT = re.compile(r"(?<=[,?.!…\u2026])\s*")

    for start_ms, end_ms, text in cues:
        parts = [p.strip() for p in _SPLIT_AT.split(text.strip()) if p.strip()]
        if len(parts) <= 1:
            result.append((start_ms, end_ms, text))
            continue

        duration = end_ms - start_ms
        total_chars = sum(len(p) for p in parts)
        cur_ms = start_ms
        for i, part in enumerate(parts):
            if i == len(parts) - 1:
                result.append((cur_ms, end_ms, part))
            else:
                part_end = cur_ms + (int(duration * len(part) / total_chars) if total_chars else 0)
                result.append((cur_ms, part_end, part))
                cur_ms = part_end

    return result


def merge_phrases(cues: list[tuple[int, int, str]]) -> list[tuple[int, int, str]]:
    """
    Gộp các cue liên tiếp cho đến khi text kết thúc bằng dấu câu.
    Gọi sau explode_cues để dấu câu bên trong cue cũng được xử lý.
    Timestamp: start = cue đầu, end = cue cuối của nhóm.
    """
    result: list[tuple[int, int, str]] = []
    buf_start: int | None = None
    buf_end: int | None = None
    buf_text: list[str] = []

    def flush() -> None:
        if buf_text:
            text = re.sub(r" +", " ", " ".join(buf_text)).strip()
            result.append((buf_start, buf_end, text))

    for start, end, text in cues:
        if buf_start is None:
            buf_start = start

        buf_end = end
        buf_text.append(text)

        if _END_PUNCT.search(text):
            flush()
            buf_start = None
            buf_end = None
            buf_text = []

    if buf_text:
        flush()

    return result


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main() -> int:
    if len(sys.argv) < 2:
        print("Dùng: python merge_srt_phrases.py <input.srt> [output.srt]")
        return 1

    input_path = Path(sys.argv[1])
    if len(sys.argv) >= 3:
        output_path = Path(sys.argv[2])
    else:
        out_dir = input_path.parent.parent / "srt-output"
        out_dir.mkdir(parents=True, exist_ok=True)
        output_path = out_dir / input_path.name

    if not input_path.exists():
        print(f"Không tìm thấy file: {input_path}")
        return 1

    raw = input_path.read_text(encoding="utf-8", errors="replace")
    cues = parse_srt(raw)
    print(f"Input : {len(cues)} blocks  ({input_path.name})")

    exploded = explode_cues(cues)
    print(f"Explode: {len(exploded)} blocks (sau tách nội bộ)")
    merged = merge_phrases(exploded)
    print(f"Output: {len(merged)} blocks  ({output_path.name})")

    write_srt(output_path, merged)
    print(f"Đã lưu: {output_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
