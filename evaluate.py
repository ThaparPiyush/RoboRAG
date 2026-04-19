"""
Evaluation script for RoboRAG.

Runs the RAG pipeline against a benchmark set of Q&A pairs and reports:
  - ROUGE-1, ROUGE-2, ROUGE-L
  - Token-level F1
  - Retrieval Precision@K
  - Average latency
  - Peak memory usage

Also runs a *no-RAG baseline* (GPT-4o-mini without retrieval) for comparison.

Usage:
    python evaluate.py                         # full evaluation
    python evaluate.py --no-baseline           # skip the no-RAG comparison
    python evaluate.py --qa eval/qa_pairs.json # custom QA file
"""

import argparse
import json
import os
import time
from collections import defaultdict

import psutil
from dotenv import load_dotenv
from rouge_score import rouge_scorer

import config

load_dotenv()

RESULTS_DIR = os.path.join(os.path.dirname(__file__), "eval", "results")
CHECKPOINT_PATH = os.path.join(RESULTS_DIR, "_checkpoint.json")


# ── Helpers ──────────────────────────────────────────────────────────────────

def token_f1(prediction: str, reference: str) -> float:
    pred_tokens = prediction.lower().split()
    ref_tokens = reference.lower().split()
    common = set(pred_tokens) & set(ref_tokens)
    if not common:
        return 0.0
    precision = len(common) / len(pred_tokens)
    recall = len(common) / len(ref_tokens)
    return 2 * precision * recall / (precision + recall)


def retrieval_precision(source_docs, relevant_keywords: list[str]) -> float:
    """Estimate precision@K by checking if any relevant keyword appears
    in each retrieved chunk."""
    if not relevant_keywords or not source_docs:
        return 0.0
    hits = 0
    for doc in source_docs:
        text_lower = doc.page_content.lower()
        if any(kw.lower() in text_lower for kw in relevant_keywords):
            hits += 1
    return hits / len(source_docs)


def _call_with_retry(fn, *args, max_retries=3, **kwargs):
    """Call *fn* with exponential backoff on rate-limit errors."""
    for attempt in range(max_retries):
        try:
            return fn(*args, **kwargs)
        except Exception as e:
            if ("429" in str(e) or "rate" in str(e).lower()) and attempt < max_retries - 1:
                wait = 30 * (attempt + 1)
                print(f"       Rate-limited. Waiting {wait}s (attempt {attempt+1}/{max_retries}) …")
                time.sleep(wait)
            else:
                raise


# ── Baseline: GPT-4o-mini without retrieval ──────────────────────────────────

def ask_llm_no_rag(question: str) -> str:
    from langchain_openai import ChatOpenAI

    llm = ChatOpenAI(
        model=config.LLM_MODEL,
        temperature=config.LLM_TEMPERATURE,
        max_tokens=config.LLM_MAX_OUTPUT_TOKENS,
    )
    response = llm.invoke(question)
    return response.content


# ── Main evaluation ──────────────────────────────────────────────────────────

def run_evaluation(qa_path: str, run_baseline: bool = True):
    from rag_chain import build_rag_chain

    with open(qa_path, encoding="utf-8") as f:
        qa_pairs = json.load(f)

    chain, retriever = build_rag_chain()
    scorer = rouge_scorer.RougeScorer(["rouge1", "rouge2", "rougeL"], use_stemmer=True)

    rag_metrics: dict[str, list] = defaultdict(list)
    baseline_metrics: dict[str, list] = defaultdict(list)
    per_question: list[dict] = []
    process = psutil.Process(os.getpid())

    os.makedirs(RESULTS_DIR, exist_ok=True)

    # Resume from checkpoint if available
    start_idx = 0
    if os.path.exists(CHECKPOINT_PATH):
        with open(CHECKPOINT_PATH) as f:
            ckpt = json.load(f)
        per_question = ckpt.get("per_question", [])
        start_idx = len(per_question)
        for pq in per_question:
            for k in ("rouge1", "rouge2", "rougeL", "f1", "precision_at_k", "latency"):
                rag_metrics[k].append(pq["rag"][k])
            if "baseline" in pq and pq["baseline"]:
                for k in ("rouge1", "rouge2", "rougeL", "f1", "latency"):
                    baseline_metrics[k].append(pq["baseline"][k])
        print(f"Resumed from checkpoint — skipping first {start_idx} questions.\n")

    print(f"Evaluating {len(qa_pairs)} questions ({start_idx} already done) …\n")
    print(f"{'#':<4} {'ROUGE-1':>8} {'ROUGE-L':>8} {'F1':>8} {'P@K':>8} {'Latency':>8}")
    print("-" * 52)

    for idx, pair in enumerate(qa_pairs):
        if idx < start_idx:
            continue

        question = pair["question"]
        reference = pair["reference_answer"]
        keywords = pair.get("relevant_keywords", [])
        qresult: dict = {"question": question}

        # --- RAG ---
        try:
            t0 = time.time()
            source_docs = _call_with_retry(retriever.invoke, question)
            answer = _call_with_retry(chain.invoke, question)
            latency = time.time() - t0
        except Exception as e:
            print(f"{idx+1:<4} SKIPPED (error): {e!s:.80s}")
            _save_checkpoint(per_question, rag_metrics, baseline_metrics, process, len(qa_pairs))
            print(f"\n  Stopped at question {idx+1}. Run again later to resume.")
            break

        scores = scorer.score(reference, answer)
        f1 = token_f1(answer, reference)
        pk = retrieval_precision(source_docs, keywords)

        rag_metrics["rouge1"].append(scores["rouge1"].fmeasure)
        rag_metrics["rouge2"].append(scores["rouge2"].fmeasure)
        rag_metrics["rougeL"].append(scores["rougeL"].fmeasure)
        rag_metrics["f1"].append(f1)
        rag_metrics["precision_at_k"].append(pk)
        rag_metrics["latency"].append(latency)

        qresult["rag"] = {
            "rouge1": scores["rouge1"].fmeasure,
            "rouge2": scores["rouge2"].fmeasure,
            "rougeL": scores["rougeL"].fmeasure,
            "f1": f1,
            "precision_at_k": pk,
            "latency": latency,
        }

        print(
            f"{idx+1:<4} "
            f"{scores['rouge1'].fmeasure:>8.3f} "
            f"{scores['rougeL'].fmeasure:>8.3f} "
            f"{f1:>8.3f} "
            f"{pk:>8.2f} "
            f"{latency:>7.1f}s"
        )

        # --- Baseline (no RAG) ---
        if run_baseline:
            try:
                t0 = time.time()
                bl_answer = _call_with_retry(ask_llm_no_rag, question)
                bl_latency = time.time() - t0
                bl_scores = scorer.score(reference, bl_answer)
                bl_f1 = token_f1(bl_answer, reference)
                baseline_metrics["rouge1"].append(bl_scores["rouge1"].fmeasure)
                baseline_metrics["rouge2"].append(bl_scores["rouge2"].fmeasure)
                baseline_metrics["rougeL"].append(bl_scores["rougeL"].fmeasure)
                baseline_metrics["f1"].append(bl_f1)
                baseline_metrics["latency"].append(bl_latency)
                qresult["baseline"] = {
                    "rouge1": bl_scores["rouge1"].fmeasure,
                    "rouge2": bl_scores["rouge2"].fmeasure,
                    "rougeL": bl_scores["rougeL"].fmeasure,
                    "f1": bl_f1,
                    "latency": bl_latency,
                }
            except Exception:
                qresult["baseline"] = None

        per_question.append(qresult)
        _save_checkpoint(per_question, rag_metrics, baseline_metrics, process, len(qa_pairs))

    _print_and_save_summary(rag_metrics, baseline_metrics, process, per_question, len(qa_pairs))


