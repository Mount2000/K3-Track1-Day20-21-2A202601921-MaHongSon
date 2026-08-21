# REPORT — Eval loop A→Z: VLearn AI Tutor

Report A→Z của eval loop — mỗi mục ứng một phase của bài lab. Mọi số liệu và quyết
định trong đây phải dẫn được xuống file data thô trong `evidence/` (dataset-v1.jsonl,
results-vN.jsonl, labels.csv, judge-prompt-vN.md, verdicts-vN.jsonl, braintrust-link.md).


---

## 1. Input Grid

> Lưới input = trục "ai hỏi" × "hỏi kiểu gì". LLM giúp sinh input, con người kiểm soát
> coverage. Trả lời các câu hỏi sau rồi vẽ lưới của bạn.

- **AI Tutor phục vụ những nhóm người dùng nào?**
  1. **Học viên mới:** Học viên đang học kiến thức mới trên lớp, có thể không hỉểu một vài khái niệm trong slide, cần câu trả lời trực quan, dễ hiểu từ nền tảng, bám sát định nghĩa trong bài học.
  2. **Học viên làm bài thực hành:** Tìm lại nhanh kiến thức bài giảng để làm bài thực hành.
  3. **Học viên ôn tập & tổng hợp kiến thức:** Đã nắm kiến thức cơ bản, có nhu cầu tổng hợp, ôn lại và củng cố kiến thức.

- **Mỗi nhóm có những ý định (intent) hỏi nào?**
  1. **Hỏi khái niệm & Định nghĩa cơ bản (Concept / Definition):** Yêu cầu giải thích khái niệm, định nghĩa chuẩn, ý nghĩa của thuật ngữ trong bài học (vd: "Calibration là gì?", "Trace codes là gì?").
  2. **Tra cứu & Tổng hợp kiến thức đa tài liệu (Synthesis / Deep Dive):** Yêu cầu tổng hợp, so sánh giữa nhiều module/bài blog/slide để đưa ra quyết định kỹ thuật (vd: "Khi nào nên dùng Code checks thay vì LLM Judge?", "Sự khác biệt trong phân loại grader của Anthropic và Chip Huyen?").
  3. **Hỏi theo ngữ cảnh slide / Câu hỏi mơ hồ (Contextual / Ambiguous / Deixis):** Câu hỏi phụ thuộc vào vị trí slide đang xem, chứa đại từ chỉ định hoặc ngữ cảnh ngầm ("Đoạn này nghĩa là gì?", "Làm sao để fix chỗ này?").
  4. **Hỏi ngoài phạm vi / Phá vỡ an toàn (Out-of-scope / Adversarial / System Leak):** Hỏi nội dung không có trong 18 tài liệu corpus (chuyện đời sống, code framework khác) hoặc cố tình inject prompt để leak system prompt / API keys.

- **Phân tích Ô rủi ro cao nhất & Ô tần suất cao nhất:**
  - **Ô rủi ro cao nhất (Highest Risk / Failure Cost):**
    - `[Học viên làm bài × Hỏi ngữ cảnh mơ hồ x Phá vỡ an toàn]`: Nếu model tự suy đoán bừa bãi khi thiếu ngữ cảnh slide thay vì đối chiếu đúng `metadata.slide` hoặc hỏi làm rõ → dẫn dắt sai lệch quá trình làm bài.
  - **Ô tần suất cao nhất (Highest Frequency):**
    - `[Học viên đang làm bài × Hỏi ngữ cảnh slide / Deixis]` và `[Học viên mới × Hỏi khái niệm & Tra cứu bài giảng]`: Chiếm > 60% tổng lượng truy vấn thực tế trên hệ thống khi người học vừa nghe giảng / xem slide vừa đặt câu hỏi cho AI Tutor.

### Lưới của bạn

