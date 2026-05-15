#!/usr/bin/env python3
"""
validate.py — Kiểm tra chất lượng file SRT VN dịch từ SRT EN gốc.

Cách dùng:
    python3 validate.py <VN.srt> <EN.srt>
    python3 validate.py <VN.srt> <EN.srt> --json out.json
    python3 validate.py --calibrate <thư_mục_chứa_SRT_EN>

Metric kiểm tra (xem speaker-profile.md để biết ngưỡng):
    - tts_ratio    = VN_syllables / TTS_RATE / duration       (≤ 95%)
    - content_ratio = VN_syllables / EN_words_in_window       (≥ 0.9 mong muốn, hard floor 0.7)
    - gap > 3s với block kế tiếp (nếu EN window không phải toàn filler)
    - độ dài block > 16s (lỗi), > 18s (lỗi tuyệt đối)
    - block bắt đầu bằng liên từ trống chủ ngữ
    - block chứa ≥ 2 dấu kết câu (vi phạm "một câu = một block")
"""
from __future__ import annotations
import argparse
import json
import os
import re
import statistics
import sys
from dataclasses import dataclass, field, asdict
from glob import glob

# ============================================================
# Cấu hình baseline cho speaker Game Theory / Secret History.
# Nếu dịch series khác, chạy --calibrate để tính lại baseline.
# ============================================================
EN_BASELINE_WPS   = 2.4   # file-level WPS trung bình của speaker
VN_PER_EN_RATIO   = 1.1   # số âm tiết VN ≈ 1.1 × số từ EN
TTS_RATE          = 4.5   # CapCut TTS VN, giọng mặc định, tốc độ 1.0x

# Block-level hard limits
TTS_CEILING       = 0.95  # tts_ratio > 95% là lỗi (đè block sau)
CONTENT_FLOOR     = 0.7   # content_ratio < 0.7 là lỗi (rút gọn quá mức)
CONTENT_TARGET    = 0.9   # content_ratio < 0.9 là cảnh báo
CONTENT_CEILING   = 1.5   # content_ratio > 1.5 là cảnh báo (có thể bịa)
GAP_LIMIT_SEC     = 3.0   # gap > 3s là lỗi (trừ filler-only window)
BLOCK_DUR_WARN    = 16.0  # block > 16s là cảnh báo nặng
BLOCK_DUR_FATAL   = 18.0  # block > 18s là lỗi tuyệt đối

# File-level mục tiêu
FILE_PASS_RATE    = 0.90  # ≥ 90% block phải đạt cả tts ≤ 95% và content ≥ 0.9
FILE_CONTENT_RATIO_MIN = 0.95
FILE_CONTENT_RATIO_MAX = 1.30

FILLER_EN = {
    "okay", "ok", "alright", "all", "right", "yeah", "yep", "yes",
    "uh", "um", "uhh", "umm", "you", "know", "so", "well", "like",
    "i", "mean", "kind", "of", "sort", "guys", "folks", "hey",
}

VN_FORBIDDEN_START = {"Và", "Nhưng", "Vì", "Bởi", "Để", "Mà", "Nên", "Vậy"}

# ============================================================
# Parsing
# ============================================================
@dataclass
class Block:
    idx: int
    start: float
    end: float
    text: str
    @property
    def dur(self) -> float: return self.end - self.start

def _ts_to_sec(ts: str) -> float | None:
    m = re.match(r"(\d{2}):(\d{2}):(\d{2})[,.](\d{3})", ts.strip())
    if not m: return None
    h, mn, s, ms = map(int, m.groups())
    return h*3600 + mn*60 + s + ms/1000

def parse_srt(path: str) -> list[Block]:
    with open(path, "r", encoding="utf-8-sig") as f:
        content = f.read()
    blocks: list[Block] = []
    for raw in re.split(r"\n\s*\n", content.strip()):
        lines = [l for l in raw.strip().split("\n") if l.strip()]
        if len(lines) < 2: continue
        ts_line = next((l for l in lines if "-->" in l), None)
        if not ts_line: continue
        parts = ts_line.split("-->")
        if len(parts) != 2: continue
        start, end = _ts_to_sec(parts[0]), _ts_to_sec(parts[1])
        if start is None or end is None: continue
        idx_line = lines[0].strip()
        idx = int(idx_line) if idx_line.isdigit() else len(blocks)+1
        text_lines = [l for l in lines if l != ts_line and l.strip() != idx_line]
        text = " ".join(text_lines).strip()
        if not text: continue
        blocks.append(Block(idx=idx, start=start, end=end, text=text))
    return blocks

