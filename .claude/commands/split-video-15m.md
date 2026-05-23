---
description: "Cắt 1 video thành đúng 3 phần theo ranh giới block SRT tiếng Việt tương ứng. Đặt tên _p1, _p2, _p3. Stream copy, không re-encode. Windows/PowerShell."
argument-hint: "<tên file hoặc đường dẫn video trong videos/> [<đường dẫn SRT VN>]"
allowed-tools: Read, Shell
---

# /split-video-15m — Cắt video thành 3 phần theo SRT tiếng Việt

Người dùng vừa gọi lệnh với tham số:

**Tham số:** `$ARGUMENTS`

## Quy tắc

1. Input video: 1 file trong thư mục `videos/`. Tham số có thể là:
   - Chỉ tên file (vd. `myvideo.mp4`) → resolve thành `videos/myvideo.mp4`.
   - Đường dẫn tương đối (`videos/sub/abc.mp4`) → dùng nguyên.
   - Đường dẫn tuyệt đối → dùng nguyên.
2. Input SRT VN (bắt buộc để xác định điểm cắt):
   - Tham số thứ 2 (nếu có): đường dẫn file `[Vietnamese] ... .srt`.
   - Nếu không có tham số thứ 2: tự tìm trong `srt-output/**/[Vietnamese]*.srt` khớp tên video (so khớp tên gốc, bỏ tiền tố `[Vietnamese]`, bỏ hậu tố `[DownSub.com]`, không phân biệt hoa thường/khoảng trắng thừa).
   - Nếu tìm thấy **0** hoặc **> 1** file khớp → **dừng**, yêu cầu người dùng chỉ rõ đường dẫn SRT VN. Không đoán.
3. Nếu tham số video rỗng hoặc file không tồn tại → **dừng**, yêu cầu người dùng cung cấp lại. Không tự đoán file.
4. Output: `videos-cut/<basename>_p1.<ext>`, `_p2.<ext>`, `_p3.<ext>`. Tạo thư mục `videos-cut/` nếu chưa có.
5. Nếu **bất kỳ** file `<basename>_pN.<ext>` (N = 1..3) đã tồn tại → hỏi người dùng ghi đè hay đổi tên. **Không** tự ghi đè.
6. **Luôn cắt đúng 3 phần** theo nội dung SRT VN — **không** cắt theo mốc thời gian cố định (15 phút, 20 phút, v.v.).

## Quy trình

Chạy toàn bộ lệnh shell trên **Windows PowerShell** (môi trường mặc định của user).

### Bước 0 — Thiết lập PowerShell an toàn

Trước khi chạy các bước bên dưới, luôn dùng các thiết lập này trong cùng shell:

```powershell
$ErrorActionPreference = "Stop"
$env:PYTHONIOENCODING = "utf-8"
$env:Path = [System.Environment]::GetEnvironmentVariable("Path","Machine") + ";" + [System.Environment]::GetEnvironmentVariable("Path","User")
$root = (Get-Location).Path
```

Quy tắc PowerShell bắt buộc:

- Với đường dẫn có ký tự `[` hoặc `]` như `[Vietnamese] ... .srt`, mọi kiểm tra file phải dùng `-LiteralPath`.
- Không dùng biến tên `$args` trong function PowerShell vì đây là biến đặc biệt, dễ làm ffmpeg nhận sai tham số.
- Khi gọi ffmpeg/ffprobe với đường dẫn Unicode hoặc có khoảng trắng, truyền tham số bằng mảng và splatting: `& ffmpeg @ffArgs`.
- Không dùng `-y` trừ khi người dùng đã đồng ý ghi đè.

### Bước 1 — Kiểm tra ffmpeg/ffprobe

```powershell
$tools = Get-Command ffmpeg, ffprobe -ErrorAction SilentlyContinue
$tools | Select-Object -ExpandProperty Source
```

Nếu thiếu → dừng, báo người dùng cài bằng một trong các cách:

- `winget install Gyan.FFmpeg`
- Hoặc tải bản build Windows tại https://www.gyan.dev/ffmpeg/builds/ rồi thêm thư mục `bin` vào `PATH`.

Sau khi người dùng cài xong, refresh PATH trong shell bằng dòng ở Bước 0 rồi kiểm tra lại. Không tiếp tục khi vẫn thiếu ffmpeg/ffprobe.

### Bước 2 — Resolve SRT VN và parse block

Đọc file SRT VN, parse toàn bộ block (index, start, end, text). Tái sử dụng `parse_srt()` trong `validate.py` — chạy từ thư mục gốc project.

Đầu tiên xác định Python thật, tránh Microsoft Store alias `python` giả:

