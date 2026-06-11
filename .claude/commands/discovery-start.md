---
description: "Tự động dịch tuần tự tất cả file SRT EN chưa dịch trong một thư mục. Quét srt/<dir>/ vs srt-output/<dir>/, hiển thị checklist, spawn subagent dịch từng file. Hỗ trợ resume tự động nếu session bị gián đoạn."
argument-hint: "<tên thư mục series> [--skip-review]"
allowed-tools: Read, Write, Edit, Bash, TaskCreate, TaskUpdate, TaskList, Agent
---

# /discovery-start — Dịch hàng loạt SRT theo thư mục (có resume)

Người dùng vừa gọi lệnh với tham số: **`$ARGUMENTS`**

Nếu tham số rỗng, **dừng lại và yêu cầu** người dùng cung cấp tên thư mục (ví dụ: `Civilization`, `game-theory`, `secret-history`).

Nếu tham số kết thúc bằng `--skip-review`, truyền `--skip-review` vào từng lần dịch (bỏ qua comparison-reviewer).

---

## Bước 1 — Xác định thư mục và quét file

Tách tham số: tên thư mục là phần đầu (trước `--skip-review` nếu có).

Chạy lệnh sau để liệt kê tất cả file SRT EN trong thư mục input:

```bash
ls "srt/<tên thư mục>/"
```

Nếu thư mục không tồn tại hoặc không có file `.srt`, **dừng và báo người dùng**.

---

## Bước 2 — Đọc progress file (resume logic)

Progress file lưu tại: `.discovery-progress/<dir>.json`

**Đọc file này nếu tồn tại:**

```bash
cat ".discovery-progress/<dir>.json" 2>/dev/null
```

File có dạng:
```json
{
  "dir": "<dir>",
  "updated": "<ISO timestamp>",
  "files": {
    "<tên file EN 1>": "completed",
    "<tên file EN 2>": "in_progress",
    "<tên file EN 3>": "pending",
    "<tên file EN 4>": "failed"
  }
}
```

**Xử lý từng trạng thái khi resume:**

| Trạng thái | Hành động |
|---|---|
| `completed` | Bỏ qua — output đã tồn tại |
| `in_progress` | **Xóa output dở** (nếu có), đặt lại thành `pending`, dịch lại từ đầu file đó |
| `pending` | Tiếp tục bình thường |
| `failed` | Thử lại — đặt lại thành `pending` |

**Nếu progress file chưa tồn tại:** tạo mới với tất cả file là `pending`.

**Tạo thư mục nếu chưa có:**
```bash
mkdir -p ".discovery-progress"
```

**Ghi progress file** (dùng Write tool với JSON đầy đủ mỗi khi có thay đổi trạng thái).

---

## Bước 3 — Xác định file chưa dịch

Với mỗi file EN trong `srt/<dir>/`, tính đường dẫn output tương ứng:
- Bỏ tiền tố `[English (auto-generated)] ` hoặc `[English] `
- Bỏ hậu tố ` [DownSub.com]` (và các hậu tố tương tự như `[DownSub]`, `[SubtitleCat]`, v.v.)
- Thêm tiền tố `[Vietnamese] `
- Output path: `srt-output/<dir>/[Vietnamese] <tên đã làm sạch>.srt`

Kiểm tra output thực tế trên disk:
```bash
ls "srt-output/<dir>/" 2>/dev/null
```

**Ưu tiên progress file**, nhưng cross-check với disk:
- Nếu progress = `completed` nhưng output không tồn tại → đặt lại `pending` (output bị xóa ngoài)
- Nếu progress = `pending` nhưng output đã tồn tại → đặt lại `completed` (đã dịch ngoài luồng)

Danh sách cần dịch = tất cả file có trạng thái `pending` sau khi cross-check.

---

## Bước 4 — Hiển thị checklist cho người dùng

Trước khi bắt đầu dịch, in ra:

