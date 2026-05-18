---
description: "Pipeline dịch SRT EN → VN tối ưu cho CapCut TTS. Tự động đọc rule, dịch theo batch 5 phút, validate, gọi comparison-reviewer đối chiếu ngữ nghĩa, fix lỗi, xuất file."
argument-hint: "<đường dẫn file SRT EN> [--skip-review]"
allowed-tools: Read, Write, Edit, Bash, TaskCreate, TaskUpdate, TaskList, Agent
---

# /translate-srt — Pipeline dịch SRT EN → VN

Bạn đang chạy pipeline dịch SRT EN → VN cho project này. Người dùng vừa gọi lệnh với tham số:

**Tham số:** `$ARGUMENTS`

Nếu tham số rỗng hoặc không phải file `.srt` tồn tại, **dừng lại và yêu cầu người dùng cung cấp đường dẫn**. Không tự đoán file.

Nếu tham số kết thúc bằng `--skip-review`, bỏ qua Bước 7 (comparison-reviewer) — chỉ chạy validate.py.

---

## Bối cảnh bắt buộc đọc trước

Trước khi bắt đầu, đọc **đầy đủ** các file sau (đây là source of truth, không suy diễn):

1. `rule.md` — quy tắc dịch, các Cổng 1–9, công thức `tts_ratio` / `content_ratio`.
2. `speaker-profile.md` — baseline tốc độ speaker, ngưỡng đã hiệu chỉnh.
3. `validate.py` (header + hàm `main`) — biết exit code và format báo cáo.

Nếu bất kỳ file nào thiếu, dừng và báo người dùng.

---

## Quy trình 10 bước

Dùng `TaskCreate` ngay từ đầu để track 10 bước này. Cập nhật `in_progress`/`completed` từng bước. **Không** nhảy bước.

### Bước 1 — Xác định input/output

- Input: file EN tại đường dẫn người dùng cung cấp.
- Series name: rút từ đường dẫn (`srt/game-theory/...` → `game-theory`; `srt/secrest-history/...` → `secrest-history`).
- Tên file gốc: bỏ tiền tố `[English]` hoặc `[English (auto-generated)]`, bỏ hậu tố `[DownSub.com]` và các hậu tố tải xuống tương tự.
- Output path: `srt-output/<series-name>/[Vietnamese] <tên gốc đã làm sạch>.srt`.
- Tạo thư mục output nếu chưa có (`mkdir -p`).
- Nếu output đã tồn tại, hỏi người dùng: ghi đè hay đổi tên? Không tự ghi đè.

### Bước 2 — Đọc EN và chia batch 5 phút

- Đọc nguyên file EN.
- Chia thành các batch ~5 phút theo timestamp (mỗi batch kết thúc ở ranh giới câu/dấu chấm gần nhất sau mốc 5 phút).
- Ghi nhớ số block EN mỗi batch, timestamp đầu/cuối batch.

### Bước 3 — Lập glossary sơ bộ

Quét nhanh toàn file EN. Liệt kê 5–15 thuật ngữ quan trọng xuất hiện ≥ 3 lần:
- Tên người, chức danh, tổ chức, địa danh.
- Tên chiến dịch quân sự, chỉ số (index), khái niệm chuyên ngành.
- Idiom lặp lại.

Cố định **một** cách dịch cho mỗi mục. Lưu glossary này vào `srt-output/<series-name>/.glossary-<tên file>.md` để dùng xuyên suốt và soát lại ở Bước 8.

### Bước 4 — Dịch từng batch

Cho mỗi batch:

1. Đọc kỹ EN trong batch để hiểu cụm ý hoàn chỉnh.
2. Xóa noise dạng `[laughter]`, `[clears throat]`, block rỗng.
3. Gộp/tách block EN theo cụm ý — **tuyệt đối không gộp qua dấu chấm/hỏi/than** (Luật cứng số 1 của `rule.md`).
4. Dịch sang VN một dòng, câu hoàn chỉnh, dùng glossary đã lập.
5. Tính nhanh `tts_ratio` và `content_ratio` từng block — fix tại chỗ block có `tts_ratio > 95%` (tách/rút gọn) hoặc `content_ratio < 0.7` (dịch lại đầy đủ).
6. Ghi batch ra file output (append). Đánh số block tạm thời theo batch — sẽ đánh lại liên tục ở Bước 9.

**Không** chuyển sang batch tiếp theo nếu batch hiện tại còn block HARD fail rõ ràng (`tts > 95%`, `content < 0.7`, block > 18s, gap > 3s không phải filler).

### Bước 5 — Đánh số lại liên tục từ 1

Sau khi tất cả batch xong, đánh lại số thứ tự block từ 1 liên tục.

### Bước 6 — Chạy validate.py

```bash
python3 validate.py "<output-path>" "<input-path>"
```

