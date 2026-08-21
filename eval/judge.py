"""Chấm results.jsonl bằng LLM judge -> verdicts.jsonl, rồi đối chiếu labels.csv.

Cách dùng (chạy từ root repo):
  python3 eval/judge.py                                      # chấm tất cả các row với judge_prompt.md
  python3 eval/judge.py sc-01 sc-03                          # chỉ chấm các scenario_id được chọn
  python3 eval/judge.py --prompt eval/judge_prompt_followup.md --out verdicts-followup.jsonl

Judge dùng prompt trong eval/judge_prompt.md (placeholder {{input}} {{answer}} {{sources}} {{followup_questions}}).
Model judge mặc định khác model tutor (EVAL_JUDGE_MODEL, mặc định gemini/gemini-3.5-flash-lite hoặc openai/gpt-4o-mini)
để tránh tự chấm chéo cùng một model.
"""
import argparse
import csv
import json
import os
import sys
from pathlib import Path

# tutor.py nằm ở tutor/ (khu vực sản phẩm) — thêm vào sys.path để import được
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "tutor"))

import tutor
import tracing

# --- Tracing (tuỳ chọn): Braintrust hoặc LangSmith, log mỗi verdict thành 1 trace
_tracer = tracing.init_tracer()

JUDGE_MODEL = os.environ.get("EVAL_JUDGE_MODEL", "gemini/gemini-3.5-flash-lite")

# judge_prompt.md nằm cạnh file này trong eval/ — resolve theo __file__, không theo cwd
DEFAULT_PROMPT_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "judge_prompt.md")


def read_jsonl(path):
    if not os.path.exists(path):
        return []
    with open(path, encoding="utf-8") as f:
        return [json.loads(line) for line in f if line.strip()]


def read_labels(path="labels.csv"):
    """labels.csv: scenario_id,label,note — chỉ lấy dòng có label."""
    candidates = [path, "deliverables/evidence/labels-MaiHongSon.csv", "data/labels.example.csv"]
    target = None
    for p in candidates:
        if os.path.exists(p):
            target = p
            break
    if not target:
        return {}
    with open(target, encoding="utf-8") as f:
        return {
            r["scenario_id"]: r["label"].strip().lower()
            for r in csv.DictReader(f)
            if r.get("label", "").strip()
        }


def build_judge_prompt(rec, template):
    """Nhồi input/answer/sources/followup_questions của 1 row vào template.
    Nếu row có slide context thì gắn vào input — judge phải chấm theo đúng
    bối cảnh học viên đang đứng ở slide nào."""
    input_text = rec.get("input", "")
    if rec.get("slide"):
        input_text = tutor.format_slide_context(rec["slide"]).strip() + "\n" + input_text
    output = rec.get("output") or {}
    answer = json.dumps(output, ensure_ascii=False, indent=2)
    sources = json.dumps(output.get("sources", []), ensure_ascii=False, indent=2)
    fqs = json.dumps(output.get("followup_questions", []), ensure_ascii=False, indent=2)

    return (
        template.replace("{{input}}", input_text)
        .replace("{{answer}}", answer)
        .replace("{{sources}}", sources)
        .replace("{{followup_questions}}", fqs)
    )


def judge_row(rec, template):
    prompt = build_judge_prompt(rec, template)
    data, latency = tutor.chat(
        [{"role": "user", "content": prompt}], model=JUDGE_MODEL, max_tokens=600
    )
    content = data["choices"][0]["message"]["content"]
    out = tutor.parse_json_content(content)
    return {
        "scenario_id": rec["scenario_id"],
        "verdict": out.get("verdict", "uncertain"),
        "score": out.get("score"),
        "rationale": out.get("rationale", ""),
        "issues": out.get("issues", []),
        "raw_content": content,
        "usage": data.get("usage", {}),
        "latency_s": round(latency, 2),
    }


def print_confusion(verdicts, labels):
    """Ma trận nhầm lẫn judge (hàng) vs nhãn người (cột) + tỉ lệ đồng thuận."""
    classes = ["pass", "fail", "uncertain"]
    pairs = [
        (v["verdict"], labels[v["scenario_id"]])
        for v in verdicts
        if v["scenario_id"] in labels
    ]
    if not pairs:
        print("\nlabels.csv chưa có nhãn nào trùng scenario_id -> chưa tính được agreement.")
        print("Mở report.html, gán nhãn rồi bấm 'Export labels.csv' để có nhãn người.")
        return
    print("\nConfusion matrix (hàng = judge, cột = nhãn người):")
    print("%10s | %s" % ("", " ".join("%9s" % c for c in classes)))
    for cj in classes:
        row = [sum(1 for v, h in pairs if v == cj and h == ch) for ch in classes]
        print("%10s | %s" % (cj, " ".join("%9d" % x for x in row)))
    agree = sum(1 for v, h in pairs if v == h)
    print("Agreement: %d/%d = %.0f%%" % (agree, len(pairs), 100.0 * agree / len(pairs)))


def main():
    parser = argparse.ArgumentParser(description="Run LLM Judge evaluation")
    parser.add_argument("scenarios", nargs="*", help="Optional scenario IDs to evaluate")
    parser.add_argument(
        "--prompt", default=DEFAULT_PROMPT_PATH, help="Path to judge prompt markdown file"
    )
    parser.add_argument("--out", default="verdicts.jsonl", help="Output path for verdicts JSONL")
    args = parser.parse_args()

    results = read_jsonl("results.jsonl")
    if not results:
        sys.exit("Không thấy results.jsonl — chạy python3 eval/run_eval.py trước.")
    if not tutor.get_api_key(JUDGE_MODEL):
        sys.exit("Chưa có API key cho judge model %s — xem .env.example." % JUDGE_MODEL)

    chosen = set(args.scenarios)
    rows = [r for r in results if not chosen or r["scenario_id"] in chosen]
    rows = [r for r in rows if "output" in r]  # bỏ row lỗi, không có gì để chấm

    if not os.path.exists(args.prompt):
        sys.exit(f"Không tìm thấy file prompt: {args.prompt}")

    template = open(args.prompt, encoding="utf-8").read()
    print(f"Chấm {len(rows)} row bằng judge {JUDGE_MODEL} [prompt: {args.prompt}] ...")

    verdicts = []
    for i, rec in enumerate(rows, 1):
        print(f"[{i}/{len(rows)}] {rec['scenario_id']} ... ", end="", flush=True)
        try:
            v = judge_row(rec, template)
            _tracer.log_run(
                name="judge-run",
                inputs={"scenario_id": rec["scenario_id"], "judge_model": JUDGE_MODEL},
                outputs={"verdict": v["verdict"], "rationale": v.get("rationale", "")},
                metrics={
                    **{
                        k: x
                        for k, x in v.get("usage", {}).items()
                        if isinstance(x, (int, float))
                    },
                    "latency_s": v.get("latency_s", 0),
                },
            )
            print(v["verdict"])
        except Exception as e:
            v = {
                "scenario_id": rec["scenario_id"],
                "verdict": "uncertain",
                "error": str(e),
            }
            print(f"LỖI: {e}")
        verdicts.append(v)

    with open(args.out, "w", encoding="utf-8") as f:
        for v in verdicts:
            f.write(json.dumps(v, ensure_ascii=False) + "\n")
    print(f"Ghi {len(verdicts)} verdict vào {args.out}")
    if _tracer.backend:
        _tracer.flush()
        print(f"Đã log {len(verdicts)} trace judge lên {_tracer.backend}.")
    print_confusion(verdicts, read_labels())


if __name__ == "__main__":
    main()

