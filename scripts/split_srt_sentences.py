# -*- coding: utf-8 -*-
"""
split_srt_sentences.py
----------------------
Tách file SRT thành từng câu hoàn chỉnh, mỗi block = 1 câu.

Cách dùng:
    python split_srt_sentences.py <input.srt> [output.srt]

Nếu không truyền output thì ghi đè lên file input.

Ví dụ:
    python split_srt_sentences.py "video.srt"
    python split_srt_sentences.py "video.srt" "video_fixed.srt"
"""

import io
import re
import sys
from pathlib import Path

# Đảm bảo stdout hỗ trợ Unicode trên Windows
if sys.stdout.encoding and sys.stdout.encoding.lower() != "utf-8":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")


def ts_to_ms(t: str) -> int:
    m = re.match(r"(\d+):(\d+):(\d+),(\d+)", t)
    if not m:
        return 0
    h, mi, s, ms = map(int, m.groups())
    return ((h * 60 + mi) * 60 + s) * 1000 + ms


def ms_to_ts(ms: int) -> str:
    if ms < 0:
        ms = 0
    s, ms = divmod(ms, 1000)
    m, s = divmod(s, 60)
    h, m = divmod(m, 60)
    return f"{h:02d}:{m:02d}:{s:02d},{ms:03d}"


def clean(text: str) -> str:
    # xoá các chú thích trong ngoặc vuông, vd [cười khẩy], [applause], [music]
    text = re.sub(r"\[[^\]]*\]", "", text)
    # thay "Được rồi", "Được chứ" (mọi biến thể hoa/thường) thành "Okay"
    text = re.sub(r"[Đđ]ược rồi", "Okay", text)
    text = re.sub(r"[Đđ]ược chứ", "Okay", text)
    text = re.sub(r"\s+", " ", text).strip()
    # sửa số bị tách sai, vd "70. 000" → "70.000"
    text = re.sub(r"(\d)\.\s+(\d)", r"\1.\2", text)
    # loại khoảng trắng trước dấu câu
    text = re.sub(r"\s+([.?!,;:])", r"\1", text)
    # đảm bảo sau dấu câu cuối câu có khoảng trắng (trừ cuối chuỗi)
    text = re.sub(r"([.?!])([^\s.?!\d'\"])", r"\1 \2", text)
    return text.strip()


def is_sentence_boundary(text: str, pos: int) -> bool:
    """True nếu vị trí pos là kết thúc câu hợp lệ (không phải số hoặc ellipsis)."""
    window = text[max(0, pos - 2): pos + 3]
    if re.search(r"\.[\s.]*\.", window):
        return False
    before = text[pos - 1] if pos > 0 else ""
    after = text[pos + 1] if pos + 1 < len(text) else ""
    if before.isdigit() and (
        after.isdigit()
        or (after == " " and pos + 2 < len(text) and text[pos + 2].isdigit())
    ):
        return False
    return True


def split_sentences(text: str) -> list[str]:
    """Tách text thành danh sách câu hoàn chỉnh."""
    text = clean(text)
    sentences: list[str] = []
    current = ""
    i = 0
    while i < len(text):
        ch = text[i]
        current += ch
        if ch in ".?!":
            if is_sentence_boundary(text, i):
                # ăn thêm dấu câu liền kề nếu có (!!, ?!)
                while i + 1 < len(text) and text[i + 1] in ".?!":
                    i += 1
                    current += text[i]
                sentences.append(current.strip())
                current = ""
        i += 1
    if current.strip():
        sentences.append(current.strip())
    return [s for s in sentences if s]


def parse_blocks(path: Path) -> list[tuple[int, int, str]]:
    text = path.read_text(encoding="utf-8-sig")
    blocks: list[tuple[int, int, str]] = []
    for chunk in re.split(r"\n\s*\n", text.strip()):
        lines = [ln for ln in chunk.splitlines() if ln.strip()]
        if len(lines) < 2:
            continue
        if not lines[0].strip().isdigit():
            continue
        m = re.match(
            r"(\d\d:\d\d:\d\d,\d\d\d)\s*-->\s*(\d\d:\d\d:\d\d,\d\d\d)", lines[1]
        )
        if not m:
            continue
        st, en = ts_to_ms(m.group(1)), ts_to_ms(m.group(2))
        body = " ".join(lines[2:])
        blocks.append((st, en, body))
    return blocks


def expand_blocks(blocks: list[tuple[int, int, str]]) -> list[tuple[int, int, str]]:
    """Tách mỗi block thành các câu riêng, phân bổ timing theo tỷ lệ ký tự."""
    result: list[tuple[int, int, str]] = []
    for st, en, body in blocks:
        sentences = split_sentences(body)
        if not sentences:
            continue
        if len(sentences) == 1:
            result.append((st, en, sentences[0]))
            continue
        duration = en - st
        total_chars = sum(len(s) for s in sentences)
        if total_chars == 0:
            result.append((st, en, body))
            continue
        cursor = st
        for idx, sent in enumerate(sentences):
            ratio = len(sent) / total_chars
            seg_end = cursor + int(duration * ratio) if idx < len(sentences) - 1 else en
            result.append((cursor, seg_end, sent))
            cursor = seg_end
    return result


def chain_times(blocks: list[tuple[int, int, str]]) -> list[tuple[int, int, str]]:
    """start của block sau = end của block trước."""
    if not blocks:
        return blocks
    result = [blocks[0]]
    for i in range(1, len(blocks)):
        _, en, body = blocks[i]
        result.append((result[i - 1][1], en, body))
    return result


def write_srt(path: Path, blocks: list[tuple[int, int, str]]) -> None:
    out: list[str] = []
    for idx, (st, en, body) in enumerate(blocks, 1):
        out.append(str(idx))
        out.append(f"{ms_to_ts(st)} --> {ms_to_ts(en)}")
        out.append(body)
        out.append("")
    path.write_text("\n".join(out) + "\n", encoding="utf-8")


def main() -> None:
    if len(sys.argv) < 2:
        print("Dùng: python split_srt_sentences.py <input.srt> [output.srt]")
        sys.exit(1)

    input_path = Path(sys.argv[1])
    output_path = Path(sys.argv[2]) if len(sys.argv) >= 3 else input_path

    if not input_path.exists():
        print(f"Không tìm thấy file: {input_path}")
        sys.exit(1)

    blocks = parse_blocks(input_path)
    print(f"Input : {len(blocks)} blocks  ({input_path.name})")

    expanded = expand_blocks(blocks)
    chained = chain_times(expanded)
    print(f"Output: {len(chained)} blocks  ({output_path.name})")

    write_srt(output_path, chained)
    print(f"Đã lưu: {output_path}")


if __name__ == "__main__":
    main()
