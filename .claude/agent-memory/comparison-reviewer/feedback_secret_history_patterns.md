---
name: secret-history-patterns
description: Pattern lỗi tái diễn khi đối chiếu bản dịch VN của series Secret History (đã auto-merge block)
metadata:
  type: feedback
---

Khi đối chiếu các bản dịch SRT thuộc series Secret History (giảng viên dạy lịch sử/triết/tôn giáo), cần ưu tiên scan các pattern lỗi sau:

**1. Typo "nuốt chữ" tại đường nối block đã merge**
- Pattern: `cuốiđiều`, `cuốicó`, `cuốiđến`, `cuốicũng` (mất chữ "cùng" và dấu cách)
- Cũng gặp: `như ?` (mất "vậy"), `là mà` (mất "cái"), `Vì ông rằng` (mất "nghĩ")
- **Why:** Auto-merge nhiều block ngắn nối lại làm rơi từ nối ở ranh giới.
- **How to apply:** Grep nhanh `cuối[đc]`, `cuối cũng`, ` ?$`, ` rằng` để bắt cluster lỗi này trước.

**2. Block "rỗng" chỉ chứa "?"**
- Sau khi merge filler "Does that make sense? Right?" có thể còn lại một block chỉ có dấu "?".
- **How to apply:** Tìm các block có nội dung ngắn dưới 3 ký tự để gộp hoặc xóa.

**3. Dấu "?" thừa cuối câu khẳng định**
- Pattern: VN dịch xong nhưng để dấu "?" cuối câu khẳng định EN — thường do EN có "right?" filler.
- **How to apply:** Khi câu EN kết thúc bằng "right?" mang nghĩa khẳng định/xác nhận, VN nên dùng dấu "." không phải "?".

**4. Đoạn nhạy cảm (Israel/Gaza, tôn giáo, hiến tế) — sắc thái leak**
- Pattern: VN có xu hướng thêm sắc thái phán xét ("trắng trợn", "khẩu hiệu") so với EN trung tính ("blatant", "shout").
- **Why:** Glossary file ghi rõ "phải bám sát EN, không thêm sắc thái" cho đoạn này.
- **How to apply:** Với Israel/Gaza/Jewish eschatology/hiến tế trẻ em/Sparta-pederasty — kiểm tra từng tính từ, trạng từ xem có cường điệu hơn EN không.

**5. Tên riêng sau khi auto-sub méo**
- "thieves" = Thebes; "Traonia" = Chaeronea; "Leonitis" = Leonidas; "Thermopily" = Thermopylae; "phoenetians/Infineticians" = Phoenicians; "constant genians" = Carthaginians; "Theian" = Theban.
- File .glossary-*.md là nguồn chuẩn — xem [[reference_glossary_authority]].
- **How to apply:** Trong khi đối chiếu, nếu thấy VN giữ nguyên tên auto-sub méo → flag Critical.

**6. Sun/son auto-sub confusion**
- Xem [[project_sun_son_nous]].

**7. Lỗi địa lý lịch sử do auto-sub mất conjunction**
- VD: "Macedonia destroyed thieves in Athens" thực ra là "Macedonia destroyed Thebes AND Athens" (liên quân Thebes-Athens) — auto-sub có thể nuốt "and" thành "in".
- **How to apply:** Khi VN dịch giới từ "ở/tại" cho địa danh — kiểm tra xem trận đánh đó có thực sự diễn ra tại địa danh đó không, hay đó là tên một bên tham chiến.

**8. Negation flip ở câu hỏi tu từ**
- EN: "Doesn't that make sense?" / "Doesn't it?" = câu khẳng định mềm xác nhận.
- VN dễ dịch nhầm thành phủ định: "không có nghĩa hay sao?", "chẳng có lý sao?" → đảo nghĩa.
- **How to apply:** Khi gặp "Doesn't [it/that]..." trong EN, VN nên dịch "Có hợp lý chứ?", "Đúng không?", "Không hợp lý sao?" tránh "không... hay sao".

**9. Missing content (câu/cụm bị bỏ trọn) ở đoạn lý thuyết then chốt**
- Trong file #5 "The Birth of Evil", VN bỏ sót:
  - "You will live forever" (EN khi mô tả Vườn Địa Đàng) — quan trọng vì sau đó cây sự sống chính là cây bất tử.
  - "In fact, Jesus is God himself. Because they believe in Jesus Christ." — cốt lõi giáo lý Cơ Đốc + tại sao gọi là Christianity.
  - "Satan is telling the truth. You will not die. You will learn." — kết luận của giảng viên sau khi đọc Genesis.
  - Danh sách cụ thể "Hercules / Achilles / Theseus" (anh hùng = Nephilim) và "Zeus / Ares / Apollo" (sons of God = các thần cũ).
- **Why:** Có thể do auto-merge block hoặc dịch giả tóm lược quá mạnh ở đoạn liệt kê.
- **How to apply:** Với bài giảng có cấu trúc "đọc Kinh Thánh xong → đưa ra kết luận then chốt" — sau câu trích Kinh Thánh trong VN, phải có câu kết luận diễn giải. Nếu thiếu → Critical. Với danh sách tên anh hùng / tên thần — đếm số tên trong EN và VN phải khớp.

**10. Nhầm lẫn hai nhóm "sons of God" và "Nephilim" trong Genesis 6**
- Genesis 6:2-4 phân biệt: (a) "sons of God" = thiên thần / các thần cũ (Zeus, Ares, Apollo theo cách giảng của thầy), (b) "Nephilim" = con của (a) với phụ nữ phàm trần = các anh hùng cổ đại (Hercules, Achilles, Theseus).
- VN trong file #5 đã gom 2 nhóm này thành một câu mơ hồ "Họ là anh hùng nổi tiếng trong nhiều thần thoại. Họ là kết quả giao phối giữa thiên thần và con người." — mất sự phân biệt.
- **How to apply:** Khi đối chiếu các đoạn về Nephilim, kiểm tra xem VN có duy trì được sự phân biệt "thiên thần/sons of God" ≠ "Nephilim/con cháu" hay không.
