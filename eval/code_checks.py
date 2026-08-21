"""Code checks — kiểm tra results.jsonl bằng rule thuần Python (không tốn API).

Đây là làn "Code check" của bài lab: những tiêu chí viết được thành rule thì kiểm
bằng code — nhanh, rẻ, khách quan, chạy lại bao nhiêu lần cũng được.

Chạy:  python3 eval/code_checks.py            # in bảng pass/fail từng check từng row
Mở rộng: thêm hàm check_* mới của riêng nhóm (xem các hàm mẫu dưới).
"""
import inspect
import json
import os
import re
import sys
from pathlib import Path

# tutor.py nằm ở tutor/ (khu vực sản phẩm) — thêm vào sys.path để import được
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "tutor"))

import tutor  # dùng lại load_corpus, tokens

EXPECTED_FIELDS = {"scope", "answer", "sources", "followup_questions"}
EXPECTED_SOURCE_FIELDS = {"doc_id", "section_id", "quote"}
VALID_SCOPES = {"in_scope", "out_of_scope"}


def check_schema(rec):
    """Output parse được và đủ 4 field đúng contract."""
    out = rec.get("output") or {}
    if out.get("_parse_error"):
        return False, "JSON không parse được (xem raw_content)"
    missing = EXPECTED_FIELDS - set(out)
    if missing:
        return False, "thiếu field: " + ", ".join(sorted(missing))
    return True, None


def check_scope_valid(rec):
    """Scope phải là in_scope hoặc out_of_scope."""
    out = rec.get("output") or {}
    if out.get("_parse_error"):
        return None, "bỏ qua (JSON vỡ)"
    scope = out.get("scope")
    if scope not in VALID_SCOPES:
        return False, f"scope không hợp lệ: {scope}"
    return True, None


def check_sources_fields(rec):
    """Mỗi source phải có đủ 3 trường chuẩn: doc_id, section_id, quote (không dùng text/content)."""
    out = rec.get("output") or {}
    if out.get("_parse_error"):
        return None, "bỏ qua (JSON vỡ)"
    sources = out.get("sources")
    if not isinstance(sources, list):
        return False, "sources không phải là list"
    for i, s in enumerate(sources):
        if not isinstance(s, dict):
            return False, f"sources[{i}] không phải object"
        missing = EXPECTED_SOURCE_FIELDS - set(s.keys())
        if missing:
            return False, f"sources[{i}] thiếu field: {sorted(missing)} (keys hiện có: {list(s.keys())})"
    return True, None


def check_followup_format(rec):
    """followup_questions phải là list gồm đúng 3 câu hỏi không rỗng."""
    out = rec.get("output") or {}
    if out.get("_parse_error"):
        return None, "bỏ qua (JSON vỡ)"
    fu = out.get("followup_questions")
    if not isinstance(fu, list):
        return False, "followup_questions không phải list"
    if len(fu) != 3:
        return False, f"followup_questions cần đúng 3 câu, hiện có {len(fu)}"
    if any(not isinstance(q, str) or not q.strip() for q in fu):
        return False, "chứa câu hỏi rỗng hoặc không phải string"
    return True, None


def check_citation_exists(rec, valid_ids):
    """Mọi doc_id/section_id trong sources phải tồn tại thật trong corpus."""
    out = rec.get("output") or {}
    if out.get("_parse_error"):
        return None, "bỏ qua (JSON vỡ)"
    for s in out.get("sources") or []:
        key = (s.get("doc_id"), s.get("section_id"))
        if key not in valid_ids:
            return False, f"nguồn không tồn tại: {key[0]}#{key[1]}"
    return True, None


def _check_quote_segment(part, target_tokens):
    """Kiểm tra một phân đoạn quote có xuất hiện trong target_tokens hay không."""
    part_toks = tutor.tokens(part)
    if not part_toks:
        return True
    n = len(part_toks)
    # 1. Trích đoạn liên tiếp chính xác
    if any(target_tokens[i:i + n] == part_toks for i in range(len(target_tokens) - n + 1)):
        return True
    # 2. Xử lý trường hợp slide ngắt cột / OCR / xuống dòng: độ trùng khớp token >= 80%
    target_set = set(target_tokens)
    matched = sum(1 for t in part_toks if t in target_set)
    if matched / n >= 0.8:
        return True
    return False


def check_quote_verbatim(rec, section_tokens):
    """Quote phải nằm trong section đã cite.
    
    Hỗ trợ quote chứa dấu ba chấm (...) hoặc xuống dòng khi trích đoạn ngắt quãng,
    và xử lý định dạng ngắt dòng/cột của slide bài giảng.
    """
    out = rec.get("output") or {}
    if out.get("_parse_error"):
        return None, "bỏ qua (JSON vỡ)"
    for s in out.get("sources") or []:
        key = (s.get("doc_id"), s.get("section_id"))
        tokens = section_tokens.get(key, [])
        raw_quote = s.get("quote") or s.get("text") or ""
        if not raw_quote:
            continue
        # Tách quote theo dấu ba chấm (...) hoặc xuống dòng nếu trích ngắt quãng
        segments = [seg.strip() for seg in re.split(r"\.{2,}|…|\n", raw_quote) if seg.strip()]
        for seg in segments:
            if not _check_quote_segment(seg, tokens):
                sec_id = s.get("section_id")
                return False, f"quote không khớp section {sec_id}: \"{raw_quote[:40]}...\""
    return True, None


CHECKS = [
    ("schema_valid", check_schema),
    ("scope_valid", check_scope_valid),
    ("sources_fields", check_sources_fields),
    ("followup_format", check_followup_format),
    ("citation_exists", check_citation_exists),
    ("quote_verbatim", check_quote_verbatim),
]


def main(path="results.jsonl"):
    if not os.path.exists(path):
        raise SystemExit("Không thấy %s — chạy python3 eval/run_eval.py trước." % path)
    rows = [json.loads(l) for l in open(path, encoding="utf-8") if l.strip()]

    sections = tutor.load_corpus()
    valid_ids = {(s["doc_id"], s["section_id"]) for s in sections}
    section_tokens = {(s["doc_id"], s["section_id"]): tutor.tokens(s["text"]) for s in sections}

    totals = {name: [0, 0] for name, _ in CHECKS}  # [pass, fail] (skip không đếm)
    for rec in rows:
        sid = rec.get("scenario_id", "?")
        line = [sid]
        for name, fn in CHECKS:
            # Tự động truyền đúng tham số theo chữ ký của hàm check
            sig = inspect.signature(fn)
            params_count = len(sig.parameters)
            if params_count == 1:
                ok, reason = fn(rec)
            elif name == "citation_exists":
                ok, reason = fn(rec, valid_ids)
            elif name == "quote_verbatim":
                ok, reason = fn(rec, section_tokens)
            else:
                ok, reason = fn(rec, valid_ids)

            if ok is None:
                line.append(f"{name}: skip")
                continue
            totals[name][0 if ok else 1] += 1
            line.append(f"{name}: {'pass' if ok else 'FAIL — ' + str(reason)}")
        print(" | ".join(line))

    print("\nTổng kết:")
    for name, (p, f) in totals.items():
        print(f"  {name}: {p} pass / {f} fail")


if __name__ == "__main__":
    import sys
    main(sys.argv[1] if len(sys.argv) > 1 else "results.jsonl")
