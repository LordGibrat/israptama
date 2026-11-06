"""Reproduce the UCI recipe-review experiment and checked-in demo artifact.

Run from the repository root: python research/run_experiment.py
Use --check to retrain and compare the checked-in results without overwriting them.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import sys
from pathlib import Path
from urllib.request import urlopen

import joblib
import numpy as np
import sklearn
from sklearn.metrics import (accuracy_score, average_precision_score,
                             balanced_accuracy_score, confusion_matrix, f1_score,
                             precision_recall_curve,
                             precision_recall_fscore_support)

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from review_model import (ARTIFACTS, DATA_SHA256, DATA_URL, TITLE_EXCLUSION,
                          TITLE_RULE, Review, build_model, load_reviews,
                          split_reviews)


CACHE = Path(__file__).parent / "cache" / "recipe_reviews.zip"


def ensure_archive() -> Path:
    """Download once, then refuse bytes that differ from the declared source."""
    CACHE.parent.mkdir(parents=True, exist_ok=True)
    if not CACHE.exists():
        temporary = CACHE.with_suffix(".download")
        try:
            with urlopen(DATA_URL, timeout=60) as response, temporary.open("wb") as target:
                while chunk := response.read(1024 * 1024):
                    target.write(chunk)
            temporary.replace(CACHE)
        finally:
            temporary.unlink(missing_ok=True)
    digest = hashlib.sha256(CACHE.read_bytes()).hexdigest()
    if digest != DATA_SHA256:
        raise ValueError(f"UCI archive checksum mismatch: {digest}")
    return CACHE


def choose_threshold(labels: np.ndarray, scores: np.ndarray) -> float:
    """Maximize validation low-rating F1; break ties by higher threshold."""
    precision, recall, thresholds = precision_recall_curve(labels, scores)
    f1 = 2 * precision[:-1] * recall[:-1] / np.maximum(
        precision[:-1] + recall[:-1], 1e-15)
    winners = np.flatnonzero(np.isclose(f1, f1.max(), rtol=0, atol=1e-12))
    return float(thresholds[winners[-1]])


def metrics(labels: np.ndarray, scores: np.ndarray, threshold: float) -> dict:
    predicted = (scores >= threshold).astype(int)
    precision, recall, f1, support = precision_recall_fscore_support(
        labels, predicted, labels=[0, 1], zero_division=0)
    matrix = confusion_matrix(labels, predicted, labels=[0, 1]).tolist()
    return {
        "threshold": round(threshold, 8),
        "accuracy": round(float(accuracy_score(labels, predicted)), 6),
        "balanced_accuracy": round(float(balanced_accuracy_score(labels, predicted)), 6),
        "low_rating_precision": round(float(precision[1]), 6),
        "low_rating_recall": round(float(recall[1]), 6),
        "low_rating_f1": round(float(f1[1]), 6),
        "low_rating_support": int(support[1]),
        "average_precision": round(float(average_precision_score(labels, scores)), 6),
        "prevalence_reference": round(float(np.mean(labels)), 6),
        "confusion_matrix_0_positive_1_low": matrix,
    }


def split_summary(rows: list[Review], indices: list[int]) -> dict:
    subset = [rows[i] for i in indices]
    minority = sum(row.low_rating for row in subset)
    return {"rows": len(subset), "recipes": len({r.recipe_code for r in subset}),
            "positive_4_or_5": len(subset) - minority, "low_1_to_3": minority,
            "low_prevalence": round(minority / len(subset), 6),
            "recipe_codes": sorted({r.recipe_code for r in subset})}


def bootstrap_delta(rows: list[Review], indices: list[int],
                    labels: np.ndarray, baseline_scores: np.ndarray,
                    expanded_scores: np.ndarray, thresholds: dict[str, float]) -> dict:
    """Recipe-cluster bootstrap for expanded minus baseline test F1."""
    group = np.array([rows[i].recipe_code for i in indices])
    recipes = np.unique(group)
    rng = np.random.default_rng(2026)
    deltas = []
    for _ in range(2000):
        drawn = rng.choice(recipes, size=len(recipes), replace=True)
        sample = np.concatenate([np.flatnonzero(group == recipe) for recipe in drawn])
        values = []
        for kind, scores in (("baseline", baseline_scores),
                             ("expanded", expanded_scores)):
            prediction = scores[sample] >= thresholds[kind]
            _, _, f1, _ = precision_recall_fscore_support(
                labels[sample], prediction, labels=[0, 1], zero_division=0)
            values.append(float(f1[1]))
        deltas.append(values[1] - values[0])
    return {"method": "2000 recipe-cluster resamples; expanded minus baseline low-rating F1",
            "seed": 2026, "lower_95": round(float(np.quantile(deltas, 0.025)), 6),
            "upper_95": round(float(np.quantile(deltas, 0.975)), 6)}


def run() -> tuple[dict, dict, list[dict]]:
    archive = ensure_archive()
    rows, cleaning = load_reviews(archive)
    parts = split_reviews(rows)
    split_info = {name: split_summary(rows, ids) for name, ids in parts.items()}
    for name, info in split_info.items():
        if min(info["positive_4_or_5"], info["low_1_to_3"]) == 0:
            raise ValueError(f"The frozen {name} split has only one label")
    # Both arms see identical rows. Text normalization and both TF-IDF fits are
    # inside the training boundary. Recipe titles, user IDs and stars are absent.
    texts = {name: [rows[i].text for i in ids] for name, ids in parts.items()}
    labels = {name: np.array([rows[i].low_rating for i in ids], dtype=int)
              for name, ids in parts.items()}
    fitted = {}
    scores = {}
    thresholds = {}
    evaluated = {}
    for kind in ("baseline", "expanded"):
        model = build_model(kind)
        model.fit(texts["train"], labels["train"])
        fitted[kind] = model
        scores[kind] = {"validation": model.predict_proba(texts["validation"])[:, 1]}
        thresholds[kind] = choose_threshold(labels["validation"],
                                            scores[kind]["validation"])
        evaluated[kind] = {
            "validation": metrics(labels["validation"],
                                  scores[kind]["validation"], thresholds[kind])}
    # Deployment choice is made by validation F1 alone; a tie favors simplicity.
    validation_f1 = {
        kind: f1_score(labels["validation"],
                       scores[kind]["validation"] >= thresholds[kind])
        for kind in ("baseline", "expanded")
    }
    selected = ("expanded" if validation_f1["expanded"] > validation_f1["baseline"]
                else "baseline")
    # The final test is opened only after the threshold and deployment choice.
    for kind in ("baseline", "expanded"):
        scores[kind]["test"] = fitted[kind].predict_proba(texts["test"])[:, 1]
        evaluated[kind]["test"] = metrics(labels["test"], scores[kind]["test"],
                                          thresholds[kind])
    results = {
        "study": "English recipe-review low-rating prediction for bakery feedback triage",
        "dataset": {"name": "UCI Recipe Reviews and User Feedback",
                    "url": "https://archive.ics.uci.edu/dataset/911/recipe+reviews+and+user+feedback+dataset",
                    "doi": "10.24432/C5FG95", "license": "CC BY 4.0",
                    "archive_sha256": DATA_SHA256,
                    "title_rule": TITLE_RULE.pattern,
                    "title_exclusion": TITLE_EXCLUSION.pattern},
        "protocol": {"labels": "1-3 stars = low rating; 4-5 = positive; 0 excluded",
                     "input": "review text only; no recipe title/code, star, user or engagement fields",
                     "split": "recipe-disjoint GroupShuffleSplit; test 16% seed 42, then validation 18% of remainder seed 43",
                     "selection": "validation minority F1; threshold maximizes validation minority F1, ties choose highest threshold; deployment tie chooses baseline",
                     "controlled_change": "add character_wb 3-5 gram TF-IDF to word unigram TF-IDF; identical logistic regression and row L2 norm",
                     "test_policy": "one frozen test evaluation after validation selection"},
        "cleaning": cleaning,
        "splits": split_info,
        "models": evaluated,
        "deployment": {"model": selected,
                       "threshold": round(thresholds[selected], 8)},
        "uncertainty": bootstrap_delta(
            rows, parts["test"], labels["test"],
            scores["baseline"]["test"], scores["expanded"]["test"], thresholds),
        "versions": {"numpy": np.__version__, "scikit_learn": sklearn.__version__},
        "limitations": [
            "Recipe comments are a proxy, not bakery customer transactions or demand.",
            "The corpus is English and does not validate Kazakh-language inference.",
            "Stars are weak, imbalanced labels; 1-3 does not prove a complaint.",
            "Only a small number of held-out recipes support the test estimate.",
            "No business uplift or planning benefit is established by this classifier.",
        ],
    }
    predictions = []
    for position, index in enumerate(parts["test"]):
        row = rows[index]
        predictions.append({
            "recipe_code": row.recipe_code,
            "text_sha256": hashlib.sha256(row.text.casefold().encode()).hexdigest(),
            "low_rating_true": row.low_rating,
            "baseline_score": round(float(scores["baseline"]["test"][position]), 8),
            "expanded_score": round(float(scores["expanded"]["test"][position]), 8),
        })
    return results, fitted, predictions


def check(existing: dict, current: dict) -> None:
    """Allow floating-point drift across CPUs but require stable conclusions."""
    for key in ("cleaning", "splits", "deployment", "versions", "uncertainty"):
        if existing[key] != current[key]:
            raise SystemExit(f"Reproduction failed: {key} changed")
    for kind in ("baseline", "expanded"):
        for phase in ("validation", "test"):
            before, after = existing["models"][kind][phase], current["models"][kind][phase]
            for key in before:
                if key == "confusion_matrix_0_positive_1_low":
                    if before[key] != after[key]:
                        raise SystemExit(f"Reproduction failed: {kind}/{phase}/{key}")
                elif abs(before[key] - after[key]) > 1e-5:
                    raise SystemExit(f"Reproduction failed: {kind}/{phase}/{key}")


def check_artifacts(models: dict, predictions: list[dict]) -> None:
    """Confirm saved models and row-level test scores match a fresh training run."""
    rows, _ = load_reviews(ensure_archive())
    test = split_reviews(rows)["test"]
    texts = [rows[index].text for index in test]
    for kind, current in models.items():
        saved = joblib.load(ARTIFACTS / f"{kind}.joblib")
        if not np.allclose(saved.predict_proba(texts), current.predict_proba(texts),
                           rtol=0, atol=1e-8):
            raise SystemExit(f"Reproduction failed: saved {kind} model changed")
    with (ARTIFACTS / "test_predictions.csv").open(encoding="utf-8", newline="") as stream:
        recorded = list(csv.DictReader(stream))
    if len(recorded) != len(predictions):
        raise SystemExit("Reproduction failed: prediction row count changed")
    for before, after in zip(recorded, predictions):
        for key in ("recipe_code", "text_sha256", "low_rating_true"):
            if str(before[key]) != str(after[key]):
                raise SystemExit(f"Reproduction failed: prediction {key} changed")
        for key in ("baseline_score", "expanded_score"):
            if abs(float(before[key]) - after[key]) > 1e-8:
                raise SystemExit(f"Reproduction failed: prediction {key} changed")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true", help="retrain and compare the checked-in result")
    args = parser.parse_args()
    results, models, predictions = run()
    report_path = ARTIFACTS / "results.json"
    if args.check:
        check(json.loads(report_path.read_text(encoding="utf-8")), results)
        check_artifacts(models, predictions)
        print("Reproduction PASS: split, model selection and metrics agree")
        return
    ARTIFACTS.mkdir(parents=True, exist_ok=True)
    report_path.write_text(json.dumps(results, indent=2, ensure_ascii=False) + "\n",
                           encoding="utf-8")
    for kind, model in models.items():
        joblib.dump(model, ARTIFACTS / f"{kind}.joblib", compress=3)
    with (ARTIFACTS / "test_predictions.csv").open("w", encoding="utf-8", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=list(predictions[0]))
        writer.writeheader()
        writer.writerows(predictions)
    print(json.dumps({"splits": results["splits"], "models": results["models"],
                      "deployment": results["deployment"]}, indent=2))


if __name__ == "__main__":
    main()