- Nếu exit code = 0 và không có HARD ở Cổng 3, 8, 9: chuyển sang Bước 7.
- Nếu có lỗi HARD: đọc kỹ từng dòng báo cáo, fix theo hướng dẫn ở `rule.md` Mục 3.5. **Không** ghi đè giá trị thresholds trong validate.py để "qua test" — đó là cấm tuyệt đối.
- Fix xong chạy lại. Lặp tối đa 5 lần. Nếu sau 5 lần vẫn fail, dừng và báo người dùng kèm tóm tắt lỗi còn lại.

### Bước 7 — Đối chiếu ngữ nghĩa bằng comparison-reviewer

Bỏ qua bước này nếu người dùng truyền `--skip-review`.

Gọi agent `comparison-reviewer` qua tool `Agent`:

- **subagent_type:** `comparison-reviewer`
- **description:** `Đối chiếu ngữ nghĩa VN ↔ EN`
- **prompt:** Cung cấp đầy đủ:
  - Đường dẫn EN gốc và VN output.
  - Yêu cầu kiểm tra: (a) đảo nghĩa / nhầm phủ định; (b) sai chủ thể, sai số liệu, sai năm, sai tên riêng; (c) idiom dịch chữ thay vì dịch nghĩa; (d) tên chiến dịch / chỉ số bị văn vẻ hóa; (e) đoạn nhạy cảm chính trị/tôn giáo có thêm sắc thái không có trong EN; (f) tính nhất quán glossary.
  - Format trả về: bảng `block_number | EN_excerpt | VN_excerpt | severity (Critical/Moderate/Minor) | issue | recommended_fix`.
  - Yêu cầu chỉ liệt kê block có vấn đề thật, không liệt kê block đạt.

Nhận báo cáo từ agent. Áp dụng các fix **Critical** ngay (sửa file VN). Với **Moderate**: sửa nếu chắc chắn cải thiện, bỏ qua nếu đó là lựa chọn dịch hợp lý khác. Với **Minor**: ghi nhận, không sửa hàng loạt.

Sau khi sửa: chạy lại `validate.py` lần nữa để chắc các sửa đổi không phá tỷ lệ.

### Bước 8 — Soát Cổng 7 (chất lượng dịch)

Soát thủ công các điểm sau (xem `rule.md` Cổng 7):

- Glossary nhất quán xuyên file.
- Không có idiom / index bị dịch nghĩa đen.
- Tên chiến dịch không bị thêm tính từ văn vẻ.
- Không có 3 block liên tiếp cùng kết bằng "các bạn ạ" / "nhé".
- Đoạn nhạy cảm bám sát EN.
- Không có block đọc lên thấy gượng.

Fix tại chỗ nếu phát hiện.

### Bước 9 — Validate lần cuối

Chạy `python3 validate.py "<output-path>" "<input-path>"` lần cuối. **Chỉ chấp nhận file khi exit code = 0** và không còn HARD ở Cổng 3, 8, 9.

### Bước 10 — Báo cáo cho người dùng

Trả về ngắn gọn:

- Đường dẫn file output.
- Số block VN, tổng thời lượng.
- Tóm tắt validate.py cuối cùng (số block đạt / WARN / lỗi).
- Số fix Critical đã áp dụng từ comparison-reviewer (nếu chạy Bước 7).
- Đường dẫn glossary nếu đã tạo.

**Không** dán toàn bộ nội dung SRT vào câu trả lời — file đã được ghi ra đĩa.

---

## Quy tắc bất khả xâm phạm

1. **Không sửa `validate.py` hay `rule.md` hay `speaker-profile.md`** để file qua test. Đây là source of truth.
2. **Không** xuất file khi `validate.py` exit code ≠ 0 hoặc còn HARD ở Cổng 1, 3, 8, 9.
3. **Không** bỏ Bước 7 trừ khi người dùng truyền `--skip-review`.
4. **Không** lấp `content_ratio` bằng filler ("các bạn ạ", "vâng", "đúng vậy", "thật sự", "rõ ràng là"). Nếu thấp, viết lại đầy đủ ý EN. Nếu thấp mà EN window đúng là chỗ nói chậm/filler-only — để nguyên.
5. **Không** gộp block qua dấu `.`, `?`, `!`. Vi phạm Cổng 1 là no-go tuyệt đối.
6. Trước khi ghi đè file output đã tồn tại, hỏi người dùng.

---

## Khi gặp sự cố

- File EN không đọc được / parse fail: dừng, báo người dùng kèm dòng lỗi.
- `validate.py` không chạy được (thiếu Python, lỗi import): dừng, báo người dùng.
- `comparison-reviewer` agent không tồn tại hoặc lỗi: tiếp tục nhưng cảnh báo trong báo cáo Bước 10 rằng đã skip semantic review.
- Sau 5 vòng fix vẫn còn HARD: dừng, ghi lại tóm tắt 5 lỗi đầu trong báo cáo, hỏi người dùng có muốn ghi file dạng nháp `*.draft.srt` không.
