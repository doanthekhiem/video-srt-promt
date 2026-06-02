---
description: "Dịch SRT EN → DE. Dịch sát nghĩa, giữ nguyên timestamp, chia batch 5 phút để dịch, xuất file."
argument-hint: "<đường dẫn file SRT EN>"
allowed-tools: Read, Write, Bash
---

# /translate-srt-de — Dịch SRT EN → DE

**Tham số:** `$ARGUMENTS`

Nếu tham số rỗng hoặc file không tồn tại, dừng và yêu cầu người dùng cung cấp đường dẫn.

---

## Bước 1 — Xác định input/output

- Series name: rút từ đường dẫn (`srt/Civilization/...` → `Civilization`).
- Tên file output: bỏ tiền tố `[English]` / `[English (auto-generated)]`, bỏ hậu tố `[DownSub.com]` và tương tự, thêm tiền tố `[German]`.
- Output: `srt-output/<series-name>/[German] <tên sạch>.srt`.
- `mkdir -p` thư mục output nếu chưa có.
- Nếu output đã tồn tại, hỏi trước khi ghi đè.

## Bước 2 — Đọc file EN và chia batch ~5 phút

Đọc toàn bộ file. Chia thành các batch ~5 phút theo timestamp.

## Bước 3 — Dịch từng batch, append vào file output

Với mỗi batch, dịch từng block và **ghi ngay (append) vào file output** sau khi dịch xong batch đó — không giữ trong bộ nhớ rồi mới ghi.

Quy tắc dịch:
- Giữ nguyên số thứ tự block và timestamp — **không sửa**.
- Dịch sát nghĩa, tự nhiên tiếng Đức — không thêm, không bớt ý.
- Tên riêng, số liệu, năm tháng — giữ nguyên.
- Idiom → dịch nghĩa tương đương tiếng Đức, không dịch chữ.
- Block chỉ có `[laughter]`, `[music]`, `[applause]` và không có lời thoại → xóa block đó.
- **Không gộp, không tách block** — 1 block EN = 1 block DE.

## Bước 4 — Báo cáo

- Đường dẫn file output.
- Số block, timestamp cuối.

**Không** dán nội dung SRT vào câu trả lời.