```
📋 Thư mục: srt/<dir>/
✅ Đã dịch: X file
🔄 Resume (in_progress → restart): R file  ← chỉ hiện nếu R > 0
⏳ Cần dịch: Y file

Danh sách cần dịch:
  [ ] 1. <tên file 1>
  [ ] 2. <tên file 2>
  ...

Progress file: .discovery-progress/<dir>.json
Bắt đầu dịch tuần tự...
```

Dùng `TaskCreate` để tạo task cho từng file cần dịch (title = tên file, status = pending).

Nếu **không có file nào cần dịch**, báo người dùng và dừng.

---

## Bước 5 — Dịch tuần tự từng file

Với từng file trong danh sách (theo thứ tự, **không song song**):

1. **Cập nhật progress file** → trạng thái file = `in_progress`, ghi timestamp `updated`.
2. Cập nhật task tương ứng thành `in_progress`.
3. Thông báo ngắn: `▶ Đang dịch: <tên file> (<i>/<tổng>)`
4. Spawn **1 subagent** bằng `Agent` tool với:
   - `description`: `Dịch SRT: <tên file>`
   - `prompt`: Toàn bộ nội dung bên dưới (thay thế các placeholder thực tế)

---

### Prompt mẫu cho subagent

```
Bạn đang chạy pipeline dịch SRT EN → VN cho project này.

Working directory: /home/edu_admin/projects/Khiemdt/{{PROJECT-CODE}}-ADLC 1/video-srt-promt

File cần dịch:
- Input EN: srt/<dir>/<tên file EN>
- Output VN: srt-output/<dir>/[Vietnamese] <tên file đã làm sạch>.srt
<nếu --skip-review: thêm dòng "- Flag: --skip-review (bỏ qua comparison-reviewer)">

Đọc đầy đủ 2 file context sau trước khi bắt đầu:
1. rule.md — quy tắc dịch, Cổng 1–9, công thức tts_ratio / content_ratio
2. speaker-profile.md — baseline tốc độ speaker, ngưỡng đã hiệu chỉnh

Sau đó thực hiện đúng quy trình 10 bước sau:

### Bước 1 — Xác định input/output
- Input: file EN tại đường dẫn đã cho.
- Series name: <dir>
- Output path: srt-output/<dir>/[Vietnamese] <tên đã làm sạch>.srt
- Tạo thư mục output nếu chưa có (mkdir -p).
- Nếu output đã tồn tại (resume sau gián đoạn), xóa file cũ và dịch lại từ đầu.

### Bước 2 — Đọc EN và chia batch 5 phút
- Đọc nguyên file EN.
- Chia thành các batch ~5 phút theo timestamp (mỗi batch kết thúc ở ranh giới câu/dấu chấm gần nhất sau mốc 5 phút).

### Bước 3 — Lập glossary sơ bộ
Quét nhanh toàn file EN, liệt kê 5–15 thuật ngữ quan trọng xuất hiện ≥ 3 lần (tên người, địa danh, tổ chức, khái niệm chuyên ngành, idiom lặp lại). Cố định một cách dịch cho mỗi mục. Lưu vào srt-output/<dir>/.glossary-<tên file>.md.

### Bước 4 — Dịch từng batch
Cho mỗi batch:
1. Hiểu cụm ý hoàn chỉnh trong EN.
2. Xóa noise: [laughter], [clears throat], block rỗng.
3. Gộp/tách block EN theo cụm ý — TUYỆT ĐỐI không gộp qua dấu chấm/hỏi/than (Luật cứng số 1).
4. Dịch sang VN một dòng, câu hoàn chỉnh, dùng glossary.
5. Tính tts_ratio và content_ratio từng block — fix tại chỗ block có tts_ratio > 95% hoặc content_ratio < 0.7.
6. Ghi batch ra file output (append).

### Bước 5 — Đánh số lại liên tục từ 1

### Bước 6 — Chạy validate.py
```bash
python3 validate.py "srt-output/<dir>/[Vietnamese] <tên>.srt" "srt/<dir>/<tên EN>.srt" --max-issues 15
```
Nếu có lỗi HARD: đọc toàn bộ danh sách, fix tất cả trong một lượt, chạy lại. Tối đa 3 lần.

### Bước 7 — Đối chiếu ngữ nghĩa (bỏ qua nếu --skip-review)
Gọi Agent comparison-reviewer với:
- subagent_type: comparison-reviewer
- Kiểm tra: (a) đảo nghĩa/phủ định; (b) sai chủ thể/số liệu/tên; (c) idiom dịch chữ; (d) tên chiến dịch/chỉ số bị văn vẻ hóa; (e) đoạn nhạy cảm thêm sắc thái; (f) nhất quán glossary; (g) liên từ logic sai; (h) causative sai chủ thể.
- Format: bảng block_number | EN_excerpt | VN_excerpt | severity | issue | recommended_fix
Áp dụng fix Critical ngay. Sau khi sửa: chạy lại validate.py.

### Bước 8 — Soát Cổng 7
- Glossary nhất quán xuyên file.
- Không idiom/index dịch nghĩa đen.
- Tên chiến dịch không thêm tính từ văn vẻ.
- Không 3 block liên tiếp cùng kết bằng "các bạn ạ"/"nhé".
- Đoạn nhạy cảm bám sát EN.

### Bước 9 — Validate lần cuối (chỉ khi --skip-review)

### Bước 10 — Báo cáo ngắn gọn
- Đường dẫn file output.
- Số block VN, tổng thời lượng.
- Tóm tắt validate.py cuối (đạt/WARN/lỗi).
- Số fix Critical từ comparison-reviewer (nếu chạy Bước 7).
- Đường dẫn glossary.

### Quy tắc bất khả xâm phạm
1. Không sửa validate.py hay rule.md hay speaker-profile.md để qua test.
2. Không xuất file khi validate.py exit code ≠ 0 hoặc còn HARD ở Cổng 1, 3, 8, 9.
3. Không bỏ Bước 7 trừ khi có --skip-review.
4. Không lấp content_ratio bằng filler.
5. Không gộp block qua dấu . ? !
6. KHÔNG hỏi ghi đè khi đây là resume — xóa output cũ và dịch lại.
```

