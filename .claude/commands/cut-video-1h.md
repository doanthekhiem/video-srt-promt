---
description: "Cắt video xuống 59m58s nếu dài hơn 1 giờ. Giữ phần đầu, bỏ phần đuôi. Stream copy, không re-encode."
argument-hint: "<tên file hoặc đường dẫn video trong videos/>"
allowed-tools: Read, Bash
---

# /cut-video-1h — Cắt video xuống dưới 1 giờ

Người dùng vừa gọi lệnh với tham số:

**Tham số:** `$ARGUMENTS`

## Quy tắc

1. Input: 1 video trong thư mục `videos/`. Tham số có thể là:
   - Chỉ tên file (vd. `myvideo.mp4`) → resolve thành `videos/myvideo.mp4`.
   - Đường dẫn tương đối (`videos/sub/abc.mp4`) → dùng nguyên.
   - Đường dẫn tuyệt đối → dùng nguyên.
2. Nếu tham số rỗng hoặc file không tồn tại → **dừng**, yêu cầu người dùng cung cấp lại. Không tự đoán file.
3. Output: `videos-cut/<tên-file-gốc>_cut.<ext>`. Tạo thư mục `videos-cut/` nếu chưa có.
4. Nếu output đã tồn tại → hỏi người dùng ghi đè hay đổi tên. **Không** tự ghi đè.

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

Đọc giá trị duration (giây, float).

### Bước 3 — Quyết định cắt hay không

- **Nếu duration ≤ 3600 giây (1 giờ):** không cần cắt. Báo người dùng video chỉ dài `X phút Y giây`, không thực hiện cắt, **không** tạo file output. Kết thúc.
- **Nếu duration > 3600 giây:** sang Bước 4.

### Bước 4 — Cắt video xuống 59m58s

Target duration cố định: **00:59:58** (3598 giây).

```bash
ffmpeg -hide_banner -loglevel warning -stats \
  -i "<input>" \
  -t 00:59:58 \
  -c copy -avoid_negative_ts make_zero \
  "videos-cut/<basename>_cut.<ext>"
```

Lưu ý về `-c copy`: ffmpeg cắt tại keyframe gần nhất ≤ 59:58, output thực tế có thể ngắn hơn 59:58 vài giây. Đây là đánh đổi để cắt nhanh, không re-encode, giữ nguyên chất lượng — đã thống nhất với người dùng.

### Bước 5 — Verify output

```bash
ffprobe -v error -show_entries format=duration -of default=noprint_wrappers=1:nokey=1 "videos-cut/<basename>_cut.<ext>"
```

- Phải tồn tại và duration nằm trong khoảng `[3580, 3598]` giây (cho phép lệch ~18s vì keyframe).
- Nếu duration > 3598s hoặc < 3580s → cảnh báo trong báo cáo, **không** tự xoá file.

### Bước 6 — Báo cáo ngắn

Trả về cho người dùng:

- Đường dẫn input + duration gốc (`HH:MM:SS`).
- Đường dẫn output + duration mới (`HH:MM:SS`).
- Kích thước file output (`du -h`).

Không in log ffmpeg trừ khi có lỗi.

## Quy tắc bất khả xâm phạm

1. **Không re-encode.** Luôn dùng `-c copy`.
2. **Không** xoá / ghi đè file input gốc trong `videos/`.
3. **Không** tạo output khi video ≤ 1 giờ — báo người dùng và dừng.
4. **Không** đoán file nếu tham số rỗng / sai.

## Khi gặp sự cố

- ffmpeg/ffprobe không tồn tại → dừng, yêu cầu cài đặt.
- File input không tồn tại / không đọc được → dừng, in lỗi.
- ffmpeg exit code ≠ 0 → in 20 dòng log cuối, dừng, **không** giữ file output dở dang (xoá nếu có).
