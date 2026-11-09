# Recipe-review NLP study — Assignment #2, Option A

## Research question and role in Israptama

Can a text-only model flag **low-rated English recipe reviews (1–3 stars)** among feedback on bakery-like products? The dashboard lets a person paste a review, see two model outputs, and compare their held-out results. This is a separate qualitative feedback signal. It does **not** alter the daily production forecast or establish customer demand.

The open dataset is [UCI Recipe Reviews and User Feedback](https://archive.ics.uci.edu/dataset/911/recipe+reviews+and+user+feedback+dataset), by Ali, Matuszewski and Czupyt (2023), [DOI: 10.24432/C5FG95](https://doi.org/10.24432/C5FG95), licensed **CC BY 4.0**. The experiment downloads UCI's 2.1 MB archive; no third-party review text is committed to this repository. The archive is pinned to SHA-256 `aff630962b32fb8e8fc43ba8eddf79c45e2ae70321e81dda383c95f04887b77f` so an upstream change cannot silently change the experiment.

## Frozen protocol

1. Select bakery-like recipe titles with the fixed title rule in `review_model.py`. This includes breads, cakes, pies, cookies, muffins, bars and related desserts. Exclude the two clearly savory title matches, shepherd's pie and corn pudding. This rule uses **title only before any model result**. Title is never a prediction feature.
2. Keep ratings 1–5 and nonempty review text. Rating 0 means unrated and is excluded. Define 1–3 as *low rating* and 4–5 as *positive*. These are rating-derived labels, not verified complaints or sentiment annotations.
3. Decode HTML entities, normalize Unicode and whitespace, and case-fold for duplicate detection. Remove an entire normalized-text cluster if its binary labels conflict; otherwise keep one copy. This happens **before** splitting, so identical text cannot cross partitions.
4. Split by `recipe_code` with `GroupShuffleSplit`: test uses 16% of recipe groups with seed 42; validation uses 18% of the remainder with seed 43. `results.json` records every group in each partition. No recipe occurs in more than one partition. The vectorizers are fit **only** on training comments. Stars, recipe title/code, author identity, timestamps, votes and ranking fields never enter either model.
5. Baseline: word unigram TF-IDF (`min_df=2`, Unicode accent stripping, sublinear term frequency) followed by row L2 normalization and class-weighted logistic regression (`C=1`, `liblinear`, `max_iter=2000`, seed 42). Expanded candidate: **add** character-within-word 3–5-gram TF-IDF (`min_df=2`) to those same word features. Its row is L2-normalized after concatenation. Classifier, weights, settings, train rows and evaluation are identical. This isolates one meaningful representation change.
6. Choose each decision threshold on validation comments to maximize low-rating F1; ties use the higher threshold. Choose the deployed model by validation F1; ties favor the baseline. Only then evaluate the fixed test. Later reruns check reproducibility and never change model selection. The live dashboard exposes both candidates, while the validation-selected model supplies the headline decision.

### Dataset and partitions

| Stage | Reviews | Recipes | Low 1–3 stars | Positive 4–5 stars |
|---|---:|---:|---:|---:|
| UCI source | 18,182 | 100 | — | — |
| Bakery titles with ratings | 6,038 | 38 | — | — |
| After cleaning and deduplication | 5,984 | 38 | 400 | 5,584 |
| Train | 4,011 | 25 | 253 | 3,758 |
| Validation | 799 | 6 | 74 | 725 |
| Untouched test | 1,174 | 7 | 73 | 1,101 |

Among bakery titles, 773 unrated rows were excluded. Four rated rows lacked usable text; six rows from conflicting-label duplicate clusters and 44 same-label duplicates were removed. The test low-rating prevalence is 73/1,174 = **6.2%**; an uninformed ranking has average precision near 0.062.

## Measured results

All test figures use the **validation-selected thresholds**; lower test accuracy for the expanded model accompanies higher low-rating recall. Average precision (AP) summarizes the precision–recall ranking without choosing a threshold.

| Untouched recipe-group test | Baseline: words | Expanded: words + characters |
|---|---:|---:|
| Low-rating F1 | 0.493 | **0.511** |
| Average precision (AP) | 0.518 | **0.558** |
| Low-rating precision | **0.493** | 0.417 |
| Low-rating recall | 0.493 | **0.658** |
| Balanced accuracy | 0.730 | **0.798** |
| Overall accuracy | **0.937** | 0.922 |

Confusion matrices use rows = true `positive, low`, columns = predicted `positive, low`. Baseline: `[[1064, 37], [37, 36]]`. Expanded: `[[1034, 67], [25, 48]]`. The expanded candidate catches 12 more of the 73 low-rated test comments, while adding 30 false flags.

Validation low-rating F1 was **0.620155** for baseline and **0.619355** for expanded. The predeclared selection rule therefore deploys the **baseline**, even though the expanded candidate does better on several test measures. The test F1 difference is +0.0175 for expanded. A 2,000-resample recipe-cluster bootstrap gives a 95% interval of **−0.0656 to +0.0798**. It spans zero, so this experiment does not establish a reliable F1 improvement. Threshold choice on the same validation set makes validation F1 optimistic; the test result is the relevant estimate.

## Reproduce and inspect

Use Python 3.11 or newer. The checked-in result was generated with the exact versions in `requirements.txt` (NumPy 2.3.5 and scikit-learn 1.9.1). From the repository root:

```text
python -m venv .venv
# activate the environment for your shell
python -m pip install -r requirements.txt
python research/run_experiment.py --check
python -m unittest discover -s tests -v
python app.py
```

`--check` downloads the pinned dataset into ignored `research/cache/`, retrains both arms, and checks the recorded partitions, selection and metrics. Run without `--check` to regenerate `research/artifacts/results.json`, `baseline.joblib`, `expanded.joblib`, and `test_predictions.csv`. The prediction CSV holds text hashes, recipe codes, true labels and both model scores; it does not republish review text. The two `.joblib` files are trusted local build artifacts, never loaded from an upload. Open `http://localhost:8765` and select **Пікірлер** to try the interactive MVP. The [presentation](https://israptama.vercel.app/presentation.html) (offline bundle: `public/presentation.*`) and [speaker notes / Q&A](presentation/NOTES.md) cover the 7-minute talk.

## Interpretation and limitations

- UCI comments are about popular home recipes, not retail bakery purchases. Even the title-filtered subset does not measure sales, stockouts or production waste. The dataset is English; the classifier has **not** been validated on Kazakh or Russian reviews.
- Stars are weak and imbalanced supervision. A 1–3-star rating is not necessarily a complaint, and a 4–5-star review can contain criticism. Some review text may mention its own rating; no rating metadata is supplied, but this linguistic cue can make the task easier.
- Seven held-out recipes give a wide uncertainty interval. Exact duplicate text is removed, but near-duplicates or authors who reviewed more than one recipe may remain across splits. The title rule and top-100 source also limit representativeness.
- The 0–1 model scores are **not calibrated probabilities**. A person should review any flagged comment. No experiment here demonstrates business uplift or a better numerical bakery forecast. The separate forecasting demo still uses explicitly synthetic data.
