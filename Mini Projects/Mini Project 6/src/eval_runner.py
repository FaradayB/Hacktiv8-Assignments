import argparse
import csv
import time
from pathlib import Path

from src.config import settings
from src.costing import estimate_cost_idr
from src.generator import build_context, get_generator
from src.metrics import bleu_like, embedding_similarity_like, rouge_l
from src.retriever import LocalRetriever
from src.safety import check_safety
from src.text_utils import estimate_tokens


REPORTS_DIR = Path("reports")

def _to_bool(value: str) -> bool:
    return str(value).strip().lower() in {"true", "1", "yes"}


def _is_grounded(answer: str, retrieved_chunks: list, threshold: float = 0.15) -> bool:
    if not answer.strip() or not retrieved_chunks:
        return False
    context_text = " ".join(chunk.text for chunk in retrieved_chunks)
    return embedding_similarity_like(context_text, answer) >= threshold

def run_eval(variant: str, top_k: int | None = None) -> Path:
    # TODO(STAGE 2): Read data/gold_questions.csv.
    # TODO(STAGE 2): Call the same safety + retrieval + generator pipeline used by /chat.
    # TODO(STAGE 2): Compute quality, retrieval, groundedness, latency, and cost metrics.
    # TODO(STAGE 3): Respect variant and top_k so A/B compares one changed variable.
    retriever = LocalRetriever()
    generator = get_generator()

    gold_path = settings.data_path / "gold_questions.csv"
    k = top_k if top_k is not None else settings.top_k

    REPORTS_DIR.mkdir(parents=True, exist_ok=True)
    output_path = REPORTS_DIR / f"eval_report_{variant}.csv"

    with gold_path.open("r", encoding="utf-8-sig", newline="") as in_handle, \
         output_path.open("w", encoding="utf-8", newline="") as out_handle:
        reader = csv.DictReader(in_handle)
        writer = csv.DictWriter(
            out_handle,
            fieldnames=[
                "question_id",
                "variant",
                "status",
                "bleu",
                "rouge_l",
                "embedding_similarity",
                "retrieval_hit",
                "grounded",
                "refusal",
                "latency_ms",
                "cost_idr",
            ],
        )
        writer.writeheader()

        for row in reader:
            query = row["query"]
            expected_answer = row.get("expected_answer", "")
            expected_source = row.get("expected_source", "")
            expected_refusal = _to_bool(row.get("expected_refusal", "false"))

            started = time.perf_counter()
            safety = check_safety(query)

            if not safety["allowed"]:
                latency_ms = int((time.perf_counter() - started) * 1000)
                refusal = True
                status = "refused"
                answer = ""
                retrieved = []
                cost_idr = 0.0
                bleu = 0.0
                rouge = 0.0
                similarity = 0.0
                retrieval_hit = int(expected_refusal)
                grounded = 0
            else:
                retrieved = retriever.search(query, top_k=k)
                answer = generator.generate(query, retrieved)
                latency_ms = int((time.perf_counter() - started) * 1000)

                context = build_context(retrieved)
                input_tokens = estimate_tokens(query + "\n" + context)
                output_tokens = estimate_tokens(answer)
                cost_idr = estimate_cost_idr(input_tokens, output_tokens)

                refusal = False
                status = "ok"

                bleu = bleu_like(expected_answer, answer)
                rouge = rouge_l(expected_answer, answer)
                similarity = embedding_similarity_like(expected_answer, answer)

                source_names = {chunk.filename for chunk in retrieved}
                retrieval_hit = int((not expected_refusal) and expected_source in source_names)
                grounded = int(_is_grounded(answer, retrieved))

            writer.writerow(
                {
                    "question_id": row["question_id"],
                    "variant": variant,
                    "status": status,
                    "bleu": round(bleu, 4),
                    "rouge_l": round(rouge, 4),
                    "embedding_similarity": round(similarity, 4),
                    "retrieval_hit": retrieval_hit,
                    "grounded": grounded,
                    "refusal": refusal,
                    "latency_ms": latency_ms,
                    "cost_idr": round(float(cost_idr), 4),
                }
            )

    print(f"Wrote eval report to {output_path}")
    return output_path


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--variant", default="A")
    parser.add_argument("--top-k", type=int, default=None)
    args = parser.parse_args()
    _ = settings
    run_eval(args.variant, args.top_k)


if __name__ == "__main__":
    main()

