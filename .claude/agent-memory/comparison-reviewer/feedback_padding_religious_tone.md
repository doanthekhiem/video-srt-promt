---
name: padding-religious-tone
description: Pattern bịa thêm sắc thái sùng đạo/phán xét trong file đoạn Cơ Đốc, content_ratio bất thường
metadata:
  type: feedback
---

Khi file content_ratio > 1.30 trong các đoạn nói về Jesus/Kinh Thánh, kiểm tra ngay các pattern bịa sau:

1. **Thêm tính từ phán xét/cảm xúc:** EN "the Romans" → VN "đế chế tà ác/quân La Mã tàn bạo"; EN "Christianity is aggressive" → VN "hung hăng nhất"; EN "the rich/powerful" → VN "kẻ giàu, kẻ quyền lực tà ác"
2. **Thay danh từ trừu tượng bằng từ tôn giáo:** EN "the Monad" → VN "Đấng Tối Cao"; EN "the divine" → VN "thần thánh/Thiên Chúa"
3. **Bịa cụm "thuần khiết/tuyệt đối":** EN "pure evil" OK với "thuần khiết" nhưng EN "the rich are bad" KHÔNG được thành "kẻ giàu là tà ác tuyệt đối"
4. **Thêm "muôn vua/Đức Chúa/Đấng":** EN "he's king" → VN "vua trên muôn vua" (thêm trang trọng); EN "our Lord, our Savior" được giữ "Đức Chúa, Đấng Cứu Thế" là OK, nhưng cần check EN có "Lord" không
5. **Bịa cụm cố định văn vẻ:** "tia lửa thiêng liêng chân thực", "trật tự tự nhiên" (EN: "natural order" OK), "luật bất thành văn" (EN có "unwritten law" OK)

**Why:** File #22 đạt content_ratio 1.39 (vượt ngưỡng 1.30), nguyên nhân chính là người dịch tự thêm sắc thái nhấn mạnh cho dễ nghe TTS, làm méo lập trường tác giả — vốn KHÔNG phải sùng đạo cũng KHÔNG phải bài Cơ Đốc, mà là phân tích lịch sử-triết học.

**How to apply:**
- Mọi đoạn Jesus/Bible/Roman/Church: sát từng tính từ, từng danh từ trừu tượng
- Đặc biệt soát các đoạn cảm thán "Okay?" "Right?" của EN — VN dễ biến chúng thành câu khẳng định/nhấn mạnh
- Liên kết: [[god-polytheist-context]], [[monad-mistranslation]], [[pronoun-fabrication]]

## ⚠️ CAVEAT QUAN TRỌNG — KHÔNG ÁP DỤNG BLANKET

Rule này chỉ áp dụng khi **VN có nhấn mạnh mà EN KHÔNG có**. KHÔNG được cắt blanket cả file.

**Kiểm tra 1-1 trước khi flag:**
- VN "thật sự quan trọng" — phải grep EN trong cùng timestamp xem có "really/very/truly/extremely" không. **Có → BẮT BUỘC GIỮ**.
- VN "rất X" — EN có "very/so/really X"? Có → giữ.
- VN "cực kỳ X" — EN có "extremely/incredibly X"? Có → giữ.
- VN "hoàn toàn X" — EN có "totally/completely/absolutely X"? Có → giữ.

**Bài học từ regression file #22 block 232 (review 2026-06):**
- EN "this is **really** important" → VN trước "thật sự quan trọng" (đúng) → agent cắt thành "điều này quan trọng" (sai, mất "really")
- Đây là **false positive** do agent áp dụng rule #1 quá rộng cho cả file.
- **Cách tránh:** Trước khi flag intensifier là padding, MUST grep EN trong cùng timestamp. Nếu không tìm được EN gốc → không flag.

**Quy tắc thay thế (preferred over blanket):**
- Tính ratio theo TỪNG ĐOẠN/scene, không phải cả file
- Chỉ flag intensifier khi EN không có từ nhấn mạnh tương ứng trong cùng cụm thời gian (±2s)
- Khi nghi ngờ → giữ nguyên, không cắt
