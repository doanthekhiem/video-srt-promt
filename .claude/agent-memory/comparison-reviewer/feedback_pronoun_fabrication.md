---
name: pronoun-fabrication
description: VN bịa xưng hô (em/anh/chị/con/ông/bà) khi EN dùng imperative hoặc không nêu chủ ngữ
metadata:
  type: feedback
---

VN bịa xưng hô vai vế (em/anh/chị/con/ông/bà/ngươi) khi EN dùng imperative hoặc không nêu chủ ngữ rõ ràng.

**Why:** Pipeline dịch tự động (LLM) thường thêm xưng hô VN cho "tự nhiên" với TTS, nhưng:
- EN imperative ("continue reading", "look at this", "remember", "consider") KHÔNG có chủ ngữ — VN thêm "em/anh/con" là **bịa quan hệ vai vế** không có trong nguồn.
- Bài giảng triết học/lịch sử của series Secret History/Game Theory là **độc thoại lecturer → audience**, không phải đối thoại có tôn ti — không nên thêm xưng hô thân mật.
- Sai vai vế làm méo register: lecturer trang trọng → giọng đối thoại gia đình.

**How to apply:**

**Pattern cần flag (Moderate, có thể Critical nếu lặp lại nhiều):**
1. EN imperative không có chủ ngữ → VN thêm "em/anh/chị/con":
   - EN "continue reading, please" → VN "**em** đọc tiếp" ❌ → đúng: "**xin** đọc tiếp" / "**hãy** đọc tiếp"
   - EN "look at this" → VN "**em** nhìn xem" ❌ → đúng: "**hãy** nhìn xem" / "nhìn xem"
   - EN "remember that" → VN "**con** nhớ rằng" ❌ → đúng: "**hãy** nhớ rằng" / "nhớ rằng"
   - EN "consider" → VN "**bạn** thử nghĩ xem" ⚠️ — "bạn" generic tạm chấp nhận nhưng nên ưu tiên "hãy nghĩ xem"

2. EN "you" generic (mang nghĩa "người ta/ai cũng") → VN bịa quan hệ cụ thể:
   - EN "you can see" → VN "**em/con** thấy" ❌ → đúng: "**bạn** thấy" / "ta thấy" / "ai cũng thấy"
   - EN "if you're a Christian" → VN "nếu **con** là tín đồ" ❌ → đúng: "nếu **bạn** là tín đồ"

3. EN đối thoại có speaker rõ (Q&A với học sinh, dialogue trích từ sách) → VN cần khớp xưng hô:
   - EN "He said to his disciples" → VN "Ngài nói với môn đệ" ✅ (đúng vai vế lịch sử)
   - EN "They said to him, 'Shall we...'" → VN "họ hỏi Ngài rằng vậy **chúng con**..." ✅ (vai môn đệ → "con" hợp ngữ cảnh tôn giáo)
   - Lưu ý: chỉ giữ "con/ngươi/Ngài" khi đó là **trích kinh điển** hoặc đối thoại tôn giáo rõ ràng.

**Quy tắc thay thế ưu tiên:**
- Imperative → "hãy/xin" + verb (không chủ ngữ)
- "You" generic → "bạn/ta" hoặc passive
- Chỉ dùng "em/anh/con" khi EN có vocative rõ hoặc context đối thoại trực tiếp với người ngang vai

## ⚠️ EXCEPTION: "anh / anh chị" cho generic "you" — Secret History series

**ALLOWED (không flag):** Trong series Secret History, lecturer dùng "you" generic → VN dịch thành "**anh / anh chị**" được CHẤP NHẬN như **voice nhất quán toàn series** cho TTS.

**Why:** User chốt 2026-06-11 sau review file #20 "Hellenistic World" — dịch giả/pipeline cố ý dùng "anh/anh chị" để tạo register lecturer thân thiện-trang trọng cho TTS Vietnamese. Đây là dịch tự do có chủ ý, không phải bịa.

**How to apply:**
- KHÔNG flag VN "anh/anh chị X" khi EN có "you X" generic, dù EN không có vocative.
- Vẫn flag "**em/con/cháu**" — đây là vai vế hạ thấp, KHÔNG được dùng cho "you" generic.
- Vẫn flag "anh/anh chị" nếu xuất hiện trong **imperative không chủ ngữ** ("anh đọc tiếp" cho EN "continue reading") — vì imperative không có "you" subject.
- File #20 review 2026-06: 6+ instance "anh/anh chị" cho "you generic" → confirmed OK, không cần fix.

**Bài học từ regression file #22 block 232 (review 2026-06):**
- EN "continue reading, please" → VN "**em** đọc tiếp phần này" — bịa "em" vì pipeline tự thêm xưng hô cho TTS.
- Đây là **blind spot** của agent — memory trước không có rule này nên không flag.

**Cách quét nhanh:**
- Grep `\bem \b`, `\bcon \b`, `\bcháu \b` ở đầu mệnh đề trong VN → xem EN cùng timestamp có vocative/chủ ngữ tương ứng không
- Đặc biệt soát các block có động từ ra lệnh: đọc, nghe, nhớ, nhìn, hiểu, xem, nghĩ — kiểm tra trước đó có "em/con/bạn" không cần thiết không

Liên kết: [[secret-history-patterns]], [[padding-religious-tone]]
