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

**11. "Disclaimer" và "personal thing" dịch chữ trong file #6**
- "Disclaimer" (block 403, EN block 1101) → VN dịch "lời tuyên bố loại trừ" — quá kỹ thuật. Chuẩn: "lời miễn trừ trách nhiệm" hoặc "lời cảnh báo trước".
- "a personal thing owned by Elon Musk" (block 391, EN block 1066) → VN dịch "một thứ riêng tư do Elon Musk sở hữu" — sai nghĩa (personal/private property ≠ privacy). Chuẩn: "tài sản cá nhân" hoặc "tài sản tư nhân".
- **Why:** Auto-pipeline dịch chữ idiom EN không qua bộ lọc tự nhiên.
- **How to apply:** Grep nhanh "riêng tư", "tuyên bố loại trừ" sau khi dịch.

**12. "Egyptian prisons" trong context chiến tranh Iraq/Guantanamo (file #6)**
- Speaker EN gốc nói "Egyptian prisons / Egyptian authorities" khi đang nói về nhà tù Mỹ ở Trung Đông (Abu Ghraib, Guantanamo). Có thể là lỗi đọc của speaker hoặc trích dẫn từ báo cáo Human Rights First về Ai Cập.
- VN bám sát EN — không phải lỗi dịch nhưng cần flag biên tập vì khán giả VN có thể bối rối.
- **How to apply:** Khi gặp tên quốc gia/địa danh đột ngột không khớp context xung quanh — flag Moderate kèm note "có thể là lỗi speaker EN gốc".

**13. "Chúa" vs "thần" trong context đa thần giáo Ai Cập (file #6)**
- VN dịch "God" → "Chúa" trong context Pharaoh-Ai Cập (block 244 "feel as though they're truly God").
- "Chúa" có sắc thái Christian-độc thần; nên dùng "thần" để khớp ngữ cảnh đa thần Ai Cập.
- Tuy nhiên với NDE chung (block 239-241) "they all went to meet God" — "Chúa" có thể chấp nhận vì context phổ quát.
- **How to apply:** Phân biệt theo context — Pharaoh/Ai Cập = "thần"; NDE phổ quát = "Chúa" hoặc "Đấng Tối Cao".

**14. Đảo nghĩa logic ở câu hỏi mâu thuẫn của học sinh (file #6, block 252-254)**
- EN: học sinh đặt câu hỏi có hai vế mâu thuẫn cần giảng viên giải đáp ("nếu làm xấu không lên thiên đường, nhưng NDE cho thấy không có khác biệt — vậy là sao?").
- VN trình bày như tuyên bố thay vì câu hỏi mâu thuẫn → người đọc không hiểu giảng viên đang trả lời gì.
- **How to apply:** Với câu hỏi học sinh có cấu trúc "if A but if B then C", VN phải giữ kết cấu giả thiết-mâu thuẫn rõ ràng, không biến thành chuỗi câu khẳng định rời rạc.

**15. Thêm tính từ không có vào tên hội kín / câu lạc bộ / tên trường (file #7)**
- Pattern: VN thêm "nổi tiếng" sau tên câu lạc bộ mà EN không có "famous".
- VD file #7 block 486: "Porcelain Club nổi tiếng" trong khi EN chỉ "Porcelain Club".
- **Why:** Có thể do dịch giả muốn cho người Việt biết đây là CLB quan trọng. Nhưng vi phạm criterion "không thêm tính từ không có trong EN cho tên trường, hội kín".
- **How to apply:** Grep nhanh "nổi tiếng", "lừng danh", "danh giá" sau tên Porcelain/Ivy/Skull and Bones/Harvard/Yale; nếu EN không có "famous/well-known/prestigious" — xóa.

**16. "Took risks" dịch quá mạnh thành "phá luật" (file #7)**
- Block 53 EN: "They played football. They took risks." VN: "rồi chơi bóng bầu dục, họ liều lĩnh phá luật."
- **Why:** "Took risks" = chấp nhận rủi ro/liều lĩnh; thêm "phá luật" là vượt nghĩa.
- **How to apply:** "Take risks" → "chấp nhận rủi ro", "liều lĩnh"; KHÔNG thêm "phá luật/luật lệ" trừ khi EN dùng "break the rules", "transgressive".

**17. Filler "now/okay" cuối câu được dịch thành "giờ đây/bây giờ" gây nghĩa lệch (file #7)**
- Block 363 EN: "...he never went to college." VN: "...chưa bao giờ học đại học giờ đây."
- "giờ đây" thừa, có thể đã merge filler "Now,/Okay," của block sau.
- **How to apply:** Khi VN có "giờ đây/bây giờ" ở cuối câu khẳng định về sự kiện quá khứ (George Washington, Lincoln...), kiểm tra xem có phải merge nhầm filler không.

**19. Speaker tự sửa lỗi nói nhịu — VN xử lý đúng là BỎ phần nhịu (file #9, xác nhận tốt)**
- EN block 1216-1219 (#9): speaker nói "God will never forgive you. Oh, sorry. God will never forget you." → tự sửa forgive→forget. VN bỏ phần "Oh sorry" và chỉ giữ "không bao giờ quên" + "luôn tha thứ". Đây là cách xử lý ĐÚNG, không flag.
- **How to apply:** Khi EN có "Oh sorry / I mean / let me rephrase" + câu sửa lại — VN nên dịch theo phiên bản đã sửa, bỏ phần nhịu. Đừng flag là missing content.

**20. File #9 "The Theory of Everything" — chất lượng cao, không lỗi Critical (mốc so sánh)**
- Toàn bộ thuật ngữ triết/lượng tử (noumenon=vật tự thân, phenomena=hiện tượng, Geist, wave function collapse=sụp đổ hàm sóng, quantum fields=trường lượng tử, monad/dyad, transhumanism=siêu nhân loại, eschatology=thuyết mạt thế, transgression=phạm giới, inversion=đảo ngược, "as above so below"=trên sao dưới vậy) đều đúng.
- Negation flip trọng điểm: Wigner "it does not collapse" → "không hề sụp đổ" — KHÔNG đảo nghĩa. Số liệu (80/90%, 99.9% DNA, 200k/50k năm, 987+25=20) khớp hết. Đoạn God-sex (block 677) dịch sát "ăn nằm với mẹ ta", không thêm sắc thái.
- sun/son ([[sun-son-nous]]) KHÔNG xuất hiện vấn đề ở tập này (monad mô tả "vibrates/emanates/breathes" → VN "phát tỏa, suy nghĩ, hít thở" đúng).
- Lỗi duy nhất đáng sửa: block 558 thừa "như vậy" (lỗi nối block kiểu pattern #1).

**18. Bỏ tính từ phân biệt định chế quan trọng (file #7)**
- Block 113: EN "institutional reasons" → VN "lý do riêng" (bỏ "institutional").
- Block 510: EN "political career" → VN "sự nghiệp" (bỏ "political").
- **Why:** Trong bài giảng phân tích quyền lực Harvard/Obama, các tính từ "institutional", "political" mang ý nghĩa luận điểm. Bỏ làm yếu lập luận.
- **How to apply:** Khi đối chiếu các đoạn lý thuyết về định chế/chính trị, kiểm tra các tính từ "institutional/political/structural/systemic" có được giữ trong VN không.