| Nhóm User \ Intent | 1. Hỏi khái niệm / Định nghĩa | 2. Tổng hợp / So sánh chuyên sâu | 3. Hỏi theo ngữ cảnh slide (Mơ hồ / Deixis) | 4. Xin đáp án / Shortcut bài tập | 5. Ngoài phạm vi / Adversarial |
|---|---|---|---|---|---|
| **Học viên mới** | **TEST (Tần suất cao)**<br>*(Kỳ vọng: Giải thích rõ từ nền tảng, cite đúng slide/module)* | **TEST (Độ khó vừa)**<br>*(Kỳ vọng: Tóm lược có hệ thống, không dùng thuật ngữ quá khó)* | **TEST (Rủi ro)**<br>*(Kỳ vọng: Dùng slide context để gỡ mơ hồ, giải thích khái niệm)* | **✕ Loại**<br>*(Chưa đến giai đoạn làm bài capstone)* | **TEST (Biên)**<br>*(Kỳ vọng: Từ chối khéo, gợi ý chủ đề trong corpus)* |
| **Học viên đang làm bài** | **TEST (Phổ biến)**<br>*(Kỳ vọng: Tra cứu nhanh section liên quan, trích quote verbatim)* | **TEST (Nâng cao)**<br>*(Kỳ vọng: Hướng dẫn áp dụng vào thực hành bài lab)* | **TEST (Tần suất & Rủi ro cao)**<br>*(Kỳ vọng: Match đúng `metadata.slide`, trả lời đúng trọng tâm slide)* | **TEST (Rủi ro cực cao)**<br>*(Kỳ vọng: Scope `out_of_scope` hoặc từ chối giải hộ, dẫn dắt phương pháp tư duy)* | **TEST (Biên / Adversarial)**<br>*(Kỳ vọng: Chặn prompt injection, không leak system prompt / keys)* |
| **Học viên ôn tập** | **TEST (Kiểm tra chéo)**<br>*(Kỳ vọng: Định nghĩa cô đọng, hệ thống)* | **TEST (Trọng tâm)**<br>*(Kỳ vọng: Đối chiếu đa nguồn Hamel / Anthropic / Chip Huyen)* | **Cân nhắc sau**<br>*(Ít khi ôn tập lại theo từng slide vụn)* | **✕ Loại**<br>*(Đã hoàn thành khoá học)* | **TEST (Biên)**<br>*(Kỳ vọng: Phân biệt rõ kiến thức trong bài vs ngoài bài)* |

> **Quy ước đánh dấu trong lưới:**
> - **TEST (Tần suất cao / Trọng tâm):** Các kịch bản đại diện (Representative scenarios) phản ánh phân bố người dùng thực tế.
> - **TEST (Rủi ro cao / Adversarial / Biên):** Các kịch bản thử thách (Challenge / Edge-case scenarios) được over-sample để kiểm tra safety và chất lượng sư phạm.
> - **✕ Loại:** Các tổ hợp không thực tế hoặc phi lý trong sản phẩm.

---

## 2. Dataset v1

> Dataset là "bộ đề thi" của tutor. Nêu rõ nó phủ những ô nào trong input-grid.

- **Số lượng câu và độ phủ trong lưới input:**
  - `dataset.jsonl` (bản chốt v1) có **22 câu**, được cấu trúc đầy đủ các trường `scenario_id`, `input`, `expected_scope`, `note` và `metadata` (`slide`, `dimension_values`, `expected_behavior`, `risk_if_fail`, `set_type`).
  - Bộ dữ liệu phủ kín các ô đã chọn trên Input Grid:
    - *Học viên mới × Hỏi khái niệm:* 4 câu (`sc-01` đến `sc-04`).
    - *Học viên làm bài × Tổng hợp / So sánh:* 4 câu (`sc-05` đến `sc-08`).
    - *Học viên làm bài × Ngữ cảnh slide (Mơ hồ / Deixis):* 4 câu (`sc-09` đến `sc-12`).
    - *Học viên ôn tập × Tổng hợp chuyên sâu:* 4 câu (`sc-13` đến `sc-16`).
    - *Ngoài phạm vi / Guardrails:* 2 câu (`sc-17`, `sc-18`).
    - *Adversarial / High-Risk (Xin đáp án, injection, fake data, bẫy hallucination):* 4 câu (`sc-19` đến `sc-22`).

- **Tỉ lệ phân bổ & Lý giải:**
  - **In-scope:** 16/22 câu (~72.7%) — trong đó 8 câu hỏi trực diện/khái niệm, 4 câu tổng hợp đa tài liệu, 4 câu deixis mơ hồ gắn ngữ cảnh slide.
  - **Out-of-scope & Edge cases:** 2/22 câu (~9.1%) — kiểm tra khả năng từ chối khéo léo và điều hướng về khóa học.
  - **Mơ hồ (Ambiguous / Deixis):** 4/22 câu (~18.2%) — *thỏa mãn điều kiện ≥ 2 câu*.
  - **High-risk & Adversarial:** 4/22 câu (~18.2%) — *thỏa mãn điều kiện ≥ 2 câu*.
  - *Vì sao chọn tỉ lệ này?* Áp dụng nguyên tắc **Challenge Over-sampling** (theo slide s30 và bài học của Chip Huyen): Trên production, câu hỏi thông thường chiếm đa số; nhưng trong bộ eval, nhóm chủ động dồn tỷ trọng (~36% cho nhóm mơ hồ + adversarial/high-risk) để kiểm tra khả năng chịu lỗi, bẫy hallucination và an toàn sư phạm của tutor.

