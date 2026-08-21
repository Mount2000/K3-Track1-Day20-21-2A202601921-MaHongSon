# K3 Track 1 · Day 20–21 — AI Evaluation Capstone (eval-kit)

Repo làm bài capstone **AI Evaluation** của case **VLearn AI Tutor** — trợ giảng trả lời câu hỏi học viên, chỉ dựa trên tài liệu khóa học, output là JSON `{scope, answer, sources, followup_questions}`.

---

## 📌 Thông Tin Cá Nhân & Nhóm

- **Họ và tên:** Mai Hồng Sơn
- **Mã học viên (MHV):** `2A202601921`
- **Tên Repo / Thư mục:** `K3-Track1-Day20-21-2A202601921-MaiHongSon`
- **Danh sách thành viên nhóm:**
  1. **Mai Hồng Sơn** MHV: `2A202601921`
  2. **Nguyễn Tuấn Vũ** MHV: `2A202601845`

---

## 🚀 Đóng Góp Của Tôi (Mai Hồng Sơn)

Dưới đây là chi tiết các hạng mục đóng góp trong toàn bộ vòng đời Eval Loop, được đối chiếu trực tiếp với lịch sử các commit trong repository:

### 1. Phase 1 — Thiết kế Coverage & Chuẩn hóa Dataset
- **Nội dung thực hiện:**
  - Brainstorm và xây dựng Lưới Input Grid (3 Persona × 5 Ý định hỏi), áp dụng chiến lược **Challenge Over-sampling** (~36.4% ca khó/biên).
  - Khởi tạo và chuẩn hóa bộ dữ liệu kiểm thử `dataset-v1.jsonl` gồm 22 kịch bản chuẩn hóa (`scenario_id`, `input`, `expected_scope`, `metadata.slide`, `dimension_values`, `expected_behavior`, `risk_if_fail`).
  - Viết và hoàn thiện Mục 1 & Mục 2 trong `deliverables/REPORT.md`.

### 2. Phase 2 — Human Baseline & Phân Tích Đồng Thuận
- **Nội dung thực hiện:**
  - Chạy mô phỏng tutor và xuất kết quả `deliverables/evidence/results-v1.jsonl`.
  - Thực hiện gán nhãn thủ công độc lập 22 kịch bản tại `deliverables/evidence/labels-Son.csv` (`labels-MaiHongSon.csv`).
  - Phân tích và mổ xẻ 3 ca bất đồng quan điểm (`sc-03`, `sc-10`, `sc-16`) giữa annotator Sơn và Vũ (đạt độ đồng thuận ban đầu 86.4%), xác định nguyên nhân gốc rễ để chuẩn hóa Rubric.

### 3. Phase 3 — Thiết Kế Rubric v1 & Routing Map
- **Nội dung thực hiện:**
  - Thiết kế bộ tiêu chí Rubric v1 gồm 5 tiêu chí chuẩn hóa, triệt tiêu tính từ định tính, chuyển sang **Checklist Yes/No quan sát được** kèm bộ 3 ví dụ (Pass/Fail/Borderline).
  - Phân định rạch ròi nhóm tiêu chí **Blocker P0** (bắt buộc 100% Pass) vs **Non-Blocker**.
  - Xây dựng **Routing Map 4 làn** (Code Check, LLM Judge, LLM Assist, Expert Review) tối ưu hóa chi phí ($0 cho tầng code, tiết kiệm API token) và đảm bảo an toàn sư phạm.


### 4. Phase 4 — Scale & Hiệu Chuẩn LLM Judge (Calibration)
- **Nội dung thực hiện:**
  - Mở rộng bộ kiểm tra tự động `eval/code_checks.py` (bổ sung hàm kiểm tra tính toàn vẹn JSON schema, kiểm tra doc_id tồn tại trong manifest, và thuật toán so khớp trích dẫn nguyên văn token-level).
  - Nâng cấp `eval/judge.py` và thiết kế 3 phiên bản Prompt cho Judge: `judge-prompt-v1.md`, `judge-prompt-v2.md` (bổ sung Near-miss Examples), `judge-prompt-v3.md` (chấm câu hỏi gợi mở).
  - Thực hiện chạy và đo đạc Calibration: Nâng độ đồng thuận của Judge với Human

### 5. Phase 5 & 6 — Scorecard, Gate Policy & Báo Cáo Verdict (PM 1-Page Summary)
- **Nội dung thực hiện:**
  - Xây dựng Scorecard tổng hợp đo lường trên cả 3 góc độ: Kỹ thuật (Code/Judge), Trải nghiệm & Độ trễ (Latency/Cost), và An toàn Sư phạm.

