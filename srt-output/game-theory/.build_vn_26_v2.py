#!/usr/bin/env python3
"""Build VN SRT using sentence-boundary detection.

Algorithm:
1. Parse EN srt into blocks.
2. Flatten into a word stream with interpolated times.
3. Identify sentence boundaries (`. ? !`) and build list of sentences.
4. Each VN block in TRANSLATIONS covers one or more EN sentences identified by `last_en_idx`.
   - VN block end time = end time of the last EN sentence that ENDS WITHIN or before block `last_en_idx`.
   - VN block start time = end of previous VN block (or sentence-aware start for first).
"""
import re
import os
import importlib.util

EN = os.path.expanduser("~/projects/Khiemdt/video-srt-promt/srt/game-theory/[English] Game Theory #26  The Holy Empire of AI.srt")
OUT = os.path.expanduser("~/projects/Khiemdt/video-srt-promt/srt-output/game-theory/[Vietnamese] Game Theory #26  The Holy Empire of AI.srt")
TRANS_PY = os.path.expanduser("~/projects/Khiemdt/video-srt-promt/srt-output/game-theory/.build_vn_26.py")

def ts_to_sec(ts):
    m = re.match(r"(\d{2}):(\d{2}):(\d{2})[,.](\d{3})", ts.strip())
    if not m: return None
    h, mn, s, ms = map(int, m.groups())
    return h*3600 + mn*60 + s + ms/1000