def _save_checkpoint(per_question, rag_metrics, baseline_metrics, process, total):
    os.makedirs(RESULTS_DIR, exist_ok=True)
    with open(CHECKPOINT_PATH, "w") as f:
        json.dump({"per_question": per_question, "total": total}, f, indent=2)


def _print_and_save_summary(rag_metrics, baseline_metrics, process, per_question, total_questions):
    mem_mb = process.memory_info().rss / 1024 / 1024

    def avg(lst):
        return sum(lst) / len(lst) if lst else 0.0

    evaluated = len(per_question)

    print("\n" + "=" * 60)
    print(f"SUMMARY — RAG (RoboRAG)  [{evaluated}/{total_questions} questions]")
    print("=" * 60)
    print(f"  ROUGE-1          : {avg(rag_metrics['rouge1']):.4f}")
    print(f"  ROUGE-2          : {avg(rag_metrics['rouge2']):.4f}")
    print(f"  ROUGE-L          : {avg(rag_metrics['rougeL']):.4f}")
    print(f"  Token F1         : {avg(rag_metrics['f1']):.4f}")
    print(f"  Precision@{config.TOP_K}      : {avg(rag_metrics['precision_at_k']):.4f}")
    print(f"  Avg latency      : {avg(rag_metrics['latency']):.2f}s")
    print(f"  Peak memory      : {mem_mb:.1f} MB")

    if baseline_metrics and baseline_metrics.get("rouge1"):
        print("\n" + "=" * 60)
        print(f"SUMMARY — Baseline (GPT-4o-mini without RAG)  [{len(baseline_metrics['rouge1'])}/{total_questions}]")
        print("=" * 60)
        print(f"  ROUGE-1          : {avg(baseline_metrics['rouge1']):.4f}")
        print(f"  ROUGE-2          : {avg(baseline_metrics['rouge2']):.4f}")
        print(f"  ROUGE-L          : {avg(baseline_metrics['rougeL']):.4f}")
        print(f"  Token F1         : {avg(baseline_metrics['f1']):.4f}")
        print(f"  Avg latency      : {avg(baseline_metrics['latency']):.2f}s")

        r1_delta = avg(rag_metrics["rouge1"]) - avg(baseline_metrics["rouge1"])
        f1_delta = avg(rag_metrics["f1"]) - avg(baseline_metrics["f1"])
        print(f"\n  RAG improvement (ROUGE-1): {r1_delta:+.4f}")
        print(f"  RAG improvement (F1):      {f1_delta:+.4f}")

    results = {
        "rag": {k: round(avg(v), 4) for k, v in rag_metrics.items()},
        "baseline": {k: round(avg(v), 4) for k, v in baseline_metrics.items()} if baseline_metrics.get("rouge1") else None,
        "peak_memory_mb": round(mem_mb, 1),
        "num_questions_evaluated": evaluated,
        "num_questions_total": total_questions,
        "per_question": per_question,
    }
    out_path = os.path.join(RESULTS_DIR, "eval_results.json")
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2)
    print(f"\nResults saved to {out_path}")

    if evaluated >= total_questions and os.path.exists(CHECKPOINT_PATH):
        os.remove(CHECKPOINT_PATH)


# ── CLI ──────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Evaluate RoboRAG")
    parser.add_argument(
        "--qa",
        default=os.path.join(os.path.dirname(__file__), "eval", "qa_pairs.json"),
        help="Path to the Q&A benchmark JSON file.",
    )
    parser.add_argument("--no-baseline", action="store_true", help="Skip the no-RAG baseline.")
    args = parser.parse_args()
    run_evaluation(args.qa, run_baseline=not args.no_baseline)
