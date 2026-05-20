---
name: game-theory-patterns
description: Pattern lỗi tái diễn khi đối chiếu bản dịch VN của series Game Theory (đặc biệt #26 The Holy Empire of AI)
metadata:
  type: feedback
---

Khi đối chiếu bản dịch SRT thuộc series Game Theory (giảng viên John dạy địa chính trị + lịch sử hội kín), ưu tiên scan các pattern lỗi sau:

**1. Speech-to-text bug ở văn bản trích dẫn kinh điển**
- Khi giảng viên đọc to văn bản Albert Pike (Morals and Dogma), Brzezinski (Between Two Ages), Thiel (Zero to One), auto-sub méo từ → dịch giả đoán nhầm.
- Ví dụ thực tế từ #26:
  - "Morality is **faced** in full bloom" thực ra là **"Morality is faith in full bloom"** — VN dịch "khuôn mặt" thay vì "đức tin" → Critical.
  - "bow to **arrow**" thực ra là **"bow to error"** — VN dịch "nỗi sai trái".
  - "**emlarations** of mankind" thực ra là **"amelioration of mankind"** — VN dịch "khai sáng".
  - "despos and **desperatisms** temporary and spiritual" thực ra là **"despots and despotisms temporal and spiritual"** — VN dịch "tâm linh" thay vì "thần quyền".
- **How to apply:** Khi gặp đoạn lecturer đọc văn bản (thường bắt đầu "Can you read, Alan?" / "I'll read the first part"), nếu một từ trong VN nghe lạ → đối chiếu với bản gốc PDF của Morals and Dogma / Between Two Ages / Zero to One trên Internet Archive.

**2. Nhất quán khái niệm trung tâm "Holy Empire of Reason"**
- Glossary quy định **Đế quốc Lý trí Thiêng liêng** (viết hoa) là khái niệm trung tâm.
- VN trong #26 viết thường khắp nơi và đôi chỗ bỏ "lý trí" (chỉ "đế chế thiêng liêng đích thực").
- **How to apply:** Grep "đế quốc" và "đế chế" trong file VN, kiểm tra viết hoa và đầy đủ 3 thành tố "Lý trí + Thiêng liêng + Đế quốc".

**3. "sons of God" trong context Game Theory ≠ spiritual SUN**
- Khác với series Secret History (xem [[sun-son-nous]]), trong Game Theory #26 cụm "real sons of God" để chỉ Caesar/Napoleon/Hitler/Stalin tự coi mình là anh hùng-thần (Nephilim) — đây thực sự là "sons" (con), không phải "sun".
- VN dịch "con đích thực của Chúa" → dễ hiểu nhầm = Jesus.
- **How to apply:** Trong context Caesar/Napoleon/Hitler/Trump self-image: dịch "những người con đích thực của các vị thần" hoặc giữ ngoặc "sons of God".

**4. Đảo cú pháp "neither...nor"**
- EN: "offers **neither** principles **nor** progress" → VN dịch "không hề cho cả nguyên tắc lẫn tiến bộ" gây tối nghĩa.
- **How to apply:** Với "neither X nor Y" → dùng "chẳng X cũng chẳng Y" / "không X cũng không Y" — tránh "không... cả... lẫn..." mơ hồ.

**5. Auto-sub đã xử lý tốt trong series này (không cần flag)**
- "Nice Templars" / "Night Templars" / "dice templars" → đều xử lý đúng thành **Hiệp sĩ dòng Đền**.
- "AI civilian state" (speech-to-text bug) → **nhà nước giám sát AI/nhà nước AI giám sát công dân**.
- "esquetology" / "estology" → **thuyết cánh chung**.
- "narcissism" (bug từ "neoplatonism") → **chủ nghĩa Tân Plato**.
- "Jack de mole" → **Jacques de Molay**.
- "Baffomet" → **Baphomet**.
- "Zedith Bzinski" / "Zebrainski" → **Zbigniew Brzezinski**.
- "Sen Altman" → **Sam Altman**.
- "Peter Theo/Theal/Theel" → **Peter Thiel**.

**6. Đoạn nhạy cảm — Marxism khen ngợi**
- Brzezinski trong Between Two Ages công khai khen chủ nghĩa Mác là "đỉnh cao tiến hóa của lý trí". VN giữ trung tính theo lời nguyên văn, không thêm sắc thái phê phán — đúng rule glossary.
- **How to apply:** Tiếp tục giữ trung tính khi gặp đoạn trích này; không thêm "(theo Brzezinski)" hay tính từ đánh giá.

Related: [[secret-history-patterns]], [[glossary-authority]]
