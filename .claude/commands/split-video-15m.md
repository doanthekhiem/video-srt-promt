---
description: "Cắt 1 video thành nhiều phần tối đa 15 phút mỗi phần. Đặt tên _part01, _part02... Stream copy, không re-encode."
argument-hint: "<tên file hoặc đường dẫn video trong videos/>"
allowed-tools: Read, Bash
---

# /split-video-15m — Cắt video thành các phần ≤ 15 phút

Người dùng vừa gọi lệnh với tham số:

**Tham số:** `$ARGUMENTS`

## Quy tắc

1. Input: 1 video trong thư mục `videos/`. Tham số có thể là:
   - Chỉ tên file (vd. `myvideo.mp4`) → resolve thành `videos/myvideo.mp4`.
   - Đường dẫn tương đối (`videos/sub/abc.mp4`) → dùng nguyên.
   - Đường dẫn tuyệt đối → dùng nguyên.
2. Nếu tham số rỗng hoặc file không tồn tại → **dừng**, yêu cầu người dùng cung cấp lại. Không tự đoán file.
3. Output: `videos-cut/<basename>_part01.<ext>`, `_part02.<ext>`, ...
4. Nếu **bất kỳ** file `<basename>_partNN.<ext>` đã tồn tại → hỏi người dùng ghi đè hay đổi tên. **Không** tự ghi đè.

## Quy trình

### Bước 1 — Kiểm tra ffmpeg/ffprobe

```bash
command -v ffmpeg && command -v ffprobe
```

Nếu thiếu → dừng, báo người dùng cài bằng `sudo apt install ffmpeg`. Không tiếp tục.

### Bước 2 — Đo độ dài video

```bash
ffprobe -v error -show_entries format=duration -of default=noprint_wrappers=1:nokey=1 "<input>"
```

Đọc duration (giây, float).

### Bước 3 — Quyết định có cần cắt không

- **Nếu duration ≤ 900 giây (15 phút):** không cần cắt. Báo người dùng, **không** tạo file output. Kết thúc.
- **Nếu duration > 900 giây:** sang Bước 4. Tính số part dự kiến: `ceil(duration / 900)` để báo trước trong log.

### Bước 4 — Cắt thành các segment ≤ 15 phút

Dùng demuxer `segment` của ffmpeg. Pattern `%02d` cho 2 chữ số bắt đầu từ `00`:

```bash
ffmpeg -hide_banner -loglevel warning -stats \
  -i "<input>" \
  -c copy -map 0 \
  -f segment -segment_time 900 -reset_timestamps 1 \
  "videos-cut/<basename>_part_RAW_%02d.<ext>"
```

Lưu ý về `-c copy`: ffmpeg cắt tại keyframe gần nhất, mỗi part có thể ngắn/dài hơn 15 phút một vài giây tuỳ keyframe interval của source. Đây là đánh đổi để cắt nhanh, không re-encode — đã thống nhất với người dùng.

### Bước 5 — Đổi tên `_part_RAW_00` → `_part01` (1-based)

Segment muxer của ffmpeg index từ `00`, nhưng user muốn `_part01`. Sau khi ffmpeg xong, rename:

```bash
# Đọc list file _part_RAW_NN, sort theo NN, rename thành _partMM với MM = NN+1, 2 chữ số.
# Nếu số part ≥ 100, dùng 3 chữ số (_part001).
```

Implement bằng bash loop:

```bash
shopt -s nullglob
files=( "videos-cut/<basename>_part_RAW_"*.<ext> )
total=${#files[@]}
width=2
if [ "$total" -ge 100 ]; then width=3; fi
i=1
for f in "${files[@]}"; do
  new=$(printf "videos-cut/<basename>_part%0${width}d.<ext>" "$i")
  mv -- "$f" "$new"
  i=$((i+1))
done
```

### Bước 6 — Verify từng part

Với mỗi file `_partNN.<ext>` vừa tạo:

```bash
ffprobe -v error -show_entries format=duration -of default=noprint_wrappers=1:nokey=1 "<file>"
```

- Mỗi part phải tồn tại và `duration > 0`.
- Mỗi part nên ≤ 920 giây (cho phép lệch ~20s do keyframe). Part cuối thường ngắn hơn — OK.
- Tổng duration các part phải xấp xỉ duration gốc (chênh < 2 giây). Nếu lệch lớn → cảnh báo trong báo cáo, không tự xoá file.

### Bước 7 — Báo cáo ngắn

Trả về cho người dùng dạng bảng:

```
Input:  <path>  (duration: HH:MM:SS, size: X MB)
Output: videos-cut/
  - <basename>_part01.<ext>  HH:MM:SS  X MB
  - <basename>_part02.<ext>  HH:MM:SS  X MB
  - ...
Total parts: N
```

Không in log ffmpeg trừ khi có lỗi.

## Quy tắc bất khả xâm phạm

1. **Không re-encode.** Luôn dùng `-c copy`.
2. **Không** xoá / ghi đè file input gốc trong `videos/`.
3. **Không** tạo output khi video ≤ 15 phút — báo người dùng và dừng.
4. **Không** đoán file nếu tham số rỗng / sai.
5. **Không** để lại file `_part_RAW_*` sau khi hoàn tất — phải rename hết. Nếu rename fail, xoá output dở và báo lỗi.

## Khi gặp sự cố

- ffmpeg/ffprobe không tồn tại → dừng, yêu cầu cài đặt.
- File input không tồn tại / không đọc được → dừng, in lỗi.
- ffmpeg exit code ≠ 0 → in 20 dòng log cuối, dừng, **xoá toàn bộ file `_part_RAW_*` và `_partNN.*` vừa tạo** để tránh để lại trạng thái nửa vời.
- Output đã tồn tại trước khi chạy → hỏi người dùng trước, không tự ghi đè.
