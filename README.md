# K3 Track 1 · Day 20–21 — AI Evaluation Capstone (eval-kit)

Repo làm bài capstone **AI Evaluation** của case **VLearn AI Tutor** — trợ giảng trả lời câu hỏi học viên, chỉ dựa trên tài liệu khóa học, output là JSON `{scope, answer, sources, followup_questions}`.

---

## 📌 Thông Tin Cá Nhân & Nhóm

- **Tên bài thi / Case:** VLearn AI Tutor Evaluation (eval-kit)
- **Khóa học:** AI Engineer K3 — Track 1
- **Danh sách thành viên nhóm:**
  1. **Mai Hồng Sơn** (Trưởng nhóm) — MHV: `2A202601921` — GitHub: [`@Mount2000`](https://github.com/Mount2000)
  2. **Nguyễn Tuấn Vũ** (Thành viên) — MHV: `2A202601845` — GitHub: [`@vunt2`](https://github.com/vunt2)

---

## 👥 Phân Công Nhiệm Vụ & Đóng Góp

| Mai Hồng Sơn (`2A202601921`)<br>*(Trưởng nhóm)* | Nguyễn Tuấn Vũ (`2A202601845`)<br>*(Thành viên)* |
|---|---|
| • Xây dựng bộ kịch bản dataset độc lập ban đầu.<br>• Thống nhất chốt bộ dữ liệu chuẩn 22 câu (`dataset-v1.jsonl`).<br>• Chạy mô hình Tutor sinh kết quả `results-v1.jsonl` và giao diện `report.html`.<br>• Thực hiện gán nhãn độc lập 22 kịch bản (`labels-Son.csv`).<br>• Đo độ đồng thuận (`eval/agreement.py`), thảo luận giải quyết các ca bất đồng và chốt Nhãn Vàng (`labels.csv`).<br>• Xây dựng Rubric checklist Yes/No và Routing Map 4 làn trong `REPORT.md`.<br>• Thiết kế và tinh chỉnh các phiên bản Prompt cho Judge (`judge-prompt-v1/v2/v3`).<br>• Kiểm thử làn Code checks (`code_checks.py`) và chạy calibration LLM Judge đo Confusion Matrix.<br>• Phân tích Scorecard theo lát cắt, mổ xẻ failure traces và hoàn thiện Báo cáo tổng kết PM Verdict trong `REPORT.md`. | • Xây dựng bộ kịch bản dataset độc lập ban đầu, thiết kế khung User Input Grid.<br>• Thống nhất chốt bộ dữ liệu chuẩn 22 câu (`dataset-v1.jsonl`).<br>• Thiết lập hạ tầng Braintrust Tracing (`vunt2/p/My Project`).<br>• Thực hiện gán nhãn độc lập 22 kịch bản (`labels-vu.csv`), ghi nhận các ca bất đồng về schema và deixis.<br>• Thảo luận giải quyết các ca bất đồng và chốt Nhãn Vàng (`labels.csv`).<br>• Phân tích cụm bất đồng để chuẩn hóa Rubric và hoàn thiện Routing Map 4 làn trong `REPORT.md`.<br>• Thực thi và xác nhận 44 unit tests offline (`tests/test_eval_kit.py`).<br>• Phân tích pattern lệch của Judge và đề xuất đòn bẩy kỹ thuật xử lý lỗi định dạng JSON.<br>• Đồng bộ nhật ký sử dụng AI (`ai-support-log.md`) và hoàn thiện Báo cáo tổng kết PM Verdict trong `REPORT.md`. |

---

## 🎯 Tóm Tắt Quyết Định Chất Lượng (Executive Verdict Summary)

- **Quyết định Release:** **HOLD (TẠM HOÃN PHÁT HÀNH — MỞ KHÓA TRONG 24H)**
- **Lý do từ chối phát hành ngay:**
  - Hệ thống đạt chất lượng xuất sắc ở các tiêu chí cốt lõi: **100% Chống Hallucination / Factuality**, **100% An toàn Sư phạm / Từ chối Jailbreak & Cheat**, và **100% Trích dẫn ID tồn tại thật**.
  - Tuy nhiên, sản phẩm **vi phạm 2 tiêu chí Blocker P0 về Hợp đồng Dữ liệu (System Contract)**:
    1. `schema_valid` đạt **95.5% < 100%** (Lỗi thiếu dấu phẩy trong mảng JSON tại `sc-11-amb-uig-bien` làm sập parser frontend).
    2. `sources_fields` đạt **90.9% < 95%** (Lỗi dùng sai key `"text"` thay vì `"quote"` tại `sc-03-in-eval-gap`).
- **Kế hoạch đòn bẩy 24 giờ:**
  1. *Code Layer ($0, 2h):* Tích hợp Pydantic Schema Validator & Middleware Auto-repair (tự động chèn dấu phẩy mảng JSON bị thiếu) trong `tutor/`.
  2. *Prompt Layer ($0, 30m):* Siết System Prompt cấm tuyệt đối dùng key `"text"` trong `sources`.
  3. *Release Gate:* Chạy lại bộ 22 regression test, ngay khi `schema_valid` đạt 100% sẽ chuyển trạng thái sang **SHIP WITH CONDITIONS**.

---

## 📂 Cấu Trúc Repo & Minh Chứng Nộp Bài

| Thư mục / file | Vai trò |
|---|---|
| `README.md` | **Báo cáo tổng quan** — Thông tin cá nhân/nhóm, bảng phân công nhiệm vụ chi tiết theo commit, tóm tắt quyết định |
| `ai-support-log.md` | **Nhật ký AI** — Ghi lại trung thực các bước dùng AI, cách kiểm chứng và các gợi ý đã bác bỏ |
| `tutor/` | **Sản phẩm đang được đánh giá** — tutor thật (`tutor.py`: system prompt + tool-calling `kb_search`, BM25 retrieval) và `corpus/` 18 tài liệu nguồn + `manifest.json` (địa chỉ nguồn: `doc_id#section_id`) |
| `eval/` | **Bộ máy chấm** — code chạy & phân tích eval + tracking: `run_eval.py`, `code_checks.py`, `judge.py`, `agreement.py`, `report.py`, `tracing.py`, kèm `judge_prompt.md` |
| `deliverables/` | **Khung bài nộp** — report log A→Z: `REPORT.md` (7 mục quyết định theo phase) + `evidence/` chứa data thô dẫn chứng |
| `deliverables/evidence/` | **Data thô minh chứng** — `dataset-v1.jsonl`, `results-v1.jsonl`, `labels.csv`, `labels-Son.csv`, `labels-vu.csv`, `judge-prompt-v1/v2/v3.md`, `verdicts-v1/v2/v3.jsonl`, `braintrust-link.md` |
| `tests/` | `test_eval_kit.py` — 44 test offline (không tốn API), chạy kiểm thử toàn bộ hệ thống |
| `data/` | File mẫu: `dataset.example.jsonl` và `labels.example.csv` |

**Mọi lệnh đều chạy từ root repo** (thư mục chứa README này). Luồng làm việc: file scratch sinh ra ở root → chốt một vòng thì copy vào `deliverables/evidence/`, đặt tên theo version (`results-v1.jsonl`, `verdicts-v2.jsonl`...), không ghi đè vòng cũ.

---

## 🚀 Quickstart (3 phút)

```bash
pip install -r requirements.txt        # 1. Cài đặt thư viện
cp .env.example .env                   # 2. Điền API key (OpenAI / DeepSeek / Gemini / Anthropic + BRAINTRUST_API_KEY)
python tests/test_eval_kit.py          # 3. Chạy 44 test offline (phải pass 100%)
python eval/code_checks.py             # 4. Chạy làn code checks trên results.jsonl
python eval/agreement.py deliverables/evidence/labels-Son.csv deliverables/evidence/labels-vu.csv # 5. Đo độ đồng thuận Human Baseline
python eval/judge.py                   # 6. Chạy LLM Judge tự động chấm theo rubric
python eval/report.py                  # 7. Sinh dashboard report.html trực quan
```

---

## 📖 Làm Bài Theo 6 Phase — Bước Nào Chạy Gì?

| Phase (theo file lab tổng) | Làm ở đâu | Trong repo này chạy gì |
|---|---|---|
| **P1. Thiết kế coverage** — chọn dimensions, tổ hợp, sinh câu hỏi | Giấy/sheet + AI chat | Chưa cần repo. Kết quả: viết vào `dataset.jsonl` (format xem `data/dataset.example.jsonl`, nhớ field `metadata.slide`) |
| **P2. Human baseline** — chạy dataset, chấm tay | Repo | `python eval/run_eval.py` → `python eval/report.py` → mở `report.html` gán nhãn → Export `labels-<tên>.csv` → `python eval/agreement.py labels-*.csv` đo đồng thuận |
| **P3. Rubric + routing** | Thảo luận nhóm | Không chạy repo. Viết vào mục 3 (Rubric v1) và mục 4 (Routing Map) trong `deliverables/REPORT.md` |
| **P4. Scale & calibrate judge** | Repo | `python eval/code_checks.py` (làn code) → sửa `eval/judge_prompt.md` → `python eval/judge.py` → đọc confusion matrix + % agreement. Sửa ít một thứ, chạy lại — mỗi vòng copy `eval/judge_prompt.md` + `verdicts.jsonl` ra `deliverables/evidence/` |
| **P5. Đọc kết quả, đặt ngưỡng** | Repo | `results.jsonl` có sẵn latency/tokens/cost từng câu; `report.html` để đọc theo slice |
| **P6. Verdict + report** | Viết trong `deliverables/` | Điền mục 6 (Scorecard & Gate) và mục 7 (Verdict) trong `deliverables/REPORT.md` |

---

## 🛠️ Chi Tiết Từng Lệnh Trong Eval Kit

```bash
python eval/run_eval.py      # 1. Chạy tutor trên dataset.jsonl -> results.jsonl
python eval/code_checks.py   # 2. Làn code: rule thuần Python trên results (không tốn API)
python eval/report.py        # 3. Sinh report.html -> mở, gán nhãn người, Export labels.csv
python eval/agreement.py labels-*.csv   # 4. Đo đồng thuận giữa các thành viên
python eval/judge.py         # 5. Judge chấm theo judge_prompt.md -> verdicts.jsonl + confusion matrix
```

### Bước 1 — `eval/run_eval.py`: Tutor thật chạy trên dataset
- Đọc từng dòng `dataset.jsonl`, gọi tutor theo **cơ chế tool-calling thật**: model tự quyết định gọi `kb_search` bao nhiêu lần, với truy vấn nào (xem trong `results.jsonl`, trường `tool_calls`).
- In từng dòng: thời gian, số token, chi phí ước tính. Tổng chi phí in ở cuối.

### Bước 2 — `eval/code_checks.py`: Làn code
- Kiểm tra các rule tự động: `schema_valid` (JSON đủ 4 field), `citation_exists` (doc_id/section_id có thật trong corpus), `quote_verbatim` (quote nằm đúng trong section đã cite).

### Bước 3 — `eval/judge.py`: LLM judge chấm
- Judge là model KHÁC tutor (mặc định `gemini-3.5-flash-lite` hoặc `gpt-4o-mini`) — tránh tự chấm chéo.
- Rubric judge nằm trong `eval/judge_prompt.md`.
- Đối chiếu với `labels.csv` để in ra Confusion Matrix và % Agreement.

### Bước 4 — `eval/report.py`: Nhìn và gán nhãn
- `report.html` tự chứa mọi dữ liệu: câu hỏi, slide context, câu trả lời, nguồn trích, verdict judge.
- Bấm pass/fail/uncertain và nhập note ngắn để gán nhãn người.

---

## 🤖 Chọn Model & Provider

Model viết dạng `provider/model` — repo gọi **thẳng API chuẩn của từng hãng**:

| Prefix model | Cần key trong .env |
|---|---|
| `openai/gpt-4o-mini`, ... | `OPENAI_API_KEY` |
| `deepseek/deepseek-v4-flash`, ... | `DEEPSEEK_API_KEY` |
| `gemini/gemini-3.1-flash-lite`, ... | `GEMINI_API_KEY` |
| `anthropic/claude-...` | `ANTHROPIC_API_KEY` |
| `openrouter/<vendor>/<model>` | `OPENROUTER_API_KEY` |

| Biến | Mặc định | Ý nghĩa |
|---|---|---|
| `EVAL_MODEL` | `deepseek/deepseek-v4-flash` | Model của tutor |
| `EVAL_JUDGE_MODEL` | `gemini/gemini-3.5-flash-lite` / `openai/gpt-4o-mini` | Model của judge (KHÁC tutor — tránh tự chấm chéo) |
| `BRAINTRUST_API_KEY` | — | Bật log trace lên Braintrust (bắt buộc khi nộp bài) |
| `LANGSMITH_API_KEY` | — | Bật log trace lên LangSmith |

---

## 📡 Tracing (Bắt Buộc Khi Nộp Bài)

Mọi run tutor/judge phải được log trace — đây là minh chứng bạn chạy thật.
- Link project Braintrust: `https://www.braintrust.dev/app/vunt2/p/My%20Project` (lưu tại `deliverables/evidence/braintrust-link.md`).

---

## 📝 Định Dạng Một Dòng Dataset

```json
{"scenario_id": "sc-01-in-calibration", "input": "câu hỏi của học viên",
 "expected_scope": "in_scope", "note": "ghi chú ngắn của nhóm",
 "metadata": {"slide": {"id": "s51", "title": "Calibration là gì", "keyword": "calibration"}}}
```

---

## 🔧 Gỡ Lỗi Nhanh

| Triệu chứng | Nguyên nhân thường gặp |
|---|---|
| `Chưa có API key...` | Thiếu `.env`, hoặc tên biến sai family |
| Row có `_parse_error` | Model trả JSON vỡ — mở `raw_content` xem; đó là failure mode thật, đáng ghi vào bài |
| Judge toàn 401 | Sai key cho provider của model judge |
| Retrieve trượt chủ đề | Câu hỏi quá ngắn/deixis — gắn `metadata.slide` với `keyword` vào row dataset |

---

## 📦 Quy Cách Nộp Bài Từ Repo

Từ repo này, copy sang `deliverables/evidence/` của bài nộp:
- `dataset.jsonl` → `deliverables/evidence/dataset-v1.jsonl`
- `results.jsonl` → `deliverables/evidence/results-v1.jsonl`
- `verdicts.jsonl` → `deliverables/evidence/verdicts-v1.jsonl` (v2, v3...)
- `eval/judge_prompt.md` → `deliverables/evidence/judge-prompt-v1.md` (v2, v3...)
- `labels.csv` → `deliverables/evidence/labels.csv`
- Số liệu agreement/confusion matrix → chép vào Mục 5 & Mục 7 của `deliverables/REPORT.md`.