# ============================================================
# Đếm âm tiết / từ
# ============================================================
def _strip_tags(text: str) -> str:
    text = re.sub(r"\[[^\]]*\]", " ", text)
    text = re.sub(r"<[^>]*>", " ", text)
    return text

def vn_syllables(text: str) -> int:
    text = _strip_tags(text)
    text = re.sub(r"[^\w\s]", " ", text)
    return len([w for w in text.split() if w])

def en_words(text: str, drop_filler: bool = False) -> int:
    text = _strip_tags(text).lower()
    tokens = [w for w in re.sub(r"[^\w'\-]", " ", text).split() if w]
    if drop_filler:
        tokens = [t for t in tokens if t not in FILLER_EN]
    return len(tokens)

def is_filler_only(text: str) -> bool:
    """Window EN có thể bỏ không (chỉ chứa filler / pause marker)."""
    tokens = [t for t in re.sub(r"[^\w'\-]", " ", _strip_tags(text).lower()).split() if t]
    if not tokens: return True
    non_filler = [t for t in tokens if t not in FILLER_EN]
    return len(non_filler) <= 1 and len(tokens) <= 6

# ============================================================
# Lấy nội dung EN trong window thời gian của block VN
# ============================================================
def en_in_window(en_blocks: list[Block], start: float, end: float) -> str:
    out = []
    for eb in en_blocks:
        if eb.end >= start and eb.start <= end:
            out.append(eb.text)
    return " ".join(out)

# ============================================================
# Phân tích từng block VN
# ============================================================
@dataclass
class BlockReport:
    idx: int
    start: float
    end: float
    dur: float
    text: str
    vn_syl: int
    en_words: int
    en_window: str
    tts_ratio: float
    content_ratio: float | None
    gap_to_next: float | None
    issues: list[str] = field(default_factory=list)

    @property
    def passed(self) -> bool:
        # block PASS nếu không có issue nào ở severity hard
        return not any(i.startswith("HARD:") for i in self.issues)

def analyze(vn: list[Block], en: list[Block]) -> list[BlockReport]:
    reports = []
    for i, b in enumerate(vn):
        dur = b.dur
        syl = vn_syllables(b.text)
        win_text = en_in_window(en, b.start, b.end)
        en_w = en_words(win_text, drop_filler=False)
        en_w_clean = en_words(win_text, drop_filler=True)

        tts_ratio = (syl / TTS_RATE / dur) if dur > 0 else 0.0
        content_ratio = (syl / en_w_clean) if en_w_clean > 0 else None

        gap = None
        if i + 1 < len(vn):
            gap = vn[i+1].start - b.end

        issues: list[str] = []

        # Cổng 3 — TTS overflow
        if tts_ratio > TTS_CEILING:
            issues.append(f"HARD: tts_ratio {tts_ratio*100:.0f}% > {TTS_CEILING*100:.0f}% (đè block sau)")

        # Cổng 8 — bảo toàn nội dung
        if content_ratio is not None:
            if content_ratio < CONTENT_FLOOR and not is_filler_only(win_text):
                issues.append(f"HARD: content_ratio {content_ratio:.2f} < {CONTENT_FLOOR} (bỏ nội dung EN)")
            elif content_ratio < CONTENT_TARGET and not is_filler_only(win_text):
                issues.append(f"WARN: content_ratio {content_ratio:.2f} < {CONTENT_TARGET}")
            elif content_ratio > CONTENT_CEILING:
                issues.append(f"WARN: content_ratio {content_ratio:.2f} > {CONTENT_CEILING} (có thể bịa)")

        # Cổng 4 — độ dài block
        if dur > BLOCK_DUR_FATAL:
            issues.append(f"HARD: dur {dur:.1f}s > {BLOCK_DUR_FATAL}s (lỗi tuyệt đối, phải tách)")
        elif dur > BLOCK_DUR_WARN:
            issues.append(f"WARN: dur {dur:.1f}s > {BLOCK_DUR_WARN}s")

        # Gap với block sau
        if gap is not None and gap > GAP_LIMIT_SEC:
            # Có thể chấp nhận nếu EN giữa gap là filler-only
            if i+1 < len(vn):
                gap_en = en_in_window(en, b.end, vn[i+1].start)
                if not is_filler_only(gap_en):
                    issues.append(f"HARD: gap {gap:.1f}s > {GAP_LIMIT_SEC}s và EN window không chỉ chứa filler")
                else:
                    issues.append(f"WARN: gap {gap:.1f}s > {GAP_LIMIT_SEC}s (EN filler-only)")

        # Cổng 1 — một câu = một block
        terminal_punct = re.findall(r"[.!?](?=\s|$)", b.text)
        if len(terminal_punct) >= 2:
            issues.append(f"HARD: chứa {len(terminal_punct)} dấu kết câu trong 1 block (vi phạm 1 câu = 1 block)")
        elif len(terminal_punct) == 1 and not re.search(r"[.!?]\s*$", b.text):
            issues.append("HARD: dấu kết câu nằm giữa block (không ở cuối)")

        # Cổng 2 — không bắt đầu bằng liên từ trống chủ ngữ
        if i > 0:
            prev = vn[i-1].text.strip()
            if re.search(r"[.!?]\s*$", prev):
                first_word = b.text.strip().split()[0] if b.text.strip() else ""
                if first_word in VN_FORBIDDEN_START:
                    issues.append(f"WARN: bắt đầu bằng '{first_word}' sau khi block trước kết câu")

        reports.append(BlockReport(
            idx=b.idx, start=b.start, end=b.end, dur=dur, text=b.text,
            vn_syl=syl, en_words=en_w_clean, en_window=win_text,
            tts_ratio=tts_ratio, content_ratio=content_ratio,
            gap_to_next=gap, issues=issues,
        ))
    return reports