```powershell
function Test-PythonExe([string]$cmd) {
  if (-not $cmd) { return $false }
  try {
    $v = & $cmd --version 2>&1
    return ($LASTEXITCODE -eq 0 -and "$v" -match "Python 3\.")
  } catch {
    return $false
  }
}

$pythonCandidates = @(
  (Get-Command python -ErrorAction SilentlyContinue | Select-Object -ExpandProperty Source -ErrorAction SilentlyContinue),
  (Get-Command py -ErrorAction SilentlyContinue | Select-Object -ExpandProperty Source -ErrorAction SilentlyContinue),
  "$env:LOCALAPPDATA\Programs\Python\Python312\python.exe"
) | Where-Object { $_ -and (Test-PythonExe $_) }

if (-not $pythonCandidates) {
  throw "Không tìm thấy Python. Cài Python 3.12 rồi chạy lại."
}

$python = $pythonCandidates[0]
```

Nếu có tham số SRT thứ 2, resolve bằng `Get-Item -LiteralPath`. Nếu không có, tự tìm trong `srt-output/**/[Vietnamese]*.srt` theo rule ở trên. Nếu tên video đã dịch sang tiếng Việt nhưng SRT giữ tên tiếng Anh, kết quả khớp có thể là 0; khi đó dừng và yêu cầu người dùng chỉ rõ SRT, không tự chọn theo số tập.

```powershell
$vnSrt = (Get-Item -LiteralPath "<đường_dẫn_SRT_VN>").FullName

$splitScript = Join-Path $env:TEMP "split-video-srt-boundary.py"
@'
import json, sys
from pathlib import Path

root = Path(sys.argv[1])
vn_srt = Path(sys.argv[2])
sys.path.insert(0, str(root))
from validate import parse_srt

blocks = parse_srt(str(vn_srt))
n = len(blocks)
if n < 3:
    raise SystemExit(f'Can it 3 phan: SRT chi co {n} block (can >= 3)')
s1 = n // 3          # block cuoi phan 1 (1-based: s1)
s2 = (2 * n) // 3    # block cuoi phan 2 (1-based: s2)
out = {
    'total_blocks': n,
    'part1_end_sec': blocks[s1 - 1].end,
    'part2_start_sec': blocks[s1].start,
    'part2_end_sec': blocks[s2 - 1].end,
    'part3_start_sec': blocks[s2].start,
    'split_after_block_1': s1,
    'split_after_block_2': s2,
}
print(json.dumps(out))
'@ | Set-Content -LiteralPath $splitScript -Encoding utf8

$json = & $python $splitScript $root $vnSrt
if ($LASTEXITCODE -ne 0) { throw "Parse SRT thất bại" }
$split = $json | ConvertFrom-Json
```

Lưu JSON output. Các biến:

| Biến | Ý nghĩa |
|---|---|
| `part1_end_sec` | Thời điểm kết thúc phần 1 = `end` của block thứ `s1` |
| `part2_start_sec` | Thời điểm bắt đầu phần 2 = `start` của block `s1 + 1` |
| `part2_end_sec` | Thời điểm kết thúc phần 2 = `end` của block thứ `s2` |
| `part3_start_sec` | Thời điểm bắt đầu phần 3 = `start` của block `s2 + 1` |

**Nguyên tắc chia 3 phần theo nội dung:**

- Tổng `N` block SRT VN → chia gần bằng nhau:
  - Phần 1: block `1` … `N//3`
  - Phần 2: block `N//3 + 1` … `(2*N)//3`
  - Phần 3: block `(2*N)//3 + 1` … `N`
- Điểm cắt **luôn nằm giữa hai block** (ranh giới câu TTS), không cắt giữa block.

Ghi log cho người dùng: tổng block, số block mỗi phần, timestamp cắt dạng `HH:MM:SS,mmm`.

### Bước 3 — Đo độ dài listing video gốc

```powershell
$inputVideo = (Get-Item -LiteralPath "<input>").FullName
$probeArgs = @(
  "-v", "error",
  "-show_entries", "format=duration",
  "-of", "default=noprint_wrappers=1:nokey=1",
  "-i", $inputVideo
)
$duration = [double]((& ffprobe @probeArgs).Trim())
```

Đọc `duration` (giây, float). Dùng làm `-to` cho phần 3 nếu cần.

### Bước 4 — Cắt 3 phần bằng ffmpeg (stream copy)

Chuyển giây sang định dạng `HH:MM:SS.mmm` cho ffmpeg. Với mỗi phần dùng `-c copy -avoid_negative_ts make_zero`:

**Phần 1** — từ đầu video đến hết block cuối phần 1:

```powershell
$ffArgs = @(
  "-hide_banner", "-loglevel", "warning", "-stats",
  "-i", $inputVideo,
  "-ss", "0", "-to", "<part1_end_sec>",
  "-c", "copy", "-map", "0", "-avoid_negative_ts", "make_zero",
  "<output_p1>"
)
& ffmpeg @ffArgs
```

**Phần 2** — từ block đầu phần 2 đến hết block cuối phần 2:

