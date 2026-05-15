# Speaker Profile — Game Theory & Secret History

File này ghi nhận tốc độ nói thật của speaker (cùng một người trên cả hai series Game Theory và Secret History) và các ngưỡng đã được hiệu chỉnh từ dữ liệu thật. Dùng làm tham chiếu khi dịch và khi viết/sửa rule.

## 1. Tổng Quan Corpus

- 27 file SRT EN gốc (22 Game Theory + 5 Secret History).
- Tổng thời lượng: ~25 giờ.
- Tổng từ EN: 199,633.
- 33,455 block sau khi parse.

## 2. Tốc Độ Nói EN

| Chỉ số | Giá trị | Ghi chú |
|---|---|---|
| WPS trung bình (file-level) | **2.27 wps** | Rất ổn định: file thấp nhất 2.12, cao nhất 2.45 |
| WPS median (block-level) | **2.50 wps** | Loại bỏ ảnh hưởng auto-sub cắt vụn |
| p10 block | 1.02 wps | Block speaker chậm / có pause |
| p25 block | 1.75 wps | |
| p75 block | 3.24 wps | |
| p90 block | 4.17 wps | Block speaker bùng phát ý nhanh |

**Phân bố block (% block trong dải wps):**

| WPS | % block |
|---|---|
| < 1.0 | 9.5% |
| 1.0 – 1.5 | 8.7% |
| 1.5 – 2.0 | 14.5% |
| 2.0 – 2.5 | 18.3% |
| 2.5 – 3.0 | 16.2% |
| 3.0 – 3.5 | 12.7% |
| > 3.5 | 20.1% |

→ ~18% block dưới 1.5 wps (speaker pause / auto-sub vụn) — block đơn lẻ không nên dùng làm baseline. Dùng file-level hoặc batch 5-phút.

## 3. Baseline Dùng Cho Quy Tắc Dịch

```
EN_baseline      = 2.4 wps              (file-level, dùng cho mọi tính toán density)
VN_per_EN_ratio  = 1.1 syllables/word   (số âm tiết VN ≈ 1.1 × số từ EN tự nhiên)
TTS_VN_rate      = 4.5 syllables/sec    (giả định CapCut TTS giọng VN mặc định, tốc độ 1.0x)
```

Suy ra mật độ VN tự nhiên: **2.4 × 1.1 = 2.65 âm tiết/giây**.
Tỷ lệ TTS tự nhiên: **2.65 / 4.5 ≈ 59%**.

→ **Mức "tự nhiên" cho speaker này là ~55-70% TTS, không phải 85-98%.** Đây là phát hiện then chốt — rule cũ ép 85-98% sẽ buộc agent thêm nội dung không có trong bản gốc.

## 4. Ngưỡng Đã Hiệu Chỉnh

### 4.1 Block-level

| Metric | Hard floor | Hard ceiling | Target sweet spot |
|---|---|---|---|
| `tts_ratio = VN_âm_tiết / 4.5 / duration` | (không có) | **95%** | 50 – 80% |
| `content_ratio = VN_âm_tiết / EN_từ_trong_window` | **0.7** (filler-only window có thể thấp hơn) | 1.5 (cảnh báo, có thể đang bịa) | **0.9 – 1.3** |
| Độ dài block | 2s | **16s** (lỗi tuyệt đối ở 18s) | 4 – 10s |
| Gap với block kế tiếp | (không có) | **3s** (trừ filler-only window) | < 1s |

### 4.2 File-level

| Metric | Yêu cầu |
|---|---|
| Tỷ lệ block đạt cả hai ngưỡng (`tts ≤ 95%` AND `content ≥ 0.9`) | **≥ 90%** |
| Median VN density toàn file | 2.4 – 3.0 syl/s |
| `Σ VN_âm_tiết / Σ EN_từ` toàn file | 0.95 – 1.30 |
| Sai lệch timestamp kết block VN cuối vs EN cuối | ≤ 15s |

## 5. Quy Tắc Vàng

- **Không ép tts_ratio đạt 85-98%.** Speaker này chậm; ép = bịa.
- **Đo content_ratio với EN window time-overlap.** Đây là cách duy nhất phát hiện rút gọn thật.
- **Xóa filler thì đóng gap.** Khi loại `okay`, `alright`, `you know`, `um`, `right`, `so` — phải kéo dài end của block trước hoặc start của block sau để không tạo gap > 3s.
- **Block-level WPS không tin được cho block ngắn.** Auto-sub cắt vụn → block-level WPS sai. Tin file-level và batch 5-phút.

## 6. Khi Nào Cần Re-Calibrate

Nếu dịch series khác (speaker khác), phải đo lại bằng `validate.py --calibrate <thư mục SRT EN>` trước khi áp ngưỡng. Cụ thể cần đo lại:
- WPS trung bình file-level
- Quyết định baseline mới
- Suy ra ngưỡng tts_ratio sweet-spot mới

Các ngưỡng trên file này CHỈ áp dụng cho hai series Game Theory + Secret History (đo từ 27 file gốc).