# ============================================================
# Tóm tắt file
# ============================================================
def summarize(reports: list[BlockReport], vn: list[Block], en: list[Block]) -> dict:
    total = len(reports)
    passed = sum(1 for r in reports if r.passed)
    hard_issues = sum(1 for r in reports if any(i.startswith("HARD:") for i in r.issues))
    warn_issues = sum(1 for r in reports if any(i.startswith("WARN:") for i in r.issues))

    # tts distribution
    tts_vals = [r.tts_ratio for r in reports]
    cr_vals = [r.content_ratio for r in reports if r.content_ratio is not None]

    total_vn_syl = sum(r.vn_syl for r in reports)
    total_en_words = sum(en_words(e.text, drop_filler=True) for e in en)
    file_content_ratio = total_vn_syl / total_en_words if total_en_words else None

    file_dur = vn[-1].end - vn[0].start if vn else 0
    median_vn_density = statistics.median([r.vn_syl/r.dur for r in reports if r.dur>0]) if reports else 0

    end_diff = abs(vn[-1].end - en[-1].end) if vn and en else None

    return {
        "total_blocks": total,
        "passed_blocks": passed,
        "pass_rate": passed/total if total else 0,
        "blocks_with_hard_issues": hard_issues,
        "blocks_with_warn_issues": warn_issues,
        "tts_ratio_mean": statistics.mean(tts_vals) if tts_vals else 0,
        "tts_ratio_median": statistics.median(tts_vals) if tts_vals else 0,
        "tts_over_95": sum(1 for v in tts_vals if v > TTS_CEILING),
        "tts_under_40": sum(1 for v in tts_vals if v < 0.4),
        "content_ratio_mean": statistics.mean(cr_vals) if cr_vals else None,
        "content_ratio_median": statistics.median(cr_vals) if cr_vals else None,
        "content_under_floor": sum(1 for v in cr_vals if v < CONTENT_FLOOR),
        "content_under_target": sum(1 for v in cr_vals if v < CONTENT_TARGET),
        "file_content_ratio": file_content_ratio,
        "median_vn_density_syl_per_sec": median_vn_density,
        "blocks_over_16s": sum(1 for r in reports if r.dur > BLOCK_DUR_WARN),
        "blocks_over_18s": sum(1 for r in reports if r.dur > BLOCK_DUR_FATAL),
        "gaps_over_3s_real": sum(1 for r in reports if r.gap_to_next and r.gap_to_next > GAP_LIMIT_SEC
                                  and any("HARD: gap" in i for i in r.issues)),
        "end_time_diff_sec": end_diff,
    }