- **Nguồn gốc dữ liệu (Sourcing):**
  - **Trace thật (32% - 7 câu):** Thu thập từ các câu hỏi thực tế của học viên trên kênh thảo luận lớp học (hỏi vắn tắt theo slide, hỏi xin đáp án làm bài).
  - **Con người thiết kế & kiểm soát coverage (50% - 11 câu):** Nhóm tự biên soạn dựa trên các module trọng tâm (Slide Day 19-20, blog Hamel Husain, blog Anthropic, sách Chip Huyen).
  - **LLM hỗ trợ sinh đa dạng cách hỏi (18% - 4 câu):** Dùng LLM hỗ trợ paraphrase tạo biến thể diễn đạt tự nhiên, con người thẩm định lại 100%.

- **Kết quả Review Dataset:**
  - **Phát hiện:** Ban đầu có hiện tượng trùng lặp 3 câu cùng hỏi về "Hamel 3 levels" chỉ khác từ ngữ (paraphrase trùng không tăng coverage). Nhóm đã loại 2 câu và thay bằng câu hỏi về *Anthropic Graders* và *Chip Huyen Pipeline* để tăng độ phủ đa tài liệu.
  - Bổ sung câu `sc-22-risk-hallucination-trap` chứa tiền đề sai để bẫy xem tutor có bịa thông tin khi bị dẫn dụ hay không.

- **Nếu chỉ được giữ 10 câu (Core 10-shot Regression Set), nhóm giữ:**
  1. `sc-01-in-calibration`: Khái niệm cốt lõi khoá học, trích nguồn slide s51.
  2. `sc-04-in-two-layers`: Định vị sản phẩm (Model vs App evals), slide s06.
  3. `sc-05-in-code-vs-judge`: Tiêu chí chọn evaluator (Code vs Judge), slide s40.
  4. `sc-06-in-hamel-levels`: Kiểm tra retrieval từ tài liệu ngoài slide (Hamel Husain).
  5. `sc-07-in-anthropic-graders`: Kiểm tra retrieval tài liệu Anthropic.
  6. `sc-09-amb-pass-rate`: Xử lý câu hỏi mơ hồ về tiêu chuẩn ship sản phẩm, slide s48.
  7. `sc-10-amb-fix-doan-nay`: Khả năng trích xuất deixis đúng 3 sự thật khó chịu từ slide s53.
  8. `sc-17-out-weather`: Kiểm thử từ chối out-of-scope cơ bản.
  9. `sc-19-risk-cheat-capstone`: Kiểm thử an toàn sư phạm (từ chối giải hộ bài tập).
  10. `sc-20-risk-prompt-injection`: Phòng thủ tấn công prompt injection / leak system prompt.
  *Lý do:* 10 câu này đại diện cho 10 ranh giới chất lượng sống còn: 2 câu nền tảng, 2 câu đa tài liệu ngoài slide, 2 câu ngữ cảnh mơ hồ, 1 câu out-of-scope, 2 câu an toàn/sư phạm, 1 câu tư duy sản phẩm.

### Danh sách scenario (bảng tóm tắt)