def sec_to_ts(sec):
    if sec < 0: sec = 0
    h = int(sec // 3600); sec -= h*3600
    m = int(sec // 60);   sec -= m*60
    s = int(sec)
    ms = int(round((sec - s) * 1000))
    if ms == 1000: s += 1; ms = 0
    return f"{h:02d}:{m:02d}:{s:02d},{ms:03d}"

def parse_en(path):
    with open(path, "r", encoding="utf-8-sig") as f:
        content = f.read()
    blocks = []
    for raw in re.split(r"\n\s*\n", content.strip()):
        lines = [l for l in raw.strip().split("\n") if l.strip()]
        if len(lines) < 3:
            continue
        try:
            idx = int(lines[0].strip())
        except ValueError:
            continue
        ts = lines[1].strip()
        text = " ".join(lines[2:]).strip()
        try:
            start_sec = ts_to_sec(ts.split("-->")[0])
            end_sec = ts_to_sec(ts.split("-->")[1])
        except Exception:
            continue
        blocks.append({"idx": idx, "ts": ts, "text": text, "start": start_sec, "end": end_sec})
    blocks.sort(key=lambda b: b["idx"])
    return blocks

def build_sentences(en_blocks):
    """Yields list of {text, start, end, last_block_idx} per sentence."""
    sentences = []
    cur_words = []
    cur_start = None
    cur_last_idx = None
    for blk in en_blocks:
        tokens = blk["text"].split()
        n = len(tokens)
        if n == 0: continue
        dur = blk["end"] - blk["start"]
        for j, tok in enumerate(tokens):
            word_start = blk["start"] + j/n * dur
            word_end   = blk["start"] + (j+1)/n * dur
            if cur_start is None:
                cur_start = word_start
            cur_words.append(tok)
            cur_last_idx = blk["idx"]
            if re.search(r"[.!?]$", tok):
                txt = " ".join(cur_words).strip()
                sentences.append({"text": txt, "start": cur_start, "end": word_end, "last_block_idx": cur_last_idx})
                cur_words = []
                cur_start = None
    if cur_words:
        sentences.append({"text": " ".join(cur_words), "start": cur_start, "end": en_blocks[-1]["end"], "last_block_idx": en_blocks[-1]["idx"]})
    return sentences

def load_translations():
    spec = importlib.util.spec_from_file_location("buildmod", TRANS_PY)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod.TRANSLATIONS

en_blocks = parse_en(EN)
sentences = build_sentences(en_blocks)
print(f"EN blocks: {len(en_blocks)}, EN sentences detected: {len(sentences)}")

TRANSLATIONS = load_translations()
print(f"Translations: {len(TRANSLATIONS)}")

en_by_idx = {b["idx"]: b for b in en_blocks}

FILLER_EN = {
    "okay", "ok", "alright", "all", "right", "yeah", "yep", "yes",
    "uh", "um", "uhh", "umm", "you", "know", "so", "well", "like",
    "i", "mean", "kind", "of", "sort", "guys", "folks", "hey",
}

def is_filler_sentence(text):
    tokens = re.sub(r"[^\w'\-]", " ", text.lower()).split()
    if not tokens: return True
    non_filler = [t for t in tokens if t not in FILLER_EN]
    return len(non_filler) <= 1 and len(tokens) <= 4

# Walk through translations
output = []
prev_sent_idx = -1   # last fully-consumed sentence index
prev_end_sec = en_blocks[0]["start"]
errors = []

for i, entry in enumerate(TRANSLATIONS, start=1):
    marker, vn_text = entry
    if isinstance(marker, float):
        end_sec = marker
        start_sec = prev_end_sec
        if end_sec <= start_sec:
            errors.append(f"Block {i}: float end {end_sec:.3f} <= prev start {start_sec:.3f}")
            continue
        output.append((start_sec, end_sec, vn_text))
        prev_end_sec = end_sec
        while prev_sent_idx + 1 < len(sentences) and sentences[prev_sent_idx + 1]["end"] <= end_sec + 0.01:
            prev_sent_idx += 1
    else:
        last_idx = marker
        if last_idx not in en_by_idx:
            errors.append(f"Block {i}: last_idx {last_idx} not found")
            continue
        time_limit = en_by_idx[last_idx]["end"]
        # Find the last NON-FILLER sentence ending within (prev_end_sec, time_limit]
        # Also accept the very-last sentence in range even if filler.
        target_sent_idx = None
        last_in_range = None
        for si in range(prev_sent_idx + 1, len(sentences)):
            if sentences[si]["end"] <= time_limit + 0.01:
                last_in_range = si
                if not is_filler_sentence(sentences[si]["text"]):
                    target_sent_idx = si
            else:
                break
        if target_sent_idx is None and last_in_range is not None:
            target_sent_idx = last_in_range
        if target_sent_idx is not None:
            # Use sentence's natural end
            end_sec = sentences[target_sent_idx]["end"]
            first_covered = prev_sent_idx + 1
            start_sec = sentences[first_covered]["start"] if first_covered < len(sentences) else prev_end_sec
            start_sec = max(start_sec, prev_end_sec)
            prev_sent_idx = target_sent_idx
        else:
            # Mid-sentence split or no new sentence end: cap at block end
            end_sec = time_limit
            start_sec = prev_end_sec
        if end_sec <= start_sec:
            errors.append(f"Block {i}: end {end_sec:.3f} <= start {start_sec:.3f} (last_idx={last_idx})")
            continue
        output.append((start_sec, end_sec, vn_text))
        prev_end_sec = end_sec

print(f"\nVN blocks built: {len(output)}")
if errors:
    print("ERRORS:")
    for e in errors[:30]: print(" ", e)

# Auto-split long blocks (> 14s) at the nearest comma to the temporal midpoint.
FORBIDDEN_START_WORDS = {"và", "nhưng", "vì", "bởi", "để", "mà", "nên", "vậy"}

def split_long(blocks, max_dur=14.0):
    out = []
    for s, e, txt in blocks:
        dur = e - s
        if dur <= max_dur or "," not in txt:
            out.append((s, e, txt))
            continue
        words = txt.split()
        n = len(words)
        # Find comma indices
        comma_positions = [i for i, w in enumerate(words) if w.endswith(",")]
        if not comma_positions:
            out.append((s, e, txt))
            continue
        # Pick comma closest to middle, where next word is not forbidden-start
        best = None
        best_dist = n
        for i in comma_positions:
            if i + 1 < n:
                next_word = words[i+1].rstrip(",.?!").lower()
                if next_word in FORBIDDEN_START_WORDS:
                    continue
            dist = abs(i - n//2)
            if dist < best_dist:
                best_dist = dist
                best = i
        if best is None:
            out.append((s, e, txt))
            continue
        part1_words = words[:best+1]
        part2_words = words[best+1:]
        part1 = " ".join(part1_words).rstrip(",")
        part2 = " ".join(part2_words)
        # Capitalize part2 if needed
        if part2 and part2[0].islower():
            part2 = part2[0].upper() + part2[1:]
        # Time split proportional to syllable count
        syl1 = max(1, len([w for w in part1_words if w.strip(",.?!")]))
        syl2 = max(1, len([w for w in part2_words if w.strip(",.?!")]))
        split_t = s + dur * syl1 / (syl1 + syl2)
        # Recursively split if still too long
        out.extend(split_long([(s, split_t, part1)], max_dur))
        out.extend(split_long([(split_t, e, part2)], max_dur))
    return out

output = split_long(output, max_dur=14.0)
print(f"After split: {len(output)} blocks")

# Close gaps > 1s by extending previous block's end to next block's start
def close_gaps(blocks, max_gap=1.0):
    if not blocks: return blocks
    out = [list(blocks[0])]
    for i in range(1, len(blocks)):
        s, e, t = blocks[i]
        prev_end = out[-1][1]
        gap = s - prev_end
        if gap > max_gap:
            out[-1][1] = s - 0.001
        out.append([s, e, t])
    return [tuple(b) for b in out]

output = close_gaps(output, max_gap=1.0)

# Merge consecutive very-short blocks (≤3 syllables) into the previous block.
# This handles speaker's list-style enumerations ("Napoleon. Hitler. Stalin.") where
# auto-sub time windows are too generous for one-word sentences.
def vn_syl_count(text):
    cleaned = re.sub(r"[^\w\s]", " ", text)
    return len([w for w in cleaned.split() if w])

def merge_short_into_prev(blocks, max_short_syl=3, max_dur_after=12.0):
    if not blocks: return blocks
    out = [list(blocks[0])]
    for i in range(1, len(blocks)):
        s, e, t = blocks[i]
        syl = vn_syl_count(t)
        prev_s, prev_e, prev_t = out[-1]
        prev_syl = vn_syl_count(prev_t)
        merged_dur = e - prev_s
        # Merge if current is short AND result not too long AND prev doesn't already end with .?! ... actually we want to allow joining
        if syl <= max_short_syl and merged_dur <= max_dur_after:
            # Replace prev's trailing punctuation with comma if it ends with period
            new_text = prev_t
            if re.search(r"[.!?]\s*$", new_text):
                new_text = re.sub(r"[.!?]+\s*$", ",", new_text)
            # Append current text (lowercase first letter for list flow)
            cur_text = t
            if cur_text and cur_text[0].isupper() and prev_syl <= 25:
                # Keep names capitalized; otherwise lowercase
                first_word = cur_text.split()[0] if cur_text.split() else ""
                # Heuristic: if it looks like a proper name (e.g., Stalin, Napoleon, JD Vance)
                # keep it. Otherwise lowercase.
                if first_word and first_word[0].isupper() and len(first_word) > 1 and first_word.lower() not in {"đúng","vâng","yes","có"}:
                    pass  # keep capitalization for names
                else:
                    cur_text = cur_text[0].lower() + cur_text[1:]
            merged = (new_text + " " + cur_text).strip()
            out[-1] = [prev_s, e, merged]
        else:
            out.append([s, e, t])
    return [tuple(b) for b in out]

output = merge_short_into_prev(output, max_short_syl=5, max_dur_after=14.0)
print(f"After merge-short: {len(output)} blocks")

# Also try merging short blocks into the next block (forward) — handles "Tại sao? <explanation>"
def merge_short_into_next(blocks, max_short_syl=4, max_dur_after=14.0):
    if not blocks: return blocks
    out = []
    i = 0
    while i < len(blocks):
        s, e, t = blocks[i]
        syl = vn_syl_count(t)
        merged_dur = (blocks[i+1][1] - s) if i+1 < len(blocks) else 0
        if syl <= max_short_syl and i+1 < len(blocks) and merged_dur <= max_dur_after:
            ns, ne, nt = blocks[i+1]
            # Combine: t + " " + nt (lowercase first letter of nt if not a proper noun)
            cur_text = t
            if re.search(r"[.!?]\s*$", cur_text):
                cur_text = re.sub(r"[.!?]+\s*$", ",", cur_text)
            next_text = nt
            if next_text and next_text[0].isupper():
                first_word = next_text.split()[0]
                if not (len(first_word) > 1 and first_word[0].isupper() and first_word.lower() not in {"đúng","vâng","yes","có","còn","hãy","trong","khi","để"}):
                    next_text = next_text[0].lower() + next_text[1:]
            merged_text = (cur_text + " " + next_text).strip()
            out.append((s, ne, merged_text))
            i += 2
        else:
            out.append((s, e, t))
            i += 1
    return out

output = merge_short_into_next(output)
print(f"After merge-next: {len(output)} blocks")

# Re-split anything that became too long
output = split_long(output, max_dur=14.0)
print(f"After re-split: {len(output)} blocks")

# Renumber & write
lines = []
for i, (s, e, t) in enumerate(output, start=1):
    lines.append(f"{i}\n{sec_to_ts(s)} --> {sec_to_ts(e)}\n{t}\n")

with open(OUT, "w", encoding="utf-8") as f:
    f.write("\n".join(lines))
print(f"OUT: {OUT}")