# ============================================================
# Báo cáo console
# ============================================================
def print_report(reports: list[BlockReport], summary: dict, max_issues: int = 30):
    print("=" * 76)
    print(f"  TỔNG QUAN")
    print("=" * 76)
    print(f"  Block VN:                {summary['total_blocks']}")
    print(f"  Block ĐẠT (no HARD):     {summary['passed_blocks']} ({summary['pass_rate']*100:.1f}%)")
    print(f"  Block có lỗi HARD:       {summary['blocks_with_hard_issues']}")
    print(f"  Block có lỗi WARN:       {summary['blocks_with_warn_issues']}")
    print()
    print(f"  tts_ratio mean / median: {summary['tts_ratio_mean']*100:.0f}% / {summary['tts_ratio_median']*100:.0f}%")
    print(f"  Block tts > 95% (đè):    {summary['tts_over_95']}")
    print(f"  Block tts < 40% (thưa):  {summary['tts_under_40']}")
    print()
    cr_m = summary['content_ratio_median']
    print(f"  content_ratio median:    {cr_m:.2f}" if cr_m else "  content_ratio median:    n/a")
    print(f"  Block content < 0.7:     {summary['content_under_floor']} (rút gọn nghiêm trọng)")
    print(f"  Block content < 0.9:     {summary['content_under_target']} (rút gọn nhẹ/cảnh báo)")
    fr = summary['file_content_ratio']
    print(f"  File content ratio:      {fr:.2f}" if fr else "  File content ratio:      n/a")
    print(f"  VN density median:       {summary['median_vn_density_syl_per_sec']:.2f} syl/s")
    print()
    print(f"  Block > 16s:             {summary['blocks_over_16s']}")
    print(f"  Block > 18s (cấm):       {summary['blocks_over_18s']}")
    print(f"  Gap > 3s (không filler): {summary['gaps_over_3s_real']}")
    et = summary['end_time_diff_sec']
    print(f"  Sai lệch end VN vs EN:   {et:.1f}s" if et is not None else "  Sai lệch end VN vs EN:   n/a")
    print()

    # Verdict
    verdict_ok = (
        summary['pass_rate'] >= FILE_PASS_RATE
        and summary['tts_over_95'] == 0
        and summary['blocks_over_18s'] == 0
        and summary['gaps_over_3s_real'] == 0
        and (fr is None or (FILE_CONTENT_RATIO_MIN <= fr <= FILE_CONTENT_RATIO_MAX))
    )
    print("=" * 76)
    if verdict_ok:
        print("  KẾT LUẬN: ✅ ĐẠT — file có thể xuất.")
    else:
        print("  KẾT LUẬN: ❌ KHÔNG ĐẠT — phải fix trước khi xuất.")
        if summary['pass_rate'] < FILE_PASS_RATE:
            print(f"    - pass rate {summary['pass_rate']*100:.1f}% < {FILE_PASS_RATE*100:.0f}%")
        if summary['tts_over_95'] > 0:
            print(f"    - {summary['tts_over_95']} block có tts_ratio > 95% (sẽ đè block sau)")
        if summary['blocks_over_18s'] > 0:
            print(f"    - {summary['blocks_over_18s']} block > 18s")
        if summary['gaps_over_3s_real'] > 0:
            print(f"    - {summary['gaps_over_3s_real']} gap > 3s không phải filler (mất nội dung)")
        if fr is not None and not (FILE_CONTENT_RATIO_MIN <= fr <= FILE_CONTENT_RATIO_MAX):
            print(f"    - file content_ratio {fr:.2f} ngoài dải {FILE_CONTENT_RATIO_MIN}-{FILE_CONTENT_RATIO_MAX}")
    print("=" * 76)
    print()

    # Danh sách block lỗi (HARD trước, WARN sau)
    hard_blocks = [r for r in reports if any(i.startswith("HARD:") for i in r.issues)]
    warn_blocks = [r for r in reports if not any(i.startswith("HARD:") for i in r.issues)
                                       and any(i.startswith("WARN:") for i in r.issues)]
    if hard_blocks:
        print(f"  --- {len(hard_blocks)} BLOCK LỖI HARD (hiển thị {min(max_issues, len(hard_blocks))}) ---")
        for r in hard_blocks[:max_issues]:
            print(f"\n  #{r.idx} @ {r.start:.1f}-{r.end:.1f}s (dur={r.dur:.1f}s) "
                  f"vn_syl={r.vn_syl} en_w={r.en_words} "
                  f"tts={r.tts_ratio*100:.0f}% "
                  f"cr={('%.2f' % r.content_ratio) if r.content_ratio else 'n/a'}")
            for i in r.issues:
                print(f"    {i}")
            print(f"    VN: {r.text[:140]}")
            print(f"    EN: {r.en_window[:140]}")
    if warn_blocks and len(hard_blocks) < max_issues:
        remaining = max_issues - len(hard_blocks)
        print(f"\n  --- {len(warn_blocks)} BLOCK CẢNH BÁO (hiển thị {min(remaining, len(warn_blocks))}) ---")
        for r in warn_blocks[:remaining]:
            print(f"\n  #{r.idx} @ {r.start:.1f}-{r.end:.1f}s (dur={r.dur:.1f}s)")
            for i in r.issues:
                print(f"    {i}")