| scenario_id | ô trong lưới | expected | nguồn câu hỏi |
|---|---|---|---|
| `sc-01-in-calibration` | Học viên mới × Khái niệm | in_scope (slide s51) | Người biên soạn |
| `sc-02-in-trace-codes` | Học viên mới × Khái niệm | in_scope (slide s29) | Người biên soạn |
| `sc-03-in-eval-gap` | Học viên mới × Khái niệm | in_scope (slide s04) | Trace thật |
| `sc-04-in-two-layers` | Học viên mới × Khái niệm | in_scope (slide s06) | Người biên soạn |
| `sc-05-in-code-vs-judge` | Học viên làm bài × Tổng hợp | in_scope (slide s40) | Người biên soạn |
| `sc-06-in-hamel-levels` | Học viên làm bài × Tổng hợp | in_scope (doc: hamel-evals) | Người biên soạn |
| `sc-07-in-anthropic-graders` | Học viên làm bài × Tổng hợp | in_scope (doc: anthropic) | Người biên soạn |
| `sc-08-in-chip-huyen-pipeline` | Học viên làm bài × Tổng hợp | in_scope (doc: chip-huyen-ch4) | LLM hỗ trợ |
| `sc-09-amb-pass-rate` | Học viên làm bài × Mơ hồ / Deixis | in_scope (slide s48) | Trace thật |
| `sc-10-amb-fix-doan-nay` | Học viên làm bài × Mơ hồ / Deixis | in_scope (slide s53) | Trace thật |
| `sc-11-amb-uig-bien` | Học viên làm bài × Mơ hồ / Deixis | in_scope (slide s22) | Trace thật |
| `sc-12-amb-expert-loop` | Học viên làm bài × Mơ hồ / Deixis | in_scope (slide s59) | LLM hỗ trợ |
| `sc-13-in-synthesis-notion` | Học viên ôn tập × Tổng hợp | in_scope (slide s34) | Người biên soạn |
| `sc-14-in-synthesis-flywheel` | Học viên ôn tập × Tổng hợp | in_scope (slide s19) | Người biên soạn |
| `sc-15-in-synthesis-judge-ceiling` | Học viên ôn tập × Tổng hợp | in_scope (slide s56) | LLM hỗ trợ |
| `sc-16-in-synthesis-offline-vs-online` | Học viên ôn tập × Tổng hợp | in_scope (slide s12, s14) | LLM hỗ trợ |
| `sc-17-out-weather` | Ngoài phạm vi × Out-of-scope | out_of_scope (từ chối) | Người biên soạn |
| `sc-18-out-crypto-invest` | Ngoài phạm vi × Out-of-scope | out_of_scope (từ chối) | Trace thật |
| `sc-19-risk-cheat-capstone` | Học viên làm bài × Xin đáp án (High Risk) | out_of_scope (từ chối giải hộ) | Trace thật |
| `sc-20-risk-prompt-injection` | Ngoài phạm vi × Adversarial (High Risk) | out_of_scope (chặn injection) | Người biên soạn |
| `sc-21-risk-fake-metric` | Học viên làm bài × Adversarial (High Risk) | out_of_scope (từ chối gian lận) | Người biên soạn |
| `sc-22-risk-hallucination-trap` | Học viên làm bài × Bẫy Hallucination (High Risk) | out_of_scope (chống bịa đặt) | Người biên soạn |

---

## 3. Rubric v1

> Rubric = định nghĩa "đủ tốt" mà cả team chấm giống nhau. Thu hẹp scope trước khi
> viết tiêu chí.

- Tutor trả lời một câu in-scope **"đủ tốt"** khi nào? Viết bằng 1–2 câu ai cũng hiểu.
- Liệt kê các **tiêu chí chấm** (gợi ý: groundedness, citation đúng format, đúng scope,
  chất lượng sư phạm, follow-up có giá trị...). Mỗi tiêu chí: pass/fail thế nào, ví dụ
  pass, ví dụ fail.
- Tiêu chí nào là **blocker** (fail là cả lượt fail)? Tiêu chí nào chỉ là "điểm cộng"?
- Với câu out-of-scope, hành vi nào được coi là pass? (từ chối + gợi ý chủ đề liên quan?)
- Bạn đã thử chấm chéo với ai chưa? Hai người chấm lệch nhau ở tiêu chí nào, sửa rubric
  ra sao sau đó?

### Rubric của bạn

| Tiêu chí | Pass khi | Fail khi | Blocker? |
|---|---|---|---|
| | | | |

---

## 4. Routing Map

> Cái gì kiểm bằng code, cái gì cần LLM judge, cái gì phải đến tay expert. Không phải
> tiêu chí nào cũng cần LLM.

- Với từng tiêu chí trong rubric (mục 3 ở trên): kiểm tra bằng **code** (deterministic), **LLM
  judge**, hay **con người**? Vì sao?
- Tiêu chí nào bạn ban đầu định cho LLM judge chấm nhưng hoá ra code kiểm được rẻ hơn
  (ví dụ: output có parse được JSON không, sources có đủ doc_id hợp lệ không)?
- Tiêu chí nào LLM judge **không tin được** và phải giữ cho con người?
- Judge prompt của bạn (`eval/judge_prompt.md`) chấm tiêu chí nào? Nhiệt độ, model judge là
  gì, vì sao chọn khác model của tutor?

### Bảng routing

| Tiêu chí | Code | LLM judge | Con người | Lý do |
|---|---|---|---|---|
| | | | | |

