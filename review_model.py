"""Bakery-adjacent review experiment and local inference helpers.

Only review text enters a classifier. Recipe identity is used to define the
evaluation split, never as a prediction feature.
"""
from __future__ import annotations

import csv
import html
import json
import re
import unicodedata
from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path
from zipfile import ZipFile

import joblib
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import GroupShuffleSplit
from sklearn.pipeline import FeatureUnion, Pipeline
from sklearn.preprocessing import Normalizer


ROOT = Path(__file__).parent
ARTIFACTS = ROOT / "research" / "artifacts"
DATA_URL = ("https://archive.ics.uci.edu/static/public/911/"
            "recipe+reviews+and+user+feedback+dataset.zip")
DATA_SHA256 = "aff630962b32fb8e8fc43ba8eddf79c45e2ae70321e81dda383c95f04887b77f"
TITLE_RULE = re.compile(
    r"\b(?:bread|muffins?|cookies?|cupcakes?|cakes?|pies?|bars?|crisps?|"
    r"cheesecake|macaroons?|pancakes?|dessert|pudding|heavenlies|cornbread)\b",
    re.IGNORECASE,
)
TITLE_EXCLUSION = re.compile(r"\b(?:shepherd|corn pudding)\b", re.IGNORECASE)


@dataclass(frozen=True)
class Review:
    recipe_code: str
    text: str
    low_rating: int


def clean_text(value: str) -> str:
    """Apply the same fixed, label-free cleanup in training and inference."""
    return " ".join(unicodedata.normalize("NFKC", html.unescape(value)).split())


def is_bakery_title(title: str) -> bool:
    """Select bakery and dessert recipes using only the recipe title."""
    return bool(TITLE_RULE.search(title) and not TITLE_EXCLUSION.search(title))


def deduplicate(rows: list[Review]) -> tuple[list[Review], dict[str, int]]:
    """Drop conflicting text clusters, then keep one row per identical text."""
    clusters: dict[str, list[Review]] = {}
    for row in rows:
        normalized = clean_text(row.text)
        if normalized:
            clusters.setdefault(normalized.casefold(), []).append(
                Review(row.recipe_code, normalized, row.low_rating))
    kept: list[Review] = []
    conflicts = duplicates = 0
    for cluster in clusters.values():
        if len({row.low_rating for row in cluster}) > 1:
            conflicts += len(cluster)
        else:
            kept.append(cluster[0])
            duplicates += len(cluster) - 1
    return kept, {"conflicting_rows_removed": conflicts,
                  "duplicate_rows_removed": duplicates}


def load_reviews(archive: Path) -> tuple[list[Review], dict[str, int]]:
    """Read the pinned UCI CSV, retain bakery titles and rated text only."""
    counts = {"source_rows": 0, "bakery_rated_rows": 0,
              "unrated_bakery_rows": 0, "empty_text_rows": 0}
    candidate: list[Review] = []
    with ZipFile(archive) as bundle:
        names = bundle.namelist()
        if len(names) != 1 or not names[0].endswith(".csv"):
            raise ValueError("Unexpected UCI archive contents")
        with bundle.open(names[0]) as raw:
            import io
            reader = csv.DictReader(io.TextIOWrapper(raw, encoding="utf-8-sig", newline=""))
            required = {"recipe_code", "recipe_name", "stars", "text"}
            if not required.issubset(reader.fieldnames or []):
                raise ValueError("UCI CSV is missing required columns")
            for row in reader:
                counts["source_rows"] += 1
                if not is_bakery_title(row["recipe_name"]):
                    continue
                stars = int(row["stars"])
                if stars == 0:
                    counts["unrated_bakery_rows"] += 1
                    continue
                if stars not in range(1, 6):
                    raise ValueError("Unexpected star rating")
                counts["bakery_rated_rows"] += 1
                review = clean_text(row["text"] or "")
                if not review or not any(ch.isalpha() for ch in review):
                    counts["empty_text_rows"] += 1
                    continue
                candidate.append(Review(row["recipe_code"], review, int(stars <= 3)))
    unique, removed = deduplicate(candidate)
    counts.update(removed)
    counts["usable_rows"] = len(unique)
    counts["recipes"] = len({row.recipe_code for row in unique})
    return unique, counts


def split_reviews(rows: list[Review]) -> dict[str, list[int]]:
    """Freeze recipe-disjoint partitions with seeds 42 and 43."""
    if len({row.recipe_code for row in rows}) < 12:
        raise ValueError("At least 12 recipes are needed for grouped evaluation")
    if len({clean_text(row.text).casefold() for row in rows}) != len(rows):
        raise ValueError("Deduplicate normalized text before splitting")
    indices = np.arange(len(rows))
    groups = np.array([row.recipe_code for row in rows])
    first = GroupShuffleSplit(n_splits=1, test_size=0.16, random_state=42)
    trainval, test = next(first.split(indices, groups=groups))
    second = GroupShuffleSplit(n_splits=1, test_size=0.18, random_state=43)
    train_relative, validation_relative = next(
        second.split(trainval, groups=groups[trainval]))
    return {"train": trainval[train_relative].tolist(),
            "validation": trainval[validation_relative].tolist(),
            "test": test.tolist()}


def build_model(kind: str) -> Pipeline:
    """Hold classifier settings fixed; expanded adds character features only."""
    word = TfidfVectorizer(min_df=2, ngram_range=(1, 1),
                           strip_accents="unicode", sublinear_tf=True)
    if kind == "baseline":
        features = word
    elif kind == "expanded":
        character = TfidfVectorizer(analyzer="char_wb", ngram_range=(3, 5),
                                    min_df=2, strip_accents="unicode",
                                    sublinear_tf=True)
        features = FeatureUnion([("word", word), ("character", character)])
    else:
        raise ValueError(f"Unknown model kind: {kind}")
    return Pipeline([
        ("features", features),
        ("row_norm", Normalizer(norm="l2")),
        ("classifier", LogisticRegression(
            C=1.0, class_weight="balanced", solver="liblinear",
            max_iter=2000, random_state=42)),
    ])


@lru_cache(maxsize=1)
def study_bundle() -> tuple[dict[str, Pipeline], dict]:
    """Load only trusted, checked-in local artifacts; never user uploads."""
    report = json.loads((ARTIFACTS / "results.json").read_text(encoding="utf-8"))
    models = {kind: joblib.load(ARTIFACTS / f"{kind}.joblib")
              for kind in ("baseline", "expanded")}
    return models, report


def public_study() -> dict:
    """Return the source, protocol, splits and measured results to the UI."""
    return study_bundle()[1]


def classify_review(value: str) -> dict:
    """Triage English review text without changing the bakery forecast."""
    if not isinstance(value, str):
        raise ValueError("Пікір мәтінін енгізіңіз.")
    text = clean_text(value)
    if len(text) > 2000:
        raise ValueError("Пікір 2000 таңбадан аспауы керек.")
    if len(re.findall(r"[A-Za-z]{2,}", text)) < 3:
        raise ValueError("Кемінде үш ағылшын сөзінен тұратын пікір енгізіңіз.")
    models, report = study_bundle()
    candidates = {}
    for kind, model in models.items():
        score = float(model.predict_proba([text])[0, 1])
        threshold = float(report["models"][kind]["validation"]["threshold"])
        candidates[kind] = {
            "label": "low_rating" if score >= threshold else "positive",
            "low_rating_score": round(score, 4), "threshold": threshold,
        }
    selected = report["deployment"]["model"]
    return {"label": candidates[selected]["label"], "model": selected,
            "candidates": candidates,
            "caution": "English recipe-review proxy; not bakery demand or verified customer sentiment."}
