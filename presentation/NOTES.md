# Israptama · Assignment #2 presentation notes

Open `presentation/index.html` in any modern browser. The deck is self-contained and works offline. Use **← / →**, **Page Up / Page Down**, **Space**, the on-screen controls, or swipe. Press **Home** to restart. Run the dashboard separately with `python app.py --port 8765` before the talk, then keep `http://localhost:8765` open in another tab for slide 7.

The eight slide timings total **7:00**. Rehearse the switch to the live tab; slide 7 reserves roughly 30 seconds for interaction. The deck is in English, while the current dashboard labels are in Kazakh.

## 7-minute talk track

### 1 · The question · 0:00–0:35

“Israptama is a bakery planning prototype. Its first component uses sales history to suggest tomorrow’s production. For Assignment #2, I wanted a genuine NLP research question that belongs in the same workflow: can text help an owner decide which feedback to inspect? I used Option A: an open dataset, a baseline, one controlled model change, and a held-out comparison. I will show both the experiment and a working interface.”

### 2 · Two signals, two jobs · 0:35–1:25

“The original dashboard takes daily baked and sold counts and makes a quantity recommendation. Its existing evaluation uses fictional bakery data; those numbers are a simulation, not proven savings. The new view does a different job. It reads English written feedback and estimates whether the comment resembles reviews that received a low rating. I deliberately keep that signal out of the quantity forecast. A review is not a sales count, and this experiment cannot tell us how many croissants to bake.”

### 3 · Open data and labels · 1:25–2:20

“The source is UCI’s Recipe Reviews and User Feedback dataset, released under CC BY 4.0. It contains 18,182 comments. I froze a title-only bakery and dessert filter, then excluded zero-star unrated comments, empty text, and normalized duplicates. Six rows in conflicting-label text clusters were removed. That left 5,984 unique, rated reviews from 38 recipes. The task is binary: 1–3 stars are the low-rating class and 4–5 stars are positive. It is a rating proxy, not a hand-labeled complaint dataset. The model sees text only: it never receives the stars, recipe name, recipe code, user ID, or engagement fields.”

### 4 · Honest split · 2:20–3:15

“A random row split could let reviews of the same recipe appear in both training and test sets. That would overstate performance on a new bakery product. I therefore grouped by recipe: 25 training recipes with 4,011 reviews, six validation recipes with 799 reviews, and seven held-out test recipes with 1,174 reviews. I normalized and deduplicated text before splitting, and I fit both TF-IDF branches only on training reviews. I used validation data to select each decision threshold and the model for the interface. The test set was evaluated after those choices were frozen; later reruns check reproducibility, not model selection.”

### 5 · Controlled model change · 3:15–4:10

“Both candidates use class-balanced logistic regression with the same C value, solver, data split, and normalization. The baseline represents each review with word unigram TF-IDF. The expanded candidate adds character 3–5-gram TF-IDF; this is the one planned change. After combining features, I normalize each row so adding a second branch does not silently double its scale. Character patterns might handle misspellings or word variants. The experiment asks whether they actually help on unseen recipes.”

### 6 · Results and interpretation · 4:10–5:15

“Only 73 of 1,174 test reviews have a low rating: 6.2%. Accuracy alone would conceal that imbalance, so I report low-rating precision, recall, F1, and average precision. The expanded candidate moved test F1 from 0.493 to 0.511 and average precision from 0.518 to 0.558. It found more low-rated reviews: recall rose from 0.493 to 0.658, while precision fell from 0.493 to 0.417. The F1 difference is only 0.017. A recipe-cluster bootstrap interval for the difference runs from −0.066 to +0.080, so this is not strong evidence of a general improvement. The interface uses the word baseline because the predeclared validation F1 rule chose it: 0.620 versus 0.619. I did not use the test result to change that choice.”

### 7 · Live MVP · 5:15–6:15