# ============================================================
# Calibrate — đo baseline cho corpus mới
# ============================================================
def calibrate(folder: str):
    files = sorted(glob(os.path.join(folder, "**", "*.srt"), recursive=True))
    if not files:
        print(f"Không tìm thấy SRT trong {folder}")
        return
    print(f"Đo {len(files)} file SRT EN trong {folder}\n")
    print(f"{'File':<70} {'Dur(s)':>8} {'Words':>7} {'WPS':>6} {'Median':>8}")
    print("-" * 105)
    all_block_wps = []
    file_wps = []
    for path in files:
        blocks = parse_srt(path)
        if not blocks: continue
        dur = blocks[-1].end - blocks[0].start
        total_w = sum(en_words(b.text, drop_filler=False) for b in blocks)
        if dur <= 0 or total_w == 0: continue
        block_wps = [en_words(b.text)/b.dur for b in blocks if b.dur > 0.5 and en_words(b.text) > 0]
        if not block_wps: continue
        wps = total_w/dur
        med = statistics.median(block_wps)
        file_wps.append(wps)
        all_block_wps.extend(block_wps)
        print(f"{os.path.basename(path)[:65]:<70} {dur:>8.0f} {total_w:>7} {wps:>6.2f} {med:>8.2f}")
    print()
    print(f"Corpus: {len(all_block_wps)} block từ {len(file_wps)} file")
    print(f"File-level WPS — trung bình: {statistics.mean(file_wps):.2f}, "
          f"min: {min(file_wps):.2f}, max: {max(file_wps):.2f}")
    print(f"Block-level WPS — median: {statistics.median(all_block_wps):.2f}, "
          f"mean: {statistics.mean(all_block_wps):.2f}")
    print()
    suggested = round(statistics.mean(file_wps), 1)
    print(f"Gợi ý EN_BASELINE_WPS = {suggested}")
    print(f"Suy ra mật độ VN tự nhiên = {suggested}*1.1 = {suggested*1.1:.2f} syl/s")
    print(f"Suy ra TTS sweet spot = {suggested*1.1/TTS_RATE*100:.0f}% (target = sweet ± 15%)")

# ============================================================
# Main
# ============================================================
def main():
    ap = argparse.ArgumentParser(description="Validate VN SRT against EN source.")
    ap.add_argument("vn", nargs="?", help="Đường dẫn SRT VN")
    ap.add_argument("en", nargs="?", help="Đường dẫn SRT EN gốc")
    ap.add_argument("--json", help="Xuất báo cáo JSON ra file")
    ap.add_argument("--calibrate", help="Thư mục SRT EN để đo baseline mới")
    ap.add_argument("--max-issues", type=int, default=30,
                    help="Số block lỗi tối đa hiển thị (mặc định 30)")
    args = ap.parse_args()

    if args.calibrate:
        calibrate(args.calibrate)
        return

    if not args.vn or not args.en:
        ap.print_help()
        sys.exit(2)

    if not os.path.exists(args.vn):
        print(f"Không tìm thấy file VN: {args.vn}"); sys.exit(2)
    if not os.path.exists(args.en):
        print(f"Không tìm thấy file EN: {args.en}"); sys.exit(2)

    vn = parse_srt(args.vn)
    en = parse_srt(args.en)
    if not vn:
        print("File VN không có block hợp lệ."); sys.exit(2)
    if not en:
        print("File EN không có block hợp lệ."); sys.exit(2)

    print(f"VN: {args.vn} ({len(vn)} block)")
    print(f"EN: {args.en} ({len(en)} block)")
    print()

    reports = analyze(vn, en)
    summary = summarize(reports, vn, en)
    print_report(reports, summary, max_issues=args.max_issues)

    if args.json:
        out = {
            "vn_path": args.vn,
            "en_path": args.en,
            "summary": summary,
            "blocks": [
                {
                    **{k: v for k, v in asdict(r).items() if k != "en_window"},
                    "en_window_preview": r.en_window[:200],
                }
                for r in reports
            ],
        }
        with open(args.json, "w", encoding="utf-8") as f:
            json.dump(out, f, ensure_ascii=False, indent=2)
        print(f"\nĐã ghi báo cáo JSON: {args.json}")

    # exit code: 0 nếu đạt, 1 nếu không
    verdict_ok = (
        summary['pass_rate'] >= FILE_PASS_RATE
        and summary['tts_over_95'] == 0
        and summary['blocks_over_18s'] == 0
        and summary['gaps_over_3s_real'] == 0
    )
    sys.exit(0 if verdict_ok else 1)

if __name__ == "__main__":
    main()