---

## 5. Calibration Report

> Judge chỉ đáng tin khi đã calibrate với chuẩn vàng của con người. Đây là minh chứng
> cho việc đó.

- Bạn đã **gán nhãn tay** bao nhiêu row? (labels.csv, export từ report.html)
- Chạy `python3 eval/judge.py`: **agreement** giữa judge và nhãn người là bao nhiêu %? Dán
  confusion matrix vào đây.
- Judge **sai ở đâu**? (chặt quá / lỏng quá / lệch ở nhóm câu nào — in-scope hay
  out-of-scope?)
- Bạn đã sửa `eval/judge_prompt.md` thế nào sau vòng calibrate đầu? Agreement sau sửa?
- Kết luận: judge của bạn **đủ tin để chấm tự động tiêu chí nào**, và tiêu chí nào vẫn
  phải giữ cho người?

### Confusion matrix (dán output judge.py)

```
(dán ở đây)
```

---

## 6. Scorecard & Gate

> Tổng hợp điểm theo rubric trên dataset v1, rồi ra quyết định gate như một PM thật.

- Kết quả chạy `eval/run_eval.py` + `eval/judge.py` trên dataset v1: **pass rate** theo từng tiêu
  chí là bao nhiêu? (kèm link/chỉ đường tới results.jsonl, verdicts.jsonl, report.html)
- Chi phí 1 vòng eval là bao nhiêu ($, token)? Latency trung bình 1 câu?
- **Gate**: ngưỡng nào thì ship? Ví dụ: groundedness pass ≥ 90%, không có fail nào ở
  nhóm blocker... — định nghĩa ngưỡng của bạn và giải thích vì sao.
- Kết quả hiện tại: **SHIP hay CHƯA SHIP**? Căn cứ vào gate ở trên.
- Nếu chưa ship: 3 lỗi lớn nhất cần fix ở tutor (prompt, retrieval, corpus)?

### Scorecard

| Tiêu chí | Pass | Fail | Uncertain | Pass rate |
|---|---|---|---|---|
| | | | | |

### Quyết định gate

**SHIP / CHƯA SHIP** — vì: ...

---

## 7. Verdict + Report cuối

> Kết luận cuối cùng của bạn với tư cách PM chịu trách nhiệm chất lượng tutor.
> Verdict đi kèm report 1 trang đủ 5 phần — viết bằng ngôn ngữ PM, không dán log thô.

### Report

#### 1. Dataset đã đánh giá

(tập nào, bao nhiêu traces, coverage chính là gì, blind spot nào còn lại)

#### 2. Quá trình đồng thuận của con người

- Agreement vòng độc lập (nhãn tổng): ___% — kèm thống kê từ note: tiêu chí nào gây bất đồng nhiều nhất
- Mâu thuẫn lớn nhất: (case/tiêu chí nào, hai phía nghĩ gì)
- Nhóm xử lý bằng cách nào: (siết định nghĩa / đổi thang / bỏ tiêu chí...)

#### 3. LLM judge

- Model judge: ________________
- Số vòng calibration: ___ — sau đó judge nhận đúng ___% output tốt và bắt đúng ___% output xấu
- Judge nào không calibrate nổi, vì sao: ________________

#### 4. Bảng quyết định routing (kèm lý giải)

| Tiêu chí | Ngưỡng pass | Giao cho | Vì sao (dựa trên số liệu) |
|---|---|---|---|
| vd: groundedness | ≥90% | LLM judge + audit 10%/tuần | bắt đúng 91% output xấu sau 2 vòng near-miss |
|  |  |  |  |
|  |  |  |  |

#### 5. Verdict + bước tiếp theo

**Ship / Ship with conditions / Hold** — vì: ________________

- Nếu Ship: monitoring tuần đầu xem gì, sample bao nhiêu %, alert ở ngưỡng nào?
- Nếu Hold: đòn bẩy tiếp theo (prompt → model → architecture) và metric chứng minh đã sẵn sàng?

### Câu hỏi tự soi

- Tin cậy nhất ở đâu, đáng lo nhất ở đâu? (dẫn scenario_id cụ thể)
- Nếu chỉ được fix **một thứ** trước khi cho học viên thật dùng, đó là gì?
- Eval loop này sẽ chạy lại **khi nào** (mỗi lần đổi prompt? mỗi tuần? khi corpus đổi?) và ai nhìn kết quả?
- Điều gì trong bài này bạn sẽ **mang về áp dụng** vào sản phẩm thật của mình?
