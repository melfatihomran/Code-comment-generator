"""
Evaluation utilities for the Code Comment Generation project.

Metrics:
  - BLEU       : n-gram precision, standard for seq2seq generation tasks
  - ROUGE-L    : longest common subsequence overlap, good for summarization
  - Exact Match: strict sanity check (rare to be high, useful as a floor)

Usage (inside a Kaggle notebook with internet access):
    import evaluate
    bleu = evaluate.load("bleu")
    rouge = evaluate.load("rouge")
    metrics = compute_metrics(predictions, references, bleu, rouge)
"""

from typing import Dict, List


def exact_match(predictions: List[str], references: List[str]) -> float:
    assert len(predictions) == len(references)
    if not predictions:
        return 0.0
    matches = sum(
        p.strip().lower() == r.strip().lower()
        for p, r in zip(predictions, references)
    )
    return matches / len(predictions)


def compute_metrics(
    predictions: List[str],
    references: List[str],
    bleu_metric,
    rouge_metric,
) -> Dict[str, float]:
    """
    predictions: list[str] generated comments
    references:  list[str] ground-truth comments
    bleu_metric / rouge_metric: loaded via `evaluate.load("bleu")` / `evaluate.load("rouge")`
    """
    # sacrebleu-style BLEU via `evaluate` expects references as list[list[str]]
    bleu_score = bleu_metric.compute(
        predictions=predictions,
        references=[[r] for r in references],
    )
    rouge_score = rouge_metric.compute(
        predictions=predictions,
        references=references,
    )
    return {
        "bleu": round(bleu_score["bleu"] * 100, 2),
        "rouge1": round(rouge_score["rouge1"] * 100, 2),
        "rouge2": round(rouge_score["rouge2"] * 100, 2),
        "rougeL": round(rouge_score["rougeL"] * 100, 2),
        "exact_match": round(exact_match(predictions, references) * 100, 2),
        "n_examples": len(predictions),
    }


def qualitative_samples(
    codes: List[str],
    predictions: List[str],
    references: List[str],
    n: int = 10,
) -> List[Dict[str, str]]:
    """Build a list of side-by-side examples for a markdown/README table."""
    samples = []
    for code, pred, ref in list(zip(codes, predictions, references))[:n]:
        samples.append({
            "code": code.strip()[:300],
            "predicted": pred.strip(),
            "reference": ref.strip(),
        })
    return samples


def format_samples_markdown(samples: List[Dict[str, str]]) -> str:
    lines = ["| Code (truncated) | Predicted Comment | Reference Comment |",
             "|---|---|---|"]
    for s in samples:
        code = s["code"].replace("\n", " ").replace("|", "\\|")
        pred = s["predicted"].replace("\n", " ").replace("|", "\\|")
        ref = s["reference"].replace("\n", " ").replace("|", "\\|")
        lines.append(f"| `{code}` | {pred} | {ref} |")
    return "\n".join(lines)
