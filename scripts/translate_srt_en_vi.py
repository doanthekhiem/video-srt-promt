# One-off: EN SRT -> VI SRT, giữ nguyên index và timestamp.
from __future__ import annotations

import re
import sys
import time
from pathlib import Path

from deep_translator import GoogleTranslator


def parse_srt(raw: str) -> list[tuple[str, str, str]]:
    raw = raw.replace("\r\n", "\n").replace("\r", "\n")
    blocks = re.split(r"\n\s*\n", raw.strip())
    cues: list[tuple[str, str, str]] = []
    for block in blocks:
        lines = [ln for ln in block.split("\n") if ln is not None]
        if len(lines) < 3:
            continue
        idx, time_line = lines[0].strip(), lines[1].strip()
        if "-->" not in time_line:
            continue
        text = "\n".join(lines[2:]).strip()
        cues.append((idx, time_line, text))
    return cues


def build_srt(cues: list[tuple[str, str, str]]) -> str:
    parts: list[str] = []
    for idx, time_line, text in cues:
        parts.append(f"{idx}\n{time_line}\n{text}\n")
    return "\n".join(parts) + "\n"


def normalize_for_translate(s: str) -> str:
    s = s.replace("\n", " ")
    s = re.sub(r"\s+", " ", s).strip()
    return s


def translate_one(translator: GoogleTranslator, text: str, retries: int = 4) -> str:
    if not text:
        return ""
    src = normalize_for_translate(text)
    if not src:
        return ""
    last_err: Exception | None = None
    for attempt in range(retries):
        try:
            out = translator.translate(src)
            return out.strip() if out else src
        except Exception as e:
            last_err = e
            time.sleep(1.5 * (attempt + 1))
    raise RuntimeError(f"translate failed after {retries} tries: {last_err}") from last_err


def main() -> int:
    if len(sys.argv) < 3:
        print("usage: translate_srt_en_vi.py <input.srt> <output.srt>", file=sys.stderr)
        return 2
    inp = Path(sys.argv[1])
    outp = Path(sys.argv[2])
    raw = inp.read_text(encoding="utf-8", errors="replace")
    cues = parse_srt(raw)
    translator = GoogleTranslator(source="en", target="vi")
    total = len(cues)
    print(f"cues: {total}", flush=True)
    out_cues: list[tuple[str, str, str]] = []
    for i, (idx, time_line, text) in enumerate(cues):
        vi = translate_one(translator, text)
        out_cues.append((idx, time_line, vi))
        if (i + 1) % 25 == 0 or i + 1 == total:
            print(f"done {i + 1}/{total}", flush=True)
        time.sleep(0.12)
    outp.parent.mkdir(parents=True, exist_ok=True)
    outp.write_text(build_srt(out_cues), encoding="utf-8")
    print("wrote", outp, flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