---

5. **Chờ subagent hoàn thành** (đồng bộ — không chuyển sang file tiếp theo khi chưa xong).
6. Sau khi subagent xong:
   - Nếu thành công → **cập nhật progress file** = `completed`, cập nhật task = `completed`.
   - Nếu thất bại → **cập nhật progress file** = `failed`, cập nhật task = ghi nhận lỗi, tiếp tục file tiếp theo.
7. Chuyển sang file tiếp theo.

---

## Bước 6 — Báo cáo tổng kết

Sau khi dịch xong tất cả file, **cập nhật progress file lần cuối** rồi in tóm tắt:

```
✅ Hoàn thành batch dịch thư mục: srt/<dir>/

Kết quả:
  ✅ Dịch thành công: X file
  ❌ Thất bại / cần xem lại: Y file (liệt kê tên nếu có)

File output tại: srt-output/<dir>/
Progress file: .discovery-progress/<dir>.json
```

---

## Lưu ý quan trọng

- **Dịch tuần tự**, không song song — đảm bảo chất lượng và tránh conflict glossary.
- Nếu 1 file thất bại, **tiếp tục** với file tiếp theo, ghi nhận lỗi để báo cáo cuối.
- Không tự bỏ qua file nào trong checklist trừ khi progress = `completed` VÀ output tồn tại trên disk.
- **Ghi progress file ngay trước và ngay sau mỗi file** — đây là điểm mấu chốt để resume hoạt động đúng khi mất điện giữa chừng.
