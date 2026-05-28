---
name: game-theory-patterns
description: Pattern lỗi tái diễn khi đối chiếu bản dịch VN của series Game Theory (#26 Holy Empire of AI, #28 Predictive History)
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
- "esquetology" / "estology" → **thuyết cánh chung / thuyết mạt thế**.
- "narcissism" (bug từ "neoplatonism") → **chủ nghĩa Tân Plato**.
- "Jack de mole" → **Jacques de Molay**.
- "Baffomet" → **Baphomet**.
- "Zedith Bzinski" / "Zebrainski" → **Zbigniew Brzezinski**.
- "Sen Altman" → **Sam Altman**.
- "Peter Theo/Theal/Theel" → **Peter Thiel**.
- **#28 (Predictive History) — auto-sub names ĐÃ sửa đúng hết trong VN:** "Sith the great"→Cyrus Đại đế; "Bashibba"→Bathsheba; "Uria/Urea the Hitite/Heitite"→Uriah người Hittite; "alaxic/Alex mosque"→đền thờ Al-Aqsa; "luranic capitalism"→Kabbalah của Luria; "Adam Kenmont/Connan/Kenmon"→Adam Kadmon; "Bronage collapse"→sụp đổ Thời đại Đồ đồng; "straight of Hmoose/Jialter/Malaka"→Hormuz/Gibraltar/Malacca; "cape of gold...good hope"→mũi Hảo Vọng.

**6. Đoạn nhạy cảm — Marxism khen ngợi**
- Brzezinski trong Between Two Ages công khai khen chủ nghĩa Mác là "đỉnh cao tiến hóa của lý trí". VN giữ trung tính theo lời nguyên văn, không thêm sắc thái phê phán — đúng rule glossary.
- **How to apply:** Tiếp tục giữ trung tính khi gặp đoạn trích này; không thêm "(theo Brzezinski)" hay tính từ đánh giá.

**7. ĐẢO NGHĨA "had little of X" — bẫy phổ biến trong Pike**
- EN Pike: "Carthaginian soldiers... had little of Hannibal's magnimity" = THIẾU/Ít có khí phách Hannibal (so sánh ngược).
- VN dễ dịch nhầm thành "có một chút khí phách của Hannibal" → đảo ý hoàn toàn.
- **Why:** "have little of X" trong văn cổ điển = lack X (mang ít/không có X).
- **How to apply:** Quét tất cả "có chút/một chút" trong block dịch Pike; đối chiếu xem EN có "little of" → phải đổi sang "thiếu/không có".

**8. ĐẢO NGHĨA "I'm not saying he's X" — phủ định mệnh đề phát ngôn**
- EN: "I'm not saying he's a Freemason" = "Tôi không bảo ông ấy là Tam Điểm" (phủ định ở mệnh đề "tôi nói").
- VN trong #26 dịch thành "Ông ấy không là Tam Điểm" → phủ định sự kiện luôn (mạnh hơn nhiều).
- **Why:** Speaker chỉ rào trước, không khẳng định/phủ định sự kiện. VN làm mất nuance.
- **How to apply:** Với cấu trúc "I'm not saying X" → giữ "Tôi không nói rằng X" / "Tôi không bảo X" / "Không phải ý tôi là X" — đừng cắt thành phủ định sự kiện.
- **#28:** "I'm not saying this is 100% correct" → VN "tôi đâu có nói nó đúng tuyệt đối" — xử lý ĐÚNG.

**9. "piecemeal" — speech-to-text thường ra "peacemail"**
- EN gốc Brzezinski: "piecemeal transformation" = chuyển đổi từng bước/từng phần.
- Auto-sub: "peacemail" → VN dễ dịch "êm thấm/êm đẹp" → sai nghĩa.
- **How to apply:** Khi thấy "peacemail" trong auto-sub → dịch là "từng bước" / "từng phần".

**10. "useful idiots" — thuật ngữ chính trị, không nên thô tục hóa**
- EN: "the secret societies call this are just useful idiots" — thuật ngữ Lenin/chiến tranh lạnh.
- VN #26 dịch "những thằng ngu hữu dụng" → quá thô; nên "những kẻ ngu hữu dụng" hoặc "con tốt thí có ích".
- **How to apply:** Giữ thuật ngữ chính trị trung tính, tránh "thằng/đứa". (#28 dịch "stupid things"→"chuyện ngu ngốc" — chấp nhận được, sát giọng giảng viên.)

**11. REGRESSION khi dịch lại — khi sửa pattern cũ, kiểm tra không tạo pattern mới**
- Thực tế vòng 2 review #26: bản cũ (.bak) dịch ĐÚNG "đức tin nở rộ" (faith in full bloom) và "khuất phục trước sai lầm" (bow to error), nhưng bản dịch lại đã regressed thành "khuôn mặt nở rộ" và "cúi đầu trước mũi tên" (= literal từ auto-sub buggy "faced" và "arrow").
- **Why:** Khi reviewer/dịch lại tin auto-sub thay vì giữ kết quả bản trước, đảo nghĩa lại xuất hiện.
- **How to apply:** Khi đối chiếu vòng 2, ALWAYS so sánh 3 chiều EN-VN-VN.bak: nếu bản .bak đúng nhưng bản mới sai, đây là regression — flag ngay với severity Critical.

**12. "holy temple of reason" vs "holy empire of reason" — phân biệt 2 cụm**
- EN có 2 cụm: "holy **empire** of reason" (khái niệm chính trị toàn cầu) và "holy **temple** of reason" (metaphor về biến con người thành đá xây đền).
- Glossary chỉ quy định "Đế quốc Lý trí Thiêng liêng" cho cụm thứ nhất. Cụm thứ hai nên viết hoa nhất quán: "Đền Lý trí Thiêng liêng" (hiện tại VN #26 viết thường "ngôi đền lý trí thiêng liêng").
- **How to apply:** Cả 2 cụm nên viết hoa Lý trí + Thiêng liêng để nhất quán branding khái niệm trung tâm.

**13. Auto-sub "the world is not perfect" — kiểm tra logic ngữ cảnh**
- EN line 1534-1535: "If we all think alike, the world is not perfect" — auto-sub có thể đã insert "not" sai (vì sau đó nói "We now achieve a common brotherhood... achieve God if everyone thinks alike" → rõ ràng phải là perfect).
- VN #26 dịch literal "thế giới không hoàn hảo" → đảo nghĩa.
- **How to apply:** Khi câu EN mâu thuẫn với câu liền sau, KHÔNG dịch literal — kiểm tra context để quyết đúng/sai.

**14. #28 "sexual in nature / climax / accelerationism" — đoạn nhạy cảm đã dịch ĐÚNG, giữ nguyên**
- "fundamentally sexual in nature" → "về bản chất, mang tính tính dục" / "Mang bản chất tính dục" — bám sát, không né tránh, không tô đậm. ĐÚNG.
- "trying to climax as soon as possible" → "muốn lên đỉnh càng sớm càng tốt" — sát nghĩa tính dục theo dụng ý giảng viên (climax = cực khoái + cao trào). Giữ.
- "accelerationism" → "chủ nghĩa gia tốc"; "back propagation" → "lan truyền ngược"; "Federal Reserve" → "Cục Dự trữ Liên bang"; "transnational capital" → "tư bản xuyên quốc gia"; "techno-Marxism" → "chủ nghĩa Marx công nghệ"; "Plato's cave" → "hang động Plato". Tất cả ĐÚNG glossary.
- "demons summoned... Jesus resurrecting through AI" → "con quỷ được triệu hồi... Chúa Jesus đang tự hồi sinh thông qua AI" — bám sát, trung tính. ĐÚNG.

**15. #29 ĐẢO NGHĨA "fatality rate" — auto-sub bug từ "fertility rate"**
- EN block 2108 (Final Examination): "Israel is energetic as has high fatality rate" — speaker đang liệt kê ĐIỂM MẠNH Israel. Israel nổi tiếng tỷ suất sinh cao trong các nước phát triển (high fertility). Auto-sub méo fertility → fatality.
- VN #29 block 1010 dịch LITERAL "Israel có sức bật, tỷ lệ tử vong cao" → đảo nghĩa Critical (tỷ lệ tử vong cao là điểm YẾU, ngược với dụng ý speaker).
- **How to apply:** Khi auto-sub có "fatality rate" trong context dân số/sức mạnh quốc gia — kiểm tra context, gần như chắc chắn là "fertility rate" (tỷ suất sinh). Đảo nghĩa từ "tử vong" → "sinh".

**16. #29 "extract whales" idiom — không dịch literal "vắt cá voi"**
- EN block 1233: "How can American extract whales from the Chinese consumer" — "whales" trong context tài chính/marketing/gambling = khách hàng VIP, người tiêu dùng cao cấp/giàu nhất.
- VN dịch LITERAL "vắt cá voi từ người tiêu dùng Trung Quốc" → người Việt không hiểu. Đáng lẽ "vắt khách hàng lớn" / "khai thác con cá lớn" / "khai thác tầng lớp tiêu dùng cao cấp".
- **How to apply:** "whales" trong context kinh tế/marketing/gambling → "khách hàng VIP" / "con cá lớn" / "khách sộp", KHÔNG dịch chữ "cá voi".

**17. #29 "Adam Mus" / "Theo" / "Mariel Maro" — KHÔNG sửa auto-sub tên người**
- VN #29 giữ nguyên auto-sub bug nhiều tên: "Adam Musk" (đúng = Elon Musk), "Trump, Theo, Musk" (đúng = Trump, Thiel, Musk), "Maria Maro" (đúng = Maria Bartiromo).
- Đây là regression so với #28 đã sửa hết tên auto-sub (xem pattern #5).
- **How to apply:** Trước khi xuất file VN, GREP các tên ngoại quốc nghi vấn ("Adam Mus", "Theo" độc lập, "Maro", "Carson" thay vì Carlson, "Ghan", etc.) và đối chiếu với glossary file. Đặc biệt chú ý các tên có trong glossary nhưng auto-sub méo.

**18. #29 "domination trial" / "defamation" — bug pháp lý**
- EN block 1953: "2020 election domination trial" → đây là auto-sub bug từ "defamation/Dominion trial" (vụ kiện Dominion Voting Systems vs Fox News năm 2023, dẫn đến Tucker Carlson rời Fox).
- VN dịch "vụ kiện thao túng bầu cử" → sai nghĩa (manipulation ≠ defamation). Đáng lẽ "vụ kiện Dominion" hoặc "vụ kiện phỉ báng bầu cử 2020".
- **How to apply:** Khi auto-sub có "domination" trong context legal/court → kiểm tra xem có phải "defamation" (phỉ báng) hay "Dominion" (tên công ty máy bầu cử). Cả 2 đều dẫn về vụ Fox-Dominion 2023.

**19. #29 "Israel(ite)" vs "Jews" — phân biệt rõ trong context lịch sử**
- EN dùng lẫn "Israelite" (dân Israel cổ trong Kinh Thánh / dân Do Thái) và "Jews" (người Do Thái) trong cùng đoạn nói về 109 nước trục xuất.
- VN #29 dịch hết thành "người Israel" → người Việt sẽ hiểu nhầm là "Israeli" (công dân Israel hiện đại). Trong cùng đoạn, lúc thì "người Israel" lúc thì "người Do Thái" gây bất nhất nghiêm trọng.
- **How to apply:** Trong context lịch sử cổ/Kinh Thánh/trục xuất xuyên thế kỷ → DÙNG "người Do Thái" cho cả "Israelites" lẫn "Jews". Chỉ dùng "người Israel" khi nói về công dân Israel hiện đại (state of Israel post-1948).

**20. #29 "border work" auto-sub bug từ "broader work"**
- EN block 1494: "Terasra letter lecture and your border work on civilizational strategy" → "border" auto-sub bug, đáng lẽ "broader" (= rộng hơn/lớn hơn).
- VN dịch "công trình mở đường" → sai nghĩa (pioneer work ≠ broader work). Đáng lẽ "công trình rộng hơn về chiến lược nền văn minh".
- **How to apply:** "border work" trong context khen ngợi tác giả/công trình → gần như chắc chắn là "broader work".

**21. #29 "if Israel were to nuke Iran" → dịch động từ**
- EN "nuke Iran" = ném bom hạt nhân/tấn công hạt nhân Iran.
- VN #29 dịch "nếu Israel hạt nhân hóa Iran" → "hạt nhân hóa" trong tiếng Việt thường = nuclearize (trang bị vũ khí hạt nhân cho ai đó), KHÁC nghĩa "nuke" (tấn công bằng vũ khí hạt nhân).
- **How to apply:** "nuke X" → "ném bom hạt nhân X" / "tấn công X bằng vũ khí hạt nhân", KHÔNG dùng "hạt nhân hóa".

**22. #29 "sacage" auto-sub bug từ "sacrilege"**
- EN block 2128: "It is sacage" trong context UAE bị Iran ghê tởm — đúng = "sacrilege" (báng bổ thiêng liêng, phạm thượng).
- VN dịch "sự ô uế thiêng liêng" → không chuẩn (ô uế = pollution/defilement; sacrilege = báng bổ). Đáng lẽ "báng bổ thần thánh" hoặc "phạm thượng".

**23. #29 inconsistent capitalization "monad" vs "Monad"**
- VN #29: 16 lần "monad" thường, 3 lần "Monad" hoa. Cần thống nhất 1 cách viết xuyên file.

**24. #29 eschatology dịch không nhất quán**
- VN #29 dùng cả: "chung mạt luận" (block 204, 220), "hệ cánh chung" (block 678), "thuyết cánh chung" (block 751).
- Glossary nên chốt 1 cách dịch. Khuyến nghị "thuyết cánh chung" (phổ biến nhất trong văn bản tôn giáo VN).

Related: [[secret-history-patterns]], [[glossary-authority]]
