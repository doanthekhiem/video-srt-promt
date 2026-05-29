#!/usr/bin/env python3
"""
build_srt.py — Lắp file SRT VN từ các file segment dạng `END_TS<TAB>text`.

Cách dùng:
    python3 build_srt.py <out.srt> seg1.txt seg2.txt ...

Mỗi dòng trong segN.txt: `END_TS<TAB>nội dung VN` (một dòng).
  - END_TS: thời điểm KẾT THÚC block, dạng HH:MM:SS,mmm (hoặc MM:SS,mmm / SS,mmm).
  - start của block = end (raw) của block trước → liền mạch, gap = 0.
  - Block đầu tiên bắt đầu cố định ở START0.
Builder tự inset INSET giây mỗi đầu để tránh window-overlap bleed khi tính content_ratio
(xem memory srt-window-overlap-inset). Đánh số block liên tục từ 1.

Dòng trống / dòng bắt đầu bằng '#' bị bỏ qua.
"""
import sys, re

START0 = 0.960   # block đầu bắt đầu ở 00:00:00,960
INSET  = 0.002   # inset mỗi đầu để cắt bleed biên

def parse_ts(s: str) -> float:
    s = s.strip().replace('.', ',')
    parts = s.split(',')
    hms = parts[0]
    ms = int(parts[1]) if len(parts) > 1 and parts[1] != '' else 0
    bits = [int(x) for x in hms.split(':')]
    while len(bits) < 3:
        bits.insert(0, 0)
    h, m, sec = bits
    return h*3600 + m*60 + sec + ms/1000

def fmt_ts(t: float) -> str:
    if t < 0:
        t = 0.0
    ms = int(round(t * 1000))
    h, ms = divmod(ms, 3600000)
    m, ms = divmod(ms, 60000)
    s, ms = divmod(ms, 1000)
    return f"{h:02d}:{m:02d}:{s:02d},{ms:03d}"

def main():
    if len(sys.argv) < 3:
        print("Cách dùng: python3 build_srt.py <out.srt> seg1.txt seg2.txt ...")
        sys.exit(2)
    out_path = sys.argv[1]
    seg_paths = sys.argv[2:]

    rows = []  # (end_raw_ts, text)
    for p in seg_paths:
        with open(p, encoding='utf-8') as f:
            for ln, raw in enumerate(f, 1):
                line = raw.rstrip('\n')
                if not line.strip() or line.lstrip().startswith('#'):
                    continue
                if '\t' not in line:
                    print(f"[{p}:{ln}] thiếu TAB: {line[:60]!r}")
                    sys.exit(2)
                ts, text = line.split('\t', 1)
                rows.append((parse_ts(ts), text.strip()))

    blocks = []
    prev_end = START0
    for i, (end_raw, text) in enumerate(rows):
        start_raw = START0 if i == 0 else prev_end
        s = start_raw + INSET
        e = end_raw - INSET
        if e <= s:           # block quá ngắn / END không tăng → cảnh báo
            print(f"CẢNH BÁO block {i+1}: end <= start ({fmt_ts(start_raw)} -> {fmt_ts(end_raw)})")
            e = s + 0.05
        blocks.append((s, e, text))
        prev_end = end_raw

    with open(out_path, 'w', encoding='utf-8') as f:
        for n, (s, e, text) in enumerate(blocks, 1):
            f.write(f"{n}\n{fmt_ts(s)} --> {fmt_ts(e)}\n{text}\n\n")
    print(f"Đã ghi {len(blocks)} block → {out_path}")

if __name__ == '__main__':
    main()