“Now I’ll show the research in the product.” Switch to the localhost tab. Open **Пікірлер**. Select the example English review or paste: “The banana bread was dry and had very little flavor.” Submit it. Point to the two model outputs, then the measured comparison and the warning that these are English recipe-review signals. Return to **Пісіру жоспары** to show the existing plan still works and is not altered by review text. “The owner can inspect feedback without mistaking it for a demand forecast.” Switch back to slide 8. If the local server is unavailable, show `research/artifacts/results.json` and the source files instead; describe the slide graphic as a mock, not a live run.

### 8 · Limits and next evidence · 6:15–7:00

“This is a research prototype. Home-recipe comments are a proxy for retail bakery feedback, and the corpus is English; we have no evidence that the model works on Kazakh text. The held-out test covers only seven recipes, and the bootstrap interval includes no improvement. The next step is opt-in bakery feedback with local labels, followed by a separate pilot to see whether triage helps an owner make decisions. The source, split manifest, script, saved model, test predictions, and tests are in the repository. I’m ready to show the code or take questions.”

## 2–3-minute Q&A preparation

Use three or four of these, depending on what the instructor asks. Keep each answer near 20–30 seconds.

| Likely question | Concise answer |
|---|---|
| Why NLP instead of an LLM? | Option A allows NLP. A small, transparent classifier makes the controlled change and leakage boundary easy to reproduce, with no API key or external inference service. |
| Why group by recipe? | The app may encounter feedback on products unseen during training. Holding out entire recipes tests that situation and prevents recipe-specific wording from appearing in both train and test. Exact normalized text was also deduplicated before splitting. |
| Are 1–3 stars really complaints? | No. They are a weak low-rating proxy. A three-star review can be mixed or constructive, and a five-star review may contain a criticism. The interface says “low-rating signal” and leaves the decision to a person. |
| Why is the baseline live when the expanded model did better on test? | The selection rule was fixed on validation minority F1. The baseline scored 0.620, slightly above 0.619, so it was selected before the test was read. Reversing that choice after seeing test scores would contaminate evaluation. Both candidate outputs remain visible for study. |
| Is the improvement statistically secure? | No. The test F1 difference is +0.017, with a recipe-cluster bootstrap interval from −0.066 to +0.080. Only seven recipes were held out. The expanded model gained recall and average precision but lost precision. |
| Why report average precision? | Test low-rating prevalence is 0.062, so a majority-class accuracy can look high while missing all low ratings. Average precision evaluates ranking across thresholds; the no-skill reference is the class prevalence. Minority F1, precision, and recall show the chosen threshold’s tradeoff. |
| Does this reduce bakery waste? | The NLP experiment has not tested that. The production model’s published results are synthetic, and the feedback classifier does not feed its demand forecast. A real bakery pilot is needed for operational impact. |
| Can it analyze Kazakh reviews? | The server can receive text, but this English-trained model is not validated for Kazakh and the interface asks for English. Language-specific data and labels are needed before making that claim. |
| How can I reproduce it? | Install the pinned Python dependencies, run `python research/run_experiment.py`, then `python research/run_experiment.py --check`. The script verifies the UCI archive SHA-256, freezes recipe-group seeds, and writes results and test predictions. Run `python -m unittest discover -s tests -v` for the app and model checks. |

## Source-code tour if requested

1. `review_model.py`: title filter, deduplication, recipe-group split, two model definitions, local inference.
2. `research/run_experiment.py`: pinned download, validation threshold rule, test metrics, cluster bootstrap, artifacts.
3. `research/artifacts/results.json`: exact counts, split recipe codes, thresholds, measured results and caveats.
4. `app.py` and `public/`: API and dashboard view; the NLP path is separate from `/api/analyze`.
5. `tests/`: split, model configuration, HTTP and original forecasting checks.

Data attribution: Ali, A., Matuszewski, S., & Czupyt, J. (2023), *Recipe Reviews and User Feedback*, UCI Machine Learning Repository, DOI [10.24432/C5FG95](https://doi.org/10.24432/C5FG95), CC BY 4.0.