```powershell
$ffArgs = @(
  "-hide_banner", "-loglevel", "warning", "-stats",
  "-i", $inputVideo,
  "-ss", "<part2_start_sec>", "-to", "<part2_end_sec>",
  "-c", "copy", "-map", "0", "-avoid_negative_ts", "make_zero",
  "<output_p2>"
)
& ffmpeg @ffArgs
```

**Phần 3** — từ block đầu phần 3 đến hết video:

```powershell
$ffArgs = @(
  "-hide_banner", "-loglevel", "warning", "-stats",
  "-i", $inputVideo,
  "-ss", "<part3_start_sec>",
  "-c", "copy", "-map", "0", "-avoid_negative_ts", "make_zero",
  "<output_p3>"
)
& ffmpeg @ffArgs
```

Nếu bọc lệnh cắt trong function, dùng tên tham số như `$ffArgsList`, không dùng `$args`:

```powershell
function Invoke-Cut([string[]]$ffArgsList, [string]$outFile) {
  & ffmpeg @ffArgsList
  if ($LASTEXITCODE -ne 0) { throw "ffmpeg failed for $outFile" }
}
```

Lưu ý về `-c copy`: ffmpeg cắt tại keyframe gần nhất, mỗi part có thể lệch vài giây so với timestamp SRT. Đây là đánh đổi để cắt nhanh, không re-encode — đã thống nhất với người dùng. **Không** re-encode để bám pixel-perfect timestamp SRT trừ khi người dùng yêu cầu riêng.

### Bước 5 — Verify từng part

Với mỗi file `_p1`, `_p2`, `_p3`:

```powershell
$probeArgs = @(
  "-v", "error",
  "-show_entries", "format=duration",
  "-of", "default=noprint_wrappers=1:nokey=1",
  "-i", "<file>"
)
[double]((& ffprobe @probeArgs).Trim())
```

- Cả 3 part phải tồn tại và `duration > 0`.
- Tổng duration 3 part phải xấp xỉ duration gốc (chênh < 5 giây do keyframe). Nếu lệch lớn → cảnh báo trong báo cáo, không tự xoá file.
- Phần 1 nên kết thúc gần `part1_end_sec` (± 5s). Phần 2/3 tương tự.

### Bước 6 — Báo cáo ngắn

Trả về cho người dùng dạng bảng:

```
SRT VN: <path>  (N blocks)
Split:  sau block s1=<N//3>, s2=<(2*N)//3>

Input:  <path>  (duration: HH:MM:SS, size: X MB)
Output: videos-cut/
  - <basename>_p1.<ext>  HH:MM:SS  X MB  (block 1..s1)
  - <basename>_p2.<ext>  HH:MM:SS  X MB  (block s1+1..s2)
  - <basename>_p3.<ext>  HH:MM:SS  X MB  (block s2+1..N)
Total parts: 3
```

Không in log ffmpeg trừ khi có lỗi.

## Quy tắc bất khả xâm phạm

1. **Không re-encode.** Luôn dùng `-c copy`.
2. **Không** xoá / ghi đè file input gốc trong `videos/`.
3. **Không** cắt theo mốc thời gian cố định — điểm cắt **bắt buộc** lấy từ file SRT VN tương ứng.
4. **Luôn** tạo đúng **3** part. Không tạo 2 part, 4 part, hoặc số part theo duration.
5. **Không** đoán file nếu tham số rỗng / sai / SRT không xác định được.
6. **Không** cắt giữa block SRT — chỉ cắt tại ranh giới block.

## Khi gặp sự cố

- ffmpeg/ffprobe không tồn tại → dừng, yêu cầu cài đặt (xem Bước 1).
- Python không tồn tại hoặc `python` mở Microsoft Store alias → tìm `py` / `%LOCALAPPDATA%\Programs\Python\Python312\python.exe`; nếu vẫn không có thì dừng, yêu cầu cài Python.
- File video hoặc SRT VN không tồn tại / không đọc được → dừng, in lỗi.
- SRT có tên `[Vietnamese] ...` → luôn dùng `-LiteralPath`; không dùng `Test-Path $vnSrt` thường vì PowerShell sẽ coi `[` `]` là wildcard.
- Console in tiếng Việt lỗi encoding → đặt `$env:PYTHONIOENCODING = "utf-8"` và không in nội dung SRT ra stdout, chỉ in JSON ASCII.
- SRT VN có < 3 block → dừng, báo không thể chia 3 phần có nghĩa.
- Không tìm được SRT VN khớp (0 hoặc > 1 kết quả) → dừng, yêu cầu người dùng truyền đường dẫn SRT rõ ràng.
- ffmpeg báo `Error opening input file -ss` → kiểm tra lại cách truyền tham số; lỗi này thường do function dùng biến `$args` hoặc splatting sai.
- ffmpeg exit code ≠ 0 → in 20 dòng log cuối, dừng, **xoá toàn bộ file `_pN.*` vừa tạo trong lần chạy này** để tránh để lại trạng thái nửa vời.
- Output đã tồn tại trước khi chạy → hỏi người dùng trước, không tự ghi đè.
