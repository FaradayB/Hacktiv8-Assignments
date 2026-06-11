import csv
import math
import statistics
from pathlib import Path

REPORTS_DIR = Path("reports")
TARGET_COST_IDR = 250.0

def _to_float(row: dict, key: str) -> float:
    try:
        return float(row.get(key, 0) or 0)
    except (TypeError, ValueError):
        return 0.0


def _to_int(row: dict, key: str) -> int:
    try:
        return int(float(row.get(key, 0) or 0))
    except (TypeError, ValueError):
        return 0


def _to_bool(row: dict, key: str) -> bool:
    return str(row.get(key, "")).strip().lower() in {"true", "1", "yes"}


def _quantile(values: list[float], q: float) -> float:
    if not values:
        return 0.0
    if len(values) == 1:
        return values[0]
    arr = sorted(values)
    pos = (len(arr) - 1) * q
    lo = math.floor(pos)
    hi = math.ceil(pos)
    if lo == hi:
        return arr[lo]
    return arr[lo] + (arr[hi] - arr[lo]) * (pos - lo)


def _safe_mean(values: list[float]) -> float:
    return statistics.mean(values) if values else 0.0


def _safe_std(values: list[float]) -> float:
    return statistics.pstdev(values) if len(values) > 1 else 0.0


def _load_rows(path: Path) -> list[dict]:
    if not path.exists():
        return []
    with path.open("r", encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def _aggregate(rows: list[dict], label: str) -> dict:
    total = len(rows)
    latencies = [_to_float(r, "latency_ms") for r in rows]
    costs = [_to_float(r, "cost_idr") for r in rows]
    bleus = [_to_float(r, "bleu") for r in rows]
    rouges = [_to_float(r, "rouge_l") for r in rows]
    sims = [_to_float(r, "embedding_similarity") for r in rows]

    retrieval_hits = sum(_to_int(r, "retrieval_hit") for r in rows)
    grounded_hits = sum(_to_int(r, "grounded") for r in rows)
    refusal_count = sum(1 for r in rows if _to_bool(r, "refusal"))

    return {
        "variant": label,
        "num_samples": total,
        "bleu_mean": _safe_mean(bleus),
        "bleu_std": _safe_std(bleus),
        "rouge_l_mean": _safe_mean(rouges),
        "rouge_l_std": _safe_std(rouges),
        "embedding_similarity_mean": _safe_mean(sims),
        "embedding_similarity_std": _safe_std(sims),
        "retrieval_hit_rate": (retrieval_hits / total) if total else 0.0,
        "grounded_rate": (grounded_hits / total) if total else 0.0,
        "refusal_rate": (refusal_count / total) if total else 0.0,
        "latency_p50_ms": _quantile(latencies, 0.50),
        "latency_p95_ms": _quantile(latencies, 0.95),
        "latency_mean_ms": _safe_mean(latencies),
        "cost_mean_idr": _safe_mean(costs),
        "cost_p95_idr": _quantile(costs, 0.95),
    }


def _write_ab_comparison(path: Path, summaries: list[dict]) -> None:
    fieldnames = [
        "variant",
        "num_samples",
        "bleu_mean",
        "bleu_std",
        "rouge_l_mean",
        "rouge_l_std",
        "embedding_similarity_mean",
        "embedding_similarity_std",
        "retrieval_hit_rate",
        "grounded_rate",
        "refusal_rate",
        "latency_p50_ms",
        "latency_p95_ms",
        "latency_mean_ms",
        "cost_mean_idr",
        "cost_p95_idr",
    ]
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        for summary in summaries:
            writer.writerow(
                {
                    key: (round(value, 4) if isinstance(value, float) else value)
                    for key, value in summary.items()
                }
            )


def _write_dashboard_md(path: Path, a: dict, b: dict) -> None:
    delta_latency = b["latency_p95_ms"] - a["latency_p95_ms"]
    delta_cost = b["cost_mean_idr"] - a["cost_mean_idr"]
    delta_grounded = b["grounded_rate"] - a["grounded_rate"]

    content = f"""# Dashboard

    ## Experiment Setup
    - Variant A: default `top_k` (from config)
    - Variant B: `top_k=6`
    - Gold set: same file `data/gold_questions.csv`

    ## Variant A
    - Samples: {a['num_samples']}
    - BLEU mean/std: {a['bleu_mean']:.4f} / {a['bleu_std']:.4f}
    - ROUGE-L mean/std: {a['rouge_l_mean']:.4f} / {a['rouge_l_std']:.4f}
    - Embedding similarity mean/std: {a['embedding_similarity_mean']:.4f} / {a['embedding_similarity_std']:.4f}
    - Retrieval hit-rate: {a['retrieval_hit_rate']:.2%}
    - Groundedness rate: {a['grounded_rate']:.2%}
    - Refusal rate: {a['refusal_rate']:.2%}
    - Latency p50/p95: {a['latency_p50_ms']:.2f} / {a['latency_p95_ms']:.2f} ms
    - Mean cost/query: IDR {a['cost_mean_idr']:.4f}

    ## Variant B
    - Samples: {b['num_samples']}
    - BLEU mean/std: {b['bleu_mean']:.4f} / {b['bleu_std']:.4f}
    - ROUGE-L mean/std: {b['rouge_l_mean']:.4f} / {b['rouge_l_std']:.4f}
    - Embedding similarity mean/std: {b['embedding_similarity_mean']:.4f} / {b['embedding_similarity_std']:.4f}
    - Retrieval hit-rate: {b['retrieval_hit_rate']:.2%}
    - Groundedness rate: {b['grounded_rate']:.2%}
    - Refusal rate: {b['refusal_rate']:.2%}
    - Latency p50/p95: {b['latency_p50_ms']:.2f} / {b['latency_p95_ms']:.2f} ms
    - Mean cost/query: IDR {b['cost_mean_idr']:.4f}

    ## A/B Summary
    - Δ Groundedness (B-A): {delta_grounded:+.2%}
    - Δ p95 latency (B-A): {delta_latency:+.2f} ms
    - Δ mean cost/query (B-A): IDR {delta_cost:+.4f}
    - Target check (`<= IDR {TARGET_COST_IDR:.0f}/query`):
    - Variant A: {"PASS" if a["cost_mean_idr"] <= TARGET_COST_IDR else "FAIL"}
    - Variant B: {"PASS" if b["cost_mean_idr"] <= TARGET_COST_IDR else "FAIL"}
    """
    path.write_text(content, encoding="utf-8")

def _write_dashboard_png_from_md(md_path: Path, png_path: Path) -> None:
    _ = md_path  # main still passes this, but chart uses ab_comparison.csv data
    try:
        from PIL import Image, ImageDraw, ImageFont
    except Exception:
        print("Pillow not installed; skipped dashboard.png generation.")
        return

    ab_path = REPORTS_DIR / "ab_comparison.csv"
    if not ab_path.exists():
        print(f"Missing {ab_path}; skipped dashboard.png generation.")
        return

    with ab_path.open("r", encoding="utf-8", newline="") as handle:
        rows = list(csv.DictReader(handle))

    summary_by_variant = {row.get("variant", "").strip(): row for row in rows}
    if "A" not in summary_by_variant or "B" not in summary_by_variant:
        print("ab_comparison.csv must contain both variant A and B.")
        return

    a_row = summary_by_variant["A"]
    b_row = summary_by_variant["B"]

    metrics = [
        ("BLEU Mean", "bleu_mean", False),
        ("ROUGE-L Mean", "rouge_l_mean", False),
        ("Embed Sim Mean", "embedding_similarity_mean", False),
        ("Retrieval Hit Rate", "retrieval_hit_rate", True),
        ("Grounded Rate", "grounded_rate", True),
        ("Refusal Rate", "refusal_rate", True),
        ("Latency p95 (ms)", "latency_p95_ms", False),
        ("Cost Mean (IDR)", "cost_mean_idr", False),
    ]

    width = 1400
    margin = 50
    row_height = 90
    chart_width = 560
    chart_start_x = 420
    bar_height = 18
    top_pad = 110
    bottom_pad = 40
    height = top_pad + len(metrics) * row_height + bottom_pad

    try:
        title_font = ImageFont.truetype("arialbd.ttf", 34)
        label_font = ImageFont.truetype("arial.ttf", 22)
        value_font = ImageFont.truetype("arial.ttf", 18)
    except Exception:
        title_font = ImageFont.load_default()
        label_font = ImageFont.load_default()
        value_font = ImageFont.load_default()

    image = Image.new("RGB", (width, height), "white")
    draw = ImageDraw.Draw(image)

    color_a = "#2563EB"
    color_b = "#F97316"
    text_color = "#111827"
    muted = "#6B7280"
    bar_bg = "#E5E7EB"

    draw.text((margin, 26), "A/B Comparison Dashboard", fill=text_color, font=title_font)
    draw.text((margin, 70), "Variant A (blue) vs Variant B (orange)", fill=muted, font=value_font)

    for index, (label, key, as_percent) in enumerate(metrics):
        y_base = top_pad + index * row_height
        a_value = _to_float(a_row, key)
        b_value = _to_float(b_row, key)
        max_value = max(a_value, b_value, 1e-9)

        draw.text((margin, y_base + 10), label, fill=text_color, font=label_font)

        draw.rounded_rectangle(
            (chart_start_x, y_base + 14, chart_start_x + chart_width, y_base + 14 + (bar_height * 2) + 10),
            radius=7,
            fill=bar_bg,
        )

        a_bar_width = int((a_value / max_value) * chart_width)
        b_bar_width = int((b_value / max_value) * chart_width)

        draw.rounded_rectangle(
            (chart_start_x, y_base + 16, chart_start_x + a_bar_width, y_base + 16 + bar_height),
            radius=5,
            fill=color_a,
        )
        draw.rounded_rectangle(
            (chart_start_x, y_base + 16 + bar_height + 6, chart_start_x + b_bar_width, y_base + 16 + (bar_height * 2) + 6),
            radius=5,
            fill=color_b,
        )

        if as_percent:
            a_text = f"A: {a_value:.2%}"
            b_text = f"B: {b_value:.2%}"
        elif key == "latency_p95_ms":
            a_text = f"A: {a_value:.2f}"
            b_text = f"B: {b_value:.2f}"
        else:
            a_text = f"A: {a_value:.4f}"
            b_text = f"B: {b_value:.4f}"

        draw.text((chart_start_x + chart_width + 18, y_base + 16), a_text, fill=color_a, font=value_font)
        draw.text((chart_start_x + chart_width + 18, y_base + 16 + bar_height + 6), b_text, fill=color_b, font=value_font)

    png_path.parent.mkdir(parents=True, exist_ok=True)
    image.save(png_path)
    print(f"Wrote dashboard comparison chart to {png_path}")

def main() -> None:
    REPORTS_DIR.mkdir(parents=True, exist_ok=True)
    # TODO(STAGE 3): Read eval_report_A.csv and eval_report_B.csv, then write ab_comparison.csv.
    # TODO(STAGE 4): Generate dashboard.png or dashboard.md with p95 latency, cost, refusal rate, and groundedness.
    path_a = REPORTS_DIR / "eval_report_A.csv"
    path_b = REPORTS_DIR / "eval_report_B.csv"
    path_ab = REPORTS_DIR / "ab_comparison.csv"
    path_dash = REPORTS_DIR / "dashboard.md"
    path_png = REPORTS_DIR / "dashboard.png"

    rows_a = _load_rows(path_a)
    rows_b = _load_rows(path_b)

    summary_a = _aggregate(rows_a, "A")
    summary_b = _aggregate(rows_b, "B")

    _write_ab_comparison(path_ab, [summary_a, summary_b])
    _write_dashboard_md(path_dash, summary_a, summary_b)
    _write_dashboard_png_from_md(path_dash, path_png)

    print(f"Wrote placeholder dashboard to {REPORTS_DIR / 'dashboard.md'}")


if __name__ == "__main__":
    main()

